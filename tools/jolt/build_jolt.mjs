// tools/jolt/build_jolt.mjs -- V202: Jolt Physics as one classic script, for the walkthrough.
//
// JoltPhysics.js (MIT, github.com/jrouwe/JoltPhysics.js) is published as ES modules only. The engine is ES5 in one
// closure and must also run from file://, where a browser refuses a module and refuses to fetch a .wasm file, so its
// `wasm-compat` build (the WebAssembly carried inside the script as base64) is bundled, unchanged, by esbuild into one
// classic script whose only global is BIMJOLT (BIMJOLT.default() resolves to Jolt), and written with its licence to
// runtime/jolt/<version>/. runtime/MANIFEST.json pins both by size and SHA-256 (tools/check_runtime.py); this script
// writes their two entries, so the manifest cannot fall behind the files. docs/research/research-walkthrough.md, e02.
//
//   cd tools/jolt && npm ci --ignore-scripts     (the versions are pinned in package.json and its lock)
//   node build_jolt.mjs            writes the bundle, the licence and the manifest's entries
//   node build_jolt.mjs --check    builds in memory and fails when the committed bundle differs
//
// Nothing of Jolt is edited. Its Emscripten loader imports `node:module` on its Node path only, never reached in a
// page; esbuild leaves `node:*` imports outside the bundle (experiment e02 loaded the result from file:// in Chromium).
import * as esbuild from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const WANT = '1.1.1';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const mod = path.join(here, 'node_modules');
const read = (p) => fs.readFileSync(p, 'utf8');
const pkg = (n) => JSON.parse(read(path.join(mod, n, 'package.json')));
if (!fs.existsSync(path.join(mod, 'jolt-physics'))) { console.error('Run npm ci --ignore-scripts in tools/jolt first'); process.exit(2); }
if (pkg('jolt-physics').version !== WANT) { console.error('jolt-physics is ' + pkg('jolt-physics').version + ', expected ' + WANT); process.exit(2); }

const r = await esbuild.build({
  stdin: { contents: "export { default } from 'jolt-physics/wasm-compat';\n", resolveDir: here, loader: 'js' },
  bundle: true, format: 'iife', globalName: 'BIMJOLT', target: 'es2020', platform: 'browser',
  minify: true, legalComments: 'none', charset: 'ascii', write: false, logLevel: 'warning', external: ['node:*']
});
const licence = read(path.join(mod, 'jolt-physics', 'LICENSE'));
const owner = /^Copyright .*$/m.exec(licence);
if (!owner) { console.error('no copyright line in jolt-physics/LICENSE'); process.exit(1); }
const banner =
  '/* __acad3dV202: Jolt Physics ' + WANT + ' (github.com/jrouwe/JoltPhysics.js, MIT, ' + owner[0].trim() + '), its wasm-compat\n' +
  '   build unchanged, as published on npm, bundled into one classic script by esbuild ' + pkg('esbuild').version +
  ' (tools/jolt/build_jolt.mjs).\n   Its only global is BIMJOLT; BIMJOLT.default() resolves to Jolt. The licence is beside this file. */\n';
const text = banner + r.outputFiles[0].text;
const dir = path.join(root, 'runtime', 'jolt', WANT);
const out = path.join(dir, 'bim-jolt.min.js');
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');

if (process.argv.includes('--check')) {
  const have = fs.existsSync(out) ? read(out) : '';
  if (have !== text) { console.error('runtime/jolt/' + WANT + '/bim-jolt.min.js is not what this script builds'); process.exit(1); }
  console.log('runtime/jolt/' + WANT + '/bim-jolt.min.js is what tools/jolt builds: ' + Buffer.byteLength(text) + ' bytes');
  process.exit(0);
}

fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(out, text);
fs.writeFileSync(path.join(dir, 'LICENSE'), licence);

// the manifest's entries for the two files, replaced in place
const manPath = path.join(root, 'runtime', 'MANIFEST.json');
const man = JSON.parse(read(manPath));
const lock = JSON.parse(read(path.join(here, 'package-lock.json')));
const integrity = (lock.packages['node_modules/jolt-physics'] || {}).integrity || '';
const entry = (rel, from) => {
  const b = fs.readFileSync(path.join(root, 'runtime', rel));
  return { path: rel, bytes: b.length, sha256: sha(b), from, licence: 'MIT (Jolt Physics, JoltPhysics.js)' };
};
const mine = [
  entry('jolt/' + WANT + '/LICENSE', 'npm jolt-physics@' + WANT + ', LICENSE (the tarball ' + integrity + ')'),
  entry('jolt/' + WANT + '/bim-jolt.min.js', 'npm jolt-physics@' + WANT + ' (the tarball ' + integrity + '), dist/jolt-physics.wasm-compat.js ' +
    'bundled unchanged by esbuild ' + pkg('esbuild').version + ': tools/jolt/build_jolt.mjs')
];
man.jolt = WANT;
man.files = man.files.filter((f) => !/^jolt\//.test(f.path)).concat(mine);
fs.writeFileSync(manPath, JSON.stringify(man, null, 1) + '\n');

const b = fs.readFileSync(out);
console.log('runtime/jolt/' + WANT + '/bim-jolt.min.js: ' + b.length + ' bytes');
console.log('sha256 ' + sha(b));
console.log('sri    sha256-' + crypto.createHash('sha256').update(b).digest('base64'));
