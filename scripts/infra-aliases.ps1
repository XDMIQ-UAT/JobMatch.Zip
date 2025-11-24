# Infrastructure Agent Convenience Aliases
# Source this file to use shorter commands

# Define shorter function names
function infra-up { E:\JobFinder\scripts\infra-agent.ps1 up @args }
function infra-down { E:\JobFinder\scripts\infra-agent.ps1 down @args }
function infra-status { E:\JobFinder\scripts\infra-agent.ps1 status @args }
function infra-verify { E:\JobFinder\scripts\infra-agent.ps1 verify @args }
function infra-restart { E:\JobFinder\scripts\infra-agent.ps1 restart @args }
function infra-logs { E:\JobFinder\scripts\infra-agent.ps1 logs @args }
function infra-clean { E:\JobFinder\scripts\infra-agent.ps1 clean @args }

Write-Host "Infrastructure Agent aliases loaded!" -ForegroundColor Green
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  infra-up         - Start environment"
Write-Host "  infra-down       - Stop environment"
Write-Host "  infra-status     - Check status"
Write-Host "  infra-verify     - Run verification tests"
Write-Host "  infra-restart    - Restart environment"
Write-Host "  infra-logs       - View logs"
Write-Host "  infra-clean      - Clean all data"
Write-Host ""
Write-Host "To load automatically, add to your PowerShell profile:" -ForegroundColor Yellow
Write-Host "  . E:\JobFinder\scripts\infra-aliases.ps1"
