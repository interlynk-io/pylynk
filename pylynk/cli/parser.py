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

        'vulns': '''  pylynk vulns --prod 'my-product'
  pylynk vulns --prod 'my-product' --env 'production'
  pylynk vulns --prod 'my-product' --vuln-details --vex-details
  pylynk vulns --list-columns''',

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
    parser.add_argument("--human-time", action='store_true',
                        help="Show timestamps in human-friendly format (e.g., '2 days ago')")


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
  pylynk vulns --prod 'my-product'                List vulnerabilities
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
