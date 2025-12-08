# Products Command (`prods`)

List all products in your Interlynk organization.

## Usage

```bash
python3 pylynk.py prods [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--output` | Output format: `table` (default), `json`, or `csv` |
| `--human-time` | Show timestamps in human-friendly format (e.g., '2 days ago') |
| `--token` | Security token (can also use `INTERLYNK_SECURITY_TOKEN` env var) |
| `-v, --verbose` | Enable verbose/debug output |

## Examples

### List products in table format (default)

```bash
python3 pylynk.py prods
```

### List products in JSON format

```bash
python3 pylynk.py prods --output json
```

### List products in CSV format

```bash
python3 pylynk.py prods --output csv
```

### List products with human-friendly timestamps

```bash
python3 pylynk.py prods --human-time
```

### Using Docker

```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  ghcr.io/interlynk-io/pylynk prods
```

## Output Fields

| Field | Description |
|-------|-------------|
| NAME | Product name |
| ID | Unique product identifier |
| VERSIONS | Number of versions/SBOMs |
| UPDATED AT | Last update timestamp |
