"""
ControlNot v2 - Case Payment Repository
CRUD para la tabla case_payments (pagos de un expediente)
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class CasePaymentRepository(BaseRepository):
    """Repository for case_payments table"""

    def __init__(self):
        super().__init__('case_payments')

    async def list_by_case(
        self,
        case_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List payments for a specific case"""
        try:
            result = self._table()\
                .select('*')\
                .eq('case_id', str(case_id))\
                .order('fecha_pago', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("payment_list_failed", case_id=str(case_id), error=str(e))
            raise

    async def get_totals_by_case(
        self,
        case_id: UUID
    ) -> Dict[str, float]:
        """Get payment totals grouped by tipo for a case"""
        try:
            result = self._table()\
                .select('tipo, monto')\
                .eq('case_id', str(case_id))\
                .execute()

            totals: Dict[str, float] = {}
            grand_total = 0.0
            if result.data:
                for row in result.data:
                    tipo = row['tipo']
                    monto = float(row['monto'])
                    totals[tipo] = totals.get(tipo, 0.0) + monto
                    grand_total += monto

            return {
                'by_tipo': totals,
                'total': grand_total,
                'count': len(result.data) if result.data else 0,
            }
        except APIError as e:
            logger.error("payment_totals_failed", case_id=str(case_id), error=str(e))
            raise

    async def create_payment(
        self,
        tenant_id: UUID,
        case_id: UUID,
        tipo: str,
        concepto: str,
        monto: float,
        metodo_pago: str = 'efectivo',
        referencia: Optional[str] = None,
        fecha_pago: Optional[str] = None,
        recibido_por: Optional[str] = None,
        comprobante_path: Optional[str] = None,
        notas: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new payment record"""
        data: Dict[str, Any] = {
            'tenant_id': str(tenant_id),
            'case_id': str(case_id),
            'tipo': tipo,
            'concepto': concepto,
            'monto': monto,
            'metodo_pago': metodo_pago,
        }
        if referencia:
            data['referencia'] = referencia
        if fecha_pago:
            data['fecha_pago'] = fecha_pago
        if recibido_por:
            data['recibido_por'] = recibido_por
        if comprobante_path:
            data['comprobante_path'] = comprobante_path
        if notas:
            data['notas'] = notas

        return await self.create(data)


# Singleton instance
case_payment_repository = CasePaymentRepository()
