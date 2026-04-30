import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Todo MCP Chat",
  description: "Manage todos through natural language",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
