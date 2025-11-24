'use client'

import { useState } from 'react'

interface UATTest {
  id: string
  name: string
  description: string
  testUrl: string
  productionUrl: string
  status: 'pending' | 'passed' | 'failed' | 'verified'
  notes: string
  screenshots: string[]
}

const UAT_TESTS: UATTest[] = [
  {
    id: 'version-display',
    name: 'Version Display (REV001)',
    description: 'Verify REV001 version badge appears on homepage',
    testUrl: '/',
    productionUrl: 'https://jobmatch.zip',
    status: 'pending',
    notes: '',
    screenshots: []
  },
  {
    id: 'universal-canvas',
    name: 'Universal Canvas',
    description: 'Test Universal Canvas loads and is interactive',
    testUrl: '/canvas',
    productionUrl: 'https://jobmatch.zip/canvas',
    status: 'pending',
    notes: '',
    screenshots: []
  },
  {
    id: 'assessment-canvas-field',
    name: 'Assessment Form with Canvas Field',
    description: 'Verify Universal Canvas form field appears and works in assessment',
    testUrl: '/assessment',
    productionUrl: 'https://jobmatch.zip/assessment',
    status: 'pending',
    notes: '',
    screenshots: []
  },
  {
    id: 'assessment-other-option',
    name: 'Assessment "Other" Option',
    description: 'Verify "Other (specify)" option with freetext works',
    testUrl: '/assessment',
    productionUrl: 'https://jobmatch.zip/assessment',
    status: 'pending',
    notes: '',
    screenshots: []
  },
  {
    id: 'xdmiq-canvas-field',
    name: 'XDMIQ Canvas Field',
    description: 'Verify Canvas form field for reasoning works',
    testUrl: '/xdmiq',
    productionUrl: 'https://jobmatch.zip/xdmiq',
    status: 'pending',
    notes: '',
    screenshots: []
  },
  {
    id: 'xdmiq-other-option',
    name: 'XDMIQ "Other" Option',
    description: 'Verify "Other (specify your own)" radio option works',
    testUrl: '/xdmiq',
    productionUrl: 'https://jobmatch.zip/xdmiq',
    status: 'pending',
    notes: '',
    screenshots: []
  },
  {
    id: 'marketplace-canvas-field',
    name: 'Marketplace Canvas Field',
    description: 'Verify Canvas form field for description works',
    testUrl: '/marketplace',
    productionUrl: 'https://jobmatch.zip/marketplace',
    status: 'pending',
    notes: '',
    screenshots: []
  },
  {
    id: 'marketplace-other-option',
    name: 'Marketplace "Other" Option',
    description: 'Verify "Other (specify your own)" option in listing type works',
    testUrl: '/marketplace',
    productionUrl: 'https://jobmatch.zip/marketplace',
    status: 'pending',
    notes: '',
    screenshots: []
  }
]

export default function UATPage() {
  const [tests, setTests] = useState<UATTest[]>(UAT_TESTS)
  const [currentTest, setCurrentTest] = useState<UATTest | null>(null)
  const [reportData, setReportData] = useState({
    testerName: '',
    testEnvironment: 'localhost',
    overallStatus: 'in-progress',
    summary: ''
  })

  const updateTestStatus = (testId: string, status: UATTest['status'], notes: string = '') => {
    setTests(prev => prev.map(test => 
      test.id === testId ? { ...test, status, notes } : test
    ))
  }

  const generateReport = () => {
    const passed = tests.filter(t => t.status === 'passed' || t.status === 'verified').length
    const failed = tests.filter(t => t.status === 'failed').length
    const pending = tests.filter(t => t.status === 'pending').length

    const report = `
# UAT Test Report

**Tester:** ${reportData.testerName || 'Anonymous'}
**Environment:** ${reportData.testEnvironment}
**Date:** ${new Date().toLocaleString()}

## Test Results Summary
- ✅ Passed: ${passed}/${tests.length}
- ❌ Failed: ${failed}/${tests.length}
- ⏳ Pending: ${pending}/${tests.length}

## Detailed Results

${tests.map(test => `
### ${test.name}
- **Status:** ${test.status === 'passed' ? '✅ PASSED' : test.status === 'failed' ? '❌ FAILED' : test.status === 'verified' ? '✅ VERIFIED' : '⏳ PENDING'}
- **Description:** ${test.description}
- **Localhost URL:** http://localhost:3000${test.testUrl}
- **Production URL:** ${test.productionUrl}
- **Notes:** ${test.notes || 'None'}
`).join('\n')}

## Overall Summary
${reportData.summary || 'No summary provided'}
    `.trim()

    return report
  }

  const copyReport = () => {
    const report = generateReport()
    navigator.clipboard.writeText(report)
    alert('Report copied to clipboard! Paste it in the chat.')
  }

  return (
    <main style={{ 
      padding: '2rem', 
      maxWidth: '1200px', 
      margin: '0 auto',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '2rem',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '2rem' }}>UAT Testing Portal</h1>
          <p style={{ margin: '0.5rem 0 0 0', color: '#666' }}>
            Test changes locally, then verify on production
          </p>
        </div>
        <div style={{
          padding: '0.5rem 1rem',
          backgroundColor: '#2196f3',
          color: 'white',
          borderRadius: '8px',
          fontSize: '0.875rem',
          fontWeight: '600'
        }}>
          REV001
        </div>
      </div>

      {/* Tester Info */}
      <div style={{
        padding: '1.5rem',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
        marginBottom: '2rem'
      }}>
        <h2 style={{ marginTop: 0, fontSize: '1.25rem' }}>Tester Information</h2>
        <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Your Name:
            </label>
            <input
              type="text"
              value={reportData.testerName}
              onChange={(e) => setReportData({ ...reportData, testerName: e.target.value })}
              placeholder="Enter your name"
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '1rem'
              }}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Test Environment:
            </label>
            <select
              value={reportData.testEnvironment}
              onChange={(e) => setReportData({ ...reportData, testEnvironment: e.target.value })}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '1rem'
              }}
            >
              <option value="localhost">Localhost (Testing)</option>
              <option value="production">Production (Verification)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Test List */}
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Test Cases</h2>
        <div style={{ display: 'grid', gap: '1rem' }}>
          {tests.map((test) => (
            <div
              key={test.id}
              style={{
                padding: '1.5rem',
                border: '2px solid',
                borderColor: test.status === 'passed' || test.status === 'verified' ? '#4caf50' : 
                            test.status === 'failed' ? '#f44336' : '#e0e0e0',
                borderRadius: '8px',
                backgroundColor: '#fff'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: '600' }}>
                    {test.name}
                  </h3>
                  <p style={{ margin: '0.5rem 0', color: '#666' }}>
                    {test.description}
                  </p>
                </div>
                <div style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: test.status === 'passed' || test.status === 'verified' ? '#4caf50' : 
                                 test.status === 'failed' ? '#f44336' : '#ff9800',
                  color: 'white',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                  fontWeight: '600'
                }}>
                  {test.status === 'passed' ? '✅ PASSED' : 
                   test.status === 'failed' ? '❌ FAILED' : 
                   test.status === 'verified' ? '✅ VERIFIED' : '⏳ PENDING'}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                <a
                  href={`http://localhost:3000${test.testUrl}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#2196f3',
                    color: 'white',
                    textDecoration: 'none',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                  }}
                >
                  🧪 Test Locally
                </a>
                <a
                  href={test.productionUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#4caf50',
                    color: 'white',
                    textDecoration: 'none',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                  }}
                >
                  ✅ Verify Production
                </a>
              </div>

              <div style={{ marginTop: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Test Notes:
                </label>
                <textarea
                  value={test.notes}
                  onChange={(e) => updateTestStatus(test.id, test.status, e.target.value)}
                  placeholder="Add notes about this test..."
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    minHeight: '80px',
                    fontFamily: 'inherit'
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', flexWrap: 'wrap' }}>
                <button
                  onClick={() => updateTestStatus(test.id, 'passed', test.notes)}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#4caf50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                  }}
                >
                  ✅ Mark Passed
                </button>
                <button
                  onClick={() => updateTestStatus(test.id, 'failed', test.notes)}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                  }}
                >
                  ❌ Mark Failed
                </button>
                {reportData.testEnvironment === 'production' && (
                  <button
                    onClick={() => updateTestStatus(test.id, 'verified', test.notes)}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: '#2196f3',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      fontWeight: '500'
                    }}
                  >
                    ✅ Verify Matches
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div style={{
        padding: '1.5rem',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
        marginBottom: '2rem'
      }}>
        <h2 style={{ marginTop: 0, fontSize: '1.25rem' }}>Overall Summary</h2>
        <textarea
          value={reportData.summary}
          onChange={(e) => setReportData({ ...reportData, summary: e.target.value })}
          placeholder="Add overall summary of testing results..."
          style={{
            width: '100%',
            padding: '0.75rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '0.875rem',
            minHeight: '120px',
            fontFamily: 'inherit'
          }}
        />
      </div>

      {/* Generate Report */}
      <div style={{
        padding: '1.5rem',
        backgroundColor: '#e3f2fd',
        borderRadius: '8px',
        border: '2px solid #2196f3'
      }}>
        <h2 style={{ marginTop: 0, fontSize: '1.25rem' }}>Generate Test Report</h2>
        <p style={{ marginBottom: '1rem', color: '#666' }}>
          Copy the report below and paste it in the chat to report your UAT results.
        </p>
        <div style={{
          padding: '1rem',
          backgroundColor: '#fff',
          border: '1px solid #ddd',
          borderRadius: '4px',
          marginBottom: '1rem',
          maxHeight: '300px',
          overflowY: 'auto',
          fontFamily: 'monospace',
          fontSize: '0.875rem',
          whiteSpace: 'pre-wrap'
        }}>
          {generateReport()}
        </div>
        <button
          onClick={copyReport}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#2196f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: '600'
          }}
        >
          📋 Copy Report to Clipboard
        </button>
        <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: '#666' }}>
          After copying, paste the report in the chat to submit your UAT results.
        </p>
      </div>

      {/* Quick Links */}
      <div style={{
        marginTop: '2rem',
        padding: '1.5rem',
        backgroundColor: '#fff',
        border: '1px solid #e0e0e0',
        borderRadius: '8px'
      }}>
        <h2 style={{ marginTop: 0, fontSize: '1.25rem' }}>Quick Links</h2>
        <div style={{ display: 'grid', gap: '0.5rem', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
          <a href="http://localhost:3000" target="_blank" style={{ color: '#2196f3', textDecoration: 'none' }}>
            🏠 Localhost Homepage
          </a>
          <a href="https://jobmatch.zip" target="_blank" style={{ color: '#2196f3', textDecoration: 'none' }}>
            🌐 Production Homepage
          </a>
          <a href="http://localhost:3000/canvas" target="_blank" style={{ color: '#2196f3', textDecoration: 'none' }}>
            🎨 Localhost Universal Canvas
          </a>
          <a href="https://jobmatch.zip/canvas" target="_blank" style={{ color: '#2196f3', textDecoration: 'none' }}>
            🎨 Production Universal Canvas
          </a>
        </div>
      </div>
    </main>
  )
}

