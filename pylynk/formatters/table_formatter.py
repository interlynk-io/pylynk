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

from pylynk.utils.time import user_time


def format_products_table(products):
    """
    Format products list as a table.
    
    Args:
        products (list): List of product dictionaries
    """
    if not products:
        print("No products found")
        return
    
    # Calculate dynamic column widths
    name_width = max(len("NAME"), max(len(prod['name']) for prod in products))
    updated_at_width = max(len("UPDATED AT"),
                          max(len(user_time(prod['updatedAt'])) for prod in products))
    id_width = max(len("ID"), max(len(prod['id']) for prod in products))
    version_width = len("VERSIONS")
    
    # Print header
    header = (
        f"{'NAME':<{name_width}} | "
        f"{'ID':<{id_width}} | "
        f"{'VERSIONS':<{version_width}} | "
        f"{'UPDATED AT':<{updated_at_width}} | "
    )
    print(header)
    
    # Print separator line
    width = sum([name_width, version_width, updated_at_width, id_width]) + 10
    line = "-" * width + "|"
    print(line)
    
    # Print rows
    for prod in products:
        row = (
            f"{prod['name']:<{name_width}} | "
            f"{prod['id']:<{id_width}} | "
            f"{prod['versions']:<{version_width}} | "
            f"{user_time(prod['updatedAt']):<{updated_at_width}} | "
        )
        print(row)


def format_versions_table(versions):
    """
    Format versions list as a table.
    
    Args:
        versions (list): List of version dictionaries
    """
    if not versions:
        print('No versions found')
        return
    
    # Calculate dynamic column widths
    id_width = max(len('ID'), max(len(sbom['id']) for sbom in versions))
    version_width = max(len('VERSION'), max(
        len(str(s.get('primaryComponent', {}).get('version', ''))) for s in versions))
    primary_component_width = max(len('PRIMARY COMPONENT'), max(
        len(str(sbom.get('primaryComponent', {}).get('name', ''))) for sbom in versions))
    updated_at_width = max(len('UPDATED AT'),
                          max(len(user_time(sbom['updatedAt'])) for sbom in versions))
    
    # Print header
    header = (
        f"{'ID':<{id_width}} | "
        f"{'VERSION':<{version_width}} | "
        f"{'PRIMARY COMPONENT':<{primary_component_width}} | "
        f"{'UPDATED AT':<{updated_at_width}} |"
    )
    print(header)
    
    # Print separator line
    width = sum([id_width, version_width, primary_component_width, updated_at_width]) + 10
    line = "-" * width + "|"
    print(line)
    
    # Print rows
    for sbom in versions:
        if sbom.get('primaryComponent') is None:
            continue
        version = sbom.get('primaryComponent', {}).get('version', '')
        primary_component = sbom.get('primaryComponent', {}).get('name', '')
        row = (
            f"{sbom['id']:<{id_width}} | "
            f"{str(version):<{version_width}} | "
            f"{primary_component:<{primary_component_width}} | "
            f"{user_time(sbom['updatedAt']):<{updated_at_width}} |"
        )
        print(row)


def format_status_table(status):
    """
    Format status dictionary as a table.
    
    Args:
        status (dict): Status dictionary
    """
    if not status:
        print('Failed to fetch status for the version')
        return
    
    # Fixed column widths for status display
    key_width = 20
    value_width = 20
    
    # Print header
    header = (
        f"{'ACTION KEY':<{key_width}} | "
        f"{'STATUS':<{value_width}}"
    )
    print(header)
    
    # Print separator line
    width = key_width + value_width + 5
    line = "-" * width + "|"
    print(line)
    
    # Print rows
    for key, value in status.items():
        row = (
            f"{key:<{key_width}} | "
            f"{value:<{value_width}}  |"
        )
        print(row)