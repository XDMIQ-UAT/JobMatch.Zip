# Prompt Optimization Guide

## Overview

This guide codifies prompt optimization strategies for capability-first, anonymous-identity development using Claude Code hooks with Warp and Cursor.

## Core Principles

### 1. Capability-First Prompting

**Principle**: Focus on what users CAN DO, not who they ARE.

**Pattern**:
```
❌ Bad: "Create a user profile page that shows name, email, and job history"
✅ Good: "Create a capability assessment interface that captures skills and preferences anonymously"
```

**Why**: Separating capability from identity is fundamental to the platform architecture. Prompts that conflate the two will generate code that violates privacy-by-default principles.

### 2. Example-Driven Context

**Principle**: Always provide concrete examples from the codebase.

**Pattern**:
```
❌ Bad: "Create an API endpoint"
✅ Good: "Create an API endpoint following the pattern in backend/api/auth.py:
         - Use Pydantic models
         - Include error handling
         - Maintain anonymous identity
         - Reference: backend/api/xdmiq.py for assessment patterns"
```

**Why**: Examples ground the AI in existing patterns, ensuring consistency and reducing need for rework.

### 3. Constraints and Invariants

**Principle**: State what MUST NOT change alongside what should change.

**Pattern**:
```
✅ Good: "Add matching score calculation to the assessment flow.
         CONSTRAINTS:
         - Must not expose user identity
         - Must create state checkpoint before calculation
         - Must support rollback if calculation fails
         - Must log decision for human review"
```

**Why**: Invariants prevent accidental violations of core principles (anonymous-first, human-in-the-loop, state recovery).

### 4. Safety Guardrails

**Principle**: Every prompt should reinforce privacy and security boundaries.

**Mandatory Guardrails**:
1. **Anonymous-First**: Never generate code that reveals user identity without explicit consent
2. **No Identity Leakage**: Avoid logging, analytics, or error messages that could correlate anonymous IDs with real identities
3. **Human-in-the-Loop**: AI decisions must queue for human review
4. **State Checkpoints**: Operations that change state must create checkpoints first

## Prompt Templates

### For API Endpoints

```
Context: Creating [endpoint purpose]
Pattern: backend/api/[reference].py
Requirements:
- FastAPI route with Pydantic models
- Anonymous identity maintained (use anonymous_id from session)
- Error handling with appropriate HTTP status codes
- State checkpoint if modifying data
- Human review queue if AI decision involved

Example:
POST /api/assess/capability
- Accept anonymous_id + capability_data
- Validate capability_data (Pydantic)
- Create checkpoint
- Store assessment
- Return assessment_id (anonymous)

Constraints:
- NEVER expose user identity
- NEVER skip checkpoint for state changes
- ALWAYS log AI decisions for review
```

### For XDMIQ Questions

```
Context: Generating preference-based assessment questions
Pattern: backend/assessment/xdmiq_assessment.py
Format: "Which do you prefer?" + "Why?"

Requirements:
- Questions reveal capability preferences, NOT identity
- Scoring is 0-100 scale
- Multiple questions per capability domain
- Questions stored in business/xdmiq/questions.yaml

Example:
Domain: Problem Solving
Question: "Which approach do you prefer when facing a complex technical problem?"
Options:
  A: Break it into smaller sub-problems
  B: Research similar solutions first
  C: Prototype quickly and iterate
  D: Diagram the system before coding
Follow-up: "Why does this approach work better for you?"

Constraints:
- Questions MUST NOT ask for personal information
- Questions MUST assess capability/preference, not credentials
- Scoring MUST be transparent and explainable
```

### For Identity Proxy Flows

```
Context: Managing anonymous sessions and voluntary identification
Pattern: backend/auth/anonymous_identity.py
Architecture: Zero-knowledge (platform cannot link anonymous_id to real identity)

Requirements:
- Generate cryptographically secure anonymous_id
- Store session data keyed by anonymous_id
- Support multiple personas per real identity (if user creates them)
- Voluntary identification is separate flow (never required)

Example Flow:
1. User visits site → generate anonymous_id → create session
2. User completes assessments → store keyed by anonymous_id
3. User gets job matches → display to anonymous_id
4. (Optional) User volunteers identity → link to anonymous_id in separate table with user consent
5. Platform never correlates anonymous_id → real identity without explicit user action

Constraints:
- Platform CANNOT reverse-engineer identity from anonymous_id
- Sessions MUST work without any identity information
- Voluntary identification MUST be opt-in, never required
- Identity linking MUST be user-initiated, with clear consent UI
```

### For Platform Health Checks

```
Context: Creating health check or monitoring
Pattern: business/health/checks.yaml
Purpose: Operational visibility without compromising user privacy

Requirements:
- Monitor system health (DB, Redis, Elasticsearch, Ollama)
- Track business metrics (matches, assessments, checkpoint success)
- Aggregate data only (no individual user tracking)
- Dashboards for ops team

Example Metrics:
- anonymous_sessions_active: count (no IDs)
- assessments_completed_today: count
- matches_generated_last_hour: count
- checkpoint_success_rate: percentage
- human_review_queue_depth: count
- ollama_response_time_p99: milliseconds

Constraints:
- NEVER log individual anonymous_ids in metrics
- NEVER correlate metrics across users
- Aggregate only (counts, percentages, distributions)
- Privacy-preserving monitoring
```

## Anti-Patterns to Avoid

### ❌ Identity-First Thinking

**Bad**:
```
"Create a user profile page with name, email, photo, and resume"
```

**Why Bad**: Assumes identity is required up-front. Violates anonymous-first principle.

**Fix**:
```
"Create a capability profile interface that shows:
- Assessed capabilities (from XDMIQ)
- Skill preferences
- Match criteria
- Anonymous session ID
- (Optional) Voluntary identity if user has provided it"
```

### ❌ Skipping Checkpoints

**Bad**:
```
"Update the matching algorithm to use new scoring formula"
```

**Why Bad**: No checkpoint, no rollback, state corruption risk.

**Fix**:
```
"Update the matching algorithm:
1. Create checkpoint of current algorithm state
2. Deploy new scoring formula
3. Run validation suite
4. If validation fails, rollback to checkpoint
5. Log results for human review"
```

### ❌ Credentials Over Capabilities

**Bad**:
```
"Parse resume and extract job titles, companies, degrees"
```

**Why Bad**: Assumes credentials matter. Platform is capability-first.

**Fix**:
```
"Extract capability signals from unstructured text:
- Skills mentioned (technical and soft)
- Problem types solved
- Tools/technologies used
- Preferences indicated
Map to capability taxonomy, not job titles"
```

### ❌ Automatic AI Decisions

**Bad**:
```
"Auto-match users with jobs based on AI score"
```

**Why Bad**: Bypasses human-in-the-loop. No human review.

**Fix**:
```
"Generate AI-powered match candidates:
1. Calculate match scores (AI)
2. Create checkpoint
3. Queue top matches for human review
4. Human reviewer approves/rejects
5. Only approved matches sent to users
Human-in-the-loop always more beneficial"
```

## Prompt Hygiene Checklist

Before submitting a prompt to Claude Code, verify:

- [ ] **Context Loaded**: Used `--hook` or `--example` flag to load project context
- [ ] **Examples Referenced**: Cited at least one existing file as pattern
- [ ] **Constraints Stated**: Listed what MUST NOT change
- [ ] **Invariants Clear**: Specified anonymous-first, checkpoint, human-review requirements
- [ ] **Privacy Checked**: No identity leakage in proposed solution
- [ ] **Capability-First**: Focused on what user CAN DO, not who they ARE
- [ ] **Human-in-the-Loop**: AI decisions queued for review
- [ ] **State Recovery**: Checkpoints for state-changing operations

## Integration with Tools

### Using with Warp

```powershell
# Load context for a task
python .claude-code\context-loader.py --hook api_endpoint "Create matching endpoint"

# Show examples for a hook type
python .claude-code\context-loader.py --example xdmiq_questions
```

### Using with Cursor

1. Open `.cursorrules` in project root
2. Cursor AI will auto-load these patterns
3. When requesting code generation, reference hook types:
   - "Generate an API endpoint [api_endpoint hook]"
   - "Create XDMIQ questions [xdmiq_questions hook]"

### Using with Claude Code

1. Run context-loader to build prompt context
2. Copy output as context prefix to Claude Code
3. Add your specific task
4. Claude Code generates code following patterns

## Optimization Workflow

### Daily Loop

1. **Morning**: Review overnight human review queue
2. **Development**: Use hooks for all code generation
3. **Testing**: Run checkpoint tests before committing
4. **Evening**: Create system checkpoint

### Code Generation Pattern

```
1. Identify task → Select hook type
2. Load context → python .claude-code\context-loader.py --hook [type]
3. Add task details → Append to context
4. Generate code → Claude Code / Cursor
5. Validate → Check against invariants
6. Commit → Include hook reference in commit message
```

### Example Commit Message

```
feat(api): Add capability assessment endpoint [api_endpoint]

Generated using api_endpoint hook with constraints:
- Anonymous identity maintained
- State checkpoint before storage
- Human review queue for AI scores

References: backend/api/auth.py, backend/api/xdmiq.py
```

## Advanced Techniques

### Multi-Hook Composition

For complex features spanning multiple concerns:

```
Task: Build end-to-end capability assessment flow

Hooks:
1. api_endpoint → API routes
2. database_model → Assessment storage schema
3. frontend_component → Assessment UI
4. xdmiq_questions → Question generation
5. identity_proxy → Session management

Sequence:
1. Generate questions (xdmiq_questions)
2. Create database schema (database_model)
3. Build API (api_endpoint)
4. Create UI (frontend_component)
5. Wire up identity (identity_proxy)
```

### Constraint Layering

For high-risk operations, layer constraints:

```
Task: Deploy new matching algorithm

Constraints (Layer 1 - Safety):
- Must create checkpoint
- Must support rollback
- Must queue for human review

Constraints (Layer 2 - Privacy):
- Must not expose user identity
- Must not log individual anonymous_ids
- Must aggregate metrics only

Constraints (Layer 3 - Business):
- Must maintain match quality > 80%
- Must complete < 100ms p99
- Must scale to 1M users
```

## Troubleshooting

### "AI generated identity-exposing code"

**Fix**: Add explicit constraint:
```
"CONSTRAINT: This feature must work with zero knowledge of user identity.
Anonymous_id is only identifier available. Platform cannot reverse-engineer identity."
```

### "Code skipped checkpoint creation"

**Fix**: Make checkpoint explicit in prompt:
```
"Step 1: Create checkpoint using state_manager.create_checkpoint()
Step 2: Perform operation
Step 3: If success, commit; if failure, restore checkpoint"
```

### "Generated credential-based logic"

**Fix**: Reframe as capability-first:
```
"Focus on capabilities, NOT credentials:
- Extract skills (what they CAN DO)
- Assess preferences (what they PREFER)
- Measure proficiency (how WELL they do it)
Do NOT extract job titles, company names, degree names"
```

## Conclusion

Prompt optimization is about **encoding invariants** into every interaction with AI coding tools. By following these patterns, you ensure generated code:

1. Respects user privacy (anonymous-first)
2. Maintains system resilience (checkpoints, human-review)
3. Focuses on capabilities (not credentials)
4. Scales sustainably (state recovery, monitoring)

**Remember**: The prompt is the specification. Make it precise, example-driven, and constraint-rich.

