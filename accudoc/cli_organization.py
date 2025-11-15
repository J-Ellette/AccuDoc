"""
CLI commands for organization-wide features.

Adds CLI support for glossary, onboarding, sharing, and license management.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from accudoc.glossary import GlossaryManager
from accudoc.onboarding_generator import OnboardingGenerator
from accudoc.document_sharing import DocumentSharingManager
from accudoc.license_management import LicenseManagementToolkit
from accudoc.scanner import RepositoryScanner


def add_organization_commands(subparsers):
    """
    Add organization-wide feature commands to CLI.
    
    Args:
        subparsers: Argparse subparsers object
    """
    
    # Glossary command
    glossary_parser = subparsers.add_parser('glossary',
                                            help='Manage organization-wide glossary')
    glossary_subparsers = glossary_parser.add_subparsers(dest='glossary_action',
                                                         help='Glossary action')
    
    # Add term
    glossary_add = glossary_subparsers.add_parser('add', help='Add glossary term')
    glossary_add.add_argument('term', help='Term to add')
    glossary_add.add_argument('definition', help='Term definition')
    glossary_add.add_argument('usage', help='Preferred usage example')
    glossary_add.add_argument('--aliases', help='Comma-separated aliases')
    glossary_add.add_argument('--deprecated', help='Comma-separated deprecated terms')
    glossary_add.add_argument('--category', help='Category')
    glossary_add.add_argument('--org-id', help='Organization ID')
    
    # List terms
    glossary_list = glossary_subparsers.add_parser('list', help='List glossary terms')
    glossary_list.add_argument('--org-id', help='Organization ID')
    glossary_list.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Scan content
    glossary_scan = glossary_subparsers.add_parser('scan', help='Scan content for violations')
    glossary_scan.add_argument('path', help='File or directory to scan')
    glossary_scan.add_argument('--org-id', help='Organization ID')
    glossary_scan.add_argument('-o', '--output', help='Output file')
    
    # Onboarding command
    onboarding_parser = subparsers.add_parser('onboarding',
                                             help='Generate onboarding guides')
    onboarding_subparsers = onboarding_parser.add_subparsers(dest='onboarding_action',
                                                             help='Onboarding action')
    
    # Create checklist
    onboarding_create = onboarding_subparsers.add_parser('create',
                                                         help='Create onboarding checklist')
    onboarding_create.add_argument('repository', help='Repository path')
    onboarding_create.add_argument('-o', '--output', help='Output file')
    onboarding_create.add_argument('--title', help='Custom title')
    onboarding_create.add_argument('--org-id', help='Organization ID')
    onboarding_create.add_argument('--format', choices=['markdown', 'checklist', 'json'],
                                   default='markdown', help='Output format')
    
    # Share command
    share_parser = subparsers.add_parser('share',
                                        help='Share documentation sections')
    share_subparsers = share_parser.add_subparsers(dest='share_action',
                                                   help='Share action')
    
    # Create share
    share_create = share_subparsers.add_parser('create', help='Create document share')
    share_create.add_argument('document', help='Document path')
    share_create.add_argument('--section', help='Section ID')
    share_create.add_argument('--title', help='Section title')
    share_create.add_argument('--expires', type=int, help='Expiration in days')
    share_create.add_argument('--watermark', action='store_true', help='Add watermark')
    share_create.add_argument('--limit', type=int, help='Download limit')
    share_create.add_argument('--user-id', required=True, help='User ID')
    
    # List shares
    share_list = share_subparsers.add_parser('list', help='List shares')
    share_list.add_argument('--user-id', required=True, help='User ID')
    share_list.add_argument('--active-only', action='store_true', help='Only show active shares')
    
    # Revoke share
    share_revoke = share_subparsers.add_parser('revoke', help='Revoke a share')
    share_revoke.add_argument('share_id', help='Share ID to revoke')
    share_revoke.add_argument('--user-id', required=True, help='User ID')
    
    # License command
    license_parser = subparsers.add_parser('license',
                                          help='Manage licenses and copyright')
    license_subparsers = license_parser.add_subparsers(dest='license_action',
                                                      help='License action')
    
    # Create header
    license_header = license_subparsers.add_parser('header', help='Create copyright header')
    license_header.add_argument('organization', help='Organization name')
    license_header.add_argument('year', help='Copyright year')
    license_header.add_argument('license_type', help='License type (MIT, Apache-2.0, etc.)')
    license_header.add_argument('--patterns', help='Comma-separated file patterns')
    
    # Apply headers
    license_apply = license_subparsers.add_parser('apply', help='Apply copyright headers')
    license_apply.add_argument('repository', help='Repository path')
    license_apply.add_argument('header_id', help='Header template ID')
    
    # Scan headers
    license_scan = license_subparsers.add_parser('scan', help='Scan for copyright headers')
    license_scan.add_argument('repository', help='Repository path')
    license_scan.add_argument('-o', '--output', help='Output file')
    
    # Add attribution
    license_attr = license_subparsers.add_parser('attribution', help='Add attribution')
    license_attr.add_argument('component', help='Component name')
    license_attr.add_argument('author', help='Author/organization')
    license_attr.add_argument('license', help='License type')
    license_attr.add_argument('--url', help='Source URL')
    license_attr.add_argument('--project-id', help='Project ID')
    
    # Generate attribution file
    license_attr_file = license_subparsers.add_parser('attribution-file',
                                                     help='Generate attribution file')
    license_attr_file.add_argument('-o', '--output', help='Output file')
    license_attr_file.add_argument('--project-id', help='Project ID')
    
    # Check compliance
    license_check = license_subparsers.add_parser('check', help='Check license compliance')
    license_check.add_argument('repository', help='Repository path')
    license_check.add_argument('-o', '--output', help='Output file')


def handle_glossary_command(args):
    """Handle glossary commands."""
    manager = GlossaryManager()
    
    try:
        if args.glossary_action == 'add':
            # Add term
            term = manager.add_term(
                term=args.term,
                definition=args.definition,
                preferred_usage=args.usage,
                aliases=args.aliases.split(',') if args.aliases else None,
                deprecated_terms=args.deprecated.split(',') if args.deprecated else None,
                category=args.category,
                organization_id=args.org_id
            )
            print(f"✓ Term added: {term.term_id}")
            return 0
            
        elif args.glossary_action == 'list':
            # List terms
            terms = manager.get_terms(args.org_id)
            
            if args.json:
                print(json.dumps([{
                    'term': t.term,
                    'definition': t.definition,
                    'category': t.category
                } for t in terms], indent=2))
            else:
                print(f"\nGlossary Terms ({len(terms)}):")
                for term in terms:
                    print(f"\n{term.term}:")
                    print(f"  Definition: {term.definition}")
                    print(f"  Usage: {term.preferred_usage}")
                    if term.category:
                        print(f"  Category: {term.category}")
            return 0
            
        elif args.glossary_action == 'scan':
            # Scan for violations
            path = Path(args.path)
            
            if path.is_file():
                content = path.read_text(encoding='utf-8', errors='ignore')
                violations = manager.scan_content(content, args.org_id)
                report = manager.generate_report(violations, str(path))
            else:
                # Scan directory
                all_violations = []
                for file in path.rglob('*.md'):
                    content = file.read_text(encoding='utf-8', errors='ignore')
                    violations = manager.scan_content(content, args.org_id)
                    all_violations.extend(violations)
                report = manager.generate_report(all_violations, str(path))
            
            if args.output:
                Path(args.output).write_text(report)
                print(f"✓ Report saved to: {args.output}")
            else:
                print(report)
            return 0
            
    finally:
        manager.close()
    
    return 1


def handle_onboarding_command(args):
    """Handle onboarding commands."""
    generator = OnboardingGenerator()
    
    try:
        if args.onboarding_action == 'create':
            # Scan repository
            scanner = RepositoryScanner(args.repository)
            repo_info = scanner.scan()
            
            # Create checklist
            checklist = generator.create_checklist(
                repository_path=args.repository,
                repo_info=repo_info,
                title=args.title,
                organization_id=args.org_id
            )
            
            # Generate output
            if args.format == 'markdown':
                content = generator.generate_markdown_guide(checklist)
            elif args.format == 'checklist':
                content = generator.generate_interactive_checklist(checklist)
            else:  # json
                content = json.dumps({
                    'checklist_id': checklist.checklist_id,
                    'title': checklist.title,
                    'steps': [{
                        'title': s.title,
                        'description': s.description,
                        'category': s.category,
                        'required': s.required
                    } for s in (checklist.steps or [])]
                }, indent=2)
            
            if args.output:
                Path(args.output).write_text(content)
                print(f"✓ Onboarding guide saved to: {args.output}")
            else:
                print(content)
            
            return 0
            
    finally:
        generator.close()
    
    return 1


def handle_share_command(args):
    """Handle document sharing commands."""
    manager = DocumentSharingManager()
    
    try:
        if args.share_action == 'create':
            # Read document content
            content = Path(args.document).read_text(encoding='utf-8')
            
            # Create share
            shared = manager.share_document_section(
                document_path=args.document,
                content=content,
                shared_by=args.user_id,
                section_id=args.section,
                section_title=args.title,
                expires_in_days=args.expires,
                watermark=args.watermark,
                download_limit=args.limit
            )
            
            print(f"✓ Document shared successfully")
            print(f"  Share ID: {shared.share_id}")
            print(f"  Access Token: {shared.access_token}")
            if shared.expires_at:
                print(f"  Expires: {shared.expires_at}")
            return 0
            
        elif args.share_action == 'list':
            # List user's shares
            shares = manager.get_user_shares(args.user_id, args.active_only)
            
            print(f"\nShares for {args.user_id} ({len(shares)}):")
            for share in shares:
                status = "Active" if share.is_active else "Inactive"
                print(f"\n{share.share_id} [{status}]:")
                print(f"  Document: {share.document_path}")
                if share.section_title:
                    print(f"  Section: {share.section_title}")
                print(f"  Downloads: {share.download_count}/{share.download_limit or '∞'}")
            return 0
            
        elif args.share_action == 'revoke':
            # Revoke share
            success = manager.revoke_share(args.share_id, args.user_id)
            if success:
                print(f"✓ Share {args.share_id} revoked")
                return 0
            else:
                print(f"✗ Failed to revoke share")
                return 1
                
    finally:
        manager.close()
    
    return 1


def handle_license_command(args):
    """Handle license management commands."""
    manager = LicenseManagementToolkit()
    
    try:
        if args.license_action == 'header':
            # Create header
            patterns = args.patterns.split(',') if args.patterns else None
            header = manager.create_copyright_header(
                organization=args.organization,
                year=args.year,
                license_type=args.license_type,
                file_patterns=patterns
            )
            print(f"✓ Header template created: {header.header_id}")
            print(f"\n{header.header_text}")
            return 0
            
        elif args.license_action == 'apply':
            # Apply headers
            results = manager.bulk_apply_headers(args.repository, args.header_id)
            print(f"\nCopyright Header Application Results:")
            print(f"  Processed: {results['total_processed']}")
            print(f"  Headers Added: {results['headers_added']}")
            print(f"  Already Had Header: {results['already_had_header']}")
            print(f"  Failed: {results['failed']}")
            return 0
            
        elif args.license_action == 'scan':
            # Scan for headers
            results = manager.scan_for_headers(args.repository)
            
            output = f"""
License Header Scan Results:
  Total Files: {results['total_files']}
  Files with Headers: {results['files_with_headers']}
  Missing Headers: {len(results['missing_headers'])}
  
Coverage: {(results['files_with_headers'] / results['total_files'] * 100):.1f}%
"""
            if args.output:
                Path(args.output).write_text(output)
                print(f"✓ Scan results saved to: {args.output}")
            else:
                print(output)
            return 0
            
        elif args.license_action == 'attribution':
            # Add attribution
            attr = manager.add_attribution(
                component_name=args.component,
                author=args.author,
                license=args.license,
                source_url=args.url,
                project_id=args.project_id
            )
            print(f"✓ Attribution added: {attr.attribution_id}")
            return 0
            
        elif args.license_action == 'attribution-file':
            # Generate attribution file
            content = manager.generate_attribution_file(args.project_id)
            
            if args.output:
                Path(args.output).write_text(content)
                print(f"✓ Attribution file saved to: {args.output}")
            else:
                print(content)
            return 0
            
        elif args.license_action == 'check':
            # Check compliance
            results = manager.check_license_compliance(args.repository)
            
            output = f"""
License Compliance Check:
  Project License: {results['project_license'] or 'Not Found'}
  Header Coverage: {results['compliance_percentage']:.1f}%
  
Issues:
"""
            for issue in results['issues']:
                output += f"  [{issue['severity'].upper()}] {issue['message']}\n"
            
            if args.output:
                Path(args.output).write_text(output)
                print(f"✓ Compliance report saved to: {args.output}")
            else:
                print(output)
            return 0
            
    finally:
        manager.close()
    
    return 1
