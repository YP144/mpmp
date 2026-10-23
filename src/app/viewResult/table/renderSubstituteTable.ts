import {
  id,
  escapeHtml,
  safeString,
  getPath,
  getFirstAvailablePath,
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
 * 1. Daftar Kolom yang Dikecualikan Khusus Substitute
 */
export const substituteExcludedKeys = new Set([
  'id', 'datatype', 'data type', 'data_type',
  'pp_obid', 'ppobid', 'uniquestr', 'unique str', 'unique_str',
  'uniquestrparent', 'unique str parent', 'uniquestr_parent',
  'referencedesignator', 'reference designator', 'reference_designator',
  'pp_states', 'ppstates',
]);

/**
 * 2. Fungsi Helper untuk Mengambil Data HW Part Status
 */
export function getSubstitutePartStatusRows(data: any): any[] {
  if (Array.isArray(data)) return data;
  const raw = getFirstAvailablePath(data, [
    'subsCheck.partStatus.compareData2',
    'subsCheck.partStatus.compData'
  ]);
  return normalizeTableRows(raw);
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
 * Format JSON substitute -> bentuk baris yang dipakai tabel.
 *   Baru (compareSubs_New.py): { target_category, target_bomLevel, target_part_number, target_part_quantity,
 *                                dev_..., init_... }
 *   Lama                     : { Description, Subs_Init, Subs_Dev, Subs_Target, Status }
 * Hasil: { Description, Level_Init, Part_Init, Qty_Init, Level_Dev, ..., Status, Remarks }
 * Status (SAME / DIFFERENT) dihitung dari Level + Part Number + Qty ketiga model,
 * kecuali backend sudah mengirim kolom status sendiri.
 */
export function normalizeSubstituteRow(row: any): any {
  if (!row || typeof row !== 'object') return row;

  const isNewFormat = ['target_part_number', 'dev_part_number', 'init_part_number', 'target_category']
    .some(k => k in row);

  const pick = (prefixes: string[], field: string) =>
    firstFilled(row, prefixes.map(p => `${p}_${field}`));

  const groups = isNewFormat
    ? {
        Init: { level: pick(['init', 'initial'], 'bomLevel'), part: pick(['init', 'initial'], 'part_number'), qty: pick(['init', 'initial'], 'part_quantity') },
        Dev: { level: pick(['dev'], 'bomLevel'), part: pick(['dev'], 'part_number'), qty: pick(['dev'], 'part_quantity') },
        Target: { level: pick(['target'], 'bomLevel'), part: pick(['target'], 'part_number'), qty: pick(['target'], 'part_quantity') },
      }
    : {
        Init: { level: '', part: firstFilled(row, ['Subs_Init', 'subs_init']), qty: '' },
        Dev: { level: '', part: firstFilled(row, ['Subs_Dev', 'subs_dev']), qty: '' },
        Target: { level: '', part: firstFilled(row, ['Subs_Target', 'subs_target']), qty: '' },
      };

  const sig = (g: { level: any; part: any; qty: any }) => `${g.level}|${String(g.part).trim()}|${g.qty}`;
  const same = sig(groups.Init) === sig(groups.Dev) && sig(groups.Dev) === sig(groups.Target);
  const backendStatus = firstFilled(row, ['MPX Result', 'mpx_result', 'Status', 'status']);

  return {
    ...row,
    Description: isNewFormat
      ? firstFilled(row, ['target_category', 'dev_category', 'init_category', 'initial_category'])
      : firstFilled(row, ['Description', 'description']),
    Level_Init: groups.Init.level, Part_Init: groups.Init.part, Qty_Init: groups.Init.qty,
    Level_Dev: groups.Dev.level, Part_Dev: groups.Dev.part, Qty_Dev: groups.Dev.qty,
    Level_Target: groups.Target.level, Part_Target: groups.Target.part, Qty_Target: groups.Target.qty,
    Status: backendStatus !== '' ? backendStatus : (same ? 'SAME' : 'DIFFERENT'),
    Remarks: firstFilled(row, ['Remarks', 'remarks']),
  };
}

/**
 * 3. Fungsi Helper untuk Mengambil Data Substitute
 * Mendukung 2 format backend:
 *   - lama : subsCheck.subsJson.compData  (array)
 *   - baru : subsCheck.subsJson           (langsung array, dari compareSubs_New.py)
 */
export function getSubstituteCompDataRows(data: any): any[] {
  if (Array.isArray(data)) return data.map(normalizeSubstituteRow);
  const subsJson = getPath(data, 'subsCheck.subsJson');
  const raw = Array.isArray(subsJson)
    ? subsJson
    : getFirstAvailablePath(data, ['subsCheck.subsJson.compData', 'subsCheck.subsJson.result']);
  return normalizeTableRows(raw).map(normalizeSubstituteRow);
}

/**
 * 4. Fungsi Helper Seluruh Baris Substitute (untuk Tab Counters & Progress)
 * (HW Part Status sudah punya tab sendiri: Assy Release Status, jadi tidak ikut dihitung di sini)
 */
export function getAllSubstituteRows(data: any): any[] {
  return getSubstituteCompDataRows(data);
}

/**
 * 5. Fungsi Render Tabel Substitute (MPX Result: SAME / DIFFERENT)
 *
 * || Description ||   Initial Model           ||   Development Model       ||   Target Model (MP)       || MPX Result | Engineer Check | Remarks ||
 * ||             ||   <nama model TV>         ||   <nama model TV>         ||   <nama model TV>         ||            |                |         ||
 * ||             || Level | Part Number | Qty || Level | Part Number | Qty || Level | Part Number | Qty ||            |                |         ||
 *
 * - Description                         : freeze di kiri
 * - MPX Result, Engineer Check, Remarks : freeze di kanan
 * - Header 3 baris freeze di atas
 */
export function renderSingleSubstituteTable(
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

  // Kolom per model (urutan sama dengan <td> di tbody)
  const MODEL_GROUPS = [
    { label: 'Initial', suffix: 'Init', grp: 'grp-c1', name: initModel, lastClass: 'thick-right' },
    { label: 'Development', suffix: 'Dev', grp: 'grp-c2', name: devModel, lastClass: 'thick-right' },
    { label: 'Target', suffix: 'Target', grp: 'grp-c3', name: mpModel, lastClass: 'no-right-border' },
  ];
  const SUB_COLUMNS = [
    { label: 'Level', field: 'Level', cls: 'col-level' },
    { label: 'Part Number', field: 'Part', cls: 'col-part' },
    { label: 'Qty', field: 'Qty', cls: 'col-qty' },
  ];

  const columns: HeaderColumn[] = [
    { label: 'Description' },
    ...MODEL_GROUPS.flatMap(g => SUB_COLUMNS.map(c => ({ label: `${g.label} ${c.label}` }))),
    { label: 'MPX Result' },
    { label: 'Engineer Check' },
    { label: 'Remarks' },
  ];

  // Nilai part number substitute diberi prefix "*S*  " (kecuali kosong / strip)
  const withSubsPrefix = (value: any) => {
    const text = value === undefined || value === null ? '' : String(value).trim();
    if (!text || text === '-') return value;
    return `*S*\u00A0\u00A0${text}`;   // \u00A0 = spasi yang tidak dihapus HTML
  };

  // ---------------- HEADER (3 baris, freeze di atas)
  const span = SUB_COLUMNS.length;
  const thead = `
    <tr>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-left freeze-left-edge fl-1 thick-right" rowspan="3">Description</th>
      ${MODEL_GROUPS.map(g => `<th class="hdr-r1 hdr-banner ${g.grp} ${g.lastClass}" colspan="${span}">${g.label} Model${g.suffix === 'Target' ? ' (MP)' : ''}</th>`).join('')}
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
    const result = normalizeSameDifferent(row.status ?? row.Status ?? row.result ?? row.Result);
    const rowStatusClass = result === 'DIFFERENT' ? 'status-ng' : '';

    tbody += `<tr class="${rowStatusClass}" data-result="${result}" data-row-index="${rowIndex}">`;
    tbody += renderDataCell(row.Description ?? row.description, false, 'cell-left-key freeze-left freeze-left-edge fl-1 thick-right');
    MODEL_GROUPS.forEach(g => {
      SUB_COLUMNS.forEach((c, i) => {
        let value = row[`${c.field}_${g.suffix}`];
        if (c.field === 'Part') value = withSubsPrefix(value);
        tbody += renderDataCell(value, false, `${c.cls} ${i === span - 1 ? g.lastClass : ''}`);
      });
    });
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
 * 6. Fungsi Utama: Render Tabel Substitute
 */
export function renderSubstituteSection(data: any) {
  renderSingleSubstituteTable('container-substitute-comp-data', getSubstituteCompDataRows(data), data);
}
