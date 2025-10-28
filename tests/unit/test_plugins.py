"""
Unit tests for plugin system
"""

import pytest
from core.plugins import (
    Plugin,
    PreScanPlugin,
    PostScanPlugin,
    PluginManager,
    ExamplePreScanPlugin,
    ExamplePostScanPlugin
)


class TestPlugin:
    """Tests for base Plugin class"""

    def test_plugin_info(self):
        """Test plugin information retrieval"""
        plugin = ExamplePreScanPlugin()

        info = plugin.get_info()

        assert info['name'] == 'example_pre_scan'
        assert info['version'] == '1.0.0'
        assert 'description' in info


class TestPluginManager:
    """Tests for PluginManager"""

    def test_initialization(self):
        """Test plugin manager initialization"""
        manager = PluginManager()

        assert len(manager.plugins) == 0
        assert len(manager.plugin_types) > 0

    def test_register_plugin(self):
        """Test plugin registration"""
        manager = PluginManager()
        plugin = ExamplePreScanPlugin()

        success = manager.register_plugin(plugin)

        assert success
        assert plugin.name in manager.plugins

    def test_register_duplicate(self):
        """Test registering duplicate plugin"""
        manager = PluginManager()
        plugin1 = ExamplePreScanPlugin()
        plugin2 = ExamplePreScanPlugin()

        manager.register_plugin(plugin1)
        success = manager.register_plugin(plugin2)

        # Should fail to register duplicate
        assert not success

    def test_unregister_plugin(self):
        """Test plugin unregistration"""
        manager = PluginManager()
        plugin = ExamplePreScanPlugin()

        manager.register_plugin(plugin)
        success = manager.unregister_plugin(plugin.name)

        assert success
        assert plugin.name not in manager.plugins

    def test_get_plugin(self):
        """Test getting plugin by name"""
        manager = PluginManager()
        plugin = ExamplePreScanPlugin()
        manager.register_plugin(plugin)

        retrieved = manager.get_plugin(plugin.name)

        assert retrieved is plugin

    def test_get_plugins_by_type(self):
        """Test getting plugins by type"""
        manager = PluginManager()

        pre_scan = ExamplePreScanPlugin()
        post_scan = ExamplePostScanPlugin()

        manager.register_plugin(pre_scan)
        manager.register_plugin(post_scan)

        pre_scan_plugins = manager.get_plugins_by_type('pre_scan')
        post_scan_plugins = manager.get_plugins_by_type('post_scan')

        assert len(pre_scan_plugins) == 1
        assert len(post_scan_plugins) == 1
        assert pre_scan_plugins[0].name == pre_scan.name

    def test_initialize_all(self):
        """Test initializing all plugins"""
        manager = PluginManager()
        plugin = ExamplePreScanPlugin()
        manager.register_plugin(plugin)

        config = {'plugins': {plugin.name: {}}}
        results = manager.initialize_all(config)

        assert plugin.name in results
        assert results[plugin.name] is True

    def test_execute_plugins(self):
        """Test executing plugins"""
        manager = PluginManager()
        plugin = ExamplePreScanPlugin()
        manager.register_plugin(plugin)
        manager.initialize_all({})

        context = {
            'target_url': 'https://example.com',
            'config': {}
        }

        results = manager.execute_plugins('pre_scan', context)

        assert len(results) == 1
        assert results[0]['plugin'] == plugin.name
        assert results[0]['success'] is True

    def test_list_plugins(self):
        """Test listing plugins"""
        manager = PluginManager()

        plugin1 = ExamplePreScanPlugin()
        plugin2 = ExamplePostScanPlugin()

        manager.register_plugin(plugin1)
        manager.register_plugin(plugin2)

        plugin_list = manager.list_plugins()

        assert len(plugin_list) == 2
        assert any(p['name'] == plugin1.name for p in plugin_list)
        assert any(p['name'] == plugin2.name for p in plugin_list)

    def test_cleanup_all(self):
        """Test cleaning up all plugins"""
        manager = PluginManager()
        plugin = ExamplePreScanPlugin()
        manager.register_plugin(plugin)

        # Should not raise exception
        manager.cleanup_all()


class MockPreScanPlugin(PreScanPlugin):
    """Mock plugin for testing"""

    name = "mock_pre_scan"
    version = "1.0.0"

    def __init__(self):
        self.initialized = False
        self.executed = False

    def initialize(self, config):
        self.initialized = True
        return True

    def pre_scan(self, target_url, config):
        self.executed = True
        return {'status': 'ok', 'target': target_url}


class TestPluginExecution:
    """Tests for plugin execution"""

    def test_pre_scan_execution(self):
        """Test pre-scan plugin execution"""
        manager = PluginManager()
        plugin = MockPreScanPlugin()

        manager.register_plugin(plugin)
        manager.initialize_all({})

        assert plugin.initialized

        context = {
            'target_url': 'https://test.com',
            'config': {}
        }

        results = manager.execute_plugins('pre_scan', context)

        assert plugin.executed
        assert results[0]['success']
        assert results[0]['result']['status'] == 'ok'
