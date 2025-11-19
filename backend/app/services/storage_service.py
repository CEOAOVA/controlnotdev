"""
ControlNot v2 - Storage Service
Gestión de almacenamiento dual: Google Drive + Local filesystem

Migrado de por_partes.py líneas 1814-1834, 1836-1854
"""
from typing import List, Dict, Optional
from pathlib import Path
from io import BytesIO
import structlog

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import Resource

from app.core.config import settings

logger = structlog.get_logger()


class DriveStorageService:
    """
    Servicio de almacenamiento en Google Drive

    Maneja:
    - Listado de templates (.docx)
    - Descarga de archivos
    - Búsqueda por carpeta
    """

    def __init__(self, drive_service: Resource):
        """
        Args:
            drive_service: Cliente de Google Drive API (from dependencies)
        """
        self.drive = drive_service

    def get_templates(self, folder_id: Optional[str] = None) -> List[Dict]:
        """
        Lista templates Word (.docx) desde Google Drive

        Args:
            folder_id: ID de carpeta específica (opcional)
                      Si es None, busca en todo el Drive

        Returns:
            List[Dict]: Lista de templates con:
                - id: File ID de Drive
                - name: Nombre del archivo
                - size: Tamaño en bytes (si disponible)
                - modified: Fecha de modificación
                - source: "drive"

        Example:
            >>> templates = drive_storage.get_templates()
            >>> templates[0]
            {
                'id': '1abc...xyz',
                'name': 'Compraventa_Template.docx',
                'size': 45678,
                'modified': '2024-01-15T10:30:00Z',
                'source': 'drive'
            }
        """
        try:
            # Construir query
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            query = f"mimeType='{mime_type}' and trashed=false"

            if folder_id:
                query += f" and '{folder_id}' in parents"

            # Ejecutar búsqueda
            results = self.drive.files().list(
                q=query,
                pageSize=50,
                fields="files(id, name, size, modifiedTime)"
            ).execute()

            files = results.get('files', [])

            # Formatear respuesta
            templates = []
            for file in files:
                templates.append({
                    'id': file['id'],
                    'name': file['name'],
                    'size': int(file.get('size', 0)),
                    'modified': file.get('modifiedTime'),
                    'source': 'drive'
                })

            logger.info(
                "Templates listados desde Drive",
                folder_id=folder_id,
                total_templates=len(templates)
            )

            return templates

        except Exception as e:
            logger.error(
                "Error al listar templates desde Drive",
                folder_id=folder_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    def download_template(self, file_id: str) -> bytes:
        """
        Descarga un template desde Google Drive

        Args:
            file_id: ID del archivo en Drive

        Returns:
            bytes: Contenido del archivo .docx

        Raises:
            Exception: Si falla la descarga
        """
        try:
            # Crear request de descarga
            request = self.drive.files().get_media(fileId=file_id)

            # Buffer para el contenido
            file_content = BytesIO()

            # Descargar en chunks
            downloader = MediaIoBaseDownload(file_content, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.debug(
                        "Descargando template",
                        file_id=file_id,
                        progress_percent=progress
                    )

            # Obtener bytes
            content = file_content.getvalue()

            logger.info(
                "Template descargado desde Drive",
                file_id=file_id,
                size_bytes=len(content)
            )

            return content

        except Exception as e:
            logger.error(
                "Error al descargar template desde Drive",
                file_id=file_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    def get_template_by_name(self, template_name: str, folder_id: Optional[str] = None) -> Optional[Dict]:
        """
        Busca un template por nombre

        Args:
            template_name: Nombre del archivo a buscar
            folder_id: ID de carpeta (opcional)

        Returns:
            Optional[Dict]: Template encontrado o None
        """
        templates = self.get_templates(folder_id)

        for template in templates:
            if template['name'] == template_name:
                return template

        logger.warning(
            "Template no encontrado en Drive",
            template_name=template_name,
            folder_id=folder_id
        )
        return None


class LocalStorageService:
    """
    Servicio de almacenamiento en filesystem local

    Maneja:
    - Listado de templates (.docx) en directorio local
    - Lectura de archivos
    - Guardado de templates
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Args:
            templates_dir: Directorio donde se guardan los templates
                          Si es None, usa settings.TEMPLATES_DIR
        """
        self.templates_dir = templates_dir or Path(settings.TEMPLATES_DIR)

        # Crear directorio si no existe
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(
            "LocalStorageService inicializado",
            templates_dir=str(self.templates_dir)
        )

    def get_templates(self) -> List[Dict]:
        """
        Lista templates Word (.docx) desde directorio local

        Returns:
            List[Dict]: Lista de templates con:
                - id: Nombre del archivo (para compatibilidad con Drive)
                - name: Nombre del archivo
                - size: Tamaño en bytes
                - modified: Timestamp de modificación
                - source: "local"
                - path: Path absoluto al archivo

        Example:
            >>> templates = local_storage.get_templates()
            >>> templates[0]
            {
                'id': 'Compraventa_Template.docx',
                'name': 'Compraventa_Template.docx',
                'size': 45678,
                'modified': 1705320600.0,
                'source': 'local',
                'path': 'C:/templates/Compraventa_Template.docx'
            }
        """
        try:
            # Buscar archivos .docx
            docx_files = list(self.templates_dir.glob("*.docx"))

            templates = []
            for file_path in docx_files:
                stat = file_path.stat()

                templates.append({
                    'id': file_path.name,  # Usar nombre como ID
                    'name': file_path.name,
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'source': 'local',
                    'path': str(file_path.absolute())
                })

            logger.info(
                "Templates listados desde local",
                templates_dir=str(self.templates_dir),
                total_templates=len(templates)
            )

            return templates

        except Exception as e:
            logger.error(
                "Error al listar templates desde local",
                templates_dir=str(self.templates_dir),
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    def read_template(self, file_name: str) -> bytes:
        """
        Lee un template desde el filesystem local

        Args:
            file_name: Nombre del archivo .docx

        Returns:
            bytes: Contenido del archivo

        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        file_path = self.templates_dir / file_name

        if not file_path.exists():
            logger.error(
                "Template no encontrado en local",
                file_name=file_name,
                path=str(file_path)
            )
            raise FileNotFoundError(f"Template no encontrado: {file_name}")

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            logger.info(
                "Template leído desde local",
                file_name=file_name,
                size_bytes=len(content)
            )

            return content

        except Exception as e:
            logger.error(
                "Error al leer template desde local",
                file_name=file_name,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    def save_template(self, file_name: str, content: bytes) -> bool:
        """
        Guarda un template en el filesystem local

        Args:
            file_name: Nombre del archivo .docx
            content: Contenido del archivo

        Returns:
            bool: True si se guardó exitosamente

        Raises:
            Exception: Si falla el guardado
        """
        file_path = self.templates_dir / file_name

        try:
            with open(file_path, 'wb') as f:
                f.write(content)

            logger.info(
                "Template guardado en local",
                file_name=file_name,
                path=str(file_path),
                size_bytes=len(content)
            )

            return True

        except Exception as e:
            logger.error(
                "Error al guardar template en local",
                file_name=file_name,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    def get_template_by_name(self, template_name: str) -> Optional[Dict]:
        """
        Busca un template por nombre en el directorio local

        Args:
            template_name: Nombre del archivo a buscar

        Returns:
            Optional[Dict]: Template encontrado o None
        """
        templates = self.get_templates()

        for template in templates:
            if template['name'] == template_name:
                return template

        logger.warning(
            "Template no encontrado en local",
            template_name=template_name,
            templates_dir=str(self.templates_dir)
        )
        return None

    def delete_template(self, file_name: str) -> bool:
        """
        Elimina un template del filesystem local

        Args:
            file_name: Nombre del archivo a eliminar

        Returns:
            bool: True si se eliminó exitosamente

        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        file_path = self.templates_dir / file_name

        if not file_path.exists():
            logger.error(
                "Template no encontrado para eliminar",
                file_name=file_name,
                path=str(file_path)
            )
            raise FileNotFoundError(f"Template no encontrado: {file_name}")

        try:
            file_path.unlink()

            logger.info(
                "Template eliminado de local",
                file_name=file_name,
                path=str(file_path)
            )

            return True

        except Exception as e:
            logger.error(
                "Error al eliminar template de local",
                file_name=file_name,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
