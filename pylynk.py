"""
This module contains functions for interacting with the Interlynk API.
"""

import os
import sys
import json
import argparse
import logging
import requests


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

QUERY_PROJECT_PARAMS = {
    'operationName': 'GetProjects',
    'variables': {},
    'query': QUERY_PROJECTS_LIST
    }


def products(token):
    """
    Fetches the Interlynk list of products using the provided token.

    Args:
      token (str): The authentication token to use for the API request.

    Returns:
      map
    """
    products_map = {}
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
            logging.debug("Products response: %s", response_data)
            for product in response_data['data']['projects']['nodes']:
                products_map[product["name"]] = product["id"]
            logging.debug("%d products: %s", len(products_map), products_map)
            return products_map
        logging.error("Error fetching products: %s", response.status_code)
    except requests.exceptions.RequestException as ex:
        logging.error("RequestException:  %s", ex)
    except json.JSONDecodeError as ex:
        logging.error("JSONDecodeError: %s", ex)

    return products_map


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

    products_map = products(token)
    if products_map is None or product not in products_map:
        logging.error("No product found with the name %s", product)
        return 1
    product_id = products_map[product]
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
    upload_parser.add_argument("--sbom", required=True, help="SBOM path")
    upload_parser.add_argument("--prod", required=True, help="Product name")
    upload_parser.add_argument("--token",
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

    if args.subcommand == "upload":
        logging.info("Uploading SBOM %s for product %s", args.sbom, args.prod)
        return upload_sbom(args.sbom, args.prod, token)
    if args.subcommand == "prods":
        logging.info("Fetching Product list")
        return print_products(token)
    logging.error("Missing or invalid command. \
                  Supported commands: {upload,prods}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
