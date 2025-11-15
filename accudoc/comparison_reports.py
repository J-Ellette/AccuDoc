"""
Comparison Reports module for AccuDoc.
Compares metrics across multiple repositories.
"""

from typing import Dict, List, Optional
from pathlib import Path
import json


class RepositoryComparison:
    """Compares multiple repositories and generates comparison reports."""
    
    def __init__(self):
        """Initialize repository comparison."""
        self.repositories = []
        self.comparison_data = {}
    
    def add_repository(self, repo_info: Dict, name: Optional[str] = None):
        """
        Add a repository to compare.
        
        Args:
            repo_info: Repository information from scanner
            name: Optional custom name for the repository
        """
        if name is None:
            name = repo_info.get('name', f'Repo_{len(self.repositories) + 1}')
        
        self.repositories.append({
            'name': name,
            'info': repo_info
        })
    
    def load_from_json(self, json_path: str, name: Optional[str] = None):
        """
        Load repository data from JSON file.
        
        Args:
            json_path: Path to JSON file with repository data
            name: Optional custom name for the repository
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            repo_info = json.load(f)
        
        if name is None:
            name = Path(json_path).stem
        
        self.add_repository(repo_info, name)
    
    def compare(self) -> Dict:
        """
        Compare all added repositories.
        
        Returns:
            Dictionary containing comparison data
        """
        if len(self.repositories) < 2:
            raise ValueError("At least 2 repositories are required for comparison")
        
        comparison = {
            'repository_count': len(self.repositories),
            'repository_names': [r['name'] for r in self.repositories],
            'metrics': {}
        }
        
        # Compare basic statistics
        comparison['metrics']['files'] = self._compare_files()
        comparison['metrics']['languages'] = self._compare_languages()
        comparison['metrics']['code_stats'] = self._compare_code_stats()
        comparison['metrics']['dependencies'] = self._compare_dependencies()
        comparison['metrics']['documentation'] = self._compare_documentation()
        comparison['metrics']['todos'] = self._compare_todos()
        comparison['metrics']['license'] = self._compare_licenses()
        
        # Calculate health scores if available
        health_scores = self._compare_health_scores()
        if health_scores:
            comparison['metrics']['health'] = health_scores
        
        # Add rankings
        comparison['rankings'] = self._calculate_rankings(comparison['metrics'])
        
        # Add summary
        comparison['summary'] = self._generate_summary(comparison)
        
        self.comparison_data = comparison
        return comparison
    
    def _compare_files(self) -> Dict:
        """Compare file counts."""
        data = {}
        for repo in self.repositories:
            info = repo['info']
            data[repo['name']] = {
                'count': info.get('files_count', 0),
                'languages': len(info.get('languages', {}))
            }
        
        # Find max/min
        counts = [d['count'] for d in data.values()]
        data['_max'] = max(counts) if counts else 0
        data['_min'] = min(counts) if counts else 0
        data['_avg'] = sum(counts) / len(counts) if counts else 0
        
        return data
    
    def _compare_languages(self) -> Dict:
        """Compare programming languages."""
        data = {}
        all_languages = set()
        
        for repo in self.repositories:
            info = repo['info']
            languages = info.get('languages', {})
            data[repo['name']] = languages
            all_languages.update(languages.keys())
        
        data['_all_languages'] = sorted(list(all_languages))
        data['_language_count'] = len(all_languages)
        
        return data
    
    def _compare_code_stats(self) -> Dict:
        """Compare code statistics."""
        data = {}
        
        for repo in self.repositories:
            info = repo['info']
            stats = info.get('statistics', {})
            
            data[repo['name']] = {
                'total_lines': stats.get('total_lines', 0),
                'code_lines': stats.get('code_lines', 0),
                'comment_lines': stats.get('comment_lines', 0),
                'blank_lines': stats.get('blank_lines', 0),
                'comment_ratio': 0
            }
            
            # Calculate comment ratio
            total = stats.get('total_lines', 0)
            if total > 0:
                ratio = (stats.get('comment_lines', 0) / total) * 100
                data[repo['name']]['comment_ratio'] = round(ratio, 2)
        
        # Calculate averages
        if data:
            total_lines = [d['total_lines'] for d in data.values()]
            data['_avg_total_lines'] = sum(total_lines) / len(total_lines) if total_lines else 0
        
        return data
    
    def _compare_dependencies(self) -> Dict:
        """Compare dependencies."""
        data = {}
        
        for repo in self.repositories:
            info = repo['info']
            dependencies = info.get('dependencies', {})
            
            total_deps = sum(len(deps) if isinstance(deps, list) else 0 
                           for deps in dependencies.values())
            
            data[repo['name']] = {
                'total': total_deps,
                'by_manager': {}
            }
            
            for manager, deps in dependencies.items():
                if isinstance(deps, list):
                    data[repo['name']]['by_manager'][manager] = len(deps)
        
        # Find max/min
        counts = [d['total'] for d in data.values()]
        data['_max'] = max(counts) if counts else 0
        data['_min'] = min(counts) if counts else 0
        
        return data
    
    def _compare_documentation(self) -> Dict:
        """Compare documentation."""
        data = {}
        
        for repo in self.repositories:
            info = repo['info']
            docs = info.get('documentation', [])
            api_docs = info.get('api_docs', [])
            examples = info.get('code_examples', [])
            
            data[repo['name']] = {
                'doc_files': len(docs),
                'api_docs': len(api_docs),
                'examples': len(examples),
                'total': len(docs) + len(api_docs) + len(examples)
            }
        
        return data
    
    def _compare_todos(self) -> Dict:
        """Compare TODO/FIXME counts."""
        data = {}
        
        for repo in self.repositories:
            info = repo['info']
            todos = info.get('todos', [])
            
            data[repo['name']] = {
                'count': len(todos),
                'types': {}
            }
            
            # Count by type
            for todo in todos:
                todo_type = todo.get('type', 'TODO')
                data[repo['name']]['types'][todo_type] = \
                    data[repo['name']]['types'].get(todo_type, 0) + 1
        
        return data
    
    def _compare_licenses(self) -> Dict:
        """Compare licenses."""
        data = {}
        
        for repo in self.repositories:
            info = repo['info']
            license_info = info.get('license', 'Not found')
            data[repo['name']] = license_info
        
        return data
    
    def _compare_health_scores(self) -> Optional[Dict]:
        """Compare health scores if available."""
        # Try to calculate health scores
        try:
            from accudoc.health_dashboard import HealthMetrics
            
            data = {}
            for repo in self.repositories:
                info = repo['info']
                metrics = HealthMetrics(info)
                summary = metrics.get_summary()
                
                data[repo['name']] = {
                    'overall': summary['overall_score'],
                    'documentation': summary['documentation'],
                    'code_quality': summary['code_quality'],
                    'dependencies': summary['dependencies'],
                    'maintainability': summary['maintainability'],
                    'license': summary['license']
                }
            
            return data
        except Exception:
            return None
    
    def _calculate_rankings(self, metrics: Dict) -> Dict:
        """Calculate rankings for repositories."""
        rankings = {}
        
        # Rank by files
        if 'files' in metrics:
            file_data = [(name, data['count']) for name, data in metrics['files'].items() 
                        if not name.startswith('_')]
            file_data.sort(key=lambda x: x[1], reverse=True)
            rankings['by_files'] = [name for name, _ in file_data]
        
        # Rank by code lines
        if 'code_stats' in metrics:
            code_data = [(name, data['total_lines']) for name, data in metrics['code_stats'].items() 
                        if not name.startswith('_')]
            code_data.sort(key=lambda x: x[1], reverse=True)
            rankings['by_code_lines'] = [name for name, _ in code_data]
        
        # Rank by documentation
        if 'documentation' in metrics:
            doc_data = [(name, data['total']) for name, data in metrics['documentation'].items()]
            doc_data.sort(key=lambda x: x[1], reverse=True)
            rankings['by_documentation'] = [name for name, _ in doc_data]
        
        # Rank by health score
        if 'health' in metrics:
            health_data = [(name, data['overall']) for name, data in metrics['health'].items()]
            health_data.sort(key=lambda x: x[1], reverse=True)
            rankings['by_health'] = [name for name, _ in health_data]
        
        return rankings
    
    def _generate_summary(self, comparison: Dict) -> Dict:
        """Generate comparison summary."""
        summary = {
            'total_repositories': comparison['repository_count'],
            'best_performers': {},
            'worst_performers': {}
        }
        
        rankings = comparison.get('rankings', {})
        
        # Best performers
        if 'by_files' in rankings and rankings['by_files']:
            summary['best_performers']['most_files'] = rankings['by_files'][0]
        
        if 'by_code_lines' in rankings and rankings['by_code_lines']:
            summary['best_performers']['most_code'] = rankings['by_code_lines'][0]
        
        if 'by_documentation' in rankings and rankings['by_documentation']:
            summary['best_performers']['most_documented'] = rankings['by_documentation'][0]
        
        if 'by_health' in rankings and rankings['by_health']:
            summary['best_performers']['healthiest'] = rankings['by_health'][0]
        
        # Worst performers
        if 'by_files' in rankings and rankings['by_files']:
            summary['worst_performers']['least_files'] = rankings['by_files'][-1]
        
        if 'by_health' in rankings and rankings['by_health']:
            summary['worst_performers']['needs_improvement'] = rankings['by_health'][-1]
        
        return summary
    
    def generate_report(self) -> str:
        """Generate text comparison report."""
        if not self.comparison_data:
            return "No comparison data available. Run compare() first."
        
        lines = []
        lines.append("=" * 80)
        lines.append("REPOSITORY COMPARISON REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        data = self.comparison_data
        
        lines.append(f"Comparing {data['repository_count']} repositories:")
        for name in data['repository_names']:
            lines.append(f"  • {name}")
        lines.append("")
        
        # File comparison
        lines.append("-" * 80)
        lines.append("FILE STATISTICS")
        lines.append("-" * 80)
        lines.append(f"{'Repository':<30} {'Files':<15} {'Languages':<15}")
        lines.append("-" * 80)
        
        files_data = data['metrics']['files']
        for repo_name in data['repository_names']:
            if repo_name in files_data:
                repo_data = files_data[repo_name]
                lines.append(f"{repo_name:<30} {repo_data['count']:<15} {repo_data['languages']:<15}")
        
        lines.append(f"{'Average':<30} {files_data.get('_avg', 0):<15.0f}")
        lines.append("")
        
        # Code statistics
        lines.append("-" * 80)
        lines.append("CODE STATISTICS")
        lines.append("-" * 80)
        lines.append(f"{'Repository':<30} {'Total Lines':<15} {'Code Lines':<15} {'Comment %':<15}")
        lines.append("-" * 80)
        
        code_data = data['metrics']['code_stats']
        for repo_name in data['repository_names']:
            if repo_name in code_data:
                repo_data = code_data[repo_name]
                lines.append(f"{repo_name:<30} {repo_data['total_lines']:<15} "
                           f"{repo_data['code_lines']:<15} {repo_data['comment_ratio']:<15.1f}%")
        lines.append("")
        
        # Dependencies
        lines.append("-" * 80)
        lines.append("DEPENDENCIES")
        lines.append("-" * 80)
        lines.append(f"{'Repository':<30} {'Total Dependencies':<20}")
        lines.append("-" * 80)
        
        deps_data = data['metrics']['dependencies']
        for repo_name in data['repository_names']:
            if repo_name in deps_data:
                total = deps_data[repo_name]['total']
                lines.append(f"{repo_name:<30} {total:<20}")
        lines.append("")
        
        # Documentation
        lines.append("-" * 80)
        lines.append("DOCUMENTATION")
        lines.append("-" * 80)
        lines.append(f"{'Repository':<30} {'Doc Files':<15} {'API Docs':<15} {'Examples':<15}")
        lines.append("-" * 80)
        
        doc_data = data['metrics']['documentation']
        for repo_name in data['repository_names']:
            if repo_name in doc_data:
                repo_data = doc_data[repo_name]
                lines.append(f"{repo_name:<30} {repo_data['doc_files']:<15} "
                           f"{repo_data['api_docs']:<15} {repo_data['examples']:<15}")
        lines.append("")
        
        # Health scores
        if 'health' in data['metrics']:
            lines.append("-" * 80)
            lines.append("HEALTH SCORES")
            lines.append("-" * 80)
            lines.append(f"{'Repository':<30} {'Overall':<12} {'Docs':<12} {'Quality':<12} {'Deps':<12}")
            lines.append("-" * 80)
            
            health_data = data['metrics']['health']
            for repo_name in data['repository_names']:
                if repo_name in health_data:
                    repo_data = health_data[repo_name]
                    lines.append(f"{repo_name:<30} {repo_data['overall']:<12} "
                               f"{repo_data['documentation']:<12} "
                               f"{repo_data['code_quality']:<12} "
                               f"{repo_data['dependencies']:<12}")
            lines.append("")
        
        # Rankings
        lines.append("-" * 80)
        lines.append("RANKINGS")
        lines.append("-" * 80)
        
        rankings = data['rankings']
        if 'by_health' in rankings:
            lines.append("By Health Score:")
            for i, name in enumerate(rankings['by_health'], 1):
                lines.append(f"  {i}. {name}")
            lines.append("")
        
        if 'by_files' in rankings:
            lines.append("By File Count:")
            for i, name in enumerate(rankings['by_files'], 1):
                lines.append(f"  {i}. {name}")
            lines.append("")
        
        # Summary
        lines.append("=" * 80)
        lines.append("SUMMARY")
        lines.append("=" * 80)
        
        summary = data['summary']
        if 'best_performers' in summary:
            lines.append("Best Performers:")
            for category, name in summary['best_performers'].items():
                lines.append(f"  • {category.replace('_', ' ').title()}: {name}")
        lines.append("")
        
        lines.append("=" * 80)
        
        return '\n'.join(lines)
    
    def export_to_json(self) -> Dict:
        """Export comparison to JSON format."""
        return self.comparison_data
    
    def export_to_csv(self, output_dir: str) -> List[str]:
        """Export comparison to CSV files."""
        import csv
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        data = self.comparison_data
        
        # Summary CSV
        summary_file = output_path / 'comparison_summary.csv'
        with open(summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Repository', 'Files', 'Total Lines', 'Dependencies', 
                           'Doc Files', 'TODOs'])
            
            for repo_name in data['repository_names']:
                files = data['metrics']['files'].get(repo_name, {}).get('count', 0)
                lines = data['metrics']['code_stats'].get(repo_name, {}).get('total_lines', 0)
                deps = data['metrics']['dependencies'].get(repo_name, {}).get('total', 0)
                docs = data['metrics']['documentation'].get(repo_name, {}).get('doc_files', 0)
                todos = data['metrics']['todos'].get(repo_name, {}).get('count', 0)
                
                writer.writerow([repo_name, files, lines, deps, docs, todos])
        
        created_files.append(str(summary_file))
        
        # Health scores CSV (if available)
        if 'health' in data['metrics']:
            health_file = output_path / 'comparison_health.csv'
            with open(health_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Repository', 'Overall', 'Documentation', 'Code Quality', 
                               'Dependencies', 'Maintainability', 'License'])
                
                for repo_name in data['repository_names']:
                    if repo_name in data['metrics']['health']:
                        health = data['metrics']['health'][repo_name]
                        writer.writerow([
                            repo_name,
                            health['overall'],
                            health['documentation'],
                            health['code_quality'],
                            health['dependencies'],
                            health['maintainability'],
                            health['license']
                        ])
            
            created_files.append(str(health_file))
        
        return created_files
