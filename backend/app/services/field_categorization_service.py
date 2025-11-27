"""
ControlNot v2 - Field Categorization Service
Categorización inteligente de placeholders de templates por tipo semántico

Migrado de movil_cancelaciones.py - función categorize_fields()

Este servicio categoriza los placeholders de un template en categorías semánticas
basándose en palabras clave, facilitando la organización y el mapeo de datos.
"""
from typing import Dict, List
import structlog

logger = structlog.get_logger()


# ==========================================
# CATEGORÍAS Y KEYWORDS
# ==========================================

FIELD_CATEGORIES = {
    "Personas": [
        "Nombre", "nombre", "NOMBRE",
        "RFC", "rfc", "Rfc",
        "CURP", "curp", "Curp",
        "Vendedor", "vendedor", "VENDEDOR",
        "Comprador", "comprador", "COMPRADOR",
        "Donador", "donador", "DONADOR",
        "Donatario", "donatario", "DONATARIO",
        "Deudor", "deudor", "DEUDOR",
        "Acreedor", "acreedor", "ACREEDOR",
        "Testador", "testador", "TESTADOR",
        "Otorgante", "otorgante", "OTORGANTE",
        "Apoderado", "apoderado", "APODERADO",
        "Representante", "representante", "REPRESENTANTE",
        "Socio", "socio", "SOCIO",
        "Propietario", "propietario", "PROPIETARIO",
        "Estado_Civil", "estado_civil", "Estado civil",
        "Domicilio", "domicilio", "DOMICILIO",
        "Nacionalidad", "nacionalidad", "NACIONALIDAD",
        "Edad", "edad", "EDAD",
        "Ocupación", "ocupacion", "OCUPACION",
    ],
    "Inmueble": [
        "Inmueble", "inmueble", "INMUEBLE",
        "Propiedad", "propiedad", "PROPIEDAD",
        "Terreno", "terreno", "TERRENO",
        "Casa", "casa", "CASA",
        "Departamento", "departamento", "DEPARTAMENTO",
        "Superficie", "superficie", "SUPERFICIE",
        "Metros", "metros", "METROS",
        "Dirección", "direccion", "DIRECCION",
        "Ubicación", "ubicacion", "UBICACION",
        "Calle", "calle", "CALLE",
        "Colonia", "colonia", "COLONIA",
        "Municipio", "municipio", "MUNICIPIO",
        "Estado", "estado", "ESTADO",
        "Código_Postal", "codigo_postal", "CP",
        "Colindancias", "colindancias", "COLINDANCIAS",
        "Norte", "norte", "NORTE",
        "Sur", "sur", "SUR",
        "Oriente", "oriente", "ORIENTE",
        "Poniente", "poniente", "PONIENTE",
        "Tipo", "tipo", "TIPO",
    ],
    "Documentos": [
        "Escritura", "escritura", "ESCRITURA",
        "Instrumento", "instrumento", "INSTRUMENTO",
        "Numero", "numero", "NUMERO", "Número",
        "Fecha", "fecha", "FECHA",
        "Notario", "notario", "NOTARIO",
        "Notaria", "notaria", "NOTARIA",
        "Folio", "folio", "FOLIO",
        "Partida", "partida", "PARTIDA",
        "Registro", "registro", "REGISTRO",
        "Inscripción", "inscripcion", "INSCRIPCION",
        "Volumen", "volumen", "VOLUMEN",
        "Libro", "libro", "LIBRO",
        "Sección", "seccion", "SECCION",
        "Antecedente", "antecedente", "ANTECEDENTE",
        "RPP", "rpp", "Rpp",
        "Certificado", "certificado", "CERTIFICADO",
        "Constancia", "constancia", "CONSTANCIA",
        "Finiquito", "finiquito", "FINIQUITO",
        "Poder", "poder", "PODER",
        "Testamento", "testamento", "TESTAMENTO",
    ],
    "Financiero": [
        "Precio", "precio", "PRECIO",
        "Monto", "monto", "MONTO",
        "Valor", "valor", "VALOR",
        "Cantidad", "cantidad", "CANTIDAD",
        "Pesos", "pesos", "PESOS",
        "Credito", "credito", "CREDITO", "Crédito",
        "Cuenta", "cuenta", "CUENTA",
        "Adeudo", "adeudo", "ADEUDO",
        "Liquidación", "liquidacion", "LIQUIDACION",
        "Pago", "pago", "PAGO",
        "Enganche", "enganche", "ENGANCHE",
        "Saldo", "saldo", "SALDO",
        "Banco", "banco", "BANCO",
        "Hipoteca", "hipoteca", "HIPOTECA",
        "Gravamen", "gravamen", "GRAVAMEN",
    ],
    "Otros": [
        # Catch-all para campos que no matchean las otras categorías
        "Observaciones", "observaciones", "OBSERVACIONES",
        "Notas", "notas", "NOTAS",
        "Comentarios", "comentarios", "COMENTARIOS",
        "Adicional", "adicional", "ADICIONAL",
        "Extra", "extra", "EXTRA",
        "Otros", "otros", "OTROS",
    ]
}


# ==========================================
# FUNCIONES DE CATEGORIZACIÓN
# ==========================================

def categorize_field(field_name: str) -> str:
    """
    Categoriza un solo placeholder basándose en palabras clave

    Args:
        field_name: Nombre del placeholder (ej: "Vendedor_Nombre_Completo")

    Returns:
        str: Categoría asignada ("Personas", "Inmueble", "Documentos", "Financiero", "Otros")

    Example:
        >>> categorize_field("Vendedor_Nombre_Completo")
        "Personas"
        >>> categorize_field("Inmueble_Superficie")
        "Inmueble"
        >>> categorize_field("Escritura_Numero")
        "Documentos"
    """
    # Verificar cada categoría
    for category, keywords in FIELD_CATEGORIES.items():
        for keyword in keywords:
            if keyword in field_name:
                logger.debug(
                    "Campo categorizado",
                    field=field_name,
                    category=category,
                    keyword_matched=keyword
                )
                return category

    # Si no matchea ninguna categoría, va a "Otros"
    logger.debug(
        "Campo sin categoría específica, asignado a Otros",
        field=field_name
    )
    return "Otros"


def categorize_fields(placeholders: List[str]) -> Dict[str, List[str]]:
    """
    Categoriza una lista de placeholders en categorías semánticas

    Esta función replica la lógica de movil_cancelaciones.py pero de forma
    más robusta y con logging.

    Args:
        placeholders: Lista de nombres de placeholders del template

    Returns:
        Dict[str, List[str]]: Diccionario con categorías como keys y listas de
                              placeholders como values

    Example:
        >>> placeholders = [
        ...     "Vendedor_Nombre_Completo",
        ...     "Inmueble_Superficie",
        ...     "Precio_Cantidad"
        ... ]
        >>> categorize_fields(placeholders)
        {
            "Personas": ["Vendedor_Nombre_Completo"],
            "Inmueble": ["Inmueble_Superficie"],
            "Financiero": ["Precio_Cantidad"],
            "Documentos": [],
            "Otros": []
        }
    """
    # Inicializar categorías vacías
    categories = {
        "Personas": [],
        "Inmueble": [],
        "Documentos": [],
        "Financiero": [],
        "Otros": []
    }

    # Categorizar cada placeholder
    for placeholder in placeholders:
        category = categorize_field(placeholder)
        categories[category].append(placeholder)

    # Log estadísticas
    total_fields = len(placeholders)
    stats = {cat: len(fields) for cat, fields in categories.items()}

    logger.info(
        "Placeholders categorizados",
        total_placeholders=total_fields,
        personas=stats["Personas"],
        inmueble=stats["Inmueble"],
        documentos=stats["Documentos"],
        financiero=stats["Financiero"],
        otros=stats["Otros"]
    )

    # Filtrar categorías vacías para respuesta más limpia (opcional)
    # categories = {k: v for k, v in categories.items() if v}

    return categories


def get_category_stats(placeholders: List[str]) -> Dict[str, int]:
    """
    Obtiene estadísticas de categorización sin devolver los placeholders

    Args:
        placeholders: Lista de nombres de placeholders

    Returns:
        Dict[str, int]: Conteo de placeholders por categoría

    Example:
        >>> get_category_stats(["Vendedor_Nombre", "Inmueble_Tipo"])
        {"Personas": 1, "Inmueble": 1, "Documentos": 0, "Financiero": 0, "Otros": 0}
    """
    categorized = categorize_fields(placeholders)
    return {cat: len(fields) for cat, fields in categorized.items()}


def get_placeholders_by_category(
    placeholders: List[str],
    category: str
) -> List[str]:
    """
    Obtiene solo los placeholders de una categoría específica

    Args:
        placeholders: Lista de placeholders
        category: Categoría deseada ("Personas", "Inmueble", etc.)

    Returns:
        List[str]: Placeholders que pertenecen a esa categoría

    Example:
        >>> placeholders = ["Vendedor_Nombre", "Inmueble_Tipo", "Comprador_RFC"]
        >>> get_placeholders_by_category(placeholders, "Personas")
        ["Vendedor_Nombre", "Comprador_RFC"]
    """
    categorized = categorize_fields(placeholders)
    return categorized.get(category, [])


def add_custom_keyword(category: str, keyword: str) -> bool:
    """
    Agrega una palabra clave custom a una categoría

    Args:
        category: Categoría destino
        keyword: Palabra clave a agregar

    Returns:
        bool: True si se agregó exitosamente

    Example:
        >>> add_custom_keyword("Personas", "Beneficiario")
        True
    """
    if category not in FIELD_CATEGORIES:
        logger.error("Categoría no válida", category=category)
        return False

    if keyword not in FIELD_CATEGORIES[category]:
        FIELD_CATEGORIES[category].append(keyword)
        logger.info(
            "Keyword custom agregada",
            category=category,
            keyword=keyword
        )
        return True

    logger.warning(
        "Keyword ya existe en categoría",
        category=category,
        keyword=keyword
    )
    return False


# ==========================================
# UTILIDADES
# ==========================================

def get_all_categories() -> List[str]:
    """
    Obtiene lista de todas las categorías disponibles

    Returns:
        List[str]: Nombres de categorías

    Example:
        >>> get_all_categories()
        ["Personas", "Inmueble", "Documentos", "Financiero", "Otros"]
    """
    return list(FIELD_CATEGORIES.keys())


def get_keywords_for_category(category: str) -> List[str]:
    """
    Obtiene todas las palabras clave de una categoría

    Args:
        category: Nombre de la categoría

    Returns:
        List[str]: Lista de palabras clave

    Example:
        >>> keywords = get_keywords_for_category("Personas")
        >>> "Vendedor" in keywords
        True
    """
    return FIELD_CATEGORIES.get(category, [])


# ==========================================
# EXAMPLE USAGE
# ==========================================

if __name__ == "__main__":
    # Test con placeholders de ejemplo
    test_placeholders = [
        "Vendedor_Nombre_Completo",
        "Vendedor_RFC",
        "Comprador_Nombre_Completo",
        "Inmueble_Superficie",
        "Inmueble_Direccion",
        "Inmueble_Colindancias_Norte",
        "Escritura_Numero",
        "Escritura_Fecha",
        "Notario_Actuante",
        "Precio_Cantidad",
        "Monto_Credito_Original",
        "Observaciones"
    ]

    print("🏷️ Test de Categorización de Campos\n")

    # Categorizar
    categorized = categorize_fields(test_placeholders)

    # Mostrar resultados
    for category, fields in categorized.items():
        if fields:
            print(f"\n📁 {category} ({len(fields)} campos):")
            for field in fields:
                print(f"   - {field}")

    # Estadísticas
    print("\n📊 Estadísticas:")
    stats = get_category_stats(test_placeholders)
    for cat, count in stats.items():
        if count > 0:
            print(f"   {cat}: {count} campos")

    # Test de categoría individual
    print("\n🔍 Test de campo individual:")
    test_field = "Deudor_CURP"
    category = categorize_field(test_field)
    print(f"   '{test_field}' → {category}")
