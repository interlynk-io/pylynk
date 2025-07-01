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

"""CSV formatter for PyLynk CLI output."""


def format_csv(content, output_file=None):
    """
    Format and output CSV content.
    
    Args:
        content (str): CSV content to output
        output_file (str): Optional output file path
    """
    if output_file:
        with open(output_file, 'w') as f:
            f.write(content)
    else:
        print(content)