import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "..");
const out = path.join(root, "out");
const target = path.join(root, "..", "backend", "static");

if (!fs.existsSync(out)) {
  console.warn("copy-static: no out/ folder (run next build first). skipping.");
  process.exit(0);
}

fs.rmSync(target, { recursive: true, force: true });
fs.cpSync(out, target, { recursive: true });
console.log("Copied Next.js export to backend/static");
