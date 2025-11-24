# Activate Auth Flow Agent for Warp
# Account: zsbw@proton.me
# Scope: Account-level authentication flows

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Auth Flow Agent Activation" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Account: zsbw@proton.me" -ForegroundColor Green
Write-Host "Scope: Account-level (not personal identity)" -ForegroundColor Green
Write-Host "Agent Type: auth_flow_specialist" -ForegroundColor Green
Write-Host ""

# Check if config file exists
$configFile = "business/identity-proxy/warp-workflows/auth-flow-agent.yaml"
if (Test-Path $configFile) {
    Write-Host "✓ Config file found: $configFile" -ForegroundColor Green
} else {
    Write-Host "✗ Config file not found: $configFile" -ForegroundColor Red
    Write-Host "  Please ensure the file exists before activating the agent." -ForegroundColor Yellow
    exit 1
}

# Display agent responsibilities
Write-Host ""
Write-Host "Agent Responsibilities:" -ForegroundColor Cyan
Write-Host "  • OAuth authentication flows (Facebook, LinkedIn, Google, Microsoft, Apple)" -ForegroundColor White
Write-Host "  • Magic link email authentication" -ForegroundColor White
Write-Host "  • Anonymous session management" -ForegroundColor White
Write-Host "  • Account-level security and session persistence" -ForegroundColor White
Write-Host "  • Pieces MCP integration for knowledge sharing" -ForegroundColor White
Write-Host ""

# Display authentication flows
Write-Host "Authentication Flows Covered:" -ForegroundColor Cyan
Write-Host "  1. OAuth Flow: Initiation → Redirect → Callback → Account Linking → Session" -ForegroundColor White
Write-Host "  2. Magic Link: Request → Generation → Delivery → Verification → Session" -ForegroundColor White
Write-Host "  3. Anonymous: Visit → ID Generation → Storage → Return" -ForegroundColor White
Write-Host ""

# Display available commands
Write-Host "Available Warp Commands:" -ForegroundColor Cyan
Write-Host "  warp auth-status                  # Check agent status" -ForegroundColor White
Write-Host "  warp auth-test-magic-link         # Test magic link flow" -ForegroundColor White
Write-Host "  warp auth-send-magic-link         # Send test magic link" -ForegroundColor White
Write-Host "  warp auth-get-magic-link          # Get magic link for email" -ForegroundColor White
Write-Host "  warp auth-test-endpoint           # Test auth endpoint" -ForegroundColor White
Write-Host "  warp auth-check-ses               # Check SES configuration" -ForegroundColor White
Write-Host "  warp auth-test-simple             # Simple email test" -ForegroundColor White
Write-Host ""

# Check environment variables
Write-Host "Environment Variables Check:" -ForegroundColor Cyan

$requiredVars = @(
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "SES_FROM_EMAIL"
)

$missingVars = @()
foreach ($var in $requiredVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "  ✓ $var is set" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $var is NOT set" -ForegroundColor Red
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Host ""
    Write-Host "Warning: Some environment variables are missing." -ForegroundColor Yellow
    Write-Host "These are required for full authentication functionality." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Missing variables:" -ForegroundColor Yellow
    foreach ($var in $missingVars) {
        Write-Host "  - $var" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Please set these in your .env file or environment." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Agent Status: " -NoNewline -ForegroundColor Cyan
Write-Host "ACTIVE" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Display next steps
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review agent configuration: business/identity-proxy/warp-workflows/auth-flow-agent.yaml" -ForegroundColor White
Write-Host "  2. Read integration guide: business/identity-proxy/warp-workflows/README.md" -ForegroundColor White
Write-Host "  3. Test authentication flows using the commands above" -ForegroundColor White
Write-Host "  4. Monitor auth logs: backend/logs/auth.log" -ForegroundColor White
Write-Host ""

# Display coordination info
Write-Host "Agent Coordination:" -ForegroundColor Cyan
Write-Host "  • Identity Proxy Agent: Anonymous session management" -ForegroundColor White
Write-Host "  • Security Agent: Security validation and breach detection" -ForegroundColor White
Write-Host "  • Pieces Agent: Knowledge sync and context preservation" -ForegroundColor White
Write-Host ""

Write-Host "For help, run: Get-Help $PSCommandPath -Detailed" -ForegroundColor Gray
