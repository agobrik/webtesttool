"""
GitHub Actions Integration Helper
Generates GitHub Actions workflow files and provides CI/CD utilities
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class GitHubActionsHelper:
    """GitHub Actions integration helper"""

    @staticmethod
    def generate_workflow(
        name: str = "WebTestool Security Scan",
        target_url: str = "${{ secrets.TARGET_URL }}",
        profile: str = "security",
        on_push: bool = True,
        on_pull_request: bool = True,
        on_schedule: Optional[str] = None,
        fail_on_high: bool = True,
        upload_artifacts: bool = True
    ) -> str:
        """
        Generate GitHub Actions workflow YAML

        Args:
            name: Workflow name
            target_url: Target URL (can use GitHub secrets)
            profile: Test profile to run
            on_push: Trigger on push
            on_pull_request: Trigger on pull request
            on_schedule: Cron schedule (e.g., '0 0 * * *' for daily)
            fail_on_high: Fail workflow if high/critical findings found
            upload_artifacts: Upload reports as artifacts

        Returns:
            YAML workflow content
        """

        workflow = {
            'name': name,
            'on': {}
        }

        # Triggers
        if on_push:
            workflow['on']['push'] = {'branches': ['main', 'master', 'develop']}

        if on_pull_request:
            workflow['on']['pull_request'] = {'branches': ['main', 'master']}

        if on_schedule:
            workflow['on']['schedule'] = [{'cron': on_schedule}]

        # Jobs
        workflow['jobs'] = {
            'security-scan': {
                'runs-on': 'ubuntu-latest',
                'steps': [
                    {
                        'name': 'Checkout code',
                        'uses': 'actions/checkout@v4'
                    },
                    {
                        'name': 'Setup Python',
                        'uses': 'actions/setup-python@v4',
                        'with': {'python-version': '3.11'}
                    },
                    {
                        'name': 'Cache dependencies',
                        'uses': 'actions/cache@v3',
                        'with': {
                            'path': '~/.cache/pip',
                            'key': '${{ runner.os }}-pip-${{ hashFiles(\'**/requirements.txt\') }}',
                            'restore-keys': '${{ runner.os }}-pip-'
                        }
                    },
                    {
                        'name': 'Install WebTestool',
                        'run': 'pip install -r requirements.txt'
                    },
                    {
                        'name': 'Install Playwright browsers',
                        'run': 'python -m playwright install --with-deps chromium'
                    },
                    {
                        'name': 'Run WebTestool scan',
                        'run': f'python main.py --url {target_url} --profile {profile}',
                        'continue-on-error': not fail_on_high
                    }
                ]
            }
        }

        if upload_artifacts:
            workflow['jobs']['security-scan']['steps'].append({
                'name': 'Upload scan reports',
                'uses': 'actions/upload-artifact@v3',
                'if': 'always()',
                'with': {
                    'name': 'security-reports',
                    'path': 'reports/',
                    'retention-days': 30
                }
            })

        # Add quality gate step
        if fail_on_high:
            workflow['jobs']['security-scan']['steps'].append({
                'name': 'Check for critical/high findings',
                'run': '''
                    CRITICAL=$(grep -c "CRITICAL" reports/*/summary.txt || echo 0)
                    HIGH=$(grep -c "HIGH" reports/*/summary.txt || echo 0)

                    echo "Critical findings: $CRITICAL"
                    echo "High findings: $HIGH"

                    if [ "$CRITICAL" -gt "0" ] || [ "$HIGH" -gt "0" ]; then
                      echo "::error::Found $CRITICAL critical and $HIGH high severity findings!"
                      exit 1
                    fi
                ''',
                'shell': 'bash'
            })

        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)

    @staticmethod
    def save_workflow(
        workflow_content: str,
        filename: str = "webtestool-scan.yml",
        workflows_dir: str = ".github/workflows"
    ) -> str:
        """
        Save workflow file to .github/workflows

        Args:
            workflow_content: Workflow YAML content
            filename: Workflow filename
            workflows_dir: Workflows directory

        Returns:
            Path to saved file
        """
        os.makedirs(workflows_dir, exist_ok=True)
        filepath = os.path.join(workflows_dir, filename)

        with open(filepath, 'w') as f:
            f.write(workflow_content)

        return filepath

    @staticmethod
    def create_secrets_template() -> Dict[str, str]:
        """
        Create template for required GitHub secrets

        Returns:
            Dictionary of secret names and descriptions
        """
        return {
            'TARGET_URL': 'URL of the application to test (e.g., https://staging.example.com)',
            'AUTH_USERNAME': 'Username for authenticated testing (optional)',
            'AUTH_PASSWORD': 'Password for authenticated testing (optional)',
            'AUTH_TOKEN': 'Bearer token for API authentication (optional)',
            'SLACK_WEBHOOK_URL': 'Slack webhook URL for notifications (optional)',
            'NOTIFICATION_EMAIL': 'Email address for notifications (optional)'
        }

    @staticmethod
    def generate_pr_comment_workflow() -> str:
        """Generate workflow that comments on PR with scan results"""

        workflow = {
            'name': 'WebTestool PR Comment',
            'on': {
                'pull_request': {
                    'types': ['opened', 'synchronize']
                }
            },
            'jobs': {
                'scan-and-comment': {
                    'runs-on': 'ubuntu-latest',
                    'permissions': {
                        'pull-requests': 'write'
                    },
                    'steps': [
                        {
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '3.11'}
                        },
                        {
                            'name': 'Install and run scan',
                            'run': '''
                                pip install -r requirements.txt
                                python main.py --url ${{ secrets.TARGET_URL }} --profile quick
                            '''
                        },
                        {
                            'name': 'Post comment with results',
                            'uses': 'actions/github-script@v7',
                            'with': {
                                'script': '''
                                    const fs = require('fs');
                                    const summary = fs.readFileSync('reports/scan_*/summary.txt', 'utf8');

                                    github.rest.issues.createComment({
                                      issue_number: context.issue.number,
                                      owner: context.repo.owner,
                                      repo: context.repo.repo,
                                      body: '## WebTestool Scan Results\\n\\n```\\n' + summary + '\\n```'
                                    });
                                '''
                            }
                        }
                    ]
                }
            }
        }

        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
