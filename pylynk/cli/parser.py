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


def add_output_format_group(parser):
    """
    Add mutually exclusive output format arguments to a parser.
    
    Args:
        parser: Argument parser or subparser
    """
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json", action='store_true', help="JSON Formatted (default)")
    output_group.add_argument(
        "--table", action='store_true', help="Table Formatted")


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
    parser = argparse.ArgumentParser(description='Interlynk command line tool')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    
    # Products command
    products_parser = subparsers.add_parser("prods", help="List products")
    add_common_arguments(products_parser)
    add_output_format_group(products_parser)
    
    # Versions command
    vers_parser = subparsers.add_parser("vers", help="List Versions")
    add_product_arguments(vers_parser)
    vers_parser.add_argument("--env", help="Environment", required=False)
    add_common_arguments(vers_parser)
    add_output_format_group(vers_parser)
    
    # Status command
    status_parser = subparsers.add_parser("status", help="SBOM Status")
    add_product_arguments(status_parser)
    add_version_arguments(status_parser)
    status_parser.add_argument("--env", help="Environment", required=False)
    add_common_arguments(status_parser)
    add_output_format_group(status_parser)
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload SBOM")
    add_product_arguments(upload_parser)
    upload_parser.add_argument("--env", help="Environment", required=False)
    upload_parser.add_argument("--sbom", required=True, help="SBOM path")
    upload_parser.add_argument("--retries", type=int, default=3, help="Number of upload retries (default: 3)")
    add_common_arguments(upload_parser)
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download SBOM")
    add_product_arguments(download_parser, required=False)
    add_version_arguments(download_parser, required=False)
    download_parser.add_argument("--env", help="Environment", required=False)
    download_parser.add_argument("--output", help="Output file", required=False)
    download_parser.add_argument("--vuln", help="Include vulnerabilities", required=False)
    download_parser.add_argument("--spec", help="SBOM specification (SPDX or CycloneDX)", 
                                  choices=['SPDX', 'CycloneDX'], required=False)
    download_parser.add_argument("--spec-version", help="SBOM specification version", required=False)
    download_parser.add_argument("--lite", help="Download lite SBOM", action="store_true", required=False)
    download_parser.add_argument("--dont-package-sbom", help="Don't package SBOM", action="store_true", required=False)
    download_parser.add_argument("--original", help="Download original SBOM", action="store_true", required=False)
    download_parser.add_argument("--exclude-parts", help="Exclude parts from SBOM", action="store_true", required=False)
    download_parser.add_argument("--include-support-status", help="Include support status", action="store_true", required=False)
    add_common_arguments(download_parser)
    
    return parser