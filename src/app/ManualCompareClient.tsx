'use client';

import React, { useState, useRef } from 'react';
import { 
  GitCompare, 
  Search, 
  Plus, 
  Minus, 
  Trash2, 
  Play, 
  Layers, 
  RefreshCw, 
  Sliders, 
  Layers3, 
  Check, 
  ChevronLeft, 
  ChevronRight, 
  FolderDown, 
  Workflow, 
  List, 
  Rows, 
  LayoutGrid, 
  AlertTriangle,
  Clock,
  Table,
  CheckCircle2,
  FileSpreadsheet,
  Upload,
  Eye,
  EyeOff,
  X,
  ExternalLink,
  FileText,
  Sparkles,
  ChevronDown
} from 'lucide-react';

/* ============================================================================
   TYPES & INTERFACES
   ============================================================================ */

interface TargetModelItem {
  id: string;
  value: string;
  isSearching: boolean;
  status?: 'idle' | 'loading' | 'success' | 'error';
}

interface ExecutionLogItem {
  stage: string;
  status: string;
  time?: string;
  elapsed?: number;
  thread?: string;
  error?: string;
}

interface ApiSingleOutput {
  status: string;
  message: string;
  report?: any;
  version: number | string;
  mp_mode: string;
  get_result: string;
  all_result: {
    overallResult?: string;
    [key: string]: any;
  };
  exceptionLog: ExecutionLogItem[];
}

interface IndividualState {
  targetModels: TargetModelItem[];
  devModel: string;
  initModel: string;
  isSearchingDev: boolean;
  isSearchingInit: boolean;
  isCrosschecking: boolean;
  latestResults: ApiSingleOutput[];
}

interface MappingRow {
  id: string;
  targetModel: string;
  devModel: string;
  initModel: string;
  isTargetValid?: boolean;
  isDevValid?: boolean;
  isInitValid?: boolean;
  status?: 'idle' | 'loading' | 'success' | 'error';
  lastProcessedTime?: string;
}

interface TableRowData {
  id: string;
  mp: string;
  init: string;
  dev: string;
  version: string | number;
  timestamp: string;
  result: 'OK' | 'NG' | 'PENDING';
  allResult?: Record<string, any>;
  exceptionLogs?: ExecutionLogItem[];
  confirmation: string;
  priority: string;
  note: string;
}

type ViewModuleOption = 
  | 'structure'
  | 'ben compare'
  | 'substitute'
  | 'hw option'
  | 'HW part check'
  | 'MPS Check'
  | 'operation plan'
  | 'tool option'
  | 'substitute check';

function getCookie(name: string): string {
  if (typeof document === 'undefined') return '';
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || '';
  return '';
}

/**
 * Defensive JSON Fetcher that isolates HTTP 500/HTML responses gracefully
 */
async function safeFetchJson(url: string, options: RequestInit, retries = 1): Promise<any> {
  let response: Response;
  try {
    response = await fetch(url, options);
  } catch (netErr: any) {
    if (retries > 0) {
      await new Promise(res => setTimeout(res, 500));
      return safeFetchJson(url, options, retries - 1);
    }
    throw new Error(`Network Connection Error: ${netErr?.message || 'Server unreachable'}`);
  }

  if (!response.ok) {
    if (retries > 0 && response.status === 500) {
      await new Promise(res => setTimeout(res, 500));
      return safeFetchJson(url, options, retries - 1);
    }
    const errBody = await response.json().catch(() => ({}));
    throw new Error(errBody.detail?.message || errBody.detail || `Server returned status ${response.status}`);
  }

  return response.json();
}

const INITIAL_TABLE_ROWS: TableRowData[] = [
  { 
    id: 'row-1', 
    mp: 'insert model here', 
    init: 'insert model here', 
    dev: 'insert model here',
    version: 7.0,
    timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19),
    result: 'NG', 
    allResult: { overallResult: 'NG', operationPlan: 'NG', buildBOM: 'OK', targetMatch: 'CHECK' },
    exceptionLogs: [
      { stage: 'Operation Plan Check', status: 'NG', time: '14:22:01', error: 'Mismatched part number in sub-module' }
    ],
    confirmation: 'Requires Review', 
    priority: 'High', 
    note: 'Operation Plan mismatched' 
  }
];

const INITIAL_MAPPING_ROWS: MappingRow[] = [
  {
    id: 'map-1',
    targetModel: '85QNED74BSA.KWMFLJR',
    devModel: '85QNED74BSA.AWZFLCX',
    initModel: '85QNED70BSA.AWZFLCX',
    isTargetValid: true,
    isDevValid: true,
    isInitValid: true,
    status: 'idle'
  },
  {
    id: 'map-2',
    targetModel: '65NU7000PUA.SUSFLJR',
    devModel: '65NU8508PUA.DEVFLJR',
    initModel: '65NU8508PUA.BASEFLCX',
    isTargetValid: true,
    isDevValid: true,
    isInitValid: true,
    status: 'idle'
  }
];

const AUTO_SEARCH_TARGET_POOL = ['85QNED74BSA.KWMFLJR', '65NU7000PUA.AWZFLCX', '65NU8508PUA.KUSFLJR', 'QNED85.2026', 'OLED65C4PUA.AWZFLCX'];
const MODEL_FORMAT_REGEX = /^[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+$/;

const validateModelFormat = (val: string): boolean => {
  if (!val || !val.trim()) return true;
  return MODEL_FORMAT_REGEX.test(val.trim());
};

export default function ModelCrosscheckDashboard() {
  const [activeTab, setActiveTab] = useState<'individual' | 'multi'>('individual');
  const [multiSubView, setMultiSubView] = useState<'mapping' | 'pipeline'>('mapping');
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [tableRows, setTableRows] = useState<TableRowData[]>(INITIAL_TABLE_ROWS);
  const [resultViewLayout, setResultViewLayout] = useState<'table-row' | 'column-row' | 'grid'>('table-row');
  const [selectedRow, setSelectedRow] = useState<TableRowData | null>(null);
  const [showMappingContent, setShowMappingContent] = useState<boolean>(true);

  const [searchQuery, setSearchQuery] = useState<string>('');
  const [mappingSearchQuery, setMappingSearchQuery] = useState<string>('');
  const [individualSearchQuery, setIndividualSearchQuery] = useState<string>('');
  const [resultFilter, setResultFilter] = useState<string>('ALL');

  const [highlightDifferent, setHighlightDifferent] = useState<boolean>(false);
  const [selectedViewModule, setSelectedViewModule] = useState<ViewModuleOption>('structure');

  const [mappingRows, setMappingRows] = useState<MappingRow[]>(INITIAL_MAPPING_ROWS);
  const [isMultiCrosschecking, setIsMultiCrosschecking] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const formatModelInput = (val: string): string => {
    if (val.includes('@')) {
      return val.split('@')[0].trim();
    }
    return val;
  };

  const [individual, setIndividual] = useState<IndividualState>({
    targetModels: [
      { id: 't-1', value: 'Insert Model Here', isSearching: false, status: 'idle' },
      { id: 't-2', value: 'Insert Model Here', isSearching: false, status: 'idle' }
    ],
    devModel: '85QNED74BSA.AWZFLCX',
    initModel: '85QNED70BSA.AWZFLCX',
    isSearchingDev: false,
    isSearchingInit: false,
    isCrosschecking: false,
    latestResults: []
  });

  const handleIndividualTargetChange = (id: string, val: string) => {
    setIndividual(prev => ({
      ...prev,
      targetModels: prev.targetModels.map(item => item.id === id ? { ...item, value: val } : item)
    }));
  };

  const handleIndividualTargetBlur = (id: string, val: string) => {
    const formatted = formatModelInput(val);
    setIndividual(prev => ({
      ...prev,
      targetModels: prev.targetModels.map(item => item.id === id ? { ...item, value: formatted } : item)
    }));
  };

  const addIndividualTargetRow = (afterId: string) => {
    setIndividual(prev => {
      const index = prev.targetModels.findIndex(item => item.id === afterId);
      const newTarget: TargetModelItem = {
        id: `t-${Date.now()}-${Math.random().toString().slice(-4)}`,
        value: '',
        isSearching: false,
        status: 'idle'
      };
      const updated = [...prev.targetModels];
      updated.splice(index + 1, 0, newTarget);
      return { ...prev, targetModels: updated };
    });
  };

  const removeIndividualTargetRow = (id: string) => {
    setIndividual(prev => {
      if (prev.targetModels.length <= 1) {
        return {
          ...prev,
          targetModels: [{ id: `t-${Date.now()}`, value: '', isSearching: false, status: 'idle' }]
        };
      }
      return {
        ...prev,
        targetModels: prev.targetModels.filter(item => item.id !== id)
      };
    });
  };

  const removeAllIndividualTargets = () => {
    setIndividual(prev => ({
      ...prev,
      targetModels: [{ id: `t-${Date.now()}`, value: '', isSearching: false, status: 'idle' }]
    }));
  };

  const handleIndividualAutoSearchTarget = (id: string) => {
    setIndividual(prev => ({
      ...prev,
      targetModels: prev.targetModels.map(item => item.id === id ? { ...item, isSearching: true } : item)
    }));

    setTimeout(() => {
      const randomFind = AUTO_SEARCH_TARGET_POOL[Math.floor(Math.random() * AUTO_SEARCH_TARGET_POOL.length)];
      setIndividual(prev => ({
        ...prev,
        targetModels: prev.targetModels.map(item => item.id === id ? { ...item, value: randomFind, isSearching: false } : item)
      }));
    }, 600);
  };

  const handleIndividualParamSearch = () => {
    if (!individualSearchQuery.trim()) return;
    
    setIndividual(prev => {
      const hasEmpty = prev.targetModels.some(t => !t.value.trim());
      if (hasEmpty) {
        return {
          ...prev,
          targetModels: prev.targetModels.map((t, idx) => 
            idx === 0 && !t.value ? { ...t, value: individualSearchQuery.trim() } : t
          )
        };
      }
      return {
        ...prev,
        targetModels: [...prev.targetModels, { id: `t-${Date.now()}`, value: individualSearchQuery.trim(), isSearching: false, status: 'idle' }]
      };
    });
  };

  const handleMappingRowChange = (id: string, field: keyof MappingRow, val: string) => {
    const isValid = validateModelFormat(val);
    setMappingRows(prev => prev.map(row => {
      if (row.id !== id) return row;
      const updated = { ...row, [field]: val };
      if (field === 'targetModel') updated.isTargetValid = isValid;
      if (field === 'devModel') updated.isDevValid = isValid;
      if (field === 'initModel') updated.isInitValid = isValid;
      return updated;
    }));
  };

  const addMappingRow = () => {
    const newRow: MappingRow = {
      id: `map-${Date.now()}-${Math.random().toString().slice(-4)}`,
      targetModel: '',
      devModel: '',
      initModel: '',
      isTargetValid: true,
      isDevValid: true,
      isInitValid: true,
      status: 'idle'
    };
    setMappingRows(prev => [...prev, newRow]);
  };

  const removeMappingRow = (id: string) => {
    setMappingRows(prev => {
      if (prev.length <= 1) {
        return [{ id: `map-${Date.now()}`, targetModel: '', devModel: '', initModel: '', isTargetValid: true, isDevValid: true, isInitValid: true, status: 'idle' }];
      }
      return prev.filter(row => row.id !== id);
    });
  };

  const parseCSVText = (text: string): { target: string; dev: string; init: string }[] => {
    const lines = text.split(/\r\n|\n/).filter(line => line.trim() !== '');
    if (lines.length < 2) return [];

    const parseCSVLine = (line: string): string[] => {
      const result: string[] = [];
      let current = '';
      let inQuotes = false;
      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
          inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
          result.push(current.trim());
          current = '';
        } else {
          current += char;
        }
      }
      result.push(current.trim());
      return result;
    };

    const headers = parseCSVLine(lines[0]).map(h => h.toLowerCase().replace(/['"]/g, ''));
    let targetIdx = headers.findIndex(h => h.includes('target'));
    let devIdx = headers.findIndex(h => h.includes('dev') || h.includes('development'));
    let initIdx = headers.findIndex(h => h.includes('init') || h.includes('initial'));

    if (targetIdx === -1) targetIdx = 0;
    if (devIdx === -1) devIdx = 1;
    if (initIdx === -1) initIdx = 2;

    const parsedData: { target: string; dev: string; init: string }[] = [];

    for (let i = 1; i < lines.length; i++) {
      const columns = parseCSVLine(lines[i]);
      if (columns.length === 0) continue;
      parsedData.push({
        target: columns[targetIdx] || '',
        dev: columns[devIdx] || '',
        init: columns[initIdx] || ''
      });
    }

    return parsedData;
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const fileName = file.name.toLowerCase();

    try {
      let parsedRows: { target: string; dev: string; init: string }[] = [];

      if (fileName.endsWith('.csv')) {
        const text = await file.text();
        parsedRows = parseCSVText(text);
      } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
        const XLSX = await import('xlsx');
        const arrayBuffer = await file.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: 'array' });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        const jsonData = XLSX.utils.sheet_to_json<Record<string, any>>(worksheet, { header: 1 });

        if (jsonData.length > 1) {
          const headers = (jsonData[0] as any[]).map(h => String(h || '').toLowerCase().trim());
          let targetIdx = headers.findIndex(h => h.includes('target'));
          let devIdx = headers.findIndex(h => h.includes('dev') || h.includes('development'));
          let initIdx = headers.findIndex(h => h.includes('init') || h.includes('initial'));

          if (targetIdx === -1) targetIdx = 0;
          if (devIdx === -1) devIdx = 1;
          if (initIdx === -1) initIdx = 2;

          for (let i = 1; i < jsonData.length; i++) {
            const rowData = jsonData[i] as any[];
            if (!rowData || rowData.length === 0) continue;
            parsedRows.push({
              target: String(rowData[targetIdx] || '').trim(),
              dev: String(rowData[devIdx] || '').trim(),
              init: String(rowData[initIdx] || '').trim()
            });
          }
        }
      } else {
        alert('Unsupported file type. Please upload a .csv, .xlsx, or .xls file.');
        return;
      }

      if (parsedRows.length === 0) {
        alert('No data rows found in the uploaded file.');
        return;
      }

      const newMappingRows: MappingRow[] = parsedRows.map((item, index) => {
        const isTargetValValid = validateModelFormat(item.target);
        const isDevValValid = validateModelFormat(item.dev);
        const isInitValValid = validateModelFormat(item.init);

        return {
          id: `file-map-${Date.now()}-${index}`,
          targetModel: isTargetValValid ? item.target : '',
          devModel: isDevValValid ? item.dev : '',
          initModel: isInitValValid ? item.init : '',
          isTargetValid: isTargetValValid,
          isDevValid: isDevValValid,
          isInitValid: isInitValValid,
          status: 'idle'
        };
      });

      setMappingRows(newMappingRows);

    } catch (err) {
      console.error('Error parsing uploaded file:', err);
      alert('Failed to parse the file. Ensure it is a valid Excel or CSV file.');
    } finally {
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  /* ============================================================================
     FAULT-TOLERANT SEQUENTIAL API RETEST ENGINES
     ============================================================================ */

const runSequentialRetest = async () => {
    const validTargets = individual.targetModels.filter(t => t.value.trim() !== '');
    if (validTargets.length === 0) {
      alert('Please enter at least one target model.');
      return;
    }

    const ssolgenet_cookie = getCookie('ssolgenet');
    const smsession_cookie = getCookie('SMSESSION');

    setIndividual(prev => ({ ...prev, isCrosschecking: true, latestResults: [] }));
    
    // Reset table rows at the start of crosschecking
    let accumulatedRows: TableRowData[] = [];

    for (const targetItem of validTargets) {
      setIndividual(prev => ({
        ...prev,
        targetModels: prev.targetModels.map(item => 
          item.id === targetItem.id ? { ...item, status: 'loading' } : item
        )
      }));

      const payload = {
        ssolgenet_cookie,
        smsession_cookie,
        targetModel: formatModelInput(targetItem.value),
        devModel: formatModelInput(individual.devModel),
        initModel: formatModelInput(individual.initModel)
      };

      try {
        const data = await safeFetchJson('/api/bom/retest_manual', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const apiResult: ApiSingleOutput = (data.results && data.results[0]) ? data.results[0] : {
          status: data.status || 'success',
          message: data.message || 'Retest finished',
          version: data.version ?? 1.0,
          mp_mode: data.report?.mp_model || payload.targetModel,
          get_result: data.get_result || 'NG',
          all_result: data.all_result || {},
          exceptionLog: data.execitionLog || data.exceptionLog || []
        };

        const isSuccess = apiResult.status === 'success' && apiResult.get_result !== 'NG';

        setIndividual(prev => ({
          ...prev,
          latestResults: [...prev.latestResults, apiResult],
          targetModels: prev.targetModels.map(item => 
            item.id === targetItem.id ? { ...item, status: isSuccess ? 'success' : 'error' } : item
          )
        }));

        const timestampStr = apiResult.report?.timestamp || new Date().toISOString().replace('T', ' ').slice(0, 19);
        const overallRes = (apiResult.all_result?.overallResult || apiResult.get_result || 'NG').toUpperCase();
        
        const newRow: TableRowData = {
          id: `res-${Date.now()}-${Math.random().toString().slice(-4)}`,
          mp: apiResult.mp_mode || payload.targetModel,
          init: payload.initModel,
          dev: payload.devModel,
          version: apiResult.version,
          timestamp: timestampStr,
          result: overallRes === 'OK' ? 'OK' : 'NG',
          allResult: apiResult.all_result,
          exceptionLogs: apiResult.exceptionLog,
          confirmation: overallRes === 'OK' ? 'Auto Clearance' : 'Flagged NG',
          priority: overallRes === 'OK' ? 'Normal' : 'High',
          note: apiResult.all_result?.compareNote || apiResult.message || 'Individual Retest'
        };

        accumulatedRows.push(newRow);

      } catch (err: any) {
        console.error(`Failed execution for ${payload.targetModel}:`, err);
        
        setIndividual(prev => ({
          ...prev,
          targetModels: prev.targetModels.map(item => 
            item.id === targetItem.id ? { ...item, status: 'error' } : item
          )
        }));

        const errorRow: TableRowData = {
          id: `err-${Date.now()}-${Math.random().toString().slice(-4)}`,
          mp: payload.targetModel,
          init: payload.initModel,
          dev: payload.devModel,
          version: 'E.0',
          timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19),
          result: 'NG',
          allResult: { overallResult: 'NG', error: 'Server Failure' },
          exceptionLogs: [{ stage: 'API Retest', status: 'FAILURE', error: err?.message || 'Server Exception' }],
          confirmation: 'Server Failure',
          priority: 'High',
          note: err?.message || 'HTTP 500 Internal Server Error'
        };

        accumulatedRows.push(errorRow);
      }
      
      // Reset and set table rows with freshly processed batch in real-time
      setTableRows([...accumulatedRows]);
    }

    setIndividual(prev => ({ ...prev, isCrosschecking: false }));
  };

  const runMappingCrosscheck = async () => {
    const validRows = mappingRows.filter(r => r.targetModel.trim() !== '');
    if (validRows.length === 0) {
      alert('Please configure at least one mapping row with a valid Target Model.');
      return;
    }

    const ssolgenet_cookie = getCookie('ssolgenet');
    const smsession_cookie = getCookie('SMSESSION');

    setIsMultiCrosschecking(true);
    let accumulatedRows: TableRowData[] = [];

    for (const mapRow of validRows) {
      setMappingRows(prev => prev.map(r => r.id === mapRow.id ? { ...r, status: 'loading' } : r));

      const payload = {
        ssolgenet_cookie,
        smsession_cookie,
        targetModel: formatModelInput(mapRow.targetModel),
        devModel: formatModelInput(mapRow.devModel),
        initModel: formatModelInput(mapRow.initModel)
      };

      try {
        const data = await safeFetchJson('/api/bom/retest_manual', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const apiResult: ApiSingleOutput = (data.results && data.results[0]) ? data.results[0] : {
          status: data.status || 'success',
          message: data.message || 'Retest finished',
          version: data.version ?? 1.0,
          mp_mode: data.report?.mp_model || payload.targetModel,
          get_result: data.get_result || 'NG',
          all_result: data.all_result || {},
          exceptionLog: data.execitionLog || data.exceptionLog || []
        };

        const isSuccess = apiResult.status === 'success' && apiResult.get_result !== 'NG';
        const timestampStr = apiResult.report?.timestamp || new Date().toISOString().replace('T', ' ').slice(0, 19);
        const overallRes = (apiResult.all_result?.overallResult || apiResult.get_result || 'NG').toUpperCase();

        setMappingRows(prev => prev.map(r => r.id === mapRow.id ? { 
          ...r, 
          status: isSuccess ? 'success' : 'error', 
          lastProcessedTime: timestampStr 
        } : r));

        const newRow: TableRowData = {
          id: `res-${Date.now()}-${Math.random().toString().slice(-4)}`,
          mp: apiResult.mp_mode || payload.targetModel,
          init: payload.initModel,
          dev: payload.devModel,
          version: apiResult.version,
          timestamp: timestampStr,
          result: overallRes === 'OK' ? 'OK' : 'NG',
          allResult: apiResult.all_result,
          exceptionLogs: apiResult.exceptionLog,
          confirmation: overallRes === 'OK' ? 'Auto Clearance' : 'Flagged NG',
          priority: overallRes === 'OK' ? 'Normal' : 'High',
          note: apiResult.all_result?.compareNote || apiResult.message || 'Mapping Multi-Cross Retest'
        };

        accumulatedRows.push(newRow);

      } catch (err: any) {
        console.error(`Failed execution for row ${mapRow.id}:`, err);
        setMappingRows(prev => prev.map(r => r.id === mapRow.id ? { ...r, status: 'error' } : r));

        const errorRow: TableRowData = {
          id: `err-${Date.now()}-${Math.random().toString().slice(-4)}`,
          mp: payload.targetModel,
          init: payload.initModel,
          dev: payload.devModel,
          version: 'E.0',
          timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19),
          result: 'NG',
          allResult: { overallResult: 'NG', error: 'API Execution Error' },
          exceptionLogs: [{ stage: 'Mapping Retest', status: 'FAILURE', error: err?.message || 'Server Exception' }],
          confirmation: 'Server Failure',
          priority: 'High',
          note: err?.message || 'HTTP 500 Internal Server Error'
        };

        accumulatedRows.push(errorRow);
      }

      setTableRows([...accumulatedRows]);
    }

    setIsMultiCrosschecking(false);
  };




  const handleRowClick = (row: TableRowData) => {
    setSelectedRow(row);
  };

  const filteredMappingRows = mappingRows.filter(row => {
    if (!mappingSearchQuery.trim()) return true;
    const q = mappingSearchQuery.toLowerCase();
    return (
      row.targetModel.toLowerCase().includes(q) ||
      row.devModel.toLowerCase().includes(q) ||
      row.initModel.toLowerCase().includes(q)
    );
  });

  const totalMappingRowsCount = mappingRows.length;
  const totalUniqueTargets = new Set(mappingRows.map(r => r.targetModel.trim()).filter(Boolean)).size;
  const totalUniqueDevs = new Set(mappingRows.map(r => r.devModel.trim()).filter(Boolean)).size;
  const totalUniqueInits = new Set(mappingRows.map(r => r.initModel.trim()).filter(Boolean)).size;

  const filteredRows = tableRows.filter(row => {
    if (resultFilter === 'OK' && row.result !== 'OK') return false;
    if (resultFilter === 'NG' && row.result !== 'NG') return false;
    if (resultFilter === 'CHECK') {
      const hasCheckSub = row.allResult && Object.values(row.allResult).includes('CHECK');
      if (!hasCheckSub) return false;
    }

    if (searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      const matchMp = row.mp.toLowerCase().includes(q);
      const matchInit = row.init.toLowerCase().includes(q);
      const matchDev = row.dev.toLowerCase().includes(q);
      if (!matchMp && !matchInit && !matchDev) return false;
    }
    return true;
  });

  return (
    <div className="min-h-screen bg-[#f8f9fc] text-zinc-800 font-sans flex flex-col antialiased relative">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".csv, .xlsx, .xls"
        className="hidden"
      />

      <button
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        className="absolute top-4 left-0 z-30 bg-white border border-zinc-200 shadow-md p-1.5 rounded-r-lg text-zinc-600 hover:text-zinc-900 transition-all flex items-center justify-center cursor-pointer"
        style={{ transform: isSidebarOpen ? 'translateX(320px)' : 'translateX(0px)', transition: 'transform 0.3s ease' }}
      >
        {isSidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>

      <div className="flex-1 flex overflow-hidden relative">
        <aside 
          className={`border-r border-zinc-200 bg-white flex flex-col overflow-y-auto shadow-xs transition-all duration-300 z-20 ${
            isSidebarOpen ? 'w-80 min-w-[320px]' : 'w-0 overflow-hidden min-w-0 opacity-0'
          }`}
        >
          <div className="p-4 border-b border-zinc-100">
            <div className="grid grid-cols-2 gap-1 p-1 rounded-xl bg-zinc-100 border border-zinc-200">
              <button
                onClick={() => setActiveTab('individual')}
                className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer ${
                  activeTab === 'individual' ? 'bg-[#990000] text-white shadow-sm' : 'text-zinc-600 hover:bg-white/60'
                }`}
              >
                <GitCompare className="h-3.5 w-3.5" /> Individual
              </button>
              <button
                onClick={() => setActiveTab('multi')}
                className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer ${
                  activeTab === 'multi' ? 'bg-[#990000] text-white shadow-sm' : 'text-zinc-600 hover:bg-white/60'
                }`}
              >
                <Layers3 className="h-3.5 w-3.5" /> Multi-Cross
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-5">
            {activeTab === 'individual' ? (
              <div className="space-y-5">
                <div className="space-y-1.5">
                  <h2 className="text-xs font-bold uppercase tracking-wider text-zinc-700 flex items-center gap-1.5">
                    <Sliders className="h-3.5 w-3.5 text-[#990000]" /> Individual Parameters
                  </h2>
                  <p className="text-[11px] text-zinc-400">Process target models sequentially with initial baseline.</p>

                  <div className="flex items-center gap-1.5 pt-1">
                    <div className="relative flex-1">
                      <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-400" />
                      <input
                        type="text"
                        value={individualSearchQuery}
                        onChange={(e) => setIndividualSearchQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleIndividualParamSearch()}
                        placeholder="Search parameters or models..."
                        className="w-full pl-8 pr-2.5 py-1.5 bg-zinc-50 border border-zinc-200 rounded-lg text-xs font-mono text-zinc-800 focus:outline-none focus:border-[#990000]"
                      />
                    </div>
                    <button
                      onClick={handleIndividualParamSearch}
                      className="px-3 py-1.5 bg-[#990000] hover:bg-[#800000] text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-xs transition-colors cursor-pointer"
                    >
                      <Search className="h-3.5 w-3.5" />
                      <span>Search</span>
                    </button>
                  </div>
                </div>

                <div className="space-y-2.5 p-3.5 rounded-xl bg-zinc-50 border border-zinc-200 shadow-2xs">
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-[11px] font-mono font-bold text-zinc-600 uppercase tracking-wide">
                      Target Models ({individual.targetModels.length})
                    </label>
                    <button
                      onClick={removeAllIndividualTargets}
                      className="text-[10px] text-red-600 font-semibold bg-red-50 hover:bg-red-100 px-2 py-0.5 rounded border border-red-200 flex items-center gap-1 cursor-pointer"
                    >
                      <Trash2 className="h-3 w-3" /> Clear
                    </button>
                  </div>

                  <div className="bg-white rounded-lg border border-zinc-200 divide-y divide-zinc-100 overflow-hidden">
                    {individual.targetModels.map((target, idx) => {
                      const isLast = idx === individual.targetModels.length - 1;
                      return (
                        <div key={target.id} className="p-2.5 flex items-center gap-2 hover:bg-zinc-50/50">
                          <input
                            type="text"
                            value={target.value}
                            onChange={(e) => handleIndividualTargetChange(target.id, e.target.value)}
                            onBlur={(e) => handleIndividualTargetBlur(target.id, e.target.value)}
                            placeholder="e.g. 85QNED74BSA.KWMFLJR"
                            className="flex-1 bg-zinc-50 border border-zinc-200 rounded px-2.5 py-1.5 text-xs font-mono focus:outline-none focus:border-[#990000]"
                          />
                          <div className="flex items-center gap-1">
                            {target.status === 'loading' && <RefreshCw className="h-3.5 w-3.5 animate-spin text-[#990000]" />}
                            {target.status === 'success' && <Check className="h-3.5 w-3.5 text-emerald-600" />}
                            {target.status === 'error' && <AlertTriangle className="h-3.5 w-3.5 text-red-600" />}
                            
                            <button
                              onClick={() => handleIndividualAutoSearchTarget(target.id)}
                              disabled={target.isSearching}
                              className="p-1.5 rounded bg-zinc-100 border border-zinc-300 text-xs text-zinc-700 cursor-pointer hover:bg-zinc-200"
                            >
                              <Search className="h-3.5 w-3.5 text-[#990000]" />
                            </button>
                            {isLast ? (
                              <button
                                onClick={() => addIndividualTargetRow(target.id)}
                                className="p-1.5 rounded bg-[#990000]/10 border border-[#990000]/30 text-[#990000] cursor-pointer hover:bg-[#990000]/20"
                              >
                                <Plus className="h-3.5 w-3.5" />
                              </button>
                            ) : (
                              <button
                                onClick={() => removeIndividualTargetRow(target.id)}
                                className="p-1.5 rounded bg-red-50 border border-red-200 text-red-600 cursor-pointer hover:bg-red-100"
                              >
                                <Minus className="h-3.5 w-3.5" />
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="space-y-1.5 p-3.5 rounded-xl bg-zinc-50 border border-zinc-200">
                  <label className="text-[11px] font-mono font-bold text-zinc-600 uppercase tracking-wide">
                    Development Model
                  </label>
                  <div className="relative flex items-center">
                    <input
                      type="text"
                      value={individual.devModel}
                      onChange={(e) => setIndividual({ ...individual, devModel: e.target.value })}
                      className="w-full bg-white border border-zinc-200 rounded-lg pl-3 pr-9 py-2 text-xs font-mono focus:outline-none focus:border-[#990000]"
                    />
                    <button
                      onClick={() => handleIndividualAutoSearchTarget('dev')}
                      className="absolute right-2 p-1 text-zinc-400 hover:text-[#990000] transition-colors cursor-pointer"
                    >
                      <Search className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>

                <div className="space-y-1.5 p-3.5 rounded-xl bg-zinc-50 border border-zinc-200">
                  <label className="text-[11px] font-mono font-bold text-zinc-600 uppercase tracking-wide">
                    Initial Baseline Model
                  </label>
                  <div className="relative flex items-center">
                    <input
                      type="text"
                      value={individual.initModel}
                      onChange={(e) => setIndividual({ ...individual, initModel: e.target.value })}
                      className="w-full bg-white border border-zinc-200 rounded-lg pl-3 pr-9 py-2 text-xs font-mono focus:outline-none focus:border-[#990000]"
                    />
                    <button
                      onClick={() => handleIndividualAutoSearchTarget('init')}
                      className="absolute right-2 p-1 text-zinc-400 hover:text-[#990000] transition-colors cursor-pointer"
                    >
                      <Search className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>

                <button
                  onClick={runSequentialRetest}
                  disabled={individual.isCrosschecking}
                  className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-[#990000] to-[#cc0000] hover:from-[#800000] hover:to-[#990000] text-white font-bold text-xs uppercase shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-60 cursor-pointer"
                >
                  {individual.isCrosschecking ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" /> Retesting Sequentially...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 fill-current" /> Crosscheck
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="space-y-5">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xs font-bold uppercase tracking-wider text-zinc-700 flex items-center gap-1.5">
                      <Layers className="h-3.5 w-3.5 text-[#990000]" /> Multi-Cross Control
                    </h2>
                    <p className="text-[11px] text-zinc-400">Manage BOM mapping table & verify sidebar queue.</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setMultiSubView('mapping')}
                    className={`py-2 px-2.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                      multiSubView === 'mapping' ? 'bg-[#990000] text-white shadow-xs' : 'bg-zinc-100 hover:bg-zinc-200 text-zinc-700 border border-zinc-300'
                    }`}
                  >
                    <Workflow className="h-3.5 w-3.5" />
                    <span className="truncate">Mapping View</span>
                  </button>
                  <button
                    onClick={() => setMultiSubView('pipeline')}
                    className={`py-2 px-2.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                      multiSubView === 'pipeline' ? 'bg-[#990000] text-white shadow-xs' : 'bg-zinc-100 hover:bg-zinc-200 text-zinc-700 border border-zinc-300'
                    }`}
                  >
                    <FolderDown className="h-3.5 w-3.5" />
                    <span className="truncate">Pull BOM Data</span>
                  </button>
                </div>

                <div className="space-y-2.5 p-3 rounded-xl bg-zinc-50 border border-zinc-200">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono font-bold text-zinc-700 uppercase flex items-center gap-1">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> Verify Mapping Queue ({mappingRows.length})
                    </span>
                    <button
                      onClick={addMappingRow}
                      className="p-1 rounded bg-[#990000]/10 text-[#990000] text-[10px] font-bold flex items-center gap-0.5 hover:bg-[#990000]/20"
                    >
                      <Plus className="h-3 w-3" /> Add
                    </button>
                  </div>

                  <div className="bg-white rounded-lg border border-zinc-200 divide-y divide-zinc-100 max-h-64 overflow-y-auto">
                    {mappingRows.map((mapItem, mIdx) => (
                      <div key={mapItem.id} className="p-2 space-y-1 font-mono text-[10px] hover:bg-zinc-50">
                        <div className="flex justify-between items-center text-zinc-400">
                          <span>#0{mIdx + 1}</span>
                          <div className="flex items-center gap-1">
                            {mapItem.status === 'loading' && <RefreshCw className="h-3 w-3 animate-spin text-[#990000]" />}
                            {mapItem.status === 'success' && <Check className="h-3 w-3 text-emerald-600" />}
                            {mapItem.status === 'error' && <AlertTriangle className="h-3 w-3 text-red-600" />}
                            <button onClick={() => removeMappingRow(mapItem.id)} className="text-red-500 hover:text-red-700">
                              <Trash2 className="h-3 w-3" />
                            </button>
                          </div>
                        </div>
                        <div className="font-bold text-zinc-800 truncate">Target: {mapItem.targetModel || '(empty)'}</div>
                        <div className="text-zinc-500 truncate">Dev: {mapItem.devModel || '(empty)'}</div>
                        <div className="text-zinc-400 truncate">Init: {mapItem.initModel || '(empty)'}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  onClick={runMappingCrosscheck}
                  disabled={isMultiCrosschecking}
                  className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-[#990000] to-[#cc0000] hover:from-[#800000] hover:to-[#990000] text-white font-bold text-xs uppercase shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-60 cursor-pointer"
                >
                  {isMultiCrosschecking ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" /> Crosschecking Mapping...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 fill-current" /> Crosscheck Mappings ({mappingRows.length})
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </aside>

        <main className="flex-1 bg-[#f4f5f9] overflow-y-auto p-6 lg:p-8 space-y-6 min-w-0 transition-all duration-300">
          {activeTab === 'multi' && (
            <div className="space-y-6">
              <div className="p-5 rounded-2xl bg-white border border-zinc-200 shadow-2xs space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-100 pb-4">
                  <div>
                    <h1 className="text-base font-bold text-zinc-900 flex items-center gap-2">
                      <Workflow className="h-5 w-5 text-[#990000]" /> Multi-Cross BOM Mapping Generator
                    </h1>
                    <p className="text-xs text-zinc-400">Configure, calculate, and verify model mapping rows dynamically.</p>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-400" />
                      <input
                        type="text"
                        value={mappingSearchQuery}
                        onChange={(e) => setMappingSearchQuery(e.target.value)}
                        placeholder="Search mapping models..."
                        className="pl-8 pr-3 py-1.5 rounded-lg bg-zinc-50 border border-zinc-200 text-xs font-mono text-zinc-800 focus:outline-none focus:border-[#990000] w-64"
                      />
                    </div>

                    <button
                      onClick={() => setShowMappingContent(!showMappingContent)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 border shadow-2xs transition-all cursor-pointer ${
                        showMappingContent
                          ? 'bg-zinc-100 hover:bg-zinc-200 text-zinc-700 border-zinc-300'
                          : 'bg-[#990000]/10 hover:bg-[#990000]/20 text-[#990000] border-[#990000]/30 font-bold'
                      }`}
                    >
                      {showMappingContent ? (
                        <>
                          <EyeOff className="h-3.5 w-3.5 text-zinc-500" /> Hide View
                        </>
                      ) : (
                        <>
                          <Eye className="h-3.5 w-3.5 text-[#990000]" /> Show View
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {showMappingContent && (
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono">
                    <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 flex flex-col">
                      <span className="text-[10px] text-zinc-400 uppercase font-bold">Total Mapping Rows</span>
                      <span className="text-lg font-bold text-zinc-900">{totalMappingRowsCount}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 flex flex-col">
                      <span className="text-[10px] text-zinc-400 uppercase font-bold">Unique Target Models</span>
                      <span className="text-lg font-bold text-[#990000]">{totalUniqueTargets}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 flex flex-col">
                      <span className="text-[10px] text-zinc-400 uppercase font-bold">Unique Dev Models</span>
                      <span className="text-lg font-bold text-zinc-800">{totalUniqueDevs}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 flex flex-col">
                      <span className="text-[10px] text-zinc-400 uppercase font-bold">Unique Init Models</span>
                      <span className="text-lg font-bold text-zinc-800">{totalUniqueInits}</span>
                    </div>
                  </div>
                )}
              </div>

              {showMappingContent && (
                <div className="rounded-2xl bg-white border border-zinc-200 overflow-hidden shadow-2xs space-y-4 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-700 flex items-center gap-1.5">
                      <Table className="h-4 w-4 text-[#990000]" /> Model Mapping
                    </h3>
                    
                    <div className="flex items-center gap-2">
                      <button
                        onClick={addMappingRow}
                        className="px-3 py-1.5 rounded-lg bg-[#990000] text-white text-xs font-semibold flex items-center gap-1.5 shadow-xs cursor-pointer hover:bg-[#800000]"
                      >
                        <Plus className="h-3.5 w-3.5" /> Add Mapping Row
                      </button>

                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="px-3 py-1.5 rounded-lg bg-emerald-700 text-white text-xs font-semibold flex items-center gap-1.5 shadow-xs cursor-pointer hover:bg-emerald-800"
                      >
                        <Upload className="h-3.5 w-3.5" /> Upload Excel / CSV
                      </button>
                    </div>
                  </div>

                  <div className="overflow-x-auto border border-zinc-200 rounded-xl">
                    <table className="w-full text-left border-collapse text-xs font-mono">
                      <thead>
                        <tr className="border-b border-zinc-200 bg-zinc-50 text-[11px] text-zinc-500 uppercase">
                          <th className="p-3.5 w-12 text-center">#</th>
                          <th className="p-3.5">Target Model</th>
                          <th className="p-3.5">Development Model</th>
                          <th className="p-3.5">Initial Model</th>
                          <th className="p-3.5 w-24 text-center">Status</th>
                          <th className="p-3.5 w-16 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-zinc-100 text-zinc-700">
                        {filteredMappingRows.length > 0 ? (
                          filteredMappingRows.map((row, idx) => {
                            const hasTargetError = row.isTargetValid === false;
                            const hasDevError = row.isDevValid === false;
                            const hasInitError = row.isInitValid === false;
                            const hasAnyError = hasTargetError || hasDevError || hasInitError;

                            return (
                              <tr key={row.id} className={`transition-colors ${hasAnyError ? 'bg-red-50/70' : 'hover:bg-zinc-50/80'}`}>
                                <td className="p-3.5 text-center text-zinc-400 font-bold">{idx + 1}</td>
                                
                                <td className="p-3">
                                  <div className="space-y-1">
                                    <input
                                      type="text"
                                      value={row.targetModel}
                                      onChange={(e) => handleMappingRowChange(row.id, 'targetModel', e.target.value)}
                                      placeholder="modelname.suffixname"
                                      className={`w-full border rounded px-2.5 py-1.5 text-xs font-mono focus:outline-none ${
                                        hasTargetError 
                                          ? 'bg-red-100 border-red-400 text-red-900 placeholder-red-400' 
                                          : 'bg-zinc-50 border-zinc-200 text-zinc-900 focus:border-[#990000]'
                                      }`}
                                    />
                                    {hasTargetError && (
                                      <span className="text-[9px] text-red-600 font-bold flex items-center gap-0.5">
                                        <AlertTriangle className="h-2.5 w-2.5" /> Invalid Format (model.suffix)
                                      </span>
                                    )}
                                  </div>
                                </td>

                                <td className="p-3">
                                  <div className="space-y-1">
                                    <input
                                      type="text"
                                      value={row.devModel}
                                      onChange={(e) => handleMappingRowChange(row.id, 'devModel', e.target.value)}
                                      placeholder="modelname.suffixname"
                                      className={`w-full border rounded px-2.5 py-1.5 text-xs font-mono focus:outline-none ${
                                        hasDevError 
                                          ? 'bg-red-100 border-red-400 text-red-900 placeholder-red-400' 
                                          : 'bg-zinc-50 border-zinc-200 text-zinc-900 focus:border-[#990000]'
                                      }`}
                                    />
                                    {hasDevError && (
                                      <span className="text-[9px] text-red-600 font-bold flex items-center gap-0.5">
                                        <AlertTriangle className="h-2.5 w-2.5" /> Invalid Format (model.suffix)
                                      </span>
                                    )}
                                  </div>
                                </td>

                                <td className="p-3">
                                  <div className="space-y-1">
                                    <input
                                      type="text"
                                      value={row.initModel}
                                      onChange={(e) => handleMappingRowChange(row.id, 'initModel', e.target.value)}
                                      placeholder="modelname.suffixname"
                                      className={`w-full border rounded px-2.5 py-1.5 text-xs font-mono focus:outline-none ${
                                        hasInitError 
                                          ? 'bg-red-100 border-red-400 text-red-900 placeholder-red-400' 
                                          : 'bg-zinc-50 border-zinc-200 text-zinc-900 focus:border-[#990000]'
                                      }`}
                                    />
                                    {hasInitError && (
                                      <span className="text-[9px] text-red-600 font-bold flex items-center gap-0.5">
                                        <AlertTriangle className="h-2.5 w-2.5" /> Invalid Format (model.suffix)
                                      </span>
                                    )}
                                  </div>
                                </td>

                                <td className="p-3 text-center">
                                  {row.status === 'loading' && (
                                    <span className="inline-flex items-center gap-1 text-[#990000] font-bold text-[10px]">
                                      <RefreshCw className="h-3 w-3 animate-spin" /> Running
                                    </span>
                                  )}
                                  {row.status === 'success' && (
                                    <span className="inline-flex items-center gap-1 text-emerald-600 font-bold text-[10px]">
                                      <Check className="h-3 w-3" /> Processed
                                    </span>
                                  )}
                                  {row.status === 'idle' && (
                                    <span className="text-zinc-400 text-[10px]">Ready</span>
                                  )}
                                  {row.status === 'error' && (
                                    <span className="text-red-600 font-bold text-[10px]">Failed</span>
                                  )}
                                </td>

                                <td className="p-3 text-right">
                                  <button
                                    onClick={() => removeMappingRow(row.id)}
                                    className="p-1.5 text-zinc-400 hover:text-red-600 rounded hover:bg-red-50 transition-colors cursor-pointer"
                                  >
                                    <Trash2 className="h-3.5 w-3.5" />
                                  </button>
                                </td>
                              </tr>
                            );
                          })
                        ) : (
                          <tr>
                            <td colSpan={6} className="p-6 text-center text-zinc-400">
                              No mapping rows matched search query.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  <div className="flex justify-between items-center pt-2">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={addMappingRow}
                        className="px-4 py-2 rounded-xl bg-zinc-100 hover:bg-zinc-200 text-zinc-700 text-xs font-semibold flex items-center gap-1.5 border border-zinc-300 transition-all cursor-pointer"
                      >
                        <Plus className="h-4 w-4 text-[#990000]" /> Generate New Mapping Row
                      </button>

                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="px-4 py-2 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-semibold flex items-center gap-1.5 border border-emerald-300 transition-all cursor-pointer"
                      >
                        <FileSpreadsheet className="h-4 w-4 text-emerald-600" /> Upload Excel / CSV File
                      </button>
                    </div>

                    <button
                      onClick={runMappingCrosscheck}
                      disabled={isMultiCrosschecking}
                      className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#990000] to-[#cc0000] text-white text-xs font-bold uppercase tracking-wider flex items-center gap-2 shadow-md hover:from-[#800000] cursor-pointer disabled:opacity-50"
                    >
                      {isMultiCrosschecking ? (
                        <>
                          <RefreshCw className="h-4 w-4 animate-spin" /> Sequential Crosscheck Active...
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 fill-current" /> Crosscheck All Mappings ({mappingRows.length})
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}

            </div>
          )}

          <div className="p-4 rounded-2xl bg-white border border-zinc-200 shadow-2xs space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <button 
                  onClick={activeTab === 'multi' ? runMappingCrosscheck : runSequentialRetest} 
                  className="px-3.5 py-1.5 rounded-lg bg-[#990000] text-white text-xs font-semibold flex items-center gap-1.5 shadow-xs cursor-pointer hover:bg-[#800000]"
                >
                  <RefreshCw className="h-3.5 w-3.5" /> Retest Live
                </button>

                <button 
                  onClick={() => {
                    if (!selectedRow) {
                      alert('Please click and select a row from the table first.');
                      return;
                    }
                    alert(`Viewing comprehensive report for ${selectedRow.mp}`);
                  }}
                  className="px-3 py-1.5 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-zinc-700 text-xs font-semibold flex items-center gap-1.5 border border-zinc-300 transition-all cursor-pointer"
                >
                  <Eye className="h-3.5 w-3.5 text-[#990000]" />
                  <span>View Result</span>
                </button>

                <button 
                  onClick={() => alert('Launching Compare Mode for selected target baseline...')}
                  className="px-3 py-1.5 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-zinc-700 text-xs font-semibold flex items-center gap-1.5 border border-zinc-300 transition-all cursor-pointer"
                >
                  <GitCompare className="h-3.5 w-3.5 text-[#990000]" />
                  <span>Compare</span>
                </button>

                <div className="flex items-center gap-1 bg-zinc-100 p-1 rounded-lg border border-zinc-200">
                  <button 
                    onClick={() => setResultViewLayout('table-row')} 
                    className={`p-1 rounded text-xs ${resultViewLayout === 'table-row' ? 'bg-white text-[#990000] font-bold shadow-2xs' : 'text-zinc-500 hover:text-zinc-800'}`}
                  >
                    <List className="h-3.5 w-3.5" />
                  </button>
                  <button 
                    onClick={() => setResultViewLayout('column-row')} 
                    className={`p-1 rounded text-xs ${resultViewLayout === 'column-row' ? 'bg-white text-[#990000] font-bold shadow-2xs' : 'text-zinc-500 hover:text-zinc-800'}`}
                  >
                    <Rows className="h-3.5 w-3.5" />
                  </button>
                  <button 
                    onClick={() => setResultViewLayout('grid')} 
                    className={`p-1 rounded text-xs ${resultViewLayout === 'grid' ? 'bg-white text-[#990000] font-bold shadow-2xs' : 'text-zinc-500 hover:text-zinc-800'}`}
                  >
                    <LayoutGrid className="h-3.5 w-3.5" />
                  </button>
                </div>

                <button 
                  onClick={() => setHighlightDifferent(!highlightDifferent)} 
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition-all cursor-pointer ${
                    highlightDifferent 
                      ? 'bg-amber-100 text-amber-900 border-amber-300 font-bold' 
                      : 'bg-zinc-100 text-zinc-700 border-zinc-300 hover:bg-zinc-200'
                  }`}
                >
                  <Sparkles className="h-3.5 w-3.5 text-amber-600" />
                  <span>Highlight Different</span>
                </button>

                <div className="relative inline-flex items-center">
                  <select
                    value={selectedViewModule}
                    onChange={(e) => setSelectedViewModule(e.target.value as ViewModuleOption)}
                    className="pl-3 pr-8 py-1.5 rounded-lg bg-zinc-50 border border-zinc-300 text-xs font-mono font-semibold text-zinc-800 appearance-none focus:outline-none focus:border-[#990000] cursor-pointer hover:bg-zinc-100"
                  >
                    <option value="structure">View: Structure</option>
                    <option value="ben compare">View: BEN Compare</option>
                    <option value="substitute">View: Substitute</option>
                    <option value="hw option">View: HW Option</option>
                    <option value="HW part check">View: HW Part Check</option>
                    <option value="MPS Check">View: MPS Check</option>
                    <option value="operation plan">View: Operation Plan</option>
                    <option value="tool option">View: Tool Option</option>
                    <option value="substitute check">View: Substitute Check</option>
                  </select>
                  <ChevronDown className="absolute right-2.5 top-2.5 h-3.5 w-3.5 text-zinc-400 pointer-events-none" />
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search MP Model..."
                    className="pl-8 pr-3 py-1.5 rounded-lg bg-zinc-50 border border-zinc-200 text-xs font-mono text-zinc-800 focus:outline-none focus:border-[#990000] w-52"
                  />
                </div>

                <div className="flex items-center gap-1 bg-zinc-100 p-1 rounded-lg border border-zinc-200">
                  <button 
                    onClick={() => setResultFilter(resultFilter === 'OK' ? 'ALL' : 'OK')} 
                    className={`px-2.5 py-1 rounded text-xs font-mono font-semibold cursor-pointer transition-colors ${
                      resultFilter === 'OK' ? 'bg-emerald-600 text-white shadow-2xs' : 'text-emerald-700 hover:bg-emerald-50'
                    }`}
                  >
                    Show OK
                  </button>

                  <button 
                    onClick={() => setResultFilter(resultFilter === 'NG' ? 'ALL' : 'NG')} 
                    className={`px-2.5 py-1 rounded text-xs font-mono font-semibold cursor-pointer transition-colors ${
                      resultFilter === 'NG' ? 'bg-red-600 text-white shadow-2xs' : 'text-red-700 hover:bg-red-50'
                    }`}
                  >
                    Show NG
                  </button>

                  <button 
                    onClick={() => setResultFilter(resultFilter === 'CHECK' ? 'ALL' : 'CHECK')} 
                    className={`px-2.5 py-1 rounded text-xs font-mono font-semibold cursor-pointer transition-colors ${
                      resultFilter === 'CHECK' ? 'bg-amber-600 text-white shadow-2xs' : 'text-amber-700 hover:bg-amber-50'
                    }`}
                  >
                    Show CHECK
                  </button>
                </div>
              </div>
            </div>
          </div>

          {resultViewLayout === 'table-row' && (
            <div className="rounded-2xl bg-white border border-zinc-200 overflow-hidden shadow-xs mb-8">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs font-mono">
                  <thead>
                    <tr className="border-b border-zinc-200 bg-zinc-50 text-[11px] text-zinc-500 uppercase">
                      <th className="p-4">Timestamp</th>
                      <th className="p-4">MP Model</th>
                      <th className="p-4">Version</th>
                      <th className="p-4">Overall Result</th>
                      <th className="p-4">Sub-Module Checks ({selectedViewModule})</th>
                      <th className="p-4">Exception Log Highlights</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100 text-zinc-700">
                    {filteredRows.length > 0 ? (
                      filteredRows.map((row) => {
                        const failedLogs = row.exceptionLogs?.filter(log => log.status === 'NG' || log.status === 'FAILURE') || [];
                        const isSelected = selectedRow?.id === row.id;

                        return (
                          <tr 
                            key={row.id} 
                            onClick={() => handleRowClick(row)}
                            className={`cursor-pointer transition-colors ${
                              isSelected 
                                ? 'bg-red-50/80 border-l-4 border-l-[#990000]' 
                                : highlightDifferent && row.result === 'NG'
                                ? 'bg-amber-50/40 hover:bg-amber-50/70'
                                : 'hover:bg-zinc-50'
                            }`}
                          >
                            <td className="p-4 text-zinc-500 text-[11px]">
                              <div className="flex items-center gap-1">
                                <Clock className="h-3 w-3 text-zinc-400" />
                                {row.timestamp}
                              </div>
                            </td>
                            <td className="p-4 font-bold text-zinc-900">{row.mp}</td>
                            <td className="p-4 text-zinc-600 font-bold">{row.version}</td>
                            <td className="p-4">
                              <span className={`px-2.5 py-1 rounded font-bold text-[10px] ${row.result === 'OK' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                                {row.result}
                              </span>
                            </td>
                            <td className="p-4 text-[11px]">
                              {row.allResult ? (
                                <div className="flex flex-wrap gap-1 max-w-xs">
                                  {Object.entries(row.allResult).map(([k, v]) => (
                                    k !== 'overallResult' && (
                                      <span key={k} className={`px-1.5 py-0.5 rounded text-[9px] border ${
                                        v === 'NG' 
                                          ? 'bg-red-50 text-red-700 border-red-200 font-bold' 
                                          : v === 'CHECK' 
                                          ? 'bg-amber-50 text-amber-700 border-amber-200 font-bold' 
                                          : 'bg-zinc-100 text-zinc-600 border-zinc-200'
                                      }`}>
                                        {k}: {String(v)}
                                      </span>
                                    )
                                  ))}
                                </div>
                              ) : '-'}
                            </td>
                            <td className="p-4 text-[11px]">
                              {failedLogs.length > 0 ? (
                                <div className="space-y-1">
                                  {failedLogs.map((fLog, fIdx) => (
                                    <div key={fIdx} className="flex items-center gap-1 text-red-600 bg-red-50 p-1 rounded border border-red-200">
                                      <AlertTriangle className="h-3 w-3 flex-shrink-0" />
                                      <span className="font-bold">{fLog.stage}: {fLog.status}</span>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <span className="text-emerald-600 text-[10px] font-semibold">No Exception Errors</span>
                              )}
                            </td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr><td colSpan={6} className="p-8 text-center text-zinc-400">No matching model records found.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {resultViewLayout === 'column-row' && (
            <div className="space-y-3 mb-8">
              {filteredRows.map((row) => (
                <div 
                  key={row.id} 
                  onClick={() => handleRowClick(row)}
                  className={`p-4 rounded-xl bg-white border border-zinc-200 shadow-2xs space-y-2 font-mono text-xs cursor-pointer hover:border-[#990000] transition-colors ${
                    selectedRow?.id === row.id ? 'border-[#990000] ring-1 ring-[#990000]/20 bg-red-50/20' : ''
                  }`}
                >
                  <div className="flex justify-between items-center border-b border-zinc-100 pb-2">
                    <span className="font-bold text-zinc-900 text-sm">{row.mp}</span>
                    <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${row.result === 'OK' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                      {row.result}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-zinc-600">
                    <div>Dev: <span className="font-bold text-zinc-800">{row.dev}</span></div>
                    <div>Init: <span className="font-bold text-zinc-800">{row.init}</span></div>
                    <div>Version: <span className="font-bold text-zinc-800">{row.version}</span></div>
                    <div>Time: <span className="text-zinc-500">{row.timestamp}</span></div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {resultViewLayout === 'grid' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {filteredRows.map((row) => (
                <div 
                  key={row.id} 
                  onClick={() => handleRowClick(row)}
                  className={`p-4 rounded-xl bg-white border border-zinc-200 shadow-2xs flex flex-col justify-between font-mono text-xs space-y-3 cursor-pointer hover:border-[#990000] transition-colors ${
                    selectedRow?.id === row.id ? 'border-[#990000] ring-1 ring-[#990000]/20 bg-red-50/20' : ''
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-bold text-zinc-900">{row.mp}</div>
                      <div className="text-[10px] text-zinc-400">{row.timestamp}</div>
                    </div>
                    <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${row.result === 'OK' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                      {row.result}
                    </span>
                  </div>
                  <div className="space-y-1 text-[11px] text-zinc-600 bg-zinc-50 p-2.5 rounded-lg border border-zinc-100">
                    <div className="truncate">Dev: {row.dev}</div>
                    <div className="truncate">Init: {row.init}</div>
                    <div>Version: {row.version}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

        </main>

        {selectedRow && (
          <aside className="w-96 min-w-[384px] bg-white border-l border-zinc-200 flex flex-col h-full z-20 shadow-lg overflow-y-auto transition-all duration-300">
            <div className="p-4 border-b border-zinc-200 flex items-center justify-between bg-zinc-50">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-[#990000]" />
                <h3 className="font-bold text-xs uppercase tracking-wider text-zinc-800">
                  Model Result Details
                </h3>
              </div>
              <button
                onClick={() => setSelectedRow(null)}
                className="p-1 rounded text-zinc-400 hover:text-zinc-700 hover:bg-zinc-200 transition-colors cursor-pointer"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="p-5 flex-1 space-y-6 font-mono text-xs overflow-y-auto">
              <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-200 space-y-2">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] text-zinc-400 uppercase font-bold">Target / MP Model</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    selectedRow.result === 'OK' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {selectedRow.result}
                  </span>
                </div>
                <div className="text-sm font-bold text-zinc-900 break-all">{selectedRow.mp}</div>
                <div className="text-[10px] text-zinc-400 flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {selectedRow.timestamp}
                </div>
              </div>

              <button
                onClick={() => alert(`Opening comprehensive result report for ${selectedRow.mp}`)}
                className="w-full py-2.5 px-4 rounded-xl bg-[#990000] hover:bg-[#800000] text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-xs transition-colors cursor-pointer"
              >
                <ExternalLink className="h-4 w-4" />
                <span>View Full Result Report</span>
              </button>

              <div className="space-y-3">
                <h4 className="text-[11px] font-bold uppercase tracking-wider text-zinc-500 border-b border-zinc-100 pb-1">
                  Model Specifications
                </h4>
                <div className="bg-zinc-50 rounded-xl p-3 border border-zinc-200 space-y-2 text-[11px]">
                  <div className="flex justify-between items-center">
                    <span className="text-zinc-500">Development:</span>
                    <span className="font-bold text-zinc-800 break-all pl-2 text-right">{selectedRow.dev}</span>
                  </div>
                  <div className="flex justify-between items-center border-t border-zinc-200/60 pt-1.5">
                    <span className="text-zinc-500">Initial Baseline:</span>
                    <span className="font-bold text-zinc-800 break-all pl-2 text-right">{selectedRow.init}</span>
                  </div>
                  <div className="flex justify-between items-center border-t border-zinc-200/60 pt-1.5">
                    <span className="text-zinc-500">Version:</span>
                    <span className="font-bold text-zinc-800">{selectedRow.version}</span>
                  </div>
                  <div className="flex justify-between items-center border-t border-zinc-200/60 pt-1.5">
                    <span className="text-zinc-500">Active View:</span>
                    <span className="font-bold text-[#990000] capitalize">{selectedViewModule}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-[11px] font-bold uppercase tracking-wider text-zinc-500 border-b border-zinc-100 pb-1">
                  Sub-Module Checks
                </h4>
                {selectedRow.allResult ? (
                  <div className="grid grid-cols-1 gap-1.5">
                    {Object.entries(selectedRow.allResult).map(([key, val]) => (
                      <div key={key} className="flex items-center justify-between p-2 rounded-lg bg-zinc-50 border border-zinc-200 text-[11px]">
                        <span className="text-zinc-600 font-medium">{key}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          val === 'OK' 
                            ? 'bg-emerald-100 text-emerald-800' 
                            : val === 'NG' 
                            ? 'bg-red-100 text-red-800' 
                            : val === 'CHECK'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-zinc-200 text-zinc-700'
                        }`}>
                          {String(val)}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-zinc-400 italic text-[11px]">No sub-module check details available.</p>
                )}
              </div>

              <div className="space-y-3">
                <h4 className="text-[11px] font-bold uppercase tracking-wider text-zinc-500 border-b border-zinc-100 pb-1">
                  Exception Logs
                </h4>
                {selectedRow.exceptionLogs && selectedRow.exceptionLogs.length > 0 ? (
                  <div className="space-y-2">
                    {selectedRow.exceptionLogs.map((log, lIdx) => (
                      <div key={lIdx} className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-800 text-[11px] space-y-1">
                        <div className="flex items-center justify-between font-bold">
                          <span>{log.stage}</span>
                          <span className="text-[10px] text-red-600">{log.status}</span>
                        </div>
                        {log.error && <div className="text-[10px] text-red-700 font-sans">{log.error}</div>}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] flex items-center gap-1.5 font-semibold">
                    <Check className="h-4 w-4 text-emerald-600" />
                    <span>Clean execution with zero exceptions.</span>
                  </div>
                )}
              </div>

              {selectedRow.note && (
                <div className="space-y-1 pt-2 border-t border-zinc-100">
                  <span className="text-[10px] text-zinc-400 uppercase font-bold">Execution Note</span>
                  <p className="text-zinc-600 text-[11px] bg-zinc-50 p-2.5 rounded-lg border border-zinc-200 font-sans">
                    {selectedRow.note}
                  </p>
                </div>
              )}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}