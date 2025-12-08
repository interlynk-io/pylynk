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

# CI/CD Environment Detection
ENV_GITHUB_ACTIONS = 'GITHUB_ACTIONS'
ENV_BITBUCKET_BUILD = 'BITBUCKET_BUILD_NUMBER'
ENV_CI = 'CI'

# CI Metadata Inclusion Flag
ENV_INCLUDE_CI_METADATA = 'PYLYNK_INCLUDE_CI_METADATA'

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

# Vulnerability column definitions for vulns command
# Note: 'part_name' and 'part_version' use special handling based on 'isPart' flag
VULN_COLUMNS = {
    # Basic info
    'id': {'path': ['vuln', 'nvdAliasId'], 'fallback': ['vuln', 'vulnId'], 'header': 'ID'},
    'part_name': {'path': ['component', 'sbom', 'project', 'projectGroup', 'name'],
                  'header': 'PART NAME', 'requires_is_part': True},
    'part_version': {'path': ['component', 'sbom', 'projectVersion'],
                     'header': 'PART VERSION', 'requires_is_part': True},
    'component_name': {'path': ['component', 'name'], 'header': 'COMPONENT NAME'},
    'component_version': {'path': ['component', 'version'], 'header': 'COMPONENT VERSION'},
    'source': {'path': ['vuln', 'source'], 'header': 'SOURCE'},

    # Vuln meta
    'severity': {'path': ['vuln', 'sev'], 'header': 'SEVERITY'},
    'kev': {'path': ['vuln', 'vulnInfo', 'kev'], 'header': 'KEV'},
    'cvss': {'path': ['vuln', 'cvssScore'], 'header': 'CVSS'},
    'cvss_vector': {'path': ['vuln', 'cvssVector'], 'header': 'CVSS VECTOR'},
    'epss': {'path': ['vuln', 'vulnInfo', 'epssScore'], 'header': 'EPSS'},
    'cwe': {'path': ['vuln', 'vulnInfo', 'cwes'], 'header': 'CWE'},

    # VEX info
    'status': {'path': ['vexStatus', 'name'], 'header': 'STATUS'},
    'details': {'path': ['detail'], 'header': 'DETAILS'},
    'notes': {'path': ['note'], 'header': 'NOTES'},
    'justification': {'path': ['vexJustification', 'name'], 'header': 'JUSTIFICATION'},
    'action_statement': {'path': ['actionStmt'], 'header': 'ACTION STATEMENT'},
    'impact_statement': {'path': ['impact'], 'header': 'IMPACT STATEMENT'},
    'response': {'path': ['cdxResponse', 'name'], 'header': 'RESPONSE'},

    # Timestamps
    'assigned': {'path': ['createdAt'], 'header': 'ASSIGNED', 'is_timestamp': True},
    'published': {'path': ['vuln', 'publishedAt'], 'header': 'PUBLISHED', 'is_timestamp': True},
    'last_modified': {'path': ['vuln', 'lastModifiedAt'], 'header': 'LAST MODIFIED', 'is_timestamp': True},
    'updated': {'path': ['vuln', 'updatedAt'], 'header': 'UPDATED', 'is_timestamp': True},
}

DEFAULT_VULN_COLUMNS = ['id', 'part_name', 'part_version', 'component_name', 'component_version', 'severity', 'source', 'status', 'assigned']
VULN_META_COLUMNS = ['severity', 'kev', 'cvss', 'cvss_vector', 'epss', 'cwe']
VEX_COLUMNS = ['status', 'details', 'justification', 'action_statement', 'impact_statement', 'response']
TIMESTAMP_COLUMNS = ['assigned', 'published', 'last_modified', 'updated']
