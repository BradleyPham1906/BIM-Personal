// tools/ifc/build_ifc.mjs -- V196: BimCraft's IFC engine (cc-ifc) and Manifold as one classic script, for the IFC import.
//
// cc-ifc (vendor/cc-ifc/ifc, Apache-2.0) and Manifold's loader (npm manifold-3d, Apache-2.0) are ES modules. The
// engine is ES5 in one closure and must also run from file://, where a browser refuses a module, so both are bundled,
// unchanged, by esbuild into one classic script whose only global is BIMIFC, and written with their licences to
// runtime/cc-ifc/<rev>/, Manifold's WebAssembly beside it. runtime/MANIFEST.json pins every file by size and SHA-256
// (tools/check_runtime.py); this script writes their entries, so the manifest cannot fall behind the files.
//
//   cd tools/ifc && npm ci --ignore-scripts     (the versions are pinned in package.json and its lock)
//   node build_ifc.mjs            writes the bundle, the licences, the wasm and the manifest's entries
//   node build_ifc.mjs --check    builds in memory and fails when the committed bundle differs
import * as esbuild from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const REV = 'cfbd948', MANIFOLD = '3.5.4';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const mod = path.join(here, 'node_modules');
const vend = path.join(root, 'vendor', 'cc-ifc');
const read = (p) => fs.readFileSync(p, 'utf8');
if (!fs.existsSync(path.join(mod, 'manifold-3d'))) { console.error('Run npm ci --ignore-scripts in tools/ifc first'); process.exit(2); }
const mver = JSON.parse(read(path.join(mod, 'manifold-3d', 'package.json'))).version;
if (mver !== MANIFOLD) { console.error('manifold-3d is ' + mver + ', expected ' + MANIFOLD); process.exit(2); }
const ebver = JSON.parse(read(path.join(mod, 'esbuild', 'package.json'))).version;

const r = await esbuild.build({
  stdin: { contents: "export * from './ifc/api.js';\nexport { default as Manifold } from 'manifold-3d';\n", resolveDir: vend, loader: 'js' },
  nodePaths: [mod], bundle: true, format: 'iife', globalName: 'BIMIFC', target: 'es2020', platform: 'browser',
  minify: true, legalComments: 'none', charset: 'ascii', write: false, logLevel: 'warning',
  // Manifold's loader reaches for node:module only when it runs in Node; in a browser that branch never runs
  external: ['node:*'],
  // Manifold works out its wasm's address from import.meta.url; a classic script has none, so it is given a fixed
  // base that is never fetched (the app always hands it the address, locateFile)
  define: { 'import.meta.url': '"https://bim-ifc.invalid/manifold.js"' }
});
const banner =
  '/* __acad3dV196: cc-ifc, the IFC engine of BimCraft (github.com/getcadcraft/bimcraft @ ' + REV + ', app/ifc, Apache-2.0,\n' +
  '   Copyright 2026 The Data Design Group, Inc.; see NOTICE), and Manifold ' + MANIFOLD + ' (github.com/elalish/manifold,\n' +
  '   Apache-2.0), every file unchanged, bundled into one classic script by esbuild ' + ebver + ' (tools/ifc/build_ifc.mjs).\n' +
  '   Its only global is BIMIFC. The licences are beside this file. */\n';
const text = banner + r.outputFiles[0].text;
const dir = path.join(root, 'runtime', 'cc-ifc', REV);
const out = path.join(dir, 'bim-ifc.min.js');
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');

if (process.argv.includes('--check')) {
  const have = fs.existsSync(out) ? read(out) : '';
  if (have !== text) { console.error('runtime/cc-ifc/' + REV + '/bim-ifc.min.js is not what this script builds'); process.exit(1); }
  console.log('runtime/cc-ifc/' + REV + '/bim-ifc.min.js is what tools/ifc builds: ' + Buffer.byteLength(text) + ' bytes');
  process.exit(0);
}

fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(out, text);
fs.copyFileSync(path.join(vend, 'LICENSE'), path.join(dir, 'LICENSE'));
fs.copyFileSync(path.join(vend, 'NOTICE'), path.join(dir, 'NOTICE'));
fs.copyFileSync(path.join(mod, 'manifold-3d', 'manifold.wasm'), path.join(dir, 'manifold.wasm'));
const mlic = ['LICENSE', 'LICENSE.txt'].map((f) => path.join(mod, 'manifold-3d', f)).find((f) => fs.existsSync(f));
if (!mlic) { console.error('no LICENSE in manifold-3d'); process.exit(1); }
fs.copyFileSync(mlic, path.join(dir, 'MANIFOLD-LICENSE'));

const manPath = path.join(root, 'runtime', 'MANIFEST.json');
const man = JSON.parse(read(manPath));
const lock = JSON.parse(read(path.join(here, 'package-lock.json')));
const integrity = (lock.packages['node_modules/manifold-3d'] || {}).integrity || '';
const entry = (rel, from, licence) => {
  const b = fs.readFileSync(path.join(root, 'runtime', rel));
  return { path: rel, bytes: b.length, sha256: sha(b), from, licence };
};
const base = 'cc-ifc/' + REV + '/', up = 'getcadcraft/bimcraft@' + REV;
const mine = [
  entry(base + 'LICENSE', up + ', LICENSE', 'Apache-2.0 (cc-ifc)'),
  entry(base + 'NOTICE', up + ', NOTICE', 'Apache-2.0 (cc-ifc)'),
  entry(base + 'MANIFOLD-LICENSE', 'npm manifold-3d@' + MANIFOLD + ', LICENSE (the tarball ' + integrity + ')', 'Apache-2.0 (Manifold)'),
  entry(base + 'manifold.wasm', 'npm manifold-3d@' + MANIFOLD + ', manifold.wasm (the tarball ' + integrity + ')', 'Apache-2.0 (Manifold)'),
  entry(base + 'bim-ifc.min.js', up + ' app/ifc (vendor/cc-ifc) and npm manifold-3d@' + MANIFOLD + ', bundled unchanged by esbuild ' +
    ebver + ': tools/ifc/build_ifc.mjs', 'Apache-2.0 (cc-ifc, Manifold)')
];
man['cc-ifc'] = REV;
man.files = man.files.filter((f) => !/^cc-ifc\//.test(f.path)).concat(mine);
fs.writeFileSync(manPath, JSON.stringify(man, null, 1) + '\n');

const b = fs.readFileSync(out);
console.log('runtime/cc-ifc/' + REV + '/bim-ifc.min.js: ' + b.length + ' bytes');
console.log('sha256 ' + sha(b));
console.log('sri    sha256-' + crypto.createHash('sha256').update(b).digest('base64'));
