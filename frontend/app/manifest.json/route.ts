import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    // Try multiple possible paths for manifest.json
    const possiblePaths = [
      path.join(process.cwd(), 'public', 'manifest.json'),
      path.join(process.cwd(), 'frontend', 'public', 'manifest.json'),
      path.join(__dirname, '..', '..', 'public', 'manifest.json'),
    ]
    
    let manifestContent = null
    for (const manifestPath of possiblePaths) {
      if (fs.existsSync(manifestPath)) {
        manifestContent = fs.readFileSync(manifestPath, 'utf-8')
        break
      }
    }
    
    if (!manifestContent) {
      // Fallback: return a basic manifest
      const fallbackManifest = {
        name: "JobMatch.zip - AI Job Matching Platform",
        short_name: "JobMatch",
        description: "AI-powered job matching platform",
        start_url: "/",
        display: "standalone",
        background_color: "#ffffff",
        theme_color: "#2196f3",
        icons: [
          {
            src: "/icon.svg",
            sizes: "any",
            type: "image/svg+xml",
          },
        ],
      }
      return NextResponse.json(fallbackManifest, {
        headers: {
          'Content-Type': 'application/manifest+json',
          'Cache-Control': 'public, max-age=3600, must-revalidate',
        },
      })
    }
    
    const manifest = JSON.parse(manifestContent)
    
    return NextResponse.json(manifest, {
      headers: {
        'Content-Type': 'application/manifest+json',
        'Cache-Control': 'public, max-age=3600, must-revalidate',
      },
    })
  } catch (error) {
    console.error('Error reading manifest.json:', error)
    return NextResponse.json(
      { error: 'Manifest not found' },
      { status: 404 }
    )
  }
}

