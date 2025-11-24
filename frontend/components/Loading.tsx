'use client'

export default function Loading() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '2rem',
      backgroundColor: '#f5f5f5'
    }}>
      <div style={{
        width: '48px',
        height: '48px',
        border: '4px solid #e0e0e0',
        borderTop: '4px solid #2196f3',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite'
      }}></div>
      <p style={{
        marginTop: '1rem',
        color: '#666',
        fontSize: '1rem'
      }}>
        Loading...
      </p>
    </div>
  )
}

