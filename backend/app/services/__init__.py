"""
ControlNot v2 - Services Package
Exports de todos los servicios del backend

Servicios disponibles:
1. classification_service - Auto-detección de tipo de documento
2. categorization_service - Gestión de categorías por rol
3. template_service - Extracción de placeholders de templates Word
4. mapping_service - Mapeo de placeholders a claves estándar
5. storage_service - Almacenamiento dual (Drive + Local)
6. ocr_service - OCR async paralelo con Google Vision
7. ai_service - Extracción con LLMs (OpenRouter + OpenAI)
8. document_service - Generación de documentos Word
9. email_service - Envío de emails SMTP (sync + async)
"""

# Classification Service
from app.services.classification_service import (
    detect_document_type,
    get_document_type_display_name,
    validate_document_type,
    get_all_document_types
)

# Categorization Service
from app.services.categorization_service import (
    load_categories,
    get_categories_for_type,
    get_category_names,
    get_expected_documents,
    validate_category,
    get_all_categories
)

# Template Service
from app.services.template_service import (
    PlaceholderExtractor,
    extract_placeholders_from_template,
    validate_template_content
)

# Mapping Service
from app.services.mapping_service import (
    PlaceholderMapper,
    map_placeholders_to_keys_by_type,
    validate_mapping_quality
)

# Storage Service
from app.services.storage_service import (
    DriveStorageService,
    LocalStorageService
)

# OCR Service
from app.services.ocr_service import (
    OCRService,
    create_ocr_service
)

# AI Service
from app.services.ai_service import (
    AIExtractionService,
    get_available_models
)

# Document Service
from app.services.document_service import (
    DocumentGenerator,
    generate_document_with_dynamic_placeholders
)

# Email Service
from app.services.email_service import (
    EmailService,
    send_email_smtp
)

__all__ = [
    # Classification
    "detect_document_type",
    "get_document_type_display_name",
    "validate_document_type",
    "get_all_document_types",

    # Categorization
    "load_categories",
    "get_categories_for_type",
    "get_category_names",
    "get_expected_documents",
    "validate_category",
    "get_all_categories",

    # Template
    "PlaceholderExtractor",
    "extract_placeholders_from_template",
    "validate_template_content",

    # Mapping
    "PlaceholderMapper",
    "map_placeholders_to_keys_by_type",
    "validate_mapping_quality",

    # Storage
    "DriveStorageService",
    "LocalStorageService",

    # OCR
    "OCRService",
    "create_ocr_service",

    # AI
    "AIExtractionService",
    "get_available_models",

    # Document
    "DocumentGenerator",
    "generate_document_with_dynamic_placeholders",

    # Email
    "EmailService",
    "send_email_smtp",
]
