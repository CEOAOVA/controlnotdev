"""
ControlNot v2 - Validation Service for Anti-Hallucination
Valida datos extraidos para detectar y prevenir alucinaciones de LLM.

Best Practices 2025:
- Validacion de formatos mexicanos (CURP, RFC, etc.)
- Cross-verificacion con texto fuente (fuzzy matching)
- Confidence scores por campo
- Deteccion de patrones sospechosos

Fuentes:
- Cradl AI: Hallucination-free LLM data extraction
- LMV-RPA: Voting system for 99% accuracy
"""
import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal
import structlog

logger = structlog.get_logger()

# Import rapidfuzz with fallback
try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    logger.warning(
        "rapidfuzz no instalado. pip install rapidfuzz "
        "para mejor fuzzy matching en validacion"
    )


class ValidationStatus(str, Enum):
    """Estados de validacion por campo"""
    VALID = "valid"           # Paso todas las validaciones
    SUSPICIOUS = "suspicious"  # Posible alucinacion, requiere revision
    INVALID = "invalid"       # Formato incorrecto o inconsistente
    NOT_VALIDATED = "not_validated"  # Sin validador disponible


@dataclass
class FieldValidation:
    """Resultado de validacion para un campo"""
    field: str
    value: Any
    status: ValidationStatus = ValidationStatus.NOT_VALIDATED
    confidence: float = 1.0  # 0.0 - 1.0
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "value": self.value,
            "status": self.status.value,
            "confidence": round(self.confidence, 2),
            "issues": self.issues
        }


@dataclass
class ValidationReport:
    """Reporte completo de validacion"""
    total_fields: int = 0
    valid_fields: int = 0
    suspicious_fields: int = 0
    invalid_fields: int = 0
    overall_confidence: float = 0.0
    field_validations: List[FieldValidation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_fields": self.total_fields,
            "valid_fields": self.valid_fields,
            "suspicious_fields": self.suspicious_fields,
            "invalid_fields": self.invalid_fields,
            "overall_confidence": round(self.overall_confidence, 2),
            "field_validations": [fv.to_dict() for fv in self.field_validations]
        }


# ==================================
# VALIDADORES DE FORMATO MEXICANO
# ==================================

FIELD_VALIDATORS = {
    # Documentos de identidad mexicanos
    "curp": {
        "pattern": r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$",
        "length": 18,
        "description": "CURP mexicano: 4 letras + 6 numeros + H/M + 5 letras + 1 char + 1 digito"
    },
    "rfc": {
        "pattern": r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$",
        "length": [12, 13],  # 12 para morales, 13 para fisicas
        "description": "RFC: 3-4 letras + 6 numeros + 3 chars"
    },
    "clave_elector": {
        "pattern": r"^[A-Z]{6}\d{8}[HM]\d{3}$",
        "length": 18,
        "description": "Clave elector: 6 letras + 8 numeros + H/M + 3 numeros"
    },
    "seccion_electoral": {
        "pattern": r"^\d{4}$",
        "length": 4,
        "description": "Seccion electoral: 4 digitos"
    },

    # Fechas
    "fecha": {
        "pattern": r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$",
        "description": "Fecha: DD/MM/AAAA o DD-MM-AAAA"
    },
    "fecha_iso": {
        "pattern": r"^\d{4}-\d{2}-\d{2}$",
        "description": "Fecha ISO: AAAA-MM-DD"
    },

    # Geograficos
    "codigo_postal": {
        "pattern": r"^\d{5}$",
        "length": 5,
        "description": "Codigo postal mexicano: 5 digitos"
    },

    # Contacto
    "telefono": {
        "pattern": r"^\d{10}$",
        "length": 10,
        "description": "Telefono mexicano: 10 digitos"
    },
    "email": {
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "description": "Email valido"
    },

    # Notariales
    "numero_escritura": {
        "pattern": r"^\d+$",
        "description": "Numero de escritura: solo digitos"
    },
    "numero_notaria": {
        "pattern": r"^\d+$",
        "description": "Numero de notaria: solo digitos"
    },
    "folio_real": {
        "pattern": r"^[A-Z0-9/-]+$",
        "description": "Folio real: letras, numeros, guiones"
    },
}

# Mapeo de nombres de campo a tipo de validador
FIELD_TO_VALIDATOR = {
    # CURP fields
    "curp": "curp",
    "curp_parte_a": "curp",
    "curp_parte_b": "curp",
    "curp_donante": "curp",
    "curp_donatario": "curp",
    "curp_vendedor": "curp",
    "curp_comprador": "curp",
    "curp_testador": "curp",
    "curp_poderdante": "curp",
    "curp_apoderado": "curp",

    # RFC fields
    "rfc": "rfc",
    "rfc_parte_a": "rfc",
    "rfc_parte_b": "rfc",
    "rfc_donante": "rfc",
    "rfc_donatario": "rfc",
    "rfc_vendedor": "rfc",
    "rfc_comprador": "rfc",

    # INE fields
    "clave_elector": "clave_elector",
    "clave_elector_parte_a": "clave_elector",
    "clave_elector_parte_b": "clave_elector",
    "seccion": "seccion_electoral",
    "seccion_parte_a": "seccion_electoral",
    "seccion_parte_b": "seccion_electoral",

    # Fechas
    "fecha_nacimiento": "fecha",
    "fecha_nacimiento_parte_a": "fecha",
    "fecha_nacimiento_parte_b": "fecha",
    "fecha_escritura": "fecha",
    "fecha_otorgamiento": "fecha",
    "fecha_firma": "fecha",
    "vigencia": "fecha",

    # Geograficos
    "codigo_postal": "codigo_postal",
    "cp": "codigo_postal",
    "cp_predio": "codigo_postal",

    # Contacto
    "telefono": "telefono",
    "email": "email",
    "correo": "email",

    # Notariales
    "numero_escritura": "numero_escritura",
    "escritura": "numero_escritura",
    "numero_notaria": "numero_notaria",
    "notaria": "numero_notaria",
    "folio_real": "folio_real",
}


class ValidationService:
    """
    Servicio de validacion anti-alucinacion.

    Estrategias implementadas:
    1. Validacion de formato (regex)
    2. Cross-verificacion con texto fuente
    3. Deteccion de patrones sospechosos
    4. Confidence scoring
    """

    def __init__(self):
        logger.debug("ValidationService inicializado")

    def validate_extraction(
        self,
        extracted_data: Dict[str, Any],
        document_type: str,
        source_text: Optional[str] = None,
        strict_mode: bool = False
    ) -> ValidationReport:
        """
        Valida todos los campos extraidos.

        Args:
            extracted_data: Datos extraidos por LLM
            document_type: Tipo de documento para contexto
            source_text: Texto OCR original para cross-verificacion
            strict_mode: Si True, marca como suspicious campos no verificados

        Returns:
            ValidationReport con resultados detallados
        """
        report = ValidationReport()
        report.total_fields = len(extracted_data)

        for field_name, value in extracted_data.items():
            validation = self._validate_field(
                field_name,
                value,
                source_text,
                strict_mode
            )
            report.field_validations.append(validation)

            if validation.status == ValidationStatus.VALID:
                report.valid_fields += 1
            elif validation.status == ValidationStatus.SUSPICIOUS:
                report.suspicious_fields += 1
            elif validation.status == ValidationStatus.INVALID:
                report.invalid_fields += 1

        # Calcular confidence general
        if report.field_validations:
            confidences = [fv.confidence for fv in report.field_validations]
            report.overall_confidence = sum(confidences) / len(confidences)

        logger.info(
            "Validacion completada",
            doc_type=document_type,
            total=report.total_fields,
            valid=report.valid_fields,
            suspicious=report.suspicious_fields,
            invalid=report.invalid_fields,
            confidence=f"{report.overall_confidence:.2%}"
        )

        return report

    def _validate_field(
        self,
        field_name: str,
        value: Any,
        source_text: Optional[str],
        strict_mode: bool
    ) -> FieldValidation:
        """Valida un campo individual."""
        validation = FieldValidation(field=field_name, value=value)

        # Convertir a string para validacion
        str_value = str(value).strip() if value else ""

        # 1. Verificar campos marcados como no encontrados
        if self._is_not_found(str_value):
            validation.status = ValidationStatus.VALID  # Es valido reportar que no se encontro
            validation.confidence = 1.0
            return validation

        # 2. Detectar patrones sospechosos de alucinacion
        hallucination_issues = self._detect_hallucination_patterns(str_value)
        if hallucination_issues:
            validation.issues.extend(hallucination_issues)
            validation.status = ValidationStatus.SUSPICIOUS
            validation.confidence = 0.3

        # 3. Validar formato si hay validador disponible
        format_result = self._validate_format(field_name, str_value)
        if format_result is not None:
            if not format_result["valid"]:
                validation.issues.append(format_result["issue"])
                validation.status = ValidationStatus.INVALID
                validation.confidence = min(validation.confidence, 0.2)
            else:
                if validation.status == ValidationStatus.NOT_VALIDATED:
                    validation.status = ValidationStatus.VALID
                    validation.confidence = 0.9

        # 4. Cross-verificacion con texto fuente
        if source_text and str_value:
            in_source = self._verify_in_source(str_value, source_text)
            if not in_source:
                validation.issues.append("Valor no encontrado en texto original")
                if validation.status != ValidationStatus.INVALID:
                    validation.status = ValidationStatus.SUSPICIOUS
                validation.confidence = min(validation.confidence, 0.5)
            else:
                validation.confidence = min(validation.confidence + 0.1, 1.0)

        # 5. Si no hay validador y strict_mode, marcar como suspicious
        if validation.status == ValidationStatus.NOT_VALIDATED:
            if strict_mode:
                validation.status = ValidationStatus.SUSPICIOUS
                validation.confidence = 0.7
            else:
                validation.status = ValidationStatus.VALID
                validation.confidence = 0.8  # Confidence menor sin validacion

        return validation

    def _is_not_found(self, value: str) -> bool:
        """Verifica si el valor indica 'no encontrado'."""
        not_found_markers = [
            "no encontrado",
            "not found",
            "n/a",
            "na",
            "ilegible",
            "parcial",
            "verificar",
            "**[",
            "[no",
            "[ilegible"
        ]
        value_lower = value.lower()
        return any(marker in value_lower for marker in not_found_markers)

    def _detect_hallucination_patterns(self, value: str) -> List[str]:
        """
        Detecta patrones comunes de alucinacion de LLM.

        Patrones sospechosos:
        - Valores muy genericos
        - Fechas futuras
        - Patrones repetitivos
        - Datos obviamente falsos
        """
        issues = []

        # Valores genericos sospechosos
        generic_values = [
            "juan perez",
            "maria garcia",
            "jose lopez",
            "ejemplo",
            "test",
            "muestra",
            "xxxxx",
            "12345",
            "00000"
        ]
        if value.lower() in generic_values:
            issues.append(f"Valor generico sospechoso: {value}")

        # Patrones repetitivos (como AAAAAA o 111111)
        if len(value) >= 4:
            if len(set(value.replace(" ", ""))) == 1:
                issues.append(f"Patron repetitivo sospechoso: {value}")

        # Fechas futuras (sospechoso para documentos)
        from datetime import datetime
        date_patterns = [
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",  # DD/MM/YYYY
            r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})"   # YYYY/MM/DD
        ]
        for pattern in date_patterns:
            match = re.search(pattern, value)
            if match:
                try:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY first
                        year = int(groups[0])
                    else:  # DD first
                        year = int(groups[2])

                    if year > datetime.now().year:
                        issues.append(f"Fecha futura sospechosa: {value}")
                except ValueError:
                    pass

        # CURP con estructura sospechosa
        if len(value) == 18 and value.isalnum():
            # Verificar que la parte de fecha sea razonable
            date_part = value[4:10]
            try:
                year = int(date_part[:2])
                month = int(date_part[2:4])
                day = int(date_part[4:6])
                if month > 12 or month < 1 or day > 31 or day < 1:
                    issues.append(f"CURP con fecha invalida: {value}")
            except ValueError:
                pass

        return issues

    def _validate_format(self, field_name: str, value: str) -> Optional[Dict]:
        """
        Valida el formato de un campo usando regex.

        Returns:
            None si no hay validador, dict con resultado si lo hay
        """
        # Normalizar nombre del campo
        field_lower = field_name.lower()

        # Buscar validador
        validator_type = FIELD_TO_VALIDATOR.get(field_lower)

        # Si no hay mapeo directo, buscar por contenido del nombre
        if not validator_type:
            for key, val_type in FIELD_TO_VALIDATOR.items():
                if key in field_lower:
                    validator_type = val_type
                    break

        if not validator_type:
            return None

        validator = FIELD_VALIDATORS.get(validator_type)
        if not validator:
            return None

        # Normalizar valor para comparacion
        normalized = value.upper().replace(" ", "").replace("-", "")

        # Validar longitud si aplica
        expected_length = validator.get("length")
        if expected_length:
            if isinstance(expected_length, list):
                if len(normalized) not in expected_length:
                    return {
                        "valid": False,
                        "issue": f"Longitud incorrecta para {validator_type}: {len(normalized)}, esperado {expected_length}"
                    }
            else:
                if len(normalized) != expected_length:
                    return {
                        "valid": False,
                        "issue": f"Longitud incorrecta para {validator_type}: {len(normalized)}, esperado {expected_length}"
                    }

        # Validar patron
        pattern = validator.get("pattern")
        if pattern:
            if not re.match(pattern, normalized, re.IGNORECASE):
                return {
                    "valid": False,
                    "issue": f"Formato invalido para {validator_type}: {value}"
                }

        return {"valid": True}

    def _verify_in_source(self, value: str, source_text: str) -> bool:
        """
        Verifica que el valor aparece en el texto fuente.

        Usa fuzzy matching para tolerar errores de OCR.
        """
        # Normalizar ambos textos
        value_norm = self._normalize_for_comparison(value)
        source_norm = self._normalize_for_comparison(source_text)

        # Busqueda exacta
        if value_norm in source_norm:
            return True

        # Busqueda de partes (para nombres completos divididos)
        parts = value_norm.split()
        if len(parts) > 1:
            found_parts = sum(1 for part in parts if part in source_norm)
            if found_parts >= len(parts) * 0.6:  # 60% de partes encontradas
                return True

        # Fuzzy matching simple (Levenshtein-like)
        # Solo para valores cortos donde OCR puede fallar
        if len(value_norm) <= 20:
            similarity = self._simple_similarity(value_norm, source_norm)
            return similarity >= 0.85

        return False

    def _normalize_for_comparison(self, text: str) -> str:
        """Normaliza texto para comparacion."""
        import unicodedata

        # Convertir a minusculas
        text = text.lower()

        # Remover acentos
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')

        # Remover caracteres especiales excepto espacios
        text = re.sub(r'[^a-z0-9\s]', '', text)

        # Normalizar espacios
        text = ' '.join(text.split())

        return text

    def _simple_similarity(self, s1: str, s2: str) -> float:
        """
        Calcula similitud entre dos strings usando fuzzy matching.
        Busca s1 como substring en s2 con tolerancia.
        """
        if not s1 or not s2:
            return 0.0

        # Usar rapidfuzz si esta disponible (mucho mas rapido y preciso)
        if RAPIDFUZZ_AVAILABLE:
            # partial_ratio busca el mejor match de s1 dentro de s2
            ratio = fuzz.partial_ratio(s1, s2) / 100.0
            return ratio

        # Fallback: busqueda simple por ventana
        best_ratio = 0.0
        len_s1 = len(s1)

        for i in range(len(s2) - len_s1 + 1):
            window = s2[i:i + len_s1]
            matches = sum(1 for a, b in zip(s1, window) if a == b)
            ratio = matches / len_s1
            best_ratio = max(best_ratio, ratio)

            if best_ratio >= 0.95:  # Early exit si es muy bueno
                break

        return best_ratio

    def get_suspicious_fields(self, report: ValidationReport) -> List[str]:
        """Obtiene lista de campos sospechosos para revision manual."""
        return [
            fv.field for fv in report.field_validations
            if fv.status in [ValidationStatus.SUSPICIOUS, ValidationStatus.INVALID]
        ]

    def get_confidence_summary(self, report: ValidationReport) -> Dict:
        """Obtiene resumen de confianza por categoria de campo."""
        categories = {
            "identity": [],  # CURP, RFC, INE
            "dates": [],
            "addresses": [],
            "names": [],
            "other": []
        }

        for fv in report.field_validations:
            field_lower = fv.field.lower()
            if any(x in field_lower for x in ['curp', 'rfc', 'clave', 'ine']):
                categories["identity"].append(fv.confidence)
            elif any(x in field_lower for x in ['fecha', 'date', 'nacimiento', 'vigencia']):
                categories["dates"].append(fv.confidence)
            elif any(x in field_lower for x in ['direccion', 'domicilio', 'calle', 'colonia', 'cp']):
                categories["addresses"].append(fv.confidence)
            elif any(x in field_lower for x in ['nombre', 'name', 'apellido']):
                categories["names"].append(fv.confidence)
            else:
                categories["other"].append(fv.confidence)

        summary = {}
        for cat, confidences in categories.items():
            if confidences:
                summary[cat] = {
                    "avg_confidence": sum(confidences) / len(confidences),
                    "count": len(confidences)
                }

        return summary


# Singleton
_validation_service: Optional[ValidationService] = None


def get_validation_service() -> ValidationService:
    """Factory para obtener instancia singleton del servicio"""
    global _validation_service
    if _validation_service is None:
        _validation_service = ValidationService()
    return _validation_service
