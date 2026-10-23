import {
  id,
  setText,
  escapeHtml,
  safeString,
  getFirstAvailablePath,
  normalizeTableRows,
  HeaderColumn,
  normalizeMpxResult,
  renderDataCell,
  renderMpxResultCell,
  renderRemarkCell,
  renderTableCard,
  finishTableRender
} from './tableUtils';

/**
 * 1. Daftar Kolom yang Dikecualikan Khusus Tabel Structure
 * (Termasuk kolom-kolom kalkulasi internal dari backend)
 */
export const structureExcludedKeys = new Set([
  // Kolom referensi / internal lama
  'mother part', 'mother_part', 'motherpart',
  'desc ref', 'desc_ref', 'descref',
  'tech ref', 'tech_ref', 'techref',
  'partno check', 'partno_check', 'partnocheck',
  'qty check', 'qty_check', 'qtycheck',
  'uit check', 'uit_check', 'uitcheck',
  'supply check', 'supply_check', 'supplycheck',
  'special case', 'special-case', 'special_case', 'specialcase',
  'check num', 'check_num', 'checknum',
  'series only', 'series_only', 'seriesonly',
  'series exception', 'series_exception', 'seriesexception',
  'suffix only', 'suffix_only', 'suffixonly',
  'suffix exception', 'suffix_exception', 'suffixexception',
  'expection result', 'exception result', 'exception_result', 'exceptionresult',
  'id', 'criteria right', 'criteria_right', 'criteriaright',
  'datatype', 'data type', 'data_type', 'uniquestr', 'unique str', 'unique_str',
  'pp_obid', 'ppobid',
  'uniquestrparent', 'unique str parent', 'uniquestr_parent',
  'referencedesignator', 'reference designator', 'reference_designator',
  'pp_states', 'ppstates',

  // Kolom kalkulasi & duplikat join dari backend (quickCompare.py)
  'mother part right', 'mother_part_right', 'motherpartright', 'mother part_right',
  'bom level int', 'bom_level_int', 'bomlevel_int', 'bomlevelint', 'bomlevel int',
  'part number clean', 'part_number_clean', 'partnumberclean',
  'part descriptions clean', 'part_descriptions_clean', 'partdescriptionsclean',
  'comp right', 'comp_right', 'compright',
  'qty ref right', 'qty_ref_right', 'qtyrefright',
  'uit ref right', 'uit_ref_right', 'uitrefright',
  'supply type right', 'supply_type_right', 'supplytyperight',
  'part num right', 'part_num_right', 'partnumright',
  'part number right', 'part_number_right', 'partnumberright', 'part technical spec'
]);

/**
 * 2. Fungsi Helper untuk Mengambil Data Structure dari JSON Backend
 */
export function getStructureRows(data: any): any[] {
  if (Array.isArray(data)) return data;
  const raw = getFirstAvailablePath(data, [
    'structureCompare.result.compareData',
    'result.compareData',
    'compareData',
    'data'
  ]);
  return normalizeTableRows(raw);
}

/**
 * 3. Fungsi Helper untuk Mengisi Kartu Info Structure di Atas Tabel
 */
export function syncStructureInfo(data: any) {
  if (!data) return;
  const runInfo = getFirstAvailablePath(data, [
    'structureCompare.result.run_info',
    'structureCompare.info',
    'result.run_info',
    'run_info'
  ]) || {};
  setText('info-struct-plant-name', safeString(runInfo.subsName ?? data.subsName ?? '-'));
  setText('info-struct-suffix-name', safeString(runInfo.suffixName ?? data.suffixName ?? '-'));
  setText('info-struct-plant-suffix', safeString(runInfo.subsSuffix ?? data.subsSuffix ?? '-'));
  setText('info-struct-editor', safeString(runInfo.editor ?? data.editor ?? '-'));
  setText('info-struct-creator', safeString(runInfo.creator ?? data.creator ?? '-'));
  setText('info-struct-edited-date', safeString(runInfo.run_date ?? data.run_date ?? '-'));
  setText('info-struct-plant-code', safeString(runInfo.templateHeader ?? data.templateHeader ?? '-'));
}

/**
 * 4. Susunan Kolom Tetap Tabel Structure
 *
 * || Category || Reference Type || Reference Document (5) || Target Model (MP) (5) || Initial Model (5) || MPX Result | Reason | Remarks ||
 *
 * - Category                    : freeze di kiri saat scroll horizontal
 * - MPX Result, Reason, Remarks : freeze di kanan saat scroll horizontal
 * - Semua baris header          : freeze di atas saat scroll vertikal
 * - Border tebal (||) memisahkan grup kolom (class "thick-right" / "thick-left")
 * - Warna header per grup: class grp-fixed / grp-c1 (Reference) / grp-c2 (Target) / grp-c3 (Initial)
 *   -> variabel --ft-* di ViewResultClient.tsx
 */
interface StructureSubColumn {
  label: string;
  key?: string;   // key di JSON. Kosong = belum ada datanya (tampil "-")
}

const STRUCTURE_SUB_LABELS = ['Level', 'Part Number', 'Qty', 'UIT', 'Supply Type'];

// Reference Document (template structure)
const REFERENCE_COLUMNS: StructureSubColumn[] = [
  { label: 'Level', key: 'BOM_Level' },
  { label: 'Part Number', key: 'PartNum' },
  { label: 'Qty', key: 'Qty_Ref' },
  { label: 'UIT', key: 'Uit_Ref' },
  { label: 'Supply Type', key: 'Supply Type' },
];

// Target Model (MP)
const TARGET_COLUMNS: StructureSubColumn[] = [
  { label: 'Level', key: 'bomLevel_int' },
  { label: 'Part Number', key: 'part_number' },
  { label: 'Qty', key: 'part_quantity' },
  { label: 'UIT', key: 'part_UIT' },
  { label: 'Supply Type', key: 'part_supplyType' },
];

// Initial Model: belum ada datanya dari backend -> sementara kosong ("-")
const INITIAL_COLUMNS: StructureSubColumn[] = STRUCTURE_SUB_LABELS.map(label => ({ label }));

/**
 * Part Number diberi prefix sesuai Level supaya terlihat seperti pohon struktur:
 *   Level 1 -> ABA*
 *   Level 2 -> └ EBT*
 *   Level 3 ->     └ EAD*   (setiap level berikutnya menjorok 4 spasi lagi)
 */
export function formatPartNumberByLevel(partNumber: any, level: any): any {
  const text = partNumber === undefined || partNumber === null ? '' : String(partNumber).trim();
  const lvl = parseInt(String(level ?? ''), 10);
  if (!text || text === '-' || isNaN(lvl) || lvl <= 1) return partNumber;
  const indent = '\u00A0'.repeat((lvl - 2) * 4);   // spasi yang tidak dihapus oleh HTML
  return `${indent}└ ${text}`;
}

/** Kolom terakhir di setiap grup 5 kolom diberi class border (mis. border tebal) */
function groupCellClass(index: number, total: number, lastClass: string) {
  return index === total - 1 ? lastClass : '';
}

/**
 * 5. Fungsi Utama Render Tabel Structure
 */
export function renderStructureTable(
  containerId = 'container-structure',
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
    rows = getStructureRows(dataOrRows);
    syncStructureInfo(dataOrRows);
  }

  if (rows.length === 0) {
    container.innerHTML = '<div class="empty-state">No entries available.</div>';
    return;
  }

  const runInfo = getFirstAvailablePath(data, ['structureCompare.result.run_info', 'result.run_info']) || {};
  const referenceDocName = safeString(runInfo.templateName ?? runInfo.templateHeader ?? '-');
  const targetModelName = safeString(data?.targetName ?? data?.mpModel ?? '-');
  const initialModelName = safeString(data?.initName ?? data?.initialModel ?? '-');

  // Daftar kolom (urutan sama dengan <td> di tbody).
  // Label unik ("Target UIT", dst.) dipakai untuk highlight sel UIT / Supply / Qty milik Target
  const columns: HeaderColumn[] = [
    { label: 'Category' },
    { label: 'Reference Type' },
    ...REFERENCE_COLUMNS.map(c => ({ label: `Reference ${c.label}` })),
    ...TARGET_COLUMNS.map(c => ({ label: `Target ${c.label}` })),
    ...INITIAL_COLUMNS.map(c => ({ label: `Initial ${c.label}` })),
    { label: 'MPX Result' },
    { label: 'Reason' },
    { label: 'Remarks' },
  ];

  // ---------------- HEADER (3 baris, semuanya freeze di atas)
  const subHeaderCells = (cols: StructureSubColumn[], groupClass: string, lastClass: string) =>
    cols.map((c, i) => `<th class="hdr-r3 ${groupClass} ${groupCellClass(i, cols.length, lastClass)}">${escapeHtml(c.label)}</th>`).join('');

  const thead = `
    <tr>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-left freeze-left-edge fl-1 thick-right" rowspan="3">Category</th>
      <th class="hdr-r1 hdr-banner grp-fixed col-ref-type thick-right" rowspan="3">Reference Type</th>
      <th class="hdr-r1 hdr-banner grp-c1 thick-right" colspan="${REFERENCE_COLUMNS.length}">Reference Document</th>
      <th class="hdr-r1 hdr-banner grp-c2 thick-right" colspan="${TARGET_COLUMNS.length}">Target Model (MP)</th>
      <th class="hdr-r1 hdr-banner grp-c3 no-right-border" colspan="${INITIAL_COLUMNS.length}">Initial Model</th>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-right freeze-right-edge fr-3 thick-left" rowspan="3">MPX Result</th>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-right fr-2" rowspan="3">Reason</th>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-right fr-1" rowspan="3">Remarks</th>
    </tr>
    <tr>
      <th class="hdr-r2 hdr-name grp-c1 thick-right" colspan="${REFERENCE_COLUMNS.length}">${escapeHtml(referenceDocName)}</th>
      <th class="hdr-r2 hdr-name grp-c2 thick-right" colspan="${TARGET_COLUMNS.length}">${escapeHtml(targetModelName)}</th>
      <th class="hdr-r2 hdr-name grp-c3 no-right-border" colspan="${INITIAL_COLUMNS.length}">${escapeHtml(initialModelName)}</th>
    </tr>
    <tr>
      ${subHeaderCells(REFERENCE_COLUMNS, 'grp-c1', 'thick-right')}
      ${subHeaderCells(TARGET_COLUMNS, 'grp-c2', 'thick-right')}
      ${subHeaderCells(INITIAL_COLUMNS, 'grp-c3', 'no-right-border')}
    </tr>
  `;

  // ---------------- BODY
  // Kolom pertama grup = Level, dipakai untuk prefix kolom Part Number di grup yang sama
  const groupCells = (row: any, cols: StructureSubColumn[], lastClass: string) => {
    const levelKey = cols[0]?.key;
    return cols.map((c, i) => {
      let value = c.key ? row[c.key] : undefined;
      if (c.label === 'Part Number' && levelKey) value = formatPartNumberByLevel(value, row[levelKey]);
      return renderDataCell(value, false, groupCellClass(i, cols.length, lastClass));
    }).join('');
  };

  let tbody = '';
  rows.forEach((row, rowIndex) => {
    const result = normalizeMpxResult(row.status ?? row.Status ?? row.result ?? row.Result);
    const bomLevelVal = safeString(row['BOM_Level'] ?? row['BOM Level'] ?? row['bom_level'] ?? row['bomLevel_int'] ?? '').trim();
    const rowStatusClass = result === 'NG' ? 'status-ng' : result === 'DIFFERENT' ? 'status-check' : 'status-ok';
    const initialRowDisplayStyle = (bomLevelVal === '' || bomLevelVal === '-') ? 'display: none;' : '';

    tbody += `<tr class="${rowStatusClass}" data-result="${result}" data-bom-level="${escapeHtml(bomLevelVal)}" data-row-index="${rowIndex}" style="${initialRowDisplayStyle}">`;
    tbody += renderDataCell(row.Criteria ?? row.criteria ?? row['structure_operation'], false, 'freeze-left freeze-left-edge fl-1 thick-right cell-bold');
    // Reference Type: masih dikomunikasikan dengan backend (key rencana: reference_type)
    tbody += renderDataCell(row.reference_type ?? row['Reference Type'], false, 'col-ref-type thick-right');
    tbody += groupCells(row, REFERENCE_COLUMNS, 'thick-right');
    tbody += groupCells(row, TARGET_COLUMNS, 'thick-right');
    tbody += groupCells(row, INITIAL_COLUMNS, 'no-right-border');
    tbody += renderMpxResultCell(result, 'okng', 'freeze-right freeze-right-edge fr-3 thick-left');
    tbody += renderDataCell(row.reason ?? row.Reason, false, 'freeze-right fr-2');
    tbody += renderRemarkCell(row.remarks ?? row.Remarks ?? row.remark ?? row.Remark, 'freeze-right fr-1');
    tbody += `</tr>`;
  });

  // Toolbar khusus Structure (data-combined-filter): filter Level & filter Result bisa aktif bersamaan.
  // Logikanya di applyCombinedFilter() di ViewResultClient.tsx. Default: Show BOM Level Only aktif.
  const filterButton = (type: string, cls: string, icon: string, label: string, counterClass = '') =>
    `<button class="table-status-counter ${cls}" data-filter="${type}" onclick="window.filterTableRows(this, '${type}')">` +
    `<i class="fa-solid ${icon}"></i> ${label}${counterClass ? ` <strong class="${counterClass}">0</strong>` : ''}</button>`;

  const toolbarButtons = `
    <div class="table-status-counters" data-combined-filter="1" data-level-filter="on" data-result-filter="ALL">
      ${filterButton('NG', 'counter-ng', 'fa-circle-xmark', 'Show NG', 'counter-ng-value')}
      ${filterButton('DIFFERENT', 'counter-check', 'fa-not-equal', 'Show Differences', 'counter-diff-value')}
      ${filterButton('OK', 'counter-ok', 'fa-circle-check', 'Show OK')}
      <span class="toolbar-divider"></span>
      ${filterButton('BOM_LEVEL', 'counter-bom active-filter', 'fa-sitemap', 'Show BOM Level Only')}
      ${filterButton('ALL', 'counter-all', 'fa-rotate-left', 'Show All')}
    </div>`;

  finishTableRender(container, renderTableCard({
    resultMode: 'okng',
    rowCount: rows.length,
    columns,
    buttonsHtml: toolbarButtons,
    theadHtml: thead,
    tbodyHtml: tbody,
    tableClass: 'freeze-table structure-table',
    wrapperClass: 'freeze-wrapper',
    cardClass: 'fw-structure',
  }));
}
