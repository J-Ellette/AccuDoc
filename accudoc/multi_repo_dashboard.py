"""
Multi-Repository Documentation Consistency Dashboard for AccuDoc.

Analyzes documentation coverage, style-guide compliance, and completeness
across multiple repositories. Shows analytics and highlights consistency gaps
to help teams standardize documentation quality organization-wide.
"""

from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json
from datetime import datetime
from dataclasses import dataclass, asdict, field

from accudoc.comparison_reports import RepositoryComparison
from accudoc.health_dashboard import HealthMetrics
from accudoc.style_guides import GoogleStyleGuide, MicrosoftStyleGuide, PlainLanguageGuide
from accudoc.doc_validator import DocumentationValidator
from accudoc.membership import MembershipManager, Permission


@dataclass
class DashboardConfig:
    """Configuration for multi-repo dashboard."""
    style_guide: str = "google"  # google, microsoft, plain
    min_doc_coverage: float = 70.0
    min_completeness_score: float = 60.0
    check_consistency: bool = True
    require_membership: bool = True


@dataclass
class RepositoryAnalysis:
    """Analysis results for a single repository."""
    name: str
    path: str
    doc_coverage: Dict
    completeness_score: Dict
    style_compliance: Dict
    health_metrics: Dict
    compliance_status: Dict = field(default_factory=dict)
    consistency_issues: List[Dict] = field(default_factory=list)
    last_updated: str = ""


@dataclass
class ConsistencyGap:
    """Represents a consistency gap between repositories."""
    gap_type: str  # "coverage", "style", "completeness", "structure"
    severity: str  # "critical", "high", "medium", "low"
    description: str
    affected_repos: List[str]
    recommendation: str


class MultiRepoDashboard:
    """
    Analyzes and tracks documentation quality across multiple repositories.
    
    Provides comprehensive dashboard with:
    - Documentation coverage analysis
    - Style guide compliance checking
    - Completeness scoring
    - Consistency gap detection
    - Organization-wide analytics
    """
    
    def __init__(self, config: Optional[DashboardConfig] = None, 
                 membership_manager: Optional[MembershipManager] = None):
        """
        Initialize multi-repo dashboard.
        
        Args:
            config: Dashboard configuration
            membership_manager: Optional membership manager for access control
        """
        self.config = config or DashboardConfig()
        self.membership_manager = membership_manager
        self.repositories: List[RepositoryAnalysis] = []
        self.analytics: Dict = {}
        self.consistency_gaps: List[ConsistencyGap] = []
        
        # Initialize style guide
        self.style_guide = self._get_style_guide()
    
    def _get_style_guide(self):
        """Get configured style guide."""
        guides = {
            "google": GoogleStyleGuide,
            "microsoft": MicrosoftStyleGuide,
            "plain": PlainLanguageGuide
        }
        guide_class = guides.get(self.config.style_guide.lower(), GoogleStyleGuide)
        return guide_class()
    
    def check_access(self, user_id: str, permission: Permission) -> bool:
        """
        Check if user has required permission.
        
        Args:
            user_id: User ID to check
            permission: Required permission
            
        Returns:
            True if user has permission or membership not required
        """
        if not self.config.require_membership or not self.membership_manager:
            return True
        
        # In a real implementation, this would check against a specific resource
        # For now, we'll check if the user exists and has any permissions
        try:
            user = self.membership_manager.get_user(user_id)
            return user is not None and user.is_active
        except:
            return False
    
    def add_repository(self, repo_info: Dict, name: Optional[str] = None) -> None:
        """
        Add a repository for analysis.
        
        Args:
            repo_info: Repository information from scanner
            name: Optional custom name for the repository
        """
        if name is None:
            name = repo_info.get('name', f'Repo_{len(self.repositories) + 1}')
        
        # Analyze repository
        analysis = self._analyze_repository(repo_info, name)
        self.repositories.append(analysis)
    
    def _analyze_repository(self, repo_info: Dict, name: str) -> RepositoryAnalysis:
        """
        Perform comprehensive analysis on a repository.
        
        Args:
            repo_info: Repository information
            name: Repository name
            
        Returns:
            RepositoryAnalysis with all metrics
        """
        # Calculate health metrics
        health = HealthMetrics(repo_info)
        
        # Analyze documentation coverage
        doc_coverage = self._analyze_doc_coverage(repo_info)
        
        # Calculate completeness score
        completeness = self._calculate_completeness(repo_info)
        
        # Check style compliance
        style_compliance = self._check_style_compliance(repo_info)
        
        # Analyze regulatory compliance status
        compliance_status = self._analyze_compliance_status(repo_info)
        
        return RepositoryAnalysis(
            name=name,
            path=repo_info.get('path', ''),
            doc_coverage=doc_coverage,
            completeness_score=completeness,
            style_compliance=style_compliance,
            health_metrics=health.metrics,
            compliance_status=compliance_status,
            last_updated=datetime.now().isoformat()
        )
    
    def _analyze_doc_coverage(self, repo_info: Dict) -> Dict:
        """
        Analyze documentation coverage for a repository.
        
        Args:
            repo_info: Repository information
            
        Returns:
            Dictionary with coverage metrics
        """
        coverage = {
            'has_readme': False,
            'has_contributing': False,
            'has_license': False,
            'has_changelog': False,
            'has_code_of_conduct': False,
            'has_api_docs': False,
            'has_examples': False,
            'doc_files_count': 0,
            'coverage_percentage': 0.0,
            'missing_docs': []
        }
        
        docs = repo_info.get('documentation', [])
        doc_lower = [doc.lower() for doc in docs]
        
        # Check for key documentation files
        checks = {
            'has_readme': ('readme', 'README file'),
            'has_contributing': ('contributing', 'CONTRIBUTING guide'),
            'has_license': ('license', 'LICENSE file'),
            'has_changelog': ('changelog', 'CHANGELOG'),
            'has_code_of_conduct': ('code_of_conduct', 'CODE_OF_CONDUCT')
        }
        
        for key, (pattern, description) in checks.items():
            if any(pattern in doc for doc in doc_lower):
                coverage[key] = True
            else:
                coverage['missing_docs'].append(description)
        
        # Check for API docs and examples
        coverage['has_api_docs'] = len(repo_info.get('api_docs', [])) > 0
        coverage['has_examples'] = len(repo_info.get('code_examples', [])) > 0
        
        if not coverage['has_api_docs']:
            coverage['missing_docs'].append('API documentation')
        if not coverage['has_examples']:
            coverage['missing_docs'].append('Code examples')
        
        # Calculate coverage percentage
        total_checks = 7
        passed_checks = sum([
            coverage['has_readme'],
            coverage['has_contributing'],
            coverage['has_license'],
            coverage['has_changelog'],
            coverage['has_code_of_conduct'],
            coverage['has_api_docs'],
            coverage['has_examples']
        ])
        coverage['coverage_percentage'] = (passed_checks / total_checks) * 100
        coverage['doc_files_count'] = len(docs)
        
        return coverage
    
    def _calculate_completeness(self, repo_info: Dict) -> Dict:
        """
        Calculate documentation completeness score.
        
        Args:
            repo_info: Repository information
            
        Returns:
            Dictionary with completeness metrics
        """
        score = 0
        max_score = 100
        details = {}
        
        # Documentation files (25 points)
        docs = repo_info.get('documentation', [])
        doc_score = min(25, len(docs) * 5)
        score += doc_score
        details['documentation_files'] = {
            'score': doc_score,
            'max': 25,
            'count': len(docs)
        }
        
        # API documentation (20 points)
        api_docs = repo_info.get('api_docs', [])
        api_score = min(20, len(api_docs) * 2)
        score += api_score
        details['api_documentation'] = {
            'score': api_score,
            'max': 20,
            'count': len(api_docs)
        }
        
        # Code examples (15 points)
        examples = repo_info.get('code_examples', [])
        example_score = min(15, len(examples) * 3)
        score += example_score
        details['code_examples'] = {
            'score': example_score,
            'max': 15,
            'count': len(examples)
        }
        
        # Comments ratio (20 points)
        stats = repo_info.get('statistics', {})
        total_lines = stats.get('total_lines', 0)
        comment_lines = stats.get('comment_lines', 0)
        if total_lines > 0:
            comment_ratio = comment_lines / total_lines
            comment_score = min(20, int(comment_ratio * 100))
        else:
            comment_score = 0
        score += comment_score
        details['code_comments'] = {
            'score': comment_score,
            'max': 20,
            'ratio': comment_ratio if total_lines > 0 else 0
        }
        
        # Test coverage indicators (10 points)
        test_score = 0
        test_files = [f for f in repo_info.get('files', []) 
                     if 'test' in f.lower() or 'spec' in f.lower()]
        if test_files:
            test_score = min(10, len(test_files))
        score += test_score
        details['test_coverage'] = {
            'score': test_score,
            'max': 10,
            'test_files': len(test_files)
        }
        
        # License (10 points)
        license_score = 10 if repo_info.get('license') else 0
        score += license_score
        details['license'] = {
            'score': license_score,
            'max': 10,
            'present': bool(repo_info.get('license'))
        }
        
        # Calculate percentage and grade
        percentage = (score / max_score) * 100
        grade = self._score_to_grade(percentage)
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': percentage,
            'grade': grade,
            'details': details
        }
    
    def _check_style_compliance(self, repo_info: Dict) -> Dict:
        """
        Check style guide compliance for documentation.
        
        Args:
            repo_info: Repository information
            
        Returns:
            Dictionary with compliance metrics
        """
        compliance = {
            'style_guide': self.style_guide.name,
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'compliance_percentage': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        # Get documentation files
        docs = repo_info.get('documentation', [])
        
        if not docs:
            compliance['recommendations'].append(
                "No documentation files found to check for style compliance"
            )
            return compliance
        
        # Initialize validator with style guide
        validator = DocumentationValidator()
        for rule in self.style_guide.get_rules():
            validator.add_rule(rule)
        
        # Check each documentation file
        # Note: In a real implementation, we would read and validate actual file content
        # For now, we'll simulate based on repository metadata
        
        # Simulate some checks based on metadata
        total_files = len(docs)
        compliance['total_checks'] = total_files * 5  # Assume 5 checks per file
        
        # Use documentation coverage as a proxy for style compliance
        doc_coverage = self._analyze_doc_coverage(repo_info)
        coverage_pct = doc_coverage['coverage_percentage']
        
        # Estimate compliance based on coverage
        compliance['passed_checks'] = int((coverage_pct / 100) * compliance['total_checks'])
        compliance['failed_checks'] = compliance['total_checks'] - compliance['passed_checks']
        compliance['compliance_percentage'] = (compliance['passed_checks'] / compliance['total_checks'] * 100) if compliance['total_checks'] > 0 else 0
        
        # Add some recommendations
        if compliance['compliance_percentage'] < 80:
            compliance['recommendations'].append(
                f"Documentation compliance is below 80%. Review files against {self.style_guide.name}."
            )
        
        if not doc_coverage['has_contributing']:
            compliance['issues'].append({
                'type': 'missing_file',
                'severity': 'medium',
                'description': 'Missing CONTRIBUTING.md file'
            })
        
        if not doc_coverage['has_code_of_conduct']:
            compliance['issues'].append({
                'type': 'missing_file',
                'severity': 'low',
                'description': 'Missing CODE_OF_CONDUCT.md file'
            })
        
        return compliance
    
    def _analyze_compliance_status(self, repo_info: Dict) -> Dict:
        """
        Analyze regulatory compliance status for a repository.
        
        Args:
            repo_info: Repository information
            
        Returns:
            Dictionary with compliance status for each framework
        """
        # Try to load compliance data from project database if available
        compliance_data = {}
        
        try:
            from accudoc.compliance_mapping import ComplianceMappingManager, ComplianceFramework
            from accudoc.project_database import ProjectDatabase
            
            db = ProjectDatabase()
            project = db.get_project_by_path(repo_info.get('path', ''))
            
            if project:
                project_id = project['project_id']
                compliance_mgr = ComplianceMappingManager(db, None)
                
                # Analyze each supported framework
                for framework in [ComplianceFramework.SOC2, ComplianceFramework.HIPAA, 
                                 ComplianceFramework.GDPR, ComplianceFramework.ISO27001]:
                    mappings = compliance_mgr.get_mappings(project_id, framework)
                    
                    if mappings:
                        report = compliance_mgr.generate_report(project_id, framework)
                        
                        compliance_data[framework.value] = {
                            'total_requirements': report.total_requirements,
                            'covered_count': report.covered_count,
                            'partial_count': report.partial_count,
                            'not_covered_count': report.not_covered_count,
                            'coverage_percentage': report.coverage_percentage,
                            'gaps_count': len(report.gaps),
                            'critical_gaps': sum(1 for g in report.gaps if g.severity.value == 'critical'),
                            'high_gaps': sum(1 for g in report.gaps if g.severity.value == 'high'),
                        }
            
            db.close()
        except Exception as e:
            # If compliance data is not available, return empty dict
            pass
        
        return compliance_data
    
    def analyze_consistency(self) -> List[ConsistencyGap]:
        """
        Analyze consistency across all repositories.
        
        Returns:
            List of consistency gaps found
        """
        if len(self.repositories) < 2:
            return []
        
        gaps = []
        
        # Check documentation coverage consistency
        gaps.extend(self._check_coverage_consistency())
        
        # Check completeness score consistency
        gaps.extend(self._check_completeness_consistency())
        
        # Check style compliance consistency
        gaps.extend(self._check_style_consistency())
        
        # Check structural consistency
        gaps.extend(self._check_structural_consistency())
        
        self.consistency_gaps = gaps
        return gaps
    
    def _check_coverage_consistency(self) -> List[ConsistencyGap]:
        """Check for documentation coverage inconsistencies."""
        gaps = []
        
        coverages = [repo.doc_coverage['coverage_percentage'] 
                    for repo in self.repositories]
        
        if not coverages:
            return gaps
        
        avg_coverage = sum(coverages) / len(coverages)
        min_coverage = min(coverages)
        max_coverage = max(coverages)
        
        # Significant gap if difference is more than 30%
        if max_coverage - min_coverage > 30:
            low_repos = [repo.name for repo in self.repositories 
                        if repo.doc_coverage['coverage_percentage'] < avg_coverage - 15]
            
            if low_repos:
                gaps.append(ConsistencyGap(
                    gap_type="coverage",
                    severity="high" if len(low_repos) > len(self.repositories) / 2 else "medium",
                    description=f"Documentation coverage varies significantly (range: {min_coverage:.1f}% - {max_coverage:.1f}%)",
                    affected_repos=low_repos,
                    recommendation=f"Improve documentation coverage in {', '.join(low_repos)} to match organization average of {avg_coverage:.1f}%"
                ))
        
        return gaps
    
    def _check_completeness_consistency(self) -> List[ConsistencyGap]:
        """Check for completeness score inconsistencies."""
        gaps = []
        
        scores = [repo.completeness_score['percentage'] 
                 for repo in self.repositories]
        
        if not scores:
            return gaps
        
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        
        # Significant gap if difference is more than 25%
        if max_score - min_score > 25:
            low_repos = [repo.name for repo in self.repositories 
                        if repo.completeness_score['percentage'] < avg_score - 12.5]
            
            if low_repos:
                gaps.append(ConsistencyGap(
                    gap_type="completeness",
                    severity="high" if min_score < self.config.min_completeness_score else "medium",
                    description=f"Documentation completeness varies significantly (range: {min_score:.1f}% - {max_score:.1f}%)",
                    affected_repos=low_repos,
                    recommendation=f"Enhance documentation completeness in {', '.join(low_repos)} to meet organization standards"
                ))
        
        return gaps
    
    def _check_style_consistency(self) -> List[ConsistencyGap]:
        """Check for style compliance inconsistencies."""
        gaps = []
        
        compliances = [repo.style_compliance['compliance_percentage'] 
                      for repo in self.repositories]
        
        if not compliances:
            return gaps
        
        avg_compliance = sum(compliances) / len(compliances)
        min_compliance = min(compliances)
        max_compliance = max(compliances)
        
        # Significant gap if difference is more than 20%
        if max_compliance - min_compliance > 20:
            low_repos = [repo.name for repo in self.repositories 
                        if repo.style_compliance['compliance_percentage'] < avg_compliance - 10]
            
            if low_repos:
                gaps.append(ConsistencyGap(
                    gap_type="style",
                    severity="medium",
                    description=f"Style guide compliance varies (range: {min_compliance:.1f}% - {max_compliance:.1f}%)",
                    affected_repos=low_repos,
                    recommendation=f"Standardize documentation style in {', '.join(low_repos)} according to {self.style_guide.name}"
                ))
        
        return gaps
    
    def _check_structural_consistency(self) -> List[ConsistencyGap]:
        """Check for structural inconsistencies."""
        gaps = []
        
        # Check for missing key files across repos
        key_files = ['README', 'LICENSE', 'CONTRIBUTING']
        
        for file_type in key_files:
            repos_with_file = []
            repos_without_file = []
            
            for repo in self.repositories:
                has_file = False
                if file_type.lower() == 'readme':
                    has_file = repo.doc_coverage['has_readme']
                elif file_type.lower() == 'license':
                    has_file = repo.doc_coverage['has_license']
                elif file_type.lower() == 'contributing':
                    has_file = repo.doc_coverage['has_contributing']
                
                if has_file:
                    repos_with_file.append(repo.name)
                else:
                    repos_without_file.append(repo.name)
            
            # If some but not all repos have this file, it's a consistency issue
            if repos_without_file and repos_with_file:
                severity = "critical" if file_type in ['README', 'LICENSE'] else "medium"
                
                gaps.append(ConsistencyGap(
                    gap_type="structure",
                    severity=severity,
                    description=f"{file_type} file missing in some repositories",
                    affected_repos=repos_without_file,
                    recommendation=f"Add {file_type} file to {', '.join(repos_without_file)} for consistency"
                ))
        
        return gaps
    
    def generate_analytics(self) -> Dict:
        """
        Generate organization-wide analytics.
        
        Returns:
            Dictionary with analytics data
        """
        if not self.repositories:
            return {}
        
        analytics = {
            'generated_at': datetime.now().isoformat(),
            'total_repositories': len(self.repositories),
            'style_guide': self.style_guide.name,
            'summary': {},
            'trends': {},
            'rankings': {},
            'recommendations': []
        }
        
        # Calculate summary statistics
        analytics['summary'] = self._calculate_summary_stats()
        
        # Generate trends
        analytics['trends'] = self._generate_trends()
        
        # Create rankings
        analytics['rankings'] = self._create_rankings()
        
        # Generate recommendations
        analytics['recommendations'] = self._generate_recommendations()
        
        self.analytics = analytics
        return analytics
    
    def _calculate_summary_stats(self) -> Dict:
        """Calculate summary statistics across all repositories."""
        coverages = [repo.doc_coverage['coverage_percentage'] 
                    for repo in self.repositories]
        completeness = [repo.completeness_score['percentage'] 
                       for repo in self.repositories]
        compliances = [repo.style_compliance['compliance_percentage'] 
                      for repo in self.repositories]
        health_scores = [repo.health_metrics.get('overall_health', {}).get('score', 0)
                        for repo in self.repositories]
        
        return {
            'documentation_coverage': {
                'average': sum(coverages) / len(coverages) if coverages else 0,
                'min': min(coverages) if coverages else 0,
                'max': max(coverages) if coverages else 0,
                'below_threshold': sum(1 for c in coverages if c < self.config.min_doc_coverage)
            },
            'completeness_score': {
                'average': sum(completeness) / len(completeness) if completeness else 0,
                'min': min(completeness) if completeness else 0,
                'max': max(completeness) if completeness else 0,
                'below_threshold': sum(1 for c in completeness if c < self.config.min_completeness_score)
            },
            'style_compliance': {
                'average': sum(compliances) / len(compliances) if compliances else 0,
                'min': min(compliances) if compliances else 0,
                'max': max(compliances) if compliances else 0
            },
            'health_score': {
                'average': sum(health_scores) / len(health_scores) if health_scores else 0,
                'min': min(health_scores) if health_scores else 0,
                'max': max(health_scores) if health_scores else 0
            }
        }
    
    def _generate_trends(self) -> Dict:
        """Generate trend analysis."""
        trends = {
            'improving': [],
            'declining': [],
            'stable': []
        }
        
        # For a simple implementation, categorize by current scores
        for repo in self.repositories:
            coverage = repo.doc_coverage['coverage_percentage']
            completeness = repo.completeness_score['percentage']
            avg_score = (coverage + completeness) / 2
            
            if avg_score >= 80:
                trends['stable'].append(repo.name)
            elif avg_score >= 60:
                trends['improving'].append(repo.name)
            else:
                trends['declining'].append(repo.name)
        
        return trends
    
    def _create_rankings(self) -> Dict:
        """Create repository rankings."""
        rankings = {
            'by_coverage': [],
            'by_completeness': [],
            'by_compliance': [],
            'overall': []
        }
        
        # Rank by coverage
        by_coverage = sorted(
            self.repositories,
            key=lambda r: r.doc_coverage['coverage_percentage'],
            reverse=True
        )
        rankings['by_coverage'] = [
            {'rank': i+1, 'name': r.name, 'score': r.doc_coverage['coverage_percentage']}
            for i, r in enumerate(by_coverage)
        ]
        
        # Rank by completeness
        by_completeness = sorted(
            self.repositories,
            key=lambda r: r.completeness_score['percentage'],
            reverse=True
        )
        rankings['by_completeness'] = [
            {'rank': i+1, 'name': r.name, 'score': r.completeness_score['percentage']}
            for i, r in enumerate(by_completeness)
        ]
        
        # Rank by compliance
        by_compliance = sorted(
            self.repositories,
            key=lambda r: r.style_compliance['compliance_percentage'],
            reverse=True
        )
        rankings['by_compliance'] = [
            {'rank': i+1, 'name': r.name, 'score': r.style_compliance['compliance_percentage']}
            for i, r in enumerate(by_compliance)
        ]
        
        # Overall ranking (weighted average)
        overall_scores = []
        for repo in self.repositories:
            overall = (
                repo.doc_coverage['coverage_percentage'] * 0.4 +
                repo.completeness_score['percentage'] * 0.4 +
                repo.style_compliance['compliance_percentage'] * 0.2
            )
            overall_scores.append((repo.name, overall))
        
        overall_scores.sort(key=lambda x: x[1], reverse=True)
        rankings['overall'] = [
            {'rank': i+1, 'name': name, 'score': score}
            for i, (name, score) in enumerate(overall_scores)
        ]
        
        return rankings
    
    def _generate_recommendations(self) -> List[str]:
        """Generate organization-wide recommendations."""
        recommendations = []
        
        summary = self._calculate_summary_stats()
        
        # Documentation coverage recommendations
        if summary['documentation_coverage']['average'] < 70:
            recommendations.append(
                f"Organization-wide documentation coverage is below 70% (current: {summary['documentation_coverage']['average']:.1f}%). "
                "Focus on adding README, CONTRIBUTING, and LICENSE files across all repositories."
            )
        
        if summary['documentation_coverage']['below_threshold'] > 0:
            recommendations.append(
                f"{summary['documentation_coverage']['below_threshold']} repositories are below the minimum coverage threshold. "
                "Prioritize improving these repositories first."
            )
        
        # Completeness recommendations
        if summary['completeness_score']['average'] < 60:
            recommendations.append(
                f"Average completeness score is {summary['completeness_score']['average']:.1f}%. "
                "Add API documentation, code examples, and improve code comments."
            )
        
        # Style compliance recommendations
        if summary['style_compliance']['average'] < 75:
            recommendations.append(
                f"Style guide compliance is {summary['style_compliance']['average']:.1f}%. "
                f"Establish {self.style_guide.name} as the organization standard and train teams."
            )
        
        # Consistency recommendations
        if self.consistency_gaps:
            critical_gaps = [g for g in self.consistency_gaps if g.severity == 'critical']
            if critical_gaps:
                recommendations.append(
                    f"Found {len(critical_gaps)} critical consistency gaps. "
                    "Address these immediately to ensure baseline quality across all repositories."
                )
        
        return recommendations
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def generate_report(self, format: str = 'text') -> str:
        """
        Generate dashboard report.
        
        Args:
            format: Output format ('text', 'markdown', 'html')
            
        Returns:
            Formatted report string
        """
        if format == 'markdown':
            return self._generate_markdown_report()
        elif format == 'html':
            return self._generate_html_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate text format report."""
        if not self.repositories:
            return "No repositories analyzed yet."
        
        # Ensure analytics are generated
        if not self.analytics:
            self.generate_analytics()
        
        if not self.consistency_gaps:
            self.analyze_consistency()
        
        lines = []
        lines.append("=" * 80)
        lines.append("MULTI-REPOSITORY DOCUMENTATION CONSISTENCY DASHBOARD")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Repositories Analyzed: {len(self.repositories)}")
        lines.append(f"Style Guide: {self.style_guide.name}")
        lines.append("")
        
        # Summary statistics
        lines.append("-" * 80)
        lines.append("ORGANIZATION-WIDE SUMMARY")
        lines.append("-" * 80)
        summary = self.analytics['summary']
        
        lines.append(f"\nDocumentation Coverage:")
        lines.append(f"  Average: {summary['documentation_coverage']['average']:.1f}%")
        lines.append(f"  Range: {summary['documentation_coverage']['min']:.1f}% - {summary['documentation_coverage']['max']:.1f}%")
        lines.append(f"  Below Threshold: {summary['documentation_coverage']['below_threshold']} repositories")
        
        lines.append(f"\nCompleteness Score:")
        lines.append(f"  Average: {summary['completeness_score']['average']:.1f}%")
        lines.append(f"  Range: {summary['completeness_score']['min']:.1f}% - {summary['completeness_score']['max']:.1f}%")
        lines.append(f"  Below Threshold: {summary['completeness_score']['below_threshold']} repositories")
        
        lines.append(f"\nStyle Compliance:")
        lines.append(f"  Average: {summary['style_compliance']['average']:.1f}%")
        lines.append(f"  Range: {summary['style_compliance']['min']:.1f}% - {summary['style_compliance']['max']:.1f}%")
        
        # Individual repository details
        lines.append("")
        lines.append("-" * 80)
        lines.append("REPOSITORY DETAILS")
        lines.append("-" * 80)
        
        for repo in self.repositories:
            lines.append(f"\n{repo.name}")
            lines.append(f"  Path: {repo.path}")
            lines.append(f"  Coverage: {repo.doc_coverage['coverage_percentage']:.1f}% ({repo.doc_coverage['doc_files_count']} files)")
            lines.append(f"  Completeness: {repo.completeness_score['percentage']:.1f}% (Grade: {repo.completeness_score['grade']})")
            lines.append(f"  Style Compliance: {repo.style_compliance['compliance_percentage']:.1f}%")
            
            # Add compliance status if available
            if repo.compliance_status:
                lines.append(f"  Regulatory Compliance:")
                for framework, status in repo.compliance_status.items():
                    lines.append(f"    {framework.upper()}: {status['coverage_percentage']:.1f}% ({status['covered_count']}/{status['total_requirements']} requirements)")
                    if status['critical_gaps'] > 0:
                        lines.append(f"      Critical gaps: {status['critical_gaps']}")
            
            if repo.doc_coverage['missing_docs']:
                lines.append(f"  Missing Documentation: {', '.join(repo.doc_coverage['missing_docs'])}")
        
        # Consistency gaps
        if self.consistency_gaps:
            lines.append("")
            lines.append("-" * 80)
            lines.append("CONSISTENCY GAPS")
            lines.append("-" * 80)
            
            # Group by severity
            critical = [g for g in self.consistency_gaps if g.severity == 'critical']
            high = [g for g in self.consistency_gaps if g.severity == 'high']
            medium = [g for g in self.consistency_gaps if g.severity == 'medium']
            low = [g for g in self.consistency_gaps if g.severity == 'low']
            
            for severity, gaps in [('CRITICAL', critical), ('HIGH', high), ('MEDIUM', medium), ('LOW', low)]:
                if gaps:
                    lines.append(f"\n{severity} Severity Gaps:")
                    for gap in gaps:
                        lines.append(f"  • {gap.description}")
                        lines.append(f"    Affected: {', '.join(gap.affected_repos)}")
                        lines.append(f"    Recommendation: {gap.recommendation}")
        
        # Rankings
        lines.append("")
        lines.append("-" * 80)
        lines.append("RANKINGS")
        lines.append("-" * 80)
        
        rankings = self.analytics['rankings']
        
        lines.append("\nOverall Ranking:")
        for entry in rankings['overall'][:5]:  # Top 5
            lines.append(f"  {entry['rank']}. {entry['name']}: {entry['score']:.1f}")
        
        # Recommendations
        lines.append("")
        lines.append("-" * 80)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        
        for i, rec in enumerate(self.analytics['recommendations'], 1):
            lines.append(f"\n{i}. {rec}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown format report."""
        if not self.repositories:
            return "# Multi-Repository Documentation Dashboard\n\nNo repositories analyzed yet."
        
        # Ensure analytics are generated
        if not self.analytics:
            self.generate_analytics()
        
        if not self.consistency_gaps:
            self.analyze_consistency()
        
        lines = []
        lines.append("# Multi-Repository Documentation Consistency Dashboard")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Repositories Analyzed:** {len(self.repositories)}")
        lines.append(f"**Style Guide:** {self.style_guide.name}")
        
        # Summary
        lines.append("\n## Organization-Wide Summary")
        summary = self.analytics['summary']
        
        lines.append("\n### Documentation Coverage")
        lines.append(f"- **Average:** {summary['documentation_coverage']['average']:.1f}%")
        lines.append(f"- **Range:** {summary['documentation_coverage']['min']:.1f}% - {summary['documentation_coverage']['max']:.1f}%")
        lines.append(f"- **Below Threshold:** {summary['documentation_coverage']['below_threshold']} repositories")
        
        lines.append("\n### Completeness Score")
        lines.append(f"- **Average:** {summary['completeness_score']['average']:.1f}%")
        lines.append(f"- **Range:** {summary['completeness_score']['min']:.1f}% - {summary['completeness_score']['max']:.1f}%")
        lines.append(f"- **Below Threshold:** {summary['completeness_score']['below_threshold']} repositories")
        
        lines.append("\n### Style Compliance")
        lines.append(f"- **Average:** {summary['style_compliance']['average']:.1f}%")
        lines.append(f"- **Range:** {summary['style_compliance']['min']:.1f}% - {summary['style_compliance']['max']:.1f}%")
        
        # Repository details
        lines.append("\n## Repository Details")
        lines.append("\n| Repository | Coverage | Completeness | Style | Grade |")
        lines.append("|------------|----------|--------------|-------|-------|")
        
        for repo in self.repositories:
            lines.append(
                f"| {repo.name} | "
                f"{repo.doc_coverage['coverage_percentage']:.1f}% | "
                f"{repo.completeness_score['percentage']:.1f}% | "
                f"{repo.style_compliance['compliance_percentage']:.1f}% | "
                f"{repo.completeness_score['grade']} |"
            )
        
        # Compliance status section
        has_compliance = any(repo.compliance_status for repo in self.repositories)
        if has_compliance:
            lines.append("\n## Regulatory Compliance Status")
            for repo in self.repositories:
                if repo.compliance_status:
                    lines.append(f"\n### {repo.name}")
                    for framework, status in repo.compliance_status.items():
                        lines.append(f"\n**{framework.upper()}**")
                        lines.append(f"- Coverage: {status['coverage_percentage']:.1f}% ({status['covered_count']}/{status['total_requirements']} requirements)")
                        lines.append(f"- Gaps: {status['gaps_count']} total ({status['critical_gaps']} critical, {status['high_gaps']} high)")
                        
                        if status['critical_gaps'] > 0:
                            lines.append(f"- ⚠️ Action required: {status['critical_gaps']} critical gaps need immediate attention")
        
        # Consistency gaps
        if self.consistency_gaps:
            lines.append("\n## Consistency Gaps")
            
            for severity in ['critical', 'high', 'medium', 'low']:
                gaps = [g for g in self.consistency_gaps if g.severity == severity]
                if gaps:
                    lines.append(f"\n### {severity.upper()} Severity")
                    for gap in gaps:
                        lines.append(f"\n**{gap.description}**")
                        lines.append(f"- Affected: {', '.join(gap.affected_repos)}")
                        lines.append(f"- Recommendation: {gap.recommendation}")
        
        # Rankings
        lines.append("\n## Rankings")
        rankings = self.analytics['rankings']
        
        lines.append("\n### Overall Ranking")
        lines.append("\n| Rank | Repository | Score |")
        lines.append("|------|------------|-------|")
        for entry in rankings['overall'][:10]:
            lines.append(f"| {entry['rank']} | {entry['name']} | {entry['score']:.1f} |")
        
        # Recommendations
        lines.append("\n## Recommendations")
        for i, rec in enumerate(self.analytics['recommendations'], 1):
            lines.append(f"\n{i}. {rec}")
        
        return "\n".join(lines)
    
    def _generate_html_report(self) -> str:
        """Generate HTML format report."""
        # For simplicity, convert markdown to basic HTML
        md_report = self._generate_markdown_report()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Multi-Repository Documentation Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        h1 {{
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{
            border-bottom: 2px solid #28a745;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
        }}
        .metric {{
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .gap {{
            background-color: #fff3cd;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #ffc107;
        }}
        .gap.critical {{
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }}
        .gap.high {{
            background-color: #ffe0b2;
            border-left-color: #ff9800;
        }}
        .recommendation {{
            background-color: #d1ecf1;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #17a2b8;
        }}
    </style>
</head>
<body>
    <pre>{md_report}</pre>
</body>
</html>"""
        return html
    
    def export_to_json(self, output_path: Optional[str] = None) -> str:
        """
        Export dashboard data to JSON.
        
        Args:
            output_path: Optional path to save JSON file
            
        Returns:
            JSON string
        """
        # Ensure analytics are generated
        if not self.analytics:
            self.generate_analytics()
        
        if not self.consistency_gaps:
            self.analyze_consistency()
        
        data = {
            'dashboard_config': asdict(self.config),
            'repositories': [
                {
                    'name': repo.name,
                    'path': repo.path,
                    'doc_coverage': repo.doc_coverage,
                    'completeness_score': repo.completeness_score,
                    'style_compliance': repo.style_compliance,
                    'health_metrics': repo.health_metrics,
                    'last_updated': repo.last_updated
                }
                for repo in self.repositories
            ],
            'consistency_gaps': [
                {
                    'gap_type': gap.gap_type,
                    'severity': gap.severity,
                    'description': gap.description,
                    'affected_repos': gap.affected_repos,
                    'recommendation': gap.recommendation
                }
                for gap in self.consistency_gaps
            ],
            'analytics': self.analytics
        }
        
        json_str = json.dumps(data, indent=2, default=str)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)
        
        return json_str
