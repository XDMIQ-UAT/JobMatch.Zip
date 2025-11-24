'use client'

import { useState } from 'react'

export default function ArticulationPage() {
  const [userId, setUserId] = useState('')
  const [originalText, setOriginalText] = useState('')
  const [suggestion, setSuggestion] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleSuggest = async () => {
    if (!userId || !originalText) {
      alert('Please provide user ID and text')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/articulation/suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          original_text: originalText
        })
      })
      const data = await response.json()
      setSuggestion(data)
    } catch (error) {
      console.error('Articulation failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Articulation Assistant</h1>
      <p>Translate your AI work into job market language</p>

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
      </div>

      <div style={{ marginTop: '1rem' }}>
        <label>
          Original Text:
          <textarea
            value={originalText}
            onChange={(e) => setOriginalText(e.target.value)}
            placeholder="Describe your AI work..."
            style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem', minHeight: '100px' }}
          />
        </label>
      </div>

      <button
        onClick={handleSuggest}
        disabled={loading}
        style={{ marginTop: '1rem', padding: '0.75rem 1.5rem', fontSize: '1rem' }}
      >
        {loading ? 'Generating Suggestion...' : 'Get Suggestion'}
      </button>

      {suggestion && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Suggested Text</h2>
          <div style={{ padding: '1rem', border: '1px solid #ccc', marginTop: '1rem' }}>
            <p>{suggestion.suggested_text}</p>
          </div>
          {suggestion.human_refined && <p>✓ Human Refined</p>}
        </div>
      )}
    </main>
  )
}


