'use client';

import React, { useState, useEffect } from 'react';

export default function AuthPage() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [hideHeaderCard, setHideHeaderCard] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [message, setMessage] = useState<string>('');

  // Check initial authentication and preference status on load
  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async () => {
    try {
      const res = await fetch('/api/auth/session');
      const data = await res.json();
      if (data.authenticated) {
        setIsAuthenticated(true);
        setUsername(data.username);
        setHideHeaderCard(data.hideHeaderCard ?? false);
      }
    } catch (error) {
      console.error('Failed to retrieve session:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();

      if (res.ok) {
        setIsAuthenticated(true);
        setHideHeaderCard(data.hideHeaderCard ?? false);
        setMessage('Login successful!');
      } else {
        setMessage(data.error || 'Invalid credentials');
      }
    } catch (error) {
      setMessage('An error occurred during login.');
    }
  };

  const handleToggleHeaderCard = async () => {
    const newState = !hideHeaderCard;
    setHideHeaderCard(newState);

    try {
      await fetch('/api/auth/preference', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, hideHeaderCard: newState }),
      });
    } catch (error) {
      console.error('Failed to update preference in PostgreSQL:', error);
      // Revert state if update fails
      setHideHeaderCard(!newState);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950 text-white">
        <p>Loading authentication state...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col items-center justify-center p-6">
      {!isAuthenticated ? (
        <div className="w-full max-w-md bg-gray-900 border border-gray-800 rounded-xl p-8 shadow-2xl">
          <h1 className="text-2xl font-bold mb-6 text-center text-red-500">System Authentication</h1>
          {message && <p className="mb-4 text-sm text-center text-amber-400">{message}</p>}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs uppercase tracking-wider text-gray-400 mb-2">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full bg-gray-950 border border-gray-800 rounded px-3 py-2 text-white focus:outline-none focus:border-red-600"
              />
            </div>
            <div>
              <label className="block text-xs uppercase tracking-wider text-gray-400 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-gray-950 border border-gray-800 rounded px-3 py-2 text-white focus:outline-none focus:border-red-600"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-2 rounded transition-colors"
            >
              Authenticate
            </button>
          </form>
        </div>
      ) : (
        <div className="w-full max-w-2xl space-y-6">
          {/* Hideable Header Card */}
          {!hideHeaderCard && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl transition-all">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-semibold text-white">Dashboard Status Header</h2>
                  <p className="text-sm text-gray-400">Welcome back, {username}. PostgreSQL sync active.</p>
                </div>
                <button
                  onClick={handleToggleHeaderCard}
                  className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded border border-gray-700 transition-colors"
                >
                  Hide Header Card
                </button>
              </div>
            </div>
          )}

          {/* Main Content Card */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Main Application Panel</h3>
              {hideHeaderCard && (
                <button
                  onClick={handleToggleHeaderCard}
                  className="text-xs bg-red-600/20 hover:bg-red-600/30 text-red-400 px-3 py-1.5 rounded border border-red-900/50 transition-colors"
                >
                  Restore Header Card
                </button>
              )}
            </div>
            <p className="text-gray-400 text-sm">
              Your authentication session is active, and UI preferences are successfully persisted to your PostgreSQL database cluster (`MasterMP_Auto`).
            </p>
          </div>
        </div>
      )}
    </div>
  );
}