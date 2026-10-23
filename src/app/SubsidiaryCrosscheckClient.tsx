'use client';

import React, { useState, useMemo, useRef, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Sun, 
  Moon, 
  ChevronRight,
  Database,
  PanelLeftClose,
  PanelLeftOpen,
  ChevronLeft,
  Layers,
  X,
  ExternalLink,
  Calendar,
  Info,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Download,
  AlertTriangle,
  Mail,
  ArrowLeft,
  Play,
  Loader2,
  DownloadCloud,
  UploadCloud,
  FileSpreadsheet,
  FileText
} from 'lucide-react';
import { fetchProductionData, ProductionItem } from './actions';

interface DiscrepantPart {
  partNumber: string;
  partName: string;
  marsVersion: string;
  gmesVersion: string;
  discrepancyType: string;
}

interface EngineerContact {
  name: string;
  role: string;
  department: string;
  email: string;
  phone: string;
}

interface SubsidiaryDetail {
  name: string;
  preMpDate: string;
  mpDate: string;
  result: 'MATCHED' | 'DISCREPANCY' | 'PENDING';
  compareNote: string;
  notification: string;
  discrepantParts: DiscrepantPart[];
  assignedEngineers: EngineerContact[];
}

interface UnifiedRecord {
  id: string;
  modelName: string;
  workOrder: string;
  marsSuffix: string;
  region: string;
  series: string;
  inch: string;
  soc: string;
  devModel: string;
  initialModel: string;
  bomReleaseDate: string;
  latestEco: string;
  subsidiaryList: string;
  subsidiaries: SubsidiaryDetail[];
  bomSync: 'SYNCED' | 'PENDING' | 'FAILED';
  gmesSuffix: string;
  preMpDate: string;
  mpDate: string;
  runningStatus: 'ACTIVE' | 'HOLD' | 'COMPLETED' | 'REVIEW';
  pvStatus: 'PV1' | 'PV2' | 'PV3' | 'MP Ready';
  syncDetails: {
    lastAttempt: string;
    targetSystem: string;
    matchedCount: number;
    discrepancyCount: number;
    logs: string[];
  };
}

const initialUnifiedData: UnifiedRecord[] = Array.from({ length: 55 }, (_, index) => {
  const idNum = index + 1;
  const regions = ['NA', 'EU', 'AP', 'LATAM', 'MEA'];
  const seriesList = ['OLED-Z', 'QNED-X', 'UHD-9', 'NanoCell-8'];
  const inches = ['55"', '65"', '75"', '85"', '43"'];
  const socs = ['Alpha 9 Gen 6', 'Alpha 7 Gen 5', 'MediaTek MT9638', 'Realtek RTD2855'];
  const syncs: ('SYNCED' | 'PENDING' | 'FAILED')[] = ['SYNCED', 'PENDING', 'FAILED'];
  const statuses: ('ACTIVE' | 'HOLD' | 'COMPLETED' | 'REVIEW')[] = ['ACTIVE', 'HOLD', 'COMPLETED', 'REVIEW'];
  const pvStatuses: ('PV1' | 'PV2' | 'PV3' | 'MP Ready')[] = ['PV1', 'PV2', 'PV3', 'MP Ready'];
  
  const monthPre = String((index % 6) + 1).padStart(2, '0');
  const dayPre = String((index % 25) + 1).padStart(2, '0');
  const monthMp = String(((index + 1) % 6) + 1).padStart(2, '0');
  const dayMp = String(((index + 5) % 25) + 1).padStart(2, '0');

  const syncState = syncs[index % syncs.length];

  const subNames = [
    'North America Corp', 
    'Europe BV', 
    'Asia Pacific Ltd', 
    'LATAM S.A.', 
    'MEA Regional', 
    'Domestic Hub', 
    'Global R&D Center'
  ];
  
  const subsidiaries: SubsidiaryDetail[] = subNames.map((sName, sIdx) => {
    const isDisc = (sIdx === 0 || sIdx === 3 || sIdx === 5) && (syncState === 'FAILED' || idNum % 2 === 0);
    return {
      name: `${sName} #${idNum}`,
      preMpDate: `2026-${monthPre}-${String(Number(dayPre) + (sIdx % 15)).padStart(2, '0')}`,
      mpDate: `2026-${monthMp}-${String(Number(dayMp) + (sIdx % 15)).padStart(2, '0')}`,
      result: isDisc ? 'DISCREPANCY' : sIdx === 1 && syncState === 'PENDING' ? 'PENDING' : 'MATCHED',
      compareNote: isDisc ? 'NG: Schema mismatch detected on part #8821' : 'Checksum verification passed successfully',
      notification: isDisc ? 'Alert: Action required by regional admin' : 'Synced normally with GMES master',
      discrepantParts: isDisc ? [
        { partNumber: 'PART-8821-X', partName: 'Main Controller IC V2', marsVersion: 'Rev 4.1', gmesVersion: 'Rev 3.9', discrepancyType: 'Pin-out Configuration Mismatch' },
        { partNumber: 'PART-9912-B', partName: 'Power Regulator Module', marsVersion: 'Rev 2.0', gmesVersion: 'Rev 1.8', discrepancyType: 'Tolerance Threshold Offset' }
      ] : [],
      assignedEngineers: isDisc ? [
        { name: 'Dr. Arthur Vance', role: 'Lead HW Integration Engineer', department: 'R&D Core Architecture', email: 'arthur.vance@enterprise.com', phone: '+1 (555) 382-9101' },
        { name: 'Elena Rostova', role: 'BOM Sync Controller', department: 'Global Manufacturing Operations', email: 'elena.rostova@enterprise.com', phone: '+1 (555) 492-8822' }
      ] : []
    };
  });

  return {
    id: `rec-${idNum}`,
    modelName: `MDL-2026-${100 + idNum}.BUSYLJP`,
    workOrder: `WO-2026-${8000 + idNum}`,
    marsSuffix: `MSFX-${String(idNum).padStart(2, '0')}`,
    region: regions[index % regions.length],
    series: seriesList[index % seriesList.length],
    inch: inches[index % inches.length],
    soc: socs[index % socs.length],
    devModel: `DEV-${7000 + idNum}`,
    initialModel: `INIT-${5000 + idNum}`,
    bomReleaseDate: `2026-${monthPre}-${dayPre}`,
    latestEco: `ECO-2026-${String(idNum).padStart(3, '0')}`,
    subsidiaryList: `Subsidiary-${(index % 4) + 1} Corp`,
    subsidiaries,
    bomSync: syncState,
    gmesSuffix: `GSFX-${String(idNum).padStart(2, '0')}`,
    preMpDate: `2026-${monthPre}-${dayPre}`,
    mpDate: `2026-${monthMp}-${dayMp}`,
    runningStatus: statuses[index % statuses.length],
    pvStatus: pvStatuses[index % pvStatuses.length],
    syncDetails: {
      lastAttempt: `2026-${monthPre}-${dayPre} 14:32:10 UTC`,
      targetSystem: `GMES-Enterprise-Node-${(index % 3) + 1}`,
      matchedCount: syncState === 'SYNCED' ? 142 : syncState === 'PENDING' ? 98 : 112,
      discrepancyCount: syncState === 'SYNCED' ? 0 : syncState === 'PENDING' ? 12 : 30,
      logs: syncState === 'SYNCED' 
        ? ['Validation checksum verified successfully', 'All 142 component nodes aligned with GMES master', 'Token handshake acknowledged']
        : syncState === 'PENDING'
        ? ['Awaiting batch queue slot allocation', 'Warning: Minor schema offset detected in subsidiary table', 'Retry scheduled in 15 mins']
        : ['CRITICAL: Mismatch in BOM part code #8821', 'Database constraint violation on subsidiary key', 'Sync aborted by remote gateway']
    }
  };
});

export default function LogisticsDashboard() {
  const [unifiedRecords, setUnifiedRecords] = useState<UnifiedRecord[]>(initialUnifiedData);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  const [activeRowDetail, setActiveRowDetail] = useState<UnifiedRecord | null>(null);
  const [showBomSyncResult, setShowBomSyncResult] = useState(false);
  const [activeDiagnosticTab, setActiveDiagnosticTab] = useState<'schedule' | 'result'>('schedule');

  const [sidebarViewMode, setSidebarViewMode] = useState<'tracking' | 'discrepancy'>('tracking');
  const [activeDiscrepancyData, setActiveDiscrepancyData] = useState<{
    record: UnifiedRecord | null;
    subsidiary: SubsidiaryDetail | null;
  }>({ record: null, subsidiary: null });

  const [tableSearch, setTableSearch] = useState('');
  const [subsidiaryQuery, setSubsidiaryQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('ALL');
  
  const [bomDateRange, setBomDateRange] = useState({ start: '', end: '' });
  const [preMpDateRange, setPreMpDateRange] = useState({ start: '', end: '' });
  const [mpDateRange, setMpDateRange] = useState({ start: '', end: '' });

  const [selectedPvStatus, setSelectedPvStatus] = useState('ALL');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  const [selectedRowIds, setSelectedRowIds] = useState<string[]>([]);
  const [isCrosschecking, setIsCrosschecking] = useState(false);
  const [isPullingGmes, setIsPullingGmes] = useState(false);
  const [isPullingMars, setIsPullingMars] = useState(false);
  const [crosscheckNotification, setCrosscheckNotification] = useState<string | null>(null);

  const [showDownloadDropdown, setShowDownloadDropdown] = useState(false);
  const downloadDropdownRef = useRef<HTMLDivElement>(null);

  const [currentPage, setCurrentPage] = useState(1);
  // Defaulting to 10 rows per page as requested
  const rowsPerPage = showBomSyncResult ? 5 : 10;

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (downloadDropdownRef.current && !downloadDropdownRef.current.contains(event.target as Node)) {
        setShowDownloadDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredRecords = useMemo(() => {
    return unifiedRecords.filter(item => {
      const matchesMain = tableSearch === '' || 
        item.modelName.toLowerCase().includes(tableSearch.toLowerCase()) || 
        item.workOrder.toLowerCase().includes(tableSearch.toLowerCase()) ||
        item.marsSuffix.toLowerCase().includes(tableSearch.toLowerCase()) ||
        item.series.toLowerCase().includes(tableSearch.toLowerCase());

      const matchesSubsidiary = subsidiaryQuery === '' || 
        item.subsidiaryList.toLowerCase().includes(subsidiaryQuery.toLowerCase());

      const matchesRegion = selectedRegion === 'ALL' || item.region === selectedRegion;
      const matchesPv = selectedPvStatus === 'ALL' || item.pvStatus === selectedPvStatus;

      let matchesBomDate = true;
      if (bomDateRange.start && item.bomReleaseDate < bomDateRange.start) matchesBomDate = false;
      if (bomDateRange.end && item.bomReleaseDate > bomDateRange.end) matchesBomDate = false;

      let matchesPreMpDate = true;
      if (preMpDateRange.start && item.preMpDate < preMpDateRange.start) matchesPreMpDate = false;
      if (preMpDateRange.end && item.preMpDate > preMpDateRange.end) matchesPreMpDate = false;

      let matchesMpDate = true;
      if (mpDateRange.start && item.mpDate < mpDateRange.start) matchesMpDate = false;
      if (mpDateRange.end && item.mpDate > mpDateRange.end) matchesMpDate = false;

      return matchesMain && matchesSubsidiary && matchesRegion && matchesPv && matchesBomDate && matchesPreMpDate && matchesMpDate;
    });
  }, [unifiedRecords, tableSearch, subsidiaryQuery, selectedRegion, selectedPvStatus, bomDateRange, preMpDateRange, mpDateRange]);

  const totalPages = Math.ceil(filteredRecords.length / rowsPerPage);
  const paginatedRecords = filteredRecords.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage);

  const totalRowsCount = filteredRecords.length;
  const chosenRowsCount = selectedRowIds.length;
  const chosenRecords = filteredRecords.filter(r => selectedRowIds.includes(r.id));
  const chosenNgCount = chosenRecords.reduce((acc, r) => acc + r.subsidiaries.filter(s => s.result === 'DISCREPANCY').length, 0);
  const chosenCheckedCount = chosenRecords.filter(r => r.bomSync === 'SYNCED' || r.bomSync === 'FAILED').length;

  const sortedTrackingRecords = useMemo(() => {
    if (!isCrosschecking && !isPullingGmes && !isPullingMars) return filteredRecords;
    if (selectedRowIds.length === 0) return filteredRecords;
    const loadingItems = filteredRecords.filter(r => selectedRowIds.includes(r.id));
    const otherItems = filteredRecords.filter(r => !selectedRowIds.includes(r.id));
    return [...loadingItems, ...otherItems];
  }, [filteredRecords, isCrosschecking, isPullingGmes, isPullingMars, selectedRowIds]);

  const handleSelectAllCurrentPage = () => {
    const pageIds = paginatedRecords.map(r => r.id);
    const allSelected = pageIds.every(id => selectedRowIds.includes(id));
    if (allSelected) {
      setSelectedRowIds(prev => prev.filter(id => !pageIds.includes(id)));
    } else {
      setSelectedRowIds(prev => Array.from(new Set([...prev, ...pageIds])));
    }
  };

  const handleToggleRowSelect = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedRowIds(prev => 
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    );
  };

  const handleTriggerManualCrosscheck = () => {
    if (selectedRowIds.length === 0) {
      setCrosscheckNotification('Please select at least one row using checkboxes to run manual crosscheck.');
      setTimeout(() => setCrosscheckNotification(null), 4000);
      return;
    }

    setIsCrosschecking(true);
    setCrosscheckNotification(`Running manual crosscheck for ${selectedRowIds.length} selected model(s)...`);

    setTimeout(() => {
      setIsCrosschecking(false);
      setCrosscheckNotification(`Manual crosscheck completed successfully for ${selectedRowIds.length} records!`);
      setTimeout(() => setCrosscheckNotification(null), 4000);
    }, 1800);
  };

  const handlePullGmesData = () => {
    if (selectedRowIds.length === 0) {
      setCrosscheckNotification('Please select at least one row to pull GMES data.');
      setTimeout(() => setCrosscheckNotification(null), 4000);
      return;
    }

    setIsPullingGmes(true);
    setCrosscheckNotification(`Pulling live GMES master stream for ${selectedRowIds.length} selected record(s)...`);

    setTimeout(() => {
      setIsPullingGmes(false);
      setCrosscheckNotification(`Successfully pulled GMES telemetry for ${selectedRowIds.length} models!`);
      setTimeout(() => setCrosscheckNotification(null), 4000);
    }, 1800);
  };

  const handlePullMarsData = async () => {
    setIsPullingMars(true);
    setCrosscheckNotification('Requesting FastAPI production data stream...');

    try {
      const response = await fetchProductionData();

      if (response.success && response.data) {
        const prodItems: ProductionItem[] = response.data;

        const subNames = [
          'North America Corp', 
          'Europe BV', 
          'Asia Pacific Ltd', 
          'LATAM S.A.', 
          'MEA Regional', 
          'Domestic Hub', 
          'Global R&D Center'
        ];

        const mappedRecords: UnifiedRecord[] = prodItems.map((item, idx) => {
          // Keep Model.Suffix as Model Name
          const fullModelSuffix = item['Model.Suffix'] || 'UNKNOWN.MODEL';
          const modelSuffixParts = fullModelSuffix.split('.');
          const marsSuffix = modelSuffixParts[1] || 'GENERAL';
          const cleanDate = (item['Date'] || '2026-10-26').replace('⭐', '').trim();
          
          const subsidiaries: SubsidiaryDetail[] = subNames.map((sName, sIdx) => {
            const isDisc = (sIdx % 3 === 0) && (idx % 2 === 0);
            return {
              name: `${sName} #${idx + 1}`,
              preMpDate: cleanDate,
              mpDate: cleanDate,
              result: isDisc ? 'DISCREPANCY' : 'MATCHED',
              compareNote: isDisc ? `WO ${item['Work Order']} Discrepancy on ${item['Production Site']}` : 'Production Verification Passed',
              notification: isDisc ? `Alert: WO ${item['Work Order']} holds delay` : 'WO Telemetry active',
              discrepantParts: isDisc ? [
                { partNumber: `WO-${item['Work Order'] || '000'}`, partName: `Site ${item['Production Site'] || 'HQ'} Assembly`, marsVersion: 'Rev 1.0', gmesVersion: 'Rev 0.9', discrepancyType: 'Plan Qty Mismatch' }
              ] : [],
              assignedEngineers: isDisc ? [
                { name: 'Lead Site Admin', role: 'Production Site Manager', department: item['Production Site'] || 'Global', email: 'site.admin@enterprise.com', phone: '+1 (555) 000-1122' }
              ] : []
            };
          });

          return {
            id: `api-prod-${idx + 1}`,
            modelName: fullModelSuffix,
            workOrder: item['Work Order'] || 'N/A',
            marsSuffix: marsSuffix,
            region: item['Country'] || 'GLOBAL',
            series: item['TV Group'] || 'LCD TV',
            inch: item['Plan Qty'] ? `Qty: ${item['Plan Qty']}` : 'N/A',
            soc: item['Event'] || 'Production',
            devModel: item['Work Order'] || 'N/A',
            initialModel: item['HQ Model'] || 'N/A',
            bomReleaseDate: cleanDate,
            latestEco: item['Production Site'] || 'SITE',
            subsidiaryList: item['Production Site'] ? `${item['Production Site']} Hub` : 'Main Hub',
            subsidiaries,
            bomSync: item['Status'] === 'NG' ? 'FAILED' : 'SYNCED',
            gmesSuffix: `GSFX-${idx + 1}`,
            preMpDate: cleanDate,
            mpDate: cleanDate,
            runningStatus: 'ACTIVE',
            pvStatus: 'MP Ready',
            syncDetails: {
              lastAttempt: `${cleanDate} 12:00:00 UTC`,
              targetSystem: `Site-${item['Production Site'] || 'EKHQ'}`,
              matchedCount: 100,
              discrepancyCount: item['Status'] === 'NG' ? 1 : 0,
              logs: [
                `Fetched via FastAPI /api/bom/get_production`,
                `Work Order: ${item['Work Order']}`,
                `Event: ${item['Event']}`
              ]
            }
          };
        });

        setUnifiedRecords(mappedRecords);
        setSelectedRowIds([]);
        setCurrentPage(1);
        setCrosscheckNotification(`Successfully loaded ${mappedRecords.length} production items from FastAPI!`);
      } else {
        setCrosscheckNotification(`FastAPI Error: ${response.error || 'Failed to fetch production data'}`);
      }
    } catch (err: any) {
      setCrosscheckNotification(`Connection Error: ${err?.message || 'Unable to reach backend'}`);
    } finally {
      setIsPullingMars(false);
      setTimeout(() => setCrosscheckNotification(null), 5000);
    }
  };

  const handleEmailReport = () => {
    const count = selectedRowIds.length > 0 ? selectedRowIds.length : filteredRecords.length;
    setCrosscheckNotification(`Email report containing ${count} model telemetry records has been dispatched successfully!`);
    setTimeout(() => setCrosscheckNotification(null), 4000);
  };

  const handleDownloadReport = (format: 'csv' | 'xlsx') => {
    setShowDownloadDropdown(false);
    const targetRecords = selectedRowIds.length > 0 ? filteredRecords.filter(r => selectedRowIds.includes(r.id)) : filteredRecords;
    
    let fileContent = "";
    let mimeType = "";
    let fileExtension = format;

    if (format === 'csv') {
      fileContent = "ModelName,WorkOrder,MarsSuffix,Region,Series,Inch,SoC,BOMReleaseDate,GMESRating,Status\n" +
        targetRecords.map(r => `"${r.modelName}","${r.workOrder}","${r.marsSuffix}","${r.region}","${r.series}","${r.inch}","${r.soc}","${r.bomReleaseDate}","${r.pvStatus}","${r.bomSync}"`).join("\n");
      mimeType = "text/csv;charset=utf-8;";
    } else {
      fileContent = "Model Name\tWO\tMARS Suffix\tRegion\tSeries\tInch\tSoC\tBOM Release Date\tPV Status\tBOM Sync\n" +
        targetRecords.map(r => `${r.modelName}\t${r.workOrder}\t${r.marsSuffix}\t${r.region}\t${r.series}\t${r.inch}\t${r.soc}\t${r.bomReleaseDate}\t${r.pvStatus}\t${r.bomSync}`).join("\n");
      mimeType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8;";
      fileExtension = "xlsx";
    }

    const encodedUri = encodeURI("data:" + mimeType + "," + fileContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Logistics_Telemetry_Report_${new Date().toISOString().slice(0,10)}.${fileExtension}`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setCrosscheckNotification(`Successfully downloaded report in .${fileExtension.toUpperCase()} format (${targetRecords.length} records)!`);
    setTimeout(() => setCrosscheckNotification(null), 4000);
  };

  const resetFilters = () => {
    setTableSearch('');
    setSubsidiaryQuery('');
    setSelectedRegion('ALL');
    setBomDateRange({ start: '', end: '' });
    setPreMpDateRange({ start: '', end: '' });
    setMpDateRange({ start: '', end: '' });
    setSelectedPvStatus('ALL');
    setSelectedRowIds([]);
    setCurrentPage(1);
  };

  const handleExcelExport = (modelName: string) => {
    const csvContent = "data:text/csv;charset=utf-8," + 
      "Field,Value\n" +
      `Model Name,${modelName}\n` +
      `Export Timestamp,${new Date().toISOString()}\n` +
      `Status,Diagnostic Logs Exported Successfully`;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Sync_Diagnostic_Report_${modelName}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const isHighPriorityWarning = (preMpDateStr: string) => {
    const preMpDate = new Date(preMpDateStr);
    const today = new Date('2026-06-01');
    const diffTime = preMpDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 14 && diffDays >= 0;
  };

  const getMarsSyncBadge = (sync: UnifiedRecord['bomSync']) => {
    switch(sync) {
      case 'SYNCED': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold flex items-center space-x-1 w-fit"><CheckCircle2 className="w-3 h-3" /><span>SYNCED</span></span>;
      case 'PENDING': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold flex items-center space-x-1 w-fit"><RefreshCw className="w-3 h-3 animate-spin" /><span>PENDING</span></span>;
      case 'FAILED': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 font-semibold flex items-center space-x-1 w-fit"><AlertCircle className="w-3 h-3" /><span>FAILED</span></span>;
    }
  };

  const getGmesStatusBadge = (status: UnifiedRecord['runningStatus']) => {
    switch(status) {
      case 'ACTIVE': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 font-semibold">ACTIVE</span>;
      case 'HOLD': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold">HOLD</span>;
      case 'COMPLETED': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold">COMPLETED</span>;
      case 'REVIEW': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 font-semibold">REVIEW</span>;
    }
  };

  const getPvStatusBadge = (pv: UnifiedRecord['pvStatus']) => {
    switch(pv) {
      case 'PV1': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 dark:bg-zinc-800 dark:text-zinc-300 font-semibold">PV1</span>;
      case 'PV2': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 font-semibold">PV2</span>;
      case 'PV3': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-100 text-cyan-800 font-semibold">PV3</span>;
      case 'MP Ready': return <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-[#C8102E] font-bold">MP Ready</span>;
    }
  };

  return (
    <div className={`h-screen w-full font-sans antialiased selection:bg-[#C8102E] selection:text-white flex overflow-hidden ${isDarkMode ? 'bg-zinc-950 text-zinc-100' : 'bg-slate-50 text-slate-800'}`}>
      
      {/* Left Sidebar: Detailed Row Tracking List */}
      <aside className={`h-full border-r flex flex-col shrink-0 transition-all duration-300 ease-in-out ${isSidebarOpen ? 'w-96 opacity-100' : 'w-0 opacity-0 overflow-hidden border-transparent'} ${isDarkMode ? 'bg-zinc-900 border-zinc-800' : 'bg-white border-slate-200 shadow-sm'}`}>
        <div className="w-96 h-full flex flex-col overflow-hidden">
          
          {sidebarViewMode === 'tracking' ? (
            <>
              <div className="p-4 border-b border-slate-100 dark:border-zinc-800 space-y-3 shrink-0">
                <div className="flex items-center justify-between">
                  <h2 className="font-bold text-sm tracking-tight text-slate-900 dark:text-white flex items-center space-x-2">
                    <span>Tracking list</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-[#C8102E] font-bold">{filteredRecords.length}</span>
                  </h2>
                  <span className="text-[10px] text-slate-400 font-mono">7-Box Crosscheck Heatmap</span>
                </div>
                
                <div className="relative">
                  <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                  <input 
                    type="text" 
                    placeholder="Filter rows..." 
                    value={tableSearch}
                    onChange={(e) => setTableSearch(e.target.value)}
                    className={`w-full pl-9 pr-4 py-2 text-xs rounded-xl border focus:outline-none focus:ring-2 focus:ring-[#C8102E]/20 focus:border-[#C8102E] transition-all ${
                      isDarkMode 
                        ? 'bg-zinc-800 border-zinc-700 text-zinc-100 placeholder-zinc-500' 
                        : 'bg-slate-50 border-slate-200 text-slate-900 placeholder-slate-400'
                    }`}
                  />
                </div>
              </div>

              {/* Scrollable Container */}
              <div className="flex-1 overflow-y-auto divide-y divide-slate-100 dark:divide-zinc-800 overscroll-contain pr-1">
                {sortedTrackingRecords.length === 0 ? (
                  <div className="p-8 text-center text-slate-400 text-xs">No telemetry records match your search criteria.</div>
                ) : (
                  sortedTrackingRecords.map((record) => {
                    const isSelected = activeRowDetail?.id === record.id;
                    const isRowLoading = (isCrosschecking || isPullingGmes || isPullingMars) && selectedRowIds.includes(record.id);
                    const loadingText = isPullingGmes ? 'Pulling GMES...' : isPullingMars ? 'Pulling Production...' : 'Crosschecking...';

                    return (
                      <div 
                        key={record.id}
                        onClick={() => {
                          if (!isRowLoading) setActiveRowDetail(record);
                        }}
                        className={`p-4 cursor-pointer transition-all border-l-4 space-y-2 relative ${
                          isRowLoading ? 'bg-red-50/40 dark:bg-red-950/20 opacity-75' :
                          isSelected 
                            ? 'bg-red-50/70 dark:bg-red-950/30 border-[#C8102E]' 
                            : 'border-transparent hover:bg-slate-50/80 dark:hover:bg-zinc-800/50'
                        }`}
                      >
                        {isRowLoading && (
                          <div className="absolute inset-0 bg-white/60 dark:bg-zinc-900/60 backdrop-blur-[0.5px] z-10 flex items-center justify-center space-x-2">
                            <Loader2 className="w-5 h-5 text-[#C8102E] animate-spin" />
                            <span className="text-[11px] font-bold text-[#C8102E]">{loadingText}</span>
                          </div>
                        )}

                        <div className="flex items-center justify-between">
                          <span className="font-bold text-xs font-mono tracking-wide text-slate-900 dark:text-white flex items-center space-x-1.5 truncate pr-2">
                            <Layers className="w-3.5 h-3.5 text-[#C8102E] shrink-0" />
                            <span className="truncate">{record.modelName}</span>
                          </span>
                          <span className="text-[10px] font-mono text-slate-400 shrink-0">{record.region}</span>
                        </div>

                        <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-600 dark:text-zinc-300">
                          <div>WO: <strong className="font-mono">{record.workOrder}</strong></div>
                          <div>Series: <strong className="font-mono">{record.series}</strong></div>
                        </div>

                        {/* 7-Box Linear Heatmap */}
                        <div className="pt-1.5 space-y-1">
                          <div className="flex items-center justify-between text-[10px] text-slate-400">
                            <span>7-Box Crosscheck Heatmap</span>
                            <span className="font-mono">Click Box</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            {record.subsidiaries.map((sub, sIdx) => {
                              const isOk = sub.result === 'MATCHED';
                              return (
                                <div 
                                  key={sIdx}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    if (!isRowLoading) {
                                      setActiveRowDetail(record);
                                      setShowBomSyncResult(true);
                                      setActiveDiagnosticTab('result');
                                    }
                                  }}
                                  title={`${sub.name}: ${sub.result} - Click to open Result Tab`}
                                  className={`h-3.5 flex-1 rounded-sm cursor-pointer transition-transform hover:scale-125 ${
                                    isOk 
                                      ? 'bg-emerald-500 shadow-xs shadow-emerald-500/20 hover:bg-emerald-400' 
                                      : 'bg-rose-600 shadow-xs shadow-rose-600/30 animate-pulse hover:bg-rose-500'
                                  }`}
                                />
                              );
                            })}
                          </div>
                        </div>

                        <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-100 dark:border-zinc-800/50">
                          <span>BOM: {record.bomReleaseDate}</span>
                          <span className="font-semibold text-[#C8102E]">{record.pvStatus}</span>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </>
          ) : (
            /* Discrepancy Action Report Sidebar */
            <div className="flex flex-col h-full overflow-hidden">
              <div className="p-4 border-b border-slate-100 dark:border-zinc-800 flex items-center justify-between bg-red-50 dark:bg-red-950/30 shrink-0">
                <div className="flex items-center space-x-2">
                  <div className="p-1.5 rounded-lg bg-red-100 text-[#C8102E]">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <h2 className="font-bold text-xs tracking-tight text-slate-900 dark:text-white uppercase">
                    Discrepancy Action Report
                  </h2>
                </div>
                <button 
                  onClick={() => setSidebarViewMode('tracking')}
                  className="px-2.5 py-1 rounded-lg bg-[#C8102E] text-white text-[11px] font-semibold hover:bg-red-700 transition-colors flex items-center space-x-1 shadow-xs"
                >
                  <ArrowLeft className="w-3 h-3" />
                  <span>View Tracking List</span>
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs overscroll-contain pr-1">
                {activeDiscrepancyData.subsidiary && activeDiscrepancyData.record && (
                  <>
                    <div className="space-y-1">
                      <span className="text-[10px] text-slate-400 block font-mono">Model: {activeDiscrepancyData.record.modelName}</span>
                      <h3 className="font-bold text-slate-900 dark:text-white">{activeDiscrepancyData.subsidiary.name}</h3>
                      {isHighPriorityWarning(activeDiscrepancyData.subsidiary.preMpDate) && (
                        <span className="inline-block mt-1 px-2 py-0.5 rounded-full bg-rose-600 text-white font-bold text-[9px] tracking-wider animate-pulse">
                          HIGH PRIORITY (&lt; 2 WEEKS TO PRE-MP)
                        </span>
                      )}
                    </div>

                    <div className={`p-3 rounded-xl border ${isDarkMode ? 'bg-zinc-800/60 border-zinc-700' : 'bg-slate-50 border-slate-200'}`}>
                      <span className="text-[10px] text-slate-400 block mb-1">Milestone Dates</span>
                      <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
                        <div>Pre-MP: <strong className="text-[#C8102E]">{activeDiscrepancyData.subsidiary.preMpDate}</strong></div>
                        <div>MP: <strong>{activeDiscrepancyData.subsidiary.mpDate}</strong></div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <h4 className="font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300">Discrepant Parts</h4>
                      <div className="space-y-2">
                        {activeDiscrepancyData.subsidiary.discrepantParts.map((part, idx) => (
                          <div key={idx} className={`p-3 rounded-xl border ${isDarkMode ? 'bg-zinc-800/40 border-zinc-700' : 'bg-white border-slate-200'} space-y-1`}>
                            <div className="flex items-center justify-between font-mono font-bold text-[#C8102E]">
                              <span>{part.partNumber}</span>
                              <span className="text-[10px] text-amber-600 font-sans">{part.discrepancyType}</span>
                            </div>
                            <span className="font-medium block">{part.partName}</span>
                            <div className="text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-100 dark:border-zinc-700 flex justify-between">
                              <span>MARS: {part.marsVersion}</span>
                              <span>GMES: {part.gmesVersion}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <h4 className="font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300">Assigned Engineers</h4>
                      <div className="space-y-2">
                        {activeDiscrepancyData.subsidiary.assignedEngineers.map((eng, idx) => (
                          <div key={idx} className={`p-3 rounded-xl border ${isDarkMode ? 'bg-zinc-800/40 border-zinc-700' : 'bg-white border-slate-200'} space-y-1.5`}>
                            <div className="flex items-center justify-between">
                              <span className="font-bold">{eng.name}</span>
                              <span className="text-[9px] px-1.5 py-0.5 rounded bg-red-100 text-[#C8102E] font-semibold">{eng.department}</span>
                            </div>
                            <span className="text-[10px] text-slate-500">{eng.role}</span>
                            <div className="pt-1.5 border-t border-slate-100 dark:border-zinc-700 flex flex-col space-y-1 text-[10px]">
                              <a href={`mailto:${eng.email}`} className="text-blue-600 hover:underline truncate">{eng.email}</a>
                              <a href={`tel:${eng.phone}`} className="text-slate-600 dark:text-zinc-300">{eng.phone}</a>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

        </div>
      </aside>

      {/* Main Content Area */}
      <main className={`h-full flex-1 relative flex flex-col overflow-hidden transition-all duration-300 ${activeRowDetail ? 'mr-96' : 'mr-0'} ${isDarkMode ? 'bg-zinc-950' : 'bg-slate-100'}`}>
        
        {/* Unified Table Container */}
        <div className="h-full p-4 flex flex-col overflow-y-auto space-y-4 overscroll-contain">
          
          {/* Top Action Header */}
          <div className={`p-3.5 rounded-2xl border shadow-sm flex flex-col lg:flex-row items-center justify-between gap-3 shrink-0 ${
            isDarkMode ? 'bg-zinc-900 border-zinc-800 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'
          }`}>
            <div className="flex flex-wrap items-center gap-2.5 w-full lg:w-auto">
              <button 
                onClick={handleTriggerManualCrosscheck}
                disabled={isCrosschecking || isPullingGmes || isPullingMars || selectedRowIds.length === 0}
                className="px-3.5 py-2 rounded-xl bg-[#C8102E] hover:bg-red-700 disabled:opacity-50 text-white font-bold text-xs transition-all shadow-md shadow-red-500/20 flex items-center space-x-1.5"
              >
                {isCrosschecking ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-white" />}
                <span>Trigger Crosscheck</span>
              </button>

              <button 
                onClick={handlePullGmesData}
                disabled={isCrosschecking || isPullingGmes || isPullingMars || selectedRowIds.length === 0}
                className="px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold text-xs transition-all shadow-md shadow-blue-500/20 flex items-center space-x-1.5"
              >
                {isPullingGmes ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <DownloadCloud className="w-3.5 h-3.5" />}
                <span>Pull GMES Data</span>
              </button>

              <button 
                onClick={handlePullMarsData}
                disabled={isCrosschecking || isPullingGmes || isPullingMars}
                className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-bold text-xs transition-all shadow-md shadow-indigo-500/20 flex items-center space-x-1.5"
              >
                {isPullingMars ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <UploadCloud className="w-3.5 h-3.5" />}
                <span>Pull Production Data</span>
              </button>

              <div className="flex items-center space-x-2 text-xs font-mono ml-auto lg:ml-0">
                <span className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300">
                  Chosen: <strong className="text-[#C8102E]">{chosenRowsCount}</strong>
                </span>
                <span className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300">
                  Total: <strong className="text-slate-900 dark:text-white">{totalRowsCount}</strong>
                </span>
                <span className="px-2.5 py-1 rounded-lg bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-400">
                  NG: <strong className="font-bold">{chosenNgCount}</strong>
                </span>
                <span className="px-2.5 py-1 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400">
                  Checked: <strong className="font-bold">{chosenCheckedCount}</strong>
                </span>

                {/* Export Options */}
                <div className="flex items-center space-x-1.5 pl-2 border-l border-slate-200 dark:border-zinc-700">
                  <button 
                    onClick={handleEmailReport}
                    className="px-2.5 py-1 rounded-lg bg-slate-200/70 dark:bg-zinc-700 text-slate-700 dark:text-zinc-200 hover:bg-slate-300 dark:hover:bg-zinc-600 font-semibold text-[11px] transition-all flex items-center space-x-1"
                    title="Email report of selected or filtered data"
                  >
                    <Mail className="w-3 h-3 text-[#C8102E]" />
                    <span>Email Report</span>
                  </button>

                  <div className="relative" ref={downloadDropdownRef}>
                    <button 
                      onClick={() => setShowDownloadDropdown(!showDownloadDropdown)}
                      className="px-2.5 py-1 rounded-lg bg-[#C8102E] text-white hover:bg-red-700 font-semibold text-[11px] transition-all flex items-center space-x-1 shadow-xs"
                    >
                      <Download className="w-3 h-3" />
                      <span>Download Report</span>
                      <ChevronDown className="w-3 h-3" />
                    </button>

                    {showDownloadDropdown && (
                      <div className={`absolute right-0 mt-2 w-48 rounded-xl border shadow-xl z-50 overflow-hidden animate-fadeIn ${
                        isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'
                      }`}>
                        <div className="p-2 border-b border-slate-100 dark:border-zinc-800 text-[10px] text-slate-400 font-mono">
                          Select Export Format
                        </div>
                        <div className="p-1">
                          <button 
                            onClick={() => handleDownloadReport('csv')}
                            className="w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-red-50 dark:hover:bg-red-950/40 hover:text-[#C8102E] transition-colors flex items-center space-x-2 font-medium"
                          >
                            <FileText className="w-3.5 h-3.5 text-slate-400" />
                            <span>Download as .CSV</span>
                          </button>
                          <button 
                            onClick={() => handleDownloadReport('xlsx')}
                            className="w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-red-50 dark:hover:bg-red-950/40 hover:text-[#C8102E] transition-colors flex items-center space-x-2 font-medium"
                          >
                            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600" />
                            <span>Download as .XLSX</span>
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

              </div>
            </div>

            {crosscheckNotification && (
              <div className="px-3 py-1.5 rounded-xl bg-red-100 text-[#C8102E] font-semibold text-xs animate-pulse flex items-center space-x-1.5">
                <AlertCircle className="w-4 h-4" />
                <span>{crosscheckNotification}</span>
              </div>
            )}
          </div>

          <div className={`rounded-2xl border flex flex-col shadow-sm overflow-hidden transition-all duration-300 ${isDarkMode ? 'bg-zinc-900 border-zinc-800' : 'bg-white border-slate-200'}`}>
            
            {/* Table Header Controls */}
            <div className="p-4 border-b border-slate-100 dark:border-zinc-800 flex flex-col gap-3 shrink-0">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
                <div className="flex items-center space-x-3">
                  <button 
                    onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                    className="p-2 rounded-xl bg-red-50 dark:bg-red-950/30 text-[#C8102E] hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors"
                    title={isSidebarOpen ? "Hide Tracking List" : "Show Tracking List"}
                  >
                    {isSidebarOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeftOpen className="w-4 h-4" />}
                  </button>
                  <div className="flex items-center space-x-2.5">
                    <div className="w-3 h-3 rounded-full bg-[#C8102E]" />
                    <h3 className="font-bold text-sm tracking-tight text-slate-900 dark:text-white uppercase flex items-center space-x-2">
                      <span>Joined Model Telemetry</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-[#C8102E] font-bold">{filteredRecords.length} Records</span>
                    </h3>
                  </div>
                </div>

                <div className="flex items-center space-x-2 w-full sm:w-auto">
                  <div className="relative flex-1 sm:w-64">
                    <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                    <input 
                      type="text" 
                      placeholder="Search model name or WO..."
                      value={tableSearch}
                      onChange={(e) => { setTableSearch(e.target.value); setCurrentPage(1); }}
                      className={`w-full pl-9 pr-3 py-2 text-xs rounded-xl border focus:outline-none focus:ring-2 focus:ring-[#C8102E]/20 focus:border-[#C8102E] ${
                        isDarkMode ? 'bg-zinc-800 border-zinc-700 text-zinc-100 placeholder-zinc-500' : 'bg-slate-50 border-slate-200 text-slate-900 placeholder-slate-400'
                      }`}
                    />
                  </div>

                  <button 
                    onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                    className={`px-3 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 border transition-all ${
                      showAdvancedFilters 
                        ? 'bg-[#C8102E] text-white border-[#C8102E]' 
                        : isDarkMode ? 'bg-zinc-800 border-zinc-700 text-zinc-300 hover:bg-zinc-700' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    <Filter className="w-3.5 h-3.5" />
                    <span>Filters</span>
                  </button>

                  <button 
                    onClick={() => setIsDarkMode(!isDarkMode)}
                    className="p-2 rounded-xl border border-slate-200 dark:border-zinc-700 text-slate-600 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
                    title="Toggle Theme"
                  >
                    {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
                  </button>

                  {(subsidiaryQuery || selectedRegion !== 'ALL' || bomDateRange.start || bomDateRange.end || preMpDateRange.start || preMpDateRange.end || mpDateRange.start || mpDateRange.end || selectedPvStatus !== 'ALL' || tableSearch) && (
                    <button 
                      onClick={resetFilters}
                      className="p-2 rounded-xl border border-red-200 bg-red-50 text-[#C8102E] hover:bg-red-100 transition-colors"
                      title="Reset all filters"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>

              {/* Advanced Filter Expansion Bar */}
              {showAdvancedFilters && (
                <div className={`p-4 rounded-xl border grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3 text-xs animate-fadeIn ${
                  isDarkMode ? 'bg-zinc-800/60 border-zinc-700' : 'bg-slate-50 border-slate-200'
                }`}>
                  <div>
                    <label className="block font-semibold mb-1 text-slate-600 dark:text-zinc-400">Subsidiary</label>
                    <input 
                      type="text" 
                      placeholder="Search..." 
                      value={subsidiaryQuery}
                      onChange={(e) => { setSubsidiaryQuery(e.target.value); setCurrentPage(1); }}
                      className={`w-full px-3 py-1.5 rounded-lg border ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'}`}
                    />
                  </div>

                  <div>
                    <label className="block font-semibold mb-1 text-slate-600 dark:text-zinc-400">Region Name</label>
                    <select 
                      value={selectedRegion}
                      onChange={(e) => { setSelectedRegion(e.target.value); setCurrentPage(1); }}
                      className={`w-full px-3 py-1.5 rounded-lg border ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'}`}
                    >
                      <option value="ALL">All Regions</option>
                      <option value="NA">NA</option>
                      <option value="EU">EU</option>
                      <option value="AP">AP</option>
                      <option value="LATAM">LATAM</option>
                      <option value="MEA">MEA</option>
                    </select>
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block font-semibold mb-1 text-slate-600 dark:text-zinc-400 flex items-center space-x-1">
                      <Calendar className="w-3 h-3 text-[#C8102E]" />
                      <span>BOM Release Date Range (A to B)</span>
                    </label>
                    <div className="flex items-center space-x-1.5">
                      <input 
                        type="date" 
                        value={bomDateRange.start}
                        onChange={(e) => { setBomDateRange(prev => ({ ...prev, start: e.target.value })); setCurrentPage(1); }}
                        className={`w-full px-2 py-1.5 rounded-lg border text-[11px] ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'}`}
                      />
                      <span className="text-slate-400 text-xs">to</span>
                      <input 
                        type="date" 
                        value={bomDateRange.end}
                        onChange={(e) => { setBomDateRange(prev => ({ ...prev, end: e.target.value })); setCurrentPage(1); }}
                        className={`w-full px-2 py-1.5 rounded-lg border text-[11px] ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'}`}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block font-semibold mb-1 text-slate-600 dark:text-zinc-400">Pre MP Date (A - B)</label>
                    <div className="flex items-center space-x-1">
                      <input 
                        type="date" 
                        value={preMpDateRange.start}
                        onChange={(e) => { setPreMpDateRange(prev => ({ ...prev, start: e.target.value })); setCurrentPage(1); }}
                        className={`w-full px-1.5 py-1.5 rounded-lg border text-[10px] ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'}`}
                      />
                      <input 
                        type="date" 
                        value={preMpDateRange.end}
                        onChange={(e) => { setPreMpDateRange(prev => ({ ...prev, end: e.target.value })); setCurrentPage(1); }}
                        className={`w-full px-1.5 py-1.5 rounded-lg border text-[10px] ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'}`}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block font-semibold mb-1 text-slate-600 dark:text-zinc-400">MP Date (A - B)</label>
                    <div className="flex items-center space-x-1">
                      <input 
                        type="date" 
                        value={mpDateRange.start}
                        onChange={(e) => { setMpDateRange(prev => ({ ...prev, start: e.target.value })); setCurrentPage(1); }}
                        className={`w-full px-1.5 py-1.5 rounded-lg border text-[10px] ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'}`}
                      />
                      <input 
                        type="date" 
                        value={mpDateRange.end}
                        onChange={(e) => { setMpDateRange(prev => ({ ...prev, end: e.target.value })); setCurrentPage(1); }}
                        className={`w-full px-1.5 py-1.5 rounded-lg border text-[10px] ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'}`}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block font-semibold mb-1 text-slate-600 dark:text-zinc-400">PV Status</label>
                    <select 
                      value={selectedPvStatus}
                      onChange={(e) => { setSelectedPvStatus(e.target.value); setCurrentPage(1); }}
                      className={`w-full px-3 py-1.5 rounded-lg border ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'}`}
                    >
                      <option value="ALL">All PV Status</option>
                      <option value="PV1">PV1</option>
                      <option value="PV2">PV2</option>
                      <option value="PV3">PV3</option>
                      <option value="MP Ready">MP Ready</option>
                    </select>
                  </div>
                </div>
              )}
            </div>

            {/* Main Table Body */}
            <div className={`overflow-x-auto transition-all duration-300 ${showBomSyncResult ? 'max-h-[220px]' : 'max-h-[520px]'}`}>
              <table className="w-full text-left border-collapse text-xs whitespace-nowrap">
                <thead>
                  <tr className={`border-b text-[11px] font-semibold uppercase tracking-wider sticky top-0 z-20 ${isDarkMode ? 'border-zinc-800 text-zinc-400 bg-zinc-900' : 'border-slate-100 text-slate-500 bg-slate-50'}`}>
                    <th className="py-3 px-3 sticky left-0 z-30 bg-inherit shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)] w-10 text-center">
                      <input 
                        type="checkbox" 
                        checked={paginatedRecords.length > 0 && paginatedRecords.every(r => selectedRowIds.includes(r.id))}
                        onChange={handleSelectAllCurrentPage}
                        className="rounded border-slate-300 text-[#C8102E] focus:ring-[#C8102E] cursor-pointer"
                        title="Select/Deselect all on this page"
                      />
                    </th>
                    <th className="py-3 px-4 sticky left-10 z-30 bg-inherit shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)]">Model Name</th>
                    
                    {/* NEW COLUMN: WO */}
                    <th className="py-3 px-3 font-bold text-slate-800 dark:text-zinc-200 border-l border-slate-200 dark:border-zinc-800 bg-slate-100/50 dark:bg-zinc-800/50">WO</th>

                    <th className="py-3 px-3 text-[#C8102E] bg-red-50/30 dark:bg-red-950/20">MARS Suffix</th>
                    <th className="py-3 px-3 bg-red-50/30 dark:bg-red-950/20">Region</th>
                    <th className="py-3 px-3 bg-red-50/30 dark:bg-red-950/20">Series</th>
                    <th className="py-3 px-3 bg-red-50/30 dark:bg-red-950/20">Inch</th>
                    <th className="py-3 px-3 bg-red-50/30 dark:bg-red-950/20">SoC</th>
                    <th className="py-3 px-3 bg-red-50/30 dark:bg-red-950/20">Dev Model</th>
                    <th className="py-3 px-3 bg-red-50/30 dark:bg-red-950/20">Initial Model</th>
                    <th className="py-3 px-3 bg-red-50/30 dark:bg-red-950/20">BOM Release Date</th>
                    <th className="py-3 px-3 bg-red-50/30 dark:bg-red-950/20">Latest ECO</th>
                    <th className="py-3 px-3 bg-red-50/30 dark:bg-red-950/20">Subsidiary List</th>
                    <th className="py-3 px-3 bg-red-50/30 dark:bg-red-950/20">BOM Sync</th>

                    <th className="py-3 px-3 text-blue-600 dark:text-blue-400 border-l-2 border-slate-300 dark:border-zinc-700 bg-blue-50/30 dark:bg-blue-950/20">GMES Suffix</th>
                    <th className="py-3 px-3 bg-blue-50/30 dark:bg-blue-950/20">Pre MP Date</th>
                    <th className="py-3 px-3 bg-blue-50/30 dark:bg-blue-950/20">MP Date</th>
                    <th className="py-3 px-3 bg-blue-50/30 dark:bg-blue-950/20">Running Status</th>
                    <th className="py-3 px-3 bg-blue-50/30 dark:bg-blue-950/20">PV Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-zinc-800">
                  {paginatedRecords.length === 0 ? (
                    <tr>
                      <td colSpan={19} className="py-12 text-center text-slate-400">No matching model telemetry records found for the selected filters.</td>
                    </tr>
                  ) : (
                    paginatedRecords.map((row) => {
                      const isRowSelected = activeRowDetail?.id === row.id;
                      const isChecked = selectedRowIds.includes(row.id);
                      const isRowLoading = (isCrosschecking || isPullingGmes || isPullingMars) && isChecked;

                      return (
                        <tr 
                          key={row.id} 
                          onClick={() => { if (!isRowLoading) setActiveRowDetail(row); }}
                          className={`cursor-pointer transition-colors relative ${
                            isRowLoading ? 'bg-red-50/30 dark:bg-red-950/20 opacity-75' :
                            isRowSelected 
                              ? 'bg-red-50 dark:bg-red-950/30' 
                              : isDarkMode ? 'hover:bg-zinc-800/50' : 'hover:bg-slate-50'
                          }`}
                        >
                          <td className="py-3 px-3 sticky left-0 z-10 bg-white dark:bg-zinc-900 text-center" onClick={(e) => e.stopPropagation()}>
                            <input 
                              type="checkbox" 
                              checked={isChecked}
                              onChange={(e) => handleToggleRowSelect(row.id, e as any)}
                              className="rounded border-slate-300 text-[#C8102E] focus:ring-[#C8102E] cursor-pointer"
                            />
                          </td>
                          <td className="py-3 px-4 font-mono font-bold text-slate-900 dark:text-white sticky left-10 z-10 bg-white dark:bg-zinc-900 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)] flex items-center space-x-1.5">
                            {isRowLoading ? <Loader2 className="w-3.5 h-3.5 text-[#C8102E] animate-spin" /> : <Layers className="w-3.5 h-3.5 text-[#C8102E]" />}
                            <span>{row.modelName}</span>
                          </td>

                          {/* WO Cell */}
                          <td className="py-3 px-3 font-mono font-semibold text-slate-800 dark:text-zinc-200 border-l border-slate-100 dark:border-zinc-800 bg-slate-50/30 dark:bg-zinc-800/30">
                            {row.workOrder}
                          </td>

                          <td className="py-3 px-3 font-mono text-[#C8102E] bg-red-50/10 dark:bg-red-950/5">{row.marsSuffix}</td>
                          <td className="py-3 px-3 font-medium bg-red-50/10 dark:bg-red-950/5">{row.region}</td>
                          <td className="py-3 px-3 bg-red-50/10 dark:bg-red-950/5">{row.series}</td>
                          <td className="py-3 px-3 bg-red-50/10 dark:bg-red-950/5">{row.inch}</td>
                          <td className="py-3 px-3 bg-red-50/10 dark:bg-red-950/5">{row.soc}</td>
                          <td className="py-3 px-3 font-mono text-slate-500 bg-red-50/10 dark:bg-red-950/5">{row.devModel}</td>
                          <td className="py-3 px-3 font-mono text-slate-500 bg-red-50/10 dark:bg-red-950/5">{row.initialModel}</td>
                          <td className="py-3 px-3 font-mono bg-red-50/10 dark:bg-red-950/5">{row.bomReleaseDate}</td>
                          <td className="py-3 px-3 font-mono text-amber-600 bg-red-50/10 dark:bg-red-950/5">{row.latestEco}</td>
                          <td className="py-3 px-3 font-medium text-slate-700 dark:text-zinc-300 bg-red-50/10 dark:bg-red-950/5">{row.subsidiaryList}</td>
                          <td className="py-3 px-3 bg-red-50/10 dark:bg-red-950/5">{getMarsSyncBadge(row.bomSync)}</td>

                          <td className="py-3 px-3 font-mono text-blue-600 dark:text-blue-400 border-l-2 border-slate-200 dark:border-zinc-700 bg-blue-50/10 dark:bg-red-950/5">{row.gmesSuffix}</td>
                          <td className="py-3 px-3 font-mono bg-blue-50/10 dark:bg-red-950/5">{row.preMpDate}</td>
                          <td className="py-3 px-3 font-mono bg-blue-50/10 dark:bg-red-950/5">{row.mpDate}</td>
                          <td className="py-3 px-3 bg-blue-50/10 dark:bg-red-950/5">{getGmesStatusBadge(row.runningStatus)}</td>
                          <td className="py-3 px-3 bg-blue-50/10 dark:bg-red-950/5">{getPvStatusBadge(row.pvStatus)}</td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Footer */}
            <div className="p-3 border-t border-slate-100 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-900/50 flex items-center justify-between text-xs text-slate-500 shrink-0">
              <span>Showing page {currentPage} of {totalPages || 1} ({filteredRecords.length} filtered rows - 10 per page)</span>
              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => setCurrentPage(p => Math.max(p - 1, 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-zinc-700 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors flex items-center space-x-1"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>
                <span className="px-3 font-mono font-semibold">{currentPage} / {totalPages || 1}</span>
                <button 
                  onClick={() => setCurrentPage(p => Math.min(p + 1, totalPages))}
                  disabled={currentPage >= totalPages}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-zinc-700 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors flex items-center space-x-1"
                >
                  <span>Next</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

          </div>

          {/* Sync Diagnostic Report Container */}
          {showBomSyncResult && activeRowDetail && (
            <div className={`p-5 rounded-2xl border border-red-300 dark:border-red-900 shadow-lg animate-fadeIn shrink-0 ${
              isDarkMode ? 'bg-zinc-900/95 text-zinc-100' : 'bg-red-50/90 text-slate-900'
            }`}>
              <div className="flex items-center justify-between border-b border-red-200 dark:border-red-900/50 pb-3 mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-3.5 h-3.5 rounded-full bg-[#C8102E]" />
                  <h3 className="font-bold text-xs uppercase tracking-wider text-[#C8102E]">
                    Sync Diagnostic Report — <span className="font-mono">{activeRowDetail.modelName}</span>
                  </h3>
                  
                  {/* Tab Navigation */}
                  <div className="flex items-center space-x-1 bg-white dark:bg-zinc-800 p-1 rounded-xl border border-red-200 dark:border-zinc-700 ml-4">
                    <button 
                      onClick={() => setActiveDiagnosticTab('schedule')}
                      className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-all ${
                        activeDiagnosticTab === 'schedule' 
                          ? 'bg-[#C8102E] text-white shadow-xs' 
                          : 'text-slate-600 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-zinc-700'
                      }`}
                    >
                      Schedule View
                    </button>
                    <button 
                      onClick={() => setActiveDiagnosticTab('result')}
                      className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-all ${
                        activeDiagnosticTab === 'result' 
                          ? 'bg-[#C8102E] text-white shadow-xs' 
                          : 'text-slate-600 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-zinc-700'
                      }`}
                    >
                      Result Tab (Crosschecking Details)
                    </button>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button 
                    onClick={() => handleExcelExport(activeRowDetail.modelName)}
                    className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-[11px] transition-all flex items-center space-x-1.5 shadow-xs"
                    title="Export diagnostic report to Excel (CSV)"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export Excel</span>
                  </button>

                  <button 
                    onClick={() => setShowBomSyncResult(false)}
                    className="p-1.5 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/40 text-slate-500 transition-colors"
                    title="Close Diagnostic Report"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Conditional Tab Content */}
              {activeDiagnosticTab === 'schedule' ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 text-xs animate-fadeIn">
                  
                  {/* Left Column */}
                  <div className={`p-4 rounded-xl border flex flex-col space-y-4 ${isDarkMode ? 'bg-zinc-800/60 border-zinc-700' : 'bg-white border-slate-200'}`}>
                    <h4 className="font-bold text-[#C8102E] uppercase tracking-wider flex items-center space-x-1.5 border-b pb-2 border-red-100 dark:border-zinc-700">
                      <Database className="w-4 h-4" />
                      <span>Target Master & Subsidiary Schedule</span>
                    </h4>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <span className="text-[10px] text-slate-400 block">Target / MP Name</span>
                        <span className="font-mono font-semibold">{activeRowDetail.syncDetails.targetSystem}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 block">BOM Release Date</span>
                        <span className="font-mono font-semibold">{activeRowDetail.bomReleaseDate}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 block">Sync Status</span>
                        <div className="mt-0.5">{getMarsSyncBadge(activeRowDetail.bomSync)}</div>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 block">Latest ECO</span>
                        <span className="font-mono font-bold text-amber-600">{activeRowDetail.latestEco}</span>
                      </div>
                    </div>

                    <div className="space-y-1.5 pt-2 border-t border-slate-100 dark:border-zinc-700">
                      <span className="text-[11px] font-semibold text-slate-600 dark:text-zinc-300 block">List of Subsidiaries (Pre-MP & MP Schedule - 7 Nodes):</span>
                      <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-zinc-700 max-h-48">
                        <table className="w-full text-left text-[11px]">
                          <thead>
                            <tr className={`border-b sticky top-0 ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-400' : 'bg-slate-100 border-slate-200 text-slate-600'}`}>
                              <th className="p-2">Subsidiary Name</th>
                              <th className="p-2">Pre MP</th>
                              <th className="p-2">MP Date</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100 dark:divide-zinc-700">
                            {activeRowDetail.subsidiaries.map((sub, idx) => (
                              <tr key={idx} className={isDarkMode ? 'hover:bg-zinc-700/40' : 'hover:bg-slate-50'}>
                                <td className="p-2 font-medium truncate max-w-[130px]">{sub.name}</td>
                                <td className="p-2 font-mono">{sub.preMpDate}</td>
                                <td className="p-2 font-mono">{sub.mpDate}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  {/* Right Column */}
                  <div className={`p-4 rounded-xl border flex flex-col space-y-4 ${isDarkMode ? 'bg-zinc-800/60 border-zinc-700' : 'bg-white border-slate-200'}`}>
                    <h4 className="font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider flex items-center space-x-1.5 border-b pb-2 border-blue-100 dark:border-zinc-700">
                      <Info className="w-4 h-4" />
                      <span>Subsidiary BOM MP Diagnostic Results</span>
                    </h4>

                    <div className="space-y-1.5 flex-1 overflow-x-auto max-h-48">
                      <div className="rounded-lg border border-slate-200 dark:border-zinc-700 overflow-hidden">
                        <table className="w-full text-left text-[11px]">
                          <thead>
                            <tr className={`border-b sticky top-0 ${isDarkMode ? 'bg-zinc-900 border-zinc-700 text-zinc-400' : 'bg-slate-100 border-slate-200 text-slate-600'}`}>
                              <th className="p-2">BOM MP Target</th>
                              <th className="p-2">Result</th>
                              <th className="p-2">Compare Note</th>
                              <th className="p-2">Notification</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100 dark:divide-zinc-700">
                            {activeRowDetail.subsidiaries.map((sub, idx) => {
                              const isNgOrCheck = sub.result === 'DISCREPANCY' || sub.compareNote.startsWith('NG') || sub.compareNote.includes('Check');
                              return (
                                <tr key={idx} className={isDarkMode ? 'hover:bg-zinc-700/40' : 'hover:bg-slate-50'}>
                                  <td className="p-2 font-mono font-semibold">{activeRowDetail.syncDetails.targetSystem}</td>
                                  <td className="p-2">
                                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                      sub.result === 'MATCHED' ? 'bg-emerald-100 text-emerald-800' : sub.result === 'PENDING' ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
                                    }`}>
                                      {sub.result}
                                    </span>
                                  </td>
                                  <td className="p-2 text-slate-500 dark:text-zinc-400 truncate max-w-[120px]" title={sub.compareNote}>{sub.compareNote}</td>
                                  <td className="p-2">
                                    <div className="flex items-center space-x-1.5">
                                      {isNgOrCheck ? (
                                        <button 
                                          onClick={() => {
                                            setActiveDiscrepancyData({ record: activeRowDetail, subsidiary: sub });
                                            setSidebarViewMode('discrepancy');
                                            setIsSidebarOpen(true);
                                          }}
                                          className="relative flex h-4 w-4 items-center justify-center cursor-pointer group"
                                          title="Click to view action report in left sidebar"
                                        >
                                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                                          <AlertTriangle className="relative inline-flex rounded-full h-4 w-4 text-rose-600 group-hover:scale-125 transition-transform" />
                                        </button>
                                      ) : (
                                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                                      )}
                                      <span className="truncate max-w-[110px] text-slate-600 dark:text-zinc-300" title={sub.notification}>{sub.notification}</span>
                                    </div>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-zinc-950 text-zinc-200 font-mono text-[11px] space-y-1">
                      <span className="text-[10px] text-zinc-400 block uppercase tracking-wider">Gateway Stream Logs:</span>
                      {activeRowDetail.syncDetails.logs.map((log, idx) => (
                        <div key={idx} className="flex items-start space-x-1.5">
                          <span className="text-[#C8102E]">›</span>
                          <span className="break-all">{log}</span>
                        </div>
                      ))}
                    </div>

                  </div>

                </div>
              ) : (
                /* Result Tab View */
                <div className={`p-4 rounded-xl border flex flex-col space-y-3 animate-fadeIn ${isDarkMode ? 'bg-zinc-800/80 border-zinc-700' : 'bg-white border-slate-200'}`}>
                  
                  <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-zinc-700">
                    <div>
                      <h4 className="font-bold text-xs text-[#C8102E] flex items-center space-x-2">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Crosschecking Results Matrix & Discrepancy Breakdown</span>
                      </h4>
                      <p className="text-[10px] text-slate-500 dark:text-zinc-400">Model: {activeRowDetail.modelName}</p>
                    </div>

                    <div className="flex items-center space-x-2">
                      <div className="px-3 py-1 rounded-xl bg-rose-600 text-white font-bold text-xs flex items-center space-x-1.5 shadow-xs">
                        <AlertTriangle className="w-3.5 h-3.5 animate-pulse" />
                        <span>NG / Discrepancies Present: {activeRowDetail.subsidiaries.filter(s => s.result === 'DISCREPANCY').length}</span>
                      </div>
                      <div className="px-3 py-1 rounded-xl bg-emerald-600 text-white font-bold text-xs flex items-center space-x-1.5 shadow-xs">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Matched: {activeRowDetail.subsidiaries.filter(s => s.result === 'MATCHED').length}</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 overflow-y-auto max-h-[300px] pr-1">
                    {activeRowDetail.subsidiaries.map((sub, sIdx) => {
                      const isOk = sub.result === 'MATCHED';
                      return (
                        <div 
                          key={sIdx}
                          className={`p-3 rounded-xl border transition-all ${
                            isOk 
                              ? isDarkMode ? 'bg-zinc-900/40 border-zinc-700' : 'bg-emerald-50/20 border-emerald-200' 
                              : isDarkMode ? 'bg-red-950/20 border-red-900' : 'bg-rose-50/60 border-rose-300'
                          }`}
                        >
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-1.5">
                            <div className="flex items-center space-x-2">
                              <span className={`w-5 h-5 rounded-md flex items-center justify-center font-bold text-[10px] ${
                                isOk ? 'bg-emerald-500 text-white' : 'bg-rose-600 text-white animate-pulse'
                              }`}>
                                {sIdx + 1}
                              </span>
                              <h5 className="font-bold text-xs font-mono text-slate-900 dark:text-white">{sub.name}</h5>
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className="text-[10px] font-mono text-slate-400">Pre-MP: {sub.preMpDate}</span>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                isOk ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                              }`}>
                                {sub.result}
                              </span>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] pt-1.5 border-t border-slate-200/60 dark:border-zinc-700">
                            <div>
                              <span className="text-slate-400 block text-[10px]">Compare Note:</span>
                              <strong className={isOk ? 'text-emerald-700 dark:text-emerald-400' : 'text-rose-600 font-bold'}>{sub.compareNote}</strong>
                            </div>
                            <div>
                              <span className="text-slate-400 block text-[10px]">Notification Status:</span>
                              <div className="flex items-center space-x-1.5 mt-0.5">
                                {!isOk && (
                                  <button 
                                    onClick={() => {
                                      setActiveDiscrepancyData({ record: activeRowDetail, subsidiary: sub });
                                      setSidebarViewMode('discrepancy');
                                      setIsSidebarOpen(true);
                                    }}
                                    className="px-2 py-0.5 rounded bg-rose-600 text-white text-[10px] font-bold hover:bg-rose-700 transition-colors"
                                  >
                                    View Action Report
                                  </button>
                                )}
                                <span className="text-slate-600 dark:text-zinc-300">{sub.notification}</span>
                              </div>
                            </div>
                          </div>

                          {sub.discrepantParts.length > 0 && (
                            <div className="mt-2 pt-1.5 border-t border-rose-200 dark:border-red-900/50 space-y-1.5">
                              <span className="text-[10px] font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400 block">Flagged Discrepant Parts ({sub.discrepantParts.length}):</span>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                {sub.discrepantParts.map((dp, dIdx) => (
                                  <div key={dIdx} className="p-2 rounded-lg bg-white dark:bg-zinc-900 border border-rose-200 dark:border-red-900 space-y-1 font-mono text-[10px]">
                                    <div className="flex justify-between font-bold text-rose-600">
                                      <span>{dp.partNumber}</span>
                                      <span>{dp.discrepancyType}</span>
                                    </div>
                                    <div>{dp.partName}</div>
                                    <div className="text-slate-400 flex justify-between pt-1 border-t border-slate-100 dark:border-zinc-800">
                                      <span>MARS: {dp.marsVersion}</span>
                                      <span>GMES: {dp.gmesVersion}</span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

            </div>
          )}

        </div>

      </main>

      {/* Right Slide-Over Details Bar */}
      <aside className={`fixed top-0 right-0 h-full w-96 border-l shadow-2xl z-50 transition-all duration-300 ease-in-out flex flex-col ${activeRowDetail ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0 pointer-events-none'} ${isDarkMode ? 'bg-zinc-900 border-zinc-800 text-zinc-100' : 'bg-white border-slate-200 text-slate-900'}`}>
        {activeRowDetail && (
          <div className="flex flex-col h-full">
            
            <div className="p-5 border-b border-slate-100 dark:border-zinc-800 flex items-center justify-between bg-red-50/50 dark:bg-red-950/20">
              <div className="flex items-center space-x-2.5">
                <div className="w-3.5 h-3.5 rounded-full bg-[#C8102E]" />
                <div>
                  <h3 className="font-bold text-sm tracking-tight font-mono">{activeRowDetail.modelName}</h3>
                  <span className="text-[10px] text-[#C8102E] font-semibold">MARS & GMES Master Telemetry</span>
                </div>
              </div>
              <button 
                onClick={() => setActiveRowDetail(null)}
                className="p-2 rounded-xl hover:bg-red-100 dark:hover:bg-red-900/40 text-slate-500 transition-colors"
                title="Close sidebar"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-6 text-xs overscroll-contain">
              
              <div className="space-y-3">
                <h4 className="font-bold text-[#C8102E] uppercase tracking-wider flex items-center space-x-1.5 border-b pb-1 border-red-100 dark:border-red-950">
                  <Database className="w-3.5 h-3.5" />
                  <span>MARS Module Attributes</span>
                </h4>
                <div className="grid grid-cols-2 gap-3 bg-slate-50 dark:bg-zinc-800/50 p-3 rounded-xl">
                  <div>
                    <span className="text-[10px] text-slate-400 block">Work Order</span>
                    <span className="font-mono font-semibold">{activeRowDetail.workOrder}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Suffix</span>
                    <span className="font-mono font-semibold">{activeRowDetail.marsSuffix}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Region</span>
                    <span className="font-semibold">{activeRowDetail.region}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Series</span>
                    <span>{activeRowDetail.series}</span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-[10px] text-slate-400 block">Display Size</span>
                    <span>{activeRowDetail.inch}</span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-[10px] text-slate-400 block">Processor (SoC)</span>
                    <span className="font-medium">{activeRowDetail.soc}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Dev Model</span>
                    <span className="font-mono">{activeRowDetail.devModel}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Initial Model</span>
                    <span className="font-mono">{activeRowDetail.initialModel}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">BOM Release Date</span>
                    <span className="font-mono">{activeRowDetail.bomReleaseDate}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Latest ECO</span>
                    <span className="font-mono text-amber-600">{activeRowDetail.latestEco}</span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-[10px] text-slate-400 block">Subsidiary List</span>
                    <span className="font-semibold">{activeRowDetail.subsidiaryList}</span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-[10px] text-slate-400 block">BOM Sync Status</span>
                    <div className="mt-1 flex items-center justify-between">
                      {getMarsSyncBadge(activeRowDetail.bomSync)}
                      
                      <button 
                        onClick={() => {
                          setShowBomSyncResult(!showBomSyncResult);
                          setActiveDiagnosticTab('schedule');
                        }}
                        className="px-3 py-1.5 rounded-xl bg-red-50 dark:bg-red-950/40 text-[#C8102E] hover:bg-red-100 font-semibold text-[11px] transition-all flex items-center space-x-1.5 border border-red-200 dark:border-red-900 shadow-xs"
                      >
                        <span>BOM Sync Result</span>
                        {showBomSyncResult ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="font-bold text-blue-600 uppercase tracking-wider flex items-center space-x-1.5 border-b pb-1 border-blue-100 dark:border-blue-950">
                  <Info className="w-3.5 h-3.5" />
                  <span>GMES Module Attributes</span>
                </h4>
                <div className="grid grid-cols-2 gap-3 bg-blue-50/40 dark:bg-blue-950/20 p-3 rounded-xl">
                  <div>
                    <span className="text-[10px] text-slate-400 block">GMES Suffix</span>
                    <span className="font-mono font-semibold text-blue-600">{activeRowDetail.gmesSuffix}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">PV Status</span>
                    <div className="mt-0.5">{getPvStatusBadge(activeRowDetail.pvStatus)}</div>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Pre MP Date</span>
                    <span className="font-mono">{activeRowDetail.preMpDate}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">MP Date</span>
                    <span className="font-mono">{activeRowDetail.mpDate}</span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-[10px] text-slate-400 block">Running Status</span>
                    <div className="mt-1">{getGmesStatusBadge(activeRowDetail.runningStatus)}</div>
                  </div>
                </div>
              </div>

            </div>

            <div className="p-4 border-t border-slate-100 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-900 flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-mono">ID: {activeRowDetail.id}</span>
              <button 
                onClick={() => handleExcelExport(activeRowDetail.modelName)}
                className="px-4 py-2 bg-[#C8102E] hover:bg-red-700 text-white rounded-xl font-semibold shadow-md shadow-red-500/20 transition-all flex items-center space-x-1.5 text-xs"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                <span>Export Telemetry</span>
              </button>
            </div>

          </div>
        )}
      </aside>

    </div>
  );
}