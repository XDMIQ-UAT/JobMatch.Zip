# Setup HTTPS for localhost development
# Creates self-signed certificate and starts frontend with HTTPS on port 8443

Write-Host "🔒 Setting up HTTPS for localhost:8443..." -ForegroundColor Green

# Check if mkcert is installed (recommended tool for local HTTPS)
$mkcertInstalled = Get-Command mkcert -ErrorAction SilentlyContinue

if (-not $mkcertInstalled) {
    Write-Host "`n⚠️  mkcert not found. Installing..." -ForegroundColor Yellow
    Write-Host "Please install mkcert:" -ForegroundColor Yellow
    Write-Host "  Windows: choco install mkcert" -ForegroundColor Cyan
    Write-Host "  Or download from: https://github.com/FiloSottile/mkcert/releases" -ForegroundColor Cyan
    Write-Host "`nAlternatively, we can use a simple HTTPS proxy." -ForegroundColor Yellow
    
    # Create a simple HTTPS proxy script instead
    Write-Host "`nCreating HTTPS proxy script..." -ForegroundColor Green
    
    $proxyScript = @"
const https = require('https');
const http = require('http');
const fs = require('fs');
const { createProxyServer } = require('http-proxy-middleware');

// Create self-signed certificate (for development only)
const selfsigned = require('selfsigned');
const attrs = [{ name: 'commonName', value: 'localhost' }];
const pems = selfsigned.generate(attrs, { days: 365 });

// Write certificate files
fs.writeFileSync('./localhost-cert.pem', pems.cert);
fs.writeFileSync('./localhost-key.pem', pems.private);

const proxy = createProxyServer({
  target: 'http://localhost:3000',
  changeOrigin: true,
  ws: true
});

const options = {
  key: pems.private,
  cert: pems.cert
};

const server = https.createServer(options, (req, res) => {
  proxy.web(req, res);
});

server.on('upgrade', (req, socket, head) => {
  proxy.ws(req, socket, head);
});

server.listen(8443, () => {
  console.log('✅ HTTPS proxy running on https://localhost:8443');
  console.log('   Proxying to http://localhost:3000');
  console.log('   ⚠️  Using self-signed certificate - accept browser warning');
});
"@
    
    Set-Location frontend
    
    # Check if http-proxy-middleware is installed
    if (-not (Test-Path "node_modules/http-proxy-middleware")) {
        Write-Host "Installing http-proxy-middleware and selfsigned..." -ForegroundColor Yellow
        npm install --save-dev http-proxy-middleware selfsigned
    }
    
    $proxyScript | Out-File -FilePath "https-proxy.js" -Encoding UTF8
    
    Write-Host "✅ Created HTTPS proxy script" -ForegroundColor Green
    Write-Host "`nTo start HTTPS server:" -ForegroundColor Cyan
    Write-Host "  1. Start frontend: cd frontend && npm run dev" -ForegroundColor White
    Write-Host "  2. Start HTTPS proxy: node https-proxy.js" -ForegroundColor White
    Write-Host "  3. Visit: https://localhost:8443" -ForegroundColor White
    
    Set-Location ..
} else {
    Write-Host "✅ mkcert found" -ForegroundColor Green
    Write-Host "`nGenerating localhost certificate..." -ForegroundColor Yellow
    
    # Install local CA
    mkcert -install
    
    # Generate certificate for localhost
    Set-Location frontend
    if (-not (Test-Path ".cert")) {
        New-Item -ItemType Directory -Path ".cert" | Out-Null
    }
    mkcert -key-file .cert/localhost-key.pem -cert-file .cert/localhost-cert.pem localhost 127.0.0.1 ::1
    
    Write-Host "✅ Certificate generated" -ForegroundColor Green
    Write-Host "`nNow configure Next.js to use HTTPS..." -ForegroundColor Yellow
    
    Set-Location ..
}

