"""
Database configuration and Supabase client initialization

IMPORTANTE: Los clientes Supabase usan LAZY INITIALIZATION para evitar
bloquear el startup de la aplicación si Supabase no está disponible.
Los clientes se crean la primera vez que se usan, no al importar este módulo.
"""
import time
from typing import Optional
from supabase import create_client, Client
from fastapi import Header, HTTPException
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()

# ========================================
# LAZY SUPABASE CLIENTS
# ========================================

# Clientes singleton (inicializados como None - NO se conectan al importar)
_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Obtiene o crea el cliente Supabase (anon key) con lazy initialization.
    Solo se conecta cuando se llama por primera vez, NO al importar el módulo.

    Returns:
        Client: Authenticated Supabase client
    """
    global _supabase_client

    if _supabase_client is None:
        settings = get_settings()
        try:
            _supabase_client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY
            )
            logger.info("supabase_client_initialized_lazy")
        except Exception as e:
            logger.error("supabase_client_initialization_failed", error=str(e))
            raise

    return _supabase_client


def get_supabase_admin_client() -> Client:
    """
    Obtiene o crea el cliente Supabase admin (service_role key) con lazy initialization.
    Bypasea RLS para operaciones administrativas del backend.

    Returns:
        Client: Admin Supabase client que bypasea RLS
    """
    global _supabase_admin_client

    if _supabase_admin_client is None:
        settings = get_settings()

        # Validar que SERVICE_ROLE_KEY esté configurada correctamente
        service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        if not service_key or service_key in ["TU_SERVICE_ROLE_KEY_AQUI", ""]:
            logger.warning(
                "SUPABASE_SERVICE_ROLE_KEY no configurada o inválida, "
                "usando cliente anon (sujeto a RLS)"
            )
            return get_supabase_client()

        try:
            _supabase_admin_client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=service_key
            )
            logger.info("supabase_admin_client_initialized_lazy")
        except Exception as e:
            logger.error("supabase_admin_client_initialization_failed", error=str(e))
            raise

    return _supabase_admin_client


# ========================================
# LAZY PROXY PARA COMPATIBILIDAD
# ========================================

class _LazySupabaseProxy:
    """
    Proxy que carga el cliente Supabase solo cuando se accede a sus atributos.
    Permite que los imports existentes (from app.database import supabase)
    funcionen sin bloquear el startup.
    """

    def __init__(self, getter_func):
        self._getter = getter_func
        self._client = None

    def __getattr__(self, name):
        if self._client is None:
            self._client = self._getter()
        return getattr(self._client, name)


# Estos objetos NO se conectan al importar - solo cuando se usan por primera vez
supabase = _LazySupabaseProxy(get_supabase_client)
supabase_admin = _LazySupabaseProxy(get_supabase_admin_client)


# ========================================
# AUTHENTICATION HELPERS
# ========================================

async def get_current_user(authorization: str = Header(..., alias="Authorization")) -> dict:
    """
    Extracts and validates the current authenticated user from JWT token

    Args:
        authorization: JWT token from Authorization header

    Returns:
        dict: User data with id, email, etc.

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Remove "Bearer " prefix if present
        token = authorization.replace("Bearer ", "")

        # Log del intento de autenticación (sin exponer el token completo)
        token_preview = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "***"
        logger.debug("auth_attempt", token_preview=token_preview)

        # Get user from Supabase Auth
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            logger.warning(
                "auth_invalid_token",
                reason="user_not_found_in_supabase",
                token_preview=token_preview
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )

        user_data = {
            "id": user_response.user.id,
            "email": user_response.user.email,
            "metadata": user_response.user.user_metadata
        }

        # Log exitoso con contexto útil
        logger.info(
            "auth_success",
            user_id=user_data["id"],
            email=user_data["email"]
        )
        return user_data

    except HTTPException:
        raise
    except Exception as e:
        # Log detallado del error de autenticación
        logger.error(
            "auth_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


async def get_current_tenant_id(authorization: str = Header(..., alias="Authorization")) -> str:
    """
    Extracts tenant_id for the current authenticated user

    Args:
        authorization: JWT token from Authorization header

    Returns:
        str: UUID of the tenant (notaría)

    Raises:
        HTTPException: If tenant lookup fails
    """
    try:
        # Get authenticated user
        user = await get_current_user(authorization)

        # Query users table to get tenant_id
        result = supabase.table('users')\
            .select('tenant_id')\
            .eq('id', user['id'])\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="User tenant not found"
            )

        tenant_id = result.data['tenant_id']

        logger.info(
            "tenant_retrieved",
            user_id=user['id'],
            tenant_id=tenant_id
        )

        return tenant_id

    except HTTPException:
        raise
    except Exception as e:
        logger.error("tenant_lookup_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve tenant information"
        )


# ========================================
# TENANT CONTEXT MANAGER
# ========================================

class TenantContext:
    """
    Context manager for tenant-scoped database operations
    Ensures all queries are automatically filtered by tenant_id
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.client = supabase

    def table(self, table_name: str):
        """
        Returns a query builder with automatic tenant filtering

        Args:
            table_name: Name of the table to query

        Returns:
            Query builder with tenant filter applied
        """
        return self.client.table(table_name).eq('tenant_id', self.tenant_id)

    async def create_document(self, tipo_documento: str, extracted_data: dict, **kwargs) -> dict:
        """
        Creates a new document in the tenant's context

        Args:
            tipo_documento: Type of document
            extracted_data: Extracted data from document
            **kwargs: Additional document fields

        Returns:
            dict: Created document data
        """
        document_data = {
            'tenant_id': self.tenant_id,
            'tipo_documento': tipo_documento,
            'extracted_data': extracted_data,
            **kwargs
        }

        result = self.client.table('documentos')\
            .insert(document_data)\
            .execute()

        logger.info(
            "document_created",
            tenant_id=self.tenant_id,
            tipo=tipo_documento,
            document_id=result.data[0]['id'] if result.data else None
        )

        return result.data[0] if result.data else None

    async def get_documents(
        self,
        tipo_documento: Optional[str] = None,
        estado: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """
        Retrieves documents for the tenant with optional filters

        Args:
            tipo_documento: Filter by document type
            estado: Filter by status
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            list: List of documents
        """
        query = self.table('documentos').select('*')

        if tipo_documento:
            query = query.eq('tipo_documento', tipo_documento)

        if estado:
            query = query.eq('estado', estado)

        result = query\
            .order('created_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        return result.data if result.data else []

    async def get_templates(
        self,
        tipo_documento: Optional[str] = None,
        include_public: bool = True
    ) -> list:
        """
        Retrieves templates available to the tenant

        Args:
            tipo_documento: Filter by document type
            include_public: Include public/shared templates

        Returns:
            list: List of templates
        """
        # Build query for tenant's own templates
        query = self.client.table('templates').select('*')

        if include_public:
            # Include public templates or tenant-specific
            query = query.or_(f'tenant_id.eq.{self.tenant_id},es_publico.eq.true')
        else:
            query = query.eq('tenant_id', self.tenant_id)

        if tipo_documento:
            query = query.eq('tipo_documento', tipo_documento)

        query = query.eq('activo', True)

        result = query.order('created_at', desc=True).execute()

        return result.data if result.data else []

    async def get_preferences(self) -> Optional[dict]:
        """
        Retrieves style preferences for the tenant

        Returns:
            Optional[dict]: Preference data or None
        """
        result = self.client.table('estilo_preferencias')\
            .select('*')\
            .eq('tenant_id', self.tenant_id)\
            .single()\
            .execute()

        return result.data if result.data else None

    async def update_preferences(self, preferences: dict) -> dict:
        """
        Updates or creates style preferences for the tenant

        Args:
            preferences: Preference data to save

        Returns:
            dict: Updated preference data
        """
        result = self.client.table('estilo_preferencias')\
            .upsert({
                'tenant_id': self.tenant_id,
                **preferences
            })\
            .execute()

        logger.info("preferences_updated", tenant_id=self.tenant_id)

        return result.data[0] if result.data else None


# ========================================
# DEPENDENCY INJECTION
# ========================================

async def get_tenant_context(
    authorization: str = Header(..., alias="Authorization")
) -> TenantContext:
    """
    FastAPI dependency for injecting tenant context into endpoints

    Usage:
        @router.get("/documentos")
        async def list_documents(
            tenant: TenantContext = Depends(get_tenant_context)
        ):
            documents = await tenant.get_documents()
            return documents

    Args:
        authorization: JWT token from header

    Returns:
        TenantContext: Tenant-scoped database context
    """
    tenant_id = await get_current_tenant_id(authorization)
    return TenantContext(tenant_id)


# ========================================
# STORAGE HELPERS
# ========================================

def get_tenant_storage_path(tenant_id: str, category: str, filename: str) -> str:
    """
    Generates storage path for tenant files

    Args:
        tenant_id: UUID of tenant
        category: Category (uploads, outputs, ejemplos)
        filename: Name of file

    Returns:
        str: Full storage path
    """
    return f"{tenant_id}/{category}/{filename}"


async def upload_to_storage(
    bucket: str,
    path: str,
    file_data: bytes,
    content_type: str = "application/octet-stream"
) -> dict:
    """
    Uploads file to Supabase Storage

    Args:
        bucket: Bucket name
        path: File path in storage
        file_data: Binary file data
        content_type: MIME type

    Returns:
        dict: Upload result with path and URL
    """
    start_time = time.time()
    logger.debug(
        "storage_upload_starting",
        bucket=bucket,
        path=path,
        size_bytes=len(file_data),
        content_type=content_type
    )

    try:
        upload_start = time.time()
        result = supabase_admin.storage.from_(bucket).upload(
            path=path,
            file=file_data,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        upload_duration = (time.time() - upload_start) * 1000

        # Get public URL (if bucket is public) or generate signed URL
        url_start = time.time()
        public_url = supabase_admin.storage.from_(bucket).get_public_url(path)
        url_duration = (time.time() - url_start) * 1000

        total_duration = (time.time() - start_time) * 1000

        logger.info(
            "storage_upload_complete",
            bucket=bucket,
            path=path,
            size_bytes=len(file_data),
            upload_ms=round(upload_duration, 2),
            url_ms=round(url_duration, 2),
            total_ms=round(total_duration, 2)
        )

        return {
            "path": path,
            "url": public_url,
            "bucket": bucket
        }

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "storage_upload_failed",
            bucket=bucket,
            path=path,
            error=str(e),
            error_type=type(e).__name__,
            duration_ms=round(duration_ms, 2)
        )
        raise


async def download_from_storage(bucket: str, path: str) -> bytes:
    """
    Downloads file from Supabase Storage

    Args:
        bucket: Bucket name
        path: File path in storage

    Returns:
        bytes: File content
    """
    start_time = time.time()
    logger.debug(
        "storage_download_starting",
        bucket=bucket,
        path=path
    )

    try:
        result = supabase_admin.storage.from_(bucket).download(path)
        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "storage_download_complete",
            bucket=bucket,
            path=path,
            size_bytes=len(result),
            duration_ms=round(duration_ms, 2)
        )

        return result

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "storage_download_failed",
            bucket=bucket,
            path=path,
            error=str(e),
            error_type=type(e).__name__,
            duration_ms=round(duration_ms, 2)
        )
        raise
