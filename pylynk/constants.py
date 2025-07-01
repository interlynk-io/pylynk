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

"""Constants and default values for PyLynk CLI."""

# API Configuration
DEFAULT_API_URL = 'https://api.interlynk.io/lynkapi'
API_TIMEOUT = 100

# Environment Variables
ENV_API_URL = 'INTERLYNK_API_URL'
ENV_SECURITY_TOKEN = 'INTERLYNK_SECURITY_TOKEN'

# Default Values
DEFAULT_ENVIRONMENT = 'default'

# Valid boolean values for flags
VALID_BOOLEAN_VALUES = ['true', 'false', '1', '0', 'yes', 'no']

# Status Types
STATUS_UNKNOWN = 'UNKNOWN'
STATUS_NOT_STARTED = 'NOT_STARTED'
STATUS_IN_PROGRESS = 'IN_PROGRESS'
STATUS_COMPLETED = 'COMPLETED'
STATUS_FINISHED = 'FINISHED'

# Status Keys
STATUS_KEYS = {
    'CHECKS': 'checksStatus',
    'POLICY': 'policyStatus',
    'LABELING': 'labelingStatus',
    'AUTOMATION': 'automationStatus',
    'VULN_SCAN': 'vulnScanStatus'
}

# SBOM Specification Types
SBOM_SPEC_SPDX = 'SPDX'
SBOM_SPEC_CYCLONEDX = 'CycloneDX'

# Content Types
CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_XML = 'text/xml'
CONTENT_TYPE_CSV = 'text/csv'