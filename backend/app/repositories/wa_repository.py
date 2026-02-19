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

    # === Templates ===

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


# Singleton
wa_repository = WARepository()
