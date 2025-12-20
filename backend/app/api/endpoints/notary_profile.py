"""
ControlNot v2 - Notary Profile Endpoints
Endpoints para gestionar el perfil de la notaría

Rutas:
- GET    /api/notary-profile      - Obtener perfil de la notaría
- PUT    /api/notary-profile      - Actualizar perfil de la notaría
- POST   /api/notary-profile/increment-instrument - Incrementar número de instrumento
"""
from fastapi import APIRouter, Depends, HTTPException
import structlog

from app.schemas.notary_profile_schemas import (
    NotaryProfileResponse,
    NotaryProfileUpdate,
    IncrementInstrumentResponse
)
from app.database import get_current_tenant_id, supabase_admin

logger = structlog.get_logger()
router = APIRouter(prefix="/notary-profile", tags=["Notary Profile"])


def numero_a_palabras(num: int) -> str:
    """Convierte número a palabras en español (hasta 999)"""
    if num is None or num < 0 or num > 999:
        return ""

    unidades = ['', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve']
    decenas = ['', 'diez', 'veinte', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa']
    especiales = ['diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciséis', 'diecisiete', 'dieciocho', 'diecinueve']
    veintis = ['veinte', 'veintiuno', 'veintidós', 'veintitrés', 'veinticuatro', 'veinticinco', 'veintiséis', 'veintisiete', 'veintiocho', 'veintinueve']
    centenas = ['', 'ciento', 'doscientos', 'trescientos', 'cuatrocientos', 'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos']

    if num == 0:
        return 'cero'
    if num == 100:
        return 'cien'

    resultado = ''
    c = num // 100
    d = (num % 100) // 10
    u = num % 10

    if c > 0:
        resultado = centenas[c]

    if d == 1:
        if resultado:
            resultado += ' '
        resultado += especiales[u]
    elif d == 2:
        if resultado:
            resultado += ' '
        resultado += veintis[u]
    elif d > 2:
        if resultado:
            resultado += ' '
        resultado += decenas[d]
        if u > 0:
            resultado += ' y ' + unidades[u]
    elif u > 0:
        if resultado:
            resultado += ' '
        resultado += unidades[u]

    return resultado


@router.get("", response_model=NotaryProfileResponse)
async def get_notary_profile(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Obtiene el perfil de la notaría actual

    Retorna todos los datos de la notaría incluyendo:
    - Datos de identificación (nombre, RFC, número)
    - Datos del notario titular
    - Ubicación
    - Control de numeración de instrumentos
    """
    logger.info("Obteniendo perfil de notaría", tenant_id=tenant_id)

    try:
        result = supabase_admin.table('tenants').select('*').eq('id', tenant_id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Notaría no encontrada")

        tenant = result.data

        # Construir respuesta con campos calculados
        notario_completo = None
        if tenant.get('notario_nombre'):
            titulo = tenant.get('notario_titulo', 'Licenciado')
            notario_completo = f"{titulo} {tenant['notario_nombre']}"

        lugar_instrumento = None
        if tenant.get('ciudad') and tenant.get('estado'):
            lugar_instrumento = f"{tenant['ciudad']}, {tenant['estado']}"

        return NotaryProfileResponse(
            nombre=tenant['nombre'],
            rfc=tenant['rfc'],
            numero_notaria=tenant.get('numero_notaria'),
            numero_notaria_palabras=tenant.get('numero_notaria_palabras'),
            estado=tenant['estado'],
            ciudad=tenant.get('ciudad'),
            direccion=tenant.get('direccion'),
            notario_nombre=tenant.get('notario_nombre'),
            notario_titulo=tenant.get('notario_titulo', 'Licenciado'),
            ultimo_numero_instrumento=tenant.get('ultimo_numero_instrumento', 0),
            notario_completo=notario_completo,
            lugar_instrumento=lugar_instrumento
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error al obtener perfil de notaría", error=str(e), tenant_id=tenant_id)
        raise HTTPException(status_code=500, detail=f"Error al obtener perfil: {str(e)}")


@router.put("", response_model=NotaryProfileResponse)
async def update_notary_profile(
    update_data: NotaryProfileUpdate,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Actualiza el perfil de la notaría

    Campos actualizables:
    - notario_nombre: Nombre del notario titular
    - notario_titulo: Título (Licenciado, Doctor, etc.)
    - numero_notaria: Número de la notaría
    - numero_notaria_palabras: Número en palabras
    - ciudad, estado: Ubicación
    - direccion: Dirección completa
    """
    logger.info("Actualizando perfil de notaría", tenant_id=tenant_id)

    try:
        # Construir diccionario de actualización (solo campos no nulos)
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        if not update_dict:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")

        # Auto-generar numero_notaria_palabras si se actualiza numero_notaria
        if 'numero_notaria' in update_dict and 'numero_notaria_palabras' not in update_dict:
            update_dict['numero_notaria_palabras'] = numero_a_palabras(update_dict['numero_notaria'])

        # Agregar timestamp de actualización
        from datetime import datetime
        update_dict['updated_at'] = datetime.utcnow().isoformat()

        result = supabase_admin.table('tenants').update(update_dict).eq('id', tenant_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Notaría no encontrada")

        logger.info("Perfil de notaría actualizado", tenant_id=tenant_id, campos=list(update_dict.keys()))

        # Retornar perfil actualizado
        return await get_notary_profile(tenant_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error al actualizar perfil de notaría", error=str(e), tenant_id=tenant_id)
        raise HTTPException(status_code=500, detail=f"Error al actualizar perfil: {str(e)}")


@router.post("/increment-instrument", response_model=IncrementInstrumentResponse)
async def increment_instrument_number(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Incrementa el número de instrumento y retorna el nuevo valor

    Útil para obtener el siguiente número de escritura al generar un documento.
    El número se incrementa atómicamente para evitar duplicados.
    """
    logger.info("Incrementando número de instrumento", tenant_id=tenant_id)

    try:
        # Obtener número actual
        result = supabase_admin.table('tenants').select('ultimo_numero_instrumento').eq('id', tenant_id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Notaría no encontrada")

        current_num = result.data.get('ultimo_numero_instrumento', 0) or 0
        new_num = current_num + 1

        # Actualizar
        from datetime import datetime
        supabase_admin.table('tenants').update({
            'ultimo_numero_instrumento': new_num,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', tenant_id).execute()

        logger.info("Número de instrumento incrementado",
                   tenant_id=tenant_id,
                   anterior=current_num,
                   nuevo=new_num)

        return IncrementInstrumentResponse(
            nuevo_numero=new_num,
            numero_palabras=numero_a_palabras(new_num)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error al incrementar número de instrumento", error=str(e), tenant_id=tenant_id)
        raise HTTPException(status_code=500, detail=f"Error al incrementar número: {str(e)}")
