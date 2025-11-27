"""
ControlNot v2 - Dependencies
Dependency injection para FastAPI endpoints
"""
from typing import Generator, Optional
from fastapi import HTTPException, status, Header, Depends
import structlog
from functools import lru_cache

# Google Cloud (Vision API only)
from google.cloud import vision
from google.oauth2 import service_account

# OpenAI
from openai import OpenAI, AsyncOpenAI

from app.core.config import settings
from app.services.email_service import EmailService
from app.services.ocr_service import OCRService
from app.services.ai_service import AIExtractionService
from app.services.storage_service import LocalStorageService
from app.services.supabase_storage_service import SupabaseStorageService
from app.services.session_service import get_session_manager, SessionManager
from app.database import get_current_user, get_current_tenant_id, get_tenant_context, TenantContext

logger = structlog.get_logger()


# ==========================================
# GLOBAL CLIENTS (Singleton pattern)
# ==========================================
_vision_client = None
_openai_client = None
_async_openai_client = None


# ==========================================
# DEPENDENCY: Settings
# ==========================================
def get_settings():
    """Get application settings"""
    return settings


# ==========================================
# CLIENT INITIALIZATION
# ==========================================
def initialize_vision_client():
    """
    Initialize Google Cloud Vision client

    Returns:
        vision.ImageAnnotatorClient: Vision client instance
    """
    global _vision_client

    if _vision_client is None:
        try:
            credentials = service_account.Credentials.from_service_account_info(
                settings.google_credentials_dict
            )
            _vision_client = vision.ImageAnnotatorClient(credentials=credentials)
            logger.info("✅ Google Vision client initialized")
        except Exception as e:
            logger.error("❌ Error initializing Vision client", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize Vision client: {str(e)}"
            )

    return _vision_client


def initialize_openai_client():
    """
    Initialize OpenAI or OpenRouter client

    Returns:
        OpenAI: OpenAI client instance (compatible with OpenRouter)
    """
    global _openai_client

    if _openai_client is None:
        try:
            if settings.use_openrouter:
                # OpenRouter with OpenAI-compatible API
                _openai_client = OpenAI(
                    api_key=settings.OPENROUTER_API_KEY,
                    base_url=settings.OPENROUTER_BASE_URL
                )
                logger.info("✅ OpenRouter client initialized", model=settings.OPENROUTER_MODEL)
            else:
                # Direct OpenAI
                _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized", model=settings.OPENAI_MODEL)
        except Exception as e:
            logger.error("❌ Error initializing AI client", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize AI client: {str(e)}"
            )

    return _openai_client


def initialize_async_openai_client():
    """
    Initialize async OpenAI or OpenRouter client

    Returns:
        AsyncOpenAI: Async OpenAI client instance
    """
    global _async_openai_client

    if _async_openai_client is None:
        try:
            if settings.use_openrouter:
                _async_openai_client = AsyncOpenAI(
                    api_key=settings.OPENROUTER_API_KEY,
                    base_url=settings.OPENROUTER_BASE_URL
                )
                logger.info("✅ Async OpenRouter client initialized")
            else:
                _async_openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ Async OpenAI client initialized")
        except Exception as e:
            logger.error("❌ Error initializing async AI client", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize async AI client: {str(e)}"
            )

    return _async_openai_client


# ==========================================
# DEPENDENCY INJECTORS
# ==========================================
def get_vision_client():
    """Dependency injector for Google Vision client"""
    return initialize_vision_client()


def get_openai_client():
    """Dependency injector for OpenAI/OpenRouter client"""
    return initialize_openai_client()


def get_async_openai_client():
    """Dependency injector for async OpenAI/OpenRouter client"""
    return initialize_async_openai_client()


def get_email_service() -> EmailService:
    """
    Dependency injector for EmailService

    Returns:
        EmailService instance configured with settings
    """
    return EmailService(
        smtp_server=settings.SMTP_SERVER,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        smtp_password=settings.SMTP_PASSWORD,
        from_email=settings.FROM_EMAIL
    )


def get_ocr_service() -> OCRService:
    """
    Dependency injector for OCRService

    Returns:
        OCRService instance with Vision client
    """
    vision_client = get_vision_client()
    return OCRService(vision_client=vision_client)


def get_ai_service() -> AIExtractionService:
    """
    Dependency injector for AIExtractionService

    Returns:
        AIExtractionService instance with OpenAI/OpenRouter client
    """
    ai_client = get_openai_client()
    return AIExtractionService(client=ai_client)


def get_local_storage() -> LocalStorageService:
    """
    Dependency injector for LocalStorageService

    Returns:
        LocalStorageService instance configured with settings
    """
    return LocalStorageService(templates_dir=settings.TEMPLATES_DIR)


def get_supabase_storage() -> SupabaseStorageService:
    """
    Dependency injector for SupabaseStorageService

    Returns:
        SupabaseStorageService instance for Supabase Storage operations
    """
    return SupabaseStorageService()


def get_session_manager_dependency() -> SessionManager:
    """
    Dependency injector for SessionManager

    Returns:
        SessionManager: Global session manager singleton
    """
    return get_session_manager()


# ==========================================
# DEPENDENCY: Validation helpers
# ==========================================
def validate_document_type(doc_type: str) -> str:
    """
    Validate document type against allowed types

    Args:
        doc_type: Document type to validate

    Returns:
        Validated document type

    Raises:
        HTTPException: If document type is invalid
    """
    ALLOWED_TYPES = [
        "compraventa",
        "donacion",
        "testamento",
        "poder",
        "sociedad",
        "otros"
    ]

    if doc_type.lower() not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de documento inválido. Permitidos: {', '.join(ALLOWED_TYPES)}"
        )

    return doc_type.lower()


def validate_role_category(role: str) -> str:
    """
    Validate role category for document upload

    Args:
        role: Role category to validate

    Returns:
        Validated role

    Raises:
        HTTPException: If role is invalid
    """
    ALLOWED_ROLES = ["parte_a", "parte_b", "otros"]

    if role.lower() not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoría de rol inválida. Permitidas: {', '.join(ALLOWED_ROLES)}"
        )

    return role.lower()


# ==========================================
# AUTHENTICATION DEPENDENCIES
# ==========================================
async def get_authenticated_user(
    authorization: str = Header(..., alias="Authorization")
) -> dict:
    """
    FastAPI dependency for extracting authenticated user from JWT token

    Usage:
        @router.post("/protected")
        async def protected_endpoint(
            user: dict = Depends(get_authenticated_user)
        ):
            return {"user_id": user["id"], "email": user["email"]}

    Args:
        authorization: JWT token from Authorization header

    Returns:
        dict: User data with id, email, metadata

    Raises:
        HTTPException: If authentication fails (401)
    """
    return await get_current_user(authorization)


async def get_user_tenant_id(
    authorization: str = Header(..., alias="Authorization")
) -> str:
    """
    FastAPI dependency for extracting tenant_id from authenticated user

    Usage:
        @router.get("/my-documents")
        async def list_my_documents(
            tenant_id: str = Depends(get_user_tenant_id)
        ):
            # Query documents filtered by tenant_id
            return documents

    Args:
        authorization: JWT token from Authorization header

    Returns:
        str: UUID of the user's tenant (notaría)

    Raises:
        HTTPException: If authentication or tenant lookup fails
    """
    return await get_current_tenant_id(authorization)


async def get_authenticated_tenant_context(
    authorization: str = Header(..., alias="Authorization")
) -> TenantContext:
    """
    FastAPI dependency for injecting authenticated tenant context

    This is the RECOMMENDED way to work with multi-tenant data.
    It automatically filters all queries by tenant_id.

    Usage:
        @router.get("/documents")
        async def list_documents(
            tenant: TenantContext = Depends(get_authenticated_tenant_context)
        ):
            # All queries automatically filtered by tenant_id
            documents = await tenant.get_documents(tipo_documento="compraventa")
            return documents

    Args:
        authorization: JWT token from Authorization header

    Returns:
        TenantContext: Tenant-scoped database context

    Raises:
        HTTPException: If authentication fails
    """
    return await get_tenant_context(authorization)


# ==========================================
# OPTIONAL AUTHENTICATION (Backward Compatibility)
# ==========================================
async def get_optional_user(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> Optional[dict]:
    """
    Optional authentication dependency (for gradual migration)

    Returns user data if valid token is provided, None otherwise.
    Does NOT raise exceptions if authentication fails.

    Usage during migration period:
        @router.get("/public-or-protected")
        async def hybrid_endpoint(
            user: Optional[dict] = Depends(get_optional_user)
        ):
            if user:
                # User is authenticated
                return {"message": f"Hello {user['email']}"}
            else:
                # Anonymous access
                return {"message": "Hello guest"}

    Args:
        authorization: Optional JWT token from Authorization header

    Returns:
        Optional[dict]: User data or None if not authenticated
    """
    if not authorization:
        return None

    try:
        return await get_current_user(authorization)
    except HTTPException:
        # Invalid token, but don't raise - return None for optional auth
        return None
    except Exception as e:
        logger.warning(
            "Optional authentication failed",
            error=str(e),
            error_type=type(e).__name__
        )
        return None


async def get_optional_tenant_id(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> Optional[str]:
    """
    Optional tenant_id dependency (for gradual migration)

    Returns tenant_id if valid token is provided, None otherwise.
    Does NOT raise exceptions if authentication fails.

    Usage during migration period:
        @router.post("/upload")
        async def upload_documents(
            tenant_id: Optional[str] = Depends(get_optional_tenant_id)
        ):
            if tenant_id:
                # Save to BD with tenant isolation
                await save_with_tenant(tenant_id, data)
            else:
                # Fallback to SessionManager (in-memory)
                session_manager.store(data)

    Args:
        authorization: Optional JWT token from Authorization header

    Returns:
        Optional[str]: tenant_id UUID or None
    """
    if not authorization:
        return None

    try:
        return await get_current_tenant_id(authorization)
    except HTTPException:
        return None
    except Exception as e:
        logger.warning(
            "Optional tenant lookup failed",
            error=str(e),
            error_type=type(e).__name__
        )
        return None
