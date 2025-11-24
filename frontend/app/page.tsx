'use client'

import { useEffect, useState, useCallback } from 'react'
import HomeChat from '@/components/HomeChat'
import RotatingHero from '@/components/RotatingHero'

// Force dynamic rendering to avoid static generation issues with event handlers
export const dynamic = 'force-dynamic'

export default function Home() {
  const [anonymousId, setAnonymousId] = useState<string | null>(null)
  const [userLocale, setUserLocale] = useState<string | undefined>(undefined)

  // Memoized hover handlers
  const handleRecoverHoverEnter = useCallback((e: React.MouseEvent<HTMLAnchorElement>) => {
    e.currentTarget.style.background = '#ffe082'
    e.currentTarget.style.borderColor = '#ff8f00'
    e.currentTarget.style.transform = 'translateY(-2px)'
  }, [])

  const handleRecoverHoverLeave = useCallback((e: React.MouseEvent<HTMLAnchorElement>) => {
    e.currentTarget.style.background = '#fff3cd'
    e.currentTarget.style.borderColor = '#ffc107'
    e.currentTarget.style.transform = 'translateY(0)'
  }, [])

  const handleUatHoverEnter = useCallback((e: React.MouseEvent<HTMLAnchorElement>) => {
    e.currentTarget.style.background = '#c8e6c9'
    e.currentTarget.style.borderColor = '#388e3c'
    e.currentTarget.style.transform = 'translateY(-2px)'
  }, [])

  const handleUatHoverLeave = useCallback((e: React.MouseEvent<HTMLAnchorElement>) => {
    e.currentTarget.style.background = '#e8f5e9'
    e.currentTarget.style.borderColor = '#4caf50'
    e.currentTarget.style.transform = 'translateY(0)'
  }, [])

  // Get anonymous ID from session cookie, URL params, or localStorage
  useEffect(() => {
    // Prevent scroll jump on initial load
    if (typeof window !== 'undefined') {
      const initSession = async () => {
        // Check URL params first (from authentication redirect)
        const urlParams = new URLSearchParams(window.location.search)
        const idFromUrl = urlParams.get('id')
        const authenticated = urlParams.get('authenticated')
        
        let sessionId: string | null = null
        
        // First, try to get session from cookie (secure, token-based)
        try {
          const sessionResponse = await fetch('/api/auth/session', {
            credentials: 'include'
          })
          
          if (sessionResponse.ok) {
            const sessionData = await sessionResponse.json()
            sessionId = sessionData.anonymous_id
            
            if (sessionData.preferred_language) {
              setUserLocale(sessionData.preferred_language)
            }
            
            // Sync to localStorage for backwards compatibility
            if (sessionId) {
              localStorage.setItem('anonymous_id', sessionId)
            }
          }
        } catch (error) {
          // Silently fail - no active session is expected for new users
        }
        
        // Fallback to URL param or localStorage if no session cookie
        if (!sessionId) {
          const storedId = idFromUrl || localStorage.getItem('anonymous_id')
          if (storedId) {
            sessionId = storedId
            
            // Save to localStorage if from URL
            if (idFromUrl) {
              localStorage.setItem('anonymous_id', idFromUrl)
            }
            
            // Fetch user locale from API
            try {
              const userResponse = await fetch(`/api/auth/user?anonymous_id=${storedId}`)
              const data = await userResponse.json()
              if (data.preferred_language) {
                setUserLocale(data.preferred_language)
              }
            } catch (error) {
              // Silently fail, will use browser locale
            }
          }
        }
        
        if (sessionId) {
          setAnonymousId(sessionId)
        }
        
        // Only restore scroll if we're coming from auth redirect
        if (idFromUrl || authenticated) {
          // Save scroll position before any layout shifts
          const scrollY = window.scrollY
          
          // Restore scroll position after layout stabilizes
          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              if (scrollY > 0) {
                window.scrollTo({ top: scrollY, behavior: 'instant' })
              }
            })
          })
        }
      }
      
      initSession()
    }
  }, [])

  return (
    <main className="container container-lg" style={{ 
      paddingTop: 'var(--spacing-xl)', 
      paddingBottom: 'var(--spacing-xl)',
      minHeight: '100vh'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--spacing-md)', flexWrap: 'wrap', gap: 'var(--spacing-md)' }}>
        <div style={{ flex: 1 }}>
          <RotatingHero locale={userLocale} anonymousId={anonymousId || undefined} />
          <p className="text-lg" style={{ marginBottom: 'var(--spacing-md)' }}>
            The first job matching platform for LLC owners who work with AI. 
            <strong> Find the longest-lasting matches first</strong> - capability-first matching that prioritizes quality over quantity.
          </p>
          <p className="text-base" style={{ marginBottom: 0, color: '#666' }}>
            🌍 Anonymous-First · 🤖 AI-Powered · 🎯 Longevity Focused
          </p>
          <p className="text-sm" style={{ marginTop: 'var(--spacing-xs)', color: '#666' }}>
            Part of the <a href="https://xdmiq.com" target="_blank" rel="noopener noreferrer" style={{ color: 'inherit', textDecoration: 'underline' }}>XDMIQ ecosystem</a> · Privacy-first principles
          </p>
        </div>
        <div style={{
          padding: 'var(--spacing-sm) var(--spacing-md)',
          backgroundColor: '#2196f3',
          color: 'white',
          borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
          fontSize: 'var(--font-base)',
          fontWeight: '600',
          whiteSpace: 'nowrap',
          alignSelf: 'flex-start'
        }}>
          REV001
        </div>
      </div>

      {/* Chat Experience - Featured Prominently */}
      <section style={{ marginTop: 'calc(var(--spacing-xl) * 2)', marginBottom: 'calc(var(--spacing-xl) * 2)' }}>
        <div style={{
          padding: 'var(--spacing-xl)',
          background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
          borderRadius: 'clamp(8px, 1vw + 4px, 12px)',
          marginBottom: 'var(--spacing-xl)',
          border: '2px solid #2196f3',
          textAlign: 'center'
        }}>
          <h2 className="text-2xl" style={{ marginTop: 0, marginBottom: 'var(--spacing-md)', color: '#1976d2' }}>
            💬 Start Your Journey - Chat with Us!
          </h2>
          <p className="text-lg" style={{ marginBottom: 'var(--spacing-lg)', color: '#1565c0' }}>
            Get personalized help finding opportunities that match your AI capabilities. 
            Our assistant will guide you through authentication and help you get started.
          </p>
          <HomeChat anonymousId={anonymousId} authenticated={!!anonymousId} />
        </div>
      </section>
      
      <section style={{ marginTop: 'calc(var(--spacing-xl) * 2)', marginBottom: 'calc(var(--spacing-xl) * 2)' }}>
        <h2 className="text-2xl" style={{ marginBottom: 'var(--spacing-md)' }}>
          Why We Show Longest Matches First
        </h2>
        <p className="text-base" style={{ marginBottom: 'var(--spacing-md)' }}>
          At JobMatch.zip, we prioritize <strong>longest-lasting job matches first</strong> because quality relationships matter more than quick placements. Many LLC owners and independent contractors have deep AI capabilities but struggle to:
        </p>
        <ul className="text-base" style={{ 
          paddingLeft: 'var(--spacing-lg)',
          display: 'grid',
          gap: 'var(--spacing-sm)',
          listStylePosition: 'outside'
        }}>
          <li>Articulate their skills in traditional resume formats</li>
          <li>Translate their practical AI work into job market language</li>
          <li>Match with opportunities that value their actual capabilities</li>
          <li>Overcome credential-based gatekeeping</li>
        </ul>
      </section>

      <section style={{ marginTop: 'calc(var(--spacing-xl) * 2)' }}>
        <h2 className="text-2xl" style={{ marginBottom: 'var(--spacing-lg)' }}>
          Get Started
        </h2>
        <div style={{ 
          padding: 'var(--spacing-xl)', 
          background: '#e3f2fd', 
          borderRadius: 'clamp(8px, 1vw + 4px, 12px)', 
          marginBottom: 'var(--spacing-xl)',
          border: '2px solid #2196f3',
          containerType: 'inline-size'
        }}>
          <h3 className="text-xl" style={{ marginTop: 0, color: '#1976d2', marginBottom: 'var(--spacing-md)' }}>
            🎨 Universal Canvas
          </h3>
          <p className="text-lg" style={{ marginBottom: 'var(--spacing-lg)' }}>
            <strong>Start here:</strong> A canvas workspace that works anywhere with basic internet.
            Create, plan, collaborate - works offline, low bandwidth optimized.
          </p>
          <a 
            href="/canvas" 
            className="canvas-link-button"
            style={{ 
              display: 'inline-block',
              padding: 'var(--spacing-md) var(--spacing-xl)', 
              background: '#2196f3', 
              color: 'white', 
              textDecoration: 'none',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              fontWeight: 'bold',
              fontSize: 'var(--font-lg)',
              transition: 'background 0.2s ease'
            }}
          >
            Open Universal Canvas →
          </a>
        </div>
        <nav className="grid-responsive" style={{ 
          gap: 'var(--spacing-md)',
          marginTop: 'var(--spacing-lg)'
        }}>
          <a 
            href="/assessment" 
            className="text-base hover-card"
            style={{ 
              display: 'block',
              padding: 'var(--spacing-md)',
              background: '#f5f5f5',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              border: '1px solid #e0e0e0',
              transition: 'all 0.2s ease'
            }}
          >
            Assess Your AI Capabilities
          </a>
          <a 
            href="/matching" 
            className="text-base hover-card"
            style={{ 
              display: 'block',
              padding: 'var(--spacing-md)',
              background: '#f5f5f5',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              border: '1px solid #e0e0e0',
              transition: 'all 0.2s ease'
            }}
          >
            Find Matches
          </a>
          <a 
            href="/articulation" 
            className="text-base hover-card"
            style={{ 
              display: 'block',
              padding: 'var(--spacing-md)',
              background: '#f5f5f5',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              border: '1px solid #e0e0e0',
              transition: 'all 0.2s ease'
            }}
          >
            Improve Your Articulation
          </a>
          <a 
            href="/forums" 
            className="text-base hover-card"
            style={{ 
              display: 'block',
              padding: 'var(--spacing-md)',
              background: '#f5f5f5',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              border: '1px solid #e0e0e0',
              transition: 'all 0.2s ease'
            }}
          >
            Community Forums
          </a>
          <a 
            href="/xdmiq" 
            className="text-base hover-card"
            style={{ 
              display: 'block',
              padding: 'var(--spacing-md)',
              background: '#f5f5f5',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              border: '1px solid #e0e0e0',
              transition: 'all 0.2s ease'
            }}
          >
            XDMIQ Assessment
          </a>
          <a 
            href="/auth" 
            className="text-base hover-card"
            style={{ 
              display: 'block',
              padding: 'var(--spacing-md)',
              background: '#f5f5f5',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              border: '1px solid #e0e0e0',
              transition: 'all 0.2s ease'
            }}
          >
            Authenticate (Facebook, LinkedIn, Google, Microsoft, Apple, Email, SMS)
          </a>
          <a 
            href="/recover" 
            className="text-base"
            style={{ 
              display: 'block',
              padding: 'var(--spacing-md)',
              background: '#fff3cd',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              border: '2px solid #ffc107',
              transition: 'all 0.2s ease',
              fontWeight: '600'
            }}
            onMouseEnter={handleRecoverHoverEnter}
            onMouseLeave={handleRecoverHoverLeave}
          >
            🔑 Lost Your Anonymous ID?
          </a>
          <a 
            href="/marketplace" 
            className="text-base hover-card"
            style={{ 
              display: 'block',
              padding: 'var(--spacing-md)',
              background: '#f5f5f5',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              border: '1px solid #e0e0e0',
              transition: 'all 0.2s ease'
            }}
          >
            Marketplace (Buy/Sell Goods & Services)
          </a>
          <a 
            href="/uat" 
            className="text-base"
            style={{ 
              display: 'block',
              padding: 'var(--spacing-md)',
              background: '#fff3cd',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              border: '2px solid #ffc107',
              transition: 'all 0.2s ease',
              fontWeight: '600'
            }}
            onMouseEnter={handleRecoverHoverEnter}
            onMouseLeave={handleRecoverHoverLeave}
          >
            🧪 UAT Testing Portal
          </a>
          <a 
            href="http://localhost:3000/uat" 
            target="_blank"
            rel="noopener noreferrer"
            className="text-base"
            style={{ 
              display: 'block',
              padding: 'var(--spacing-md)',
              background: '#e8f5e9',
              borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
              border: '2px solid #4caf50',
              transition: 'all 0.2s ease',
              fontWeight: '600'
            }}
            onMouseEnter={handleUatHoverEnter}
            onMouseLeave={handleUatHoverLeave}
          >
            🔗 UAT (Localhost:3000)
          </a>
        </nav>
      </section>

      <footer style={{ 
        marginTop: 'var(--spacing-xl)', 
        paddingTop: 'var(--spacing-xl)',
        borderTop: '1px solid #e0e0e0'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--spacing-lg)',
          marginBottom: 'var(--spacing-lg)'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <h3 className="text-base" style={{ margin: 0, fontWeight: 'bold', color: '#333' }}>JobMatch</h3>
            <p className="text-sm" style={{ margin: 0, color: '#666' }}>
              Capability-first matching for LLC owners
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <h3 className="text-base" style={{ margin: 0, fontWeight: 'bold', color: '#333' }}>Our Ecosystem</h3>
            <a 
              href="https://xdmiq.com" 
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm hover-link"
              style={{ color: '#666', textDecoration: 'none', transition: 'color 0.2s ease' }}
            >
              XDMIQ - Privacy Infrastructure
            </a>
            <a 
              href="https://yourl.cloud" 
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm hover-link"
              style={{ color: '#666', textDecoration: 'none', transition: 'color 0.2s ease' }}
            >
              Yourl.Cloud - Tech Support
            </a>
            <a 
              href="https://jobmatch.zip" 
              className="text-sm hover-link"
              style={{ color: '#666', textDecoration: 'none', transition: 'color 0.2s ease' }}
            >
              JobMatch - AI Job Matching
            </a>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <h3 className="text-base" style={{ margin: 0, fontWeight: 'bold', color: '#333' }}>Learn More</h3>
            <a 
              href="/privacy" 
              className="text-sm hover-link"
              style={{ color: '#666', textDecoration: 'none', transition: 'color 0.2s ease' }}
            >
              Privacy
            </a>
            <a 
              href="/how-were-different" 
              className="text-sm hover-link"
              style={{ color: '#666', textDecoration: 'none', transition: 'color 0.2s ease' }}
            >
              How we're different
            </a>
            <a 
              href="/feedback" 
              className="text-sm hover-link"
              style={{ color: '#666', textDecoration: 'none', transition: 'color 0.2s ease' }}
            >
              Give feedback
            </a>
          </div>
        </div>
        <div style={{ 
          paddingTop: 'var(--spacing-md)',
          borderTop: '1px solid #e0e0e0',
          textAlign: 'center'
        }}>
          <p className="text-sm" style={{ margin: 0, color: '#666' }}>
            © 2025 JobMatch · Built with ❤️ for capability-first matching
          </p>
          <p className="text-sm" style={{ marginTop: '0.5rem', color: '#666' }}>
            Privacy-first principles · Part of the XDMIQ ecosystem
          </p>
        </div>
        <div style={{ 
          width: '100%', 
          marginTop: 'var(--spacing-md)',
          paddingTop: 'var(--spacing-md)',
          borderTop: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'center',
          flexWrap: 'wrap',
          gap: 'var(--spacing-sm)',
          alignItems: 'center'
        }}>
          <span className="text-sm" style={{ color: '#666', marginRight: 'var(--spacing-xs)' }}>
            Authentication powered by:
          </span>
          <a 
            href="https://www.linkedin.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm hover-link"
            style={{ 
              color: '#666',
              textDecoration: 'none',
              transition: 'color 0.2s ease'
            }}
          >
            LinkedIn
          </a>
          <span style={{ color: '#ccc' }}>•</span>
          <a 
            href="https://www.facebook.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm hover-link"
            style={{ 
              color: '#666',
              textDecoration: 'none',
              transition: 'color 0.2s ease'
            }}
          >
            Facebook
          </a>
          <span style={{ color: '#ccc' }}>•</span>
          <a 
            href="https://www.google.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm hover-link"
            style={{ 
              color: '#666',
              textDecoration: 'none',
              transition: 'color 0.2s ease'
            }}
          >
            Google
          </a>
          <span style={{ color: '#ccc' }}>•</span>
          <a 
            href="https://www.microsoft.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm hover-link"
            style={{ 
              color: '#666',
              textDecoration: 'none',
              transition: 'color 0.2s ease'
            }}
          >
            Microsoft
          </a>
          <span style={{ color: '#ccc' }}>•</span>
          <a 
            href="https://www.apple.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm hover-link"
            style={{ 
              color: '#666',
              textDecoration: 'none',
              transition: 'color 0.2s ease'
            }}
          >
            Apple
          </a>
        </div>
      </footer>
    </main>
  )
}

