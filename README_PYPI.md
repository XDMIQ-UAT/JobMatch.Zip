# JobMatch CLI

Terminal-based capability matching interface for [JobMatch.zip](https://jobmatch.zip) paid beta users.

[![PyPI version](https://badge.fury.io/py/jobmatch-cli.svg)](https://badge.fury.io/py/jobmatch-cli)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

Install directly from PyPI:

```bash
pip install jobmatch-cli
```

### Requirements

- Python 3.8+
- PostgreSQL 14+ (for session data)
- Redis 7+ (for state management)

## Quick Start

Launch the interactive CLI:

```bash
jobmatch-cli
```

The CLI will prompt you through a 3-step capability assessment:

1. **Describe your task** - What capability do you need? (200 chars max)
2. **Session preferences** - Time estimate, availability, interaction mode
3. **Review & submit** - Confirm details before request submission

### Available Commands

```
start     - Start or continue capability assessment
status    - Check your session status
match     - Check if you have a match
feedback  - Leave feedback after your session
help      - Show available commands
logout    - Exit the terminal
```

## Setup Environment Variables

The CLI requires these environment variables:

```bash
# Database connection
export DATABASE_URL="postgresql://user:password@localhost:5432/jobmatch"

# Redis configuration
export REDIS_HOST="localhost"
export REDIS_PORT=6379

# Session authentication (set by SSH)
export JOBMATCH_USER_ID="your-user-id"
export JOBMATCH_SESSION_ID="your-session-id"
```

## Example Session

```
╔══════════════════════════════════════════════════════════╗
║              JOBMATCH.ZIP - Session #abc123             ║
║  Capability-First Matching | Beta Access Confirmed      ║
╚══════════════════════════════════════════════════════════╝

Welcome! You've purchased a JobMatch session.

Let's find your best match in 3 steps.

Type 'help' for commands or just follow the prompts.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> start

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: What capability do you need?

Examples:
• Debug Python FastAPI endpoint
• Review AI prompt engineering strategy
• Explain Kubernetes deployment
• Brainstorm LLC business structure
• Automate data pipeline with n8n

Your task (200 chars max):
> Debug my Next.js Server Components data fetching issue and optimize performance
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/XDM-ZSBW/jobmatch-ai.git
cd jobmatch-ai

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black backend/
isort backend/
```

### Build Distribution

```bash
python -m build
```

## Project Structure

```
jobmatch-ai/
├── backend/
│   └── jobmatch_cli.py       # Main CLI implementation
├── setup.py                   # Package configuration
├── pyproject.toml            # Modern Python packaging
├── .github/workflows/
│   └── publish-to-pypi.yml   # CI/CD for PyPI publishing
└── README.md                 # This file
```

## API Documentation

JobMatch.zip provides a REST API alongside the CLI:

- **Base URL**: https://jobmatch.zip
- **API Docs**: https://jobmatch.zip/docs
- **Health Check**: https://jobmatch.zip/health

## Security

- Session credentials are environment-managed, never hardcoded
- Database connections use encrypted credentials
- Redis uses connection pooling with optional authentication
- All user data is encrypted at rest

## Support

- **Issues**: [GitHub Issues](https://github.com/XDM-ZSBW/jobmatch-ai/issues)
- **Documentation**: [GitHub Wiki](https://github.com/XDM-ZSBW/jobmatch-ai/wiki)
- **Website**: [jobmatch.zip](https://jobmatch.zip)

## License

MIT License - See LICENSE file for details

## Versioning

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking API changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Changelog

### v0.1.0 (2025-01-27)

- Initial PyPI release
- Terminal-based capability assessment (3-step flow)
- Session state persistence via Redis
- Database integration for request tracking
- Interactive command interface (start, status, match, feedback)
- Environment-based configuration

---

**Built with ❤️ for capability-first matching**
