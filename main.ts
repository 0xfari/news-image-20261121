/**
 * news-image-20261121 v5 entrypoint.
 *
 * Runs render.py (draws entry.png deterministically with Pillow), validates
 * the PNG (signature, IHDR 1024x1024, chunk CRCs, IEND), and copies it to
 * MAKEFUN_OUTPUT_DIR. The output directory itself is never removed: only its
 * contents are cleared, because the grader mounts it (rmSync on a mount
 * point fails with EBUSY).
 */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoDir = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "out";

function fail(message: string): never {
  console.error(`error: ${message}`);
  process.exit(1);
}

function validatePng(path: string): void {
  const buf = readFileSync(path);
  const pngSig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
let crcTable: number[] | undefined;
function pngCrcTable(): number[] {
  if (crcTable) return crcTable;
  crcTable = [];
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    crcTable[n] = c >>> 0;
  }
  return crcTable;
}
  if (buf.length < 8 || !buf.subarray(0, 8).equals(pngSig)) {
    fail(`${path}: not a PNG`);
  }
  let off = 8;
  let sawIhdr = false;
  let sawIend = false;
  while (off + 8 <= buf.length) {
    const len = buf.readUInt32BE(off);
    const type = buf.subarray(off + 4, off + 8).toString("ascii");
    if (off + 12 + len > buf.length) fail(`${path}: truncated ${type} chunk`);
    const storedCrc = buf.readUInt32BE(off + 8 + len);
    const table = pngCrcTable();
    let crc = 0xffffffff;
    for (let i = off + 4; i < off + 8 + len; i++) {
      crc = table[(crc ^ buf[i]) & 0xff] ^ (crc >>> 8);
    }
    if ((crc ^ 0xffffffff) >>> 0 !== storedCrc) fail(`${path}: bad CRC in ${type}`);
    if (type === "IHDR") {
      sawIhdr = true;
      const w = buf.readUInt32BE(off + 8);
      const h = buf.readUInt32BE(off + 12);
      if (w !== 1024 || h !== 1024) fail(`${path}: expected 1024x1024, got ${w}x${h}`);
    }
    if (type === "IEND") sawIend = true;
    off += 12 + len;
  }
  if (!sawIhdr || !sawIend) fail(`${path}: missing IHDR or IEND`);
}

function main(): void {
  mkdirSync(outDir, { recursive: true });
  for (const f of readdirSync(outDir)) {
    rmSync(join(outDir, f), { recursive: true, force: true });
  }

  const py = spawnSync("python3", ["render.py"], { cwd: repoDir, stdio: "inherit" });
  if (py.status !== 0) fail(`render.py exited with status ${py.status}`);

  const src = join(repoDir, "entry.png");
  if (!existsSync(src)) fail("render.py did not write entry.png");
  validatePng(src);
  const size = statSync(src).size;
  if (size > 1048576) fail(`entry.png is ${size} bytes, over the 1 MiB cap`);
  copyFileSync(src, join(outDir, "entry.png"));
  const sha = createHash("sha256").update(readFileSync(src)).digest("hex");
  console.log(`entry.png ${size} bytes sha256 ${sha}`);
}

main();
