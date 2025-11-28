# Cloud Run Agents Setup Guide

## Overview

This guide explains how to deploy your stateless agent workflows to Google Cloud Run for auto-scaling, cost-effective agent execution.

## Architecture

```
┌─────────────────┐
│   Frontend/     │  ← VM (Compute Engine)
│   Backend       │
└────────┬────────┘
         │
         ├───→ Cloud Run (Agent Service)
         │     ├── Stateless Workflows
         │     ├── Agent Commands
         │     └── Auto-scaling
         │
         └───→ Pub/Sub (Optional - for async)
```

## Benefits

✅ **Auto-scaling** - Handles agent task bursts automatically  
✅ **Cost-effective** - Pay only when agents are running  
✅ **Stateless** - Perfect for your stateless workflow system  
✅ **No VM management** - Fully managed by Google  
✅ **Fast deployment** - Deploy in minutes  

## Quick Start

### Step 1: Deploy Agent Service

**Windows:**
```powershell
.\scripts\deploy-agents-cloud-run.ps1
```

**Linux/Mac:**
```bash
cd agents-cloud-run
chmod +x deploy.sh
./deploy.sh
```

### Step 2: Get Service URL

After deployment, get your service URL:
```bash
gcloud run services describe agent-service \
  --region us-central1 \
  --format="value(status.url)"
```

### Step 3: Test the Service

```bash
# Health check
curl https://agent-service-xxx.run.app/health

# List workflows
curl https://agent-service-xxx.run.app/workflows

# Execute workflow
curl -X POST https://agent-service-xxx.run.app/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{"workflow_id": "branding-review", "inputs": {}}'
```

## Integration with Backend

### Update Backend to Call Cloud Run

Add to your backend configuration:

```python
# backend/config.py
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "https://agent-service-xxx.run.app")
```

### Create Agent Client

```python
# backend/services/agent_client.py
import httpx
from config import settings

class AgentClient:
    def __init__(self):
        self.base_url = settings.AGENT_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def execute_workflow(self, workflow_id: str, inputs: dict):
        """Execute a stateless workflow"""
        response = await self.client.post(
            f"{self.base_url}/workflows/execute",
            json={"workflow_id": workflow_id, "inputs": inputs}
        )
        response.raise_for_status()
        return response.json()
    
    async def execute_agent_command(self, agent_id: str, command: str, inputs: dict):
        """Execute an agent command"""
        response = await self.client.post(
            f"{self.base_url}/agents/command",
            json={"agent_id": agent_id, "command": command, "inputs": inputs}
        )
        response.raise_for_status()
        return response.json()
    
    async def list_workflows(self):
        """List all available workflows"""
        response = await self.client.get(f"{self.base_url}/workflows")
        response.raise_for_status()
        return response.json()
```

### Use in Backend Routes

```python
# backend/api/agents.py
from fastapi import APIRouter
from services.agent_client import AgentClient

router = APIRouter()
agent_client = AgentClient()

@router.post("/workflows/execute")
async def execute_workflow(workflow_id: str, inputs: dict):
    """Execute a workflow via Cloud Run"""
    result = await agent_client.execute_workflow(workflow_id, inputs)
    return result
```

## Environment Variables

Set in Cloud Run:

```bash
gcloud run services update agent-service \
  --update-env-vars "NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6" \
  --region us-central1
```

Or via Secret Manager (recommended for secrets):

```bash
# Create secret
echo -n "secret-value" | gcloud secrets create AGENT_SECRET --data-file=-

# Grant access
gcloud secrets add-iam-policy-binding AGENT_SECRET \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Use in deployment
gcloud run deploy agent-service \
  --set-secrets "SECRET_VAR=AGENT_SECRET:latest" \
  --region us-central1
```

## Monitoring

### View Logs

```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=agent-service"
```

### View Metrics

- Go to [Cloud Run Console](https://console.cloud.google.com/run)
- Select `agent-service`
- View metrics: requests, latency, errors, instances

### Set Up Alerts

```bash
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Agent Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="agent-service"'
```

## Cost Optimization

### Current Configuration

- **Min instances**: 0 (scales to zero)
- **Max instances**: 10 (limits scaling)
- **Memory**: 512Mi
- **CPU**: 1 (throttled when idle)

### Cost Estimate

For typical agent workload:
- **Requests**: ~$0.40 per million requests
- **CPU**: ~$0.00002400 per vCPU-second
- **Memory**: ~$0.00000250 per GiB-second

**Estimated monthly cost**: $5-15 (depending on usage)

### Optimization Tips

1. **Set min instances to 0** - Scale to zero when idle ✅
2. **Use CPU throttling** - Only pay for CPU during requests ✅
3. **Optimize memory** - Use minimum required (512Mi) ✅
4. **Cache results** - Reduce repeated agent calls
5. **Batch requests** - Execute multiple workflows together

## Troubleshooting

### Service Not Starting

**Check logs:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=agent-service" --limit 50
```

**Common issues:**
- Workflow engine not found (check paths)
- Missing dependencies (check requirements.txt)
- Port not listening (ensure PORT env var)

### Workflows Not Found

**Verify workflow files are included:**
- Check `.dockerignore` doesn't exclude `.cursor/workflows/`
- Ensure workflow files are copied in Dockerfile

### Agent Commands Failing

**Check agent registry:**
- Verify `agents-registry.json` is accessible
- Check agent config files exist
- Verify agent scripts are executable

## Next Steps

1. ✅ **Deploy agent service** - Run deployment script
2. ⏳ **Update backend** - Add agent client integration
3. ⏳ **Test workflows** - Execute via Cloud Run API
4. ⏳ **Monitor usage** - Track costs and performance
5. ⏳ **Optimize** - Adjust based on usage patterns

## Files Created

- ✅ `agents-cloud-run/Dockerfile` - Container definition
- ✅ `agents-cloud-run/agent_service.py` - FastAPI service
- ✅ `agents-cloud-run/requirements.txt` - Python dependencies
- ✅ `agents-cloud-run/cloudbuild.yaml` - Cloud Build config
- ✅ `scripts/deploy-agents-cloud-run.ps1` - Deployment script
- ✅ `agents-cloud-run/deploy.sh` - Linux/Mac deployment
- ✅ `agents-cloud-run/README.md` - Service documentation

---

**Service Name**: agent-service  
**Region**: us-central1  
**Status**: Ready for deployment

