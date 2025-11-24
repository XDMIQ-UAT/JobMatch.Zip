import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic'

// Embedded SVG icon content
const iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2196f3;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1976d2;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background with rounded corners -->
  <rect width="512" height="512" rx="76" fill="url(#bg)"/>
  
  <!-- "JM" Monogram -->
  <text x="256" y="320" font-family="Arial, sans-serif" font-size="240" font-weight="700" fill="white" text-anchor="middle" dominant-baseline="middle">JM</text>
</svg>`

export async function GET() {
  // Try to read from public folder first (for development)
  const possiblePaths = [
    path.join(process.cwd(), 'public', 'icon.svg'),
    path.join(process.cwd(), 'frontend', 'public', 'icon.svg'),
    path.join(__dirname, '..', '..', 'public', 'icon.svg'),
  ]
  
  for (const iconPath of possiblePaths) {
    try {
      if (fs.existsSync(iconPath)) {
        const svgContent = fs.readFileSync(iconPath, 'utf-8')
        return new NextResponse(svgContent, {
          headers: {
            'Content-Type': 'image/svg+xml',
            'Cache-Control': 'public, max-age=31536000, immutable',
          },
        })
      }
    } catch (error) {
      // Continue to next path
    }
  }
  
  // Fallback to embedded SVG
  return new NextResponse(iconSvg, {
    headers: {
      'Content-Type': 'image/svg+xml',
      'Cache-Control': 'public, max-age=31536000, immutable',
    },
  })
}

