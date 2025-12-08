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

"""Products command implementation."""

from pylynk.formatters.json_formatter import format_json
from pylynk.formatters.table_formatter import format_products_table
from pylynk.formatters.csv_formatter import format_products_csv
from pylynk.constants import PRODUCT_COLUMNS, DEFAULT_PRODUCT_COLUMNS
from pylynk.utils.time import human_time, user_time


def execute(api_client, config):
    """
    Execute the products command.

    Args:
        api_client: Initialized API client
        config: Configuration object

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    products = api_client.get_products()

    if not products:
        print("No products found")
        return 1

    # Check if human-friendly timestamps are requested
    use_human_time = getattr(config, 'human_time', False)

    # Transform raw data to formatted rows
    formatted_products = _format_product_data(products, DEFAULT_PRODUCT_COLUMNS, use_human_time)

    # Output based on format
    output_format = getattr(config, 'output_format', 'table')

    if output_format == 'json':
        format_json(formatted_products)
    elif output_format == 'csv':
        format_products_csv(formatted_products)
    else:
        format_products_table(formatted_products)

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
    col_def = PRODUCT_COLUMNS.get(column, {})
    path = col_def.get('path', [])

    value = item
    for key in path:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            value = None
            break

    return value if value is not None else ''


def _format_product_data(products, columns, use_human_time=False):
    """
    Transform raw product data into formatted rows with selected columns.

    Args:
        products (list): List of raw product dictionaries from API
        columns (list): List of column names to include
        use_human_time (bool): If True, format timestamps as human-friendly strings

    Returns:
        list: List of dictionaries with column headers as keys
    """
    formatted = []
    for product in products:
        row = {}
        for col in columns:
            if col in PRODUCT_COLUMNS:
                col_def = PRODUCT_COLUMNS[col]
                header = col_def['header']
                value = _get_value(product, col)

                # Apply time formatting for timestamp columns
                if col_def.get('is_timestamp') and value:
                    if use_human_time:
                        value = human_time(value)
                    else:
                        value = user_time(value)

                row[header] = value
        formatted.append(row)
    return formatted
