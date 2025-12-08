# Status Command (`status`)

Check the processing status of a specific SBOM version.

## Usage

```bash
python3 pylynk.py status --prod <product-name> --verId <version-id> [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--prod` | Product name (required) |
| `--verId` | Version ID (mutually exclusive with `--ver`) |
| `--ver` | Version name (mutually exclusive with `--verId`) |
| `--env` | Environment name (optional, defaults to 'default') |
| `--token` | Security token (can also use `INTERLYNK_SECURITY_TOKEN` env var) |
| `--table` | Output in table format |
| `--json` | Output in JSON format (default) |
| `-v, --verbose` | Enable verbose/debug output |

## Status Values

The status of actions associated with an SBOM is reported in these states:

| Status | Description |
|--------|-------------|
| `UNKNOWN` | Status cannot be determined |
| `NOT_STARTED` | Processing has not begun |
| `IN_PROGRESS` | Processing is currently running |
| `COMPLETED` | Processing has finished successfully |

## Status Types

The following SBOM processing actions are tracked:

| Key | Description |
|-----|-------------|
| `checksStatus` | SBOM quality and format checks |
| `policyStatus` | Policy evaluation status |
| `labelingStatus` | Internal labeling status |
| `automationStatus` | Automation rules execution status |
| `vulnScanStatus` | Vulnerability scanning status |

## Examples

### Check status by version ID

```bash
python3 pylynk.py status --prod 'sbomqs' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```

### Check status by version name

```bash
python3 pylynk.py status --prod 'sbomqs' --env 'production' --ver 'v1.0.0'
```

### Using Docker

```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  ghcr.io/interlynk-io/pylynk status --prod 'sbomqs' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```

## Use Cases

- **Wait for processing**: Poll status after upload to wait for vulnerability scanning to complete
- **CI/CD integration**: Check if SBOM processing finished before proceeding with deployment
- **Troubleshooting**: Identify which processing step may have failed or stalled
