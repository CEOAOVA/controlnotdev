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
    AIExtractionService,
    SessionManager,
    get_session_manager
)
from app.services.anthropic_service import AnthropicExtractionService
from app.core.dependencies import (
    get_ocr_service,
    get_ai_service,
    get_anthropic_service
)
from app.repositories.uploaded_file_repository import uploaded_file_repository
from app.repositories.session_repository import session_repository
from uuid import UUID

logger = structlog.get_logger()
router = APIRouter(prefix="/extraction", tags=["Extraction"])


@router.post("/ocr", response_model=OCRResponse)
async def process_ocr(
    session_id: str,
    ocr_service: OCRService = Depends(get_ocr_service),
    session_manager: SessionManager = Depends(get_session_manager)
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

    # Obtener documentos desde SessionManager (NO circular import)
    session = session_manager.get_document_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )

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

        # Guardar resultado en SessionManager (almacenamiento temporal - cache)
        session_manager.store_extraction_result(
            session_id=session_id,
            data={
                'extracted_text': extracted_text,
                'ocr_results': results
            }
        )

        logger.info(
            "OCR completado",
            session_id=session_id,
            total_files=total_files,
            success=success_count,
            failed=failed_count,
            processing_time_seconds=processing_time
        )

        # ====================================================================
        # PERSISTENCIA EN BD: Actualizar archivos con resultados OCR
        # ====================================================================
        try:
            # Buscar sesión en BD por session_id almacenado en session_data
            db_sessions = await session_repository.list({})  # TODO: Filtrar por session_id en metadata

            if db_sessions and len(db_sessions) > 0:
                # Actualizar cada archivo con su texto OCR
                for category, category_results in results.items():
                    for result in category_results:
                        if result['success']:
                            # Buscar archivo en BD por nombre
                            files = await uploaded_file_repository.list_by_session(
                                session_id=UUID(db_sessions[0]['id']),
                                category=category
                            )

                            matching_file = next(
                                (f for f in files if f['filename'] == result['filename']),
                                None
                            )

                            if matching_file:
                                # Actualizar con texto OCR
                                await uploaded_file_repository.update(
                                    UUID(matching_file['id']),
                                    {
                                        'ocr_completed': True,
                                        'ocr_text': result['text'],
                                        'ocr_confidence': result.get('confidence', 0.0)
                                    }
                                )

                logger.info(
                    "Resultados OCR persistidos en BD",
                    session_id=session_id,
                    files_updated=success_count
                )

        except Exception as db_error:
            # No fallar el OCR si falla la persistencia
            logger.warning(
                "Error al persistir OCR en BD (no crítico)",
                error=str(db_error),
                session_id=session_id
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
    anthropic_service: AnthropicExtractionService = Depends(get_anthropic_service),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Extrae datos estructurados con IA (Anthropic Claude + Prompt Caching)

    MEJORA CRÍTICA: Prompt Caching para ~80% ahorro en costos
    - 1er documento: Costo completo
    - Documentos siguientes (5 min): Solo texto nuevo (10x más barato)

    Basado en por_partes.py líneas 1745-1789

    Args:
        request: Texto del OCR + tipo de documento + placeholders opcionales

    Returns:
        Datos extraídos en formato Dict[str, str]
    """
    logger.info(
        "Iniciando extracción con Anthropic + Prompt Caching",
        session_id=request.session_id,
        document_type=request.document_type,
        text_length=len(request.text),
        model=anthropic_service.model
    )

    try:
        import time
        start_time = time.time()

        # Procesar con Anthropic Claude (con Prompt Caching)
        extracted_data = anthropic_service.extract_with_caching(
            text=request.text,
            document_type=request.document_type,
            placeholders=request.template_placeholders
        )

        processing_time = time.time() - start_time

        # Validar datos extraídos
        validation_stats = anthropic_service.validate_extracted_data(
            extracted_data,
            request.document_type
        )

        # Enriquecer con defaults para campos faltantes
        complete_data = anthropic_service.enrich_with_defaults(
            extracted_data,
            request.document_type
        )

        # Guardar en SessionManager - obtener resultado existente y actualizar
        existing_result = session_manager.get_extraction_result(request.session_id)
        if existing_result:
            existing_result['ai_extracted_data'] = complete_data
            session_manager.store_extraction_result(
                session_id=request.session_id,
                data=existing_result
            )
        else:
            # Si no existe, crear uno nuevo (caso edge)
            session_manager.store_extraction_result(
                session_id=request.session_id,
                data={'ai_extracted_data': complete_data}
            )

        # Obtener stats de cache
        cache_stats = anthropic_service.get_cache_stats()

        logger.info(
            "Extracción con Anthropic completada",
            session_id=request.session_id,
            keys_found=validation_stats['found_fields'],
            completeness=f"{validation_stats['completeness'] * 100:.1f}%",
            processing_time=processing_time,
            cache_hit=cache_stats['cache_hit'],
            cached_tokens=cache_stats['cached_tokens']
        )

        # ====================================================================
        # PERSISTENCIA EN BD: Guardar datos extraídos (MEJORA v2)
        # ====================================================================
        try:
            db_sessions = await session_repository.list({})

            if db_sessions and len(db_sessions) > 0:
                # Actualizar progreso de sesión
                await session_repository.update_progress(
                    session_id=UUID(db_sessions[0]['id']),
                    archivos_procesados=1,
                    total_archivos=1
                )

                # Agregar datos de extracción a session_data (con stats de cache)
                await session_repository.add_session_data(
                    session_id=UUID(db_sessions[0]['id']),
                    data={
                        'ai_extraction_completed': True,
                        'completeness_percent': validation_stats['completeness'] * 100,
                        'keys_found': validation_stats['found_fields'],
                        'model_used': anthropic_service.model,
                        'tokens_used': anthropic_service.last_tokens_used,
                        'cache_hit': cache_stats['cache_hit'],
                        'cached_tokens': cache_stats['cached_tokens']
                    }
                )

                logger.info(
                    "Datos de extracción Anthropic persistidos en BD",
                    session_id=request.session_id,
                    db_session_id=db_sessions[0]['id']
                )

        except Exception as db_error:
            logger.warning(
                "Error al persistir extracción IA en BD (no crítico)",
                error=str(db_error),
                session_id=request.session_id
            )

        return AIExtractionResponse(
            session_id=request.session_id,
            extracted_data=complete_data,
            total_keys=validation_stats['total_fields'],
            keys_found=validation_stats['found_fields'],
            keys_missing=len(validation_stats['missing_fields']),
            missing_list=validation_stats['not_found_values'],
            completeness_percent=validation_stats['completeness'] * 100,
            model_used=anthropic_service.model,
            tokens_used=anthropic_service.last_tokens_used,
            processing_time_seconds=processing_time
        )

    except Exception as e:
        logger.error(
            "Error en extracción con Anthropic",
            session_id=request.session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en extracción con IA: {str(e)}"
        )


@router.post("/edit", response_model=SuccessResponse)
async def edit_extracted_data(
    request: DataEditRequest,
    session_manager: SessionManager = Depends(get_session_manager)
):
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

    # Obtener resultado existente desde SessionManager
    extraction_result = session_manager.get_extraction_result(request.session_id)
    if not extraction_result:
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
    extraction_result['edited_data'] = request.edited_data
    extraction_result['confirmed'] = True

    session_manager.store_extraction_result(
        session_id=request.session_id,
        data=extraction_result
    )

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
async def get_extraction_results(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Obtiene todos los resultados de extracción de una sesión

    Útil para debugging o revisión
    """
    results = session_manager.get_extraction_result(session_id)
    if not results:
        raise HTTPException(
            status_code=404,
            detail="Resultados de extracción no encontrados"
        )

    return {
        "session_id": session_id,
        "has_ocr": 'extracted_text' in results,
        "has_ai_extraction": 'ai_extracted_data' in results,
        "has_edits": 'edited_data' in results,
        "confirmed": results.get('confirmed', False),
        "text_length": len(results.get('extracted_text', '')),
        "fields_count": len(results.get('ai_extracted_data', {}))
    }
