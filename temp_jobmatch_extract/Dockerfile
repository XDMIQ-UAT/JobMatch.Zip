# Unified Dockerfile for Frontend + Backend
FROM python:3.11-slim

# Install Node.js and system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    postgresql-client \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir supervisor

# Install Node dependencies
COPY frontend/package.json frontend/package-lock.json* ./frontend/
WORKDIR /app/frontend
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Build frontend
COPY frontend/ .
RUN npm run build

# Copy backend code
WORKDIR /app
COPY backend/ ./backend/

# Create supervisord config
RUN mkdir -p /etc/supervisor/conf.d /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health && curl -f http://localhost:3000 || exit 1

# Start both services with supervisord
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

