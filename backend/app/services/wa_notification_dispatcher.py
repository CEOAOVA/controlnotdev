"""
ControlNot v2 - WhatsApp Notification Dispatcher
Centralized dispatcher for case-related notifications.
Looks up client phones from case_parties and delegates to wa_notification_service.
"""
from typing import Optional
from uuid import UUID
import structlog

logger = structlog.get_logger()


async def dispatch_case_notification(
    tenant_id: str,
    case_id: str,
    event_type: str,
    message: str,
    notify_staff: bool = True,
) -> None:
    """
    Send WhatsApp notifications for a case event.

    - Looks up phones from case_parties (same logic as case_workflow_service)
    - Sends to each client phone via wa_notification_service.notify_case_event()
    - Optionally notifies staff via wa_notification_service.notify_staff_event()
    - Never raises — all errors are logged and swallowed.
    """
    try:
        from app.repositories.wa_repository import wa_repository
        from app.services.wa_notification_service import wa_notification_service

        tid = UUID(tenant_id)
        cid = UUID(case_id)

        # Check if there's a notification rule for this event type
        rules = await wa_repository.get_notification_rules(tid, event_type)
        if rules:
            rule = rules[0]
            rule_message = rule.get('message_text')
            if rule_message:
                message = rule_message
            rule_notify_staff = rule.get('notify_staff', notify_staff)
            notify_staff = rule_notify_staff
        elif not rules:
            # No rule configured — still send with the provided message
            pass

        # Look up client phones from case_parties
        from app.database import get_supabase_admin_client
        client = get_supabase_admin_client()

        result = client.table('case_parties') \
            .select('nombre, telefono') \
            .eq('case_id', case_id) \
            .neq('telefono', '') \
            .execute()

        parties_with_phone = [
            p for p in (result.data or [])
            if p.get('telefono')
        ]

        # Notify each client
        for party in parties_with_phone:
            phone = party['telefono']
            try:
                await wa_notification_service.notify_case_event(
                    tenant_id=tid,
                    event_type=event_type,
                    case_id=cid,
                    phone=phone,
                    message=message,
                )
            except Exception as e:
                logger.warning(
                    "dispatch_client_notify_failed",
                    phone=phone, event_type=event_type, error=str(e),
                )

        # Notify staff
        if notify_staff:
            try:
                await wa_notification_service.notify_staff_event(
                    tenant_id=tid,
                    event_type=event_type,
                    message=message,
                    case_id=cid,
                )
            except Exception as e:
                logger.warning(
                    "dispatch_staff_notify_failed",
                    event_type=event_type, error=str(e),
                )

        logger.info(
            "dispatch_notification_done",
            event_type=event_type,
            case_id=case_id,
            clients_notified=len(parties_with_phone),
        )

    except Exception as e:
        logger.error(
            "dispatch_notification_failed",
            event_type=event_type,
            case_id=case_id,
            error=str(e),
        )
