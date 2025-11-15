"""
Interactive tutorial system for AccuDoc.

Provides step-by-step tutorials for new users to learn AccuDoc features.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum


class TutorialStatus(Enum):
    """Tutorial completion status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class TutorialStep:
    """A single step in a tutorial."""
    
    id: str
    title: str
    description: str
    instructions: List[str]
    example: Optional[str] = None
    tip: Optional[str] = None
    completed: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TutorialStep':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Tutorial:
    """A complete tutorial."""
    
    id: str
    title: str
    description: str
    difficulty: str  # beginner, intermediate, advanced
    duration: str  # estimated time
    steps: List[TutorialStep] = field(default_factory=list)
    status: str = TutorialStatus.NOT_STARTED.value
    current_step: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['steps'] = [s.to_dict() for s in self.steps]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Tutorial':
        """Create from dictionary."""
        steps_data = data.pop('steps', [])
        tutorial = cls(**data)
        tutorial.steps = [TutorialStep.from_dict(s) for s in steps_data]
        return tutorial
    
    def get_progress(self) -> float:
        """Get completion progress (0-100)."""
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.completed)
        return (completed / len(self.steps)) * 100


class TutorialSystem:
    """
    Interactive tutorial system for AccuDoc.
    
    Manages tutorials, tracks progress, and provides guided learning.
    """
    
    # Built-in tutorials
    BUILTIN_TUTORIALS = {
        'getting_started': Tutorial(
            id='getting_started',
            title='Getting Started with AccuDoc',
            description='Learn the basics of AccuDoc and generate your first documentation',
            difficulty='beginner',
            duration='10 minutes',
            steps=[
                TutorialStep(
                    id='step1',
                    title='What is AccuDoc?',
                    description='Introduction to AccuDoc',
                    instructions=[
                        'AccuDoc is an automated documentation generator',
                        'It scans your code repository and generates comprehensive docs',
                        'No manual writing needed - AccuDoc does the heavy lifting!'
                    ],
                    tip='AccuDoc works with both local and remote repositories'
                ),
                TutorialStep(
                    id='step2',
                    title='Scanning a Repository',
                    description='Learn how to scan your first repository',
                    instructions=[
                        '1. Open AccuDoc GUI or use the CLI',
                        '2. Enter your repository path or URL',
                        '3. Click "Scan Repository" or run: accudoc scan /path/to/repo',
                        '4. Wait for the scan to complete'
                    ],
                    example='python accudoc_cli.py scan /path/to/my-project -o scan.json',
                    tip='For faster scans on large repos, caching is enabled by default'
                ),
                TutorialStep(
                    id='step3',
                    title='Generating Documentation',
                    description='Generate documentation from scan results',
                    instructions=[
                        '1. After scanning, review the detected information',
                        '2. Choose your output format (Markdown, HTML, PDF)',
                        '3. Select a template (default, minimal, detailed, etc.)',
                        '4. Generate the documentation'
                    ],
                    example='python accudoc_cli.py generate scan.json -o README.md',
                    tip='You can generate multiple formats from the same scan'
                ),
                TutorialStep(
                    id='step4',
                    title='Saving Your Documentation',
                    description='Export documentation to files',
                    instructions=[
                        '1. Click "Save Documentation" in the GUI',
                        '2. Choose your output location',
                        '3. Select file format',
                        '4. Optionally choose a theme for HTML output'
                    ],
                    example='python accudoc_cli.py export /path/to/repo -o docs.html --format html --theme dark',
                    tip='Use the "export" command to scan and generate in one step'
                )
            ]
        ),
        'advanced_features': Tutorial(
            id='advanced_features',
            title='Advanced AccuDoc Features',
            description='Explore advanced features like caching, plugins, and automation',
            difficulty='intermediate',
            duration='20 minutes',
            steps=[
                TutorialStep(
                    id='step1',
                    title='Using Templates',
                    description='Choose the right template for your documentation',
                    instructions=[
                        '1. Browse available templates using the template gallery',
                        '2. Preview template descriptions and use cases',
                        '3. Select the template that fits your project',
                        '4. Generate documentation with your chosen template'
                    ],
                    example='python accudoc_cli.py export /path/to/repo -o docs.md --template api',
                    tip='Use "minimal" for quick READMEs, "api" for libraries, "detailed" for complex projects'
                ),
                TutorialStep(
                    id='step2',
                    title='Working with Cache',
                    description='Speed up scans with intelligent caching',
                    instructions=[
                        '1. First scan creates a cache automatically',
                        '2. Subsequent scans only re-analyze changed files',
                        '3. View cache stats: accudoc cache stats /path/to/repo',
                        '4. Clear cache if needed: accudoc cache clear /path/to/repo'
                    ],
                    example='python accudoc_cli.py cache stats /path/to/repo',
                    tip='Caching can improve scan speed by 50-90% on large repositories'
                ),
                TutorialStep(
                    id='step3',
                    title='Using the REST API',
                    description='Access AccuDoc features programmatically',
                    instructions=[
                        '1. Start the API server: accudoc api',
                        '2. Access API at http://localhost:5000',
                        '3. View API docs at http://localhost:5000/api/docs',
                        '4. Make API calls using curl or Python requests'
                    ],
                    example='curl -X POST http://localhost:5000/api/scan -H "Content-Type: application/json" -d \'{"path": "/path/to/repo"}\'',
                    tip='The API is perfect for integrating AccuDoc into your CI/CD pipeline'
                ),
                TutorialStep(
                    id='step4',
                    title='Setting Up Scheduled Scans',
                    description='Automate documentation generation with schedules',
                    instructions=[
                        '1. Use the scheduler to scan repositories automatically',
                        '2. Set up daily, weekly, or custom intervals',
                        '3. Configure email notifications for completed scans',
                        '4. Monitor scheduled scans and their status'
                    ],
                    tip='Scheduled scans ensure your documentation stays up-to-date'
                )
            ]
        ),
        'cli_mastery': Tutorial(
            id='cli_mastery',
            title='Mastering the AccuDoc CLI',
            description='Become proficient with AccuDoc command-line interface',
            difficulty='intermediate',
            duration='15 minutes',
            steps=[
                TutorialStep(
                    id='step1',
                    title='Essential CLI Commands',
                    description='Learn the core CLI commands',
                    instructions=[
                        '1. scan - Scan a repository',
                        '2. generate - Generate docs from scan',
                        '3. export - Scan and generate in one step',
                        '4. info - Get AccuDoc information',
                        '5. help - View command help'
                    ],
                    example='python accudoc_cli.py --help',
                    tip='Use "export" for quick one-step documentation generation'
                ),
                TutorialStep(
                    id='step2',
                    title='Batch Processing',
                    description='Process multiple repositories at once',
                    instructions=[
                        '1. Create a batch configuration JSON file',
                        '2. List all repositories to process',
                        '3. Run: accudoc batch batch-config.json',
                        '4. Review results for each repository'
                    ],
                    example='python accudoc_cli.py batch my-repos.json',
                    tip='Batch processing is great for maintaining docs across multiple projects'
                ),
                TutorialStep(
                    id='step3',
                    title='Data Export and Analysis',
                    description='Export repository data for analysis',
                    instructions=[
                        '1. Export to CSV: accudoc data-export /repo -o exports -f csv',
                        '2. Export to JSON: accudoc data-export /repo -o data.json -f json',
                        '3. Generate summary: accudoc data-export /repo -o summary.csv -f summary',
                        '4. Analyze exported data in Excel or other tools'
                    ],
                    example='python accudoc_cli.py data-export /path/to/repo -o ./exports -f csv -r all',
                    tip='CSV exports are perfect for importing into spreadsheets'
                ),
                TutorialStep(
                    id='step4',
                    title='Health Metrics and Trends',
                    description='Monitor repository health and growth',
                    instructions=[
                        '1. Get health dashboard: accudoc health /repo',
                        '2. Analyze trends: accudoc trends /repo -p month',
                        '3. Compare repositories: accudoc compare /repo1 /repo2',
                        '4. Export metrics to JSON for tracking'
                    ],
                    example='python accudoc_cli.py health /path/to/repo -o dashboard.json -f json',
                    tip='Track trends over time to see how your project evolves'
                )
            ]
        )
    }
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize tutorial system.
        
        Args:
            config_dir: Directory for storing progress
        """
        self.config_dir = Path(config_dir or Path.home() / ".accudoc")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.progress_file = self.config_dir / "tutorial_progress.json"
        self.tutorials: Dict[str, Tutorial] = self.BUILTIN_TUTORIALS.copy()
        
        self._load_progress()
    
    def _load_progress(self):
        """Load tutorial progress from file."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for tutorial_id, progress in data.get('tutorials', {}).items():
                    if tutorial_id in self.tutorials:
                        tutorial = Tutorial.from_dict(progress)
                        self.tutorials[tutorial_id] = tutorial
    
    def _save_progress(self):
        """Save tutorial progress to file."""
        from datetime import datetime
        data = {
            'tutorials': {k: v.to_dict() for k, v in self.tutorials.items()},
            'updated': datetime.now().isoformat()
        }
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def list_tutorials(self, difficulty: Optional[str] = None) -> List[Tutorial]:
        """
        List available tutorials.
        
        Args:
            difficulty: Filter by difficulty level
            
        Returns:
            List of tutorials
        """
        tutorials = list(self.tutorials.values())
        if difficulty:
            tutorials = [t for t in tutorials if t.difficulty == difficulty]
        return tutorials
    
    def get_tutorial(self, tutorial_id: str) -> Optional[Tutorial]:
        """
        Get a specific tutorial.
        
        Args:
            tutorial_id: Tutorial identifier
            
        Returns:
            Tutorial or None
        """
        return self.tutorials.get(tutorial_id)
    
    def start_tutorial(self, tutorial_id: str) -> bool:
        """
        Start a tutorial.
        
        Args:
            tutorial_id: Tutorial identifier
            
        Returns:
            True if started
        """
        tutorial = self.get_tutorial(tutorial_id)
        if not tutorial:
            return False
        
        tutorial.status = TutorialStatus.IN_PROGRESS.value
        tutorial.current_step = 0
        self._save_progress()
        return True
    
    def complete_step(self, tutorial_id: str, step_index: int) -> bool:
        """
        Mark a tutorial step as completed.
        
        Args:
            tutorial_id: Tutorial identifier
            step_index: Step index
            
        Returns:
            True if marked complete
        """
        tutorial = self.get_tutorial(tutorial_id)
        if not tutorial or step_index >= len(tutorial.steps):
            return False
        
        tutorial.steps[step_index].completed = True
        tutorial.current_step = min(step_index + 1, len(tutorial.steps) - 1)
        
        # Check if tutorial is completed
        if all(s.completed for s in tutorial.steps):
            tutorial.status = TutorialStatus.COMPLETED.value
        
        self._save_progress()
        return True
    
    def reset_tutorial(self, tutorial_id: str) -> bool:
        """
        Reset tutorial progress.
        
        Args:
            tutorial_id: Tutorial identifier
            
        Returns:
            True if reset
        """
        tutorial = self.get_tutorial(tutorial_id)
        if not tutorial:
            return False
        
        tutorial.status = TutorialStatus.NOT_STARTED.value
        tutorial.current_step = 0
        for step in tutorial.steps:
            step.completed = False
        
        self._save_progress()
        return True
    
    def get_current_step(self, tutorial_id: str) -> Optional[TutorialStep]:
        """
        Get current step of a tutorial.
        
        Args:
            tutorial_id: Tutorial identifier
            
        Returns:
            Current TutorialStep or None
        """
        tutorial = self.get_tutorial(tutorial_id)
        if not tutorial or not tutorial.steps:
            return None
        
        return tutorial.steps[tutorial.current_step]
    
    def format_tutorial_list(self) -> str:
        """
        Format list of tutorials.
        
        Returns:
            Formatted string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("AccuDoc Interactive Tutorials")
        lines.append("=" * 70)
        lines.append("")
        
        for tutorial in self.tutorials.values():
            status_icon = {
                TutorialStatus.NOT_STARTED.value: "⚪",
                TutorialStatus.IN_PROGRESS.value: "🔵",
                TutorialStatus.COMPLETED.value: "✅"
            }.get(tutorial.status, "⚪")
            
            progress = tutorial.get_progress()
            
            lines.append(f"{status_icon} {tutorial.title}")
            lines.append(f"   {tutorial.description}")
            lines.append(f"   Difficulty: {tutorial.difficulty.title()} | Duration: {tutorial.duration}")
            lines.append(f"   Progress: {progress:.0f}% ({sum(1 for s in tutorial.steps if s.completed)}/{len(tutorial.steps)} steps)")
            lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def format_tutorial_step(self, tutorial_id: str, step_index: Optional[int] = None) -> str:
        """
        Format a tutorial step.
        
        Args:
            tutorial_id: Tutorial identifier
            step_index: Optional step index (defaults to current)
            
        Returns:
            Formatted string
        """
        tutorial = self.get_tutorial(tutorial_id)
        if not tutorial:
            return f"Tutorial '{tutorial_id}' not found."
        
        if step_index is None:
            step_index = tutorial.current_step
        
        if step_index >= len(tutorial.steps):
            return "Invalid step index."
        
        step = tutorial.steps[step_index]
        
        lines = []
        lines.append("=" * 70)
        lines.append(f"{tutorial.title} - Step {step_index + 1}/{len(tutorial.steps)}")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"📚 {step.title}")
        lines.append(f"{step.description}")
        lines.append("")
        lines.append("Instructions:")
        for instruction in step.instructions:
            lines.append(f"  {instruction}")
        lines.append("")
        
        if step.example:
            lines.append("Example:")
            lines.append(f"  {step.example}")
            lines.append("")
        
        if step.tip:
            lines.append(f"💡 Tip: {step.tip}")
            lines.append("")
        
        status = "✅ Completed" if step.completed else "⚪ Not completed"
        lines.append(f"Status: {status}")
        lines.append("=" * 70)
        
        return "\n".join(lines)


def get_tutorial_system() -> TutorialSystem:
    """
    Get the tutorial system instance.
    
    Returns:
        TutorialSystem instance
    """
    return TutorialSystem()
