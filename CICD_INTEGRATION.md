# CI/CD Integration Guide for AccuDoc

Complete guide for integrating AccuDoc into your CI/CD pipelines for automated documentation generation.

## Overview

AccuDoc integrates seamlessly with popular CI/CD platforms to automatically generate and deploy documentation whenever your code changes. This guide covers setup for:

- GitHub Actions
- GitLab CI/CD
- Jenkins
- Docker-based workflows
- Custom integrations

## GitHub Actions

### Basic Workflow

Create `.github/workflows/docs.yml` in your repository:

```yaml
name: Generate Documentation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  docs:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install AccuDoc
        run: git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
      
      - name: Generate Documentation
        run: |
          python /tmp/accudoc/accudoc_cli.py export . \
            -o docs/README.md \
            --template default
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: docs/
```

### Advanced Workflow with Multiple Formats

```yaml
name: Documentation Pipeline

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install AccuDoc
        run: git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
      
      - name: Scan Repository
        run: |
          python /tmp/accudoc/accudoc_cli.py scan . \
            -o scan-results.json
      
      - name: Generate Markdown Docs
        run: |
          mkdir -p docs
          python /tmp/accudoc/accudoc_cli.py generate scan-results.json \
            -o docs/README.md --template default
          python /tmp/accudoc/accudoc_cli.py generate scan-results.json \
            -o docs/API.md --template api
      
      - name: Generate HTML Docs
        run: |
          python /tmp/accudoc/accudoc_cli.py generate scan-results.json \
            -o docs/index.html --format html --theme dark
      
      - name: Check Links
        run: |
          python /tmp/accudoc/accudoc_cli.py check-links docs/ \
            --format markdown -o docs/link-report.md
      
      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

### Workflow with Caching

```yaml
name: Fast Documentation with Cache

on:
  push:
    branches: [ main ]

jobs:
  docs:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Cache AccuDoc Scan Results
        uses: actions/cache@v3
        with:
          path: .accudoc_cache
          key: accudoc-${{ hashFiles('**/*.py', '**/*.js', '**/*.java') }}
          restore-keys: |
            accudoc-
      
      - name: Install AccuDoc
        run: git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
      
      - name: Generate Documentation
        run: |
          python /tmp/accudoc/accudoc_cli.py export . \
            -o docs/README.md
```

## GitLab CI/CD

### Basic Pipeline

Create `.gitlab-ci.yml` in your repository:

```yaml
stages:
  - docs
  - deploy

generate_docs:
  stage: docs
  image: python:3.9
  before_script:
    - git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
  script:
    - python /tmp/accudoc/accudoc_cli.py export . -o docs/README.md
  artifacts:
    paths:
      - docs/
    expire_in: 1 week

pages:
  stage: deploy
  dependencies:
    - generate_docs
  script:
    - mv docs public
  artifacts:
    paths:
      - public
  only:
    - main
```

### Advanced Pipeline with Multiple Stages

```yaml
stages:
  - scan
  - generate
  - test
  - deploy

variables:
  DOCS_DIR: "docs"

scan_repository:
  stage: scan
  image: python:3.9
  before_script:
    - git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
  script:
    - python /tmp/accudoc/accudoc_cli.py scan . -o scan-results.json
  artifacts:
    paths:
      - scan-results.json
    expire_in: 1 day

generate_markdown:
  stage: generate
  image: python:3.9
  dependencies:
    - scan_repository
  before_script:
    - git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
  script:
    - mkdir -p $DOCS_DIR
    - python /tmp/accudoc/accudoc_cli.py generate scan-results.json -o $DOCS_DIR/README.md
    - python /tmp/accudoc/accudoc_cli.py generate scan-results.json -o $DOCS_DIR/API.md --template api
  artifacts:
    paths:
      - $DOCS_DIR/
    expire_in: 1 week

generate_html:
  stage: generate
  image: python:3.9
  dependencies:
    - scan_repository
  before_script:
    - git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
  script:
    - mkdir -p $DOCS_DIR
    - python /tmp/accudoc/accudoc_cli.py generate scan-results.json -o $DOCS_DIR/index.html --format html --theme dark
  artifacts:
    paths:
      - $DOCS_DIR/
    expire_in: 1 week

test_links:
  stage: test
  image: python:3.9
  dependencies:
    - generate_markdown
    - generate_html
  before_script:
    - git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
  script:
    - python /tmp/accudoc/accudoc_cli.py check-links $DOCS_DIR/ --format markdown -o link-report.md
  artifacts:
    paths:
      - link-report.md
    when: always

pages:
  stage: deploy
  dependencies:
    - generate_markdown
    - generate_html
  script:
    - mv $DOCS_DIR public
  artifacts:
    paths:
      - public
  only:
    - main
```

## Jenkins

### Declarative Pipeline

Create `Jenkinsfile` in your repository:

```groovy
pipeline {
    agent any
    
    environment {
        ACCUDOC_PATH = '/tmp/accudoc'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'git clone https://github.com/jamesellette/AccuDoc.git ${ACCUDOC_PATH}'
            }
        }
        
        stage('Generate Documentation') {
            steps {
                sh 'python3 ${ACCUDOC_PATH}/accudoc_cli.py export . -o docs/README.md'
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'docs/**', fingerprint: true
            }
        }
    }
}
```

### Advanced Pipeline with Parallel Stages

```groovy
pipeline {
    agent any
    
    environment {
        ACCUDOC_PATH = '/tmp/accudoc'
    }
    
    stages {
        stage('Setup') {
            steps {
                git 'https://github.com/jamesellette/AccuDoc.git'
                sh 'git clone https://github.com/jamesellette/AccuDoc.git ${ACCUDOC_PATH}'
            }
        }
        
        stage('Scan') {
            steps {
                sh 'python3 ${ACCUDOC_PATH}/accudoc_cli.py scan . -o scan-results.json'
                stash includes: 'scan-results.json', name: 'scan'
            }
        }
        
        stage('Generate') {
            parallel {
                stage('Markdown') {
                    steps {
                        unstash 'scan'
                        sh '''
                            mkdir -p docs
                            python3 ${ACCUDOC_PATH}/accudoc_cli.py generate scan-results.json -o docs/README.md
                            python3 ${ACCUDOC_PATH}/accudoc_cli.py generate scan-results.json -o docs/API.md --template api
                        '''
                    }
                }
                stage('HTML') {
                    steps {
                        unstash 'scan'
                        sh 'mkdir -p docs && python3 ${ACCUDOC_PATH}/accudoc_cli.py generate scan-results.json -o docs/index.html --format html --theme dark'
                    }
                }
            }
        }
        
        stage('Test') {
            steps {
                sh 'python3 ${ACCUDOC_PATH}/accudoc_cli.py check-links docs/ --format markdown -o link-report.md'
            }
        }
        
        stage('Publish') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'docs',
                    reportFiles: 'index.html',
                    reportName: 'Documentation'
                ])
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'docs/**,link-report.md', fingerprint: true
        }
    }
}
```

## Docker-Based Workflows

### Using AccuDoc Docker Image

```bash
# Build the image
docker build -t accudoc https://github.com/jamesellette/AccuDoc.git

# Generate documentation
docker run -v $(pwd):/repos -v $(pwd)/docs:/output \
  accudoc export /repos -o /output/README.md

# With custom template
docker run -v $(pwd):/repos -v $(pwd)/docs:/output \
  accudoc export /repos -o /output/docs.html \
    --format html --theme dark --template detailed
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  accudoc:
    build: https://github.com/jamesellette/AccuDoc.git
    volumes:
      - .:/repos
      - ./docs:/output
    command: export /repos -o /output/README.md
```

Run with:
```bash
docker-compose up
```

### GitLab CI with Docker

```yaml
generate_docs:
  stage: docs
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t accudoc https://github.com/jamesellette/AccuDoc.git
    - docker run -v $CI_PROJECT_DIR:/repos -v $CI_PROJECT_DIR/docs:/output accudoc export /repos -o /output/README.md
  artifacts:
    paths:
      - docs/
```

## CircleCI

Create `.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  generate-docs:
    docker:
      - image: python:3.9
    steps:
      - checkout
      - run:
          name: Install AccuDoc
          command: git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc
      - run:
          name: Generate Documentation
          command: |
            python /tmp/accudoc/accudoc_cli.py export . -o docs/README.md
      - store_artifacts:
          path: docs/
      - persist_to_workspace:
          root: .
          paths:
            - docs

workflows:
  documentation:
    jobs:
      - generate-docs
```

## Travis CI

Create `.travis.yml`:

```yaml
language: python
python:
  - "3.9"

install:
  - git clone https://github.com/jamesellette/AccuDoc.git /tmp/accudoc

script:
  - python /tmp/accudoc/accudoc_cli.py export . -o docs/README.md

deploy:
  provider: pages
  skip_cleanup: true
  github_token: $GITHUB_TOKEN
  local_dir: docs
  on:
    branch: main
```

## Batch Processing in CI/CD

Create `batch-config.json`:

```json
{
  "repositories": [
    {
      "path": "./service-a",
      "output": "docs/service-a.md",
      "template": "api"
    },
    {
      "path": "./service-b",
      "output": "docs/service-b.md",
      "template": "api"
    },
    {
      "path": "./shared-lib",
      "output": "docs/shared-lib.md",
      "template": "default"
    }
  ]
}
```

Then in your CI/CD pipeline:

```bash
python /tmp/accudoc/accudoc_cli.py batch batch-config.json
```

## Best Practices

1. **Use Caching**
   - Cache AccuDoc scan results between builds
   - Only regenerate when source files change

2. **Separate Stages**
   - Scan once, generate multiple formats
   - Enables faster iterations and parallel processing

3. **Validate Documentation**
   - Use `check-links` command to validate links
   - Fail builds on broken internal links

4. **Version Documentation**
   - Tag documentation with git tags/branches
   - Keep historical documentation versions

5. **Optimize for Performance**
   - Use `--no-cache` flag for clean builds
   - Enable caching for incremental updates
   - Use quiet mode (`-q`) to reduce output

6. **Artifact Management**
   - Archive generated documentation
   - Set appropriate expiry times
   - Store scan results for reuse

## Troubleshooting

### Issue: Slow CI builds

**Solution**: Enable caching
```yaml
- uses: actions/cache@v3
  with:
    path: .accudoc_cache
    key: accudoc-${{ hashFiles('**/*.py') }}
```

### Issue: Out of memory errors

**Solution**: Use Docker with memory limits
```bash
docker run -m 2g accudoc export /repos -o /output/docs.md
```

### Issue: Broken links in generated docs

**Solution**: Add link checking step
```bash
python accudoc_cli.py check-links docs/ || exit 1
```

## Examples Repository

For more examples and templates, visit:
https://github.com/jamesellette/AccuDoc/tree/main/github-workflows

---

*AccuDoc - Automate your documentation in every pipeline*
