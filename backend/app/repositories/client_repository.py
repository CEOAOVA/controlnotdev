"""
ControlNot v2 - Client Repository
Repositorio para gestión de clientes (personas físicas y morales)
"""
from typing import Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class ClientRepository(BaseRepository):
    """
    Repositorio para la tabla 'clients'

    Gestiona clientes de la notaría (personas físicas o morales)
    """

    def __init__(self):
        super().__init__('clients')

    async def create_client(
        self,
        tenant_id: UUID,
        tipo_persona: str,
        nombre_completo: str,
        rfc: Optional[str] = None,
        curp: Optional[str] = None,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        direccion: Optional[str] = None,
        ciudad: Optional[str] = None,
        estado: Optional[str] = None,
        codigo_postal: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Crea un nuevo cliente

        Args:
            tenant_id: UUID de la notaría
            tipo_persona: 'fisica' o 'moral'
            nombre_completo: Nombre completo del cliente
            rfc: RFC del cliente (opcional pero recomendado)
            curp: CURP (solo para personas físicas)
            email: Email del cliente
            telefono: Teléfono del cliente
            direccion: Dirección completa
            ciudad: Ciudad
            estado: Estado
            codigo_postal: Código postal
            metadata: Metadata adicional (JSONB)

        Returns:
            Cliente creado
        """
        client_data = {
            'tenant_id': str(tenant_id),
            'tipo_persona': tipo_persona,
            'nombre_completo': nombre_completo.upper(),  # Normalizar a mayúsculas
            'activo': True
        }

        # Agregar campos opcionales solo si tienen valor
        if rfc:
            client_data['rfc'] = rfc.upper()
        if curp:
            client_data['curp'] = curp.upper()
        if email:
            client_data['email'] = email.lower()
        if telefono:
            client_data['telefono'] = telefono
        if direccion:
            client_data['direccion'] = direccion
        if ciudad:
            client_data['ciudad'] = ciudad
        if estado:
            client_data['estado'] = estado
        if codigo_postal:
            client_data['codigo_postal'] = codigo_postal
        if metadata:
            client_data['metadata'] = metadata

        try:
            return await self.create(client_data)

        except APIError as e:
            # Manejar violación de constraint único (RFC duplicado)
            if 'unique_client_rfc_per_tenant' in str(e):
                logger.warning(
                    "client_rfc_duplicate",
                    tenant_id=str(tenant_id),
                    rfc=rfc
                )
                raise ValueError(f"Ya existe un cliente con el RFC {rfc} en esta notaría")
            raise

    async def get_by_rfc(
        self,
        tenant_id: UUID,
        rfc: str
    ) -> Optional[Dict]:
        """
        Obtiene un cliente por su RFC

        Args:
            tenant_id: UUID de la notaría
            rfc: RFC a buscar

        Returns:
            Cliente encontrado o None
        """
        try:
            result = self._table()\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .eq('rfc', rfc.upper())\
                .single()\
                .execute()

            return result.data if result.data else None

        except APIError as e:
            if 'PGRST116' in str(e):  # No rows
                return None
            logger.error("client_get_by_rfc_failed", rfc=rfc, error=str(e))
            raise

    async def search_by_name(
        self,
        tenant_id: UUID,
        nombre: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Busca clientes por nombre (búsqueda por texto completo)

        Args:
            tenant_id: UUID de la notaría
            nombre: Texto a buscar en el nombre
            limit: Número máximo de resultados

        Returns:
            Lista de clientes que coinciden
        """
        try:
            # Búsqueda case-insensitive con ILIKE
            result = self._table()\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .ilike('nombre_completo', f'%{nombre}%')\
                .eq('activo', True)\
                .limit(limit)\
                .execute()

            return result.data if result.data else []

        except APIError as e:
            logger.error("client_search_failed", nombre=nombre, error=str(e))
            raise

    async def list_active_clients(
        self,
        tenant_id: UUID,
        tipo_persona: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Lista clientes activos de una notaría

        Args:
            tenant_id: UUID de la notaría
            tipo_persona: Filtrar por 'fisica' o 'moral' (opcional)
            limit: Número máximo de resultados
            offset: Offset para paginación

        Returns:
            Lista de clientes activos
        """
        filters = {'activo': True}

        if tipo_persona:
            filters['tipo_persona'] = tipo_persona

        return await self.list_by_tenant(
            tenant_id=tenant_id,
            filters=filters,
            limit=limit,
            offset=offset,
            order_by='created_at',
            descending=True
        )

    async def update_client(
        self,
        client_id: UUID,
        updates: Dict
    ) -> Optional[Dict]:
        """
        Actualiza datos de un cliente

        Args:
            client_id: UUID del cliente
            updates: Diccionario con campos a actualizar

        Returns:
            Cliente actualizado
        """
        # Normalizar campos si están presentes
        if 'nombre_completo' in updates:
            updates['nombre_completo'] = updates['nombre_completo'].upper()
        if 'rfc' in updates:
            updates['rfc'] = updates['rfc'].upper()
        if 'curp' in updates:
            updates['curp'] = updates['curp'].upper()
        if 'email' in updates:
            updates['email'] = updates['email'].lower()

        return await self.update(client_id, updates)

    async def deactivate_client(
        self,
        client_id: UUID
    ) -> Optional[Dict]:
        """
        Desactiva un cliente (soft delete)

        Args:
            client_id: UUID del cliente

        Returns:
            Cliente desactivado
        """
        return await self.update(client_id, {'activo': False})

    async def count_clients(
        self,
        tenant_id: UUID,
        tipo_persona: Optional[str] = None
    ) -> int:
        """
        Cuenta clientes activos de una notaría

        Args:
            tenant_id: UUID de la notaría
            tipo_persona: Filtrar por tipo (opcional)

        Returns:
            Número de clientes
        """
        filters = {'activo': True}

        if tipo_persona:
            filters['tipo_persona'] = tipo_persona

        return await self.count_by_tenant(tenant_id, filters)


# Instancia singleton del repositorio
client_repository = ClientRepository()
