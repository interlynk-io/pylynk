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
| `--output` | Output format: `table` (default), `json`, or `csv` |
| `--human-time` | Show timestamps in human-friendly format (e.g., '2 days ago') |
| `--token` | Security token (can also use `INTERLYNK_SECURITY_TOKEN` env var) |
| `-v, --verbose` | Enable verbose/debug output |

## Examples

### List versions for a product (default)

```bash
python3 pylynk.py vers --prod 'sbomqs'
```

### List versions in JSON format

```bash
python3 pylynk.py vers --prod 'sbomqs' --output json
```

### List versions in CSV format

```bash
python3 pylynk.py vers --prod 'sbomqs' --output csv
```

### List versions with human-friendly timestamps

```bash
python3 pylynk.py vers --prod 'sbomqs' --human-time
```

### List versions for a specific environment

```bash
python3 pylynk.py vers --prod 'sbomqs' --env 'production'
```

### Using Docker

```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  ghcr.io/interlynk-io/pylynk vers --prod 'sbomqs'
```

## Output Fields

| Field | Description |
|-------|-------------|
| ID | Unique version identifier (use this for `--verId` in other commands) |
| VERSION | Version name/label from primary component |
| PRIMARY COMPONENT | Name of the primary component |
| UPDATED AT | Last update timestamp |
