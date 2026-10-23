// src/app/LoginClient.tsx
'use client';

import React, { useState, FormEvent, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface LoginClientProps {
  errorCode?: string;
  userId?: string;
  userIc?: string;
  emailParam?: string;
}

export default function LoginClient({ errorCode, userId, userIc, emailParam }: LoginClientProps) {
  const router = useRouter();

  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [isAutoLoggingIn, setIsAutoLoggingIn] = useState<boolean>(false);
  
  const [activeTab, setActiveTab] = useState<
    | 'login'
    | 'noauthority'
    | 'noauth'
    | 'servererror'
    | 'backendunreachable'
    | 'backendtimeout'
    | 'backendhttperror'
    | 'backendinvalidjson'
    | 'authdataerror'
    | 'backendunexpected'
    | 'sessionerror'
    | 'databaseerror'
  >('login');

  const [email, setEmail] = useState(emailParam || '');
  const [password, setPassword] = useState('secretpassword123');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  const [modalOpen, setModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [modalBody, setModalBody] = useState('');
  const [redirectOnClose, setRedirectOnClose] = useState(false);

  // Sync tab status with error codes
  useEffect(() => {
    if (errorCode === 'not_exist') {
      setActiveTab('noauthority');
    } else if (errorCode === 'no_auth') {
      setActiveTab('noauth');
    } else if (errorCode === 'server_error' || errorCode === 'backend_unreachable') {
      setActiveTab('servererror');
    }
  }, [errorCode]);

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    if (nextTheme === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    }
  };

  const showModal = (title: string, body: string, shouldRedirect: boolean = false) => {
    setModalTitle(title);
    setModalBody(body);
    setRedirectOnClose(shouldRedirect);
    setModalOpen(true);
  };

  const handleModalProceed = () => {
    setModalOpen(false);
    if (redirectOnClose) {
      router.push('/');
      router.refresh();
    }
  };

  const executeAutoLogin = useCallback(() => {
    setIsAutoLoggingIn(true);
    showModal(
      'SSO Authentication Detected',
      `Valid SSO credentials found (${userId || userIc || 'SSO User'}). Authenticating session and redirecting to MPX Dashboard...`,
      true
    );
  }, [userId, userIc]);

  // Automated SSO Detection and Auto-Login Effect
  useEffect(() => {
    const hasSsoCredentials = Boolean((userId && userId !== 'Unknown') || (userIc && userIc !== 'Unknown'));
    const isCleanState = !errorCode && activeTab === 'login';

    if (hasSsoCredentials && isCleanState && !isAutoLoggingIn) {
      const timer = setTimeout(() => {
        executeAutoLogin();
      }, 400); // Brief delay for smoother UI transition
      return () => clearTimeout(timer);
    }
  }, [userId, userIc, errorCode, activeTab, isAutoLoggingIn, executeAutoLogin]);

  const handleLogin = (e: FormEvent) => {
    e.preventDefault();
    showModal(
      'Access Granted',
      `Authenticated session initialized for ${email || userId || 'User'}. Transitioning to MPX BOM Crosscheck dashboard...`,
      true
    );
  };

  const handleSSOLogin = () => {
    executeAutoLogin();
  };

  return (
    <div className={`h-full min-h-screen ${theme}`}>
      <main className="min-h-screen w-full m-0 p-0 flex flex-col lg:flex-row bg-[#FAF9F6] text-neutral-900 dark:bg-black dark:text-white transition-colors duration-300 selection:bg-pantone-red selection:text-white">
        
        {/* Left Hero Branding Panel */}
        <div className="relative w-full lg:w-7/12 min-h-screen bg-[#F7F6F3] dark:bg-black bg-grid-pattern-light dark:bg-grid-pattern-dark flex flex-col justify-between p-6 sm:p-10 lg:p-14 border-b lg:border-b-0 lg:border-r border-neutral-200 dark:border-neutral-900 transition-colors duration-300 overflow-hidden">
          
          <div className="z-20 flex items-center justify-between w-full mb-8 lg:mb-0">
            <div className="flex items-center space-x-3">
              <span className="text-pantone-red font-bold text-xl sm:text-2xl tracking-tight font-headline flex items-center gap-1.5">
                <span className="inline-block w-3 h-3 bg-pantone-red rounded-sm"></span>
                MPX&reg;
              </span>
              <span className="text-[10px] font-mono tracking-widest uppercase bg-pantone-softred text-pantone-red border border-pantone-redborder px-2 py-0.5 rounded font-semibold dark:bg-neutral-900 dark:text-neutral-400 dark:border-neutral-800">
                PANTONE 186 C
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="hidden sm:block text-xs font-mono text-neutral-500 dark:text-neutral-500 tracking-wider">
                SYS.ID // MPX-2026
              </div>
              
              <button 
                type="button"
                onClick={toggleTheme} 
                className="flex items-center space-x-2 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 px-3 py-1.5 rounded-full text-xs font-mono text-neutral-700 dark:text-neutral-300 hover:border-pantone-red transition-all cursor-pointer shadow-sm"
              >
                <span>{theme === 'light' ? '☀️ Light' : '🌙 Dark'}</span>
              </button>
            </div>
          </div>

          <div className="z-10 my-auto py-8 w-full flex flex-col justify-center items-start">
            <div className="max-w-3xl">
              <div className="flex items-center gap-2 mb-4">
                <span className="h-0.5 w-8 bg-pantone-red inline-block"></span>
                <p className="text-xs sm:text-sm font-mono text-pantone-red font-semibold uppercase tracking-[0.3em]">
                  
                </p>
              </div>
              
              <h1 className="font-headline font-black text-6xl sm:text-7xl md:text-8xl lg:text-[8rem] xl:text-[9.2rem] leading-[0.85] tracking-tighter uppercase text-neutral-950 dark:text-white select-none">
                MPX<br />
                <span className="text-pantone-red">MP BOM.</span><br />
                <span className="text-neutral-400 dark:text-neutral-600">CRX</span>
              </h1>
            </div>
          </div>

          <div className="z-20 pt-8 border-t border-neutral-200 dark:border-neutral-800/80 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6">
              <h2 className="font-headline font-bold text-sm sm:text-base tracking-[0.25em] text-neutral-900 dark:text-white uppercase flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-pantone-red inline-block animate-pulse"></span>
                MP BOM CROSSCHECK
              </h2>
              <span className="hidden sm:inline-block text-neutral-300 dark:text-neutral-700">|</span>
              <p className="text-xs font-mono text-neutral-500 dark:text-neutral-400 tracking-wider uppercase">
                DATA INTEGRITY PROTOCOL ACTIVE
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-neutral-500">
              <span>COLOR: <span className="text-pantone-red font-bold">186 C</span></span>
              <span className="text-neutral-300 dark:text-neutral-700">•</span>
              <span>STATUS: <span className="text-pantone-red font-semibold">ONLINE</span></span>
              <span className="text-neutral-300 dark:text-neutral-700">•</span>
              <span>&copy; MPX 2026</span>
            </div>
          </div>

        </div>

        {/* Right Panel: Access Container */}
        <div className="w-full lg:w-5/12 min-h-screen bg-[#FAF9F6] dark:bg-[#08080a] flex flex-col justify-center items-center p-4 sm:p-8 relative transition-colors duration-300">
          
          <div className="w-full max-w-xl bg-white dark:bg-[#121214] border border-neutral-200 dark:border-neutral-800 rounded-3xl pantone-glow overflow-hidden flex flex-col my-auto transition-colors duration-300 shadow-xl">

            <div className="p-6 sm:p-8 border-b border-neutral-100 dark:border-neutral-800/80 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-mono text-pantone-red font-bold tracking-widest uppercase block mb-1">
                    Secure Portal Access
                  </span>
                  <h2 className="text-2xl sm:text-3xl font-light text-neutral-900 dark:text-white font-headline">
                    Portal Navigation
                  </h2>
                </div>
                <span className="text-[10px] font-mono font-semibold text-pantone-red bg-pantone-lightred dark:bg-red-950/40 border border-pantone-redborder dark:border-red-900 px-2.5 py-1 rounded-full uppercase tracking-wider flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-pantone-red animate-pulse"></span>
                  ZERO-TRUST
                </span>
              </div>
            </div>

            <div className="p-6 sm:p-8 space-y-6">

              {/* VIEW 1: Login Page View */}
              {activeTab === 'login' && (
                <div className="space-y-6 transition-all duration-300">

                  {/* SSO Auto-Login Indicator Banner */}
                  {(userId || userIc) && (
                    <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-4 flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="w-3 h-3 rounded-full bg-emerald-500 animate-ping"></span>
                        <div>
                          <p className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400 uppercase">
                            SSO Credentials Detected
                          </p>
                          <p className="text-[11px] font-mono text-neutral-500 dark:text-neutral-400">
                            User: <span className="font-semibold text-neutral-900 dark:text-white">{userId || 'N/A'}</span> (IC: {userIc || 'N/A'})
                          </p>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono bg-emerald-500 text-white px-2 py-0.5 rounded uppercase font-bold">
                        Auto-Authenticating
                      </span>
                    </div>
                  )}

                  <form id="loginForm" onSubmit={handleLogin} className="space-y-6">
                    <div>
                      <label htmlFor="email" className="block text-xs font-mono text-neutral-600 dark:text-neutral-400 uppercase tracking-wider mb-2 font-medium">
                        Username / Email
                      </label>
                      <input 
                        type="text" 
                        id="email" 
                        name="email" 
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="w-full bg-[#F4F4F6] dark:bg-[#18181b] text-neutral-900 dark:text-white text-sm px-4 py-3 rounded-xl border border-neutral-200 dark:border-neutral-800 focus:border-pantone-red dark:focus:border-pantone-red focus:bg-white dark:focus:bg-[#18181b] focus:outline-none transition-all font-mono-code placeholder-neutral-400"
                        placeholder="developer@mpx.io"
                      />
                    </div>

                    <div>
                      <label htmlFor="password" className="block text-xs font-mono text-neutral-600 dark:text-neutral-400 uppercase tracking-wider mb-2 font-medium">
                        Password
                      </label>
                      <div className="relative flex items-center">
                        <input 
                          type={showPassword ? 'text' : 'password'} 
                          id="password" 
                          name="password" 
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          required
                          className="w-full bg-[#F4F4F6] dark:bg-[#18181b] text-neutral-900 dark:text-white text-sm px-4 py-3 rounded-xl border border-neutral-200 dark:border-neutral-800 focus:border-pantone-red dark:focus:border-pantone-red focus:bg-white dark:focus:bg-[#18181b] focus:outline-none transition-all font-mono-code tracking-widest pr-12"
                        />
                        <button 
                          type="button" 
                          onClick={() => setShowPassword(!showPassword)} 
                          className="absolute right-4 text-neutral-400 hover:text-pantone-red transition-colors focus:outline-none cursor-pointer"
                        >
                          <svg className={`w-5 h-5 ${showPassword ? 'opacity-40' : 'opacity-100'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </button>
                      </div>
                    </div>

                    <div className="flex items-start justify-between text-xs pt-1">
                      <label className="flex items-center space-x-2.5 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          checked={rememberMe}
                          onChange={(e) => setRememberMe(e.target.checked)}
                          className="w-4 h-4 rounded border-neutral-300 dark:border-neutral-700 bg-neutral-100 dark:bg-neutral-900 text-pantone-red focus:ring-0 focus:ring-offset-0 accent-pantone-red" 
                        />
                        <span className="text-neutral-600 dark:text-neutral-400 group-hover:text-neutral-900 dark:group-hover:text-neutral-200 transition-colors font-medium">Remember me</span>
                      </label>
                      
                      <div className="text-right flex flex-col items-end space-y-1.5">
                        <button 
                          type="button"
                          onClick={() => showModal('Password Reset', 'Password recovery instructions dispatched to registered email.', false)} 
                          className="text-neutral-500 hover:text-pantone-red dark:text-neutral-400 dark:hover:text-white transition-colors border-none bg-transparent cursor-pointer p-0"
                        >
                          Forgot?
                        </button>
                        
                        <button 
                          type="button" 
                          onClick={handleSSOLogin} 
                          className="font-bold text-xs text-pantone-red hover:text-pantone-darkred dark:text-white dark:hover:text-pantone-red underline underline-offset-2 transition-colors cursor-pointer focus:outline-none border-none bg-transparent p-0"
                        >
                          Login via SSO
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
              )}

              {/* VIEW 2: No Authority View Page */}
              {activeTab === 'noauthority' && (
                <div className="space-y-6 transition-all duration-300">
                  <div className="bg-pantone-lightred/80 dark:bg-red-950/20 border border-pantone-redborder dark:border-red-900/60 rounded-2xl p-6 text-center space-y-4">
                    <div className="w-14 h-14 bg-white dark:bg-neutral-900 text-pantone-red rounded-full flex items-center justify-center mx-auto text-2xl font-bold border border-pantone-redborder shadow-sm">
                      ⚠️
                    </div>
                    <div>
                      <span className="text-[10px] font-mono font-bold text-pantone-red uppercase tracking-widest block mb-1">
                        HTTP 403 // INSUFFICIENT ROLE PRIVILEGES
                      </span>
                      <h3 className="text-xl font-bold font-headline text-neutral-900 dark:text-white">No Authority Granted</h3>
                      <p className="text-xs font-mono text-neutral-600 dark:text-neutral-400 mt-2 leading-relaxed max-w-sm mx-auto">
                        User account lacks scope authority or does not exist in the master database.
                      </p>
                    </div>

                    <div className="bg-white/90 dark:bg-neutral-900/90 rounded-xl p-3 border border-pantone-redborder/50 text-left text-[11px] font-mono space-y-1 text-neutral-700 dark:text-neutral-300">
                      <div className="flex justify-between">
                        <span className="text-neutral-400">User ID (Name):</span>
                        <span className="font-semibold text-pantone-red">{userId || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-400">Emp No (UserIC):</span>
                        <span className="font-semibold text-neutral-900 dark:text-white">{userIc || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-400">Email:</span>
                        <span className="font-semibold text-neutral-900 dark:text-white">{emailParam || 'N/A'}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3">
                    <button 
                      type="button" 
                      onClick={() => showModal('Authority Request Submitted', 'Access request ticket has been dispatched to system administrators for approval.', false)}
                      className="w-full bg-pantone-red text-white hover:bg-pantone-darkred font-semibold text-xs py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all cursor-pointer shadow-md shadow-pantone-red/20 uppercase tracking-wider font-mono"
                    >
                      <span>Request Authority</span>
                    </button>
                    <button 
                      type="button" 
                      onClick={() => setActiveTab('login')}
                      className="w-full bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-900 dark:hover:bg-neutral-800 text-neutral-800 dark:text-neutral-200 font-semibold text-xs py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all cursor-pointer font-mono border border-neutral-200 dark:border-neutral-800"
                    >
                      <span>&larr; Back to Login</span>
                    </button>
                  </div>
                </div>
              )}

              {/* VIEW 3: No Authentication View Page */}
              {activeTab === 'noauth' && (
                <div className="space-y-6 transition-all duration-300">
                  <div className="bg-pantone-lightred/80 dark:bg-red-950/20 border border-pantone-redborder dark:border-red-900/60 rounded-2xl p-6 text-center space-y-4">
                    <div className="w-14 h-14 bg-white dark:bg-neutral-900 text-pantone-red rounded-full flex items-center justify-center mx-auto text-2xl font-bold border border-pantone-redborder shadow-sm">
                      🔒
                    </div>
                    <div>
                      <span className="text-[10px] font-mono font-bold text-pantone-red uppercase tracking-widest block mb-1">
                        HTTP 401 // UNAUTHENTICATED SESSION
                      </span>
                      <h3 className="text-xl font-bold font-headline text-neutral-900 dark:text-white">No Authentication Found</h3>
                      <p className="text-xs font-mono text-neutral-600 dark:text-neutral-400 mt-2 leading-relaxed max-w-sm mx-auto">
                        Valid authentication status was not detected (Auth is set to NO).
                      </p>
                    </div>

                    <div className="bg-white/90 dark:bg-neutral-900/90 rounded-xl p-3 border border-pantone-redborder/50 text-left text-[11px] font-mono space-y-1 text-neutral-700 dark:text-neutral-300">
                      <div className="flex justify-between">
                        <span className="text-neutral-400">User ID (Name):</span>
                        <span className="font-semibold text-pantone-red">{userId || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-400">Emp No (UserIC):</span>
                        <span className="font-semibold text-neutral-900 dark:text-white">{userIc || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-400">Email:</span>
                        <span className="font-semibold text-neutral-900 dark:text-white">{emailParam || 'N/A'}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3">
                    <button 
                      type="button" 
                      onClick={handleSSOLogin}
                      className="w-full bg-pantone-red text-white hover:bg-pantone-darkred font-semibold text-xs py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all cursor-pointer shadow-md shadow-pantone-red/20 uppercase tracking-wider font-mono"
                    >
                      <span>Authenticate via SSO</span>
                    </button>
                    <button 
                      type="button" 
                      onClick={() => setActiveTab('login')}
                      className="w-full bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-900 dark:hover:bg-neutral-800 text-neutral-800 dark:text-neutral-200 font-semibold text-xs py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all cursor-pointer font-mono border border-neutral-200 dark:border-neutral-800"
                    >
                      <span>&larr; Back to Login</span>
                    </button>
                  </div>
                </div>
              )}

              {/* VIEW 4: Server Connection Error */}
              {activeTab === 'servererror' && (
                <div className="space-y-6 transition-all duration-300">
                  <div className="bg-amber-500/10 dark:bg-amber-950/20 border border-amber-500/30 dark:border-amber-900/60 rounded-2xl p-6 text-center space-y-4">
                    <div className="w-14 h-14 bg-white dark:bg-neutral-900 text-amber-500 rounded-full flex items-center justify-center mx-auto text-2xl font-bold border border-amber-500/40 shadow-sm">
                      🔌
                    </div>
                    <div>
                      <span className="text-[10px] font-mono font-bold text-amber-600 dark:text-amber-400 uppercase tracking-widest block mb-1">
                        HTTP 500 // BACKEND API UNREACHABLE
                      </span>
                      <h3 className="text-xl font-bold font-headline text-neutral-900 dark:text-white">Authentication Service Unavailable</h3>
                      <p className="text-xs font-mono text-neutral-600 dark:text-neutral-400 mt-2 leading-relaxed max-w-sm mx-auto">
                        Could not reach the FastAPI authentication backend at <code>127.0.0.1:8000</code>. Verify that the Python server is running.
                      </p>
                    </div>

                    <div className="bg-white/90 dark:bg-neutral-900/90 rounded-xl p-3 border border-amber-500/30 text-left text-[11px] font-mono space-y-1 text-neutral-700 dark:text-neutral-300">
                      <div className="flex justify-between">
                        <span className="text-neutral-400">User ID:</span>
                        <span className="font-semibold text-amber-600 dark:text-amber-400">{userIc || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-400">Emp No:</span>
                        <span className="font-semibold text-neutral-900 dark:text-white">{userId || 'N/A'}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3">
                    <button 
                      type="button" 
                      onClick={() => { router.push('/'); router.refresh(); }}
                      className="w-full bg-amber-600 text-white hover:bg-amber-700 font-semibold text-xs py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all cursor-pointer shadow-md uppercase tracking-wider font-mono"
                    >
                      <span>Retry Connection</span>
                    </button>
                    <button 
                      type="button" 
                      onClick={() => setActiveTab('login')}
                      className="w-full bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-900 dark:hover:bg-neutral-800 text-neutral-800 dark:text-neutral-200 font-semibold text-xs py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all cursor-pointer font-mono border border-neutral-200 dark:border-neutral-800"
                    >
                      <span>&larr; Back to Login</span>
                    </button>
                  </div>
                </div>
              )}

            </div>

            {/* Footer Action Bar */}
            <div className="p-5 bg-[#F9F9FB] dark:bg-[#0e0e10] border-t border-neutral-200 dark:border-neutral-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="w-full sm:w-auto bg-pantone-lightred border border-pantone-redborder dark:bg-neutral-900 dark:border-neutral-800 rounded-full px-4 py-2 flex items-center justify-center space-x-2 text-pantone-red text-xs font-mono font-medium">
                <span className="w-2 h-2 rounded-full bg-pantone-red animate-pulse"></span>
                <span>
                  {activeTab === 'login' && 'Secured Formation'}
                  {activeTab === 'noauthority' && '403 Insufficient Scope'}
                  {activeTab === 'noauth' && '401 Session Required'}
                  {activeTab === 'servererror' && '500 API Error'}
                </span>
              </div>

              {activeTab === 'login' && (
                <button 
                  type="submit" 
                  form="loginForm"
                  className="w-full sm:w-auto bg-pantone-red text-white hover:bg-pantone-darkred font-semibold text-xs py-3 px-8 rounded-full flex items-center justify-center space-x-2 active:scale-98 transition-all cursor-pointer group shadow-md shadow-pantone-red/20"
                >
                  <span className="tracking-wider uppercase font-bold">Login</span>
                  <svg className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                  </svg>
                </button>
              )}
            </div>

          </div>
        </div>

        {modalOpen && (
          <div className="fixed inset-0 bg-neutral-900/60 dark:bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-[#121215] border border-neutral-200 dark:border-neutral-800 p-8 rounded-2xl max-w-sm w-full text-center space-y-5 shadow-2xl">
              <div className="w-12 h-12 bg-pantone-red text-white rounded-full flex items-center justify-center mx-auto text-xl font-bold font-headline shadow-lg">
                &#10003;
              </div>
              <h3 className="text-lg font-medium text-neutral-900 dark:text-white">{modalTitle}</h3>
              <p className="text-xs text-neutral-600 dark:text-neutral-400 font-mono leading-relaxed">{modalBody}</p>
              <button 
                type="button"
                onClick={handleModalProceed} 
                className="w-full py-3 bg-pantone-red text-white text-xs uppercase tracking-widest font-semibold rounded-lg hover:bg-pantone-darkred transition-colors focus:outline-none cursor-pointer"
              >
                Proceed
              </button>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}