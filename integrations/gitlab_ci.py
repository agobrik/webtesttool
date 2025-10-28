"""GitLab CI Integration Helper"""

import yaml


class GitLabCIHelper:
    """GitLab CI/CD integration helper"""

    @staticmethod
    def generate_pipeline(
        target_url: str = "$TARGET_URL",
        profile: str = "security",
        docker_image: str = "python:3.11"
    ) -> str:
        """Generate GitLab CI pipeline YAML"""

        pipeline = {
            'image': docker_image,
            'stages': ['test', 'report'],
            'variables': {
                'PIP_CACHE_DIR': '$CI_PROJECT_DIR/.cache/pip'
            },
            'cache': {
                'paths': ['.cache/pip']
            },
            'before_script': [
                'pip install -r requirements.txt',
                'playwright install --with-deps chromium'
            ],
            'security_scan': {
                'stage': 'test',
                'script': [
                    f'python main.py --url {target_url} --profile {profile}'
                ],
                'artifacts': {
                    'when': 'always',
                    'paths': ['reports/'],
                    'expire_in': '30 days'
                },
                'allow_failure': False
            }
        }

        return yaml.dump(pipeline, default_flow_style=False, sort_keys=False)
