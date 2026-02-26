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

"""Download command implementation."""

import json
from pylynk.formatters.json_formatter import format_json
from pylynk.utils.validators import parse_boolean_flag
from pylynk.constants import CONTENT_TYPE_JSON, CONTENT_TYPE_CSV, CONTENT_TYPE_XML, PROCESSING_STAGE_MAP


def _parse_wait_for(wait_for_str):
    """
    Parse --wait-for argument into list of GraphQL enum values.

    Args:
        wait_for_str (str): Comma-separated stage names (e.g. "vuln-scan,automation")

    Returns:
        list: GraphQL enum values, or None if input is None/empty
    """
    if not wait_for_str:
        return None

    stages = []
    for stage in wait_for_str.split(','):
        stage = stage.strip().lower()
        if stage not in PROCESSING_STAGE_MAP:
            valid = ', '.join(sorted(PROCESSING_STAGE_MAP.keys()))
            print(f"Error: unknown processing stage '{stage}'")
            print(f"Valid stages: {valid}")
            return False
        stages.append(PROCESSING_STAGE_MAP[stage])

    return stages if stages else None


def execute(api_client, config):
    """
    Execute the download command.

    Args:
        api_client: Initialized API client
        config: Configuration object

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # If using names instead of IDs, resolve them first
    if not config.ver_id and config.prod and config.env and config.ver:
        if not api_client.resolve_identifiers():
            return 1

    # Parse boolean flag for vulnerabilities
    include_vulns = parse_boolean_flag(config.vuln)

    # Parse --wait-for stages
    require_completed = _parse_wait_for(config.wait_for)
    if require_completed is False:
        return 1

    # Call download with resolved IDs
    content, content_type, filename = api_client.download_sbom(
        env_id=config.env_id,
        ver_id=config.ver_id,
        include_vulns=include_vulns,
        spec=config.spec,
        spec_version=config.spec_version,
        lite=config.lite,
        dont_package_sbom=config.dont_package_sbom,
        original=config.original,
        exclude_parts=config.exclude_parts,
        include_support_status=config.include_support_status,
        support_level_only=getattr(config, 'support_level_only', False),
        require_completed=require_completed,
        poll_interval=config.poll_interval,
        poll_timeout=config.poll_timeout,
    )

    if content is None:
        print('Failed to fetch SBOM')
        return 1

    # Determine output filename
    output_file = config.output_file or filename

    # Handle different content types
    if content_type == CONTENT_TYPE_JSON and not config.original:
        # Parse and format JSON
        try:
            sbom_data = json.loads(content)
            format_json(sbom_data, output_file)
        except json.JSONDecodeError:
            # If JSON parsing fails, write as-is
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(content)
            else:
                print(content)
    elif content_type == CONTENT_TYPE_CSV:
        # CSV content (support level only)
        if output_file:
            with open(output_file, 'w') as f:
                f.write(content)
        else:
            print(content)
    else:
        # XML or original content - write as-is
        if output_file:
            with open(output_file, 'w') as f:
                f.write(content)
        else:
            print(content)

    return 0
