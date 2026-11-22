// tools/occt/build_occt_import.mjs -- V270: IGES import (docs/research/research-freecad-gap.md; the owner's approval,
// 2026-11-22: "Yes").
//
// occt-import-js 0.0.23 (LGPL-2.1, github.com/kovacsv/occt-import-js): OpenCASCADE's IGES, STEP and BREP readers built
// with emscripten into occt-import-js.js (a classic script whose only global is occtimportjs) and occt-import-js.wasm.
// Copied byte for byte, as their own files, with both licences and a written offer of their source, to
// runtime/occt-import/<ver>/; runtime/MANIFEST.json pins each by size and SHA-256, written here.
//
//   cd tools/occt && npm ci --ignore-scripts
//   node tools/occt/build_occt_import.mjs            writes the files and the manifest's entries
//   node tools/occt/build_occt_import.mjs --check    fails when a committed file differs
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const VER = '0.0.23';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const pkg = path.join(here, 'node_modules', 'occt-import-js');
if (!fs.existsSync(pkg)) { console.error('Run npm ci --ignore-scripts in tools/occt first'); process.exit(2); }
const v = JSON.parse(fs.readFileSync(path.join(pkg, 'package.json'), 'utf8')).version;
if (v !== VER) { console.error('occt-import-js is ' + v + ', expected ' + VER); process.exit(2); }
const read = (p) => fs.readFileSync(p);
const source =
  '# The source of the files in this folder\n\n' +
  '`occt-import-js.js` and `occt-import-js.wasm` are the npm package `occt-import-js@' + VER + '` (its `dist/`), copied byte for\n' +
  'byte, under the GNU Lesser General Public License 2.1 (`LICENSE-occt-import-js.txt`). They are a build of Open CASCADE\n' +
  'Technology (`LICENSE-occt.txt`, LGPL-2.1 with the Open CASCADE exception) made with emscripten.\n\n' +
  'Their source: https://github.com/kovacsv/occt-import-js (the release tagged v' + VER + ') and\n' +
  'https://github.com/Open-Cascade-SAS/OCCT (the library). On request to the owner of this repository, a copy of that source\n' +
  'is provided, as section 6 of the licence asks.\n\n' +
  'They are their own files, loaded by the app only through `src/js/engine/io/iges-io.js`, when an IGES file is imported,\n' +
  'and can be replaced by any build with the same interface: put its two files here under these names and update\n' +
  '`runtime/MANIFEST.json` (`tools/occt/build_occt_import.mjs`).\n';
const files = {
  'occt-import-js.js': read(path.join(pkg, 'dist', 'occt-import-js.js')),
  'occt-import-js.wasm': read(path.join(pkg, 'dist', 'occt-import-js.wasm')),
  'LICENSE-occt-import-js.txt': read(path.join(pkg, 'dist', 'license.occt-import-js.txt')),
  'LICENSE-occt.txt': read(path.join(pkg, 'dist', 'license.occt.txt')),
  'SOURCE.md': Buffer.from(source)
};
const dir = path.join(root, 'runtime', 'occt-import', VER);
if (process.argv.includes('--check')) {
  let bad = 0;
  for (const [n, b] of Object.entries(files)) {
    const f = path.join(dir, n);
    if (!fs.existsSync(f) || !read(f).equals(b)) { console.error('runtime/occt-import/' + VER + '/' + n + ' is not what this script builds'); bad++; }
  }
  if (bad) process.exit(1);
  console.log('runtime/occt-import/' + VER + '/ is what tools/occt builds: ' + Object.keys(files).length + ' files');
  process.exit(0);
}
fs.mkdirSync(dir, { recursive: true });
for (const [n, b] of Object.entries(files)) fs.writeFileSync(path.join(dir, n), b);
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const manPath = path.join(root, 'runtime', 'MANIFEST.json');
const man = JSON.parse(fs.readFileSync(manPath, 'utf8'));
const from = {
  'occt-import-js.js': 'npm occt-import-js@' + VER + ', dist/occt-import-js.js, unchanged',
  'occt-import-js.wasm': 'npm occt-import-js@' + VER + ', dist/occt-import-js.wasm, unchanged',
  'LICENSE-occt-import-js.txt': 'npm occt-import-js@' + VER + ', dist/license.occt-import-js.txt',
  'LICENSE-occt.txt': 'npm occt-import-js@' + VER + ', dist/license.occt.txt',
  'SOURCE.md': 'written by tools/occt/build_occt_import.mjs: the source offer'
};
man.occtImport = VER;
man.files = man.files.filter((f) => !/^occt-import\//.test(f.path)).concat(Object.keys(files).map((n) => {
  const b = files[n]; return { path: 'occt-import/' + VER + '/' + n, bytes: b.length, sha256: sha(b), from: from[n], licence: 'LGPL-2.1 (occt-import-js; OpenCASCADE)' };
}));
fs.writeFileSync(manPath, JSON.stringify(man, null, 1) + '\n');
for (const n of Object.keys(files)) console.log('runtime/occt-import/' + VER + '/' + n + ': ' + files[n].length + ' bytes');
console.log('sri occt-import-js.js sha256-' + crypto.createHash('sha256').update(files['occt-import-js.js']).digest('base64'));
