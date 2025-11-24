'use client';

/**
 * UAT Earnings Dashboard
 * 
 * Track compensation, payment history, and test completion status
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface EarningsData {
  total_earned_usd: number;
  pending_usd: number;
  tests_completed: number;
  tests_in_progress: number;
  tests_submitted: number;
  history: Array<{
    scenario_id: string;
    amount_usd: number;
    status: string;
    completed_at: string;
  }>;
}

export default function EarningsPage() {
  const [testerId, setTesterId] = useState('');
  const [earnings, setEarnings] = useState<EarningsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchEarnings = async () => {
    if (!testerId) {
      setError('Please enter your tester ID');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`/api/uat/earnings?tester_id=${testerId}`);
      const data = await response.json();
      
      if (response.ok) {
        setEarnings(data);
      } else {
        setError(data.error || 'Failed to fetch earnings');
      }
    } catch (err) {
      setError('Network error - please try again');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      completed: 'bg-green-500/20 text-green-300 border-green-500/50',
      escrow: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50',
      pending: 'bg-blue-500/20 text-blue-300 border-blue-500/50',
      failed: 'bg-red-500/20 text-red-300 border-red-500/50',
      refunded: 'bg-gray-500/20 text-gray-300 border-gray-500/50',
    };
    return colors[status] || 'bg-gray-500/20 text-gray-300 border-gray-500/50';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        
        {/* Header */}
        <div className="mb-8">
          <Link 
            href="/uat"
            className="text-purple-300 hover:text-purple-200 mb-4 inline-block"
          >
            ← Back to Portal
          </Link>
          <h1 className="text-4xl font-bold text-white mb-4">
            💰 Your Earnings
          </h1>
          <p className="text-purple-200">
            Track your compensation, payment history, and test completion status
          </p>
        </div>

        {/* Tester ID Input */}
        {!earnings && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-white mb-4">
              Enter Your Anonymous Tester ID
            </h2>
            
            <div className="flex gap-4">
              <input
                type="text"
                value={testerId}
                onChange={(e) => setTesterId(e.target.value)}
                placeholder="tester_ABC123..."
                className="flex-1 bg-white/5 border border-purple-500/30 rounded-lg px-4 py-3 text-white placeholder-purple-400"
              />
              <button
                onClick={fetchEarnings}
                disabled={loading}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white font-bold px-8 py-3 rounded-lg transition"
              >
                {loading ? 'Loading...' : 'View Earnings'}
              </button>
            </div>

            {error && (
              <div className="mt-4 bg-red-500/20 border border-red-500/50 rounded-lg p-4">
                <p className="text-red-200">{error}</p>
              </div>
            )}

            <div className="mt-6 bg-blue-500/20 border border-blue-500/50 rounded-lg p-4">
              <p className="text-blue-200 text-sm">
                <strong>Privacy Note:</strong> Your tester ID is never linked to your payment identity. 
                This dashboard shows only test completion status and compensation amounts.
              </p>
            </div>
          </div>
        )}

        {/* Earnings Dashboard */}
        {earnings && (
          <>
            {/* Statistics Cards */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-lg rounded-lg p-6 border border-green-500/30">
                <div className="text-sm text-green-300 mb-2">Total Earned</div>
                <div className="text-4xl font-bold text-white">
                  ${earnings.total_earned_usd.toFixed(2)}
                </div>
                <div className="text-xs text-green-200 mt-2">
                  {earnings.tests_completed} tests completed
                </div>
              </div>

              <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 backdrop-blur-lg rounded-lg p-6 border border-yellow-500/30">
                <div className="text-sm text-yellow-300 mb-2">Pending Payment</div>
                <div className="text-4xl font-bold text-white">
                  ${earnings.pending_usd.toFixed(2)}
                </div>
                <div className="text-xs text-yellow-200 mt-2">
                  In escrow
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 backdrop-blur-lg rounded-lg p-6 border border-blue-500/30">
                <div className="text-sm text-blue-300 mb-2">In Progress</div>
                <div className="text-4xl font-bold text-white">
                  {earnings.tests_in_progress}
                </div>
                <div className="text-xs text-blue-200 mt-2">
                  Active tests
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-lg rounded-lg p-6 border border-purple-500/30">
                <div className="text-sm text-purple-300 mb-2">Submitted</div>
                <div className="text-4xl font-bold text-white">
                  {earnings.tests_submitted}
                </div>
                <div className="text-xs text-purple-200 mt-2">
                  Under review
                </div>
              </div>
            </div>

            {/* Payment History */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">
                  Payment History
                </h2>
                <button
                  onClick={() => setEarnings(null)}
                  className="text-purple-300 hover:text-purple-200 text-sm"
                >
                  Switch Account
                </button>
              </div>

              {earnings.history.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-purple-200 mb-4">No payment history yet</p>
                  <Link
                    href="/uat/scenarios"
                    className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded-lg inline-block transition"
                  >
                    Browse Test Scenarios
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {earnings.history.map((item, index) => (
                    <div
                      key={index}
                      className="bg-white/5 rounded-lg p-4 flex items-center justify-between hover:bg-white/10 transition"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-mono text-sm text-purple-300">
                            {item.scenario_id}
                          </span>
                          <span className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(item.status)}`}>
                            {item.status.toUpperCase()}
                          </span>
                        </div>
                        <div className="text-xs text-purple-400">
                          {new Date(item.completed_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-white">
                          ${item.amount_usd.toFixed(2)}
                        </div>
                        <div className="text-xs text-purple-300">
                          {item.status === 'completed' ? 'Paid' : 
                           item.status === 'escrow' ? 'In Escrow' : 
                           'Processing'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Request Withdrawal */}
            {earnings.total_earned_usd > 0 && (
              <div className="mt-8 bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-2xl p-8 border border-purple-500/30">
                <h2 className="text-2xl font-bold text-white mb-4">
                  💳 Request Withdrawal
                </h2>
                <p className="text-purple-200 mb-6">
                  Ready to withdraw your earnings? You'll need to provide payment details 
                  in our secure identity vault (completely separate from test data).
                </p>
                <div className="flex gap-4">
                  <button className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg transition">
                    Withdraw via USD Transfer
                  </button>
                  <button className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-6 rounded-lg transition">
                    Withdraw via Bitcoin
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
