"""
ControlNot v2 - Audit Middleware
Middleware para registrar todas las operaciones en audit_logs table

Registra:
- Todas las operaciones de modificación (POST, PUT, DELETE)
- Usuario, tenant, timestamp, IP, user-agent
- Detalles de la operación (path, método, status code)
- Duración de la request

NO registra:
- Operaciones de solo lectura (GET)
- Health checks
- Static files
"""
from fastapi import Request
from typing import Optional
import time
import structlog
from uuid import UUID

from app.database import get_supabase_client

logger = structlog.get_logger()
supabase = get_supabase_client()

# Mapeo de rutas a acciones auditables
ACTION_MAP = {
    ('POST', '/api/clients'): 'create_client',
    ('PUT', '/api/clients'): 'update_client',
    ('DELETE', '/api/clients'): 'delete_client',

    ('POST', '/api/cases'): 'create_case',
    ('PUT', '/api/cases'): 'update_case',
    ('DELETE', '/api/cases'): 'delete_case',

    ('POST', '/api/documents/upload'): 'upload_documents',
    ('POST', '/api/documents/generate'): 'generate_document',
    ('POST', '/api/documents/send-email'): 'send_email',

    ('POST', '/api/extraction/ocr'): 'start_ocr',
    ('POST', '/api/extraction/ai'): 'extract_data',
    ('POST', '/api/extraction/edit'): 'validate_data',

    ('POST', '/api/templates/upload'): 'upload_template',
    ('DELETE', '/api/templates'): 'delete_template',

    ('POST', '/api/cancelaciones/upload'): 'upload_documents',
    ('POST', '/api/cancelaciones/validate'): 'validate_data',
}

# Mapeo de rutas a tipos de entidad
ENTITY_TYPE_MAP = {
    '/api/clients': 'client',
    '/api/cases': 'case',
    '/api/documents': 'document',
    '/api/templates': 'template',
    '/api/extraction': 'session',
    '/api/cancelaciones': 'document',
}


def extract_entity_type(path: str) -> Optional[str]:
    """
    Extrae el tipo de entidad de la ruta

    Args:
        path: Ruta del endpoint (ej: /api/clients/123)

    Returns:
        Tipo de entidad (client, case, document, etc.) o None
    """
    for prefix, entity_type in ENTITY_TYPE_MAP.items():
        if path.startswith(prefix):
            return entity_type
    return 'system'


def get_tenant_id_from_request(request: Request) -> Optional[str]:
    """
    Extrae tenant_id del request (de token o state)

    Args:
        request: FastAPI Request object

    Returns:
        tenant_id o None
    """
    try:
        # TODO: Activar cuando se implemente autenticación
        # Buscar en request.state (seteado por dependency)
        if hasattr(request.state, 'tenant_id'):
            return str(request.state.tenant_id)

        # O buscar en headers de autorización
        # auth_header = request.headers.get('authorization')
        # if auth_header:
        #     return extract_tenant_from_token(auth_header)

        return None
    except Exception:
        return None


def get_user_id_from_request(request: Request) -> Optional[str]:
    """
    Extrae user_id del request (de token o state)

    Args:
        request: FastAPI Request object

    Returns:
        user_id o None
    """
    try:
        # TODO: Activar cuando se implemente autenticación
        if hasattr(request.state, 'user_id'):
            return str(request.state.user_id)

        return None
    except Exception:
        return None


async def audit_middleware(request: Request, call_next):
    """
    Middleware de auditoría que registra todas las operaciones importantes

    Args:
        request: FastAPI Request
        call_next: Siguiente middleware en la cadena

    Returns:
        Response del endpoint
    """
    start_time = time.time()

    # Procesar request
    response = await call_next(request)

    # Calcular duración
    duration_ms = (time.time() - start_time) * 1000

    # Solo auditar operaciones exitosas (2xx y 3xx)
    if 200 <= response.status_code < 400:
        # Buscar acción en el mapa
        route_key = (request.method, request.url.path)
        action = ACTION_MAP.get(route_key)

        # Solo registrar si es una acción auditable
        if action:
            try:
                # Extraer contexto
                tenant_id = get_tenant_id_from_request(request)
                user_id = get_user_id_from_request(request)
                entity_type = extract_entity_type(request.url.path)

                # Preparar registro de auditoría
                audit_data = {
                    'action': action,
                    'entity_type': entity_type,
                    'details': {
                        'method': request.method,
                        'path': request.url.path,
                        'query_params': str(request.query_params),
                        'status_code': response.status_code,
                        'duration_ms': round(duration_ms, 2)
                    },
                    'ip_address': request.client.host if request.client else None,
                    'user_agent': request.headers.get('user-agent')
                }

                # Agregar tenant_id y user_id si existen
                if tenant_id:
                    audit_data['tenant_id'] = tenant_id
                if user_id:
                    audit_data['user_id'] = user_id

                # Guardar en BD
                result = supabase.table('audit_logs').insert(audit_data).execute()

                logger.debug(
                    "Audit log registrado",
                    action=action,
                    entity_type=entity_type,
                    duration_ms=round(duration_ms, 2),
                    tenant_id=tenant_id,
                    user_id=user_id
                )

            except Exception as audit_error:
                # NUNCA fallar el request por error de auditoría
                logger.warning(
                    "Error al registrar audit log (no crítico)",
                    error=str(audit_error),
                    action=action,
                    path=request.url.path
                )

    return response


def should_audit_request(request: Request) -> bool:
    """
    Determina si una request debe ser auditada

    Args:
        request: FastAPI Request

    Returns:
        True si debe auditarse, False si no
    """
    # No auditar GET requests (solo lectura)
    if request.method == 'GET':
        return False

    # No auditar health checks
    if request.url.path.startswith('/health'):
        return False

    # No auditar docs y static
    if request.url.path.startswith(('/docs', '/redoc', '/openapi.json', '/static')):
        return False

    return True
