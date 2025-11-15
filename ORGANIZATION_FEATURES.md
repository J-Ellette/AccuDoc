# Organization-wide Features Documentation

This document describes the organization-wide features implemented in AccuDoc for enterprise and team collaboration.

## Table of Contents

1. [Organization-wide Glossary & Style Standardization](#1-organization-wide-glossary--style-standardization)
2. [Onboarding and Training Path Generator](#2-onboarding-and-training-path-generator)
3. [Granular Document Sharing Controls](#3-granular-document-sharing-controls)
4. [Microservice Doc API Endpoints](#4-microservice-doc-api-endpoints)
5. [License and Copyright Management Toolkit](#5-license-and-copyright-management-toolkit)

---

## 1. Organization-wide Glossary & Style Standardization

Maintain and enforce terminology and language conventions across all documentation projects.

### Features

- **Glossary Management**: Define preferred terms, aliases, and deprecated terms
- **Style Rules**: Create custom style rules with regex patterns
- **Violation Detection**: Automatically scan documentation for violations
- **Organization Isolation**: Support multiple organizations with separate glossaries
- **Severity Levels**: Categorize violations as error, warning, or info
- **Detailed Reporting**: Generate reports with line numbers and context
- **Database Persistence**: All terms and scans stored in SQLite

### CLI Usage

```bash
# Add a glossary term
accudoc glossary add "API" "Application Programming Interface" \
  "Use the REST API" --deprecated "web service" --category "technical"

# List glossary terms
accudoc glossary list --org-id org123

# Scan documentation for violations
accudoc glossary scan ./docs --org-id org123 -o violations.md
```

### Python API

```python
from accudoc.glossary import GlossaryManager

manager = GlossaryManager()

# Add term
term = manager.add_term(
    term='API',
    definition='Application Programming Interface',
    preferred_usage='Use REST API for...',
    deprecated_terms=['web service'],
    category='technical',
    organization_id='org123'
)

# Scan content
violations = manager.scan_content(content, organization_id='org123')

# Generate report
report = manager.generate_report(violations, '/path/to/repo')
```

### REST API

```bash
# Add glossary term
curl -X POST http://localhost:5000/api/glossary/terms \
  -H 'Content-Type: application/json' \
  -H 'X-API-Token: your-token' \
  -d '{
    "term": "API",
    "definition": "Application Programming Interface",
    "preferred_usage": "Use REST API",
    "organization_id": "org123"
  }'

# Scan content
curl -X POST http://localhost:5000/api/glossary/scan \
  -H 'Content-Type: application/json' \
  -d '{
    "content": "Documentation text...",
    "organization_id": "org123"
  }'
```

---

## 2. Onboarding and Training Path Generator

Automatically generate customized onboarding guides and interactive checklists for new contributors.

### Features

- **Automatic Analysis**: Analyze repository structure to generate relevant steps
- **Language Detection**: Customize onboarding based on detected languages
- **Dependency Installation**: Include setup steps for all package managers
- **Documentation Links**: Reference existing documentation files
- **Progress Tracking**: Track user progress through checklist
- **Multiple Formats**: Export as markdown, interactive checklist, or JSON
- **Time Estimates**: Provide estimated completion times

### CLI Usage

```bash
# Create onboarding checklist
accudoc onboarding create /path/to/repo -o ONBOARDING.md

# Create interactive checklist
accudoc onboarding create /path/to/repo --format checklist -o CHECKLIST.md

# Get existing checklist
accudoc onboarding get checklist_abc123 -o guide.md

# Assign to user
accudoc onboarding assign checklist_abc123 user456

# Update progress
accudoc onboarding progress progress_xyz789 step_1
```

### Python API

```python
from accudoc.onboarding_generator import OnboardingGenerator
from accudoc.scanner import RepositoryScanner

generator = OnboardingGenerator()

# Scan repository
scanner = RepositoryScanner('/path/to/repo')
repo_info = scanner.scan()

# Create checklist
checklist = generator.create_checklist(
    repository_path='/path/to/repo',
    repo_info=repo_info,
    title='Custom Onboarding Guide',
    organization_id='org123'
)

# Generate markdown guide
markdown = generator.generate_markdown_guide(checklist)

# Assign to user
progress = generator.assign_checklist(checklist.checklist_id, 'user456')

# Update progress
updated = generator.update_progress(progress.progress_id, 'step_1')
```

### REST API

```bash
# Create checklist
curl -X POST http://localhost:5000/api/onboarding/checklists \
  -H 'Content-Type: application/json' \
  -H 'X-API-Token: your-token' \
  -d '{
    "repository_path": "/path/to/repo",
    "repo_info": {...},
    "title": "Onboarding Guide"
  }'

# Get checklist
curl http://localhost:5000/api/onboarding/checklists/checklist_abc123

# Get as markdown
curl http://localhost:5000/api/onboarding/checklists/checklist_abc123/markdown
```

---

## 3. Granular Document Sharing Controls

Share documentation sections securely with external parties with fine-grained access controls.

### Features

- **Section Sharing**: Share specific sections, not entire documents
- **Expiring Access**: Set automatic expiration dates
- **Watermarking**: Add watermarks to shared content
- **Download Limits**: Restrict number of downloads
- **Access Tracking**: Complete audit trail of all access
- **IP Logging**: Track access by IP address
- **Revocation**: Instantly revoke access to shared documents
- **Secure Tokens**: Cryptographically secure access tokens

### CLI Usage

```bash
# Share document section
accudoc share create /docs/api.md --section auth \
  --title "Authentication Guide" --expires 7 \
  --watermark --limit 10 --user-id user123

# List shares
accudoc share list --user-id user123

# Revoke share
accudoc share revoke share_abc123 --user-id user123
```

### Python API

```python
from accudoc.document_sharing import DocumentSharingManager

manager = DocumentSharingManager()

# Share document
shared = manager.share_document_section(
    document_path='/docs/api.md',
    content='# API Documentation\n...',
    shared_by='user123',
    section_title='Authentication Guide',
    expires_in_days=7,
    watermark=True,
    download_limit=10
)

# Access shared document
doc = manager.get_shared_document(
    shared.access_token,
    ip_address='192.168.1.1'
)

# Record download
manager.record_download(shared.share_id)

# Get access log
log = manager.get_access_log(shared.share_id)

# Revoke
manager.revoke_share(shared.share_id, 'user123')
```

### REST API

```bash
# Share document
curl -X POST http://localhost:5000/api/sharing/share \
  -H 'Content-Type: application/json' \
  -H 'X-API-Token: your-token' \
  -d '{
    "document_path": "/docs/api.md",
    "content": "# API Documentation...",
    "section_title": "Authentication Guide",
    "expires_in_days": 7,
    "watermark": true,
    "download_limit": 10
  }'

# Access shared document (no auth required)
curl http://localhost:5000/api/sharing/access/TOKEN

# Revoke share
curl -X POST http://localhost:5000/api/sharing/shares/share_abc123/revoke \
  -H 'X-API-Token: your-token'
```

---

## 4. Microservice Doc API Endpoints

Expose documentation sections as microservice endpoints with role-based access and rate limiting.

### Features

- **RESTful API**: Clean JSON API for all features
- **Rate Limiting**: 60 requests per minute per client (configurable)
- **Role-Based Access**: Integration with membership system
- **Permission Checks**: Fine-grained permission validation
- **Usage Auditing**: Complete audit trail of API usage
- **Token Authentication**: API token-based authentication
- **CORS Enabled**: Ready for web applications
- **OpenAPI Documentation**: Built-in API specification

### Authentication

All authenticated endpoints require an API token in the `X-API-Token` header:

```bash
curl -X POST http://localhost:5000/api/user/login \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

Response includes API token for use in subsequent requests.

### Rate Limiting

- Default: 60 requests per minute per client
- Client identified by API token or IP address
- Returns 429 status code when limit exceeded

### Available Endpoints

**Glossary Management:**
- `GET /api/glossary/terms` - List glossary terms
- `POST /api/glossary/terms` - Add glossary term
- `POST /api/glossary/scan` - Scan content for violations

**Onboarding:**
- `POST /api/onboarding/checklists` - Create checklist
- `GET /api/onboarding/checklists/:id` - Get checklist
- `GET /api/onboarding/checklists/:id/markdown` - Get as markdown

**Document Sharing:**
- `POST /api/sharing/share` - Share document
- `GET /api/sharing/access/:token` - Access shared document
- `POST /api/sharing/shares/:id/revoke` - Revoke share

**License Management:**
- `POST /api/license/headers` - Create copyright header
- `POST /api/license/headers/:id/apply` - Apply headers
- `POST /api/license/compliance` - Check compliance
- `POST /api/license/attributions` - Add attribution
- `GET /api/license/attributions/file` - Generate attribution file

---

## 5. License and Copyright Management Toolkit

Bulk management of license notices, copyright headers, and attribution information.

### Features

- **Copyright Headers**: Generate and apply copyright headers
- **Multiple Licenses**: Support for MIT, Apache-2.0, GPL, BSD, and more
- **Bulk Application**: Apply headers to entire repositories
- **Header Scanning**: Detect existing headers
- **Attribution Management**: Track third-party components
- **Attribution File Generation**: Auto-generate THIRD_PARTY_LICENSES
- **Compliance Checking**: Check license compliance status
- **Coverage Reporting**: Track header coverage percentage

### CLI Usage

```bash
# Create copyright header
accudoc license header "Acme Corp" "2024" "MIT" \
  --patterns "*.py,*.js"

# Apply headers to repository
accudoc license apply /path/to/repo header_abc123

# Scan for headers
accudoc license scan /path/to/repo -o scan_report.txt

# Add attribution
accudoc license attribution "Flask" "Pallets" "BSD-3-Clause" \
  --url "https://flask.palletsprojects.com"

# Generate attribution file
accudoc license attribution-file -o THIRD_PARTY_LICENSES.md

# Check compliance
accudoc license check /path/to/repo -o compliance.txt
```

### Python API

```python
from accudoc.license_management import LicenseManagementToolkit

manager = LicenseManagementToolkit()

# Create header
header = manager.create_copyright_header(
    organization='Acme Corp',
    year='2024',
    license_type='MIT',
    file_patterns=['*.py', '*.js']
)

# Apply to repository
results = manager.bulk_apply_headers('/path/to/repo', header.header_id)

# Scan for headers
scan_results = manager.scan_for_headers('/path/to/repo')

# Add attribution
attr = manager.add_attribution(
    component_name='Flask',
    author='Pallets',
    license='BSD-3-Clause',
    source_url='https://flask.palletsprojects.com'
)

# Generate attribution file
content = manager.generate_attribution_file()

# Check compliance
compliance = manager.check_license_compliance('/path/to/repo')
```

### REST API

```bash
# Create copyright header
curl -X POST http://localhost:5000/api/license/headers \
  -H 'Content-Type: application/json' \
  -H 'X-API-Token: your-token' \
  -d '{
    "organization": "Acme Corp",
    "year": "2024",
    "license_type": "MIT",
    "organization_id": "org123"
  }'

# Apply headers
curl -X POST http://localhost:5000/api/license/headers/header_abc123/apply \
  -H 'Content-Type: application/json' \
  -H 'X-API-Token: your-token' \
  -d '{"repository_path": "/path/to/repo"}'

# Check compliance
curl -X POST http://localhost:5000/api/license/compliance \
  -H 'Content-Type: application/json' \
  -d '{"repository_path": "/path/to/repo"}'
```

---

## Integration with Membership System

All features integrate with AccuDoc's membership system for access control:

### Roles

- **Owner**: Full access to all features
- **Admin**: Can manage terms, rules, and shares
- **Editor**: Can create and edit content
- **Viewer**: Read-only access

### Permissions

- `READ`: View glossary terms, checklists, etc.
- `WRITE`: Create and modify content
- `COMMENT`: Add comments and suggestions
- `MANAGE_USERS`: Manage team members
- `DELETE`: Delete content

### Usage

```python
from accudoc.membership import MembershipManager, Permission

# Initialize with membership
membership_mgr = MembershipManager()

# Create user
user = membership_mgr.create_user(
    username='john_doe',
    email='john@example.com',
    password='secure_password',
    role=Role.EDITOR
)

# Check permission
has_permission = membership_mgr.check_permission(
    user_id=user.user_id,
    project_id='org123',
    permission=Permission.WRITE
)
```

---

## Database Schema

All features use SQLite for persistence:

- **Glossary**: `~/.accudoc/glossary.db`
- **Onboarding**: `~/.accudoc/onboarding.db`
- **Sharing**: `~/.accudoc/document_sharing.db`
- **License**: `~/.accudoc/license_management.db`
- **Membership**: `~/.accudoc/membership.db`

---

## Complete Example

Here's a complete workflow using all features:

```python
from accudoc.glossary import GlossaryManager
from accudoc.onboarding_generator import OnboardingGenerator
from accudoc.document_sharing import DocumentSharingManager
from accudoc.license_management import LicenseManagementToolkit
from accudoc.scanner import RepositoryScanner

# 1. Set up glossary
glossary = GlossaryManager()
glossary.add_term('API', 'Application Programming Interface', 'Use REST API')

# 2. Generate onboarding guide
scanner = RepositoryScanner('/path/to/repo')
repo_info = scanner.scan()

onboarding = OnboardingGenerator()
checklist = onboarding.create_checklist('/path/to/repo', repo_info)
guide = onboarding.generate_markdown_guide(checklist)

# 3. Share onboarding guide securely
sharing = DocumentSharingManager()
shared = sharing.share_document_section(
    document_path='ONBOARDING.md',
    content=guide,
    shared_by='admin',
    expires_in_days=30
)

# 4. Apply copyright headers
license_mgr = LicenseManagementToolkit()
header = license_mgr.create_copyright_header('Acme Corp', '2024', 'MIT')
results = license_mgr.bulk_apply_headers('/path/to/repo', header.header_id)

print(f"Onboarding guide shared: {shared.access_token}")
print(f"Copyright headers applied to {results['headers_added']} files")
```

---

## Testing

Run tests with:

```bash
python -m unittest test_organization_features -v
```

All 17 tests should pass.

---

## Demo

Run the comprehensive demo:

```bash
python demo_organization_features.py
```

This demonstrates all features working together.
