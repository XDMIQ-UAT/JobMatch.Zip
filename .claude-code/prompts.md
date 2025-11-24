# Claude Code Prompt Architecture

## Optimized Prompts for Development

### API Endpoint Generation

**Prompt Template:**
```
Create a FastAPI endpoint for [FEATURE] that:
- Follows existing patterns in backend/api/
- Uses Pydantic models for request/response validation
- Maintains anonymous identity (user_id parameter)
- Includes proper error handling (HTTPException)
- Adds to appropriate router
- Supports human-in-the-loop where applicable
- Creates state checkpoints for AI decisions

Reference examples:
- backend/api/xdmiq.py (XDMIQ assessment)
- backend/api/social_auth.py (authentication)
- backend/api/matching.py (matching engine)
```

### Database Model Creation

**Prompt Template:**
```
Create a SQLAlchemy model for [ENTITY] that:
- Inherits from Base (backend.database.models)
- Uses proper column types (String, Integer, DateTime, JSON, etc.)
- Includes relationships if needed
- Adds indexes for performance (user_id, created_at, etc.)
- Supports anonymous identity (user_id foreign key)
- Includes metadata JSON field for extensibility

Reference: backend/database/models.py
```

### Frontend Component Generation

**Prompt Template:**
```
Create a Next.js component for [FEATURE] that:
- Uses TypeScript with proper types
- Follows capability-first design principles
- Maintains accessibility (WCAG AAA)
- Uses design tokens from frontend/components/CapabilityDesign.tsx
- Supports anonymous user flow
- Handles loading and error states
- Uses 'use client' directive if needed

Reference examples:
- frontend/app/xdmiq/page.tsx (assessment interface)
- frontend/app/auth/page.tsx (authentication)
- frontend/components/CapabilityDesign.tsx (design system)
```

### AI Feature Integration

**Prompt Template:**
```
Create an AI feature for [FEATURE] that:
- Includes human-in-the-loop architecture
- Creates state checkpoints (StateManager)
- Supports rollback/recovery
- Uses OpenAI API with fallback logic
- Logs AI decisions for human review
- Integrates with human review queue
- Follows existing AI patterns

Reference examples:
- backend/ai/matching_engine.py
- backend/assessment/xdmiq_assessment.py
- backend/ai/articulation_assistant.py
```

### Testing & Debugging

**Prompt Template:**
```
Create tests for [FEATURE] that:
- Test happy path and error cases
- Verify anonymous identity preservation
- Test state recovery mechanisms
- Validate human-in-the-loop workflows
- Use pytest for backend, Jest for frontend

Reference: backend/testing/simulation.py
```

## Context Injection Hooks

### Before Code Generation
- Load project structure
- Read relevant example files
- Understand existing patterns
- Check for similar implementations

### During Code Generation
- Maintain consistency with codebase
- Follow established conventions
- Include proper error handling
- Add necessary documentation

### After Code Generation
- Verify integration points
- Check for missing dependencies
- Ensure state management
- Validate anonymous identity flow

## Optimization Tips

1. **Be Specific**: Include exact requirements and constraints
2. **Reference Examples**: Point to similar code in the codebase
3. **Maintain Patterns**: Follow existing architectural patterns
4. **Consider Scale**: Think about 1B+ user scalability
5. **Human Oversight**: Always include human review mechanisms


