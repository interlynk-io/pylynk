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

"""Status command implementation."""

from pylynk.formatters.json_formatter import format_json
from pylynk.formatters.table_formatter import format_status_table


def execute(api_client, config):
    """
    Execute the status command.
    
    Args:
        api_client: Initialized API client
        config: Configuration object
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    if not api_client.resolve_identifiers():
        return 1
    
    # Get status based on version's vulnerability status
    status = api_client.get_status(getattr(config, 'ver_status', ''))
    
    if not status:
        print('Failed to fetch status for the version')
        return 1
    
    if config.format_json:
        format_json(status)
    else:
        format_status_table(status)
    
    return 0