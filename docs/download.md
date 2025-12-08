# Download Command (`download`)

Download an SBOM from the Interlynk platform.

## Usage

```bash
python3 pylynk.py download --prod <product-name> --verId <version-id> [OPTIONS]
# OR
python3 pylynk.py download --prod <product-name> --env <environment> --ver <version-name> [OPTIONS]
```

**Note:** You must provide either `--verId` OR all three of `--prod`, `--env`, and `--ver`.

## Options

| Option | Description |
|--------|-------------|
| `--prod` | Product name |
| `--verId` | Version ID (mutually exclusive with `--ver`) |
| `--ver` | Version name (mutually exclusive with `--verId`) |
| `--env` | Environment name |
| `--output` | Output file path |
| `--vuln` | Include vulnerabilities (true/false/yes/no/1/0) |
| `--spec` | SBOM specification (SPDX or CycloneDX) |
| `--spec-version` | SBOM specification version |
| `--lite` | Download lite SBOM (reduced metadata) |
| `--original` | Download original uploaded SBOM |
| `--dont-package-sbom` | Don't package into single file |
| `--exclude-parts` | Exclude parts from SBOM |
| `--include-support-status` | Include support status |
| `--support-level-only` | Download only support level info (CSV) |
| `--token` | Security token |
| `-v, --verbose` | Enable verbose/debug output |

## Examples

### Download by version ID

```bash
python3 pylynk.py download --prod 'sbomqs' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```

### Download by version name

```bash
python3 pylynk.py download --prod 'sbomqs' --env 'default' --ver 'v1.0.0'
```

### Download with vulnerabilities

```bash
python3 pylynk.py download --prod 'sbomqs' --verId 'fbcc24ad-...' --vuln true
```

### Download in specific format

```bash
# Download as SPDX 2.3
python3 pylynk.py download --prod 'sbomqs' --verId 'fbcc24ad-...' --spec SPDX --spec-version 2.3

# Download as CycloneDX 1.5
python3 pylynk.py download --prod 'sbomqs' --verId 'fbcc24ad-...' --spec CycloneDX --spec-version 1.5
```

### Download lite SBOM

```bash
python3 pylynk.py download --prod 'sbomqs' --verId 'fbcc24ad-...' --lite
```

### Download original SBOM

```bash
python3 pylynk.py download --prod 'sbomqs' --verId 'fbcc24ad-...' --original
```

### Download with additional options

```bash
python3 pylynk.py download --prod 'sbomqs' --verId 'fbcc24ad-...' \
  --include-support-status --exclude-parts
```

### Download support level only (CSV)

```bash
python3 pylynk.py download --prod 'sbomqs' --verId 'fbcc24ad-...' \
  --support-level-only --output support-levels.csv
```

### Using Docker

```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  -v $(pwd):/app/data \
  ghcr.io/interlynk-io/pylynk download --prod 'sbomqs' --verId 'fbcc24ad-...' \
  --output /app/data/sbom.json
```

## Download Options Explained

| Option | Description |
|--------|-------------|
| `--lite` | Downloads a lightweight version with reduced metadata, smaller file size |
| `--original` | Downloads the exact SBOM that was originally uploaded, without any processing |
| `--dont-package-sbom` | For multi-SBOM documents, keeps them separate instead of packaging into one |
| `--exclude-parts` | Excludes linked/nested parts from the SBOM |
| `--include-support-status` | Adds support status information to components |
