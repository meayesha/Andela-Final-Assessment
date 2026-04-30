import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { proxyToUpstream } from "../../../lib/upstream-proxy";

/**
 * Fallback proxy for `/api/*` not covered by explicit routes (avoids trailingSlash + optional catch-all 404s).
 * @see lib/upstream-proxy.ts
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}

export async function GET(req: NextRequest) {
  return proxyToUpstream(req);
}

export async function HEAD(req: NextRequest) {
  return proxyToUpstream(req);
}

export async function POST(req: NextRequest) {
  return proxyToUpstream(req);
}

export async function PUT(req: NextRequest) {
  return proxyToUpstream(req);
}

export async function PATCH(req: NextRequest) {
  return proxyToUpstream(req);
}

export async function DELETE(req: NextRequest) {
  return proxyToUpstream(req);
}
