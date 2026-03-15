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

"""Main entry point for PyLynk CLI."""

import sys
import os

# Add the parent directory to sys.path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pylynk.cli.parser import create_parser
from pylynk.utils.config import Config
from pylynk.api.client import LynkAPIClient
from pylynk.cli.commands import products, versions, status, upload, download, version, vulns, report


def main():
    """Main function that serves as the entry point of the program."""
    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Create configuration
    config = Config(args)
    
    # Create API client
    api_client = LynkAPIClient(config)
    
    # Version command doesn't need API initialization
    if args.subcommand == "version":
        from pylynk.cli.commands import version
        return version.execute(None, None)

    # Vulns --list-columns doesn't need API initialization
    if args.subcommand == "vulns" and getattr(config, 'list_columns', False):
        return vulns.execute(None, config)
    
    # Only 'prods' needs full initialization (fetches all products)
    # All other commands use minimal init + targeted queries
    if args.subcommand == "prods":
        if not api_client.initialize():
            return 1
    else:
        if not api_client.initialize_minimal():
            return 1

    # Validate download parameters early
    if args.subcommand == "download":
        has_id_params = bool(config.ver_id)
        has_name_params = all([config.prod, config.env, config.ver])

        if not has_id_params and not has_name_params:
            print("Error: Missing required parameters for download")
            print()
            print("Please provide either:")
            print("  --verId <version-id>")
            print("    OR")
            print("  --prod <product> --env <environment> --ver <version>")
            print()
            print("Examples:")
            print("  pylynk download --verId 'abc-123-def'")
            print("  pylynk download --prod 'my-product' --env 'default' --ver 'v1.0.0'")
            print()
            print("For more information: pylynk download --help")
            return 1
    
    # Execute the appropriate command
    exit_code = 0
    
    if args.subcommand == "prods":
        exit_code = products.execute(api_client, config)
    elif args.subcommand == "vers":
        exit_code = versions.execute(api_client, config)
    elif args.subcommand == "status":
        exit_code = status.execute(api_client, config)
    elif args.subcommand == "upload":
        exit_code = upload.execute(api_client, config, args.sbom)
    elif args.subcommand == "download":
        exit_code = download.execute(api_client, config)
    elif args.subcommand == "vulns":
        exit_code = vulns.execute(api_client, config)
    elif args.subcommand == "report":
        exit_code = report.execute(api_client, config)
    else:
        print("Error: No command specified")
        print()
        print("Available commands:")
        print("  prods      List products")
        print("  vers       List versions for a product")
        print("  status     Check SBOM processing status")
        print("  upload     Upload an SBOM")
        print("  download   Download an SBOM")
        print("  vulns      List vulnerabilities")
        print("  report     Generate reports")
        print("  version    Show version information")
        print()
        print("For help: pylynk --help")
        print("For command help: pylynk <command> --help")
        exit_code = 1
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())