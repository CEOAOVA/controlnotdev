"""
ControlNot v2 - Supabase Storage Service
Gestión de almacenamiento en Supabase Storage buckets

Reemplaza DriveStorageService y LocalStorageService
"""
import time
from typing import List, Dict, Optional
import structlog
from datetime import datetime

from app.database import supabase_admin, get_supabase_admin_client, upload_to_storage, download_from_storage, get_tenant_storage_path

logger = structlog.get_logger()


class SupabaseStorageService:
    """
    Servicio de almacenamiento en Supabase Storage

    Maneja:
    - Listado de templates (.docx) desde bucket 'templates'
    - Upload/download de templates
    - Almacenamiento de documentos generados en bucket 'documentos'
    """

    TEMPLATES_BUCKET = "templates"
    DOCUMENTS_BUCKET = "documentos"

    def __init__(self, client=None):
        """
        Args:
            client: Cliente de Supabase (opcional)

        NOTA: Usamos admin client para bypassear RLS ya que el backend
        no tiene sesión de usuario autenticado (auth.uid() es NULL).
        La seguridad multi-tenant se maneja a nivel de aplicación.
        """
        self.client = client or get_supabase_admin_client()
        # Cliente admin para operaciones de escritura que bypasean RLS
        self.admin_client = supabase_admin

        logger.debug("SupabaseStorageService inicializado")

    def get_templates(self, tenant_id: Optional[str] = None, include_public: bool = True) -> List[Dict]:
        """
        Lista templates Word (.docx) desde tabla Supabase (incluye tipo_documento)

        Args:
            tenant_id: ID del tenant para filtrar templates propios
            include_public: Si incluir templates públicos (tenant_id = null)

        Returns:
            List[Dict]: Lista de templates con:
                - id: UUID del template
                - name: Nombre del archivo
                - document_type: Tipo de documento (compraventa, donacion, etc.)
                - source: "supabase"
                - storage_path: Path en storage
                - placeholders: Lista de placeholders
                - created_at: Fecha de creación

        Example:
            >>> templates = supabase_storage.get_templates(tenant_id="uuid-123")
            >>> templates[0]
            {
                'id': 'uuid-abc',
                'name': 'Compraventa_Template.docx',
                'document_type': 'compraventa',
                'source': 'supabase',
                'storage_path': 'uuid-123/Compraventa_Template.docx',
                'placeholders': ['vendedor', 'comprador', ...]
            }
        """
        start_time = time.time()
        logger.debug(
            "storage_get_templates_starting",
            tenant_id=tenant_id,
            include_public=include_public
        )

        try:
            templates = []

            # Leer desde la tabla 'templates' (tiene tipo_documento)
            try:
                db_start = time.time()
                if tenant_id and include_public:
                    # Templates del tenant + públicos (tenant_id es null)
                    # FILTRO: Solo templates con storage_path válido, ordenados por fecha desc
                    result = self.client.table('templates').select("*").or_(
                        f"tenant_id.eq.{tenant_id},tenant_id.is.null"
                    ).not_.is_('storage_path', 'null').order(
                        'created_at', desc=True
                    ).execute()
                elif tenant_id:
                    # Solo templates del tenant
                    result = self.client.table('templates').select("*").eq(
                        'tenant_id', tenant_id
                    ).not_.is_('storage_path', 'null').order(
                        'created_at', desc=True
                    ).execute()
                else:
                    # Solo templates públicos
                    result = self.client.table('templates').select("*").is_(
                        'tenant_id', 'null'
                    ).not_.is_('storage_path', 'null').order(
                        'created_at', desc=True
                    ).execute()

                db_duration = (time.time() - db_start) * 1000
                logger.debug(
                    "storage_get_templates_db_query_complete",
                    records_found=len(result.data) if result.data else 0,
                    duration_ms=round(db_duration, 2)
                )

                # Deduplicar por nombre: mantener solo el más reciente (ya ordenado por created_at DESC)
                seen_names = {}
                for record in result.data:
                    template_name = record.get('nombre', '')
                    # Si ya vimos este nombre, saltar (es una versión más vieja)
                    if template_name in seen_names:
                        continue
                    seen_names[template_name] = True

                    templates.append({
                        'id': str(record.get('id', '')),
                        'name': template_name,
                        'document_type': record.get('tipo_documento'),  # CLAVE: Incluir tipo
                        'source': 'supabase',
                        'storage_path': record.get('storage_path', ''),
                        'placeholders': record.get('placeholders', []),
                        'created_at': record.get('created_at'),
                        'modified': record.get('updated_at') or record.get('created_at'),
                        'size': 0,  # No disponible desde tabla
                        'path': record.get('storage_path', '')
                    })

            except Exception as e:
                db_duration = (time.time() - db_start) * 1000
                logger.warning(
                    "storage_get_templates_db_failed_fallback_to_storage",
                    error=str(e),
                    duration_ms=round(db_duration, 2)
                )
                # Fallback: intentar leer desde Storage (sin document_type)
                return self._get_templates_from_storage(tenant_id, include_public)

            total_duration = (time.time() - start_time) * 1000
            logger.info(
                "storage_get_templates_complete",
                tenant_id=tenant_id,
                include_public=include_public,
                total_templates=len(templates),
                duration_ms=round(total_duration, 2)
            )

            return templates

        except Exception as e:
            total_duration = (time.time() - start_time) * 1000
            logger.error(
                "storage_get_templates_failed",
                tenant_id=tenant_id,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(total_duration, 2)
            )
            raise

    def _get_templates_from_storage(self, tenant_id: Optional[str] = None, include_public: bool = True) -> List[Dict]:
        """
        Fallback: Lista templates desde Storage (sin document_type)
        """
        templates = []

        if include_public:
            try:
                public_files = self.client.storage.from_(self.TEMPLATES_BUCKET).list("public")
                for file in public_files:
                    if file.get('name', '').endswith('.docx'):
                        templates.append(self._format_template(file, "public"))
            except Exception as e:
                logger.warning("No se pudieron listar templates públicos", error=str(e))

        if tenant_id:
            try:
                tenant_files = self.client.storage.from_(self.TEMPLATES_BUCKET).list(tenant_id)
                for file in tenant_files:
                    if file.get('name', '').endswith('.docx'):
                        templates.append(self._format_template(file, tenant_id))
            except Exception as e:
                logger.warning("No se pudieron listar templates del tenant", tenant_id=tenant_id, error=str(e))

        return templates

    def _format_template(self, file: Dict, folder: str) -> Dict:
        """
        Formatea un archivo de Storage al formato estándar

        Args:
            file: Objeto de archivo de Supabase Storage
            folder: Carpeta donde está el archivo

        Returns:
            Dict: Template formateado
        """
        file_name = file.get('name', '')
        path = f"{folder}/{file_name}"

        return {
            'id': path,
            'name': file_name,
            'size': file.get('metadata', {}).get('size', 0) if file.get('metadata') else 0,
            'modified': file.get('updated_at') or file.get('created_at'),
            'source': 'supabase',
            'path': path,
            'folder': folder
        }

    def read_template(self, path: str) -> bytes:
        """
        Lee un template desde Supabase Storage

        Args:
            path: Path del template (ej: "public/template.docx" o "tenant-id/template.docx")

        Returns:
            bytes: Contenido del archivo

        Raises:
            Exception: Si falla la descarga
        """
        start_time = time.time()
        logger.debug(
            "storage_read_template_starting",
            bucket=self.TEMPLATES_BUCKET,
            path=path
        )

        try:
            content = self.client.storage.from_(self.TEMPLATES_BUCKET).download(path)
            duration_ms = (time.time() - start_time) * 1000

            logger.info(
                "storage_read_template_complete",
                path=path,
                size_bytes=len(content),
                duration_ms=round(duration_ms, 2)
            )

            return content

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "storage_read_template_failed",
                path=path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
            )
            raise

    async def save_template(
        self,
        file_name: str,
        content: bytes,
        tenant_id: Optional[str] = None,
        is_public: bool = False
    ) -> Dict:
        """
        Guarda un template en Supabase Storage

        Args:
            file_name: Nombre del archivo .docx
            content: Contenido del archivo
            tenant_id: ID del tenant (requerido si no es público)
            is_public: Si el template es público

        Returns:
            Dict: Información del archivo guardado

        Raises:
            ValueError: Si no se proporciona tenant_id para templates no públicos
            Exception: Si falla el upload
        """
        if not is_public and not tenant_id:
            raise ValueError("tenant_id es requerido para templates no públicos")

        folder = "public" if is_public else tenant_id
        path = f"{folder}/{file_name}"

        start_time = time.time()
        logger.debug(
            "storage_save_template_starting",
            bucket=self.TEMPLATES_BUCKET,
            path=path,
            size_bytes=len(content),
            is_public=is_public
        )

        try:
            result = await upload_to_storage(
                bucket=self.TEMPLATES_BUCKET,
                path=path,
                file_data=content,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            duration_ms = (time.time() - start_time) * 1000

            logger.info(
                "storage_save_template_complete",
                path=path,
                size_bytes=len(content),
                is_public=is_public,
                duration_ms=round(duration_ms, 2)
            )

            return {
                'id': path,
                'name': file_name,
                'path': path,
                'url': result.get('url'),
                'source': 'supabase'
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "storage_save_template_failed",
                path=path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
            )
            raise

    def delete_template(self, path: str) -> bool:
        """
        Elimina un template de Supabase Storage

        Args:
            path: Path del template a eliminar

        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            self.client.storage.from_(self.TEMPLATES_BUCKET).remove([path])

            logger.info(
                "Template eliminado de Supabase",
                path=path
            )

            return True

        except Exception as e:
            logger.error(
                "Error al eliminar template de Supabase",
                path=path,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    def get_template_by_name(
        self,
        template_name: str,
        tenant_id: Optional[str] = None,
        include_public: bool = True
    ) -> Optional[Dict]:
        """
        Busca un template por nombre

        Args:
            template_name: Nombre del archivo a buscar
            tenant_id: ID del tenant
            include_public: Si buscar en templates públicos

        Returns:
            Optional[Dict]: Template encontrado o None
        """
        templates = self.get_templates(tenant_id=tenant_id, include_public=include_public)

        for template in templates:
            if template['name'] == template_name:
                return template

        logger.warning(
            "Template no encontrado en Supabase",
            template_name=template_name,
            tenant_id=tenant_id
        )
        return None

    # ==========================================
    # MÉTODOS PARA DOCUMENTOS GENERADOS
    # ==========================================

    async def store_document(
        self,
        tenant_id: str,
        filename: str,
        content: bytes,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Guarda un documento generado en Supabase Storage

        Args:
            tenant_id: ID del tenant
            filename: Nombre del archivo
            content: Contenido del documento
            metadata: Metadata adicional (tipo_documento, etc.)

        Returns:
            Dict: Información del documento guardado
        """
        path = get_tenant_storage_path(tenant_id, "generated", filename)

        start_time = time.time()
        logger.debug(
            "storage_store_document_starting",
            bucket=self.DOCUMENTS_BUCKET,
            tenant_id=tenant_id,
            filename=filename,
            path=path,
            size_bytes=len(content)
        )

        try:
            result = await upload_to_storage(
                bucket=self.DOCUMENTS_BUCKET,
                path=path,
                file_data=content,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            duration_ms = (time.time() - start_time) * 1000

            logger.info(
                "storage_store_document_complete",
                tenant_id=tenant_id,
                filename=filename,
                path=path,
                size_bytes=len(content),
                duration_ms=round(duration_ms, 2)
            )

            return {
                'id': path,
                'name': filename,
                'path': path,
                'url': result.get('url'),
                'bucket': self.DOCUMENTS_BUCKET,
                'metadata': metadata,
                'stored_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "storage_store_document_failed",
                tenant_id=tenant_id,
                filename=filename,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
            )
            raise

    async def download_document(self, path: str, tenant_id: Optional[str] = None) -> bytes:
        """
        Descarga un documento desde Supabase Storage

        Args:
            path: Path del documento
            tenant_id: ID del tenant (opcional, para logging)

        Returns:
            bytes: Contenido del documento
        """
        start_time = time.time()
        logger.debug(
            "storage_download_document_starting",
            bucket=self.DOCUMENTS_BUCKET,
            tenant_id=tenant_id,
            path=path
        )

        try:
            content = await download_from_storage(
                bucket=self.DOCUMENTS_BUCKET,
                path=path
            )
            duration_ms = (time.time() - start_time) * 1000

            logger.info(
                "storage_download_document_complete",
                tenant_id=tenant_id,
                path=path,
                size_bytes=len(content),
                duration_ms=round(duration_ms, 2)
            )

            return content

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "storage_download_document_failed",
                tenant_id=tenant_id,
                path=path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
            )
            raise

    def get_document_url(self, path: str, expires_in: int = 3600) -> str:
        """
        Genera una URL firmada para descargar un documento

        Args:
            path: Path del documento
            expires_in: Tiempo de expiración en segundos (default: 1 hora)

        Returns:
            str: URL firmada para descarga
        """
        try:
            result = self.client.storage.from_(self.DOCUMENTS_BUCKET).create_signed_url(
                path=path,
                expires_in=expires_in
            )

            return result.get('signedURL') or result.get('signedUrl', '')

        except Exception as e:
            logger.error(
                "Error al generar URL firmada",
                path=path,
                error=str(e)
            )
            raise

    async def delete_document(self, path: str) -> bool:
        """
        Elimina un documento de Supabase Storage

        Args:
            path: Path del documento a eliminar

        Returns:
            bool: True si se eliminó exitosamente
        """
        start_time = time.time()
        logger.debug(
            "storage_delete_document_starting",
            bucket=self.DOCUMENTS_BUCKET,
            path=path
        )

        try:
            self.client.storage.from_(self.DOCUMENTS_BUCKET).remove([path])
            duration_ms = (time.time() - start_time) * 1000

            logger.info(
                "storage_delete_document_complete",
                path=path,
                duration_ms=round(duration_ms, 2)
            )

            return True

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "storage_delete_document_failed",
                path=path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
            )
            raise
