# Cursor Agents Quick Start Guide

## Overview

This directory contains Cursor agent configurations based on your E:\agents folder structure. These agents can help you with specialized tasks across your development workflow.

## How to Use Agents in Cursor

### Basic Usage

In Cursor, you can reference agents using the `@` symbol:

```
@agent-name [command] [parameters]
```

### Examples

**Strategic Planning:**
```
@fractional-ceo-agent strategic_review
@fractional-ceo-agent board_prep
```

**Financial Analysis:**
```
@fractional-cfo-agent financial_health
@fractional-cfo-agent budget_review
@fractional-cfo-agent fundraising_prep
```

**Development:**
```
@principal-dev-agent review
@principal-dev-agent analyze
@principal-dev-agent assess_debt
@principal-dev-agent security_scan
```

**Project Management:**
```
@git-project-manager-agent scan_repos
@git-project-manager-agent sync_issues
@git-project-manager-agent health_check
@project-manager-agent sprint_status
@project-manager-agent daily_standup
@project-manager-agent manage_blockers
```

**Operations:**
```
@fractional-coo-agent operations_check
@fractional-coo-agent okr_review
@fractional-coo-agent process_audit
@change-management-agent assess
@change-management-agent healthcheck
```

**Specialized:**
```
@historian-agent record
@historian-agent entity --name project-name
@link-validation-agent validate --url https://example.com
@data-governance-agent [compliance checks]
```

## Agent Categories

### C-Suite Agents
- **fractional-ceo-agent**: Strategic leadership and executive decisions
- **fractional-cfo-agent**: Financial strategy and planning
- **fractional-coo-agent**: Operational excellence and execution

### Development Agents
- **principal-dev-agent**: High-level architecture and complex development
- **dev-sync-agent**: Coordinate parallel development across tools
- **review-agent**: Code and document review

### Project Management Agents
- **git-project-manager-agent**: GitHub/GitLab project management
- **project-manager-agent**: Tactical project execution and sprints
- **program-manager-agent**: Strategic program coordination
- **product-agent**: Product management and feature coordination

### Operations Agents
- **change-management-agent**: Change velocity and governance
- **infrastructure-agent**: Environment and deployment management

### Specialized Agents
- **historian-agent**: Documentation and narrative history
- **data-governance-agent**: Compliance and data stewardship
- **link-validation-agent**: URL validation and testing

## Agent Integration

Agents are designed to work together. For example:

- **CEO Agent** coordinates with **CFO** and **COO** agents
- **Project Manager** syncs with **Git Project Manager** and **Product** agents
- **Change Management** coordinates with all agents for change velocity

## Configuration Files

Each agent has a JSON configuration file in this directory:
- `fractional-ceo-agent.json`
- `fractional-cfo-agent.json`
- `fractional-coo-agent.json`
- `principal-dev-agent.json`
- `git-project-manager-agent.json`
- `project-manager-agent.json`
- `program-manager-agent.json`
- `product-agent.json`
- `change-management-agent.json`
- `historian-agent.json`
- `data-governance-agent.json`
- `dev-sync-agent.json`
- `infrastructure-agent.json`
- `review-agent.json`
- `link-validation-agent.json`

## Registry

See `agents-registry.json` for the complete list of all available agents and their metadata.

## Notes

- Agents reference scripts and tools from `E:\agents\` directory
- Some agents require Python scripts to be available
- PowerShell scripts are used for Windows-specific operations
- Agent outputs are typically written to `E:\agents\reports\` or `E:\agents\logs\`

## Next Steps

1. Review the agent configurations in this directory
2. Try invoking agents using the `@agent-name` syntax
3. Check agent outputs in `E:\agents\reports\`
4. Customize agent configurations as needed for your workflow

