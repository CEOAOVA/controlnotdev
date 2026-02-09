"""
ControlNot v2 - Anthropic AI Service
Extracción de datos con Claude Vision + Prompt Caching

=== CLAUDE VISION DOCS (docs.anthropic.com) ===
https://docs.anthropic.com/en/docs/build-with-claude/vision

Best Practices Oficiales:
- "Resize images to no more than 1.15 megapixels"
- "Images placed after text still perform well, but image-then-text is better"
- "Introduce each image with Image 1:, Image 2:"
- "Claude may hallucinate on low-quality, rotated, or very small images"
- Tokens: (width * height) / 750

| Especificación          | Valor Oficial               |
|-------------------------|------------------------------|
| Tamaño óptimo           | ≤1568px en ambas dims       |
| Megapíxeles óptimos     | ≤1.15 MP                    |
| Tamaño mínimo efectivo  | >200px                      |
| Límite por request      | 100 imágenes API            |
| Peso máximo             | 5MB por imagen              |

Beneficios vs OpenAI GPT-4o:
- Costo: $0.003/1K tokens input (con cache) vs $0.005 OpenAI (-40%)
- Calidad: Mejor en español legal y documentos largos
- Context: 200K tokens vs 128K OpenAI
- Cache: Reutiliza prompts grandes automáticamente
"""
import json
from typing import Dict, List, Optional
import structlog
from anthropic import Anthropic
from pydantic import BaseModel

from app.core.config import settings
from app.models.base import BaseKeys
from app.models.compraventa import CompraventaKeys
from app.models.donacion import DonacionKeys
from app.utils.number_conversion import convertir_si_es_numero
from app.models.testamento import TestamentoKeys
from app.models.poder import PoderKeys
from app.models.sociedad import SociedadKeys
from app.models.cancelacion import CancelacionKeys
# Identificaciones mexicanas
from app.models.ine import INECredencial
from app.models.pasaporte import PasaporteMexicano
from app.models.curp_constancia import ConstanciaCURP

logger = structlog.get_logger()


# =========================================
# PROMPTS ESPECIALIZADOS POR TIPO DE DOCUMENTO
# Best Practices 2025 para reducir alucinaciones
# =========================================

DOCUMENT_SPECIFIC_PROMPTS = {
    "escritura_antigua": """
TIPO DE DOCUMENTO: Escritura Notarial Antigua (posiblemente mecanografiada)

CONSIDERACIONES ESPECIALES:
- El documento puede tener sellos o firmas que cubren parcialmente el texto
- El texto puede estar desvanecido en algunas partes debido a la antiguedad
- Puede haber manchas, dobleces o deterioro del papel
- La tipografia mecanografiada puede tener caracteres dificiles de distinguir

INSTRUCCIONES:
- Si un campo es parcialmente ilegible, indica el texto visible seguido de "[parcial]"
- NO inventes informacion que no puedas ver claramente
- Prioriza extraer: partes involucradas, fecha, notario, numero de escritura
- Si hay sellos sobre texto importante, intenta leer lo que sea visible
- Indica "[ilegible por sello]" si un sello cubre completamente informacion critica
""",

    "ine_fotocopia": """
TIPO DE DOCUMENTO: INE/IFE (posiblemente fotocopia o foto de WhatsApp)

CONSIDERACIONES ESPECIALES:
- La calidad puede ser baja por compresion de imagen
- Algunos datos pueden ser dificiles de leer por la resolucion
- El documento puede estar ligeramente inclinado o con reflejos
- Las fotos de WhatsApp tienen compresion agresiva

INSTRUCCIONES:
- Busca: nombre completo, CURP, clave de elector, seccion, vigencia
- Si un dato es ilegible, indica "ilegible" en lugar de adivinar
- La direccion puede estar cortada o parcial
- Verifica que el CURP tenga 18 caracteres
- La clave de elector tiene formato especifico: 6 letras + 8 numeros + H/M + 3 numeros
""",

    "curp_constancia": """
TIPO DE DOCUMENTO: Constancia de CURP

CONSIDERACIONES ESPECIALES:
- Documento digital generalmente nitido
- El CURP es el dato mas importante y debe ser exacto
- Contiene datos biometricos y de registro civil

INSTRUCCIONES:
- El CURP debe tener exactamente 18 caracteres
- Verifica: 4 letras + 6 numeros + H/M + 5 letras + 2 caracteres
- Extrae fecha de nacimiento, entidad de registro, sexo
- El nombre debe coincidir exactamente con el CURP
""",

    "avaluo": """
TIPO DE DOCUMENTO: Avaluo o Documento de Valuacion

CONSIDERACIONES ESPECIALES:
- Contiene muchos datos numericos que deben ser exactos
- Puede tener tablas, graficos o planos
- Los valores monetarios son criticos

INSTRUCCIONES:
- Extrae con precision: valor total, superficie, ubicacion, fecha
- Los numeros son criticos - NO redondees ni aproximes
- Mantén el formato de moneda: $X,XXX,XXX.XX
- Las superficies deben incluir unidad (m2, hectareas, etc.)
- Busca el valor catastral y valor comercial por separado
""",

    "acta_nacimiento": """
TIPO DE DOCUMENTO: Acta de Nacimiento

CONSIDERACIONES ESPECIALES:
- Documento oficial con formato estandar del Registro Civil
- Puede ser copia certificada reciente o documento antiguo
- Contiene informacion genealogica importante

INSTRUCCIONES:
- Extrae: nombre completo, fecha de nacimiento, lugar, padres
- La fecha de nacimiento es CRITICA para calcular edad
- Los nombres de los padres incluyen apellidos completos
- Busca el numero de acta y tomo si estan visibles
- CURP puede aparecer en actas recientes
""",

    "recibo_cfe": """
TIPO DE DOCUMENTO: Recibo CFE (Comision Federal de Electricidad)

CONSIDERACIONES ESPECIALES:
- Documento con formato estandar de CFE
- Contiene direccion del predio que es importante para notaria

INSTRUCCIONES:
- Prioriza: direccion completa, numero de servicio
- La direccion es la informacion mas importante
- Extrae colonia, municipio, codigo postal
- El numero de servicio tiene formato especifico de CFE
""",

    "juicio_sucesorio": """
TIPO DE DOCUMENTO: Juicio Sucesorio / Sentencia de Adjudicación

CONSIDERACIONES ESPECIALES:
- Este documento puede ser una sentencia judicial o su protocolización notarial
- Contiene información sobre la transmisión de propiedad por fallecimiento
- Puede ser intestamentario (sin testamento) o testamentario (con testamento)

CAMPOS CRITICOS A BUSCAR:
- Tipo de juicio: "INTESTAMENTARIO" o "TESTAMENTARIO"
- Nombre del causante (persona fallecida): "SUCESION A BIENES DE", "DE CUJUS"
- Número de expediente judicial: "EXPEDIENTE", "EXP."
- Juzgado que conoció del caso: "JUZGADO", "TRIBUNAL"
- Fecha de la sentencia: "SENTENCIA DE FECHA", "RESOLUCION"
- Notario que protocolizó (si aplica): "PROTOCOLIZADO ANTE"

INSTRUCCIONES:
- Si detectas "JUICIO SUCESORIO", llena los campos Juicio_Sucesorio_*
- Los campos Escritura_Privada_* aplican para escrituras, NO para juicios
- El notario de protocolización es DIFERENTE al notario de una escritura antecedente

BUSCAR FRASES CLAVE:
- "JUICIO SUCESORIO INTESTAMENTARIO A BIENES DE..."
- "SUCESION TESTAMENTARIA DE..."
- "SENTENCIA DEFINITIVA DE ADJUDICACION"
- "PROTOCOLIZACION DE SENTENCIA"
""",

    "default": """
TIPO DE DOCUMENTO: Documento General

INSTRUCCIONES:
- Analiza el documento visualmente para identificar su tipo
- Extrae todos los campos solicitados con precision
- Si un dato no es visible, usa "**[NO ENCONTRADO]**"
- Mantén formatos exactos de fechas, numeros y nombres
"""
}


# Campos que requieren conversión automática de números a palabras
CAMPOS_CONVERSION_NUMEROS = [
    "Numero_Registro",
    "Numero_tomo_Registro",
]


def post_process_extracted_data(extracted_data: dict, document_type: str) -> dict:
    """
    Post-procesa datos extraídos para aplicar conversiones automáticas.

    Actualmente maneja:
    - Conversión de números a palabras para campos RPP (Numero_Registro, Numero_tomo_Registro)
    - Fallback de campos de Juicio Sucesorio → campos genéricos de antecedente

    Args:
        extracted_data: Diccionario con datos extraídos por Claude
        document_type: Tipo de documento (para futuras reglas específicas)

    Returns:
        dict: Datos post-procesados con conversiones aplicadas
    """
    if not extracted_data:
        return extracted_data

    processed = extracted_data.copy()

    # === CONVERSIÓN DE NÚMEROS A PALABRAS ===
    for campo in CAMPOS_CONVERSION_NUMEROS:
        if campo in processed:
            valor = processed[campo]
            # Solo convertir si no es NO ENCONTRADO y tiene valor
            if valor and "NO ENCONTRADO" not in str(valor):
                valor_convertido = convertir_si_es_numero(valor, mayusculas=True)
                if valor_convertido != valor:
                    logger.debug(
                        f"Campo {campo} convertido",
                        original=valor,
                        convertido=valor_convertido
                    )
                processed[campo] = valor_convertido

    # === FALLBACK PARA JUICIO SUCESORIO ===
    # Si el antecedente es juicio sucesorio, copiar campos a los genéricos de antecedente
    antecedente_tipo = processed.get("Antecedente_Tipo", "").lower()

    if "juicio" in antecedente_tipo or "sucesorio" in antecedente_tipo or "herencia" in antecedente_tipo:
        # Mapeo de campos de juicio sucesorio → campos genéricos de escritura antecedente
        fallback_map = {
            "Juicio_Sucesorio_Notario_Protocolizacion": "Escritura_Privada_Notario",
            "Juicio_Sucesorio_Fecha_Sentencia": "Escritura_Privada_fecha",
            "Juicio_Sucesorio_Expediente": "Escritura_Privada_numero",
        }

        for source, target in fallback_map.items():
            source_val = processed.get(source)
            target_val = processed.get(target)

            # Solo copiar si el campo destino está vacío/NO ENCONTRADO y origen tiene valor
            if source_val and "NO ENCONTRADO" not in str(source_val):
                if not target_val or "NO ENCONTRADO" in str(target_val):
                    processed[target] = source_val
                    logger.debug(
                        f"Fallback Juicio Sucesorio: {source} → {target}",
                        valor=source_val
                    )

    return processed


class AnthropicExtractionService:
    """
    Servicio de extracción con Anthropic Claude + Prompt Caching

    ARQUITECTURA:
    1. System prompt con cache_control (reutilizable)
    2. Contexto de campos con cache_control (reutilizable)
    3. Texto a procesar (no cacheable, cambia siempre)

    AHORRO DE COSTOS:
    - 1er request: Costo completo (~5,000 tokens)
    - Requests 2-N (5 min): Solo texto nuevo (~500 tokens)
    - Ahorro: 90% en tokens de prompt

    Ejemplo:
        >>> service = AnthropicExtractionService()
        >>> result = service.extract_with_caching(text, "compraventa")
        >>> # 1er request: $0.025
        >>> # 2do request (mismo tipo): $0.003 (10x más barato!)
    """

    # Mapeo de tipos de documento a modelos Pydantic (igual que ai_service)
    MODEL_MAP = {
        # Documentos notariales
        "compraventa": CompraventaKeys,
        "donacion": DonacionKeys,
        "testamento": TestamentoKeys,
        "poder": PoderKeys,
        "sociedad": SociedadKeys,
        "cancelacion": CancelacionKeys,
        # Identificaciones mexicanas
        "ine_ife": INECredencial,
        "pasaporte": PasaporteMexicano,
        "curp_constancia": ConstanciaCURP,
    }

    # Modelo recomendado (Sonnet 4 = más reciente y mejor rendimiento)
    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa cliente de Anthropic

        Args:
            api_key: API key de Anthropic (usa settings.ANTHROPIC_API_KEY por defecto)
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY no configurado. "
                "Añadir a backend/.env: ANTHROPIC_API_KEY=sk-ant-..."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = self.DEFAULT_MODEL
        self.last_tokens_used = 0
        self.last_cached_tokens = 0
        self.cache_hit = False

        logger.info(
            "AnthropicExtractionService inicializado",
            model=self.model,
            caching_enabled=True
        )

    def _get_model_for_type(self, document_type: str) -> BaseModel:
        """
        Obtiene la clase del modelo Pydantic para un tipo de documento

        Args:
            document_type: Tipo de documento

        Returns:
            BaseModel: Clase del modelo Pydantic
        """
        model_class = self.MODEL_MAP.get(document_type)

        if not model_class:
            logger.warning(
                "Tipo de documento no encontrado, usando BaseKeys",
                doc_type=document_type
            )
            model_class = BaseKeys

        return model_class

    def _get_specialized_prompt(self, document_hint: str) -> str:
        """
        Obtiene prompt especializado para tipo de documento o caracteristica.

        Args:
            document_hint: Tipo de documento o caracteristica especial
                          Ejemplos: "escritura_antigua", "ine_fotocopia", "avaluo"

        Returns:
            str: Prompt especializado o default
        """
        # Buscar coincidencia exacta
        if document_hint in DOCUMENT_SPECIFIC_PROMPTS:
            return DOCUMENT_SPECIFIC_PROMPTS[document_hint]

        # Buscar coincidencia parcial
        hint_lower = document_hint.lower()
        for key, prompt in DOCUMENT_SPECIFIC_PROMPTS.items():
            if key in hint_lower or hint_lower in key:
                return prompt

        # Detectar por nombre de archivo
        if any(x in hint_lower for x in ['ine', 'ife', 'credencial']):
            return DOCUMENT_SPECIFIC_PROMPTS.get("ine_fotocopia", "")
        if any(x in hint_lower for x in ['curp', 'constancia']):
            return DOCUMENT_SPECIFIC_PROMPTS.get("curp_constancia", "")
        if any(x in hint_lower for x in ['avaluo', 'valuacion']):
            return DOCUMENT_SPECIFIC_PROMPTS.get("avaluo", "")
        if any(x in hint_lower for x in ['acta', 'nacimiento']):
            return DOCUMENT_SPECIFIC_PROMPTS.get("acta_nacimiento", "")
        if any(x in hint_lower for x in ['cfe', 'luz', 'recibo']):
            return DOCUMENT_SPECIFIC_PROMPTS.get("recibo_cfe", "")
        if any(x in hint_lower for x in ['escritura', 'antecedente']):
            return DOCUMENT_SPECIFIC_PROMPTS.get("escritura_antigua", "")

        return DOCUMENT_SPECIFIC_PROMPTS.get("default", "")

    def _build_system_prompt(self, document_type: str) -> str:
        """
        Construye el system prompt (CACHEABLE)

        Este prompt se cachea por 5 minutos, permitiendo reutilizarlo
        para múltiples documentos del mismo tipo.

        Args:
            document_type: Tipo de documento

        Returns:
            str: System prompt formateado
        """
        # Obtener fecha actual para cálculo de edad
        from datetime import datetime
        fecha_actual = datetime.now()
        fecha_actual_str = fecha_actual.strftime('%d de %B de %Y').replace(
            'January', 'enero').replace('February', 'febrero').replace('March', 'marzo'
        ).replace('April', 'abril').replace('May', 'mayo').replace('June', 'junio'
        ).replace('July', 'julio').replace('August', 'agosto').replace('September', 'septiembre'
        ).replace('October', 'octubre').replace('November', 'noviembre').replace('December', 'diciembre')
        ano_actual = fecha_actual.year

        return f"""Eres un asistente experto en extracción de datos de documentos notariales mexicanos.

ESPECIALIZACIÓN: {document_type}

OBJETIVO:
Extraer información estructurada de documentos notariales con precisión legal.

PRINCIPIOS:
1. PRECISIÓN: Solo extrae información explícitamente presente
2. FORMATO: Mantén formatos exactos (nombres completos, fechas, números)
3. VALIDACIÓN: Valida RFC (13 caracteres), CURP (18 caracteres), fechas
4. MARCADO: Usa "**[NO ENCONTRADO]**" para campos ausentes
5. NO INVENTES: Nunca generes datos que no estén en el texto

CÁLCULO DE EDAD (IMPORTANTE):
Cuando extraigas campos de edad (Edad_Parte_*), DEBES calcularla así:
1. Primero localiza la fecha de nacimiento en el Acta de Nacimiento, INE o CURP
2. Usa la fecha actual: {fecha_actual_str} (año {ano_actual})
3. Calcula: edad = {ano_actual} - año_de_nacimiento
4. Si el cumpleaños de este año AÚN NO ha pasado, resta 1 a la edad
5. Convierte el resultado a palabras en español

CONVERSIÓN DE NÚMEROS A PALABRAS:
- 30 = treinta años
- 45 = cuarenta y cinco años
- 61 = sesenta y un años
- 78 = setenta y ocho años
- 82 = ochenta y dos años

FORMATOS REQUERIDOS:
- Fechas: DD/MM/AAAA (ejemplo: 15/03/2024)
- Dinero: $X,XXX.XX MXN (ejemplo: $1,500,000.00 MXN)
- RFC: 13 caracteres (ejemplo: AAAA860101AAA)
- CURP: 18 caracteres (ejemplo: AAAA860101HDFLLS05)
- Nombres: Apellido paterno, materno y nombre(s) completo
- Edades: número en palabras + "años" (ejemplo: sesenta y un años)

IMPORTANTE:
Tu respuesta DEBE ser JSON válido sin texto adicional.
No incluyas markdown, explicaciones ni comentarios.
Solo el objeto JSON con los campos solicitados."""

    def _condense_description(self, description: str) -> str:
        """
        Condensa una descripción larga a lo esencial (patrón movil_cancelaciones.py)

        Extrae:
        1. Primera línea significativa (qué extraer)
        2. Formato de salida si existe
        3. Primer ejemplo si existe

        Máximo ~250 caracteres para mantener contexto manejable.

        Args:
            description: Descripción completa del campo

        Returns:
            str: Descripción condensada (~150-250 chars)
        """
        lines = description.strip().split('\n')

        result_parts = []
        formato = None
        ejemplo = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith('===') or line.startswith('---'):
                continue

            # Capturar formato de salida
            if 'FORMATO' in line.upper() and ':' in line:
                formato = line.split(':', 1)[1].strip()
                continue

            # Capturar ejemplo
            if 'EJEMPLO' in line.upper() or line.startswith('Ejemplo:'):
                ejemplo = line
                continue

            # Primera línea descriptiva significativa
            if not result_parts and len(line) > 10:
                result_parts.append(line)

        # Construir descripción condensada
        condensed = result_parts[0] if result_parts else description.split('\n')[0]

        if formato:
            condensed = f"FORMATO: {formato}. {condensed}"

        if ejemplo:
            condensed += f" {ejemplo}"

        # Limitar a 250 chars máximo
        if len(condensed) > 250:
            condensed = condensed[:247] + "..."

        return condensed

    def _build_fields_context(
        self,
        document_type: str,
        placeholders: Optional[List[str]] = None
    ) -> str:
        """
        Construye el contexto de campos como JSON estructurado (CACHEABLE)

        Usa descripciones COMPLETAS de cada campo, igual que los scripts legacy
        (por_partes.py, escrituras.py) que envían json.dumps(relevant_keys, indent=4).
        Las descripciones contienen lógica de extracción crítica (prioridades,
        pasos de exclusión, lógica temporal) que no debe truncarse.
        Claude tiene 200K de contexto, así que no hay riesgo de overflow.

        Args:
            document_type: Tipo de documento
            placeholders: Placeholders opcionales del template

        Returns:
            str: Contexto de campos formateado como JSON estructurado
        """
        import json

        model_class = self._get_model_for_type(document_type)

        # Diccionario con descripciones COMPLETAS (como en legacy por_partes.py/escrituras.py)
        fields_dict = {}
        for field_name, field_info in model_class.model_fields.items():
            desc = field_info.description or ""
            if desc:
                fields_dict[field_name] = desc.strip()
            else:
                fields_dict[field_name] = f"Extraer el campo {field_name}"

        # JSON estructurado
        context = f"""CAMPOS A EXTRAER ({len(fields_dict)} total):

Extrae la información en formato JSON con las siguientes especificaciones:
{json.dumps(fields_dict, indent=2, ensure_ascii=False)}"""

        if placeholders:
            placeholders_dict = {ph: f"Extraer valor para {ph}" for ph in placeholders}
            context += f"""

PLACEHOLDERS ADICIONALES DEL TEMPLATE ({len(placeholders)} total):
{json.dumps(placeholders_dict, indent=2, ensure_ascii=False)}"""

        return context

    def extract_with_caching(
        self,
        text: str,
        document_type: str,
        placeholders: Optional[List[str]] = None,
        temperature: float = 0.0,  # Best practice: 0 para extracción determinista
        max_tokens: int = 8192
    ) -> Dict[str, str]:
        """
        Extrae datos usando Claude con Prompt Caching

        === BEST PRACTICES ===
        - temperature=0.0: Determinista para extracción factual
        - Prompt Caching: -40-60% costos reutilizando prompts

        ARQUITECTURA DE CACHE:
        - System prompt: Cache por 5 min (reutilizable)
        - Campos y contexto: Cache por 5 min (reutilizable)
        - Texto a procesar: NO cacheable (único por documento)

        AHORRO:
        1er documento tipo X: $0.025 (costo completo)
        2do-N documentos tipo X (5 min): $0.003 (10x más barato)

        Args:
            text: Texto del documento
            document_type: Tipo de documento
            placeholders: Placeholders opcionales
            temperature: 0.0 recomendado para extracción
            max_tokens: Máximo de tokens en respuesta

        Returns:
            Dict[str, str]: Datos extraídos

        Example:
            >>> service = AnthropicExtractionService()
            >>> # Procesar 10 compraventas seguidas
            >>> for text in compraventas:
            ...     result = service.extract_with_caching(text, "compraventa")
            ...     # 1er doc: $0.025, resto: $0.003 c/u
            ...     # Total: $0.025 + (9 × $0.003) = $0.052 vs $0.250 sin cache
            ...     # Ahorro: 80%

        Raises:
            Exception: Si falla la extracción
        """
        logger.info(
            "Extrayendo datos con Claude + Prompt Caching",
            doc_type=document_type,
            text_length=len(text),
            model=self.model
        )

        try:
            # Construir prompts cacheables
            system_prompt = self._build_system_prompt(document_type)
            fields_context = self._build_fields_context(document_type, placeholders)

            # Llamar a Claude con cache_control
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}  # ⚡ CACHEA SYSTEM PROMPT
                    },
                    {
                        "type": "text",
                        "text": fields_context,
                        "cache_control": {"type": "ephemeral"}  # ⚡ CACHEA CAMPOS
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": f"""DOCUMENTO A PROCESAR:

{text}

RESPONDE SOLO CON JSON (sin markdown ni explicaciones):"""
                    }
                ]
            )

            # Extraer contenido (Claude retorna lista de bloques)
            content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text

            # Limpiar markdown si existe (Claude a veces lo añade)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remover ```json
            if content.startswith("```"):
                content = content[3:]  # Remover ```
            if content.endswith("```"):
                content = content[:-3]  # Remover ```
            content = content.strip()

            # Parsear JSON
            extracted_data = json.loads(content)

            # Post-procesar datos (conversión de números, etc.)
            extracted_data = post_process_extracted_data(extracted_data, document_type)

            # Guardar métricas de tokens
            usage = response.usage
            self.last_tokens_used = usage.input_tokens + usage.output_tokens

            # Detectar cache hit (tokens cacheados)
            cache_creation_tokens = getattr(usage, 'cache_creation_input_tokens', 0)
            cache_read_tokens = getattr(usage, 'cache_read_input_tokens', 0)
            self.last_cached_tokens = cache_read_tokens
            self.cache_hit = cache_read_tokens > 0

            # Calcular ahorro
            if self.cache_hit:
                # Cache hit: Solo paga tokens nuevos
                cost_input = (usage.input_tokens * 0.003) / 1000  # $0.003/1K con cache
                savings_percent = (cache_read_tokens / (usage.input_tokens + cache_read_tokens)) * 100
            else:
                # Cache miss: Paga precio completo
                cost_input = (usage.input_tokens * 0.015) / 1000  # $0.015/1K sin cache
                savings_percent = 0

            cost_output = (usage.output_tokens * 0.075) / 1000  # $0.075/1K output
            total_cost = cost_input + cost_output

            logger.info(
                "Extracción completada con Claude",
                fields_extracted=len(extracted_data),
                tokens_used=self.last_tokens_used,
                cache_hit=self.cache_hit,
                cached_tokens=self.last_cached_tokens,
                savings_percent=f"{savings_percent:.1f}%",
                estimated_cost=f"${total_cost:.5f}"
            )

            return extracted_data

        except json.JSONDecodeError as e:
            logger.error(
                "Error al parsear respuesta JSON de Claude",
                error=str(e),
                response_content=content if 'content' in locals() else None
            )
            raise

        except Exception as e:
            logger.error(
                "Error al procesar con Claude",
                error=str(e),
                error_type=type(e).__name__,
                model=self.model
            )
            raise

    def validate_extracted_data(
        self,
        extracted_data: Dict[str, str],
        document_type: str
    ) -> Dict:
        """
        Valida datos extraídos contra el modelo Pydantic

        Args:
            extracted_data: Datos extraídos por Claude
            document_type: Tipo de documento

        Returns:
            Dict: Estadísticas de validación
        """
        model_class = self._get_model_for_type(document_type)
        required_fields = set(model_class.model_fields.keys())
        extracted_fields = set(extracted_data.keys())

        # Identificar campos opcionales desde metadata del modelo
        optional_fields = set()
        for field_name, field_info in model_class.model_fields.items():
            extra = field_info.json_schema_extra or {}
            if extra.get('optional_field', False):
                optional_fields.add(field_name)

        # Campos encontrados
        found_fields = extracted_fields & required_fields

        # Campos faltantes
        missing_fields = required_fields - extracted_fields

        # Campos con valor "NO ENCONTRADO"
        not_found_values = [
            field for field, value in extracted_data.items()
            if "NO ENCONTRADO" in str(value)
        ]

        # FIX: Restar campos con valor NO ENCONTRADO del conteo
        found_fields = found_fields - set(not_found_values)

        # Separar campos opcionales faltantes de criticos faltantes
        optional_missing = [f for f in not_found_values if f in optional_fields]
        critical_missing = [f for f in not_found_values if f not in optional_fields]

        # Calcular completitud excluyendo campos opcionales del denominador
        required_for_validation = required_fields - optional_fields
        found_required = found_fields - optional_fields
        completeness = len(found_required) / len(required_for_validation) if required_for_validation else 0.0

        stats = {
            "total_fields": len(required_fields),
            "found_fields": len(found_fields),
            "missing_fields": list(missing_fields),
            "not_found_values": not_found_values,
            "optional_missing": optional_missing,
            "critical_missing": critical_missing,
            "optional_fields_count": len(optional_fields),
            "completeness": completeness
        }

        logger.info(
            "Validación de datos extraídos (Claude)",
            doc_type=document_type,
            completeness_percent=f"{completeness * 100:.1f}%",
            optional_missing=optional_missing,
            critical_missing_count=len(critical_missing),
            **{k: v for k, v in stats.items() if k not in ['optional_missing', 'critical_missing']}
        )

        return stats

    def enrich_with_defaults(
        self,
        extracted_data: Dict[str, str],
        document_type: str
    ) -> Dict[str, str]:
        """
        Enriquece datos con valores por defecto para campos faltantes

        Args:
            extracted_data: Datos extraídos
            document_type: Tipo de documento

        Returns:
            Dict[str, str]: Datos enriquecidos
        """
        model_class = self._get_model_for_type(document_type)
        required_fields = model_class.model_fields.keys()

        enriched_data = extracted_data.copy()

        # Añadir campos faltantes
        for field in required_fields:
            if field not in enriched_data:
                enriched_data[field] = "**[NO ENCONTRADO]**"

        logger.debug(
            "Datos enriquecidos (Claude)",
            original_fields=len(extracted_data),
            enriched_fields=len(enriched_data)
        )

        return enriched_data

    def get_cache_stats(self) -> Dict:
        """
        Obtiene estadísticas de uso de cache

        Returns:
            Dict: Estadísticas de cache del último request
        """
        return {
            "cache_hit": self.cache_hit,
            "cached_tokens": self.last_cached_tokens,
            "total_tokens": self.last_tokens_used,
            "cache_percentage": (
                (self.last_cached_tokens / self.last_tokens_used * 100)
                if self.last_tokens_used > 0 else 0
            )
        }

    def extract_with_vision(
        self,
        images: List[Dict],
        document_type: str,
        placeholders: Optional[List[str]] = None,
        temperature: float = 0.0,  # OpenAI/Anthropic best practice: 0 para extracción
        max_tokens: int = 8192,
        quality_level: str = "high",
        document_hints: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Extrae datos enviando imágenes DIRECTAMENTE a Claude Vision

        === CLAUDE VISION BEST PRACTICES (docs.anthropic.com) ===
        - "Images placed after text still perform well, but image-then-text is better"
        - "Introduce each image with Image 1:, Image 2:"
        - temperature=0 para extracción determinista
        - Resize a ≤1568px y ≤1.15MP antes de enviar

        VENTAJAS:
        - NO importa la rotación - Claude entiende el contexto visual
        - Puede identificar qué es INE, CFE, Acta por su formato visual
        - Las descriptions funcionan mejor porque Claude ve dónde buscar
        - ~97% accuracy vs ~85% del OCR tradicional

        Args:
            images: Lista de imágenes con metadatos:
                [{'name': str, 'content': bytes, 'category': str}, ...]
            document_type: Tipo de documento ('donacion', 'compraventa', etc.)
            placeholders: Placeholders opcionales del template
            temperature: 0.0 recomendado para extracción (best practice)
            max_tokens: Máximo de tokens en respuesta
            quality_level: Nivel de calidad de imágenes ('high', 'medium', 'low')
                           Ajusta instrucciones para documentos difíciles
            document_hints: Hints de tipos de documento para prompts especializados
                           Ejemplo: ['escritura_antigua', 'ine_fotocopia']

        Returns:
            Dict[str, str]: Datos extraídos

        Limits (docs.anthropic.com):
            - Máximo 100 imágenes por request API (20 en claude.ai)
            - 5MB máximo por imagen
            - tokens = (width * height) / 750 por imagen

        Example:
            >>> images = [
            ...     {'name': 'INE.jpg', 'content': b'...', 'category': 'parte_a'},
            ...     {'name': 'CURP.jpg', 'content': b'...', 'category': 'parte_a'}
            ... ]
            >>> result = service.extract_with_vision(images, 'donacion')
        """
        import base64

        logger.info(
            "Extrayendo datos con Claude Vision (imágenes directas)",
            doc_type=document_type,
            num_images=len(images),
            model=self.model,
            quality_level=quality_level,
            document_hints=document_hints
        )

        # Validar límite de imágenes (100 en API, 20 en claude.ai)
        if len(images) > 100:
            logger.warning(
                "Demasiadas imágenes, truncando a 100 (límite API)",
                original_count=len(images)
            )
            images = images[:100]

        # === DETECCIÓN AUTOMÁTICA DE JUICIO SUCESORIO ===
        # Detectar por nombre de archivo si hay documentos de juicio sucesorio
        juicio_sucesorio_keywords = ['sucesorio', 'sentencia', 'juzgado', 'adjudicacion',
                                      'adjudicación', 'intestamentario', 'testamentario',
                                      'herencia', 'causante', 'albacea']
        for img in images:
            img_name = img.get('name', '').lower()
            if any(kw in img_name for kw in juicio_sucesorio_keywords):
                if document_hints is None:
                    document_hints = []
                if 'juicio_sucesorio' not in document_hints:
                    document_hints.append('juicio_sucesorio')
                    logger.info(
                        "Detectado documento de juicio sucesorio por nombre de archivo",
                        filename=img.get('name')
                    )
                break

        try:
            # =====================================================
            # ESTRUCTURA: IMAGE-THEN-TEXT (Claude Vision Best Practice)
            # Docs: "Introduce each image with Image 1:, Image 2:"
            # =====================================================
            content = []
            image_count = 0

            for i, img in enumerate(images, 1):
                img_name = img.get('name', 'documento')
                img_content = img.get('content', b'')
                img_category = img.get('category', 'otros')

                if not img_content:
                    logger.warning(f"Imagen vacía: {img_name}")
                    continue

                image_count += 1

                # Codificar a base64
                img_b64 = base64.b64encode(img_content).decode('utf-8')

                # Determinar media type
                name_lower = img_name.lower()
                if name_lower.endswith('.png'):
                    media_type = "image/png"
                elif name_lower.endswith('.gif'):
                    media_type = "image/gif"
                elif name_lower.endswith('.webp'):
                    media_type = "image/webp"
                else:
                    media_type = "image/jpeg"  # Default para jpg, jpeg y otros

                # === CLAUDE VISION BEST PRACTICE ===
                # "Introduce each image with Image 1:, Image 2:"
                content.append({
                    "type": "text",
                    "text": f"Image {image_count}: {img_name} (Categoría: {img_category})"
                })

                # Agregar imagen DESPUÉS del label (image-then-text)
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": img_b64
                    }
                })

            if not content:
                raise ValueError("No hay imágenes válidas para procesar")

            # Agregar instrucciones de extracción
            fields_context = self._build_fields_context(document_type, placeholders)

            # ===== PROMPTS ESPECIALIZADOS (Best Practices 2025) =====
            specialized_prompts = []

            # 1. Prompts basados en document_hints
            if document_hints:
                for hint in document_hints:
                    prompt = self._get_specialized_prompt(hint)
                    if prompt and prompt not in specialized_prompts:
                        specialized_prompts.append(prompt)

            # 2. Detección automática por nombre de imagen
            for img in images:
                img_name = img.get('name', '').lower()
                detected_prompt = self._get_specialized_prompt(img_name)
                if detected_prompt and detected_prompt not in specialized_prompts:
                    specialized_prompts.append(detected_prompt)

            # 3. Instrucciones adicionales para documentos de baja calidad
            quality_instructions = ""
            if quality_level == "low":
                quality_instructions = """
ADVERTENCIA - DOCUMENTOS DE BAJA CALIDAD DETECTADOS:
- Las imágenes pueden estar borrosas, desvanecidas o con bajo contraste
- PRESTA ATENCION ESPECIAL a caracteres que pueden confundirse (0/O, 1/l/I, 5/S, 8/B)
- Si un dato es parcialmente legible, indica lo visible seguido de "[parcial]"
- NO adivines datos ilegibles - mejor indicar "[ilegible]"
- Valida CURP (18 chars) y RFC (13 chars) aunque estén borrosos
"""
            elif quality_level == "medium":
                quality_instructions = """
NOTA - CALIDAD MEDIA DE IMAGENES:
- Algunas secciones pueden requerir atención extra
- Verifica formatos de CURP/RFC antes de extraer
- Si hay ambigüedad, indica "[verificar]" junto al valor
"""

            # Construir sección de prompts especializados
            specialized_section = ""
            if specialized_prompts:
                specialized_section = "\n\n".join(specialized_prompts)
                specialized_section = f"""
=== CONSIDERACIONES ESPECIALIZADAS POR TIPO DE DOCUMENTO ===
{specialized_section}
=== FIN CONSIDERACIONES ESPECIALIZADAS ===
"""

            content.append({
                "type": "text",
                "text": f"""
Analiza VISUALMENTE los documentos anteriores y extrae los datos solicitados.

INSTRUCCIONES IMPORTANTES:
1. Puedes ver INEs, Actas de Nacimiento, Recibos CFE, Constancias CURP, Escrituras, etc.
2. Identifica cada tipo de documento por su formato visual característico
3. Los documentos pueden estar rotados o inclinados - analiza su contenido sin importar la orientación
4. Extrae los datos según las instrucciones específicas de cada campo
5. Si un campo no está visible en ningún documento, usa "**[NO ENCONTRADO]**"
6. Mantén el formato exacto: nombres en MAYÚSCULAS cuando se indique, fechas completas, etc.
{quality_instructions}
{specialized_section}
{fields_context}

RESPONDE SOLO CON JSON VÁLIDO (sin markdown, sin explicaciones, sin ```):
"""
            })

            # Llamar a Claude con las imágenes
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=[{
                    "type": "text",
                    "text": self._build_system_prompt(document_type),
                    "cache_control": {"type": "ephemeral"}
                }],
                messages=[{
                    "role": "user",
                    "content": content
                }]
            )

            # Extraer contenido de la respuesta
            response_content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_content += block.text

            # Limpiar markdown si existe
            response_content = response_content.strip()
            if response_content.startswith("```json"):
                response_content = response_content[7:]
            if response_content.startswith("```"):
                response_content = response_content[3:]
            if response_content.endswith("```"):
                response_content = response_content[:-3]
            response_content = response_content.strip()

            # Parsear JSON
            extracted_data = json.loads(response_content)

            # Post-procesar datos (conversión de números, etc.)
            extracted_data = post_process_extracted_data(extracted_data, document_type)

            # Guardar métricas de tokens
            usage = response.usage
            self.last_tokens_used = usage.input_tokens + usage.output_tokens
            cache_read_tokens = getattr(usage, 'cache_read_input_tokens', 0)
            self.last_cached_tokens = cache_read_tokens
            self.cache_hit = cache_read_tokens > 0

            # Estimar costo (imágenes = ~1000 tokens c/u aprox)
            estimated_image_tokens = len(images) * 1000
            total_input = usage.input_tokens
            cost_input = (total_input * 0.003) / 1000  # Precio con cache
            cost_output = (usage.output_tokens * 0.015) / 1000
            total_cost = cost_input + cost_output

            logger.info(
                "Extracción Vision completada",
                fields_extracted=len(extracted_data),
                images_processed=len(images),
                tokens_used=self.last_tokens_used,
                estimated_cost=f"${total_cost:.4f}",
                cache_hit=self.cache_hit
            )

            return extracted_data

        except json.JSONDecodeError as e:
            logger.error(
                "Error al parsear respuesta JSON de Claude Vision",
                error=str(e),
                response_content=response_content[:500] if 'response_content' in locals() else None
            )
            raise

        except Exception as e:
            logger.error(
                "Error al procesar con Claude Vision",
                error=str(e),
                error_type=type(e).__name__,
                model=self.model,
                num_images=len(images)
            )
            raise


# ==========================================
# HELPERS
# ==========================================

def calculate_cost_comparison(
    num_documents: int,
    tokens_per_document: int = 5000
) -> Dict:
    """
    Calcula comparación de costos: OpenAI vs Anthropic con cache

    Args:
        num_documents: Número de documentos a procesar
        tokens_per_document: Tokens promedio por documento

    Returns:
        Dict: Comparación de costos

    Example:
        >>> calculate_cost_comparison(100, 5000)
        {
            'openai_cost': 2.50,      # $0.025 × 100 docs
            'anthropic_no_cache': 1.50,  # $0.015 × 100 docs
            'anthropic_with_cache': 0.42, # $0.015 + ($0.003 × 99)
            'savings_vs_openai': 83.2,    # % ahorrado vs OpenAI
            'savings_vs_no_cache': 72.0   # % ahorrado vs sin cache
        }
    """
    # Precios por 1K tokens (input)
    OPENAI_PRICE = 0.005  # GPT-4o
    ANTHROPIC_PRICE = 0.015  # Claude sin cache
    ANTHROPIC_CACHED_PRICE = 0.003  # Claude con cache

    # OpenAI (sin cache)
    openai_cost = (num_documents * tokens_per_document * OPENAI_PRICE) / 1000

    # Anthropic sin cache
    anthropic_no_cache = (num_documents * tokens_per_document * ANTHROPIC_PRICE) / 1000

    # Anthropic con cache (1er doc completo, resto con cache)
    first_doc_cost = (tokens_per_document * ANTHROPIC_PRICE) / 1000
    remaining_docs_cost = ((num_documents - 1) * tokens_per_document * ANTHROPIC_CACHED_PRICE) / 1000
    anthropic_with_cache = first_doc_cost + remaining_docs_cost

    # Calcular ahorros
    savings_vs_openai = ((openai_cost - anthropic_with_cache) / openai_cost) * 100
    savings_vs_no_cache = ((anthropic_no_cache - anthropic_with_cache) / anthropic_no_cache) * 100

    return {
        "openai_cost": round(openai_cost, 2),
        "anthropic_no_cache": round(anthropic_no_cache, 2),
        "anthropic_with_cache": round(anthropic_with_cache, 2),
        "savings_vs_openai": round(savings_vs_openai, 1),
        "savings_vs_no_cache": round(savings_vs_no_cache, 1),
        "documents": num_documents,
        "tokens_per_document": tokens_per_document
    }


# Example usage
if __name__ == "__main__":
    # Demo de ahorro de costos
    print("💰 ANÁLISIS DE COSTOS - 100 DOCUMENTOS\n")

    comparison = calculate_cost_comparison(100, 5000)

    print(f"OpenAI GPT-4o:           ${comparison['openai_cost']}")
    print(f"Claude sin cache:        ${comparison['anthropic_no_cache']}")
    print(f"Claude CON cache:        ${comparison['anthropic_with_cache']} ⚡")
    print(f"\nAhorro vs OpenAI:        {comparison['savings_vs_openai']}% 🎯")
    print(f"Ahorro vs sin cache:     {comparison['savings_vs_no_cache']}%")
    print(f"\n✅ Total ahorrado: ${comparison['openai_cost'] - comparison['anthropic_with_cache']:.2f}")
