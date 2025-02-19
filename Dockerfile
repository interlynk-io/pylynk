# Use a minimal Python Alpine base image
FROM python:3.12.9-alpine

# Set the working directory inside the container
WORKDIR /app

# Install required dependencies
RUN apk add --no-cache git \
    && git clone https://github.com/interlynk-io/pylynk /app \
    && pip install -r /app/requirements.txt

# Set default entrypoint
ENTRYPOINT ["python3", "/app/pylynk.py"]
