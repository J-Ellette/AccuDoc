"""
AccuDoc - Automated Repository Documentation Generator

A Python library for automatically generating comprehensive documentation
from code repositories.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="accudoc",
    version="1.0.0",
    author="AccuDoc Contributors",
    author_email="",
    description="Automated Repository Documentation Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jamesellette/AccuDoc",
    packages=find_packages(exclude=["tests", "tests.*", "demo_*", "test_*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No required dependencies - uses Python standard library
    ],
    extras_require={
        "gui": [
            "tkinterdnd2>=0.3.0",
            "tkinterweb>=3.0.0",
            "tkhtmlview>=0.1.0",
            "markdown>=3.0.0",
        ],
        "api": [
            "flask>=2.0.0",
            "flask-cors>=3.0.0",
        ],
        "pdf": [
            "weasyprint>=52.0",
        ],
        "scheduler": [
            "schedule>=1.1.0",
        ],
        "email": [
            "secure-smtplib>=0.1.1",
        ],
        "testbed": [
            "docker>=6.0.0",
        ],
        "all": [
            "tkinterdnd2>=0.3.0",
            "tkinterweb>=3.0.0",
            "tkhtmlview>=0.1.0",
            "markdown>=3.0.0",
            "flask>=2.0.0",
            "flask-cors>=3.0.0",
            "weasyprint>=52.0",
            "schedule>=1.1.0",
            "docker>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "accudoc=accudoc_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "accudoc": [
            "translations/*.json",
            "templates/*.json",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/jamesellette/AccuDoc/issues",
        "Source": "https://github.com/jamesellette/AccuDoc",
        "Documentation": "https://github.com/jamesellette/AccuDoc/blob/main/README.md",
    },
)
