"""
ControlNot v2 - Dependencies
Dependency injection para FastAPI endpoints
"""
from typing import Generator, Optional
from fastapi import HTTPException, status
import structlog
from functools import lru_cache

# Google Cloud
from google.cloud import vision
from google.oauth2 import service_account
from googleapiclient.discovery import build
import httplib2

# OpenAI
from openai import OpenAI, AsyncOpenAI

from app.core.config import settings
from app.services.email_service import EmailService

logger = structlog.get_logger()


# ==========================================
# GLOBAL CLIENTS (Singleton pattern)
# ==========================================
_vision_client = None
_drive_service = None
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


def initialize_drive_service():
    """
    Initialize Google Drive service

    Returns:
        Resource: Drive service instance or None if GOOGLE_DRIVE_FOLDER_ID not set
    """
    global _drive_service

    # Skip if no Drive folder configured
    if not settings.GOOGLE_DRIVE_FOLDER_ID:
        logger.info("⏭️  Google Drive not configured (GOOGLE_DRIVE_FOLDER_ID empty)")
        return None

    if _drive_service is None:
        try:
            credentials = service_account.Credentials.from_service_account_info(
                settings.google_credentials_dict
            )

            try:
                _drive_service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
            except:
                # Fallback method
                http = httplib2.Http(disable_ssl_certificate_validation=False)
                http = credentials.authorize(http)
                _drive_service = build('drive', 'v3', http=http, cache_discovery=False)

            logger.info("✅ Google Drive service initialized")
        except Exception as e:
            logger.error("❌ Error initializing Drive service", error=str(e))
            # Don't raise, Drive is optional
            _drive_service = None

    return _drive_service


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


def get_drive_service():
    """Dependency injector for Google Drive service"""
    return initialize_drive_service()


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
