#!/usr/bin/env python3
"""
Demo script for organization-wide features.

Demonstrates:
1. Organization-wide Glossary & Style Standardization
2. Onboarding and Training Path Generator
3. Granular Document Sharing Controls
4. License and Copyright Management Toolkit
"""

import tempfile
import shutil
from pathlib import Path
import json

from accudoc.glossary import GlossaryManager
from accudoc.onboarding_generator import OnboardingGenerator
from accudoc.document_sharing import DocumentSharingManager
from accudoc.license_management import LicenseManagementToolkit
from accudoc.scanner import RepositoryScanner


def demo_glossary():
    """Demonstrate glossary and style standardization."""
    print("\n" + "="*70)
    print("DEMO 1: Organization-wide Glossary & Style Standardization")
    print("="*70)
    
    manager = GlossaryManager()
    
    # Add terms
    print("\n1. Adding glossary terms...")
    term1 = manager.add_term(
        term='API',
        definition='Application Programming Interface',
        preferred_usage='Use "REST API" for our web services',
        aliases=['api', 'interface'],
        deprecated_terms=['web service', 'endpoint'],
        category='technical'
    )
    print(f"   ✓ Added term: {term1.term}")
    
    term2 = manager.add_term(
        term='Repository',
        definition='A storage location for software packages',
        preferred_usage='Use "repository" not "repo"',
        deprecated_terms=['repo', 'code base'],
        category='technical'
    )
    print(f"   ✓ Added term: {term2.term}")
    
    # Add style rule
    print("\n2. Adding style rule...")
    rule = manager.add_style_rule(
        name='avoid-future-tense',
        description='Use present tense instead of future tense',
        pattern=r'\bwill\s+\w+',
        replacement='Use present tense',
        severity='info'
    )
    print(f"   ✓ Added rule: {rule.name}")
    
    # Scan content
    print("\n3. Scanning documentation for violations...")
    test_content = """
    # API Documentation
    
    This web service will provide access to our data.
    You can use the endpoint to retrieve information.
    The repo contains all the source code.
    """
    
    violations = manager.scan_content(test_content)
    print(f"   Found {len(violations)} violations:")
    for v in violations:
        print(f"   - Line {v.line_number}: {v.term} → {v.preferred} [{v.severity}]")
    
    # Generate report
    print("\n4. Generating compliance report...")
    report = manager.generate_report(violations, '/demo/docs')
    print(f"   ✓ Report generated ({len(report)} chars)")
    
    manager.close()


def demo_onboarding():
    """Demonstrate onboarding generator."""
    print("\n" + "="*70)
    print("DEMO 2: Onboarding and Training Path Generator")
    print("="*70)
    
    generator = OnboardingGenerator()
    
    # Simulate repository info
    print("\n1. Analyzing repository structure...")
    repo_info = {
        'name': 'AccuDoc',
        'url': 'https://github.com/user/accudoc',
        'languages': {
            'Python': 85,
            'JavaScript': 10,
            'Shell': 5
        },
        'dependencies': {
            'requirements.txt': ['flask', 'pytest'],
            'package.json': ['express']
        },
        'documentation': {
            'README.md': {},
            'CONTRIBUTING.md': {},
            'docs/': {}
        }
    }
    
    # Create checklist
    print("2. Creating onboarding checklist...")
    checklist = generator.create_checklist(
        repository_path='/demo/accudoc',
        repo_info=repo_info,
        title='AccuDoc Contributor Onboarding'
    )
    print(f"   ✓ Created checklist: {checklist.checklist_id}")
    print(f"   ✓ Total steps: {len(checklist.steps)}")
    print(f"   ✓ Estimated time: {checklist.total_time} minutes")
    
    # Show steps
    print("\n3. Onboarding steps:")
    for i, step in enumerate(checklist.steps[:5], 1):
        print(f"   {i}. {step.title} ({step.category})")
        if step.estimated_time:
            print(f"      Time: ~{step.estimated_time} minutes")
    
    if len(checklist.steps) > 5:
        print(f"   ... and {len(checklist.steps) - 5} more steps")
    
    # Generate markdown guide
    print("\n4. Generating markdown guide...")
    markdown = generator.generate_markdown_guide(checklist)
    print(f"   ✓ Guide generated ({len(markdown)} chars)")
    print("\n   Preview (first 300 chars):")
    print("   " + markdown[:300].replace('\n', '\n   '))
    
    # Assign to user and track progress
    print("\n5. Assigning checklist to user...")
    progress = generator.assign_checklist(checklist.checklist_id, 'user123')
    print(f"   ✓ Assigned to user123")
    print(f"   Progress ID: {progress.progress_id}")
    
    # Update progress
    print("\n6. Marking first step as complete...")
    updated = generator.update_progress(progress.progress_id, checklist.steps[0].step_id)
    print(f"   ✓ Progress: {updated.progress_percentage:.1f}% complete")
    
    generator.close()


def demo_document_sharing():
    """Demonstrate document sharing."""
    print("\n" + "="*70)
    print("DEMO 3: Granular Document Sharing Controls")
    print("="*70)
    
    manager = DocumentSharingManager()
    
    # Share a document
    print("\n1. Sharing documentation section...")
    doc_content = """
# API Reference

## Authentication

Use Bearer tokens for authentication.

## Endpoints

- GET /api/users - List users
- POST /api/users - Create user
"""
    
    shared = manager.share_document_section(
        document_path='/docs/api.md',
        content=doc_content,
        shared_by='user123',
        section_id='authentication',
        section_title='API Authentication Guide',
        expires_in_days=7,
        watermark=True,
        download_limit=10
    )
    print(f"   ✓ Document shared")
    print(f"   Share ID: {shared.share_id}")
    print(f"   Access Token: {shared.access_token[:20]}...")
    print(f"   Expires: {shared.expires_at}")
    print(f"   Download limit: {shared.download_limit}")
    
    # Access shared document
    print("\n2. Accessing shared document...")
    accessed = manager.get_shared_document(
        shared.access_token,
        ip_address='192.168.1.100',
        user_agent='Mozilla/5.0'
    )
    print(f"   ✓ Document accessed")
    print(f"   Section: {accessed.section_title}")
    print(f"   Watermark: {'Yes' if accessed.watermark else 'No'}")
    
    # Record download
    print("\n3. Recording download...")
    success = manager.record_download(shared.share_id)
    print(f"   ✓ Download recorded")
    
    # Get access log
    print("\n4. Viewing access log...")
    log = manager.get_access_log(shared.share_id)
    print(f"   Total accesses: {len(log)}")
    for entry in log:
        print(f"   - {entry.action} at {entry.accessed_at[:19]} from {entry.ip_address}")
    
    # Revoke share
    print("\n5. Revoking share...")
    manager.revoke_share(shared.share_id, 'user123')
    print(f"   ✓ Share revoked")
    
    manager.close()


def demo_license_management():
    """Demonstrate license and copyright management."""
    print("\n" + "="*70)
    print("DEMO 4: License and Copyright Management Toolkit")
    print("="*70)
    
    manager = LicenseManagementToolkit()
    
    # Create copyright header
    print("\n1. Creating copyright header template...")
    header = manager.create_copyright_header(
        organization='Acme Corporation',
        year='2024',
        license_type='MIT',
        file_patterns=['*.py', '*.js']
    )
    print(f"   ✓ Header created: {header.header_id}")
    print("\n   Header text (first 200 chars):")
    print("   " + header.header_text[:200].replace('\n', '\n   '))
    
    # Add attributions
    print("\n2. Adding third-party attributions...")
    attr1 = manager.add_attribution(
        component_name='Flask',
        author='Pallets',
        license='BSD-3-Clause',
        source_url='https://flask.palletsprojects.com',
        description='Lightweight WSGI web application framework'
    )
    print(f"   ✓ Added: {attr1.component_name}")
    
    attr2 = manager.add_attribution(
        component_name='pytest',
        author='pytest-dev',
        license='MIT',
        source_url='https://pytest.org',
        description='Testing framework'
    )
    print(f"   ✓ Added: {attr2.component_name}")
    
    # Generate attribution file
    print("\n3. Generating attribution file...")
    attr_file = manager.generate_attribution_file()
    print(f"   ✓ Attribution file generated ({len(attr_file)} chars)")
    print("\n   Preview (first 300 chars):")
    print("   " + attr_file[:300].replace('\n', '\n   '))
    
    # Create test repo and scan for headers
    print("\n4. Scanning repository for copyright headers...")
    temp_dir = tempfile.mkdtemp()
    try:
        test_file = Path(temp_dir) / 'test.py'
        test_file.write_text('''# Copyright (c) 2024 Test Corp
# Licensed under MIT

def hello():
    pass
''')
        
        results = manager.scan_for_headers(temp_dir)
        print(f"   ✓ Scan complete")
        print(f"   Total files: {results['total_files']}")
        print(f"   Files with headers: {results['files_with_headers']}")
        print(f"   Coverage: {(results['files_with_headers'] / max(results['total_files'], 1) * 100):.1f}%")
    finally:
        shutil.rmtree(temp_dir)
    
    manager.close()


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("AccuDoc Organization-wide Features Demo")
    print("="*70)
    
    try:
        demo_glossary()
        demo_onboarding()
        demo_document_sharing()
        demo_license_management()
        
        print("\n" + "="*70)
        print("All demos completed successfully!")
        print("="*70)
        print("\nKey Features Demonstrated:")
        print("  ✓ Glossary management with violation detection")
        print("  ✓ Automated onboarding checklist generation")
        print("  ✓ Secure document sharing with access control")
        print("  ✓ License and copyright management")
        print("\nAll features integrate with the membership system")
        print("for role-based access control and permissions.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
