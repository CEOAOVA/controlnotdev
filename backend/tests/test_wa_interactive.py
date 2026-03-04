"""
Tests for WhatsApp Interactive Message Payloads
Verifies correct JSON structure for Meta Cloud API
"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.whatsapp_service import WhatsAppService


class TestSendButtons:
    """Tests for send_interactive_buttons payload structure"""

    def setup_method(self):
        self.service = WhatsAppService()
        # Pre-configure to avoid lazy-load
        self.service._api_url = 'https://graph.facebook.com/v18.0'
        self.service._phone_id = 'test_phone_id'
        self.service._access_token = 'test_token'
        self.service._verify_token = 'test_verify'

    @pytest.mark.asyncio
    async def test_send_buttons_payload_structure(self):
        """Verifies correct JSON structure for Meta API buttons"""
        captured_payload = {}

        async def mock_post(url, json=None, headers=None, timeout=None):
            captured_payload.update(json)
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json.return_value = {'messages': [{'id': 'msg_123'}]}
            return mock_resp

        with patch('httpx.AsyncClient') as MockClient:
            instance = AsyncMock()
            instance.post = mock_post
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = instance

            await self.service.send_interactive_buttons(
                to_phone='5211111111',
                body_text='Test body',
                buttons=[
                    {'id': 'btn_1', 'title': 'Button 1'},
                    {'id': 'btn_2', 'title': 'Button 2'},
                ],
                header='Test Header',
            )

        assert captured_payload['messaging_product'] == 'whatsapp'
        assert captured_payload['type'] == 'interactive'
        interactive = captured_payload['interactive']
        assert interactive['type'] == 'button'
        assert interactive['body']['text'] == 'Test body'
        assert interactive['header']['type'] == 'text'
        assert interactive['header']['text'] == 'Test Header'

        action_buttons = interactive['action']['buttons']
        assert len(action_buttons) == 2
        assert action_buttons[0]['type'] == 'reply'
        assert action_buttons[0]['reply']['id'] == 'btn_1'

    @pytest.mark.asyncio
    async def test_send_buttons_max_3(self):
        """Only 3 buttons even if 5 are passed"""
        captured_payload = {}

        async def mock_post(url, json=None, headers=None, timeout=None):
            captured_payload.update(json)
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json.return_value = {'messages': [{'id': 'msg_123'}]}
            return mock_resp

        with patch('httpx.AsyncClient') as MockClient:
            instance = AsyncMock()
            instance.post = mock_post
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = instance

            buttons = [{'id': f'b{i}', 'title': f'Btn {i}'} for i in range(5)]
            await self.service.send_interactive_buttons(
                to_phone='5211111111',
                body_text='Test',
                buttons=buttons,
            )

        action_buttons = captured_payload['interactive']['action']['buttons']
        assert len(action_buttons) == 3

    @pytest.mark.asyncio
    async def test_send_buttons_title_truncation(self):
        """Title > 20 chars gets truncated"""
        captured_payload = {}

        async def mock_post(url, json=None, headers=None, timeout=None):
            captured_payload.update(json)
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json.return_value = {'messages': [{'id': 'msg_123'}]}
            return mock_resp

        with patch('httpx.AsyncClient') as MockClient:
            instance = AsyncMock()
            instance.post = mock_post
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = instance

            long_title = 'A' * 30  # 30 chars
            await self.service.send_interactive_buttons(
                to_phone='5211111111',
                body_text='Test',
                buttons=[{'id': 'b1', 'title': long_title}],
            )

        btn_title = captured_payload['interactive']['action']['buttons'][0]['reply']['title']
        assert len(btn_title) <= 20


class TestSendList:
    """Tests for send_interactive_list payload structure"""

    def setup_method(self):
        self.service = WhatsAppService()
        self.service._api_url = 'https://graph.facebook.com/v18.0'
        self.service._phone_id = 'test_phone_id'
        self.service._access_token = 'test_token'
        self.service._verify_token = 'test_verify'

    @pytest.mark.asyncio
    async def test_send_list_payload_structure(self):
        """Verifies correct JSON structure for Meta API list"""
        captured_payload = {}

        async def mock_post(url, json=None, headers=None, timeout=None):
            captured_payload.update(json)
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json.return_value = {'messages': [{'id': 'msg_123'}]}
            return mock_resp

        with patch('httpx.AsyncClient') as MockClient:
            instance = AsyncMock()
            instance.post = mock_post
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = instance

            await self.service.send_interactive_list(
                to_phone='5211111111',
                body_text='Select an option:',
                button_text='View options',
                sections=[{
                    'title': 'Section 1',
                    'rows': [
                        {'id': 'row_1', 'title': 'Row 1', 'description': 'Desc 1'},
                    ],
                }],
                header='Header',
                footer='Footer text',
            )

        assert captured_payload['messaging_product'] == 'whatsapp'
        assert captured_payload['type'] == 'interactive'
        interactive = captured_payload['interactive']
        assert interactive['type'] == 'list'
        assert interactive['body']['text'] == 'Select an option:'
        assert interactive['action']['button'] == 'View options'
        assert len(interactive['action']['sections']) == 1
        assert interactive['header']['text'] == 'Header'
        assert interactive['footer']['text'] == 'Footer text'

    @pytest.mark.asyncio
    async def test_send_list_button_text_truncation(self):
        """button_text > 20 chars gets truncated"""
        captured_payload = {}

        async def mock_post(url, json=None, headers=None, timeout=None):
            captured_payload.update(json)
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json.return_value = {'messages': [{'id': 'msg_123'}]}
            return mock_resp

        with patch('httpx.AsyncClient') as MockClient:
            instance = AsyncMock()
            instance.post = mock_post
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = instance

            long_button = 'B' * 30
            await self.service.send_interactive_list(
                to_phone='5211111111',
                body_text='Test',
                button_text=long_button,
                sections=[{'title': 'S', 'rows': [{'id': 'r1', 'title': 'R1'}]}],
            )

        action_button = captured_payload['interactive']['action']['button']
        assert len(action_button) <= 20
