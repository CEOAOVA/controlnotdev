"""
ControlNot v2 - Uploaded File Repository
Repositorio para gestión de archivos subidos durante sesiones
"""
from typing import Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class UploadedFileRepository(BaseRepository):
    """
    Repositorio para la tabla 'uploaded_files'

    Gestiona metadata de archivos subidos (binarios en Supabase Storage)
    """

    def __init__(self):
        super().__init__('uploaded_files')

    async def create_uploaded_file(
        self,
        session_id: UUID,
        filename: str,
        storage_path: str,
        category: Optional[str] = None,
        original_filename: Optional[str] = None,
        file_hash: Optional[str] = None,
        content_type: Optional[str] = None,
        size_bytes: Optional[int] = None,
        storage_bucket: str = 'uploads'
    ) -> Optional[Dict]:
        """
        Registra un archivo subido

        Args:
            session_id: UUID de la sesión de procesamiento
            filename: Nombre del archivo en storage
            storage_path: Ruta completa en Supabase Storage
            category: Categoría (parte_a, parte_b, otros)
            original_filename: Nombre original del archivo
            file_hash: SHA-256 hash del archivo
            content_type: MIME type
            size_bytes: Tamaño en bytes
            storage_bucket: Bucket de Supabase Storage

        Returns:
            Archivo registrado
        """
        file_data = {
            'session_id': str(session_id),
            'filename': filename,
            'storage_path': storage_path,
            'storage_bucket': storage_bucket,
            'ocr_completed': False
        }

        if category:
            file_data['category'] = category
        if original_filename:
            file_data['original_filename'] = original_filename
        if file_hash:
            file_data['file_hash'] = file_hash
        if content_type:
            file_data['content_type'] = content_type
        if size_bytes is not None:
            file_data['size_bytes'] = size_bytes

        return await self.create(file_data)

    async def list_by_session(
        self,
        session_id: UUID,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Lista archivos de una sesión

        Args:
            session_id: UUID de la sesión
            category: Filtrar por categoría (opcional)

        Returns:
            Lista de archivos de la sesión
        """
        try:
            query = self._table()\
                .select('*')\
                .eq('session_id', str(session_id))

            if category:
                query = query.eq('category', category)

            result = query\
                .order('uploaded_at', desc=False)\
                .execute()

            return result.data if result.data else []

        except APIError as e:
            logger.error("uploaded_file_list_by_session_failed", session_id=str(session_id), error=str(e))
            raise

    async def update_ocr_result(
        self,
        file_id: UUID,
        ocr_text: str,
        ocr_confidence: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Actualiza resultado de OCR para un archivo

        Args:
            file_id: UUID del archivo
            ocr_text: Texto extraído por OCR
            ocr_confidence: Confianza del OCR (0.0 - 1.0)

        Returns:
            Archivo actualizado
        """
        from datetime import datetime, timezone

        updates = {
            'ocr_text': ocr_text,
            'ocr_completed': True,
            'processed_at': datetime.now(timezone.utc).isoformat()
        }

        if ocr_confidence is not None:
            updates['ocr_confidence'] = ocr_confidence

        return await self.update(file_id, updates)

    async def get_by_hash(
        self,
        session_id: UUID,
        file_hash: str
    ) -> Optional[Dict]:
        """
        Busca un archivo por su hash en una sesión

        Args:
            session_id: UUID de la sesión
            file_hash: SHA-256 hash del archivo

        Returns:
            Archivo encontrado o None
        """
        try:
            result = self._table()\
                .select('*')\
                .eq('session_id', str(session_id))\
                .eq('file_hash', file_hash)\
                .single()\
                .execute()

            return result.data if result.data else None

        except APIError as e:
            if 'PGRST116' in str(e):
                return None
            logger.error("uploaded_file_get_by_hash_failed", file_hash=file_hash, error=str(e))
            raise

    async def get_files_pending_ocr(
        self,
        session_id: UUID
    ) -> List[Dict]:
        """
        Obtiene archivos que aún no han sido procesados con OCR

        Args:
            session_id: UUID de la sesión

        Returns:
            Lista de archivos pendientes
        """
        try:
            result = self._table()\
                .select('*')\
                .eq('session_id', str(session_id))\
                .eq('ocr_completed', False)\
                .execute()

            return result.data if result.data else []

        except APIError as e:
            logger.error("uploaded_file_pending_ocr_failed", session_id=str(session_id), error=str(e))
            raise

    async def get_total_size(
        self,
        session_id: UUID
    ) -> int:
        """
        Calcula el tamaño total de archivos en una sesión

        Args:
            session_id: UUID de la sesión

        Returns:
            Tamaño total en bytes
        """
        try:
            files = await self.list_by_session(session_id)

            total_size = sum(
                file.get('size_bytes', 0) for file in files
            )

            return total_size

        except Exception as e:
            logger.error("uploaded_file_total_size_failed", session_id=str(session_id), error=str(e))
            raise

    async def get_files_by_category(
        self,
        session_id: UUID
    ) -> Dict[str, List[Dict]]:
        """
        Agrupa archivos de una sesión por categoría

        Args:
            session_id: UUID de la sesión

        Returns:
            Diccionario {categoría: [archivos]}
        """
        try:
            files = await self.list_by_session(session_id)

            by_category = {}

            for file in files:
                category = file.get('category', 'sin_categoria')

                if category not in by_category:
                    by_category[category] = []

                by_category[category].append(file)

            return by_category

        except Exception as e:
            logger.error("uploaded_file_by_category_failed", session_id=str(session_id), error=str(e))
            raise

    async def delete_by_session(
        self,
        session_id: UUID
    ) -> int:
        """
        Elimina todos los archivos de una sesión

        Args:
            session_id: UUID de la sesión

        Returns:
            Número de archivos eliminados
        """
        try:
            result = self._table()\
                .delete()\
                .eq('session_id', str(session_id))\
                .execute()

            deleted_count = len(result.data) if result.data else 0

            logger.info(
                "uploaded_files_deleted",
                session_id=str(session_id),
                count=deleted_count
            )

            return deleted_count

        except APIError as e:
            logger.error("uploaded_file_delete_by_session_failed", session_id=str(session_id), error=str(e))
            raise


# Instancia singleton del repositorio
uploaded_file_repository = UploadedFileRepository()
