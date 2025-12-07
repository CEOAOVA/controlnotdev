"""
ControlNot v2 - Classification Service
Auto-detecta el tipo de documento basándose en placeholders y nombre del template

MEJORAS v2:
- Keywords expandidas de escrituras.py (legacy)
- Confidence score (0.0 - 1.0)
- Flag requires_confirmation para UI
- Soporte para cancelacion de hipotecas
- Re-detección con contenido OCR

Migrado de por_partes.py líneas 1388-1416
"""
from typing import List, Dict, Optional, TypedDict
import structlog

logger = structlog.get_logger()


# Keywords mejoradas por tipo de documento
# Basado en escrituras.py para máxima precisión
DOCUMENT_KEYWORDS = {
    "compraventa": [
        "vendedor", "vendedora", "comprador", "compradora",
        "precio", "venta", "compraventa", "adquirir",
        "enajenar", "transmitir", "inmueble", "propiedad",
        "escritura_venta", "precio_venta"
    ],
    "donacion": [
        "donante", "donataria", "donatario", "donacion",
        "donadora", "donador", "parentezco", "liberalidad",
        "gratuito", "sin_contraprestacion", "afecto", "familiar"
    ],
    "testamento": [
        "testador", "testadora", "heredero", "heredera",
        "legatario", "albacea", "testamento", "disposicion",
        "ultima_voluntad", "sucesion", "legado", "intestado"
    ],
    "poder": [
        "otorgante", "apoderado", "apoderada", "poder",
        "facultades", "representacion", "mandato", "sustituir",
        "revocar", "poderdante", "general", "especial"
    ],
    "sociedad": [
        "sociedad", "socio", "socia", "capital", "denominacion",
        "administrador", "accionista", "consejo", "asamblea",
        "razon_social", "objeto_social", "estatutos", "constitucion"
    ],
    "cancelacion": [
        "hipoteca", "cancelacion", "cancelar", "gravamen",
        "acreedor", "deudor", "liberacion", "credito",
        "garantia", "registro", "inscripcion", "carta_liberacion"
    ]
}

# Umbrales de confianza
CONFIDENCE_THRESHOLD_HIGH = 0.7  # > 70% = confianza alta
CONFIDENCE_THRESHOLD_LOW = 0.4   # < 40% = requiere confirmación


class DetectionResult(TypedDict):
    """Estructura de resultado de detección"""
    detected_type: str
    confidence_score: float
    all_scores: Dict[str, float]
    requires_confirmation: bool
    detection_method: str


def detect_document_type(
    template_placeholders: List[str],
    template_name: str = "",
    ocr_text: Optional[str] = None
) -> DetectionResult:
    """
    Detecta automáticamente el tipo de documento con confidence score

    Args:
        template_placeholders: Lista de placeholders encontrados en el template
        template_name: Nombre del archivo del template (opcional)
        ocr_text: Texto extraído por OCR para re-detección (opcional)

    Returns:
        DetectionResult: Dict con detected_type, confidence_score, all_scores,
                        requires_confirmation, detection_method

    Example:
        >>> placeholders = ["Vendedor_Nombre", "Comprador_Nombre", "Precio_Venta"]
        >>> result = detect_document_type(placeholders)
        >>> result['detected_type']
        'compraventa'
        >>> result['confidence_score']
        0.85
    """
    scores: Dict[str, float] = {}

    # Preparar textos para análisis
    placeholders_text = " ".join(template_placeholders).lower()
    template_name_lower = template_name.lower() if template_name else ""

    # Texto combinado para análisis
    combined_text = placeholders_text
    if ocr_text:
        combined_text += " " + ocr_text.lower()[:5000]  # Limitar a 5000 chars

    detection_method = "placeholders"
    if ocr_text:
        detection_method = "placeholders+ocr"

    # Calcular score para cada tipo
    max_possible_score = 0
    for doc_type, keywords_list in DOCUMENT_KEYWORDS.items():
        score = 0
        keyword_matches = 0

        for keyword in keywords_list:
            # Mayor peso a matches en placeholders
            if keyword in placeholders_text:
                score += 3
                keyword_matches += 1
            # Peso medio a matches en nombre del template
            elif keyword in template_name_lower:
                score += 2
                keyword_matches += 1
            # Peso menor a matches en OCR text
            elif ocr_text and keyword in ocr_text.lower():
                score += 1
                keyword_matches += 1

        # Normalizar score a 0-1
        max_score_for_type = len(keywords_list) * 3  # Máximo posible
        normalized_score = score / max_score_for_type if max_score_for_type > 0 else 0

        # Bonus por múltiples matches (indica mayor certeza)
        if keyword_matches >= 3:
            normalized_score = min(1.0, normalized_score * 1.2)

        scores[doc_type] = round(normalized_score, 3)

        if max_score_for_type > max_possible_score:
            max_possible_score = max_score_for_type

    # Encontrar mejor tipo
    if scores:
        best_type = max(scores.items(), key=lambda x: x[1])
        detected_type = best_type[0]
        confidence_score = best_type[1]

        # Verificar si hay empate o scores muy cercanos
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_scores) > 1:
            diff = sorted_scores[0][1] - sorted_scores[1][1]
            if diff < 0.1:  # Diferencia < 10%
                confidence_score *= 0.8  # Reducir confianza

        # Determinar si requiere confirmación
        requires_confirmation = confidence_score < CONFIDENCE_THRESHOLD_HIGH

        logger.info(
            "Tipo de documento detectado",
            doc_type=detected_type,
            confidence=f"{confidence_score * 100:.1f}%",
            requires_confirmation=requires_confirmation,
            method=detection_method,
            template_name=template_name,
            all_scores={k: f"{v*100:.1f}%" for k, v in sorted_scores[:3]}
        )

        return {
            "detected_type": detected_type,
            "confidence_score": round(confidence_score, 3),
            "all_scores": scores,
            "requires_confirmation": requires_confirmation,
            "detection_method": detection_method
        }

    # Default si no hay scores (no debería ocurrir)
    logger.warning(
        "No se pudo detectar tipo de documento, usando default",
        template_name=template_name,
        placeholders_count=len(template_placeholders)
    )
    return {
        "detected_type": "compraventa",
        "confidence_score": 0.0,
        "all_scores": scores,
        "requires_confirmation": True,
        "detection_method": "default"
    }


def detect_document_type_simple(
    template_placeholders: List[str],
    template_name: str = ""
) -> str:
    """
    Versión simplificada que retorna solo el tipo (compatibilidad)

    Args:
        template_placeholders: Lista de placeholders
        template_name: Nombre del template

    Returns:
        str: Tipo de documento detectado
    """
    result = detect_document_type(template_placeholders, template_name)
    return result["detected_type"]


def redetect_with_ocr(
    original_detection: DetectionResult,
    ocr_text: str,
    placeholders: List[str]
) -> DetectionResult:
    """
    Re-detecta el tipo de documento usando contenido OCR

    Útil cuando la detección inicial tuvo baja confianza

    Args:
        original_detection: Resultado de detección original
        ocr_text: Texto extraído por OCR
        placeholders: Placeholders originales

    Returns:
        DetectionResult: Nueva detección o original si no mejora
    """
    if original_detection["confidence_score"] >= CONFIDENCE_THRESHOLD_HIGH:
        # Ya tiene alta confianza, no re-detectar
        return original_detection

    # Re-detectar con OCR
    new_detection = detect_document_type(
        placeholders,
        template_name="",
        ocr_text=ocr_text
    )

    # Solo usar nueva detección si mejora confianza
    if new_detection["confidence_score"] > original_detection["confidence_score"]:
        logger.info(
            "Re-detección mejoró confianza",
            original_type=original_detection["detected_type"],
            original_confidence=f"{original_detection['confidence_score']*100:.1f}%",
            new_type=new_detection["detected_type"],
            new_confidence=f"{new_detection['confidence_score']*100:.1f}%"
        )
        return new_detection

    return original_detection


def get_document_type_display_name(doc_type: str) -> str:
    """
    Obtiene el nombre de display para un tipo de documento

    Args:
        doc_type: Tipo de documento

    Returns:
        str: Nombre amigable del tipo de documento
    """
    display_names = {
        "compraventa": "Compraventa",
        "donacion": "Donación",
        "testamento": "Testamento",
        "poder": "Poder Notarial",
        "sociedad": "Constitución de Sociedad",
        "cancelacion": "Cancelación de Hipoteca"
    }

    return display_names.get(doc_type, doc_type.capitalize())


def validate_document_type(doc_type: str) -> bool:
    """
    Valida que el tipo de documento sea válido

    Args:
        doc_type: Tipo de documento a validar

    Returns:
        bool: True si es válido
    """
    valid_types = list(DOCUMENT_KEYWORDS.keys())
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
        {"id": "sociedad", "nombre": "Constitución de Sociedad"},
        {"id": "cancelacion", "nombre": "Cancelación de Hipoteca"}
    ]


def get_keywords_for_type(doc_type: str) -> List[str]:
    """
    Retorna las keywords para un tipo de documento

    Args:
        doc_type: Tipo de documento

    Returns:
        List[str]: Lista de keywords
    """
    return DOCUMENT_KEYWORDS.get(doc_type.lower(), [])
