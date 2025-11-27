"""
ControlNot v2 - Session Repository
Repositorio para gestión de sesiones de extracción/procesamiento
"""
from typing import Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError
from datetime import datetime, timezone

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class SessionRepository(BaseRepository):
    """
    Repositorio para la tabla 'sessions'

    Gestiona sesiones de procesamiento de documentos (OCR + IA)
    """

    def __init__(self):
        super().__init__('sessions')

    async def create_session(
        self,
        tenant_id: UUID,
        case_id: UUID,
        tipo_documento: str,
        total_archivos: int = 0,
        session_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Crea una nueva sesión de procesamiento

        Args:
            tenant_id: UUID de la notaría
            case_id: UUID del caso al que pertenece esta sesión
            tipo_documento: Tipo de documento (compraventa, cancelacion, etc.)
            total_archivos: Número total de archivos a procesar
            session_data: Datos adicionales de la sesión (JSONB)

        Returns:
            Sesión creada
        """
        session_info = {
            'tenant_id': str(tenant_id),
            'case_id': str(case_id),
            'tipo_documento': tipo_documento,
            'estado': 'iniciado',
            'total_archivos': total_archivos,
            'archivos_procesados': 0,
            'progreso_porcentaje': 0.0,
            'session_data': session_data or {}
        }

        return await self.create(session_info)

    async def get_session_with_case(
        self,
        session_id: UUID
    ) -> Optional[Dict]:
        """
        Obtiene una sesión con información del caso y cliente

        Args:
            session_id: UUID de la sesión

        Returns:
            Sesión con datos del caso y cliente
        """
        try:
            result = self._table()\
                .select('*, cases(*, clients(*))')\
                .eq('id', str(session_id))\
                .single()\
                .execute()

            return result.data if result.data else None

        except APIError as e:
            if 'PGRST116' in str(e):
                return None
            logger.error("session_get_with_case_failed", session_id=str(session_id), error=str(e))
            raise

    async def list_by_case(
        self,
        case_id: UUID,
        limit: int = 20
    ) -> List[Dict]:
        """
        Lista sesiones de un caso específico

        Args:
            case_id: UUID del caso
            limit: Número máximo de resultados

        Returns:
            Lista de sesiones del caso
        """
        try:
            result = self._table()\
                .select('*')\
                .eq('case_id', str(case_id))\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()

            return result.data if result.data else []

        except APIError as e:
            logger.error("session_list_by_case_failed", case_id=str(case_id), error=str(e))
            raise

    async def update_progress(
        self,
        session_id: UUID,
        archivos_procesados: int,
        total_archivos: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Actualiza el progreso de una sesión

        Args:
            session_id: UUID de la sesión
            archivos_procesados: Número de archivos procesados
            total_archivos: Total de archivos (opcional, si cambió)

        Returns:
            Sesión actualizada
        """
        try:
            # Obtener sesión actual para calcular progreso
            session = await self.get_by_id(session_id)

            if not session:
                return None

            total = total_archivos if total_archivos is not None else session['total_archivos']

            # Calcular progreso porcentual
            if total > 0:
                progreso = (archivos_procesados / total) * 100.0
            else:
                progreso = 0.0

            updates = {
                'archivos_procesados': archivos_procesados,
                'progreso_porcentaje': round(progreso, 2)
            }

            if total_archivos is not None:
                updates['total_archivos'] = total_archivos

            # Si completó todos los archivos, marcar como procesando
            if archivos_procesados >= total and total > 0:
                updates['estado'] = 'procesando'

            return await self.update(session_id, updates)

        except Exception as e:
            logger.error("session_update_progress_failed", session_id=str(session_id), error=str(e))
            raise

    async def complete_session(
        self,
        session_id: UUID,
        error_message: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Marca una sesión como completada o con error

        Args:
            session_id: UUID de la sesión
            error_message: Mensaje de error (si falló)

        Returns:
            Sesión actualizada
        """
        updates = {
            'completed_at': datetime.now(timezone.utc).isoformat()
        }

        if error_message:
            updates['estado'] = 'error'
            updates['error_message'] = error_message
        else:
            updates['estado'] = 'completado'
            updates['progreso_porcentaje'] = 100.0

        return await self.update(session_id, updates)

    async def add_session_data(
        self,
        session_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """
        Agrega o actualiza datos adicionales de la sesión

        Args:
            session_id: UUID de la sesión
            data: Diccionario con datos a agregar/actualizar

        Returns:
            Sesión actualizada
        """
        try:
            # Obtener sesión actual
            session = await self.get_by_id(session_id)

            if not session:
                return None

            # Merge con datos existentes
            session_data = session.get('session_data', {})
            session_data.update(data)

            return await self.update(session_id, {'session_data': session_data})

        except Exception as e:
            logger.error("session_add_data_failed", session_id=str(session_id), error=str(e))
            raise

    async def get_active_sessions(
        self,
        tenant_id: UUID,
        tipo_documento: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtiene sesiones activas (en procesamiento)

        Args:
            tenant_id: UUID de la notaría
            tipo_documento: Filtrar por tipo de documento (opcional)

        Returns:
            Lista de sesiones activas
        """
        try:
            query = self._table()\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .in_('estado', ['iniciado', 'procesando'])

            if tipo_documento:
                query = query.eq('tipo_documento', tipo_documento)

            result = query\
                .order('created_at', desc=True)\
                .execute()

            return result.data if result.data else []

        except APIError as e:
            logger.error("session_get_active_failed", tenant_id=str(tenant_id), error=str(e))
            raise

    async def cancel_session(
        self,
        session_id: UUID,
        reason: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Cancela una sesión en proceso

        Args:
            session_id: UUID de la sesión
            reason: Razón de cancelación (opcional)

        Returns:
            Sesión cancelada
        """
        updates = {
            'estado': 'cancelado',
            'error_message': reason or 'Sesión cancelada por el usuario'
        }

        return await self.update(session_id, updates)


# Instancia singleton del repositorio
session_repository = SessionRepository()
