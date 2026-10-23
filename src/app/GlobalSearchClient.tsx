'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  ChevronDown,
  Search,
  Compass,
  Video,
  Settings,
  HelpCircle,
  Sparkles,
  Edit3,
  Copy,
  FolderInput,
  Download,
  Trash2,
  Clock,
  ArrowUp,
  UserCheck,
  Package,
  Check,
  Bookmark,
  ChevronRight,
  Folder,
  Bot,
  BrainCircuit,
  Paperclip,
  UploadCloud,
  User,
  RotateCcw,
  ThumbsUp,
  ThumbsDown,
  Table as TableIcon,
  Filter,
  MoreHorizontal,
  FileText,
  ExternalLink,
  Plus,
  FileSearch,
  X,
  Boxes,
  Layers
} from 'lucide-react';

interface RecentSearch {
  id: string;
  title: string;
  timestamp: string;
}

interface PresetOption {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ElementType;
  badge?: string;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  files?: { name: string; size?: string }[];
  preset?: string;
  timestamp: string;
}

interface TableRecord {
  id: string;
  name: string;
  type: string;
  agent: string;
  status: 'Completed' | 'Processing' | 'Failed';
  date: string;
  size: string;
}

interface BomSpec {
  id: string;
  bomNumber: string;
  title: string;
  revision: string;
  componentsCount: number;
  status: 'Approved' | 'In Review' | 'Draft';
  lastUpdated: string;
}

const PRESET_OPTIONS: PresetOption[] = [
  {
    id: 'bom-assistant',
    title: 'BOM Assistant',
    subtitle: 'Autonomous intelligent agents for BOM Management and Automation',
    icon: Bot
  },
  {
    id: 'bom-validation',
    title: 'BOM Validation',
    subtitle: 'Place lifelike avatars in videos',
    icon: UserCheck,
    badge: 'Pro'
  },
  {
    id: 'bom-change-eco',
    title: 'BOM Change ECO',
    subtitle: 'Create a custom agent for brand',
    icon: Video,
    badge: 'Beta'
  },
  {
    id: 'bom-operation-agent',
    title: 'BOM Operation Agent',
    subtitle: 'Show products handled on screen',
    icon: Package
  }
];

const INITIAL_RECENT_SEARCHES: RecentSearch[] = [
  { id: '1', title: 'B-roll market footage', timestamp: '2 hours ago' },
  { id: '2', title: 'My old project pitch', timestamp: 'Yesterday' },
  { id: '3', title: 'Cyberpunk neon street cinematic', timestamp: '3 days ago' },
  { id: '4', title: 'Product demo avatar script', timestamp: '1 week ago' }
];

const INITIAL_TABLE_RECORDS: TableRecord[] = [
  {
    id: 'REC-101',
    name: 'Cyberpunk Neon Market Script.docx',
    type: 'Script',
    agent: 'AI Agents',
    status: 'Completed',
    date: 'Oct 09, 2026',
    size: '1.2 MB'
  },
  {
    id: 'REC-102',
    name: 'Futuristic Puddle Reflection Shot.mp4',
    type: 'Video',
    agent: 'Video Agent',
    status: 'Processing',
    date: 'Oct 09, 2026',
    size: '48.5 MB'
  },
  {
    id: 'REC-103',
    name: 'Avatar Voice Pitch Deep Analysis.pdf',
    type: 'Report',
    agent: 'Deep Analysis',
    status: 'Completed',
    date: 'Oct 08, 2026',
    size: '3.4 MB'
  },
  {
    id: 'REC-104',
    name: 'Brand Product Handheld Preview.mov',
    type: 'Video',
    agent: 'Product in Hand',
    status: 'Completed',
    date: 'Oct 07, 2026',
    size: '112 MB'
  },
  {
    id: 'REC-105',
    name: 'Tokyo Night Scene B-roll Prompt.txt',
    type: 'Prompt Data',
    agent: 'AI Agents',
    status: 'Failed',
    date: 'Oct 05, 2026',
    size: '42 KB'
  }
];

const SAMPLE_BOM_DATA: BomSpec[] = [
  { id: 'bom-1', bomNumber: 'BOM-2026-001', title: 'Main Control Unit (MCU) PCB Assembly', revision: 'v2.4', componentsCount: 142, status: 'Approved', lastUpdated: '2 hours ago' },
  { id: 'bom-2', bomNumber: 'BOM-2026-042', title: 'Power Distribution Harness & Relays', revision: 'v1.1', componentsCount: 38, status: 'In Review', lastUpdated: '1 day ago' },
  { id: 'bom-3', bomNumber: 'BOM-2026-089', title: 'Sensor Hub Array Subsystem', revision: 'v3.0', componentsCount: 86, status: 'Approved', lastUpdated: 'Oct 14, 2026' },
  { id: 'bom-4', bomNumber: 'BOM-2026-104', title: 'Telemetry & Communication Module', revision: 'v0.8', componentsCount: 54, status: 'Draft', lastUpdated: 'Oct 10, 2026' },
  { id: 'bom-5', bomNumber: 'BOM-2026-118', title: 'Chassis Structural Enclosure & Fasteners', revision: 'v1.5', componentsCount: 210, status: 'Approved', lastUpdated: 'Oct 02, 2026' }
];

export default function GlobalSearchClient() {
  // Left sidebar hidden by default
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [rightPanelOpen, setRightPanelOpen] = useState<boolean>(true);
  const [isProjectMenuOpen, setIsProjectMenuOpen] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>(INITIAL_RECENT_SEARCHES);
  
  // Table state
  const [tableFilter, setTableFilter] = useState('');
  const [records, setRecords] = useState<TableRecord[]>(INITIAL_TABLE_RECORDS);

  // Chat and Prompt bar states
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [promptText, setPromptText] = useState('');
  const [isPresetPopoverOpen, setIsPresetPopoverOpen] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<PresetOption>(PRESET_OPTIONS[0]);
  const [isAiWriterActive, setIsAiWriterActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  // BOM Search Panel State
  const [showBomSearchPanel, setShowBomSearchPanel] = useState(false);
  const [bomSearchQuery, setBomSearchQuery] = useState('');

  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Menu Refs for click outside
  const projectMenuRef = useRef<HTMLDivElement>(null);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const presetPopoverRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (projectMenuRef.current && !projectMenuRef.current.contains(event.target as Node)) {
        setIsProjectMenuOpen(false);
      }
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target as Node)) {
        setIsSearchFocused(false);
      }
      if (presetPopoverRef.current && !presetPopoverRef.current.contains(event.target as Node)) {
        setIsPresetPopoverOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Auto-scroll to bottom on new chat bubble
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setRecentSearches(prev => [
        { id: Date.now().toString(), title: searchQuery, timestamp: 'Just now' },
        ...prev.filter(item => item.title.toLowerCase() !== searchQuery.toLowerCase())
      ]);
      setIsSearchFocused(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setUploadedFiles(prev => [...prev, ...Array.from(e.target.files || [])]);
    }
  };

  const handlePromptSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!promptText.trim() && uploadedFiles.length === 0) return;

    const userMessageText = promptText.trim();
    const currentFiles = uploadedFiles.map(f => ({ name: f.name, size: `${(f.size / 1024).toFixed(1)} KB` }));
    const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // 1. Append User Message Bubble
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: userMessageText,
      files: currentFiles.length > 0 ? currentFiles : undefined,
      preset: selectedPreset.title,
      timestamp: nowTime
    };

    setMessages(prev => [...prev, userMsg]);
    setPromptText('');
    setUploadedFiles([]);
    setIsThinking(true);

    // Insert record entry to table
    if (userMessageText) {
      const newRec: TableRecord = {
        id: `REC-${Math.floor(100 + Math.random() * 900)}`,
        name: userMessageText.length > 25 ? userMessageText.substring(0, 25) + '...' : userMessageText,
        type: 'Query Log',
        agent: selectedPreset.title,
        status: 'Completed',
        date: 'Just now',
        size: '12 KB'
      };
      setRecords(prev => [newRec, ...prev]);

      setRecentSearches(prev => [
        { id: Date.now().toString(), title: userMessageText, timestamp: 'Just now' },
        ...prev.filter(item => item.title.toLowerCase() !== userMessageText.toLowerCase())
      ]);
    }

    // 2. Simulate AI Agents responding
    setTimeout(() => {
      const responses = [
        `I've processed your query using the **${selectedPreset.title}** module. Here are key insights regarding your request: "_${userMessageText}_". I can generate concept drafts or perform deep analysis whenever you are ready!`,
        `Analyzing query with **${selectedPreset.title}**... Your request "${userMessageText}" has been queued. I recommend exploring the Video Agent tools to bring this idea to full production.`,
        `Got it! I am running a rapid simulation for "${userMessageText}". Let me know if you would like me to adjust the visual tone, script details, or attach extra scene references.`
      ];
      
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];

      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        sender: 'assistant',
        text: randomResponse,
        preset: selectedPreset.title,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, aiMsg]);
      setIsThinking(false);
    }, 1200);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handlePromptSubmit();
    }
  };

  const filteredTableRecords = records.filter(rec =>
    rec.name.toLowerCase().includes(tableFilter.toLowerCase()) ||
    rec.type.toLowerCase().includes(tableFilter.toLowerCase()) ||
    rec.agent.toLowerCase().includes(tableFilter.toLowerCase())
  );

  const filteredBoms = SAMPLE_BOM_DATA.filter(bom =>
    bom.bomNumber.toLowerCase().includes(bomSearchQuery.toLowerCase()) ||
    bom.title.toLowerCase().includes(bomSearchQuery.toLowerCase()) ||
    bom.revision.toLowerCase().includes(bomSearchQuery.toLowerCase())
  );

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Roboto:wght@500;700;900&display=swap');

        .font-title {
          font-family: 'Roboto', sans-serif;
        }

        .font-body {
          font-family: 'Montserrat', sans-serif;
        }

        .custom-scrollbar::-webkit-scrollbar {
          width: 5px;
          height: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(226, 232, 240, 0.8);
          border-radius: 9999px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(203, 213, 225, 1);
        }
      `}</style>

      <div className="relative flex h-screen w-full overflow-hidden bg-slate-50 text-slate-800 font-body antialiased selection:bg-red-500 selection:text-white">
        
        {/* Dynamic Background Mesh Gradient */}
        <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden">
          <div className="absolute -top-32 -left-32 h-[500px] w-[500px] rounded-full bg-gradient-to-tr from-red-200/40 via-red-100/30 to-transparent blur-3xl transition-all duration-1000 ease-in-out" />
          <div className="absolute -bottom-40 -right-40 h-[600px] w-[600px] rounded-full bg-gradient-to-br from-red-100/50 via-rose-50/40 to-slate-100/20 blur-3xl" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/80 via-rose-50/20 to-slate-100/50" />
        </div>

        {/* Left Sidebar - Hidden by default */}
        <aside
          className={`relative z-20 flex flex-col border-r border-slate-200/80 bg-white/80 backdrop-blur-xl transition-all duration-300 ease-in-out ${
            sidebarOpen ? 'w-64 min-w-[16rem]' : 'w-0 min-w-0 border-r-0 overflow-hidden'
          }`}
        >
          <div className="flex h-full flex-col p-4 w-64">
            {/* Sidebar Toggle Control at Top */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider font-title">Navigation</span>
              <button
                onClick={() => setSidebarOpen(false)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors"
                title="Hide Sidebar"
              >
                <PanelLeftClose className="h-5 w-5" />
              </button>
            </div>

            {/* Quick Nav Links */}
            <div className="mt-4 space-y-1">
              <a href="#" className="flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition-colors">
                <Check className="h-4 w-4 text-slate-400" />
                Completed routes
              </a>
              <a href="#" className="flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition-colors">
                <Bookmark className="h-4 w-4 text-slate-400" />
                Favorites
              </a>
            </div>

            {/* Explore Section */}
            <div className="mt-6">
              <p className="px-3 text-[11px] font-bold tracking-wider text-slate-400 uppercase font-title">Explore</p>
              <nav className="mt-2 space-y-1">
                <a href="#" className="flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-slate-700 hover:bg-red-50 hover:text-red-600 transition-colors group">
                  <Compass className="h-4 w-4 text-slate-400 group-hover:text-red-500" />
                  Tutorials
                </a>
                <a href="#" className="flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-slate-700 hover:bg-red-50 hover:text-red-600 transition-colors group">
                  <Video className="h-4 w-4 text-slate-400 group-hover:text-red-500" />
                  Video Agent
                </a>
              </nav>
            </div>

            {/* System Navigation */}
            <div className="mt-6">
              <nav className="space-y-1">
                <a href="#" className="flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100/80 transition-colors">
                  <Settings className="h-4 w-4 text-slate-400" />
                  Settings
                </a>
                <a href="#" className="flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100/80 transition-colors">
                  <HelpCircle className="h-4 w-4 text-slate-400" />
                  Get support
                </a>
              </nav>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="relative z-10 flex flex-1 flex-col h-full overflow-hidden">
          
          {/* Top Header */}
          <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200/60 bg-white/60 px-6 backdrop-blur-md">
            <div className="flex items-center gap-3">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="rounded-lg border border-slate-200 p-2 text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors shadow-sm"
                  title="Expand Sidebar"
                >
                  <PanelLeftOpen className="h-4 w-4 text-red-600" />
                </button>
              )}

              {/* Breadcrumb / Project Switcher Dropdown */}
              <div className="relative" ref={projectMenuRef}>
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <Folder className="h-4 w-4 text-red-500 fill-red-50" />
                  <span className="font-medium text-slate-500 font-title">Cool folder</span>
                  <ChevronRight className="h-3.5 w-3.5 text-slate-300" />
                  <button
                    onClick={() => setIsProjectMenuOpen(!isProjectMenuOpen)}
                    className="flex items-center gap-1.5 font-bold text-slate-900 hover:text-red-600 rounded-lg px-2 py-1 hover:bg-slate-100/70 transition-colors font-title"
                  >
                    My first project
                    <ChevronDown className={`h-3.5 w-3.5 text-slate-400 transition-transform ${isProjectMenuOpen ? 'rotate-180' : ''}`} />
                  </button>
                </div>

                {/* Project Options Dropdown Menu */}
                {isProjectMenuOpen && (
                  <div className="absolute left-0 top-full mt-2 w-56 rounded-2xl border border-slate-200/80 bg-white/95 p-1.5 shadow-2xl backdrop-blur-xl z-50">
                    <button className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100 transition-colors">
                      <Edit3 className="h-4 w-4 text-slate-400" />
                      Rename project
                    </button>
                    <button className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100 transition-colors">
                      <Copy className="h-4 w-4 text-slate-400" />
                      Duplicate
                    </button>
                    <button className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100 transition-colors">
                      <FolderInput className="h-4 w-4 text-slate-400" />
                      Move to
                    </button>
                    <button className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100 transition-colors">
                      <Download className="h-4 w-4 text-slate-400" />
                      Download
                    </button>
                    <div className="my-1 border-t border-slate-100" />
                    <button className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-red-600 hover:bg-red-50 transition-colors">
                      <Trash2 className="h-4 w-4 text-red-500" />
                      Delete
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Top Right Controls & Keyword Search */}
            <div className="flex items-center gap-3">
              <div className="relative" ref={searchContainerRef}>
                <form onSubmit={handleSearchSubmit} className="relative flex items-center">
                  <Search className="absolute left-3 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Keyword"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onFocus={() => setIsSearchFocused(true)}
                    className="w-44 sm:w-60 rounded-full border border-slate-200 bg-slate-50/80 py-1.5 pl-9 pr-4 text-xs font-medium text-slate-800 placeholder-slate-400 focus:border-red-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-100 transition-all shadow-inner"
                  />
                </form>

                {/* Recent Searches Dropdown Popover */}
                {isSearchFocused && (
                  <div className="absolute right-0 top-full mt-2 w-72 rounded-2xl border border-slate-200/90 bg-white/95 p-3 shadow-2xl backdrop-blur-xl z-50">
                    <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
                      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider font-title">Recent</span>
                      <button
                        onClick={() => setRecentSearches([])}
                        className="text-[10px] text-red-500 hover:underline font-medium"
                      >
                        Clear all
                      </button>
                    </div>
                    {recentSearches.length > 0 ? (
                      <div className="space-y-1">
                        {recentSearches.map((item) => (
                          <button
                            key={item.id}
                            onClick={() => {
                              setPromptText(item.title);
                              setIsSearchFocused(false);
                            }}
                            className="flex w-full items-center justify-between rounded-xl px-2.5 py-2 text-left text-xs text-slate-700 hover:bg-red-50/70 hover:text-red-600 transition-colors group"
                          >
                            <div className="flex items-center gap-2.5 truncate">
                              <Clock className="h-3.5 w-3.5 text-slate-400 group-hover:text-red-500" />
                              <span className="truncate">{item.title}</span>
                            </div>
                            <span className="text-[10px] text-slate-300 group-hover:text-red-400">{item.timestamp}</span>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="py-4 text-center text-xs text-slate-400">No recent searches</p>
                    )}
                  </div>
                )}
              </div>

              {/* Button to toggle Full Right Panel */}
              <button
                onClick={() => setRightPanelOpen(!rightPanelOpen)}
                className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold transition-all shadow-sm ${
                  rightPanelOpen
                    ? 'border-red-500 bg-red-50 text-red-600 ring-2 ring-red-100'
                    : 'border-slate-200 bg-white text-slate-700 hover:border-red-200 hover:text-red-600'
                }`}
                title="Toggle Table List Panel"
              >
                <TableIcon className="h-4 w-4 text-red-500" />
                <span className="hidden sm:inline font-title">Table Records</span>
              </button>
            </div>
          </header>

          {/* 2-Column Main Layout */}
          <div className="relative flex flex-1 overflow-hidden">
            
            {/* Column 1: Left-Aligned Chat Container */}
            <div className="relative flex flex-1 flex-col h-full overflow-hidden transition-all duration-300 ease-in-out">
              
              {/* Scrollable Chat Area */}
              <div className="flex-1 overflow-y-auto px-6 pt-6 pb-44 custom-scrollbar">
                
                {/* BOM Search Floating Panel Container */}
                {showBomSearchPanel && (
                  <div className="mb-6 w-full max-w-xl rounded-2xl border border-red-200 bg-white/95 p-4 shadow-xl backdrop-blur-md animate-in fade-in slide-in-from-top-4 duration-200">
                    <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                      <div className="flex items-center gap-2">
                        <Boxes className="h-4 w-4 text-red-600" />
                        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-title">
                          BOM Specification Reference
                        </h3>
                      </div>
                      <button
                        onClick={() => setShowBomSearchPanel(false)}
                        className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>

                    {/* BOM Search Bar */}
                    <div className="relative mt-3">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
                      <input
                        type="text"
                        placeholder="Search by BOM #, Component title, or Revision..."
                        value={bomSearchQuery}
                        onChange={(e) => setBomSearchQuery(e.target.value)}
                        className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-xs font-medium text-slate-800 placeholder-slate-400 focus:border-red-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-100"
                      />
                    </div>

                    {/* Results List */}
                    <div className="mt-3 max-h-56 overflow-y-auto space-y-2 custom-scrollbar pr-1">
                      {filteredBoms.length > 0 ? (
                        filteredBoms.map((bom) => (
                          <div
                            key={bom.id}
                            className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50/60 p-2.5 hover:bg-red-50/50 hover:border-red-200 transition-all group"
                          >
                            <div className="min-w-0 pr-2">
                              <div className="flex items-center gap-2">
                                <span className="rounded bg-red-100 px-1.5 py-0.5 text-[10px] font-bold text-red-600 font-title">
                                  {bom.bomNumber}
                                </span>
                                <span className="text-xs font-bold text-slate-800 truncate font-title group-hover:text-red-600 transition-colors">
                                  {bom.title}
                                </span>
                              </div>
                              <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-1">
                                <span>Rev: {bom.revision}</span>
                                <span>•</span>
                                <span>{bom.componentsCount} Parts</span>
                                <span>•</span>
                                <span>{bom.lastUpdated}</span>
                              </div>
                            </div>
                            <button
                              onClick={() => {
                                setPromptText(`Reference Spec: [${bom.bomNumber}] ${bom.title} (${bom.revision})`);
                                setShowBomSearchPanel(false);
                              }}
                              className="shrink-0 rounded-lg bg-white border border-slate-200 px-2.5 py-1 text-[11px] font-semibold text-slate-700 shadow-sm hover:border-red-300 hover:text-red-600 transition-all font-title"
                            >
                              Insert Reference
                            </button>
                          </div>
                        ))
                      ) : (
                        <p className="py-4 text-center text-xs text-slate-400">No matching BOM specifications found.</p>
                      )}
                    </div>
                  </div>
                )}

                {messages.length === 0 ? (
                  /* Hero View */
                  <div className="flex h-full flex-col justify-center text-left py-12 max-w-xl">
                    <div className="space-y-3">
                      <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 font-title">
                        BOM Engineering Workspace
                      </h1>
                      <p className="text-sm text-slate-500 font-medium leading-relaxed">
                        Query engineering assets, review component ECOs, or search BOM structures using AI agents.
                      </p>
                    </div>
                  </div>
                ) : (
                  /* Chat Bubbles Left-Aligned Layout */
                  <div className="w-full max-w-2xl space-y-6">
                    {messages.map((msg) => (
                      <div
                        key={msg.id}
                        className={`flex flex-col ${
                          msg.sender === 'user' ? 'items-end' : 'items-start'
                        }`}
                      >
                        {/* User / AI Header */}
                        <div className="flex items-center gap-2 mb-1 px-1 text-[11px] font-medium text-slate-400">
                          {msg.sender === 'user' ? (
                            <>
                              <span>{msg.timestamp}</span>
                              <span className="font-bold text-slate-700 font-title">You</span>
                              <div className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-900 text-white">
                                <User className="h-3 w-3" />
                              </div>
                            </>
                          ) : (
                            <>
                              <div className="flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-white">
                                <Bot className="h-3 w-3" />
                              </div>
                              <span className="font-bold text-red-600 font-title">{msg.preset || 'AI Agent'}</span>
                              <span>• {msg.timestamp}</span>
                            </>
                          )}
                        </div>

                        {/* Speech Bubble */}
                        <div
                          className={`relative max-w-[90%] sm:max-w-[85%] rounded-3xl px-5 py-3.5 shadow-sm transition-all ${
                            msg.sender === 'user'
                              ? 'bg-gradient-to-r from-red-600 to-rose-600 text-white rounded-tr-sm shadow-red-500/10'
                              : 'bg-white border border-slate-200/90 text-slate-800 rounded-tl-sm shadow-slate-200/50'
                          }`}
                        >
                          {/* Attached File Badges */}
                          {msg.files && msg.files.length > 0 && (
                            <div className="mb-2 flex flex-wrap gap-1.5 border-b border-white/20 pb-2">
                              {msg.files.map((file, fIdx) => (
                                <span
                                  key={fIdx}
                                  className="inline-flex items-center gap-1 rounded-lg bg-black/10 px-2 py-0.5 text-xs font-medium text-white/90"
                                >
                                  <Paperclip className="h-3 w-3" />
                                  {file.name}
                                </span>
                              ))}
                            </div>
                          )}

                          <p className="text-sm font-medium leading-relaxed whitespace-pre-wrap font-body">
                            {msg.text}
                          </p>

                          {/* AI Action Toolbar */}
                          {msg.sender === 'assistant' && (
                            <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-2 text-xs text-slate-400">
                              <div className="flex items-center gap-2">
                                <button className="hover:text-red-600 transition-colors p-1" title="Thumbs up">
                                  <ThumbsUp className="h-3.5 w-3.5" />
                                </button>
                                <button className="hover:text-red-600 transition-colors p-1" title="Thumbs down">
                                  <ThumbsDown className="h-3.5 w-3.5" />
                                </button>
                                <button className="hover:text-red-600 transition-colors p-1" title="Regenerate">
                                  <RotateCcw className="h-3.5 w-3.5" />
                                </button>
                              </div>
                              <span className="text-[10px] text-slate-300 font-title">AI Agents v2.4</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}

                    {/* AI Thinking Indicator */}
                    {isThinking && (
                      <div className="flex flex-col items-start">
                        <div className="flex items-center gap-2 mb-1 px-1 text-[11px] font-medium text-slate-400">
                          <div className="flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-white animate-pulse">
                            <Bot className="h-3 w-3" />
                          </div>
                          <span className="font-bold text-red-600 font-title">{selectedPreset.title}</span>
                          <span>is thinking...</span>
                        </div>
                        <div className="flex items-center gap-1.5 rounded-2xl bg-white border border-slate-200 px-4 py-3 shadow-sm rounded-tl-sm">
                          <span className="h-2 w-2 rounded-full bg-red-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                          <span className="h-2 w-2 rounded-full bg-red-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                          <span className="h-2 w-2 rounded-full bg-red-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                      </div>
                    )}

                    <div ref={chatBottomRef} />
                  </div>
                )}
              </div>

              {/* Left-Aligned Prompt Input Bar */}
              <div className="absolute bottom-6 left-6 right-6 max-w-2xl z-30">
                <form onSubmit={handlePromptSubmit} className="relative rounded-3xl border border-slate-200/90 bg-white/95 p-4 shadow-2xl backdrop-blur-2xl ring-1 ring-slate-900/5">
                  
                  {/* Uploaded Files Preview Chips */}
                  {uploadedFiles.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-2 px-1">
                      {uploadedFiles.map((file, index) => (
                        <div key={index} className="flex items-center gap-1.5 rounded-lg bg-red-50 px-2.5 py-1 text-xs font-medium text-red-600 border border-red-100">
                          <Paperclip className="h-3.5 w-3.5 text-red-500" />
                          <span className="truncate max-w-[150px]">{file.name}</span>
                          <button
                            type="button"
                            onClick={() => setUploadedFiles(prev => prev.filter((_, i) => i !== index))}
                            className="ml-1 text-red-400 hover:text-red-700 font-bold"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Input Textarea */}
                  <div className="relative flex items-center">
                    <textarea
                      rows={2}
                      value={promptText}
                      onChange={(e) => setPromptText(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="What is the status of My BOMs?"
                      className="w-full resize-none bg-transparent px-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none font-body"
                    />
                  </div>

                  {/* Hidden File Input */}
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    className="hidden"
                    multiple
                  />

                  {/* Bottom Controls Bar */}
                  <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3">
                    <div className="flex flex-wrap items-center gap-2">
                      
                      {/* File Upload Button */}
                      <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50/80 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-white hover:text-red-600 hover:border-red-200 transition-all shadow-sm"
                        title="Upload files"
                      >
                        <UploadCloud className="h-4 w-4 text-red-500" />
                        <span>Attach</span>
                      </button>

                      {/* Preset Selector Popover */}
                      <div className="relative" ref={presetPopoverRef}>
                        <button
                          type="button"
                          onClick={() => setIsPresetPopoverOpen(!isPresetPopoverOpen)}
                          className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50/80 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:border-red-300 hover:bg-white hover:text-red-600 transition-all shadow-sm"
                        >
                          <selectedPreset.icon className="h-4 w-4 text-red-500" />
                          <span className="font-title">{selectedPreset.title}</span>
                          <ChevronDown className={`h-3.5 w-3.5 text-slate-400 transition-transform ${isPresetPopoverOpen ? 'rotate-180' : ''}`} />
                        </button>

                        {isPresetPopoverOpen && (
                          <div className="absolute bottom-full left-0 mb-2 w-72 rounded-2xl border border-slate-200/90 bg-white p-2 shadow-2xl backdrop-blur-xl z-50">
                            <div className="space-y-1">
                              {PRESET_OPTIONS.map((option) => {
                                const IconComp = option.icon;
                                const isSelected = option.id === selectedPreset.id;
                                return (
                                  <button
                                    key={option.id}
                                    type="button"
                                    onClick={() => {
                                      setSelectedPreset(option);
                                      setIsPresetPopoverOpen(false);
                                    }}
                                    className={`flex w-full items-start gap-3 rounded-xl p-2.5 text-left transition-all ${
                                      isSelected
                                        ? 'bg-red-50/80 border border-red-200/80'
                                        : 'hover:bg-slate-50'
                                    }`}
                                  >
                                    <div className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${
                                      isSelected ? 'bg-red-500 text-white' : 'bg-slate-100 text-slate-500'
                                    }`}>
                                      <IconComp className="h-4 w-4" />
                                    </div>
                                    <div className="flex-1">
                                      <div className="flex items-center justify-between">
                                        <span className={`text-xs font-bold font-title ${isSelected ? 'text-red-600' : 'text-slate-800'}`}>
                                          {option.title}
                                        </span>
                                        {option.badge && (
                                          <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[9px] font-semibold text-slate-500">
                                            {option.badge}
                                          </span>
                                        )}
                                      </div>
                                      <p className="text-[11px] text-slate-400 leading-tight mt-0.5 font-body">
                                        {option.subtitle}
                                      </p>
                                    </div>
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Deep Analysis Button */}
                      <button
                        type="button"
                        className="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50/80 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-white hover:text-slate-900 transition-colors shadow-sm"
                      >
                        <BrainCircuit className="h-3.5 w-3.5 text-red-500" />
                        <span>Deep Analysis</span>
                      </button>

                      {/* Get BOM Button */}
                      <button
                        type="button"
                        onClick={() => setShowBomSearchPanel(!showBomSearchPanel)}
                        className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold transition-all shadow-sm ${
                          showBomSearchPanel
                            ? 'border-red-500 bg-red-50 text-red-600 ring-2 ring-red-100'
                            : 'border-slate-200 bg-slate-50/80 text-slate-700 hover:bg-white hover:border-red-200 hover:text-red-600'
                        }`}
                      >
                        <FileSearch className="h-3.5 w-3.5 text-red-500" />
                        <span className="font-title">Get BOM</span>
                      </button>
                    </div>

                    {/* AI Writer & Submit Controls */}
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => setIsAiWriterActive(!isAiWriterActive)}
                        className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold transition-all shadow-sm ${
                          isAiWriterActive
                            ? 'border-red-500 bg-red-50 text-red-600'
                            : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-white'
                        }`}
                      >
                        <Sparkles className={`h-3.5 w-3.5 ${isAiWriterActive ? 'text-red-500' : 'text-slate-400'}`} />
                        <span>AI Writer</span>
                      </button>

                      <button
                        type="submit"
                        disabled={!promptText.trim() && uploadedFiles.length === 0}
                        className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-white shadow-md hover:bg-red-600 disabled:opacity-40 disabled:hover:bg-slate-900 transition-all active:scale-95"
                        title="Submit Prompt (Enter)"
                      >
                        <ArrowUp className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </form>
              </div>

            </div>

            {/* Column 2: Extended Full-Panel Right Sidebar */}
            <aside
              className={`relative z-20 flex flex-col border-l border-slate-200/80 bg-white/90 backdrop-blur-xl transition-all duration-300 ease-in-out ${
                rightPanelOpen ? 'w-full md:w-1/2 lg:w-3/5 min-w-[22rem]' : 'w-0 min-w-0 border-l-0 overflow-hidden'
              }`}
            >
              <div className="flex h-full w-full flex-col overflow-hidden">
                
                {/* Right Panel Header */}
                <div className="flex shrink-0 items-center justify-between p-4 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <TableIcon className="h-4 w-4 text-red-600" />
                    <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-title">
                      Project Asset & BOM Records
                    </h2>
                    <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-600 font-title">
                      {records.length}
                    </span>
                  </div>
                  <button
                    onClick={() => setRightPanelOpen(false)}
                    className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors"
                    title="Close Table Panel"
                  >
                    <PanelRightClose className="h-4 w-4" />
                  </button>
                </div>

                {/* Table Filter Controls */}
                <div className="flex items-center justify-between gap-2 p-3 border-b border-slate-100 bg-slate-50/50">
                  <div className="relative flex-1">
                    <Filter className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Filter records..."
                      value={tableFilter}
                      onChange={(e) => setTableFilter(e.target.value)}
                      className="w-full rounded-xl border border-slate-200 bg-white py-1.5 pl-8 pr-3 text-xs font-medium text-slate-700 placeholder-slate-400 focus:border-red-400 focus:outline-none focus:ring-1 focus:ring-red-100"
                    />
                  </div>
                  <button
                    onClick={() => {
                      const newSample: TableRecord = {
                        id: `REC-${Math.floor(100 + Math.random() * 900)}`,
                        name: `Manual Record Entry #${records.length + 1}`,
                        type: 'Asset',
                        agent: 'AI Agents',
                        status: 'Completed',
                        date: 'Just now',
                        size: '2.1 MB'
                      };
                      setRecords([newSample, ...records]);
                    }}
                    className="flex items-center gap-1 rounded-xl bg-slate-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-600 transition-colors shrink-0"
                    title="Add Entry"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    <span>Add Entry</span>
                  </button>
                </div>

                {/* Extended Table Data List */}
                <div className="flex-1 overflow-y-auto custom-scrollbar p-3">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase tracking-wider font-title">
                        <th className="pb-2 pt-1 px-3">Name / Specification Details</th>
                        <th className="pb-2 pt-1 px-3">Type</th>
                        <th className="pb-2 pt-1 px-3">Status</th>
                        <th className="pb-2 pt-1 px-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {filteredTableRecords.map((record) => (
                        <tr
                          key={record.id}
                          className="group hover:bg-red-50/40 transition-colors"
                        >
                          <td className="py-3 px-3">
                            <div className="flex items-start gap-2.5">
                              <FileText className="h-4 w-4 shrink-0 text-red-500 mt-0.5" />
                              <div className="min-w-0">
                                <p className="text-xs font-bold text-slate-800 truncate group-hover:text-red-600 transition-colors font-title">
                                  {record.name}
                                </p>
                                <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-0.5">
                                  <span>{record.agent}</span>
                                  <span>•</span>
                                  <span>{record.date}</span>
                                  <span>•</span>
                                  <span>{record.size}</span>
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="py-3 px-3 text-xs font-medium text-slate-600">
                            {record.type}
                          </td>
                          <td className="py-3 px-3 shrink-0 align-top">
                            <span
                              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                                record.status === 'Completed'
                                  ? 'bg-emerald-50 text-emerald-600 border border-emerald-200/60'
                                  : record.status === 'Processing'
                                  ? 'bg-amber-50 text-amber-600 border border-amber-200/60 animate-pulse'
                                  : 'bg-rose-50 text-rose-600 border border-rose-200/60'
                              }`}
                            >
                              {record.status}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-right align-top shrink-0">
                            <div className="flex items-center justify-end gap-1">
                              <button
                                onClick={() => {
                                  setPromptText(`Inspect asset record: ${record.name}`);
                                }}
                                className="rounded p-1 text-slate-400 hover:bg-white hover:text-red-600 transition-colors"
                                title="Use in prompt"
                              >
                                <ExternalLink className="h-3.5 w-3.5" />
                              </button>
                              <button
                                onClick={() => {
                                  setRecords(records.filter(r => r.id !== record.id));
                                }}
                                className="rounded p-1 text-slate-400 hover:bg-white hover:text-red-600 transition-colors"
                                title="Remove entry"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {filteredTableRecords.length === 0 && (
                    <div className="py-12 text-center text-xs text-slate-400">
                      No matching records found.
                    </div>
                  )}
                </div>

                {/* Right Panel Footer */}
                <div className="border-t border-slate-100 p-3 bg-slate-50/50 text-[11px] text-slate-400 flex items-center justify-between font-title">
                  <span>Showing {filteredTableRecords.length} records</span>
                  <button
                    onClick={() => setRecords(INITIAL_TABLE_RECORDS)}
                    className="text-red-500 hover:underline font-medium"
                  >
                    Reset List
                  </button>
                </div>

              </div>
            </aside>

          </div>

        </main>
      </div>
    </>
  );
}