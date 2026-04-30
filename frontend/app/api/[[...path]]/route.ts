import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

/**
 * Vercel: proxy same-origin /api/* to Hugging Face (or any FastAPI host).
 * Reads API_PROXY_ORIGIN or NEXT_PUBLIC_API_URL at request time so Preview
 * deployments work once env vars exist, even if the client bundle had no NEXT_PUBLIC_*.
 *
 * Removed before `STATIC_EXPORT` Docker build (see root Dockerfile).
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

function upstreamOrigin(): string {
  const raw = (process.env.API_PROXY_ORIGIN || process.env.NEXT_PUBLIC_API_URL || "").trim();
  return raw.replace(/\/$/, "");
}

function forwardRequestHeaders(req: NextRequest): Headers {
  const out = new Headers();
  for (const name of ["authorization", "content-type", "accept"]) {
    const v = req.headers.get(name);
    if (v) out.set(name, v);
  }
  return out;
}

async function proxy(req: NextRequest): Promise<Response> {
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

  const path = req.nextUrl.pathname + req.nextUrl.search;
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

export async function GET(req: NextRequest) {
  return proxy(req);
}

export async function HEAD(req: NextRequest) {
  return proxy(req);
}

export async function POST(req: NextRequest) {
  return proxy(req);
}

export async function PUT(req: NextRequest) {
  return proxy(req);
}

export async function PATCH(req: NextRequest) {
  return proxy(req);
}

export async function DELETE(req: NextRequest) {
  return proxy(req);
}
