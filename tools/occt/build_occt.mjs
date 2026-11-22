// tools/occt/build_occt.mjs -- V264: OpenCASCADE for the solid tools (docs/research/research-occt-library.md).
//
// Two parts, kept apart as the third-party rule asks of an LGPL library (CLAUDE.md):
//   bim-replicad.min.js  replicad 1.2.1 (MIT) and what it imports (flatbush, flatqueue: ISC; opentype.js: MIT),
//                        bundled unchanged by esbuild into one classic script whose only global is BIMREPLICAD;
//   replicad_single.js and replicad_single.wasm, the OpenCASCADE build replicad drives (replicad-opencascadejs 1.2.1,
//                        LGPL-2.1-only), copied byte for byte as their own files, replaceable by any build of the same
//                        interface, with the LGPL text and a written offer of their source (OCCT-SOURCE.md).
// All go to runtime/occt/<ver>/; runtime/MANIFEST.json pins each by size and SHA-256, and this script writes those
// entries, so the manifest cannot fall behind the files.
//
//   cd tools/occt && npm ci --ignore-scripts
//   node tools/occt/build_occt.mjs            writes the files and the manifest's entries
//   node tools/occt/build_occt.mjs --check    builds in memory and fails when a committed file differs
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const VER = '1.2.1';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const mod = path.join(here, 'node_modules');
if (!fs.existsSync(path.join(mod, 'replicad'))) { console.error('Run npm ci --ignore-scripts in tools/occt first'); process.exit(2); }
const read = (p) => fs.readFileSync(p);
const pj = (p) => JSON.parse(fs.readFileSync(path.join(mod, p, 'package.json'), 'utf8'));
for (const [p, v] of [['replicad', VER], ['replicad-opencascadejs', VER]]) if (pj(p).version !== v) { console.error(p + ' is ' + pj(p).version + ', expected ' + v); process.exit(2); }
const esbuild = createRequire(path.join(mod, 'x.js'))('esbuild');
const ebver = pj('esbuild').version;

const r = await esbuild.build({
  stdin: { contents: "export * from 'replicad';\n", resolveDir: here, loader: 'js' },
  nodePaths: [mod], bundle: true, format: 'iife', globalName: 'BIMREPLICAD', target: 'es2020', platform: 'browser',
  minify: true, legalComments: 'none', charset: 'ascii', write: false, logLevel: 'warning'
});
const banner =
  '/* __acad3dV264: replicad ' + VER + ' (github.com/sgenoud/replicad, MIT, Copyright 2023 QuaroTech Sarl) with flatbush ' +
  pj('flatbush').version + ', flatqueue ' + pj('flatqueue').version + ' (ISC, Vladimir Agafonkin) and opentype.js ' + pj('opentype.js').version +
  ' (MIT), unchanged, bundled into one classic script by esbuild ' + ebver + ' (tools/occt/build_occt.mjs). Its only global is BIMREPLICAD.\n' +
  '   It drives OpenCASCADE through replicad_single.js and replicad_single.wasm beside it (LGPL-2.1, their own files). */\n';
const bundle = Buffer.from(banner + r.outputFiles[0].text);
const oc = path.join(mod, 'replicad-opencascadejs');
const licence = (dir) => ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'license'].map((f) => path.join(dir, f)).find((f) => fs.existsSync(f));
const source =
  '# The source of the OpenCASCADE build in this folder\n\n' +
  '`replicad_single.js` and `replicad_single.wasm` are the npm package `replicad-opencascadejs@' + VER + '` (its `dist/`), copied\n' +
  'byte for byte, under the GNU Lesser General Public License 2.1 (`OCCT-LICENSE`). They are a build of Open CASCADE Technology\n' +
  '(https://dev.opencascade.org, LGPL-2.1 with the Open CASCADE exception) made with the opencascade.js tool chain.\n\n' +
  'Their source: https://github.com/sgenoud/replicad (`packages/replicad-opencascadejs`, the build configuration, at the release\n' +
  'tagged for ' + VER + '), https://github.com/donalffons/opencascade.js (the tool chain) and https://github.com/Open-Cascade-SAS/OCCT\n' +
  '(the library). On request to the owner of this repository, a copy of that source is provided, as section 6 of the licence asks.\n\n' +
  'They are their own files, loaded by the app only through `src/js/engine/solids/occt-adapter.js`, and can be replaced by any build\n' +
  'with the same interface: put its two files here under these names and update `runtime/MANIFEST.json` (`tools/occt/build_occt.mjs`).\n';
const files = {
  'bim-replicad.min.js': bundle,
  'REPLICAD-LICENSE': read(licence(path.join(mod, 'replicad'))),
  'replicad_single.js': read(path.join(oc, 'dist', 'replicad_single.js')),
  'replicad_single.wasm': read(path.join(oc, 'dist', 'replicad_single.wasm')),
  'OCCT-LICENSE': read(licence(oc)),
  'OCCT-SOURCE.md': Buffer.from(source)
};
const dir = path.join(root, 'runtime', 'occt', VER);
if (process.argv.includes('--check')) {
  let bad = 0;
  for (const [n, b] of Object.entries(files)) {
    const f = path.join(dir, n);
    if (!fs.existsSync(f) || !read(f).equals(b)) { console.error('runtime/occt/' + VER + '/' + n + ' is not what this script builds'); bad++; }
  }
  if (bad) process.exit(1);
  console.log('runtime/occt/' + VER + '/ is what tools/occt builds: ' + Object.keys(files).length + ' files');
  process.exit(0);
}
fs.mkdirSync(dir, { recursive: true });
for (const [n, b] of Object.entries(files)) fs.writeFileSync(path.join(dir, n), b);
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const manPath = path.join(root, 'runtime', 'MANIFEST.json');
const man = JSON.parse(fs.readFileSync(manPath, 'utf8'));
const from = {
  'bim-replicad.min.js': 'npm replicad@' + VER + ' with flatbush, flatqueue, opentype.js, bundled unchanged by esbuild ' + ebver + ': tools/occt/build_occt.mjs',
  'REPLICAD-LICENSE': 'npm replicad@' + VER + ', LICENSE',
  'replicad_single.js': 'npm replicad-opencascadejs@' + VER + ', dist/replicad_single.js, unchanged',
  'replicad_single.wasm': 'npm replicad-opencascadejs@' + VER + ', dist/replicad_single.wasm, unchanged',
  'OCCT-LICENSE': 'npm replicad-opencascadejs@' + VER + ', LICENSE',
  'OCCT-SOURCE.md': 'written by tools/occt/build_occt.mjs: the source offer'
};
const lic = (n) => /replicad\.min|REPLICAD/.test(n) ? 'MIT (replicad, opentype.js), ISC (flatbush, flatqueue)' : 'LGPL-2.1-only (OpenCASCADE, replicad-opencascadejs)';
man.occt = VER;
man.files = man.files.filter((f) => !/^occt\//.test(f.path)).concat(Object.keys(files).map((n) => {
  const b = files[n]; return { path: 'occt/' + VER + '/' + n, bytes: b.length, sha256: sha(b), from: from[n], licence: lic(n) };
}));
fs.writeFileSync(manPath, JSON.stringify(man, null, 1) + '\n');
for (const n of Object.keys(files)) console.log('runtime/occt/' + VER + '/' + n + ': ' + files[n].length + ' bytes');
console.log('sri bim-replicad.min.js sha256-' + crypto.createHash('sha256').update(bundle).digest('base64'));
console.log('sri replicad_single.js sha256-' + crypto.createHash('sha256').update(files['replicad_single.js']).digest('base64'));
