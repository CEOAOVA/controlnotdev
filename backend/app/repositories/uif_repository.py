"""
ControlNot v2 - UIF Repository
CRUD para la tabla uif_operations
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class UIFRepository(BaseRepository):
    """Repository for uif_operations table"""

    def __init__(self):
        super().__init__('uif_operations')

    async def list_vulnerable(
        self,
        tenant_id: UUID,
        status: Optional[str] = None,
        nivel_riesgo: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List vulnerable operations with optional filters"""
        try:
            query = self._table()\
                .select('*')\
                .eq('tenant_id', str(tenant_id))

            if status:
                query = query.eq('status', status)
            if nivel_riesgo:
                query = query.eq('nivel_riesgo', nivel_riesgo)

            result = query\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return result.data if result.data else []
        except APIError as e:
            logger.error("uif_list_failed", error=str(e))
            raise

    async def get_by_case(self, case_id: UUID) -> Optional[Dict[str, Any]]:
        """Get UIF operation for a specific case"""
        try:
            result = self._table()\
                .select('*')\
                .eq('case_id', str(case_id))\
                .limit(1)\
                .execute()
            return result.data[0] if result.data else None
        except APIError as e:
            logger.error("uif_get_by_case_failed", case_id=str(case_id), error=str(e))
            raise

    async def get_summary(self, tenant_id: UUID) -> Dict[str, Any]:
        """Get summary counts by status and risk level"""
        try:
            result = self._table()\
                .select('status, nivel_riesgo, es_vulnerable')\
                .eq('tenant_id', str(tenant_id))\
                .execute()

            rows = result.data or []
            by_status: Dict[str, int] = {}
            by_riesgo: Dict[str, int] = {}
            vulnerables = 0

            for row in rows:
                st = row.get('status', 'pendiente')
                by_status[st] = by_status.get(st, 0) + 1

                nr = row.get('nivel_riesgo', 'bajo')
                by_riesgo[nr] = by_riesgo.get(nr, 0) + 1

                if row.get('es_vulnerable'):
                    vulnerables += 1

            return {
                'total': len(rows),
                'vulnerables': vulnerables,
                'by_status': by_status,
                'by_riesgo': by_riesgo,
            }
        except APIError as e:
            logger.error("uif_summary_failed", error=str(e))
            raise


# Singleton instance
uif_repository = UIFRepository()
