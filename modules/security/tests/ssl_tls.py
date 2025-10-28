"""SSL/TLS Testing"""

import ssl
import socket
from urllib.parse import urlparse
from core.models import TestContext, Severity
from .base_security_test import BaseSecurityTest


class SSLTLSTest(BaseSecurityTest):
    name = "ssl_tls"
    description = "Tests SSL/TLS configuration"
    config_key = "ssl_tls"

    async def run_test(self, context: TestContext) -> None:
        parsed = urlparse(context.target_url)

        if parsed.scheme != 'https':
            self.add_finding(
                title="No HTTPS",
                description="Website does not use HTTPS encryption",
                severity=Severity.HIGH,
                url=context.target_url,
                cwe_id="CWE-319"
            )
            return

        hostname = parsed.hostname
        port = parsed.port or 443

        try:
            # Check SSL certificate
            ctx = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    version = ssock.version()

                    # Check TLS version
                    if version in ['TLSv1', 'TLSv1.1', 'SSLv2', 'SSLv3']:
                        self.add_finding(
                            title="Weak TLS Version",
                            description=f"Server uses outdated {version}",
                            severity=Severity.HIGH,
                            url=context.target_url,
                            cwe_id="CWE-327"
                        )

        except ssl.SSLCertVerificationError as e:
            self.add_finding(
                title="Invalid SSL Certificate",
                description=f"SSL certificate validation failed: {str(e)}",
                severity=Severity.HIGH,
                url=context.target_url,
                cwe_id="CWE-295"
            )
        except Exception as e:
            pass
