// src/app/dev_options/history/page.tsx
'use client';

import { useEffect, useState } from 'react';

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

export default function HistoryPage() {
  // Column 1: Live Stream States
  const [liveLogs, setLiveLogs] = useState<ChangeEvent[]>([]);
  const [connected, setConnected] = useState(false);

  // Column 2: Historical / Previous Requests States
  const [historyDocs, setHistoryDocs] = useState<HistoricalDoc[]>([]);
  const [initialRequestCount, setInitialRequestCount] = useState<number>(0);
  const [loadingHistory, setLoadingHistory] = useState(true);
  
  // Sorting & Search States for Column 2
  const [sortOrder, setSortOrder] = useState<'latest' | 'oldest'>('latest');
  const [historySearchQuery, setHistorySearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  // Active Payload & Right Sidebar States
  const [activePayload, setActivePayload] = useState<{ title: string; data: any } | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Extract metadata safely from document
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

  // Helper to render color badge for overall status
  const renderStatusBadge = (status: string) => {
    let bgColor = '#cbd5e1';
    let textColor = '#0f172a';

    if (status.toUpperCase() === 'OK') {
      bgColor = '#dcfce7';
      textColor = '#166534';
    } else if (status.toUpperCase() === 'CHECK') {
      bgColor = '#fef3c7';
      textColor = '#92400e';
    } else if (status.toUpperCase() === 'NG' || status.toUpperCase() === 'FAIL') {
      bgColor = '#fee2e2';
      textColor = '#991b1b';
    }

    return (
      <span
        style={{
          padding: '2px 8px',
          backgroundColor: bgColor,
          color: textColor,
          borderRadius: '4px',
          fontWeight: 'bold',
          fontSize: '11px',
          border: '1px solid rgba(0,0,0,0.05)',
        }}
      >
        📊 Result: {status}
      </span>
    );
  };

  // Extract date/time from document _id or date fields
  const extractTimestamp = (doc: HistoricalDoc): string => {
    const rawDate = doc.createdAt || doc.updatedAt || doc.timestamp;
    if (rawDate) {
      return new Date(rawDate).toLocaleString();
    }

    if (doc._id && typeof doc._id === 'string' && doc._id.length === 24) {
      try {
        const timestamp = parseInt(doc._id.substring(0, 8), 16) * 1000;
        return new Date(timestamp).toLocaleString();
      } catch (err) {
        return 'N/A';
      }
    }

    return 'N/A';
  };

  // 1. Filter documents by Search Query (ID, Target, Dev, Init Names)
  const filteredHistoryDocs = historyDocs.filter((doc) => {
    if (!historySearchQuery.trim()) return true;
    const query = historySearchQuery.toLowerCase();
    const meta = extractMetadata(doc);

    return (
      doc._id?.toLowerCase().includes(query) ||
      meta.targetName.toLowerCase().includes(query) ||
      meta.devName.toLowerCase().includes(query) ||
      meta.initName.toLowerCase().includes(query)
    );
  });

  // 2. Sort filtered documents
  const sortedHistoryDocs = [...filteredHistoryDocs].sort((a, b) => {
    const timeA = new Date(extractTimestamp(a)).getTime();
    const timeB = new Date(extractTimestamp(b)).getTime();

    if (isNaN(timeA) || isNaN(timeB)) return 0;

    return sortOrder === 'latest' ? timeB - timeA : timeA - timeB;
  });

  // 3. Paginate sorted documents (15 items per page)
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
        setLiveLogs((prev) => [change, ...prev.slice(0, 49)]);
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

  const formatAndFilterPayload = (data: any) => {
    const rawJson = JSON.stringify(data, null, 2);
    if (!searchQuery.trim()) return rawJson;

    const lines = rawJson.split('\n');
    return lines
      .filter((line) => line.toLowerCase().includes(searchQuery.toLowerCase()))
      .join('\n');
  };

  return (
    <div style={{ display: 'flex', width: '100%', minHeight: '100vh', overflowX: 'hidden' }}>
      
      {/* MAIN CONTAINER */}
      <div
        style={{
          flex: 1,
          padding: '24px',
          fontFamily: 'sans-serif',
          transition: 'margin-right 0.3s ease',
          marginRight: activePayload ? '400px' : '0px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h1 style={{ margin: 0 }}>Database Monitoring Dashboard</h1>
          <button
            onClick={fetchHistory}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              backgroundColor: '#0f172a',
              color: '#ffffff',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            🔄 Refresh Previous Requests
          </button>
        </div>

        {/* Two-Column Side-by-Side Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          
          {/* COLUMN 1: LIVE ACTIVITY */}
          <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '16px', backgroundColor: '#ffffff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h2 style={{ fontSize: '18px', margin: 0 }}>🔴 Live Requests Stream</h2>
                <small style={{ color: '#64748b' }}>Real-time Trigger Activity</small>
              </div>
              <span
                style={{
                  padding: '4px 10px',
                  fontSize: '12px',
                  borderRadius: '12px',
                  backgroundColor: connected ? '#dcfce7' : '#fee2e2',
                  color: connected ? '#166534' : '#991b1b',
                  fontWeight: 'bold',
                }}
              >
                {connected ? '● Live Connected' : '○ Disconnected'}
              </span>
            </div>

            {liveLogs.length === 0 ? (
              <p style={{ color: '#94a3b8' }}>Listening for live triggers...</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {liveLogs.map((log, index) => {
                  const docId = log.documentKey?._id || 'N/A';
                  const meta = extractMetadata(log);
                  return (
                    <div
                      key={index}
                      onClick={() =>
                        setActivePayload({
                          title: `Live Trigger [${log.operationType.toUpperCase()}]`,
                          data: log.fullDocument || log,
                        })
                      }
                      style={{
                        padding: '12px',
                        backgroundColor: '#f8fafc',
                        borderRadius: '6px',
                        border: '1px solid #cbd5e1',
                        cursor: 'pointer',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '6px',
                        transition: 'background-color 0.15s ease',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f1f5f9')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#f8fafc')}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>
                          <strong style={{ textTransform: 'uppercase' }}>[{log.operationType}]</strong> - ID:{' '}
                          <code>{docId}</code>
                        </span>
                        <small style={{ color: '#2563eb' }}>View ➔</small>
                      </div>

                      <div style={{ display: 'flex', gap: '8px', fontSize: '11px', flexWrap: 'wrap', alignItems: 'center' }}>
                        <span style={{ padding: '2px 6px', backgroundColor: '#e2e8f0', borderRadius: '4px' }}>
                          🎯 Target: <b>{meta.targetName}</b>
                        </span>
                        <span style={{ padding: '2px 6px', backgroundColor: '#e2e8f0', borderRadius: '4px' }}>
                          💻 Dev: <b>{meta.devName}</b>
                        </span>
                        <span style={{ padding: '2px 6px', backgroundColor: '#e2e8f0', borderRadius: '4px' }}>
                          🚀 Init: <b>{meta.initName}</b>
                        </span>
                        {renderStatusBadge(meta.overallResult)}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* COLUMN 2: PREVIOUS / HISTORICAL REQUESTS */}
          <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '16px', backgroundColor: '#ffffff', display: 'flex', flexDirection: 'column' }}>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div>
                <h2 style={{ fontSize: '18px', margin: 0 }}>📜 Previous Requests & IDs</h2>
                <small style={{ color: '#64748b' }}>Showing {sortedHistoryDocs.length} matching requests</small>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '12px', color: '#64748b', display: 'block' }}>Initial Total Requests</span>
                <span
                  style={{
                    display: 'inline-block',
                    backgroundColor: '#f1f5f9',
                    color: '#0f172a',
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontWeight: 'bold',
                    fontSize: '14px',
                    border: '1px solid #cbd5e1',
                  }}
                >
                  {initialRequestCount} Requests
                </span>
              </div>
            </div>

            {/* NEW: Search Bar Container */}
            <div style={{ marginBottom: '8px' }}>
              <input
                type="text"
                placeholder="🔍 Search by ID, Target, Dev, or Init Name..."
                value={historySearchQuery}
                onChange={(e) => {
                  setHistorySearchQuery(e.target.value);
                  setCurrentPage(1); // Reset to page 1 on search
                }}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid #cbd5e1',
                  fontSize: '13px',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            {/* Sorting Container */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '8px 12px',
                backgroundColor: '#f8fafc',
                borderRadius: '6px',
                border: '1px solid #e2e8f0',
                marginBottom: '12px',
              }}
            >
              <span style={{ fontSize: '12px', color: '#475569', fontWeight: 600 }}>Sort By Timestamp:</span>
              <select
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value as 'latest' | 'oldest')}
                style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  border: '1px solid #cbd5e1',
                  fontSize: '12px',
                  backgroundColor: '#ffffff',
                  color: '#0f172a',
                  cursor: 'pointer',
                }}
              >
                <option value="latest">⬇️ Newest / Latest First</option>
                <option value="oldest">⬆️ Oldest First</option>
              </select>
            </div>

            {/* List Body */}
            <div style={{ flex: 1 }}>
              {loadingHistory ? (
                <p style={{ color: '#94a3b8' }}>Loading existing database records...</p>
              ) : paginatedHistoryDocs.length === 0 ? (
                <p style={{ color: '#94a3b8' }}>No matching previous records found.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {paginatedHistoryDocs.map((doc) => {
                    const timestampStr = extractTimestamp(doc);
                    const meta = extractMetadata(doc);

                    return (
                      <div
                        key={doc._id}
                        onClick={() =>
                          setActivePayload({
                            title: `Historical Record [${doc._id}]`,
                            data: doc,
                          })
                        }
                        style={{
                          padding: '12px',
                          backgroundColor: '#f1f5f9',
                          borderRadius: '6px',
                          border: '1px solid #cbd5e1',
                          cursor: 'pointer',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '6px',
                          transition: 'background-color 0.15s ease',
                        }}
                        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#e2e8f0')}
                        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#f1f5f9')}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                            <span>
                              <strong>ID:</strong> <code>{doc._id}</code>
                            </span>
                            <small style={{ color: '#64748b', fontSize: '11px' }}>
                              🕒 {timestampStr}
                            </small>
                          </div>
                          <small style={{ color: '#2563eb' }}>View Payload ➔</small>
                        </div>

                        <div style={{ display: 'flex', gap: '8px', fontSize: '11px', flexWrap: 'wrap', alignItems: 'center' }}>
                          <span style={{ padding: '2px 6px', backgroundColor: '#cbd5e1', borderRadius: '4px', color: '#0f172a' }}>
                            🎯 Target: <b>{meta.targetName}</b>
                          </span>
                          <span style={{ padding: '2px 6px', backgroundColor: '#cbd5e1', borderRadius: '4px', color: '#0f172a' }}>
                            💻 Dev: <b>{meta.devName}</b>
                          </span>
                          <span style={{ padding: '2px 6px', backgroundColor: '#cbd5e1', borderRadius: '4px', color: '#0f172a' }}>
                            🚀 Init: <b>{meta.initName}</b>
                          </span>
                          {renderStatusBadge(meta.overallResult)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* NEW: Pagination Control Footer */}
            {totalPages > 1 && (
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginTop: '16px',
                  paddingTop: '12px',
                  borderTop: '1px solid #e2e8f0',
                }}
              >
                <button
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '4px',
                    border: '1px solid #cbd5e1',
                    backgroundColor: currentPage === 1 ? '#f1f5f9' : '#ffffff',
                    color: currentPage === 1 ? '#94a3b8' : '#0f172a',
                    cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                    fontSize: '12px',
                  }}
                >
                  ◀ Previous
                </button>

                <span style={{ fontSize: '12px', color: '#475569', fontWeight: 600 }}>
                  Page {currentPage} of {totalPages}
                </span>

                <button
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '4px',
                    border: '1px solid #cbd5e1',
                    backgroundColor: currentPage === totalPages ? '#f1f5f9' : '#ffffff',
                    color: currentPage === totalPages ? '#94a3b8' : '#0f172a',
                    cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                    fontSize: '12px',
                  }}
                >
                  Next ▶
                </button>
              </div>
            )}

          </div>

        </div>
      </div>

      {/* RIGHT SIDEBAR */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          right: activePayload ? 0 : '-400px',
          width: '400px',
          height: '100vh',
          backgroundColor: '#0f172a',
          color: '#f8fafc',
          boxShadow: '-4px 0 16px rgba(0,0,0,0.2)',
          transition: 'right 0.3s ease',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 1000,
        }}
      >
        <div
          style={{
            padding: '16px',
            borderBottom: '1px solid #334155',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <h3 style={{ margin: 0, fontSize: '16px', color: '#38bdf8' }}>{activePayload?.title}</h3>
          <button
            onClick={() => {
              setActivePayload(null);
              setSearchQuery('');
            }}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              fontSize: '20px',
              cursor: 'pointer',
            }}
          >
            ✕
          </button>
        </div>

        <div style={{ padding: '16px', borderBottom: '1px solid #334155', backgroundColor: '#1e293b' }}>
          <input
            type="text"
            placeholder="🔍 Search keys or values in payload..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: '6px',
              border: '1px solid #475569',
              backgroundColor: '#0f172a',
              color: '#f8fafc',
              fontSize: '13px',
              outline: 'none',
            }}
          />
        </div>

        <div style={{ flex: 1, padding: '16px', overflowY: 'auto' }}>
          <pre
            style={{
              margin: 0,
              fontSize: '12px',
              fontFamily: 'monospace',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all',
              color: '#e2e8f0',
            }}
          >
            {activePayload ? formatAndFilterPayload(activePayload.data) : ''}
          </pre>
        </div>
      </div>

    </div>
  );
}