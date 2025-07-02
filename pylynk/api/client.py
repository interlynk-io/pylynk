# Copyright 2025 Interlynk.io
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

"""API client for interacting with Interlynk platform."""

import json
import logging
import base64
import time
import requests

from pylynk.constants import (
    API_TIMEOUT, DEFAULT_ENVIRONMENT,
    STATUS_NOT_STARTED, STATUS_IN_PROGRESS, STATUS_FINISHED,
    STATUS_COMPLETED, STATUS_UNKNOWN, STATUS_KEYS
)
from pylynk.utils.validators import validate_file_exists, validate_boolean_flag, parse_boolean_flag
from pylynk.api.queries import PRODUCTS_TOTAL_COUNT, PRODUCTS_LIST, SBOM_DOWNLOAD, SBOM_DOWNLOAD_NEW
from pylynk.api.mutations import SBOM_UPLOAD


class LynkAPIClient:
    """Client for interacting with Interlynk API."""

    def __init__(self, config):
        """
        Initialize API client with configuration.

        Args:
            config: Configuration object with API settings
        """
        self.config = config
        self._data = None
        self._products_count = None
        self._api_call_stats = {
            'total_calls': 0,
            'total_time': 0.0,
            'total_bytes': 0,
            'calls': []
        }

    def initialize(self):
        """
        Initialize the API client by fetching initial data.

        Returns:
            bool: True if initialization successful, False otherwise
        """
        if not self.config.validate_token():
            return False

        # Fetch products count
        self._products_count = self._fetch_product_count()
        if not self._products_count or self._products_count.get('errors'):
            print("Error getting products count")
            print(
                "Possible problems: invalid security token, stale pylynk or invalid INTERLYNK_API_URL")
            return False

        # Fetch full context data
        self._data = self._fetch_context()
        if not self._data or self._data.get('errors'):
            print("Error getting Interlynk data")
            print(
                "Possible problems: invalid security token, stale pylynk or invalid INTERLYNK_API_URL")
            return False

        # Validate vuln flag if provided
        if not validate_boolean_flag(self.config.vuln, 'vuln'):
            return False

        return True

    def initialize_minimal(self):
        """
        Minimal initialization - only validate token.
        Used for operations that don't need full product data.

        Returns:
            bool: True if token is valid, False otherwise
        """
        if not self.config.validate_token():
            return False

        # Validate vuln flag if provided
        if not validate_boolean_flag(self.config.vuln, 'vuln'):
            return False

        return True

    def _make_request(self, query, variables=None, operation_name=None):
        """
        Make a GraphQL request to the API.

        Args:
            query (str): GraphQL query string
            variables (dict): Query variables
            operation_name (str): Operation name

        Returns:
            dict: Response data or None if error
        """
        headers = {"Authorization": f"Bearer {self.config.token}"}

        request_data = {"query": query}
        if variables:
            request_data["variables"] = variables
        if operation_name:
            request_data["operationName"] = operation_name

        # Log query details in verbose mode
        variables_str = f", variables={json.dumps(variables)}" if variables else ""
        logging.debug("API Request: operation=%s, url=%s%s",
                      operation_name or "unnamed", self.config.api_url, variables_str)

        start_time = time.time()

        try:
            response = requests.post(
                self.config.api_url,
                headers=headers,
                json=request_data,
                timeout=API_TIMEOUT
            )

            elapsed_time = time.time() - start_time
            response_size = len(response.content)

            # Log response details in one line
            logging.debug("API Response: status=%d, time=%.3fs, size=%s",
                          response.status_code, elapsed_time, self._format_size(response_size))

            # Track statistics
            self._api_call_stats['total_calls'] += 1
            self._api_call_stats['total_time'] += elapsed_time
            self._api_call_stats['total_bytes'] += response_size
            self._api_call_stats['calls'].append({
                'operation': operation_name or 'unnamed',
                'time': elapsed_time,
                'size': response_size,
                'status': response.status_code
            })

            if response.status_code == 200:
                response_data = response.json()
                if "errors" in response_data:
                    logging.error("GraphQL response contains errors:")
                    for error in response_data["errors"]:
                        logging.error(error["message"])
                return response_data

            logging.error("Request failed with status code: %s",
                          response.status_code)

        except requests.exceptions.RequestException as ex:
            elapsed_time = time.time() - start_time
            logging.error(
                "RequestException after %.3f seconds: %s", elapsed_time, ex)
        except json.JSONDecodeError as ex:
            logging.error("JSONDecodeError: %s", ex)

        return None

    def _format_size(self, size_bytes):
        """Format bytes to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def _fetch_product_count(self):
        """Fetch the total count of products."""
        return self._make_request(
            PRODUCTS_TOTAL_COUNT,
            operation_name="GetProductsCount"
        )

    def _fetch_context(self):
        """Fetch full context data including all products."""
        product_count = self._products_count.get('data', {}).get(
            'organization', {}).get('productNodes', {}).get('prodCount', 0)

        return self._make_request(
            PRODUCTS_LIST,
            variables={"first": product_count},
            operation_name="GetProducts"
        )

    def get_products(self):
        """
        Get list of all products.

        Returns:
            list: List of product dictionaries
        """
        if not self._data:
            return []

        prod_nodes = self._data['data']['organization']['productNodes']['products']
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

    def get_versions(self, prod_id, env_id):
        """
        Get versions for a specific product and environment.

        Args:
            prod_id (str): Product ID
            env_id (str): Environment ID

        Returns:
            list: List of version dictionaries
        """
        prod_nodes = self._data['data']['organization']['productNodes']['products']

        for prod in prod_nodes:
            if prod['id'] == prod_id:
                for env in prod['environments']:
                    if env['id'] == env_id:
                        return env['versions']

        return None

    def get_status(self, vuln_status):
        """
        Convert vulnerability status to full status dictionary.

        Args:
            vuln_status (str): Vulnerability scan status

        Returns:
            dict: Status dictionary with all status keys
        """
        result = {key: STATUS_UNKNOWN for key in STATUS_KEYS.values()}

        if vuln_status == STATUS_NOT_STARTED:
            for key in STATUS_KEYS.values():
                result[key] = STATUS_NOT_STARTED
        elif vuln_status == STATUS_IN_PROGRESS:
            result[STATUS_KEYS['VULN_SCAN']] = STATUS_IN_PROGRESS
            for key in [STATUS_KEYS['CHECKS'], STATUS_KEYS['POLICY'],
                        STATUS_KEYS['LABELING'], STATUS_KEYS['AUTOMATION']]:
                result[key] = STATUS_COMPLETED
        elif vuln_status == STATUS_FINISHED:
            for key in STATUS_KEYS.values():
                result[key] = STATUS_COMPLETED

        return result

    def download_sbom(self, env_id=None, ver_id=None, env_name=None,
                      prod_name=None, ver_name=None, include_vulns=False,
                      spec=None, spec_version=None, lite=False,
                      dont_package_sbom=False, original=False,
                      exclude_parts=False, include_support_status=False,
                      support_level_only=False):
        """
        Download an SBOM from the API.

        Args:
            env_id (str): Environment ID (projectId) (optional)
            ver_id (str): Version ID (sbomId) (optional)
            env_name (str): Environment name (projectName) (optional)
            prod_name (str): Product name (projectGroupName) (optional)
            ver_name (str): Version name (versionName) (optional)
            include_vulns (bool): Include vulnerabilities in download
            spec (str): SBOM specification (SPDX or CycloneDX)
            spec_version (str): SBOM specification version
            lite (bool): Download lite SBOM
            dont_package_sbom (bool): Don't package SBOM
            original (bool): Download original SBOM
            exclude_parts (bool): Exclude parts from SBOM
            include_support_status (bool): Include support status
            support_level_only (bool): Download support level only (CSV format)

        Returns:
            tuple: (content, content_type, filename) or (None, None, None) if error
        """
        # Build variables for new server format
        variables = {}

        # Add identifier parameters
        if ver_id:
            variables["sbomId"] = ver_id
        if env_id:
            variables["projectId"] = env_id
        if prod_name:
            variables["projectGroupName"] = prod_name
        if env_name:
            variables["projectName"] = env_name
        if ver_name:
            variables["versionName"] = ver_name

        # Add optional parameters
        if include_vulns:
            variables["includeVulns"] = include_vulns
        if spec:
            variables["spec"] = spec
        if original:
            variables["original"] = original
        # Note: query uses dontPackageSbom: $package, so package should match dont_package_sbom
        if dont_package_sbom:
            variables["package"] = dont_package_sbom
        if lite:
            variables["lite"] = lite
        if exclude_parts:
            variables["excludeParts"] = exclude_parts
        if support_level_only:
            variables["supportLevelOnly"] = support_level_only
        if include_support_status:
            variables["includeSupportStatus"] = include_support_status

        logging.debug("Downloading SBOM with parameters: %s", variables)
        logging.debug("GraphQL Query for download:\n%s", SBOM_DOWNLOAD_NEW)
        logging.debug("Query variables: %s", json.dumps(variables, indent=2))

        response_data = self._make_request(
            SBOM_DOWNLOAD_NEW, variables, operation_name="downloadSbom")

        if not response_data:
            return None, None, None

        if "errors" in response_data:
            return None, None, None

        sbom = response_data.get('data', {}).get(
            'sbom', {}).get('download', {})

        if not sbom:
            print('No SBOM matched with the given criteria')
            return None, None, None

        # Common processing for both formats
        b64data = sbom.get('content')
        content_type = sbom.get('contentType', 'application/json')
        filename = sbom.get('filename', 'sbom.json')

        decoded_content = base64.b64decode(b64data)

        # Log download details
        decoded_size = len(decoded_content)
        compression_ratio = (1 - decoded_size / len(b64data)
                             ) * 100 if b64data else 0
        logging.debug('Download completed: base64_size=%s, decoded_size=%s, compression=%.2f%%, content_type=%s',
                      self._format_size(
                          len(b64data)), self._format_size(decoded_size),
                      compression_ratio, content_type)

        return decoded_content.decode('utf-8'), content_type, filename

    def upload_sbom(self, sbom_file):
        """
        Upload an SBOM to the API using available identifiers with retry logic.

        Args:
            sbom_file (str): Path to SBOM file

        Returns:
            int: 0 if successful, 1 if error
        """
        if not validate_file_exists(sbom_file):
            return 1

        # Get file size for logging
        import os
        file_size = os.path.getsize(sbom_file)

        # Build variables based on what's available
        variables = {"doc": None}

        # Add project group (product) identifiers
        if hasattr(self.config, 'prod_id') and self.config.prod_id:
            variables["projectGroupId"] = self.config.prod_id
        elif self.config.prod:
            variables["projectGroupName"] = self.config.prod

        # Add project (environment) identifiers
        if self.config.env_id:
            variables["projectId"] = self.config.env_id
        elif self.config.env:
            variables["projectName"] = self.config.env

        logging.debug("Upload Request: operation=uploadSbom, url=%s, variables=%s, file=%s, size=%s",
                      self.config.api_url,
                      {k: v for k, v in variables.items() if k != "doc"},
                      sbom_file,
                      self._format_size(file_size))

        headers = {"Authorization": f"Bearer {self.config.token}"}

        operations = json.dumps({
            "query": SBOM_UPLOAD,
            "variables": variables
        })
        map_data = json.dumps({"0": ["variables.doc"]})

        form_data = {
            "operations": operations,
            "map": map_data
        }

        # Get number of retries from config (default to 3)
        max_retries = getattr(self.config, 'retries', 3)

        for attempt in range(max_retries + 1):
            start_time = time.time()

            try:
                with open(sbom_file, 'rb') as sbom:
                    files_map = {'0': sbom}
                    response = requests.post(
                        self.config.api_url,
                        headers=headers,
                        data=form_data,
                        files=files_map,
                        timeout=API_TIMEOUT
                    )

                    elapsed_time = time.time() - start_time
                    response_size = len(response.content)

                    # Log response details
                    upload_speed = file_size / elapsed_time if elapsed_time > 0 else 0
                    logging.debug("Upload Response: status=%d, time=%.3fs, size=%s, speed=%s/s, attempt=%d/%d",
                                  response.status_code, elapsed_time, self._format_size(
                                      response_size),
                                  self._format_size(upload_speed), attempt + 1, max_retries + 1)

                    if response.status_code == 200:
                        resp_json = response.json()
                        errors = resp_json.get('data', {}).get(
                            'sbomUpload', {}).get('errors')
                        if errors:
                            print(f"Error uploading sbom: {errors}")
                            return 1
                        print('Uploaded successfully')
                        return 0

                    # Don't retry on authentication errors
                    if response.status_code == 401:
                        print(
                            "Authentication failed. Please check your INTERLYNK_SECURITY_TOKEN")
                        logging.debug("Token used: %s...%s", self.config.token[:10] if self.config.token else "None",
                                      self.config.token[-4:] if self.config.token else "")
                        return 1

                    # For other errors, log and maybe retry
                    logging.error("Error uploading sbom: %d",
                                  response.status_code)
                    try:
                        error_data = response.json()
                        if 'errors' in error_data:
                            for error in error_data['errors']:
                                print(f"Error: {error.get('message', error)}")
                    except:
                        # If response is not JSON, try to print text
                        if response.text:
                            print(f"Response: {response.text}")

                    # Don't retry on client errors (4xx) except rate limiting
                    if 400 <= response.status_code < 500 and response.status_code != 429:
                        return 1

            except requests.exceptions.RequestException as ex:
                elapsed_time = time.time() - start_time
                logging.error("RequestException after %.3f seconds: %s (attempt %d/%d)",
                              elapsed_time, ex, attempt + 1, max_retries + 1)
            except FileNotFoundError as ex:
                logging.error("FileNotFoundError: %s", ex)
                return 1  # Don't retry file not found errors

            # If this wasn't the last attempt, sleep before retrying
            if attempt < max_retries:
                # Exponential backoff: 1s, 2s, 4s
                backoff_time = (2 ** attempt) * 1
                logging.info("Retrying upload in %d seconds...", backoff_time)
                time.sleep(backoff_time)

        print(f"Upload failed after {max_retries + 1} attempts")
        return 1

    def resolve_identifiers(self):
        """
        Resolve product, environment, and version identifiers.

        Returns:
            bool: True if all required identifiers resolved, False otherwise
        """
        # Resolve product
        if self.config.prod or getattr(self.config, 'prod_id', None):
            if not self._resolve_product():
                print('Product not found')
                return False

        # Resolve environment (if product is set)
        if self.config.prod:
            if not self._resolve_environment():
                print('Environment not found')
                return False

        # Resolve version (if needed)
        if self.config.ver or self.config.ver_id:
            if not self._resolve_version():
                print('Version not found')
                return False

        return True

    def _resolve_product(self):
        """Resolve product name and ID."""
        if not self._data:
            # No data available, can't resolve
            return self.config.prod and getattr(self.config, 'prod_id', None)

        nodes = self._data.get('data', {}).get('organization', {}).get(
            'productNodes', {}).get('products', [])

        # Check if prod_id exists and resolve if needed
        prod_id = getattr(self.config, 'prod_id', None)
        if not prod_id and self.config.prod:
            self.config.prod_id = next(
                (node['id'] for node in nodes if node['name'] == self.config.prod), None)

        # Check if prod exists and resolve if needed
        if not self.config.prod and prod_id:
            self.config.prod = next(
                (node['name'] for node in nodes if node['id'] == prod_id), None)

        return self.config.prod and getattr(self.config, 'prod_id', None)

    def _resolve_environment(self):
        """Resolve environment name and ID."""
        if not self._data:
            # No data available, can't resolve
            return self.config.env and self.config.env_id

        env = self.config.env or DEFAULT_ENVIRONMENT

        # For pre-configured environments, use case-insensitive comparison
        if env.lower() in ['default', 'development', 'production']:
            env = env.lower()

        for product in self._data.get('data', {}).get('organization', {}).get(
                'productNodes', {}).get('products', []):
            if product['id'] == getattr(self.config, 'prod_id', None):
                if not self.config.env_id:
                    self.config.env_id = next(
                        (env_node['id'] for env_node in product.get('environments', [])
                         if env_node.get('name') == env), None)

                if not self.config.env:
                    self.config.env = next(
                        (env_node['name'] for env_node in product.get('environments', [])
                         if env_node.get('id') == self.config.env_id), None)
                break

        return self.config.env and self.config.env_id

    def _resolve_version(self):
        """Resolve version name and ID."""
        if not self._data:
            # No data available, can't resolve
            return self.config.ver_id is not None

        for product in self._data.get('data', {}).get('organization', {}).get(
                'productNodes', {}).get('products', []):
            if product['id'] == getattr(self.config, 'prod_id', None):
                for env in product['environments']:
                    if env['id'] == self.config.env_id:
                        for ver in env['versions']:
                            pc = ver.get('primaryComponent', {})

                            if not self.config.ver_id and pc.get('version') == self.config.ver:
                                self.config.ver_id = ver['id']
                                self.config.ver_status = ver.get(
                                    'vulnRunStatus', '')

                            if not self.config.ver and ver['id'] == self.config.ver_id:
                                self.config.ver = pc.get('version', '')
                                self.config.ver_status = ver.get(
                                    'vulnRunStatus', '')
                        break
                break

        return self.config.ver_id is not None

    def print_api_summary(self):
        """Print summary of API calls made during the session."""
        if self._api_call_stats['total_calls'] == 0:
            return

        avg_time = self._api_call_stats['total_time'] / \
            self._api_call_stats['total_calls']
        avg_size = self._api_call_stats['total_bytes'] / \
            self._api_call_stats['total_calls']

        logging.debug("API Summary: calls=%d, total_time=%.3fs, total_data=%s, avg_time=%.3fs, avg_size=%s",
                      self._api_call_stats['total_calls'],
                      self._api_call_stats['total_time'],
                      self._format_size(self._api_call_stats['total_bytes']),
                      avg_time,
                      self._format_size(avg_size))

        # Log individual calls
        for i, call in enumerate(self._api_call_stats['calls'], 1):
            logging.debug("  Call %d: operation=%s, time=%.3fs, size=%s, status=%d",
                          i, call['operation'], call['time'],
                          self._format_size(call['size']), call['status'])
