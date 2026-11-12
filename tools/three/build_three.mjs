// tools/three/build_three.mjs -- V194: three.js as one classic script, for the rendered view.
//
// three.js (MIT) is published as ES modules only. The engine is ES5 in one closure and must also run from
// file://, where a browser refuses a module, so three's own files are bundled, unchanged, by esbuild into one
// classic script whose only global is BIMTHREE, and written with its licence to runtime/three/<version>/.
// runtime/MANIFEST.json pins both by size and SHA-256 (tools/check_runtime.py); this script writes their two
// entries, so the manifest cannot fall behind the files.
//
//   cd tools/three && npm ci --ignore-scripts     (the versions are pinned in package.json and its lock)
//   node build_three.mjs            writes the bundle, the licence and the manifest's entries
//   node build_three.mjs --check    builds in memory and fails when the committed bundle differs
//
// Nothing of three.js is edited: every name it exports is BIMTHREE's (export * from 'three').
import * as esbuild from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const WANT = '0.186.1';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const mod = path.join(here, 'node_modules');
const read = (p) => fs.readFileSync(p, 'utf8');
const pkg = (n) => JSON.parse(read(path.join(mod, n, 'package.json')));
if (!fs.existsSync(path.join(mod, 'three'))) { console.error('Run npm ci --ignore-scripts in tools/three first'); process.exit(2); }
if (pkg('three').version !== WANT) { console.error('three is ' + pkg('three').version + ', expected ' + WANT); process.exit(2); }

const r = await esbuild.build({
  stdin: { contents: "export * from 'three';\n", resolveDir: here, loader: 'js' },
  bundle: true, format: 'iife', globalName: 'BIMTHREE', target: 'es2020', platform: 'browser',
  minify: true, legalComments: 'none', charset: 'ascii', write: false, logLevel: 'warning'
});
const licence = read(path.join(mod, 'three', 'LICENSE'));
const owner = /^Copyright .*$/m.exec(licence);
if (!owner) { console.error('no copyright line in three/LICENSE'); process.exit(1); }
const banner =
  '/* __acad3dV194: three.js ' + WANT + ' (github.com/mrdoob/three.js, MIT, ' + owner[0].trim() + '), every file\n' +
  '   unchanged, as published on npm, bundled into one classic script by esbuild ' + pkg('esbuild').version +
  ' (tools/three/build_three.mjs).\n   Its only global is BIMTHREE. The licence is beside this file. */\n';
const text = banner + r.outputFiles[0].text;
const dir = path.join(root, 'runtime', 'three', WANT);
const out = path.join(dir, 'bim-three.min.js');
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');

if (process.argv.includes('--check')) {
  const have = fs.existsSync(out) ? read(out) : '';
  if (have !== text) { console.error('runtime/three/' + WANT + '/bim-three.min.js is not what this script builds'); process.exit(1); }
  console.log('runtime/three/' + WANT + '/bim-three.min.js is what tools/three builds: ' + Buffer.byteLength(text) + ' bytes');
  process.exit(0);
}

fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(out, text);
fs.writeFileSync(path.join(dir, 'LICENSE'), licence);

// the manifest's entries for the two files, replaced in place
const manPath = path.join(root, 'runtime', 'MANIFEST.json');
const man = JSON.parse(read(manPath));
const lock = JSON.parse(read(path.join(here, 'package-lock.json')));
const integrity = (lock.packages['node_modules/three'] || {}).integrity || '';
const entry = (rel, from) => {
  const b = fs.readFileSync(path.join(root, 'runtime', rel));
  return { path: rel, bytes: b.length, sha256: sha(b), from, licence: 'MIT (three.js)' };
};
const mine = [
  entry('three/' + WANT + '/LICENSE', 'npm three@' + WANT + ', LICENSE (the tarball ' + integrity + ')'),
  entry('three/' + WANT + '/bim-three.min.js', 'npm three@' + WANT + ' (the tarball ' + integrity + '), bundled unchanged by esbuild ' +
    pkg('esbuild').version + ': tools/three/build_three.mjs')
];
man.three = WANT;
man.files = man.files.filter((f) => !/^three\//.test(f.path)).concat(mine);
fs.writeFileSync(manPath, JSON.stringify(man, null, 1) + '\n');

const b = fs.readFileSync(out);
console.log('runtime/three/' + WANT + '/bim-three.min.js: ' + b.length + ' bytes');
console.log('sha256 ' + sha(b));
console.log('sri    sha256-' + crypto.createHash('sha256').update(b).digest('base64'));
console.log('REVISION ' + (/REVISION\s*=\s*"(\d+)"/.exec(read(path.join(mod, 'three', 'build', 'three.core.js'))) || [])[1]);
