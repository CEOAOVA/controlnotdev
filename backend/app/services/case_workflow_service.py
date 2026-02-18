"""
ControlNot v2 - Case Workflow Service
State machine para el flujo de expedientes notariales
"""
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timezone
import structlog

from app.repositories.case_repository import case_repository
from app.repositories.case_activity_repository import case_activity_repository

logger = structlog.get_logger()

# Status labels en español para display
STATUS_LABELS = {
    'borrador': 'Borrador',
    'en_revision': 'En Revisión',
    'checklist_pendiente': 'Checklist Pendiente',
    'presupuesto': 'Presupuesto',
    'calculo_impuestos': 'Cálculo de Impuestos',
    'en_firma': 'En Firma',
    'postfirma': 'Post-Firma',
    'tramites_gobierno': 'Trámites de Gobierno',
    'inscripcion': 'Inscripción',
    'facturacion': 'Facturación',
    'entrega': 'Entrega',
    'cerrado': 'Cerrado',
    'cancelado': 'Cancelado',
    'suspendido': 'Suspendido',
}

# Transiciones válidas del state machine
ALLOWED_TRANSITIONS = {
    'borrador': ['en_revision', 'cancelado'],
    'en_revision': ['checklist_pendiente', 'presupuesto', 'cancelado', 'suspendido'],
    'checklist_pendiente': ['en_revision', 'presupuesto', 'cancelado', 'suspendido'],
    'presupuesto': ['calculo_impuestos', 'cancelado', 'suspendido'],
    'calculo_impuestos': ['en_firma', 'cancelado', 'suspendido'],
    'en_firma': ['postfirma', 'cancelado', 'suspendido'],
    'postfirma': ['tramites_gobierno', 'cancelado', 'suspendido'],
    'tramites_gobierno': ['inscripcion', 'cancelado', 'suspendido'],
    'inscripcion': ['facturacion', 'cancelado', 'suspendido'],
    'facturacion': ['entrega', 'cancelado', 'suspendido'],
    'entrega': ['cerrado', 'cancelado', 'suspendido'],
    'suspendido': [],  # se restaura con resume()
    'cancelado': [],   # terminal
    'cerrado': [],     # terminal
}


class CaseWorkflowService:
    """
    Servicio de state machine para el flujo de expedientes.

    Valida transiciones, ejecuta cambios de status, y registra actividad.
    """

    def validate_transition(self, current_status: str, new_status: str) -> bool:
        """Valida si una transición es permitida"""
        allowed = ALLOWED_TRANSITIONS.get(current_status, [])
        return new_status in allowed

    def get_available_transitions(self, current_status: str) -> List[Dict[str, str]]:
        """Retorna las transiciones disponibles desde el status actual"""
        allowed = ALLOWED_TRANSITIONS.get(current_status, [])
        return [
            {'status': s, 'label': STATUS_LABELS.get(s, s)}
            for s in allowed
        ]

    async def transition(
        self,
        case_id: UUID,
        tenant_id: UUID,
        new_status: str,
        user_id: Optional[UUID] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Ejecuta una transición de status validada.

        Returns:
            Caso actualizado

        Raises:
            ValueError: Si la transición no es válida
        """
        case = await case_repository.get_by_id(case_id)
        if not case:
            raise ValueError("Caso no encontrado")

        current_status = case['status']

        if not self.validate_transition(current_status, new_status):
            allowed = ALLOWED_TRANSITIONS.get(current_status, [])
            raise ValueError(
                f"Transición no permitida: {current_status} -> {new_status}. "
                f"Transiciones válidas: {allowed}"
            )

        updates = {'status': new_status}
        if new_status == 'cerrado':
            updates['fecha_cierre'] = datetime.now(timezone.utc).isoformat()
        if new_status == 'cancelado':
            updates['fecha_cierre'] = datetime.now(timezone.utc).isoformat()

        updated_case = await case_repository.update(case_id, updates)

        # Registrar en activity log
        description = f"Estado cambiado de {STATUS_LABELS.get(current_status, current_status)} a {STATUS_LABELS.get(new_status, new_status)}"
        if notes:
            description += f". Nota: {notes}"

        await case_activity_repository.log(
            tenant_id=tenant_id,
            case_id=case_id,
            action='status_change',
            description=description,
            user_id=user_id,
            entity_type='case',
            entity_id=case_id,
            old_value={'status': current_status},
            new_value={'status': new_status},
        )

        logger.info(
            "case_transitioned",
            case_id=str(case_id),
            from_status=current_status,
            to_status=new_status
        )

        return updated_case

    async def suspend(
        self,
        case_id: UUID,
        tenant_id: UUID,
        reason: str,
        user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Suspende un caso, guardando el status anterior en metadata.

        Raises:
            ValueError: Si el caso ya está suspendido/cancelado/cerrado
        """
        case = await case_repository.get_by_id(case_id)
        if not case:
            raise ValueError("Caso no encontrado")

        current_status = case['status']
        if current_status in ('suspendido', 'cancelado', 'cerrado'):
            raise ValueError(f"No se puede suspender un caso con status '{current_status}'")

        metadata = case.get('metadata', {}) or {}
        metadata['suspended_from'] = current_status
        metadata['suspend_reason'] = reason

        updated_case = await case_repository.update(case_id, {
            'status': 'suspendido',
            'metadata': metadata,
        })

        await case_activity_repository.log(
            tenant_id=tenant_id,
            case_id=case_id,
            action='status_change',
            description=f"Caso suspendido desde {STATUS_LABELS.get(current_status, current_status)}. Razón: {reason}",
            user_id=user_id,
            entity_type='case',
            entity_id=case_id,
            old_value={'status': current_status},
            new_value={'status': 'suspendido', 'reason': reason},
        )

        return updated_case

    async def resume(
        self,
        case_id: UUID,
        tenant_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Reanuda un caso suspendido, restaurando el status anterior.

        Raises:
            ValueError: Si el caso no está suspendido
        """
        case = await case_repository.get_by_id(case_id)
        if not case:
            raise ValueError("Caso no encontrado")

        if case['status'] != 'suspendido':
            raise ValueError("Solo se pueden reanudar casos suspendidos")

        metadata = case.get('metadata', {}) or {}
        previous_status = metadata.pop('suspended_from', 'borrador')
        metadata.pop('suspend_reason', None)

        updated_case = await case_repository.update(case_id, {
            'status': previous_status,
            'metadata': metadata,
        })

        await case_activity_repository.log(
            tenant_id=tenant_id,
            case_id=case_id,
            action='status_change',
            description=f"Caso reanudado a {STATUS_LABELS.get(previous_status, previous_status)}",
            user_id=user_id,
            entity_type='case',
            entity_id=case_id,
            old_value={'status': 'suspendido'},
            new_value={'status': previous_status},
        )

        return updated_case


# Instancia singleton
case_workflow_service = CaseWorkflowService()
