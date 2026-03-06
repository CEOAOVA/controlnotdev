"""
ControlNot v2 - WhatsApp Admin AI Assistant (AuriNot AI)
Agentic Claude loop that queries the DB in real-time via tool-calling.
"""
import json
from datetime import date, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

import structlog
from anthropic import AsyncAnthropic, APIConnectionError, RateLimitError

from app.core.config import settings
from app.services.whatsapp_service import whatsapp_service

logger = structlog.get_logger()

MAX_TOOL_ROUNDS = 5
MAX_HISTORY_TURNS = 10  # 10 user+assistant pairs = 20 messages
MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """\
Eres *AuriNot AI*, el asistente inteligente de la notaría. Respondes en español, \
eres conciso y profesional. Usas formato WhatsApp: *negritas*, _cursivas_, ~tachado~.

Reglas:
- Siempre usa las herramientas disponibles para obtener datos reales. Nunca inventes datos.
- Si no encuentras información, dilo claramente.
- Formatea montos con separador de miles y 2 decimales ($1,234.56).
- Fechas en formato dd/mm/yyyy.
- Listas con viñetas (- o •).
- Respuestas cortas y directas, máximo 1000 caracteres por mensaje.
- Si el usuario pide algo que no puedes hacer, sugiérele usar el menú normal con 'menu'.
- Si el usuario pide un documento o que le envíes un archivo, usa send_document_to_me.
"""

ADMIN_AI_TOOLS = [
    {
        "name": "get_case_statistics",
        "description": "Obtiene estadísticas generales de expedientes: total, por estado, activos vs cerrados.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_case_by_number",
        "description": "Busca un expediente por su número (ej: '2024-001'). Devuelve detalles del caso.",
        "input_schema": {
            "type": "object",
            "properties": {
                "case_number": {"type": "string", "description": "Número del expediente"},
            },
            "required": ["case_number"],
        },
    },
    {
        "name": "list_cases_by_status",
        "description": "Lista expedientes filtrados por estado. Estados válidos: borrador, en_revision, checklist_pendiente, presupuesto, calculo_impuestos, en_firma, postfirma, tramites_gobierno, inscripcion, facturacion, entrega, cerrado, cancelado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Estado del expediente"},
            },
            "required": ["status"],
        },
    },
    {
        "name": "search_clients",
        "description": "Busca clientes por nombre o apellido. Devuelve nombre, RFC, teléfono, email.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Texto de búsqueda (nombre o apellido)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_overdue_tramites",
        "description": "Lista todos los trámites gubernamentales vencidos (fecha límite ya pasó).",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_upcoming_tramites",
        "description": "Lista trámites gubernamentales próximos a vencer dentro de N días.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Número de días hacia adelante (default: 7)", "default": 7},
            },
            "required": [],
        },
    },
    {
        "name": "get_case_payments",
        "description": "Obtiene resumen de pagos de un expediente: totales por tipo y gran total.",
        "input_schema": {
            "type": "object",
            "properties": {
                "case_id": {"type": "string", "description": "UUID del expediente"},
            },
            "required": ["case_id"],
        },
    },
    {
        "name": "get_calendar_events",
        "description": "Lista eventos del calendario en un rango de fechas. Formato de fechas: YYYY-MM-DD.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Fecha inicio (YYYY-MM-DD). Default: hoy."},
                "end_date": {"type": "string", "description": "Fecha fin (YYYY-MM-DD). Default: +7 días."},
            },
            "required": [],
        },
    },
    {
        "name": "get_uif_summary",
        "description": "Obtiene resumen de operaciones UIF: total, vulnerables, por nivel de riesgo y estado.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_case_documents",
        "description": "Lista documentos generados de un expediente con URLs de descarga temporales.",
        "input_schema": {
            "type": "object",
            "properties": {
                "case_id": {"type": "string", "description": "UUID del expediente"},
            },
            "required": ["case_id"],
        },
    },
    {
        "name": "get_case_full_detail",
        "description": "Obtiene detalle completo de un expediente: datos, partes, checklist, trámites y pagos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "case_id": {"type": "string", "description": "UUID del expediente"},
            },
            "required": ["case_id"],
        },
    },
    {
        "name": "send_document_to_me",
        "description": "Envía un documento generado (.docx) al staff vía WhatsApp. Si no se especifica document_id, envía el más reciente del caso.",
        "input_schema": {
            "type": "object",
            "properties": {
                "case_id": {"type": "string", "description": "UUID del expediente"},
                "document_id": {"type": "string", "description": "UUID específico del documento (opcional)"},
            },
            "required": ["case_id"],
        },
    },
]


class WAAdminAIService:
    """Agentic AI assistant for admin staff via WhatsApp."""

    def __init__(self):
        self._client: Optional[AsyncAnthropic] = None

    def _get_client(self) -> AsyncAnthropic:
        if self._client is None:
            self._client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        return self._client

    async def handle_message(
        self,
        tenant_id: UUID,
        phone: str,
        staff: Dict[str, Any],
        text: str,
        session: Dict[str, Any],
    ) -> None:
        """Main entry: run agentic loop and send response via WhatsApp."""
        try:
            # Restore conversation history
            history: List[Dict] = session.get('ai_history', [])

            # Add user message
            history.append({"role": "user", "content": text})

            # Agentic loop
            client = self._get_client()
            messages = list(history)

            for _round in range(MAX_TOOL_ROUNDS):
                response = await client.messages.create(
                    model=MODEL,
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    tools=ADMIN_AI_TOOLS,
                    messages=messages,
                )

                # Check if Claude wants to use tools
                tool_uses = [b for b in response.content if b.type == "tool_use"]

                if not tool_uses:
                    # No tools — extract text and send
                    break

                # Execute tools and build results
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for tool_use in tool_uses:
                    result = await self._execute_tool(
                        tenant_id, tool_use.name, tool_use.input, phone=phone,
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result,
                    })

                messages.append({"role": "user", "content": tool_results})

            # Extract final text response
            final_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    final_text += block.text

            if not final_text:
                final_text = "No pude generar una respuesta. Escribe 'menu' para volver al menú."

            # Send via WhatsApp (split if too long for WA 4096 limit)
            for chunk in self._split_message(final_text):
                await whatsapp_service.send_text(phone, chunk)

            # Save clean history (only text turns, no tool intermediates)
            history.append({
                "role": "assistant",
                "content": final_text,
            })

            # Truncate to MAX_HISTORY_TURNS pairs
            if len(history) > MAX_HISTORY_TURNS * 2:
                history = history[-(MAX_HISTORY_TURNS * 2):]

            session['ai_history'] = history
            session['menu'] = 'ai'
            from app.repositories.wa_repository import wa_repository
            await wa_repository.update_staff_session(tenant_id, phone, session)

        except APIConnectionError:
            logger.error("ai_admin_connection_error", phone=phone)
            await whatsapp_service.send_text(
                phone, "No pude conectarme al servicio de IA. Intenta de nuevo en un momento."
            )
        except RateLimitError:
            logger.error("ai_admin_rate_limit", phone=phone)
            await whatsapp_service.send_text(
                phone, "Demasiadas solicitudes. Intenta de nuevo en 30 segundos."
            )
        except Exception as e:
            logger.error("ai_admin_error", phone=phone, error=str(e))
            await whatsapp_service.send_text(
                phone,
                "Ocurrió un error con el asistente IA. Escribe 'menu' para usar el menú normal.",
            )

    async def _execute_tool(
        self, tenant_id: UUID, tool_name: str, tool_input: Dict[str, Any],
        phone: str = "",
    ) -> str:
        """Dispatch tool call to the appropriate repository and return JSON string."""
        try:
            if tool_name == "get_case_statistics":
                from app.repositories import CaseRepository
                data = await CaseRepository().get_case_statistics(tenant_id)
                return json.dumps(data, default=str, ensure_ascii=False)

            elif tool_name == "get_case_by_number":
                from app.repositories import CaseRepository
                case = await CaseRepository().get_by_case_number(
                    tenant_id, tool_input["case_number"]
                )
                if not case:
                    return json.dumps({"error": "Expediente no encontrado"})
                return json.dumps(case, default=str, ensure_ascii=False)

            elif tool_name == "list_cases_by_status":
                from app.repositories import CaseRepository
                cases = await CaseRepository().list_by_status(
                    tenant_id, tool_input["status"], limit=20
                )
                return json.dumps(
                    {"count": len(cases), "cases": cases},
                    default=str, ensure_ascii=False,
                )

            elif tool_name == "search_clients":
                from app.repositories import ClientRepository
                clients = await ClientRepository().search_by_name(
                    tenant_id, tool_input["query"]
                )
                return json.dumps(
                    {"count": len(clients), "clients": clients},
                    default=str, ensure_ascii=False,
                )

            elif tool_name == "get_overdue_tramites":
                from app.repositories import CaseTramiteRepository
                tramites = await CaseTramiteRepository().list_overdue(tenant_id)
                return json.dumps(
                    {"count": len(tramites), "tramites": tramites},
                    default=str, ensure_ascii=False,
                )

            elif tool_name == "get_upcoming_tramites":
                from app.repositories import CaseTramiteRepository
                days = tool_input.get("days", 7)
                tramites = await CaseTramiteRepository().list_upcoming(tenant_id, days=days)
                return json.dumps(
                    {"count": len(tramites), "tramites": tramites},
                    default=str, ensure_ascii=False,
                )

            elif tool_name == "get_case_payments":
                from app.repositories.case_payment_repository import case_payment_repository
                case_id = UUID(tool_input["case_id"])
                totals = await case_payment_repository.get_totals_by_case(case_id)
                return json.dumps(totals, default=str, ensure_ascii=False)

            elif tool_name == "get_calendar_events":
                from app.repositories.calendar_repository import CalendarRepository
                today = date.today()
                start = tool_input.get("start_date", today.isoformat())
                end = tool_input.get("end_date", (today + timedelta(days=7)).isoformat())
                events = await CalendarRepository().list_by_range(tenant_id, start, end)
                return json.dumps(
                    {"count": len(events), "events": events},
                    default=str, ensure_ascii=False,
                )

            elif tool_name == "get_uif_summary":
                from app.repositories.uif_repository import UIFRepository
                summary = await UIFRepository().get_summary(tenant_id)
                return json.dumps(summary, default=str, ensure_ascii=False)

            elif tool_name == "get_case_documents":
                from app.repositories import DocumentRepository
                case_id = UUID(tool_input["case_id"])
                doc_repo = DocumentRepository()
                docs = await doc_repo.list_by_case(case_id)
                # Add signed URLs for documents with storage_path
                for doc in docs:
                    if doc.get('storage_path'):
                        try:
                            url = await doc_repo.get_signed_url(doc['storage_path'])
                            doc['download_url'] = url
                        except Exception:
                            doc['download_url'] = None
                return json.dumps(
                    {"count": len(docs), "documents": docs},
                    default=str, ensure_ascii=False,
                )

            elif tool_name == "get_case_full_detail":
                from app.repositories import (
                    CaseRepository, CasePartyRepository,
                    CaseChecklistRepository, CaseTramiteRepository,
                )
                from app.repositories.case_payment_repository import case_payment_repository

                case_id = UUID(tool_input["case_id"])
                case_repo = CaseRepository()

                case = await case_repo.get_case_with_client(case_id)
                if not case:
                    return json.dumps({"error": "Expediente no encontrado"})

                parties = await CasePartyRepository().list_by_case(case_id, limit=20)
                checklist = await CaseChecklistRepository().list_by_case(case_id, limit=50)
                tramites = await CaseTramiteRepository().list_by_case(case_id, limit=50)
                payments = await case_payment_repository.get_totals_by_case(case_id)

                return json.dumps({
                    "case": case,
                    "parties": parties,
                    "checklist_items": len(checklist),
                    "checklist_completed": len([c for c in checklist if c.get('status') == 'recibido']),
                    "tramites": tramites,
                    "payments": payments,
                }, default=str, ensure_ascii=False)

            elif tool_name == "send_document_to_me":
                from app.repositories import DocumentRepository
                doc_repo = DocumentRepository()
                case_id = UUID(tool_input["case_id"])

                document_id = tool_input.get("document_id")
                if document_id:
                    doc = await doc_repo.get_by_id(UUID(document_id))
                else:
                    docs = await doc_repo.list_by_case(case_id)
                    doc = docs[0] if docs else None

                if not doc:
                    return json.dumps({"error": "No se encontró documento para este expediente"})

                if not doc.get('storage_path'):
                    return json.dumps({"error": "El documento no tiene archivo almacenado"})

                if not phone:
                    return json.dumps({"error": "No se pudo determinar el teléfono de destino"})

                from app.services.wa_docgen_service import wa_docgen_service
                sent = await wa_docgen_service.send_document_via_whatsapp(
                    phone=phone,
                    storage_path=doc['storage_path'],
                    filename=doc.get('nombre_documento', 'documento.docx'),
                    caption=f"Documento: {doc.get('nombre_documento', '')}",
                )

                if sent:
                    return json.dumps({"success": True, "message": f"Documento '{doc.get('nombre_documento', '')}' enviado por WhatsApp"})
                else:
                    return json.dumps({"error": "No se pudo enviar el documento por WhatsApp"})

            else:
                return json.dumps({"error": f"Herramienta desconocida: {tool_name}"})

        except Exception as e:
            logger.error("ai_tool_execution_error", tool=tool_name, error=str(e))
            return json.dumps({"error": f"Error ejecutando {tool_name}: {str(e)}"})

    @staticmethod
    def _split_message(text: str, max_len: int = 4000) -> List[str]:
        """Split text into chunks that fit WhatsApp's message limit."""
        if len(text) <= max_len:
            return [text]

        chunks = []
        while text:
            if len(text) <= max_len:
                chunks.append(text)
                break
            # Find last newline within limit
            cut = text.rfind('\n', 0, max_len)
            if cut == -1:
                cut = max_len
            chunks.append(text[:cut])
            text = text[cut:].lstrip('\n')
        return chunks


# Singleton
wa_admin_ai_service = WAAdminAIService()
