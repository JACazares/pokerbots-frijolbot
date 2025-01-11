// app/layout.tsx
import "./globals.css";
import React from "react";
import Navbar from "./navbar";
import type { Metadata } from "next";

// You can define site-wide meta here
export const metadata: Metadata = {
  title: "My Poker App",
  description: "Next.js 13 + TypeScript Poker Parser Viewer",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}