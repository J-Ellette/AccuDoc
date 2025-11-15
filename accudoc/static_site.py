"""
Static site generator for AccuDoc.

Creates a complete documentation website with navigation, search functionality,
and multiple pages organized by topics.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import re


class StaticSiteGenerator:
    """Generate a static documentation website."""
    
    def __init__(self, repo_info: Dict, output_dir: Path, 
                 title: str = "Documentation", theme: str = "default"):
        """
        Initialize static site generator.
        
        Args:
            repo_info: Repository information from scanner
            output_dir: Output directory for the website
            title: Site title
            theme: Color theme
        """
        self.repo_info = repo_info
        self.output_dir = Path(output_dir)
        self.title = title
        self.theme = theme
        self.logger = logging.getLogger('accudoc.staticsite')
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate(self) -> Path:
        """
        Generate the complete static site.
        
        Returns:
            Path to the generated site (index.html)
        """
        self.logger.info(f"Generating static site in {self.output_dir}")
        
        # Generate pages
        self._generate_index_page()
        self._generate_api_page()
        self._generate_architecture_page()
        self._generate_contributing_page()
        
        # Generate assets
        self._generate_css()
        self._generate_search_js()
        self._generate_search_index()
        
        self.logger.info("Static site generation complete")
        return self.output_dir / "index.html"
    
    def _generate_index_page(self):
        """Generate the main index page."""
        content = f"""
<h1>{self.repo_info.get('name', 'Repository')} Documentation</h1>

<div class="overview-section">
    <h2>Overview</h2>
    <p>{self.repo_info.get('readme_content', 'No description available.')[:500]}</p>
</div>

<div class="quick-stats">
    <h2>Quick Stats</h2>
    <div class="stats-grid">
        <div class="stat-card">
            <h3>{len(self.repo_info.get('files', []))}</h3>
            <p>Files</p>
        </div>
        <div class="stat-card">
            <h3>{len(self.repo_info.get('languages', {}))}</h3>
            <p>Languages</p>
        </div>
        <div class="stat-card">
            <h3>{len(self.repo_info.get('dependencies', {}))}</h3>
            <p>Dependencies</p>
        </div>
        <div class="stat-card">
            <h3>{self.repo_info.get('git_info', {}).get('stars', 0)}</h3>
            <p>Stars</p>
        </div>
    </div>
</div>

<div class="languages-section">
    <h2>Languages</h2>
    <ul>
"""
        for lang, count in self.repo_info.get('languages', {}).items():
            content += f"        <li><strong>{lang}</strong>: {count} files</li>\n"
        
        content += """
    </ul>
</div>
"""
        
        self._write_page("index.html", content, "Home")
    
    def _generate_api_page(self):
        """Generate API documentation page."""
        api_docs = self.repo_info.get('api_docs', {})
        
        content = """
<h1>API Documentation</h1>

<div class="api-section">
"""
        
        if not api_docs:
            content += "<p>No API documentation available.</p>"
        else:
            for module, items in api_docs.items():
                content += f"<h2>Module: {module}</h2>\n"
                
                # Functions
                if 'functions' in items:
                    content += "<h3>Functions</h3>\n<ul>\n"
                    for func in items['functions']:
                        content += f"<li><code>{func}</code></li>\n"
                    content += "</ul>\n"
                
                # Classes
                if 'classes' in items:
                    content += "<h3>Classes</h3>\n<ul>\n"
                    for cls in items['classes']:
                        content += f"<li><code>{cls}</code></li>\n"
                    content += "</ul>\n"
        
        content += """
</div>
"""
        
        self._write_page("api.html", content, "API Documentation")
    
    def _generate_architecture_page(self):
        """Generate architecture documentation page."""
        architecture = self.repo_info.get('architecture', '')
        dependency_graph = self.repo_info.get('dependency_graph', '')
        
        content = """
<h1>Architecture</h1>

<div class="architecture-section">
    <h2>Project Structure</h2>
"""
        
        if architecture:
            content += f"<pre><code class=\"language-mermaid\">{architecture}</code></pre>\n"
        else:
            content += "<p>No architecture diagram available.</p>\n"
        
        content += """
    <h2>Dependencies</h2>
"""
        
        if dependency_graph:
            content += f"<pre><code class=\"language-mermaid\">{dependency_graph}</code></pre>\n"
        else:
            content += "<p>No dependency graph available.</p>\n"
        
        content += """
</div>
"""
        
        self._write_page("architecture.html", content, "Architecture")
    
    def _generate_contributing_page(self):
        """Generate contributing guidelines page."""
        git_info = self.repo_info.get('git_info', {})
        
        content = f"""
<h1>Contributing</h1>

<div class="contributing-section">
    <h2>How to Contribute</h2>
    <p>We welcome contributions to this project!</p>
    
    <h3>Getting Started</h3>
    <ol>
        <li>Fork the repository</li>
        <li>Create a feature branch</li>
        <li>Make your changes</li>
        <li>Submit a pull request</li>
    </ol>
    
    <h3>Repository Information</h3>
    <ul>
        <li><strong>Default Branch:</strong> {git_info.get('default_branch', 'main')}</li>
        <li><strong>License:</strong> {git_info.get('license', 'Unknown')}</li>
    </ul>
    
    <h3>Top Contributors</h3>
    <ul>
"""
        
        contributors = git_info.get('contributors', [])[:10]
        for contributor in contributors:
            content += f"        <li>{contributor.get('login', 'Unknown')} ({contributor.get('contributions', 0)} contributions)</li>\n"
        
        content += """
    </ul>
</div>
"""
        
        self._write_page("contributing.html", content, "Contributing")
    
    def _write_page(self, filename: str, content: str, page_title: str):
        """Write a page with the standard template."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - {self.title}</title>
    <link rel="stylesheet" href="styles.css">
    <script src="search.js" defer></script>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">{self.title}</div>
        <div class="nav-links">
            <a href="index.html">Home</a>
            <a href="api.html">API</a>
            <a href="architecture.html">Architecture</a>
            <a href="contributing.html">Contributing</a>
        </div>
        <div class="search-box">
            <input type="text" id="search-input" placeholder="Search documentation...">
            <div id="search-results" class="search-results"></div>
        </div>
    </nav>
    
    <main class="container">
        {content}
    </main>
    
    <footer>
        <p>Generated by <a href="https://github.com/jamesellette/AccuDoc">AccuDoc</a></p>
    </footer>
</body>
</html>"""
        
        output_path = self.output_dir / filename
        output_path.write_text(html, encoding='utf-8')
        self.logger.debug(f"Generated {filename}")
    
    def _generate_css(self):
        """Generate CSS stylesheet."""
        css = self._get_css_for_theme()
        css_path = self.output_dir / "styles.css"
        css_path.write_text(css, encoding='utf-8')
    
    def _get_css_for_theme(self) -> str:
        """Get CSS based on selected theme."""
        base_css = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.6;
    color: #333;
    background: #f5f5f5;
}

.navbar {
    background: #2c3e50;
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-brand {
    font-size: 1.5rem;
    font-weight: bold;
}

.nav-links {
    display: flex;
    gap: 2rem;
}

.nav-links a {
    color: white;
    text-decoration: none;
    transition: opacity 0.3s;
}

.nav-links a:hover {
    opacity: 0.8;
}

.search-box {
    position: relative;
    width: 300px;
}

.search-box input {
    width: 100%;
    padding: 0.5rem;
    border: none;
    border-radius: 4px;
    font-size: 0.9rem;
}

.search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-top: 0.5rem;
    max-height: 400px;
    overflow-y: auto;
    display: none;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.search-results.active {
    display: block;
}

.search-result-item {
    padding: 0.75rem;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    color: #333;
}

.search-result-item:hover {
    background: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 2rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h1 {
    color: #2c3e50;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5rem;
}

h2 {
    color: #34495e;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h3 {
    color: #7f8c8d;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 1.5rem 0;
}

.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.stat-card h3 {
    font-size: 2.5rem;
    margin: 0;
    color: white;
}

.stat-card p {
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
}

ul {
    margin: 1rem 0;
    padding-left: 2rem;
}

li {
    margin: 0.5rem 0;
}

code {
    background: #f4f4f4;
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}

pre {
    background: #f4f4f4;
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    margin: 1rem 0;
}

pre code {
    background: none;
    padding: 0;
}

footer {
    text-align: center;
    padding: 2rem;
    color: #7f8c8d;
    margin-top: 3rem;
}

footer a {
    color: #3498db;
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}
"""
        
        if self.theme == "dark":
            base_css += """
body { background: #1a1a1a; color: #e0e0e0; }
.container { background: #2d2d2d; }
h1 { color: #58a6ff; border-bottom-color: #58a6ff; }
h2, h3 { color: #8b949e; }
code, pre { background: #161b22; color: #e0e0e0; }
.search-results { background: #2d2d2d; border-color: #444; }
.search-result-item { color: #e0e0e0; border-bottom-color: #444; }
.search-result-item:hover { background: #1a1a1a; }
"""
        
        return base_css
    
    def _generate_search_js(self):
        """Generate JavaScript for search functionality."""
        js = """
let searchIndex = [];

// Load search index
fetch('search-index.json')
    .then(response => response.json())
    .then(data => {
        searchIndex = data;
    });

const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');

searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    
    if (query.length < 2) {
        searchResults.classList.remove('active');
        return;
    }
    
    const results = searchIndex.filter(item => 
        item.title.toLowerCase().includes(query) ||
        item.content.toLowerCase().includes(query)
    ).slice(0, 10);
    
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
        searchResults.classList.add('active');
        return;
    }
    
    searchResults.innerHTML = results.map(result => 
        `<div class="search-result-item" onclick="window.location.href='${result.page}'">
            <strong>${result.title}</strong><br>
            <small>${result.content.substring(0, 100)}...</small>
        </div>`
    ).join('');
    
    searchResults.classList.add('active');
});

// Close search results when clicking outside
document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.classList.remove('active');
    }
});
"""
        
        js_path = self.output_dir / "search.js"
        js_path.write_text(js, encoding='utf-8')
    
    def _generate_search_index(self):
        """Generate search index JSON."""
        index = [
            {
                "page": "index.html",
                "title": "Home",
                "content": self.repo_info.get('name', '') + " " + 
                          self.repo_info.get('readme_content', '')[:200]
            },
            {
                "page": "api.html",
                "title": "API Documentation",
                "content": "API reference documentation for all modules, functions, and classes"
            },
            {
                "page": "architecture.html",
                "title": "Architecture",
                "content": "Project architecture, structure, and dependencies"
            },
            {
                "page": "contributing.html",
                "title": "Contributing",
                "content": "How to contribute to the project, guidelines and information"
            }
        ]
        
        # Add API documentation to search index
        api_docs = self.repo_info.get('api_docs', {})
        for module in api_docs:
            index.append({
                "page": "api.html",
                "title": f"Module: {module}",
                "content": f"API documentation for {module} module"
            })
        
        index_path = self.output_dir / "search-index.json"
        index_path.write_text(json.dumps(index, indent=2), encoding='utf-8')


def generate_static_site(repo_info: Dict, output_dir: Path,
                        title: str = "Documentation",
                        theme: str = "default") -> Path:
    """
    Convenience function to generate a static documentation site.
    
    Args:
        repo_info: Repository information from scanner
        output_dir: Output directory for the website
        title: Site title
        theme: Color theme
        
    Returns:
        Path to index.html
    """
    generator = StaticSiteGenerator(repo_info, output_dir, title, theme)
    return generator.generate()
