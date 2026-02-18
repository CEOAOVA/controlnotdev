"""
ControlNot v2 - Case Activity Endpoints
Endpoints REST para timeline de actividad y notas de un caso
"""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
import structlog

from app.repositories.case_repository import case_repository
from app.services.case_activity_service import case_activity_service
from app.schemas.case_schemas import (
    CaseNoteRequest,
    CaseTimelineResponse,
)
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/cases/{case_id}", tags=["Case Activity"])


async def _verify_case_ownership(case_id: UUID, tenant_id: str):
    """Verifica que el caso existe y pertenece al tenant"""
    case = await case_repository.get_by_id(case_id)
    if not case or case['tenant_id'] != tenant_id:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return case


@router.get("/timeline", response_model=CaseTimelineResponse)
async def get_case_timeline(
    case_id: UUID,
    limit: int = Query(50, ge=1, le=200, description="Máximo de eventos"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Obtiene el timeline de actividad de un caso"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        result = await case_activity_service.get_timeline(
            case_id=case_id,
            limit=limit,
            offset=offset,
        )

        return CaseTimelineResponse(
            case_id=case_id,
            events=result['events'],
            total=result['total'],
            limit=result['limit'],
            offset=result['offset'],
        )

    except Exception as e:
        logger.error("get_timeline_failed", case_id=str(case_id), error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener timeline")


@router.post("/notes", status_code=201)
async def add_case_note(
    case_id: UUID,
    request: CaseNoteRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Agrega una nota al timeline del caso"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        result = await case_activity_service.add_note(
            tenant_id=UUID(tenant_id),
            case_id=case_id,
            note=request.note,
        )

        if not result:
            raise HTTPException(status_code=500, detail="Error al agregar nota")

        return {"message": "Nota agregada", "id": result['id']}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("add_note_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al agregar nota")
