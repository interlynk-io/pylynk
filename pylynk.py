# Copyright 2023 Interlynk.io
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

import os
import argparse
import logging
import datetime
import pytz
import tzlocal
import sys
from lynkctx import LynkContext


def user_time(utc_time):
    timestamp = datetime.datetime.fromisoformat(utc_time[:-1])
    local_timezone = tzlocal.get_localzone()
    local_time = timestamp.replace(tzinfo=pytz.UTC).astimezone(local_timezone)
    return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')


def print_products(lynk_ctx):
    products = lynk_ctx.prods()

    # Calculate dynamic column widths
    name_width = max(len("NAME"), max(len(prod['name'])
                                       for prod in products))
    updated_at_width = max(len("UPDATED AT"),
                           max(len(user_time(prod['updatedAt']))
                               for prod in products))
    id_width = max(len("ID"), max(len(prod['id']) for prod in products))
    version_width = len("VERSIONS")

    header = (
        f"{ 'NAME':<{name_width}} | "
        f"{ 'ID':<{id_width}} | "
        f"{ 'VERSIONS':<{version_width}} | "
        f"{ 'UPDATED AT':<{updated_at_width}} | "
    )
    print(header)

    # Add a horizontal line after the header
    # 10 is the total length of separators and spaces
    width = sum([name_width, version_width, updated_at_width, id_width]) + 10
    line = "-" * width + "|"
    print(line)

    for prod in products:
        row = (
            f"{prod['name']:<{name_width}} | "
            f"{prod['id']:<{id_width}} | "
            f"{prod['versions']:<{version_width}} | "
            f"{user_time(prod['updatedAt']):<{updated_at_width}} | "
        )
        print(row)
    return 0


def print_versions(lynk_ctx):
    versions = lynk_ctx.versions()
    if not versions:
        print('No versions found')
        return 0

    # Calculate dynamic column widths
    id_width = max(len('ID'), max(len(sbom['id'])
                                  for sbom in versions))
    version_width = max(len('VERSION'),
                        max(len(s.get('primaryComponent', {})
                                .get('version', ''))
                        for s in versions))
    primary_component_width = max(len('PRIMARY COMPONENT'),
                                  max(len(sbom.get('primaryComponent', {})
                                          .get('name', ''))
                                      for sbom in versions))
    updated_at_width = max(len('UPDATED AT'),
                           max(len(user_time(sbom['updatedAt']))
                               for sbom in versions))

    # Format the header with dynamic column widths
    header = (
        f"{'ID':<{id_width}} | "
        f"{'VERSION':<{version_width}} | "
        f"{'PRIMARY COMPONENT':<{primary_component_width}} | "
        f"{'UPDATED AT':<{updated_at_width}} |"
    )
    print(header)

    # Add a horizontal line after the header
    # 12 is the total length of separators and spaces
    width = sum([id_width, version_width,
                 primary_component_width,
                 updated_at_width]) + 10
    line = "-" * width + "|"
    print(line)

    # Format each row with dynamic column widths and a bar between elements
    for sbom in versions:
        if sbom.get('primaryComponent') is None:
            continue
        version = sbom.get('primaryComponent', {}).get('version', '')
        primary_component = sbom.get('primaryComponent', {}).get('name', '')
        row = (
            f"{sbom['id']:<{id_width}} | "
            f"{version:<{version_width}} | "
            f"{primary_component:<{primary_component_width}} | "
            f"{user_time(sbom['updatedAt']):<{updated_at_width}} |"
        )
        print(row)

    return 0

def download_sbom(lynk_ctx):
    sbom = lynk_ctx.download()
    if sbom is None:
        print('Failed to fetch SBOM')
        return 1

    #print(sbom.encode("utf-8"))
    #print(sbom.encode('utf-8', errors='ignore').decode('utf-8'))
    sys.stdout.buffer.write(sbom.encode("utf-8", errors='ignore'))
    return 0

def upload_sbom(lynk_ctx, sbom_file):
    return lynk_ctx.upload(sbom_file)
    
def setup_args():
    parser = argparse.ArgumentParser(description='Interlynk command line tool')
    parser.add_argument('--verbose', '-v', action='count', default=0)

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    products_parser = subparsers.add_parser("prods", help="List products")
    products_parser.add_argument("--token",
                                 required=False,
                                 help="Security token")

    vers_parser = subparsers.add_parser("vers", help="List Versions")
    vers_group = vers_parser.add_mutually_exclusive_group(required=True)

    vers_group.add_argument("--prod", help="Product name")
    vers_group.add_argument("--prodId", help="Product ID")

    vers_parser.add_argument("--env", help="Environment", required=False)
    vers_parser.add_argument("--token",
                             required=False,
                             help="Security token")

    upload_parser = subparsers.add_parser("upload", help="Upload SBOM")
    upload_group = upload_parser.add_mutually_exclusive_group(required=True)
    upload_group.add_argument("--prod", help="Product name")
    upload_group.add_argument("--prodId", help="Product ID")

    upload_parser.add_argument("--env", help="Environment", required=False)
    upload_parser.add_argument("--sbom", required=True, help="SBOM path")
    upload_parser.add_argument("--token",
                               required=False,
                               help="Security token")

    download_parser = subparsers.add_parser("download", help="Download SBOM")
    download_group = download_parser.add_mutually_exclusive_group(required=True)
    download_group.add_argument("--prod", help="Product name")
    download_group.add_argument("--prodId", help="Product ID")

    download_group = download_parser.add_mutually_exclusive_group(required=True)
    download_group.add_argument("--ver", help="Version")
    download_group.add_argument("--verId", help="Version ID")

    download_parser.add_argument("--env", help="Environment", required=False)
    download_parser.add_argument("--token",
                                 required=False,
                                 help="Security token")


    args = parser.parse_args()
    return args


def setup_log_level(args):
    if args.verbose == 0:
        logging.basicConfig(level=logging.ERROR)
    logging.basicConfig(level=logging.DEBUG)

def setup_lynk_context(args):
    return LynkContext(
        os.environ.get('INTERLYNK_API_URL'),
        getattr(args, 'token', None) or os.environ.get('INTERLYNK_SECURITY_TOKEN'),
        getattr(args, 'prodId', None),
        getattr(args, 'prod', None),
        getattr(args, 'envId', None),
        getattr(args, 'env', None),
        getattr(args, 'verId', None),
        getattr(args, 'ver', None)
    )
    
def main() -> int:
    args = setup_args()
    setup_log_level(args)
    lynk_ctx = setup_lynk_context(args)
    if not lynk_ctx.validate():
        exit(1)

    if args.subcommand == "prods":
        print_products(lynk_ctx)
    elif args.subcommand == "vers":            
        print_versions(lynk_ctx)
    elif args.subcommand == "upload":
        upload_sbom(lynk_ctx, args.sbom)
    elif args.subcommand == "download":
        download_sbom(lynk_ctx)
    else:
      print("Missing or invalid command. \
            Supported commands: {prods, upload, download, sign, verify}")
      exit(1)
    exit(0)

if __name__ == "__main__":
    main()
