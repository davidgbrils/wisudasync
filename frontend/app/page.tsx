import { redirect } from "next/navigation";

export default function RootPage() {
  // Landing page dihapus: rute utama langsung menuju halaman validasi data wisuda
  redirect("/sinkronisasi");
}
