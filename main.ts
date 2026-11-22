// news-image-20261121 — round 6 entrypoint.
//
// The front page for 21 November 2026 is already drawn: entry.png sits in
// this repository, committed byte for byte. This program only validates
// that PNG and copies it to the grader output directory. It never runs
// render.py and never writes into the repository: the grader mounts the
// repo read-only, so any write there (or any render step that writes
// there) fails the run. Rendering is a build-time job, done long before
// grading; grading is validate-and-copy only.
//
// Validation: PNG signature, IHDR 1024x1024, every chunk inside the
// file with a matching CRC-32, at least one IDAT, an IEND trailer with
// nothing after it, and at most 1 MiB. The copy is verified byte for
// byte (sha256 of source and output must match) so both grader runs
// produce identical output.
//
// The output directory itself is never removed — the grader mounts it,
// and removing a mount point fails (EBUSY). Only its contents are
// cleared before the copy.

import { createHash } from "node:crypto";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
} from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? join(HERE, "out");
const OUT = join(OUT_DIR, "entry.png");

const PNG_MAGIC = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);
const MAX_BYTES = 1048576;
const WANT_WIDTH = 1024;
const WANT_HEIGHT = 1024;

function fail(message: string): never {
  console.error(`entry: ${message}`);
  process.exit(1);
}

// Clearing the output directory would delete the source image if the
// output directory were the repository itself. Refuse that outright.
if (resolve(OUT_DIR) === resolve(HERE)) {
  fail("MAKEFUN_OUTPUT_DIR must not be the repository directory");
}

function sha256Hex(data: Buffer): string {
  return createHash("sha256").update(data).digest("hex");
}

// CRC-32 (IEEE polynomial), the checksum PNG stores per chunk.
const CRC_TABLE: number[] = [];
for (let n = 0; n < 256; n++) {
  let c = n;
  for (let k = 0; k < 8; k++) {
    c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  }
  CRC_TABLE[n] = c >>> 0;
}

function crc32(buf: Buffer): number {
  let c = 0xffffffff;
  for (const byte of buf) {
    c = CRC_TABLE[(c ^ byte) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

// Validate the committed PNG. Returns its bytes on success.
function validatePng(): Buffer {
  if (!existsSync(SRC)) {
    fail("entry.png is missing from the repository");
  }
  const png = readFileSync(SRC);
  if (png.length > MAX_BYTES) {
    fail(`entry.png is ${png.length} bytes, over the 1 MiB cap`);
  }
  if (png.length < 8 || !png.subarray(0, 8).equals(PNG_MAGIC)) {
    fail("entry.png does not start with the PNG signature");
  }

  let offset = 8;
  let sawIdat = false;
  let sawIend = false;
  let firstChunk = true;
  while (offset + 8 <= png.length) {
    const length = png.readUInt32BE(offset);
    const type = png.toString("ascii", offset + 4, offset + 8);
    if (firstChunk && type !== "IHDR") {
      fail(`entry.png starts with ${type}, not IHDR`);
    }
    firstChunk = false;
    if (offset + 12 + length > png.length) {
      fail(`chunk ${type} at offset ${offset} runs past the end of the file`);
    }
    const stored = png.readUInt32BE(offset + 8 + length);
    const actual = crc32(png.subarray(offset + 4, offset + 8 + length));
    if (stored !== actual) {
      fail(`chunk ${type} at offset ${offset} has a bad CRC`);
    }
    if (type === "IHDR") {
      const ihdrLength = png.readUInt32BE(offset);
      if (ihdrLength !== 13) {
        fail("entry.png has a malformed IHDR chunk");
      }
      const width = png.readUInt32BE(offset + 8);
      const height = png.readUInt32BE(offset + 12);
      if (width !== WANT_WIDTH || height !== WANT_HEIGHT) {
        fail(`entry.png is ${width}x${height}, must be 1024x1024`);
      }
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
  if (offset !== png.length) {
    fail("entry.png has bytes after the IEND chunk");
  }
  return png;
}

// Clear a directory's contents without removing the directory itself.
function clearDir(dir: string): void {
  mkdirSync(dir, { recursive: true });
  for (const name of readdirSync(dir)) {
    rmSync(join(dir, name), { recursive: true, force: true });
  }
}

const png = validatePng();
clearDir(OUT_DIR);
copyFileSync(SRC, OUT);

const sourceHash = sha256Hex(png);
const outputHash = sha256Hex(readFileSync(OUT));
if (sourceHash !== outputHash) {
  fail(`output differs from entry.png: ${outputHash} != ${sourceHash}`);
}
console.log(`entry.png ${png.length} bytes sha256 ${sourceHash} -> ${OUT}`);
