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

"""Table formatter for PyLynk CLI output."""

from pylynk.constants import (
    VULN_COLUMNS, PRODUCT_COLUMNS, VERSION_COLUMNS, STATUS_COLUMNS,
    DEFAULT_PRODUCT_COLUMNS, DEFAULT_VERSION_COLUMNS, DEFAULT_STATUS_COLUMNS
)


def _format_generic_table(data, columns, column_defs):
    """
    Generic table formatter for any data type.

    Args:
        data (list): List of pre-formatted dictionaries (with header names as keys)
        columns (list): List of column names to display
        column_defs (dict): Column definitions with headers
    """
    if not data:
        return

    # Get headers for the columns
    headers = [column_defs[c]['header'] for c in columns if c in column_defs]

    if not headers:
        return

    # Calculate column widths based on header names and values
    col_widths = {}
    for header in headers:
        max_val_len = max(len(str(v.get(header, ''))) for v in data) if data else 0
        col_widths[header] = max(len(header), max_val_len, 5)  # Minimum width of 5

    # Print header
    header_parts = [f"{h:<{col_widths[h]}}" for h in headers]
    print(" | ".join(header_parts))

    # Print separator
    separator_parts = ["-" * col_widths[h] for h in headers]
    print("-|-".join(separator_parts))

    # Print rows
    for item in data:
        row_parts = [f"{str(item.get(h, '')):<{col_widths[h]}}" for h in headers]
        print(" | ".join(row_parts))


def format_products_table(products, columns=None):
    """
    Format products list as a table.

    Args:
        products (list): List of pre-formatted product dictionaries
        columns (list): Optional list of column names to display
    """
    if not products:
        print("No products found")
        return

    columns = columns or DEFAULT_PRODUCT_COLUMNS
    _format_generic_table(products, columns, PRODUCT_COLUMNS)


def format_versions_table(versions, columns=None):
    """
    Format versions list as a table.

    Args:
        versions (list): List of pre-formatted version dictionaries
        columns (list): Optional list of column names to display
    """
    if not versions:
        print('No versions found')
        return

    columns = columns or DEFAULT_VERSION_COLUMNS
    _format_generic_table(versions, columns, VERSION_COLUMNS)


def format_status_table(status, columns=None):
    """
    Format status list as a table.

    Args:
        status (list): List of pre-formatted status dictionaries
        columns (list): Optional list of column names to display
    """
    if not status:
        print('Failed to fetch status for the version')
        return

    columns = columns or DEFAULT_STATUS_COLUMNS
    _format_generic_table(status, columns, STATUS_COLUMNS)


def format_vulns_table(vulns, columns):
    """
    Format vulnerabilities as a table with dynamic columns.

    Args:
        vulns (list): List of pre-formatted vulnerability dictionaries (with header names as keys)
        columns (list): List of column names to display
    """
    if not vulns:
        print('No vulnerabilities found')
        return

    # Get headers for the columns
    headers = [VULN_COLUMNS[c]['header'] for c in columns if c in VULN_COLUMNS]

    if not headers:
        print('No valid columns specified')
        return

    # Calculate column widths based on header names and values
    col_widths = {}
    for header in headers:
        max_val_len = max(len(str(v.get(header, ''))) for v in vulns) if vulns else 0
        col_widths[header] = max(len(header), max_val_len, 5)  # Minimum width of 5

    # Print header
    header_parts = [f"{h:<{col_widths[h]}}" for h in headers]
    print(" | ".join(header_parts))

    # Print separator
    separator_parts = ["-" * col_widths[h] for h in headers]
    print("-|-".join(separator_parts))

    # Print rows
    for vuln in vulns:
        row_parts = [f"{str(vuln.get(h, '')):<{col_widths[h]}}" for h in headers]
        print(" | ".join(row_parts))
