"""
ControlNot v2 - Templates Endpoints
Endpoints para upload y procesamiento de templates Word

Rutas:
- POST   /api/templates/upload          - Subir template Word
- GET    /api/templates/list            - Listar templates disponibles
- POST   /api/templates/confirm         - [DEPRECATED] No usado - frontend maneja estado localmente
- GET    /api/types                     - Listar tipos de documento
"""
import time
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
    get_all_document_types,
    SessionManager,
    get_session_manager,
    TemplateVersionService
)
from app.services.supabase_storage_service import SupabaseStorageService
from app.core.dependencies import (
    get_supabase_storage,
    get_optional_tenant_id,
    get_user_tenant_id
)
from app.database import supabase_admin
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/templates", tags=["Templates"])


@router.post("/upload", response_model=PlaceholderExtractionResponse)
async def upload_template(
    file: UploadFile = File(..., description="Archivo .docx del template"),
    session_manager: SessionManager = Depends(get_session_manager),
    tenant_id: str = Depends(get_user_tenant_id),
    supabase_storage: SupabaseStorageService = Depends(get_supabase_storage)
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
    upload_start = time.time()
    logger.info(
        "template_upload_received",
        filename=file.filename,
        tenant_id=tenant_id
    )

    # Validar extensión
    if not file.filename.endswith('.docx'):
        logger.error("template_invalid_extension", filename=file.filename)
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un documento Word (.docx)"
        )

    try:
        # Leer contenido del archivo
        read_start = time.time()
        content = await file.read()
        read_duration = (time.time() - read_start) * 1000

        logger.debug(
            "template_file_read",
            filename=file.filename,
            size_bytes=len(content),
            duration_ms=round(read_duration, 2)
        )

        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="El archivo está vacío"
            )

        # Extraer placeholders
        extract_start = time.time()
        placeholders = extract_placeholders_from_template(content)
        extract_duration = (time.time() - extract_start) * 1000

        logger.info(
            "template_placeholders_extracted",
            filename=file.filename,
            placeholders_count=len(placeholders) if placeholders else 0,
            placeholders_preview=placeholders[:10] if placeholders else [],
            duration_ms=round(extract_duration, 2)
        )

        if not placeholders or len(placeholders) == 0:
            raise HTTPException(
                status_code=400,
                detail="No se detectaron placeholders en el template"
            )

        # Auto-detectar tipo de documento con confidence score
        detect_start = time.time()
        detection_result = detect_document_type(placeholders, file.filename)
        document_type = detection_result['detected_type']
        confidence_score = detection_result['confidence_score']
        requires_confirmation = detection_result['requires_confirmation']
        detect_duration = (time.time() - detect_start) * 1000

        logger.info(
            "template_type_detected",
            filename=file.filename,
            document_type=document_type,
            confidence_score=round(confidence_score, 3),
            confidence_percent=f"{confidence_score * 100:.1f}%",
            requires_confirmation=requires_confirmation,
            duration_ms=round(detect_duration, 2)
        )

        # Mapear placeholders a claves estándar
        map_start = time.time()
        placeholder_mapping = map_placeholders_to_keys_by_type(
            placeholders,
            document_type,
            file.filename
        )
        map_duration = (time.time() - map_start) * 1000

        logger.debug(
            "template_placeholders_mapped",
            filename=file.filename,
            original_count=len(placeholders),
            mapped_count=len(placeholder_mapping) if placeholder_mapping else 0,
            duration_ms=round(map_duration, 2)
        )

        # Generar ID de sesión
        template_id = f"tpl_{uuid.uuid4().hex[:12]}"

        # Guardar en SessionManager (almacenamiento temporal)
        session_manager.store_template_session(
            template_id=template_id,
            data={
                'content': content,
                'filename': file.filename,
                'placeholders': placeholders,
                'document_type': document_type,
                'confidence_score': confidence_score,
                'requires_confirmation': requires_confirmation,
                'placeholder_mapping': placeholder_mapping
            }
        )

        # ============================================================
        # VERSIONAMIENTO: Buscar si existe template con mismo nombre
        # ============================================================
        db_start = time.time()
        db_template_id = template_id  # Default al ID temporal
        version_number = 1
        is_new_template = True
        existing_template = None

        try:
            # Buscar template existente por nombre + tenant
            existing_result = supabase_admin.table('templates').select(
                'id, nombre, storage_path'
            ).eq('nombre', file.filename).eq('tenant_id', tenant_id).limit(1).execute()

            if existing_result.data and len(existing_result.data) > 0:
                existing_template = existing_result.data[0]
                db_template_id = str(existing_template['id'])
                is_new_template = False
                logger.info(
                    "template_existing_found",
                    template_id=db_template_id,
                    filename=file.filename,
                    tenant_id=tenant_id
                )
        except Exception as lookup_error:
            logger.warning(
                "template_lookup_failed",
                error=str(lookup_error),
                filename=file.filename
            )

        # ============================================================
        # Crear nuevo template si no existe
        # ============================================================
        if is_new_template:
            try:
                logger.debug(
                    "template_db_insert_starting",
                    table="templates",
                    tenant_id=tenant_id,
                    filename=file.filename
                )

                template_record = supabase_admin.table('templates').insert({
                    'tenant_id': tenant_id,
                    'tipo_documento': document_type,
                    'nombre': file.filename,
                    'storage_path': None,  # Se actualizará con la versión
                    'placeholders': placeholders,
                    'total_placeholders': len(placeholders)
                }).execute()

                if template_record.data:
                    db_template_id = str(template_record.data[0]['id'])
                    logger.info(
                        "template_db_insert_complete",
                        db_template_id=db_template_id,
                        tenant_id=tenant_id
                    )
            except Exception as db_error:
                logger.error(
                    "template_db_insert_failed",
                    error=str(db_error),
                    error_type=type(db_error).__name__
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al crear template: {str(db_error)}"
                )

        # ============================================================
        # Crear versión del template (nueva o actualización)
        # ============================================================
        version_start = time.time()
        storage_path = None
        try:
            version_service = TemplateVersionService(storage_service=supabase_storage)
            version_result = await version_service.create_version(
                template_id=db_template_id,
                content=content,
                placeholders=placeholders,
                placeholder_mapping=placeholder_mapping,
                tenant_id=tenant_id,
                notas=f"{'Nueva versión' if not is_new_template else 'Versión inicial'} - {document_type}"
            )

            version_number = version_result['version_number']
            storage_path = version_result['storage_path']
            version_duration = (time.time() - version_start) * 1000

            logger.info(
                "template_version_created",
                template_id=db_template_id,
                version_number=version_number,
                is_new_template=is_new_template,
                storage_path=storage_path,
                duration_ms=round(version_duration, 2)
            )
        except Exception as version_error:
            version_duration = (time.time() - version_start) * 1000
            logger.error(
                "template_version_create_failed",
                template_id=db_template_id,
                error=str(version_error),
                duration_ms=round(version_duration, 2)
            )
            # Fallback: guardar directamente en storage sin versionamiento
            try:
                storage_result = await supabase_storage.save_template(
                    file_name=file.filename,
                    content=content,
                    tenant_id=tenant_id
                )
                storage_path = storage_result.get('path', f"{tenant_id}/{file.filename}")
                # Actualizar storage_path del template
                supabase_admin.table('templates').update({
                    'storage_path': storage_path
                }).eq('id', db_template_id).execute()
            except Exception as fallback_error:
                logger.error("template_fallback_storage_failed", error=str(fallback_error))

        db_duration = (time.time() - db_start) * 1000

        # Resumen final del endpoint
        total_duration = (time.time() - upload_start) * 1000
        logger.info(
            "template_upload_endpoint_complete",
            template_id=db_template_id,
            filename=file.filename,
            document_type=document_type,
            version_number=version_number,
            is_new_template=is_new_template,
            placeholders_count=len(placeholders),
            total_ms=round(total_duration, 2),
            extract_ms=round(extract_duration, 2),
            detect_ms=round(detect_duration, 2),
            map_ms=round(map_duration, 2),
            db_ms=round(db_duration, 2)
        )

        return PlaceholderExtractionResponse(
            template_id=db_template_id,
            template_name=file.filename,
            document_type=document_type,
            confidence_score=confidence_score,
            requires_confirmation=requires_confirmation,
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
    include_public: bool = Query(
        True,
        description="Incluir templates públicos"
    ),
    tenant_id: Optional[str] = Depends(get_optional_tenant_id),
    supabase_storage: SupabaseStorageService = Depends(get_supabase_storage)
):
    """
    Lista templates disponibles desde Supabase Storage

    - Templates públicos (carpeta 'public')
    - Templates del tenant autenticado (si hay token)
    """
    logger.info("Listando templates desde Supabase", tenant_id=tenant_id, include_public=include_public)

    try:
        templates = supabase_storage.get_templates(
            tenant_id=tenant_id,
            include_public=include_public
        )

        sources_count = {
            'supabase': len(templates),
            'public': sum(1 for t in templates if t.get('folder') == 'public'),
            'tenant': sum(1 for t in templates if t.get('folder') != 'public')
        }

        logger.info(
            "Templates listados",
            total=len(templates),
            sources=sources_count
        )

        return TemplateListResponse(
            templates=templates,
            total_count=len(templates),
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


@router.post("/confirm", response_model=SuccessResponse, deprecated=True)
async def confirm_template(
    request: TemplateConfirmRequest,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    [DEPRECATED] Confirma el template y tipo de documento seleccionado

    NOTA: Este endpoint ya no es usado por el frontend.
    El estado del documento se maneja localmente en el cliente.
    SessionManager es volatil (en memoria) y causa errores 404.

    Mantenido temporalmente para compatibilidad con versiones antiguas.
    """
    logger.info(
        "Confirmando template",
        template_id=request.template_id,
        document_type=request.document_type
    )

    # Verificar que el template existe en sesión
    session = session_manager.get_template_session(request.template_id)
    if not session:
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

    # Actualizar sesión en SessionManager
    session_manager.store_template_session(
        template_id=request.template_id,
        data=session
    )

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
async def get_template_info(
    template_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Obtiene información de un template por ID de sesión
    """
    session = session_manager.get_template_session(template_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Template no encontrado"
        )

    return {
        "template_id": template_id,
        "filename": session['filename'],
        "document_type": session['document_type'],
        "placeholders_count": len(session['placeholders']),
        "confirmed": session.get('confirmed', False)
    }


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    tenant_id: str = Depends(get_user_tenant_id),
    supabase_storage: SupabaseStorageService = Depends(get_supabase_storage)
):
    """
    Elimina un template del tenant

    Proceso:
    1. Verifica que el template existe y pertenece al tenant
    2. Elimina versiones del template
    3. Elimina archivo de Supabase Storage
    4. Elimina registro de BD

    Args:
        template_id: UUID del template a eliminar
        tenant_id: UUID del tenant (obtenido del token)

    Returns:
        Confirmación de eliminación
    """
    logger.info(
        "delete_template_starting",
        template_id=template_id,
        tenant_id=tenant_id
    )

    try:
        # 1. Verificar que el template existe y pertenece al tenant
        template_result = supabase_admin.table('templates').select(
            'id, nombre, storage_path, tenant_id'
        ).eq('id', template_id).eq('tenant_id', tenant_id).single().execute()

        if not template_result.data:
            logger.warning(
                "delete_template_not_found",
                template_id=template_id,
                tenant_id=tenant_id
            )
            raise HTTPException(
                status_code=404,
                detail="Template no encontrado o no tienes permisos para eliminarlo"
            )

        template = template_result.data
        storage_path = template.get('storage_path')
        template_name = template.get('nombre')

        logger.info(
            "delete_template_found",
            template_id=template_id,
            template_name=template_name,
            storage_path=storage_path
        )

        # 2. Eliminar versiones del template (si existen)
        try:
            versions_result = supabase_admin.table('template_versions').select(
                'id, storage_path'
            ).eq('template_id', template_id).execute()

            if versions_result.data:
                version_count = len(versions_result.data)
                logger.info(
                    "delete_template_versions",
                    template_id=template_id,
                    version_count=version_count
                )

                # Eliminar archivos de versiones en Storage
                for version in versions_result.data:
                    version_path = version.get('storage_path')
                    if version_path:
                        try:
                            supabase_storage.delete_file('templates', version_path)
                        except Exception as storage_err:
                            logger.warning(
                                "delete_version_storage_failed",
                                version_path=version_path,
                                error=str(storage_err)
                            )

                # Eliminar registros de versiones
                supabase_admin.table('template_versions').delete().eq(
                    'template_id', template_id
                ).execute()

                logger.info(
                    "delete_template_versions_complete",
                    template_id=template_id,
                    deleted_count=version_count
                )
        except Exception as version_err:
            logger.warning(
                "delete_template_versions_error",
                template_id=template_id,
                error=str(version_err)
            )

        # 3. Eliminar archivo principal de Storage (si existe)
        if storage_path:
            try:
                supabase_storage.delete_file('templates', storage_path)
                logger.info(
                    "delete_template_storage_complete",
                    storage_path=storage_path
                )
            except Exception as storage_err:
                logger.warning(
                    "delete_template_storage_failed",
                    storage_path=storage_path,
                    error=str(storage_err)
                )

        # 4. Eliminar registro de BD
        supabase_admin.table('templates').delete().eq('id', template_id).execute()

        logger.info(
            "delete_template_complete",
            template_id=template_id,
            template_name=template_name,
            tenant_id=tenant_id
        )

        return SuccessResponse(
            message=f"Template '{template_name}' eliminado correctamente",
            data={
                "template_id": template_id,
                "template_name": template_name,
                "deleted": True
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "delete_template_failed",
            template_id=template_id,
            tenant_id=tenant_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar template: {str(e)}"
        )
