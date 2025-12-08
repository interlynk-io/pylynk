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


def human_time(utc_time):
    """
    Convert UTC time to a human-friendly relative time string.

    Args:
        utc_time (str): The UTC time in ISO format.

    Returns:
        str: Human-friendly time string (e.g., '2 days ago', 'in 3 hours')
    """
    if not utc_time:
        return ''

    try:
        # Parse the input UTC time
        if utc_time.endswith('Z'):
            timestamp = datetime.datetime.fromisoformat(utc_time[:-1])
        else:
            timestamp = datetime.datetime.fromisoformat(utc_time.replace('Z', ''))

        timestamp = timestamp.replace(tzinfo=pytz.UTC)
        now = datetime.datetime.now(pytz.UTC)

        diff = now - timestamp

        # Calculate the difference
        seconds = diff.total_seconds()
        is_future = seconds < 0
        seconds = abs(seconds)

        # Define time intervals
        intervals = [
            (31536000, 'year'),    # 365 days
            (2592000, 'month'),    # 30 days
            (604800, 'week'),      # 7 days
            (86400, 'day'),        # 1 day
            (3600, 'hour'),        # 1 hour
            (60, 'minute'),        # 1 minute
            (1, 'second'),
        ]

        for interval_seconds, interval_name in intervals:
            count = int(seconds // interval_seconds)
            if count >= 1:
                plural = 's' if count > 1 else ''
                if is_future:
                    return f"in {count} {interval_name}{plural}"
                else:
                    return f"{count} {interval_name}{plural} ago"

        return "just now"

    except (ValueError, TypeError):
        return utc_time if utc_time else ''
