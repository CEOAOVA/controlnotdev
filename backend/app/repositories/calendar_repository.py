"""
ControlNot v2 - Calendar Repository
CRUD para la tabla calendar_events
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class CalendarRepository(BaseRepository):
    """Repository for calendar_events table"""

    def __init__(self):
        super().__init__('calendar_events')

    async def list_by_range(
        self,
        tenant_id: UUID,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        """List events within a date range for a tenant"""
        try:
            result = self._table()\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .gte('fecha_inicio', start_date)\
                .lte('fecha_inicio', end_date)\
                .order('fecha_inicio', desc=False)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("calendar_list_range_failed", error=str(e))
            raise

    async def list_upcoming(
        self,
        tenant_id: UUID,
        from_date: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """List upcoming events from a date"""
        try:
            result = self._table()\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .gte('fecha_inicio', from_date)\
                .order('fecha_inicio', desc=False)\
                .limit(limit)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("calendar_upcoming_failed", error=str(e))
            raise

    async def list_by_case(
        self,
        case_id: UUID,
    ) -> List[Dict[str, Any]]:
        """List events linked to a case"""
        try:
            result = self._table()\
                .select('*')\
                .eq('case_id', str(case_id))\
                .order('fecha_inicio', desc=False)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("calendar_by_case_failed", case_id=str(case_id), error=str(e))
            raise

    async def create_event(
        self,
        tenant_id: UUID,
        titulo: str,
        fecha_inicio: str,
        tipo: str = 'otro',
        descripcion: Optional[str] = None,
        case_id: Optional[UUID] = None,
        fecha_fin: Optional[str] = None,
        todo_el_dia: bool = False,
        recordatorio_minutos: int = 30,
        color: str = '#3b82f6',
        created_by: Optional[UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a calendar event"""
        data: Dict[str, Any] = {
            'tenant_id': str(tenant_id),
            'titulo': titulo,
            'fecha_inicio': fecha_inicio,
            'tipo': tipo,
            'todo_el_dia': todo_el_dia,
            'recordatorio_minutos': recordatorio_minutos,
            'color': color,
        }
        if descripcion:
            data['descripcion'] = descripcion
        if case_id:
            data['case_id'] = str(case_id)
        if fecha_fin:
            data['fecha_fin'] = fecha_fin
        if created_by:
            data['created_by'] = str(created_by)

        return await self.create(data)


# Singleton instance
calendar_repository = CalendarRepository()
