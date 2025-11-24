FROM python:3.11-slim

WORKDIR /app

# Install required tools
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    curl \
    gzip \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir redis psycopg2-binary

# Copy checkpointer script
COPY checkpointer.py .

# Run checkpointer
CMD ["python", "checkpointer.py"]
