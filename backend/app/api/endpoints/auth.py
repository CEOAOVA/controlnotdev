"""
ControlNot v2 - Auth Logging Endpoints
Endpoints para registrar eventos de autenticación desde el frontend

Los eventos de login/logout se manejan directamente con Supabase Auth en el frontend,
pero necesitamos registrarlos en el backend para auditoría y métricas.
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import structlog

from app.database import get_supabase_admin_client

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = structlog.get_logger()


class AuthEventRequest(BaseModel):
    """Schema para eventos de autenticación"""
    event_type: Literal["login_success", "login_failed", "logout", "signup", "password_reset"]
    user_id: Optional[str] = Field(None, description="ID del usuario (si está disponible)")
    email: Optional[str] = Field(None, description="Email del usuario (ofuscado para logs)")
    tenant_id: Optional[str] = Field(None, description="ID del tenant/notaría")
    error_message: Optional[str] = Field(None, description="Mensaje de error (para login_failed)")
    metadata: Optional[dict] = Field(default_factory=dict, description="Metadata adicional")


class AuthEventResponse(BaseModel):
    """Response para eventos de autenticación"""
    success: bool
    message: str
    event_id: Optional[str] = None


def mask_email(email: str) -> str:
    """Ofusca un email para logs (user@domain.com -> u***@domain.com)"""
    if not email or "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "***"
    else:
        masked_local = local[0] + "***" + local[-1]
    return f"{masked_local}@{domain}"


@router.post("/log", response_model=AuthEventResponse)
async def log_auth_event(
    request: Request,
    event: AuthEventRequest
):
    """
    Registra eventos de autenticación para auditoría

    Este endpoint es llamado desde el frontend después de:
    - Login exitoso
    - Login fallido
    - Logout
    - Registro de usuario
    - Solicitud de reset de contraseña

    Los datos sensibles (email, contraseña) se ofuscan antes de guardar.
    """
    try:
        # Obtener información del cliente
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Ofuscar email para logs
        masked_email = mask_email(event.email) if event.email else None

        # Log estructurado del evento
        log_data = {
            "event_type": event.event_type,
            "user_id": event.user_id,
            "email": masked_email,
            "tenant_id": event.tenant_id,
            "ip_address": client_ip,
            "user_agent": user_agent[:100] if user_agent else None,  # Truncar user agent
        }

        # Log según el tipo de evento
        if event.event_type == "login_success":
            logger.info(
                "auth_login_success",
                **log_data
            )
        elif event.event_type == "login_failed":
            logger.warning(
                "auth_login_failed",
                **log_data,
                error=event.error_message
            )
        elif event.event_type == "logout":
            logger.info(
                "auth_logout",
                **log_data
            )
        elif event.event_type == "signup":
            logger.info(
                "auth_signup",
                **log_data
            )
        elif event.event_type == "password_reset":
            logger.info(
                "auth_password_reset_requested",
                **log_data
            )

        # Guardar en tabla de auditoría
        supabase = get_supabase_admin_client()

        audit_data = {
            "action": f"auth_{event.event_type}",
            "entity_type": "auth",
            "details": {
                "event_type": event.event_type,
                "email_masked": masked_email,
                "error": event.error_message if event.event_type == "login_failed" else None,
                "metadata": event.metadata
            },
            "ip_address": client_ip,
            "user_agent": user_agent[:255] if user_agent else None,  # Limitar longitud
        }

        # Agregar user_id y tenant_id si existen
        if event.user_id:
            audit_data["user_id"] = event.user_id
        if event.tenant_id:
            audit_data["tenant_id"] = event.tenant_id

        result = supabase.table("audit_logs").insert(audit_data).execute()

        event_id = result.data[0]["id"] if result.data else None

        return AuthEventResponse(
            success=True,
            message=f"Evento {event.event_type} registrado",
            event_id=str(event_id) if event_id else None
        )

    except Exception as e:
        # No fallar por errores de logging
        logger.error(
            "auth_log_event_failed",
            error=str(e),
            event_type=event.event_type
        )
        # Retornar success=True para no bloquear el frontend
        return AuthEventResponse(
            success=True,
            message="Evento procesado (con advertencias)"
        )


@router.get("/events/recent")
async def get_recent_auth_events(
    limit: int = 50,
    event_type: Optional[str] = None
):
    """
    Obtiene eventos de autenticación recientes (para dashboard de admin)

    Requiere permisos de administrador (TODO: agregar auth check)
    """
    try:
        supabase = get_supabase_admin_client()

        query = supabase.table("audit_logs")\
            .select("*")\
            .like("action", "auth_%")\
            .order("created_at", desc=True)\
            .limit(limit)

        if event_type:
            query = query.eq("action", f"auth_{event_type}")

        result = query.execute()

        return {
            "events": result.data or [],
            "count": len(result.data) if result.data else 0
        }

    except Exception as e:
        logger.error("get_auth_events_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Error al obtener eventos de autenticación"
        )


@router.get("/stats")
async def get_auth_stats():
    """
    Obtiene estadísticas de autenticación (para métricas)

    - Total de logins exitosos hoy
    - Total de logins fallidos hoy
    - Usuarios activos
    """
    try:
        supabase = get_supabase_admin_client()

        # Obtener fecha de hoy
        today = datetime.utcnow().strftime("%Y-%m-%d")

        # Contar logins exitosos hoy
        logins_result = supabase.table("audit_logs")\
            .select("id", count="exact")\
            .eq("action", "auth_login_success")\
            .gte("created_at", f"{today}T00:00:00")\
            .execute()

        # Contar logins fallidos hoy
        failed_result = supabase.table("audit_logs")\
            .select("id", count="exact")\
            .eq("action", "auth_login_failed")\
            .gte("created_at", f"{today}T00:00:00")\
            .execute()

        # Contar logouts hoy
        logouts_result = supabase.table("audit_logs")\
            .select("id", count="exact")\
            .eq("action", "auth_logout")\
            .gte("created_at", f"{today}T00:00:00")\
            .execute()

        return {
            "date": today,
            "logins_success": logins_result.count or 0,
            "logins_failed": failed_result.count or 0,
            "logouts": logouts_result.count or 0
        }

    except Exception as e:
        logger.error("get_auth_stats_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Error al obtener estadísticas"
        )
