# Copyright 2023 Interlynk.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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


def product_index(data_json, product):
    """
    Finds the index of the project node in the given JSON response
    that matches the given product name.

    Args:
      data_json (dict): The JSON response from the Interlynk API.
      product (str): The name of the product to match.

    Returns:
      int or None: The index of the matched project node, or
      None if no match was found.
    """
    return next((index for index, node in enumerate(
        data_json["data"]["projects"]["nodes"]
    ) if node["name"] == product), None)


def product_node(data_json, index):
    """
    Returns the project node at the given index in the JSON response.

    Args:
      data_json (dict): The JSON response from the Interlynk API.
      index (int): The index of the project node to return.

    Returns:
      dict: The project node at the given index.
    """
    return data_json['data']['projects']['nodes'][index]


def product_version_index(data_json, product, version):
    """
    Finds the index of the version node in the given JSON response
    that matches the given product name and version number.

    Args:
      data_json (dict): The JSON response from the Interlynk API.
      product (str): The name of the product to match.
      version (str): The version number to match.

    Returns:
      tuple[int, int] or tuple[None, None]: A tuple containing the
        indices of the matched product and version nodes, or (None, None)
        if no match was found.
    """
    prod_idx = product_index(data_json, product)
    if prod_idx is None:
        return (None, None)

    prod = product_node(data_json, prod_idx)

    return next(((prod_idx, index) for index, sbom in enumerate(
        prod['sboms']
    ) if sbom.get('primaryComponent') and
       sbom['primaryComponent']['version'] == version),
       (None, None))


def version_node(data_json, prod_idx, version_idx):
    """
    Returns the version node at the given index in the JSON response.

    Args:
      data_json (dict): The JSON response from the Interlynk API.
      prod_idx (int): The index of the product containing version node.
      version_idx (int): The index of the version node to return.

    Returns:
      dict: The version node at the given index.
    """
    prod_node = product_node(data_json, prod_idx)
    return prod_node['sboms'][version_idx]


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
    prod_idx = product_index(data_json, product)
    if prod_idx is None:
        logging.error("No product found with the name %s", product)
        return 1
    prod = product_node(data_json, prod_idx)
    product_id = prod.get('id', None)
    if not product_id:
        logging.error("Could not resolve to product ID %s", prod)
        return 1

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


def download_sbom(product, version, token):

    data_json = products(token)
    if not data_json:
        logging.error("No product found with the name %s", product)
        return 1
    prod_idx, version_idx = product_version_index(data_json, product, version)
    if prod_idx is None or version_idx is None:
        logging.error("No match with name %s, version %s", product, version)
        return 1

    product_id = product_node(data_json, prod_idx).get('id', None)
    version_id = version_node(data_json, prod_idx, version_idx).get('id', None)

    if not product_id or not version_id:
        logging.error("Product id or sbom ID is null: %s, %s",
                      product_id, version_id)
        return None
    logging.debug("Downloading SBOM for product ID %s, sbom ID %s",
                  product_id, version_id)

    variables = {
        "projectId": product_id,
        "sbomId": version_id,
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
            return decoded_content.decode('utf-8')
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON response.")
    else:
        logging.error("Failed to send GraphQL request. Status code: %s",
                      response.status_code)
    return None


def download(product, version, token):
    """
    Downloads an SBOM file for a given product and version using the
    provided authentication token.

    Args:
      product (str): The name of the product to download the SBOM for.
      version (str): The version of the product to download the SBOM for.
      token (str): The authentication token to use for the API request.

    Returns:
      0 for success, 1 otherwise
    """

    sbom = download_sbom(product, version, token)
    if sbom is None:
        logging.error("Error fetching SBOM")
        return 1

    print(sbom)
    return 0


def sign(product, version, pem_file, token):
    """
    Signs the SBOM file for a given product and version using the provided
    authentication token and private key file.

    Args:
      product (str): The name of the product to sign the SBOM for.
      version (str): The version of the product to sign the SBOM for.
      pem_file (str): The path to the private key file to use for signing.
      token (str): The authentication token to use for the API request.

    Returns:
      The base64-encoded signature for the SBOM file,
      or None if signing failed.
    """
    sbom = download_sbom(product, version, token)
    if not sbom:
        logging.error("SBOM content is empty")
        return 1

    rsa_key = paramiko.RSAKey(filename=pem_file, password=None)
    signature = rsa_key.sign_ssh_data(bytes(sbom, 'utf-8'))
    signature_text = base64.b64encode(signature.asbytes()).decode('utf-8')
    print(signature_text)
    if rsa_key.verify_ssh_sig(bytes(sbom, 'utf-8'),
                              Message(base64.b64decode(signature_text))):
        print("Signature is valid")
    else:
        print("Signature is not valid")

    return 0


def verify(product, version, pem_file, signature, token):
    """
    Validates the signature of the SBOM file for a given product and
    version using the provided authentication token and public key file.

    Args:
      product (str): The product name to validate the SBOM signature for.
      version (str): The product version to validate the SBOM signature for.
      pem_file (str): The public key file to use for signature validation.
      signature (str): The base64-encoded signature to validate.
      token (str): The authentication token to use for the API request.

    Returns:
      0 for success, 1 otherwise
    """

    sbom = download_sbom(product, version, token)
    if not sbom:
        logging.error("SBOM content is empty")
        return 1

    rsa_key = paramiko.RSAKey(filename=pem_file, password=None)
    if rsa_key.verify_ssh_sig(bytes(sbom, 'utf-8'),
                              Message(base64.b64decode(signature))):
        print("Signature is valid")
    else:
        print("Signature is not valid")

    return 0


def list_products(token):
    """
    Print the Interlynk list of products using the provided token.

    Args:
      token (str): The authentication token to use for the API request.

    Returns:
      0 for success 1 otherwise
    """
    products_json = products(token)
    if not products_json:
        logging.error("No products found")
        return 1

    prod_nodes = products_json['data']['projects']['nodes']
    print("ID\t\t\t\t\tPRODUCT NAME")
    for prod in prod_nodes:
        print(f"{prod['id']}\t{prod['name']}")
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
        logging.debug("Fetching Product list")
        return list_products(token)
    if args.subcommand == "upload":
        logging.debug("Uploading SBOM %s for product %s", args.sbom, args.prod)
        return upload_sbom(args.sbom, args.prod, token)
    if args.subcommand == "download":
        logging.debug("Downloading SBOM %s for product %s, version %s",
                      args.prod,
                      args.ver,
                      args.token)
        return download(args.prod, args.ver, token)
    if args.subcommand == "sign":
        logging.debug("Signing SBOM for product %s, version %s",
                      args.prod,
                      args.ver)
        return sign(args.prod, args.ver, args.key, token)
    if args.subcommand == "verify":
        logging.debug("Verifying SBOM for product %s, version %s",
                      args.prod,
                      args.ver)
        return verify(args.prod, args.ver, args.key, args.signature,
                      token)

    logging.error("Missing or invalid command. \
                  Supported commands: {prods, upload, download, sign, verify}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
