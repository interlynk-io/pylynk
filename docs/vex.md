# VEX Command (`vex`)

Update VEX data for one or more component vulnerabilities.

## Usage

```bash
python3 pylynk.py vex update --prod <product-name> [OPTIONS]
python3 pylynk.py vex bulk-update --prod <product-name> [OPTIONS]
```

You can target a version by name:

```bash
python3 pylynk.py vex update --prod 'my-product' --env 'production' --ver 'v1.0.0' ...
```

Or use a version ID when you already have component vulnerability IDs:

```bash
python3 pylynk.py vex update --verId 'version-uuid' --component-vuln-id 'component-vuln-uuid' ...
```

## Single Update

```bash
python3 pylynk.py vex update \
  --prod 'my-product' \
  --env 'production' \
  --ver 'v1.0.0' \
  --vuln CVE-2024-1234 \
  --component lodash \
  --component-version 4.17.21 \
  --status not_affected \
  --justification 'Code not reachable' \
  --detail 'Not reachable in deployed configuration' \
  --note 'Reviewed by AppSec'
```

You can also use internal IDs directly:

```bash
python3 pylynk.py vex update \
  --verId 'version-uuid' \
  --component-vuln-id 'component-vuln-uuid' \
  --status-id 'status-uuid' \
  --justification-id 'justification-uuid' \
  --response-id 'response-uuid' \
  --note 'Reviewed by AppSec'
```

## Bulk Update

Use repeated component vulnerability IDs:

```bash
python3 pylynk.py vex bulk-update \
  --verId 'version-uuid' \
  --component-vuln-id 'component-vuln-1' \
  --component-vuln-id 'component-vuln-2' \
  --status affected \
  --propagate
```

Or use a CSV/JSON file:

```bash
python3 pylynk.py vex bulk-update \
  --prod 'my-product' \
  --env 'production' \
  --ver 'v1.0.0' \
  --file vex-updates.csv
```

Bulk updates require a status from either `--status` / `--status-id` or each file row. Rows with different VEX payloads are grouped and sent as separate bulk updates.

## CSV Format

Rows may use internal IDs:

```csv
component_vuln_id,status_id,justification_id,response_id,note,detail,propagate_vex
component-vuln-1,status-uuid,justification-uuid,response-uuid,Reviewed,Not reachable,false
component-vuln-2,status-uuid,,,Reviewed,Requires upgrade,true
```

Or names:

```csv
vuln,component,component_version,status,justification,note,detail
CVE-2024-1234,lodash,4.17.21,not_affected,Code not reachable,Reviewed,Not reachable
CVE-2024-5678,express,4.18.2,affected,,Reviewed,Upgrade required
```

## JSON Format

JSON files must contain an array of row objects. The supported keys are the same as CSV columns.

```json
[
  {
    "component_vuln_id": "component-vuln-1",
    "status": "fixed",
    "response": "Rollback",
    "note": "Fixed in the next release"
  },
  {
    "vuln": "CVE-2024-1234",
    "component": "lodash",
    "component_version": "4.17.21",
    "status": "in_triage",
    "note": "Queued for review"
  }
]
```

Supported file columns include:

| Column | Description |
|--------|-------------|
| `component_vuln_id` | Component vulnerability UUID |
| `vuln` / `cve` / `vuln_id` | Vulnerability ID such as CVE |
| `component` / `component_name` | Component name |
| `component_version` | Component version |
| `status` / `status_id` | VEX status name or ID |
| `justification` / `justification_id` | VEX justification name or ID |
| `response` / `response_id` | CycloneDX response name or ID |
| `note` | VEX note |
| `impact` | Impact statement |
| `detail` | VEX detail |
| `action` | Action statement |
| `fixed_in` | Fixed-in version |
| `propagate_vex` | `true` or `false` |

## Custom Fields

Use `--custom-fields-file` with a JSON array matching the API's `ComponentVulnCustomFieldAttributesInput` shape:

```json
[
  {
    "value": "5",
    "componentVulnCustomFieldDefinitionId": "definition-uuid"
  },
  {
    "value": "Reviewed by AppSec",
    "componentVulnCustomFieldDefinitionId": "definition-uuid"
  }
]
```

To clear a custom field, include `_destroy: true`:

```json
[
  {
    "value": "",
    "_destroy": true,
    "componentVulnCustomFieldDefinitionId": "definition-uuid"
  }
]
```

## Name Matching

Names are matched case-insensitively and normalize spaces, hyphens, and underscores. For example, these all resolve to the same status when that option exists:

- `not_affected`
- `Not Affected`
- `not-affected`

Common local API values include:

| Type | Example Names |
|------|---------------|
| Status | `In Triage`, `Not Affected`, `Affected`, `Fixed` |
| Justification | `Code not reachable`, `Code not present`, `Protected by network` |
| Response | `Update`, `Rollback`, `Will Not Fix`, `Workaround Available` |

If name resolution fails, use the corresponding ID flag or file column.

## Notes

- When using `--component-vuln-id`, ensure the ID belongs to the target `--verId` / version. The CLI trusts explicit IDs.
- Some VEX fields may be enforced by server-side status rules. For example, response/action/fixed-in fields may only persist for statuses where the API accepts them.
- For name-based component vulnerability resolution, use `--component` and `--component-version` when a vulnerability appears in more than one component.

## Options

| Option | Description |
|--------|-------------|
| `--prod` | Product name |
| `--env` | Environment name, defaults to `default` when product is used |
| `--ver` | Version name |
| `--verId` | Version ID |
| `--component-vuln-id` | Component vulnerability ID |
| `--vuln` | Vulnerability ID such as CVE |
| `--component` | Component name |
| `--component-version` | Component version |
| `--status` / `--status-id` | VEX status name or ID |
| `--justification` / `--justification-id` | VEX justification name or ID |
| `--response` / `--response-id` | CycloneDX response name or ID |
| `--note` | VEX note |
| `--impact` | Impact statement |
| `--detail` | VEX detail |
| `--action` | Action statement |
| `--fixed-in` | Fixed-in version |
| `--propagate` / `--no-propagate` | Control VEX propagation |
| `--custom-fields-file` | JSON array of custom field attributes |
| `--output` | `table` or `json` |
