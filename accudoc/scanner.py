"""Repository scanner module for analyzing repository contents."""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
import re
import json


class RepositoryScanner:
    """Scans and analyzes repository structure and contents."""
    
    def __init__(self, repo_path: str, progress_callback=None):
        """
        Initialize the scanner.
        
        Args:
            repo_path: URL or local path to repository
            progress_callback: Optional callback function for progress updates
        """
        self.repo_path = repo_path
        self.is_remote = self._is_remote_repo(repo_path)
        self.temp_dir = None
        self.scan_path = None
        self.progress_callback = progress_callback
        self.use_cache = True
        self.cache_manager = None
        
    def _is_remote_repo(self, path: str) -> bool:
        """Check if the path is a remote repository URL."""
        return path.startswith(('http://', 'https://', 'git@', 'ssh://'))
    
    def _report_progress(self, message: str):
        """Report progress if callback is provided."""
        if self.progress_callback:
            self.progress_callback(message)
    
    def disable_cache(self):
        """Disable caching for this scan."""
        self.use_cache = False
    
    def enable_cache(self):
        """Enable caching for this scan."""
        self.use_cache = True
        
    def scan(self) -> Dict:
        """
        Scan the repository and collect information.
        
        Returns:
            Dictionary containing repository information
        """
        try:
            # Clone if remote, otherwise use local path
            if self.is_remote:
                self._report_progress("Cloning repository...")
                self.scan_path = self._clone_repository()
            else:
                self._report_progress("Loading local repository...")
                self.scan_path = Path(self.repo_path)
                
            if not self.scan_path.exists():
                raise ValueError(f"Repository path does not exist: {self.scan_path}")
            
            # Initialize cache for local repositories
            if self.use_cache and not self.is_remote:
                from accudoc.cache import CacheManager
                self.cache_manager = CacheManager(str(self.scan_path))
                self.cache_manager.initialize()
                self._report_progress("Cache initialized")
            
            # Collect repository information
            self._report_progress("Analyzing file structure...")
            files = self._get_file_structure()
            
            self._report_progress("Detecting languages...")
            languages = self._detect_languages()
            
            self._report_progress("Detecting dependencies...")
            dependencies = self._detect_dependencies()
            
            self._report_progress("Finding documentation...")
            documentation = self._find_documentation()
            
            self._report_progress("Detecting build tools...")
            build_tools = self._detect_build_tools()
            
            self._report_progress("Analyzing scripts...")
            scripts = self._find_scripts()
            
            self._report_progress("Reading README...")
            readme_content = self._read_readme()
            
            self._report_progress("Finding license...")
            license_info = self._find_license()
            
            self._report_progress("Getting git info...")
            git_info = self._get_git_info()
            
            self._report_progress("Calculating code statistics...")
            code_stats = self._get_code_statistics()
            
            self._report_progress("Extracting TODO/FIXME comments...")
            todos = self._extract_todos()
            
            self._report_progress("Extracting API documentation...")
            api_docs = self._extract_api_docs()
            
            self._report_progress("Finding code examples...")
            code_examples = self._find_code_examples()
            
            self._report_progress("Generating architecture diagram...")
            architecture = self._generate_architecture_diagram()
            
            self._report_progress("Analyzing dependencies...")
            dependency_graph = self._generate_dependency_graph()
            
            self._report_progress("Generating badges...")
            badges = self._generate_badges()
            
            self._report_progress("Parsing configuration files...")
            config_files = self._parse_configuration_files()
            
            self._report_progress("Extracting environment variables...")
            env_vars = self._extract_environment_variables()
            
            self._report_progress("Detecting frameworks...")
            frameworks = self._detect_frameworks()
            
            self._report_progress("Extracting type information...")
            type_info = self._extract_type_information()
            
            self._report_progress("Analyzing imports...")
            import_analysis = self._analyze_imports()
            
            repo_info = {
                'path': str(self.scan_path),
                'name': self._get_repo_name(),
                'files': files,
                'languages': languages,
                'dependencies': dependencies,
                'documentation': documentation,
                'build_tools': build_tools,
                'scripts': scripts,
                'readme_content': readme_content,
                'license': license_info,
                'git_info': git_info,
                'code_stats': code_stats,
                'todos': todos,
                'api_docs': api_docs,
                'code_examples': code_examples,
                'architecture': architecture,
                'dependency_graph': dependency_graph,
                'badges': badges,
                'config_files': config_files,
                'env_vars': env_vars,
                'frameworks': frameworks,
                'type_info': type_info,
                'imports': import_analysis,
                'stats': {
                    'total_files': len(files),
                    'total_languages': len(languages),
                    'total_dependencies': sum(len(deps) for deps in dependencies.values()),
                    'total_docs': len(documentation),
                }
            }
            
            # Save cache if enabled
            if self.cache_manager:
                self._report_progress("Saving cache...")
                self.cache_manager.save()
            
            self._report_progress("Scan complete!")
            return repo_info
            
        finally:
            # Cleanup temporary directory if created
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                
    def _clone_repository(self) -> Path:
        """Clone a remote repository to a temporary directory."""
        self.temp_dir = tempfile.mkdtemp(prefix='accudoc_')
        clone_path = Path(self.temp_dir) / 'repo'
        
        try:
            # Use git clone with depth 1 for faster cloning
            subprocess.run(
                ['git', 'clone', '--depth', '1', self.repo_path, str(clone_path)],
                check=True,
                capture_output=True,
                text=True
            )
            return clone_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clone repository: {e.stderr}")
            
    def _get_repo_name(self) -> str:
        """Get the repository name."""
        if self.is_remote:
            # Extract name from URL
            name = self.repo_path.rstrip('/').split('/')[-1]
            return name.replace('.git', '')
        else:
            return Path(self.repo_path).name
            
    def _get_file_structure(self) -> List[str]:
        """Get the file structure of the repository."""
        files = []
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                      'dist', 'build', '.idea', '.vscode', 'target', 'bin', 'obj'}
        
        for root, dirs, filenames in os.walk(self.scan_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(self.scan_path)
                files.append(str(rel_path))
                
        return sorted(files)
        
    def _detect_languages(self) -> Dict[str, int]:
        """Detect programming languages used in the repository."""
        language_extensions = {
            'Python': ['.py'],
            'JavaScript': ['.js', '.jsx'],
            'TypeScript': ['.ts', '.tsx'],
            'Java': ['.java'],
            'C': ['.c', '.h'],
            'C++': ['.cpp', '.hpp', '.cc', '.cxx'],
            'C#': ['.cs'],
            'Go': ['.go'],
            'Ruby': ['.rb'],
            'PHP': ['.php'],
            'Swift': ['.swift'],
            'Kotlin': ['.kt'],
            'Rust': ['.rs'],
            'Shell': ['.sh', '.bash'],
            'HTML': ['.html', '.htm'],
            'CSS': ['.css', '.scss', '.sass'],
            'SQL': ['.sql'],
            'R': ['.r', '.R'],
            'Perl': ['.pl'],
            'Scala': ['.scala'],
            'Dart': ['.dart'],
            'Lua': ['.lua'],
        }
        
        language_counts = {}
        
        for root, dirs, files in os.walk(self.scan_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__'}]
            
            for filename in files:
                ext = Path(filename).suffix.lower()
                for lang, extensions in language_extensions.items():
                    if ext in extensions:
                        language_counts[lang] = language_counts.get(lang, 0) + 1
                        
        return language_counts
        
    def _detect_dependencies(self) -> Dict[str, List[str]]:
        """Detect dependency files and package managers."""
        dependencies = {}
        
        dependency_files = {
            'Python': ['requirements.txt', 'Pipfile', 'pyproject.toml', 'setup.py'],
            'JavaScript/Node': ['package.json', 'yarn.lock', 'package-lock.json'],
            'Ruby': ['Gemfile', 'Gemfile.lock'],
            'Java/Maven': ['pom.xml'],
            'Java/Gradle': ['build.gradle', 'build.gradle.kts'],
            'Go': ['go.mod', 'go.sum'],
            'Rust': ['Cargo.toml', 'Cargo.lock'],
            'PHP': ['composer.json', 'composer.lock'],
            'C#/.NET': ['*.csproj', '*.sln', 'packages.config'],
        }
        
        for category, filenames in dependency_files.items():
            found = []
            for filename in filenames:
                if '*' in filename:
                    # Handle wildcards
                    pattern = filename.replace('*', '.*')
                    for file in self._get_file_structure():
                        if re.match(pattern, Path(file).name):
                            found.append(file)
                else:
                    file_path = self.scan_path / filename
                    if file_path.exists():
                        found.append(filename)
            if found:
                dependencies[category] = found
                
        return dependencies
        
    def _detect_build_tools(self) -> List[str]:
        """Detect build tools and configuration files."""
        build_files = {
            'Makefile': 'Make',
            'CMakeLists.txt': 'CMake',
            'build.gradle': 'Gradle',
            'pom.xml': 'Maven',
            'Cargo.toml': 'Cargo',
            'package.json': 'npm/yarn',
            'setup.py': 'Python setuptools',
            'pyproject.toml': 'Python build',
            'Dockerfile': 'Docker',
            'docker-compose.yml': 'Docker Compose',
            '.travis.yml': 'Travis CI',
            '.gitlab-ci.yml': 'GitLab CI',
            'Jenkinsfile': 'Jenkins',
            '.github/workflows': 'GitHub Actions',
        }
        
        detected = []
        for file, tool in build_files.items():
            path = self.scan_path / file
            if path.exists():
                detected.append(tool)
                
        return detected
        
    def _find_documentation(self) -> List[str]:
        """Find documentation files in the repository."""
        doc_patterns = ['README', 'CHANGELOG', 'CONTRIBUTING', 'LICENSE', 
                       'DOCS', 'API', 'GUIDE', 'TUTORIAL']
        doc_extensions = ['.md', '.rst', '.txt', '']
        
        docs = []
        for file in self._get_file_structure():
            file_upper = file.upper()
            for pattern in doc_patterns:
                if pattern in file_upper:
                    docs.append(file)
                    break
                    
        return docs
        
    def _find_scripts(self) -> Dict[str, List[str]]:
        """Find build, test, and run scripts."""
        scripts = {
            'build': [],
            'test': [],
            'run': [],
            'install': [],
        }
        
        # Check package.json scripts
        package_json = self.scan_path / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    if 'scripts' in data:
                        for script_name, script_cmd in data['scripts'].items():
                            if 'build' in script_name:
                                scripts['build'].append(f"npm run {script_name}")
                            elif 'test' in script_name:
                                scripts['test'].append(f"npm run {script_name}")
                            elif 'start' in script_name or 'dev' in script_name:
                                scripts['run'].append(f"npm run {script_name}")
                            elif 'install' in script_name:
                                scripts['install'].append(f"npm run {script_name}")
            except Exception:
                pass
                
        # Check Makefile
        makefile = self.scan_path / 'Makefile'
        if makefile.exists():
            try:
                with open(makefile, 'r') as f:
                    content = f.read()
                    targets = re.findall(r'^([a-zA-Z_-]+):', content, re.MULTILINE)
                    for target in targets:
                        if 'build' in target:
                            scripts['build'].append(f"make {target}")
                        elif 'test' in target:
                            scripts['test'].append(f"make {target}")
                        elif 'run' in target or 'start' in target:
                            scripts['run'].append(f"make {target}")
                        elif 'install' in target:
                            scripts['install'].append(f"make {target}")
            except Exception:
                pass
                
        return scripts
        
    def _read_readme(self) -> Optional[str]:
        """Read the README file content."""
        readme_names = ['README.md', 'README.rst', 'README.txt', 'README', 'Readme.md']
        
        for name in readme_names:
            readme_path = self.scan_path / name
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception:
                    pass
                    
        return None
        
    def _find_license(self) -> Optional[str]:
        """Find and identify the license."""
        license_names = ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'COPYING']
        
        for name in license_names:
            license_path = self.scan_path / name
            if license_path.exists():
                try:
                    with open(license_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Try to identify license type
                        if 'MIT' in content:
                            return 'MIT License'
                        elif 'Apache' in content:
                            return 'Apache License'
                        elif 'GPL' in content:
                            return 'GPL License'
                        elif 'BSD' in content:
                            return 'BSD License'
                        else:
                            return 'Custom License'
                except Exception:
                    pass
                    
        return None
        
    def _get_git_info(self) -> Dict:
        """Get git repository information."""
        git_info = {}
        
        git_dir = self.scan_path / '.git'
        if git_dir.exists():
            try:
                # Get current branch
                result = subprocess.run(
                    ['git', '-C', str(self.scan_path), 'rev-parse', '--abbrev-ref', 'HEAD'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                git_info['branch'] = result.stdout.strip()
                
                # Get all branches
                result = subprocess.run(
                    ['git', '-C', str(self.scan_path), 'branch', '-a'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.stdout:
                    branches = []
                    for line in result.stdout.strip().split('\n'):
                        branch = line.strip().lstrip('*').strip()
                        if branch and not branch.startswith('remotes/origin/HEAD'):
                            branches.append(branch)
                    git_info['branches'] = branches[:20]  # Limit to 20
                
                # Get tags
                result = subprocess.run(
                    ['git', '-C', str(self.scan_path), 'tag', '-l'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.stdout:
                    tags = result.stdout.strip().split('\n')
                    git_info['tags'] = [t for t in tags if t][:10]  # Last 10 tags
                
                # Check for submodules
                gitmodules_file = self.scan_path / '.gitmodules'
                if gitmodules_file.exists():
                    submodules = []
                    try:
                        result = subprocess.run(
                            ['git', '-C', str(self.scan_path), 'submodule', 'status'],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        if result.stdout:
                            for line in result.stdout.strip().split('\n'):
                                parts = line.strip().split()
                                if len(parts) >= 2:
                                    submodules.append({
                                        'path': parts[1],
                                        'commit': parts[0].lstrip('-+U')
                                    })
                        git_info['submodules'] = submodules
                    except:
                        pass
                
                # Get last commit
                result = subprocess.run(
                    ['git', '-C', str(self.scan_path), 'log', '-1', '--pretty=format:%H %s'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                git_info['last_commit'] = result.stdout.strip()
                
                # Get remote URL
                result = subprocess.run(
                    ['git', '-C', str(self.scan_path), 'config', '--get', 'remote.origin.url'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                git_info['remote_url'] = result.stdout.strip()
                
                # Get recent commits for changelog (last 20)
                result = subprocess.run(
                    ['git', '-C', str(self.scan_path), 'log', '--pretty=format:%h|%ai|%an|%s', '-20'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.stdout:
                    commits = []
                    for line in result.stdout.strip().split('\n'):
                        parts = line.split('|', 3)
                        if len(parts) == 4:
                            commits.append({
                                'hash': parts[0],
                                'date': parts[1].split()[0],  # Just the date part
                                'author': parts[2],
                                'message': parts[3]
                            })
                    git_info['recent_commits'] = commits
                
                # Get contributor list
                result = subprocess.run(
                    ['git', '-C', str(self.scan_path), 'log', '--format=%an|%ae', '--all'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.stdout:
                    contributors = {}
                    for line in result.stdout.strip().split('\n'):
                        parts = line.split('|')
                        if len(parts) == 2:
                            name, email = parts
                            if name not in contributors:
                                contributors[name] = {'email': email, 'commits': 0}
                            contributors[name]['commits'] += 1
                    
                    # Sort by commit count
                    git_info['contributors'] = sorted(
                        [{'name': name, **info} for name, info in contributors.items()],
                        key=lambda x: x['commits'],
                        reverse=True
                    )
                
            except subprocess.CalledProcessError:
                pass
                
        return git_info
    
    def _get_code_statistics(self) -> Dict:
        """Calculate code statistics."""
        stats = {
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'file_count': 0,
            'by_language': {}
        }
        
        # Language extensions and comment patterns
        language_info = {
            'Python': {
                'extensions': ['.py'],
                'line_comment': '#',
                'block_comment_start': '"""',
                'block_comment_end': '"""'
            },
            'JavaScript': {
                'extensions': ['.js', '.jsx', '.ts', '.tsx'],
                'line_comment': '//',
                'block_comment_start': '/*',
                'block_comment_end': '*/'
            },
            'Java': {
                'extensions': ['.java'],
                'line_comment': '//',
                'block_comment_start': '/*',
                'block_comment_end': '*/'
            },
            'C/C++': {
                'extensions': ['.c', '.cpp', '.h', '.hpp'],
                'line_comment': '//',
                'block_comment_start': '/*',
                'block_comment_end': '*/'
            },
            'Ruby': {
                'extensions': ['.rb'],
                'line_comment': '#',
                'block_comment_start': '=begin',
                'block_comment_end': '=end'
            },
            'Go': {
                'extensions': ['.go'],
                'line_comment': '//',
                'block_comment_start': '/*',
                'block_comment_end': '*/'
            },
            'Rust': {
                'extensions': ['.rs'],
                'line_comment': '//',
                'block_comment_start': '/*',
                'block_comment_end': '*/'
            }
        }
        
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                      'dist', 'build', '.idea', '.vscode', 'target', 'bin', 'obj'}
        
        for root, dirs, files in os.walk(self.scan_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for filename in files:
                file_path = Path(root) / filename
                ext = file_path.suffix.lower()
                
                # Find language for this file
                lang_name = None
                lang_config = None
                for lang, config in language_info.items():
                    if ext in config['extensions']:
                        lang_name = lang
                        lang_config = config
                        break
                
                if not lang_name:
                    continue
                
                # Initialize language stats if needed
                if lang_name not in stats['by_language']:
                    stats['by_language'][lang_name] = {
                        'files': 0,
                        'total_lines': 0,
                        'code_lines': 0,
                        'comment_lines': 0,
                        'blank_lines': 0
                    }
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
                    in_block_comment = False
                    file_stats = {'total': 0, 'code': 0, 'comment': 0, 'blank': 0}
                    
                    for line in lines:
                        stripped = line.strip()
                        file_stats['total'] += 1
                        
                        if not stripped:
                            file_stats['blank'] += 1
                        elif in_block_comment:
                            file_stats['comment'] += 1
                            if lang_config['block_comment_end'] in stripped:
                                in_block_comment = False
                        elif stripped.startswith(lang_config['line_comment']):
                            file_stats['comment'] += 1
                        elif lang_config['block_comment_start'] in stripped:
                            file_stats['comment'] += 1
                            if lang_config['block_comment_end'] not in stripped:
                                in_block_comment = True
                        else:
                            file_stats['code'] += 1
                    
                    # Update totals
                    stats['total_lines'] += file_stats['total']
                    stats['code_lines'] += file_stats['code']
                    stats['comment_lines'] += file_stats['comment']
                    stats['blank_lines'] += file_stats['blank']
                    stats['file_count'] += 1
                    
                    # Update language-specific stats
                    lang_stats = stats['by_language'][lang_name]
                    lang_stats['files'] += 1
                    lang_stats['total_lines'] += file_stats['total']
                    lang_stats['code_lines'] += file_stats['code']
                    lang_stats['comment_lines'] += file_stats['comment']
                    lang_stats['blank_lines'] += file_stats['blank']
                    
                except Exception:
                    pass
        
        return stats
    
    def _extract_todos(self) -> List[Dict]:
        """Extract TODO, FIXME, and similar comments from code."""
        todos = []
        # Look for TODO/FIXME in comments only (with # or // prefix)
        todo_pattern = r'(?:#|//)\s*(?:TODO|FIXME|HACK|XXX|BUG|NOTE)[\s:]*(.+?)$'
        
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                      'dist', 'build', '.idea', '.vscode', 'target', 'bin', 'obj'}
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', 
                          '.h', '.hpp', '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt'}
        
        for root, dirs, files in os.walk(self.scan_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for filename in files:
                file_path = Path(root) / filename
                ext = file_path.suffix.lower()
                
                if ext not in code_extensions:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        match = re.search(todo_pattern, line, re.IGNORECASE)
                        if match:
                            # Extract the TODO type
                            todo_part = match.group(0)
                            todo_type = None
                            for keyword in ['TODO', 'FIXME', 'HACK', 'XXX', 'BUG', 'NOTE']:
                                if keyword in todo_part.upper():
                                    todo_type = keyword
                                    break
                            
                            if todo_type:
                                message = match.group(1).strip() if match.lastindex >= 1 else todo_part
                                
                                rel_path = file_path.relative_to(self.scan_path)
                                todos.append({
                                    'type': todo_type,
                                    'message': message,
                                    'file': str(rel_path),
                                    'line': line_num
                                })
                except Exception:
                    pass
        
        return todos
    
    def _extract_api_docs(self) -> Dict[str, List[Dict]]:
        """Extract API documentation from code (functions, classes, methods)."""
        api_docs = {
            'functions': [],
            'classes': [],
            'methods': []
        }
        
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                      'dist', 'build', '.idea', '.vscode', 'target', 'bin', 'obj'}
        
        # Python API extraction patterns
        python_function_pattern = r'^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)(?:\s*->.*?)?:'
        python_class_pattern = r'^class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        python_docstring_pattern = r'^\s*"""(.*?)"""'
        
        for root, dirs, files in os.walk(self.scan_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for filename in files:
                file_path = Path(root) / filename
                ext = file_path.suffix.lower()
                
                # Focus on Python for now (can be extended)
                if ext == '.py':
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                        
                        rel_path = file_path.relative_to(self.scan_path)
                        current_class = None
                        
                        for i, line in enumerate(lines):
                            # Check for class definitions
                            class_match = re.match(python_class_pattern, line)
                            if class_match:
                                class_name = class_match.group(1)
                                docstring = self._extract_next_docstring(lines, i + 1)
                                
                                api_docs['classes'].append({
                                    'name': class_name,
                                    'file': str(rel_path),
                                    'line': i + 1,
                                    'docstring': docstring
                                })
                                current_class = class_name
                            
                            # Check for function/method definitions
                            func_match = re.match(python_function_pattern, line)
                            if func_match:
                                func_name = func_match.group(1)
                                params = func_match.group(2)
                                docstring = self._extract_next_docstring(lines, i + 1)
                                
                                # Skip private methods/functions (starting with _)
                                if func_name.startswith('_') and not func_name.startswith('__'):
                                    continue
                                
                                entry = {
                                    'name': func_name,
                                    'params': params,
                                    'file': str(rel_path),
                                    'line': i + 1,
                                    'docstring': docstring
                                }
                                
                                if current_class:
                                    entry['class'] = current_class
                                    api_docs['methods'].append(entry)
                                else:
                                    api_docs['functions'].append(entry)
                    
                    except Exception:
                        pass
        
        return api_docs
    
    def _extract_next_docstring(self, lines: List[str], start_idx: int) -> Optional[str]:
        """Extract docstring from the next line(s) after a function/class definition."""
        if start_idx >= len(lines):
            return None
        
        # Check if next line starts a docstring
        line = lines[start_idx].strip()
        if line.startswith('"""') or line.startswith("'''"):
            quote = '"""' if line.startswith('"""') else "'''"
            docstring_lines = []
            
            # Single line docstring
            if line.count(quote) >= 2:
                return line.strip(quote).strip()
            
            # Multi-line docstring
            docstring_lines.append(line.strip(quote))
            for i in range(start_idx + 1, min(start_idx + 20, len(lines))):
                line = lines[i]
                if quote in line:
                    docstring_lines.append(line.split(quote)[0])
                    break
                docstring_lines.append(line.strip())
            
            return ' '.join(docstring_lines).strip()
        
        return None
    
    def _find_code_examples(self) -> List[Dict]:
        """Find code examples in documentation files or example directories."""
        examples = []
        
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                      'dist', 'build', '.idea', '.vscode', 'target', 'bin', 'obj'}
        
        # Look for example directories
        example_dirs = {'examples', 'example', 'samples', 'demos', 'demo'}
        
        for root, dirs, files in os.walk(self.scan_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            # Check if we're in an examples directory
            is_example_dir = any(ex_dir in Path(root).parts for ex_dir in example_dirs)
            
            for filename in files:
                file_path = Path(root) / filename
                ext = file_path.suffix.lower()
                
                # Code files in example directories
                code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', 
                                 '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt'}
                
                if is_example_dir and ext in code_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        rel_path = file_path.relative_to(self.scan_path)
                        examples.append({
                            'name': filename,
                            'file': str(rel_path),
                            'description': f"Example code from {rel_path.parent}",
                            'preview': content[:500] + ('...' if len(content) > 500 else '')
                        })
                    except Exception:
                        pass
                
                # Also look for markdown files with code blocks
                elif ext == '.md' and is_example_dir:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Find code blocks
                        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
                        if code_blocks:
                            rel_path = file_path.relative_to(self.scan_path)
                            for lang, code in code_blocks[:3]:  # Limit to 3 examples per file
                                examples.append({
                                    'name': f"{filename} - {lang or 'code'} example",
                                    'file': str(rel_path),
                                    'language': lang or 'unknown',
                                    'description': f"Code example from documentation",
                                    'preview': code.strip()[:300] + ('...' if len(code.strip()) > 300 else '')
                                })
                    except Exception:
                        pass
        
        return examples[:20]  # Limit to 20 examples
    
    def _generate_architecture_diagram(self) -> Dict:
        """Generate a simple architecture diagram using Mermaid syntax."""
        files = self._get_file_structure()
        languages = self._detect_languages()
        
        # Identify main directories
        directories = set()
        for file in files:
            parts = Path(file).parts
            if len(parts) > 1:
                directories.add(parts[0])
        
        # Build mermaid diagram
        mermaid_lines = ["graph TD"]
        mermaid_lines.append(f"    Root[{self._get_repo_name()}]")
        
        # Add main directories
        for i, dir_name in enumerate(sorted(directories)[:10]):  # Limit to 10 directories
            safe_name = dir_name.replace('-', '_').replace('.', '_')
            mermaid_lines.append(f"    Root --> {safe_name}[{dir_name}]")
        
        # Create simple text-based diagram as fallback
        text_diagram = [f"{self._get_repo_name()}/"]
        for dir_name in sorted(directories)[:15]:
            text_diagram.append(f"├── {dir_name}/")
        
        return {
            'mermaid': '\n'.join(mermaid_lines),
            'text': '\n'.join(text_diagram),
            'directories': sorted(directories)
        }
    
    def _generate_dependency_graph(self) -> Dict:
        """Generate dependency graph showing language and package dependencies."""
        dependencies = self._detect_dependencies()
        languages = self._detect_languages()
        
        # Build mermaid diagram for dependencies
        mermaid_lines = ["graph LR"]
        mermaid_lines.append(f"    Project[{self._get_repo_name()}]")
        
        # Add language nodes
        for lang in languages.keys():
            safe_lang = lang.replace(' ', '_').replace('/', '_')
            mermaid_lines.append(f"    Project --> {safe_lang}Lang[{lang}]")
        
        # Add dependency nodes
        dep_count = 0
        for dep_type, dep_list in dependencies.items():
            safe_type = dep_type.replace(' ', '_').replace('/', '_')
            if dep_list:
                mermaid_lines.append(f"    Project --> {safe_type}Deps[{dep_type} Dependencies]")
                for dep in dep_list[:5]:  # Limit to 5 per type
                    dep_safe = dep.replace('-', '_').replace('.', '_').replace(' ', '_')
                    mermaid_lines.append(f"    {safe_type}Deps --> {dep_safe}[{dep}]")
                    dep_count += 1
                    if dep_count >= 15:  # Overall limit
                        break
            if dep_count >= 15:
                break
        
        # Create simple text representation
        text_lines = ["Dependencies:"]
        for dep_type, dep_list in dependencies.items():
            if dep_list:
                text_lines.append(f"  {dep_type}:")
                for dep in dep_list[:10]:
                    text_lines.append(f"    - {dep}")
        
        return {
            'mermaid': '\n'.join(mermaid_lines),
            'text': '\n'.join(text_lines),
            'summary': dependencies
        }
    
    def _generate_badges(self) -> List[Dict[str, str]]:
        """Generate status badges for the repository."""
        badges = []
        
        # License badge
        license_info = self._find_license()
        if license_info:
            badges.append({
                'label': 'License',
                'message': license_info,
                'color': 'blue',
                'url': f"https://img.shields.io/badge/License-{license_info.replace(' ', '%20')}-blue"
            })
        
        # Language badges
        languages = self._detect_languages()
        if languages:
            # Primary language (most files)
            primary_lang = max(languages.items(), key=lambda x: x[1])[0]
            badges.append({
                'label': 'Language',
                'message': primary_lang,
                'color': 'green',
                'url': f"https://img.shields.io/badge/Language-{primary_lang.replace(' ', '%20')}-green"
            })
        
        # Code quality badges based on statistics
        code_stats = self._get_code_statistics()
        if code_stats and code_stats.get('total_lines', 0) > 0:
            total_lines = code_stats['total_lines']
            comment_lines = code_stats['comment_lines']
            
            # Documentation ratio
            if total_lines > 0:
                doc_ratio = (comment_lines / total_lines) * 100
                if doc_ratio >= 20:
                    doc_status = 'excellent'
                    doc_color = 'brightgreen'
                elif doc_ratio >= 10:
                    doc_status = 'good'
                    doc_color = 'green'
                elif doc_ratio >= 5:
                    doc_status = 'fair'
                    doc_color = 'yellow'
                else:
                    doc_status = 'low'
                    doc_color = 'orange'
                
                badges.append({
                    'label': 'Documentation',
                    'message': f"{doc_ratio:.1f}% - {doc_status}",
                    'color': doc_color,
                    'url': f"https://img.shields.io/badge/Documentation-{doc_ratio:.1f}%25%20{doc_status}-{doc_color}"
                })
            
            # Lines of code badge
            if total_lines >= 10000:
                size = 'large'
                size_color = 'blue'
            elif total_lines >= 1000:
                size = 'medium'
                size_color = 'blue'
            else:
                size = 'small'
                size_color = 'lightgrey'
            
            badges.append({
                'label': 'Size',
                'message': f"{total_lines:,} LOC - {size}",
                'color': size_color,
                'url': f"https://img.shields.io/badge/Size-{total_lines:,}%20LOC%20{size}-{size_color}".replace(',', '%2C')
            })
        
        # Repository status
        git_info = self._get_git_info()
        if git_info:
            badges.append({
                'label': 'Status',
                'message': 'Active',
                'color': 'brightgreen',
                'url': "https://img.shields.io/badge/Status-Active-brightgreen"
            })
        
        # Build tool badges
        build_tools = self._detect_build_tools()
        if 'GitHub Actions' in build_tools:
            badges.append({
                'label': 'CI/CD',
                'message': 'GitHub Actions',
                'color': 'blue',
                'url': "https://img.shields.io/badge/CI/CD-GitHub%20Actions-blue"
            })
        
        return badges
    
    def _parse_configuration_files(self) -> Dict[str, Any]:
        """Parse configuration files (JSON, YAML, TOML, .env, etc.)."""
        configs = {
            'json': [],
            'yaml': [],
            'toml': [],
            'env': [],
            'ini': [],
            'xml': []
        }
        
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                      'dist', 'build', '.idea', '.vscode', 'target', 'bin', 'obj'}
        
        config_patterns = {
            'json': ['.json'],
            'yaml': ['.yaml', '.yml'],
            'toml': ['.toml'],
            'env': ['.env', '.env.example', '.env.local', '.env.development', '.env.production'],
            'ini': ['.ini', '.cfg'],
            'xml': ['.xml']
        }
        
        for root, dirs, files in os.walk(self.scan_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for filename in files:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(self.scan_path)
                
                # Check each config type
                for config_type, patterns in config_patterns.items():
                    match = False
                    for pattern in patterns:
                        if filename.endswith(pattern) or filename == pattern:
                            match = True
                            break
                    
                    if match:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            config_info = {
                                'file': str(rel_path),
                                'type': config_type,
                                'size': len(content)
                            }
                            
                            # Try to parse JSON files
                            if config_type == 'json' and len(content) < 100000:  # Limit size
                                try:
                                    parsed = json.loads(content)
                                    config_info['keys'] = list(parsed.keys()) if isinstance(parsed, dict) else []
                                    config_info['parsed'] = True
                                except:
                                    config_info['parsed'] = False
                            
                            configs[config_type].append(config_info)
                        except Exception:
                            pass
        
        return configs
    
    def _extract_environment_variables(self) -> List[Dict[str, str]]:
        """Extract environment variables from .env files and code."""
        env_vars = []
        seen = set()
        
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                      'dist', 'build', '.idea', '.vscode', 'target', 'bin', 'obj'}
        
        # Pattern for environment variable usage
        env_patterns = [
            r'os\.environ\.get\(["\']([A-Z_][A-Z0-9_]*)["\']',  # Python
            r'os\.getenv\(["\']([A-Z_][A-Z0-9_]*)["\']',  # Python
            r'process\.env\.([A-Z_][A-Z0-9_]*)',  # JavaScript/Node
            r'ENV\[["\']([A-Z_][A-Z0-9_]*)["\']',  # Ruby/PHP
            r'\$\{([A-Z_][A-Z0-9_]*)\}',  # Shell/env files
        ]
        
        for root, dirs, files in os.walk(self.scan_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for filename in files:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(self.scan_path)
                
                # Check .env files
                if filename.startswith('.env'):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith('#') and '=' in line:
                                    var_name = line.split('=')[0].strip()
                                    if var_name and var_name not in seen:
                                        env_vars.append({
                                            'name': var_name,
                                            'source': str(rel_path),
                                            'type': 'definition'
                                        })
                                        seen.add(var_name)
                    except Exception:
                        pass
                
                # Check code files for usage
                ext = file_path.suffix.lower()
                if ext in {'.py', '.js', '.jsx', '.ts', '.tsx', '.rb', '.php', '.sh'}:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        for pattern in env_patterns:
                            matches = re.finditer(pattern, content)
                            for match in matches:
                                var_name = match.group(1)
                                if var_name and var_name not in seen:
                                    env_vars.append({
                                        'name': var_name,
                                        'source': str(rel_path),
                                        'type': 'usage'
                                    })
                                    seen.add(var_name)
                    except Exception:
                        pass
        
        return sorted(env_vars, key=lambda x: x['name'])
    
    def _detect_frameworks(self) -> List[Dict[str, str]]:
        """Detect frameworks and libraries used in the project."""
        frameworks = []
        seen = set()
        
        # Framework indicators
        framework_indicators = {
            # Python frameworks
            'Django': ['django', 'manage.py', 'settings.py', 'urls.py'],
            'Flask': ['flask', 'from flask import'],
            'FastAPI': ['fastapi', 'from fastapi import'],
            'Pyramid': ['pyramid', 'from pyramid'],
            'Tornado': ['tornado', 'from tornado'],
            
            # JavaScript frameworks
            'React': ['react', '"react":', 'from "react"', 'import React'],
            'Vue': ['vue', '"vue":', '@vue/', 'import Vue'],
            'Angular': ['angular', '@angular/', 'ng serve'],
            'Next.js': ['next', '"next":', 'next.config'],
            'Nuxt': ['nuxt', '"nuxt":', 'nuxt.config'],
            'Express': ['express', '"express":', 'from "express"'],
            'Nest': ['nestjs', '@nestjs/'],
            
            # Other frameworks
            'Spring Boot': ['spring-boot', 'org.springframework.boot'],
            'Laravel': ['laravel', 'artisan'],
            'Ruby on Rails': ['rails', 'bin/rails'],
            'ASP.NET': ['asp.net', 'Microsoft.AspNetCore'],
            'Gin': ['gin-gonic', '"github.com/gin-gonic/gin"'],
            'Echo': ['labstack/echo', '"github.com/labstack/echo"'],
        }
        
        # Check package files first (most reliable)
        dependencies = self._detect_dependencies()
        for framework, indicators in framework_indicators.items():
            if framework in seen:
                continue
            
            # Check in dependencies
            for dep_type, dep_list in dependencies.items():
                for dep_file in dep_list:
                    try:
                        file_path = self.scan_path / dep_file
                        if file_path.exists():
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                            
                            for indicator in indicators:
                                if indicator.lower() in content:
                                    if framework not in seen:
                                        frameworks.append({
                                            'name': framework,
                                            'evidence': f'Found in {dep_file}',
                                            'confidence': 'high'
                                        })
                                        seen.add(framework)
                                    break
                    except Exception:
                        pass
        
        # Only check source files if we haven't found many frameworks yet and skip scanner files
        if len(seen) < 5:
            ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                          'dist', 'build', '.idea', '.vscode', 'target', 'bin', 'obj', 'accudoc'}
            
            code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rb'}
            
            # Look for main application files
            main_files = ['main.py', 'app.py', 'index.js', 'index.ts', 'server.js', 'app.js']
            
            for root, dirs, files in os.walk(self.scan_path):
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                
                for filename in files:
                    # Prioritize main files
                    if filename not in main_files:
                        continue
                    
                    file_path = Path(root) / filename
                    ext = file_path.suffix.lower()
                    
                    if ext not in code_extensions:
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        # Only check import lines (first 30 lines)
                        import_section = '\n'.join(lines[:30])
                        
                        for framework, indicators in framework_indicators.items():
                            if framework in seen:
                                continue
                            
                            for indicator in indicators:
                                if indicator in import_section:
                                    frameworks.append({
                                        'name': framework,
                                        'evidence': f'Imported in {filename}',
                                        'confidence': 'high'
                                    })
                                    seen.add(framework)
                                    break
                    except Exception:
                        pass
        
        return frameworks
    
    def _extract_type_information(self) -> Dict[str, List[Dict]]:
        """Extract type hints and annotations from code."""
        type_info = {
            'python_typed_functions': [],
            'python_typed_classes': [],
            'typescript_interfaces': [],
            'typescript_types': []
        }
        
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                      'dist', 'build', '.idea', '.vscode', 'target', 'bin', 'obj'}
        
        # Python type hints pattern
        python_typed_func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*:\s*[^)]+\)\s*->\s*([^:]+):'
        
        for root, dirs, files in os.walk(self.scan_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for filename in files:
                file_path = Path(root) / filename
                ext = file_path.suffix.lower()
                rel_path = file_path.relative_to(self.scan_path)
                
                # Python files
                if ext == '.py':
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Find typed functions
                        matches = re.finditer(python_typed_func_pattern, content)
                        for match in matches:
                            func_name = match.group(1)
                            return_type = match.group(2).strip()
                            
                            if len(type_info['python_typed_functions']) < 20:  # Limit
                                type_info['python_typed_functions'].append({
                                    'name': func_name,
                                    'return_type': return_type,
                                    'file': str(rel_path)
                                })
                    except Exception:
                        pass
                
                # TypeScript files
                elif ext in {'.ts', '.tsx'}:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Find interfaces
                        interface_pattern = r'interface\s+([A-Z][a-zA-Z0-9]*)'
                        matches = re.finditer(interface_pattern, content)
                        for match in matches:
                            if len(type_info['typescript_interfaces']) < 20:
                                type_info['typescript_interfaces'].append({
                                    'name': match.group(1),
                                    'file': str(rel_path)
                                })
                        
                        # Find type aliases
                        type_pattern = r'type\s+([A-Z][a-zA-Z0-9]*)'
                        matches = re.finditer(type_pattern, content)
                        for match in matches:
                            if len(type_info['typescript_types']) < 20:
                                type_info['typescript_types'].append({
                                    'name': match.group(1),
                                    'file': str(rel_path)
                                })
                    except Exception:
                        pass
        
        return type_info
    
    def _analyze_imports(self) -> Dict[str, Any]:
        """Analyze import statements to map dependencies."""
        imports = {
            'python': {},
            'javascript': {},
            'java': {},
            'go': {}
        }
        
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                      'dist', 'build', '.idea', '.vscode', 'target', 'bin', 'obj'}
        
        for root, dirs, files in os.walk(self.scan_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for filename in files:
                file_path = Path(root) / filename
                ext = file_path.suffix.lower()
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Python imports
                    if ext == '.py':
                        # import X or from X import Y
                        python_imports = re.findall(r'^\s*(?:from\s+([a-zA-Z_][a-zA-Z0-9_.]*)|import\s+([a-zA-Z_][a-zA-Z0-9_.]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_.]*)*))', content, re.MULTILINE)
                        for imp in python_imports:
                            module = imp[0] if imp[0] else imp[1].split(',')[0].strip()
                            base_module = module.split('.')[0]
                            imports['python'][base_module] = imports['python'].get(base_module, 0) + 1
                    
                    # JavaScript/TypeScript imports
                    elif ext in {'.js', '.jsx', '.ts', '.tsx'}:
                        js_imports = re.findall(r'(?:import|require)\s*\(?["\']([^"\']+)["\']', content)
                        for imp in js_imports:
                            # Skip relative imports
                            if not imp.startswith('.'):
                                base_module = imp.split('/')[0]
                                imports['javascript'][base_module] = imports['javascript'].get(base_module, 0) + 1
                    
                    # Java imports
                    elif ext == '.java':
                        java_imports = re.findall(r'^\s*import\s+([a-zA-Z][a-zA-Z0-9_.]*);', content, re.MULTILINE)
                        for imp in java_imports:
                            parts = imp.split('.')
                            if len(parts) >= 2:
                                base_package = '.'.join(parts[:2])
                                imports['java'][base_package] = imports['java'].get(base_package, 0) + 1
                    
                    # Go imports
                    elif ext == '.go':
                        go_imports = re.findall(r'^\s*import\s+"([^"]+)"', content, re.MULTILINE)
                        for imp in go_imports:
                            base_package = imp.split('/')[0]
                            imports['go'][base_package] = imports['go'].get(base_package, 0) + 1
                
                except Exception:
                    pass
        
        # Sort by frequency and limit
        for lang in imports:
            if imports[lang]:
                sorted_imports = sorted(imports[lang].items(), key=lambda x: x[1], reverse=True)
                imports[lang] = dict(sorted_imports[:30])  # Top 30
        
        return imports
