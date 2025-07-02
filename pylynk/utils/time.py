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

"""Time utilities for PyLynk CLI."""

import datetime
import time
import pytz


def user_time(utc_time):
    """
    Convert UTC time to local time and format it as a string.

    Args:
        utc_time (str): The UTC time in ISO format.

    Returns:
        str: The local time formatted as a string.
    """
    # Parse the input UTC time
    timestamp = datetime.datetime.fromisoformat(utc_time[:-1])

    # Get the local timezone
    local_timezone = datetime.timezone(
        datetime.timedelta(seconds=-time.timezone))

    # Convert the UTC time to local time
    local_time = timestamp.replace(tzinfo=pytz.UTC).astimezone(local_timezone)

    # Format and return the local time as a string
    return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')
