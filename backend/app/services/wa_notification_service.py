"""
ControlNot v2 - WhatsApp Notification Service
Automatic notifications based on system events
"""
from typing import Any, Dict, List, Optional
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
        """
        Send notification for a case event.

        Checks wa_notification_rules first to see if a template is configured
        for this event_type. Falls back to the provided message/template_name.
        """
        if not phone:
            logger.debug("wa_notify_no_phone", event_type=event_type)
            return False

        try:
            # Check notification rules for this event type
            rules = await wa_repository.get_notification_rules(
                tenant_id=tenant_id,
                event_type=event_type,
            )
            if rules:
                rule = rules[0]
                rule_template = rule.get('template_id') or rule.get('template_name')
                rule_message = rule.get('message_text')
                if rule_template:
                    template_name = rule_template
                elif rule_message:
                    message = rule_message

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


    async def notify_staff_event(
        self,
        tenant_id: UUID,
        event_type: str,
        message: str,
        case_id: Optional[UUID] = None,
        role_filter: Optional[str] = None,
    ) -> int:
        """
        Send a notification to all active staff phones for a tenant.

        Args:
            tenant_id: Tenant ID
            event_type: Event type for logging
            message: Text message to send
            case_id: Optional case ID for context
            role_filter: Optional role to filter (notario, asistente, etc.)

        Returns:
            Number of staff members notified
        """
        try:
            staff_phones = await wa_repository.list_staff_phones(tenant_id)
            active = [s for s in staff_phones if s.get('is_active')]

            if role_filter:
                active = [s for s in active if s.get('role') == role_filter]

            notified = 0
            for staff in active:
                phone = staff.get('phone')
                if not phone:
                    continue
                result = await whatsapp_service.send_text(phone, message)
                if result:
                    notified += 1

            logger.info(
                "wa_staff_notification_sent",
                event_type=event_type,
                notified=notified,
                total_staff=len(active),
            )
            return notified
        except Exception as e:
            logger.error("wa_staff_notification_failed", event_type=event_type, error=str(e))
            return 0

    async def send_daily_digest(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Generate and send a daily digest to all staff phones.
        Includes: active cases, overdue tramites, upcoming deadlines.
        """
        try:
            from app.repositories import CaseRepository
            from app.services.tramite_service import tramite_service

            case_repo = CaseRepository()
            stats = await case_repo.get_case_statistics(tenant_id)
            overdue = await tramite_service.get_overdue(tenant_id)
            upcoming = await tramite_service.get_upcoming(tenant_id, days=3)

            total = stats.get('total_cases', 0)
            by_status = stats.get('by_status', {})
            active = total - by_status.get('cerrado', 0) - by_status.get('cancelado', 0)

            msg = (
                "*📋 Resumen Diario — ControlNot*\n\n"
                f"Expedientes activos: {active}\n"
                f"Total expedientes: {total}\n"
            )

            if overdue:
                msg += f"\n🔴 *Tramites Vencidos ({len(overdue)}):*\n"
                for t in overdue[:5]:
                    msg += f"  - {t.get('nombre', '')}\n"
                if len(overdue) > 5:
                    msg += f"  ... y {len(overdue) - 5} mas\n"

            if upcoming:
                msg += f"\n🟡 *Proximos a vencer ({len(upcoming)}):*\n"
                for t in upcoming[:5]:
                    fecha = (t.get('fecha_limite', '') or '')[:10]
                    msg += f"  - {t.get('nombre', '')} ({fecha})\n"
                if len(upcoming) > 5:
                    msg += f"  ... y {len(upcoming) - 5} mas\n"

            if not overdue and not upcoming:
                msg += "\n✅ Sin alertas pendientes.\n"

            msg += "\nEnvia 'menu' para gestionar desde aqui."

            notified = await self.notify_staff_event(
                tenant_id=tenant_id,
                event_type='daily_digest',
                message=msg,
            )

            return {
                'notified': notified,
                'active_cases': active,
                'overdue_tramites': len(overdue),
                'upcoming_tramites': len(upcoming),
            }
        except Exception as e:
            logger.error("wa_daily_digest_failed", error=str(e))
            return {'error': str(e), 'notified': 0}


# Singleton
wa_notification_service = WANotificationService()
