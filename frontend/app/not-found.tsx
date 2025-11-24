'use client'

import Link from 'next/link'

export default function NotFound() {
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
        <h1 style={{
          fontSize: '6rem',
          fontWeight: '700',
          margin: 0,
          color: '#2196f3',
          lineHeight: '1'
        }}>
          404
        </h1>
        <div style={{
          height: '2px',
          width: '100px',
          backgroundColor: '#2196f3',
          margin: '1.5rem auto'
        }}></div>
        <h2 style={{
          fontSize: '2rem',
          fontWeight: '600',
          marginBottom: '1rem',
          color: '#333'
        }}>
          Page Not Found
        </h2>
        <p style={{
          fontSize: '1.125rem',
          color: '#666',
          marginBottom: '2rem',
          lineHeight: '1.6'
        }}>
          The page you're looking for doesn't exist or has been moved.
        </p>
        
        <div style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <Link
            href="/"
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#2196f3',
              color: '#fff',
              textDecoration: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              transition: 'background-color 0.2s',
              display: 'inline-block'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#1976d2'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#2196f3'
            }}
          >
            Go Home
          </Link>
          <button
            onClick={() => window.history.back()}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#fff',
              color: '#2196f3',
              border: '2px solid #2196f3',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f0f7ff'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#fff'
            }}
          >
            Go Back
          </button>
        </div>

        <div style={{
          marginTop: '3rem',
          padding: '1.5rem',
          backgroundColor: '#fff',
          borderRadius: '8px',
          border: '1px solid #e0e0e0'
        }}>
          <h3 style={{
            fontSize: '1.25rem',
            fontWeight: '600',
            marginBottom: '1rem',
            color: '#333'
          }}>
            Popular Pages
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '1rem',
            marginTop: '1rem'
          }}>
            <Link href="/assessment" style={{ color: '#2196f3', textDecoration: 'none' }}>
              Assessment
            </Link>
            <Link href="/canvas" style={{ color: '#2196f3', textDecoration: 'none' }}>
              Canvas
            </Link>
            <Link href="/matching" style={{ color: '#2196f3', textDecoration: 'none' }}>
              Matching
            </Link>
            <Link href="/auth" style={{ color: '#2196f3', textDecoration: 'none' }}>
              Auth
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

