"""
Documentation coverage analyzer for AccuDoc.

Measures what's documented vs. what isn't by analyzing:
- Docstrings/JSDoc comments for functions and classes
- README and documentation files
- Code comments vs. code ratio
- API documentation completeness
"""

import re
import logging
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from collections import defaultdict


class DocumentationCoverageAnalyzer:
    """Analyzes documentation coverage in a codebase."""
    
    def __init__(self, repo_path: str):
        """
        Initialize documentation coverage analyzer.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.doc_coverage')
        
    def analyze_python_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Analyze Python file for documentation coverage.
        
        Args:
            filepath: Path to Python file
            
        Returns:
            Documentation coverage metrics
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find all function and class definitions
            functions = list(re.finditer(r'^(?:async\s+)?def\s+(\w+)\s*\(', content, re.MULTILINE))
            classes = list(re.finditer(r'^class\s+(\w+)', content, re.MULTILINE))
            
            total_items = len(functions) + len(classes)
            
            if total_items == 0:
                return None
            
            # Count documented items (those with docstrings)
            documented = 0
            undocumented_items = []
            
            # Check functions
            for match in functions:
                func_name = match.group(1)
                # Skip private functions (starting with _) unless they're special methods
                if func_name.startswith('_') and not (func_name.startswith('__') and func_name.endswith('__')):
                    total_items -= 1
                    continue
                
                # Look for docstring after function definition
                func_start = match.end()
                func_section = content[func_start:func_start+200]
                
                if '"""' in func_section or "'''" in func_section:
                    documented += 1
                else:
                    undocumented_items.append(f"function {func_name}")
            
            # Check classes
            for match in classes:
                class_name = match.group(1)
                # Skip private classes
                if class_name.startswith('_'):
                    total_items -= 1
                    continue
                
                # Look for docstring after class definition
                class_start = match.end()
                class_section = content[class_start:class_start+200]
                
                if '"""' in class_section or "'''" in class_section:
                    documented += 1
                else:
                    undocumented_items.append(f"class {class_name}")
            
            if total_items == 0:
                return None
            
            coverage = (documented / total_items * 100) if total_items > 0 else 0
            
            return {
                'file': str(filepath.relative_to(self.repo_path)),
                'language': 'python',
                'total_items': total_items,
                'documented': documented,
                'undocumented': total_items - documented,
                'coverage': round(coverage, 2),
                'undocumented_items': undocumented_items[:10]  # Limit to first 10
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing Python file {filepath}: {e}")
            return None
    
    def analyze_javascript_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript file for documentation coverage.
        
        Args:
            filepath: Path to JS/TS file
            
        Returns:
            Documentation coverage metrics
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find all function and class definitions
            functions = list(re.finditer(
                r'(?:export\s+)?(?:async\s+)?function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(',
                content
            ))
            classes = list(re.finditer(r'(?:export\s+)?class\s+(\w+)', content))
            
            total_items = len(functions) + len(classes)
            
            if total_items == 0:
                return None
            
            # Count documented items (those with JSDoc comments)
            documented = 0
            undocumented_items = []
            
            # Check functions
            for match in functions:
                func_name = match.group(1) or match.group(2)
                if not func_name:
                    continue
                
                # Skip private functions (starting with _)
                if func_name.startswith('_'):
                    total_items -= 1
                    continue
                
                # Look for JSDoc comment before function
                func_start = match.start()
                # Look back up to 500 characters for JSDoc
                look_back = max(0, func_start - 500)
                section = content[look_back:func_start]
                
                if '/**' in section and '*/' in section:
                    documented += 1
                else:
                    undocumented_items.append(f"function {func_name}")
            
            # Check classes
            for match in classes:
                class_name = match.group(1)
                
                # Skip private classes
                if class_name.startswith('_'):
                    total_items -= 1
                    continue
                
                # Look for JSDoc comment before class
                class_start = match.start()
                look_back = max(0, class_start - 500)
                section = content[look_back:class_start]
                
                if '/**' in section and '*/' in section:
                    documented += 1
                else:
                    undocumented_items.append(f"class {class_name}")
            
            if total_items == 0:
                return None
            
            coverage = (documented / total_items * 100) if total_items > 0 else 0
            
            return {
                'file': str(filepath.relative_to(self.repo_path)),
                'language': 'javascript',
                'total_items': total_items,
                'documented': documented,
                'undocumented': total_items - documented,
                'coverage': round(coverage, 2),
                'undocumented_items': undocumented_items[:10]
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing JavaScript file {filepath}: {e}")
            return None
    
    def analyze_directory(self, dirpath: Path = None) -> List[Dict[str, Any]]:
        """
        Analyze documentation coverage for all code files.
        
        Args:
            dirpath: Directory to analyze (defaults to repo root)
            
        Returns:
            List of file analysis results
        """
        if dirpath is None:
            dirpath = self.repo_path
        
        results = []
        
        # Analyze Python files
        for filepath in dirpath.rglob('*.py'):
            # Skip common directories
            if any(part in filepath.parts for part in ['venv', '.venv', '__pycache__', 'tests', 'test']):
                continue
            
            result = self.analyze_python_file(filepath)
            if result:
                results.append(result)
        
        # Analyze JavaScript/TypeScript files
        for ext in ['.js', '.ts', '.jsx', '.tsx']:
            for filepath in dirpath.rglob(f'*{ext}'):
                # Skip common directories
                if any(part in filepath.parts for part in ['node_modules', 'dist', 'build']):
                    continue
                
                result = self.analyze_javascript_file(filepath)
                if result:
                    results.append(result)
        
        return results
    
    def calculate_overall_coverage(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall documentation coverage statistics.
        
        Args:
            results: Results from analyze_directory()
            
        Returns:
            Overall coverage statistics
        """
        if not results:
            return {
                'total_files': 0,
                'total_items': 0,
                'documented': 0,
                'coverage': 0
            }
        
        total_items = sum(r['total_items'] for r in results)
        documented = sum(r['documented'] for r in results)
        
        coverage = (documented / total_items * 100) if total_items > 0 else 0
        
        # Group by language
        by_language = defaultdict(lambda: {'items': 0, 'documented': 0})
        for result in results:
            lang = result['language']
            by_language[lang]['items'] += result['total_items']
            by_language[lang]['documented'] += result['documented']
        
        # Calculate language-specific coverage
        for lang in by_language:
            items = by_language[lang]['items']
            documented = by_language[lang]['documented']
            by_language[lang]['coverage'] = (documented / items * 100) if items > 0 else 0
        
        # Find files with low coverage
        low_coverage_files = sorted(
            [r for r in results if r['coverage'] < 50],
            key=lambda x: x['coverage']
        )
        
        # Find completely undocumented files
        undocumented_files = [r for r in results if r['documented'] == 0]
        
        return {
            'total_files': len(results),
            'total_items': total_items,
            'documented': documented,
            'undocumented': total_items - documented,
            'coverage': round(coverage, 2),
            'by_language': dict(by_language),
            'low_coverage_files': low_coverage_files[:10],
            'undocumented_files': undocumented_files[:10]
        }
    
    def generate_report(self, results: List[Dict[str, Any]], 
                       overall: Dict[str, Any] = None) -> str:
        """
        Generate documentation coverage report.
        
        Args:
            results: Results from analyze_directory()
            overall: Optional pre-calculated overall stats
            
        Returns:
            Markdown formatted report
        """
        if not results:
            return "# Documentation Coverage Report\n\nNo code files found to analyze."
        
        if overall is None:
            overall = self.calculate_overall_coverage(results)
        
        md = []
        md.append("# Documentation Coverage Report\n")
        
        # Overall statistics
        coverage = overall['coverage']
        md.append("## Overall Statistics\n")
        md.append(f"**Files Analyzed**: {overall['total_files']}")
        md.append(f"**Total Items**: {overall['total_items']} (functions, classes, methods)")
        md.append(f"**Documented**: {overall['documented']}")
        md.append(f"**Undocumented**: {overall['undocumented']}")
        md.append(f"**Coverage**: {coverage:.1f}%\n")
        
        # Coverage badge
        if coverage >= 80:
            badge = "🟢 Excellent"
            color = "brightgreen"
        elif coverage >= 60:
            badge = "🟡 Good"
            color = "yellow"
        elif coverage >= 40:
            badge = "🟠 Fair"
            color = "orange"
        else:
            badge = "🔴 Poor"
            color = "red"
        
        md.append(f"**Status**: {badge}")
        md.append(f"![Coverage](https://img.shields.io/badge/doc--coverage-{coverage:.0f}%25-{color})\n")
        
        # Language breakdown
        if overall['by_language']:
            md.append("## Coverage by Language\n")
            md.append("| Language | Items | Documented | Coverage |")
            md.append("|----------|-------|------------|----------|")
            
            for lang, stats in sorted(overall['by_language'].items()):
                coverage_pct = stats['coverage']
                icon = "✓" if coverage_pct >= 60 else "⚠️"
                md.append(f"| {icon} {lang.title()} | {stats['items']} | {stats['documented']} | {coverage_pct:.1f}% |")
            
            md.append("")
        
        # Undocumented files
        if overall.get('undocumented_files'):
            md.append("## 🔴 Completely Undocumented Files\n")
            md.append("| File | Items | Action |")
            md.append("|------|-------|--------|")
            
            for file_result in overall['undocumented_files']:
                md.append(f"| {file_result['file']} | {file_result['total_items']} | Add docstrings |")
            
            if len(overall['undocumented_files']) >= 10:
                md.append(f"\n*Limited to first 10 files*")
            md.append("")
        
        # Low coverage files
        if overall.get('low_coverage_files') and not overall.get('undocumented_files'):
            md.append("## ⚠️ Low Coverage Files (<50%)\n")
            md.append("| File | Coverage | Documented | Total |")
            md.append("|------|----------|------------|-------|")
            
            for file_result in overall['low_coverage_files'][:10]:
                md.append(
                    f"| {file_result['file']} | {file_result['coverage']:.1f}% | "
                    f"{file_result['documented']} | {file_result['total_items']} |"
                )
            
            if len(overall['low_coverage_files']) > 10:
                md.append(f"\n*... and {len(overall['low_coverage_files']) - 10} more files*")
            md.append("")
        
        # Recommendations
        md.append("## Recommendations\n")
        
        if coverage < 40:
            md.append("- 🔴 **Critical**: Documentation coverage is very low")
            md.append("- Start by documenting public APIs and main entry points")
            md.append("- Create a documentation standard for the project")
        elif coverage < 60:
            md.append("- 🟠 **Important**: Improve documentation coverage")
            md.append("- Focus on documenting public interfaces")
            md.append("- Add docstrings to frequently used functions")
        elif coverage < 80:
            md.append("- 🟡 **Good progress**: Continue improving coverage")
            md.append("- Document remaining public APIs")
            md.append("- Review and improve existing documentation")
        else:
            md.append("- 🟢 **Excellent**: Maintain high documentation standards")
            md.append("- Keep documentation up-to-date with code changes")
            md.append("- Consider adding more detailed examples")
        
        md.append("\n**Documentation Tips**:")
        md.append("- Use docstrings/JSDoc for all public functions and classes")
        md.append("- Include parameter descriptions and return types")
        md.append("- Add usage examples for complex APIs")
        md.append("- Keep documentation concise but informative\n")
        
        return '\n'.join(md)
