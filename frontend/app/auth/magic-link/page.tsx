'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import AnonymousIdDisplay from '@/components/AnonymousIdDisplay'
import { getApiUrl } from '@/utils/api'

function MagicLinkContent() {
  const searchParams = useSearchParams()
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [anonymousId, setAnonymousId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const API_URL = getApiUrl()

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    if (!tokenParam) {
      setError('No magic link token provided')
      setLoading(false)
      return
    }

    setToken(tokenParam)
    verifyMagicLink(tokenParam)
  }, [searchParams])

  // Auto-redirect when authenticated
  useEffect(() => {
    if (anonymousId) {
      const timer = setTimeout(() => {
        window.location.href = '/?authenticated=true'
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [anonymousId])

  const verifyMagicLink = async (magicToken: string) => {
    try {
      const response = await fetch(`${API_URL}/auth/social/magic-link/verify?token=${magicToken}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'  // Include cookies for session
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Verification failed' }))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      const data = await response.json()
      // Session cookie is now set automatically
      setAnonymousId(data.anonymous_id)
      
      // Still persist to localStorage for backwards compatibility
      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem('anonymous_id', data.anonymous_id)
        } catch {}
      }
    } catch (error) {
      console.error('Magic link verification failed:', error)
      setError(error instanceof Error ? error.message : 'Verification failed. The link may have expired or already been used.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <main style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
        <h1>Verifying Magic Link...</h1>
        <p>Please wait while we verify your authentication link.</p>
      </main>
    )
  }

  if (error) {
    return (
      <main style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
        <h1>Verification Failed</h1>
        <div style={{ 
          padding: '1rem', 
          backgroundColor: '#ffebee', 
          border: '1px solid #f44336', 
          borderRadius: '8px',
          marginTop: '1rem'
        }}>
          <p style={{ color: '#c62828', margin: 0 }}>{error}</p>
        </div>
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <a 
            href="/auth?provider=email" 
            style={{ 
              display: 'inline-block', 
              padding: '0.75rem 1.5rem', 
              background: '#2196f3', 
              color: 'white', 
              textDecoration: 'none', 
              borderRadius: '4px' 
            }}
          >
            Request New Magic Link
          </a>
        </div>
      </main>
    )
  }

  if (anonymousId) {
    // Redirect to home - session cookie is already set
    const redirectUrl = '/?authenticated=true'

    return (
      <main style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>✅ Authentication Successful!</h1>
        <AnonymousIdDisplay anonymousId={anonymousId} showTips={true} />
        <p style={{ textAlign: 'center', marginTop: '1rem', color: '#666' }}>Redirecting you back to the platform...</p>
        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <a 
            href={redirectUrl}
            style={{ 
              display: 'inline-block', 
              padding: '0.75rem 1.5rem', 
              background: '#0066cc', 
              color: 'white', 
              textDecoration: 'none', 
              borderRadius: '4px' 
            }}
          >
            Continue Now
          </a>
        </div>
      </main>
    )
  }

  return null
}

export default function MagicLinkPage() {
  return (
    <Suspense fallback={
      <main style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
        <h1>Loading...</h1>
        <p>Please wait while we load the magic link verification page.</p>
      </main>
    }>
      <MagicLinkContent />
    </Suspense>
  )
}

