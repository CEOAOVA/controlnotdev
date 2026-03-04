"""
ControlNot v2 - WhatsApp Document Pipeline
Process documents received via WhatsApp: download → preprocess → extract → save
"""
from typing import Any, Dict, Optional
from uuid import UUID
import structlog

logger = structlog.get_logger()


class WADocumentPipeline:
    """
    Pipeline for processing documents sent via WhatsApp.

    When a client sends an image/document in a conversation linked to a case:
    1. Download media from Meta
    2. Determine document_type from the linked case
    3. Preprocess image (WhatsApp-optimized settings)
    4. Extract data with Claude Vision
    5. Save extracted data linked to the case
    6. Send confirmation message in the conversation
    """

    async def process_media_message(
        self,
        tenant_id: UUID,
        conversation_id: UUID,
        message_id: UUID,
        media_id: str,
        media_type: str,
        case_id: Optional[UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Process an incoming media message through the extraction pipeline.

        Returns extraction result dict or None if not applicable.
        """
        if not case_id:
            logger.debug("wa_pipeline_no_case", conversation_id=str(conversation_id))
            return None

        if media_type not in ('image', 'document'):
            logger.debug("wa_pipeline_unsupported_type", media_type=media_type)
            return None

        try:
            # 1. Download media
            from app.services.whatsapp_service import whatsapp_service
            media_bytes = await whatsapp_service.download_media(media_id)
            if not media_bytes:
                logger.warning("wa_pipeline_download_failed", media_id=media_id)
                return None

            # 2. Determine document type from case
            from app.database import get_supabase_admin_client
            client = get_supabase_admin_client()
            case_result = client.table('cases')\
                .select('document_type, tipo_documento')\
                .eq('id', str(case_id))\
                .limit(1)\
                .execute()

            if not case_result.data:
                logger.warning("wa_pipeline_case_not_found", case_id=str(case_id))
                return None

            document_type = (
                case_result.data[0].get('document_type')
                or case_result.data[0].get('tipo_documento')
                or 'ine_ife'
            )

            # 3. Preprocess image
            from app.services.image_preprocessing_service import get_image_preprocessing_service
            preprocessing_service = get_image_preprocessing_service()
            processed_content, media_mime_type = preprocessing_service.preprocess(
                media_bytes, f"whatsapp_media.jpg"
            )

            # 4. Extract with Claude Vision
            from app.services.anthropic_service import AnthropicExtractionService
            anthropic_service = AnthropicExtractionService()

            images = [{
                'name': 'whatsapp_document',
                'content': processed_content,
                'category': 'parte_a',
                'media_type': media_mime_type,
            }]

            extracted_data = anthropic_service.extract_with_vision(
                images=images,
                document_type=document_type,
            )

            fields_count = len([v for v in extracted_data.values() if v and v != '**[NO ENCONTRADO]**'])

            # 5. Save to wa_document_extractions
            extraction_record = client.table('wa_document_extractions').insert({
                'tenant_id': str(tenant_id),
                'message_id': str(message_id),
                'case_id': str(case_id),
                'document_type': document_type,
                'extracted_data': extracted_data,
                'confidence': 0.0,
                'status': 'completed',
            }).execute()

            # 6. Send confirmation message in conversation
            from app.repositories.wa_repository import wa_repository
            await wa_repository.create_message(
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                content=f"Documento procesado. {fields_count} campos extraidos.",
                sender_type='system',
                message_type='text',
            )

            logger.info(
                "wa_pipeline_completed",
                case_id=str(case_id),
                document_type=document_type,
                fields_extracted=fields_count,
            )

            return {
                'document_type': document_type,
                'extracted_data': extracted_data,
                'fields_count': fields_count,
                'extraction_id': extraction_record.data[0]['id'] if extraction_record.data else None,
            }

        except Exception as e:
            logger.error(
                "wa_pipeline_failed",
                conversation_id=str(conversation_id),
                media_id=media_id,
                error=str(e),
            )

            # Record failure
            try:
                from app.database import get_supabase_admin_client
                client = get_supabase_admin_client()
                client.table('wa_document_extractions').insert({
                    'tenant_id': str(tenant_id),
                    'message_id': str(message_id),
                    'case_id': str(case_id) if case_id else None,
                    'document_type': None,
                    'extracted_data': {},
                    'status': 'failed',
                }).execute()
            except Exception:
                pass

            return None


# Singleton
wa_document_pipeline = WADocumentPipeline()
