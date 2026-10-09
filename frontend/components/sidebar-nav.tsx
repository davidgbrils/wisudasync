"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Ringkasan" },
  { href: "/sinkronisasi", label: "Validasi Wisuda" },
  { href: "/riwayat", label: "Riwayat Sinkronisasi" },
  { href: "/sitasi", label: "Data SITASI" },
  { href: "/certiport", label: "Data Certiport" },
];

export default function SidebarNav({ orientation }: { orientation: "vertical" | "horizontal" }) {
  const pathname = usePathname();
  const horizontal = orientation === "horizontal";

  return (
    <nav aria-label="Navigasi utama" className={horizontal ? "flex gap-2 overflow-x-auto" : "space-y-1"}>
      {links.map((link) => {
        const active = pathname === link.href;
        return <Link
          key={link.href}
          href={link.href}
          aria-current={active ? "page" : undefined}
          className={`${horizontal ? "min-h-11 shrink-0 px-3" : "min-h-11 w-full px-3"} inline-flex items-center rounded-md text-sm font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 ${active ? "bg-teal-50 text-teal-900" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"}`}
        >{link.label}</Link>;
      })}
    </nav>
  );
}
