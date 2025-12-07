"""
ControlNot v2 - Document Repository
Repositorio para gestión de documentos generados
"""
from typing import Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError
from datetime import datetime, timezone, timedelta

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class DocumentRepository(BaseRepository):
    """
    Repositorio para la tabla 'documentos'

    Gestiona documentos finales generados por el sistema
    """

    def __init__(self):
        super().__init__('documentos')

    async def create_document(
        self,
        tenant_id: UUID,
        case_id: UUID,
        session_id: Optional[UUID],
        template_id: Optional[UUID],
        tipo_documento: str,
        nombre_documento: str,
        storage_path: str,
        extracted_data: Optional[Dict] = None,
        edited_data: Optional[Dict] = None,
        google_drive_id: Optional[str] = None,
        confidence_score: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Crea un nuevo documento generado

        Args:
            tenant_id: UUID de la notaría
            case_id: UUID del caso al que pertenece
            session_id: UUID de la sesión de procesamiento (opcional)
            template_id: UUID del template usado (opcional)
            tipo_documento: Tipo de documento
            nombre_documento: Nombre del documento
            storage_path: Ruta en Supabase Storage
            extracted_data: Datos extraídos con IA
            edited_data: Datos editados por usuario
            google_drive_id: ID en Google Drive (si se usa)
            confidence_score: Score de confianza de la extracción
            metadata: Metadata adicional

        Returns:
            Documento creado
        """
        doc_data = {
            'tenant_id': str(tenant_id),
            'case_id': str(case_id),
            'tipo_documento': tipo_documento,
            'nombre_documento': nombre_documento,
            'storage_path': storage_path,
            'estado': 'borrador',
            'extracted_data': extracted_data or {},
            'metadata': metadata or {}
        }

        if session_id:
            doc_data['session_id'] = str(session_id)
        if template_id:
            doc_data['template_id'] = str(template_id)
        if edited_data:
            doc_data['edited_data'] = edited_data
        if google_drive_id:
            doc_data['google_drive_id'] = google_drive_id
        if confidence_score is not None:
            doc_data['confidence_score'] = confidence_score

        return await self.create(doc_data)

    async def get_document_with_relations(
        self,
        document_id: UUID
    ) -> Optional[Dict]:
        """
        Obtiene un documento con todas sus relaciones

        Args:
            document_id: UUID del documento

        Returns:
            Documento con caso, template, sesión
        """
        try:
            result = self._table()\
                .select('*, cases(*, clients(*)), templates(*), sessions(*)')\
                .eq('id', str(document_id))\
                .single()\
                .execute()

            return result.data if result.data else None

        except APIError as e:
            if 'PGRST116' in str(e):
                return None
            logger.error("document_get_with_relations_failed", document_id=str(document_id), error=str(e))
            raise

    async def list_by_case(
        self,
        case_id: UUID,
        estado: Optional[str] = None
    ) -> List[Dict]:
        """
        Lista documentos de un caso

        Args:
            case_id: UUID del caso
            estado: Filtrar por estado (opcional)

        Returns:
            Lista de documentos del caso
        """
        try:
            query = self._table()\
                .select('*')\
                .eq('case_id', str(case_id))

            if estado:
                query = query.eq('estado', estado)

            result = query\
                .order('created_at', desc=True)\
                .execute()

            return result.data if result.data else []

        except APIError as e:
            logger.error("document_list_by_case_failed", case_id=str(case_id), error=str(e))
            raise

    async def list_by_session(
        self,
        session_id: UUID
    ) -> List[Dict]:
        """
        Lista documentos generados en una sesión

        Args:
            session_id: UUID de la sesión

        Returns:
            Lista de documentos de la sesión
        """
        try:
            result = self._table()\
                .select('*')\
                .eq('session_id', str(session_id))\
                .order('created_at', desc=True)\
                .execute()

            return result.data if result.data else []

        except APIError as e:
            logger.error("document_list_by_session_failed", session_id=str(session_id), error=str(e))
            raise

    async def update_estado(
        self,
        document_id: UUID,
        nuevo_estado: str
    ) -> Optional[Dict]:
        """
        Actualiza el estado de un documento

        Args:
            document_id: UUID del documento
            nuevo_estado: Nuevo estado (borrador, procesando, revisado, completado, error)

        Returns:
            Documento actualizado
        """
        updates = {'estado': nuevo_estado}

        # Si se completa, marcar timestamp
        if nuevo_estado == 'completado':
            updates['completed_at'] = datetime.now(timezone.utc).isoformat()

        return await self.update(document_id, updates)

    async def update_edited_data(
        self,
        document_id: UUID,
        edited_data: Dict
    ) -> Optional[Dict]:
        """
        Actualiza datos editados por el usuario

        Args:
            document_id: UUID del documento
            edited_data: Datos editados

        Returns:
            Documento actualizado
        """
        return await self.update(document_id, {'edited_data': edited_data})

    async def mark_as_good_example(
        self,
        document_id: UUID,
        is_good: bool = True
    ) -> Optional[Dict]:
        """
        Marca un documento como buen ejemplo para entrenamiento

        Args:
            document_id: UUID del documento
            is_good: Si es buen ejemplo o no

        Returns:
            Documento actualizado
        """
        return await self.update(document_id, {'es_ejemplo_bueno': is_good})

    async def set_expiration(
        self,
        document_id: UUID,
        days: int = 30
    ) -> Optional[Dict]:
        """
        Establece fecha de expiración para un documento

        Args:
            document_id: UUID del documento
            days: Días hasta expiración (desde ahora)

        Returns:
            Documento actualizado
        """
        try:
            # Agregar campo expires_at si no existe
            # Esto requeriría una migración, por ahora usar metadata
            expires_at = datetime.now(timezone.utc) + timedelta(days=days)

            # Obtener documento actual
            doc = await self.get_by_id(document_id)

            if not doc:
                return None

            metadata = doc.get('metadata', {})
            metadata['expires_at'] = expires_at.isoformat()

            return await self.update(document_id, {'metadata': metadata})

        except Exception as e:
            logger.error("document_set_expiration_failed", document_id=str(document_id), error=str(e))
            raise

    async def get_documents_requiring_review(
        self,
        tenant_id: UUID,
        limit: int = 50
    ) -> List[Dict]:
        """
        Obtiene documentos que requieren revisión

        Args:
            tenant_id: UUID de la notaría
            limit: Número máximo de resultados

        Returns:
            Lista de documentos que requieren revisión
        """
        return await self.list_by_tenant(
            tenant_id=tenant_id,
            filters={'requiere_revision': True},
            limit=limit,
            order_by='created_at',
            descending=True
        )

    async def get_signed_url(
        self,
        storage_path: str,
        bucket: str = 'generated',
        expires_in: int = 3600
    ) -> str:
        """
        Genera URL firmada para descargar documento

        Args:
            storage_path: Ruta en Storage
            bucket: Bucket de Supabase Storage
            expires_in: Tiempo de expiración en segundos (default 1 hora)

        Returns:
            URL firmada
        """
        try:
            from app.database import supabase_admin

            signed_url = supabase_admin.storage.from_(bucket)\
                .create_signed_url(storage_path, expires_in)

            if signed_url and 'signedURL' in signed_url:
                return signed_url['signedURL']

            return ""

        except Exception as e:
            logger.error("document_get_signed_url_failed", storage_path=storage_path, error=str(e))
            raise


# Instancia singleton del repositorio
document_repository = DocumentRepository()
