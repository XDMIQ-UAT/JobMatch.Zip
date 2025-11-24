# Restart Frontend on Production VM
# Usage: .\scripts\restart-frontend-on-vm.ps1

$VM_NAME = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
$ZONE = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }

Write-Host "🔄 Restarting frontend on $VM_NAME..." -ForegroundColor Cyan

$restartCmd = @"
cd /opt/jobmatch/frontend
echo 'Checking current process...'
ps aux | grep 'next start' | grep -v grep || echo 'No frontend process found'
echo ''
echo 'Stopping frontend...'
sudo supervisorctl stop frontend 2>/dev/null || sudo systemctl stop frontend 2>/dev/null || pkill -f 'next start' || echo 'No process to stop'
sleep 2
echo ''
echo 'Starting frontend...'
if command -v supervisorctl &> /dev/null; then
    sudo supervisorctl start frontend
    sleep 3
    sudo supervisorctl status frontend
elif systemctl list-units | grep -q frontend; then
    sudo systemctl start frontend
    sleep 3
    sudo systemctl status frontend --no-pager
else
    echo 'Starting manually...'
    cd /opt/jobmatch/frontend
    export NODE_ENV=production
    export PORT=3000
    nohup npm run start > /tmp/frontend.log 2>&1 &
    sleep 3
    ps aux | grep 'next start' | grep -v grep
    echo 'Logs: tail -f /tmp/frontend.log'
fi
echo ''
echo '✅ Frontend restart complete!'
"@

gcloud compute ssh $VM_NAME --zone=$ZONE --command=$restartCmd

Write-Host "`n✅ Frontend restart command executed" -ForegroundColor Green
Write-Host "`n🌐 Test URLs:" -ForegroundColor Cyan
Write-Host "   https://jobmatch.zip/manifest.json" -ForegroundColor White
Write-Host "   https://jobmatch.zip/sw.js" -ForegroundColor White

