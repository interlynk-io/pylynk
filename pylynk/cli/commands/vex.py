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

"""VEX update command implementation."""

import csv
import json
import os

from pylynk.formatters.json_formatter import format_json


VEX_FIELD_MAP = {
    'note': 'note',
    'impact': 'impact',
    'detail': 'detail',
    'action': 'action',
    'fixed_in': 'fixedIn',
}

UNRESOLVED_OPTION = object()


def execute(api_client, config):
    """
    Execute the vex command.

    Args:
        api_client: Initialized API client
        config: Configuration object

    Returns:
        int: Exit code
    """
    if config.vex_action == 'update':
        return _execute_update(api_client, config)
    if config.vex_action == 'bulk-update':
        return _execute_bulk_update(api_client, config)

    print("Error: Missing VEX action. Use 'update' or 'bulk-update'.")
    return 1


def _execute_update(api_client, config):
    if not _resolve_context(api_client, config):
        return 1

    component_vuln_id = _resolve_component_vuln_id(api_client, config, {})
    if not component_vuln_id:
        return 1

    variables = _build_variables(api_client, config, {}, bulk=False)
    if variables is None:
        return 1
    variables['compVulnId'] = component_vuln_id
    variables['sbomId'] = config.ver_id

    payload = api_client.update_component_vex(_drop_none_values(variables))
    if not payload:
        print("Error: VEX update failed")
        return 1

    errors = payload.get('errors')
    if errors:
        print(f"Error updating VEX: {errors}")
        return 1

    component_vuln = payload.get('componentVuln') or {}
    if config.output_format == 'json':
        format_json(component_vuln)
        print()
    else:
        print(f"Updated VEX for component vulnerability {component_vuln.get('id', component_vuln_id)}")
        status = (component_vuln.get('vexStatus') or {}).get('name')
        justification = (component_vuln.get('vexJustification') or {}).get('name')
        response = (component_vuln.get('cdxResponse') or {}).get('name')
        if status:
            print(f"Status: {status}")
        if justification:
            print(f"Justification: {justification}")
        if response:
            print(f"Response: {response}")
    return 0


def _execute_bulk_update(api_client, config):
    if not _resolve_context(api_client, config):
        return 1

    rows = _load_bulk_rows(config)
    if rows is None:
        return 1

    resolved_rows = []
    for row in rows:
        component_vuln_id = _resolve_component_vuln_id(api_client, config, row)
        if not component_vuln_id:
            return 1
        variables = _build_variables(api_client, config, row, bulk=True)
        if variables is None:
            return 1
        resolved_rows.append((component_vuln_id, variables))

    groups = _group_bulk_rows(resolved_rows)
    results = []
    updated_count = 0

    for group in groups:
        variables = group['variables']
        variables['comVulnIds'] = group['component_vuln_ids']
        variables['sbomId'] = config.ver_id

        payload = api_client.bulk_update_component_vex(_drop_none_values(variables))
        if not payload:
            print("Error: Bulk VEX update failed")
            return 1

        errors = payload.get('errors')
        if errors:
            print(f"Error updating VEX: {errors}")
            return 1

        component_vulns = payload.get('componentVulns') or []
        updated_count += len(component_vulns)
        results.extend(component_vulns)

    if config.output_format == 'json':
        format_json(results)
        print()
    else:
        print(f"Updated VEX for {updated_count} component vulnerabilities")
    return 0


def _resolve_context(api_client, config):
    if config.prod and (config.ver or not config.ver_id or config.env):
        original_ver_id = config.ver_id
        if not api_client.resolve_product_env(config.prod, config.env, config.ver):
            print('Could not resolve product, environment, or version')
            return False
        if original_ver_id and not config.ver:
            config.ver_id = original_ver_id
    elif not config.ver_id:
        print("Error: Provide --prod with optional --env/--ver, or provide --verId with component vulnerability IDs.")
        return False

    if not config.ver_id:
        print('Error: No version resolved')
        return False

    return True


def _load_bulk_rows(config):
    if config.vex_file:
        return _read_rows_from_file(config.vex_file)

    ids = config.component_vuln_ids or []
    if not ids:
        print("Error: Provide --file or at least one --component-vuln-id.")
        return None

    return [{'component_vuln_id': component_vuln_id} for component_vuln_id in ids]


def _read_rows_from_file(path):
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        return None

    _, ext = os.path.splitext(path.lower())
    try:
        if ext == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return [_normalize_row_keys(row) for row in data]
            print("Error: JSON VEX file must contain an array of row objects.")
            return None

        with open(path, 'r', encoding='utf-8', newline='') as f:
            return [_normalize_row_keys(row) for row in csv.DictReader(f)]
    except (OSError, csv.Error, json.JSONDecodeError) as ex:
        print(f"Error reading VEX file: {ex}")
        return None


def _normalize_row_keys(row):
    return {
        _normalize_key(key): value
        for key, value in row.items()
        if key is not None
    }


def _normalize_key(key):
    return str(key).strip().lower().replace('-', '_').replace(' ', '_')


def _resolve_component_vuln_id(api_client, config, row):
    component_vuln_id = _first_value(row, 'component_vuln_id', 'component_vuln_uuid')
    if component_vuln_id:
        return component_vuln_id

    component_vuln_id = getattr(config, 'component_vuln_id', None)
    if component_vuln_id:
        return component_vuln_id

    vuln = _first_value(row, 'vuln', 'vuln_id', 'cve', 'id') or config.vuln_id
    component = _first_value(row, 'component', 'component_name') or config.component
    component_version = _first_value(row, 'component_version') or config.component_version

    if not vuln:
        print("Error: Provide component_vuln_id, or provide vuln/CVE plus optional component details.")
        return None

    if not config.env_id:
        print("Error: Name-based component vulnerability resolution requires --prod and --env.")
        return None

    return api_client.resolve_component_vuln_id(
        config.env_id,
        config.ver_id,
        vuln,
        component_name=component,
        component_version=component_version
    )


def _build_variables(api_client, config, row, bulk=False):
    variables = {}

    status_id = _resolve_option(api_client, config, row, 'status', 'vex_status')
    if status_id is UNRESOLVED_OPTION:
        return None
    if status_id:
        variables['vexStatusId'] = status_id
    elif bulk:
        print("Error: Bulk VEX update requires --status/--status-id or status/status_id in the file.")
        return None

    justification_id = _resolve_option(api_client, config, row, 'justification', 'vex_justification')
    if justification_id is UNRESOLVED_OPTION:
        return None
    if justification_id:
        variables['vexJustificationId'] = justification_id

    response_id = _resolve_option(api_client, config, row, 'response', 'cdx_response')
    if response_id is UNRESOLVED_OPTION:
        return None
    if response_id:
        variables['cdxResponseId'] = response_id

    for cli_name, graphql_name in VEX_FIELD_MAP.items():
        value = _first_value(row, cli_name, graphql_name.lower()) or getattr(config, cli_name, None)
        if value is not None:
            variables[graphql_name] = value

    propagate = _first_value(row, 'propagate_vex', 'propagate')
    if propagate is None:
        propagate = config.propagate_vex
    if propagate is not None:
        variables['propagateVex'] = _parse_bool(propagate)

    custom_fields = _load_custom_fields(config.custom_fields_file)
    if custom_fields is None and config.custom_fields_file:
        return None
    if custom_fields is not None:
        variables['componentVulnCustomFieldAttributes'] = custom_fields

    return variables


def _resolve_option(api_client, config, row, option_type, row_prefix):
    id_key = f'{row_prefix}_id'
    name_key = row_prefix

    option_id = _first_value(row, id_key, f'{option_type}_id')
    if option_id:
        return option_id

    option_id = getattr(config, f'{option_type}_id', None)
    if option_id:
        return option_id

    option_name = _first_value(row, name_key, option_type)
    if option_name is None:
        option_name = getattr(config, option_type, None)
    if not option_name:
        return None

    resolved_id = api_client.resolve_vex_option_id(option_type, option_name)
    if not resolved_id:
        valid_names = api_client.list_vex_option_names(option_type)
        print(f"Error: Could not resolve VEX {option_type} name '{option_name}'.")
        if valid_names:
            print(f"Valid {option_type} names: {', '.join(valid_names)}")
        print(f"Or pass --{option_type}-id directly.")
        return UNRESOLVED_OPTION
    return resolved_id


def _load_custom_fields(path):
    if not path:
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as ex:
        print(f"Error reading custom fields file: {ex}")
        return None

    if not isinstance(data, list):
        print("Error: Custom fields file must contain a JSON array.")
        return None
    return data


def _group_bulk_rows(resolved_rows):
    grouped = {}
    for component_vuln_id, variables in resolved_rows:
        key = json.dumps(_drop_none_values(variables), sort_keys=True)
        grouped.setdefault(key, {
            'variables': _drop_none_values(variables),
            'component_vuln_ids': []
        })
        grouped[key]['component_vuln_ids'].append(component_vuln_id)
    return list(grouped.values())


def _drop_none_values(data):
    return {key: value for key, value in data.items() if value is not None}


def _first_value(row, *keys):
    for key in keys:
        value = row.get(key)
        if value not in (None, ''):
            return value
    return None


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    value = str(value).strip().lower()
    if value in ('true', '1', 'yes', 'y'):
        return True
    if value in ('false', '0', 'no', 'n'):
        return False
    return None
