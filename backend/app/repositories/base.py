"""
ControlNot v2 - Base Repository
Repositorio base con métodos CRUD genéricos para todas las entidades
"""
from typing import Any, Dict, List, Optional, TypeVar, Generic
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.database import supabase

logger = structlog.get_logger()

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Repositorio base con operaciones CRUD genéricas

    Todos los repositorios específicos heredan de esta clase
    """

    def __init__(self, table_name: str):
        """
        Inicializa el repositorio

        Args:
            table_name: Nombre de la tabla en Supabase
        """
        self.table_name = table_name
        self.client = supabase

    def _table(self):
        """Retorna query builder para la tabla"""
        return self.client.table(self.table_name)

    async def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo registro en la tabla

        Args:
            data: Diccionario con los datos a insertar

        Returns:
            Registro creado o None si falla
        """
        try:
            result = self._table().insert(data).execute()

            if result.data:
                logger.info(
                    f"{self.table_name}_created",
                    table=self.table_name,
                    id=result.data[0].get('id')
                )
                return result.data[0]

            return None

        except APIError as e:
            logger.error(
                f"{self.table_name}_create_failed",
                table=self.table_name,
                error=str(e)
            )
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        """
        Obtiene un registro por ID

        Args:
            id: UUID del registro

        Returns:
            Registro encontrado o None
        """
        try:
            result = self._table()\
                .select('*')\
                .eq('id', str(id))\
                .single()\
                .execute()

            return result.data if result.data else None

        except APIError as e:
            if 'PGRST116' in str(e):  # No rows returned
                return None
            logger.error(
                f"{self.table_name}_get_failed",
                table=self.table_name,
                id=str(id),
                error=str(e)
            )
            raise

    async def update(self, id: UUID, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Actualiza un registro

        Args:
            id: UUID del registro
            updates: Diccionario con los campos a actualizar

        Returns:
            Registro actualizado o None
        """
        try:
            result = self._table()\
                .update(updates)\
                .eq('id', str(id))\
                .execute()

            if result.data:
                logger.info(
                    f"{self.table_name}_updated",
                    table=self.table_name,
                    id=str(id)
                )
                return result.data[0]

            return None

        except APIError as e:
            logger.error(
                f"{self.table_name}_update_failed",
                table=self.table_name,
                id=str(id),
                error=str(e)
            )
            raise

    async def delete(self, id: UUID) -> bool:
        """
        Elimina un registro

        Args:
            id: UUID del registro

        Returns:
            True si se eliminó, False si no existía
        """
        try:
            result = self._table()\
                .delete()\
                .eq('id', str(id))\
                .execute()

            deleted = len(result.data) > 0 if result.data else False

            if deleted:
                logger.info(
                    f"{self.table_name}_deleted",
                    table=self.table_name,
                    id=str(id)
                )

            return deleted

        except APIError as e:
            logger.error(
                f"{self.table_name}_delete_failed",
                table=self.table_name,
                id=str(id),
                error=str(e)
            )
            raise

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0,
        order_by: str = 'created_at',
        descending: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Lista registros de un tenant con filtros opcionales

        Args:
            tenant_id: UUID del tenant
            filters: Filtros adicionales {campo: valor}
            limit: Número máximo de resultados
            offset: Offset para paginación
            order_by: Campo para ordenar
            descending: Ordenar descendente

        Returns:
            Lista de registros
        """
        try:
            query = self._table()\
                .select('*')\
                .eq('tenant_id', str(tenant_id))

            # Aplicar filtros adicionales
            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)

            # Ordenar
            query = query.order(order_by, desc=descending)

            # Paginación
            query = query.range(offset, offset + limit - 1)

            result = query.execute()

            return result.data if result.data else []

        except APIError as e:
            logger.error(
                f"{self.table_name}_list_failed",
                table=self.table_name,
                tenant_id=str(tenant_id),
                error=str(e)
            )
            raise

    async def count_by_tenant(
        self,
        tenant_id: UUID,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Cuenta registros de un tenant

        Args:
            tenant_id: UUID del tenant
            filters: Filtros opcionales

        Returns:
            Número de registros
        """
        try:
            query = self._table()\
                .select('id', count='exact')\
                .eq('tenant_id', str(tenant_id))

            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)

            result = query.execute()

            return result.count if result.count is not None else 0

        except APIError as e:
            logger.error(
                f"{self.table_name}_count_failed",
                table=self.table_name,
                tenant_id=str(tenant_id),
                error=str(e)
            )
            raise
