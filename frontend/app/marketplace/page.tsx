'use client'

import { useState } from 'react'
import CanvasFormField from '@/components/CanvasFormField'

export default function MarketplacePage() {
  const [view, setView] = useState<'browse' | 'sell'>('browse')
  const [listings, setListings] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const [newListing, setNewListing] = useState({
    seller_id: '',
    listing_type: 'combined',
    custom_listing_type: '',
    title: '',
    description: '',
    asset_price: '',
    capability_rate: '',
    xdmiq_score: null as number | null
  })

  const loadListings = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/marketplace/listings')
      const data = await response.json()
      setListings(data)
    } catch (error) {
      console.error('Failed to load listings:', error)
    } finally {
      setLoading(false)
    }
  }

  const createListing = async () => {
    if (!newListing.seller_id || !newListing.title) {
      alert('Please fill in required fields')
      return
    }

    setLoading(true)
    try {
      const asset_details = newListing.asset_price ? {
        price: parseFloat(newListing.asset_price),
        condition: 'new',
        quantity: 1
      } : null

      const capability_details = newListing.capability_rate ? {
        hourly_rate: parseFloat(newListing.capability_rate),
        experience_years: 5,
        portfolio_quality: 'good'
      } : null

      const finalListingType = newListing.listing_type === 'other' 
        ? newListing.custom_listing_type.trim() 
        : newListing.listing_type

      const response = await fetch('http://localhost:8000/api/marketplace/listings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          seller_id: newListing.seller_id,
          listing_type: finalListingType,
          is_custom_type: newListing.listing_type === 'other',
          title: newListing.title,
          description: newListing.description,
          asset_details,
          capability_details,
          pricing: {
            asset_price: newListing.asset_price ? parseFloat(newListing.asset_price) : 0,
            capability_rate: newListing.capability_rate ? parseFloat(newListing.capability_rate) : 0
          }
        })
      })
      const data = await response.json()
      alert(`Listing created! Valuation: $${data.valuation?.total_value?.toFixed(2)}`)
      setView('browse')
      loadListings()
    } catch (error) {
      console.error('Failed to create listing:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateValuation = async () => {
    if (!newListing.seller_id) {
      alert('Please enter seller ID')
      return
    }

    setLoading(true)
    try {
      const asset_details = newListing.asset_price ? {
        price: parseFloat(newListing.asset_price),
        condition: 'new'
      } : null

      const capability_details = newListing.capability_rate ? {
        hourly_rate: parseFloat(newListing.capability_rate)
      } : null

      const response = await fetch(
        `http://localhost:8000/api/marketplace/valuation/calculate?` +
        `asset_details=${asset_details ? JSON.stringify(asset_details) : ''}&` +
        `capability_details=${capability_details ? JSON.stringify(capability_details) : ''}&` +
        `xdmiq_score=${newListing.xdmiq_score || ''}`
      )
      const data = await response.json()
      alert(`Estimated Value: $${data.total_value?.toFixed(2)}\n` +
            `Assets: $${data.asset_value?.toFixed(2)} (${data.value_breakdown?.assets_percentage?.toFixed(1)}%)\n` +
            `Capabilities: $${data.capability_value?.toFixed(2)} (${data.value_breakdown?.capabilities_percentage?.toFixed(1)}%)`)
    } catch (error) {
      console.error('Failed to calculate valuation:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Marketplace for LLCs & Solo Proprietors</h1>
      <p>Exchange goods and services - Value based on "what we have" and "what we can do"</p>

      <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
        <button
          onClick={() => setView('browse')}
          style={{
            padding: '0.75rem 1.5rem',
            background: view === 'browse' ? '#0066cc' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Browse Listings
        </button>
        <button
          onClick={() => setView('sell')}
          style={{
            padding: '0.75rem 1.5rem',
            background: view === 'sell' ? '#0066cc' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Sell Goods/Services
        </button>
      </div>

      {view === 'browse' && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Browse Marketplace</h2>
          <button onClick={loadListings} disabled={loading} style={{ marginTop: '1rem', padding: '0.75rem 1.5rem' }}>
            {loading ? 'Loading...' : 'Load Listings'}
          </button>
          {listings.length === 0 && !loading && (
            <p style={{ marginTop: '1rem' }}>No listings yet. Be the first to list!</p>
          )}
        </div>
      )}

      {view === 'sell' && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Create Listing</h2>
          <p>List what you have (assets) or what you can do (capabilities)</p>

          <div style={{ marginTop: '1rem' }}>
            <label>
              Seller ID (Anonymous):
              <input
                type="text"
                value={newListing.seller_id}
                onChange={(e) => setNewListing({...newListing, seller_id: e.target.value})}
                style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem' }}
              />
            </label>
          </div>

          <div style={{ marginTop: '1rem' }}>
            <label htmlFor="listing-type-select" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Listing Type:
            </label>
            <select
              id="listing-type-select"
              value={newListing.listing_type}
              onChange={(e) => {
                setNewListing({
                  ...newListing, 
                  listing_type: e.target.value,
                  custom_listing_type: e.target.value === 'other' ? newListing.custom_listing_type : ''
                })
              }}
              aria-label="Select listing type"
              style={{ width: '100%', padding: '0.75rem', marginTop: '0.5rem', fontSize: '1rem', border: '1px solid #ddd', borderRadius: '8px' }}
            >
              <option value="asset">Asset Only (What I Have)</option>
              <option value="capability">Capability Only (What I Can Do)</option>
              <option value="combined">Combined (Both)</option>
              <option value="other">Other (specify your own)</option>
            </select>
            {newListing.listing_type === 'other' && (
              <div style={{ marginTop: '0.75rem' }}>
                <label htmlFor="custom-listing-type" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Please specify your listing type:
                </label>
                <input
                  id="custom-listing-type"
                  type="text"
                  value={newListing.custom_listing_type}
                  onChange={(e) => setNewListing({...newListing, custom_listing_type: e.target.value})}
                  placeholder="Enter your own listing type..."
                  aria-label="Enter your own listing type"
                  style={{ 
                    width: '100%', 
                    padding: '0.75rem', 
                    fontSize: '1rem',
                    border: '1px solid #2196f3',
                    borderRadius: '8px',
                    outline: 'none'
                  }}
                  autoFocus
                />
              </div>
            )}
          </div>

          <div style={{ marginTop: '1rem' }}>
            <label>
              Title:
              <input
                type="text"
                value={newListing.title}
                onChange={(e) => setNewListing({...newListing, title: e.target.value})}
                placeholder="e.g., AI Development Services + Custom Tools"
                style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem' }}
              />
            </label>
          </div>

          {/* Canvas Form Field for Description */}
          <div style={{ marginTop: '1rem' }}>
            <CanvasFormField
              label="Description (use Universal Canvas to describe interactively):"
              value={newListing.description}
              onChange={(canvasValue) => {
                const descriptionText = canvasValue?.chatMessages?.[canvasValue.chatMessages.length - 1]?.content || 
                                       canvasValue?.lastInput || 
                                       canvasValue?.canvasData || 
                                       ''
                setNewListing({...newListing, description: descriptionText})
              }}
              placeholder="Draw, chat, or interact to describe your goods/services..."
              interactiveMode="hybrid"
              aiTrainingEnabled={true}
              onAITraining={(interaction) => {
                console.log('Marketplace AI Training interaction:', interaction)
              }}
              height={200}
              width={600}
            />
          </div>

          {/* Traditional Text Input for Description */}
          <div style={{ marginTop: '1rem' }}>
            <label>
              Or type description here:
              <textarea
                value={newListing.description}
                onChange={(e) => setNewListing({...newListing, description: e.target.value})}
                placeholder="Describe your goods/services..."
                style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem', minHeight: '100px' }}
              />
            </label>
          </div>

          {(newListing.listing_type === 'asset' || newListing.listing_type === 'combined') && (
            <div style={{ marginTop: '1rem' }}>
              <label>
                Asset Price ($):
                <input
                  type="number"
                  value={newListing.asset_price}
                  onChange={(e) => setNewListing({...newListing, asset_price: e.target.value})}
                  placeholder="Price for what you have"
                  style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem' }}
                />
              </label>
            </div>
          )}

          {(newListing.listing_type === 'capability' || newListing.listing_type === 'combined') && (
            <>
              <div style={{ marginTop: '1rem' }}>
                <label>
                  Capability Rate ($/hour):
                  <input
                    type="number"
                    value={newListing.capability_rate}
                    onChange={(e) => setNewListing({...newListing, capability_rate: e.target.value})}
                    placeholder="Rate for what you can do"
                    style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem' }}
                  />
                </label>
              </div>
              <div style={{ marginTop: '1rem' }}>
                <label>
                  XDMIQ Score (optional):
                  <input
                    type="number"
                    value={newListing.xdmiq_score || ''}
                    onChange={(e) => setNewListing({...newListing, xdmiq_score: e.target.value ? parseInt(e.target.value) : null})}
                    placeholder="Your XDMIQ score (0-100)"
                    style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem' }}
                  />
                </label>
              </div>
            </>
          )}

          <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
            <button
              onClick={calculateValuation}
              disabled={loading}
              style={{ padding: '0.75rem 1.5rem', background: '#666', color: 'white', border: 'none', borderRadius: '4px' }}
            >
              Calculate Valuation
            </button>
            <button
              onClick={createListing}
              disabled={loading}
              style={{ padding: '0.75rem 1.5rem', background: '#0066cc', color: 'white', border: 'none', borderRadius: '4px' }}
            >
              {loading ? 'Creating...' : 'Create Listing'}
            </button>
          </div>
        </div>
      )}
    </main>
  )
}

