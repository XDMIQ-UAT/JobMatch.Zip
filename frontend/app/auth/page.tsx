'use client'

import { useState, useEffect, useRef } from 'react'
import AnonymousIdDisplay from '@/components/AnonymousIdDisplay'
import HomeChat from '@/components/HomeChat'
import { getApiUrl } from '@/utils/api'

export default function AuthPage() {
  const [authMethod, setAuthMethod] = useState<string | null>(null)
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [anonymousId, setAnonymousId] = useState<string | null>(null)
  const [redirecting, setRedirecting] = useState(false)
  const verificationAttempted = useRef(false)

  // Get URL params immediately (not in useEffect)
  const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null
  const urlToken = searchParams?.get('token')
  const urlProvider = searchParams?.get('provider')
  
  // Handle provider query parameter from chat and magic link tokens
  useEffect(() => {
    if (typeof window === 'undefined') return
    
    const token = urlToken
    const provider = urlProvider
    
    console.log('Auth page loaded with params:', { provider, token, authMethod, anonymousId })
    
    // IMPORTANT: Handle magic link token FIRST before checking localStorage
    // This allows users to link additional emails or re-authenticate
    if (token && !provider && authMethod !== 'verifying' && authMethod !== 'authenticated' && !loading && !verificationAttempted.current) {
      console.log('Magic link token detected, starting verification...')
      // Set verifying state immediately to prevent showing auth buttons
      verificationAttempted.current = true
      setAuthMethod('verifying')
      setLoading(true)
      verifyMagicLinkToken(token)
      return
    }
    
    // Check if user is already authenticated (has anonymousId in localStorage)
    // Only redirect if there's NO token to verify
    if (!token) {
      const storedId = localStorage.getItem('anonymous_id')
      if (storedId && !anonymousId) {
        console.log('Found stored anonymous ID:', storedId.substring(0, 8) + '...', 'Redirecting to home')
        // Set redirecting state and redirect
        setRedirecting(true)
        window.location.replace(`/?id=${storedId}&authenticated=true`)
        return
      }
    }
    
    // Handle provider parameter - set auth method immediately
    if (provider && !token) {
      if (provider === 'email') {
        console.log('Setting authMethod to email')
        setAuthMethod('email')
      } else if (provider === 'sms') {
        console.log('Setting authMethod to sms')
        setAuthMethod('sms')
      } else {
        // Auto-trigger social auth
        console.log('Triggering social auth for:', provider)
        handleSocialAuth(provider)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlProvider, urlToken]) // Re-run when provider or token changes
  
  // Secondary check: if token exists in URL but verification hasn't started, start it
  useEffect(() => {
    if (typeof window === 'undefined') return
    if (verificationAttempted.current) return // Skip if already attempted
    
    const urlParams = new URLSearchParams(window.location.search)
    const token = urlParams.get('token')
    
    // If token exists but we're not verifying/authenticated, start verification
    if (token && authMethod !== 'verifying' && authMethod !== 'authenticated' && !loading) {
      console.log('Secondary check: Token detected, starting verification...', { token: token.substring(0, 20) + '...', authMethod, loading })
      verificationAttempted.current = true
      setAuthMethod('verifying')
      setLoading(true)
      verifyMagicLinkToken(token)
    }
  }, [authMethod, loading]) // Re-check when authMethod or loading changes

  // Auto-redirect if authenticated
  useEffect(() => {
    if (anonymousId && !redirecting) {
      setRedirecting(true)
      window.location.replace(`/?id=${anonymousId}&authenticated=true`)
    }
  }, [anonymousId, redirecting])
  
  const verifyMagicLinkToken = async (token: string) => {
    try {
      const apiUrl = getApiUrl()
      console.log('[Magic Link] Verifying token:', token.substring(0, 20) + '...')
      console.log('[Magic Link] API URL:', apiUrl)
      
      // Try the correct endpoint path
      const endpoint = `${apiUrl}/auth/social/magic-link/verify?token=${encodeURIComponent(token)}`
      console.log('[Magic Link] Calling endpoint:', endpoint)
      
      const response = await fetch(endpoint, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        // Add timeout
        signal: AbortSignal.timeout(15000) // 15 second timeout
      })
      
      console.log('[Magic Link] Verification response:', response.status, response.statusText)
      
      if (!response.ok) {
        let errorDetail = `HTTP ${response.status}: ${response.statusText}`
        try {
          const errorData = await response.json()
          errorDetail = errorData.detail || errorData.error || errorDetail
        } catch {
          // If JSON parse fails, use status text
        }
        console.error('[Magic Link] Verification error:', errorDetail)
        throw new Error(errorDetail)
      }
      
      const data = await response.json()
      console.log('[Magic Link] Verified successfully:', { anonymousId: data.anonymous_id?.substring(0, 8) + '...' })
      
      if (!data.anonymous_id) {
        throw new Error('No anonymous ID returned from verification')
      }
      
      // Set state atomically to prevent race conditions
      setAnonymousId(data.anonymous_id)
      
      // Store anonymous ID in localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('anonymous_id', data.anonymous_id)
        console.log('[Magic Link] Stored anonymous ID in localStorage')
      }
      
      // Set redirecting state to prevent rendering
      setRedirecting(true)
      
      // Redirect to home page immediately - don't show auth page
      // Use replace to prevent back button issues
      const redirectUrl = `/?id=${data.anonymous_id}&authenticated=true`
      console.log('[Magic Link] Redirecting to:', redirectUrl)
      window.location.replace(redirectUrl)
      
    } catch (error) {
      console.error('[Magic Link] Verification failed:', error)
      const errorMessage = error instanceof Error ? error.message : 'The link may have expired or already been used.'
      
      // Show error state (don't reset to null)
      setAuthMethod('error')
      setLoading(false)
      
      // Log detailed error for debugging
      console.error('Full error details:', {
        error,
        message: errorMessage,
        token: token.substring(0, 10) + '...'
      })
    }
  }

  const providers = [
    { id: 'facebook', name: 'Facebook', icon: '📘' },
    { id: 'linkedin', name: 'LinkedIn', icon: '💼' },
    { id: 'google', name: 'Google', icon: '🔍' },
    { id: 'microsoft', name: 'Microsoft', icon: '🪟' },
    { id: 'apple', name: 'Apple', icon: '🍎' },
    { id: 'email', name: 'Email', icon: '📧' },
    { id: 'sms', name: 'SMS/VoIP', icon: '📱' }
  ]

  const handleSocialAuth = async (provider: string) => {
    setLoading(true)
    try {
      // In production, would redirect to OAuth provider
      // For now, simulate authentication
      const response = await fetch(`${getApiUrl()}/auth/social/authenticate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: provider,
          provider_token: `mock_token_${provider}_${Date.now()}`
        })
      })
      const data = await response.json()
      setAnonymousId(data.anonymous_id)
      
      // Store anonymous ID in localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('anonymous_id', data.anonymous_id)
      }
      
      // Redirect to home page for personalized chat experience
      setTimeout(() => {
        window.location.href = `/?id=${data.anonymous_id}&authenticated=true`
      }, 1500)
    } catch (error) {
      console.error('Social auth failed:', error)
      // Show error message but don't block - allow retry
      alert('Authentication failed. Please try again or choose a different method.')
    } finally {
      setLoading(false)
    }
  }

  const sendMagicLink = async () => {
    if (!email) {
      alert('Please enter your email address')
      return
    }

    setLoading(true)
    try {
      const apiUrl = getApiUrl()
      const baseUrl = typeof window !== 'undefined' 
        ? `${window.location.protocol}//${window.location.host}`
        : 'https://jobmatch.zip'
      
      console.log('Sending magic link to:', email)
      console.log('API URL:', apiUrl)
      console.log('Base URL:', baseUrl)
      
      const response = await fetch(`${apiUrl}/auth/social/email/magic-link`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, base_url: baseUrl })
      })
      
      console.log('Magic link send response:', response.status, response.statusText)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to send magic link' }))
        console.error('Magic link send error:', errorData)
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('Magic link sent successfully:', data)
      
      // Store email for convenience
      if (typeof window !== 'undefined') {
        localStorage.setItem('last_email', email)
      }
      
      // Show success message
      setAuthMethod('magic_link_sent')
    } catch (error) {
      console.error('Failed to send magic link:', error)
      const errorMsg = error instanceof Error ? error.message : 'Please try again.'
      
      // Clean up duplicate error messages
      let cleanError = errorMsg
      if (errorMsg.includes('Failed to send')) {
        cleanError = errorMsg.replace('Failed to send', '').trim()
      }
      
      // Provide helpful guidance based on error type
      let guidance = ''
      if (cleanError.includes('connect') || cleanError.includes('network')) {
        guidance = '\n\nPlease check your connection and try again.'
      } else {
        guidance = '\n\nPlease try again or contact support if the issue persists.'
      }
      
      alert(`Unable to send magic link: ${cleanError || 'Unknown error'}${guidance}`)
    } finally {
      setLoading(false)
    }
  }

  const sendSMSCode = async () => {
    if (!phone) {
      alert('Please enter your phone number')
      return
    }

    setLoading(true)
    try {
      await fetch(`${getApiUrl()}/auth/social/sms/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone })
      })
      setAuthMethod('sms_verify')
    } catch (error) {
      console.error('Failed to send SMS code:', error)
      alert('Failed to send SMS code. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const verifySMSCode = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${getApiUrl()}/auth/social/sms/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone, code })
      })
      const data = await response.json()
      setAnonymousId(data.anonymous_id)
      
      // Store anonymous ID in localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('anonymous_id', data.anonymous_id)
      }
      
      // Redirect to home page for personalized chat experience
      setTimeout(() => {
        window.location.href = `/?id=${data.anonymous_id}&authenticated=true`
      }, 1500)
    } catch (error) {
      console.error('SMS verification failed:', error)
      alert('Verification failed. Please check your code and try again.')
    } finally {
      setLoading(false)
    }
  }

  // Dark mode CSS variables with white background layer
  const darkModeStyles = `
    /* White/off-white background layer for dark mode - ensures text visibility */
    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #fafafa;
      z-index: -5000;
      pointer-events: none;
    }
    
    /* Also add background to html element */
    html {
      background-color: #fafafa;
    }
    
    @media (prefers-color-scheme: dark) {
      :root {
        --auth-bg: #fafafa;
        --auth-text: #1a1a1a;
        --auth-text-secondary: #4a4a4a;
        --auth-border: #e0e0e0;
      }
      
      /* Ensure white/off-white background in dark mode */
      body::before {
        background-color: #fafafa;
      }
      
      html {
        background-color: #fafafa;
      }
      
      body {
        background-color: #fafafa;
      }
    }
    @media (prefers-color-scheme: light) {
      :root {
        --auth-bg: #fff;
        --auth-text: #333;
        --auth-text-secondary: #666;
        --auth-border: #e0e0e0;
      }
      
      body::before {
        background-color: #fff;
      }
      
      html {
        background-color: #fff;
      }
      
      body {
        background-color: #fff;
      }
    }
  `

  // Standard Banner Component
  const Banner = () => (
    <>
      <style suppressHydrationWarning>{darkModeStyles}</style>
      <header style={{
        padding: 'var(--spacing-md) var(--spacing-lg)',
        backgroundColor: 'var(--auth-bg, #fff)',
        color: 'var(--auth-text, #333)',
        borderBottom: '1px solid var(--auth-border, #e0e0e0)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      flexWrap: 'wrap',
      gap: 'var(--spacing-md)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
        <a href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <h1 style={{ margin: 0, fontSize: 'var(--font-2xl)', fontWeight: '700', color: '#2196f3' }}>
            JobMatch.zip
          </h1>
        </a>
        <span style={{ 
          padding: '0.25rem 0.5rem',
          backgroundColor: '#2196f3',
          color: 'white',
          borderRadius: '4px',
          fontSize: 'var(--font-xs)',
          fontWeight: '600'
        }}>
          REV001
        </span>
      </div>
      <nav style={{ display: 'flex', gap: 'var(--spacing-md)', alignItems: 'center', flexWrap: 'wrap' }}>
        <a href="/" style={{ 
          color: 'var(--text-secondary, #666)', 
          textDecoration: 'none',
          fontSize: 'var(--font-base)',
          transition: 'color 0.2s ease'
        }}
        onMouseEnter={(e) => e.currentTarget.style.color = '#2196f3'}
        onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary, #666)'}
        >
          Home
        </a>
        {anonymousId && (
          <a href={`/profile?id=${anonymousId}`} style={{ 
            color: 'var(--text-secondary, #666)', 
            textDecoration: 'none',
            fontSize: 'var(--font-base)',
            transition: 'color 0.2s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#2196f3'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary, #666)'}
          >
            Profile
          </a>
        )}
      </nav>
    </header>
    </>
  )

  // Standard Footer Component
  const Footer = () => (
    <footer style={{ 
      marginTop: 'var(--spacing-xl)', 
      paddingTop: 'var(--spacing-xl)',
      borderTop: '1px solid var(--border-color, #e0e0e0)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      flexWrap: 'wrap',
      gap: 'var(--spacing-md)'
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        <p className="text-sm" style={{ margin: 0, color: 'var(--text-secondary, #666)' }}>
          © 2025 jobmatch
        </p>
        <p className="text-sm" style={{ margin: 0, color: 'var(--text-secondary, #666)' }}>
          Built with ❤️ for capability-first matching
        </p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', alignItems: 'flex-end' }}>
        <a 
          href="/privacy" 
          className="text-sm hover-link"
          style={{ 
            color: 'var(--text-secondary, #666)',
            textDecoration: 'none',
            transition: 'color 0.2s ease'
          }}
        >
          Privacy
        </a>
        <a 
          href="/how-were-different" 
          className="text-sm hover-link"
          style={{ 
            color: 'var(--text-secondary, #666)',
            textDecoration: 'none',
            transition: 'color 0.2s ease'
          }}
        >
          How we're different
        </a>
        <a 
          href="/feedback" 
          className="text-sm hover-link"
          style={{ 
            color: 'var(--text-secondary, #666)',
            textDecoration: 'none',
            transition: 'color 0.2s ease'
          }}
        >
          Give feedback
        </a>
      </div>
    </footer>
  )

  // Show redirecting state
  if (redirecting) {
    return (
      <>
        <Banner />
        <style suppressHydrationWarning>{darkModeStyles}</style>
        <main className="container container-md" style={{ 
          paddingTop: 'var(--spacing-xl)', 
          paddingBottom: 'var(--spacing-xl)',
          minHeight: 'calc(100vh - 200px)',
          textAlign: 'center',
          backgroundColor: 'var(--auth-bg, #fff)',
          color: 'var(--auth-text, #333)'
        }}>
          <h1 style={{ color: 'var(--auth-text, #333)' }}>Redirecting...</h1>
          <p style={{ color: 'var(--auth-text-secondary, #666)' }}>Taking you to your chat experience.</p>
        </main>
        <Footer />
      </>
    )
  }
  
  // Show loading state when verifying magic link
  // Check for token in URL - if present, show verifying state IMMEDIATELY
  const hasTokenInUrl = !!urlToken
  
  if (authMethod === 'verifying' || (loading && urlToken) || (hasTokenInUrl && !authMethod && !anonymousId)) {
    return (
      <>
        <style suppressHydrationWarning>{darkModeStyles}</style>
        <Banner />
        <main className="container container-md" style={{ 
          paddingTop: 'var(--spacing-xl)', 
          paddingBottom: 'var(--spacing-xl)',
          minHeight: 'calc(100vh - 200px)',
          textAlign: 'center',
          backgroundColor: 'var(--auth-bg, #fff)',
          color: 'var(--auth-text, #333)'
        }}>
          <h1 style={{ color: 'var(--auth-text, #333)' }}>Verifying Magic Link...</h1>
          <p style={{ color: 'var(--auth-text-secondary, #666)' }}>Please wait while we verify your authentication link.</p>
          <div style={{ marginTop: '2rem' }}>
            <div style={{ 
              display: 'inline-block',
              width: '40px',
              height: '40px',
              border: '4px solid var(--auth-border, #f3f3f3)',
              borderTop: '4px solid #2196f3',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></div>
          </div>
          <style>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
        </main>
        <Footer />
      </>
    )
  }

  // Show error state
  if (authMethod === 'error') {
    return (
      <>
        <Banner />
        <style suppressHydrationWarning>{darkModeStyles}</style>
        <main className="container container-md" style={{ 
          paddingTop: 'var(--spacing-xl)', 
          paddingBottom: 'var(--spacing-xl)',
          minHeight: 'calc(100vh - 200px)',
          textAlign: 'center',
          backgroundColor: 'var(--auth-bg, #fff)',
          color: 'var(--auth-text, #333)'
        }}>
          <h1 style={{ color: 'var(--auth-text, #333)' }}>Verification Failed</h1>
          <p style={{ color: '#d32f2f', marginBottom: '1rem' }}>The magic link could not be verified. It may have expired or already been used.</p>
          <p style={{ fontSize: '0.875rem', color: 'var(--auth-text-secondary, #666)', marginBottom: '2rem' }}>
            Check the browser console for detailed error information.
          </p>
          <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="/" style={{ 
              display: 'inline-block', 
              padding: '0.75rem 1.5rem', 
              background: '#2196f3', 
              color: 'white', 
              textDecoration: 'none', 
              borderRadius: '4px',
              transition: 'background 0.2s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = '#1976d2'}
            onMouseLeave={(e) => e.currentTarget.style.background = '#2196f3'}
            >
              Go to Home
            </a>
            <button 
              onClick={() => {
                setAuthMethod(null)
                setLoading(false)
                // Reload page to retry
                window.location.reload()
              }} 
              style={{ 
                padding: '0.75rem 1.5rem',
                background: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'background 0.2s ease'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = '#5a6268'}
              onMouseLeave={(e) => e.currentTarget.style.background = '#6c757d'}
            >
              Try Again
            </button>
          </div>
        </main>
        <Footer />
      </>
    )
  }

  // Show authentication provider selection for direct visits to /auth
  return (
    <>
      <Banner />
      <style suppressHydrationWarning>{darkModeStyles}</style>
      <main className="container container-md" style={{ 
        paddingTop: 'var(--spacing-xl)', 
        paddingBottom: 'var(--spacing-xl)',
        minHeight: 'calc(100vh - 200px)',
        textAlign: 'center',
        backgroundColor: 'var(--auth-bg, #fff)',
        color: 'var(--auth-text, #333)'
      }}>
        <h1 style={{ 
          color: 'var(--auth-text, #333)',
          fontSize: '2rem',
          marginBottom: '1rem',
          fontWeight: '700'
        }}>Create Your Account</h1>
        <p style={{ 
          color: 'var(--auth-text-secondary, #666)',
          marginBottom: '2rem',
          fontSize: '1.125rem'
        }}>Choose your preferred authentication method</p>
        
        {/* Authentication Providers Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem',
          maxWidth: '700px',
          margin: '0 auto',
          padding: '0 1rem'
        }}>
          {providers.map((provider) => (
            <button
              key={provider.id}
              onClick={() => {
                if (provider.id === 'email') {
                  setAuthMethod('email')
                } else if (provider.id === 'sms') {
                  setAuthMethod('sms')
                } else {
                  handleSocialAuth(provider.id)
                }
              }}
              disabled={loading}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem',
                padding: '1rem',
                backgroundColor: loading ? '#f5f5f5' : 'white',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                color: 'var(--auth-text, #333)'
              }}
              onMouseEnter={(e) => {
                if (!loading) {
                  e.currentTarget.style.borderColor = '#2196f3'
                  e.currentTarget.style.backgroundColor = '#f0f7ff'
                }
              }}
              onMouseLeave={(e) => {
                if (!loading) {
                  e.currentTarget.style.borderColor = '#e0e0e0'
                  e.currentTarget.style.backgroundColor = 'white'
                }
              }}
            >
              <span style={{ fontSize: '1.5rem' }}>{provider.icon}</span>
              <span>{provider.name}</span>
            </button>
          ))}
        </div>

        {/* Email Form */}
        {authMethod === 'email' && (
          <div style={{
            marginTop: '2rem',
            maxWidth: '500px',
            marginLeft: 'auto',
            marginRight: 'auto',
            padding: '2rem',
            backgroundColor: 'white',
            border: '2px solid #e0e0e0',
            borderRadius: '12px'
          }}>
            <h2 style={{ 
              fontSize: '1.5rem', 
              marginBottom: '1rem',
              color: 'var(--auth-text, #333)'
            }}>📧 Email Authentication</h2>
            <p style={{ 
              color: 'var(--auth-text-secondary, #666)',
              marginBottom: '1.5rem',
              fontSize: '0.875rem'
            }}>We'll send you a magic link - no password needed.</p>
            <input
              type="email"
              placeholder="your.email@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMagicLink()}
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.75rem',
                fontSize: '1rem',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                marginBottom: '1rem',
                boxSizing: 'border-box'
              }}
            />
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={sendMagicLink}
                disabled={loading || !email}
                style={{
                  flex: 1,
                  padding: '0.75rem',
                  backgroundColor: loading || !email ? '#ccc' : '#2196f3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: loading || !email ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Sending...' : 'Send Magic Link'}
              </button>
              <button
                onClick={() => setAuthMethod(null)}
                disabled={loading}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: 'transparent',
                  color: '#666',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                Back
              </button>
            </div>
          </div>
        )}

        {/* SMS Form */}
        {authMethod === 'sms' && (
          <div style={{
            marginTop: '2rem',
            maxWidth: '500px',
            marginLeft: 'auto',
            marginRight: 'auto',
            padding: '2rem',
            backgroundColor: 'white',
            border: '2px solid #e0e0e0',
            borderRadius: '12px'
          }}>
            <h2 style={{ 
              fontSize: '1.5rem', 
              marginBottom: '1rem',
              color: 'var(--auth-text, #333)'
            }}>📱 SMS Authentication</h2>
            <p style={{ 
              color: 'var(--auth-text-secondary, #666)',
              marginBottom: '1.5rem',
              fontSize: '0.875rem'
            }}>We'll send you a verification code via SMS.</p>
            <input
              type="tel"
              placeholder="+1234567890"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendSMSCode()}
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.75rem',
                fontSize: '1rem',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                marginBottom: '1rem',
                boxSizing: 'border-box'
              }}
            />
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={sendSMSCode}
                disabled={loading || !phone}
                style={{
                  flex: 1,
                  padding: '0.75rem',
                  backgroundColor: loading || !phone ? '#ccc' : '#2196f3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: loading || !phone ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Sending...' : 'Send Code'}
              </button>
              <button
                onClick={() => setAuthMethod(null)}
                disabled={loading}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: 'transparent',
                  color: '#666',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                Back
              </button>
            </div>
          </div>
        )}

        {/* Magic Link Sent Success */}
        {authMethod === 'magic_link_sent' && (
          <div style={{
            marginTop: '2rem',
            maxWidth: '500px',
            marginLeft: 'auto',
            marginRight: 'auto',
            padding: '2rem',
            backgroundColor: '#f0f7ff',
            border: '2px solid #2196f3',
            borderRadius: '12px'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
            <h2 style={{ 
              fontSize: '1.5rem', 
              marginBottom: '1rem',
              color: 'var(--auth-text, #333)'
            }}>Magic Link Sent!</h2>
            <p style={{ 
              color: 'var(--auth-text-secondary, #666)',
              marginBottom: '1rem',
              fontSize: '0.875rem'
            }}>Check your inbox at <strong>{email}</strong></p>
            <p style={{ 
              color: 'var(--auth-text-secondary, #666)',
              fontSize: '0.875rem',
              marginBottom: '1rem'
            }}>Click the link in the email to complete authentication. The link is valid for 24 hours.</p>
            <p style={{ 
              color: 'var(--auth-text-secondary, #666)',
              fontSize: '0.75rem',
              fontStyle: 'italic'
            }}>💡 Don't see the email? Check your spam folder.</p>
          </div>
        )}

        {/* SMS Code Verification */}
        {authMethod === 'sms_verify' && (
          <div style={{
            marginTop: '2rem',
            maxWidth: '500px',
            marginLeft: 'auto',
            marginRight: 'auto',
            padding: '2rem',
            backgroundColor: 'white',
            border: '2px solid #e0e0e0',
            borderRadius: '12px'
          }}>
            <h2 style={{ 
              fontSize: '1.5rem', 
              marginBottom: '1rem',
              color: 'var(--auth-text, #333)'
            }}>Enter Verification Code</h2>
            <p style={{ 
              color: 'var(--auth-text-secondary, #666)',
              marginBottom: '1.5rem',
              fontSize: '0.875rem'
            }}>We sent a 6-digit code to <strong>{phone}</strong></p>
            <input
              type="text"
              placeholder="123456"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && verifySMSCode()}
              disabled={loading}
              maxLength={6}
              style={{
                width: '100%',
                padding: '0.75rem',
                fontSize: '1.5rem',
                textAlign: 'center',
                letterSpacing: '0.5rem',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                marginBottom: '1rem',
                boxSizing: 'border-box',
                fontFamily: 'monospace'
              }}
            />
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={verifySMSCode}
                disabled={loading || code.length !== 6}
                style={{
                  flex: 1,
                  padding: '0.75rem',
                  backgroundColor: loading || code.length !== 6 ? '#ccc' : '#2196f3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: loading || code.length !== 6 ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Verifying...' : 'Verify Code'}
              </button>
              <button
                onClick={() => {
                  setAuthMethod('sms')
                  setCode('')
                }}
                disabled={loading}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: 'transparent',
                  color: '#666',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                Back
              </button>
            </div>
          </div>
        )}

        <div style={{ marginTop: '2rem' }}>
          <a 
            href="/"
            style={{
              color: 'var(--auth-text-secondary, #666)',
              textDecoration: 'none',
              fontSize: '0.875rem'
            }}
          >
            ← Back to Home
          </a>
        </div>
      </main>
      <Footer />
    </>
  )
}



