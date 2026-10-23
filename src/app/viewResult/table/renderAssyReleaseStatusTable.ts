import {
  id,
  escapeHtml,
  safeString,
  getFirstAvailablePath,
  normalizeTableRows,
  HeaderColumn,
  normalizeMpxResult,
  renderDataCell,
  renderFilterButtons,
  renderTableCard,
  finishTableRender,
  freezeRightHeaderCells,
  freezeRightBodyCells
} from './tableUtils';

/**
 * Tab "Assy Release Status"
 * (dulu sub-tabel "HW Part Status" di dalam tab Substitute, data: subsCheck.partStatus)
 */

/**
 * 1. Daftar Kolom yang Dikecualikan Khusus Assy Release Status
 */
export const assyReleaseStatusExcludedKeys = new Set([
  'id', 'datatype', 'data type', 'data_type',
  'pp_obid', 'ppobid', 'uniquestr', 'unique str', 'unique_str',
  'uniquestrparent', 'unique str parent', 'uniquestr_parent',
  'referencedesignator', 'reference designator', 'reference_designator',
  'pp_states', 'ppstates',
]);

/**
 * 2. Fungsi Helper untuk Mengambil Data Assy Release Status (HW Part Status)
 */
export function getAssyReleaseStatusRows(data: any): any[] {
  if (Array.isArray(data)) return data.map(normalizeAssyReleaseStatusRow);
  const raw = getFirstAvailablePath(data, [
    'subsCheck.partStatus.compareData2',
    'subsCheck.partStatus.compData',
    'subsCheck.HWpartStatus.result',   // format baru (backend get_hw_main_part.py)
    'subsCheck.partStatus.result'
  ]);
  return normalizeTableRows(raw).map(normalizeAssyReleaseStatusRow);
}

/** Ambil nilai pertama yang tidak kosong dari beberapa key */
function firstFilled(row: any, keys: string[]): any {
  for (const k of keys) {
    const v = row?.[k];
    if (v !== undefined && v !== null && String(v).trim() !== '') return v;
  }
  return '';
}

/**
 * Format JSON HW Part Status -> bentuk baris yang dipakai tabel.
 *   Baru (get_hw_main_part.py): { target_pn, target_state, target_qty, target_uit, target_supplytype, target_Category,
 *                                 dev_..., initial_..., "MPX Result", "MPX Reason", "Engineering Confirm", Remarks }
 *   Lama                      : { Category, Part_Init, Status_Init, Part_Dev, ..., Status, Remarks }
 * Hasil: { Category, Part_Init, Status_Init, Qty_Init, UIT_Init, Supply_Init, ..., Status, engineer_confirm, Remarks }
 */
export function normalizeAssyReleaseStatusRow(row: any): any {
  if (!row || typeof row !== 'object') return row;
  const isNewFormat = ['target_pn', 'dev_pn', 'initial_pn', 'target_Category', 'MPX Result'].some(k => k in row);
  if (!isNewFormat) return row;

  const pick = (prefixes: string[], field: string) =>
    firstFilled(row, prefixes.map(p => `${p}_${field}`));
  const INIT = ['initial', 'init'];

  return {
    ...row,
    Category: firstFilled(row, ['target_Category', 'dev_Category', 'initial_Category', 'Category']),
    Part_Init: pick(INIT, 'pn'), Status_Init: pick(INIT, 'state'), Qty_Init: pick(INIT, 'qty'), UIT_Init: pick(INIT, 'uit'), Supply_Init: pick(INIT, 'supplytype'),
    Part_Dev: pick(['dev'], 'pn'), Status_Dev: pick(['dev'], 'state'), Qty_Dev: pick(['dev'], 'qty'), UIT_Dev: pick(['dev'], 'uit'), Supply_Dev: pick(['dev'], 'supplytype'),
    Part_Target: pick(['target'], 'pn'), Status_Target: pick(['target'], 'state'), Qty_Target: pick(['target'], 'qty'), UIT_Target: pick(['target'], 'uit'), Supply_Target: pick(['target'], 'supplytype'),
    // MPX Result backend: SAME / DIFFERENT (SAME -> OK di tabel ini)
    Status: firstFilled(row, ['MPX Result', 'Status', 'status']),
    reason: firstFilled(row, ['MPX Reason', 'reason']),
    // Nilai awal Engineer Check dari backend: OK / Unchecked
    engineer_confirm: firstFilled(row, ['Engineering Confirm', 'engineer_confirm']),
    Remarks: firstFilled(row, ['Remarks', 'remarks']),
  };
}

/**
 * 3. Fungsi Helper Hasil MPX Result per baris (OK / NG / DIFFERENT)
 * Backend lama mengirim angka: 1 = ada perbedaan -> DIFFERENT, 0 = sama -> OK
 * Backend baru mengirim "MPX Result": SAME -> OK, DIFFERENT -> DIFFERENT
 */
export function getAssyReleaseStatusResult(row: any): 'OK' | 'NG' | 'DIFFERENT' {
  const raw = String(row?.status ?? row?.Status ?? row?.result ?? row?.Result ?? row?.['MPX Result'] ?? '').trim();
  if (raw === '1') return 'DIFFERENT';
  if (raw === '0' || raw.toUpperCase() === 'SAME') return 'OK';
  return normalizeMpxResult(raw);
}

/**
 * Baris dengan status yang sudah dinormalisasi (OK / NG / DIFFERENT),
 * dipakai ViewResultClient untuk counter tab & sidebar summary
 */
export function getAssyReleaseStatusSummaryRows(data: any): any[] {
  return getAssyReleaseStatusRows(data).map(row => ({ ...row, status: getAssyReleaseStatusResult(row) }));
}

/**
 * 4. Fungsi Utama Render Tabel Assy Release Status (MPX Result: OK / NG / DIFFERENT)
 *
 * || Description ||                Initial Model               ||  Development Model (5 kolom)  ||  Target Model (MP) (5 kolom)  || MPX Result | Engineer Check | Remarks ||
 * ||             ||               <nama model TV>              ||       <nama model TV>         ||       <nama model TV>         ||            |                |         ||
 * ||             || Part Number | Status | Qty | UIT | Supply Type ||  (sama)                       ||  (sama)                       ||            |                |         ||
 *
 * - Description                         : freeze di kiri
 * - MPX Result, Engineer Check, Remarks : freeze di kanan
 * - Header 3 baris freeze di atas
 */
export function renderAssyReleaseStatusTable(
  containerId = 'container-assy-release-status',
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
    rows = getAssyReleaseStatusRows(dataOrRows);
  }

  if (rows.length === 0) {
    container.innerHTML = `<div class="empty-state">No entries available.</div>`;
    return;
  }

  const initModel = safeString(data?.initName ?? data?.initialModel ?? '-');
  const devModel = safeString(data?.devName ?? data?.devModel ?? '-');
  const mpModel = safeString(data?.targetName ?? data?.mpModel ?? '-');

  // Kolom per model (urutan sama dengan <td> di tbody)
  const MODEL_GROUPS = [
    { label: 'Initial Model', suffix: 'Init', grp: 'grp-c1', name: initModel, lastClass: 'thick-right' },
    { label: 'Development Model', suffix: 'Dev', grp: 'grp-c2', name: devModel, lastClass: 'thick-right' },
    { label: 'Target Model (MP)', suffix: 'Target', grp: 'grp-c3', name: mpModel, lastClass: 'no-right-border' },
  ];
  const SUB_COLUMNS = [
    { label: 'Part Number', field: 'Part', cls: 'col-part' },
    { label: 'Status', field: 'Status', cls: 'col-status' },
    { label: 'Qty', field: 'Qty', cls: 'col-qty' },
    { label: 'UIT', field: 'UIT', cls: 'col-uit' },
    { label: 'Supply Type', field: 'Supply', cls: 'col-supply' },
  ];

  const columns: HeaderColumn[] = [
    { label: 'Description' },
    ...MODEL_GROUPS.flatMap(g => SUB_COLUMNS.map(c => ({ label: `${g.suffix} ${c.label}` }))),
    { label: 'MPX Result' },
    { label: 'Engineer Check' },
    { label: 'Remarks' },
  ];

  // ---------------- HEADER (3 baris, freeze di atas)
  const span = SUB_COLUMNS.length;
  const thead = `
    <tr>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-left freeze-left-edge fl-1 thick-right" rowspan="3">Description</th>
      ${MODEL_GROUPS.map(g => `<th class="hdr-r1 hdr-banner ${g.grp} ${g.lastClass}" colspan="${span}">${g.label}</th>`).join('')}
      ${freezeRightHeaderCells(3)}
    </tr>
    <tr>
      ${MODEL_GROUPS.map(g => `<th class="hdr-r2 hdr-name ${g.grp} ${g.lastClass}" colspan="${span}">${escapeHtml(g.name)}</th>`).join('')}
    </tr>
    <tr>
      ${MODEL_GROUPS.map(g => SUB_COLUMNS.map((c, i) =>
        `<th class="hdr-r3 ${g.grp} ${c.cls} ${i === span - 1 ? g.lastClass : ''}">${c.label}</th>`).join('')).join('')}
    </tr>
  `;

  // ---------------- BODY
  let tbody = '';
  rows.forEach((row, rowIndex) => {
    const result = getAssyReleaseStatusResult(row);
    const rowStatusClass = result === 'NG' ? 'status-ng' : result === 'DIFFERENT' ? 'status-check' : '';

    tbody += `<tr class="${rowStatusClass}" data-result="${result}" data-row-index="${rowIndex}">`;
    tbody += renderDataCell(row.Category ?? row.category, false, 'cell-left-key freeze-left freeze-left-edge fl-1 thick-right');
    MODEL_GROUPS.forEach(g => {
      SUB_COLUMNS.forEach((c, i) => {
        tbody += renderDataCell(row[`${c.field}_${g.suffix}`], false, `${c.cls} ${i === span - 1 ? g.lastClass : ''}`);
      });
    });
    tbody += freezeRightBodyCells(result, 'okng', row.engineer_confirm ?? row.engineerConfirm,
      row.remarks ?? row.Remarks ?? row.remark ?? row.Remark);
    tbody += `</tr>`;
  });

  finishTableRender(container, renderTableCard({
    resultMode: 'okng',
    rowCount: rows.length,
    columns,
    buttonsHtml: renderFilterButtons({ mode: 'okng' }),
    theadHtml: thead,
    tbodyHtml: tbody,
    tableClass: 'freeze-table compare-table',
    wrapperClass: 'freeze-wrapper',
    cardClass: 'fw-compare',
  }));
}
