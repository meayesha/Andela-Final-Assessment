import path from "node:path";
import { config as loadEnv } from "dotenv";
import type { NextConfig } from "next";

// Load repo-root `.env` so Next.js picks up NEXT_PUBLIC_* and Clerk keys during `next dev` / `next build`.
loadEnv({ path: path.resolve(__dirname, "..", ".env") });

const staticExport = process.env.STATIC_EXPORT === "true";
const apiProxyOrigin = (process.env.API_PROXY_ORIGIN || "").trim().replace(/\/$/, "");

const nextConfig: NextConfig = {
  ...(staticExport ? { output: "export" as const } : {}),
  trailingSlash: true,
  images: { unoptimized: true },
  env: {
    // So the client can hide the "set NEXT_PUBLIC_API_URL" banner when only API_PROXY_ORIGIN is used.
    NEXT_PUBLIC_BUILD_API_PROXY: !staticExport && apiProxyOrigin ? "1" : "",
  },
  async rewrites() {
    const rules = [{ source: "/favicon.ico", destination: "/favicon.svg" }];
    // Vercel: set API_PROXY_ORIGIN (e.g. https://your-space.hf.space) so /api/* is proxied at build time.
    // Not used with STATIC_EXPORT (Docker/HF static bundle serves API on the same host).
    if (!staticExport && apiProxyOrigin) {
      rules.push({ source: "/api/:path*", destination: `${apiProxyOrigin}/api/:path*` });
    }
    return rules;
  },
};

export default nextConfig;
