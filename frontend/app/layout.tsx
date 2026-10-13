import type { Metadata } from "next";
import type { ReactNode } from "react";
import { IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";

import "./globals.css";

const ibmPlexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-ibm-plex-sans",
  display: "swap",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-ibm-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ITCC Wisuda Sync",
  description: "Aplikasi internal pengelolaan data sertifikasi ITCC.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="id" className={`${ibmPlexSans.variable} ${ibmPlexMono.variable}`}>
      <body className="font-sans antialiased bg-[#F5F7F6] text-[#172321]">{children}</body>
    </html>
  );
}
