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

"""GraphQL queries for PyLynk API."""

# Query to get the total count of products
PRODUCTS_TOTAL_COUNT = """
query GetProductsCount($name: String, $enabled: Boolean) {
  organization {
    productNodes: projectGroups(
      search: $name
      enabled: $enabled
      orderBy: { field: PROJECT_GROUPS_UPDATED_AT, direction: DESC }
    ) {
      prodCount: totalCount
    }
  }
}
"""

# Query to get the list of products with details
PRODUCTS_LIST = """
query GetProducts($first: Int) {
  organization {
    productNodes: projectGroups(
      enabled: true
      first: $first
      orderBy: { field: PROJECT_GROUPS_UPDATED_AT, direction: DESC }
    ) {
      prodCount: totalCount
      products: nodes {
        id
        name
        updatedAt
        enabled
        environments: projects {
          id: id
          name: name
          versions: sboms {
            id
            vulnRunStatus
            updatedAt
            primaryComponent {
              name
              version
            }
          }
        }
      }
    }
  }
}
"""

# Query to download an SBOM (current server format)
SBOM_DOWNLOAD = """
query downloadSbom($projectId: Uuid!, $sbomId: Uuid!, $includeVulns: Boolean, 
                   $spec: String, $original: Boolean, $package: Boolean, 
                   $lite: Boolean, $excludeParts: Boolean, 
                   $supportLevelOnly: Boolean, $includeSupportStatus: Boolean) {
  sbom(projectId: $projectId, sbomId: $sbomId) {
    download(
      sbomId: $sbomId
      includeVulns: $includeVulns
      spec: $spec
      original: $original
      dontPackageSbom: $package
      lite: $lite
      excludeParts: $excludeParts
      supportLevelOnly: $supportLevelOnly
      includeSupportStatus: $includeSupportStatus
    ) {
      content
      contentType
      filename
    }
  }
}
"""

# Query to download an SBOM (future format with sbomDownload resolver)
SBOM_DOWNLOAD_NEW = """
query downloadSbom($projectId: Uuid, $sbomId: Uuid, $projectName: String,
                   $projectGroupName: String, $versionName: String,
                   $includeVulns: Boolean, $spec: SbomSpec, $original: Boolean, 
                   $package: Boolean, $lite: Boolean, $excludeParts: Boolean, 
                   $supportLevelOnly: Boolean, $includeSupportStatus: Boolean) {
  sbom(projectId: $projectId, sbomId: $sbomId, projectName: $projectName, 
       projectGroupName: $projectGroupName, versionName: $versionName) {
    download(
      sbomId: $sbomId
      includeVulns: $includeVulns
      spec: $spec
      original: $original
      dontPackageSbom: $package
      lite: $lite
      excludeParts: $excludeParts
      supportLevelOnly: $supportLevelOnly
      includeSupportStatus: $includeSupportStatus
    ) {
      content
      contentType
      filename
      __typename
    }
    __typename
  }
}
"""

# Query to get a specific product by ID
PRODUCT_BY_ID = """
query GetProductById($id: ID!) {
  organization {
    productNodes: projectGroups(
      ids: [$id]
      enabled: true
      first: 1
    ) {
      products: nodes {
        id
        name
        environments: projects {
          id
          name
        }
      }
    }
  }
}
"""