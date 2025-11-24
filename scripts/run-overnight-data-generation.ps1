# Run data generation script overnight on VM
# This script can be run as a background job

param(
    [string]$VmName = "jobmatch-vm",
    [string]$Zone = "us-central1-a",
    [int]$MaxJobs = 50,
    [int]$MaxCandidates = 100
)

$ErrorActionPreference = "Stop"

$logFile = "/tmp/overnight-data-generation.log"

Write-Host "🌙 Starting overnight data generation..." -ForegroundColor Cyan
Write-Host "   Max Jobs: $MaxJobs" -ForegroundColor White
Write-Host "   Max Candidates: $MaxCandidates" -ForegroundColor White
Write-Host "   Log file: $logFile" -ForegroundColor White
Write-Host ""

# Upload script to VM
Write-Host "📤 Uploading data generation script..." -ForegroundColor Cyan
$scriptPath = Join-Path $PSScriptRoot "generate-test-data.py"
if (-not (Test-Path $scriptPath)) {
    $scriptPath = Join-Path (Split-Path $PSScriptRoot -Parent) "scripts\generate-test-data.py"
}
if (Test-Path $scriptPath) {
    gcloud compute scp $scriptPath "${VmName}:/opt/jobmatch/scripts/generate-test-data.py" --zone=$Zone
} else {
    Write-Host "⚠️  Script not found locally, will use existing on VM" -ForegroundColor Yellow
}

# Run script in background (inside Docker container where dependencies are installed)
Write-Host "🚀 Starting data generation in background..." -ForegroundColor Cyan
$bashScript = @"
cd /opt/jobmatch
export DATABASE_URL='postgresql://jobfinder:jobfinder@postgres:5432/jobfinder'
export OLLAMA_BASE_URL='http://ollama:11434'
export OLLAMA_MODEL='llama3.2'
export MAX_JOBS=$MaxJobs
export MAX_CANDIDATES=$MaxCandidates
docker compose exec -d app bash -c "export DATABASE_URL='postgresql://jobfinder:jobfinder@postgres:5432/jobfinder' && export OLLAMA_BASE_URL='http://ollama:11434' && export OLLAMA_MODEL='llama3.2' && export MAX_JOBS=$MaxJobs && export MAX_CANDIDATES=$MaxCandidates && python3 scripts/generate-test-data.py > $logFile 2>&1"
sleep 2
echo '✅ Data generation started in background'
echo "   Log file: $logFile"
echo ''
echo 'To check progress:'
echo "   tail -f $logFile"
echo ''
echo 'To check if still running:'
echo '   docker compose exec app ps aux | grep generate-test-data'
"@

# Write script to temp file and execute
$tempScript = "/tmp/run-data-gen.sh"
gcloud compute ssh $VmName --zone=$Zone --command="cat > $tempScript << 'EOFBASH'
$bashScript
EOFBASH
chmod +x $tempScript
bash $tempScript"


Write-Host ""
Write-Host "✅ Overnight data generation started!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 To check progress, run:" -ForegroundColor Yellow
Write-Host "   gcloud compute ssh $VmName --zone=$Zone --command='tail -f $logFile'" -ForegroundColor White
Write-Host ""
Write-Host "📊 To check current database stats:" -ForegroundColor Yellow
$statsCmd = "docker-compose exec -T postgres psql -U jobfinder -d jobfinder -c `"SELECT COUNT(*) as jobs FROM job_postings; SELECT COUNT(*) as candidates FROM anonymous_users;`""
Write-Host "   gcloud compute ssh $VmName --zone=$Zone --command='$statsCmd'" -ForegroundColor White

