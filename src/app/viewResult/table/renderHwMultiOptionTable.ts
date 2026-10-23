import {
  id,
  escapeHtml,
  safeString,
  getPath,
  normalizeTableRows,
  HeaderColumn,
  normalizeSameDifferent,
  renderDataCell,
  renderFilterButtons,
  renderTableCard,
  finishTableRender,
  freezeRightHeaderCells,
  freezeRightBodyCells
} from './tableUtils';

/**
 * 1. Daftar Kolom yang Dikecualikan Khusus HW Multi Option
 */
export const hwMultiOptionExcludedKeys = new Set([
  'id', 'datatype', 'data type', 'data_type',
  'pp_obid', 'ppobid', 'uniquestr', 'unique str', 'unique_str',
  'uniquestrparent', 'unique str parent', 'uniquestr_parent',
  'referencedesignator', 'reference designator', 'reference_designator',
  'pp_states', 'ppstates',
]);

/**
 * 2. Fungsi Helper untuk Mengambil Data multiOpt
 * (tabel singleOpt sudah dipindah ke tab sendiri: renderHwSingleOptionTable.ts)
 */
export function getHwMultiOptionMultiRows(data: any): any[] {
  if (Array.isArray(data)) return data;
  const raw = getPath(data, 'multiOption.multiOpt.compData') || getPath(data, 'multiOption.multiOpt');
  // Backend baru mengirim hasil di kolom "Comparison" (OK / DIFFERENT / MISSING OPTION), bukan "Status"
  return normalizeTableRows(raw).map(row => {
    if (!row || typeof row !== 'object' || row.Status !== undefined || row.Comparison === undefined) return row;
    return { ...row, Status: normalizeSameDifferent(row.Comparison) };
  });
}

/**
 * 3. Fungsi Helper Seluruh Baris HW Multi Option (untuk Tab Counters & Progress)
 */
export function getAllHwMultiOptionRows(data: any): any[] {
  return getHwMultiOptionMultiRows(data);
}

/**
 * 4. Fungsi Render Tabel Multi HW Option (multiOpt) (MPX Result: SAME / DIFFERENT)
 *
 * || Multi Option || Initial Model || Initial Region || Development Model || Target Model (MP) || MPX Result | Engineer Check | Remarks ||
 *
 * - Multi Option                         : freeze di kiri
 * - MPX Result, Engineer Check, Remarks : freeze di kanan
 * - Header 2 baris freeze di atas (baris 2 = nama model TV)
 */
export function renderSingleHwMultiOptionTable(
  containerId: string,
  rows: any[],
  data: any
) {
  const container = id(containerId);
  if (!container) return;

  if (!rows || rows.length === 0) {
    container.innerHTML = `<div class="empty-state">No entries available.</div>`;
    return;
  }

  const initModel = safeString(data?.initName ?? data?.initialModel ?? '-');
  const devModel = safeString(data?.devName ?? data?.devModel ?? '-');
  const mpModel = safeString(data?.targetName ?? data?.mpModel ?? '-');
  // Nama model TV Initial Region: belum ada dari backend (key rencana: initRegionName)
  const initRegionModel = safeString(data?.initRegionName ?? data?.initialRegionName ?? '-');

  // Daftar kolom (urutan sama dengan <td> di tbody)
  const columns: HeaderColumn[] = [
    { label: 'Multi Option' },
    { label: 'Initial Model' },
    { label: 'Initial Region' },
    { label: 'Development Model' },
    { label: 'Target Model (MP)' },
    { label: 'MPX Result' },
    { label: 'Engineer Check' },
    { label: 'Remarks' },
  ];

  // ---------------- HEADER (2 baris, freeze di atas)
  const thead = `
    <tr>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-left freeze-left-edge fl-1 thick-right" rowspan="2">Multi Option</th>
      <th class="hdr-r1 hdr-banner grp-c1 col-value thick-right">Initial Model</th>
      <th class="hdr-r1 hdr-banner grp-c4 col-value thick-right">Initial Region</th>
      <th class="hdr-r1 hdr-banner grp-c2 col-value thick-right">Development Model</th>
      <th class="hdr-r1 hdr-banner grp-c3 col-value no-right-border">Target Model (MP)</th>
      ${freezeRightHeaderCells(2)}
    </tr>
    <tr>
      <th class="hdr-r2 hdr-name grp-c1 thick-right">${escapeHtml(initModel)}</th>
      <th class="hdr-r2 hdr-name grp-c4 thick-right">${escapeHtml(initRegionModel)}</th>
      <th class="hdr-r2 hdr-name grp-c2 thick-right">${escapeHtml(devModel)}</th>
      <th class="hdr-r2 hdr-name grp-c3 no-right-border">${escapeHtml(mpModel)}</th>
    </tr>
  `;

  // Info jumlah baris & DIFFERENT di tombol switch "Multi HW Option"
  const diffCount = rows.filter(r => normalizeSameDifferent(r.status ?? r.Status ?? r.result ?? r.Result) === 'DIFFERENT').length;
  const meta = id('hw-switch-multi-meta');
  if (meta) meta.innerHTML = `${rows.length} rows · <span class="meta-diff">${diffCount} different</span>`;

  // ---------------- BODY
  let tbody = '';
  rows.forEach((row, rowIndex) => {
    const result = normalizeSameDifferent(row.status ?? row.Status ?? row.result ?? row.Result);
    const rowStatusClass = result === 'DIFFERENT' ? 'status-ng' : '';

    tbody += `<tr class="${rowStatusClass}" data-result="${result}" data-row-index="${rowIndex}">`;
    tbody += renderDataCell(row['Multi Option'] ?? row['multiOption'], false, 'cell-left-key freeze-left freeze-left-edge fl-1 thick-right');
    tbody += renderDataCell(row.Initial ?? row.initial, false, 'col-value thick-right');
    // Initial Region: belum ada dari backend (key rencana: initial_region)
    tbody += renderDataCell(row.initial_region, false, 'col-value thick-right');
    tbody += renderDataCell(row.Development ?? row.development, false, 'col-value thick-right');
    tbody += renderDataCell(row.Target ?? row.target, false, 'col-value no-right-border');
    tbody += freezeRightBodyCells(result, 'samediff', row.engineer_confirm ?? row.engineerConfirm,
      row.remarks ?? row.Remarks ?? row.remark ?? row.Remark);
    tbody += `</tr>`;
  });

  finishTableRender(container, renderTableCard({
    resultMode: 'samediff',
    rowCount: rows.length,
    columns,
    buttonsHtml: renderFilterButtons({ mode: 'samediff' }),
    theadHtml: thead,
    tbodyHtml: tbody,
    tableClass: 'freeze-table compare-table',
    wrapperClass: 'freeze-wrapper',
    cardClass: 'fw-compare',
  }));
}

/**
 * 5. Fungsi Utama: Render Tabel Multi HW Option
 */
export function renderHwMultiOptionSection(data: any) {
  renderSingleHwMultiOptionTable('container-multi-option-multi', getHwMultiOptionMultiRows(data), data);
}
