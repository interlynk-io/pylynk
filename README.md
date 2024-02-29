# PyLynk
Interlynk Python Command line utility

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
## Upload SBOM to specific environment
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
