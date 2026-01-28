"""
ControlNot v2 - Cancelacion Service
Servicio especializado para procesamiento de Cancelaciones de Hipotecas

OPTIMIZADO: Prompt simplificado estilo movil_cancelaciones.py
CORRECCIÓN CRÍTICA: Usar CLAVES_ESTANDARIZADAS_LEGACY exactas del original
"""
import re
import json
import structlog
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from app.models.cancelacion import CancelacionKeys, CANCELACION_METADATA

logger = structlog.get_logger()


# ==============================================================================
# CLAVES_ESTANDARIZADAS_LEGACY - Copia EXACTA de movil_cancelaciones.py (líneas 221-253)
# CRÍTICO: Estas son las claves que FUNCIONAN al 100% en extracción
# ==============================================================================
CLAVES_ESTANDARIZADAS_LEGACY = {
    "intermediario_financiero": "Extrae el intermediario financiero del texto.",
    "deudor": "Extrae el deudor del texto legal. Ejemplo: 'Juan Pérez Gómez'",
    "numero_escritura": "Extrae el número de escritura en letras y mayúsculas. Ejemplo: 125 → 'CIENTO VEINTICINCO'",
    "fecha_escritura": "Extrae la fecha de la escritura en palabras minúsculas. Ejemplo: 'veinticinco de marzo de dos mil veinticuatro'",
    "notario": "Extrae el nombre del notario, añadiendo de la Licenciada o del Lincenciado antes del nombre, según el género. Ejemplo: 'del Lincenciado Roberto Sánchez Martínez'",
    "numero_notario": "Extrae el número del notario en letras minúsculas. Ejemplo: 15 → 'quince'",
    "ciudad_residencia": "Extrae la ciudad de residencia del notario público. Ejemplo: 'Morelia'",
    "numero_registro_libro_propiedad": "Extrae el número de registro de la propiedad y conviértelo en palabras mayúsculas. Ejemplo: 19 → 'DIECINUEVE'",
    "tomo_libro_propiedad": "Extrae el tomo del libro de propiedad y conviértelo en palabras mayúsculas. Ejemplo: 7069 → 'SIETE MIL SESENTA Y NUEVE'",
    "numero_registro_libro_gravamen": "Extrae el número de registro del gravamen y conviértelo en palabras mayúsculas. Ejemplo: 4 → 'CUATRO'",
    "tomo_libro_gravamen": "Extrae el tomo del libro de gravamen y conviértelo en palabras mayúsculas. Ejemplo: 4 → 'CUATRO'",
    "suma_credito": "Extrae la suma de crédito con garantía hipotecaria. Ejemplo: '$250,000.00'",
    "suma_credito_letras": "Extrae la suma de crédito en letras y mayúsculas. Ejemplo: $250,000.00' → 'DOSCIENTOS CINCUENTA MIL'",
    "equivalente_salario_minimo": "Extrae el equivalente en salario mínimo (número). Ejemplo: '500'",
    "equivalente_salario_minimo_letras": "Extrae el equivalente en salario mínimo en letras mayúsculas. Ejemplo: 500 → 'QUINIENTOS'",
    "ubicacion_inmueble": "Extrae la ubicación del inmueble hipotecado y su tipo. Ejemplo: 'CASA HABITACIÓN UBICADA EN LA CALLE PRIMER RETORNO DE LA ESTACAS, NUMERO 49 (CUARENTA Y NUEVE), CASA \"B\", CONSTRUIDA SOBRE EL LOTE NUMERO 136 (CIENTO TREINTA Y SEIS), DE LA MANZANA 8 (OCHO), PERTENECIENTE AL CONJUNTO HABITACIONAL DE INTERÉS SOCIAL BAJO EL RÉGIMEN DE PROPIEDAD EN CONDOMINIO, LOMAS DE LA MAESTRANZA, DE ESTE MUNICIPIO DE MORELIA, MICHOACAN'",
    "cesion_credito_fecha": "Extrae la fecha de la cesión de crédito en palabras minúsculas. Ejemplo: 'quince de julio de dos mil veintitrés'",
    "cesion_credito_valor": "Extrae cuántos derechos hipotecarios se transmitieron en la cesión en palabras minúsculas. Ejemplo: 'tres derechos hipotecarios'",
    "constancia_finiquito_numero_oficio": "Extrae el número de oficio de la constancia de finiquito. Ejemplo: 'OFICIO NO. JSGR-PROG-30-60/2023/4885'",
    "constancia_finiquito_fecha_emision": "Extrae la fecha de emisión de la constancia de finiquito en palabras minúsculas. Ejemplo: 'doce de junio de dos mil veintidós'",
    "carta_instrucciones_numero_oficio": "Extrae el número de oficio de la carta de instrucciones en el formato EXP. No. CANC-SOFOL/XXXX/XX. Ejemplo: 'EXP. No. CANC-SOFOL/2023/12'",
    "carta_instrucciones_fecha_constancia_liquidacion": "Extrae la fecha de la constancia de liquidación en palabras minúsculas. Ejemplo: 'veinte de abril de dos mil veintidós'",
    "carta_instrucciones_nombre_titular_credito": "Extrae el nombre del titular del crédito. Ejemplo: 'María López Ramírez'",
    "carta_instrucciones_numero_credito": "Extrae el número de crédito. Ejemplo: '123456789'",
    "carta_instrucciones_tipo_credito": "Extrae el tipo de crédito",
    "carta_instrucciones_fecha_adjudicacion": "Extrae la fecha de adjudicación del crédito en palabras minúsculas. Ejemplo: 'uno de marzo de dos mil veintiuno'",
    "carta_instrucciones_ubicacion_inmueble": "Extrae la ubicación del inmueble. Ejemplo: 'CASA HABITACIÓN UBICADA EN LA CALLE PRIMER RETORNO DE LA ESTACAS, NUMERO 49 (CUARENTA Y NUEVE), CASA \"B\", CONSTRUIDA SOBRE EL LOTE NUMERO 136 (CIENTO TREINTA Y SEIS), DE LA MANZANA 8 (OCHO), PERTENECIENTE AL CONJUNTO HABITACIONAL DE INTERÉS SOCIAL BAJO EL RÉGIMEN DE PROPIEDAD EN CONDOMINIO, LOMAS DE LA MAESTRANZA, DE ESTE MUNICIPIO DE MORELIA, MICHOACÁN'",
    "carta_instrucciones_valor_credito": "Extrae el valor del crédito. Ejemplo: '500000'",
    "carta_instrucciones_valor_credito_letras": "Extrae el valor del crédito en letras y mayúsculas. Ejemplo: 500000 → 'QUINIENTOS MIL'",
    "carta_instrucciones_numero_registro": "Extrae el número de registro del crédito en palabras mayúsculas. Ejemplo: 302 → 'TRESCIENTOS DOS'",
    "carta_instrucciones_tomo": "Extrae el tomo donde se inscribió el crédito en palabras mayúsculas. Ejemplo: 27 → 'VEINTISIETE'",
}


class CancelacionService:
    """
    Servicio para procesamiento de documentos de Cancelación de Hipotecas

    Proporciona métodos especializados para:
    - Obtención de categorías de documentos
    - Validación de datos financieros
    - Procesamiento de campos específicos
    - Generación de prompts optimizados para IA (estilo movil_cancelaciones.py)
    """

    def __init__(self):
        self.metadata = CANCELACION_METADATA

    def get_categories(self) -> Dict:
        """
        Obtiene las categorías de documentos necesarios para una cancelación de hipoteca

        Returns:
            Dict: Categorías organizadas en parte_a, parte_b, otros
        """
        return {
            "parte_a": {
                "nombre": "Documentos del Deudor/Propietario",
                "icono": "👤",
                "descripcion": "Identificaciones y documentos personales del propietario del inmueble",
                "documentos": [
                    "INE o IFE (ambos lados)",
                    "RFC (Constancia de Situación Fiscal)",
                    "CURP",
                    "Comprobante de domicilio actualizado (máximo 3 meses)",
                    "Estado de cuenta bancario (opcional)"
                ],
                "requeridos": ["INE", "RFC"],
                "color": "#3B82F6"
            },
            "parte_b": {
                "nombre": "Documentos del Banco/Acreedor",
                "icono": "🏦",
                "descripcion": "Documentos oficiales emitidos por la institución financiera",
                "documentos": [
                    "Constancia de No Adeudo o Finiquito",
                    "Carta de Instrucciones del Banco",
                    "Poder Notarial del representante del banco",
                    "Estado de cuenta final del crédito",
                    "Constancia de liquidación"
                ],
                "requeridos": ["Constancia de No Adeudo", "Carta de Instrucciones", "Poder Notarial"],
                "color": "#10B981"
            },
            "otros": {
                "nombre": "Documentos del Inmueble y Registrales",
                "icono": "🏠",
                "descripcion": "Documentación del inmueble hipotecado y registros públicos",
                "documentos": [
                    "Escritura original de la hipoteca",
                    "Certificado de Libertad de Gravamen (RPP)",
                    "Certificado de Inscripción registral",
                    "Certificado catastral del inmueble",
                    "Boleta predial actualizada",
                    "Escritura de cesión de crédito (si aplica)"
                ],
                "requeridos": ["Escritura de Hipoteca", "Certificado de Libertad de Gravamen"],
                "color": "#F59E0B"
            }
        }

    def get_required_documents(self) -> List[str]:
        """
        Obtiene la lista de documentos CRÍTICOS para una cancelación

        Returns:
            List[str]: Lista de documentos absolutamente necesarios
        """
        return [
            "Constancia de No Adeudo del Banco",
            "Carta de Instrucciones del Banco",
            "Poder Notarial del Representante del Banco",
            "Escritura Original de la Hipoteca",
            "Certificado de Libertad de Gravamen",
            "INE del Deudor",
            "RFC del Deudor"
        ]

    def validate_salario_minimo(self, monto_credito: Optional[float]) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Calcula y valida el equivalente en salarios mínimos (VSMGM)

        IMPORTANTE: Requerido por ley para créditos de vivienda en México

        Args:
            monto_credito: Monto del crédito en pesos

        Returns:
            Tuple[bool, Optional[float], Optional[str]]:
                - válido: si el cálculo fue exitoso
                - equivalente_num: número de salarios mínimos
                - equivalente_letras: número en letras MAYÚSCULAS
        """
        if not monto_credito or monto_credito <= 0:
            return False, None, None

        # Salario mínimo general vigente 2024 (actualizar anualmente)
        SALARIO_MINIMO_VIGENTE = 248.93  # pesos diarios

        try:
            equivalente = round(monto_credito / SALARIO_MINIMO_VIGENTE, 2)

            # Convertir a letras (implementación básica)
            equivalente_letras = self._numero_a_letras(int(equivalente))
            equivalente_letras = f"{equivalente_letras} VECES EL SALARIO MÍNIMO"

            logger.info(
                "Equivalente en salarios mínimos calculado",
                monto_credito=monto_credito,
                equivalente=equivalente,
                salario_minimo=SALARIO_MINIMO_VIGENTE
            )

            return True, equivalente, equivalente_letras

        except Exception as e:
            logger.error("Error al calcular equivalente en salarios mínimos", error=str(e))
            return False, None, None

    def validate_numero_credito(self, numero: str) -> bool:
        """
        Valida formato de número de crédito bancario

        Args:
            numero: Número de crédito a validar

        Returns:
            bool: True si el formato es válido
        """
        if not numero:
            return False

        # Eliminar espacios y guiones
        numero_limpio = re.sub(r'[\s\-]', '', numero)

        # Debe tener entre 6 y 20 dígitos
        if len(numero_limpio) < 6 or len(numero_limpio) > 20:
            return False

        # Debe contener solo números
        if not numero_limpio.isdigit():
            return False

        return True

    def validate_folio_real(self, folio: str) -> bool:
        """
        Valida formato de folio real del Registro Público

        Args:
            folio: Número de folio real

        Returns:
            bool: True si el formato es válido
        """
        if not folio:
            return False

        folio_limpio = re.sub(r'[\s\-]', '', folio)

        # Debe tener entre 4 y 10 dígitos
        if len(folio_limpio) < 4 or len(folio_limpio) > 10:
            return False

        # Puede contener números y letras
        if not folio_limpio.isalnum():
            return False

        return True

    def extract_carta_instrucciones_fields(self, extracted_data: Dict) -> Dict:
        """
        Extrae y valida campos específicos de la Carta de Instrucciones

        Args:
            extracted_data: Diccionario con datos extraídos por IA

        Returns:
            Dict: Campos de carta de instrucciones validados
        """
        carta_fields = {}
        carta_prefix = "Carta_Instrucciones_"

        for key, value in extracted_data.items():
            if key.startswith(carta_prefix):
                carta_fields[key] = value

        logger.info(
            "Campos de Carta de Instrucciones extraídos",
            total_campos=len(carta_fields),
            campos=list(carta_fields.keys())
        )

        return carta_fields

    def validate_cancelacion_data(self, data: Dict) -> Tuple[bool, List[str], Dict]:
        """
        Valida completitud y coherencia de datos de cancelación

        Args:
            data: Diccionario con datos extraídos

        Returns:
            Tuple[bool, List[str], Dict]:
                - válido: True si pasa todas las validaciones
                - errores: Lista de errores encontrados
                - warnings: Diccionario con advertencias no críticas
        """
        errors = []
        warnings = {}

        # Validar campos críticos (ajustados según PDF documentos notaria)
        campos_criticos = self.metadata['campos_criticos']

        for campo in campos_criticos:
            value = data.get(campo)
            if not value or value == "NO LOCALIZADO" or value == "NO ENCONTRADO":
                errors.append(f"Campo crítico faltante: {campo}")

        # Validar formato de número de crédito en carta de instrucciones
        numero_credito = data.get("Carta_Instrucciones_Numero_Credito")
        if numero_credito and not self.validate_numero_credito(numero_credito):
            warnings["numero_credito"] = "Formato de número de crédito inválido"

        # Validar que exista monto de crédito
        suma_credito = data.get("Suma_Credito")
        if not suma_credito or suma_credito == "NO LOCALIZADO":
            errors.append("Debe existir el monto de crédito (Suma_Credito)")

        # Validar equivalente en salarios mínimos (requerido por ley)
        equiv_salario = data.get("Equivalente_Salario_Minimo")
        if not equiv_salario or equiv_salario == "NO LOCALIZADO":
            warnings["equivalente_salario"] = "Equivalente en salarios mínimos no encontrado (requerido por ley)"

        # Validar datos registrales (libro propiedad)
        if not data.get("Numero_Registro_Libro_Propiedad"):
            warnings["registro_propiedad"] = "Falta número de registro en libro de propiedad"

        # Validar datos registrales (libro gravamen)
        if not data.get("Numero_Registro_Libro_Gravamen"):
            warnings["registro_gravamen"] = "Falta número de registro en libro de gravamen"

        is_valid = len(errors) == 0

        logger.info(
            "Validación de datos de cancelación",
            valido=is_valid,
            errores=len(errors),
            warnings=len(warnings)
        )

        return is_valid, errors, warnings

    def get_simple_keys_dict(self) -> Dict[str, str]:
        """
        Genera un diccionario simple de claves con sus descriptions
        ESTILO MOVIL_CANCELACIONES.PY - Claves simples para mejor extracción

        Returns:
            Dict[str, str]: Diccionario {campo: descripción_simple}
        """
        claves_simples = {}

        for field_name, field_info in CancelacionKeys.model_fields.items():
            desc = field_info.description or f"Extrae {field_name}"
            # La descripción ya está simplificada en el modelo
            claves_simples[field_name] = desc

        return claves_simples

    def get_extraction_prompt(self, document_type: str = "cancelacion") -> str:
        """
        Genera un prompt SIMPLIFICADO para extracción de datos con IA
        ESTILO MOVIL_CANCELACIONES.PY - Prompt IDÉNTICO al original que funciona 100%

        Args:
            document_type: Tipo de documento (siempre 'cancelacion')

        Returns:
            str: Prompt formateado para el modelo de IA
        """
        # PROMPT SIMPLE - IDÉNTICO a movil_cancelaciones.py líneas 332-333
        system_message = "Eres controlnot, un asistente de notaría. Extrae información en formato JSON con las siguientes especificaciones:\n"
        system_message += json.dumps(CLAVES_ESTANDARIZADAS_LEGACY, indent=4, ensure_ascii=False)
        return system_message

    def get_extraction_prompt_legacy(self) -> str:
        """
        Genera el prompt EXACTO de movil_cancelaciones.py
        Para uso con process_text_with_openai_legacy()

        Returns:
            str: Prompt idéntico al sistema original
        """
        system_message = "Eres controlnot, un asistente de notaría. Extrae información en formato JSON con las siguientes especificaciones:\n"
        system_message += json.dumps(CLAVES_ESTANDARIZADAS_LEGACY, indent=4, ensure_ascii=False)
        return system_message

    def process_text_with_openai_legacy(self, text: str, openai_client) -> Dict:
        """
        Procesa texto EXACTAMENTE como movil_cancelaciones.py (líneas 329-350)

        USA LOS PARÁMETROS EXACTOS QUE FUNCIONAN:
        - model: gpt-4o
        - temperature: 0.5
        - max_tokens: 1500
        - top_p: 1

        Args:
            text: Texto OCR extraído de los documentos
            openai_client: Cliente de OpenAI

        Returns:
            Dict: Datos extraídos con formato **valor** para negrita
        """
        try:
            system_message = self.get_extraction_prompt_legacy()

            logger.info(
                "Procesando con método legacy (movil_cancelaciones.py)",
                text_length=len(text),
                claves_count=len(CLAVES_ESTANDARIZADAS_LEGACY)
            )

            # PARÁMETROS EXACTOS de movil_cancelaciones.py líneas 335-344
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Extrae la información en formato JSON del siguiente texto:\n{text}"}
                ],
                temperature=0.5,  # CRÍTICO: 0.5 no 0.0
                max_tokens=1500,  # CRÍTICO: 1500 no 3000
                top_p=1           # CRÍTICO: top_p=1
            )

            content = response.choices[0].message.content.strip()

            # Limpiar markdown si existe (línea 347)
            cleaned_content = re.sub(r"```json|```", "", content)

            # Parsear JSON (línea 348)
            extracted_data = json.loads(cleaned_content)

            # Formatear con negrita para Word (línea 350)
            formatted_data = {
                key: f"**{value.strip()}**" if isinstance(value, str) else f"**{value}**"
                for key, value in extracted_data.items()
            }

            logger.info(
                "Extracción legacy completada",
                campos_extraidos=len(formatted_data),
                campos_con_valor=[k for k, v in extracted_data.items() if v and v != "NO LOCALIZADO"]
            )

            return formatted_data

        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error al procesar con OpenAI: {str(e)}")
            return {}

    def _numero_a_letras(self, numero: int) -> str:
        """
        Convierte número entero a palabras en español (MAYÚSCULAS)

        Implementación básica para números hasta 999,999

        Args:
            numero: Número entero a convertir

        Returns:
            str: Número en palabras MAYÚSCULAS
        """
        unidades = ["", "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        especiales = ["DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE",
                      "DIECISÉIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"]
        decenas = ["", "DIEZ", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA",
                   "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
        centenas = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                    "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]

        if numero == 0:
            return "CERO"

        if numero == 100:
            return "CIEN"

        if numero < 10:
            return unidades[numero]

        if numero < 20:
            return especiales[numero - 10]

        if numero < 100:
            d, u = divmod(numero, 10)
            if d == 2 and u > 0:
                return f"VEINTI{unidades[u]}"
            elif u == 0:
                return decenas[d]
            else:
                return f"{decenas[d]} Y {unidades[u]}"

        if numero < 1000:
            c, resto = divmod(numero, 100)
            if resto == 0:
                return centenas[c] if c != 1 else "CIEN"
            else:
                return f"{centenas[c]} {self._numero_a_letras(resto)}"

        if numero < 1000000:
            miles, resto = divmod(numero, 1000)
            if miles == 1:
                prefijo = "MIL"
            else:
                prefijo = f"{self._numero_a_letras(miles)} MIL"

            if resto == 0:
                return prefijo
            else:
                return f"{prefijo} {self._numero_a_letras(resto)}"

        # Para números mayores, usar representación simple
        return str(numero)


# Instancia singleton del servicio
cancelacion_service = CancelacionService()


# Funciones de conveniencia
def get_cancelacion_categories() -> Dict:
    """Wrapper para obtener categorías de cancelación"""
    return cancelacion_service.get_categories()


def validate_cancelacion_data(data: Dict) -> Tuple[bool, List[str], Dict]:
    """Wrapper para validar datos de cancelación"""
    return cancelacion_service.validate_cancelacion_data(data)


def get_cancelacion_prompt() -> str:
    """Wrapper para obtener prompt de extracción"""
    return cancelacion_service.get_extraction_prompt()


def get_simple_keys() -> Dict[str, str]:
    """Wrapper para obtener claves simples"""
    return cancelacion_service.get_simple_keys_dict()


def get_legacy_keys() -> Dict[str, str]:
    """
    Wrapper para obtener CLAVES_ESTANDARIZADAS_LEGACY exactas
    Estas son las claves que funcionan 100% en movil_cancelaciones.py
    """
    return CLAVES_ESTANDARIZADAS_LEGACY


def get_cancelacion_prompt_legacy() -> str:
    """
    Wrapper para obtener el prompt EXACTO de movil_cancelaciones.py
    """
    return cancelacion_service.get_extraction_prompt_legacy()


def process_cancelacion_legacy(text: str, openai_client) -> Dict:
    """
    Procesa texto de cancelación EXACTAMENTE como movil_cancelaciones.py

    PARÁMETROS USADOS (idénticos al original):
    - model: gpt-4o
    - temperature: 0.5
    - max_tokens: 1500
    - top_p: 1

    Args:
        text: Texto OCR de documentos de cancelación
        openai_client: Cliente de OpenAI inicializado

    Returns:
        Dict: Datos extraídos con formato **valor** para negrita en Word

    Example:
        >>> from openai import OpenAI
        >>> client = OpenAI(api_key="...")
        >>> result = process_cancelacion_legacy(texto_ocr, client)
        >>> print(result['deudor'])  # → "**Juan Pérez Gómez**"
    """
    return cancelacion_service.process_text_with_openai_legacy(text, openai_client)
