'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { fetchUserIdentity } from '@/lib/apiCache'

export default function UniversalCanvasPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [tool, setTool] = useState<'pen' | 'eraser' | 'text' | 'shape'>('pen')
  const [color, setColor] = useState('#000000')
  const [lineWidth, setLineWidth] = useState(2)
  const [isLowBandwidth, setIsLowBandwidth] = useState(false)
  const [isOffline, setIsOffline] = useState(false)
  const [saved, setSaved] = useState(false)
  const [mounted, setMounted] = useState(false)
  const animationFrameRef = useRef<number | null>(null)
  const lastDrawTimeRef = useRef<number>(0)
  interface CanvasDocument {
    id: string
    title: string
    data: string
    createdAt: number
    updatedAt: number
  }

  const [currentCanvasId, setCurrentCanvasId] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('currentCanvasId') || 'default'
    }
    return 'default'
  })
  const [canvases, setCanvases] = useState<CanvasDocument[]>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('canvas_documents')
      if (saved) {
        try {
          const parsed = JSON.parse(saved)
          if (Array.isArray(parsed) && parsed.length > 0) {
            return parsed
          }
        } catch {
          // Invalid JSON, will initialize below
        }
      }
      // Migrate old single canvas if it exists
      const oldData = localStorage.getItem('canvas_data')
      if (oldData) {
        const defaultCanvas: CanvasDocument = {
          id: 'default',
          title: localStorage.getItem('canvasTitle') || 'Universal Canvas',
          data: oldData,
          createdAt: Date.now(),
          updatedAt: Date.now()
        }
        return [defaultCanvas]
      }
    }
    return []
  })
  const [canvasTitle, setCanvasTitle] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('canvas_documents')
      if (saved) {
        try {
          const parsed = JSON.parse(saved)
          if (Array.isArray(parsed) && parsed.length > 0) {
            const currentId = localStorage.getItem('currentCanvasId') || 'default'
            const current = parsed.find((c: CanvasDocument) => c.id === currentId)
            if (current) return current.title
          }
        } catch {
          // Fall through
        }
      }
      return localStorage.getItem('canvasTitle') || 'Universal Canvas'
    }
    return 'Universal Canvas'
  })
  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const [showCanvasList, setShowCanvasList] = useState(false)
  const titleInputRef = useRef<HTMLInputElement>(null)
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null)
  const [userIdentity, setUserIdentity] = useState<{
    anonymousId: string | null
    provider: string | null
    providerDisplayName: string | null
  }>(() => {
    if (typeof window !== 'undefined') {
      const stored = sessionStorage.getItem('user_identity')
      if (stored) {
        try {
          return JSON.parse(stored)
        } catch {
          // Invalid JSON, will fetch fresh
        }
      }
    }
    return { anonymousId: null, provider: null, providerDisplayName: null }
  })

  useEffect(() => {
    setMounted(true)
    
    // Check connection speed
    if ('connection' in navigator) {
      const connection = (navigator as any).connection
      if (connection) {
        const effectiveType = connection.effectiveType
        setIsLowBandwidth(effectiveType === '2g' || effectiveType === 'slow-2g')
      }
    }

    // Check offline status
    setIsOffline(!navigator.onLine)
    window.addEventListener('online', () => setIsOffline(false))
    window.addEventListener('offline', () => setIsOffline(true))

    // Load canvas from localStorage
    // Use setTimeout to ensure state is initialized
    const loadTimer = setTimeout(() => {
      loadCanvas()
    }, 100)

    // Load user identity info using cached utility
    const loadUserIdentity = async () => {
      try {
        const anonymousId = localStorage.getItem('anonymous_id') || sessionStorage.getItem('anonymous_id')
        if (anonymousId) {
          const data = await fetchUserIdentity(anonymousId)
          if (data) {
            const identity = {
              anonymousId: data.anonymous_id,
              provider: data.provider || null,
              providerDisplayName: data.provider_display_name || null
            }
            setUserIdentity(identity)
          }
        }
      } catch (error) {
        console.error('Failed to load user identity:', error)
        // Silently fail - identity display is optional
      }
    }
    
    loadUserIdentity()

    // Auto-save before page unload
    const handleBeforeUnload = () => {
      autoSaveCanvas()
    }
    window.addEventListener('beforeunload', handleBeforeUnload)

    // Periodic auto-save every 60 seconds as backup (reduced frequency)
    const periodicSave = setInterval(() => {
      autoSaveCanvas()
    }, 60000)

    return () => {
      clearTimeout(loadTimer)
      window.removeEventListener('online', () => setIsOffline(false))
      window.removeEventListener('offline', () => setIsOffline(false))
      window.removeEventListener('beforeunload', handleBeforeUnload)
      clearInterval(periodicSave)
      // Save on unmount
      autoSaveCanvas()
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }
    }
  }, []) // Only run once on mount

  useEffect(() => {
    if (isEditingTitle && titleInputRef.current) {
      const timer = setTimeout(() => {
        if (titleInputRef.current) {
          titleInputRef.current.focus()
        }
      }, 10)
      return () => clearTimeout(timer)
    }
    return
  }, [isEditingTitle])

  const saveCanvasesToStorage = (updatedCanvases: CanvasDocument[]) => {
    localStorage.setItem('canvas_documents', JSON.stringify(updatedCanvases))
    setCanvases(updatedCanvases)
  }

  const getCurrentCanvas = (): CanvasDocument | undefined => {
    return canvases.find(c => c.id === currentCanvasId)
  }

  const autoSaveCanvas = useCallback(() => {
    try {
      const canvas = canvasRef.current
      if (!canvas) return

      const dataURL = canvas.toDataURL('image/png', 0.8)
      const current = canvases.find(c => c.id === currentCanvasId)
      const now = Date.now()
      
      if (current) {
        // Update existing canvas
        const updated = canvases.map(c => 
          c.id === currentCanvasId 
            ? { ...c, data: dataURL, updatedAt: now }
            : c
        )
        saveCanvasesToStorage(updated)
      } else {
        // Create new canvas document
        const newCanvas: CanvasDocument = {
          id: currentCanvasId,
          title: canvasTitle,
          data: dataURL,
          createdAt: now,
          updatedAt: now
        }
        saveCanvasesToStorage([...canvases, newCanvas])
      }
      // Silent save - don't show "Saved" notification for auto-saves
    } catch (error) {
      console.error('Failed to auto-save canvas:', error)
    }
  }, [canvases, currentCanvasId, canvasTitle])

  const createNewCanvas = () => {
    const newId = `canvas_${Date.now()}`
    const newCanvas: CanvasDocument = {
      id: newId,
      title: 'Universal Canvas',
      data: '',
      createdAt: Date.now(),
      updatedAt: Date.now()
    }
    const updated = [...canvases, newCanvas]
    saveCanvasesToStorage(updated)
    setCurrentCanvasId(newId)
    localStorage.setItem('currentCanvasId', newId)
    setCanvasTitle('Universal Canvas')
    
    // Clear the canvas
    const canvas = canvasRef.current
    if (canvas) {
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
      }
    }
    setShowCanvasList(false)
  }

  const switchCanvas = (canvasId: string) => {
    // Save current canvas before switching
    autoSaveCanvas()
    
    const targetCanvas = canvases.find(c => c.id === canvasId)
    if (targetCanvas) {
      setCurrentCanvasId(canvasId)
      localStorage.setItem('currentCanvasId', canvasId)
      setCanvasTitle(targetCanvas.title)
      loadCanvasById(canvasId)
    }
    setShowCanvasList(false)
  }

  const deleteCanvas = (canvasId: string) => {
    if (!confirm('Are you sure you want to delete this canvas? This cannot be undone.')) {
      return
    }
    
    const updated = canvases.filter(c => c.id !== canvasId)
    saveCanvasesToStorage(updated)
    
    if (canvasId === currentCanvasId) {
      // If deleting current canvas, switch to first available or create new
      if (updated.length > 0) {
        switchCanvas(updated[0].id)
      } else {
        createNewCanvas()
      }
    }
  }

  const resetTitle = () => {
    setCanvasTitle('Universal Canvas')
    const current = getCurrentCanvas()
    if (current) {
      const updated = canvases.map(c =>
        c.id === currentCanvasId
          ? { ...c, title: 'Universal Canvas' }
          : c
      )
      saveCanvasesToStorage(updated)
    }
    if (typeof window !== 'undefined') {
      localStorage.setItem('canvasTitle', 'Universal Canvas')
    }
  }

  const loadCanvasById = (canvasId: string) => {
    try {
      const canvas = canvasRef.current
      if (!canvas) return

      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const targetCanvas = canvases.find(c => c.id === canvasId)
      if (targetCanvas && targetCanvas.data) {
        const img = new Image()
        img.onload = () => {
          ctx.clearRect(0, 0, canvas.width, canvas.height)
          ctx.drawImage(img, 0, 0)
        }
        img.src = targetCanvas.data
      } else {
        // Clear canvas if no data
        ctx.clearRect(0, 0, canvas.width, canvas.height)
      }
    } catch (error) {
      console.error('Failed to load canvas:', error)
    }
  }

  const loadCanvas = async () => {
    // Get current canvases from state
    let currentCanvases = canvases
    
    // Initialize with default canvas if none exist
    if (currentCanvases.length === 0) {
      const oldData = localStorage.getItem('canvas_data')
      const oldTitle = localStorage.getItem('canvasTitle') || 'Universal Canvas'
      const defaultCanvas: CanvasDocument = {
        id: 'default',
        title: oldTitle,
        data: oldData || '',
        createdAt: Date.now(),
        updatedAt: Date.now()
      }
      currentCanvases = [defaultCanvas]
      saveCanvasesToStorage(currentCanvases)
      const id = 'default'
      setCurrentCanvasId(id)
      localStorage.setItem('currentCanvasId', id)
      setCanvasTitle(oldTitle)
      // Load the old data if it exists
      if (oldData) {
        setTimeout(() => loadCanvasById(id), 50)
      }
    } else {
      const id = currentCanvasId
      loadCanvasById(id)
      // Update title from current canvas
      const current = currentCanvases.find(c => c.id === id)
      if (current) {
        setCanvasTitle(current.title)
      }
    }
  }

  const saveCanvas = async () => {
    try {
      const canvas = canvasRef.current
      if (!canvas) return

      const dataURL = canvas.toDataURL('image/png', 0.8)
      
      // Save to IndexedDB (offline)
      localStorage.setItem('canvas_data', dataURL)

      // Try to sync to server (if online)
      if (!isOffline) {
        try {
          await fetch('/api/canvas/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ canvas_data: dataURL })
          })
          setSaved(true)
          setTimeout(() => setSaved(false), 2000)
        } catch (error) {
          console.error('Failed to sync:', error)
          // Still saved locally
        }
      } else {
        setSaved(true)
        setTimeout(() => setSaved(false), 2000)
      }
    } catch (error) {
      console.error('Failed to save canvas:', error)
    }
  }

  const clearCanvas = () => {
    if (!confirm('Are you sure you want to clear the canvas? This cannot be undone.')) {
      return
    }
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Clear saved data for current canvas
    const current = getCurrentCanvas()
    if (current) {
      const updated = canvases.map(c =>
        c.id === currentCanvasId
          ? { ...c, data: '', updatedAt: Date.now() }
          : c
      )
      saveCanvasesToStorage(updated)
    }
  }

  const startDrawing = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDrawing(true)
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    ctx.beginPath()
    ctx.moveTo(x, y)
  }, [])

  const draw = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return
    
    // Throttle drawing using requestAnimationFrame
    if (animationFrameRef.current) {
      return // Skip if frame already scheduled
    }
    
    animationFrameRef.current = requestAnimationFrame(() => {
      const canvas = canvasRef.current
      if (!canvas) {
        animationFrameRef.current = null
        return
      }
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        animationFrameRef.current = null
        return
      }

      const rect = canvas.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top

      ctx.lineTo(x, y)
      ctx.strokeStyle = tool === 'eraser' ? '#ffffff' : color
      ctx.lineWidth = tool === 'eraser' ? lineWidth * 2 : lineWidth
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.stroke()
      
      animationFrameRef.current = null
    })
  }, [isDrawing, tool, color, lineWidth])

  const stopDrawing = useCallback(() => {
    setIsDrawing(false)
    
    // Cancel any pending animation frames
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }
    
    // Auto-save after finishing a stroke (debounced)
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current)
    }
    autoSaveTimerRef.current = setTimeout(() => {
      autoSaveCanvas()
    }, 2000) // Save 2s after stopping drawing (reduced frequency)
  }, [autoSaveCanvas])

  const exportCanvas = () => {
    const canvas = canvasRef.current
    if (!canvas) return
    const dataURL = canvas.toDataURL('image/png')
    const link = document.createElement('a')
    link.download = 'canvas.png'
    link.href = dataURL
    link.click()
  }

  return (
    <main style={{ 
      padding: '1rem', 
      maxWidth: '100%', 
      margin: '0 auto',
      minHeight: '100vh',
      background: '#f5f5f5'
    }}>
      {/* Status Bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0.5rem',
        background: '#fff',
        borderBottom: '1px solid #ddd',
        marginBottom: '1rem',
        flexWrap: 'wrap'
      }}>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap', flex: 1 }}>
          {/* User Identity Display */}
          {userIdentity.anonymousId && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.25rem 0.75rem',
              background: '#e3f2fd',
              borderRadius: '4px',
              fontSize: '0.875rem',
              color: '#1976d2',
              marginRight: 'auto'
            }}>
              <span style={{ fontWeight: '600' }}>You:</span>
              {userIdentity.providerDisplayName && (
                <span style={{ 
                  padding: '0.125rem 0.5rem',
                  background: '#fff',
                  borderRadius: '3px',
                  fontSize: '0.75rem',
                  fontWeight: '500'
                }}>
                  {userIdentity.providerDisplayName}
                </span>
              )}
              <span style={{ 
                fontFamily: 'monospace',
                fontSize: '0.75rem',
                opacity: 0.8
              }}>
                {userIdentity.anonymousId.slice(0, 8)}...
              </span>
            </div>
          )}
          {isEditingTitle ? (
            <input
              ref={titleInputRef}
              type="text"
              defaultValue={canvasTitle}
              onBlur={(e) => {
                const newValue = e.currentTarget.value.trim() || 'Universal Canvas'
                setCanvasTitle(newValue)
                
                // Update canvas document title
                const current = getCurrentCanvas()
                if (current) {
                  const updated = canvases.map(c =>
                    c.id === currentCanvasId
                      ? { ...c, title: newValue }
                      : c
                  )
                  saveCanvasesToStorage(updated)
                }
                
                if (typeof window !== 'undefined') {
                  localStorage.setItem('canvasTitle', newValue)
                }
                setIsEditingTitle(false)
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  e.currentTarget.blur()
                } else if (e.key === 'Escape') {
                  e.preventDefault()
                  setIsEditingTitle(false)
                  e.currentTarget.blur()
                }
              }}
              autoFocus
              style={{
                fontSize: '1.2rem',
                fontWeight: '600',
                margin: 0,
                padding: '0.25rem 0.5rem',
                border: '2px solid #2196f3',
                borderRadius: '4px',
                outline: 'none',
                backgroundColor: '#fff',
                minWidth: '150px',
                maxWidth: '300px',
                cursor: 'text'
              }}
            />
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h1
                onClick={() => setIsEditingTitle(true)}
                style={{
                  margin: 0,
                  fontSize: '1.2rem',
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
                {canvasTitle}
              </h1>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  resetTitle()
                }}
                title="Reset title to default"
                style={{
                  padding: '0.25rem 0.5rem',
                  background: '#ff9800',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '0.75rem',
                  lineHeight: '1'
                }}
              >
                Reset Title
              </button>
            </div>
          )}
          {isOffline && (
            <span style={{ 
              padding: '0.25rem 0.5rem', 
              background: '#ff9800', 
              color: 'white', 
              borderRadius: '4px',
              fontSize: '0.8rem'
            }}>
              Offline Mode
            </span>
          )}
          {isLowBandwidth && (
            <span style={{ 
              padding: '0.25rem 0.5rem', 
              background: '#2196f3', 
              color: 'white', 
              borderRadius: '4px',
              fontSize: '0.8rem'
            }}>
              Low Bandwidth Mode
            </span>
          )}
          {saved && (
            <span style={{ 
              padding: '0.25rem 0.5rem', 
              background: '#4caf50', 
              color: 'white', 
              borderRadius: '4px',
              fontSize: '0.8rem'
            }}>
              Saved
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => setShowCanvasList(!showCanvasList)}
            style={{
              padding: '0.5rem 1rem',
              background: '#9c27b0',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            {showCanvasList ? 'Hide' : 'Canvases'} ({mounted ? canvases.length : 0})
          </button>
          <button
            onClick={createNewCanvas}
            style={{
              padding: '0.5rem 1rem',
              background: '#ff9800',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            New Canvas
          </button>
          <button
            onClick={saveCanvas}
            style={{
              padding: '0.5rem 1rem',
              background: '#4caf50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            Save
          </button>
          <button
            onClick={clearCanvas}
            style={{
              padding: '0.5rem 1rem',
              background: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            Clear
          </button>
          <button
            onClick={exportCanvas}
            style={{
              padding: '0.5rem 1rem',
              background: '#2196f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            Export
          </button>
        </div>
      </div>

      {/* Canvas List */}
      {showCanvasList && (
        <div style={{
          marginBottom: '1rem',
          padding: '1rem',
          background: '#fff',
          border: '1px solid #ddd',
          borderRadius: '4px',
          maxHeight: '300px',
          overflowY: 'auto'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h3 style={{ margin: 0, fontSize: '1rem' }}>Your Canvases</h3>
            <button
              onClick={createNewCanvas}
              style={{
                padding: '0.25rem 0.75rem',
                background: '#4caf50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              + New
            </button>
          </div>
          {canvases.length === 0 ? (
            <p style={{ color: '#666', fontSize: '0.9rem' }}>No canvases yet. Create one to get started!</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {canvases.map((canvas) => (
                <div
                  key={canvas.id}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '0.5rem',
                    background: canvas.id === currentCanvasId ? '#e3f2fd' : '#f5f5f5',
                    border: canvas.id === currentCanvasId ? '2px solid #2196f3' : '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                  onClick={() => switchCanvas(canvas.id)}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: canvas.id === currentCanvasId ? '600' : '400' }}>
                      {canvas.title}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#666' }}>
                      {new Date(canvas.updatedAt).toLocaleString()}
                    </div>
                  </div>
                  {canvas.id === currentCanvasId && (
                    <span style={{ fontSize: '0.75rem', color: '#2196f3', marginRight: '0.5rem' }}>
                      Current
                    </span>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteCanvas(canvas.id)
                    }}
                    style={{
                      padding: '0.25rem 0.5rem',
                      background: '#f44336',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.75rem'
                    }}
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Toolbar */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        padding: '0.5rem',
        background: '#fff',
        borderBottom: '1px solid #ddd',
        marginBottom: '1rem',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button
            onClick={() => setTool('pen')}
            style={{
              padding: '0.5rem',
              background: tool === 'pen' ? '#2196f3' : '#e0e0e0',
              color: tool === 'pen' ? 'white' : 'black',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Pen
          </button>
          <button
            onClick={() => setTool('eraser')}
            style={{
              padding: '0.5rem',
              background: tool === 'eraser' ? '#2196f3' : '#e0e0e0',
              color: tool === 'eraser' ? 'white' : 'black',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Eraser
          </button>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <label style={{ fontSize: '0.9rem' }}>Color:</label>
          <input
            type="color"
            value={color}
            onChange={(e) => setColor(e.target.value)}
            style={{ width: '40px', height: '30px', border: '1px solid #ddd', cursor: 'pointer' }}
          />
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <label style={{ fontSize: '0.9rem' }}>Size:</label>
          <input
            type="range"
            min="1"
            max="20"
            value={lineWidth}
            onChange={(e) => setLineWidth(parseInt(e.target.value))}
            style={{ width: '100px' }}
          />
          <span style={{ fontSize: '0.9rem' }}>{lineWidth}px</span>
        </div>
      </div>

      {/* Canvas */}
      <div style={{
        background: '#fff',
        border: '1px solid #ddd',
        borderRadius: '4px',
        padding: '1rem',
        display: 'flex',
        justifyContent: 'center',
        overflow: 'auto'
      }}>
        <canvas
          ref={canvasRef}
          width={800}
          height={600}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          style={{
            border: '1px solid #ccc',
            cursor: 'crosshair',
            maxWidth: '100%',
            height: 'auto'
          }}
        />
      </div>

      {/* Info */}
      <div style={{
        marginTop: '1rem',
        padding: '1rem',
        background: '#fff',
        borderRadius: '4px',
        fontSize: '0.9rem',
        color: '#666'
      }}>
        <p><strong>Universal Canvas</strong> - Works anywhere with basic internet</p>
        <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
          <li>Works offline - saves locally</li>
          <li>Low bandwidth optimized</li>
          <li>Export your work</li>
          <li>Use for portfolios, planning, collaboration</li>
        </ul>
      </div>
    </main>
  )
}

