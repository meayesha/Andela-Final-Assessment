import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { proxyToUpstream } from "../../../../lib/upstream-proxy";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}

export async function POST(req: NextRequest) {
  return proxyToUpstream(req);
}
