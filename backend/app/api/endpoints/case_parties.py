"""
ControlNot v2 - Case Parties Endpoints
Endpoints REST para gestión de partes normalizadas de un caso
"""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
import structlog

from app.repositories.case_repository import case_repository
from app.repositories.case_party_repository import case_party_repository
from app.services.case_activity_service import case_activity_service
from app.schemas.case_schemas import (
    CasePartyCreateRequest,
    CasePartyUpdateRequest,
    CasePartyResponse,
)
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/cases/{case_id}/parties", tags=["Case Parties"])


async def _verify_case_ownership(case_id: UUID, tenant_id: str):
    """Verifica que el caso existe y pertenece al tenant"""
    case = await case_repository.get_by_id(case_id)
    if not case or case['tenant_id'] != tenant_id:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return case


@router.get("", response_model=list[CasePartyResponse])
async def list_parties(
    case_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Lista partes de un caso"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        parties = await case_party_repository.list_by_case(case_id)
        return [CasePartyResponse(**p) for p in parties]
    except Exception as e:
        logger.error("list_parties_failed", case_id=str(case_id), error=str(e))
        raise HTTPException(status_code=500, detail="Error al listar partes")


@router.post("", response_model=CasePartyResponse, status_code=201)
async def create_party(
    case_id: UUID,
    request: CasePartyCreateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Agrega una parte normalizada al caso"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        party = await case_party_repository.create_party(
            tenant_id=UUID(tenant_id),
            case_id=case_id,
            role=request.role,
            nombre=request.nombre,
            client_id=request.client_id,
            rfc=request.rfc,
            tipo_persona=request.tipo_persona,
            email=request.email,
            telefono=request.telefono,
            representante_legal=request.representante_legal,
            poder_notarial=request.poder_notarial,
            orden=request.orden,
        )

        if not party:
            raise HTTPException(status_code=500, detail="Error al crear parte")

        await case_activity_service.log_activity(
            tenant_id=UUID(tenant_id),
            case_id=case_id,
            action='party_added',
            description=f"Parte agregada: {request.nombre} ({request.role})",
            entity_type='party',
            entity_id=UUID(party['id']),
        )

        return CasePartyResponse(**party)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_party_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al crear parte")


@router.put("/{party_id}", response_model=CasePartyResponse)
async def update_party(
    case_id: UUID,
    party_id: UUID,
    request: CasePartyUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Actualiza una parte"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        party = await case_party_repository.get_by_id(party_id)
        if not party or str(party['case_id']) != str(case_id):
            raise HTTPException(status_code=404, detail="Parte no encontrada")

        updates = request.model_dump(exclude_unset=True)
        if not updates:
            return CasePartyResponse(**party)

        updated = await case_party_repository.update_party(party_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Error al actualizar parte")

        return CasePartyResponse(**updated)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_party_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar parte")


@router.delete("/{party_id}", status_code=204)
async def delete_party(
    case_id: UUID,
    party_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Elimina una parte"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        party = await case_party_repository.get_by_id(party_id)
        if not party or str(party['case_id']) != str(case_id):
            raise HTTPException(status_code=404, detail="Parte no encontrada")

        deleted = await case_party_repository.delete_party(party_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Error al eliminar parte")

        await case_activity_service.log_activity(
            tenant_id=UUID(tenant_id),
            case_id=case_id,
            action='party_removed',
            description=f"Parte eliminada: {party['nombre']} ({party['role']})",
            entity_type='party',
            entity_id=party_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_party_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al eliminar parte")
