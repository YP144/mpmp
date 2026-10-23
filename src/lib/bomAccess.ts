// src/lib/bomAccess.ts
// Aturan akses BOM (dipakai halaman My BOM dan halaman View Result).
// File ini aman di-import dari client maupun server (tidak memakai cookie / database).

/**
 * User khusus:
 * - di My BOM melihat SEMUA BOM (bukan hanya BOM miliknya)
 * - di View Result boleh EDIT semua BOM (Engineer Check, Remarks, Save Draft, Engineer Confirm)
 * Tulis nama persis seperti nama user dari SSO (huruf besar / kecil tidak berpengaruh).
 */
export const SPECIAL_USERS: string[] = [
  'YUDHISTIRA RANGGAWIDJAYA',
  'YOSEP PUTRA SETIYANTO',
  'AHMAD IFANDI',
  'KIM SEUNGHO',
];

function normalizeUserName(name: string | null | undefined): string {
  return (name ?? '').trim().replace(/\s+/g, ' ').toUpperCase();
}

/** true kalau user termasuk SPECIAL_USERS */
export function isSpecialUser(userName: string | null | undefined): boolean {
  const name = normalizeUserName(userName);
  return name !== '' && SPECIAL_USERS.some(u => normalizeUserName(u) === name);
}

/**
 * true kalau user adalah pemilik BOM, yaitu namanya tercantum di kolom PIC Circuit (model_circuit_pic).
 * Kolom PIC bisa berisi lebih dari satu nama, jadi dicocokkan per kata utuh.
 */
export function isBomOwner(userName: string | null | undefined, modelCircuitPic: string | null | undefined): boolean {
  const name = (userName ?? '').trim();
  if (!name) return false;
  const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`\\b${escapedName}\\b`, 'i');
  return regex.test(modelCircuitPic ?? '');
}

/** true kalau user boleh mengedit hasil crosscheck BOM ini (pemilik BOM atau user khusus) */
export function canEditBom(userName: string | null | undefined, modelCircuitPic: string | null | undefined): boolean {
  return isSpecialUser(userName) || isBomOwner(userName, modelCircuitPic);
}
