# Stateless Workflow System

## Overview

This directory contains **stateless workflow definitions** for the agent system. These workflows can be turned on/off without losing logic or requiring rebuilds.

## Key Principles

### ✅ Stateless Design

- **No persistent state**: Each workflow execution is independent
- **No memory**: Workflows don't remember previous runs
- **Self-contained**: All context included in each execution
- **Version controlled**: Workflows stored in Git, not databases

### ✅ Declarative Configuration

Workflows are defined as **YAML configuration files** that describe:
- **What** should happen (not how)
- **Which agents** to use
- **What commands** to execute
- **What conditions** to check

### ✅ Safe Shutdown

To turn off a workflow:
1. Set `enabled: false` in the workflow definition
2. Remove or disable triggers
3. Stop the execution engine

**No data loss** - workflows are stateless, so turning them off doesn't lose logic.

## Workflow Structure

```yaml
workflow-name:
  name: "Human Readable Name"
  description: "What this workflow does"
  enabled: true  # Set to false to disable
  version: "1.0.0"
  
  triggers:
    - type: "manual" | "file_change" | "webhook" | "git_push"
      # Trigger configuration
  
  steps:
    - id: "step-1"
      agent: "agent-name"
      command: "command-name"
      inputs:
        # Input parameters
      outputs:
        # Output variables
      condition: "optional condition"
  
  outputs:
    # Final workflow outputs
```

## Available Workflows

### 1. Branding Review Workflow
- **File**: `stateless-workflows.yaml` → `branding-review`
- **Purpose**: Automated branding review for product names
- **Agents**: `branding-agent`, `alert-agent`, `i18n-agent`
- **Trigger**: Manual or file changes

### 2. Copy Review Workflow
- **File**: `stateless-workflows.yaml` → `copy-review`
- **Purpose**: Automated copy review for documentation and UI
- **Agents**: `copy-review-agent`, `i18n-agent`, `alert-agent`
- **Trigger**: Manual or file changes

### 3. Pre-Deployment Check Workflow
- **File**: `stateless-workflows.yaml` → `pre-deployment`
- **Purpose**: Validate system readiness before deployment
- **Agents**: `precheck-agent`, `alert-agent`
- **Trigger**: Manual or Git push to main

### 4. Security Review Workflow
- **File**: `stateless-workflows.yaml` → `security-review`
- **Purpose**: Comprehensive security review for code changes
- **Agents**: `crypto-agent`, `threat-model-agent`, `alert-agent`
- **Trigger**: Manual or file changes

### 5. Call Handling Workflow
- **File**: `stateless-workflows.yaml` → `call-handling`
- **Purpose**: Handle incoming phone calls and route appropriately
- **Agents**: `dash-agent`, `alert-agent`
- **Trigger**: Twilio webhook

## Usage

### Enable/Disable Workflows

Edit `stateless-workflows.yaml` and set `enabled: false` for any workflow:

```yaml
branding-review:
  enabled: false  # Workflow is now disabled
```

### Execute Workflows

#### Manual Execution (via Cursor)

```bash
# Execute branding review workflow
@workflow-engine execute branding-review --name "MyProduct" --item_type "product_name"

# Execute pre-deployment checks
@workflow-engine execute pre-deployment
```

#### Trigger-Based Execution

Workflows automatically execute when triggers fire:
- **File changes**: Monitors file system for changes
- **Webhooks**: Responds to HTTP POST requests
- **Git events**: Triggers on push/merge events

### View Workflow Status

```bash
# List all workflows
@workflow-engine list

# Show workflow details
@workflow-engine show branding-review

# Check workflow execution history (monitoring only)
@workflow-engine logs branding-review
```

## Workflow Engine

The workflow engine is **stateless**:
- No database required
- No persistent state storage
- Each execution is independent
- Can be stopped/started without data loss

### Engine Configuration

See `stateless-workflows.yaml` → `engine` section for configuration:
- Execution mode: `stateless`
- Timeout: 300 seconds
- Retry: 3 attempts with exponential backoff
- Storage: `none` (stateless)

## Adding New Workflows

1. **Create workflow definition** in `stateless-workflows.yaml`:

```yaml
my-new-workflow:
  name: "My New Workflow"
  description: "What it does"
  enabled: true
  version: "1.0.0"
  
  triggers:
    - type: "manual"
  
  steps:
    - id: "step-1"
      agent: "my-agent"
      command: "my-command"
      inputs:
        param1: "{{ input.value }}"
  
  outputs:
    result: "{{ step-1.output }}"
```

2. **Test workflow**:
```bash
@workflow-engine execute my-new-workflow --value "test"
```

3. **Commit to Git** - workflows are version controlled

## Best Practices

1. **Keep workflows stateless** - Don't rely on previous executions
2. **Use version control** - All workflows in Git
3. **Include all context** - Each execution should be self-contained
4. **Use conditions** - Make workflows flexible with conditional steps
5. **Monitor execution** - Use logs for debugging (not for state)

## Troubleshooting

### Workflow Not Executing

1. Check `enabled: true` in workflow definition
2. Verify triggers are configured correctly
3. Check agent availability: `@workflow-engine check-agents`

### Workflow Failing

1. Check workflow logs: `@workflow-engine logs <workflow-name>`
2. Verify agent commands exist
3. Check input parameters match expected format
4. Review condition expressions

### Turning Off Workflows Safely

1. Set `enabled: false` in workflow definition
2. Workflow will not execute but definition remains
3. No data loss - can re-enable anytime
4. Commit changes to Git for version control

## Related Files

- `stateless-workflows.yaml` - Workflow definitions
- `../agents/agents-registry.json` - Agent registry
- `../agents/*.json` - Individual agent configurations

