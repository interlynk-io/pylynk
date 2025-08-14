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

"""Version command implementation."""

import subprocess
import os


def get_version():
    """
    Get the version of pylynk.
    
    Returns the version based on:
    1. Git tag if on a tagged commit
    2. Git commit hash if in a git repo
    3. "dirty" suffix if there are uncommitted changes
    4. "unknown" if git is not available
    """
    try:
        # Get the directory where this file is located
        file_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to the root of the project
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(file_dir)))
        
        # Check if we're on a tagged commit
        try:
            tag = subprocess.check_output(
                ["git", "describe", "--exact-match", "--tags"],
                cwd=project_root,
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            if tag:
                # Check if working directory is clean
                status = subprocess.check_output(
                    ["git", "status", "--porcelain"],
                    cwd=project_root,
                    text=True
                ).strip()
                if status:
                    return f"{tag}-dirty"
                return tag
        except subprocess.CalledProcessError:
            # Not on a tagged commit
            pass
        
        # Get the current commit hash
        try:
            commit = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=project_root,
                text=True
            ).strip()
            
            # Check if working directory is clean
            status = subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=project_root,
                text=True
            ).strip()
            
            if status:
                return f"{commit}-dirty"
            return commit
            
        except subprocess.CalledProcessError:
            return "unknown"
            
    except Exception:
        return "unknown"


def execute(api_client, config):
    """
    Execute the version command.
    
    Args:
        api_client: API client instance (not used for version command)
        config: Configuration instance (not used for version command)
    
    Returns:
        int: Exit code (0 for success)
    """
    version = get_version()
    print(f"pylynk version: {version}")
    return 0