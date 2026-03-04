"""
ControlNot v2 - WhatsApp Endpoints
Webhook, conversations, messages, templates
"""
import hmac
import hashlib
import json
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request, BackgroundTasks
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


class SendDocumentRequest(BaseModel):
    conversation_id: str = Field(..., description="UUID de la conversacion")
    document_url: str = Field(..., description="URL publica del documento (Supabase Storage)")
    filename: str = Field(..., description="Nombre del archivo")
    caption: Optional[str] = Field(None, description="Texto de acompanamiento")


# === Helpers ===

def _get_default_tenant_id() -> Optional[str]:
    """Get the default tenant ID for webhook processing"""
    try:
        from app.core.config import settings
        return getattr(settings, 'DEFAULT_TENANT_ID', None)
    except Exception:
        return None


async def _resolve_tenant_id(phone_number_id: str) -> Optional[str]:
    """Resolve tenant: wa_phone_tenant_map lookup → fallback DEFAULT_TENANT_ID"""
    if phone_number_id:
        tenant = await wa_repository.get_tenant_by_phone_number_id(phone_number_id)
        if tenant:
            return tenant
    return _get_default_tenant_id()


async def _process_incoming_message(
    tenant_id: str,
    phone: str,
    msg_id: str,
    msg_type: str,
    content: str,
    media_id: Optional[str] = None,
    contact_name: Optional[str] = None,
    interactive_id: Optional[str] = None,
    interactive_type: Optional[str] = None,
):
    """Background task: process a single incoming WhatsApp message"""
    try:
        tid = UUID(tenant_id)

        # Check if this is a staff phone → route to staff menu
        from app.services.wa_staff_router import wa_staff_router
        handled = await wa_staff_router.route_message(
            tenant_id=tenant_id,
            phone=phone,
            message_payload={
                'content': content,
                'msg_type': msg_type,
                'interactive_id': interactive_id,
                'interactive_type': interactive_type,
            },
        )
        if handled:
            return

        # Client flow (unchanged)

        # Get or create contact
        contact = await wa_repository.get_or_create_contact(
            tenant_id=tid,
            phone=phone,
            name=contact_name,
        )

        # Get or create conversation
        conversation = await wa_repository.get_or_create_conversation(
            tenant_id=tid,
            contact_id=UUID(contact['id']),
        )

        # Save the message
        message = await wa_repository.create_message(
            tenant_id=tid,
            conversation_id=UUID(conversation['id']),
            content=content or f'[{msg_type}]',
            sender_type='client',
            message_type=msg_type if msg_type != 'interactive' else 'text',
            whatsapp_message_id=msg_id,
            media_url=None,
            status='delivered',
        )

        # Download and store media in Supabase Storage
        if media_id and message:
            try:
                media_result = await whatsapp_service.download_media(media_id)
                if media_result:
                    content_bytes, mime_type = media_result
                    from app.services.supabase_storage_service import SupabaseStorageService
                    storage_svc = SupabaseStorageService()
                    media_path = await storage_svc.store_whatsapp_media(
                        tenant_id=tenant_id,
                        conversation_id=str(conversation['id']),
                        msg_id=msg_id,
                        content=content_bytes,
                        mime_type=mime_type,
                    )
                    await wa_repository.update_message_media(UUID(message['id']), media_path)
                    logger.info("whatsapp_media_stored", msg_id=msg_id, media_path=media_path)
            except Exception as media_err:
                logger.error("whatsapp_media_store_failed", msg_id=msg_id, error=str(media_err))

        # Increment unread count
        await wa_repository.increment_unread(UUID(conversation['id']))

        logger.info(
            "whatsapp_message_processed",
            phone=phone,
            msg_id=msg_id,
            msg_type=msg_type,
            conversation_id=conversation['id'],
        )

    except Exception as e:
        logger.error(
            "whatsapp_message_processing_failed",
            phone=phone,
            msg_id=msg_id,
            error=str(e),
        )


async def _process_status_update(wa_msg_id: str, status: str):
    """Background task: update message delivery status"""
    try:
        await wa_repository.update_message_status(wa_msg_id, status)
        logger.debug("whatsapp_status_updated", wa_msg_id=wa_msg_id, status=status)
    except Exception as e:
        logger.warning("whatsapp_status_update_failed", wa_msg_id=wa_msg_id, error=str(e))


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
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receive incoming WhatsApp messages from Meta"""
    try:
        raw_body = await request.body()

        # Verify HMAC signature if WHATSAPP_WEBHOOK_SECRET is configured
        webhook_secret = None
        try:
            from app.core.config import settings
            webhook_secret = settings.WHATSAPP_WEBHOOK_SECRET
        except Exception:
            pass

        if webhook_secret:
            signature = request.headers.get('X-Hub-Signature-256', '')
            expected = 'sha256=' + hmac.new(
                webhook_secret.encode(), raw_body, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                logger.warning("whatsapp_webhook_invalid_signature")
                raise HTTPException(status_code=403, detail="Invalid signature")

        body = json.loads(raw_body)
        logger.info("whatsapp_webhook_received", body_keys=list(body.keys()))

        entries = body.get('entry', [])
        for entry in entries:
            changes = entry.get('changes', [])
            for change in changes:
                value = change.get('value', {})

                # Resolve tenant from phone_number_id (multi-tenant) or DEFAULT_TENANT_ID
                phone_number_id = value.get('metadata', {}).get('phone_number_id', '')
                tenant_id = await _resolve_tenant_id(phone_number_id)
                if not tenant_id:
                    logger.warning("whatsapp_webhook_no_tenant", phone_number_id=phone_number_id)
                    continue

                # Process incoming messages
                messages = value.get('messages', [])
                contacts_info = value.get('contacts', [])
                contact_name_map = {}
                for ci in contacts_info:
                    wa_id = ci.get('wa_id', '')
                    profile_name = ci.get('profile', {}).get('name', '')
                    if wa_id and profile_name:
                        contact_name_map[wa_id] = profile_name

                for msg in messages:
                    phone = msg.get('from', '')
                    msg_id = msg.get('id', '')
                    msg_type = msg.get('type', 'text')

                    # Extract content based on type
                    content = ''
                    media_id = None
                    interactive_id = None
                    interactive_type = None

                    if msg_type == 'text':
                        content = msg.get('text', {}).get('body', '')
                    elif msg_type == 'image':
                        media_id = msg.get('image', {}).get('id')
                        content = msg.get('image', {}).get('caption', '')
                    elif msg_type == 'document':
                        media_id = msg.get('document', {}).get('id')
                        content = msg.get('document', {}).get('filename', '')
                    elif msg_type == 'audio':
                        media_id = msg.get('audio', {}).get('id')
                        content = '[Audio]'
                    elif msg_type == 'interactive':
                        interactive = msg.get('interactive', {})
                        interactive_type = interactive.get('type', '')
                        reply_data = interactive.get(interactive_type, {})
                        interactive_id = reply_data.get('id', '')
                        content = reply_data.get('title', interactive_id)

                    contact_name = contact_name_map.get(phone)

                    background_tasks.add_task(
                        _process_incoming_message,
                        tenant_id=tenant_id,
                        phone=phone,
                        msg_id=msg_id,
                        msg_type=msg_type,
                        content=content,
                        media_id=media_id,
                        contact_name=contact_name,
                        interactive_id=interactive_id,
                        interactive_type=interactive_type,
                    )

                # Process status updates (delivered, read)
                statuses = value.get('statuses', [])
                for st in statuses:
                    wa_msg_id = st.get('id', '')
                    status = st.get('status', '')
                    if wa_msg_id and status in ('delivered', 'read', 'failed'):
                        background_tasks.add_task(
                            _process_status_update,
                            wa_msg_id=wa_msg_id,
                            status=status,
                        )

        return {"status": "ok"}
    except HTTPException:
        raise
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


# === Send Document ===

@router.post("/send-document")
async def send_document(
    request: SendDocumentRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Send a document (file) in a conversation via WhatsApp"""
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

        # Send document via WhatsApp
        result = await whatsapp_service.send_media(
            to_phone=contact['phone'],
            media_type='document',
            media_url=request.document_url,
            caption=request.caption,
            filename=request.filename,
        )

        # Record message
        wa_msg_id = None
        if result:
            wa_msg_id = result.get('messages', [{}])[0].get('id')

        message = await wa_repository.create_message(
            tenant_id=UUID(tenant_id),
            conversation_id=UUID(request.conversation_id),
            content=request.caption or request.filename,
            sender_type='agent',
            message_type='document',
            whatsapp_message_id=wa_msg_id,
            media_url=request.document_url,
            status='sent' if result else 'failed',
        )

        return {"message": "Documento enviado", "data": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_send_document_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al enviar documento")


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


# === Conversation Management ===

@router.put("/conversations/{conversation_id}/assign")
async def assign_conversation(
    conversation_id: UUID,
    agent_id: Optional[str] = None,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Assign an agent to a conversation"""
    try:
        result = await wa_repository.update_conversation(
            conversation_id=conversation_id,
            updates={'assigned_to': agent_id},
        )
        if not result:
            raise HTTPException(status_code=404, detail="Conversacion no encontrada")
        return {"message": "Agente asignado", "conversation": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_assign_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al asignar conversacion")


@router.put("/conversations/{conversation_id}/close")
async def close_conversation(
    conversation_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Close a conversation"""
    try:
        result = await wa_repository.update_conversation(
            conversation_id=conversation_id,
            updates={'status': 'closed'},
        )
        if not result:
            raise HTTPException(status_code=404, detail="Conversacion no encontrada")
        return {"message": "Conversacion cerrada", "conversation": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_close_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al cerrar conversacion")


@router.put("/conversations/{conversation_id}/read")
async def mark_conversation_read(
    conversation_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Mark a conversation as read (reset unread_count)"""
    try:
        result = await wa_repository.update_conversation(
            conversation_id=conversation_id,
            updates={'unread_count': 0},
        )
        if not result:
            raise HTTPException(status_code=404, detail="Conversacion no encontrada")
        return {"message": "Conversacion marcada como leida", "conversation": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_mark_read_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al marcar como leida")


# === AI Suggestions ===

@router.get("/conversations/{conversation_id}/suggest")
async def get_suggested_reply(
    conversation_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get AI-suggested reply for the last client message in a conversation"""
    try:
        from app.services.wa_ai_responder import wa_auto_responder

        # Get last few messages to find the latest client message
        messages = await wa_repository.list_messages(
            conversation_id=conversation_id,
            limit=5,
            offset=0,
        )

        # Find the most recent client message
        last_client_msg = None
        for msg in reversed(messages):
            if msg.get('sender_type') == 'client' and msg.get('message_type') == 'text':
                last_client_msg = msg
                break

        if not last_client_msg or not last_client_msg.get('content'):
            return {"suggestion": None}

        suggestion = wa_auto_responder.suggest_reply(last_client_msg['content'])
        return {"suggestion": suggestion}

    except Exception as e:
        logger.error("wa_suggest_failed", error=str(e))
        return {"suggestion": None}


# === Staff Phones CRUD ===

class StaffPhoneRequest(BaseModel):
    phone: str = Field(..., description="Numero de telefono con codigo de pais")
    display_name: str = Field(..., description="Nombre para mostrar")
    user_id: Optional[str] = Field(None, description="UUID del usuario vinculado")
    role: str = Field('asistente', description="notario|asistente|abogado|admin")


class StaffPhoneUpdateRequest(BaseModel):
    phone: Optional[str] = None
    display_name: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/staff-phones")
async def list_staff_phones(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List all registered staff phone numbers"""
    try:
        phones = await wa_repository.list_staff_phones(UUID(tenant_id))
        return {"staff_phones": phones}
    except Exception as e:
        logger.error("wa_list_staff_phones_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener telefonos de staff")


@router.post("/staff-phones")
async def create_staff_phone(
    request: StaffPhoneRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Register a new staff phone number"""
    try:
        phone = await wa_repository.create_staff_phone(
            tenant_id=UUID(tenant_id),
            phone=request.phone,
            display_name=request.display_name,
            user_id=UUID(request.user_id) if request.user_id else None,
            role=request.role,
        )
        return {"message": "Telefono de staff registrado", "staff_phone": phone}
    except Exception as e:
        logger.error("wa_create_staff_phone_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al registrar telefono de staff")


@router.put("/staff-phones/{staff_id}")
async def update_staff_phone(
    staff_id: UUID,
    request: StaffPhoneUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Update a staff phone record"""
    try:
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        if not updates:
            raise HTTPException(status_code=400, detail="No hay cambios")

        result = await wa_repository.update_staff_phone(staff_id, updates)
        if not result:
            raise HTTPException(status_code=404, detail="Telefono no encontrado")
        return {"message": "Telefono actualizado", "staff_phone": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_update_staff_phone_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar telefono")


@router.delete("/staff-phones/{staff_id}")
async def delete_staff_phone(
    staff_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Delete a staff phone record"""
    try:
        deleted = await wa_repository.delete_staff_phone(staff_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Telefono no encontrado")
        return {"message": "Telefono eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_delete_staff_phone_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al eliminar telefono")


# === Notification Rules CRUD ===

class NotificationRuleRequest(BaseModel):
    event_type: str = Field(..., description="Tipo de evento")
    is_active: bool = Field(True)
    notify_staff: bool = Field(False, description="Notificar a telefonos de staff")
    template_id: Optional[str] = None
    message_text: Optional[str] = None
    conditions: Optional[dict] = None


class NotificationRuleUpdateRequest(BaseModel):
    event_type: Optional[str] = None
    is_active: Optional[bool] = None
    notify_staff: Optional[bool] = None
    template_id: Optional[str] = None
    message_text: Optional[str] = None
    conditions: Optional[dict] = None


@router.get("/notification-rules")
async def list_notification_rules(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List all notification rules"""
    try:
        rules = await wa_repository.list_notification_rules(UUID(tenant_id))
        return {"notification_rules": rules}
    except Exception as e:
        logger.error("wa_list_rules_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener reglas")


@router.post("/notification-rules")
async def create_notification_rule(
    request: NotificationRuleRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Create a notification rule"""
    try:
        rule = await wa_repository.create_notification_rule(
            tenant_id=UUID(tenant_id),
            event_type=request.event_type,
            is_active=request.is_active,
            notify_staff=request.notify_staff,
            template_id=UUID(request.template_id) if request.template_id else None,
            message_text=request.message_text,
            conditions=request.conditions,
        )
        return {"message": "Regla creada", "notification_rule": rule}
    except Exception as e:
        logger.error("wa_create_rule_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al crear regla")


@router.put("/notification-rules/{rule_id}")
async def update_notification_rule(
    rule_id: UUID,
    request: NotificationRuleUpdateRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Update a notification rule"""
    try:
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        if not updates:
            raise HTTPException(status_code=400, detail="No hay cambios")

        result = await wa_repository.update_notification_rule(rule_id, updates)
        if not result:
            raise HTTPException(status_code=404, detail="Regla no encontrada")
        return {"message": "Regla actualizada", "notification_rule": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_update_rule_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar regla")


@router.delete("/notification-rules/{rule_id}")
async def delete_notification_rule(
    rule_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Delete a notification rule"""
    try:
        deleted = await wa_repository.delete_notification_rule(rule_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Regla no encontrada")
        return {"message": "Regla eliminada"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_delete_rule_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al eliminar regla")


# === Command Log ===

@router.get("/command-log")
async def list_command_log(
    staff_phone: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List staff command log entries"""
    try:
        logs = await wa_repository.list_command_log(
            tenant_id=UUID(tenant_id),
            limit=limit,
            offset=offset,
            staff_phone=staff_phone,
        )
        return {"command_log": logs}
    except Exception as e:
        logger.error("wa_list_command_log_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener log de comandos")


# === Daily Digest ===

@router.post("/daily-digest")
async def trigger_daily_digest(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Trigger a daily digest notification to all staff phones"""
    try:
        from app.services.wa_notification_service import wa_notification_service
        result = await wa_notification_service.send_daily_digest(UUID(tenant_id))
        return {"message": "Resumen diario enviado", "result": result}
    except Exception as e:
        logger.error("wa_daily_digest_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al enviar resumen diario")


# === Phone-Tenant Map CRUD (Multi-tenant routing) ===

class PhoneTenantMapRequest(BaseModel):
    phone_number_id: str = Field(..., description="Meta phone_number_id del WABA")
    tenant_id: str = Field(..., description="UUID del tenant a asociar")


@router.get("/phone-tenant-map")
async def list_phone_tenant_map(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List all phone_number_id → tenant mappings"""
    try:
        mappings = await wa_repository.list_phone_tenant_map()
        return {"phone_tenant_map": mappings}
    except Exception as e:
        logger.error("wa_list_phone_tenant_map_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al obtener mapeos")


@router.post("/phone-tenant-map")
async def create_phone_tenant_map(
    request: PhoneTenantMapRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Register a phone_number_id → tenant mapping"""
    try:
        mapping = await wa_repository.create_phone_tenant_map(
            phone_number_id=request.phone_number_id,
            tenant_id=request.tenant_id,
        )
        return {"message": "Mapeo creado", "mapping": mapping}
    except Exception as e:
        logger.error("wa_create_phone_tenant_map_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al crear mapeo")


@router.delete("/phone-tenant-map/{map_id}")
async def delete_phone_tenant_map(
    map_id: UUID,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Delete a phone-tenant mapping"""
    try:
        deleted = await wa_repository.delete_phone_tenant_map(map_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Mapeo no encontrado")
        return {"message": "Mapeo eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("wa_delete_phone_tenant_map_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error al eliminar mapeo")
