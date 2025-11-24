# Capability Assessment Prompt Template

## Context

Creating capability-first assessment flows that evaluate what users CAN DO, not their credentials.

## Pattern

Reference: `backend/assessment/capability_assessment.py`

## Requirements

- Assess practical AI tool proficiency
- Portfolio-based evaluation (work samples, code, projects)
- Practical challenges demonstrating real capabilities
- Human-in-the-loop validation for edge cases
- State checkpoints for assessment results

## Example Structure

```python
class CapabilityAssessment:
    """
    Assesses user capabilities in AI tools and practical problem-solving.
    Focus: What they CAN DO, not credentials.
    """
    
    def assess_ai_proficiency(self, user_id: str, portfolio_data: dict):
        """
        Assess AI tool proficiency from portfolio.
        
        Steps:
        1. Extract capability signals (skills, tools, problem types)
        2. Map to capability taxonomy
        3. Score proficiency (0-100)
        4. Create checkpoint
        5. Queue for human review if score ambiguous
        """
```

## Constraints

- MUST NOT require credentials (degrees, job titles, company names)
- MUST focus on demonstrated capabilities (projects, code, work samples)
- MUST create state checkpoint before storing assessment
- MUST queue ambiguous assessments for human review
- MUST maintain anonymous identity throughout

## Capability Taxonomy

Focus areas:
- AI Tool Proficiency (OpenAI, Anthropic, local LLMs)
- Problem-Solving Approach (preference-based via XDMIQ)
- Technical Skills (extracted from portfolio, not resumes)
- Practical Experience (what they've built, not where they worked)

## Integration Points

- XDMIQ Assessment: Preference-based questions inform capability scoring
- Anonymous Identity: All assessments keyed by anonymous_id
- Human Review: Edge cases queued for human validation
- State Recovery: Assessment results stored as checkpoints

