export interface TeamMember {
  id: number;
  name: string;
  role: string;
  region: string;
  activeProjects: string;
  status: 'Active' | 'On Leave';
  email: string;
}

export interface BomItem {
  id: number;
  partNo: string;
  name: string;
  category: string;
  tech: 'ATSC' | 'DVB' | 'OLED';
  supplier: string;
  unitCost: string;
  status: 'Approved' | 'Under Review';
}

export interface ToolItem {
  id: number;
  toolId: string;
  name: string;
  platform: 'ATSC' | 'DVB' | 'OLED';
  calibDate: string;
  location: string;
  status: 'Calibrated' | 'Pending Audit' | 'Expired';
}

export interface SummaryMatrixRow {
  tech: 'ATSC' | 'DVB' | 'OLED';
  totalBom: number;
  ng: number;
  check: number;
  noInitial: number;
  urgent: number;
  overdue: number;
  release: number;
  working: number;
  delayCount: number;
}

export type TabKey = 'team' | 'bom' | 'tool';