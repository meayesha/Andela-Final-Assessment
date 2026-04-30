/**
 * Client-side API URL: never use huggingface.co / hf.co Hub hosts as fetch targets from Vercel
 * (browser CORS). Prefer same-origin `/api/*` (Vercel proxy) or a real `*.hf.space` origin.
 */

export function getPublicApiBase(): string {
  return (process.env.NEXT_PUBLIC_API_URL || "").trim().replace(/\/$/, "");
}

/** Hub / short-link hosts — not the running Space API origin. */
function isDisallowedCrossOriginApiOrigin(originOrUrl: string): boolean {
  const raw = originOrUrl.trim();
  if (!raw) return false;
  try {
    const u = new URL(/^https?:\/\//i.test(raw) ? raw : `https://${raw}`);
    const h = u.hostname.toLowerCase();
    if (h.endsWith(".hf.space")) return false;
    if (h === "huggingface.co" || h.endsWith(".huggingface.co")) return true;
    if (h === "hf.co") return true;
  } catch {
    /* ignore */
  }
  const low = raw.toLowerCase();
  if (low.includes(".hf.space")) return false;
  if (low.includes(".git")) return true;
  return low.includes("huggingface.co") || /^https?:\/\/([^/]*\.)?hf\.co(\/|$)/i.test(raw);
}

export function publicApiBaseIsInvalidHubUrl(): boolean {
  return isDisallowedCrossOriginApiOrigin(getPublicApiBase());
}

/**
 * Resolves the URL the browser should fetch. Path-only `/api/...` when env points at the Hub
 * so Vercel same-origin handlers can proxy.
 */
export function clientApiRequestUrl(path: string): string {
  const p = (path || "").replace(/\/+$/, "") || path;
  const b = getPublicApiBase();
  if (b && !publicApiBaseIsInvalidHubUrl()) {
    const candidate = `${b}${p}`;
    try {
      const origin = new URL(candidate).origin;
      if (isDisallowedCrossOriginApiOrigin(origin)) {
        // Env was a Hub URL or resolved to one — fall through to same-origin.
      } else {
        return candidate;
      }
    } catch {
      return candidate;
    }
  }
  if (typeof window !== "undefined" && p.startsWith("/")) return p;
  if (typeof window !== "undefined") return new URL(p, window.location.origin).toString();
  return p;
}
