"""
ControlNot v2 - WhatsApp Notification Service
Automatic notifications based on system events
"""
from typing import Any, Dict, Optional
from uuid import UUID
import structlog

from app.services.whatsapp_service import whatsapp_service
from app.repositories.wa_repository import wa_repository

logger = structlog.get_logger()


class WANotificationService:
    """Service for sending automatic WhatsApp notifications"""

    async def notify_case_event(
        self,
        tenant_id: UUID,
        event_type: str,
        case_id: UUID,
        phone: Optional[str] = None,
        message: Optional[str] = None,
        template_name: Optional[str] = None,
    ) -> bool:
        """Send notification for a case event"""
        if not phone:
            logger.debug("wa_notify_no_phone", event_type=event_type)
            return False

        try:
            # Get or create contact
            contact = await wa_repository.get_or_create_contact(
                tenant_id=tenant_id,
                phone=phone,
            )

            # Get or create conversation
            conversation = await wa_repository.get_or_create_conversation(
                tenant_id=tenant_id,
                contact_id=UUID(contact['id']),
                case_id=case_id,
            )

            # Send via template or text
            result = None
            if template_name:
                result = await whatsapp_service.send_template(
                    to_phone=phone,
                    template_name=template_name,
                )
            elif message:
                result = await whatsapp_service.send_text(
                    to_phone=phone,
                    message=message,
                )

            if result:
                # Record the message
                wa_msg_id = result.get('messages', [{}])[0].get('id')
                await wa_repository.create_message(
                    tenant_id=tenant_id,
                    conversation_id=UUID(conversation['id']),
                    content=message or f'[Template: {template_name}]',
                    sender_type='system',
                    message_type='template' if template_name else 'text',
                    whatsapp_message_id=wa_msg_id,
                )
                logger.info("wa_notification_sent", event_type=event_type, phone=phone)
                return True

            return False
        except Exception as e:
            logger.error("wa_notification_failed", event_type=event_type, error=str(e))
            return False


# Singleton
wa_notification_service = WANotificationService()
