// src/app/dev_options/history/page.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { 
  Download, RefreshCw, Filter, MoreHorizontal, Edit3, Shield, 
  Terminal, Activity, Database, Server, Cpu, FileText, CheckCircle2, 
  AlertTriangle, Clock, Copy, Check, Lock, Globe, Search, Radio, PanelRightOpen, PanelRightClose
} from 'lucide-react';

interface SummaryResult {
  Structure?: string;
  HWcompare?: string;
  subsCompare?: string;
  multiOption?: string;
  tooloptionMaster?: string;
  operationPlan?: string;
  overallResult?: string;
  compareNote?: string;
}

interface ChangeEvent {
  operationType: string;
  documentKey?: { _id: string };
  fullDocument?: Record<string, any>;
  updateDescription?: {
    updatedFields?: Record<string, any>;
  };
  clusterTime?: string;
  timestamp?: string;
}

interface HistoricalDoc {
  _id: string;
  targetName?: string;
  devName?: string;
  initName?: string;
  SummaryResult?: SummaryResult;
  createdAt?: string;
  updatedAt?: string;
  timestamp?: string;
  [key: string]: any;
}

const ITEMS_PER_PAGE = 15;

function matchesQuery(value: any, query: string): boolean {
  if (!query.trim()) return true;
  const q = query.toLowerCase().replace(/["']/g, '').trim();

  if (q.includes(':')) {
    const [rawKey, rawVal] = q.split(':').map((s) => s.trim().replace(/["']/g, ''));
    if (value !== null && typeof value === 'object') {
      for (const [k, v] of Object.entries(value)) {
        if (k.toLowerCase().includes(rawKey)) {
          if (String(v).toLowerCase().includes(rawVal)) return true;
        }
        if (matchesQuery(v, query)) return true;
      }
    }
    return false;
  }

  if (value === null || value === undefined) return false;
  if (typeof value === 'object') {
    for (const [k, v] of Object.entries(value)) {
      if (k.toLowerCase().includes(q)) return true;
      if (matchesQuery(v, query)) return true;
    }
  }
  return String(value).toLowerCase().includes(q);
}

function JsonTreeNode({ name, value, level = 0, searchQuery = '' }: { name?: string; value: any; level?: number; searchQuery?: string }) {
  const isObject = value !== null && typeof value === 'object';
  const isArray = Array.isArray(value);

  const hasMatch = searchQuery.trim() ? matchesQuery(value, searchQuery) || (name && name.toLowerCase().includes(searchQuery.toLowerCase().replace(/["']/g, '').split(':')[0])) : true;
  const [collapsed, setCollapsed] = useState(level > 2 || (!!searchQuery && !hasMatch));

  useEffect(() => {
    if (searchQuery.trim() && hasMatch) {
      setCollapsed(false);
    }
  }, [searchQuery, hasMatch]);

  if (!hasMatch && searchQuery.trim()) {
    return null;
  }

  const renderValue = (val: any) => {
    if (val === null) return <span className="text-rose-500">null</span>;
    if (typeof val === 'boolean') return <span className="text-amber-500">{val ? 'true' : 'false'}</span>;
    if (typeof val === 'number') return <span className="text-sky-400">{val}</span>;
    if (typeof val === 'string') return <span className="text-lime-400">&quot;{val}&quot;</span>;
    return <span>{String(val)}</span>;
  };

  if (!isObject) {
    return (
      <div className="font-mono text-xs leading-relaxed" style={{ paddingLeft: `${level * 16}px` }}>
        {name && <span className="text-rose-400">&quot;{name}&quot;</span>}
        {name && <span className="text-slate-400">: </span>}
        {renderValue(value)}
      </div>
    );
  }

  const entries = isArray ? (value as any[]).map((v, i) => [i, v]) : Object.entries(value);

  return (
    <div className="font-mono text-xs leading-relaxed">
      <div
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center gap-1 cursor-pointer select-none hover:bg-white/5 rounded px-1 transition-colors"
        style={{ paddingLeft: `${level * 12}px` }}
      >
        <span className="text-slate-400 text-[10px] w-3 text-center inline-block">
          {collapsed ? '▶' : '▼'}
        </span>
        {name && <span className="text-rose-400">&quot;{name}&quot;</span>}
        {name && <span className="text-slate-400">: </span>}
        <span className="text-slate-300">{isArray ? `[${entries.length}]` : `{${entries.length}}`}</span>
      </div>

      {!collapsed && (
        <div className="border-l border-slate-700/40 ml-3 pl-2">
          {entries.map(([k, v]) => (
            <JsonTreeNode key={k} name={isArray ? undefined : String(k)} value={v} level={level + 1} searchQuery={searchQuery} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [liveLogs, setLiveLogs] = useState<ChangeEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [showLiveModal, setShowLiveModal] = useState(false);

  const [historyDocs, setHistoryDocs] = useState<HistoricalDoc[]>([]);
  const [initialRequestCount, setInitialRequestCount] = useState<number>(0);
  const [loadingHistory, setLoadingHistory] = useState(true);

  const [sortOrder, setSortOrder] = useState<'latest' | 'oldest'>('latest');
  const [historySearchQuery, setHistorySearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const [activePayload, setActivePayload] = useState<{ title: string; data: any } | null>(null);
  const [sidebarSearchQuery, setSidebarSearchQuery] = useState('');
  const [isEditMode, setIsEditMode] = useState(false);
  const [editableJsonString, setEditableJsonString] = useState('');
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [isMaximized, setIsMaximized] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);

  const [notes, setNotes] = useState('Ensure cluster threshold alerts are set to notify on-call rotation if latency exceeds 250ms.');
  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [copied, setCopied] = useState(false);

  // Hidden by default operator panel toggle
  const [showOperatorPanel, setShowOperatorPanel] = useState(false);

  useEffect(() => {
    if (activePayload) {
      setEditableJsonString(JSON.stringify(activePayload.data, null, 2));
      setJsonError(null);
      setIsEditMode(false);
      setIsMinimized(false);
    }
  }, [activePayload]);

  const extractMetadata = (doc: Record<string, any>) => {
    const source = doc?.fullDocument || doc;
    const summary: SummaryResult | undefined = source?.SummaryResult;

    return {
      targetName: source?.targetName || 'N/A',
      devName: source?.devName || 'N/A',
      initName: source?.initName || 'N/A',
      overallResult: summary?.overallResult || 'N/A',
      summaryResult: summary,
    };
  };

  const renderStatusBadge = (status: string) => {
    let bgColor = 'bg-slate-100 text-slate-700 border-slate-200';
    if (status.toUpperCase() === 'OK') {
      bgColor = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    } else if (status.toUpperCase() === 'CHECK') {
      bgColor = 'bg-amber-50 text-amber-700 border-amber-200';
    } else if (status.toUpperCase() === 'NG' || status.toUpperCase() === 'FAIL') {
      bgColor = 'bg-rose-50 text-rose-700 border-rose-200';
    }

    return (
      <span className={`px-2.5 py-1 rounded-md text-xs font-semibold border shadow-sm ${bgColor}`}>
        Result: {status}
      </span>
    );
  };

  const extractTimestamp = (doc: any): string => {
    const rawDate = doc.createdAt || doc.updatedAt || doc.timestamp || doc.clusterTime;
    if (rawDate) {
      const parsed = typeof rawDate === 'number' ? new Date(rawDate * 1000) : new Date(rawDate);
      if (!isNaN(parsed.getTime())) return parsed.toLocaleString();
    }

    const docId = doc._id || doc.documentKey?._id;
    if (docId && typeof docId === 'string' && docId.length === 24) {
      try {
        const timestamp = parseInt(docId.substring(0, 8), 16) * 1000;
        return new Date(timestamp).toLocaleString();
      } catch (err) {
        return 'N/A';
      }
    }
    return 'N/A';
  };

  const totalRequests = initialRequestCount || historyDocs.length;
  const okCount = historyDocs.filter(d => extractMetadata(d).overallResult.toUpperCase() === 'OK').length;
  const ngCount = historyDocs.filter(d => ['NG', 'FAIL'].includes(extractMetadata(d).overallResult.toUpperCase())).length;
  const checkCount = historyDocs.filter(d => extractMetadata(d).overallResult.toUpperCase() === 'CHECK').length;
  
  const internalErrors500 = historyDocs.filter(d => JSON.stringify(d).includes('500') || JSON.stringify(d).includes('Internal')).length;
  const avgDailyRequests = totalRequests > 0 ? (totalRequests / 7).toFixed(1) : '0';
  
  const exceptionLogs = historyDocs.map(d => extractMetadata(d).targetName).filter(t => t !== 'N/A');
  const mostViewedException = exceptionLogs.length > 0 
    ? exceptionLogs.sort((a,b) => exceptionLogs.filter(v => v === b).length - exceptionLogs.filter(v => v === a).length)[0]
    : 'Auth Middleware Exception';

  const filteredHistoryDocs = historyDocs.filter((doc) => {
    if (!historySearchQuery.trim()) return true;
    const meta = extractMetadata(doc);
    const basicMatch =
      doc._id?.toLowerCase().includes(historySearchQuery.toLowerCase()) ||
      meta.targetName.toLowerCase().includes(historySearchQuery.toLowerCase()) ||
      meta.devName.toLowerCase().includes(historySearchQuery.toLowerCase()) ||
      meta.initName.toLowerCase().includes(historySearchQuery.toLowerCase());

    if (basicMatch) return true;
    return matchesQuery(doc, historySearchQuery);
  });

  const sortedHistoryDocs = [...filteredHistoryDocs].sort((a, b) => {
    const timeA = new Date(extractTimestamp(a)).getTime();
    const timeB = new Date(extractTimestamp(b)).getTime();
    if (isNaN(timeA) || isNaN(timeB)) return 0;
    return sortOrder === 'latest' ? timeB - timeA : timeA - timeB;
  });

  const totalPages = Math.ceil(sortedHistoryDocs.length / ITEMS_PER_PAGE) || 1;
  const paginatedHistoryDocs = sortedHistoryDocs.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const res = await fetch('/dev_options/api?mode=history&limit=100');
      const data = await res.json();
      setHistoryDocs(data.history || []);
      if (typeof data.total === 'number') {
        setInitialRequestCount(data.total);
      } else {
        setInitialRequestCount(data.history?.length || 0);
      }
    } catch (err) {
      console.error('Failed to load historical documents:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();

    const eventSource = new EventSource('/dev_options/api');
    eventSource.onopen = () => setConnected(true);

    eventSource.addEventListener('init', (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      if (data.totalDocuments !== undefined) {
        setInitialRequestCount(data.totalDocuments);
      }
    });

    eventSource.addEventListener('change', (event: MessageEvent) => {
      try {
        const change: ChangeEvent = JSON.parse(event.data);
        setLiveLogs((prev) => [change, ...prev.slice(0, 99)]);
      } catch (err) {
        console.error('Error parsing live change event:', err);
      }
    });

    eventSource.onerror = (err) => {
      console.error('SSE Connection Error:', err);
      setConnected(false);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const handleSaveJson = () => {
    try {
      const parsed = JSON.parse(editableJsonString);
      setJsonError(null);
      if (activePayload) {
        setActivePayload({ ...activePayload, data: parsed });
      }
      setIsEditMode(false);
      alert('Payload successfully updated in local view!');
    } catch (err: any) {
      setJsonError(err.message || 'Invalid JSON format');
    }
  };

  const handleCopyJson = () => {
    if (activePayload) {
      navigator.clipboard.writeText(JSON.stringify(activePayload.data, null, 2));
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const sidebarWidth = isMaximized ? '750px' : '420px';

  return (
    <div className="min-h-screen bg-[#F4F5F7] text-slate-800 font-sans antialiased flex flex-col p-6 lg:p-10 transition-all" style={{ marginRight: activePayload ? sidebarWidth : '0px' }}>
      
      {/* Top Header & Toggle Panel Button */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Telemetry & Infrastructure Dashboard</h1>
          <p className="text-xs text-slate-500 mt-0.5">Real-time monitoring and historical request analytics console</p>
        </div>
        <button 
          onClick={() => setShowOperatorPanel(!showOperatorPanel)}
          className="bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center space-x-2 shadow-sm transition-all"
        >
          {showOperatorPanel ? <PanelRightClose className="w-4 h-4 text-blue-600" /> : <PanelRightOpen className="w-4 h-4 text-blue-600" />}
          <span>{showOperatorPanel ? 'Hide Operator Panel' : 'Operator Notes & Controls'}</span>
        </button>
      </div>

      {/* Prominent Header Card for Live Request Stream */}
      <div 
        onClick={() => setShowLiveModal(true)}
        className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 mb-6 cursor-pointer hover:border-blue-300 transition-all"
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl border border-blue-100 shadow-sm">
                <Radio className={`w-6 h-6 ${connected ? 'animate-pulse text-emerald-600' : 'text-rose-500'}`} />
              </div>
              <div>
                <div className="flex items-center space-x-3">
                  <h2 className="text-lg md:text-xl font-bold text-slate-900 tracking-tight">Live Requests Stream</h2>
                  <span className={`border text-xs font-semibold px-2.5 py-1 rounded-md flex items-center space-x-1.5 shadow-sm ${connected ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'}`}>
                    <span className={`w-2 h-2 rounded-full animate-pulse ${connected ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
                    <span>{connected ? 'Streaming Active' : 'Disconnected'}</span>
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Real-time MongoDB change stream ingestion pipeline • Committed Buffer: <span className="font-mono font-semibold text-slate-700">{liveLogs.length} events</span>
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button onClick={(e) => { e.stopPropagation(); fetchHistory(); }} className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold px-3.5 py-2.5 rounded-xl flex items-center space-x-1.5 shadow-sm transition-all">
              <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
              <span>Refresh History</span>
            </button>
            <button className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2.5 rounded-xl flex items-center space-x-1.5 shadow-sm shadow-blue-500/20 transition-all">
              <Filter className="w-3.5 h-3.5" />
              <span>Open Stream Modal</span>
            </button>
          </div>
        </div>
      </div>

      {/* ANALYTICS HEADER CARD */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 mb-8">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
            <Activity className="w-4 h-4 text-blue-600" />
            <span>Telemetry & Request Analytics Overview</span>
          </h3>
          <span className="text-xs text-slate-400 font-medium">Real-time Metrics Aggregation</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-center">
          <div className="bg-slate-50 border border-slate-100 p-3 rounded-xl">
            <span className="text-slate-400 block text-[10px] uppercase font-bold mb-1">Total Requests</span>
            <span className="text-lg font-bold text-slate-900">{totalRequests}</span>
          </div>
          <div className="bg-slate-50 border border-slate-100 p-3 rounded-xl">
            <span className="text-slate-400 block text-[10px] uppercase font-bold mb-1">Avg Daily Req</span>
            <span className="text-lg font-bold text-blue-600">{avgDailyRequests}</span>
          </div>
          <div className="bg-slate-50 border border-slate-100 p-3 rounded-xl">
            <span className="text-slate-400 block text-[10px] uppercase font-bold mb-1">500 Errors</span>
            <span className="text-lg font-bold text-rose-600">{internalErrors500}</span>
          </div>
          <div className="bg-emerald-50/50 border border-emerald-100 p-3 rounded-xl">
            <span className="text-emerald-600 block text-[10px] uppercase font-bold mb-1">OK Status</span>
            <span className="text-lg font-bold text-emerald-700">{okCount}</span>
          </div>
          <div className="bg-rose-50/50 border border-rose-100 p-3 rounded-xl">
            <span className="text-rose-600 block text-[10px] uppercase font-bold mb-1">NG / Fail</span>
            <span className="text-lg font-bold text-rose-700">{ngCount}</span>
          </div>
          <div className="bg-amber-50/50 border border-amber-100 p-3 rounded-xl">
            <span className="text-amber-600 block text-[10px] uppercase font-bold mb-1">Check Status</span>
            <span className="text-lg font-bold text-amber-700">{checkCount}</span>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>Most Viewed Exception Log: <strong className="text-slate-800 font-mono">{mostViewedException}</strong></span>
          <span className="text-emerald-600 font-semibold flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Cluster Health Stable</span>
          </span>
        </div>
      </div>

      {/* Main Layout Area: Equal-Height Grid matching container height */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch w-full max-w-7xl mx-auto">
        
        {/* Main Historical Logs Container */}
        <div className={`flex flex-col space-y-6 transition-all duration-300 ${showOperatorPanel ? 'lg:col-span-8' : 'lg:col-span-12'}`}>
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 flex-1 flex flex-col justify-between space-y-6">
            
            <div className="space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <h2 className="text-base font-bold text-slate-800">Previous Requests & Historical Logs</h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Showing <span className="font-semibold text-slate-800">{sortedHistoryDocs.length}</span> matching records out of {totalRequests} total
                  </p>
                </div>

                <div className="flex items-center space-x-2 text-xs">
                  <span className="text-slate-500 font-medium">Sort:</span>
                  <select 
                    value={sortOrder} 
                    onChange={(e) => setSortOrder(e.target.value as 'latest' | 'oldest')}
                    className="bg-slate-50 border border-slate-200 text-slate-700 rounded-lg px-2.5 py-1.5 font-medium outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="latest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                  </select>
                </div>
              </div>

              {/* Master Search Bar */}
              <div className="relative">
                <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                <input 
                  type="text"
                  placeholder='Master Search (e.g. "Region" : "SCA", targetName, ID)...'
                  value={historySearchQuery}
                  onChange={(e) => {
                    setHistorySearchQuery(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="w-full bg-slate-50 text-slate-800 text-xs pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              {/* Historical Records Grid List */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {loadingHistory ? (
                  <div className="col-span-2 text-center py-12 text-slate-400 text-xs">Loading existing database records...</div>
                ) : paginatedHistoryDocs.length === 0 ? (
                  <div className="col-span-2 text-center py-12 text-slate-400 text-xs">No matching previous records found.</div>
                ) : (
                  paginatedHistoryDocs.map((doc) => {
                    const timestampStr = extractTimestamp(doc);
                    const meta = extractMetadata(doc);

                    return (
                      <div 
                        key={doc._id}
                        onClick={() => setActivePayload({ title: `Historical Record [${doc._id}]`, data: doc })}
                        className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:border-blue-300 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between gap-3"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="font-mono text-xs font-bold text-slate-900">{doc._id}</span>
                            <span className="text-slate-300">•</span>
                            <span className="text-xs text-slate-400 flex items-center space-x-1">
                              <Clock className="w-3 h-3" />
                              <span>{timestampStr}</span>
                            </span>
                          </div>
                          <span className="text-xs font-semibold text-blue-600 flex items-center space-x-1">
                            <span>View</span>
                            <span>➔</span>
                          </span>
                        </div>

                        <div className="flex flex-wrap items-center gap-1.5 text-xs">
                          <span className="bg-slate-200/70 text-slate-700 px-2 py-0.5 rounded font-medium text-[11px]">
                            Target: <strong className="text-slate-900">{meta.targetName}</strong>
                          </span>
                          <span className="bg-slate-200/70 text-slate-700 px-2 py-0.5 rounded font-medium text-[11px]">
                            Dev: <strong className="text-slate-900">{meta.devName}</strong>
                          </span>
                          {renderStatusBadge(meta.overallResult)}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Pagination Footer */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between pt-4 border-t border-slate-100 text-xs">
                <button
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                  className={`px-3 py-1.5 rounded-lg border font-semibold ${currentPage === 1 ? 'bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'}`}
                >
                  ◀ Previous
                </button>
                <span className="font-semibold text-slate-600">Page {currentPage} of {totalPages}</span>
                <button
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                  className={`px-3 py-1.5 rounded-lg border font-semibold ${currentPage === totalPages ? 'bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'}`}
                >
                  Next ▶
                </button>
              </div>
            )}

          </div>

          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-3">
            <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
              <Shield className="w-4 h-4 text-blue-600" />
              <span>Environment Governance & Security Policy</span>
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              All inbound telemetry is scanned against strict PCI-DSS and HIPAA data masking rules. PII tokens are salted and hashed upon ingestion. Retention policies dictate permanent archive to cold storage after 90 days.
            </p>
          </div>
        </div>

        {/* Operator Panel Sidebar (Matches the main container height using flex) */}
        {showOperatorPanel && (
          <div className="lg:col-span-4 flex flex-col space-y-6 transition-all duration-300">
            
            {/* Operator Notes Card */}
            <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4 flex-1 flex flex-col justify-start">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-800">Operator Notes</h3>
                <button 
                  onClick={() => setIsEditingNotes(!isEditingNotes)}
                  className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                >
                  <Edit3 className="w-3.5 h-3.5" />
                  <span>{isEditingNotes ? 'Save Note' : 'Edit Notes'}</span>
                </button>
              </div>

              {isEditingNotes ? (
                <textarea 
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full text-xs text-slate-700 p-3 rounded-xl border border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 bg-blue-50/30 flex-1 min-h-[140px]"
                ></textarea>
              ) : (
                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100 text-xs text-slate-600 leading-relaxed font-medium">
                  {notes}
                </div>
              )}
            </div>

            {/* Stream Activity Overview Card */}
            <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="text-sm font-bold text-slate-800">Stream Activity Overview</h3>
                <span className="text-xs bg-emerald-50 text-emerald-600 font-semibold px-2 py-0.5 rounded-full border border-emerald-100">
                  {liveLogs.length} Buffered
                </span>
              </div>
              <div className="space-y-3 text-xs text-slate-600">
                <div className="flex justify-between items-center bg-slate-50 p-2.5 rounded-lg">
                  <span className="font-medium">Connection State</span>
                  <span className={`font-bold ${connected ? 'text-emerald-600' : 'text-rose-500'}`}>{connected ? 'Connected (SSE)' : 'Disconnected'}</span>
                </div>
                <div className="flex justify-between items-center bg-slate-50 p-2.5 rounded-lg">
                  <span className="font-medium">Total Database Records</span>
                  <span className="font-bold text-slate-800">{totalRequests}</span>
                </div>
              </div>
            </div>

          </div>
        )}

      </div>

      {/* LIVE STREAM OVERLAY MODAL */}
      {showLiveModal && (
        <div className="fixed inset-0 bg-slate-900/75 backdrop-blur-sm flex justify-center items-center z-[2000] p-6 box-border">
          <div className="bg-white rounded-2xl w-full max-w-5xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="p-5 border-b border-slate-200 flex justify-between items-center bg-slate-50">
              <div className="flex items-center space-x-3">
                <span className={`w-3 h-3 rounded-full ${connected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
                <h2 className="text-base font-bold text-slate-900">Live Requests Stream Activity</h2>
                <span className="text-xs bg-slate-200 px-2.5 py-0.5 rounded-md font-semibold text-slate-700">{liveLogs.length} Committed</span>
              </div>
              <button onClick={() => setShowLiveModal(false)} className="text-slate-400 hover:text-slate-700 text-lg font-bold">✕</button>
            </div>

            <div className="p-6 overflow-y-auto flex-1">
              {liveLogs.length === 0 ? (
                <div className="text-center py-16 text-slate-400 text-sm">Listening for live database change stream triggers...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-left text-xs">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold">
                        <th className="p-3">ID</th>
                        <th className="p-3">Timestamp</th>
                        <th className="p-3">Target Name</th>
                        <th className="p-3">Dev Name</th>
                        <th className="p-3">Init Name</th>
                        <th className="p-3">Result</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {liveLogs.map((log, index) => {
                        const docId = log.documentKey?._id || log.fullDocument?._id || 'N/A';
                        const timestamp = extractTimestamp(log);
                        const meta = extractMetadata(log);

                        return (
                          <tr 
                            key={index}
                            onClick={() => setActivePayload({ title: `Live Trigger [${log.operationType.toUpperCase()}]`, data: log.fullDocument || log })}
                            className="hover:bg-slate-50 cursor-pointer transition-colors"
                          >
                            <td className="p-3 font-mono font-medium text-slate-800">{docId}</td>
                            <td className="p-3 text-slate-500 whitespace-nowrap">{timestamp}</td>
                            <td className="p-3 font-semibold text-slate-800">{meta.targetName}</td>
                            <td className="p-3 font-semibold text-slate-800">{meta.devName}</td>
                            <td className="p-3 font-semibold text-slate-800">{meta.initName}</td>
                            <td className="p-3">{renderStatusBadge(meta.overallResult)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
              <button onClick={() => setShowLiveModal(false)} className="bg-slate-900 text-white text-xs font-semibold px-4 py-2 rounded-xl">Close Modal</button>
            </div>
          </div>
        </div>
      )}

      {/* RIGHT SIDEBAR PAYLOAD VIEWER (MongoGUI Style) */}
      <div 
        className="fixed top-0 right-0 h-screen bg-[#0f172a] text-slate-100 shadow-2xl flex flex-col z-[3000] transition-all duration-300"
        style={{ width: sidebarWidth, right: activePayload ? '0px' : `-${sidebarWidth}` }}
      >
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-[#1e293b]">
          <h3 className="text-sm font-bold text-sky-400 truncate max-w-[240px]">{activePayload?.title}</h3>
          <div className="flex items-center space-x-1">
            <button onClick={handleCopyJson} title="Copy JSON" className="p-1.5 text-slate-400 hover:text-white rounded">
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            </button>
            <button onClick={() => setIsMinimized(!isMinimized)} title={isMinimized ? 'Expand' : 'Minimize'} className="p-1.5 text-slate-400 hover:text-white text-xs">
              {isMinimized ? '🔼' : '🔽'}
            </button>
            <button onClick={() => setIsMaximized(!isMaximized)} title={isMaximized ? 'Restore Width' : 'Maximize Width'} className="p-1.5 text-slate-400 hover:text-white text-xs">
              {isMaximized ? '🗗' : '🗖'}
            </button>
            <button onClick={() => { setActivePayload(null); setSidebarSearchQuery(''); setIsEditMode(false); setIsMaximized(false); }} className="p-1.5 text-slate-400 hover:text-white text-base">✕</button>
          </div>
        </div>

        {!isMinimized && (
          <>
            <div className="p-3 border-b border-slate-800 bg-[#0f172a] flex items-center gap-2">
              <input 
                type="text"
                placeholder="Filter keys/values in payload..."
                value={sidebarSearchQuery}
                onChange={(e) => setSidebarSearchQuery(e.target.value)}
                disabled={isEditMode}
                className="flex-1 bg-slate-900 border border-slate-700 text-xs px-3 py-1.5 rounded-lg text-slate-100 outline-none focus:ring-1 focus:ring-sky-500"
              />
              <button 
                onClick={() => { setIsEditMode(!isEditMode); setJsonError(null); }}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${isEditMode ? 'bg-amber-500 text-slate-950' : 'bg-slate-800 text-slate-200 hover:bg-slate-700'}`}
              >
                {isEditMode ? 'View Mode' : 'Edit JSON'}
              </button>
            </div>

            {jsonError && (
              <div className="p-2.5 bg-rose-950 text-rose-300 text-xs border-b border-rose-900">
                ⚠️ <b>JSON Error:</b> {jsonError}
              </div>
            )}

            <div className="flex-1 p-4 overflow-y-auto">
              {isEditMode ? (
                <div className="flex flex-col h-full gap-3">
                  <textarea 
                    value={editableJsonString}
                    onChange={(e) => setEditableJsonString(e.target.value)}
                    className="flex-1 w-full min-h-[400px] bg-slate-950 text-sky-400 font-mono text-xs p-3 rounded-lg border border-slate-700 outline-none resize-none"
                  />
                  <button onClick={handleSaveJson} className="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold py-2 rounded-lg text-xs">
                    Save Payload Changes
                  </button>
                </div>
              ) : (
                <JsonTreeNode value={activePayload?.data ?? {}} searchQuery={sidebarSearchQuery} />
              )}
            </div>
          </>
        )}
      </div>

    </div>
  );
}