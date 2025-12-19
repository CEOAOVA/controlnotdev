"""
ControlNot v2 - Validadores Notariales
Validación de RFC, CURP, fechas y otros datos legales mexicanos

SEMANA 1 - QUICK WINS:
- RFC: Validación estructural 13 caracteres
- CURP: Validación estructural 18 caracteres
- Fechas: Validación de formato y rangos lógicos
- Nombres: Detección de patrones inválidos

IMPACTO:
- 0 errores legales en documentos notariales
- Detección temprana de datos incorrectos
- Feedback inmediato al usuario para corrección
- Cumplimiento con SAT y RENAPO

Uso:
    >>> from app.utils.validators import NotarialValidator
    >>> validator = NotarialValidator()
    >>>
    >>> # Validar RFC
    >>> result = validator.validate_rfc("PEPJ860101AAA")
    >>> if result.is_valid:
    ...     print("RFC válido")
    >>>
    >>> # Validar CURP
    >>> result = validator.validate_curp("PEPJ860101HDFLRS05")
"""
import re
from datetime import datetime, date
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()


class ValidationType(Enum):
    """Tipos de validación"""
    RFC = "rfc"
    CURP = "curp"
    FECHA = "fecha"
    NOMBRE = "nombre"
    MONTO = "monto"
    CLAVE_ELECTOR = "clave_elector"
    INE = "ine"


@dataclass
class ValidationResult:
    """
    Resultado de una validación

    Attributes:
        is_valid: Si el dato es válido
        value: Valor validado (limpio/normalizado)
        errors: Lista de errores encontrados
        warnings: Lista de advertencias
        validation_type: Tipo de validación aplicada
    """
    is_valid: bool
    value: str
    errors: List[str]
    warnings: List[str]
    validation_type: ValidationType

    def to_dict(self) -> Dict:
        """Convierte a diccionario"""
        return {
            "is_valid": self.is_valid,
            "value": self.value,
            "errors": self.errors,
            "warnings": self.warnings,
            "validation_type": self.validation_type.value
        }


class NotarialValidator:
    """
    Validador de datos notariales mexicanos

    REGLAS RFC (13 caracteres):
    - Formato: AAAA######XXX
    - AAAA: 4 letras (apellidos + nombre)
    - ######: 6 dígitos (fecha: AAMMDD)
    - XXX: 3 caracteres (homoclave)

    REGLAS CURP (18 caracteres):
    - Formato: AAAA######HXXXXX#
    - AAAA: 4 letras (apellidos + nombre)
    - ######: 6 dígitos (fecha: AAMMDD)
    - H: Sexo (H/M)
    - XXXXX: 5 caracteres (entidad + consonantes)
    - #: Dígito verificador

    REGLAS FECHAS:
    - Formato: DD/MM/AAAA
    - Rango válido: 1900-2100
    - Validación de días por mes
    - Detección de años bisiestos
    """

    # Patrones regex
    RFC_PATTERN = r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$'
    CURP_PATTERN = r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$'
    FECHA_PATTERN = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'

    # Palabras inconvenientes (no permitidas por SAT)
    PALABRAS_INCONVENIENTES = [
        "BUEI", "BUEY", "CACA", "CACO", "CAGA", "CAGO", "CAKA", "CAKO",
        "COGE", "COJA", "COJE", "COJI", "COJO", "CULO", "FETO", "GUEY",
        "JOTO", "KACA", "KACO", "KAGA", "KAGO", "KAKA", "KOGE", "KOJO",
        "KULO", "MAME", "MAMO", "MEAR", "MEAS", "MEON", "MION", "MOCO",
        "MULA", "PEDA", "PEDO", "PENE", "PUTA", "PUTO", "QULO", "RATA",
        "RUIN"
    ]

    # Estados de la República (para CURP)
    ESTADOS_CURP = {
        "AS": "Aguascalientes",
        "BC": "Baja California",
        "BS": "Baja California Sur",
        "CC": "Campeche",
        "CS": "Chiapas",
        "CH": "Chihuahua",
        "CL": "Coahuila",
        "CM": "Colima",
        "DF": "Ciudad de México",
        "DG": "Durango",
        "GT": "Guanajuato",
        "GR": "Guerrero",
        "HG": "Hidalgo",
        "JC": "Jalisco",
        "MC": "México",
        "MN": "Michoacán",
        "MS": "Morelos",
        "NT": "Nayarit",
        "NL": "Nuevo León",
        "OC": "Oaxaca",
        "PL": "Puebla",
        "QT": "Querétaro",
        "QR": "Quintana Roo",
        "SP": "San Luis Potosí",
        "SL": "Sinaloa",
        "SR": "Sonora",
        "TC": "Tabasco",
        "TS": "Tamaulipas",
        "TL": "Tlaxcala",
        "VZ": "Veracruz",
        "YN": "Yucatán",
        "ZS": "Zacatecas",
        "NE": "Nacido en el Extranjero"
    }

    def __init__(self):
        """Inicializa el validador"""
        logger.info("NotarialValidator inicializado")

    # ==========================================
    # RFC VALIDATION
    # ==========================================

    def validate_rfc(self, rfc: str) -> ValidationResult:
        """
        Valida RFC (Registro Federal de Contribuyentes)

        Args:
            rfc: RFC a validar (con o sin espacios/guiones)

        Returns:
            ValidationResult con resultado de validación

        Example:
            >>> validator = NotarialValidator()
            >>> result = validator.validate_rfc("PEPJ860101AAA")
            >>> print(result.is_valid)  # True
            >>> result = validator.validate_rfc("INVALID")
            >>> print(result.errors)  # ['RFC debe tener 13 caracteres']

        Validaciones:
        - Longitud exacta 13 caracteres
        - Formato correcto (letras + números + homoclave)
        - Fecha válida embebida
        - No palabras inconvenientes
        """
        errors = []
        warnings = []

        # Limpiar RFC (uppercase, sin espacios)
        rfc_clean = rfc.upper().strip().replace("-", "").replace(" ", "")

        # Validar longitud
        if len(rfc_clean) != 13:
            errors.append(f"RFC debe tener 13 caracteres (actual: {len(rfc_clean)})")

        # Validar formato general
        if not re.match(self.RFC_PATTERN, rfc_clean):
            errors.append("RFC no cumple formato válido (AAAA######XXX)")

        # Si no hay errores estructurales, validar fecha embebida
        if not errors and len(rfc_clean) == 13:
            fecha_part = rfc_clean[4:10]  # Posiciones 5-10 son AAMMDD

            try:
                year = int(fecha_part[0:2])
                month = int(fecha_part[2:4])
                day = int(fecha_part[4:6])

                # Determinar siglo (00-39 = 2000s, 40-99 = 1900s)
                if year <= 39:
                    full_year = 2000 + year
                else:
                    full_year = 1900 + year

                # Validar que la fecha sea válida
                try:
                    date(full_year, month, day)
                except ValueError:
                    errors.append(f"Fecha embebida inválida: {day:02d}/{month:02d}/{full_year}")

            except ValueError:
                errors.append("Fecha embebida en RFC no es numérica")

        # Validar palabras inconvenientes
        primeras_cuatro = rfc_clean[:4]
        if primeras_cuatro in self.PALABRAS_INCONVENIENTES:
            warnings.append(
                f"RFC contiene palabra inconveniente: {primeras_cuatro}. "
                "El SAT normalmente la reemplaza."
            )

        is_valid = len(errors) == 0

        if is_valid:
            logger.debug("RFC válido", rfc=rfc_clean)
        else:
            logger.warning("RFC inválido", rfc=rfc_clean, errors=errors)

        return ValidationResult(
            is_valid=is_valid,
            value=rfc_clean,
            errors=errors,
            warnings=warnings,
            validation_type=ValidationType.RFC
        )

    # ==========================================
    # CURP VALIDATION
    # ==========================================

    def validate_curp(self, curp: str) -> ValidationResult:
        """
        Valida CURP (Clave Única de Registro de Población)

        Args:
            curp: CURP a validar

        Returns:
            ValidationResult con resultado de validación

        Example:
            >>> result = validator.validate_curp("PEPJ860101HDFLRS05")
            >>> print(result.is_valid)  # True

        Validaciones:
        - Longitud exacta 18 caracteres
        - Formato correcto
        - Fecha válida embebida
        - Sexo válido (H/M)
        - Estado válido (clave 2 letras)
        """
        errors = []
        warnings = []

        # Limpiar CURP
        curp_clean = curp.upper().strip().replace("-", "").replace(" ", "")

        # Validar longitud
        if len(curp_clean) != 18:
            errors.append(f"CURP debe tener 18 caracteres (actual: {len(curp_clean)})")

        # Validar formato general
        if not re.match(self.CURP_PATTERN, curp_clean):
            errors.append("CURP no cumple formato válido")

        # Si no hay errores estructurales, validar componentes
        if not errors and len(curp_clean) == 18:
            # Validar fecha embebida (posiciones 5-10)
            fecha_part = curp_clean[4:10]

            try:
                year = int(fecha_part[0:2])
                month = int(fecha_part[2:4])
                day = int(fecha_part[4:6])

                # Determinar siglo (igual que RFC)
                if year <= 39:
                    full_year = 2000 + year
                else:
                    full_year = 1900 + year

                # Validar fecha
                try:
                    date(full_year, month, day)
                except ValueError:
                    errors.append(f"Fecha embebida inválida: {day:02d}/{month:02d}/{full_year}")

            except ValueError:
                errors.append("Fecha embebida en CURP no es numérica")

            # Validar sexo (posición 11)
            sexo = curp_clean[10]
            if sexo not in ['H', 'M']:
                errors.append(f"Sexo debe ser H o M (actual: {sexo})")

            # Validar estado (posiciones 12-13)
            estado = curp_clean[11:13]
            if estado not in self.ESTADOS_CURP:
                warnings.append(
                    f"Código de estado no reconocido: {estado}. "
                    "Verificar que sea correcto."
                )
            else:
                logger.debug(
                    "Estado CURP detectado",
                    estado_codigo=estado,
                    estado_nombre=self.ESTADOS_CURP[estado]
                )

        is_valid = len(errors) == 0

        if is_valid:
            logger.debug("CURP válido", curp=curp_clean)
        else:
            logger.warning("CURP inválido", curp=curp_clean, errors=errors)

        return ValidationResult(
            is_valid=is_valid,
            value=curp_clean,
            errors=errors,
            warnings=warnings,
            validation_type=ValidationType.CURP
        )

    # ==========================================
    # FECHA VALIDATION
    # ==========================================

    def validate_fecha(
        self,
        fecha: str,
        min_year: int = 1900,
        max_year: int = 2100
    ) -> ValidationResult:
        """
        Valida fecha en formato DD/MM/AAAA

        Args:
            fecha: Fecha a validar
            min_year: Año mínimo permitido
            max_year: Año máximo permitido

        Returns:
            ValidationResult con resultado de validación

        Example:
            >>> result = validator.validate_fecha("15/03/2024")
            >>> print(result.is_valid)  # True
            >>> result = validator.validate_fecha("32/13/2024")
            >>> print(result.errors)  # ['Fecha no es válida...']

        Validaciones:
        - Formato DD/MM/AAAA
        - Fecha real (no 32/13/2024)
        - Año en rango lógico
        - Años bisiestos correctos
        """
        errors = []
        warnings = []

        # Validar formato con regex
        match = re.match(self.FECHA_PATTERN, fecha.strip())

        if not match:
            errors.append(
                f"Fecha debe tener formato DD/MM/AAAA (actual: {fecha})"
            )
            fecha_clean = fecha
        else:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))

            # Validar que sea fecha real
            try:
                fecha_obj = date(year, month, day)
                fecha_clean = fecha_obj.strftime("%d/%m/%Y")

                # Validar rango de años
                if year < min_year or year > max_year:
                    errors.append(
                        f"Año fuera de rango válido "
                        f"({min_year}-{max_year}): {year}"
                    )

                # Warnings para fechas sospechosas
                today = date.today()

                # Fecha en el futuro
                if fecha_obj > today:
                    warnings.append(
                        f"Fecha en el futuro: {fecha_clean}. "
                        "Verificar que sea correcta."
                    )

                # Fecha muy antigua
                if year < 1930:
                    warnings.append(
                        f"Fecha muy antigua: {fecha_clean}. "
                        "Verificar que sea correcta."
                    )

            except ValueError as e:
                errors.append(f"Fecha no es válida: {str(e)}")
                fecha_clean = fecha

        is_valid = len(errors) == 0

        if is_valid:
            logger.debug("Fecha válida", fecha=fecha_clean)
        else:
            logger.warning("Fecha inválida", fecha=fecha, errors=errors)

        return ValidationResult(
            is_valid=is_valid,
            value=fecha_clean if is_valid else fecha,
            errors=errors,
            warnings=warnings,
            validation_type=ValidationType.FECHA
        )

    # ==========================================
    # CLAVE ELECTOR VALIDATION (INE)
    # ==========================================

    # Patron para clave de elector: 6 letras + 8 digitos + 4 alfanumericos
    CLAVE_ELECTOR_PATTERN = r'^[A-Z]{6}\d{8}[A-Z0-9]{4}$'

    def validate_clave_elector(self, clave: str) -> ValidationResult:
        """
        Valida clave de elector INE (18 caracteres)

        Formato: 6 letras + 8 digitos + 4 caracteres alfanumericos

        Args:
            clave: Clave de elector a validar

        Returns:
            ValidationResult con resultado de validacion

        Example:
            >>> result = validator.validate_clave_elector("CRVRAL64081314H100")
            >>> print(result.is_valid)  # True

        Validaciones:
        - Longitud exacta 18 caracteres
        - Formato correcto (6 letras + 8 digitos + 4 alfanumericos)
        """
        errors = []
        warnings = []

        if not clave:
            errors.append("Clave de elector vacia")
            return ValidationResult(
                is_valid=False,
                value="",
                errors=errors,
                warnings=warnings,
                validation_type=ValidationType.CLAVE_ELECTOR
            )

        clave_clean = clave.strip().upper()

        # Validar longitud
        if len(clave_clean) != 18:
            errors.append(
                f"Clave de elector debe tener 18 caracteres (actual: {len(clave_clean)})"
            )

        # Validar formato
        if not re.match(self.CLAVE_ELECTOR_PATTERN, clave_clean):
            errors.append(
                "Formato de clave de elector invalido "
                "(debe ser 6 letras + 8 digitos + 4 alfanumericos)"
            )

        is_valid = len(errors) == 0

        if is_valid:
            logger.debug("Clave de elector valida", clave=clave_clean)
        else:
            logger.warning("Clave de elector invalida", clave=clave_clean, errors=errors)

        return ValidationResult(
            is_valid=is_valid,
            value=clave_clean,
            errors=errors,
            warnings=warnings,
            validation_type=ValidationType.CLAVE_ELECTOR
        )

    def validate_seccion_electoral(self, seccion: str) -> ValidationResult:
        """
        Valida seccion electoral (4 digitos)

        Args:
            seccion: Seccion electoral a validar

        Returns:
            ValidationResult con resultado de validacion
        """
        errors = []
        warnings = []

        if not seccion:
            errors.append("Seccion electoral vacia")
            return ValidationResult(
                is_valid=False,
                value="",
                errors=errors,
                warnings=warnings,
                validation_type=ValidationType.INE
            )

        seccion_clean = seccion.strip()

        # Validar que sean digitos
        if not seccion_clean.isdigit():
            errors.append("Seccion electoral debe contener solo digitos")

        # Validar longitud
        if len(seccion_clean) != 4:
            errors.append(
                f"Seccion electoral debe tener 4 digitos (actual: {len(seccion_clean)})"
            )

        is_valid = len(errors) == 0

        # Normalizar a 4 digitos con ceros a la izquierda
        if seccion_clean.isdigit():
            seccion_clean = seccion_clean.zfill(4)

        return ValidationResult(
            is_valid=is_valid,
            value=seccion_clean,
            errors=errors,
            warnings=warnings,
            validation_type=ValidationType.INE
        )

    def validate_ine_data(
        self,
        extracted_data: Dict[str, str]
    ) -> Dict[str, ValidationResult]:
        """
        Valida todos los campos de una INE extraida

        Args:
            extracted_data: Datos extraidos de la INE

        Returns:
            Dict[str, ValidationResult]: Resultados por campo

        Example:
            >>> data = {
            ...     "curp": "CEAR640813HMNRRL02",
            ...     "clave_elector": "CRVRAL64081314H100",
            ...     "fecha_nacimiento": "13/08/1964"
            ... }
            >>> results = validator.validate_ine_data(data)
        """
        results = {}

        # Validar CURP si existe
        curp = extracted_data.get('curp', '')
        if curp and "NO ENCONTRADO" not in curp.upper():
            results['curp'] = self.validate_curp(curp)

        # Validar clave de elector si existe
        clave = extracted_data.get('clave_elector', '')
        if clave and "NO ENCONTRADO" not in clave.upper():
            results['clave_elector'] = self.validate_clave_elector(clave)

        # Validar fecha de nacimiento si existe
        fecha = extracted_data.get('fecha_nacimiento', '')
        if fecha and "NO ENCONTRADO" not in fecha.upper():
            results['fecha_nacimiento'] = self.validate_fecha(fecha)

        # Validar seccion electoral (4 digitos)
        seccion = extracted_data.get('seccion_electoral', '')
        if seccion and "NO ENCONTRADO" not in seccion.upper():
            results['seccion_electoral'] = self.validate_seccion_electoral(seccion)

        # Validar consistencia CURP-sexo si ambos existen
        sexo = extracted_data.get('sexo', '')
        if curp and sexo and len(curp) >= 11:
            curp_sexo = curp[10]  # Posicion 11 del CURP
            if sexo.upper() in ['H', 'M'] and curp_sexo != sexo.upper():
                results['sexo_consistency'] = ValidationResult(
                    is_valid=False,
                    value=sexo,
                    errors=[
                        f"Sexo '{sexo}' no coincide con CURP (indica '{curp_sexo}')"
                    ],
                    warnings=[],
                    validation_type=ValidationType.INE
                )

        # Log resumen
        total = len(results)
        valid = sum(1 for r in results.values() if r.is_valid)
        invalid = total - valid

        logger.info(
            "Validacion de datos INE",
            total_validations=total,
            valid=valid,
            invalid=invalid
        )

        return results

    # ==========================================
    # BATCH VALIDATION
    # ==========================================

    def validate_extracted_data(
        self,
        extracted_data: Dict[str, str]
    ) -> Dict[str, ValidationResult]:
        """
        Valida todos los campos extraídos según su tipo

        Detecta automáticamente RFC, CURP y fechas en los datos extraídos
        y los valida.

        Args:
            extracted_data: Diccionario con datos extraídos

        Returns:
            Dict[str, ValidationResult]: Resultados por campo

        Example:
            >>> data = {
            ...     "Vendedor_RFC": "PEPJ860101AAA",
            ...     "Vendedor_CURP": "PEPJ860101HDFLRS05",
            ...     "Fecha_Escritura": "15/03/2024"
            ... }
            >>> results = validator.validate_extracted_data(data)
            >>> for field, result in results.items():
            ...     print(f"{field}: {'✅' if result.is_valid else '❌'}")

        Detecta automáticamente:
        - Campos con "_RFC" en el nombre
        - Campos con "_CURP" en el nombre
        - Campos con "Fecha" en el nombre
        """
        validation_results = {}

        for field, value in extracted_data.items():
            field_lower = field.lower()

            # Skip si valor vacío o "NO ENCONTRADO"
            if not value or "NO ENCONTRADO" in value:
                continue

            # Detectar y validar RFC
            if "rfc" in field_lower:
                validation_results[field] = self.validate_rfc(value)

            # Detectar y validar CURP
            elif "curp" in field_lower:
                validation_results[field] = self.validate_curp(value)

            # Detectar y validar fechas
            elif "fecha" in field_lower:
                validation_results[field] = self.validate_fecha(value)

        # Log resumen
        total = len(validation_results)
        valid = sum(1 for r in validation_results.values() if r.is_valid)
        invalid = total - valid

        logger.info(
            "Validación de datos extraídos",
            total_validations=total,
            valid=valid,
            invalid=invalid
        )

        return validation_results


# Example usage
if __name__ == "__main__":
    validator = NotarialValidator()

    print("🔍 VALIDADOR NOTARIAL - EJEMPLOS\n")

    # Test RFC
    print("📋 RFC:")
    rfcs = [
        "PEPJ860101AAA",  # Válido
        "XAXX010101000",  # Válido
        "INVALID",  # Inválido (longitud)
        "PEPJ999999AAA",  # Inválido (fecha imposible)
    ]
    for rfc in rfcs:
        result = validator.validate_rfc(rfc)
        status = "✅" if result.is_valid else "❌"
        print(f"   {status} {rfc}: {result.errors if result.errors else 'OK'}")

    # Test CURP
    print("\n👤 CURP:")
    curps = [
        "PEPJ860101HDFLRS05",  # Válido
        "INVALID",  # Inválido
    ]
    for curp in curps:
        result = validator.validate_curp(curp)
        status = "✅" if result.is_valid else "❌"
        print(f"   {status} {curp}: {result.errors if result.errors else 'OK'}")

    # Test Fechas
    print("\n📅 FECHAS:")
    fechas = [
        "15/03/2024",  # Válida
        "29/02/2024",  # Válida (bisiesto)
        "32/13/2024",  # Inválida
        "29/02/2023",  # Inválida (no bisiesto)
    ]
    for fecha in fechas:
        result = validator.validate_fecha(fecha)
        status = "✅" if result.is_valid else "❌"
        print(f"   {status} {fecha}: {result.errors if result.errors else 'OK'}")

    # Test batch
    print("\n📦 VALIDACIÓN BATCH:")
    data = {
        "Vendedor_RFC": "PEPJ860101AAA",
        "Vendedor_CURP": "PEPJ860101HDFLRS05",
        "Fecha_Escritura": "15/03/2024",
        "Comprador_RFC": "INVALID"
    }
    results = validator.validate_extracted_data(data)
    for field, result in results.items():
        status = "✅" if result.is_valid else "❌"
        print(f"   {status} {field}")
        if result.errors:
            for error in result.errors:
                print(f"      - {error}")
