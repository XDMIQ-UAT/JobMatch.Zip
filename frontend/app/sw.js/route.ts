import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    // Try multiple possible paths for sw.js
    const possiblePaths = [
      path.join(process.cwd(), 'public', 'sw.js'),
      path.join(process.cwd(), 'frontend', 'public', 'sw.js'),
      path.join(__dirname, '..', '..', 'public', 'sw.js'),
    ]
    
    let swContent = null
    for (const swPath of possiblePaths) {
      if (fs.existsSync(swPath)) {
        swContent = fs.readFileSync(swPath, 'utf-8')
        break
      }
    }
    
    if (!swContent) {
      // Fallback: return a basic service worker
      swContent = `// Service Worker for JobMatch.zip
const CACHE_NAME = 'jobmatch-v1'
self.addEventListener('install', () => self.skipWaiting())
self.addEventListener('activate', () => self.clients.claim())
self.addEventListener('fetch', (event) => {
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)))
})`
    }
    
    return new NextResponse(swContent, {
      headers: {
        'Content-Type': 'application/javascript',
        'Service-Worker-Allowed': '/',
        'Cache-Control': 'public, max-age=0, must-revalidate',
      },
    })
  } catch (error) {
    console.error('Error reading sw.js:', error)
    return NextResponse.json(
      { error: 'Service worker not found' },
      { status: 404 }
    )
  }
}

