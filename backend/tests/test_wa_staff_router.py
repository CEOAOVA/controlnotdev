"""
Tests for WhatsApp Staff Router
"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.wa_staff_router import WAStaffRouter


class TestParseInput:
    """Tests for _parse_input method"""

    def setup_method(self):
        self.router = WAStaffRouter()

    def test_parse_input_text(self):
        """Text message 'hola' → {type: 'text', text: 'hola'}"""
        payload = {'content': 'Hola', 'msg_type': 'text'}
        result = self.router._parse_input(payload)
        assert result['type'] == 'text'
        assert result['text'] == 'hola'  # lowercased
        assert result['raw'] == 'Hola'   # original preserved

    def test_parse_input_interactive(self):
        """Interactive reply → {type: 'interactive', id: '...'}"""
        payload = {
            'msg_type': 'interactive',
            'interactive_type': 'button_reply',
            'interactive_id': 'main_cases',
            'content': 'Mis Expedientes',
        }
        result = self.router._parse_input(payload)
        assert result['type'] == 'interactive'
        assert result['id'] == 'main_cases'
        assert result['interactive_type'] == 'button_reply'


class TestIsStaffPhone:
    """Tests for is_staff_phone method"""

    def setup_method(self):
        self.router = WAStaffRouter()

    @pytest.mark.asyncio
    async def test_is_staff_phone_none(self):
        """Non-registered phone → None"""
        tenant_id = uuid4()
        with patch('app.services.wa_staff_router.wa_repository') as mock_repo:
            mock_repo.get_staff_by_phone = AsyncMock(return_value=None)
            result = await self.router.is_staff_phone('5211111111', tenant_id)
            assert result is None
            mock_repo.get_staff_by_phone.assert_called_once_with(tenant_id, '5211111111')


class TestRouteMessage:
    """Tests for route_message method"""

    def setup_method(self):
        self.router = WAStaffRouter()

    @pytest.mark.asyncio
    async def test_route_message_non_staff(self):
        """Non-staff phone → returns False"""
        tenant_id = str(uuid4())
        with patch('app.services.wa_staff_router.wa_repository') as mock_repo:
            mock_repo.get_staff_by_phone = AsyncMock(return_value=None)
            result = await self.router.route_message(
                tenant_id=tenant_id,
                phone='5211111111',
                message_payload={'content': 'hola', 'msg_type': 'text'},
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_route_message_staff(self):
        """Staff phone → dispatches to handler, returns True"""
        tenant_id = str(uuid4())
        staff_record = {
            'id': str(uuid4()),
            'phone': '5299999999',
            'display_name': 'Test User',
            'role': 'asistente',
            'user_id': str(uuid4()),
            'session_state': {},
        }

        with patch('app.services.wa_staff_router.wa_repository') as mock_repo:
            mock_repo.get_staff_by_phone = AsyncMock(return_value=staff_record)
            mock_repo.log_command = AsyncMock()

            with patch('app.services.wa_menu_handlers.menu_handler') as mock_handler:
                mock_handler.handle = AsyncMock()

                result = await self.router.route_message(
                    tenant_id=tenant_id,
                    phone='5299999999',
                    message_payload={'content': 'menu', 'msg_type': 'text'},
                )

                assert result is True
                mock_handler.handle.assert_called_once()
                mock_repo.log_command.assert_called_once()
