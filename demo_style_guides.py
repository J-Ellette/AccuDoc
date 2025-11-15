#!/usr/bin/env python3
"""
Demo script for style guide enforcement feature.

Shows how to use popular style guides to validate documentation quality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.style_guides import (
    get_style_guide,
    list_style_guides,
    GoogleStyleGuide,
    MicrosoftStyleGuide,
    PlainLanguageGuide
)
from accudoc.doc_validator import DocumentationValidator


def demo_list_style_guides():
    """Demo: List available style guides."""
    print("\n" + "="*70)
    print("Demo 1: Available Style Guides")
    print("="*70)
    
    guides = list_style_guides()
    
    print("\nAccuDoc supports the following style guides:\n")
    for guide in guides:
        print(f"📚 {guide['title']}")
        print(f"   ID: {guide['name']}")
        print(f"   {guide['description']}")
        print(f"   Contains {guide['rule_count']} rules\n")


def demo_google_style():
    """Demo: Google Developer Documentation Style Guide."""
    print("\n" + "="*70)
    print("Demo 2: Google Developer Documentation Style Guide")
    print("="*70)
    
    # Sample documentation with Google style violations
    sample_doc = """# Product API Documentation

Please read this documentation carefully!

The API will return JSON responses. We recommend using HTTPS for all requests.

The authentication token will be validated on each request.
"""
    
    print("\n📄 Sample Documentation (with style issues):")
    print("-" * 70)
    print(sample_doc)
    print("-" * 70)
    
    # Create validator with Google style guide
    validator = DocumentationValidator()
    google = GoogleStyleGuide()
    
    print(f"\n📚 Applying {google.name}")
    print(f"   Loading {len(google.get_rules())} rules...")
    
    for rule in google.get_rules():
        validator.add_rule(rule)
    
    # Validate
    print("\n🔍 Validating...")
    issues = validator.validate(sample_doc)
    
    # Show results
    print("\n" + validator.format_report())
    
    print("\n💡 Google Style Tips:")
    print("   • Don't use 'please' - be direct")
    print("   • Use present tense, not future tense")
    print("   • Prefer active voice over passive voice")
    print("   • Use 'you' instead of 'we'")
    print("   • Avoid exclamation marks")


def demo_microsoft_style():
    """Demo: Microsoft Writing Style Guide."""
    print("\n" + "="*70)
    print("Demo 3: Microsoft Writing Style Guide")
    print("="*70)
    
    # Sample documentation with Microsoft style violations
    sample_doc = """# Installation Guide

In order to install the software, you should follow these steps.

Prior to installation, make use of the system check tool due to the fact
that it will verify your configuration.

Don't use the legacy installer, it doesn't work properly.
"""
    
    print("\n📄 Sample Documentation (with style issues):")
    print("-" * 70)
    print(sample_doc)
    print("-" * 70)
    
    # Create validator with Microsoft style guide
    validator = DocumentationValidator()
    microsoft = MicrosoftStyleGuide()
    
    print(f"\n📚 Applying {microsoft.name}")
    print(f"   Loading {len(microsoft.get_rules())} rules...")
    
    for rule in microsoft.get_rules():
        validator.add_rule(rule)
    
    # Validate
    print("\n🔍 Validating...")
    issues = validator.validate(sample_doc)
    
    # Show results
    print("\n" + validator.format_report())
    
    print("\n💡 Microsoft Style Tips:")
    print("   • Be concise - avoid wordy phrases")
    print("   • Use positive phrasing")
    print("   • Replace 'should' with 'must' or 'can'")
    print("   • Use consistent terminology")


def demo_plain_language():
    """Demo: Plain Language Guidelines."""
    print("\n" + "="*70)
    print("Demo 4: Plain Language Guidelines")
    print("="*70)
    
    # Sample documentation with Plain Language violations
    sample_doc = """# System Configuration

In order to commence utilization of the system, you must endeavor to
implement the configuration parameters that will facilitate optimal
performance and ascertain that all prerequisites have been obtained.

The implementation of the configuration should be accomplished by utilizing
the provided tools to demonstrate compliance with the requirements.
"""
    
    print("\n📄 Sample Documentation (with style issues):")
    print("-" * 70)
    print(sample_doc)
    print("-" * 70)
    
    # Create validator with Plain Language guide
    validator = DocumentationValidator()
    plain = PlainLanguageGuide()
    
    print(f"\n📚 Applying {plain.name}")
    print(f"   Loading {len(plain.get_rules())} rules...")
    
    for rule in plain.get_rules():
        validator.add_rule(rule)
    
    # Validate
    print("\n🔍 Validating...")
    issues = validator.validate(sample_doc)
    
    # Show results
    print("\n" + validator.format_report())
    
    print("\n💡 Plain Language Tips:")
    print("   • Use short sentences (< 25 words)")
    print("   • Avoid jargon and technical terms")
    print("   • Use common words instead of complex ones")
    print("   • Use verbs instead of nominalizations")


def demo_combined_guides():
    """Demo: Using multiple style guides together."""
    print("\n" + "="*70)
    print("Demo 5: Combined Style Guides")
    print("="*70)
    
    # Sample documentation
    sample_doc = """# Developer Guide

Please review this guide! In order to utilize the API effectively, we will
demonstrate the implementation process. You should commence by configuring
the authentication parameters.

The system was designed to facilitate the utilization of various endpoints
that will be available for your applications.
"""
    
    print("\n📄 Sample Documentation:")
    print("-" * 70)
    print(sample_doc)
    print("-" * 70)
    
    # Create validator with multiple style guides
    validator = DocumentationValidator()
    
    # Add Google style rules
    google = GoogleStyleGuide()
    print(f"\n📚 Adding {google.name}")
    for rule in google.get_rules():
        validator.add_rule(rule)
    
    # Add Plain Language rules
    plain = PlainLanguageGuide()
    print(f"📚 Adding {plain.name}")
    for rule in plain.get_rules():
        validator.add_rule(rule)
    
    print(f"\n   Total rules loaded: {len(validator.custom_rules)}")
    
    # Validate
    print("\n🔍 Validating...")
    issues = validator.validate(sample_doc)
    
    # Show results
    print("\n" + validator.format_report())
    
    # Show summary by rule type
    print("\n📊 Issue Summary by Rule:")
    rule_counts = {}
    for issue in issues:
        if issue.rule_id:
            rule_counts[issue.rule_id] = rule_counts.get(issue.rule_id, 0) + 1
    
    for rule_id in sorted(rule_counts.keys()):
        print(f"   • {rule_id}: {rule_counts[rule_id]} issue(s)")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("AccuDoc Style Guide Enforcement - Demo")
    print("="*70)
    
    demo_list_style_guides()
    demo_google_style()
    demo_microsoft_style()
    demo_plain_language()
    demo_combined_guides()
    
    print("\n" + "="*70)
    print("✓ Demo Complete!")
    print("="*70)
    print("\nStyle Guide Enforcement helps you:")
    print("  • Follow industry-standard writing guidelines")
    print("  • Improve documentation clarity and professionalism")
    print("  • Maintain consistent style across your docs")
    print("  • Catch common writing mistakes automatically")
    print("\nSupported Style Guides:")
    print("  • Google Developer Documentation Style Guide")
    print("  • Microsoft Writing Style Guide")
    print("  • Plain Language Guidelines")
    print("\nYou can use one guide or combine multiple guides!")
    print("="*70)


if __name__ == '__main__':
    sys.exit(main())
