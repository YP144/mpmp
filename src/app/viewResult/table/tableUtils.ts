/**
 * Shared Table Utilities
 */

export function id(elemId: string): HTMLElement | null {
  return document.getElementById(elemId);
}

export function setText(elemId: string, text: string) {
  const el = id(elemId);
  if (el) el.textContent = text;
}

export function safeString(value: any): string {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'object') {
    try { return JSON.stringify(value); } catch (_) { return String(value); }
  }
  return String(value);
}

export function escapeHtml(value: any): string {
  return safeString(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function camelToTitle(str: string): string {
  return String(str)
    .replace(/[_-]+/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\s+/g, ' ')
    .replace(/^./, s => s.toUpperCase());
}

export function truncateTextToThreeWords(value: string): string {
  const text = safeString(value);
  if (!text) return '';
  const words = text.trim().split(/\s+/);
  if (words.length <= 3) return text;
  return words.slice(0, 3).join(' ') + '…';
}

export function formatRawJsonValue(val: any): string {
  if (val === undefined || val === null || val === '') return '-';
  if (typeof val === 'object') {
    try { return JSON.stringify(val); } catch (_) { return String(val); }
  }
  return String(val);
}

export function getPath(obj: any, path: string) {
  if (!obj) return undefined;
  return path.split('.').reduce((acc, key) => {
    if (acc === null || acc === undefined) return undefined;
    return acc[key];
  }, obj);
}

export function getFirstAvailablePath(obj: any, paths: string[]) {
  for (const path of paths) {
    const value = getPath(obj, path);
    if (value !== undefined && value !== null) return value;
  }
  return undefined;
}

export function normalizeTableRows(value: any): any[] {
  if (Array.isArray(value)) return value;
  if (value && typeof value === 'object') {
    if (Array.isArray(value.operation_data)) return value.operation_data;
    if (Array.isArray(value.OperationCheck)) return value.OperationCheck;
    if (Array.isArray(value.compData)) return value.compData;
    if (Array.isArray(value.compareData)) return value.compareData;
    if (Array.isArray(value.data)) return value.data;
    const values = Object.values(value);
    if (values.length > 0 && typeof values[0] === 'object' && values[0] !== null && !Array.isArray(values[0])) {
      return values;
    }
  }
  return [];
}

export function collectKeys(rows: any[], excludedKeys?: Set<string>): string[] {
  if (!Array.isArray(rows)) return [];
  const keys: string[] = [];
  const seen = new Set<string>();

  // 1. Buat daftar perbandingan yang sudah dinormalkan (huruf kecil & tanpa spasi/simbol)
  const normalizedExcluded = new Set<string>();
  if (excludedKeys) {
    excludedKeys.forEach(k => {
      const lower = k.trim().toLowerCase();
      normalizedExcluded.add(lower);
      normalizedExcluded.add(lower.replace(/[\s_-]+/g, ''));
    });
  }

  // 2. Filter setiap key dari baris data
  rows.forEach(row => {
    if (!row || typeof row !== 'object' || Array.isArray(row)) return;
    Object.keys(row).forEach(key => {
      const lower = key.trim().toLowerCase();
      const norm = lower.replace(/[\s_-]+/g, '');

      // Jika kolom ini ada di daftar exclude (baik huruf besar/kecil/spasi/underscore), lewati!
      if (normalizedExcluded.has(lower) || normalizedExcluded.has(norm)) {
        return;
      }

      if (!seen.has(key)) {
        seen.add(key);
        keys.push(key);
      }
    });
  });

  return keys;
}


/* ======================================================================
 * REVISI: Header model (banner), MPX Result, Engineer Check
 * Dipakai oleh semua file render*Table.ts
 * ====================================================================== */

export type ModelGroup = 'initial' | 'development' | 'target';

export interface HeaderColumn {
  label: string;      // teks kolom (baris header paling bawah)
  key?: string;       // key data di baris JSON (kalau kolom ini mengambil data)
  groupKey?: string;  // kolom bersebelahan dengan groupKey sama digabung di banner
  className?: string;
}

export interface HeaderGroup {
  title: string;      // baris 1 (banner): "Initial Model", "Target Model", ...
  subtitle: string;   // baris 2: nama model TV
  className?: string;
}

export function getModelHeaderGroups(data: any): Record<ModelGroup, HeaderGroup> {
  return {
    initial:     { title: 'Initial Model',     subtitle: safeString(data?.initName ?? data?.initialModel ?? '-'), className: 'model-banner-init' },
    development: { title: 'Development Model', subtitle: safeString(data?.devName ?? data?.devModel ?? '-'),     className: 'model-banner-dev' },
    target:      { title: 'Target Model',      subtitle: safeString(data?.targetName ?? data?.mpModel ?? '-'),   className: 'model-banner-target' },
  };
}

/**
 * Menebak kolom milik model mana dari nama key-nya.
 * Contoh: "Initial" -> initial, "Part_Init" -> initial (label "Part"),
 *         "Status_Dev" -> development (label "Status"), "Subs_Target" -> target (label "Subs")
 */
export function detectModelGroup(key: string): { group: ModelGroup; label: string } | null {
  const patterns: [ModelGroup, RegExp][] = [
    ['initial',     /^(?:(.*?)[\s_-]+)?(initial|init)$/i],
    ['development', /^(?:(.*?)[\s_-]+)?(development|dev)$/i],
    ['target',      /^(?:(.*?)[\s_-]+)?(target)$/i],
  ];
  for (const [group, re] of patterns) {
    const m = String(key).trim().match(re);
    if (m) return { group, label: camelToTitle(m[1] || key) };
  }
  return null;
}

/**
 * Membuat <thead> bertingkat:
 *   baris 1 = judul grup (Initial Model / Development Model / Target Model)
 *   baris 2 = nama model TV
 *   baris 3 = nama kolom (hanya muncul kalau ada grup berisi lebih dari 1 kolom)
 * Kolom tanpa grup memakai rowspan penuh.
 */
export function buildGroupedHeader(columns: HeaderColumn[], groups: Record<string, HeaderGroup>): string {
  const segments: { group?: HeaderGroup; cols: HeaderColumn[] }[] = [];
  columns.forEach(col => {
    const group = col.groupKey ? groups[col.groupKey] : undefined;
    const last = segments[segments.length - 1];
    if (group && last && last.group === group) last.cols.push(col);
    else segments.push({ group, cols: [col] });
  });

  if (!segments.some(s => s.group)) {
    return `<tr>${columns.map(c => `<th class="${c.className ?? ''}">${escapeHtml(c.label)}</th>`).join('')}</tr>`;
  }

  const needLabelRow = segments.some(s => s.group && s.cols.length > 1);
  const totalRows = needLabelRow ? 3 : 2;
  let row1 = '';
  let row2 = '';
  let row3 = '';

  segments.forEach(seg => {
    if (!seg.group) {
      seg.cols.forEach(c => {
        row1 += `<th class="model-banner-th ${c.className ?? ''}" rowspan="${totalRows}">${escapeHtml(c.label)}</th>`;
      });
      return;
    }
    const span = seg.cols.length;
    const nameRowspan = needLabelRow && span === 1 ? 2 : 1;
    row1 += `<th class="model-banner-th ${seg.group.className ?? ''}" colspan="${span}">${escapeHtml(seg.group.title)}</th>`;
    row2 += `<th class="model-name-th" colspan="${span}" rowspan="${nameRowspan}">${escapeHtml(seg.group.subtitle)}</th>`;
    if (needLabelRow && span > 1) {
      seg.cols.forEach(c => { row3 += `<th class="${c.className ?? ''}">${escapeHtml(c.label)}</th>`; });
    }
  });

  return `<tr class="model-banner-row">${row1}</tr><tr>${row2}</tr>${needLabelRow ? `<tr>${row3}</tr>` : ''}`;
}

/** Tabel umum: hasil hanya OK / NG / DIFFERENT (CHECK & REVIEW -> DIFFERENT) */
export function normalizeMpxResult(raw: any): 'OK' | 'NG' | 'DIFFERENT' {
  const v = safeString(raw).trim().toUpperCase();
  if (v === 'NG' || v === 'FAIL' || v === '1') return 'NG';
  if (v === 'DIFFERENT' || v === 'CHECK' || v === 'REVIEW' || v === 'NEED HW OPTION') return 'DIFFERENT';
  return 'OK';
}

/** Tabel perbandingan (Tool Option, Substitute, HW Option): hanya SAME / DIFFERENT */
export function normalizeSameDifferent(raw: any): 'SAME' | 'DIFFERENT' {
  const v = safeString(raw).trim().toUpperCase();
  return (v === 'SAME' || v === 'OK' || v === 'PASS' || v === '0' || v === '-') ? 'SAME' : 'DIFFERENT';
}

/**
 * Sel "MPX Result": badge teks saja (tidak bisa diubah user).
 * Warna: samediff (2 hasil) -> SAME hijau, DIFFERENT merah
 *        okng (3 hasil)     -> OK hijau, DIFFERENT kuning, NG merah
 */
export function renderMpxResultCell(result: string, mode: 'okng' | 'samediff' = 'okng', className = ''): string {
  const cls = (result === 'OK' || result === 'SAME') ? 'mpx-ok'
    : (result === 'NG' || mode === 'samediff') ? 'mpx-ng'
    : 'mpx-diff';
  return `<td class="status-column ${className}"><span class="mpx-result-badge ${cls}">${escapeHtml(result)}</span></td>`;
}

/** Sel "Engineer Check": default tampil Uncheck (tidak muncul di menu), user hanya bisa pilih OK / NG */
export function renderEngineerConfirmCell(rawValue: any, className = ''): string {
  const v = safeString(rawValue).trim().toUpperCase();
  const val = v === 'OK' ? 'OK' : v === 'NG' ? 'NG' : 'Uncheck';
  const cls = val === 'OK' ? 'eng-ok' : val === 'NG' ? 'eng-ng' : 'eng-uncheck';
  return `
    <td class="engineer-confirm-column ${className}">
      <select class="engineer-confirm-select ${cls}" onchange="window.updateEngineerConfirmStyle(this)">
        ${val === 'Uncheck' ? '<option value="Uncheck" disabled selected hidden>Uncheck</option>' : ''}
        <option value="OK" ${val === 'OK' ? 'selected' : ''}>OK</option>
        <option value="NG" ${val === 'NG' ? 'selected' : ''}>NG</option>
      </select>
    </td>`;
}

/** Sel "Remarks": input teks yang bisa diisi user */
export function renderRemarkCell(rawValue: any, className = ''): string {
  const v = safeString(rawValue ?? '');
  const value = v === '-' ? '' : v;
  return `
    <td class="${className}">
      <input type="text" class="remark-input" value="${escapeHtml(value)}" placeholder="Enter detail..." oninput="this.setAttribute('value', this.value); this.classList.remove('input-required'); window.updateTableStatusCounters(this.closest('.table-card')); window.updateProgressMetrics();">
    </td>`;
}

/**
 * Sel data biasa (teks dipotong 3 kata, teks lengkap di tooltip). bold = tebal + ikon caret.
 * className opsional, mis. untuk kolom freeze / border tebal
 */
export function renderDataCell(value: any, bold = false, className = ''): string {
  const text = safeString(value === undefined || value === null || value === '' ? '-' : value);
  const inner = `<span class="static-cell-text" title="${escapeHtml(text)}">${escapeHtml(truncateTextToThreeWords(text))}</span>`;
  const cls = className ? ` class="${className}"` : '';
  if (!bold) return `<td${cls}>${inner}</td>`;
  return `<td${cls} style="font-weight: 700;"><div class="cell-product"><i class="fa-solid fa-caret-right" style="font-size:10px; color:var(--imperial-red);"></i>${inner}</div></td>`;
}

/** Tombol filter di toolbar tabel */
export function renderFilterButtons(opts: {
  mode: 'okng' | 'samediff';
  withUncheck?: boolean;
  extraButtons?: string;
  activeAll?: boolean;
}): string {
  const { mode, withUncheck = true, extraButtons = '', activeAll = true } = opts;
  const ngButton = mode === 'okng'
    ? `<button class="table-status-counter counter-ng" onclick="window.filterTableRows(this, 'NG')"><i class="fa-solid fa-circle-xmark"></i> Show NG <strong class="counter-ng-value">0</strong></button>`
    : '';
  const uncheckButton = withUncheck
    ? `<button class="table-status-counter counter-uncheck" onclick="window.filterTableRows(this, 'UNCHECK')"><i class="fa-solid fa-square-minus"></i> Show Uncheck</button>`
    : '';
  return `
    <div class="table-status-counters">
      ${ngButton}
      <button class="table-status-counter ${mode === 'samediff' ? 'counter-ng' : 'counter-check'}" onclick="window.filterTableRows(this, 'DIFFERENT')"><i class="fa-solid fa-not-equal"></i> Show Differences <strong class="counter-diff-value">0</strong></button>
      ${extraButtons}
      ${uncheckButton}
      <button class="table-status-counter counter-ok" onclick="window.filterTableRows(this, 'OK')"><i class="fa-solid fa-circle-check"></i> ${mode === 'samediff' ? 'Show Same' : 'Show OK'}</button>
      <button class="table-status-counter counter-all ${activeAll ? 'active-filter' : ''}" onclick="window.filterTableRows(this, 'ALL')">Show All</button>
    </div>`;
}

/**
 * Kerangka kartu tabel: toolbar + table.
 * data-columns dipakai untuk highlight sel, data-result-mode untuk warna baris di ViewResultClient
 */
export function renderTableCard(opts: {
  resultMode: 'okng' | 'samediff';
  rowCount: number;
  columns: HeaderColumn[];
  buttonsHtml: string;
  theadHtml: string;
  tbodyHtml: string;
  tableClass?: string;    // class tambahan untuk <table>, mis. 'structure-table'
  wrapperClass?: string;  // class tambahan untuk div.table-wrapper
  cardClass?: string;     // class tambahan untuk div.table-card (mis. lebar minimal tabel freeze)
}): string {
  return `
    <div class="table-card ${opts.cardClass ?? ''}">
      <div class="table-toolbar">
        <div class="hero-metrics" style="display: flex; align-items: center; justify-content: space-between; width: 100%; flex-wrap: wrap; gap: 8px;">
          <div style="display: flex; align-items: center; gap: 14px; font-size: 12px; color: var(--text-muted);">
            <span><i class="fa-solid fa-puzzle-piece" style="color: var(--imperial-red);"></i> <strong>${opts.rowCount}</strong> row(s)</span>
            <span><i class="fa-solid fa-table-columns" style="color: var(--imperial-red);"></i> <strong>${opts.columns.length}</strong> field(s)</span>
          </div>
          ${opts.buttonsHtml}
        </div>
      </div>
      <div class="table-wrapper ${opts.wrapperClass ?? ''}">
        <table class="dynamic-table ${opts.tableClass ?? ''}" data-result-mode="${opts.resultMode}" data-columns="${escapeHtml(opts.columns.map(c => c.label).join('|'))}">
          <thead>${opts.theadHtml}</thead>
          <tbody>${opts.tbodyHtml}</tbody>
        </table>
      </div>
    </div>`;
}

/** Pasang HTML ke container lalu hitung ulang counter NG / Different */
export function finishTableRender(container: HTMLElement, html: string) {
  container.innerHTML = html;
  if (typeof (window as any).updateTableStatusCounters === 'function') {
    (window as any).updateTableStatusCounters(container);
  }
}

/** Normalisasi nama key untuk perbandingan: huruf kecil, tanpa spasi / _ / - */
export function normKey(key: string): string {
  return String(key).toLowerCase().replace(/[\s_-]+/g, '');
}

/**
 * Merge sel kategori (class "merge-cell") per kategori yang sama, hanya menghitung baris yang tampil.
 * - Baris pertama yang tampil di tiap kategori: sel kategori dapat rowspan = jumlah baris tampil kategori itu
 * - Baris lain di kategori yang sama: sel kategori disembunyikan
 * - Baris pertama tiap kategori (kecuali paling atas) diberi class "group-start" -> garis horizontal tebal
 * Dipanggil setelah render dan setiap kali tabel difilter, supaya merge tidak rusak.
 */
export function refreshMergedCategoryCells(root: ParentNode | null | undefined) {
  if (!root) return;
  root.querySelectorAll('table.dynamic-table').forEach(table => {
    // Urutkan sesuai urutan asli (data-row-index), karena di bawah baris bisa dipindah posisinya
    const rows = (Array.from(table.querySelectorAll('tbody tr')) as HTMLTableRowElement[])
      .sort((a, b) => Number(a.getAttribute('data-row-index')) - Number(b.getAttribute('data-row-index')));
    if (!rows.some(tr => tr.querySelector('td.merge-cell'))) return;

    // Supaya rowspan pasti benar, baris yang tampil dibuat bersebelahan (urutan asli),
    // baris yang tersembunyi oleh filter dipindah ke akhir tbody.
    const visible = rows.filter(tr => tr.style.display !== 'none');
    const hidden = rows.filter(tr => tr.style.display === 'none');
    const tbody = table.querySelector('tbody');
    if (tbody) {
      visible.forEach(tr => tbody.appendChild(tr));
      hidden.forEach(tr => tbody.appendChild(tr));
    }

    let startCell: HTMLTableCellElement | null = null;
    let lastCategory: string | null = null;
    let count = 0;
    const flush = () => { if (startCell) startCell.rowSpan = count; };

    hidden.forEach(tr => {
      tr.classList.remove('group-start');
      const cell = tr.querySelector('td.merge-cell') as HTMLTableCellElement | null;
      if (cell) { cell.rowSpan = 1; cell.style.display = 'none'; }
    });

    visible.forEach((tr, i) => {
      tr.classList.remove('group-start');
      const cell = tr.querySelector('td.merge-cell') as HTMLTableCellElement | null;
      if (!cell) return;
      const category = tr.getAttribute('data-category') || '';
      if (category !== lastCategory) {
        flush();
        startCell = cell;
        lastCategory = category;
        count = 1;
        cell.style.display = '';
        if (i > 0) tr.classList.add('group-start');
      } else {
        count++;
        cell.rowSpan = 1;
        cell.style.display = 'none';
      }
    });
    flush();
  });
}

/* ======================================================================
 * TABEL FREEZE: 3 kolom yang freeze di kanan (MPX Result | Engineer Check | Remarks)
 * Dipakai tabel compare (Single / Multi HW Option, Substitute, Assy Release Status).
 * Lebar & posisi kolom diatur di CSS ".compare-table" (ViewResultClient.tsx).
 * ====================================================================== */

/** Header 3 kolom freeze kanan. rowspan = jumlah baris header tabel */
export function freezeRightHeaderCells(rowspan: number): string {
  return `
      <th class="hdr-r1 hdr-banner grp-fixed freeze-right freeze-right-edge fr-3 thick-left" rowspan="${rowspan}">MPX Result</th>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-right fr-2" rowspan="${rowspan}">Engineer Check</th>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-right fr-1" rowspan="${rowspan}">Remarks</th>`;
}

/** Isi 3 kolom freeze kanan untuk satu baris */
export function freezeRightBodyCells(
  result: string,
  mode: 'okng' | 'samediff',
  engineerCheckRaw: any,
  remarkRaw: any
): string {
  return renderMpxResultCell(result, mode, 'freeze-right freeze-right-edge fr-3 thick-left')
    + renderEngineerConfirmCell(engineerCheckRaw, 'freeze-right fr-2')
    + renderRemarkCell(remarkRaw, 'freeze-right fr-1');
}
