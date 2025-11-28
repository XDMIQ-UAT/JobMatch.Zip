# Agent-Driven UI Schema System - Implementation Guide

## Overview

This implementation provides a complete agent-driven UI system that separates concerns between agent logic and presentation. Agents output declarative UI schemas instead of HTML, enabling better maintainability and testability.

## Architecture

```
Agent Logic → UI Schema → React Renderer → Browser
     ↓            ↓            ↓
  Python      JSON      TypeScript
```

## What's Been Implemented

### 1. **UI Schema System** (`src/schemas/ui-schema.ts`)
- TypeScript definitions for UI schemas
- Component types (progress, charts, tables, etc.)
- Layout system
- Action system
- Schema builder utility

### 2. **Agent UI Mixin** (`src/agents/ui_schema_mixin.py`)
- Python mixin that adds UI schema generation to agents
- Base implementation that agents can override
- State management integration

### 3. **Agent UI Implementations**
- `JobDescriptionAnalyzerAgentUI` - Job analysis UI
- `MatchingAgentUI` - Matching results UI
- `BiasDetectionAgentUI` - Bias detection UI

### 4. **API Endpoints** (`backend/api/agent_ui.py`)
- `/api/agents/{agent_id}/ui-schema` - Get UI schema
- `/api/agents/{agent_id}/state` - Get agent state
- `/api/agents/{agent_id}/state/stream` - SSE stream for real-time updates
- `/api/agents/{agent_id}/action/{action_id}` - Execute agent action

### 5. **React Components**
- `AgentUIRenderer` - Renders schemas into React components
- Individual component renderers (Progress, Alert, Badge, etc.)

### 6. **Frontend Pages**
- `/agents/[agentId]` - Single agent UI page
- `/workflow/[workflowId]` - Multi-agent workflow page

### 7. **Styling** (`frontend/styles/agent-ui.css`)
- Component styles
- Layout styles
- Responsive design

## Usage

### Step 1: Update Your Agents

```python
from src.agents.ui_schema_mixin import UISchemaMixin
from src.agents.job_description_analyzer import JobDescriptionAnalyzerAgent

class MyAgent(JobDescriptionAnalyzerAgent, UISchemaMixin):
    def _build_ui_components(self, builder, state):
        # Add your UI components
        builder.addComponent({
            "id": "my-component",
            "type": "progress",
            "bind": "my_state.progress",
            "props": {"value": 50}
        })
```

### Step 2: Register Agents

```python
from backend.api.agent_ui import register_agent

# When creating agents
agent = MyAgent(llm=llm)
register_agent(agent.agent_id, agent)
```

### Step 3: Access UI

Navigate to:
- Single agent: `http://localhost:3000/agents/{agent_id}`
- Workflow: `http://localhost:3000/workflow/{workflow_id}`

## Real-Time Updates

The system uses Server-Sent Events (SSE) for real-time updates:

```typescript
// Automatically handled in AgentPage component
// Agents publish state changes → UI updates automatically
```

## Adding New Component Types

1. **Define in schema** (`src/schemas/ui-schema.ts`):
```typescript
export type ComponentType = 
  | 'existing-types'
  | 'my-new-type';
```

2. **Add renderer** (`frontend/components/agent/AgentUIRenderer.tsx`):
```typescript
case 'my-new-type':
  return <MyNewComponent component={component} />;
```

3. **Create component**:
```typescript
function MyNewComponent({ component }: Props) {
  return <div>My custom component</div>;
}
```

## Benefits

✅ **Separation of Concerns**: Agent logic separate from UI  
✅ **Testability**: Test agents without UI  
✅ **Maintainability**: Change UI without touching agent code  
✅ **Type Safety**: TypeScript ensures correctness  
✅ **Real-Time**: Automatic updates via SSE  
✅ **Reusability**: Same schema can render to different UIs  

## Next Steps

1. **Integrate with existing agents** - Update your agents to use UI schemas
2. **Add more component types** - Charts, forms, etc.
3. **Customize styling** - Match your design system
4. **Add authentication** - Protect agent endpoints
5. **Add error handling** - Better error states in UI

## Example: Complete Agent with UI

```python
from src.agents.base_agent import BaseAgent
from src.agents.ui_schema_mixin import UISchemaMixin
from src.models.llm_providers import OpenAILanguageModel

class ExampleAgent(BaseAgent, UISchemaMixin):
    def __init__(self):
        super().__init__(name="Example Agent")
        self.llm = OpenAILanguageModel()
    
    def perceive(self, environment):
        return {"data": environment.get("input")}
    
    def decide(self, perception):
        return {"action": "process"}
    
    def act(self, decision):
        # Your agent logic
        result = {"processed": True}
        self.update_state({"result": result})
        return result
    
    def _build_ui_components(self, builder, state):
        builder.addComponent({
            "id": "status",
            "type": "text",
            "props": {"content": f"Status: {state.get('status', 'idle')}"}
        })
        
        if state.get("result"):
            builder.addComponent({
                "id": "result",
                "type": "card",
                "children": [{
                    "id": "result-text",
                    "type": "text",
                    "props": {"content": "Processing complete!"}
                }]
            })
```

## Troubleshooting

### Schema not loading
- Check agent is registered: `register_agent(agent_id, agent)`
- Verify agent has `get_ui_schema` method
- Check API endpoint: `/api/agents/{agent_id}/ui-schema`

### Real-time updates not working
- Verify SSE endpoint: `/api/agents/{agent_id}/state/stream`
- Check browser console for errors
- Ensure agent state is updating

### Components not rendering
- Check component type is supported
- Verify component props match schema
- Check browser console for errors

## Documentation

- **UI Schema Types**: See `src/schemas/ui-schema.ts`
- **Component Renderers**: See `frontend/components/agent/AgentUIRenderer.tsx`
- **API Endpoints**: See `backend/api/agent_ui.py`
- **Modern UI Architectures**: See `docs/MODERN_UI_ARCHITECTURES.md`

