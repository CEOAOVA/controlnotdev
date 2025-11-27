"""
Database configuration and Supabase client initialization
"""
from typing import Optional
from supabase import create_client, Client
from fastapi import Header, HTTPException
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# ========================================
# SUPABASE CLIENT
# ========================================

def get_supabase_client() -> Client:
    """
    Creates and returns Supabase client instance

    Returns:
        Client: Authenticated Supabase client
    """
    try:
        supabase: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )

        logger.info("supabase_client_initialized")
        return supabase

    except Exception as e:
        logger.error("supabase_client_initialization_failed", error=str(e))
        raise


# Global Supabase client instance
supabase: Client = get_supabase_client()


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

        # Get user from Supabase Auth
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )

        user_data = {
            "id": user_response.user.id,
            "email": user_response.user.email,
            "metadata": user_response.user.user_metadata
        }

        logger.info("user_authenticated", user_id=user_data["id"])
        return user_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error("authentication_failed", error=str(e))
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
    try:
        result = supabase.storage.from_(bucket).upload(
            path=path,
            file=file_data,
            file_options={"content-type": content_type}
        )

        # Get public URL (if bucket is public) or generate signed URL
        public_url = supabase.storage.from_(bucket).get_public_url(path)

        logger.info(
            "file_uploaded_to_storage",
            bucket=bucket,
            path=path,
            size=len(file_data)
        )

        return {
            "path": path,
            "url": public_url,
            "bucket": bucket
        }

    except Exception as e:
        logger.error("storage_upload_failed", bucket=bucket, path=path, error=str(e))
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
    try:
        result = supabase.storage.from_(bucket).download(path)

        logger.info("file_downloaded_from_storage", bucket=bucket, path=path)

        return result

    except Exception as e:
        logger.error("storage_download_failed", bucket=bucket, path=path, error=str(e))
        raise
