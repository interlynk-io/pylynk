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

"""Gate command implementation - CI policy gate with blocking exit codes."""

import time
from pylynk.formatters.json_formatter import format_json
from pylynk.formatters.table_formatter import format_gate_table
from pylynk.constants import (
    EXIT_SUCCESS, EXIT_ERROR, EXIT_POLICY_FAIL, EXIT_INDETERMINATE,
    GATE_STATUS_PASS, GATE_STATUS_FAIL, GATE_STATUS_ERROR,
    GATE_STATUS_IN_PROGRESS, GATE_STATUS_NOT_EVALUATED, GATE_STATUS_NO_POLICIES,
    GATE_COLUMNS
)

# Exit code and closing note for each gate status, in one place so the two
# cannot drift. Anything unexpected falls through to the fail-closed default.
GATE_OUTCOMES = {
    GATE_STATUS_PASS: (EXIT_SUCCESS, None),
    GATE_STATUS_NO_POLICIES: (
        EXIT_SUCCESS,
        'Warning: no active policies are configured for this organization '
        '- gate passes by default'),
    GATE_STATUS_FAIL: (EXIT_POLICY_FAIL, None),
    GATE_STATUS_IN_PROGRESS: (
        EXIT_INDETERMINATE,
        'Policy scan is still running - failing closed'),
    GATE_STATUS_ERROR: (
        EXIT_INDETERMINATE,
        'Policy evaluation is incomplete or errored - failing closed'),
    GATE_STATUS_NOT_EVALUATED: (
        EXIT_INDETERMINATE,
        'Policies were not evaluated for this SBOM (is vulnerability scanning '
        'enabled for the environment?) - failing closed'),
}


def _format_violations(gate):
    """Flatten violating policies into table rows keyed by header name."""
    return [
        {
            GATE_COLUMNS['policy']['header']: violation.get('policyName', ''),
            GATE_COLUMNS['severity']['header']: violation.get('resultType', ''),
            GATE_COLUMNS['violations']['header']: violation.get('violationsCount', 0),
        }
        for violation in gate.get('violatingPolicies') or []
    ]


def _print_summary(gate):
    """Print the gate verdict summary."""
    counts = gate.get('counts') or {}
    print(f"Policy gate: {gate.get('status', 'UNKNOWN')}")
    print(f"  Policies evaluated: {counts.get('total', 0)} "
          f"(passed: {counts.get('passed', 0)}, failed: {counts.get('failed', 0)}, "
          f"warned: {counts.get('warned', 0)}, skipped: {counts.get('skipped', 0)}, "
          f"errored: {counts.get('errored', 0)})")


def execute(api_client, config):
    """
    Execute the gate command.

    Args:
        api_client: Initialized API client
        config: Configuration object

    Returns:
        int: Exit code - 0 pass, 1 operational error, 3 policy failure,
             4 indeterminate (timeout, scan error, or not evaluated)
    """
    deadline = time.time() + config.gate_timeout if config.gate_wait else None

    # Resolve names to the SBOM ID unless --verId was given (never clobber it)
    if not config.ver_id:
        resolved = api_client.resolve_version_with_retry(
            config.prod, config.env, config.ver,
            deadline=deadline,
            poll_interval=config.poll_interval,
        )
        if not resolved:
            print('Could not resolve product, environment, or version')
            print('If the SBOM was just uploaded, processing may not have '
                  'started yet - consider a longer --timeout')
            return EXIT_ERROR

    gate = api_client.wait_for_policy_gate(
        config.ver_id,
        fail_on=config.fail_on,
        deadline=deadline,
        poll_interval=config.poll_interval,
        policy_id=config.policy_id,
        policy_name=config.policy_name,
    )

    if gate is None:
        print('Failed to fetch policy gate verdict')
        return EXIT_ERROR

    status = gate.get('status')

    if config.output_format == 'json':
        format_json(gate)
    else:
        _print_summary(gate)
        rows = _format_violations(gate)
        if rows:
            print()
            format_gate_table(rows)

    # Human-readable outcome note (stdout, after the data)
    exit_code, note = GATE_OUTCOMES.get(status, (EXIT_INDETERMINATE, None))
    if note:
        print(f'{note} (exit {exit_code})')

    return exit_code
