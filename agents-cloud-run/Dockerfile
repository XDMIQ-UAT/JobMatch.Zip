# Cloud Run Agent Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent service code
COPY agent_service.py .
COPY .dockerignore .

# Copy workflow engine and agent files from parent directory
# Note: These need to be accessible at runtime
COPY ../.cursor/workflows/ ./workflows/
COPY ../.cursor/agents/ ./agents/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Cloud Run port
ENV PORT=8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT}/health')" || exit 1

# Run agent service
CMD exec uvicorn agent_service:app --host 0.0.0.0 --port $PORT --workers 1

