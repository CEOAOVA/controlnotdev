"""
ControlNot v2 - Calendar Endpoints
Endpoints REST para calendario de eventos
"""
from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import structlog

from app.repositories.calendar_repository import calendar_repository
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/calendar", tags=["Calendar"])


# === Schemas ===

class EventCreateRequest(BaseModel):
    titulo: str = Field(..., min_length=1, description="Titulo del evento")
    tipo: str = Field('otro', description="vencimiento|firma|cita|audiencia|otro")
    descripcion: Optional[str] = None
    case_id: Optional[str] = None
    fecha_inicio: str = Field(..., description="ISO 8601 datetime")
    fecha_fin: Optional[str] = None
    todo_el_dia: bool = False
    recordatorio_minutos: int = Field(30, ge=0)
    color: str = Field('#3b82f6', description="Hex color")


class EventUpdateRequest(BaseModel):
    titulo: Optional[str] = None
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    case_id: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    todo_el_dia: Optional[bool] = None
    recordatorio_minutos: Optional[int] = Field(None, ge=0)
    color: Optional[str] = None


# === Endpoints ===

@router.get("")
async def list_events(
    start: str = Query(..., description="Start date ISO 8601"),
    end: str = Query(..., description="End date ISO 8601"),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List calendar events within a date range"""
    try:
        events = await calendar_repository.list_by_range(
            tenant_id=UUID(tenant_id),
            start_date=start,
            end_date=end,
        )
        return {'events': events}
    except Exception as e:
        logger.error("list_events_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener eventos")


@router.get("/upcoming")
async def upcoming_events(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(10, ge=1, le=50),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List upcoming events from today"""
    try:
        from_date = datetime.utcnow().isoformat()
        events = await calendar_repository.list_upcoming(
            tenant_id=UUID(tenant_id),
            from_date=from_date,
            limit=limit,
        )
        return {'events': events}
    except Exception as e:
        logger.error("upcoming_events_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener proximos eventos")


@router.post("", status_code=201)
async def create_event(
    request: EventCreateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Create a calendar event"""
    try:
        event = await calendar_repository.create_event(
            tenant_id=UUID(tenant_id),
            titulo=request.titulo,
            tipo=request.tipo,
            descripcion=request.descripcion,
            case_id=UUID(request.case_id) if request.case_id else None,
            fecha_inicio=request.fecha_inicio,
            fecha_fin=request.fecha_fin,
            todo_el_dia=request.todo_el_dia,
            recordatorio_minutos=request.recordatorio_minutos,
            color=request.color,
        )

        if not event:
            raise HTTPException(status_code=500, detail="Error al crear evento")

        return {"message": "Evento creado", "event": event}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_event_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al crear evento")


@router.patch("/{event_id}")
async def update_event(
    event_id: UUID,
    request: EventUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Update a calendar event"""
    try:
        updates = request.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")

        updated = await calendar_repository.update(event_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        return {"message": "Evento actualizado", "event": updated}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_event_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar evento")


@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Delete a calendar event"""
    try:
        deleted = await calendar_repository.delete(event_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        return {"message": "Evento eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_event_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al eliminar evento")
