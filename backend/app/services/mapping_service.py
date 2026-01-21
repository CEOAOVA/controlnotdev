"""
ControlNot v2 - Mapping Service
Mapea placeholders de templates a claves estandarizadas de modelos Pydantic

Migrado de por_partes.py líneas 1424-1456
Mejorado con sistema de aliases + fuzzy semántico
"""
from typing import List, Dict, Tuple, Type
from difflib import SequenceMatcher
import structlog

from app.models.base import BaseKeys
from app.models.compraventa import CompraventaKeys
from app.models.donacion import DonacionKeys
from app.models.testamento import TestamentoKeys
from app.models.poder import PoderKeys
from app.models.sociedad import SociedadKeys
from app.models.cancelacion import CancelacionKeys

logger = structlog.get_logger()


# ==========================================
# PALABRAS CLAVE SEMÁNTICAS PARA FUZZY MEJORADO
# ==========================================
SEMANTIC_KEYWORDS = {
    # ==========================================
    # Campos de BaseKeys (heredados por todos los modelos)
    # ==========================================
    "fecha_instrumento": ["fecha", "instrumento", "escritura", "documento", "firma", "acto"],
    "lugar_instrumento": ["lugar", "ciudad", "estado", "instrumento", "firma", "plaza", "residencia"],
    "numero_instrumento": ["numero", "instrumento", "escritura", "folio"],
    "notario_actuante": ["notario", "nombre", "actuante", "publico", "fedatario"],
    "numero_notaria": ["numero", "notaria", "notario"],

    # ==========================================
    # Datos del Deudor
    # ==========================================
    "Deudor_Nombre_Completo": ["nombre", "deudor", "cliente", "titular", "acreditado", "propietario", "persona"],
    "Deudor_RFC": ["rfc", "registro", "fiscal", "contribuyente"],
    "Deudor_CURP": ["curp", "clave", "unica", "poblacion"],
    "Deudor_Estado_Civil": ["estado", "civil", "casado", "soltero"],
    "Deudor_Domicilio": ["domicilio", "direccion", "deudor", "cliente"],

    # Institución Financiera
    "Acreedor_Nombre": ["banco", "acreedor", "institucion", "financiera", "hipotecaria"],
    "Numero_Credito": ["numero", "credito", "cuenta", "folio"],
    "Fecha_Credito": ["fecha", "credito", "otorgamiento"],
    "Monto_Credito_Original": ["monto", "original", "capital", "inicial"],
    "Suma_Credito": ["suma", "monto", "credito", "capital", "importe", "cantidad", "hipoteca"],
    "Suma_Credito_Letras": ["suma", "monto", "letras", "capital"],
    "Equivalente_Salario_Minimo": ["salario", "minimo", "vsm", "veces"],
    "Equivalente_Salario_Minimo_Letras": ["salario", "minimo", "letras"],

    # Inmueble
    "Inmueble_Tipo": ["tipo", "inmueble", "casa", "propiedad"],
    "Inmueble_Direccion": ["inmueble", "direccion", "domicilio", "ubicacion", "propiedad", "casa"],
    "Inmueble_Superficie": ["superficie", "area", "metros", "m2"],
    "Inmueble_Colindancias": ["colindancias", "linderos", "medidas"],
    "Ubicacion_Inmueble": ["ubicacion", "inmueble", "completa", "descripcion"],

    # Cesión
    "Cesion_Credito_Fecha": ["cesion", "fecha", "credito"],
    "Cesion_Credito_Valor": ["cesion", "valor", "derechos"],

    # Registrales Propiedad
    "Folio_Real": ["folio", "real", "electronico", "rpp"],
    "Partida_Registral": ["partida", "registral", "seccion"],
    "Numero_Registro_Libro_Propiedad": ["registro", "propiedad", "libro", "numero", "inscripcion"],
    "Tomo_Libro_Propiedad": ["tomo", "propiedad", "volumen", "libro"],

    # Registrales Gravamen
    "Numero_Registro_Libro_Gravamen": ["registro", "gravamen", "hipoteca", "numero", "libro"],
    "Tomo_Libro_Gravamen": ["tomo", "gravamen", "volumen", "libro"],
    "Fecha_Inscripcion_Hipoteca": ["fecha", "inscripcion", "hipoteca", "registro"],

    # Multi-crédito
    "Intermediario_Financiero": ["intermediario", "sofol", "sofom", "financiero"],
    "Credito_Banco_Reg_Propiedad": ["banco", "registro", "propiedad"],
    "Credito_Banco_Reg_Gravamen": ["banco", "registro", "gravamen"],
    "Credito_FOVISSSTE_Reg_Propiedad": ["fovissste", "registro", "propiedad"],
    "Credito_FOVISSSTE_Reg_Gravamen": ["fovissste", "registro", "gravamen"],

    # Cancelación
    "Fecha_Liquidacion": ["fecha", "liquidacion", "pago", "total"],
    "Monto_Liquidacion": ["monto", "liquidacion", "importe", "saldo"],
    "Numero_Finiquito": ["numero", "finiquito", "folio"],
    "Fecha_Finiquito": ["fecha", "finiquito", "constancia"],

    # Representación
    "Representante_Banco_Nombre": ["representante", "nombre", "apoderado", "legal"],
    "Representante_Banco_Cargo": ["representante", "cargo", "apoderado"],
    "Poder_Notarial_Numero": ["poder", "numero", "notarial", "escritura"],
    "Poder_Notarial_Fecha": ["poder", "fecha", "notarial"],
    "Poder_Notarial_Notario": ["poder", "notario", "otorgante"],
    "Poder_Notarial_Ciudad": ["poder", "ciudad", "lugar"],

    # Carta de Instrucciones
    "Carta_Instrucciones_Numero_Oficio": ["carta", "oficio", "numero", "expediente"],
    "Carta_Instrucciones_Fecha_Constancia_Liquidacion": ["carta", "constancia", "liquidacion", "fecha"],
    "Carta_Instrucciones_Nombre_Titular_Credito": ["titular", "credito", "nombre", "carta"],
    "Carta_Instrucciones_Numero_Credito": ["carta", "credito", "numero"],
    "Carta_Instrucciones_Tipo_Credito": ["tipo", "credito", "programa", "fovissste", "infonavit", "cofinanciado"],
    "Carta_Instrucciones_Fecha_Adjudicacion": ["adjudicacion", "fecha", "carta"],
    "Carta_Instrucciones_Ubicacion_Inmueble": ["carta", "ubicacion", "inmueble"],
    "Carta_Instrucciones_Valor_Credito": ["carta", "valor", "credito", "monto"],
    "Carta_Instrucciones_Valor_Credito_Letras": ["carta", "valor", "letras"],
    "Carta_Instrucciones_Numero_Registro": ["carta", "registro", "numero"],
    "Carta_Instrucciones_Tomo": ["carta", "tomo", "volumen"],

    # Constancia Finiquito
    "Constancia_Finiquito_Numero_Oficio": ["constancia", "finiquito", "oficio", "numero"],
    "Constancia_Finiquito_Fecha_Emision": ["constancia", "emision", "fecha", "finiquito"],

    # Observaciones
    "Observaciones": ["observaciones", "notas", "comentarios"],
}


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
        "sociedad": SociedadKeys,
        "cancelacion": CancelacionKeys
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
    def _get_model_class_for_type(document_type: str) -> Type[BaseKeys]:
        """
        Obtiene la clase del modelo Pydantic para un tipo de documento

        Args:
            document_type: Tipo de documento

        Returns:
            Type[BaseKeys]: Clase del modelo
        """
        model_class = PlaceholderMapper.MODEL_MAP.get(document_type)
        if not model_class:
            model_class = BaseKeys
        return model_class

    @staticmethod
    def _get_field_aliases(model_class: Type[BaseKeys]) -> Dict[str, List[str]]:
        """
        Extrae aliases de cada campo del modelo Pydantic

        Args:
            model_class: Clase del modelo Pydantic

        Returns:
            Dict[str, List[str]]: Diccionario {nombre_campo: [aliases]}
        """
        aliases = {}
        for field_name, field_info in model_class.model_fields.items():
            extra = field_info.json_schema_extra or {}
            field_aliases = extra.get("aliases", [])
            aliases[field_name] = field_aliases
        return aliases

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
    def _calculate_similarity(
        placeholder: str,
        standard_key: str,
        aliases: List[str] = None
    ) -> int:
        """
        Calcula score de similitud entre placeholder y clave estándar

        Scoring mejorado con aliases + semántico:
        - Match exacto con campo: 100pts
        - Match exacto con alias: 95pts
        - Palabras clave semánticas: 20pts por match
        - Palabras comunes: 15pts por palabra
        - Fuzzy matching: hasta 30pts adicionales

        Args:
            placeholder: Placeholder del template
            standard_key: Clave estándar del modelo
            aliases: Lista de aliases para el campo (opcional)

        Returns:
            int: Score de similitud (0-130+)
        """
        if aliases is None:
            aliases = []

        # Normalizar placeholder
        placeholder_lower = placeholder.lower().replace('_', ' ').strip()
        key_lower = standard_key.lower().replace('_', ' ').strip()

        # 1. Match exacto con campo: 100 puntos
        if placeholder_lower == key_lower:
            return 100

        # 2. Match exacto con alias: 95 puntos
        for alias in aliases:
            alias_lower = alias.lower().replace('_', ' ').strip()
            if placeholder_lower == alias_lower:
                return 95

        score = 0

        # 3. Match con palabras clave semánticas: 20 puntos por match
        semantic_words = SEMANTIC_KEYWORDS.get(standard_key, [])
        for word in semantic_words:
            if word in placeholder_lower:
                score += 20

        # 4. Match de palabras comunes: 15 puntos por palabra
        placeholder_words = PlaceholderMapper._extract_words(placeholder)
        standard_words = PlaceholderMapper._extract_words(standard_key)
        common_words = placeholder_words & standard_words
        score += len(common_words) * PlaceholderMapper.WORD_MATCH_MULTIPLIER

        # 5. Match parcial con aliases: 10 puntos por palabra en común
        for alias in aliases:
            alias_words = PlaceholderMapper._extract_words(alias)
            alias_common = placeholder_words & alias_words
            score += len(alias_common) * 10

        # 6. Fuzzy matching con SequenceMatcher: hasta 30 puntos
        ratio = SequenceMatcher(None, placeholder_lower, key_lower).ratio()
        fuzzy_bonus = int(ratio * PlaceholderMapper.FUZZY_MAX_BONUS)
        score += fuzzy_bonus

        # 7. Fuzzy matching con aliases: hasta 15 puntos extra
        best_alias_fuzzy = 0
        for alias in aliases:
            alias_lower = alias.lower().replace('_', ' ')
            alias_ratio = SequenceMatcher(None, placeholder_lower, alias_lower).ratio()
            if alias_ratio > best_alias_fuzzy:
                best_alias_fuzzy = alias_ratio
        score += int(best_alias_fuzzy * 15)

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

        # Obtener modelo y aliases
        model_class = PlaceholderMapper._get_model_class_for_type(document_type)
        field_aliases = PlaceholderMapper._get_field_aliases(model_class)

        mapping = {}
        unmatched_count = 0

        for placeholder in template_placeholders:
            best_match = None
            best_score = 0

            # Calcular score contra todas las claves estándar (con aliases)
            for standard_key in standard_keys:
                aliases = field_aliases.get(standard_key, [])
                score = PlaceholderMapper._calculate_similarity(
                    placeholder, standard_key, aliases
                )

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
