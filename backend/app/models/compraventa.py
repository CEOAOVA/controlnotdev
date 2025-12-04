"""
ControlNot v2 - Modelo Compraventa
51 campos específicos para documentos de compraventa

Migrado de por_partes.py líneas 377-782
Actualizado: Agregados campos faltantes de archivos madre
"""
from pydantic import BaseModel, Field
from typing import Optional

from app.models.base import BaseKeys


class CompraventaKeys(BaseKeys):
    """
    Campos específicos para documentos de COMPRAVENTA

    Hereda 5 campos comunes de BaseKeys:
    - fecha_instrumento, lugar_instrumento, numero_instrumento
    - notario_actuante, numero_notaria

    Agrega 51 campos específicos de compraventa (actualizado con campos de archivos madre)
    """

    # Parte Vendedora
    Parte_Vendedora_Nombre_Completo: Optional[str] = Field(
        None,
        description="""===IDENTIFICAR AL VENDEDOR (PROPIETARIO ACTUAL)===

FORMATO DE SALIDA: NOMBRES Y APELLIDOS EN MAYÚSCULAS
Ejemplo: RAUL CERVANTES AREVALO

El VENDEDOR es quien ACTUALMENTE posee el inmueble y lo está vendiendo.

BUSCAR ÚNICAMENTE EN DOCUMENTOS DE PROPIEDAD ACTUAL:

1. En "Constancia de No Adeudo" buscar después de:
   - "NOMBRE DEL PROPIETARIO:"
   - "PROPIETARIO:"

2. En "Certificado Catastral" o "Certificado de Registro Catastral" buscar después de:
   - "PROPIETARIO/POSEEDOR"
   - "PROPIETARIO"

3. En "Avalúo" buscar después de:
   - "PROPIETARIO:"
   - "SOLICITANTE:"

REGLA CRÍTICA: IGNORAR completamente cualquier mención de "VENDEDOR" o "PARTE VENDEDORA"
que aparezca en documentos de ANTECEDENTE, ESCRITURA PREVIA, o INSTRUMENTO ANTERIOR.

Solo el propietario ACTUAL en documentos oficiales ES EL VENDEDOR de la operación presente.

Si no encuentras propietario actual, devuelve 'NO LOCALIZADO'"""
    )

    Parte_Compradora_Nombre_Completo: Optional[str] = Field(
        None,
        description="""===IDENTIFICAR AL COMPRADOR===

FORMATO DE SALIDA: NOMBRES Y APELLIDOS EN MAYÚSCULAS
Ejemplo: MARCO ANTONIO GARCIA BARBOZA

LÓGICA PRÁCTICA:
- Si una persona es propietario actual (vendedor)
- Y otra persona tiene INE + SAT pero NO es propietario
- ENTONCES esa segunda persona ES EL COMPRADOR

BUSCAR exactamente:
1. ENCUENTRA personas con CREDENCIAL INE + CONSTANCIA SAT
2. EXCLUYE al vendedor (ya identificado)
3. LA PERSONA QUE QUEDE con documentos ES EL COMPRADOR

Solo devuelve 'NO LOCALIZADO' si no hay una segunda persona con documentos."""
    )

    # Antecedente
    Escritura_Privada_numero: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número en palabras minúsculas
Ejemplo: cuatrocientos noventa y nueve

Extrae el número del instrumento antecedente.
Fuente: instrumento antecedente o asiento RPP.
Mantener en palabras tal como aparece en el documento."""
    )

    Escritura_Privada_fecha: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: once de diciembre de mil novecientos noventa y seis

Extrae la fecha del instrumento antecedente.
Fuente: instrumento antecedente.
Mantener formato completo en palabras minúsculas."""
    )

    Escritura_Privada_Notario: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Nombre completo con título profesional
Ejemplo: Licenciado Gilberto Rivera Martínez

Extrae el nombre del Notario del instrumento antecedente.
Fuente: instrumento antecedente.
Incluir título profesional si aparece."""
    )

    Escritura_Privada_Notario_numero: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: escrito con palabras minúsculas
Ejemplo: ciento veintitrés

Extrae el número de Notaría del instrumento antecedente.
Fuente: instrumento antecedente.
Convertir palabras a números si es necesario."""
    )

    Numero_Registro: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número en palabras MAYÚSCULAS
Ejemplo: VEINTISIETE

Extrae el número de inscripción en el RPP del antecedente.
Fuente: boleta/asiento RPP.
Mantener en palabras MAYÚSCULAS."""
    )

    Numero_tomo_Registro: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número en palabras MAYÚSCULAS
Ejemplo: TRESCIENTOS OCHENTA Y UNO

Extrae el tomo del RPP del antecedente.
Fuente: boleta/asiento RPP.
Mantener en palabras MAYÚSCULAS."""
    )

    Nombre_ANTECEDENTE_TRANSMITENTE: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: la señora/el señora + Nombres y apellidos (primera letra mayúscula)
Ejemplo: la señora María López Hernández

Esta persona aparece SOLO en documentos HISTÓRICOS/ANTECEDENTES.
Buscar en escrituras previas, boletas RPP o referencias históricas.
Es quien transmitió la propiedad al vendedor actual en operación PREVIA."""
    )

    # Descripción del predio
    Escritura_Privada_Urbano_Descripcion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Descripción completa en MAYÚSCULAS
Ejemplo: LOTE DOCE, DE LA MANZANA XXXIV, QUE FORMA PARTE DEL FRACCIONAMIENTO DE INTERÉS SOCIAL "JARDINES DE ZACAPU", UBICADO EN EL RANCHO DE CABALLERÍAS DE ESTE MUNICIPIO DE ZACAPU, MICHOACÁN

Extrae descripción del predio urbano completa.
Fuente: antecedente/contrato; valida con Certificado Catastral.
Mantener descripción completa en MAYÚSCULAS."""
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_1: Optional[str] = Field(
        None,
        description="""OBJETIVO: Capturar el PRIMER lado que aparezca en las cláusulas/planos de medidas.
DETECCIÓN: No asumas esquema. Toma literalmente la etiqueta encontrada (p. ej. "NORESTE", "ORIENTE", "SUR", "PONIENTE", etc.).
FORMATO DE SALIDA: {DIRECCION}: {DECIMAL_2} {en_palabras} metros{, centímetros si aparecen}, con {colindancia}
REGLAS:
  - Mantén la DIRECCION tal cual aparece (no traduzcas ni normalices a otra rosa de vientos).
  - Normaliza la medida numérica a dos decimales (ej. 07.00, 16.00, 15.70).
  - Si el texto trae centímetros en palabras, consérvalos (ej. 'quince metros, setenta centímetros').
  - Respeta la colindancia literal (ej. 'calle de por medio', 'lote número dieciséis', 'propiedad privada').
  - Ignora guiones decorativos, puntos de relleno y letras índice (a).-, b).-, etc.).
EJEMPLOS VÁLIDOS:
  - "NORESTE: 16.00 dieciséis metros, con lote número once"
  - "ORIENTE: 15.70 quince metros, setenta centímetros, con lote número veinte"
FUENTE: Cláusulas de medidas/planos; valida con Certificado Catastral cuando exista."""
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_2: Optional[str] = Field(
        None,
        description="""OBJETIVO: Capturar el SEGUNDO lado que aparezca en las cláusulas/planos de medidas.
DETECCIÓN: No asumas esquema. Toma literalmente la etiqueta encontrada (p. ej. "SUROESTE", "PONIENTE", "SUR", etc.).
FORMATO DE SALIDA: {DIRECCION}: {DECIMAL_2} {en_palabras} metros{, centímetros si aparecen}, con {colindancia}
REGLAS:
  - Mantén la DIRECCION tal cual aparece (no traduzcas ni normalices a otra rosa de vientos).
  - Normaliza la medida numérica a dos decimales (ej. 07.00, 16.00, 15.70).
  - Si el texto trae centímetros en palabras, consérvalos (ej. 'quince metros, setenta centímetros').
  - Respeta la colindancia literal (ej. 'calle de por medio', 'lote número dieciséis', 'propiedad privada').
  - Ignora guiones decorativos, puntos de relleno y letras índice (a).-, b).-, etc.).
EJEMPLOS VÁLIDOS:
  - "SUROESTE: 16.00 dieciséis metros, con calle"
  - "PONIENTE: 16.00 dieciséis metros, con lote número dieciséis"
FUENTE: Cláusulas de medidas/planos; valida con Certificado Catastral cuando exista."""
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_3: Optional[str] = Field(
        None,
        description="""OBJETIVO: Capturar el TERCER lado que aparezca en las cláusulas/planos de medidas.
DETECCIÓN: No asumas esquema. Toma literalmente la etiqueta encontrada (p. ej. "NOROESTE", "NORTE", etc.).
FORMATO DE SALIDA: {DIRECCION}: {DECIMAL_2} {en_palabras} metros{, centímetros si aparecen}, con {colindancia}
REGLAS:
  - Mantén la DIRECCION tal cual aparece (no traduzcas ni normalices a otra rosa de vientos).
  - Normaliza la medida numérica a dos decimales (ej. 07.00, 16.00, 15.70).
  - Si el texto trae centímetros en palabras, consérvalos (ej. 'quince metros, setenta centímetros').
  - Respeta la colindancia literal (ej. 'calle de por medio', 'lote número dieciséis', 'propiedad privada').
  - Ignora guiones decorativos, puntos de relleno y letras índice (a).-, b).-, etc.).
EJEMPLOS VÁLIDOS:
  - "NOROESTE: 07.00 siete metros, con calle"
  - "NORTE: 07.00 siete metros, con lote número diecisiete"
FUENTE: Cláusulas de medidas/planos; valida con Certificado Catastral cuando exista."""
    )

    Escritura_Privada_Urbano_Clausulas_Medidas_LADO_4: Optional[str] = Field(
        None,
        description="""OBJETIVO: Capturar el CUARTO lado que aparezca en las cláusulas/planos de medidas.
DETECCIÓN: No asumas esquema. Toma literalmente la etiqueta encontrada (p. ej. "SURESTE", "SUR", etc.).
FORMATO DE SALIDA: {DIRECCION}: {DECIMAL_2} {en_palabras} metros{, centímetros si aparecen}, con {colindancia}
REGLAS:
  - Mantén la DIRECCION tal cual aparece (no traduzcas ni normalices a otra rosa de vientos).
  - Normaliza la medida numérica a dos decimales (ej. 07.00, 16.00, 15.70).
  - Si el texto trae centímetros en palabras, consérvalos (ej. 'quince metros, setenta centímetros').
  - Respeta la colindancia literal (ej. 'calle de por medio', 'lote número dieciséis', 'propiedad privada').
  - Ignora guiones decorativos, puntos de relleno y letras índice (a).-, b).-, etc.).
EJEMPLOS VÁLIDOS:
  - "SURESTE: 07.00 siete metros, con propiedad privada"
  - "SUR: 07.00 siete metros, con calle de por medio"
FUENTE: Cláusulas de medidas/planos; valida con Certificado Catastral cuando exista."""
    )

    Certificado_Registro_Catastral: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Superficie con decimales + unidad + en letras MAYÚSCULAS EN PARENTESIS
Ejemplo: 145.00 M2 (CIENTO CUARENTA Y CINCO METROS CUADRADOS)

Extrae la superficie del predio en m².
Fuente: Certificado de Registro Catastral."""
    )

    # Datos personales Vendedor
    Edad_Parte_Vendedora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: numero en letras + palabra "años"
Ejemplo: ochenta años

Calcula edad del VENDEDOR a la fecha del instrumento.
Usar fecha nacimiento (INE/Acta) y fecha del instrumento."""
    )

    Dia_nacimiento_Parte_Vendedora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: trece de agosto de mil novecientos sesenta y cuatro

Extrae fecha de nacimiento del VENDEDOR.
Fuente: Acta o INE.
Convertir números a palabras minúsculas."""
    )

    Origen_Parte_Vendedora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Lugar completo con mayúsculas iniciales
Ejemplo: Pátzcuaro, Michoacán

Extrae lugar de origen del VENDEDOR.
Fuente: Acta o comparecencia."""
    )

    Estado_civil_Parte_Vendedora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Estado civil en minúsculas
Ejemplo: casado

Extrae estado civil del VENDEDOR.
Fuente: actas correspondientes o manifestación en las generales."""
    )

    SAT_situacion_fiscal_Parte_Vendedora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: RFC completo
Ejemplo: CEAR640813JJ8

Extrae RFC del VENDEDOR.
Fuente: Constancia SAT."""
    )

    Comprobante_Domicilio_Parte_Vendedora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Dirección completa en minúsculas
Ejemplo: calle Camelinas número trece de la Colonia Loma Linda en esta Ciudad de Zacapu, Michoacán

Extrae domicilio completo del VENDEDOR.
Fuente: comprobante de domicilio o INE."""
    )

    Identificacion_Parte_Vendedora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Descripción completa en minúsculas
Ejemplo: credencial para votar con fotografía

Extrae tipo de identificación oficial del VENDEDOR."""
    )

    INE_Parte_Vendedora_numero: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Clave completa del INE
Ejemplo: IDMEX2650430777

Extrae la clave/folio de INE del VENDEDOR.
Fuente: INE."""
    )

    CURP_Parte_Vendedora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: CURP completa
Ejemplo: CEAR640813HMNRRL02

Extrae la CURP del VENDEDOR.
Fuente: INE, constancia CURP o Acta."""
    )

    Parte_Vendedora_Ocupacion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Ocupación en minúsculas
Ejemplo: comerciante

Extrae la ocupación o profesión del VENDEDOR.
Fuente: Acta de nacimiento, manifestación en generales o INE."""
    )

    RFC_Parte_Vendedora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: RFC completo
Ejemplo: CEAR640813JJ8

Extrae el RFC del VENDEDOR.
Fuente: Constancia SAT."""
    )

    # Datos personales Comprador
    Edad_Parte_Compradora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: numero en letras + palabra "años"
Ejemplo: treinta y siete años

Calcula edad del COMPRADOR a la fecha del instrumento."""
    )

    Dia_nacimiento_Parte_Compradora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: veinticinco de marzo de mil novecientos setenta y ocho

Extrae fecha de nacimiento del COMPRADOR."""
    )

    Origen_Parte_Compradora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Lugar con mayúsculas iniciales
Ejemplo: Zacapu, Michoacán

Extrae lugar de origen del COMPRADOR."""
    )

    Estado_civil_Parte_Compradora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Estado civil en minúsculas
Ejemplo: divorciado

Extrae estado civil del COMPRADOR."""
    )

    SAT_situacion_fiscal_Parte__Compradora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: RFC completo
Ejemplo: GABM780325EG6

Extrae RFC del COMPRADOR."""
    )

    Comprobante_Domicilio_Parte_Compradora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Dirección completa en minúsculas
Ejemplo: calle Las Rosas número treinta y cuatro de la Colonia Loma Linda en esta Ciudad de Zacapu, Michoacán

Extrae domicilio completo del COMPRADOR."""
    )

    Identificacion_Parte_Compradora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Descripción completa en minúsculas
Ejemplo: credencial para votar con fotografía

Extrae tipo de identificación oficial del COMPRADOR."""
    )

    INE_Parte_Compradora_numero: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Clave completa del INE
Ejemplo: IDMEX2749126814

Extrae la clave/folio de INE del COMPRADOR."""
    )

    CURP_Parte_Compradora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: CURP completa
Ejemplo: GABM780325HMNRRR02

Extrae la CURP del COMPRADOR."""
    )

    Parte_Compradora_Ocupacion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Ocupación en minúsculas
Ejemplo: empleado

Extrae la ocupación o profesión del COMPRADOR.
Fuente: Acta de nacimiento, manifestación en generales o INE."""
    )

    RFC_Parte_Compradora: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: RFC completo
Ejemplo: GABM780325EG6

Extrae el RFC del COMPRADOR."""
    )

    # Documentos oficiales
    Constancia_No_Adeudo_Urbano_Fecha: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: veintisiete de junio de dos mil veinticinco

Extrae fecha de la Constancia de No Adeudo."""
    )

    Certificado_Registro_Catastral_Urbano_Fecha: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: treinta de junio de dos mil veinticinco

Extrae fecha del Certificado Electrónico Catastral."""
    )

    Avaluo_Urbano_Datos_Generales_Fecha: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: tres de julio de dos mil veinticinco

Extrae fecha del Avalúo."""
    )

    Numero_Avaluo: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número completo del avalúo
Ejemplo: 2025-134-387

Extrae el número de Avalúo tal como aparece."""
    )

    Valor_Catastral: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Cantidad con formato de moneda
Ejemplo: $31,920.00

Extrae el Valor Catastral.
Fuente: Avalúo o Certificado Catastral."""
    )

    Valuador: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Nombre completo con título profesional
Ejemplo: ING. JAVIER LIEVANOS HUERTA

Extrae nombre completo del valuador con título profesional."""
    )

    Constancia_No_Adeudo_Numero: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de folio o referencia
Ejemplo: CNA-2025-00456

Extrae el número de folio de la Constancia de No Adeudo.
Fuente: Constancia de No Adeudo emitida por el municipio."""
    )

    # Precio y Operación
    Precio_Operacion_Numero: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Cantidad con formato de moneda
Ejemplo: $350,000.00

Extrae el precio de la operación de compraventa.
Fuente: Contrato, acuerdo entre partes o manifestación."""
    )

    Precio_Operacion_Letras: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Cantidad en palabras MAYÚSCULAS
Ejemplo: TRESCIENTOS CINCUENTA MIL PESOS 00/100 MONEDA NACIONAL

Extrae el precio de la operación en palabras.
Fuente: Contrato o manifestación de las partes."""
    )

    Forma_Pago: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Descripción de la forma de pago en minúsculas
Ejemplo: transferencia bancaria

Extrae la forma de pago acordada.
Opciones comunes: efectivo, transferencia bancaria, cheque certificado, crédito hipotecario."""
    )

    # Superficie adicional
    Predio_Superficie_Metros_Letras: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de metros en palabras minúsculas
Ejemplo: ciento cuarenta y cinco

Extrae los metros cuadrados de superficie en palabras.
Fuente: Certificado Catastral o Avalúo."""
    )

    Predio_Superficie_Centimetros_Letras: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de centímetros en palabras minúsculas
Ejemplo: cincuenta

Extrae los centímetros cuadrados de superficie en palabras (si aplica).
Fuente: Certificado Catastral o Avalúo. Si no hay centímetros, devolver 'cero'."""
    )

    # Cláusulas Especiales
    Clausulas_Especiales: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Texto descriptivo de cláusulas
Ejemplo: El comprador se obliga a respetar servidumbre de paso existente...

Extrae cláusulas especiales acordadas entre las partes.
Fuente: Contrato o manifestación. Si no hay cláusulas especiales, devolver 'ninguna'."""
    )

    # Tratamientos
    Tratamiento_Vendedor: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Tratamiento completo
Ejemplo: el señor

Determinar tratamiento del VENDEDOR basándose en género:
- Si masculino → "el señor"
- Si femenino → "la señora"
- Si no se puede determinar → "la parte vendedora" """
    )

    Tratamiento_Comprador: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Tratamiento completo
Ejemplo: El señor

Determinar tratamiento del COMPRADOR basándose en género:
- Si masculino → "el señor"
- Si femenino → "la señora"
- Si no se puede determinar → "la parte compradora" """
    )

    class Config:
        json_schema_extra = {
            "example": {
                "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
                "Parte_Compradora_Nombre_Completo": "MARCO ANTONIO GARCIA BARBOZA",
                "Escritura_Privada_numero": "cuatrocientos noventa y nueve",
                "Certificado_Registro_Catastral": "145.00 M2 (CIENTO CUARENTA Y CINCO METROS CUADRADOS)",
                "Edad_Parte_Vendedora": "sesenta años",
                "RFC_Parte_Vendedora": "CEAR640813JJ8",
                "RFC_Parte_Compradora": "GABM780325EG6",
                "Tratamiento_Vendedor": "el señor",
                "Tratamiento_Comprador": "el señor"
            }
        }
