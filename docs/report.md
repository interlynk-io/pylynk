# Report Command (`report`)

Generate reports from the Interlynk platform.

## Usage

```bash
python3 pylynk.py report --type attribution --prod <product-name> [OPTIONS]
```

## Report Types

| Type | Description |
|------|-------------|
| `attribution` | Generate a CSV attribution report with component licenses, copyrights, and notices |

## Options

| Option | Description |
|--------|-------------|
| `--type` | Report type (required, currently: `attribution`) |
| `--prod` | Product name (required) |
| `--env` | Environment name (optional, defaults to 'default') |
| `--ver` | Version name (optional, uses latest if not specified) |
| `--verId` | Version ID (mutually exclusive with `--ver`) |
| `--include-license-text` | Include full license text in output |
| `--output-file` | Output file path (prints to stdout if not specified) |
| `--token` | Security token |
| `-v, --verbose` | Enable verbose/debug output |

## Examples

### Basic attribution report

```bash
python3 pylynk.py report --type attribution --prod 'my-product'
```

### Specify environment and version

```bash
python3 pylynk.py report --type attribution --prod 'my-product' --env 'production' --ver 'v1.0.0'
```

### Save to file

```bash
python3 pylynk.py report --type attribution --prod 'my-product' --output-file attribution.csv
```

### Include full license text

```bash
python3 pylynk.py report --type attribution --prod 'my-product' --include-license-text --output-file attribution.csv
```

### Using Docker

```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  -v $(pwd):/app/data \
  ghcr.io/interlynk-io/pylynk report --type attribution --prod 'my-product' \
  --output-file /app/data/attribution.csv
```

## Attribution Report

The attribution report generates a CSV with the following columns:

| Column | Description |
|--------|-------------|
| Component Name | Name of the software component |
| Component Version | Version of the component |
| Declared Licenses | License expression declared by the component author |
| Licenses | Resolved license expression |
| Copyright | Copyright statement |
| Notice | Attribution notice text |
| License Texts | Full license text (only with `--include-license-text`) |

### Auto-selection behavior

- If `--env` is omitted, the `default` environment is used.
- If `--ver` is omitted, the latest version (by creation date) is automatically selected.

### License cleaning

License expressions are automatically cleaned to remove internal `LicenseRef-interlynk` tokens, producing human-readable license identifiers in the output.
