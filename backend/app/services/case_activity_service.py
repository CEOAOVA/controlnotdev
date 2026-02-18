"""
ControlNot v2 - Case Activity Service
Lógica de negocio para el timeline de actividad de casos
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
import structlog

from app.repositories.case_activity_repository import case_activity_repository

logger = structlog.get_logger()


class CaseActivityService:
    """
    Servicio para gestionar el timeline de actividad de un caso.
    """

    async def log_activity(
        self,
        tenant_id: UUID,
        case_id: UUID,
        action: str,
        description: Optional[str] = None,
        user_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict]:
        """Registra una actividad en el timeline del caso"""
        return await case_activity_repository.log(
            tenant_id=tenant_id,
            case_id=case_id,
            action=action,
            description=description,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
        )

    async def get_timeline(
        self,
        case_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """
        Obtiene el timeline de actividad de un caso con paginación.

        Returns:
            Dict con events y total_count
        """
        events = await case_activity_repository.list_by_case(
            case_id=case_id,
            limit=limit,
            offset=offset
        )
        total = await case_activity_repository.count_by_case(case_id)

        return {
            'events': events,
            'total': total,
            'limit': limit,
            'offset': offset,
        }

    async def add_note(
        self,
        tenant_id: UUID,
        case_id: UUID,
        note: str,
        user_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Agrega una nota al timeline del caso"""
        return await case_activity_repository.log(
            tenant_id=tenant_id,
            case_id=case_id,
            action='note_added',
            description=note,
            user_id=user_id,
            entity_type='case',
            entity_id=case_id,
        )


# Instancia singleton
case_activity_service = CaseActivityService()
