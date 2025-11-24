'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log error to console for debugging
    console.error('Application error:', error)
  }, [error])

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '2rem',
      backgroundColor: '#f5f5f5',
      textAlign: 'center'
    }}>
      <div style={{
        maxWidth: '600px',
        width: '100%'
      }}>
        <div style={{
          fontSize: '4rem',
          marginBottom: '1rem'
        }}>
          ⚠️
        </div>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: '700',
          marginBottom: '1rem',
          color: '#d32f2f'
        }}>
          Something went wrong
        </h1>
        <p style={{
          fontSize: '1.125rem',
          color: '#666',
          marginBottom: '2rem',
          lineHeight: '1.6'
        }}>
          We encountered an unexpected error. Don't worry, your data is safe.
        </p>

        {process.env.NODE_ENV === 'development' && error.message && (
          <div style={{
            padding: '1rem',
            backgroundColor: '#fff3cd',
            border: '1px solid #ffc107',
            borderRadius: '8px',
            marginBottom: '2rem',
            textAlign: 'left'
          }}>
            <strong style={{ color: '#856404' }}>Error Details (Dev Only):</strong>
            <pre style={{
              marginTop: '0.5rem',
              fontSize: '0.875rem',
              color: '#856404',
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}>
              {error.message}
              {error.stack && `\n\n${error.stack}`}
            </pre>
          </div>
        )}

        <div style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <button
            onClick={reset}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#2196f3',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'background-color 0.2s',
              fontSize: '1rem'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#1976d2'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#2196f3'
            }}
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.href = '/'}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#fff',
              color: '#2196f3',
              border: '2px solid #2196f3',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s',
              fontSize: '1rem'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f0f7ff'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#fff'
            }}
          >
            Go Home
          </button>
        </div>

        <div style={{
          marginTop: '2rem',
          padding: '1rem',
          backgroundColor: '#e3f2fd',
          borderRadius: '8px',
          fontSize: '0.875rem',
          color: '#1976d2'
        }}>
          <strong>Tip:</strong> If this error persists, try refreshing the page or clearing your browser cache.
        </div>
      </div>
    </div>
  )
}

