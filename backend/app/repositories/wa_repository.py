"""
ControlNot v2 - WhatsApp Repository
CRUD para tablas de WhatsApp: contacts, conversations, messages
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.database import get_supabase_admin_client

logger = structlog.get_logger()


class WARepository:
    """Repository for WhatsApp tables"""

    def __init__(self):
        self.client = get_supabase_admin_client()

    # === Contacts ===

    async def get_or_create_contact(
        self,
        tenant_id: UUID,
        phone: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get existing contact or create new one"""
        try:
            result = self.client.table('wa_contacts')\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .eq('phone', phone)\
                .limit(1)\
                .execute()

            if result.data:
                return result.data[0]

            data = {
                'tenant_id': str(tenant_id),
                'phone': phone,
            }
            if name:
                data['name'] = name

            result = self.client.table('wa_contacts').insert(data).execute()
            return result.data[0]
        except APIError as e:
            logger.error("wa_contact_failed", phone=phone, error=str(e))
            raise

    async def link_contact_to_client(
        self, contact_id: UUID, client_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Link a WhatsApp contact to a client"""
        try:
            result = self.client.table('wa_contacts')\
                .update({'client_id': str(client_id)})\
                .eq('id', str(contact_id))\
                .execute()
            return result.data[0] if result.data else None
        except APIError as e:
            logger.error("wa_link_contact_failed", error=str(e))
            raise

    # === Conversations ===

    async def list_conversations(
        self,
        tenant_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List conversations with contact info"""
        try:
            query = self.client.table('wa_conversations')\
                .select('*, wa_contacts(id, phone, name, client_id)')\
                .eq('tenant_id', str(tenant_id))

            if status:
                query = query.eq('status', status)

            result = query\
                .order('last_message_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return result.data if result.data else []
        except APIError as e:
            logger.error("wa_conversations_list_failed", error=str(e))
            raise

    async def get_or_create_conversation(
        self,
        tenant_id: UUID,
        contact_id: UUID,
        case_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Get existing conversation or create new"""
        try:
            query = self.client.table('wa_conversations')\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .eq('contact_id', str(contact_id))\
                .eq('status', 'open')\
                .limit(1)

            result = query.execute()
            if result.data:
                return result.data[0]

            data = {
                'tenant_id': str(tenant_id),
                'contact_id': str(contact_id),
                'status': 'open',
            }
            if case_id:
                data['case_id'] = str(case_id)

            result = self.client.table('wa_conversations').insert(data).execute()
            return result.data[0]
        except APIError as e:
            logger.error("wa_conversation_create_failed", error=str(e))
            raise

    async def update_conversation(
        self, conversation_id: UUID, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update conversation fields"""
        try:
            result = self.client.table('wa_conversations')\
                .update(updates)\
                .eq('id', str(conversation_id))\
                .execute()
            return result.data[0] if result.data else None
        except APIError as e:
            logger.error("wa_conversation_update_failed", error=str(e))
            raise

    # === Messages ===

    async def list_messages(
        self,
        conversation_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List messages for a conversation"""
        try:
            result = self.client.table('wa_messages')\
                .select('*')\
                .eq('conversation_id', str(conversation_id))\
                .order('timestamp', desc=False)\
                .range(offset, offset + limit - 1)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("wa_messages_list_failed", error=str(e))
            raise

    async def create_message(
        self,
        tenant_id: UUID,
        conversation_id: UUID,
        content: str,
        sender_type: str = 'agent',
        sender_id: Optional[str] = None,
        message_type: str = 'text',
        whatsapp_message_id: Optional[str] = None,
        media_url: Optional[str] = None,
        status: str = 'sent',
    ) -> Optional[Dict[str, Any]]:
        """Create a message record"""
        try:
            data: Dict[str, Any] = {
                'tenant_id': str(tenant_id),
                'conversation_id': str(conversation_id),
                'content': content,
                'sender_type': sender_type,
                'message_type': message_type,
                'status': status,
            }
            if sender_id:
                data['sender_id'] = sender_id
            if whatsapp_message_id:
                data['whatsapp_message_id'] = whatsapp_message_id
            if media_url:
                data['media_url'] = media_url

            result = self.client.table('wa_messages').insert(data).execute()

            # Update conversation last message
            if result.data:
                preview = content[:100] if content else ''
                await self.update_conversation(conversation_id, {
                    'last_message_at': result.data[0].get('timestamp'),
                    'last_message_preview': preview,
                })

            return result.data[0] if result.data else None
        except APIError as e:
            logger.error("wa_message_create_failed", error=str(e))
            raise

    async def update_message_status(
        self,
        whatsapp_message_id: str,
        status: str,
    ) -> Optional[Dict[str, Any]]:
        """Update message status by WhatsApp message ID (for delivery/read callbacks)"""
        try:
            result = self.client.table('wa_messages')\
                .update({'status': status})\
                .eq('whatsapp_message_id', whatsapp_message_id)\
                .execute()
            return result.data[0] if result.data else None
        except APIError as e:
            logger.warning("wa_message_status_update_failed", wa_msg_id=whatsapp_message_id, error=str(e))
            return None

    async def increment_unread(self, conversation_id: UUID) -> None:
        """Increment unread_count for a conversation"""
        try:
            conv = self.client.table('wa_conversations')\
                .select('unread_count')\
                .eq('id', str(conversation_id))\
                .limit(1)\
                .execute()
            current = conv.data[0]['unread_count'] if conv.data else 0
            self.client.table('wa_conversations')\
                .update({'unread_count': current + 1})\
                .eq('id', str(conversation_id))\
                .execute()
        except APIError as e:
            logger.warning("wa_increment_unread_failed", error=str(e))

    # === Templates ===

    # === Notification Rules ===

    async def get_notification_rules(
        self,
        tenant_id: UUID,
        event_type: str,
    ) -> List[Dict[str, Any]]:
        """Get active notification rules for a given event type"""
        try:
            result = self.client.table('wa_notification_rules')\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .eq('event_type', event_type)\
                .eq('is_active', True)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.warning("wa_notification_rules_failed", event_type=event_type, error=str(e))
            return []

    async def list_templates(
        self, tenant_id: UUID
    ) -> List[Dict[str, Any]]:
        """List WhatsApp message templates"""
        try:
            result = self.client.table('wa_templates')\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .eq('is_active', True)\
                .order('created_at', desc=True)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("wa_templates_list_failed", error=str(e))
            raise

    # === Staff Phones ===

    async def get_staff_by_phone(
        self, tenant_id: UUID, phone: str
    ) -> Optional[Dict[str, Any]]:
        """Get active staff record by phone number"""
        try:
            result = self.client.table('wa_staff_phones')\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .eq('phone', phone)\
                .eq('is_active', True)\
                .limit(1)\
                .execute()
            return result.data[0] if result.data else None
        except APIError as e:
            logger.warning("wa_staff_by_phone_failed", phone=phone, error=str(e))
            return None

    async def list_staff_phones(
        self, tenant_id: UUID
    ) -> List[Dict[str, Any]]:
        """List all staff phones for a tenant"""
        try:
            result = self.client.table('wa_staff_phones')\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .order('created_at', desc=True)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("wa_staff_phones_list_failed", error=str(e))
            raise

    async def create_staff_phone(
        self, tenant_id: UUID, phone: str, display_name: str,
        user_id: Optional[UUID] = None, role: str = 'asistente'
    ) -> Dict[str, Any]:
        """Register a staff phone number"""
        try:
            data: Dict[str, Any] = {
                'tenant_id': str(tenant_id),
                'phone': phone,
                'display_name': display_name,
                'role': role,
            }
            if user_id:
                data['user_id'] = str(user_id)
            result = self.client.table('wa_staff_phones').insert(data).execute()
            return result.data[0]
        except APIError as e:
            logger.error("wa_staff_phone_create_failed", error=str(e))
            raise

    async def update_staff_phone(
        self, staff_id: UUID, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a staff phone record"""
        try:
            result = self.client.table('wa_staff_phones')\
                .update(updates)\
                .eq('id', str(staff_id))\
                .execute()
            return result.data[0] if result.data else None
        except APIError as e:
            logger.error("wa_staff_phone_update_failed", error=str(e))
            raise

    async def delete_staff_phone(self, staff_id: UUID) -> bool:
        """Delete a staff phone record"""
        try:
            self.client.table('wa_staff_phones')\
                .delete()\
                .eq('id', str(staff_id))\
                .execute()
            return True
        except APIError as e:
            logger.error("wa_staff_phone_delete_failed", error=str(e))
            return False

    async def update_staff_session(
        self, tenant_id: UUID, phone: str, session_state: Dict[str, Any]
    ) -> None:
        """Update the session_state JSONB for a staff phone"""
        try:
            self.client.table('wa_staff_phones')\
                .update({'session_state': session_state})\
                .eq('tenant_id', str(tenant_id))\
                .eq('phone', phone)\
                .execute()
        except APIError as e:
            logger.warning("wa_staff_session_update_failed", error=str(e))

    # === Command Log ===

    async def log_command(
        self, tenant_id: UUID, staff_phone: str,
        command: str, user_id: Optional[UUID] = None,
        payload: Optional[Dict[str, Any]] = None,
        result: Optional[str] = None,
        response_preview: Optional[str] = None,
    ) -> None:
        """Log a staff command execution"""
        try:
            data: Dict[str, Any] = {
                'tenant_id': str(tenant_id),
                'staff_phone': staff_phone,
                'command': command,
            }
            if user_id:
                data['user_id'] = str(user_id)
            if payload:
                data['payload'] = payload
            if result:
                data['result'] = result
            if response_preview:
                data['response_preview'] = response_preview[:200]
            self.client.table('wa_command_log').insert(data).execute()
        except APIError as e:
            logger.warning("wa_command_log_failed", error=str(e))

    async def list_command_log(
        self, tenant_id: UUID, limit: int = 50, offset: int = 0,
        staff_phone: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List command log entries"""
        try:
            query = self.client.table('wa_command_log')\
                .select('*')\
                .eq('tenant_id', str(tenant_id))
            if staff_phone:
                query = query.eq('staff_phone', staff_phone)
            result = query\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("wa_command_log_list_failed", error=str(e))
            raise

    # === Notification Rules CRUD ===

    async def list_notification_rules(
        self, tenant_id: UUID
    ) -> List[Dict[str, Any]]:
        """List all notification rules for a tenant"""
        try:
            result = self.client.table('wa_notification_rules')\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .order('created_at', desc=True)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("wa_notification_rules_list_failed", error=str(e))
            raise

    async def create_notification_rule(
        self, tenant_id: UUID, event_type: str,
        is_active: bool = True, notify_staff: bool = False,
        template_id: Optional[UUID] = None,
        message_text: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a notification rule"""
        try:
            data: Dict[str, Any] = {
                'tenant_id': str(tenant_id),
                'event_type': event_type,
                'is_active': is_active,
                'notify_staff': notify_staff,
            }
            if template_id:
                data['template_id'] = str(template_id)
            if message_text:
                data['message_text'] = message_text
            if conditions:
                data['conditions'] = conditions
            result = self.client.table('wa_notification_rules').insert(data).execute()
            return result.data[0]
        except APIError as e:
            logger.error("wa_notification_rule_create_failed", error=str(e))
            raise

    async def update_notification_rule(
        self, rule_id: UUID, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a notification rule"""
        try:
            result = self.client.table('wa_notification_rules')\
                .update(updates)\
                .eq('id', str(rule_id))\
                .execute()
            return result.data[0] if result.data else None
        except APIError as e:
            logger.error("wa_notification_rule_update_failed", error=str(e))
            raise

    async def delete_notification_rule(self, rule_id: UUID) -> bool:
        """Delete a notification rule"""
        try:
            self.client.table('wa_notification_rules')\
                .delete()\
                .eq('id', str(rule_id))\
                .execute()
            return True
        except APIError as e:
            logger.error("wa_notification_rule_delete_failed", error=str(e))
            return False

    # === Phone-Tenant Map (Multi-tenant routing) ===

    async def get_phone_tenant_mapping(self, phone_number_id: str) -> Optional[Dict[str, Any]]:
        """Buscar mapeo completo en wa_phone_tenant_map por phone_number_id de Meta.
        Returns dict with tenant_id and is_platform, or None."""
        try:
            result = self.client.table('wa_phone_tenant_map')\
                .select('tenant_id, is_platform')\
                .eq('phone_number_id', phone_number_id)\
                .maybe_single()\
                .execute()
            return result.data if result.data else None
        except APIError as e:
            logger.warning("wa_phone_tenant_map_lookup_failed", phone_number_id=phone_number_id, error=str(e))
            return None

    async def get_tenant_by_phone_number_id(self, phone_number_id: str) -> Optional[str]:
        """Buscar tenant_id en wa_phone_tenant_map por phone_number_id de Meta (compat)"""
        mapping = await self.get_phone_tenant_mapping(phone_number_id)
        return mapping['tenant_id'] if mapping else None

    async def get_staff_by_phone_any_tenant(self, phone: str) -> Optional[Dict[str, Any]]:
        """Search for a staff phone across ALL tenants (used for platform number routing)"""
        try:
            result = self.client.table('wa_staff_phones')\
                .select('*')\
                .eq('phone', phone)\
                .eq('is_active', True)\
                .limit(1)\
                .execute()
            return result.data[0] if result.data else None
        except APIError as e:
            logger.warning("wa_staff_by_phone_any_tenant_failed", phone=phone, error=str(e))
            return None

    async def list_phone_tenant_map(self) -> List[Dict[str, Any]]:
        """List all phone-tenant mappings"""
        try:
            result = self.client.table('wa_phone_tenant_map')\
                .select('*')\
                .order('created_at', desc=True)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("wa_phone_tenant_map_list_failed", error=str(e))
            raise

    async def create_phone_tenant_map(
        self, phone_number_id: str, tenant_id: str, is_platform: bool = False
    ) -> Dict[str, Any]:
        """Create a phone_number_id → tenant_id mapping"""
        try:
            result = self.client.table('wa_phone_tenant_map').insert({
                'phone_number_id': phone_number_id,
                'tenant_id': tenant_id,
                'is_platform': is_platform,
            }).execute()
            return result.data[0]
        except APIError as e:
            logger.error("wa_phone_tenant_map_create_failed", error=str(e))
            raise

    async def delete_phone_tenant_map(self, map_id: UUID) -> bool:
        """Delete a phone-tenant mapping"""
        try:
            self.client.table('wa_phone_tenant_map')\
                .delete()\
                .eq('id', str(map_id))\
                .execute()
            return True
        except APIError as e:
            logger.error("wa_phone_tenant_map_delete_failed", error=str(e))
            return False

    # === Idempotency & Cleanup ===

    async def get_message_by_wa_id(self, whatsapp_message_id: str) -> Optional[Dict[str, Any]]:
        """Check if a message with this WhatsApp message ID already exists."""
        try:
            result = self.client.table('wa_messages')\
                .select('id, whatsapp_message_id')\
                .eq('whatsapp_message_id', whatsapp_message_id)\
                .limit(1)\
                .execute()
            return result.data[0] if result.data else None
        except APIError as e:
            logger.warning("wa_get_message_by_wa_id_failed", wa_id=whatsapp_message_id, error=str(e))
            return None

    async def cleanup_stale_sessions(self, older_than_hours: int = 72) -> int:
        """Clear session_state for staff phones inactive for more than N hours."""
        try:
            from datetime import datetime, timedelta, timezone
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=older_than_hours)).isoformat()

            # Get staff with non-empty session_state updated before cutoff
            result = self.client.table('wa_staff_phones')\
                .select('id, session_state, updated_at')\
                .lt('updated_at', cutoff)\
                .execute()

            cleaned = 0
            for staff in (result.data or []):
                session = staff.get('session_state')
                if session and isinstance(session, dict) and len(str(session)) > 100:
                    self.client.table('wa_staff_phones')\
                        .update({'session_state': {}})\
                        .eq('id', staff['id'])\
                        .execute()
                    cleaned += 1

            if cleaned:
                logger.info("wa_stale_sessions_cleaned", count=cleaned)
            return cleaned
        except APIError as e:
            logger.warning("wa_cleanup_stale_sessions_failed", error=str(e))
            return 0

    # === Message Media Update ===

    async def update_message_media(self, message_id: UUID, media_path: str):
        """Update a message record with the stored media path"""
        try:
            self.client.table('wa_messages')\
                .update({'media_url': media_path})\
                .eq('id', str(message_id))\
                .execute()
        except APIError as e:
            logger.warning("wa_message_media_update_failed", message_id=str(message_id), error=str(e))


# Singleton
wa_repository = WARepository()
