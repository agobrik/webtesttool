"""
Cache Manager for WebTestool
Provides in-memory and disk-based caching for HTTP requests and scan results
"""

import hashlib
import json
import pickle
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import aiofiles
from loguru import logger


class CacheManager:
    """
    Asynchronous cache manager with memory and disk storage

    Features:
    - In-memory cache (fast access)
    - Disk-based cache (persistent)
    - TTL (Time-to-Live) support
    - Automatic cleanup
    - LRU eviction for memory cache

    Example:
        cache = CacheManager(cache_dir=".cache", ttl=3600)

        # Store data
        await cache.set("http://example.com", data)

        # Retrieve data
        data = await cache.get("http://example.com")

        # Clear all cache
        await cache.clear()
    """

    def __init__(
        self,
        cache_dir: str = ".cache",
        ttl: int = 3600,
        max_memory_items: int = 1000
    ):
        """
        Initialize cache manager

        Args:
            cache_dir: Directory for disk cache
            ttl: Time-to-live in seconds (default: 1 hour)
            max_memory_items: Maximum items in memory cache
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.max_memory_items = max_memory_items
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
        self._ensure_cache_dir()

        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }

    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Cache directory: {self.cache_dir}")

    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """
        Generate cache key from URL and parameters

        Args:
            url: URL to cache
            params: Optional parameters

        Returns:
            SHA256 hash as cache key
        """
        key_data = f"{url}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.cache"

    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() - timestamp > timedelta(seconds=self.ttl)

    def _evict_lru(self):
        """Evict least recently used item from memory cache"""
        if not self.access_times:
            return

        # Find oldest accessed item
        oldest_key = min(self.access_times, key=self.access_times.get)

        # Remove from caches
        if oldest_key in self.memory_cache:
            del self.memory_cache[oldest_key]
        del self.access_times[oldest_key]

        self.stats['evictions'] += 1
        logger.debug(f"Evicted cache entry: {oldest_key[:8]}...")

    async def get(self, url: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Retrieve data from cache

        Args:
            url: URL to retrieve
            params: Optional parameters

        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._get_cache_key(url, params)

        # Check memory cache first
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]

            if not self._is_expired(entry['timestamp']):
                # Update access time
                self.access_times[cache_key] = datetime.now()
                self.stats['hits'] += 1
                logger.debug(f"Memory cache HIT: {url}")
                return entry['data']
            else:
                # Expired, remove from memory
                del self.memory_cache[cache_key]
                if cache_key in self.access_times:
                    del self.access_times[cache_key]

        # Check disk cache
        cache_path = self._get_cache_path(cache_key)

        if cache_path.exists():
            try:
                async with aiofiles.open(cache_path, 'rb') as f:
                    content = await f.read()
                    entry = pickle.loads(content)

                timestamp = entry['timestamp']

                if not self._is_expired(timestamp):
                    # Load into memory cache
                    if len(self.memory_cache) >= self.max_memory_items:
                        self._evict_lru()

                    self.memory_cache[cache_key] = {
                        'data': entry['data'],
                        'timestamp': timestamp
                    }
                    self.access_times[cache_key] = datetime.now()

                    self.stats['hits'] += 1
                    logger.debug(f"Disk cache HIT: {url}")
                    return entry['data']
                else:
                    # Expired, delete file
                    cache_path.unlink()

            except Exception as e:
                logger.warning(f"Failed to read cache: {e}")

        self.stats['misses'] += 1
        logger.debug(f"Cache MISS: {url}")
        return None

    async def set(self, url: str, data: Any, params: Optional[Dict] = None):
        """
        Store data in cache

        Args:
            url: URL to cache
            data: Data to store
            params: Optional parameters
        """
        cache_key = self._get_cache_key(url, params)
        timestamp = datetime.now()

        # Store in memory cache
        if len(self.memory_cache) >= self.max_memory_items:
            self._evict_lru()

        self.memory_cache[cache_key] = {
            'data': data,
            'timestamp': timestamp
        }
        self.access_times[cache_key] = timestamp

        # Store in disk cache
        try:
            cache_path = self._get_cache_path(cache_key)
            entry = {
                'url': url,
                'data': data,
                'timestamp': timestamp,
                'params': params
            }

            async with aiofiles.open(cache_path, 'wb') as f:
                await f.write(pickle.dumps(entry))

            self.stats['sets'] += 1
            logger.debug(f"Cached: {url}")

        except Exception as e:
            logger.warning(f"Failed to write cache: {e}")

    async def has(self, url: str, params: Optional[Dict] = None) -> bool:
        """
        Check if URL is in cache

        Args:
            url: URL to check
            params: Optional parameters

        Returns:
            True if cached and not expired
        """
        result = await self.get(url, params)
        return result is not None

    async def clear(self):
        """Clear all cache (memory and disk)"""
        # Clear memory cache
        self.memory_cache.clear()
        self.access_times.clear()

        # Clear disk cache
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete cache file: {e}")

        logger.info("Cache cleared")

    async def clear_expired(self):
        """Remove expired entries from cache"""
        # Clear expired from memory
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if self._is_expired(entry['timestamp'])
        ]

        for key in expired_keys:
            del self.memory_cache[key]
            if key in self.access_times:
                del self.access_times[key]

        # Clear expired from disk
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    async with aiofiles.open(cache_file, 'rb') as f:
                        content = await f.read()
                        entry = pickle.loads(content)

                    if self._is_expired(entry['timestamp']):
                        cache_file.unlink()

                except Exception as e:
                    logger.warning(f"Failed to check cache file: {e}")

        logger.info(f"Cleared {len(expired_keys)} expired entries")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'sets': self.stats['sets'],
            'evictions': self.stats['evictions'],
            'hit_rate': f"{hit_rate:.1f}%",
            'memory_items': len(self.memory_cache),
            'max_memory_items': self.max_memory_items,
            'ttl_seconds': self.ttl
        }

    def print_stats(self):
        """Print cache statistics"""
        stats = self.get_stats()
        logger.info("Cache Statistics:")
        logger.info(f"  Hits: {stats['hits']}")
        logger.info(f"  Misses: {stats['misses']}")
        logger.info(f"  Hit Rate: {stats['hit_rate']}")
        logger.info(f"  Memory Items: {stats['memory_items']}/{stats['max_memory_items']}")
        logger.info(f"  Sets: {stats['sets']}")
        logger.info(f"  Evictions: {stats['evictions']}")


# Singleton instance
_cache_instance: Optional[CacheManager] = None


def get_cache(
    cache_dir: str = ".cache",
    ttl: int = 3600,
    max_memory_items: int = 1000
) -> CacheManager:
    """
    Get or create singleton cache instance

    Args:
        cache_dir: Directory for disk cache
        ttl: Time-to-live in seconds
        max_memory_items: Maximum items in memory cache

    Returns:
        CacheManager instance
    """
    global _cache_instance

    if _cache_instance is None:
        _cache_instance = CacheManager(
            cache_dir=cache_dir,
            ttl=ttl,
            max_memory_items=max_memory_items
        )

    return _cache_instance
