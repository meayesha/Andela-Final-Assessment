import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

export const metadata: Metadata = {
  title: "Todo MCP Chat",
  description: "Manage todos through natural language",
  icons: {
    icon: [{ url: "/favicon.svg", type: "image/svg+xml" }],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pk = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  return (
    <html lang="en">
      <body>
        {pk ? <ClerkProvider publishableKey={pk}>{children}</ClerkProvider> : children}
      </body>
    </html>
  );
}
