# Cloud Run Agents - Quick Start

## 🚀 Deploy in 3 Steps

### Step 1: Deploy to Cloud Run

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
```

## 📋 What Gets Deployed

- ✅ FastAPI HTTP API service
- ✅ Stateless workflow engine
- ✅ Agent command executor
- ✅ Health check endpoints
- ✅ Auto-scaling (0-10 instances)

## 🔗 Integration

### From Backend

```python
import httpx

AGENT_SERVICE_URL = "https://agent-service-xxx.run.app"

async def execute_workflow(workflow_id: str, inputs: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AGENT_SERVICE_URL}/workflows/execute",
            json={"workflow_id": workflow_id, "inputs": inputs}
        )
    return response.json()
```

## 💰 Cost

- **Free tier**: 2 million requests/month
- **After free tier**: ~$0.40 per million requests
- **CPU/Memory**: Pay per use (scales to zero)

**Estimated cost**: $5-15/month for typical usage

## 📊 Monitoring

```bash
# View logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=agent-service"

# View in console
# https://console.cloud.google.com/run
```

## 🔧 Configuration

### Environment Variables

```bash
gcloud run services update agent-service \
  --update-env-vars "NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6" \
  --region us-central1
```

### Scaling

```bash
# Update scaling
gcloud run services update agent-service \
  --min-instances 0 \
  --max-instances 20 \
  --region us-central1
```

## 🐛 Troubleshooting

### Service Not Starting

```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=agent-service" --limit 50
```

### Workflows Not Found

- Verify workflow files are in `.cursor/workflows/`
- Check Dockerfile copies workflow files correctly

---

**Ready to deploy?** Run the deployment script! 🚀

