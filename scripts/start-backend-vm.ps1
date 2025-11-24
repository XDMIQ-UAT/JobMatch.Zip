# Start Backend on VM
# Ensures backend is running with proper environment

param(
    [string]$VmName,
    [string]$Zone
)

# Set defaults if not provided
if (-not $VmName) {
    $VmName = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
}
if (-not $Zone) {
    $Zone = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }
}

Write-Host "🚀 Starting backend on $VmName..." -ForegroundColor Cyan
Write-Host ""

# Create startup script
$startScript = @'
#!/bin/bash
cd /opt/jobmatch

# Kill any existing backend processes
pkill -f "uvicorn backend.main:app" || true
sleep 2

# Activate virtual environment
source .venv/bin/activate

# Start backend
nohup python -m uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --app-dir /opt/jobmatch \
  > ~/.logs/jobmatch-backend.log 2>&1 &

# Wait a moment
sleep 3

# Check if it started
if ps aux | grep -E "uvicorn backend.main:app" | grep -v grep > /dev/null; then
    echo "✅ Backend started successfully"
    ps aux | grep -E "uvicorn backend.main:app" | grep -v grep | head -1
    echo ""
    echo "📋 Logs: tail -f ~/.logs/jobmatch-backend.log"
else
    echo "❌ Backend failed to start"
    echo ""
    echo "Recent logs:"
    tail -20 ~/.logs/jobmatch-backend.log 2>/dev/null || echo "No logs found"
    exit 1
fi
'@

# Write script to temp file
$tempScript = [System.IO.Path]::GetTempFileName()
$startScript | Out-File -FilePath $tempScript -Encoding utf8 -NoNewline

try {
    # Upload and execute
    gcloud compute scp $tempScript "${VmName}:/tmp/start-backend.sh" --zone=$Zone
    gcloud compute ssh $VmName --zone=$Zone --command="chmod +x /tmp/start-backend.sh && bash /tmp/start-backend.sh && rm /tmp/start-backend.sh"
} finally {
    Remove-Item $tempScript -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "✅ Backend startup command executed" -ForegroundColor Green

