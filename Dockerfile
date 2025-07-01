# Multi-stage build for smaller image
# Build stage
FROM python:3.13.2-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.13.2-alpine

# Create non-root user
RUN adduser -D -h /app pylynk

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/pylynk/.local

# Copy application code
COPY --chown=pylynk:pylynk pylynk.py .
COPY --chown=pylynk:pylynk pylynk/ ./pylynk/

# Switch to non-root user
USER pylynk

# Set Python path to find user-installed packages
ENV PYTHONPATH=/home/pylynk/.local/lib/python3.13/site-packages
ENV PATH=/home/pylynk/.local/bin:$PATH

# Set the entrypoint
ENTRYPOINT ["python", "pylynk.py"]