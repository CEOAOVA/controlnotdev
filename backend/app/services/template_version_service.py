"""
ControlNot v2 - Template Version Service
Gestión de versiones de templates Word

Maneja:
- Creación de nuevas versiones al subir templates
- Listado del historial de versiones
- Activación/rollback de versiones
- Comparación entre versiones
"""
import time
from typing import List, Dict, Optional
import structlog
from datetime import datetime

from app.database import supabase_admin, get_supabase_admin_client
from app.services.supabase_storage_service import SupabaseStorageService

logger = structlog.get_logger()


class TemplateVersionService:
    """
    Servicio para gestionar versiones de templates

    Cada template puede tener múltiples versiones, pero solo una activa.
    Al subir un template con el mismo nombre, se crea una nueva versión.
    """

    def __init__(self, storage_service: Optional[SupabaseStorageService] = None):
        """
        Args:
            storage_service: Servicio de storage para subir archivos
        """
        self.client = get_supabase_admin_client()
        self.storage = storage_service or SupabaseStorageService()
        logger.debug("TemplateVersionService inicializado")

    async def create_version(
        self,
        template_id: str,
        content: bytes,
        placeholders: List[str],
        placeholder_mapping: Dict[str, str],
        tenant_id: str,
        notas: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Crea una nueva versión del template

        Args:
            template_id: UUID del template padre
            content: Contenido binario del archivo .docx
            placeholders: Lista de placeholders extraídos
            placeholder_mapping: Mapeo de placeholders a claves estándar
            tenant_id: ID del tenant
            notas: Notas descriptivas de la versión
            user_id: UUID del usuario que crea la versión

        Returns:
            Dict: Información de la versión creada

        Raises:
            Exception: Si falla la creación
        """
        start_time = time.time()
        logger.info(
            "version_create_starting",
            template_id=template_id,
            tenant_id=tenant_id,
            placeholders_count=len(placeholders)
        )

        try:
            # 1. Obtener el número de versión siguiente
            version_number = await self._get_next_version_number(template_id)

            # 2. Generar storage_path con versión
            storage_path = f"{tenant_id}/{template_id}_v{version_number}.docx"

            # 3. Subir archivo a Storage
            storage_start = time.time()
            upload_result = await self.storage.save_template(
                file_name=f"{template_id}_v{version_number}.docx",
                content=content,
                tenant_id=tenant_id
            )
            storage_duration = (time.time() - storage_start) * 1000

            logger.debug(
                "version_storage_upload_complete",
                path=storage_path,
                duration_ms=round(storage_duration, 2)
            )

            # 4. Insertar registro en template_versions con es_activa=true
            # El trigger se encarga de desactivar las demás versiones
            db_start = time.time()
            result = supabase_admin.table('template_versions').insert({
                'template_id': template_id,
                'version_number': version_number,
                'storage_path': storage_path,
                'placeholders': placeholders,
                'placeholder_mapping': placeholder_mapping,
                'notas': notas,
                'es_activa': True,
                'created_by': user_id
            }).execute()
            db_duration = (time.time() - db_start) * 1000

            if not result.data:
                raise Exception("No se pudo crear el registro de versión")

            version_data = result.data[0]

            # 5. Actualizar active_version_id en templates
            supabase_admin.table('templates').update({
                'active_version_id': version_data['id'],
                'storage_path': storage_path  # Actualizar también storage_path del template
            }).eq('id', template_id).execute()

            total_duration = (time.time() - start_time) * 1000
            logger.info(
                "version_create_complete",
                template_id=template_id,
                version_id=version_data['id'],
                version_number=version_number,
                total_ms=round(total_duration, 2),
                storage_ms=round(storage_duration, 2),
                db_ms=round(db_duration, 2)
            )

            return {
                'id': str(version_data['id']),
                'template_id': template_id,
                'version_number': version_number,
                'storage_path': storage_path,
                'placeholders': placeholders,
                'placeholder_mapping': placeholder_mapping,
                'es_activa': True,
                'created_at': version_data.get('created_at'),
                'notas': notas
            }

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                "version_create_failed",
                template_id=template_id,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration, 2)
            )
            raise

    async def _get_next_version_number(self, template_id: str) -> int:
        """
        Obtiene el siguiente número de versión para un template

        Args:
            template_id: UUID del template

        Returns:
            int: Siguiente número de versión (1 si no hay versiones previas)
        """
        result = supabase_admin.table('template_versions').select(
            'version_number'
        ).eq(
            'template_id', template_id
        ).order(
            'version_number', desc=True
        ).limit(1).execute()

        if result.data and len(result.data) > 0:
            return result.data[0]['version_number'] + 1
        return 1

    async def get_versions(self, template_id: str) -> List[Dict]:
        """
        Lista todas las versiones de un template

        Args:
            template_id: UUID del template

        Returns:
            List[Dict]: Lista de versiones ordenadas por version_number DESC
        """
        start_time = time.time()
        logger.debug("version_list_starting", template_id=template_id)

        try:
            result = supabase_admin.table('template_versions').select(
                '*'
            ).eq(
                'template_id', template_id
            ).order(
                'version_number', desc=True
            ).execute()

            versions = []
            for record in result.data or []:
                versions.append({
                    'id': str(record['id']),
                    'template_id': str(record['template_id']),
                    'version_number': record['version_number'],
                    'storage_path': record['storage_path'],
                    'placeholders': record.get('placeholders', []),
                    'placeholder_mapping': record.get('placeholder_mapping', {}),
                    'es_activa': record.get('es_activa', False),
                    'created_at': record.get('created_at'),
                    'created_by': record.get('created_by'),
                    'notas': record.get('notas')
                })

            duration = (time.time() - start_time) * 1000
            logger.info(
                "version_list_complete",
                template_id=template_id,
                versions_count=len(versions),
                duration_ms=round(duration, 2)
            )

            return versions

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                "version_list_failed",
                template_id=template_id,
                error=str(e),
                duration_ms=round(duration, 2)
            )
            raise

    async def get_active_version(self, template_id: str) -> Optional[Dict]:
        """
        Obtiene la versión activa de un template

        Args:
            template_id: UUID del template

        Returns:
            Optional[Dict]: Versión activa o None si no hay
        """
        start_time = time.time()

        try:
            result = supabase_admin.table('template_versions').select(
                '*'
            ).eq(
                'template_id', template_id
            ).eq(
                'es_activa', True
            ).limit(1).execute()

            duration = (time.time() - start_time) * 1000

            if result.data and len(result.data) > 0:
                record = result.data[0]
                logger.debug(
                    "version_active_found",
                    template_id=template_id,
                    version_number=record['version_number'],
                    duration_ms=round(duration, 2)
                )
                return {
                    'id': str(record['id']),
                    'template_id': str(record['template_id']),
                    'version_number': record['version_number'],
                    'storage_path': record['storage_path'],
                    'placeholders': record.get('placeholders', []),
                    'placeholder_mapping': record.get('placeholder_mapping', {}),
                    'es_activa': True,
                    'created_at': record.get('created_at'),
                    'notas': record.get('notas')
                }

            # Fallback: buscar la versión con número más alto
            fallback_result = supabase_admin.table('template_versions').select(
                '*'
            ).eq(
                'template_id', template_id
            ).order(
                'version_number', desc=True
            ).limit(1).execute()

            if fallback_result.data and len(fallback_result.data) > 0:
                record = fallback_result.data[0]
                logger.warning(
                    "version_active_fallback_to_latest",
                    template_id=template_id,
                    version_number=record['version_number']
                )
                return {
                    'id': str(record['id']),
                    'template_id': str(record['template_id']),
                    'version_number': record['version_number'],
                    'storage_path': record['storage_path'],
                    'placeholders': record.get('placeholders', []),
                    'placeholder_mapping': record.get('placeholder_mapping', {}),
                    'es_activa': record.get('es_activa', False),
                    'created_at': record.get('created_at'),
                    'notas': record.get('notas')
                }

            logger.warning(
                "version_active_not_found",
                template_id=template_id,
                duration_ms=round(duration, 2)
            )
            return None

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                "version_active_failed",
                template_id=template_id,
                error=str(e),
                duration_ms=round(duration, 2)
            )
            raise

    async def set_active_version(
        self,
        template_id: str,
        version_id: str
    ) -> Dict:
        """
        Establece una versión como activa (rollback)

        El trigger de BD se encarga de desactivar las demás versiones.

        Args:
            template_id: UUID del template
            version_id: UUID de la versión a activar

        Returns:
            Dict: Versión activada con info de la anterior

        Raises:
            Exception: Si la versión no existe o falla la operación
        """
        start_time = time.time()
        logger.info(
            "version_activate_starting",
            template_id=template_id,
            version_id=version_id
        )

        try:
            # 1. Obtener versión actual activa
            current_active = await self.get_active_version(template_id)
            previous_version_number = current_active['version_number'] if current_active else None

            # 2. Verificar que la versión existe
            version_result = supabase_admin.table('template_versions').select(
                '*'
            ).eq('id', version_id).eq('template_id', template_id).single().execute()

            if not version_result.data:
                raise Exception(f"Versión {version_id} no encontrada para template {template_id}")

            version_data = version_result.data

            # 3. Activar la versión (el trigger desactiva las demás)
            update_result = supabase_admin.table('template_versions').update({
                'es_activa': True
            }).eq('id', version_id).execute()

            # 4. Actualizar active_version_id y storage_path en templates
            supabase_admin.table('templates').update({
                'active_version_id': version_id,
                'storage_path': version_data['storage_path']
            }).eq('id', template_id).execute()

            duration = (time.time() - start_time) * 1000
            logger.info(
                "version_activate_complete",
                template_id=template_id,
                version_id=version_id,
                version_number=version_data['version_number'],
                previous_version=previous_version_number,
                duration_ms=round(duration, 2)
            )

            return {
                'id': str(version_data['id']),
                'template_id': template_id,
                'version_number': version_data['version_number'],
                'storage_path': version_data['storage_path'],
                'placeholders': version_data.get('placeholders', []),
                'placeholder_mapping': version_data.get('placeholder_mapping', {}),
                'es_activa': True,
                'created_at': version_data.get('created_at'),
                'notas': version_data.get('notas'),
                'previous_active_version': previous_version_number
            }

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                "version_activate_failed",
                template_id=template_id,
                version_id=version_id,
                error=str(e),
                duration_ms=round(duration, 2)
            )
            raise

    async def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> Dict:
        """
        Compara los placeholders entre dos versiones

        Args:
            version_id_1: UUID de la primera versión
            version_id_2: UUID de la segunda versión

        Returns:
            Dict: Comparación con placeholders agregados, eliminados y sin cambios
        """
        start_time = time.time()
        logger.debug(
            "version_compare_starting",
            version_1=version_id_1,
            version_2=version_id_2
        )

        try:
            # Obtener ambas versiones
            v1_result = supabase_admin.table('template_versions').select(
                'id, version_number, placeholders'
            ).eq('id', version_id_1).single().execute()

            v2_result = supabase_admin.table('template_versions').select(
                'id, version_number, placeholders'
            ).eq('id', version_id_2).single().execute()

            if not v1_result.data:
                raise Exception(f"Versión {version_id_1} no encontrada")
            if not v2_result.data:
                raise Exception(f"Versión {version_id_2} no encontrada")

            v1 = v1_result.data
            v2 = v2_result.data

            # Comparar placeholders
            placeholders_1 = set(v1.get('placeholders', []))
            placeholders_2 = set(v2.get('placeholders', []))

            added = list(placeholders_2 - placeholders_1)
            removed = list(placeholders_1 - placeholders_2)
            unchanged = list(placeholders_1 & placeholders_2)

            duration = (time.time() - start_time) * 1000
            logger.info(
                "version_compare_complete",
                version_1=version_id_1,
                version_2=version_id_2,
                added_count=len(added),
                removed_count=len(removed),
                unchanged_count=len(unchanged),
                duration_ms=round(duration, 2)
            )

            return {
                'version_1': {
                    'id': str(v1['id']),
                    'version_number': v1['version_number']
                },
                'version_2': {
                    'id': str(v2['id']),
                    'version_number': v2['version_number']
                },
                'added_placeholders': sorted(added),
                'removed_placeholders': sorted(removed),
                'unchanged_placeholders': sorted(unchanged),
                'total_changes': len(added) + len(removed)
            }

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                "version_compare_failed",
                version_1=version_id_1,
                version_2=version_id_2,
                error=str(e),
                duration_ms=round(duration, 2)
            )
            raise

    async def get_version_content(self, version_id: str) -> bytes:
        """
        Obtiene el contenido binario de una versión específica

        Args:
            version_id: UUID de la versión

        Returns:
            bytes: Contenido del archivo .docx
        """
        # Obtener storage_path de la versión
        result = supabase_admin.table('template_versions').select(
            'storage_path'
        ).eq('id', version_id).single().execute()

        if not result.data:
            raise Exception(f"Versión {version_id} no encontrada")

        storage_path = result.data['storage_path']

        # Descargar desde storage
        return self.storage.read_template(storage_path)
