'use client'

import { useState } from 'react'
import CanvasFormField from '@/components/CanvasFormField'

export default function XDMIQAssessmentPage() {
  const [userId, setUserId] = useState('')
  const [assessmentStarted, setAssessmentStarted] = useState(false)
  const [currentQuestion, setCurrentQuestion] = useState<any>(null)
  const [selectedPreference, setSelectedPreference] = useState('')
  const [customPreference, setCustomPreference] = useState('')
  const [reasoning, setReasoning] = useState('')
  const [previousAnswers, setPreviousAnswers] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [xdmiqScore, setXdmiqScore] = useState<any>(null)

  const startAssessment = async () => {
    if (!userId) {
      alert('Please create an anonymous identity first')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/xdmiq/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      })
      const data = await response.json()
      setCurrentQuestion(data)
      setAssessmentStarted(true)
    } catch (error) {
      console.error('Failed to start XDMIQ assessment:', error)
    } finally {
      setLoading(false)
    }
  }

  const submitAnswer = async () => {
    const finalPreference = selectedPreference === 'other' ? customPreference.trim() : selectedPreference
    
    if (!finalPreference || !reasoning.trim()) {
      alert('Please select a preference (or provide your own) and provide reasoning')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/xdmiq/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          question_number: currentQuestion.question_number,
          preference: finalPreference,
          reasoning: reasoning.trim(),
          previous_answers: previousAnswers,
          is_custom: selectedPreference === 'other'
        })
      })
      const data = await response.json()

      // Add to previous answers
      setPreviousAnswers([
        ...previousAnswers,
        {
          question_number: currentQuestion.question_number,
          preference: finalPreference,
          reasoning: reasoning.trim(),
          is_custom: selectedPreference === 'other'
        }
      ])

      if (data.status === 'complete') {
        setXdmiqScore(data.xdmiq_score)
        setAssessmentStarted(false)
      } else {
        // Next question
        setCurrentQuestion(data)
        setSelectedPreference('')
        setCustomPreference('')
        setReasoning('')
      }
    } catch (error) {
      console.error('Failed to submit answer:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>XDMIQ AI-Native Credentialing</h1>
      <p>Assessment based on your preferences and reasoning</p>

      {!assessmentStarted && !xdmiqScore && (
        <div style={{ marginTop: '2rem' }}>
          <label>
            Anonymous User ID:
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem' }}
            />
          </label>
          <button
            onClick={startAssessment}
            disabled={loading}
            style={{ marginTop: '1rem', padding: '0.75rem 1.5rem', fontSize: '1rem' }}
          >
            {loading ? 'Starting...' : 'Start XDMIQ Assessment'}
          </button>
        </div>
      )}

      {assessmentStarted && currentQuestion && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Question {currentQuestion.question_number}</h2>
          <p style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>
            {currentQuestion.question}
          </p>

          <div style={{ marginBottom: '1rem' }}>
            <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
              <legend style={{ marginBottom: '0.5rem', fontWeight: '600' }}>
                Select an option:
              </legend>
              {currentQuestion.options.map((option: string, idx: number) => (
                <label 
                  key={idx} 
                  style={{ 
                    display: 'block', 
                    marginBottom: '0.75rem',
                    padding: '0.5rem',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s',
                    backgroundColor: selectedPreference === option ? '#e3f2fd' : 'transparent'
                  }}
                  onMouseEnter={(e) => {
                    if (selectedPreference !== option) {
                      e.currentTarget.style.backgroundColor = '#f5f5f5'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedPreference !== option) {
                      e.currentTarget.style.backgroundColor = 'transparent'
                    }
                  }}
                >
                  <input
                    type="radio"
                    name="preference"
                    value={option}
                    checked={selectedPreference === option}
                    onChange={(e) => {
                      setSelectedPreference(e.target.value)
                      setCustomPreference('')
                    }}
                    style={{ marginRight: '0.75rem' }}
                    aria-label={`Select option: ${option}`}
                  />
                  {option}
                </label>
              ))}
              <label 
                style={{ 
                  display: 'block', 
                  marginBottom: '0.75rem',
                  padding: '0.5rem',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s',
                  backgroundColor: selectedPreference === 'other' ? '#e3f2fd' : 'transparent'
                }}
                onMouseEnter={(e) => {
                  if (selectedPreference !== 'other') {
                    e.currentTarget.style.backgroundColor = '#f5f5f5'
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedPreference !== 'other') {
                    e.currentTarget.style.backgroundColor = 'transparent'
                  }
                }}
              >
                <input
                  type="radio"
                  name="preference"
                  value="other"
                  checked={selectedPreference === 'other'}
                  onChange={(e) => {
                    setSelectedPreference(e.target.value)
                    setCustomPreference('')
                  }}
                  style={{ marginRight: '0.75rem' }}
                  aria-label="Select other option"
                />
                Other (specify your own)
              </label>
            </fieldset>
            {selectedPreference === 'other' && (
              <div style={{ marginTop: '0.75rem', marginBottom: '0.75rem' }}>
                <label htmlFor="custom-preference" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Please specify your preference:
                </label>
                <input
                  id="custom-preference"
                  type="text"
                  value={customPreference}
                  onChange={(e) => setCustomPreference(e.target.value)}
                  placeholder="Enter your own answer..."
                  aria-label="Enter your own preference"
                  style={{ 
                    width: '100%', 
                    padding: '0.75rem', 
                    fontSize: '1rem',
                    border: '1px solid #2196f3',
                    borderRadius: '8px',
                    outline: 'none'
                  }}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && customPreference.trim() && reasoning.trim()) {
                      e.preventDefault()
                      submitAnswer()
                    }
                  }}
                  autoFocus
                />
              </div>
            )}
          </div>

          {/* Canvas Form Field for Reasoning */}
          <div style={{ marginBottom: '1rem' }}>
            <CanvasFormField
              label="Why? (Explain your reasoning using Universal Canvas):"
              value={reasoning}
              onChange={(canvasValue) => {
                const reasoningText = canvasValue?.chatMessages?.[canvasValue.chatMessages.length - 1]?.content || 
                                     canvasValue?.lastInput || 
                                     canvasValue?.canvasData || 
                                     ''
                setReasoning(reasoningText)
              }}
              placeholder="Draw, chat, or interact to explain your reasoning..."
              interactiveMode="hybrid"
              aiTrainingEnabled={true}
              onAITraining={(interaction) => {
                console.log('XDMIQ AI Training interaction:', interaction)
              }}
              height={200}
              width={600}
            />
          </div>

          {/* Traditional Text Input for Reasoning */}
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="reasoning-input" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Or type your reasoning here:
            </label>
            <textarea
              id="reasoning-input"
              value={reasoning}
              onChange={(e) => setReasoning(e.target.value)}
              placeholder="Explain why you prefer this option..."
              aria-label="Explain your reasoning"
              aria-required="true"
              style={{ 
                width: '100%', 
                padding: '0.75rem', 
                marginTop: '0.5rem', 
                minHeight: '100px',
                fontSize: '1rem',
                border: '1px solid #ddd',
                borderRadius: '8px',
                outline: 'none',
                fontFamily: 'inherit',
                lineHeight: '1.5'
              }}
            />
          </div>

          {currentQuestion.progress && (
            <p style={{ marginBottom: '1rem', color: '#666' }}>
              Progress: {currentQuestion.progress}
            </p>
          )}

          <button
            onClick={submitAnswer}
            disabled={loading || !selectedPreference || (selectedPreference === 'other' && !customPreference.trim()) || !reasoning.trim()}
            aria-label="Submit your answer"
            style={{ 
              padding: '0.75rem 1.5rem', 
              fontSize: '1rem',
              backgroundColor: (loading || !selectedPreference || (selectedPreference === 'other' && !customPreference.trim()) || !reasoning.trim()) ? '#ccc' : '#2196f3',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: (loading || !selectedPreference || (selectedPreference === 'other' && !customPreference.trim()) || !reasoning.trim()) ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              transition: 'background-color 0.2s'
            }}
          >
            {loading ? 'Submitting...' : 'Submit Answer'}
          </button>
        </div>
      )}

      {xdmiqScore && (
        <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h2>Your XDMIQ Score</h2>
          <div style={{ marginTop: '1rem' }}>
            <p><strong>Overall Score:</strong> {xdmiqScore.overall_score}/100</p>
            <p><strong>Proficiency Score:</strong> {xdmiqScore.proficiency_score}/100</p>
            <p><strong>Reasoning Score:</strong> {xdmiqScore.reasoning_score}/100</p>
            <p><strong>Adaptability Score:</strong> {xdmiqScore.adaptability_score}/100</p>
            
            {xdmiqScore.strengths && xdmiqScore.strengths.length > 0 && (
              <div style={{ marginTop: '1rem' }}>
                <strong>Strengths:</strong>
                <ul>
                  {xdmiqScore.strengths.map((s: string, i: number) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  )
}


