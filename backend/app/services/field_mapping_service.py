"""
ControlNot v2 - Field Mapping Service
Mapeo inteligente entre datos extraídos y placeholders de template con scoring

Migrado de movil_cancelaciones.py - función map_extracted_to_placeholders()

Este servicio implementa un algoritmo de mapeo basado en similitud de texto
que asigna puntuaciones para encontrar el mejor match entre campos extraídos
y placeholders de templates.
"""
from typing import Dict, List, Tuple, Optional
import re
import unicodedata
import structlog

logger = structlog.get_logger()


# ==========================================
# CONFIGURACIÓN DE SCORING
# ==========================================

MIN_SCORE_THRESHOLD = 3  # Puntuación mínima para considerar un match válido
EXACT_MATCH_SCORE = 10   # Puntos por match exacto
WORD_MATCH_SCORE = 3     # Puntos por cada palabra común
PARTIAL_MATCH_SCORE = 1  # Puntos por match parcial


# ==========================================
# FUNCIONES HELPER
# ==========================================

def normalize_text(text: str) -> str:
    """
    Normaliza texto para comparación: lowercase, sin tildes, sin espacios extra

    Args:
        text: Texto a normalizar

    Returns:
        str: Texto normalizado

    Example:
        >>> normalize_text("Vendedor Nombre Completo")
        "vendedor nombre completo"
        >>> normalize_text("Dirección_Inmueble")
        "direccion inmueble"
    """
    if not text:
        return ""

    # Convertir a lowercase
    text = text.lower()

    # Remover tildes/acentos
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    # Reemplazar underscores y guiones con espacios
    text = text.replace('_', ' ').replace('-', ' ')

    # Remover caracteres especiales (mantener solo alfanuméricos y espacios)
    text = re.sub(r'[^a-z0-9\s]', '', text)

    # Normalizar espacios múltiples
    text = ' '.join(text.split())

    return text


def extract_words(text: str) -> List[str]:
    """
    Extrae palabras individuales de un texto normalizado

    Args:
        text: Texto normalizado

    Returns:
        List[str]: Lista de palabras

    Example:
        >>> extract_words("vendedor nombre completo")
        ["vendedor", "nombre", "completo"]
    """
    return text.split()


def calculate_similarity_score(
    extracted_key: str,
    placeholder: str
) -> int:
    """
    Calcula puntuación de similitud entre un campo extraído y un placeholder

    Algoritmo:
    - Match exacto: 10 puntos
    - Por cada palabra común: 3 puntos
    - Por cada match parcial: 1 punto

    Args:
        extracted_key: Clave del dato extraído (ej: "nombre_vendedor")
        placeholder: Nombre del placeholder (ej: "Vendedor_Nombre_Completo")

    Returns:
        int: Puntuación de similitud (0+ puntos)

    Example:
        >>> calculate_similarity_score("nombre_vendedor", "Vendedor_Nombre_Completo")
        6  # "nombre" (3pts) + "vendedor" (3pts)
        >>> calculate_similarity_score("vendedor_nombre", "Vendedor_Nombre")
        10  # Match exacto después de normalizar
    """
    # Normalizar ambos textos
    norm_extracted = normalize_text(extracted_key)
    norm_placeholder = normalize_text(placeholder)

    score = 0

    # 1. Match exacto = 10 puntos
    if norm_extracted == norm_placeholder:
        score = EXACT_MATCH_SCORE
        logger.debug(
            "Match exacto",
            extracted=extracted_key,
            placeholder=placeholder,
            score=score
        )
        return score

    # 2. Extraer palabras
    extracted_words = extract_words(norm_extracted)
    placeholder_words = extract_words(norm_placeholder)

    # 3. Contar palabras comunes = 3 puntos cada una
    common_words = set(extracted_words) & set(placeholder_words)
    score += len(common_words) * WORD_MATCH_SCORE

    # 4. Verificar matches parciales (subcadenas) = 1 punto
    for ext_word in extracted_words:
        for plc_word in placeholder_words:
            # Si una palabra está contenida en la otra (pero no es match exacto)
            if ext_word != plc_word:
                if ext_word in plc_word or plc_word in ext_word:
                    score += PARTIAL_MATCH_SCORE

    logger.debug(
        "Similitud calculada",
        extracted=extracted_key,
        placeholder=placeholder,
        score=score,
        common_words=len(common_words)
    )

    return score


# ==========================================
# FUNCIONES PRINCIPALES DE MAPEO
# ==========================================

def map_extracted_to_placeholders(
    extracted_data: Dict[str, str],
    placeholders: List[str],
    min_score: int = MIN_SCORE_THRESHOLD
) -> Dict[str, str]:
    """
    Mapea datos extraídos a placeholders de template usando scoring inteligente

    Esta es la función principal que replica la lógica de movil_cancelaciones.py
    pero con mejoras en logging y configurabilidad.

    Algoritmo:
    1. Para cada placeholder, calcular similitud con todos los campos extraídos
    2. Seleccionar el campo con mayor puntuación (si >= min_score)
    3. Evitar duplicados: cada campo extraído se usa solo una vez (mejor match)

    Args:
        extracted_data: Diccionario de datos extraídos {clave: valor}
        placeholders: Lista de nombres de placeholders del template
        min_score: Puntuación mínima para considerar un match válido

    Returns:
        Dict[str, str]: Mapeo {placeholder: valor} para los matches válidos

    Example:
        >>> extracted = {
        ...     "nombre_vendedor": "Juan Pérez",
        ...     "precio": "500000",
        ...     "superficie_terreno": "150 m2"
        ... }
        >>> placeholders = [
        ...     "Vendedor_Nombre_Completo",
        ...     "Precio_Cantidad",
        ...     "Inmueble_Superficie"
        ... ]
        >>> map_extracted_to_placeholders(extracted, placeholders)
        {
            "Vendedor_Nombre_Completo": "Juan Pérez",
            "Precio_Cantidad": "500000",
            "Inmueble_Superficie": "150 m2"
        }
    """
    mapped_data = {}
    used_keys = set()  # Track de keys ya usadas para evitar duplicados

    # Para cada placeholder, encontrar el mejor match
    for placeholder in placeholders:
        best_score = 0
        best_key = None
        best_value = None

        # Comparar con cada campo extraído
        for extracted_key, extracted_value in extracted_data.items():
            # Skip si esta key ya fue usada
            if extracted_key in used_keys:
                continue

            # Skip si el valor está vacío
            if not extracted_value or extracted_value.strip() == "":
                continue

            # Calcular similitud
            score = calculate_similarity_score(extracted_key, placeholder)

            # Actualizar mejor match
            if score > best_score:
                best_score = score
                best_key = extracted_key
                best_value = extracted_value

        # Si encontramos un match válido (>= threshold)
        if best_score >= min_score and best_key:
            mapped_data[placeholder] = best_value
            used_keys.add(best_key)

            logger.info(
                "Mapeo exitoso",
                placeholder=placeholder,
                extracted_key=best_key,
                score=best_score,
                value_preview=best_value[:50] if len(best_value) > 50 else best_value
            )
        else:
            logger.debug(
                "Sin match válido para placeholder",
                placeholder=placeholder,
                best_score=best_score,
                threshold=min_score
            )

    # Estadísticas finales
    total_placeholders = len(placeholders)
    total_mapped = len(mapped_data)
    total_extracted = len(extracted_data)
    mapping_rate = (total_mapped / total_placeholders * 100) if total_placeholders > 0 else 0

    logger.info(
        "Mapeo completado",
        total_placeholders=total_placeholders,
        total_mapped=total_mapped,
        total_extracted=total_extracted,
        mapping_rate=f"{mapping_rate:.1f}%",
        unused_extracted_keys=len(extracted_data) - len(used_keys)
    )

    return mapped_data


def get_mapping_suggestions(
    extracted_data: Dict[str, str],
    placeholders: List[str],
    top_n: int = 3
) -> Dict[str, List[Tuple[str, int]]]:
    """
    Obtiene las top N sugerencias de mapeo para cada placeholder

    Útil para interfaces donde el usuario puede seleccionar manualmente
    entre múltiples opciones.

    Args:
        extracted_data: Datos extraídos
        placeholders: Placeholders del template
        top_n: Número de sugerencias por placeholder

    Returns:
        Dict[str, List[Tuple[str, int]]]: {placeholder: [(key, score), ...]}

    Example:
        >>> suggestions = get_mapping_suggestions(extracted, placeholders, top_n=2)
        >>> suggestions["Vendedor_Nombre_Completo"]
        [("nombre_vendedor", 6), ("vendedor", 3)]
    """
    suggestions = {}

    for placeholder in placeholders:
        scores = []

        for extracted_key in extracted_data.keys():
            score = calculate_similarity_score(extracted_key, placeholder)
            if score > 0:
                scores.append((extracted_key, score))

        # Ordenar por score descendente y tomar top N
        scores.sort(key=lambda x: x[1], reverse=True)
        suggestions[placeholder] = scores[:top_n]

    return suggestions


def get_unmapped_fields(
    extracted_data: Dict[str, str],
    placeholders: List[str],
    min_score: int = MIN_SCORE_THRESHOLD
) -> Dict[str, List[str]]:
    """
    Identifica campos extraídos y placeholders que no pudieron mapearse

    Args:
        extracted_data: Datos extraídos
        placeholders: Placeholders del template
        min_score: Threshold de puntuación

    Returns:
        Dict con keys 'unmapped_extracted' y 'unmapped_placeholders'

    Example:
        >>> unmapped = get_unmapped_fields(extracted, placeholders)
        >>> unmapped["unmapped_extracted"]
        ["campo_desconocido", "otro_campo"]
        >>> unmapped["unmapped_placeholders"]
        ["Placeholder_Sin_Datos"]
    """
    mapped = map_extracted_to_placeholders(extracted_data, placeholders, min_score)

    unmapped_extracted = [
        key for key in extracted_data.keys()
        if key not in [
            k for k, _ in [(key, value) for key, value in extracted_data.items()
                          if any(mapped.get(p) == value for p in placeholders)]
        ]
    ]

    unmapped_placeholders = [
        p for p in placeholders
        if p not in mapped
    ]

    logger.info(
        "Campos sin mapear",
        unmapped_extracted_count=len(unmapped_extracted),
        unmapped_placeholders_count=len(unmapped_placeholders)
    )

    return {
        "unmapped_extracted": unmapped_extracted,
        "unmapped_placeholders": unmapped_placeholders
    }


def validate_mapping(
    mapped_data: Dict[str, str],
    required_placeholders: List[str]
) -> Tuple[bool, List[str]]:
    """
    Valida que todos los placeholders requeridos tengan valores

    Args:
        mapped_data: Datos ya mapeados
        required_placeholders: Lista de placeholders obligatorios

    Returns:
        Tuple[bool, List[str]]: (es_válido, placeholders_faltantes)

    Example:
        >>> is_valid, missing = validate_mapping(
        ...     mapped_data,
        ...     ["Vendedor_Nombre", "Precio_Cantidad"]
        ... )
        >>> if not is_valid:
        ...     print(f"Faltan: {missing}")
    """
    missing = [
        p for p in required_placeholders
        if p not in mapped_data or not mapped_data[p]
    ]

    is_valid = len(missing) == 0

    if not is_valid:
        logger.warning(
            "Validación de mapeo fallida",
            missing_placeholders=missing,
            total_missing=len(missing)
        )

    return is_valid, missing


# ==========================================
# EXAMPLE USAGE
# ==========================================

if __name__ == "__main__":
    # Test con datos de ejemplo
    extracted_data = {
        "nombre_completo_vendedor": "JUAN PÉREZ GARCÍA",
        "rfc_vendedor": "PEGJ860101AAA",
        "nombre_comprador": "MARÍA GONZÁLEZ LÓPEZ",
        "precio_total": "quinientos mil pesos 00/100 M.N.",
        "superficie_terreno": "150.00 metros cuadrados",
        "superficie_construccion": "120.00 metros cuadrados",
        "direccion_inmueble": "Calle Morelos número 123",
        "numero_escritura": "mil doscientos treinta y cuatro",
        "fecha_escritura": "quince de marzo de dos mil veinticuatro",
        "campo_extra_no_usado": "valor que no matchea"
    }

    placeholders = [
        "Vendedor_Nombre_Completo",
        "Vendedor_RFC",
        "Comprador_Nombre_Completo",
        "Precio_Cantidad",
        "Inmueble_Superficie_Terreno",
        "Inmueble_Superficie_Construccion",
        "Inmueble_Direccion",
        "Escritura_Numero",
        "Escritura_Fecha",
        "Notario_Actuante",  # No tiene match
        "Numero_Notaria"      # No tiene match
    ]

    print("🔗 Test de Mapeo Inteligente de Campos\n")

    # Realizar mapeo
    mapped = map_extracted_to_placeholders(extracted_data, placeholders)

    # Mostrar resultados
    print(f"📊 Resultados del Mapeo:")
    print(f"   Placeholders totales: {len(placeholders)}")
    print(f"   Campos extraídos: {len(extracted_data)}")
    print(f"   Campos mapeados: {len(mapped)}")
    print(f"   Tasa de mapeo: {len(mapped)/len(placeholders)*100:.1f}%\n")

    print("✅ Mapeos exitosos:")
    for placeholder, value in mapped.items():
        value_preview = value[:40] + "..." if len(value) > 40 else value
        print(f"   {placeholder} → {value_preview}")

    # Identificar no mapeados
    unmapped = get_unmapped_fields(extracted_data, placeholders)

    if unmapped["unmapped_placeholders"]:
        print(f"\n❌ Placeholders sin datos:")
        for p in unmapped["unmapped_placeholders"]:
            print(f"   - {p}")

    if unmapped["unmapped_extracted"]:
        print(f"\n⚠️ Campos extraídos no usados:")
        for key in unmapped["unmapped_extracted"]:
            print(f"   - {key}")

    # Test de sugerencias
    print(f"\n💡 Sugerencias para placeholders sin match:")
    suggestions = get_mapping_suggestions(
        extracted_data,
        unmapped["unmapped_placeholders"],
        top_n=2
    )
    for placeholder, suggs in suggestions.items():
        if suggs:
            print(f"   {placeholder}:")
            for key, score in suggs:
                print(f"      - {key} (score: {score})")
