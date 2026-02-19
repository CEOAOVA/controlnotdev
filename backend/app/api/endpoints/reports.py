"""
ControlNot v2 - Reports Endpoints
Endpoints para reportes y resúmenes analíticos
"""
from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
import structlog

from app.database import get_supabase_admin_client, get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/reports", tags=["Reports"])


def _get_client():
    return get_supabase_admin_client()


@router.get("/cases-summary")
async def cases_summary(
    date_from: Optional[str] = Query(None, description="Filter from date ISO 8601"),
    date_to: Optional[str] = Query(None, description="Filter to date ISO 8601"),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Resumen de casos por status, tipo, y prioridad"""
    try:
        client = _get_client()
        query = client.table('cases')\
            .select('status, document_type, priority')\
            .eq('tenant_id', tenant_id)

        if date_from:
            query = query.gte('created_at', date_from)
        if date_to:
            query = query.lte('created_at', date_to)

        result = query.execute()
        rows = result.data or []

        by_status: dict = {}
        by_type: dict = {}
        by_priority: dict = {}

        for row in rows:
            s = row.get('status', 'unknown')
            by_status[s] = by_status.get(s, 0) + 1

            t = row.get('document_type', 'unknown')
            by_type[t] = by_type.get(t, 0) + 1

            p = row.get('priority', 'normal')
            by_priority[p] = by_priority.get(p, 0) + 1

        return {
            'total': len(rows),
            'by_status': by_status,
            'by_type': by_type,
            'by_priority': by_priority,
        }
    except Exception as e:
        logger.error("cases_summary_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al generar reporte de casos")


@router.get("/tramites-summary")
async def tramites_summary(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Semaforo global de tramites: vencidos, por vencer, activos"""
    try:
        client = _get_client()
        result = client.table('case_tramites')\
            .select('status, semaforo, fecha_limite')\
            .eq('tenant_id', tenant_id)\
            .execute()

        rows = result.data or []
        now = datetime.utcnow().isoformat()

        by_semaforo: dict = {}
        by_status: dict = {}
        vencidos = 0
        total = len(rows)

        for row in rows:
            sem = row.get('semaforo', 'gris')
            by_semaforo[sem] = by_semaforo.get(sem, 0) + 1

            st = row.get('status', 'pendiente')
            by_status[st] = by_status.get(st, 0) + 1

            if row.get('fecha_limite') and row['fecha_limite'] < now and st not in ('completado', 'cancelado'):
                vencidos += 1

        return {
            'total': total,
            'vencidos': vencidos,
            'by_semaforo': by_semaforo,
            'by_status': by_status,
        }
    except Exception as e:
        logger.error("tramites_summary_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al generar reporte de tramites")


@router.get("/financial-summary")
async def financial_summary(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Resumen financiero: pagos por tipo, totales, por caso"""
    try:
        client = _get_client()
        query = client.table('case_payments')\
            .select('tipo, monto, case_id, metodo_pago, fecha_pago')\
            .eq('tenant_id', tenant_id)

        if date_from:
            query = query.gte('fecha_pago', date_from)
        if date_to:
            query = query.lte('fecha_pago', date_to)

        result = query.execute()
        rows = result.data or []

        by_tipo: dict = {}
        by_metodo: dict = {}
        by_case: dict = {}
        grand_total = 0.0

        for row in rows:
            monto = float(row.get('monto', 0))
            grand_total += monto

            tipo = row.get('tipo', 'otro')
            by_tipo[tipo] = by_tipo.get(tipo, 0.0) + monto

            metodo = row.get('metodo_pago', 'otro')
            by_metodo[metodo] = by_metodo.get(metodo, 0.0) + monto

            cid = row.get('case_id', 'sin_caso')
            by_case[cid] = by_case.get(cid, 0.0) + monto

        return {
            'total': grand_total,
            'count': len(rows),
            'by_tipo': by_tipo,
            'by_metodo': by_metodo,
            'top_cases': dict(sorted(by_case.items(), key=lambda x: x[1], reverse=True)[:10]),
        }
    except Exception as e:
        logger.error("financial_summary_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al generar reporte financiero")


@router.get("/productivity")
async def productivity(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Productividad: casos cerrados, tiempos promedio"""
    try:
        client = _get_client()
        query = client.table('cases')\
            .select('status, created_at, updated_at')\
            .eq('tenant_id', tenant_id)

        if date_from:
            query = query.gte('created_at', date_from)
        if date_to:
            query = query.lte('created_at', date_to)

        result = query.execute()
        rows = result.data or []

        total = len(rows)
        cerrados = 0
        total_days = 0.0
        cerrados_with_time = 0

        for row in rows:
            if row.get('status') == 'cerrado':
                cerrados += 1
                if row.get('created_at') and row.get('updated_at'):
                    try:
                        created = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                        updated = datetime.fromisoformat(row['updated_at'].replace('Z', '+00:00'))
                        delta = (updated - created).days
                        total_days += delta
                        cerrados_with_time += 1
                    except (ValueError, TypeError):
                        pass

        avg_days = round(total_days / cerrados_with_time, 1) if cerrados_with_time > 0 else 0

        return {
            'total_cases': total,
            'cerrados': cerrados,
            'abiertos': total - cerrados,
            'promedio_dias_cierre': avg_days,
            'tasa_cierre': round(cerrados / total * 100, 1) if total > 0 else 0,
        }
    except Exception as e:
        logger.error("productivity_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al generar reporte de productividad")
