'use client'

import { useState, useRef, useEffect } from 'react'
import AnonymousIdDisplay from '@/components/AnonymousIdDisplay'

interface Message {
  id: string
  type: 'bot' | 'user'
  content: string
  timestamp: Date
  questionId?: string
  authProviders?: Array<{ id: string; name: string; icon: string }>
}

const AUTH_PROVIDERS = [
  { id: 'linkedin', name: 'LinkedIn', icon: '💼' },
  { id: 'microsoft', name: 'Microsoft', icon: '🪟' },
  { id: 'facebook', name: 'Facebook', icon: '📘' },
  { id: 'google', name: 'Google', icon: '🔍' },
  { id: 'apple', name: 'Apple', icon: '🍎' },
  { id: 'email', name: 'Email', icon: '📧' },
  { id: 'sms', name: 'SMS/VoIP', icon: '📱' }
]

type RecoveryStage = 'welcome' | 'explanation' | 'reassurance' | 'auth_selection' | 'authenticating' | 'success' | 'email_input' | 'email_code' | 'sms_input' | 'sms_code'

export default function RecoverPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [stage, setStage] = useState<RecoveryStage>('welcome')
  const [loading, setLoading] = useState(false)
  const [anonymousId, setAnonymousId] = useState<string | null>(null)
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [authStep, setAuthStep] = useState<'select_provider' | 'authenticating' | 'email_input' | 'email_code' | 'sms_input' | 'sms_code' | 'authenticated'>('select_provider')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize conversation
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        type: 'bot',
        content: "Hi there. 👋 I understand you've lost your anonymous ID. That can be really frustrating, and I'm here to help you get back on track.",
        timestamp: new Date()
      }
      setMessages([welcomeMessage])
      
      // Auto-advance to explanation after a moment
      setTimeout(() => {
        advanceToExplanation()
      }, 2000)
    }
  }, [])

  const advanceToExplanation = () => {
    const explanationMessage: Message = {
      id: 'explanation',
      type: 'bot',
      content: "Here's the thing: because we use zero-knowledge architecture to protect your privacy, we can't actually recover your anonymous ID. We don't store any information that would let us identify you or link your ID to your real identity - that's by design, to keep you completely anonymous.",
      timestamp: new Date()
    }
    setMessages(prev => [...prev, explanationMessage])
    setStage('explanation')
    
    setTimeout(() => {
      advanceToReassurance()
    }, 3000)
  }

  const advanceToReassurance = () => {
    const reassuranceMessage: Message = {
      id: 'reassurance',
      type: 'bot',
      content: "But don't worry! Setting up again is quick and easy - it takes less than a minute. And the good news is, if you had any assessments or matches saved, those are still in the system. You'll just need to authenticate again to get a new anonymous ID.",
      timestamp: new Date()
    }
    setMessages(prev => [...prev, reassuranceMessage])
    setStage('reassurance')
    
    setTimeout(() => {
      advanceToAuthSelection()
    }, 3000)
  }

  const advanceToAuthSelection = () => {
    const authMessage: Message = {
      id: 'auth-selection',
      type: 'bot',
      content: "Let's get you set up with a new anonymous ID. Choose your preferred authentication method:",
      timestamp: new Date(),
      questionId: 'auth',
      authProviders: AUTH_PROVIDERS
    }
    setMessages(prev => [...prev, authMessage])
    setStage('auth_selection')
    setAuthStep('select_provider')
  }

  const handleAuthProvider = async (provider: string) => {
    setLoading(true)
    setAuthStep('authenticating')
    
    const userMessage: Message = {
      id: `user-auth-${Date.now()}`,
      type: 'user',
      content: `I'll sign in with ${AUTH_PROVIDERS.find(p => p.id === provider)?.name}`,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    try {
      let newAnonymousId = ''
      
      if (provider === 'email') {
        const emailPrompt: Message = {
          id: `bot-email-${Date.now()}`,
          type: 'bot',
          content: "Perfect! Please enter your email address and we'll send you a verification code.",
          timestamp: new Date(),
          questionId: 'email_input'
        }
        setMessages(prev => [...prev, emailPrompt])
        setAuthStep('email_input')
        setLoading(false)
        return
      }

      if (provider === 'sms') {
        const smsPrompt: Message = {
          id: `bot-sms-${Date.now()}`,
          type: 'bot',
          content: "Great! Please enter your phone number and we'll send you a verification code.",
          timestamp: new Date(),
          questionId: 'sms_input'
        }
        setMessages(prev => [...prev, smsPrompt])
        setAuthStep('sms_input')
        setLoading(false)
        return
      }

      // Social auth flow
      const response = await fetch('http://localhost:8000/api/auth/social/authenticate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: provider,
          provider_token: `mock_token_${provider}_${Date.now()}`
        })
      })

      if (response.ok) {
        const data = await response.json()
        newAnonymousId = data.anonymous_id
        setAnonymousId(newAnonymousId)
        setAuthStep('authenticated')
        setStage('success')
        
        const successMessage: Message = {
          id: `bot-success-${Date.now()}`,
          type: 'bot',
          content: `Excellent! You're all set up with a new anonymous ID. Here it is - make sure to save it this time!`,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, successMessage])
      } else {
        throw new Error('Authentication failed')
      }
    } catch (error) {
      console.error('Auth failed:', error)
      const errorMessage: Message = {
        id: `bot-auth-error-${Date.now()}`,
        type: 'bot',
        content: "Hmm, that didn't work. Let's try a different sign-in method. Which would you prefer?",
        timestamp: new Date(),
        questionId: 'auth',
        authProviders: AUTH_PROVIDERS
      }
      setMessages(prev => [...prev, errorMessage])
      setAuthStep('select_provider')
    } finally {
      setLoading(false)
    }
  }

  const handleEmailSubmit = async () => {
    if (!email.trim()) return

    setLoading(true)
    const userMessage: Message = {
      id: `user-email-${Date.now()}`,
      type: 'user',
      content: email,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    try {
      const response = await fetch('http://localhost:8000/api/auth/social/email/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to send email code' }))
        const errorDetail = errorData.detail || errorData.error || `HTTP ${response.status}: ${response.statusText}`
        console.error('Failed to send email:', errorDetail)
        throw new Error(errorDetail)
      }

      const data = await response.json()
      const codePrompt: Message = {
        id: `bot-code-${Date.now()}`,
        type: 'bot',
        content: `Perfect! I've sent a verification code to ${email}. Please enter the 6-digit code you received.${data.verification_code ? `\n\n🔐 Dev mode code: ${data.verification_code}` : ''}`,
        timestamp: new Date(),
        questionId: 'email_code'
      }
      setMessages(prev => [...prev, codePrompt])
      setAuthStep('email_code')
    } catch (error) {
      console.error('Failed to send email:', error)
      const errorMsg = error instanceof Error ? error.message : 'Unknown error'
      const errorMessage: Message = {
        id: `bot-email-error-${Date.now()}`,
        type: 'bot',
        content: `Sorry, I couldn't send the email. This might be due to a connectivity issue or the email service being temporarily unavailable. Let's try a different sign-in method instead.`,
        timestamp: new Date(),
        questionId: 'auth',
        authProviders: AUTH_PROVIDERS
      }
      setMessages(prev => [...prev, errorMessage])
      setAuthStep('select_provider')
    } finally {
      setLoading(false)
    }
  }

  const handleEmailCodeVerify = async () => {
    if (!code.trim() || code.length !== 6) return

    setLoading(true)
    const userMessage: Message = {
      id: `user-code-${Date.now()}`,
      type: 'user',
      content: code,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    try {
      const response = await fetch('http://localhost:8000/api/auth/social/email/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code })
      })

      if (response.ok) {
        const data = await response.json()
        const newAnonymousId = data.anonymous_id
        setAnonymousId(newAnonymousId)
        setAuthStep('authenticated')
        setStage('success')
        
        const successMessage: Message = {
          id: `bot-success-${Date.now()}`,
          type: 'bot',
          content: `Excellent! You're verified and set up with a new anonymous ID. Here it is - make sure to save it this time!`,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, successMessage])
      } else {
        throw new Error('Verification failed')
      }
    } catch (error) {
      console.error('Verification failed:', error)
      const errorMessage: Message = {
        id: `bot-code-error-${Date.now()}`,
        type: 'bot',
        content: "That code doesn't look right. Let's try a different sign-in method instead.",
        timestamp: new Date(),
        questionId: 'auth',
        authProviders: AUTH_PROVIDERS
      }
      setMessages(prev => [...prev, errorMessage])
      setAuthStep('select_provider')
    } finally {
      setLoading(false)
      setCode('')
    }
  }

  const handleSMSSubmit = async () => {
    if (!phone.trim()) return

    setLoading(true)
    const userMessage: Message = {
      id: `user-phone-${Date.now()}`,
      type: 'user',
      content: phone,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    try {
      await fetch('http://localhost:8000/api/auth/social/sms/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone })
      })

      const codePrompt: Message = {
        id: `bot-sms-code-${Date.now()}`,
        type: 'bot',
        content: `Perfect! I've sent a verification code to ${phone}. Please enter the 6-digit code you received.`,
        timestamp: new Date(),
        questionId: 'sms_code'
      }
      setMessages(prev => [...prev, codePrompt])
      setAuthStep('sms_code')
    } catch (error) {
      console.error('Failed to send SMS:', error)
      const errorMessage: Message = {
        id: `bot-sms-error-${Date.now()}`,
        type: 'bot',
        content: "Sorry, I couldn't send the SMS. Let's try a different sign-in method instead.",
        timestamp: new Date(),
        questionId: 'auth',
        authProviders: AUTH_PROVIDERS
      }
      setMessages(prev => [...prev, errorMessage])
      setAuthStep('select_provider')
    } finally {
      setLoading(false)
    }
  }

  const handleSMSCodeVerify = async () => {
    if (!code.trim() || code.length !== 6) return

    setLoading(true)
    const userMessage: Message = {
      id: `user-sms-code-${Date.now()}`,
      type: 'user',
      content: code,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    try {
      const response = await fetch('http://localhost:8000/api/auth/social/sms/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone, code })
      })

      if (response.ok) {
        const data = await response.json()
        const newAnonymousId = data.anonymous_id
        setAnonymousId(newAnonymousId)
        setAuthStep('authenticated')
        setStage('success')
        
        const successMessage: Message = {
          id: `bot-success-${Date.now()}`,
          type: 'bot',
          content: `Excellent! You're verified and set up with a new anonymous ID. Here it is - make sure to save it this time!`,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, successMessage])
      } else {
        throw new Error('Verification failed')
      }
    } catch (error) {
      console.error('Verification failed:', error)
      const errorMessage: Message = {
        id: `bot-sms-code-error-${Date.now()}`,
        type: 'bot',
        content: "That code doesn't look right. Let's try a different sign-in method instead.",
        timestamp: new Date(),
        questionId: 'auth',
        authProviders: AUTH_PROVIDERS
      }
      setMessages(prev => [...prev, errorMessage])
      setAuthStep('select_provider')
    } finally {
      setLoading(false)
      setCode('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (authStep === 'email_input' && email.trim()) {
        handleEmailSubmit()
      } else if (authStep === 'email_code' && code.trim().length === 6) {
        handleEmailCodeVerify()
      } else if (authStep === 'sms_input' && phone.trim()) {
        handleSMSSubmit()
      } else if (authStep === 'sms_code' && code.trim().length === 6) {
        handleSMSCodeVerify()
      }
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    if (authStep === 'email_input') {
      setEmail(value)
    } else if (authStep === 'email_code') {
      setCode(value)
    } else if (authStep === 'sms_input') {
      setPhone(value)
    } else if (authStep === 'sms_code') {
      setCode(value)
    }
    
    // Auto-resize textarea
    e.target.style.height = 'auto'
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh',
      backgroundColor: '#f5f5f5'
    }}>
      {/* Header */}
      <header style={{
        padding: '1rem 1.5rem',
        backgroundColor: '#fff',
        borderBottom: '1px solid #e0e0e0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            onClick={() => window.history.back()}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.2rem',
              cursor: 'pointer',
              padding: '0.25rem 0.5rem'
            }}
          >
            ←
          </button>
          <h1 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>Recover Anonymous ID</h1>
        </div>
        <div style={{ fontSize: '0.875rem', color: '#666' }}>
          {anonymousId ? `New ID: ${anonymousId.slice(0, 8)}...` : 'Getting started...'}
        </div>
      </header>

      {/* Messages Area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        maxWidth: '800px',
        margin: '0 auto',
        width: '100%'
      }}>
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              display: 'flex',
              justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
              alignItems: 'flex-start',
              gap: '0.75rem'
            }}
          >
            {message.type === 'bot' && (
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                backgroundColor: '#ff9800',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                flexShrink: 0
              }}>
                💬
              </div>
            )}
            <div style={{
              maxWidth: '70%',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}>
              <div style={{
                padding: '0.875rem 1.125rem',
                borderRadius: message.type === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                backgroundColor: message.type === 'user' ? '#2196f3' : '#fff',
                color: message.type === 'user' ? '#fff' : '#333',
                boxShadow: message.type === 'bot' ? '0 1px 2px rgba(0,0,0,0.1)' : 'none',
                lineHeight: '1.5'
              }}>
                {message.content}
              </div>
              
              {/* Auth Providers */}
              {message.authProviders && message.type === 'bot' && (
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '0.75rem',
                  marginTop: '0.25rem'
                }}>
                  {message.authProviders.map((provider) => (
                    <button
                      key={provider.id}
                      onClick={() => handleAuthProvider(provider.id)}
                      disabled={loading}
                      style={{
                        padding: '0.75rem 1rem',
                        fontSize: '0.875rem',
                        backgroundColor: '#f0f0f0',
                        color: '#333',
                        border: '1px solid #ddd',
                        borderRadius: '12px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        transition: 'all 0.2s',
                        opacity: loading ? 0.6 : 1,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        justifyContent: 'center'
                      }}
                      onMouseEnter={(e) => {
                        if (!loading) {
                          e.currentTarget.style.backgroundColor = '#e0e0e0'
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!loading) {
                          e.currentTarget.style.backgroundColor = '#f0f0f0'
                        }
                      }}
                    >
                      <span style={{ fontSize: '1.2rem' }}>{provider.icon}</span>
                      <span>{provider.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            {message.type === 'user' && (
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                backgroundColor: '#4caf50',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                flexShrink: 0
              }}>
                👤
              </div>
            )}
          </div>
        ))}
        
        {/* Anonymous ID Display */}
        {anonymousId && stage === 'success' && (
          <div style={{ marginTop: '1rem' }}>
            <AnonymousIdDisplay anonymousId={anonymousId} showTips={true} />
            <div style={{
              marginTop: '1rem',
              padding: '1rem',
              backgroundColor: '#e8f5e9',
              border: '1px solid #4caf50',
              borderRadius: '8px'
            }}>
              <p style={{
                margin: 0,
                fontSize: '0.875rem',
                color: '#2e7d32',
                fontWeight: '600'
              }}>
                ✓ All set! You can now use this ID to access your account.
              </p>
              <a
                href="/"
                style={{
                  display: 'inline-block',
                  marginTop: '0.75rem',
                  padding: '0.5rem 1rem',
                  backgroundColor: '#4caf50',
                  color: '#fff',
                  textDecoration: 'none',
                  borderRadius: '8px',
                  fontSize: '0.875rem',
                  fontWeight: '600'
                }}
              >
                Continue to Platform →
              </a>
            </div>
          </div>
        )}
        
        {loading && (
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start',
            alignItems: 'flex-start',
            gap: '0.75rem'
          }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              backgroundColor: '#ff9800',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.2rem',
              flexShrink: 0
            }}>
              💬
            </div>
            <div style={{
              padding: '0.875rem 1.125rem',
              borderRadius: '18px 18px 18px 4px',
              backgroundColor: '#fff',
              boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
            }}>
              <div style={{ display: 'flex', gap: '0.25rem' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#999' }}></div>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#999' }}></div>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#999' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      {(authStep === 'email_input' || authStep === 'email_code' || authStep === 'sms_input' || authStep === 'sms_code') && (
        <div style={{
          padding: '1rem 1.5rem',
          backgroundColor: '#fff',
          borderTop: '1px solid #e0e0e0',
          maxWidth: '800px',
          margin: '0 auto',
          width: '100%'
        }}>
          <div style={{
            display: 'flex',
            gap: '0.75rem',
            alignItems: 'flex-end'
          }}>
            <textarea
              value={
                authStep === 'email_input' ? email :
                authStep === 'sms_input' ? phone :
                code
              }
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder={
                authStep === 'email_input' ? 'Enter your email address...' :
                authStep === 'sms_input' ? 'Enter your phone number...' :
                'Enter 6-digit code...'
              }
              disabled={loading}
              style={{
                flex: 1,
                padding: '0.75rem',
                fontSize: '1rem',
                border: '1px solid #ddd',
                borderRadius: '20px',
                resize: 'none',
                outline: 'none',
                minHeight: '44px',
                maxHeight: '120px',
                fontFamily: 'inherit',
                lineHeight: '1.5'
              }}
              rows={1}
            />
            <button
              onClick={() => {
                if (authStep === 'email_input' && email.trim()) {
                  handleEmailSubmit()
                } else if (authStep === 'email_code' && code.trim().length === 6) {
                  handleEmailCodeVerify()
                } else if (authStep === 'sms_input' && phone.trim()) {
                  handleSMSSubmit()
                } else if (authStep === 'sms_code' && code.trim().length === 6) {
                  handleSMSCodeVerify()
                }
              }}
              disabled={
                loading ||
                (authStep === 'email_input' && !email.trim()) ||
                (authStep === 'email_code' && code.trim().length !== 6) ||
                (authStep === 'sms_input' && !phone.trim()) ||
                (authStep === 'sms_code' && code.trim().length !== 6)
              }
              style={{
                padding: '0.75rem 1.25rem',
                fontSize: '1rem',
                backgroundColor: (
                  loading ||
                  (authStep === 'email_input' && !email.trim()) ||
                  (authStep === 'email_code' && code.trim().length !== 6) ||
                  (authStep === 'sms_input' && !phone.trim()) ||
                  (authStep === 'sms_code' && code.trim().length !== 6)
                ) ? '#ccc' : '#ff9800',
                color: '#fff',
                border: 'none',
                borderRadius: '20px',
                cursor: (
                  loading ||
                  (authStep === 'email_input' && !email.trim()) ||
                  (authStep === 'email_code' && code.trim().length !== 6) ||
                  (authStep === 'sms_input' && !phone.trim()) ||
                  (authStep === 'sms_code' && code.trim().length !== 6)
                ) ? 'not-allowed' : 'pointer',
                fontWeight: '600',
                transition: 'background-color 0.2s'
              }}
            >
              {authStep === 'email_input' ? 'Send Code' :
               authStep === 'sms_input' ? 'Send Code' :
               authStep === 'email_code' ? 'Verify' :
               'Verify'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

