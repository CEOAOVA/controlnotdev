"""
ControlNot v2 - Cases Endpoints
Endpoints REST para gestión de casos/expedientes
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
import structlog

from app.repositories.case_repository import case_repository
from app.repositories.session_repository import session_repository
from app.repositories.document_repository import document_repository
from app.schemas.case_schemas import (
    CaseCreateRequest,
    CaseUpdateRequest,
    CaseUpdateStatusRequest,
    CaseAddPartyRequest,
    CaseResponse,
    CaseWithClientResponse,
    CaseWithSessionsResponse,
    CaseListResponse,
    CaseStatisticsResponse
)
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("", response_model=CaseWithClientResponse, status_code=201)
async def create_case(
    request: CaseCreateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Crea un nuevo caso/expediente

    Args:
        request: Datos del caso a crear
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Caso creado con datos del cliente

    Raises:
        400: Número de caso duplicado
        500: Error del servidor
    """
    logger.info(
        "create_case_request",
        tenant_id=tenant_id,
        case_number=request.case_number,
        document_type=request.document_type
    )

    try:
        case = await case_repository.create_case(
            tenant_id=UUID(tenant_id),
            client_id=request.client_id,
            case_number=request.case_number,
            document_type=request.document_type,
            description=request.description,
            parties=request.parties,
            metadata=request.metadata
        )

        if not case:
            raise HTTPException(status_code=500, detail="Error al crear caso")

        # Obtener caso con cliente
        case_with_client = await case_repository.get_case_with_client(UUID(case['id']))

        logger.info("case_created", case_id=case['id'], case_number=request.case_number)

        return CaseWithClientResponse(**case_with_client)

    except ValueError as e:
        # Número de caso duplicado
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error("create_case_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al crear caso")


@router.get("", response_model=CaseListResponse)
async def list_cases(
    tenant_id: str = Depends(get_current_tenant_id),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    document_type: Optional[str] = Query(None, description="Filtrar por tipo"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página")
):
    """
    Lista casos de la notaría

    Args:
        tenant_id: UUID de la notaría (inyectado)
        status: Filtrar por estado (opcional)
        document_type: Filtrar por tipo de documento (opcional)
        page: Número de página
        page_size: Tamaño de página

    Returns:
        Lista paginada de casos
    """
    logger.info("list_cases_request", tenant_id=tenant_id, status=status, page=page)

    try:
        offset = (page - 1) * page_size

        # Si hay filtros específicos, usar métodos especializados
        if status:
            cases = await case_repository.list_by_status(
                tenant_id=UUID(tenant_id),
                status=status,
                limit=page_size,
                offset=offset
            )
        elif document_type:
            cases = await case_repository.list_by_document_type(
                tenant_id=UUID(tenant_id),
                document_type=document_type,
                limit=page_size,
                offset=offset
            )
        else:
            # Listar todos
            filters = {}
            cases = await case_repository.list_by_tenant(
                tenant_id=UUID(tenant_id),
                filters=filters,
                limit=page_size,
                offset=offset
            )

        # Contar total
        filters_count = {}
        if status:
            filters_count['status'] = status
        if document_type:
            filters_count['document_type'] = document_type

        total = await case_repository.count_by_tenant(UUID(tenant_id), filters_count)

        return CaseListResponse(
            cases=[CaseResponse(**case) for case in cases],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error("list_cases_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al listar casos")


@router.get("/statistics", response_model=CaseStatisticsResponse)
async def get_case_statistics(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Obtiene estadísticas de casos de la notaría

    Args:
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Estadísticas agregadas de casos
    """
    logger.info("get_case_statistics_request", tenant_id=tenant_id)

    try:
        stats = await case_repository.get_case_statistics(UUID(tenant_id))

        return CaseStatisticsResponse(**stats)

    except Exception as e:
        logger.error("get_case_statistics_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas")


@router.get("/{case_id}", response_model=CaseWithSessionsResponse)
async def get_case(
    case_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Obtiene un caso con todas sus relaciones

    Args:
        case_id: UUID del caso
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Caso con cliente, sesiones y documentos

    Raises:
        404: Caso no encontrado
    """
    logger.info("get_case_request", case_id=str(case_id))

    try:
        # Obtener caso con cliente
        case = await case_repository.get_case_with_client(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        # Obtener sesiones
        sessions = await session_repository.list_by_case(case_id)

        # Obtener documentos
        documents = await document_repository.list_by_case(case_id)

        return CaseWithSessionsResponse(
            **case,
            sessions=[
                {
                    "id": str(s['id']),
                    "tipo_documento": s['tipo_documento'],
                    "estado": s['estado'],
                    "progreso_porcentaje": s['progreso_porcentaje']
                }
                for s in sessions
            ],
            documents_count=len(documents)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_case_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener caso")


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: UUID,
    request: CaseUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Actualiza datos de un caso

    Args:
        case_id: UUID del caso
        request: Campos a actualizar
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Caso actualizado

    Raises:
        404: Caso no encontrado
    """
    logger.info("update_case_request", case_id=str(case_id))

    try:
        # Verificar que existe y pertenece al tenant
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        # Preparar actualizaciones
        updates = request.model_dump(exclude_unset=True)

        if not updates:
            return CaseResponse(**case)

        # Actualizar
        updated_case = await case_repository.update(case_id, updates)

        if not updated_case:
            raise HTTPException(status_code=500, detail="Error al actualizar caso")

        logger.info("case_updated", case_id=str(case_id))

        return CaseResponse(**updated_case)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_case_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar caso")


@router.put("/{case_id}/status", response_model=CaseResponse)
async def update_case_status(
    case_id: UUID,
    request: CaseUpdateStatusRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Actualiza el estado de un caso

    Args:
        case_id: UUID del caso
        request: Nuevo estado
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Caso actualizado

    Raises:
        404: Caso no encontrado
    """
    logger.info("update_case_status_request", case_id=str(case_id), new_status=request.status)

    try:
        # Verificar que existe y pertenece al tenant
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        # Actualizar estado
        updated_case = await case_repository.update_status(case_id, request.status)

        if not updated_case:
            raise HTTPException(status_code=500, detail="Error al actualizar estado")

        logger.info("case_status_updated", case_id=str(case_id), new_status=request.status)

        return CaseResponse(**updated_case)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_case_status_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar estado")


@router.post("/{case_id}/parties", response_model=CaseResponse)
async def add_party_to_case(
    case_id: UUID,
    request: CaseAddPartyRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Agrega una parte involucrada al caso

    Args:
        case_id: UUID del caso
        request: Datos de la parte a agregar
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Caso actualizado

    Raises:
        404: Caso no encontrado
    """
    logger.info("add_party_request", case_id=str(case_id), role=request.role)

    try:
        # Verificar que el caso existe y pertenece al tenant
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        # Preparar datos de la parte
        party_data = {
            "role": request.role,
            "metadata": request.metadata
        }

        if request.client_id:
            party_data["client_id"] = str(request.client_id)
        if request.nombre:
            party_data["nombre"] = request.nombre

        # Agregar parte
        updated_case = await case_repository.add_party(case_id, party_data)

        if not updated_case:
            raise HTTPException(status_code=500, detail="Error al agregar parte")

        logger.info("party_added", case_id=str(case_id), role=request.role)

        return CaseResponse(**updated_case)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("add_party_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al agregar parte")


@router.get("/{case_id}/documents", response_model=dict)
async def get_case_documents(
    case_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Obtiene documentos generados de un caso

    Args:
        case_id: UUID del caso
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Lista de documentos del caso

    Raises:
        404: Caso no encontrado
    """
    logger.info("get_case_documents_request", case_id=str(case_id))

    try:
        # Verificar que el caso existe y pertenece al tenant
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        # Obtener documentos
        documents = await document_repository.list_by_case(case_id)

        return {
            "case_id": str(case_id),
            "case_number": case['case_number'],
            "documents": documents,
            "total": len(documents)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_case_documents_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener documentos")
