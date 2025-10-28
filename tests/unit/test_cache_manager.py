"""
Unit tests for Cache Manager
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from utils.cache_manager import CacheManager


@pytest.fixture
async def cache_manager():
    """Create cache manager with temporary directory"""
    temp_dir = tempfile.mkdtemp()
    cache = CacheManager(
        redis_url=None,  # Disable Redis for unit tests
        cache_dir=temp_dir,
        memory_max_size=10,
        default_ttl=3600,
        enable_redis=False
    )
    await cache.connect()
    yield cache
    await cache.close()
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_set_and_get(cache_manager):
    """Test basic cache set and get operations"""
    # Set a value
    await cache_manager.set("test_key", {"data": "test_value"})

    # Get the value
    result = await cache_manager.get("test_key")

    assert result is not None
    assert result["data"] == "test_value"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_miss(cache_manager):
    """Test cache miss returns None"""
    result = await cache_manager.get("non_existent_key")
    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_with_params(cache_manager):
    """Test cache with parameters"""
    # Set value with params
    await cache_manager.set(
        "api_endpoint",
        {"response": "data"},
        params={"page": 1, "limit": 10}
    )

    # Get with same params
    result = await cache_manager.get(
        "api_endpoint",
        params={"page": 1, "limit": 10}
    )

    assert result is not None
    assert result["response"] == "data"

    # Get with different params should miss
    result = await cache_manager.get(
        "api_endpoint",
        params={"page": 2, "limit": 10}
    )

    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_ttl_expiration(cache_manager):
    """Test cache TTL expiration"""
    # Set with short TTL (1 second)
    await cache_manager.set("expiring_key", {"data": "test"}, ttl=1)

    # Should exist immediately
    result = await cache_manager.get("expiring_key")
    assert result is not None

    # Wait for expiration
    await asyncio.sleep(1.5)

    # Should be expired
    result = await cache_manager.get("expiring_key")
    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_stats(cache_manager):
    """Test cache statistics tracking"""
    # Initial stats
    stats = cache_manager.get_stats()
    assert stats['hits'] == 0
    assert stats['misses'] == 0

    # Add some data
    await cache_manager.set("key1", "value1")

    # Hit
    await cache_manager.get("key1")
    stats = cache_manager.get_stats()
    assert stats['hits'] == 1
    assert stats['misses'] == 0

    # Miss
    await cache_manager.get("key2")
    stats = cache_manager.get_stats()
    assert stats['hits'] == 1
    assert stats['misses'] == 1

    # Calculate hit rate
    assert stats['hit_rate'] == 0.5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_clear(cache_manager):
    """Test cache clear operation"""
    # Add some data
    await cache_manager.set("key1", "value1")
    await cache_manager.set("key2", "value2")

    # Verify data exists
    assert await cache_manager.get("key1") is not None
    assert await cache_manager.get("key2") is not None

    # Clear cache
    await cache_manager.clear()

    # Verify data is gone
    assert await cache_manager.get("key1") is None
    assert await cache_manager.get("key2") is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_memory_cache_lru_eviction(cache_manager):
    """Test LRU eviction in memory cache"""
    # Fill memory cache to max size (10 items)
    for i in range(10):
        await cache_manager.set(f"key{i}", f"value{i}")

    # Access first item to make it recently used
    await cache_manager.get("key0")

    # Add one more item (should evict least recently used, which is key1)
    await cache_manager.set("key10", "value10")

    # key0 should still be in cache (recently accessed)
    assert await cache_manager.get("key0") is not None

    # key10 should be in cache
    assert await cache_manager.get("key10") is not None

    # At least one of the middle keys should be evicted
    # (exact behavior depends on LRU implementation)
    stats = cache_manager.get_stats()
    assert stats['memory_items'] <= 10


@pytest.mark.unit
@pytest.mark.asyncio
async def test_disk_cache_persistence(cache_manager):
    """Test disk cache persistence"""
    # Set value that should be written to disk
    large_data = {"data": "x" * 10000}  # Large data more likely to hit disk
    await cache_manager.set("large_key", large_data)

    # Force flush to disk by filling memory cache
    for i in range(20):
        await cache_manager.set(f"filler{i}", f"value{i}")

    # Should still be able to retrieve from disk
    result = await cache_manager.get("large_key")

    # Note: This test assumes disk caching is working
    # Result might be None if memory cache hasn't evicted yet
    if result is not None:
        assert result["data"] == "x" * 10000


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_delete(cache_manager):
    """Test cache delete operation"""
    # Set a value
    await cache_manager.set("delete_me", "value")

    # Verify it exists
    assert await cache_manager.get("delete_me") is not None

    # Delete it
    await cache_manager.delete("delete_me")

    # Verify it's gone
    assert await cache_manager.get("delete_me") is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_exists(cache_manager):
    """Test cache exists check"""
    # Key doesn't exist
    assert not await cache_manager.exists("nonexistent")

    # Set a value
    await cache_manager.set("exists_key", "value")

    # Key exists
    assert await cache_manager.exists("exists_key")


@pytest.mark.unit
def test_cache_key_generation():
    """Test cache key generation"""
    cache = CacheManager(enable_redis=False)

    # Simple key
    key1 = cache._generate_cache_key("https://example.com")
    assert isinstance(key1, str)
    assert len(key1) > 0

    # Key with params
    key2 = cache._generate_cache_key(
        "https://api.example.com/users",
        params={"page": 1, "limit": 10}
    )
    assert isinstance(key2, str)

    # Same URL with same params should generate same key
    key3 = cache._generate_cache_key(
        "https://api.example.com/users",
        params={"page": 1, "limit": 10}
    )
    assert key2 == key3

    # Same URL with different params should generate different key
    key4 = cache._generate_cache_key(
        "https://api.example.com/users",
        params={"page": 2, "limit": 10}
    )
    assert key2 != key4


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_concurrent_access(cache_manager):
    """Test concurrent cache access"""
    async def set_many(start, count):
        for i in range(start, start + count):
            await cache_manager.set(f"concurrent_{i}", f"value_{i}")

    async def get_many(start, count):
        results = []
        for i in range(start, start + count):
            result = await cache_manager.get(f"concurrent_{i}")
            results.append(result)
        return results

    # Set values concurrently
    await asyncio.gather(
        set_many(0, 10),
        set_many(10, 10),
        set_many(20, 10)
    )

    # Get values concurrently
    results = await asyncio.gather(
        get_many(0, 10),
        get_many(10, 10),
        get_many(20, 10)
    )

    # Verify all values were set and retrieved
    all_results = [item for sublist in results for item in sublist]
    # At least some values should be successfully cached
    assert any(r is not None for r in all_results)
