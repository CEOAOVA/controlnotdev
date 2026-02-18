"""
ControlNot v2 - Case Activity Repository
Repositorio para el log de actividad de negocio por caso
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class CaseActivityRepository(BaseRepository):
    """
    Repositorio para la tabla 'case_activity_log'

    Registra actividad de negocio por caso: transiciones, notas, checklist updates
    """

    def __init__(self):
        super().__init__('case_activity_log')

    async def log(
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
        """Registra una actividad en el log del caso"""
        data = {
            'tenant_id': str(tenant_id),
            'case_id': str(case_id),
            'action': action,
        }
        if description:
            data['description'] = description
        if user_id:
            data['user_id'] = str(user_id)
        if entity_type:
            data['entity_type'] = entity_type
        if entity_id:
            data['entity_id'] = str(entity_id)
        if old_value:
            data['old_value'] = old_value
        if new_value:
            data['new_value'] = new_value

        try:
            return await self.create(data)
        except APIError as e:
            logger.error("activity_log_failed", case_id=str(case_id), action=action, error=str(e))
            raise

    async def list_by_case(
        self,
        case_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Lista actividad de un caso (timeline), más reciente primero"""
        try:
            result = self._table()\
                .select('*')\
                .eq('case_id', str(case_id))\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("activity_list_failed", case_id=str(case_id), error=str(e))
            raise

    async def count_by_case(self, case_id: UUID) -> int:
        """Cuenta actividades de un caso"""
        try:
            result = self._table()\
                .select('id', count='exact')\
                .eq('case_id', str(case_id))\
                .execute()
            return result.count if result.count is not None else 0
        except APIError as e:
            logger.error("activity_count_failed", case_id=str(case_id), error=str(e))
            raise


# Instancia singleton
case_activity_repository = CaseActivityRepository()
