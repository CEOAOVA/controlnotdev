"""
ControlNot v2 - WhatsApp Endpoints
Webhook, conversations, messages, templates
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
import structlog

from app.repositories.wa_repository import wa_repository
from app.services.whatsapp_service import whatsapp_service
from app.database import get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


# === Schemas ===

class SendMessageRequest(BaseModel):
    conversation_id: str = Field(..., description="UUID de la conversacion")
    content: str = Field(..., min_length=1, description="Contenido del mensaje")
    message_type: str = Field('text', description="text|image|document")


class SendTemplateRequest(BaseModel):
    phone: str = Field(..., description="Numero de telefono con codigo de pais")
    template_name: str = Field(..., description="Nombre del template")
    language: str = Field('es', description="Codigo de idioma")
    components: Optional[list] = None


class LinkContactRequest(BaseModel):
    contact_id: str = Field(..., description="UUID del contacto WA")
    client_id: str = Field(..., description="UUID del cliente")


# === Webhook (public - no auth) ===

@router.get("/webhook")
async def verify_webhook(
    request: Request,
):
    """Meta webhook verification endpoint"""
    mode = request.query_params.get('hub.mode', '')
    token = request.query_params.get('hub.verify_token', '')
    challenge = request.query_params.get('hub.challenge', '')

    result = whatsapp_service.verify_webhook(mode, token, challenge)
    if result:
        return PlainTextResponse(content=result)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_webhook(request: Request):
    """Receive incoming WhatsApp messages from Meta"""
    try:
        body = await request.json()
        logger.info("whatsapp_webhook_received", body_keys=list(body.keys()))

        # Process incoming messages
        entries = body.get('entry', [])
        for entry in entries:
            changes = entry.get('changes', [])
            for change in changes:
                value = change.get('value', {})
                messages = value.get('messages', [])
                for msg in messages:
                    phone = msg.get('from', '')
                    text = msg.get('text', {}).get('body', '')
                    msg_id = msg.get('id', '')
                    logger.info("whatsapp_message_received", phone=phone, msg_id=msg_id)

        return {"status": "ok"}
    except Exception as e:
        logger.error("whatsapp_webhook_error", error=str(e))
        return {"status": "error"}


# === Conversations (authenticated) ===

@router.get("/conversations")
async def list_conversations(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List WhatsApp conversations"""
    try:
        conversations = await wa_repository.list_conversations(
            tenant_id=UUID(tenant_id),
            status=status,
            limit=limit,
            offset=offset,
        )
        return {'conversations': conversations}
    except Exception as e:
        logger.error("wa_list_conversations_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener conversaciones")


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get message history for a conversation"""
    try:
        messages = await wa_repository.list_messages(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset,
        )
        return {'messages': messages}
    except Exception as e:
        logger.error("wa_get_messages_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener mensajes")


# === Send Messages ===

@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Send a text message in a conversation"""
    try:
        # Get conversation to find contact phone
        conversations = await wa_repository.list_conversations(
            tenant_id=UUID(tenant_id)
        )
        conversation = next(
            (c for c in conversations if c['id'] == request.conversation_id),
            None
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversacion no encontrada")

        contact = conversation.get('wa_contacts')
        if not contact or not contact.get('phone'):
            raise HTTPException(status_code=400, detail="Contacto sin telefono")

        # Send via WhatsApp API
        result = await whatsapp_service.send_text(
            to_phone=contact['phone'],
            message=request.content,
        )

        # Record message
        wa_msg_id = None
        if result:
            wa_msg_id = result.get('messages', [{}])[0].get('id')

        message = await wa_repository.create_message(
            tenant_id=UUID(tenant_id),
            conversation_id=UUID(request.conversation_id),
            content=request.content,
            sender_type='agent',
            message_type=request.message_type,
            whatsapp_message_id=wa_msg_id,
            status='sent' if result else 'failed',
        )

        return {"message": "Mensaje enviado", "data": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_send_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al enviar mensaje")


@router.post("/send-template")
async def send_template(
    request: SendTemplateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Send a template message"""
    try:
        result = await whatsapp_service.send_template(
            to_phone=request.phone,
            template_name=request.template_name,
            language=request.language,
            components=request.components,
        )

        if not result:
            raise HTTPException(status_code=500, detail="Error al enviar template")

        return {"message": "Template enviado", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_send_template_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al enviar template")


# === Templates ===

@router.get("/templates")
async def list_templates(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List available WhatsApp templates"""
    try:
        templates = await wa_repository.list_templates(UUID(tenant_id))
        return {'templates': templates}
    except Exception as e:
        logger.error("wa_list_templates_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener templates")


# === Contact Linking ===

@router.post("/contacts/link")
async def link_contact(
    request: LinkContactRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Link a WhatsApp contact to a client"""
    try:
        result = await wa_repository.link_contact_to_client(
            contact_id=UUID(request.contact_id),
            client_id=UUID(request.client_id),
        )
        if not result:
            raise HTTPException(status_code=404, detail="Contacto no encontrado")

        return {"message": "Contacto vinculado", "contact": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_link_contact_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al vincular contacto")
