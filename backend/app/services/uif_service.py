"""
ControlNot v2 - UIF Service
Logica de deteccion de umbrales y operaciones vulnerables
"""
from typing import Any, Dict, Optional
from uuid import UUID
import structlog

from app.repositories.uif_repository import uif_repository

logger = structlog.get_logger()

# UIF Thresholds (2024-2025 values)
# Source: Ley Federal para la Prevencion e Identificacion de Operaciones
#         con Recursos de Procedencia Ilicita (Art. 17)
UIF_THRESHOLDS = {
    'compraventa': 682_399.60,   # Inmuebles: aviso cuando >= this
    'donacion': 682_399.60,
    'fideicomiso': 682_399.60,
    'poder': 1_364_799.20,       # Poderes con disposicion de bienes
    'otro': 682_399.60,
}

# Risk levels based on multiples of threshold
RISK_LEVELS = [
    (3.0, 'critico'),   # >= 3x threshold
    (2.0, 'alto'),      # >= 2x threshold
    (1.0, 'medio'),     # >= 1x threshold (at threshold)
    (0.7, 'bajo'),      # >= 70% of threshold (approaching)
]


class UIFService:
    """Service for UIF/PLD vulnerability detection"""

    def evaluate_operation(
        self,
        tipo_operacion: str,
        monto: float,
    ) -> Dict[str, Any]:
        """Evaluate if an operation exceeds UIF thresholds"""
        threshold = UIF_THRESHOLDS.get(tipo_operacion, UIF_THRESHOLDS['otro'])

        # Determine risk level
        nivel_riesgo = 'bajo'
        for multiplier, level in RISK_LEVELS:
            if monto >= threshold * multiplier:
                nivel_riesgo = level
                break

        es_vulnerable = monto >= threshold
        requiere_aviso = es_vulnerable

        return {
            'es_vulnerable': es_vulnerable,
            'nivel_riesgo': nivel_riesgo,
            'umbral_aplicado': threshold,
            'requiere_aviso': requiere_aviso,
        }

    async def flag_operation(
        self,
        tenant_id: UUID,
        case_id: UUID,
        tipo_operacion: str,
        monto_operacion: float,
        responsable_id: Optional[UUID] = None,
        notas: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create or update UIF flag for a case"""
        evaluation = self.evaluate_operation(tipo_operacion, monto_operacion)

        # Check if already flagged
        existing = await uif_repository.get_by_case(case_id)
        if existing:
            updates = {
                'tipo_operacion': tipo_operacion,
                'monto_operacion': monto_operacion,
                **evaluation,
            }
            if responsable_id:
                updates['responsable_id'] = str(responsable_id)
            if notas:
                updates['notas'] = notas

            return await uif_repository.update(UUID(existing['id']), updates)

        # Create new
        data = {
            'tenant_id': str(tenant_id),
            'case_id': str(case_id),
            'tipo_operacion': tipo_operacion,
            'monto_operacion': monto_operacion,
            **evaluation,
        }
        if responsable_id:
            data['responsable_id'] = str(responsable_id)
        if notas:
            data['notas'] = notas

        return await uif_repository.create(data)

    async def check_case(
        self,
        case_id: UUID,
    ) -> Optional[Dict[str, Any]]:
        """Check if a case has a UIF flag"""
        return await uif_repository.get_by_case(case_id)


# Singleton
uif_service = UIFService()
