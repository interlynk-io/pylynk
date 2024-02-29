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
query GetProducts($name: String, $enabled: Boolean) {
  organization {
    productNodes: projectGroups(
      search: $name
      enabled: $enabled
      orderBy: { field: PROJECT_GROUPS_UPDATED_AT, direction: DESC }
    ) {
      prodCount: totalCount
      products: nodes {
        id
        name
        updatedAt
        enabled
        environments: projects {
          id: id
          name: name
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
query downloadSbom($envId: Uuid!, $sbomId: Uuid!, $includeVulns: Boolean) {
  sbom(projectId: $envId, sbomId: $sbomId) {
    download(
      sbomId: $sbomId
      includeVulns: $includeVulns
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
    timestamp = datetime.datetime.fromisoformat(utc_time[:-1])
    local_timezone = tzlocal.get_localzone()
    local_time = timestamp.replace(tzinfo=pytz.UTC).astimezone(local_timezone)
    return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')


def product_by_name(data_json, prod_name):
    nodes = data_json['data']['organization']['productNodes']['products']
    return next((node for node in nodes
                 if node['name'] == prod_name), None)


def product_by_id(data_json, prod_id):
    nodes = data_json['data']['organization']['productNodes']['products']
    return next((node for node in nodes if node['id'] == prod_id), None)


def product_version_by_name(data_json, prod_id, env_id, version):
    prod = product_by_id(data_json, prod_id)
    if prod is None:
        return None
    
    for env in prod['environments']:
        if env['id'] == env_id:
            for ver in env['versions']:
                if ver['primaryComponent']['version'] == version:
                    return ver


def product_version_by_id(data_json, product_id, version_id):
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
    ) if env_node.get('name') == env),
       None)


def products(token):
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
            logging.debug("Products response text: %s", response_data)
            return response_data
        logging.error("Error fetching products: %s", response.status_code)
    except requests.exceptions.RequestException as ex:
        logging.error("RequestException:  %s", ex)
    except json.JSONDecodeError as ex:
        logging.error("JSONDecodeError: %s", ex)

    return None


def upload_sbom(token, product_id, env_id, sbom_file):
    if os.path.isfile(sbom_file) is False:
        logging.error('SBOM File not found: %s', sbom_file)
        return 1

    logging.debug("Uploading SBOM to product ID %s", product_id)

    headers = {
      "Authorization": "Bearer " + token
    }

    operations = json.dumps({
      "query": QUERY_SBOM_UPLOAD,
      "variables": {"doc": None, "projectId": env_id}
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


def download(token, env_id, version_id):
    logging.debug("Downloading SBOM for environment ID %s, sbom ID %s",
                  env_id, version_id)

    variables = {
        "envId": env_id,
        "sbomId": version_id,
        "includeVulns": False
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
                logging.debug(data)
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


def download_sbom(token, env_id, version_id):
    sbom = download(token, env_id, version_id)
    if sbom is None:
        logging.error("Error fetching SBOM")
        return 1

    print(sbom)
    return 0


def print_products(token):
    products_json = products(token)
    if (products_json.get('errors')):
        logging.error("Query error: GetProducts")
        return 1
    
    if not products_json:
        logging.error("No products found")
        return 1
    prod_nodes = products_json['data']['organization']['productNodes']['products']

    # Calculate dynamic column widths
    name_width = max(len("NAME"), max(len(prod['name'])
                                       for prod in prod_nodes))
    updated_at_width = max(len("UPDATED AT"),
                           max(len(user_time(prod['updatedAt']))
                               for prod in prod_nodes))
    id_width = max(len("ID"), max(len(prod['id']) for prod in prod_nodes))
    version_width = len("VERSIONS")

    header = (
        f"{ 'NAME':<{name_width}} | "
        f"{ 'ID':<{id_width}} | "
        f"{ 'VERSIONS':<{version_width}} | "
        f"{ 'UPDATED AT':<{updated_at_width}} | "
    )
    print(header)

    # Add a horizontal line after the header
    # 10 is the total length of separators and spaces
    width = sum([name_width, version_width, updated_at_width, id_width]) + 10
    line = "-" * width
    print(line)

    for prod in prod_nodes:
        version_count = 0
        for env in prod['environments']:
          version_count += len(env['versions']) 
        row = (
            f"{prod['name']:<{name_width}} | "
            f"{prod['id']:<{id_width}} | "
            f"{version_count:<{version_width}} | "
            f"{user_time(prod['updatedAt']):<{updated_at_width}} | "
        )
        print(row)
    return 0


def print_versions(token, prod_id, env_id):
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
    ) if env_node['id'] == env_id),
       None)
    
    if not env_node:
        print("No matching environment for envID ", env_id)
        return 1
    
    if len(env_node['versions']) == 0:
        print(f"No version exists in {env_node['name']} environment")
        return 0
    
    # Calculate dynamic column widths
    id_width = max(len('ID'), max(len(sbom['id'])
                                  for sbom in env_node['versions']))
    version_width = max(len('VERSION'),
                        max(len(s.get('primaryComponent', {})
                                .get('version', ''))
                        for s in env_node['versions']))
    primary_component_width = max(len('PRIMARY COMPONENT'),
                                  max(len(sbom.get('primaryComponent', {})
                                          .get('name', ''))
                                      for sbom in env_node['versions']))
    updated_at_width = max(len('UPDATED AT'),
                           max(len(user_time(sbom['updatedAt']))
                               for sbom in env_node['versions']))

    # Format the header with dynamic column widths
    header = (
        f"{'ID':<{id_width}} | "
        f"{'VERSION':<{version_width}} | "
        f"{'PRIMARY COMPONENT':<{primary_component_width}} | "
        f"{'UPDATED AT':<{updated_at_width}} |"
    )
    print(header)

    # Add a horizontal line after the header
    # 12 is the total length of separators and spaces
    width = sum([id_width, version_width,
                 primary_component_width,
                 updated_at_width]) + 10
    line = "-" * width + "|"
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
            f"{user_time(sbom['updatedAt']):<{updated_at_width}} |"
        )
        print(row)

    return 0


def setup_args():
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

    args = parser.parse_args()
    return args


def log_level(args):
    if args.verbose == 0:
        logging.basicConfig(level=logging.ERROR)
    logging.basicConfig(level=logging.DEBUG)


def arg_token(args):
    if hasattr(args, 'token') and args.token is not None:
        return args.token

    return os.environ.get("INTERLYNK_SECURITY_TOKEN")


def arg_prod_id(args):
    if hasattr(args, 'prodId') and args.prodId is not None:
        return args.prodId

    if hasattr(args, 'prod') and args.prod is not None:
        token = arg_token(args)
        node = product_by_name(products(token), args.prod)
        if node is not None:
            return node.get('id')
    logging.debug("Failed to find product named: ", args.prod)

    return None

def arg_env_id(args):
    if hasattr(args, 'envId') and args.envId is not None:
        return args.envId

    env = 'default'
    if hasattr(args, 'env') and args.env is not None:
        env = args.env

    token = arg_token(args)
    prod_id = arg_prod_id(args)
    prod_node = product_env_by_name(products(token), prod_id, env)
    if prod_node is not None:
        return prod_node.get('id')
    logging.debug("Failed to find environment named: ", env)

    return None

def arg_ver_id(args, env_id):
    if hasattr(args, 'verId') and args.verId is not None:
        return args.verId

    if hasattr(args, 'ver') and args.ver is not None:
        token = arg_token(args)
        prod_id = arg_prod_id(args)
        prod_node = product_version_by_name(products(token), prod_id, env_id, args.ver)
        if prod_node is not None:
            return prod_node.get('id')

    return None


def arg_env(args):
    if getattr(args, 'env', None) is not None:
        return args.env

    if hasattr(args, 'env') and args.env is not None:
        token = arg_token(args)
        prod_id = arg_prod_id(args)
        prod_node = product_env_by_name(products(token), prod_id, args.ver)
        if prod_node is not None:
            return prod_node.get('id')

    return None

def main() -> int:
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
        env_id = arg_env_id(args)
        if not prod_id or not env_id:
          print("Failed to find product or environment")
          error_code = 1
        else:
          logging.debug('Token (Partial): %s ProductId: %s, EnvId: %s',
                        token[-5:], prod_id, env_id)
          error_code = print_versions(token, prod_id, env_id)
    elif args.subcommand == "upload":
        prod_id = arg_prod_id(args)
        env_id = arg_env_id(args)
        if not prod_id or not env_id:
          print("Failed to find product or environment")
          error_code = 1
        else:
          logging.debug('Token (Partial): %s ProductId: %s, EnvId: %s',
                        token[-5:], prod_id, env_id)
        error_code = upload_sbom(token, prod_id, env_id, args.sbom)
    elif args.subcommand == "download":
        env_id = arg_env_id(args)
        ver_id = arg_ver_id(args, env_id)
        if not env_id or not ver_id:
          print("Failed to find environment or version")
          error_code = 1
        else:
          logging.debug('Token (Partial): %s EnvId: %s',
                        token[-5:], env_id)
        error_code = download_sbom(token, env_id, ver_id)
    else:
        print("Missing or invalid command. \
              Supported commands: {prods, upload, download, sign, verify}")
        error_code = 1

    return error_code


if __name__ == "__main__":
    sys.exit(main())
