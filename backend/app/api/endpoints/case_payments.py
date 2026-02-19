"""
ControlNot v2 - Case Payments Endpoints
Endpoints REST para pagos de un expediente
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import structlog

from app.repositories.case_repository import case_repository
from app.repositories.case_payment_repository import case_payment_repository
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/cases/{case_id}/payments", tags=["Case Payments"])


# === Schemas ===

class PaymentCreateRequest(BaseModel):
    tipo: str = Field(..., description="honorarios|impuestos|derechos|gastos|otro")
    concepto: str = Field(..., min_length=1, description="Concepto del pago")
    monto: float = Field(..., gt=0, description="Monto del pago")
    metodo_pago: str = Field('efectivo', description="efectivo|transferencia|cheque|tarjeta|otro")
    referencia: Optional[str] = Field(None, description="Referencia de pago")
    fecha_pago: Optional[str] = Field(None, description="Fecha del pago ISO 8601")
    recibido_por: Optional[str] = Field(None, description="Quien recibio el pago")
    comprobante_path: Optional[str] = Field(None, description="Ruta del comprobante")
    notas: Optional[str] = Field(None, description="Notas adicionales")


class PaymentUpdateRequest(BaseModel):
    tipo: Optional[str] = None
    concepto: Optional[str] = None
    monto: Optional[float] = Field(None, gt=0)
    metodo_pago: Optional[str] = None
    referencia: Optional[str] = None
    fecha_pago: Optional[str] = None
    recibido_por: Optional[str] = None
    comprobante_path: Optional[str] = None
    notas: Optional[str] = None


# === Helpers ===

async def _verify_case_ownership(case_id: UUID, tenant_id: str):
    """Verifica que el caso existe y pertenece al tenant"""
    case = await case_repository.get_by_id(case_id)
    if not case or case['tenant_id'] != tenant_id:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return case


# === Endpoints ===

@router.get("")
async def list_payments(
    case_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Lista pagos de un expediente con totales"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        payments = await case_payment_repository.list_by_case(
            case_id=case_id, limit=limit, offset=offset
        )
        totals = await case_payment_repository.get_totals_by_case(case_id)

        return {
            'payments': payments,
            'totals': totals,
            'limit': limit,
            'offset': offset,
        }
    except Exception as e:
        logger.error("list_payments_failed", case_id=str(case_id), error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener pagos")


@router.post("", status_code=201)
async def create_payment(
    case_id: UUID,
    request: PaymentCreateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Registra un nuevo pago"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        payment = await case_payment_repository.create_payment(
            tenant_id=UUID(tenant_id),
            case_id=case_id,
            tipo=request.tipo,
            concepto=request.concepto,
            monto=request.monto,
            metodo_pago=request.metodo_pago,
            referencia=request.referencia,
            fecha_pago=request.fecha_pago,
            recibido_por=request.recibido_por,
            comprobante_path=request.comprobante_path,
            notas=request.notas,
        )

        if not payment:
            raise HTTPException(status_code=500, detail="Error al registrar pago")

        return {"message": "Pago registrado", "payment": payment}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_payment_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al registrar pago")


@router.patch("/{payment_id}")
async def update_payment(
    case_id: UUID,
    payment_id: UUID,
    request: PaymentUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Actualiza un pago existente"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        updates = request.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")

        updated = await case_payment_repository.update(payment_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail="Pago no encontrado")

        return {"message": "Pago actualizado", "payment": updated}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_payment_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar pago")


@router.delete("/{payment_id}")
async def delete_payment(
    case_id: UUID,
    payment_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Elimina un pago"""
    await _verify_case_ownership(case_id, tenant_id)

    try:
        deleted = await case_payment_repository.delete(payment_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Pago no encontrado")

        return {"message": "Pago eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_payment_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al eliminar pago")
