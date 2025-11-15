#!/usr/bin/env python3
"""
Demo script for compliance mapping and gap analysis integration with multi-repo dashboard.

Shows how to:
1. Create compliance mappings for repositories
2. Perform gap analysis
3. Generate compliance reports
4. View compliance status in multi-repo dashboard
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.compliance_mapping import (
    ComplianceMappingManager,
    ComplianceFramework,
    CoverageStatus
)
from accudoc.project_database import ProjectDatabase
from accudoc.multi_repo_dashboard import MultiRepoDashboard, DashboardConfig
from accudoc.scanner import RepositoryScanner


def create_demo_repos():
    """Create demo repositories for testing."""
    temp_dir = tempfile.mkdtemp(prefix='compliance_demo_')
    
    # Create repo 1 with some documentation
    repo1_path = Path(temp_dir) / 'secure_app'
    repo1_path.mkdir(parents=True)
    
    (repo1_path / 'README.md').write_text("""# Secure Application
    
## Overview
This is a secure application that follows industry best practices.

## Security
We implement comprehensive security measures including:
- Access control and authentication
- Data encryption
- Regular security audits

## Compliance
We maintain compliance with SOC2 and HIPAA requirements.
""")
    
    (repo1_path / 'SECURITY.md').write_text("""# Security Policy

## Access Control
All users are assigned unique IDs and role-based access.

## Data Protection
Sensitive data is encrypted at rest and in transit.

## Incident Response
We have a documented incident response procedure.
""")
    
    (repo1_path / 'CONTRIBUTING.md').write_text("# Contributing Guide\n\nPlease follow our security guidelines.")
    
    # Create repo 2 with minimal documentation
    repo2_path = Path(temp_dir) / 'basic_app'
    repo2_path.mkdir(parents=True)
    
    (repo2_path / 'README.md').write_text("""# Basic Application

This is a simple application.

## Features
- Feature 1
- Feature 2
""")
    
    return temp_dir, str(repo1_path), str(repo2_path)


def demo_compliance_mapping():
    """Demonstrate compliance mapping and gap analysis."""
    print("=" * 80)
    print("COMPLIANCE MAPPING & GAP ANALYSIS DEMO")
    print("=" * 80)
    print()
    
    # Create demo repositories
    print("Creating demo repositories...")
    temp_dir, repo1, repo2 = create_demo_repos()
    print(f"✓ Created demo repos in {temp_dir}")
    print()
    
    # Initialize database and compliance manager
    db_path = Path(temp_dir) / 'compliance.db'
    db = ProjectDatabase(db_path)
    compliance_mgr = ComplianceMappingManager(db, None)
    
    # Add projects to database
    print("Adding projects to database...")
    project1_id = db.add_project(repo1, "Secure Application")
    project2_id = db.add_project(repo2, "Basic Application")
    print(f"✓ Added projects")
    print()
    
    # Create compliance mappings for repo1
    print("-" * 80)
    print("Creating compliance mappings for Secure Application...")
    print("-" * 80)
    
    mappings = [
        ("SOC2-CC1.1", "README.md#Security", "Security section documents our organizational structure"),
        ("SOC2-CC6.1", "SECURITY.md#Access Control", "Access control policies are documented"),
        ("HIPAA-164.308(a)(1)", "SECURITY.md", "Security management documented", CoverageStatus.PARTIAL),
        ("HIPAA-164.312(a)(1)", "SECURITY.md#Access Control", "Access control implementation"),
    ]
    
    for mapping_data in mappings:
        req_id = mapping_data[0]
        doc_section = mapping_data[1]
        notes = mapping_data[2]
        status = mapping_data[3] if len(mapping_data) > 3 else CoverageStatus.COVERED
        
        framework = ComplianceFramework.SOC2 if "SOC2" in req_id else ComplianceFramework.HIPAA
        
        mapping_id = compliance_mgr.create_mapping(
            project_id=project1_id,
            requirement_id=req_id,
            framework=framework,
            doc_section=doc_section,
            coverage_status=status,
            notes=notes,
            created_by="demo_user"
        )
        
        print(f"✓ Mapped {req_id} to {doc_section}")
    
    print()
    
    # Perform gap analysis for SOC2
    print("-" * 80)
    print("Performing SOC2 Gap Analysis for Secure Application...")
    print("-" * 80)
    
    soc2_gaps = compliance_mgr.analyze_gaps(project1_id, ComplianceFramework.SOC2)
    
    print(f"\nTotal gaps found: {len(soc2_gaps)}")
    if soc2_gaps:
        critical = sum(1 for g in soc2_gaps if g.severity.value == 'critical')
        high = sum(1 for g in soc2_gaps if g.severity.value == 'high')
        print(f"  Critical: {critical}")
        print(f"  High: {high}")
        
        print("\nTop gaps:")
        for gap in soc2_gaps[:3]:
            print(f"  • {gap.requirement_id}: {gap.title} (Severity: {gap.severity.value})")
    
    print()
    
    # Generate compliance report
    print("-" * 80)
    print("Generating SOC2 Compliance Report...")
    print("-" * 80)
    
    report = compliance_mgr.generate_report(project1_id, ComplianceFramework.SOC2)
    
    print(f"\nSOC2 Compliance Status:")
    print(f"  Total Requirements: {report.total_requirements}")
    print(f"  Covered: {report.covered_count}")
    print(f"  Partially Covered: {report.partial_count}")
    print(f"  Not Covered: {report.not_covered_count}")
    print(f"  Coverage: {report.coverage_percentage:.1f}%")
    print()
    
    # Generate markdown report
    print("Generating detailed compliance report (markdown)...")
    md_report = compliance_mgr.export_report(report, 'markdown')
    report_path = Path(temp_dir) / 'soc2_compliance_report.md'
    report_path.write_text(md_report)
    print(f"✓ Report saved to: {report_path}")
    print()
    
    # Scan repositories for dashboard
    print("-" * 80)
    print("Scanning repositories for multi-repo dashboard...")
    print("-" * 80)
    
    scanner1 = RepositoryScanner(repo1)
    repo1_info = scanner1.scan()
    
    scanner2 = RepositoryScanner(repo2)
    repo2_info = scanner2.scan()
    
    print("✓ Repositories scanned")
    print()
    
    # Create multi-repo dashboard
    print("-" * 80)
    print("Generating Multi-Repository Dashboard with Compliance Data...")
    print("-" * 80)
    
    dashboard = MultiRepoDashboard()
    dashboard.add_repository(repo1_info, "Secure Application")
    dashboard.add_repository(repo2_info, "Basic Application")
    
    # Generate analytics
    dashboard.generate_analytics()
    dashboard.analyze_consistency()
    
    # Generate dashboard report
    dashboard_report = dashboard.generate_report('text')
    
    print("\n" + "=" * 80)
    print("MULTI-REPOSITORY DASHBOARD")
    print("=" * 80)
    print(dashboard_report)
    print()
    
    # Save markdown dashboard
    md_dashboard = dashboard.generate_report('markdown')
    dashboard_path = Path(temp_dir) / 'compliance_dashboard.md'
    dashboard_path.write_text(md_dashboard)
    print(f"✓ Dashboard saved to: {dashboard_path}")
    print()
    
    # Cleanup
    print("-" * 80)
    print("Demo completed!")
    print("-" * 80)
    print(f"\nDemo files created in: {temp_dir}")
    print(f"  - SOC2 Compliance Report: {report_path}")
    print(f"  - Multi-Repo Dashboard: {dashboard_path}")
    print("\nYou can review these files to see the compliance integration.")
    
    # Close database
    db.close()
    
    return temp_dir


if __name__ == '__main__':
    try:
        demo_dir = demo_compliance_mapping()
        print(f"\n✓ Demo completed successfully!")
        print(f"\nFiles are in: {demo_dir}")
    except Exception as e:
        print(f"\n✗ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
