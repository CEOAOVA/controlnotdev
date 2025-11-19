"""
ControlNot v2 - Extraction Endpoints
Endpoints para OCR y extracción con IA

Rutas:
- POST   /api/extraction/ocr             - Procesar OCR de documentos categorizados
- POST   /api/extraction/ai              - Extraer datos con IA
- POST   /api/extraction/edit            - Editar/confirmar datos extraídos
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import structlog
import asyncio

from app.schemas import (
    OCRResponse,
    AIExtractionRequest,
    AIExtractionResponse,
    DataEditRequest,
    SuccessResponse,
    ProcessingStatus
)
from app.services import (
    OCRService,
    AIExtractionService
)
from app.core.dependencies import (
    get_ocr_service,
    get_ai_service
)

logger = structlog.get_logger()
router = APIRouter(prefix="/extraction", tags=["Extraction"])


# Storage para resultados de extracción
_extraction_results = {}


@router.post("/ocr", response_model=OCRResponse)
async def process_ocr(
    session_id: str,
    ocr_service: OCRService = Depends(get_ocr_service)
):
    """
    Procesa OCR de documentos categorizados en paralelo

    MEJORA CRÍTICA: Procesamiento asíncrono paralelo (5-10x más rápido)

    Basado en por_partes.py líneas 2293-2335

    Args:
        session_id: ID de sesión con documentos categorizados

    Returns:
        Texto consolidado + resultados detallados por categoría
    """
    logger.info("Iniciando procesamiento OCR", session_id=session_id)

    # Obtener documentos de la sesión
    from app.api.endpoints.documents import _document_sessions

    if session_id not in _document_sessions:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )

    session = _document_sessions[session_id]
    categorized_files = session['categorized_files']
    document_type = session['document_type']

    try:
        # Convertir a formato esperado por el servicio OCR
        categorized_docs = {}
        for category, files in categorized_files.items():
            categorized_docs[category] = files

        # Procesar con OCR asíncrono paralelo
        logger.info(
            "Procesando OCR en paralelo",
            total_files=sum(len(files) for files in categorized_files.values())
        )

        import time
        start_time = time.time()

        extracted_text, results = await ocr_service.process_categorized_documents_async(
            categorized_docs,
            document_type
        )

        processing_time = time.time() - start_time

        # Contar éxitos y fallos
        total_files = 0
        success_count = 0
        failed_count = 0

        for category_results in results.values():
            for result in category_results:
                total_files += 1
                if result['success']:
                    success_count += 1
                else:
                    failed_count += 1

        # Guardar resultado en sesión
        _extraction_results[session_id] = {
            'extracted_text': extracted_text,
            'ocr_results': results
        }

        logger.info(
            "OCR completado",
            session_id=session_id,
            total_files=total_files,
            success=success_count,
            failed=failed_count,
            processing_time_seconds=processing_time
        )

        return OCRResponse(
            session_id=session_id,
            extracted_text=extracted_text,
            total_text_length=len(extracted_text),
            files_processed=total_files,
            files_success=success_count,
            files_failed=failed_count,
            processing_time_seconds=processing_time,
            results_by_category=results
        )

    except Exception as e:
        logger.error(
            "Error en procesamiento OCR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en OCR: {str(e)}"
        )


@router.post("/ai", response_model=AIExtractionResponse)
async def extract_with_ai(
    request: AIExtractionRequest,
    ai_service: AIExtractionService = Depends(get_ai_service)
):
    """
    Extrae datos estructurados con IA (OpenRouter/OpenAI)

    MEJORA CRÍTICA: Soporte multi-provider (GPT-4o, Claude, Gemini, Llama)

    Basado en por_partes.py líneas 1745-1789

    Args:
        request: Texto del OCR + tipo de documento + placeholders opcionales

    Returns:
        Datos extraídos en formato Dict[str, str]
    """
    logger.info(
        "Iniciando extracción con IA",
        session_id=request.session_id,
        document_type=request.document_type,
        text_length=len(request.text),
        model=request.model
    )

    try:
        import time
        start_time = time.time()

        # Procesar con IA
        extracted_data = ai_service.process_text_dynamic(
            text=request.text,
            document_type=request.document_type,
            placeholders=request.template_placeholders
        )

        processing_time = time.time() - start_time

        # Validar datos extraídos
        validation_stats = ai_service.validate_extracted_data(
            extracted_data,
            request.document_type
        )

        # Enriquecer con defaults para campos faltantes
        complete_data = ai_service.enrich_with_defaults(
            extracted_data,
            request.document_type
        )

        # Guardar en sesión
        _extraction_results[request.session_id]['ai_extracted_data'] = complete_data

        logger.info(
            "Extracción con IA completada",
            session_id=request.session_id,
            keys_found=validation_stats['found_fields'],
            completeness=f"{validation_stats['completeness'] * 100:.1f}%",
            processing_time=processing_time
        )

        return AIExtractionResponse(
            session_id=request.session_id,
            extracted_data=complete_data,
            total_keys=validation_stats['total_fields'],
            keys_found=validation_stats['found_fields'],
            keys_missing=len(validation_stats['missing_fields']),
            missing_list=validation_stats['not_found_values'],
            completeness_percent=validation_stats['completeness'] * 100,
            model_used=ai_service.model,
            tokens_used=ai_service.last_tokens_used,
            processing_time_seconds=processing_time
        )

    except Exception as e:
        logger.error(
            "Error en extracción con IA",
            session_id=request.session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en extracción con IA: {str(e)}"
        )


@router.post("/edit", response_model=SuccessResponse)
async def edit_extracted_data(request: DataEditRequest):
    """
    Usuario edita/confirma los datos extraídos

    Los datos editados se guardan para la generación del documento
    """
    logger.info(
        "Editando datos extraídos",
        session_id=request.session_id,
        confirmed=request.confirmed,
        fields_count=len(request.edited_data)
    )

    if request.session_id not in _extraction_results:
        raise HTTPException(
            status_code=404,
            detail="Sesión de extracción no encontrada"
        )

    if not request.confirmed:
        raise HTTPException(
            status_code=400,
            detail="La confirmación debe ser true"
        )

    # Guardar datos editados
    _extraction_results[request.session_id]['edited_data'] = request.edited_data
    _extraction_results[request.session_id]['confirmed'] = True

    logger.info(
        "Datos editados confirmados",
        session_id=request.session_id
    )

    return SuccessResponse(
        message="Datos confirmados correctamente",
        data={
            "session_id": request.session_id,
            "fields_count": len(request.edited_data)
        }
    )


@router.get("/{session_id}/results")
async def get_extraction_results(session_id: str):
    """
    Obtiene todos los resultados de extracción de una sesión

    Útil para debugging o revisión
    """
    if session_id not in _extraction_results:
        raise HTTPException(
            status_code=404,
            detail="Resultados de extracción no encontrados"
        )

    results = _extraction_results[session_id]

    return {
        "session_id": session_id,
        "has_ocr": 'extracted_text' in results,
        "has_ai_extraction": 'ai_extracted_data' in results,
        "has_edits": 'edited_data' in results,
        "confirmed": results.get('confirmed', False),
        "text_length": len(results.get('extracted_text', '')),
        "fields_count": len(results.get('ai_extracted_data', {}))
    }
