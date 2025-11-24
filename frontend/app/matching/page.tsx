'use client'

import { useState, useEffect } from 'react'

export default function MatchingPage() {
  const [userId, setUserId] = useState('')
  const [matches, setMatches] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  // Auto-load userId from localStorage
  useEffect(() => {
    const storedId = localStorage.getItem('anonymous_id')
    if (storedId) {
      setUserId(storedId)
    }
  }, [])

  const handleGenerateMatches = async () => {
    if (!userId) {
      alert('Please create an anonymous identity first')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/matching/generate/${userId}?limit=10`, {
        method: 'POST'
      })
      const data = await response.json()
      setMatches(data)
    } catch (error) {
      console.error('Matching failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem', padding: '1.5rem', background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)', borderRadius: '8px', border: '2px solid #2196f3' }}>
        <h1 style={{ marginTop: 0, color: '#1976d2' }}>🎯 Longest-Lasting Matches First</h1>
        <p style={{ fontSize: '1.1rem', marginBottom: 0 }}>
          Our matching algorithm prioritizes <strong>long-term engagement quality</strong> over quick placements. 
          We predict which opportunities will keep you engaged and growing for months or years, not just days.
        </p>
      </div>

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

      <button
        onClick={handleGenerateMatches}
        disabled={loading}
        style={{ marginTop: '1rem', padding: '0.75rem 1.5rem', fontSize: '1rem' }}
      >
        {loading ? 'Generating Matches...' : 'Generate Matches'}
      </button>

      {matches.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h2 style={{ marginBottom: '1.5rem' }}>Your Matches (Sorted by Longevity)</h2>
          <div style={{ display: 'grid', gap: '1.5rem' }}>
            {matches.map((match) => {
              const isHighLongevity = (match.predicted_months || 0) >= 18
              const isLongTerm = (match.predicted_months || 0) >= 12
              
              return (
                <div 
                  key={match.match_id} 
                  style={{ 
                    padding: '1.5rem', 
                    border: isHighLongevity ? '3px solid #4caf50' : '2px solid #e0e0e0',
                    borderRadius: '8px',
                    background: isHighLongevity ? '#f1f8f4' : '#fff',
                    position: 'relative',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }}
                >
                  {isHighLongevity && (
                    <div style={{
                      position: 'absolute',
                      top: '-12px',
                      right: '20px',
                      background: '#4caf50',
                      color: 'white',
                      padding: '4px 12px',
                      borderRadius: '12px',
                      fontSize: '0.85rem',
                      fontWeight: 'bold'
                    }}>
                      ⭐ High Longevity Match
                    </div>
                  )}
                  
                  {/* Longevity Prediction - Most Prominent */}
                  <div style={{ 
                    marginBottom: '1rem', 
                    padding: '1rem', 
                    background: isHighLongevity ? '#c8e6c9' : '#e3f2fd', 
                    borderRadius: '6px',
                    borderLeft: `4px solid ${isHighLongevity ? '#4caf50' : '#2196f3'}`
                  }}>
                    <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.25rem' }}>
                      Predicted Engagement Duration
                    </div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: isHighLongevity ? '#2e7d32' : '#1976d2' }}>
                      {match.predicted_months || 'N/A'} months
                      {isLongTerm && ' 🎉'}
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.25rem' }}>
                      Longevity Score: {match.longevity_score || 'N/A'}/100
                    </div>
                  </div>

                  {/* Job Details */}
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <h3 style={{ margin: 0 }}>Job #{match.job_posting_id}</h3>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <span style={{ 
                          padding: '0.25rem 0.75rem', 
                          background: '#2196f3', 
                          color: 'white', 
                          borderRadius: '4px',
                          fontSize: '0.85rem'
                        }}>
                          Overall: {match.match_score}/100
                        </span>
                        <span style={{ 
                          padding: '0.25rem 0.75rem', 
                          background: '#ff9800', 
                          color: 'white', 
                          borderRadius: '4px',
                          fontSize: '0.85rem'
                        }}>
                          Skill Fit: {match.compatibility_score || 'N/A'}/100
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Longevity Factors */}
                  {match.longevity_factors && match.longevity_factors.length > 0 && (
                    <div style={{ marginBottom: '1rem' }}>
                      <strong style={{ color: '#4caf50' }}>Why This Match Will Last:</strong>
                      <ul style={{ marginTop: '0.5rem', marginBottom: 0, paddingLeft: '1.5rem' }}>
                        {match.longevity_factors.map((factor: string, i: number) => (
                          <li key={i} style={{ color: '#2e7d32', marginBottom: '0.25rem' }}>{factor}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Match Reasons */}
                  {match.match_reasons && match.match_reasons.length > 0 && (
                    <div style={{ marginBottom: '1rem' }}>
                      <strong>Match Highlights:</strong>
                      <ul style={{ marginTop: '0.5rem', marginBottom: 0, paddingLeft: '1.5rem' }}>
                        {match.match_reasons.slice(0, 5).map((reason: string, i: number) => (
                          <li key={i} style={{ marginBottom: '0.25rem' }}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Human Review Badge */}
                  {match.human_reviewed && (
                    <div style={{ 
                      display: 'inline-block',
                      padding: '0.5rem 1rem', 
                      background: '#4caf50', 
                      color: 'white',
                      borderRadius: '4px',
                      fontSize: '0.9rem',
                      fontWeight: 'bold'
                    }}>
                      ✓ Human Reviewed
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </main>
  )
}


