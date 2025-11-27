"""
ControlNot v2 - Clients Endpoints
Endpoints REST para gestión de clientes
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
import structlog

from app.repositories.client_repository import client_repository
from app.repositories.case_repository import case_repository
from app.schemas.client_schemas import (
    ClientCreateRequest,
    ClientUpdateRequest,
    ClientSearchRequest,
    ClientResponse,
    ClientListResponse,
    ClientWithCasesResponse
)
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(
    request: ClientCreateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Crea un nuevo cliente

    Args:
        request: Datos del cliente a crear
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Cliente creado

    Raises:
        400: Si el RFC ya existe
        500: Error del servidor
    """
    logger.info("create_client_request", tenant_id=tenant_id, rfc=request.rfc)

    try:
        client = await client_repository.create_client(
            tenant_id=UUID(tenant_id),
            tipo_persona=request.tipo_persona,
            nombre_completo=request.nombre_completo,
            rfc=request.rfc,
            curp=request.curp,
            email=request.email,
            telefono=request.telefono,
            direccion=request.direccion,
            ciudad=request.ciudad,
            estado=request.estado,
            codigo_postal=request.codigo_postal,
            metadata=request.metadata
        )

        if not client:
            raise HTTPException(status_code=500, detail="Error al crear cliente")

        logger.info("client_created", client_id=client['id'])

        return ClientResponse(**client)

    except ValueError as e:
        # RFC duplicado
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error("create_client_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al crear cliente")


@router.get("", response_model=ClientListResponse)
async def list_clients(
    tenant_id: str = Depends(get_current_tenant_id),
    tipo_persona: Optional[str] = Query(None, description="Filtrar por tipo: fisica o moral"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página")
):
    """
    Lista clientes activos de la notaría

    Args:
        tenant_id: UUID de la notaría (inyectado)
        tipo_persona: Filtrar por tipo (opcional)
        page: Número de página
        page_size: Tamaño de página

    Returns:
        Lista paginada de clientes
    """
    logger.info("list_clients_request", tenant_id=tenant_id, page=page)

    try:
        offset = (page - 1) * page_size

        clients = await client_repository.list_active_clients(
            tenant_id=UUID(tenant_id),
            tipo_persona=tipo_persona,
            limit=page_size,
            offset=offset
        )

        total = await client_repository.count_clients(
            tenant_id=UUID(tenant_id),
            tipo_persona=tipo_persona
        )

        return ClientListResponse(
            clients=[ClientResponse(**client) for client in clients],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error("list_clients_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al listar clientes")


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Obtiene un cliente por ID

    Args:
        client_id: UUID del cliente
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Cliente encontrado

    Raises:
        404: Cliente no encontrado
    """
    logger.info("get_client_request", client_id=str(client_id))

    try:
        client = await client_repository.get_by_id(client_id)

        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Verificar que pertenece al tenant
        if client['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        return ClientResponse(**client)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_client_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener cliente")


@router.get("/{client_id}/cases", response_model=ClientWithCasesResponse)
async def get_client_with_cases(
    client_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Obtiene un cliente con sus casos

    Args:
        client_id: UUID del cliente
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Cliente con lista de casos

    Raises:
        404: Cliente no encontrado
    """
    logger.info("get_client_cases_request", client_id=str(client_id))

    try:
        # Obtener cliente
        client = await client_repository.get_by_id(client_id)

        if not client or client['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Obtener casos del cliente
        cases = await case_repository.list_by_client(client_id, limit=10)

        return ClientWithCasesResponse(
            **client,
            cases_count=len(cases),
            recent_cases=[
                {
                    "case_number": case['case_number'],
                    "document_type": case['document_type'],
                    "status": case['status']
                }
                for case in cases[:5]  # Solo los 5 más recientes
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_client_cases_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener casos del cliente")


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    request: ClientUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Actualiza datos de un cliente

    Args:
        client_id: UUID del cliente
        request: Campos a actualizar
        tenant_id: UUID de la notaría (inyectado)

    Returns:
        Cliente actualizado

    Raises:
        404: Cliente no encontrado
    """
    logger.info("update_client_request", client_id=str(client_id))

    try:
        # Verificar que existe y pertenece al tenant
        client = await client_repository.get_by_id(client_id)

        if not client or client['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Preparar campos a actualizar (solo los que no son None)
        updates = request.model_dump(exclude_unset=True)

        if not updates:
            # No hay nada que actualizar
            return ClientResponse(**client)

        # Actualizar
        updated_client = await client_repository.update_client(client_id, updates)

        if not updated_client:
            raise HTTPException(status_code=500, detail="Error al actualizar cliente")

        logger.info("client_updated", client_id=str(client_id))

        return ClientResponse(**updated_client)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_client_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar cliente")


@router.delete("/{client_id}", status_code=204)
async def deactivate_client(
    client_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Desactiva un cliente (soft delete)

    Args:
        client_id: UUID del cliente
        tenant_id: UUID de la notaría (inyectado)

    Raises:
        404: Cliente no encontrado
    """
    logger.info("deactivate_client_request", client_id=str(client_id))

    try:
        # Verificar que existe y pertenece al tenant
        client = await client_repository.get_by_id(client_id)

        if not client or client['tenant_id'] != tenant_id:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Desactivar
        await client_repository.deactivate_client(client_id)

        logger.info("client_deactivated", client_id=str(client_id))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("deactivate_client_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al desactivar cliente")


@router.get("/search/", response_model=ClientListResponse)
async def search_clients(
    q: str = Query(..., min_length=2, description="Texto a buscar en nombre o RFC"),
    tenant_id: str = Depends(get_current_tenant_id),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados")
):
    """
    Busca clientes por nombre o RFC

    Args:
        q: Texto a buscar
        tenant_id: UUID de la notaría (inyectado)
        limit: Máximo de resultados

    Returns:
        Lista de clientes que coinciden
    """
    logger.info("search_clients_request", query=q, tenant_id=tenant_id)

    try:
        # Buscar por nombre
        clients = await client_repository.search_by_name(
            tenant_id=UUID(tenant_id),
            nombre=q,
            limit=limit
        )

        return ClientListResponse(
            clients=[ClientResponse(**client) for client in clients],
            total=len(clients),
            page=1,
            page_size=limit
        )

    except Exception as e:
        logger.error("search_clients_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error en búsqueda de clientes")
