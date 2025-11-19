"""
ControlNot v2 - Documents Endpoints
Endpoints para categorización y generación de documentos

Rutas:
- GET    /api/documents/categories       - Obtener categorías por tipo
- POST   /api/documents/upload           - Subir documentos categorizados
- POST   /api/documents/generate         - Generar documento final
- GET    /api/documents/download/{id}    - Descargar documento generado
- POST   /api/documents/send-email       - Enviar documento por email
"""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import StreamingResponse
import structlog
import uuid
from io import BytesIO

from app.schemas import (
    CategoriesResponse,
    CategorizedDocumentsUploadResponse,
    DocumentGenerationRequest,
    DocumentGenerationResponse,
    DocumentGenerationStats,
    UploadedFileInfo,
    SuccessResponse,
    ErrorResponse,
    EmailRequest,
    EmailResponse
)
from app.services import (
    get_categories_for_type,
    DocumentGenerator
)
from app.services.email_service import EmailService
from app.core.dependencies import get_email_service

logger = structlog.get_logger()
router = APIRouter(prefix="/documents", tags=["Documents"])


# Storage para documentos subidos y generados
_document_sessions = {}
_generated_documents = {}


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories(document_type: str):
    """
    Obtiene las 3 categorías para un tipo de documento

    Basado en por_partes.py líneas 1959-2182

    Returns:
        - parte_a: Primera categoría (Vendedor, Donador, etc.)
        - parte_b: Segunda categoría (Comprador, Donatario, etc.)
        - otros: Tercera categoría (Inmueble, Patrimonio, etc.)
    """
    logger.info("Obteniendo categorías", document_type=document_type)

    try:
        categories = get_categories_for_type(document_type)

        return CategoriesResponse(
            parte_a=categories['parte_a'],
            parte_b=categories['parte_b'],
            otros=categories['otros'],
            document_type=document_type
        )

    except Exception as e:
        logger.error(
            "Error al obtener categorías",
            document_type=document_type,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener categorías: {str(e)}"
        )


@router.post("/upload", response_model=CategorizedDocumentsUploadResponse)
async def upload_categorized_documents(
    document_type: str = Form(...),
    template_id: str = Form(...),
    parte_a: List[UploadFile] = File(default=[]),
    parte_b: List[UploadFile] = File(default=[]),
    otros: List[UploadFile] = File(default=[])
):
    """
    Sube documentos categorizados por rol

    Basado en por_partes.py líneas 2184-2291

    Args:
        document_type: Tipo de documento ('compraventa', 'donacion', etc.)
        template_id: ID del template asociado
        parte_a: Archivos de la primera categoría
        parte_b: Archivos de la segunda categoría
        otros: Archivos de la tercera categoría

    Returns:
        Confirmación con session_id para continuar el proceso
    """
    logger.info(
        "Upload de documentos categorizados",
        document_type=document_type,
        template_id=template_id,
        parte_a_count=len(parte_a),
        parte_b_count=len(parte_b),
        otros_count=len(otros)
    )

    try:
        # Validar que al menos haya un archivo
        total_files = len(parte_a) + len(parte_b) + len(otros)
        if total_files == 0:
            raise HTTPException(
                status_code=400,
                detail="Debe subir al menos un archivo"
            )

        # Generar ID de sesión
        session_id = f"session_{uuid.uuid4().hex[:12]}"

        # Procesar archivos por categoría
        files_info = []
        categorized_files = {
            'parte_a': [],
            'parte_b': [],
            'otros': []
        }

        async def process_category_files(files: List[UploadFile], category: str):
            for file in files:
                content = await file.read()

                # Guardar info del archivo
                file_info = UploadedFileInfo(
                    filename=file.filename,
                    size_bytes=len(content),
                    content_type=file.content_type,
                    category=category
                )
                files_info.append(file_info)

                # Guardar contenido
                categorized_files[category].append({
                    'name': file.filename,
                    'content': content,
                    'content_type': file.content_type
                })

                logger.debug(
                    "Archivo procesado",
                    filename=file.filename,
                    category=category,
                    size=len(content)
                )

        # Procesar todas las categorías
        await process_category_files(parte_a, 'parte_a')
        await process_category_files(parte_b, 'parte_b')
        await process_category_files(otros, 'otros')

        # Guardar en sesión
        _document_sessions[session_id] = {
            'document_type': document_type,
            'template_id': template_id,
            'categorized_files': categorized_files,
            'files_info': files_info
        }

        logger.info(
            "Documentos categorizados guardados",
            session_id=session_id,
            total_files=total_files
        )

        return CategorizedDocumentsUploadResponse(
            session_id=session_id,
            files_received={
                'parte_a': len(parte_a),
                'parte_b': len(parte_b),
                'otros': len(otros)
            },
            total_files=total_files,
            files=files_info,
            message=f"{total_files} archivos recibidos, listos para procesar"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error al procesar documentos categorizados",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar documentos: {str(e)}"
        )


@router.post("/generate", response_model=DocumentGenerationResponse)
async def generate_document(request: DocumentGenerationRequest):
    """
    Genera el documento final con los datos extraídos

    Basado en por_partes.py líneas 1688-1743

    Proceso:
    1. Obtiene el template de la sesión
    2. Reemplaza placeholders con los datos
    3. Aplica formato negrita (**texto**)
    4. Guarda el documento generado
    5. Retorna URL de descarga
    """
    logger.info(
        "Generando documento",
        template_id=request.template_id,
        output_filename=request.output_filename,
        placeholders_count=len(request.placeholders)
    )

    try:
        # Verificar que el template existe (importar desde templates.py session)
        from app.api.endpoints.templates import _template_sessions

        if request.template_id not in _template_sessions:
            raise HTTPException(
                status_code=404,
                detail="Template no encontrado en sesión"
            )

        template_session = _template_sessions[request.template_id]
        template_content = template_session['content']

        # Generar documento
        generator = DocumentGenerator()

        document_content, stats = generator.generate_document(
            template_content=template_content,
            responses=request.responses,
            placeholders=request.placeholders,
            output_filename=request.output_filename
        )

        # Generar ID para el documento
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"

        # Guardar documento generado
        _generated_documents[doc_id] = {
            'content': document_content,
            'filename': f"{request.output_filename}.docx",
            'size': len(document_content),
            'stats': stats
        }

        logger.info(
            "Documento generado exitosamente",
            doc_id=doc_id,
            filename=request.output_filename,
            size=len(document_content),
            placeholders_replaced=stats['total_replaced']
        )

        # Calcular lista de placeholders faltantes
        missing_list = []
        for placeholder in request.placeholders:
            value = request.responses.get(placeholder, "")
            # Un placeholder está faltante si:
            # 1. No está en responses, O
            # 2. Su valor es vacío, O
            # 3. Su valor es "No encontrado"
            if not value or value == "No encontrado" or "NO ENCONTRADO" in value.upper():
                missing_list.append(placeholder)

        # Crear response con estadísticas
        generation_stats = DocumentGenerationStats(
            placeholders_replaced=stats['total_replaced'],
            placeholders_missing=stats['missing'],
            missing_list=missing_list,
            replaced_in_body=stats.get('replaced_in_body', 0),
            replaced_in_tables=stats.get('replaced_in_tables', 0),
            replaced_in_headers=stats.get('replaced_in_headers', 0),
            replaced_in_footers=stats.get('replaced_in_footers', 0),
            bold_conversions=stats.get('bold_conversions', 0)
        )

        return DocumentGenerationResponse(
            success=True,
            document_id=doc_id,
            filename=f"{request.output_filename}.docx",
            download_url=f"/api/documents/download/{doc_id}",
            size_bytes=len(document_content),
            stats=generation_stats,
            message=f"Documento generado: {stats['total_replaced']} placeholders reemplazados"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error al generar documento",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar documento: {str(e)}"
        )


@router.get("/download/{doc_id}")
async def download_document(doc_id: str):
    """
    Descarga un documento generado

    Returns:
        StreamingResponse con el archivo .docx
    """
    logger.info("Descargando documento", doc_id=doc_id)

    if doc_id not in _generated_documents:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado"
        )

    doc = _generated_documents[doc_id]

    # Crear stream del documento
    document_stream = BytesIO(doc['content'])

    logger.info(
        "Documento servido para descarga",
        doc_id=doc_id,
        filename=doc['filename']
    )

    return StreamingResponse(
        document_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename={doc['filename']}"
        }
    )


@router.post("/send-email", response_model=EmailResponse)
async def send_document_email(
    request: EmailRequest,
    email_service: EmailService = Depends(get_email_service)
):
    """
    Envía un documento generado por email

    Basado en por_partes.py líneas 1885-1909

    Args:
        request: EmailRequest con to_email, subject, body, document_id
        email_service: EmailService dependency

    Returns:
        EmailResponse con confirmación del envío

    Raises:
        HTTPException 404: Si el documento no existe
        HTTPException 500: Si falla el envío del email
    """
    logger.info(
        "Enviando documento por email",
        to_email=request.to_email,
        document_id=request.document_id
    )

    try:
        # Verificar que el documento existe
        if request.document_id not in _generated_documents:
            raise HTTPException(
                status_code=404,
                detail=f"Documento no encontrado: {request.document_id}"
            )

        doc = _generated_documents[request.document_id]

        # Preparar adjunto
        attachment_data = {
            'content': doc['content'],
            'filename': doc['filename']
        }

        # Enviar email usando EmailService (async)
        await email_service.send_email_async(
            to_email=request.to_email,
            subject=request.subject,
            body=request.body,
            attachment_data=attachment_data,
            html=request.html
        )

        logger.info(
            "Email enviado exitosamente",
            to_email=request.to_email,
            document_id=request.document_id,
            filename=doc['filename']
        )

        return EmailResponse(
            success=True,
            message=f"Email enviado exitosamente a {request.to_email}",
            to_email=request.to_email,
            document_filename=doc['filename']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error al enviar email",
            to_email=request.to_email,
            document_id=request.document_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar email: {str(e)}"
        )
