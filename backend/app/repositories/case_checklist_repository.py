"""
ControlNot v2 - Case Checklist Repository
Repositorio para gestión del checklist documental de casos
"""
from typing import Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class CaseChecklistRepository(BaseRepository):
    """
    Repositorio para la tabla 'case_checklist'

    Gestiona items del checklist documental por caso
    """

    def __init__(self):
        super().__init__('case_checklist')

    async def list_by_case(
        self,
        case_id: UUID,
        limit: int = 100
    ) -> List[Dict]:
        """Lista items del checklist de un caso"""
        try:
            result = self._table()\
                .select('*')\
                .eq('case_id', str(case_id))\
                .order('categoria', desc=False)\
                .order('created_at', desc=False)\
                .limit(limit)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("checklist_list_failed", case_id=str(case_id), error=str(e))
            raise

    async def create_item(
        self,
        tenant_id: UUID,
        case_id: UUID,
        nombre: str,
        categoria: str,
        obligatorio: bool = True,
        notas: Optional[str] = None
    ) -> Optional[Dict]:
        """Crea un item de checklist"""
        data = {
            'tenant_id': str(tenant_id),
            'case_id': str(case_id),
            'nombre': nombre,
            'categoria': categoria,
            'obligatorio': obligatorio,
            'status': 'pendiente',
        }
        if notas:
            data['notas'] = notas
        return await self.create(data)

    async def bulk_create(
        self,
        items: List[Dict]
    ) -> List[Dict]:
        """Crea múltiples items de checklist (para inicialización desde catálogo)"""
        try:
            result = self._table().insert(items).execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("checklist_bulk_create_failed", count=len(items), error=str(e))
            raise

    async def update_status(
        self,
        item_id: UUID,
        status: str,
        notas: Optional[str] = None
    ) -> Optional[Dict]:
        """Actualiza el status de un item"""
        from datetime import datetime, timezone
        updates = {'status': status}
        if notas:
            updates['notas'] = notas
        if status == 'solicitado':
            updates['fecha_solicitud'] = datetime.now(timezone.utc).isoformat()
        elif status == 'recibido':
            updates['fecha_recepcion'] = datetime.now(timezone.utc).isoformat()
        return await self.update(item_id, updates)

    async def count_by_status(
        self,
        case_id: UUID
    ) -> Dict[str, int]:
        """Cuenta items por status para un caso"""
        try:
            items = await self.list_by_case(case_id)
            counts = {}
            for item in items:
                s = item.get('status', 'pendiente')
                counts[s] = counts.get(s, 0) + 1
            counts['total'] = len(items)
            counts['obligatorios'] = sum(1 for i in items if i.get('obligatorio', True))
            counts['obligatorios_completados'] = sum(
                1 for i in items
                if i.get('obligatorio', True) and i.get('status') in ('aprobado', 'no_aplica')
            )
            return counts
        except APIError as e:
            logger.error("checklist_count_failed", case_id=str(case_id), error=str(e))
            raise


# Instancia singleton
case_checklist_repository = CaseChecklistRepository()
