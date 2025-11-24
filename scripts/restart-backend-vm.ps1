# Restart Backend on VM
# Simple script to restart the backend service

param(
    [string]$VmName = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" },
    [string]$Zone = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }
)

Write-Host "🔄 Restarting backend on $VmName..." -ForegroundColor Cyan
Write-Host ""

# SSH and restart
$restartScript = @'
cd /opt/jobmatch
echo "Stopping backend..."
pkill -f "uvicorn backend.main:app" || true
sleep 2

echo "Starting backend..."
source .venv/bin/activate
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --app-dir /opt/jobmatch > ~/.logs/jobmatch-backend.log 2>&1 &

sleep 3
echo ""
echo "Checking backend status..."
if ps aux | grep -E "uvicorn backend.main:app" | grep -v grep > /dev/null; then
    echo "✅ Backend restarted successfully"
    ps aux | grep -E "uvicorn backend.main:app" | grep -v grep | head -1
else
    echo "❌ Backend failed to start - check logs:"
    echo "   tail -f ~/.logs/jobmatch-backend.log"
fi
'@

# Write script to temp file and execute
$tempScript = [System.IO.Path]::GetTempFileName()
$restartScript | Out-File -FilePath $tempScript -Encoding utf8 -NoNewline

try {
    gcloud compute scp $tempScript "${VmName}:/tmp/restart-backend.sh" --zone=$Zone
    gcloud compute ssh $VmName --zone=$Zone --command="chmod +x /tmp/restart-backend.sh && bash /tmp/restart-backend.sh && rm /tmp/restart-backend.sh"
} finally {
    Remove-Item $tempScript -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "✅ Restart command executed" -ForegroundColor Green
Write-Host ""
Write-Host "🧪 Test email sending:" -ForegroundColor Cyan
Write-Host "   https://jobmatch.zip/auth?provider=email" -ForegroundColor White

