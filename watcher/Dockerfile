FROM python:3.11-slim

# Install basic tools (optional, useful for debugging)
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim less nano procps \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy watcher script into container
COPY watcher.py /app/watcher.py

RUN mkdir -p /app/config
# Set execution command
CMD ["python", "/app/watcher.py"]
