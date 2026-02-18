"""
ControlNot v2 - Catalogo Checklist Repository
Repositorio para templates de checklist configurables por tipo de documento
"""
from typing import Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class CatalogoChecklistRepository(BaseRepository):
    """
    Repositorio para la tabla 'catalogo_checklist_templates'

    Templates de checklist por tipo de documento. tenant_id NULL = defaults del sistema.
    """

    def __init__(self):
        super().__init__('catalogo_checklist_templates')

    async def list_by_type(
        self,
        document_type: str,
        tenant_id: Optional[UUID] = None
    ) -> List[Dict]:
        """
        Lista templates de checklist por tipo de documento.
        Incluye defaults del sistema (tenant_id IS NULL) y del tenant específico.
        """
        try:
            query = self._table()\
                .select('*')\
                .eq('document_type', document_type)\
                .order('orden', desc=False)

            if tenant_id:
                query = query.or_(f"tenant_id.is.null,tenant_id.eq.{str(tenant_id)}")
            else:
                query = query.is_('tenant_id', 'null')

            result = query.execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("catalogo_list_failed", document_type=document_type, error=str(e))
            raise

    async def create_template(
        self,
        document_type: str,
        nombre: str,
        categoria: str,
        obligatorio: bool = True,
        orden: int = 0,
        tenant_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Crea un template de checklist"""
        data = {
            'document_type': document_type,
            'nombre': nombre,
            'categoria': categoria,
            'obligatorio': obligatorio,
            'orden': orden,
        }
        if tenant_id:
            data['tenant_id'] = str(tenant_id)
        return await self.create(data)

    async def update_template(
        self,
        template_id: UUID,
        updates: Dict
    ) -> Optional[Dict]:
        """Actualiza un template de checklist"""
        return await self.update(template_id, updates)

    async def delete_template(self, template_id: UUID) -> bool:
        """Elimina un template de checklist"""
        return await self.delete(template_id)


# Instancia singleton
catalogo_checklist_repository = CatalogoChecklistRepository()
