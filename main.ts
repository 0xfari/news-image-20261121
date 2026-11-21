// news-image-20261121 entry (Node 22, standard library only).
// The image is entry.png beside this file; the program validates it and
// copies it to /output/entry.png. The grader mounts /output, so this file
// never removes the output directory itself — it only clears its contents.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readdirSync, rmSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const src = new URL('./entry.png', import.meta.url);

if (!existsSync(src)) {
  throw new Error('entry.png is missing from the repository');
}
const st = statSync(src);
if (!st.isFile() || st.size === 0 || st.size > 1048576) {
  throw new Error(`entry.png has an unexpected size: ${st.size} bytes`);
}

mkdirSync(outDir, { recursive: true });
for (const name of readdirSync(outDir)) {
  rmSync(join(outDir, name), { recursive: true, force: true });
}
copyFileSync(src, join(outDir, 'entry.png'));
