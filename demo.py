#!/usr/bin/env python3
"""
Demo script for AccuDoc - Command Line Interface

This script demonstrates AccuDoc functionality without the GUI.
It can be used to generate documentation from the command line.
"""

import sys
import argparse
from pathlib import Path
from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator


def main():
    """Main entry point for CLI demo."""
    parser = argparse.ArgumentParser(
        description="AccuDoc - Automated Repository Documentation Generator (CLI Demo)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/local/repo
  %(prog)s /path/to/local/repo -o documentation.md
  %(prog)s https://github.com/user/repo
        """
    )
    
    parser.add_argument(
        'repository',
        help='Path to local repository or remote Git URL'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (optional, prints to stdout if not specified)',
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        print(f"Scanning repository: {args.repository}")
        print("-" * 60)
        
        # Scan repository
        scanner = RepositoryScanner(args.repository)
        repo_info = scanner.scan()
        
        print(f"✓ Repository: {repo_info['name']}")
        print(f"✓ Files found: {len(repo_info['files'])}")
        print(f"✓ Languages: {', '.join(repo_info['languages'].keys()) or 'None detected'}")
        print(f"✓ Dependencies: {', '.join(repo_info['dependencies'].keys()) or 'None detected'}")
        print()
        
        # Generate documentation
        print("Generating documentation...")
        generator = DocumentGenerator(repo_info)
        documentation = generator.generate_all()
        
        print(f"✓ Generated {len(documentation)} characters of documentation")
        print()
        
        # Output
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(documentation)
            print(f"✓ Documentation saved to: {output_path}")
            print(f"✓ Absolute path: {output_path.absolute()}")
        else:
            print("-" * 60)
            print("GENERATED DOCUMENTATION:")
            print("-" * 60)
            print(documentation)
            
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
