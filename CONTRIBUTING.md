# Contributing to JobMatch.Zip

Thank you for your interest in contributing to JobMatch.Zip! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Documentation](#documentation)
- [Claude Code Hooks](#claude-code-hooks)

---

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior
- Be respectful and constructive in all interactions
- Provide and accept constructive feedback gracefully
- Focus on what's best for the project and community
- Show empathy towards other contributors

### Unacceptable Behavior
- Harassment, discrimination, or personal attacks
- Trolling, insulting comments, or political arguments
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

---

## Getting Started

### Prerequisites
- Node.js 20+ (for frontend)
- Python 3.10+ (for backend)
- PostgreSQL 15+
- Docker & Docker Compose
- Git
- PowerShell 7+ (for Windows scripts)

### First-Time Contributors
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/JobMatch.Zip.git`
3. Add upstream remote: `git remote add upstream https://github.com/XDM-ZSBW/JobMatch.Zip.git`
4. Follow [Development Setup](#development-setup) instructions

---

## Development Setup

### 1. Clone and Install Dependencies

```powershell
# Clone the repository
git clone https://github.com/XDM-ZSBW/JobMatch.Zip.git
cd JobMatch.Zip

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Configure Environment Variables

Edit `backend/.env` and `frontend/.env` with your local configuration.

### 3. Start Docker Services

```powershell
# Start PostgreSQL, Redis, Elasticsearch, Ollama
docker compose up -d postgres redis elasticsearch ollama

# Verify services are running
docker compose ps
```

### 4. Run Database Migrations

```powershell
cd backend
alembic upgrade head
```

### 5. Start Development Servers

```powershell
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 6. Verify Setup

- Frontend: http://localhost:3000
- Backend API: http://localhost:4000
- API Docs: http://localhost:4000/docs

---

## Project Structure

```
JobMatch.Zip/
├── backend/                # FastAPI backend
│   ├── api/               # API endpoints
│   ├── core/              # Core business logic
│   ├── database/          # Database models and connections
│   ├── services/          # External service integrations
│   ├── tests/             # Backend tests
│   └── main.py            # FastAPI application entry point
├── frontend/              # Next.js frontend
│   ├── app/               # Next.js App Router pages
│   ├── components/        # React components
│   ├── lib/               # Utility functions
│   ├── hooks/             # Custom React hooks
│   └── types/             # TypeScript type definitions
├── business/              # Business operational assets
│   ├── taxonomy/          # Skills and capability definitions
│   ├── questions/         # XDMIQ questions
│   ├── policies/          # Business policies
│   └── workflows/         # Business process workflows
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── .claude-code/          # Claude Code hooks and prompts
├── .github/               # GitHub templates and workflows
└── docker-compose.yml     # Docker services configuration
```

---

## Development Workflow

### Branch Strategy

- **`main`**: Production-ready code (protected)
- **`develop`**: Integration branch for features
- **`feature/*`**: New features (e.g., `feature/anonymous-session`)
- **`fix/*`**: Bug fixes (e.g., `fix/session-timeout`)
- **`hotfix/*`**: Urgent production fixes
- **`docs/*`**: Documentation updates

### Creating a Feature Branch

```powershell
# Update your local repository
git checkout develop
git pull upstream develop

# Create a new feature branch
git checkout -b feature/your-feature-name

# Make your changes and commit
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples**:
```
feat(auth): add anonymous session creation endpoint
fix(matching): correct skill scoring algorithm
docs(roadmap): update Q1 2025 milestones
test(api): add integration tests for session endpoint
```

---

## Code Standards

### Python (Backend)

**Style Guide**: Follow [PEP 8](https://pep8.org/)

```python
# Good: Type hints, docstrings, clear naming
from typing import Optional
from pydantic import BaseModel

class SessionCreate(BaseModel):
    """Request model for creating anonymous session."""
    anonymous_id: Optional[str] = None
    preferences: dict = {}

async def create_session(data: SessionCreate) -> Session:
    """
    Create a new anonymous session.
    
    Args:
        data: Session creation data
        
    Returns:
        Created session object
    """
    # Implementation
    pass
```

**Tools**:
- **Linter**: `flake8`
- **Formatter**: `black`
- **Type Checker**: `mypy`

```powershell
# Run checks
flake8 backend/
black backend/ --check
mypy backend/
```

### TypeScript (Frontend)

**Style Guide**: Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)

```typescript
// Good: Type safety, clear interfaces, functional components
interface SessionData {
  anonymousId: string;
  preferences: Record<string, unknown>;
}

export async function createSession(data: SessionData): Promise<Session> {
  const response = await fetch('/api/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error('Failed to create session');
  }
  
  return response.json();
}
```

**Tools**:
- **Linter**: ESLint
- **Formatter**: Prettier
- **Type Checker**: TypeScript

```powershell
# Run checks
npm run lint
npm run type-check
```

### Architecture Principles

#### 1. Anonymous-First
```python
# ✅ Good: No identity required
def assess_capabilities(anonymous_id: str, portfolio: dict) -> Assessment:
    pass

# ❌ Bad: Requires identity
def assess_capabilities(email: str, name: str, portfolio: dict) -> Assessment:
    pass
```

#### 2. Capability Over Credentials
```python
# ✅ Good: Focus on skills
skills = ["Python", "FastAPI", "PostgreSQL"]
assessment = skill_assessor.evaluate(skills)

# ❌ Bad: Focus on credentials
if user.has_degree and user.years_experience > 5:
    pass
```

#### 3. Human-in-the-Loop
```python
# ✅ Good: Queue for review
ai_decision = matching_engine.match(candidate, job)
review_queue.add(ai_decision, requires_human_approval=True)

# ❌ Bad: Automatic execution
ai_decision = matching_engine.match(candidate, job)
ai_decision.execute()  # No human review
```

---

## Testing Requirements

### Backend Tests

**Framework**: pytest

```python
# tests/test_session.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_anonymous_session():
    """Test anonymous session creation."""
    response = client.post("/api/session", json={
        "preferences": {"role": "developer"}
    })
    assert response.status_code == 201
    assert "anonymous_id" in response.json()
```

**Run Tests**:
```powershell
# All tests
pytest

# Specific test
pytest tests/test_session.py

# With coverage
pytest --cov=backend --cov-report=html
```

### Frontend Tests

**Framework**: Jest + React Testing Library

```typescript
// components/__tests__/SessionForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import SessionForm from '../SessionForm';

describe('SessionForm', () => {
  it('creates anonymous session on submit', async () => {
    render(<SessionForm />);
    
    const submitButton = screen.getByRole('button', { name: /create session/i });
    fireEvent.click(submitButton);
    
    expect(await screen.findByText(/session created/i)).toBeInTheDocument();
  });
});
```

**Run Tests**:
```powershell
npm test
npm run test:coverage
```

### Coverage Requirements
- **Backend**: Minimum 80% coverage
- **Frontend**: Minimum 70% coverage
- **Critical paths**: 100% coverage (authentication, payments, matching)

---

## Pull Request Process

### Before Submitting

1. **Update your branch**:
   ```powershell
   git checkout develop
   git pull upstream develop
   git checkout feature/your-feature
   git rebase develop
   ```

2. **Run all checks**:
   ```powershell
   # Backend
   pytest
   flake8 backend/
   black backend/ --check
   mypy backend/
   
   # Frontend
   npm run lint
   npm run type-check
   npm test
   ```

3. **Update documentation**:
   - Update README.md if needed
   - Update ROADMAP.md if completing milestone items
   - Add/update API documentation
   - Update CHANGELOG.md

### Creating the PR

1. Push to your fork: `git push origin feature/your-feature`
2. Open PR against `develop` branch (not `main`)
3. Fill out the PR template completely
4. Link related issues using keywords: `Closes #123`, `Fixes #456`
5. Request review from relevant maintainers

### PR Template Checklist

- [ ] Tests added/updated and passing
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Commits follow conventional format
- [ ] Branch is up-to-date with develop
- [ ] Screenshots added (for UI changes)

### Review Process

- **Reviews Required**: Minimum 1 approval
- **CI/CD**: All checks must pass
- **Merge Strategy**: Squash and merge (for clean history)
- **Response Time**: Expect feedback within 48 hours

---

## Issue Guidelines

### Before Creating an Issue

1. Search existing issues to avoid duplicates
2. Check ROADMAP.md to see if it's already planned
3. Verify it's not a local environment issue

### Issue Types

#### Bug Report
```markdown
**Description**: Brief description of the bug

**Steps to Reproduce**:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Environment**:
- OS: Windows 11
- Browser: Chrome 120
- Node.js: 20.10.0
- Python: 3.11.5

**Additional Context**: Screenshots, logs, etc.
```

#### Feature Request
```markdown
**Problem Statement**: What problem does this solve?

**Proposed Solution**: How should it work?

**Alternatives Considered**: Other approaches you've thought of

**Additional Context**: Mockups, references, etc.
```

### Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `priority: high`: Critical issue
- `wontfix`: This will not be worked on

---

## Documentation

### Documentation Standards

1. **Code Comments**: Explain "why", not "what"
2. **Docstrings**: Required for all public functions
3. **README Updates**: Keep in sync with code changes
4. **API Documentation**: OpenAPI/Swagger for all endpoints

### Writing Documentation

```python
# Good: Explains reasoning
# We use Redis for session storage because PostgreSQL
# can't handle the high-frequency session updates
session_cache = RedisCache()

# Bad: States the obvious
# Create Redis cache
session_cache = RedisCache()
```

---

## Claude Code Hooks

This project uses Claude Code hooks for AI-assisted development.

### Available Hooks

1. **`generate_capability_flow`**: Generate capability assessment workflows
2. **`xdmiq_questions`**: Load XDMIQ preference questions
3. **`identity_proxy`**: Implement anonymous identity patterns
4. **`platform_health`**: Generate health check endpoints
5. **`ollama_migration`**: Migrate from OpenAI to Ollama
6. **`checkpoint_workflow`**: Implement state checkpoint patterns

### Using Hooks

```powershell
# Load context for a task
python .claude-code/context-loader.py --hook api_endpoint "Create session endpoint"

# View hook examples
python .claude-code/context-loader.py --example generate_capability_flow

# Dry run with output limit
python .claude-code/context-loader.py --dry-run --limit 20 --hook xdmiq_questions
```

### Hook Guidelines

- Always load relevant hooks before AI-assisted coding
- Follow patterns defined in prompt templates
- Validate output against invariants checklist
- See `.claude-code/README.md` for detailed usage

---

## Questions or Help?

- **General Questions**: Open a discussion in GitHub Discussions
- **Bug Reports**: Create an issue with `bug` label
- **Feature Ideas**: Create an issue with `enhancement` label
- **Security Issues**: Email security@jobmatch.zip (do not create public issue)

---

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for their contributions
- GitHub contributor statistics

Thank you for contributing to JobMatch.Zip! 🎉
