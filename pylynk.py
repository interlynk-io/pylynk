import os
import sys
import json
import requests
import argparse
from gql.transport.aiohttp import AIOHTTPTransport


url_local = 'http://localhost:3000/lynkapi'

projects_query = """
query GetOrganization {
  organization {
    email
    id
    name
    updatedAt
    url
    currentUser {
      id
      name
      email
      __typename
    }
    users {
      id
      name
      email
      role
      timezone
      createdAt
      __typename
    }
    organizationConnectors {
      enabled
      name
      __typename
    }
    __typename
  }
}
"""

headers_local = {
    'Authentication': 'Bearer TBD',
    'User-Agent': 'TBD'
}

data_local = {
    'operationName': 'GetOrganization',
    'variables': {},
    'query': projects_query
    }


def fetch(url, headers, data):
    transport = AIOHTTPTransport(url)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    result = client.execute(projects_query)
    print(result)
    return


def upload(file, project, token):
    if os.path.isfile(file) is False:
        print('SBOM File not found')
        return

    url = "http://localhost:3000/lynkapi"
    headers = {
        "Authorization": "Bearer " + token
    }

    operations =json.dumps({
        "query": "mutation uploadSbom($doc: Upload!, $projectId: ID!) { sbomUpload(input: { doc: $doc, projectId: $projectId }) { errors } }",
        "variables": {"doc": None, "projectId": project}
    })
    map_data = json.dumps({"0": ["variables.doc"]})

    form_data = {
        "operations": operations,
        "map": map_data
    }
    myfiles = {'0': open(file ,'rb')}

    response = requests.post(url, headers=headers, data=form_data, files=myfiles)
    print(response.text)


def setup_args():
    """
    Setup command line arguments
    :return: arguments object
    """
    parser = argparse.ArgumentParser(description='Interlynk Python CLI')

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    upload_parser = subparsers.add_parser("upload", help="Upload an SBOM")
    upload_parser.add_argument("--sbom", required=True, help="SBOM path")
    upload_parser.add_argument("--proj", required=True, help="Project name")
    upload_parser.add_argument("--token", required=False, help="Security token")

    projects_parser = subparsers.add_parser("projects", help="List projects")
    projects_parser.add_argument("--token", required=False, help="Security token")

    args = parser.parse_args()
    return args


def main() -> int:
    """
    Run Interlynk Commands
    """
    args = setup_args()

    if args.subcommand == "upload":
        upload(args.sbom, args.proj, args.token)
    # elif args.subcommand == "projects":
    #    print('fetching')
    #    fetch(url_local, headers_local, data_local)
    else:
        print("Invalid command. Use 'upload' or 'projects'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
