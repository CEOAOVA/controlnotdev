"""
ControlNot v2 - Case Tramites Endpoints
Endpoints REST para gestión de trámites gubernamentales por caso
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
import structlog

from app.repositories.case_repository import case_repository
from app.repositories.case_tramite_repository import case_tramite_repository
from app.services.tramite_service import tramite_service
from app.schemas.case_schemas import (
    TramiteCreateRequest,
    TramiteUpdateRequest,
    TramiteCompleteRequest,
    TramiteResponse,
)
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(tags=["Tramites"])


async def _verify_case_ownership(case_id: UUID, tenant_id: str):
    """Verifica que el caso existe y pertenece al tenant"""
    case = await case_repository.get_by_id(case_id)
    if not case or case['tenant_id'] != tenant_id:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return case


# --- Case-scoped endpoints ---

@router.get("/cases/{case_id}/tramites", response_model=list[TramiteResponse])
async def list_tramites(
    case_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Lista trámites de un caso con semáforo"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        tramites = await case_tramite_repository.list_by_case(case_id)
        tramites = tramite_service.enrich_with_semaforo(tramites)
        return [TramiteResponse(**t) for t in tramites]
    except Exception as e:
        logger.error("list_tramites_failed", case_id=str(case_id), error=str(e))
        raise HTTPException(status_code=500, detail="Error al listar trámites")


@router.post("/cases/{case_id}/tramites", response_model=TramiteResponse, status_code=201)
async def create_tramite(
    case_id: UUID,
    request: TramiteCreateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Crea un trámite para un caso"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        tramite = await tramite_service.create(
            tenant_id=UUID(tenant_id),
            case_id=case_id,
            tipo=request.tipo,
            nombre=request.nombre,
            assigned_to=request.assigned_to,
            fecha_limite=request.fecha_limite.isoformat() if request.fecha_limite else None,
            costo=request.costo,
            depende_de=request.depende_de,
            notas=request.notas,
        )

        if not tramite:
            raise HTTPException(status_code=500, detail="Error al crear trámite")

        return TramiteResponse(**tramite)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_tramite_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al crear trámite")


@router.put("/cases/{case_id}/tramites/{tramite_id}", response_model=TramiteResponse)
async def update_tramite(
    case_id: UUID,
    tramite_id: UUID,
    request: TramiteUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Actualiza un trámite"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        tramite = await case_tramite_repository.get_by_id(tramite_id)
        if not tramite or str(tramite['case_id']) != str(case_id):
            raise HTTPException(status_code=404, detail="Trámite no encontrado")

        updates = request.model_dump(exclude_unset=True)
        if not updates:
            return TramiteResponse(**tramite)

        if 'assigned_to' in updates and updates['assigned_to']:
            updates['assigned_to'] = str(updates['assigned_to'])
        if 'fecha_limite' in updates and updates['fecha_limite']:
            updates['fecha_limite'] = updates['fecha_limite'].isoformat()

        updated = await case_tramite_repository.update(tramite_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Error al actualizar trámite")

        return TramiteResponse(**updated)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_tramite_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar trámite")


@router.post("/cases/{case_id}/tramites/{tramite_id}/complete", response_model=TramiteResponse)
async def complete_tramite(
    case_id: UUID,
    tramite_id: UUID,
    request: TramiteCompleteRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Marca un trámite como completado"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        tramite = await case_tramite_repository.get_by_id(tramite_id)
        if not tramite or str(tramite['case_id']) != str(case_id):
            raise HTTPException(status_code=404, detail="Trámite no encontrado")

        updated = await tramite_service.complete(
            tramite_id=tramite_id,
            tenant_id=UUID(tenant_id),
            case_id=case_id,
            resultado=request.resultado,
            costo=request.costo,
        )

        return TramiteResponse(**updated)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("complete_tramite_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al completar trámite")


@router.delete("/cases/{case_id}/tramites/{tramite_id}", status_code=204)
async def delete_tramite(
    case_id: UUID,
    tramite_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Elimina un trámite"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        tramite = await case_tramite_repository.get_by_id(tramite_id)
        if not tramite or str(tramite['case_id']) != str(case_id):
            raise HTTPException(status_code=404, detail="Trámite no encontrado")

        deleted = await case_tramite_repository.delete(tramite_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Error al eliminar trámite")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_tramite_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al eliminar trámite")


# --- Top-level endpoints ---

@router.get("/tramites/overdue", response_model=list[TramiteResponse])
async def get_overdue_tramites(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Lista trámites vencidos de toda la notaría"""
    try:
        tramites = await tramite_service.get_overdue(UUID(tenant_id))
        return [TramiteResponse(**t) for t in tramites]
    except Exception as e:
        logger.error("overdue_tramites_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener trámites vencidos")


@router.get("/tramites/upcoming", response_model=list[TramiteResponse])
async def get_upcoming_tramites(
    days: int = Query(7, ge=1, le=30, description="Días hacia adelante"),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Lista trámites próximos a vencer"""
    try:
        tramites = await tramite_service.get_upcoming(UUID(tenant_id), days=days)
        return [TramiteResponse(**t) for t in tramites]
    except Exception as e:
        logger.error("upcoming_tramites_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener trámites próximos")
