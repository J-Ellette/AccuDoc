"""
Database schema extractor for AccuDoc.

Extracts and documents database schemas from:
- SQL migration files (Django, Rails, Laravel, etc.)
- Schema definition files
- Database dump files
- ORM model definitions
"""

import re
import logging
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from collections import defaultdict


class DatabaseSchemaExtractor:
    """Extracts database schema information from various sources."""
    
    def __init__(self, repo_path: str):
        """
        Initialize schema extractor.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger('accudoc.db_schema')
        
    def find_schema_files(self) -> Dict[str, List[Path]]:
        """
        Find database schema-related files in the repository.
        
        Returns:
            Dictionary mapping schema type to list of files
        """
        schema_files = {
            'sql_migrations': [],
            'django_migrations': [],
            'rails_migrations': [],
            'schema_files': [],
            'models': []
        }
        
        # SQL migration files
        for pattern in ['**/migrations/**/*.sql', '**/migrate/**/*.sql', '**/*migration*.sql']:
            schema_files['sql_migrations'].extend(self.repo_path.glob(pattern))
        
        # Django migrations
        for pattern in ['**/migrations/*.py']:
            files = list(self.repo_path.glob(pattern))
            # Filter out __init__.py
            schema_files['django_migrations'].extend([f for f in files if f.name != '__init__.py'])
        
        # Rails migrations
        for pattern in ['**/db/migrate/*.rb']:
            schema_files['rails_migrations'].extend(self.repo_path.glob(pattern))
        
        # Schema files
        for pattern in ['**/schema.sql', '**/schema.rb', '**/schema.py', '**/database.sql']:
            schema_files['schema_files'].extend(self.repo_path.glob(pattern))
        
        # Model files (Django, SQLAlchemy, ActiveRecord)
        for pattern in ['**/models.py', '**/models/*.py', '**/app/models/*.rb']:
            schema_files['models'].extend(self.repo_path.glob(pattern))
        
        return {k: v for k, v in schema_files.items() if v}
    
    def parse_sql_create_table(self, sql: str) -> List[Dict[str, Any]]:
        """
        Parse CREATE TABLE statements from SQL.
        
        Args:
            sql: SQL content
            
        Returns:
            List of table definitions
        """
        tables = []
        
        # Match CREATE TABLE statements
        pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`"\']?[\w_]+[`"\']?)\s*\((.*?)\);'
        matches = re.finditer(pattern, sql, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            table_name = match.group(1).strip('`"\' ')
            columns_def = match.group(2)
            
            columns = []
            constraints = []
            
            # Parse columns
            for line in columns_def.split(','):
                line = line.strip()
                if not line:
                    continue
                
                # Skip constraints
                if any(kw in line.upper() for kw in ['PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK', 'INDEX']):
                    constraints.append(line)
                    continue
                
                # Parse column definition
                parts = line.split()
                if len(parts) >= 2:
                    col_name = parts[0].strip('`"\' ')
                    col_type = parts[1]
                    
                    # Check for constraints
                    is_primary = 'PRIMARY KEY' in line.upper()
                    is_not_null = 'NOT NULL' in line.upper()
                    is_unique = 'UNIQUE' in line.upper()
                    has_default = 'DEFAULT' in line.upper()
                    
                    columns.append({
                        'name': col_name,
                        'type': col_type,
                        'primary_key': is_primary,
                        'not_null': is_not_null,
                        'unique': is_unique,
                        'has_default': has_default
                    })
            
            tables.append({
                'name': table_name,
                'columns': columns,
                'constraints': constraints
            })
        
        return tables
    
    def parse_django_models(self, python_file: Path) -> List[Dict[str, Any]]:
        """
        Parse Django model definitions.
        
        Args:
            python_file: Path to Django models.py file
            
        Returns:
            List of model definitions
        """
        try:
            with open(python_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            models = []
            
            # Match class definitions that inherit from models.Model
            pattern = r'class\s+(\w+)\s*\((.*?models\.Model.*?)\):\s*(.*?)(?=\n(?:class|\Z))'
            matches = re.finditer(pattern, content, re.DOTALL)
            
            for match in matches:
                model_name = match.group(1)
                model_body = match.group(3)
                
                # Parse fields
                fields = []
                field_pattern = r'(\w+)\s*=\s*models\.(\w+)\((.*?)\)'
                field_matches = re.finditer(field_pattern, model_body)
                
                for field_match in field_matches:
                    field_name = field_match.group(1)
                    field_type = field_match.group(2)
                    field_args = field_match.group(3)
                    
                    # Parse field attributes
                    is_primary = 'primary_key=True' in field_args
                    is_nullable = 'null=True' in field_args
                    is_unique = 'unique=True' in field_args
                    
                    fields.append({
                        'name': field_name,
                        'type': field_type,
                        'primary_key': is_primary,
                        'nullable': is_nullable,
                        'unique': is_unique
                    })
                
                if fields:  # Only add if we found fields
                    models.append({
                        'name': model_name,
                        'fields': fields,
                        'type': 'django_model'
                    })
            
            return models
            
        except Exception as e:
            self.logger.error(f"Error parsing Django models from {python_file}: {e}")
            return []
    
    def extract_schema(self) -> Dict[str, Any]:
        """
        Extract database schema from the repository.
        
        Returns:
            Comprehensive schema information
        """
        schema_files = self.find_schema_files()
        
        if not schema_files:
            return {'status': 'no_schema', 'message': 'No database schema files found'}
        
        schema = {
            'status': 'success',
            'tables': [],
            'models': [],
            'source_files': []
        }
        
        # Parse SQL migration files
        for file in schema_files.get('sql_migrations', []):
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    sql = f.read()
                
                tables = self.parse_sql_create_table(sql)
                for table in tables:
                    table['source'] = str(file)
                    table['type'] = 'sql'
                schema['tables'].extend(tables)
                schema['source_files'].append(str(file))
                
            except Exception as e:
                self.logger.error(f"Error parsing SQL file {file}: {e}")
        
        # Parse schema files
        for file in schema_files.get('schema_files', []):
            if file.suffix == '.sql':
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        sql = f.read()
                    
                    tables = self.parse_sql_create_table(sql)
                    for table in tables:
                        table['source'] = str(file)
                        table['type'] = 'schema'
                    schema['tables'].extend(tables)
                    schema['source_files'].append(str(file))
                    
                except Exception as e:
                    self.logger.error(f"Error parsing schema file {file}: {e}")
        
        # Parse Django models
        for file in schema_files.get('django_migrations', []) + schema_files.get('models', []):
            if file.suffix == '.py':
                models = self.parse_django_models(file)
                for model in models:
                    model['source'] = str(file)
                schema['models'].extend(models)
                if models:
                    schema['source_files'].append(str(file))
        
        # Remove duplicates
        schema['source_files'] = list(set(schema['source_files']))
        
        return schema
    
    def generate_schema_documentation(self, schema: Dict[str, Any]) -> str:
        """
        Generate markdown documentation from schema.
        
        Args:
            schema: Schema data from extract_schema()
            
        Returns:
            Markdown formatted documentation
        """
        if schema.get('status') == 'no_schema':
            return "# Database Schema\n\nNo database schema information found."
        
        md = []
        md.append("# Database Schema Documentation\n")
        
        total_tables = len(schema.get('tables', []))
        total_models = len(schema.get('models', []))
        
        if total_tables > 0 or total_models > 0:
            md.append("## Overview\n")
            if total_tables > 0:
                md.append(f"- **SQL Tables**: {total_tables}")
            if total_models > 0:
                md.append(f"- **ORM Models**: {total_models}")
            md.append(f"- **Source Files**: {len(schema.get('source_files', []))}\n")
        
        # Document SQL tables
        if schema.get('tables'):
            md.append("## Tables\n")
            
            for table in schema['tables']:
                md.append(f"### {table['name']}\n")
                
                if 'source' in table:
                    source_file = Path(table['source']).name
                    md.append(f"*Source: {source_file}*\n")
                
                if table.get('columns'):
                    md.append("| Column | Type | Constraints |")
                    md.append("|--------|------|-------------|")
                    
                    for col in table['columns']:
                        constraints = []
                        if col.get('primary_key'):
                            constraints.append('PRIMARY KEY')
                        if col.get('not_null'):
                            constraints.append('NOT NULL')
                        if col.get('unique'):
                            constraints.append('UNIQUE')
                        if col.get('has_default'):
                            constraints.append('DEFAULT')
                        
                        constraint_str = ', '.join(constraints) if constraints else '-'
                        md.append(f"| {col['name']} | {col['type']} | {constraint_str} |")
                    
                    md.append("")
                
                if table.get('constraints'):
                    md.append("**Additional Constraints:**")
                    for constraint in table['constraints'][:5]:  # Limit to first 5
                        md.append(f"- {constraint.strip()}")
                    md.append("")
        
        # Document ORM models
        if schema.get('models'):
            md.append("## ORM Models\n")
            
            for model in schema['models']:
                md.append(f"### {model['name']}\n")
                
                if 'source' in model:
                    source_file = Path(model['source']).name
                    md.append(f"*Source: {source_file}*")
                    md.append(f"*Type: {model.get('type', 'unknown')}*\n")
                
                if model.get('fields'):
                    md.append("| Field | Type | Attributes |")
                    md.append("|-------|------|------------|")
                    
                    for field in model['fields']:
                        attributes = []
                        if field.get('primary_key'):
                            attributes.append('PK')
                        if field.get('nullable'):
                            attributes.append('Nullable')
                        if field.get('unique'):
                            attributes.append('Unique')
                        
                        attr_str = ', '.join(attributes) if attributes else '-'
                        md.append(f"| {field['name']} | {field['type']} | {attr_str} |")
                    
                    md.append("")
        
        # Add entity relationship notes
        if total_tables > 0 or total_models > 0:
            md.append("## Notes\n")
            md.append("- This schema was automatically extracted from source files")
            md.append("- Relationships and foreign keys may not be fully captured")
            md.append("- Refer to source files for complete schema definition")
            md.append("- Consider using database diagram tools for visual representation\n")
        
        return '\n'.join(md)
