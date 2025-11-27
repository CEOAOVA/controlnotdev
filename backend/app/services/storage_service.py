"""
ControlNot v2 - Storage Service
Gestión de almacenamiento local (filesystem)

Nota: Google Drive ha sido removido. Usar SupabaseStorageService para
almacenamiento en la nube.
"""
from typing import List, Dict, Optional
from pathlib import Path
import structlog

from app.core.config import settings

logger = structlog.get_logger()


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
