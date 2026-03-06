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


@router.get("/whatsapp-summary")
async def whatsapp_summary(
    date_from: Optional[str] = Query(None, description="Filter from date ISO 8601"),
    date_to: Optional[str] = Query(None, description="Filter to date ISO 8601"),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Resumen de actividad WhatsApp: mensajes, conversaciones, extracciones, comandos"""
    try:
        client = _get_client()

        # --- Messages ---
        msg_query = client.table('wa_messages')\
            .select('sender_type, message_type, status')\
            .eq('tenant_id', tenant_id)
        if date_from:
            msg_query = msg_query.gte('created_at', date_from)
        if date_to:
            msg_query = msg_query.lte('created_at', date_to)
        msg_rows = (msg_query.execute()).data or []

        by_sender_type: dict = {}
        by_message_type: dict = {}
        by_msg_status: dict = {}
        failed_count = 0
        for row in msg_rows:
            st = row.get('sender_type', 'unknown')
            by_sender_type[st] = by_sender_type.get(st, 0) + 1
            mt = row.get('message_type', 'text')
            by_message_type[mt] = by_message_type.get(mt, 0) + 1
            ms = row.get('status', 'unknown')
            by_msg_status[ms] = by_msg_status.get(ms, 0) + 1
            if ms == 'failed':
                failed_count += 1

        # --- Conversations ---
        conv_query = client.table('wa_conversations')\
            .select('status, unread_count')\
            .eq('tenant_id', tenant_id)
        if date_from:
            conv_query = conv_query.gte('created_at', date_from)
        if date_to:
            conv_query = conv_query.lte('created_at', date_to)
        conv_rows = (conv_query.execute()).data or []

        by_conv_status: dict = {}
        total_unread = 0
        for row in conv_rows:
            cs = row.get('status', 'unknown')
            by_conv_status[cs] = by_conv_status.get(cs, 0) + 1
            total_unread += int(row.get('unread_count', 0) or 0)

        # --- Document Extractions ---
        ext_query = client.table('wa_document_extractions')\
            .select('document_type, status, confidence')\
            .eq('tenant_id', tenant_id)
        if date_from:
            ext_query = ext_query.gte('created_at', date_from)
        if date_to:
            ext_query = ext_query.lte('created_at', date_to)
        ext_rows = (ext_query.execute()).data or []

        by_doc_type: dict = {}
        by_ext_status: dict = {}
        confidence_sum = 0.0
        confidence_count = 0
        for row in ext_rows:
            dt = row.get('document_type', 'unknown')
            by_doc_type[dt] = by_doc_type.get(dt, 0) + 1
            es = row.get('status', 'unknown')
            by_ext_status[es] = by_ext_status.get(es, 0) + 1
            conf = row.get('confidence')
            if conf is not None:
                confidence_sum += float(conf)
                confidence_count += 1

        avg_confidence = round(confidence_sum / confidence_count, 2) if confidence_count > 0 else 0.0

        # --- Command Log ---
        cmd_query = client.table('wa_command_log')\
            .select('command, staff_phone')\
            .eq('tenant_id', tenant_id)
        if date_from:
            cmd_query = cmd_query.gte('created_at', date_from)
        if date_to:
            cmd_query = cmd_query.lte('created_at', date_to)
        cmd_rows = (cmd_query.execute()).data or []

        cmd_counts: dict = {}
        by_staff: dict = {}
        for row in cmd_rows:
            cmd = row.get('command', 'unknown')
            cmd_counts[cmd] = cmd_counts.get(cmd, 0) + 1
            staff = row.get('staff_phone', 'unknown')
            by_staff[staff] = by_staff.get(staff, 0) + 1

        top_commands = dict(sorted(cmd_counts.items(), key=lambda x: x[1], reverse=True)[:10])

        return {
            'messages': {
                'total': len(msg_rows),
                'by_sender_type': by_sender_type,
                'by_message_type': by_message_type,
                'by_status': by_msg_status,
                'failed_count': failed_count,
            },
            'conversations': {
                'total': len(conv_rows),
                'by_status': by_conv_status,
                'total_unread': total_unread,
            },
            'extractions': {
                'total': len(ext_rows),
                'by_document_type': by_doc_type,
                'by_status': by_ext_status,
                'avg_confidence': avg_confidence,
            },
            'commands': {
                'total': len(cmd_rows),
                'top_commands': top_commands,
                'by_staff': by_staff,
            },
        }
    except Exception as e:
        logger.error("whatsapp_summary_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al generar reporte de WhatsApp")


@router.get("/templates-summary")
async def templates_summary(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Resumen de plantillas Word y documentos generados"""
    try:
        client = _get_client()

        # --- Templates ---
        tpl_result = client.table('templates')\
            .select('id, name, document_type, placeholders, created_at')\
            .eq('tenant_id', tenant_id)\
            .execute()
        tpl_rows = tpl_result.data or []

        # --- Documents (generated) ---
        doc_result = client.table('documentos')\
            .select('template_id, document_type, status, confidence_score, created_at')\
            .eq('tenant_id', tenant_id)\
            .execute()
        doc_rows = doc_result.data or []

        # Count docs per template
        docs_by_template: dict = {}
        last_used_by_template: dict = {}
        docs_by_status: dict = {}
        doc_confidence_sum = 0.0
        doc_confidence_count = 0

        for doc in doc_rows:
            tid = doc.get('template_id')
            if tid:
                docs_by_template[tid] = docs_by_template.get(tid, 0) + 1
                doc_date = doc.get('created_at', '')
                if doc_date > last_used_by_template.get(tid, ''):
                    last_used_by_template[tid] = doc_date

            ds = doc.get('status', 'unknown')
            docs_by_status[ds] = docs_by_status.get(ds, 0) + 1

            conf = doc.get('confidence_score')
            if conf is not None:
                doc_confidence_sum += float(conf)
                doc_confidence_count += 1

        avg_doc_confidence = round(doc_confidence_sum / doc_confidence_count, 2) if doc_confidence_count > 0 else 0.0

        # Build template list
        by_doc_type: dict = {}
        template_list = []
        for tpl in tpl_rows:
            tpl_id = tpl.get('id', '')
            placeholders = tpl.get('placeholders')
            total_placeholders = len(placeholders) if isinstance(placeholders, list) else 0
            doc_type = tpl.get('document_type', 'unknown')
            by_doc_type[doc_type] = by_doc_type.get(doc_type, 0) + 1

            template_list.append({
                'id': tpl_id,
                'nombre': tpl.get('name', ''),
                'tipo_documento': doc_type,
                'total_placeholders': total_placeholders,
                'documents_generated': docs_by_template.get(tpl_id, 0),
                'last_used_at': last_used_by_template.get(tpl_id),
                'created_at': tpl.get('created_at'),
            })

        return {
            'templates': {
                'total': len(tpl_rows),
                'by_document_type': by_doc_type,
                'list': template_list,
            },
            'documents': {
                'total_generated': len(doc_rows),
                'by_status': docs_by_status,
                'avg_confidence': avg_doc_confidence,
            },
        }
    except Exception as e:
        logger.error("templates_summary_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al generar reporte de plantillas")


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
