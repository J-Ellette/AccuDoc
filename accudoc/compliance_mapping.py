"""
Compliance Mapping & Gap Analysis for AccuDoc.

Provides functionality to:
- Map documentation sections to specific regulatory requirements (SOC2, HIPAA, GDPR, ISO27001, etc.)
- Perform gap analysis to identify missing coverage
- Generate compliance reports showing coverage status
- Store mappings in the project database
- Integrate with membership system for permission management
"""

import json
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    SOC2 = "soc2"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    CCPA = "ccpa"
    NIST = "nist"
    FedRAMP = "fedramp"


class CoverageStatus(Enum):
    """Coverage status for a requirement."""
    COVERED = "covered"
    PARTIAL = "partial"
    NOT_COVERED = "not_covered"
    NOT_APPLICABLE = "not_applicable"


class GapSeverity(Enum):
    """Severity level for compliance gaps."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class RegulatoryRequirement:
    """Represents a single regulatory requirement."""
    requirement_id: str
    framework: ComplianceFramework
    category: str
    title: str
    description: str
    mandatory: bool = True
    control_objectives: List[str] = field(default_factory=list)


@dataclass
class ComplianceMapping:
    """Maps a documentation section to a regulatory requirement."""
    mapping_id: str
    requirement_id: str
    framework: ComplianceFramework
    doc_section: str
    doc_path: Optional[str]
    coverage_status: CoverageStatus
    notes: Optional[str] = None
    evidence: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    created_by: str = ""


@dataclass
class ComplianceGap:
    """Represents a compliance gap."""
    gap_id: str
    requirement_id: str
    framework: ComplianceFramework
    category: str
    title: str
    description: str
    severity: GapSeverity
    current_status: CoverageStatus
    recommendations: List[str]
    affected_controls: List[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """Comprehensive compliance report."""
    framework: ComplianceFramework
    generated_at: str
    total_requirements: int
    covered_count: int
    partial_count: int
    not_covered_count: int
    coverage_percentage: float
    gaps: List[ComplianceGap]
    mappings: List[ComplianceMapping]
    summary: Dict[str, Any] = field(default_factory=dict)


class ComplianceFrameworkRegistry:
    """Registry of compliance frameworks and their requirements."""
    
    def __init__(self):
        """Initialize the framework registry."""
        self.logger = logging.getLogger('accudoc.compliance')
        self.frameworks = self._initialize_frameworks()
    
    def _initialize_frameworks(self) -> Dict[ComplianceFramework, List[RegulatoryRequirement]]:
        """Initialize default frameworks and requirements."""
        return {
            ComplianceFramework.SOC2: self._get_soc2_requirements(),
            ComplianceFramework.HIPAA: self._get_hipaa_requirements(),
            ComplianceFramework.GDPR: self._get_gdpr_requirements(),
            ComplianceFramework.ISO27001: self._get_iso27001_requirements(),
            ComplianceFramework.PCI_DSS: self._get_pci_dss_requirements(),
        }
    
    def _get_soc2_requirements(self) -> List[RegulatoryRequirement]:
        """Get SOC2 Type II requirements."""
        return [
            RegulatoryRequirement(
                requirement_id="SOC2-CC1.1",
                framework=ComplianceFramework.SOC2,
                category="Control Environment",
                title="Organizational Structure",
                description="The entity demonstrates a commitment to integrity and ethical values.",
                control_objectives=["Document organizational structure", "Define roles and responsibilities"]
            ),
            RegulatoryRequirement(
                requirement_id="SOC2-CC2.1",
                framework=ComplianceFramework.SOC2,
                category="Communication and Information",
                title="Information Quality",
                description="The entity obtains or generates and uses relevant, quality information.",
                control_objectives=["Document data handling", "Quality assurance processes"]
            ),
            RegulatoryRequirement(
                requirement_id="SOC2-CC3.1",
                framework=ComplianceFramework.SOC2,
                category="Risk Assessment",
                title="Risk Identification",
                description="The entity specifies objectives with sufficient clarity.",
                control_objectives=["Document risk assessment", "Risk management procedures"]
            ),
            RegulatoryRequirement(
                requirement_id="SOC2-CC6.1",
                framework=ComplianceFramework.SOC2,
                category="Logical and Physical Access Controls",
                title="Access Control",
                description="The entity implements logical access security software and infrastructure.",
                control_objectives=["Access control policies", "Authentication mechanisms", "Authorization procedures"]
            ),
            RegulatoryRequirement(
                requirement_id="SOC2-CC7.1",
                framework=ComplianceFramework.SOC2,
                category="System Operations",
                title="Operations Management",
                description="The entity manages the capacity and performance of systems.",
                control_objectives=["System documentation", "Performance monitoring", "Capacity planning"]
            ),
        ]
    
    def _get_hipaa_requirements(self) -> List[RegulatoryRequirement]:
        """Get HIPAA Security Rule requirements."""
        return [
            RegulatoryRequirement(
                requirement_id="HIPAA-164.308(a)(1)",
                framework=ComplianceFramework.HIPAA,
                category="Administrative Safeguards",
                title="Security Management Process",
                description="Implement policies and procedures to prevent, detect, contain, and correct security violations.",
                control_objectives=["Risk analysis", "Risk management", "Sanction policy", "Information system activity review"]
            ),
            RegulatoryRequirement(
                requirement_id="HIPAA-164.308(a)(3)",
                framework=ComplianceFramework.HIPAA,
                category="Administrative Safeguards",
                title="Workforce Security",
                description="Implement policies and procedures to ensure workforce members have appropriate access.",
                control_objectives=["Authorization/supervision", "Workforce clearance", "Termination procedures"]
            ),
            RegulatoryRequirement(
                requirement_id="HIPAA-164.308(a)(4)",
                framework=ComplianceFramework.HIPAA,
                category="Administrative Safeguards",
                title="Information Access Management",
                description="Implement policies and procedures for authorizing access to ePHI.",
                control_objectives=["Access authorization", "Access establishment", "Access modification"]
            ),
            RegulatoryRequirement(
                requirement_id="HIPAA-164.310(a)(1)",
                framework=ComplianceFramework.HIPAA,
                category="Physical Safeguards",
                title="Facility Access Controls",
                description="Implement policies to limit physical access to electronic information systems.",
                control_objectives=["Facility security plan", "Access control procedures", "Validation procedures"]
            ),
            RegulatoryRequirement(
                requirement_id="HIPAA-164.312(a)(1)",
                framework=ComplianceFramework.HIPAA,
                category="Technical Safeguards",
                title="Access Control",
                description="Implement technical policies to allow only authorized persons to access ePHI.",
                control_objectives=["Unique user IDs", "Emergency access", "Automatic logoff", "Encryption"]
            ),
        ]
    
    def _get_gdpr_requirements(self) -> List[RegulatoryRequirement]:
        """Get GDPR requirements."""
        return [
            RegulatoryRequirement(
                requirement_id="GDPR-Art5",
                framework=ComplianceFramework.GDPR,
                category="Principles",
                title="Principles of Processing",
                description="Personal data shall be processed lawfully, fairly and transparently.",
                control_objectives=["Data processing documentation", "Privacy policy", "Consent mechanisms"]
            ),
            RegulatoryRequirement(
                requirement_id="GDPR-Art13",
                framework=ComplianceFramework.GDPR,
                category="Transparency",
                title="Information to be Provided",
                description="Provide data subjects with information about data processing.",
                control_objectives=["Privacy notices", "Data collection documentation"]
            ),
            RegulatoryRequirement(
                requirement_id="GDPR-Art25",
                framework=ComplianceFramework.GDPR,
                category="Data Protection by Design",
                title="Privacy by Design",
                description="Implement appropriate technical and organizational measures.",
                control_objectives=["Privacy impact assessments", "Data protection measures"]
            ),
            RegulatoryRequirement(
                requirement_id="GDPR-Art30",
                framework=ComplianceFramework.GDPR,
                category="Documentation",
                title="Records of Processing Activities",
                description="Maintain records of all processing activities.",
                control_objectives=["Processing records", "Data inventory", "Data flows"]
            ),
            RegulatoryRequirement(
                requirement_id="GDPR-Art32",
                framework=ComplianceFramework.GDPR,
                category="Security",
                title="Security of Processing",
                description="Implement appropriate security measures to protect personal data.",
                control_objectives=["Encryption", "Access controls", "Security testing", "Incident response"]
            ),
        ]
    
    def _get_iso27001_requirements(self) -> List[RegulatoryRequirement]:
        """Get ISO 27001 requirements."""
        return [
            RegulatoryRequirement(
                requirement_id="ISO27001-A.5.1",
                framework=ComplianceFramework.ISO27001,
                category="Security Policy",
                title="Information Security Policies",
                description="Define and document information security policies.",
                control_objectives=["Security policy documentation", "Policy approval", "Policy communication"]
            ),
            RegulatoryRequirement(
                requirement_id="ISO27001-A.6.1",
                framework=ComplianceFramework.ISO27001,
                category="Organization",
                title="Internal Organization",
                description="Establish management framework for information security.",
                control_objectives=["Roles and responsibilities", "Segregation of duties", "Contact with authorities"]
            ),
            RegulatoryRequirement(
                requirement_id="ISO27001-A.9.1",
                framework=ComplianceFramework.ISO27001,
                category="Access Control",
                title="Business Requirements",
                description="Limit access to information and information processing facilities.",
                control_objectives=["Access control policy", "User access management"]
            ),
            RegulatoryRequirement(
                requirement_id="ISO27001-A.12.1",
                framework=ComplianceFramework.ISO27001,
                category="Operations Security",
                title="Operational Procedures",
                description="Document and maintain operational procedures.",
                control_objectives=["Operating procedures", "Change management", "Capacity management"]
            ),
            RegulatoryRequirement(
                requirement_id="ISO27001-A.18.1",
                framework=ComplianceFramework.ISO27001,
                category="Compliance",
                title="Legal and Regulatory",
                description="Identify and document applicable legal and regulatory requirements.",
                control_objectives=["Legal requirements", "Intellectual property", "Privacy protection"]
            ),
        ]
    
    def _get_pci_dss_requirements(self) -> List[RegulatoryRequirement]:
        """Get PCI DSS requirements."""
        return [
            RegulatoryRequirement(
                requirement_id="PCI-DSS-3.1",
                framework=ComplianceFramework.PCI_DSS,
                category="Data Protection",
                title="Cardholder Data Storage",
                description="Keep cardholder data storage to a minimum.",
                control_objectives=["Data retention policy", "Storage limitation", "Secure deletion"]
            ),
            RegulatoryRequirement(
                requirement_id="PCI-DSS-8.1",
                framework=ComplianceFramework.PCI_DSS,
                category="Access Control",
                title="User Identification",
                description="Assign unique IDs to each person with computer access.",
                control_objectives=["Unique user IDs", "User account management"]
            ),
            RegulatoryRequirement(
                requirement_id="PCI-DSS-10.1",
                framework=ComplianceFramework.PCI_DSS,
                category="Monitoring",
                title="Audit Trails",
                description="Implement audit trails to link all access to system components.",
                control_objectives=["Logging mechanisms", "Audit trail documentation"]
            ),
            RegulatoryRequirement(
                requirement_id="PCI-DSS-12.1",
                framework=ComplianceFramework.PCI_DSS,
                category="Information Security Policy",
                title="Security Policy",
                description="Establish, publish, maintain, and disseminate a security policy.",
                control_objectives=["Security policy", "Policy review", "Policy distribution"]
            ),
        ]
    
    def get_requirements(self, framework: ComplianceFramework) -> List[RegulatoryRequirement]:
        """
        Get all requirements for a specific framework.
        
        Args:
            framework: The compliance framework
            
        Returns:
            List of regulatory requirements
        """
        return self.frameworks.get(framework, [])
    
    def get_requirement(self, framework: ComplianceFramework, requirement_id: str) -> Optional[RegulatoryRequirement]:
        """
        Get a specific requirement by ID.
        
        Args:
            framework: The compliance framework
            requirement_id: The requirement ID
            
        Returns:
            The requirement or None if not found
        """
        requirements = self.get_requirements(framework)
        for req in requirements:
            if req.requirement_id == requirement_id:
                return req
        return None


class ComplianceMappingManager:
    """Manages compliance mappings and gap analysis."""
    
    def __init__(self, project_db=None, membership_manager=None):
        """
        Initialize compliance mapping manager.
        
        Args:
            project_db: Project database instance
            membership_manager: Membership manager for access control
        """
        self.logger = logging.getLogger('accudoc.compliance')
        self.project_db = project_db
        self.membership_manager = membership_manager
        self.registry = ComplianceFrameworkRegistry()
        
        if self.project_db:
            self._ensure_compliance_tables()
    
    def _ensure_compliance_tables(self) -> None:
        """Ensure compliance tables exist in the database."""
        if not self.project_db or not self.project_db.conn:
            return
        
        cursor = self.project_db.conn.cursor()
        
        # Compliance frameworks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_frameworks (
                framework_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT,
                description TEXT,
                enabled BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Compliance mappings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_mappings (
                mapping_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                requirement_id TEXT NOT NULL,
                framework TEXT NOT NULL,
                doc_section TEXT NOT NULL,
                doc_path TEXT,
                coverage_status TEXT NOT NULL,
                notes TEXT,
                evidence TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        ''')
        
        # Compliance gaps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_gaps (
                gap_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                requirement_id TEXT NOT NULL,
                framework TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                current_status TEXT NOT NULL,
                recommendations TEXT,
                affected_controls TEXT,
                detected_at TEXT NOT NULL,
                resolved_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        ''')
        
        self.project_db.conn.commit()
    
    def create_mapping(
        self,
        project_id: str,
        requirement_id: str,
        framework: ComplianceFramework,
        doc_section: str,
        doc_path: Optional[str] = None,
        coverage_status: CoverageStatus = CoverageStatus.COVERED,
        notes: Optional[str] = None,
        evidence: Optional[List[str]] = None,
        created_by: str = "system"
    ) -> str:
        """
        Create a new compliance mapping.
        
        Args:
            project_id: Project identifier
            requirement_id: Regulatory requirement ID
            framework: Compliance framework
            doc_section: Documentation section identifier
            doc_path: Optional path to documentation file
            coverage_status: Coverage status
            notes: Optional notes
            evidence: Optional list of evidence
            created_by: User who created the mapping
            
        Returns:
            Mapping ID
        """
        import uuid
        
        mapping_id = f"map_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        
        if self.project_db and self.project_db.conn:
            cursor = self.project_db.conn.cursor()
            cursor.execute('''
                INSERT INTO compliance_mappings (
                    mapping_id, project_id, requirement_id, framework,
                    doc_section, doc_path, coverage_status, notes, evidence,
                    created_at, updated_at, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                mapping_id, project_id, requirement_id, framework.value,
                doc_section, doc_path, coverage_status.value, notes,
                json.dumps(evidence or []), now, now, created_by
            ))
            self.project_db.conn.commit()
        
        self.logger.info(f"Created compliance mapping: {mapping_id}")
        return mapping_id
    
    def get_mappings(
        self,
        project_id: str,
        framework: Optional[ComplianceFramework] = None
    ) -> List[ComplianceMapping]:
        """
        Get all compliance mappings for a project.
        
        Args:
            project_id: Project identifier
            framework: Optional framework filter
            
        Returns:
            List of compliance mappings
        """
        if not self.project_db or not self.project_db.conn:
            return []
        
        cursor = self.project_db.conn.cursor()
        
        if framework:
            cursor.execute('''
                SELECT * FROM compliance_mappings
                WHERE project_id = ? AND framework = ?
                ORDER BY created_at DESC
            ''', (project_id, framework.value))
        else:
            cursor.execute('''
                SELECT * FROM compliance_mappings
                WHERE project_id = ?
                ORDER BY created_at DESC
            ''', (project_id,))
        
        mappings = []
        for row in cursor.fetchall():
            mappings.append(ComplianceMapping(
                mapping_id=row['mapping_id'],
                requirement_id=row['requirement_id'],
                framework=ComplianceFramework(row['framework']),
                doc_section=row['doc_section'],
                doc_path=row['doc_path'],
                coverage_status=CoverageStatus(row['coverage_status']),
                notes=row['notes'],
                evidence=json.loads(row['evidence']) if row['evidence'] else [],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                created_by=row['created_by']
            ))
        
        return mappings
    
    def analyze_gaps(
        self,
        project_id: str,
        framework: ComplianceFramework
    ) -> List[ComplianceGap]:
        """
        Perform gap analysis for a specific framework.
        
        Args:
            project_id: Project identifier
            framework: Compliance framework to analyze
            
        Returns:
            List of compliance gaps
        """
        # Get all requirements for the framework
        requirements = self.registry.get_requirements(framework)
        
        # Get existing mappings
        mappings = self.get_mappings(project_id, framework)
        mapped_requirements = {m.requirement_id for m in mappings}
        
        # Identify gaps
        gaps = []
        for req in requirements:
            if req.requirement_id not in mapped_requirements:
                # Not covered at all
                gap = self._create_gap(
                    project_id,
                    req,
                    CoverageStatus.NOT_COVERED,
                    GapSeverity.CRITICAL if req.mandatory else GapSeverity.MEDIUM
                )
                gaps.append(gap)
            else:
                # Check if partially covered
                mapping = next((m for m in mappings if m.requirement_id == req.requirement_id), None)
                if mapping and mapping.coverage_status == CoverageStatus.PARTIAL:
                    gap = self._create_gap(
                        project_id,
                        req,
                        CoverageStatus.PARTIAL,
                        GapSeverity.HIGH if req.mandatory else GapSeverity.LOW
                    )
                    gaps.append(gap)
        
        # Store gaps in database
        if self.project_db and self.project_db.conn:
            self._store_gaps(project_id, gaps)
        
        return gaps
    
    def _create_gap(
        self,
        project_id: str,
        requirement: RegulatoryRequirement,
        status: CoverageStatus,
        severity: GapSeverity
    ) -> ComplianceGap:
        """Create a compliance gap from a requirement."""
        import uuid
        
        gap_id = f"gap_{uuid.uuid4().hex[:12]}"
        
        recommendations = []
        if status == CoverageStatus.NOT_COVERED:
            recommendations = [
                f"Create documentation for {requirement.title}",
                f"Map relevant documentation sections to requirement {requirement.requirement_id}",
                "Review and implement required controls"
            ]
        elif status == CoverageStatus.PARTIAL:
            recommendations = [
                "Complete documentation for all control objectives",
                "Provide additional evidence for partial coverage",
                "Review and address missing elements"
            ]
        
        return ComplianceGap(
            gap_id=gap_id,
            requirement_id=requirement.requirement_id,
            framework=requirement.framework,
            category=requirement.category,
            title=requirement.title,
            description=requirement.description,
            severity=severity,
            current_status=status,
            recommendations=recommendations,
            affected_controls=requirement.control_objectives
        )
    
    def _store_gaps(self, project_id: str, gaps: List[ComplianceGap]) -> None:
        """Store gaps in the database."""
        if not self.project_db or not self.project_db.conn:
            return
        
        cursor = self.project_db.conn.cursor()
        now = datetime.now().isoformat()
        
        for gap in gaps:
            cursor.execute('''
                INSERT OR REPLACE INTO compliance_gaps (
                    gap_id, project_id, requirement_id, framework,
                    category, title, description, severity,
                    current_status, recommendations, affected_controls,
                    detected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                gap.gap_id, project_id, gap.requirement_id, gap.framework.value,
                gap.category, gap.title, gap.description, gap.severity.value,
                gap.current_status.value, json.dumps(gap.recommendations),
                json.dumps(gap.affected_controls), now
            ))
        
        self.project_db.conn.commit()
    
    def generate_report(
        self,
        project_id: str,
        framework: ComplianceFramework
    ) -> ComplianceReport:
        """
        Generate a comprehensive compliance report.
        
        Args:
            project_id: Project identifier
            framework: Compliance framework
            
        Returns:
            Compliance report
        """
        requirements = self.registry.get_requirements(framework)
        mappings = self.get_mappings(project_id, framework)
        gaps = self.analyze_gaps(project_id, framework)
        
        # Calculate coverage statistics
        total_requirements = len(requirements)
        covered_count = sum(1 for m in mappings if m.coverage_status == CoverageStatus.COVERED)
        partial_count = sum(1 for m in mappings if m.coverage_status == CoverageStatus.PARTIAL)
        not_covered_count = total_requirements - covered_count - partial_count
        
        coverage_percentage = (covered_count + (partial_count * 0.5)) / total_requirements * 100 if total_requirements > 0 else 0
        
        # Generate summary
        summary = {
            "framework": framework.value,
            "total_requirements": total_requirements,
            "coverage_percentage": round(coverage_percentage, 2),
            "critical_gaps": sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL),
            "high_gaps": sum(1 for g in gaps if g.severity == GapSeverity.HIGH),
            "medium_gaps": sum(1 for g in gaps if g.severity == GapSeverity.MEDIUM),
            "low_gaps": sum(1 for g in gaps if g.severity == GapSeverity.LOW),
            "categories": self._get_category_summary(requirements, mappings)
        }
        
        return ComplianceReport(
            framework=framework,
            generated_at=datetime.now().isoformat(),
            total_requirements=total_requirements,
            covered_count=covered_count,
            partial_count=partial_count,
            not_covered_count=not_covered_count,
            coverage_percentage=coverage_percentage,
            gaps=gaps,
            mappings=mappings,
            summary=summary
        )
    
    def _get_category_summary(
        self,
        requirements: List[RegulatoryRequirement],
        mappings: List[ComplianceMapping]
    ) -> Dict[str, Dict[str, int]]:
        """Generate summary by category."""
        categories = {}
        mapped_ids = {m.requirement_id for m in mappings if m.coverage_status == CoverageStatus.COVERED}
        
        for req in requirements:
            if req.category not in categories:
                categories[req.category] = {"total": 0, "covered": 0}
            
            categories[req.category]["total"] += 1
            if req.requirement_id in mapped_ids:
                categories[req.category]["covered"] += 1
        
        return categories
    
    def export_report(
        self,
        report: ComplianceReport,
        format: str = "text"
    ) -> str:
        """
        Export compliance report in various formats.
        
        Args:
            report: Compliance report
            format: Output format (text, markdown, json, html)
            
        Returns:
            Formatted report string
        """
        if format == "json":
            return self._export_json(report)
        elif format == "markdown":
            return self._export_markdown(report)
        elif format == "html":
            return self._export_html(report)
        else:
            return self._export_text(report)
    
    def _export_text(self, report: ComplianceReport) -> str:
        """Export report as plain text."""
        lines = []
        lines.append("=" * 70)
        lines.append(f"COMPLIANCE REPORT: {report.framework.value.upper()}")
        lines.append("=" * 70)
        lines.append(f"Generated: {report.generated_at}")
        lines.append("")
        lines.append("COVERAGE SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Total Requirements: {report.total_requirements}")
        lines.append(f"Covered: {report.covered_count} ({report.covered_count/report.total_requirements*100:.1f}%)")
        lines.append(f"Partially Covered: {report.partial_count}")
        lines.append(f"Not Covered: {report.not_covered_count}")
        lines.append(f"Overall Coverage: {report.coverage_percentage:.1f}%")
        lines.append("")
        
        if report.gaps:
            lines.append("COMPLIANCE GAPS")
            lines.append("-" * 70)
            for gap in report.gaps:
                lines.append(f"\n{gap.requirement_id}: {gap.title}")
                lines.append(f"  Category: {gap.category}")
                lines.append(f"  Severity: {gap.severity.value.upper()}")
                lines.append(f"  Status: {gap.current_status.value}")
                if gap.recommendations:
                    lines.append("  Recommendations:")
                    for rec in gap.recommendations:
                        lines.append(f"    - {rec}")
        
        lines.append("\n" + "=" * 70)
        return "\n".join(lines)
    
    def _export_markdown(self, report: ComplianceReport) -> str:
        """Export report as markdown."""
        lines = []
        lines.append(f"# Compliance Report: {report.framework.value.upper()}")
        lines.append(f"\n**Generated:** {report.generated_at}\n")
        
        lines.append("## Coverage Summary\n")
        lines.append(f"- **Total Requirements:** {report.total_requirements}")
        lines.append(f"- **Covered:** {report.covered_count} ({report.covered_count/report.total_requirements*100:.1f}%)")
        lines.append(f"- **Partially Covered:** {report.partial_count}")
        lines.append(f"- **Not Covered:** {report.not_covered_count}")
        lines.append(f"- **Overall Coverage:** {report.coverage_percentage:.1f}%\n")
        
        if report.gaps:
            lines.append("## Compliance Gaps\n")
            for gap in report.gaps:
                lines.append(f"### {gap.requirement_id}: {gap.title}\n")
                lines.append(f"- **Category:** {gap.category}")
                lines.append(f"- **Severity:** {gap.severity.value.upper()}")
                lines.append(f"- **Status:** {gap.current_status.value}\n")
                if gap.recommendations:
                    lines.append("**Recommendations:**")
                    for rec in gap.recommendations:
                        lines.append(f"- {rec}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _export_html(self, report: ComplianceReport) -> str:
        """Export report as HTML."""
        html = f"""
        <html>
        <head>
            <title>Compliance Report: {report.framework.value.upper()}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .gap {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .critical {{ border-left: 5px solid #d32f2f; }}
                .high {{ border-left: 5px solid #f57c00; }}
                .medium {{ border-left: 5px solid #fbc02d; }}
                .low {{ border-left: 5px solid #388e3c; }}
            </style>
        </head>
        <body>
            <h1>Compliance Report: {report.framework.value.upper()}</h1>
            <p><strong>Generated:</strong> {report.generated_at}</p>
            
            <div class="summary">
                <h2>Coverage Summary</h2>
                <ul>
                    <li><strong>Total Requirements:</strong> {report.total_requirements}</li>
                    <li><strong>Covered:</strong> {report.covered_count} ({report.covered_count/report.total_requirements*100:.1f}%)</li>
                    <li><strong>Partially Covered:</strong> {report.partial_count}</li>
                    <li><strong>Not Covered:</strong> {report.not_covered_count}</li>
                    <li><strong>Overall Coverage:</strong> {report.coverage_percentage:.1f}%</li>
                </ul>
            </div>
            
            <h2>Compliance Gaps</h2>
        """
        
        for gap in report.gaps:
            html += f"""
            <div class="gap {gap.severity.value}">
                <h3>{gap.requirement_id}: {gap.title}</h3>
                <p><strong>Category:</strong> {gap.category}</p>
                <p><strong>Severity:</strong> {gap.severity.value.upper()}</p>
                <p><strong>Status:</strong> {gap.current_status.value}</p>
                <p><strong>Recommendations:</strong></p>
                <ul>
            """
            for rec in gap.recommendations:
                html += f"<li>{rec}</li>"
            html += "</ul></div>"
        
        html += "</body></html>"
        return html
    
    def _export_json(self, report: ComplianceReport) -> str:
        """Export report as JSON."""
        return json.dumps({
            "framework": report.framework.value,
            "generated_at": report.generated_at,
            "total_requirements": report.total_requirements,
            "covered_count": report.covered_count,
            "partial_count": report.partial_count,
            "not_covered_count": report.not_covered_count,
            "coverage_percentage": report.coverage_percentage,
            "summary": report.summary,
            "gaps": [
                {
                    "gap_id": g.gap_id,
                    "requirement_id": g.requirement_id,
                    "framework": g.framework.value,
                    "category": g.category,
                    "title": g.title,
                    "description": g.description,
                    "severity": g.severity.value,
                    "current_status": g.current_status.value,
                    "recommendations": g.recommendations,
                    "affected_controls": g.affected_controls
                }
                for g in report.gaps
            ],
            "mappings": [
                {
                    "mapping_id": m.mapping_id,
                    "requirement_id": m.requirement_id,
                    "framework": m.framework.value,
                    "doc_section": m.doc_section,
                    "doc_path": m.doc_path,
                    "coverage_status": m.coverage_status.value,
                    "notes": m.notes,
                    "evidence": m.evidence,
                    "created_at": m.created_at,
                    "updated_at": m.updated_at,
                    "created_by": m.created_by
                }
                for m in report.mappings
            ]
        }, indent=2)
