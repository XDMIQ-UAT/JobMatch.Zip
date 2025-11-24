# Verbs - Actions

This folder contains definitions of actions and operations in the platform: assess, match, notify, and other platform verbs.

## Purpose

Define the core actions that the platform performs:
- **Assess**: Evaluate user capabilities through XDMIQ and portfolio analysis
- **Match**: Connect users with opportunities based on capability alignment
- **Notify**: Send notifications and updates to users
- **Articulate**: Help users express their capabilities clearly

## Key Principles

- **Anonymous-First**: All actions work with anonymous IDs
- **Capability-Focused**: Actions evaluate what users CAN DO
- **Human-in-the-Loop**: AI decisions queue for human review
- **State Checkpoints**: State-changing actions create checkpoints

## Files

- `actions.yaml` - Action definitions and workflows

## Usage

Actions defined here are used by:
- API endpoints (`backend/api/`)
- AI matching engine (`backend/ai/matching_engine.py`)
- Assessment flows (`backend/assessment/`)
- Notification systems

## Example Action Structure

```yaml
actions:
  - id: assess_capability
    name: Assess User Capability
    workflow:
      - start_xdmiq_assessment
      - collect_portfolio_data
      - generate_capability_score
      - create_checkpoint
      - queue_for_human_review_if_needed
    anonymous_id_required: true
    creates_checkpoint: true
```

