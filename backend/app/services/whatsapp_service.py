"""
ControlNot v2 - WhatsApp Service
Meta Cloud API client for sending/receiving WhatsApp messages
"""
from typing import Any, Dict, Optional
import httpx
import structlog

logger = structlog.get_logger()


class WhatsAppService:
    """Client for Meta Cloud API (WhatsApp Business)"""

    def __init__(self):
        self._api_url: Optional[str] = None
        self._phone_id: Optional[str] = None
        self._access_token: Optional[str] = None
        self._verify_token: Optional[str] = None

    def _load_config(self):
        """Lazy load config to avoid import-time settings validation"""
        if self._api_url is not None:
            return

        try:
            from app.core.config import settings
            self._api_url = getattr(settings, 'WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0')
            self._phone_id = getattr(settings, 'WHATSAPP_PHONE_ID', '')
            self._access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
            self._verify_token = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', 'controlnot_verify')
        except Exception:
            self._api_url = 'https://graph.facebook.com/v18.0'
            self._phone_id = ''
            self._access_token = ''
            self._verify_token = 'controlnot_verify'

    @property
    def verify_token(self) -> str:
        self._load_config()
        return self._verify_token or 'controlnot_verify'

    async def send_text(
        self,
        to_phone: str,
        message: str,
    ) -> Optional[Dict[str, Any]]:
        """Send a text message via WhatsApp"""
        self._load_config()

        if not self._phone_id or not self._access_token:
            logger.warning("whatsapp_not_configured", message="WhatsApp API not configured")
            return None

        url = f"{self._api_url}/{self._phone_id}/messages"
        headers = {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json',
        }
        payload = {
            'messaging_product': 'whatsapp',
            'to': to_phone,
            'type': 'text',
            'text': {'body': message},
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                logger.info("whatsapp_text_sent", to=to_phone, message_id=data.get('messages', [{}])[0].get('id'))
                return data
        except Exception as e:
            logger.error("whatsapp_send_failed", to=to_phone, error=str(e))
            return None

    async def send_template(
        self,
        to_phone: str,
        template_name: str,
        language: str = 'es',
        components: Optional[list] = None,
    ) -> Optional[Dict[str, Any]]:
        """Send a template message via WhatsApp"""
        self._load_config()

        if not self._phone_id or not self._access_token:
            logger.warning("whatsapp_not_configured")
            return None

        url = f"{self._api_url}/{self._phone_id}/messages"
        headers = {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json',
        }
        template_data: Dict[str, Any] = {
            'name': template_name,
            'language': {'code': language},
        }
        if components:
            template_data['components'] = components

        payload = {
            'messaging_product': 'whatsapp',
            'to': to_phone,
            'type': 'template',
            'template': template_data,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                logger.info("whatsapp_template_sent", to=to_phone, template=template_name)
                return data
        except Exception as e:
            logger.error("whatsapp_template_send_failed", to=to_phone, error=str(e))
            return None

    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook subscription from Meta"""
        self._load_config()
        if mode == 'subscribe' and token == self.verify_token:
            logger.info("whatsapp_webhook_verified")
            return challenge
        logger.warning("whatsapp_webhook_verification_failed", mode=mode)
        return None


# Singleton
whatsapp_service = WhatsAppService()
