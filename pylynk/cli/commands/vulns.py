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

"""Vulns command implementation."""

from pylynk.formatters.json_formatter import format_json
from pylynk.formatters.table_formatter import format_vulns_table
from pylynk.formatters.csv_formatter import format_vulns_csv
from pylynk.constants import (
    DEFAULT_VULN_COLUMNS, VULN_META_COLUMNS, VEX_COLUMNS,
    TIMESTAMP_COLUMNS, VULN_COLUMNS
)
from pylynk.utils.time import human_time


def execute(api_client, config):
    """
    Execute the vulns command.

    Args:
        api_client: Initialized API client
        config: Configuration object

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Handle --list-columns flag
    if getattr(config, 'list_columns', False):
        _print_available_columns()
        return 0

    # Resolve product/environment/version (latest picked if --ver omitted)
    if not api_client.resolve_product_env(config.prod, config.env, config.ver):
        print('Could not resolve product, environment, or version')
        return 1

    if not config.ver_id:
        print('Error: No versions found for this product/environment')
        return 1

    # Fetch vulnerabilities
    vulns_data = api_client.get_vulnerabilities(config.env_id, config.ver_id)

    if not vulns_data or not vulns_data.get('nodes'):
        print('No vulnerabilities found')
        return 0

    # Determine columns to display
    columns = _get_columns(config)

    # Check if human-friendly timestamps are requested
    use_human_time = getattr(config, 'human_time', False)

    # Transform raw data to formatted rows with selected columns
    formatted_vulns = _format_vuln_data(vulns_data['nodes'], columns, use_human_time)

    # Output based on format
    output_format = getattr(config, 'output_format', 'table')

    if output_format == 'json':
        format_json(formatted_vulns)
    elif output_format == 'csv':
        format_vulns_csv(formatted_vulns, columns)
    else:
        format_vulns_table(formatted_vulns, columns)

    return 0


def _get_columns(config):
    """
    Determine which columns to display.

    Args:
        config: Configuration object

    Returns:
        list: List of column names to display
    """
    # User specified custom columns
    if getattr(config, 'columns', None):
        user_cols = [c.strip().lower() for c in config.columns.split(',')]
        valid_cols = [c for c in user_cols if c in VULN_COLUMNS]
        if valid_cols:
            return valid_cols
        # If no valid columns, fall back to default
        print(f"Warning: No valid columns specified. Available columns: {', '.join(VULN_COLUMNS.keys())}")

    # Default columns, optionally extended with detail flags
    columns = DEFAULT_VULN_COLUMNS.copy()

    if getattr(config, 'vuln_details', False):
        columns.extend([c for c in VULN_META_COLUMNS if c not in columns])

    if getattr(config, 'vex_details', False):
        columns.extend([c for c in VEX_COLUMNS if c not in columns])

    if getattr(config, 'timestamp_details', False):
        columns.extend([c for c in TIMESTAMP_COLUMNS if c not in columns])

    return columns


def _get_value(vuln, column):
    """
    Extract value from vulnerability using column path.

    Args:
        vuln (dict): Vulnerability data
        column (str): Column name

    Returns:
        Value extracted from vulnerability, or empty string if not found
    """
    col_def = VULN_COLUMNS.get(column, {})

    # Handle columns that require isPart flag check
    if col_def.get('requires_is_part'):
        is_part = vuln.get('isPart', False)
        if not is_part:
            return 'N/A'

    path = col_def.get('path', [])

    value = vuln
    for key in path:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            value = None
            break

    # Try fallback path if primary is None
    if value is None and 'fallback' in col_def:
        value = vuln
        for key in col_def['fallback']:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break

    # Handle list values (like CWE)
    if isinstance(value, list):
        value = ', '.join(str(v) for v in value)

    return value if value is not None else ''


def _format_vuln_data(vulns, columns, use_human_time=False):
    """
    Transform raw vulnerability data into formatted rows with selected columns.

    Args:
        vulns (list): List of raw vulnerability dictionaries from API
        columns (list): List of column names to include
        use_human_time (bool): If True, format timestamps as human-friendly strings

    Returns:
        list: List of dictionaries with column headers as keys
    """
    formatted = []
    for vuln in vulns:
        row = {}
        for col in columns:
            if col in VULN_COLUMNS:
                col_def = VULN_COLUMNS[col]
                header = col_def['header']
                value = _get_value(vuln, col)

                # Apply human-friendly time formatting for timestamp columns
                if use_human_time and col_def.get('is_timestamp') and value:
                    value = human_time(value)

                row[header] = value
        formatted.append(row)
    return formatted


def _print_available_columns():
    """Print available column names that can be used with --columns."""
    print("Available columns for --columns option:\n")

    # Group columns by category
    categories = {
        'Basic': ['id', 'part_name', 'part_version', 'component_name', 'component_version', 'source', 'assigned'],
        'Vulnerability Meta (--vuln-details)': ['severity', 'kev', 'cvss', 'cvss_vector', 'epss', 'cwe'],
        'VEX Information (--vex-details)': ['status', 'details', 'notes', 'justification',
                                            'action_statement', 'impact_statement', 'response'],
        'Timestamps (--timestamp-details)': ['assigned', 'published', 'last_modified', 'updated']
    }

    # Calculate column width for alignment
    max_name_len = max(len(name) for name in VULN_COLUMNS.keys())

    for category, cols in categories.items():
        print(f"{category}:")
        for col in cols:
            if col in VULN_COLUMNS:
                header = VULN_COLUMNS[col]['header']
                note = " (N/A if not from a part)" if VULN_COLUMNS[col].get('requires_is_part') else ""
                print(f"  {col:<{max_name_len}}  ->  {header}{note}")
        print()

    print(f"Default columns: {', '.join(DEFAULT_VULN_COLUMNS)}")
    print(f"Vuln meta columns (--vuln-details): {', '.join(VULN_META_COLUMNS)}")
    print(f"VEX columns (--vex-details): {', '.join(VEX_COLUMNS)}")
    print(f"Timestamp columns (--timestamp-details): {', '.join(TIMESTAMP_COLUMNS)}")
    print("\nExample: --columns \"id,component_name,severity,cvss\"")
