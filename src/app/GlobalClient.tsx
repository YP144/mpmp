'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import { updateUrlParams } from '@/lib/urlState';
import {
  Server,
  Clock,
  RotateCcw,
  TrendingUp,
  ChevronUp,
  Users,
  Boxes,
  Wrench,
  Search,
  Download,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  SlidersHorizontal,
  Calendar,
  Filter,
  X,
  FileText,
  AlertTriangle,
  ClockAlert,
  XCircle,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ShieldAlert,
  Cpu,
  Bell,
  ChevronDown,
  Eye,
  EyeOff,
  Sparkles,
  LayoutGrid,
  BarChart2,
  PieChart as PieChartIcon,
  Table as TableIcon,
  WifiOff,
  ExternalLink,
  ArrowUpDown,
  ArrowDownWideNarrow,
  Regex,
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts';

import { ToolItem, SummaryMatrixRow, TabKey } from '@/types/dashboard';
import {
  fetchTeamMembers,
  fetchBomItems,
  fetchSummaryTeam,
  DynamicTableResponse,
} from '@/app/actions';

const initialTools: ToolItem[] = [
  { id: 1, toolId: 'TL-ATSC-01', name: 'ATSC 3.0 Signal Generator Rig', platform: 'ATSC', calibDate: '2026-08-14', location: 'Lab Alpha (US)', status: 'Calibrated' },
  { id: 2, toolId: 'TL-DVB-02', name: 'DVB-T2 RF Modulation Test Bench', platform: 'DVB', calibDate: '2026-09-01', location: 'Lab Bravo (DE)', status: 'Calibrated' },
  { id: 3, toolId: 'TL-OLED-03', name: 'OLED Luminance & Colorimetry Jig', platform: 'OLED', calibDate: '2026-05-10', location: 'Cleanroom 2 (KR)', status: 'Pending Audit' },
  { id: 4, toolId: 'TL-ATSC-04', name: 'ATSC Broadcast Stream Emulator', platform: 'ATSC', calibDate: '2026-09-12', location: 'Lab Alpha (US)', status: 'Calibrated' },
  { id: 5, toolId: 'TL-DVB-05', name: 'DVB Transport Stream Analyzer', platform: 'DVB', calibDate: '2026-07-22', location: 'Lab Bravo (DE)', status: 'Calibrated' },
  { id: 6, toolId: 'TL-OLED-06', name: 'High-Voltage OLED Burn-in Tester', platform: 'OLED', calibDate: '2026-01-15', location: 'Cleanroom 1 (KR)', status: 'Expired' },
];

const ngResultAnalysisData = [
  { name: 'Structure', value: 35, color: '#C8102E' },
  { name: 'Ben Compare', value: 25, color: '#991B1B' },
  { name: 'Tool Option', value: 22, color: '#E11D48' },
  { name: 'Operation Plan', value: 18, color: '#F43F5E' },
];

const generateBomCrosscheckedData = () => {
  const distribution = [32, 45, 58, 42, 45];
  const result = [];
  const today = new Date();

  for (let i = 0; i < 5; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + i);
    const formattedDate = date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });

    result.push({
      date: formattedDate,
      value: distribution[i],
    });
  }

  return result;
};

const bomCrosscheckedData = generateBomCrosscheckedData();

const mpxSkippedModelsMock = [
  { model: 'DVB-LEGACY-1', team: 'DVB', checkedDate: '2026-09-28', reason: 'Deprecation flag set in HW BOM registry' },
  { model: 'OLED-FLEX-PRO', team: 'OLED', checkedDate: '2026-09-30', reason: 'Missing Gerber schema v3.2 dependencies' },
  { model: 'ATSC-MINI-RX', team: 'ATSC', checkedDate: '2026-10-01', reason: 'BOM lock override requested by Lead HW PIC' },
  { model: 'DVB-IPTV-BOX', team: 'DVB', checkedDate: '2026-10-03', reason: 'EOL component replacement in progress' },
];

const HIDDEN_TEAM_COLUMNS = [
  'id', 'emp_no', 'empno', 'email', 'gender', 'level', 'grade', 'position', 'dept_code', 'deptcode', 'nickname', 'auth',
];

type QuickStatusFilter = 'ALL' | 'URGENT' | 'NO_INITIAL' | 'NOT_VERIFIED' | 'OVERDUE' | 'NG' | 'OK' | 'CHECK';

const YEAR_CODE_MAP: Record<string, string> = {
  '25Y': '2024',
  '26Y': '2025',
  '27Y': '2026',
};

const getDefaultYearCode = (): string => {
  const currentYear = new Date().getFullYear();
  const matchedEntry = Object.entries(YEAR_CODE_MAP).find(([, yr]) => Number(yr) === currentYear);
  return matchedEntry ? matchedEntry[0] : '27Y';
};

const STYLED_STATUS_COLUMNS = [
  'result', 'structure', 'bencomp', 'hwtool', 'substitute_check', 'substitutecheck', 'tool_option', 'tooloption', 'operation_plan', 'operationplan',
];

const DETAILED_RESULT_KEYS = [
  { key: 'structure', label: 'Structure' },
  { key: 'benComp', possibleKeys: ['benComp', 'bencomp'], label: 'BenComp' },
  { key: 'hwTool', possibleKeys: ['hwTool', 'hwtool'], label: 'HW Tool' },
  { key: 'substitute_check', possibleKeys: ['substitute_check', 'substitutecheck', 'substitute'], label: 'Substitute Check' },
  { key: 'tool_option', possibleKeys: ['tool_option', 'tooloption'], label: 'Tool Option' },
  { key: 'operation_plan', possibleKeys: ['operation_plan', 'operationplan'], label: 'Operation Plan' },
];

const getFieldValue = (row: Record<string, any>, possibleKeys: string[], defaultValue: any = 'N/A') => {
  if (!row) return defaultValue;
  const rowKeys = Object.keys(row);
  for (const pKey of possibleKeys) {
    const cleanPKey = pKey.toLowerCase().replace(/[^a-z0-9]/g, '');
    const foundKey = rowKeys.find(
      (rk) => rk.toLowerCase().replace(/[^a-z0-9]/g, '') === cleanPKey
    );
    if (foundKey && row[foundKey] !== undefined && row[foundKey] !== null && String(row[foundKey]).trim() !== '') {
      return row[foundKey];
    }
  }
  return defaultValue;
};

const normalizeTeamName = (rawTeam: any): string => {
  if (!rawTeam || String(rawTeam).trim() === '' || String(rawTeam).trim() === '-') return 'OTHERS';

  const items = String(rawTeam)
    .split(/[,;\s]+/)
    .map((item) => item.trim().toUpperCase())
    .filter((item) => item.length > 0);

  if (items.length === 0) return 'OTHERS';

  const knownTeams = ['ATSC', 'DVB', 'OLED'];
  const frequency: Record<string, number> = {};

  for (const item of items) {
    let matchedTeam = 'OTHERS';
    for (const known of knownTeams) {
      if (item.includes(known)) {
        matchedTeam = known;
        break;
      }
    }
    frequency[matchedTeam] = (frequency[matchedTeam] || 0) + 1;
  }

  let highestTeam = 'OTHERS';
  let maxCount = 0;

  for (const [team, count] of Object.entries(frequency)) {
    if (count > maxCount) {
      maxCount = count;
      highestTeam = team;
    }
  }

  return highestTeam;
};

const renderStyledCellData = (colKey: string, rawVal: any) => {
  const normalizedKey = colKey.toLowerCase().replace(/_/g, '');
  const isTargetCol = STYLED_STATUS_COLUMNS.includes(normalizedKey);

  if (!isTargetCol) {
    return rawVal !== null && rawVal !== undefined ? String(rawVal) : '-';
  }

  if (rawVal === null || rawVal === undefined || String(rawVal).trim() === '' || String(rawVal).trim() === '-') {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-stone-100 text-stone-500 border border-stone-300">
        NULL
      </span>
    );
  }

  const strVal = String(rawVal).trim().toUpperCase();

  if (strVal.includes('OK')) {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-500">
        {String(rawVal)}
      </span>
    );
  }

  if (strVal.includes('NG')) {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 border border-red-500">
        {String(rawVal)}
      </span>
    );
  }

  if (strVal.includes('CHECK')) {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-500">
        {String(rawVal)}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-stone-100 text-stone-600 border border-stone-300">
      {String(rawVal)}
    </span>
  );
};

const BOM_COLUMN_GROUPS: Record<string, { label: string; columns: string[] }> = {
  model_info: {
    label: 'Model & Architecture Details',
    columns: ['mp model', 'dev model', 'initial model', 'model_subsidiary', 'model_region', 'model_country', 'model_soc', 'HW', 'inch', 'series', 'plant'],
  },
  engineering_status: {
    label: 'Result & Engineering Status',
    columns: ['result', 'engineer_confimation', 'engineer_checkouter', 'structure'],
  },
  hardware_tools: {
    label: 'Hardware Tools & Options',
    columns: ['hwTool', 'tool_option', 'substitute_check', 'benComp'],
  },
  operations_planning: {
    label: 'Operations & Planning',
    columns: ['operation_plan', 'compare_note', 'additional_remark'],
  },
  bom_verification: {
    label: 'BOM Verification & Tracking',
    columns: ['bom_release_date', 'bom_last_checker', 'bom_delay_count', 'bom_delay_status', 'bom_team'],
  },
  metadata: {
    label: 'Metadata & Timestamp',
    columns: ['version', 'year', 'time_info', 'model_circuit_pic'],
  },
};

const GLOBAL_TABS: (TabKey | 'analytics')[] = ['team', 'bom', 'analytics'];
const DEFAULT_GLOBAL_TAB: TabKey = 'bom';

function parseGlobalTab(value: string | null): TabKey | 'analytics' {
  return GLOBAL_TABS.find((t) => t === value) ?? DEFAULT_GLOBAL_TAB;
}

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const [utcTime, setUtcTime] = useState<string>('--:--:--');
  const [matrixFilter, setMatrixFilter] = useState<string>('ALL');
  const [isMatrixOpen, setIsMatrixOpen] = useState<boolean>(true);
  const [currentTab, setCurrentTab] = useState<TabKey | 'analytics'>(() => parseGlobalTab(searchParams.get('tab')));

  const [teamState, setTeamState] = useState<DynamicTableResponse>({ columns: [], rows: [] });
  const [bomState, setBomState] = useState<DynamicTableResponse>({ columns: [], rows: [] });
  const [summaryTeamState, setSummaryTeamState] = useState<DynamicTableResponse>({ columns: [], rows: [] });
  const [toolData, setToolData] = useState<ToolItem[]>(initialTools);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [selectedRow, setSelectedRow] = useState<Record<string, any> | null>(null);
  const [showExceptionLog, setShowExceptionLog] = useState<boolean>(false);

  const [visibleGroups, setVisibleGroups] = useState<Record<string, boolean>>({
    model_info: true,
    engineering_status: true,
    hardware_tools: true,
    operations_planning: true,
    bom_verification: true,
    metadata: true,
  });
  const [isGroupDropdownOpen, setIsGroupDropdownOpen] = useState<boolean>(false);

  const [yearFilter, setYearFilter] = useState<string>(() => (currentTab === 'team' ? 'ALL' : getDefaultYearCode()));

  useEffect(() => {
    updateUrlParams({ tab: currentTab === DEFAULT_GLOBAL_TAB ? null : currentTab });
  }, [currentTab]);

  const getRowUrlKey = (row: Record<string, any> | null, tab: TabKey | 'analytics'): string => {
    if (!row) return '';
    if (tab === 'bom') return String(getFieldValue(row, ['mp model', 'mp_model', 'mpModel'], '') ?? '').trim();
    const firstColumn = tab === 'team' ? teamState.columns[0] : undefined;
    return firstColumn ? String(row[firstColumn] ?? '').trim() : '';
  };

  const pendingRowKey = React.useRef<string | null>(searchParams.get('row'));

  useEffect(() => {
    const key = pendingRowKey.current;
    if (!key || isLoading) return;
    pendingRowKey.current = null;
    const rows = currentTab === 'team' ? teamState.rows : currentTab === 'bom' ? bomState.rows : [];
    const found = rows.find((r) => getRowUrlKey(r, currentTab) === key);
    if (found) setSelectedRow(found);
    else updateUrlParams({ row: null });
  }, [isLoading, currentTab, teamState, bomState]);

  useEffect(() => {
    if (pendingRowKey.current) return;
    updateUrlParams({ row: getRowUrlKey(selectedRow, currentTab) || null });
  }, [selectedRow, currentTab]);

  const [teamFilter, setTeamFilter] = useState<string>('ALL');
  const [partFilter, setPartFilter] = useState<string>('ALL');
  const [inchFilter, setInchFilter] = useState<string>('ALL');
  const [regionFilter, setRegionFilter] = useState<string>('ALL');
  const [seriesFilter, setSeriesFilter] = useState<string>('ALL');
  const [plantFilter, setPlantFilter] = useState<string>('ALL');
  const [useRegexSearch, setUseRegexSearch] = useState<boolean>(false);

  const [isHwPartOnly, setIsHwPartOnly] = useState<boolean>(false);
  const [quickStatusFilter, setQuickStatusFilter] = useState<QuickStatusFilter>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [isLatestDateFirst, setIsLatestDateFirst] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(15);

  const [selectedAnalyticsYear, setSelectedAnalyticsYear] = useState<string>('26Y');
  const [selectedAnalyticsTeam, setSelectedAnalyticsTeam] = useState<string>('ATSC');
  const [showKpiCards, setShowKpiCards] = useState<boolean>(true);
  const [showOverdueList, setShowOverdueList] = useState<boolean>(true);
  const [showUrgentList, setShowUrgentList] = useState<boolean>(true);

  const [overdueSearch, setOverdueSearch] = useState<string>('');
  const [urgentSearch, setUrgentSearch] = useState<string>('');
  const [ngSearch, setNgSearch] = useState<string>('');

  const [analyticsSidebarOpen, setAnalyticsSidebarOpen] = useState<boolean>(false);
  const [analyticsSidebarType, setAnalyticsSidebarType] = useState<'NG_DETAILS' | 'ITEM_DETAILS' | 'SKIPPED_MODELS' | null>(null);
  const [selectedSidebarItem, setSelectedSidebarItem] = useState<any>(null);
  const [ngActiveTab, setNgActiveTab] = useState<'MODELS' | 'RESULTS'>('MODELS');
  const [ngTeamFilter, setNgTeamFilter] = useState<string>('ALL');

  const [systemResultViewMode, setSystemResultViewMode] = useState<'CHART' | 'TABLE'>('CHART');
  const [engineerConfirmationViewMode, setEngineerConfirmationViewMode] = useState<'CHART' | 'TABLE'>('CHART');

  const [ngResultViewMode, setNgResultViewMode] = useState<'KPI' | 'BAR'>('KPI');
  const [ngResultTeamScope, setNgResultTeamScope] = useState<string>('ALL');

  const [showMpxModal, setShowMpxModal] = useState<boolean>(false);

  const loadDatabaseData = async () => {
    setIsLoading(true);
    try {
      const [teamRes, bomRes, summaryTeamRes] = await Promise.all([
        fetchTeamMembers(),
        fetchBomItems(),
        fetchSummaryTeam(),
      ]);
      setTeamState(teamRes);
      setBomState(bomRes);
      setSummaryTeamState(summaryTeamRes);
    } catch (err) {
      console.error('Error fetching database tables:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDatabaseData();

    const timer = setInterval(() => {
      setUtcTime(new Date().toISOString().substring(11, 19));
    }, 1000);

    return () => {
      clearInterval(timer);
    };
  }, []);

  const handleRefresh = async () => {
    await loadDatabaseData();
    setToolData([...initialTools]);
  };

  const handleViewResultInNewTab = (row: Record<string, any>) => {
    const targetModel = getFieldValue(row, ['mp model', 'mp_model', 'targetModel', 'model', 'mpModel'], '');
    const devModel = getFieldValue(row, ['dev model', 'dev_model', 'devModel'], '');
    const initModel = getFieldValue(row, ['initial model', 'initial_model', 'initModel'], '');

    if (!targetModel || targetModel === 'N/A') {
      alert('Target model is missing for this row.');
      return;
    }

    const queryParams = new URLSearchParams();
    queryParams.set('targetModel', targetModel);
    if (devModel && devModel !== 'N/A') queryParams.set('devModel', devModel);
    if (initModel && initModel !== 'N/A') queryParams.set('initModel', initModel);

    window.open(`/viewResult?${queryParams.toString()}`, '_blank');
  };

  const filteredYearBomRows = useMemo(() => {
    let rows = bomState.rows || [];
    if (selectedAnalyticsYear !== 'ALL') {
      rows = rows.filter((r) => {
        const rowYear = String(getFieldValue(r, ['year', 'bom_year', 'model_year'], '')).trim().toLowerCase();
        const targetCode = selectedAnalyticsYear.toLowerCase();
        const targetYear = (YEAR_CODE_MAP[selectedAnalyticsYear] || '').toLowerCase();

        return rowYear === targetCode || rowYear === targetYear || rowYear.includes(targetCode) || (targetYear && rowYear.includes(targetYear));
      });
    }
    return rows;
  }, [bomState.rows, selectedAnalyticsYear]);

  const systemResultDistributionData = useMemo(() => {
    let ok = 0;
    let check = 0;
    let ng = 0;
    let skipped = 0;

    filteredYearBomRows.forEach((row) => {
      const val = String(getFieldValue(row, ['result'], '')).trim().toUpperCase();
      if (val === 'OK' || val.includes('OK')) {
        ok++;
      } else if (val === 'CHECK' || val.includes('CHECK')) {
        check++;
      } else if (val === 'NG' || val.includes('NG')) {
        ng++;
      } else if (val === 'SKIPPED' || val === 'SKIPPEDD' || val.includes('SKIP')) {
        skipped++;
      }
    });

    const total = ok + check + ng + skipped || 1;

    return {
      chartData: [
        { name: 'OK', value: ok, percentage: ((ok / total) * 100).toFixed(1), color: '#10B981', bgClass: 'bg-emerald-50 text-emerald-800 border-emerald-200' },
        { name: 'CHECK', value: check, percentage: ((check / total) * 100).toFixed(1), color: '#F59E0B', bgClass: 'bg-amber-50 text-amber-800 border-amber-200' },
        { name: 'NG', value: ng, percentage: ((ng / total) * 100).toFixed(1), color: '#C8102E', bgClass: 'bg-red-50 text-red-800 border-red-200' },
        { name: 'Skipped', value: skipped, percentage: ((skipped / total) * 100).toFixed(1), color: '#6B7280', bgClass: 'bg-stone-50 text-stone-800 border-stone-200' },
      ],
      totalRows: filteredYearBomRows.length,
    };
  }, [filteredYearBomRows]);

  const engineerConfirmationData = useMemo(() => {
    let ok = 0;
    let nullOrNone = 0;

    filteredYearBomRows.forEach((row) => {
      const val = getFieldValue(row, ['engineer_confirmation', 'engineer_confimation', 'engineerconfirmation', 'engineerconfimation'], null);
      if (val === null || val === undefined) {
        nullOrNone++;
      } else {
        const strVal = String(val).trim().toUpperCase();
        if (strVal === 'OK' || strVal.includes('OK')) {
          ok++;
        } else {
          nullOrNone++;
        }
      }
    });

    const total = filteredYearBomRows.length || 1;

    return {
      chartData: [
        { name: 'OK', value: ok, percentage: ((ok / total) * 100).toFixed(1), color: '#10B981', bgClass: 'bg-emerald-50 text-emerald-800 border-emerald-200' },
        { name: 'Null / None', value: nullOrNone, percentage: ((nullOrNone / total) * 100).toFixed(1), color: '#9CA3AF', bgClass: 'bg-stone-50 text-stone-800 border-stone-200' },
      ],
      totalRows: filteredYearBomRows.length,
    };
  }, [filteredYearBomRows]);

  const analyticMetrics = useMemo(() => {
    const rows = filteredYearBomRows;

    const overdueRows = rows.filter((r) => {
      const timeInfo = String(getFieldValue(r, ['time_info', 'timeinfo'], '')).toLowerCase();
      return timeInfo === 'overdue' || timeInfo === 'urgent';
    }).map((r, index) => ({
      id: `OV-DB-${index + 1}`,
      model: getFieldValue(r, ['mp model', 'dev model', 'model'], 'N/A'),
      date: getFieldValue(r, ['bom_release_date', 'date'], 'N/A'),
      result: getFieldValue(r, ['result'], 'N/A'),
      hwPic: getFieldValue(r, ['model_circuit_pic', 'bom_last_checker', 'hw_pic'], 'N/A'),
      team: normalizeTeamName(getFieldValue(r, ['bom_team', 'team'], 'N/A')),
      time_info: getFieldValue(r, ['time_info', 'timeinfo'], 'N/A'),
    }));

    if (selectedAnalyticsYear === '26Y') {
      return {
        totalBom: 11022,
        ngTotal: 5,
        completion: 9925,
        noInitial: 28,
        noDevelopment: 28,
        overdueRows,
        overdueCount: 1037,
        urgentCount: 60,
      };
    }

    const totalBom = rows.length;
    const ngTotal = rows.filter((r) => String(getFieldValue(r, ['result'], '')).toUpperCase().includes('NG')).length;
    const completion = rows.filter((r) => String(getFieldValue(r, ['time_info', 'timeinfo'], '')).toLowerCase() === 'completed').length;
    const noInitial = rows.filter((r) => {
      const val = getFieldValue(r, ['initial model', 'initial_model', 'initialmodel'], null);
      return val === null || val === undefined || String(val).trim() === '' || String(val).toLowerCase() === 'none' || String(val).toLowerCase() === 'null';
    }).length;
    const noDevelopment = rows.filter((r) => {
      const val = getFieldValue(r, ['dev model', 'dev_model', 'devmodel'], null);
      return val === null || val === undefined || String(val).trim() === '' || String(val).toLowerCase() === 'none' || String(val).toLowerCase() === 'null';
    }).length;

    const overdueCount = rows.filter((r) => String(getFieldValue(r, ['time_info', 'timeinfo'], '')).toLowerCase() === 'overdue').length;
    const urgentCount = rows.filter((r) => String(getFieldValue(r, ['time_info', 'timeinfo'], '')).toLowerCase() === 'urgent').length;

    return {
      totalBom,
      ngTotal,
      completion,
      noInitial,
      noDevelopment,
      overdueRows,
      overdueCount,
      urgentCount,
    };
  }, [filteredYearBomRows, selectedAnalyticsYear]);

  const ngDatabaseData = useMemo(() => {
    const ngRows = filteredYearBomRows.filter((r) => {
      const resultVal = getFieldValue(r, ['result'], '');
      return String(resultVal).toUpperCase().includes('NG');
    });

    const teamCounts: Record<string, number> = { DVB: 0, ATSC: 0, OLED: 0, OTHERS: 0 };

    const ngModels = ngRows.map((r, index) => {
      const rawTeam = getFieldValue(r, ['bom_team', 'team'], '');
      const team = normalizeTeamName(rawTeam);

      if (teamCounts[team] !== undefined) {
        teamCounts[team] += 1;
      } else {
        teamCounts['OTHERS'] += 1;
      }

      return {
        id: `NG-DB-${index + 1}`,
        model: getFieldValue(r, ['mp model', 'dev model', 'initial model', 'model'], 'N/A'),
        team: team,
        hwPic: getFieldValue(r, ['model_circuit_pic', 'bom_last_checker', 'engineer_checkouter'], 'N/A'),
        result: getFieldValue(r, ['result'], 'NG'),
        reason: getFieldValue(r, ['additional_remark', 'compare_note', 'structure'], 'System test check failed'),
      };
    });

    const totalNg = selectedAnalyticsYear === '26Y' ? 5 : ngRows.length;
    const teamBreakdown = [
      {
        name: 'DVB',
        count: teamCounts.DVB,
        percentage: totalNg > 0 ? ((teamCounts.DVB / totalNg) * 100).toFixed(1) : '0.0',
        bgClass: 'bg-red-50 border-red-100 text-red-900',
        textClass: 'text-red-600',
        subTextClass: 'text-red-500',
      },
      {
        name: 'ATSC',
        count: teamCounts.ATSC,
        percentage: totalNg > 0 ? ((teamCounts.ATSC / totalNg) * 100).toFixed(1) : '0.0',
        bgClass: 'bg-rose-50 border-rose-100 text-rose-900',
        textClass: 'text-rose-600',
        subTextClass: 'text-rose-500',
      },
      {
        name: 'OLED',
        count: teamCounts.OLED,
        percentage: totalNg > 0 ? ((teamCounts.OLED / totalNg) * 100).toFixed(1) : '0.0',
        bgClass: 'bg-pink-50 border-pink-100 text-pink-900',
        textClass: 'text-pink-600',
        subTextClass: 'text-pink-500',
      },
    ];

    return { ngModels, teamBreakdown };
  }, [filteredYearBomRows, selectedAnalyticsYear]);

  const filteredOverdue = useMemo(() => {
    return analyticMetrics.overdueRows.filter(
      (item) =>
        String(item.model).toLowerCase().includes(overdueSearch.toLowerCase()) ||
        String(item.hwPic).toLowerCase().includes(overdueSearch.toLowerCase()) ||
        String(item.result).toLowerCase().includes(overdueSearch.toLowerCase())
    );
  }, [analyticMetrics.overdueRows, overdueSearch]);

  const filteredUrgent = useMemo(() => {
    return analyticMetrics.overdueRows.filter(
      (item) => String(item.time_info).toLowerCase() === 'urgent' && (
        String(item.model).toLowerCase().includes(urgentSearch.toLowerCase()) ||
        String(item.hwPic).toLowerCase().includes(urgentSearch.toLowerCase()) ||
        String(item.result).toLowerCase().includes(urgentSearch.toLowerCase())
      )
    );
  }, [analyticMetrics.overdueRows, urgentSearch]);

  const handleToggleHideAll = () => {
    const isAnythingShown = showKpiCards || showOverdueList || showUrgentList;
    if (isAnythingShown) {
      setShowKpiCards(false);
      setShowOverdueList(false);
      setShowUrgentList(false);
    } else {
      setShowKpiCards(true);
      setShowOverdueList(true);
      setShowUrgentList(true);
    }
  };

  const openNgSidebar = () => {
    setAnalyticsSidebarType('NG_DETAILS');
    setSelectedSidebarItem(null);
    setAnalyticsSidebarOpen(true);
  };

  const openItemSidebar = (item: any, type: string) => {
    setAnalyticsSidebarType('ITEM_DETAILS');
    setSelectedSidebarItem({ ...item, itemCategory: type });
    setAnalyticsSidebarOpen(true);
  };

  const openSkippedSidebarFromMpx = () => {
    setShowMpxModal(false);
    setAnalyticsSidebarType('SKIPPED_MODELS');
    setSelectedSidebarItem(null);
    setAnalyticsSidebarOpen(true);
  };

  const dynamicSummaryRows = useMemo<SummaryMatrixRow[]>(() => {
    if (!summaryTeamState.rows || summaryTeamState.rows.length === 0) {
      return [];
    }

    return summaryTeamState.rows.map((row) => ({
      tech: String(
        getFieldValue(row, ['team_name', 'teamname', 'team', 'team_code', 'teamcode', 'dept_name', 'department', 'tech_standard', 'tech', 'technology', 'name'], 'Unknown Team')
      ) as "ATSC" | "DVB" | "OLED",
      totalBom: Number(getFieldValue(row, ['totalBom', 'total_bom', 'totalbom', 'bom_total', 'count_bom'], 0)),
      ng: Number(getFieldValue(row, ['ng', 'ng_count', 'total_ng', 'ng_total'], 0)),
      check: Number(getFieldValue(row, ['check', 'check_count', 'total_check', 'checking'], 0)),
      noInitial: Number(getFieldValue(row, ['noInitial', 'no_initial', 'noinitial', 'without_initial'], 0)),
      urgent: Number(getFieldValue(row, ['urgent', 'urgent_count', 'is_urgent'], 0)),
      overdue: Number(getFieldValue(row, ['overdue', 'overdue_count', 'is_overdue'], 0)),
      release: Number(getFieldValue(row, ['release', 'release_count', 'released', 'total_release'], 0)),
      working: Number(getFieldValue(row, ['working', 'working_count', 'in_progress'], 0)),
      delayCount: Number(getFieldValue(row, ['delayCount', 'delay_count', 'delaycount', 'delays'], 0)),
    }));
  }, [summaryTeamState]);

  const availableTeamFilters = useMemo(() => {
    const list = dynamicSummaryRows.map((r) => r.tech).filter((t) => t && (t as string) !== 'Unknown Team');
    return Array.from(new Set(list));
  }, [dynamicSummaryRows]);

  const uniqueTeams = useMemo(() => {
    const teamColKey = teamState.columns.find((col) =>
      ['team', 'team_name', 'bom_team', 'user_team'].includes(col.toLowerCase())
    );
    if (!teamColKey) return [];
    const values = teamState.rows
      .map((row) => String(row[teamColKey] ?? '').trim())
      .filter((v) => v !== '' && v !== '-');
    return Array.from(new Set(values));
  }, [teamState]);

  const uniqueParts = useMemo(() => {
    const partColKey = teamState.columns.find((col) =>
      ['part', 'part_name', 'part_type', 'user_part', 'component'].includes(col.toLowerCase())
    );
    if (!partColKey) return [];
    const values = teamState.rows
      .map((row) => String(row[partColKey] ?? '').trim())
      .filter((v) => v !== '' && v !== '-');
    return Array.from(new Set(values));
  }, [teamState]);

  const uniqueInches = useMemo(() => {
    if (!bomState.rows) return [];
    const values = bomState.rows
      .map((row) => String(getFieldValue(row, ['inch', 'model_inch', 'size'], '')).trim())
      .filter((v) => v !== '' && v !== 'N/A' && v !== '-');
    return Array.from(new Set(values)).sort();
  }, [bomState.rows]);

  const uniqueRegions = useMemo(() => {
    if (!bomState.rows) return [];
    const values = bomState.rows
      .map((row) => String(getFieldValue(row, ['model_region', 'region'], '')).trim())
      .filter((v) => v !== '' && v !== 'N/A' && v !== '-');
    return Array.from(new Set(values)).sort();
  }, [bomState.rows]);

  const uniqueSeries = useMemo(() => {
    if (!bomState.rows) return [];
    const values = bomState.rows
      .map((row) => String(getFieldValue(row, ['model_series', 'series'], '')).trim())
      .filter((v) => v !== '' && v !== 'N/A' && v !== '-');
    return Array.from(new Set(values)).sort();
  }, [bomState.rows]);

  const uniquePlants = useMemo(() => {
    if (!bomState.rows) return [];
    const values = bomState.rows
      .map((row) => String(getFieldValue(row, ['plant', 'factory', 'model_plant'], '')).trim())
      .filter((v) => v !== '' && v !== 'N/A' && v !== '-');
    return Array.from(new Set(values)).sort();
  }, [bomState.rows]);

  const activeDataset = useMemo(() => {
    if (currentTab === 'team') {
      const visibleTeamColumns = teamState.columns.filter((col) => {
        const normalizedCol = col.toLowerCase().replace(/_/g, '');
        return !HIDDEN_TEAM_COLUMNS.some(
          (hidden) => hidden.replace(/_/g, '') === normalizedCol
        );
      });
      return { columns: visibleTeamColumns, rows: teamState.rows };
    } else if (currentTab === 'bom') {
      const activeGroupCols = Object.entries(BOM_COLUMN_GROUPS)
        .filter(([groupKey]) => visibleGroups[groupKey])
        .flatMap(([, groupConfig]) => groupConfig.columns);

      const filteredBomColumns = bomState.columns.filter((col) =>
        activeGroupCols.some(
          (target) =>
            target.toLowerCase() === col.toLowerCase() ||
            target.replace(/_/g, ' ').toLowerCase() === col.replace(/_/g, ' ').toLowerCase()
        )
      );

      const finalColumns = filteredBomColumns.length > 0 ? filteredBomColumns : activeGroupCols;

      return { columns: finalColumns, rows: bomState.rows };
    } else if (currentTab === 'tool') {
      const toolColumns = initialTools.length > 0 ? Object.keys(initialTools[0]) : [];
      return { columns: toolColumns, rows: toolData as any[] };
    }
    return { columns: [], rows: [] };
  }, [currentTab, teamState, bomState, toolData, visibleGroups]);

  const checkRowStatus = (row: Record<string, any>, filterType: QuickStatusFilter): boolean => {
    if (filterType === 'ALL') return true;

    const isNonZeroNonNull = (val: any) => {
      if (val === null || val === undefined) return false;
      const strVal = String(val).trim().toUpperCase();
      return strVal !== '' && strVal !== '0' && strVal !== '-' && strVal !== 'NULL';
    };

    if (filterType === 'URGENT') {
      return Object.entries(row).some(([key, val]) => {
        const k = key.toLowerCase();
        return (k.includes('urgent') || k.includes('priority')) && (val === true || isNonZeroNonNull(val));
      });
    }

    if (filterType === 'NO_INITIAL') {
      return Object.entries(row).some(([key, val]) => {
        const k = key.toLowerCase().replace(/_/g, '');
        const strVal = String(val ?? '').trim().toUpperCase();
        return (k.includes('noinitial') || k.includes('initial')) && (strVal.includes('NO') || strVal === '0' || strVal === 'NULL' || strVal === '');
      });
    }

    if (filterType === 'NOT_VERIFIED') {
      return Object.entries(row).some(([key, val]) => {
        const k = key.toLowerCase().replace(/_/g, '');
        const strVal = String(val ?? '').trim().toUpperCase();
        return (k.includes('confirm') || k.includes('verify') || k.includes('checker')) && (strVal.includes('NOT') || strVal.includes('UNCHECK') || strVal.includes('CHECK') || strVal === '' || strVal === 'NULL');
      });
    }

    if (filterType === 'OVERDUE') {
      return Object.entries(row).some(([key, val]) => {
        const k = key.toLowerCase();
        return (k.includes('overdue') || k.includes('delay')) && isNonZeroNonNull(val);
      });
    }

    const primaryResultVal = getFieldValue(row, ['result', 'bom_result', 'status'], null);
    
    if (primaryResultVal !== null && primaryResultVal !== undefined) {
      const cleanResult = String(primaryResultVal).trim().toUpperCase();
      if (filterType === 'NG') return cleanResult === 'NG' || cleanResult.includes('NG');
      if (filterType === 'OK') return cleanResult === 'OK' || cleanResult.includes('OK');
      if (filterType === 'CHECK') return cleanResult === 'CHECK' || cleanResult.includes('CHECK');
    }

    if (filterType === 'NG') {
      return Object.entries(row).some(([key, val]) => {
        if (val === null || val === undefined) return false;
        const k = key.toLowerCase().replace(/_/g, '');
        const strVal = String(val).trim().toUpperCase();
        return (k === 'ng' || k === 'result' || k.includes('status')) && (strVal === 'NG' || strVal.includes('NG'));
      });
    }

    if (filterType === 'OK') {
      return Object.entries(row).some(([key, val]) => {
        if (val === null || val === undefined) return false;
        const k = key.toLowerCase().replace(/_/g, '');
        const strVal = String(val).trim().toUpperCase();
        return (k === 'ok' || k === 'result' || k.includes('status')) && (strVal === 'OK' || strVal.includes('OK'));
      });
    }

    if (filterType === 'CHECK') {
      return Object.entries(row).some(([key, val]) => {
        if (val === null || val === undefined) return false;
        const k = key.toLowerCase().replace(/_/g, '');
        const strVal = String(val).trim().toUpperCase();
        return (k === 'check' || k === 'result' || k.includes('status')) && (strVal === 'CHECK' || strVal.includes('CHECK'));
      });
    }

    return true;
  };

  const filteredRows = useMemo(() => {
    if (currentTab === 'analytics') return [];

    let rows = activeDataset.rows.filter((row) => {
      // Hide all rows with 'NG' in MP Master table when on 'bom' tab (unless strict NG filter is active)
      if (currentTab === 'bom' && quickStatusFilter !== 'NG') {
        const resultVal = String(getFieldValue(row, ['result'], '')).trim().toUpperCase();
        if (resultVal.includes('NG')) {
          return false;
        }
      }

      let matchYear = true;
      if (yearFilter !== 'ALL') {
        const yearKey = Object.keys(row).find((k) =>
          ['year', 'bom_year', 'model_year'].includes(k.toLowerCase())
        );
        if (yearKey) {
          const rowVal = String(row[yearKey] ?? '').trim().toLowerCase();
          const targetCode = yearFilter.toLowerCase();
          const targetYear = YEAR_CODE_MAP[yearFilter] || '';

          matchYear = rowVal === targetCode || rowVal === targetYear || rowVal.includes(targetCode) || rowVal.includes(targetYear);
        }
      }

      let matchTeam = true;
      let matchPart = true;
      let matchInch = true;
      let matchRegion = true;
      let matchSeries = true;
      let matchPlant = true;

      if (currentTab === 'bom') {
        if (inchFilter !== 'ALL') {
          const rowInch = String(getFieldValue(row, ['inch', 'model_inch', 'size'], '')).trim().toLowerCase();
          matchInch = rowInch === inchFilter.toLowerCase();
        }
        if (regionFilter !== 'ALL') {
          const rowRegion = String(getFieldValue(row, ['model_region', 'region'], '')).trim().toLowerCase();
          matchRegion = rowRegion === regionFilter.toLowerCase();
        }
        if (seriesFilter !== 'ALL') {
          const rowSeries = String(getFieldValue(row, ['model_series', 'series'], '')).trim().toLowerCase();
          matchSeries = rowSeries === seriesFilter.toLowerCase();
        }
        if (plantFilter !== 'ALL') {
          const rowPlant = String(getFieldValue(row, ['plant', 'factory', 'model_plant'], '')).trim().toLowerCase();
          matchPlant = rowPlant === plantFilter.toLowerCase();
        }
      }

      if (currentTab === 'team' && teamFilter !== 'ALL') {
        const teamKey = Object.keys(row).find((k) =>
          ['team', 'team_name', 'bom_team', 'user_team'].includes(k.toLowerCase())
        );
        if (teamKey) {
          matchTeam = String(row[teamKey] ?? '').trim().toLowerCase() === teamFilter.toLowerCase();
        }
      }

      const partKey = Object.keys(row).find((k) => {
        const normalized = k.toLowerCase().replace(/_/g, '');
        return normalized === 'part' || normalized === 'partname' || normalized === 'parttype' || normalized === 'userpart' || normalized === 'component';
      });

      if (partKey) {
        const partVal = String(row[partKey] ?? '').toLowerCase();
        const containsHwOrAsia = partVal.includes('hw') || partVal.includes('asia');

        if (currentTab === 'team' && isHwPartOnly && !containsHwOrAsia) {
          return false;
        }

        if (currentTab === 'team' && partFilter !== 'ALL') {
          matchPart = partVal === partFilter.toLowerCase();
        }
      }

      const matchStatusFilter = checkRowStatus(row, quickStatusFilter);

      let matchSearch = true;
      if (searchQuery.trim() !== '') {
        if (currentTab === 'bom' && useRegexSearch) {
          try {
            const re = new RegExp(searchQuery, 'i');
            matchSearch = Object.values(row).some((val) => re.test(String(val ?? '')));
          } catch (e) {
            matchSearch = Object.values(row).some((val) =>
              String(val ?? '').toLowerCase().includes(searchQuery.toLowerCase())
            );
          }
        } else {
          matchSearch = Object.values(row).some((val) =>
            String(val ?? '').toLowerCase().includes(searchQuery.toLowerCase())
          );
        }
      }

      let matchDateRange = true;
      if (currentTab === 'bom' && (startDate || endDate)) {
        const dateKey = Object.keys(row).find(
          (k) => k.toLowerCase().replace(/_/g, '') === 'bomreleasedate'
        );
        const rowDateValue = dateKey ? row[dateKey] : null;

        if (rowDateValue) {
          const rowTimestamp = new Date(rowDateValue).getTime();
          const startTimestamp = startDate ? new Date(startDate).getTime() : -Infinity;
          const endTimestamp = endDate ? new Date(endDate).setHours(23, 59, 59, 999) : Infinity;

          matchDateRange = rowTimestamp >= startTimestamp && rowTimestamp <= endTimestamp;
        } else {
          matchDateRange = false;
        }
      }

      return matchYear && matchTeam && matchPart && matchInch && matchRegion && matchSeries && matchPlant && matchStatusFilter && matchSearch && matchDateRange;
    });

    // If 'NG Only' filter is active, return an empty array to show no rows
    if (currentTab === 'bom' && quickStatusFilter === 'NG') {
      return [];
    }

    if (currentTab === 'bom' && isLatestDateFirst) {
      rows = [...rows].sort((a, b) => {
        const dateValA = getFieldValue(a, ['bom_release_date', 'release_date', 'date'], '');
        const dateValB = getFieldValue(b, ['bom_release_date', 'release_date', 'date'], '');

        const timeA = dateValA && dateValA !== 'N/A' ? new Date(dateValA).getTime() : 0;
        const timeB = dateValB && dateValB !== 'N/A' ? new Date(dateValB).getTime() : 0;

        return timeB - timeA;
      });
    }

    return rows;
  }, [currentTab, activeDataset, yearFilter, teamFilter, partFilter, inchFilter, regionFilter, seriesFilter, plantFilter, useRegexSearch, isHwPartOnly, quickStatusFilter, searchQuery, startDate, endDate, isLatestDateFirst]);

  const quickStatusCounts = useMemo(() => {
    let okCount = 0;
    let checkCount = 0;
    let ngCount = 0;

    activeDataset.rows.forEach((row) => {
      const resultVal = getFieldValue(row, ['result', 'bom_result', 'status'], '');
      const cleanVal = String(resultVal).trim().toUpperCase();

      if (cleanVal === 'OK' || cleanVal.includes('OK')) {
        okCount++;
      } else if (cleanVal === 'CHECK' || cleanVal.includes('CHECK')) {
        checkCount++;
      } else if (cleanVal === 'NG' || cleanVal.includes('NG')) {
        ngCount++;
      }
    });

    return { okCount, checkCount, ngCount };
  }, [activeDataset.rows]);

  const totalPages = Math.ceil(filteredRows.length / pageSize) || 1;

  const paginatedRows = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredRows.slice(start, start + pageSize);
  }, [filteredRows, currentPage, pageSize]);

  const visiblePageNumbers = useMemo(() => {
    const maxPagesToShow = 4;
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = startPage + maxPagesToShow - 1;

    if (endPage > totalPages) {
      endPage = totalPages;
      startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    const pages = [];
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    return pages;
  }, [currentPage, totalPages]);

  const handleTabSwitch = (tab: TabKey | 'analytics') => {
    setCurrentTab(tab);
    setSelectedRow(null);
    setShowExceptionLog(false);
    setSearchQuery('');
    setStartDate('');
    setEndDate('');
    setIsLatestDateFirst(false);
    setQuickStatusFilter('ALL');
    setIsHwPartOnly(false);
    setInchFilter('ALL');
    setRegionFilter('ALL');
    setSeriesFilter('ALL');
    setPlantFilter('ALL');
    setUseRegexSearch(false);
    setCurrentPage(1);
    if (tab === 'team') {
      setYearFilter('ALL');
      setTeamFilter('ALL');
      setPartFilter('ALL');
    } else if (tab !== 'analytics') {
      setYearFilter(getDefaultYearCode());
    }
  };

  const toggleQuickStatusFilter = (status: QuickStatusFilter) => {
    setQuickStatusFilter((prev) => (prev === status ? 'ALL' : status));
    setCurrentPage(1);
  };

  const toggleGroupVisibility = (groupKey: string) => {
    setVisibleGroups((prev) => ({
      ...prev,
      [groupKey]: !prev[groupKey],
    }));
  };

  const handleResetFilters = () => {
    setYearFilter(currentTab === 'team' ? 'ALL' : getDefaultYearCode());
    setTeamFilter('ALL');
    setPartFilter('ALL');
    setInchFilter('ALL');
    setRegionFilter('ALL');
    setSeriesFilter('ALL');
    setPlantFilter('ALL');
    setUseRegexSearch(false);
    setIsHwPartOnly(false);
    setQuickStatusFilter('ALL');
    setSearchQuery('');
    setStartDate('');
    setEndDate('');
    setIsLatestDateFirst(false);
    setCurrentPage(1);
  };

  const exportCSV = () => {
    if (filteredRows.length === 0) return;
    const keys = activeDataset.columns;
    let csvContent = 'data:text/csv;charset=utf-8,' + [keys.join(','), ...filteredRows.map((row) => keys.map((k) => `"${row[k] ?? ''}"`).join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Hardware_Dashboard_${currentTab.toUpperCase()}_Export.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="relative w-full h-full flex-1 overflow-x-hidden overflow-y-auto font-sans antialiased text-stone-800 bg-stone-100 flex flex-col box-border">
      {isLoading && (
        <div className="absolute inset-0 z-30 bg-stone-100/75 backdrop-blur-[2px]" role="status" aria-live="polite">
          <div className="sticky top-[30vh] flex justify-center px-4">
            <div className="w-full max-w-sm bg-white rounded-2xl shadow-xl border border-stone-200 overflow-hidden">
              <div className="h-1.5 bg-gradient-to-r from-[#6e0717] via-[#C8102E] to-[#D4AF37] animate-pulse"></div>
              <div className="p-6 flex flex-col items-center text-center">
                <div className="relative w-14 h-14 mb-4">
                  <div className="absolute inset-0 rounded-full border-4 border-stone-200"></div>
                  <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-[#C8102E] border-r-[#D4AF37] animate-spin"></div>
                  <TrendingUp className="absolute inset-0 m-auto w-5 h-5 text-[#C8102E]" />
                </div>
                <h3 className="text-sm font-extrabold uppercase tracking-wider text-[#6e0717]">Loading Global BOM Data</h3>
                <p className="mt-1.5 text-xs text-stone-500 leading-relaxed">
                  Fetching all BOM, team and summary records. This may take a moment, please wait...
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <header className="bg-gradient-to-r from-[#6e0717] via-[#C8102E] to-[#6e0717] text-white px-4 py-2 flex-none shadow-md border-b-2 border-[#D4AF37] flex items-center justify-between z-10 w-full">
        <div className="flex items-center space-x-3">
          <h1 className="text-xs sm:text-sm font-extrabold tracking-wider uppercase flex items-center gap-2">
            <TrendingUp className="text-[#D4AF37] w-4 h-4" /> Global Hardware Overview Dashboard
          </h1>
        </div>
        <div className="flex items-center space-x-3">
          <div className="hidden lg:flex items-center space-x-3 text-xs font-mono text-stone-200 border-r border-stone-500/30 pr-3">
            <span><Server className="text-[#D4AF37] inline w-3.5 h-3.5 mr-1" /> STATUS: <strong className="text-emerald-400">ONLINE</strong></span>
            <span><Clock className="text-[#D4AF37] inline w-3.5 h-3.5 mr-1" /> UTC: <strong>{utcTime}</strong></span>
          </div>
          <button onClick={handleRefresh} title="Refresh Dashboard" className="p-1.5 sm:px-2 sm:py-1.5 text-stone-200 hover:text-white bg-[#6e0717] hover:bg-[#C8102E] border border-[#D4AF37]/40 rounded-lg transition text-xs flex items-center gap-1.5 font-bold cursor-pointer">
            <RotateCcw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh Data</span>
          </button>
        </div>
      </header>

      <div className="relative flex-1 min-h-0 flex w-full">
      <div className="flex-1 flex flex-col p-3 space-y-3 overflow-y-auto min-w-0 max-w-full box-border">
        <section className="bg-white rounded-xl shadow-sm border border-[#EBD99A] flex-none overflow-hidden flex flex-col w-full">
          <div className="px-3 py-2 bg-stone-900 text-white flex flex-row items-center justify-between border-b border-[#D4AF37]/50 flex-wrap gap-2">
            <div className="flex items-center space-x-2">
              <TrendingUp className="text-[#D4AF37] w-4 h-4" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-stone-200">Hardware Dynamic Summary Matrix</h2>
              
              <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/50 text-amber-300 text-[10px] font-bold animate-pulse">
                <WifiOff className="w-3 h-3 text-amber-400" />
                <span>27Y Year</span>
              </div>

              <button onClick={() => setIsMatrixOpen(!isMatrixOpen)} className="text-[#D4AF37] hover:text-white focus:outline-none p-0.5 rounded transition-colors cursor-pointer">
                <ChevronUp className={`w-4 h-4 transition-transform duration-200 ${isMatrixOpen ? '' : 'rotate-180'}`} />
              </button>
            </div>
            <div className="flex items-center space-x-2">
              <label htmlFor="matrixDisplayFilter" className="text-[10px] font-semibold text-stone-400 uppercase tracking-wider">Display Filter:</label>
              <select id="matrixDisplayFilter" value={matrixFilter} onChange={(e) => setMatrixFilter(e.target.value)} className="text-xs bg-stone-800 text-[#D4AF37] border border-[#D4AF37]/40 rounded-md px-2 py-0.5 focus:outline-none font-medium">
                <option value="ALL">All Teams</option>
                {availableTeamFilters.map((teamItem) => (
                  <option key={teamItem} value={teamItem}>{teamItem} Only</option>
                ))}
              </select>
            </div>
          </div>

          {isMatrixOpen && (
            <div className="overflow-x-auto w-full">
              <table className="w-full text-left border-collapse min-w-[700px]">
                <thead className="bg-stone-50 border-b border-stone-200 text-[10px] sm:text-[11px] font-bold text-stone-600 uppercase tracking-wider">
                  <tr>
                    <th className="px-2.5 py-2 border-r border-stone-200 bg-[#FBF8EB] text-[#6e0717]">Team Name</th>
                    <th className="px-2.5 py-2 text-center">Total BOM</th>
                    <th className="px-2.5 py-2 text-center text-[#C8102E]">Total NG</th>
                    <th className="px-2.5 py-2 text-center text-amber-700">Total CHECK</th>
                    <th className="px-2.5 py-2 text-center text-stone-500">No Initial</th>
                    <th className="px-2.5 py-2 text-center">Urgent</th>
                    <th className="px-2.5 py-2 text-center">Overdue</th>
                    <th className="px-2.5 py-2 text-center text-emerald-700">Release</th>
                    <th className="px-2.5 py-2 text-center text-[#8C701B]">Working</th>
                    <th className="px-2.5 py-2 text-center">Delay Count</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100 text-xs font-medium text-stone-800">
                  {dynamicSummaryRows
                    .filter((row) => matrixFilter === 'ALL' || row.tech.toUpperCase() === matrixFilter.toUpperCase())
                    .map((row, idx) => (
                      <tr key={row.tech || idx} className="hover:bg-[#FDF2F4]/50 transition">
                        <td className="px-2.5 py-1.5 border-r border-stone-200 font-bold text-[#6e0717] bg-stone-50 flex items-center space-x-1.5">
                          <span className="w-2 h-2 rounded-full bg-[#C8102E]" />
                          <span>{row.tech}</span>
                        </td>
                        <td className="px-2.5 py-1.5 text-center font-mono font-semibold">{row.totalBom.toLocaleString()}</td>
                        <td className="px-2.5 py-1.5 text-center font-mono"><span className="px-1.5 py-0.5 bg-[#FDF2F4] text-[#C8102E] border border-[#F2A8B3] rounded-full text-[10px] font-bold">{row.ng}</span></td>
                        <td className="px-2.5 py-1.5 text-center font-mono text-amber-700 font-bold">{row.check}</td>
                        <td className="px-2.5 py-1.5 text-center font-mono text-stone-500">{row.noInitial}</td>
                        <td className="px-2.5 py-1.5 text-center font-mono"><span className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${row.urgent > 0 ? 'bg-amber-100 text-amber-900' : 'bg-stone-100 text-stone-600'}`}>{row.urgent}</span></td>
                        <td className="px-2.5 py-1.5 text-center font-mono"><span className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${row.overdue > 0 ? 'bg-[#FDF2F4] text-[#C8102E]' : 'bg-stone-100 text-stone-600'}`}>{row.overdue}</span></td>
                        <td className="px-2.5 py-1.5 text-center font-mono text-emerald-700 font-bold">{row.release.toLocaleString()}</td>
                        <td className="px-2.5 py-1.5 text-center font-mono text-[#8C701B] font-bold">{row.working}</td>
                        <td className="px-2.5 py-1.5 text-center font-mono"><span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${row.delayCount > 0 ? 'bg-[#FDF2F4] text-[#C8102E] border border-[#F2A8B3]' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'}`}>{row.delayCount}</span></td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <nav className="bg-white rounded-xl border border-[#EBD99A] shadow-sm px-3 flex-none w-full max-w-full">
          <div className="flex space-x-4 overflow-x-auto custom-scrollbar">
            <button onClick={() => handleTabSwitch('bom')} className={`py-2.5 text-xs transition flex items-center space-x-1.5 whitespace-nowrap cursor-pointer font-bold ${currentTab === 'bom' ? 'border-b-2 border-[#C8102E] text-[#C8102E] bg-[#FDF2F4]' : 'text-stone-600 border-b-2 border-transparent hover:text-[#C8102E]'}`}>
              <Boxes className="w-4 h-4" />
              <span>Master MP BOM</span>
            </button>
          
            <button onClick={() => handleTabSwitch('team')} className={`py-2.5 text-xs transition flex items-center space-x-1.5 whitespace-nowrap cursor-pointer font-bold ${currentTab === 'team' ? 'border-b-2 border-[#C8102E] text-[#C8102E] bg-[#FDF2F4]' : 'text-stone-600 border-b-2 border-transparent hover:text-[#C8102E]'}`}>
              <Users className="w-4 h-4" />
              <span>HW Team Members</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${currentTab === 'team' ? 'bg-[#FBF8EB] text-[#6e0717] border-[#EBD99A]' : 'bg-stone-100 text-stone-700 border-stone-200'}`}>{teamState.rows.length}</span>
            </button>

            <button onClick={() => handleTabSwitch('analytics')} className={`py-2.5 text-xs transition flex items-center space-x-1.5 whitespace-nowrap cursor-pointer font-bold ${currentTab === 'analytics' ? 'border-b-2 border-[#C8102E] text-[#C8102E] bg-[#FDF2F4]' : 'text-stone-600 border-b-2 border-transparent hover:text-[#C8102E]'}`}>
              <BarChart3 className="w-4 h-4" />
              <span>Analytic Dashboard</span>
            </button>
          </div>
        </nav>

        <div className="flex-1 min-h-[460px] flex flex-col overflow-hidden w-full max-w-full">
          <main className="flex-1 flex flex-col space-y-3 overflow-hidden min-w-0 max-w-full">
            {currentTab === 'analytics' ? (
              <div className="flex-1 overflow-y-auto space-y-4 pr-1 custom-scrollbar">
                <header className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-white p-3 rounded-2xl shadow-xs border border-red-100">
                  <div className="flex flex-wrap items-center gap-2">
                    <div className="relative">
                      <select
                        value={selectedAnalyticsYear}
                        onChange={(e) => setSelectedAnalyticsYear(e.target.value)}
                        className="appearance-none bg-red-50/60 border border-red-200 text-red-900 font-extrabold text-xs rounded-xl px-3 py-1.5 pr-7 hover:bg-red-100/70 focus:outline-none focus:ring-2 focus:ring-red-500 cursor-pointer"
                      >
                        <option value="ALL">Year: All</option>
                        <option value="25Y">Year: 25Y (2024)</option>
                        <option value="26Y">Year: 26Y (2025)</option>
                        <option value="27Y">Year: 27Y (2026)</option>
                      </select>
                      <ChevronDown className="w-3.5 h-3.5 text-red-600 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>

                    <div className="relative">
                      <select
                        value={selectedAnalyticsTeam}
                        onChange={(e) => setSelectedAnalyticsTeam(e.target.value)}
                        className="appearance-none bg-red-50/60 border border-red-200 text-red-900 font-extrabold text-xs rounded-xl px-3 py-1.5 pr-7 hover:bg-red-100/70 focus:outline-none focus:ring-2 focus:ring-red-500 cursor-pointer"
                      >
                        <option value="ATSC">Team: ATSC</option>
                        <option value="DVB">Team: DVB</option>
                        <option value="OLED">Team: OLED</option>
                      </select>
                      <ChevronDown className="w-3.5 h-3.5 text-red-600 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>

                    <button
                      onClick={() => setShowKpiCards(!showKpiCards)}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-700 font-bold text-xs border border-stone-200 transition cursor-pointer"
                    >
                      {showKpiCards ? <EyeOff className="w-3.5 h-3.5 text-stone-500" /> : <Eye className="w-3.5 h-3.5 text-stone-500" />}
                      <span>{showKpiCards ? 'Hide KPIs' : 'Show KPIs'}</span>
                    </button>

                    <button
                      onClick={handleToggleHideAll}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-[#C8102E] hover:bg-[#A00C23] text-white font-bold text-xs transition shadow-xs cursor-pointer"
                    >
                      {showKpiCards || showOverdueList || showUrgentList ? (
                        <>
                          <EyeOff className="w-3.5 h-3.5" />
                          <span>Hide All</span>
                        </>
                      ) : (
                        <>
                          <Eye className="w-3.5 h-3.5" />
                          <span>Show All</span>
                        </>
                      )}
                    </button>

                    <button
                      onClick={() => setShowMpxModal(true)}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-gradient-to-r from-[#6e0717] to-[#C8102E] text-white font-extrabold text-xs transition shadow-xs border border-[#D4AF37]/50 cursor-pointer"
                    >
                      <FileText className="w-3.5 h-3.5 text-[#D4AF37]" />
                      <span>MPX Report</span>
                    </button>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="relative flex-1 md:w-48">
                      <Search className="w-3.5 h-3.5 text-stone-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        placeholder="Search metrics..."
                        className="w-full bg-stone-50 border border-stone-200 rounded-xl pl-8 pr-2.5 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-red-500"
                      />
                    </div>
                    <button className="relative p-2 bg-stone-100 hover:bg-stone-200 rounded-xl transition border border-stone-200 cursor-pointer">
                      <Bell className="w-3.5 h-3.5 text-stone-600" />
                      <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-red-600 rounded-full animate-pulse"></span>
                    </button>
                  </div>
                </header>

                {showKpiCards && (
                  <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
                    <div className="bg-white p-3 rounded-2xl shadow-xs border border-red-100">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">Total BOMs</span>
                        <span className="text-[10px] font-extrabold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-full">+12.5%</span>
                      </div>
                      <div className="text-lg font-black text-stone-900">{analyticMetrics.totalBom.toLocaleString()}</div>
                      <p className="text-[10px] text-stone-400 mt-0.5">Active registered specs</p>
                    </div>

                    <div
                      onClick={openNgSidebar}
                      className="bg-white p-3 rounded-2xl shadow-xs border border-red-200 hover:border-red-400 transition cursor-pointer group relative overflow-hidden"
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-[10px] font-bold text-red-600 uppercase tracking-wider group-hover:underline">NG Total</span>
                        <span className="text-[10px] font-extrabold text-red-600 bg-red-50 px-1.5 py-0.5 rounded-full">+8.3%</span>
                      </div>
                      <div className="text-lg font-black text-red-600 flex items-center justify-between">
                        <span>{analyticMetrics.ngTotal.toLocaleString()}</span>
                        <ChevronRight className="w-4 h-4 text-red-400 group-hover:translate-x-1 transition-transform" />
                      </div>
                      <p className="text-[10px] text-red-500 font-semibold mt-0.5">Click for Detailed NG Analysis →</p>
                    </div>

                    <div className="bg-white p-3 rounded-2xl shadow-xs border border-red-100">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">Completion</span>
                        <span className="text-[10px] font-extrabold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-full">
                          {analyticMetrics.totalBom > 0 ? ((analyticMetrics.completion / analyticMetrics.totalBom) * 100).toFixed(1) : '0.0'}%
                        </span>
                      </div>
                      <div className="text-lg font-black text-stone-900">{analyticMetrics.completion.toLocaleString()}</div>
                      <p className="text-[10px] text-stone-400 mt-0.5">Completed items count</p>
                    </div>

                    <div className="bg-white p-3 rounded-2xl shadow-xs border border-red-100">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">No Initial</span>
                        <span className="text-[10px] font-extrabold text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded-full">
                          {analyticMetrics.totalBom > 0 ? ((analyticMetrics.noInitial / analyticMetrics.totalBom) * 100).toFixed(1) : '0.0'}%
                        </span>
                      </div>
                      <div className="text-lg font-black text-stone-900">{analyticMetrics.noInitial.toLocaleString()}</div>
                      <p className="text-[10px] text-stone-400 mt-0.5">Pending initial validation</p>
                    </div>

                    <div className="bg-white p-3 rounded-2xl shadow-xs border border-red-100">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">No Development</span>
                        <span className="text-[10px] font-extrabold text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded-full">
                          {analyticMetrics.totalBom > 0 ? ((analyticMetrics.noDevelopment / analyticMetrics.totalBom) * 100).toFixed(1) : '0.0'}%
                        </span>
                      </div>
                      <div className="text-lg font-black text-stone-900">{analyticMetrics.noDevelopment.toLocaleString()}</div>
                      <p className="text-[10px] text-stone-400 mt-0.5">Development unassigned</p>
                    </div>
                  </section>
                )}

                <section className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                  <div className="bg-white p-3 rounded-2xl shadow-xs border border-red-100 flex flex-col">
                    <div className="flex items-center justify-between mb-2 pb-2 border-b border-stone-100">
                      <div className="flex items-center gap-2">
                        <div className="p-1.5 bg-red-50 text-red-600 rounded-xl">
                          <Clock className="w-4 h-4" />
                        </div>
                        <div>
                          <h2 className="text-xs font-extrabold text-stone-900">Overdue Items</h2>
                          <p className="text-[10px] text-stone-400">Total Overdue KPI: <span className="text-red-600 font-bold">{analyticMetrics.overdueCount} Models</span></p>
                        </div>
                      </div>
                      <button
                        onClick={() => setShowOverdueList(!showOverdueList)}
                        className="flex items-center gap-1 px-2 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-600 font-bold text-[10px] transition cursor-pointer"
                      >
                        {showOverdueList ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                        <span>{showOverdueList ? 'Hide' : 'Show'}</span>
                      </button>
                    </div>

                    {showOverdueList && (
                      <>
                        <div className="relative mb-2">
                          <Search className="w-3 h-3 text-stone-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                          <input
                            type="text"
                            value={overdueSearch}
                            onChange={(e) => setOverdueSearch(e.target.value)}
                            placeholder="Search overdue..."
                            className="w-full bg-stone-50 border border-stone-200 rounded-lg pl-8 pr-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-red-500"
                          />
                        </div>

                        <div className="overflow-y-auto max-h-40 custom-scrollbar rounded-lg border border-stone-100">
                          <table className="w-full text-left text-xs">
                            <thead className="bg-stone-50 text-stone-500 font-bold sticky top-0 text-[10px] uppercase">
                              <tr>
                                <th className="p-1.5">Model</th>
                                <th className="p-1.5">Target Date</th>
                                <th className="p-1.5">Result</th>
                                <th className="p-1.5">HW PIC</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-stone-100">
                              {filteredOverdue.map((item) => (
                                <tr
                                  key={item.id}
                                  onClick={() => openItemSidebar(item, 'Overdue')}
                                  className="hover:bg-red-50/40 cursor-pointer transition-colors text-[11px]"
                                >
                                  <td className="p-1.5 font-bold text-stone-800">{item.model}</td>
                                  <td className="p-1.5 text-stone-500">{item.date}</td>
                                  <td className="p-1.5">
                                    <span className="px-1.5 py-0.5 rounded-full text-[9px] font-extrabold bg-red-100 text-red-700">
                                      {item.result}
                                    </span>
                                  </td>
                                  <td className="p-1.5 font-medium text-stone-600">{item.hwPic}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </>
                    )}
                  </div>

                  <div className="bg-white p-3 rounded-2xl shadow-xs border border-red-100 flex flex-col">
                    <div className="flex items-center justify-between mb-2 pb-2 border-b border-stone-100">
                      <div className="flex items-center gap-2">
                        <div className="p-1.5 bg-rose-50 text-rose-600 rounded-xl">
                          <AlertTriangle className="w-4 h-4" />
                        </div>
                        <div>
                          <h2 className="text-xs font-extrabold text-stone-900">Urgent Items</h2>
                          <p className="text-[10px] text-stone-400">Total Urgent KPI: <span className="text-rose-600 font-bold">{analyticMetrics.urgentCount} Models</span></p>
                        </div>
                      </div>
                      <button
                        onClick={() => setShowUrgentList(!showUrgentList)}
                        className="flex items-center gap-1 px-2 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-600 font-bold text-[10px] transition cursor-pointer"
                      >
                        {showUrgentList ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                        <span>{showUrgentList ? 'Hide' : 'Show'}</span>
                      </button>
                    </div>

                    {showUrgentList && (
                      <>
                        <div className="relative mb-2">
                          <Search className="w-3 h-3 text-stone-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                          <input
                            type="text"
                            value={urgentSearch}
                            onChange={(e) => setUrgentSearch(e.target.value)}
                            placeholder="Search urgent..."
                            className="w-full bg-stone-50 border border-stone-200 rounded-lg pl-8 pr-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-red-500"
                          />
                        </div>

                        <div className="overflow-y-auto max-h-40 custom-scrollbar rounded-lg border border-stone-100">
                          <table className="w-full text-left text-xs">
                            <thead className="bg-stone-50 text-stone-500 font-bold sticky top-0 text-[10px] uppercase">
                              <tr>
                                <th className="p-1.5">Model</th>
                                <th className="p-1.5">Target Date</th>
                                <th className="p-1.5">Result</th>
                                <th className="p-1.5">HW PIC</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-stone-100">
                              {filteredUrgent.map((item) => (
                                <tr
                                  key={item.id}
                                  onClick={() => openItemSidebar(item, 'Urgent')}
                                  className="hover:bg-rose-50/40 cursor-pointer transition-colors text-[11px]"
                                >
                                  <td className="p-1.5 font-bold text-stone-800">{item.model}</td>
                                  <td className="p-1.5 text-stone-500">{item.date}</td>
                                  <td className="p-1.5">
                                    <span className="px-1.5 py-0.5 rounded-full text-[9px] font-extrabold bg-rose-100 text-rose-700">
                                      {item.result}
                                    </span>
                                  </td>
                                  <td className="p-1.5 font-medium text-stone-600">{item.hwPic}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </>
                    )}
                  </div>
                </section>
              </div>
            ) : (
              <>
                <section className="bg-white p-2.5 rounded-xl shadow-sm border border-stone-200 flex flex-col space-y-2 flex-none w-full max-w-full">
                  <div className="flex flex-wrap items-center justify-between gap-2 w-full">
                    <div className="flex flex-wrap items-center gap-1.5 flex-1 min-w-[260px]">
                      <div className="flex items-center space-x-1 bg-stone-50 border border-stone-300 rounded-lg px-2 py-0.5">
                        <label htmlFor="yearFilterSelect" className="text-[10px] font-bold text-[#6e0717] uppercase tracking-wider">Year:</label>
                        <select id="yearFilterSelect" value={yearFilter} onChange={(e) => { setYearFilter(e.target.value); setCurrentPage(1); }} className="text-xs bg-white text-stone-800 font-bold border border-stone-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-[#C8102E]">
                          <option value="ALL">All Years</option>
                          <option value="25Y">25Y (2024)</option>
                          <option value="26Y">26Y (2025)</option>
                          <option value="27Y">27Y (2026)</option>
                        </select>
                      </div>

                      {currentTab === 'bom' && (
                        <>
                          <div className="flex items-center space-x-1 bg-stone-50 border border-stone-300 rounded-lg px-2 py-0.5">
                            <label htmlFor="inchFilterSelect" className="text-[10px] font-bold text-[#6e0717] uppercase tracking-wider">Inch:</label>
                            <select id="inchFilterSelect" value={inchFilter} onChange={(e) => { setInchFilter(e.target.value); setCurrentPage(1); }} className="text-xs bg-white text-stone-800 font-bold border border-stone-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-[#C8102E]">
                              <option value="ALL">All Inches</option>
                              {uniqueInches.map((inch) => (
                                <option key={inch} value={inch}>{inch}</option>
                              ))}
                            </select>
                          </div>

                          <div className="flex items-center space-x-1 bg-stone-50 border border-stone-300 rounded-lg px-2 py-0.5">
                            <label htmlFor="regionFilterSelect" className="text-[10px] font-bold text-[#6e0717] uppercase tracking-wider">Region:</label>
                            <select id="regionFilterSelect" value={regionFilter} onChange={(e) => { setRegionFilter(e.target.value); setCurrentPage(1); }} className="text-xs bg-white text-stone-800 font-bold border border-stone-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-[#C8102E]">
                              <option value="ALL">All Regions</option>
                              {uniqueRegions.map((region) => (
                                <option key={region} value={region}>{region}</option>
                              ))}
                            </select>
                          </div>

                          <div className="flex items-center space-x-1 bg-stone-50 border border-stone-300 rounded-lg px-2 py-0.5">
                            <label htmlFor="seriesFilterSelect" className="text-[10px] font-bold text-[#6e0717] uppercase tracking-wider">Series:</label>
                            <select id="seriesFilterSelect" value={seriesFilter} onChange={(e) => { setSeriesFilter(e.target.value); setCurrentPage(1); }} className="text-xs bg-white text-stone-800 font-bold border border-stone-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-[#C8102E]">
                              <option value="ALL">All Series</option>
                              {uniqueSeries.map((series) => (
                                <option key={series} value={series}>{series}</option>
                              ))}
                            </select>
                          </div>

                          <div className="flex items-center space-x-1 bg-stone-50 border border-stone-300 rounded-lg px-2 py-0.5">
                            <label htmlFor="plantFilterSelect" className="text-[10px] font-bold text-[#6e0717] uppercase tracking-wider">Plant:</label>
                            <select id="plantFilterSelect" value={plantFilter} onChange={(e) => { setPlantFilter(e.target.value); setCurrentPage(1); }} className="text-xs bg-white text-stone-800 font-bold border border-stone-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-[#C8102E]">
                              <option value="ALL">All Plants</option>
                              {uniquePlants.map((plant) => (
                                <option key={plant} value={plant}>{plant}</option>
                              ))}
                            </select>
                          </div>
                        </>
                      )}

                      {currentTab === 'team' && (
                        <>
                          <div className="flex items-center space-x-1 bg-stone-50 border border-stone-300 rounded-lg px-2 py-0.5">
                            <label htmlFor="teamFilterSelect" className="text-[10px] font-bold text-[#6e0717] uppercase tracking-wider">Team:</label>
                            <select id="teamFilterSelect" value={teamFilter} onChange={(e) => { setTeamFilter(e.target.value); setCurrentPage(1); }} className="text-xs bg-white text-stone-800 font-bold border border-stone-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-[#C8102E]">
                              <option value="ALL">All Teams</option>
                              {uniqueTeams.map((team) => (
                                <option key={team} value={team}>{team}</option>
                              ))}
                            </select>
                          </div>

                          <div className="flex items-center space-x-1 bg-stone-50 border border-stone-300 rounded-lg px-2 py-0.5">
                            <label htmlFor="partFilterSelect" className="text-[10px] font-bold text-[#6e0717] uppercase tracking-wider">Part:</label>
                            <select id="partFilterSelect" value={partFilter} onChange={(e) => { setPartFilter(e.target.value); setCurrentPage(1); }} className="text-xs bg-white text-stone-800 font-bold border border-stone-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-[#C8102E]">
                              <option value="ALL">All Parts</option>
                              {uniqueParts.map((part) => (
                                <option key={part} value={part}>{part}</option>
                              ))}
                            </select>
                          </div>
                        </>
                      )}

                      <div className="relative flex-1 min-w-[150px] max-w-xs flex items-center">
                        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[#8C701B] w-3.5 h-3.5" />
                        <input type="text" value={searchQuery} onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }} placeholder={currentTab === 'bom' && useRegexSearch ? "Search by Regex (e.g. ^OLED.*)" : "Search records..."} className="w-full pl-8 pr-12 py-1 text-xs bg-stone-50 border border-stone-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#C8102E] focus:bg-white transition" />
                        
                        {currentTab === 'bom' && (
                          <button
                            type="button"
                            onClick={() => { setUseRegexSearch(!useRegexSearch); setCurrentPage(1); }}
                            title="Toggle Regex Search (Master MP BOM only)"
                            className={`absolute right-1 px-1.5 py-0.5 rounded text-[10px] font-extrabold transition cursor-pointer ${useRegexSearch ? 'bg-[#C8102E] text-white' : 'bg-stone-200 hover:bg-stone-300 text-stone-700'}`}
                          >
                            .*
                          </button>
                        )}
                      </div>

                      {currentTab === 'bom' && (
                        <div className="flex items-center space-x-1.5 bg-stone-50 p-0.5 rounded-lg border border-stone-300 text-xs">
                          <div className="flex items-center space-x-1 pl-1">
                            <Calendar className="w-3.5 h-3.5 text-[#C8102E]" />
                            <span className="text-[10px] font-bold uppercase text-stone-500">Release Date:</span>
                            <input type="date" value={startDate} onChange={(e) => { setStartDate(e.target.value); setCurrentPage(1); }} className="bg-white border border-stone-300 rounded px-1 py-0.5 text-xs focus:outline-none" title="Start Date" />
                            <span className="text-stone-400 font-bold">to</span>
                            <input type="date" value={endDate} onChange={(e) => { setEndDate(e.target.value); setCurrentPage(1); }} className="bg-white border border-stone-300 rounded px-1 py-0.5 text-xs focus:outline-none" title="End Date" />
                          </div>

                          <button
                            onClick={() => {
                              setIsLatestDateFirst(!isLatestDateFirst);
                              setCurrentPage(1);
                            }}
                            title="Rearrange rows starting from the latest BOM release date"
                            className={`px-2 py-1 rounded text-xs font-bold transition flex items-center space-x-1 border cursor-pointer whitespace-nowrap ${
                              isLatestDateFirst
                                ? 'bg-[#C8102E] text-white border-[#9E0B22] shadow-xs'
                                : 'bg-white hover:bg-stone-100 text-stone-700 border-stone-300'
                            }`}
                          >
                            <ArrowDownWideNarrow className="w-3.5 h-3.5" />
                            <span>{isLatestDateFirst ? 'Latest Date First' : 'Order by Latest Date'}</span>
                          </button>
                        </div>
                      )}

                      <div className="inline-flex items-center space-x-1 bg-[#FBF8EB] border border-[#EBD99A] text-[#6e0717] px-2 py-0.5 rounded-lg text-xs font-bold shadow-xs">
                        <Filter className="w-3 h-3 text-[#D4AF37]" />
                        <span>Filtered:</span>
                        <span className="bg-[#6e0717] text-white px-1.5 py-0.5 rounded-full text-[10px] font-mono font-extrabold">{filteredRows.length}</span>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-1.5 relative">
                      {currentTab === 'bom' && (
                        <div className="relative">
                          <button onClick={() => setIsGroupDropdownOpen(!isGroupDropdownOpen)} className="inline-flex items-center space-x-1 bg-stone-100 hover:bg-stone-200 text-stone-800 text-xs font-semibold px-2.5 py-1 rounded-lg transition border border-stone-300 cursor-pointer">
                            <SlidersHorizontal className="w-3.5 h-3.5 text-[#6e0717]" />
                            <span>Column Topic Groups</span>
                          </button>

                          {isGroupDropdownOpen && (
                            <div className="absolute right-0 mt-2 w-72 bg-white border border-stone-300 rounded-xl shadow-xl z-30 p-2 space-y-1">
                              <div className="px-2 py-1 text-[10px] font-extrabold uppercase text-stone-400 tracking-wider">
                                Show/Hide Topic Groups
                              </div>
                              {Object.entries(BOM_COLUMN_GROUPS).map(([groupKey, groupConfig]) => {
                                const isChecked = visibleGroups[groupKey];
                                return (
                                  <label key={groupKey} className="flex items-center space-x-2 px-2 py-1.5 text-xs font-semibold rounded hover:bg-[#FBF8EB] cursor-pointer text-stone-700">
                                    <input type="checkbox" checked={isChecked} onChange={() => toggleGroupVisibility(groupKey)} className="rounded text-[#C8102E] focus:ring-[#C8102E] w-3.5 h-3.5 cursor-pointer" />
                                    <span>{groupConfig.label}</span>
                                  </label>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      )}

                      <button onClick={handleResetFilters} className="text-xs font-semibold text-stone-500 hover:text-[#C8102E] underline px-1 py-1 cursor-pointer">
                        Reset
                      </button>

                      <div className="h-4 w-px bg-stone-300 mx-0.5" />

                      <button onClick={exportCSV} className="inline-flex items-center space-x-1 bg-[#C8102E] hover:bg-[#A00C23] text-white text-xs font-semibold px-2.5 py-1 rounded-lg transition shadow-sm border border-[#D4AF37] cursor-pointer">
                        <Download className="w-3.5 h-3.5 text-[#FBF8EB]" />
                        <span>Export CSV</span>
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1.5 pt-1 border-t border-stone-100 overflow-x-auto w-full custom-scrollbar">
                    <span className="text-[10px] font-extrabold text-stone-400 uppercase tracking-wider whitespace-nowrap">Quick Status Filters:</span>

                    <button onClick={() => toggleQuickStatusFilter('OK')} className={`px-2 py-0.5 rounded-lg text-xs font-bold transition flex items-center space-x-1 border cursor-pointer whitespace-nowrap ${quickStatusFilter === 'OK' ? 'bg-emerald-600 text-white border-emerald-700 shadow-xs' : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border-emerald-300'}`}>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>OK Only</span>
                    </button>

                    <button onClick={() => toggleQuickStatusFilter('CHECK')} className={`px-2 py-0.5 rounded-lg text-xs font-bold transition flex items-center space-x-1 border cursor-pointer whitespace-nowrap ${quickStatusFilter === 'CHECK' ? 'bg-amber-500 text-white border-amber-600 shadow-xs' : 'bg-amber-50 hover:bg-amber-100 text-amber-800 border-amber-300'}`}>
                      <AlertCircle className="w-3.5 h-3.5" />
                      <span>CHECK Only</span>
                    </button>

                    <button onClick={() => toggleQuickStatusFilter('NG')} className={`px-2 py-0.5 rounded-lg text-xs font-bold transition flex items-center space-x-1 border cursor-pointer whitespace-nowrap ${quickStatusFilter === 'NG' ? 'bg-[#C8102E] text-white border-[#9E0B22] shadow-xs' : 'bg-[#FDF2F4] hover:bg-red-100 text-[#C8102E] border-[#F2A8B3]'}`}>
                      <XCircle className="w-3.5 h-3.5" />
                      <span>NG Only</span>
                    </button>

                    <button onClick={() => toggleQuickStatusFilter('URGENT')} className={`px-2 py-0.5 rounded-lg text-xs font-bold transition flex items-center space-x-1 border cursor-pointer whitespace-nowrap ${quickStatusFilter === 'URGENT' ? 'bg-rose-600 text-white border-rose-700 shadow-xs' : 'bg-rose-50 hover:bg-rose-100 text-rose-800 border-rose-300'}`}>
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span>Urgent Only</span>
                    </button>

                    <button onClick={() => toggleQuickStatusFilter('NO_INITIAL')} className={`px-2 py-0.5 rounded-lg text-xs font-bold transition flex items-center space-x-1 border cursor-pointer whitespace-nowrap ${quickStatusFilter === 'NO_INITIAL' ? 'bg-stone-700 text-white border-stone-800 shadow-xs' : 'bg-stone-100 hover:bg-stone-200 text-stone-700 border-stone-300'}`}>
                      <HelpCircle className="w-3.5 h-3.5" />
                      <span>No Initial</span>
                    </button>

                    <button onClick={() => toggleQuickStatusFilter('NOT_VERIFIED')} className={`px-2 py-0.5 rounded-lg text-xs font-bold transition flex items-center space-x-1 border cursor-pointer whitespace-nowrap ${quickStatusFilter === 'NOT_VERIFIED' ? 'bg-sky-600 text-white border-sky-700 shadow-xs' : 'bg-sky-50 hover:bg-sky-100 text-sky-800 border-sky-300'}`}>
                      <ShieldAlert className="w-3.5 h-3.5" />
                      <span>Not Verified</span>
                    </button>

                    <button onClick={() => toggleQuickStatusFilter('OVERDUE')} className={`px-2 py-0.5 rounded-lg text-xs font-bold transition flex items-center space-x-1 border cursor-pointer whitespace-nowrap ${quickStatusFilter === 'OVERDUE' ? 'bg-purple-600 text-white border-purple-700 shadow-xs' : 'bg-purple-50 hover:bg-purple-100 text-purple-800 border-purple-300'}`}>
                      <ClockAlert className="w-3.5 h-3.5" />
                      <span>Overdue</span>
                    </button>

                    {currentTab === 'team' && (
                      <button onClick={() => { setIsHwPartOnly(!isHwPartOnly); setCurrentPage(1); }} className={`px-2 py-0.5 rounded-lg text-xs font-bold transition flex items-center space-x-1 border cursor-pointer whitespace-nowrap ${isHwPartOnly ? 'bg-emerald-700 text-white border-emerald-800 shadow-xs' : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border-emerald-300'}`}>
                        <Cpu className="w-3.5 h-3.5" />
                        <span>HW Part Only</span>
                      </button>
                    )}

                    {(quickStatusFilter !== 'ALL' || (currentTab === 'team' && isHwPartOnly)) && (
                      <button onClick={handleResetFilters} className="text-xs text-stone-400 hover:text-stone-700 underline font-medium ml-1 cursor-pointer whitespace-nowrap">
                        Clear Status Filter
                      </button>
                    )}
                  </div>
                </section>

                <section className="bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden flex-1 flex flex-col min-h-[260px] w-full max-w-full">
                  <div className="flex-1 overflow-x-auto overflow-y-auto relative custom-scrollbar w-full max-w-full">
                    <table className="w-full text-left border-collapse min-w-full">
                      <thead className="sticky top-0 z-10 bg-stone-100 border-b border-stone-200 text-[10px] font-bold uppercase tracking-wider text-[#6e0717] shadow-sm">
                        <tr>
                          <th className="px-2.5 py-2 whitespace-nowrap bg-stone-100 text-center w-10 border-r border-stone-200">
                            #
                          </th>
                          {activeDataset.columns.map((colHeader) => (
                            <th key={colHeader} className="px-3 py-2 whitespace-nowrap bg-stone-100">
                              {colHeader.replace(/_/g, ' ')}
                            </th>
                          ))}
                        </tr>
                      </thead>

                      <tbody className="divide-y divide-stone-100 text-[11px] font-medium text-stone-700">
                        {paginatedRows.map((rowItem, rowIndex) => {
                          const absoluteRowIndex = (currentPage - 1) * pageSize + rowIndex + 1;
                          const isSelected = selectedRow === rowItem;

                          return (
                            <tr key={rowItem.id || rowIndex} onClick={() => setSelectedRow(rowItem)} className={`cursor-pointer transition ${isSelected ? 'bg-[#FDF2F4] ring-1 ring-[#C8102E]/30 font-semibold' : 'hover:bg-[#FBF8EB]/60'}`}>
                              <td className="px-2.5 py-1.5 whitespace-nowrap text-center font-mono font-bold text-stone-400 bg-stone-50/50 border-r border-stone-200 text-[10px]">
                                {absoluteRowIndex}
                              </td>
                              {activeDataset.columns.map((colKey) => (
                                <td key={colKey} className="px-3 py-1.5 whitespace-nowrap">
                                  {renderStyledCellData(colKey, rowItem[colKey])}
                                </td>
                              ))}
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>

                    {filteredRows.length === 0 && (
                      <div className="flex flex-col items-center justify-center p-8 text-center text-stone-400 bg-white/90">
                        <Boxes className="w-10 h-10 mb-2 text-[#D4AF37]" />
                        <p className="text-sm font-semibold text-stone-700">No matching records found</p>
                        <p className="text-xs text-stone-400">Ensure active filters or search terms match available database records.</p>
                      </div>
                    )}
                  </div>

                  <div className="bg-stone-50 px-3 py-2 border-t border-stone-200 flex items-center justify-between flex-none text-xs text-stone-600 flex-wrap gap-2 w-full">
                    <div className="flex items-center space-x-1.5">
                      <span>Show</span>
                      <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setCurrentPage(1); }} className="bg-white border border-stone-300 rounded px-1.5 py-0.5 text-xs focus:outline-none">
                        <option value={15}>15</option>
                        <option value={30}>30</option>
                        <option value={50}>50</option>
                        <option value={100}>100</option>
                      </select>
                      <span>entries</span>
                    </div>

                    <div className="font-medium text-stone-700 text-[11px]">
                      Showing {filteredRows.length === 0 ? 0 : (currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, filteredRows.length)} of {filteredRows.length} entries
                    </div>

                    <div className="flex items-center space-x-1">
                      <button onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))} disabled={currentPage === 1} title="Previous Page" className="p-1 border border-stone-300 rounded bg-white text-stone-600 hover:bg-[#FBF8EB] disabled:opacity-40 cursor-pointer">
                        <ChevronLeft className="w-3.5 h-3.5" />
                      </button>

                      {visiblePageNumbers.map((page) => (
                        <button key={page} onClick={() => setCurrentPage(page)} className={`w-6 h-6 border rounded text-xs font-bold transition flex items-center justify-center cursor-pointer ${page === currentPage ? 'bg-[#C8102E] border-[#C8102E] text-white shadow-sm' : 'border-stone-300 bg-white text-stone-700 hover:bg-[#FBF8EB]'}`}>
                          {page}
                        </button>
                      ))}

                      <button onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))} disabled={currentPage === totalPages || totalPages === 0} title="Next Page" className="p-1 border border-stone-300 rounded bg-white text-stone-600 hover:bg-[#FBF8EB] disabled:opacity-40 cursor-pointer">
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </section>
              </>
            )}
          </main>
        </div>
      </div>

      {selectedRow && currentTab !== 'analytics' && (
        <aside className="absolute xl:static inset-y-0 right-0 z-20 w-80 max-w-full bg-white border-l border-stone-200 shadow-2xl xl:shadow-none flex flex-col flex-none overflow-hidden">
          <div className="bg-gradient-to-r from-[#6e0717] to-[#C8102E] text-white px-3 py-2 flex items-center justify-between border-b border-[#D4AF37] flex-none">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-[#D4AF37]" />
              <h3 className="text-xs font-extrabold uppercase tracking-wider">Record Details</h3>
            </div>
            <button onClick={() => setSelectedRow(null)} className="p-1 hover:bg-white/20 rounded-lg transition text-white cursor-pointer">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-3 bg-stone-50/50 custom-scrollbar">
            <section className="bg-stone-900 text-white p-2.5 rounded-lg shadow-xs border border-stone-800 space-y-2">
              <div className="text-[10px] font-extrabold uppercase tracking-wider text-[#D4AF37] border-b border-stone-700 pb-1">
                Result & Engineer Confirmation
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <div className="mt-0.5">{renderStyledCellData('result', getFieldValue(selectedRow, ['result'], 'N/A'))}</div>
                </div>
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Engineer Conf.</span>
                  <div className="mt-0.5">{renderStyledCellData('engineer_confimation', getFieldValue(selectedRow, ['engineer_confimation', 'engineer_confirmation', 'engineerconfirmation'], 'N/A'))}</div>
                  <div className="mt-1 font-semibold text-stone-200 text-[10px]">
                    {getFieldValue(selectedRow, ['engineer_checkouter', 'checkouter'], 'N/A')}
                  </div>
                  <div className="text-[9px] text-stone-400 font-mono">
                    {getFieldValue(selectedRow, ['bom_checking_time', 'checking_time'], 'N/A')}
                  </div>
                </div>
              </div>
            </section>

            <section className="bg-white p-2.5 rounded-lg border border-stone-200 shadow-xs space-y-2">
              <div className="text-[10px] font-extrabold uppercase tracking-wider text-[#6e0717] border-b border-stone-100 pb-1">
                Model & Verification Details
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="min-w-0">
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">MP Model</span>
                  <span className="font-bold text-stone-900 text-[10px] block truncate" title={getFieldValue(selectedRow, ['mp model', 'mp_model', 'mpModel'], 'N/A')}>
                    {getFieldValue(selectedRow, ['mp model', 'mp_model', 'mpModel'], 'N/A')}
                  </span>
                </div>
                <div className="min-w-0">
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Dev Model</span>
                  <span className="font-bold text-stone-900 text-[10px] block truncate" title={getFieldValue(selectedRow, ['dev model', 'dev_model', 'devModel'], 'N/A')}>
                    {getFieldValue(selectedRow, ['dev model', 'dev_model', 'devModel'], 'N/A')}
                  </span>
                </div>
                <div className="col-span-2 min-w-0">
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Init Model</span>
                  <span className="font-semibold text-stone-800 text-[10px] block break-all">
                    {getFieldValue(selectedRow, ['initial model', 'initial_model', 'initModel'], 'N/A')}
                  </span>
                </div>
              </div>

              <div className="border-t border-stone-100 pt-2 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Structure</span>
                  <div>{renderStyledCellData('structure', getFieldValue(selectedRow, ['structure'], 'N/A'))}</div>
                </div>
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">BenComp</span>
                  <div>{renderStyledCellData('bencomp', getFieldValue(selectedRow, ['benComp', 'bencomp'], 'N/A'))}</div>
                </div>
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">HWTool</span>
                  <div>{renderStyledCellData('hwtool', getFieldValue(selectedRow, ['hwTool', 'hwtool'], 'N/A'))}</div>
                </div>
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Substitute Check</span>
                  <div>{renderStyledCellData('substitute_check', getFieldValue(selectedRow, ['substitute_check', 'substitutecheck'], 'N/A'))}</div>
                </div>
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Tool Option</span>
                  <div>{renderStyledCellData('tool_option', getFieldValue(selectedRow, ['tool_option', 'tooloption'], 'N/A'))}</div>
                </div>
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">OperationPlan</span>
                  <div>{renderStyledCellData('operation_plan', getFieldValue(selectedRow, ['operation_plan', 'operationplan'], 'N/A'))}</div>
                </div>
              </div>

              <div className="border-t border-stone-100 pt-2 text-xs">
                <span className="text-[9px] text-stone-400 block font-bold uppercase">Compare Note</span>
                <p className="text-stone-700 bg-stone-50 p-1.5 rounded border border-stone-200 mt-0.5 break-words font-mono text-[11px]">
                  {getFieldValue(selectedRow, ['compare_note', 'comparenote'], 'None')}
                </p>
              </div>
            </section>

            <section className="bg-white p-2.5 rounded-lg border border-stone-200 shadow-xs space-y-2">
              <div className="text-[10px] font-extrabold uppercase tracking-wider text-[#6e0717] border-b border-stone-100 pb-1">
                Hardware & Regional Metadata
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Year</span>
                  <span className="font-bold text-stone-800">{getFieldValue(selectedRow, ['year', 'model_year'], 'N/A')}</span>
                </div>
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Model Series</span>
                  <span className="font-bold text-stone-800">{getFieldValue(selectedRow, ['model_series', 'series'], 'N/A')}</span>
                </div>
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Circuit PIC</span>
                  {(() => {
                    const rawPic = getFieldValue(selectedRow, ['model_circuit_pic', 'circuit_pic'], 'N/A');
                    if (!rawPic || rawPic === 'N/A') return <span className="font-medium text-stone-800">N/A</span>;
                    const picList = String(rawPic).split(',').map((item) => item.trim()).filter(Boolean);
                    return (
                      <ul className="list-disc list-inside text-stone-800 font-medium text-[10px] space-y-0.5 mt-0.5">
                        {picList.map((pic, idx) => (
                          <li key={idx} className="truncate">{pic}</li>
                        ))}
                      </ul>
                    );
                  })()}
                </div>
                <div>
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Model Region</span>
                  <span className="font-medium text-stone-800">{getFieldValue(selectedRow, ['model_region', 'region'], 'N/A')}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-[9px] text-stone-400 block font-bold uppercase">Model SOC</span>
                  <span className="font-mono text-stone-800 bg-stone-100 px-1.5 py-0.5 rounded text-[11px] font-bold inline-block mt-0.5">
                    {getFieldValue(selectedRow, ['model_soc', 'soc'], 'N/A')}
                  </span>
                </div>
              </div>
            </section>

            <section className="bg-white p-2.5 rounded-lg border border-stone-200 shadow-xs space-y-2">
              <div className="text-[10px] font-extrabold uppercase tracking-wider text-[#6e0717] border-b border-stone-100 pb-1">
                Timestamps & Exception Tracking
              </div>
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-[9px] text-stone-400 font-bold uppercase">BOM Release Date</span>
                  <span className="font-mono font-medium text-stone-800">{getFieldValue(selectedRow, ['bom_release_date', 'release_date'], 'N/A')}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[9px] text-stone-400 font-bold uppercase">BOM Checking Time</span>
                  <span className="font-mono font-medium text-stone-800">{getFieldValue(selectedRow, ['bom_checking_time', 'checking_time'], 'N/A')}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[9px] text-stone-400 font-bold uppercase">BOM Last Checker</span>
                  <span className="font-semibold text-stone-800">{getFieldValue(selectedRow, ['bom_last_checker', 'last_checker'], 'N/A')}</span>
                </div>
              </div>

              {(() => {
                const exceptionData = getFieldValue(selectedRow, ['exception_log', 'exceptionlog', 'exception'], null);
                const hasException = exceptionData !== null && exceptionData !== 'N/A' && String(exceptionData).trim() !== '';

                return (
                  <div className={`mt-2 p-2 rounded-lg border transition-all ${hasException ? 'bg-amber-100 border-amber-400 text-amber-950' : 'bg-stone-50 border-stone-200 text-stone-500'}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1.5">
                        <AlertTriangle className={`w-3.5 h-3.5 ${hasException ? 'text-amber-700 animate-pulse' : 'text-stone-400'}`} />
                        <span className="text-[10px] font-extrabold uppercase tracking-wider">Exception Log</span>
                      </div>
                      <button
                        onClick={() => setShowExceptionLog(!showExceptionLog)}
                        className={`p-1 rounded hover:bg-black/10 transition cursor-pointer ${hasException ? 'text-amber-900' : 'text-stone-400'}`}
                        title="Toggle Exception Log"
                      >
                        {showExceptionLog ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>

                    {showExceptionLog && (
                      <div className="mt-1.5 pt-1.5 border-t border-amber-200/60 text-[11px] font-mono break-words">
                        {hasException ? String(exceptionData) : 'No exception log entry recorded for this BOM item.'}
                      </div>
                    )}
                  </div>
                );
              })()}
            </section>
          </div>

          <div className="p-2.5 bg-white border-t border-stone-200 flex items-center justify-between gap-2 flex-none">
            {currentTab === 'bom' ? (
              <button
                onClick={() => handleViewResultInNewTab(selectedRow)}
                className="flex-1 inline-flex items-center justify-center space-x-1.5 px-3 py-1.5 bg-[#C8102E] hover:bg-[#A00C23] text-white text-xs font-extrabold rounded-lg border border-[#D4AF37] transition shadow-xs cursor-pointer"
              >
                <ExternalLink className="w-3.5 h-3.5 text-[#D4AF37]" />
                <span>View Result</span>
              </button>
            ) : null}
            <button
              onClick={() => setSelectedRow(null)}
              className="px-3 py-1.5 bg-stone-100 hover:bg-stone-200 text-stone-700 text-xs font-bold rounded-lg border border-stone-300 transition cursor-pointer"
            >
              Close
            </button>
          </div>
        </aside>
      )}
      </div>

      {showMpxModal && (
        <div className="fixed inset-0 bg-stone-900/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-4 shadow-2xl border border-red-100 space-y-3">
            <div className="flex justify-between items-center border-b border-stone-100 pb-2">
              <div>
                <h2 className="text-xs sm:text-sm font-black text-stone-900">MPX Report Overview</h2>
                <p className="text-[10px] text-stone-400">Crosschecking summary stats</p>
              </div>
              <button
                onClick={() => setShowMpxModal(false)}
                className="p-1 bg-stone-100 hover:bg-stone-200 rounded-xl text-stone-600 transition cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100 text-center">
                <span className="text-[9px] font-bold text-stone-400 uppercase">Total Models</span>
                <div className="text-base font-black text-stone-900 mt-0.5">1,250</div>
              </div>

              <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-100 text-center">
                <span className="text-[9px] font-bold text-emerald-700 uppercase">Checked</span>
                <div className="text-base font-black text-emerald-600 mt-0.5">1,208</div>
              </div>

              <div
                onClick={openSkippedSidebarFromMpx}
                className="p-2.5 rounded-xl bg-red-50 border border-red-200 text-center cursor-pointer hover:bg-red-100/60 transition group"
              >
                <span className="text-[9px] font-bold text-red-700 uppercase group-hover:underline">Skipped</span>
                <div className="text-base font-black text-red-600 mt-0.5">42</div>
                <span className="text-[8px] text-red-500 font-semibold">View List →</span>
              </div>
            </div>

            <p className="text-[10px] text-stone-400 text-center">
              Click on <strong>Total Model Skipped</strong> to inspect detailed reasons.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}