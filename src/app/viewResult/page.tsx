import { Suspense } from 'react';
import ViewResultClient from './ViewResultClient';
import { getViewResultAccess } from '@/lib/bomAccessServer';

interface ViewResultPageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

/**
 * Halaman hasil crosscheck (satu-satunya, dibuka dari My BOM maupun Global Overview).
 * Mode ditentukan di server dari user yang login, bukan dari URL:
 *   - pemilik BOM (PIC Circuit) atau user khusus -> Edit mode
 *   - selain itu                                 -> View only
 */
export default async function Page({ searchParams }: ViewResultPageProps) {
  const params = await searchParams;
  const rawTarget = params?.targetModel;
  const targetModel = (Array.isArray(rawTarget) ? rawTarget[0] : rawTarget ?? '').trim();

  const access = await getViewResultAccess(targetModel);

  return (
    <Suspense fallback={<div className="global-loading-overlay show">Loading workspace...</div>}>
      <ViewResultClient canEdit={access.canEdit} userName={access.userName} bomConfig={access.bomConfig} />
    </Suspense>
  );
}
