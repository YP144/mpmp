import {
  id,
  escapeHtml,
  safeString,
  camelToTitle,
  getPath,
  HeaderColumn,
  buildGroupedHeader,
  normalizeMpxResult,
  renderMpxResultCell,
  renderEngineerConfirmCell,
  renderRemarkCell,
  renderFilterButtons,
  renderTableCard,
  finishTableRender
} from './tableUtils';

/**
 * 1. Peta Nama Modul Teknis ke Nama Tampilan Resmi
 */
const moduleLabelMap: Record<string, string> = {
  'Structure': 'Structure & Operation Plan Check',
  'HWcompare': 'Tool Option',
  'subsCompare': 'Substitute Check',
  'multiOption': 'HW Multi Option',
  'tooloptionMaster': 'Tool Option Master',
  'operationPlan': 'Operation Plan Check',
  'overallResult': 'Overall Crosscheck Result',
  'compareNote': 'Crosscheck Compare Note',
};

/**
 * 2. Fungsi Helper untuk Mengambil Baris Summary Result dari Backend
 */
export function getCrosscheckingResultRows(data: any): any[] {
  if (Array.isArray(data)) return data;
  const raw = getPath(data, 'SummaryResult');
  if (!raw) return [];

  if (Array.isArray(raw)) return raw;

  if (typeof raw === 'object') {
    const rows: any[] = [];
    Object.entries(raw).forEach(([key, val]) => {
      rows.push({
        moduleKey: key,
        moduleName: moduleLabelMap[key] || camelToTitle(key),
        resultValue: val
      });
    });
    return rows;
  }
  return [];
}

/**
 * 3. Fungsi Utama Render Tabel Crosschecking Result (MPX Result: OK / NG / DIFFERENT)
 */
export function renderCrosscheckingResultTable(
  containerId = 'container-crosschecking-result',
  dataOrRows: any
) {
  const container = id(containerId);
  if (!container) return;

  let rows: any[] = [];
  if (Array.isArray(dataOrRows)) {
    rows = dataOrRows;
  } else if (dataOrRows && typeof dataOrRows === 'object') {
    rows = getCrosscheckingResultRows(dataOrRows);
  }

  if (rows.length === 0) {
    container.innerHTML = '<div class="empty-state">No summary entries available.</div>';
    return;
  }

  const columns: HeaderColumn[] = [
    { label: 'Module / Item' },
    { label: 'MPX Result', className: 'status-column' },
    { label: 'Engineer Check', className: 'engineer-confirm-column' },
    { label: 'Remarks' },
  ];

  const STATUS_VALUES = ['OK', 'NG', 'CHECK', 'REVIEW', 'SAME', 'DIFFERENT', 'PASS', 'FAIL', '0', '1'];

  let tbody = '';
  rows.forEach((row, rowIndex) => {
    const moduleName = safeString(row.moduleName ?? row.name ?? row.field ?? row.Item ?? 'Unknown Item');
    const rawVal = safeString(row.resultValue ?? row.value ?? row.status ?? row.Result ?? '-');
    // Nilai status (OK/NG/...) jadi badge; teks biasa (mis. compareNote) tetap teks
    const isStatus = STATUS_VALUES.includes(rawVal.trim().toUpperCase());
    const result = isStatus ? normalizeMpxResult(rawVal) : 'OK';
    const rowStatusClass = result === 'NG' ? 'status-ng' : result === 'DIFFERENT' ? 'status-check' : '';

    tbody += `<tr class="${rowStatusClass}" data-result="${result}" data-row-index="${rowIndex}">`;
    tbody += `
      <td style="font-weight: 700;">
        <div class="cell-product">
          <i class="fa-solid fa-layer-group" style="font-size:10px; color:var(--imperial-red);"></i>
          <span class="static-cell-text" title="${escapeHtml(moduleName)}">${escapeHtml(moduleName)}</span>
        </div>
      </td>
    `;
    tbody += isStatus
      ? renderMpxResultCell(result)
      : `<td><span class="static-cell-text" title="${escapeHtml(rawVal)}">${escapeHtml(rawVal)}</span></td>`;
    tbody += renderEngineerConfirmCell(row.engineer_confirm ?? row.engineerConfirm);
    tbody += renderRemarkCell(row.remarks ?? row.Remarks ?? row.remark ?? row.Remark);
    tbody += `</tr>`;
  });

  finishTableRender(container, renderTableCard({
    resultMode: 'okng',
    rowCount: rows.length,
    columns,
    buttonsHtml: renderFilterButtons({ mode: 'okng' }),
    theadHtml: buildGroupedHeader(columns, {}),
    tbodyHtml: tbody,
  }));
}
