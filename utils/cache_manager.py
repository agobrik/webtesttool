"""
Cache Manager - Multi-tier caching system
Supports Memory (L1), Redis (L2), and Disk (L3) caching
"""

import hashlib
import json
import asyncio
import os
import shutil
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis not installed, Redis caching will be disabled")


class CacheManager:
    """
    Multi-tier caching system
    - L1: Memory (fastest, limited size)
    - L2: Redis (fast, persistent) - optional
    - L3: Disk (slower, large capacity)
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        cache_dir: str = ".cache",
        memory_max_size: int = 1000,
        default_ttl: int = 3600,
        enable_redis: bool = True
    ):
        self.redis_url = redis_url
        self.cache_dir = Path(cache_dir)
        self.redis = None
        self.memory_cache: Dict[str, dict] = {}
        self.memory_max_size = memory_max_size
        self.default_ttl = default_ttl
        self.enable_redis = enable_redis and REDIS_AVAILABLE

        self.stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'memory_hits': 0,
            'redis_hits': 0,
            'disk_hits': 0
        }

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def connect(self):
        """Connect to Redis (if enabled)"""
        if not self.enable_redis:
            logger.info("Redis caching disabled, using memory + disk only")
            return

        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("✓ Redis cache connected")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}, falling back to memory + disk")
            self.redis = None

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    def _generate_key(self, url: str, params: dict = None) -> str:
        """Generate cache key from URL and params"""
        key_str = f"{url}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _generate_cache_key(self, url: str, params: dict = None) -> str:
        """Generate cache key from URL and params (alias for _generate_key)"""
        return self._generate_key(url, params)

    async def get(self, url: str, params: dict = None) -> Optional[Any]:
        """
        Get data from cache (L1 -> L2 -> L3)

        Args:
            url: URL to fetch
            params: Optional parameters

        Returns:
            Cached data or None if not found
        """
        cache_key = self._generate_key(url, params)

        # L1: Memory cache
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if datetime.now() < entry['expires_at']:
                self.stats['hits'] += 1
                self.stats['memory_hits'] += 1
                logger.debug(f"Cache HIT (memory): {url[:60]}...")
                return entry['data']
            else:
                # Expired, remove
                del self.memory_cache[cache_key]

        # L2: Redis cache
        if self.redis:
            try:
                data = await self.redis.get(f"cache:{cache_key}")
                if data:
                    self.stats['hits'] += 1
                    self.stats['redis_hits'] += 1
                    logger.debug(f"Cache HIT (redis): {url[:60]}...")

                    # Promote to L1
                    parsed_data = json.loads(data)
                    self._add_to_memory(cache_key, parsed_data)

                    return parsed_data
            except Exception as e:
                logger.error(f"Redis get error: {e}")

        # L3: Disk cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)

                expires_at = datetime.fromisoformat(entry['expires_at'])
                if datetime.now() < expires_at:
                    self.stats['hits'] += 1
                    self.stats['disk_hits'] += 1
                    logger.debug(f"Cache HIT (disk): {url[:60]}...")

                    # Promote to L1 and L2
                    self._add_to_memory(cache_key, entry['data'])
                    if self.redis:
                        try:
                            ttl = int((expires_at - datetime.now()).total_seconds())
                            await self.redis.setex(
                                f"cache:{cache_key}",
                                ttl,
                                json.dumps(entry['data'])
                            )
                        except Exception:
                            pass

                    return entry['data']
                else:
                    # Expired, remove
                    cache_file.unlink(missing_ok=True)
            except Exception as e:
                logger.error(f"Disk cache read error: {e}")

        # Cache miss
        self.stats['misses'] += 1
        logger.debug(f"Cache MISS: {url[:60]}...")
        return None

    async def set(
        self,
        url: str,
        data: Any,
        params: dict = None,
        ttl: int = None
    ):
        """
        Set data in cache (all tiers)

        Args:
            url: URL
            data: Data to cache
            params: Optional parameters
            ttl: Time to live in seconds
        """
        cache_key = self._generate_key(url, params)
        ttl = ttl or self.default_ttl

        self.stats['writes'] += 1

        # Serialize Pydantic models to dict for JSON storage
        serializable_data = data
        if hasattr(data, 'model_dump'):
            # Pydantic v2 model
            serializable_data = data.model_dump()
        elif hasattr(data, 'dict'):
            # Pydantic v1 model (fallback)
            serializable_data = data.dict()

        # L1: Memory (store original object for fast access)
        self._add_to_memory(cache_key, data, ttl)

        # L2: Redis (store serialized data)
        if self.redis:
            try:
                await self.redis.setex(
                    f"cache:{cache_key}",
                    ttl,
                    json.dumps(serializable_data, default=str)
                )
            except Exception as e:
                logger.error(f"Redis set error: {e}")

        # L3: Disk (store serialized data)
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            entry = {
                'url': url,
                'data': serializable_data,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=ttl)).isoformat()
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(entry, f, default=str)
        except Exception as e:
            logger.error(f"Disk cache write error: {e}")

    def _add_to_memory(self, key: str, data: Any, ttl: int = None):
        """Add to memory cache with LRU eviction"""
        ttl = ttl or self.default_ttl

        # Evict oldest if full
        if len(self.memory_cache) >= self.memory_max_size:
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k]['created_at']
            )
            del self.memory_cache[oldest_key]

        self.memory_cache[key] = {
            'data': data,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=ttl)
        }

    async def delete(self, url: str):
        """
        Delete a cache entry

        Args:
            url: URL to delete from cache
        """
        cache_key = self._generate_cache_key(url)

        # Delete from memory
        self.memory_cache.pop(cache_key, None)

        # Delete from Redis
        if self.redis:
            try:
                await self.redis.delete(f"cache:{cache_key}")
            except Exception as e:
                logger.error(f"Redis delete error: {e}")

        # Delete from disk
        cache_file = self.cache_dir / f"{cache_key}.json"
        cache_file.unlink(missing_ok=True)

    async def exists(self, url: str) -> bool:
        """
        Check if a cache entry exists

        Args:
            url: URL to check

        Returns:
            True if cached, False otherwise
        """
        cache_key = self._generate_cache_key(url)

        # Check memory
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if datetime.now() < entry['expires_at']:
                return True

        # Check Redis
        if self.redis:
            try:
                exists = await self.redis.exists(f"cache:{cache_key}")
                if exists:
                    return True
            except Exception:
                pass

        # Check disk
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                expires_at = datetime.fromisoformat(entry['expires_at'])
                if datetime.now() < expires_at:
                    return True
            except Exception:
                pass

        return False

    async def clear(self, pattern: str = "*"):
        """
        Clear cache entries

        Args:
            pattern: Pattern to match (e.g., "*.html")
        """
        # Clear memory
        self.memory_cache.clear()

        # Clear Redis
        if self.redis:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self.redis.scan(
                        cursor,
                        match=f"cache:*",
                        count=100
                    )
                    if keys:
                        await self.redis.delete(*keys)
                    if cursor == 0:
                        break
                logger.info("Redis cache cleared")
            except Exception as e:
                logger.error(f"Redis clear error: {e}")

        # Clear disk
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Disk cache cleared")
        except Exception as e:
            logger.error(f"Disk cache clear error: {e}")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (
            self.stats['hits'] / total_requests
            if total_requests > 0 else 0.0
        )

        return {
            **self.stats,
            'hit_rate': hit_rate,
            'hit_rate_percent': f"{hit_rate * 100:.2f}%",
            'memory_items': len(self.memory_cache),
            'total_requests': total_requests
        }

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'memory_hits': 0,
            'redis_hits': 0,
            'disk_hits': 0
        }
