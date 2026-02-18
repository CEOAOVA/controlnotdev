"""
ControlNot v2 - Catalogos Endpoints
Endpoints REST para gestión de catálogos de checklist templates
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
import structlog

from app.repositories.catalogo_checklist_repository import catalogo_checklist_repository
from app.schemas.case_schemas import (
    CatalogoChecklistCreateRequest,
    CatalogoChecklistUpdateRequest,
    CatalogoChecklistResponse,
)
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/catalogos", tags=["Catalogos"])


@router.get("/checklist-templates", response_model=list[CatalogoChecklistResponse])
async def list_checklist_templates(
    document_type: Optional[str] = Query(None, description="Filtrar por tipo de documento"),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Lista templates de checklist (sistema + tenant)"""
    try:
        if document_type:
            templates = await catalogo_checklist_repository.list_by_type(
                document_type=document_type,
                tenant_id=UUID(tenant_id),
            )
        else:
            templates = await catalogo_checklist_repository.list_by_tenant(
                tenant_id=UUID(tenant_id),
                limit=200,
            )

        return [CatalogoChecklistResponse(**t) for t in templates]

    except Exception as e:
        logger.error("list_checklist_templates_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al listar templates de checklist")


@router.post("/checklist-templates", response_model=CatalogoChecklistResponse, status_code=201)
async def create_checklist_template(
    request: CatalogoChecklistCreateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Crea un template de checklist para el tenant"""
    try:
        template = await catalogo_checklist_repository.create_template(
            document_type=request.document_type,
            nombre=request.nombre,
            categoria=request.categoria,
            obligatorio=request.obligatorio,
            orden=request.orden,
            tenant_id=UUID(tenant_id),
        )

        if not template:
            raise HTTPException(status_code=500, detail="Error al crear template")

        return CatalogoChecklistResponse(**template)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_checklist_template_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al crear template de checklist")


@router.put("/checklist-templates/{template_id}", response_model=CatalogoChecklistResponse)
async def update_checklist_template(
    template_id: UUID,
    request: CatalogoChecklistUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Actualiza un template de checklist"""
    try:
        template = await catalogo_checklist_repository.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template no encontrado")

        # Only allow editing own tenant's templates (not system defaults)
        if template.get('tenant_id') and template['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Template no encontrado")

        updates = request.model_dump(exclude_unset=True)
        if not updates:
            return CatalogoChecklistResponse(**template)

        updated = await catalogo_checklist_repository.update_template(template_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Error al actualizar template")

        return CatalogoChecklistResponse(**updated)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_checklist_template_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar template")


@router.delete("/checklist-templates/{template_id}", status_code=204)
async def delete_checklist_template(
    template_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Elimina un template de checklist"""
    try:
        template = await catalogo_checklist_repository.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template no encontrado")

        if template.get('tenant_id') and template['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Template no encontrado")

        if not template.get('tenant_id'):
            raise HTTPException(status_code=403, detail="No se pueden eliminar templates del sistema")

        deleted = await catalogo_checklist_repository.delete_template(template_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Error al eliminar template")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_checklist_template_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al eliminar template")
