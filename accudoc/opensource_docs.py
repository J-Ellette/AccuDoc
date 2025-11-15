"""Open source documentation generators for AccuDoc.

This module generates standard open source project documentation including:
- CONTRIBUTING.md (contributor guidelines)
- Issue templates (bug reports, feature requests)
- CODE_OF_CONDUCT.md
"""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import os


class OpenSourceDocsGenerator:
    """Generator for open source project documentation."""
    
    def __init__(self, repo_info: Dict):
        """
        Initialize the generator.
        
        Args:
            repo_info: Dictionary containing repository information
        """
        self.repo_info = repo_info
        
        # Get repo name from name field, or derive from path
        name = repo_info.get('name', '')
        if not name or name.strip() == '':
            # Derive from path
            path = repo_info.get('path', '.')
            name = os.path.basename(os.path.abspath(path))
        
        self.repo_name = name if name else 'Project'
        self.description = repo_info.get('description', '')
        
    def generate_contributing_guide(self) -> str:
        """
        Generate a CONTRIBUTING.md file.
        
        Returns:
            Content for CONTRIBUTING.md
        """
        # Detect languages and frameworks
        languages_data = self.repo_info.get('languages', {})
        if isinstance(languages_data, dict):
            languages = list(languages_data.keys())
        else:
            languages = languages_data if isinstance(languages_data, list) else []
        
        primary_language = languages[0] if languages else 'the project'
        
        # Detect test framework
        dependencies = self.repo_info.get('dependencies', {})
        has_tests = 'test' in str(dependencies).lower() or any(
            'test' in str(f).lower() for f in self.repo_info.get('files', [])
        )
        
        # Detect package manager
        package_manager = self._detect_package_manager()
        
        content = f"""# Contributing to {self.repo_name}

Thank you for your interest in contributing to {self.repo_name}! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Contact](#contact)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/{self.repo_name}.git
   cd {self.repo_name}
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

We accept contributions in various forms:

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🧪 Test coverage improvements
- 🎨 Code refactoring

## Development Setup

### Prerequisites

"""
        
        # Add language-specific setup
        if 'Python' in languages:
            content += """- Python 3.7 or higher
- pip (Python package manager)

"""
        elif 'JavaScript' in languages or 'TypeScript' in languages:
            content += """- Node.js 14 or higher
- npm or yarn

"""
        elif 'Java' in languages:
            content += """- Java JDK 11 or higher
- Maven or Gradle

"""
        elif 'Go' in languages:
            content += """- Go 1.16 or higher

"""
        
        content += """### Installation

"""
        
        # Add installation instructions based on package manager
        if package_manager:
            if package_manager == 'npm':
                content += """```bash
npm install
```

"""
            elif package_manager == 'pip':
                content += """```bash
pip install -r requirements.txt
```

"""
            elif package_manager == 'maven':
                content += """```bash
mvn install
```

"""
            elif package_manager == 'gradle':
                content += """```bash
./gradlew build
```

"""
            elif package_manager == 'go':
                content += """```bash
go mod download
```

"""
        
        if has_tests:
            content += """### Running Tests

Ensure all tests pass before submitting a pull request:

"""
            if 'Python' in languages:
                content += """```bash
python -m pytest
# or
python -m unittest discover
```

"""
            elif 'JavaScript' in languages or 'TypeScript' in languages:
                content += """```bash
npm test
```

"""
            elif 'Java' in languages:
                content += """```bash
mvn test
# or
./gradlew test
```

"""
            elif 'Go' in languages:
                content += """```bash
go test ./...
```

"""
        
        content += f"""## Coding Guidelines

### Code Style

- Follow the existing code style in the project
- Write clear, readable code with meaningful variable names
- Add comments for complex logic
"""
        
        if 'Python' in languages:
            content += """- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters
"""
        elif 'JavaScript' in languages or 'TypeScript' in languages:
            content += """- Follow ESLint configuration
- Use meaningful variable names
- Prefer const over let when possible
"""
        
        content += """
### Documentation

- Update documentation for any changed functionality
- Add docstrings/comments for new functions and classes
- Update README.md if needed

### Commits

- Write clear, descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference issue numbers when applicable

## Pull Request Process

1. **Update documentation** - Ensure all docs reflect your changes
2. **Add tests** - Add tests for new functionality
3. **Run tests** - Verify all tests pass
4. **Update CHANGELOG** - Add your changes to CHANGELOG.md (if applicable)
5. **Create Pull Request** - Submit your PR with a clear description
6. **Code Review** - Address any feedback from reviewers
7. **Merge** - Once approved, your PR will be merged

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests have been added/updated
- [ ] All tests pass
- [ ] Documentation has been updated
- [ ] Commit messages are clear
- [ ] No merge conflicts

## Reporting Bugs

Found a bug? Please create an issue with:

- **Clear title** - Concise description of the issue
- **Description** - Detailed explanation of the problem
- **Steps to reproduce** - How to replicate the bug
- **Expected behavior** - What should happen
- **Actual behavior** - What actually happens
- **Environment** - OS, version, etc.
- **Screenshots** - If applicable

## Suggesting Features

Have an idea? Create an issue with:

- **Clear title** - Concise feature description
- **Problem** - What problem does this solve?
- **Solution** - Your proposed solution
- **Alternatives** - Other solutions you've considered
- **Additional context** - Any other relevant information

## Contact

- **Issues** - Use GitHub issues for bug reports and features
- **Discussions** - Use GitHub discussions for questions
- **Email** - Contact maintainers directly for sensitive issues

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to {self.repo_name}! 🎉
"""
        
        return content
    
    def generate_issue_template_bug(self) -> str:
        """
        Generate a bug report issue template.
        
        Returns:
            Content for .github/ISSUE_TEMPLATE/bug_report.md
        """
        content = f"""---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

A clear and concise description of what the bug is.

## Steps to Reproduce

Steps to reproduce the behavior:

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

A clear and concise description of what actually happened.

## Screenshots

If applicable, add screenshots to help explain your problem.

## Environment

- **OS**: [e.g., Windows 10, macOS 12.0, Ubuntu 20.04]
- **Version**: [e.g., 1.0.0]
"""
        
        languages_data = self.repo_info.get('languages', {})
        if isinstance(languages_data, dict):
            languages = list(languages_data.keys())
        else:
            languages = languages_data if isinstance(languages_data, list) else []
        
        if 'Python' in languages:
            content += "- **Python Version**: [e.g., 3.9.0]\n"
        elif 'JavaScript' in languages or 'TypeScript' in languages:
            content += "- **Node Version**: [e.g., 16.0.0]\n"
        elif 'Java' in languages:
            content += "- **Java Version**: [e.g., 11]\n"
        elif 'Go' in languages:
            content += "- **Go Version**: [e.g., 1.18]\n"
        
        content += """- **Browser** (if applicable): [e.g., Chrome 95, Firefox 94]

## Additional Context

Add any other context about the problem here.

## Possible Solution

If you have ideas on how to fix this, please share them here.
"""
        
        return content
    
    def generate_issue_template_feature(self) -> str:
        """
        Generate a feature request issue template.
        
        Returns:
            Content for .github/ISSUE_TEMPLATE/feature_request.md
        """
        content = f"""---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description

A clear and concise description of the feature you'd like to see.

## Problem Statement

What problem does this feature solve? Why do you need it?

Example: I'm always frustrated when [...]

## Proposed Solution

A clear and concise description of what you want to happen.

## Alternative Solutions

A clear and concise description of any alternative solutions or features you've considered.

## Use Cases

Describe specific use cases where this feature would be helpful:

1. Use case 1: ...
2. Use case 2: ...
3. Use case 3: ...

## Additional Context

Add any other context, screenshots, mockups, or examples about the feature request here.

## Implementation Ideas

If you have ideas on how this could be implemented, please share them here.

## Priority

How important is this feature to you?

- [ ] Critical - Blocking my work
- [ ] High - Would significantly improve my workflow
- [ ] Medium - Nice to have
- [ ] Low - Just an idea
"""
        
        return content
    
    def generate_code_of_conduct(self) -> str:
        """
        Generate a CODE_OF_CONDUCT.md file based on Contributor Covenant.
        
        Returns:
            Content for CODE_OF_CONDUCT.md
        """
        content = f"""# Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the
  overall community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or
  advances of any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email
  address, without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.
Examples of representing our community include using an official e-mail address,
posting via an official social media account, or acting as an appointed
representative at an online or offline event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement.

All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining
the consequences for any action they deem in violation of this Code of Conduct:

### 1. Correction

**Community Impact**: Use of inappropriate language or other behavior deemed
unprofessional or unwelcome in the community.

**Consequence**: A private, written warning from community leaders, providing
clarity around the nature of the violation and an explanation of why the
behavior was inappropriate. A public apology may be requested.

### 2. Warning

**Community Impact**: A violation through a single incident or series
of actions.

**Consequence**: A warning with consequences for continued behavior. No
interaction with the people involved, including unsolicited interaction with
those enforcing the Code of Conduct, for a specified period of time. This
includes avoiding interactions in community spaces as well as external channels
like social media. Violating these terms may lead to a temporary or
permanent ban.

### 3. Temporary Ban

**Community Impact**: A serious violation of community standards, including
sustained inappropriate behavior.

**Consequence**: A temporary ban from any sort of interaction or public
communication with the community for a specified period of time. No public or
private interaction with the people involved, including unsolicited interaction
with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

### 4. Permanent Ban

**Community Impact**: Demonstrating a pattern of violation of community
standards, including sustained inappropriate behavior, harassment of an
individual, or aggression toward or disparagement of classes of individuals.

**Consequence**: A permanent ban from any sort of public interaction within
the community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.0, available at
https://www.contributor-covenant.org/version/2/0/code_of_conduct.html.

Community Impact Guidelines were inspired by [Mozilla's code of conduct
enforcement ladder](https://github.com/mozilla/diversity).

[homepage]: https://www.contributor-covenant.org

For answers to common questions about this code of conduct, see the FAQ at
https://www.contributor-covenant.org/faq. Translations are available at
https://www.contributor-covenant.org/translations.

## Contact

For questions or concerns about this Code of Conduct, please contact the project maintainers.
"""
        
        return content
    
    def _detect_package_manager(self) -> Optional[str]:
        """Detect the package manager used in the project."""
        files = [f.lower() for f in self.repo_info.get('files', [])]
        
        if 'package.json' in files:
            return 'npm'
        elif 'requirements.txt' in files or 'setup.py' in files or 'pyproject.toml' in files:
            return 'pip'
        elif 'pom.xml' in files:
            return 'maven'
        elif 'build.gradle' in files or 'build.gradle.kts' in files:
            return 'gradle'
        elif 'go.mod' in files:
            return 'go'
        elif 'cargo.toml' in files:
            return 'cargo'
        elif 'composer.json' in files:
            return 'composer'
        
        return None
    
    def generate_all_templates(self, output_dir: str = '.') -> Dict[str, str]:
        """
        Generate all open source documentation templates.
        
        Args:
            output_dir: Directory to write files to
            
        Returns:
            Dictionary mapping file paths to their content
        """
        from pathlib import Path
        import os
        
        templates = {}
        
        # Generate CONTRIBUTING.md
        contributing_path = os.path.join(output_dir, 'CONTRIBUTING.md')
        templates[contributing_path] = self.generate_contributing_guide()
        
        # Generate CODE_OF_CONDUCT.md
        conduct_path = os.path.join(output_dir, 'CODE_OF_CONDUCT.md')
        templates[conduct_path] = self.generate_code_of_conduct()
        
        # Generate issue templates
        issue_template_dir = os.path.join(output_dir, '.github', 'ISSUE_TEMPLATE')
        os.makedirs(issue_template_dir, exist_ok=True)
        
        bug_template_path = os.path.join(issue_template_dir, 'bug_report.md')
        templates[bug_template_path] = self.generate_issue_template_bug()
        
        feature_template_path = os.path.join(issue_template_dir, 'feature_request.md')
        templates[feature_template_path] = self.generate_issue_template_feature()
        
        return templates
    
    def write_all_templates(self, output_dir: str = '.') -> List[str]:
        """
        Generate and write all open source documentation templates to files.
        
        Args:
            output_dir: Directory to write files to
            
        Returns:
            List of file paths that were created
        """
        templates = self.generate_all_templates(output_dir)
        created_files = []
        
        for file_path, content in templates.items():
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(file_path)
        
        return created_files
