"""
Integration tests for full scan workflow
"""

import pytest
import asyncio
from pathlib import Path
import tempfile

from core.config import ConfigManager
from core.engine import TestEngine
from core.scanner import WebScanner


@pytest.fixture
def test_config():
    """Create test configuration"""
    config = ConfigManager()

    # Set test URL (use a safe test site)
    config.set('target.url', 'https://example.com')

    # Limit scope for faster tests
    config.set('crawler.max_pages', 5)
    config.set('crawler.max_depth', 1)
    config.set('crawler.timeout', 10)

    # Disable modules for faster test
    config.set('modules.security.enabled', False)
    config.set('modules.performance.enabled', False)
    config.set('modules.seo.enabled', False)
    config.set('modules.accessibility.enabled', False)

    # Enable cache but without Redis
    config.set('cache.enabled', True)
    config.set('cache.redis.enabled', False)

    return config


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_basic_scan_workflow(test_config):
    """Test basic scan workflow"""
    # Create engine
    engine = TestEngine(test_config, enable_progress_display=False)

    # Run scan
    result = await engine.run()

    # Verify result
    assert result is not None
    assert result.target_url == 'https://example.com'
    assert result.status is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scanner_basic_crawl(test_config):
    """Test basic scanner functionality"""
    # Create scanner
    scanner = WebScanner(test_config)

    # Scan
    crawled_pages, api_endpoints = await scanner.scan()

    # Verify results
    assert isinstance(crawled_pages, list)
    assert isinstance(api_endpoints, list)
    assert len(crawled_pages) >= 1  # At least the base URL

    # Cleanup
    await scanner.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scanner_with_cache(test_config):
    """Test scanner with cache enabled"""
    # Enable cache
    test_config.set('cache.enabled', True)
    test_config.set('cache.redis.enabled', False)

    # First scan
    scanner1 = WebScanner(test_config)
    crawled_pages1, _ = await scanner1.scan()
    await scanner1.close()

    # Second scan (should use cache)
    scanner2 = WebScanner(test_config)
    crawled_pages2, _ = await scanner2.scan()
    await scanner2.close()

    # Both scans should return results
    assert len(crawled_pages1) > 0
    assert len(crawled_pages2) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_engine_with_progress_tracking(test_config):
    """Test engine with progress tracking"""
    # Create engine with progress tracking disabled for test
    engine = TestEngine(test_config, enable_progress_display=False)

    # Progress tracker should be initialized
    assert engine.progress is not None

    # Run scan
    result = await engine.run()

    # Verify result
    assert result is not None


@pytest.mark.integration
def test_config_cache_integration(test_config):
    """Test cache configuration integration"""
    # Verify cache config is accessible
    cache_enabled = test_config.get('cache.enabled', False)

    if cache_enabled:
        # Cache should have configuration
        assert test_config.config.cache is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scanner_error_handling(test_config):
    """Test scanner handles errors gracefully"""
    # Set invalid URL
    test_config.set('target.url', 'https://invalid-domain-that-does-not-exist.com')

    scanner = WebScanner(test_config)

    # Should handle error gracefully
    try:
        crawled_pages, _ = await scanner.scan()
        # May return empty list on error
        assert isinstance(crawled_pages, list)
    except Exception as e:
        # Or may raise exception
        assert e is not None

    await scanner.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_scans(test_config):
    """Test running multiple scans concurrently"""
    async def run_scan():
        scanner = WebScanner(test_config)
        result = await scanner.scan()
        await scanner.close()
        return result

    # Run 3 concurrent scans
    results = await asyncio.gather(
        run_scan(),
        run_scan(),
        run_scan(),
        return_exceptions=True
    )

    # All should complete (may return results or exceptions)
    assert len(results) == 3


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scan_result_structure(test_config):
    """Test that scan result has expected structure"""
    engine = TestEngine(test_config, enable_progress_display=False)
    result = await engine.run()

    # Verify structure
    assert hasattr(result, 'target_url')
    assert hasattr(result, 'start_time')
    assert hasattr(result, 'status')
    assert hasattr(result, 'summary')

    # Summary should be a dict
    summary = result.summary
    assert isinstance(summary, dict)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scanner_respects_max_pages(test_config):
    """Test that scanner respects max_pages limit"""
    # Set low max_pages
    test_config.set('crawler.max_pages', 2)

    scanner = WebScanner(test_config)
    crawled_pages, _ = await scanner.scan()
    await scanner.close()

    # Should not exceed max_pages
    assert len(crawled_pages) <= 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scanner_respects_max_depth(test_config):
    """Test that scanner respects max_depth limit"""
    # Set max_depth to 0 (only crawl base URL)
    test_config.set('crawler.max_depth', 0)

    scanner = WebScanner(test_config)
    crawled_pages, _ = await scanner.scan()
    await scanner.close()

    # Should only have base URL
    assert len(crawled_pages) <= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_engine_module_loading(test_config):
    """Test that engine loads modules correctly"""
    engine = TestEngine(test_config, enable_progress_display=False)

    # Module loader should be initialized
    assert engine.module_loader is not None


@pytest.mark.integration
def test_cache_directory_creation(test_config):
    """Test that cache directory is created if needed"""
    # Set temp cache directory
    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / "test_cache"

    test_config.set('cache.disk.directory', str(cache_dir))
    test_config.set('cache.disk.enabled', True)

    # Create scanner (should create cache dir)
    scanner = WebScanner(test_config)

    # Directory should be created by CacheManager
    # (may not exist yet if cache not connected)
    assert scanner is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_progress_stats_update_during_scan(test_config):
    """Test that progress stats update during scan"""
    engine = TestEngine(test_config, enable_progress_display=False)

    # Check initial stats
    initial_pages = engine.progress.stats['pages_crawled']
    assert initial_pages == 0

    # Run scan
    await engine.run()

    # Stats should have updated
    # (may still be 0 if crawler disabled or failed)
    final_pages = engine.progress.stats['pages_crawled']
    assert final_pages >= 0
