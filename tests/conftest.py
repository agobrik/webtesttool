"""
Pytest configuration and fixtures
Shared fixtures for all tests
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_url():
    """Sample URL for testing"""
    return "https://example.com"


@pytest.fixture
def sample_urls():
    """Sample URLs for testing"""
    return [
        "https://example.com",
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/api/endpoint",
    ]


@pytest.fixture
def sample_html():
    """Sample HTML content"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="Test description">
    </head>
    <body>
        <h1>Test Heading</h1>
        <a href="/page1">Page 1</a>
        <a href="/page2">Page 2</a>
        <form action="/submit" method="post">
            <input type="text" name="username">
            <input type="password" name="password">
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """


@pytest.fixture
def sample_config():
    """Sample configuration dictionary"""
    return {
        'target': {
            'url': 'https://example.com',
            'timeout': 30,
            'headers': {},
            'cookies': {}
        },
        'crawler': {
            'enabled': True,
            'max_depth': 3,
            'max_pages': 100,
            'crawl_delay': 0.5,
            'timeout': 30,
            'concurrent_requests': 10,
            'follow_external': False,
            'exclude_patterns': [],
            'include_patterns': []
        },
        'modules': {
            'security': {
                'enabled': True
            },
            'performance': {
                'enabled': True
            }
        },
        'reporting': {
            'output_dir': 'reports',
            'formats': {'html': {}, 'json': {}},
            'severity_levels': {},
            'include_evidence': True,
            'include_screenshots': True,
            'include_recommendations': True
        },
        'cache': {
            'enabled': False,
            'memory': {'max_size': 1000, 'ttl': 3600},
            'redis': {'enabled': False, 'url': 'redis://localhost:6379'},
            'disk': {'enabled': True, 'directory': '.cache'}
        },
        'advanced': {
            'parallel_execution': True,
            'max_workers': 10,
            'timeout_multiplier': 1.0
        }
    }


@pytest.fixture
def temp_directory(tmp_path):
    """Create temporary directory"""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def temp_config_file(tmp_path, sample_config):
    """Create temporary configuration file"""
    import yaml

    config_file = tmp_path / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)

    return str(config_file)


@pytest.fixture
def invalid_config():
    """Invalid configuration for testing error handling"""
    return {
        'target': {
            'url': ''  # Invalid: empty URL
        },
        'modules': {}  # Invalid: no modules enabled
    }


@pytest.fixture
def sample_scan_result():
    """Sample scan result for testing"""
    from core.models import ScanResult, ModuleResult, TestStatus, Category

    scan_result = ScanResult(
        target_url='https://example.com',
        config={}
    )

    # Add a sample module result
    module_result = ModuleResult(
        name='security',
        category=Category.SECURITY,
        status=TestStatus.PASSED
    )

    scan_result.add_module_result(module_result)
    scan_result.mark_completed(TestStatus.PASSED)

    return scan_result


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    # Reset cache singleton
    import utils.cache
    utils.cache._cache_instance = None

    yield

    # Cleanup after test
    utils.cache._cache_instance = None


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
