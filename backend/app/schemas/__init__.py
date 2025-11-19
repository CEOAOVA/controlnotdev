"""
ControlNot v2 - Schemas Package
Exports de todos los schemas Pydantic para la API

Schemas disponibles:
1. response_schemas - Respuestas HTTP est�ndar
2. template_schemas - Upload y procesamiento de templates Word
3. document_schemas - Categorizaci�n y generaci�n de documentos
4. extraction_schemas - OCR y extracci�n con IA
"""

# ===== RESPONSE SCHEMAS =====
from app.schemas.response_schemas import (
    ProcessingStatusEnum,
    SuccessResponse,
    ErrorResponse,
    ValidationError,
    ValidationErrorResponse,
    ProcessingStatus,
    HealthCheckResponse,
    PaginatedResponse
)

# ===== TEMPLATE SCHEMAS =====
from app.schemas.template_schemas import (
    DocumentTypeEnum,
    TemplateUploadResponse,
    PlaceholderExtractionResponse,
    TemplateConfirmRequest,
    TemplateInfo,
    TemplateListResponse,
    DocumentTypeInfo,
    DocumentTypesResponse
)

# ===== DOCUMENT SCHEMAS =====
from app.schemas.document_schemas import (
    CategoryEnum,
    CategoryInfo,
    CategoriesResponse,
    DocumentGenerationRequest,
    DocumentGenerationStats,
    DocumentGenerationResponse,
    UploadedFileInfo,
    CategorizedDocumentsUploadResponse
)

# ===== EXTRACTION SCHEMAS =====
from app.schemas.extraction_schemas import (
    OCRFileResult,
    OCRResponse,
    AIExtractionRequest,
    AIExtractionResponse,
    DataEditRequest,
    ModelInfo,
    ModelsListResponse
)

# ===== EMAIL SCHEMAS =====
from app.schemas.email_schemas import (
    EmailRequest,
    EmailResponse
)


__all__ = [
    # Response Schemas
    "ProcessingStatusEnum",
    "SuccessResponse",
    "ErrorResponse",
    "ValidationError",
    "ValidationErrorResponse",
    "ProcessingStatus",
    "HealthCheckResponse",
    "PaginatedResponse",

    # Template Schemas
    "DocumentTypeEnum",
    "TemplateUploadResponse",
    "PlaceholderExtractionResponse",
    "TemplateConfirmRequest",
    "TemplateInfo",
    "TemplateListResponse",
    "DocumentTypeInfo",
    "DocumentTypesResponse",

    # Document Schemas
    "CategoryEnum",
    "CategoryInfo",
    "CategoriesResponse",
    "DocumentGenerationRequest",
    "DocumentGenerationStats",
    "DocumentGenerationResponse",
    "UploadedFileInfo",
    "CategorizedDocumentsUploadResponse",

    # Extraction Schemas
    "OCRFileResult",
    "OCRResponse",
    "AIExtractionRequest",
    "AIExtractionResponse",
    "DataEditRequest",
    "ModelInfo",
    "ModelsListResponse",

    # Email Schemas
    "EmailRequest",
    "EmailResponse",
]
