'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function RedirectPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to canvas as initial public experience
    router.push('/canvas')
  }, [router])

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      <p>Redirecting to Universal Canvas...</p>
      <a href="/canvas" style={{ color: '#2196f3' }}>Click here if not redirected</a>
    </div>
  )
}

