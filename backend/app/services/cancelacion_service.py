"""
ControlNot v2 - Cancelacion Service
Servicio especializado para procesamiento de Cancelaciones de Hipotecas

Migrado de movil_cancelaciones.py con funcionalidades específicas para:
- Extracción de datos de documentos bancarios
- Validación de campos financieros
- Procesamiento de cartas de instrucciones
- Generación de documentos de cancelación
"""
import re
import structlog
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from app.models.cancelacion import CancelacionKeys, CANCELACION_METADATA

logger = structlog.get_logger()


class CancelacionService:
    """
    Servicio para procesamiento de documentos de Cancelación de Hipotecas

    Proporciona métodos especializados para:
    - Obtención de categorías de documentos
    - Validación de datos financieros
    - Procesamiento de campos específicos
    - Generación de prompts optimizados para IA
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

        # Validar campos críticos
        campos_criticos = self.metadata['campos_criticos']

        for campo in campos_criticos:
            value = data.get(campo)
            if not value or value == "NO LOCALIZADO" or value == "NO ENCONTRADO":
                errors.append(f"Campo crítico faltante: {campo}")

        # Validar formato de número de crédito
        numero_credito = data.get("Numero_Credito")
        if numero_credito and not self.validate_numero_credito(numero_credito):
            warnings["numero_credito"] = "Formato de número de crédito inválido"

        # Validar folio real
        folio_real = data.get("Folio_Real")
        if folio_real and not self.validate_folio_real(folio_real):
            warnings["folio_real"] = "Formato de folio real inválido"

        # Validar que exista al menos un monto de crédito
        monto_original = data.get("Monto_Credito_Original")
        suma_credito = data.get("Suma_Credito")
        if not monto_original and not suma_credito:
            errors.append("Debe existir al menos un monto de crédito (original o suma)")

        # Validar equivalente en salarios mínimos (requerido por ley)
        equiv_salario = data.get("Equivalente_Salario_Minimo")
        if not equiv_salario or equiv_salario == "NO LOCALIZADO":
            warnings["equivalente_salario"] = "Equivalente en salarios mínimos no encontrado (requerido por ley)"

        # Validar datos registrales
        if not data.get("Numero_Registro_Libro_Propiedad") and not data.get("Folio_Real"):
            warnings["registro"] = "Faltan datos registrales (número de registro o folio real)"

        is_valid = len(errors) == 0

        logger.info(
            "Validación de datos de cancelación",
            valido=is_valid,
            errores=len(errors),
            warnings=len(warnings)
        )

        return is_valid, errors, warnings

    def get_extraction_prompt(self, document_type: str = "cancelacion") -> str:
        """
        Genera un prompt optimizado para extracción de datos con IA

        Args:
            document_type: Tipo de documento (siempre 'cancelacion')

        Returns:
            str: Prompt formateado para el modelo de IA
        """
        prompt = f"""Eres un experto en extracción de datos de documentos notariales y bancarios.

Tu tarea es extraer información de documentos de CANCELACIÓN DE HIPOTECA.

DOCUMENTOS QUE RECIBIRÁS:
- Constancia de No Adeudo o Finiquito del banco
- Carta de Instrucciones del banco
- Poder Notarial del representante del banco
- Escritura original de la hipoteca
- Certificado de Libertad de Gravamen
- Identificaciones del deudor (INE, RFC, CURP)
- Documentos del inmueble

CAMPOS A EXTRAER: {self.metadata['total_campos']} campos en total

CATEGORÍAS:
{', '.join(self.metadata['categorias'])}

CAMPOS CRÍTICOS (PRIORIDAD ALTA):
{', '.join(self.metadata['campos_criticos'])}

INSTRUCCIONES ESPECIALES:

1. EQUIVALENTE EN SALARIOS MÍNIMOS:
   - Es OBLIGATORIO por ley para créditos de vivienda
   - Buscar en la escritura original de la hipoteca
   - Puede aparecer como "VSMGM" o "veces el salario mínimo"

2. CARTA DE INSTRUCCIONES:
   - Es un documento CRÍTICO emitido por el banco
   - Contiene 11 campos específicos muy importantes
   - Formato típico: "EXP. No. CANC-SOFOL/XXXX/XX"

3. DATOS REGISTRALES:
   - Diferenciar LIBRO DE PROPIEDAD vs LIBRO DE GRAVÁMENES
   - Son libros separados en el Registro Público
   - El gravamen (hipoteca) se cancela en el libro de gravámenes

4. CESIÓN DE CRÉDITO:
   - Si el crédito fue cedido a otra institución, documentar la cesión
   - De lo contrario, usar "NO APLICA"

5. FORMATOS:
   - Fechas: en palabras minúsculas (ej: "quince de marzo de dos mil diez")
   - Números de registro/tomo: en palabras MAYÚSCULAS (ej: "DIECINUEVE")
   - Montos en letras: MAYÚSCULAS con centavos (ej: "QUINIENTOS MIL PESOS 00/100 M.N.")
   - Nombres propios: MAYÚSCULAS (ej: "JUAN CARLOS MARTINEZ LOPEZ")

6. SI NO ENCUENTRAS UN DATO:
   - Usa "NO LOCALIZADO" para datos que deberían estar pero no se encuentran
   - Usa "NO APLICA" solo para cesión de crédito si no hubo cesión

EXTRAE TODOS LOS CAMPOS POSIBLES DEL TEXTO SIGUIENTE:
"""
        return prompt

    def _numero_a_letras(self, numero: int) -> str:
        """
        Convierte número entero a palabras en español (MAYÚSCULAS)

        Implementación básica para números hasta 9999

        Args:
            numero: Número entero a convertir

        Returns:
            str: Número en palabras MAYÚSCULAS
        """
        # Implementación simplificada
        # Para producción, usar librería como num2words
        unidades = ["", "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        decenas = ["", "DIEZ", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA",
                   "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
        centenas = ["", "CIEN", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                    "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]

        if numero == 0:
            return "CERO"

        if numero < 10:
            return unidades[numero]

        # Para números mayores, usar conversión simplificada
        # En producción, implementar conversión completa
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
