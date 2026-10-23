// src/app/viewResult/ViewResultClient.tsx
"use client";
// MENJADI (tambahkan structureExcludedKeys):
import { renderStructureTable, structureExcludedKeys, getStructureRows } from './table/renderStructureTable';
import { renderOperationPlanTable, getOperationPlanRows } from './table/renderOperationPlanTable';
import { renderToolOptionTable, getAllCompareToolRows } from './table/renderToolOptionTable';
import { renderSubstituteSection, getAllSubstituteRows } from './table/renderSubstituteTable';
import { renderAssyReleaseStatusTable, getAssyReleaseStatusSummaryRows } from './table/renderAssyReleaseStatusTable';
import { renderHwSingleOptionTable, getHwSingleOptionRows } from './table/renderHwSingleOptionTable';
import { renderHwMultiOptionSection, getAllHwMultiOptionRows } from './table/renderHwMultiOptionTable';
import { renderEaxSubstituteTable, getEaxSubstituteRows } from './table/renderEaxSubstituteTable';
import { renderCheckPartSection, getAllCheckPartRows } from './table/renderCheckPartTable';
import { renderCrosscheckingResultTable, getCrosscheckingResultRows } from './table/renderCrosscheckingResultTable';
import {
  id,
  setText,
  safeString,
  escapeHtml,
  formatRawJsonValue,
  collectKeys,
  getPath,
  getFirstAvailablePath,
  normalizeTableRows,
  camelToTitle,
  truncateTextToThreeWords,
  refreshMergedCategoryCells
} from './table/tableUtils';
import React, { useEffect, useRef } from 'react';
import type { BomCrosscheckConfig } from '@/lib/bomAccessServer';
import Head from 'next/head';
import { useSearchParams, useRouter } from 'next/navigation';

interface ViewResultProps {
  initialData?: any[];
  // Ditentukan server di page.tsx: true = pemilik BOM / user khusus (Edit mode), false = View only
  canEdit?: boolean;
  userName?: string | null;
  // Crosscheck Configuration dari drawer My BOM (nama model di header tabel & link JIRA Power Cons.)
  bomConfig?: BomCrosscheckConfig | null;
}

type ResultStatus =
  | 'OK'
  | 'NG'
  | 'CHECK'
  | 'SAME'
  | 'DIFFERENT';

export default function ViewResultClient({ initialData, canEdit = false, userName = null, bomConfig = null }: ViewResultProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const listenersAttached = useRef(false);

  useEffect(() => {
    // ==========================================
    // VANILLA JS / DOM LOGIC ENCAPSULATED
    // ==========================================
    const queryParams = searchParams ?? new URLSearchParams();

    let currentMasterJson: any = null;

    // ==========================================
    // MODE HALAMAN: EDIT / VIEW ONLY
    // - Ditentukan di server (page.tsx -> src/lib/bomAccessServer.ts), bukan dari URL
    // - View only: Engineer Check & Remarks hanya ditampilkan (tidak bisa diubah),
    //   tombol Save Draft / Engineer Confirm / Resolve Next Issue disembunyikan
    // ==========================================
    const isViewOnly = !canEdit;

    /** Kunci semua input review di dalam root (dipanggil ulang setiap kali tabel di-render) */
    function applyViewOnlyMode(root: ParentNode = document) {
      if (!isViewOnly) return;
      root.querySelectorAll<HTMLSelectElement>('select.engineer-confirm-select, select.result-select').forEach(el => {
        el.disabled = true;
        el.tabIndex = -1;
      });
      root.querySelectorAll<HTMLInputElement>('input.remark-input').forEach(el => {
        el.readOnly = true;
        el.tabIndex = -1;
        el.placeholder = '';
      });
    }

    // Tabel dibuat lewat innerHTML di banyak tempat, jadi setiap ada elemen baru langsung dikunci
    let viewOnlyObserver: MutationObserver | null = null;
    const viewOnlyRoot = document.querySelector('.main-container');
    if (isViewOnly && viewOnlyRoot) {
      applyViewOnlyMode(viewOnlyRoot);
      viewOnlyObserver = new MutationObserver(() => applyViewOnlyMode(viewOnlyRoot));
      viewOnlyObserver.observe(viewOnlyRoot, { childList: true, subtree: true });
    }

    // ==========================================
    // DAFTAR MODUL / TAB
    // - Urutan array = urutan default tab dari kiri
    // - defaultVisible: tampil saat halaman dibuka; sisanya disembunyikan dan bisa dibuka lewat "Show Tab"
    // - inSummary: ikut dihitung di sidebar summary (NG / Different / OK), progress review,
    //             Resolve Next Issue & syarat toggle Engineer Confirm. false = tab tidak dipakai untuk review
    // ==========================================
    interface ModuleConfig {
      name: string;
      tabId: string;
      secId: string;
      defaultVisible: boolean;
      inSummary: boolean;
      getRows: (data: any) => any[];
    }

    const MODULES: ModuleConfig[] = [
      { name: 'Structure & Operation Plan Check', tabId: 'tab-nav-structure',            secId: 'sec-structure',            defaultVisible: true,  inSummary: true,  getRows: getStructureRows },
      { name: 'Tool Option Compare',         tabId: 'tab-nav-ben-compare',          secId: 'sec-ben-compare',          defaultVisible: true,  inSummary: true,  getRows: getAllCompareToolRows },
      // HW Option Compare = tabel Single + Multi dalam 1 tab (dipilih lewat switch di atas tabel)
      { name: 'HW Option Compare',           tabId: 'tab-nav-hw-option',            secId: 'sec-hw-option',            defaultVisible: true,  inSummary: true,  getRows: (data: any) => [...getHwSingleOptionRows(data), ...getAllHwMultiOptionRows(data)] },
      { name: 'Substitute Compare',          tabId: 'tab-nav-substitute-check',     secId: 'sec-substitute-check',     defaultVisible: true,  inSummary: true,  getRows: getAllSubstituteRows },
      { name: 'Assy Release Status Compare', tabId: 'tab-nav-assy-release-status',  secId: 'sec-assy-release-status',  defaultVisible: true,  inSummary: true,  getRows: getAssyReleaseStatusSummaryRows },
      // Tab di bawah ini jarang dipakai: disembunyikan (buka lewat "Show Tab") & tidak ikut review
      { name: 'Operation Plan Check',        tabId: 'tab-nav-operation-plan-check', secId: 'sec-operation-plan-check', defaultVisible: false, inSummary: false, getRows: getOperationPlanRows },
      { name: 'EAX Substitute Check',        tabId: 'tab-nav-eax-substitute-check', secId: 'sec-eax-substitute-check', defaultVisible: false, inSummary: false, getRows: getEaxSubstituteRows },
      { name: 'Check Part',                  tabId: 'tab-nav-check-part',           secId: 'sec-check-part',           defaultVisible: false, inSummary: false, getRows: getAllCheckPartRows },
      { name: 'Crosschecking Result',        tabId: 'tab-nav-crosschecking-result', secId: 'sec-crosschecking-result', defaultVisible: false, inSummary: false, getRows: getCrosscheckingResultRows },
    ];

    const summaryModules = MODULES.filter(m => m.inSummary);

    /** Section (tab) yang barisnya ikut dihitung untuk review (progress, Resolve Next Issue, toggle) */
    function isReviewSection(section: Element | null): boolean {
      if (!section) return false;
      return summaryModules.some(m => m.secId === section.id);
    }

    const moduleTabNavMap: Record<string, string> = Object.fromEntries(MODULES.map(m => [m.name, m.tabId]));

    function applyRemarkCellHighlighting(rootContainer?: HTMLElement | Document) {
      const scope = rootContainer || document;
      const tables = scope.querySelectorAll('.dynamic-table');

      tables.forEach((table) => {
        // Header tabel bisa 2-3 baris, jadi daftar kolom diambil dari atribut data-columns.
        // Tabel lama tanpa data-columns tetap memakai baris header terakhir.
        const columnsAttr = table.getAttribute('data-columns');
        let headers: string[];
        if (columnsAttr) {
          headers = columnsAttr.split('|').map(h => h.trim().toLowerCase());
        } else {
          const headerRow = table.querySelector('thead tr:last-child');
          if (!headerRow) return;
          headers = Array.from(headerRow.querySelectorAll('th')).map(th => th.textContent?.trim().toLowerCase() || '');
        }

        const remarkIndices: number[] = [];
        headers.forEach((h, idx) => {
          if (h.includes('reason') || h.includes('remark') || h.includes('note')) {
            remarkIndices.push(idx);
          }
        });

        let uitIdx = -1;
        let supplyIdx = -1;
        let qtyIdx = -1;

        // Kalau ada beberapa kolom UIT / Supply / Qty (mis. Reference, Target, Initial),
        // kolom milik Target (label diawali "target") yang di-highlight
        const pickIdx = (current: number, h: string, idx: number) =>
          (current === -1 || h.startsWith('target')) ? idx : current;

        headers.forEach((h, idx) => {
          if (h === 'part uit' || h.includes('uit')) {
            uitIdx = pickIdx(uitIdx, h, idx);
          } else if (h === 'part supply type' || h.includes('supply')) {
            supplyIdx = pickIdx(supplyIdx, h, idx);
          } else if (h === 'part quantity' || h.includes('quantity') || h.includes('qty')) {
            qtyIdx = pickIdx(qtyIdx, h, idx);
          }
        });

        const rows = table.querySelectorAll('tbody tr');
        rows.forEach((tr) => {
          const cells = tr.querySelectorAll('td');
          // Baris dengan hasil OK / SAME tidak perlu di-highlight walaupun ada reason
          const rowResult = (tr.getAttribute('data-result') || '').toUpperCase();
          const rowIsOk = rowResult === 'OK' || rowResult === 'SAME';

          let combinedRemarkText = '';
          remarkIndices.forEach((rIdx) => {
            const rCell = cells[rIdx];
            if (rCell) {
              const input = rCell.querySelector('.remark-input') as HTMLInputElement;
              const txt = (input ? input.value : rCell.textContent)?.trim().toLowerCase() || '';
              if (txt && txt !== '-') {
                combinedRemarkText += ' ' + txt;
              }

              rCell.classList.remove('cell-highlight-reason', 'cell-highlight-red-red');
              rCell.style.backgroundColor = '';
              rCell.style.border = '';
              if (input) {
                input.classList.remove('input-required');
                input.style.backgroundColor = '#ffffff';
                input.style.borderColor = '#e5e7eb';
                input.style.outline = 'none';
              }
            }
          });

          const highlightUIT = !rowIsOk && uitIdx !== -1 && (combinedRemarkText.includes('uit') || combinedRemarkText.includes('part uit'));
          const highlightSupply = !rowIsOk && supplyIdx !== -1 && (combinedRemarkText.includes('supply') || combinedRemarkText.includes('supply type'));
          const highlightQty = !rowIsOk && qtyIdx !== -1 && (combinedRemarkText.includes('quantity') || combinedRemarkText.includes('qty') || combinedRemarkText.includes('part quantity'));

          if (uitIdx !== -1 && cells[uitIdx]) {
            const cell = cells[uitIdx] as HTMLElement;
            if (highlightUIT) {
              cell.classList.add('cell-highlight-red-red');
              cell.style.setProperty('background-color', '#FEE2E2', 'important');
              cell.style.setProperty('color', '#DC2626', 'important');
              cell.style.setProperty('font-weight', '700', 'important');
            } else {
              cell.classList.remove('cell-highlight-red-red');
              cell.style.backgroundColor = '';
              cell.style.color = '';
              cell.style.fontWeight = '';
            }
          }

          if (supplyIdx !== -1 && cells[supplyIdx]) {
            const cell = cells[supplyIdx] as HTMLElement;
            if (highlightSupply) {
              cell.classList.add('cell-highlight-red-red');
              cell.style.setProperty('background-color', '#FEE2E2', 'important');
              cell.style.setProperty('color', '#DC2626', 'important');
              cell.style.setProperty('font-weight', '700', 'important');
            } else {
              cell.classList.remove('cell-highlight-red-red');
              cell.style.backgroundColor = '';
              cell.style.color = '';
              cell.style.fontWeight = '';
            }
          }

          if (qtyIdx !== -1 && cells[qtyIdx]) {
            const cell = cells[qtyIdx] as HTMLElement;
            if (highlightQty) {
              cell.classList.add('cell-highlight-red-red');
              cell.style.setProperty('background-color', '#FEE2E2', 'important');
              cell.style.setProperty('color', '#DC2626', 'important');
              cell.style.setProperty('font-weight', '700', 'important');
            } else {
              cell.classList.remove('cell-highlight-red-red');
              cell.style.backgroundColor = '';
              cell.style.color = '';
              cell.style.fontWeight = '';
            }
          }
        });
      });
    }

    function applyReasonHighlighting(rootContainer?: HTMLElement | Document) {
      applyRemarkCellHighlighting(rootContainer);
    }

    function applyRowHighlightStyles(rootContainer?: HTMLElement | Document) {
      const scope = rootContainer || document;
      const rows = scope.querySelectorAll('.dynamic-table tbody tr');

      rows.forEach((tr: Element) => {
        const row = tr as HTMLElement;
        const isStructureContainer = row.closest('#container-structure') !== null;
        const isToolOptionContainer = row.closest('#container-ben-compare-tool') !== null;
        // Tabel OK / NG / DIFFERENT: DIFFERENT kuning. Tabel SAME / DIFFERENT: DIFFERENT merah
        const isOkNgTable = row.closest('table')?.getAttribute('data-result-mode') === 'okng';

        const resultAttr = safeString(row.getAttribute('data-result')).toUpperCase();
        const selectElem = row.querySelector('.result-select') as HTMLSelectElement | null;
        const currentVal = selectElem ? selectElem.value.toUpperCase() : resultAttr;

        const remarkInputs = row.querySelectorAll('.remark-input');
        let hasReasonData = false;
        remarkInputs.forEach((inp) => {
          const val = (inp as HTMLInputElement).value.trim();
          if (val !== '' && val !== '-') hasReasonData = true;
        });

        row.classList.remove('highlight-row-ng', 'highlight-row-different', 'highlight-row-check', 'highlight-row-difference-reason');

        if (isToolOptionContainer) {
          if (currentVal === 'DIFFERENT' || currentVal === 'NG') {
            row.classList.add('highlight-row-different');
          }
        } else if (!isStructureContainer) {
          const isAmberRow = currentVal === 'CHECK' || (currentVal === 'DIFFERENT' && isOkNgTable);

          if (currentVal === 'NG') {
            row.classList.add('highlight-row-ng');
          } else if (isAmberRow) {
            row.classList.add('highlight-row-check');
          } else if (currentVal === 'DIFFERENT') {
            row.classList.add('highlight-row-different');
          }

          if (hasReasonData && !isAmberRow && currentVal !== 'SAME' && currentVal !== 'OK') {
            row.classList.add('highlight-row-difference-reason');
          }
        }
      });

      applyReasonHighlighting(rootContainer);
    }

    function updateTabHighlighting() {
      const resultBadges = document.querySelectorAll('.crosscheck-list .result-badge-btn');
      resultBadges.forEach(badge => {
        const moduleName = badge.getAttribute('data-module');
        const status = badge.textContent?.trim().toUpperCase();
        if (!moduleName) return;
        const tabId = moduleTabNavMap[moduleName];
        if (!tabId) return;
        const tabElem = id(tabId);
        if (!tabElem) return;
        tabElem.classList.remove('tab-highlight-ng', 'tab-highlight-check');
        if (status === 'NG' || status === 'DIFFERENT') tabElem.classList.add('tab-highlight-ng');
        else if (status === 'CHECK') tabElem.classList.add('tab-highlight-check');
      });
    }

    /**
     * Apa yang masih kurang dari satu baris agar dianggap "sudah direview".
     * Baris OK / SAME selalu dianggap selesai. Baris NG / DIFFERENT wajib:
     *   - Engineer Check dipilih OK atau NG (kalau tabelnya punya kolom Engineer Check)
     *   - Remarks diisi teks yang valid
     */
    function getRowReviewIssues(tr: Element): string[] {
      const status = safeString(tr.getAttribute('data-result')).trim().toUpperCase();
      if (status !== 'NG' && status !== 'DIFFERENT' && status !== 'CHECK') return [];

      const issues: string[] = [];
      // Engineer Check berupa badge read-only (otomatis dari PRM check) tidak perlu diisi user
      const engSelect = tr.querySelector('.engineer-confirm-select') as HTMLSelectElement | null;
      if (engSelect && engSelect.value !== 'OK' && engSelect.value !== 'NG') issues.push('Engineer Check');

      const remarkInput = tr.querySelector('.remark-input') as HTMLInputElement | null;
      if (!remarkInput || !isValidRemark(remarkInput.value)) issues.push('Remarks');
      return issues;
    }

    /**
     * Tinggi area scroll tabel freeze (.freeze-wrapper) dibuat pas dengan sisa tinggi layar,
     * supaya halaman sendiri tidak punya scrollbar vertikal (cukup scrollbar di dalam tabel).
     * Tinggi minimal FREEZE_TABLE_MIN_HEIGHT; kalau layar terlalu pendek, halaman boleh scroll.
     */
    const FREEZE_TABLE_MIN_HEIGHT = 320;
    const FREEZE_TABLE_BOTTOM_GAP = 16;

    function fitFreezeTablesToViewport() {
      const wrappers = (Array.from(document.querySelectorAll('.section-block.active-tab-panel .table-wrapper.freeze-wrapper')) as HTMLElement[])
        .filter(w => w.offsetParent !== null);   // hanya yang sedang tampil
      if (wrappers.length === 0) return;

      wrappers.forEach(w => {
        const top = w.getBoundingClientRect().top + window.scrollY;
        const height = window.innerHeight - top - FREEZE_TABLE_BOTTOM_GAP;
        w.style.maxHeight = `${Math.max(FREEZE_TABLE_MIN_HEIGHT, height)}px`;
      });

      // Koreksi: kalau halaman masih bisa di-scroll (margin/padding di bawah tabel), kurangi tinggi tabel
      const overflow = document.documentElement.scrollHeight - window.innerHeight;
      if (overflow > 0) {
        wrappers.forEach(w => {
          const current = parseFloat(w.style.maxHeight) || w.clientHeight;
          w.style.maxHeight = `${Math.max(FREEZE_TABLE_MIN_HEIGHT, current - overflow)}px`;
        });
      }
    }

    // Dipanggil setelah tab / sub-tab / sidebar berubah (tunggu layout selesai dulu)
    function scheduleFitFreezeTables() {
      window.requestAnimationFrame(() => fitFreezeTablesToViewport());
    }
    (window as any).fitFreezeTablesToViewport = scheduleFitFreezeTables;

    function updateProgressMetrics() {
      let totalRows = 0;
      let reviewedRows = 0;

      const allTableCards = document.querySelectorAll('.table-card');
      allTableCards.forEach(card => {
        if (!isReviewSection(card.closest('.section-block'))) return;
        const rows = card.querySelectorAll('tbody tr');
        rows.forEach((tr: any) => {
          totalRows++;
          if (getRowReviewIssues(tr).length === 0) reviewedRows++;
        });
      });

      const pct = totalRows > 0 ? Math.round((reviewedRows / totalRows) * 100) : 0;
      setText('progressText', `(${reviewedRows}/${totalRows} reviewed)`);
      setText('progressPct', `${pct}%`);

      const bar = id('progressBarFill');
      if (bar) bar.style.width = `${pct}%`;
    }

    function applyInitialTabVisibility() {
      // Tab default (lihat MODULES) tampil, sisanya disembunyikan -> bisa dibuka lewat "Show Tab"
      MODULES.forEach(mod => {
        const tabElem = id(mod.tabId);
        if (tabElem) tabElem.style.display = mod.defaultVisible ? 'inline-flex' : 'none';
      });

      const firstModule = MODULES.find(m => m.defaultVisible) ?? MODULES[0];
      (window as any).navigateToSection(firstModule.secId);
      updateShowTabDropdownMenu();
    }

    function updateShowTabDropdownMenu() {
      const dropdownContent = id('showTabDropdownList');
      if (!dropdownContent) return;

      const allTabs = document.querySelectorAll('.chrome-tabs-bar .tab-item');
      let hiddenTabsHtml = '';
      let hiddenCount = 0;

      allTabs.forEach(tab => {
        if ((tab as HTMLElement).style.display === 'none') {
          hiddenCount++;
          const tabId = tab.id;
          const secId = tab.getAttribute('href')?.replace('#', '') || '';
          const title = tab.querySelector('.tab-title')?.textContent || tabId;

          hiddenTabsHtml += `
            <button onclick="window.restoreHiddenTab('${tabId}', '${secId}')">
              <i class="fa-solid fa-plus-circle" style="color:var(--royal-blue);"></i> ${escapeHtml(title)}
            </button>
          `;
        }
      });

      if (hiddenCount === 0) {
        dropdownContent.innerHTML = '<div style="padding: 8px 12px; font-size: 11px; color: var(--text-muted);">All tabs are currently visible</div>';
      } else {
        dropdownContent.innerHTML = hiddenTabsHtml;
      }

      setText('hiddenTabsBadgeCount', hiddenCount > 0 ? String(hiddenCount) : '');
    }

    function autoManageRightSidebarState(data: any) {
      const rightSidebar = id('workspaceRightSidebar');
      const showBtn = id('showModelProfileBtn');
      if (!rightSidebar || !showBtn) return;

      let hasNGorCheck = false;
      const modules = summaryModules.map(m => m.getRows(data));

      modules.forEach(modRows => {
        if (Array.isArray(modRows)) {
          modRows.forEach(r => {
            const st = safeString(r?.status || r?.Status || r?.result || r?.Result).toUpperCase();
            if (st === 'NG' || st === 'DIFFERENT' || st === 'CHECK') hasNGorCheck = true;
          });
        }
      });

      if (hasNGorCheck) {
        rightSidebar.classList.remove('sidebar-hidden');
        showBtn.classList.remove('show');
        showBtn.classList.add('has-warning');
      } else {
        rightSidebar.classList.add('sidebar-hidden');
        showBtn.classList.add('show');
        showBtn.classList.remove('has-warning');
      }
    }

    /**
     * Nama model di header tabel mengikuti Crosscheck Configuration (drawer My BOM).
     * Kalau konfigurasi kosong, tetap memakai nama dari hasil crosscheck (backend).
     */
    function applyBomConfig(data: any) {
      if (!bomConfig || !data || typeof data !== 'object' || Array.isArray(data)) return data;
      return {
        ...data,
        devName: bomConfig.devModel || data.devName,
        initName: bomConfig.initialModel || data.initName,
        initRegionName: bomConfig.initialRegion || data.initRegionName,
        jiraPowerConsLink: bomConfig.jiraPowerConsLink || data.jiraPowerConsLink,
      };
    }

    function processMasterJson(rawData: any) {
      if (!rawData) return;
      const data = applyBomConfig(rawData);
      currentMasterJson = data;
      syncHeaderData(data);
      syncModelProfile(data);
      syncHWProfile(data);
      syncSectionInfoContainers(data);
      renderAllJsonTables(data);
      syncCrosscheckBadges(data);
      updateTabCounters(data);
      updateTabHighlighting();
      updateCompareNoteSidebar(data);
      syncActionCenterAndNavigator(data);
      autoManageRightSidebarState(data);
      applyRowHighlightStyles();
      applyInitialTabVisibility();
      updateProgressMetrics();
      scheduleFitFreezeTables();
      applyViewOnlyMode();
    }

    function getModuleStats(rows: any[]) {
      let ng = 0;
      let check = 0;
      let ok = 0;
      if (Array.isArray(rows)) {
        rows.forEach(r => {
          if (!r || typeof r !== 'object') return;
          const status = safeString(r.status || r.Status || r.result || r.Result).trim().toUpperCase();
          if (status === 'NG') ng++;
          else if (status === 'CHECK' || status === 'REVIEW' || status === 'DIFFERENT') check++;
          else ok++;
        });
      }
      return { total: Array.isArray(rows) ? rows.length : 0, ng, check, ok };
    }

    function syncActionCenterAndNavigator(data: any) {
      const modules = summaryModules.map(m => ({ key: m.name, secId: m.secId, rows: m.getRows(data) }));

      let totalNG = 0;
      let totalCheck = 0;
      let totalOK = 0;
      const attentionList: { name: string; secId: string; ng: number; check: number; statusText: string }[] = [];

      modules.forEach(mod => {
        const stats = getModuleStats(mod.rows);
        totalNG += stats.ng;
        totalCheck += stats.check;
        totalOK += stats.ok;

        const overallModuleStatus = stats.ng > 0 ? 'NG' : stats.check > 0 ? 'CHECK' : 'OK';

        if (stats.ng > 0 || stats.check > 0) {
          attentionList.push({
            name: mod.key,
            secId: mod.secId,
            ng: stats.ng,
            check: stats.check,
            statusText: overallModuleStatus
          });
        }
      });

      setText('ac-total-ng', String(totalNG));
      setText('ac-total-check', String(totalCheck));
      setText('ac-total-ok', String(totalOK));

      const attentionContainer = id('action-center-attention-list');
      if (attentionContainer) {
        if (attentionList.length === 0) {
          attentionContainer.innerHTML = '<div class="no-issues-card"><i class="fa-solid fa-circle-check"></i> All crosscheck modules passed without any NG or Review issues.</div>';
        } else {
          attentionContainer.innerHTML = attentionList.map(item => {
            let statusBadgeClass = 'status-badge-ok';
            let statusLabel = 'OK';

            if (item.statusText === 'NG') {
              statusBadgeClass = 'status-badge-ng';
              statusLabel = 'NG';
            } else if (item.statusText === 'CHECK') {
              statusBadgeClass = 'status-badge-check';
              statusLabel = 'DIFFERENT';
            }

            return `
              <div class="attention-row">
                <div class="attention-info">
                  <span class="status-dot ${item.ng > 0 ? 'dot-ng' : item.check > 0 ? 'dot-check' : 'dot-ok'}"></span>
                  <span class="attention-name">${escapeHtml(item.name)}</span>
                  <span class="crosscheck-result-pill ${statusBadgeClass}">${statusLabel}</span>
                  <span class="attention-status">
                    ${item.ng > 0 ? `<strong class="text-ng">(${item.ng} NG)</strong>` : ''}
                    ${item.check > 0 ? `<strong class="text-check">(${item.check} Different)</strong>` : ''}
                  </span>
                </div>
                <button class="review-jump-btn" onclick="window.jumpToProblemRow('${item.secId}')">
                  Review <i class="fa-solid fa-arrow-right"></i>
                </button>
              </div>
            `;
          }).join('');
        }
      }
    }

    function syncHWProfile(data: any) {
      if (!data) return;

      const eaxInfo = getPath(data, 'eaxSubstitute.info') || {};
      setText('hwEaxPartNo', safeString(eaxInfo.eaxPartNumber ?? '-'));
      setText('hwEbrPartNo', safeString(eaxInfo.ebrPartNumber ?? '-'));
      setText('hwEbrMainPartNo', safeString(eaxInfo.ebrMainPartNumber ?? '-'));
      setText('hwEbtPartNo', safeString(eaxInfo.ebtPartNumber ?? '-'));
      setText('hwEaxChassis', safeString(eaxInfo.chassisName ?? getPath(data, 'ModelProfile.profileData.0.Chassis') ?? '-'));
      setText('hwEaxPcbRev', safeString(eaxInfo.pcbRev ?? '-'));
      setText('hwEaxStatus', safeString(eaxInfo.status ?? 'OK'));

      setText('chkHwEaxPartNo', safeString(eaxInfo.eaxPartNumber ?? '-'));
      setText('chkHwEbrPartNo', safeString(eaxInfo.ebrPartNumber ?? '-'));
      setText('chkHwEbrMainPartNo', safeString(eaxInfo.ebrMainPartNumber ?? '-'));
      setText('chkHwEbtPartNo', safeString(eaxInfo.ebtPartNumber ?? '-'));
      setText('chkHwEaxChassis', safeString(eaxInfo.chassisName ?? getPath(data, 'ModelProfile.profileData.0.Chassis') ?? '-'));
      setText('chkHwEaxPcbRev', safeString(eaxInfo.pcbRev ?? '-'));
      setText('chkHwEaxStatus', safeString(eaxInfo.status ?? 'OK'));

      const eaxRows = normalizeTableRows(getPath(data, 'eaxSubstitute.compareData'));
      renderGenericTable('container-hw-eax-profile', eaxRows, 'EAX Profile Raw Data', false);
      renderGenericTable('container-chk-hw-eax-profile', eaxRows, 'EAX Profile Raw Data', false);

      const opInfo = getPath(data, 'OperationPlan.info') || {};
      setText('hwEbtPartNoDetail', safeString(eaxInfo.ebtPartNumber ?? '-'));
      setText('hwEbtBoardType', safeString(getPath(data, 'ModelProfile.profileData.0.Board') ?? '-'));
      setText('hwEbtOpPlan', safeString(opInfo.databaseName ?? '-'));
      setText('hwEbtDbVer', safeString(opInfo.databaseVersion ?? '-'));
      setText('hwEbtReleaseDate', safeString(opInfo.databaseDate ?? '-'));

      setText('chkHwEbtPartNoDetail', safeString(eaxInfo.ebtPartNumber ?? '-'));
      setText('chkHwEbtBoardType', safeString(getPath(data, 'ModelProfile.profileData.0.Board') ?? '-'));
      setText('chkHwEbtOpPlan', safeString(opInfo.databaseName ?? '-'));
      setText('chkHwEbtDbVer', safeString(opInfo.databaseVersion ?? '-'));
      setText('chkHwEbtReleaseDate', safeString(opInfo.databaseDate ?? '-'));

      const ebtRows = getOperationPlanRows(data);
      renderGenericTable('container-hw-ebt-profile', ebtRows, 'EBT Profile Raw Data', false);
      renderGenericTable('container-chk-hw-ebt-profile', ebtRows, 'EBT Profile Raw Data', false);

      const runInfo = getPath(data, 'structureCompare.result.run_info') || getPath(data, 'structureCompare.info') || {};
      setText('hwStructPlantName', safeString(runInfo.subsName ?? data.subsName ?? '-'));
      setText('hwStructSuffixName', safeString(runInfo.suffixName ?? data.suffixName ?? '-'));
      setText('hwStructPlantSuffix', safeString(runInfo.subsSuffix ?? data.subsSuffix ?? '-'));
      setText('hwStructPlantCode', safeString(runInfo.templateHeader ?? data.templateHeader ?? '-'));
      setText('hwStructEditor', safeString(runInfo.editor ?? data.editor ?? '-'));
      setText('hwStructCreator', safeString(runInfo.creator ?? data.creator ?? '-'));
      setText('hwStructEditedDate', safeString(runInfo.run_date ?? data.run_date ?? '-'));

      setText('chkHwStructPlantName', safeString(runInfo.subsName ?? data.subsName ?? '-'));
      setText('chkHwStructSuffixName', safeString(runInfo.suffixName ?? data.suffixName ?? '-'));
      setText('chkHwStructPlantSuffix', safeString(runInfo.subsSuffix ?? data.subsSuffix ?? '-'));
      setText('chkHwStructPlantCode', safeString(runInfo.templateHeader ?? data.templateHeader ?? '-'));
      setText('chkHwStructEditor', safeString(runInfo.editor ?? data.editor ?? '-'));
      setText('chkHwStructCreator', safeString(runInfo.creator ?? data.creator ?? '-'));
      setText('chkHwStructEditedDate', safeString(runInfo.run_date ?? data.run_date ?? '-'));

      const structRows = normalizeTableRows(getFirstAvailablePath(data, ['structureCompare.result.compareData', 'result.compareData']));
      renderGenericTable('container-hw-struct-profile', structRows, 'Structure Profile Details', false, false, structureExcludedKeys);
      renderGenericTable('container-chk-hw-struct-profile', structRows, 'Structure Profile Details', false, false, structureExcludedKeys);
    }

    function syncSectionInfoContainers(data: any) {
      if (!data) return;

      const runInfo = getPath(data, 'structureCompare.result.run_info') || getPath(data, 'structureCompare.info') || {};
      setText('info-struct-plant-name', safeString(runInfo.subsName ?? data.subsName ?? '-'));
      setText('info-struct-suffix-name', safeString(runInfo.suffixName ?? data.suffixName ?? '-'));
      setText('info-struct-plant-suffix', safeString(runInfo.subsSuffix ?? data.subsSuffix ?? '-'));
      setText('info-struct-editor', safeString(runInfo.editor ?? data.editor ?? '-'));
      setText('info-struct-creator', safeString(runInfo.creator ?? data.creator ?? '-'));
      setText('info-struct-edited-date', safeString(runInfo.run_date ?? data.run_date ?? '-'));
      setText('info-struct-plant-code', safeString(runInfo.templateHeader ?? data.templateHeader ?? '-'));

      setText('info-ben-model-name', safeString(data.targetName ?? '-'));
      setText('info-ben-dev-model', safeString(data.devName ?? '-'));
      setText('info-ben-init-model', safeString(data.initName ?? '-'));

      const eaxInfo = getPath(data, 'eaxSubstitute.info') || {};
      setText('info-eax-part-no', safeString(eaxInfo.eaxPartNumber ?? '-'));
      setText('info-ebr-part-no', safeString(eaxInfo.ebrPartNumber ?? '-'));
      setText('info-ebr-main-part-no', safeString(eaxInfo.ebrMainPartNumber ?? '-'));
      setText('info-ebt-part-no', safeString(eaxInfo.ebtPartNumber ?? '-'));
      setText('info-chassis-name', safeString(eaxInfo.chassisName ?? getPath(data, 'ModelProfile.profileData.0.Chassis') ?? '-'));

      const opInfo = getPath(data, 'OperationPlan.info') || {};
      setText('info-op-db-name', safeString(opInfo.databaseName ?? '-'));
      setText('info-op-db-version', safeString(opInfo.databaseVersion ?? '-'));
      setText('info-op-db-date', safeString(opInfo.databaseDate ?? '-'));
      setText('info-op-db-year', safeString(opInfo.databaseYear ?? '-'));

      setText('info-check-part-model-name', safeString(data.targetName ?? '-'));
      setText('info-check-part-dev-model', safeString(data.devName ?? '-'));
      setText('info-check-part-init-model', safeString(data.initName ?? '-'));
    }

    function syncHeaderData(data: any) {
      const model = safeString(data.targetName || '85QNED74BSA');
      const revision = data.version !== undefined && data.version !== null ? `Rev ${safeString(data.version)}` : 'Rev 1.0';

      setText('headerModelName', model);
      setText('revisionValue', revision);
      setText('ac-model-title', model);
      setText('ac-revision', revision);
    }

    function syncModelProfile(data: any) {
      const profileRows = getPath(data, 'ModelProfile.profileData') || getPath(data, 'modelProfile.profileData');
      const prof = Array.isArray(profileRows) && profileRows.length ? profileRows[0] : {};

      setText('profRegion', safeString(prof.Region));
      setText('profMarket', safeString(prof.Market));
      setText('profPlant', safeString(prof.Plant));
      setText('profChassis', safeString(prof.Chassis));
      setText('profInch', prof.Inch !== undefined && prof.Inch !== null && prof.Inch !== '' ? `${prof.Inch}"` : '-');
      setText('profSeries', safeString(prof.Series));
      setText('profSoC', safeString(prof.SoC));
      setText('profBoard', safeString(prof.Board));
      setText('profPanel', safeString(prof.Panel));
      setText('profCircuitPIC', safeString(prof.CircuitPIC));
    }

    function renderAllJsonTables(data: any) {
      renderStructureTable('container-structure', data);
      renderToolOptionTable('container-ben-compare-tool', data);
      renderHwSingleOptionTable('container-single-hw-option', data);
      renderHwMultiOptionSection(data);
      renderSubstituteSection(data);
      renderAssyReleaseStatusTable('container-assy-release-status', data);
      renderEaxSubstituteTable('container-eax-substitute-check', data);
      renderOperationPlanTable('container-operation-plan-check', data);
      renderCheckPartSection(data);
      renderCrosscheckingResultTable('container-crosschecking-result', data);
      renderCrosscheckingResultTable('container-sidebar-crosschecking-result', data);
    }

    function getStatusFromRows(rows: any[]) {
      if (!Array.isArray(rows) || rows.length === 0) return 'OK';
      const values = rows.map(row => {
        if (!row || typeof row !== 'object') return '';
        return safeString(row.status || row.Status || row.result || row.Result).trim().toUpperCase();
      });
      if (values.includes('NG') || values.includes('DIFFERENT') || values.includes('FAIL')) return 'NG';
      if (values.includes('CHECK')) return 'CHECK';
      return 'OK';
    }

    function getNoteFromRows(rows: any[]) {
      if (!Array.isArray(rows)) return '';
      const priority = ['NG', 'DIFFERENT', 'CHECK'];
      for (const wanted of priority) {
        const row = rows.find(r => {
          if (!r || typeof r !== 'object') return false;
          return safeString(r.status || r.Status || r.result || r.Result).trim().toUpperCase() === wanted;
        });
        if (row) {
          return safeString(row['compare note'] ?? row.compare_note ?? row.reason ?? row.Reason ?? row.remarks ?? row.Remarks ?? row.remark ?? row.Remark ?? '');
        }
      }
      return '';
    }

    function syncCrosscheckBadges(data: any) {
      const badgeContainer = id('crosscheckBadgeList');
      if (!badgeContainer) return;

      const modules = summaryModules.map(m => ({ name: m.name, rows: m.getRows(data) }));

      badgeContainer.innerHTML = modules.map(mod => {
        const status = getStatusFromRows(mod.rows);
        const note = getNoteFromRows(mod.rows) || `${mod.name} result.`;
        let badgeClass = 'btn-badge-ok';
        if (status === 'CHECK') badgeClass = 'btn-badge-check';
        if (status === 'NG') badgeClass = 'btn-badge-ng';

        return `
          <div class="crosscheck-item">
            <span class="crosscheck-name">${escapeHtml(mod.name)}</span>
            <button class="result-badge-btn ${badgeClass}" data-module="${escapeHtml(mod.name)}" data-note="${escapeHtml(note)}">${status}</button>
          </div>
        `;
      }).join('');
    }

    function renderGenericTable(
      containerId: string,
      rows: any,
      explicitTitle = 'Details',
      objectAsKeyValue = false,
      isHwMultiOption = false,
      excludedKeysSet?: Set<string>
    ) {
      const container = id(containerId);
      if (!container) return;

      const normalizedRows = normalizeTableRows(rows);
      if (!Array.isArray(normalizedRows) || normalizedRows.length === 0) {
        container.innerHTML = '<div class="empty-state">No entries available.</div>';
        return;
      }

      let keys = collectKeys(normalizedRows, excludedKeysSet);
      keys = keys.filter(k => {
        const lk = k.toLowerCase().replace(/[_-]/g, '').trim();
        return lk !== 'engineerconfirm' && lk !== 'engineer_confirm' && lk !== 'engineer confirm' &&
               lk !== 'remarks' && lk !== 'remark' && lk !== 'comparenote' && lk !== 'compare_note' &&
               lk !== 'status' && lk !== 'result';
      });

      let html = `
        <div class="table-card">
          <div class="table-toolbar">
            <div class="table-status-counters">
              <button class="table-status-counter counter-ng" onclick="window.filterTableRows(this, 'NG')"><i class="fa-solid fa-circle-xmark"></i> Show NG <strong class="counter-ng-value">0</strong></button>
              <button class="table-status-counter counter-check" onclick="window.filterTableRows(this, 'CHECK')"><i class="fa-solid fa-circle-question"></i> Show Check <strong class="counter-check-value">0</strong></button>
              <button class="table-status-counter counter-uncheck" onclick="window.filterTableRows(this, 'UNCHECK')"><i class="fa-solid fa-square-minus"></i> Show Uncheck</button>
              <button class="table-status-counter counter-ok" onclick="window.filterTableRows(this, 'OK')"><i class="fa-solid fa-circle-check"></i> OK</button>
              <button class="table-status-counter counter-all active-filter" onclick="window.filterTableRows(this, 'ALL')">Show All</button>
            </div>
          </div>
          <div class="table-wrapper">
            <table class="dynamic-table">
              <thead>
                <tr>
      `;

      keys.forEach(k => {
        html += `<th>${escapeHtml(camelToTitle(k))}</th>`;
      });
      html += `
                  <th class="status-column">Status</th>
                  <th class="engineer-confirm-column">Engineer Check</th>
                  <th>Remarks</th>
                </tr>
              </thead>
              <tbody>
      `;

      normalizedRows.forEach((row, rowIndex) => {
        const rawStatus = safeString(row?.status ?? row?.Status ?? row?.result ?? row?.Result ?? 'OK').trim().toUpperCase();
        const rowStatus = (rawStatus === 'NG' || rawStatus === 'DIFFERENT') ? 'NG' : (rawStatus === 'CHECK' || rawStatus === 'REVIEW') ? 'CHECK' : 'OK';
        const rowStatusClass = rowStatus === 'NG' ? 'status-ng' : rowStatus === 'CHECK' ? 'status-check' : '';
        const remarkVal = safeString(row?.remarks ?? row?.Remarks ?? row?.remark ?? row?.Remark ?? row?.reason ?? row?.Reason ?? '');

        html += `<tr class="${rowStatusClass}" data-result="${escapeHtml(rowStatus)}" data-row-index="${rowIndex}">`;

        keys.forEach(k => {
          const val = row ? row[k] : undefined;
          const text = safeString(val === undefined || val === null || val === '' ? '-' : val);
          const displayText = truncateTextToThreeWords(text);
          html += `<td><span class="static-cell-text" title="${escapeHtml(text)}">${escapeHtml(displayText)}</span></td>`;
        });

        // Status Column
        const statusColorClass = rowStatus === 'OK' ? 'res-ok' : rowStatus === 'CHECK' ? 'res-check' : 'res-ng';
        html += `
          <td class="status-column">
            <select class="result-select ${statusColorClass}" onfocus="window.storePreviousResult(this)" onchange="window.updateResultStyle(this, false)">
              <option value="OK" ${rowStatus === 'OK' ? 'selected' : ''}>OK</option>
              <option value="CHECK" ${rowStatus === 'CHECK' ? 'selected' : ''}>REVIEW</option>
              <option value="NG" ${rowStatus === 'NG' ? 'selected' : ''}>NG</option>
            </select>
          </td>
        `;

        // Engineer Check Column
        html += `
          <td class="engineer-confirm-column">
            <select class="engineer-confirm-select eng-uncheck" onchange="window.updateEngineerConfirmStyle(this)">
              <option value="Uncheck" selected>Uncheck</option>
              <option value="OK">OK</option>
              <option value="NG">NG</option>
            </select>
          </td>
        `;

        // Remarks Column
        html += `
          <td>
            <input type="text" class="remark-input" value="${escapeHtml(remarkVal === '-' ? '' : remarkVal)}" placeholder="Enter detail..." oninput="this.setAttribute('value', this.value); this.classList.remove('input-required'); window.updateTableStatusCounters(this.closest('.table-card')); window.updateProgressMetrics(); applyRemarkCellHighlighting(this.closest('.table-card')); applyRowHighlightStyles(this.closest('.section-block') || document);">
          </td>
        `;

        html += `</tr>`;
      });

      html += '</tbody></table></div></div>';
      container.innerHTML = html;
      (window as any).updateTableStatusCounters(container);
      initializeTableColumnBehavior(container);
      applyRowHighlightStyles(container);
    }

    function initializeTableColumnBehavior(containerOrTable: any) {
      const root = containerOrTable?.querySelectorAll ? containerOrTable : document;

      root.querySelectorAll('.dynamic-table').forEach((table: any) => {
        const headers = Array.from(table.querySelectorAll('thead th'));
        headers.forEach((th: any) => {
          if (th.querySelector('.column-resizer')) return;

          const resizer = document.createElement('span');
          resizer.className = 'column-resizer';
          th.appendChild(resizer);

          resizer.addEventListener('mousedown', (event) => {
            event.preventDefault();
            event.stopPropagation();

            const startX = event.clientX;
            const startWidth = th.getBoundingClientRect().width;
            const minWidth = Math.max(55, th.scrollWidth > 0 ? Math.min(th.scrollWidth + 10, 120) : 55);

            resizer.classList.add('resizing');
            document.body.classList.add('column-resizing');

            const onMove = (moveEvent: MouseEvent) => {
              const nextWidth = Math.max(minWidth, startWidth + (moveEvent.clientX - startX));
              th.style.width = `${nextWidth}px`;
              th.style.minWidth = `${nextWidth}px`;
            };

            const onUp = () => {
              resizer.classList.remove('resizing');
              document.body.classList.remove('column-resizing');
              document.removeEventListener('mousemove', onMove);
              document.removeEventListener('mouseup', onUp);
            };

            document.addEventListener('mousemove', onMove);
            document.addEventListener('mouseup', onUp, { once: true });
          });
        });
      });
    }



    function updateTabCounters(data: any) {
      MODULES.forEach(mod => {
        const titleElem = document.querySelector(`#${mod.tabId} .tab-title`);
        if (titleElem) titleElem.textContent = `${mod.name} (${mod.getRows(data).length})`;
      });
    }

    function isValidRemark(remark: string) {
      if (!remark) return false;
      const trimmed = remark.trim();
      if (trimmed.length === 0) return false;
      const onlySymbolsRegex = /^[\p{P}\p{S}\s]+$/u;
      if (onlySymbolsRegex.test(trimmed)) return false;
      const hasTextRegex = /[a-zA-Z0-9]/;
      return hasTextRegex.test(trimmed);
    }

    function updateCompareNoteSidebar(data: any) {
      const container = id('compareNoteSidebarContent');
      if (!container) return;

      if (!data) {
        container.innerHTML = '<div class="notes-placeholder">No compare data loaded yet.</div>';
        return;
      }

      const modules = summaryModules.map(m => ({ name: m.name, rows: m.getRows(data) }));

      let html = '';
      modules.forEach(mod => {
        const rows = mod.rows;
        const status = getStatusFromRows(rows);
        const note = getNoteFromRows(rows) || 'No compare notes recorded.';
        let badgeClass = 'btn-badge-ok';
        if (status === 'CHECK') badgeClass = 'btn-badge-check';
        if (status === 'NG') badgeClass = 'btn-badge-ng';

        html += `
          <div class="note-module-card">
            <div class="note-module-header">
              <span class="note-module-title"><i class="fa-solid fa-table"></i> ${escapeHtml(mod.name)}</span>
              <span class="result-badge-btn ${badgeClass}">${escapeHtml(status)}</span>
            </div>
            <div class="note-module-body">${escapeHtml(note)}</div>
          </div>
        `;
      });

      container.innerHTML = html;
    }

    function showNotification(message: string, type: 'success' | 'info' | 'warning' = 'info') {
      let toastContainer = id('toastNotificationContainer');
      if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastNotificationContainer';
        toastContainer.className = 'toast-notification-container';
        document.body.appendChild(toastContainer);
      }

      const toast = document.createElement('div');
      toast.className = `toast-item toast-${type}`;
      toast.innerHTML = `
        <div class="toast-content">
          <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : type === 'warning' ? 'fa-triangle-exclamation' : 'fa-circle-info'}"></i>
          <span>${escapeHtml(message)}</span>
        </div>
      `;

      toastContainer.appendChild(toast);
      setTimeout(() => toast.classList.add('show'), 10);
      setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
      }, 4000);
    }

    (window as any).updateProgressMetrics = updateProgressMetrics;

    (window as any).hideRightSidebar = function() {
      scheduleFitFreezeTables();
      const rightSidebar = id('workspaceRightSidebar');
      const showBtn = id('showModelProfileBtn');
      if (rightSidebar) rightSidebar.classList.add('sidebar-hidden');
      if (showBtn) showBtn.classList.add('show');
    };

    (window as any).showRightSidebar = function() {
      scheduleFitFreezeTables();
      const rightSidebar = id('workspaceRightSidebar');
      const showBtn = id('showModelProfileBtn');
      if (rightSidebar) rightSidebar.classList.remove('sidebar-hidden');
      if (showBtn) showBtn.classList.add('show');
    };

    (window as any).toggleRightSidebar = function() {
      const rightSidebar = id('workspaceRightSidebar');
      if (!rightSidebar) return;
      const isHidden = rightSidebar.classList.contains('sidebar-hidden');
      if (isHidden) {
        (window as any).showRightSidebar();
      } else {
        (window as any).hideRightSidebar();
      }
    };

    (window as any).closeTab = function(e: MouseEvent, tabId: string) {
      e.preventDefault();
      e.stopPropagation();

      const tabElem = id(tabId);
      if (!tabElem) return;

      const wasActive = tabElem.classList.contains('active');
      tabElem.style.display = 'none';

      if (wasActive) {
        const remainingTabs = Array.from(document.querySelectorAll('.chrome-tabs-bar .tab-item'))
          .filter((t: any) => t.style.display !== 'none');

        if (remainingTabs.length > 0) {
          const nextTab = remainingTabs[0] as HTMLElement;
          const targetSec = nextTab.getAttribute('href')?.replace('#', '');
          if (targetSec) (window as any).navigateToSection(targetSec);
        }
      }

      updateShowTabDropdownMenu();
    };

    (window as any).restoreHiddenTab = function(tabId: string, sectionId: string) {
      const tabElem = id(tabId);
      if (tabElem) {
        tabElem.style.display = 'inline-flex';
        (window as any).navigateToSection(sectionId);
        updateShowTabDropdownMenu();
      }
    };

    (window as any).toggleInlineModelProfile = function() {
      const inlineProfileCard = id('inlineModelProfileCard');
      const btnIcon = id('toggleInlineProfileIcon');
      const btnText = id('toggleInlineProfileText');

      if (!inlineProfileCard) return;
      const isHidden = inlineProfileCard.style.display === 'none' || !inlineProfileCard.style.display;

      if (isHidden) {
        inlineProfileCard.style.display = 'block';
        if (btnIcon) btnIcon.className = 'fa-solid fa-chevron-up';
        if (btnText) btnText.textContent = 'Hide Model Profile';
      } else {
        inlineProfileCard.style.display = 'none';
        if (btnIcon) btnIcon.className = 'fa-solid fa-chevron-down';
        if (btnText) btnText.textContent = 'Show Model Profile';
      }
    };

    (window as any).navigateToSection = function(sectionId: string) {
      document.querySelectorAll('.section-block').forEach((sec: any) => {
        sec.style.display = 'none';
        sec.classList.remove('active-tab-panel');
      });

      const activeSec = id(sectionId);
      if (activeSec) {
        activeSec.style.display = 'flex';
        activeSec.classList.add('active-tab-panel');
      }

      scheduleFitFreezeTables();

      document.querySelectorAll('.tab-item').forEach(el => el.classList.remove('active'));
      const targetTab = document.querySelector(`.tab-item[href="#${sectionId}"]`);
      if (targetTab) {
        targetTab.classList.add('active');
        (targetTab as HTMLElement).style.display = 'inline-flex';
      }
      updateShowTabDropdownMenu();
    };

    (window as any).jumpToProblemRow = function(sectionId: string) {
      (window as any).navigateToSection(sectionId);
      setTimeout(() => {
        const sec = id(sectionId);
        if (!sec) return;
        const targetRow = sec.querySelector('tr.highlight-row-ng, tr.highlight-row-different, tr.highlight-row-check, tr.status-ng, tr.status-check, tr.highlight-row-difference-reason');
        if (targetRow) {
          targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
          targetRow.classList.add('row-focused-pulse');
          setTimeout(() => targetRow.classList.remove('row-focused-pulse'), 2500);
        }
      }, 100);
    };

    (window as any).resolveNextIssue = function() {
      if (isViewOnly) return;
      // Cari baris NG / DIFFERENT pertama yang belum lengkap (Engineer Check / Remarks)
      const allRows = (Array.from(document.querySelectorAll('.section-block .dynamic-table tbody tr')) as HTMLElement[])
        .filter(tr => isReviewSection(tr.closest('.section-block')));
      let found = false;

      for (const tr of allRows) {
        const issues = getRowReviewIssues(tr);
        const parentSec = tr.closest('.section-block');
        if (issues.length === 0 || !parentSec) continue;

        (window as any).navigateToSection(parentSec.id);

        // Buka sub-tab tempat baris berada (bisa bertingkat, mis. Check Part > Chassis > EBT)
        let panel = tr.closest('.section-subtab-panel') as HTMLElement | null;
        while (panel) {
          if (!panel.classList.contains('active')) {
            (document.querySelector(`.section-subtab[data-target="${panel.id}"]`) as HTMLElement | null)?.click();
          }
          panel = panel.parentElement?.closest('.section-subtab-panel') as HTMLElement | null;
        }

        // Kalau baris tersembunyi oleh filter tabel, tampilkan semua baris dulu
        if (tr.style.display === 'none') {
          (tr.closest('.table-card')?.querySelector('.counter-all') as HTMLElement | null)?.click();
        }

        const focusTarget = issues[0] === 'Engineer Check'
          ? tr.querySelector('.engineer-confirm-select') as HTMLElement | null
          : tr.querySelector('.remark-input') as HTMLElement | null;

        setTimeout(() => {
          tr.scrollIntoView({ behavior: 'smooth', block: 'center' });
          tr.classList.add('row-focused-pulse');
          focusTarget?.focus();
          setTimeout(() => tr.classList.remove('row-focused-pulse'), 2500);
        }, 150);
        found = true;
        break;
      }

      if (!found) {
        showNotification("All NG/Different rows already have Engineer Check and remarks!", "success");
      }
    };

    (window as any).filterCompareToolSection = function(btnElem: any, sectionName: string) {
      const tableCard = btnElem.closest('.table-card');
      if (!tableCard) return;
      const rows = tableCard.querySelectorAll('tbody tr');

      tableCard.querySelectorAll('.table-status-counter').forEach((b: HTMLElement) => b.classList.remove('active-filter'));
      btnElem.classList.add('active-filter');

      rows.forEach((tr: any) => {
        const cat = safeString(tr.getAttribute('data-category')).trim();
        if (cat.toLowerCase() === sectionName.toLowerCase() || cat.toLowerCase().includes(sectionName.toLowerCase())) {
          tr.style.display = '';
        } else {
          tr.style.display = 'none';
        }
      });
      // Hitung ulang merge sel Category (tabel Tool Option)
      refreshMergedCategoryCells(tableCard);
    };

    /**
     * Filter gabungan (dipakai tabel Structure, toolbar dengan data-combined-filter):
     *   - Level  : "Show BOM Level Only" (on) <-> "Show All" (off)
     *   - Result : "Show NG" / "Show Differences" / "Show OK" (klik lagi tombol yang aktif = batal)
     * Kedua filter berlaku bersamaan. "Show All" mereset semuanya.
     */
    function applyCombinedFilter(group: HTMLElement, filterType: string) {
      const tableCard = group.closest('.table-card');
      if (!tableCard) return;

      if (filterType === 'ALL') {
        group.dataset.levelFilter = 'off';
        group.dataset.resultFilter = 'ALL';
      } else if (filterType === 'BOM_LEVEL') {
        group.dataset.levelFilter = 'on';
      } else {
        group.dataset.resultFilter = group.dataset.resultFilter === filterType ? 'ALL' : filterType;
      }

      const levelOn = group.dataset.levelFilter === 'on';
      const resultFilter = group.dataset.resultFilter || 'ALL';

      // Tampilan tombol aktif
      group.querySelectorAll('.table-status-counter').forEach((b: Element) => {
        const type = b.getAttribute('data-filter');
        const active =
          (type === 'BOM_LEVEL' && levelOn) ||
          (type === 'ALL' && !levelOn && resultFilter === 'ALL') ||
          (type !== 'ALL' && type !== 'BOM_LEVEL' && type === resultFilter);
        b.classList.toggle('active-filter', active);
      });

      tableCard.querySelectorAll('tbody tr').forEach((tr: any) => {
        const status = safeString(tr.getAttribute('data-result')).toUpperCase();
        const bomLevel = safeString(tr.getAttribute('data-bom-level')).trim();

        const passLevel = !levelOn || (bomLevel !== '' && bomLevel !== '-');
        const passResult =
          resultFilter === 'ALL' ||
          (resultFilter === 'NG' && status === 'NG') ||
          (resultFilter === 'DIFFERENT' && (status === 'DIFFERENT' || status === 'CHECK')) ||
          (resultFilter === 'OK' && (status === 'OK' || status === 'SAME'));

        tr.style.display = passLevel && passResult ? '' : 'none';
      });
    }

    (window as any).filterTableRows = function(btnElem: any, filterType: string) {
      const combinedGroup = btnElem.closest('.table-status-counters[data-combined-filter]');
      if (combinedGroup) {
        applyCombinedFilter(combinedGroup, filterType);
        return;
      }

      const tableCard = btnElem.closest('.table-card');
      if (!tableCard) return;
      const rows = tableCard.querySelectorAll('tbody tr');

      tableCard.querySelectorAll('.table-status-counter').forEach((b: HTMLElement) => b.classList.remove('active-filter'));
      btnElem.classList.add('active-filter');

      rows.forEach((tr: any) => {
        const status = safeString(tr.getAttribute('data-result')).toUpperCase();
        const bomLevel = safeString(tr.getAttribute('data-bom-level')).trim();
        const selectElem = tr.querySelector('.engineer-confirm-select');
        const readonlyElem = tr.querySelector('.engineer-check-readonly');
        const engStatus = selectElem
          ? selectElem.value.toUpperCase()
          : readonlyElem ? safeString(readonlyElem.getAttribute('data-value')).toUpperCase() : 'UNCHECK';

        if (filterType === 'ALL') {
          tr.style.display = '';
        } else if (filterType === 'NG') {
          tr.style.display = (status === 'NG') ? '' : 'none';
        } else if (filterType === 'DIFFERENT') {
          tr.style.display = (status === 'DIFFERENT' || status === 'CHECK') ? '' : 'none';
        } else if (filterType === 'UNCHECK') {
          tr.style.display = (engStatus === 'UNCHECK') ? '' : 'none';
        } else if (filterType === 'OK') {
          tr.style.display = (status === 'OK' || status === 'SAME') ? '' : 'none';
        } else if (filterType === 'BOM_LEVEL') {
          tr.style.display = (bomLevel !== '' && bomLevel !== '-') ? '' : 'none';
        }
      });
      // Hitung ulang merge sel Category (tabel Tool Option)
      refreshMergedCategoryCells(tableCard);
    };

    (window as any).storePreviousResult = function(selectElem: any) {
      selectElem.setAttribute('data-prev-value', selectElem.value);
    };

    (window as any).updateEngineerConfirmStyle = function(selectElem: HTMLSelectElement) {
      const val = selectElem.value;
      selectElem.classList.remove('eng-uncheck', 'eng-ok', 'eng-ng');
      if (val === 'OK') {
        selectElem.classList.add('eng-ok');
      } else if (val === 'NG') {
        selectElem.classList.add('eng-ng');
      } else {
        selectElem.classList.add('eng-uncheck');
      }
      // Pilihan Engineer Check ikut menentukan apakah baris sudah direview
      updateProgressMetrics();
    };

    (window as any).updateResultStyle = function(selectElem: any, isSameDiffMode = false) {
      const val = selectElem.value;
      const prevVal = selectElem.getAttribute('data-prev-value') || (isSameDiffMode ? 'SAME' : 'OK');
      const tr = selectElem.closest('tr');
      const remarkInput = tr ? tr.querySelector('.remark-input') : null;

      const isPrevNotOk = isSameDiffMode ? prevVal.toUpperCase() === 'DIFFERENT' : (prevVal.toUpperCase() === 'CHECK' || prevVal.toUpperCase() === 'NG');
      const isNewOk = isSameDiffMode ? val.toUpperCase() === 'SAME' : val.toUpperCase() === 'OK';

      if (isPrevNotOk && isNewOk) {
        const currentRemark = remarkInput ? remarkInput.value : '';
        if (!isValidRemark(currentRemark)) {
          alert(`Warning: To change status to ${isSameDiffMode ? 'SAME' : 'OK'}, you must enter a valid remark.\n\nRemark Rules:\n1. Cannot be empty\n2. Cannot be symbols only\n3. Must contain valid text`);
          if (remarkInput) {
            remarkInput.classList.add('input-required');
            remarkInput.focus();
          }
          selectElem.value = prevVal;
          return;
        }
      }

      selectElem.classList.remove('res-ok', 'res-check', 'res-ng');
      if (isSameDiffMode) {
        if (val.toUpperCase() === 'SAME') selectElem.classList.add('res-ok');
        else selectElem.classList.add('res-ng');
      } else {
        if (val.toUpperCase() === 'OK') selectElem.classList.add('res-ok');
        else if (val.toUpperCase() === 'NG') selectElem.classList.add('res-ng');
        else selectElem.classList.add('res-check');
      }

      if (tr) {
        const normalized = val.toUpperCase();
        tr.setAttribute('data-result', normalized);
        tr.classList.remove('status-ok', 'status-check', 'status-ng');
        tr.classList.add((normalized === 'NG' || normalized === 'DIFFERENT') ? 'status-ng' : normalized === 'CHECK' ? 'status-check' : '');
        applyRowHighlightStyles(tr.closest('.table-card') || undefined);
      }
      if (remarkInput) remarkInput.classList.remove('input-required');

      selectElem.setAttribute('data-prev-value', val);
      (window as any).updateTableStatusCounters(tr ? tr.closest('.table-card') : null);
      if (currentMasterJson) {
        syncActionCenterAndNavigator(currentMasterJson);
        autoManageRightSidebarState(currentMasterJson);
      }
      updateProgressMetrics();
    };

    (window as any).copyCellValue = function(icon: any) {
      const span = icon.parentElement.querySelector('span');
      const value = span ? span.textContent : '';
      if (navigator.clipboard && value) {
        navigator.clipboard.writeText(value).then(() => alert(`Copied value: ${value}`));
      }
    };

    (window as any).updateTableStatusCounters = function(containerOrCard: any) {
      const card = containerOrCard && containerOrCard.classList && containerOrCard.classList.contains('table-card')
        ? containerOrCard
        : containerOrCard?.querySelector?.('.table-card');
      if (!card) return;

      let ng = 0;
      let check = 0;
      let different = 0;
      let unremarked = 0;

      card.querySelectorAll('tbody tr').forEach((row: any) => {
        const resultSelect = row.querySelector('.result-select');
        const remarkInput = row.querySelector('.remark-input');

        const status = safeString(resultSelect ? resultSelect.value : row.getAttribute('data-result')).trim().toUpperCase();
        if (status === 'NG') ng++;
        if (status === 'CHECK') check++;
        if (status === 'DIFFERENT' || status === 'CHECK') different++;

        if ((status === 'NG' || status === 'DIFFERENT' || status === 'CHECK') && remarkInput && !isValidRemark(remarkInput.value)) {
          unremarked++;
        }
      });

      const ngEl = card.querySelector('.counter-ng-value');
      const checkEl = card.querySelector('.counter-check-value');
      const unremarkedEl = card.querySelector('.counter-unremarked-value');
      if (ngEl) ngEl.textContent = ng;
      if (checkEl) checkEl.textContent = check;
      if (unremarkedEl) unremarkedEl.textContent = unremarked;
      const diffEl = card.querySelector('.counter-diff-value');
      if (diffEl) diffEl.textContent = different;
    };

    // ==========================================
    // SAVE DRAFT & ENGINEER CONFIRM -> dikirim ke backend
    // ==========================================
    const SAVE_REVIEW_ENDPOINT = '/api/sendremark';   // endpoint dari backend (main.py: post_remark_result)
    let saveMode: 'draft' | 'confirmed' = 'draft';
    let engineerConfirmed = false;

    /**
     * Kumpulkan Engineer Check & Remarks setiap baris di semua tab yang ikut review.
     * Hasilnya per modul (tab): [{ rowIndex, rowKey, category, mpxResult, engineerCheck, remark }]
     */
    function collectReviewData() {
      const modules: Record<string, any[]> = {};
      summaryModules.forEach(mod => {
        const section = id(mod.secId);
        if (!section) return;
        const rows: any[] = [];
        section.querySelectorAll('.table-card').forEach(card => {
          // Tab HW Option punya 2 tabel (Single / Multi): bedakan lewat id panel-nya
          const tableName = card.closest('.section-subtab-panel')?.id || mod.secId;
          card.querySelectorAll('tbody tr').forEach(tr => {
            const cells = tr.querySelectorAll('td');
            const cellText = (td: Element | undefined) =>
              td ? (td.querySelector('.static-cell-text')?.getAttribute('title') ?? td.textContent ?? '').trim() : '';
            const engSelect = tr.querySelector('.engineer-confirm-select') as HTMLSelectElement | null;
            const engReadonly = tr.querySelector('.engineer-check-readonly');
            const remarkInput = tr.querySelector('.remark-input') as HTMLInputElement | null;
            const category = tr.getAttribute('data-category') || '';
            // rowKey: isi kolom paling kiri yang tidak di-merge (mis. Option Key, Single Option, Description)
            const keyCell = Array.from(cells).find(td => !td.classList.contains('merge-cell'));
            rows.push({
              table: tableName,
              rowIndex: Number(tr.getAttribute('data-row-index')),
              rowKey: cellText(keyCell),
              category,
              mpxResult: tr.getAttribute('data-result') || '',
              engineerCheck: engSelect ? engSelect.value : engReadonly ? engReadonly.getAttribute('data-value') : null,
              remark: remarkInput ? remarkInput.value.trim() : '',
            });
          });
        });
        modules[mod.name] = rows;
      });
      return modules;
    }

    /** Payload yang dikirim ke backend (lihat penjelasan format di bawah kode / dokumentasi) */
    function buildSavePayload(finalRemark: string, status: 'draft' | 'confirmed') {
      return {
        crosschecking_result: {
          resultId: currentMasterJson?._id ?? null,           // _id dokumen Mongo yang sedang direview
          targetName: currentMasterJson?.targetName ?? '',
          devName: currentMasterJson?.devName ?? '',
          initName: currentMasterJson?.initName ?? '',
          version: currentMasterJson?.version ?? null,
          status,                                            // 'draft' = Save Draft, 'confirmed' = Engineer Confirm
          finalRemark,
          savedAt: new Date().toISOString(),
          modules: collectReviewData(),
        }
      };
    }

    async function sendReview(finalRemark: string, status: 'draft' | 'confirmed'): Promise<boolean> {
      const payload = buildSavePayload(finalRemark, status);
      console.log('>>> DATA YANG DIKIRIM KE BACKEND:', payload);
      try {
        const response = await fetch(SAVE_REVIEW_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!response.ok) {
          const text = await response.text();
          showNotification(`Save failed (HTTP ${response.status}): ${text || 'server error'}`, 'warning');
          return false;
        }
        return true;
      } catch (error: any) {
        showNotification(`Save failed: ${error?.message ?? error}`, 'warning');
        return false;
      }
    }

    function setSaveModalText(mode: 'draft' | 'confirmed') {
      setText('draftModalTitleText', mode === 'confirmed' ? 'Engineer Confirm' : 'Save Draft');
      setText('draftModalDesc', mode === 'confirmed'
        ? 'All NG / Different rows are checked. Enter your final remark to confirm and finish this crosscheck. After confirming, the result is locked.'
        : 'Enter your final remark. All Engineer Check values and Remarks in every table will be saved as a draft.');
      setText('draftModalSubmitText', mode === 'confirmed' ? 'Confirm & Finish' : 'Save Draft');
      const submitBtn = id('draftModalSubmitBtn');
      if (submitBtn) submitBtn.className = mode === 'confirmed' ? 'btn btn-confirm' : 'btn btn-dark';
    }

    (window as any).openSaveDraftModal = function(mode: 'draft' | 'confirmed' = 'draft') {
      if (isViewOnly) return;
      saveMode = mode;
      setSaveModalText(mode);
      const remarkBox = id('draftFinalRemark') as HTMLTextAreaElement | null;
      if (remarkBox) remarkBox.classList.remove('input-required');
      const draftModalOverlay = id('draftModalOverlay');
      if (draftModalOverlay) draftModalOverlay.classList.add('show');
      setTimeout(() => remarkBox?.focus(), 50);
    };

    (window as any).closeSaveDraftModal = function() {
      const draftModalOverlay = id('draftModalOverlay');
      if (draftModalOverlay) draftModalOverlay.classList.remove('show');
    };

    (window as any).confirmSaveDraft = async function() {
      if (isViewOnly) return;
      const remarkBox = id('draftFinalRemark') as HTMLTextAreaElement | null;
      const finalRemark = remarkBox ? remarkBox.value.trim() : '';
      if (!isValidRemark(finalRemark)) {
        remarkBox?.classList.add('input-required');
        showNotification('Final remark cannot be empty or symbols only.', 'warning');
        return;
      }

      const submitBtn = id('draftModalSubmitBtn') as HTMLButtonElement | null;
      if (submitBtn) submitBtn.disabled = true;
      const ok = await sendReview(finalRemark, saveMode);
      if (submitBtn) submitBtn.disabled = false;
      if (!ok) return;

      (window as any).closeSaveDraftModal();
      if (saveMode === 'confirmed') {
        engineerConfirmed = true;
        setEngineerConfirmButtonState();
        showNotification('Engineer Confirmation completed. Result has been saved.', 'success');
      } else {
        showNotification('Draft saved: Engineer Check & Remarks have been sent to the server.', 'success');
      }
    };

    /** Tampilan tombol Engineer Confirm: biasa / sudah dikonfirmasi */
    function setEngineerConfirmButtonState() {
      const btn = id('engineerConfirmBtn') as HTMLButtonElement | null;
      if (!btn) return;
      if (engineerConfirmed) {
        btn.classList.add('confirmed');
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Confirmed';
      }
    }

    /**
     * Tombol Engineer Confirm (menyelesaikan pekerjaan).
     * Syarat: setiap baris NG / DIFFERENT sudah dipilih Engineer Check (OK/NG) dan diisi remark.
     */
    (window as any).engineerConfirm = function() {
      if (isViewOnly || engineerConfirmed) return;
      let pendingTotal = 0;
      const pendingPerTab: string[] = [];

      document.querySelectorAll('.section-block').forEach(section => {
        if (!isReviewSection(section)) return;
        let pending = 0;
        section.querySelectorAll('tbody tr').forEach(row => {
          if (getRowReviewIssues(row).length > 0) pending++;
        });
        if (pending === 0) return;

        pendingTotal += pending;
        const tabTitle = document.querySelector(`.tab-item[href="#${section.id}"] .tab-title`)?.textContent?.replace(/\s*\(\d+\)$/, '').trim();
        pendingPerTab.push(`${tabTitle || section.id} (${pending})`);
      });

      if (pendingTotal > 0) {
        showNotification(
          `Cannot confirm yet: ${pendingTotal} NG/Different row(s) still need Engineer Check (OK/NG) and a remark — ${pendingPerTab.join(', ')}`,
          "warning"
        );
        (window as any).resolveNextIssue();
        return;
      }
      (window as any).openSaveDraftModal('confirmed');
    };

    (window as any).downloadDeliverable = function(format: string) {
      showNotification(`Exporting deliverables dataset in .${format.toUpperCase()} format...`, "info");
      setTimeout(() => {
        showNotification(`Deliverable dataset download ready (.${format})!`, "success");
      }, 1200);
    };

    const initWorkspaceTabs = () => {
      const mainTabs = document.querySelectorAll('.chrome-tabs-bar .tab-item');
      mainTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
          e.preventDefault();
          const targetId = tab.getAttribute('href')?.replace('#', '');
          if (targetId) {
            (window as any).navigateToSection(targetId);
          }
        });
      });
    };

    const loadResultData = async () => {
      const loadingOverlay = id('global-loading-overlay');
      if (loadingOverlay) loadingOverlay.classList.add('show');

      const params = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : new URLSearchParams();
      const targetModel = searchParams.get('targetModel') || params.get('targetModel') || '';
      const devModel = searchParams.get('devModel') || params.get('devModel') || '';
      const initModel = searchParams.get('initModel') || params.get('initModel') || '';

      if (initialData && initialData.length > 0) {
        const row = initialData.find((r: any) => r.mpModel === targetModel);
        if (row) {
          const parseJSON = (val: any) => {
            if (!val) return undefined;
            if (typeof val === 'object') return val;
            try { return JSON.parse(val); } catch (e) { return undefined; }
          };

          const processedData = {
            ...row,
            targetName: row.mpModel,
            devName: row.devModel,
            initName: row.initialModel,
            structureCompare: parseJSON(row.structure),
            benComapre: parseJSON(row.benComp),
            benCompare: parseJSON(row.benComp),
            subsCheck: parseJSON(row.substituteCheck),
            multiOption: parseJSON(row.hwTool),
            toolOptCompare: parseJSON(row.toolOption),
            OperationPlan: parseJSON(row.operationPlan),
            eaxSubstitute: parseJSON(row.eaxSubstitute || row.eax_substitute),
            checkPart: parseJSON(row.checkPart || row.check_part),
            SummaryResult: parseJSON(row.SummaryResult || row.summary_result)
          };

          console.log(">>> DATA JSON DARI BACKEND:", processedData);
          processMasterJson(processedData);
          if (loadingOverlay) loadingOverlay.classList.remove('show');
          return;
        }
      }

      if (!targetModel && !devModel && !initModel) {
        if (loadingOverlay) loadingOverlay.classList.remove('show');
        const container = document.getElementById('container-crosschecking-result');
        if (container) {
          container.innerHTML = `
            <div class="empty-state" style="color: var(--imperial-red); font-weight: bold;">
              No model parameters provided in the URL query string.<br/>
              Please select a model from the dashboard.
            </div>
          `;
        }
        return;
      }

      // Kalau backend error 5xx (mis. dokumen Mongo terbaru sedang/baru ditulis oleh proses retest),
      // coba ulang otomatis beberapa kali sebelum menampilkan pesan error
      const MAX_ATTEMPTS = 3;
      const RETRY_DELAY_MS = 3000;
      const loadingSub = document.querySelector('#global-loading-overlay .loading-subtext');

      const fetchViewResult = async (): Promise<Response> => {
        let lastResponse: Response | null = null;
        for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
          lastResponse = await fetch('/api/bom/view_result', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ targetModel, devModel, initModel })
          });
          if (lastResponse.ok || lastResponse.status < 500 || attempt === MAX_ATTEMPTS) return lastResponse;
          console.warn(`view_result gagal (HTTP ${lastResponse.status}), percobaan ${attempt}/${MAX_ATTEMPTS}. Mencoba lagi...`);
          if (loadingSub) loadingSub.textContent = `Server error (HTTP ${lastResponse.status}), retrying ${attempt}/${MAX_ATTEMPTS - 1}...`;
          await new Promise(res => setTimeout(res, RETRY_DELAY_MS));
        }
        return lastResponse as Response;
      };

      // Pesan error ditampilkan di semua area tabel (supaya terlihat di tab mana pun yang terbuka)
      const showLoadError = (title: string, detail: string) => {
        const html = `
          <div class="empty-state load-error-state">
            <div style="font-weight: 800; color: var(--imperial-red);"><i class="fa-solid fa-triangle-exclamation"></i> ${escapeHtml(title)}</div>
            <div style="margin-top: 6px; font-size: 11px; color: var(--text-muted); word-break: break-word;">${escapeHtml(detail)}</div>
            <button class="btn btn-secondary" style="margin-top: 10px;" onclick="window.location.reload()"><i class="fa-solid fa-rotate-right"></i> Reload</button>
          </div>`;
        document.querySelectorAll('.section-block .table-container').forEach(el => { el.innerHTML = html; });
        showNotification(title, 'warning');
      };

      try {
        const response = await fetchViewResult();

        if (response.ok) {
          let rawData = await response.json();
          if (typeof rawData === 'string') {
            try { rawData = JSON.parse(rawData); } catch (e) { console.error(e); }
          }

          let processedData = rawData;
          if (Array.isArray(rawData) && rawData.length > 0) {
            processedData = rawData[0];
          } else if (rawData && rawData.data) {
            processedData = rawData.data;
          }

          console.log(">>> DATA JSON DARI BACKEND:", processedData);
          processMasterJson(processedData);
        } else {
          const errorText = await response.text();
          console.error(`view_result error HTTP ${response.status}:`, errorText);
          showLoadError(`Error ${response.status}: Failed to load crosscheck result.`, errorText || 'Internal server error occurred.');
        }
      } catch (error: any) {
        console.error("Error fetching result data:", error);
        showLoadError('Failed to connect to the server.', String(error?.message ?? error));
      } finally {
        if (loadingOverlay) loadingOverlay.classList.remove('show');
      }
    };

    loadResultData();
    initWorkspaceTabs();

    if (!listenersAttached.current) {
      document.querySelectorAll('.table-card').forEach((card) => (window as any).updateTableStatusCounters(card));
      initializeTableColumnBehavior(document);

      document.querySelectorAll('.section-subtabs').forEach(tabBar => {
        const buttons = tabBar.querySelectorAll('.section-subtab');
        buttons.forEach(button => {
          button.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('active'));
            tabBar.parentElement?.querySelectorAll(':scope > .section-subtab-panel').forEach(panel => {
              panel.classList.remove('active');
            });
            button.classList.add('active');
            const target = id(button.getAttribute('data-target') || '');
            if (target) target.classList.add('active');
            scheduleFitFreezeTables();
          });
        });
      });

      window.addEventListener('resize', scheduleFitFreezeTables);

      listenersAttached.current = true;
    }

    return () => {
      viewOnlyObserver?.disconnect();
    };
  }, [searchParams, initialData, canEdit, bomConfig]);

  return (
    <>
      <Head>
        <title>MPX BOM Crosschecking Workspace</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
      </Head>

      <style dangerouslySetInnerHTML={{ __html: `
        :root {
          --imperial-red: #FB3640;
          --penn-blue: #00043A;
          --royal-blue: #0A2463;
          --cardinal-red: #BF3242;

          --bg-canvas: #F4F6F9;
          --bg-card: #FFFFFF;
          --bg-subtle-blue: #EEF2F9;
          --bg-subtle-red: #FFF0F1;
          --bg-subtle-amber: #FFF8E6;

          --border-color: #DCE3ED;
          --border-focus: #FB3640;
          --text-main: #00043A;
          --text-muted: #5C6B8A;

          /* Warna badge MPX Result (semua tabel) */
          --badge-ok-bg: #BCFFCD;
          --badge-ok-text: #34C759;
          --badge-pass-bg: #D8D8D8;
          --badge-pass-text: #858585;
          --badge-ng-bg: #F8C3C3;
          --badge-ng-text: #D32F2F;
          --badge-check-bg: #FFE371;
          --badge-check-text: #FF6B2C;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        html { scroll-behavior: smooth; }

        body {
          background-color: var(--bg-canvas);
          color: var(--text-main);
          display: flex;
          flex-direction: column;
          min-height: 100vh;
          position: relative;
          overflow-x: auto;
        }

        .toast-notification-container {
          position: fixed;
          top: 20px;
          right: 20px;
          z-index: 100000;
          display: flex;
          flex-direction: column;
          gap: 10px;
          pointer-events: none;
        }

        .toast-item {
          background: var(--penn-blue);
          color: #ffffff;
          padding: 12px 18px;
          border-radius: 8px;
          border-left: 4px solid var(--imperial-red);
          box-shadow: 0 8px 24px rgba(0, 4, 58, 0.25);
          font-size: 13px;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 10px;
          opacity: 0;
          transform: translateY(-20px);
          transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
          pointer-events: auto;
          max-width: 420px;
        }

        .toast-item.show { opacity: 1; transform: translateY(0); }
        .toast-item.toast-success { border-left-color: #10B981; }
        .toast-item.toast-success i { color: #10B981; }
        .toast-item.toast-warning { border-left-color: #F59E0B; }
        .toast-item.toast-warning i { color: #F59E0B; }
        .toast-item.toast-info i { color: var(--imperial-red); }
        .toast-content { display: flex; align-items: center; gap: 10px; }

        .global-loading-overlay {
          position: fixed;
          top: 0; left: 0;
          width: 100vw; height: 100vh;
          background-color: rgba(244, 246, 249, 0.95);
          backdrop-filter: blur(4px);
          z-index: 999999;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          opacity: 0;
          visibility: hidden;
          transition: opacity 0.3s ease, visibility 0.3s ease;
        }
        .global-loading-overlay.show { opacity: 1; visibility: visible; }
        .loading-spinner {
          width: 50px; height: 50px;
          border: 4px solid var(--bg-subtle-blue);
          border-top: 4px solid var(--imperial-red);
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
          margin-bottom: 16px;
        }
        .loading-text { font-size: 16px; font-weight: 700; color: var(--penn-blue); }
        .loading-subtext { font-size: 12px; color: var(--text-muted); margin-top: 6px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        .header-top-block {
          background: var(--bg-card);
          border-bottom: 1px solid var(--border-color);
          padding: 16px 32px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .header-row-main {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 16px;
        }

        .header-title-group {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .workspace-main-title {
          font-size: 18px;
          font-weight: 800;
          color: var(--penn-blue);
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .model-header-subrow {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-top: 2px;
        }

        .model-name-badge {
          background: var(--penn-blue);
          color: #FFFFFF;
          padding: 4px 10px;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 800;
          letter-spacing: 0.5px;
        }

        .revision-pill {
          background: var(--royal-blue);
          color: #FFFFFF;
          padding: 3px 8px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 700;
        }

        .progress-indicator-box {
          display: flex;
          align-items: center;
          gap: 8px;
          background: var(--bg-subtle-blue);
          padding: 4px 10px;
          border-radius: 6px;
          border: 1px solid var(--border-color);
          font-size: 11px;
          font-weight: 700;
          color: var(--penn-blue);
        }

        .progress-bar-track {
          width: 80px;
          height: 6px;
          background: var(--border-color);
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-bar-fill {
          height: 100%;
          width: 0%;
          background: var(--imperial-red);
          transition: width 0.3s ease;
        }

        .header-widget-group {
          display: flex;
          align-items: center;
          gap: 10px;
          flex-wrap: wrap;
        }

        .engineer-confirm-widget {
          display: flex;
          align-items: center;
          gap: 8px;
          background-color: var(--bg-subtle-blue);
          padding: 6px 12px;
          border-radius: 6px;
          border: 1px solid var(--border-color);
          font-size: 11px;
          font-weight: 700;
        }

        .deliverables-dropdown, .show-tab-dropdown {
          position: relative;
          display: inline-block;
        }

        .deliverables-dropdown-content, .show-tab-dropdown-content {
          display: none;
          position: absolute;
          right: 0;
          top: 100%;
          margin-top: 4px;
          background-color: var(--bg-card);
          min-width: 200px;
          box-shadow: 0 8px 16px rgba(0, 4, 58, 0.15);
          border: 1px solid var(--border-color);
          border-radius: 6px;
          z-index: 1000;
          overflow: hidden;
        }

        .deliverables-dropdown:hover .deliverables-dropdown-content,
        .show-tab-dropdown:hover .show-tab-dropdown-content {
          display: block;
        }

        .deliverables-dropdown-content button, .show-tab-dropdown-content button {
          color: var(--text-main);
          padding: 8px 12px;
          text-decoration: none;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
          width: 100%;
          border: none;
          background: transparent;
          font-size: 11px;
          font-weight: 600;
          cursor: pointer;
          text-align: left;
        }

        .deliverables-dropdown-content button:hover, .show-tab-dropdown-content button:hover {
          background-color: var(--bg-subtle-blue);
          color: var(--imperial-red);
        }

        .guided-navigator-bar {
          background: var(--bg-card);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          padding: 10px 16px;
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
        }

        .guided-nav-title {
          font-size: 12px;
          font-weight: 800;
          color: var(--penn-blue);
          text-transform: uppercase;
          display: flex;
          align-items: center;
          gap: 6px;
          white-space: nowrap;
        }

        .guided-nav-actions {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .resolve-issue-btn {
          background: var(--imperial-red);
          color: #FFFFFF;
          border: none;
          padding: 6px 14px;
          border-radius: 6px;
          font-size: 11px;
          font-weight: 700;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 6px;
          box-shadow: 0 2px 6px rgba(251, 54, 64, 0.3);
          transition: all 0.2s ease;
        }

        .resolve-issue-btn:hover {
          background: var(--cardinal-red);
        }

        .show-summary-nav-btn {
          background: var(--penn-blue);
          color: #FFFFFF;
          border: 1px solid var(--royal-blue);
          padding: 6px 14px;
          border-radius: 6px;
          font-size: 11px;
          font-weight: 700;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 6px;
          transition: all 0.2s ease;
        }

        .show-summary-nav-btn:hover {
          background: var(--imperial-red);
          border-color: var(--imperial-red);
        }

        .chrome-tabs-container {
          background-color: #E2E8F0;
          padding: 8px 12px 0 12px;
          border-radius: 12px 12px 0 0;
          border: 1px solid var(--border-color);
          border-bottom: none;
          position: relative;
        }

        .chrome-tabs-bar {
          display: flex;
          align-items: flex-end;
          gap: 4px;
          overflow-x: auto;
          white-space: nowrap;
          scrollbar-width: none;
        }

        .chrome-tabs-bar::-webkit-scrollbar { display: none; }

        .tab-item {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          font-size: 12px;
          font-weight: 600;
          color: var(--text-muted);
          background: transparent;
          border-radius: 10px 10px 0 0;
          text-decoration: none;
          cursor: pointer;
          position: relative;
          transition: background-color 0.15s ease, color 0.15s ease;
          user-select: none;
        }

        .tab-item:hover {
          background: rgba(255, 255, 255, 0.5);
          color: var(--penn-blue);
        }

        .tab-item.active {
          background: var(--bg-card);
          color: var(--imperial-red);
          font-weight: 800;
          z-index: 2;
          box-shadow: 0 -2px 10px rgba(0, 4, 58, 0.04);
        }

        .tab-item.active::before {
          content: "";
          position: absolute;
          bottom: 0;
          left: -10px;
          width: 10px;
          height: 10px;
          background: radial-gradient(circle at 0 0, transparent 10px, var(--bg-card) 10px);
          pointer-events: none;
        }

        .tab-item.active::after {
          content: "";
          position: absolute;
          bottom: 0;
          right: -10px;
          width: 10px;
          height: 10px;
          background: radial-gradient(circle at 100% 0, transparent 10px, var(--bg-card) 10px);
          pointer-events: none;
        }

        .tab-close-icon {
          font-size: 11px;
          color: var(--text-muted);
          border-radius: 50%;
          width: 16px;
          height: 16px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          margin-left: 4px;
          transition: all 0.2s ease;
        }

        .tab-close-icon:hover {
          background-color: rgba(251, 54, 64, 0.15);
          color: var(--imperial-red);
        }

        .tab-item.tab-highlight-ng { border-top: 3px solid var(--imperial-red); }
        .tab-item.tab-highlight-check { border-top: 3px solid #F59E0B; }

        .table-toolbar {
          padding: 8px 12px;
          background-color: var(--bg-card);
          border-bottom: 1px solid var(--border-color);
          display: flex;
          align-items: center;
          justify-content: flex-start;
        }

        .table-status-counters {
          display: flex;
          align-items: center;
          gap: 6px;
          flex-wrap: wrap;
        }

        .table-status-counter {
          background: var(--bg-card);
          border: 1px solid var(--border-color);
          border-radius: 6px;
          padding: 4px 10px;
          font-size: 11px;
          font-weight: 700;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 6px;
          color: var(--penn-blue);
          transition: all 0.2s ease;
        }

        .table-status-counter:hover { background: var(--bg-subtle-blue); border-color: var(--royal-blue); }

        .table-status-counter.counter-ng { color: var(--imperial-red); }
        .table-status-counter.counter-check { color: #D97706; }
        .table-status-counter.counter-uncheck { color: var(--text-muted); }
        .table-status-counter.counter-ok { color: #10B981; }
        .table-status-counter.counter-bom { color: var(--royal-blue); }

        .table-status-counter.active-filter {
          background: var(--penn-blue) !important;
          color: #FFFFFF !important;
          border-color: var(--penn-blue) !important;
        }

        .table-status-counter.active-filter.counter-ng { background: var(--imperial-red) !important; border-color: var(--imperial-red) !important; }
        .table-status-counter.active-filter.counter-check { background: #D97706 !important; border-color: #D97706 !important; }
        .table-status-counter.active-filter.counter-uncheck { background: #64748B !important; border-color: #64748B !important; }
        .table-status-counter.active-filter.counter-ok { background: #10B981 !important; border-color: #10B981 !important; }

        .main-container {
          width: 100%;
          padding: 20px 32px 16px 32px;
          flex-grow: 1;
        }

        .workspace-split-layout {
          display: flex;
          gap: 20px;
          align-items: flex-start;
          width: 100%;
        }

        .workspace-main-col {
          flex: 1;
          min-width: 0;
          display: flex;
          flex-direction: column;
        }

        .table-card {
          background: var(--bg-card);
          border: 1px solid var(--border-color);
          border-radius: 0 0 12px 12px;
          box-shadow: 0 4px 16px rgba(0, 4, 58, 0.04);
          margin-bottom: 24px;
          overflow: hidden;
          width: 100%;
          margin-top: -1px;
        }

        /* Scrollbar umum di halaman ini (halaman, sidebar, dropdown, dll.).
           Menimpa scrollbar merah tipis dari globals.css supaya jelas terlihat sebagai scrollbar:
           ada jalur (track) abu muda dan pegangan (thumb) abu yang cukup lebar untuk di-drag. */
        html { scrollbar-color: #A0AEC0 #EEF2F7; }   /* Firefox */
        ::-webkit-scrollbar { width: 12px; height: 12px; }
        ::-webkit-scrollbar-track { background: #EEF2F7; border-radius: 0; }
        ::-webkit-scrollbar-thumb {
          background-color: #A0AEC0;
          border-radius: 8px;
          border: 2px solid #EEF2F7;
          min-height: 40px;
        }
        ::-webkit-scrollbar-thumb:hover { background-color: #64748B; }
        ::-webkit-scrollbar-corner { background: #EEF2F7; }

        /* Komponen tabel: tidak menempel ke tepi kartu, border abu tebal + shadow tipis + sudut membulat */
        .table-wrapper {
          width: auto;
          margin: 14px 16px 16px 16px;
          overflow: auto;
          border: 2px solid #CBD5E1;
          border-radius: 10px;
          box-shadow: 0 2px 10px rgba(0, 4, 58, 0.08);
          background-color: var(--bg-card);
          /* Firefox: scrollbar tebal */
          scrollbar-width: auto;
          scrollbar-color: #94A3B8 #EEF2F7;
        }

        /* Chrome / Edge: scrollbar besar & tebal, mudah di-drag pakai mouse */
        .table-wrapper::-webkit-scrollbar { width: 16px; height: 16px; }
        .table-wrapper::-webkit-scrollbar-track { background: #EEF2F7; }
        .table-wrapper::-webkit-scrollbar-thumb {
          background-color: #94A3B8;
          border-radius: 10px;
          border: 3px solid #EEF2F7;
        }
        .table-wrapper::-webkit-scrollbar-thumb:hover { background-color: #64748B; }
        .table-wrapper::-webkit-scrollbar-corner { background: #EEF2F7; }

        .dynamic-table {
          width: 100%;
          border-collapse: separate;
          border-spacing: 0;
          text-align: left;
          font-size: 11px;
          table-layout: auto;
        }

        .model-banner-row {
          background-color: var(--penn-blue);
        }

        .model-banner-th {
          padding: 6px 12px;
          font-size: 11.5px;
          font-weight: 800;
          letter-spacing: 0.4px;
          text-transform: uppercase;
          text-align: center;
          border-bottom: 1px solid var(--border-color);
          border-right: 1px solid var(--border-color);
          color: #FFFFFF;
          vertical-align: middle;
        }

        .model-banner-init { background-color: #1E293B; color: #94A3B8; }
        .model-banner-dev { background-color: var(--royal-blue); color: #93C5FD; }
        .model-banner-target { background-color: var(--penn-blue); color: #FCA5A5; }

        /* Header semua tabel: font lebih besar & jelas, rata tengah */
        .dynamic-table th {
          background-color: var(--bg-canvas);
          padding: 8px 12px;
          font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.2px;
          color: var(--penn-blue);
          text-transform: none;
          text-align: center;
          vertical-align: middle;
          border-bottom: 1px solid var(--border-color);
          border-right: 1px solid var(--border-color);
          position: relative;
        }

        .dynamic-table td {
          padding: 8px 12px;
          border-bottom: 1px solid var(--border-color);
          border-right: 1px solid var(--border-color);
          color: var(--text-main);
          vertical-align: middle;
          background-color: var(--bg-card);
          transition: background-color 0.2s ease;
        }

        .dynamic-table td.cell-highlight-reason {
          background-color: #FEF2F2 !important;
          color: var(--imperial-red) !important;
          font-weight: bold;
          border: 1px solid var(--imperial-red) !important;
        }

        .dynamic-table td input.remark-input {
          background-color: #ffffff !important;
          border: 1px solid #d1d5db !important;
          color: #1f2937 !important;
        }

        .dynamic-table td.cell-highlight-red-red {
          background-color: #FEE2E2 !important;
          color: #DC2626 !important;
          font-weight: 700 !important;
          border: 1px solid #F87171 !important;
        }

        .dynamic-table tr:hover td { background-color: var(--bg-subtle-blue); }

        .dynamic-table tr.highlight-row-ng td,
        .dynamic-table tr.highlight-row-different td,
        .dynamic-table tr.highlight-row-difference-reason td {
          background-color: var(--bg-subtle-red) !important;
          color: #991B1B !important;
          border-bottom-color: rgba(251, 54, 64, 0.2) !important;
        }

        .dynamic-table tr.highlight-row-ng td:first-child,
        .dynamic-table tr.highlight-row-different td:first-child,
        .dynamic-table tr.highlight-row-difference-reason td:first-child {
          border-left: 4px solid var(--imperial-red) !important;
        }

        .dynamic-table tr.highlight-row-check td {
          background-color: var(--bg-subtle-amber) !important;
          color: #92400E !important;
          border-bottom-color: #FDE68A !important;
        }

        .dynamic-table tr.highlight-row-check td:first-child {
          border-left: 4px solid #F59E0B !important;
        }

        .dynamic-table th .column-resizer {
          position: absolute;
          top: 0; right: -3px;
          width: 7px; height: 100%;
          cursor: col-resize;
          z-index: 3;
        }

        .dynamic-table th .column-resizer:hover, .dynamic-table th .column-resizer.resizing { background-color: var(--imperial-red); }

        .status-read-only-pill {
          display: inline-block;
          padding: 3px 8px;
          border-radius: 4px;
          font-size: 10px;
          font-weight: 800;
          text-align: center;
          user-select: none;
        }
        .status-read-only-pill.status-pill-same {
          background-color: #e6f4ea;
          color: #137333;
          border: 1px solid #a7f3d0;
        }
        .status-read-only-pill.status-pill-different {
          background-color: var(--bg-subtle-red);
          color: var(--imperial-red);
          border: 1px solid rgba(251, 54, 64, 0.3);
        }

        /* =====================================================================
         * TABEL FREEZE (dipakai tabel Structure & Tool Option, class "freeze-table")
         * Header freeze di atas, kolom freeze kiri & kanan.
         * Lebar kolom freeze dibuat tetap supaya posisi left / right-nya pasti.
         * Kalau lebar diubah, sesuaikan juga nilai left / right-nya (lihat bagian per tabel di bawah).
         * ===================================================================== */
        /* ---------------------------------------------------------------
         * >>> PENGATURAN WARNA & BORDER TABEL FREEZE (silakan eksperimen di sini) <<<
         *   --ft-fixed-* : header abu-abu
         *                  Structure   : Category, Reference Type, MPX Result, Reason, Remarks
         *                  Tool Option : Category / Section, Option Key, JIRA Power Cons, MPX Result, Engineer Check, Remarks
         *   --ft-c1-*    : warna grup 1 (indigo) -> Structure: Reference Document | Tool Option & tabel compare: Initial Model
         *   --ft-c2-*    : warna grup 2 (hijau)  -> Structure: Target Model (MP)  | Tool Option & tabel compare: Development Model
         *   --ft-c3-*    : warna grup 3 (ungu)   -> Structure: Initial Model      | Tool Option & tabel compare: Target Model (MP)
         *   --ft-c4-*    : warna grup 4 (cyan)   -> HW Option: Initial Region
         *   (tabel compare = Single / Multi HW Option, Substitute, Assy Release Status)
         *   --ft-thick-border : border tebal (||) antar grup & antar kategori
         * --------------------------------------------------------------- */
        .dynamic-table.freeze-table {
          --ft-fixed-bg: #F3F4F6;
          --ft-fixed-text: var(--penn-blue);
          --ft-c1-bg: #EEF2FF;
          --ft-c1-text: #4F46E5;
          --ft-c2-bg: #F0FDF4;
          --ft-c2-text: #16A34A;
          --ft-c3-bg: #FDF4FF;
          --ft-c3-text: #C026D3;
          --ft-c4-bg: #ECFEFF;
          --ft-c4-text: #0891B2;
          --ft-thick-border: 3px solid #d2d7ddff;
        }

        /* Tinggi area scroll tabel freeze diatur otomatis oleh fitFreezeTablesToViewport() (JS),
           nilai di bawah hanya cadangan sebelum JS berjalan */
        .table-wrapper.freeze-wrapper {
          max-height: max(320px, calc(100vh - 300px));
          min-height: 200px;
        }

        /* Lebar minimal area tabel = lebar kolom freeze kiri + kanan + area scroll minimal 240px.
           Dipasang di kolom utama (workspace-main-col) sesuai tabel di tab yang sedang aktif, supaya
           kalau window lebih sempit halaman bisa di-scroll horizontal dan isi tabel tidak tertutup kolom freeze */
        .workspace-main-col:has(.section-block.active-tab-panel .table-card.fw-structure)  { min-width: 870px; }   /* freeze 170 + 410 + margin/scrollbar */
        .workspace-main-col:has(.section-block.active-tab-panel .table-card.fw-tooloption) { min-width: 1140px; }  /* freeze 360 + 490 + margin/scrollbar */
        .workspace-main-col:has(.section-block.active-tab-panel .table-card.fw-compare)    { min-width: 1000px; }  /* freeze 220 + 490 + margin/scrollbar */

        .dynamic-table.freeze-table td { white-space: nowrap; }

        /* --- Header: tiap baris tingginya tetap 36px, freeze di atas --- */
        .dynamic-table.freeze-table thead th {
          position: sticky;
          z-index: 3;
          height: 36px;
          padding-top: 0;
          padding-bottom: 0;
          white-space: nowrap;
          text-align: center;
        }
        /* Header yang tingginya lebih dari 1 baris (rowspan) boleh turun 2 baris */
        .dynamic-table.freeze-table thead th[rowspan] { white-space: normal; line-height: 1.3; }
        .dynamic-table.freeze-table thead th.hdr-r1 { top: 0; }
        .dynamic-table.freeze-table thead th.hdr-r2 { top: 36px; }
        .dynamic-table.freeze-table thead th.hdr-r3 { top: 72px; }

        /* Font header: banner & nama kolom normal (tanpa uppercase), nama model TV uppercase */
        .dynamic-table.freeze-table thead th.hdr-banner { font-size: 12.5px; letter-spacing: 0.2px; text-transform: none; }
        .dynamic-table.freeze-table thead th.hdr-name { font-size: 12.5px; font-weight: 700; text-transform: uppercase; }
        /* Link di header (mis. JIRA Power Cons. dari Crosscheck Configuration) */
        .dynamic-table thead th .hdr-link { color: #1D4ED8; text-decoration: underline; text-underline-offset: 2px; }
        .dynamic-table thead th .hdr-link:hover { color: #1E3A8A; }
        .dynamic-table thead th .hdr-link i { font-size: 10px; margin-left: 2px; }

        /* Warna header per grup (nilai warna ada di variabel --ft-* di atas) */
        .dynamic-table.freeze-table thead th.grp-fixed { background-color: var(--ft-fixed-bg); color: var(--ft-fixed-text); }
        .dynamic-table.freeze-table thead th.grp-c1    { background-color: var(--ft-c1-bg);    color: var(--ft-c1-text); }
        .dynamic-table.freeze-table thead th.grp-c2    { background-color: var(--ft-c2-bg);    color: var(--ft-c2-text); }
        .dynamic-table.freeze-table thead th.grp-c3    { background-color: var(--ft-c3-bg);    color: var(--ft-c3-text); }
        .dynamic-table.freeze-table thead th.grp-c4    { background-color: var(--ft-c4-bg);    color: var(--ft-c4-text); }

        /* --- Kolom freeze kiri / kanan --- */
        .dynamic-table.freeze-table .freeze-left,
        .dynamic-table.freeze-table .freeze-right {
          position: sticky;
          z-index: 2;
        }
        /* Header di pojok (freeze atas + kiri/kanan) harus di atas semua sel lain */
        .dynamic-table.freeze-table thead th.freeze-left,
        .dynamic-table.freeze-table thead th.freeze-right { z-index: 5; }

        /* Bayangan tipis di sisi kolom freeze terakhir (kiri) & pertama (kanan) */
        .dynamic-table.freeze-table .freeze-left-edge { box-shadow: 4px 0 6px -3px rgba(0, 4, 58, 0.18); }
        .dynamic-table.freeze-table .freeze-right-edge { box-shadow: -4px 0 6px -3px rgba(0, 4, 58, 0.18); }

        .dynamic-table.freeze-table td.freeze-left .static-cell-text,
        .dynamic-table.freeze-table td.freeze-right .static-cell-text {
          display: block;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        /* Kotak input Remarks & dropdown Engineer Check mengikuti lebar kolom */
        .dynamic-table.freeze-table td.freeze-right .remark-input { width: 100%; min-width: 0; }
        .dynamic-table.freeze-table td.freeze-right .engineer-confirm-select { width: 100%; }
        .dynamic-table.freeze-table td.cell-bold { font-weight: 700; color: var(--penn-blue); }

        /* --- Border: || = tebal (pemisah grup), | = normal --- */
        .dynamic-table.freeze-table th.thick-right,
        .dynamic-table.freeze-table td.thick-right { border-right: var(--ft-thick-border); }
        .dynamic-table.freeze-table th.thick-left,
        .dynamic-table.freeze-table td.thick-left { border-left: var(--ft-thick-border); }
        .dynamic-table.freeze-table th.no-right-border,
        .dynamic-table.freeze-table td.no-right-border { border-right: none; }

        /* --- Lebar & posisi kolom freeze: TABEL STRUCTURE --- */
        /* Kiri : Category 170px. Reference Type ikut scroll (min 110px) */
        .dynamic-table.structure-table .fl-1 { left: 0;     width: 170px; min-width: 170px; max-width: 170px; }
        .dynamic-table.structure-table .col-ref-type { min-width: 110px; }
        /* Kanan: MPX Result 100px + Reason 130px + Remarks 180px */
        .dynamic-table.structure-table .fr-3 { right: 310px; width: 100px; min-width: 100px; max-width: 100px; }
        .dynamic-table.structure-table .fr-2 { right: 180px; width: 130px; min-width: 130px; max-width: 130px; }
        .dynamic-table.structure-table .fr-1 { right: 0;     width: 180px; min-width: 180px; max-width: 180px; }

        /* --- Lebar & posisi kolom freeze: TABEL TOOL OPTION --- */
        /* Kiri : Category / Section 170px + Option Key 190px */
        .dynamic-table.tooloption-table .fl-1 { left: 0;     width: 170px; min-width: 170px; max-width: 170px; }
        .dynamic-table.tooloption-table .fl-2 { left: 170px; width: 190px; min-width: 190px; max-width: 190px; }
        /* Kanan: MPX Result 120px + Engineer Check 130px + Remarks 240px
           Kalau lebar diubah: right .fr-2 = lebar Remarks, right .fr-3 = lebar Remarks + Engineer Check */
        .dynamic-table.tooloption-table .fr-3 { right: 370px; width: 120px; min-width: 120px; max-width: 120px; }
        .dynamic-table.tooloption-table .fr-2 { right: 240px; width: 130px; min-width: 130px; max-width: 130px; }
        .dynamic-table.tooloption-table .fr-1 { right: 0;     width: 240px; min-width: 240px; max-width: 240px; }
        /* Kolom nilai model & JIRA: tabel tetap full width, sisa ruang dibagi rata ke 4 kolom ini (masing-masing ~12%) */
        .dynamic-table.tooloption-table .col-value { width: 12%; min-width: 130px; }
        .dynamic-table.tooloption-table td.col-value .static-cell-text { display: block; overflow: hidden; text-overflow: ellipsis; }
        /* Font kolom Category / Section & Option Key sedikit lebih besar */
        .dynamic-table.tooloption-table td.cell-category,
        .dynamic-table.tooloption-table td.cell-option-key { font-size: 12.5px; }
        .dynamic-table.tooloption-table td.cell-category {
          font-weight: 700;
          color: var(--penn-blue);
          background-color: var(--bg-subtle-blue);
          vertical-align: middle;
          white-space: normal;
        }
        .dynamic-table.tooloption-table td.cell-option-key { font-weight: 600; }
        /* Sel Category yang di-merge tidak ikut warna highlight baris pertamanya */
        .dynamic-table.tooloption-table tr td.cell-category {
          background-color: var(--bg-subtle-blue) !important;
          color: var(--penn-blue) !important;
          border-left: none !important;
        }
        /* Garis horizontal tebal di antara kategori (baris pertama tiap kategori: class group-start) */
        .dynamic-table.tooloption-table tr.group-start > td { border-top: var(--ft-thick-border); }

        /* --- Lebar & posisi kolom freeze: TABEL COMPARE ---
           (Single HW Option, Multi HW Option, Substitute, Assy Release Status: class "compare-table") */
        /* Kiri : kolom pertama (Single Option / Multi Option / Description / Category) 220px */
        .dynamic-table.compare-table .fl-1 { left: 0; width: 220px; min-width: 220px; max-width: 220px; }
        /* Kanan: MPX Result 120px + Engineer Check 130px + Remarks 240px
           Kalau lebar diubah: right .fr-2 = lebar Remarks, right .fr-3 = lebar Remarks + Engineer Check */
        .dynamic-table.compare-table .fr-3 { right: 370px; width: 120px; min-width: 120px; max-width: 120px; }
        .dynamic-table.compare-table .fr-2 { right: 240px; width: 130px; min-width: 130px; max-width: 130px; }
        .dynamic-table.compare-table .fr-1 { right: 0;     width: 240px; min-width: 240px; max-width: 240px; }
        /* Kolom nilai per model: tabel tetap full width, sisa ruang dibagi rata ke kolom-kolom ini */
        .dynamic-table.compare-table .col-value { min-width: 150px; }
        .dynamic-table.compare-table .col-region { width: 120px; min-width: 120px; }
        .dynamic-table.compare-table .col-part { min-width: 130px; }
        .dynamic-table.compare-table .col-status { min-width: 100px; }
        .dynamic-table.compare-table .col-level { min-width: 60px; }
        .dynamic-table.compare-table .col-qty { min-width: 60px; }
        .dynamic-table.compare-table .col-uit { min-width: 55px; }
        .dynamic-table.compare-table .col-supply { min-width: 120px; }
        /* Isi kolom perbandingan model rata tengah, kolom kiri tebal & sedikit lebih besar */
        .dynamic-table.compare-table td.col-value,
        .dynamic-table.compare-table td.col-region,
        .dynamic-table.compare-table td.col-part,
        .dynamic-table.compare-table td.col-status,
        .dynamic-table.compare-table td.col-level,
        .dynamic-table.compare-table td.col-qty,
        .dynamic-table.compare-table td.col-uit,
        .dynamic-table.compare-table td.col-supply { text-align: center; }
        .dynamic-table.compare-table td.cell-left-key { font-size: 12.5px; font-weight: 700; color: var(--penn-blue); }

        /* --- Switch besar Single / Multi di tab HW Option Compare --- */
        .section-subtabs.hw-option-switch {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-bottom: 4px;
        }
        .section-subtabs.hw-option-switch .hw-switch-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 14px;
          padding: 14px 20px;
          border: 2px solid var(--border-color);
          border-radius: 10px;
          background: var(--bg-card);
          color: var(--text-muted);
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .section-subtabs.hw-option-switch .hw-switch-btn:hover { border-color: var(--royal-blue); color: var(--royal-blue); }
        .section-subtabs.hw-option-switch .hw-switch-btn.active {
          border-color: var(--royal-blue);
          background: var(--bg-subtle-blue);
          color: var(--royal-blue);
          box-shadow: 0 3px 10px rgba(10, 36, 99, 0.15);
        }
        .hw-switch-btn .hw-switch-icon { font-size: 22px; }
        .hw-switch-btn .hw-switch-text { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; }
        .hw-switch-btn .hw-switch-title { font-size: 15px; font-weight: 800; }
        .hw-switch-btn .hw-switch-meta { font-size: 12px; font-weight: 600; color: var(--text-muted); }
        .hw-switch-btn .hw-switch-meta .meta-diff { color: var(--imperial-red); font-weight: 800; }

        /* Tanda bullet (●) di Single HW Option dibuat lebih besar supaya jelas beda dengan strip (-) */
        .dynamic-table .bullet-mark {
          display: inline-block;
          font-size: 18px;
          line-height: 1;
          color: var(--penn-blue);
        }

        /* Garis pemisah tombol filter Result dan tombol Level di toolbar Structure */
        .table-status-counters .toolbar-divider {
          display: inline-block;
          width: 1px;
          height: 22px;
          background-color: var(--border-color);
          margin: 0 4px;
          align-self: center;
        }


        /* ===== Revisi: badge MPX Result & baris nama model di header ===== */
        /* Badge MPX Result (semua tabel). Warna diatur lewat variabel --badge-* di :root */
        .mpx-result-badge {
          display: inline-block;
          min-width: 64px;
          padding: 4px 10px;
          border-radius: 6px;
          font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
          font-size: 11.5px;
          font-weight: 700;
          letter-spacing: 0.4px;
          line-height: 1.2;
          text-align: center;
          user-select: none;
        }
        .mpx-result-badge.mpx-ok   { background-color: var(--badge-ok-bg);    color: var(--badge-ok-text); }
        .mpx-result-badge.mpx-ng   { background-color: var(--badge-ng-bg);    color: var(--badge-ng-text); }
        .mpx-result-badge.mpx-diff { background-color: var(--badge-check-bg); color: var(--badge-check-text); }
        .mpx-result-badge.mpx-pass { background-color: var(--badge-pass-bg);  color: var(--badge-pass-text); }
        .dynamic-table td.status-column { text-align: center; }

        .dynamic-table th.model-name-th {
          background-color: var(--bg-subtle-blue);
          color: var(--penn-blue);
          font-weight: 800;
          text-align: center;
          text-transform: none;
        }

        .workspace-side-col {
          width: 320px;
          flex-shrink: 0;
          position: sticky;
          top: 20px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .workspace-side-col.sidebar-hidden { display: none !important; }

        .action-center-card {
          background: var(--bg-card);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0, 4, 58, 0.05);
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .ac-model-title-container {
          background: var(--penn-blue);
          border-left: 4px solid var(--imperial-red);
          border-radius: 6px;
          padding: 10px 14px;
          color: #FFFFFF;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .ac-model-title { font-size: 14px; font-weight: 800; }

        .sidebar-close-toggle-btn {
          background: transparent;
          border: none;
          color: #FFFFFF;
          cursor: pointer;
          font-size: 14px;
        }

        .stat-pill {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          padding: 6px 10px;
          border-radius: 6px;
          font-size: 11px;
          font-weight: 700;
          flex: 1;
        }

        .stat-pill.pill-ng { background: var(--bg-subtle-red); color: var(--imperial-red); border: 1px solid rgba(251, 54, 64, 0.2); }
        .stat-pill.pill-check { background: var(--bg-subtle-amber); color: #92400e; border: 1px solid #fde68a; }
        .stat-pill.pill-ok { background: #e6f4ea; color: #137333; border: 1px solid #a7f3d0; }

        .attention-list { display: flex; flex-direction: column; gap: 8px; }
        .attention-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: var(--bg-canvas);
          padding: 8px 10px;
          border-radius: 6px;
          border: 1px solid var(--border-color);
          font-size: 11px;
        }

        .review-jump-btn {
          background: var(--royal-blue);
          color: #ffffff;
          border: none;
          padding: 3px 8px;
          border-radius: 4px;
          font-size: 10px;
          font-weight: 600;
          cursor: pointer;
        }

        .review-jump-btn:hover { background: var(--imperial-red); }

        .show-model-profile-btn {
          display: none;
          align-items: center;
          gap: 8px;
          background-color: var(--penn-blue);
          color: #FFFFFF;
          border: 1px solid var(--royal-blue);
          border-radius: 6px;
          padding: 6px 12px;
          font-size: 11px;
          font-weight: 700;
          cursor: pointer;
        }

        .show-model-profile-btn.show { display: inline-flex; }

        .btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border-radius: 6px;
          font-size: 11px;
          font-weight: 600;
          cursor: pointer;
          border: none;
          transition: all 0.2s ease;
        }

        .btn-secondary { background-color: var(--bg-card); color: var(--penn-blue); border: 1px solid var(--border-color); }
        .btn-secondary:hover { background-color: var(--bg-subtle-blue); }
        .btn-dark { background-color: var(--penn-blue); color: #ffffff; }
        .btn-dark:hover { background-color: var(--imperial-red); }

        /* Tombol akhir Engineer Confirm: hijau solid, lebih menonjol dari tombol lain */
        .btn-confirm {
          background-color: #16A34A;
          color: #ffffff;
          border: 1px solid #15803D;
          font-weight: 800;
          padding-left: 16px;
          padding-right: 16px;
          box-shadow: 0 2px 6px rgba(22, 163, 74, 0.35);
        }
        .btn-confirm:hover { background-color: #15803D; }
        .btn-confirm:disabled { cursor: default; opacity: 0.9; }
        .btn-confirm.confirmed { background-color: #DCFCE7; color: #166534; border-color: #86EFAC; box-shadow: none; }

        /* Textarea remark akhir di modal Save Draft / Engineer Confirm */
        .final-remark-input {
          width: 100%;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          padding: 8px 10px;
          font-family: inherit;
          font-size: 12px;
          resize: vertical;
          outline: none;
        }
        .final-remark-input:focus { border-color: var(--royal-blue); }
        .final-remark-input.input-required { border-color: var(--imperial-red); background-color: var(--bg-subtle-red); }

        .toggle-switch { position: relative; display: inline-block; width: 32px; height: 16px; }
        .toggle-switch input { opacity: 0; width: 0; height: 0; }
        .slider {
          position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
          background-color: #cbd5e1; transition: .3s; border-radius: 16px;
        }
        .slider:before {
          position: absolute; content: ""; height: 10px; width: 10px; left: 3px; bottom: 3px;
          background-color: white; transition: .3s; border-radius: 50%;
        }
        input:checked + .slider { background-color: var(--imperial-red); }
        input:checked + .slider:before { transform: translateX(16px); }

        .section-block { display: none; flex-direction: column; gap: 12px; }
        .section-block.active-tab-panel { display: flex; }
        .section-title { font-size: 14px; font-weight: 700; color: var(--penn-blue); }

        .section-subtabs { display: flex; gap: 6px; margin-bottom: 8px; flex-wrap: wrap; }
        .section-subtab {
          border: 1px solid var(--border-color);
          background: var(--bg-card);
          color: var(--penn-blue);
          border-radius: 4px;
          padding: 4px 10px;
          font-size: 11px;
          font-weight: 600;
          cursor: pointer;
        }
        .section-subtab.active { background: var(--imperial-red); color: #ffffff; border-color: var(--imperial-red); }
        .section-subtab-panel { display: none; }
        .section-subtab-panel.active { display: block; }

        .section-info-container {
          background-color: var(--bg-subtle-blue);
          border: 1px solid var(--border-color);
          border-radius: 6px;
          padding: 8px 12px;
          display: flex;
          flex-wrap: wrap;
          gap: 8px 16px;
        }

        .info-item-chip { display: flex; align-items: center; gap: 6px; font-size: 11px; }
        .info-chip-label { font-weight: 700; color: var(--penn-blue); }
        .info-chip-value { font-weight: 600; color: var(--text-main); background-color: var(--bg-card); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border-color); }

        .draft-modal-overlay {
          display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
          background-color: rgba(0, 4, 58, 0.4); z-index: 20000; justify-content: center; align-items: center;
        }
        .draft-modal-overlay.show { display: flex; }
        .draft-modal-card {
          background: var(--bg-card); padding: 20px; border-radius: 8px; width: 440px; max-width: calc(100vw - 32px);
          border: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 14px;
        }

        .result-select {
          border: 1px solid var(--border-color); border-radius: 4px; padding: 2px 4px;
          font-size: 11px; font-weight: 700; outline: none; cursor: pointer;
        }
        .result-select.res-ok { background-color: #e6f4ea; color: #137333; }
        .result-select.res-check { background-color: var(--bg-subtle-amber); color: #92400e; }
        .result-select.res-ng { background-color: var(--bg-subtle-red); color: var(--imperial-red); }

        .engineer-confirm-select {
          border: 1px solid var(--border-color); border-radius: 4px; padding: 2px 4px;
          font-size: 11px; font-weight: 700; outline: none; cursor: pointer;
        }
        .engineer-confirm-select.eng-uncheck { background-color: #f1f5f9; color: var(--text-muted); }
        .engineer-confirm-select.eng-ok { background-color: #e6f4ea; color: #137333; }
        .engineer-confirm-select.eng-ng { background-color: var(--bg-subtle-red); color: var(--imperial-red); }

        /* Label mode halaman di header: Edit Mode (pemilik BOM / user khusus) atau View Only */
        .access-mode-pill {
          display: inline-flex; align-items: center; gap: 6px;
          padding: 3px 10px; border-radius: 999px;
          font-size: 11px; font-weight: 700; white-space: nowrap; border: 1px solid;
        }
        .access-mode-pill.access-edit { background-color: #DCFCE7; color: #166534; border-color: #86EFAC; }
        .access-mode-pill.access-view { background-color: #F1F5F9; color: #475569; border-color: #CBD5E1; }

        /* Mode View Only: Engineer Check & Remarks tampil seperti teks biasa, tidak bisa diubah */
        .view-only-mode .engineer-confirm-select:disabled,
        .view-only-mode .result-select:disabled {
          appearance: none; -webkit-appearance: none; -moz-appearance: none;
          background-image: none; opacity: 1; cursor: default; pointer-events: none;
          text-align: center; text-align-last: center;
        }
        .view-only-mode .remark-input[readonly] {
          border-color: transparent; background-color: transparent; box-shadow: none; cursor: default;
        }

        /* Engineer Check read-only (Not Dropdownable): nilai otomatis dari PRM check, tidak bisa diubah */
        .engineer-check-readonly {
          display: inline-block;
          width: 100%;
          padding: 3px 6px;
          border: 1px solid transparent;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 700;
          text-align: center;
          cursor: not-allowed;
          user-select: none;
        }
        .engineer-check-readonly.eng-uncheck { background-color: #f1f5f9; color: var(--text-muted); }
        .engineer-check-readonly.eng-ok { background-color: #e6f4ea; color: #137333; }
        .engineer-check-readonly.eng-ng { background-color: var(--bg-subtle-red); color: var(--imperial-red); }

        .remark-input {
          width: 100%;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          padding: 4px 8px;
          font-size: 11px;
          outline: none;
          min-width: 200px;
          background-color: #ffffff !important;
          color: var(--text-main) !important;
        }

        .remark-input.input-required {
          border-color: var(--imperial-red) !important;
          background-color: var(--bg-subtle-red) !important;
        }

        .dynamic-table td.cell-highlight-red-red {
          background-color: #FEE2E2 !important;
          color: #DC2626 !important;
          font-weight: 800 !important;
          border: 1px solid #EF4444 !important;
        }
      `}} />

      {/* Global Loading Overlay */}
      <div id="global-loading-overlay" className="global-loading-overlay show">
        <div className="loading-spinner"></div>
        <div className="loading-text">Loading MPX Crosschecking Workspace</div>
        <div className="loading-subtext">Fetching data from API, please wait...</div>
      </div>

      {/* Modal Save Draft / Engineer Confirm: user mengisi remark akhir, lalu semua Engineer Check & Remarks dikirim */}
      <div className="draft-modal-overlay" id="draftModalOverlay">
        <div className="draft-modal-card">
          <div className="draft-modal-header" style={{ fontWeight: 800, fontSize: '14px' }}>
            <i className="fa-solid fa-floppy-disk"></i> <span id="draftModalTitleText">Save Draft</span>
          </div>
          <div className="draft-modal-body" id="draftModalDesc" style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Enter your final remark. All Engineer Check values and Remarks in every table will be saved as a draft.
          </div>
          <textarea id="draftFinalRemark" className="final-remark-input" rows={4} placeholder="Final remark (required)..."></textarea>
          <div className="draft-modal-actions" style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary" onClick={() => (window as any).closeSaveDraftModal()}>Cancel</button>
            <button className="btn btn-dark" id="draftModalSubmitBtn" onClick={() => (window as any).confirmSaveDraft()}>
              <i className="fa-solid fa-paper-plane"></i> <span id="draftModalSubmitText">Save Draft</span>
            </button>
          </div>
        </div>
      </div>

      {/* HEADER BLOCK WITH MODEL NAME & REVISION BELOW TITLE */}
      <header className="header-top-block">
        <div className="header-row-main">
          <div className="header-title-group">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <button
                onClick={() => {
                  if (typeof window !== 'undefined' && window.opener) window.close();
                  else router.push('/');
                }}
                className="btn btn-secondary"
                title="Go Back to Main Dashboard"
              >
                <i className="fa-solid fa-arrow-left"></i> Back
              </button>
              <h1 className="workspace-main-title">
                <i className="fa-solid fa-layer-group" style={{ color: 'var(--imperial-red)' }}></i> MPX Crosschecking Workspace
              </h1>
            </div>

            <div className="model-header-subrow">
              <span className="model-name-badge" id="headerModelName">Model Name</span>
              <span className="revision-pill" id="revisionValue">Rev 1.0</span>
              {canEdit ? (
                <span className="access-mode-pill access-edit" title={`Signed in as ${userName ?? '-'}. You can edit this crosscheck result.`}>
                  <i className="fa-solid fa-pen-to-square"></i> Edit Mode
                </span>
              ) : (
                <span className="access-mode-pill access-view" title="Only the BOM owner (PIC Circuit) can edit Engineer Check and Remarks.">
                  <i className="fa-solid fa-eye"></i> View Only
                </span>
              )}
              <div className="progress-indicator-box">
                <i className="fa-solid fa-list-check" style={{ color: 'var(--imperial-red)' }}></i>
                <span>Progress:</span>
                <span id="progressText">(0/0 reviewed)</span>
                <div className="progress-bar-track">
                  <div className="progress-bar-fill" id="progressBarFill"></div>
                </div>
                <span id="progressPct" style={{ color: 'var(--imperial-red)' }}>0%</span>
              </div>
            </div>
          </div>

          <div className="header-widget-group">
            {canEdit && (
              <button className="btn btn-secondary" onClick={() => (window as any).openSaveDraftModal('draft')}>
                <i className="fa-solid fa-floppy-disk"></i> Save Draft
              </button>
            )}

            <div className="deliverables-dropdown">
              <button className="btn btn-secondary">
                <i className="fa-solid fa-download"></i> Deliverables <i className="fa-solid fa-chevron-down" style={{ fontSize: '9px' }}></i>
              </button>
              <div className="deliverables-dropdown-content">
                <button onClick={() => (window as any).downloadDeliverable('json')}><i className="fa-solid fa-file-code"></i> Export JSON Data</button>
                <button onClick={() => (window as any).downloadDeliverable('csv')}><i className="fa-solid fa-file-csv"></i> Export CSV Table</button>
                <button onClick={() => (window as any).downloadDeliverable('xlsx')}><i className="fa-solid fa-file-excel"></i> Export Excel Report</button>
              </div>
            </div>

            {/* Tombol akhir: menyelesaikan crosscheck (validasi semua baris NG/Different, lalu minta remark akhir) */}
            {canEdit && (
              <button className="btn btn-confirm" id="engineerConfirmBtn" onClick={() => (window as any).engineerConfirm()}
                title="Finish the crosscheck: all NG/Different rows must have Engineer Check and remarks">
                <i className="fa-solid fa-user-check"></i> Engineer Confirm
              </button>
            )}

            <button className="show-model-profile-btn" id="showModelProfileBtn" onClick={() => (window as any).showRightSidebar()}>
              <i className="fa-solid fa-gauge-high"></i> Show Summary
            </button>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT AREA */}
      <main className={`main-container${canEdit ? '' : ' view-only-mode'}`}>

        <div className="guided-navigator-bar">
          <div className="guided-nav-title">
            <i className="fa-solid fa-compass" style={{ color: 'var(--imperial-red)' }}></i>
            Guided Module Review Navigator
          </div>
          <div className="guided-nav-actions">
            <button className="show-summary-nav-btn" onClick={() => (window as any).toggleRightSidebar()}>
              <i className="fa-solid fa-id-card"></i> Model Profile & Module Results List
            </button>

            <div className="show-tab-dropdown">
              <button className="btn btn-secondary">
                <i className="fa-solid fa-eye"></i> Show Tab <span id="hiddenTabsBadgeCount" style={{ background: 'var(--imperial-red)', color: '#FFF', borderRadius: '50%', padding: '1px 5px', fontSize: '9px' }}></span> <i className="fa-solid fa-chevron-down" style={{ fontSize: '9px' }}></i>
              </button>
              <div className="show-tab-dropdown-content" id="showTabDropdownList">
                <div style={{ padding: '8px 12px', fontSize: '11px', color: 'var(--text-muted)' }}>All tabs are currently visible</div>
              </div>
            </div>

            {canEdit && (
              <button className="resolve-issue-btn" onClick={() => (window as any).resolveNextIssue()}>
                <i className="fa-solid fa-bolt"></i> Resolve Next Issue
              </button>
            )}
          </div>
        </div>

        <div className="workspace-split-layout">

          <div className="workspace-main-col">

            <div className="chrome-tabs-container">
              <div className="chrome-tabs-bar">
                {/* Urutan & tab default harus sama dengan MODULES di atas. Tab tersembunyi dibuka lewat "Show Tab" */}
                <a href="#sec-structure" className="tab-item active" id="tab-nav-structure">
                  <i className="fa-solid fa-sitemap"></i> <span className="tab-title">Structure &amp; Operation Plan Check</span>
                  <span className="tab-close-icon" title="Close Tab" onClick={(e) => (window as any).closeTab(e, 'tab-nav-structure')}>×</span>
                </a>
                <a href="#sec-ben-compare" className="tab-item" id="tab-nav-ben-compare">
                  <i className="fa-solid fa-code-compare"></i> <span className="tab-title">Tool Option Compare</span>
                  <span className="tab-close-icon" title="Close Tab" onClick={(e) => (window as any).closeTab(e, 'tab-nav-ben-compare')}>×</span>
                </a>
                <a href="#sec-hw-option" className="tab-item" id="tab-nav-hw-option">
                  <i className="fa-solid fa-sliders"></i> <span className="tab-title">HW Option Compare</span>
                  <span className="tab-close-icon" title="Close Tab" onClick={(e) => (window as any).closeTab(e, 'tab-nav-hw-option')}>×</span>
                </a>
                <a href="#sec-substitute-check" className="tab-item" id="tab-nav-substitute-check">
                  <i className="fa-solid fa-rotate"></i> <span className="tab-title">Substitute Compare</span>
                  <span className="tab-close-icon" title="Close Tab" onClick={(e) => (window as any).closeTab(e, 'tab-nav-substitute-check')}>×</span>
                </a>
                <a href="#sec-assy-release-status" className="tab-item" id="tab-nav-assy-release-status">
                  <i className="fa-solid fa-clipboard-list"></i> <span className="tab-title">Assy Release Status Compare</span>
                  <span className="tab-close-icon" title="Close Tab" onClick={(e) => (window as any).closeTab(e, 'tab-nav-assy-release-status')}>×</span>
                </a>
                <a href="#sec-operation-plan-check" className="tab-item" id="tab-nav-operation-plan-check" style={{ display: 'none' }}>
                  <i className="fa-solid fa-calendar-check"></i> <span className="tab-title">Operation Plan Check</span>
                  <span className="tab-close-icon" title="Close Tab" onClick={(e) => (window as any).closeTab(e, 'tab-nav-operation-plan-check')}>×</span>
                </a>
                <a href="#sec-eax-substitute-check" className="tab-item" id="tab-nav-eax-substitute-check" style={{ display: 'none' }}>
                  <i className="fa-solid fa-microchip"></i> <span className="tab-title">EAX Substitute Check</span>
                  <span className="tab-close-icon" title="Close Tab" onClick={(e) => (window as any).closeTab(e, 'tab-nav-eax-substitute-check')}>×</span>
                </a>
                <a href="#sec-check-part" className="tab-item" id="tab-nav-check-part" style={{ display: 'none' }}>
                  <i className="fa-solid fa-check-double"></i> <span className="tab-title">Check Part</span>
                  <span className="tab-close-icon" title="Close Tab" onClick={(e) => (window as any).closeTab(e, 'tab-nav-check-part')}>×</span>
                </a>
                <a href="#sec-crosschecking-result" className="tab-item" id="tab-nav-crosschecking-result" style={{ display: 'none' }}>
                  <i className="fa-solid fa-clipboard-check"></i> <span className="tab-title">Crosschecking Result</span>
                  <span className="tab-close-icon" title="Close Tab" onClick={(e) => (window as any).closeTab(e, 'tab-nav-crosschecking-result')}>×</span>
                </a>
              </div>
            </div>

            {/* SECTION 1: Structure */}
            <section id="sec-structure" className="section-block active-tab-panel">
              <div className="section-info-container" style={{ marginTop: '12px' }}>
                <div className="info-item-chip"><span className="info-chip-label">Plant Name:</span><span className="info-chip-value" id="info-struct-plant-name">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Suffix Name:</span><span className="info-chip-value" id="info-struct-suffix-name">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Plant Suffix:</span><span className="info-chip-value" id="info-struct-plant-suffix">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Editor:</span><span className="info-chip-value" id="info-struct-editor">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Creator:</span><span className="info-chip-value" id="info-struct-creator">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Edited Date:</span><span className="info-chip-value" id="info-struct-edited-date">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Plant Code:</span><span className="info-chip-value" id="info-struct-plant-code">-</span></div>
              </div>
              <div className="table-container" id="container-structure">
                <div className="empty-state">No data loaded yet.</div>
              </div>
            </section>

            {/* SECTION 2: Tool Option */}
            <section id="sec-ben-compare" className="section-block">
              <div className="section-info-container" style={{ marginTop: '12px' }}>
                <div className="info-item-chip"><span className="info-chip-label">Model Name:</span><span className="info-chip-value" id="info-ben-model-name">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Dev Model:</span><span className="info-chip-value" id="info-ben-dev-model">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Init Model:</span><span className="info-chip-value" id="info-ben-init-model">-</span></div>
              </div>
              <div id="ben-compare-tool" className="section-subtab-panel active">
                <div className="table-container" id="container-ben-compare-tool"><div className="empty-state">No data loaded yet.</div></div>
              </div>
            </section>

            {/* SECTION 3a: Assy Release Status (dulu sub-tabel HW Part Status di tab Substitute) */}
            <section id="sec-assy-release-status" className="section-block">
              <div className="table-container" id="container-assy-release-status" style={{ marginTop: '12px' }}>
                <div className="empty-state">No data loaded yet.</div>
              </div>
            </section>

            {/* SECTION 3b: Substitute */}
            <section id="sec-substitute-check" className="section-block">
              <div className="table-container" id="container-substitute-comp-data" style={{ marginTop: '12px' }}>
                <div className="empty-state">No data loaded yet.</div>
              </div>
            </section>

            {/* SECTION 4: HW Option Compare (Single & Multi, dipilih lewat switch besar di atas tabel) */}
            <section id="sec-hw-option" className="section-block">
              {/* Switch Single / Multi: memakai mekanisme .section-subtabs (data-target = id panel) */}
              <div className="section-subtabs hw-option-switch" style={{ marginTop: '12px' }}>
                <button className="section-subtab hw-switch-btn active" data-target="hw-option-single">
                  <i className="fa-solid fa-toggle-on hw-switch-icon"></i>
                  <span className="hw-switch-text">
                    <span className="hw-switch-title">Single HW Option</span>
                    <span className="hw-switch-meta" id="hw-switch-single-meta">-</span>
                  </span>
                </button>
                <button className="section-subtab hw-switch-btn" data-target="hw-option-multi">
                  <i className="fa-solid fa-sliders hw-switch-icon"></i>
                  <span className="hw-switch-text">
                    <span className="hw-switch-title">Multi HW Option</span>
                    <span className="hw-switch-meta" id="hw-switch-multi-meta">-</span>
                  </span>
                </button>
              </div>
              <div id="hw-option-single" className="section-subtab-panel active">
                <div className="table-container" id="container-single-hw-option">
                  <div className="empty-state">No data loaded yet.</div>
                </div>
              </div>
              <div id="hw-option-multi" className="section-subtab-panel">
                <div className="table-container" id="container-multi-option-multi">
                  <div className="empty-state">No data loaded yet.</div>
                </div>
              </div>
            </section>

            {/* SECTION 5: EAX Substitute Check */}
            <section id="sec-eax-substitute-check" className="section-block">
              <div className="section-info-container" style={{ marginTop: '12px' }}>
                <div className="info-item-chip"><span className="info-chip-label">EAX Part Number:</span><span className="info-chip-value" id="info-eax-part-no">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">EBR Part Number:</span><span className="info-chip-value" id="info-ebr-part-no">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">EBR Main Part Number:</span><span className="info-chip-value" id="info-ebr-main-part-no">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">EBT Part Number:</span><span className="info-chip-value" id="info-ebt-part-no">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Chassis Name:</span><span className="info-chip-value" id="info-chassis-name">-</span></div>
              </div>
              <div className="table-container" id="container-eax-substitute-check"><div className="empty-state">No data loaded yet.</div></div>
            </section>

            {/* SECTION 6: Operation Plan Check */}
            <section id="sec-operation-plan-check" className="section-block">
              <div className="section-info-container" style={{ marginTop: '12px' }}>
                <div className="info-item-chip"><span className="info-chip-label">Database Name:</span><span className="info-chip-value" id="info-op-db-name">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Database Version:</span><span className="info-chip-value" id="info-op-db-version">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Database Date:</span><span className="info-chip-value" id="info-op-db-date">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Database Year:</span><span className="info-chip-value" id="info-op-db-year">-</span></div>
              </div>
              <div className="table-container" id="container-operation-plan-check"><div className="empty-state">No data loaded yet.</div></div>
            </section>

            {/* SECTION 7: CHECK PART TAB */}
            <section id="sec-check-part" className="section-block">
              <div className="section-info-container" style={{ marginTop: '12px' }}>
                <div className="info-item-chip"><span className="info-chip-label">Model Name:</span><span className="info-chip-value" id="info-check-part-model-name">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Dev Model:</span><span className="info-chip-value" id="info-check-part-dev-model">-</span></div>
                <div className="info-item-chip"><span className="info-chip-label">Init Model:</span><span className="info-chip-value" id="info-check-part-init-model">-</span></div>
              </div>

              <div className="section-subtabs">
                <button className="section-subtab active" data-target="check-part-chassis">Chassis Assembly</button>
                <button className="section-subtab" data-target="check-part-op-plan">Operation Plan Section</button>
                <button className="section-subtab" data-target="check-part-eco">ECO List</button>
                <button className="section-subtab" data-target="check-part-hw-list">HW Part List</button>
                <button className="section-subtab" data-target="check-part-hw-profile"><i className="fa-solid fa-microchip"></i> HW Profile</button>
              </div>

              <div id="check-part-chassis" className="section-subtab-panel active">
                <div className="section-subtabs">
                  <button className="section-subtab active" data-target="check-part-ebt">EBT Section</button>
                  <button className="section-subtab" data-target="check-part-ebr">EBR Section</button>
                  <button className="section-subtab" data-target="check-part-ebu">EBU Section</button>
                  <button className="section-subtab" data-target="check-part-eax">EAX Section</button>
                </div>
                <div id="check-part-ebt" className="section-subtab-panel active"><div className="table-container" id="container-check-part-ebt"><div className="empty-state">No EBT section data.</div></div></div>
                <div id="check-part-ebr" className="section-subtab-panel"><div className="table-container" id="container-check-part-ebr"><div className="empty-state">No EBR section data.</div></div></div>
                <div id="check-part-ebu" className="section-subtab-panel"><div className="table-container" id="container-check-part-ebu"><div className="empty-state">No EBU section data.</div></div></div>
                <div id="check-part-eax" className="section-subtab-panel"><div className="table-container" id="container-check-part-eax"><div className="empty-state">No EAX section data.</div></div></div>
              </div>

              <div id="check-part-op-plan" className="section-subtab-panel">
                <div className="table-container" id="container-check-part-op-ref"><div className="empty-state">No Operation Plan reference data.</div></div>
              </div>

              <div id="check-part-eco" className="section-subtab-panel">
                <div className="table-container" id="container-check-part-eco-list"><div className="empty-state">No Affected Part List data.</div></div>
              </div>

              <div id="check-part-hw-list" className="section-subtab-panel">
                <div className="section-subtabs">
                  <button className="section-subtab active" data-target="check-part-hw-single">Single Part</button>
                  <button className="section-subtab" data-target="check-part-hw-dup">Duplicated Part</button>
                </div>
                <div id="check-part-hw-single" className="section-subtab-panel active"><div className="table-container" id="container-check-part-hw-single"><div className="empty-state">No Single HW Part data.</div></div></div>
                <div id="check-part-hw-dup" className="section-subtab-panel"><div className="table-container" id="container-check-part-hw-dup"><div className="empty-state">No Duplicated HW Part data.</div></div></div>
              </div>

              <div id="check-part-hw-profile" className="section-subtab-panel">
                <div className="profile-tabs-card" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '16px' }}>
                  <div className="profile-grid">
                    <div className="profile-row"><span>EAX Part No: </span><span id="chkHwEaxPartNo">-</span></div>
                    <div className="profile-row"><span>EBR Part No: </span><span id="chkHwEbrPartNo">-</span></div>
                    <div className="profile-row"><span>EBT Part No: </span><span id="chkHwEbtPartNo">-</span></div>
                  </div>
                  <div className="table-wrapper" id="container-chk-hw-eax-profile" style={{ marginTop: '12px' }}>
                    <div className="empty-state">No EAX profile data loaded.</div>
                  </div>
                </div>
              </div>
            </section>

            {/* SECTION 8: Crosschecking Result */}
            <section id="sec-crosschecking-result" className="section-block">
              <div className="table-container" id="container-crosschecking-result" style={{ marginTop: '12px' }}>
                <div className="empty-state">No data loaded yet.</div>
              </div>
            </section>

          </div>

         <aside className="workspace-side-col" id="workspaceRightSidebar">
            <div className="action-center-card">
              <div className="ac-model-title-container">
                <span className="ac-model-title" id="ac-model-title">CROSSCHECK SUMMARY</span>
                <button className="sidebar-close-toggle-btn" onClick={() => (window as any).hideRightSidebar()} title="Hide Summary">
                  <i className="fa-solid fa-xmark"></i>
                </button>
              </div>

              <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'center' }} onClick={() => (window as any).toggleInlineModelProfile()}>
                <i id="toggleInlineProfileIcon" className="fa-solid fa-chevron-down"></i> <span id="toggleInlineProfileText">Show Model Profile</span>
              </button>

              <div id="inlineModelProfileCard" style={{ display: 'none', fontSize: '11px', background: 'var(--bg-canvas)', padding: '10px', borderRadius: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 0' }}><span>Region</span><span id="profRegion">-</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 0' }}><span>Plant</span><span id="profPlant">-</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 0' }}><span>Chassis</span><span id="profChassis">-</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 0' }}><span>Board</span><span id="profBoard">-</span></div>
              </div>

              <div style={{ display: 'flex', gap: '6px' }}>
                <span className="stat-pill pill-ng"><i className="fa-solid fa-circle-xmark"></i> <span id="ac-total-ng">0</span> NG</span>
                <span className="stat-pill pill-check"><i className="fa-solid fa-triangle-exclamation"></i> <span id="ac-total-check">0</span> DIFFERENT</span>
                <span className="stat-pill pill-ok"><i className="fa-solid fa-circle-check"></i> <span id="ac-total-ok">0</span> OK</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
                <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--penn-blue)' }}>MODULE RESULTS LIST</span>
                <div className="attention-list" id="action-center-attention-list">
                  <div className="empty-state">Calculating process status...</div>
                </div>
              </div>
            </div>

          </aside>

        </div>
      </main>
    </>
  );
}