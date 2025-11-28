# Agent UI - URLs to Verify Interface

## 🚀 Quick Access URLs

### Demo Page (No Backend Required)
**Perfect for verifying the interface works!**

```
http://localhost:3000/agents/demo
```

This page shows 3 demo agents with mock data:
- Job Description Analyzer
- Matching Agent  
- Bias Detection Agent

**No backend setup needed** - works immediately!

---

### Real Agent Pages (Requires Backend)

#### Single Agent
```
http://localhost:3000/agents/{agentId}
```

**Example:**
```
http://localhost:3000/agents/job-matching-agent-123
```

**Requirements:**
- Backend running on port 8000
- Agent registered via `register_agent(agent_id, agent)`
- Agent has `get_ui_schema()` method

#### Workflow (Multiple Agents)
```
http://localhost:3000/workflow/{workflowId}
```

**Example:**
```
http://localhost:3000/workflow/job-matching-workflow-456
```

---

## 🔧 Setup Instructions

### 1. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend will run on: `http://localhost:3000`

### 2. Verify Demo Page
Navigate to: `http://localhost:3000/agents/demo`

You should see:
- ✅ 3 agent UI cards
- ✅ Progress bars
- ✅ Badges and alerts
- ✅ Action buttons
- ✅ Responsive layout

### 3. Test Real Agents (Optional)

#### Start Backend
```bash
cd backend
python -m uvicorn main:app --reload
```

#### Register an Agent
```python
from src.agents.job_description_analyzer_ui import JobDescriptionAnalyzerAgentUI
from backend.api.agent_ui import register_agent
from src.models.llm_providers import OpenAILanguageModel

llm = OpenAILanguageModel()
agent = JobDescriptionAnalyzerAgentUI(llm=llm)
register_agent(agent.agent_id, agent)

print(f"Agent ID: {agent.agent_id}")
```

#### Access Agent UI
```
http://localhost:3000/agents/{agent.agent_id}
```

---

## 📋 API Endpoints (For Testing)

### Get UI Schema
```bash
curl http://localhost:8000/api/agents/{agentId}/ui-schema
```

### Get Agent State
```bash
curl http://localhost:8000/api/agents/{agentId}/state
```

### Stream State Updates (SSE)
```bash
curl http://localhost:8000/api/agents/{agentId}/state/stream
```

---

## ✅ Verification Checklist

### Demo Page (`/agents/demo`)
- [ ] Page loads without errors
- [ ] 3 agent cards visible
- [ ] Progress bars render correctly
- [ ] Badges show correct colors
- [ ] Alerts display properly
- [ ] Action buttons work (show alert)
- [ ] Layout is responsive
- [ ] Styles applied correctly

### Real Agent Page (`/agents/{agentId}`)
- [ ] Page loads agent schema
- [ ] Components render from schema
- [ ] Real-time updates work (SSE)
- [ ] Actions execute correctly
- [ ] Error handling works

---

## 🐛 Troubleshooting

### Demo Page Not Loading
- Check frontend is running: `npm run dev`
- Check browser console for errors
- Verify `AgentUIRenderer` component exists
- Check CSS file is imported

### Real Agent Page Not Loading
- Verify backend is running
- Check agent is registered
- Verify API endpoint: `/api/agents/{id}/ui-schema`
- Check browser network tab for errors

### Components Not Rendering
- Check schema structure matches TypeScript types
- Verify component types are supported
- Check browser console for errors

---

## 📱 Mobile Testing

The interface is responsive. Test on:
- Desktop: `http://localhost:3000/agents/demo`
- Mobile: Use browser dev tools or actual device
- Tablet: Test various screen sizes

---

## 🎯 Quick Test

1. **Start frontend**: `cd frontend && npm run dev`
2. **Open browser**: `http://localhost:3000/agents/demo`
3. **Verify**: You should see 3 agent UI cards with all components rendering

That's it! The demo page works without any backend setup.

