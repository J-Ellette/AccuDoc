"""
Interactive wizard mode for AccuDoc.

Provides a step-by-step guided experience for new users.
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any


class WizardMode:
    """Interactive wizard for AccuDoc documentation generation."""
    
    def __init__(self):
        """Initialize wizard."""
        self.repository_path: Optional[Path] = None
        self.output_path: Optional[Path] = None
        self.template: str = 'default'
        self.output_format: str = 'markdown'
        self.markdown_flavor: str = 'github'
        self.html_theme: Optional[str] = None
        self.options: Dict[str, Any] = {}
    
    def run(self):
        """Run the interactive wizard."""
        self.print_welcome()
        
        # Step 1: Repository selection
        if not self.select_repository():
            return False
        
        # Step 2: Output location
        if not self.select_output():
            return False
        
        # Step 3: Template selection
        if not self.select_template():
            return False
        
        # Step 4: Output format
        if not self.select_format():
            return False
        
        # Step 5: Additional options
        if not self.select_options():
            return False
        
        # Step 6: Confirmation and generation
        return self.confirm_and_generate()
    
    def print_welcome(self):
        """Print welcome message."""
        print("\n" + "="*70)
        print("🧙 Welcome to AccuDoc Wizard Mode!")
        print("="*70)
        print("\nThis wizard will guide you through generating documentation")
        print("for your repository. You can exit at any time by pressing Ctrl+C.\n")
    
    def select_repository(self) -> bool:
        """Step 1: Select repository."""
        print("\n" + "="*70)
        print("Step 1: Repository Selection")
        print("="*70)
        
        print("\nWhat would you like to document?")
        print("  1. Current directory")
        print("  2. Specify a local path")
        print("  3. Clone from Git URL")
        
        choice = self.get_input("\nEnter your choice (1-3): ", ["1", "2", "3"])
        
        if choice == "1":
            self.repository_path = Path.cwd()
            print(f"\n✓ Using current directory: {self.repository_path}")
        elif choice == "2":
            while True:
                path_str = input("\nEnter the repository path: ").strip()
                path = Path(path_str).expanduser().resolve()
                if path.exists() and path.is_dir():
                    self.repository_path = path
                    print(f"\n✓ Selected: {self.repository_path}")
                    break
                else:
                    print(f"❌ Error: '{path}' is not a valid directory")
                    if not self.ask_yes_no("Try again?"):
                        return False
        else:  # choice == "3"
            print("\n📝 Note: Git clone support would be implemented here")
            print("   For now, please clone manually and use option 2")
            return self.select_repository()
        
        return True
    
    def select_output(self) -> bool:
        """Step 2: Select output location."""
        print("\n" + "="*70)
        print("Step 2: Output Location")
        print("="*70)
        
        print("\nWhere should we save the documentation?")
        print("  1. Same directory as repository (README.md)")
        print("  2. Docs folder (docs/)")
        print("  3. Custom location")
        
        choice = self.get_input("\nEnter your choice (1-3): ", ["1", "2", "3"])
        
        if choice == "1":
            self.output_path = self.repository_path / "README.md"
        elif choice == "2":
            self.output_path = self.repository_path / "docs"
        else:
            path_str = input("\nEnter output path: ").strip()
            self.output_path = Path(path_str).expanduser().resolve()
        
        print(f"\n✓ Documentation will be saved to: {self.output_path}")
        return True
    
    def select_template(self) -> bool:
        """Step 3: Select documentation template."""
        print("\n" + "="*70)
        print("Step 3: Documentation Template")
        print("="*70)
        
        print("\nWhat type of documentation would you like to generate?")
        print("\n  1. Default - Complete documentation with all sections")
        print("  2. Minimal - Essential sections only (quick start)")
        print("  3. Detailed - Comprehensive technical documentation")
        print("  4. API Reference - Focus on API documentation")
        print("  5. README Style - GitHub README format")
        print("  6. Student Project - Academic/student project template")
        
        choice = self.get_input("\nEnter your choice (1-6): ", ["1", "2", "3", "4", "5", "6"])
        
        templates = {
            "1": "default",
            "2": "minimal",
            "3": "detailed",
            "4": "api",
            "5": "readme",
            "6": "student"
        }
        
        self.template = templates[choice]
        template_names = {
            "default": "Default (Complete)",
            "minimal": "Minimal (Essential)",
            "detailed": "Detailed (Comprehensive)",
            "api": "API Reference",
            "readme": "README Style",
            "student": "Student Project"
        }
        
        print(f"\n✓ Template: {template_names[self.template]}")
        return True
    
    def select_format(self) -> bool:
        """Step 4: Select output format."""
        print("\n" + "="*70)
        print("Step 4: Output Format")
        print("="*70)
        
        print("\nWhat format would you like for the documentation?")
        print("\n  1. Markdown (default)")
        print("  2. HTML (with styling)")
        print("  3. PDF (requires additional dependencies)")
        print("  4. Plain text")
        
        choice = self.get_input("\nEnter your choice (1-4): ", ["1", "2", "3", "4"])
        
        formats = {
            "1": "markdown",
            "2": "html",
            "3": "pdf",
            "4": "text"
        }
        
        self.output_format = formats[choice]
        
        # If markdown, ask about flavor
        if self.output_format == "markdown":
            print("\nWhich Markdown flavor?")
            print("  1. GitHub Flavored Markdown (default)")
            print("  2. GitLab Flavored Markdown")
            print("  3. CommonMark")
            
            flavor_choice = self.get_input("\nEnter your choice (1-3, or press Enter for default): ", 
                                          ["1", "2", "3", ""], allow_empty=True)
            
            flavors = {"1": "github", "2": "gitlab", "3": "commonmark", "": "github"}
            self.markdown_flavor = flavors.get(flavor_choice, "github")
        
        # If HTML, ask about theme
        elif self.output_format == "html":
            print("\nWhich HTML theme?")
            print("  1. Default (light, professional)")
            print("  2. Dark (modern dark theme)")
            print("  3. Minimal (ultra-clean)")
            print("  4. Corporate (professional gradient)")
            
            theme_choice = self.get_input("\nEnter your choice (1-4, or press Enter for default): ",
                                         ["1", "2", "3", "4", ""], allow_empty=True)
            
            themes = {"1": "default", "2": "dark", "3": "minimal", "4": "corporate", "": "default"}
            self.html_theme = themes.get(theme_choice, "default")
        
        # PDF warning
        elif self.output_format == "pdf":
            print("\n📝 Note: PDF export requires 'weasyprint' or 'wkhtmltopdf'")
            if not self.ask_yes_no("Continue with PDF?"):
                return self.select_format()
        
        print(f"\n✓ Format: {self.output_format.upper()}")
        return True
    
    def select_options(self) -> bool:
        """Step 5: Select additional options."""
        print("\n" + "="*70)
        print("Step 5: Additional Options")
        print("="*70)
        
        print("\nWould you like to enable any additional features?")
        print("(Press Enter to skip each option)")
        
        # Code analysis
        if self.ask_yes_no("\n• Include code complexity analysis?", default=False):
            self.options['complexity'] = True
        
        # Best practices
        if self.ask_yes_no("• Check for best practices violations?", default=False):
            self.options['best_practices'] = True
        
        # Security scan
        if self.ask_yes_no("• Scan for exposed secrets?", default=False):
            self.options['security'] = True
        
        # Spell check
        if self.ask_yes_no("• Run spell checker on documentation?", default=False):
            self.options['spellcheck'] = True
        
        # Link check
        if self.ask_yes_no("• Validate all links in documentation?", default=False):
            self.options['linkcheck'] = True
        
        if self.options:
            print(f"\n✓ Enabled {len(self.options)} additional feature(s)")
        else:
            print("\n✓ No additional features selected")
        
        return True
    
    def confirm_and_generate(self) -> bool:
        """Step 6: Confirm and generate."""
        print("\n" + "="*70)
        print("Step 6: Summary & Confirmation")
        print("="*70)
        
        print("\n📋 Documentation Generation Summary:")
        print(f"\n  Repository:    {self.repository_path}")
        print(f"  Output:        {self.output_path}")
        print(f"  Template:      {self.template}")
        print(f"  Format:        {self.output_format}")
        
        if self.output_format == "markdown":
            print(f"  Flavor:        {self.markdown_flavor}")
        elif self.html_theme:
            print(f"  Theme:         {self.html_theme}")
        
        if self.options:
            print(f"  Options:       {', '.join(self.options.keys())}")
        
        print()
        
        if not self.ask_yes_no("Generate documentation now?", default=True):
            print("\n❌ Documentation generation cancelled")
            return False
        
        # Generate the command that would be run
        print("\n" + "="*70)
        print("🚀 Generating Documentation...")
        print("="*70)
        
        command = self.build_command()
        print(f"\nEquivalent command:\n  {command}\n")
        
        print("📝 Note: In a full implementation, this would:")
        print("  1. Scan the repository")
        print("  2. Analyze the code")
        print("  3. Generate documentation")
        print("  4. Save to the specified location")
        print("  5. Apply any additional checks")
        
        print("\n" + "="*70)
        print("✅ Wizard Complete!")
        print("="*70)
        print("\n💡 Tip: You can run the command above directly next time")
        print("   to skip the wizard.")
        
        return True
    
    def build_command(self) -> str:
        """Build the equivalent CLI command."""
        parts = [
            "python accudoc_cli.py generate",
            str(self.repository_path),
            f"--output {self.output_path}",
            f"--template {self.template}"
        ]
        
        if self.output_format != "markdown":
            parts.append(f"--format {self.output_format}")
        
        if self.output_format == "markdown" and self.markdown_flavor != "github":
            parts.append(f"--flavor {self.markdown_flavor}")
        
        if self.html_theme:
            parts.append(f"--theme {self.html_theme}")
        
        for option in self.options:
            parts.append(f"--{option}")
        
        return " ".join(parts)
    
    def get_input(self, prompt: str, valid_choices: List[str], 
                  allow_empty: bool = False) -> str:
        """Get user input with validation."""
        while True:
            choice = input(prompt).strip()
            
            if allow_empty and choice == "":
                return ""
            
            if choice in valid_choices:
                return choice
            
            print(f"❌ Invalid choice. Please enter one of: {', '.join(valid_choices)}")
    
    def ask_yes_no(self, question: str, default: Optional[bool] = None) -> bool:
        """Ask a yes/no question."""
        if default is True:
            prompt = f"{question} [Y/n]: "
            default_value = "y"
        elif default is False:
            prompt = f"{question} [y/N]: "
            default_value = "n"
        else:
            prompt = f"{question} [y/n]: "
            default_value = None
        
        while True:
            response = input(prompt).strip().lower()
            
            if response == "" and default_value:
                response = default_value
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("❌ Please answer 'y' or 'n'")


def run_wizard():
    """Run the wizard mode."""
    wizard = WizardMode()
    try:
        return wizard.run()
    except KeyboardInterrupt:
        print("\n\n❌ Wizard cancelled by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        return False


if __name__ == '__main__':
    sys.exit(0 if run_wizard() else 1)
