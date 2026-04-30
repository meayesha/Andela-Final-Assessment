import path from "node:path";
import { config as loadEnv } from "dotenv";
import type { NextConfig } from "next";

// Load repo-root `.env` so Next.js picks up NEXT_PUBLIC_* and Clerk keys during `next dev` / `next build`.
loadEnv({ path: path.resolve(__dirname, "..", ".env") });

const staticExport = process.env.STATIC_EXPORT === "true";

const nextConfig: NextConfig = {
  ...(staticExport ? { output: "export" as const } : {}),
  trailingSlash: true,
  images: { unoptimized: true },
};

export default nextConfig;
