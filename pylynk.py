"""
This module contains functions for interacting with the Interlynk API.
"""

import os
import sys
import json
import argparse
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
    Fetches a list of products from the Interlynk API using the provided token.

    Args:
      token (str): The authentication token to use for the API request.

    Returns:
      None
    """
    headers = {
      "Authorization": "Bearer " + token
    }

    response = requests.post(INTERLYNK_API_URL,
                             headers=headers,
                             data=QUERY_PROJECT_PARAMS,
                             timeout=INTERLYNK_API_TIMEOUT)
    for proj in json.loads(response.text)['data']['projects']['nodes']:
        print(f'{proj["name"]}')


def upload(file, product, token):
    """
    Uploads an SBOM file to a project in the Interlynk API.

    Args:
      file (str): The path to the SBOM file to upload.
      product (str): The ID of the product to upload the SBOM to.
      token (str): The authentication token to use for the API request.

    Returns:
      None
    """
    if os.path.isfile(file) is False:
        print('SBOM File not found')
        return

    headers = {
      "Authorization": "Bearer " + token
    }

    operations = json.dumps({
      "query": QUERY_SBOM_UPLOAD,
      "variables": {"doc": None, "projectId": product}
    })
    map_data = json.dumps({"0": ["variables.doc"]})

    form_data = {
      "operations": operations,
      "map": map_data
    }

    with open(file, 'rb') as sbom:
        myfiles = {'0': sbom}
        response = requests.post(INTERLYNK_API_URL,
                                 headers=headers,
                                 data=form_data,
                                 files=myfiles,
                                 timeout=INTERLYNK_API_TIMEOUT)
        if os.path.isfile(file) is False:
            print('SBOM File not found')
            return

        headers = {
            "Authorization": "Bearer " + token
        }

        operations = json.dumps({
            "query": QUERY_SBOM_UPLOAD,
            "variables": {"doc": None, "projectId": product}
        })
        map_data = json.dumps({"0": ["variables.doc"]})

        form_data = {
            "operations": operations,
            "map": map_data
        }

        with open(file, 'rb') as sbom:
            myfiles = {'0': sbom}
            response = requests.post(INTERLYNK_API_URL,
                                     headers=headers,
                                     data=form_data,
                                     files=myfiles,
                                     timeout=INTERLYNK_API_TIMEOUT)
            print(response.text)


def setup_args():
    """
    Setup command line arguments
    :return: arguments object
    """
    parser = argparse.ArgumentParser(description='Interlynk command line tool')

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    upload_parser = subparsers.add_parser("upload", help="Upload an SBOM file")
    upload_parser.add_argument("--sbom", required=True, help="SBOM path")
    upload_parser.add_argument("--proj", required=True, help="Project name")
    upload_parser.add_argument("--token",
                               required=False,
                               help="Security token")

    products_parser = subparsers.add_parser("prods", help="List products")
    products_parser.add_argument("--token",
                                 required=False,
                                 help="Security token")

    args = parser.parse_args()
    return args


def main() -> int:
    """
    Run Interlynk Commands
    """
    args = setup_args()
    token = args.token or os.environ.get("INTERLYNK_SECURITY_TOKEN")
    if args.subcommand == "upload":
        upload(args.sbom, args.proj, token)
    elif args.subcommand == "prods":
        products(token)
    else:
        print("Invalid command.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
