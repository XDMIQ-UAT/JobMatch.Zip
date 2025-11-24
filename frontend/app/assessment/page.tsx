'use client'

import { useState, useRef, useEffect } from 'react'
import CanvasFormField from '@/components/CanvasFormField'

interface Message {
  id: string
  type: 'bot' | 'user'
  content: string
  timestamp: Date
  questionId?: string
  quickReplies?: string[]
  showOtherInput?: boolean
  authProviders?: Array<{ id: string; name: string; icon: string }>
}

interface AssessmentData {
  skills: string[]
  projects: any[]
  responses: Record<string, string>
}

const ASSESSMENT_QUESTIONS = [
  {
    id: 'intro',
    question: "Hi! I'm here to help discover what you're capable of. Let's start with a simple question: What do you enjoy doing most?",
    quickReplies: ['Solving problems', 'Creating things', 'Helping others', 'Learning new things', 'Working with others'],
    field: 'enjoyment'
  },
  {
    id: 'strengths',
    question: "Great! Now, what would you say are your main strengths? Think about what comes naturally to you.",
    quickReplies: ['Communication', 'Analysis', 'Creativity', 'Organization', 'Adaptability'],
    field: 'strengths'
  },
  {
    id: 'problems',
    question: "When you encounter a problem you've never seen before, how do you typically approach it?",
    quickReplies: ['Research and learn', 'Ask for help', 'Break it into smaller parts', 'Try different approaches', 'Think it through first'],
    field: 'problem_solving'
  },
  {
    id: 'collaboration',
    question: "How do you prefer to work with others?",
    quickReplies: ['Independently', 'In small teams', 'In large groups', 'As a leader', 'As a supporter'],
    field: 'collaboration'
  },
  {
    id: 'learning',
    question: "What's your favorite way to learn something new?",
    quickReplies: ['Hands-on practice', 'Reading and research', 'Watching tutorials', 'Learning from others', 'Trial and error'],
    field: 'learning_style'
  },
  {
    id: 'goals',
    question: "What kind of work or projects are you most interested in?",
    quickReplies: ['Building products', 'Solving complex problems', 'Creative projects', 'Technical challenges', 'Helping people'],
    field: 'interests'
  }
]

const AUTH_PROVIDERS = [
  { id: 'linkedin', name: 'LinkedIn', icon: '💼' },
  { id: 'microsoft', name: 'Microsoft', icon: '🪟' },
  { id: 'facebook', name: 'Facebook', icon: '📘' },
  { id: 'google', name: 'Google', icon: '🔍' },
  { id: 'apple', name: 'Apple', icon: '🍎' },
  { id: 'email', name: 'Email', icon: '📧' }
]

export default function AssessmentPage() {
  const [userId, setUserId] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(-1) // -1 = auth flow, 0+ = assessment
  const [assessmentData, setAssessmentData] = useState<AssessmentData>({
    skills: [],
    projects: [],
    responses: {}
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [showOtherInput, setShowOtherInput] = useState(false)
  const [otherInputValue, setOtherInputValue] = useState('')
  const [authStep, setAuthStep] = useState<'welcome' | 'select_provider' | 'authenticating' | 'authenticated' | 'email_input' | 'email_code'>('welcome')
  const [email, setEmail] = useState('')
  const [emailCode, setEmailCode] = useState('')
  const [appName, setAppName] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('appName') || 'jobmatch'
    }
    return 'jobmatch'
  })
  const [isEditingName, setIsEditingName] = useState(false)
  const [editingNameValue, setEditingNameValue] = useState(appName)
  const nameInputRef = useRef<HTMLInputElement>(null)
  
  // Sync editingNameValue with appName when appName changes externally
  useEffect(() => {
    if (!isEditingName) {
      setEditingNameValue(appName)
    }
  }, [appName, isEditingName])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const messagesContainerRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = (instant = false) => {
    // Use requestAnimationFrame for reliable scrolling
    requestAnimationFrame(() => {
      if (messagesContainerRef.current) {
        const container = messagesContainerRef.current
        // Scroll to bottom of container
        container.scrollTop = container.scrollHeight
      }
      // Also use the ref method as backup
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ 
          behavior: instant ? 'auto' : 'smooth',
          block: 'end',
          inline: 'nearest'
        })
      }
    })
  }

  useEffect(() => {
    // Scroll to bottom when messages change (smooth)
    if (messages.length > 0) {
      setTimeout(() => scrollToBottom(false), 150)
    }
  }, [messages.length]) // Only trigger on length change, not content

  useEffect(() => {
    // Scroll to bottom when input value changes (user typing - instant)
    if (inputValue && messagesContainerRef.current) {
      requestAnimationFrame(() => {
        if (messagesContainerRef.current) {
          messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight
        }
      })
    }
  }, [inputValue])

  useEffect(() => {
    if (isEditingName && nameInputRef.current) {
      // Use setTimeout to ensure the input is rendered and ready
      const timer = setTimeout(() => {
        if (nameInputRef.current) {
          nameInputRef.current.focus()
          // Don't select - let user position cursor naturally
        }
      }, 10)
      return () => clearTimeout(timer)
    }
  }, [isEditingName])

  const handleNameClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsEditingName(true)
    setEditingNameValue(appName)
  }

  const handleNameBlur = (e?: React.FocusEvent<HTMLInputElement>) => {
    if (e) {
      e.stopPropagation()
    }
    // Save the value immediately
    if (editingNameValue.trim()) {
      setAppName(editingNameValue.trim())
      if (typeof window !== 'undefined') {
        localStorage.setItem('appName', editingNameValue.trim())
      }
    } else {
      setEditingNameValue(appName)
    }
    setIsEditingName(false)
  }

  const handleNameKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    e.stopPropagation()
    if (e.key === 'Enter') {
      e.preventDefault()
      if (nameInputRef.current) {
        nameInputRef.current.blur()
      }
      handleNameBlur()
    } else if (e.key === 'Escape') {
      e.preventDefault()
      setEditingNameValue(appName)
      setIsEditingName(false)
      if (nameInputRef.current) {
        nameInputRef.current.blur()
      }
    }
  }

  // Save conversation to backend
  const saveConversation = async () => {
    if (messages.length === 0) return
    
    try {
      const messagesToSave = messages.map(msg => ({
        id: msg.id,
        type: msg.type,
        content: msg.content,
        timestamp: msg.timestamp.toISOString(),
        questionId: msg.questionId,
        quickReplies: msg.quickReplies,
        authProviders: msg.authProviders
      }))
      
      const response = await fetch('http://localhost:8000/api/conversations/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId || undefined,
          user_id: userId || undefined,
          conversation_type: 'assessment',
          messages: messagesToSave,
          metadata: {
            currentQuestionIndex,
            assessmentData,
            authStep
          }
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.session_id && !sessionId) {
          setSessionId(data.session_id)
          // Update URL with session ID
          window.history.replaceState({}, '', `/assessment?session=${data.session_id}`)
        }
      }
    } catch (error) {
      console.error('Failed to save conversation:', error)
    }
  }

  // Load conversation from session ID
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const sessionParam = urlParams.get('session')
    
    if (sessionParam && messages.length === 0) {
      // Load existing conversation
      fetch(`http://localhost:8000/api/conversations/${sessionParam}`)
        .then(res => res.json())
        .then(data => {
          setSessionId(data.session_id)
          if (data.user_id) setUserId(data.user_id)
          
          // Restore messages
          const restoredMessages: Message[] = data.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
          setMessages(restoredMessages)
          
          // Restore state from metadata
          if (data.metadata) {
            if (data.metadata.currentQuestionIndex !== undefined) {
              setCurrentQuestionIndex(data.metadata.currentQuestionIndex)
            }
            if (data.metadata.assessmentData) {
              setAssessmentData(data.metadata.assessmentData)
            }
            if (data.metadata.authStep) {
              const step = data.metadata.authStep as typeof authStep
              if (['welcome', 'select_provider', 'authenticating', 'authenticated', 'email_input', 'email_code'].includes(step)) {
                setAuthStep(step)
              }
            }
          }
        })
        .catch(error => {
          console.error('Failed to load conversation:', error)
          // Start new conversation if load fails
          startNewConversation()
        })
    } else if (messages.length === 0) {
      startNewConversation()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const startNewConversation = () => {
    const welcomeMessage: Message = {
      id: 'welcome',
      type: 'bot',
      content: "Hi! 👋 Welcome to JobMatch! I'm here to help discover what you're capable of. First, let's get you set up with a quick sign-in. Your identity stays completely anonymous - we just need to verify you're real. Which would you prefer?",
      timestamp: new Date(),
      questionId: 'auth',
      authProviders: AUTH_PROVIDERS
    }
    setMessages([welcomeMessage])
    setAuthStep('select_provider')
  }

  // Auto-save conversation when messages change
  useEffect(() => {
    if (messages.length > 0) {
      const saveTimer = setTimeout(() => {
        saveConversation()
      }, 2000) // Debounce saves
      
      return () => clearTimeout(saveTimer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages.length, userId, sessionId])

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
      let anonymousId = ''
      
      if (provider === 'email') {
        // Email flow - show input for email
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
        anonymousId = data.anonymous_id
        setUserId(anonymousId)
        
        const successMessage: Message = {
          id: `bot-auth-success-${Date.now()}`,
          type: 'bot',
          content: `Great! You're all set. Your anonymous ID is ${anonymousId.slice(0, 8)}... (your identity stays private). Now let's discover what you're capable of!`,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, successMessage])
        
        // Start assessment after brief delay
        setTimeout(() => {
          startAssessment()
        }, 1000)
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
    if (!email.trim()) {
      return
    }

    setLoading(true)
    const userMessage: Message = {
      id: `user-email-${Date.now()}`,
      type: 'user',
      content: email,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    try {
      // Send verification code
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
        content: `Sorry, I couldn't send the email: ${errorMsg}\n\nThis might be due to:\n• Email service configuration issue\n• Email address not verified in SES (if using AWS)\n• Network connectivity problem\n\nLet's try a different sign-in method instead.`,
        timestamp: new Date(),
        questionId: 'auth',
        authProviders: AUTH_PROVIDERS
      }
      setMessages(prev => [...prev, errorMessage])
      setAuthStep('select_provider')
    } finally {
      setLoading(false)
      setEmail('')
    }
  }

  const handleEmailCodeVerify = async () => {
    if (!emailCode.trim() || emailCode.length !== 6) {
      return
    }

    setLoading(true)
    const userMessage: Message = {
      id: `user-code-${Date.now()}`,
      type: 'user',
      content: emailCode,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    try {
      const response = await fetch('http://localhost:8000/api/auth/social/email/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code: emailCode })
      })

      if (response.ok) {
        const data = await response.json()
        const anonymousId = data.anonymous_id
        setUserId(anonymousId)
        
        const successMessage: Message = {
          id: `bot-auth-success-${Date.now()}`,
          type: 'bot',
          content: `Excellent! You're verified. Your anonymous ID is ${anonymousId.slice(0, 8)}... (your identity stays private). Now let's discover what you're capable of!`,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, successMessage])
        
        setTimeout(() => {
          startAssessment()
        }, 1000)
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
      setEmailCode('')
    }
  }

  const startAssessment = () => {
    setAuthStep('authenticated')
    setCurrentQuestionIndex(0)
    const firstQuestion = ASSESSMENT_QUESTIONS[0]
    const assessmentMessage: Message = {
      id: 'assessment-start',
      type: 'bot',
      content: firstQuestion.question,
      timestamp: new Date(),
      questionId: firstQuestion.id,
      quickReplies: firstQuestion.quickReplies
    }
    setMessages(prev => [...prev, assessmentMessage])
  }

  const sendMessage = async (content: string, isQuickReply = false) => {
    if (!content.trim() && !isQuickReply) return

    // Handle auth flow
    if (currentQuestionIndex === -1) {
      if (authStep === 'email_input') {
        setEmail(content.trim())
        return // Will be handled by handleEmailSubmit
      }
      if (authStep === 'email_code') {
        setEmailCode(content.trim())
        return // Will be handled by handleEmailCodeVerify
      }
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setShowOtherInput(false)
    setOtherInputValue('')
    setLoading(true)

    // Store the response if in assessment
    if (currentQuestionIndex >= 0) {
      const currentQuestion = ASSESSMENT_QUESTIONS[currentQuestionIndex]
      setAssessmentData(prev => ({
        ...prev,
        responses: {
          ...prev.responses,
          [currentQuestion.field]: content.trim()
        }
      }))
    }

    // Simulate thinking delay
    await new Promise(resolve => setTimeout(resolve, 800))

    // Check if there are more questions
    if (currentQuestionIndex >= 0 && currentQuestionIndex < ASSESSMENT_QUESTIONS.length - 1) {
      const nextIndex = currentQuestionIndex + 1
      const nextQuestion = ASSESSMENT_QUESTIONS[nextIndex]
      
      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        type: 'bot',
        content: nextQuestion.question,
        timestamp: new Date(),
        questionId: nextQuestion.id,
        quickReplies: nextQuestion.quickReplies
      }
      
      setMessages(prev => [...prev, botMessage])
      setCurrentQuestionIndex(nextIndex)
      setLoading(false)
    } else if (currentQuestionIndex >= 0) {
      // Assessment complete
      await completeAssessment()
    } else {
      setLoading(false)
    }
  }

  const completeAssessment = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/assessment/assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          portfolio_data: {
            skills: assessmentData.skills,
            projects: assessmentData.projects,
            responses: assessmentData.responses
          }
        })
      })
      
      const data = await response.json()
      setResult(data)
      
      const completionMessage: Message = {
        id: `bot-complete-${Date.now()}`,
        type: 'bot',
        content: "Thank you! I've completed your assessment. Your capabilities have been analyzed and you'll be matched with opportunities that fit your strengths.",
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, completionMessage])
    } catch (error) {
      console.error('Assessment failed:', error)
      const errorMessage: Message = {
        id: `bot-error-${Date.now()}`,
        type: 'bot',
        content: "I encountered an error processing your assessment. Please try again.",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (authStep === 'email_input' && email.trim()) {
        handleEmailSubmit()
      } else if (authStep === 'email_code' && emailCode.trim().length === 6) {
        handleEmailCodeVerify()
      } else if (currentQuestionIndex >= 0 && inputValue.trim()) {
        sendMessage(inputValue)
      }
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    setInputValue(value)
    
    if (authStep === 'email_input') {
      setEmail(value)
    } else if (authStep === 'email_code') {
      setEmailCode(value)
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
      <header 
        onClick={(e) => {
          // Prevent header clicks from interfering with input
          if (isEditingName && e.target !== nameInputRef.current) {
            e.stopPropagation()
          }
        }}
        style={{
          padding: '1rem 1.5rem',
          backgroundColor: '#fff',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          position: 'relative',
          zIndex: 1
        }}
      >
        <div 
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          onClick={(e) => {
            // Only stop propagation if not clicking the input
            if (!isEditingName || e.target !== nameInputRef.current) {
              e.stopPropagation()
            }
          }}
        >
          <button
            onClick={(e) => {
              e.stopPropagation()
              window.history.back()
            }}
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
          {isEditingName ? (
            <input
              ref={nameInputRef}
              type="text"
              defaultValue={editingNameValue}
              onBlur={(e) => {
                const newValue = e.currentTarget.value.trim() || appName
                setAppName(newValue)
                if (typeof window !== 'undefined') {
                  localStorage.setItem('appName', newValue)
                }
                setIsEditingName(false)
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  e.currentTarget.blur()
                } else if (e.key === 'Escape') {
                  e.preventDefault()
                  setIsEditingName(false)
                  e.currentTarget.blur()
                }
              }}
              autoFocus
              style={{
                fontSize: '1.25rem',
                fontWeight: '600',
                margin: 0,
                padding: '0.25rem 0.5rem',
                border: '2px solid #2196f3',
                borderRadius: '4px',
                outline: 'none',
                backgroundColor: '#fff',
                minWidth: '100px',
                maxWidth: '200px',
                cursor: 'text',
                position: 'relative',
                zIndex: 1000
              }}
            />
          ) : (
            <h1
              onClick={handleNameClick}
              style={{
                fontSize: '1.25rem',
                fontWeight: '600',
                margin: 0,
                cursor: 'pointer',
                padding: '0.125rem 0.25rem',
                borderRadius: '4px',
                transition: 'background-color 0.2s',
                userSelect: 'none'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f0f0f0'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent'
              }}
            >
              {appName}
            </h1>
          )}
        </div>
        <div style={{ fontSize: '0.875rem', color: '#666', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.25rem' }}>
          {userId ? <span>ID: {userId.slice(0, 8)}...</span> : <span>Getting started...</span>}
          {sessionId && (
            <span style={{ fontSize: '0.75rem', color: '#999' }}>
              Session: {sessionId.slice(0, 8)}...
            </span>
          )}
        </div>
      </header>

      {/* Messages Area */}
      <div 
        ref={messagesContainerRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          padding: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
          maxWidth: '800px',
          margin: '0 auto',
          width: '100%',
          scrollBehavior: 'auto'
        }}
      >
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
                backgroundColor: '#2196f3',
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
              
              {/* Auth Providers - Hide when chat has started */}
              {message.authProviders && message.type === 'bot' && currentQuestionIndex < 0 && (
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

              {/* Quick Replies */}
              {message.quickReplies && message.type === 'bot' && currentQuestionIndex >= 0 && (
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem',
                  marginTop: '0.25rem'
                }}>
                  <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '0.5rem'
                  }}>
                    {message.quickReplies.map((reply, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          setShowOtherInput(false)
                          setOtherInputValue('')
                          sendMessage(reply, true)
                        }}
                        disabled={loading}
                        style={{
                          padding: '0.5rem 1rem',
                          fontSize: '0.875rem',
                          backgroundColor: '#f0f0f0',
                          color: '#333',
                          border: '1px solid #ddd',
                          borderRadius: '20px',
                          cursor: loading ? 'not-allowed' : 'pointer',
                          transition: 'all 0.2s',
                          opacity: loading ? 0.6 : 1
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
                        {reply}
                      </button>
                    ))}
                    <button
                      onClick={() => {
                        setShowOtherInput(!showOtherInput)
                        if (showOtherInput) {
                          setOtherInputValue('')
                        }
                      }}
                      disabled={loading}
                      style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.875rem',
                        backgroundColor: showOtherInput ? '#2196f3' : '#f0f0f0',
                        color: showOtherInput ? '#fff' : '#333',
                        border: `1px solid ${showOtherInput ? '#2196f3' : '#ddd'}`,
                        borderRadius: '20px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        transition: 'all 0.2s',
                        opacity: loading ? 0.6 : 1
                      }}
                    >
                      Other (specify)
                    </button>
                  </div>
                  {showOtherInput && (
                    <div style={{
                      display: 'flex',
                      gap: '0.5rem',
                      alignItems: 'flex-end'
                    }}>
                      <textarea
                        value={otherInputValue}
                        onChange={(e) => {
                          setOtherInputValue(e.target.value)
                          e.target.style.height = 'auto'
                          e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`
                        }}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey && otherInputValue.trim()) {
                            e.preventDefault()
                            sendMessage(otherInputValue.trim())
                            setShowOtherInput(false)
                            setOtherInputValue('')
                          }
                        }}
                        placeholder="Type your own answer..."
                        disabled={loading}
                        style={{
                          flex: 1,
                          padding: '0.75rem',
                          fontSize: '0.875rem',
                          border: '1px solid #2196f3',
                          borderRadius: '8px',
                          resize: 'none',
                          outline: 'none',
                          minHeight: '44px',
                          maxHeight: '120px',
                          fontFamily: 'inherit'
                        }}
                        autoFocus
                      />
                      <button
                        onClick={() => {
                          if (otherInputValue.trim()) {
                            sendMessage(otherInputValue.trim())
                            setShowOtherInput(false)
                            setOtherInputValue('')
                          }
                        }}
                        disabled={loading || !otherInputValue.trim()}
                        style={{
                          padding: '0.75rem 1rem',
                          fontSize: '0.875rem',
                          backgroundColor: (loading || !otherInputValue.trim()) ? '#ccc' : '#2196f3',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: (loading || !otherInputValue.trim()) ? 'not-allowed' : 'pointer',
                          fontWeight: '600'
                        }}
                      >
                        Submit
                      </button>
                    </div>
                  )}
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
              backgroundColor: '#2196f3',
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
      <div style={{
        padding: '1rem 1.5rem',
        backgroundColor: '#fff',
        borderTop: '1px solid #e0e0e0',
        maxWidth: '800px',
        margin: '0 auto',
        width: '100%'
      }}>
        {/* Canvas Form Field - Only show during assessment */}
        {currentQuestionIndex >= 0 && (
          <div style={{ marginBottom: '1rem' }}>
            <CanvasFormField
              label="Or use Universal Canvas to answer interactively:"
              value={assessmentData.responses[ASSESSMENT_QUESTIONS[currentQuestionIndex]?.field]}
              onChange={(canvasValue) => {
                const currentQuestion = ASSESSMENT_QUESTIONS[currentQuestionIndex]
                if (currentQuestion && canvasValue) {
                  setAssessmentData(prev => ({
                    ...prev,
                    responses: {
                      ...prev.responses,
                      [currentQuestion.field]: canvasValue.chatMessages?.[canvasValue.chatMessages.length - 1]?.content || 
                                               canvasValue.lastInput || 
                                               canvasValue.canvasData || 
                                               'Canvas response'
                    }
                  }))
                }
              }}
              placeholder="Draw, chat, or interact to provide your answer..."
              interactiveMode="hybrid"
              aiTrainingEnabled={true}
              onAITraining={(interaction) => {
                console.log('AI Training interaction:', interaction)
              }}
              height={200}
              width={600}
            />
          </div>
        )}

        {/* Text Input */}
        <div style={{
          display: 'flex',
          gap: '0.75rem',
          alignItems: 'flex-end'
        }}>
          <textarea
            value={authStep === 'email_input' ? email : authStep === 'email_code' ? emailCode : inputValue}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder={
              authStep === 'email_input' ? 'Enter your email address...' :
              authStep === 'email_code' ? 'Enter 6-digit code...' :
              currentQuestionIndex >= 0 ? 'Type your answer or select an option above...' :
              'Type your message...'
            }
            disabled={loading || (currentQuestionIndex >= 0 && currentQuestionIndex >= ASSESSMENT_QUESTIONS.length)}
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
              } else if (authStep === 'email_code' && emailCode.trim().length === 6) {
                handleEmailCodeVerify()
              } else if (currentQuestionIndex >= 0 && inputValue.trim()) {
                sendMessage(inputValue)
              }
            }}
            disabled={
              loading || 
              (authStep === 'email_input' && !email.trim()) ||
              (authStep === 'email_code' && emailCode.trim().length !== 6) ||
              (currentQuestionIndex >= 0 && (!inputValue.trim() || currentQuestionIndex >= ASSESSMENT_QUESTIONS.length))
            }
            style={{
              padding: '0.75rem 1.25rem',
              fontSize: '1rem',
              backgroundColor: (
                loading || 
                (authStep === 'email_input' && !email.trim()) ||
                (authStep === 'email_code' && emailCode.trim().length !== 6) ||
                (currentQuestionIndex >= 0 && (!inputValue.trim() || currentQuestionIndex >= ASSESSMENT_QUESTIONS.length))
              ) ? '#ccc' : '#2196f3',
              color: '#fff',
              border: 'none',
              borderRadius: '20px',
              cursor: (
                loading || 
                (authStep === 'email_input' && !email.trim()) ||
                (authStep === 'email_code' && emailCode.trim().length !== 6) ||
                (currentQuestionIndex >= 0 && (!inputValue.trim() || currentQuestionIndex >= ASSESSMENT_QUESTIONS.length))
              ) ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              transition: 'background-color 0.2s'
            }}
          >
            {authStep === 'email_input' ? 'Send Code' :
             authStep === 'email_code' ? 'Verify' :
             'Send'}
          </button>
        </div>
      </div>
    </div>
  )
}
