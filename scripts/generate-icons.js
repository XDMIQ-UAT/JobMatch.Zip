/**
 * Generate PWA icons for JobMatch.zip
 * Creates icon-192.png and icon-512.png in frontend/public/
 * 
 * Usage: node scripts/generate-icons.js
 */

const fs = require('fs');
const path = require('path');

// Check if canvas package is available
let canvas;
try {
  canvas = require('canvas');
} catch (e) {
  console.log('Canvas package not found. Installing...');
  console.log('Please run: npm install canvas --save-dev');
  console.log('Or use SVG icons instead (already created)');
  process.exit(1);
}

const { createCanvas } = canvas;

const sizes = [192, 512];
const publicDir = path.join(__dirname, '..', 'frontend', 'public');

// Ensure public directory exists
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true });
}

sizes.forEach(size => {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext('2d');

  // Background gradient (blue theme matching #2196f3)
  const gradient = ctx.createLinearGradient(0, 0, size, size);
  gradient.addColorStop(0, '#2196f3');
  gradient.addColorStop(1, '#1976d2');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);

  // Add rounded corners effect
  ctx.globalCompositeOperation = 'destination-in';
  ctx.beginPath();
  const radius = size * 0.15; // 15% corner radius
  ctx.roundRect(0, 0, size, size, radius);
  ctx.fill();

  // Reset composite operation
  ctx.globalCompositeOperation = 'source-over';

  // Draw icon content - "JM" monogram or job matching symbol
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${size * 0.4}px Arial`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  
  // Draw "JM" text
  ctx.fillText('JM', size / 2, size / 2);

  // Add a subtle border
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
  ctx.lineWidth = size * 0.02;
  ctx.strokeRect(size * 0.1, size * 0.1, size * 0.8, size * 0.8);

  // Save as PNG
  const buffer = canvas.toBuffer('image/png');
  const filename = path.join(publicDir, `icon-${size}.png`);
  fs.writeFileSync(filename, buffer);
  console.log(`✓ Created ${filename}`);
});

console.log('\n✅ Icons generated successfully!');

