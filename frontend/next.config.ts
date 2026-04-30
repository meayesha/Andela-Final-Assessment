import path from "node:path";
import { config as loadEnv } from "dotenv";
import type { NextConfig } from "next";

// Load repo-root `.env` so Next.js picks up NEXT_PUBLIC_* and Clerk keys during `next dev` / `next build`.
loadEnv({ path: path.resolve(__dirname, "..", ".env") });

// Docker/HF only. Never static-export on Vercel — `output: "export"` drops App Router `/api/*` handlers → 404.
const staticExport =
  process.env.STATIC_EXPORT === "true" && process.env.VERCEL !== "1";

const nextConfig: NextConfig = {
  ...(staticExport ? { output: "export" as const } : {}),
  // false: trailing slashes on /api/* break App Router route handlers on Vercel (404 on proxied routes).
  trailingSlash: false,
  images: { unoptimized: true },
  async rewrites() {
    return [{ source: "/favicon.ico", destination: "/favicon.svg" }];
  },
};

export default nextConfig;
