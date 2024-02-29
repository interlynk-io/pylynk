# PyLynk
Interlynk Python Command line utility

Getting started with Interlynk CLI
Once you have installed the PyLynk CLI, you can verify it's working by running:

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
python3 pylynk.py
```
Output
```
NAME             | ID                                   | VERSIONS | UPDATED AT              |
---------------------------------------------------------------------------------------------
PSA3000 Firmware | f995875c-43f1-4f3b-b8dc-20cb166653e6 | 2        | 2024-02-28 01:43:57 PST |
ProductX         | 30911a38-98cd-4734-b794-2085671aa1ca | 1        | 2024-02-18 17:01:34 PST |
sbom-exec        | 0bcdcc92-c3db-47fa-a554-236ea1974817 | 3        | 2024-02-18 17:01:22 PST |
sbom-zen         | 577eee34-98a9-4c99-bab0-bf7592e05c5f | 1        | 2024-02-18 17:01:19 PST |
Test Project 3   | 137cdf61-a99c-42ca-b6c6-449bf5aa24cd | 0        | 2024-02-14 09:09:33 PST |
```

# List Environments
TBD

# List Versions 
## List Versions by Product ID (default Environment)
```bash
python3 pylynk.py vers --prodId 'f995875c-43f1-4f3b-b8dc-20cb166653e6'
```
Output
```bash
ID                                   | VERSION          | PRIMARY COMPONENT | UPDATED AT              |
------------------------------------------------------------------------------------------------------
5ad77318-56e9-4bfa-9147-d28d0c76dc1c | 9.1.18.2-24467.1 | ICS               | 2024-02-20 02:58:35 PST
```
## List Versions by Product Name (default Environment)
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
## List Versions for specific Environment Name
```bash
python3 pylynk.py vers --prod 'PSA3000 Firmware' --env 'development'
```
Output
```bash
ID                                   | VERSION | PRIMARY COMPONENT | UPDATED AT              |
---------------------------------------------------------------------------------------------|
5c374ad9-2e74-4043-87d8-652982fe18b8 |         | .                 | 2024-02-28 01:43:57 PST |
```
## List Versions for specific Environment ID
TBD

# Download SBOM
## Download SBOM for specific Version by ID
Run the following command to upload an SBOM:
```bash
python3 pylynk.py download --prod 'sbom-exec' --verId '5a46ab07-174f-4074-b4af-f8f83a17b822'
```
## Download SBOM for specific Version by Name
Run the following command to upload an SBOM:
```bash
python3 pylynk.py -v download --prod 'sbom-exec' --env 'production' --ver '1.0.1'
```
# Upload SBOM
## Upload SBOM
Run the following command to upload an SBOM:
```bash
python3 pylynk.py upload --prod 'sbom-exec' --sbom lynk-api.cdx.json
```
## Upload SBOM to specific Environment
Run the following command to upload an SBOM:
```bash
python3 pylynk.py upload --prod 'sbom-exec' --env 'production' --sbom lynk-dash-app.cdx.json
```


##  Increasing Verbosity of out
Use `--verbose` or `-v` with any command to see debug output.
