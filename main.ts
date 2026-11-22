// news-image-20261121 v4 — entrypoint.
//
// Validates the front-page PNG this repository holds (PNG signature,
// IHDR 1024x1024, IEND trailer, at most 1 MiB) and copies it to the
// grader output directory. The copy is byte-identical by construction:
// the program writes nothing of its own, so both grader runs produce
// the same bytes.
//
// The output directory itself is never removed: the grader mounts
// /output, and removing a mount point fails (EBUSY). Only its
// contents are cleared before the copy.

import { createHash } from "node:crypto";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? join(HERE, "out");
const OUT = join(OUT_DIR, "entry.png");

const PNG_MAGIC = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);

function fail(message: string): never {
  console.error(`entry: ${message}`);
  process.exit(1);
}

function sha256(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

// --- validate the image -------------------------------------------------
if (!existsSync(SRC)) fail("entry.png is missing from the repository");
const png = readFileSync(SRC);
if (png.length > 1048576) {
  fail(`entry.png is ${png.length} bytes, over the 1 MiB cap`);
}
if (png.length < 8 || !png.subarray(0, 8).equals(PNG_MAGIC)) {
  fail("entry.png does not start with the PNG signature");
}
const ihdrLength = png.readUInt32BE(8);
const ihdrType = png.toString("ascii", 12, 16);
if (ihdrType !== "IHDR" || ihdrLength !== 13) {
  fail("entry.png has no valid IHDR chunk");
}
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  fail(`entry.png is ${width}x${height}, must be 1024x1024`);
}
// CRC-32 (IEEE polynomial) over a chunk's type + data, as the PNG
// spec stores it. Verifies every chunk the file carries.
const CRC_TABLE: number[] = [];
for (let n = 0; n < 256; n++) {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  CRC_TABLE[n] = c >>> 0;
}
function crc32(buf: Buffer): number {
  let c = 0xffffffff;
  for (const byte of buf) c = CRC_TABLE[(c ^ byte) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

// Walk the chunk list: every chunk must fit inside the file, carry a
// matching CRC, and the file must end with the IEND chunk. At least
// one IDAT chunk must be present.
let offset = 8;
let sawIend = false;
let sawIdat = false;
while (offset + 8 <= png.length) {
  const length = png.readUInt32BE(offset);
  const type = png.toString("ascii", offset + 4, offset + 8);
  if (offset + 12 + length > png.length) {
    fail(`chunk ${type} at offset ${offset} runs past the end of the file`);
  }
  const storedCrc = png.readUInt32BE(offset + 8 + length);
  const actualCrc = crc32(png.subarray(offset + 4, offset + 8 + length));
  if (storedCrc !== actualCrc) {
    fail(`chunk ${type} at offset ${offset} has a bad CRC`);
  }
  if (type === "IDAT") sawIdat = true;
  offset += 12 + length;
  if (type === "IEND") {
    sawIend = true;
    break;
  }
}
if (!sawIend) fail("entry.png has no IEND chunk");
if (!sawIdat) fail("entry.png has no IDAT chunk");
if (offset !== png.length) fail("entry.png has bytes after the IEND chunk");

// --- copy it to the output directory ------------------------------------
mkdirSync(OUT_DIR, { recursive: true });
for (const name of readdirSync(OUT_DIR)) {
  rmSync(join(OUT_DIR, name), { recursive: true, force: true });
}
copyFileSync(SRC, OUT);

// --- the output must be byte-identical to the source --------------------
const sourceHash = sha256(SRC);
const outputHash = sha256(OUT);
if (sourceHash !== outputHash) {
  fail(`output differs from entry.png: ${outputHash} != ${sourceHash}`);
}
console.log(`entry.png ${png.length} bytes sha256 ${sourceHash} -> ${OUT}`);
