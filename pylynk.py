"""
This module contains functions for interacting with the Interlynk API.
"""

import os
import sys
import json
import argparse
import logging
import base64
import requests
import paramiko
import hashlib
from paramiko.message import Message

INTERLYNK_API_URL = 'https://api.interlynk.io/lynkapi'
INTERLYNK_API_TIMEOUT = 100

QUERY_PROJECTS_LIST = """
query GetProjects($first: Int, $last: Int, $after: String, $before: String) {
  projects(first: $first, last: $last, after: $after, before: $before) {
    pageInfo {
      endCursor
      hasNextPage
      startCursor
      hasPreviousPage
      __typename
    }
    nodes {
      id
      name
      description
      updatedAt
      organizationId
      sboms {
        id
        format
        updatedAt
        primaryComponent {
          id
          name
          version
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}
"""

QUERY_SBOM_UPLOAD = """
mutation uploadSbom($doc: Upload!, $projectId: ID!) {
  sbomUpload(
    input: {
      doc: $doc,
      projectId: $projectId
    }
  ) {
    errors
  }
}
"""

QUERY_SBOM_DOWNLOAD = """
query downloadSbom($projectId: Uuid!, $sbomId: Uuid!, $spec: String,
  $format: String, $includeVulns: Boolean, $includeVex: Boolean,
  $original: Boolean) {
  sbom(projectId: $projectId, sbomId: $sbomId) {
    download(
      sbomId: $sbomId
      spec: $spec
      format: $format
      includeVulns: $includeVulns
      includeVex: $includeVex
      original: $original
    )
    __typename
  }
}
"""

QUERY_PROJECT_PARAMS = {
    'operationName': 'GetProjects',
    'variables': {},
    'query': QUERY_PROJECTS_LIST
    }


def match_product_id(data_json, product):
    for node in data_json["data"]["projects"]["nodes"]:
        if node["name"] == product:
            return node["id"]
    return None


def match_product_sbom_id(data_json, product, version):

    for node in data_json["data"]["projects"]["nodes"]:
        if node["name"] == product:
            sbom_list = node["sboms"]
            for sbom in sbom_list:
                sbom_component = sbom["primaryComponent"]
                if sbom_component["version"] == version:
                    return node["id"], sbom["id"]
    return None, None


def products(token):
    """
    Fetches the Interlynk list of products using the provided token.

    Args:
      token (str): The authentication token to use for the API request.

    Returns:
      json_map
    """
    headers = {
      "Authorization": "Bearer " + token
    }
    try:
        response = requests.post(INTERLYNK_API_URL,
                                 headers=headers,
                                 data=QUERY_PROJECT_PARAMS,
                                 timeout=INTERLYNK_API_TIMEOUT)
        if response.status_code == 200:
            response_data = response.json()
            logging.debug("Products response type: %s", type(response_data))
            return response_data
        logging.error("Error fetching products: %s", response.status_code)
    except requests.exceptions.RequestException as ex:
        logging.error("RequestException:  %s", ex)
    except json.JSONDecodeError as ex:
        logging.error("JSONDecodeError: %s", ex)

    return None


def upload_sbom(file, product, token):
    """
    Uploads an SBOM file to a product using the Interlynk API.

    Args:
      file (str): The path to the SBOM file to upload.
      product (str): The ID of the product to upload the SBOM to.
      token (str): The authentication token to use for the API request.

    Returns:
      0 for success 1 otherwise
    """
    if os.path.isfile(file) is False:
        logging.error('SBOM File not found')
        return 1

    data_json = products(token)
    if data_json is None:
        logging.error("No product found with the name %s", product)
        return 1
    product_id = match_product_id(data_json, product)
    logging.debug("Uploading SBOM to product ID %s", product_id)

    headers = {
      "Authorization": "Bearer " + token
    }

    operations = json.dumps({
      "query": QUERY_SBOM_UPLOAD,
      "variables": {"doc": None, "projectId": product_id}
    })
    map_data = json.dumps({"0": ["variables.doc"]})

    form_data = {
      "operations": operations,
      "map": map_data
    }

    try:
        with open(file, 'rb') as sbom:
            files_map = {'0': sbom}
            response = requests.post(INTERLYNK_API_URL,
                                     headers=headers,
                                     data=form_data,
                                     files=files_map,
                                     timeout=INTERLYNK_API_TIMEOUT)
            if response.status_code == 200:
                logging.debug("SBOM Uploading response: %s", response.text)
                return 0
            logging.error("Error uploading sbom: %d", response.status_code)
    except requests.exceptions.RequestException as ex:
        logging.error("RequestException: %s", ex)
    except FileNotFoundError as ex:
        logging.error("FileNotFoundError: %s", ex)
    return 1


def download_sbom(product_id, sbom_id, token):
    """
    Downloads an SBOM file from using the provided authentication token.

    Args:
      token (str): The authentication token to use for the API request.

    Returns:
      The downloaded SBOM file as a or None if the download failed.
    """
    variables = {
        "projectId": product_id,
        "sbomId": sbom_id,
        "spec": "cyclonedx",
        "format": "json",
        "includeVulns": False,
        "includeVex": False,
        "original": False,
    }

    request_data = {
        "query": QUERY_SBOM_DOWNLOAD,
        "variables": variables,
    }

    headers = {
      "Authorization": "Bearer " + token
    }

    response = requests.post(INTERLYNK_API_URL,
                             headers=headers,
                             json=request_data,
                             timeout=INTERLYNK_API_TIMEOUT)

    if response.status_code == 200:
        try:
            data = response.json()

            if "errors" in data:
                logging.error("GraphQL response contains errors:")
                for error in data["errors"]:
                    logging.error(error["message"])
                return None

            b64data = data.get("data", {}).get("sbom", {}).get("download")
            decoded_content = base64.b64decode(b64data)
            logging.debug('Completed download and decoding')
            return decoded_content
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON response.")
    else:
        logging.error("Failed to send GraphQL request. Status code: %s",
                      response.status_code)
    return None


def download(product, version, token):
    data_json = products(token)
    if not data_json:
        logging.error("No products found")
        return 1
    product_id, sbom_id = match_product_sbom_id(data_json, product, version)
    if not product_id or not sbom_id:
        logging.error("No match with name %s, version %s", product, version)
        return 1

    sbom = download_sbom(product_id, sbom_id, token)
    print(sbom)
    return 0


def sign(product, version, pem_file, token):
    mykey = paramiko.RSAKey(filename=pem_file, password=None)
    data_json = products(token)
    if not data_json:
        logging.error("No products found")
        return 1
    product_id, sbom_id = match_product_sbom_id(data_json, product, version)
    if not product_id or not sbom_id:
        logging.error("No match with name %s, version %s", product, version)
        return 1

    sbom = download_sbom(product_id, sbom_id, token)
    if not sbom:
        logging.error("SBOM content is empty")
        return 1

    signature_message = mykey.sign_ssh_data(sbom)
    logging.debug("Signature (Message encoded): %s", signature_message)
    signature = signature_message.asbytes()
    encoded_signature = base64.b64encode(signature)
    print(encoded_signature.decode('utf-8'))

    return 0


def validate(product, version, pem_file, signature, token):
    mykey = paramiko.RSAKey(filename=pem_file, password=None)
    data_json = products(token)
    if not data_json:
        logging.error("No products found")
        return 1
    product_id, sbom_id = match_product_sbom_id(data_json, product, version)
    if not product_id or not sbom_id:
        logging.error("No match with name %s, version %s", product, version)
        return 1

    sbom = download_sbom(product_id, sbom_id, token)
    if not sbom:
        logging.error("SBOM content is empty")
        return 1

    hash_obj = hashlib.sha256()
    hash_obj.update(sbom)
    data_hash = hash_obj.digest()
    logging.debug("Data hash: %s, signature: %s", data_hash, base64.b64decode(signature))

    try:
        if mykey.verify_ssh_sig(sbom, Message(base64.b64decode(signature))):
            print("Signature is valid")
            return True
        else:
            print("Signature is not valid")
            return 1
    except Exception as e:
        logging.error(f"Error validating signature: {str(e)}")
        return 1

    return 0

def print_products(token):
    """
    Print the Interlynk list of products using the provided token.

    Args:
      token (str): The authentication token to use for the API request.

    Returns:
      0 for success 1 otherwise
    """
    products_map = products(token)
    if not products_map:
        logging.error("No products found")
        return 1

    print("ID\t\t\t\t\tPRODUCT NAME")
    for prod_name, prod_id in products_map.items():
        print(f"{prod_id}\t{prod_name}")
    return 0


def setup_args():
    """
    Setup command line arguments

    Returns:
      argparse: The parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Interlynk command line tool')
    parser.add_argument('--verbose', '-v', action='count', default=0)

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    products_parser = subparsers.add_parser("prods", help="List products")
    products_parser.add_argument("--token",
                                 required=False,
                                 help="Security token")

    upload_parser = subparsers.add_parser("upload", help="Upload SBOM")
    upload_parser.add_argument("--prod", required=True, help="Product name")
    upload_parser.add_argument("--sbom", required=True, help="SBOM path")
    upload_parser.add_argument("--token",
                               required=False,
                               help="Security token")

    download_parser = subparsers.add_parser("download", help="Download SBOM")
    download_parser.add_argument("--prod", required=True, help="Product name")
    download_parser.add_argument("--ver", required=True, help="Version")
    download_parser.add_argument("--token",
                                 required=False,
                                 help="Security token")

    sign_parser = subparsers.add_parser("sign", help="Sign SBOM")
    sign_parser.add_argument("--prod", required=True, help="Product name")
    sign_parser.add_argument("--ver", required=True, help="Product version")
    sign_parser.add_argument("--key", required=True, help="Private key")
    sign_parser.add_argument("--token",
                             required=False,
                             help="Security token")

    verify_parser = subparsers.add_parser("verify", help="Verify signature")
    verify_parser.add_argument("--prod", required=True, help="Product name")
    verify_parser.add_argument("--ver", required=True, help="Product version")
    verify_parser.add_argument("--key", required=True, help="Public key")
    verify_parser.add_argument("--signature", required=True, help="Signature")
    verify_parser.add_argument("--token",
                               required=False,
                               help="Security token")

    args = parser.parse_args()
    return args


def log_level(args):
    """
    Set the logging level from verbose param

    Args:
      args (argparse.Namespace): The parsed command line arguments.

    Returns:
      None
    """
    if args.verbose == 0:
        logging.basicConfig(level=logging.ERROR)
    elif args.verbose == 1:
        logging.basicConfig(level=logging.WARNING)
    elif args.verbose == 2:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose >= 3:
        logging.basicConfig(level=logging.DEBUG)


def main() -> int:
    """
    Run Interlynk Commands

    Returns:
      Error code
    """
    args = setup_args()
    log_level(args)
    token = os.environ.get("INTERLYNK_SECURITY_TOKEN")
    if hasattr(args, 'token') and args.token is not None:
        token = args.token

    if args.subcommand == "prods":
        logging.info("Fetching Product list")
        return print_products(token)
    if args.subcommand == "upload":
        logging.info("Uploading SBOM %s for product %s", args.sbom, args.prod)
        return upload_sbom(args.sbom, args.prod, token)
    if args.subcommand == "download":
        logging.info("Downloading SBOM %s for product %s, version %s",
                     args.prod,
                     args.ver,
                     args.token)
        return download(args.prod, args.ver, token)
    if args.subcommand == "sign":
        logging.info("Signing SBOM %s for product %s, version %s",
                     args.prod,
                     args.ver,
                     args.token)
        return sign(args.prod, args.ver, args.key, token)
    if args.subcommand == "verify":
        logging.info("Verifying SBOM %s for product %s, version %s",
                     args.prod,
                     args.ver,
                     args.signature,
                     args.token)
        return validate(args.prod, args.ver, args.key, args.signature, token)


    if args.subcommand in ["sign", "verify"]:
        logging.error("Not implemented")
        return 1

    if args.subcommand in ["sign", "verify"]:
        logging.error("Not implemented")
        return 1

    logging.error("Missing or invalid command. \
                  Supported commands: {upload,prods}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
