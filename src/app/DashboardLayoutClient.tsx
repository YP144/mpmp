// src/app/DashboardLayoutClient.tsx
"use client";

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import { updateUrlParams } from '@/lib/urlState';
import DashboardClient, { BomItem } from './DashboardClient';
import GlobalClient from './GlobalClient';
import ManualCompareClient from './ManualCompareClient';
import LogisticsDashboard from './SubsidiaryCrosscheckClient';
import GlobalSearchClient from './GlobalSearchClient';
import DatabasePage from './dev_options/history/page';

interface SsoUserProps {
    userId: string | null;
    userIc: string | null;
    userName: string | null;
    ssolgenet: string | null;
}

interface DashboardLayoutClientProps {
    initialBomData: BomItem[];
    ssoUser?: SsoUserProps;
}

type ViewType =
    | 'dashboard'
    | 'global'
    | 'global-search'
    | 'tool-option-mp'
    | 'manual-compare'
    | 'eco-tracker'
    | 'tool-option-check'
    | 'reference-library'
    | 'mpx-crosschecking'
    | 'subsidiary-crosschecking'
    | 'dev-history'
    | 'dev-mapping'
    | 'dev-logging'
    | 'dev-auth';

/**
 * Nama menu di URL (?menu=...). Menu tanpa nama di sini tidak disimpan ke URL.
 * Contoh: /?menu=global-overview  -> refresh / link yang dibagikan langsung membuka Global Overview
 */
const MENU_SLUGS: Partial<Record<ViewType, string>> = {
    'dashboard': 'my-bom',
    'global': 'global-overview',
    'global-search': 'adam',
    'manual-compare': 'manual-compare',
    'subsidiary-crosschecking': 'subsidiary-crosschecking',
    'dev-logging': 'system-logging',
    'dev-mapping': 'model-mapping',
    'dev-history': 'audit-report',
    'dev-auth': 'data-verification',
};

// Menu Developer Tool: hanya untuk user yang punya akses (canAccessDevTools)
const DEV_VIEWS: ViewType[] = ['dev-logging', 'dev-mapping', 'dev-history', 'dev-auth'];

function viewFromMenuSlug(slug: string | null): ViewType | null {
    if (!slug) return null;
    const found = (Object.entries(MENU_SLUGS) as [ViewType, string][]).find(([, s]) => s === slug);
    return found ? found[0] : null;
}

interface NavItemConfig {
    id: ViewType;
    name: string;
    description?: string;
    tooltip: string;
    icon: React.ReactNode;
}

interface ChatMessage {
    id: string;
    sender: 'user' | 'adam';
    text: string;
    timestamp: string;
}

export default function DashboardLayoutClient({ initialBomData, ssoUser }: DashboardLayoutClientProps) {
    const hasOnlyIdOrIc = Boolean(
        (ssoUser?.userId && !ssoUser?.userIc) || (!ssoUser?.userId && ssoUser?.userIc)
    );

    const [isCollapsed, setIsCollapsed] = useState<boolean>(false);
    const [isDarkTheme, setIsDarkTheme] = useState<boolean>(false);
    const [searchQuery, setSearchQuery] = useState<string>('');

    const canAccessDevTools = useMemo(() => {
        const name = ssoUser?.userName ? ssoUser.userName.trim().toUpperCase() : '';
        if (!name) return false;
        const ALLOWED_USERS = ['YUDHISTIRA RANGGAWIDJAYA', 'YOSEP PUTRA SETIYANTO', 'AHMAD IFANDI', 'KIM SEUNGHO'];
        return ALLOWED_USERS.includes(name);
    }, [ssoUser?.userName]);

    // Menu aktif dibaca dari URL (?menu=...), bukan dari state, supaya tetap sama setelah refresh
    // dan tombol Back / Forward browser ikut berfungsi.
    const searchParams = useSearchParams();
    const defaultView: ViewType = hasOnlyIdOrIc ? 'global' : 'dashboard';
    const currentView = useMemo<ViewType>(() => {
        const view = viewFromMenuSlug(searchParams.get('menu'));
        if (!view) return defaultView;
        if (DEV_VIEWS.includes(view) && !canAccessDevTools) return defaultView;
        return view;
    }, [searchParams, defaultView, canAccessDevTools]);

    /** Pindah menu: URL diganti tanpa reload (instan). Parameter milik halaman sebelumnya dibuang. */
    const setCurrentView = (view: ViewType) => {
        if (view === currentView) return;
        updateUrlParams({ menu: MENU_SLUGS[view] ?? null }, { mode: 'push', clearOthers: true });
    };

    const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
    const [chatInput, setChatInput] = useState<string>('');
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: '1',
            sender: 'adam',
            text: 'Hello! I am ADAM AI Assistant. How can I help you today?',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
    ]);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (isChatOpen) {
            scrollToBottom();
        }
    }, [messages, isChatOpen]);

    useEffect(() => {
        if (ssoUser) {
            console.log('[Browser Console] Current SSO User Loaded:', {
                userId: ssoUser.userId,
                userIc: ssoUser.userIc,
                userName: ssoUser.userName,
                ssolgenet: ssoUser.ssolgenet
            });
        }
    }, [ssoUser]);

    useEffect(() => {
        if (isDarkTheme) {
            document.documentElement.setAttribute('data-theme', 'dark');
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
            document.documentElement.classList.remove('dark');
        }
    }, [isDarkTheme]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
                e.preventDefault();
                setIsCollapsed(prev => !prev);
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    const handleSendMessage = (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        const trimmed = chatInput.trim();
        if (!trimmed) return;

        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            sender: 'user',
            text: trimmed,
            timestamp: timeStr
        };

        const adamResponse: ChatMessage = {
            id: (Date.now() + 1).toString(),
            sender: 'adam',
            text: 'ADAM currently Unavailable, please check in again later Thank you',
            timestamp: timeStr
        };

        setMessages(prev => [...prev, userMsg, adamResponse]);
        setChatInput('');
    };

    const overviewItems: NavItemConfig[] = [
        {
            id: 'dashboard',
            name: 'My BOM',
            description: 'Overview & metrics',
            tooltip: 'Dashboard',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="7" height="9" rx="1"></rect>
                    <rect x="14" y="3" width="7" height="5" rx="1"></rect>
                    <rect x="14" y="12" width="7" height="9" rx="1"></rect>
                    <rect x="3" y="16" width="7" height="5" rx="1"></rect>
                </svg>
            ),
        },
        {
            id: 'global',
            name: 'Global Overview',
            description: 'Global workspace view',
            tooltip: 'Global Client',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="2" y1="12" x2="22" y2="12"></line>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
            ),
        },
        {
            id: 'global-search',
            name: 'ADAM',
            description: 'Global search',
            tooltip: 'Global Search',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            ),
        },
    ];

    const crosscheckItems: NavItemConfig[] = [
        {
            id: 'manual-compare',
            name: 'Manual Compare',
            description: 'Compare BOM items manually',
            tooltip: 'Manual Compare',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M16 3h5v5"></path>
                    <path d="M4 20L21 3"></path>
                    <path d="M21 16v5h-5"></path>
                    <path d="M15 15l6 6"></path>
                    <path d="M4 4l5 5"></path>
                </svg>
            ),
        },
        {
            id: 'subsidiary-crosschecking',
            name: 'Subsidiary Crosschecking',
            description: 'Logistics & subsidiary BOM crosscheck',
            tooltip: 'Subsidiary Crosscheck',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="1" y="3" width="15" height="13" rx="2"></rect>
                    <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
                    <circle cx="5.5" cy="18.5" r="2.5"></circle>
                    <circle cx="18.5" cy="18.5" r="2.5"></circle>
                </svg>
            ),
        },
    ];

    const devToolItems: NavItemConfig[] = [
        {
            id: 'dev-logging',
            name: 'System Logging',
            description: 'Execution & error logs',
            tooltip: 'Logging',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="4 17 10 11 14 15 20 9"></polyline>
                    <line x1="12" y1="19" x2="20" y2="19"></line>
                </svg>
            ),
        },
        {
            id: 'dev-mapping',
            name: 'Model Mapping',
            description: 'Data field relationship mapping',
            tooltip: 'Mapping',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
                    <line x1="8" y1="2" x2="8" y2="18"></line>
                    <line x1="16" y1="6" x2="16" y2="22"></line>
                </svg>
            ),
        },
        {
            id: 'dev-history',
            name: 'Audit Report',
            description: 'Inspection audit reports',
            tooltip: 'Report',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
            ),
        },
        {
            id: 'dev-auth',
            name: 'Data Verification',
            description: 'Verify system initial flags',
            tooltip: 'Verification',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                    <polyline points="9 12 11 14 15 10"></polyline>
                </svg>
            ),
        },
    ];

    const renderMainContent = () => {
        switch (currentView) {
            case 'dashboard':
                return React.createElement(DashboardClient as any, { initialBomData, userName: ssoUser?.userName || undefined });
            case 'global':
                return React.createElement(GlobalClient as any, { initialBomData });
            case 'global-search':
                return React.createElement(GlobalSearchClient as any, { initialBomData, ssoUser });
            case 'manual-compare':
                return React.createElement(ManualCompareClient as any, { initialBomData });
            case 'subsidiary-crosschecking':
                return React.createElement(LogisticsDashboard as any, { initialBomData });
            case 'dev-logging':
                return <DatabasePage />;
            case 'dev-mapping':
                return (
                    <div className="p-6 max-w-[1800px] mx-auto space-y-4">
                        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                            <h2 className="text-lg font-bold text-slate-800 flex items-center space-x-2">
                                <i className="fa-solid fa-sitemap text-pantone-700"></i>
                                <span>Developer Tool Section: Model Mapping</span>
                            </h2>
                            <p className="text-xs text-slate-500 mt-1">Model field relationships, dev-to-MP structure maps, and schema alignment.</p>
                            <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-xl">
                                <p className="text-xs font-semibold text-slate-700">Active Mappings Loaded:</p>
                                <ul className="mt-2 text-xs space-y-1 font-mono text-slate-600">
                                    <li>MP Model ➔ Dev Model ➔ Initial Model</li>
                                    <li>Circuit PIC ➔ Subsidiary Plant ➔ Market Region</li>
                                    <li>Structure Group ➔ Ben Comp ➔ HW Tool Option</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                );
            case 'dev-history':
                return (
                    <div className="p-6 max-w-[1800px] mx-auto space-y-4">
                        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                            <h2 className="text-lg font-bold text-slate-800 flex items-center space-x-2">
                                <i className="fa-solid fa-file-contract text-pantone-700"></i>
                                <span>Developer Tool Section: Audit Report</span>
                            </h2>
                            <p className="text-xs text-slate-500 mt-1">Historical inspection reports, retest archives, and verification trails.</p>
                            <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600">
                                System ready for audit export. Total models under monitoring: <strong>{initialBomData.length}</strong>
                            </div>
                        </div>
                    </div>
                );
            case 'dev-auth':
                return (
                    <div className="p-6 max-w-[1800px] mx-auto space-y-4">
                        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                            <h2 className="text-lg font-bold text-slate-800 flex items-center space-x-2">
                                <i className="fa-solid fa-shield-halved text-pantone-700"></i>
                                <span>Developer Tool Section: Data Verification</span>
                            </h2>
                            <p className="text-xs text-slate-500 mt-1">Verification portal for system initial updaters and automated checks.</p>
                            <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900">
                                Authorized Inspector: <strong>{ssoUser?.userName}</strong>. Data verification engine operational.
                            </div>
                        </div>
                    </div>
                );
            default:
                return <DashboardClient initialBomData={initialBomData} userName={ssoUser?.userName || undefined} />;
        }
    };

    return (
        <div className="h-screen overflow-hidden bg-slate-100 flex flex-col font-sans">
            {/* Kerangka aplikasi setinggi layar: header tetap di atas, sidebar & isi menu masing-masing scroll sendiri.
                Dengan ini halaman (mis. tabel My BOM / Global Overview) bisa menyesuaikan tinggi dengan sisa layar. */}
            {/* Top Navigation Bar */}
            <header className="h-16 flex-none bg-white border-b border-slate-200 px-4 flex items-center justify-between sticky top-0 z-40 shadow-sm">
                <div className="flex items-center space-x-3">
                    <button
                        onClick={() => setIsCollapsed(!isCollapsed)}
                        className="p-2 rounded-xl text-slate-500 hover:bg-slate-100 transition-colors"
                        title="Toggle Navigation Sidebar (Ctrl+B)"
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="3" y1="12" x2="21" y2="12"></line>
                            <line x1="3" y1="6" x2="21" y2="6"></line>
                            <line x1="3" y1="18" x2="21" y2="18"></line>
                        </svg>
                    </button>

                    <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 rounded-xl bg-pantone-700 text-white flex items-center justify-center font-bold text-sm shadow-sm">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-swords preview-icon"><path d="m13 19 6-6"/><path d="M14.5 17.5 3.586 6.586A2 2 0 013 5.172V3h2.172a2 2 0 011.414.586L17.5 14.5"/><path d="m14.828 6.172 2.586-2.586A2 2 0 0118.828 3H21v2.172a2 2 0 01-.586 1.414l-2.586 2.586"/><path d="m16 16 4 4"/><path d="m19 21 2-2"/><path d="m5 14 4 4"/><path d="m5 21-2-2"/><path d="M7.5 16.5 4 20"/></svg>
                        </div>
                        <span className="font-extrabold text-slate-800 text-sm uppercase tracking-wider hidden sm:inline">
                            MPX
                        </span>
                    </div>
                </div>

                <div className="flex items-center space-x-3">
                    {/* Slot kontrol khusus halaman (mis. Filter Year My BOM, diisi lewat createPortal) */}
                    <div id="page-header-actions" className="flex items-center"></div>

                    {/* ADAM AI Assistant: dipindah ke header supaya tidak menutupi tombol di pojok bawah halaman */}
                    <button
                        onClick={() => setIsChatOpen(!isChatOpen)}
                        className={`flex items-center space-x-2 px-3 py-1.5 rounded-xl border text-xs font-bold transition-colors ${
                            isChatOpen
                                ? 'bg-pantone-700 border-pantone-700 text-white'
                                : 'bg-white border-pantone-200 text-pantone-800 hover:bg-pantone-50'
                        }`}
                        title={isChatOpen ? 'Close ADAM AI Assistant' : 'Open ADAM AI Assistant'}
                    >
                        <i className="fa-solid fa-robot"></i>
                        <span className="hidden md:inline">Ask ADAM</span>
                    </button>

                    <div className="flex items-center space-x-2 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl">
                        <div className="w-6 h-6 rounded-full bg-pantone-100 text-pantone-800 flex items-center justify-center font-bold text-xs">
                            {ssoUser?.userName ? ssoUser.userName.charAt(0) : 'U'}
                        </div>
                        <div className="text-left hidden md:block">
                            <div className="text-xs font-bold text-slate-800 leading-tight">
                                {ssoUser?.userName || 'Guest User'}
                            </div>
                            <div className="text-[10px] text-slate-400 font-mono leading-tight">
                                {ssoUser?.userId || ssoUser?.userIc || 'SSO Active'}
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={() => setIsDarkTheme(!isDarkTheme)}
                        className="p-2 rounded-xl text-slate-500 hover:bg-slate-100 transition-colors"
                        title="Toggle Theme"
                    >
                        <i className={`fa-solid ${isDarkTheme ? 'fa-sun text-amber-500' : 'fa-moon'}`}></i>
                    </button>
                </div>
            </header>

            <div className="flex-1 min-h-0 flex overflow-hidden">
                <aside
                    className={`bg-white border-r border-slate-200 transition-all duration-300 ease-in-out flex flex-col shrink-0 ${
                        isCollapsed ? 'w-16' : 'w-64'
                    }`}
                >
                    <div className="flex-1 overflow-y-auto p-3 space-y-6">
                        <div>
                            {!isCollapsed && (
                                <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-3 mb-2">
                                    Overview
                                </h3>
                            )}
                            <div className="space-y-1">
                                {overviewItems.map(item => (
                                    <button
                                        key={item.id}
                                        onClick={() => setCurrentView(item.id)}
                                        title={isCollapsed ? item.tooltip : undefined}
                                        className={`w-full flex items-center ${
                                            isCollapsed ? 'justify-center px-2' : 'px-3'
                                        } py-2.5 rounded-xl text-xs font-bold transition-all ${
                                            currentView === item.id
                                                ? 'bg-pantone-700 text-white shadow-sm'
                                                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                                        }`}
                                    >
                                        <span className={currentView === item.id ? 'text-white' : 'text-slate-500'}>
                                            {item.icon}
                                        </span>
                                        {!isCollapsed && <span className="ml-3 truncate">{item.name}</span>}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div>
                            {!isCollapsed && (
                                <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-3 mb-2">
                                    Crosschecking Tools
                                </h3>
                            )}
                            <div className="space-y-1">
                                {crosscheckItems.map(item => (
                                    <button
                                        key={item.id}
                                        onClick={() => setCurrentView(item.id)}
                                        title={isCollapsed ? item.tooltip : undefined}
                                        className={`w-full flex items-center ${
                                            isCollapsed ? 'justify-center px-2' : 'px-3'
                                        } py-2.5 rounded-xl text-xs font-bold transition-all ${
                                            currentView === item.id
                                                ? 'bg-pantone-700 text-white shadow-sm'
                                                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                                        }`}
                                    >
                                        <span className={currentView === item.id ? 'text-white' : 'text-slate-500'}>
                                            {item.icon}
                                        </span>
                                        {!isCollapsed && <span className="ml-3 truncate">{item.name}</span>}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {canAccessDevTools && (
                            <div>
                                {!isCollapsed && (
                                    <h3 className="text-[10px] font-bold text-pantone-700 uppercase tracking-wider px-3 mb-2 flex items-center space-x-1">
                                        <i className="fa-solid fa-code text-[10px]"></i>
                                        <span>Developer Tool Section</span>
                                    </h3>
                                )}
                                <div className="space-y-1">
                                    {devToolItems.map(item => (
                                        <button
                                            key={item.id}
                                            onClick={() => setCurrentView(item.id)}
                                            title={isCollapsed ? item.tooltip : undefined}
                                            className={`w-full flex items-center ${
                                                isCollapsed ? 'justify-center px-2' : 'px-3'
                                            } py-2.5 rounded-xl text-xs font-bold transition-all ${
                                                currentView === item.id
                                                    ? 'bg-pantone-700 text-white shadow-sm'
                                                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                                            }`}
                                        >
                                            <span className={currentView === item.id ? 'text-white' : 'text-pantone-700'}>
                                                {item.icon}
                                            </span>
                                            {!isCollapsed && <span className="ml-3 truncate">{item.name}</span>}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </aside>

                <main className="flex-1 min-w-0 min-h-0 overflow-y-auto bg-slate-100">
                    {renderMainContent()}
                </main>
            </div>

            {/* Panel chat ADAM: muncul di bawah tombol "Ask ADAM" di header */}
            <div className="fixed top-[72px] right-6 z-50">
                {isChatOpen && (
                    <div className="w-80 sm:w-96 h-[480px] max-h-[calc(100vh-96px)] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
                        <div className="p-3.5 bg-pantone-900 text-white flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                                <div className="w-7 h-7 rounded-lg bg-pantone-700 flex items-center justify-center text-white text-xs">
                                    <i className="fa-solid fa-robot"></i>
                                </div>
                                <div>
                                    <h4 className="font-bold text-xs leading-tight">ADAM AI Assistant</h4>
                                    <span className="text-[10px] text-pantone-200 font-mono">Automated Intelligence</span>
                                </div>
                            </div>
                            <button
                                onClick={() => setIsChatOpen(false)}
                                className="text-pantone-200 hover:text-white p-1"
                            >
                                <i className="fa-solid fa-xmark text-sm"></i>
                            </button>
                        </div>

                        <div className="flex-1 p-3 overflow-y-auto space-y-3 bg-slate-50/50 text-xs">
                            {messages.map(msg => (
                                <div
                                    key={msg.id}
                                    className={`flex flex-col ${
                                        msg.sender === 'user' ? 'items-end' : 'items-start'
                                    }`}
                                >
                                    <div
                                        className={`p-2.5 rounded-2xl max-w-[85%] ${
                                            msg.sender === 'user'
                                                ? 'bg-pantone-700 text-white rounded-br-none'
                                                : 'bg-white border border-slate-200 text-slate-800 shadow-sm rounded-bl-none'
                                        }`}
                                    >
                                        <p className="leading-relaxed">{msg.text}</p>
                                    </div>
                                    <span className="text-[9px] text-slate-400 mt-1 px-1 font-mono">
                                        {msg.timestamp}
                                    </span>
                                </div>
                            ))}
                            <div ref={messagesEndRef} />
                        </div>

                        <form onSubmit={handleSendMessage} className="p-2.5 bg-white border-t border-slate-200 flex space-x-2">
                            <input
                                type="text"
                                value={chatInput}
                                onChange={e => setChatInput(e.target.value)}
                                placeholder="Ask ADAM a question..."
                                className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-1 focus:ring-pantone-700"
                            />
                            <button
                                type="submit"
                                className="p-2 bg-pantone-700 hover:bg-pantone-800 text-white rounded-xl text-xs font-bold transition-colors"
                            >
                                <i className="fa-solid fa-paper-plane"></i>
                            </button>
                        </form>
                    </div>
                )}
            </div>
        </div>
    );
}