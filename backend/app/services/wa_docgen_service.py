"""
ControlNot v2 - WhatsApp Document Generation Service
Orchestrates document generation from WhatsApp: download images, extract data, generate .docx, send.
"""
import base64
import json
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import structlog

from app.services.whatsapp_service import whatsapp_service

logger = structlog.get_logger()

# Claude Sonnet for lightweight image evaluation
EVAL_MODEL = "claude-sonnet-4-20250514"

# Document types supported
DOC_TYPES = {
    'compraventa': 'Compraventa',
    'donacion': 'Donacion',
    'testamento': 'Testamento',
    'poder': 'Poder',
    'sociedad': 'Sociedad',
    'cancelacion': 'Cancelacion de Hipoteca',
}


class WADocgenService:
    """Orchestrates document generation flow triggered from WhatsApp."""

    async def download_and_preprocess_images(
        self, media_ids: List[str]
    ) -> List[Dict]:
        """Download images from Meta and preprocess them for Claude Vision.

        Returns list of dicts with keys: content (base64), media_type, source_type.
        """
        from app.services.image_preprocessing_service import ImagePreprocessingService
        preprocessor = ImagePreprocessingService()

        images = []
        for media_id in media_ids:
            try:
                result = await whatsapp_service.download_media(media_id)
                if not result:
                    logger.warning("wa_docgen_download_failed", media_id=media_id)
                    continue

                content_bytes, mime_type = result

                # Preprocess image
                processed_bytes, processed_type = preprocessor.preprocess(
                    content_bytes, filename=f"wa_{media_id}"
                )

                # Encode to base64 for Claude Vision
                b64 = base64.b64encode(processed_bytes).decode('utf-8')
                images.append({
                    'name': f'wa_{media_id}',
                    'content': b64,
                    'media_type': processed_type or mime_type,
                    'source_type': 'base64',
                })
            except Exception as e:
                logger.error("wa_docgen_preprocess_error", media_id=media_id, error=str(e))

        return images

    async def extract_from_images(
        self,
        images: List[Dict],
        doc_type: str,
        tenant_id: UUID,
    ) -> Dict[str, str]:
        """Extract data from images using Claude Vision and inject notary profile.

        Returns dict of {field_name: value}.
        """
        from app.services.anthropic_service import AnthropicExtractionService
        extraction_service = AnthropicExtractionService()

        extracted = extraction_service.extract_with_vision(
            images=images,
            document_type=doc_type,
        )

        # Inject notary profile data
        try:
            from app.api.endpoints.extraction import inject_notary_profile_data
            extracted = await inject_notary_profile_data(
                extracted_data=extracted,
                tenant_id=str(tenant_id),
                document_type=doc_type,
            )
        except Exception as e:
            logger.warning("wa_docgen_inject_profile_failed", error=str(e))

        return extracted

    async def get_templates_for_type(
        self, tenant_id: UUID, doc_type: str
    ) -> List[Dict]:
        """List available templates for a document type."""
        from app.services.supabase_storage_service import SupabaseStorageService
        storage = SupabaseStorageService()

        all_templates = storage.get_templates(tenant_id=str(tenant_id), include_public=True)

        # Filter by tipo_documento
        return [
            t for t in all_templates
            if t.get('document_type', '').lower() == doc_type.lower()
        ]

    async def get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """Get a single template record by ID."""
        try:
            from app.database import supabase_admin
            result = supabase_admin.table('templates').select('*').eq(
                'id', template_id
            ).single().execute()
            return result.data if result.data else None
        except Exception as e:
            logger.error("wa_docgen_get_template_failed", template_id=template_id, error=str(e))
            return None

    async def generate_and_store(
        self,
        tenant_id: UUID,
        template_id: str,
        extracted_data: Dict[str, str],
        doc_type: str,
        case_id: Optional[UUID] = None,
    ) -> Optional[Dict]:
        """Generate .docx from template + extracted data, store in Storage and DB.

        Returns the created document record or None on failure.
        """
        from app.services.supabase_storage_service import SupabaseStorageService
        from app.services.document_service import DocumentGenerator
        from app.repositories.document_repository import DocumentRepository

        storage = SupabaseStorageService()
        doc_repo = DocumentRepository()

        # 1. Get template record
        template = await self.get_template_by_id(template_id)
        if not template:
            logger.error("wa_docgen_template_not_found", template_id=template_id)
            return None

        storage_path = template.get('storage_path')
        if not storage_path:
            logger.error("wa_docgen_template_no_path", template_id=template_id)
            return None

        placeholders = template.get('placeholders', [])
        template_name = template.get('nombre', 'documento')

        # 2. Download template content
        template_content = storage.read_template(storage_path)

        # 3. Generate document
        generator = DocumentGenerator()
        output_filename = f"{doc_type}_{template_name}.docx"

        doc_bytes, stats = generator.generate_document(
            template_content=template_content,
            responses=extracted_data,
            placeholders=placeholders,
            output_filename=output_filename,
            doc_type=doc_type,
        )

        # 4. Store in Supabase Storage
        store_result = await storage.store_document(
            tenant_id=str(tenant_id),
            filename=output_filename,
            content=doc_bytes,
            metadata={'tipo_documento': doc_type, 'source': 'whatsapp'},
        )

        doc_storage_path = store_result.get('path', '')

        # 5. Create DB record
        document = await doc_repo.create_document(
            tenant_id=tenant_id,
            case_id=case_id,
            session_id=None,
            template_id=UUID(template_id),
            tipo_documento=doc_type,
            nombre_documento=output_filename,
            storage_path=doc_storage_path,
            extracted_data=extracted_data,
            metadata={
                'source': 'whatsapp',
                'generation_stats': stats,
            },
        )

        return document

    async def send_document_via_whatsapp(
        self,
        phone: str,
        storage_path: str,
        filename: str,
        caption: Optional[str] = None,
    ) -> bool:
        """Generate signed URL and send document via WhatsApp.

        Returns True if sent successfully.
        """
        from app.repositories.document_repository import DocumentRepository
        doc_repo = DocumentRepository()

        try:
            signed_url = await doc_repo.get_signed_url(storage_path)
            if not signed_url:
                logger.error("wa_docgen_signed_url_empty", storage_path=storage_path)
                return False

            result = await whatsapp_service.send_media(
                to_phone=phone,
                media_type='document',
                media_url=signed_url,
                caption=caption or f"Documento: {filename}",
                filename=filename,
            )
            return result is not None

        except Exception as e:
            logger.error("wa_docgen_send_failed", phone=phone, error=str(e))
            return False

    # ── Progressive image storage ──

    async def store_image_progressively(
        self, tenant_id: str, phone: str, media_id: str, image_index: int
    ) -> Optional[Dict]:
        """Download from Meta + store in Supabase Storage.

        Returns: {storage_path, content_bytes, mime_type} or None.
        """
        from app.services.supabase_storage_service import SupabaseStorageService

        try:
            result = await whatsapp_service.download_media(media_id)
            if not result:
                logger.warning("wa_docgen_progressive_download_failed", media_id=media_id)
                return None

            content_bytes, mime_type = result

            storage = SupabaseStorageService()
            storage_path = await storage.store_whatsapp_media(
                tenant_id=tenant_id,
                conversation_id=f"docgen_{phone}",
                msg_id=f"img_{image_index}_{media_id[:8]}",
                content=content_bytes,
                mime_type=mime_type,
            )

            logger.info(
                "wa_docgen_image_stored",
                phone=phone, image_index=image_index, storage_path=storage_path,
            )

            return {
                'storage_path': storage_path,
                'content_bytes': content_bytes,
                'mime_type': mime_type,
            }

        except Exception as e:
            logger.error("wa_docgen_store_progressive_error", media_id=media_id, error=str(e))
            return None

    async def load_stored_images(self, image_records: List[Dict]) -> List[Dict]:
        """Read images from Supabase storage paths, preprocess, return base64 for Claude."""
        from app.services.image_preprocessing_service import ImagePreprocessingService
        from app.services.supabase_storage_service import SupabaseStorageService

        preprocessor = ImagePreprocessingService()
        storage = SupabaseStorageService()
        images = []

        for record in image_records:
            try:
                path = record['storage_path']
                mime_type = record.get('mime_type', 'image/jpeg')

                content = storage.read_stored_file(path)
                if not content:
                    logger.warning("wa_docgen_load_stored_empty", path=path)
                    continue

                processed_bytes, processed_type = preprocessor.preprocess(
                    content, filename=path.split('/')[-1]
                )

                b64 = base64.b64encode(processed_bytes).decode('utf-8')
                images.append({
                    'name': path.split('/')[-1],
                    'content': b64,
                    'media_type': processed_type or mime_type,
                    'source_type': 'base64',
                    'category': record.get('category'),
                })
            except Exception as e:
                logger.error("wa_docgen_load_stored_error", path=record.get('storage_path'), error=str(e))

        return images

    # ── Quick image evaluation ──

    async def evaluate_image_quick(
        self, image_bytes: bytes, mime_type: str, doc_type: str
    ) -> Dict:
        """Lightweight Claude Vision call (~200 tokens) to classify one image.

        Returns: {readable, document_type, quality, fields_contributed}
        """
        try:
            import anthropic
            from app.core.config import settings

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            b64 = base64.b64encode(image_bytes).decode('utf-8')
            media = mime_type if mime_type in ('image/jpeg', 'image/png', 'image/webp', 'image/gif') else 'image/jpeg'

            response = client.messages.create(
                model=EVAL_MODEL,
                max_tokens=256,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": media, "data": b64},
                        },
                        {
                            "type": "text",
                            "text": (
                                "Eres un clasificador de documentos notariales mexicanos. "
                                "Dada la imagen, responde SOLO con JSON valido (sin markdown):\n"
                                '{"document_type": "<INE|Constancia SAT|Escritura|Avaluo|Boleta RPP|Certificado Catastral|Otro>", '
                                '"readable": "<si|no|parcial>", '
                                '"quality": "<Buena|Regular|Mala>", '
                                '"fields_contributed": ["campo1", "campo2", "campo3"]}\n'
                                "fields_contributed: 3-5 campos clave visibles en el documento."
                            ),
                        },
                    ],
                }],
            )

            text = response.content[0].text.strip()
            # Parse JSON - handle potential markdown wrapping
            if text.startswith('```'):
                text = text.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
            result = json.loads(text)

            return {
                'readable': result.get('readable', 'unknown'),
                'document_type': result.get('document_type', 'No evaluado'),
                'quality': result.get('quality', '?'),
                'fields_contributed': result.get('fields_contributed', []),
            }

        except Exception as e:
            logger.warning("wa_docgen_evaluate_quick_failed", error=str(e))
            return {
                'readable': 'unknown',
                'document_type': 'No evaluado',
                'quality': '?',
                'fields_contributed': [],
            }

    # ── Field sources from Pydantic models ──

    def get_field_sources(self, document_type: str) -> Dict[str, str]:
        """Read 'source' from json_schema_extra of each model field.

        Returns: {field_name: source_label}
        """
        from app.services.anthropic_service import AnthropicExtractionService

        model_class = AnthropicExtractionService.MODEL_MAP.get(document_type)
        if not model_class:
            return {}

        sources = {}
        for field_name, field_info in model_class.model_fields.items():
            extra = field_info.json_schema_extra or {}
            source = extra.get('source', '')
            if source:
                sources[field_name] = source

        return sources

    # ── Category labels for guided wizard ──

    def get_category_labels(self, doc_type: str) -> Optional[Dict[str, str]]:
        """Returns CATEGORY_LABELS for doc_type, or None if no categories defined."""
        from app.services.anthropic_service import CATEGORY_LABELS
        return CATEGORY_LABELS.get(doc_type)

    # ── Merge extracted data ──

    def merge_extracted_data(self, existing: Dict, new_data: Dict) -> Dict:
        """Merge new extraction into existing.

        Rules:
        - New field not in existing -> add
        - Existing is "NO ENCONTRADO" and new has value -> replace
        - Both have values -> keep existing (first extraction wins)
        """
        merged = dict(existing)

        for key, new_val in new_data.items():
            if key not in merged:
                merged[key] = new_val
            elif "NO ENCONTRADO" in str(merged[key]) and "NO ENCONTRADO" not in str(new_val):
                merged[key] = new_val

        return merged


# Singleton
wa_docgen_service = WADocgenService()
