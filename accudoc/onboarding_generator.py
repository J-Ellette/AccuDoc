"""
Onboarding and Training Path Generator for AccuDoc.

Translates repository documentation and code structure into customized 
onboarding guides and interactive checklists for new contributors.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import re

from accudoc.membership import MembershipManager, Permission


@dataclass
class OnboardingStep:
    """Represents a step in the onboarding process."""
    step_id: str
    title: str
    description: str
    order: int
    category: str  # setup, code, documentation, testing, deployment
    required: bool = True
    estimated_time: Optional[int] = None  # in minutes
    resources: Optional[List[str]] = None
    commands: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None


@dataclass
class OnboardingChecklist:
    """Represents a complete onboarding checklist."""
    checklist_id: str
    title: str
    description: str
    repository_path: str
    created_at: str
    created_by: Optional[str] = None
    organization_id: Optional[str] = None
    steps: Optional[List[OnboardingStep]] = None
    total_time: Optional[int] = None


@dataclass
class OnboardingProgress:
    """Tracks user progress through onboarding."""
    progress_id: str
    user_id: str
    checklist_id: str
    started_at: str
    completed_steps: List[str]
    completed_at: Optional[str] = None
    progress_percentage: float = 0.0


class OnboardingGenerator:
    """Generates onboarding guides and tracks progress."""
    
    def __init__(self, db_path: Optional[Path] = None, 
                 membership_manager: Optional[MembershipManager] = None):
        """
        Initialize onboarding generator.
        
        Args:
            db_path: Path to database file
            membership_manager: Optional membership manager for access control
        """
        if db_path is None:
            db_path = Path.home() / '.accudoc' / 'onboarding.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.membership_manager = membership_manager
        
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database schema."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Onboarding checklists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS onboarding_checklists (
                checklist_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                repository_path TEXT NOT NULL,
                organization_id TEXT,
                created_at TEXT NOT NULL,
                created_by TEXT,
                steps_data TEXT,
                total_time INTEGER
            )
        ''')
        
        # User progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS onboarding_progress (
                progress_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                checklist_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                completed_steps TEXT,
                progress_percentage REAL DEFAULT 0.0,
                FOREIGN KEY (checklist_id) REFERENCES onboarding_checklists(checklist_id)
            )
        ''')
        
        # Create indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_checklist_org ON onboarding_checklists(organization_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_progress_user ON onboarding_progress(user_id)')
        
        self.conn.commit()
    
    def analyze_repository(self, repo_info: Dict[str, Any]) -> List[OnboardingStep]:
        """
        Analyze repository and generate onboarding steps.
        
        Args:
            repo_info: Repository information from scanner
            
        Returns:
            List of onboarding steps
        """
        steps = []
        step_order = 0
        
        # Step 1: Repository setup
        steps.append(OnboardingStep(
            step_id=f"step_{step_order}",
            title="Clone Repository",
            description=f"Clone the repository to your local machine",
            order=step_order,
            category="setup",
            required=True,
            estimated_time=5,
            commands=[
                f"git clone {repo_info.get('url', '<repository-url>')}",
                f"cd {repo_info.get('name', '<repository-name>')}"
            ]
        ))
        step_order += 1
        
        # Step 2: Install dependencies based on detected package managers
        dependencies = repo_info.get('dependencies', {})
        languages = repo_info.get('languages', {})
        
        if 'package.json' in dependencies:
            steps.append(OnboardingStep(
                step_id=f"step_{step_order}",
                title="Install Node.js Dependencies",
                description="Install project dependencies using npm or yarn",
                order=step_order,
                category="setup",
                required=True,
                estimated_time=10,
                commands=["npm install"],
                resources=["package.json"]
            ))
            step_order += 1
        
        if 'requirements.txt' in dependencies or 'Python' in languages:
            steps.append(OnboardingStep(
                step_id=f"step_{step_order}",
                title="Install Python Dependencies",
                description="Set up Python virtual environment and install dependencies",
                order=step_order,
                category="setup",
                required=True,
                estimated_time=10,
                commands=[
                    "python -m venv venv",
                    "source venv/bin/activate  # On Windows: venv\\Scripts\\activate",
                    "pip install -r requirements.txt"
                ],
                resources=["requirements.txt"]
            ))
            step_order += 1
        
        if 'pom.xml' in dependencies or 'build.gradle' in dependencies:
            steps.append(OnboardingStep(
                step_id=f"step_{step_order}",
                title="Build Java Project",
                description="Build the project using Maven or Gradle",
                order=step_order,
                category="setup",
                required=True,
                estimated_time=15,
                commands=["mvn clean install"] if 'pom.xml' in dependencies else ["gradle build"],
                resources=["pom.xml"] if 'pom.xml' in dependencies else ["build.gradle"]
            ))
            step_order += 1
        
        # Step 3: Read documentation
        doc_files = repo_info.get('documentation', {})
        if doc_files:
            steps.append(OnboardingStep(
                step_id=f"step_{step_order}",
                title="Read Project Documentation",
                description="Familiarize yourself with the project documentation",
                order=step_order,
                category="documentation",
                required=True,
                estimated_time=30,
                resources=list(doc_files.keys())[:5]
            ))
            step_order += 1
        
        # Step 4: Understand project structure
        steps.append(OnboardingStep(
            step_id=f"step_{step_order}",
            title="Explore Project Structure",
            description="Navigate through the codebase to understand the organization",
            order=step_order,
            category="code",
            required=True,
            estimated_time=20,
            resources=["Project directory structure"]
        ))
        step_order += 1
        
        # Step 5: Run tests if test framework detected
        if self._has_tests(repo_info):
            test_commands = self._get_test_commands(repo_info)
            steps.append(OnboardingStep(
                step_id=f"step_{step_order}",
                title="Run Tests",
                description="Execute the test suite to ensure everything is working",
                order=step_order,
                category="testing",
                required=True,
                estimated_time=10,
                commands=test_commands
            ))
            step_order += 1
        
        # Step 6: Make first contribution
        steps.append(OnboardingStep(
            step_id=f"step_{step_order}",
            title="Make Your First Contribution",
            description="Pick a good first issue and submit a pull request",
            order=step_order,
            category="code",
            required=False,
            estimated_time=120,
            resources=["CONTRIBUTING.md"] if "CONTRIBUTING.md" in doc_files else []
        ))
        step_order += 1
        
        # Step 7: CI/CD understanding
        ci_configs = repo_info.get('ci_cd', {})
        if ci_configs:
            steps.append(OnboardingStep(
                step_id=f"step_{step_order}",
                title="Understand CI/CD Pipeline",
                description="Learn how the continuous integration and deployment works",
                order=step_order,
                category="deployment",
                required=False,
                estimated_time=15,
                resources=list(ci_configs.keys())
            ))
            step_order += 1
        
        return steps
    
    def _has_tests(self, repo_info: Dict[str, Any]) -> bool:
        """Check if repository has tests."""
        files = repo_info.get('files', [])
        for file in files:
            file_path = file.get('path', '').lower()
            if 'test' in file_path or 'spec' in file_path:
                return True
        return False
    
    def _get_test_commands(self, repo_info: Dict[str, Any]) -> List[str]:
        """Get test commands based on detected frameworks."""
        languages = repo_info.get('languages', {})
        dependencies = repo_info.get('dependencies', {})
        
        commands = []
        
        if 'package.json' in dependencies:
            commands.append("npm test")
        elif 'Python' in languages:
            commands.append("python -m pytest")
        elif 'pom.xml' in dependencies:
            commands.append("mvn test")
        elif 'build.gradle' in dependencies:
            commands.append("gradle test")
        else:
            commands.append("# Run test command specific to your project")
        
        return commands
    
    def create_checklist(self, repository_path: str, repo_info: Dict[str, Any],
                        title: Optional[str] = None,
                        organization_id: Optional[str] = None,
                        user_id: Optional[str] = None) -> OnboardingChecklist:
        """
        Create an onboarding checklist for a repository.
        
        Args:
            repository_path: Path to repository
            repo_info: Repository information
            title: Custom title for checklist
            organization_id: Organization context
            user_id: User creating the checklist
            
        Returns:
            Created OnboardingChecklist
        """
        # Check permission if needed
        if self.membership_manager and user_id and organization_id:
            if not self.membership_manager.check_permission(user_id, organization_id, Permission.WRITE):
                raise PermissionError("User does not have permission to create checklists")
        
        import secrets
        checklist_id = f"checklist_{secrets.token_urlsafe(12)}"
        created_at = datetime.now().isoformat()
        
        # Generate steps
        steps = self.analyze_repository(repo_info)
        total_time = sum(step.estimated_time or 0 for step in steps)
        
        # Prepare steps data for storage
        steps_data = json.dumps([asdict(step) for step in steps])
        
        if not title:
            title = f"Onboarding Guide for {repo_info.get('name', 'Repository')}"
        
        description = f"Complete onboarding guide for new contributors to {repo_info.get('name', 'this repository')}"
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO onboarding_checklists 
            (checklist_id, title, description, repository_path, organization_id,
             created_at, created_by, steps_data, total_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            checklist_id,
            title,
            description,
            repository_path,
            organization_id,
            created_at,
            user_id,
            steps_data,
            total_time
        ))
        self.conn.commit()
        
        return OnboardingChecklist(
            checklist_id=checklist_id,
            title=title,
            description=description,
            repository_path=repository_path,
            created_at=created_at,
            created_by=user_id,
            organization_id=organization_id,
            steps=steps,
            total_time=total_time
        )
    
    def get_checklist(self, checklist_id: str) -> Optional[OnboardingChecklist]:
        """Get a checklist by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM onboarding_checklists WHERE checklist_id = ?', (checklist_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        steps_data = json.loads(row['steps_data']) if row['steps_data'] else []
        steps = [OnboardingStep(**step) for step in steps_data]
        
        return OnboardingChecklist(
            checklist_id=row['checklist_id'],
            title=row['title'],
            description=row['description'],
            repository_path=row['repository_path'],
            created_at=row['created_at'],
            created_by=row['created_by'],
            organization_id=row['organization_id'],
            steps=steps,
            total_time=row['total_time']
        )
    
    def assign_checklist(self, checklist_id: str, user_id: str) -> OnboardingProgress:
        """
        Assign a checklist to a user.
        
        Args:
            checklist_id: Checklist ID
            user_id: User to assign to
            
        Returns:
            Created OnboardingProgress
        """
        import secrets
        progress_id = f"progress_{secrets.token_urlsafe(12)}"
        started_at = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO onboarding_progress 
            (progress_id, user_id, checklist_id, started_at, completed_steps)
            VALUES (?, ?, ?, ?, ?)
        ''', (progress_id, user_id, checklist_id, started_at, json.dumps([])))
        self.conn.commit()
        
        return OnboardingProgress(
            progress_id=progress_id,
            user_id=user_id,
            checklist_id=checklist_id,
            started_at=started_at,
            completed_steps=[],
            progress_percentage=0.0
        )
    
    def update_progress(self, progress_id: str, completed_step_id: str) -> OnboardingProgress:
        """
        Mark a step as completed.
        
        Args:
            progress_id: Progress ID
            completed_step_id: Step ID that was completed
            
        Returns:
            Updated OnboardingProgress
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM onboarding_progress WHERE progress_id = ?', (progress_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError("Progress not found")
        
        completed_steps = json.loads(row['completed_steps'])
        if completed_step_id not in completed_steps:
            completed_steps.append(completed_step_id)
        
        # Get checklist to calculate percentage
        checklist = self.get_checklist(row['checklist_id'])
        total_steps = len(checklist.steps) if checklist and checklist.steps else 1
        progress_percentage = (len(completed_steps) / total_steps) * 100
        
        # Check if completed
        completed_at = None
        if progress_percentage >= 100:
            completed_at = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE onboarding_progress 
            SET completed_steps = ?, progress_percentage = ?, completed_at = ?
            WHERE progress_id = ?
        ''', (json.dumps(completed_steps), progress_percentage, completed_at, progress_id))
        self.conn.commit()
        
        return OnboardingProgress(
            progress_id=progress_id,
            user_id=row['user_id'],
            checklist_id=row['checklist_id'],
            started_at=row['started_at'],
            completed_steps=completed_steps,
            completed_at=completed_at,
            progress_percentage=progress_percentage
        )
    
    def generate_markdown_guide(self, checklist: OnboardingChecklist) -> str:
        """
        Generate markdown onboarding guide.
        
        Args:
            checklist: Onboarding checklist
            
        Returns:
            Markdown formatted guide
        """
        lines = []
        lines.append(f"# {checklist.title}\n")
        lines.append(f"{checklist.description}\n")
        
        if checklist.total_time:
            hours = checklist.total_time // 60
            minutes = checklist.total_time % 60
            time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            lines.append(f"**Estimated Time**: {time_str}\n")
        
        # Group steps by category
        by_category = {}
        for step in checklist.steps or []:
            if step.category not in by_category:
                by_category[step.category] = []
            by_category[step.category].append(step)
        
        category_order = ['setup', 'documentation', 'code', 'testing', 'deployment']
        category_names = {
            'setup': 'Initial Setup',
            'documentation': 'Documentation',
            'code': 'Code Exploration',
            'testing': 'Testing',
            'deployment': 'Deployment & CI/CD'
        }
        
        for category in category_order:
            if category in by_category:
                lines.append(f"## {category_names.get(category, category.title())}\n")
                
                for step in sorted(by_category[category], key=lambda s: s.order):
                    required = "**Required**" if step.required else "*Optional*"
                    time = f" (~{step.estimated_time}min)" if step.estimated_time else ""
                    
                    lines.append(f"### {step.order + 1}. {step.title} {required}{time}\n")
                    lines.append(f"{step.description}\n")
                    
                    if step.commands:
                        lines.append("**Commands:**")
                        lines.append("```bash")
                        for cmd in step.commands:
                            lines.append(cmd)
                        lines.append("```\n")
                    
                    if step.resources:
                        lines.append("**Resources:**")
                        for resource in step.resources:
                            lines.append(f"- {resource}")
                        lines.append("")
                    
                    if step.prerequisites:
                        lines.append("**Prerequisites:**")
                        for prereq in step.prerequisites:
                            lines.append(f"- {prereq}")
                        lines.append("")
        
        lines.append("---")
        lines.append("*This onboarding guide was automatically generated by AccuDoc*")
        
        return '\n'.join(lines)
    
    def generate_interactive_checklist(self, checklist: OnboardingChecklist) -> str:
        """
        Generate interactive markdown checklist.
        
        Args:
            checklist: Onboarding checklist
            
        Returns:
            Interactive markdown checklist
        """
        lines = []
        lines.append(f"# {checklist.title} - Checklist\n")
        lines.append(f"{checklist.description}\n")
        lines.append("Track your progress by checking off items as you complete them.\n")
        
        if checklist.total_time:
            hours = checklist.total_time // 60
            minutes = checklist.total_time % 60
            time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            lines.append(f"**Total Estimated Time**: {time_str}\n")
        
        lines.append("## Progress Checklist\n")
        
        for step in sorted(checklist.steps or [], key=lambda s: s.order):
            required = "🔴" if step.required else "🟡"
            time = f" ({step.estimated_time}min)" if step.estimated_time else ""
            lines.append(f"- [ ] {required} **{step.title}**{time}")
            lines.append(f"  - {step.description}")
        
        lines.append("\n**Legend:**")
        lines.append("- 🔴 Required step")
        lines.append("- 🟡 Optional step")
        
        return '\n'.join(lines)
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
