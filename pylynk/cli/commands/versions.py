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

"""Versions command implementation."""

from pylynk.formatters.json_formatter import format_json
from pylynk.formatters.table_formatter import format_versions_table


def execute(api_client, config):
    """
    Execute the versions command.
    
    Args:
        api_client: Initialized API client
        config: Configuration object
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    if not api_client.resolve_identifiers():
        return 1
    
    # After resolve_identifiers, prod_id should be set on config if product was resolved
    if not hasattr(config, 'prod_id') or not config.prod_id:
        print('Product ID not resolved')
        return 1
    
    versions = api_client.get_versions(config.prod_id, config.env_id)
    
    if not versions:
        print('No versions found')
        return 0
    
    if config.format_json:
        format_json(versions)
    else:
        format_versions_table(versions)
    
    return 0