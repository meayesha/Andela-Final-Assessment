import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

export function upstreamOrigin(): string {
  const raw = (process.env.API_PROXY_ORIGIN || process.env.NEXT_PUBLIC_API_URL || "").trim();
  return raw.replace(/\/$/, "");
}

export function forwardRequestHeaders(req: NextRequest): Headers {
  const out = new Headers();
  for (const name of ["authorization", "content-type", "accept"]) {
    const v = req.headers.get(name);
    if (v) out.set(name, v);
  }
  return out;
}

/** FastAPI routes have no trailing slash; Next may request `/api/todos/`. */
function normalizedApiPath(pathname: string): string {
  if (pathname.length <= 1 || !pathname.startsWith("/api")) return pathname;
  let p = pathname;
  while (p.length > 1 && p.endsWith("/")) p = p.slice(0, -1);
  return p;
}

export async function proxyToUpstream(req: NextRequest): Promise<Response> {
  const origin = upstreamOrigin();
  if (!origin) {
    return NextResponse.json(
      {
        detail:
          "Set API_PROXY_ORIGIN or NEXT_PUBLIC_API_URL in Vercel → Environment Variables (include Preview), then redeploy.",
      },
      { status: 503 },
    );
  }

  const path = normalizedApiPath(req.nextUrl.pathname) + req.nextUrl.search;
  const target = `${origin}${path}`;

  const init: RequestInit & { duplex?: string } = {
    method: req.method,
    headers: forwardRequestHeaders(req),
    redirect: "manual",
  };
  if (req.method !== "GET" && req.method !== "HEAD") {
    init.body = req.body;
    init.duplex = "half";
  }

  const res = await fetch(target, init);
  const headers = new Headers(res.headers);
  headers.delete("transfer-encoding");
  return new NextResponse(res.body, {
    status: res.status,
    statusText: res.statusText,
    headers,
  });
}
