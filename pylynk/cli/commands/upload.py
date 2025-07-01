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

"""Upload command implementation."""


def execute(api_client, config, sbom_file):
    """
    Execute the upload command.
    
    Args:
        api_client: Initialized API client
        config: Configuration object
        sbom_file (str): Path to SBOM file to upload
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Check if we have at least a product identifier
    if not config.prod:
        print("Error: Product name (--prod) is required")
        return 1
    
    # Upload will use whatever identifiers are available
    return api_client.upload_sbom(sbom_file)