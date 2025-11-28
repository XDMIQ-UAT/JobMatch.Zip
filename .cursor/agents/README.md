# Cursor Agents - AI-Enabled Agent System

This directory contains Cursor agent configurations based on the E:\agents folder structure. These agents can be invoked by Cursor AI to perform specialized tasks.

## ✅ How to Verify Agents Are Active

**At the start of any Cursor chat, ask:**
```
What agents are available?
Show me the agent registry
List all available agents
```

**Or test a specific agent:**
```
@fractional-ceo-agent status
@principal-dev-agent status
@git-project-manager-agent status
```

**You'll know agents are working when:**
- ✅ Cursor mentions specific agents in responses
- ✅ Cursor suggests using agents for relevant tasks  
- ✅ Agent commands execute successfully
- ✅ Agent context (workspace paths, scripts) is referenced correctly

See `verify-agents.md` for detailed verification steps.

## Agent Structure

Each agent is defined with:
- **Name & Description**: What the agent does
- **Capabilities**: What it can help with
- **Commands**: Available actions
- **Integration Points**: How it coordinates with other agents
- **Context**: Relevant files and directories

## Usage

To invoke an agent in Cursor, use:
```
@agent-name [command] [parameters]
```

Example:
```
@fractional-ceo-agent strategic_review
@git-project-manager-agent scan_repos
@principal-dev-agent review
```

## Agent Registry

See `agents-registry.json` for the complete list of available agents.

## Agent Categories

- **C-Suite**: Strategic leadership agents (CEO, CFO, COO)
- **Development**: Technical development agents
- **Project Management**: Project and program management
- **Operations**: Operational and infrastructure agents
- **Specialized**: Domain-specific agents (data governance, historian, etc.)

## Integration with Cursor

These agents are automatically available because:
1. **`.cursorrules` file** references all agents (see project root)
2. **Agent registry** (`agents-registry.json`) lists all 15 agents
3. **Individual JSON files** define each agent's capabilities
4. **Cursor reads** these files at chat startup

If agents don't appear active, see `verify-agents.md` for troubleshooting.

