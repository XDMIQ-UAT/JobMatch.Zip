# XDMIQ - Question Banks and Scoring

This folder contains XDMIQ (AI-native credentialing) question banks and scoring configurations.

## Purpose

Manage preference-based assessment questions:
- **Question Banks**: Preference questions organized by domain
- **Scoring**: Methodology for calculating XDMIQ scores (0-100)
- **Question Format**: "Which do you prefer?" + "Why?"

## Key Principles

- **Preference-Based**: Questions assess preferences, not credentials
- **Capability-Focused**: Reveal what users CAN DO, not who they ARE
- **Anonymous-Friendly**: Questions don't require identity information
- **Transparent Scoring**: Scoring methodology is explainable

## Files

- `questions/` - Question bank YAML files organized by domain
- `scoring.md` - Scoring methodology documentation

## Question Format

Every question follows this structure:
1. **Preference Question**: "Which do you prefer?"
2. **Reasoning Question**: "Why?"

### Example
```yaml
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

## Scoring Schema

- **Overall Score**: 0-100 (aggregate of all domains)
- **Proficiency Score**: 0-100 (technical capability)
- **Reasoning Score**: 0-100 (quality of "why" responses)
- **Adaptability Score**: 0-100 (preference diversity)

## Constraints

- Questions MUST NOT ask for personal information
- Questions MUST assess capability/preference, not credentials
- Scoring MUST be transparent and explainable
- Questions MUST reveal what user CAN DO, not who they ARE

## Related Code

- `backend/assessment/xdmiq_assessment.py` - XDMIQ assessment engine
- `backend/api/xdmiq.py` - XDMIQ API endpoints
- `.claude-code/prompts/xdmiq_questions.md` - Question generation prompts

