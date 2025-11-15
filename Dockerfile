# AccuDoc Dockerfile
# Automated Repository Documentation Generator

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install git (required for cloning repositories)
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
COPY accudoc/ /app/accudoc/
COPY accudoc_cli.py /app/
COPY main.py /app/
COPY requirements.txt /app/

# Create output directory
RUN mkdir -p /output

# Set the CLI as the default entry point
ENTRYPOINT ["python", "/app/accudoc_cli.py"]

# Default command shows help
CMD ["--help"]
