# Pieces MCP Integration with Warp

## Overview

Pieces MCP can stay in sync with Warp terminal activities to provide context-aware AI assistance.

## Integration Points

### 1. Warp Terminal Activities

Pieces MCP can capture:
- Commands executed in Warp
- File operations
- Project context
- Workflow state

### 2. Context Sharing

- Warp activities → Pieces MCP → Claude Code
- Provides full context for AI assistance
- Maintains development workflow continuity

## Setup

### Warp Configuration

Add to Warp workflows to sync with Pieces:

```yaml
# In Warp workflow
on_command_execution:
  - python .claude-code/pieces-warp-sync.py command "{{command}}"
  
on_file_access:
  - python .claude-code/pieces-warp-sync.py file "{{file_path}}" "{{operation}}"
```

### Pieces MCP Configuration

Pieces MCP automatically tracks:
- Warp terminal sessions
- Command history
- File access patterns
- Project context

## Usage

### Manual Sync

```bash
# Capture current context
python .claude-code/pieces-warp-sync.py context

# Capture command
python .claude-code/pieces-warp-sync.py command "npm run dev"

# Capture file access
python .claude-code/pieces-warp-sync.py file "backend/main.py" "edited"
```

### Automatic Sync

Pieces MCP automatically syncs when:
- Warp terminal is active
- Commands are executed
- Files are accessed
- Project context changes

## Benefits

1. **Context Continuity**: Pieces maintains context across Warp sessions
2. **Better AI Assistance**: Claude Code has full context from Warp
3. **Workflow Tracking**: Track development workflow automatically
4. **Pattern Recognition**: Learn from Warp usage patterns

## Integration with Claude Code

Pieces MCP context enhances Claude Code prompts:
- Warp command history → Better code suggestions
- File access patterns → Context-aware generation
- Project state → Accurate recommendations

