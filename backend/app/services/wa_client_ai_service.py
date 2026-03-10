"""
ControlNot v2 - WhatsApp Client AI Service
LLM-powered auto-responder for client messages using Claude Haiku.
"""
import json
from typing import Any, Dict, List, Optional
from uuid import UUID

import structlog
from anthropic import AsyncAnthropic

logger = structlog.get_logger()

MODEL = "claude-haiku-4-5-20251001"
MAX_RESPONSE_CHARS = 300
MAX_CONTEXT_MESSAGES = 5

SYSTEM_PROMPT = """\
Eres un asistente profesional de notaria. Respondes en espanol de manera cordial y concisa.
Formato WhatsApp: *negritas*, _cursivas_.

Reglas estrictas:
- Maximo 300 caracteres por respuesta.
- NUNCA compartas montos, costos, precios o datos financieros especificos.
- NUNCA compartas datos legales sensibles (RFC, CURP, datos de escritura).
- Si el cliente pregunta algo que no puedes responder, di que un asesor lo atendera pronto.
- Si el cliente tiene un expediente activo, puedes decirle en que fase esta (informacion general).
- Se amable pero profesional. No uses emojis excesivos.
- Si no entiendes la pregunta, pide que la reformule o indica que un humano lo atendera.
"""


class WAClientAIService:
    """LLM-powered auto-responder for client WhatsApp messages."""

    def __init__(self):
        self._client: Optional[AsyncAnthropic] = None

    def _get_client(self) -> AsyncAnthropic:
        if self._client is None:
            from app.core.config import settings
            self._client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        return self._client

    async def generate_reply(
        self,
        tenant_id: UUID,
        phone: str,
        message_text: str,
        recent_messages: Optional[List[Dict[str, Any]]] = None,
        client_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate an AI reply for a client message.

        Args:
            tenant_id: Tenant UUID
            phone: Client phone number
            message_text: The incoming message text
            recent_messages: Last N messages for context
            client_id: Optional linked client ID for case lookup

        Returns:
            Reply text or None on failure
        """
        try:
            # Build context
            system = SYSTEM_PROMPT
            case_context = await self._get_case_context(tenant_id, client_id)
            if case_context:
                system += f"\n\nContexto del expediente del cliente:\n{case_context}"

            # Build message history
            messages = self._build_messages(message_text, recent_messages)

            client = self._get_client()
            response = await client.messages.create(
                model=MODEL,
                max_tokens=150,
                system=system,
                messages=messages,
            )

            reply = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    reply += block.text

            if not reply:
                return None

            # Truncate to max chars
            if len(reply) > MAX_RESPONSE_CHARS:
                # Cut at last sentence boundary
                cut = reply[:MAX_RESPONSE_CHARS].rfind('.')
                if cut > 100:
                    reply = reply[:cut + 1]
                else:
                    reply = reply[:MAX_RESPONSE_CHARS - 3] + "..."

            return reply

        except Exception as e:
            logger.error("wa_client_ai_failed", phone=phone, error=str(e))
            return None

    async def _get_case_context(
        self, tenant_id: UUID, client_id: Optional[str]
    ) -> Optional[str]:
        """Look up active case info for a linked client."""
        if not client_id:
            return None

        try:
            from app.database import get_supabase_admin_client
            db = get_supabase_admin_client()

            result = db.table('cases') \
                .select('case_number, document_type, status') \
                .eq('tenant_id', str(tenant_id)) \
                .eq('client_id', client_id) \
                .neq('status', 'cerrado') \
                .neq('status', 'cancelado') \
                .order('created_at', desc=True) \
                .limit(3) \
                .execute()

            if not result.data:
                return None

            from app.services.case_workflow_service import STATUS_LABELS

            lines = []
            for case in result.data:
                status_label = STATUS_LABELS.get(case['status'], case['status'])
                lines.append(
                    f"- Expediente {case['case_number']} ({case['document_type']}): {status_label}"
                )

            return "\n".join(lines)

        except Exception as e:
            logger.warning("wa_client_ai_case_context_failed", error=str(e))
            return None

    def _build_messages(
        self,
        current_message: str,
        recent_messages: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, str]]:
        """Build conversation messages for the LLM from recent history."""
        messages: List[Dict[str, str]] = []

        if recent_messages:
            for msg in recent_messages[-MAX_CONTEXT_MESSAGES:]:
                sender = msg.get('sender_type', 'client')
                content = msg.get('content', '')
                if not content:
                    continue
                if sender == 'client':
                    messages.append({"role": "user", "content": content})
                elif sender in ('agent', 'bot', 'system'):
                    messages.append({"role": "assistant", "content": content})

        # Ensure the last message is the current user message
        if messages and messages[-1].get('role') == 'user':
            # Replace last user message with current one (it's the same)
            messages[-1] = {"role": "user", "content": current_message}
        else:
            messages.append({"role": "user", "content": current_message})

        # Ensure messages alternate properly and start with user
        if messages and messages[0].get('role') != 'user':
            messages = messages[1:]

        # Ensure at least one message
        if not messages:
            messages = [{"role": "user", "content": current_message}]

        return messages


# Singleton
wa_client_ai_service = WAClientAIService()
