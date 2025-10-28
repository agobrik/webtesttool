"""
Enhanced notification system with multiple providers
"""

import asyncio
from typing import Dict, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from loguru import logger
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class NotificationProvider(ABC):
    """Base class for notification providers"""

    @abstractmethod
    async def send(self, message: str, **kwargs) -> bool:
        """Send notification"""
        pass


class SlackNotificationProvider(NotificationProvider):
    """
    Slack notification provider

    Example:
        provider = SlackNotificationProvider(webhook_url="https://hooks.slack.com/...")
        await provider.send("Security scan completed", severity="high")
    """

    def __init__(self, webhook_url: str, channel: Optional[str] = None):
        self.webhook_url = webhook_url
        self.channel = channel

    async def send(self, message: str, **kwargs) -> bool:
        """Send Slack notification"""
        severity = kwargs.get('severity', 'info')
        title = kwargs.get('title', 'WebTestool Notification')
        details = kwargs.get('details', {})

        # Color based on severity
        color_map = {
            'critical': '#FF0000',
            'high': '#FF6B6B',
            'medium': '#FFA500',
            'low': '#FFD700',
            'info': '#36A64F'
        }
        color = color_map.get(severity, '#36A64F')

        # Build Slack message
        payload = {
            'text': title,
            'attachments': [{
                'color': color,
                'title': title,
                'text': message,
                'fields': [
                    {'title': key, 'value': str(value), 'short': True}
                    for key, value in details.items()
                ],
                'footer': 'WebTestool',
                'ts': int(datetime.now().timestamp())
            }]
        }

        if self.channel:
            payload['channel'] = self.channel

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                logger.info("Slack notification sent successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False


class EmailNotificationProvider(NotificationProvider):
    """
    Email notification provider

    Example:
        provider = EmailNotificationProvider(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="user@example.com",
            password="password",
            from_address="alerts@example.com"
        )
        await provider.send("Scan completed", to="admin@example.com")
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_address: str,
        use_tls: bool = True
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.use_tls = use_tls

    async def send(self, message: str, **kwargs) -> bool:
        """Send email notification"""
        to_addresses = kwargs.get('to', [])
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]

        subject = kwargs.get('subject', 'WebTestool Notification')
        html = kwargs.get('html', False)

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_address
            msg['To'] = ', '.join(to_addresses)

            # Attach message
            if html:
                part = MIMEText(message, 'html')
            else:
                part = MIMEText(message, 'plain')
            msg.attach(part)

            # Send email
            await asyncio.to_thread(self._send_smtp, msg, to_addresses)

            logger.info(f"Email notification sent to {to_addresses}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

    def _send_smtp(self, msg, to_addresses):
        """Send via SMTP (synchronous)"""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg, self.from_address, to_addresses)


class DiscordNotificationProvider(NotificationProvider):
    """
    Discord notification provider

    Example:
        provider = DiscordNotificationProvider(webhook_url="https://discord.com/api/webhooks/...")
        await provider.send("Scan completed", severity="high")
    """

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, message: str, **kwargs) -> bool:
        """Send Discord notification"""
        severity = kwargs.get('severity', 'info')
        title = kwargs.get('title', 'WebTestool Notification')

        # Color based on severity
        color_map = {
            'critical': 0xFF0000,
            'high': 0xFF6B6B,
            'medium': 0xFFA500,
            'low': 0xFFD700,
            'info': 0x36A64F
        }
        color = color_map.get(severity, 0x36A64F)

        payload = {
            'embeds': [{
                'title': title,
                'description': message,
                'color': color,
                'timestamp': datetime.now().isoformat(),
                'footer': {
                    'text': 'WebTestool'
                }
            }]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                logger.info("Discord notification sent successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False


class WebhookNotificationProvider(NotificationProvider):
    """
    Generic webhook notification provider

    Example:
        provider = WebhookNotificationProvider(url="https://api.example.com/webhook")
        await provider.send("Scan completed", extra_data={"scan_id": "123"})
    """

    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        self.url = url
        self.headers = headers or {}

    async def send(self, message: str, **kwargs) -> bool:
        """Send webhook notification"""
        payload = {
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'source': 'webtestool',
            **kwargs
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                logger.info("Webhook notification sent successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False


class NotificationManager:
    """
    Manage multiple notification providers

    Example:
        manager = NotificationManager()
        manager.add_provider("slack", SlackNotificationProvider(...))
        manager.add_provider("email", EmailNotificationProvider(...))

        await manager.notify_all(
            "Critical vulnerability found!",
            severity="critical",
            details={"url": "https://example.com"}
        )
    """

    def __init__(self):
        self.providers: Dict[str, NotificationProvider] = {}

    def add_provider(self, name: str, provider: NotificationProvider):
        """Add notification provider"""
        self.providers[name] = provider
        logger.info(f"Notification provider '{name}' added")

    async def notify(self, provider_name: str, message: str, **kwargs) -> bool:
        """Send notification via specific provider"""
        if provider_name not in self.providers:
            logger.warning(f"Provider '{provider_name}' not found")
            return False

        return await self.providers[provider_name].send(message, **kwargs)

    async def notify_all(self, message: str, **kwargs) -> Dict[str, bool]:
        """Send notification via all providers"""
        results = {}
        tasks = []

        for name, provider in self.providers.items():
            task = provider.send(message, **kwargs)
            tasks.append((name, task))

        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                logger.error(f"Provider '{name}' failed: {e}")
                results[name] = False

        return results

    async def notify_scan_complete(self, scan_result, **kwargs):
        """Notify about completed scan"""
        summary = scan_result.summary
        severity = 'critical' if summary.get('critical_findings', 0) > 0 else \
                   'high' if summary.get('high_findings', 0) > 0 else \
                   'medium' if summary.get('medium_findings', 0) > 0 else 'info'

        message = f"""
        Security scan completed for {scan_result.target_url}

        Findings:
        - Critical: {summary.get('critical_findings', 0)}
        - High: {summary.get('high_findings', 0)}
        - Medium: {summary.get('medium_findings', 0)}
        - Low: {summary.get('low_findings', 0)}

        Duration: {scan_result.duration}
        """

        return await self.notify_all(
            message,
            title="Security Scan Complete",
            severity=severity,
            details={
                'target': scan_result.target_url,
                'total_findings': summary.get('total_findings', 0),
                'duration': str(scan_result.duration)
            },
            **kwargs
        )
