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

"""CSV formatter for PyLynk CLI output."""

import csv
import sys

from pylynk.constants import (
    VULN_COLUMNS, PRODUCT_COLUMNS, VERSION_COLUMNS, STATUS_COLUMNS,
    DEFAULT_PRODUCT_COLUMNS, DEFAULT_VERSION_COLUMNS, DEFAULT_STATUS_COLUMNS
)


def _format_generic_csv(data, columns, column_defs):
    """
    Generic CSV formatter for any data type.

    Args:
        data (list): List of pre-formatted dictionaries (with header names as keys)
        columns (list): List of column names to display
        column_defs (dict): Column definitions with headers
    """
    if not data:
        return

    writer = csv.writer(sys.stdout)

    # Get headers for the columns
    headers = [column_defs[c]['header'] for c in columns if c in column_defs]

    if not headers:
        return

    # Write header
    writer.writerow(headers)

    # Write rows
    for item in data:
        row = [item.get(h, '') for h in headers]
        writer.writerow(row)


def format_products_csv(products, columns=None):
    """
    Format products list as CSV output.

    Args:
        products (list): List of pre-formatted product dictionaries
        columns (list): Optional list of column names to display
    """
    columns = columns or DEFAULT_PRODUCT_COLUMNS
    _format_generic_csv(products, columns, PRODUCT_COLUMNS)


def format_versions_csv(versions, columns=None):
    """
    Format versions list as CSV output.

    Args:
        versions (list): List of pre-formatted version dictionaries
        columns (list): Optional list of column names to display
    """
    columns = columns or DEFAULT_VERSION_COLUMNS
    _format_generic_csv(versions, columns, VERSION_COLUMNS)


def format_status_csv(status, columns=None):
    """
    Format status list as CSV output.

    Args:
        status (list): List of pre-formatted status dictionaries
        columns (list): Optional list of column names to display
    """
    columns = columns or DEFAULT_STATUS_COLUMNS
    _format_generic_csv(status, columns, STATUS_COLUMNS)


def format_vulns_csv(vulns, columns):
    """
    Format vulnerabilities as CSV output.

    Args:
        vulns (list): List of pre-formatted vulnerability dictionaries (with header names as keys)
        columns (list): List of column names to display
    """
    _format_generic_csv(vulns, columns, VULN_COLUMNS)
