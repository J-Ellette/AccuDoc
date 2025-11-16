#!/usr/bin/env python3
"""
AccuDoc CLI - Command-line interface for AccuDoc.

Provides comprehensive CLI for repository documentation generation with
automation support for CI/CD integration.
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List
from accudoc.scanner import RepositoryScanner
from accudoc.generator import DocumentGenerator
from accudoc.cache import CacheManager
from accudoc.linkchecker import check_documentation_links
from accudoc.github_api import GitHubAPIClient, scan_github_repository
from accudoc.gitlab_api import GitLabAPIClient, scan_gitlab_repository
from accudoc.bitbucket_api import BitbucketAPIClient, scan_bitbucket_repository
from accudoc.plugins import get_plugin_manager
from quality_scoring import QualityAnalyzer


class AccuDocCLI:
    """Command-line interface for AccuDoc."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.logger = logging.getLogger('accudoc')
        self.setup_logging()
        
    def setup_logging(self, verbosity: int = 0):
        """
        Setup logging based on verbosity level.
        
        Args:
            verbosity: 0=WARNING, 1=INFO, 2=DEBUG
        """
        levels = [logging.WARNING, logging.INFO, logging.DEBUG]
        level = levels[min(verbosity, len(levels) - 1)]
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
    def scan_command(self, args):
        """Execute scan command."""
        self.logger.info(f"Scanning repository: {args.repository}")
        
        # Progress callback
        def progress_callback(message):
            if not args.quiet:
                print(f"  {message}")
        
        try:
            scanner = RepositoryScanner(args.repository, progress_callback=progress_callback)
            
            # Handle caching options
            if args.no_cache:
                scanner.disable_cache()
            
            repo_info = scanner.scan()
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    json.dump(repo_info, f, indent=2, default=str)
                self.logger.info(f"Scan results saved to: {output_path}")
                if not args.quiet:
                    print(f"\n✓ Scan complete. Results saved to: {output_path}")
            else:
                if args.json:
                    print(json.dumps(repo_info, indent=2, default=str))
                else:
                    self._print_scan_summary(repo_info, args.quiet)
                    
            return 0
            
        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def _print_scan_summary(self, repo_info: Dict, quiet: bool = False):
        """Print a summary of scan results."""
        if quiet:
            return
            
        print("\n" + "=" * 60)
        print("Scan Summary")
        print("=" * 60)
        print(f"Repository: {repo_info['name']}")
        print(f"Files: {len(repo_info.get('files', []))}")
        print(f"Languages: {', '.join(repo_info.get('languages', {}).keys())}")
        print(f"Dependencies: {len(repo_info.get('dependencies', {}))}")
        print(f"Documentation files: {len(repo_info.get('documentation', []))}")
        print(f"License: {repo_info.get('license', 'Not found')}")
        print("=" * 60)
    
    def generate_command(self, args):
        """Execute generate command."""
        self.logger.info(f"Generating documentation from: {args.scan_file}")
        
        try:
            # Load scan results
            with open(args.scan_file, 'r') as f:
                repo_info = json.load(f)
            
            # Generate documentation
            generator = DocumentGenerator(repo_info, template=args.template)
            
            if not args.quiet:
                print(f"Generating documentation using template: {args.template}")
            
            # Export to file
            output_path = generator.generate_and_export(
                args.output,
                format=args.format,
                theme=args.theme,
                markdown_flavor=args.markdown_flavor,
                language=args.language
            )
            
            self.logger.info(f"Documentation saved to: {output_path}")
            if not args.quiet:
                print(f"✓ Documentation generated: {output_path}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}")
            if not args.quiet:
                print(f"✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def export_command(self, args):
        """Execute export command (combined scan + generate)."""
        self.logger.info(f"Processing repository: {args.repository}")
        
        # Progress callback
        def progress_callback(message):
            if not args.quiet:
                print(f"  {message}")
        
        try:
            # Scan repository
            if not args.quiet:
                print("Scanning repository...")
            scanner = RepositoryScanner(args.repository, progress_callback=progress_callback)
            
            # Handle caching options
            if args.no_cache:
                scanner.disable_cache()
            
            repo_info = scanner.scan()
            
            # Generate documentation
            if not args.quiet:
                print(f"\nGenerating documentation using template: {args.template}")
            generator = DocumentGenerator(repo_info, template=args.template)
            output_path = generator.generate_and_export(
                args.output,
                format=args.format,
                theme=args.theme,
                markdown_flavor=args.markdown_flavor,
                language=args.language
            )
            
            self.logger.info(f"Documentation saved to: {output_path}")
            if not args.quiet:
                print(f"\n✓ Documentation generated: {output_path}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Export failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def site_command(self, args):
        """Execute static site generation command."""
        self.logger.info(f"Generating static site from: {args.repository}")
        
        # Progress callback
        def progress_callback(message):
            if not args.quiet:
                print(f"  {message}")
        
        try:
            # Scan repository
            if not args.quiet:
                print("Scanning repository...")
            scanner = RepositoryScanner(args.repository, progress_callback=progress_callback)
            
            # Handle caching options
            if args.no_cache:
                scanner.disable_cache()
            
            repo_info = scanner.scan()
            
            # Generate static site
            if not args.quiet:
                print(f"\nGenerating static site in: {args.output}")
            
            from accudoc.static_site import generate_static_site
            from pathlib import Path
            
            index_path = generate_static_site(
                repo_info,
                Path(args.output),
                title=args.title or repo_info.get('name', 'Documentation'),
                theme=args.theme
            )
            
            self.logger.info(f"Static site generated: {index_path}")
            if not args.quiet:
                print(f"\n✓ Static site generated: {index_path}")
                print(f"   Open in browser: file://{index_path.absolute()}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Site generation failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def info_command(self, args):
        """Execute info command - display information about AccuDoc."""
        print("AccuDoc - Automated Repository Documentation Generator")
        print("=" * 60)
        print("\nAvailable Templates:")
        templates = ['default', 'minimal', 'detailed', 'api', 'readme']
        for template in templates:
            print(f"  - {template}")
        
        print("\nAvailable Formats:")
        formats = ['markdown', 'html', 'txt', 'pdf']
        for fmt in formats:
            print(f"  - {fmt}")
        
        print("\nAvailable Themes (HTML):")
        themes = ['default', 'dark', 'minimal', 'corporate']
        for theme in themes:
            print(f"  - {theme}")
        
        print("\nAvailable Markdown Flavors:")
        flavors = ['github', 'gitlab', 'commonmark']
        for flavor in flavors:
            print(f"  - {flavor}")
        
        print("\nFor more information, visit:")
        print("  https://github.com/jamesellette/AccuDoc")
        print("=" * 60)
        
        return 0
    
    def plugins_command(self, args):
        """Execute plugins command - manage plugins."""
        try:
            plugin_manager = get_plugin_manager()
            
            if args.plugin_action == 'list':
                plugins = plugin_manager.list_plugins()
                
                print("AccuDoc Plugins")
                print("=" * 60)
                
                if plugins['analyzers']:
                    print("\nAnalyzers:")
                    for name in plugins['analyzers']:
                        print(f"  - {name}")
                else:
                    print("\nNo analyzer plugins loaded")
                
                if plugins['exporters']:
                    print("\nExporters:")
                    for name in plugins['exporters']:
                        print(f"  - {name}")
                else:
                    print("\nNo exporter plugins loaded")
                
                if plugins['templates']:
                    print("\nTemplates:")
                    for name in plugins['templates']:
                        print(f"  - {name}")
                else:
                    print("\nNo template plugins loaded")
                
                print("=" * 60)
                
            elif args.plugin_action == 'info':
                plugin_info = plugin_manager.get_plugin_info()
                
                if not plugin_info:
                    print("No plugins loaded")
                    return 0
                
                print("Plugin Information")
                print("=" * 60)
                
                for info in plugin_info:
                    print(f"\n{info['type'].upper()}: {info['name']}")
                    print(f"  Version: {info['version']}")
                    print(f"  Description: {info['description']}")
                    if 'extension' in info:
                        print(f"  Extension: {info['extension']}")
                
                print("=" * 60)
            
            return 0
            
        except Exception as e:
            print(f"Error managing plugins: {str(e)}", file=sys.stderr)
            return 1
    
    def cache_command(self, args):
        """Execute cache management command."""
        if args.cache_action == 'stats':
            return self._cache_stats(args)
        elif args.cache_action == 'clear':
            return self._cache_clear(args)
        else:
            print("Invalid cache action", file=sys.stderr)
            return 1
    
    def _cache_stats(self, args):
        """Show cache statistics."""
        try:
            cache = CacheManager(args.repository)
            cache.initialize()
            stats = cache.get_stats()
            
            print("Cache Statistics")
            print("=" * 60)
            print(f"Repository: {args.repository}")
            print(f"Cache Directory: {stats['cache_dir']}")
            print(f"Cache Enabled: {stats['enabled']}")
            print(f"Cache Exists: {stats['cache_exists']}")
            print(f"Cache Version: {stats['version']}")
            print(f"Created: {stats['created_at']}")
            print(f"Last Updated: {stats['last_updated']}")
            print(f"Cached Files: {stats['cached_files']}")
            print(f"Total Size: {stats['total_size_bytes']:,} bytes")
            print("=" * 60)
            
            return 0
        except Exception as e:
            print(f"Error getting cache stats: {str(e)}", file=sys.stderr)
            return 1
    
    def _cache_clear(self, args):
        """Clear cache."""
        try:
            cache = CacheManager(args.repository)
            cache.initialize()
            cache.clear()
            
            if not args.quiet:
                print(f"✓ Cache cleared for: {args.repository}")
            
            return 0
        except Exception as e:
            print(f"Error clearing cache: {str(e)}", file=sys.stderr)
            return 1
    
    def check_links_command(self, args):
        """Execute link checking command."""
        try:
            doc_path = Path(args.path)
            
            if not doc_path.exists():
                print(f"Error: Path not found: {doc_path}", file=sys.stderr)
                return 1
            
            if not args.quiet:
                print(f"Checking links in: {doc_path}")
            
            # Check links
            report = check_documentation_links(doc_path, output_format=args.format)
            
            # Output report
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                if not args.quiet:
                    print(f"\n✓ Link check report saved to: {args.output}")
            else:
                print(report)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Link checking failed: {str(e)}")
            if not args.quiet:
                print(f"Error: {str(e)}", file=sys.stderr)
            return 1
    
    def batch_command(self, args):
        """Execute batch command - process multiple repositories."""
        self.logger.info(f"Processing batch file: {args.batch_file}")
        
        try:
            # Load batch configuration
            with open(args.batch_file, 'r') as f:
                batch_config = json.load(f)
            
            repositories = batch_config.get('repositories', [])
            if not repositories:
                print("No repositories found in batch file", file=sys.stderr)
                return 1
            
            success_count = 0
            fail_count = 0
            
            for i, repo_config in enumerate(repositories, 1):
                repo_url = repo_config.get('url') or repo_config.get('path')
                output = repo_config.get('output', f'docs_{i}.md')
                template = repo_config.get('template', 'default')
                
                if not args.quiet:
                    print(f"\n[{i}/{len(repositories)}] Processing: {repo_url}")
                
                try:
                    # Create temporary args for export command
                    export_args = argparse.Namespace(
                        repository=repo_url,
                        output=output,
                        template=template,
                        format=repo_config.get('format', 'markdown'),
                        theme=repo_config.get('theme', 'default'),
                        markdown_flavor=repo_config.get('markdown_flavor', 'github'),
                        quiet=args.quiet
                    )
                    
                    result = self.export_command(export_args)
                    if result == 0:
                        success_count += 1
                    else:
                        fail_count += 1
                        
                except Exception as e:
                    self.logger.error(f"Failed to process {repo_url}: {str(e)}")
                    fail_count += 1
            
            if not args.quiet:
                print(f"\n{'=' * 60}")
                print(f"Batch processing complete:")
                print(f"  Success: {success_count}/{len(repositories)}")
                print(f"  Failed: {fail_count}/{len(repositories)}")
                print("=" * 60)
            
            return 0 if fail_count == 0 else 1
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            if not args.quiet:
                print(f"✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def branch_compare_command(self, args):
        """Execute branch comparison command."""
        from accudoc.branch_comparison import BranchComparator
        
        self.logger.info(f"Comparing branches in: {args.repository}")
        
        try:
            comparator = BranchComparator(args.repository)
            
            # If list branches requested
            if args.list_branches:
                branches = comparator.get_available_branches()
                if not args.quiet:
                    print("\nAvailable branches:")
                    for branch in branches:
                        current = " (current)" if branch == comparator.get_current_branch() else ""
                        print(f"  - {branch}{current}")
                return 0
            
            # Perform comparison
            base_branch = args.base
            compare_branch = args.compare
            
            if not base_branch or not compare_branch:
                print("Error: Both --base and --compare branches are required", file=sys.stderr)
                return 1
            
            comparison = comparator.compare_branches(base_branch, compare_branch)
            
            # Generate report
            if args.format == 'json':
                output_data = json.dumps(comparison, indent=2, default=str)
            else:
                output_data = comparator.generate_comparison_markdown(comparison)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Comparison report saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Branch comparison failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def version_check_command(self, args):
        """Execute version checking command."""
        from accudoc.version_analyzer import VersionAnalyzer
        
        self.logger.info(f"Analyzing dependencies in: {args.repository}")
        
        try:
            analyzer = VersionAnalyzer(args.repository)
            
            # Analyze dependencies
            dependencies = analyzer.analyze_all_dependencies()
            
            if not dependencies:
                if not args.quiet:
                    print("\nNo dependency files found (requirements.txt, package.json)")
                return 0
            
            # Generate report
            if args.format == 'json':
                output_data = json.dumps(dependencies, indent=2, default=str)
            else:
                output_data = analyzer.generate_analysis_report(dependencies)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Version analysis report saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Version analysis failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def spellcheck_command(self, args):
        """Execute spell checking command."""
        from accudoc.spellcheck import SpellChecker
        
        self.logger.info(f"Spell checking: {args.path}")
        
        try:
            checker = SpellChecker()
            path = Path(args.path)
            
            # Check if path is file or directory
            if path.is_file():
                results = [checker.check_file(path)]
            elif path.is_dir():
                extensions = args.extensions.split(',') if args.extensions else None
                results = checker.check_directory(path, extensions)
            else:
                print(f"Error: Path not found: {path}", file=sys.stderr)
                return 1
            
            # Generate report
            if args.format == 'json':
                output_data = json.dumps(results, indent=2, default=str)
            else:
                output_data = checker.generate_report(results)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Spell check report saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Spell checking failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def multi_repo_command(self, args):
        """Execute multi-repository command."""
        from accudoc.multi_repo import MultiRepositoryManager
        
        self.logger.info("Processing multiple repositories")
        
        try:
            # Load repository configuration
            with open(args.config, 'r') as f:
                config = json.load(f)
            
            repositories = config.get('repositories', [])
            if not repositories:
                print("Error: No repositories defined in config file", file=sys.stderr)
                return 1
            
            # Progress callback
            def progress_callback(message):
                if not args.quiet:
                    print(f"  {message}")
            
            manager = MultiRepositoryManager(max_workers=args.workers)
            results = manager.scan_repositories(repositories, progress_callback)
            
            # Generate documentation
            if args.format == 'json':
                output_data = json.dumps(results, indent=2, default=str)
            elif args.format == 'comparison':
                output_data = manager.generate_comparison_matrix(results)
            else:  # markdown
                title = config.get('title', 'Multi-Repository Documentation')
                output_data = manager.generate_unified_documentation(results, title)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Multi-repository documentation saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Multi-repository processing failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def coverage_command(self, args):
        """Execute test coverage analysis command."""
        from accudoc.test_coverage import TestCoverageAnalyzer
        
        self.logger.info(f"Analyzing test coverage in: {args.repository}")
        
        try:
            analyzer = TestCoverageAnalyzer(args.repository)
            coverage_data = analyzer.analyze_coverage()
            
            if coverage_data.get('status') == 'no_coverage':
                if not args.quiet:
                    print("\nNo test coverage files found.")
                    print("Supported formats: coverage.xml (Python), coverage-final.json (JavaScript), coverage.out (Go)")
                return 0
            
            # Generate report
            if args.format == 'json':
                output_data = json.dumps(coverage_data, indent=2, default=str)
            else:
                output_data = analyzer.generate_coverage_report(coverage_data)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Coverage report saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Coverage analysis failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def readability_command(self, args):
        """Execute readability analysis command."""
        from accudoc.readability import ReadabilityAnalyzer
        
        self.logger.info(f"Analyzing readability: {args.path}")
        
        try:
            analyzer = ReadabilityAnalyzer()
            path = Path(args.path)
            
            # Check if path is file or directory
            if path.is_file():
                results = [analyzer.analyze_file(path)]
            elif path.is_dir():
                extensions = args.extensions.split(',') if args.extensions else None
                results = analyzer.analyze_directory(path, extensions)
            else:
                print(f"Error: Path not found: {path}", file=sys.stderr)
                return 1
            
            # Generate report
            if args.format == 'json':
                output_data = json.dumps(results, indent=2, default=str)
            else:
                output_data = analyzer.generate_report(results)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Readability report saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Readability analysis failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def db_schema_command(self, args):
        """Execute database schema extraction command."""
        from accudoc.db_schema import DatabaseSchemaExtractor
        
        self.logger.info(f"Extracting database schema from: {args.repository}")
        
        try:
            extractor = DatabaseSchemaExtractor(args.repository)
            schema = extractor.extract_schema()
            
            if schema.get('status') == 'no_schema':
                if not args.quiet:
                    print("\nNo database schema files found.")
                    print("Supported: SQL migrations, Django models, Rails migrations, schema files")
                return 0
            
            # Generate documentation
            if args.format == 'json':
                output_data = json.dumps(schema, indent=2, default=str)
            else:
                output_data = extractor.generate_schema_documentation(schema)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Schema documentation saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Schema extraction failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def monorepo_command(self, args):
        """Execute monorepo analysis command."""
        from accudoc.monorepo import MonorepoDetector
        
        self.logger.info(f"Analyzing monorepo structure: {args.repository}")
        
        try:
            detector = MonorepoDetector(args.repository)
            
            if not detector.is_monorepo():
                if not args.quiet:
                    print("\nNot a monorepo structure.")
                return 0
            
            monorepo_data = detector.scan_monorepo()
            
            # Generate documentation
            if args.format == 'json':
                output_data = json.dumps(monorepo_data, indent=2, default=str)
            else:
                output_data = detector.generate_monorepo_documentation(monorepo_data)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Monorepo documentation saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Monorepo analysis failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def breaking_changes_command(self, args):
        """Execute breaking changes detection command."""
        from accudoc.breaking_changes import BreakingChangesDetector
        
        self.logger.info(f"Analyzing breaking changes: {args.from_ref} -> {args.to_ref}")
        
        try:
            detector = BreakingChangesDetector(args.repository)
            changes = detector.analyze_changes(args.from_ref, args.to_ref)
            
            # Check semantic versioning if versions provided
            semver_check = None
            if args.from_version and args.to_version:
                semver_check = detector.check_semantic_versioning(
                    args.from_version, args.to_version, changes
                )
            
            # Generate report
            if args.format == 'json':
                output_data = json.dumps({
                    'changes': changes,
                    'semver_check': semver_check
                }, indent=2, default=str)
            else:
                output_data = detector.generate_report(changes, semver_check)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Breaking changes report saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Breaking changes analysis failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def code_quality_command(self, args):
        """Execute code quality analysis command."""
        from accudoc.code_quality import CodeQualityAnalyzer
        
        self.logger.info(f"Analyzing code quality: {args.repository}")
        
        try:
            analyzer = CodeQualityAnalyzer(args.repository)
            results = analyzer.analyze_directory()
            
            if not results:
                if not args.quiet:
                    print("\nNo code files found to analyze.")
                return 0
            
            summary = analyzer.generate_summary(results)
            
            # Generate report
            if args.format == 'json':
                output_data = json.dumps({
                    'results': results,
                    'summary': summary
                }, indent=2, default=str)
            else:
                output_data = analyzer.generate_report(results, summary)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Code quality report saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Code quality analysis failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def grammar_check_command(self, args):
        """Execute grammar checking command."""
        from accudoc.grammar_check import GrammarChecker
        
        self.logger.info(f"Checking grammar: {args.path}")
        
        try:
            checker = GrammarChecker()
            path = Path(args.path)
            
            # Check if path is file or directory
            if path.is_file():
                results = [checker.check_file(path)]
            elif path.is_dir():
                extensions = args.extensions.split(',') if args.extensions else None
                results = checker.check_directory(path, extensions)
            else:
                print(f"Error: Path not found: {path}", file=sys.stderr)
                return 1
            
            # Generate report
            if args.format == 'json':
                output_data = json.dumps(results, indent=2, default=str)
            else:
                output_data = checker.generate_report(results)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Grammar check report saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Grammar checking failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def doc_coverage_command(self, args):
        """Execute documentation coverage analysis command."""
        from accudoc.doc_coverage import DocumentationCoverageAnalyzer
        
        self.logger.info(f"Analyzing documentation coverage: {args.repository}")
        
        try:
            analyzer = DocumentationCoverageAnalyzer(args.repository)
            results = analyzer.analyze_directory()
            
            if not results:
                if not args.quiet:
                    print("\nNo code files found to analyze.")
                return 0
            
            overall = analyzer.calculate_overall_coverage(results)
            
            # Generate report
            if args.format == 'json':
                output_data = json.dumps({
                    'results': results,
                    'overall': overall
                }, indent=2, default=str)
            else:
                output_data = analyzer.generate_report(results, overall)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Documentation coverage report saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Documentation coverage analysis failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def dataflow_command(self, args):
        """Execute data flow analysis command."""
        from accudoc.dataflow import DataFlowAnalyzer
        
        self.logger.info(f"Analyzing data flow: {args.repository}")
        
        try:
            analyzer = DataFlowAnalyzer(args.repository)
            
            # Analyze repository or single file
            if Path(args.repository).is_file():
                results = analyzer.analyze_file(Path(args.repository))
            else:
                results = analyzer.analyze_repository()
            
            # Generate report
            include_diagrams = not args.no_diagrams
            if args.format == 'json':
                output_data = json.dumps(results, indent=2, default=str)
            else:
                output_data = analyzer.generate_report(results, include_diagrams=include_diagrams)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    f.write(output_data)
                if not args.quiet:
                    print(f"\n✓ Data flow analysis report saved to: {output_path}")
            else:
                print(output_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Data flow analysis failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def config_command(self, args):
        """Execute configuration management command."""
        from accudoc.config import ConfigManager
        
        self.logger.info("Managing configuration")
        
        try:
            manager = ConfigManager()
            
            # Init: Create example config file
            if args.config_action == 'init':
                format = args.format or 'yaml'
                output = args.output or f'accudoc.{format}'
                
                content = manager.generate_example_config(format=format)
                
                output_path = Path(output)
                with open(output_path, 'w') as f:
                    f.write(content)
                
                if not args.quiet:
                    print(f"\n✓ Created example config file: {output_path}")
                    print(f"  Edit this file to customize your documentation settings")
                
                return 0
            
            # Show: Display current config
            elif args.config_action == 'show':
                config_path = args.config or manager._find_config_file()
                
                if not config_path:
                    if not args.quiet:
                        print("\nNo configuration file found.")
                        print("Run 'accudoc_cli.py config init' to create one.")
                    return 1
                
                config = manager.load_config(str(config_path) if config_path else None)
                
                # Output as JSON for easy reading
                data = manager._config_to_dict(config)
                print(json.dumps(data, indent=2))
                
                return 0
            
            # Validate: Check config file syntax
            elif args.config_action == 'validate':
                config_path = args.config
                
                if not config_path:
                    if not args.quiet:
                        print("\n✗ Error: No config file specified")
                        print("  Use: accudoc_cli.py config validate --config <file>")
                    return 1
                
                try:
                    config = manager.load_config(config_path)
                    
                    if not args.quiet:
                        print(f"\n✓ Configuration file is valid: {config_path}")
                        print(f"  Version: {config.version}")
                        print(f"  Repository: {config.repository or 'Not specified'}")
                        print(f"  Template: {config.generate.template}")
                        print(f"  Format: {config.generate.format}")
                    
                    return 0
                    
                except Exception as e:
                    if not args.quiet:
                        print(f"\n✗ Configuration file is invalid: {config_path}")
                        print(f"  Error: {str(e)}")
                    return 1
            
            else:
                if not args.quiet:
                    print("\n✗ Error: Unknown config action")
                return 1
            
        except Exception as e:
            self.logger.error(f"Configuration command failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def opensource_command(self, args):
        """Execute open source documentation generation command."""
        from accudoc.opensource_docs import OpenSourceDocsGenerator
        from accudoc.scanner import RepositoryScanner
        
        self.logger.info(f"Generating open source documentation for: {args.repository}")
        
        try:
            # Scan repository first
            scanner = RepositoryScanner(args.repository)
            repo_info = scanner.scan()
            
            # Create generator
            generator = OpenSourceDocsGenerator(repo_info)
            
            # Determine what to generate
            generate_all = args.all or not (args.contributing or args.conduct or args.issues)
            
            created_files = []
            
            # Generate CONTRIBUTING.md
            if generate_all or args.contributing:
                contributing_path = Path(args.output_dir) / 'CONTRIBUTING.md'
                contributing_path.parent.mkdir(parents=True, exist_ok=True)
                content = generator.generate_contributing_guide()
                with open(contributing_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created_files.append(str(contributing_path))
                self.logger.info(f"Created: {contributing_path}")
            
            # Generate CODE_OF_CONDUCT.md
            if generate_all or args.conduct:
                conduct_path = Path(args.output_dir) / 'CODE_OF_CONDUCT.md'
                conduct_path.parent.mkdir(parents=True, exist_ok=True)
                content = generator.generate_code_of_conduct()
                with open(conduct_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created_files.append(str(conduct_path))
                self.logger.info(f"Created: {conduct_path}")
            
            # Generate issue templates
            if generate_all or args.issues:
                issue_dir = Path(args.output_dir) / '.github' / 'ISSUE_TEMPLATE'
                issue_dir.mkdir(parents=True, exist_ok=True)
                
                # Bug report
                bug_path = issue_dir / 'bug_report.md'
                content = generator.generate_issue_template_bug()
                with open(bug_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created_files.append(str(bug_path))
                self.logger.info(f"Created: {bug_path}")
                
                # Feature request
                feature_path = issue_dir / 'feature_request.md'
                content = generator.generate_issue_template_feature()
                with open(feature_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created_files.append(str(feature_path))
                self.logger.info(f"Created: {feature_path}")
            
            # Output results
            if not args.quiet:
                print(f"\n✓ Generated open source documentation for {repo_info.get('name', 'repository')}")
                print(f"\nCreated {len(created_files)} file(s):")
                for file_path in created_files:
                    print(f"  • {file_path}")
                
                if args.output_dir != '.':
                    print(f"\nFiles created in: {args.output_dir}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Open source documentation generation failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def data_export_command(self, args):
        """Execute data export command."""
        from accudoc.data_export import export_data
        from accudoc.scanner import RepositoryScanner
        import json
        
        self.logger.info(f"Exporting data from: {args.repository}")
        
        try:
            # Load scan results or scan repository
            if args.repository.endswith('.json'):
                # Load from JSON file
                with open(args.repository, 'r') as f:
                    repo_info = json.load(f)
            else:
                # Scan repository
                if not args.quiet:
                    print(f"Scanning repository: {args.repository}")
                scanner = RepositoryScanner(args.repository)
                repo_info = scanner.scan()
            
            # Export data
            if not args.quiet:
                print(f"Exporting data to: {args.output}")
                print(f"Format: {args.format}")
                if args.format == 'csv':
                    print(f"Report type: {args.report_type}")
            
            created_files = export_data(
                repo_info,
                args.output,
                format=args.format,
                report_type=args.report_type if args.format == 'csv' else 'all'
            )
            
            self.logger.info(f"Data exported successfully")
            if not args.quiet:
                print(f"\n✓ Data exported successfully!")
                print(f"\nCreated {len(created_files)} file(s):")
                for file_path in created_files:
                    print(f"  • {file_path}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Data export failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def health_command(self, args):
        """Execute health dashboard command."""
        from accudoc.health_dashboard import HealthDashboard
        from accudoc.scanner import RepositoryScanner
        import json
        
        self.logger.info(f"Generating health dashboard for: {args.repository}")
        
        try:
            # Load scan results or scan repository
            if args.repository.endswith('.json'):
                # Load from JSON file
                with open(args.repository, 'r') as f:
                    repo_info = json.load(f)
            else:
                # Scan repository
                if not args.quiet:
                    print(f"Scanning repository: {args.repository}")
                scanner = RepositoryScanner(args.repository)
                repo_info = scanner.scan()
            
            # Create dashboard
            dashboard = HealthDashboard(repo_info)
            
            if args.format == 'text':
                # Generate text dashboard
                output = dashboard.generate_text_dashboard()
                
                if args.output:
                    # Save to file
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(output)
                    if not args.quiet:
                        print(f"\n✓ Health dashboard saved to: {args.output}")
                else:
                    # Print to stdout
                    print(output)
            
            elif args.format == 'json':
                # Export to JSON
                data = dashboard.export_to_dict()
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    if not args.quiet:
                        print(f"\n✓ Health dashboard saved to: {args.output}")
                else:
                    print(json.dumps(data, indent=2))
            
            self.logger.info(f"Health dashboard generated successfully")
            return 0
            
        except Exception as e:
            self.logger.error(f"Health dashboard generation failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def trends_command(self, args):
        """Execute trend analysis command."""
        from accudoc.trend_analysis import TrendAnalyzer
        import json
        
        self.logger.info(f"Analyzing trends for: {args.repository}")
        
        try:
            # Create analyzer
            analyzer = TrendAnalyzer(args.repository)
            
            if not args.quiet:
                print(f"Analyzing trends over: {args.period}")
                print(f"Collecting {args.intervals} data points...")
            
            # Analyze trends
            trends = analyzer.analyze(period=args.period, intervals=args.intervals)
            
            if args.format == 'text':
                # Generate text report
                report = analyzer.generate_report()
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(report)
                    if not args.quiet:
                        print(f"\n✓ Trend report saved to: {args.output}")
                else:
                    print(report)
            
            elif args.format == 'json':
                # Export to JSON
                data = analyzer.export_to_json()
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    if not args.quiet:
                        print(f"\n✓ Trend data saved to: {args.output}")
                else:
                    print(json.dumps(data, indent=2))
            
            elif args.format == 'csv':
                # Export to CSV
                output_dir = args.output if args.output else './trends_export'
                created_files = analyzer.export_to_csv(output_dir)
                
                if not args.quiet:
                    print(f"\n✓ Trend data exported to CSV")
                    print(f"\nCreated {len(created_files)} file(s):")
                    for file_path in created_files:
                        print(f"  • {file_path}")
            
            self.logger.info(f"Trend analysis completed successfully")
            return 0
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def compare_command(self, args):
        """Execute comparison reports command."""
        from accudoc.comparison_reports import RepositoryComparison
        from accudoc.scanner import RepositoryScanner
        import json
        
        self.logger.info(f"Comparing {len(args.repositories)} repositories")
        
        try:
            comparison = RepositoryComparison()
            
            # Add repositories
            for i, repo_path in enumerate(args.repositories):
                if not args.quiet:
                    print(f"Loading repository {i+1}/{len(args.repositories)}: {repo_path}")
                
                # Check if it's a JSON file or directory
                if repo_path.endswith('.json'):
                    # Load from JSON
                    comparison.load_from_json(repo_path)
                else:
                    # Scan repository
                    scanner = RepositoryScanner(repo_path)
                    repo_info = scanner.scan()
                    
                    # Use custom name if provided
                    name = args.names[i] if args.names and i < len(args.names) else None
                    comparison.add_repository(repo_info, name)
            
            # Perform comparison
            if not args.quiet:
                print(f"\nComparing repositories...")
            
            comparison.compare()
            
            # Generate output
            if args.format == 'text':
                report = comparison.generate_report()
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(report)
                    if not args.quiet:
                        print(f"\n✓ Comparison report saved to: {args.output}")
                else:
                    print(report)
            
            elif args.format == 'json':
                data = comparison.export_to_json()
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    if not args.quiet:
                        print(f"\n✓ Comparison data saved to: {args.output}")
                else:
                    print(json.dumps(data, indent=2))
            
            elif args.format == 'csv':
                output_dir = args.output if args.output else './comparison_export'
                created_files = comparison.export_to_csv(output_dir)
                
                if not args.quiet:
                    print(f"\n✓ Comparison data exported to CSV")
                    print(f"\nCreated {len(created_files)} file(s):")
                    for file_path in created_files:
                        print(f"  • {file_path}")
            
            self.logger.info(f"Comparison completed successfully")
            return 0
            
        except Exception as e:
            self.logger.error(f"Comparison failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def dashboard_command(self, args):
        """Execute multi-repo documentation consistency dashboard command."""
        from accudoc.multi_repo_dashboard import MultiRepoDashboard, DashboardConfig
        from accudoc.scanner import RepositoryScanner
        from accudoc.membership import MembershipManager
        import json
        
        self.logger.info(f"Generating multi-repo dashboard for {len(args.repositories)} repositories")
        
        try:
            # Initialize dashboard configuration
            config = DashboardConfig(
                style_guide=args.style_guide,
                min_doc_coverage=args.min_coverage,
                min_completeness_score=args.min_completeness,
                check_consistency=not args.no_consistency,
                require_membership=args.require_auth
            )
            
            # Initialize membership manager if required
            membership_manager = None
            if args.require_auth:
                membership_manager = MembershipManager()
                
                # Check user access if user ID provided
                if args.user:
                    from accudoc.membership import Permission
                    if not dashboard.check_access(args.user, Permission.READ):
                        if not args.quiet:
                            print(f"\n✗ Error: User {args.user} does not have permission to access dashboard")
                        return 1
            
            # Create dashboard
            dashboard = MultiRepoDashboard(config, membership_manager)
            
            # Add repositories
            for i, repo_path in enumerate(args.repositories):
                if not args.quiet:
                    print(f"Analyzing repository {i+1}/{len(args.repositories)}: {repo_path}")
                
                # Check if it's a JSON file or directory
                if repo_path.endswith('.json'):
                    # Load from JSON
                    with open(repo_path, 'r', encoding='utf-8') as f:
                        repo_info = json.load(f)
                    
                    # Use custom name if provided
                    name = args.names[i] if args.names and i < len(args.names) else None
                    dashboard.add_repository(repo_info, name)
                else:
                    # Scan repository
                    scanner = RepositoryScanner(repo_path)
                    repo_info = scanner.scan()
                    
                    # Use custom name if provided
                    name = args.names[i] if args.names and i < len(args.names) else None
                    dashboard.add_repository(repo_info, name)
            
            # Analyze consistency
            if config.check_consistency:
                if not args.quiet:
                    print(f"\nAnalyzing consistency across repositories...")
                dashboard.analyze_consistency()
            
            # Generate analytics
            if not args.quiet:
                print(f"Generating organization-wide analytics...")
            dashboard.generate_analytics()
            
            # Generate output
            if args.format == 'json':
                data = dashboard.export_to_json()
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(data)
                    if not args.quiet:
                        print(f"\n✓ Dashboard data saved to: {args.output}")
                else:
                    print(data)
            
            elif args.format == 'html':
                report = dashboard.generate_report('html')
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(report)
                    if not args.quiet:
                        print(f"\n✓ Dashboard HTML saved to: {args.output}")
                else:
                    print(report)
            
            elif args.format == 'markdown':
                report = dashboard.generate_report('markdown')
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(report)
                    if not args.quiet:
                        print(f"\n✓ Dashboard markdown saved to: {args.output}")
                else:
                    print(report)
            
            else:  # text format (default)
                report = dashboard.generate_report('text')
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(report)
                    if not args.quiet:
                        print(f"\n✓ Dashboard report saved to: {args.output}")
                else:
                    print(report)
            
            self.logger.info(f"Multi-repo dashboard generated successfully")
            return 0
            
        except Exception as e:
            self.logger.error(f"Dashboard generation failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
                import traceback
                if args.verbose:
                    traceback.print_exc()
            return 1
    
    def custom_report_command(self, args):
        """Execute custom report generation command."""
        from accudoc.custom_reports import CustomReportGenerator, ReportTemplate, create_sample_template
        from accudoc.scanner import RepositoryScanner
        import json
        
        self.logger.info(f"Generating custom report for: {args.repository}")
        
        try:
            # Load or scan repository
            if args.repository.endswith('.json'):
                with open(args.repository, 'r') as f:
                    repo_info = json.load(f)
            else:
                if not args.quiet:
                    print(f"Scanning repository: {args.repository}")
                scanner = RepositoryScanner(args.repository)
                repo_info = scanner.scan()
            
            # Create generator
            generator = CustomReportGenerator(repo_info)
            
            # Handle listing templates
            if args.list:
                if not args.quiet:
                    print("\nAvailable built-in templates:")
                    print("-" * 60)
                templates = generator.list_builtin_templates()
                for tmpl in templates:
                    print(f"\n{tmpl['name']}: {tmpl['title']}")
                    print(f"  {tmpl['description']}")
                print()
                return 0
            
            # Handle sample template creation
            if args.create_sample:
                sample = create_sample_template(args.create_sample)
                output_file = args.output if args.output else f'{args.create_sample}_template.json'
                with open(output_file, 'w') as f:
                    json.dump(sample, f, indent=2)
                if not args.quiet:
                    print(f"\n✓ Sample template created: {output_file}")
                return 0
            
            # Load template
            if args.template:
                # Custom template file
                template = generator.load_template(args.template)
            elif args.builtin:
                # Built-in template
                template = generator.get_builtin_template(args.builtin)
            else:
                # Default to minimal
                template = generator.get_builtin_template('minimal')
            
            if not args.quiet:
                print(f"Using template: {template.name}")
            
            # Generate report
            report = generator.generate(template)
            
            # Output report
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(report)
                if not args.quiet:
                    print(f"\n✓ Custom report saved to: {args.output}")
            else:
                print(report)
            
            self.logger.info(f"Custom report generated successfully")
            return 0
            
        except Exception as e:
            self.logger.error(f"Custom report generation failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def api_server_command(self, args):
        """Execute API server command."""
        from accudoc.rest_api import is_flask_available, run_server
        
        self.logger.info(f"Starting API server on {args.host}:{args.port}")
        
        try:
            if not is_flask_available():
                if not args.quiet:
                    print("\n✗ Error: Flask is not installed", file=sys.stderr)
                    print("Install it with: pip install flask flask-cors", file=sys.stderr)
                return 1
            
            if not args.quiet:
                print(f"\nStarting AccuDoc REST API server...")
                print(f"Host: {args.host}")
                print(f"Port: {args.port}")
                print(f"Debug mode: {'enabled' if args.debug else 'disabled'}")
                print(f"\nAPI will be available at: http://{args.host}:{args.port}")
                print(f"API documentation: http://{args.host}:{args.port}/api/docs")
                print(f"\nPress Ctrl+C to stop the server\n")
            
            # Run server
            run_server(
                host=args.host,
                port=args.port,
                debug=args.debug
            )
            
            return 0
            
        except KeyboardInterrupt:
            if not args.quiet:
                print("\n\n✓ API server stopped")
            return 0
        except Exception as e:
            self.logger.error(f"API server failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
    
    def start_collab_server_command(self, args):
        """Execute start collaboration server command."""
        from collaboration_cli import start_collaboration_server
        
        self.logger.info("Starting collaboration server")
        return start_collaboration_server(args)
    
    def collab_status_command(self, args):
        """Execute collaboration status command."""
        from collaboration_cli import collaboration_status
        
        return collaboration_status(args)
    
    def stop_collab_server_command(self, args):
        """Execute stop collaboration server command."""
        from collaboration_cli import stop_collaboration_server
        
        return stop_collaboration_server(args)
    
    def manage_sessions_command(self, args):
        """Execute manage sessions command."""
        from collaboration_cli import manage_sessions
        
        return manage_sessions(args)
    
    def manage_comments_command(self, args):
        """Execute manage comments command."""
        from collaboration_cli import manage_comments
        
        return manage_comments(args)
    
    def manage_reviews_command(self, args):
        """Execute manage reviews command."""
        from collaboration_cli import manage_reviews
        
        return manage_reviews(args)
    
    def hooks_command(self, args):
        """Execute hooks command."""
        from accudoc.hooks_system import get_hooks_manager, HookPoint
        
        manager = get_hooks_manager()
        
        # List hooks
        if args.list:
            if not args.quiet:
                print("\n" + "=" * 70)
                print("REGISTERED HOOKS")
                print("=" * 70)
                print()
            
            for hook_point in HookPoint:
                hooks = manager.get_hooks(hook_point)
                if hooks or args.all:
                    if not args.quiet:
                        print(f"{hook_point.name} ({hook_point.value}):")
                    
                    if hooks:
                        for hook in hooks:
                            status = "✓ enabled" if hook.enabled else "✗ disabled"
                            if not args.quiet:
                                print(f"  • {hook.name} (priority: {hook.priority}) [{status}]")
                    else:
                        if not args.quiet:
                            print(f"  (no hooks registered)")
                    
                    if not args.quiet:
                        print()
            
            return 0
        
        # Enable/disable hooks
        if args.enable or args.disable:
            try:
                hook_point = HookPoint[args.hook_point.upper()]
                hook_name = args.hook_name
                
                if args.enable:
                    manager.enable_hook(hook_point, hook_name)
                    if not args.quiet:
                        print(f"\n✓ Enabled hook '{hook_name}' at {hook_point.value}")
                else:
                    manager.disable_hook(hook_point, hook_name)
                    if not args.quiet:
                        print(f"\n✓ Disabled hook '{hook_name}' at {hook_point.value}")
                
                return 0
            except KeyError:
                if not args.quiet:
                    print(f"\n✗ Error: Invalid hook point '{args.hook_point}'", file=sys.stderr)
                return 1
            except Exception as e:
                self.logger.error(f"Hook command failed: {str(e)}")
                if not args.quiet:
                    print(f"\n✗ Error: {str(e)}", file=sys.stderr)
                return 1
        
        # Show usage
        if not args.quiet:
            print("\nUsage: accudoc_cli.py hooks [--list] [--enable/--disable HOOK_POINT HOOK_NAME]")
            print("Run with --help for more information")
        
        return 0
    
    def collaborate_command(self, args):
        """Execute collaborative commands."""
        from accudoc.collaboration import CollaborationManager
        from accudoc.crdt import OperationType
        from accudoc.project_database import ProjectDatabase
        
        manager = CollaborationManager()
        db = ProjectDatabase()
        
        try:
            # Create session
            if args.collab_command == 'create':
                initial_content = ''
                if args.content and Path(args.content).exists():
                    with open(args.content, 'r') as f:
                        initial_content = f.read()
                
                session = manager.create_session(
                    project_id=args.project_id,
                    document_path=args.document,
                    created_by=args.user,
                    initial_content=initial_content
                )
                
                # Add to project database
                db.add_collaborative_session(
                    session_id=session.session_id,
                    project_id=args.project_id,
                    document_path=args.document,
                    created_by=args.user
                )
                
                if not args.quiet:
                    print(f"\n✓ Created collaborative session")
                    print(f"  Session ID: {session.session_id}")
                    print(f"  Document: {session.document_path}")
                    print(f"  Status: {session.status.value}")
                
                return 0
            
            # Join session
            elif args.collab_command == 'join':
                user_id = args.user_id or args.user
                result = manager.join_session(args.session_id, user_id, args.user)
                
                if result:
                    if not args.quiet:
                        print(f"\n✓ Joined session {args.session_id}")
                    return 0
                else:
                    if not args.quiet:
                        print(f"\n✗ Failed to join session", file=sys.stderr)
                    return 1
            
            # List sessions
            elif args.collab_command == 'list':
                sessions = db.get_project_collaborative_sessions(
                    args.project_id, 
                    status=args.status
                )
                
                if args.json:
                    print(json.dumps(sessions, indent=2, default=str))
                else:
                    if not args.quiet:
                        print(f"\n{'=' * 70}")
                        print(f"COLLABORATIVE SESSIONS - {args.project_id}")
                        print(f"{'=' * 70}\n")
                        
                        if sessions:
                            for session in sessions:
                                print(f"Session ID: {session['session_id']}")
                                print(f"  Document: {session['document_path']}")
                                print(f"  Created by: {session['created_by']}")
                                print(f"  Status: {session['status']}")
                                print(f"  Participants: {session['participant_count']}")
                                print(f"  Operations: {session['operation_count']}")
                                print(f"  Comments: {session['comment_count']}")
                                print()
                        else:
                            print("No sessions found.\n")
                
                return 0
            
            # Add comment
            elif args.collab_command == 'comment':
                user_id = args.user_id or args.user
                comment_id = manager.add_comment(
                    session_id=args.session_id,
                    user_id=user_id,
                    username=args.user,
                    content=args.content,
                    position=args.position
                )
                
                if not args.quiet:
                    print(f"\n✓ Added comment: {comment_id}")
                
                return 0
            
            # Add suggestion
            elif args.collab_command == 'suggest':
                user_id = args.user_id or args.user
                suggestion_id = manager.add_suggestion(
                    session_id=args.session_id,
                    user_id=user_id,
                    username=args.user,
                    position=args.position,
                    suggested_text=args.suggested_text,
                    original_text=args.original,
                    reason=args.reason
                )
                
                if not args.quiet:
                    print(f"\n✓ Added suggestion: {suggestion_id}")
                
                return 0
            
            else:
                if not args.quiet:
                    print("\nUse --help to see available collaborative commands")
                return 1
        
        except Exception as e:
            self.logger.error(f"Collaborative command failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
        finally:
            manager.close()
            db.close()
    
    def user_command(self, args):
        """Execute user management commands."""
        from accudoc.membership import MembershipManager, Role
        import getpass
        
        manager = MembershipManager()
        
        try:
            # Create user
            if args.user_command == 'create':
                password = args.password
                if not password:
                    password = getpass.getpass("Password: ")
                    confirm = getpass.getpass("Confirm password: ")
                    if password != confirm:
                        if not args.quiet:
                            print("\n✗ Passwords do not match", file=sys.stderr)
                        return 1
                
                user = manager.create_user(
                    username=args.username,
                    email=args.email,
                    password=password,
                    role=Role(args.role)
                )
                
                if not args.quiet:
                    print(f"\n✓ Created user")
                    print(f"  User ID: {user.user_id}")
                    print(f"  Username: {user.username}")
                    print(f"  Email: {user.email}")
                    print(f"  Role: {user.role.value}")
                
                return 0
            
            # Create team
            elif args.user_command == 'create-team':
                team = manager.create_team(
                    name=args.name,
                    owner_id=args.owner,
                    description=args.description
                )
                
                if not args.quiet:
                    print(f"\n✓ Created team")
                    print(f"  Team ID: {team.team_id}")
                    print(f"  Name: {team.name}")
                    print(f"  Owner: {team.owner_id}")
                
                return 0
            
            # Grant access
            elif args.user_command == 'grant':
                if not args.user and not args.team:
                    if not args.quiet:
                        print("\n✗ Must specify --user or --team", file=sys.stderr)
                    return 1
                
                manager.grant_project_access(
                    project_id=args.project_id,
                    granted_by=args.granted_by,
                    user_id=args.user,
                    team_id=args.team,
                    role=Role(args.role)
                )
                
                target = args.user or args.team
                target_type = "user" if args.user else "team"
                
                if not args.quiet:
                    print(f"\n✓ Granted {args.role} access")
                    print(f"  Project: {args.project_id}")
                    print(f"  {target_type.capitalize()}: {target}")
                
                return 0
            
            else:
                if not args.quiet:
                    print("\nUse --help to see available user commands")
                return 1
        
        except Exception as e:
            self.logger.error(f"User command failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
        finally:
            manager.close()
    
    def archive_command(self, args):
        """Execute archive management commands."""
        from accudoc.archive import ArchiveManager, ArchiveFormat
        from accudoc.project_database import ProjectDatabase
        from accudoc.audit import get_audit_logger
        from accudoc.membership import MembershipManager
        import json
        import os
        
        # Initialize components
        db = ProjectDatabase()
        audit_logger = get_audit_logger()
        membership = MembershipManager() if args.use_auth else None
        archive_mgr = ArchiveManager(db, audit_logger, membership)
        
        try:
            # Create archive
            if args.archive_command == 'create':
                # Get or create project
                project = db.get_project_by_path(args.repository)
                if not project:
                    project_id = db.add_project(args.repository, args.project_name)
                else:
                    project_id = project['project_id']
                
                # Determine format
                doc_path = Path(args.document)
                if not doc_path.exists():
                    if not args.quiet:
                        print(f"\n✗ Document not found: {args.document}", file=sys.stderr)
                    return 1
                
                ext = doc_path.suffix.lower()
                if args.format:
                    format = ArchiveFormat(args.format)
                elif ext == '.md':
                    format = ArchiveFormat.MARKDOWN
                elif ext == '.html':
                    format = ArchiveFormat.HTML
                elif ext == '.pdf':
                    format = ArchiveFormat.PDF
                else:
                    format = ArchiveFormat.MARKDOWN
                
                # Create archive
                user_id = args.user or os.getenv('USER') or 'unknown'
                tags = args.tags.split(',') if args.tags else []
                
                if not args.quiet:
                    print(f"\nCreating archive...")
                    print(f"  Project: {project_id}")
                    print(f"  Document: {doc_path.name}")
                    print(f"  Format: {format.value}")
                
                archive_id = archive_mgr.create_archive(
                    project_id=project_id,
                    document_path=doc_path,
                    format=format,
                    created_by=user_id,
                    tags=tags,
                    description=args.description
                )
                
                if not args.quiet:
                    print(f"\n✓ Archive created successfully")
                    print(f"  Archive ID: {archive_id}")
                
                if args.json:
                    print(json.dumps({'archive_id': archive_id, 'project_id': project_id}, indent=2))
                
                return 0
            
            # List archives
            elif args.archive_command == 'list':
                project_id = None
                if args.repository:
                    project = db.get_project_by_path(args.repository)
                    project_id = project['project_id'] if project else None
                
                format = ArchiveFormat(args.format) if args.format else None
                tags = args.tags.split(',') if args.tags else None
                
                archives = archive_mgr.list_archives(
                    project_id=project_id,
                    tags=tags,
                    format=format,
                    limit=args.limit
                )
                
                if args.json:
                    archive_list = [
                        {
                            'archive_id': a.archive_id,
                            'project_id': a.project_id,
                            'document_name': a.document_name,
                            'format': a.format,
                            'created_at': a.created_at,
                            'created_by': a.created_by,
                            'size_bytes': a.size_bytes,
                            'tags': a.tags,
                            'description': a.description
                        }
                        for a in archives
                    ]
                    print(json.dumps(archive_list, indent=2))
                else:
                    if not args.quiet:
                        print(f"\n{'=' * 70}")
                        print(f"DOCUMENTATION ARCHIVES")
                        if project_id:
                            print(f"Project: {project_id}")
                        print(f"{'=' * 70}\n")
                        
                        if archives:
                            for i, archive in enumerate(archives, 1):
                                print(f"{i}. {archive.document_name}")
                                print(f"   Archive ID: {archive.archive_id}")
                                print(f"   Format: {archive.format}")
                                print(f"   Created: {archive.created_at}")
                                print(f"   By: {archive.created_by}")
                                print(f"   Size: {archive.size_bytes:,} bytes")
                                if archive.tags:
                                    print(f"   Tags: {', '.join(archive.tags)}")
                                if archive.description:
                                    print(f"   Description: {archive.description}")
                                print()
                        else:
                            print("No archives found.\n")
                
                return 0
            
            # Retrieve archive
            elif args.archive_command == 'retrieve':
                user_id = args.user or os.getenv('USER') or 'unknown'
                
                if not args.quiet:
                    print(f"\nRetrieving archive: {args.archive_id}")
                
                content, metadata = archive_mgr.retrieve_archive(
                    args.archive_id,
                    user_id,
                    validate=not args.no_validate
                )
                
                # Save to file
                output_path = Path(args.output) if args.output else Path(metadata.document_name)
                with open(output_path, 'wb') as f:
                    f.write(content)
                
                if not args.quiet:
                    print(f"\n✓ Archive retrieved successfully")
                    print(f"  Document: {metadata.document_name}")
                    print(f"  Format: {metadata.format}")
                    print(f"  Size: {metadata.size_bytes:,} bytes")
                    print(f"  Saved to: {output_path}")
                    if not args.no_validate:
                        print(f"  ✓ Signature validated")
                
                return 0
            
            # Validate archive
            elif args.archive_command == 'validate':
                if not args.quiet:
                    print(f"\nValidating archive: {args.archive_id}")
                
                is_valid = archive_mgr.validate_archive(args.archive_id)
                
                if is_valid:
                    if not args.quiet:
                        print(f"\n✓ Archive is valid")
                        print(f"  Signature: VERIFIED")
                        print(f"  Content integrity: OK")
                    return 0
                else:
                    if not args.quiet:
                        print(f"\n✗ Archive validation failed", file=sys.stderr)
                        print(f"  Signature: INVALID", file=sys.stderr)
                        print(f"  Content may have been tampered with!", file=sys.stderr)
                    return 1
            
            # Delete archive
            elif args.archive_command == 'delete':
                user_id = args.user or os.getenv('USER') or 'unknown'
                
                if not args.quiet and not args.yes:
                    confirm = input(f"\nAre you sure you want to delete archive {args.archive_id}? (yes/no): ")
                    if confirm.lower() not in ['yes', 'y']:
                        print("Cancelled.")
                        return 0
                
                archive_mgr.delete_archive(args.archive_id, user_id)
                
                if not args.quiet:
                    print(f"\n✓ Archive deleted: {args.archive_id}")
                
                return 0
            
            # Archive statistics
            elif args.archive_command == 'stats':
                project_id = None
                if args.repository:
                    project = db.get_project_by_path(args.repository)
                    project_id = project['project_id'] if project else None
                
                stats = archive_mgr.get_archive_statistics(project_id=project_id)
                
                if args.json:
                    print(json.dumps(stats, indent=2))
                else:
                    if not args.quiet:
                        print(f"\n{'=' * 60}")
                        print(f"ARCHIVE STATISTICS")
                        if project_id:
                            print(f"Project: {project_id}")
                        print(f"{'=' * 60}\n")
                        print(f"Total archives: {stats['total_archives']}")
                        print(f"Total size: {stats['total_size_bytes']:,} bytes")
                        print(f"Compressed size: {stats['total_compressed_bytes']:,} bytes")
                        print(f"Compression ratio: {stats['compression_ratio']:.2%}")
                        print(f"\nBy format:")
                        for fmt, count in stats['by_format'].items():
                            print(f"  {fmt}: {count}")
                        if stats['oldest_archive']:
                            print(f"\nOldest archive: {stats['oldest_archive']}")
                        if stats['newest_archive']:
                            print(f"Newest archive: {stats['newest_archive']}")
                        print()
                
                return 0
            
            else:
                if not args.quiet:
                    print("\nUse --help to see available archive commands")
                return 1
        
        except Exception as e:
            self.logger.error(f"Archive command failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
                import traceback
                if args.verbose:
                    traceback.print_exc()
            return 1
        finally:
            if membership:
                membership.close()
            db.close()
    
    def compliance_command(self, args):
        """Execute compliance mapping commands."""
        from accudoc.compliance_mapping import (
            ComplianceMappingManager, ComplianceFramework, 
            CoverageStatus, ComplianceFrameworkRegistry
        )
        from accudoc.project_database import ProjectDatabase
        from accudoc.membership import MembershipManager, Permission
        import json
        
        # Initialize components
        db = ProjectDatabase()
        use_auth = getattr(args, 'use_auth', False)
        membership = MembershipManager() if use_auth else None
        compliance_mgr = ComplianceMappingManager(db, membership)
        
        try:
            # Map documentation to requirements
            if args.compliance_command == 'map':
                # Get or create project
                project = db.get_project_by_path(args.repository)
                if not project:
                    project_id = db.add_project(args.repository, args.project_name)
                else:
                    project_id = project['project_id']
                
                # Check permissions if authentication is enabled
                if membership and args.user:
                    if not membership.check_project_permission(args.user, project_id, Permission.WRITE):
                        if not args.quiet:
                            print(f"\n✗ Permission denied: User {args.user} does not have write access", file=sys.stderr)
                        return 1
                
                framework = ComplianceFramework(args.framework)
                coverage_status = CoverageStatus(args.status) if args.status else CoverageStatus.COVERED
                
                mapping_id = compliance_mgr.create_mapping(
                    project_id=project_id,
                    requirement_id=args.requirement_id,
                    framework=framework,
                    doc_section=args.doc_section,
                    doc_path=args.doc_path,
                    coverage_status=coverage_status,
                    notes=args.notes,
                    evidence=args.evidence.split(',') if args.evidence else None,
                    created_by=args.user or 'system'
                )
                
                if not args.quiet:
                    print(f"\n✓ Created compliance mapping")
                    print(f"  Mapping ID: {mapping_id}")
                    print(f"  Framework: {framework.value}")
                    print(f"  Requirement: {args.requirement_id}")
                    print(f"  Documentation: {args.doc_section}")
                
                return 0
            
            # List mappings
            elif args.compliance_command == 'list':
                project = db.get_project_by_path(args.repository)
                if not project:
                    if not args.quiet:
                        print(f"\n✗ Project not found: {args.repository}", file=sys.stderr)
                    return 1
                
                project_id = project['project_id']
                framework = ComplianceFramework(args.framework) if args.framework else None
                
                mappings = compliance_mgr.get_mappings(project_id, framework)
                
                if args.json:
                    mapping_list = [
                        {
                            'mapping_id': m.mapping_id,
                            'requirement_id': m.requirement_id,
                            'framework': m.framework.value,
                            'doc_section': m.doc_section,
                            'coverage_status': m.coverage_status.value,
                            'created_at': m.created_at
                        }
                        for m in mappings
                    ]
                    print(json.dumps(mapping_list, indent=2))
                else:
                    if not args.quiet:
                        print(f"\n{'=' * 70}")
                        print(f"COMPLIANCE MAPPINGS")
                        if framework:
                            print(f"Framework: {framework.value.upper()}")
                        print(f"{'=' * 70}\n")
                        
                        if mappings:
                            for i, mapping in enumerate(mappings, 1):
                                print(f"{i}. {mapping.requirement_id}")
                                print(f"   Framework: {mapping.framework.value}")
                                print(f"   Documentation: {mapping.doc_section}")
                                print(f"   Status: {mapping.coverage_status.value}")
                                print(f"   Created: {mapping.created_at}")
                                if mapping.notes:
                                    print(f"   Notes: {mapping.notes}")
                                print()
                        else:
                            print("No mappings found.")
                        print()
                
                return 0
            
            # Perform gap analysis
            elif args.compliance_command == 'analyze':
                project = db.get_project_by_path(args.repository)
                if not project:
                    if not args.quiet:
                        print(f"\n✗ Project not found: {args.repository}", file=sys.stderr)
                    return 1
                
                project_id = project['project_id']
                framework = ComplianceFramework(args.framework)
                
                if not args.quiet:
                    print(f"\nAnalyzing compliance gaps for {framework.value.upper()}...")
                
                gaps = compliance_mgr.analyze_gaps(project_id, framework)
                
                if args.json:
                    gap_list = [
                        {
                            'gap_id': g.gap_id,
                            'requirement_id': g.requirement_id,
                            'category': g.category,
                            'title': g.title,
                            'severity': g.severity.value,
                            'status': g.current_status.value,
                            'recommendations': g.recommendations
                        }
                        for g in gaps
                    ]
                    print(json.dumps(gap_list, indent=2))
                else:
                    if not args.quiet:
                        print(f"\n{'=' * 70}")
                        print(f"COMPLIANCE GAPS: {framework.value.upper()}")
                        print(f"{'=' * 70}\n")
                        
                        if gaps:
                            critical = sum(1 for g in gaps if g.severity.value == 'critical')
                            high = sum(1 for g in gaps if g.severity.value == 'high')
                            medium = sum(1 for g in gaps if g.severity.value == 'medium')
                            low = sum(1 for g in gaps if g.severity.value == 'low')
                            
                            print(f"Total gaps: {len(gaps)}")
                            print(f"  Critical: {critical}")
                            print(f"  High: {high}")
                            print(f"  Medium: {medium}")
                            print(f"  Low: {low}\n")
                            
                            for i, gap in enumerate(gaps, 1):
                                print(f"{i}. {gap.requirement_id}: {gap.title}")
                                print(f"   Category: {gap.category}")
                                print(f"   Severity: {gap.severity.value.upper()}")
                                print(f"   Status: {gap.current_status.value}")
                                if gap.recommendations:
                                    print(f"   Recommendations:")
                                    for rec in gap.recommendations:
                                        print(f"     - {rec}")
                                print()
                        else:
                            print("✓ No compliance gaps found!")
                        print()
                
                return 0
            
            # Generate compliance report
            elif args.compliance_command == 'report':
                project = db.get_project_by_path(args.repository)
                if not project:
                    if not args.quiet:
                        print(f"\n✗ Project not found: {args.repository}", file=sys.stderr)
                    return 1
                
                project_id = project['project_id']
                framework = ComplianceFramework(args.framework)
                
                if not args.quiet:
                    print(f"\nGenerating compliance report for {framework.value.upper()}...")
                
                report = compliance_mgr.generate_report(project_id, framework)
                report_content = compliance_mgr.export_report(report, args.format)
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(report_content)
                    if not args.quiet:
                        print(f"\n✓ Compliance report saved to: {args.output}")
                else:
                    print(report_content)
                
                return 0
            
            # List available frameworks and requirements
            elif args.compliance_command == 'frameworks':
                registry = ComplianceFrameworkRegistry()
                
                if args.framework:
                    framework = ComplianceFramework(args.framework)
                    requirements = registry.get_requirements(framework)
                    
                    if args.json:
                        req_list = [
                            {
                                'requirement_id': r.requirement_id,
                                'category': r.category,
                                'title': r.title,
                                'description': r.description,
                                'mandatory': r.mandatory,
                                'control_objectives': r.control_objectives
                            }
                            for r in requirements
                        ]
                        print(json.dumps(req_list, indent=2))
                    else:
                        if not args.quiet:
                            print(f"\n{'=' * 70}")
                            print(f"FRAMEWORK: {framework.value.upper()}")
                            print(f"{'=' * 70}\n")
                            print(f"Total requirements: {len(requirements)}\n")
                            
                            for i, req in enumerate(requirements, 1):
                                print(f"{i}. {req.requirement_id}: {req.title}")
                                print(f"   Category: {req.category}")
                                print(f"   Mandatory: {'Yes' if req.mandatory else 'No'}")
                                if req.control_objectives:
                                    print(f"   Control Objectives:")
                                    for obj in req.control_objectives:
                                        print(f"     - {obj}")
                                print()
                else:
                    if not args.quiet:
                        print(f"\n{'=' * 70}")
                        print(f"AVAILABLE COMPLIANCE FRAMEWORKS")
                        print(f"{'=' * 70}\n")
                        
                        for framework in ComplianceFramework:
                            requirements = registry.get_requirements(framework)
                            print(f"• {framework.value.upper()}")
                            print(f"  Requirements: {len(requirements)}")
                            print()
                
                return 0
            
            else:
                if not args.quiet:
                    print("\nUse --help to see available compliance commands")
                return 1
        
        except Exception as e:
            self.logger.error(f"Compliance command failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
                import traceback
                if args.verbose:
                    traceback.print_exc()
            return 1
        finally:
            if membership:
                membership.close()
            db.close()
    
    def onboarding_command(self, args):
        """Execute onboarding command."""
        from accudoc.onboarding_generator import OnboardingGenerator
        from accudoc.membership import MembershipManager
        
        try:
            # Initialize managers
            membership = None
            if hasattr(args, 'user') and args.user:
                membership = MembershipManager()
            
            generator = OnboardingGenerator(membership_manager=membership)
            
            if args.onboarding_command == 'create':
                if not args.quiet:
                    print(f"\nCreating onboarding checklist for: {args.repository}")
                
                # Scan repository
                scanner = RepositoryScanner(args.repository)
                repo_info = scanner.scan()
                
                # Create checklist
                checklist = generator.create_checklist(
                    repository_path=args.repository,
                    repo_info=repo_info,
                    title=args.title,
                    organization_id=args.org_id,
                    user_id=getattr(args, 'user', None)
                )
                
                # Generate output based on format
                if args.format == 'markdown':
                    content = generator.generate_markdown_guide(checklist)
                elif args.format == 'checklist':
                    content = generator.generate_interactive_checklist(checklist)
                else:  # json
                    content = json.dumps({
                        'checklist_id': checklist.checklist_id,
                        'title': checklist.title,
                        'description': checklist.description,
                        'total_time': checklist.total_time,
                        'total_steps': len(checklist.steps) if checklist.steps else 0,
                        'steps': [{
                            'step_id': s.step_id,
                            'title': s.title,
                            'description': s.description,
                            'category': s.category,
                            'required': s.required,
                            'estimated_time': s.estimated_time,
                            'commands': s.commands,
                            'resources': s.resources
                        } for s in (checklist.steps or [])]
                    }, indent=2)
                
                if args.output:
                    output_path = Path(args.output)
                    output_path.write_text(content, encoding='utf-8')
                    if not args.quiet:
                        print(f"\n✓ Onboarding guide saved to: {output_path}")
                        print(f"  Checklist ID: {checklist.checklist_id}")
                        print(f"  Total Steps: {len(checklist.steps) if checklist.steps else 0}")
                        if checklist.total_time:
                            hours = checklist.total_time // 60
                            minutes = checklist.total_time % 60
                            print(f"  Estimated Time: {hours}h {minutes}m")
                else:
                    print(content)
                
                return 0
            
            elif args.onboarding_command == 'get':
                checklist = generator.get_checklist(args.checklist_id)
                
                if not checklist:
                    if not args.quiet:
                        print(f"\n✗ Checklist not found: {args.checklist_id}", file=sys.stderr)
                    return 1
                
                # Generate output based on format
                if args.format == 'markdown':
                    content = generator.generate_markdown_guide(checklist)
                elif args.format == 'checklist':
                    content = generator.generate_interactive_checklist(checklist)
                else:  # json
                    content = json.dumps({
                        'checklist_id': checklist.checklist_id,
                        'title': checklist.title,
                        'description': checklist.description,
                        'total_time': checklist.total_time,
                        'steps': [{
                            'step_id': s.step_id,
                            'title': s.title,
                            'description': s.description,
                            'category': s.category
                        } for s in (checklist.steps or [])]
                    }, indent=2)
                
                if args.output:
                    Path(args.output).write_text(content, encoding='utf-8')
                    if not args.quiet:
                        print(f"\n✓ Checklist saved to: {args.output}")
                else:
                    print(content)
                
                return 0
            
            elif args.onboarding_command == 'assign':
                progress = generator.assign_checklist(args.checklist_id, args.user_id)
                
                if not args.quiet:
                    print(f"\n✓ Checklist assigned to user: {args.user_id}")
                    print(f"  Progress ID: {progress.progress_id}")
                
                return 0
            
            elif args.onboarding_command == 'progress':
                updated = generator.update_progress(args.progress_id, args.step_id)
                
                if not args.quiet:
                    print(f"\n✓ Progress updated")
                    print(f"  Completion: {updated.progress_percentage:.1f}%")
                    if updated.completed_at:
                        print(f"  Status: Completed ✓")
                
                return 0
            
            else:
                if not args.quiet:
                    print("\nUse --help to see available onboarding commands")
                return 1
        
        except Exception as e:
            self.logger.error(f"Onboarding command failed: {str(e)}")
            if not args.quiet:
                print(f"\n✗ Error: {str(e)}", file=sys.stderr)
            return 1
        finally:
            generator.close()
            if membership:
                membership.close()
    
    def run(self):
        """Run the CLI application."""
        parser = argparse.ArgumentParser(
            description='AccuDoc - Automated Repository Documentation Generator',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Quick export (scan + generate in one command)
  %(prog)s export https://github.com/user/repo -o docs.md
  
  # Scan and save results
  %(prog)s scan https://github.com/user/repo -o scan.json
  
  # Generate from existing scan
  %(prog)s generate scan.json -o docs.html --format html --theme dark
  
  # Batch process multiple repositories
  %(prog)s batch repos.json
  
  # Get information about available options
  %(prog)s info
            """
        )
        
        # Global options
        parser.add_argument('-v', '--verbose', action='count', default=0,
                          help='Increase verbosity (can be used multiple times)')
        parser.add_argument('-q', '--quiet', action='store_true',
                          help='Suppress output messages')
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Scan command
        scan_parser = subparsers.add_parser('scan', help='Scan a repository')
        scan_parser.add_argument('repository', help='Repository URL or local path')
        scan_parser.add_argument('-o', '--output', help='Save scan results to JSON file')
        scan_parser.add_argument('--json', action='store_true',
                               help='Output results as JSON to stdout')
        scan_parser.add_argument('--no-cache', action='store_true',
                               help='Disable caching for this scan')
        
        # Generate command
        gen_parser = subparsers.add_parser('generate', help='Generate documentation from scan results')
        gen_parser.add_argument('scan_file', help='JSON file with scan results')
        gen_parser.add_argument('-o', '--output', required=True,
                              help='Output file path')
        gen_parser.add_argument('-t', '--template', default='default',
                              choices=['default', 'minimal', 'detailed', 'api', 'readme', 'student'],
                              help='Documentation template (default: default)')
        gen_parser.add_argument('-f', '--format', default='markdown',
                              choices=['markdown', 'html', 'txt', 'pdf'],
                              help='Output format (default: markdown)')
        gen_parser.add_argument('--theme', default='default',
                              choices=['default', 'dark', 'minimal', 'corporate'],
                              help='Theme for HTML output (default: default)')
        gen_parser.add_argument('--markdown-flavor', default='github',
                              choices=['github', 'gitlab', 'commonmark'],
                              help='Markdown flavor (default: github)')
        gen_parser.add_argument('-l', '--language', default='en',
                              choices=['en', 'es', 'fr', 'de', 'zh', 'ja', 'ar'],
                              help='Documentation language (default: en)')
        
        # Export command (combined scan + generate)
        export_parser = subparsers.add_parser('export', 
                                             help='Scan and generate documentation in one step')
        export_parser.add_argument('repository', help='Repository URL or local path')
        export_parser.add_argument('-o', '--output', required=True,
                                 help='Output file path')
        export_parser.add_argument('-t', '--template', default='default',
                                 choices=['default', 'minimal', 'detailed', 'api', 'readme', 'student'],
                                 help='Documentation template (default: default)')
        export_parser.add_argument('-f', '--format', default='markdown',
                                 choices=['markdown', 'html', 'txt', 'pdf'],
                                 help='Output format (default: markdown)')
        export_parser.add_argument('--theme', default='default',
                                 choices=['default', 'dark', 'minimal', 'corporate'],
                                 help='Theme for HTML output (default: default)')
        export_parser.add_argument('--markdown-flavor', default='github',
                                 choices=['github', 'gitlab', 'commonmark'],
                                 help='Markdown flavor (default: github)')
        export_parser.add_argument('-l', '--language', default='en',
                                 choices=['en', 'es', 'fr', 'de', 'zh', 'ja', 'ar'],
                                 help='Documentation language (default: en)')
        export_parser.add_argument('--no-cache', action='store_true',
                                 help='Disable caching for this scan')
        
        # Info command
        subparsers.add_parser('info', help='Display information about AccuDoc')
        
        # Cache command
        cache_parser = subparsers.add_parser('cache', help='Manage cache')
        cache_parser.add_argument('cache_action', choices=['stats', 'clear'],
                                help='Cache action to perform')
        cache_parser.add_argument('repository', help='Repository path')
        
        # Link checker command
        link_parser = subparsers.add_parser('check-links', help='Check links in documentation')
        link_parser.add_argument('path', help='File or directory to check')
        link_parser.add_argument('-o', '--output', help='Save report to file')
        link_parser.add_argument('-f', '--format', default='text',
                               choices=['text', 'markdown', 'json'],
                               help='Report format (default: text)')
        
        # Plugins command
        plugins_parser = subparsers.add_parser('plugins', help='Manage plugins')
        plugins_parser.add_argument('plugin_action', choices=['list', 'info'],
                                  help='Plugin action to perform')
        
        # Static site command
        site_parser = subparsers.add_parser('site', help='Generate static documentation website')
        site_parser.add_argument('repository', help='Repository URL or local path')
        site_parser.add_argument('-o', '--output', required=True,
                                help='Output directory for website')
        site_parser.add_argument('--title', help='Site title (defaults to repo name)')
        site_parser.add_argument('--theme', default='default',
                                choices=['default', 'dark'],
                                help='Site theme (default: default)')
        site_parser.add_argument('--no-cache', action='store_true',
                                help='Disable caching for this scan')
        
        # Batch command
        batch_parser = subparsers.add_parser('batch', help='Process multiple repositories')
        batch_parser.add_argument('batch_file', help='JSON file with batch configuration')
        
        # Branch comparison command
        branch_parser = subparsers.add_parser('branch-compare', 
                                              help='Compare two branches')
        branch_parser.add_argument('repository', help='Repository path')
        branch_parser.add_argument('-b', '--base', help='Base branch name')
        branch_parser.add_argument('-c', '--compare', help='Branch to compare')
        branch_parser.add_argument('-l', '--list-branches', action='store_true',
                                  help='List available branches')
        branch_parser.add_argument('-o', '--output', help='Save report to file')
        branch_parser.add_argument('-f', '--format', default='markdown',
                                  choices=['markdown', 'json'],
                                  help='Output format (default: markdown)')
        
        # Version checking command
        version_parser = subparsers.add_parser('version-check',
                                              help='Check dependency versions')
        version_parser.add_argument('repository', help='Repository path')
        version_parser.add_argument('-o', '--output', help='Save report to file')
        version_parser.add_argument('-f', '--format', default='markdown',
                                   choices=['markdown', 'json'],
                                   help='Output format (default: markdown)')
        
        # Spell checking command
        spell_parser = subparsers.add_parser('spellcheck',
                                            help='Check documentation spelling')
        spell_parser.add_argument('path', help='File or directory to check')
        spell_parser.add_argument('-o', '--output', help='Save report to file')
        spell_parser.add_argument('-f', '--format', default='markdown',
                                 choices=['markdown', 'json'],
                                 help='Output format (default: markdown)')
        spell_parser.add_argument('-e', '--extensions',
                                 help='File extensions to check (comma-separated, e.g., .md,.txt)')
        
        # Multi-repository command
        multi_repo_parser = subparsers.add_parser('multi-repo',
                                                  help='Scan multiple repositories')
        multi_repo_parser.add_argument('config', help='JSON configuration file')
        multi_repo_parser.add_argument('-o', '--output', help='Save report to file')
        multi_repo_parser.add_argument('-f', '--format', default='markdown',
                                      choices=['markdown', 'json', 'comparison'],
                                      help='Output format (default: markdown)')
        multi_repo_parser.add_argument('-w', '--workers', type=int, default=4,
                                      help='Number of parallel workers (default: 4)')
        
        # Test coverage command
        coverage_parser = subparsers.add_parser('coverage',
                                               help='Analyze test coverage')
        coverage_parser.add_argument('repository', help='Repository path')
        coverage_parser.add_argument('-o', '--output', help='Save report to file')
        coverage_parser.add_argument('-f', '--format', default='markdown',
                                    choices=['markdown', 'json'],
                                    help='Output format (default: markdown)')
        
        # Readability analysis command
        readability_parser = subparsers.add_parser('readability',
                                                   help='Analyze documentation readability')
        readability_parser.add_argument('path', help='File or directory to analyze')
        readability_parser.add_argument('-o', '--output', help='Save report to file')
        readability_parser.add_argument('-f', '--format', default='markdown',
                                       choices=['markdown', 'json'],
                                       help='Output format (default: markdown)')
        readability_parser.add_argument('-e', '--extensions',
                                       help='File extensions to analyze (comma-separated, e.g., .md,.txt)')
        
        # Database schema command
        db_schema_parser = subparsers.add_parser('db-schema',
                                                help='Extract database schema')
        db_schema_parser.add_argument('repository', help='Repository path')
        db_schema_parser.add_argument('-o', '--output', help='Save documentation to file')
        db_schema_parser.add_argument('-f', '--format', default='markdown',
                                     choices=['markdown', 'json'],
                                     help='Output format (default: markdown)')
        
        # Monorepo analysis command
        monorepo_parser = subparsers.add_parser('monorepo',
                                               help='Analyze monorepo structure')
        monorepo_parser.add_argument('repository', help='Repository path')
        monorepo_parser.add_argument('-o', '--output', help='Save documentation to file')
        monorepo_parser.add_argument('-f', '--format', default='markdown',
                                    choices=['markdown', 'json'],
                                    help='Output format (default: markdown)')
        
        # Breaking changes detection command
        breaking_parser = subparsers.add_parser('breaking-changes',
                                               help='Detect breaking changes between versions')
        breaking_parser.add_argument('repository', help='Repository path')
        breaking_parser.add_argument('from_ref', help='Starting reference (tag, branch, commit)')
        breaking_parser.add_argument('to_ref', help='Ending reference')
        breaking_parser.add_argument('--from-version', help='Starting version (for semver check)')
        breaking_parser.add_argument('--to-version', help='Ending version (for semver check)')
        breaking_parser.add_argument('-o', '--output', help='Save report to file')
        breaking_parser.add_argument('-f', '--format', default='markdown',
                                    choices=['markdown', 'json'],
                                    help='Output format (default: markdown)')
        
        # Code quality analysis command
        quality_parser = subparsers.add_parser('code-quality',
                                              help='Analyze code quality metrics')
        quality_parser.add_argument('repository', help='Repository path')
        quality_parser.add_argument('-o', '--output', help='Save report to file')
        quality_parser.add_argument('-f', '--format', default='markdown',
                                   choices=['markdown', 'json'],
                                   help='Output format (default: markdown)')
        
        # Grammar checking command
        grammar_parser = subparsers.add_parser('grammar',
                                              help='Check documentation grammar')
        grammar_parser.add_argument('path', help='File or directory to check')
        grammar_parser.add_argument('-o', '--output', help='Save report to file')
        grammar_parser.add_argument('-f', '--format', default='markdown',
                                   choices=['markdown', 'json'],
                                   help='Output format (default: markdown)')
        grammar_parser.add_argument('-e', '--extensions',
                                   help='File extensions to check (comma-separated, e.g., .md,.txt)')
        
        # Documentation coverage command
        doc_coverage_parser = subparsers.add_parser('doc-coverage',
                                                   help='Analyze documentation coverage')
        doc_coverage_parser.add_argument('repository', help='Repository path')
        doc_coverage_parser.add_argument('-o', '--output', help='Save report to file')
        doc_coverage_parser.add_argument('-f', '--format', default='markdown',
                                        choices=['markdown', 'json'],
                                        help='Output format (default: markdown)')
        
        # Data flow analysis command
        dataflow_parser = subparsers.add_parser('dataflow',
                                               help='Analyze data flow in code')
        dataflow_parser.add_argument('repository', help='Repository path or Python file')
        dataflow_parser.add_argument('-o', '--output', help='Save report to file')
        dataflow_parser.add_argument('-f', '--format', default='markdown',
                                    choices=['markdown', 'json'],
                                    help='Output format (default: markdown)')
        dataflow_parser.add_argument('--no-diagrams', action='store_true',
                                    help='Exclude Mermaid diagrams from report')
        
        # Configuration management command
        config_parser = subparsers.add_parser('config',
                                             help='Manage configuration files')
        config_parser.add_argument('config_action',
                                  choices=['init', 'show', 'validate'],
                                  help='Config action: init (create example), show (display), validate (check)')
        config_parser.add_argument('-c', '--config', help='Config file path')
        config_parser.add_argument('-o', '--output', help='Output file for init command')
        config_parser.add_argument('-f', '--format', choices=['yaml', 'json'],
                                  help='Config format for init command (default: yaml)')
        
        # Open source documentation command
        opensource_parser = subparsers.add_parser('opensource',
                                                 help='Generate open source project documentation')
        opensource_parser.add_argument('repository', help='Repository path')
        opensource_parser.add_argument('-o', '--output-dir', default='.',
                                     help='Output directory for generated files (default: current directory)')
        opensource_parser.add_argument('--contributing', action='store_true',
                                     help='Generate CONTRIBUTING.md only')
        opensource_parser.add_argument('--conduct', action='store_true',
                                     help='Generate CODE_OF_CONDUCT.md only')
        opensource_parser.add_argument('--issues', action='store_true',
                                     help='Generate issue templates only')
        opensource_parser.add_argument('--all', action='store_true',
                                     help='Generate all templates (default if no specific option given)')
        
        # Data export command
        data_export_parser = subparsers.add_parser('data-export',
                                                   help='Export repository data to CSV/JSON')
        data_export_parser.add_argument('repository', help='Repository path or scan JSON file')
        data_export_parser.add_argument('-o', '--output', required=True,
                                       help='Output path (directory for CSV, file for JSON/summary)')
        data_export_parser.add_argument('-f', '--format', default='csv',
                                       choices=['csv', 'json', 'summary'],
                                       help='Export format (default: csv)')
        data_export_parser.add_argument('-r', '--report-type', default='all',
                                       choices=['all', 'files', 'dependencies', 'todos', 'metrics', 'languages'],
                                       help='Type of CSV report to generate (default: all)')
        
        # Health dashboard command
        health_parser = subparsers.add_parser('health',
                                             help='Generate project health dashboard')
        health_parser.add_argument('repository', help='Repository path or scan JSON file')
        health_parser.add_argument('-o', '--output', help='Output file path (optional, prints to stdout if not provided)')
        health_parser.add_argument('-f', '--format', default='text',
                                  choices=['text', 'json'],
                                  help='Output format (default: text)')
        
        # Trend analysis command
        trends_parser = subparsers.add_parser('trends',
                                             help='Analyze repository trends over time')
        trends_parser.add_argument('repository', help='Repository path (must be a git repository)')
        trends_parser.add_argument('-o', '--output', help='Output file path (optional for text/json, directory for csv)')
        trends_parser.add_argument('-f', '--format', default='text',
                                  choices=['text', 'json', 'csv'],
                                  help='Output format (default: text)')
        trends_parser.add_argument('-p', '--period', default='all',
                                  choices=['week', 'month', 'quarter', 'year', 'all'],
                                  help='Time period to analyze (default: all)')
        trends_parser.add_argument('-i', '--intervals', type=int, default=10,
                                  help='Number of data points to collect (default: 10)')
        
        # Comparison reports command
        compare_parser = subparsers.add_parser('compare',
                                              help='Compare multiple repositories')
        compare_parser.add_argument('repositories', nargs='+',
                                   help='Repository paths or JSON scan files (minimum 2)')
        compare_parser.add_argument('-o', '--output', 
                                   help='Output file path (optional for text/json, directory for csv)')
        compare_parser.add_argument('-f', '--format', default='text',
                                   choices=['text', 'json', 'csv'],
                                   help='Output format (default: text)')
        compare_parser.add_argument('-n', '--names', nargs='+',
                                   help='Custom names for repositories (optional)')
        
        # Multi-repo dashboard command
        dashboard_parser = subparsers.add_parser('dashboard',
                                                help='Generate multi-repository documentation consistency dashboard')
        dashboard_parser.add_argument('repositories', nargs='+',
                                     help='Repository paths or JSON scan files (minimum 2)')
        dashboard_parser.add_argument('-o', '--output',
                                     help='Output file path (optional, prints to stdout if not provided)')
        dashboard_parser.add_argument('-f', '--format', default='text',
                                     choices=['text', 'markdown', 'html', 'json'],
                                     help='Output format (default: text)')
        dashboard_parser.add_argument('-n', '--names', nargs='+',
                                     help='Custom names for repositories (optional)')
        dashboard_parser.add_argument('-s', '--style-guide', default='google',
                                     choices=['google', 'microsoft', 'plain'],
                                     help='Style guide to check against (default: google)')
        dashboard_parser.add_argument('--min-coverage', type=float, default=70.0,
                                     help='Minimum documentation coverage threshold (default: 70.0)')
        dashboard_parser.add_argument('--min-completeness', type=float, default=60.0,
                                     help='Minimum completeness score threshold (default: 60.0)')
        dashboard_parser.add_argument('--no-consistency', action='store_true',
                                     help='Skip consistency analysis')
        dashboard_parser.add_argument('--require-auth', action='store_true',
                                     help='Require membership authentication for access')
        dashboard_parser.add_argument('-u', '--user',
                                     help='User ID for authentication (if --require-auth is enabled)')
        
        # Custom report command
        custom_report_parser = subparsers.add_parser('custom-report',
                                                    help='Generate custom report from template')
        custom_report_parser.add_argument('repository', 
                                         help='Repository path or JSON scan file')
        custom_report_parser.add_argument('-o', '--output',
                                         help='Output file path (prints to stdout if not provided)')
        custom_report_parser.add_argument('-t', '--template',
                                         help='Path to custom template JSON file')
        custom_report_parser.add_argument('-b', '--builtin',
                                         choices=['minimal', 'detailed', 'executive', 'technical'],
                                         help='Use built-in template')
        custom_report_parser.add_argument('--list', action='store_true',
                                         help='List available built-in templates')
        custom_report_parser.add_argument('--create-sample',
                                         choices=['basic', 'comprehensive'],
                                         help='Create a sample template file')
        
        # API server command
        api_parser = subparsers.add_parser('api',
                                           help='Start REST API server')
        api_parser.add_argument('--host', default='127.0.0.1',
                               help='Host address to bind to (default: 127.0.0.1)')
        api_parser.add_argument('--port', type=int, default=5000,
                               help='Port to listen on (default: 5000)')
        api_parser.add_argument('--debug', action='store_true',
                               help='Enable debug mode')
        
        # Real-time collaboration server commands
        start_collab_parser = subparsers.add_parser('start-collab-server',
                                                   help='Start real-time collaboration WebSocket server')
        start_collab_parser.add_argument('--port', type=int, default=8765,
                                       help='WebSocket server port (default: 8765)')
        start_collab_parser.add_argument('--database', default='collaboration.db',
                                       help='Database file path (default: collaboration.db)')
        start_collab_parser.add_argument('--slack-webhook',
                                       help='Slack webhook URL for notifications')
        start_collab_parser.add_argument('--teams-webhook',
                                       help='Microsoft Teams webhook URL for notifications')
        start_collab_parser.add_argument('--daemon', action='store_true',
                                       help='Run as daemon process')
        
        # Collaboration status command
        collab_status_parser = subparsers.add_parser('collab-status',
                                                    help='Check collaboration server status')
        collab_status_parser.add_argument('--port', type=int, default=8765,
                                        help='WebSocket server port (default: 8765)')
        collab_status_parser.add_argument('--database', default='collaboration.db',
                                        help='Database file path (default: collaboration.db)')
        
        # Stop collaboration server command
        stop_collab_parser = subparsers.add_parser('stop-collab-server',
                                                  help='Stop collaboration server')
        
        # Manage collaboration sessions
        manage_sessions_parser = subparsers.add_parser('manage-sessions',
                                                      help='Manage collaboration sessions')
        manage_sessions_parser.add_argument('action', choices=['list', 'history'],
                                          help='Action to perform')
        manage_sessions_parser.add_argument('--database', default='collaboration.db',
                                          help='Database file path (default: collaboration.db)')
        manage_sessions_parser.add_argument('--document-id',
                                          help='Document ID for history action')
        
        # Manage comments
        manage_comments_parser = subparsers.add_parser('manage-comments',
                                                      help='Manage document comments')
        manage_comments_parser.add_argument('action', choices=['list', 'resolve'],
                                          help='Action to perform')
        manage_comments_parser.add_argument('--database', default='collaboration.db',
                                          help='Database file path (default: collaboration.db)')
        manage_comments_parser.add_argument('--document-id',
                                          help='Filter by document ID')
        manage_comments_parser.add_argument('--comment-id',
                                          help='Comment ID for resolve action')
        
        # Manage reviews
        manage_reviews_parser = subparsers.add_parser('manage-reviews',
                                                     help='Manage review workflows')
        manage_reviews_parser.add_argument('action', choices=['list', 'stats'],
                                         help='Action to perform')
        manage_reviews_parser.add_argument('--database', default='collaboration.db',
                                         help='Database file path (default: collaboration.db)')
        
        # Collaborative commands
        collab_parser = subparsers.add_parser('collaborate',
                                             help='Collaborative documentation workspace')
        collab_subparsers = collab_parser.add_subparsers(dest='collab_command',
                                                         help='Collaborative commands')
        
        # Create session
        session_create = collab_subparsers.add_parser('create',
                                                     help='Create a collaborative session')
        session_create.add_argument('project_id', help='Project ID')
        session_create.add_argument('document', help='Document path')
        session_create.add_argument('-u', '--user', required=True,
                                   help='Username or user ID')
        session_create.add_argument('-c', '--content',
                                   help='Initial document content file')
        
        # Join session
        session_join = collab_subparsers.add_parser('join',
                                                   help='Join a collaborative session')
        session_join.add_argument('session_id', help='Session ID')
        session_join.add_argument('-u', '--user', required=True,
                                 help='Username')
        session_join.add_argument('--user-id',
                                 help='User ID')
        
        # List sessions
        session_list = collab_subparsers.add_parser('list',
                                                   help='List collaborative sessions')
        session_list.add_argument('project_id', help='Project ID')
        session_list.add_argument('--status',
                                 choices=['active', 'paused', 'closed'],
                                 help='Filter by status')
        session_list.add_argument('--json', action='store_true',
                                 help='Output as JSON')
        
        # Add comment
        comment_add = collab_subparsers.add_parser('comment',
                                                  help='Add a comment to a session')
        comment_add.add_argument('session_id', help='Session ID')
        comment_add.add_argument('content', help='Comment content')
        comment_add.add_argument('-u', '--user', required=True,
                                help='Username')
        comment_add.add_argument('--user-id',
                                help='User ID')
        comment_add.add_argument('-p', '--position', type=int,
                                help='Position in document')
        
        # Add suggestion
        suggest_add = collab_subparsers.add_parser('suggest',
                                                  help='Add a change suggestion')
        suggest_add.add_argument('session_id', help='Session ID')
        suggest_add.add_argument('suggested_text', help='Suggested text')
        suggest_add.add_argument('-u', '--user', required=True,
                                help='Username')
        suggest_add.add_argument('--user-id',
                                help='User ID')
        suggest_add.add_argument('-p', '--position', type=int, required=True,
                                help='Position in document')
        suggest_add.add_argument('--original',
                                help='Original text to replace')
        suggest_add.add_argument('-r', '--reason',
                                help='Reason for suggestion')
        
        # User management
        user_parser = subparsers.add_parser('user',
                                           help='User management')
        user_subparsers = user_parser.add_subparsers(dest='user_command',
                                                     help='User commands')
        
        # Create user
        user_create = user_subparsers.add_parser('create',
                                                help='Create a new user')
        user_create.add_argument('username', help='Username')
        user_create.add_argument('email', help='Email address')
        user_create.add_argument('-p', '--password',
                                help='Password (will prompt if not provided)')
        user_create.add_argument('-r', '--role',
                                choices=['owner', 'admin', 'editor', 'viewer'],
                                default='viewer',
                                help='User role (default: viewer)')
        
        # Create team
        team_create = user_subparsers.add_parser('create-team',
                                                help='Create a team')
        team_create.add_argument('name', help='Team name')
        team_create.add_argument('--owner', required=True,
                                help='Owner user ID')
        team_create.add_argument('-d', '--description',
                                help='Team description')
        
        # Grant access
        access_grant = user_subparsers.add_parser('grant',
                                                 help='Grant project access')
        access_grant.add_argument('project_id', help='Project ID')
        access_grant.add_argument('--user',
                                 help='User ID to grant access to')
        access_grant.add_argument('--team',
                                 help='Team ID to grant access to')
        access_grant.add_argument('--role',
                                 choices=['owner', 'admin', 'editor', 'viewer'],
                                 default='viewer',
                                 help='Access role')
        access_grant.add_argument('--granted-by', required=True,
                                 help='User ID granting access')
        
        # Hooks command
        hooks_parser = subparsers.add_parser('hooks',
                                             help='Manage hooks system')
        hooks_parser.add_argument('--list', action='store_true',
                                 help='List all registered hooks')
        hooks_parser.add_argument('--all', action='store_true',
                                 help='Show all hook points (including empty ones)')
        hooks_parser.add_argument('--enable', action='store_true',
                                 help='Enable a hook')
        hooks_parser.add_argument('--disable', action='store_true',
                                 help='Disable a hook')
        hooks_parser.add_argument('hook_point', nargs='?',
                                 help='Hook point (e.g., before_scan)')
        hooks_parser.add_argument('hook_name', nargs='?',
                                 help='Hook name to enable/disable')
        
        # Archive management
        archive_parser = subparsers.add_parser('archive',
                                              help='Manage immutable documentation archives')
        archive_subparsers = archive_parser.add_subparsers(dest='archive_command',
                                                          help='Archive commands')
        archive_parser.add_argument('--use-auth', action='store_true',
                                   help='Enable authentication and permission checks')
        
        # Create archive
        archive_create = archive_subparsers.add_parser('create',
                                                      help='Create a new archive')
        archive_create.add_argument('repository', help='Repository path')
        archive_create.add_argument('document', help='Document file to archive')
        archive_create.add_argument('-f', '--format',
                                   choices=['markdown', 'html', 'pdf'],
                                   help='Archive format (auto-detected if not specified)')
        archive_create.add_argument('-u', '--user',
                                   help='User ID (defaults to current user)')
        archive_create.add_argument('-t', '--tags',
                                   help='Comma-separated tags')
        archive_create.add_argument('-d', '--description',
                                   help='Archive description')
        archive_create.add_argument('--project-name',
                                   help='Project name (if creating new project)')
        archive_create.add_argument('--json', action='store_true',
                                   help='Output JSON response')
        
        # List archives
        archive_list = archive_subparsers.add_parser('list',
                                                    help='List archives')
        archive_list.add_argument('-r', '--repository',
                                 help='Filter by repository path')
        archive_list.add_argument('-f', '--format',
                                 choices=['markdown', 'html', 'pdf'],
                                 help='Filter by format')
        archive_list.add_argument('-t', '--tags',
                                 help='Filter by tags (comma-separated)')
        archive_list.add_argument('-l', '--limit', type=int, default=100,
                                 help='Maximum number of results (default: 100)')
        archive_list.add_argument('--json', action='store_true',
                                 help='Output as JSON')
        
        # Retrieve archive
        archive_get = archive_subparsers.add_parser('retrieve',
                                                   help='Retrieve an archive')
        archive_get.add_argument('archive_id', help='Archive ID')
        archive_get.add_argument('-o', '--output',
                                help='Output file path (defaults to original name)')
        archive_get.add_argument('-u', '--user',
                                help='User ID (defaults to current user)')
        archive_get.add_argument('--no-validate', action='store_true',
                                help='Skip signature validation')
        
        # Validate archive
        archive_validate = archive_subparsers.add_parser('validate',
                                                        help='Validate archive signature')
        archive_validate.add_argument('archive_id', help='Archive ID')
        
        # Delete archive
        archive_delete = archive_subparsers.add_parser('delete',
                                                      help='Delete an archive')
        archive_delete.add_argument('archive_id', help='Archive ID')
        archive_delete.add_argument('-u', '--user',
                                   help='User ID (defaults to current user)')
        archive_delete.add_argument('-y', '--yes', action='store_true',
                                   help='Skip confirmation')
        
        # Archive statistics
        archive_stats = archive_subparsers.add_parser('stats',
                                                     help='Show archive statistics')
        archive_stats.add_argument('-r', '--repository',
                                  help='Filter by repository path')
        archive_stats.add_argument('--json', action='store_true',
                                  help='Output as JSON')
        
        # Onboarding command
        onboarding_parser = subparsers.add_parser('onboarding',
                                                 help='Generate onboarding guides for new contributors')
        onboarding_subparsers = onboarding_parser.add_subparsers(
            dest='onboarding_command',
            help='Onboarding subcommands'
        )
        
        # Create onboarding checklist
        onboarding_create = onboarding_subparsers.add_parser('create',
                                                             help='Create onboarding checklist')
        onboarding_create.add_argument('repository', help='Repository path')
        onboarding_create.add_argument('-o', '--output', help='Output file path')
        onboarding_create.add_argument('--title', help='Custom checklist title')
        onboarding_create.add_argument('--org-id', help='Organization ID')
        onboarding_create.add_argument('--format', choices=['markdown', 'checklist', 'json'],
                                       default='markdown', help='Output format (default: markdown)')
        onboarding_create.add_argument('-u', '--user', help='User ID for authentication')
        
        # List checklists
        onboarding_list = onboarding_subparsers.add_parser('list',
                                                          help='List existing onboarding checklists')
        onboarding_list.add_argument('--org-id', help='Filter by organization ID')
        onboarding_list.add_argument('--json', action='store_true', help='Output as JSON')
        
        # Get checklist
        onboarding_get = onboarding_subparsers.add_parser('get',
                                                         help='Get a specific checklist')
        onboarding_get.add_argument('checklist_id', help='Checklist ID')
        onboarding_get.add_argument('-o', '--output', help='Output file path')
        onboarding_get.add_argument('--format', choices=['markdown', 'checklist', 'json'],
                                   default='markdown', help='Output format')
        
        # Assign checklist to user
        onboarding_assign = onboarding_subparsers.add_parser('assign',
                                                            help='Assign checklist to user')
        onboarding_assign.add_argument('checklist_id', help='Checklist ID')
        onboarding_assign.add_argument('user_id', help='User ID to assign to')
        
        # Update progress
        onboarding_progress = onboarding_subparsers.add_parser('progress',
                                                              help='Update checklist progress')
        onboarding_progress.add_argument('progress_id', help='Progress ID')
        onboarding_progress.add_argument('step_id', help='Completed step ID')
        
        # Compliance mapping command
        compliance_parser = subparsers.add_parser('compliance',
                                                 help='Regulatory compliance mapping and gap analysis')
        compliance_subparsers = compliance_parser.add_subparsers(
            dest='compliance_command',
            help='Compliance subcommands'
        )
        
        # Map documentation to requirement
        compliance_map = compliance_subparsers.add_parser('map',
                                                         help='Map documentation to regulatory requirement')
        compliance_map.add_argument('repository', help='Repository path')
        compliance_map.add_argument('requirement_id', help='Regulatory requirement ID (e.g., SOC2-CC1.1)')
        compliance_map.add_argument('doc_section', help='Documentation section identifier')
        compliance_map.add_argument('-f', '--framework', required=True,
                                   choices=['soc2', 'hipaa', 'gdpr', 'iso27001', 'pci_dss', 'ccpa', 'nist', 'fedramp'],
                                   help='Compliance framework')
        compliance_map.add_argument('-p', '--doc-path', help='Path to documentation file')
        compliance_map.add_argument('-s', '--status', 
                                   choices=['covered', 'partial', 'not_covered', 'not_applicable'],
                                   help='Coverage status (default: covered)')
        compliance_map.add_argument('-n', '--notes', help='Additional notes')
        compliance_map.add_argument('-e', '--evidence', help='Evidence (comma-separated list)')
        compliance_map.add_argument('--project-name', help='Project name (if creating new project)')
        compliance_map.add_argument('-u', '--user', help='User ID for authentication')
        compliance_map.add_argument('--use-auth', action='store_true',
                                   help='Enable membership authentication')
        
        # List mappings
        compliance_list = compliance_subparsers.add_parser('list',
                                                          help='List compliance mappings')
        compliance_list.add_argument('repository', help='Repository path')
        compliance_list.add_argument('-f', '--framework',
                                    choices=['soc2', 'hipaa', 'gdpr', 'iso27001', 'pci_dss', 'ccpa', 'nist', 'fedramp'],
                                    help='Filter by framework')
        compliance_list.add_argument('--json', action='store_true',
                                    help='Output as JSON')
        
        # Analyze gaps
        compliance_analyze = compliance_subparsers.add_parser('analyze',
                                                             help='Perform compliance gap analysis')
        compliance_analyze.add_argument('repository', help='Repository path')
        compliance_analyze.add_argument('-f', '--framework', required=True,
                                       choices=['soc2', 'hipaa', 'gdpr', 'iso27001', 'pci_dss', 'ccpa', 'nist', 'fedramp'],
                                       help='Compliance framework')
        compliance_analyze.add_argument('--json', action='store_true',
                                       help='Output as JSON')
        
        # Generate report
        compliance_report = compliance_subparsers.add_parser('report',
                                                            help='Generate compliance report')
        compliance_report.add_argument('repository', help='Repository path')
        compliance_report.add_argument('-f', '--framework', required=True,
                                      choices=['soc2', 'hipaa', 'gdpr', 'iso27001', 'pci_dss', 'ccpa', 'nist', 'fedramp'],
                                      help='Compliance framework')
        compliance_report.add_argument('-o', '--output', help='Output file path')
        compliance_report.add_argument('--format', default='text',
                                      choices=['text', 'markdown', 'html', 'json'],
                                      help='Report format (default: text)')
        
        # List frameworks and requirements
        compliance_frameworks = compliance_subparsers.add_parser('frameworks',
                                                                help='List available frameworks and requirements')
        compliance_frameworks.add_argument('-f', '--framework',
                                          choices=['soc2', 'hipaa', 'gdpr', 'iso27001', 'pci_dss', 'ccpa', 'nist', 'fedramp'],
                                          help='Show requirements for specific framework')
        compliance_frameworks.add_argument('--json', action='store_true',
                                          help='Output as JSON')
        
        # Quality Scoring commands
        quality_analyze_parser = subparsers.add_parser('quality-analyze',
                                                      help='Analyze documentation quality with advanced metrics')
        quality_analyze_parser.add_argument('repository', help='Repository path')
        quality_analyze_parser.add_argument('-t', '--project-type',
                                          choices=['web-framework', 'library', 'cli-tool', 'api-service', 
                                                  'mobile-app', 'desktop-app', 'data-science', 'other'],
                                          default='library',
                                          help='Project type for benchmarking (default: library)')
        quality_analyze_parser.add_argument('--save-metrics', action='store_true',
                                          help='Save metrics to database for historical tracking')
        quality_analyze_parser.add_argument('--benchmark', action='store_true',
                                          help='Include industry benchmark comparison')
        quality_analyze_parser.add_argument('--suggestions', action='store_true',
                                          help='Generate improvement suggestions')
        quality_analyze_parser.add_argument('--format', choices=['text', 'json', 'html'],
                                          default='text',
                                          help='Output format (default: text)')
        quality_analyze_parser.add_argument('-o', '--output',
                                          help='Output file path')
        
        quality_history_parser = subparsers.add_parser('quality-history',
                                                      help='View quality scoring history and trends')
        quality_history_parser.add_argument('repository', help='Repository path')
        quality_history_parser.add_argument('--days', type=int, default=30,
                                          help='Number of days to look back (default: 30)')
        quality_history_parser.add_argument('--format', choices=['text', 'json', 'csv'],
                                          default='text',
                                          help='Output format (default: text)')
        quality_history_parser.add_argument('-o', '--output',
                                          help='Output file path')
        
        quality_benchmark_parser = subparsers.add_parser('quality-benchmark',
                                                        help='Compare quality against industry benchmarks')
        quality_benchmark_parser.add_argument('repository', help='Repository path')
        quality_benchmark_parser.add_argument('-t', '--project-type',
                                            choices=['web-framework', 'library', 'cli-tool', 'api-service', 
                                                    'mobile-app', 'desktop-app', 'data-science', 'other'],
                                            default='library',
                                            help='Project type for benchmarking (default: library)')
        quality_benchmark_parser.add_argument('--format', choices=['text', 'json'],
                                            default='text',
                                            help='Output format (default: text)')
        
        quality_report_parser = subparsers.add_parser('quality-report',
                                                     help='Generate comprehensive quality report')
        quality_report_parser.add_argument('repository', help='Repository path')
        quality_report_parser.add_argument('-t', '--project-type',
                                         choices=['web-framework', 'library', 'cli-tool', 'api-service', 
                                                 'mobile-app', 'desktop-app', 'data-science', 'other'],
                                         default='library',
                                         help='Project type for benchmarking (default: library)')
        quality_report_parser.add_argument('--include-history', action='store_true',
                                         help='Include historical trend analysis')
        quality_report_parser.add_argument('--include-benchmark', action='store_true',
                                         help='Include industry benchmark comparison')
        quality_report_parser.add_argument('--format', choices=['text', 'html', 'markdown', 'json'],
                                         default='html',
                                         help='Output format (default: html)')
        quality_report_parser.add_argument('-o', '--output',
                                         help='Output file path')
        
        # Parse arguments
        args = parser.parse_args()
        
        # Setup logging based on verbosity
        self.setup_logging(args.verbose)
        
        # Execute command
        if not args.command:
            parser.print_help()
            return 0
        
        command_map = {
            'scan': self.scan_command,
            'generate': self.generate_command,
            'export': self.export_command,
            'site': self.site_command,
            'info': self.info_command,
            'cache': self.cache_command,
            'onboarding': self.onboarding_command,
            'check-links': self.check_links_command,
            'plugins': self.plugins_command,
            'batch': self.batch_command,
            'branch-compare': self.branch_compare_command,
            'version-check': self.version_check_command,
            'spellcheck': self.spellcheck_command,
            'multi-repo': self.multi_repo_command,
            'coverage': self.coverage_command,
            'readability': self.readability_command,
            'db-schema': self.db_schema_command,
            'monorepo': self.monorepo_command,
            'breaking-changes': self.breaking_changes_command,
            'code-quality': self.code_quality_command,
            'grammar': self.grammar_check_command,
            'doc-coverage': self.doc_coverage_command,
            'dataflow': self.dataflow_command,
            'config': self.config_command,
            'opensource': self.opensource_command,
            'data-export': self.data_export_command,
            'health': self.health_command,
            'trends': self.trends_command,
            'compare': self.compare_command,
            'dashboard': self.dashboard_command,
            'custom-report': self.custom_report_command,
            'api': self.api_server_command,
            'start-collab-server': self.start_collab_server_command,
            'collab-status': self.collab_status_command,
            'stop-collab-server': self.stop_collab_server_command,
            'manage-sessions': self.manage_sessions_command,
            'manage-comments': self.manage_comments_command,
            'manage-reviews': self.manage_reviews_command,
            'hooks': self.hooks_command,
            'collaborate': self.collaborate_command,
            'user': self.user_command,
            'archive': self.archive_command,
            'quality-analyze': self.quality_analyze_command,
            'quality-history': self.quality_history_command,
            'quality-benchmark': self.quality_benchmark_command,
            'quality-report': self.quality_report_command,
            'compliance': self.compliance_command,
        }
        
        handler = command_map.get(args.command)
        if handler:
            return handler(args)
        else:
            parser.print_help()
            return 1

    def quality_analyze_command(self, args):
        """Handle quality analyze command."""
        try:
            analyzer = QualityAnalyzer()
            
            # Run quality analysis
            results = analyzer.analyze_repository(
                args.repository,
                project_type=args.project_type
            )
            
            # Save metrics if requested
            if args.save_metrics:
                analyzer.save_metrics(args.repository, results.metrics)
                print(f"✓ Quality metrics saved to database")
            
            # Generate output based on format
            if args.format == 'json':
                output = json.dumps({
                    'overall_score': results.overall_score,
                    'metrics': results.metrics.__dict__,
                    'suggestions': results.suggestions,
                    'documentation_debt': results.documentation_debt
                }, indent=2)
            elif args.format == 'html':
                output = analyzer.generate_html_report(results, args.project_type)
            else:
                # Text format
                output = f"""
📊 AccuDoc Quality Analysis Report
================================
Repository: {args.repository}
Project Type: {args.project_type}
Analysis Date: {results.analysis_date}

📈 Overall Quality Score: {results.overall_score:.1f}/100

📋 Detailed Metrics:
• Clarity Score: {results.metrics.clarity_score:.1f}/100
  - Flesch Reading Ease: {results.metrics.flesch_reading_ease:.1f}
  - Gunning Fog Index: {results.metrics.gunning_fog_index:.1f}
  - Avg Sentence Length: {results.metrics.avg_sentence_length:.1f} words

• Completeness Score: {results.metrics.completeness_score:.1f}/100
  - Documentation Coverage: {results.metrics.documentation_coverage:.1f}%
  - API Coverage: {results.metrics.api_coverage:.1f}%
  - Required Sections: {results.metrics.required_sections_count}/{results.metrics.total_required_sections}

• Accuracy Score: {results.metrics.accuracy_score:.1f}/100
  - Broken Links: {results.metrics.broken_links_count}
  - Outdated Content Score: {results.metrics.outdated_content_score:.1f}%
  - Factual Consistency: {results.metrics.factual_consistency_score:.1f}%
"""
                
                if args.benchmark and results.benchmark:
                    output += f"""
🏆 Industry Benchmark Comparison:
• Industry Average: {results.benchmark['industry_average']:.1f}
• Your Score: {results.overall_score:.1f} ({'+' if results.overall_score > results.benchmark['industry_average'] else ''}{results.overall_score - results.benchmark['industry_average']:.1f})
• Percentile Rank: {results.benchmark['percentile_rank']}th percentile
"""
                
                if args.suggestions and results.suggestions:
                    output += f"""
💡 Improvement Suggestions:
{chr(10).join(f"• {suggestion}" for suggestion in results.suggestions)}
"""
                
                output += f"""
📊 Documentation Debt: {results.documentation_debt:.1f}
"""
            
            # Write to file or print to stdout
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"✓ Quality analysis report saved to {args.output}")
            else:
                print(output)
            
            return 0
            
        except Exception as e:
            print(f"❌ Error analyzing quality: {e}")
            return 1

    def quality_history_command(self, args):
        """Handle quality history command."""
        try:
            analyzer = QualityAnalyzer()
            history = analyzer.get_quality_history(args.repository, days=args.days)
            
            if args.format == 'json':
                output = json.dumps([
                    {
                        'date': entry['analysis_date'],
                        'overall_score': entry['overall_score'],
                        'clarity_score': entry['clarity_score'],
                        'completeness_score': entry['completeness_score'],
                        'accuracy_score': entry['accuracy_score'],
                        'documentation_debt': entry['documentation_debt']
                    }
                    for entry in history
                ], indent=2)
            elif args.format == 'csv':
                output = "Date,Overall Score,Clarity,Completeness,Accuracy,Documentation Debt\n"
                output += "\n".join([
                    f"{entry['analysis_date']},{entry['overall_score']:.1f},{entry['clarity_score']:.1f},"
                    f"{entry['completeness_score']:.1f},{entry['accuracy_score']:.1f},{entry['documentation_debt']:.1f}"
                    for entry in history
                ])
            else:
                # Text format
                output = f"""
📈 Quality History for {args.repository}
======================================
Last {args.days} days

"""
                for entry in history:
                    output += f"""
📅 {entry['analysis_date']}
• Overall Score: {entry['overall_score']:.1f}/100
• Clarity: {entry['clarity_score']:.1f}/100
• Completeness: {entry['completeness_score']:.1f}/100  
• Accuracy: {entry['accuracy_score']:.1f}/100
• Documentation Debt: {entry['documentation_debt']:.1f}
"""
            
            # Write to file or print to stdout
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"✓ Quality history saved to {args.output}")
            else:
                print(output)
            
            return 0
            
        except Exception as e:
            print(f"❌ Error retrieving quality history: {e}")
            return 1

    def quality_benchmark_command(self, args):
        """Handle quality benchmark command."""
        try:
            analyzer = QualityAnalyzer()
            benchmark = analyzer.get_industry_benchmark(args.project_type)
            
            # Get current score for comparison
            results = analyzer.analyze_repository(args.repository, project_type=args.project_type)
            
            if args.format == 'json':
                output = json.dumps({
                    'project_type': args.project_type,
                    'industry_benchmark': benchmark,
                    'your_score': results.overall_score,
                    'percentile_rank': analyzer.calculate_percentile_rank(results.overall_score, args.project_type)
                }, indent=2)
            else:
                # Text format
                percentile = analyzer.calculate_percentile_rank(results.overall_score, args.project_type)
                output = f"""
🏆 Industry Benchmark Comparison
===============================
Project Type: {args.project_type}
Repository: {args.repository}

📊 Benchmark Results:
• Industry Average: {benchmark['average']:.1f}/100
• Industry Median: {benchmark['median']:.1f}/100
• 75th Percentile: {benchmark['p75']:.1f}/100
• 90th Percentile: {benchmark['p90']:.1f}/100

📈 Your Performance:
• Your Score: {results.overall_score:.1f}/100
• Difference from Average: {'+' if results.overall_score > benchmark['average'] else ''}{results.overall_score - benchmark['average']:.1f}
• Percentile Rank: {percentile}th percentile

🎯 Performance Level: {analyzer.get_performance_level(percentile)}
"""
            
            print(output)
            return 0
            
        except Exception as e:
            print(f"❌ Error getting benchmark data: {e}")
            return 1

    def quality_report_command(self, args):
        """Handle quality report command."""
        try:
            analyzer = QualityAnalyzer()
            
            # Run comprehensive analysis
            results = analyzer.analyze_repository(args.repository, project_type=args.project_type)
            
            # Get history if requested
            history = None
            if args.include_history:
                history = analyzer.get_quality_history(args.repository, days=90)
            
            # Get benchmark if requested
            benchmark = None
            if args.include_benchmark:
                benchmark = analyzer.get_industry_benchmark(args.project_type)
            
            # Generate report based on format
            if args.format == 'html':
                output = analyzer.generate_html_report(
                    results, 
                    args.project_type,
                    history=history,
                    benchmark=benchmark
                )
            elif args.format == 'markdown':
                output = analyzer.generate_markdown_report(
                    results,
                    args.project_type,
                    history=history,
                    benchmark=benchmark
                )
            elif args.format == 'json':
                report_data = {
                    'repository': args.repository,
                    'project_type': args.project_type,
                    'analysis_date': results.analysis_date,
                    'overall_score': results.overall_score,
                    'metrics': results.metrics.__dict__,
                    'suggestions': results.suggestions,
                    'documentation_debt': results.documentation_debt
                }
                if history:
                    report_data['history'] = history
                if benchmark:
                    report_data['benchmark'] = benchmark
                output = json.dumps(report_data, indent=2)
            else:
                # Text format (comprehensive)
                output = analyzer.generate_text_report(
                    results,
                    args.project_type, 
                    history=history,
                    benchmark=benchmark
                )
            
            # Save or display report
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"✓ Comprehensive quality report saved to {args.output}")
            else:
                print(output)
            
            return 0
            
        except Exception as e:
            print(f"❌ Error generating quality report: {e}")
            return 1


def main():
    """Main entry point."""
    cli = AccuDocCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
