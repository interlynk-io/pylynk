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

"""Configuration management for PyLynk CLI."""

import os
import logging
from pylynk.constants import DEFAULT_API_URL, ENV_API_URL, ENV_SECURITY_TOKEN


class Config:
    """Configuration container for PyLynk CLI."""

    def __init__(self, args):
        """
        Initialize configuration from command line arguments and environment.

        Args:
            args: Parsed command line arguments
        """
        # API configuration
        self.api_url = os.environ.get(ENV_API_URL, DEFAULT_API_URL)
        self.token = getattr(args, 'token', None) or os.environ.get(
            ENV_SECURITY_TOKEN)

        # Product/Version identifiers
        self.prod = getattr(args, 'prod', None)
        self.env_id = getattr(args, 'envId', None)
        self.env = getattr(args, 'env', None)
        self.ver_id = getattr(args, 'verId', None)
        self.ver = getattr(args, 'ver', None)

        # Output options
        self.output_file = getattr(args, 'output', None)
        self.vuln = getattr(args, 'vuln', None)
        self.format_json = not getattr(args, 'table', False)

        # Download options
        self.spec = getattr(args, 'spec', None)
        self.spec_version = getattr(args, 'spec_version', None)
        self.lite = getattr(args, 'lite', False)
        self.dont_package_sbom = getattr(args, 'dont_package_sbom', False)
        self.original = getattr(args, 'original', False)
        self.exclude_parts = getattr(args, 'exclude_parts', False)
        self.include_support_status = getattr(
            args, 'include_support_status', False)

        # Upload options
        self.retries = getattr(args, 'retries', 3)

        # Logging
        self.setup_logging(args)

    def setup_logging(self, args):
        """Set up logging based on verbosity level."""
        if getattr(args, 'verbose', 0) == 0:
            logging.basicConfig(
                level=logging.ERROR,
                format='%(levelname)s: %(message)s'
            )
        else:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            # Suppress urllib3 connection pool debug messages
            logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

    def validate_token(self):
        """Validate that security token is present."""
        if not self.token:
            print("Security token not found")
            print(
                "Please set INTERLYNK_SECURITY_TOKEN environment variable or use --token parameter")
            return False
        logging.debug("Token found: %s...%s", self.token[:10] if len(self.token) > 10 else self.token,
                      self.token[-4:] if len(self.token) > 4 else "")
        return True
