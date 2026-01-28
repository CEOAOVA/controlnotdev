"""
ControlNot v2 - Cancelaciones Endpoints
Endpoints especializados para Cancelaciones de Hipotecas

Migrado de movil_cancelaciones.py

Rutas:
- GET    /api/cancelaciones/categories         - Categorías de documentos
- POST   /api/cancelaciones/upload             - Subir documentos de cancelación
- POST   /api/cancelaciones/extract             - Extraer datos con IA
- POST   /api/cancelaciones/validate           - Validar datos extraídos
- GET    /api/cancelaciones/required-docs      - Lista de documentos requeridos
"""
from typing import List, Dict
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
import structlog
import uuid

from app.schemas import (
    CategoriesResponse,
    SuccessResponse,
    ErrorResponse
)
from app.services import (
    SessionManager,
    get_session_manager
)
from app.services.cancelacion_service import (
    cancelacion_service,
    get_cancelacion_categories,
    validate_cancelacion_data,
    get_cancelacion_prompt,
    get_legacy_keys,
    get_cancelacion_prompt_legacy,
    process_cancelacion_legacy,
    CLAVES_ESTANDARIZADAS_LEGACY
)
from app.core.dependencies import get_ai_service
from app.services.ai_service import AIExtractionService
from app.models.cancelacion import CancelacionKeys, CANCELACION_METADATA

logger = structlog.get_logger()
router = APIRouter(prefix="/cancelaciones", tags=["Cancelaciones"])


@router.get("/categories")
async def get_cancelacion_categories_endpoint():
    """
    Obtiene las categorías de documentos para una cancelación de hipoteca

    Returns:
        Dict con 3 categorías:
        - parte_a: Documentos del Deudor/Propietario
        - parte_b: Documentos del Banco/Acreedor
        - otros: Documentos del Inmueble y Registrales
    """
    logger.info("Obteniendo categorías de cancelación")

    try:
        categories = get_cancelacion_categories()

        return {
            "parte_a": categories['parte_a'],
            "parte_b": categories['parte_b'],
            "otros": categories['otros'],
            "document_type": "cancelacion",
            "total_categories": 3,
            "metadata": {
                "nombre_largo": CANCELACION_METADATA['nombre_largo'],
                "total_campos": CANCELACION_METADATA['total_campos'],
                "descripcion": CANCELACION_METADATA['descripcion']
            }
        }

    except Exception as e:
        logger.error("Error al obtener categorías de cancelación", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener categorías: {str(e)}"
        )


@router.get("/required-docs")
async def get_required_documents():
    """
    Obtiene la lista de documentos CRÍTICOS para una cancelación

    Returns:
        Lista de documentos absolutamente necesarios
    """
    logger.info("Obteniendo documentos requeridos")

    try:
        required_docs = cancelacion_service.get_required_documents()

        return {
            "required_documents": required_docs,
            "total": len(required_docs),
            "document_type": "cancelacion",
            "descripcion": "Documentos críticos para completar una cancelación de hipoteca"
        }

    except Exception as e:
        logger.error("Error al obtener documentos requeridos", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener documentos requeridos: {str(e)}"
        )


@router.get("/metadata")
async def get_cancelacion_metadata():
    """
    Obtiene metadatos completos del modelo de cancelación

    Returns:
        Metadatos del modelo CancelacionKeys
    """
    logger.info("Obteniendo metadatos de cancelación")

    return {
        "metadata": CANCELACION_METADATA,
        "model_info": {
            "name": "CancelacionKeys",
            "description": "Modelo para extracción de datos de Cancelación de Hipotecas",
            "version": "2.0",
            "migrated_from": "movil_cancelaciones.py"
        }
    }


@router.post("/upload")
async def upload_cancelacion_documents(
    session_name: str = Form(..., description="Nombre de la sesión (ej: apellido del deudor)"),
    parte_a: List[UploadFile] = File(default=[], description="Documentos del Deudor"),
    parte_b: List[UploadFile] = File(default=[], description="Documentos del Banco"),
    otros: List[UploadFile] = File(default=[], description="Documentos del Inmueble"),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Sube documentos categorizados para una cancelación de hipoteca

    Args:
        session_name: Identificador de la sesión (nombre del deudor/caso)
        parte_a: Documentos del deudor (INE, RFC, CURP, domicilio)
        parte_b: Documentos del banco (finiquito, carta instrucciones, poder)
        otros: Documentos del inmueble (escritura, certificados, etc.)

    Returns:
        Confirmación con session_id para continuar el proceso
    """
    logger.info(
        "Upload de documentos de cancelación",
        session_name=session_name,
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
                detail="Debe subir al menos un documento"
            )

        # Validar que existan documentos críticos en parte_b (banco)
        if len(parte_b) == 0:
            logger.warning(
                "No se subieron documentos del banco",
                session_name=session_name
            )

        # Generar session_id único
        session_id = f"canc_{uuid.uuid4().hex[:12]}"

        # Procesar y almacenar archivos
        files_by_category = {
            "parte_a": [],
            "parte_b": [],
            "otros": []
        }

        # Procesar parte_a (Deudor)
        for file in parte_a:
            content = await file.read()
            files_by_category["parte_a"].append({
                "filename": file.filename,
                "content_type": file.content_type,
                "content": content,
                "size": len(content)
            })

        # Procesar parte_b (Banco)
        for file in parte_b:
            content = await file.read()
            files_by_category["parte_b"].append({
                "filename": file.filename,
                "content_type": file.content_type,
                "content": content,
                "size": len(content)
            })

        # Procesar otros (Inmueble)
        for file in otros:
            content = await file.read()
            files_by_category["otros"].append({
                "filename": file.filename,
                "content_type": file.content_type,
                "content": content,
                "size": len(content)
            })

        # Guardar en SessionManager (almacenamiento temporal)
        session_manager.store_cancelacion_session(
            session_id=session_id,
            data={
                "session_name": session_name,
                "document_type": "cancelacion",
                "files": files_by_category,
                "total_files": total_files,
                "status": "uploaded",
                "created_at": None  # Se puede agregar timestamp
            }
        )

        logger.info(
            "Documentos de cancelación subidos exitosamente",
            session_id=session_id,
            total_files=total_files
        )

        return {
            "session_id": session_id,
            "session_name": session_name,
            "document_type": "cancelacion",
            "files_received": {
                "parte_a": len(parte_a),
                "parte_b": len(parte_b),
                "otros": len(otros)
            },
            "total_files": total_files,
            "status": "uploaded",
            "next_step": "Procesar OCR usando POST /api/extraction/ocr con este session_id"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error al subir documentos de cancelación",
            session_name=session_name,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir documentos: {str(e)}"
        )


@router.post("/validate")
async def validate_cancelacion(
    session_id: str = Form(...),
    extracted_data: Dict = Form(...),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Valida datos extraídos de una cancelación

    Args:
        session_id: ID de la sesión de cancelación
        extracted_data: Datos extraídos por IA

    Returns:
        Resultado de validación con errores y warnings
    """
    logger.info("Validando datos de cancelación", session_id=session_id)

    try:
        # Verificar que exista la sesión
        session = session_manager.get_cancelacion_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Sesión {session_id} no encontrada"
            )

        # Validar datos
        is_valid, errors, warnings = validate_cancelacion_data(extracted_data)

        # Calcular equivalente en salarios mínimos si falta
        monto_str = extracted_data.get("Suma_Credito", "")
        if monto_str and monto_str != "NO LOCALIZADO":
            try:
                # Extraer números del string (ej: "$250,000.00" -> 250000.00)
                monto_num = float(monto_str.replace("$", "").replace(",", ""))
                valid_salario, equiv_num, equiv_letras = cancelacion_service.validate_salario_minimo(monto_num)

                if valid_salario and not extracted_data.get("Equivalente_Salario_Minimo"):
                    warnings["equivalente_salario_calculado"] = {
                        "numero": equiv_num,
                        "letras": equiv_letras,
                        "mensaje": "Equivalente calculado automáticamente"
                    }
            except ValueError:
                logger.warning("No se pudo calcular equivalente en salarios mínimos", monto=monto_str)

        logger.info(
            "Validación completada",
            session_id=session_id,
            valido=is_valid,
            errores=len(errors),
            warnings=len(warnings)
        )

        return {
            "session_id": session_id,
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "total_errors": len(errors),
            "total_warnings": len(warnings),
            "campos_criticos_validados": is_valid,
            "mensaje": "Datos válidos para generar documento" if is_valid else "Corrija los errores antes de continuar"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error al validar datos de cancelación",
            session_id=session_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en validación: {str(e)}"
        )


@router.get("/prompt")
async def get_extraction_prompt_endpoint():
    """
    Obtiene el prompt optimizado para extracción con IA

    Returns:
        Prompt formateado para modelos de lenguaje
    """
    logger.info("Obteniendo prompt de extracción para cancelación")

    try:
        prompt = get_cancelacion_prompt()

        return {
            "document_type": "cancelacion",
            "prompt": prompt,
            "total_campos": CANCELACION_METADATA['total_campos'],
            "categorias": CANCELACION_METADATA['categorias'],
            "uso": "Usar este prompt como system message en llamadas a GPT-4, Claude, etc."
        }

    except Exception as e:
        logger.error("Error al obtener prompt", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener prompt: {str(e)}"
        )


@router.get("/sessions/{session_id}")
async def get_cancelacion_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Obtiene información de una sesión de cancelación

    Args:
        session_id: ID de la sesión

    Returns:
        Detalles de la sesión
    """
    logger.info("Obteniendo información de sesión", session_id=session_id)

    session = session_manager.get_cancelacion_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Sesión {session_id} no encontrada"
        )

    # No incluir contenido de archivos en respuesta (solo metadata)
    session_info = {
        "session_id": session_id,
        "session_name": session["session_name"],
        "document_type": session["document_type"],
        "total_files": session["total_files"],
        "status": session["status"],
        "files_count": {
            "parte_a": len(session["files"]["parte_a"]),
            "parte_b": len(session["files"]["parte_b"]),
            "otros": len(session["files"]["otros"])
        }
    }

    return session_info


@router.delete("/sessions/{session_id}")
async def delete_cancelacion_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Elimina una sesión de cancelación

    Args:
        session_id: ID de la sesión a eliminar

    Returns:
        Confirmación de eliminación
    """
    logger.info("Eliminando sesión de cancelación", session_id=session_id)

    session = session_manager.get_cancelacion_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Sesión {session_id} no encontrada"
        )

    session_manager.delete_cancelacion_session(session_id)

    logger.info("Sesión eliminada exitosamente", session_id=session_id)

    return {
        "session_id": session_id,
        "deleted": True,
        "mensaje": "Sesión eliminada exitosamente"
    }


# ==============================================================================
# NUEVO: Endpoints LEGACY - Replican EXACTAMENTE movil_cancelaciones.py
# ==============================================================================

@router.get("/legacy/keys")
async def get_legacy_extraction_keys():
    """
    Obtiene las CLAVES_ESTANDARIZADAS_LEGACY exactas de movil_cancelaciones.py

    Estas son las 31 claves que funcionan al 100% en extracción:
    - intermediario_financiero
    - deudor
    - numero_escritura
    - fecha_escritura
    - notario
    - numero_notario
    - ciudad_residencia
    - numero_registro_libro_propiedad
    - tomo_libro_propiedad
    - numero_registro_libro_gravamen
    - tomo_libro_gravamen
    - suma_credito
    - suma_credito_letras
    - equivalente_salario_minimo
    - equivalente_salario_minimo_letras
    - ubicacion_inmueble
    - cesion_credito_fecha
    - cesion_credito_valor
    - constancia_finiquito_numero_oficio
    - constancia_finiquito_fecha_emision
    - carta_instrucciones_numero_oficio
    - carta_instrucciones_fecha_constancia_liquidacion
    - carta_instrucciones_nombre_titular_credito
    - carta_instrucciones_numero_credito
    - carta_instrucciones_tipo_credito
    - carta_instrucciones_fecha_adjudicacion
    - carta_instrucciones_ubicacion_inmueble
    - carta_instrucciones_valor_credito
    - carta_instrucciones_valor_credito_letras
    - carta_instrucciones_numero_registro
    - carta_instrucciones_tomo

    Returns:
        Las 31 claves exactas con sus descripciones
    """
    return {
        "source": "movil_cancelaciones.py lineas 221-253",
        "total_claves": len(CLAVES_ESTANDARIZADAS_LEGACY),
        "claves": CLAVES_ESTANDARIZADAS_LEGACY,
        "nota": "Estas claves funcionan al 100% - NO MODIFICAR"
    }


@router.get("/legacy/prompt")
async def get_legacy_prompt_endpoint():
    """
    Obtiene el prompt EXACTO de movil_cancelaciones.py

    Este prompt simple funciona mejor que el complejo:
    "Eres controlnot, un asistente de notaría. Extrae información en formato JSON..."

    Returns:
        Prompt exacto del sistema original
    """
    prompt = get_cancelacion_prompt_legacy()

    return {
        "source": "movil_cancelaciones.py lineas 332-333",
        "prompt": prompt,
        "parametros_requeridos": {
            "model": "gpt-4o",
            "temperature": 0.5,
            "max_tokens": 1500,
            "top_p": 1
        },
        "nota": "Usar EXACTAMENTE estos parámetros para 100% extracción"
    }


@router.post("/legacy/extract")
async def extract_cancelacion_legacy(
    text: str = Form(..., description="Texto OCR de los documentos de cancelación"),
    ai_service: AIExtractionService = Depends(get_ai_service),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Extrae datos de cancelación usando el método LEGACY de movil_cancelaciones.py

    === MÉTODO QUE FUNCIONA AL 100% ===

    Parámetros EXACTOS que usa internamente:
    - model: gpt-4o
    - temperature: 0.5 (NO 0.0)
    - max_tokens: 1500 (NO 3000)
    - top_p: 1
    - Prompt simple con CLAVES_ESTANDARIZADAS_LEGACY

    Args:
        text: Texto OCR extraído de los documentos

    Returns:
        Dict con los 31 campos extraídos formateados con **negrita** para Word

    Ejemplo de respuesta:
    {
        "deudor": "**Juan Pérez Gómez**",
        "numero_escritura": "**CIENTO VEINTICINCO**",
        "fecha_escritura": "**veinticinco de marzo de dos mil veinticuatro**",
        ...
    }
    """
    import time
    start_time = time.time()

    logger.info(
        "Extrayendo cancelación con método LEGACY (movil_cancelaciones.py)",
        text_length=len(text),
        claves_count=len(CLAVES_ESTANDARIZADAS_LEGACY)
    )

    try:
        # Usar método legacy que replica EXACTAMENTE movil_cancelaciones.py
        extracted_data = ai_service.process_cancelacion_legacy(text)

        processing_time = time.time() - start_time

        # Contar campos extraídos exitosamente
        campos_encontrados = [
            k for k, v in extracted_data.items()
            if v and "NO LOCALIZADO" not in str(v) and "NO ENCONTRADO" not in str(v)
        ]

        campos_no_encontrados = [
            k for k, v in extracted_data.items()
            if not v or "NO LOCALIZADO" in str(v) or "NO ENCONTRADO" in str(v)
        ]

        tasa_exito = len(campos_encontrados) / len(CLAVES_ESTANDARIZADAS_LEGACY) * 100

        logger.info(
            "Extracción legacy completada",
            campos_encontrados=len(campos_encontrados),
            campos_no_encontrados=len(campos_no_encontrados),
            tasa_exito=f"{tasa_exito:.1f}%",
            processing_time=processing_time
        )

        return {
            "source": "movil_cancelaciones.py (método legacy)",
            "extracted_data": extracted_data,
            "stats": {
                "total_claves": len(CLAVES_ESTANDARIZADAS_LEGACY),
                "campos_encontrados": len(campos_encontrados),
                "campos_no_encontrados": len(campos_no_encontrados),
                "tasa_exito_percent": round(tasa_exito, 1),
                "lista_encontrados": campos_encontrados,
                "lista_no_encontrados": campos_no_encontrados
            },
            "parametros_usados": {
                "model": "gpt-4o",
                "temperature": 0.5,
                "max_tokens": 1500,
                "top_p": 1
            },
            "processing_time_seconds": round(processing_time, 2)
        }

    except Exception as e:
        logger.error(
            "Error en extracción legacy",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en extracción legacy: {str(e)}"
        )
