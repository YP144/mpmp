import {
  id,
  setText,
  safeString,
  camelToTitle,
  collectKeys,
  getPath,
  getFirstAvailablePath,
  normalizeTableRows,
  HeaderColumn,
  getModelHeaderGroups,
  detectModelGroup,
  buildGroupedHeader,
  normalizeMpxResult,
  renderDataCell,
  renderMpxResultCell,
  renderEngineerConfirmCell,
  renderRemarkCell,
  renderFilterButtons,
  renderTableCard,
  finishTableRender,
  normKey
} from './tableUtils';

/**
 * 1. Daftar Kolom yang Dikecualikan Khusus EAX Substitute Check
 */
export const eaxSubstituteExcludedKeys = new Set([
  'id', 'datatype', 'data type', 'data_type',
  'pp_obid', 'ppobid', 'uniquestr', 'unique str', 'unique_str',
  'uniquestrparent', 'unique str parent', 'uniquestr_parent',
  'referencedesignator', 'reference designator', 'reference_designator',
  'pp_states', 'ppstates',
]);

/**
 * 2. Fungsi Helper untuk Mengambil Data EAX Substitute dari JSON Backend
 */
export function getEaxSubstituteRows(data: any): any[] {
  if (Array.isArray(data)) return data;
  const raw = getFirstAvailablePath(data, [
    'eaxSubstitute.compareData',
    'eaxSubstitute.data',
    'eaxSubstitute'
  ]);
  return normalizeTableRows(raw);
}

/**
 * 3. Fungsi Helper untuk Mengisi Kartu Info EAX / EBR / EBT di Atas Tabel
 */
export function syncEaxSubstituteInfo(data: any) {
  if (!data) return;
  const eaxInfo = getPath(data, 'eaxSubstitute.info') || getPath(data, 'eaxSubstitute') || {};
  setText('info-eax-part-no', safeString(eaxInfo.eaxPartNumber ?? eaxInfo.eaxPartNo ?? '-'));
  setText('info-ebr-part-no', safeString(eaxInfo.ebrPartNumber ?? eaxInfo.ebrPartNo ?? '-'));
  setText('info-ebr-main-part-no', safeString(eaxInfo.ebrMainPartNumber ?? eaxInfo.ebrMainPartNo ?? '-'));
  setText('info-ebt-part-no', safeString(eaxInfo.ebtPartNumber ?? eaxInfo.ebtPartNo ?? '-'));
  setText('info-chassis-name', safeString(eaxInfo.chassisName ?? getPath(data, 'ModelProfile.profileData.0.Chassis') ?? '-'));
}

/**
 * 4. Fungsi Utama Render Tabel EAX Substitute Check (MPX Result: OK / NG / DIFFERENT)
 */
export function renderEaxSubstituteTable(
  containerId = 'container-eax-substitute-check',
  dataOrRows: any
) {
  let rows: any[] = [];
  let data: any = {};
  if (Array.isArray(dataOrRows)) {
    rows = dataOrRows;
  } else if (dataOrRows && typeof dataOrRows === 'object') {
    data = dataOrRows;
    rows = getEaxSubstituteRows(dataOrRows);
    syncEaxSubstituteInfo(dataOrRows); // Otomatis mengisi 5 info chip di atas tabel
  }

  const container = id(containerId);
  if (!container) return;

  if (!rows || rows.length === 0) {
    container.innerHTML = `<div class="empty-state">No entries available.</div>`;
    return;
  }

  // Ambil keys yang tidak di-exclude, lalu buang status/engineer confirm/reason/remarks dari tengah
  const keys = collectKeys(rows, eaxSubstituteExcludedKeys).filter(k => {
    const lk = k.toLowerCase().replace(/[_-]/g, '').trim();
    return lk !== 'status' && lk !== 'result' && lk !== 'reason' && lk !== 'remarks' && lk !== 'remark' && lk !== 'engineerconfirm' && lk !== 'engineercheck';
  });

  // Kolom milik model (mis. Part_Init, Status_Dev, Initial, Target) masuk ke banner model masing-masing
  const dataColumns: HeaderColumn[] = keys.map(k => {
    const g = detectModelGroup(k);
    return g ? { key: k, label: g.label, groupKey: g.group } : { key: k, label: camelToTitle(k) };
  });

  const columns: HeaderColumn[] = [
    ...dataColumns,
    { label: 'MPX Result', className: 'status-column' },
    { label: 'Engineer Check', className: 'engineer-confirm-column' },
    { label: 'Remarks' },
  ];

  // Kolom yang ditampilkan tebal + ikon caret
  const boldKeys = ['series', 'actualpartno', 'partnumber'];

  let tbody = '';
  rows.forEach((row, rowIndex) => {
    const result = normalizeMpxResult(row.status ?? row.Status ?? row.result ?? row.Result);
    const rowStatusClass = result === 'NG' ? 'status-ng' : result === 'DIFFERENT' ? 'status-check' : '';

    tbody += `<tr class="${rowStatusClass}" data-result="${result}" data-row-index="${rowIndex}">`;
    dataColumns.forEach(col => {
      tbody += renderDataCell(col.key ? row[col.key] : undefined, !!col.key && boldKeys.includes(normKey(col.key)));
    });
    tbody += renderMpxResultCell(result);
    tbody += renderEngineerConfirmCell(row.engineer_confirm ?? row.engineerConfirm);
    tbody += renderRemarkCell(row.remarks ?? row.Remarks ?? row.remark ?? row.Remark ?? row.reason ?? row.Reason);
    tbody += `</tr>`;
  });

  finishTableRender(container, renderTableCard({
    resultMode: 'okng',
    rowCount: rows.length,
    columns,
    buttonsHtml: renderFilterButtons({ mode: 'okng' }),
    theadHtml: buildGroupedHeader(columns, getModelHeaderGroups(data)),
    tbodyHtml: tbody,
  }));
}
