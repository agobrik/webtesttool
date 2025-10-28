"""
Infrastructure Testing Module
Tests DNS, SSL, HTTP/2, compression, caching, CDN
"""

import ssl
import socket
import httpx
import dns.resolver
from urllib.parse import urlparse
from loguru import logger

from core.module_loader import BaseTestModule
from core.models import (
    Category, ModuleResult, TestResult, TestStatus,
    Finding, Severity, TestContext
)


class InfrastructureModule(BaseTestModule):
    """Infrastructure Testing Module"""

    name = "infrastructure"
    description = "Infrastructure testing: DNS, SSL, HTTP/2, caching, compression"
    category = Category.INFRASTRUCTURE
    version = "1.0.0"

    async def run(self, context: TestContext) -> ModuleResult:
        """Run infrastructure tests"""

        module_result = ModuleResult(
            name=self.name,
            category=self.category,
            status=TestStatus.RUNNING
        )

        module_config = self.config.get_module_config(self.name)

        # DNS Tests
        if module_config.get('dns', {}).get('enabled', True):
            test_result = await self._test_dns(context, module_config)
            module_result.add_test_result(test_result)

        # SSL/TLS Tests
        if module_config.get('ssl', {}).get('enabled', True):
            test_result = await self._test_ssl_advanced(context, module_config)
            module_result.add_test_result(test_result)

        # HTTP Protocol Tests
        if module_config.get('http_protocol', {}).get('enabled', True):
            test_result = await self._test_http_protocol(context, module_config)
            module_result.add_test_result(test_result)

        # Compression Tests
        if module_config.get('compression', {}).get('enabled', True):
            test_result = await self._test_compression(context, module_config)
            module_result.add_test_result(test_result)

        # Caching Tests
        if module_config.get('caching', {}).get('enabled', True):
            test_result = await self._test_caching(context, module_config)
            module_result.add_test_result(test_result)

        # Server Info Tests
        if module_config.get('server_info', {}).get('enabled', True):
            test_result = await self._test_server_info(context, module_config)
            module_result.add_test_result(test_result)

        module_result.mark_completed(TestStatus.PASSED)
        return module_result

    async def _test_dns(self, context: TestContext, config: dict) -> TestResult:
        """Test DNS configuration"""

        test_result = TestResult(
            name="dns_test",
            description="DNS configuration testing",
            category=self.category,
            status=TestStatus.RUNNING
        )

        parsed = urlparse(context.target_url)
        hostname = parsed.hostname

        if not hostname:
            test_result.mark_completed(TestStatus.SKIPPED)
            return test_result

        try:
            # Check A records
            try:
                answers = dns.resolver.resolve(hostname, 'A')
                a_records = [str(rdata) for rdata in answers]
                logger.debug(f"A records for {hostname}: {a_records}")

                if len(a_records) > 1:
                    logger.info(f"Multiple A records found (load balancing): {len(a_records)}")

            except dns.resolver.NXDOMAIN:
                test_result.add_finding(Finding(
                    title="DNS Resolution Failed",
                    description=f"Domain {hostname} does not exist",
                    severity=Severity.CRITICAL,
                    category=self.category,
                    url=context.target_url
                ))
            except Exception as e:
                logger.debug(f"Error resolving A records: {str(e)}")

            # Check AAAA records (IPv6)
            try:
                answers = dns.resolver.resolve(hostname, 'AAAA')
                aaaa_records = [str(rdata) for rdata in answers]
                logger.debug(f"AAAA records: {aaaa_records}")
            except:
                test_result.add_finding(Finding(
                    title="No IPv6 Support",
                    description="Website does not support IPv6 (AAAA records)",
                    severity=Severity.INFO,
                    category=self.category,
                    url=context.target_url
                ))

            # Check MX records
            try:
                answers = dns.resolver.resolve(hostname, 'MX')
                mx_records = [str(rdata) for rdata in answers]
                logger.debug(f"MX records: {mx_records}")
            except:
                pass  # MX records not critical for websites

        except Exception as e:
            logger.error(f"DNS test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_ssl_advanced(self, context: TestContext, config: dict) -> TestResult:
        """Advanced SSL/TLS testing"""

        test_result = TestResult(
            name="ssl_advanced_test",
            description="Advanced SSL/TLS testing",
            category=self.category,
            status=TestStatus.RUNNING
        )

        parsed = urlparse(context.target_url)

        if parsed.scheme != 'https':
            test_result.add_finding(Finding(
                title="No HTTPS",
                description="Website not using HTTPS encryption",
                severity=Severity.CRITICAL,
                category=self.category,
                url=context.target_url,
                cwe_id="CWE-319"
            ))
            test_result.mark_completed(TestStatus.PASSED)
            return test_result

        hostname = parsed.hostname
        port = parsed.port or 443

        try:
            context_ssl = ssl.create_default_context()

            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context_ssl.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()

                    # Check TLS version
                    if version in ['TLSv1', 'TLSv1.1', 'SSLv2', 'SSLv3']:
                        test_result.add_finding(Finding(
                            title="Outdated TLS Version",
                            description=f"Server uses outdated {version}. Recommended: TLS 1.2 or 1.3",
                            severity=Severity.HIGH,
                            category=self.category,
                            url=context.target_url,
                            cwe_id="CWE-327"
                        ))
                    elif version == 'TLSv1.2':
                        logger.info("Using TLS 1.2 (acceptable)")
                    elif version == 'TLSv1.3':
                        logger.info("Using TLS 1.3 (excellent)")

                    # Check cipher suite
                    if cipher:
                        cipher_name = cipher[0]
                        if any(weak in cipher_name.upper() for weak in ['RC4', 'DES', 'MD5', 'NULL', 'EXPORT']):
                            test_result.add_finding(Finding(
                                title="Weak Cipher Suite",
                                description=f"Server uses weak cipher: {cipher_name}",
                                severity=Severity.HIGH,
                                category=self.category,
                                url=context.target_url
                            ))

                    # Check certificate validity
                    if cert:
                        import datetime
                        not_after = cert.get('notAfter')
                        if not_after:
                            # Parse certificate expiry
                            expiry_date = ssl.cert_time_to_seconds(not_after)
                            current_time = datetime.datetime.now().timestamp()

                            days_until_expiry = (expiry_date - current_time) / 86400

                            if days_until_expiry < 0:
                                test_result.add_finding(Finding(
                                    title="Expired SSL Certificate",
                                    description="SSL certificate has expired",
                                    severity=Severity.CRITICAL,
                                    category=self.category,
                                    url=context.target_url
                                ))
                            elif days_until_expiry < 30:
                                test_result.add_finding(Finding(
                                    title="SSL Certificate Expiring Soon",
                                    description=f"Certificate expires in {int(days_until_expiry)} days",
                                    severity=Severity.MEDIUM,
                                    category=self.category,
                                    url=context.target_url
                                ))

        except ssl.SSLCertVerificationError as e:
            test_result.add_finding(Finding(
                title="SSL Certificate Validation Failed",
                description=f"Certificate validation error: {str(e)}",
                severity=Severity.HIGH,
                category=self.category,
                url=context.target_url,
                cwe_id="CWE-295"
            ))
        except Exception as e:
            logger.debug(f"SSL test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_http_protocol(self, context: TestContext, config: dict) -> TestResult:
        """Test HTTP protocol version"""

        test_result = TestResult(
            name="http_protocol_test",
            description="HTTP protocol version testing",
            category=self.category,
            status=TestStatus.RUNNING
        )

        try:
            async with httpx.AsyncClient(http2=True, verify=False) as client:
                response = await client.get(context.target_url)

                # Check if HTTP/2 is supported
                if hasattr(response, 'http_version'):
                    http_version = response.http_version
                    if http_version == 'HTTP/1.1':
                        test_result.add_finding(Finding(
                            title="No HTTP/2 Support",
                            description="Server does not support HTTP/2",
                            severity=Severity.LOW,
                            category=self.category,
                            url=context.target_url
                        ))
                    elif http_version == 'HTTP/2':
                        logger.info("HTTP/2 supported")

        except Exception as e:
            logger.debug(f"HTTP protocol test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_compression(self, context: TestContext, config: dict) -> TestResult:
        """Test compression"""

        test_result = TestResult(
            name="compression_test",
            description="Compression testing",
            category=self.category,
            status=TestStatus.RUNNING
        )

        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(context.target_url)

                encoding = response.headers.get('Content-Encoding', '').lower()

                if not encoding:
                    # Check if content is compressible
                    content_type = response.headers.get('Content-Type', '').lower()
                    if any(ct in content_type for ct in ['text/', 'application/json', 'application/javascript']):
                        test_result.add_finding(Finding(
                            title="No Compression Enabled",
                            description="Compressible content served without gzip/brotli compression",
                            severity=Severity.LOW,
                            category=self.category,
                            url=context.target_url
                        ))
                elif 'gzip' in encoding:
                    logger.info("Gzip compression enabled")
                elif 'br' in encoding:
                    logger.info("Brotli compression enabled (excellent)")

        except Exception as e:
            logger.debug(f"Compression test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_caching(self, context: TestContext, config: dict) -> TestResult:
        """Test caching headers"""

        test_result = TestResult(
            name="caching_test",
            description="Caching headers testing",
            category=self.category,
            status=TestStatus.RUNNING
        )

        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(context.target_url)

                cache_control = response.headers.get('Cache-Control', '')
                expires = response.headers.get('Expires', '')
                etag = response.headers.get('ETag', '')

                if not cache_control and not expires:
                    test_result.add_finding(Finding(
                        title="No Caching Headers",
                        description="No Cache-Control or Expires headers found",
                        severity=Severity.LOW,
                        category=self.category,
                        url=context.target_url
                    ))

        except Exception as e:
            logger.debug(f"Caching test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result

    async def _test_server_info(self, context: TestContext, config: dict) -> TestResult:
        """Test server information disclosure"""

        test_result = TestResult(
            name="server_info_test",
            description="Server information testing",
            category=self.category,
            status=TestStatus.RUNNING
        )

        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(context.target_url)

                # Check Server header
                server = response.headers.get('Server', '')
                if server:
                    # Check if version is disclosed
                    if any(char.isdigit() for char in server):
                        test_result.add_finding(Finding(
                            title="Server Version Disclosure",
                            description=f"Server header discloses version: {server}",
                            severity=Severity.LOW,
                            category=self.category,
                            url=context.target_url,
                            cwe_id="CWE-200"
                        ))

                # Check X-Powered-By header
                powered_by = response.headers.get('X-Powered-By', '')
                if powered_by:
                    test_result.add_finding(Finding(
                        title="Technology Stack Disclosure",
                        description=f"X-Powered-By header reveals: {powered_by}",
                        severity=Severity.LOW,
                        category=self.category,
                        url=context.target_url,
                        cwe_id="CWE-200"
                    ))

        except Exception as e:
            logger.debug(f"Server info test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        return test_result
