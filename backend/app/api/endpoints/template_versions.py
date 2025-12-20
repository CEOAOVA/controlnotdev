"""
ControlNot v2 - Template Versions Endpoints
Endpoints para gestión de versiones de templates

Rutas:
- GET    /api/templates/{id}/versions          - Listar versiones
- GET    /api/templates/{id}/versions/active   - Obtener versión activa
- GET    /api/templates/{id}/versions/{v_id}   - Detalle de versión
- POST   /api/templates/{id}/versions/{v_id}/activate - Activar versión
- POST   /api/templates/{id}/versions/compare  - Comparar versiones
"""
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
import structlog

from app.schemas import (
    TemplateVersionResponse,
    TemplateVersionListResponse,
    VersionCompareRequest,
    VersionCompareResponse,
    ActivateVersionResponse,
    SuccessResponse,
    ErrorResponse
)
from app.services import TemplateVersionService
from app.core.dependencies import get_user_tenant_id
from app.database import supabase_admin

logger = structlog.get_logger()
router = APIRouter(prefix="/templates", tags=["Template Versions"])


def get_version_service() -> TemplateVersionService:
    """Dependency para obtener el servicio de versiones"""
    return TemplateVersionService()


@router.get("/{template_id}/versions", response_model=TemplateVersionListResponse)
async def list_versions(
    template_id: str,
    tenant_id: str = Depends(get_user_tenant_id),
    version_service: TemplateVersionService = Depends(get_version_service)
):
    """
    Lista todas las versiones de un template

    Retorna versiones ordenadas por version_number DESC (más reciente primero)
    """
    start_time = time.time()
    logger.info(
        "versions_list_endpoint",
        template_id=template_id,
        tenant_id=tenant_id
    )

    try:
        # Verificar que el template existe y pertenece al tenant
        template_result = supabase_admin.table('templates').select(
            'id, nombre, tenant_id'
        ).eq('id', template_id).single().execute()

        if not template_result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Template {template_id} no encontrado"
            )

        template = template_result.data
        if template.get('tenant_id') and str(template['tenant_id']) != tenant_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes acceso a este template"
            )

        # Obtener versiones
        versions = await version_service.get_versions(template_id)

        # Encontrar versión activa
        active_version = next(
            (v['version_number'] for v in versions if v.get('es_activa')),
            None
        )

        duration = (time.time() - start_time) * 1000
        logger.info(
            "versions_list_complete",
            template_id=template_id,
            versions_count=len(versions),
            active_version=active_version,
            duration_ms=round(duration, 2)
        )

        return TemplateVersionListResponse(
            template_id=template_id,
            template_name=template.get('nombre', ''),
            versions=[TemplateVersionResponse(**v) for v in versions],
            total_versions=len(versions),
            active_version=active_version
        )

    except HTTPException:
        raise
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            "versions_list_failed",
            template_id=template_id,
            error=str(e),
            duration_ms=round(duration, 2)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar versiones: {str(e)}"
        )


@router.get("/{template_id}/versions/active", response_model=TemplateVersionResponse)
async def get_active_version(
    template_id: str,
    tenant_id: str = Depends(get_user_tenant_id),
    version_service: TemplateVersionService = Depends(get_version_service)
):
    """
    Obtiene la versión activa de un template

    Retorna la versión marcada como es_activa=true
    """
    start_time = time.time()
    logger.debug(
        "version_active_endpoint",
        template_id=template_id,
        tenant_id=tenant_id
    )

    try:
        # Verificar acceso al template
        template_result = supabase_admin.table('templates').select(
            'id, tenant_id'
        ).eq('id', template_id).single().execute()

        if not template_result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Template {template_id} no encontrado"
            )

        template = template_result.data
        if template.get('tenant_id') and str(template['tenant_id']) != tenant_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes acceso a este template"
            )

        # Obtener versión activa
        active = await version_service.get_active_version(template_id)

        if not active:
            raise HTTPException(
                status_code=404,
                detail="No hay versión activa para este template"
            )

        duration = (time.time() - start_time) * 1000
        logger.info(
            "version_active_complete",
            template_id=template_id,
            version_number=active['version_number'],
            duration_ms=round(duration, 2)
        )

        return TemplateVersionResponse(**active)

    except HTTPException:
        raise
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            "version_active_failed",
            template_id=template_id,
            error=str(e),
            duration_ms=round(duration, 2)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener versión activa: {str(e)}"
        )


@router.get("/{template_id}/versions/{version_id}", response_model=TemplateVersionResponse)
async def get_version_detail(
    template_id: str,
    version_id: str,
    tenant_id: str = Depends(get_user_tenant_id),
    version_service: TemplateVersionService = Depends(get_version_service)
):
    """
    Obtiene el detalle de una versión específica
    """
    logger.debug(
        "version_detail_endpoint",
        template_id=template_id,
        version_id=version_id
    )

    try:
        # Verificar acceso al template
        template_result = supabase_admin.table('templates').select(
            'id, tenant_id'
        ).eq('id', template_id).single().execute()

        if not template_result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Template {template_id} no encontrado"
            )

        template = template_result.data
        if template.get('tenant_id') and str(template['tenant_id']) != tenant_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes acceso a este template"
            )

        # Obtener la versión específica
        version_result = supabase_admin.table('template_versions').select(
            '*'
        ).eq('id', version_id).eq('template_id', template_id).single().execute()

        if not version_result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Versión {version_id} no encontrada"
            )

        v = version_result.data
        return TemplateVersionResponse(
            id=str(v['id']),
            template_id=str(v['template_id']),
            version_number=v['version_number'],
            storage_path=v['storage_path'],
            placeholders=v.get('placeholders', []),
            placeholder_mapping=v.get('placeholder_mapping', {}),
            es_activa=v.get('es_activa', False),
            created_at=v.get('created_at'),
            created_by=v.get('created_by'),
            notas=v.get('notas')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "version_detail_failed",
            template_id=template_id,
            version_id=version_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener versión: {str(e)}"
        )


@router.post("/{template_id}/versions/{version_id}/activate", response_model=ActivateVersionResponse)
async def activate_version(
    template_id: str,
    version_id: str,
    tenant_id: str = Depends(get_user_tenant_id),
    version_service: TemplateVersionService = Depends(get_version_service)
):
    """
    Activa una versión específica (rollback)

    Desactiva automáticamente la versión anterior y activa la seleccionada.
    Útil para revertir a una versión anterior del template.
    """
    start_time = time.time()
    logger.info(
        "version_activate_endpoint",
        template_id=template_id,
        version_id=version_id,
        tenant_id=tenant_id
    )

    try:
        # Verificar acceso al template
        template_result = supabase_admin.table('templates').select(
            'id, tenant_id'
        ).eq('id', template_id).single().execute()

        if not template_result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Template {template_id} no encontrado"
            )

        template = template_result.data
        if template.get('tenant_id') and str(template['tenant_id']) != tenant_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes acceso a este template"
            )

        # Activar la versión
        activated = await version_service.set_active_version(
            template_id=template_id,
            version_id=version_id
        )

        duration = (time.time() - start_time) * 1000
        logger.info(
            "version_activate_complete",
            template_id=template_id,
            version_id=version_id,
            version_number=activated['version_number'],
            previous_version=activated.get('previous_active_version'),
            duration_ms=round(duration, 2)
        )

        return ActivateVersionResponse(
            success=True,
            message=f"Versión {activated['version_number']} activada exitosamente",
            activated_version=TemplateVersionResponse(**{
                k: v for k, v in activated.items()
                if k != 'previous_active_version'
            }),
            previous_active_version=activated.get('previous_active_version')
        )

    except HTTPException:
        raise
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            "version_activate_failed",
            template_id=template_id,
            version_id=version_id,
            error=str(e),
            duration_ms=round(duration, 2)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al activar versión: {str(e)}"
        )


@router.post("/{template_id}/versions/compare", response_model=VersionCompareResponse)
async def compare_versions(
    template_id: str,
    request: VersionCompareRequest,
    tenant_id: str = Depends(get_user_tenant_id),
    version_service: TemplateVersionService = Depends(get_version_service)
):
    """
    Compara placeholders entre dos versiones

    Retorna:
    - Placeholders agregados en versión 2
    - Placeholders eliminados en versión 2
    - Placeholders sin cambios
    """
    start_time = time.time()
    logger.info(
        "version_compare_endpoint",
        template_id=template_id,
        version_1=request.version_id_1,
        version_2=request.version_id_2
    )

    try:
        # Verificar acceso al template
        template_result = supabase_admin.table('templates').select(
            'id, tenant_id'
        ).eq('id', template_id).single().execute()

        if not template_result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Template {template_id} no encontrado"
            )

        template = template_result.data
        if template.get('tenant_id') and str(template['tenant_id']) != tenant_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes acceso a este template"
            )

        # Comparar versiones
        comparison = await version_service.compare_versions(
            version_id_1=request.version_id_1,
            version_id_2=request.version_id_2
        )

        duration = (time.time() - start_time) * 1000
        logger.info(
            "version_compare_complete",
            template_id=template_id,
            added=len(comparison['added_placeholders']),
            removed=len(comparison['removed_placeholders']),
            unchanged=len(comparison['unchanged_placeholders']),
            duration_ms=round(duration, 2)
        )

        return VersionCompareResponse(**comparison)

    except HTTPException:
        raise
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            "version_compare_failed",
            template_id=template_id,
            error=str(e),
            duration_ms=round(duration, 2)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al comparar versiones: {str(e)}"
        )
