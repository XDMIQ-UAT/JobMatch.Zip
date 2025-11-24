import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

// Service Worker content
const swContent = `// Service Worker for JobMatch Platform
// Enables offline functionality

const CACHE_NAME = 'jobmatch-v1'
const CACHE_URLS = [
  '/',
  '/auth',
  '/canvas',
  '/api/manifest'
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

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  // Only cache GET requests
  if (event.request.method !== 'GET') {
    return
  }
  
  event.respondWith(
    caches.match(event.request).then((response) => {
      // Return cached version or fetch from network
      return response || fetch(event.request).then((networkResponse) => {
        // Cache successful responses
        if (networkResponse.ok) {
          const responseClone = networkResponse.clone()
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone)
          })
        }
        return networkResponse
      }).catch(() => {
        // If offline and not cached, return offline page
        if (event.request.destination === 'document') {
          return caches.match('/')
        }
      })
    })
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
})
`

export async function GET() {
  return new NextResponse(swContent, {
    headers: {
      'Content-Type': 'application/javascript',
      'Service-Worker-Allowed': '/',
      'Cache-Control': 'public, max-age=3600, must-revalidate',
    },
  })
}
