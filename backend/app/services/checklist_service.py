"""
ControlNot v2 - Checklist Service
Lógica de negocio para el checklist documental de expedientes
"""
from typing import Dict, List, Optional
from uuid import UUID
import structlog

from app.repositories.case_checklist_repository import case_checklist_repository
from app.repositories.catalogo_checklist_repository import catalogo_checklist_repository
from app.repositories.case_activity_repository import case_activity_repository

logger = structlog.get_logger()


class ChecklistService:
    """
    Servicio para gestionar el checklist documental de expedientes.

    Permite inicializar desde catálogo, actualizar items, y calcular progreso.
    """

    async def initialize_from_catalog(
        self,
        tenant_id: UUID,
        case_id: UUID,
        document_type: str,
        user_id: Optional[UUID] = None
    ) -> List[Dict]:
        """
        Inicializa el checklist de un caso desde el catálogo de templates.

        Returns:
            Lista de items creados
        """
        templates = await catalogo_checklist_repository.list_by_type(
            document_type=document_type,
            tenant_id=tenant_id
        )

        if not templates:
            logger.warning(
                "checklist_no_templates",
                document_type=document_type,
                tenant_id=str(tenant_id)
            )
            return []

        items = [
            {
                'tenant_id': str(tenant_id),
                'case_id': str(case_id),
                'nombre': t['nombre'],
                'categoria': t['categoria'],
                'obligatorio': t.get('obligatorio', True),
                'status': 'pendiente',
            }
            for t in templates
        ]

        created = await case_checklist_repository.bulk_create(items)

        await case_activity_repository.log(
            tenant_id=tenant_id,
            case_id=case_id,
            action='initialize_checklist',
            description=f"Checklist inicializado con {len(created)} items desde catálogo ({document_type})",
            user_id=user_id,
            entity_type='checklist',
        )

        logger.info(
            "checklist_initialized",
            case_id=str(case_id),
            items_count=len(created),
            document_type=document_type
        )

        return created

    async def update_item_status(
        self,
        item_id: UUID,
        status: str,
        tenant_id: UUID,
        case_id: UUID,
        user_id: Optional[UUID] = None,
        notas: Optional[str] = None
    ) -> Optional[Dict]:
        """Actualiza el status de un item y registra actividad"""
        item = await case_checklist_repository.get_by_id(item_id)
        if not item:
            raise ValueError("Item de checklist no encontrado")

        old_status = item.get('status')
        updated = await case_checklist_repository.update_status(item_id, status, notas)

        await case_activity_repository.log(
            tenant_id=tenant_id,
            case_id=case_id,
            action='update_checklist_item',
            description=f"Checklist '{item['nombre']}': {old_status} → {status}",
            user_id=user_id,
            entity_type='checklist',
            entity_id=item_id,
            old_value={'status': old_status},
            new_value={'status': status},
        )

        return updated

    async def get_completion_pct(self, case_id: UUID) -> float:
        """Calcula el porcentaje de completación del checklist"""
        counts = await case_checklist_repository.count_by_status(case_id)
        total = counts.get('obligatorios', 0)
        if total == 0:
            return 100.0
        completed = counts.get('obligatorios_completados', 0)
        return round((completed / total) * 100, 1)

    async def check_all_required_complete(self, case_id: UUID) -> bool:
        """Verifica si todos los items obligatorios están completos"""
        counts = await case_checklist_repository.count_by_status(case_id)
        return counts.get('obligatorios', 0) == counts.get('obligatorios_completados', 0)

    async def get_summary(self, case_id: UUID) -> Dict:
        """Retorna resumen del checklist para el caso"""
        counts = await case_checklist_repository.count_by_status(case_id)
        pct = await self.get_completion_pct(case_id)
        return {
            'total': counts.get('total', 0),
            'by_status': {
                k: v for k, v in counts.items()
                if k not in ('total', 'obligatorios', 'obligatorios_completados')
            },
            'obligatorios': counts.get('obligatorios', 0),
            'obligatorios_completados': counts.get('obligatorios_completados', 0),
            'completion_pct': pct,
            'all_required_complete': counts.get('obligatorios', 0) == counts.get('obligatorios_completados', 0),
        }


# Instancia singleton
checklist_service = ChecklistService()
