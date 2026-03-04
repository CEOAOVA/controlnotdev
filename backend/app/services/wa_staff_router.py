"""
ControlNot v2 - WhatsApp Staff Router
Routes incoming messages from registered staff phones to interactive menu handlers.
"""
from typing import Any, Dict, Optional
from uuid import UUID
import structlog

from app.repositories.wa_repository import wa_repository

logger = structlog.get_logger()


class WAStaffRouter:
    """Routes WhatsApp messages from staff phones to menu handlers"""

    async def is_staff_phone(
        self, phone: str, tenant_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Check if a phone number belongs to registered staff. Returns staff record or None."""
        return await wa_repository.get_staff_by_phone(tenant_id, phone)

    async def route_message(
        self, tenant_id: str, phone: str, message_payload: Dict[str, Any]
    ) -> bool:
        """
        Route an incoming message from a staff phone.

        Args:
            tenant_id: Tenant ID string
            phone: Sender phone number
            message_payload: Dict with keys: content, msg_type, interactive_id, interactive_type

        Returns:
            True if message was handled (staff phone), False otherwise (let client flow handle it)
        """
        tid = UUID(tenant_id)
        staff = await self.is_staff_phone(phone, tid)
        if not staff:
            return False

        try:
            # Parse the user input
            user_input = self._parse_input(message_payload)

            # Load session state
            session = self._get_session(staff)

            # Lazy import to avoid circular imports
            from app.services.wa_menu_handlers import menu_handler

            # Dispatch to menu handler
            await menu_handler.handle(
                tenant_id=tid,
                phone=phone,
                staff=staff,
                user_input=user_input,
                session=session,
            )

            # Log the command
            await wa_repository.log_command(
                tenant_id=tid,
                staff_phone=phone,
                command=user_input.get('text', user_input.get('id', 'unknown')),
                user_id=UUID(staff['user_id']) if staff.get('user_id') else None,
                payload=message_payload,
                result='ok',
                response_preview=user_input.get('text', '')[:200],
            )

        except Exception as e:
            logger.error("wa_staff_route_error", phone=phone, error=str(e))
            # Send error message to staff
            from app.services.whatsapp_service import whatsapp_service
            await whatsapp_service.send_text(
                phone, "Error procesando tu solicitud. Envia 'menu' para reiniciar."
            )

        return True

    def _parse_input(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the raw message payload into a normalized input dict."""
        msg_type = payload.get('msg_type', 'text')

        if msg_type == 'interactive':
            return {
                'type': 'interactive',
                'interactive_type': payload.get('interactive_type', ''),
                'id': payload.get('interactive_id', ''),
                'text': payload.get('content', ''),
            }

        # Text message
        text = (payload.get('content', '') or '').strip().lower()
        return {
            'type': 'text',
            'text': text,
            'raw': payload.get('content', ''),
        }

    def _get_session(self, staff: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current session state from staff record."""
        return staff.get('session_state') or {}


# Singleton
wa_staff_router = WAStaffRouter()
