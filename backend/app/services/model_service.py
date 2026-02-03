"""
ControlNot v2 - Model Service
Servicio para extraer metadata de campos de los modelos Pydantic

Proporciona campos dinámicamente para el DataEditor del frontend
"""
from typing import Dict, List, Optional, Type
from pydantic import BaseModel
import structlog

from app.models import (
    CompraventaKeys,
    DonacionKeys,
    TestamentoKeys,
    PoderKeys,
    SociedadKeys,
    CancelacionKeys,
)

logger = structlog.get_logger()


# Mapeo de tipos de documento a sus modelos Pydantic
MODEL_MAP: Dict[str, Type[BaseModel]] = {
    "compraventa": CompraventaKeys,
    "donacion": DonacionKeys,
    "testamento": TestamentoKeys,
    "poder": PoderKeys,
    "sociedad": SociedadKeys,
    "cancelacion": CancelacionKeys,
}


# Patrones para categorizar campos automáticamente
CATEGORY_PATTERNS = {
    # Compraventa / Donacion
    "Parte_Vendedora": "Parte Vendedora",
    "Parte_Compradora": "Parte Compradora",
    "Parte_Donadora": "Parte Donadora",
    "Parte_Donataria": "Parte Donataria",

    # Testamento
    "Testador": "Testador",
    "Heredero": "Herederos",
    "Albacea": "Albacea",

    # Poder
    "Poderdante": "Poderdante",
    "Apoderado": "Apoderado",

    # Sociedad
    "Socio": "Socios",
    "Representante": "Representante Legal",
    "Sociedad": "Datos de la Sociedad",

    # Cancelacion
    "Deudor": "Deudor",
    "Acreedor": "Acreedor",
    "Hipoteca": "Datos de Hipoteca",

    # Comunes
    "Escritura_Privada": "Antecedente de Propiedad",
    "Juicio_Sucesorio": "Antecedente (Juicio Sucesorio)",
    "Certificado": "Documentos Oficiales",
    "Constancia": "Documentos Oficiales",
    "Avaluo": "Avalúo",
    "Numero_Registro": "Registro Público",
    "Registro": "Registro Público",
    "Urbano": "Inmueble",
    "Predio": "Inmueble",
    "Valor": "Valores",
    "Precio": "Valores",
    "RFC": "Documentos Fiscales",
    "CURP": "Documentos de Identidad",
    "INE": "Documentos de Identidad",
    "fecha_instrumento": "Datos del Instrumento",
    "lugar_instrumento": "Datos del Instrumento",
    "numero_instrumento": "Datos del Instrumento",
    "notario": "Datos del Instrumento",
    "numero_notaria": "Datos del Instrumento",
}


# Etiquetas legibles para campos comunes
FIELD_LABELS = {
    # Base
    "fecha_instrumento": "Fecha del Instrumento",
    "lugar_instrumento": "Lugar del Instrumento",
    "numero_instrumento": "Número del Instrumento",
    "notario_actuante": "Notario Actuante",
    "numero_notaria": "Número de Notaría",

    # Partes - Vendedor/Comprador
    "Parte_Vendedora_Nombre_Completo": "Nombre Completo del Vendedor",
    "Parte_Compradora_Nombre_Completo": "Nombre Completo del Comprador",
    "Edad_Parte_Vendedora": "Edad del Vendedor",
    "Edad_Parte_Compradora": "Edad del Comprador",

    # Partes - Donador/Donatario
    "Parte_Donadora_Nombre_Completo": "Nombre Completo del Donador",
    "Parte_Donataria_Nombre_Completo": "Nombre Completo del Donatario",
    "Edad_Parte_Donadora": "Edad del Donador",
    "Edad_Parte_Donataria": "Edad del Donatario",

    # Documentos comunes
    "RFC_Parte_Vendedora": "RFC del Vendedor",
    "RFC_Parte_Compradora": "RFC del Comprador",
    "RFC_Parte_Donadora": "RFC del Donador",
    "RFC_Parte_Donataria": "RFC del Donatario",
    "CURP_Parte_Vendedora": "CURP del Vendedor",
    "CURP_Parte_Compradora": "CURP del Comprador",
    "CURP_Parte_Donadora": "CURP del Donador",
    "CURP_Parte_Donataria": "CURP del Donatario",

    # Antecedente
    "Escritura_Privada_numero": "Número de Escritura Antecedente",
    "Escritura_Privada_fecha": "Fecha de Escritura Antecedente",
    "Escritura_Privada_Notario": "Notario del Antecedente",
    "Escritura_Privada_Notario_numero": "Notaría del Antecedente",

    # Juicio Sucesorio (cuando el antecedente es por herencia)
    "Antecedente_Tipo": "Tipo de Antecedente",
    "Juicio_Sucesorio_Tipo": "Tipo de Juicio Sucesorio",
    "Juicio_Sucesorio_Juzgado": "Juzgado del Sucesorio",
    "Juicio_Sucesorio_Expediente": "Expediente del Sucesorio",
    "Juicio_Sucesorio_Causante": "Causante (Finado)",
    "Juicio_Sucesorio_Fecha_Sentencia": "Fecha de Sentencia",
    "Juicio_Sucesorio_Notario_Protocolizacion": "Notario de Protocolización",

    # Inmueble
    "Escritura_Privada_Urbano_Descripcion": "Descripción del Inmueble",
    "Certificado_Registro_Catastral": "Superficie del Inmueble",
}


def categorize_field(field_name: str) -> str:
    """
    Determina la categoría de un campo basándose en su nombre

    Args:
        field_name: Nombre del campo del modelo

    Returns:
        Nombre de la categoría correspondiente
    """
    for pattern, category in CATEGORY_PATTERNS.items():
        if pattern.lower() in field_name.lower():
            return category

    return "Otros Datos"


def get_field_label(field_name: str, description: Optional[str] = None) -> str:
    """
    Genera una etiqueta legible para un campo

    Args:
        field_name: Nombre del campo
        description: Descripción del campo (para extraer info adicional)

    Returns:
        Etiqueta legible para mostrar en UI
    """
    # Primero verificar si hay una etiqueta predefinida
    if field_name in FIELD_LABELS:
        return FIELD_LABELS[field_name]

    # Convertir snake_case a Title Case
    label = field_name.replace("_", " ").title()

    # Limpiar algunos términos comunes
    replacements = {
        "Parte ": "",
        " Parte": "",
        "Urbano ": "",
        "Escritura Privada ": "",
        "Sat ": "SAT ",
        "Ine ": "INE ",
        "Rfc ": "RFC ",
        "Curp ": "CURP ",
    }

    for old, new in replacements.items():
        label = label.replace(old, new)

    return label.strip()


def infer_field_type(field_name: str, field_type: type) -> str:
    """
    Infiere el tipo de input apropiado para un campo

    Args:
        field_name: Nombre del campo
        field_type: Tipo Python del campo

    Returns:
        Tipo de input: 'text', 'textarea', 'date', 'number'
    """
    name_lower = field_name.lower()

    # Campos que deberían ser textarea (texto largo)
    textarea_patterns = [
        "descripcion", "clausulas", "medidas", "domicilio",
        "direccion", "acreditacion", "motivo", "clausula"
    ]

    for pattern in textarea_patterns:
        if pattern in name_lower:
            return "textarea"

    # Campos de fecha
    if "fecha" in name_lower or "dia_nacimiento" in name_lower:
        return "text"  # Usamos text porque las fechas son en palabras

    # Campos numéricos
    if "numero" in name_lower and "telefono" not in name_lower:
        return "text"  # Números en palabras también

    if "precio" in name_lower or "valor" in name_lower or "monto" in name_lower:
        return "text"  # Pueden tener formato especial

    return "text"


def get_short_description(description: Optional[str]) -> Optional[str]:
    """
    Extrae una descripción corta del texto completo

    Args:
        description: Descripción completa del campo

    Returns:
        Descripción resumida (primera línea o primeros 150 caracteres)
    """
    if not description:
        return None

    # Tomar primera línea no vacía
    lines = description.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("==="):
            # Limpiar marcadores y limitar longitud
            clean_line = line.replace("===", "").strip()
            if len(clean_line) > 150:
                return clean_line[:147] + "..."
            return clean_line

    return None


def get_fields_for_document_type(document_type: str) -> Dict:
    """
    Obtiene todos los campos con metadata para un tipo de documento

    Args:
        document_type: Tipo de documento (compraventa, donacion, etc.)

    Returns:
        Dict con campos estructurados para el DataEditor:
        {
            "document_type": "compraventa",
            "fields": [...],
            "categories": [...],
            "total_fields": 51
        }
    """
    logger.info("Obteniendo campos para tipo de documento", document_type=document_type)

    # Obtener el modelo correspondiente
    model_class = MODEL_MAP.get(document_type.lower())

    if not model_class:
        logger.warning("Tipo de documento no encontrado", document_type=document_type)
        return {
            "document_type": document_type,
            "fields": [],
            "categories": [],
            "total_fields": 0,
            "error": f"Tipo de documento '{document_type}' no soportado"
        }

    fields = []
    categories_set = set()

    # Iterar sobre los campos del modelo Pydantic
    for field_name, field_info in model_class.model_fields.items():
        # Obtener descripción del Field
        description = field_info.description if hasattr(field_info, 'description') else None

        # Determinar categoría
        category = categorize_field(field_name)
        categories_set.add(category)

        # Verificar si el campo es opcional (desde json_schema_extra)
        extra = field_info.json_schema_extra or {}
        is_optional_field = extra.get('optional_field', False)
        field_source = extra.get('source', None)

        # Construir metadata del campo
        field_metadata = {
            "name": field_name,
            "label": get_field_label(field_name, description),
            "category": category,
            "type": infer_field_type(field_name, field_info.annotation),
            "required": field_info.is_required() if hasattr(field_info, 'is_required') else False,
            "help": get_short_description(description),
            "optional": is_optional_field,
            "source": field_source,
        }

        fields.append(field_metadata)

    # Ordenar campos: primero por categoría, luego por nombre
    category_order = [
        "Datos del Instrumento",
        "Parte Vendedora", "Parte Compradora",
        "Parte Donadora", "Parte Donataria",
        "Testador", "Herederos", "Albacea",
        "Poderdante", "Apoderado",
        "Deudor", "Acreedor", "Datos de Hipoteca",
        "Socios", "Representante Legal", "Datos de la Sociedad",
        "Antecedente de Propiedad",
        "Antecedente (Juicio Sucesorio)",
        "Inmueble",
        "Documentos de Identidad",
        "Documentos Fiscales",
        "Documentos Oficiales",
        "Valores",
        "Avalúo",
        "Registro Público",
        "Otros Datos",
    ]

    def sort_key(field):
        category = field["category"]
        try:
            cat_idx = category_order.index(category)
        except ValueError:
            cat_idx = len(category_order)
        return (cat_idx, field["name"])

    fields.sort(key=sort_key)

    # Ordenar categorías según el orden definido
    categories = []
    for cat in category_order:
        if cat in categories_set:
            categories.append(cat)
    # Agregar cualquier categoría no prevista
    for cat in categories_set:
        if cat not in categories:
            categories.append(cat)

    result = {
        "document_type": document_type,
        "fields": fields,
        "categories": categories,
        "total_fields": len(fields)
    }

    logger.info(
        "Campos obtenidos exitosamente",
        document_type=document_type,
        total_fields=len(fields),
        categories=len(categories)
    )

    return result


def get_all_document_types_with_fields() -> List[Dict]:
    """
    Obtiene un resumen de todos los tipos de documento con conteo de campos

    Returns:
        Lista de tipos con información básica
    """
    result = []

    for doc_type, model_class in MODEL_MAP.items():
        field_count = len(model_class.model_fields)
        result.append({
            "id": doc_type,
            "name": doc_type.replace("_", " ").title(),
            "total_fields": field_count
        })

    return result
