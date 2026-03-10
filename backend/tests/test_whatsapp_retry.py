"""
Tests for WhatsApp Service retry logic and rate limiting.
Verifies _send_with_retry handles 429, 5xx, timeouts, and success.
"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.whatsapp_service import WhatsAppService


def _mock_response(status_code: int, json_data=None):
    """Create a mock httpx.Response with given status code."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}

    if 400 <= status_code < 600:
        request = MagicMock()
        request.url = "https://example.com/messages"
        resp.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                f"{status_code}", request=request, response=resp
            )
        )
    else:
        resp.raise_for_status = MagicMock()

    return resp


def _setup_service():
    """Create a WhatsAppService with mocked config and HTTP client."""
    service = WhatsAppService()
    service._api_url = 'https://graph.facebook.com/v18.0'
    service._phone_id = 'test_phone_id'
    service._access_token = 'test_token'
    service._verify_token = 'test_verify'
    service._rate_limiter = MagicMock()
    service._rate_limiter.acquire = AsyncMock()

    mock_client = AsyncMock()
    # Prevent _get_http_client from creating a real httpx client
    service._get_http_client = lambda: mock_client
    return service, mock_client


class TestSendWithRetry:
    """Tests for _send_with_retry()"""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self):
        """Should return response on 200 without retry"""
        service, mock_client = _setup_service()
        mock_resp = _mock_response(200, {'messages': [{'id': 'msg_1'}]})
        mock_client.post = AsyncMock(return_value=mock_resp)

        result = await service._send_with_retry(
            'https://graph.facebook.com/v18.0/test/messages',
            {'messaging_product': 'whatsapp', 'to': '123'},
        )

        assert result.status_code == 200
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_retries_on_429(self):
        """Should retry on 429 (rate limited) then succeed"""
        service, mock_client = _setup_service()
        rate_limited = _mock_response(429)
        success = _mock_response(200)
        mock_client.post = AsyncMock(side_effect=[rate_limited, success])

        with patch('asyncio.sleep', new_callable=AsyncMock):
            result = await service._send_with_retry(
                'https://example.com/messages',
                {'test': True},
                max_retries=3,
            )

        assert result.status_code == 200
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_retries_on_500(self):
        """Should retry on 5xx server error then succeed"""
        service, mock_client = _setup_service()
        server_error = _mock_response(500)
        success = _mock_response(200)
        mock_client.post = AsyncMock(side_effect=[server_error, success])

        with patch('asyncio.sleep', new_callable=AsyncMock):
            result = await service._send_with_retry(
                'https://example.com/messages',
                {'test': True},
                max_retries=3,
            )

        assert result.status_code == 200
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self):
        """Should raise after exhausting all retries on persistent 429"""
        service, mock_client = _setup_service()
        rate_limited = _mock_response(429)
        mock_client.post = AsyncMock(return_value=rate_limited)

        with patch('asyncio.sleep', new_callable=AsyncMock):
            with pytest.raises(httpx.HTTPStatusError):
                await service._send_with_retry(
                    'https://example.com/messages',
                    {'test': True},
                    max_retries=3,
                )

        assert mock_client.post.call_count == 3

    @pytest.mark.asyncio
    async def test_retries_on_timeout(self):
        """Should retry on timeout then succeed"""
        service, mock_client = _setup_service()
        success = _mock_response(200)
        mock_client.post = AsyncMock(
            side_effect=[httpx.TimeoutException("timeout"), success]
        )

        with patch('asyncio.sleep', new_callable=AsyncMock):
            result = await service._send_with_retry(
                'https://example.com/messages',
                {'test': True},
                max_retries=3,
            )

        assert result.status_code == 200
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_does_not_retry_on_4xx(self):
        """Should NOT retry on client errors (400) — raise immediately"""
        service, mock_client = _setup_service()
        bad_request = _mock_response(400)
        mock_client.post = AsyncMock(return_value=bad_request)

        with pytest.raises(httpx.HTTPStatusError):
            await service._send_with_retry(
                'https://example.com/messages',
                {'test': True},
                max_retries=3,
            )

        mock_client.post.assert_called_once()
