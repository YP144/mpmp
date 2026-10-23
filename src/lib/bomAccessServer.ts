// src/lib/bomAccessServer.ts
// Menentukan mode halaman View Result (Edit / View Only) di SERVER.
// Hanya boleh di-import dari server component (memakai cookie SSO & database).

import pool from './postgres';
import { getSsoSession } from './sso';
import { canEditBom } from './bomAccess';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';

/**
 * Crosscheck Configuration dari tabel resultmain (diatur di drawer My BOM).
 * Dipakai halaman View Result untuk nama model TV di header tabel & link JIRA Power Cons.
 */
export interface BomCrosscheckConfig {
  devModel: string;
  initialModel: string;
  initialRegion: string;
  jiraPowerConsLink: string;
}

export interface ViewResultAccess {
  canEdit: boolean;
  userName: string | null;
  bomPic: string | null;
  bomConfig: BomCrosscheckConfig | null;
}

/** Nama user yang sedang login (alur sama dengan halaman dashboard: SSO -> FastAPI /api/authentication) */
async function getCurrentUserName(): Promise<string | null> {
  const ssoSession: any = await getSsoSession();
  if (!ssoSession?.success) return null;

  const response = await fetch(`${FASTAPI_URL}/api/authentication`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({
      userId: ssoSession.userId,
      userIc: ssoSession.userIc,
      authBearer: ssoSession.authBearer || '',
      smsession: ssoSession.smsession || '',
      ssolgenet: ssoSession.ssolgenet || '',
    }),
    cache: 'no-store',
    signal: AbortSignal.timeout(15000),
  });
  if (!response.ok) return null;

  const authResult = await response.json();
  const userName = typeof authResult?.userName === 'string' ? authResult.userName.trim() : '';
  return userName || null;
}

const text = (value: any) => (value === undefined || value === null ? '' : String(value).trim());

/**
 * Data BOM dari tabel resultmain (bisa lebih dari 1 baris untuk model yang sama):
 * - PIC Circuit (gabungan semua baris) untuk menentukan Edit / View only
 * - Crosscheck Configuration (baris pertama yang terisi)
 */
async function getBomInfo(targetModel: string): Promise<{ pic: string | null; config: BomCrosscheckConfig | null }> {
  const result = await pool.query('SELECT * FROM resultmain WHERE "mp model" = $1', [targetModel]);
  const rows: any[] = result.rows;
  if (rows.length === 0) return { pic: null, config: null };

  const pics = rows.map(row => text(row.model_circuit_pic ?? row['model circuit pic'])).filter(Boolean);
  const firstFilled = (getter: (row: any) => any) => rows.map(r => text(getter(r))).find(Boolean) ?? '';

  return {
    pic: pics.length > 0 ? pics.join(', ') : null,
    config: {
      devModel: firstFilled(r => r['dev model'] ?? r.dev_model),
      initialModel: firstFilled(r => r['initial model'] ?? r.initial_model),
      initialRegion: firstFilled(r => r['initial region'] ?? r.initial_region),
      jiraPowerConsLink: firstFilled(r => r['jira power cons link'] ?? r.jira_power_cons_link),
    },
  };
}

/**
 * Edit mode  : user adalah PIC Circuit BOM ini, atau termasuk user khusus (SPECIAL_USERS)
 * View only  : selain itu, termasuk kalau terjadi error (SSO / backend / database tidak bisa diakses)
 * Fungsi ini tidak pernah throw, supaya halaman tetap bisa dibuka.
 */
export async function getViewResultAccess(targetModel: string): Promise<ViewResultAccess> {
  let userName: string | null = null;
  let bomPic: string | null = null;
  let bomConfig: BomCrosscheckConfig | null = null;

  try {
    userName = await getCurrentUserName();
  } catch (error) {
    console.error('[VIEW RESULT] Gagal membaca user login, halaman dibuka View Only:', error);
  }

  if (targetModel) {
    try {
      const bomInfo = await getBomInfo(targetModel);
      bomPic = bomInfo.pic;
      bomConfig = bomInfo.config;
    } catch (error) {
      console.error('[VIEW RESULT] Gagal membaca data BOM (PIC Circuit / Crosscheck Configuration), halaman dibuka View Only:', error);
    }
  }

  const canEdit = canEditBom(userName, bomPic);
  console.log('[VIEW RESULT] Access:', { targetModel, userName, bomPic, canEdit });

  return { canEdit, userName, bomPic, bomConfig };
}
