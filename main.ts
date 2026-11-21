// news-image-20261121 v3 entry (Node 22, standard library only).
// The image is entry.png beside this file; the program checks it and copies
// it to /output/entry.png. The grader mounts /output, so this file never
// removes the output directory itself — it only clears what is inside it.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const src = new URL('./entry.png', import.meta.url);

if (!existsSync(src)) {
  throw new Error('entry.png is missing from the repository');
}
const data = readFileSync(src);
if (data.length === 0 || data.length > 1048576) {
  throw new Error(`entry.png has an unexpected size: ${data.length} bytes`);
}
// PNG files start with a fixed 8-byte signature; refuse anything else.
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!data.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error('entry.png is not a PNG file');
}
// The IHDR chunk carries the image dimensions at bytes 16-23 (big-endian).
const width = data.readUInt32BE(16);
const height = data.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is too large: ${width}x${height}`);
}

mkdirSync(outDir, { recursive: true });
for (const name of readdirSync(outDir)) {
  rmSync(join(outDir, name), { recursive: true, force: true });
}
copyFileSync(src, join(outDir, 'entry.png'));
// Verify the copy landed intact: compare the written bytes with the source.
const written = readFileSync(join(outDir, 'entry.png'));
if (!written.equals(data)) {
  throw new Error('entry.png copy does not match the source');
}
