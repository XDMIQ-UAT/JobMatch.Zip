'use client';

import React, { useState, useEffect } from 'react';

interface HeaderProps {
  anonymousId?: string;
  showVRBadge?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ 
  anonymousId,
  showVRBadge = true
}) => {
  const [isVR, setIsVR] = useState(false);

  useEffect(() => {
    setIsVR(/Quest/i.test(navigator.userAgent));
  }, []);

  return (
    <header className="container mx-auto px-8 py-8">
      {/* VR Indicator */}
      {showVRBadge && isVR && (
        <div className="fixed top-4 right-4 bg-purple-600 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-lg z-50">
          🥽 Quest 3 Optimized
        </div>
      )}

      <div className="flex items-center justify-between">
        <a href="/" className="text-3xl font-bold text-gray-800 hover:text-blue-600 transition">
          jobmatch
        </a>
        
        <nav className="flex items-center gap-6">
          {anonymousId && (
            <div className="text-xl text-gray-500">
              Session: {anonymousId.slice(0, 8)}...
            </div>
          )}
          <a href="/assess" className="text-xl font-semibold text-gray-700 hover:text-blue-600 transition">
            Assess
          </a>
          <a href="/matches" className="text-xl font-semibold text-gray-700 hover:text-blue-600 transition">
            Matches
          </a>
          <a href="/profile" className="text-xl font-semibold text-gray-700 hover:text-blue-600 transition">
            Profile
          </a>
        </nav>
      </div>
    </header>
  );
};
