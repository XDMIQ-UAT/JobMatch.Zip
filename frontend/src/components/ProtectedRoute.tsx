import React, { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'

interface ProtectedRouteProps {
  children: ReactNode
}

/**
 * ProtectedRoute component that checks if user is authenticated
 * Currently checks for anonymous_id in localStorage as a simple auth check
 * TODO: Replace with proper JWT token or session-based auth check
 */
export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  // Check if user is authenticated
  // For now, we check if they have an anonymous_id stored (from QuickAuth flow)
  // In production, this should check for a valid JWT token or session
  const isAuthenticated = (() => {
    if (typeof window === 'undefined') return false
    
    // Check for anonymous_id (from QuickAuth verification)
    const anonymousId = localStorage.getItem('anonymous_id')
    if (anonymousId) return true
    
    // TODO: Check for JWT token or session token
    // const token = localStorage.getItem('auth_token')
    // if (token) return true
    
    return false
  })()

  if (!isAuthenticated) {
    // Redirect to home page with a message to log in
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

