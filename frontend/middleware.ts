import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Handle icon.svg - return directly
  if (pathname === '/icon.svg') {
    const iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2196f3;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1976d2;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background with rounded corners -->
  <rect width="512" height="512" rx="76" fill="url(#bg)"/>
  
  <!-- White border -->
  <rect x="51" y="51" width="410" height="410" rx="61" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="10"/>
  
  <!-- "JM" Monogram -->
  <text x="256" y="320" font-family="Arial, sans-serif" font-size="200" font-weight="bold" fill="#ffffff" text-anchor="middle" dominant-baseline="middle">JM</text>
  
  <!-- Subtle accent - connection lines representing matching -->
  <circle cx="150" cy="150" r="8" fill="rgba(255,255,255,0.5)"/>
  <circle cx="362" cy="150" r="8" fill="rgba(255,255,255,0.5)"/>
  <line x1="150" y1="150" x2="256" y2="280" stroke="rgba(255,255,255,0.3)" stroke-width="3"/>
  <line x1="362" y1="150" x2="256" y2="280" stroke="rgba(255,255,255,0.3)" stroke-width="3"/>
</svg>`
    
    return new NextResponse(iconSvg, {
      headers: {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    })
  }

  // Handle manifest.json - return directly
  if (pathname === '/manifest.json') {
    const manifest = {
      name: "JobMatch.zip - AI Job Matching Platform",
      short_name: "JobMatch",
      description: "AI-powered job matching platform for LLC owners and independent contractors with AI capabilities. Find the longest-lasting job matches first.",
      start_url: "/",
      display: "standalone",
      background_color: "#ffffff",
      theme_color: "#2196f3",
      icons: [
        {
          src: "/icon.svg",
          sizes: "any",
          type: "image/svg+xml",
          purpose: "any maskable"
        },
        {
          src: "/icon-192.png",
          sizes: "192x192",
          type: "image/png"
        },
        {
          src: "/icon-512.png",
          sizes: "512x512",
          type: "image/png"
        }
      ],
      orientation: "any",
      categories: ["business", "productivity"],
      shortcuts: [
        {
          name: "Start Chat",
          short_name: "Chat",
          description: "Chat with JobMatch assistant",
          url: "/",
          icons: [{ src: "/icon.svg", sizes: "any" }]
        },
        {
          name: "Universal Canvas",
          short_name: "Canvas",
          description: "Create a new canvas",
          url: "/canvas?new=true",
          icons: [{ src: "/icon.svg", sizes: "any" }]
        }
      ]
    }
    
    return NextResponse.json(manifest, {
      headers: {
        'Content-Type': 'application/manifest+json',
        'Cache-Control': 'public, max-age=3600, must-revalidate',
      },
    })
  }

  // Handle sw.js - return directly
  if (pathname === '/sw.js') {
    const swContent = `// Service Worker for JobMatch Platform
// Enables offline functionality

const CACHE_NAME = 'jobmatch-v1'
const CACHE_URLS = [
  '/',
  // '/auth' intentionally excluded from cache to prevent stale tokens
  '/canvas',
  '/manifest.json'
]

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CACHE_URLS).catch((err) => {
        console.log('Cache addAll failed:', err)
        // Continue even if some resources fail to cache
      })
    })
  )
  self.skipWaiting()
})

// Fetch event - network-first and NEVER cache auth or API routes
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)
  const isGET = event.request.method === 'GET'
  const isAuth = url.pathname.startsWith('/auth')
  const isAPI = url.pathname.startsWith('/api')
  const hasToken = url.searchParams.has('token')

  if (!isGET || isAuth || isAPI || hasToken) {
    // Bypass cache entirely for auth/API/tokened requests
    event.respondWith(fetch(event.request))
    return
  }

  // Network-first for everything else, cache successful responses for offline
  event.respondWith(
    fetch(event.request).then((networkResponse) => {
      if (networkResponse && networkResponse.ok) {
        const responseClone = networkResponse.clone()
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone))
      }
      return networkResponse
    }).catch(() => caches.match(event.request).then((cached) => cached || (event.request.destination === 'document' ? caches.match('/') : undefined)))
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName)
          }
        })
      )
    })
  )
  self.clients.claim()
})`
    
    return new NextResponse(swContent, {
      headers: {
        'Content-Type': 'application/javascript',
        'Service-Worker-Allowed': '/',
        'Cache-Control': 'public, max-age=3600, must-revalidate',
      },
    })
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/manifest.json', '/sw.js', '/icon.svg'],
}

