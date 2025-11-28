# Cloud Run Agent Service

HTTP API service for executing stateless workflows and agent commands on Google Cloud Run.

## Overview

This service provides a REST API for:
- Executing stateless workflows
- Running agent commands
- Listing available workflows
- Health checks

## Architecture

```
Cloud Run Service
├── FastAPI HTTP API
├── Stateless Workflow Engine
├── Agent Command Executor
└── Health Check Endpoints
```

## API Endpoints

### Health Check
```
GET /health
```

### List Workflows
```
GET /workflows
```

### Get Workflow
```
GET /workflows/{workflow_id}
```

### Execute Workflow
```
POST /workflows/execute
{
  "workflow_id": "branding-review",
  "inputs": {
    "name": "Product Name",
    "item_type": "feature"
  }
}
```

### Execute Agent Command
```
POST /agents/command
{
  "agent_id": "branding-agent",
  "command": "review_name",
  "inputs": {
    "name": "Product Name"
  }
}
```

## Deployment

### Quick Deploy

```powershell
.\scripts\deploy-agents-cloud-run.ps1
```

### Manual Deploy

```bash
# Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/agent-service

# Deploy
gcloud run deploy agent-service \
  --image gcr.io/$PROJECT_ID/agent-service:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

## Environment Variables

Set via Cloud Run:
- `NEXT_PUBLIC_GTM_ID` - Google Tag Manager ID
- `REDIS_URL` - Redis connection (if needed)
- `DATABASE_URL` - Database connection (if needed)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python agent_service.py

# Or with uvicorn
uvicorn agent_service:app --host 0.0.0.0 --port 8080 --reload
```

## Testing

```bash
# Health check
curl http://localhost:8080/health

# List workflows
curl http://localhost:8080/workflows

# Execute workflow
curl -X POST http://localhost:8080/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{"workflow_id": "branding-review", "inputs": {}}'
```

## Integration with VM

The Cloud Run service can be called from your VM-based backend:

```python
import httpx

AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "https://agent-service-xxx.run.app")

async def execute_workflow(workflow_id: str, inputs: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AGENT_SERVICE_URL}/workflows/execute",
            json={"workflow_id": workflow_id, "inputs": inputs}
        )
    return response.json()
```

## Cost Optimization

- **Min instances: 0** - Scales to zero when not in use
- **Max instances: 10** - Limits scaling
- **CPU throttling** - Only uses CPU during requests
- **Memory: 512Mi** - Sufficient for agent workloads

## Monitoring

View logs:
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=agent-service"
```

View metrics:
- Cloud Run console
- Cloud Monitoring dashboard

---

**Service Name**: agent-service  
**Region**: us-central1  
**Platform**: Cloud Run (managed)

