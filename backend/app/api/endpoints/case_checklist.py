"""
ControlNot v2 - Case Checklist Endpoints
Endpoints REST para gestión del checklist documental de un caso
"""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
import structlog

from app.repositories.case_repository import case_repository
from app.repositories.case_checklist_repository import case_checklist_repository
from app.services.checklist_service import checklist_service
from app.schemas.case_schemas import (
    ChecklistItemCreateRequest,
    ChecklistItemUpdateRequest,
    ChecklistInitializeRequest,
    ChecklistItemResponse,
)
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/cases/{case_id}/checklist", tags=["Case Checklist"])


async def _verify_case_ownership(case_id: UUID, tenant_id: str):
    """Verifica que el caso existe y pertenece al tenant"""
    case = await case_repository.get_by_id(case_id)
    if not case or case['tenant_id'] != tenant_id:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return case


@router.get("", response_model=list[ChecklistItemResponse])
async def list_checklist(
    case_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Lista items del checklist de un caso"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        items = await case_checklist_repository.list_by_case(case_id)
        return [ChecklistItemResponse(**i) for i in items]
    except Exception as e:
        logger.error("list_checklist_failed", case_id=str(case_id), error=str(e))
        raise HTTPException(status_code=500, detail="Error al listar checklist")


@router.post("", response_model=ChecklistItemResponse, status_code=201)
async def create_checklist_item(
    case_id: UUID,
    request: ChecklistItemCreateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Agrega un item custom al checklist"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        item = await case_checklist_repository.create_item(
            tenant_id=UUID(tenant_id),
            case_id=case_id,
            nombre=request.nombre,
            categoria=request.categoria,
            obligatorio=request.obligatorio,
            notas=request.notas,
        )

        if not item:
            raise HTTPException(status_code=500, detail="Error al crear item")

        return ChecklistItemResponse(**item)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_checklist_item_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al crear item de checklist")


@router.post("/initialize", response_model=list[ChecklistItemResponse])
async def initialize_checklist(
    case_id: UUID,
    request: ChecklistInitializeRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Inicializa el checklist desde el catálogo de templates"""
    case = await _verify_case_ownership(case_id, tenant_id)

    try:
        doc_type = request.document_type or case['document_type']

        items = await checklist_service.initialize_from_catalog(
            tenant_id=UUID(tenant_id),
            case_id=case_id,
            document_type=doc_type,
        )

        return [ChecklistItemResponse(**i) for i in items]

    except Exception as e:
        logger.error("initialize_checklist_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al inicializar checklist")


@router.put("/{item_id}", response_model=ChecklistItemResponse)
async def update_checklist_item(
    case_id: UUID,
    item_id: UUID,
    request: ChecklistItemUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Actualiza el status de un item del checklist"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        item = await case_checklist_repository.get_by_id(item_id)
        if not item or str(item['case_id']) != str(case_id):
            raise HTTPException(status_code=404, detail="Item no encontrado")

        updated = await checklist_service.update_item_status(
            item_id=item_id,
            status=request.status,
            tenant_id=UUID(tenant_id),
            case_id=case_id,
            notas=request.notas,
        )

        if not updated:
            raise HTTPException(status_code=500, detail="Error al actualizar item")

        return ChecklistItemResponse(**updated)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_checklist_item_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar item")


@router.delete("/{item_id}", status_code=204)
async def delete_checklist_item(
    case_id: UUID,
    item_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Elimina un item del checklist"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        item = await case_checklist_repository.get_by_id(item_id)
        if not item or str(item['case_id']) != str(case_id):
            raise HTTPException(status_code=404, detail="Item no encontrado")

        deleted = await case_checklist_repository.delete(item_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Error al eliminar item")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_checklist_item_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al eliminar item")
