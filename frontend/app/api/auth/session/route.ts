import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Get backend URL
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    // Forward cookies to backend
    const cookies = request.headers.get('cookie')
    
    const response = await fetch(`${backendUrl}/auth/session`, {
      headers: {
        'Cookie': cookies || '',
      },
    })
    
    if (!response.ok) {
      return NextResponse.json({ error: 'No session' }, { status: 401 })
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Session check failed:', error)
    return NextResponse.json({ error: 'Session check failed' }, { status: 500 })
  }
}
