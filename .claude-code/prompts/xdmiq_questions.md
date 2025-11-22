# XDMIQ Questions Prompt Template

## Context

Generating preference-based assessment questions for XDMIQ AI-native credentialing system.

## Pattern

Reference: `backend/assessment/xdmiq_assessment.py`, `business/xdmiq/questions.yaml`

## Question Format

Every question follows this structure:

1. **Preference Question**: "Which do you prefer?"
2. **Reasoning Question**: "Why?"

## Example Questions

### Domain: Problem-Solving Approach

**Question 1:**
- Text: "Which approach do you prefer when facing a complex technical problem?"
- Options:
  - A: Break it into smaller sub-problems
  - B: Research similar solutions first
  - C: Prototype quickly and iterate
  - D: Diagram the system before coding
- Follow-up: "Why does this approach work better for you?"

### Domain: AI Tool Usage

**Question 2:**
- Text: "Which do you prefer when working with AI tools?"
- Options:
  - A: Using pre-built models and APIs
  - B: Fine-tuning models for specific tasks
  - C: Building custom architectures
  - D: Combining multiple AI approaches
- Follow-up: "What makes this approach more effective for your work?"

## Scoring Schema

- **Overall Score**: 0-100 (aggregate of all domains)
- **Proficiency Score**: 0-100 (technical capability)
- **Reasoning Score**: 0-100 (quality of "why" responses)
- **Adaptability Score**: 0-100 (preference diversity)

## Storage

Questions stored in: `business/xdmiq/questions.yaml`

```yaml
domains:
  - name: problem_solving
    questions:
      - id: 1
        text: "Which approach do you prefer..."
        options: [...]
        follow_up: "Why..."
```

## Constraints

- Questions MUST NOT ask for personal information
- Questions MUST assess capability/preference, not credentials
- Scoring MUST be transparent and explainable
- Questions MUST reveal what user CAN DO, not who they ARE

## Integration

- Used in matching algorithm to find capability-aligned opportunities
- Informs capability assessment scoring
- Stored anonymously (keyed by anonymous_id)

