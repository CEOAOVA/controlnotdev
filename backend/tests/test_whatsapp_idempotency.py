"""
Tests for WhatsApp message idempotency.
Verifies that duplicate incoming messages are skipped.
"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


TENANT_ID = 'a0000000-0000-0000-0000-000000000001'


class TestIdempotency:
    """Tests for duplicate message skipping in _process_incoming_message"""

    @pytest.mark.asyncio
    async def test_duplicate_message_skipped(self):
        """Should skip processing if message ID already exists"""
        mock_repo = MagicMock()
        mock_repo.get_message_by_wa_id = AsyncMock(return_value={'id': 'existing-msg-uuid'})
        mock_repo.get_or_create_contact = AsyncMock()
        mock_repo.get_or_create_conversation = AsyncMock()
        mock_repo.create_message = AsyncMock()

        with patch('app.api.endpoints.whatsapp.wa_repository', mock_repo):
            from app.api.endpoints.whatsapp import _process_incoming_message

            await _process_incoming_message(
                tenant_id=TENANT_ID,
                phone='5215512345678',
                msg_id='wamid.duplicate123',
                msg_type='text',
                content='Hola duplicado',
            )

            mock_repo.get_message_by_wa_id.assert_called_once_with('wamid.duplicate123')
            mock_repo.get_or_create_contact.assert_not_called()
            mock_repo.get_or_create_conversation.assert_not_called()
            mock_repo.create_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_new_message_processed(self):
        """Should process a new message normally"""
        mock_repo = MagicMock()
        mock_repo.get_message_by_wa_id = AsyncMock(return_value=None)
        mock_repo.get_or_create_contact = AsyncMock(return_value={
            'id': 'a0000000-0000-0000-0000-000000000099',
            'client_id': None,
        })
        mock_repo.get_or_create_conversation = AsyncMock(return_value={
            'id': 'a0000000-0000-0000-0000-000000000088',
            'assigned_to': 'agent-1',  # assigned -> no auto-reply
        })
        mock_repo.create_message = AsyncMock(return_value={'id': 'msg-uuid'})
        mock_repo.increment_unread = AsyncMock()
        mock_repo.get_notification_rules = AsyncMock(return_value=[])

        mock_staff_router = MagicMock()
        mock_staff_router.route_message = AsyncMock(return_value=False)

        mock_wa_service = MagicMock()

        with patch('app.api.endpoints.whatsapp.wa_repository', mock_repo), \
             patch('app.api.endpoints.whatsapp.whatsapp_service', mock_wa_service), \
             patch('app.services.wa_staff_router.wa_staff_router', mock_staff_router):

            from app.api.endpoints.whatsapp import _process_incoming_message

            await _process_incoming_message(
                tenant_id=TENANT_ID,
                phone='5215512345678',
                msg_id='wamid.new456',
                msg_type='text',
                content='Hola nuevo',
            )

            mock_repo.get_message_by_wa_id.assert_called_once_with('wamid.new456')
            mock_repo.get_or_create_contact.assert_called_once()
            mock_repo.create_message.assert_called_once()
            mock_repo.increment_unread.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_msg_id_not_checked(self):
        """Should skip idempotency check when msg_id is empty"""
        mock_repo = MagicMock()
        mock_repo.get_message_by_wa_id = AsyncMock(return_value=None)
        mock_repo.get_or_create_contact = AsyncMock(return_value={
            'id': 'a0000000-0000-0000-0000-000000000099',
            'client_id': None,
        })
        mock_repo.get_or_create_conversation = AsyncMock(return_value={
            'id': 'a0000000-0000-0000-0000-000000000088',
            'assigned_to': 'agent-1',
        })
        mock_repo.create_message = AsyncMock(return_value={'id': 'msg-uuid'})
        mock_repo.increment_unread = AsyncMock()
        mock_repo.get_notification_rules = AsyncMock(return_value=[])

        mock_staff_router = MagicMock()
        mock_staff_router.route_message = AsyncMock(return_value=False)

        mock_wa_service = MagicMock()

        with patch('app.api.endpoints.whatsapp.wa_repository', mock_repo), \
             patch('app.api.endpoints.whatsapp.whatsapp_service', mock_wa_service), \
             patch('app.services.wa_staff_router.wa_staff_router', mock_staff_router):

            from app.api.endpoints.whatsapp import _process_incoming_message

            await _process_incoming_message(
                tenant_id=TENANT_ID,
                phone='5215512345678',
                msg_id='',
                msg_type='text',
                content='Mensaje sin ID',
            )

            mock_repo.get_message_by_wa_id.assert_not_called()
            mock_repo.get_or_create_contact.assert_called_once()
