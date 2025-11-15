"""
Jenkins integration module for AccuDoc.

Provides Jenkins pipeline templates and integration examples
for automated documentation generation in CI/CD workflows.
"""

import logging
from typing import Dict, Optional


def generate_jenkinsfile(
    repo_url: str,
    output_path: str = 'docs/README.md',
    accudoc_version: str = 'main',
    triggers: Optional[Dict] = None
) -> str:
    """
    Generate a Jenkinsfile for AccuDoc integration.
    
    Args:
        repo_url: Repository URL to document
        output_path: Path where documentation should be generated
        accudoc_version: AccuDoc version/branch to use
        triggers: Optional build triggers configuration
        
    Returns:
        Jenkinsfile content as string
    """
    triggers_config = triggers or {
        'pollSCM': 'H/15 * * * *',  # Poll every 15 minutes
        'cron': '@daily'  # Daily build
    }
    
    jenkinsfile = f'''pipeline {{
    agent any
    
    triggers {{
        pollSCM('{triggers_config.get("pollSCM", "H/15 * * * *")}')
        cron('{triggers_config.get("cron", "@daily")}')
    }}
    
    environment {{
        ACCUDOC_VERSION = '{accudoc_version}'
        DOCS_OUTPUT = '{output_path}'
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}
        
        stage('Setup AccuDoc') {{
            steps {{
                script {{
                    sh """
                        if [ ! -d "/tmp/accudoc" ]; then
                            git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
                        else
                            cd /tmp/accudoc && git pull
                        fi
                    """
                }}
            }}
        }}
        
        stage('Generate Documentation') {{
            steps {{
                script {{
                    sh """
                        python3 /tmp/accudoc/accudoc_cli.py export . \\
                            -o ${{DOCS_OUTPUT}} \\
                            --template default
                    """
                }}
            }}
        }}
        
        stage('Archive Documentation') {{
            steps {{
                archiveArtifacts artifacts: 'docs/**/*', fingerprint: true
            }}
        }}
        
        stage('Publish Documentation') {{
            when {{
                branch 'main'
            }}
            steps {{
                // Publish to your documentation hosting service
                // Example: GitHub Pages, GitLab Pages, Netlify, etc.
                echo 'Publishing documentation...'
                
                // Uncomment and configure based on your hosting:
                
                // GitHub Pages:
                // sh 'git checkout gh-pages && cp -r docs/* . && git add . && git commit -m "Update docs" && git push'
                
                // Netlify:
                // sh 'netlify deploy --prod --dir=docs'
                
                // S3:
                // sh 'aws s3 sync docs/ s3://your-bucket/docs/'
            }}
        }}
    }}
    
    post {{
        success {{
            echo 'Documentation generated successfully!'
            emailext (
                subject: "Documentation Updated - Build #${{BUILD_NUMBER}}",
                body: "Documentation has been successfully generated and published.\\n\\nBuild: ${{BUILD_URL}}",
                to: '${{DEFAULT_RECIPIENTS}}'
            )
        }}
        failure {{
            echo 'Documentation generation failed!'
            emailext (
                subject: "Documentation Generation Failed - Build #${{BUILD_NUMBER}}",
                body: "Documentation generation failed. Please check the build logs.\\n\\nBuild: ${{BUILD_URL}}",
                to: '${{DEFAULT_RECIPIENTS}}'
            )
        }}
        always {{
            cleanWs()
        }}
    }}
}}
'''
    return jenkinsfile


def generate_jenkins_shared_library() -> str:
    """
    Generate a Jenkins shared library for AccuDoc.
    
    Returns:
        Groovy code for Jenkins shared library
    """
    return '''// vars/accuDoc.groovy
// Jenkins Shared Library for AccuDoc

def call(Map config = [:]) {{
    def outputPath = config.outputPath ?: 'docs/README.md'
    def template = config.template ?: 'default'
    def format = config.format ?: 'markdown'
    def accudocVersion = config.accudocVersion ?: 'main'
    
    pipeline {{
        agent any
        
        stages {{
            stage('Setup AccuDoc') {{
                steps {{
                    script {{
                        sh """
                            if [ ! -d "/tmp/accudoc" ]; then
                                git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
                                cd /tmp/accudoc && git checkout ${{accudocVersion}}
                            else
                                cd /tmp/accudoc && git pull && git checkout ${{accudocVersion}}
                            fi
                        """
                    }}
                }}
            }}
            
            stage('Generate Documentation') {{
                steps {{
                    script {{
                        sh """
                            python3 /tmp/accudoc/accudoc_cli.py export . \\
                                -o ${{outputPath}} \\
                                --template ${{template}} \\
                                --format ${{format}}
                        """
                    }}
                }}
            }}
            
            stage('Publish') {{
                steps {{
                    archiveArtifacts artifacts: 'docs/**/*', fingerprint: true
                    
                    if (config.publish) {{
                        script {{
                            config.publish()
                        }}
                    }}
                }}
            }}
        }}
    }}
}}

// Example usage in Jenkinsfile:
// @Library('accudoc-library') _
// 
// accuDoc(
//     outputPath: 'docs/README.md',
//     template: 'default',
//     format: 'html',
//     publish: {{
//         sh 'netlify deploy --prod --dir=docs'
//     }}
// )
'''


def generate_jenkins_pipeline_script() -> str:
    """
    Generate a declarative Jenkins pipeline script.
    
    Returns:
        Jenkins pipeline script as string
    """
    return '''// Declarative Pipeline for AccuDoc
pipeline {
    agent {
        docker {
            image 'python:3.9'
            args '-v /tmp:/tmp'
        }
    }
    
    parameters {
        string(name: 'OUTPUT_FORMAT', defaultValue: 'markdown', description: 'Output format (markdown, html, pdf)')
        string(name: 'TEMPLATE', defaultValue: 'default', description: 'Documentation template to use')
        booleanParam(name: 'PUBLISH_DOCS', defaultValue: true, description: 'Publish documentation')
    }
    
    environment {
        ACCUDOC_PATH = '/tmp/accudoc'
        DOCS_DIR = 'docs'
    }
    
    stages {
        stage('Initialize') {
            steps {
                echo "Starting AccuDoc documentation generation..."
                echo "Format: ${params.OUTPUT_FORMAT}"
                echo "Template: ${params.TEMPLATE}"
            }
        }
        
        stage('Install AccuDoc') {{
            steps {{
                sh \'''
                    if [ ! -d "${{ACCUDOC_PATH}}" ]; then
                        git clone https://github.com/jamesellette/AccuDoc.git ${{ACCUDOC_PATH}}
                    fi
                    cd ${{ACCUDOC_PATH}} && git pull origin main
                \'''
            }}
        }}
        
        stage('Scan Repository') {{
            steps {{
                sh \'''
                    mkdir -p ${{DOCS_DIR}}
                    python3 ${{ACCUDOC_PATH}}/accudoc_cli.py scan . -o scan-results.json
                \'''
            }}
        }}
        
        stage('Generate Documentation') {{
            steps {{
                sh """
                    python3 ${{ACCUDOC_PATH}}/accudoc_cli.py generate scan-results.json \\
                        -o ${{DOCS_DIR}}/README.${{params.OUTPUT_FORMAT == 'html' ? 'html' : 'md'}} \\
                        --template ${{params.TEMPLATE}} \\
                        --format ${{params.OUTPUT_FORMAT}}
                """
            }}
        }}
        
        stage('Archive Results') {{
            steps {{
                archiveArtifacts artifacts: "${{DOCS_DIR}}/**/*", fingerprint: true
                archiveArtifacts artifacts: 'scan-results.json', fingerprint: true
            }}
        }}
        
        stage('Publish Documentation') {{
            when {{
                expression {{ params.PUBLISH_DOCS == true }}
                branch 'main'
            }}
            steps {{
                echo 'Publishing documentation...'
                // Add your publishing logic here
                // Examples:
                // - publishHTML (for Jenkins HTML Publisher Plugin)
                // - Deploy to GitHub Pages
                // - Upload to S3
                // - Deploy to Netlify
                
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: "${{DOCS_DIR}}",
                    reportFiles: 'README.html',
                    reportName: 'AccuDoc Documentation'
                ])
            }}
        }}
    }
    
    post {{
        success {{
            echo 'Documentation generation completed successfully!'
            
            // Send notification
            // mail to: 'team@example.com',
            //      subject: "Documentation Updated - ${{env.JOB_NAME}} #${{env.BUILD_NUMBER}}",
            //      body: "Documentation has been successfully generated.\\n\\nView: ${{env.BUILD_URL}}"
        }}
        
        failure {{
            echo 'Documentation generation failed!'
            
            // Send failure notification
            // mail to: 'team@example.com',
            //      subject: "Documentation Generation Failed - ${{env.JOB_NAME}} #${{env.BUILD_NUMBER}}",
            //      body: "Documentation generation failed. Check logs: ${{env.BUILD_URL}}"
        }}
        
        always {{
            // Clean up
            cleanWs(deleteDirs: true)
        }}
    }}
}
'''


def generate_multibranch_pipeline() -> str:
    """
    Generate a multibranch pipeline configuration.
    
    Returns:
        Multibranch Jenkinsfile content
    """
    return '''// Multibranch Pipeline Jenkinsfile
// This file should be placed in the root of your repository

pipeline {{
    agent any
    
    options {{
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }}
    
    environment {{
        ACCUDOC_PATH = '/tmp/accudoc'
        DOCS_DIR = 'docs'
        BRANCH_DOCS_DIR = "${{DOCS_DIR}}/${{env.BRANCH_NAME}}"
    }}
    
    stages {{
        stage('Setup') {{
            steps {{
                echo "Building documentation for branch: ${{env.BRANCH_NAME}}"
                sh 'mkdir -p ${{BRANCH_DOCS_DIR}}'
                
                // Install AccuDoc
                sh \'''
                    if [ ! -d "${{ACCUDOC_PATH}}" ]; then
                        git clone https://github.com/jamesellette/AccuDoc.git ${{ACCUDOC_PATH}}
                    fi
                    cd ${{ACCUDOC_PATH}} && git pull
                \'''
            }}
        }}
        
        stage('Generate Docs') {{
            steps {{
                sh """
                    python3 ${{ACCUDOC_PATH}}/accudoc_cli.py export . \\
                        -o ${{BRANCH_DOCS_DIR}}/README.md \\
                        --template default
                """
            }}
        }}
        
        stage('Branch Comparison') {{
            when {{
                not {{ branch 'main' }}
            }}
            steps {{
                script {{
                    // Generate branch comparison documentation
                    sh """
                        python3 ${{ACCUDOC_PATH}}/accudoc_cli.py compare-branches \\
                            main ${{env.BRANCH_NAME}} \\
                            -o ${{BRANCH_DOCS_DIR}}/BRANCH_COMPARISON.md
                    """
                }}
            }}
        }}
        
        stage('Archive') {{
            steps {{
                archiveArtifacts artifacts: "${{BRANCH_DOCS_DIR}}/**/*", fingerprint: true
            }}
        }}
        
        stage('Deploy') {{
            when {{
                branch 'main'
            }}
            steps {{
                echo 'Deploying main branch documentation...'
                // Add deployment logic here
            }}
        }}
    }}
    
    post {{
        success {{
            echo "Documentation for ${{env.BRANCH_NAME}} generated successfully!"
        }}
        failure {{
            echo "Failed to generate documentation for ${{env.BRANCH_NAME}}"
        }}
    }}
}}
'''


class JenkinsIntegration:
    """Jenkins integration helper class."""
    
    def __init__(self):
        """Initialize Jenkins integration."""
        self.logger = logging.getLogger('accudoc.jenkins')
    
    def generate_configuration(self, config: Dict) -> Dict[str, str]:
        """
        Generate all Jenkins configuration files.
        
        Args:
            config: Configuration dictionary with options
            
        Returns:
            Dictionary with filename as key and content as value
        """
        files = {}
        
        # Generate Jenkinsfile
        files['Jenkinsfile'] = generate_jenkinsfile(
            repo_url=config.get('repo_url', 'https://github.com/user/repo'),
            output_path=config.get('output_path', 'docs/README.md'),
            accudoc_version=config.get('accudoc_version', 'main')
        )
        
        # Generate multibranch pipeline
        if config.get('multibranch', False):
            files['Jenkinsfile.multibranch'] = generate_multibranch_pipeline()
        
        # Generate shared library
        if config.get('shared_library', False):
            files['vars/accuDoc.groovy'] = generate_jenkins_shared_library()
        
        # Generate pipeline script
        if config.get('pipeline_script', True):
            files['pipeline-script.groovy'] = generate_jenkins_pipeline_script()
        
        return files
    
    def save_configurations(self, output_dir: str, config: Dict) -> None:
        """
        Save Jenkins configurations to files.
        
        Args:
            output_dir: Directory to save files
            config: Configuration dictionary
        """
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files = self.generate_configuration(config)
        
        for filename, content in files.items():
            filepath = output_path / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)
            self.logger.info(f"Created {filepath}")
