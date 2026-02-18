"""
ControlNot v2 - Cases Endpoints
Endpoints REST para gestión de casos/expedientes con workflow CRM
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
import structlog

from app.repositories.case_repository import case_repository
from app.repositories.session_repository import session_repository
from app.repositories.document_repository import document_repository
from app.repositories.case_party_repository import case_party_repository
from app.repositories.case_checklist_repository import case_checklist_repository
from app.repositories.case_tramite_repository import case_tramite_repository
from app.services.case_workflow_service import case_workflow_service, STATUS_LABELS
from app.services.checklist_service import checklist_service
from app.services.tramite_service import tramite_service
from app.schemas.case_schemas import (
    CaseCreateRequest,
    CaseUpdateRequest,
    CaseUpdateStatusRequest,
    CaseAddPartyRequest,
    CaseTransitionRequest,
    CaseSuspendRequest,
    CaseResponse,
    CaseWithClientResponse,
    CaseWithSessionsResponse,
    CaseDetailResponse,
    CaseListResponse,
    CaseStatisticsResponse,
    CaseDashboardResponse,
    SemaforoSummary,
    TransitionResponse,
)
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("", response_model=CaseWithClientResponse, status_code=201)
async def create_case(
    request: CaseCreateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Crea un nuevo caso/expediente con campos CRM"""
    logger.info(
        "create_case_request",
        tenant_id=tenant_id,
        case_number=request.case_number,
        document_type=request.document_type
    )

    try:
        case_data = {
            'tenant_id': tenant_id,
            'client_id': str(request.client_id),
            'case_number': request.case_number.upper(),
            'document_type': request.document_type,
            'status': 'borrador',
            'parties': request.parties or [],
            'metadata': request.metadata or {},
        }

        if request.description:
            case_data['description'] = request.description
        if request.priority:
            case_data['priority'] = request.priority
        if request.assigned_to:
            case_data['assigned_to'] = str(request.assigned_to)
        if request.valor_operacion is not None:
            case_data['valor_operacion'] = request.valor_operacion
        if request.fecha_firma:
            case_data['fecha_firma'] = request.fecha_firma.isoformat()
        if request.notas:
            case_data['notas'] = request.notas
        if request.tags:
            case_data['tags'] = request.tags

        case = await case_repository.create(case_data)

        if not case:
            raise HTTPException(status_code=500, detail="Error al crear caso")

        case_with_client = await case_repository.get_case_with_client(UUID(case['id']))

        logger.info("case_created", case_id=case['id'], case_number=request.case_number)

        return CaseWithClientResponse(**(case_with_client or case))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_case_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al crear caso")


@router.get("", response_model=CaseListResponse)
async def list_cases(
    tenant_id: str = Depends(get_current_tenant_id),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    document_type: Optional[str] = Query(None, description="Filtrar por tipo"),
    priority: Optional[str] = Query(None, description="Filtrar por prioridad"),
    assigned_to: Optional[UUID] = Query(None, description="Filtrar por asignado"),
    search: Optional[str] = Query(None, description="Buscar en case_number o description"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página")
):
    """Lista casos con filtros avanzados"""
    logger.info("list_cases_request", tenant_id=tenant_id, status=status, page=page)

    try:
        offset = (page - 1) * page_size
        filters = {}

        if status:
            filters['status'] = status
        if document_type:
            filters['document_type'] = document_type
        if priority:
            filters['priority'] = priority
        if assigned_to:
            filters['assigned_to'] = str(assigned_to)

        cases = await case_repository.list_by_tenant(
            tenant_id=UUID(tenant_id),
            filters=filters,
            limit=page_size,
            offset=offset
        )

        total = await case_repository.count_by_tenant(UUID(tenant_id), filters)

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
    """Obtiene estadísticas de casos de la notaría"""
    logger.info("get_case_statistics_request", tenant_id=tenant_id)

    try:
        stats = await case_repository.get_case_statistics(UUID(tenant_id))
        return CaseStatisticsResponse(**stats)
    except Exception as e:
        logger.error("get_case_statistics_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas")


@router.get("/dashboard", response_model=CaseDashboardResponse)
async def get_case_dashboard(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Resumen dashboard: counts por status, prioridad, semáforo global, trámites vencidos"""
    logger.info("get_case_dashboard_request", tenant_id=tenant_id)

    try:
        tid = UUID(tenant_id)

        # Counts por status
        total = await case_repository.count_by_tenant(tid)
        statuses = [
            'borrador', 'en_revision', 'checklist_pendiente', 'presupuesto',
            'calculo_impuestos', 'en_firma', 'postfirma', 'tramites_gobierno',
            'inscripcion', 'facturacion', 'entrega', 'cerrado', 'cancelado', 'suspendido'
        ]
        by_status = {}
        for s in statuses:
            count = await case_repository.count_by_tenant(tid, {'status': s})
            if count > 0:
                by_status[s] = count

        # Counts por priority
        priorities = ['baja', 'normal', 'alta', 'urgente']
        by_priority = {}
        for p in priorities:
            count = await case_repository.count_by_tenant(tid, {'priority': p})
            if count > 0:
                by_priority[p] = count

        # Semáforo global de trámites
        overdue = await tramite_service.get_overdue(tid)
        upcoming = await tramite_service.get_upcoming(tid)

        # Count all active tramites for semaforo
        from app.repositories.case_tramite_repository import case_tramite_repository as tr
        all_tramites = await tr.list_by_tenant(tid, filters={}, limit=500)
        semaforo_data = tramite_service.get_semaforo(all_tramites)

        return CaseDashboardResponse(
            total_cases=total,
            by_status=by_status,
            by_priority=by_priority,
            semaforo_global=SemaforoSummary(**semaforo_data),
            overdue_tramites=len(overdue),
            upcoming_tramites=len(upcoming),
        )

    except Exception as e:
        logger.error("get_case_dashboard_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener dashboard")


@router.get("/{case_id}", response_model=CaseDetailResponse)
async def get_case(
    case_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Obtiene un caso con partes, checklist summary, trámites y transiciones disponibles"""
    logger.info("get_case_request", case_id=str(case_id))

    try:
        case = await case_repository.get_case_with_client(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        # Partes normalizadas
        parties = await case_party_repository.list_by_case(case_id)

        # Checklist summary
        checklist_sum = await checklist_service.get_summary(case_id)

        # Trámites summary con semáforo
        tramites = await case_tramite_repository.list_by_case(case_id)
        tramites_semaforo = tramite_service.get_semaforo(tramites)

        # Transiciones disponibles
        transitions = case_workflow_service.get_available_transitions(case['status'])

        return CaseDetailResponse(
            **case,
            case_parties=parties,
            checklist_summary=checklist_sum,
            tramites_summary=tramites_semaforo,
            available_transitions=transitions,
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
    """Actualiza datos de un caso"""
    logger.info("update_case_request", case_id=str(case_id))

    try:
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        updates = request.model_dump(exclude_unset=True)

        if not updates:
            return CaseResponse(**case)

        # Convert UUIDs to strings for Supabase
        if 'assigned_to' in updates and updates['assigned_to']:
            updates['assigned_to'] = str(updates['assigned_to'])
        if 'fecha_firma' in updates and updates['fecha_firma']:
            updates['fecha_firma'] = updates['fecha_firma'].isoformat()

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
    """Actualiza el estado de un caso (legacy, sin validación de state machine)"""
    logger.info("update_case_status_request", case_id=str(case_id), new_status=request.status)

    try:
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

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


@router.post("/{case_id}/transition", response_model=CaseResponse)
async def transition_case(
    case_id: UUID,
    request: CaseTransitionRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Transición validada por state machine"""
    logger.info("transition_case_request", case_id=str(case_id), new_status=request.status)

    try:
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        updated_case = await case_workflow_service.transition(
            case_id=case_id,
            tenant_id=UUID(tenant_id),
            new_status=request.status,
            notes=request.notes,
        )

        return CaseResponse(**updated_case)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("transition_case_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al transicionar caso")


@router.post("/{case_id}/suspend", response_model=CaseResponse)
async def suspend_case(
    case_id: UUID,
    request: CaseSuspendRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Suspende un caso"""
    logger.info("suspend_case_request", case_id=str(case_id))

    try:
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        updated_case = await case_workflow_service.suspend(
            case_id=case_id,
            tenant_id=UUID(tenant_id),
            reason=request.reason,
        )

        return CaseResponse(**updated_case)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("suspend_case_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al suspender caso")


@router.post("/{case_id}/resume", response_model=CaseResponse)
async def resume_case(
    case_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Reanuda un caso suspendido"""
    logger.info("resume_case_request", case_id=str(case_id))

    try:
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        updated_case = await case_workflow_service.resume(
            case_id=case_id,
            tenant_id=UUID(tenant_id),
        )

        return CaseResponse(**updated_case)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("resume_case_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al reanudar caso")


@router.get("/{case_id}/transitions", response_model=TransitionResponse)
async def get_available_transitions(
    case_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Obtiene las transiciones disponibles para un caso"""
    try:
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        current = case['status']
        transitions = case_workflow_service.get_available_transitions(current)

        return TransitionResponse(
            current_status=current,
            current_label=STATUS_LABELS.get(current, current),
            transitions=transitions,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_transitions_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener transiciones")


@router.post("/{case_id}/parties", response_model=CaseResponse)
async def add_party_to_case(
    case_id: UUID,
    request: CaseAddPartyRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Agrega una parte involucrada al caso (legacy JSONB)"""
    logger.info("add_party_request", case_id=str(case_id), role=request.role)

    try:
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        party_data = {
            "role": request.role,
            "metadata": request.metadata
        }

        if request.client_id:
            party_data["client_id"] = str(request.client_id)
        if request.nombre:
            party_data["nombre"] = request.nombre

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
    """Obtiene documentos generados de un caso"""
    logger.info("get_case_documents_request", case_id=str(case_id))

    try:
        case = await case_repository.get_by_id(case_id)

        if not case or case['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

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
