// src/app/DashboardClient.tsx
"use client";

import React, { useState, useMemo, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useRouter, useSearchParams } from 'next/navigation';
import { isSpecialUser, isBomOwner } from '@/lib/bomAccess';
import { updateUrlParams } from '@/lib/urlState';

const initialQueue = [
    { id: 1, type: "REJECTION", message: "Model flagged as NG by M.R.", time: "10 mins ago", urgent: true },
    { id: 2, type: "UNASSIGNED", message: "Model pending inspector assignment", time: "25 mins ago", urgent: false },
    { id: 3, type: "OVERDUE", message: "Model breached Inspection SLA", time: "1 hour ago", urgent: true },
    { id: 4, type: "PASSED", message: "QC clearance completed by J.D.", time: "2 hours ago", urgent: false }
];

export interface BomItem {
    id: number;
    mpModel: string;
    devModel: string;
    initialModel: string;
    result: string;
    structure: string;
    benComp: string;
    hwTool: string;
    substituteCheck: string;
    toolOption: string;
    operationPlan: string;
    compareNote: string;
    year: string;
    version: string;
    modelCircuitPic: string;
    modelSubsidiary: string;
    modelSeries: string;
    modelRegion: string;
    modelSoc: string;
    engineerConfirmation: string;
    bomReleaseDate: string;
    bomDelayCount: number;
    bomTeam: string;
    remark: string;
    additionalRemark: string;
    initialRegion?: string;      // Crosscheck Configuration: nama model TV Initial Region
    jiraPowerConsLink?: string;  // Crosscheck Configuration: link halaman JIRA Power Cons.
    [key: string]: any;
}

interface DashboardClientProps {
    initialBomData: BomItem[];
    userName?: string;
}

/**
 * Crosscheck Configuration di drawer (tab Component Attribute).
 * Nilai awal ditentukan sistem (backend), user bisa override lewat tombol pensil.
 * key = nama field di BomItem = nama "field" yang dikirim ke /api/bom/update_model_info
 * Halaman View Result memakai nilai yang sama untuk nama model di header tabel.
 */
type CrosscheckConfigKey = 'devModel' | 'initialModel' | 'initialRegion' | 'jiraPowerConsLink';

const CROSSCHECK_CONFIG_FIELDS: { key: CrosscheckConfigKey; label: string; placeholder: string; isLink?: boolean }[] = [
    { key: 'devModel', label: 'Development Model', placeholder: 'Development model name' },
    { key: 'initialModel', label: 'Initial Model', placeholder: 'Initial model name' },
    { key: 'initialRegion', label: 'Initial Region', placeholder: 'Initial region model name' },
    { key: 'jiraPowerConsLink', label: 'JIRA Power Cons. Page', placeholder: 'https://...', isLink: true },
];

const EMPTY_CONFIG_DRAFT: Record<CrosscheckConfigKey, string> = {
    devModel: '', initialModel: '', initialRegion: '', jiraPowerConsLink: '',
};

function getConfigValues(item: BomItem): Record<CrosscheckConfigKey, string> {
    return {
        devModel: item.devModel || '',
        initialModel: item.initialModel || '',
        initialRegion: item.initialRegion || '',
        jiraPowerConsLink: item.jiraPowerConsLink || '',
    };
}

function isValidHttpUrl(value: string): boolean {
    try {
        const url = new URL(value);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch {
        return false;
    }
}

/**
 * Drawer yang terbuka disimpan di URL (?model=<MP model>&drawerTab=profile).
 * Cari BOM berdasarkan nama MP model, hanya di antara BOM yang memang tampil di My BOM user ini
 * (aturan sama dengan filter My BOM: semua BOM untuk user khusus, selain itu hanya BOM milik PIC-nya).
 */
function findMyBomIdByModel(items: BomItem[], mpModel: string | null, userName?: string): number | null {
    const model = (mpModel ?? '').trim();
    if (!model) return null;
    const name = (userName ?? '').trim();
    const item = items.find(i =>
        (i.mpModel || '').trim() === model &&
        (name === '' || isSpecialUser(name) || isBomOwner(name, i.modelCircuitPic))
    );
    return item ? item.id : null;
}

function getCookie(name: string): string {
    if (typeof document === 'undefined') return '';
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift() || '';
    return '';
}

function getYearCode(calendarYear: number): string {
    const codeNum = (calendarYear % 100) + 1;
    return `${codeNum}Y`;
}

/**
 * Deep/recursive helper to check if any key containing 'initial' and 'updater'
 * is set to 'system' anywhere in the row item or its nested sub-objects.
 */
function isSystemUpdater(obj?: Record<string, any> | null): boolean {
    if (!obj || typeof obj !== 'object') return false;

    for (const [key, value] of Object.entries(obj)) {
        if (value === undefined || value === null) continue;

        const normalizedKey = key.toLowerCase().replace(/[^a-z0-9]/g, '');

        if (
            (normalizedKey.includes('initial') && normalizedKey.includes('updater')) ||
            normalizedKey === 'initialupdater' ||
            normalizedKey === 'initialupdatertext'
        ) {
            const strVal = String(value).trim().toLowerCase();
            if (strVal === 'system' || strVal.includes('system')) {
                return true;
            }
        }

        if (typeof value === 'object' && !Array.isArray(value) && key !== 'parent') {
            if (isSystemUpdater(value)) {
                return true;
            }
        }
    }

    return false;
}

export default function DashboardClient({ initialBomData, userName }: DashboardClientProps) {
    const router = useRouter();

    const currentCalendarYear = new Date().getFullYear();
    const defaultYearCode = getYearCode(currentCalendarYear);

    // --- STATE ---
    const [bomData, setBomData] = useState<BomItem[]>(initialBomData);
    const [queue, setQueue] = useState(initialQueue);
    const [filter, setFilter] = useState('ALL');
    const [search, setSearch] = useState('');
    const [selectedYear, setSelectedYear] = useState<string>('27Y');
    const [prioritization, setPrioritization] = useState(false);
    const [urgentOnly, setUrgentOnly] = useState(false);
    const [systemOnly, setSystemOnly] = useState(false);
    const [page, setPage] = useState(1);
    const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
    // Drawer & tab drawer: nilai awal dari URL, supaya setelah refresh / dari link yang dibagikan langsung terbuka lagi
    const searchParams = useSearchParams();
    const [sidebarItemId, setSidebarItemId] = useState<number | null>(
        () => findMyBomIdByModel(initialBomData, searchParams.get('model'), userName)
    );
    const [viewResult, setViewResult] = useState(false);
    const [toasts, setToasts] = useState<{ id: number, msg: string, type: string }[]>([]);

    const [showKpis, setShowKpis] = useState(true);
    const [queuePage, setQueuePage] = useState(1);
    const queueItemsPerPage = 3;

    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');

    const [visibleGroups, setVisibleGroups] = useState({
        group2: false,
        group3: false,
        group4: false
    });
    const [isGroupDropdownOpen, setIsGroupDropdownOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const [sidebarTab, setSidebarTab] = useState<'attributes' | 'profile'>(
        () => (searchParams.get('drawerTab') === 'profile' ? 'profile' : 'attributes')
    );
    const [sbInitial, setSbInitial] = useState('');
    const [sbRemarks, setSbRemarks] = useState('');

    // --- EDIT MODEL STATES ---
    // Crosscheck Configuration (drawer): field yang sedang diedit + isi kotak input
    const [editingConfig, setEditingConfig] = useState<CrosscheckConfigKey | null>(null);
    const [configDraft, setConfigDraft] = useState<Record<CrosscheckConfigKey, string>>(EMPTY_CONFIG_DRAFT);
    const [isUpdatingModel, setIsUpdatingModel] = useState(false);
    // Tempat filter tahun di header halaman (elemen dibuat oleh DashboardLayoutClient)
    const [headerSlot, setHeaderSlot] = useState<HTMLElement | null>(null);
    useEffect(() => {
        setHeaderSlot(document.getElementById('page-header-actions'));
    }, []);
    const [sidebarNotification, setSidebarNotification] = useState('');

    const [fetchedProfile, setFetchedProfile] = useState<any>(null);
    const [isProfileLoading, setIsProfileLoading] = useState(false);

    // Retest Loading, Timer Tracking, Exception Log Toggle & Retest Result Popup Data
    const [retestResult, setRetestResult] = useState<any | null>(null);
    const [showExceptionLog, setShowExceptionLog] = useState(false);
    const [activeRetestId, setActiveRetestId] = useState<number | null>(null);
    const [isBatchRetesting, setIsBatchRetesting] = useState(false);
    const [timer, setTimer] = useState(0);

    const itemsPerPage = showKpis ? 6 : 12;

    const isRetestingActive = activeRetestId !== null || isBatchRetesting;

    const yearOptions = useMemo(() => {
        const yearsSet = new Set<string>();
        yearsSet.add("27Y");
        yearsSet.add("26Y");
        initialBomData.forEach(item => {
            const yr = item.year || item.modelYear;
            if (yr && yr.trim() !== '' && yr !== '-') {
                yearsSet.add(yr.trim());
            }
        });
        return Array.from(yearsSet).sort();
    }, [initialBomData]);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (isRetestingActive) {
            setTimer(0);
            interval = setInterval(() => {
                setTimer((prev) => prev + 1);
            }, 1000);
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [isRetestingActive]);

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsGroupDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const userFilteredBomData = useMemo(() => {
        if (!userName || userName.trim() === '') return bomData;

        // User khusus melihat semua BOM. Daftarnya di src/lib/bomAccess.ts (SPECIAL_USERS)
        if (isSpecialUser(userName)) {
            return bomData;
        }

        // User biasa hanya melihat BOM yang PIC Circuit-nya dia sendiri
        return bomData.filter(item => isBomOwner(userName, item.modelCircuitPic));
    }, [bomData, userName]);

    const kpiFilteredBomData = useMemo(() => {
        if (selectedYear === 'ALL') return userFilteredBomData;
        return userFilteredBomData.filter(item => {
            const itemYr = item.year || item.modelYear || '';
            return itemYr.trim() === selectedYear;
        });
    }, [userFilteredBomData, selectedYear]);

    // Active KPI dataset excluding hidden NG rows (ensuring cards reflect 0 for NG items)
    const activeKpiBomData = useMemo(() => {
        return kpiFilteredBomData.filter(i => i.result !== 'NG');
    }, [kpiFilteredBomData]);

    const systemUpdaterCount = useMemo(() => {
        return userFilteredBomData.filter(item => isSystemUpdater(item) && item.result !== 'NG').length;
    }, [userFilteredBomData]);

    const liveActivityItems = useMemo(() => {
        return activeKpiBomData.filter(item => {
            const delay = item.bomDelayCount || 0;
            const isUrgentOrOverdue = delay > 0;
            
            const engineer = item.engineerConfirmation ? item.engineerConfirmation.trim() : '';
            const isUnassignedOrNull = !engineer || engineer === '-' || engineer.toLowerCase() === 'unassigned' || engineer.toLowerCase() === 'null';

            return isUrgentOrOverdue || isUnassignedOrNull;
        });
    }, [activeKpiBomData]);

    const totalQueuePages = Math.ceil(liveActivityItems.length / queueItemsPerPage) || 1;
    const safeQueuePage = Math.min(queuePage, totalQueuePages);
    const paginatedQueueData = liveActivityItems.slice((safeQueuePage - 1) * queueItemsPerPage, safeQueuePage * queueItemsPerPage);

    // KPI Card Counts (reflecting non-NG active view)
    const totalBOM = activeKpiBomData.length;
    const totalNG = 0; // Forced to 0 since NG rows are hidden from view
    const totalCheck = activeKpiBomData.filter(i => i.result === 'CHECK').length;
    
    // No Initial count: rows where Initial Model is null, none, empty, '-', or 'cannot detected'
    const noInitial = activeKpiBomData.filter(i => {
        const init = (i.initialModel || '').trim().toLowerCase();
        return !init || init === '-' || init === 'null' || init === 'none' || init === 'cannot detected' || init === 'no data';
    }).length;

    const totalUnremarked = activeKpiBomData.filter(i => !i.remark || i.remark.trim() === '' || i.remark === '-').length;
    const urgentCount = activeKpiBomData.filter(i => (i.bomDelayCount || 0) > 5).length; 
    const overdueCount = activeKpiBomData.filter(i => (i.bomDelayCount || 0) > 0).length; 
    const okCount = activeKpiBomData.filter(i => i.result === 'OK').length;

    const parseDateValue = (dateStr: string): number | null => {
        if (!dateStr || dateStr === '-' || dateStr.toLowerCase() === 'n/a') return null;
        const parsed = new Date(dateStr);
        return isNaN(parsed.getTime()) ? null : parsed.getTime();
    };

    const handleSetCurrentDate = () => {
        const today = new Date().toISOString().split('T')[0];
        setStartDate(today);
        setEndDate(today);
        setPage(1);
    };

    const handleClearDateRange = () => {
        setStartDate('');
        setEndDate('');
        setPage(1);
    };

    const handleToggleKpis = () => {
        setShowKpis(prev => !prev);
        setPage(1);
    };

    const handleTogglePrioritization = (checked: boolean) => {
        setPrioritization(checked);
        setPage(1);
    };

    const filteredData = useMemo(() => {
        const startTimestamp = startDate ? new Date(startDate).setHours(0, 0, 0, 0) : null;
        const endTimestamp = endDate ? new Date(endDate).setHours(23, 59, 59, 999) : null;

        const items = userFilteredBomData.filter(item => {
            // Requirement Fix: Hide all rows with 'NG' result in the MP Master table
            if (item.result === 'NG') return false;

            if (selectedYear !== 'ALL') {
                const itemYr = item.year || item.modelYear || '';
                if (itemYr.trim() !== selectedYear) return false;
            }

            if (filter === 'OK' && item.result !== 'OK') return false;
            if (filter === 'NG') return false; // Force 'NG Only' to show no rows
            if (filter === 'CHECK' && item.result !== 'CHECK') return false;
            
            if (filter === 'NO_INITIAL') {
                const init = (item.initialModel || '').trim().toLowerCase();
                const isNoInit = !init || init === '-' || init === 'null' || init === 'none' || init === 'cannot detected' || init === 'no data';
                if (!isNoInit) return false;
            }

            if (filter === 'UNREMARKED' && (item.remark && item.remark.trim() !== '' && item.remark !== '-')) return false;
            if (filter === 'URGENT' && (item.bomDelayCount || 0) <= 5) return false;
            if (filter === 'OVERDUE' && (item.bomDelayCount || 0) <= 0) return false;
            if (urgentOnly && (item.bomDelayCount || 0) <= 5) return false;
            if (systemOnly && !isSystemUpdater(item)) return false;

            if (startTimestamp || endTimestamp) {
                const itemTime = parseDateValue(item.bomReleaseDate);
                if (itemTime === null) return false;
                if (startTimestamp && itemTime < startTimestamp) return false;
                if (endTimestamp && itemTime > endTimestamp) return false;
            }

            if (search.trim() !== '') {
                const q = search.toLowerCase();
                return (item.mpModel && item.mpModel.toLowerCase().includes(q)) ||
                    (item.devModel && item.devModel.toLowerCase().includes(q)) ||
                    (item.engineerConfirmation && item.engineerConfirmation.toLowerCase().includes(q)) ||
                    (item.initialModel && item.initialModel.toLowerCase().includes(q)) ||
                    (item.result && item.result.toLowerCase().includes(q)) ||
                    (item.remark && item.remark.toLowerCase().includes(q));
            }
            return true;
        });

        if (!prioritization) return items;

        const isPriority1 = (i: BomItem) => {
            const res = (i.result || '').toUpperCase();
            return res === 'NG' || res === 'CHECK';
        };

        const isPriority2 = (i: BomItem) => {
            const dev = (i.devModel || '').trim().toLowerCase();
            return !dev || dev === '-' || dev === 'cannot detected' || dev === 'no data';
        };

        const isPriority3 = (i: BomItem) => {
            const init = (i.initialModel || '').trim().toLowerCase();
            return !init || init === '-' || init === 'cannot detected' || init === 'no data';
        };

        const getPriorityScore = (i: BomItem) => {
            if (isPriority1(i)) return 1;
            if (isPriority2(i)) return 2;
            if (isPriority3(i)) return 3;
            return 4;
        };

        return [...items].sort((a, b) => getPriorityScore(a) - getPriorityScore(b));
    }, [userFilteredBomData, filter, search, urgentOnly, systemOnly, startDate, endDate, selectedYear, prioritization]);

    const totalPages = Math.ceil(filteredData.length / itemsPerPage) || 1;
    const safePage = Math.min(page, totalPages);
    const startIndex = (safePage - 1) * itemsPerPage;
    const paginatedData = filteredData.slice(startIndex, startIndex + itemsPerPage);

    const getPageNumbers = () => {
        const maxPagesToShow = 5;
        if (totalPages <= maxPagesToShow) {
            return Array.from({ length: totalPages }, (_, i) => i + 1);
        }
        
        let startPage = Math.max(1, safePage - 2);
        let endPage = Math.min(totalPages, safePage + 2);

        if (safePage <= 3) {
            endPage = 5;
        } else if (safePage >= totalPages - 2) {
            startPage = totalPages - 4;
        }

        const pages = [];
        for (let i = startPage; i <= endPage; i++) {
            pages.push(i);
        }
        return pages;
    };

    const isSidebarOpen = sidebarItemId !== null;
    const activeSidebarItem = bomData.find(i => i.id === sidebarItemId) ?? null;

    // Simpan drawer yang terbuka ke URL (replace: tidak menambah riwayat Back browser)
    const activeSidebarModel = activeSidebarItem?.mpModel || null;
    useEffect(() => {
        updateUrlParams({
            model: activeSidebarModel,
            drawerTab: activeSidebarModel && sidebarTab === 'profile' ? 'profile' : null,
        });
    }, [activeSidebarModel, sidebarTab]);

    // Link berisi ?model= untuk BOM yang tidak ada di My BOM user ini: drawer tidak dibuka, beri tahu user
    const sharedModelChecked = useRef(false);
    useEffect(() => {
        if (sharedModelChecked.current) return;
        sharedModelChecked.current = true;
        const sharedModel = searchParams.get('model');
        if (sharedModel && findMyBomIdByModel(initialBomData, sharedModel, userName) === null) {
            showToast(`BOM ${sharedModel} is not in your My BOM list. Open it from Global Overview instead.`, 'warning');
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        setFetchedProfile(null);
    }, [activeSidebarItem?.id]);

    useEffect(() => {
        if (activeSidebarItem && sidebarTab === 'profile' && !fetchedProfile) {
            const fetchProfileData = async () => {
                setIsProfileLoading(true);
                try {
                    const response = await fetch('/api/bom/model_profile', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ targetModel: activeSidebarItem.mpModel })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        const profile = Array.isArray(data) ? data[0] : (data.profileData ? data.profileData[0] : data);
                        setFetchedProfile(profile);
                    } else {
                        showToast("Failed to fetch model profile details", "warning");
                    }
                } catch (error) {
                    console.error("Error fetching profile:", error);
                    showToast("Network error while fetching profile", "warning");
                } finally {
                    setIsProfileLoading(false);
                }
            };
            
            fetchProfileData();
        }
    }, [activeSidebarItem, sidebarTab, fetchedProfile]);

    useEffect(() => {
        if (activeSidebarItem) {
            setSbInitial(activeSidebarItem.engineerConfirmation || '');
            setSbRemarks(activeSidebarItem.remark || '');
            
            setConfigDraft(getConfigValues(activeSidebarItem));
            setEditingConfig(null);
            setSidebarNotification('');
        }
    }, [activeSidebarItem]);

    const showToast = (msg: string, type = "success") => {
        const id = Date.now() + Math.random();
        setToasts(prev => [...prev, { id, msg, type }]);
        setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id));
        }, 3500);
    };

    /** Klik pensil: buka edit field ini (isi kotak input dikembalikan ke nilai tersimpan) */
    const startEditConfig = (key: CrosscheckConfigKey) => {
        if (!activeSidebarItem) return;
        setConfigDraft(prev => ({ ...prev, [key]: getConfigValues(activeSidebarItem)[key] }));
        setEditingConfig(key);
    };

    const cancelEditConfig = () => {
        if (activeSidebarItem) setConfigDraft(getConfigValues(activeSidebarItem));
        setEditingConfig(null);
    };

    /** Simpan override Crosscheck Configuration ke backend (/api/bom/update_model_info) */
    const handleUpdateModelInfo = async (key: CrosscheckConfigKey) => {
        if (!activeSidebarItem) return;
        const config = CROSSCHECK_CONFIG_FIELDS.find(f => f.key === key);
        if (!config) return;

        const newValue = configDraft[key].trim();
        const fieldName = config.key;
        const modelLabel = config.label;

        if (config.isLink && newValue !== '' && !isValidHttpUrl(newValue)) {
            showToast('Please enter a valid link (starting with http:// or https://)', 'warning');
            return;
        }

        setIsUpdatingModel(true);
        try {
            const response = await fetch('/api/bom/update_model_info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mpModel: activeSidebarItem.mpModel,
                    field: fieldName,
                    value: newValue
                })
            });

            if (response.ok) {
                setBomData(prev => prev.map(item => 
                    item.id === activeSidebarItem.id 
                        ? { ...item, [fieldName]: newValue } 
                        : item
                ));
                
                setEditingConfig(null);

                setSidebarNotification(`${modelLabel} has been changed successfully.`);
                setTimeout(() => setSidebarNotification(''), 4000);
                showToast(`${modelLabel} updated for ${activeSidebarItem.mpModel}`, "success");
            } else {
                showToast(`Failed to update ${modelLabel}`, "warning");
            }
        } catch (error) {
            console.error("Error updating model info:", error);
            showToast("Network error while updating", "warning");
        } finally {
            setIsUpdatingModel(false);
        }
    };

    const handleSetFilter = (type: string) => {
        setFilter(type);
        setUrgentOnly(type === 'URGENT');
        setPage(1);
    };

    const handleToggleUrgent = () => {
        setUrgentOnly(!urgentOnly);
        if (!(!urgentOnly) && filter === 'URGENT') setFilter('ALL');
        setPage(1);
    };

    const handleToggleSystemOnly = () => {
        setSystemOnly(!systemOnly);
        setPage(1);
    };

    const handleSearch = (val: string) => {
        setSearch(val);
        setPage(1);
    };

    const resetAllFilters = () => {
        setSearch('');
        setUrgentOnly(false);
        setSystemOnly(false);
        setPrioritization(false);
        setFilter('ALL');
        setStartDate('');
        setEndDate('');
        setSelectedYear('ALL');
        setPage(1);
    };

    const handleCheckboxToggle = (id: number, checked: boolean) => {
        const newSet = new Set(selectedIds);
        if (checked) {
            newSet.add(id);
            setSidebarItemId(id);
        } else {
            newSet.delete(id);
            if (sidebarItemId === id) setSidebarItemId(null);
        }
        setSelectedIds(newSet);
    };

    const toggleSelectAllRows = (checked: boolean) => {
        if (checked) {
            const newSet = new Set(selectedIds);
            filteredData.forEach(item => newSet.add(item.id));
            setSelectedIds(newSet);
            if (filteredData.length > 0) setSidebarItemId(filteredData[0].id);
        } else {
            setSelectedIds(new Set());
            setSidebarItemId(null);
        }
    };

    const handleRowClick = (id: number) => {
        setSidebarItemId(id);
    };

    const toggleGroupVisibility = (groupKey: 'group2' | 'group3' | 'group4') => {
        setVisibleGroups(prev => ({ ...prev, [groupKey]: !prev[groupKey] }));
    };

    const toggleAllGroups = (showAll: boolean) => {
        setVisibleGroups({
            group2: showAll,
            group3: showAll,
            group4: showAll
        });
    };

    const areAllGroupsVisible = visibleGroups.group2 && visibleGroups.group3 && visibleGroups.group4;

    const handleSingleRowRetest = async (id: number) => {
        const item = bomData.find(i => i.id === id);
        if (!item) return;

        const ssolgenet_cookie = getCookie('ssolgenet');
        const smsession_cookie = getCookie('SMSESSION');

        setActiveRetestId(id);

        try {
            const response = await fetch('/api/bom/retest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ssolgenet_cookie,
                    smsession_cookie,
                    targetModel: item.mpModel,
                    devModel: item.devModel || "",
                    initModel: item.initialModel || ""
                })
            });

            if (response.ok) {
                const data = await response.json();
                const resPayload = data?.results ? data.results[0] : data;
                setRetestResult(resPayload);
                setShowExceptionLog(false);

                setBomData(prev => prev.map(i => {
                    if (i.id === id) {
                        return { ...i, result: 'CHECK', remark: (i.remark ? i.remark + " | " : "") + "Row retest initiated" };
                    }
                    return i;
                }));
                
                setQueue(prev => [{ id: Date.now(), type: "RETEST", message: `${item.mpModel} queued for retest inspection`, time: "Just now", urgent: true }, ...prev]);
                showToast(`Retest finished for ${item.mpModel}`, "info");
                setSidebarItemId(id);
            } else {
                showToast(`Failed to initiate retest for ${item.mpModel}`, "warning");
            }
        } catch (error) {
            console.error("Error during retest:", error);
            showToast("Network error while initiating retest", "warning");
        } finally {
            setActiveRetestId(null);
        }
    };

    const handleSingleRowCheck = (id: number) => {
        setBomData(prev => prev.map(item => {
            if (item.id === id) {
                return { ...item, result: 'OK', engineerConfirmation: (!item.engineerConfirmation || item.engineerConfirmation.trim() === '') ? 'QC.SYS' : item.engineerConfirmation };
            }
            return item;
        }));
        const item = bomData.find(i => i.id === id);
        if (item) {
            setQueue(prev => [{ id: Date.now(), type: "CHECK PASSED", message: `${item.mpModel} verified & marked as OK`, time: "Just now", urgent: false }, ...prev]);
            showToast(`${item.mpModel} status set to OK`, "success");
        }
    };

    const handleRetestAction = async () => {
        const targets = selectedIds.size > 0 ? bomData.filter(i => selectedIds.has(i.id)) : bomData.filter(i => i.result === 'NG');
        if (targets.length === 0) return showToast("No NG or selected items found for retest", "info");

        const ssolgenet_cookie = getCookie('ssolgenet');
        const smsession_cookie = getCookie('SMSESSION');

        setIsBatchRetesting(true);

        try {
            const responses = await Promise.all(targets.map(item => 
                fetch('/api/bom/retest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ssolgenet_cookie,
                        smsession_cookie,
                        targetModel: item.mpModel,
                        devModel: item.devModel || "",
                        initModel: item.initialModel || ""
                    })
                })
            ));

            const firstRes = responses[0];
            if (firstRes && firstRes.ok) {
                const data = await firstRes.json();
                const resPayload = data?.results ? data.results[0] : data;
                setRetestResult(resPayload);
                setShowExceptionLog(false);
            }

            setBomData(prev => prev.map(item => {
                if (targets.some(t => t.id === item.id)) {
                    return { ...item, result: 'CHECK', remark: (item.remark ? item.remark + " | " : "") + "Queued for retest" };
                }
                return item;
            }));

            const newQueueItems = targets.map(item => ({ id: Date.now() + Math.random(), type: "RETEST", message: `${item.mpModel} retest initiated`, time: "Just now", urgent: true }));
            setQueue(prev => [...newQueueItems, ...prev]);
            setSelectedIds(new Set());
            setSidebarItemId(targets[0].id);
            showToast(`Initiated retest for ${targets.length} item(s)`, "success");
        } catch (error) {
            console.error("Error during bulk retest:", error);
            showToast("Network error while initiating bulk retest", "warning");
        } finally {
            setIsBatchRetesting(false);
        }
    };

    const handleCheckAction = () => {
        const targets = selectedIds.size > 0 ? bomData.filter(i => selectedIds.has(i.id)) : bomData.filter(i => i.result === 'CHECK');
        if (targets.length === 0) return showToast("Select items or view 'CHECK' status items to verify", "info");

        setBomData(prev => prev.map(item => {
            if (targets.some(t => t.id === item.id)) {
                return { ...item, result: 'OK', engineerConfirmation: (!item.engineerConfirmation || item.engineerConfirmation.trim() === '') ? 'QC.SYS' : item.engineerConfirmation };
            }
            return item;
        }));

        const newQueueItems = targets.map(item => ({ id: Date.now() + Math.random(), type: "CHECK PASSED", message: `${item.mpModel} verified & set to OK`, time: "Just now", urgent: false }));
        setQueue(prev => [...newQueueItems, ...prev]);
        setSelectedIds(new Set());
        showToast(`Marked ${targets.length} item(s) as Checked & OK`, "success");
    };

    const saveSidebarChanges = () => {
        if (!activeSidebarItem) return;
        setBomData(prev => prev.map(item => item.id === activeSidebarItem.id ? { ...item, remark: sbRemarks.trim(), engineerConfirmation: sbInitial.trim() } : item));
        setQueue(prev => [{ id: Date.now(), type: "UPDATE", message: `${activeSidebarItem.mpModel} updated via Inspector Drawer`, time: "Just now", urgent: false }, ...prev]);
        showToast(`Saved updates for ${activeSidebarItem.mpModel}`, "success");
    };

    const downloadSingleItemReport = (id: number) => {
        const item = bomData.find(i => i.id === id);
        if (!item) return;
        const reportData = { reportTitle: "BOM Quality Control Certificate", generatedDate: new Date().toISOString(), itemDetails: item };
        const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Report_${item.mpModel}_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast(`Downloaded diagnostic report for ${item.mpModel}`, "success");
    };

    const downloadCSVReport = () => {
        if (filteredData.length === 0) return showToast("No inspection data available to export", "warning");
        const headers = ["MP Model", "Dev Model", "Initial Model", "Delay Count", "QC Result", "Engineer Confirmation", "Priority Urgent", "Overdue SLA", "Remarks", "BOM Release Date"];
        const csvRows = [
            headers.join(","),
            ...filteredData.map(item => [
                `"${item.mpModel}"`, `"${(item.devModel || '').replace(/"/g, '""')}"`, `"${item.initialModel || ''}"`, item.bomDelayCount || 0, `"${item.result}"`, `"${item.engineerConfirmation || 'Unassigned'}"`,
                (item.bomDelayCount || 0) > 5 ? "YES" : "NO", (item.bomDelayCount || 0) > 0 ? "YES" : "NO", `"${(item.remark || '').replace(/"/g, '""')}"`, `"${item.bomReleaseDate || ''}"`
            ].join(","))
        ];
        const csvContent = "data:text/csv;charset=utf-8," + csvRows.join("\n");
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `BOM_Inspection_Report_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showToast(`Exported ${filteredData.length} BOM records to CSV`, "success");
    };

    const getFilterBannerText = () => {
        const names: Record<string, string> = { 'OK': 'Status: OK Cleared', 'NG': 'Status: NG Rejections', 'CHECK': 'Status: Pending Check', 'NO_INITIAL': 'No Initial Model (Null/None/Cannot Detected)', 'UNREMARKED': 'Unremarked (No Notes)', 'URGENT': 'Priority: Urgent Items', 'OVERDUE': 'SLA Status: Overdue Breached' };
        let text = names[filter] || 'Custom Query Filter';
        if (selectedYear !== 'ALL') text += ` + Year: ${selectedYear}`;
        if (urgentOnly && filter !== 'URGENT') text += ' + Urgent Only';
        if (systemOnly) text += ' + System Initial Verification';
        if (startDate || endDate) {
            text += ` + Release Date: ${startDate || 'Any'} to ${endDate || 'Any'}`;
        }
        if (search.trim() !== '') text += ` + Search: "${search}"`;
        return text;
    };

    return (
        <>
            <div id="dashboard-view" className={`w-full h-full flex-col ${viewResult ? 'hidden' : 'flex'}`}>
                <div id="app-wrapper" className={`w-full h-full overflow-y-auto flex flex-col transition-all duration-300 ease-in-out ${isSidebarOpen ? 'lg:pr-[420px]' : ''}`}>
                    <main id="main-container" className="flex-1 min-h-full max-w-[1800px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-3 gap-3 flex flex-col">
                        
                        {headerSlot && createPortal(
                            <div className="flex items-center space-x-2">
                                <span className="text-xs font-bold text-slate-500 hidden lg:inline">Filter Year:</span>
                                <div className="flex items-center space-x-1.5 bg-slate-50 p-1 rounded-xl border border-slate-200">
                                    <i className="fa-regular fa-calendar text-pantone-700 text-xs pl-2"></i>
                                    <select
                                        value={selectedYear}
                                        onChange={(e) => {
                                            const val = e.target.value;
                                            setSelectedYear(val === 'ALL' ? '27Y' : val);
                                            setPage(1);
                                            setQueuePage(1);
                                        }}
                                        className="bg-transparent text-xs font-bold text-slate-800 pr-2 py-1 outline-none cursor-pointer"
                                        title="Filter My BOM by model year"
                                    >
                                        <option value="ALL">All Years</option>
                                        {yearOptions.map(yr => (
                                            <option key={yr} value={yr}>
                                                {yr}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>,
                            headerSlot
                        )}

                        {/* KPI Cards & Live Activity */}
                        {showKpis && (
                            <section className="flex-none grid grid-cols-1 lg:grid-cols-12 gap-5 transition-all duration-300">
                                <div className="lg:col-span-8 xl:col-span-8 grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
                                    <div onClick={() => handleSetFilter('ALL')} className={`kpi-card bg-gradient-to-br from-pantone-900 to-pantone-950 p-4 rounded-2xl border border-pantone-700/60 shadow-md text-white group relative overflow-hidden cursor-pointer ${filter === 'ALL' ? 'active-card ring-2 ring-pantone-400' : ''}`}>
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-[11px] font-bold uppercase tracking-wider text-pantone-200">Total BOM</span>
                                            <div className="w-8 h-8 rounded-lg bg-pantone-800/80 text-pantone-100 flex items-center justify-center border border-pantone-600/50"><i className="fa-solid fa-boxes-stacked text-xs"></i></div>
                                        </div>
                                        <div className="flex items-baseline justify-between">
                                            <span className="text-2xl sm:text-3xl font-extrabold text-white font-mono">{totalBOM}</span>
                                            <span className="text-[11px] text-pantone-200/80 font-medium">Items</span>
                                        </div>
                                        <div className="mt-2.5 w-full bg-pantone-950/80 h-1.5 rounded-full overflow-hidden border border-pantone-800/50">
                                            <div className="bg-pantone-400 h-full rounded-full" style={{ width: '100%' }}></div>
                                        </div>
                                    </div>

                                    <div onClick={() => handleSetFilter('NG')} className={`kpi-card bg-gradient-to-br from-pantone-800 to-pantone-900 p-4 rounded-2xl border border-pantone-600 shadow-md text-white group relative overflow-hidden cursor-pointer ${filter === 'NG' ? 'active-card ring-2 ring-pantone-400' : ''}`}>
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-[11px] font-bold uppercase tracking-wider text-pantone-200">Total NG</span>
                                            <div className="w-8 h-8 rounded-lg bg-pantone-700/80 text-pantone-100 flex items-center justify-center border border-pantone-500/50"><i className="fa-solid fa-circle-xmark text-xs"></i></div>
                                        </div>
                                        <div className="flex items-baseline justify-between">
                                            <span className="text-2xl sm:text-3xl font-extrabold text-white font-mono">{totalNG}</span>
                                            <span className="text-[11px] text-pantone-200/80 font-medium">Rejections</span>
                                        </div>
                                        <div className="mt-2.5 w-full bg-pantone-950/80 h-1.5 rounded-full overflow-hidden border border-pantone-700/50">
                                            <div className="bg-pantone-300 h-full rounded-full" style={{ width: '0%' }}></div>
                                        </div>
                                    </div>

                                    <div onClick={() => handleSetFilter('CHECK')} className={`kpi-card bg-gradient-to-br from-pantone-850 to-pantone-900 p-4 rounded-2xl border border-pantone-700/80 shadow-md text-white group relative overflow-hidden cursor-pointer ${filter === 'CHECK' ? 'active-card ring-2 ring-pantone-400' : ''}`}>
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-[11px] font-bold uppercase tracking-wider text-pantone-200">Total Check</span>
                                            <div className="w-8 h-8 rounded-lg bg-pantone-700/60 text-pantone-100 flex items-center justify-center border border-pantone-500/40"><i className="fa-solid fa-magnifying-glass-chart text-xs"></i></div>
                                        </div>
                                        <div className="flex items-baseline justify-between">
                                            <span className="text-2xl sm:text-3xl font-extrabold text-white font-mono">{totalCheck}</span>
                                            <span className="text-[11px] text-pantone-200/80 font-medium">Pending QC</span>
                                        </div>
                                        <div className="mt-2.5 w-full bg-pantone-950/80 h-1.5 rounded-full overflow-hidden border border-pantone-800/50">
                                            <div className="bg-pantone-400 h-full rounded-full" style={{ width: totalBOM ? `${(totalCheck / totalBOM) * 100}%` : '0%' }}></div>
                                        </div>
                                    </div>

                                    <div onClick={() => handleSetFilter('NO_INITIAL')} className={`kpi-card bg-gradient-to-br from-pantone-900 to-pantone-950 p-4 rounded-2xl border border-pantone-700/70 shadow-md text-white group relative overflow-hidden cursor-pointer ${filter === 'NO_INITIAL' ? 'active-card ring-2 ring-pantone-400' : ''}`}>
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-[11px] font-bold uppercase tracking-wider text-pantone-200">No Initial</span>
                                            <div className="w-8 h-8 rounded-lg bg-pantone-800/80 text-pantone-100 flex items-center justify-center border border-pantone-600/40"><i className="fa-solid fa-user-slash text-xs"></i></div>
                                        </div>
                                        <div className="flex items-baseline justify-between">
                                            <span className="text-2xl sm:text-3xl font-extrabold text-white font-mono">{noInitial}</span>
                                            <span className="text-[11px] text-pantone-200/80 font-medium">Unassigned</span>
                                        </div>
                                        <div className="mt-2.5 w-full bg-pantone-950/80 h-1.5 rounded-full overflow-hidden border border-pantone-800/50">
                                            <div className="bg-pantone-400 h-full rounded-full" style={{ width: totalBOM ? `${(noInitial / totalBOM) * 100}%` : '0%' }}></div>
                                        </div>
                                    </div>

                                    <div onClick={() => handleSetFilter('UNREMARKED')} className={`kpi-card bg-gradient-to-br from-pantone-850 to-pantone-900 p-4 rounded-2xl border border-pantone-700/80 shadow-md text-white group relative overflow-hidden cursor-pointer ${filter === 'UNREMARKED' ? 'active-card ring-2 ring-pantone-400' : ''}`}>
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-[11px] font-bold uppercase tracking-wider text-pantone-200">Unremarked</span>
                                            <div className="w-8 h-8 rounded-lg bg-pantone-700/60 text-pantone-100 flex items-center justify-center border border-pantone-500/40"><i className="fa-regular fa-comment-dots text-xs"></i></div>
                                        </div>
                                        <div className="flex items-baseline justify-between">
                                            <span className="text-2xl sm:text-3xl font-extrabold text-white font-mono">{totalUnremarked}</span>
                                            <span className="text-[11px] text-pantone-200/80 font-medium">No Notes</span>
                                        </div>
                                        <div className="mt-2.5 w-full bg-pantone-950/80 h-1.5 rounded-full overflow-hidden border border-pantone-800/50">
                                            <div className="bg-pantone-300 h-full rounded-full" style={{ width: totalBOM ? `${(totalUnremarked / totalBOM) * 100}%` : '0%' }}></div>
                                        </div>
                                    </div>

                                    <div onClick={() => handleSetFilter('URGENT')} className={`kpi-card bg-gradient-to-br from-pantone-700 to-pantone-900 p-4 rounded-2xl border border-pantone-500 shadow-md text-white group relative overflow-hidden cursor-pointer ${filter === 'URGENT' ? 'active-card ring-2 ring-pantone-400' : ''}`}>
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-[16px] font-bold uppercase tracking-wider text-pantone-100">Urgent ({'<1W'})</span>
                                            <div className="w-8 h-8 rounded-lg bg-pantone-600/80 text-white flex items-center justify-center border border-pantone-400/50"><i className="fa-solid fa-triangle-exclamation text-xs"></i></div>
                                        </div>
                                        <div className="flex items-baseline justify-between">
                                            <span className="text-2xl sm:text-3xl font-extrabold text-white font-mono">{urgentCount}</span>
                                            <span className="text-[11px] text-pantone-100/90 font-medium">High Priority</span>
                                        </div>
                                        <div className="mt-2.5 w-full bg-pantone-950/80 h-1.5 rounded-full overflow-hidden border border-pantone-600/50">
                                            <div className="bg-white h-full rounded-full" style={{ width: totalBOM ? `${(urgentCount / totalBOM) * 100}%` : '0%' }}></div>
                                        </div>
                                    </div>

                                    <div onClick={() => handleSetFilter('OVERDUE')} className={`kpi-card bg-pantone-950 text-white p-4 rounded-2xl shadow-md border border-pantone-700 col-span-2 sm:col-span-2 group relative overflow-hidden flex flex-col justify-between cursor-pointer ${filter === 'OVERDUE' ? 'active-card ring-2 ring-pantone-400' : ''}`}>
                                        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-pantone-700/40 rounded-full blur-xl pointer-events-none"></div>
                                        <div>
                                            <div className="flex items-center justify-between mb-1">
                                                <span className="text-[16px] font-bold uppercase tracking-wider text-pantone-200">Critical Status ({'>2W'})</span>
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-pantone-700 text-pantone-100 uppercase tracking-widest border border-pantone-500">Overdue SLA</span>
                                            </div>
                                            <div className="flex items-baseline space-x-3 mt-1">
                                                <span className="text-6xl sm:text-4xl font-extrabold text-white font-mono tracking-tight">{overdueCount}</span>
                                                <span className="text-xs text-pantone-200">Inspection Breached</span>
                                            </div>
                                        </div>
                                        <p className="text-[11px] text-pantone-300/80 mt-2 flex items-center space-x-1">
                                            <i className="fa-solid fa-filter text-[10px]"></i>
                                            <span>Click card to filter breached SLA items</span>
                                        </p>
                                    </div>
                                </div>

                                {/* LIVE ACTIVITY QUEUE SECTION */}
                                <div className="lg:col-span-4 xl:col-span-4 bg-white rounded-2xl border border-slate-200/80 shadow-sm flex flex-col h-[290px] lg:h-auto overflow-hidden">
                                    <div className="p-3.5 border-b border-pantone-100 bg-gradient-to-r from-pantone-50 via-white to-slate-50 flex items-center justify-between">
                                        <div className="flex items-center space-x-2">
                                            <div className="w-2.5 h-2.5 rounded-full bg-pantone-700 animate-pulse"></div>
                                            <h2 className="text-xs font-bold text-pantone-950 uppercase tracking-wider">Live Activity Queue</h2>
                                        </div>
                                        <span className={`text-[11px] font-mono px-2 py-0.5 rounded-full font-bold transition-all ${
                                            liveActivityItems.length > 3 
                                                ? 'bg-red-600 text-white animate-pulse shadow-sm shadow-red-500/50' 
                                                : 'bg-pantone-100 text-pantone-800'
                                        }`}>
                                            {liveActivityItems.length} items
                                        </span>
                                    </div>
                                    <div className="p-3 overflow-y-auto flex-1 space-y-2.5 bg-slate-50/50">
                                        {paginatedQueueData.length === 0 ? (
                                            <div className="p-6 text-center text-xs text-slate-400">Queue is clear. No matching models requiring action.</div>
                                        ) : paginatedQueueData.map(item => {
                                            const delay = item.bomDelayCount || 0;
                                            const isUrgent = delay > 5;
                                            const isOverdue = delay > 0;
                                            const engineer = item.engineerConfirmation ? item.engineerConfirmation.trim() : '';
                                            const isUnassigned = !engineer || engineer === '-' || engineer.toLowerCase() === 'unassigned' || engineer.toLowerCase() === 'null';

                                            return (
                                                <div 
                                                    key={item.id} 
                                                    onClick={() => setSidebarItemId(item.id)}
                                                    className={`p-2.5 rounded-xl border cursor-pointer ${isUrgent || isOverdue ? 'bg-pantone-50/80 border-pantone-200' : 'bg-white border-slate-200/70'} flex items-start space-x-2.5 shadow-sm transition-all hover:border-pantone-300 hover:shadow-md`}
                                                >
                                                    <div className={`w-7 h-7 rounded-lg ${isUrgent ? 'bg-pantone-700 text-white' : isOverdue ? 'bg-red-600 text-white' : 'bg-amber-500 text-white'} flex items-center justify-center shrink-0 mt-0.5 text-[11px]`}>
                                                        <i className={isUrgent ? 'fa-solid fa-fire' : isOverdue ? 'fa-solid fa-triangle-exclamation' : 'fa-solid fa-user-slash'}></i>
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-center justify-between">
                                                            <span className="text-xs font-extrabold text-slate-900 font-mono truncate">{item.mpModel || 'N/A'}</span>
                                                            <span className="text-[10px] font-mono text-slate-400 truncate ml-1">{item.devModel || 'N/A'}</span>
                                                        </div>
                                                        <div className="flex items-center space-x-1.5 mt-1 flex-wrap gap-y-1">
                                                            {isUrgent ? (
                                                                <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-pantone-700 text-white">Urgent</span>
                                                            ) : (
                                                                <span className="text-[9px] font-medium px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 border border-slate-200">Normal</span>
                                                            )}

                                                            {isOverdue ? (
                                                                <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-red-100 text-red-700 border border-red-200">Overdue</span>
                                                            ) : (
                                                                <span className="text-[9px] font-medium px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 border border-emerald-200">On Schedule</span>
                                                            )}

                                                            {isUnassigned ? (
                                                                <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 border border-amber-200">Unassigned</span>
                                                            ) : (
                                                                <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-slate-100 text-slate-700 border border-slate-200 truncate max-w-[80px]">{item.engineerConfirmation}</span>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>

                                    <div className="p-2.5 bg-white border-t border-slate-100 flex items-center justify-between text-xs px-3">
                                        <span className="text-[10px] text-slate-400 font-medium">
                                            Page <strong className="text-slate-700 font-mono">{safeQueuePage}</strong> of <strong className="text-slate-700 font-mono">{totalQueuePages}</strong>
                                        </span>
                                        <div className="flex items-center space-x-1">
                                            <button 
                                                onClick={() => setQueuePage(p => Math.max(1, p - 1))}
                                                disabled={safeQueuePage === 1}
                                                className={`w-6 h-6 rounded flex items-center justify-center border text-[10px] transition-colors ${safeQueuePage === 1 ? 'text-slate-300 border-slate-100 bg-slate-50 cursor-not-allowed' : 'text-slate-600 border-slate-200 hover:bg-pantone-700 hover:text-white hover:border-pantone-700'}`}
                                            >
                                                <i className="fa-solid fa-chevron-left"></i>
                                            </button>
                                            <button 
                                                onClick={() => setQueuePage(p => Math.min(totalQueuePages, p + 1))}
                                                disabled={safeQueuePage === totalQueuePages || totalQueuePages === 0}
                                                className={`w-6 h-6 rounded flex items-center justify-center border text-[10px] transition-colors ${safeQueuePage === totalQueuePages || totalQueuePages === 0 ? 'text-slate-300 border-slate-100 bg-slate-50 cursor-not-allowed' : 'text-slate-600 border-slate-200 hover:bg-pantone-700 hover:text-white hover:border-pantone-700'}`}
                                            >
                                                <i className="fa-solid fa-chevron-right"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </section>
                        )}

                        {/* Filter Toolbar */}
                        <section className="flex-none bg-white p-3.5 sm:p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col space-y-3">
                            <div className="flex flex-col xl:flex-row items-stretch xl:items-center justify-between gap-4">
                                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full xl:w-auto overflow-x-auto pb-1 xl:pb-0">
                                    <div className="flex items-center space-x-2 shrink-0">
                                        <div className="flex items-center space-x-1.5 bg-slate-100/80 p-1 rounded-xl border border-slate-200/60">
                                            <i className="fa-regular fa-calendar text-pantone-700 text-xs pl-2"></i>
                                            <select
                                                value={selectedYear}
                                                onChange={(e) => {
                                                    const val = e.target.value;
                                                    setSelectedYear(val === 'ALL' ? '27Y' : val);
                                                    setPage(1);
                                                    setQueuePage(1);
                                                }}
                                                className="bg-transparent text-xs font-bold text-slate-800 pr-2 py-1 outline-none cursor-pointer"
                                            >
                                                <option value="ALL">All Years</option>
                                                {yearOptions.map(yr => (
                                                    <option key={yr} value={yr}>
                                                        {yr}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>

                                        <label className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-100/80 hover:bg-slate-200/80 rounded-xl border border-slate-200/60 text-xs font-bold text-slate-700 cursor-pointer transition-all select-none">
                                            <input
                                                type="checkbox"
                                                checked={prioritization}
                                                onChange={(e) => handleTogglePrioritization(e.target.checked)}
                                                className="rounded border-slate-300 text-pantone-700 focus:ring-pantone-700 w-3.5 h-3.5 cursor-pointer"
                                            />
                                            <i className="fa-solid fa-arrow-down-short-wide text-pantone-700 text-xs"></i>
                                            <span>Prioritization</span>
                                        </label>

                                        <button 
                                            disabled={isBatchRetesting} 
                                            onClick={handleRetestAction} 
                                            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 whitespace-nowrap ${
                                                isBatchRetesting 
                                                    ? 'bg-slate-200 text-slate-400 border border-slate-300 cursor-not-allowed' 
                                                    : 'bg-pantone-700 hover:bg-pantone-800 text-white'
                                            }`}
                                        >
                                            <i className={`fa-solid ${isBatchRetesting ? 'fa-spinner fa-spin text-slate-400' : 'fa-rotate-right text-[11px]'}`}></i>
                                            <span>{isBatchRetesting ? formatTime(timer) : 'Retest'}</span>
                                        </button>
                                        <button onClick={handleCheckAction} className="px-3.5 py-2 bg-pantone-50 hover:bg-pantone-100 text-pantone-800 border border-pantone-200 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 whitespace-nowrap">
                                            <i className="fa-solid fa-clipboard-check text-[11px]"></i><span>Check</span>
                                        </button>
                                        <button onClick={downloadCSVReport} className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 whitespace-nowrap">
                                            <i className="fa-solid fa-file-arrow-down text-[11px]"></i><span>Download Result</span>
                                        </button>
                                        <button 
                                            onClick={handleToggleKpis} 
                                            className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300/80 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 whitespace-nowrap"
                                        >
                                            <i className={`fa-solid ${showKpis ? 'fa-eye-slash' : 'fa-chart-pie'} text-[11px]`}></i>
                                            <span>{showKpis ? 'Hide Header' : 'Show Headers'}</span>
                                        </button>
                                    </div>
                                    <div className="hidden sm:block h-6 w-px bg-slate-200 shrink-0"></div>
                                    <div className="flex items-center space-x-3 shrink-0 overflow-x-auto">
                                        <div className="flex items-center space-x-1 bg-slate-100/80 p-1 rounded-xl border border-slate-200/60 overflow-x-auto">
                                            <button onClick={() => handleSetFilter('ALL')} className={`tab-btn px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap ${filter === 'ALL' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600 hover:text-slate-900'}`}>
                                                <span>All</span><span className="bg-slate-200 text-slate-700 text-[10px] px-1.5 py-0.5 rounded-md font-mono">{totalBOM}</span>
                                            </button>
                                            <button onClick={() => handleSetFilter('OK')} className={`tab-btn px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap ${filter === 'OK' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600 hover:text-slate-900'}`}>
                                                <span className="w-2 h-2 rounded-full bg-emerald-500"></span><span>OK</span><span className="bg-emerald-100 text-emerald-800 text-[10px] px-1.5 py-0.5 rounded-md font-mono">{okCount}</span>
                                            </button>
                                            <button onClick={() => handleSetFilter('NG')} className={`tab-btn px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap ${filter === 'NG' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600 hover:text-slate-900'}`}>
                                                <span className="w-2 h-2 rounded-full bg-pantone-700"></span><span>NG Only</span><span className="bg-pantone-100 text-pantone-800 text-[10px] px-1.5 py-0.5 rounded-md font-mono">0</span>
                                            </button>
                                            <button onClick={() => handleSetFilter('CHECK')} className={`tab-btn px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap ${filter === 'CHECK' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600 hover:text-slate-900'}`}>
                                                <span className="w-2 h-2 rounded-full bg-blue-500"></span><span>Check</span><span className="bg-blue-100 text-blue-800 text-[10px] px-1.5 py-0.5 rounded-md font-mono">{totalCheck}</span>
                                            </button>
                                        </div>
                                        <div className="flex items-center space-x-2 border-l border-slate-200 pl-3">
                                            <button onClick={handleToggleUrgent} className={`px-3 py-1.5 border rounded-xl text-xs font-semibold transition-all flex items-center space-x-1.5 whitespace-nowrap ${urgentOnly || filter === 'URGENT' ? 'bg-pantone-700 text-white border-pantone-700' : 'border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
                                                <i className="fa-solid fa-fire text-pantone-600"></i><span>Urgent Only</span>
                                            </button>

                                            <button 
                                                onClick={handleToggleSystemOnly} 
                                                className={`px-3 py-1.5 border rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 whitespace-nowrap ${
                                                    systemOnly 
                                                        ? 'bg-amber-600 text-white border-amber-600 shadow-sm' 
                                                        : 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100'
                                                }`}
                                            >
                                                <i className={`fa-solid fa-triangle-exclamation ${systemOnly ? 'text-white' : 'text-amber-600'}`}></i>
                                                <span>System Initial</span>
                                                <span className={`text-[10px] px-1.5 py-0.2 rounded-md font-mono font-bold ${systemOnly ? 'bg-amber-700 text-white' : 'bg-amber-200 text-amber-900'}`}>
                                                    {systemUpdaterCount}
                                                </span>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <div className="relative w-full xl:w-72 shrink-0">
                                    <i className="fa-solid fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                                    <input type="text" value={search} onChange={(e) => handleSearch(e.target.value)} placeholder="Search model, structure, initial..." className="w-full pl-9 pr-8 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-pantone-700/30" />
                                    {search && (
                                        <button onClick={() => handleSearch('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs">
                                            <i className="fa-solid fa-circle-xmark"></i>
                                        </button>
                                    )}
                                </div>
                            </div>
                            {(filter !== 'ALL' || search.trim() !== '' || urgentOnly || systemOnly || startDate !== '' || endDate !== '' || selectedYear !== 'ALL') && (
                                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs flex-wrap gap-2">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-slate-400 font-medium">Active Filter:</span>
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full font-bold bg-pantone-50 text-pantone-800 border border-pantone-200">{getFilterBannerText()}</span>
                                    </div>
                                    <button onClick={resetAllFilters} className="text-pantone-700 hover:text-pantone-900 font-bold text-[11px] hover:underline flex items-center space-x-1">
                                        <i className="fa-solid fa-rotate-left text-[10px]"></i><span>Reset All Filters</span>
                                    </button>
                                </div>
                            )}
                        </section>

                        {/* Complete Data Table */}
                        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col w-full flex-1 min-h-[300px]">
                            <div className="p-3 bg-slate-50/90 border-b border-slate-200 flex items-center justify-between flex-wrap gap-3">
                                <div className="flex items-center space-x-2">
                                    <i className="fa-solid fa-table-columns text-slate-500 text-xs"></i>
                                    <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Table View Options</span>
                                </div>

                                <div className="flex items-center space-x-3 flex-wrap gap-y-2">
                                    <div className="flex items-center space-x-1.5 bg-white p-1 rounded-xl border border-slate-200 shadow-sm text-xs">
                                        <span className="text-slate-500 font-bold px-2 text-[11px] flex items-center space-x-1">
                                            <i className="fa-regular fa-calendar-days text-pantone-700"></i>
                                            <span className="hidden sm:inline">BOM Date:</span>
                                        </span>
                                        <input
                                            type="date"
                                            value={startDate}
                                            onChange={(e) => { setStartDate(e.target.value); setPage(1); }}
                                            className="px-2 py-1 bg-slate-50 border border-slate-200 rounded-lg text-xs font-mono"
                                        />
                                        <span className="text-slate-400 font-medium">to</span>
                                        <input
                                            type="date"
                                            value={endDate}
                                            onChange={(e) => { setEndDate(e.target.value); setPage(1); }}
                                            className="px-2 py-1 bg-slate-50 border border-slate-200 rounded-lg text-xs font-mono"
                                        />
                                        <button
                                            type="button"
                                            onClick={handleSetCurrentDate}
                                            className="px-2.5 py-1 bg-pantone-50 hover:bg-pantone-700 hover:text-white text-pantone-800 border border-pantone-200 rounded-lg text-[11px] font-bold transition-all flex items-center space-x-1 whitespace-nowrap"
                                        >
                                            <i className="fa-solid fa-clock text-[10px]"></i>
                                            <span>Today</span>
                                        </button>
                                        {(startDate || endDate) && (
                                            <button
                                                type="button"
                                                onClick={handleClearDateRange}
                                                className="px-1.5 py-1 text-slate-400 hover:text-slate-700 transition-colors"
                                            >
                                                <i className="fa-solid fa-circle-xmark text-xs"></i>
                                            </button>
                                        )}
                                    </div>

                                    <div className="relative inline-block text-left" ref={dropdownRef}>
                                        <button
                                            type="button"
                                            onClick={() => setIsGroupDropdownOpen(!isGroupDropdownOpen)}
                                            className="px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 rounded-xl text-xs font-semibold shadow-sm transition-all flex items-center space-x-2"
                                        >
                                            <i className="fa-solid fa-eye-slash text-slate-500 text-[11px]"></i>
                                            <span>Column Groups</span>
                                            <i className={`fa-solid fa-chevron-down text-[10px] transition-transform duration-200 ${isGroupDropdownOpen ? 'rotate-180' : ''}`}></i>
                                        </button>

                                        {isGroupDropdownOpen && (
                                            <div className="origin-top-right absolute right-0 mt-2 w-64 rounded-xl shadow-lg bg-white border border-slate-200 ring-1 ring-black ring-opacity-5 divide-y divide-slate-100 z-30 focus:outline-none">
                                                <div className="p-2.5 space-y-1">
                                                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 py-1">Toggle Groups</div>
                                                    <label className="flex items-center px-2 py-1.5 hover:bg-slate-50 rounded-lg cursor-pointer text-xs text-slate-700 select-none">
                                                        <input
                                                            type="checkbox"
                                                            checked={visibleGroups.group2}
                                                            onChange={() => toggleGroupVisibility('group2')}
                                                            className="rounded border-slate-300 text-pantone-700 mr-2.5"
                                                        />
                                                        <span className="font-medium">Group 2: Structure & Crosscheck</span>
                                                    </label>

                                                    <label className="flex items-center px-2 py-1.5 hover:bg-slate-50 rounded-lg cursor-pointer text-xs text-slate-700 select-none">
                                                        <input
                                                            type="checkbox"
                                                            checked={visibleGroups.group3}
                                                            onChange={() => toggleGroupVisibility('group3')}
                                                            className="rounded border-slate-300 text-pantone-700 mr-2.5"
                                                        />
                                                        <span className="font-medium">Group 3: Model Regional</span>
                                                    </label>

                                                    <label className="flex items-center px-2 py-1.5 hover:bg-slate-50 rounded-lg cursor-pointer text-xs text-slate-700 select-none">
                                                        <input
                                                            type="checkbox"
                                                            checked={visibleGroups.group4}
                                                            onChange={() => toggleGroupVisibility('group4')}
                                                            className="rounded border-slate-300 text-pantone-700 mr-2.5"
                                                        />
                                                        <span className="font-medium">Group 4: Circuit & Responsibilities</span>
                                                    </label>
                                                </div>

                                                <div className="p-2 flex items-center justify-between bg-slate-50/80 rounded-b-xl">
                                                    <button
                                                        onClick={() => toggleAllGroups(true)}
                                                        className={`text-[11px] font-bold px-2 py-1 rounded hover:underline ${areAllGroupsVisible ? 'text-slate-400 cursor-default' : 'text-pantone-700'}`}
                                                        disabled={areAllGroupsVisible}
                                                    >
                                                        Show All
                                                    </button>
                                                    <button
                                                        onClick={() => toggleAllGroups(false)}
                                                        className="text-[11px] font-bold text-slate-600 hover:text-slate-900 px-2 py-1 rounded hover:underline"
                                                    >
                                                        Hide All Groups
                                                    </button>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="overflow-auto w-full flex-1 min-h-0">
                                <table className="w-full text-left text-xs border-collapse min-w-full">
                                    <thead className="sticky top-0 z-30">
                                        <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[11px] whitespace-nowrap">
                                            <th className="py-3.5 px-4 w-28 text-center sticky left-0 bg-slate-50 z-20 border-r border-slate-200 shadow-sm">
                                                <div className="flex items-center justify-center space-x-2">
                                                    <input type="checkbox" checked={selectedIds.size > 0 && selectedIds.size === filteredData.length} onChange={(e) => toggleSelectAllRows(e.target.checked)} className="rounded border-slate-300 text-pantone-700" />
                                                    <span className="text-[10px] text-slate-400 font-normal">Select</span>
                                                </div>
                                            </th>
                                            <th className="py-3.5 px-4">MP Model</th>
                                            <th className="py-3.5 px-4">Dev Model</th>
                                            <th className="py-3.5 px-4">Initial Model</th>
                                            <th className="py-3.5 px-4 text-center">Delay Count</th>
                                            <th className="py-3.5 px-4 text-center">Result</th>
                                            <th className="py-3.5 px-4">Engineer Confirmation</th>
                                            <th className="py-3.5 px-4">Time Status</th>
                                            <th className="py-3.5 px-4">BOM Delay Status</th>
                                            <th className="py-3.5 px-4">Additional Remarks</th>

                                            {visibleGroups.group2 && (
                                                <>
                                                    <th className="py-3.5 px-4 bg-slate-100/60 border-l border-slate-200">Structure</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60">Ben Compare</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60">HW Tool</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60">Substitute Check</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60">Tool Option</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60">Operation Plan</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60 border-r border-slate-200">Compare Note</th>
                                                </>
                                            )}

                                            {visibleGroups.group3 && (
                                                <>
                                                    <th className="py-3.5 px-4 bg-slate-100/60 border-l border-slate-200">Year</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60">Model Subsidiary</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60">Model Series</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60">Model Region</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60 border-r border-slate-200">Model Country</th>
                                                </>
                                            )}

                                            {visibleGroups.group4 && (
                                                <>
                                                    <th className="py-3.5 px-4 bg-slate-100/60 border-l border-slate-200">Model Circuit PIC</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60">Engineer Checkouter</th>
                                                    <th className="py-3.5 px-4 bg-slate-100/60">BOM Last Checker</th>
                                                </>
                                            )}
                                            
                                            <th className="py-3.5 px-4 border-l border-slate-200">BOM Release Date</th>
                                            <th className="py-3.5 px-4 text-right sticky right-0 bg-slate-50 z-20 border-l border-slate-200 shadow-sm">Actions & Details</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100 font-normal whitespace-nowrap">
                                        {paginatedData.map(item => {
                                            const isChecked = selectedIds.has(item.id);
                                            const isActive = sidebarItemId === item.id;
                                            const isRowRetesting = activeRetestId === item.id;
                                            const isInitialUpdaterSystem = isSystemUpdater(item);

                                            return (
                                                <tr 
                                                    key={item.id} 
                                                    onClick={() => handleRowClick(item.id)} 
                                                    className={`cursor-pointer transition-all hover:bg-pantone-50/50 ${isChecked ? 'bg-pantone-50/40' : ''} ${isActive ? 'bg-pantone-200/45 border-l-4 border-pantone-700' : ''}`}
                                                >
                                                    <td className="py-3 px-4 text-center sticky left-0 bg-white z-10 border-r border-slate-100">
                                                        <div className="flex items-center justify-center space-x-2">
                                                            <input 
                                                                type="checkbox" 
                                                                checked={isChecked} 
                                                                onClick={e => e.stopPropagation()} 
                                                                onChange={(e) => handleCheckboxToggle(item.id, e.target.checked)} 
                                                                className="rounded border-slate-300 text-pantone-700" 
                                                            />
                                                            <button 
                                                                onClick={(e) => { e.stopPropagation(); setSidebarItemId(item.id); }} 
                                                                title="View Details" 
                                                                className="w-6 h-6 rounded-lg bg-slate-100 hover:bg-pantone-700 hover:text-white text-slate-600 transition-colors flex items-center justify-center text-[11px]"
                                                            >
                                                                <i className="fa-solid fa-eye"></i>
                                                            </button>
                                                            <button 
                                                                onClick={(e) => { e.stopPropagation(); downloadSingleItemReport(item.id); }} 
                                                                title="Export Report" 
                                                                className="w-6 h-6 rounded-lg bg-pantone-50 hover:bg-pantone-800 hover:text-white text-pantone-700 transition-colors flex items-center justify-center text-[11px]"
                                                            >
                                                                <i className="fa-solid fa-file-arrow-down"></i>
                                                            </button>
                                                        </div>
                                                    </td>
                                                    
                                                    <td className="py-3 px-4 font-bold text-slate-900 font-mono">
                                                        <div className="inline-flex items-center space-x-2">
                                                            <span>{item.mpModel || 'N/A'}</span>
                                                            {isInitialUpdaterSystem && (
                                                                <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded bg-amber-100 border border-amber-300 text-amber-800 text-[10px] font-sans font-bold">
                                                                    <i className="fa-solid fa-triangle-exclamation text-amber-600 animate-pulse"></i>
                                                                    <span>System</span>
                                                                </span>
                                                            )}
                                                        </div>
                                                    </td>
                                                    
                                                    <td className="py-3 px-4 text-slate-600 font-medium font-mono">{item.devModel || 'N/A'}</td>
                                                    <td className="py-3 px-4 text-slate-600 font-medium font-mono">{item.initialModel || 'N/A'}</td>
                                                    <td className="py-3 px-4 text-center font-mono font-semibold text-slate-700">{(item.bomDelayCount || 0).toLocaleString()}</td>
                                                    <td className="py-3 px-4 text-center">
                                                        {item.result === 'OK' && <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200"><i className="fa-solid fa-circle-check text-[9px] mr-1"></i>OK</span>}
                                                        {item.result === 'NG' && <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-pantone-100 text-pantone-800 border border-pantone-300"><i className="fa-solid fa-circle-xmark text-[9px] mr-1"></i>NG</span>}
                                                        {item.result === 'CHECK' && <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-blue-100 text-blue-800 border border-blue-200"><i className="fa-solid fa-hourglass-half text-[9px] mr-1"></i>CHECK</span>}
                                                    </td>
                                                    <td className="py-3 px-4">
                                                        {item.engineerConfirmation && item.engineerConfirmation.trim() !== '' && item.engineerConfirmation !== '-' ? (
                                                            <span className="font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 font-mono text-[11px]">{item.engineerConfirmation}</span>
                                                        ) : (
                                                            <span className="inline-flex items-center text-pantone-700 bg-pantone-50 px-2 py-0.5 rounded border border-pantone-200 font-medium text-[11px]"><i className="fa-solid fa-user-slash mr-1 text-[9px]"></i>Unassigned</span>
                                                        )}
                                                    </td>
                                                    <td className="py-3 px-4">
                                                        {(item.bomDelayCount || 0) > 5 ? <span className="inline-flex items-center text-pantone-700 font-bold bg-pantone-50 px-2 py-0.5 rounded border border-pantone-200 text-[10px]"><i className="fa-solid fa-fire mr-1"></i>Urgent</span> : <span className="text-slate-400 font-normal">Normal</span>}
                                                    </td>
                                                    <td className="py-3 px-4">
                                                        {(item.bomDelayCount || 0) > 0 ? <span className="inline-flex items-center text-red-700 font-bold bg-red-100 px-1.5 py-0.5 rounded text-[10px]">Overdue</span> : <span className="text-emerald-600 font-medium">On Schedule</span>}
                                                    </td>
                                                    <td className="py-3 px-4">
                                                        {item.additionalRemark && item.additionalRemark.trim() !== '' && item.additionalRemark !== '-' ? <span className="text-slate-700 truncate max-w-xs block">{item.additionalRemark}</span> : <span className="text-slate-400 italic">None</span>}
                                                    </td>

                                                    {visibleGroups.group2 && (
                                                        <>
                                                            <td className="py-3 px-4 font-mono text-slate-700 bg-slate-50/40 border-l border-slate-100">{item.structure || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40">{item.benComp || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40">{item.hwTool || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40">{item.substituteCheck || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40">{item.toolOption || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40">{item.operationPlan || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 max-w-xs truncate bg-slate-50/40 border-r border-slate-100">{item.compareNote || 'N/A'}</td>
                                                        </>
                                                    )}

                                                    {visibleGroups.group3 && (
                                                        <>
                                                            <td className="py-3 px-4 font-mono text-slate-700 bg-slate-50/40 border-l border-slate-100">{item.year || item.modelYear || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40">{item.modelSubsidiary || item.plant || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40">{item.modelSeries || item.series || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40">{item.modelRegion || item.region || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40 border-r border-slate-100">{item.market || 'N/A'}</td>
                                                        </>
                                                    )}

                                                    {visibleGroups.group4 && (
                                                        <>
                                                            <td className="py-3 px-4 text-slate-700 font-mono bg-slate-50/40 border-l border-slate-100">{item.modelCircuitPic || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40">{item.engineerConfirmation || 'N/A'}</td>
                                                            <td className="py-3 px-4 text-slate-700 bg-slate-50/40">{item.bomTeam || 'N/A'}</td>
                                                        </>
                                                    )}

                                                    <td className="py-3 px-4 font-mono text-slate-600 border-l border-slate-100 font-semibold">{item.bomReleaseDate || 'N/A'}</td>

                                                    <td className="py-3 px-4 text-right sticky right-0 bg-white z-10 border-l border-slate-100">
                                                        <div className="inline-flex items-center space-x-1">
                                                            <button 
                                                                disabled={isRowRetesting}
                                                                onClick={(e) => { e.stopPropagation(); handleSingleRowRetest(item.id); }} 
                                                                className={`px-2 py-1 rounded-lg font-bold transition-all text-[11px] flex items-center space-x-1 ${
                                                                    isRowRetesting
                                                                        ? 'bg-slate-200 text-slate-400 border border-slate-300 cursor-not-allowed'
                                                                        : 'bg-pantone-50 hover:bg-pantone-700 hover:text-white text-pantone-800 border border-pantone-200'
                                                                }`}
                                                            >
                                                                <i className={`fa-solid ${isRowRetesting ? 'fa-spinner fa-spin text-slate-400' : 'fa-rotate-right text-[10px]'}`}></i>
                                                                <span>{isRowRetesting ? formatTime(timer) : 'Retest'}</span>
                                                            </button>
                                                            <button 
                                                                onClick={(e) => { e.stopPropagation(); handleSingleRowCheck(item.id); }} 
                                                                className="px-2 py-1 bg-emerald-50 hover:bg-emerald-600 hover:text-white text-emerald-800 border border-emerald-200 rounded-lg font-bold transition-all text-[11px] flex items-center space-x-1"
                                                            >
                                                                <i className="fa-solid fa-check text-[10px]"></i><span>Pass</span>
                                                            </button>
                                                            <button 
                                                                onClick={(e) => { e.stopPropagation(); setSidebarItemId(item.id); }} 
                                                                className="px-2 py-1 bg-slate-100 hover:bg-slate-800 hover:text-white text-slate-700 rounded-lg font-semibold transition-all text-[11px]"
                                                            >
                                                                <i className="fa-solid fa-angles-right text-[10px]"></i>
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>

                            {paginatedData.length === 0 && (
                                <div className="p-12 text-center flex flex-col items-center justify-center space-y-3">
                                    <div className="w-12 h-12 rounded-full bg-pantone-50 text-pantone-700 flex items-center justify-center text-lg mx-auto"><i className="fa-solid fa-folder-open"></i></div>
                                    <p className="text-sm font-semibold text-slate-700">No BOM inspection items found</p>
                                    <p className="text-xs text-slate-500">Try adjusting your active KPI card filter, year, date range, or search query.</p>
                                    <button onClick={resetAllFilters} className="text-xs text-pantone-700 font-bold hover:underline">Reset All Filters</button>
                                </div>
                            )}

                            <div className="flex-none px-4 py-2.5 bg-slate-50/60 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
                                <div className="flex items-center space-x-2">
                                    <span>Showing</span>
                                    <span className="font-bold text-slate-700 font-mono">{filteredData.length > 0 ? `${startIndex + 1} - ${Math.min(startIndex + itemsPerPage, filteredData.length)}` : '0 - 0'}</span>
                                    <span>of</span>
                                    <span className="font-bold text-slate-700 font-mono">{filteredData.length}</span>
                                    <span>entries</span>
                                </div>
                                
                                <div className="flex items-center space-x-1.5">
                                    <button 
                                        onClick={() => setPage(p => Math.max(1, p - 1))} 
                                        disabled={safePage === 1} 
                                        className={`w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 transition-colors ${safePage === 1 ? 'text-slate-300 cursor-not-allowed bg-slate-50' : 'text-slate-600 hover:bg-slate-100'}`}
                                    >
                                        <i className="fa-solid fa-chevron-left text-[10px]"></i>
                                    </button>
                                    
                                    {getPageNumbers().map(p => (
                                        <button 
                                            key={p} 
                                            onClick={() => setPage(p)} 
                                            className={`w-8 h-8 flex items-center justify-center rounded-lg font-mono text-xs transition-colors ${p === safePage ? 'bg-pantone-700 text-white font-bold' : 'border border-slate-200 text-slate-600 hover:bg-slate-100'}`}
                                        >
                                            {p}
                                        </button>
                                    ))}
                                    
                                    <button 
                                        onClick={() => setPage(p => Math.min(totalPages, p + 1))} 
                                        disabled={safePage === totalPages || totalPages === 0} 
                                        className={`w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 transition-colors ${safePage === totalPages || totalPages === 0 ? 'text-slate-300 cursor-not-allowed bg-slate-50' : 'text-slate-600 hover:bg-slate-100'}`}
                                    >
                                        <i className="fa-solid fa-chevron-right text-[10px]"></i>
                                    </button>
                                </div>
                            </div>
                        </section>
                    </main>
                </div>

                {/* Inspector Drawer Sidebar */}
                <aside id="right-sidebar" className={`fixed top-0 right-0 h-full w-full sm:w-[420px] bg-white border-l border-slate-200 shadow-2xl z-50 flex flex-col overflow-hidden transition-transform duration-300 ease-in-out ${isSidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}>
                    <div className="p-4 bg-gradient-to-r from-pantone-900 to-pantone-950 text-white flex items-center justify-between border-b border-pantone-800">
                        <div className="flex items-center space-x-2.5">
                            <div className="w-7 h-7 rounded-lg bg-pantone-800/80 flex items-center justify-center text-pantone-200 border border-pantone-600/50"><i className="fa-solid fa-sliders text-xs"></i></div>
                            <div>
                                <h3 className="font-bold text-sm leading-tight">{activeSidebarItem?.mpModel || 'Model Details'}</h3>
                                <p className="text-[10px] text-pantone-200/80 font-mono">{activeSidebarItem?.devModel || 'Inspection Spec Sheet'}</p>
                            </div>
                        </div>
                        <button onClick={() => setSidebarItemId(null)} className="w-8 h-8 rounded-lg hover:bg-pantone-800 text-pantone-200 hover:text-white transition-colors flex items-center justify-center"><i className="fa-solid fa-xmark text-sm"></i></button>
                    </div>

                    {activeSidebarItem && (
                        <div className="flex-1 flex flex-col overflow-hidden">
                            {/* RETEST RESULT POPUP CONTAINER */}
                            {retestResult && (
                                <div className="p-4 border-b border-slate-200 shrink-0">
                                    <div className={`p-4 rounded-2xl shadow-lg border text-white space-y-3 relative overflow-hidden ${
                                        (retestResult?.report?.status || retestResult?.status) === 'error' || retestResult?.get_result === 'Ng' || retestResult?.all_result?.overallResult === 'NG'
                                            ? 'bg-gradient-to-br from-red-600 via-rose-700 to-red-900 border-red-500/50'
                                            : 'bg-gradient-to-br from-emerald-600 via-teal-700 to-emerald-900 border-emerald-500/50'
                                    }`}>
                                        <div className="flex items-center justify-between pb-2 border-b border-white/20">
                                            <div className="flex items-center space-x-2">
                                                <i className={`fa-solid ${
                                                    (retestResult?.report?.status || retestResult?.status) === 'error' || retestResult?.get_result === 'Ng'
                                                        ? 'fa-triangle-exclamation text-red-200 animate-pulse'
                                                        : 'fa-circle-check text-emerald-200'
                                                }`}></i>
                                                <span className="font-extrabold text-xs uppercase tracking-wider">
                                                    Retest Report: {retestResult?.report?.status || retestResult?.status || 'N/A'}
                                                </span>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <button 
                                                    onClick={() => setShowExceptionLog(!showExceptionLog)} 
                                                    title={showExceptionLog ? "Hide Exception Log" : "Open Exception Log"}
                                                    className={`transition-colors p-1 rounded-md ${showExceptionLog ? 'text-white bg-white/20' : 'text-white/70 hover:text-white'}`}
                                                >
                                                    <i className="fa-solid fa-file-lines text-xs"></i>
                                                </button>
                                                <button 
                                                    onClick={() => { setRetestResult(null); setShowExceptionLog(false); }} 
                                                    className="text-white/70 hover:text-white transition-colors p-1"
                                                >
                                                    <i className="fa-solid fa-xmark text-xs"></i>
                                                </button>
                                            </div>
                                        </div>

                                        {/* Result Summary Badges */}
                                        <div className="flex items-center justify-between text-xs bg-black/20 p-2 rounded-xl backdrop-blur-sm border border-white/10">
                                            <div>
                                                <span className="text-[10px] text-white/70 uppercase block font-semibold">Get Result</span>
                                                <span className="font-mono font-extrabold text-sm">{retestResult?.get_result || 'N/A'}</span>
                                            </div>
                                            <div className="text-right">
                                                <span className="text-[10px] text-white/70 uppercase block font-semibold">Overall Result</span>
                                                <span className="font-mono font-extrabold text-sm">{retestResult?.all_result?.overallResult || 'N/A'}</span>
                                            </div>
                                        </div>

                                        {/* Message & Compare Note */}
                                        <div className="space-y-1.5 text-xs">
                                            {retestResult?.message && (
                                                <p className="text-[11px] font-medium leading-snug text-white/90">
                                                    <strong className="text-white">Message:</strong> {retestResult.message}
                                                </p>
                                            )}
                                            {retestResult?.report?.message && (
                                                <p className="text-[11px] font-medium leading-snug text-white/90">
                                                    <strong className="text-white">Report Message:</strong> {retestResult.report.message}
                                                </p>
                                            )}
                                            {retestResult?.all_result?.compareNote && (
                                                <p className="text-[11px] leading-snug bg-black/20 p-2 rounded-lg text-white/90 border border-white/10">
                                                    <strong className="text-white block mb-0.5">Compare Note:</strong>
                                                    {retestResult.all_result.compareNote}
                                                </p>
                                            )}
                                        </div>

                                        {/* Exception Log & Errors - Hidden by default until report icon clicked */}
                                        {showExceptionLog && retestResult?.exceptionLog && retestResult.exceptionLog.length > 0 && (
                                            <div className="space-y-1.5 pt-2 border-t border-white/20">
                                                <span className="text-[10px] uppercase font-extrabold tracking-wider text-red-100 flex items-center space-x-1">
                                                    <i className="fa-solid fa-bug text-[10px]"></i>
                                                    <span>Exception Log & Error</span>
                                                </span>
                                                {retestResult.exceptionLog.map((log: any, idx: number) => (
                                                    <div key={idx} className="bg-black/30 p-2 rounded-xl text-[11px] space-y-1 border border-red-400/30">
                                                        <div className="flex items-center justify-between font-bold text-white">
                                                            <span>{log.stage || 'Pipeline Stage'}</span>
                                                            <span className="px-1.5 py-0.2 rounded bg-red-500/40 text-[9px] uppercase font-mono">{log.status}</span>
                                                        </div>
                                                        <p className="text-red-100 leading-tight font-mono text-[10px] break-words">{log.error}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            <div className="px-5 pt-4 bg-white border-b border-slate-100 flex space-x-2 shrink-0">
                                <button
                                    onClick={() => setSidebarTab('attributes')}
                                    className={`pb-2 px-3 text-xs font-bold border-b-2 transition-all ${sidebarTab === 'attributes' ? 'border-pantone-700 text-pantone-900' : 'border-transparent text-slate-400 hover:text-slate-700'}`}
                                >
                                    Component Attribute
                                </button>
                                <button
                                    onClick={() => setSidebarTab('profile')}
                                    className={`pb-2 px-3 text-xs font-bold border-b-2 transition-all ${sidebarTab === 'profile' ? 'border-pantone-700 text-pantone-900' : 'border-transparent text-slate-400 hover:text-slate-700'}`}
                                >
                                    Model Profile
                                </button>
                            </div>

                            <div className="p-5 overflow-y-auto flex-1 space-y-5 text-xs text-slate-700">
                                
                                <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200/80 flex items-center justify-between">
                                    <div>
                                        <span className="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">MP Model</span>
                                        <span className="font-mono font-extrabold text-pantone-950 text-base">{activeSidebarItem.mpModel}</span>
                                    </div>
                                    <div>
                                        {activeSidebarItem.result === 'OK' && <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200"><i className="fa-solid fa-circle-check text-[9px] mr-1"></i>OK Cleared</span>}
                                        {activeSidebarItem.result === 'NG' && <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-pantone-100 text-pantone-800 border border-pantone-300"><i className="fa-solid fa-circle-xmark text-[9px] mr-1"></i>NG Rejected</span>}
                                        {activeSidebarItem.result === 'CHECK' && <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-blue-100 text-blue-800 border border-blue-200"><i className="fa-solid fa-hourglass-half text-[9px] mr-1"></i>CHECK Pending</span>}
                                    </div>
                                </div>

                                {sidebarTab === 'attributes' ? (
                                    <>
                                        {isSystemUpdater(activeSidebarItem) && (
                                            <div className="p-3.5 bg-amber-50 border-2 border-amber-300/90 text-amber-900 rounded-xl flex items-start space-x-3 shadow-md animate-pulse">
                                                <i className="fa-solid fa-triangle-exclamation text-amber-600 text-lg mt-0.5 shrink-0"></i>
                                                <div>
                                                    <p className="font-extrabold text-xs tracking-wide uppercase text-amber-900">please verify Initial Model</p>
                                                    <p className="text-[11px] text-amber-800 font-medium leading-tight mt-0.5">
                                                        Initial updater is set by system default. Please double-check component data.
                                                    </p>
                                                </div>
                                            </div>
                                        )}

                                        {sidebarNotification && (
                                            <div className="px-3 py-2 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-lg text-[11px] font-bold flex items-center space-x-2 animate-pulse">
                                                <i className="fa-solid fa-circle-check"></i>
                                                <span>{sidebarNotification}</span>
                                            </div>
                                        )}
                                        {/* Crosscheck Configuration: nilai awal dari sistem, bisa di-override user lewat tombol pensil */}
                                        <div className="space-y-3">
                                            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider text-[11px] border-b border-slate-100 pb-1 flex items-center space-x-1.5"><i className="fa-solid fa-sliders text-pantone-700"></i><span>Crosscheck Configuration</span></h4>
                                            <div className="flex flex-col gap-3 bg-slate-50/70 p-3 rounded-xl border border-slate-100">
                                                {CROSSCHECK_CONFIG_FIELDS.map(field => {
                                                    const isEditing = editingConfig === field.key;
                                                    const savedValue = getConfigValues(activeSidebarItem)[field.key];
                                                    const inputValue = isEditing ? configDraft[field.key] : savedValue;
                                                    const canOpenLink = field.isLink && isValidHttpUrl(savedValue);
                                                    const iconBtn = 'w-8 h-8 shrink-0 rounded-lg border flex items-center justify-center transition-colors disabled:opacity-40 disabled:cursor-not-allowed';
                                                    return (
                                                        <div key={field.key}>
                                                            <label htmlFor={`cfg-${field.key}`} className="text-slate-400 font-medium block mb-1">{field.label}</label>
                                                            <div className="flex items-center gap-1.5">
                                                                <input
                                                                    id={`cfg-${field.key}`}
                                                                    type="text"
                                                                    value={inputValue}
                                                                    readOnly={!isEditing}
                                                                    autoFocus={isEditing}
                                                                    onChange={(e) => setConfigDraft(prev => ({ ...prev, [field.key]: e.target.value }))}
                                                                    onKeyDown={(e) => {
                                                                        if (!isEditing) return;
                                                                        if (e.key === 'Enter') handleUpdateModelInfo(field.key);
                                                                        if (e.key === 'Escape') cancelEditConfig();
                                                                    }}
                                                                    placeholder={isEditing ? field.placeholder : 'N/A'}
                                                                    title={inputValue}
                                                                    className={`flex-1 min-w-0 h-8 px-2.5 rounded-lg border text-xs font-bold outline-none transition-colors ${field.isLink ? 'font-sans' : 'font-mono'} ${
                                                                        isEditing
                                                                            ? 'bg-white border-pantone-700 text-slate-900 ring-2 ring-pantone-700/20'
                                                                            : 'bg-white/70 border-slate-200 text-slate-800 cursor-default'
                                                                    }`}
                                                                />
                                                                {isEditing ? (
                                                                    <>
                                                                        <button
                                                                            onClick={() => handleUpdateModelInfo(field.key)}
                                                                            disabled={isUpdatingModel}
                                                                            className={`${iconBtn} bg-pantone-700 border-pantone-700 text-white hover:bg-pantone-800`}
                                                                            title="Save"
                                                                        >
                                                                            {isUpdatingModel ? <i className="fa-solid fa-spinner fa-spin text-[11px]"></i> : <i className="fa-solid fa-check text-[11px]"></i>}
                                                                        </button>
                                                                        <button
                                                                            onClick={cancelEditConfig}
                                                                            disabled={isUpdatingModel}
                                                                            className={`${iconBtn} bg-white border-slate-200 text-slate-500 hover:text-slate-800 hover:bg-slate-100`}
                                                                            title="Cancel"
                                                                        >
                                                                            <i className="fa-solid fa-xmark text-[11px]"></i>
                                                                        </button>
                                                                    </>
                                                                ) : (
                                                                    <button
                                                                        onClick={() => startEditConfig(field.key)}
                                                                        disabled={isUpdatingModel}
                                                                        className={`${iconBtn} bg-white border-slate-200 text-slate-500 hover:text-pantone-700 hover:border-pantone-300 hover:bg-pantone-50`}
                                                                        title={`Edit ${field.label}`}
                                                                    >
                                                                        <i className="fa-solid fa-pen text-[11px]"></i>
                                                                    </button>
                                                                )}
                                                                {field.isLink && (
                                                                    <button
                                                                        onClick={() => window.open(savedValue, '_blank', 'noopener,noreferrer')}
                                                                        disabled={!canOpenLink}
                                                                        className={`${iconBtn} bg-white border-slate-200 text-slate-500 hover:text-pantone-700 hover:border-pantone-300 hover:bg-pantone-50`}
                                                                        title={canOpenLink ? 'Open in new tab' : 'No valid link yet'}
                                                                    >
                                                                        <i className="fa-solid fa-arrow-up-right-from-square text-[11px]"></i>
                                                                    </button>
                                                                )}
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>

                                        <div className="space-y-3">
                                            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider text-[11px] border-b border-slate-100 pb-1 flex items-center space-x-1.5"><i className="fa-solid fa-microscope text-pantone-700"></i><span>Crosschecking Information</span></h4>
                                            <div className="grid grid-cols-2 gap-3 bg-slate-50/70 p-3 rounded-xl border border-slate-100">
                                                <div><span className="text-slate-400 font-medium block">Compare Note</span><span className="font-medium text-pantone-800">{activeSidebarItem.compareNote || 'None'}</span></div>
                                                <div><span className="text-slate-400 font-medium block">Release Date</span><span className="font-mono text-slate-600 font-bold">{activeSidebarItem.bomReleaseDate || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block">BOM Team</span><span className="font-mono font-bold text-slate-700">{activeSidebarItem.bomTeam || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block">Engineer Conf.</span><span className="font-semibold text-slate-800">{activeSidebarItem.engineerConfirmation || 'Unassigned'}</span></div>
                                                <div><span className="text-slate-400 font-medium block">Region</span><span className="font-mono font-semibold text-slate-700">{activeSidebarItem.modelRegion || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block">Delay Count</span><span className="font-mono font-bold text-slate-800">{(activeSidebarItem.bomDelayCount || 0).toLocaleString()}</span></div>
                                                <div><span className="text-slate-400 font-medium block">Priority Level</span>{(activeSidebarItem.bomDelayCount || 0) > 5 ? <span className="text-pantone-700 font-bold"><i className="fa-solid fa-fire text-xs mr-1"></i>Urgent</span> : <span className="text-slate-500">Normal</span>}</div>
                                            </div>
                                        </div>
                                    </>
                                ) : (
                                    <div className="space-y-3">
                                        <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider text-[11px] border-b border-slate-100 pb-1 flex items-center space-x-1.5"><i className="fa-solid fa-tags text-pantone-700"></i><span>Model Profile Details</span></h4>
                                        
                                        {isProfileLoading ? (
                                            <div className="flex justify-center items-center p-8 text-slate-400">
                                                <i className="fa-solid fa-spinner fa-spin text-2xl"></i>
                                            </div>
                                        ) : (
                                            <div className="grid grid-cols-2 gap-3 bg-slate-50/70 p-3 rounded-xl border border-slate-100 font-mono">
                                                <div><span className="text-slate-400 font-medium block font-sans">ModelYear</span><span className="font-semibold text-slate-800">{fetchedProfile?.modelYear || activeSidebarItem.modelYear || activeSidebarItem.year || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block font-sans">Inch</span><span className="font-semibold text-slate-800">{fetchedProfile?.Inch || activeSidebarItem.inch || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block font-sans">Series</span><span className="font-semibold text-slate-800">{fetchedProfile?.Series || activeSidebarItem.modelSeries || activeSidebarItem.series || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block font-sans">Region</span><span className="font-semibold text-slate-800">{fetchedProfile?.Region || activeSidebarItem.modelRegion || activeSidebarItem.region || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block font-sans">Market</span><span className="font-semibold text-slate-800">{fetchedProfile?.Market || activeSidebarItem.market || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block font-sans">Board</span><span className="font-semibold text-slate-800">{fetchedProfile?.Board || activeSidebarItem.board || activeSidebarItem.modelSoc || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block font-sans">CP Unit</span><span className="font-semibold text-slate-800">{fetchedProfile?.CPunit || activeSidebarItem.cpUnit || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block font-sans">Panel</span><span className="font-semibold text-slate-800">{fetchedProfile?.Panel || activeSidebarItem.panel || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block font-sans">Remote</span><span className="font-semibold text-slate-800">{fetchedProfile?.RemoteMR || fetchedProfile?.RemoteSR || activeSidebarItem.remote || 'N/A'}</span></div>
                                                <div><span className="text-slate-400 font-medium block font-sans">Plant</span><span className="font-semibold text-slate-800">{fetchedProfile?.Plant || activeSidebarItem.plant || activeSidebarItem.modelSubsidiary || 'N/A'}</span></div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                <div className="space-y-3 pt-1">
                                    <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider text-[11px] border-b border-slate-100 pb-1 flex items-center space-x-1.5"><i className="fa-solid fa-pen-to-square text-pantone-700"></i><span>Update Inspection Notes</span></h4>
                                    <div>
                                        <label htmlFor="sb-initial-input" className="block font-semibold text-slate-700 mb-1">Engineer Confirmation</label>
                                        <input type="text" id="sb-initial-input" value={sbInitial} onChange={e => setSbInitial(e.target.value)} placeholder="e.g. J.D., M.R." className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold focus:ring-2 focus:ring-pantone-700/30" />
                                    </div>
                                    <div>
                                        <label htmlFor="sb-remarks-input" className="block font-semibold text-slate-700 mb-1">Remarks & Findings</label>
                                        <textarea id="sb-remarks-input" rows={3} value={sbRemarks} onChange={e => setSbRemarks(e.target.value)} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-pantone-700/30 placeholder:text-slate-400" placeholder="Enter defect description..."></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col space-y-2">
                        <button onClick={() => {
                            if (activeSidebarItem) {
                                const query = new URLSearchParams({
                                    targetModel: activeSidebarItem.mpModel || '',
                                    devModel: activeSidebarItem.devModel || '',
                                    initModel: activeSidebarItem.initialModel || ''
                                }).toString();
                                router.push(`/viewResult?${query}`); 
                            }
                        }} className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-xs shadow-md transition-all flex items-center justify-center space-x-2">
                            <i className="fa-solid fa-file-invoice text-pantone-300"></i><span>View Result (Full Detailed Report)</span>
                        </button>
                        <button onClick={saveSidebarChanges} className="w-full py-2 bg-pantone-700 hover:bg-pantone-800 text-white rounded-xl font-bold text-xs transition-all flex items-center justify-center space-x-1.5">
                            <i className="fa-solid fa-floppy-disk"></i><span>Save Sidebar Updates</span>
                        </button>
                        <div className="grid grid-cols-2 gap-2">
                            <button 
                                disabled={activeSidebarItem !== null && activeRetestId === activeSidebarItem.id} 
                                onClick={() => activeSidebarItem && handleSingleRowRetest(activeSidebarItem.id)} 
                                className={`py-2 border rounded-xl font-semibold text-xs transition-all flex items-center justify-center space-x-1.5 ${
                                    activeSidebarItem !== null && activeRetestId === activeSidebarItem.id
                                        ? 'bg-slate-200 text-slate-400 border-slate-300 cursor-not-allowed font-mono' 
                                        : 'bg-pantone-50 hover:bg-pantone-100 text-pantone-800 border-pantone-200'
                                }`}
                            >
                                <i className={`fa-solid ${activeSidebarItem !== null && activeRetestId === activeSidebarItem.id ? 'fa-spinner fa-spin text-slate-400' : 'fa-rotate-right text-pantone-700'}`}></i>
                                <span>
                                    {activeSidebarItem !== null && activeRetestId === activeSidebarItem.id ? formatTime(timer) : 'Retest Item'}
                                </span>
                            </button>
                            <button onClick={() => activeSidebarItem && handleSingleRowCheck(activeSidebarItem.id)} className="py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 rounded-xl font-semibold text-xs transition-all flex items-center justify-center space-x-1">
                                <i className="fa-solid fa-circle-check text-emerald-600"></i><span>Mark OK</span>
                            </button>
                        </div>
                    </div>
                </aside>
            </div>

            <div id="toast-container" className="fixed bottom-5 right-5 z-50 flex flex-col space-y-2 pointer-events-none">
                {toasts.map(t => (
                    <div key={t.id} className={`toast-animate px-4 py-3 rounded-xl border shadow-lg flex items-center space-x-2.5 text-xs font-semibold pointer-events-auto min-w-[260px] ${t.type === 'warning' ? 'bg-amber-800 text-white border-amber-600' : t.type === 'info' ? 'bg-slate-800 text-white border-slate-600' : 'bg-pantone-900 text-white border-pantone-700'}`}>
                        <i className={`fa-solid text-sm text-pantone-300 ${t.type === 'warning' ? 'fa-triangle-exclamation' : t.type === 'info' ? 'fa-circle-info' : 'fa-circle-check'}`}></i>
                        <span className="flex-1">{t.msg}</span>
                        <button onClick={() => setToasts(prev => prev.filter(x => x.id !== t.id))} className="text-slate-300 hover:text-white ml-2"><i className="fa-solid fa-xmark"></i></button>
                    </div>
                ))}
            </div>
        </>
    );
}