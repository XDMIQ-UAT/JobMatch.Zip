# Stateless Workflow Quick Start

## What is Stateless Automation?

A **stateless system** doesn't remember past interactions. Each workflow execution is independent and self-contained. This means:

✅ **Safe to turn off** - No data loss when disabled  
✅ **No rebuilds needed** - Logic stored in version-controlled config files  
✅ **Easy to restart** - Just re-enable the workflow  
✅ **Scalable** - Can run multiple instances without state conflicts  

## Quick Examples

### 1. Execute a Workflow

```bash
# List available workflows
python .cursor/workflows/workflow-engine.py list

# Execute branding review workflow
python .cursor/workflows/workflow-engine.py execute branding-review --inputs '{"name": "MyProduct", "item_type": "product_name", "context": "New product launch"}'

# Execute pre-deployment checks
python .cursor/workflows/workflow-engine.py execute pre-deployment
```

### 2. Enable/Disable Workflows

Edit `.cursor/workflows/stateless-workflows.yaml`:

```yaml
branding-review:
  enabled: false  # Disable workflow
```

**That's it!** The workflow is now disabled. No data loss, no rebuilds needed.

### 3. Add a New Workflow

Add to `stateless-workflows.yaml`:

```yaml
my-workflow:
  name: "My Workflow"
  description: "Does something useful"
  enabled: true
  version: "1.0.0"
  
  triggers:
    - type: "manual"
  
  steps:
    - id: "step-1"
      agent: "my-agent"
      command: "my-command"
      inputs:
        param: "{{ input.value }}"
  
  outputs:
    result: "{{ step-1.output }}"
```

Commit to Git - workflow is now version controlled and ready to use!

## Key Concepts

| Concept | Description |
|--------|-------------|
| **Stateless** | No memory between executions |
| **Declarative** | Define what, not how |
| **Version Controlled** | Workflows in Git |
| **Safe Shutdown** | Set `enabled: false` |

## Benefits

1. **Turn off safely** - Set `enabled: false`, no data loss
2. **No rebuilds** - Logic in config files, not compiled code
3. **Version control** - All workflows tracked in Git
4. **Easy testing** - Each execution is independent
5. **Scalable** - Run multiple instances without conflicts

## Next Steps

- Read `README.md` for detailed documentation
- Check `stateless-workflows.yaml` for workflow examples
- Execute workflows using `workflow-engine.py`

