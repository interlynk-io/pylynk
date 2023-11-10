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
import datetime
import requests
import paramiko
import pytz
import tzlocal
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


def user_time(utc_time):
    """
    Converts a UTC timestamp to the local timezone and returns it
    in the format 'YYYY-MM-DD HH:MM:SS TZ'.

    Args:
      utc_time (str): The UTC timestamp to convert.

    Returns:
      str: The local time in the format 'YYYY-MM-DD HH:MM:SS TZ'.
    """
    timestamp = datetime.datetime.fromisoformat(utc_time[:-1])
    local_timezone = tzlocal.get_localzone()
    local_time = timestamp.replace(tzinfo=pytz.UTC).astimezone(local_timezone)
    return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')


def product_by_name(data_json, prod_name):
    """
    Returns the project node by name from JSON data

    Args:
      data_json (dict): The JSON data to search.
      prod_name (str): The name of the project to find.

    Returns:
      dict or None: The project node or None if not found.
    """
    nodes = data_json["data"]["projects"]["nodes"]
    return next((node for node in nodes
                 if node["name"] == prod_name), None)


def product_by_id(data_json, prod_id):
    """
    Finds the project node in the given JSON response that matches
    the given product ID.

    Args:
      data_json (dict): The JSON response from the Interlynk API.
      prod_id (str): The ID of the product to match.

    Returns:
      dict or None: The project node that matches the given ID, or None
        if no match was found.
    """
    nodes = data_json["data"]["projects"]["nodes"]
    return next((node for node in nodes if node["id"] == prod_id), None)


def product_version_by_name(data_json, product, version):
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
    prod = product_by_name(data_json, product)

    return next((sbom for index, sbom in enumerate(
        prod['sboms']
    ) if sbom.get('primaryComponent') and
       sbom['primaryComponent']['version'] == version),
       None)


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


def upload(file, product, product_id, token):
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
    if product_id is not None:
        prod = product_by_id(data_json, product_id)
    else:
        prod = product_by_name(data_json, product)

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
                print('Uploaded successfully')
                logging.debug("SBOM Uploading response: %s", response.text)
                return 0
            logging.error("Error uploading sbom: %d", response.status_code)
    except requests.exceptions.RequestException as ex:
        logging.error("RequestException: %s", ex)
    except FileNotFoundError as ex:
        logging.error("FileNotFoundError: %s", ex)
    return 1


def download_sbom(product, version, token):
    """
    Downloads an SBOM file for a specific product and version

    Args:
      product (str): The name of the product to download the SBOM for.
      version (str): The version of the product to download the SBOM for.
      token (str): The authentication token to use for the API request.

    Returns:
      The SBOM file contents as a string, or None if the download failed.
    """
    products_json = products(token)
    if not products_json:
        logging.error("No product found with the name %s", product)
        return 1
    prod, ver = product_version_by_name(products_json,
                                        product,
                                        version)
    if prod is None or ver is None:
        logging.error("No match with name %s, version %s", product, version)
        return 1

    product_id = prod.get('id', None)
    version_id = ver.get('id', None)

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

    response = requests.post(INTERLYNK_API_URL,
                             headers={"Authorization": "Bearer " + token},
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
    # if rsa_key.verify_ssh_sig(bytes(sbom, 'utf-8'),
    #                           Message(base64.b64decode(signature_text))):
    #     print("Signature is valid")
    # else:
    #     print("Signature is not valid")

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
    print(f"{'ID':<40} {'PRODUCT NAME':<30} {'VERSIONS':<4} \
          {'UPDATED AT'}")
    for prod in prod_nodes:
        print(f"{prod['id']:<40} {prod['name']:<30} {len(prod['sboms']):<4} \
              {user_time(prod['updatedAt'])}")
    return 0


def list_versions(token, prod, prod_id=None):
    """
    Lists the available versions for a given product.

    Args:
      token (str): The authentication token to use for the API request.
      prod (str): The name of the product to list versions for.

    Returns:
      int: 0 for success, 1 otherwise
    """
    products_json = products(token)
    if not products_json:
        logging.error("No products found")
        return 1

    if prod_id is not None:
        product = product_by_id(products_json, prod_id)
    else:
        product = product_by_name(products_json, prod)

    if product is None:
        print('No matching product')
        return 0

    print(f"{'ID':<40} {'VERSION':<20} {'PRIMARY COMPONENT':<30}\
          {'UPDATED AT':<20}")
    for sbom in product['sboms']:
        if sbom.get('primaryComponent') is None:
            continue
        version = sbom.get('primaryComponent').get('version', None)
        primary_component = sbom.get('primaryComponent').get('name', None)
        print(f"{sbom['id']:<40} {version:<20} {primary_component:<30} \
              {user_time(sbom['updatedAt']):<20}")
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

    vers_parser = subparsers.add_parser("vers", help="List Versions")
    vers_group = vers_parser.add_mutually_exclusive_group(required=True)

    vers_group.add_argument("--prod", help="Product name")
    vers_group.add_argument("--prodId", help="Product ID")
    vers_parser.add_argument("--token",
                             required=False,
                             help="Security token")

    upload_parser = subparsers.add_parser("upload", help="Upload SBOM")
    arg_group = upload_parser.add_mutually_exclusive_group(required=True)
    arg_group.add_argument("--prod", help="Product name")
    arg_group.add_argument("--prodId", help="Product ID")

    upload_parser.add_argument("--sbom", required=True, help="SBOM path")
    upload_parser.add_argument("--token",
                               required=False,
                               help="Security token")

    download_parser = subparsers.add_parser("download", help="Download SBOM")
    arg_group = download_parser.add_mutually_exclusive_group(required=True)
    arg_group.add_argument("--prod", help="Product name")
    arg_group.add_argument("--prodId", help="Product ID")

    arg_group = download_parser.add_mutually_exclusive_group(required=True)
    arg_group.add_argument("--ver", help="Version")
    arg_group.add_argument("--verId", help="Version ID")

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

    if token is None:
        logging.error("Missing security token")
        return 1

    if args.subcommand == "prods":
        logging.debug("Fetching Product list")
        return list_products(token)
    if args.subcommand == "vers":
        logging.debug("Fetching Version list")
        return list_versions(token, args.prod, args.prodId)
    if args.subcommand == "upload":
        logging.debug("Uploading SBOM %s for product %s", args.sbom, args.prod)
        return upload(args.sbom, args.prod, args.prodId, token)
    if args.subcommand == "download":
        logging.debug("Downloading SBOM %s for product %s, version %s",
                      args.prod,
                      args.ver,
                      args.token)
        return download(args.prod, args.prodId, args.ver, args.verId, token)
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
