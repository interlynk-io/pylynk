<!--
 Copyright 2024 Interlynk.io

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

`pylynk` is your primary tool to interface with interlynk's SAAS platform. 

```sh
git clone https://github.com/interlynk-io/pylynk
pip3 install -r requirements.txt
python3 pylynk.py --help
````
or 

```sh
docker pull ghcr.io/interlynk-io/pylynk:latest
```
# Usage

### Authenticate
PyLynk can be authenticated by setting an environment variable `INTERLYNK_SECURITY_TOKEN` or by providing a `-token` param to all commands.
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
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk prods
```


## List Products
```bash
python3 pylynk.py prods --table
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk prods --table 
```

## List Products as JSON
```bash
python3 pylynk.py prods --json
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk prods --json
```

## List Versions
### List Versions by product ID (default environment)
```bash
python3 pylynk.py vers --prodId 'e865710e-b262-4f44-9078-970052794a60' --table
```
OR 

```bash
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk  vers --prodId 'e865710e-b262-4f44-9078-970052794a60' --table
```

### List Versions by product ID (default environment) as JSON
```bash
python3 pylynk.py vers --prodId 'e865710e-b262-4f44-9078-970052794a60' --json
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk  vers --prodId 'e865710e-b262-4f44-9078-970052794a60' --json
```

### List Versions by product name (default environment)
```bash
python3 pylynk.py vers --prod 'sbom-exec' --table
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk  vers --prod 'sbom-exec' --table
```


### List Versions for specific environment by name
```bash
python3 pylynk.py vers --prod 'sbomqs' --env 'production' --table
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk  vers --prod 'sbomqs' --env 'production' --table
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
python3 pylynk.py status --prodId 'e865710e-b262-4f44-9078-970052794a60' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```


## Download SBOM

### Download SBOM for specific version by version ID
Run the following command to upload an SBOM:
```bash
python3 pylynk.py download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```
OR 
```bash
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```

### Download SBOM for specific version by version name
Run the following command to upload an SBOM:
```bash
python3 pylynk.py download --prod 'sbomex' --env 'default' --vers 'sha256:5ed7e95ae79fe3fe6c4b8660f6f9e31154e64eca76ae42963a679fbb198c3951'
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk download --prod 'sbomex' --env 'default' --vers 'sha256:5ed7e95ae79fe3fe6c4b8660f6f9e31154e64eca76ae42963a679fbb198c3951'
```

## Upload SBOM
### Upload SBOM to the default environment
Upload SBOM file sbomqs.cdx.json to the product named **sbomqs**
```bash
python3 pylynk.py upload --prod 'sbomqs' --sbom sbomqs.cdx.json
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk upload --prod 'sbomqs' --sbom sbomqs.cdx.json
```


### Upload SBOM to a specific environment
Upload SBOM file sbomqs.cdx.json to the product named **sbomqs** under environment **production**
```bash
python3 pylynk.py upload --prod 'sbomqs' --env 'production' --sbom sbomqs.cdx.json
```
OR
```bash
docker run -e INTERLYNK_SECURITY_TOKEN  ghcr.io/interlynk-io/pylynk upload --prod 'sbomqs' --env 'production' --sbom sbomqs.cdx.json
```

###  Increasing the verbosity of output
Use `--verbose` or `-v` with any command to see debug output.


###  Debugging
To point to a different API endpoint than production
```bash
export INTERLYNK_API_URL=http://localhost:3000/lynkapi
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



