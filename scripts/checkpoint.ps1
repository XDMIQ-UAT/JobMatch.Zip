# State Checkpoint Script for JobMatch AI
# Creates a checkpoint of current application state

param(
    [Parameter(Mandatory=$false)]
    [string]$CheckpointName = "auto_$(Get-Date -Format 'yyyyMMdd_HHmmss')",
    
    [Parameter(Mandatory=$false)]
    [string]$Description = "Automatic checkpoint",
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeDatabase,
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeRedis,
    
    [Parameter(Mandatory=$false)]
    [switch]$Compress
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "E:\zip-jobmatch"
$CheckpointDir = "$ProjectRoot\data\checkpoints"
$CheckpointPath = "$CheckpointDir\$CheckpointName"

# Color output functions
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }

Write-Info "Creating checkpoint: $CheckpointName"
Write-Info "Description: $Description"

# Create checkpoint directory
if (-not (Test-Path $CheckpointDir)) {
    New-Item -ItemType Directory -Path $CheckpointDir -Force | Out-Null
}

New-Item -ItemType Directory -Path $CheckpointPath -Force | Out-Null

# Create checkpoint metadata
$metadata = @{
    name = $CheckpointName
    description = $Description
    created_at = (Get-Date).ToString('o')
    created_by = $env:USERNAME
    hostname = $env:COMPUTERNAME
    git_commit = ""
    git_branch = ""
    services_status = @{}
}

# Get Git information
try {
    $metadata.git_commit = git rev-parse HEAD 2>$null
    $metadata.git_branch = git branch --show-current 2>$null
    Write-Success "Git info captured"
} catch {
    Write-Warning "Git information not available"
}

# Check Docker services status
try {
    $services = docker-compose ps --format json | ConvertFrom-Json
    foreach ($service in $services) {
        $metadata.services_status[$service.Service] = $service.State
    }
    Write-Success "Docker services status captured"
} catch {
    Write-Warning "Could not capture Docker services status"
}

# Backup PostgreSQL database
if ($IncludeDatabase) {
    Write-Info "Backing up PostgreSQL database..."
    try {
        $dbDumpPath = "$CheckpointPath\database.sql"
        docker exec jobmatch-postgres pg_dump -U jobmatch -d jobmatch > $dbDumpPath
        
        if ($LASTEXITCODE -eq 0) {
            $metadata.database_backup = $true
            $metadata.database_size = (Get-Item $dbDumpPath).Length
            Write-Success "Database backup created"
        } else {
            Write-Error "Database backup failed"
        }
    } catch {
        Write-Error "Database backup error: $_"
        $metadata.database_backup = $false
    }
} else {
    $metadata.database_backup = $false
    Write-Info "Database backup skipped (use -IncludeDatabase to enable)"
}

# Backup Redis data
if ($IncludeRedis) {
    Write-Info "Backing up Redis data..."
    try {
        $redisDumpPath = "$CheckpointPath\redis_dump.rdb"
        docker exec jobmatch-redis redis-cli SAVE | Out-Null
        docker cp jobmatch-redis:/data/dump.rdb $redisDumpPath
        
        if ($LASTEXITCODE -eq 0) {
            $metadata.redis_backup = $true
            $metadata.redis_size = (Get-Item $redisDumpPath).Length
            Write-Success "Redis backup created"
        } else {
            Write-Error "Redis backup failed"
        }
    } catch {
        Write-Error "Redis backup error: $_"
        $metadata.redis_backup = $false
    }
} else {
    $metadata.redis_backup = $false
    Write-Info "Redis backup skipped (use -IncludeRedis to enable)"
}

# Backup environment configuration
Write-Info "Backing up environment configuration..."
try {
    $envBackupPath = "$CheckpointPath\environment"
    New-Item -ItemType Directory -Path $envBackupPath -Force | Out-Null
    
    # Copy .env files (if they exist)
    if (Test-Path "$ProjectRoot\backend\.env") {
        Copy-Item "$ProjectRoot\backend\.env" "$envBackupPath\backend.env"
    }
    if (Test-Path "$ProjectRoot\frontend\.env") {
        Copy-Item "$ProjectRoot\frontend\.env" "$envBackupPath\frontend.env"
    }
    if (Test-Path "$ProjectRoot\.env") {
        Copy-Item "$ProjectRoot\.env" "$envBackupPath\root.env"
    }
    
    $metadata.env_backup = $true
    Write-Success "Environment configuration backed up"
} catch {
    Write-Error "Environment backup error: $_"
    $metadata.env_backup = $false
}

# Backup docker-compose configuration
Write-Info "Backing up Docker configuration..."
try {
    Copy-Item "$ProjectRoot\docker-compose.yml" "$CheckpointPath\docker-compose.yml"
    $metadata.docker_config_backup = $true
    Write-Success "Docker configuration backed up"
} catch {
    Write-Error "Docker config backup error: $_"
    $metadata.docker_config_backup = $false
}

# Save metadata
$metadata | ConvertTo-Json -Depth 10 | Set-Content "$CheckpointPath\metadata.json"
Write-Success "Metadata saved"

# Compress checkpoint if requested
if ($Compress) {
    Write-Info "Compressing checkpoint..."
    try {
        $archivePath = "$CheckpointDir\$CheckpointName.zip"
        Compress-Archive -Path $CheckpointPath -DestinationPath $archivePath -Force
        
        # Remove uncompressed directory
        Remove-Item -Path $CheckpointPath -Recurse -Force
        
        $metadata.compressed = $true
        $metadata.archive_path = $archivePath
        $metadata.archive_size = (Get-Item $archivePath).Length
        
        Write-Success "Checkpoint compressed: $archivePath"
    } catch {
        Write-Error "Compression error: $_"
    }
} else {
    $metadata.compressed = $false
    Write-Info "Checkpoint saved: $CheckpointPath"
}

# Display checkpoint summary
Write-Host "`n=== Checkpoint Summary ===" -ForegroundColor Cyan
Write-Host "Name: $CheckpointName"
Write-Host "Created: $($metadata.created_at)"
Write-Host "Git Commit: $($metadata.git_commit)"
Write-Host "Git Branch: $($metadata.git_branch)"
Write-Host "Database Backup: $(if ($metadata.database_backup) { '✓ Yes' } else { '✗ No' })"
Write-Host "Redis Backup: $(if ($metadata.redis_backup) { '✓ Yes' } else { '✗ No' })"
Write-Host "Compressed: $(if ($metadata.compressed) { '✓ Yes' } else { '✗ No' })"

Write-Success "`nCheckpoint created successfully!"

# List recent checkpoints
Write-Host "`n=== Recent Checkpoints ===" -ForegroundColor Cyan
Get-ChildItem $CheckpointDir -Directory | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 5 | 
    ForEach-Object {
        Write-Host "  - $($_.Name) ($(Get-Date $_.LastWriteTime -Format 'yyyy-MM-dd HH:mm:ss'))"
    }

Get-ChildItem $CheckpointDir -Filter "*.zip" | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 5 | 
    ForEach-Object {
        Write-Host "  - $($_.Name) ($(Get-Date $_.LastWriteTime -Format 'yyyy-MM-dd HH:mm:ss')) [Compressed]"
    }
