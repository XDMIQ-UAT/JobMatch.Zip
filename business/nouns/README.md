# Nouns - Entities

This folder contains definitions of entities in the platform: capabilities, roles, and jobs.

## Purpose

Define the core entities that the platform works with:
- **Capabilities**: What users can do (skills, proficiencies, demonstrated abilities)
- **Roles**: Job roles and positions available in the marketplace
- **Jobs**: Specific job postings and opportunities

## Key Principles

- **Capability-First**: Focus on what users CAN DO, not credentials
- **Anonymous-Friendly**: Entity definitions don't require identity information
- **Preference-Based**: Capabilities assessed through preference questions (XDMIQ)

## Files

- `capabilities.yaml` - Capability taxonomy and definitions
- `roles.yaml` - Role definitions and requirements
- `jobs.yaml` - Job posting templates (if needed)

## Usage

Entities defined here are used by:
- Matching engine (`backend/ai/matching_engine.py`)
- Capability assessment (`backend/assessment/capability_assessment.py`)
- XDMIQ scoring (`backend/assessment/xdmiq_assessment.py`)

## Example Capability Structure

```yaml
capabilities:
  - id: ai-tool-proficiency
    name: AI Tool Proficiency
    description: Ability to work with AI tools and frameworks
    domains:
      - OpenAI API
      - Anthropic Claude
      - Local LLMs (Ollama)
    assessment_method: xdmiq + portfolio
```

