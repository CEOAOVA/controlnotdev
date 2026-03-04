"""
ControlNot v2 - Services Package
Exports de todos los servicios del backend (lazy loading)

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

NOTA: Imports lazy con __getattr__ + importlib para que si un servicio
falla al importar (ej. API key faltante), solo ese endpoint falle,
no la app completa.
"""
import importlib
from typing import Any

# Mapping: nombre exportado -> (módulo, nombre en módulo)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # Classification
    "detect_document_type": ("app.services.classification_service", "detect_document_type"),
    "get_document_type_display_name": ("app.services.classification_service", "get_document_type_display_name"),
    "validate_document_type": ("app.services.classification_service", "validate_document_type"),
    "get_all_document_types": ("app.services.classification_service", "get_all_document_types"),

    # Categorization
    "load_categories": ("app.services.categorization_service", "load_categories"),
    "get_categories_for_type": ("app.services.categorization_service", "get_categories_for_type"),
    "get_category_names": ("app.services.categorization_service", "get_category_names"),
    "get_expected_documents": ("app.services.categorization_service", "get_expected_documents"),
    "validate_category": ("app.services.categorization_service", "validate_category"),
    "get_all_categories": ("app.services.categorization_service", "get_all_categories"),

    # Template
    "PlaceholderExtractor": ("app.services.template_service", "PlaceholderExtractor"),
    "extract_placeholders_from_template": ("app.services.template_service", "extract_placeholders_from_template"),
    "validate_template_content": ("app.services.template_service", "validate_template_content"),

    # Mapping
    "PlaceholderMapper": ("app.services.mapping_service", "PlaceholderMapper"),
    "map_placeholders_to_keys_by_type": ("app.services.mapping_service", "map_placeholders_to_keys_by_type"),
    "validate_mapping_quality": ("app.services.mapping_service", "validate_mapping_quality"),

    # Storage
    "LocalStorageService": ("app.services.storage_service", "LocalStorageService"),
    "SupabaseStorageService": ("app.services.supabase_storage_service", "SupabaseStorageService"),

    # OCR
    "OCRService": ("app.services.ocr_service", "OCRService"),
    "create_ocr_service": ("app.services.ocr_service", "create_ocr_service"),

    # AI
    "AIExtractionService": ("app.services.ai_service", "AIExtractionService"),
    "get_available_models": ("app.services.ai_service", "get_available_models"),

    # Document
    "DocumentGenerator": ("app.services.document_service", "DocumentGenerator"),
    "generate_document_with_dynamic_placeholders": ("app.services.document_service", "generate_document_with_dynamic_placeholders"),

    # Email
    "EmailService": ("app.services.email_service", "EmailService"),
    "send_email_smtp": ("app.services.email_service", "send_email_smtp"),

    # Session
    "SessionManager": ("app.services.session_service", "SessionManager"),
    "get_session_manager": ("app.services.session_service", "get_session_manager"),

    # Model
    "get_fields_for_document_type": ("app.services.model_service", "get_fields_for_document_type"),
    "get_all_document_types_with_fields": ("app.services.model_service", "get_all_document_types_with_fields"),

    # Image Preprocessing
    "ImagePreprocessingService": ("app.services.image_preprocessing_service", "ImagePreprocessingService"),
    "get_image_preprocessing_service": ("app.services.image_preprocessing_service", "get_image_preprocessing_service"),

    # Template Version
    "TemplateVersionService": ("app.services.template_version_service", "TemplateVersionService"),
}

__all__ = list(_LAZY_IMPORTS.keys())


def __getattr__(name: str) -> Any:
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(module_path)
        return getattr(module, attr_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
