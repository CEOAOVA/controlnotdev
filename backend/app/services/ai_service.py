"""
ControlNot v2 - AI Service
Extracción de datos estructurados con LLMs (OpenRouter + OpenAI)

=== BEST PRACTICES OPENAI COOKBOOK ===
https://cookbook.openai.com/examples/data_extraction_transformation

| Configuración           | Valor Recomendado              |
|-------------------------|--------------------------------|
| temperature             | 0.0 (determinista)             |
| response_format         | {"type": "json_object"}        |
| Prompt: interpolación   | "Don't interpolate or make up" |
| Prompt: campos vacíos   | "Include blank as null"        |

MEJORA CRÍTICA: Soporte multi-provider con OpenRouter + Cache de extracciones
"""
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
import structlog

from openai import OpenAI
from pydantic import BaseModel

from app.core.config import settings
from app.models.base import BaseKeys
from app.models.compraventa import CompraventaKeys
from app.models.donacion import DonacionKeys
from app.models.testamento import TestamentoKeys
from app.models.poder import PoderKeys
from app.models.sociedad import SociedadKeys
from app.database import get_supabase_client

logger = structlog.get_logger()
supabase = get_supabase_client()


class AIExtractionService:
    """
    Servicio de extracción de datos con LLMs

    MEJORA CRÍTICA: Soporte multi-provider
    - OpenRouter: Acceso a múltiples modelos (GPT-4o, Claude, Gemini, Llama)
    - OpenAI: Fallback directo si OpenRouter falla
    - Configuración dinámica vía settings
    """

    # Mapeo de tipos de documento a modelos Pydantic
    MODEL_MAP = {
        "compraventa": CompraventaKeys,
        "donacion": DonacionKeys,
        "testamento": TestamentoKeys,
        "poder": PoderKeys,
        "sociedad": SociedadKeys
    }

    def __init__(self, ai_client: OpenAI):
        """
        Args:
            ai_client: Cliente de OpenAI o OpenRouter (from dependencies)
        """
        self.ai_client = ai_client
        self.provider = settings.active_ai_provider  # "OpenRouter" o "OpenAI"
        self.model = settings.active_model  # e.g., "openai/gpt-4o" o "gpt-4o"
        self.last_tokens_used = 0  # Tokens usados en el último request

        logger.info(
            "AIExtractionService inicializado",
            provider=self.provider,
            model=self.model
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

    def _build_extraction_prompt(
        self,
        text: str,
        document_type: str,
        placeholders: Optional[List[str]] = None
    ) -> str:
        """
        Construye el prompt para extracción de datos

        Args:
            text: Texto del cual extraer información
            document_type: Tipo de documento
            placeholders: Lista opcional de placeholders específicos a buscar

        Returns:
            str: Prompt formateado
        """
        # Obtener modelo y sus campos
        model_class = self._get_model_for_type(document_type)
        fields = list(model_class.model_fields.keys())

        # Construir lista de campos
        fields_list = "\n".join([f"- {field}" for field in fields])

        # Si hay placeholders específicos, añadirlos
        if placeholders:
            placeholders_list = "\n".join([f"- {ph}" for ph in placeholders])
            placeholders_section = f"\n\nPLACEHOLDERS ESPECÍFICOS DEL TEMPLATE:\n{placeholders_list}"
        else:
            placeholders_section = ""

        # Prompt basado en OpenAI Cookbook best practices:
        # https://cookbook.openai.com/examples/data_extraction_transformation
        prompt = f"""Eres una herramienta de extracción de datos notariales mexicanos.

=== INSTRUCCIONES CRÍTICAS (OpenAI Best Practices) ===
1. **NO INTERPOLES NI INVENTES DATOS** - Extrae SOLO información explícitamente presente
2. Para campos no encontrados, usa: null (no inventes valores)
3. NO asumas, NO deduzcas, NO completes información faltante
4. Para tablas, incluye TODAS las filas y columnas
5. Preserva el idioma y formato original del documento

TIPO DE DOCUMENTO: {document_type}

CAMPOS A EXTRAER (JSON keys exactas):
{fields_list}{placeholders_section}

REGLAS DE FORMATO:
- Fechas: DD/MM/AAAA (ej: 15/03/2024)
- Dinero: $X,XXX.XX MXN (ej: $150,000.00 MXN)
- CURP: 18 caracteres exactos
- RFC: 12-13 caracteres
- Nombres: Incluir apellidos completos como aparecen
- Direcciones: Copiar textualmente del documento

TEXTO A PROCESAR:
---
{text}
---

Responde SOLO con JSON válido. Para campos no encontrados usa null.
"""

        return prompt

    def process_text_structured(
        self,
        text: str,
        document_type: str,
        placeholders: Optional[List[str]] = None,
        temperature: float = 0.0,  # OpenAI Cookbook: "0 is best for factual extraction"
        max_tokens: int = 3000
    ) -> Dict[str, str]:
        """
        Procesa texto con Structured Outputs (OpenAI beta - 0 errores JSON)

        === OPENAI COOKBOOK BEST PRACTICES ===
        - temperature=0: Determinista para extracción de datos
        - response_format=Pydantic: Garantiza schema válido
        - "Don't interpolate or make up data"

        Garantiza:
        - 0 errores JSON (schema enforcement)
        - Respuesta siempre válida según Pydantic model
        - Sin necesidad de json.loads() manual
        - Manejo automático de refusals

        Args:
            text: Texto del cual extraer información
            document_type: Tipo de documento
            placeholders: Lista opcional de placeholders
            temperature: 0.0 recomendado para extracción (OpenAI)
            max_tokens: Máximo de tokens

        Returns:
            Dict[str, str]: Diccionario con campos extraídos

        Example:
            >>> result = ai_service.process_text_structured(text, "compraventa")
            >>> # Garantizado: result tiene estructura exacta de CompraventaKeys
        """
        logger.info(
            "Procesando con Structured Outputs",
            doc_type=document_type,
            text_length=len(text),
            model=self.model
        )

        try:
            # Obtener modelo Pydantic para el documento
            model_class = self._get_model_for_type(document_type)

            # Construir prompt
            prompt = self._build_extraction_prompt(text, document_type, placeholders)

            # Llamar con Structured Outputs (beta API)
            completion = self.ai_client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en extracción de datos de documentos notariales mexicanos."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format=model_class,  # Pydantic model directo!
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extraer datos parseados (ya es objeto Pydantic)
            message = completion.choices[0].message

            # Manejar refusals (si el modelo rehúsa responder)
            if message.refusal:
                logger.error(
                    "Modelo rehusó responder",
                    refusal=message.refusal
                )
                raise Exception(f"AI refusal: {message.refusal}")

            # Obtener datos parseados
            parsed_data = message.parsed

            # Convertir Pydantic model a dict
            extracted_data = parsed_data.model_dump()

            # Guardar tokens
            if hasattr(completion, 'usage') and completion.usage:
                self.last_tokens_used = completion.usage.total_tokens
            else:
                self.last_tokens_used = 0

            logger.info(
                "Structured Outputs completado",
                fields_extracted=len(extracted_data),
                tokens_used=self.last_tokens_used,
                model=self.model
            )

            return extracted_data

        except Exception as e:
            logger.error(
                "Error en Structured Outputs",
                error=str(e),
                error_type=type(e).__name__
            )
            # Fallback a método tradicional
            logger.warning("Fallback a process_text_dynamic")
            return self.process_text_dynamic(text, document_type, placeholders, temperature, max_tokens)

    def process_text_dynamic(
        self,
        text: str,
        document_type: str,
        placeholders: Optional[List[str]] = None,
        temperature: float = 0.0,  # OpenAI Cookbook: "0 is best for factual extraction"
        max_tokens: int = 3000
    ) -> Dict[str, str]:
        """
        Procesa texto con LLM para extraer datos estructurados

        === OPENAI COOKBOOK BEST PRACTICES ===
        - temperature=0.0: Determinista para extracción factual
        - response_format=json_object: Garantiza JSON válido
        - "Don't interpolate or make up data"

        FUNCIÓN PRINCIPAL del servicio

        Args:
            text: Texto del cual extraer información
            document_type: Tipo de documento ('compraventa', 'donacion', etc.)
            placeholders: Lista opcional de placeholders del template
            temperature: 0.0 recomendado para extracción (OpenAI)
            max_tokens: Máximo de tokens en la respuesta

        Returns:
            Dict[str, str]: Diccionario con campos extraídos

        Example:
            >>> text = "Juan Pérez vende a María González..."
            >>> result = ai_service.process_text_dynamic(text, "compraventa")
            >>> result
            {
                'Vendedor_Nombre': 'Juan Pérez',
                'Comprador_Nombre': 'María González',
                ...
            }

        Raises:
            Exception: Si falla la extracción
        """
        logger.info(
            "Procesando texto con LLM",
            doc_type=document_type,
            text_length=len(text),
            provider=self.provider,
            model=self.model,
            placeholders_count=len(placeholders) if placeholders else 0
        )

        # ========================================================================
        # CACHE DE EXTRACCIONES: Verificar si ya procesamos este texto
        # ========================================================================
        file_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

        try:
            # Buscar en cache (requiere tenant_id - por ahora sin RLS activo)
            cached_result = supabase.table('extraction_cache')\
                .select('*')\
                .eq('file_hash', file_hash)\
                .eq('document_type', document_type)\
                .execute()

            if cached_result.data and len(cached_result.data) > 0:
                # CACHE HIT - Retornar datos cacheados
                cache_entry = cached_result.data[0]

                logger.info(
                    "CACHE HIT - Extracción recuperada de cache",
                    file_hash=file_hash[:12],
                    document_type=document_type,
                    hit_count=cache_entry.get('hit_count', 0),
                    age_days=(datetime.now() - datetime.fromisoformat(
                        cache_entry['created_at'].replace('Z', '+00:00')
                    )).days
                )

                # Incrementar contador de hits
                supabase.table('extraction_cache')\
                    .update({
                        'hit_count': cache_entry.get('hit_count', 0) + 1,
                        'last_used_at': datetime.now().isoformat()
                    })\
                    .eq('id', cache_entry['id'])\
                    .execute()

                return cache_entry['extracted_data']

        except Exception as cache_error:
            # No fallar si hay error en cache, continuar con extracción normal
            logger.warning(
                "Error al consultar cache, continuando con extracción",
                error=str(cache_error),
                file_hash=file_hash[:12]
            )

        # CACHE MISS - Procesar con LLM
        logger.info(
            "CACHE MISS - Procesando con LLM",
            file_hash=file_hash[:12],
            document_type=document_type
        )

        try:
            # Construir prompt
            prompt = self._build_extraction_prompt(text, document_type, placeholders)

            # Llamar a LLM
            response = self.ai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en extracción de datos de documentos notariales mexicanos."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}  # Forzar respuesta JSON
            )

            # Extraer contenido
            content = response.choices[0].message.content

            # Parsear JSON
            extracted_data = json.loads(content)

            # Guardar tokens usados
            if hasattr(response, 'usage') and response.usage:
                self.last_tokens_used = response.usage.total_tokens
            else:
                self.last_tokens_used = 0

            logger.info(
                "Extracción completada",
                fields_extracted=len(extracted_data),
                provider=self.provider,
                model=self.model,
                tokens_used=self.last_tokens_used
            )

            # ====================================================================
            # GUARDAR EN CACHE para futuras extracciones
            # ====================================================================
            try:
                # Nota: tenant_id será NULL hasta que se active autenticación
                # Por ahora el cache funciona sin tenant_id (RLS deshabilitado temporalmente)
                cache_data = {
                    'file_hash': file_hash,
                    'document_type': document_type,
                    'ocr_text': text[:10000],  # Primeros 10k chars para referencia
                    'extracted_data': extracted_data,
                    'extraction_model': self.model,
                    'extraction_provider': self.provider,
                    'hit_count': 0
                }

                supabase.table('extraction_cache').insert(cache_data).execute()

                logger.info(
                    "Extracción guardada en cache",
                    file_hash=file_hash[:12],
                    document_type=document_type,
                    fields_count=len(extracted_data)
                )

            except Exception as cache_error:
                # No fallar la extracción si falla el guardado en cache
                logger.warning(
                    "Error al guardar en cache (no crítico)",
                    error=str(cache_error),
                    file_hash=file_hash[:12]
                )

            return extracted_data

        except json.JSONDecodeError as e:
            logger.error(
                "Error al parsear respuesta JSON del LLM",
                error=str(e),
                response_content=content if 'content' in locals() else None
            )
            raise

        except Exception as e:
            logger.error(
                "Error al procesar texto con LLM",
                error=str(e),
                error_type=type(e).__name__,
                provider=self.provider,
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
            extracted_data: Datos extraídos por el LLM
            document_type: Tipo de documento

        Returns:
            Dict: Estadísticas de validación:
                - total_fields: int
                - found_fields: int
                - missing_fields: List[str]
                - invalid_fields: List[str]
                - completeness: float (0.0-1.0)
        """
        model_class = self._get_model_for_type(document_type)
        required_fields = set(model_class.model_fields.keys())
        extracted_fields = set(extracted_data.keys())

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

        completeness = len(found_fields) / len(required_fields) if required_fields else 0.0

        stats = {
            "total_fields": len(required_fields),
            "found_fields": len(found_fields),
            "missing_fields": list(missing_fields),
            "not_found_values": not_found_values,
            "completeness": completeness
        }

        logger.info(
            "Validación de datos extraídos",
            doc_type=document_type,
            completeness_percent=f"{completeness * 100:.1f}%",
            **stats
        )

        return stats

    def enrich_with_defaults(
        self,
        extracted_data: Dict[str, str],
        document_type: str
    ) -> Dict[str, str]:
        """
        Enriquece datos extraídos con valores por defecto para campos faltantes

        Args:
            extracted_data: Datos extraídos
            document_type: Tipo de documento

        Returns:
            Dict[str, str]: Datos enriquecidos con todos los campos del modelo
        """
        model_class = self._get_model_for_type(document_type)
        required_fields = model_class.model_fields.keys()

        enriched_data = extracted_data.copy()

        # Añadir campos faltantes con valor por defecto
        for field in required_fields:
            if field not in enriched_data:
                enriched_data[field] = "**[NO ENCONTRADO]**"

        logger.debug(
            "Datos enriquecidos con defaults",
            original_fields=len(extracted_data),
            enriched_fields=len(enriched_data)
        )

        return enriched_data

    def process_with_fallback(
        self,
        text: str,
        document_type: str,
        placeholders: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Procesa texto con fallback automático entre providers

        Intenta con el provider configurado, si falla, intenta con fallback

        Args:
            text: Texto a procesar
            document_type: Tipo de documento
            placeholders: Placeholders opcionales

        Returns:
            Dict[str, str]: Datos extraídos
        """
        try:
            # Intentar con provider principal
            return self.process_text_dynamic(text, document_type, placeholders)

        except Exception as primary_error:
            logger.warning(
                "Error con provider principal, intentando fallback",
                primary_provider=self.provider,
                error=str(primary_error)
            )

            # Si ya estamos usando OpenAI, no hay fallback
            if self.provider == "OpenAI":
                raise

            # Intentar con OpenAI como fallback
            try:
                # Cambiar temporalmente a modelo OpenAI
                original_model = self.model
                self.model = "gpt-4o"

                logger.info("Usando OpenAI como fallback", model=self.model)

                result = self.process_text_dynamic(text, document_type, placeholders)

                # Restaurar modelo original
                self.model = original_model

                return result

            except Exception as fallback_error:
                logger.error(
                    "Fallback también falló",
                    fallback_error=str(fallback_error)
                )
                raise primary_error  # Lanzar error original


def get_available_models() -> List[Dict[str, str]]:
    """
    Retorna lista de modelos disponibles según configuración

    Returns:
        List[Dict]: Lista de modelos con id y nombre
    """
    if settings.use_openrouter:
        return [
            {"id": "openai/gpt-4o", "name": "GPT-4o (OpenAI via OpenRouter)"},
            {"id": "anthropic/claude-3-opus", "name": "Claude 3 Opus (Anthropic)"},
            {"id": "anthropic/claude-3-sonnet", "name": "Claude 3 Sonnet (Anthropic)"},
            {"id": "google/gemini-pro-1.5", "name": "Gemini Pro 1.5 (Google)"},
            {"id": "meta-llama/llama-3-70b-instruct", "name": "Llama 3 70B (Meta)"}
        ]
    else:
        return [
            {"id": "gpt-4o", "name": "GPT-4o (OpenAI)"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo (OpenAI)"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo (OpenAI)"}
        ]
