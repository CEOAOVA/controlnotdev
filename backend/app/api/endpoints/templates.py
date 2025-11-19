"""
ControlNot v2 - Templates Endpoints
Endpoints para upload y procesamiento de templates Word

Rutas:
- POST   /api/templates/upload          - Subir template Word
- GET    /api/templates/list            - Listar templates disponibles
- POST   /api/templates/confirm         - Confirmar template y tipo
- GET    /api/types                     - Listar tipos de documento
"""
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
import structlog
import uuid

from app.schemas import (
    TemplateUploadResponse,
    PlaceholderExtractionResponse,
    TemplateConfirmRequest,
    TemplateListResponse,
    DocumentTypesResponse,
    SuccessResponse,
    ErrorResponse
)
from app.services import (
    extract_placeholders_from_template,
    detect_document_type,
    map_placeholders_to_keys_by_type,
    DriveStorageService,
    LocalStorageService,
    get_all_document_types
)
from app.core.dependencies import (
    get_drive_service,
    get_local_storage
)
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/templates", tags=["Templates"])


# Session storage simple (en producción usar Redis)
_template_sessions = {}


@router.post("/upload", response_model=PlaceholderExtractionResponse)
async def upload_template(
    file: UploadFile = File(..., description="Archivo .docx del template")
):
    """
    Sube un template Word y extrae sus placeholders

    Proceso:
    1. Valida que sea archivo .docx
    2. Extrae placeholders del documento
    3. Auto-detecta tipo de documento
    4. Mapea placeholders a claves estándar
    5. Retorna toda la información procesada

    Basado en por_partes.py líneas 1458-1502, 1639-1684
    """
    logger.info("Upload de template recibido", filename=file.filename)

    # Validar extensión
    if not file.filename.endswith('.docx'):
        logger.error("Archivo no es .docx", filename=file.filename)
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un documento Word (.docx)"
        )

    try:
        # Leer contenido del archivo
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="El archivo está vacío"
            )

        # Extraer placeholders
        placeholders = extract_placeholders_from_template(content)

        if not placeholders or len(placeholders) == 0:
            raise HTTPException(
                status_code=400,
                detail="No se detectaron placeholders en el template"
            )

        # Auto-detectar tipo de documento
        document_type = detect_document_type(placeholders, file.filename)

        # Mapear placeholders a claves estándar
        placeholder_mapping = map_placeholders_to_keys_by_type(
            placeholders,
            document_type,
            file.filename
        )

        # Generar ID de sesión
        template_id = f"tpl_{uuid.uuid4().hex[:12]}"

        # Guardar en sesión
        _template_sessions[template_id] = {
            'content': content,
            'filename': file.filename,
            'placeholders': placeholders,
            'document_type': document_type,
            'placeholder_mapping': placeholder_mapping
        }

        logger.info(
            "Template procesado exitosamente",
            template_id=template_id,
            filename=file.filename,
            document_type=document_type,
            placeholders_count=len(placeholders)
        )

        return PlaceholderExtractionResponse(
            template_id=template_id,
            template_name=file.filename,
            document_type=document_type,
            placeholders=placeholders,
            placeholder_mapping=placeholder_mapping,
            total_placeholders=len(placeholders)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error al procesar template",
            filename=file.filename,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el template: {str(e)}"
        )


@router.get("/list", response_model=TemplateListResponse)
async def list_templates(
    source: Optional[str] = Query(
        None,
        description="Filtrar por fuente: 'drive', 'local', o None para ambos"
    ),
    drive_service: DriveStorageService = Depends(get_drive_service),
    local_storage: LocalStorageService = Depends(get_local_storage)
):
    """
    Lista templates disponibles de Google Drive y/o almacenamiento local

    Basado en por_partes.py líneas 1814-1854
    """
    logger.info("Listando templates", source=source)

    try:
        all_templates = []
        sources_count = {}

        # Obtener de Drive si corresponde
        if source in [None, 'drive']:
            try:
                drive_templates = drive_service.get_templates()
                all_templates.extend(drive_templates)
                sources_count['drive'] = len(drive_templates)
                logger.debug("Templates de Drive obtenidos", count=len(drive_templates))
            except Exception as e:
                logger.warning("Error al obtener templates de Drive", error=str(e))
                sources_count['drive'] = 0

        # Obtener de Local si corresponde
        if source in [None, 'local']:
            try:
                local_templates = local_storage.get_templates()
                all_templates.extend(local_templates)
                sources_count['local'] = len(local_templates)
                logger.debug("Templates locales obtenidos", count=len(local_templates))
            except Exception as e:
                logger.warning("Error al obtener templates locales", error=str(e))
                sources_count['local'] = 0

        logger.info(
            "Templates listados",
            total=len(all_templates),
            sources=sources_count
        )

        return TemplateListResponse(
            templates=all_templates,
            total_count=len(all_templates),
            sources=sources_count
        )

    except Exception as e:
        logger.error(
            "Error al listar templates",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar templates: {str(e)}"
        )


@router.post("/confirm", response_model=SuccessResponse)
async def confirm_template(request: TemplateConfirmRequest):
    """
    Confirma el template y tipo de documento seleccionado

    El usuario puede cambiar el tipo auto-detectado si es necesario
    """
    logger.info(
        "Confirmando template",
        template_id=request.template_id,
        document_type=request.document_type
    )

    # Verificar que el template existe en sesión
    if request.template_id not in _template_sessions:
        raise HTTPException(
            status_code=404,
            detail="Template no encontrado en sesión"
        )

    if not request.confirmed:
        raise HTTPException(
            status_code=400,
            detail="La confirmación debe ser true"
        )

    # Actualizar tipo de documento si cambió
    session = _template_sessions[request.template_id]
    if session['document_type'] != request.document_type:
        logger.info(
            "Tipo de documento actualizado",
            template_id=request.template_id,
            old_type=session['document_type'],
            new_type=request.document_type
        )

        # Re-mapear placeholders con el nuevo tipo
        placeholder_mapping = map_placeholders_to_keys_by_type(
            session['placeholders'],
            request.document_type,
            session['filename']
        )

        session['document_type'] = request.document_type
        session['placeholder_mapping'] = placeholder_mapping

    session['confirmed'] = True

    return SuccessResponse(
        message=f"Template confirmado: {session['filename']}",
        data={
            "template_id": request.template_id,
            "document_type": request.document_type,
            "placeholders_count": len(session['placeholders'])
        }
    )


@router.get("/types", response_model=DocumentTypesResponse)
async def list_document_types():
    """
    Lista todos los tipos de documento soportados

    Basado en por_partes.py líneas 1363-1384
    """
    logger.info("Listando tipos de documento")

    try:
        document_types = get_all_document_types()

        return DocumentTypesResponse(
            document_types=document_types,
            total_types=len(document_types)
        )

    except Exception as e:
        logger.error(
            "Error al listar tipos de documento",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar tipos: {str(e)}"
        )


@router.get("/{template_id}")
async def get_template_info(template_id: str):
    """
    Obtiene información de un template por ID de sesión
    """
    if template_id not in _template_sessions:
        raise HTTPException(
            status_code=404,
            detail="Template no encontrado"
        )

    session = _template_sessions[template_id]

    return {
        "template_id": template_id,
        "filename": session['filename'],
        "document_type": session['document_type'],
        "placeholders_count": len(session['placeholders']),
        "confirmed": session.get('confirmed', False)
    }
