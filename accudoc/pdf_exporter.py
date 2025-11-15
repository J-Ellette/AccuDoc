"""
PDF export module for AccuDoc.

Provides PDF export functionality using HTML as an intermediate format.
For best results, requires wkhtmltopdf or weasyprint to be installed.
Falls back to basic PDF generation if neither is available.
"""

import subprocess
import logging
import tempfile
from pathlib import Path
from typing import Optional
import shutil


class PDFExporter:
    """Export documentation to PDF format."""
    
    def __init__(self):
        """Initialize PDF exporter."""
        self.logger = logging.getLogger('accudoc.pdf')
        self.has_wkhtmltopdf = self._check_wkhtmltopdf()
        self.has_weasyprint = self._check_weasyprint()
        
    def _check_wkhtmltopdf(self) -> bool:
        """Check if wkhtmltopdf is available."""
        try:
            result = subprocess.run(
                ['wkhtmltopdf', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_weasyprint(self) -> bool:
        """Check if weasyprint is available."""
        try:
            import weasyprint
            return True
        except ImportError:
            return False
    
    def export_to_pdf(self, html_content: str, output_path: Path,
                      title: str = "Documentation") -> Path:
        """
        Export HTML content to PDF.
        
        Args:
            html_content: HTML content to convert
            output_path: Output PDF file path
            title: Document title
            
        Returns:
            Path to generated PDF file
        """
        # Try methods in order of preference
        if self.has_weasyprint:
            return self._export_with_weasyprint(html_content, output_path, title)
        elif self.has_wkhtmltopdf:
            return self._export_with_wkhtmltopdf(html_content, output_path)
        else:
            # Fallback: Create a guide for installing dependencies
            return self._create_installation_guide(output_path)
    
    def _export_with_weasyprint(self, html_content: str, output_path: Path,
                                title: str) -> Path:
        """Export using WeasyPrint."""
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # Add PDF-specific styling
            pdf_css = CSS(string="""
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-family: 'DejaVu Sans', 'Arial', sans-serif;
                    font-size: 10pt;
                    line-height: 1.5;
                }
                h1 {
                    page-break-before: always;
                    font-size: 24pt;
                    margin-top: 0;
                }
                h1:first-of-type {
                    page-break-before: auto;
                }
                h2 {
                    font-size: 18pt;
                    page-break-after: avoid;
                }
                h3 {
                    font-size: 14pt;
                }
                pre, code {
                    font-family: 'Courier New', monospace;
                    background-color: #f5f5f5;
                    padding: 0.5em;
                    border: 1px solid #ddd;
                    page-break-inside: avoid;
                }
                table {
                    page-break-inside: avoid;
                }
            """)
            
            font_config = FontConfiguration()
            html_obj = HTML(string=html_content)
            html_obj.write_pdf(
                output_path,
                stylesheets=[pdf_css],
                font_config=font_config
            )
            
            self.logger.info(f"PDF exported successfully using WeasyPrint: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"WeasyPrint export failed: {str(e)}")
            raise
    
    def _export_with_wkhtmltopdf(self, html_content: str, output_path: Path) -> Path:
        """Export using wkhtmltopdf."""
        try:
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_html:
                temp_html.write(html_content)
                temp_html_path = temp_html.name
            
            try:
                # Run wkhtmltopdf
                subprocess.run(
                    [
                        'wkhtmltopdf',
                        '--page-size', 'A4',
                        '--margin-top', '20mm',
                        '--margin-bottom', '20mm',
                        '--margin-left', '20mm',
                        '--margin-right', '20mm',
                        '--encoding', 'UTF-8',
                        '--enable-local-file-access',
                        temp_html_path,
                        str(output_path)
                    ],
                    check=True,
                    capture_output=True,
                    timeout=60
                )
                
                self.logger.info(f"PDF exported successfully using wkhtmltopdf: {output_path}")
                return output_path
                
            finally:
                # Clean up temp file
                Path(temp_html_path).unlink(missing_ok=True)
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"wkhtmltopdf export failed: {e.stderr.decode()}")
            raise
        except Exception as e:
            self.logger.error(f"wkhtmltopdf export failed: {str(e)}")
            raise
    
    def _create_installation_guide(self, output_path: Path) -> Path:
        """Create a text file with installation instructions."""
        guide = """
AccuDoc PDF Export - Installation Required

To export documentation to PDF format, please install one of the following:

Option 1: WeasyPrint (Recommended)
-----------------------------------
pip install weasyprint

WeasyPrint is a Python library that converts HTML/CSS to PDF.
It provides high-quality output and is easy to install.

Option 2: wkhtmltopdf
---------------------
Install wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html

For Ubuntu/Debian:
  sudo apt-get install wkhtmltopdf

For macOS:
  brew install wkhtmltopdf

For Windows:
  Download installer from wkhtmltopdf.org

After Installation
------------------
Once installed, re-run your export command:
  python accudoc_cli.py export /repo -o docs.pdf --format pdf

For more information, visit:
  https://github.com/jamesellette/AccuDoc
"""
        
        # Write guide to a text file instead of PDF
        guide_path = output_path.with_suffix('.txt')
        guide_path.write_text(guide)
        
        self.logger.warning(
            f"PDF export requires additional dependencies. "
            f"Installation guide created: {guide_path}"
        )
        
        print(f"\n⚠️  PDF export requires additional dependencies.")
        print(f"   Installation guide created: {guide_path}")
        print(f"\n   Quick install: pip install weasyprint")
        
        return guide_path
    
    def is_available(self) -> bool:
        """Check if PDF export is available."""
        return self.has_weasyprint or self.has_wkhtmltopdf
    
    def get_available_method(self) -> Optional[str]:
        """Get the available PDF export method."""
        if self.has_weasyprint:
            return "weasyprint"
        elif self.has_wkhtmltopdf:
            return "wkhtmltopdf"
        else:
            return None


def export_to_pdf(html_content: str, output_path: Path, 
                 title: str = "Documentation") -> Path:
    """
    Convenience function to export HTML to PDF.
    
    Args:
        html_content: HTML content to convert
        output_path: Output PDF file path
        title: Document title
        
    Returns:
        Path to generated file (PDF if successful, guide if dependencies missing)
    """
    exporter = PDFExporter()
    return exporter.export_to_pdf(html_content, output_path, title)
