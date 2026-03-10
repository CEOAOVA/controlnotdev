"""
Tests for WhatsApp Client AI Service
Verifies generate_reply, guardrails, message building, and truncation.
"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.wa_client_ai_service import WAClientAIService, SYSTEM_PROMPT, MAX_RESPONSE_CHARS


TENANT_UUID = UUID('a0000000-0000-0000-0000-000000000001')


class TestGenerateReply:
    """Tests for WAClientAIService.generate_reply()"""

    def setup_method(self):
        self.service = WAClientAIService()

    @pytest.mark.asyncio
    async def test_returns_reply_from_claude(self):
        """Should return Claude's response text"""
        mock_block = MagicMock()
        mock_block.text = "Hola, con gusto le ayudo."

        mock_response = MagicMock()
        mock_response.content = [mock_block]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        self.service._client = mock_client

        result = await self.service.generate_reply(
            tenant_id=TENANT_UUID,
            phone='5215512345678',
            message_text='Hola, necesito informacion',
        )

        assert result == "Hola, con gusto le ayudo."
        mock_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_truncates_long_response(self):
        """Should truncate responses exceeding MAX_RESPONSE_CHARS"""
        long_text = "A" * 200 + ". " + "B" * 200

        mock_block = MagicMock()
        mock_block.text = long_text

        mock_response = MagicMock()
        mock_response.content = [mock_block]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        self.service._client = mock_client

        result = await self.service.generate_reply(
            tenant_id=TENANT_UUID,
            phone='5215512345678',
            message_text='Test',
        )

        assert len(result) <= MAX_RESPONSE_CHARS

    @pytest.mark.asyncio
    async def test_returns_none_on_api_error(self):
        """Should return None when Claude API fails"""
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))
        self.service._client = mock_client

        result = await self.service.generate_reply(
            tenant_id=TENANT_UUID,
            phone='5215512345678',
            message_text='Hola',
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_empty_response(self):
        """Should return None when Claude returns empty content"""
        mock_response = MagicMock()
        mock_response.content = []

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        self.service._client = mock_client

        result = await self.service.generate_reply(
            tenant_id=TENANT_UUID,
            phone='5215512345678',
            message_text='Hola',
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_includes_case_context(self):
        """Should include case context in system prompt when client is linked"""
        mock_block = MagicMock()
        mock_block.text = "Su expediente esta en revision."

        mock_response = MagicMock()
        mock_response.content = [mock_block]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        self.service._client = mock_client

        # Mock _get_case_context
        with patch.object(self.service, '_get_case_context', new_callable=AsyncMock) as mock_ctx:
            mock_ctx.return_value = "- Expediente EXP-001 (compraventa): En revision"

            await self.service.generate_reply(
                tenant_id=TENANT_UUID,
                phone='5215512345678',
                message_text='Como va mi tramite?',
                client_id='client-123',
            )

            # Verify system prompt includes case context
            call_kwargs = mock_client.messages.create.call_args.kwargs
            assert 'Expediente EXP-001' in call_kwargs['system']


class TestBuildMessages:
    """Tests for _build_messages helper"""

    def setup_method(self):
        self.service = WAClientAIService()

    def test_single_message(self):
        """Should return single user message"""
        result = self.service._build_messages("Hola")
        assert result == [{"role": "user", "content": "Hola"}]

    def test_builds_from_recent_messages(self):
        """Should build alternating user/assistant messages"""
        recent = [
            {'sender_type': 'client', 'content': 'Hola'},
            {'sender_type': 'bot', 'content': 'Buenos dias'},
            {'sender_type': 'client', 'content': 'Status?'},
        ]
        result = self.service._build_messages("Status?", recent)
        assert result[0]['role'] == 'user'
        assert result[-1]['role'] == 'user'
        assert result[-1]['content'] == 'Status?'

    def test_skips_empty_content(self):
        """Should skip messages with empty content"""
        recent = [
            {'sender_type': 'client', 'content': ''},
            {'sender_type': 'client', 'content': 'Hola'},
        ]
        result = self.service._build_messages("Hola", recent)
        assert len(result) == 1

    def test_ensures_starts_with_user(self):
        """Should strip leading assistant messages"""
        recent = [
            {'sender_type': 'bot', 'content': 'Bienvenido'},
            {'sender_type': 'client', 'content': 'Gracias'},
        ]
        result = self.service._build_messages("Gracias", recent)
        assert result[0]['role'] == 'user'


class TestGuardrails:
    """Verify system prompt contains guardrail rules"""

    def test_no_financial_data(self):
        assert 'montos' in SYSTEM_PROMPT.lower() or 'costos' in SYSTEM_PROMPT.lower()

    def test_no_sensitive_data(self):
        assert 'RFC' in SYSTEM_PROMPT or 'CURP' in SYSTEM_PROMPT

    def test_max_chars_defined(self):
        assert '300' in SYSTEM_PROMPT
