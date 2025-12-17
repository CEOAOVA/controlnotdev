"""
ControlNot v2 - Redis Cache Client
Gestión del cliente Redis singleton con conexión pool

IMPORTANTE: Este módulo es NON-BLOCKING. Si Redis no está disponible,
las funciones retornan None/False/default en vez de lanzar excepciones.
El sistema funciona sin caché si Redis falla.

Uso:
    >>> from app.core.cache import get_redis_client, is_redis_available
    >>> if is_redis_available():
    ...     redis = get_redis_client()
    ...     redis.set("key", "value", ex=300)
"""
import redis
from redis.connection import ConnectionPool
from typing import Optional
import structlog

logger = structlog.get_logger()

# Global Redis client instance (singleton)
_redis_client: Optional[redis.Redis] = None
_connection_pool: Optional[ConnectionPool] = None
_redis_available: Optional[bool] = None  # Cache del estado de disponibilidad


def get_redis_client() -> Optional[redis.Redis]:
    """
    Obtiene instancia singleton del cliente Redis de forma NON-BLOCKING.

    IMPORTANTE: Esta función NUNCA lanza excepciones. Si Redis no está
    disponible, retorna None y el sistema funciona sin caché.

    Returns:
        Optional[redis.Redis]: Cliente Redis o None si no disponible

    Example:
        >>> redis = get_redis_client()
        >>> if redis:
        ...     redis.set("test", "value")
    """
    global _redis_client, _connection_pool, _redis_available

    # Si ya sabemos que Redis no está disponible, retornar None rápido
    if _redis_available is False:
        return None

    if _redis_client is None:
        try:
            # Importar settings aquí para evitar import circular
            from app.core.config import settings

            # Crear connection pool con timeout corto (2s) para no bloquear startup
            _connection_pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,
                socket_keepalive=True,
                socket_connect_timeout=2,  # Timeout CORTO: 2 segundos
                socket_timeout=2,  # Timeout CORTO para operaciones
                retry_on_timeout=False  # NO reintentar - falla rápido
            )

            # Crear cliente Redis con pool
            _redis_client = redis.Redis(connection_pool=_connection_pool)

            # Verificar conexión (timeout de 2s)
            _redis_client.ping()

            _redis_available = True
            logger.info(
                "redis_client_initialized",
                url=settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                ttl_default=settings.REDIS_TTL
            )

        except Exception as e:
            # NO lanzar excepción - marcar como no disponible y continuar
            logger.warning(
                "redis_not_available_cache_disabled",
                error=str(e),
                message="Sistema funcionará sin caché Redis"
            )
            _redis_available = False
            _redis_client = None
            _connection_pool = None
            return None

    return _redis_client


def close_redis_client():
    """
    Cierra el cliente Redis y libera recursos

    Debe llamarse al cerrar la aplicación (shutdown event).
    Cierra todas las conexiones del pool.

    Example:
        >>> # En FastAPI lifespan
        >>> @asynccontextmanager
        >>> async def lifespan(app: FastAPI):
        ...     yield
        ...     close_redis_client()
    """
    global _redis_client, _connection_pool

    if _redis_client:
        try:
            _redis_client.close()
            logger.info("Redis client cerrado")
        except Exception as e:
            logger.error("Error al cerrar Redis client", error=str(e))

    if _connection_pool:
        try:
            _connection_pool.disconnect()
            logger.info("Redis connection pool desconectado")
        except Exception as e:
            logger.error("Error al desconectar Redis pool", error=str(e))

    _redis_client = None
    _connection_pool = None


def is_redis_available() -> bool:
    """
    Verifica si Redis está disponible de forma NON-BLOCKING.

    Returns:
        bool: True si Redis está disponible, False en caso contrario

    Example:
        >>> if is_redis_available():
        ...     # usar cache
        ... else:
        ...     # skip cache (sistema funciona sin Redis)
    """
    client = get_redis_client()
    return client is not None


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_cached(key: str, default=None) -> Optional[str]:
    """
    Obtiene valor del cache de forma segura (NON-BLOCKING)

    Args:
        key: Clave del cache
        default: Valor por defecto si no existe, error, o Redis no disponible

    Returns:
        Optional[str]: Valor del cache o default
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return default

    try:
        value = redis_client.get(key)
        if value:
            logger.debug("cache_hit", key=key)
            return value
        else:
            logger.debug("cache_miss", key=key)
            return default
    except Exception as e:
        logger.warning("cache_read_error", key=key, error=str(e))
        return default


def set_cached(
    key: str,
    value: str,
    ttl: Optional[int] = None
) -> bool:
    """
    Guarda valor en cache de forma segura (NON-BLOCKING)

    Args:
        key: Clave del cache
        value: Valor a guardar (string o JSON)
        ttl: Time-to-live en segundos (usa 300 por defecto)

    Returns:
        bool: True si guardó exitosamente, False si Redis no disponible o error
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return False

    try:
        from app.core.config import settings
        ttl_seconds = ttl if ttl is not None else settings.REDIS_TTL
        redis_client.setex(key, ttl_seconds, value)
        logger.debug("cache_set", key=key, ttl=ttl_seconds, value_length=len(value))
        return True
    except Exception as e:
        logger.warning("cache_write_error", key=key, error=str(e))
        return False


def delete_cached(key: str) -> bool:
    """
    Elimina valor del cache (NON-BLOCKING)

    Args:
        key: Clave a eliminar

    Returns:
        bool: True si eliminó, False si Redis no disponible o error
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return False

    try:
        result = redis_client.delete(key)
        logger.debug("cache_delete", key=key, deleted=bool(result))
        return bool(result)
    except Exception as e:
        logger.warning("cache_delete_error", key=key, error=str(e))
        return False


def clear_all_cache() -> bool:
    """
    Limpia TODO el cache (usar con precaución)

    Returns:
        bool: True si limpió, False si Redis no disponible o error
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return False

    try:
        redis_client.flushdb()
        logger.warning("cache_flushed_all")
        return True
    except Exception as e:
        logger.error("cache_flush_error", error=str(e))
        return False


def get_cache_stats() -> dict:
    """
    Obtiene estadísticas del cache Redis (NON-BLOCKING)

    Returns:
        dict: Estadísticas de Redis o estado desconectado
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return {"connected": False, "error": "Redis not available"}

    try:
        info = redis_client.info()
        stats = {
            "connected": True,
            "keys": redis_client.dbsize(),
            "used_memory_human": info.get('used_memory_human', 'N/A'),
            "used_memory_bytes": info.get('used_memory', 0),
            "hits": info.get('keyspace_hits', 0),
            "misses": info.get('keyspace_misses', 0),
            "hit_rate": (
                info.get('keyspace_hits', 0) /
                max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)
                * 100
            ),
            "evicted_keys": info.get('evicted_keys', 0),
            "expired_keys": info.get('expired_keys', 0)
        }
        logger.info("cache_stats", **stats)
        return stats
    except Exception as e:
        logger.error("cache_stats_error", error=str(e))
        return {"connected": False, "error": str(e)}


# Example usage
if __name__ == "__main__":
    import json

    # Test conexión
    print("🔌 Conectando a Redis...")
    if is_redis_available():
        print("✅ Redis disponible\n")

        # Test SET/GET
        print("📝 Test SET/GET:")
        test_data = {"name": "Juan Pérez", "rfc": "PEPJ860101AAA"}
        set_cached("test:user", json.dumps(test_data), ttl=60)
        cached = get_cached("test:user")
        if cached:
            print(f"   Cached: {json.loads(cached)}")

        # Test stats
        print("\n📊 Estadísticas:")
        stats = get_cache_stats()
        print(f"   Keys: {stats['keys']}")
        print(f"   Memoria: {stats['used_memory_human']}")
        print(f"   Hit rate: {stats['hit_rate']:.1f}%")

    else:
        print("❌ Redis no disponible")
        print("   Asegúrate de tener Redis ejecutándose:")
        print("   - Local: docker run -d -p 6379:6379 redis:7-alpine")
        print("   - Cloud: https://redis.com/try-free/")
