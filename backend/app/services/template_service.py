"""
ControlNot v2 - Template Service
Extrae placeholders de templates Word (.docx)

Migrado de por_partes.py líneas 1458-1502
"""
import re
import tempfile
from typing import List
from pathlib import Path
import structlog
from docx import Document

logger = structlog.get_logger()


class PlaceholderExtractor:
    """
    Extrae placeholders de documentos Word

    Soporta dos formatos:
    - {{placeholder}} - Formato primario
    - {placeholder} - Formato alternativo
    """

    # Patrones de búsqueda para placeholders
    PLACEHOLDER_PATTERNS = [
        r'\{\{([^}]+)\}\}',  # {{placeholder}}
        r'\{([^}]+)\}',      # {placeholder}
    ]

    @staticmethod
    def extract_from_bytes(template_content: bytes) -> List[str]:
        """
        Extrae placeholders de un template en bytes

        Args:
            template_content: Contenido del archivo .docx en bytes

        Returns:
            List[str]: Lista ordenada de placeholders únicos encontrados

        Example:
            >>> content = open('template.docx', 'rb').read()
            >>> placeholders = PlaceholderExtractor.extract_from_bytes(content)
            >>> placeholders
            ['Cliente_Nombre', 'Fecha_Escritura', 'Notario_Numero']
        """
        placeholders = set()

        # Crear archivo temporal para procesar
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_path = Path(temp_file.name)
            try:
                # Escribir contenido al archivo temporal
                temp_file.write(template_content)
                temp_file.flush()

                # Abrir documento con python-docx
                doc = Document(temp_path)

                # Extraer texto de diferentes partes del documento
                text_parts = []

                # 1. Párrafos del body
                for paragraph in doc.paragraphs:
                    text_parts.append(paragraph.text)

                # 2. Tablas
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            text_parts.append(cell.text)

                # 3. Headers (encabezados)
                for section in doc.sections:
                    header = section.header
                    for paragraph in header.paragraphs:
                        text_parts.append(paragraph.text)

                # 4. Footers (pies de página)
                for section in doc.sections:
                    footer = section.footer
                    for paragraph in footer.paragraphs:
                        text_parts.append(paragraph.text)

                # Buscar placeholders en todo el texto extraído
                all_text = "\n".join(text_parts)

                for pattern in PlaceholderExtractor.PLACEHOLDER_PATTERNS:
                    matches = re.finditer(pattern, all_text)
                    for match in matches:
                        placeholder = match.group(1).strip()
                        if placeholder:  # Ignorar placeholders vacíos
                            placeholders.add(placeholder)

                logger.info(
                    "Placeholders extraídos del template",
                    total_placeholders=len(placeholders),
                    placeholders=sorted(placeholders)[:5]  # Primeros 5 para log
                )

            except Exception as e:
                logger.error(
                    "Error al extraer placeholders del template",
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise
            finally:
                # Limpiar archivo temporal
                try:
                    temp_path.unlink()
                except Exception as cleanup_error:
                    logger.warning(
                        "No se pudo eliminar archivo temporal",
                        temp_path=str(temp_path),
                        error=str(cleanup_error)
                    )

        # Retornar lista ordenada
        return sorted(list(placeholders))

    @staticmethod
    def extract_from_file(file_path: Path) -> List[str]:
        """
        Extrae placeholders de un archivo Word en disco

        Args:
            file_path: Path al archivo .docx

        Returns:
            List[str]: Lista ordenada de placeholders únicos
        """
        logger.info("Extrayendo placeholders de archivo", file_path=str(file_path))

        with open(file_path, 'rb') as f:
            content = f.read()

        return PlaceholderExtractor.extract_from_bytes(content)


def extract_placeholders_from_template(template_content: bytes) -> List[str]:
    """
    Función pública para extraer placeholders de un template

    Esta es la función principal que debe usarse desde otros módulos.
    Wrapper sobre PlaceholderExtractor.extract_from_bytes()

    Args:
        template_content: Contenido del archivo .docx en bytes

    Returns:
        List[str]: Lista ordenada de placeholders únicos

    Example:
        >>> from app.services.template_service import extract_placeholders_from_template
        >>> with open('template.docx', 'rb') as f:
        ...     content = f.read()
        >>> placeholders = extract_placeholders_from_template(content)
        >>> print(placeholders)
        ['Cliente_Apellido', 'Cliente_Nombre', 'Fecha_Escritura']
    """
    return PlaceholderExtractor.extract_from_bytes(template_content)


def validate_template_content(template_content: bytes) -> bool:
    """
    Valida que el contenido sea un archivo Word válido

    Args:
        template_content: Contenido a validar

    Returns:
        bool: True si es válido, False si no
    """
    if not template_content or len(template_content) == 0:
        logger.warning("Template vacío")
        return False

    # Verificar firma de archivo .docx (ZIP)
    # Los archivos .docx son ZIP con firma PK (50 4B)
    if not template_content.startswith(b'PK'):
        logger.warning("Template no tiene firma de archivo .docx")
        return False

    try:
        # Intentar extraer placeholders (validación completa)
        placeholders = extract_placeholders_from_template(template_content)
        logger.info(
            "Template validado exitosamente",
            placeholders_found=len(placeholders)
        )
        return True
    except Exception as e:
        logger.error(
            "Error al validar template",
            error=str(e),
            error_type=type(e).__name__
        )
        return False
