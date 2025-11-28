# Runbook: Stateless Workflow Recovery

## Overview

**Severity**: Medium  
**Impact**: Workflow execution failures may prevent automated processes from running  
**Detection**: Workflow execution errors, failed agent commands, monitoring alerts

## Symptoms

- Workflow execution returns errors
- Agent commands fail to execute
- Workflow logs show failures
- Automated processes stop working
- Workflow engine reports errors

## Diagnosis

### Step 1: Check Workflow Status

```bash
# List all workflows
python .cursor/workflows/workflow-engine.py list

# Show workflow details
python .cursor/workflows/workflow-engine.py show <workflow-id>
```

**Expected**: Workflow shows as enabled with valid steps  
**Issue**: Workflow disabled, missing steps, or invalid configuration

### Step 2: Verify Workflow Definition

```bash
# Check workflow YAML file
cat .cursor/workflows/stateless-workflows.yaml | grep -A 20 "<workflow-id>:"
```

**Expected**: Valid YAML with enabled: true and defined steps  
**Issue**: Syntax errors, missing sections, or disabled workflow

### Step 3: Check Agent Availability

```bash
# Verify agents are registered
cat .cursor/agents/agents-registry.json | grep -i "<agent-id>"

# Check agent config file exists
ls .cursor/agents/<agent-id>.json
```

**Expected**: Agent found in registry with valid config  
**Issue**: Agent missing, disabled, or config file missing

### Step 4: Review Workflow Logs

```bash
# Check execution logs (if monitoring enabled)
ls workflow-logs/<workflow-id>-*.json

# View latest log
cat workflow-logs/<workflow-id>-<timestamp>.json | jq .
```

**Expected**: Successful execution records  
**Issue**: Error messages, failed steps, or missing logs

## Resolution

### Immediate Actions

1. **Disable Workflow** (if causing issues)
   ```bash
   # Edit workflow file
   # Set enabled: false for the problematic workflow
   ```
   
   Edit `.cursor/workflows/stateless-workflows.yaml`:
   ```yaml
   <workflow-id>:
     enabled: false  # Temporarily disable
   ```

2. **Check Agent Status**
   ```bash
   # Verify agent is available
   @<agent-name> status
   ```

### Step-by-Step Resolution

1. **Identify Failed Step**
   - Review workflow logs
   - Identify which step failed
   - Check error messages

2. **Verify Agent Command**
   - Check agent config: `.cursor/agents/<agent-id>.json`
   - Verify command exists: `commands.<command-name>`
   - Check script path is valid

3. **Test Agent Command Manually**
   ```bash
   # Execute agent command directly
   python E:\agents\<agent-path>\<script>.py <command> <args>
   ```

4. **Fix Workflow Definition**
   - Update workflow YAML if needed
   - Fix input/output mappings
   - Correct condition expressions
   - Verify template variable syntax

5. **Re-enable Workflow**
   ```yaml
   <workflow-id>:
     enabled: true  # Re-enable after fixes
   ```

6. **Test Workflow Execution**
   ```bash
   # Execute workflow manually
   python .cursor/workflows/workflow-engine.py execute <workflow-id> --inputs '{}'
   ```

## Prevention

### Monitoring

- Enable workflow execution logging
- Set up alerts for workflow failures
- Monitor agent availability
- Track workflow execution success rates

### Proactive Measures

- Test workflows before enabling
- Validate agent commands exist
- Review workflow definitions in code reviews
- Keep workflow documentation updated
- Regular runbook audits via @business-continuity-agent

### Runbook Updates

- Document new workflows when created
- Update recovery procedures when workflows change
- Review runbooks quarterly
- Keep workflow documentation synchronized

## Recovery Procedure

### Safe Workflow Shutdown

**This is a stateless workflow** - can be safely disabled:

1. Edit `.cursor/workflows/stateless-workflows.yaml`
2. Find workflow: `<workflow-id>`
3. Set `enabled: false`
4. Commit changes to Git

**No data loss** - workflows are stateless, logic preserved in config files.

### Workflow Recovery

1. **Fix Underlying Issue**
   - Resolve agent command failures
   - Fix workflow definition errors
   - Update input/output mappings

2. **Re-enable Workflow**
   ```yaml
   <workflow-id>:
     enabled: true
   ```

3. **Verify Recovery**
   ```bash
   python .cursor/workflows/workflow-engine.py execute <workflow-id>
   ```

## Related Runbooks

- `agent-runtime-recovery.md` - Agent system recovery
- `database-recovery.md` - Database recovery procedures
- `twilio-recovery.md` - Twilio integration recovery

## Escalation

If workflow recovery doesn't resolve issue within 1 hour:

1. Document the failure scenario
2. Review agent system health: `@infrastructure-agent status`
3. Check for system-wide issues
4. Escalate to infrastructure team if needed

## Post-Incident

After resolution:

1. Document root cause analysis
2. Update workflow definition if needed
3. Review prevention measures
4. Update this runbook with learnings
5. Run business continuity audit: `@business-continuity-agent audit_runbooks`

## Notes

- **Stateless Design**: Workflows don't store state between executions
- **Safe Shutdown**: Setting `enabled: false` doesn't lose logic
- **Version Control**: All workflows stored in Git
- **No Rebuilds**: Logic in config files, not compiled code

