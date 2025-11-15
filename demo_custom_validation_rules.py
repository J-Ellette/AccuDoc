#!/usr/bin/env python3
"""
Demo script for custom validation rules feature.

Shows how to use custom validation rules to enforce documentation standards.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.doc_validator import (
    DocumentationValidator,
    MaxLineLengthRule,
    RequiredSectionsRule,
    ForbiddenWordsRule,
    CodeBlockLanguageRule
)


def demo_basic_validation():
    """Demo: Basic validation with custom rules."""
    print("\n" + "="*70)
    print("Demo 1: Basic Validation with Custom Rules")
    print("="*70)
    
    # Sample documentation with various issues
    sample_doc = """# Project Documentation

## Overview
This project is simply amazing and so easy to use! You just need to follow these instructions and you'll be up and running in no time. Obviously, this is the best tool available. This is a very long line that exceeds the recommended maximum line length and will trigger a validation warning from the max-line-length rule.

## Installation
Run the following command:
```
pip install project
```

## Features
- Easy to use
- Fast and efficient
"""
    
    # Create validator with custom rules
    validator = DocumentationValidator()
    
    # Add custom rules
    validator.add_rule(MaxLineLengthRule(
        severity='warning',
        config={'max_length': 100}
    ))
    
    validator.add_rule(RequiredSectionsRule(
        severity='error',
        config={'sections': ['Overview', 'Installation', 'Usage', 'License']}
    ))
    
    validator.add_rule(ForbiddenWordsRule(
        severity='warning',
        config={
            'words': ['simply', 'just', 'easy', 'obviously'],
            'case_sensitive': False
        }
    ))
    
    validator.add_rule(CodeBlockLanguageRule(severity='warning'))
    
    print("\n📋 Sample Documentation:")
    print("-" * 70)
    print(sample_doc[:300] + "...")
    
    # Validate
    print("\n🔍 Running validation with custom rules...")
    issues = validator.validate(sample_doc)
    
    # Show results
    print("\n" + validator.format_report())
    
    print("\n📊 Summary:")
    summary = validator.get_summary()
    print(f"  Total issues: {summary['total']}")
    print(f"  Errors: {summary['by_severity']['error']}")
    print(f"  Warnings: {summary['by_severity']['warning']}")
    print(f"  Info: {summary['by_severity']['info']}")


def demo_config_file_validation():
    """Demo: Load rules from configuration file."""
    print("\n" + "="*70)
    print("Demo 2: Load Rules from Configuration File")
    print("="*70)
    
    # Create validator
    validator = DocumentationValidator()
    
    # Load rules from config file
    config_path = Path(__file__).parent / 'examples' / 'validation_rules.yaml'
    
    if config_path.exists():
        print(f"\n📄 Loading rules from: {config_path}")
        validator.load_rules_from_config(config_path)
        
        print(f"\n✓ Loaded {len(validator.custom_rules)} custom rules")
        
        # List loaded rules
        print("\n📋 Loaded Rules:")
        for rule_info in validator.list_rules():
            status = "✓ enabled" if rule_info['enabled'] else "✗ disabled"
            print(f"  {status} [{rule_info['severity'].upper()}] {rule_info['id']}")
            print(f"      {rule_info['description']}")
        
        # Sample doc to validate
        sample_doc = """# test document

## overview
this is the overview.

## installation


Run these commands.

## usage
simply install and run.
"""
        
        print("\n🔍 Validating sample documentation...")
        issues = validator.validate(sample_doc)
        
        print("\n" + validator.format_report())
    else:
        print(f"\n⚠️  Configuration file not found: {config_path}")


def demo_programmatic_rules():
    """Demo: Create and use custom rules programmatically."""
    print("\n" + "="*70)
    print("Demo 3: Programmatic Rule Creation")
    print("="*70)
    
    # Create specific rules for a project
    print("\n🔧 Creating project-specific validation rules...")
    
    validator = DocumentationValidator()
    
    # API documentation must have specific sections
    validator.add_rule(RequiredSectionsRule(
        severity='error',
        config={
            'sections': [
                'Overview',
                'Installation',
                'API Reference',
                'Examples',
                'Contributing',
                'License'
            ]
        }
    ))
    
    # Enforce professional language
    validator.add_rule(ForbiddenWordsRule(
        severity='warning',
        config={
            'words': [
                'basically', 'simply', 'just', 'easy', 'trivial',
                'obviously', 'clearly', 'of course', 'duh'
            ],
            'case_sensitive': False
        }
    ))
    
    # Strict line length for readability
    validator.add_rule(MaxLineLengthRule(
        severity='info',
        config={'max_length': 80}
    ))
    
    print("\n✓ Created 3 custom rules for API documentation")
    
    # Show rules
    print("\n📋 Active Rules:")
    for rule_info in validator.list_rules():
        print(f"  [{rule_info['severity'].upper()}] {rule_info['id']}")
        print(f"      {rule_info['description']}")
    
    # Validate a sample API doc
    api_doc = """# MyAPI Documentation

## Overview
MyAPI is a simple REST API for data processing.

## Installation
Just run pip install myapi.

## API Reference
Obviously, the API is easy to use.
"""
    
    print("\n🔍 Validating API documentation...")
    issues = validator.validate(api_doc)
    
    print("\n" + validator.format_report())


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("AccuDoc Custom Validation Rules - Demo")
    print("="*70)
    
    demo_basic_validation()
    demo_config_file_validation()
    demo_programmatic_rules()
    
    print("\n" + "="*70)
    print("✓ Demo Complete!")
    print("="*70)
    print("\nCustom validation rules allow you to:")
    print("  • Enforce project-specific documentation standards")
    print("  • Check for required sections and content")
    print("  • Detect discouraged words or phrases")
    print("  • Validate formatting and style")
    print("  • Load rules from configuration files")
    print("  • Create rules programmatically")
    print("\nSee examples/validation_rules.yaml for configuration examples.")
    print("="*70)


if __name__ == '__main__':
    sys.exit(main())
