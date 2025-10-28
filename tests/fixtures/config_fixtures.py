"""
Test fixtures for configuration testing
"""

import pytest
from pathlib import Path
import tempfile
import yaml


@pytest.fixture
def temp_config_file():
    """Create a temporary config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config = {
            'target': {
                'url': 'https://example.com',
                'timeout': 30
            },
            'modules': {
                'security': {'enabled': True},
                'performance': {'enabled': True}
            },
            'reporting': {
                'output_dir': 'reports',
                'formats': ['html', 'json']
            }
        }
        yaml.dump(config, f)
        yield f.name
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def sample_config():
    """Provide a sample configuration dictionary"""
    return {
        'target': {
            'url': 'https://testsite.com',
            'auth': None,
            'headers': {},
            'cookies': {}
        },
        'crawler': {
            'enabled': True,
            'max_depth': 3,
            'max_pages': 50,
            'delay': 0.5
        },
        'modules': {
            'security': {
                'enabled': True,
                'tests': ['xss', 'sql_injection']
            },
            'performance': {
                'enabled': True,
                'thresholds': {
                    'response_time': 2.0
                }
            }
        }
    }


@pytest.fixture
def invalid_config():
    """Provide an invalid configuration"""
    return {
        'target': {
            # Missing required 'url' field
            'timeout': 'invalid'  # Wrong type
        }
    }
