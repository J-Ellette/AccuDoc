# Compliance Mapping & Gap Analysis

AccuDoc now includes powerful regulatory compliance mapping and gap analysis features to help organizations track documentation coverage against specific regulatory requirements such as SOC2, HIPAA, GDPR, ISO 27001, and PCI DSS.

## Overview

The compliance mapping feature allows you to:

- **Map Documentation to Requirements**: Link documentation sections to specific regulatory requirements
- **Track Coverage**: Monitor which requirements are covered, partially covered, or not covered
- **Gap Analysis**: Automatically identify missing or incomplete compliance documentation
- **Generate Reports**: Create comprehensive compliance reports in multiple formats
- **Dashboard Integration**: View compliance status across multiple repositories
- **Permission Management**: Control access using the integrated membership system

## Supported Frameworks

AccuDoc currently supports the following compliance frameworks:

| Framework | Requirements | Description |
|-----------|--------------|-------------|
| **SOC2** | 5 controls | SOC2 Type II Trust Service Criteria |
| **HIPAA** | 5 safeguards | HIPAA Security Rule requirements |
| **GDPR** | 5 articles | EU General Data Protection Regulation |
| **ISO 27001** | 5 controls | Information Security Management System |
| **PCI DSS** | 4 requirements | Payment Card Industry Data Security Standard |

Additional frameworks (CCPA, NIST, FedRAMP) are available for future expansion.

## CLI Usage

### List Available Frameworks

View all supported compliance frameworks and their requirements:

```bash
# List all frameworks
python accudoc_cli.py compliance frameworks

# View specific framework requirements
python accudoc_cli.py compliance frameworks -f soc2
python accudoc_cli.py compliance frameworks -f hipaa --json
```

Example output:
```
======================================================================
FRAMEWORK: SOC2
======================================================================

Total requirements: 5

1. SOC2-CC1.1: Organizational Structure
   Category: Control Environment
   Mandatory: Yes
   Control Objectives:
     - Document organizational structure
     - Define roles and responsibilities

2. SOC2-CC2.1: Information Quality
   Category: Communication and Information
   Mandatory: Yes
   Control Objectives:
     - Document data handling
     - Quality assurance processes
...
```

### Create Compliance Mappings

Map documentation sections to regulatory requirements:

```bash
# Basic mapping
python accudoc_cli.py compliance map /path/to/repo SOC2-CC1.1 "README.md#Security" -f soc2

# With additional details
python accudoc_cli.py compliance map /path/to/repo HIPAA-164.308 "SECURITY.md#Access" \
    -f hipaa \
    -p SECURITY.md \
    -s covered \
    -n "Access control policies documented" \
    -e "SECURITY.md,ACCESS_POLICY.md"

# With partial coverage
python accudoc_cli.py compliance map /path/to/repo GDPR-Art30 "docs/privacy.md" \
    -f gdpr \
    -s partial \
    -n "Processing records partially documented"
```

Parameters:
- `repository`: Path to repository
- `requirement_id`: Regulatory requirement ID (e.g., SOC2-CC1.1)
- `doc_section`: Documentation section identifier
- `-f, --framework`: Compliance framework (required)
- `-p, --doc-path`: Path to documentation file
- `-s, --status`: Coverage status (covered, partial, not_covered, not_applicable)
- `-n, --notes`: Additional notes
- `-e, --evidence`: Comma-separated evidence files
- `--use-auth`: Enable membership authentication
- `-u, --user`: User ID for authentication

### List Mappings

View all compliance mappings for a repository:

```bash
# List all mappings
python accudoc_cli.py compliance list /path/to/repo

# Filter by framework
python accudoc_cli.py compliance list /path/to/repo -f soc2

# JSON output
python accudoc_cli.py compliance list /path/to/repo --json
```

Example output:
```
======================================================================
COMPLIANCE MAPPINGS
======================================================================

1. SOC2-CC1.1
   Framework: soc2
   Documentation: README.md#Security
   Status: covered
   Created: 2025-11-15T15:05:33.891051
   Notes: Security section covers organizational structure

2. SOC2-CC6.1
   Framework: soc2
   Documentation: SECURITY.md#Access Control
   Status: covered
   Created: 2025-11-15T15:05:35.123456
```

### Perform Gap Analysis

Analyze compliance gaps and identify missing documentation:

```bash
# Basic gap analysis
python accudoc_cli.py compliance analyze /path/to/repo -f soc2

# JSON output for automation
python accudoc_cli.py compliance analyze /path/to/repo -f hipaa --json
```

Example output:
```
Analyzing compliance gaps for SOC2...

======================================================================
COMPLIANCE GAPS: SOC2
======================================================================

Total gaps: 3
  Critical: 3
  High: 0
  Medium: 0
  Low: 0

1. SOC2-CC2.1: Information Quality
   Category: Communication and Information
   Severity: CRITICAL
   Status: not_covered
   Recommendations:
     - Create documentation for Information Quality
     - Map relevant documentation sections to requirement SOC2-CC2.1
     - Review and implement required controls

2. SOC2-CC3.1: Risk Identification
   Category: Risk Assessment
   Severity: CRITICAL
   Status: not_covered
   Recommendations:
     - Create documentation for Risk Identification
     - Map relevant documentation sections to requirement SOC2-CC3.1
     - Review and implement required controls
...
```

Gap severity levels:
- **CRITICAL**: Mandatory requirement not covered
- **HIGH**: Mandatory requirement partially covered
- **MEDIUM**: Important but non-mandatory requirement not covered
- **LOW**: Optional requirement with partial coverage

### Generate Compliance Reports

Create comprehensive compliance reports:

```bash
# Text report (default)
python accudoc_cli.py compliance report /path/to/repo -f soc2

# Markdown report
python accudoc_cli.py compliance report /path/to/repo -f gdpr \
    --format markdown -o compliance_report.md

# HTML report
python accudoc_cli.py compliance report /path/to/repo -f iso27001 \
    --format html -o compliance_report.html

# JSON for automation
python accudoc_cli.py compliance report /path/to/repo -f hipaa \
    --format json -o compliance_data.json
```

Report contents include:
- **Coverage Summary**: Total requirements, covered count, coverage percentage
- **Compliance Gaps**: Detailed list of gaps with severity and recommendations
- **Category Breakdown**: Coverage by requirement category
- **Mapping Details**: All current documentation mappings

## Dashboard Integration

The compliance mapping feature is fully integrated with AccuDoc's multi-repository dashboard.

### Viewing Compliance in Dashboard

When generating a multi-repo dashboard, compliance information is automatically included if mappings exist:

```bash
# Generate dashboard with compliance data
python accudoc_cli.py dashboard /path/to/repo1 /path/to/repo2 -o dashboard.md
```

The dashboard will include:

1. **Repository Details Section**: Shows compliance status for each repository
   ```
   Secure Application
     Path: /path/to/repo
     Coverage: 42.9% (3 files)
     Completeness: 16.0% (Grade: F)
     Style Compliance: 40.0%
     Regulatory Compliance:
       SOC2: 40.0% (2/5 requirements)
         Critical gaps: 3
       HIPAA: 40.0% (2/5 requirements)
         Critical gaps: 2
   ```

2. **Compliance Status Section**: Detailed compliance breakdown
   ```markdown
   ## Regulatory Compliance Status
   
   ### Secure Application
   
   **SOC2**
   - Coverage: 40.0% (2/5 requirements)
   - Gaps: 3 total (3 critical, 0 high)
   - ⚠️ Action required: 3 critical gaps need immediate attention
   
   **HIPAA**
   - Coverage: 40.0% (2/5 requirements)
   - Gaps: 3 total (2 critical, 1 high)
   ```

### Example Dashboard Output

When viewing a dashboard with compliance data:

```markdown
# Multi-Repository Documentation Consistency Dashboard

## Organization-Wide Summary

### Documentation Coverage
- **Average:** 35.7%
- **Range:** 28.6% - 42.9%

### Regulatory Compliance Status

#### Secure Application

**SOC2**
- Coverage: 40.0% (2/5 requirements)
- Gaps: 3 total (3 critical, 0 high)
- ⚠️ Action required: 3 critical gaps need immediate attention

**HIPAA**
- Coverage: 40.0% (2/5 requirements)
- Gaps: 3 total (2 critical, 1 high)

#### Basic Application
- No compliance mappings configured
```

## Database Schema

Compliance data is stored in three tables:

### compliance_frameworks

```sql
CREATE TABLE compliance_frameworks (
    framework_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT,
    description TEXT,
    enabled BOOLEAN DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### compliance_mappings

```sql
CREATE TABLE compliance_mappings (
    mapping_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    framework TEXT NOT NULL,
    doc_section TEXT NOT NULL,
    doc_path TEXT,
    coverage_status TEXT NOT NULL,  -- covered, partial, not_covered, not_applicable
    notes TEXT,
    evidence TEXT,  -- JSON array of evidence files
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

### compliance_gaps

```sql
CREATE TABLE compliance_gaps (
    gap_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    framework TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,  -- critical, high, medium, low
    current_status TEXT NOT NULL,
    recommendations TEXT,  -- JSON array
    affected_controls TEXT,  -- JSON array
    detected_at TEXT NOT NULL,
    resolved_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

## Programmatic Usage

You can use the compliance mapping feature programmatically in Python:

```python
from accudoc.compliance_mapping import (
    ComplianceMappingManager,
    ComplianceFramework,
    CoverageStatus
)
from accudoc.project_database import ProjectDatabase

# Initialize
db = ProjectDatabase()
compliance_mgr = ComplianceMappingManager(db)

# Create a mapping
mapping_id = compliance_mgr.create_mapping(
    project_id="project_123",
    requirement_id="SOC2-CC1.1",
    framework=ComplianceFramework.SOC2,
    doc_section="README.md#Security",
    doc_path="README.md",
    coverage_status=CoverageStatus.COVERED,
    notes="Security documentation is complete",
    evidence=["README.md", "SECURITY.md"],
    created_by="user@example.com"
)

# Get all mappings
mappings = compliance_mgr.get_mappings("project_123", ComplianceFramework.SOC2)

# Perform gap analysis
gaps = compliance_mgr.analyze_gaps("project_123", ComplianceFramework.SOC2)

# Generate report
report = compliance_mgr.generate_report("project_123", ComplianceFramework.SOC2)

# Export to different formats
text_report = compliance_mgr.export_report(report, 'text')
md_report = compliance_mgr.export_report(report, 'markdown')
html_report = compliance_mgr.export_report(report, 'html')
json_report = compliance_mgr.export_report(report, 'json')
```

## Permission Management

The compliance feature integrates with AccuDoc's membership system for access control:

```bash
# Enable authentication
python accudoc_cli.py compliance map /path/to/repo SOC2-CC1.1 "README.md" \
    -f soc2 \
    --use-auth \
    -u user@example.com
```

Required permissions:
- **READ**: View compliance mappings and reports
- **WRITE**: Create and update compliance mappings
- **MANAGE_USERS**: Configure compliance frameworks

## Best Practices

### 1. Start with Core Requirements

Begin by mapping the most critical requirements first:
- SOC2: CC1.1, CC6.1 (control environment, access controls)
- HIPAA: 164.308, 164.312 (administrative and technical safeguards)
- GDPR: Art 30, Art 32 (records, security)

### 2. Use Consistent Documentation Structure

Organize documentation to align with compliance requirements:
```
docs/
  ├── security/
  │   ├── access-control.md      (SOC2-CC6.1, HIPAA-164.312)
  │   ├── risk-management.md     (SOC2-CC3.1)
  │   └── incident-response.md   (ISO27001-A.16.1)
  ├── privacy/
  │   ├── data-processing.md     (GDPR-Art30)
  │   └── privacy-policy.md      (GDPR-Art13)
  └── operations/
      └── change-management.md   (ISO27001-A.12.1)
```

### 3. Maintain Evidence Trail

Always include evidence files when creating mappings:
```bash
python accudoc_cli.py compliance map /repo SOC2-CC6.1 "docs/security/access.md" \
    -f soc2 \
    -e "access-policy.pdf,audit-logs.csv,training-records.pdf"
```

### 4. Regular Gap Analysis

Run gap analysis regularly (monthly/quarterly):
```bash
# Generate gap report for all frameworks
for framework in soc2 hipaa gdpr iso27001; do
    python accudoc_cli.py compliance analyze /repo -f $framework \
        -o gaps_${framework}_$(date +%Y%m%d).json --json
done
```

### 5. Track Changes Over Time

Use the project database to track compliance progress:
```bash
# Initial baseline
python accudoc_cli.py compliance report /repo -f soc2 -o baseline.json --json

# After improvements
python accudoc_cli.py compliance report /repo -f soc2 -o current.json --json

# Compare coverage improvements
```

### 6. Integrate with CI/CD

Add compliance checking to your CI/CD pipeline:
```yaml
# .github/workflows/compliance.yml
name: Compliance Check
on: [push, pull_request]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check SOC2 Compliance
        run: |
          python accudoc_cli.py compliance analyze . -f soc2 --json > gaps.json
          critical_gaps=$(jq '[.[] | select(.severity == "critical")] | length' gaps.json)
          if [ $critical_gaps -gt 0 ]; then
            echo "❌ Found $critical_gaps critical compliance gaps"
            exit 1
          fi
```

## Troubleshooting

### "Project not found" error

Make sure the repository has been scanned first:
```bash
python accudoc_cli.py scan /path/to/repo -o scan.json
python accudoc_cli.py compliance map /path/to/repo ...
```

### Mappings not appearing in dashboard

The dashboard only shows compliance data if:
1. Mappings have been created for the repository
2. The repository path matches exactly
3. The project database is accessible

### Permission denied errors

When using authentication:
```bash
# Create user with appropriate role
python accudoc_cli.py user create username user@example.com --role editor

# Grant project access
python accudoc_cli.py user grant project_123 --user username --role editor
```

## Examples

### Complete Workflow Example

```bash
# 1. Scan repository
python accudoc_cli.py scan /path/to/myapp -o scan.json

# 2. List SOC2 requirements
python accudoc_cli.py compliance frameworks -f soc2

# 3. Create mappings
python accudoc_cli.py compliance map /path/to/myapp SOC2-CC1.1 "README.md#Organization" -f soc2
python accudoc_cli.py compliance map /path/to/myapp SOC2-CC6.1 "SECURITY.md#Access" -f soc2

# 4. Analyze gaps
python accudoc_cli.py compliance analyze /path/to/myapp -f soc2

# 5. Generate report
python accudoc_cli.py compliance report /path/to/myapp -f soc2 --format markdown -o soc2_report.md

# 6. Include in dashboard
python accudoc_cli.py dashboard /path/to/myapp -o dashboard.md
```

### Multi-Framework Example

Track compliance across multiple frameworks:

```bash
# Map to multiple frameworks
python accudoc_cli.py compliance map /repo SOC2-CC6.1 "docs/access-control.md" -f soc2
python accudoc_cli.py compliance map /repo HIPAA-164.312 "docs/access-control.md" -f hipaa
python accudoc_cli.py compliance map /repo ISO27001-A.9.1 "docs/access-control.md" -f iso27001

# Generate reports for all frameworks
for fw in soc2 hipaa iso27001 gdpr; do
    python accudoc_cli.py compliance report /repo -f $fw --format markdown -o ${fw}_report.md
done
```

## See Also

- [Multi-Repository Dashboard](MULTI_REPO_DASHBOARD.md)
- [Project Database](project_database.py)
- [Membership System](membership.py)
- [Test Suite](test_compliance_mapping.py)
- [Demo Script](demo_compliance.py)
