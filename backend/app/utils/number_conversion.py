"""
ControlNot v2 - Utilidades de Conversión de Números a Letras

Convierte números a su representación en palabras en español.
Usado principalmente para campos RPP que vienen como números pero deben
mostrarse en palabras en documentos notariales.

Ejemplo:
    >>> numero_a_letras(18)
    'DIECIOCHO'
    >>> numero_a_letras(1688)
    'MIL SEISCIENTOS OCHENTA Y OCHO'
"""
import re
from typing import Optional


# Diccionarios para conversión
UNIDADES = {
    0: '', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro',
    5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve',
    10: 'diez', 11: 'once', 12: 'doce', 13: 'trece', 14: 'catorce',
    15: 'quince', 16: 'dieciseis', 17: 'diecisiete', 18: 'dieciocho',
    19: 'diecinueve', 20: 'veinte', 21: 'veintiuno', 22: 'veintidos',
    23: 'veintitres', 24: 'veinticuatro', 25: 'veinticinco',
    26: 'veintiseis', 27: 'veintisiete', 28: 'veintiocho', 29: 'veintinueve'
}

DECENAS = {
    3: 'treinta', 4: 'cuarenta', 5: 'cincuenta',
    6: 'sesenta', 7: 'setenta', 8: 'ochenta', 9: 'noventa'
}

CENTENAS = {
    1: 'ciento', 2: 'doscientos', 3: 'trescientos', 4: 'cuatrocientos',
    5: 'quinientos', 6: 'seiscientos', 7: 'setecientos', 8: 'ochocientos',
    9: 'novecientos'
}


def _unidades_a_letras(n: int) -> str:
    """Convierte números del 0 al 29 a palabras."""
    return UNIDADES.get(n, '')


def _decenas_a_letras(n: int) -> str:
    """Convierte números del 30 al 99 a palabras."""
    if n < 30:
        return _unidades_a_letras(n)

    decena = n // 10
    unidad = n % 10

    if unidad == 0:
        return DECENAS[decena]
    else:
        return f"{DECENAS[decena]} y {UNIDADES[unidad]}"


def _centenas_a_letras(n: int) -> str:
    """Convierte números del 1 al 999 a palabras."""
    if n == 0:
        return ''
    if n == 100:
        return 'cien'
    if n < 30:
        return _unidades_a_letras(n)
    if n < 100:
        return _decenas_a_letras(n)

    centena = n // 100
    resto = n % 100

    if resto == 0:
        if centena == 1:
            return 'cien'
        return CENTENAS[centena]
    else:
        if resto < 30:
            return f"{CENTENAS[centena]} {_unidades_a_letras(resto)}"
        else:
            return f"{CENTENAS[centena]} {_decenas_a_letras(resto)}"


def numero_a_letras(numero: int, mayusculas: bool = True) -> str:
    """
    Convierte un número entero a su representación en palabras en español.

    Args:
        numero: Número entero a convertir (0 a 999,999,999)
        mayusculas: Si True, retorna en MAYÚSCULAS (default True)

    Returns:
        str: Número en palabras

    Examples:
        >>> numero_a_letras(18)
        'DIECIOCHO'
        >>> numero_a_letras(1688)
        'MIL SEISCIENTOS OCHENTA Y OCHO'
        >>> numero_a_letras(21, mayusculas=False)
        'veintiuno'
        >>> numero_a_letras(100)
        'CIEN'
        >>> numero_a_letras(101)
        'CIENTO UNO'
    """
    if numero == 0:
        resultado = 'cero'
    elif numero < 0:
        resultado = f"menos {numero_a_letras(abs(numero), mayusculas=False)}"
    elif numero < 30:
        resultado = _unidades_a_letras(numero)
    elif numero < 100:
        resultado = _decenas_a_letras(numero)
    elif numero < 1000:
        resultado = _centenas_a_letras(numero)
    elif numero < 1000000:
        # Miles
        miles = numero // 1000
        resto = numero % 1000

        if miles == 1:
            parte_miles = 'mil'
        else:
            parte_miles = f"{_centenas_a_letras(miles)} mil"

        if resto == 0:
            resultado = parte_miles
        else:
            resultado = f"{parte_miles} {_centenas_a_letras(resto)}"
    elif numero < 1000000000:
        # Millones
        millones = numero // 1000000
        resto = numero % 1000000

        if millones == 1:
            parte_millones = 'un millon'
        else:
            parte_millones = f"{_centenas_a_letras(millones)} millones"

        if resto == 0:
            resultado = parte_millones
        else:
            resultado = f"{parte_millones} {numero_a_letras(resto, mayusculas=False)}"
    else:
        # Número muy grande, retornar como string
        resultado = str(numero)

    return resultado.upper() if mayusculas else resultado


def extraer_numero(texto: str) -> Optional[int]:
    """
    Extrae un número de un texto que puede contener ceros a la izquierda.

    Args:
        texto: Texto que contiene un número (ej: "00000018", "1688", "018")

    Returns:
        int o None: El número extraído, o None si no se encuentra

    Examples:
        >>> extraer_numero("00000018")
        18
        >>> extraer_numero("00001688")
        1688
        >>> extraer_numero("texto sin numero")
        None
    """
    if not texto:
        return None

    # Buscar secuencia de dígitos
    match = re.search(r'\d+', str(texto))
    if match:
        return int(match.group())
    return None


def convertir_si_es_numero(valor: str, mayusculas: bool = True) -> str:
    """
    Convierte un valor a palabras si es un número, de lo contrario lo deja igual.

    Esta función es útil para post-procesamiento de datos extraídos donde
    el modelo puede haber extraído un número (ej: "00000018") pero se espera
    texto en palabras (ej: "DIECIOCHO").

    Args:
        valor: Valor a convertir (puede ser número como string o ya texto)
        mayusculas: Si True, retorna en MAYÚSCULAS

    Returns:
        str: El valor convertido a palabras o el original si no es número

    Examples:
        >>> convertir_si_es_numero("00000018")
        'DIECIOCHO'
        >>> convertir_si_es_numero("00001688")
        'MIL SEISCIENTOS OCHENTA Y OCHO'
        >>> convertir_si_es_numero("VEINTISIETE")
        'VEINTISIETE'
        >>> convertir_si_es_numero("**[NO ENCONTRADO]**")
        '**[NO ENCONTRADO]**'
    """
    if not valor:
        return valor

    valor_str = str(valor).strip()

    # Si ya es texto con letras (no solo dígitos), retornar tal cual
    # Excepto si son solo dígitos (posiblemente con ceros a la izquierda)
    if not valor_str.isdigit() and not re.match(r'^0+\d+$', valor_str):
        return valor_str

    # Es un número, convertir
    numero = extraer_numero(valor_str)
    if numero is not None:
        return numero_a_letras(numero, mayusculas=mayusculas)

    return valor_str


def es_numero_con_ceros(valor: str) -> bool:
    """
    Detecta si un valor es un número con ceros a la izquierda (típico de RPP).

    Args:
        valor: Valor a verificar

    Returns:
        bool: True si parece ser un número con ceros a la izquierda

    Examples:
        >>> es_numero_con_ceros("00000018")
        True
        >>> es_numero_con_ceros("18")
        True
        >>> es_numero_con_ceros("DIECIOCHO")
        False
    """
    if not valor:
        return False
    return str(valor).strip().isdigit()
