"""
WebSocket Testing Module
Tests WebSocket connections and real-time communication
"""

import asyncio
import json
from loguru import logger

from core.models import TestResult, Finding, Severity, Category


class WebSocketTester:
    """WebSocket Connection Tester"""

    def __init__(self, config):
        self.config = config
        self.timeout = 10

    async def test_websocket(self, url: str, test_result: TestResult) -> None:
        """
        Test WebSocket endpoint

        Args:
            url: WebSocket URL (ws:// or wss://)
            test_result: TestResult to add findings to
        """
        try:
            import websockets
        except ImportError:
            logger.warning("websockets library not installed. Install with: pip install websockets")
            return

        # Convert http(s) to ws(s)
        ws_url = url.replace('http://', 'ws://').replace('https://', 'wss://')

        # Test basic connection
        await self._test_connection(ws_url, test_result)

        # Test authentication
        await self._test_auth(ws_url, test_result)

        # Test message handling
        await self._test_messages(ws_url, test_result)

        # Test vulnerabilities
        await self._test_vulnerabilities(ws_url, test_result)

    async def _test_connection(self, url: str, test_result: TestResult) -> None:
        """Test basic WebSocket connection"""

        try:
            import websockets

            async with websockets.connect(url, timeout=self.timeout) as websocket:
                logger.info(f"WebSocket connection established: {url}")

                # Send ping
                await websocket.ping()

                # Try to receive a message
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    logger.debug(f"Received message: {message[:100]}")
                except asyncio.TimeoutError:
                    logger.debug("No initial message received")

        except Exception as e:
            logger.debug(f"WebSocket connection error: {str(e)}")

    async def _test_auth(self, url: str, test_result: TestResult) -> None:
        """Test WebSocket authentication"""

        try:
            import websockets

            # Try to connect without authentication
            try:
                async with websockets.connect(url, timeout=self.timeout) as websocket:
                    # Send a message without auth
                    await websocket.send(json.dumps({'type': 'test', 'data': 'test'}))

                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        # Connection allowed without auth - potential issue
                        test_result.add_finding(Finding(
                            title="WebSocket Missing Authentication",
                            description="WebSocket connection allows unauthenticated access",
                            severity=Severity.MEDIUM,
                            category=Category.API,
                            url=url,
                            cwe_id="CWE-306"
                        ))
                    except asyncio.TimeoutError:
                        pass

            except Exception as e:
                logger.debug(f"WebSocket auth test error: {str(e)}")

        except ImportError:
            pass

    async def _test_messages(self, url: str, test_result: TestResult) -> None:
        """Test WebSocket message handling"""

        try:
            import websockets

            async with websockets.connect(url, timeout=self.timeout) as websocket:
                # Test different message types
                test_messages = [
                    '{"type": "test"}',
                    'invalid json',
                    '{"type": "' + 'A' * 10000 + '"}',  # Large message
                    '{}',
                    'null',
                ]

                for msg in test_messages:
                    try:
                        await websocket.send(msg)
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.debug(f"Message test error: {str(e)}")

        except Exception as e:
            logger.debug(f"WebSocket message test error: {str(e)}")

    async def _test_vulnerabilities(self, url: str, test_result: TestResult) -> None:
        """Test for WebSocket vulnerabilities"""

        # Test for message flooding (DoS)
        await self._test_message_flooding(url, test_result)

        # Test for injection in messages
        await self._test_message_injection(url, test_result)

    async def _test_message_flooding(self, url: str, test_result: TestResult) -> None:
        """Test for message flooding DoS"""

        try:
            import websockets

            async with websockets.connect(url, timeout=self.timeout) as websocket:
                # Send many messages rapidly
                for i in range(100):
                    try:
                        await websocket.send(json.dumps({'index': i}))
                    except Exception as e:
                        logger.debug(f"Flooding test error: {str(e)}")
                        break

                # If all messages were accepted, might be vulnerable to flooding
                test_result.add_finding(Finding(
                    title="WebSocket Message Rate Not Limited",
                    description="WebSocket endpoint does not appear to rate limit messages",
                    severity=Severity.LOW,
                    category=Category.API,
                    url=url
                ))

        except Exception as e:
            logger.debug(f"Message flooding test error: {str(e)}")

    async def _test_message_injection(self, url: str, test_result: TestResult) -> None:
        """Test for injection vulnerabilities in WebSocket messages"""

        try:
            import websockets

            injection_payloads = [
                '{"cmd": "\'; DROP TABLE users--"}',
                '{"data": "<script>alert(\'XSS\')</script>"}',
                '{"input": "../../etc/passwd"}',
            ]

            async with websockets.connect(url, timeout=self.timeout) as websocket:
                for payload in injection_payloads:
                    try:
                        await websocket.send(payload)
                        await asyncio.sleep(0.5)
                    except Exception:
                        pass

        except Exception as e:
            logger.debug(f"Injection test error: {str(e)}")
