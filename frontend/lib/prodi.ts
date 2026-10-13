import prodiData from './prodi_mapping.json';

export type ProdiInfo = {
  nama: string;
  jenjang: string;
  mcf_wajib: boolean;
};

export type ProdiConfig = {
  version: string;
  description: string;
  mcf_required_codes: string[];
  programs: Record<string, ProdiInfo>;
};

export const PRODI_CONFIG: ProdiConfig = prodiData as ProdiConfig;

/**
 * Cek apakah sebuah program studi relevan/wajib sertifikasi MCF (contoh: 31 Informatika, 32 Sistem Informasi).
 */
export function isMcfRelevant(kodeProdi?: string | null): boolean {
  if (!kodeProdi) return false;
  const cleanCode = kodeProdi.trim();
  return PRODI_CONFIG.mcf_required_codes.includes(cleanCode);
}

/**
 * Dapatkan nama Program Studi berdasarkan Kode NIM/Prodi.
 * Jika kode terdaftar di prodi_mapping.json, kembalikan nama resmi. Jika tidak, gunakan fallback.
 */
export function getProgramStudiName(kodeProdi?: string | null, fallback?: string | null): string {
  if (!kodeProdi) return fallback || '';
  const cleanCode = kodeProdi.trim();
  return PRODI_CONFIG.programs[cleanCode]?.nama || fallback || '';
}

/**
 * Ekstraksi Kode Prodi langsung dari NIM: 2 digit setelah 4 digit tahun angkatan.
 * Contoh: 202331243 -> '31' (Informatika), 202110039 -> '10'.
 */
export function resolveKodeProdiFromNim(nim?: string | null): string {
  if (!nim) return '';
  const cleanNim = String(nim).trim();
  const digitsOnly = cleanNim.replace(/\D/g, '');
  if (digitsOnly.length >= 6) {
    return digitsOnly.substring(4, 6);
  }
  if (digitsOnly.length >= 2 && PRODI_CONFIG.programs[digitsOnly.substring(0, 2)]) {
    return digitsOnly.substring(0, 2);
  }
  return '';
}
