# Agent Verification Guide

## How to Verify Agents Are Active in Cursor

### Method 1: Ask Cursor Directly
At the start of any chat, ask:
```
What agents are available?
Show me the agent registry
List all available agents
```

### Method 2: Check Agent Status
Ask Cursor to check a specific agent:
```
@fractional-ceo-agent status
@principal-dev-agent status
@git-project-manager-agent status
```

### Method 3: Verify Agent Registry
Ask Cursor to read the registry:
```
Read .cursor/agents/agents-registry.json
Show me all agent configurations
```

### Method 4: Test Agent Invocation
Try invoking an agent command:
```
@fractional-ceo-agent strategic_review
@principal-dev-agent review
@git-project-manager-agent scan_repos
```

## Expected Behavior

When agents are properly loaded, Cursor should:
1. **Acknowledge agent availability** - Mention agents when relevant to your question
2. **Load agent context** - Use agent capabilities and commands when appropriate
3. **Reference agent configurations** - Know about agent integrations and workflows
4. **Execute agent commands** - Run scripts or provide agent-specific guidance

## Agent Availability Indicators

You'll know agents are working when:
- ✅ Cursor mentions specific agents in responses
- ✅ Cursor suggests using agents for relevant tasks
- ✅ Agent commands execute successfully
- ✅ Agent context (workspace paths, scripts) is referenced correctly
- ✅ Agent integrations are understood (e.g., CEO agent coordinating with CFO agent)

## Troubleshooting

If agents don't seem to be working:

1. **Check file structure**: Verify `.cursor/agents/` directory exists with all JSON files
2. **Verify registry**: Check that `agents-registry.json` is valid JSON
3. **Check .cursorrules**: Ensure `.cursorrules` file includes agent references
4. **Restart Cursor**: Sometimes Cursor needs a restart to load new configurations
5. **Explicit mention**: Try explicitly mentioning `@agent-name` in your query

## Agent File Locations

- **Registry**: `E:\zip-jobmatch\.cursor\agents\agents-registry.json`
- **Configurations**: `E:\zip-jobmatch\.cursor\agents\*.json`
- **Documentation**: `E:\zip-jobmatch\.cursor\agents\README.md`
- **Quick Start**: `E:\zip-jobmatch\.cursor\agents\QUICK_START.md`
- **Cursor Rules**: `E:\zip-jobmatch\.cursorrules` (references agents)

## Next Steps

1. Start a new Cursor chat
2. Ask: "What agents are available?"
3. Try invoking an agent: `@fractional-ceo-agent status`
4. Verify Cursor acknowledges and uses agent context

