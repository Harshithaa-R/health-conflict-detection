import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "HealthSync | Karnataka Health Conflict Review",
  description: "Review multi-source health record conflicts and risk summaries.",
};

export default function RootLayout({children}: Readonly<{children: ReactNode}>) {
  return <html lang="en"><body>{children}</body></html>;
}
