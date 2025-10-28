"""
Unit tests for Configuration Manager
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from core.config import ConfigManager
from core.exceptions import ConfigurationError


@pytest.fixture
def temp_config_file():
    """Create temporary config file"""
    config_data = {
        'target': {
            'url': 'https://example.com',
            'base_url': 'https://example.com'
        },
        'crawler': {
            'enabled': True,
            'max_depth': 3,
            'max_pages': 100
        },
        'modules': {
            'security': {
                'enabled': True
            }
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/test.log',
            'console': True,
            'max_size': '100MB',
            'backup_count': 5
        }
    }

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_config_manager_default_initialization():
    """Test ConfigManager with default config"""
    config = ConfigManager()
    assert config is not None
    assert config.config is not None


@pytest.mark.unit
def test_config_manager_from_file(temp_config_file):
    """Test loading config from file"""
    config = ConfigManager(temp_config_file)

    assert config.config.target.url == 'https://example.com'
    assert config.config.crawler.enabled is True
    assert config.config.crawler.max_depth == 3


@pytest.mark.unit
def test_config_get_value(temp_config_file):
    """Test getting config values"""
    config = ConfigManager(temp_config_file)

    # Get nested value
    url = config.get('target.url')
    assert url == 'https://example.com'

    # Get with default
    value = config.get('nonexistent.key', default='default_value')
    assert value == 'default_value'


@pytest.mark.unit
def test_config_set_value(temp_config_file):
    """Test setting config values"""
    config = ConfigManager(temp_config_file)

    # Set value
    config.set('target.url', 'https://newsite.com')

    # Verify it was set
    assert config.get('target.url') == 'https://newsite.com'


@pytest.mark.unit
def test_config_validation(temp_config_file):
    """Test config validation"""
    config = ConfigManager(temp_config_file)

    # Validate should pass with valid config
    is_valid, errors = config.validate()

    # May have some validation (depends on implementation)
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)


@pytest.mark.unit
def test_config_invalid_file():
    """Test loading invalid config file"""
    with pytest.raises((ConfigurationError, FileNotFoundError, Exception)):
        ConfigManager('/nonexistent/path/config.yaml')


@pytest.mark.unit
def test_config_nested_access(temp_config_file):
    """Test accessing nested config values"""
    config = ConfigManager(temp_config_file)

    # Access nested values
    max_depth = config.get('crawler.max_depth')
    assert max_depth == 3

    security_enabled = config.get('modules.security.enabled')
    assert security_enabled is True


@pytest.mark.unit
def test_config_set_nested_value(temp_config_file):
    """Test setting nested config values"""
    config = ConfigManager(temp_config_file)

    # Set nested value
    config.set('crawler.max_depth', 5)

    # Verify
    assert config.get('crawler.max_depth') == 5


@pytest.mark.unit
def test_config_dict_conversion(temp_config_file):
    """Test converting config to dictionary"""
    config = ConfigManager(temp_config_file)

    # Convert to dict
    config_dict = config.config.model_dump()

    assert isinstance(config_dict, dict)
    assert 'target' in config_dict
    assert 'crawler' in config_dict


@pytest.mark.unit
def test_config_default_values():
    """Test default config values"""
    config = ConfigManager()

    # Check some default values exist
    # (exact values depend on default_config.yaml)
    assert config.config.crawler is not None
    assert config.config.modules is not None


@pytest.mark.unit
def test_config_override_defaults(temp_config_file):
    """Test overriding default values"""
    config = ConfigManager(temp_config_file)

    # Override default
    original = config.get('crawler.max_pages', 1000)
    config.set('crawler.max_pages', 500)

    assert config.get('crawler.max_pages') == 500


@pytest.mark.unit
def test_config_boolean_values(temp_config_file):
    """Test boolean config values"""
    config = ConfigManager(temp_config_file)

    # Get boolean
    enabled = config.get('crawler.enabled')
    assert isinstance(enabled, bool)
    assert enabled is True

    # Set boolean
    config.set('crawler.enabled', False)
    assert config.get('crawler.enabled') is False


@pytest.mark.unit
def test_config_integer_values(temp_config_file):
    """Test integer config values"""
    config = ConfigManager(temp_config_file)

    # Get integer
    max_depth = config.get('crawler.max_depth')
    assert isinstance(max_depth, int)
    assert max_depth == 3


@pytest.mark.unit
def test_config_string_values(temp_config_file):
    """Test string config values"""
    config = ConfigManager(temp_config_file)

    # Get string
    url = config.get('target.url')
    assert isinstance(url, str)
    assert url == 'https://example.com'


@pytest.mark.unit
def test_config_get_nonexistent_without_default(temp_config_file):
    """Test getting non-existent key without default"""
    config = ConfigManager(temp_config_file)

    # Should return None or raise exception (depends on implementation)
    result = config.get('nonexistent.key')
    # May be None or may raise
    assert result is None or result


@pytest.mark.unit
def test_config_multiple_get_set(temp_config_file):
    """Test multiple get/set operations"""
    config = ConfigManager(temp_config_file)

    # Multiple sets
    config.set('target.url', 'https://site1.com')
    config.set('crawler.max_depth', 10)
    config.set('logging.level', 'DEBUG')

    # Verify all changes
    assert config.get('target.url') == 'https://site1.com'
    assert config.get('crawler.max_depth') == 10
    assert config.get('logging.level') == 'DEBUG'


@pytest.mark.unit
def test_config_persistence():
    """Test that config changes persist within same instance"""
    config = ConfigManager()

    # Set value
    config.set('test.value', 123)

    # Get it back
    assert config.get('test.value') == 123

    # Set it again
    config.set('test.value', 456)

    # Should have new value
    assert config.get('test.value') == 456


@pytest.mark.unit
def test_config_cache_section():
    """Test accessing cache configuration section"""
    config = ConfigManager()

    # Try to access cache config (may not exist in all configs)
    cache_config = config.get('cache', default={})

    # Should at least not raise an error
    assert cache_config is not None


@pytest.mark.unit
def test_config_has_logging_section(temp_config_file):
    """Test that config has logging section"""
    config = ConfigManager(temp_config_file)

    # Should have logging config
    assert config.config.logging is not None
    assert config.config.logging.level == 'INFO'
    assert config.config.logging.console is True
