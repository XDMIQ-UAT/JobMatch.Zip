# Test Cursor Agents Availability
# Run this script to verify all agent files are present and valid

Write-Host "=== Cursor Agents Verification ===" -ForegroundColor Cyan
Write-Host ""

$agentsDir = "E:\zip-jobmatch\.cursor\agents"
$registryFile = Join-Path $agentsDir "agents-registry.json"

# Check if directory exists
if (-not (Test-Path $agentsDir)) {
    Write-Host "❌ Agents directory not found: $agentsDir" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Agents directory found: $agentsDir" -ForegroundColor Green

# Check registry file
if (-not (Test-Path $registryFile)) {
    Write-Host "❌ Registry file not found: $registryFile" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Registry file found: $registryFile" -ForegroundColor Green

# Parse registry
try {
    $registry = Get-Content $registryFile | ConvertFrom-Json
    $agentCount = $registry.agents.Count
    Write-Host "✅ Registry contains $agentCount agents" -ForegroundColor Green
    Write-Host ""
    
    # Check each agent file
    Write-Host "Checking individual agent files..." -ForegroundColor Yellow
    $missingFiles = @()
    $validFiles = 0
    
    foreach ($agent in $registry.agents) {
        $agentFile = Join-Path $agentsDir $agent.file
        
        if (Test-Path $agentFile) {
            try {
                $agentConfig = Get-Content $agentFile | ConvertFrom-Json
                Write-Host "  ✅ $($agent.name) - $($agentFile)" -ForegroundColor Green
                $validFiles++
            } catch {
                Write-Host "  ⚠️  $($agent.name) - Invalid JSON: $($agentFile)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  ❌ $($agent.name) - Missing: $($agentFile)" -ForegroundColor Red
            $missingFiles += $agent.name
        }
    }
    
    Write-Host ""
    Write-Host "=== Summary ===" -ForegroundColor Cyan
    Write-Host "Total agents: $agentCount" -ForegroundColor White
    Write-Host "Valid files: $validFiles" -ForegroundColor Green
    
    if ($missingFiles.Count -gt 0) {
        Write-Host "Missing files: $($missingFiles.Count)" -ForegroundColor Red
        foreach ($missing in $missingFiles) {
            Write-Host "  - $missing" -ForegroundColor Red
        }
    } else {
        Write-Host "✅ All agent files present and valid!" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "1. Open Cursor and start a new chat" -ForegroundColor White
    Write-Host "2. Ask: 'What agents are available?'" -ForegroundColor White
    Write-Host "3. Try: '@fractional-ceo-agent status'" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "❌ Error parsing registry: $_" -ForegroundColor Red
    exit 1
}

