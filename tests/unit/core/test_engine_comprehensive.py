"""
Comprehensive tests for TestEngine
Coverage target: 85%+
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from core.engine import TestEngine
from core.config import ConfigManager
from core.models import (
    ScanResult, ModuleResult, TestContext, TestStatus,
    Category, Severity, CrawledPage
)


class TestEngineInitialization:
    """Test engine initialization"""

    def test_engine_creation(self):
        """Test creating test engine"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')

        engine = TestEngine(config)

        assert engine is not None
        assert engine.config == config
        assert engine.scanner is not None
        assert engine.module_loader is not None

    def test_engine_with_custom_config(self):
        """Test engine with custom configuration"""
        config = ConfigManager()
        config.set('target.url', 'https://custom.com')
        config.set('crawler.max_pages', 50)

        engine = TestEngine(config)

        assert engine.config.get('target.url') == 'https://custom.com'
        assert engine.config.get('crawler.max_pages') == 50


class TestEngineRun:
    """Test main engine run method"""

    @pytest.mark.asyncio
    async def test_run_creates_scan_result(self):
        """Test run method creates scan result"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.enabled', False)  # Disable crawler for speed
        config.set('modules.security.enabled', False)  # Disable modules

        engine = TestEngine(config)

        with patch.object(engine.module_loader, 'get_enabled_modules', return_value=[]):
            result = await engine.run()

        assert result is not None
        assert isinstance(result, ScanResult)
        assert result.target_url == 'https://example.com'

    @pytest.mark.asyncio
    async def test_run_with_crawler_disabled(self):
        """Test run with crawler disabled"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.enabled', False)
        config.set('modules.security.enabled', False)

        engine = TestEngine(config)

        with patch.object(engine.module_loader, 'get_enabled_modules', return_value=[]):
            result = await engine.run()

        assert result.crawled_urls == []

    @pytest.mark.asyncio
    async def test_run_with_crawler_enabled(self):
        """Test run with crawler enabled"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.enabled', True)
        config.set('crawler.max_pages', 5)
        config.set('modules.security.enabled', False)

        engine = TestEngine(config)

        # Mock scanner
        mock_pages = [CrawledPage(url=f'https://example.com/page{i}', status_code=200) for i in range(5)]
        mock_apis = []

        with patch.object(engine.scanner, 'scan', return_value=(mock_pages, mock_apis)):
            with patch.object(engine.module_loader, 'get_enabled_modules', return_value=[]):
                result = await engine.run()

        assert len(result.crawled_urls) == 5

    @pytest.mark.asyncio
    async def test_run_executes_modules(self):
        """Test run executes enabled modules"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.enabled', False)

        engine = TestEngine(config)

        # Create mock module
        mock_module = Mock()
        mock_module.name = 'test_module'
        mock_module.category = Category.SECURITY
        mock_module.setup = AsyncMock()
        mock_module.teardown = AsyncMock()

        mock_result = ModuleResult(
            name='test_module',
            category=Category.SECURITY,
            status=TestStatus.PASSED
        )
        mock_module.run = AsyncMock(return_value=mock_result)

        with patch.object(engine.module_loader, 'get_enabled_modules', return_value=[mock_module]):
            result = await engine.run()

        # Verify module was called
        mock_module.setup.assert_called_once()
        mock_module.run.assert_called_once()
        mock_module.teardown.assert_called_once()

        assert len(result.module_results) == 1

    @pytest.mark.asyncio
    async def test_run_handles_module_errors(self):
        """Test run handles module errors gracefully"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.enabled', False)

        engine = TestEngine(config)

        # Create mock module that raises error
        mock_module = Mock()
        mock_module.name = 'failing_module'
        mock_module.category = Category.SECURITY
        mock_module.setup = AsyncMock()
        mock_module.run = AsyncMock(side_effect=Exception("Test error"))
        mock_module.teardown = AsyncMock()

        with patch.object(engine.module_loader, 'get_enabled_modules', return_value=[mock_module]):
            result = await engine.run()

        # Engine should complete despite module error
        assert result is not None
        assert len(result.module_results) == 1
        assert result.module_results[0].status == TestStatus.ERROR


class TestEngineModuleExecution:
    """Test module execution logic"""

    @pytest.mark.asyncio
    async def test_run_module_success(self):
        """Test successful module execution"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')

        engine = TestEngine(config)

        # Create mock module
        mock_module = Mock()
        mock_module.name = 'test_module'
        mock_module.category = Category.SECURITY
        mock_module.setup = AsyncMock()
        mock_module.teardown = AsyncMock()

        mock_result = ModuleResult(
            name='test_module',
            category=Category.SECURITY,
            status=TestStatus.PASSED
        )
        mock_module.run = AsyncMock(return_value=mock_result)

        context = TestContext(
            target_url='https://example.com',
            base_url='https://example.com'
        )

        result = await engine._run_module(mock_module, context)

        assert result.name == 'test_module'
        assert result.status == TestStatus.PASSED

    @pytest.mark.asyncio
    async def test_run_module_with_error(self):
        """Test module execution with error"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')

        engine = TestEngine(config)

        # Create mock module that fails
        mock_module = Mock()
        mock_module.name = 'failing_module'
        mock_module.category = Category.SECURITY
        mock_module.setup = AsyncMock()
        mock_module.run = AsyncMock(side_effect=Exception("Module error"))
        mock_module.teardown = AsyncMock()

        context = TestContext(
            target_url='https://example.com',
            base_url='https://example.com'
        )

        result = await engine._run_module(mock_module, context)

        assert result.status == TestStatus.ERROR


class TestEngineParallelExecution:
    """Test parallel module execution"""

    @pytest.mark.asyncio
    async def test_parallel_execution_enabled(self):
        """Test modules run in parallel when enabled"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.enabled', False)
        config.set('advanced.parallel_execution', True)

        engine = TestEngine(config)

        # Create multiple mock modules
        mock_modules = []
        for i in range(3):
            mock_module = Mock()
            mock_module.name = f'module_{i}'
            mock_module.category = Category.SECURITY
            mock_module.setup = AsyncMock()
            mock_module.teardown = AsyncMock()

            mock_result = ModuleResult(
                name=f'module_{i}',
                category=Category.SECURITY,
                status=TestStatus.PASSED
            )
            mock_module.run = AsyncMock(return_value=mock_result)
            mock_modules.append(mock_module)

        with patch.object(engine.module_loader, 'get_enabled_modules', return_value=mock_modules):
            result = await engine.run()

        # All modules should have been executed
        assert len(result.module_results) == 3

    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Test modules run sequentially when parallel disabled"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.enabled', False)
        config.set('advanced.parallel_execution', False)

        engine = TestEngine(config)

        # Create mock modules
        mock_modules = []
        for i in range(2):
            mock_module = Mock()
            mock_module.name = f'module_{i}'
            mock_module.category = Category.SECURITY
            mock_module.setup = AsyncMock()
            mock_module.teardown = AsyncMock()

            mock_result = ModuleResult(
                name=f'module_{i}',
                category=Category.SECURITY,
                status=TestStatus.PASSED
            )
            mock_module.run = AsyncMock(return_value=mock_result)
            mock_modules.append(mock_module)

        with patch.object(engine.module_loader, 'get_enabled_modules', return_value=mock_modules):
            result = await engine.run()

        assert len(result.module_results) == 2


class TestEngineUtilityMethods:
    """Test engine utility methods"""

    def test_get_result_before_run(self):
        """Test get_result before running scan"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')

        engine = TestEngine(config)

        result = engine.get_result()
        assert result is None

    @pytest.mark.asyncio
    async def test_get_result_after_run(self):
        """Test get_result after running scan"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.enabled', False)
        config.set('modules.security.enabled', False)

        engine = TestEngine(config)

        with patch.object(engine.module_loader, 'get_enabled_modules', return_value=[]):
            await engine.run()

        result = engine.get_result()
        assert result is not None
        assert isinstance(result, ScanResult)

    def test_list_modules(self):
        """Test listing available modules"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')

        engine = TestEngine(config)

        with patch.object(engine.module_loader, 'list_modules', return_value={'security': {}, 'performance': {}}):
            modules = engine.list_modules()

        assert 'security' in modules
        assert 'performance' in modules

    @pytest.mark.asyncio
    async def test_run_specific_module(self):
        """Test running a specific module by name"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')

        engine = TestEngine(config)

        # Create mock module
        mock_module = Mock()
        mock_module.name = 'security'
        mock_module.category = Category.SECURITY
        mock_module.enabled = True
        mock_module.setup = AsyncMock()
        mock_module.teardown = AsyncMock()

        mock_result = ModuleResult(
            name='security',
            category=Category.SECURITY,
            status=TestStatus.PASSED
        )
        mock_module.run = AsyncMock(return_value=mock_result)

        with patch.object(engine.module_loader, 'get_module', return_value=mock_module):
            result = await engine.run_module('security')

        assert result.name == 'security'


class TestEngineContextCreation:
    """Test test context creation"""

    @pytest.mark.asyncio
    async def test_context_with_crawled_pages(self):
        """Test context includes crawled pages"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.enabled', True)

        engine = TestEngine(config)

        # Mock crawler results
        mock_pages = [CrawledPage(url='https://example.com/page1', status_code=200)]
        mock_apis = []

        mock_module = Mock()
        mock_module.name = 'test'
        mock_module.category = Category.SECURITY
        mock_module.setup = AsyncMock()
        mock_module.teardown = AsyncMock()
        mock_module.run = AsyncMock(return_value=ModuleResult(
            name='test',
            category=Category.SECURITY,
            status=TestStatus.PASSED
        ))

        with patch.object(engine.scanner, 'scan', return_value=(mock_pages, mock_apis)):
            with patch.object(engine.module_loader, 'get_enabled_modules', return_value=[mock_module]):
                await engine.run()

        # Verify module was called with context containing pages
        call_args = mock_module.run.call_args
        context = call_args[0][0]

        assert len(context.crawled_pages) == 1
        assert context.crawled_pages[0].url == 'https://example.com/page1'


class TestEngineSummary:
    """Test scan summary generation"""

    @pytest.mark.asyncio
    async def test_summary_includes_findings_count(self):
        """Test summary includes findings count"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('crawler.enabled', False)

        engine = TestEngine(config)

        # Create mock module with findings
        mock_module = Mock()
        mock_module.name = 'security'
        mock_module.category = Category.SECURITY
        mock_module.setup = AsyncMock()
        mock_module.teardown = AsyncMock()

        mock_result = ModuleResult(
            name='security',
            category=Category.SECURITY,
            status=TestStatus.PASSED
        )
        mock_result.summary = {
            'total_findings': 5,
            'critical_findings': 1,
            'high_findings': 2
        }
        mock_module.run = AsyncMock(return_value=mock_result)

        with patch.object(engine.module_loader, 'get_enabled_modules', return_value=[mock_module]):
            result = await engine.run()

        assert result.summary is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.engine', '--cov-report=html'])
