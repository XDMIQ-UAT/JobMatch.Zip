'use client'

import { useState } from 'react'

interface AnonymousIdDisplayProps {
  anonymousId: string
  showTips?: boolean
}

export default function AnonymousIdDisplay({ anonymousId, showTips = true }: AnonymousIdDisplayProps) {
  const [copied, setCopied] = useState(false)
  const [downloaded, setDownloaded] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(anonymousId)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
      // Fallback for older browsers
      const textArea = document.createElement('textarea')
      textArea.value = anonymousId
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      document.body.appendChild(textArea)
      textArea.select()
      try {
        document.execCommand('copy')
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Fallback copy failed:', err)
      }
      document.body.removeChild(textArea)
    }
  }

  const handleDownload = () => {
    const blob = new Blob([`Your Anonymous ID\n\n${anonymousId}\n\nSave this ID to access your account later. Without it, you'll need to set up again.\n\nGenerated: ${new Date().toLocaleString()}`], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `jobmatch-anonymous-id-${anonymousId.slice(0, 8)}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    setDownloaded(true)
    setTimeout(() => setDownloaded(false), 2000)
  }

  return (
    <div style={{
      padding: '1.5rem',
      backgroundColor: '#fff',
      border: '2px solid #2196f3',
      borderRadius: '12px',
      marginTop: '1rem',
      marginBottom: '1rem'
    }}>
      <div style={{ marginBottom: '1rem' }}>
        <label style={{
          display: 'block',
          fontSize: '0.875rem',
          fontWeight: '600',
          color: '#666',
          marginBottom: '0.5rem'
        }}>
          Your anonymous ID:
        </label>
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          alignItems: 'center',
          flexWrap: 'wrap'
        }}>
          <div style={{
            flex: 1,
            padding: '0.75rem',
            backgroundColor: '#f5f5f5',
            border: '1px solid #ddd',
            borderRadius: '8px',
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            wordBreak: 'break-all',
            userSelect: 'all',
            cursor: 'text'
          }}>
            {anonymousId}
          </div>
          <button
            onClick={handleCopy}
            style={{
              padding: '0.75rem 1rem',
              backgroundColor: copied ? '#4caf50' : '#2196f3',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '600',
              transition: 'background-color 0.2s',
              whiteSpace: 'nowrap'
            }}
            onMouseEnter={(e) => {
              if (!copied) {
                e.currentTarget.style.backgroundColor = '#1976d2'
              }
            }}
            onMouseLeave={(e) => {
              if (!copied) {
                e.currentTarget.style.backgroundColor = '#2196f3'
              }
            }}
          >
            {copied ? '✓ Copied!' : 'Copy'}
          </button>
          <button
            onClick={handleDownload}
            style={{
              padding: '0.75rem 1rem',
              backgroundColor: downloaded ? '#4caf50' : '#f5f5f5',
              color: downloaded ? '#fff' : '#333',
              border: '1px solid #ddd',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '600',
              transition: 'all 0.2s',
              whiteSpace: 'nowrap'
            }}
            onMouseEnter={(e) => {
              if (!downloaded) {
                e.currentTarget.style.backgroundColor = '#e0e0e0'
              }
            }}
            onMouseLeave={(e) => {
              if (!downloaded) {
                e.currentTarget.style.backgroundColor = '#f5f5f5'
              }
            }}
          >
            {downloaded ? '✓ Downloaded!' : 'Download'}
          </button>
        </div>
      </div>

      {showTips && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '8px',
          marginTop: '1rem'
        }}>
          <p style={{
            margin: 0,
            fontSize: '0.875rem',
            color: '#856404',
            fontWeight: '600',
            marginBottom: '0.5rem'
          }}>
            💡 Important: Save this ID!
          </p>
          <p style={{
            margin: 0,
            fontSize: '0.875rem',
            color: '#856404',
            lineHeight: '1.5'
          }}>
            Without your anonymous ID, we cannot recover your account due to our zero-knowledge architecture. 
            Save it in a password manager, notes app, or download it as a file. You'll need it to access your account later.
          </p>
          <div style={{
            marginTop: '0.75rem',
            fontSize: '0.8125rem',
            color: '#856404'
          }}>
            <strong>Suggested places to save:</strong>
            <ul style={{
              margin: '0.5rem 0 0 1.25rem',
              padding: 0,
              listStyleType: 'disc'
            }}>
              <li>Password manager (1Password, LastPass, Bitwarden)</li>
              <li>Notes app (Apple Notes, Google Keep, Notion)</li>
              <li>Secure file on your device</li>
              <li>Email it to yourself</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

