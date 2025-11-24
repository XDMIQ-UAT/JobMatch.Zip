'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import AnonymousIdDisplay from '@/components/AnonymousIdDisplay'
import { getApiUrl } from '@/utils/api'

const SOCIAL_PROVIDERS = [
  { id: 'facebook', name: 'Facebook', icon: '📘', color: '#1877f2' },
  { id: 'linkedin', name: 'LinkedIn', icon: '💼', color: '#0077b5' },
  { id: 'google', name: 'Google', icon: '🔍', color: '#4285f4' },
  { id: 'microsoft', name: 'Microsoft', icon: '🪟', color: '#00a4ef' },
  { id: 'apple', name: 'Apple', icon: '🍎', color: '#000000' },
  { id: 'email', name: 'Email', icon: '📧', color: '#2196f3' },
  { id: 'sms', name: 'SMS/VoIP', icon: '📱', color: '#9c27b0' }
]

function ProfileContent() {
  const searchParams = useSearchParams()
  const [anonymousId, setAnonymousId] = useState<string | null>(null)
  const [linkedAccounts, setLinkedAccounts] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)
  const [linking, setLinking] = useState<string | null>(null)
  const API_URL = getApiUrl()

  useEffect(() => {
    // Get anonymous ID from URL or localStorage
    const idFromUrl = searchParams.get('id')
    const idFromStorage = typeof window !== 'undefined' ? localStorage.getItem('anonymous_id') : null
    const anonymousIdValue = idFromUrl || idFromStorage

    if (anonymousIdValue) {
      setAnonymousId(anonymousIdValue)
      loadUserProfile(anonymousIdValue)
    } else {
      setLoading(false)
    }
  }, [searchParams])

  const loadUserProfile = async (id: string) => {
    try {
      const response = await fetch(`${API_URL}/auth/user?anonymous_id=${id}`)
      if (response.ok) {
        const data = await response.json()
        // Extract linked accounts from metadata
        if (data.meta_data?.social_accounts) {
          setLinkedAccounts(data.meta_data.social_accounts)
        }
        // Also check for email/phone
        if (data.meta_data?.emails?.length > 0) {
          setLinkedAccounts(prev => ({
            ...prev,
            email: { linked_at: data.meta_data.emails[0].linked_at }
          }))
        }
        if (data.meta_data?.phone_numbers?.length > 0) {
          setLinkedAccounts(prev => ({
            ...prev,
            sms: { linked_at: data.meta_data.phone_numbers[0].linked_at }
          }))
        }
      }
    } catch (error) {
      console.error('Failed to load profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const linkSocialAccount = async (providerId: string) => {
    if (!anonymousId) {
      alert('Please authenticate first')
      return
    }

    setLinking(providerId)
    try {
      // For email, send magic link
      if (providerId === 'email') {
        const response = await fetch(`${API_URL}/auth/social/email/magic-link`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            email: 'me@myl.zip',
            base_url: typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.host}` : 'https://jobmatch.zip'
          })
        })
        
        if (response.ok) {
          alert('Magic link sent to me@myl.zip. Check your email to complete linking.')
        } else {
          throw new Error('Failed to send magic link')
        }
      } else {
        // For social providers, simulate OAuth flow
        const response = await fetch(`${API_URL}/auth/social/link`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            anonymous_id: anonymousId,
            provider: providerId,
            provider_token: `mock_token_${providerId}_${Date.now()}`,
            provider_data: {
              name: `${providerId} User`,
              email: `user@${providerId}.com`
            }
          })
        })

        if (response.ok) {
          const data = await response.json()
          setLinkedAccounts(prev => ({
            ...prev,
            [providerId]: { linked_at: new Date().toISOString() }
          }))
          alert(`${SOCIAL_PROVIDERS.find(p => p.id === providerId)?.name} account linked successfully!`)
        } else {
          throw new Error('Failed to link account')
        }
      }
    } catch (error) {
      console.error('Failed to link account:', error)
      alert(`Failed to link ${SOCIAL_PROVIDERS.find(p => p.id === providerId)?.name}. Please try again.`)
    } finally {
      setLinking(null)
    }
  }

  const unlinkSocialAccount = async (providerId: string) => {
    if (!anonymousId) return
    
    if (!confirm(`Are you sure you want to unlink your ${SOCIAL_PROVIDERS.find(p => p.id === providerId)?.name} account?`)) {
      return
    }

    try {
      const response = await fetch(`${API_URL}/auth/social/unlink`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          anonymous_id: anonymousId,
          provider: providerId
        })
      })

      if (response.ok) {
        setLinkedAccounts(prev => {
          const updated = { ...prev }
          delete updated[providerId]
          return updated
        })
        alert('Account unlinked successfully')
      } else {
        throw new Error('Failed to unlink account')
      }
    } catch (error) {
      console.error('Failed to unlink account:', error)
      alert('Failed to unlink account. Please try again.')
    }
  }

  if (loading) {
    return (
      <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <h1>Loading Profile...</h1>
      </main>
    )
  }

  if (!anonymousId) {
    return (
      <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
        <h1>Profile</h1>
        <div style={{ 
          padding: '1.5rem', 
          backgroundColor: '#fff3cd', 
          border: '1px solid #ffc107', 
          borderRadius: '8px',
          marginTop: '1rem'
        }}>
          <p style={{ margin: 0 }}>Please authenticate first to view your profile.</p>
          <div style={{ marginTop: '1rem' }}>
            <a 
              href="/auth" 
              style={{ 
                display: 'inline-block', 
                padding: '0.75rem 1.5rem', 
                background: '#2196f3', 
                color: 'white', 
                textDecoration: 'none', 
                borderRadius: '4px' 
              }}
            >
              Go to Authentication
            </a>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Your Profile</h1>
      <p style={{ color: '#666' }}>Manage your anonymous identity and linked accounts.</p>

      {/* Anonymous ID Display */}
      <section style={{ marginTop: '2rem', padding: '1.5rem', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
        <h2 style={{ marginTop: 0 }}>Anonymous Identity</h2>
        <AnonymousIdDisplay anonymousId={anonymousId} showTips={false} />
      </section>

      {/* Linked Accounts */}
      <section style={{ marginTop: '2rem' }}>
        <h2>Linked Accounts</h2>
        <p style={{ color: '#666', fontSize: '0.9em' }}>
          Link multiple authentication methods to your anonymous identity. Your real identity remains protected.
        </p>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', 
          gap: '1rem', 
          marginTop: '1rem' 
        }}>
          {SOCIAL_PROVIDERS.map(provider => {
            const isLinked = linkedAccounts[provider.id]
            const isLinking = linking === provider.id

            return (
              <div
                key={provider.id}
                style={{
                  padding: '1rem',
                  border: `2px solid ${isLinked ? provider.color : '#e0e0e0'}`,
                  borderRadius: '8px',
                  backgroundColor: isLinked ? '#f0f8ff' : 'white',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '0.75rem',
                  position: 'relative'
                }}
              >
                <span style={{ fontSize: '2rem' }}>{provider.icon}</span>
                <span style={{ fontWeight: '600' }}>{provider.name}</span>
                
                {isLinked ? (
                  <>
                    <div style={{ 
                      fontSize: '0.75em', 
                      color: '#666',
                      textAlign: 'center'
                    }}>
                      ✓ Linked
                    </div>
                    <button
                      onClick={() => unlinkSocialAccount(provider.id)}
                      disabled={linking !== null}
                      style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: '#ffebee',
                        color: '#c62828',
                        border: '1px solid #f44336',
                        borderRadius: '4px',
                        cursor: linking !== null ? 'not-allowed' : 'pointer',
                        fontSize: '0.875rem',
                        width: '100%'
                      }}
                    >
                      Unlink
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => linkSocialAccount(provider.id)}
                    disabled={linking !== null}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: provider.color,
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: linking !== null ? 'not-allowed' : 'pointer',
                      fontSize: '0.875rem',
                      width: '100%',
                      opacity: linking !== null ? 0.6 : 1
                    }}
                  >
                    {isLinking ? 'Linking...' : 'Link Account'}
                  </button>
                )}
              </div>
            )
          })}
        </div>
      </section>

      {/* Navigation */}
      <div style={{ marginTop: '2rem', textAlign: 'center' }}>
        <a 
          href="/" 
          style={{ 
            display: 'inline-block', 
            padding: '0.75rem 1.5rem', 
            background: '#2196f3', 
            color: 'white', 
            textDecoration: 'none', 
            borderRadius: '4px',
            marginRight: '0.5rem'
          }}
        >
          Back to Home
        </a>
        <a 
          href="/auth" 
          style={{ 
            display: 'inline-block', 
            padding: '0.75rem 1.5rem', 
            background: '#6c757d', 
            color: 'white', 
            textDecoration: 'none', 
            borderRadius: '4px'
          }}
        >
          Authentication
        </a>
      </div>
    </main>
  )
}

export default function ProfilePage() {
  return (
    <Suspense fallback={
      <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <h1>Loading...</h1>
      </main>
    }>
      <ProfileContent />
    </Suspense>
  )
}

