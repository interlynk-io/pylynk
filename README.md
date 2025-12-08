<!--
 Copyright 2025 Interlynk.io

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

# `pylynk`: Command Line Tool for the Interlynk Platform

![GitHub all releases](https://img.shields.io/github/downloads/interlynk-io/pylynk/total)

`pylynk` is the official CLI tool for interfacing with Interlynk's SBOM management platform. Upload, download, and manage SBOMs (Software Bill of Materials) from your terminal or CI/CD pipelines.

## Installation

### Using pip

```bash
git clone https://github.com/interlynk-io/pylynk
cd pylynk
pip3 install -r requirements.txt
python3 pylynk.py --help
```

### Using Docker

```bash
docker pull ghcr.io/interlynk-io/pylynk:latest
```

Or build locally:

```bash
docker build -t pylynk .
```

## Authentication

Set your security token via environment variable (recommended):

```bash
export INTERLYNK_SECURITY_TOKEN=your_token_here
```

Or pass it with each command:

```bash
python3 pylynk.py prods --token your_token_here
```

## Quick Start

### Upload an SBOM

```bash
python3 pylynk.py upload --prod 'my-product' --sbom my-sbom.json
```

### Download an SBOM

```bash
python3 pylynk.py download --prod 'my-product' --verId 'version-id' --output sbom.json
```

### List Vulnerabilities

```bash
python3 pylynk.py vulns --prod 'my-product' --env 'production'
```

### Using Docker

```bash
# Upload
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  -v $(pwd):/app/data \
  ghcr.io/interlynk-io/pylynk upload --prod 'my-product' --sbom /app/data/my-sbom.json

# Download
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  -v $(pwd):/app/data \
  ghcr.io/interlynk-io/pylynk download --prod 'my-product' --verId 'version-id' --output /app/data/sbom.json
```

## Commands

| Command | Description | Documentation |
|---------|-------------|---------------|
| `prods` | List products | [docs/prods.md](docs/prods.md) |
| `vers` | List versions for a product | [docs/vers.md](docs/vers.md) |
| `status` | Check SBOM processing status | [docs/status.md](docs/status.md) |
| `upload` | Upload an SBOM | [docs/upload.md](docs/upload.md) |
| `download` | Download an SBOM | [docs/download.md](docs/download.md) |
| `vulns` | List vulnerabilities | [docs/vulns.md](docs/vulns.md) |
| `version` | Show pylynk version | - |

## Output Formats

All commands support multiple output formats via `--output`:

- `table` - Human-readable table format (default)
- `json` - JSON format for programmatic use
- `csv` - CSV format for spreadsheet import

Commands with timestamps also support `--human-time` to display timestamps in human-friendly format (e.g., '2 days ago').

```bash
# Table format (default)
python3 pylynk.py prods

# JSON format
python3 pylynk.py prods --output json

# CSV format
python3 pylynk.py prods --output csv

# With human-friendly timestamps
python3 pylynk.py prods --human-time
```

## CI/CD Integration

PyLynk automatically detects CI environments (GitHub Actions, Bitbucket Pipelines, Azure DevOps) and captures build metadata during uploads.

See [docs/ci-cd.md](docs/ci-cd.md) for detailed CI/CD integration instructions.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `INTERLYNK_SECURITY_TOKEN` | Authentication token (required) |
| `INTERLYNK_API_URL` | Override API endpoint (default: `https://api.interlynk.io/lynkapi`) |
| `PYLYNK_INCLUDE_CI_METADATA` | Control CI metadata collection (`auto`/`true`/`false`) |

## Debugging

Enable verbose output:

```bash
python3 pylynk.py prods --verbose
```

Point to a different API endpoint:

```bash
export INTERLYNK_API_URL=http://localhost:3000/lynkapi
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Authentication failed" | Verify your `INTERLYNK_SECURITY_TOKEN` is correct |
| "Product not found" | Check product name spelling and organization access |
| "Version not found" | Verify version ID or use `vers` command to list available versions |

### Docker with Local API

On macOS/Windows, use `host.docker.internal`:

```bash
export INTERLYNK_API_URL=http://host.docker.internal:3000/lynkapi
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  -e INTERLYNK_API_URL=$INTERLYNK_API_URL ...
```

On Linux, use `--network="host"`:

```bash
docker run --network="host" -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN ...
```

## Other SBOM Open Source Tools

- [SBOM Assembler](https://github.com/interlynk-io/sbomasm) - Compose SBOMs from multiple parts
- [SBOM Quality Score](https://github.com/interlynk-io/sbomqs) - Evaluate SBOM quality and completeness
- [SBOM Search Tool](https://github.com/interlynk-io/sbomagr) - Grep-style semantic search in SBOMs
- [SBOM Explorer](https://github.com/interlynk-io/sbomex) - Discover and download public SBOMs

## Contact

- [Live Chat](https://www.interlynk.io/#hs-chat-open)
- [Email Us](mailto:hello@interlynk.io)
- [Report Issues](https://github.com/interlynk-io/pylynk/issues)
- [Follow on X](https://twitter.com/InterlynkIo)

## Stargazers

If you like this project, please support us by starring it.

[![Stargazers](https://starchart.cc/interlynk-io/pylynk.svg)](https://starchart.cc/interlynk-io/pylynk)



