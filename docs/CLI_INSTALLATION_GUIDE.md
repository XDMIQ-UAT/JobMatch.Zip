# JobMatch CLI Installation & Deployment Guide

## Overview

The JobMatch CLI is now available on PyPI and GitHub for easy installation and distribution.

### Available Installation Methods

1. **PyPI (Recommended)** - Simple pip install
2. **GitHub Releases** - Download pre-built wheels
3. **From Source** - Clone and install from repository

---

## Installation Methods

### Method 1: PyPI Installation (Simplest)

The CLI is published to PyPI as `jobmatch-cli`.

```bash
# Install latest version
pip install jobmatch-cli

# Verify installation
jobmatch-cli --help
```

**PyPI Package Page:**
https://pypi.org/project/jobmatch-cli/

---

### Method 2: GitHub Releases

Download pre-built distributions from GitHub releases:

```bash
# Option A: Download wheel (recommended for speed)
# From: https://github.com/XDM-ZSBW/jobmatch-ai/releases/tag/v0.1.0
pip install jobmatch_cli-0.1.0-py3-none-any.whl

# Option B: Download source (tar.gz)
# From: https://github.com/XDM-ZSBW/jobmatch-ai/releases/tag/v0.1.0
pip install jobmatch_cli-0.1.0.tar.gz
```

**GitHub Releases:**
https://github.com/XDM-ZSBW/jobmatch-ai/releases

---

### Method 3: Install from Source

```bash
# Clone repository
git clone https://github.com/XDM-ZSBW/jobmatch-ai.git
cd jobmatch-ai

# Install with dependencies
pip install -e .

# Install with development tools
pip install -e ".[dev]"
```

---

## Configuration

### Environment Variables

Before running the CLI, set these environment variables:

```bash
# Required: Database connection
export DATABASE_URL="postgresql://user:password@localhost:5432/jobmatch"

# Optional: Redis configuration (defaults to localhost:6379)
export REDIS_HOST="localhost"
export REDIS_PORT=6379

# Set by SSH/server (CLI will fail if not set)
export JOBMATCH_USER_ID="your-user-id"
export JOBMATCH_SESSION_ID="your-session-id"
```

### Configuration File

Create `~/.jobmatch/config.env`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/jobmatch
REDIS_HOST=localhost
REDIS_PORT=6379
```

Then load before running:

```bash
source ~/.jobmatch/config.env
jobmatch-cli
```

---

## Running the CLI

### Basic Usage

```bash
jobmatch-cli
```

### Command Reference

| Command | Description |
|---------|-------------|
| `start` | Start capability assessment |
| `status` | Check session status |
| `match` | View your match (when ready) |
| `feedback` | Leave session feedback |
| `help` | Show all commands |
| `logout` | Exit CLI |

### Example Session

```
╔══════════════════════════════════════════════════════════╗
║              JOBMATCH.ZIP - Session #abc123             ║
║  Capability-First Matching | Beta Access Confirmed      ║
╚══════════════════════════════════════════════════════════╝

> start
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: What capability do you need?

Your task (200 chars max):
> Debug FastAPI authentication flow
```

---

## System Requirements

### Minimum

- Python 3.8+
- pip 21.0+
- 50 MB disk space

### Recommended

- Python 3.11+ (latest stable)
- PostgreSQL 14+
- Redis 7+
- 100 MB disk space

---

## Troubleshooting

### "command not found: jobmatch-cli"

**Problem:** CLI not in PATH after installation

**Solution:**

```bash
# Verify pip install location
pip show jobmatch-cli

# Add Python scripts to PATH (Windows)
setx PATH "%PATH%;%APPDATA%\Python\Python311\Scripts"

# Add Python scripts to PATH (macOS/Linux)
export PATH="$HOME/.local/bin:$PATH"
```

### "Failed to connect to database"

**Problem:** DATABASE_URL not set or invalid

**Solution:**

```bash
# Check environment variable
echo $DATABASE_URL

# Set correct PostgreSQL connection string
export DATABASE_URL="postgresql://username:password@localhost:5432/jobmatch"

# Test connection
psql $DATABASE_URL
```

### "Failed to connect to Redis"

**Problem:** Redis not running or incorrect host

**Solution:**

```bash
# Verify Redis is running
redis-cli ping
# Should return: PONG

# Check Redis configuration
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

### "Invalid session"

**Problem:** JOBMATCH_USER_ID or JOBMATCH_SESSION_ID not set

**Solution:**

These are set by the SSH server when you log in. If running locally for testing:

```bash
export JOBMATCH_USER_ID="test-user-123"
export JOBMATCH_SESSION_ID="test-session-456"
```

---

## Deployment

### Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install CLI
RUN pip install --no-cache-dir jobmatch-cli

# Create non-root user
RUN useradd -m jobmatch

USER jobmatch

# Set entrypoint
ENTRYPOINT ["jobmatch-cli"]
```

Build and run:

```bash
docker build -t jobmatch-cli .
docker run -e DATABASE_URL=$DATABASE_URL -it jobmatch-cli
```

### Server Deployment

```bash
# Install on production server
ssh user@server "pip install jobmatch-cli"

# Create startup script (/opt/jobmatch/run.sh)
#!/bin/bash
source /etc/jobmatch/config.env
exec jobmatch-cli

# Make executable
chmod +x /opt/jobmatch/run.sh
```

---

## Development

### Building Distributions

```bash
# Install build tools
pip install build twine wheel setuptools

# Build wheel and source
python -m build

# Verify packages
python -m twine check dist/*

# Upload to PyPI
python -m twine upload dist/*
```

### Testing

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Check code style
black backend/
flake8 backend/
```

---

## Publishing New Versions

### Version Bump & Release

```bash
# Update version in setup.py and pyproject.toml
# Then tag and push:

git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0

# GitHub Actions automatically:
# 1. Builds wheel and source
# 2. Publishes to PyPI
# 3. Creates GitHub release
```

---

## Package Information

| Property | Value |
|----------|-------|
| **Package Name** | jobmatch-cli |
| **PyPI URL** | https://pypi.org/project/jobmatch-cli/ |
| **GitHub Repo** | https://github.com/XDM-ZSBW/jobmatch-ai |
| **Latest Version** | 0.1.0 |
| **License** | MIT |
| **Python Support** | 3.8+ |
| **Dependencies** | psycopg2-binary, redis |

---

## Support

- **Bug Reports:** https://github.com/XDM-ZSBW/jobmatch-ai/issues
- **Documentation:** https://github.com/XDM-ZSBW/jobmatch-ai/wiki
- **Website:** https://jobmatch.zip

---

## Next Steps

1. ✅ Install CLI: `pip install jobmatch-cli`
2. ✅ Set environment variables
3. ✅ Run: `jobmatch-cli`
4. ✅ Follow the 3-step assessment
5. ✅ Get matched with capability providers!
