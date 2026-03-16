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

"""Report command implementation."""

import csv
import logging
import re
import sys


def execute(api_client, config):
    """
    Execute the report command.

    Args:
        api_client: Initialized API client
        config: Configuration object

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    if config.report_type == 'attribution':
        return _execute_attribution(api_client, config)

    print(f"Error: Unknown report type '{config.report_type}'")
    return 1


def _execute_attribution(api_client, config):
    """Execute the attribution report."""
    # Resolve product, environment, and version with a targeted query
    # If --ver is omitted, the latest version (by createdAt) is auto-selected
    if not api_client.resolve_product_env(config.prod, config.env, config.ver):
        print(f"Error: Could not resolve product '{config.prod}', environment '{config.env or 'default'}'"
              + (f", or version '{config.ver}'" if config.ver else ""))
        return 1

    if not config.ver_id:
        print(f"Error: No versions found for '{config.prod}' in '{config.env}'")
        return 1

    logging.debug("Resolved: prod_id=%s, env_id=%s, ver_id=%s",
                  config.prod_id, config.env_id, config.ver_id)

    nodes = api_client.get_attributions(config.ver_id, include_license_text=config.include_license_text)

    if nodes is None:
        print(f"Error: Failed to fetch attribution data for '{config.prod}'")
        return 1

    if not nodes:
        print(f"No attribution data found for '{config.prod}'")
        return 0

    rows = _flatten_attribution_nodes(nodes, config.include_license_text)
    _write_csv(rows, config.output_file, config.include_license_text)
    return 0


def _clean_license(value):
    """Strip LicenseRef-interlynk tokens from license expressions.

    Mirrors the JS parseLicenseString: /-?LicenseRef-interlynk-?/g
    Then cleans up dangling AND/OR operators and extra whitespace.
    """
    if not value:
        return ''
    cleaned = re.sub(r'-?LicenseRef-interlynk-?', '', value)
    # Clean up dangling operators left after removal
    cleaned = re.sub(r'\(\s*\)', '', cleaned)
    cleaned = re.sub(r'^\s*(AND|OR)\s+', '', cleaned)
    cleaned = re.sub(r'\s+(AND|OR)\s*$', '', cleaned)
    cleaned = re.sub(r'\s+(AND|OR)\s+(AND|OR)\s+', ' ', cleaned)
    return cleaned.strip()


def _clean_license_key(key):
    """Strip LicenseRef-interlynk prefix from license text keys.

    Also strips bare 'interlynk-' prefix.
    """
    if not key:
        return ''
    cleaned = re.sub(r'-?LicenseRef-interlynk-?', '', key)
    if cleaned.startswith('interlynk-'):
        cleaned = cleaned[len('interlynk-'):]
    return cleaned.strip()


def _flatten_attribution_nodes(nodes, include_license_text):
    """
    Flatten attribution nodes into CSV rows.
    One row per component; attribution data is duplicated per component.
    """
    rows = []
    for node in nodes:
        attr = node.get('attribution') or {}
        components = node.get('components') or []

        base = {
            'Component Name': '',
            'Component Version': '',
            'Declared Licenses': _clean_license(attr.get('declaredLicensesExp', '') or ''),
            'Licenses': _clean_license(attr.get('licensesExp', '') or ''),
            'Copyright': attr.get('copyright', '') or '',
            'Notice': attr.get('notice', '') or '',
        }

        if include_license_text:
            license_texts = attr.get('licensesText') or []
            base['License Texts'] = '; '.join(
                f"{_clean_license_key(lt.get('key', ''))}: {lt.get('value', '')}"
                for lt in license_texts
            ) if license_texts else ''

        if components:
            for comp in components:
                row = dict(base)
                row['Component Name'] = comp.get('name', '') or ''
                row['Component Version'] = comp.get('version', '') or ''
                rows.append(row)
        else:
            rows.append(base)

    return rows


def _write_csv(rows, output_file, include_license_text):
    """Write rows to CSV file or stdout."""
    headers = [
        'Component Name', 'Component Version',
        'Declared Licenses', 'Licenses',
        'Copyright', 'Notice',
    ]
    if include_license_text:
        headers.append('License Texts')

    if output_file:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
        print(f"Report written to {output_file}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
