# Quick Commands for Terminal (Not WARP)

Since WARP commands aren't working in regular terminal, use these PowerShell commands directly:

## Deploy Chat Backend

```powershell
# Option 1: Run the workflow directly
warp run warp-workflows/deploy-with-ollama-chat.yaml

# Option 2: Manual steps
cd frontend
npm install
npm run build
cd ..
powershell -ExecutionPolicy Bypass -File scripts/create-release.ps1
$env:VM_NAME = "jobmatch-vm"
$env:ZONE = "us-central1-a"
gcloud compute scp jobmatch.zip jobmatch-vm:/opt/jobmatch/ --zone=us-central1-a
gcloud compute ssh jobmatch-vm --zone=us-central1-a --command="cd /opt/jobmatch && unzip -o jobmatch.zip && docker-compose down && docker-compose build --no-cache && docker-compose up -d"
```

## Generate Test Data Overnight

```powershell
# Direct PowerShell command
.\scripts\run-overnight-data-generation.ps1

# Or with custom limits
$env:MAX_JOBS = 100
$env:MAX_CANDIDATES = 200
.\scripts\run-overnight-data-generation.ps1
```

## Setup SSL on VM

```powershell
.\scripts\setup-vm-ssl-from-bundle.ps1
```

## Check VM Status

```powershell
# Check services
gcloud compute ssh jobmatch-vm --zone=us-central1-a --command="docker-compose ps"

# Check logs
gcloud compute ssh jobmatch-vm --zone=us-central1-a --command="docker-compose logs --tail=50 app"

# Check Ollama
gcloud compute ssh jobmatch-vm --zone=us-central1-a --command="curl http://localhost:11434/api/tags"
```

