# Custom Validation Rules

AccuDoc now supports custom validation rules that allow you to enforce project-specific documentation standards and quality requirements.

## Overview

Custom validation rules extend AccuDoc's built-in documentation validation to check for:
- Required documentation sections
- Maximum line lengths
- Forbidden or discouraged words/phrases
- Heading capitalization styles
- Code block language specifications
- Consecutive blank lines
- And more...

## Quick Start

### Using Built-in Rules

```python
from accudoc.doc_validator import (
    DocumentationValidator,
    MaxLineLengthRule,
    RequiredSectionsRule,
    ForbiddenWordsRule
)

# Create validator
validator = DocumentationValidator()

# Add custom rules
validator.add_rule(MaxLineLengthRule(
    severity='warning',
    config={'max_length': 100}
))

validator.add_rule(RequiredSectionsRule(
    severity='error',
    config={'sections': ['Overview', 'Installation', 'Usage']}
))

# Validate documentation
issues = validator.validate(documentation_content)

# View results
print(validator.format_report())
```

### Using Configuration Files

Create a `validation_rules.yaml` file:

```yaml
validation_rules:
  - type: max-line-length
    enabled: true
    severity: warning
    config:
      max_length: 120

  - type: required-sections
    enabled: true
    severity: error
    config:
      sections:
        - Overview
        - Installation
        - Usage
        - License

  - type: forbidden-words
    enabled: true
    severity: warning
    config:
      words:
        - simply
        - just
        - easy
      case_sensitive: false
```

Then load the rules:

```python
from pathlib import Path
from accudoc.doc_validator import DocumentationValidator

validator = DocumentationValidator()
validator.load_rules_from_config(Path('validation_rules.yaml'))
issues = validator.validate(documentation_content)
```

## Built-in Rule Types

### 1. MaxLineLengthRule

Enforces maximum line length for readability.

**Configuration:**
```yaml
- type: max-line-length
  severity: warning  # or error, info
  config:
    max_length: 120  # Maximum characters per line
```

**Example Issues:**
- "Line exceeds maximum length (150 > 120)"

### 2. RequiredSectionsRule

Ensures documentation contains required sections.

**Configuration:**
```yaml
- type: required-sections
  severity: error
  config:
    sections:
      - Overview
      - Installation
      - Usage
      - Contributing
      - License
```

**Example Issues:**
- "Missing required section: 'Usage'"

### 3. ForbiddenWordsRule

Detects discouraged words or phrases that may indicate unprofessional or unclear writing.

**Configuration:**
```yaml
- type: forbidden-words
  severity: warning
  config:
    words:
      - simply
      - just
      - easy
      - obviously
      - basically
      - clearly
    case_sensitive: false
```

**Example Issues:**
- "Discouraged word found: 'simply'"

**Why avoid these words?**
- "simply", "just", "easy" - What's simple for you may not be simple for others
- "obviously", "clearly" - If it were obvious, you wouldn't need to document it
- "basically" - Often adds no value to the explanation

### 4. NoConsecutiveBlankLinesRule

Prevents excessive blank lines that can make documentation harder to read.

**Configuration:**
```yaml
- type: no-consecutive-blanks
  severity: info
  config:
    max_consecutive: 1  # Maximum consecutive blank lines
```

**Example Issues:**
- "Too many consecutive blank lines (3)"

### 5. HeadingCapitalizationRule

Enforces consistent heading capitalization style.

**Configuration:**
```yaml
- type: heading-capitalization
  severity: info
  config:
    style: title  # Options: title, sentence, upper, lower
```

**Styles:**
- `title`: Title Case (First Letter of Major Words Capitalized)
- `sentence`: Sentence case (First letter capitalized)
- `upper`: UPPER CASE
- `lower`: lower case

**Example Issues:**
- "Heading should use Title Case"

### 6. CodeBlockLanguageRule

Requires language specification for code blocks to enable proper syntax highlighting.

**Configuration:**
```yaml
- type: code-block-language
  severity: warning
  config: {}
```

**Example Issues:**
- "Code block missing language specification"

**Good:**
````markdown
```python
print("Hello, World!")
```
````

**Bad:**
````markdown
```
print("Hello, World!")
```
````

## Rule Severities

Each rule can have one of three severity levels:

- **`error`**: Critical issues that should block documentation publication
- **`warning`**: Issues that should be fixed but don't block publication
- **`info`**: Informational issues or style suggestions

## Programmatic Usage

### Adding Rules Dynamically

```python
from accudoc.doc_validator import (
    DocumentationValidator,
    MaxLineLengthRule,
    ForbiddenWordsRule
)

validator = DocumentationValidator()

# Add rules with custom configuration
validator.add_rule(MaxLineLengthRule(
    severity='warning',
    config={'max_length': 80}
))

validator.add_rule(ForbiddenWordsRule(
    severity='info',
    config={
        'words': ['TODO', 'FIXME', 'XXX'],
        'case_sensitive': True
    }
))

# Validate
issues = validator.validate(content)
```

### Listing Active Rules

```python
# Get information about loaded rules
rules = validator.list_rules()

for rule in rules:
    print(f"{rule['id']}: {rule['description']}")
    print(f"  Severity: {rule['severity']}")
    print(f"  Enabled: {rule['enabled']}")
```

### Getting Validation Summary

```python
# Run validation
issues = validator.validate(content)

# Get summary statistics
summary = validator.get_summary()

print(f"Total issues: {summary['total']}")
print(f"Errors: {summary['by_severity']['error']}")
print(f"Warnings: {summary['by_severity']['warning']}")
print(f"Info: {summary['by_severity']['info']}")

print(f"Custom rule issues: {summary['by_category']['custom']}")
```

### Formatting Reports

```python
# Run validation
validator.validate(content)

# Generate formatted report
report = validator.format_report()
print(report)
```

## Creating Custom Rules

You can create your own custom validation rules by extending the `ValidationRule` base class:

```python
from accudoc.doc_validator import ValidationRule, ValidationIssue

class MyCustomRule(ValidationRule):
    """Custom rule to check for specific patterns."""
    
    def __init__(self, severity='warning', enabled=True, config=None):
        super().__init__('my-custom-rule', severity, enabled, config)
        # Load custom configuration
        self.pattern = self.config.get('pattern', 'default')
    
    @property
    def description(self) -> str:
        return f"Custom validation for pattern: {self.pattern}"
    
    def validate(self, content: str) -> List[ValidationIssue]:
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Your validation logic here
            if self._check_condition(line):
                issues.append(ValidationIssue(
                    severity=self.severity,
                    category='custom',
                    message='Custom rule violation found',
                    line_number=line_num,
                    context=line.strip(),
                    rule_id=self.rule_id
                ))
        
        return issues
    
    def _check_condition(self, line: str) -> bool:
        # Implement your validation logic
        return False

# Use your custom rule
validator = DocumentationValidator()
validator.add_rule(MyCustomRule(config={'pattern': 'my-pattern'}))
```

## Best Practices

### 1. Start with Sensible Defaults

Begin with lenient rules and gradually tighten them:

```yaml
validation_rules:
  - type: max-line-length
    severity: info  # Start with info, upgrade to warning later
    config:
      max_length: 120  # Be generous initially

  - type: required-sections
    severity: warning  # Not error initially
    config:
      sections:
        - Overview
        - Installation
```

### 2. Use Project-Specific Configurations

Different projects have different needs:

```yaml
# API documentation project
validation_rules:
  - type: required-sections
    config:
      sections:
        - Overview
        - Authentication
        - Endpoints
        - Error Codes
        - Rate Limiting

# Tutorial project
validation_rules:
  - type: required-sections
    config:
      sections:
        - Introduction
        - Prerequisites
        - Step-by-Step Guide
        - Troubleshooting
```

### 3. Balance Strictness with Practicality

Avoid overly strict rules that create friction:

```yaml
# Too strict - hard to satisfy
- type: forbidden-words
  config:
    words: [is, are, was, were, be, been]  # Don't do this!

# Better - target specific problematic phrases
- type: forbidden-words
  config:
    words: [simply, just, easy, obviously, clearly]
```

### 4. Document Your Rules

Create a `VALIDATION_RULES.md` in your project explaining why each rule exists:

```markdown
# Project Validation Rules

## max-line-length (120 characters)
We enforce a 120-character limit to ensure code examples remain
readable without horizontal scrolling on standard displays.

## required-sections
All documentation must include Overview, Installation, and Usage
sections to help users get started quickly.

## forbidden-words
We avoid words like "simply" and "just" because they can make
users feel inadequate when they find something difficult.
```

## Examples

See these files for complete examples:
- `examples/validation_rules.yaml` - Example configuration file
- `demo_custom_validation_rules.py` - Demo script showing usage
- `test_custom_validation_rules.py` - Test suite with examples

## Integration

### With AccuDoc CLI

Custom validation rules can be integrated into the AccuDoc CLI workflow:

```bash
# Generate documentation
python accudoc_cli.py generate /path/to/repo

# Validate with custom rules (future feature)
python accudoc_cli.py validate /path/to/repo --rules validation_rules.yaml
```

### With CI/CD

Add validation to your CI/CD pipeline:

```yaml
# .github/workflows/docs.yml
name: Documentation Quality

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Validate Documentation
        run: |
          python accudoc_cli.py generate . --output docs/
          python validate_docs.py docs/ --rules .accudoc/validation_rules.yaml
```

## API Reference

### Classes

- **`ValidationRule`**: Base class for custom validation rules
- **`ValidationIssue`**: Represents a validation issue
- **`DocumentationValidator`**: Main validator class

### Methods

- **`validator.add_rule(rule)`**: Add a custom rule
- **`validator.load_rules_from_config(path)`**: Load rules from YAML/JSON
- **`validator.validate(content)`**: Run validation
- **`validator.get_summary()`**: Get issue summary
- **`validator.format_report()`**: Generate formatted report
- **`validator.list_rules()`**: List loaded rules

## Troubleshooting

### Rules Not Loading

If rules aren't being applied:

1. Check that the configuration file exists and is valid YAML/JSON
2. Verify the rule type names match exactly
3. Ensure `enabled: true` is set for each rule
4. Check for syntax errors in the configuration

### False Positives

If rules are triggering incorrectly:

1. Adjust rule configuration (e.g., increase max_length)
2. Change severity from error to warning or info
3. Disable specific rules with `enabled: false`
4. Create custom rules with more specific logic

### Performance

For large documents:

1. Disable expensive rules during development
2. Use `apply_custom_rules=False` to skip custom rules
3. Validate only changed sections
4. Cache validation results

## Future Enhancements

Planned improvements to custom validation rules:

- More built-in rule types
- Rule templates for common use cases
- Integration with style guides (Google, Microsoft, etc.)
- AI-powered rules for content quality
- Visual rule builder/editor
- Rule marketplace for sharing

## Contributing

To contribute new built-in rules:

1. Extend the `ValidationRule` class
2. Add the rule to `doc_validator.py`
3. Update `_create_rule()` method
4. Add tests to `test_custom_validation_rules.py`
5. Document the rule in this file
6. Submit a pull request

## License

Custom validation rules are part of AccuDoc and share the same license.
