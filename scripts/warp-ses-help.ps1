# Quick help for Warp: Amazon SES Credentials
# Run this in Warp to get help finding SES credentials

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🔍 Warp: Finding Amazon SES Credentials" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Quick Commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Find credentials:" -ForegroundColor White
Write-Host "   .\scripts\find-ses-credentials.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "   Check configuration:" -ForegroundColor White
Write-Host "   .\scripts\get-ses-config.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "   Test connection:" -ForegroundColor White
Write-Host "   .\scripts\get-ses-config.ps1 -TestConnection" -ForegroundColor Gray
Write-Host ""

Write-Host "📁 Credential Locations:" -ForegroundColor Yellow
Write-Host "   • .env (project root) - Primary location" -ForegroundColor White
Write-Host "   • secrets/ directory - Secondary location" -ForegroundColor White
Write-Host "   • Environment variables (current session)" -ForegroundColor White
Write-Host ""

Write-Host "🔒 Security:" -ForegroundColor Yellow
Write-Host "   ✅ All credential files are in .gitignore" -ForegroundColor Green
Write-Host "   ✅ Scripts never expose actual values" -ForegroundColor Green
Write-Host "   ✅ Safe for Warp terminal" -ForegroundColor Green
Write-Host ""

Write-Host "📖 Full Documentation:" -ForegroundColor Yellow
Write-Host "   docs/WARP_SES_CREDENTIALS.md" -ForegroundColor Gray
Write-Host ""

