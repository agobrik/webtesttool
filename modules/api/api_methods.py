"""
Additional API Testing Methods
GraphQL and WebSocket testing methods for API Module
"""

from loguru import logger
from core.models import TestResult, TestStatus

from .graphql_tester import GraphQLTester
from .websocket_tester import WebSocketTester


async def test_graphql(self, context, config: dict) -> TestResult:
    """Test GraphQL endpoints"""

    test_result = TestResult(
        name="graphql_test",
        description="Tests GraphQL endpoints",
        category=self.category,
        status=TestStatus.RUNNING
    )

    graphql_tester = GraphQLTester(self.config)

    # Look for GraphQL endpoints
    graphql_urls = []

    # Check common GraphQL paths
    common_paths = ['/graphql', '/api/graphql', '/v1/graphql', '/query']

    for path in common_paths:
        test_url = context.target_url.rstrip('/') + path
        graphql_urls.append(test_url)

    # Also check discovered endpoints
    for endpoint in context.api_endpoints:
        if 'graphql' in endpoint.url.lower():
            graphql_urls.append(endpoint.url)

    # Remove duplicates
    graphql_urls = list(set(graphql_urls))

    for url in graphql_urls[:5]:  # Test first 5
        try:
            await graphql_tester.test_graphql_endpoint(url, test_result)
        except Exception as e:
            logger.debug(f"GraphQL test error for {url}: {str(e)}")

    test_result.mark_completed(TestStatus.PASSED)
    return test_result


async def test_websocket(self, context, config: dict) -> TestResult:
    """Test WebSocket endpoints"""

    test_result = TestResult(
        name="websocket_test",
        description="Tests WebSocket connections",
        category=self.category,
        status=TestStatus.RUNNING
    )

    websocket_tester = WebSocketTester(self.config)

    # Look for WebSocket endpoints
    ws_urls = []

    # Check common WebSocket paths
    common_paths = ['/ws', '/websocket', '/socket.io', '/api/ws']

    base_url = context.target_url.replace('http://', 'ws://').replace('https://', 'wss://')

    for path in common_paths:
        test_url = base_url.rstrip('/') + path
        ws_urls.append(test_url)

    # Remove duplicates
    ws_urls = list(set(ws_urls))

    for url in ws_urls[:3]:  # Test first 3
        try:
            await websocket_tester.test_websocket(url, test_result)
        except Exception as e:
            logger.debug(f"WebSocket test error for {url}: {str(e)}")

    test_result.mark_completed(TestStatus.PASSED)
    return test_result
