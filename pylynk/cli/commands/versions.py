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
from pylynk.formatters.csv_formatter import format_versions_csv
from pylynk.constants import VERSION_COLUMNS, DEFAULT_VERSION_COLUMNS
from pylynk.utils.time import human_time, user_time


def execute(api_client, config):
    """
    Execute the versions command.

    Args:
        api_client: Initialized API client
        config: Configuration object

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    if not api_client.resolve_product_env(config.prod, config.env):
        print('Could not resolve product or environment')
        return 1

    versions = api_client.get_versions(config.prod_id, config.env_id)

    if not versions:
        print('No versions found')
        return 0

    # Check if human-friendly timestamps are requested
    use_human_time = getattr(config, 'human_time', False)

    # Transform raw data to formatted rows
    formatted_versions = _format_version_data(versions, DEFAULT_VERSION_COLUMNS, use_human_time)

    # Output based on format
    output_format = getattr(config, 'output_format', 'table')

    if output_format == 'json':
        format_json(formatted_versions)
    elif output_format == 'csv':
        format_versions_csv(formatted_versions)
    else:
        format_versions_table(formatted_versions)

    return 0


def _get_value(item, column):
    """
    Extract value from item using column path.

    Args:
        item (dict): Data item
        column (str): Column name

    Returns:
        Value extracted from item, or empty string if not found
    """
    col_def = VERSION_COLUMNS.get(column, {})
    path = col_def.get('path', [])

    value = item
    for key in path:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            value = None
            break

    return value if value is not None else ''


def _format_version_data(versions, columns, use_human_time=False):
    """
    Transform raw version data into formatted rows with selected columns.

    Args:
        versions (list): List of raw version dictionaries from API
        columns (list): List of column names to include
        use_human_time (bool): If True, format timestamps as human-friendly strings

    Returns:
        list: List of dictionaries with column headers as keys
    """
    formatted = []
    for version in versions:
        # Skip versions without primary component
        if version.get('primaryComponent') is None:
            continue

        row = {}
        for col in columns:
            if col in VERSION_COLUMNS:
                col_def = VERSION_COLUMNS[col]
                header = col_def['header']
                value = _get_value(version, col)

                # Apply time formatting for timestamp columns
                if col_def.get('is_timestamp') and value:
                    if use_human_time:
                        value = human_time(value)
                    else:
                        value = user_time(value)

                row[header] = value
        formatted.append(row)
    return formatted
