// Custom HTTPS server for Next.js development
// Usage: node server.js
const { createServer } = require('https');
const { parse } = require('url');
const next = require('next');
const fs = require('fs');
const path = require('path');

const dev = process.env.NODE_ENV !== 'production';
const hostname = 'localhost';
const port = parseInt(process.env.PORT || '8443', 10);

// Try to load certificate files
const certPath = path.join(__dirname, '.cert', 'localhost-cert.pem');
const keyPath = path.join(__dirname, '.cert', 'localhost-key.pem');

let httpsOptions = {};

if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
  httpsOptions = {
    key: fs.readFileSync(keyPath),
    cert: fs.readFileSync(certPath),
  };
  console.log('✅ Using mkcert certificates');
} else {
  // Fallback: generate self-signed certificate
  const selfsigned = require('selfsigned');
  const attrs = [{ name: 'commonName', value: 'localhost' }];
  const pems = selfsigned.generate(attrs, { days: 365 });
  httpsOptions = {
    key: pems.private,
    cert: pems.cert,
  };
  console.log('⚠️  Using self-signed certificate (accept browser warning)');
}

const app = next({ dev, hostname });
const handle = app.getRequestHandler();

app.prepare().then(() => {
  createServer(httpsOptions, async (req, res) => {
    try {
      const parsedUrl = parse(req.url, true);
      await handle(req, res, parsedUrl);
    } catch (err) {
      console.error('Error occurred handling', req.url, err);
      res.statusCode = 500;
      res.end('internal server error');
    }
  }).listen(port, hostname, (err) => {
    if (err) throw err;
    console.log(`✅ Ready on https://${hostname}:${port}`);
    console.log(`   Frontend: https://localhost:${port}`);
  });
});

