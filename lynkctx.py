import os
import json
import logging
import base64
import requests

INTERLYNK_API_URL = 'https://api.interlynk.io/lynkapi'

INTERLYNK_API_TIMEOUT = 100

QUERY_PRODUCTS_TOTAL_COUNT = """
query GetProductsCount($name: String, $enabled: Boolean) {
  organization {
    productNodes: projectGroups(
      search: $name
      enabled: $enabled
      orderBy: { field: PROJECT_GROUPS_UPDATED_AT, direction: DESC }
    ) {
      prodCount: totalCount
    }
  }
}
"""

QUERY_PROJECT_COUNT_PARAMS = {
    'operationName': 'GetProductsCount',
    'variables': {},
    'query': QUERY_PRODUCTS_TOTAL_COUNT
}


QUERY_PRODUCTS_LIST = """
query GetProducts($first: Int) {
  organization {
    productNodes: projectGroups(
      enabled: true
      first: $first
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
            vulnRunStatus
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

QUERY_PROJECT_PARAMS = {
    'operationName': 'GetProducts',
    'variables': {},
    'query': QUERY_PRODUCTS_LIST
}


QUERY_SBOM_UPLOAD = """
mutation uploadSbom($doc: Upload!, $projectId: ID!) {
  sbomUpload(
    input: {
      doc: $doc,
      projectId: $projectId
    }
  ) {
    id
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


class LynkContext:
    def __init__(self, api_url, token, prod_id, prod, env_id, env, ver_id, ver, output_file):
        self.api_url = api_url or INTERLYNK_API_URL
        self.token = token
        self.prod_id = prod_id
        self.prod = prod
        self.env_id = env_id
        self.env = env
        self.ver_id = ver_id
        self.ver = ver
        self.ver_status = self.vuln_status_to_status('')
        self.output_file = output_file

    def validate(self):
        if not self.token:
            print("Security token not found")
            return False

        self.products_count = self._fetch_product_count()
        if not self.products_count or self.products_count.get('errors'):
            print("Error getting products count")
            print(
                "Possible problems: invalid security token, stale pylynk or invalid INTERLYNK_API_URL")
            return False

        self.data = self._fetch_context()
        if not self.data or self.data.get('errors'):
            print("Error getting Interlynk data")
            print(
                "Possible problems: invalid security token, stale pylynk or invalid INTERLYNK_API_URL")
            return False

        if (self.prod or self.prod_id) and not self.resolve_prod():
            self.prod = self.prod_id = None
            print('Product not found')
            return False

        if self.prod and not self.resolve_env():  # There must be a default env
            self.env = self.env_id = None
            print('Environment not found')
            return False

        if (self.ver or self.ver_id) and not self.resolve_ver():
            self.ver = self.ver_id = None
            print('Version not found')
            return False

        return True

    def _fetch_product_count(self):
        headers = {"Authorization": "Bearer " + self.token}
        try:
            response = requests.post(self.api_url,
                                     headers=headers,
                                     data=QUERY_PROJECT_COUNT_PARAMS,
                                     timeout=INTERLYNK_API_TIMEOUT)
            if response.status_code == 200:
                response_data = response.json()
                logging.debug(
                    "Products count response text: %s", response_data)
                return response_data
            logging.error("Error fetching products: %s", response.status_code)
        except requests.exceptions.RequestException as ex:
            logging.error("RequestException: %s", ex)
        except json.JSONDecodeError as ex:
            logging.error("JSONDecodeError: %s", ex)
        return None

    def _fetch_context(self):
        headers = {"Authorization": "Bearer " + self.token}
        product_count = self.products_count.get(
            'data', {}).get('organization', {}).get('productNodes', {}).get('prodCount', 0)

        variables = {
            "first": product_count
        }

        request_data = {
            "query": QUERY_PRODUCTS_LIST,
            "variables": variables,
        }

        try:
            response = requests.post(self.api_url,
                                     headers=headers,
                                     json=request_data,
                                     timeout=INTERLYNK_API_TIMEOUT)
            if response.status_code == 200:
                response_data = response.json()
                logging.debug("Products response text: %s", response_data)
                return response_data
            logging.error("Error fetching products: %s", response.status_code)
        except requests.exceptions.RequestException as ex:
            logging.error("RequestException: %s", ex)
        except json.JSONDecodeError as ex:
            logging.error("JSONDecodeError: %s", ex)
        return None

    def resolve_prod(self):
        if not self.prod_id:
            nodes = self.data.get('data', {}).get('organization', {}).get(
                'productNodes', {}).get('products', [])
            self.prod_id = next(
                (node['id'] for node in nodes if node['name'] == self.prod), None)
        if not self.prod:
            nodes = self.data.get('data', {}).get('organization', {}).get(
                'productNodes', {}).get('products', [])
            self.prod = next(
                (node['name'] for node in nodes if node['id'] == self.prod_id), None)
        return self.prod and self.prod_id

    def resolve_env(self):
        env = self.env or 'default'
        # For pre-configured environments, use case-insensitive comparison
        if env.lower() in ['default', 'development', 'production']:
            env = env.lower()

        if not self.env_id:
            for product in self.data.get('data', {}).get('organization', {}).get('productNodes', {}).get('products', []):
                if product['id'] == self.prod_id:
                    self.env_id = next((env_node['id'] for env_node in product.get('environments', [])
                                        if env_node.get('name') == env), None)
        if not self.env:
            for product in self.data.get('data', {}).get('organization', {}).get('productNodes', {}).get('products', []):
                if product['id'] == self.prod_id:
                    self.env = next((env_node['id'] for env_node in product.get('environments', [])
                                     if env_node.get('id') == self.env_id), None)
        return self.env and self.env_id

    def resolve_ver(self):
        env = self.env or 'default'

        if not self.ver_id:
            for product in self.data.get('data', {}).get('organization', {}).get('productNodes', {}).get('products', []):
                if product['id'] == self.prod_id:
                    for env in product['environments']:
                        if env['id'] == self.env_id:
                            for ver in env['versions']:
                                if ver['primaryComponent']['version'] == self.ver:
                                    self.ver_id = ver['id']
                                    self.ver_status = self.vuln_status_to_status(
                                        ver['vulnRunStatus'])

        empty_ver = False
        if not self.ver:
            for product in self.data.get('data', {}).get('organization', {}).get('productNodes', {}).get('products', []):
                if product['id'] == self.prod_id:
                    for env in product['environments']:
                        if env['id'] == self.env_id:
                            for ver in env['versions']:
                                if ver['id'] == self.ver_id:
                                    if ver.get('primaryComponent'):
                                        self.ver = ver['primaryComponent']['version']
                                    if not self.ver:
                                        empty_ver = True
                                    self.ver_status = self.vuln_status_to_status(
                                        ver['vulnRunStatus'])
                                    
       
        # if ver is not empty
        if not empty_ver:
            for product in self.data.get('data', {}).get('organization', {}).get('productNodes', {}).get('products', []):
                if product['id'] == self.prod_id:
                    for env in product['environments']:
                        if env['id'] == self.env_id:
                            for ver in env['versions']:
                                if ver['id'] == self.ver_id:
                                    if ver.get('primaryComponent'):
                                        self.ver = ver['primaryComponent']['version']
                                    self.ver_status = self.vuln_status_to_status(ver['vulnRunStatus'])

        return (empty_ver or self.ver) and self.ver_id

    def __repr__(self):
        from pprint import pformat
        return pformat(vars(self), indent=1, width=1)

    def prods(self):
        if (self.data.get('errors')):
            logging.error("Query error: GetProducts")
            return None

        if not self.data:
            logging.error("No products found")
            return None

        prod_nodes = self.data['data']['organization']['productNodes']['products']
        prod_list = []
        for prod in prod_nodes:
            versions = sum(len(env['versions'])
                           for env in prod['environments'])
            prod_list.append({
                'name': prod['name'],
                'updatedAt': prod['updatedAt'],
                'id': prod['id'],
                'versions': versions
            })
        return prod_list

    def versions(self):
        prod_nodes = self.data['data']['organization']['productNodes']['products']
        versions_node = next((env['versions'] for prod in prod_nodes if self.prod_id == prod['id']
                              for env in prod['environments'] if self.env_id == env['id']), None)
        return versions_node

    def status(self):
        self.data = self._fetch_context()
        self.resolve_ver()
        return self.ver_status

    def download(self):
        logging.debug("Downloading SBOM for environment ID %s, sbom ID %s",
                      self.env_id, self.ver_id)

        variables = {
            "envId": self.env_id,
            "sbomId": self.ver_id,
            "includeVulns": False
        }

        request_data = {
            "query": QUERY_SBOM_DOWNLOAD,
            "variables": variables,
        }

        response = requests.post(self.api_url,
                                 headers={
                                     "Authorization": "Bearer " + self.token},
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

    def upload(self, sbom_file):
        if os.path.isfile(sbom_file) is False:
            print(f"SBOM File not found: {sbom_file}")
            return

        if not self.prod_id:
            print(f"Product not found: {self.prod}")
            return

        if not self.env_id:
            print(f"Environment not found: {self.env}")
            return

        logging.debug("Uploading SBOM to product ID %s", self.prod_id)

        headers = {
            "Authorization": "Bearer " + self.token
        }

        operations = json.dumps({
            "query": QUERY_SBOM_UPLOAD,
            "variables": {"doc": None, "projectId": self.env_id}
        })
        map_data = json.dumps({"0": ["variables.doc"]})

        form_data = {
            "operations": operations,
            "map": map_data
        }

        try:
            with open(sbom_file, 'rb') as sbom:
                files_map = {'0': sbom}
                response = requests.post(self.api_url,
                                         headers=headers,
                                         data=form_data,
                                         files=files_map,
                                         timeout=INTERLYNK_API_TIMEOUT)
                if response.status_code == 200:
                    resp_json = response.json()
                    version_id = resp_json.get('data', {}).get('sbomUpload', {}).get('id')
                    errors = resp_json.get('data', {}).get(
                        'sbomUpload', {}).get('errors')
                    if errors:
                        print(f"Error uploading sbom: {errors}")
                        return 1
                    if version_id:
                        self.ver_id = version_id
                        print("SBOM ID successfully returned in the response: ", self.ver_id)
                        logging.debug("SBOM upload response: %s", response.text)
                    else:
                        print("Error: SBOM ID not returned in the response.")
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

    def vuln_status_to_status(self, status):
        result_dict = dict()
        result_dict['checksStatus'] = 'UNKNOWN'
        result_dict['policyStatus'] = 'UNKNOWN'
        result_dict['labelingStatus'] = 'UNKNOWN'
        result_dict['automationStatus'] = 'UNKNOWN'
        result_dict['vulnScanStatus'] = 'UNKNOWN'
        if status == 'NOT_STARTED':
            result_dict['vulnScanStatus'] = 'NOT_STARTED'
            result_dict['checksStatus'] = 'NOT_STARTED'
            result_dict['policyStatus'] = 'NOT_STARTED'
            result_dict['labelingStatus'] = 'NOT_STARTED'
            result_dict['automationStatus'] = 'NOT_STARTED'
        elif status == 'IN_PROGRESS':
            result_dict['vulnScanStatus'] = 'IN_PROGRESS'
            result_dict['checksStatus'] = 'COMPLETED'
            result_dict['policyStatus'] = 'COMPLETED'
            result_dict['labelingStatus'] = 'COMPLETED'
            result_dict['automationStatus'] = 'COMPLETED'
        elif status == 'FINISHED':
            result_dict['vulnScanStatus'] = 'COMPLETED'
            result_dict['checksStatus'] = 'COMPLETED'
            result_dict['policyStatus'] = 'COMPLETED'
            result_dict['labelingStatus'] = 'COMPLETED'
            result_dict['automationStatus'] = 'COMPLETED'
        return result_dict
