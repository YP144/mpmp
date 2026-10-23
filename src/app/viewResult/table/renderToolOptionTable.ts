import {
  id,
  setText,
  escapeHtml,
  safeString,
  camelToTitle,
  formatRawJsonValue,
  getFirstAvailablePath,
  HeaderColumn,
  renderDataCell,
  renderMpxResultCell,
  renderEngineerConfirmCell,
  renderRemarkCell,
  renderFilterButtons,
  renderTableCard,
  finishTableRender,
  refreshMergedCategoryCells
} from './tableUtils';

/**
 * 1. Fungsi Helper untuk Mengambil Objek Data Tool Option dari Backend
 */
export function getCompareToolData(data: any): any {
  const raw = getFirstAvailablePath(data, [
    'benComapre.compareTool',
    'benCompare.compareTool',
    'toolOptCompare.compareTool',
    'ToolOption.compareTool',
    'compareTool'
  ]);
  if (!raw) return {};
  if (raw.compData && typeof raw.compData === 'object' && !Array.isArray(raw.compData)) {
    return raw.compData;
  }
  return raw;
}

/** "model_tool_option" -> "Model Tool Option", "tool_option1" -> "Tool Option1" */
function toTitleCase(key: string): string {
  return camelToTitle(key).replace(/\b[a-z]/g, ch => ch.toUpperCase());
}

/** Nilai berupa object berindeks {"1": .., "2": ..} (atau string JSON-nya) -> object, selain itu null */
function parseIndexedObject(value: any): Record<string, any> | null {
  let v = value;
  if (typeof v === 'string' && v.trim().startsWith('{')) {
    try { v = JSON.parse(v); } catch (_) { return null; }
  }
  if (v && typeof v === 'object' && !Array.isArray(v) && Object.keys(v).length > 0) return v;
  return null;
}

/**
 * Baris yang nilainya object berindeks, mis. key "Tool Option":
 *   init {"1":"218240", ..., "6":"582077696"}, dev {...}, target {...}
 * dipecah menjadi 1 baris per indeks: "Tool Option 1" ... "Tool Option 6".
 * Status tiap baris pecahan dihitung ulang dari perbandingan ketiga nilainya.
 */
function expandIndexedRow(row: any): any[] {
  const init = parseIndexedObject(row?.init_value);
  const dev = parseIndexedObject(row?.dev_value);
  const target = parseIndexedObject(row?.target_value);
  if (!init && !dev && !target) return [row];

  const indexes = Array.from(new Set([
    ...Object.keys(init ?? {}),
    ...Object.keys(dev ?? {}),
    ...Object.keys(target ?? {}),
  ])).sort((a, b) => Number(a) - Number(b) || a.localeCompare(b));

  const baseKey = safeString(row.key ?? row.Key ?? row.option_key ?? 'Option');
  return indexes.map(idx => {
    const initVal = init?.[idx] ?? '-';
    const devVal = dev?.[idx] ?? '-';
    const targetVal = target?.[idx] ?? '-';
    const same = String(initVal) === String(devVal) && String(devVal) === String(targetVal);
    return {
      ...row,
      _sourceKey: baseKey,
      key: `${baseKey} ${idx}`,
      init_value: initVal,
      dev_value: devVal,
      target_value: targetVal,
      status: same ? 'SAME' : 'DIFFERENT',
      'compare note': same ? 'All sources match' : `Target: ${targetVal} | Dev: ${devVal} | Init: ${initVal}`,
    };
  });
}

/**
 * 2. Fungsi Helper: data Tool Option per kategori (sudah dipecah, siap ditampilkan)
 */
export function getToolOptionGroups(data: any): { category: string; rows: any[] }[] {
  const toolData = getCompareToolData(data);
  if (Array.isArray(toolData)) {
    return [{ category: 'General', rows: toolData.flatMap(expandIndexedRow) }];
  }
  if (!toolData || typeof toolData !== 'object') return [];

  return Object.keys(toolData)
    .filter(subKey => Array.isArray(toolData[subKey]))
    .map(subKey => ({ category: toTitleCase(subKey), rows: toolData[subKey].flatMap(expandIndexedRow) }))
    .filter(group => group.rows.length > 0);
}

/**
 * 3. Fungsi Helper untuk Mengambil Seluruh Baris Tool Option dalam Bentuk Array Datar
 * (Digunakan untuk menghitung jumlah baris pada tab title, progress bar & sidebar summary)
 */
export function getAllCompareToolRows(data: any): any[] {
  return getToolOptionGroups(data).flatMap(group => group.rows);
}

/**
 * 4. Fungsi Helper untuk Evaluasi Status Baris (SAME vs DIFFERENT)
 */
export function evaluateCompareToolRowStatus(row: any): 'SAME' | 'DIFFERENT' {
  if (!row || typeof row !== 'object') return 'SAME';

  if (row.status) {
    const st = safeString(row.status).trim().toUpperCase();
    if (st === 'DIFFERENT' || st === 'NG' || st === 'FAIL') return 'DIFFERENT';
    if (st === 'SAME' || st === 'OK' || st === 'PASS') return 'SAME';
  }

  const initial = safeString(row.init_value ?? row.initVal ?? row.Initial ?? row.initial).trim();
  const dev = safeString(row.dev_value ?? row.devVal ?? row.Development ?? row.development).trim();
  const target = safeString(row.target_value ?? row.targetVal ?? row.Target ?? row.target).trim();

  if (initial !== dev || dev !== target || initial !== target) {
    return 'DIFFERENT';
  }
  return 'SAME';
}

/**
 * 5. Fungsi Helper untuk Mengisi Kartu Info Model di Atas Tabel
 */
export function syncToolOptionInfo(data: any) {
  if (!data) return;
  setText('info-ben-model-name', safeString(data.targetName ?? data.mpModel ?? '-'));
  setText('info-ben-dev-model', safeString(data.devName ?? data.devModel ?? '-'));
  setText('info-ben-init-model', safeString(data.initName ?? data.initModel ?? '-'));
}

/* =====================================================================
 * ENGINEER CHECK: DAFTAR ITEM SPESIAL TOOL OPTION
 * ---------------------------------------------------------------------
 * Item yang terdaftar di sini:
 *   - Nilai awal Engineer Check diambil dari "prm check" backend
 *     (benComapre.compareTool.<kategori>[n]["prm check"]), huruf besar/kecil diabaikan:
 *       OK         -> OK
 *       NG         -> NG
 *       lainnya    -> Uncheck (default seperti biasa; termasuk "Uncheck", "PASS", "FAIL", kosong)
 *   - type:
 *       DD    = Dropdownable     -> dropdown, user bisa memilih OK / NG
 *       NO_DD = Not Dropdownable -> badge saja (tidak bisa diubah user)
 *   - values: kemungkinan nilai "prm check" item tsb (OK_NG atau OK_NG_UNCHECK), sebagai catatan.
 *     Uncheck TIDAK PERNAH bisa dipilih user, hanya muncul sebagai nilai awal.
 *
 * Item yang TIDAK terdaftar: seperti biasa (awal Uncheck, dropdown OK / NG).
 *
 * MENAMBAH ITEM BARU: cukup tambahkan 1 baris di ENGINEER_CHECK_SPECIAL_ITEMS.
 *   - key      : yang dipakai untuk mencocokkan adalah kata setelah 'tv.model.' / 'tv.board.'
 *                (mis. 'tv.model.pwm2Duty' -> Option Key 'pwm2Duty' di tabel)
 *   - category : 'ToolOption1'..'ToolOption6' / 'BoardOption' (angka di belakang BoardOption diabaikan)
 * ===================================================================== */
type EngineerCheckValue = 'OK' | 'NG' | 'Uncheck';

export interface EngineerCheckRule {
  category: string;
  key: string;
  values: EngineerCheckValue[];
  type: 'DD' | 'NO_DD';
}

const OK_NG: EngineerCheckValue[] = ['OK', 'NG'];
const OK_NG_UNCHECK: EngineerCheckValue[] = ['OK', 'NG', 'Uncheck'];
const DD = 'DD' as const;
const NO_DD = 'NO_DD' as const;

export const ENGINEER_CHECK_SPECIAL_ITEMS: EngineerCheckRule[] = [
  // ---------------- ToolOption1
  { category: 'ToolOption1', key: 'tv.model.moduleInchType',             values: OK_NG,         type: DD },
  { category: 'ToolOption1', key: 'tv.model.toolType',                   values: OK_NG,         type: DD },
  { category: 'ToolOption1', key: 'tv.model.moduleMakerType',            values: OK_NG,         type: DD },
  { category: 'ToolOption1', key: 'tv.model.tconPmicType',               values: OK_NG,         type: DD },
  { category: 'ToolOption1', key: 'tv.model.moduleBackLightType',        values: OK_NG,         type: DD },
  { category: 'ToolOption1', key: 'tv.model.panelLedBarType',            values: OK_NG,         type: DD },
  { category: 'ToolOption1', key: 'tv.model.adjustVCOM',                 values: OK_NG,         type: DD },
  // ---------------- ToolOption2
  { category: 'ToolOption2', key: 'tv.model.audioPwVolt',                values: OK_NG,         type: DD },
  { category: 'ToolOption2', key: 'tv.model.pwm2Duty',                   values: OK_NG,         type: DD },
  { category: 'ToolOption2', key: 'tv.model.maxPwmType',                 values: OK_NG,         type: NO_DD },
  { category: 'ToolOption2', key: 'tv.model.scanningBl',                 values: OK_NG,         type: DD },
  { category: 'ToolOption2', key: 'tv.model.bplCurrentType',             values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption2', key: 'tv.model.modeSelect',                 values: OK_NG,         type: DD },
  { category: 'ToolOption2', key: 'tv.model.eyeSensorLEDGain',           values: OK_NG,         type: NO_DD },
  { category: 'ToolOption2', key: 'tv.model.standardBacklight',          values: OK_NG,         type: NO_DD },
  { category: 'ToolOption2', key: 'tv.model.vividSportsBacklight',       values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption2', key: 'tv.model.hdrDefaultBacklight',        values: OK_NG_UNCHECK, type: DD },
  // ---------------- ToolOption3
  { category: 'ToolOption3', key: 'tv.model.panelGamutType',             values: OK_NG,         type: DD },
  { category: 'ToolOption3', key: 'tv.model.motionProMode',              values: OK_NG,         type: DD },
  { category: 'ToolOption3', key: 'tv.model.supportDolbyVisionHDR',      values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption3', key: 'tv.model.ampChipType',                values: OK_NG,         type: DD },
  { category: 'ToolOption3', key: 'tv.model.audioSpkWatt',               values: OK_NG,         type: DD },
  { category: 'ToolOption3', key: 'tv.model.supportLuminanceUp',         values: OK_NG,         type: NO_DD },
  { category: 'ToolOption3', key: 'tv.model.supportVRR',                 values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption3', key: 'tv.model.supportFreesync',            values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption3', key: 'tv.model.aiSoundType',                values: OK_NG,         type: DD },
  { category: 'ToolOption3', key: 'tv.model.dolbyVisionPrecisionDetail', values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption3', key: 'tv.model.pwmFreqDouble',              values: OK_NG,         type: DD },
  { category: 'ToolOption3', key: 'tv.model.motionBooster',              values: OK_NG,         type: DD },
  { category: 'ToolOption3', key: 'tv.model.DPCType',                    values: OK_NG,         type: DD },
  { category: 'ToolOption3', key: 'tv.model.supportFreesyncPro',         values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption3', key: 'tv.model.supportHDRPlus',             values: OK_NG_UNCHECK, type: DD },
  // ---------------- ToolOption4
  { category: 'ToolOption4', key: 'tv.model.logoLight',                  values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportFanControl',          values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.cameraType',                 values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportWol',                 values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.hdmiSwitchType',             values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportMovingSpeaker',       values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportIRBlaster',           values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportMirrorMode',          values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportScreenRollerMotor',   values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportMotionDetectSensor',  values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportLCDScreenCooling',    values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportLAN',                 values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.specialEditionType',         values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportOpticalJack',         values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportFarFieldVoice',       values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.supportTypecCtric',          values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.AiArtExtension',             values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.boardDesign',                values: OK_NG,         type: DD },
  { category: 'ToolOption4', key: 'tv.model.emmcDensityAutoExtension',   values: OK_NG,         type: DD },
  // ---------------- ToolOption5
  { category: 'ToolOption5', key: 'tv.model.videoIndex',                 values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption5', key: 'tv.model.audioIndex',                 values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption5', key: 'tv.model.maxInputNumberUsb',          values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption5', key: 'tv.model.usb1',                       values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption5', key: 'tv.model.usb2',                       values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption5', key: 'tv.model.usb3',                       values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption5', key: 'tv.model.supportHeadPhone',           values: OK_NG,         type: NO_DD },
  { category: 'ToolOption5', key: 'tv.model.supportCiAp',                values: OK_NG,         type: NO_DD },
  { category: 'ToolOption5', key: 'tv.model.supportDtcpKey',             values: OK_NG,         type: NO_DD },
  { category: 'ToolOption5', key: 'tv.model.supportMacAp',               values: OK_NG,         type: DD },
  { category: 'ToolOption5', key: 'tv.model.supportEsnAp',               values: OK_NG,         type: DD },
  { category: 'ToolOption5', key: 'tv.model.supportWidevineAp',          values: OK_NG,         type: DD },
  { category: 'ToolOption5', key: 'tv.model.supportCiEcpAp',             values: OK_NG,         type: NO_DD },
  { category: 'ToolOption5', key: 'tv.model.supportUhdcpKey',            values: OK_NG,         type: NO_DD },
  { category: 'ToolOption5', key: 'tv.model.supportNewErP',              values: OK_NG,         type: NO_DD },
  { category: 'ToolOption5', key: 'tv.model.oledCPC',                    values: OK_NG,         type: NO_DD },
  { category: 'ToolOption5', key: 'tv.model.PDCharge',                   values: OK_NG,         type: DD },
  // ---------------- ToolOption6
  { category: 'ToolOption6', key: 'tv.model.digitalEye',                 values: OK_NG,         type: DD },
  { category: 'ToolOption6', key: 'tv.model.supportEpa',                 values: OK_NG,         type: NO_DD },
  { category: 'ToolOption6', key: 'tv.model.adaptDimDefault',            values: OK_NG,         type: NO_DD },
  { category: 'ToolOption6', key: 'tv.model.motionEyeCareIndex',         values: OK_NG,         type: NO_DD },
  { category: 'ToolOption6', key: 'tv.model.defaultStdBacklight',        values: OK_NG,         type: NO_DD },
  { category: 'ToolOption6', key: 'tv.model.soundModeType',              values: OK_NG_UNCHECK, type: DD },
  { category: 'ToolOption6', key: 'tv.model.supportIsf',                 values: OK_NG,         type: DD },
  { category: 'ToolOption6', key: 'tv.model.supportTvLink',              values: OK_NG,         type: DD },
  { category: 'ToolOption6', key: 'tv.model.supportCalmanSW',            values: OK_NG,         type: DD },
  { category: 'ToolOption6', key: 'tv.model.supportDvrReady',            values: OK_NG,         type: NO_DD },
  { category: 'ToolOption6', key: 'tv.model.supportAudioLineOut',        values: OK_NG,         type: DD },
  { category: 'ToolOption6', key: 'tv.model.wifiType',                   values: OK_NG,         type: DD },
  { category: 'ToolOption6', key: 'tv.model.wifiMacType',                values: OK_NG,         type: DD },
  { category: 'ToolOption6', key: 'tv.model.motionRemoconType',          values: OK_NG,         type: DD },
  { category: 'ToolOption6', key: 'tv.model.eyeCurveDerivation',         values: OK_NG,         type: DD },
  { category: 'ToolOption6', key: 'tv.model.edidType',                   values: OK_NG,         type: DD },
  // ---------------- BoardOption1 (di JSON kategori: board_option)
  { category: 'BoardOption1', key: 'tv.board.panelType',                 values: OK_NG,         type: DD },
  { category: 'BoardOption1', key: 'tv.board.panelInterface',            values: OK_NG,         type: DD },
  { category: 'BoardOption1', key: 'tv.board.panelResolution',           values: OK_NG,         type: DD },
  { category: 'BoardOption1', key: 'tv.board.panelMaxFrameRate',         values: OK_NG,         type: DD },
  { category: 'BoardOption1', key: 'tv.board.panelMaxBitRate',           values: OK_NG,         type: DD },
  { category: 'BoardOption1', key: 'tv.board.panelDivisionType',         values: OK_NG,         type: DD },
  { category: 'BoardOption1', key: 'tv.board.externalFrcType',           values: OK_NG,         type: DD },
  { category: 'BoardOption1', key: 'tv.board.ddrSize',                   values: OK_NG,         type: DD },
  { category: 'BoardOption1', key: 'tv.board.countryType',               values: OK_NG,         type: NO_DD },
  { category: 'BoardOption1', key: 'tv.board.tunerType',                 values: OK_NG,         type: NO_DD },
  { category: 'BoardOption1', key: 'tv.board.micomLocalKeyType',         values: OK_NG,         type: DD },
  // ---------------- BoardOption2 (di JSON kategori: board_option)
  { category: 'BoardOption2', key: 'tv.board.arRlOnControl',             values: OK_NG,         type: DD },
  { category: 'BoardOption2', key: 'tv.board.irLedControl',              values: OK_NG,         type: DD },
  { category: 'BoardOption2', key: 'tv.board.modelType',                 values: OK_NG,         type: DD },
  { category: 'BoardOption2', key: 'tv.board.weeTurnkeyVersion',         values: OK_NG,         type: DD },
  { category: 'BoardOption2', key: 'tv.board.pmicType',                  values: OK_NG,         type: DD },
];

/** 'tv.model.adjustVCOM' -> 'adjustvcom', 'Tool_Option1' -> 'tooloption1' */
function normalizeRuleText(value: string): string {
  return String(value ?? '').trim().replace(/^tv\.(model|board)\./i, '').toLowerCase().replace(/[^a-z0-9]/g, '');
}

/** Kategori untuk dicocokkan: 'BoardOption1' / 'BoardOption2' / 'board_option' -> 'boardoption' */
function normalizeRuleCategory(value: string): string {
  const cat = normalizeRuleText(value);
  return cat.startsWith('boardoption') ? 'boardoption' : cat;
}

/**
 * Cari aturan Engineer Check untuk satu baris.
 * Yang utama adalah Option Key (kata setelah 'tv.model.' / 'tv.board.').
 * Kalau ada beberapa aturan dengan key yang sama, dipilih yang kategorinya juga sama.
 */
export function findEngineerCheckRule(category: string, key: string): EngineerCheckRule | undefined {
  const k = normalizeRuleText(key);
  const sameKey = ENGINEER_CHECK_SPECIAL_ITEMS.filter(rule => normalizeRuleText(rule.key) === k);
  if (sameKey.length <= 1) return sameKey[0];

  const cat = normalizeRuleCategory(category);
  return sameKey.find(rule => normalizeRuleCategory(rule.category) === cat);
}

/** Nilai "prm check" backend -> OK / NG, selain itu Uncheck (default seperti biasa) */
export function prmCheckToEngineerValue(prmCheck: any): EngineerCheckValue {
  const v = String(prmCheck ?? '').trim().toUpperCase();
  if (v === 'OK') return 'OK';
  if (v === 'NG') return 'NG';
  return 'Uncheck';
}

/**
 * Sel Engineer Check Tool Option.
 * - Item tidak terdaftar : dropdown biasa (awal Uncheck, pilihan OK / NG)
 * - Item terdaftar DD    : dropdown, awal dari prm check, pilihan OK / NG (Uncheck hanya nilai awal)
 * - Item terdaftar NO_DD : badge read-only berisi nilai dari prm check
 */
function renderToolOptionEngineerCheckCell(category: string, row: any, cellClass: string): string {
  const optionKey = safeString(row?.key ?? row?.Key ?? row?.option_key ?? '');
  // Baris pecahan "Tool Option 1..6" memakai aturan key aslinya ("Tool Option")
  const rule = findEngineerCheckRule(category, row?._sourceKey ?? optionKey);

  if (!rule) {
    return renderEngineerConfirmCell(row?.engineer_confirm ?? row?.engineerConfirm, cellClass);
  }

  const value = prmCheckToEngineerValue(row?.['prm check'] ?? row?.prm_check ?? row?.prmCheck);
  const colorClass = value === 'OK' ? 'eng-ok' : value === 'NG' ? 'eng-ng' : 'eng-uncheck';

  if (rule.type === NO_DD) {
    return `
    <td class="engineer-confirm-column ${cellClass}">
      <span class="engineer-check-readonly ${colorClass}" data-value="${value}" title="Engineer Check otomatis dari PRM check (tidak bisa diubah)">${value}</span>
    </td>`;
  }

  // Pilihan user selalu OK / NG. Uncheck hanya nilai awal (placeholder tersembunyi, tidak bisa dipilih)
  const options = (['OK', 'NG'] as EngineerCheckValue[]).map(opt =>
    `<option value="${opt}" ${opt === value ? 'selected' : ''}>${opt}</option>`
  ).join('');
  const placeholder = value === 'Uncheck'
    ? '<option value="Uncheck" disabled selected hidden>Uncheck</option>'
    : '';

  return `
    <td class="engineer-confirm-column ${cellClass}">
      <select class="engineer-confirm-select ${colorClass}" onchange="window.updateEngineerConfirmStyle(this)">
        ${placeholder}${options}
      </select>
    </td>`;
}

/**
 * 6. Fungsi Utama Render Tabel Tool Option
 *
 * || Category / Section | Option Key || Initial Model || Development Model || Target Model (MP) || JIRA Power Cons || MPX Result | Engineer Check | Remarks ||
 *
 * - Category / Section & Option Key            : freeze di kiri
 * - MPX Result, Engineer Check, Remarks      : freeze di kanan
 * - Header 2 baris freeze di atas (baris 2 = nama model TV / nomor JIRA)
 * - Sel Category di-merge per kategori (diatur refreshMergedCategoryCells di tableUtils.ts,
 *   dihitung ulang setiap kali tabel difilter)
 */
export function renderToolOptionTable(
  containerId = 'container-ben-compare-tool',
  data: any
) {
  const container = id(containerId);
  if (!container) return;

  if (!data) {
    container.innerHTML = '<div class="empty-state">No compareTool data loaded.</div>';
    return;
  }

  // Sinkronkan info chip di atas tabel
  syncToolOptionInfo(data);

  const groups = getToolOptionGroups(data);
  const totalRows = groups.reduce((sum, g) => sum + g.rows.length, 0);
  if (totalRows === 0) {
    container.innerHTML = '<div class="empty-state">No compareTool data entries available.</div>';
    return;
  }

  const initModel = safeString(data?.initName ?? data?.initialModel ?? '-');
  const devModel = safeString(data?.devName ?? data?.devModel ?? '-');
  const mpModel = safeString(data?.targetName ?? data?.mpModel ?? '-');
  // Nomor JIRA Power Cons: belum ada dari backend (key rencana: jira_power_cons)
  const jiraNumber = safeString(data?.jira_power_cons ?? data?.jiraPowerCons ?? '-');
  // Link halaman JIRA Power Cons. dari Crosscheck Configuration (drawer My BOM)
  const jiraLink = safeString(data?.jiraPowerConsLink ?? '').trim();
  const jiraHeaderHtml = /^https?:\/\//i.test(jiraLink)
    ? `<a class="hdr-link" href="${escapeHtml(jiraLink)}" target="_blank" rel="noopener noreferrer" title="Open JIRA Power Cons. page">${escapeHtml(jiraNumber === '-' ? 'Open Page' : jiraNumber)} <i class="fa-solid fa-arrow-up-right-from-square"></i></a>`
    : escapeHtml(jiraNumber);

  // Tombol filter kategori dinamis
  const categoryFilterButtonsHtml = groups.map(g => `
    <button class="table-status-counter" onclick="window.filterCompareToolSection(this, '${escapeHtml(g.category)}')">
      <i class="fa-solid fa-toolbox"></i> ${escapeHtml(g.category)}
    </button>
  `).join('');

  // Daftar kolom (urutan sama dengan <td> di tbody)
  const columns: HeaderColumn[] = [
    { label: 'Category / Section' },
    { label: 'Option Key' },
    { label: 'Initial Model' },
    { label: 'Development Model' },
    { label: 'Target Model (MP)' },
    { label: 'JIRA Power Cons' },
    { label: 'MPX Result' },
    { label: 'Engineer Check' },
    { label: 'Remarks' },
  ];

  // ---------------- HEADER (2 baris, freeze di atas)
  const thead = `
    <tr>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-left fl-1" rowspan="2">Category / Section</th>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-left freeze-left-edge fl-2 thick-right" rowspan="2">Option Key</th>
      <th class="hdr-r1 hdr-banner grp-c1 col-value thick-right">Initial Model</th>
      <th class="hdr-r1 hdr-banner grp-c2 col-value thick-right">Development Model</th>
      <th class="hdr-r1 hdr-banner grp-c3 col-value thick-right">Target Model (MP)</th>
      <th class="hdr-r1 hdr-banner grp-fixed col-value no-right-border">JIRA Power Cons</th>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-right freeze-right-edge fr-3 thick-left" rowspan="2">MPX Result</th>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-right fr-2" rowspan="2">Engineer Check</th>
      <th class="hdr-r1 hdr-banner grp-fixed freeze-right fr-1" rowspan="2">Remarks</th>
    </tr>
    <tr>
      <th class="hdr-r2 hdr-name grp-c1 thick-right">${escapeHtml(initModel)}</th>
      <th class="hdr-r2 hdr-name grp-c2 thick-right">${escapeHtml(devModel)}</th>
      <th class="hdr-r2 hdr-name grp-c3 thick-right">${escapeHtml(mpModel)}</th>
      <th class="hdr-r2 hdr-name grp-fixed no-right-border">${jiraHeaderHtml}</th>
    </tr>
  `;

  // ---------------- BODY
  const valueCell = (val: any, cls: string) => {
    const text = formatRawJsonValue(val);
    return `<td class="col-value ${cls}"><span class="static-cell-text" title="${escapeHtml(text)}">${escapeHtml(text)}</span></td>`;
  };

  let tbody = '';
  let rowIndex = 0;
  groups.forEach(({ category, rows }) => {
    rows.forEach(row => {
      const rowResult = evaluateCompareToolRowStatus(row);

      tbody += `<tr class="${rowResult === 'DIFFERENT' ? 'status-ng' : ''}" data-result="${rowResult}" data-category="${escapeHtml(category)}" data-row-index="${rowIndex}">`;
      // Sel Category ada di setiap baris; merge (rowspan) diatur refreshMergedCategoryCells
      tbody += `<td class="merge-cell cell-category freeze-left fl-1"><span class="static-cell-text" title="${escapeHtml(category)}">${escapeHtml(category)}</span></td>`;
      tbody += renderDataCell(row.key ?? row.Key ?? row.option_key, false, 'cell-option-key freeze-left freeze-left-edge fl-2 thick-right');
      tbody += valueCell(row.init_value ?? row.initVal ?? row.Initial ?? '-', 'thick-right');
      tbody += valueCell(row.dev_value ?? row.devVal ?? row.Development ?? '-', 'thick-right');
      tbody += valueCell(row.target_value ?? row.targetVal ?? row.Target ?? '-', 'thick-right');
      // JIRA Power Cons per baris: belum ada dari backend (key rencana: jira_power_cons)
      tbody += valueCell(row.jira_power_cons ?? '-', 'no-right-border');
      tbody += renderMpxResultCell(rowResult, 'samediff', 'freeze-right freeze-right-edge fr-3 thick-left');
      // Engineer Check: tipe & nilai awal mengikuti ENGINEER_CHECK_SPECIAL_ITEMS (lihat di atas)
      tbody += renderToolOptionEngineerCheckCell(category, row, 'freeze-right fr-2');
      tbody += renderRemarkCell(row['compare note'] ?? row.compare_note ?? row.remark ?? row.remarks, 'freeze-right fr-1');
      tbody += `</tr>`;
      rowIndex++;
    });
  });

  finishTableRender(container, renderTableCard({
    resultMode: 'samediff',
    rowCount: totalRows,
    columns,
    buttonsHtml: renderFilterButtons({ mode: 'samediff', extraButtons: categoryFilterButtonsHtml }),
    theadHtml: thead,
    tbodyHtml: tbody,
    tableClass: 'freeze-table tooloption-table',
    wrapperClass: 'freeze-wrapper',
    cardClass: 'fw-tooloption',
  }));

  refreshMergedCategoryCells(container);
}
