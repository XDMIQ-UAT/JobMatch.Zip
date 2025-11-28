# State Recovery Script for JobMatch AI
# Restores application state from a checkpoint

param(
    [Parameter(Mandatory=$false)]
    [string]$CheckpointName,
    
    [Parameter(Mandatory=$false)]
    [switch]$List,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "E:\zip-jobmatch"
$CheckpointDir = "$ProjectRoot\data\checkpoints"

# Color output functions
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }

# List checkpoints
if ($List) {
    Write-Host "`n=== Available Checkpoints ===" -ForegroundColor Cyan
    
    $checkpoints = @()
    
    # List directories
    Get-ChildItem $CheckpointDir -Directory | ForEach-Object {
        $metadataPath = "$($_.FullName)\metadata.json"
        if (Test-Path $metadataPath) {
            $metadata = Get-Content $metadataPath | ConvertFrom-Json
            $checkpoints += [PSCustomObject]@{
                Name = $_.Name
                Created = $metadata.created_at
                GitCommit = $metadata.git_commit.Substring(0, 7)
                GitBranch = $metadata.git_branch
                HasDatabase = $metadata.database_backup
                HasRedis = $metadata.redis_backup
                Compressed = $false
            }
        }
    }
    
    # List archives
    Get-ChildItem $CheckpointDir -Filter "*.zip" | ForEach-Object {
        $checkpoints += [PSCustomObject]@{
            Name = $_.BaseName
            Created = $_.LastWriteTime.ToString('o')
            GitCommit = "N/A"
            GitBranch = "N/A"
            HasDatabase = "Unknown"
            HasRedis = "Unknown"
            Compressed = $true
        }
    }
    
    $checkpoints | Sort-Object Created -Descending | Format-Table -AutoSize
    
    Write-Info "Use: .\recover.ps1 -CheckpointName <name> to restore"
    exit 0
}

# Require checkpoint name if not listing
if (-not $CheckpointName) {
    Write-Error "Please specify a checkpoint name with -CheckpointName or use -List to see available checkpoints"
    exit 1
}

# Find checkpoint
$CheckpointPath = "$CheckpointDir\$CheckpointName"
$CheckpointArchive = "$CheckpointDir\$CheckpointName.zip"
$isCompressed = $false

if (Test-Path $CheckpointArchive) {
    Write-Info "Found compressed checkpoint: $CheckpointName.zip"
    $isCompressed = $true
    
    # Extract archive
    Write-Info "Extracting checkpoint..."
    $tempPath = "$CheckpointDir\temp_$CheckpointName"
    Expand-Archive -Path $CheckpointArchive -DestinationPath $tempPath -Force
    $CheckpointPath = $tempPath
    
} elseif (Test-Path $CheckpointPath) {
    Write-Info "Found checkpoint: $CheckpointName"
} else {
    Write-Error "Checkpoint not found: $CheckpointName"
    Write-Info "Use -List to see available checkpoints"
    exit 1
}

# Load metadata
$metadataPath = "$CheckpointPath\metadata.json"
if (-not (Test-Path $metadataPath)) {
    Write-Error "Checkpoint metadata not found"
    exit 1
}

$metadata = Get-Content $metadataPath | ConvertFrom-Json
Write-Info "Checkpoint: $($metadata.name)"
Write-Info "Created: $($metadata.created_at)"
Write-Info "Description: $($metadata.description)"
Write-Info "Git Commit: $($metadata.git_commit)"
Write-Info "Git Branch: $($metadata.git_branch)"

# Confirm recovery
if (-not $Force) {
    Write-Warning "`nThis will restore the application state to the checkpoint."
    Write-Warning "Current data may be overwritten!"
    $confirm = Read-Host "Continue? (yes/no)"
    
    if ($confirm -ne "yes") {
        Write-Info "Recovery cancelled"
        exit 0
    }
}

Write-Info "`nStarting recovery..."

# Stop Docker services
Write-Info "Stopping Docker services..."
try {
    docker-compose down
    Write-Success "Services stopped"
} catch {
    Write-Warning "Could not stop services: $_"
}

# Restore PostgreSQL database
if ($metadata.database_backup) {
    Write-Info "Restoring PostgreSQL database..."
    try {
        # Start only PostgreSQL
        docker-compose up -d postgres
        Start-Sleep -Seconds 5
        
        $dbDumpPath = "$CheckpointPath\database.sql"
        if (Test-Path $dbDumpPath) {
            # Drop and recreate database
            docker exec jobmatch-postgres psql -U jobmatch -c "DROP DATABASE IF EXISTS jobmatch;"
            docker exec jobmatch-postgres psql -U jobmatch -c "CREATE DATABASE jobmatch;"
            
            # Restore from dump
            Get-Content $dbDumpPath | docker exec -i jobmatch-postgres psql -U jobmatch -d jobmatch
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Database restored"
            } else {
                Write-Error "Database restore failed"
            }
        } else {
            Write-Warning "Database dump not found in checkpoint"
        }
    } catch {
        Write-Error "Database restore error: $_"
    }
} else {
    Write-Info "No database backup in checkpoint"
}

# Restore Redis data
if ($metadata.redis_backup) {
    Write-Info "Restoring Redis data..."
    try {
        # Start Redis
        docker-compose up -d redis
        Start-Sleep -Seconds 3
        
        $redisDumpPath = "$CheckpointPath\redis_dump.rdb"
        if (Test-Path $redisDumpPath) {
            # Stop Redis, replace dump file, restart
            docker-compose stop redis
            docker cp $redisDumpPath jobmatch-redis:/data/dump.rdb
            docker-compose up -d redis
            
            Write-Success "Redis data restored"
        } else {
            Write-Warning "Redis dump not found in checkpoint"
        }
    } catch {
        Write-Error "Redis restore error: $_"
    }
} else {
    Write-Info "No Redis backup in checkpoint"
}

# Restore environment configuration
if ($metadata.env_backup) {
    Write-Info "Restoring environment configuration..."
    try {
        $envBackupPath = "$CheckpointPath\environment"
        
        if (Test-Path "$envBackupPath\backend.env") {
            Copy-Item "$envBackupPath\backend.env" "$ProjectRoot\backend\.env" -Force
            Write-Success "Backend .env restored"
        }
        if (Test-Path "$envBackupPath\frontend.env") {
            Copy-Item "$envBackupPath\frontend.env" "$ProjectRoot\frontend\.env" -Force
            Write-Success "Frontend .env restored"
        }
        if (Test-Path "$envBackupPath\root.env") {
            Copy-Item "$envBackupPath\root.env" "$ProjectRoot\.env" -Force
            Write-Success "Root .env restored"
        }
    } catch {
        Write-Error "Environment restore error: $_"
    }
} else {
    Write-Info "No environment configuration in checkpoint"
}

# Restore Docker configuration
if ($metadata.docker_config_backup) {
    Write-Info "Restoring Docker configuration..."
    try {
        Copy-Item "$CheckpointPath\docker-compose.yml" "$ProjectRoot\docker-compose.yml" -Force
        Write-Success "Docker configuration restored"
    } catch {
        Write-Error "Docker config restore error: $_"
    }
}

# Clean up temporary extraction
if ($isCompressed) {
    Write-Info "Cleaning up temporary files..."
    Remove-Item -Path $CheckpointPath -Recurse -Force
}

# Restart all services
Write-Info "Starting all services..."
try {
    docker-compose up -d
    Start-Sleep -Seconds 10
    
    Write-Success "Services restarted"
    
    # Show service status
    Write-Host "`n=== Service Status ===" -ForegroundColor Cyan
    docker-compose ps
    
} catch {
    Write-Error "Failed to restart services: $_"
}

Write-Success "`nRecovery completed!"
Write-Info "Application state restored to checkpoint: $CheckpointName"

# Display Git information
if ($metadata.git_commit) {
    Write-Host "`n=== Git Information ===" -ForegroundColor Cyan
    Write-Host "Commit: $($metadata.git_commit)"
    Write-Host "Branch: $($metadata.git_branch)"
    Write-Warning "Remember to checkout the correct Git commit if needed:"
    Write-Host "  git checkout $($metadata.git_commit)"
}
