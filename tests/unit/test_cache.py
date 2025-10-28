"""
Unit tests for Cache Manager
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from utils.cache import CacheManager, get_cache


class TestCacheManager:
    """Test CacheManager functionality"""

    @pytest.fixture
    def cache_dir(self):
        """Create temporary cache directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def cache_manager(self, cache_dir):
        """Create CacheManager instance"""
        return CacheManager(cache_dir=cache_dir, ttl=60)

    @pytest.mark.asyncio
    async def test_cache_initialization(self, cache_manager, cache_dir):
        """Test cache initialization"""
        assert cache_manager.cache_dir == Path(cache_dir)
        assert cache_manager.ttl == 60
        assert len(cache_manager.memory_cache) == 0
        assert Path(cache_dir).exists()

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, cache_manager):
        """Test setting and getting cache"""
        url = "https://example.com"
        data = {"status": 200, "content": "Hello World"}

        # Set cache
        await cache_manager.set(url, data)

        # Get cache
        cached_data = await cache_manager.get(url)

        assert cached_data == data
        assert cache_manager.stats['sets'] == 1
        assert cache_manager.stats['hits'] == 1

    @pytest.mark.asyncio
    async def test_cache_miss(self, cache_manager):
        """Test cache miss"""
        url = "https://example.com/nonexistent"

        # Get non-existent
        cached_data = await cache_manager.get(url)

        assert cached_data is None
        assert cache_manager.stats['misses'] == 1

    @pytest.mark.asyncio
    async def test_cache_with_params(self, cache_manager):
        """Test cache with parameters"""
        url = "https://example.com/api"
        params = {"page": 1, "limit": 10}
        data = {"results": [1, 2, 3]}

        # Set with params
        await cache_manager.set(url, data, params)

        # Get with same params
        cached_data = await cache_manager.get(url, params)
        assert cached_data == data

        # Get with different params (should miss)
        cached_data = await cache_manager.get(url, {"page": 2})
        assert cached_data is None

    @pytest.mark.asyncio
    async def test_cache_expiration(self, cache_dir):
        """Test cache expiration"""
        # Create cache with 1 second TTL
        cache_manager = CacheManager(cache_dir=cache_dir, ttl=1)

        url = "https://example.com"
        data = {"content": "test"}

        # Set cache
        await cache_manager.set(url, data)

        # Should get immediately
        cached = await cache_manager.get(url)
        assert cached == data

        # Wait for expiration
        await asyncio.sleep(1.5)

        # Should be expired
        cached = await cache_manager.get(url)
        assert cached is None

    @pytest.mark.asyncio
    async def test_cache_has(self, cache_manager):
        """Test cache has method"""
        url = "https://example.com"
        data = {"test": "data"}

        # Should not have initially
        assert await cache_manager.has(url) is False

        # Set cache
        await cache_manager.set(url, data)

        # Should have now
        assert await cache_manager.has(url) is True

    @pytest.mark.asyncio
    async def test_cache_clear(self, cache_manager):
        """Test cache clearing"""
        # Add multiple items
        for i in range(5):
            await cache_manager.set(f"https://example.com/{i}", {"id": i})

        assert len(cache_manager.memory_cache) == 5

        # Clear cache
        await cache_manager.clear()

        assert len(cache_manager.memory_cache) == 0

    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache_dir):
        """Test LRU eviction"""
        # Create cache with max 3 items
        cache_manager = CacheManager(cache_dir=cache_dir, max_memory_items=3)

        # Add 4 items
        for i in range(4):
            await cache_manager.set(f"https://example.com/{i}", {"id": i})

        # Should only have 3 items in memory
        assert len(cache_manager.memory_cache) == 3

        # First item should be evicted
        assert cache_manager.stats['evictions'] == 1

    @pytest.mark.asyncio
    async def test_cache_stats(self, cache_manager):
        """Test cache statistics"""
        # Perform various operations
        await cache_manager.set("https://example.com/1", {"data": 1})
        await cache_manager.set("https://example.com/2", {"data": 2})

        await cache_manager.get("https://example.com/1")  # Hit
        await cache_manager.get("https://example.com/3")  # Miss

        stats = cache_manager.get_stats()

        assert stats['sets'] == 2
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['memory_items'] == 2

    @pytest.mark.asyncio
    async def test_get_cache_singleton(self):
        """Test singleton cache instance"""
        cache1 = get_cache()
        cache2 = get_cache()

        assert cache1 is cache2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
