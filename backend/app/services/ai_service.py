"""
ControlNot v2 - AI Service
Extracción de datos estructurados con LLMs (OpenRouter + OpenAI)
MEJORA CRÍTICA: Soporte multi-provider con OpenRouter

Migrado de por_partes.py líneas 1745-1789, 1418-1422
Original: Solo OpenAI GPT-4o
Mejorado: OpenRouter (GPT-4o, Claude, Gemini, Llama) + OpenAI fallback
"""
import json
from typing import Dict, List, Optional
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

logger = structlog.get_logger()


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

        prompt = f"""Eres un asistente experto en extracción de datos notariales.

TAREA: Extrae información estructurada del siguiente texto de documentos notariales.

TIPO DE DOCUMENTO: {document_type}

CAMPOS A EXTRAER:
{fields_list}{placeholders_section}

INSTRUCCIONES:
1. Extrae SOLO información que esté explícitamente presente en el texto
2. Para campos no encontrados, usa: "**[NO ENCONTRADO]**"
3. Mantén el formato exacto de nombres, fechas y números
4. Para fechas, usa formato: DD/MM/AAAA
5. Para dinero, incluye símbolo de moneda: $X,XXX.XX MXN
6. Los nombres deben incluir apellidos completos
7. Sé preciso y no inventes información

TEXTO A PROCESAR:
{text}

RESPONDE EN FORMATO JSON con las claves exactas de los campos solicitados.
"""

        return prompt

    def process_text_dynamic(
        self,
        text: str,
        document_type: str,
        placeholders: Optional[List[str]] = None,
        temperature: float = 0.3,
        max_tokens: int = 3000
    ) -> Dict[str, str]:
        """
        Procesa texto con LLM para extraer datos estructurados

        FUNCIÓN PRINCIPAL del servicio

        Args:
            text: Texto del cual extraer información
            document_type: Tipo de documento ('compraventa', 'donacion', etc.)
            placeholders: Lista opcional de placeholders del template
            temperature: Temperatura del modelo (0.0-1.0)
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
