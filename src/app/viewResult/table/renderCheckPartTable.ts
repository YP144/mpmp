import {
  id,
  setText,
  escapeHtml,
  safeString,
  camelToTitle,
  collectKeys,
  getPath,
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
 * 1. Daftar Kolom yang Dikecualikan Khusus Check Part
 */
export const checkPartExcludedKeys = new Set([
  'id', 'datatype', 'data type', 'data_type',
  'pp_obid', 'ppobid', 'uniquestr', 'unique str', 'unique_str',
  'uniquestrparent', 'unique str parent', 'uniquestr_parent',
  'referencedesignator', 'reference designator', 'reference_designator',
  'pp_states', 'ppstates',
]);

/**
 * 2. Fungsi-Fungsi Helper Ekstraksi Data Sub-Tabel Check Part
 */
export function getCheckPartEbtRows(data: any): any[] {
  return normalizeTableRows(getPath(data, 'checkPart.ebt') || getPath(data, 'ChassisAssembly.ebt'));
}

export function getCheckPartEbrRows(data: any): any[] {
  return normalizeTableRows(getPath(data, 'checkPart.ebr') || getPath(data, 'ChassisAssembly.ebr'));
}

export function getCheckPartEbuRows(data: any): any[] {
  return normalizeTableRows(getPath(data, 'checkPart.ebu') || getPath(data, 'ChassisAssembly.ebu'));
}

export function getCheckPartEaxRows(data: any): any[] {
  return normalizeTableRows(getPath(data, 'checkPart.eax') || getPath(data, 'ChassisAssembly.eax'));
}

export function getCheckPartOpRefRows(data: any): any[] {
  return normalizeTableRows(getPath(data, 'checkPart.operationPlanRef') || getPath(data, 'OperationPlan.reference'));
}

export function getCheckPartEcoRows(data: any): any[] {
  return normalizeTableRows(getPath(data, 'checkPart.ecoList') || getPath(data, 'ECO.affectedPartList'));
}

export function getCheckPartHwSingleRows(data: any): any[] {
  return normalizeTableRows(getPath(data, 'checkPart.hwSingle') || getPath(data, 'HWPartList.singlePart'));
}

export function getCheckPartHwDupRows(data: any): any[] {
  return normalizeTableRows(getPath(data, 'checkPart.hwDup') || getPath(data, 'HWPartList.duplicatedPart'));
}

/**
 * 3. Fungsi Helper Menggabungkan Seluruh Baris Check Part (untuk Tab Counter)
 */
export function getAllCheckPartRows(data: any): any[] {
  return [
    ...getCheckPartEbtRows(data),
    ...getCheckPartEbrRows(data),
    ...getCheckPartEbuRows(data),
    ...getCheckPartEaxRows(data),
    ...getCheckPartHwSingleRows(data),
    ...getCheckPartHwDupRows(data)
  ];
}

/**
 * 4. Fungsi Helper Sinkronisasi Info Chip di Atas Tab
 */
export function syncCheckPartInfo(data: any) {
  if (!data) return;
  setText('info-check-part-model-name', safeString(data.targetName ?? data.mpModel ?? '-'));
  setText('info-check-part-dev-model', safeString(data.devName ?? data.devModel ?? '-'));
  setText('info-check-part-init-model', safeString(data.initName ?? data.initModel ?? '-'));
}

/**
 * 5. Fungsi Render Satu Sub-Tabel Check Part (MPX Result: OK / NG / DIFFERENT)
 */
export function renderSingleCheckPartTable(
  containerId: string,
  rows: any[],
  title = 'Check Part Table',
  data: any = {}
) {
  const container = id(containerId);
  if (!container) return;

  if (!rows || rows.length === 0) {
    container.innerHTML = `<div class="empty-state">No ${escapeHtml(title)} entries available.</div>`;
    return;
  }

  // Ambil keys yang tidak di-exclude, lalu buang status/engineer confirm/reason/remarks dari tengah
  const keys = collectKeys(rows, checkPartExcludedKeys).filter(k => {
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
  const boldKeys = ['product', 'criteria', 'name', 'category', 'partno', 'partnumber'];

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

/**
 * 6. Fungsi Utama: Render Seluruh Sub-Tabel Check Part Sekaligus
 */
export function renderCheckPartSection(data: any) {
  syncCheckPartInfo(data);

  renderSingleCheckPartTable('container-check-part-ebt', getCheckPartEbtRows(data), 'EBT Section', data);
  renderSingleCheckPartTable('container-check-part-ebr', getCheckPartEbrRows(data), 'EBR Section', data);
  renderSingleCheckPartTable('container-check-part-ebu', getCheckPartEbuRows(data), 'EBU Section', data);
  renderSingleCheckPartTable('container-check-part-eax', getCheckPartEaxRows(data), 'EAX Section', data);

  renderSingleCheckPartTable('container-check-part-op-ref', getCheckPartOpRefRows(data), 'Operation Plan Reference', data);
  renderSingleCheckPartTable('container-check-part-eco-list', getCheckPartEcoRows(data), 'Affected Part List', data);

  renderSingleCheckPartTable('container-check-part-hw-single', getCheckPartHwSingleRows(data), 'Single HW Part', data);
  renderSingleCheckPartTable('container-check-part-hw-dup', getCheckPartHwDupRows(data), 'Duplicated HW Part', data);
}
