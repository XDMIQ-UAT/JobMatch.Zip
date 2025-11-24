'use client';

/**
 * UAT Scenarios Listing
 * 
 * Browse and select available high-risk test scenarios
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Scenario {
  id: string;
  title: string;
  description: string;
  type: string;
  compensation_usd: number;
  pii_categories: string[];
  spots_available: number;
  created_at: string;
}

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScenarios();
  }, []);

  const fetchScenarios = async () => {
    try {
      const response = await fetch('/api/uat/scenarios');
      const data = await response.json();
      setScenarios(data.scenarios || []);
    } catch (error) {
      console.error('Failed to fetch scenarios:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      financial: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50',
      healthcare: 'bg-red-500/20 text-red-300 border-red-500/50',
      legal: 'bg-blue-500/20 text-blue-300 border-blue-500/50',
      pii_handling: 'bg-purple-500/20 text-purple-300 border-purple-500/50',
      identity: 'bg-green-500/20 text-green-300 border-green-500/50',
      biometric: 'bg-pink-500/20 text-pink-300 border-pink-500/50',
      payment_gateway: 'bg-orange-500/20 text-orange-300 border-orange-500/50',
    };
    return colors[type] || 'bg-gray-500/20 text-gray-300 border-gray-500/50';
  };

  const getCompensationTier = (amount: number) => {
    if (amount >= 150) return { tier: 'CRITICAL', color: 'text-red-400' };
    if (amount >= 75) return { tier: 'HIGH', color: 'text-orange-400' };
    if (amount >= 35) return { tier: 'MEDIUM', color: 'text-yellow-400' };
    return { tier: 'STANDARD', color: 'text-green-400' };
  };

  const filteredScenarios = scenarios.filter(s => 
    filter === 'all' || s.type === filter
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12">
      <div className="container mx-auto px-4">
        
        {/* Header */}
        <div className="mb-8">
          <Link 
            href="/uat"
            className="text-purple-300 hover:text-purple-200 mb-4 inline-block"
          >
            ← Back to Portal
          </Link>
          <h1 className="text-4xl font-bold text-white mb-4">
            Available Test Scenarios
          </h1>
          <p className="text-purple-200">
            Choose from approved high-risk UI tests. All scenarios reviewed by legal/medical experts.
          </p>
        </div>

        {/* Filters */}
        <div className="mb-8 flex flex-wrap gap-2">
          {['all', 'financial', 'healthcare', 'legal', 'pii_handling', 'identity', 'biometric', 'payment_gateway'].map(type => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === type
                  ? 'bg-purple-600 text-white'
                  : 'bg-white/10 text-purple-200 hover:bg-white/20'
              }`}
            >
              {type.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>

        {/* Statistics */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4">
            <div className="text-3xl font-bold text-white">{scenarios.length}</div>
            <div className="text-purple-200 text-sm">Total Scenarios</div>
          </div>
          <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4">
            <div className="text-3xl font-bold text-white">
              {scenarios.reduce((sum, s) => sum + s.spots_available, 0)}
            </div>
            <div className="text-purple-200 text-sm">Spots Available</div>
          </div>
          <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4">
            <div className="text-3xl font-bold text-white">
              ${scenarios.reduce((sum, s) => sum + s.compensation_usd, 0)}
            </div>
            <div className="text-purple-200 text-sm">Total Compensation</div>
          </div>
          <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4">
            <div className="text-3xl font-bold text-white">
              ${Math.round(scenarios.reduce((sum, s) => sum + s.compensation_usd, 0) / scenarios.length || 0)}
            </div>
            <div className="text-purple-200 text-sm">Avg per Test</div>
          </div>
        </div>

        {/* Scenarios Grid */}
        {loading ? (
          <div className="text-center text-white py-12">
            Loading scenarios...
          </div>
        ) : filteredScenarios.length === 0 ? (
          <div className="bg-white/10 backdrop-blur-lg rounded-lg p-8 text-center">
            <p className="text-purple-200">No scenarios available in this category.</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredScenarios.map(scenario => {
              const compTier = getCompensationTier(scenario.compensation_usd);
              
              return (
                <div 
                  key={scenario.id}
                  className="bg-white/10 backdrop-blur-lg rounded-lg p-6 hover:bg-white/15 transition"
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <span className={`inline-block px-2 py-1 rounded text-xs font-medium border ${getTypeColor(scenario.type)}`}>
                        {scenario.type.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${compTier.color}`}>
                        ${scenario.compensation_usd}
                      </div>
                      <div className="text-xs text-purple-300">{compTier.tier}</div>
                    </div>
                  </div>

                  {/* Title & Description */}
                  <h3 className="text-xl font-bold text-white mb-2">
                    {scenario.title}
                  </h3>
                  <p className="text-purple-200 text-sm mb-4 line-clamp-3">
                    {scenario.description}
                  </p>

                  {/* PII Categories */}
                  <div className="mb-4">
                    <div className="text-xs text-purple-300 mb-1">PII Exposure:</div>
                    <div className="flex flex-wrap gap-1">
                      {scenario.pii_categories.map(cat => (
                        <span 
                          key={cat}
                          className="px-2 py-1 bg-red-500/20 text-red-300 text-xs rounded"
                        >
                          {cat}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-white/10">
                    <div className="text-sm text-purple-300">
                      {scenario.spots_available > 0 ? (
                        <span className="text-green-400">
                          {scenario.spots_available} spot{scenario.spots_available !== 1 ? 's' : ''} left
                        </span>
                      ) : (
                        <span className="text-red-400">Full</span>
                      )}
                    </div>
                    
                    <Link
                      href={`/uat/test/${scenario.id}`}
                      className={`px-4 py-2 rounded-lg font-medium transition ${
                        scenario.spots_available > 0
                          ? 'bg-purple-600 hover:bg-purple-700 text-white'
                          : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                      }`}
                      onClick={(e) => scenario.spots_available === 0 && e.preventDefault()}
                    >
                      {scenario.spots_available > 0 ? 'Start Test' : 'Full'}
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
