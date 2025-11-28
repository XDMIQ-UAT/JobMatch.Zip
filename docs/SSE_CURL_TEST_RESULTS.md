# SSE Endpoint - Curl Test Results

## Test Performed

```bash
curl -N -H "Accept: text/event-stream" \
     -H "Cache-Control: no-cache" \
     http://localhost:8000/api/agents/{agentId}/state/stream
```

## Test Results

### ✅ Endpoint Structure Verified
- Endpoint exists: `/api/agents/{agent_id}/state/stream`
- Returns proper HTTP response
- Handles missing agents correctly (404)

### ⚠️ Requirements for Full Test

To fully test SSE, you need:

1. **Backend running** ✅ (Verified: http://localhost:8000/health returns 200)
2. **Agent registered** ❌ (Need to register agent in running backend)
3. **State changes** ❌ (Need agent to update state)

## Manual Test Steps

### Step 1: Register an Agent

Add to your backend startup or create an endpoint:

```python
from backend.api.agent_ui import register_agent
from src.agents.base_agent import BaseAgent

# Create simple test agent
class TestAgent(BaseAgent):
    def perceive(self, env): return {}
    def decide(self, p): return {}
    def act(self, d): 
        self.update_state({"count": self.state.get("count", 0) + 1})
        return {}

agent = TestAgent(agent_id="test-agent", name="Test")
register_agent(agent.agent_id, agent)
```

### Step 2: Test SSE Endpoint

```bash
# Windows PowerShell
curl.exe -N -H "Accept: text/event-stream" `
         -H "Cache-Control: no-cache" `
         http://localhost:8000/api/agents/test-agent/state/stream

# Linux/Mac
curl -N -H "Accept: text/event-stream" \
     -H "Cache-Control: no-cache" \
     http://localhost:8000/api/agents/test-agent/state/stream
```

### Step 3: Expected Output

You should see events like:

```
data: {"agentId":"test-agent","state":{"count":1},"timestamp":"2025-01-26T..."}

data: {"agentId":"test-agent","state":{"count":2},"timestamp":"2025-01-26T..."}
```

## Verification Checklist

- [x] Backend is running
- [x] SSE endpoint exists
- [x] Proper error handling (404 for missing agent)
- [ ] Agent registration works
- [ ] SSE stream connects
- [ ] Events are received
- [ ] Events are valid JSON
- [ ] Connection stays open

## Next Steps

1. Register a test agent in the running backend
2. Run curl test to verify SSE stream
3. Verify events are received correctly
4. Test with frontend EventSource API

## Test Scripts Created

- `scripts/test-sse-endpoint.sh` - Bash script for SSE testing
- `scripts/test-sse-endpoint.ps1` - PowerShell script for SSE testing
- `scripts/test-agent-api.sh` - Full API test suite
- `scripts/test-agent-api.ps1` - PowerShell API test suite

Use these scripts once an agent is registered!

