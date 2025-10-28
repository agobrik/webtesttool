"""
Advanced caching system with multiple backends
"""

import json
import hashlib
from typing import Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger


class CacheBackend(ABC):
    """Base class for cache backends"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        pass

    @abstractmethod
    async def delete(self, key: str):
        """Delete key from cache"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass

    @abstractmethod
    async def clear(self):
        """Clear all cache"""
        pass


class MemoryCacheBackend(CacheBackend):
    """
    In-memory cache backend (simple dictionary)

    Example:
        cache = MemoryCacheBackend()
        await cache.set("key", "value", ttl=300)
        value = await cache.get("key")
    """

    def __init__(self):
        self.cache = {}
        self.expiry = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None

        # Check expiry
        if key in self.expiry and datetime.now() > self.expiry[key]:
            await self.delete(key)
            return None

        return self.cache[key]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        self.cache[key] = value

        if ttl:
            self.expiry[key] = datetime.now() + timedelta(seconds=ttl)

    async def delete(self, key: str):
        """Delete key from cache"""
        self.cache.pop(key, None)
        self.expiry.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.get(key) is not None

    async def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.expiry.clear()


class FileCacheBackend(CacheBackend):
    """
    File-based cache backend

    Example:
        cache = FileCacheBackend(cache_dir=".cache")
        await cache.set("key", {"data": "value"}, ttl=300)
    """

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_file = self._get_cache_file(key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)

            # Check expiry
            if 'expiry' in data:
                expiry = datetime.fromisoformat(data['expiry'])
                if datetime.now() > expiry:
                    await self.delete(key)
                    return None

            return data['value']
        except Exception as e:
            logger.error(f"Failed to read cache: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        cache_file = self._get_cache_file(key)

        data = {'value': value}

        if ttl:
            expiry = datetime.now() + timedelta(seconds=ttl)
            data['expiry'] = expiry.isoformat()

        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to write cache: {e}")

    async def delete(self, key: str):
        """Delete key from cache"""
        cache_file = self._get_cache_file(key)
        cache_file.unlink(missing_ok=True)

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.get(key) is not None

    async def clear(self):
        """Clear all cache"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()


class RedisCacheBackend(CacheBackend):
    """
    Redis cache backend (requires redis-py)

    Example:
        cache = RedisCacheBackend(host="localhost", port=6379)
        await cache.set("key", "value", ttl=300)
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        try:
            import redis.asyncio as redis
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        except ImportError:
            raise ImportError("redis package required for RedisCacheBackend")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        try:
            value_str = json.dumps(value)
            if ttl:
                await self.redis.setex(key, ttl, value_str)
            else:
                await self.redis.set(key, value_str)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def delete(self, key: str):
        """Delete key from cache"""
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    async def clear(self):
        """Clear all cache"""
        try:
            await self.redis.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")


class CacheManager:
    """
    High-level cache manager

    Example:
        manager = CacheManager(backend=RedisCacheBackend())

        @manager.cached(ttl=300)
        async def expensive_operation(param):
            # ... expensive computation
            return result
    """

    def __init__(self, backend: Optional[CacheBackend] = None):
        self.backend = backend or MemoryCacheBackend()

    async def get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        return await self.backend.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set in cache"""
        await self.backend.set(key, value, ttl)

    async def delete(self, key: str):
        """Delete from cache"""
        await self.backend.delete(key)

    async def clear(self):
        """Clear cache"""
        await self.backend.clear()

    def cached(self, ttl: Optional[int] = None, key_prefix: str = ""):
        """
        Decorator to cache function results

        Example:
            @cache_manager.cached(ttl=300)
            async def get_data(url):
                return await fetch(url)
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}{func.__name__}:{args}:{kwargs}"

                # Try to get from cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value

                # Execute function
                result = await func(*args, **kwargs)

                # Store in cache
                await self.set(cache_key, result, ttl)
                logger.debug(f"Cache miss: {cache_key}")

                return result

            return wrapper
        return decorator


# Global cache manager instance
_cache_manager = None


def get_cache_manager(backend: Optional[CacheBackend] = None) -> CacheManager:
    """Get or create global cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(backend)
    return _cache_manager
