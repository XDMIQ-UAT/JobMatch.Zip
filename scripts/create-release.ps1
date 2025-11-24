# PowerShell script to create release package
# More efficient than bash version for Windows

$excludePatterns = @(
    "*.git*",
    "node_modules",
    ".next",
    "__pycache__",
    "*.pyc",
    "*.env*",
    "dist",
    ".DS_Store",
    "warp-workflows",
    ".claude-code",
    "releases",
    "*.log",
    "*.zip"
)

Write-Host "Creating release package..." -ForegroundColor Cyan

# Remove old zip if exists (with retry for file locks)
if (Test-Path "jobmatch.zip") {
    $retries = 3
    $removed = $false
    for ($i = 1; $i -le $retries; $i++) {
        try {
            Remove-Item "jobmatch.zip" -Force -ErrorAction Stop
            $removed = $true
            Write-Host "Removed old jobmatch.zip" -ForegroundColor Yellow
            break
        } catch {
            if ($i -lt $retries) {
                Start-Sleep -Milliseconds 500
            } else {
                Write-Host "Warning: Could not remove old zip, will overwrite" -ForegroundColor Yellow
            }
        }
    }
}

# Get all files, excluding patterns
$files = Get-ChildItem -Recurse -File | Where-Object {
    $exclude = $false
    foreach ($pattern in $excludePatterns) {
        if ($_.FullName -like "*$pattern*") {
            $exclude = $true
            break
        }
    }
    return -not $exclude
}

Write-Host "Found $($files.Count) files to include" -ForegroundColor Green

# Create zip preserving directory structure
$zipPath = Join-Path $PWD "jobmatch.zip"
# Use .NET compression to preserve directory structure
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($PWD, $zipPath, [System.IO.Compression.CompressionLevel]::Fastest, $false, $null)
# Then remove excluded files from zip
$zip = [System.IO.Compression.ZipFile]::Open($zipPath, [System.IO.Compression.ZipArchiveMode]::Update)
$entriesToRemove = $zip.Entries | Where-Object {
    $entryPath = $_.FullName
    $exclude = $false
    foreach ($pattern in $excludePatterns) {
        if ($entryPath -like "*$pattern*") {
            $exclude = $true
            break
        }
    }
    $exclude
}
$entriesToRemove | ForEach-Object { $_.Delete() }
$zip.Dispose()

$zipSize = (Get-Item $zipPath).Length / 1MB
$sizeMB = [math]::Round($zipSize, 2)
Write-Host "Created jobmatch.zip - Size: $sizeMB MB" -ForegroundColor Green
