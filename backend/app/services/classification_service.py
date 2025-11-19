"""
ControlNot v2 - Classification Service
Auto-detecta el tipo de documento basándose en placeholders y nombre del template

Migrado de por_partes.py líneas 1388-1416
"""
from typing import List, Dict
import structlog

logger = structlog.get_logger()


def detect_document_type(
    template_placeholders: List[str],
    template_name: str = ""
) -> str:
    """
    Detecta automáticamente el tipo de documento basándose en keywords

    Args:
        template_placeholders: Lista de placeholders encontrados en el template
        template_name: Nombre del archivo del template (opcional)

    Returns:
        str: Tipo de documento detectado ('compraventa', 'donacion', 'testamento', 'poder', 'sociedad')
             Si no se puede determinar, retorna 'compraventa' por defecto

    Example:
        >>> placeholders = ["Vendedor_Nombre", "Comprador_Nombre", "Precio_Venta"]
        >>> detect_document_type(placeholders)
        'compraventa'
    """
    scores: Dict[str, int] = {}
    placeholders_text = " ".join(template_placeholders).lower()
    template_name_lower = template_name.lower()

    # Keywords por tipo de documento
    keywords = {
        "compraventa": ["vendedor", "vendedora", "comprador", "compradora", "precio", "venta"],
        "donacion": ["donante", "donataria", "donatario", "donacion", "donadora", "donador"],
        "testamento": ["testador", "heredero", "legatario", "albacea"],
        "poder": ["otorgante", "apoderado", "poder", "facultades"],
        "sociedad": ["sociedad", "socio", "capital", "denominacion"]
    }

    # Calcular score para cada tipo
    for doc_type, keywords_list in keywords.items():
        score = 0
        for keyword in keywords_list:
            if keyword in placeholders_text:
                score += 2  # Mayor peso a placeholders
            if keyword in template_name_lower:
                score += 1  # Menor peso al nombre del archivo

        scores[doc_type] = score

    # Retornar el tipo con mayor score
    if scores:
        best_type = max(scores.items(), key=lambda x: x[1])
        if best_type[1] > 0:
            logger.info(
                "Tipo de documento detectado",
                doc_type=best_type[0],
                score=best_type[1],
                template_name=template_name
            )
            return best_type[0]

    # Default si no se puede determinar
    logger.warning(
        "No se pudo detectar tipo de documento, usando default",
        template_name=template_name,
        placeholders_count=len(template_placeholders)
    )
    return "compraventa"


def get_document_type_display_name(doc_type: str) -> str:
    """
    Obtiene el nombre de display para un tipo de documento

    Args:
        doc_type: Tipo de documento ('compraventa', 'donacion', etc.)

    Returns:
        str: Nombre amigable del tipo de documento
    """
    display_names = {
        "compraventa": "Compraventa",
        "donacion": "Donación",
        "testamento": "Testamento",
        "poder": "Poder Notarial",
        "sociedad": "Constitución de Sociedad"
    }

    return display_names.get(doc_type, doc_type.capitalize())


def validate_document_type(doc_type: str) -> bool:
    """
    Valida que el tipo de documento sea válido

    Args:
        doc_type: Tipo de documento a validar

    Returns:
        bool: True si es válido, False si no
    """
    valid_types = ["compraventa", "donacion", "testamento", "poder", "sociedad"]
    return doc_type.lower() in valid_types


def get_all_document_types() -> List[Dict[str, str]]:
    """
    Retorna lista de todos los tipos de documentos soportados

    Returns:
        List[Dict]: Lista de dicts con 'id' y 'nombre' de cada tipo
    """
    return [
        {"id": "compraventa", "nombre": "Compraventa"},
        {"id": "donacion", "nombre": "Donación"},
        {"id": "testamento", "nombre": "Testamento"},
        {"id": "poder", "nombre": "Poder Notarial"},
        {"id": "sociedad", "nombre": "Constitución de Sociedad"}
    ]
