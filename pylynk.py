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

INTERLYNK_API_URL = 'http://localhost:3000/lynkapi'
INTERLYNK_API_TIMEOUT = 100

QUERY_PRODUCTS_LIST = """
query GetProducts($enabled: Boolean) {
  organization {
    products: projectGroups(
      enabled: $enabled
    ) {
      totalCount
      nodes {
        prodId: id
        prodName: name
        prodUpdateAt: updatedAt
        prodEnabled: enabled
        environments: projects {
          envId: id
          envName: name
          versions: sboms {
            id
            updatedAt
            primaryComponent {
              name
              version
            }
          }
        }
      }
    }
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
    'operationName': 'GetProducts',
    'variables': {},
    'query': QUERY_PRODUCTS_LIST
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
    nodes = data_json['data']['organization']['products']['nodes']
    return next((node for node in nodes
                 if node['prodName'] == prod_name), None)


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
    nodes = data_json["data"]["organization"]["products"]["nodes"]
    return next((node for node in nodes if node["prodId"] == prod_id), None)


def product_version_by_name(data_json, prod_id, version):
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
    prod = product_by_id(data_json, prod_id)
    if prod is None:
        return None

    return next((sbom for index, sbom in enumerate(
        prod['sboms']
    ) if sbom.get('primaryComponent') and
       sbom['primaryComponent']['version'] == version),
       None)


def product_version_by_id(data_json, product_id, version_id):
    """
    Finds the index of the version node in the given JSON response
    that matches the given product ID and version number.

    Args:
      data_json (dict): The JSON response from the Interlynk API.
      product_id (str): The ID of the product to match.
      version_id (str): The version number to match.

    Returns:
      tuple[int, int] or tuple[None, None]: A tuple containing the
        indices of the matched product and version nodes, or (None, None)
        if no match was found.
    """
    prod = product_by_id(data_json, product_id)

    return next((sbom for index, sbom in enumerate(
        prod['sboms']
    ) if sbom.get('primaryComponent') and
       sbom['primaryComponent']['version'] == version_id),
       None)


def product_env_by_name(data_json, prod_id, env):
    prod = product_by_id(data_json, prod_id)
    if prod is None:
        return None

    return next((env_node for index, env_node in enumerate(
        prod['environments']
    ) if env_node.get('envName') == env),
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


def upload_sbom(token, product_id, sbom_file):
    """
    Uploads an SBOM file to a product using the Interlynk API.

    Args:
      file (str): The path to the SBOM file to upload.
      product (str): The ID of the product to upload the SBOM to.
      token (str): The authentication token to use for the API request.

    Returns:
      0 for success 1 otherwise
    """
    if os.path.isfile(sbom_file) is False:
        logging.error('SBOM File not found: %s', sbom_file)
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
        with open(sbom_file, 'rb') as sbom:
            files_map = {'0': sbom}
            response = requests.post(INTERLYNK_API_URL,
                                     headers=headers,
                                     data=form_data,
                                     files=files_map,
                                     timeout=INTERLYNK_API_TIMEOUT)
            if response.status_code == 200:
                resp_json = response.json()
                errors = resp_json.get('data').get('sbomUpload').get('errors')
                if errors is not None and errors != '[]':
                    print(f"Error uploading sbom: {errors}")
                    return 1
                print('Uploaded successfully')
                logging.debug("SBOM Uploading response: %s", response.text)
                return 0
            logging.error("Error uploading sbom: %d", response.status_code)
    except requests.exceptions.RequestException as ex:
        logging.error("RequestException: %s", ex)
    except FileNotFoundError as ex:
        logging.error("FileNotFoundError: %s", ex)
    return 1


def download(token, product_id, version_id):
    """
    Downloads an SBOM file for a specific product and version

    Args:
      product (str): The name of the product to download the SBOM for.
      version (str): The version of the product to download the SBOM for.
      token (str): The authentication token to use for the API request.

    Returns:
      The SBOM file contents as a string, or None if the download failed.
    """
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

            sbom = data.get('data', {}).get('sbom', {})
            if sbom is None:
                print('No SBOM matched with the given ID')
                return None
            b64data = sbom.get('download')
            decoded_content = base64.b64decode(b64data)
            logging.debug('Completed download and decoding')
            return decoded_content.decode('utf-8')
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON response.")
    else:
        logging.error("Failed to send GraphQL request. Status code: %s",
                      response.status_code)
    return None


def download_sbom(token, product_id, version_id):
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

    sbom = download(token, product_id, version_id)
    if sbom is None:
        logging.error("Error fetching SBOM")
        return 1

    print(sbom)
    return 0


def print_signature(token, product_id, ver_id, pem_file):
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
    sbom = download_sbom(token, product_id, ver_id)
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


def verify_signature(token, product_id, version_id, signature, pem_file):
    """
    Verifies the signature of an SBOM for a given product and version using
    the provided authentication token, signature, and public key file.

    Args:
      token (str): The authentication token to use for the API request.
      product_id (str): The ID of the product to verify the SBOM signature for.
      version_id (str): The ID of the version to verify the SBOM signature for.
      signature (str): The base64-encoded signature to verify.
      pem_file (str): The path to the public key file to use for verification.

    Returns:
      0 for success, 1 otherwise
    """
    sbom = download_sbom(token, product_id, version_id)
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


def print_products(token):
    """
    Print the Interlynk list of products using the provided token.

    Args:
      token (str): The authentication token to use for the API request.

    Returns:
      0 for success 1 otherwise
    """
    products_json = products(token)
    if (products_json.get('errors')):
        logging.error("Query error: GetProducts")
        return 1
    
    if not products_json:
        logging.error("No products found")
        return 1
    prod_nodes = products_json['data']['organization']['projectGroups']['nodes']

    # Calculate dynamic column widths
    name_width = max(len("NAME"), max(len(prod['name'])
                                       for prod in prod_nodes))
    updated_at_width = max(len("UPDATED AT"),
                           max(len(user_time(prod['updatedAt']))
                               for prod in prod_nodes))
    id_width = max(len("ID"), max(len(prod['id']) for prod in prod_nodes))

    header = (
        f"{ 'NAME':<{name_width}} | "
        f"{ 'ID':<{id_width}} | "
        f"{ 'UPDATED AT':<{updated_at_width}} | "
    )
    print(header)

    # Add a horizontal line after the header
    # 8 is the total length of separators and spaces
    width = sum([name_width, updated_at_width, id_width]) + 8
    line = "-" * width
    print(line)

    for prod in prod_nodes:
        row = (
            f"{prod['name']:<{name_width}} | "
            f"{prod['id']:<{id_width}} | "
            f"{user_time(prod['updatedAt']):<{updated_at_width}} | "
        )
        print(row)
    return 0


def print_versions(token, prod_id, env_id):
    """
    Lists the available versions for a given product.

    Args:
      token (str): The authentication token to use for the API request.
      prod_id (str): The ID of the product to list versions for.

    Returns:
      int: 0 for success, 1 otherwise
    """
    products_json = products(token)
    if not products_json:
        logging.error("No products found")
        return 1

    product_node = product_by_id(products_json, prod_id)
    if product_node is None:
        print('No matching product')
        return 0

    env_node = next((env_node for index, env_node in enumerate(
        product_node['environments']
    ) if env_node['envId'] == env_id),
       None)
    
    # Calculate dynamic column widths
    id_width = max(len("ID"), max(len(sbom['id'])
                                  for sbom in env_node['versions']))
    version_width = max(len("VERSION"),
                        max(len(s.get('primaryComponent', {})
                                .get('version', ''))
                        for s in env_node['versions']))
    primary_component_width = max(len("PRIMARY COMPONENT"),
                                  max(len(sbom.get('primaryComponent', {})
                                          .get('name', ''))
                                      for sbom in env_node['versions']))
    updated_at_width = max(len("UPDATED AT"),
                           max(len(user_time(sbom['updatedAt']))
                               for sbom in env_node['versions']))

    # Format the header with dynamic column widths
    header = (
        f"{'ID':<{id_width}} | "
        f"{'VERSION':<{version_width}} | "
        f"{'PRIMARY COMPONENT':<{primary_component_width}} | "
        f"{'UPDATED AT':<{updated_at_width}}"
    )
    print(header)

    # Add a horizontal line after the header
    # 12 is the total length of separators and spaces
    width = sum([id_width, version_width,
                 primary_component_width,
                 updated_at_width]) + 12
    line = "-" * width
    print(line)

    # Format each row with dynamic column widths and a bar between elements
    for sbom in env_node['versions']:
        if sbom.get('primaryComponent') is None:
            continue
        version = sbom.get('primaryComponent', {}).get('version', '')
        primary_component = sbom.get('primaryComponent', {}).get('name', '')
        row = (
            f"{sbom['id']:<{id_width}} | "
            f"{version:<{version_width}} | "
            f"{primary_component:<{primary_component_width}} | "
            f"{user_time(sbom['updatedAt']):<{updated_at_width}}"
        )
        print(row)

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

    vers_parser.add_argument("--env", help="Environment", required=False)
    vers_parser.add_argument("--token",
                             required=False,
                             help="Security token")

    upload_parser = subparsers.add_parser("upload", help="Upload SBOM")
    upload_group = upload_parser.add_mutually_exclusive_group(required=True)
    upload_group.add_argument("--prod", help="Product name")
    upload_group.add_argument("--prodId", help="Product ID")

    upload_parser.add_argument("--env", help="Environment", required=False)
    upload_parser.add_argument("--sbom", required=True, help="SBOM path")
    upload_parser.add_argument("--token",
                               required=False,
                               help="Security token")

    download_parser = subparsers.add_parser("download", help="Download SBOM")
    download_group = download_parser.add_mutually_exclusive_group(required=True)
    download_group.add_argument("--prod", help="Product name")
    download_group.add_argument("--prodId", help="Product ID")

    download_group = download_parser.add_mutually_exclusive_group(required=True)
    download_group.add_argument("--ver", help="Version")
    download_group.add_argument("--verId", help="Version ID")

    download_parser.add_argument("--env", help="Environment", required=False)
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


def arg_token(args):
    """
    Get the security token from the CLI or environment variables.

    Args:
      args (argparse.Namespace): The parsed command line arguments.

    Returns:
      str: The security token.
    """
    if hasattr(args, 'token') and args.token is not None:
        return args.token

    return os.environ.get("INTERLYNK_SECURITY_TOKEN")


def arg_prod_id(args):
    """
    Get the product ID from the CLI or environment variables.

    Args:
      args (argparse.Namespace): The parsed command line arguments.

    Returns:
      str: The product ID.
    """
    if hasattr(args, 'prodId') and args.prodId is not None:
        return args.prodId

    if hasattr(args, 'prod') and args.prod is not None:
        token = arg_token(args)
        node = product_by_name(products(token), args.prod)
        if node is not None:
            return node.get('prodId')

    return None

def arg_env_id(args):
    """
    Get the version ID from the CLI or environment variables.

    Args:
      args (argparse.Namespace): The parsed command line arguments.

    Returns:
      str: The version ID.
    """
    if hasattr(args, 'envId') and args.envId is not None:
        return args.envId

    env = 'default'
    if hasattr(args, 'env') and args.env is not None:
        env = args.env

    token = arg_token(args)
    prod_id = arg_prod_id(args)
    prod_node = product_env_by_name(products(token), prod_id, env)
    if prod_node is not None:
        return prod_node.get('envId')

    return None

def arg_ver_id(args):
    """
    Get the version ID from the CLI or environment variables.

    Args:
      args (argparse.Namespace): The parsed command line arguments.

    Returns:
      str: The version ID.
    """
    if hasattr(args, 'verId') and args.verId is not None:
        return args.verId

    if hasattr(args, 'ver') and args.ver is not None:
        token = arg_token(args)
        prod_id = arg_prod_id(args)
        prod_node = product_version_by_name(products(token), prod_id, args.ver)
        if prod_node is not None:
            return prod_node.get('id')

    return None


def arg_env(args):
    if getattr(args, 'env', None) is not None:
        return args.env

    if hasattr(args, 'env') and args.env is not None:
        token = arg_token(args)
        prod_id = arg_prod_id(args)
        print('KKKKKK', products(token))
        prod_node = product_env_by_name(products(token), prod_id, args.ver)
        if prod_node is not None:
            return prod_node.get('id')

    return None

def main() -> int:
    """
    Run Interlynk Commands

    Returns:
      Error code
    """
    args = setup_args()
    log_level(args)
    error_code = 1

    token = arg_token(args)
    if token is None:
      print("Missing security token")
      return error_code

    if args.subcommand == "prods":
        error_code = print_products(token)
    elif args.subcommand == "vers":            
        prod_id = arg_prod_id(args)
        ver_id = arg_ver_id(args)
        env_id = arg_env_id(args)
        logging.debug('Token (Partial): %s ProductId: %s, VersionId: %s',
                      token[-5:], prod_id, ver_id)
        error_code = print_versions(token, prod_id, env_id)
    elif args.subcommand == "upload":
        error_code = upload_sbom(token, prod_id, args.sbom)
    elif args.subcommand == "download":
        error_code = download_sbom(token, prod_id, ver_id)
    elif args.subcommand == "sign":
        error_code = print_signature(token, prod_id, ver_id, args.key)
    elif args.subcommand == "verify":
        error_code = verify_signature(token, prod_id, ver_id,
                                      args.key, args.signature)
    else:
        print("Missing or invalid command. \
              Supported commands: {prods, upload, download, sign, verify}")
        error_code = 1

    return error_code


if __name__ == "__main__":
    sys.exit(main())
