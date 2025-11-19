"""
ControlNot v2 - Mapping Service
Mapea placeholders de templates a claves estandarizadas de modelos Pydantic

Migrado de por_partes.py líneas 1424-1456
"""
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import structlog

from app.models.base import BaseKeys
from app.models.compraventa import CompraventaKeys
from app.models.donacion import DonacionKeys
from app.models.testamento import TestamentoKeys
from app.models.poder import PoderKeys
from app.models.sociedad import SociedadKeys

logger = structlog.get_logger()


class PlaceholderMapper:
    """
    Mapea placeholders de templates a claves estandarizadas

    Algoritmo de scoring:
    1. Match exacto (case-insensitive): 100 puntos
    2. Palabras en común: 15 puntos por palabra
    3. Fuzzy matching con SequenceMatcher: hasta 30 puntos
    4. Umbral mínimo: 25 puntos

    Example:
        Placeholder: "Vendedor_Nombre_Completo"
        Standard Key: "Vendedor_Nombre"
        Score: 15 (Vendedor) + 15 (Nombre) + fuzzy bonus = ~45 puntos ✓
    """

    # Constantes de scoring
    EXACT_MATCH_SCORE = 100
    WORD_MATCH_MULTIPLIER = 15
    FUZZY_MAX_BONUS = 30
    MIN_MATCH_THRESHOLD = 25

    # Mapeo de tipos de documento a modelos Pydantic
    MODEL_MAP = {
        "compraventa": CompraventaKeys,
        "donacion": DonacionKeys,
        "testamento": TestamentoKeys,
        "poder": PoderKeys,
        "sociedad": SociedadKeys
    }

    @staticmethod
    def _get_standard_keys_for_type(document_type: str) -> List[str]:
        """
        Obtiene las claves estándar del modelo Pydantic para un tipo de documento

        Args:
            document_type: Tipo de documento ('compraventa', 'donacion', etc.)

        Returns:
            List[str]: Lista de nombres de campos del modelo
        """
        model_class = PlaceholderMapper.MODEL_MAP.get(document_type)

        if not model_class:
            logger.warning(
                "Tipo de documento no encontrado, usando BaseKeys",
                doc_type=document_type
            )
            model_class = BaseKeys

        # Obtener campos del modelo Pydantic
        standard_keys = list(model_class.model_fields.keys())

        logger.debug(
            "Claves estándar obtenidas del modelo",
            doc_type=document_type,
            model=model_class.__name__,
            total_keys=len(standard_keys)
        )

        return standard_keys

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normaliza texto para comparación (lowercase, sin espacios extra)

        Args:
            text: Texto a normalizar

        Returns:
            str: Texto normalizado
        """
        return text.lower().strip()

    @staticmethod
    def _extract_words(text: str) -> set:
        """
        Extrae palabras de un texto (separadas por _, -, espacio)

        Args:
            text: Texto del cual extraer palabras

        Returns:
            set: Set de palabras normalizadas
        """
        # Reemplazar separadores con espacios
        for sep in ['_', '-', ' ']:
            text = text.replace(sep, ' ')

        # Dividir y normalizar
        words = set(word.lower().strip() for word in text.split() if word.strip())

        return words

    @staticmethod
    def _calculate_similarity(placeholder: str, standard_key: str) -> int:
        """
        Calcula score de similitud entre placeholder y clave estándar

        Args:
            placeholder: Placeholder del template
            standard_key: Clave estándar del modelo

        Returns:
            int: Score de similitud (0-130+)
        """
        score = 0

        # Normalizar ambos textos
        placeholder_norm = PlaceholderMapper._normalize_text(placeholder)
        standard_norm = PlaceholderMapper._normalize_text(standard_key)

        # 1. Match exacto: 100 puntos
        if placeholder_norm == standard_norm:
            return PlaceholderMapper.EXACT_MATCH_SCORE

        # 2. Palabras en común: 15 puntos por palabra
        placeholder_words = PlaceholderMapper._extract_words(placeholder)
        standard_words = PlaceholderMapper._extract_words(standard_key)
        common_words = placeholder_words & standard_words

        score += len(common_words) * PlaceholderMapper.WORD_MATCH_MULTIPLIER

        # 3. Fuzzy matching con SequenceMatcher (hasta 30 puntos)
        ratio = SequenceMatcher(None, placeholder_norm, standard_norm).ratio()
        fuzzy_bonus = int(ratio * PlaceholderMapper.FUZZY_MAX_BONUS)
        score += fuzzy_bonus

        return score

    @staticmethod
    def map_placeholders_to_keys(
        template_placeholders: List[str],
        document_type: str,
        template_name: str = ""
    ) -> Dict[str, str]:
        """
        Mapea placeholders de template a claves estandarizadas del modelo

        Args:
            template_placeholders: Lista de placeholders encontrados en el template
            document_type: Tipo de documento ('compraventa', 'donacion', etc.)
            template_name: Nombre del template (opcional, para logging)

        Returns:
            Dict[str, str]: Mapeo de {placeholder: standard_key}
                           Si no hay match, placeholder se mapea a sí mismo

        Example:
            >>> placeholders = ["Vendedor_Nombre", "Comprador_Apellido", "Precio"]
            >>> mapping = map_placeholders_to_keys(placeholders, "compraventa")
            >>> mapping
            {
                'Vendedor_Nombre': 'Vendedor_Nombre',
                'Comprador_Apellido': 'Comprador_Apellido_Paterno',
                'Precio': 'Precio_Venta'
            }
        """
        # Obtener claves estándar del modelo
        standard_keys = PlaceholderMapper._get_standard_keys_for_type(document_type)

        mapping = {}
        unmatched_count = 0

        for placeholder in template_placeholders:
            best_match = None
            best_score = 0

            # Calcular score contra todas las claves estándar
            for standard_key in standard_keys:
                score = PlaceholderMapper._calculate_similarity(placeholder, standard_key)

                if score > best_score:
                    best_score = score
                    best_match = standard_key

            # Solo aceptar match si supera el umbral
            if best_score >= PlaceholderMapper.MIN_MATCH_THRESHOLD:
                mapping[placeholder] = best_match
                logger.debug(
                    "Placeholder mapeado",
                    placeholder=placeholder,
                    standard_key=best_match,
                    score=best_score
                )
            else:
                # Sin match: mapear a sí mismo
                mapping[placeholder] = placeholder
                unmatched_count += 1
                logger.debug(
                    "Placeholder sin match, usando nombre original",
                    placeholder=placeholder,
                    best_score=best_score,
                    threshold=PlaceholderMapper.MIN_MATCH_THRESHOLD
                )

        logger.info(
            "Mapeo de placeholders completado",
            doc_type=document_type,
            template_name=template_name,
            total_placeholders=len(template_placeholders),
            mapped=len(template_placeholders) - unmatched_count,
            unmatched=unmatched_count
        )

        return mapping

    @staticmethod
    def get_mapping_statistics(mapping: Dict[str, str]) -> Dict:
        """
        Calcula estadísticas sobre un mapeo de placeholders

        Args:
            mapping: Diccionario de {placeholder: standard_key}

        Returns:
            Dict: Estadísticas del mapeo
        """
        total = len(mapping)
        # Placeholders que se mapearon a sí mismos (sin match)
        self_mapped = sum(1 for p, k in mapping.items() if p == k)
        # Placeholders que se mapearon a una clave diferente
        mapped = total - self_mapped

        return {
            "total_placeholders": total,
            "successfully_mapped": mapped,
            "unmapped": self_mapped,
            "mapping_rate": (mapped / total * 100) if total > 0 else 0
        }


def map_placeholders_to_keys_by_type(
    template_placeholders: List[str],
    document_type: str,
    template_name: str = ""
) -> Dict[str, str]:
    """
    Función pública para mapear placeholders a claves estándar

    Esta es la función principal que debe usarse desde otros módulos.
    Wrapper sobre PlaceholderMapper.map_placeholders_to_keys()

    Args:
        template_placeholders: Lista de placeholders del template
        document_type: Tipo de documento
        template_name: Nombre del template (opcional)

    Returns:
        Dict[str, str]: Mapeo de placeholders a claves estándar

    Example:
        >>> from app.services.mapping_service import map_placeholders_to_keys_by_type
        >>> placeholders = ["Vendedor_Nombre", "Precio"]
        >>> mapping = map_placeholders_to_keys_by_type(placeholders, "compraventa")
    """
    return PlaceholderMapper.map_placeholders_to_keys(
        template_placeholders,
        document_type,
        template_name
    )


def validate_mapping_quality(mapping: Dict[str, str], min_rate: float = 0.5) -> Tuple[bool, Dict]:
    """
    Valida la calidad de un mapeo de placeholders

    Args:
        mapping: Diccionario de mapeo
        min_rate: Tasa mínima de mapeo exitoso (0.0-1.0)

    Returns:
        Tuple[bool, Dict]: (es_válido, estadísticas)
    """
    stats = PlaceholderMapper.get_mapping_statistics(mapping)
    mapping_rate = stats["mapping_rate"] / 100  # Convertir a 0.0-1.0

    is_valid = mapping_rate >= min_rate

    if not is_valid:
        logger.warning(
            "Calidad de mapeo por debajo del umbral",
            mapping_rate=f"{stats['mapping_rate']:.1f}%",
            required_rate=f"{min_rate * 100:.1f}%",
            unmapped_count=stats["unmapped"]
        )

    return is_valid, stats
