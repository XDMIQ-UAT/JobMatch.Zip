'use client'

import React from 'react'

interface BannerProps {
  anonymousId?: string | null
  showProfile?: boolean
}

export const Banner: React.FC<BannerProps> = ({ 
  anonymousId = null,
  showProfile = true 
}) => {
  // Dark mode CSS variables
  const darkModeStyles = `
    /* White/off-white background layer for dark mode - ensures text visibility */
    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #fafafa;
      z-index: -5000;
      pointer-events: none;
    }
    
    html {
      background-color: #fafafa;
    }
    
    @media (prefers-color-scheme: dark) {
      :root {
        --auth-bg: #fafafa;
        --auth-text: #1a1a1a;
        --auth-text-secondary: #4a4a4a;
        --auth-border: #e0e0e0;
      }
      
      body::before {
        background-color: #fafafa;
      }
      
      html {
        background-color: #fafafa;
      }
      
      body {
        background-color: #fafafa;
      }
    }
    
    @media (prefers-color-scheme: light) {
      :root {
        --auth-bg: #fff;
        --auth-text: #333;
        --auth-text-secondary: #666;
        --auth-border: #e0e0e0;
      }
      
      body::before {
        background-color: #fff;
      }
      
      html {
        background-color: #fff;
      }
      
      body {
        background-color: #fff;
      }
    }
  `

  return (
    <>
      <style suppressHydrationWarning>{darkModeStyles}</style>
      <header style={{
        padding: 'var(--spacing-md, 1rem) var(--spacing-lg, 1.5rem)',
        backgroundColor: 'var(--auth-bg, #fff)',
        color: 'var(--auth-text, #333)',
        borderBottom: '1px solid var(--auth-border, #e0e0e0)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 'var(--spacing-md, 1rem)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm, 0.5rem)' }}>
          <a href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <h1 style={{ margin: 0, fontSize: 'var(--font-2xl, 1.875rem)', fontWeight: '700', color: '#2196f3' }}>
              JobMatch.zip
            </h1>
          </a>
          <span style={{ 
            padding: '0.25rem 0.5rem',
            backgroundColor: '#2196f3',
            color: 'white',
            borderRadius: '4px',
            fontSize: 'var(--font-xs, 0.75rem)',
            fontWeight: '600'
          }}>
            REV001
          </span>
        </div>
        <nav style={{ display: 'flex', gap: 'var(--spacing-md, 1rem)', alignItems: 'center', flexWrap: 'wrap' }}>
          <a href="/" style={{ 
            color: 'var(--text-secondary, #666)', 
            textDecoration: 'none',
            fontSize: 'var(--font-base, 1rem)',
            transition: 'color 0.2s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#2196f3'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary, #666)'}
          >
            Home
          </a>
          {anonymousId && showProfile && (
            <a href={`/profile?id=${anonymousId}`} style={{ 
              color: 'var(--text-secondary, #666)', 
              textDecoration: 'none',
              fontSize: 'var(--font-base, 1rem)',
              transition: 'color 0.2s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.color = '#2196f3'}
            onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary, #666)'}
            >
              Profile
            </a>
          )}
        </nav>
      </header>
    </>
  )
}
