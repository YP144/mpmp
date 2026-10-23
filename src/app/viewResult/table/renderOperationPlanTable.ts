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
  buildGroupedHeader,
  normalizeMpxResult,
  renderDataCell,
  renderMpxResultCell,
  renderRemarkCell,
  renderFilterButtons,
  renderTableCard,
  finishTableRender
} from './tableUtils';

/**
 * 1. Daftar Kolom yang Dikecualikan Khusus Tabel Operation Plan
 */
export const operationPlanExcludedKeys = new Set([
  'id', 'datatype', 'data type', 'data_type',
  'jobexpl', 'job_expl', 'job expl',
  'changeno', 'change_no', 'change no',
  'matched_criteria', 'matched criteria',
  'raw_model', 'raw_modelexception', 'raw model', 'raw model exception',
  'raw_plant', 'raw_plantexception', 'raw plant', 'raw plant exception',
  'raw_suffixhq', 'raw_suffixhqexception', 'raw suffix hq', 'raw suffix hq exception',
  'raw_operationrole', 'raw_operationyear', 'raw_boxheight',
  'raw operation role', 'raw operation year', 'raw box height',
  'status_remark', 'status remark',
  'part_number_status', 'part number status',
  '_join_key',
]);

/**
 * 2. Fungsi Helper untuk Mengambil Data Operation Plan dari JSON Backend
 * Mendukung pembacaan baik format array murni maupun format object berindeks { "0": {...}, "1": {...} }
 */
export function getOperationPlanRows(data: any): any[] {
  if (Array.isArray(data)) return data;
  const raw = getFirstAvailablePath(data, [
    'OperationPlan.OperationCheck.operation_data',
    'OperationPlan.OperationCheck',
    'OperationPlan.operation_data',
    'operationPlan.OperationCheck.operation_data',
    'operationPlan.OperationCheck',
    'operationPlan.operation_data',
    'operationPlan'
  ]);
  return normalizeTableRows(raw);
}

/**
 * 3. Fungsi Helper untuk Mengisi Kartu Info Database di Atas Tabel
 */
export function syncOperationPlanInfo(data: any) {
  if (!data) return;
  const opInfo = getPath(data, 'OperationPlan.info') || getPath(data, 'operationPlan.info') || {};
  setText('info-op-db-name', safeString(opInfo.databaseName ?? data.databaseName ?? '-'));
  setText('info-op-db-version', safeString(opInfo.databaseVersion ?? data.databaseVersion ?? data.db_version ?? '-'));
  setText('info-op-db-date', safeString(opInfo.databaseDate ?? data.databaseDate ?? '-'));
  setText('info-op-db-year', safeString(opInfo.databaseYear ?? data.databaseYear ?? '-'));
}

/**
 * 4. Fungsi Utama Render Tabel Operation Plan Check (MPX Result: OK / NG / DIFFERENT)
 */
export function renderOperationPlanTable(
  containerId = 'container-operation-plan-check',
  dataOrRows: any
) {
  const container = id(containerId);
  if (!container) return;

  let rows: any[] = [];
  if (Array.isArray(dataOrRows)) {
    rows = dataOrRows;
  } else if (dataOrRows && typeof dataOrRows === 'object') {
    rows = getOperationPlanRows(dataOrRows);
    syncOperationPlanInfo(dataOrRows); // Otomatis mengisi info chip di atas tabel
  }

  if (rows.length === 0) {
    container.innerHTML = '<div class="empty-state">No entries available.</div>';
    return;
  }

  // Ambil keys kolom yang tidak di-exclude
  let keys = collectKeys(rows, operationPlanExcludedKeys);

  // Singkirkan kolom status/reason/remarks bawaan agar diposisikan rapi di ujung kanan
  keys = keys.filter(k => {
    const lk = k.toLowerCase().replace(/[_-]/g, '').trim();
    return lk !== 'status' && lk !== 'result' && lk !== 'reason' && lk !== 'remarks' && lk !== 'remark' && lk !== 'engineerconfirm' && lk !== 'engineercheck' && lk !== 'comparestates';
  });

  // Prioritaskan posisi Category dan Input Part Number di kolom awal jika tersedia
  const findKey = (name: string) => keys.find(k => k.toLowerCase().replace(/[_-]/g, '').trim() === name.toLowerCase().replace(/[_-]/g, '').trim());
  const catKey = findKey('category');
  const inputPartKey = findKey('input part number') || findKey('input_part_number') || findKey('partno') || findKey('part_number');

  if (catKey) {
    keys = keys.filter(k => k !== catKey);
    keys.unshift(catKey);
  }
  if (inputPartKey && catKey) {
    keys = keys.filter(k => k !== inputPartKey);
    const catIdx = keys.indexOf(catKey);
    keys.splice(catIdx + 1, 0, inputPartKey);
  }

  const columns: HeaderColumn[] = [
    ...keys.map(k => ({ key: k, label: camelToTitle(k) })),
    { label: 'MPX Result', className: 'status-column' },
    { label: 'Reason' },
    { label: 'Remarks' },
  ];

  let tbody = '';
  rows.forEach((row, rowIndex) => {
    // Status dari status/result; kalau kosong disimpulkan dari teks compare_states
    const compareStates = safeString(row.compare_states ?? row.compareStates ?? '').trim();
    let rawStatus = safeString(row.status ?? row.Status ?? row.result ?? '').trim();
    if (!rawStatus || rawStatus === '-') {
      rawStatus = compareStates.toLowerCase().includes('not match') ? 'NG' : 'OK';
    }
    const result = normalizeMpxResult(rawStatus);
    const rowStatusClass = result === 'NG' ? 'status-ng' : result === 'DIFFERENT' ? 'status-check' : 'status-ok';

    tbody += `<tr class="${rowStatusClass}" data-result="${result}" data-row-index="${rowIndex}">`;
    keys.forEach(k => { tbody += renderDataCell(row[k]); });
    tbody += renderMpxResultCell(result);
    tbody += renderDataCell(row.reason ?? row.Reason ?? compareStates ?? row.status_remark);
    tbody += renderRemarkCell(row.remarks ?? row.Remarks ?? row.remark ?? row.Remark);
    tbody += `</tr>`;
  });

  finishTableRender(container, renderTableCard({
    resultMode: 'okng',
    rowCount: rows.length,
    columns,
    buttonsHtml: renderFilterButtons({ mode: 'okng', withUncheck: false }),
    theadHtml: buildGroupedHeader(columns, {}),
    tbodyHtml: tbody,
  }));
}
