"""
Unit tests for caching system
"""

import pytest
import asyncio
from pathlib import Path
import shutil
from core.caching import (
    MemoryCacheBackend,
    FileCacheBackend,
    CacheManager
)


class TestMemoryCacheBackend:
    """Tests for memory cache backend"""

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test setting and getting values"""
        cache = MemoryCacheBackend()

        await cache.set("key1", "value1")
        value = await cache.get("key1")

        assert value == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self):
        """Test getting non-existent key"""
        cache = MemoryCacheBackend()

        value = await cache.get("nonexistent")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test deleting keys"""
        cache = MemoryCacheBackend()

        await cache.set("key1", "value1")
        await cache.delete("key1")

        value = await cache.get("key1")
        assert value is None

    @pytest.mark.asyncio
    async def test_exists(self):
        """Test checking key existence"""
        cache = MemoryCacheBackend()

        await cache.set("key1", "value1")

        assert await cache.exists("key1")
        assert not await cache.exists("key2")

    @pytest.mark.asyncio
    async def test_clear(self):
        """Test clearing cache"""
        cache = MemoryCacheBackend()

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.clear()

        assert not await cache.exists("key1")
        assert not await cache.exists("key2")

    @pytest.mark.asyncio
    async def test_ttl(self):
        """Test TTL expiry"""
        cache = MemoryCacheBackend()

        await cache.set("key1", "value1", ttl=1)

        # Should exist immediately
        assert await cache.exists("key1")

        # Wait for expiry
        await asyncio.sleep(1.1)

        # Should be expired
        assert not await cache.exists("key1")


class TestFileCacheBackend:
    """Tests for file cache backend"""

    @pytest.fixture
    def cache_dir(self, tmp_path):
        """Create temporary cache directory"""
        cache_dir = tmp_path / "cache"
        yield str(cache_dir)
        # Cleanup
        if cache_dir.exists():
            shutil.rmtree(cache_dir)

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_dir):
        """Test setting and getting values"""
        cache = FileCacheBackend(cache_dir=cache_dir)

        await cache.set("key1", {"data": "value1"})
        value = await cache.get("key1")

        assert value == {"data": "value1"}

    @pytest.mark.asyncio
    async def test_persistence(self, cache_dir):
        """Test that cache persists"""
        cache1 = FileCacheBackend(cache_dir=cache_dir)
        await cache1.set("key1", "value1")

        # Create new cache instance
        cache2 = FileCacheBackend(cache_dir=cache_dir)
        value = await cache2.get("key1")

        assert value == "value1"

    @pytest.mark.asyncio
    async def test_delete(self, cache_dir):
        """Test deleting keys"""
        cache = FileCacheBackend(cache_dir=cache_dir)

        await cache.set("key1", "value1")
        await cache.delete("key1")

        value = await cache.get("key1")
        assert value is None

    @pytest.mark.asyncio
    async def test_clear(self, cache_dir):
        """Test clearing cache"""
        cache = FileCacheBackend(cache_dir=cache_dir)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.clear()

        assert not await cache.exists("key1")
        assert not await cache.exists("key2")


class TestCacheManager:
    """Tests for cache manager"""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test cache manager initialization"""
        manager = CacheManager()
        assert manager.backend is not None

    @pytest.mark.asyncio
    async def test_basic_operations(self):
        """Test basic cache operations"""
        manager = CacheManager()

        await manager.set("key1", "value1")
        value = await manager.get("key1")
        assert value == "value1"

        await manager.delete("key1")
        value = await manager.get("key1")
        assert value is None

    @pytest.mark.asyncio
    async def test_cached_decorator(self):
        """Test cached decorator"""
        manager = CacheManager()

        call_count = 0

        @manager.cached(ttl=60)
        async def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call should execute function
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call should use cache
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented

        # Different argument should execute function again
        result3 = await expensive_function(10)
        assert result3 == 20
        assert call_count == 2
