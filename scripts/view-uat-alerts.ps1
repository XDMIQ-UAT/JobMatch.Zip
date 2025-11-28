# UAT Alerts Dashboard Viewer
# Quick view of critical alerts from UAT monitoring
# Author: Security Team
# Last Updated: 2025-11-25

param(
    [string]$AlertsPath = "E:\zip-jobmatch\logs\uat-alerts.json",
    [switch]$ShowAll,
    [switch]$ClearAlerts
)

function Show-Alert {
    param($Alert)
    
    $color = switch ($Alert.severity) {
        "CRITICAL" { "Red" }
        "WARNING" { "Yellow" }
        default { "White" }
    }
    
    Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor $color
    Write-Host "🚨 ALERT: $($Alert.type)" -ForegroundColor $color
    Write-Host "───────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "Time:     $($Alert.timestamp)" -ForegroundColor Gray
    Write-Host "File:     $($Alert.file)" -ForegroundColor Cyan
    Write-Host "Reason:   $($Alert.reason)" -ForegroundColor Yellow
    
    if ($Alert.contentSnippet) {
        Write-Host "Preview:  $($Alert.contentSnippet.Substring(0, [Math]::Min(100, $Alert.contentSnippet.Length)))..." -ForegroundColor DarkGray
    }
    
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor $color
}

# Check if alerts file exists
if (-not (Test-Path $AlertsPath)) {
    Write-Host "✅ No alerts file found. UAT folder is clean!" -ForegroundColor Green
    exit 0
}

# Clear alerts if requested
if ($ClearAlerts) {
    $confirm = Read-Host "Are you sure you want to clear all alerts? (yes/no)"
    if ($confirm -eq "yes") {
        "[]" | Out-File -FilePath $AlertsPath -Encoding UTF8
        Write-Host "✅ All alerts cleared!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "⚠️  Alert clearing cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Read alerts
$alerts = Get-Content $AlertsPath -Raw | ConvertFrom-Json

if ($alerts.Count -eq 0) {
    Write-Host "✅ No alerts! UAT folder is clean!" -ForegroundColor Green
    exit 0
}

# Display header
Write-Host "`n╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         UAT MONITORING - ALERTS DASHBOARD        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Count by severity
$critical = ($alerts | Where-Object { $_.severity -eq "CRITICAL" }).Count
$warnings = ($alerts | Where-Object { $_.severity -eq "WARNING" }).Count

Write-Host "Total Alerts: $($alerts.Count)" -ForegroundColor White
Write-Host "  Critical:   $critical" -ForegroundColor Red
Write-Host "  Warnings:   $warnings" -ForegroundColor Yellow

# Show alerts
if ($ShowAll) {
    Write-Host "`nShowing all alerts:" -ForegroundColor Cyan
    foreach ($alert in $alerts) {
        Show-Alert -Alert $alert
    }
} else {
    # Show only recent (last 10)
    $recentCount = [Math]::Min(10, $alerts.Count)
    Write-Host "`nShowing most recent $recentCount alerts:" -ForegroundColor Cyan
    $alerts[-$recentCount..-1] | ForEach-Object {
        Show-Alert -Alert $_
    }
    
    if ($alerts.Count -gt 10) {
        Write-Host "`n⚠️  $($alerts.Count - 10) older alerts not shown. Use -ShowAll to see all." -ForegroundColor Yellow
    }
}

# Summary by type
Write-Host "`n📊 Alert Summary by Type:" -ForegroundColor Cyan
$alerts | Group-Object -Property type | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Count)" -ForegroundColor Gray
}

# Action recommendations
Write-Host "`n💡 Recommended Actions:" -ForegroundColor Green
if ($critical -gt 0) {
    Write-Host "  1. Investigate CRITICAL alerts immediately" -ForegroundColor Red
    Write-Host "  2. Check for PII or sensitive data leaks" -ForegroundColor Red
    Write-Host "  3. Review UAT tester activity logs" -ForegroundColor Red
    Write-Host "  4. Contact security team if breach suspected" -ForegroundColor Red
}
Write-Host "  5. Run: .\scripts\monitor-uat-content.ps1 (if not already running)" -ForegroundColor Yellow
Write-Host "  6. Clear alerts after investigation: -ClearAlerts" -ForegroundColor Yellow

Write-Host ""
