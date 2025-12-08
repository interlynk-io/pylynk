# Versions Command (`vers`)

List all versions (SBOMs) for a specific product.

## Usage

```bash
python3 pylynk.py vers --prod <product-name> [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--prod` | Product name (required) |
| `--env` | Environment name (optional, defaults to 'default') |
| `--token` | Security token (can also use `INTERLYNK_SECURITY_TOKEN` env var) |
| `--table` | Output in table format |
| `--json` | Output in JSON format (default) |
| `-v, --verbose` | Enable verbose/debug output |

## Examples

### List versions for a product (default environment)

```bash
python3 pylynk.py vers --prod 'sbomqs' --table
```

### List versions in JSON format

```bash
python3 pylynk.py vers --prod 'sbomqs' --json
```

### List versions for a specific environment

```bash
python3 pylynk.py vers --prod 'sbomqs' --env 'production' --table
```

### Using Docker

```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  ghcr.io/interlynk-io/pylynk vers --prod 'sbomqs' --table
```

## Output Fields

| Field | Description |
|-------|-------------|
| ID | Unique version identifier (use this for `--verId` in other commands) |
| Version | Version name/label |
| Spec | SBOM specification (SPDX or CycloneDX) |
| Components | Number of components in the SBOM |
| Created | Creation timestamp |
| Updated | Last update timestamp |
