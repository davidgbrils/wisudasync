"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/sinkronisasi", label: "Validasi Wisuda", icon: "/brand/icon-wisuda.png" },
  { href: "/dashboard", label: "Ringkasan Master", icon: "/brand/icon-laporan.png" },
  { href: "/riwayat", label: "Riwayat Sinkronisasi", icon: "/brand/icon-sinkronisasi.png" },
  { href: "/sitasi", label: "Data SITASI", icon: "/brand/icon-sitasi.png" },
  { href: "/certiport", label: "Data Certiport", icon: "/brand/icon-certiport.png" },
];

export default function SidebarNav({
  orientation,
  onNavigate,
}: {
  orientation: "vertical" | "horizontal";
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const horizontal = orientation === "horizontal";

  return (
    <nav aria-label="Navigasi utama" className={horizontal ? "flex gap-2 overflow-x-auto pb-1" : "space-y-1.5"}>
      {links.map((link) => {
        const active = pathname === link.href || (link.href !== "/dashboard" && pathname.startsWith(link.href));
        return (
          <Link
            key={link.href}
            href={link.href}
            onClick={onNavigate}
            aria-current={active ? "page" : undefined}
            className={`${
              horizontal
                ? `min-h-11 shrink-0 px-3.5 border-b-2 ${
                    active
                      ? "border-[#0F766E] bg-[#ECFAF8] text-[#0F4B46] font-semibold"
                      : "border-transparent text-[#66736F] hover:bg-[#F5F7F6] hover:text-[#172321]"
                  }`
                : `min-h-11 w-full px-3.5 border-l-[3px] ${
                    active
                      ? "border-[#0F766E] bg-[#ECFAF8] text-[#0F4B46] font-semibold shadow-xs"
                      : "border-transparent text-[#66736F] hover:bg-[#F5F7F6] hover:text-[#172321]"
                  }`
            } inline-flex items-center gap-3 rounded-r-lg text-xs sm:text-sm font-medium transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]`}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={link.icon} alt="" width={20} height={20} className="h-5 w-5 shrink-0 object-contain" />
            <span className="truncate">{link.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
