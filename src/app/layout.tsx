import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Universal AI Story-to-Video",
  description: "Agent-based story understanding and cinematic planning platform"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}

