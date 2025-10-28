"""
Comprehensive tests for ConfigManager
Coverage target: 90%+
"""

import pytest
import os
import tempfile
from pathlib import Path
import yaml

from core.config import ConfigManager, Config, TargetConfig
from core.exceptions import ConfigurationError, ValidationError


class TestConfigManagerBasics:
    """Basic configuration manager tests"""

    def test_config_initialization(self):
        """Test configuration manager initialization"""
        config = ConfigManager()

        assert config is not None
        assert config.config is not None
        assert isinstance(config.config, Config)

    def test_config_has_default_values(self):
        """Test default configuration values"""
        config = ConfigManager()

        # Check default crawler settings
        assert config.config.crawler.max_depth == 5
        assert config.config.crawler.max_pages == 1000
        assert config.config.crawler.enabled is True
        assert config.config.crawler.timeout == 30

    def test_config_target_structure(self):
        """Test target configuration structure"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')

        assert config.config.target.url == 'https://example.com'
        assert isinstance(config.config.target, TargetConfig)


class TestConfigGetSet:
    """Test get/set operations"""

    def test_set_simple_value(self):
        """Test setting a simple configuration value"""
        config = ConfigManager()
        config.set('target.url', 'https://test.com')

        assert config.get('target.url') == 'https://test.com'

    def test_set_nested_value(self):
        """Test setting nested configuration values"""
        config = ConfigManager()
        config.set('modules.security.enabled', True)

        assert config.get('modules.security.enabled') is True

    def test_get_nonexistent_key_returns_default(self):
        """Test getting non-existent key returns default"""
        config = ConfigManager()

        result = config.get('nonexistent.key', 'default_value')
        assert result == 'default_value'

    def test_set_creates_nested_structure(self):
        """Test set creates nested structure if not exists"""
        config = ConfigManager()
        config.set('new.nested.key', 'value')

        assert config.get('new.nested.key') == 'value'

    def test_set_overwrites_existing_value(self):
        """Test set overwrites existing values"""
        config = ConfigManager()
        config.set('target.url', 'https://first.com')
        config.set('target.url', 'https://second.com')

        assert config.get('target.url') == 'https://second.com'


class TestConfigValidation:
    """Test configuration validation"""

    def test_validate_missing_url_fails(self):
        """Test validation fails without URL"""
        config = ConfigManager()

        is_valid, errors = config.validate()

        assert not is_valid
        assert any('URL' in error for error in errors)

    def test_validate_with_url_succeeds(self):
        """Test validation succeeds with URL"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')

        is_valid, errors = config.validate()

        assert is_valid
        assert len(errors) == 0

    def test_validate_requires_at_least_one_module(self):
        """Test validation requires at least one enabled module"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')

        # Disable all modules
        for module in ['security', 'performance', 'functional', 'api',
                       'compatibility', 'accessibility', 'seo', 'infrastructure']:
            config.set(f'modules.{module}.enabled', False)

        is_valid, errors = config.validate()

        assert not is_valid
        assert any('module' in error.lower() for error in errors)

    def test_validate_with_valid_config(self):
        """Test validation with complete valid config"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')
        config.set('modules.security.enabled', True)

        is_valid, errors = config.validate()

        assert is_valid
        assert len(errors) == 0


class TestConfigModules:
    """Test module-related configuration"""

    def test_is_module_enabled(self):
        """Test checking if module is enabled"""
        config = ConfigManager()
        config.set('modules.security.enabled', True)

        assert config.is_module_enabled('security') is True

    def test_is_module_disabled(self):
        """Test checking if module is disabled"""
        config = ConfigManager()
        config.set('modules.performance.enabled', False)

        assert config.is_module_enabled('performance') is False

    def test_get_module_config(self):
        """Test getting module configuration"""
        config = ConfigManager()
        config.set('modules.security.enabled', True)
        config.set('modules.security.aggressive', False)

        module_config = config.get_module_config('security')

        assert module_config is not None
        assert module_config.get('enabled') is True
        assert module_config.get('aggressive') is False

    def test_get_nonexistent_module_config(self):
        """Test getting config for non-existent module"""
        config = ConfigManager()

        module_config = config.get_module_config('nonexistent')

        assert module_config == {}


class TestConfigFile:
    """Test configuration file operations"""

    def test_load_custom_config_file(self):
        """Test loading custom configuration file"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'target': {
                    'url': 'https://custom.com'
                },
                'crawler': {
                    'max_pages': 50
                }
            }
            yaml.dump(config_data, f)
            temp_file = f.name

        try:
            # Load custom config
            config = ConfigManager(temp_file)

            assert config.get('target.url') == 'https://custom.com'
            assert config.get('crawler.max_pages') == 50
        finally:
            # Cleanup
            os.unlink(temp_file)

    def test_save_config_file(self):
        """Test saving configuration to file"""
        config = ConfigManager()
        config.set('target.url', 'https://save-test.com')

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name

        try:
            # Save config
            config.save(temp_file)

            # Verify file exists and is valid
            assert os.path.exists(temp_file)

            # Load and verify
            with open(temp_file, 'r') as f:
                saved_data = yaml.safe_load(f)

            assert saved_data['target']['url'] == 'https://save-test.com'
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_config_merge_custom_over_default(self):
        """Test custom config overrides default"""
        # Create custom config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'crawler': {
                    'max_pages': 99  # Override default
                }
            }
            yaml.dump(config_data, f)
            temp_file = f.name

        try:
            config = ConfigManager(temp_file)

            # Custom value should override
            assert config.get('crawler.max_pages') == 99

            # Default values should still exist
            assert config.get('crawler.max_depth') == 5
        finally:
            os.unlink(temp_file)


class TestConfigEdgeCases:
    """Test edge cases and error handling"""

    def test_get_with_none_default(self):
        """Test get with None as default"""
        config = ConfigManager()

        result = config.get('nonexistent.key', None)
        assert result is None

    def test_set_none_value(self):
        """Test setting None value"""
        config = ConfigManager()
        config.set('test.key', None)

        assert config.get('test.key') is None

    def test_config_representation(self):
        """Test string representation"""
        config = ConfigManager()
        config.set('target.url', 'https://example.com')

        repr_str = repr(config)
        assert 'ConfigManager' in repr_str
        assert 'example.com' in repr_str

    def test_deep_nested_set(self):
        """Test deeply nested configuration"""
        config = ConfigManager()
        config.set('level1.level2.level3.level4.value', 'deep')

        assert config.get('level1.level2.level3.level4.value') == 'deep'

    def test_set_with_dict_value(self):
        """Test setting dictionary values"""
        config = ConfigManager()
        test_dict = {'key1': 'value1', 'key2': 'value2'}
        config.set('test.dict', test_dict)

        result = config.get('test.dict')
        assert result == test_dict


class TestConfigTypes:
    """Test configuration type handling"""

    def test_set_integer_value(self):
        """Test setting integer values"""
        config = ConfigManager()
        config.set('test.integer', 42)

        assert config.get('test.integer') == 42
        assert isinstance(config.get('test.integer'), int)

    def test_set_float_value(self):
        """Test setting float values"""
        config = ConfigManager()
        config.set('test.float', 3.14)

        assert config.get('test.float') == 3.14
        assert isinstance(config.get('test.float'), float)

    def test_set_boolean_value(self):
        """Test setting boolean values"""
        config = ConfigManager()
        config.set('test.bool_true', True)
        config.set('test.bool_false', False)

        assert config.get('test.bool_true') is True
        assert config.get('test.bool_false') is False

    def test_set_list_value(self):
        """Test setting list values"""
        config = ConfigManager()
        test_list = ['item1', 'item2', 'item3']
        config.set('test.list', test_list)

        assert config.get('test.list') == test_list


@pytest.fixture
def temp_config_file():
    """Fixture for temporary config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            'target': {
                'url': 'https://fixture.com'
            }
        }
        yaml.dump(config_data, f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


class TestConfigWithFixtures:
    """Tests using fixtures"""

    def test_load_from_fixture(self, temp_config_file):
        """Test loading config from fixture"""
        config = ConfigManager(temp_config_file)

        assert config.get('target.url') == 'https://fixture.com'


# Performance tests
class TestConfigPerformance:
    """Test configuration performance"""

    def test_multiple_set_operations_performance(self):
        """Test performance of multiple set operations"""
        config = ConfigManager()

        import time
        start = time.time()

        # Perform 1000 set operations
        for i in range(1000):
            config.set(f'test.key{i}', f'value{i}')

        duration = time.time() - start

        # Should complete in reasonable time (< 1 second)
        assert duration < 1.0

    def test_multiple_get_operations_performance(self):
        """Test performance of multiple get operations"""
        config = ConfigManager()

        # Set up data
        for i in range(100):
            config.set(f'test.key{i}', f'value{i}')

        import time
        start = time.time()

        # Perform 1000 get operations
        for i in range(1000):
            config.get(f'test.key{i % 100}')

        duration = time.time() - start

        # Should complete in reasonable time (< 0.5 seconds)
        assert duration < 0.5


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.config', '--cov-report=html'])
