# Server-Sent Events (SSE) Testing Guide

## Quick Test Commands

### Test SSE Endpoint with curl

```bash
# Basic test (runs until Ctrl+C)
curl -N -H "Accept: text/event-stream" \
     -H "Cache-Control: no-cache" \
     http://localhost:8000/api/agents/{agentId}/state/stream

# Test for 5 seconds then stop
timeout 5 curl -N -H "Accept: text/event-stream" \
     -H "Cache-Control: no-cache" \
     http://localhost:8000/api/agents/{agentId}/state/stream
```

### PowerShell Test

```powershell
# Using curl.exe (Windows)
curl.exe -N -H "Accept: text/event-stream" `
         -H "Cache-Control: no-cache" `
         http://localhost:8000/api/agents/{agentId}/state/stream

# Or use the test script
.\scripts\test-sse-endpoint.ps1 -AgentId "your-agent-id"
```

## Expected Output

You should see SSE events like:

```
data: {"agentId":"demo-agent","state":{},"timestamp":"2025-01-26T..."}

data: {"agentId":"demo-agent","state":{"analysis_count":1},"timestamp":"2025-01-26T..."}

data: {"agentId":"demo-agent","state":{"analysis_count":2},"timestamp":"2025-01-26T..."}
```

## Test Scripts

### Full API Test
```bash
# Bash
./scripts/test-agent-api.sh {agentId}

# PowerShell
.\scripts\test-agent-api.ps1 -AgentId "your-agent-id"
```

### SSE Only Test
```bash
# Bash
./scripts/test-sse-endpoint.sh {agentId}

# PowerShell
.\scripts\test-sse-endpoint.ps1 -AgentId "your-agent-id"
```

## Verification Checklist

- [ ] Backend is running on port 8000
- [ ] Agent is registered (check with `/api/agents/{id}/state`)
- [ ] SSE endpoint returns `text/event-stream` content type
- [ ] Events are received every second (when state changes)
- [ ] Events are valid JSON
- [ ] Connection stays open
- [ ] Frontend can connect via EventSource API

## Troubleshooting

### No events received
- Check agent state is actually changing
- Verify agent is registered
- Check backend logs for errors

### Connection closes immediately
- Check CORS settings
- Verify SSE headers are set correctly
- Check for nginx/proxy buffering issues

### Events not parsing
- Verify JSON format is correct
- Check `data: ` prefix is present
- Ensure double newline `\n\n` after each event

