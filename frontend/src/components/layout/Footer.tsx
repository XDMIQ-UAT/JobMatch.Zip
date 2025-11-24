'use client'

import React from 'react'

export const Footer: React.FC = () => {
  return (
    <footer style={{ 
      marginTop: 'var(--spacing-xl, 3rem)', 
      paddingTop: 'var(--spacing-xl, 3rem)',
      borderTop: '1px solid var(--border-color, #e0e0e0)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      flexWrap: 'wrap',
      gap: 'var(--spacing-md, 1rem)'
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        <p className="text-sm" style={{ margin: 0, color: 'var(--text-secondary, #666)' }}>
          © 2025 jobmatch
        </p>
        <p className="text-sm" style={{ margin: 0, color: 'var(--text-secondary, #666)' }}>
          Built with ❤️ for capability-first matching
        </p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', alignItems: 'flex-end' }}>
        <a 
          href="/privacy" 
          className="text-sm hover-link"
          style={{ 
            color: 'var(--text-secondary, #666)',
            textDecoration: 'none',
            transition: 'color 0.2s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#2196f3'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary, #666)'}
        >
          Privacy
        </a>
        <a 
          href="/how-were-different" 
          className="text-sm hover-link"
          style={{ 
            color: 'var(--text-secondary, #666)',
            textDecoration: 'none',
            transition: 'color 0.2s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#2196f3'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary, #666)'}
        >
          How we&apos;re different
        </a>
        <a 
          href="/feedback" 
          className="text-sm hover-link"
          style={{ 
            color: 'var(--text-secondary, #666)',
            textDecoration: 'none',
            transition: 'color 0.2s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#2196f3'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary, #666)'}
        >
          Give feedback
        </a>
      </div>
    </footer>
  )
}
