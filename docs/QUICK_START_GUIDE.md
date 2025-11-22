# Quick Start Guide: Capability-First Development Workflow

**For**: Warp + Claude Code + Cursor development on Windows  
**Project**: Anonymous capability-based matching platform  
**Version**: 1.0

---

## Table of Contents
1. [Daily Workflow](#daily-workflow)
2. [Claude Code Integration](#claude-code-integration)
3. [Business Folder Operations](#business-folder-operations)
4. [Anonymous-First Patterns](#anonymous-first-patterns)
5. [State Recovery & Checkpoints](#state-recovery--checkpoints)
6. [Windows Development Setup](#windows-development-setup)
7. [Troubleshooting](#troubleshooting)

---

## Daily Workflow

### Morning Routine
```powershell
# Navigate to project
cd E:\jobfinder  # or C:\Users\dash\projects\jobmatch-ai

# Start Docker stack
docker compose up -d

# Verify all services healthy
docker compose ps

# Check human review queue
curl http://localhost:8000/api/review/queue/count
```

### Development Loop

**1. Open Cursor IDE**
- Cursor automatically loads `.cursorrules` from project root
- Rules enforce: anonymous-first, capability focus, checkpoint patterns

**2. Load Context Before Coding**
```powershell
# For API endpoint
python .claude-code\context-loader.py --hook api_endpoint "Your task"

# For XDMIQ questions
python .claude-code\context-loader.py --example xdmiq_questions

# Show available hooks
python .claude-code\context-loader.py --example nonexistent
```

**3. Generate Code with Cursor/Claude Code**
- Reference hook type in prompt: `[api_endpoint hook]`
- AI generates code following project patterns
- Validate against invariants (anonymous-first, checkpoints, human-review)

**4. Test Locally**
```powershell
# Backend tests
cd backend
pytest

# Frontend dev server
cd frontend
npm run dev
```

**5. Create Checkpoint Before Commit**
```powershell
# Manual checkpoint
python scripts\checkpoint.ps1 -tag "pre-commit-feature-x"

# Verify checkpoint created
curl http://localhost:8000/api/checkpoints/list
```

**6. Commit with Context**
```
feat(api): Add capability assessment endpoint [api_endpoint]

Generated using api_endpoint hook with constraints:
- Anonymous identity maintained
- State checkpoint before storage
- Human review queue for AI scores

References: backend/api/auth.py, backend/api/xdmiq.py
```

### Evening Routine
```powershell
# Create system checkpoint
python .claude-code\context-loader.py --hook create_checkpoint_workflow

# Review day's metrics (aggregate only)
curl http://localhost:8000/api/metrics/daily

# Shut down gracefully
docker compose down
```

---

## Claude Code Integration

### Available Hooks

| Hook Type | Purpose | Example Files |
|-----------|---------|---------------|
| `before_generate` | General context | main.py, config.py |
| `api_endpoint` | FastAPI routes | backend/api/auth.py |
| `database_model` | SQLAlchemy models | backend/database/models.py |
| `frontend_component` | Next.js components | frontend/app/xdmiq/page.tsx |
| `ai_integration` | AI features | backend/ai/matching_engine.py |
| `generate_capability_flow` | Capability assessment | backend/assessments/ |
| `generate_xdmiq_questions` | XDMIQ question banks | business/xdmiq/ |
| `generate_identity_proxy` | Anonymous sessions | backend/auth/anonymous_identity.py |
| `generate_platform_health` | Health checks | business/health/ |
| `migrate_to_ollama_llama32` | Ollama integration | backend/llm/ |
| `create_checkpoint_workflow` | State checkpoints | backend/resilience/ |

### Using Hooks

**Basic Usage**:
```powershell
python .claude-code\context-loader.py --hook api_endpoint "Create matching endpoint"
```

**With Limits** (for large output):
```powershell
python .claude-code\context-loader.py --hook ai_integration --limit 30 "AI matching"
```

**Dry Run** (no side effects):
```powershell
python .claude-code\context-loader.py --dry-run --hook database_model "User model"
```

**Show Hook Details**:
```powershell
python .claude-code\context-loader.py --example generate_xdmiq_questions
```

### Adding New Hooks

Edit `.claude-code/hooks.json`:
```json
{
  "hooks": {
    "your_new_hook": {
      "template": "Instructions for this hook type...",
      "example_files": [
        "path/to/example1.py",
        "path/to/example2.py"
      ]
    }
  }
}
```

### Warp Terminal Commands

Define in `warp.config.yaml`:
```yaml
commands:
  backend-dev: "cd backend && uvicorn main:app --reload"
  frontend-dev: "cd frontend && npm run dev"
  docker-up: "docker compose up -d"
  docker-down: "docker compose down"
  checkpoint: "python scripts/checkpoint.ps1"
  recover: "python scripts/recover.ps1"
```

Use in Warp:
```powershell
warp run backend-dev
warp run checkpoint -tag my-checkpoint
```

---

## Business Folder Operations

### Structure
```
business/
├── nouns/              # Entities (capabilities, roles, jobs)
├── verbs/              # Actions (assess, match, notify)
├── identity-proxy/     # Anonymous session flows
├── xdmiq/              # Question banks, scoring
├── health/             # Health checks, dashboards
├── runbooks/           # Operational playbooks
├── metrics/            # KPIs, OKRs
└── policies/           # Privacy, data boundaries
```

### Purpose
**"Keep all platform components healthy and happy"**

- **Platform health monitoring** (without exposing user data)
- **Operational runbooks** (incident response, scaling)
- **XDMIQ question management** (preference-based assessments)
- **Identity proxy policies** (anonymous-first rules)
- **Business metrics** (aggregate only)

### Common Operations

**1. Add XDMIQ Questions**
```yaml
# business/xdmiq/questions/problem-solving.yaml
domain: Problem Solving
questions:
  - id: ps-001
    text: "Which approach do you prefer when facing a complex problem?"
    options:
      - Break into sub-problems
      - Research similar solutions
      - Prototype and iterate
      - Diagram first
    follow_up: "Why does this work better for you?"
    scoring:
      weights: [0.8, 0.6, 0.9, 0.7]
```

**2. Update Identity Proxy Policies**
```yaml
# business/identity-proxy/policies/anonymous-sessions.yaml
policy:
  name: Anonymous Session Management
  rules:
    - Anonymous ID generation: cryptographically secure (SHA256)
    - Session data: keyed by anonymous_id only
    - Zero-knowledge: platform cannot reverse-engineer identity
    - Voluntary ID: opt-in only, explicit consent UI
    - Multiple personas: supported (user can create multiple anonymous IDs)
```

**3. Create Health Check**
```yaml
# business/health/checks/database.yaml
check:
  name: PostgreSQL Health
  endpoint: /health/database
  interval: 30s
  alert_threshold: 3 consecutive failures
  metrics:
    - connection_pool_size
    - query_latency_p99
    - active_connections
  privacy: No individual user data logged
```

**4. Add Runbook**
```markdown
# business/runbooks/incident-high-latency.md

## Incident: High API Latency (>500ms p99)

### Symptoms
- API response times exceed 500ms
- User experience degraded
- Matching queue backing up

### Diagnosis
1. Check Elasticsearch health
2. Check Redis cache hit rate
3. Check database query performance
4. Check Ollama response times

### Resolution
1. Scale Elasticsearch nodes
2. Increase Redis cache size
3. Add database read replicas
4. Optimize Ollama batch size

### Prevention
- Monitor p99 latency continuously
- Alert at 300ms threshold
- Auto-scale triggers at 400ms
```

---

## Anonymous-First Patterns

### Core Principle
**Separate capability from identity**. Users engage based on what they CAN DO, not who they ARE. Personalization comes later, voluntarily.

### Design Patterns

**1. Anonymous Session Flow**
```
User visits → Generate anonymous_id → Create session → Store preferences
                    ↓
              No identity required
                    ↓
        User completes assessments, matches jobs
                    ↓
        (Optional) User volunteers identity → Explicit consent → Link to anonymous_id
```

**2. Zero-Knowledge Architecture**
```python
# ✅ Good: Platform cannot reverse-engineer identity
anonymous_id = generate_secure_hash()  # SHA256 random bytes
session = create_session(anonymous_id)
# Platform stores: {anonymous_id: session_data}
# Platform CANNOT derive: {session_data → real_identity}

# ❌ Bad: Identity leakage
user_id = email.split('@')[0]  # Can reverse-engineer email
```

**3. Voluntary Identification**
```python
# User initiates (not platform)
if user.chooses_to_identify():
    # Explicit consent UI shown first
    consent = show_consent_dialog()
    if consent.granted:
        link_identity(anonymous_id, user_provided_identity)
        # Stored in separate table with clear consent audit trail
```

**4. Capability-First Matching**
```python
# ✅ Good: Match on capabilities
match_score = calculate_match(
    user_capabilities=["Python", "FastAPI", "AI/ML"],
    job_requirements=["Backend dev", "API design", "ML ops"],
    preferences=user.get_preferences()
)

# ❌ Bad: Match on credentials
match_score = calculate_match(
    user_education="MIT CS",  # Credential, not capability
    user_companies=["Google", "Meta"]  # Prestige, not ability
)
```

### Data Boundaries

**What Can Be Stored**:
- Anonymous session ID
- Capability assessments (skills, preferences)
- XDMIQ scores (0-100 scale)
- Match preferences
- Aggregated usage metrics

**What Cannot Be Stored** (without explicit consent):
- Real name, email, phone
- IP addresses (beyond session)
- Device fingerprints
- Cross-session tracking identifiers
- Any PII linkable to anonymous_id

### Privacy-Preserving Monitoring

**Aggregate Only**:
```python
# ✅ Good
metrics.increment("assessments_completed")  # Count only
metrics.histogram("matching_latency_ms", value)  # Distribution

# ❌ Bad
metrics.tag("user_id", anonymous_id).increment("action")  # Individual tracking
logger.info(f"User {anonymous_id} completed assessment")  # Identity in logs
```

---

## State Recovery & Checkpoints

### Last-Known-Good (LKG) Strategy

**Principle**: System can reboot to most recent good state without data loss.

### Checkpoint Types

1. **Automatic** (scheduled):
   - Every 30 minutes via `state-checkpointer` container
   - Marks LKG if health checks pass

2. **Manual** (on-demand):
   ```powershell
   python scripts\checkpoint.ps1 -tag "pre-deploy-v2"
   ```

3. **Pre-operation** (code-triggered):
   ```python
   checkpoint_id = state_manager.create_checkpoint(
       checkpoint_type=CheckpointType.MATCHING,
       entity_id="matching-algorithm",
       state_data=current_algorithm_state
   )
   ```

### Creating Checkpoints

**Full System Checkpoint**:
```powershell
# Checkpoint all services
docker exec backend python -c "
from backend.resilience.state_management import create_checkpoint_manager
from backend.database.connection import get_db_session
manager = create_checkpoint_manager(get_db_session())
manager.create_system_checkpoint({'source': 'manual'})
"
```

**Component Checkpoint**:
```python
# In code
from backend.resilience.state_management import StateManager, CheckpointType

checkpoint = state_manager.create_checkpoint(
    checkpoint_type=CheckpointType.MATCHING,
    entity_id="algorithm-v2",
    state_data={
        "algorithm_version": "2.0",
        "weights": current_weights,
        "config": current_config
    },
    metadata={"reason": "Deploying new algorithm"}
)
```

### Recovery

**List Available Checkpoints**:
```powershell
curl http://localhost:8000/api/checkpoints/list?limit=10
```

**Restore to LKG**:
```powershell
python scripts\recover.ps1 -checkpoint lkg
```

**Restore to Specific Checkpoint**:
```powershell
python scripts\recover.ps1 -checkpoint 12345
```

**Safe Reboot with Recovery**:
```powershell
# Full stack restart with auto-recovery on failure
python scripts\reboot_safe.ps1
```

### Reboot Procedure

1. **Drain traffic** (if load balancer present)
2. **Create pre-reboot checkpoint**
3. **Shut down services**: `docker compose down`
4. **Verify volumes intact**
5. **Restart services**: `docker compose up -d`
6. **Health checks**: All services healthy?
7. **If healthy**: Mark as LKG
8. **If unhealthy**: Restore to pre-reboot checkpoint

---

## Windows Development Setup

### Prerequisites

**Required**:
- Windows 10/11 Pro (for Docker Desktop)
- Docker Desktop with WSL2 backend
- Python 3.11+
- Node.js 18+
- PowerShell 7+
- Git

**Recommended**:
- Warp terminal
- Cursor IDE
- Visual Studio Code (fallback)

### Docker Desktop Configuration

**Settings**:
- WSL2 backend enabled
- Resources: 8GB RAM minimum, 4 CPUs
- File sharing: Enable for `C:\Users\dash\projects` and `E:\`
- Kubernetes: Disabled (unless needed)

**Volume Mapping**:
```yaml
# docker-compose.yml
volumes:
  - C:\Users\dash\projects\jobmatch-ai\data\postgres:/var/lib/postgresql/data
  - C:\Users\dash\projects\jobmatch-ai\data\redis:/data
  - C:\Users\dash\projects\jobmatch-ai\data\elasticsearch:/usr/share/elasticsearch/data
```

**Note**: Windows paths use `\` but Docker Compose accepts `/`. Both work.

### Path Handling

**PowerShell scripts use backslashes**:
```powershell
cd C:\Users\dash\projects\jobmatch-ai
python .claude-code\context-loader.py
```

**Docker Compose volumes use forward slashes**:
```yaml
volumes:
  - ./backend:/app  # Relative paths work
  - C:/Users/dash/projects/jobmatch-ai/data:/data  # Absolute with /
```

### Performance Tips

1. **WSL2 filesystem**: Keep code in WSL2 filesystem for best performance
   ```powershell
   # Move project to WSL2
   wsl
   cd ~
   git clone <repo>
   ```

2. **Exclude from Windows Defender**:
   - Add `C:\Users\dash\projects` to exclusions
   - Add Docker Desktop paths

3. **Volume mounts**: Use named volumes instead of bind mounts for databases
   ```yaml
   volumes:
     postgres_data:  # Named volume (faster)
   ```

### Common Windows Issues

**Issue**: `CRLF vs LF line endings`  
**Fix**:
```powershell
git config --global core.autocrlf false
```

**Issue**: `Permission denied on scripts`  
**Fix**:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Issue**: `Docker volume not updating`  
**Fix**:
```powershell
docker compose down -v  # Remove volumes
docker compose up -d    # Recreate
```

---

## Troubleshooting

### Claude Code Issues

**Problem**: Context loader fails with `ModuleNotFoundError`  
**Solution**:
```powershell
cd E:\jobfinder  # or jobmatch-ai
python -m pip install -r requirements.txt
```

**Problem**: Hooks not loading expected files  
**Solution**:
```powershell
# Verify hooks.json syntax
python -m json.tool .claude-code\hooks.json

# Check file paths exist
ls backend\api\auth.py
```

**Problem**: Generated code violates anonymous-first principle  
**Solution**: Add explicit constraint in prompt:
```
CONSTRAINT: Must work with zero knowledge of user identity.
Only anonymous_id available. Platform cannot reverse-engineer identity.
```

### Docker Issues

**Problem**: Service unhealthy  
**Solution**:
```powershell
# Check logs
docker compose logs [service-name]

# Check health
docker compose ps

# Restart service
docker compose restart [service-name]
```

**Problem**: Ollama not responding  
**Solution**:
```powershell
# Check if model loaded
docker exec ollama ollama list

# Pull llama3.2 if missing
docker exec ollama ollama pull llama3.2
```

**Problem**: Out of disk space  
**Solution**:
```powershell
# Clean up
docker system prune -a --volumes

# Remove old checkpoints
rm C:\Users\dash\projects\jobmatch-ai\data\checkpoints\old-*
```

### State Recovery Issues

**Problem**: Checkpoint creation fails  
**Solution**:
```powershell
# Check database connection
docker exec backend python -c "from backend.database.connection import engine; engine.connect()"

# Check disk space
df -h
```

**Problem**: Recovery doesn't restore state  
**Solution**:
```powershell
# Verify checkpoint exists
curl http://localhost:8000/api/checkpoints/list

# Check checkpoint data integrity
docker exec postgres pg_dump -U jobfinder jobfinder > test.sql
```

### Business Folder Issues

**Problem**: XDMIQ questions not loading  
**Solution**:
```powershell
# Verify YAML syntax
python -c "import yaml; yaml.safe_load(open('business/xdmiq/questions/file.yaml'))"
```

**Problem**: Health checks failing  
**Solution**:
```powershell
# Test endpoint directly
curl http://localhost:8000/health/database
curl http://localhost:8000/health/redis
```

---

## Quick Reference Card

### Essential Commands

```powershell
# Start
docker compose up -d

# Stop
docker compose down

# Logs
docker compose logs -f [service]

# Checkpoint
python scripts\checkpoint.ps1 -tag "my-tag"

# Recover
python scripts\recover.ps1 -checkpoint lkg

# Context
python .claude-code\context-loader.py --hook [type] "task"

# Health
curl http://localhost:8000/health
```

### Invariants Checklist

Before committing code, verify:
- [ ] Anonymous-first (no identity exposure)
- [ ] Checkpoint created (if state changes)
- [ ] Human-review queue (if AI decision)
- [ ] Capability-focus (not credentials)
- [ ] Privacy-preserving (aggregate metrics only)
- [ ] Hook referenced (in commit message)

### Support

- **Docs**: `E:\jobfinder\docs\` or `C:\Users\dash\projects\jobmatch-ai\docs\`
- **Audit Report**: `docs/AUDIT_REPORT.md`
- **Prompt Guide**: `docs/PROMPT_OPTIMIZATION.md`
- **Hooks Config**: `.claude-code/hooks.json`
- **Cursor Rules**: `.cursorrules`

---

**Last Updated**: 2025-01-22  
**Version**: 1.0  
**For**: jobmatch-ai capability-first development
