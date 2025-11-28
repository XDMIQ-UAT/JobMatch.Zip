# Comprehensive Agent Execution and Codebase Indexing Script
# Runs all agents from E:\agents across E:\zip-jobmatch project
# Indexes codebase and scans external context from E:\

param(
    [string]$ProjectPath = "E:\zip-jobmatch",
    [string]$AgentsPath = "E:\agents",
    [string]$ExternalScanPath = "E:\",
    [switch]$IndexOnly = $false,
    [switch]$ScanOnly = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Comprehensive Agent Execution & Indexing" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $ProjectPath" -ForegroundColor White
Write-Host "Agents: $AgentsPath" -ForegroundColor White
Write-Host "External Scan: $ExternalScanPath" -ForegroundColor White
Write-Host ""

# Set working directory
Set-Location $ProjectPath

# Create output directory
$OutputDir = "$ProjectPath\agent-index-output"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$OutputDir\index-log-$Timestamp.txt"

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage
}

function Invoke-AgentCommand {
    param(
        [string]$AgentName,
        [string]$Command,
        [string]$AgentPath,
        [string]$ProjectPath
    )
    
    Write-Log "Executing $AgentName.$Command" "Yellow"
    
    try {
        # Check for agent.yaml
        $AgentYaml = Join-Path $AgentPath "agent.yaml"
        if (-not (Test-Path $AgentYaml)) {
            Write-Log "  No agent.yaml found, skipping" "Gray"
            return $false
        }
        
        # Load agent config
        $AgentConfig = Get-Content $AgentYaml -Raw | ConvertFrom-Yaml -ErrorAction SilentlyContinue
        
        if (-not $AgentConfig) {
            Write-Log "  Failed to parse agent.yaml" "Red"
            return $false
        }
        
        # Check if agent is enabled
        $IsEnabled = $AgentConfig.config.enabled
        if ($IsEnabled -eq $false) {
            Write-Log "  Agent is disabled, skipping" "Gray"
            return $false
        }
        
        # Get command script
        $Commands = $AgentConfig.commands
        if (-not $Commands -or -not $Commands.$Command) {
            Write-Log "  Command '$Command' not found" "Gray"
            return $false
        }
        
        $CommandDef = $Commands.$Command
        $Script = $null
        
        if ($CommandDef -is [string]) {
            $Script = $CommandDef
        } elseif ($CommandDef.script) {
            $Script = $CommandDef.script
        } elseif ($CommandDef.cursor_cli) {
            Write-Log "  Cursor CLI command, using Cursor integration" "Cyan"
            # For Cursor CLI commands, we'll use the Cursor CLI integration
            return $true
        }
        
        if (-not $Script) {
            Write-Log "  No script found for command" "Gray"
            return $false
        }
        
        # Replace workspace paths
        $Script = $Script -replace 'E:\\zip-jobmatch', $ProjectPath
        $Script = $Script -replace 'E:\\agents', $AgentsPath
        
        # Execute script
        Write-Log "  Running: $Script" "Gray"
        
        $Output = & pwsh -Command $Script 2>&1
        $ExitCode = $LASTEXITCODE
        
        if ($ExitCode -eq 0) {
            Write-Log "  ✓ $AgentName.$Command completed successfully" "Green"
            if ($Output) {
                $Output | ForEach-Object { Write-Log "    $_" "Gray" }
            }
            return $true
        } else {
            Write-Log "  ✗ $AgentName.$Command failed (exit code: $ExitCode)" "Red"
            if ($Output) {
                $Output | ForEach-Object { Write-Log "    $_" "Red" }
            }
            return $false
        }
        
    } catch {
        Write-Log "  ✗ Error executing $AgentName.$Command : $_" "Red"
        return $false
    }
}

function Index-Codebase {
    param([string]$ProjectPath, [string]$OutputDir)
    
    Write-Log "=== Indexing Codebase ===" "Cyan"
    
    $IndexFile = "$OutputDir\codebase-index-$Timestamp.json"
    $Index = @{
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        project_path = $ProjectPath
        files = @()
        structure = @{}
        languages = @{}
        dependencies = @{}
    }
    
    # Scan project structure
    Write-Log "Scanning project structure..." "Yellow"
    
    $ExcludeDirs = @('node_modules', '__pycache__', '.git', 'dist', 'build', '.next', 'venv', '.venv', 'env')
    $IncludeExtensions = @('.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.yaml', '.yml', '.md', '.sql', '.ps1', '.sh')
    
    $Files = Get-ChildItem -Path $ProjectPath -Recurse -File | 
        Where-Object { 
            $Exclude = $false
            foreach ($Dir in $ExcludeDirs) {
                if ($_.FullName -like "*\$Dir\*") {
                    $Exclude = $true
                    break
                }
            }
            -not $Exclude -and ($IncludeExtensions -contains $_.Extension)
        }
    
    Write-Log "Found $($Files.Count) files to index" "Green"
    
    foreach ($File in $Files) {
        $RelativePath = $File.FullName.Substring($ProjectPath.Length + 1)
        $Extension = $File.Extension
        
        # Count by language
        if (-not $Index.languages[$Extension]) {
            $Index.languages[$Extension] = 0
        }
        $Index.languages[$Extension]++
        
        # Get file info
        $FileInfo = @{
            path = $RelativePath
            full_path = $File.FullName
            extension = $Extension
            size = $File.Length
            modified = $File.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
        }
        
        # Try to get line count for code files
        if ($IncludeExtensions -contains $Extension) {
            try {
                $Content = Get-Content $File.FullName -ErrorAction SilentlyContinue
                $FileInfo.lines = $Content.Count
            } catch {
                $FileInfo.lines = 0
            }
        }
        
        $Index.files += $FileInfo
        
        # Build structure tree
        $Parts = $RelativePath -split '\\'
        $Current = $Index.structure
        foreach ($Part in $Parts[0..($Parts.Length - 2)]) {
            if (-not $Current[$Part]) {
                $Current[$Part] = @{}
            }
            $Current = $Current[$Part]
        }
    }
    
    # Scan for dependencies
    Write-Log "Scanning dependencies..." "Yellow"
    
    # Python dependencies
    $RequirementsTxt = Join-Path $ProjectPath "requirements.txt"
    if (Test-Path $RequirementsTxt) {
        $Index.dependencies.python = @()
        Get-Content $RequirementsTxt | ForEach-Object {
            if ($_ -match '^([a-zA-Z0-9_-]+)') {
                $Index.dependencies.python += $Matches[1]
            }
        }
    }
    
    # Node.js dependencies
    $PackageJson = Join-Path $ProjectPath "package.json"
    if (Test-Path $PackageJson) {
        $PackageContent = Get-Content $PackageJson -Raw | ConvertFrom-Json
        $Index.dependencies.node = @{
            dependencies = if ($PackageContent.dependencies) { $PackageContent.dependencies.PSObject.Properties.Name } else { @() }
            devDependencies = if ($PackageContent.devDependencies) { $PackageContent.devDependencies.PSObject.Properties.Name } else { @() }
        }
    }
    
    # Save index
    $Index | ConvertTo-Json -Depth 10 | Set-Content $IndexFile
    Write-Log "Codebase index saved to: $IndexFile" "Green"
    
    # Generate summary
    $SummaryFile = "$OutputDir\codebase-summary-$Timestamp.md"
    $Summary = @"
# Codebase Index Summary
Generated: $($Index.timestamp)

## Project Structure
- **Total Files**: $($Index.files.Count)
- **Languages**: $($Index.languages.Count)

## File Types
"@
    
    foreach ($Lang in $Index.languages.GetEnumerator() | Sort-Object Value -Descending) {
        $Summary += "`n- $($Lang.Key): $($Lang.Value) files"
    }
    
    $Summary += @"

## Dependencies
"@
    
    if ($Index.dependencies.python) {
        $Summary += "`n### Python ($($Index.dependencies.python.Count) packages)"
        $Index.dependencies.python | ForEach-Object { $Summary += "`n- $_" }
    }
    
    if ($Index.dependencies.node) {
        $Summary += "`n### Node.js"
        if ($Index.dependencies.node.dependencies) {
            $Summary += "`n**Dependencies** ($($Index.dependencies.node.dependencies.Count)):"
            $Index.dependencies.node.dependencies | ForEach-Object { $Summary += "`n- $_" }
        }
        if ($Index.dependencies.node.devDependencies) {
            $Summary += "`n**Dev Dependencies** ($($Index.dependencies.node.devDependencies.Count)):"
            $Index.dependencies.node.devDependencies | ForEach-Object { $Summary += "`n- $_" }
        }
    }
    
    $Summary | Set-Content $SummaryFile
    Write-Log "Summary saved to: $SummaryFile" "Green"
    
    return $Index
}

function Scan-ExternalContext {
    param([string]$ScanPath, [string]$OutputDir)
    
    Write-Log "=== Scanning External Context ===" "Cyan"
    
    $ScanFile = "$OutputDir\external-context-$Timestamp.json"
    $Context = @{
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        scan_path = $ScanPath
        projects = @()
        codebases = @()
    }
    
    Write-Log "Scanning $ScanPath for projects and codebases..." "Yellow"
    
    try {
        # Discover projects using project_discovery.py
        $DiscoveryScript = @"
import sys
sys.path.insert(0, r'$AgentsPath\runtime')
from project_discovery import get_project_discovery
import json

discovery = get_project_discovery(['$ScanPath'])
projects = discovery.discover_projects(force_refresh=True, max_depth=3)
print(json.dumps(projects, indent=2))
"@
        
        $ProjectsJson = & python -c $DiscoveryScript 2>&1
        if ($LASTEXITCODE -eq 0) {
            $Projects = $ProjectsJson | ConvertFrom-Json
            Write-Log "Discovered $($Projects.Count) projects" "Green"
            
            foreach ($ProjectPath in $Projects.PSObject.Properties.Name) {
                $ProjectInfo = $Projects.$ProjectPath
                $Context.projects += @{
                    path = $ProjectPath
                    name = $ProjectInfo.name
                    type = $ProjectInfo.type
                    has_git = $ProjectInfo.has_git
                    has_cursor = $ProjectInfo.has_cursor
                    has_agents = $ProjectInfo.has_agents
                }
            }
        }
    } catch {
        Write-Log "Error in project discovery: $_" "Red"
    }
    
    # Scan for codebases (directories with code files)
    Write-Log "Scanning for codebases..." "Yellow"
    
    $CodebaseIndicators = @('package.json', 'requirements.txt', 'pyproject.toml', 'Cargo.toml', 'pom.xml', '.git')
    
    try {
        $TopLevelDirs = Get-ChildItem -Path $ScanPath -Directory -ErrorAction SilentlyContinue | 
            Where-Object { -not $_.Name.StartsWith('.') }
        
        foreach ($Dir in $TopLevelDirs) {
            $IsCodebase = $false
            $CodebaseType = "unknown"
            
            foreach ($Indicator in $CodebaseIndicators) {
                $IndicatorPath = Join-Path $Dir.FullName $Indicator
                if (Test-Path $IndicatorPath) {
                    $IsCodebase = $true
                    switch ($Indicator) {
                        'package.json' { $CodebaseType = "node" }
                        'requirements.txt' { $CodebaseType = "python" }
                        'pyproject.toml' { $CodebaseType = "python" }
                        'Cargo.toml' { $CodebaseType = "rust" }
                        'pom.xml' { $CodebaseType = "java" }
                        '.git' { $CodebaseType = "git" }
                    }
                    break
                }
            }
            
            if ($IsCodebase) {
                $Context.codebases += @{
                    path = $Dir.FullName
                    name = $Dir.Name
                    type = $CodebaseType
                }
            }
        }
        
        Write-Log "Found $($Context.codebases.Count) codebases" "Green"
    } catch {
        Write-Log "Error scanning codebases: $_" "Red"
    }
    
    # Save context
    $Context | ConvertTo-Json -Depth 10 | Set-Content $ScanFile
    Write-Log "External context saved to: $ScanFile" "Green"
    
    return $Context
}

function Run-AllAgents {
    param([string]$AgentsPath, [string]$ProjectPath, [string]$OutputDir)
    
    Write-Log "=== Running All Agents ===" "Cyan"
    
    $AgentResults = @{
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        agents_run = @()
        summary = @{
            total = 0
            successful = 0
            failed = 0
            skipped = 0
        }
    }
    
    # Load agent registry
    $RegistryPath = "$ProjectPath\.cursor\agents\agents-registry.json"
    if (Test-Path $RegistryPath) {
        $Registry = Get-Content $RegistryPath -Raw | ConvertFrom-Json
        Write-Log "Loaded agent registry with $($Registry.agents.Count) agents" "Green"
    } else {
        Write-Log "Agent registry not found, scanning agents directory" "Yellow"
        $Registry = @{ agents = @() }
        
        # Scan for agents manually
        $AgentDirs = Get-ChildItem -Path $AgentsPath -Directory | 
            Where-Object { 
                (Test-Path (Join-Path $_.FullName "agent.yaml")) -or
                (Test-Path (Join-Path $_.FullName "*.py"))
            }
        
        foreach ($Dir in $AgentDirs) {
            $Registry.agents += @{
                id = $Dir.Name
                name = $Dir.Name
                enabled = $true
            }
        }
    }
    
    # Run each agent
    foreach ($Agent in $Registry.agents) {
        if ($Agent.enabled -eq $false) {
            Write-Log "Skipping disabled agent: $($Agent.id)" "Gray"
            $AgentResults.summary.skipped++
            continue
        }
        
        $AgentResults.summary.total++
        $AgentPath = Join-Path $AgentsPath $Agent.id
        
        if (-not (Test-Path $AgentPath)) {
            Write-Log "Agent path not found: $AgentPath" "Red"
            $AgentResults.agents_run += @{
                agent = $Agent.id
                status = "not_found"
                commands_run = @()
            }
            $AgentResults.summary.failed++
            continue
        }
        
        Write-Log "Processing agent: $($Agent.id)" "Yellow"
        
        $AgentResult = @{
            agent = $Agent.id
            status = "running"
            commands_run = @()
        }
        
        # Determine commands to run based on agent type
        $CommandsToRun = @()
        
        # Common commands by category
        switch ($Agent.category) {
            "c-suite" {
                $CommandsToRun = @("status", "review", "assess")
            }
            "development" {
                $CommandsToRun = @("review", "analyze", "status")
            }
            "project-management" {
                $CommandsToRun = @("status", "scan_repos", "work")
            }
            "operations" {
                $CommandsToRun = @("status", "healthcheck", "assess")
            }
            "specialized" {
                $CommandsToRun = @("status", "record", "validate")
            }
            default {
                $CommandsToRun = @("status")
            }
        }
        
        $SuccessCount = 0
        foreach ($Command in $CommandsToRun) {
            $Success = Invoke-AgentCommand -AgentName $Agent.id -Command $Command -AgentPath $AgentPath -ProjectPath $ProjectPath
            $AgentResult.commands_run += @{
                command = $Command
                success = $Success
            }
            if ($Success) { $SuccessCount++ }
        }
        
        if ($SuccessCount -gt 0) {
            $AgentResult.status = "success"
            $AgentResults.summary.successful++
        } else {
            $AgentResult.status = "failed"
            $AgentResults.summary.failed++
        }
        
        $AgentResults.agents_run += $AgentResult
    }
    
    # Save results
    $ResultsFile = "$OutputDir\agent-results-$Timestamp.json"
    $AgentResults | ConvertTo-Json -Depth 10 | Set-Content $ResultsFile
    Write-Log "Agent results saved to: $ResultsFile" "Green"
    
    # Generate summary
    Write-Log "=== Agent Execution Summary ===" "Cyan"
    Write-Log "Total: $($AgentResults.summary.total)" "White"
    Write-Log "Successful: $($AgentResults.summary.successful)" "Green"
    Write-Log "Failed: $($AgentResults.summary.failed)" "Red"
    Write-Log "Skipped: $($AgentResults.summary.skipped)" "Gray"
    
    return $AgentResults
}

# Main execution
try {
    Write-Log "Starting comprehensive agent execution and indexing" "Cyan"
    
    # Step 1: Index codebase
    if (-not $ScanOnly) {
        $CodebaseIndex = Index-Codebase -ProjectPath $ProjectPath -OutputDir $OutputDir
    }
    
    # Step 2: Scan external context
    if (-not $IndexOnly) {
        $ExternalContext = Scan-ExternalContext -ScanPath $ExternalScanPath -OutputDir $OutputDir
    }
    
    # Step 3: Run all agents
    if (-not $IndexOnly -and -not $ScanOnly) {
        $AgentResults = Run-AllAgents -AgentsPath $AgentsPath -ProjectPath $ProjectPath -OutputDir $OutputDir
    }
    
    Write-Log "=== Complete ===" "Green"
    Write-Log "Output directory: $OutputDir" "White"
    Write-Log "Log file: $LogFile" "White"
    
} catch {
    Write-Log "Fatal error: $_" "Red"
    Write-Log $_.ScriptStackTrace "Red"
    exit 1
}

