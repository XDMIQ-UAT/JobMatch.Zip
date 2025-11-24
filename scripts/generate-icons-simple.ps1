# PowerShell script to generate PWA icons using ImageMagick or create SVG fallback
# This script creates simple PNG icons for JobMatch.zip

$publicDir = Join-Path $PSScriptRoot "..\frontend\public"
$publicDir = Resolve-Path $publicDir -ErrorAction SilentlyContinue

if (-not $publicDir) {
    $publicDir = Join-Path $PSScriptRoot "..\frontend\public"
    New-Item -ItemType Directory -Path $publicDir -Force | Out-Null
}

Write-Host "Generating PWA icons for JobMatch.zip..." -ForegroundColor Cyan

# Check if ImageMagick is available
$magick = Get-Command magick -ErrorAction SilentlyContinue

if ($magick) {
    Write-Host "Using ImageMagick to generate PNG icons..." -ForegroundColor Green
    
    # Generate 192x192 icon
    & magick -size 192x192 `
        xc:"#2196f3" `
        -fill white `
        -font Arial-Bold `
        -pointsize 76 `
        -gravity center `
        -annotate +0+0 "JM" `
        -bordercolor "#1976d2" `
        -border 10 `
        "$publicDir\icon-192.png"
    
    # Generate 512x512 icon
    & magick -size 512x512 `
        xc:"#2196f3" `
        -fill white `
        -font Arial-Bold `
        -pointsize 200 `
        -gravity center `
        -annotate +0+0 "JM" `
        -bordercolor "#1976d2" `
        -border 25 `
        "$publicDir\icon-512.png"
    
    Write-Host "✓ Icons generated successfully!" -ForegroundColor Green
} else {
    Write-Host "ImageMagick not found. Creating SVG icons instead..." -ForegroundColor Yellow
    Write-Host "Note: Modern browsers support SVG in manifest.json" -ForegroundColor Yellow
    
    # Copy SVG icon
    $svgContent = @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2196f3;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1976d2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="76" fill="url(#bg)"/>
  <rect x="51" y="51" width="410" height="410" rx="61" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="10"/>
  <text x="256" y="320" font-family="Arial, sans-serif" font-size="200" font-weight="bold" fill="#ffffff" text-anchor="middle" dominant-baseline="middle">JM</text>
  <circle cx="150" cy="150" r="8" fill="rgba(255,255,255,0.5)"/>
  <circle cx="362" cy="150" r="8" fill="rgba(255,255,255,0.5)"/>
  <line x1="150" y1="150" x2="256" y2="280" stroke="rgba(255,255,255,0.3)" stroke-width="3"/>
  <line x1="362" y1="150" x2="256" y2="280" stroke="rgba(255,255,255,0.3)" stroke-width="3"/>
</svg>
"@
    
    Set-Content -Path "$publicDir\icon.svg" -Value $svgContent
    
    Write-Host "✓ SVG icon created at $publicDir\icon.svg" -ForegroundColor Green
    Write-Host "To generate PNG icons, install ImageMagick or use an online converter" -ForegroundColor Yellow
}

