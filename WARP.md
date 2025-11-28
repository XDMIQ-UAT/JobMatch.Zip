# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

JobMatch AI is an AI-powered SaaS platform that connects job seekers directly with hiring managers, bypassing traditional job board inefficiencies. The platform uses AI for intelligent resume parsing, job-candidate matching, and automated communication while maintaining human-in-the-loop decision making.

**Hybrid Architecture**: Python FastAPI backend + Next.js frontend + Docker orchestration

## Quick Start Commands

### Infrastructure Management (Primary Development Flow)

```powershell
# Start all services (Docker-based)
.\scripts\infra-agent.ps1 up

# Check status and health
.\scripts\infra-agent.ps1 status

# View logs
.\scripts\infra-agent.ps1 logs

# Run verification tests before production
.\scripts\infra-agent.ps1 verify

# Stop all services
.\scripts\infra-agent.ps1 down

# Clean restart
.\scripts\infra-agent.ps1 clean
.\scripts\infra-agent.ps1 up
```

**Access Points (when running):**
- Frontend: http://localhost:3000
- Universal Canvas: http://localhost:3000/canvas
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Elasticsearch: localhost:9200
- Ollama (Local LLM, fallback): localhost:11434

### Monorepo NPM Commands (Alternative)

```bash
# Install dependencies
npm install

# Start both frontend and backend (dev mode)
npm run dev

# Start individually
npm run dev:backend    # Node.js API on port 4000
npm run dev:frontend   # Next.js on port 3000

# Build all workspaces
npm run build

# Run all tests
npm run test

# E2E tests with Playwright
npm run test:e2e
npm run test:e2e:ui       # Interactive UI mode
npm run test:e2e:headed   # Visible browser
npm run test:e2e:debug    # Debug mode

# Lint and type check
npm run lint
npm run typecheck
```

### Backend Python Commands

```bash
# Backend development server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Python tests
pytest

# Database migrations (Alembic)
alembic upgrade head
alembic revision --autogenerate -m "description"

# CLI tool (for paid beta users)
pip install -e .
jobmatch-cli
```

### Database Operations

```bash
# Prisma (if using Node.js backend)
npm run generate --workspace=backend
npm run migrate --workspace=backend
npm run db:studio --workspace=backend

# PostgreSQL direct access
psql -U jobmatch -d jobmatch

# Via Docker
docker exec -it jobmatch-postgres psql -U jobmatch -d jobmatch
```

### Testing Single Files

```bash
# Backend Python tests
pytest backend/tests/test_specific.py
pytest backend/tests/test_specific.py::test_function_name

# Backend Node.js tests (Jest)
npm run test --workspace=backend -- path/to/test.test.ts
npm run test --workspace=backend -- -t "test name pattern"

# Frontend tests
npm run test --workspace=frontend -- -t "test pattern"

# E2E specific test
npx playwright test tests/e2e/homepage.spec.ts
npx playwright test --debug tests/e2e/auth.spec.ts
```

## High-Level Architecture

### Technology Stack

**Backend (Hybrid)**:
- Primary: **Python FastAPI** (production API)
- Secondary: **Node.js/Express** (TypeScript, monorepo workspace)
- Database: **PostgreSQL 16** + **Redis** cache
- Search: **Elasticsearch 8**
- AI/LLM: **OpenRouter** (primary, Claude 3.5 Sonnet) + **Ollama** fallback for local dev
- ORM: **Alembic** (Python migrations) + **Prisma** (Node.js, legacy)

**Frontend**:
- Framework: **Next.js 14** (App Router)
- UI: **React 18** + **TypeScript** + **TailwindCSS**
- State: **Zustand** (client) + **React Query** (server)
- Forms: **React Hook Form** + **Zod** validation
- Real-time: **Socket.io**

**Infrastructure**:
- Orchestration: **Docker Compose** (dev, prod, VM variants)
- Deployment: **Google Cloud Platform** (Cloud Run, Compute Engine)
- CI/CD: **GitHub Actions**
- Monitoring: **Supervisord** (VM), custom health checks

### Directory Structure

```
zip-jobmatch/
├── backend/              # Python FastAPI application
│   ├── ai/              # AI/LLM integrations
│   ├── api/             # API routes
│   ├── auth/            # Authentication logic
│   ├── database/        # Database models, connections
│   ├── alembic/         # Database migrations
│   ├── assessment/      # Job-candidate matching logic
│   ├── marketplace/     # Job posting, application flows
│   ├── human_review/    # Human-in-the-loop workflows
│   ├── security/        # Security utilities
│   ├── monitoring/      # Health checks, metrics
│   └── jobmatch_cli.py  # Terminal CLI for beta users
├── frontend/            # Next.js application
│   ├── app/            # Next.js App Router pages
│   ├── components/     # React components
│   ├── lib/            # Utilities, API clients
│   └── public/         # Static assets
├── shared/              # Shared types (future)
├── scripts/             # Deployment, setup scripts
│   ├── infra-agent.ps1          # Primary dev workflow manager
│   ├── deploy-to-vm.ps1         # GCP VM deployment
│   ├── deploy-backend-quick.sh  # Backend-only deploy
│   └── setup-playwright.ps1     # E2E testing setup
├── tests/               # E2E tests (Playwright)
├── warp-workflows/      # Warp Drive workflows
├── .warp/              # Warp configuration
│   ├── INFRA_COMMANDS.md        # Quick reference
│   └── agents/                  # Guardian agents
├── docker-compose.yml           # Production Docker setup
├── docker-compose.dev.yml       # Development Docker setup
├── docker-compose.vm.yml        # VM deployment variant
└── docker-compose.simple.yml    # Minimal setup
```

### Backend Architecture Deep Dive

**Primary Framework**: Python FastAPI (port 8000)
- `backend/app/main.py` - Application entry point
- `backend/api/` - Route handlers organized by domain
- `backend/database/` - SQLAlchemy models, connection management
- `backend/alembic/` - Database migration management

**Key Backend Modules**:
- **AI Integration** (`backend/ai/`): Ollama + OpenAI clients
- **Assessment** (`backend/assessment/`): Capability matching, scoring algorithms
- **Marketplace** (`backend/marketplace/`): Job postings, applications, matches
- **Human Review** (`backend/human_review/`): Queue management for human decisions
- **Security** (`backend/security/`): JWT, RBAC, encryption utilities
- **Monitoring** (`backend/monitoring/`): Health endpoints, metrics collection

**Authentication Flow**:
- JWT-based with roles: `JOB_SEEKER`, `HIRING_MANAGER`, `ADMIN`
- Magic link support for passwordless auth
- Token expiry: Configurable via environment

**Database Patterns**:
- PostgreSQL for relational data (users, jobs, applications)
- Redis for caching, session management, rate limiting
- Elasticsearch for full-text search (job postings, resumes)

### AI/LLM Integration Strategy

**Primary Provider**: OpenRouter with `anthropic/claude-3.5-sonnet`
- Unified API access to best AI models at lower costs (~$3/1M tokens)
- Automatic failover, pay-as-you-go billing
- Alternative models: `anthropic/claude-3-haiku` (fast, $0.25/1M), `meta-llama/llama-3.1-70b-instruct` (cheap, $0.50/1M)

**Fallback**: Ollama with `llama3.2` (local development, no API costs)
- Automatically used if OPENROUTER_API_KEY not set or service unavailable

**AI Service Locations**:
- Python: `backend/llm/client.py` (unified LLM client), `backend/ai/` (AI utilities)
- Node.js (legacy): `backend/src/services/aiService.ts`

**Key AI Functions**:
1. **Resume Parsing**: Extract structured data from text/PDF resumes
2. **Match Scoring**: Calculate job-candidate compatibility (0-100 score)
3. **Interview Generation**: Create relevant interview questions
4. **Fraud Detection**: Identify scam job postings
5. **Recommendation Engine**: Batch scoring for job suggestions

**LLM Response Format**:
- Prefer JSON output with structured schemas
- Retry logic for failed API calls
- Caching to avoid redundant requests

### Frontend Architecture

**Routing**: Next.js 14 App Router
- `frontend/app/` - Pages using file-system routing
- Server components by default, client components marked with `'use client'`

**State Management**:
- **Zustand**: Global client state (user session, UI state)
- **React Query**: Server state, API caching, mutations
- **Socket.io**: Real-time updates (application status, messages)

**Key Components**:
- Authentication flows (login, signup, magic link)
- Job browsing and search
- Application submission
- Messaging interface
- Universal Canvas (special feature at `/canvas`)

**API Client Pattern**:
- Centralized in `frontend/lib/api.ts` or similar
- Axios or fetch with interceptors for auth tokens
- Type-safe with TypeScript interfaces

## Core Development Patterns

### Pre-Release Verification (CRITICAL)

**Always run before production deployment**:

```powershell
# 1. Start environment
.\scripts\infra-agent.ps1 up

# 2. Verify everything works
.\scripts\infra-agent.ps1 verify

# 3. Check logs if verification fails
.\scripts\infra-agent.ps1 logs

# 4. Only proceed to deployment if verification passes ✓
```

### Docker Compose Modes

**Development** (`docker-compose.dev.yml`):
- Hot reload enabled (volume mounts)
- Debug logging
- Source code mounted into containers

**Production** (`docker-compose.yml`):
- OpenRouter API integration (requires OPENROUTER_API_KEY)
- Ollama container available as fallback
- Optimized builds
- Health checks enabled
- Automatic restarts

**VM Deployment** (`docker-compose.vm.yml`):
- Tailored for GCP Compute Engine
- External IP configuration
- Supervisord for process management

**Simple** (`docker-compose.simple.yml`):
- Minimal services (backend, frontend, postgres)
- Quick testing

### Environment Variables

**Backend** (`backend/.env`):
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/jobmatch
REDIS_URL=redis://localhost:6379
ELASTICSEARCH_URL=http://localhost:9200

# LLM Configuration (OpenRouter primary)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_BASE_URL=https://openrouter.ai/api/v1

# Fallback for local dev (if no API key)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Application
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret
ENVIRONMENT=development

# External Services
AWS_SES_REGION=us-east-1
AWS_SES_ACCESS_KEY=...
TWILIO_ACCOUNT_SID=...
STRIPE_SECRET_KEY=sk_test_...
```

**Frontend** (`frontend/.env`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SOCKET_URL=http://localhost:8000
NODE_ENV=development
```

### Service Health Checks

**Backend Health Endpoint**: `http://localhost:8000/health`
- Returns JSON: `{ "status": "ok", "timestamp": "..." }`
- Checks database connectivity, Redis, Elasticsearch

**Verify All Services**:
```powershell
# Automated health check
.\scripts\infra-agent.ps1 verify

# Manual checks
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:9200/_cluster/health
```

### Development Workflow with Cursor + Warp

**Simultaneous Development Pattern**:
- **Warp**: CLI, monitoring, logs, Docker management, deployment
- **Cursor**: Code editing, debugging, file operations
- **Pieces MCP**: Context synchronization between tools

**Typical Session**:
1. Start in Warp: `.\scripts\infra-agent.ps1 up`
2. Verify services: `.\scripts\infra-agent.ps1 status`
3. Open Cursor for code changes
4. Run tests in Warp: `npm run test`
5. Check logs: `.\scripts\infra-agent.ps1 logs`
6. Deploy: `.\scripts\infra-agent.ps1 verify` then deploy scripts

## Deployment

### Google Cloud Platform

**Project**: `futurelink-private-112912460`
**VM Instance**: `futurelink-vm`
**Region**: `us-central1-a`
**Machine Type**: `e2-micro`
**External IP**: `34.134.208.48`
**OS**: Ubuntu 22.04 LTS

### Deployment Commands

```powershell
# Deploy to GCP VM (comprehensive)
.\scripts\deploy-to-vm.ps1

# Quick backend deployment
.\scripts\deploy-backend-quick.sh

# Deploy frontend only
.\scripts\deploy-frontend-vm.sh

# Setup SSL/DNS
.\scripts\setup-https-jobmatch-zip.sh
.\scripts\setup-cloud-run-ssl-domain.sh
```

### GCP Services Used

- **Compute Engine**: VM hosting (`futurelink-vm`)
- **Cloud Run**: Serverless container deployment (planned)
- **Cloud SQL**: Managed PostgreSQL (optional)
- **Secret Manager**: API keys, credentials
- **Cloud Storage**: Static assets, backups

### GitHub Actions (CI/CD)

Located in `.github/workflows/`:
- `deploy.yml` - Main deployment workflow
- `publish-to-pypi.yml` - Publish CLI to PyPI

## Testing Strategy

### E2E Testing with Playwright

**Setup**:
```powershell
.\scripts\setup-playwright.ps1
```

**Test Locations**: `tests/e2e/`
- `homepage.spec.ts` - Landing page tests
- `auth.spec.ts` - Authentication flows
- `fixtures.ts` - Custom test utilities

**Running Tests**:
```bash
npm run test:e2e           # Headless
npm run test:e2e:ui        # Interactive UI (recommended)
npm run test:e2e:headed    # Visible browser
npm run test:e2e:debug     # Debug mode
npm run test:e2e:report    # View report
```

**MCP Integration**: Warp's browser MCP tools can interact with Playwright tests directly via AI commands.

### Backend Testing

**Python (FastAPI)**:
```bash
# All tests
pytest

# Specific module
pytest backend/tests/test_api.py

# Specific test
pytest backend/tests/test_api.py::test_user_creation

# With coverage
pytest --cov=backend
```

**Node.js (if using legacy backend)**:
```bash
npm run test --workspace=backend
npm run test --workspace=backend -- -t "user authentication"
```

### Testing Philosophy

- **Unit Tests**: Business logic, utilities, services
- **Integration Tests**: API endpoints, database operations
- **E2E Tests**: User flows (signup, job application, messaging)
- **Human-in-the-Loop**: Manual review queues before AI decisions

## OpenRouter Setup

**Why OpenRouter**: Access to Claude, GPT-4, and other top models at significantly lower costs (~$3/1M tokens for Claude 3.5 Sonnet vs $15+ direct).

### Quick Setup

1. **Get API Key**:
   - Go to https://openrouter.ai/keys
   - Sign up (GitHub OAuth)
   - Create new API key (starts with `sk-or-v1-...`)

2. **Add to Environment**:
   ```bash
   # In backend/.env
   LLM_PROVIDER=openrouter
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   LLM_MODEL=anthropic/claude-3.5-sonnet
   ```

3. **Test**:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
   ```

### Model Options

- **claude-3.5-sonnet**: Best quality, ~$3/1M tokens
- **claude-3-haiku**: Fast & cheap, ~$0.25/1M tokens  
- **meta-llama/llama-3.1-70b-instruct**: Open source, ~$0.50/1M tokens

See `docs/OPENROUTER_SETUP.md` for detailed cost analysis and configuration.

## CLI Tool (JobMatch CLI)

**Package**: `jobmatch-cli` (PyPI)
**Purpose**: Terminal-based capability matching for paid beta users

**Installation**:
```bash
# Development install
pip install -e .

# Production install (after PyPI publish)
pip install jobmatch-cli
```

**Usage**:
```bash
# Set environment
export JOBMATCH_USER_ID="user-id"
export DATABASE_URL="postgresql://..."
export REDIS_HOST="localhost"

# Run CLI
jobmatch-cli
```

**Development**: `backend/jobmatch_cli.py`

## Stripe Payment Integration

**Setup Documentation**:
- `STRIPE_SETUP_COMPLETE.md` - Complete setup guide
- `STRIPE_CLI_QUICKREF.md` - Quick reference
- `.stripe/` - Stripe configuration files

**Webhook Testing**:
```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook
```

## State Management & Checkpointing

### Create Checkpoint

```powershell
# Create basic checkpoint
.\scripts\checkpoint.ps1 -CheckpointName "before-deployment" -Description "Pre-deployment backup"

# Create checkpoint with database backup
.\scripts\checkpoint.ps1 -CheckpointName "full-backup" -IncludeDatabase -IncludeRedis

# Create compressed checkpoint
.\scripts\checkpoint.ps1 -CheckpointName "archive" -IncludeDatabase -IncludeRedis -Compress
```

### List Checkpoints

```powershell
# View all available checkpoints
.\scripts\recover.ps1 -List
```

### Restore from Checkpoint

```powershell
# Restore (with confirmation)
.\scripts\recover.ps1 -CheckpointName "before-deployment"

# Force restore (no confirmation)
.\scripts\recover.ps1 -CheckpointName "before-deployment" -Force
```

**Checkpoint Features**:
- Git commit and branch tracking
- Docker services status capture
- PostgreSQL database backup
- Redis data backup
- Environment configuration backup
- Docker Compose configuration backup
- Optional compression
- Automatic metadata tracking

## Troubleshooting

### Port Conflicts

```powershell
# Check what's using a port (Windows)
Get-NetTCPConnection -LocalPort 8000

# Kill process by port (PowerShell as admin)
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force
```

### Docker Issues

```powershell
# Clean restart
docker-compose down -v
docker system prune -a
.\scripts\infra-agent.ps1 up

# View logs for specific service
docker logs jobmatch-backend
docker logs jobmatch-frontend

# Rebuild without cache
docker-compose build --no-cache
```

### Database Issues

```bash
# Reset database (destroys data!)
docker exec -it jobmatch-postgres psql -U jobmatch -c "DROP DATABASE jobmatch;"
docker exec -it jobmatch-postgres psql -U jobmatch -c "CREATE DATABASE jobmatch;"
alembic upgrade head

# Check database connection
docker exec -it jobmatch-postgres psql -U jobmatch -d jobmatch -c "SELECT 1;"
```

### Frontend Build Issues

```bash
# Clear Next.js cache
rm -rf frontend/.next
rm -rf frontend/node_modules/.cache

# Rebuild
cd frontend
npm install
npm run build
```

### LLM Issues

**OpenRouter (Primary)**:
```bash
# Test OpenRouter connection
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "test"}]}'

# Check if API key is set
grep OPENROUTER_API_KEY backend/.env
```

**Ollama (Fallback)**:
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Pull model manually (if using Ollama)
docker exec -it jobmatch-ollama ollama pull llama3.2

# View Ollama logs
docker logs jobmatch-ollama
```

## Guardian Agents

Located in `.warp/agents/`:
- `SaM-brand-ux-guardian.md` - Brand consistency guardian
- `compliance-guardian.md` - Regulatory compliance checks
- `data-governance-guardian.md` - Data privacy enforcement

These are specialized AI agents for code review and quality gates.

## Important Files

### Configuration
- `warp.config.yaml` - Warp terminal configuration
- `playwright.config.ts` - E2E test configuration
- `pyproject.toml` - Python package configuration
- `package.json` - Node.js workspace configuration

### Documentation
- `README.md` - Project overview
- `CONTRIBUTING.md` - Contribution guidelines
- `docs/` - Comprehensive documentation
  - `SETUP.md` - Setup instructions
  - `GCP_DEPLOYMENT.md` - GCP deployment guide
  - `PLAYWRIGHT_QUICK_REFERENCE.md` - Testing guide

### Deployment
- `Dockerfile` - Production backend container
- `Dockerfile.dev` - Development backend container
- `frontend/Dockerfile` - Frontend container
- `supervisord.conf` - Process management for VM

### Special Features
- `.claude-code/` - Claude AI integration files
- `.github/PULL_REQUEST_TEMPLATE.md` - PR guidelines
- `business/` - Business documentation

## Architecture Principles (from PR Template)

All code must adhere to:
1. **Anonymous-first**: Features work without requiring identity
2. **Capability over credentials**: Focus on skills/abilities, not titles/degrees
3. **Human-in-the-loop**: AI decisions queued for human review
4. **State recovery**: Changes create checkpoints for rollback

## Additional Resources

- **Warp Drive Workflows**: `warp-workflows/` - Reusable command sequences
- **Infrastructure Docs**: `.warp/INFRA_COMMANDS.md` - Quick reference
- **Testing Guide**: `tests/README.md` - E2E testing instructions
- **Playwright MCP Setup**: `docs/PLAYWRIGHT_MCP_SETUP.md` - Browser automation
- **OpenRouter Setup**: `docs/OPENROUTER_SETUP.md` - LLM configuration and cost analysis

---

**Last Updated**: 2025-11-24  
**Maintainers**: Update this file when changing scripts, ports, API paths, or deployment configuration.
