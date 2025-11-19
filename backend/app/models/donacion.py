"""
ControlNot v2 - Modelo Donación
42 campos específicos para documentos de donación

Migrado de por_partes.py líneas 785-1283
IMPORTANTE: Incluye lógica temporal (donador actual vs antecedente)
"""
from pydantic import BaseModel, Field
from typing import Optional

from app.models.base import BaseKeys


class DonacionKeys(BaseKeys):
    """
    Campos específicos para documentos de DONACIÓN

    Hereda 5 campos comunes de BaseKeys
    Agrega 42+ campos específicos de donación

    IMPORTANTE: La donación tiene lógica temporal crítica:
    - ANTECEDENTE = Transacción del PASADO (quién ERA dueño)
    - DONADOR = Propietario ACTUAL (quién ES dueño HOY y dona)
    """

    # Partes
    Parte_Donadora_Nombre_Completo: Optional[str] = Field(
        None,
        description="""===IDENTIFICAR AL DONADOR/A (PROPIETARIO ACTUAL QUE DONA)===

FORMATO DE SALIDA: NOMBRES Y APELLIDOS EN MAYÚSCULAS
Ejemplo: JUAN PEREZ GOMEZ

LÓGICA CRÍTICA - DIFERENCIA TEMPORAL:
- ANTECEDENTE = Transacción del PASADO (quién ERA dueño anteriormente)
- DONADOR = Propietario ACTUAL (quién ES dueño HOY y está donando)

BUSCAR PROPIETARIO ACTUAL SOLO EN ESTOS DOCUMENTOS RECIENTES:

1. **RECIBO CFE/LUZ (PRIORIDAD MÁXIMA):**
   - Buscar el titular del servicio en la parte superior del recibo
   - El nombre que aparece como titular = PROPIETARIO ACTUAL = DONADOR

2. **CONSTANCIA SAT/RFC (PRIORIDAD ALTA):**
   - Buscar campo "Nombre (s):" o "Nombre denominación o razón"
   - Este nombre = PROPIETARIO FISCAL ACTUAL = DONADOR

3. **CONSTANCIA DE NO ADEUDO PREDIAL (PRIORIDAD MEDIA):**
   - Buscar campo "PROPIETARIO:" o "NOMBRE DEL PROPIETARIO:"
   - Este nombre = PROPIETARIO ACTUAL = DONADOR

4. **CERTIFICADO CATASTRAL (PRIORIDAD MEDIA):**
   - Buscar campo "PROPIETARIO/POSEEDOR" o "PROPIETARIO"
   - Este nombre = PROPIETARIO ACTUAL = DONADOR

IGNORAR COMPLETAMENTE (son documentos del PASADO):
- Escrituras antecedentes o instrumentos notariales previos
- Frases como "VENDE a..." o "en favor de..." en documentos históricos
- Contratos de compraventa anteriores ya ejecutados
- Boletas de Registro Público de la Propiedad antiguas
- Cualquier documento que describa transacciones ya realizadas

LÓGICA EXPLICADA:
Si el antecedente dice: "PERSONA_A VENDE a PERSONA_B"
→ Esto es PASADO: Persona_A ya NO es dueña
→ Persona_B RECIBIÓ y ahora ES la propietaria

Si el CFE actual dice: "PERSONA_B"
→ Esto es PRESENTE: Persona_B ES la propietaria actual = DONADORA

El antecedente solo muestra CÓMO llegó a ser propietaria, NO quién ES propietaria HOY.

Si no encuentras propietario en documentos actuales: 'NO LOCALIZADO'"""
    )

    Parte_Donataria_Nombre_Completo: Optional[str] = Field(
        None,
        description="""===IDENTIFICAR AL DONATARIO/A (QUIEN RECIBE LA DONACIÓN)===

FORMATO DE SALIDA: NOMBRES Y APELLIDOS EN MAYÚSCULAS
Ejemplo: MARIA LOPEZ HERNANDEZ

LÓGICA SIMPLE DE EXCLUSIÓN:
El DONATARIO es la persona que RECIBE el inmueble como donación.
Es alguien DIFERENTE al donador que tiene documentación de identidad completa.

MÉTODO DE IDENTIFICACIÓN (PASO A PASO):

PASO 1: Identificar a TODAS las personas que tienen documentos de identidad:
   - Credencial INE/IFE (identificación oficial con fotografía)
   - Acta de Nacimiento (registro civil)
   - Opcionalmente: CURP, Constancia SAT, RFC

PASO 2: De esa lista, ELIMINAR a la persona ya identificada como DONADORA

PASO 3: La persona que quede con documentación completa = DONATARIO

DIFERENCIA CLAVE:
- DONADOR tiene: Documentos de PROPIEDAD (CFE, SAT como propietario, Predial)
- DONATARIO tiene: Documentos de IDENTIDAD (INE, Acta, CURP) pero NO de propiedad

PISTAS ADICIONALES:
- Acta de nacimiento de alguien que NO es el propietario actual
- Persona con INE reciente pero SIN recibos de servicios a su nombre
- Relación familiar mencionada (hijo/a, nieto/a, sobrino/a, hermano/a)
- Persona generalmente más joven en casos de donaciones familiares
- Tiene todos los documentos personales pero NO aparece en CFE/Predial/SAT

PROCESO LÓGICO GENÉRICO:
1. Listar personas con INE + Acta
2. ¿Esta persona es el donador? → SI: excluir, NO: es donatario
3. Si quedan múltiples personas, elegir quien tenga más documentos completos

Si después de excluir al donador no queda nadie con documentos de identidad: 'NO LOCALIZADO'"""
    )

    # Antecedente (igual que compraventa)
    Escritura_Privada_numero: Optional[str] = Field(
        None,
        description="Número en palabras minúsculas. Ejemplo: cuatrocientos noventa y nueve"
    )

    Escritura_Privada_fecha: Optional[str] = Field(
        None,
        description="Fecha completa en palabras minúsculas. Ejemplo: once de diciembre de mil novecientos noventa y seis"
    )

    Escritura_Privada_Notario: Optional[str] = Field(
        None,
        description="Nombre completo con título profesional. Ejemplo: Licenciado Gilberto Rivera Martínez"
    )

    Escritura_Privada_Notario_numero: Optional[str] = Field(
        None,
        description="Número de notaría en palabras minúsculas. Ejemplo: ciento veintitrés"
    )

    Numero_Registro: Optional[str] = Field(
        None,
        description="Número de inscripción RPP en palabras MAYÚSCULAS. Ejemplo: VEINTISIETE"
    )

    Numero_tomo_Registro: Optional[str] = Field(
        None,
        description="Tomo del RPP en palabras MAYÚSCULAS. Ejemplo: TRESCIENTOS OCHENTA Y UNO"
    )

    Nombre_ANTECEDENTE_TRANSMITENTE: Optional[str] = Field(
        None,
        description="Transmitente del antecedente. Ejemplo: la señora María López Hernández"
    )

    # Descripción del predio
    Escritura_Privada_Urbano_Descripcion: Optional[str] = Field(
        None,
        description="Descripción completa del predio en MAYÚSCULAS"
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_1: Optional[str] = Field(
        None,
        description="Primer lado con medidas y colindancias. Ejemplo: NORESTE: 16.00 dieciséis metros, con lote número once"
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_2: Optional[str] = Field(
        None,
        description="Segundo lado con medidas y colindancias"
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_3: Optional[str] = Field(
        None,
        description="Tercer lado con medidas y colindancias"
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_4: Optional[str] = Field(
        None,
        description="Cuarto lado con medidas y colindancias"
    )

    Certificado_Registro_Catastral: Optional[str] = Field(
        None,
        description="Superficie en m². Ejemplo: 145.00 M2 (CIENTO CUARENTA Y CINCO METROS CUADRADOS)"
    )

    # Datos personales Donador
    Edad_Parte_Donadora: Optional[str] = Field(
        None,
        description="Edad en letras + años. Ejemplo: ochenta años"
    )

    Dia_nacimiento_Parte_Donadora: Optional[str] = Field(
        None,
        description="Fecha de nacimiento completa en palabras minúsculas"
    )

    Origen_Parte_Donadora: Optional[str] = Field(
        None,
        description="Lugar de origen. Ejemplo: Pátzcuaro, Michoacán"
    )

    Estado_civil_Parte_Donadora: Optional[str] = Field(
        None,
        description="Estado civil en minúsculas. Ejemplo: casado"
    )

    SAT_situacion_fiscal_Parte_Donadora: Optional[str] = Field(
        None,
        description="RFC completo. Ejemplo: CEAR640813JJ8"
    )

    Comprobante_Domicilio_Parte_Donadora: Optional[str] = Field(
        None,
        description="Dirección completa en minúsculas"
    )

    Identificacion_Parte_Donadora: Optional[str] = Field(
        None,
        description="Tipo de identificación. Ejemplo: credencial para votar con fotografía"
    )

    INE_Parte_Donadora_numero: Optional[str] = Field(
        None,
        description="Clave/folio INE. Ejemplo: IDMEX2650430777"
    )

    CURP_Parte_Donadora: Optional[str] = Field(
        None,
        description="CURP completa. Ejemplo: CEAR640813HMNRRL02"
    )

    RFC_Parte_Donadora: Optional[str] = Field(
        None,
        description="RFC completo. Ejemplo: CEAR640813JJ8"
    )

    # Datos personales Donatario
    Edad_Parte_Donataria: Optional[str] = Field(
        None,
        description="Edad en letras + años. Ejemplo: treinta y siete años"
    )

    Dia_nacimiento_Parte_Donataria: Optional[str] = Field(
        None,
        description="Fecha de nacimiento completa en palabras minúsculas"
    )

    Origen_Parte_Donataria: Optional[str] = Field(
        None,
        description="Lugar de origen. Ejemplo: Zacapu, Michoacán"
    )

    Estado_civil_Parte_Donataria: Optional[str] = Field(
        None,
        description="Estado civil en minúsculas. Ejemplo: divorciado"
    )

    SAT_situacion_fiscal_Parte__Donataria: Optional[str] = Field(
        None,
        description="RFC completo. Ejemplo: GABM780325EG6"
    )

    Comprobante_Domicilio_Parte_Donataria: Optional[str] = Field(
        None,
        description="Dirección completa en minúsculas"
    )

    Identificacion_Parte_Donataria: Optional[str] = Field(
        None,
        description="Tipo de identificación. Ejemplo: credencial para votar con fotografía"
    )

    INE_Parte_Donataria_numero: Optional[str] = Field(
        None,
        description="Clave/folio INE. Ejemplo: IDMEX2749126814"
    )

    CURP_Parte_Donataria: Optional[str] = Field(
        None,
        description="CURP completa. Ejemplo: GABM780325HMNRRR02"
    )

    RFC_Parte_Donataria: Optional[str] = Field(
        None,
        description="RFC completo. Ejemplo: GABM780325EG6"
    )

    # Documentos oficiales
    Constancia_No_Adeudo_Urbano_Fecha: Optional[str] = Field(
        None,
        description="Fecha de Constancia de No Adeudo en palabras minúsculas"
    )

    Certificado_Registro_Catastral_Urbano_Fecha: Optional[str] = Field(
        None,
        description="Fecha del Certificado Catastral en palabras minúsculas"
    )

    Avaluo_Urbano_Datos_Generales_Fecha: Optional[str] = Field(
        None,
        description="Fecha del Avalúo en palabras minúsculas"
    )

    Numero_Avaluo: Optional[str] = Field(
        None,
        description="Número completo del avalúo. Ejemplo: 2025-134-387"
    )

    Valor_Catastral: Optional[str] = Field(
        None,
        description="Valor catastral con formato. Ejemplo: $31,920.00"
    )

    Valuador: Optional[str] = Field(
        None,
        description="Nombre del valuador con título. Ejemplo: ING. JAVIER LIEVANOS HUERTA"
    )

    # Tratamientos
    Tratamiento_Donador: Optional[str] = Field(
        None,
        description="Tratamiento del donador: el señor / la señora / la parte donadora"
    )

    Tratamiento_Donatario: Optional[str] = Field(
        None,
        description="Tratamiento del donatario: el señor / la señora / la parte donataria"
    )

    # Campos específicos de donación
    Parentezco: Optional[str] = Field(
        None,
        description="""Parentesco del donatario respecto del donador en minúsculas.
Ejemplos: hija, hijo, nieto, sobrina
Fuente: comparecencia, cláusulas, constancias, acta de nacimiento o lógica de apellidos.
Si no aparece: 'NO LOCALIZADO'"""
    )

    Estado_civil_acreditacion_Parte_Donataria: Optional[str] = Field(
        None,
        description="""Estado civil del donatario y documento que lo acredita.
Ejemplo: tal y como lo acredita con la copia certificada de su acta de matrimonio la cual quedará agregada al apéndice de la presente escritura"""
    )

    Estado_civil_acreditacion_Parte_Donadora: Optional[str] = Field(
        None,
        description="""Estado civil del donador y documento que lo acredita.
Ejemplo: tal y como lo acredita con la copia certificada de su acta de matrimonio la cual quedará agregada al apéndice de la presente escritura"""
    )

    class Config:
        json_schema_extra = {
            "example": {
                "Parte_Donadora_Nombre_Completo": "JUAN PEREZ GOMEZ",
                "Parte_Donataria_Nombre_Completo": "MARIA PEREZ LOPEZ",
                "Parentezco": "hija",
                "Edad_Parte_Donadora": "setenta años",
                "Edad_Parte_Donataria": "cuarenta años",
                "RFC_Parte_Donadora": "PEGJ540310JJ8",
                "RFC_Parte_Donataria": "PELM840520EG6",
                "Tratamiento_Donador": "el señor",
                "Tratamiento_Donatario": "la señora"
            }
        }
