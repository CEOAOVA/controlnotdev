"""
ControlNot v2 - Case Tramite Repository
Repositorio para gestión de trámites de gobierno/inscripciones por caso
"""
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timezone
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class CaseTramiteRepository(BaseRepository):
    """
    Repositorio para la tabla 'case_tramites'

    Gestiona trámites gubernamentales, pagos de impuestos, inscripciones RPP, etc.
    """

    def __init__(self):
        super().__init__('case_tramites')

    async def list_by_case(
        self,
        case_id: UUID,
        limit: int = 50
    ) -> List[Dict]:
        """Lista trámites de un caso"""
        try:
            result = self._table()\
                .select('*')\
                .eq('case_id', str(case_id))\
                .order('created_at', desc=False)\
                .limit(limit)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("tramites_list_failed", case_id=str(case_id), error=str(e))
            raise

    async def create_tramite(
        self,
        tenant_id: UUID,
        case_id: UUID,
        tipo: str,
        nombre: str,
        assigned_to: Optional[UUID] = None,
        fecha_limite: Optional[str] = None,
        costo: Optional[float] = None,
        depende_de: Optional[UUID] = None,
        notas: Optional[str] = None
    ) -> Optional[Dict]:
        """Crea un nuevo trámite"""
        data = {
            'tenant_id': str(tenant_id),
            'case_id': str(case_id),
            'tipo': tipo,
            'nombre': nombre,
            'status': 'pendiente',
            'fecha_inicio': datetime.now(timezone.utc).isoformat(),
        }
        if assigned_to:
            data['assigned_to'] = str(assigned_to)
        if fecha_limite:
            data['fecha_limite'] = fecha_limite
        if costo is not None:
            data['costo'] = costo
        if depende_de:
            data['depende_de'] = str(depende_de)
        if notas:
            data['notas'] = notas
        return await self.create(data)

    async def complete_tramite(
        self,
        tramite_id: UUID,
        resultado: Optional[str] = None,
        costo: Optional[float] = None
    ) -> Optional[Dict]:
        """Marca un trámite como completado"""
        updates = {
            'status': 'completado',
            'fecha_completado': datetime.now(timezone.utc).isoformat(),
        }
        if resultado:
            updates['resultado'] = resultado
        if costo is not None:
            updates['costo'] = costo
        return await self.update(tramite_id, updates)

    async def list_overdue(
        self,
        tenant_id: UUID,
        limit: int = 50
    ) -> List[Dict]:
        """Lista trámites vencidos (fecha_limite pasada y no completados)"""
        try:
            now = datetime.now(timezone.utc).isoformat()
            result = self._table()\
                .select('*, cases(case_number, document_type)')\
                .eq('tenant_id', str(tenant_id))\
                .in_('status', ['pendiente', 'en_proceso'])\
                .lt('fecha_limite', now)\
                .order('fecha_limite', desc=False)\
                .limit(limit)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("tramites_overdue_failed", tenant_id=str(tenant_id), error=str(e))
            raise

    async def list_upcoming(
        self,
        tenant_id: UUID,
        days: int = 7,
        limit: int = 50
    ) -> List[Dict]:
        """Lista trámites próximos a vencer"""
        try:
            from datetime import timedelta
            now = datetime.now(timezone.utc)
            future = (now + timedelta(days=days)).isoformat()
            result = self._table()\
                .select('*, cases(case_number, document_type)')\
                .eq('tenant_id', str(tenant_id))\
                .in_('status', ['pendiente', 'en_proceso'])\
                .gte('fecha_limite', now.isoformat())\
                .lte('fecha_limite', future)\
                .order('fecha_limite', desc=False)\
                .limit(limit)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("tramites_upcoming_failed", tenant_id=str(tenant_id), error=str(e))
            raise


# Instancia singleton
case_tramite_repository = CaseTramiteRepository()
