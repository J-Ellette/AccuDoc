"""
Test suite for compliance mapping and gap analysis.
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from accudoc.compliance_mapping import (
    ComplianceMappingManager,
    ComplianceFramework,
    ComplianceFrameworkRegistry,
    CoverageStatus,
    GapSeverity,
    RegulatoryRequirement,
    ComplianceMapping,
    ComplianceGap,
    ComplianceReport
)
from accudoc.project_database import ProjectDatabase


class TestComplianceFrameworkRegistry(unittest.TestCase):
    """Test cases for ComplianceFrameworkRegistry."""
    
    def setUp(self):
        """Set up test registry."""
        self.registry = ComplianceFrameworkRegistry()
    
    def test_initialization(self):
        """Test registry initialization."""
        self.assertIsNotNone(self.registry.frameworks)
        self.assertIn(ComplianceFramework.SOC2, self.registry.frameworks)
        self.assertIn(ComplianceFramework.HIPAA, self.registry.frameworks)
        self.assertIn(ComplianceFramework.GDPR, self.registry.frameworks)
    
    def test_get_soc2_requirements(self):
        """Test SOC2 requirements."""
        requirements = self.registry.get_requirements(ComplianceFramework.SOC2)
        self.assertIsInstance(requirements, list)
        self.assertGreater(len(requirements), 0)
        
        # Check first requirement
        req = requirements[0]
        self.assertIsInstance(req, RegulatoryRequirement)
        self.assertEqual(req.framework, ComplianceFramework.SOC2)
        self.assertIsNotNone(req.requirement_id)
        self.assertIsNotNone(req.title)
        self.assertIsNotNone(req.category)
    
    def test_get_hipaa_requirements(self):
        """Test HIPAA requirements."""
        requirements = self.registry.get_requirements(ComplianceFramework.HIPAA)
        self.assertIsInstance(requirements, list)
        self.assertGreater(len(requirements), 0)
        
        # Verify HIPAA-specific requirements
        req_ids = [r.requirement_id for r in requirements]
        self.assertTrue(any('HIPAA-164' in rid for rid in req_ids))
    
    def test_get_gdpr_requirements(self):
        """Test GDPR requirements."""
        requirements = self.registry.get_requirements(ComplianceFramework.GDPR)
        self.assertIsInstance(requirements, list)
        self.assertGreater(len(requirements), 0)
        
        # Verify GDPR-specific requirements
        req_ids = [r.requirement_id for r in requirements]
        self.assertTrue(any('GDPR' in rid for rid in req_ids))
    
    def test_get_iso27001_requirements(self):
        """Test ISO 27001 requirements."""
        requirements = self.registry.get_requirements(ComplianceFramework.ISO27001)
        self.assertIsInstance(requirements, list)
        self.assertGreater(len(requirements), 0)
    
    def test_get_pci_dss_requirements(self):
        """Test PCI DSS requirements."""
        requirements = self.registry.get_requirements(ComplianceFramework.PCI_DSS)
        self.assertIsInstance(requirements, list)
        self.assertGreater(len(requirements), 0)
    
    def test_get_specific_requirement(self):
        """Test getting a specific requirement."""
        requirements = self.registry.get_requirements(ComplianceFramework.SOC2)
        if requirements:
            req_id = requirements[0].requirement_id
            req = self.registry.get_requirement(ComplianceFramework.SOC2, req_id)
            self.assertIsNotNone(req)
            self.assertEqual(req.requirement_id, req_id)
    
    def test_get_nonexistent_requirement(self):
        """Test getting a non-existent requirement."""
        req = self.registry.get_requirement(ComplianceFramework.SOC2, "NONEXISTENT-123")
        self.assertIsNone(req)


class TestComplianceMappingManager(unittest.TestCase):
    """Test cases for ComplianceMappingManager."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        self.db = ProjectDatabase(self.db_path)
        
        # Create test project
        self.project_id = self.db.add_project('/test/repo', 'Test Project')
        
        # Initialize compliance manager
        self.manager = ComplianceMappingManager(self.db, None)
    
    def tearDown(self):
        """Clean up test environment."""
        self.db.close()
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager.registry)
        self.assertIsNotNone(self.manager.project_db)
    
    def test_create_mapping(self):
        """Test creating a compliance mapping."""
        mapping_id = self.manager.create_mapping(
            project_id=self.project_id,
            requirement_id="SOC2-CC1.1",
            framework=ComplianceFramework.SOC2,
            doc_section="README.md#Security",
            doc_path="/docs/README.md",
            coverage_status=CoverageStatus.COVERED,
            notes="Security section covers organizational structure",
            evidence=["README.md", "SECURITY.md"],
            created_by="test_user"
        )
        
        self.assertIsNotNone(mapping_id)
        self.assertTrue(mapping_id.startswith('map_'))
    
    def test_get_mappings(self):
        """Test retrieving mappings."""
        # Create multiple mappings
        self.manager.create_mapping(
            project_id=self.project_id,
            requirement_id="SOC2-CC1.1",
            framework=ComplianceFramework.SOC2,
            doc_section="README.md",
            created_by="test_user"
        )
        
        self.manager.create_mapping(
            project_id=self.project_id,
            requirement_id="SOC2-CC2.1",
            framework=ComplianceFramework.SOC2,
            doc_section="CONTRIBUTING.md",
            created_by="test_user"
        )
        
        # Get all mappings
        mappings = self.manager.get_mappings(self.project_id)
        self.assertEqual(len(mappings), 2)
        
        # Get SOC2 mappings only
        soc2_mappings = self.manager.get_mappings(self.project_id, ComplianceFramework.SOC2)
        self.assertEqual(len(soc2_mappings), 2)
    
    def test_gap_analysis_no_mappings(self):
        """Test gap analysis with no mappings."""
        gaps = self.manager.analyze_gaps(self.project_id, ComplianceFramework.SOC2)
        
        # Should have gaps for all requirements
        requirements = self.manager.registry.get_requirements(ComplianceFramework.SOC2)
        self.assertEqual(len(gaps), len(requirements))
        
        # All gaps should be NOT_COVERED
        for gap in gaps:
            self.assertEqual(gap.current_status, CoverageStatus.NOT_COVERED)
            self.assertIsInstance(gap.severity, GapSeverity)
    
    def test_gap_analysis_with_mappings(self):
        """Test gap analysis with some mappings."""
        # Create mapping for one requirement
        self.manager.create_mapping(
            project_id=self.project_id,
            requirement_id="SOC2-CC1.1",
            framework=ComplianceFramework.SOC2,
            doc_section="README.md",
            coverage_status=CoverageStatus.COVERED,
            created_by="test_user"
        )
        
        gaps = self.manager.analyze_gaps(self.project_id, ComplianceFramework.SOC2)
        
        # Should have gaps for unmapped requirements
        requirements = self.manager.registry.get_requirements(ComplianceFramework.SOC2)
        self.assertEqual(len(gaps), len(requirements) - 1)
    
    def test_gap_analysis_partial_coverage(self):
        """Test gap analysis with partial coverage."""
        # Create mapping with partial coverage
        self.manager.create_mapping(
            project_id=self.project_id,
            requirement_id="SOC2-CC1.1",
            framework=ComplianceFramework.SOC2,
            doc_section="README.md",
            coverage_status=CoverageStatus.PARTIAL,
            created_by="test_user"
        )
        
        gaps = self.manager.analyze_gaps(self.project_id, ComplianceFramework.SOC2)
        
        # Should have gap for partially covered requirement
        partial_gaps = [g for g in gaps if g.requirement_id == "SOC2-CC1.1"]
        self.assertEqual(len(partial_gaps), 1)
        self.assertEqual(partial_gaps[0].current_status, CoverageStatus.PARTIAL)
    
    def test_generate_report(self):
        """Test compliance report generation."""
        # Create some mappings
        self.manager.create_mapping(
            project_id=self.project_id,
            requirement_id="SOC2-CC1.1",
            framework=ComplianceFramework.SOC2,
            doc_section="README.md",
            coverage_status=CoverageStatus.COVERED,
            created_by="test_user"
        )
        
        self.manager.create_mapping(
            project_id=self.project_id,
            requirement_id="SOC2-CC2.1",
            framework=ComplianceFramework.SOC2,
            doc_section="CONTRIBUTING.md",
            coverage_status=CoverageStatus.PARTIAL,
            created_by="test_user"
        )
        
        report = self.manager.generate_report(self.project_id, ComplianceFramework.SOC2)
        
        self.assertIsInstance(report, ComplianceReport)
        self.assertEqual(report.framework, ComplianceFramework.SOC2)
        self.assertGreater(report.total_requirements, 0)
        self.assertEqual(report.covered_count, 1)
        self.assertEqual(report.partial_count, 1)
        self.assertGreater(report.coverage_percentage, 0)
        self.assertLess(report.coverage_percentage, 100)
    
    def test_export_report_text(self):
        """Test exporting report as text."""
        report = self.manager.generate_report(self.project_id, ComplianceFramework.SOC2)
        text_report = self.manager.export_report(report, 'text')
        
        self.assertIsInstance(text_report, str)
        self.assertIn('COMPLIANCE REPORT', text_report)
        self.assertIn('SOC2', text_report.upper())
        self.assertIn('COVERAGE SUMMARY', text_report)
    
    def test_export_report_markdown(self):
        """Test exporting report as markdown."""
        report = self.manager.generate_report(self.project_id, ComplianceFramework.SOC2)
        md_report = self.manager.export_report(report, 'markdown')
        
        self.assertIsInstance(md_report, str)
        self.assertIn('# Compliance Report', md_report)
        self.assertIn('## Coverage Summary', md_report)
    
    def test_export_report_html(self):
        """Test exporting report as HTML."""
        report = self.manager.generate_report(self.project_id, ComplianceFramework.SOC2)
        html_report = self.manager.export_report(report, 'html')
        
        self.assertIsInstance(html_report, str)
        self.assertIn('<html>', html_report)
        self.assertIn('Compliance Report', html_report)
        self.assertIn('<style>', html_report)
    
    def test_export_report_json(self):
        """Test exporting report as JSON."""
        report = self.manager.generate_report(self.project_id, ComplianceFramework.SOC2)
        json_report = self.manager.export_report(report, 'json')
        
        self.assertIsInstance(json_report, str)
        
        # Parse JSON to verify structure
        data = json.loads(json_report)
        self.assertIn('framework', data)
        self.assertIn('coverage_percentage', data)
        self.assertIn('gaps', data)
        self.assertIn('mappings', data)
    
    def test_multiple_frameworks(self):
        """Test working with multiple frameworks."""
        # Create mappings for different frameworks
        self.manager.create_mapping(
            project_id=self.project_id,
            requirement_id="SOC2-CC1.1",
            framework=ComplianceFramework.SOC2,
            doc_section="README.md",
            created_by="test_user"
        )
        
        self.manager.create_mapping(
            project_id=self.project_id,
            requirement_id="HIPAA-164.308(a)(1)",
            framework=ComplianceFramework.HIPAA,
            doc_section="SECURITY.md",
            created_by="test_user"
        )
        
        # Get SOC2 mappings
        soc2_mappings = self.manager.get_mappings(self.project_id, ComplianceFramework.SOC2)
        self.assertEqual(len(soc2_mappings), 1)
        
        # Get HIPAA mappings
        hipaa_mappings = self.manager.get_mappings(self.project_id, ComplianceFramework.HIPAA)
        self.assertEqual(len(hipaa_mappings), 1)
        
        # Get all mappings
        all_mappings = self.manager.get_mappings(self.project_id)
        self.assertEqual(len(all_mappings), 2)
    
    def test_gap_severity(self):
        """Test gap severity assignment."""
        gaps = self.manager.analyze_gaps(self.project_id, ComplianceFramework.SOC2)
        
        # Check that gaps have severity assigned
        for gap in gaps:
            self.assertIn(gap.severity, [
                GapSeverity.CRITICAL,
                GapSeverity.HIGH,
                GapSeverity.MEDIUM,
                GapSeverity.LOW
            ])
    
    def test_gap_recommendations(self):
        """Test gap recommendations."""
        gaps = self.manager.analyze_gaps(self.project_id, ComplianceFramework.SOC2)
        
        # All gaps should have recommendations
        for gap in gaps:
            self.assertIsInstance(gap.recommendations, list)
            self.assertGreater(len(gap.recommendations), 0)
    
    def test_category_summary(self):
        """Test category summary in report."""
        # Create mapping
        self.manager.create_mapping(
            project_id=self.project_id,
            requirement_id="SOC2-CC1.1",
            framework=ComplianceFramework.SOC2,
            doc_section="README.md",
            coverage_status=CoverageStatus.COVERED,
            created_by="test_user"
        )
        
        report = self.manager.generate_report(self.project_id, ComplianceFramework.SOC2)
        
        # Check category summary
        self.assertIn('categories', report.summary)
        categories = report.summary['categories']
        self.assertIsInstance(categories, dict)
        
        # Each category should have total and covered counts
        for category, counts in categories.items():
            self.assertIn('total', counts)
            self.assertIn('covered', counts)


class TestComplianceDataClasses(unittest.TestCase):
    """Test compliance data classes."""
    
    def test_regulatory_requirement(self):
        """Test RegulatoryRequirement dataclass."""
        req = RegulatoryRequirement(
            requirement_id="TEST-001",
            framework=ComplianceFramework.SOC2,
            category="Test Category",
            title="Test Requirement",
            description="Test description",
            mandatory=True,
            control_objectives=["Objective 1", "Objective 2"]
        )
        
        self.assertEqual(req.requirement_id, "TEST-001")
        self.assertEqual(req.framework, ComplianceFramework.SOC2)
        self.assertTrue(req.mandatory)
        self.assertEqual(len(req.control_objectives), 2)
    
    def test_compliance_mapping(self):
        """Test ComplianceMapping dataclass."""
        mapping = ComplianceMapping(
            mapping_id="map_123",
            requirement_id="TEST-001",
            framework=ComplianceFramework.SOC2,
            doc_section="README.md",
            doc_path="/docs/README.md",
            coverage_status=CoverageStatus.COVERED,
            notes="Test notes",
            evidence=["file1.md", "file2.md"]
        )
        
        self.assertEqual(mapping.mapping_id, "map_123")
        self.assertEqual(mapping.coverage_status, CoverageStatus.COVERED)
        self.assertEqual(len(mapping.evidence), 2)
    
    def test_compliance_gap(self):
        """Test ComplianceGap dataclass."""
        gap = ComplianceGap(
            gap_id="gap_123",
            requirement_id="TEST-001",
            framework=ComplianceFramework.SOC2,
            category="Test Category",
            title="Test Gap",
            description="Test description",
            severity=GapSeverity.HIGH,
            current_status=CoverageStatus.NOT_COVERED,
            recommendations=["Fix 1", "Fix 2"],
            affected_controls=["Control 1"]
        )
        
        self.assertEqual(gap.gap_id, "gap_123")
        self.assertEqual(gap.severity, GapSeverity.HIGH)
        self.assertEqual(len(gap.recommendations), 2)


if __name__ == '__main__':
    unittest.main()
