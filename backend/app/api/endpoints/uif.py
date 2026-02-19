"""
ControlNot v2 - UIF / PLD Endpoints
Endpoints para operaciones vulnerables (actividades vulnerables)
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import structlog

from app.repositories.uif_repository import uif_repository
from app.services.uif_service import uif_service
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/uif", tags=["UIF/PLD"])


# === Schemas ===

class UIFFlagRequest(BaseModel):
    case_id: str = Field(..., description="UUID del caso")
    tipo_operacion: str = Field('compraventa', description="compraventa|donacion|fideicomiso|poder|otro")
    monto_operacion: float = Field(..., gt=0, description="Monto de la operacion")
    responsable_id: Optional[str] = None
    notas: Optional[str] = None


class UIFUpdateRequest(BaseModel):
    status: Optional[str] = Field(None, description="pendiente|reportado|archivado")
    numero_aviso: Optional[str] = None
    fecha_aviso: Optional[str] = None
    notas: Optional[str] = None
    responsable_id: Optional[str] = None


# === Endpoints ===

@router.get("")
async def list_operations(
    status: Optional[str] = Query(None),
    nivel_riesgo: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Lista operaciones vulnerables con filtros"""
    try:
        operations = await uif_repository.list_vulnerable(
            tenant_id=UUID(tenant_id),
            status=status,
            nivel_riesgo=nivel_riesgo,
            limit=limit,
            offset=offset,
        )
        summary = await uif_repository.get_summary(UUID(tenant_id))
        return {
            'operations': operations,
            'summary': summary,
        }
    except Exception as e:
        logger.error("uif_list_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener operaciones UIF")


@router.get("/check/{case_id}")
async def check_case(
    case_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Verifica si un caso tiene flag UIF"""
    try:
        operation = await uif_service.check_case(case_id)
        return {
            'flagged': operation is not None,
            'operation': operation,
        }
    except Exception as e:
        logger.error("uif_check_failed", case_id=str(case_id), error=str(e))
        raise HTTPException(status_code=500, detail="Error al verificar caso UIF")


@router.post("/flag", status_code=201)
async def flag_operation(
    request: UIFFlagRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Marca una operacion como vulnerable"""
    try:
        result = await uif_service.flag_operation(
            tenant_id=UUID(tenant_id),
            case_id=UUID(request.case_id),
            tipo_operacion=request.tipo_operacion,
            monto_operacion=request.monto_operacion,
            responsable_id=UUID(request.responsable_id) if request.responsable_id else None,
            notas=request.notas,
        )

        if not result:
            raise HTTPException(status_code=500, detail="Error al marcar operacion")

        return {"message": "Operacion marcada", "operation": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("uif_flag_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al marcar operacion UIF")


@router.patch("/{operation_id}")
async def update_operation(
    operation_id: UUID,
    request: UIFUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Actualiza una operacion UIF"""
    try:
        updates = request.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")

        updated = await uif_repository.update(operation_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail="Operacion no encontrada")

        return {"message": "Operacion actualizada", "operation": updated}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("uif_update_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar operacion UIF")


@router.get("/evaluate")
async def evaluate_operation(
    tipo_operacion: str = Query('compraventa'),
    monto: float = Query(..., gt=0),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Evalua si un monto excede umbrales UIF (sin guardar)"""
    evaluation = uif_service.evaluate_operation(tipo_operacion, monto)
    return evaluation
