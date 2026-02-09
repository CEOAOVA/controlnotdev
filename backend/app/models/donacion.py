"""
ControlNot v2 - Modelo Donación
48 campos específicos para documentos de donación

Migrado de por_partes.py líneas 785-1283
IMPORTANTE: Incluye lógica temporal (donador actual vs antecedente)
Actualizado: Agregados campos faltantes de archivos madre
"""
from pydantic import BaseModel, Field
from typing import Optional

from app.models.base import BaseKeys


class DonacionKeys(BaseKeys):
    """
    Campos específicos para documentos de DONACIÓN

    Hereda 5 campos comunes de BaseKeys
    Agrega 48 campos específicos de donación (actualizado)

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

    # ==========================================
    # ANTECEDENTE DE PROPIEDAD
    # Puede ser: Escritura Notarial, Juicio Sucesorio, Sentencia, etc.
    # ==========================================

    Antecedente_Tipo: Optional[str] = Field(
        None,
        description="""TIPO DE ANTECEDENTE de la propiedad.

VALORES POSIBLES:
- escritura: Escritura pública o privada notarial
- juicio_sucesorio: Juicio sucesorio intestamentario o testamentario
- sentencia: Sentencia judicial de adjudicación
- contrato_privado: Contrato privado de compraventa
- otro: Otro tipo de documento

COMO DETECTAR:
- Si aparece "JUICIO SUCESORIO", "SUCESION A BIENES DE", "INTESTAMENTARIO" → juicio_sucesorio
- Si aparece "SENTENCIA", "JUZGADO", "EXPEDIENTE JUDICIAL" → sentencia
- Si aparece "ESCRITURA", "INSTRUMENTO", "NOTARIA" → escritura
- Si no se identifica claramente → escritura (default)

Si no hay antecedente visible: '**[NO ENCONTRADO]**'"""
    )

    Escritura_Privada_numero: Optional[str] = Field(
        None,
        description="""Número del instrumento antecedente en palabras minúsculas.

APLICA PARA: Escrituras notariales (NO juicios sucesorios)
Ejemplo: cuatrocientos noventa y nueve

Si el antecedente es JUICIO SUCESORIO, este campo debe ser: '**[NO ENCONTRADO]**'
(usar campo Juicio_Sucesorio_Expediente en su lugar)"""
    )

    Escritura_Privada_fecha: Optional[str] = Field(
        None,
        description="""Fecha del instrumento antecedente en palabras minúsculas.

APLICA PARA: Escrituras notariales (NO juicios sucesorios)
Ejemplo: once de diciembre de mil novecientos noventa y seis

Si el antecedente es JUICIO SUCESORIO, este campo debe ser: '**[NO ENCONTRADO]**'
(usar campo Juicio_Sucesorio_Fecha_Sentencia en su lugar)"""
    )

    Escritura_Privada_Notario: Optional[str] = Field(
        None,
        description="""Nombre del Notario del instrumento antecedente con título profesional.

APLICA PARA: Escrituras notariales (NO juicios sucesorios)
Ejemplo: Licenciado Gilberto Rivera Martínez

IMPORTANTE - DISTINGUIR:
- Si viene de una ESCRITURA NOTARIAL → extraer el notario de esa escritura
- Si viene de un JUICIO SUCESORIO → usar campo Juicio_Sucesorio_Notario_Protocolizacion

Si el antecedente NO es escritura notarial: '**[NO ENCONTRADO]**'"""
    )

    Escritura_Privada_Notario_numero: Optional[str] = Field(
        None,
        description="""Número de notaría del instrumento antecedente en palabras minúsculas.

APLICA PARA: Escrituras notariales (NO juicios sucesorios)
Ejemplo: ciento veintitrés

Si el antecedente NO es escritura notarial: '**[NO ENCONTRADO]**'"""
    )

    # ==========================================
    # CAMPOS ESPECÍFICOS PARA JUICIO SUCESORIO
    # Usar cuando el antecedente es un juicio sucesorio
    # ==========================================

    Juicio_Sucesorio_Tipo: Optional[str] = Field(
        None,
        description="""Tipo de juicio sucesorio.

VALORES: intestamentario, testamentario

BUSCAR: "JUICIO SUCESORIO INTESTAMENTARIO" o "JUICIO SUCESORIO TESTAMENTARIO"
- Intestamentario: cuando NO hay testamento
- Testamentario: cuando SÍ hay testamento

Si el antecedente NO es juicio sucesorio: '**[NO ENCONTRADO]**'""",
        json_schema_extra={"optional_field": True, "source": "juicio_sucesorio"}
    )

    Juicio_Sucesorio_Juzgado: Optional[str] = Field(
        None,
        description="""Juzgado que conoció del juicio sucesorio.

FORMATO: Nombre completo del juzgado
EJEMPLOS:
- Juzgado Primero Civil de Primera Instancia del Distrito Judicial de Morelia
- Juzgado Segundo de lo Familiar de Zacapu, Michoacán

BUSCAR: "JUZGADO", "TRIBUNAL", después de "ante el" o "radicado en"

Si el antecedente NO es juicio sucesorio: '**[NO ENCONTRADO]**'""",
        json_schema_extra={"optional_field": True, "source": "juicio_sucesorio"}
    )

    Juicio_Sucesorio_Expediente: Optional[str] = Field(
        None,
        description="""Número de expediente del juicio sucesorio.

FORMATO: Número tal como aparece
EJEMPLOS: 123/2020, 2019-456, EXP. 789/2021

BUSCAR: "EXPEDIENTE", "EXP.", "No. DE EXPEDIENTE"

Si el antecedente NO es juicio sucesorio: '**[NO ENCONTRADO]**'""",
        json_schema_extra={"optional_field": True, "source": "juicio_sucesorio"}
    )

    Juicio_Sucesorio_Causante: Optional[str] = Field(
        None,
        description="""Nombre del causante (persona fallecida) del juicio sucesorio.

FORMATO: Nombre completo con tratamiento
EJEMPLOS:
- la señora María López Hernández
- el señor Juan Pérez García

BUSCAR: "SUCESION A BIENES DE", "DE CUJUS", "CAUSANTE", "QUIEN EN VIDA FUE"

Si el antecedente NO es juicio sucesorio: '**[NO ENCONTRADO]**'""",
        json_schema_extra={"optional_field": True, "source": "juicio_sucesorio"}
    )

    Juicio_Sucesorio_Fecha_Sentencia: Optional[str] = Field(
        None,
        description="""Fecha de la sentencia del juicio sucesorio en palabras.

FORMATO: Fecha completa en palabras minúsculas
EJEMPLOS: dieciséis de julio de dos mil veinticinco

BUSCAR: "SENTENCIA DE FECHA", "RESOLUCION DE", "ADJUDICACION DE FECHA"

Si el antecedente NO es juicio sucesorio: '**[NO ENCONTRADO]**'""",
        json_schema_extra={"optional_field": True, "source": "juicio_sucesorio"}
    )

    Juicio_Sucesorio_Notario_Protocolizacion: Optional[str] = Field(
        None,
        description="""Notario que protocolizó la sentencia del juicio sucesorio.

FORMATO: Nombre completo con título profesional
EJEMPLOS: Lic. Ana Mariela Servin Pita, Licenciado Roberto García López

BUSCAR: "PROTOCOLIZADO ANTE", "NOTARIO QUE PROTOCOLIZO", después de la sentencia

IMPORTANTE: Este es el notario que convirtió la sentencia judicial en escritura pública,
NO es el notario de una escritura antecedente regular.

Si el antecedente NO es juicio sucesorio: '**[NO ENCONTRADO]**'""",
        json_schema_extra={"optional_field": True, "source": "juicio_sucesorio"}
    )

    Numero_Registro: Optional[str] = Field(
        None,
        description="""NUMERO DE INSCRIPCION en el Registro Público de la Propiedad (RPP).

FORMATO DE SALIDA: Número en palabras MAYÚSCULAS
EJEMPLOS: DIECIOCHO, VEINTISIETE, MIL SEISCIENTOS OCHENTA Y OCHO

BUSCAR EN BOLETA RPP o ASIENTO REGISTRAL:
- Campo "REGISTRO:", "INSCRIPCION:", "No. DE INSCRIPCION:"
- Puede aparecer como número (00000018, 18) o ya en palabras

CONVERSION AUTOMATICA:
- Si encuentras "00000018" o "18" → extraer como DIECIOCHO
- Si encuentras "00001688" o "1688" → extraer como MIL SEISCIENTOS OCHENTA Y OCHO
- Si ya viene en palabras, mantener tal cual

IMPORTANTE: El sistema convertirá automáticamente números a palabras.
Puedes extraer el valor como aparece (número o palabras).

Si no hay boleta RPP visible: '**[NO ENCONTRADO]**'""",
        json_schema_extra={"optional_field": True, "source": "boleta_rpp", "auto_convert": True}
    )

    Numero_tomo_Registro: Optional[str] = Field(
        None,
        description="""NUMERO DE TOMO en el Registro Público de la Propiedad (RPP).

FORMATO DE SALIDA: Número en palabras MAYÚSCULAS
EJEMPLOS: TRESCIENTOS OCHENTA Y UNO, MIL SEISCIENTOS OCHENTA Y OCHO

BUSCAR EN BOLETA RPP o ASIENTO REGISTRAL:
- Campo "TOMO:", "No. DE TOMO:", "LIBRO:"
- Puede aparecer como número (00001688, 381) o ya en palabras

CONVERSION AUTOMATICA:
- Si encuentras "00001688" o "1688" → extraer como MIL SEISCIENTOS OCHENTA Y OCHO
- Si encuentras "00000381" o "381" → extraer como TRESCIENTOS OCHENTA Y UNO
- Si ya viene en palabras, mantener tal cual

IMPORTANTE: El sistema convertirá automáticamente números a palabras.
Puedes extraer el valor como aparece (número o palabras).

Si no hay boleta RPP visible: '**[NO ENCONTRADO]**'""",
        json_schema_extra={"optional_field": True, "source": "boleta_rpp", "auto_convert": True}
    )

    Nombre_ANTECEDENTE_TRANSMITENTE: Optional[str] = Field(
        None,
        description="""Transmitente del antecedente. Ejemplo: la señora María López Hernández

LOGICA TEMPORAL: Buscar en la escritura antecedente quien VENDIO o TRANSFIRIO la propiedad.
BUSCAR frases clave: "VENDE a", "ENAJENA a", "CEDE a", "TRANSMITE a", "OTORGA en favor de"
La persona que aparece ANTES de estas frases es el transmitente.
FORMATO: tratamiento + nombre completo (ej: "el señor Juan Pérez García")
BUSCAR EN: documentos de categoria 'otros' (escritura antecedente, boleta RPP)"""
    )

    # Descripción del predio
    Escritura_Privada_Urbano_Descripcion: Optional[str] = Field(
        None,
        description="""Descripción completa del predio en MAYÚSCULAS

BUSCAR EN: escritura antecedente, certificado catastral, avaluo (categoria 'otros')
Buscar frases: "LOTE DE TERRENO", "FRACCION", "PREDIO URBANO", "INMUEBLE UBICADO EN"
Incluir: tipo de predio, ubicacion (calle, numero, colonia, ciudad), clave catastral si existe
FORMATO: Todo en MAYUSCULAS, descripcion completa tal como aparece en el documento"""
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_1: Optional[str] = Field(
        None,
        description="""Primer lado con medidas y colindancias. Ejemplo: NORESTE: 16.00 dieciséis metros, con lote número once

FORMATO: ORIENTACION + medida numerica + medida en palabras + colindancia
BUSCAR EN: escritura antecedente, certificado catastral, avaluo (categoria 'otros')
Buscar secciones de "MEDIDAS Y COLINDANCIAS", "LINDEROS", "DIMENSIONES"
Ejemplo completo: "AL NORTE: 16.00 dieciseis metros, colinda con lote numero once" """
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_2: Optional[str] = Field(
        None,
        description="""Segundo lado con medidas y colindancias

FORMATO: ORIENTACION + medida numerica + medida en palabras + colindancia
BUSCAR EN: escritura antecedente, certificado catastral, avaluo (categoria 'otros')"""
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_3: Optional[str] = Field(
        None,
        description="""Tercer lado con medidas y colindancias

FORMATO: ORIENTACION + medida numerica + medida en palabras + colindancia
BUSCAR EN: escritura antecedente, certificado catastral, avaluo (categoria 'otros')"""
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_4: Optional[str] = Field(
        None,
        description="""Cuarto lado con medidas y colindancias

FORMATO: ORIENTACION + medida numerica + medida en palabras + colindancia
BUSCAR EN: escritura antecedente, certificado catastral, avaluo (categoria 'otros')"""
    )

    Certificado_Registro_Catastral: Optional[str] = Field(
        None,
        description="""Superficie en m². Ejemplo: 145.00 M2 (CIENTO CUARENTA Y CINCO METROS CUADRADOS)

BUSCAR EN: certificado catastral, avaluo, escritura antecedente (categoria 'otros')
Buscar: "SUPERFICIE", "AREA DEL TERRENO", "SUPERFICIE TOTAL", "AREA CONSTRUIDA"
FORMATO: numero + M2 + (numero en palabras MAYUSCULAS + METROS CUADRADOS)"""
    )

    # Datos personales Donador
    Edad_Parte_Donadora: Optional[str] = Field(
        None,
        description="""CALCULAR la edad del DONADOR a partir de su fecha de nacimiento.

FORMATO DE SALIDA: número en palabras + "años"
Ejemplo: ochenta años, sesenta y un años

PROCESO DE CÁLCULO:
1. Localiza la fecha de nacimiento del DONADOR en:
   - Acta de Nacimiento (fecha registrada)
   - INE/IFE (fecha de nacimiento)
   - CURP (los 6 dígitos después de las letras = AAMMDD)
2. Calcula: año_actual - año_de_nacimiento
3. Si el cumpleaños de este año aún no ha pasado, resta 1
4. Convierte el número a palabras en español

CONVERSIÓN A PALABRAS:
- 45 = cuarenta y cinco años
- 61 = sesenta y un años
- 78 = setenta y ocho años
- 82 = ochenta y dos años

Si no encuentras fecha de nacimiento: '**[NO ENCONTRADO]**'"""
    )

    Dia_nacimiento_Parte_Donadora: Optional[str] = Field(
        None,
        description="""Fecha de nacimiento del DONADOR en palabras minúsculas.

FORMATO: día de mes de año (todo en palabras)
Ejemplo: trece de agosto de mil novecientos sesenta y cuatro

FUENTES: Acta de Nacimiento, INE, CURP"""
    )

    Origen_Parte_Donadora: Optional[str] = Field(
        None,
        description="""Lugar de origen. Ejemplo: Pátzcuaro, Michoacán

BUSCAR EN: acta de nacimiento del DONADOR (categoria 'parte_a')
Campo "Lugar de nacimiento", "Lugar de origen", "Nacio en"
FORMATO: Ciudad, Estado (ej: "Morelia, Michoacán", "Zacapu, Michoacán")"""
    )

    Estado_civil_Parte_Donadora: Optional[str] = Field(
        None,
        description="""Estado civil en minúsculas. Ejemplo: casado

BUSCAR EN: acta de matrimonio, anotaciones marginales en acta de nacimiento, INE del DONADOR
Valores posibles: casado, casada, soltero, soltera, viudo, viuda, divorciado, divorciada
Si hay acta de matrimonio entre documentos parte_a → probablemente casado/a"""
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
        description="""NUMERO OCR / IDMEX del INE del DONADOR.

UBICACION CRITICA: REVERSO de la credencial INE/IFE
- Buscar en la zona MRZ (Machine Readable Zone) - parte inferior del reverso
- Es un código alfanumérico que identifica de forma única la credencial

FORMATO: IDMEX + 10 dígitos numéricos
EJEMPLOS: IDMEX2650430777, IDMEX2545265854

INSTRUCCIONES:
1. Localizar el REVERSO de la credencial INE del DONADOR
2. Buscar la línea que comienza con "IDMEX" en la zona inferior
3. Extraer SOLO caracteres alfanuméricos (ignorar símbolos < o >>)
4. El código completo debe tener 14 caracteres (IDMEX + 10 dígitos)

NOTA: Este dato NO aparece en el frente de la credencial.
Si no está visible el reverso del INE: '**[NO ENCONTRADO]**'"""
    )

    CURP_Parte_Donadora: Optional[str] = Field(
        None,
        description="CURP completa. Ejemplo: CEAR640813HMNRRL02"
    )

    RFC_Parte_Donadora: Optional[str] = Field(
        None,
        description="RFC completo. Ejemplo: CEAR640813JJ8"
    )

    Parte_Donadora_Ocupacion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Ocupación en minúsculas
Ejemplo: comerciante, empleado, hogar, jubilado

FUENTES DE BÚSQUEDA (en orden de prioridad):
1. MANIFESTACIÓN EN GENERALES: Buscar frases como "de ocupación...", "dedicado a...", "se dedica a..."
2. ACTA DE NACIMIENTO: Sección de anotaciones marginales o datos de los padres
3. INE/IFE: Algunos formatos incluyen ocupación

OCUPACIONES COMUNES EN NOTARÍAS:
- Profesiones: licenciado, ingeniero, contador, arquitecto, médico, abogado
- Oficios: comerciante, empleado, obrero, agricultor, ganadero, artesano
- Sin actividad: hogar, jubilado, pensionado, estudiante

IMPORTANTE: Usa minúsculas sin artículo (no "el comerciante", solo "comerciante")

Si no encuentras ocupación explícita: '**[NO ENCONTRADO]**'"""
    )

    # Datos personales Donatario
    Edad_Parte_Donataria: Optional[str] = Field(
        None,
        description="""CALCULAR la edad del DONATARIO a partir de su fecha de nacimiento.

FORMATO DE SALIDA: número en palabras + "años"
Ejemplo: treinta y siete años, cuarenta y cinco años

PROCESO DE CÁLCULO:
1. Localiza la fecha de nacimiento del DONATARIO en:
   - Acta de Nacimiento (fecha registrada)
   - INE/IFE (fecha de nacimiento)
   - CURP (los 6 dígitos después de las letras = AAMMDD)
2. Calcula: año_actual - año_de_nacimiento
3. Si el cumpleaños de este año aún no ha pasado, resta 1
4. Convierte el número a palabras en español

CONVERSIÓN A PALABRAS:
- 37 = treinta y siete años
- 45 = cuarenta y cinco años
- 52 = cincuenta y dos años

Si no encuentras fecha de nacimiento: '**[NO ENCONTRADO]**'"""
    )

    Dia_nacimiento_Parte_Donataria: Optional[str] = Field(
        None,
        description="""Fecha de nacimiento del DONATARIO en palabras minúsculas.

FORMATO: día de mes de año (todo en palabras)
Ejemplo: veintidós de marzo de mil novecientos ochenta y ocho

FUENTES: Acta de Nacimiento, INE, CURP"""
    )

    Origen_Parte_Donataria: Optional[str] = Field(
        None,
        description="""Lugar de origen. Ejemplo: Zacapu, Michoacán

BUSCAR EN: acta de nacimiento del DONATARIO (categoria 'parte_b')
Campo "Lugar de nacimiento", "Lugar de origen", "Nacio en"
FORMATO: Ciudad, Estado (ej: "Morelia, Michoacán", "Zacapu, Michoacán")"""
    )

    Estado_civil_Parte_Donataria: Optional[str] = Field(
        None,
        description="""Estado civil en minúsculas. Ejemplo: divorciado

BUSCAR EN: acta de matrimonio, anotaciones marginales en acta de nacimiento, INE del DONATARIO
Valores posibles: casado, casada, soltero, soltera, viudo, viuda, divorciado, divorciada
Si hay acta de matrimonio entre documentos parte_b → probablemente casado/a"""
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
        description="""NUMERO OCR / IDMEX del INE del DONATARIO.

UBICACION CRITICA: REVERSO de la credencial INE/IFE
- Buscar en la zona MRZ (Machine Readable Zone) - parte inferior del reverso
- Es un código alfanumérico que identifica de forma única la credencial

FORMATO: IDMEX + 10 dígitos numéricos
EJEMPLOS: IDMEX2749126814, IDMEX2545265854

INSTRUCCIONES:
1. Localizar el REVERSO de la credencial INE del DONATARIO
2. Buscar la línea que comienza con "IDMEX" en la zona inferior
3. Extraer SOLO caracteres alfanuméricos (ignorar símbolos < o >>)
4. El código completo debe tener 14 caracteres (IDMEX + 10 dígitos)

NOTA: Este dato NO aparece en el frente de la credencial.
Si no está visible el reverso del INE: '**[NO ENCONTRADO]**'"""
    )

    CURP_Parte_Donataria: Optional[str] = Field(
        None,
        description="CURP completa. Ejemplo: GABM780325HMNRRR02"
    )

    RFC_Parte_Donataria: Optional[str] = Field(
        None,
        description="RFC completo. Ejemplo: GABM780325EG6"
    )

    Parte_Donataria_Ocupacion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Ocupación en minúsculas
Ejemplo: empleado, comerciante, hogar, estudiante

FUENTES DE BÚSQUEDA (en orden de prioridad):
1. MANIFESTACIÓN EN GENERALES: Buscar frases como "de ocupación...", "dedicado a...", "se dedica a..."
2. ACTA DE NACIMIENTO: Sección de anotaciones marginales
3. INE/IFE: Algunos formatos incluyen ocupación

OCUPACIONES COMUNES EN NOTARÍAS:
- Profesiones: licenciado, ingeniero, contador, arquitecto, médico, abogado
- Oficios: comerciante, empleado, obrero, agricultor, ganadero, artesano
- Sin actividad: hogar, jubilado, pensionado, estudiante

IMPORTANTE: Usa minúsculas sin artículo (no "la empleada", solo "empleada")

Si no encuentras ocupación explícita: '**[NO ENCONTRADO]**'"""
    )

    # Documentos oficiales
    Constancia_No_Adeudo_Urbano_Fecha: Optional[str] = Field(
        None,
        description="""Fecha de Constancia de No Adeudo en palabras minúsculas

BUSCAR EN: constancia de no adeudo de predial (categoria 'otros')
Buscar: "FECHA DE EXPEDICION", "EXPEDIDA EL", fecha del documento
FORMATO: dia de mes de año en palabras (ej: "quince de enero de dos mil veinticinco")""",
        json_schema_extra={"optional_field": True, "source": "constancia_no_adeudo"}
    )

    Certificado_Registro_Catastral_Urbano_Fecha: Optional[str] = Field(
        None,
        description="""Fecha del Certificado Catastral en palabras minúsculas

BUSCAR EN: certificado catastral (categoria 'otros')
Buscar: "FECHA DE EXPEDICION", fecha del documento catastral
FORMATO: dia de mes de año en palabras (ej: "diez de febrero de dos mil veinticinco")""",
        json_schema_extra={"optional_field": True, "source": "certificado_catastral"}
    )

    Avaluo_Urbano_Datos_Generales_Fecha: Optional[str] = Field(
        None,
        description="""Fecha del Avalúo en palabras minúsculas

BUSCAR EN: avaluo o dictamen de valuacion (categoria 'otros')
Buscar: "FECHA DEL AVALUO", "FECHA DE VALUACION", "VIGENCIA"
FORMATO: dia de mes de año en palabras (ej: "veinte de marzo de dos mil veinticinco")""",
        json_schema_extra={"optional_field": True, "source": "avaluo"}
    )

    Numero_Avaluo: Optional[str] = Field(
        None,
        description="""Número completo del avalúo. Ejemplo: 2025-134-387

BUSCAR EN: avaluo o dictamen de valuacion (categoria 'otros')
Buscar: NUMERO DE AVALUO, No. DE AVALUO, FOLIO""",
        json_schema_extra={"optional_field": True, "source": "avaluo"}
    )

    Valor_Catastral: Optional[str] = Field(
        None,
        description="""Valor catastral con formato. Ejemplo: $31,920.00

BUSCAR EN: avaluo, certificado catastral (categoria 'otros')
Buscar: "VALOR CATASTRAL", "VALOR FISCAL", "VALOR DEL TERRENO"
FORMATO: $X,XXX.XX""",
        json_schema_extra={"optional_field": True, "source": "avaluo"}
    )

    Valuador: Optional[str] = Field(
        None,
        description="""Nombre del valuador con título. Ejemplo: ING. JAVIER LIEVANOS HUERTA

BUSCAR EN: avaluo o dictamen de valuacion (categoria 'otros')
Buscar: "PERITO VALUADOR", "VALUADOR", "ELABORO"
FORMATO: TITULO + NOMBRE COMPLETO EN MAYUSCULAS""",
        json_schema_extra={"optional_field": True, "source": "avaluo"}
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
        description="""FRASE LEGAL COMPLETA que acredita el estado civil del DONATARIO.

FORMATO POR ESTADO CIVIL:

CASADO(A):
"tal y como lo acredita con la copia certificada de su acta de matrimonio la cual quedará agregada al apéndice de la presente escritura"

SOLTERO(A):
"estado civil que manifiesta bajo protesta de decir verdad"
(alternativa: "tal y como lo acredita con su acta de nacimiento en donde no aparece anotación marginal de matrimonio")

VIUDO(A):
"tal y como lo acredita con la copia certificada del acta de defunción de quien en vida fue su cónyuge"

DIVORCIADO(A):
"tal y como lo acredita con la sentencia de divorcio debidamente ejecutoriada"

UNIÓN LIBRE:
"estado civil que manifiesta bajo protesta de decir verdad"

INSTRUCCIÓN:
1. Identifica el estado civil del DONATARIO (casado, soltero, viudo, divorciado)
2. Busca el documento que lo acredita entre los documentos adjuntos
3. Genera la frase legal correspondiente

Si solo hay manifestación verbal: 'estado civil que manifiesta bajo protesta de decir verdad'
Si no hay información: '**[NO ENCONTRADO]**'"""
    )

    Estado_civil_acreditacion_Parte_Donadora: Optional[str] = Field(
        None,
        description="""FRASE LEGAL COMPLETA que acredita el estado civil del DONADOR.

FORMATO POR ESTADO CIVIL:

CASADO(A):
"tal y como lo acredita con la copia certificada de su acta de matrimonio la cual quedará agregada al apéndice de la presente escritura"

SOLTERO(A):
"estado civil que manifiesta bajo protesta de decir verdad"
(alternativa: "tal y como lo acredita con su acta de nacimiento en donde no aparece anotación marginal de matrimonio")

VIUDO(A):
"tal y como lo acredita con la copia certificada del acta de defunción de quien en vida fue su cónyuge"

DIVORCIADO(A):
"tal y como lo acredita con la sentencia de divorcio debidamente ejecutoriada"

UNIÓN LIBRE:
"estado civil que manifiesta bajo protesta de decir verdad"

INSTRUCCIÓN:
1. Identifica el estado civil del DONADOR (casado, soltero, viudo, divorciado)
2. Busca el documento que lo acredita entre los documentos adjuntos
3. Genera la frase legal correspondiente

Si solo hay manifestación verbal: 'estado civil que manifiesta bajo protesta de decir verdad'
Si no hay información: '**[NO ENCONTRADO]**'"""
    )

    Acreditacion_Parentesco: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Documento que acredita el parentesco
Ejemplo: acta de nacimiento del donatario

Indica el documento que acredita la relación familiar entre donador y donatario.
Fuente: Acta de nacimiento, acta de matrimonio, constancia de adopción.
Si no hay parentesco o no se acredita: 'no aplica'"""
    )

    Motivo_Donacion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Descripción del motivo en minúsculas
Ejemplo: por el amor y cariño que le profesa

Extrae el motivo o causa de la donación manifestado por el donador.
Fuente: Cláusulas del contrato, manifestación de voluntad.
Si no se especifica: 'por la voluntad del donador'"""
    )

    Clausula_Reserva_Usufructo: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Texto descriptivo de la reserva
Ejemplo: El donador se reserva el usufructo vitalicio del inmueble donado

Indica si el donador se reserva el derecho de uso y goce del inmueble.
Fuente: Cláusulas del contrato.
Si no hay reserva: 'sin reserva de usufructo'"""
    )

    Aceptacion_Donacion_Explicita: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Texto de aceptación
Ejemplo: El donatario acepta expresamente la donación que se le hace

Extrae la declaración explícita de aceptación de la donación por parte del donatario.
Fuente: Cláusulas del contrato, declaración del donatario.
La aceptación es requisito legal para la validez de la donación."""
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
