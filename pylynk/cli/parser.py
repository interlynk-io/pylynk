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

"""Command line argument parser for PyLynk CLI."""

import argparse
import sys

from pylynk.constants import DEFAULT_GATE_TIMEOUT, DEFAULT_GATE_POLL_INTERVAL


class CustomArgumentParser(argparse.ArgumentParser):
    """Custom argument parser with improved error messages."""

    def error(self, message):
        """Print a usage message with examples on error."""
        self.print_usage(sys.stderr)

        # Get the command name for context-specific help
        prog_parts = self.prog.split()
        command = prog_parts[-1] if len(prog_parts) > 1 else None

        # Print the error
        sys.stderr.write(f'\nerror: {message}\n')

        # Add helpful examples based on command
        examples = _get_command_examples(command)
        if examples:
            sys.stderr.write(f'\nExamples:\n{examples}\n')

        sys.stderr.write(f'\nFor more information, try: {self.prog} --help\n')
        sys.exit(2)


def _get_command_examples(command):
    """Get example usage for a specific command."""
    examples = {
        'prods': '''  pylynk prods
  pylynk prods --output json
  pylynk prods --human-time''',

        'vers': '''  pylynk vers --prod 'my-product'
  pylynk vers --prod 'my-product' --env 'production'
  pylynk vers --prod 'my-product' --output json''',

        'status': '''  pylynk status --prod 'my-product' --verId 'abc-123'
  pylynk status --prod 'my-product' --ver 'v1.0.0' --env 'production' ''',

        'upload': '''  pylynk upload --prod 'my-product' --sbom sbom.json
  pylynk upload --prod 'my-product' --env 'production' --sbom sbom.json''',

        'download': '''  pylynk download --prod 'my-product' --env 'default' --ver 'v1.0.0'
  pylynk download --prod 'my-product' --env 'default' --ver 'v1.0.0' --out-file sbom.json
  pylynk download --prod 'my-product' --env 'default' --ver 'v1.0.0' --wait-for vuln-scan,automation
  pylynk download --verId 'abc-123' --out-file sbom.json''',

        'gate': '''  pylynk gate --prod 'my-product' --env 'default' --ver 'v1.0.0'
  pylynk gate --prod 'my-product' --env 'default' --ver 'v1.0.0' --timeout 900
  pylynk gate --prod 'my-product' --env 'default' --ver 'v1.0.0' --policy-name 'No criticals'
  pylynk gate --verId 'abc-123' --fail-on warn
  pylynk gate --verId 'abc-123' --no-wait --output json''',

        'vulns': '''  pylynk vulns --prod 'my-product'
  pylynk vulns --prod 'my-product' --env 'production'
  pylynk vulns --prod 'my-product' --vuln-details --vex-details
  pylynk vulns --list-columns''',

        'vex': '''  pylynk vex update --prod 'my-product' --ver 'v1.0.0' --vuln CVE-2024-1234 --component lodash --status not_affected
  pylynk vex bulk-update --prod 'my-product' --ver 'v1.0.0' --file vex-updates.csv
  pylynk vex bulk-update --verId 'abc-123' --component-vuln-id 'def-456' --status affected''',

        'report': '''  pylynk report --type attribution --prod 'my-product' --env 'production' --ver 'v1.0.0'
  pylynk report --type attribution --prod 'my-product' --env 'production'
  pylynk report --type attribution --prod 'my-product' --env 'default' --ver 'v1.0.0' --include-license-text
  pylynk report --type attribution --prod 'my-product' --env 'default' --ver 'v1.0.0' --output-file report.csv''',
    }
    return examples.get(command)


def add_output_format_group(parser, include_csv=True):
    """
    Add output format arguments to a parser.

    Args:
        parser: Argument parser or subparser
        include_csv (bool): Whether to include CSV as an option
    """
    choices = ['table', 'json', 'csv'] if include_csv else ['table', 'json']
    parser.add_argument("--output", choices=choices,
                        default='table', help="Output format (default: table)")


def add_human_time_argument(parser):
    """
    Add human-friendly time format argument to a parser.

    Args:
        parser: Argument parser or subparser
    """
    parser.add_argument("--human-time", action='store_true', default=True,
                        help="Show timestamps in human-friendly format (default: enabled)")
    parser.add_argument("--no-human-time", action='store_false', dest='human_time',
                        help="Show timestamps in raw ISO format")


def add_common_arguments(parser):
    """
    Add common arguments to a parser.

    Args:
        parser: Argument parser or subparser
    """
    parser.add_argument("--token", required=False, help="Security token")


def add_product_arguments(parser, required=True):
    """
    Add product identification arguments.

    Args:
        parser: Argument parser or subparser
        required (bool): Whether product identification is required
    """
    parser.add_argument("--prod", help="Product name", required=required)


def add_environment_argument(parser):
    """
    Add environment argument to a parser.

    Args:
        parser: Argument parser or subparser
    """
    parser.add_argument("--env", help="Environment", required=False)


def add_version_arguments(parser, required=True):
    """
    Add version identification arguments.

    Args:
        parser: Argument parser or subparser
        required (bool): Whether version identification is required
    """
    version_group = parser.add_mutually_exclusive_group(required=required)
    version_group.add_argument("--ver", help="Version")
    version_group.add_argument("--verId", help="Version ID")


def add_vex_target_arguments(parser):
    """Add product/version targeting arguments for VEX commands."""
    add_product_arguments(parser, required=False)
    add_environment_argument(parser)
    add_version_arguments(parser, required=False)


def add_vex_payload_arguments(parser):
    """Add shared VEX mutation payload arguments."""
    parser.add_argument("--status", help="VEX status name")
    parser.add_argument("--status-id", help="VEX status ID")
    parser.add_argument("--justification", help="VEX justification name")
    parser.add_argument("--justification-id", help="VEX justification ID")
    parser.add_argument("--response", help="CycloneDX response name")
    parser.add_argument("--response-id", help="CycloneDX response ID")
    parser.add_argument("--note", help="VEX note")
    parser.add_argument("--impact", help="VEX impact statement")
    parser.add_argument("--detail", help="VEX detail")
    parser.add_argument("--action", help="VEX action statement")
    parser.add_argument("--fixed-in", help="Fixed-in version")
    propagate_group = parser.add_mutually_exclusive_group()
    propagate_group.add_argument("--propagate", dest="propagate_vex", action="store_true",
                                 help="Propagate VEX to related component vulnerabilities")
    propagate_group.add_argument("--no-propagate", dest="propagate_vex", action="store_false",
                                 help="Do not propagate VEX")
    parser.set_defaults(propagate_vex=None)
    parser.add_argument("--custom-fields-file", metavar="FILE",
                        help="JSON file containing component vulnerability custom field attributes")
    parser.add_argument("--output", choices=['table', 'json'], default='table',
                        help="Output format (default: table)")


def create_parser():
    """
    Create and configure the main argument parser.

    Returns:
        argparse.ArgumentParser: Configured parser
    """
    main_epilog = '''
Examples:
  pylynk prods                                    List all products
  pylynk vers --prod 'my-product'                 List versions for a product
  pylynk upload --prod 'my-product' --sbom s.json Upload an SBOM
  pylynk download --verId 'abc-123'               Download an SBOM
  pylynk gate --prod 'p' --env 'default' --ver 'v1.0'  Policy gate for CI (exit 3 on failure)
  pylynk vulns --prod 'my-product'                List vulnerabilities
  pylynk vex update --prod 'p' --ver 'v1.0' --vuln CVE-2024-1234 --status not_affected
  pylynk report --type attribution --prod 'p' --env 'default' --ver 'v1.0'

Environment Variables:
  INTERLYNK_SECURITY_TOKEN    Authentication token (required)
  INTERLYNK_API_URL           API endpoint (optional)

For detailed help on a command: pylynk <command> --help
Documentation: https://github.com/interlynk-io/pylynk
'''

    parser = CustomArgumentParser(
        description='pylynk - Command line tool for the Interlynk SBOM platform',
        epilog=main_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='Increase output verbosity (use -vv for more)')

    subparsers = parser.add_subparsers(title="commands", dest="subcommand",
                                       metavar='<command>')

    # Products command
    prods_epilog = '''
Examples:
  pylynk prods                     List products in table format
  pylynk prods --output json       List products in JSON format
  pylynk prods --output csv        List products in CSV format
  pylynk prods --human-time        Show timestamps as '2 days ago'
'''
    products_parser = subparsers.add_parser(
        "prods",
        help="List products",
        description="List all products in your Interlynk organization.",
        epilog=prods_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    add_output_format_group(products_parser)
    add_human_time_argument(products_parser)

    # Versions command
    vers_epilog = '''
Examples:
  pylynk vers --prod 'my-product'                   List versions (default env)
  pylynk vers --prod 'my-product' --env 'prod'      List versions for environment
  pylynk vers --prod 'my-product' --output json     Output as JSON
  pylynk vers --prod 'my-product' --human-time      Show relative timestamps
'''
    vers_parser = subparsers.add_parser(
        "vers",
        help="List versions for a product",
        description="List all SBOM versions for a specific product.",
        epilog=vers_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    add_product_arguments(vers_parser)
    add_environment_argument(vers_parser)
    add_output_format_group(vers_parser)
    add_human_time_argument(vers_parser)

    # Status command
    status_epilog = '''
Examples:
  pylynk status --prod 'my-product' --verId 'abc-123'
  pylynk status --prod 'my-product' --ver 'v1.0.0' --env 'production'
  pylynk status --prod 'my-product' --verId 'abc-123' --output json

Note: Requires either --verId OR both --ver and --env
'''
    status_parser = subparsers.add_parser(
        "status",
        help="Check SBOM processing status",
        description="Check the processing status of a specific SBOM version.",
        epilog=status_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    add_product_arguments(status_parser)
    add_environment_argument(status_parser)
    add_version_arguments(status_parser, required=False)
    add_output_format_group(status_parser, include_csv=False)

    # Upload command
    upload_epilog = '''
Examples:
  pylynk upload --prod 'my-product' --sbom sbom.json
  pylynk upload --prod 'my-product' --env 'production' --sbom sbom.json
  pylynk upload --prod 'my-product' --sbom sbom.json --retries 5

Supported SBOM formats: CycloneDX (JSON/XML), SPDX (JSON/tag-value)
'''
    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload an SBOM",
        description="Upload an SBOM file to the Interlynk platform.",
        epilog=upload_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    add_product_arguments(upload_parser)
    add_environment_argument(upload_parser)
    upload_parser.add_argument("--sbom", required=True, metavar='FILE',
                               help="Path to SBOM file")
    upload_parser.add_argument("--retries", type=int, default=3, metavar='N',
                               help="Number of upload retries (default: 3)")

    # Download command
    download_epilog = '''
Examples:
  pylynk download --prod 'my-product' --env 'default' --ver 'v1.0.0'
  pylynk download --prod 'my-product' --env 'default' --ver 'v1.0.0' --out-file sbom.json
  pylynk download --prod 'my-product' --env 'default' --ver 'v1.0.0' --vuln true
  pylynk download --prod 'my-product' --env 'default' --ver 'v1.0.0' --spec CycloneDX --spec-version 1.5
  pylynk download --prod 'my-product' --env 'default' --ver 'v1.0.0' --wait-for vuln-scan
  pylynk download --prod 'my-product' --env 'default' --ver 'v1.0.0' --wait-for vuln-scan,automation --poll-interval 15
  pylynk download --verId 'abc-123' --out-file sbom.json

Note: Requires either --verId OR all of --prod, --env, and --ver
'''
    download_parser = subparsers.add_parser(
        "download",
        help="Download an SBOM",
        description="Download an SBOM from the Interlynk platform.",
        epilog=download_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    add_product_arguments(download_parser, required=False)
    add_environment_argument(download_parser)
    add_version_arguments(download_parser, required=False)
    download_parser.add_argument("--out-file", "--output", dest="out_file",
                                 metavar='FILE', help="Output file path")
    download_parser.add_argument("--vuln", metavar='BOOL',
                                 help="Include vulnerabilities (true/false)")
    download_parser.add_argument("--spec", choices=['SPDX', 'CycloneDX'],
                                 help="SBOM specification format")
    download_parser.add_argument("--spec-version", metavar='VER',
                                 help="SBOM specification version (e.g., 2.3, 1.5)")
    download_parser.add_argument("--lite", action="store_true",
                                 help="Download lite SBOM (reduced metadata)")
    download_parser.add_argument("--dont-package-sbom", action="store_true",
                                 help="Don't package into single file")
    download_parser.add_argument("--original", action="store_true",
                                 help="Download original uploaded SBOM")
    download_parser.add_argument("--exclude-parts", action="store_true",
                                 help="Exclude parts from SBOM")
    download_parser.add_argument("--include-support-status", action="store_true",
                                 help="Include support status")
    download_parser.add_argument("--wait-for", metavar='STAGES',
                                 help="Wait for processing stages before download "
                                      "(comma-separated: automation,vuln-scan,policy-scan)")
    download_parser.add_argument("--poll-interval", type=int, default=10, metavar='SECS',
                                 help="Seconds between polling attempts when using --wait-for (default: 10)")
    download_parser.add_argument("--poll-timeout", type=int, default=300, metavar='SECS',
                                 help="Maximum seconds to wait for processing (default: 300)")

    # Gate command
    gate_epilog = f'''
Examples:
{_get_command_examples('gate')}

Exit codes:
  0  gate passed (or no active policies configured)
  1  operational error (auth, network, resolution, or missing --verId/--prod --ver)
  2  arguments rejected by the parser
  3  policy gate FAILED - blocking violations detected
  4  indeterminate - scan timed out, errored, or was never evaluated

Note: Requires either --verId OR both --prod and --ver (an explicit version;
the latest-version fallback is disabled because it is racy in CI).
'''
    gate_parser = subparsers.add_parser(
        "gate",
        help="Check the policy gate for an SBOM (CI/PR blocking)",
        description="Check whether an SBOM version passes the organization's "
                    "policies. Waits for the policy scan to finish and exits "
                    "non-zero on failure so CI can block the PR.",
        epilog=gate_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    add_product_arguments(gate_parser, required=False)
    add_environment_argument(gate_parser)
    add_version_arguments(gate_parser, required=False)
    gate_parser.add_argument("--fail-on", choices=['fail', 'warn'], default='fail',
                             help="Lowest policy severity that blocks (default: fail)")
    policy_filter_group = gate_parser.add_mutually_exclusive_group()
    policy_filter_group.add_argument("--policy-name",
                                     help="Gate on a single active policy by exact name")
    policy_filter_group.add_argument("--policy-id",
                                     help="Gate on a single active policy by ID")
    gate_parser.add_argument("--no-wait", action='store_false', dest='wait',
                             help="Check current state once instead of waiting "
                                  "for the policy scan to finish")
    gate_parser.add_argument("--timeout", type=int, default=DEFAULT_GATE_TIMEOUT, metavar='SECS',
                             help="Total seconds to wait for resolution and policy scan "
                                  f"(default: {DEFAULT_GATE_TIMEOUT})")
    gate_parser.add_argument("--poll-interval", type=int, default=DEFAULT_GATE_POLL_INTERVAL, metavar='SECS',
                             help="Seconds between polling attempts "
                                  f"(default: {DEFAULT_GATE_POLL_INTERVAL})")
    add_output_format_group(gate_parser, include_csv=False)

    # Version command
    version_parser = subparsers.add_parser(
        "version",
        help="Show version information",
        description="Display pylynk version information."
    )

    # Vulns command
    vulns_epilog = '''
Examples:
  pylynk vulns --prod 'my-product'
  pylynk vulns --prod 'my-product' --env 'production'
  pylynk vulns --prod 'my-product' --vuln-details
  pylynk vulns --prod 'my-product' --vex-details
  pylynk vulns --prod 'my-product' --output csv > vulns.csv
  pylynk vulns --prod 'my-product' --columns 'id,severity,cvss,status'
  pylynk vulns --list-columns

Column Groups:
  --vuln-details       Add: severity, kev, cvss, cvss_vector, epss, cwe
  --vex-details        Add: status, details, justification, action_statement
  --timestamp-details  Add: assigned, published, last_modified, updated
'''
    vulns_parser = subparsers.add_parser(
        "vulns",
        help="List vulnerabilities",
        description="List vulnerabilities for a product/environment.",
        epilog=vulns_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    add_product_arguments(vulns_parser, required=False)
    add_environment_argument(vulns_parser)
    add_version_arguments(vulns_parser, required=False)
    vulns_parser.add_argument("--vuln-details", action='store_true',
                              help="Include vulnerability metadata columns")
    vulns_parser.add_argument("--vex-details", action='store_true',
                              help="Include VEX information columns")
    vulns_parser.add_argument("--timestamp-details", action='store_true',
                              help="Include all timestamp columns")
    vulns_parser.add_argument("--columns", metavar='COLS',
                              help="Comma-separated list of columns")
    vulns_parser.add_argument("--list-columns", action='store_true',
                              help="List available column names and exit")
    add_output_format_group(vulns_parser)
    add_human_time_argument(vulns_parser)

    # VEX command
    vex_epilog = '''
Examples:
  pylynk vex update --prod 'my-product' --ver 'v1.0.0' --vuln CVE-2024-1234 --component lodash --status not_affected
  pylynk vex update --verId 'abc-123' --component-vuln-id 'def-456' --status-id 'status-uuid'
  pylynk vex bulk-update --prod 'my-product' --ver 'v1.0.0' --file vex-updates.csv
  pylynk vex bulk-update --verId 'abc-123' --component-vuln-id 'def-456' --component-vuln-id 'ghi-789' --status affected

CSV files may use component_vuln_id directly, or vuln/component/component_version names.
'''
    vex_parser = subparsers.add_parser(
        "vex",
        help="Update VEX data",
        description="Update VEX data for component vulnerabilities.",
        epilog=vex_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    vex_subparsers = vex_parser.add_subparsers(title="actions", dest="vex_action",
                                               metavar='<action>')
    vex_subparsers.required = True

    vex_update_parser = vex_subparsers.add_parser(
        "update",
        help="Update VEX data for one component vulnerability",
        description="Update VEX data for one component vulnerability.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    add_vex_target_arguments(vex_update_parser)
    component_group = vex_update_parser.add_mutually_exclusive_group(required=True)
    component_group.add_argument("--component-vuln-id", help="Component vulnerability ID")
    component_group.add_argument("--vuln", dest="vuln_id", help="CVE or vulnerability ID")
    vex_update_parser.add_argument("--component", help="Component name")
    vex_update_parser.add_argument("--component-version", help="Component version")
    add_vex_payload_arguments(vex_update_parser)

    vex_bulk_parser = vex_subparsers.add_parser(
        "bulk-update",
        help="Update VEX data for multiple component vulnerabilities",
        description="Update VEX data for multiple component vulnerabilities.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    add_vex_target_arguments(vex_bulk_parser)
    bulk_component_group = vex_bulk_parser.add_mutually_exclusive_group(required=True)
    bulk_component_group.add_argument("--file", metavar="FILE",
                                      help="CSV or JSON file with VEX updates")
    bulk_component_group.add_argument("--component-vuln-id", dest="component_vuln_ids",
                                      action="append", help="Component vulnerability ID; may be repeated")
    vex_bulk_parser.add_argument("--component", help="Component name for CLI-provided vulnerability")
    vex_bulk_parser.add_argument("--component-version", help="Component version for CLI-provided vulnerability")
    vex_bulk_parser.add_argument("--vuln", dest="vuln_id", help="CVE or vulnerability ID for CLI-provided update")
    add_vex_payload_arguments(vex_bulk_parser)

    # Report command
    report_epilog = '''
Examples:
  pylynk report --type attribution --prod 'my-product' --env 'production' --ver 'v1.0.0'
  pylynk report --type attribution --prod 'my-product' --env 'default' --ver 'v1.0.0' --include-license-text
  pylynk report --type attribution --prod 'my-product' --env 'default' --ver 'v1.0.0' --output-file report.csv

Note: If --ver is omitted, the latest version is used automatically.
'''
    report_parser = subparsers.add_parser(
        "report",
        help="Generate reports",
        description="Generate reports from the Interlynk platform.",
        epilog=report_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_create_base_parser()]
    )
    report_parser.add_argument("--type", required=True, choices=['attribution'],
                               dest="report_type",
                               help="Report type to generate")
    add_product_arguments(report_parser, required=True)
    add_environment_argument(report_parser)
    add_version_arguments(report_parser, required=False)
    report_parser.add_argument("--include-license-text", action='store_true',
                               help="Include full license text in output")
    report_parser.add_argument("--output-file", metavar='FILE',
                               help="Output file path (default: attribution_<product>.csv)")

    return parser


def _create_base_parser():
    """Create a base parser with common arguments for inheritance."""
    base = argparse.ArgumentParser(add_help=False)
    base.add_argument("--token", metavar='TOKEN',
                      help="Security token (or set INTERLYNK_SECURITY_TOKEN)")
    return base
