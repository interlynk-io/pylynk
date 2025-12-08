# Products Command (`prods`)

List all products in your Interlynk organization.

## Usage

```bash
python3 pylynk.py prods [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--token` | Security token (can also use `INTERLYNK_SECURITY_TOKEN` env var) |
| `--table` | Output in table format |
| `--json` | Output in JSON format (default) |
| `-v, --verbose` | Enable verbose/debug output |

## Examples

### List products in table format

```bash
python3 pylynk.py prods --table
```

### List products in JSON format

```bash
python3 pylynk.py prods --json
# or simply
python3 pylynk.py prods
```

### Using Docker

```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  ghcr.io/interlynk-io/pylynk prods --table
```

## Output Fields

| Field | Description |
|-------|-------------|
| ID | Unique product identifier |
| Name | Product name |
| Environments | Number of environments configured |
| Created | Creation timestamp |
| Updated | Last update timestamp |
