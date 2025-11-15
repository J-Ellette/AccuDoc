"""
Documentation Completeness Score Module for AccuDoc.

This module calculates a completeness score for repository documentation,
identifying gaps and providing actionable recommendations for improvement.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import ast


class CompletenessScorer:
    """Calculator for documentation completeness scores."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the completeness scorer.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.results = {}
    
    def analyze_repository(self) -> Dict[str, Any]:
        """
        Analyze repository and calculate completeness score.
        
        Returns:
            Dictionary containing completeness analysis and score
        """
        results = {
            'scores': {},
            'gaps': [],
            'overall_score': 0.0,
            'grade': '',
            'summary': {}
        }
        
        # Check different aspects of documentation
        results['scores']['readme'] = self._check_readme()
        results['scores']['license'] = self._check_license()
        results['scores']['contributing'] = self._check_contributing()
        results['scores']['code_documentation'] = self._check_code_documentation()
        results['scores']['comments'] = self._check_comments()
        results['scores']['api_docs'] = self._check_api_docs()
        results['scores']['changelog'] = self._check_changelog()
        results['scores']['examples'] = self._check_examples()
        results['scores']['config_docs'] = self._check_config_documentation()
        
        # Calculate overall score
        weights = {
            'readme': 0.25,
            'license': 0.05,
            'contributing': 0.05,
            'code_documentation': 0.30,
            'comments': 0.10,
            'api_docs': 0.10,
            'changelog': 0.05,
            'examples': 0.05,
            'config_docs': 0.05
        }
        
        total_score = 0.0
        for category, weight in weights.items():
            score = results['scores'].get(category, {}).get('score', 0)
            total_score += score * weight
        
        results['overall_score'] = round(total_score, 2)
        results['grade'] = self._calculate_grade(results['overall_score'])
        
        # Identify gaps
        results['gaps'] = self._identify_gaps(results['scores'])
        
        # Create summary
        results['summary'] = {
            'total_files_analyzed': self._count_files(),
            'documented_files': sum(1 for s in results['scores'].values() 
                                   if s.get('score', 0) >= 70),
            'missing_critical': len([g for g in results['gaps'] 
                                    if g['severity'] == 'critical']),
            'missing_important': len([g for g in results['gaps'] 
                                     if g['severity'] == 'important']),
            'missing_optional': len([g for g in results['gaps'] 
                                    if g['severity'] == 'optional'])
        }
        
        return results
    
    def _check_readme(self) -> Dict[str, Any]:
        """Check README file completeness."""
        result = {
            'score': 0,
            'found': False,
            'quality': 'none',
            'sections_found': [],
            'sections_missing': []
        }
        
        # Look for README files
        readme_files = list(self.repo_path.glob('README*'))
        
        if not readme_files:
            result['sections_missing'] = [
                'Installation', 'Usage', 'Features', 'Contributing', 
                'License', 'Description'
            ]
            return result
        
        result['found'] = True
        
        # Read and analyze README
        readme_path = readme_files[0]
        try:
            content = readme_path.read_text(encoding='utf-8').lower()
            
            # Check for essential sections
            sections = {
                'title': bool(re.search(r'^#\s+\w+', content, re.MULTILINE)),
                'description': len(content) > 200,
                'installation': bool(re.search(r'install', content)),
                'usage': bool(re.search(r'usage|how to|getting started', content)),
                'features': bool(re.search(r'feature|what it does', content)),
                'license': bool(re.search(r'license', content)),
                'contributing': bool(re.search(r'contribut', content)),
            }
            
            result['sections_found'] = [k for k, v in sections.items() if v]
            result['sections_missing'] = [k for k, v in sections.items() if not v]
            
            # Calculate score
            score = (len(result['sections_found']) / len(sections)) * 100
            result['score'] = round(score, 2)
            
            # Determine quality
            if score >= 85:
                result['quality'] = 'excellent'
            elif score >= 70:
                result['quality'] = 'good'
            elif score >= 50:
                result['quality'] = 'fair'
            else:
                result['quality'] = 'poor'
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _check_license(self) -> Dict[str, Any]:
        """Check for LICENSE file."""
        result = {'score': 0, 'found': False}
        
        license_files = list(self.repo_path.glob('LICENSE*'))
        if license_files:
            result['found'] = True
            result['score'] = 100
            result['file'] = str(license_files[0].name)
        
        return result
    
    def _check_contributing(self) -> Dict[str, Any]:
        """Check for CONTRIBUTING file."""
        result = {'score': 0, 'found': False}
        
        contrib_files = list(self.repo_path.glob('CONTRIBUTING*'))
        if contrib_files:
            result['found'] = True
            result['score'] = 100
            result['file'] = str(contrib_files[0].name)
        
        return result
    
    def _check_code_documentation(self) -> Dict[str, Any]:
        """Check code documentation (docstrings, comments)."""
        result = {
            'score': 0,
            'total_functions': 0,
            'documented_functions': 0,
            'total_classes': 0,
            'documented_classes': 0,
            'total_modules': 0,
            'documented_modules': 0
        }
        
        python_files = list(self.repo_path.rglob('*.py'))
        python_files = [f for f in python_files 
                       if '.git' not in str(f) and '__pycache__' not in str(f)]
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                # Check module docstring
                result['total_modules'] += 1
                if ast.get_docstring(tree):
                    result['documented_modules'] += 1
                
                # Check functions and classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        result['total_functions'] += 1
                        if ast.get_docstring(node):
                            result['documented_functions'] += 1
                    elif isinstance(node, ast.ClassDef):
                        result['total_classes'] += 1
                        if ast.get_docstring(node):
                            result['documented_classes'] += 1
            except Exception:
                continue
        
        # Calculate score
        total_items = (result['total_modules'] + result['total_functions'] + 
                      result['total_classes'])
        documented_items = (result['documented_modules'] + 
                           result['documented_functions'] + 
                           result['documented_classes'])
        
        if total_items > 0:
            result['score'] = round((documented_items / total_items) * 100, 2)
        
        return result
    
    def _check_comments(self) -> Dict[str, Any]:
        """Check inline comments in code."""
        result = {
            'score': 0,
            'total_lines': 0,
            'comment_lines': 0,
            'comment_ratio': 0.0
        }
        
        python_files = list(self.repo_path.rglob('*.py'))
        python_files = [f for f in python_files 
                       if '.git' not in str(f) and '__pycache__' not in str(f)]
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('"""') and not stripped.startswith("'''"):
                        result['total_lines'] += 1
                        if '#' in line:
                            result['comment_lines'] += 1
            except Exception:
                continue
        
        if result['total_lines'] > 0:
            result['comment_ratio'] = round(
                (result['comment_lines'] / result['total_lines']) * 100, 2
            )
            
            # Good comment ratio is between 10-30%
            if 10 <= result['comment_ratio'] <= 30:
                result['score'] = 100
            elif result['comment_ratio'] < 10:
                result['score'] = result['comment_ratio'] * 10
            else:
                result['score'] = max(0, 100 - (result['comment_ratio'] - 30) * 2)
            
            result['score'] = round(result['score'], 2)
        
        return result
    
    def _check_api_docs(self) -> Dict[str, Any]:
        """Check for API documentation."""
        result = {'score': 0, 'found': False, 'files': []}
        
        # Look for common API doc patterns
        api_patterns = ['**/api.md', '**/API.md', '**/docs/api/*', '**/api/**/*.md']
        
        for pattern in api_patterns:
            files = list(self.repo_path.glob(pattern))
            if files:
                result['found'] = True
                result['files'].extend([str(f.relative_to(self.repo_path)) for f in files])
        
        if result['found']:
            result['score'] = 100
        
        return result
    
    def _check_changelog(self) -> Dict[str, Any]:
        """Check for CHANGELOG file."""
        result = {'score': 0, 'found': False}
        
        changelog_files = list(self.repo_path.glob('CHANGELOG*'))
        if changelog_files:
            result['found'] = True
            result['score'] = 100
            result['file'] = str(changelog_files[0].name)
        
        return result
    
    def _check_examples(self) -> Dict[str, Any]:
        """Check for examples or demos."""
        result = {'score': 0, 'found': False, 'count': 0}
        
        # Look for example files
        example_patterns = ['**/example*.py', '**/demo*.py', '**/examples/**/*', 
                           '**/demos/**/*', '**/sample*.py']
        
        example_files = []
        for pattern in example_patterns:
            example_files.extend(self.repo_path.glob(pattern))
        
        example_files = [f for f in example_files 
                        if '.git' not in str(f) and '__pycache__' not in str(f)]
        
        if example_files:
            result['found'] = True
            result['count'] = len(example_files)
            # Score based on number of examples
            result['score'] = min(100, len(example_files) * 20)
        
        return result
    
    def _check_config_documentation(self) -> Dict[str, Any]:
        """Check if configuration files are documented."""
        result = {
            'score': 0,
            'total_config_files': 0,
            'documented_config_files': 0
        }
        
        # Common config files
        config_patterns = ['*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.cfg']
        
        for pattern in config_patterns:
            config_files = list(self.repo_path.glob(pattern))
            config_files = [f for f in config_files 
                           if '.git' not in str(f) and 'node_modules' not in str(f)]
            
            for config_file in config_files:
                result['total_config_files'] += 1
                
                # Check if there's documentation near the config file
                doc_file = config_file.parent / f"{config_file.stem}_README.md"
                if doc_file.exists():
                    result['documented_config_files'] += 1
                else:
                    # Check for comments in the config file itself
                    try:
                        content = config_file.read_text(encoding='utf-8')
                        if '#' in content or '//' in content:
                            result['documented_config_files'] += 1
                    except Exception:
                        pass
        
        if result['total_config_files'] > 0:
            result['score'] = round(
                (result['documented_config_files'] / result['total_config_files']) * 100, 2
            )
        
        return result
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
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
    
    def _identify_gaps(self, scores: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify documentation gaps."""
        gaps = []
        
        # Check README
        readme = scores.get('readme', {})
        if not readme.get('found'):
            gaps.append({
                'category': 'README',
                'severity': 'critical',
                'message': 'No README file found',
                'recommendation': 'Create a README.md file with project overview, installation, and usage instructions'
            })
        elif readme.get('sections_missing'):
            gaps.append({
                'category': 'README',
                'severity': 'important',
                'message': f"README missing sections: {', '.join(readme['sections_missing'])}",
                'recommendation': 'Add missing sections to provide complete project documentation'
            })
        
        # Check License
        if not scores.get('license', {}).get('found'):
            gaps.append({
                'category': 'License',
                'severity': 'important',
                'message': 'No LICENSE file found',
                'recommendation': 'Add a LICENSE file to clarify usage rights'
            })
        
        # Check code documentation
        code_docs = scores.get('code_documentation', {})
        if code_docs.get('score', 0) < 50:
            gaps.append({
                'category': 'Code Documentation',
                'severity': 'critical',
                'message': f"Only {code_docs.get('score', 0)}% of code is documented",
                'recommendation': 'Add docstrings to modules, classes, and functions'
            })
        
        # Check CONTRIBUTING
        if not scores.get('contributing', {}).get('found'):
            gaps.append({
                'category': 'Contributing Guidelines',
                'severity': 'optional',
                'message': 'No CONTRIBUTING file found',
                'recommendation': 'Add CONTRIBUTING.md to help potential contributors'
            })
        
        # Check CHANGELOG
        if not scores.get('changelog', {}).get('found'):
            gaps.append({
                'category': 'Changelog',
                'severity': 'optional',
                'message': 'No CHANGELOG file found',
                'recommendation': 'Add CHANGELOG.md to track project changes'
            })
        
        # Check examples
        if not scores.get('examples', {}).get('found'):
            gaps.append({
                'category': 'Examples',
                'severity': 'optional',
                'message': 'No example or demo files found',
                'recommendation': 'Add example code to help users get started'
            })
        
        return gaps
    
    def _count_files(self) -> int:
        """Count total number of files in repository."""
        count = 0
        for _ in self.repo_path.rglob('*'):
            if _.is_file() and '.git' not in str(_):
                count += 1
        return count
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a markdown report of completeness analysis.
        
        Args:
            results: Results from analyze_repository()
            
        Returns:
            Markdown formatted report
        """
        report = ["# Documentation Completeness Report\n"]
        
        # Overall Score
        report.append("## Overall Score\n")
        score = results['overall_score']
        grade = results['grade']
        
        # Score bar visualization
        bar_length = int(score / 5)
        bar = '█' * bar_length + '░' * (20 - bar_length)
        
        report.append(f"**Score: {score}/100** (Grade: **{grade}**)\n")
        report.append(f"```\n{bar} {score}%\n```\n")
        
        # Summary
        summary = results['summary']
        report.append("## Summary\n")
        report.append(f"- **Total Files**: {summary['total_files_analyzed']}")
        report.append(f"- **Critical Gaps**: {summary['missing_critical']}")
        report.append(f"- **Important Gaps**: {summary['missing_important']}")
        report.append(f"- **Optional Gaps**: {summary['missing_optional']}\n")
        
        # Category Scores
        report.append("## Category Scores\n")
        report.append("| Category | Score | Status |")
        report.append("|----------|-------|--------|")
        
        scores = results['scores']
        for category, data in scores.items():
            score_val = data.get('score', 0)
            status = '✅' if score_val >= 70 else ('⚠️' if score_val >= 50 else '❌')
            category_name = category.replace('_', ' ').title()
            report.append(f"| {category_name} | {score_val}% | {status} |")
        report.append("")
        
        # Gaps
        gaps = results['gaps']
        if gaps:
            # Critical gaps
            critical = [g for g in gaps if g['severity'] == 'critical']
            if critical:
                report.append("## Critical Gaps\n")
                for gap in critical:
                    report.append(f"### ❌ {gap['category']}\n")
                    report.append(f"**Issue**: {gap['message']}\n")
                    report.append(f"**Recommendation**: {gap['recommendation']}\n")
            
            # Important gaps
            important = [g for g in gaps if g['severity'] == 'important']
            if important:
                report.append("## Important Gaps\n")
                for gap in important:
                    report.append(f"### ⚠️ {gap['category']}\n")
                    report.append(f"**Issue**: {gap['message']}\n")
                    report.append(f"**Recommendation**: {gap['recommendation']}\n")
            
            # Optional gaps
            optional = [g for g in gaps if g['severity'] == 'optional']
            if optional:
                report.append("## Optional Improvements\n")
                for gap in optional:
                    report.append(f"### 💡 {gap['category']}\n")
                    report.append(f"**Suggestion**: {gap['message']}\n")
                    report.append(f"**Recommendation**: {gap['recommendation']}\n")
        
        # Recommendations
        report.append("## Next Steps\n")
        report.append("1. **Address critical gaps first** - These are essential for project usability")
        report.append("2. **Improve code documentation** - Add docstrings to all public APIs")
        report.append("3. **Complete README** - Ensure all essential sections are present")
        report.append("4. **Add examples** - Help users get started quickly")
        report.append("5. **Maintain documentation** - Keep docs updated as code changes\n")
        
        return '\n'.join(report)
