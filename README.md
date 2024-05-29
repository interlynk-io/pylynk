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

# `pylynk`: Interlynk Python Command line utility

Getting started with Interlynk CLI

# Setup
```bash
git clone https://github.com/interlynk-io/pylynk
```

Once cloned, cd and install requirements
```bash
cd pylynk
```

```bash
pip3 install -r requirements.txt
```

Verify it's working by running:

```sh
python3 pylynk.py --help
```

See the full PyLynk CLI help.

# Authenticate
PyLynk can be authenticated by setting an environment variable `INTERLYNK_SECURITY_TOKEN` or by providing a `-token` param to all commands.
```bash
export INTERLYNK_SECURITY_TOKEN=lynk_test_GDGEB2j6jnhkzLSAQk9U3wiiQLrbNT11Y8J4
```

OR
```bash
python3 pylynk.py prods --token lynk_test_GDGEB2j6jnhkzLSAQk9U3wiiQLrbNT11Y8J4
```


# List Products
```bash
python3 pylynk.py prods
```
Output
```
NAME   | ID                                   | VERSIONS | UPDATED AT              |
-----------------------------------------------------------------------------------|
sbomqs | 478ba2d2-ec5c-4eec-afb7-85a72fe17bd3 | 1        | 2024-02-29 01:07:59 PST |
sbomex | e865710e-b262-4f44-9078-970052794a60 | 1        | 2024-02-29 01:05:24 PST |

```
# List Products as JSON
```bash
python3 pylynk.py prods --json
```
Output
```
[
    {
        "name": "sbomqs",
        "updatedAt": "2024-02-29T09:07:59Z",
        "id": "478ba2d2-ec5c-4eec-afb7-85a72fe17bd3",
        "versions": 1
    },
    {
        "name": "sbomex",
        "updatedAt": "2024-02-29T09:05:24Z",
        "id": "e865710e-b262-4f44-9078-970052794a60",
        "versions": 1
    }
]
```

# List Environments
TBD

# List Versions 
## List Versions by product ID (default environment)
```bash
python3 pylynk.py vers --prodId 'e865710e-b262-4f44-9078-970052794a60'
```
Output
```bash
ID                                   | VERSION                                                                 | PRIMARY COMPONENT     | UPDATED AT              |
-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
fbcc24ad-5911-4229-8943-acf863c07bb4 | sha256:5ed7e95ae79fe3fe6c4b8660f6f9e31154e64eca76ae42963a679fbb198c3951 | centos:centos7.9.2009 | 2024-02-29 01:05:24 PST |
```
## List Versions by product ID (default environment) as JSON
```bash
python3 pylynk.py vers --prodId 'e865710e-b262-4f44-9078-970052794a60' --json
```
Output
```bash
[
    {
        "id": "fbcc24ad-5911-4229-8943-acf863c07bb4",
        "vulnRunStatus": "FINISHED",
        "updatedAt": "2024-02-29T09:05:24Z",
        "primaryComponent": {
            "name": "centos:centos7.9.2009",
            "version": "sha256:5ed7e95ae79fe3fe6c4b8660f6f9e31154e64eca76ae42963a679fbb198c3951"
        }
    }
]
```
## List Versions by product name (default environment)
```bash
python3 pylynk.py vers --prod 'sbom-exec'
```
Output
```bash
ID                                   | VERSION | PRIMARY COMPONENT       | UPDATED AT              |
---------------------------------------------------------------------------------------------------|
e0b1fb60-03de-4202-b316-51422351b96b | 1.3     | agdfda                  | 2024-02-18 17:01:17 PST |
2f576a83-0918-4749-86a8-3788dd8fd26d | 1.1     | xxx                     | 2024-02-18 17:01:17 PST |
5a46ab07-174f-4074-b4af-f8f83a17b822 | 1.0.1   | Implantatron Programmer | 2024-02-18 17:01:22 PST |
```
## List Versions for specific environment by name
```bash
python3 pylynk.py vers --prod 'sbomqs' --env 'production'
```
Output
```bash
ID                                   | VERSION                                                                 | PRIMARY COMPONENT     | UPDATED AT              |
-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
6067a2f0-76b1-4b51-97cf-cc01175d66c4 | sha256:5ed7e95ae79fe3fe6c4b8660f6f9e31154e64eca76ae42963a679fbb198c3951 | centos:centos7.9.2009 | 2024-02-29 00:59:11 PST |
```
## List Versions for specific environment ID
TBD

# Status of a specific version 
Possible Version Status values are:
1. CHECKS_IN_PRORGRESS
2. VULN_SCAN_IN_PROGRESS
3. VULN_SCAN_COMPLETED
4. UNKNOWN_STATUS

## Status of a specific version by version ID
```bash
python3 pylynk.py status --prodId 'e865710e-b262-4f44-9078-970052794a60' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```
Output
```bash
VULN_SCAN_COMPLETED
```

# Download SBOM
## Download SBOM for specific version by version ID
Run the following command to upload an SBOM:
```bash
python3 pylynk.py download --prod 'sbomex' --verId 'fbcc24ad-5911-4229-8943-acf863c07bb4'
```
Output
```bash
{SBOM Data}
```
## Download SBOM for specific version by version name
Run the following command to upload an SBOM:
```bash
python3 pylynk.py download --prod 'sbomex' --env 'default' --vers 'sha256:5ed7e95ae79fe3fe6c4b8660f6f9e31154e64eca76ae42963a679fbb198c3951'
```
Output
```bash
{SBOM Data}
```
# Upload SBOM
## Upload SBOM to the default environment
Upload SBOM file sbomqs.cdx.json to the product named **sbomqs**
```bash
python3 pylynk.py upload --prod 'sbomqs' --sbom sbomqs.cdx.json
```
Output
```
Uploaded successfully
```
## Upload SBOM to a specific environment
Upload SBOM file sbomqs.cdx.json to the product named **sbomqs** under environment **production**
```bash
python3 pylynk.py upload --prod 'sbomqs' --env 'production' --sbom sbomqs.cdx.json
```
Output
```
Uploaded successfully
```

##  Increasing the verbosity of output
Use `--verbose` or `-v` with any command to see debug output.


##  Debugging 
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



