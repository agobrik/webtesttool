"""
Notification System
Sends notifications via email, Slack, webhooks, etc.
"""

import asyncio
import httpx
from typing import Dict, Any
from datetime import datetime
from loguru import logger

from .models import ScanResult


class Notifier:
    """
    Multi-channel notification system
    Supports email, Slack, Discord, webhooks, and more
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Notifier

        Args:
            config: Notification configuration
        """
        self.config = config
        self.enabled = config.get('enabled', False)

    async def send_scan_complete(self, scan_result: ScanResult) -> None:
        """
        Send scan completion notification

        Args:
            scan_result: Completed scan result
        """
        if not self.enabled:
            return

        # Prepare notification data
        notification_data = self._prepare_notification_data(scan_result)

        # Send to all configured channels
        tasks = []

        if self.config.get('email', {}).get('enabled', False):
            tasks.append(self._send_email(notification_data))

        if self.config.get('slack', {}).get('enabled', False):
            tasks.append(self._send_slack(notification_data))

        if self.config.get('discord', {}).get('enabled', False):
            tasks.append(self._send_discord(notification_data))

        if self.config.get('webhook', {}).get('enabled', False):
            tasks.append(self._send_webhook(notification_data))

        if self.config.get('teams', {}).get('enabled', False):
            tasks.append(self._send_teams(notification_data))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _prepare_notification_data(self, scan_result: ScanResult) -> Dict[str, Any]:
        """Prepare notification data from scan result"""

        summary = scan_result.summary

        return {
            'target_url': scan_result.target_url,
            'scan_id': scan_result.id,
            'start_time': scan_result.start_time.isoformat(),
            'end_time': scan_result.end_time.isoformat() if scan_result.end_time else None,
            'duration': scan_result.duration,
            'status': scan_result.status.value,
            'total_findings': summary.get('total_findings', 0),
            'critical': summary.get('critical_findings', 0),
            'high': summary.get('high_findings', 0),
            'medium': summary.get('medium_findings', 0),
            'low': summary.get('low_findings', 0),
            'info': summary.get('info_findings', 0),
            'urls_crawled': summary.get('urls_crawled', 0),
            'timestamp': datetime.now().isoformat()
        }

    async def _send_email(self, data: Dict[str, Any]) -> None:
        """Send email notification"""

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            email_config = self.config.get('email', {})

            smtp_host = email_config.get('smtp_host')
            smtp_port = email_config.get('smtp_port', 587)
            username = email_config.get('username')
            password = email_config.get('password')
            recipients = email_config.get('recipients', [])

            if not all([smtp_host, username, password, recipients]):
                logger.error("Email configuration incomplete")
                return

            # Create message
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"WebTestool Scan Complete: {data['target_url']}"

            # Create HTML body
            body = f"""
            <html>
            <body>
                <h2>WebTestool Scan Complete</h2>
                <p><strong>Target:</strong> {data['target_url']}</p>
                <p><strong>Status:</strong> {data['status']}</p>
                <p><strong>Duration:</strong> {data['duration']:.2f} seconds</p>

                <h3>Findings Summary</h3>
                <ul>
                    <li>🔴 Critical: {data['critical']}</li>
                    <li>🟠 High: {data['high']}</li>
                    <li>🟡 Medium: {data['medium']}</li>
                    <li>🟢 Low: {data['low']}</li>
                    <li>ℹ️ Info: {data['info']}</li>
                </ul>

                <p><strong>Total Findings:</strong> {data['total_findings']}</p>
                <p><strong>URLs Crawled:</strong> {data['urls_crawled']}</p>

                <p><em>Scan ID: {data['scan_id']}</em></p>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

            logger.info(f"Email notification sent to {len(recipients)} recipients")

        except Exception as e:
            logger.error(f"Email notification error: {str(e)}")

    async def _send_slack(self, data: Dict[str, Any]) -> None:
        """Send Slack notification"""

        try:
            slack_config = self.config.get('slack', {})
            webhook_url = slack_config.get('webhook_url')

            if not webhook_url:
                logger.error("Slack webhook URL not configured")
                return

            # Determine color based on severity
            color = 'danger' if data['critical'] > 0 else 'warning' if data['high'] > 0 else 'good'

            # Create Slack message
            message = {
                'text': f"WebTestool Scan Complete: {data['target_url']}",
                'attachments': [
                    {
                        'color': color,
                        'fields': [
                            {'title': 'Target', 'value': data['target_url'], 'short': True},
                            {'title': 'Status', 'value': data['status'], 'short': True},
                            {'title': 'Duration', 'value': f"{data['duration']:.2f}s", 'short': True},
                            {'title': 'Total Findings', 'value': str(data['total_findings']), 'short': True},
                            {'title': 'Critical', 'value': f"🔴 {data['critical']}", 'short': True},
                            {'title': 'High', 'value': f"🟠 {data['high']}", 'short': True},
                            {'title': 'Medium', 'value': f"🟡 {data['medium']}", 'short': True},
                            {'title': 'Low', 'value': f"🟢 {data['low']}", 'short': True},
                        ],
                        'footer': f"Scan ID: {data['scan_id']}",
                        'ts': int(datetime.now().timestamp())
                    }
                ]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=message)

                if response.status_code == 200:
                    logger.info("Slack notification sent")
                else:
                    logger.error(f"Slack notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Slack notification error: {str(e)}")

    async def _send_discord(self, data: Dict[str, Any]) -> None:
        """Send Discord notification"""

        try:
            discord_config = self.config.get('discord', {})
            webhook_url = discord_config.get('webhook_url')

            if not webhook_url:
                logger.error("Discord webhook URL not configured")
                return

            # Determine color based on severity
            color = 0xFF0000 if data['critical'] > 0 else 0xFFA500 if data['high'] > 0 else 0x00FF00

            # Create Discord embed
            message = {
                'embeds': [
                    {
                        'title': "WebTestool Scan Complete",
                        'description': f"Target: {data['target_url']}",
                        'color': color,
                        'fields': [
                            {'name': 'Status', 'value': data['status'], 'inline': True},
                            {'name': 'Duration', 'value': f"{data['duration']:.2f}s", 'inline': True},
                            {'name': 'Total Findings', 'value': str(data['total_findings']), 'inline': True},
                            {'name': '🔴 Critical', 'value': str(data['critical']), 'inline': True},
                            {'name': '🟠 High', 'value': str(data['high']), 'inline': True},
                            {'name': '🟡 Medium', 'value': str(data['medium']), 'inline': True},
                            {'name': '🟢 Low', 'value': str(data['low']), 'inline': True},
                            {'name': 'ℹ️ Info', 'value': str(data['info']), 'inline': True},
                        ],
                        'footer': {'text': f"Scan ID: {data['scan_id']}"},
                        'timestamp': data['timestamp']
                    }
                ]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=message)

                if response.status_code in [200, 204]:
                    logger.info("Discord notification sent")
                else:
                    logger.error(f"Discord notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Discord notification error: {str(e)}")

    async def _send_webhook(self, data: Dict[str, Any]) -> None:
        """Send custom webhook notification"""

        try:
            webhook_config = self.config.get('webhook', {})
            webhook_url = webhook_config.get('url')

            if not webhook_url:
                logger.error("Webhook URL not configured")
                return

            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=data)

                if response.status_code in [200, 201, 202]:
                    logger.info("Webhook notification sent")
                else:
                    logger.error(f"Webhook notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Webhook notification error: {str(e)}")

    async def _send_teams(self, data: Dict[str, Any]) -> None:
        """Send Microsoft Teams notification"""

        try:
            teams_config = self.config.get('teams', {})
            webhook_url = teams_config.get('webhook_url')

            if not webhook_url:
                logger.error("Teams webhook URL not configured")
                return

            # Determine color based on severity
            theme_color = 'FF0000' if data['critical'] > 0 else 'FFA500' if data['high'] > 0 else '00FF00'

            # Create Teams message
            message = {
                '@type': 'MessageCard',
                '@context': 'https://schema.org/extensions',
                'summary': f"WebTestool Scan Complete: {data['target_url']}",
                'themeColor': theme_color,
                'title': 'WebTestool Scan Complete',
                'sections': [
                    {
                        'activityTitle': data['target_url'],
                        'activitySubtitle': f"Scan completed in {data['duration']:.2f} seconds",
                        'facts': [
                            {'name': 'Status', 'value': data['status']},
                            {'name': 'Total Findings', 'value': str(data['total_findings'])},
                            {'name': 'Critical', 'value': str(data['critical'])},
                            {'name': 'High', 'value': str(data['high'])},
                            {'name': 'Medium', 'value': str(data['medium'])},
                            {'name': 'Low', 'value': str(data['low'])},
                            {'name': 'URLs Crawled', 'value': str(data['urls_crawled'])},
                        ]
                    }
                ]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=message)

                if response.status_code == 200:
                    logger.info("Teams notification sent")
                else:
                    logger.error(f"Teams notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Teams notification error: {str(e)}")
