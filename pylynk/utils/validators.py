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

"""Input validation utilities for PyLynk CLI."""

import os
from pylynk.constants import VALID_BOOLEAN_VALUES


def validate_file_exists(file_path):
    """
    Validate that a file exists.

    Args:
        file_path (str): Path to the file

    Returns:
        bool: True if file exists, False otherwise
    """
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return False
    return True


def validate_boolean_flag(value, flag_name):
    """
    Validate a boolean flag value.

    Args:
        value: Value to validate
        flag_name (str): Name of the flag for error messages

    Returns:
        bool: True if valid, False otherwise
    """
    if value is None:
        return True

    if str(value).lower() not in VALID_BOOLEAN_VALUES:
        print(
            f"Invalid value for {flag_name}: {value}. Expected one of {VALID_BOOLEAN_VALUES}")
        return False
    return True


def parse_boolean_flag(value):
    """
    Parse a boolean flag value.

    Args:
        value: Value to parse

    Returns:
        bool: Parsed boolean value
    """
    if value is None:
        return False

    value_str = str(value).lower()
    return value_str in ['true', '1', 'yes']
