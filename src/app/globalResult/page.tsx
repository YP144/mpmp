import { redirect } from 'next/navigation';

interface GlobalResultPageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

/**
 * Halaman lama. Sekarang semua hasil crosscheck dibuka di /viewResult
 * (mode Edit / View only ditentukan otomatis dari pemilik BOM).
 * Link lama /globalResult?targetModel=... tetap jalan karena diteruskan ke sana.
 */
export default async function GlobalResultPage({ searchParams }: GlobalResultPageProps) {
  const params = await searchParams;
  const query = new URLSearchParams();
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (Array.isArray(value)) value.forEach(v => query.append(key, v));
    else if (value !== undefined) query.set(key, value);
  });
  const qs = query.toString();
  redirect(qs ? `/viewResult?${qs}` : '/viewResult');
}
