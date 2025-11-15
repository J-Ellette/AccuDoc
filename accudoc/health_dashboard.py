"""
Project Health Dashboard module for AccuDoc.
Provides comprehensive health metrics and scoring for repository analysis.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import math


class HealthMetrics:
    """Calculates and manages project health metrics."""
    
    # Scoring thresholds
    EXCELLENT_SCORE = 90
    GOOD_SCORE = 75
    FAIR_SCORE = 60
    POOR_SCORE = 40
    
    def __init__(self, repo_info: Dict):
        """
        Initialize health metrics calculator.
        
        Args:
            repo_info: Repository information from scanner
        """
        self.repo_info = repo_info
        self.metrics = {}
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate all health metrics."""
        self.metrics['documentation_coverage'] = self._calculate_doc_coverage()
        self.metrics['code_quality'] = self._calculate_code_quality()
        self.metrics['dependency_health'] = self._calculate_dependency_health()
        self.metrics['maintainability'] = self._calculate_maintainability()
        self.metrics['license_compliance'] = self._calculate_license_compliance()
        self.metrics['overall_health'] = self._calculate_overall_health()
    
    def _calculate_doc_coverage(self) -> Dict:
        """Calculate documentation coverage score."""
        score = 0
        reasons = []
        
        # Check for README
        docs = self.repo_info.get('documentation', [])
        readme_found = any('readme' in doc.lower() for doc in docs)
        if readme_found:
            score += 20
            reasons.append("README found")
        else:
            reasons.append("Missing README")
        
        # Check for other documentation
        important_docs = ['contributing', 'license', 'changelog', 'code_of_conduct']
        for doc_type in important_docs:
            if any(doc_type in doc.lower() for doc in docs):
                score += 10
                reasons.append(f"{doc_type.upper()} found")
        
        # Check for API documentation
        api_docs = self.repo_info.get('api_docs', [])
        if api_docs:
            score += 20
            reasons.append(f"API documentation: {len(api_docs)} items")
        
        # Check for code examples
        examples = self.repo_info.get('code_examples', [])
        if examples:
            score += 10
            reasons.append(f"Code examples: {len(examples)}")
        
        # Normalize to 100
        score = min(100, score)
        
        return {
            'score': score,
            'grade': self._score_to_grade(score),
            'status': self._score_to_status(score),
            'reasons': reasons
        }
    
    def _calculate_code_quality(self) -> Dict:
        """Calculate code quality score."""
        score = 80  # Start with good baseline
        reasons = []
        
        # Check for TODO/FIXME comments
        todos = self.repo_info.get('todos', [])
        if todos:
            todo_penalty = min(20, len(todos) * 2)
            score -= todo_penalty
            reasons.append(f"{len(todos)} TODO/FIXME items found (-{todo_penalty})")
        else:
            reasons.append("No TODO/FIXME items")
        
        # Check for complexity issues (if available)
        complexity = self.repo_info.get('complexity', {})
        if complexity:
            high_complexity = complexity.get('high_complexity_functions', [])
            if high_complexity:
                complexity_penalty = min(15, len(high_complexity) * 3)
                score -= complexity_penalty
                reasons.append(f"{len(high_complexity)} high complexity functions (-{complexity_penalty})")
        
        # Check for best practices violations (if available)
        best_practices = self.repo_info.get('best_practices', {})
        if best_practices:
            violations = best_practices.get('violations', [])
            if violations:
                bp_penalty = min(20, len(violations) * 2)
                score -= bp_penalty
                reasons.append(f"{len(violations)} best practice violations (-{bp_penalty})")
        
        # Bonus for having tests
        files = self.repo_info.get('files', [])
        test_files = [f for f in files if 'test' in f.lower()]
        if test_files:
            score += 10
            reasons.append(f"{len(test_files)} test files found (+10)")
        else:
            reasons.append("No test files detected")
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'grade': self._score_to_grade(score),
            'status': self._score_to_status(score),
            'reasons': reasons
        }
    
    def _calculate_dependency_health(self) -> Dict:
        """Calculate dependency health score."""
        score = 85  # Start with good baseline
        reasons = []
        
        dependencies = self.repo_info.get('dependencies', {})
        
        if not dependencies:
            reasons.append("No dependencies detected")
            return {
                'score': 100,
                'grade': 'A',
                'status': 'Excellent',
                'reasons': reasons
            }
        
        # Count total dependencies
        total_deps = sum(len(deps) if isinstance(deps, list) else 0 
                        for deps in dependencies.values())
        
        if total_deps > 0:
            reasons.append(f"{total_deps} dependencies found")
            
            # Penalty for too many dependencies
            if total_deps > 50:
                score -= 15
                reasons.append("Large number of dependencies (-15)")
            elif total_deps > 100:
                score -= 25
                reasons.append("Very large number of dependencies (-25)")
        
        # Check for package version analysis (if available)
        package_analysis = self.repo_info.get('package_analysis', {})
        if package_analysis:
            outdated = package_analysis.get('outdated_packages', [])
            if outdated:
                outdated_penalty = min(20, len(outdated) * 5)
                score -= outdated_penalty
                reasons.append(f"{len(outdated)} outdated packages (-{outdated_penalty})")
            
            vulnerable = package_analysis.get('vulnerable_packages', [])
            if vulnerable:
                vuln_penalty = len(vulnerable) * 10
                score -= vuln_penalty
                reasons.append(f"{len(vulnerable)} vulnerable packages (-{vuln_penalty})")
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'grade': self._score_to_grade(score),
            'status': self._score_to_status(score),
            'reasons': reasons
        }
    
    def _calculate_maintainability(self) -> Dict:
        """Calculate maintainability index."""
        score = 75  # Start with fair baseline
        reasons = []
        
        stats = self.repo_info.get('statistics', {})
        
        if not stats:
            reasons.append("No statistics available")
            return {
                'score': 75,
                'grade': 'B',
                'status': 'Good',
                'reasons': reasons
            }
        
        # Check comment ratio
        total_lines = stats.get('total_lines', 0)
        comment_lines = stats.get('comment_lines', 0)
        
        if total_lines > 0:
            comment_ratio = (comment_lines / total_lines) * 100
            
            if comment_ratio >= 15:
                score += 15
                reasons.append(f"Good comment ratio: {comment_ratio:.1f}% (+15)")
            elif comment_ratio >= 10:
                score += 10
                reasons.append(f"Fair comment ratio: {comment_ratio:.1f}% (+10)")
            elif comment_ratio < 5:
                score -= 10
                reasons.append(f"Low comment ratio: {comment_ratio:.1f}% (-10)")
        
        # Check for configuration files (good practice)
        config_files = self.repo_info.get('config_files', [])
        if config_files:
            score += 10
            reasons.append(f"{len(config_files)} config files found (+10)")
        
        # Check repository size
        files_count = self.repo_info.get('files_count', 0)
        if files_count > 1000:
            score -= 10
            reasons.append(f"Large repository: {files_count} files (-10)")
        elif files_count > 500:
            score -= 5
            reasons.append(f"Medium repository: {files_count} files (-5)")
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'grade': self._score_to_grade(score),
            'status': self._score_to_status(score),
            'reasons': reasons
        }
    
    def _calculate_license_compliance(self) -> Dict:
        """Calculate license compliance score."""
        score = 50  # Start neutral
        reasons = []
        
        license_info = self.repo_info.get('license', '')
        
        if license_info and license_info != 'Not found':
            score = 100
            reasons.append(f"License found: {license_info}")
            
            # Check for license compliance issues (if available)
            license_compliance = self.repo_info.get('license_compliance', {})
            if license_compliance:
                issues = license_compliance.get('issues', [])
                if issues:
                    score -= len(issues) * 20
                    reasons.append(f"{len(issues)} license compliance issues")
        else:
            reasons.append("No license found")
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'grade': self._score_to_grade(score),
            'status': self._score_to_status(score),
            'reasons': reasons
        }
    
    def _calculate_overall_health(self) -> Dict:
        """Calculate overall health score as weighted average."""
        weights = {
            'documentation_coverage': 0.25,
            'code_quality': 0.30,
            'dependency_health': 0.20,
            'maintainability': 0.15,
            'license_compliance': 0.10
        }
        
        weighted_score = 0
        for metric, weight in weights.items():
            if metric in self.metrics and metric != 'overall_health':
                weighted_score += self.metrics[metric]['score'] * weight
        
        score = round(weighted_score)
        
        return {
            'score': score,
            'grade': self._score_to_grade(score),
            'status': self._score_to_status(score),
            'weights': weights
        }
    
    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= self.EXCELLENT_SCORE:
            return 'A'
        elif score >= self.GOOD_SCORE:
            return 'B'
        elif score >= self.FAIR_SCORE:
            return 'C'
        elif score >= self.POOR_SCORE:
            return 'D'
        else:
            return 'F'
    
    def _score_to_status(self, score: int) -> str:
        """Convert score to status label."""
        if score >= self.EXCELLENT_SCORE:
            return 'Excellent'
        elif score >= self.GOOD_SCORE:
            return 'Good'
        elif score >= self.FAIR_SCORE:
            return 'Fair'
        elif score >= self.POOR_SCORE:
            return 'Poor'
        else:
            return 'Critical'
    
    def get_metrics(self) -> Dict:
        """Get all calculated metrics."""
        return self.metrics
    
    def get_summary(self) -> Dict:
        """Get summary of key metrics."""
        return {
            'overall_score': self.metrics['overall_health']['score'],
            'overall_grade': self.metrics['overall_health']['grade'],
            'overall_status': self.metrics['overall_health']['status'],
            'documentation': self.metrics['documentation_coverage']['score'],
            'code_quality': self.metrics['code_quality']['score'],
            'dependencies': self.metrics['dependency_health']['score'],
            'maintainability': self.metrics['maintainability']['score'],
            'license': self.metrics['license_compliance']['score']
        }


class HealthDashboard:
    """Generates health dashboard displays."""
    
    def __init__(self, repo_info: Dict):
        """
        Initialize health dashboard.
        
        Args:
            repo_info: Repository information from scanner
        """
        self.repo_info = repo_info
        self.metrics = HealthMetrics(repo_info)
    
    def generate_text_dashboard(self) -> str:
        """Generate text-based dashboard."""
        lines = []
        lines.append("=" * 70)
        lines.append("PROJECT HEALTH DASHBOARD")
        lines.append("=" * 70)
        lines.append("")
        
        # Repository info
        repo_name = self.repo_info.get('name', 'Unknown')
        repo_path = self.repo_info.get('path', 'Unknown')
        lines.append(f"Repository: {repo_name}")
        lines.append(f"Path: {repo_path}")
        lines.append(f"Scanned: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Overall health
        overall = self.metrics.metrics['overall_health']
        lines.append("-" * 70)
        lines.append("OVERALL HEALTH")
        lines.append("-" * 70)
        lines.append(f"Score: {overall['score']}/100 (Grade: {overall['grade']}) - {overall['status']}")
        lines.append(self._create_progress_bar(overall['score']))
        lines.append("")
        
        # Individual metrics
        metric_order = [
            ('documentation_coverage', 'Documentation Coverage'),
            ('code_quality', 'Code Quality'),
            ('dependency_health', 'Dependency Health'),
            ('maintainability', 'Maintainability Index'),
            ('license_compliance', 'License Compliance')
        ]
        
        for metric_key, metric_name in metric_order:
            metric = self.metrics.metrics[metric_key]
            lines.append("-" * 70)
            lines.append(metric_name.upper())
            lines.append("-" * 70)
            lines.append(f"Score: {metric['score']}/100 (Grade: {metric['grade']}) - {metric['status']}")
            lines.append(self._create_progress_bar(metric['score']))
            
            if metric['reasons']:
                lines.append("\nDetails:")
                for reason in metric['reasons']:
                    lines.append(f"  • {reason}")
            lines.append("")
        
        # Recommendations
        lines.append("=" * 70)
        lines.append("RECOMMENDATIONS")
        lines.append("=" * 70)
        recommendations = self._generate_recommendations()
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
        else:
            lines.append("No recommendations - project is in excellent health!")
        lines.append("")
        
        lines.append("=" * 70)
        
        return '\n'.join(lines)
    
    def _create_progress_bar(self, score: int, width: int = 50) -> str:
        """Create a text progress bar."""
        filled = int((score / 100) * width)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {score}%"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        # Documentation recommendations
        doc_score = self.metrics.metrics['documentation_coverage']['score']
        if doc_score < 60:
            recommendations.append("Add comprehensive documentation (README, API docs, examples)")
        elif doc_score < 80:
            recommendations.append("Enhance documentation with more examples and API references")
        
        # Code quality recommendations
        quality_score = self.metrics.metrics['code_quality']['score']
        if quality_score < 70:
            recommendations.append("Address TODO/FIXME items and refactor complex code")
        
        todos = self.repo_info.get('todos', [])
        if len(todos) > 10:
            recommendations.append(f"Resolve {len(todos)} TODO/FIXME items in the codebase")
        
        # Dependency recommendations
        dep_score = self.metrics.metrics['dependency_health']['score']
        if dep_score < 70:
            recommendations.append("Review and update outdated dependencies")
        
        # Maintainability recommendations
        maint_score = self.metrics.metrics['maintainability']['score']
        if maint_score < 70:
            recommendations.append("Improve code documentation with more comments")
        
        # License recommendations
        license_score = self.metrics.metrics['license_compliance']['score']
        if license_score < 60:
            recommendations.append("Add a license file to clarify usage terms")
        
        return recommendations
    
    def export_to_dict(self) -> Dict:
        """Export dashboard data to dictionary."""
        return {
            'repository': {
                'name': self.repo_info.get('name', 'Unknown'),
                'path': self.repo_info.get('path', 'Unknown'),
                'scan_date': datetime.now().isoformat()
            },
            'metrics': self.metrics.get_metrics(),
            'summary': self.metrics.get_summary(),
            'recommendations': self._generate_recommendations()
        }
