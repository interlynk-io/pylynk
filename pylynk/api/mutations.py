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

"""GraphQL mutations for PyLynk API."""

# Mutation to upload an SBOM
SBOM_UPLOAD = """
mutation uploadSbom(
  $doc: Upload!, 
  $projectId: ID, 
  $projectName: String, 
  $projectGroupName: String, 
  $projectGroupId: ID
) {
  sbomUpload(
    input: {
      doc: $doc,
      projectId: $projectId,
      projectName: $projectName,
      projectGroupName: $projectGroupName,
      projectGroupId: $projectGroupId
    }
  ) {
    errors
  }
}
"""


COMPONENT_VEX_UPDATE = """
mutation UpdateCompVulnVex(
  $compVulnId: Uuid!,
  $vexStatusId: Uuid,
  $sbomId: Uuid!,
  $propagateVex: Boolean,
  $vexJustificationId: Uuid,
  $cdxResponseId: Uuid,
  $note: String,
  $impact: String,
  $detail: String,
  $action: String,
  $fixedIn: String,
  $componentVulnCustomFieldAttributes: [ComponentVulnCustomFieldAttributesInput!]
) {
  componentVexUpdate(
    input: {
      componentVulnId: $compVulnId,
      vexStatusId: $vexStatusId,
      currentSbomId: $sbomId,
      propagateVex: $propagateVex,
      vexJustificationId: $vexJustificationId,
      cdxResponseId: $cdxResponseId,
      note: $note,
      impact: $impact,
      detail: $detail,
      action: $action,
      fixedIn: $fixedIn,
      componentVulnCustomFieldAttributes: $componentVulnCustomFieldAttributes
    }
  ) {
    componentVuln {
      id
      vexJustification {
        id
        name
      }
      vexStatus {
        id
        name
      }
      cdxResponse {
        id
        name
      }
      note
      impact
      detail
      actionStmt
      fixedIn
    }
    errors
  }
}
"""


COMPONENT_VEX_BULK_UPDATE = """
mutation UpdateBulkCompVex(
  $comVulnIds: [Uuid!]!,
  $vexStatusId: Uuid!,
  $sbomId: Uuid,
  $propagateVex: Boolean,
  $vexJustificationId: Uuid,
  $cdxResponseId: Uuid,
  $note: String,
  $impact: String,
  $detail: String,
  $action: String,
  $fixedIn: String,
  $componentVulnCustomFieldAttributes: [ComponentVulnCustomFieldAttributesInput!]
) {
  componentVexBulkUpdate(
    input: {
      componentVulnIds: $comVulnIds,
      vexStatusId: $vexStatusId,
      currentSbomId: $sbomId,
      propagateVex: $propagateVex,
      vexJustificationId: $vexJustificationId,
      cdxResponseId: $cdxResponseId,
      note: $note,
      impact: $impact,
      detail: $detail,
      action: $action,
      fixedIn: $fixedIn,
      componentVulnCustomFieldAttributes: $componentVulnCustomFieldAttributes
    }
  ) {
    clientMutationId
    errors
    componentVulns {
      id
      vulnId
    }
  }
}
"""
