import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Genvicure Treasury MIS",
  description: "Genvicure Treasury Management Information System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}