#!/usr/bin/env python3
"""
Demo script for Bitbucket API integration.

This demonstrates how to use AccuDoc's Bitbucket API integration to scan
repositories without cloning them locally.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from accudoc.bitbucket_api import BitbucketAPIClient, scan_bitbucket_repository
from accudoc.generator import DocumentGenerator


def demo_basic_usage():
    """Demonstrate basic Bitbucket API usage."""
    print("\n" + "=" * 70)
    print("Demo 1: Basic Bitbucket API Client Usage")
    print("=" * 70 + "\n")
    
    # Create a client (no credentials needed for public repos)
    client = BitbucketAPIClient()
    print("✓ Created Bitbucket API client")
    
    # Parse a Bitbucket URL
    url = "https://bitbucket.org/tutorials/markdowndemo"
    workspace, repo_slug = client.parse_bitbucket_url(url)
    print(f"✓ Parsed URL: {url}")
    print(f"  Workspace: {workspace}")
    print(f"  Repository: {repo_slug}")
    
    print("\n" + "-" * 70)


def demo_authenticated_client():
    """Demonstrate creating an authenticated client."""
    print("\n" + "=" * 70)
    print("Demo 2: Authenticated Bitbucket API Client")
    print("=" * 70 + "\n")
    
    # Create authenticated client (for private repositories)
    # In real usage, get these from environment variables or config
    username = "your_username"
    app_password = "your_app_password"
    
    client = BitbucketAPIClient(username=username, app_password=app_password)
    print("✓ Created authenticated Bitbucket API client")
    print("  (For private repositories)")
    
    print("\nTo use authentication:")
    print("  1. Go to Bitbucket Settings > App passwords")
    print("  2. Create a new app password with 'repository:read' permission")
    print("  3. Use your username and app password to create the client")
    
    print("\n" + "-" * 70)


def demo_url_formats():
    """Demonstrate different URL format support."""
    print("\n" + "=" * 70)
    print("Demo 3: Supported Bitbucket URL Formats")
    print("=" * 70 + "\n")
    
    client = BitbucketAPIClient()
    
    # Test various URL formats
    test_urls = [
        "https://bitbucket.org/workspace/repo",
        "https://bitbucket.org/workspace/repo.git",
        "http://bitbucket.org/workspace/repo",
        "git@bitbucket.org:workspace/repo.git",
    ]
    
    print("Supported URL formats:")
    for url in test_urls:
        try:
            workspace, repo = client.parse_bitbucket_url(url)
            print(f"  ✓ {url}")
            print(f"    -> {workspace}/{repo}")
        except Exception as e:
            print(f"  ✗ {url}: {e}")
    
    print("\n" + "-" * 70)


def demo_convenience_function():
    """Demonstrate the convenience scanning function."""
    print("\n" + "=" * 70)
    print("Demo 4: Convenience Function for Repository Scanning")
    print("=" * 70 + "\n")
    
    print("The scan_bitbucket_repository() function provides easy access:")
    print()
    print("  from accudoc.bitbucket_api import scan_bitbucket_repository")
    print()
    print("  # Scan a public repository")
    print("  repo_info = scan_bitbucket_repository(")
    print("      'https://bitbucket.org/workspace/repo'")
    print("  )")
    print()
    print("  # Scan a private repository with authentication")
    print("  repo_info = scan_bitbucket_repository(")
    print("      'https://bitbucket.org/workspace/repo',")
    print("      username='your_username',")
    print("      app_password='your_app_password'")
    print("  )")
    print()
    print("  # Scan a specific branch")
    print("  repo_info = scan_bitbucket_repository(")
    print("      'https://bitbucket.org/workspace/repo',")
    print("      branch='develop'")
    print("  )")
    
    print("\n" + "-" * 70)


def demo_api_methods():
    """Demonstrate available API methods."""
    print("\n" + "=" * 70)
    print("Demo 5: Available Bitbucket API Methods")
    print("=" * 70 + "\n")
    
    print("BitbucketAPIClient provides the following methods:")
    print()
    print("  Repository Information:")
    print("    • get_repository_info(workspace, repo_slug)")
    print("    • get_repository_tree(workspace, repo_slug, branch='main')")
    print()
    print("  File Content:")
    print("    • get_file_content(workspace, repo_slug, path, branch='main')")
    print("    • get_readme(workspace, repo_slug, branch='main')")
    print()
    print("  Repository Metadata:")
    print("    • get_languages(workspace, repo_slug)")
    print("    • get_commits(workspace, repo_slug, branch='main', limit=50)")
    print()
    print("  High-Level Scanning:")
    print("    • scan_via_api(workspace, repo_slug, branch='main')")
    print()
    
    print("\n" + "-" * 70)


def demo_integration_with_generator():
    """Demonstrate integration with DocumentGenerator."""
    print("\n" + "=" * 70)
    print("Demo 6: Integration with AccuDoc Document Generator")
    print("=" * 70 + "\n")
    
    print("Bitbucket API scanning integrates seamlessly with AccuDoc:")
    print()
    print("  from accudoc.bitbucket_api import scan_bitbucket_repository")
    print("  from accudoc.generator import DocumentGenerator")
    print()
    print("  # Scan repository via API")
    print("  repo_info = scan_bitbucket_repository(")
    print("      'https://bitbucket.org/workspace/repo'")
    print("  )")
    print()
    print("  # Generate documentation from scan results")
    print("  generator = DocumentGenerator(repo_info)")
    print("  documentation = generator.generate(template='detailed')")
    print()
    print("  # Save to file")
    print("  with open('DOCUMENTATION.md', 'w') as f:")
    print("      f.write(documentation)")
    
    print("\n" + "-" * 70)


def demo_benefits():
    """Demonstrate benefits of API integration."""
    print("\n" + "=" * 70)
    print("Demo 7: Benefits of Bitbucket API Integration")
    print("=" * 70 + "\n")
    
    print("Benefits of using Bitbucket API integration:")
    print()
    print("  ✓ No Cloning Required")
    print("    - Scan repositories without downloading entire history")
    print("    - Saves disk space and bandwidth")
    print()
    print("  ✓ Faster Scanning")
    print("    - Direct API access is often faster than git clone")
    print("    - Especially for large repositories")
    print()
    print("  ✓ Lower Bandwidth")
    print("    - Only download metadata and specific files needed")
    print("    - Great for CI/CD environments")
    print()
    print("  ✓ Support for Private Repositories")
    print("    - Use app passwords for authentication")
    print("    - Secure access to private repositories")
    print()
    print("  ✓ Branch Selection")
    print("    - Scan specific branches without checking them out")
    print("    - Compare documentation across branches")
    
    print("\n" + "-" * 70)


def demo_comparison_with_other_platforms():
    """Compare with GitHub and GitLab integrations."""
    print("\n" + "=" * 70)
    print("Demo 8: Multi-Platform Support")
    print("=" * 70 + "\n")
    
    print("AccuDoc now supports API integration with three major platforms:")
    print()
    print("  GitHub:")
    print("    from accudoc.github_api import scan_github_repository")
    print("    repo_info = scan_github_repository('https://github.com/user/repo')")
    print()
    print("  GitLab:")
    print("    from accudoc.gitlab_api import scan_gitlab_repository")
    print("    repo_info = scan_gitlab_repository('https://gitlab.com/user/repo')")
    print()
    print("  Bitbucket:")
    print("    from accudoc.bitbucket_api import scan_bitbucket_repository")
    print("    repo_info = scan_bitbucket_repository('https://bitbucket.org/workspace/repo')")
    print()
    print("All three integrations provide consistent interfaces and return")
    print("compatible data structures for use with AccuDoc's DocumentGenerator.")
    
    print("\n" + "-" * 70)


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("AccuDoc Bitbucket API Integration - Demo")
    print("=" * 70)
    print()
    print("This demo showcases AccuDoc's Bitbucket API integration capabilities.")
    print("No actual API calls are made - this is purely educational.")
    
    try:
        demo_basic_usage()
        demo_authenticated_client()
        demo_url_formats()
        demo_convenience_function()
        demo_api_methods()
        demo_integration_with_generator()
        demo_benefits()
        demo_comparison_with_other_platforms()
        
        print("\n" + "=" * 70)
        print("Demo Complete!")
        print("=" * 70)
        print()
        print("To scan an actual Bitbucket repository:")
        print("  python3 -c \"from accudoc.bitbucket_api import scan_bitbucket_repository;")
        print("             print(scan_bitbucket_repository('https://bitbucket.org/workspace/repo'))\"")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
