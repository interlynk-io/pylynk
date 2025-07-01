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

# `pylynk`: cmdline utility for the Interlynk Platform 

![GitHub all releases](https://img.shields.io/github/downloads/interlynk-io/pylynk/total)

`pylynk` is your primary tool to interface with interlynk's SAAS platform. Its main purpose is to **upload and download SBOMs** (Software Bill of Materials) to/from the Interlynk platform, along with managing products and versions.

## Quick Start - Upload & Download

### Upload an SBOM
```bash
# Using Python
export INTERLYNK_SECURITY_TOKEN=your_token_here
python3 pylynk.py upload --prod 'my-product' --sbom my-sbom.json

# Using Docker
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk upload --prod 'my-product' --sbom /app/data/my-sbom.json
```

### Download an SBOM
```bash
# Using Python
python3 pylynk.py download --prod 'my-product' --verId 'version-id-here' --output downloaded-sbom.json

# Using Docker
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk download --prod 'my-product' --verId 'version-id-here' --output /app/data/downloaded-sbom.json
```

## Installation

```sh
git clone https://github.com/interlynk-io/pylynk
pip3 install -r requirements.txt
python3 pylynk.py --help
````
or 

```sh
docker pull ghcr.io/interlynk-io/pylynk:latest
```

or build locally:

```sh
docker build -t pylynk .
```
# Usage

### Docker Volume Mounting
When using Docker, you need to mount your local directory to access files for upload or to save downloaded files. The examples use `-v $(pwd):/app/data` which mounts your current directory to `/app/data` inside the container.

### Docker Authentication
When using Docker with environment variables, make sure to pass the value of the environment variable:
```bash
# Correct - passes the value
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN ...

# Incorrect - only passes the variable name  
docker run -e INTERLYNK_SECURITY_TOKEN ...
```

### Authenticate
PyLynk can be authenticated by setting an environment variable `INTERLYNK_SECURITY_TOKEN` or by providing a `--token` param to all commands.
```bash
export INTERLYNK_SECURITY_TOKEN=lynk_test_GDGEB2j6jnhkzLSAQk9U3wiiQLrbNT11Y8J4
python3 pylynk.py prods
```

OR

```bash
python3 pylynk.py prods --token lynk_test_GDGEB2j6jnhkzLSAQk9U3wiiQLrbNT11Y8J4
```

OR 

```bash
export INTERLYNK_SECURITY_TOKEN=lynk_test_GDGEB2j6jnhkzLSAQk9U3wiiQLrbNT11Y8J4
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk prods
```


## Output Formats
PyLynk supports multiple output formats:
- `--json` - JSON format (default)
- `--table` - Table format

## List Products
```bash
# Table format
python3 pylynk.py prods --table

# JSON format (default if no format specified)
python3 pylynk.py prods --json
# or simply
python3 pylynk.py prods
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk prods --table 
```

## List Versions
### List Versions by product name (default environment)
```bash
python3 pylynk.py vers --prod 'sbom-exec' --table
```
OR 

```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk  vers --prod 'sbom-exec' --table
```

### List Versions by product name (default environment) as JSON
```bash
python3 pylynk.py vers --prod 'sbom-exec' --json
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk  vers --prod 'sbom-exec' --json
```



### List Versions for specific environment by name
```bash
python3 pylynk.py vers --prod 'sbomqs' --env 'production' --table
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk  vers --prod 'sbomqs' --env 'production' --table
```

## Status of a specific version
The status of actions associated with SBOM is reported in three states:
1. UNKNOWN
2. NOT_STARTED
3. IN_PROGRESS
4. COMPLETED

This applies to the following SBOM actions (represented with specific keys):
1. SBOM Checks (Key: `checksStatus`)
2. SBOM Policies (Key: `policyStatus`)
3. SBOM Internal Labeling (Key: `labelingStatus`)
4. SBOM Automation Rules (Key: `automationStatus`)
5. SBOM Vulnerability Scan (Key: `vulnScanStatus`)

### Status of a specific version by version ID
```bash
python3 pylynk.py status --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk status --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```


## Download SBOM

**Note:** Download requires either `--verId` OR all three parameters (`--prod`, `--env`, and `--ver`) together.

### Download SBOM for specific version by version ID
Download SBOM for a specific version using version ID:
```bash
python3 pylynk.py download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --output /app/data/sbom.json
```

### Download SBOM for specific version by version name
Download SBOM for a specific version using product name, environment, and version name:
```bash
python3 pylynk.py download --prod 'sbomex' --env 'default' --ver 'sha256:5ed7e95ae79fe3fe6c4b8660f6f9e31154e64eca76ae42963a679fbb198c3951'
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --env 'default' --ver 'sha256:5ed7e95ae79fe3fe6c4b8660f6f9e31154e64eca76ae42963a679fbb198c3951' --output /app/data/sbom.json
```

### Download SBOM for specific version by version ID with Vulnerabilities
Download SBOM including vulnerability information (accepts: true, false, 1, 0, yes, no):
```bash
python3 pylynk.py download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --vuln true
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --vuln true --output /app/data/sbom-with-vulns.json
```

### Download SBOM with Advanced Options

#### Download SBOM in specific format
Download SBOM in SPDX or CycloneDX format with a specific version:
```bash
python3 pylynk.py download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --spec SPDX --spec-version 2.3
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --spec CycloneDX --spec-version 1.5 --output /app/data/sbom.json
```

#### Download Lite SBOM
Download a lightweight version of the SBOM (reduced metadata):
```bash
python3 pylynk.py download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --lite
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --lite --output /app/data/sbom-lite.json
```

#### Download Original SBOM
Download the original uploaded SBOM without any processing:
```bash
python3 pylynk.py download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --original
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --original --output /app/data/sbom-original.json
```

#### Download SBOM with Additional Options
Download SBOM with support status and excluding parts:
```bash
python3 pylynk.py download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --include-support-status --exclude-parts
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --include-support-status --exclude-parts --output /app/data/sbom-filtered.json
```

#### Download Support Level Information Only
Download only the support level information in CSV format:
```bash
python3 pylynk.py download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --support-level-only
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --support-level-only --output /app/data/support-levels.csv
```

#### Download without packaging
Download SBOM without packaging into a single file (useful for multi-SBOM documents):
```bash
python3 pylynk.py download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --dont-package-sbom
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4' --dont-package-sbom --output /app/data/sbom-unpackaged.json
```


## Upload SBOM
### Upload SBOM to the default environment
Upload SBOM file sbomqs.cdx.json to the product named **sbomqs**
```bash
python3 pylynk.py upload --prod 'sbomqs' --sbom sbomqs.cdx.json
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk upload --prod 'sbomqs' --sbom /app/data/sbomqs.cdx.json
```


### Upload SBOM to a specific environment
Upload SBOM file sbomqs.cdx.json to the product named **sbomqs** under environment **production**
```bash
python3 pylynk.py upload --prod 'sbomqs' --env 'production' --sbom sbomqs.cdx.json
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk upload --prod 'sbomqs' --env 'production' --sbom /app/data/sbomqs.cdx.json
```

### Upload with Retry Configuration
PyLynk includes automatic retry logic with exponential backoff for failed uploads. By default, it will retry 3 times with increasing delays (1s, 2s, 4s).

Configure the number of retries:
```bash
# Disable retries
python3 pylynk.py upload --prod 'sbomqs' --sbom sbomqs.cdx.json --retries 0

# Increase retries to 5
python3 pylynk.py upload --prod 'sbomqs' --sbom sbomqs.cdx.json --retries 5
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN -v $(pwd):/app/data ghcr.io/interlynk-io/pylynk upload --prod 'sbomqs' --sbom /app/data/sbomqs.cdx.json --retries 5
```

**Note:** Retries are not attempted for authentication errors (401) or client errors (4xx) except rate limiting (429).

###  Increasing the verbosity of output
Use `--verbose` or `-v` with any command to see debug output. You can increase verbosity by using multiple `-v` flags:
- `-v` - Basic debug output
- `-vv` - More detailed debug output
- `-vvv` - Maximum verbosity


###  Debugging
To point to a different API endpoint than production
```bash
export INTERLYNK_API_URL=http://localhost:3000/lynkapi
```

## Troubleshooting

### Common Error Messages
- **"Authentication failed. Please check your INTERLYNK_SECURITY_TOKEN"** - Verify your token is correct and hasn't expired
- **"Error: Please provide either --verId OR all of --prod, --env, and --ver"** - The download command requires specific parameter combinations
- **"Product not found"** - Check that the product name is spelled correctly and exists in your organization
- **"Version not found"** - Ensure the version ID or version name is correct

### Local Testing with Docker
When testing against a local API server running on your host machine, Docker containers cannot access `localhost`. Use the following approach:

#### macOS/Windows
```bash
# Set API URL using host.docker.internal
export INTERLYNK_API_URL=http://host.docker.internal:3000/lynkapi
export INTERLYNK_SECURITY_TOKEN=your_test_token_here

# Run Docker with both environment variables
docker run \
  -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  -e INTERLYNK_API_URL=$INTERLYNK_API_URL \
  -v $(pwd):/app/data \
  ghcr.io/interlynk-io/pylynk upload --prod 'test-product' --sbom /app/data/test-sbom.json
```

#### Linux
On Linux, use the `--network="host"` flag:
```bash
export INTERLYNK_API_URL=http://localhost:3000/lynkapi
export INTERLYNK_SECURITY_TOKEN=your_test_token_here

docker run \
  --network="host" \
  -e INTERLYNK_SECURITY_TOKEN=$INTERLYNK_SECURITY_TOKEN \
  -e INTERLYNK_API_URL=$INTERLYNK_API_URL \
  -v $(pwd):/app/data \
  ghcr.io/interlynk-io/pylynk upload --prod 'test-product' --sbom /app/data/test-sbom.json
```

# Other SBOM Open Source tools
- [SBOM Assembler](https://github.com/interlynk-io/sbomasm) - A tool to compose a single SBOM by combining other (part) SBOMs
- [SBOM Quality Score](https://github.com/interlynk-io/sbomqs) - A tool for evaluating the quality and completeness of SBOMs
- [SBOM Search Tool](https://github.com/interlynk-io/sbomagr) - A tool to grep style semantic search in SBOMs
- [SBOM Explorer](https://github.com/interlynk-io/sbomex) - A tool for discovering and downloading SBOM from a public repository

# Contact
We appreciate all feedback. The best ways to get in touch with us:
- :phone: [Live Chat](https://www.interlynk.io/#hs-chat-open)
- 📫 [Email Us](mailto:hello@interlynk.io)
- 🐛 [Report a bug or enhancement](https://github.com/interlynk-io/sbomex/issues)
- :x: [Follow us on X](https://twitter.com/InterlynkIo)

# Stargazers

If you like this project, please support us by starring it.

[![Stargazers](https://starchart.cc/interlynk-io/pylynk.svg)](https://starchart.cc/interlynk-io/pylynk)



