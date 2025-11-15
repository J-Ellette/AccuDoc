"""
Tutorial generation module for AccuDoc.

Creates step-by-step tutorials from code:
- Extract code examples
- Generate explanations
- Create learning paths
- Progressive complexity
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class TutorialGenerator:
    """Generate step-by-step tutorials from code."""
    
    def __init__(self, repo_path: str):
        """
        Initialize tutorial generator.
        
        Args:
            repo_path: Path to repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.tutorial')
    
    def extract_code_examples(self, file_path: Path, 
                             max_examples: int = 10) -> List[Dict[str, Any]]:
        """
        Extract code examples from a file.
        
        Args:
            file_path: Path to source file
            max_examples: Maximum number of examples to extract
            
        Returns:
            List of code examples with metadata
        """
        examples = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Look for functions/classes
            current_example = []
            in_example = False
            example_type = None
            example_name = None
            
            for i, line in enumerate(lines):
                # Detect function definitions (Python, JavaScript, Java, etc.)
                if re.match(r'^\s*(def|function|public|private|protected)\s+(\w+)', line):
                    if current_example and in_example:
                        examples.append({
                            'type': example_type,
                            'name': example_name,
                            'code': '\n'.join(current_example),
                            'line_start': i - len(current_example) + 1,
                            'line_end': i
                        })
                        if len(examples) >= max_examples:
                            break
                    
                    # Start new example
                    match = re.match(r'^\s*(def|function|public|private|protected)\s+(\w+)', line)
                    if match:
                        example_type = 'function'
                        example_name = match.group(2)
                        current_example = [line]
                        in_example = True
                elif in_example:
                    current_example.append(line)
                    
                    # End of function (heuristic: empty line or dedent)
                    if line.strip() == '' and len(current_example) > 3:
                        examples.append({
                            'type': example_type,
                            'name': example_name,
                            'code': '\n'.join(current_example),
                            'line_start': i - len(current_example) + 1,
                            'line_end': i
                        })
                        if len(examples) >= max_examples:
                            break
                        current_example = []
                        in_example = False
            
            # Add last example if any
            if current_example and in_example:
                examples.append({
                    'type': example_type,
                    'name': example_name,
                    'code': '\n'.join(current_example),
                    'line_start': len(lines) - len(current_example),
                    'line_end': len(lines)
                })
        
        except Exception as e:
            self.logger.error(f"Error extracting examples from {file_path}: {e}")
        
        return examples[:max_examples]
    
    def categorize_by_complexity(self, examples: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize examples by complexity level.
        
        Args:
            examples: List of code examples
            
        Returns:
            Examples grouped by complexity (beginner, intermediate, advanced)
        """
        categorized = {
            'beginner': [],
            'intermediate': [],
            'advanced': []
        }
        
        for example in examples:
            code = example.get('code', '')
            lines = len(code.split('\n'))
            
            # Simple heuristic based on length and complexity indicators
            complexity_score = lines
            
            # Add points for complexity indicators
            if 'class' in code.lower():
                complexity_score += 10
            if 'async' in code or 'await' in code:
                complexity_score += 5
            if 'try' in code and 'except' in code:
                complexity_score += 3
            if re.search(r'lambda|comprehension|\[.*for.*in.*\]', code):
                complexity_score += 5
            
            # Categorize
            if complexity_score < 15:
                categorized['beginner'].append(example)
            elif complexity_score < 30:
                categorized['intermediate'].append(example)
            else:
                categorized['advanced'].append(example)
        
        return categorized
    
    def generate_tutorial_step(self, example: Dict[str, Any], step_number: int) -> str:
        """
        Generate a tutorial step from a code example.
        
        Args:
            example: Code example
            step_number: Step number in tutorial
            
        Returns:
            Tutorial step in markdown
        """
        md = []
        
        name = example.get('name', 'Example')
        code = example.get('code', '')
        example_type = example.get('type', 'code')
        
        md.append(f"### Step {step_number}: {name}\n")
        
        # Add description based on type
        if example_type == 'function':
            md.append(f"In this step, we'll implement the `{name}` function. ")
            md.append("This function demonstrates important concepts:\n")
            
            # Identify patterns in code
            if 'return' in code:
                md.append("- Returns a value for use by other parts of the program")
            if 'if' in code or 'else' in code:
                md.append("- Uses conditional logic to handle different cases")
            if 'for' in code or 'while' in code:
                md.append("- Iterates over data structures")
            md.append("")
        
        md.append("**Code:**\n")
        md.append("```python")
        md.append(code.strip())
        md.append("```\n")
        
        md.append("**Explanation:**\n")
        lines = code.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            md.append(f"1. The code starts by defining `{name}`")
            if 'def' in first_line:
                # Extract parameters
                params_match = re.search(r'\((.*?)\)', first_line)
                if params_match and params_match.group(1).strip():
                    md.append(f"2. It accepts parameters: {params_match.group(1)}")
            if 'return' in code:
                md.append("3. Finally, it returns the computed result")
        
        md.append("\n**Try it yourself:**")
        md.append(f"- Modify the `{name}` function to add new functionality")
        md.append("- Test it with different inputs")
        md.append("- Add error handling if needed\n")
        
        return '\n'.join(md)
    
    def generate_tutorial(self, title: str, examples: List[Dict[str, Any]],
                         difficulty: str = 'beginner') -> str:
        """
        Generate a complete tutorial.
        
        Args:
            title: Tutorial title
            examples: Code examples to include
            difficulty: Difficulty level
            
        Returns:
            Complete tutorial in markdown
        """
        md = []
        
        md.append(f"# {title}\n")
        md.append(f"**Difficulty Level:** {difficulty.capitalize()}\n")
        
        md.append("## Introduction\n")
        md.append(f"This tutorial will guide you through implementing {title}. ")
        md.append("By the end, you'll understand the key concepts and be able to apply them in your own projects.\n")
        
        md.append("## Prerequisites\n")
        md.append("Before starting this tutorial, you should have:")
        md.append("- Basic programming knowledge")
        md.append("- Familiarity with the programming language used")
        md.append("- A development environment set up\n")
        
        md.append("## Learning Objectives\n")
        md.append("After completing this tutorial, you will be able to:")
        md.append(f"- Understand the architecture of {title}")
        md.append("- Implement core functionality")
        md.append("- Apply best practices")
        md.append("- Test and validate your implementation\n")
        
        md.append("## Tutorial Steps\n")
        
        # Generate steps from examples
        for i, example in enumerate(examples, 1):
            md.append(self.generate_tutorial_step(example, i))
            md.append("")
        
        md.append("## Summary\n")
        md.append(f"Congratulations! You've completed the {title} tutorial. ")
        md.append(f"You've learned {len(examples)} key concepts and implemented functional code. ")
        md.append("Continue practicing to reinforce these skills.\n")
        
        md.append("## Next Steps\n")
        md.append("- Explore the complete source code")
        md.append("- Experiment with modifications")
        md.append("- Build a project using these concepts")
        md.append("- Share your work with the community\n")
        
        return '\n'.join(md)
    
    def generate_learning_path(self, project_name: str,
                              all_examples: Dict[str, List[Dict]]) -> str:
        """
        Generate a learning path with progressive difficulty.
        
        Args:
            project_name: Name of the project
            all_examples: Examples categorized by difficulty
            
        Returns:
            Learning path document
        """
        md = []
        
        md.append(f"# {project_name} Learning Path\n")
        md.append("Follow this structured learning path to master the project:\n")
        
        # Beginner level
        if all_examples.get('beginner'):
            md.append("## Level 1: Beginner\n")
            md.append("Start here if you're new to the project:\n")
            for i, ex in enumerate(all_examples['beginner'][:5], 1):
                name = ex.get('name', f'Example {i}')
                md.append(f"{i}. **{name}** - Introduction to basic concepts")
            md.append("")
        
        # Intermediate level
        if all_examples.get('intermediate'):
            md.append("## Level 2: Intermediate\n")
            md.append("Once comfortable with basics, proceed to:\n")
            for i, ex in enumerate(all_examples['intermediate'][:5], 1):
                name = ex.get('name', f'Example {i}')
                md.append(f"{i}. **{name}** - Building on fundamentals")
            md.append("")
        
        # Advanced level
        if all_examples.get('advanced'):
            md.append("## Level 3: Advanced\n")
            md.append("Master advanced topics:\n")
            for i, ex in enumerate(all_examples['advanced'][:5], 1):
                name = ex.get('name', f'Example {i}')
                md.append(f"{i}. **{name}** - Advanced techniques")
            md.append("")
        
        md.append("## Recommended Timeline\n")
        md.append("- **Week 1-2**: Complete Level 1")
        md.append("- **Week 3-4**: Progress through Level 2")
        md.append("- **Week 5+**: Tackle Level 3 and build projects\n")
        
        return '\n'.join(md)
    
    def create_quick_start_guide(self, project_info: Dict[str, Any]) -> str:
        """
        Create a quick start guide.
        
        Args:
            project_info: Project information
            
        Returns:
            Quick start guide in markdown
        """
        md = []
        
        name = project_info.get('name', 'Project')
        md.append(f"# Quick Start Guide: {name}\n")
        
        md.append("## Installation\n")
        md.append("```bash")
        md.append("# Clone the repository")
        md.append(f"git clone {project_info.get('repo_url', 'https://github.com/user/repo')}")
        md.append(f"cd {name.lower().replace(' ', '-')}")
        md.append("")
        md.append("# Install dependencies")
        languages = project_info.get('languages', [])
        if 'Python' in str(languages):
            md.append("pip install -r requirements.txt")
        elif 'JavaScript' in str(languages):
            md.append("npm install")
        else:
            md.append("# Follow project-specific installation instructions")
        md.append("```\n")
        
        md.append("## Basic Usage\n")
        md.append("```python")
        md.append("# Import the main module")
        md.append(f"import {name.lower().replace(' ', '_')}")
        md.append("")
        md.append("# Create an instance")
        md.append(f"app = {name.replace(' ', '')}()")
        md.append("")
        md.append("# Use the functionality")
        md.append("result = app.run()")
        md.append("print(result)")
        md.append("```\n")
        
        md.append("## Next Steps\n")
        md.append("- Read the [Full Documentation](#)")
        md.append("- Follow the [Tutorial](#)")
        md.append("- Explore [Examples](#)")
        md.append("- Join the [Community](#)\n")
        
        return '\n'.join(md)
