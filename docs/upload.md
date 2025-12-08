# Upload Command (`upload`)

Upload an SBOM file to the Interlynk platform.

## Usage

```bash
python3 pylynk.py upload --prod <product-name> --sbom <sbom-file> [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--prod` | Product name (required) |
| `--sbom` | Path to SBOM file (required) |
| `--env` | Environment name (optional, defaults to 'default') |
| `--retries` | Number of upload retries (default: 3) |
| `--token` | Security token (can also use `INTERLYNK_SECURITY_TOKEN` env var) |
| `-v, --verbose` | Enable verbose/debug output |

## Examples

### Upload to default environment

```bash
python3 pylynk.py upload --prod 'sbomqs' --sbom sbomqs.cdx.json
```

### Upload to a specific environment

```bash
python3 pylynk.py upload --prod 'sbomqs' --env 'production' --sbom sbomqs.cdx.json
```

### Upload with custom retry count

```bash
# Disable retries
python3 pylynk.py upload --prod 'sbomqs' --sbom sbomqs.cdx.json --retries 0

# Increase retries to 5
python3 pylynk.py upload --prod 'sbomqs' --sbom sbomqs.cdx.json --retries 5
```

### Using Docker

```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  -v $(pwd):/app/data \
  ghcr.io/interlynk-io/pylynk upload --prod 'sbomqs' --sbom /app/data/sbomqs.cdx.json
```

## Retry Behavior

PyLynk includes automatic retry logic with exponential backoff for failed uploads:

- Default: 3 retries with increasing delays (1s, 2s, 4s)
- Retries are **not** attempted for:
  - Authentication errors (401)
  - Client errors (4xx) except rate limiting (429)

## CI/CD Metadata

When running in CI environments, PyLynk automatically captures and sends metadata about the build pipeline. See [CI/CD Integration](ci-cd.md) for details.

## Supported SBOM Formats

- CycloneDX (JSON and XML)
- SPDX (JSON and tag-value)
