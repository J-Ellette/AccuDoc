"""
License compliance module for AccuDoc.

Analyzes project licenses and checks for compatibility issues:
- Detect licenses in project files
- Check license compatibility
- Generate compliance reports
- Warn about incompatible licenses
"""

import logging
import re
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
from collections import defaultdict


# Common license patterns
LICENSE_PATTERNS = {
    'MIT': [
        r'MIT License',
        r'Permission is hereby granted, free of charge',
        r'MIT/X11 License'
    ],
    'Apache-2.0': [
        r'Apache License.*Version 2\.0',
        r'Licensed under the Apache License, Version 2\.0'
    ],
    'GPL-3.0': [
        r'GNU GENERAL PUBLIC LICENSE.*Version 3',
        r'This program is free software.*GPL'
    ],
    'GPL-2.0': [
        r'GNU GENERAL PUBLIC LICENSE.*Version 2',
        r'GPL-2\.0'
    ],
    'BSD-3-Clause': [
        r'BSD 3-Clause',
        r'Redistribution and use in source and binary forms.*3 clauses'
    ],
    'BSD-2-Clause': [
        r'BSD 2-Clause',
        r'Redistribution and use in source and binary forms.*2 clauses'
    ],
    'ISC': [
        r'ISC License',
        r'Permission to use, copy, modify.*ISC'
    ],
    'MPL-2.0': [
        r'Mozilla Public License.*Version 2\.0',
        r'MPL-2\.0'
    ],
    'LGPL-3.0': [
        r'GNU LESSER GENERAL PUBLIC LICENSE.*Version 3',
        r'LGPL-3\.0'
    ],
    'LGPL-2.1': [
        r'GNU LESSER GENERAL PUBLIC LICENSE.*Version 2\.1',
        r'LGPL-2\.1'
    ],
    'Unlicense': [
        r'This is free and unencumbered software released into the public domain',
        r'Unlicense'
    ],
    'CC0-1.0': [
        r'Creative Commons.*CC0 1\.0',
        r'Public Domain Dedication'
    ]
}


# License compatibility matrix
# Compatible if project can include dependency
LICENSE_COMPATIBILITY = {
    'MIT': {'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC', 'Unlicense', 'CC0-1.0'},
    'Apache-2.0': {'Apache-2.0', 'MIT', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC', 'Unlicense', 'CC0-1.0'},
    'GPL-3.0': {'GPL-3.0', 'LGPL-3.0', 'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC'},
    'GPL-2.0': {'GPL-2.0', 'LGPL-2.1', 'MIT', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC'},
    'BSD-3-Clause': {'MIT', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC', 'Apache-2.0', 'Unlicense'},
    'BSD-2-Clause': {'MIT', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC', 'Apache-2.0', 'Unlicense'},
    'ISC': {'MIT', 'ISC', 'BSD-3-Clause', 'BSD-2-Clause', 'Apache-2.0', 'Unlicense'},
    'MPL-2.0': {'MPL-2.0', 'MIT', 'BSD-3-Clause', 'Apache-2.0'},
    'LGPL-3.0': {'LGPL-3.0', 'MIT', 'BSD-3-Clause', 'Apache-2.0'},
    'LGPL-2.1': {'LGPL-2.1', 'MIT', 'BSD-3-Clause'},
    'Unlicense': {'Unlicense', 'MIT', 'BSD-3-Clause', 'ISC', 'Apache-2.0', 'CC0-1.0'},
    'CC0-1.0': {'CC0-1.0', 'Unlicense', 'MIT', 'BSD-3-Clause', 'Apache-2.0'}
}


# License categories
LICENSE_CATEGORIES = {
    'permissive': {'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC', 'Unlicense', 'CC0-1.0'},
    'copyleft-strong': {'GPL-3.0', 'GPL-2.0'},
    'copyleft-weak': {'LGPL-3.0', 'LGPL-2.1', 'MPL-2.0'},
    'public-domain': {'Unlicense', 'CC0-1.0'}
}


class LicenseAnalyzer:
    """Analyze and check license compliance."""
    
    def __init__(self, repo_path: str):
        """
        Initialize license analyzer.
        
        Args:
            repo_path: Path to repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.license_analyzer')
    
    def detect_license(self, file_path: Path) -> Optional[str]:
        """
        Detect license from file content.
        
        Args:
            file_path: Path to license file
            
        Returns:
            License identifier or None
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Check against patterns
            for license_name, patterns in LICENSE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                        return license_name
            
            return 'Unknown'
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def find_license_files(self) -> List[Dict[str, Any]]:
        """
        Find license files in repository.
        
        Returns:
            List of license file info
        """
        licenses = []
        
        # Common license file names
        license_names = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'COPYING', 'COPYRIGHT']
        
        for name in license_names:
            for file in self.repo_path.rglob(name):
                if file.is_file():
                    detected = self.detect_license(file)
                    licenses.append({
                        'file': str(file.relative_to(self.repo_path)),
                        'license': detected,
                        'path': str(file)
                    })
        
        return licenses
    
    def get_project_license(self) -> Optional[str]:
        """
        Get main project license.
        
        Returns:
            License identifier or None
        """
        # Check root LICENSE file first
        for name in ['LICENSE', 'LICENSE.txt', 'LICENSE.md']:
            license_file = self.repo_path / name
            if license_file.exists():
                return self.detect_license(license_file)
        
        return None
    
    def check_compatibility(self, project_license: str, dependency_license: str) -> bool:
        """
        Check if dependency license is compatible with project license.
        
        Args:
            project_license: Project's license
            dependency_license: Dependency's license
            
        Returns:
            True if compatible
        """
        if project_license not in LICENSE_COMPATIBILITY:
            return True  # Unknown license, assume compatible
        
        return dependency_license in LICENSE_COMPATIBILITY[project_license]
    
    def analyze_dependencies(self, dependencies: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze license compliance for dependencies.
        
        Args:
            dependencies: List of dependencies with 'name' and 'license' fields
            
        Returns:
            Analysis results
        """
        project_license = self.get_project_license()
        
        analysis = {
            'project_license': project_license,
            'total_dependencies': len(dependencies),
            'compatible': [],
            'incompatible': [],
            'unknown': [],
            'by_category': defaultdict(list)
        }
        
        for dep in dependencies:
            dep_license = dep.get('license', 'Unknown')
            dep_name = dep.get('name', 'Unknown')
            
            if dep_license == 'Unknown':
                analysis['unknown'].append(dep_name)
                continue
            
            # Categorize
            for category, licenses in LICENSE_CATEGORIES.items():
                if dep_license in licenses:
                    analysis['by_category'][category].append(dep_name)
                    break
            
            # Check compatibility
            if project_license:
                if self.check_compatibility(project_license, dep_license):
                    analysis['compatible'].append({
                        'name': dep_name,
                        'license': dep_license
                    })
                else:
                    analysis['incompatible'].append({
                        'name': dep_name,
                        'license': dep_license,
                        'reason': f'{dep_license} not compatible with {project_license}'
                    })
            else:
                # No project license, just list
                analysis['compatible'].append({
                    'name': dep_name,
                    'license': dep_license
                })
        
        return analysis
    
    def generate_compliance_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generate license compliance report.
        
        Args:
            analysis: Analysis results from analyze_dependencies()
            
        Returns:
            Markdown formatted report
        """
        md = []
        md.append("# License Compliance Report\n")
        
        project_license = analysis.get('project_license', 'Unknown')
        md.append(f"**Project License**: {project_license}\n")
        
        total = analysis['total_dependencies']
        md.append(f"**Total Dependencies**: {total}\n")
        
        # Compatibility summary
        md.append("## Summary\n")
        md.append(f"- ✅ Compatible: {len(analysis['compatible'])}")
        md.append(f"- ⚠️ Incompatible: {len(analysis['incompatible'])}")
        md.append(f"- ❓ Unknown: {len(analysis['unknown'])}\n")
        
        # Incompatible licenses (most important)
        if analysis['incompatible']:
            md.append("## ⚠️ Incompatible Licenses\n")
            md.append("These dependencies may have licensing issues:\n")
            md.append("| Dependency | License | Reason |")
            md.append("|------------|---------|--------|")
            for item in analysis['incompatible']:
                md.append(f"| {item['name']} | {item['license']} | {item['reason']} |")
            md.append("")
        
        # Unknown licenses
        if analysis['unknown']:
            md.append("## ❓ Unknown Licenses\n")
            md.append("These dependencies have unknown or undetected licenses:\n")
            for name in analysis['unknown']:
                md.append(f"- {name}")
            md.append("")
        
        # By category
        if analysis['by_category']:
            md.append("## Dependencies by License Category\n")
            for category, deps in sorted(analysis['by_category'].items()):
                if deps:
                    md.append(f"### {category.replace('-', ' ').title()} ({len(deps)})")
                    for dep in sorted(deps)[:10]:
                        md.append(f"- {dep}")
                    if len(deps) > 10:
                        md.append(f"- *... and {len(deps) - 10} more*")
                    md.append("")
        
        # Compatible licenses
        if analysis['compatible']:
            md.append("## ✅ Compatible Licenses\n")
            license_groups = defaultdict(list)
            for item in analysis['compatible']:
                license_groups[item['license']].append(item['name'])
            
            for license_name, deps in sorted(license_groups.items()):
                md.append(f"### {license_name} ({len(deps)})")
                for dep in sorted(deps)[:10]:
                    md.append(f"- {dep}")
                if len(deps) > 10:
                    md.append(f"- *... and {len(deps) - 10} more*")
                md.append("")
        
        # Recommendations
        md.append("## Recommendations\n")
        if analysis['incompatible']:
            md.append("- ⚠️ Review incompatible licenses and consider alternatives")
            md.append("- Consult with legal team about license compliance")
        if analysis['unknown']:
            md.append("- ❓ Investigate dependencies with unknown licenses")
            md.append("- Check package repositories for license information")
        if not analysis['incompatible'] and not analysis['unknown']:
            md.append("- ✅ No licensing issues detected")
        
        md.append("")
        md.append("*Note: This is an automated analysis. Consult with legal professionals for definitive guidance.*")
        
        return '\n'.join(md)
    
    def get_license_info(self, license_name: str) -> Dict[str, Any]:
        """
        Get information about a license.
        
        Args:
            license_name: License identifier
            
        Returns:
            License information
        """
        info = {
            'name': license_name,
            'category': 'unknown',
            'commercial_use': True,
            'distribution': True,
            'modification': True,
            'patent_use': False,
            'private_use': True
        }
        
        # Determine category
        for category, licenses in LICENSE_CATEGORIES.items():
            if license_name in licenses:
                info['category'] = category
                break
        
        # Set specific permissions
        if license_name in ['Apache-2.0']:
            info['patent_use'] = True
        
        if license_name in ['GPL-3.0', 'GPL-2.0']:
            info['same_license'] = True  # Copyleft requirement
        
        return info
