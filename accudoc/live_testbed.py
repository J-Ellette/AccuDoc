"""
Live Documentation Testbed for AccuDoc.

Enables execution of code snippets in secure Docker containers for
interactive documentation with validated outputs and trust badges.
"""

import re
import json
import docker
import tempfile
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class ExecutionStatus(Enum):
    """Status of code execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"
    DENIED = "denied"


class Language(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    GO = "go"
    RUBY = "ruby"
    RUST = "rust"


# Language-specific Docker images and execution commands
LANGUAGE_CONFIG = {
    Language.PYTHON: {
        "image": "python:3.11-slim",
        "extension": ".py",
        "run_command": ["python", "/code/script.py"]
    },
    Language.JAVASCRIPT: {
        "image": "node:18-slim",
        "extension": ".js",
        "run_command": ["node", "/code/script.js"]
    },
    Language.JAVA: {
        "image": "openjdk:11-slim",
        "extension": ".java",
        "run_command": ["sh", "-c", "javac /code/Main.java && java -cp /code Main"]
    },
    Language.GO: {
        "image": "golang:1.20-alpine",
        "extension": ".go",
        "run_command": ["go", "run", "/code/script.go"]
    },
    Language.RUBY: {
        "image": "ruby:3.1-slim",
        "extension": ".rb",
        "run_command": ["ruby", "/code/script.rb"]
    },
    Language.RUST: {
        "image": "rust:1.70-slim",
        "extension": ".rs",
        "run_command": ["sh", "-c", "rustc /code/script.rs -o /code/script && /code/script"]
    }
}


@dataclass
class ExecutionResult:
    """Result of code execution."""
    status: ExecutionStatus
    output: str
    error: str
    execution_time: float
    timestamp: str
    badge: str
    language: Language
    code_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['language'] = self.language.value
        return data


@dataclass
class CodeSnippet:
    """Represents a code snippet from documentation."""
    code: str
    language: Language
    line_number: int
    title: Optional[str] = None
    

class LiveTestbed:
    """
    Manages execution of code snippets in secure Docker containers.
    
    Provides isolation, security, and validation for interactive documentation.
    """
    
    def __init__(
        self,
        timeout: int = 30,
        memory_limit: str = "256m",
        cpu_quota: int = 50000,  # 50% of one CPU
        network_disabled: bool = True,
        enable_cache: bool = True
    ):
        """
        Initialize live testbed.
        
        Args:
            timeout: Maximum execution time in seconds (default: 30)
            memory_limit: Memory limit for containers (default: "256m")
            cpu_quota: CPU quota in microseconds (default: 50000 = 50% of one CPU)
            network_disabled: Disable network access in containers (default: True)
            enable_cache: Cache execution results (default: True)
        """
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_quota = cpu_quota
        self.network_disabled = network_disabled
        self.enable_cache = enable_cache
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            # Test connection
            self.docker_client.ping()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Docker: {e}")
        
        # Execution cache
        self.cache: Dict[str, ExecutionResult] = {}
    
    def extract_code_snippets(self, markdown_content: str) -> List[CodeSnippet]:
        """
        Extract code snippets from markdown documentation.
        
        Args:
            markdown_content: Markdown content to parse
            
        Returns:
            List of extracted code snippets
        """
        snippets = []
        
        # Pattern to match fenced code blocks with language specification
        pattern = r'```(\w+)\s*\n(.*?)```'
        
        for match in re.finditer(pattern, markdown_content, re.DOTALL):
            lang_str = match.group(1).lower()
            code = match.group(2).strip()
            line_number = markdown_content[:match.start()].count('\n') + 1
            
            # Map language string to Language enum
            language = self._detect_language(lang_str)
            if language:
                snippets.append(CodeSnippet(
                    code=code,
                    language=language,
                    line_number=line_number
                ))
        
        return snippets
    
    def _detect_language(self, lang_str: str) -> Optional[Language]:
        """Detect language from string."""
        lang_map = {
            'python': Language.PYTHON,
            'py': Language.PYTHON,
            'javascript': Language.JAVASCRIPT,
            'js': Language.JAVASCRIPT,
            'node': Language.JAVASCRIPT,
            'java': Language.JAVA,
            'go': Language.GO,
            'golang': Language.GO,
            'ruby': Language.RUBY,
            'rb': Language.RUBY,
            'rust': Language.RUST,
            'rs': Language.RUST,
        }
        return lang_map.get(lang_str)
    
    def execute_code(
        self,
        code: str,
        language: Language,
        check_cache: bool = True
    ) -> ExecutionResult:
        """
        Execute code in a secure Docker container.
        
        Args:
            code: Code to execute
            language: Programming language
            check_cache: Check cache before execution (default: True)
            
        Returns:
            Execution result with status, output, and badge
        """
        # Generate code hash for caching
        code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
        
        # Check cache
        if check_cache and self.enable_cache and code_hash in self.cache:
            return self.cache[code_hash]
        
        start_time = time.time()
        
        try:
            # Get language configuration
            if language not in LANGUAGE_CONFIG:
                return self._create_error_result(
                    language,
                    code_hash,
                    f"Unsupported language: {language.value}",
                    time.time() - start_time
                )
            
            config = LANGUAGE_CONFIG[language]
            
            # Pull Docker image if not available
            self._ensure_image(config['image'])
            
            # Create temporary directory for code
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Write code to file
                if language == Language.JAVA:
                    # Java requires specific class name
                    code_file = temp_path / "Main.java"
                    # Ensure code has Main class
                    if 'class Main' not in code:
                        code = f"public class Main {{\n    public static void main(String[] args) {{\n{code}\n    }}\n}}"
                else:
                    code_file = temp_path / f"script{config['extension']}"
                
                code_file.write_text(code)
                
                # Run container
                result = self._run_container(
                    config['image'],
                    config['run_command'],
                    temp_path
                )
                
                execution_time = time.time() - start_time
                
                # Create execution result
                exec_result = ExecutionResult(
                    status=result['status'],
                    output=result['output'],
                    error=result['error'],
                    execution_time=execution_time,
                    timestamp=datetime.now().isoformat(),
                    badge=self._generate_badge(result['status']),
                    language=language,
                    code_hash=code_hash
                )
                
                # Cache result
                if self.enable_cache:
                    self.cache[code_hash] = exec_result
                
                return exec_result
                
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_error_result(
                language,
                code_hash,
                str(e),
                execution_time
            )
    
    def _ensure_image(self, image_name: str) -> None:
        """Ensure Docker image is available, pull if necessary."""
        try:
            self.docker_client.images.get(image_name)
        except docker.errors.ImageNotFound:
            # Pull image
            self.docker_client.images.pull(image_name)
    
    def _run_container(
        self,
        image: str,
        command: List[str],
        code_dir: Path
    ) -> Dict[str, Any]:
        """
        Run code in Docker container.
        
        Args:
            image: Docker image name
            command: Command to execute
            code_dir: Directory containing code
            
        Returns:
            Dictionary with status, output, and error
        """
        try:
            # Container configuration
            container_config = {
                'image': image,
                'command': command,
                'volumes': {
                    str(code_dir): {'bind': '/code', 'mode': 'ro'}
                },
                'mem_limit': self.memory_limit,
                'cpu_quota': self.cpu_quota,
                'network_disabled': self.network_disabled,
                'detach': True,
                'remove': True,
                'working_dir': '/code'
            }
            
            # Run container
            container = self.docker_client.containers.run(**container_config)
            
            # Wait for completion with timeout
            try:
                result = container.wait(timeout=self.timeout)
                exit_code = result.get('StatusCode', -1)
                
                # Get logs
                logs = container.logs().decode('utf-8', errors='replace')
                
                if exit_code == 0:
                    return {
                        'status': ExecutionStatus.SUCCESS,
                        'output': logs,
                        'error': ''
                    }
                else:
                    return {
                        'status': ExecutionStatus.FAILURE,
                        'output': '',
                        'error': logs
                    }
                    
            except Exception as e:
                # Timeout or other error
                try:
                    container.stop(timeout=1)
                except:
                    pass
                
                return {
                    'status': ExecutionStatus.TIMEOUT,
                    'output': '',
                    'error': f'Execution timeout ({self.timeout}s)'
                }
                
        except Exception as e:
            return {
                'status': ExecutionStatus.ERROR,
                'output': '',
                'error': str(e)
            }
    
    def _create_error_result(
        self,
        language: Language,
        code_hash: str,
        error_message: str,
        execution_time: float
    ) -> ExecutionResult:
        """Create an error execution result."""
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output='',
            error=error_message,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
            badge=self._generate_badge(ExecutionStatus.ERROR),
            language=language,
            code_hash=code_hash
        )
    
    def _generate_badge(self, status: ExecutionStatus) -> str:
        """
        Generate SVG badge for execution status.
        
        Args:
            status: Execution status
            
        Returns:
            SVG badge as string
        """
        badge_config = {
            ExecutionStatus.SUCCESS: {
                'label': 'validated',
                'color': '#44cc11',
                'text': '✓ Validated'
            },
            ExecutionStatus.FAILURE: {
                'label': 'failed',
                'color': '#e05d44',
                'text': '✗ Failed'
            },
            ExecutionStatus.TIMEOUT: {
                'label': 'timeout',
                'color': '#fe7d37',
                'text': '⏱ Timeout'
            },
            ExecutionStatus.ERROR: {
                'label': 'error',
                'color': '#9f9f9f',
                'text': '⚠ Error'
            },
            ExecutionStatus.DENIED: {
                'label': 'denied',
                'color': '#9f9f9f',
                'text': '🔒 Denied'
            }
        }
        
        config = badge_config.get(status, badge_config[ExecutionStatus.ERROR])
        
        # Simple text badge (could be replaced with actual SVG if needed)
        return f"[{config['text']}]"
    
    def validate_documentation(
        self,
        markdown_content: str,
        auto_execute: bool = False
    ) -> Dict[str, Any]:
        """
        Validate all code snippets in documentation.
        
        Args:
            markdown_content: Markdown documentation content
            auto_execute: Automatically execute all snippets (default: False)
            
        Returns:
            Validation report with results for each snippet
        """
        snippets = self.extract_code_snippets(markdown_content)
        
        results = {
            'total_snippets': len(snippets),
            'executed': 0,
            'success': 0,
            'failure': 0,
            'timeout': 0,
            'error': 0,
            'snippets': []
        }
        
        if auto_execute:
            for snippet in snippets:
                result = self.execute_code(snippet.code, snippet.language)
                
                results['executed'] += 1
                if result.status == ExecutionStatus.SUCCESS:
                    results['success'] += 1
                elif result.status == ExecutionStatus.FAILURE:
                    results['failure'] += 1
                elif result.status == ExecutionStatus.TIMEOUT:
                    results['timeout'] += 1
                else:
                    results['error'] += 1
                
                results['snippets'].append({
                    'line': snippet.line_number,
                    'language': snippet.language.value,
                    'status': result.status.value,
                    'badge': result.badge
                })
        else:
            # Just list snippets without executing
            for snippet in snippets:
                results['snippets'].append({
                    'line': snippet.line_number,
                    'language': snippet.language.value,
                    'code_preview': snippet.code[:100] + '...' if len(snippet.code) > 100 else snippet.code,
                    'status': 'not_executed'
                })
        
        return results
    
    def clear_cache(self) -> None:
        """Clear execution cache."""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cached_executions': len(self.cache),
            'languages': list(set(r.language.value for r in self.cache.values())),
            'success_rate': sum(1 for r in self.cache.values() if r.status == ExecutionStatus.SUCCESS) / len(self.cache) * 100 if self.cache else 0
        }
    
    def close(self) -> None:
        """Close Docker client connection."""
        if hasattr(self, 'docker_client'):
            self.docker_client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
