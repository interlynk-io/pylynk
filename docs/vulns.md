# Vulnerabilities Command (`vulns`)

List vulnerabilities for a product/environment with flexible output formatting.

## Usage

```bash
python3 pylynk.py vulns --prod <product-name> [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--prod` | Product name |
| `--env` | Environment name (optional, defaults to 'default') |
| `--verId` | Version ID (optional, uses latest if not specified) |
| `--ver` | Version name (mutually exclusive with `--verId`) |
| `--output` | Output format: `table` (default), `json`, or `csv` |
| `--columns` | Comma-separated list of columns to display |
| `--vuln-details` | Include vulnerability metadata columns |
| `--vex-details` | Include VEX information columns |
| `--timestamp-details` | Include all timestamp columns |
| `--human-time` | Show timestamps in human-friendly format (e.g., '2 days ago') |
| `--list-columns` | List available column names and exit |
| `--token` | Security token |
| `-v, --verbose` | Enable verbose/debug output |

## Examples

### Basic usage (table format)

```bash
python3 pylynk.py vulns --prod 'sbomqs' --env 'production'
```

### JSON output

```bash
python3 pylynk.py vulns --prod 'sbomqs' --output json
```

### CSV output

```bash
python3 pylynk.py vulns --prod 'sbomqs' --output csv > vulnerabilities.csv
```

### With vulnerability details

```bash
python3 pylynk.py vulns --prod 'sbomqs' --vuln-details
```

### With VEX information

```bash
python3 pylynk.py vulns --prod 'sbomqs' --vex-details
```

### With all timestamps

```bash
python3 pylynk.py vulns --prod 'sbomqs' --timestamp-details
```

### Human-friendly timestamps

```bash
python3 pylynk.py vulns --prod 'sbomqs' --human-time
```

### Custom columns

```bash
python3 pylynk.py vulns --prod 'sbomqs' --columns "id,component_name,severity,cvss,status"
```

### List available columns

```bash
python3 pylynk.py vulns --list-columns
```

### Using Docker

```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  ghcr.io/interlynk-io/pylynk vulns --prod 'sbomqs' --output table
```

## Available Columns

### Basic Columns (Default)

| Column | Header | Description |
|--------|--------|-------------|
| `id` | ID | Vulnerability ID (CVE/NVD alias) |
| `part_name` | PART NAME | Part name (N/A if not from a part) |
| `part_version` | PART VERSION | Part version (N/A if not from a part) |
| `component_name` | COMPONENT NAME | Affected component name |
| `component_version` | COMPONENT VERSION | Affected component version |
| `severity` | SEVERITY | Vulnerability severity |
| `source` | SOURCE | Vulnerability data source |
| `status` | STATUS | VEX status |
| `assigned` | ASSIGNED | When vulnerability was assigned |

### Vulnerability Metadata (`--vuln-details`)

| Column | Header | Description |
|--------|--------|-------------|
| `severity` | SEVERITY | Vulnerability severity |
| `kev` | KEV | Known Exploited Vulnerability flag |
| `cvss` | CVSS | CVSS score |
| `cvss_vector` | CVSS VECTOR | Full CVSS vector string |
| `epss` | EPSS | EPSS score (exploitation probability) |
| `cwe` | CWE | CWE identifiers |

### VEX Information (`--vex-details`)

| Column | Header | Description |
|--------|--------|-------------|
| `status` | STATUS | VEX status (affected, not_affected, etc.) |
| `details` | DETAILS | Additional details |
| `justification` | JUSTIFICATION | VEX justification reason |
| `action_statement` | ACTION STATEMENT | Recommended action |
| `impact_statement` | IMPACT STATEMENT | Impact description |
| `response` | RESPONSE | Response action taken |

### Timestamps (`--timestamp-details`)

| Column | Header | Description |
|--------|--------|-------------|
| `assigned` | ASSIGNED | When vulnerability was assigned to component |
| `published` | PUBLISHED | When vulnerability was published |
| `last_modified` | LAST MODIFIED | Last modification timestamp |
| `updated` | UPDATED | Last update timestamp |

## Output Formats

### Table (default)

Human-readable table format with aligned columns:

```
ID             | COMPONENT NAME | SEVERITY | STATUS
---------------|----------------|----------|--------
CVE-2024-1234  | lodash         | HIGH     | affected
CVE-2024-5678  | express        | MEDIUM   | not_affected
```

### JSON

Structured JSON output for programmatic use:

```json
[
  {
    "ID": "CVE-2024-1234",
    "COMPONENT NAME": "lodash",
    "SEVERITY": "HIGH",
    "STATUS": "affected"
  }
]
```

### CSV

Comma-separated values for spreadsheet import:

```csv
ID,COMPONENT NAME,SEVERITY,STATUS
CVE-2024-1234,lodash,HIGH,affected
CVE-2024-5678,express,MEDIUM,not_affected
```

## Part Name and Part Version

The `part_name` and `part_version` columns show the name and version of the linked part (sub-SBOM) that contains the vulnerable component. If the vulnerability is from the main SBOM (not from a linked part), these columns display "N/A".

## Human-Friendly Timestamps

With `--human-time`, timestamp columns display relative times:

- "2 days ago"
- "3 hours ago"
- "in 1 week"
- "just now"
