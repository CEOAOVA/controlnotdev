"""
ControlNot v2 - WhatsApp Service
Meta Cloud API client for sending/receiving WhatsApp messages
"""
from typing import Any, Dict, List, Optional
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
        self._waba_id: Optional[str] = None

    def _load_config(self):
        """Lazy load config to avoid import-time settings validation"""
        if self._api_url is not None:
            return

        try:
            from app.core.config import settings
            self._api_url = getattr(settings, 'WHATSAPP_API_URL', 'https://graph.facebook.com/v21.0')
            self._phone_id = getattr(settings, 'WHATSAPP_PHONE_ID', '')
            self._access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
            self._verify_token = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', 'controlnot_verify')
            self._waba_id = getattr(settings, 'WHATSAPP_BUSINESS_ACCOUNT_ID', '')
        except Exception:
            self._api_url = 'https://graph.facebook.com/v21.0'
            self._phone_id = ''
            self._access_token = ''
            self._verify_token = 'controlnot_verify'
            self._waba_id = ''

    @property
    def _headers(self) -> Dict[str, str]:
        self._load_config()
        return {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json',
        }

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
        payload = {
            'messaging_product': 'whatsapp',
            'to': to_phone,
            'type': 'text',
            'text': {'body': message},
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self._headers, timeout=30)
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
                response = await client.post(url, json=payload, headers=self._headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                logger.info("whatsapp_template_sent", to=to_phone, template=template_name)
                return data
        except Exception as e:
            logger.error("whatsapp_template_send_failed", to=to_phone, error=str(e))
            return None

    async def send_media(
        self,
        to_phone: str,
        media_type: str,
        media_url: str,
        caption: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a media message (image or document) via WhatsApp.

        Args:
            to_phone: Recipient phone number
            media_type: 'image' or 'document'
            media_url: Public URL of the media file (e.g. Supabase signed URL)
            caption: Optional caption text
            filename: Optional filename (for documents)
        """
        self._load_config()

        if not self._phone_id or not self._access_token:
            logger.warning("whatsapp_not_configured")
            return None

        url = f"{self._api_url}/{self._phone_id}/messages"

        media_obj: Dict[str, Any] = {'link': media_url}
        if caption:
            media_obj['caption'] = caption
        if filename and media_type == 'document':
            media_obj['filename'] = filename

        payload = {
            'messaging_product': 'whatsapp',
            'to': to_phone,
            'type': media_type,
            media_type: media_obj,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self._headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                logger.info(
                    "whatsapp_media_sent",
                    to=to_phone,
                    media_type=media_type,
                    message_id=data.get('messages', [{}])[0].get('id')
                )
                return data
        except Exception as e:
            logger.error("whatsapp_media_send_failed", to=to_phone, media_type=media_type, error=str(e))
            return None

    async def download_media(self, media_id: str) -> Optional[tuple]:
        """
        Download media from Meta API.

        Two-step process:
        1. GET media_id → get download URL + mime_type
        2. GET download URL → get actual bytes

        Returns:
            tuple[bytes, str] of (content, mime_type) or None on failure
        """
        self._load_config()

        if not self._access_token:
            return None

        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Get media URL + mime_type
                url_resp = await client.get(
                    f"{self._api_url}/{media_id}",
                    headers={'Authorization': f'Bearer {self._access_token}'},
                    timeout=30,
                )
                url_resp.raise_for_status()
                url_data = url_resp.json()
                media_url = url_data.get('url')
                mime_type = url_data.get('mime_type', 'application/octet-stream')

                if not media_url:
                    logger.warning("whatsapp_media_no_url", media_id=media_id)
                    return None

                # Step 2: Download actual file
                file_resp = await client.get(
                    media_url,
                    headers={'Authorization': f'Bearer {self._access_token}'},
                    timeout=60,
                )
                file_resp.raise_for_status()

                logger.info("whatsapp_media_downloaded", media_id=media_id, size=len(file_resp.content), mime_type=mime_type)
                return (file_resp.content, mime_type)

        except Exception as e:
            logger.error("whatsapp_media_download_failed", media_id=media_id, error=str(e))
            return None

    async def subscribe_waba(self) -> Dict[str, Any]:
        """Subscribe WABA to webhook so Meta actually sends message events."""
        self._load_config()

        if not self._waba_id:
            return {"success": False, "error": "WHATSAPP_BUSINESS_ACCOUNT_ID not configured"}
        if not self._access_token:
            return {"success": False, "error": "WHATSAPP_ACCESS_TOKEN not configured"}

        url = f"{self._api_url}/{self._waba_id}/subscribed_apps"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self._headers, timeout=30)
                data = response.json()
                logger.info("waba_subscribe_result", waba_id=self._waba_id, status=response.status_code, data=data)

                if response.status_code == 200 and data.get('success'):
                    return {"success": True, "data": data}
                else:
                    return {"success": False, "error": data.get('error', {}).get('message', str(data))}
        except Exception as e:
            logger.error("waba_subscribe_failed", waba_id=self._waba_id, error=str(e))
            return {"success": False, "error": str(e)}

    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook subscription from Meta"""
        self._load_config()
        if mode == 'subscribe' and token == self.verify_token:
            logger.info("whatsapp_webhook_verified")
            return challenge
        logger.warning("whatsapp_webhook_verification_failed", mode=mode)
        return None

    async def send_interactive_buttons(
        self,
        to_phone: str,
        body_text: str,
        buttons: List[Dict[str, str]],
        header: Optional[str] = None,
        footer: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send an interactive button message (max 3 buttons).

        Args:
            to_phone: Recipient phone number
            body_text: Main message body
            buttons: List of dicts with 'id' and 'title' (max 3, title max 20 chars)
            header: Optional header text
            footer: Optional footer text
        """
        self._load_config()
        if not self._phone_id or not self._access_token:
            logger.warning("whatsapp_not_configured")
            return None

        url = f"{self._api_url}/{self._phone_id}/messages"

        action_buttons = [
            {"type": "reply", "reply": {"id": b['id'], "title": b['title'][:20]}}
            for b in buttons[:3]
        ]

        interactive: Dict[str, Any] = {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": action_buttons},
        }
        if header:
            interactive["header"] = {"type": "text", "text": header}
        if footer:
            interactive["footer"] = {"text": footer}

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "interactive",
            "interactive": interactive,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self._headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                logger.info("whatsapp_buttons_sent", to=to_phone)
                return data
        except Exception as e:
            logger.error("whatsapp_buttons_send_failed", to=to_phone, error=str(e))
            return None

    async def send_interactive_list(
        self,
        to_phone: str,
        body_text: str,
        button_text: str,
        sections: List[Dict[str, Any]],
        header: Optional[str] = None,
        footer: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send an interactive list message (max 10 items total across sections).

        Args:
            to_phone: Recipient phone number
            body_text: Main message body
            button_text: Text on the list button (max 20 chars)
            sections: List of dicts with 'title' and 'rows' (each row has 'id', 'title', optional 'description')
            header: Optional header text
            footer: Optional footer text
        """
        self._load_config()
        if not self._phone_id or not self._access_token:
            logger.warning("whatsapp_not_configured")
            return None

        url = f"{self._api_url}/{self._phone_id}/messages"

        interactive: Dict[str, Any] = {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_text[:20],
                "sections": sections,
            },
        }
        if header:
            interactive["header"] = {"type": "text", "text": header}
        if footer:
            interactive["footer"] = {"text": footer}

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "interactive",
            "interactive": interactive,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self._headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                logger.info("whatsapp_list_sent", to=to_phone)
                return data
        except Exception as e:
            logger.error("whatsapp_list_send_failed", to=to_phone, error=str(e))
            return None

    @staticmethod
    def build_template_components(
        template_components: list,
        parameters: Dict[str, str],
    ) -> list:
        """
        Build template components array with interpolated parameter values.

        Args:
            template_components: Original template component definitions
            parameters: Dict of parameter name → value

        Returns:
            Components array ready for the Meta API
        """
        result = []
        for comp in template_components:
            comp_type = comp.get('type', '')
            if comp_type == 'body':
                params = []
                for param in comp.get('parameters', []):
                    param_key = param.get('key', '')
                    params.append({
                        'type': 'text',
                        'text': parameters.get(param_key, param.get('default', '')),
                    })
                result.append({
                    'type': 'body',
                    'parameters': params,
                })
            else:
                result.append(comp)
        return result


# Singleton
whatsapp_service = WhatsAppService()
