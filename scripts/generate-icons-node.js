/**
 * Generate PWA icons for JobMatch.zip using Node.js
 * This script creates PNG icons using the 'sharp' library
 * 
 * Install dependencies: npm install sharp --save-dev
 * Run: node scripts/generate-icons-node.js
 */

const fs = require('fs');
const path = require('path');

let sharp;
try {
  // Try to require sharp from frontend/node_modules first
  try {
    sharp = require('../frontend/node_modules/sharp');
  } catch (e) {
    // Fallback to regular require (if installed at root)
    sharp = require('sharp');
  }
} catch (e) {
  console.error('❌ Sharp library not found.');
  console.log('\n📦 To install: cd frontend && npm install sharp --save-dev');
  console.log('\n💡 Alternative: Open frontend/public/generate-icons.html in your browser to generate icons interactively.');
  process.exit(1);
}

const publicDir = path.join(__dirname, '..', 'frontend', 'public');

// Ensure public directory exists
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true });
}

// SVG template for the icon
const svgIcon = `
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
`;

async function generateIcons() {
  const sizes = [192, 512];
  
  console.log('🎨 Generating PWA icons for JobMatch.zip...\n');
  
  for (const size of sizes) {
    try {
      const filename = path.join(publicDir, `icon-${size}.png`);
      
      await sharp(Buffer.from(svgIcon))
        .resize(size, size)
        .png()
        .toFile(filename);
      
      console.log(`✅ Created icon-${size}.png (${size}x${size})`);
    } catch (error) {
      console.error(`❌ Failed to create icon-${size}.png:`, error.message);
    }
  }
  
  console.log('\n✨ Icons generated successfully!');
  console.log(`📁 Location: ${publicDir}`);
}

generateIcons().catch(console.error);

