'use server';

import { Pool } from 'pg';
import poolUser from '@/lib/postgres_user';
import poolAuto from '@/lib/postgres_auto';
import { getSsoSession } from '@/lib/sso';

export interface DynamicTableResponse {
  columns: string[];
  rows: Record<string, any>[];
}

export interface ProductionItem {
  "No."?: number;
  "Work Order"?: string;
  "Plan Qty"?: string;
  "Event"?: string;
  "Model.Suffix"?: string;
  "Production Site"?: string;
  "Country"?: string;
  "Date"?: string;
  "TV Group"?: string;
  "HQ Model"?: string | null;
  "Status"?: string | null;
  [key: string]: any;
}

// Pool instance connecting to MasterMP_Data summary_team database
const poolSummaryTeam = new Pool({
  connectionString:
    'postgresql://mybini-user:vzS3Bo0K8Bx2DcHQPd0zIpkiEhjDcZKJ8vyTqHPcwF796dMbYF0m4dFaedWAxWIN@mybini-0.mybini.postgres.svc:5432/MasterMP_Data',
});

/**
 * Fetch HW Dynamic Summary Matrix from 'summary_team'
 */
export async function fetchSummaryTeam(): Promise<DynamicTableResponse> {
  try {
    const result = await poolSummaryTeam.query('SELECT * FROM summary_team ORDER BY 1 ASC');

    if (!result || result.rows.length === 0) {
      return { columns: [], rows: [] };
    }

    const columns = result.fields.map((field) => field.name);

    return {
      columns,
      rows: result.rows,
    };
  } catch (error) {
    console.error('Failed to fetch summary_team from database:', error);
    return { columns: [], rows: [] };
  }
}

/**
 * Fetch HW Team Members from 'summary_user' in MasterMP_Data
 */
export async function fetchTeamMembers(): Promise<DynamicTableResponse> {
  try {
    const result = await poolUser.query('SELECT * FROM summary_user ORDER BY 1 ASC');

    if (!result || result.rows.length === 0) {
      return { columns: [], rows: [] };
    }

    const columns = result.fields.map((field: { name: string }) => field.name);

    return {
      columns,
      rows: result.rows,
    };
  } catch (error) {
    console.error('Failed to fetch summary_user from MasterMP_Data:', error);
    return { columns: [], rows: [] };
  }
}

/**
 * Fetch Master MP BOM items from 'resultmain' in MasterMP_Auto
 */
export async function fetchBomItems(): Promise<DynamicTableResponse> {
  try {
    const result = await poolAuto.query('SELECT * FROM resultmain ORDER BY 1 ASC');

    if (!result || result.rows.length === 0) {
      return { columns: [], rows: [] };
    }

    const columns = result.fields.map((field: { name: string }) => field.name);

    return {
      columns,
      rows: result.rows,
    };
  } catch (error) {
    console.error('Failed to fetch resultmain from MasterMP_Auto:', error);
    return { columns: [], rows: [] };
  }
}

/**
 * Trigger FastAPI call to fetch Production Data using current SSO session
 */
export async function fetchProductionData(): Promise<{ success: boolean; data?: ProductionItem[]; error?: string }> {
  try {
    const ssoSession = await getSsoSession();

    if (!ssoSession.success) {
      console.warn('SSO session missing or invalid during fetchProductionData:', ssoSession.error);
    }

    const fastApiUrl = process.env.FASTAPI_BACKEND_URL || 'http://localhost:8000';

    const payload = {
      process: "production_pull",
      datetime: new Date().toISOString(),
      userId: ssoSession.userId || "",
      userIc: ssoSession.userIc || "",
      ssolgenet_cookie: ssoSession.ssolgenet || "",
      smsession_cookie: ssoSession.smsession || ""
    };

    const response = await fetch(`${fastApiUrl}/api/bom/get_production`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`FastAPI request failed with status: ${response.status}`);
    }

    const productionData: ProductionItem[] = await response.json();
    return { success: true, data: productionData };
  } catch (error: any) {
    console.error('Error fetching production data from FastAPI:', error);
    return { success: false, error: error?.message || 'Failed to connect to FastAPI backend' };
  }
}