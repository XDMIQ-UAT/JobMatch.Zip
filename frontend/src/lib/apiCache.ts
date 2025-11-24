/**
 * API Cache utilities for user data
 * Provides caching layer for API requests to reduce redundant calls
 */

interface CacheEntry<T> {
  data: T
  timestamp: number
  expiresAt: number
}

// Simple in-memory cache (5 minute TTL)
const cache = new Map<string, CacheEntry<any>>()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

function getCacheKey(endpoint: string, params?: Record<string, any>): string {
  const paramStr = params ? JSON.stringify(params) : ''
  return `${endpoint}:${paramStr}`
}

function getCached<T>(key: string): T | null {
  const entry = cache.get(key)
  if (!entry) return null
  
  if (Date.now() > entry.expiresAt) {
    cache.delete(key)
    return null
  }
  
  return entry.data as T
}

function setCached<T>(key: string, data: T): void {
  cache.set(key, {
    data,
    timestamp: Date.now(),
    expiresAt: Date.now() + CACHE_TTL
  })
}

/**
 * Fetch user locale with caching
 */
export async function fetchUserLocale(anonymousId: string): Promise<string | null> {
  const cacheKey = getCacheKey('/api/auth/user', { anonymous_id: anonymousId })
  const cached = getCached<string | null>(cacheKey)
  if (cached !== null) {
    return cached
  }
  
  try {
    const apiUrl = typeof window !== 'undefined' 
      ? (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
          ? '/api'
          : 'http://localhost:8001/api')
      : '/api'
    
    const response = await fetch(`${apiUrl}/auth/user?anonymous_id=${anonymousId}`)
    if (!response.ok) {
      return null
    }
    
    const data = await response.json()
    const locale = data.preferred_language || null
    setCached(cacheKey, locale)
    return locale
  } catch (error) {
    console.error('Failed to fetch user locale:', error)
    return null
  }
}

/**
 * Fetch user identity with caching
 */
export async function fetchUserIdentity(anonymousId: string): Promise<any | null> {
  const cacheKey = getCacheKey('/api/auth/user', { anonymous_id: anonymousId })
  const cached = getCached<any>(cacheKey)
  if (cached !== null) {
    return cached
  }
  
  try {
    const apiUrl = typeof window !== 'undefined' 
      ? (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
          ? '/api'
          : 'http://localhost:8001/api')
      : '/api'
    
    const response = await fetch(`${apiUrl}/auth/user?anonymous_id=${anonymousId}`)
    if (!response.ok) {
      return null
    }
    
    const data = await response.json()
    setCached(cacheKey, data)
    return data
  } catch (error) {
    console.error('Failed to fetch user identity:', error)
    return null
  }
}

/**
 * Clear cache for a specific endpoint
 */
export function clearCache(endpoint: string, params?: Record<string, any>): void {
  const key = getCacheKey(endpoint, params)
  cache.delete(key)
}

/**
 * Clear all cache
 */
export function clearAllCache(): void {
  cache.clear()
}
