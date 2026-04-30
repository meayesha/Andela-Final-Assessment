import type { NextRequest } from "next/server";
import { proxyToUpstream } from "../../../lib/upstream-proxy";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  return proxyToUpstream(req);
}
