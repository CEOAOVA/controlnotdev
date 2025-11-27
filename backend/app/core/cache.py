"""
ControlNot v2 - Redis Cache Client
Gestión del cliente Redis singleton con conexión pool

SEMANA 1 - QUICK WINS:
- Cliente Redis singleton con connection pool
- Soporte para Redis Cloud (free tier) o local
- Manejo automático de reconexión
- Logging detallado de operaciones

Uso:
    >>> from app.core.cache import get_redis_client
    >>> redis = get_redis_client()
    >>> redis.set("key", "value", ex=300)
    >>> value = redis.get("key")
"""
import redis
from redis.connection import ConnectionPool
from typing import Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Global Redis client instance (singleton)
_redis_client: Optional[redis.Redis] = None
_connection_pool: Optional[ConnectionPool] = None


def get_redis_client() -> redis.Redis:
    """
    Obtiene instancia singleton del cliente Redis

    Usa connection pool para reutilizar conexiones y mejorar performance.
    Se reconecta automáticamente si la conexión se pierde.

    Returns:
        redis.Redis: Cliente Redis configurado

    Example:
        >>> redis = get_redis_client()
        >>> redis.ping()  # True
        >>> redis.set("test", "value")
        >>> redis.get("test")  # b'value'

    Raises:
        redis.ConnectionError: Si no puede conectar a Redis
    """
    global _redis_client, _connection_pool

    if _redis_client is None:
        try:
            # Crear connection pool (más eficiente que conexiones individuales)
            _connection_pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,  # Auto-decodificar bytes a strings
                socket_keepalive=True,  # Mantener conexiones vivas
                socket_connect_timeout=5,  # 5 segundos timeout
                retry_on_timeout=True  # Reintentar si timeout
            )

            # Crear cliente Redis con pool
            _redis_client = redis.Redis(connection_pool=_connection_pool)

            # Verificar conexión
            _redis_client.ping()

            logger.info(
                "✅ Redis client inicializado",
                url=settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                ttl_default=settings.REDIS_TTL
            )

        except redis.ConnectionError as e:
            logger.error(
                "❌ Error al conectar a Redis",
                error=str(e),
                url=settings.REDIS_URL
            )
            raise

        except Exception as e:
            logger.error(
                "❌ Error inesperado al inicializar Redis",
                error=str(e),
                error_type=type(e).__name__
            )
            raise

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
    Verifica si Redis está disponible y responde

    Returns:
        bool: True si Redis responde a PING, False en caso contrario

    Example:
        >>> if is_redis_available():
        ...     # usar cache
        ... else:
        ...     # skip cache
    """
    try:
        redis_client = get_redis_client()
        return redis_client.ping()
    except Exception as e:
        logger.warning("Redis no disponible", error=str(e))
        return False


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_cached(key: str, default=None) -> Optional[str]:
    """
    Obtiene valor del cache de forma segura

    Args:
        key: Clave del cache
        default: Valor por defecto si no existe o error

    Returns:
        Optional[str]: Valor del cache o default

    Example:
        >>> value = get_cached("ocr:abc123")
        >>> if value:
        ...     data = json.loads(value)
    """
    try:
        redis_client = get_redis_client()
        value = redis_client.get(key)

        if value:
            logger.debug("Cache HIT", key=key)
            return value
        else:
            logger.debug("Cache MISS", key=key)
            return default

    except Exception as e:
        logger.warning(
            "Error al leer cache, usando default",
            key=key,
            error=str(e)
        )
        return default


def set_cached(
    key: str,
    value: str,
    ttl: Optional[int] = None
) -> bool:
    """
    Guarda valor en cache de forma segura

    Args:
        key: Clave del cache
        value: Valor a guardar (string o JSON)
        ttl: Time-to-live en segundos (usa settings.REDIS_TTL por defecto)

    Returns:
        bool: True si guardó exitosamente, False en caso contrario

    Example:
        >>> import json
        >>> data = {"field": "value"}
        >>> set_cached("key", json.dumps(data), ttl=300)
    """
    try:
        redis_client = get_redis_client()
        ttl_seconds = ttl if ttl is not None else settings.REDIS_TTL

        redis_client.setex(key, ttl_seconds, value)

        logger.debug(
            "Cache SET",
            key=key,
            ttl=ttl_seconds,
            value_length=len(value)
        )

        return True

    except Exception as e:
        logger.warning(
            "Error al escribir cache",
            key=key,
            error=str(e)
        )
        return False


def delete_cached(key: str) -> bool:
    """
    Elimina valor del cache

    Args:
        key: Clave a eliminar

    Returns:
        bool: True si eliminó, False en caso contrario

    Example:
        >>> delete_cached("ocr:abc123")
    """
    try:
        redis_client = get_redis_client()
        result = redis_client.delete(key)

        logger.debug("Cache DELETE", key=key, deleted=bool(result))

        return bool(result)

    except Exception as e:
        logger.warning(
            "Error al eliminar cache",
            key=key,
            error=str(e)
        )
        return False


def clear_all_cache() -> bool:
    """
    Limpia TODO el cache (usar con precaución)

    Returns:
        bool: True si limpió, False en caso contrario

    Example:
        >>> clear_all_cache()  # ⚠️ ELIMINA TODO
    """
    try:
        redis_client = get_redis_client()
        redis_client.flushdb()

        logger.warning("⚠️ Cache completamente limpiado (FLUSHDB)")

        return True

    except Exception as e:
        logger.error(
            "Error al limpiar cache",
            error=str(e)
        )
        return False


def get_cache_stats() -> dict:
    """
    Obtiene estadísticas del cache Redis

    Returns:
        dict: Estadísticas de Redis (keys, memory, hits, etc.)

    Example:
        >>> stats = get_cache_stats()
        >>> print(f"Keys en cache: {stats['keys']}")
        >>> print(f"Memoria usada: {stats['used_memory_human']}")
    """
    try:
        redis_client = get_redis_client()
        info = redis_client.info()

        # Extraer métricas importantes
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

        logger.info(
            "📊 Cache stats",
            **stats
        )

        return stats

    except Exception as e:
        logger.error("Error al obtener stats de cache", error=str(e))
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
