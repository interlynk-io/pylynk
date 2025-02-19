# Use a minimal Python Alpine base image
FROM python:3.13.2-alpine

# Set the working directory inside the container
WORKDIR /app

# Install git, clone latest release, and remove git
RUN apk add --no-cache git \
    && git clone https://github.com/interlynk-io/pylynk /app \
    && cd /app \
    && git checkout $(git describe --tags `git rev-list --tags --max-count=1`) \
    && apk del git

# Install Python dependencies in a virtual environment
RUN python3 -m venv /venv \
    && /venv/bin/pip install --no-cache-dir -r /app/requirements.txt

# Use the virtual environment's Python binary as the entrypoint
ENTRYPOINT ["/venv/bin/python", "/app/pylynk.py"]
