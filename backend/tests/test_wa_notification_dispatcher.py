"""
Tests for WhatsApp Notification Dispatcher
Verifies dispatch_case_notification looks up case_parties and delegates correctly.
"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

TENANT_ID = 'a0000000-0000-0000-0000-000000000001'
CASE_ID = 'a0000000-0000-0000-0000-000000001001'
TENANT_UUID = UUID(TENANT_ID)
CASE_UUID = UUID(CASE_ID)


def _make_mock_db(parties):
    """Create a mock Supabase client that returns given parties."""
    mock_execute = MagicMock()
    mock_execute.data = parties

    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.neq.return_value.execute.return_value = mock_execute
    return mock_db


class TestDispatchCaseNotification:
    """Tests for dispatch_case_notification()"""

    @pytest.mark.asyncio
    async def test_dispatches_to_client_phones(self):
        """Should look up case_parties and notify each client phone"""
        mock_repo = MagicMock()
        mock_repo.get_notification_rules = AsyncMock(return_value=[])

        mock_notify_svc = MagicMock()
        mock_notify_svc.notify_case_event = AsyncMock(return_value=True)
        mock_notify_svc.notify_staff_event = AsyncMock(return_value=True)

        mock_db = _make_mock_db([
            {'nombre': 'Juan Perez', 'telefono': '5215512345678'},
            {'nombre': 'Ana Garcia', 'telefono': '5215587654321'},
        ])

        with patch('app.repositories.wa_repository.wa_repository', mock_repo), \
             patch('app.services.wa_notification_service.wa_notification_service', mock_notify_svc), \
             patch('app.database.get_supabase_admin_client', return_value=mock_db):

            from app.services.wa_notification_dispatcher import dispatch_case_notification

            await dispatch_case_notification(
                tenant_id=TENANT_ID,
                case_id=CASE_ID,
                event_type='status_change',
                message='Su expediente cambio de estado.',
            )

            assert mock_notify_svc.notify_case_event.call_count == 2
            phones_called = [
                call.kwargs['phone'] for call in mock_notify_svc.notify_case_event.call_args_list
            ]
            assert '5215512345678' in phones_called
            assert '5215587654321' in phones_called

    @pytest.mark.asyncio
    async def test_uses_rule_message_when_available(self):
        """Should override message with notification rule's message_text"""
        mock_repo = MagicMock()
        mock_repo.get_notification_rules = AsyncMock(return_value=[{
            'message_text': 'Mensaje personalizado',
            'notify_staff': False,
        }])

        mock_notify_svc = MagicMock()
        mock_notify_svc.notify_case_event = AsyncMock(return_value=True)
        mock_notify_svc.notify_staff_event = AsyncMock(return_value=True)

        mock_db = _make_mock_db([{'nombre': 'Test', 'telefono': '5215500001111'}])

        with patch('app.repositories.wa_repository.wa_repository', mock_repo), \
             patch('app.services.wa_notification_service.wa_notification_service', mock_notify_svc), \
             patch('app.database.get_supabase_admin_client', return_value=mock_db):

            from app.services.wa_notification_dispatcher import dispatch_case_notification

            await dispatch_case_notification(
                tenant_id=TENANT_ID,
                case_id=CASE_ID,
                event_type='status_change',
                message='Original message',
            )

            call_kwargs = mock_notify_svc.notify_case_event.call_args.kwargs
            assert call_kwargs['message'] == 'Mensaje personalizado'
            mock_notify_svc.notify_staff_event.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_parties_no_error(self):
        """Should handle case with no parties gracefully"""
        mock_repo = MagicMock()
        mock_repo.get_notification_rules = AsyncMock(return_value=[])

        mock_notify_svc = MagicMock()
        mock_notify_svc.notify_case_event = AsyncMock()
        mock_notify_svc.notify_staff_event = AsyncMock(return_value=True)

        mock_db = _make_mock_db([])

        with patch('app.repositories.wa_repository.wa_repository', mock_repo), \
             patch('app.services.wa_notification_service.wa_notification_service', mock_notify_svc), \
             patch('app.database.get_supabase_admin_client', return_value=mock_db):

            from app.services.wa_notification_dispatcher import dispatch_case_notification

            await dispatch_case_notification(
                tenant_id=TENANT_ID,
                case_id=CASE_ID,
                event_type='case_created',
                message='Caso creado.',
            )

            mock_notify_svc.notify_case_event.assert_not_called()
            mock_notify_svc.notify_staff_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_never_raises_on_error(self):
        """dispatch_case_notification should swallow all exceptions"""
        mock_repo = MagicMock()
        mock_repo.get_notification_rules = AsyncMock(side_effect=Exception("DB down"))

        with patch('app.repositories.wa_repository.wa_repository', mock_repo):
            from app.services.wa_notification_dispatcher import dispatch_case_notification

            # Should NOT raise
            await dispatch_case_notification(
                tenant_id=TENANT_ID,
                case_id=CASE_ID,
                event_type='status_change',
                message='test',
            )
