'use client'

import { useState, useEffect } from 'react'
import { getApiUrl } from '@/utils/api'

export default function LogoutPage() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const API_URL = getApiUrl()

  useEffect(() => {
    const performLogout = async () => {
      try {
        const response = await fetch(`${API_URL}/auth/logout`, {
          method: 'POST',
          credentials: 'include'
        })

        const data = await response.json()
        
        if (response.ok) {
          setStatus('success')
          setMessage(data.message || 'Logged out successfully')
          
          // Clear localStorage
          if (typeof window !== 'undefined') {
            localStorage.removeItem('anonymous_id')
            localStorage.removeItem('chat_messages') // Clear chat history too
          }
          
          // Redirect to home page with logout flag after 2 seconds
          // The logout flag tells HomeChat to clear all state
          setTimeout(() => {
            window.location.replace('/?logout=true')
          }, 2000)
        } else {
          setStatus('error')
          setMessage(data.detail || 'Logout failed')
        }
      } catch (error) {
        setStatus('error')
        setMessage('An error occurred during logout')
        console.error('Logout error:', error)
      }
    }

    performLogout()
  }, [API_URL])

  return (
    <main style={{ 
      padding: '2rem', 
      maxWidth: '600px', 
      margin: '0 auto', 
      textAlign: 'center',
      minHeight: '50vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center'
    }}>
      {status === 'loading' && (
        <>
          <h1>Logging out...</h1>
          <p style={{ color: '#666' }}>Please wait while we sign you out.</p>
        </>
      )}

      {status === 'success' && (
        <>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>✓</div>
          <h1 style={{ color: '#4caf50' }}>Logged Out Successfully</h1>
          <p style={{ color: '#666', marginTop: '1rem' }}>
            {message}
          </p>
          <p style={{ color: '#999', marginTop: '0.5rem' }}>
            Redirecting to home page...
          </p>
        </>
      )}

      {status === 'error' && (
        <>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>⚠</div>
          <h1 style={{ color: '#f44336' }}>Logout Issue</h1>
          <p style={{ 
            color: '#666', 
            marginTop: '1rem',
            padding: '1rem',
            background: '#ffebee',
            borderRadius: '8px',
            border: '1px solid #f44336'
          }}>
            {message}
          </p>
          <div style={{ marginTop: '2rem' }}>
            <a 
              href="/"
              style={{
                display: 'inline-block',
                padding: '0.75rem 1.5rem',
                background: '#2196f3',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '4px',
                fontWeight: '600'
              }}
            >
              Return to Home
            </a>
          </div>
        </>
      )}
    </main>
  )
}
