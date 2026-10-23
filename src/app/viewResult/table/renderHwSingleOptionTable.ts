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
 * Tab "Single HW Option Compare" (dulu sub-tabel singleOpt di tab HW Multi Option)
 */

/**
 * 1. Daftar Kolom yang Dikecualikan Khusus Single HW Option
 */
export const hwSingleOptionExcludedKeys = new Set([
  'id', 'datatype', 'data type', 'data_type',
  'pp_obid', 'ppobid', 'uniquestr', 'unique str', 'unique_str',
  'uniquestrparent', 'unique str parent', 'uniquestr_parent',
  'referencedesignator', 'reference designator', 'reference_designator',
  'pp_states', 'ppstates',
]);

/**
 * 2. Fungsi Helper untuk Mengambil Data singleOpt
 */
export function getHwSingleOptionRows(data: any): any[] {
  if (Array.isArray(data)) return data;
  const raw = getPath(data, 'multiOption.singleOpt.compData') || getPath(data, 'multiOption.singleOpt');
  return normalizeTableRows(raw);
}

/**
 * 3. Fungsi Render Tabel Single HW Option (singleOpt) (MPX Result: SAME / DIFFERENT)
 *
 * || Single Option || Initial Model || Initial Region || Development Model || Target Model (MP) || MPX Result | Engineer Check | Remarks ||
 *
 * - Single Option                         : freeze di kiri
 * - MPX Result, Engineer Check, Remarks : freeze di kanan
 * - Header 2 baris freeze di atas (baris 2 = nama model TV)
 */
export function renderHwSingleOptionTable(
  containerId = 'container-single-hw-option',
  dataOrRows: any
) {
  const container = id(containerId);
  if (!container) return;

  let rows: any[] = [];
  let data: any = {};
  if (Array.isArray(dataOrRows)) {
    rows = dataOrRows;
  } else if (dataOrRows && typeof dataOrRows === 'object') {
    data = dataOrRows;
    rows = getHwSingleOptionRows(dataOrRows);
  }

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
    { label: 'Single Option' },
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
      <th class="hdr-r1 hdr-banner grp-fixed freeze-left freeze-left-edge fl-1 thick-right" rowspan="2">Single Option</th>
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

  // Nilai bullet (● / •) ditampilkan sebagai tanda besar, nilai lain seperti biasa
  const optionValueCell = (value: any, cls: string) => {
    const text = value === undefined || value === null ? '' : String(value).trim();
    if (text === '●' || text === '•') {
      return `<td class="${cls}"><span class="bullet-mark" title="${escapeHtml(text)}">●</span></td>`;
    }
    return renderDataCell(value, false, cls);
  };

  // Info jumlah baris & DIFFERENT di tombol switch "Single HW Option"
  const diffCount = rows.filter(r => normalizeSameDifferent(r.status ?? r.Status ?? r.result ?? r.Result) === 'DIFFERENT').length;
  const meta = id('hw-switch-single-meta');
  if (meta) meta.innerHTML = `${rows.length} rows · <span class="meta-diff">${diffCount} different</span>`;

  // ---------------- BODY
  let tbody = '';
  rows.forEach((row, rowIndex) => {
    const result = normalizeSameDifferent(row.status ?? row.Status ?? row.result ?? row.Result);
    const rowStatusClass = result === 'DIFFERENT' ? 'status-ng' : '';

    tbody += `<tr class="${rowStatusClass}" data-result="${result}" data-row-index="${rowIndex}">`;
    tbody += renderDataCell(row['Singel Option'] ?? row['Single Option'] ?? row['singleOption'], false, 'cell-left-key freeze-left freeze-left-edge fl-1 thick-right');
    tbody += optionValueCell(row.Initial ?? row.initial, 'col-value thick-right');
    // Initial Region: belum ada dari backend (key rencana: initial_region)
    tbody += renderDataCell(row.initial_region, false, 'col-value thick-right');
    tbody += optionValueCell(row.Development ?? row.development, 'col-value thick-right');
    tbody += optionValueCell(row.Target ?? row.target, 'col-value no-right-border');
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
