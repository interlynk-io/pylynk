import requests
import json
import logging
import os
import base64

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
    def __init__(self, token, prod_id, prod, env_id, env, ver_id, ver):
        self.token = token
        self.prod_id = prod_id
        self.prod = prod
        self.env_id = env_id
        self.env = env
        self.ver_id = ver_id
        self.ver = ver
        self.data = self._fetch_context()

        if prod:
            self._set_prod_id()

        if env_id is None:
            self._set_env_id()

        if ver_id is None:
            self._set_ver_id()

    def _fetch_context(self):
        headers = {"Authorization": "Bearer " + self.token}
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
            logging.error("RequestException: %s", ex)
        except json.JSONDecodeError as ex:
            logging.error("JSONDecodeError: %s", ex)
        return None

    def _set_prod_id(self):
        nodes = self.data.get('data', {}).get('organization', {}).get('productNodes', {}).get('products', [])
        self.prod_id = next((node['id'] for node in nodes if node['name'] == self.prod), None)

    def _set_env_id(self):
        env = self.env or 'default'
        for product in self.data.get('data', {}).get('organization', {}).get('productNodes', {}).get('products', []):
            if product['id'] == self.prod_id:
                self.env_id = next((env_node['id'] for env_node in product.get('environments', [])
                                    if env_node.get('name') == env), None)

    def _set_ver_id(self):
        env = self.env or 'default'
        for product in self.data.get('data', {}).get('organization', {}).get('productNodes', {}).get('products', []):
            if product['id'] == self.prod_id:
                for env in product['environments']:
                    if env['id'] == self.env_id:
                            for ver in env['versions']:
                                if ver['primaryComponent']['version'] == self.ver:
                                    self.ver_id = ver['id']

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
            versions = sum(len(env['versions']) for env in prod['environments'])
            prod_list.append({
                'name': prod['name'],
                'updatedAt': prod['updatedAt'],
                'id': prod['id'],
                'versions': versions
            })
        return prod_list
    
    def versions(self):
        if (self.data.get('errors')):
            logging.error("Query error: GetProducts")
            return None
        
        if not self.data:
            logging.error("No products found")
            return None
        
        prod_nodes = self.data['data']['organization']['productNodes']['products']                    
        versions_node = next((env['versions'] for prod in prod_nodes if self.prod_id == prod['id'] 
                              for env in prod['environments'] if self.env_id == env['id']), None)
        return versions_node

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

        response = requests.post(INTERLYNK_API_URL,
                                headers={"Authorization": "Bearer " + self.token},
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
                response = requests.post(INTERLYNK_API_URL,
                                        headers=headers,
                                        data=form_data,
                                        files=files_map,
                                        timeout=INTERLYNK_API_TIMEOUT)
                if response.status_code == 200:
                    resp_json = response.json()
                    errors = resp_json.get('errors')
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
