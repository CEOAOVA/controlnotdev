"""
ControlNot v2 - Categorization Service
Gestión de categorías de documentos por rol (Parte A, Parte B, Otros)

Migrado de por_partes.py líneas 1959-2182
"""
import json
from typing import Dict, List
from pathlib import Path
import structlog

logger = structlog.get_logger()

# Path al archivo de categorías
CATEGORIES_FILE = Path(__file__).parent.parent.parent / "data" / "categories.json"


def load_categories() -> Dict:
    """
    Carga el archivo de categorías desde JSON

    Returns:
        Dict: Diccionario completo de categorías
    """
    try:
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Archivo categories.json no encontrado", path=str(CATEGORIES_FILE))
        return {}
    except json.JSONDecodeError as e:
        logger.error("Error al parsear categories.json", error=str(e))
        return {}


def get_categories_for_type(document_type: str) -> Dict:
    """
    Obtiene las categorías de documentos para un tipo específico

    Args:
        document_type: Tipo de documento ('compraventa', 'donacion', etc.)

    Returns:
        Dict: Diccionario con categorías 'parte_a', 'parte_b', 'otros'
              Cada categoría contiene: nombre, icono, descripcion, documentos

    Example:
        >>> cats = get_categories_for_type('compraventa')
        >>> cats['parte_a']['nombre']
        'Documentos del Vendedor'
    """
    categories = load_categories()

    # Buscar categorías para el tipo específico
    doc_categories = categories.get(document_type)

    if not doc_categories:
        logger.warning(
            "Tipo de documento no encontrado en categories.json, usando default",
            doc_type=document_type
        )
        doc_categories = categories.get("default", {})

    if not doc_categories:
        # Fallback si no hay categorías
        logger.error("No hay categorías default disponibles")
        return {
            "parte_a": {
                "nombre": "Documentos Parte A",
                "icono": "📄",
                "descripcion": "Documentos de la primera parte",
                "documentos": []
            },
            "parte_b": {
                "nombre": "Documentos Parte B",
                "icono": "📄",
                "descripcion": "Documentos de la segunda parte",
                "documentos": []
            },
            "otros": {
                "nombre": "Otros Documentos",
                "icono": "📋",
                "descripcion": "Documentación adicional",
                "documentos": []
            }
        }

    logger.info(
        "Categorías cargadas",
        doc_type=document_type,
        parte_a_docs=len(doc_categories.get("parte_a", {}).get("documentos", [])),
        parte_b_docs=len(doc_categories.get("parte_b", {}).get("documentos", [])),
        otros_docs=len(doc_categories.get("otros", {}).get("documentos", []))
    )

    return doc_categories


def get_category_names(document_type: str) -> Dict[str, str]:
    """
    Obtiene solo los nombres de las categorías para un tipo de documento

    Args:
        document_type: Tipo de documento

    Returns:
        Dict: Diccionario con los nombres de cada categoría
    """
    categories = get_categories_for_type(document_type)
    return {
        "parte_a": categories.get("parte_a", {}).get("nombre", "Parte A"),
        "parte_b": categories.get("parte_b", {}).get("nombre", "Parte B"),
        "otros": categories.get("otros", {}).get("nombre", "Otros")
    }


def get_expected_documents(document_type: str, category: str) -> List[str]:
    """
    Obtiene la lista de documentos esperados para una categoría específica

    Args:
        document_type: Tipo de documento
        category: Categoría ('parte_a', 'parte_b', 'otros')

    Returns:
        List[str]: Lista de nombres de documentos esperados
    """
    categories = get_categories_for_type(document_type)
    category_data = categories.get(category, {})
    return category_data.get("documentos", [])


def validate_category(category: str) -> bool:
    """
    Valida que la categoría sea válida

    Args:
        category: Categoría a validar

    Returns:
        bool: True si es válida ('parte_a', 'parte_b', 'otros')
    """
    valid_categories = ["parte_a", "parte_b", "otros"]
    return category.lower() in valid_categories


def get_all_categories() -> List[str]:
    """
    Retorna lista de todas las categorías válidas

    Returns:
        List[str]: ['parte_a', 'parte_b', 'otros']
    """
    return ["parte_a", "parte_b", "otros"]
