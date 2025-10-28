"""Jenkins Integration Helper"""


class JenkinsHelper:
    """Jenkins integration helper"""

    @staticmethod
    def generate_jenkinsfile(
        target_url: str = "${TARGET_URL}",
        profile: str = "security"
    ) -> str:
        """Generate Jenkinsfile"""

        jenkinsfile = f'''
pipeline {{
    agent any

    environment {{
        PYTHONUNBUFFERED = '1'
    }}

    stages {{
        stage('Setup') {{
            steps {{
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
                sh '. venv/bin/activate && playwright install --with-deps chromium'
            }}
        }}

        stage('Security Scan') {{
            steps {{
                sh '. venv/bin/activate && python main.py --url {target_url} --profile {profile}'
            }}
        }}

        stage('Publish Reports') {{
            steps {{
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: '*/report.html',
                    reportName: 'WebTestool Report'
                ])
            }}
        }}
    }}

    post {{
        always {{
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
        }}
        failure {{
            emailext (
                subject: "WebTestool Scan Failed: ${{env.JOB_NAME}}",
                body: "Check console output at ${{env.BUILD_URL}}",
                to: "${{env.NOTIFICATION_EMAIL}}"
            )
        }}
    }}
}}
'''
        return jenkinsfile
