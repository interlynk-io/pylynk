# PyLynk
Interlynk Python Command line utility

Getting started with Interlynk CLI
Once you have installed the PyLynk CLI, you can verify it's working by running:

```sh
python3 pylynk.py --help
```

See the full PyLynk CLI help.

## Authenticating PyLynk CLI
PyLynk can be authenticated by setting an environment variable `INTERLYNK_SECURITY_TOKEN` or by providing `-token` param to all commands

## Listing Products
Run following command to list existing products:
```bash
python3 pylynk.py prods
```

## Uploading SBOM
Run following command to upload an SBOM:
```bash
python3 pylynk.py sbom --sbom /sboms/product1.cdx.json --prod product1
```

##  Increasing Verbosity of out
Use `--verbose` or `-v` `-vv` or `-vvv` with any command to see verbose output
