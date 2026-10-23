// src/lib/urlState.ts
// Menyimpan posisi halaman (menu sidebar, tab, drawer) di URL tanpa reload.
// Pakai window.history.pushState / replaceState: address bar berubah, tapi TIDAK ada request ke server,
// jadi perpindahan menu tetap instan. Next.js menyinkronkan perubahan ini ke useSearchParams().
// Hasilnya: refresh browser kembali ke posisi terakhir, dan URL bisa di-copy untuk dibagikan.

export type UrlParamUpdates = Record<string, string | null | undefined>;

export interface UpdateUrlOptions {
  // 'push'    = tambah riwayat baru (tombol Back browser kembali ke posisi sebelumnya), dipakai untuk pindah menu
  // 'replace' = ganti riwayat saat ini (tidak menambah riwayat), dipakai untuk tab & drawer
  mode?: 'push' | 'replace';
  // Hapus semua parameter lain sebelum menerapkan updates (dipakai saat pindah menu,
  // supaya parameter milik halaman sebelumnya seperti ?model= / ?tab= tidak terbawa)
  clearOthers?: boolean;
}

/** Ubah parameter URL. Nilai null / undefined / '' = parameter dihapus. */
export function updateUrlParams(updates: UrlParamUpdates, options: UpdateUrlOptions = {}) {
  if (typeof window === 'undefined') return;
  const { mode = 'replace', clearOthers = false } = options;

  const params = clearOthers ? new URLSearchParams() : new URLSearchParams(window.location.search);
  Object.entries(updates).forEach(([key, value]) => {
    if (value === null || value === undefined || value === '') params.delete(key);
    else params.set(key, value);
  });

  const query = params.toString();
  const nextUrl = `${window.location.pathname}${query ? `?${query}` : ''}${window.location.hash}`;
  const currentUrl = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  if (nextUrl === currentUrl) return;

  if (mode === 'push') window.history.pushState(null, '', nextUrl);
  else window.history.replaceState(null, '', nextUrl);
}
