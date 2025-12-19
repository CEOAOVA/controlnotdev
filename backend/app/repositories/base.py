"""
ControlNot v2 - Base Repository
Repositorio base con métodos CRUD genéricos para todas las entidades
"""
import time
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
        start_time = time.time()
        logger.debug(
            "db_create_starting",
            table=self.table_name,
            data_keys=list(data.keys())
        )

        try:
            result = self._table().insert(data).execute()
            duration_ms = (time.time() - start_time) * 1000

            if result.data:
                logger.info(
                    "db_create_complete",
                    table=self.table_name,
                    id=result.data[0].get('id'),
                    duration_ms=round(duration_ms, 2)
                )
                return result.data[0]

            logger.warning(
                "db_create_no_result",
                table=self.table_name,
                duration_ms=round(duration_ms, 2)
            )
            return None

        except APIError as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "db_create_failed",
                table=self.table_name,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
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
        start_time = time.time()
        logger.debug(
            "db_get_by_id_starting",
            table=self.table_name,
            id=str(id)
        )

        try:
            result = self._table()\
                .select('*')\
                .eq('id', str(id))\
                .single()\
                .execute()

            duration_ms = (time.time() - start_time) * 1000
            found = result.data is not None

            logger.debug(
                "db_get_by_id_complete",
                table=self.table_name,
                id=str(id),
                found=found,
                duration_ms=round(duration_ms, 2)
            )

            return result.data if result.data else None

        except APIError as e:
            duration_ms = (time.time() - start_time) * 1000
            if 'PGRST116' in str(e):  # No rows returned
                logger.debug(
                    "db_get_by_id_not_found",
                    table=self.table_name,
                    id=str(id),
                    duration_ms=round(duration_ms, 2)
                )
                return None
            logger.error(
                "db_get_by_id_failed",
                table=self.table_name,
                id=str(id),
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
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
        start_time = time.time()
        logger.debug(
            "db_update_starting",
            table=self.table_name,
            id=str(id),
            update_fields=list(updates.keys())
        )

        try:
            result = self._table()\
                .update(updates)\
                .eq('id', str(id))\
                .execute()

            duration_ms = (time.time() - start_time) * 1000

            if result.data:
                logger.info(
                    "db_update_complete",
                    table=self.table_name,
                    id=str(id),
                    fields_updated=len(updates),
                    duration_ms=round(duration_ms, 2)
                )
                return result.data[0]

            logger.warning(
                "db_update_no_result",
                table=self.table_name,
                id=str(id),
                duration_ms=round(duration_ms, 2)
            )
            return None

        except APIError as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "db_update_failed",
                table=self.table_name,
                id=str(id),
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
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
        start_time = time.time()
        logger.debug(
            "db_delete_starting",
            table=self.table_name,
            id=str(id)
        )

        try:
            result = self._table()\
                .delete()\
                .eq('id', str(id))\
                .execute()

            duration_ms = (time.time() - start_time) * 1000
            deleted = len(result.data) > 0 if result.data else False

            if deleted:
                logger.info(
                    "db_delete_complete",
                    table=self.table_name,
                    id=str(id),
                    duration_ms=round(duration_ms, 2)
                )
            else:
                logger.debug(
                    "db_delete_not_found",
                    table=self.table_name,
                    id=str(id),
                    duration_ms=round(duration_ms, 2)
                )

            return deleted

        except APIError as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "db_delete_failed",
                table=self.table_name,
                id=str(id),
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
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
        start_time = time.time()
        logger.debug(
            "db_list_by_tenant_starting",
            table=self.table_name,
            tenant_id=str(tenant_id),
            filters=filters,
            limit=limit,
            offset=offset
        )

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
            duration_ms = (time.time() - start_time) * 1000
            count = len(result.data) if result.data else 0

            logger.debug(
                "db_list_by_tenant_complete",
                table=self.table_name,
                tenant_id=str(tenant_id),
                results_count=count,
                duration_ms=round(duration_ms, 2)
            )

            return result.data if result.data else []

        except APIError as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "db_list_by_tenant_failed",
                table=self.table_name,
                tenant_id=str(tenant_id),
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
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
        start_time = time.time()
        logger.debug(
            "db_count_by_tenant_starting",
            table=self.table_name,
            tenant_id=str(tenant_id),
            filters=filters
        )

        try:
            query = self._table()\
                .select('id', count='exact')\
                .eq('tenant_id', str(tenant_id))

            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)

            result = query.execute()
            duration_ms = (time.time() - start_time) * 1000
            count = result.count if result.count is not None else 0

            logger.debug(
                "db_count_by_tenant_complete",
                table=self.table_name,
                tenant_id=str(tenant_id),
                count=count,
                duration_ms=round(duration_ms, 2)
            )

            return count

        except APIError as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "db_count_by_tenant_failed",
                table=self.table_name,
                tenant_id=str(tenant_id),
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
            )
            raise
