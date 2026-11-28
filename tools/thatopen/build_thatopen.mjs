// tools/thatopen/build_thatopen.mjs -- V206: That Open Engine and web-ifc as classic scripts, for the Review view and
// the IFC import (docs/research/research-thatopen.md, the owner's decisions 2026-11-13).
//
// The engine is ES5 in one closure and must also run from file://, where a browser refuses a module and a fetch of a
// .wasm, so three files are written to runtime/thatopen/<ver>/, each library unchanged, by esbuild:
//   bim-webifc.min.js     web-ifc (MPL-2.0) alone, so its file stays its own; its only global is BIMWEBIFC
//   bim-webifc-wasm.js    web-ifc.wasm as base64 in BIMWEBIFC_WASM: the adapter hands it to web-ifc through a fetch
//                         wrapper, which is what works from file:// (e01, F12)
//   bim-thatopen.min.js   @thatopen/components, components-front and fragments (MIT) with their MIT/ISC/BSD/
//                         Apache-2.0 dependencies; its only global is BIMTOE. "three" is the app's own BIMTHREE
//                         (runtime/three), "web-ifc" is BIMWEBIFC; three/webgpu, three/tsl and potree-core are left out
//                         and throw if reached (WebGPU-only paths, point clouds: research F8, F14)
// The licence of every package in the bundles is written beside them. runtime/MANIFEST.json pins every file by size
// and SHA-256 (tools/check_runtime.py); this script writes their entries, so the manifest cannot fall behind.
//
//   cd tools/thatopen && npm ci --ignore-scripts     (the versions are pinned in package.json and its lock)
//   node build_thatopen.mjs            writes the files, the licences and the manifest's entries
//   node build_thatopen.mjs --check    builds in memory and fails when a committed file differs
import * as esbuild from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const PINS = { '@thatopen/components': '3.6.0', '@thatopen/components-front': '3.6.1', '@thatopen/fragments': '3.6.1',
  'web-ifc': '0.0.79', 'camera-controls': '3.1.2', three: '0.186.1' };
const VER = PINS['@thatopen/components'];
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const mod = path.join(here, 'node_modules');
const read = (p) => fs.readFileSync(p, 'utf8');
const pkg = (n) => JSON.parse(read(path.join(mod, n, 'package.json')));
if (!fs.existsSync(path.join(mod, '@thatopen', 'components'))) { console.error('Run npm ci --ignore-scripts in tools/thatopen first'); process.exit(2); }
for (const n of Object.keys(PINS)) {
  const v = pkg(n).version;
  if (v !== PINS[n]) { console.error(n + ' is ' + v + ', expected ' + PINS[n]); process.exit(2); }
}
const ebver = pkg('esbuild').version;

// "three" and "web-ifc" are the page's globals; three/webgpu, three/tsl and potree-core are left out
const globals = { name: 'globals', setup(b) {
  b.onResolve({ filter: /^three$/ }, () => ({ path: 'BIMTHREE', namespace: 'g' }));
  b.onResolve({ filter: /^web-ifc$/ }, () => ({ path: 'BIMWEBIFC', namespace: 'g' }));
  b.onResolve({ filter: /^(three\/(webgpu|tsl)|potree-core)$/ }, (a) => ({ path: a.path, namespace: 'out' }));
  b.onLoad({ filter: /.*/, namespace: 'g' }, (a) => ({ contents: 'module.exports = window.' + a.path, loader: 'js' }));
  b.onLoad({ filter: /.*/, namespace: 'out' }, (a) => ({ contents: "throw new Error('" + a.path + " is left out of the app\\'s That Open build')", loader: 'js' }));
} };
const common = { nodePaths: [mod], absWorkingDir: here, bundle: true, format: 'iife', target: 'es2020', platform: 'browser',
  minify: true, legalComments: 'none', charset: 'ascii', write: false, logLevel: 'warning', metafile: true };

const toe = await esbuild.build(Object.assign({}, common, {
  stdin: { contents: "import '@thatopen/fragments/inline';\n" +
    "export * as FRAGS from '@thatopen/fragments';\nexport * as OBC from '@thatopen/components';\n" +
    "export * as OBF from '@thatopen/components-front';\n", resolveDir: here, loader: 'js' },
  globalName: 'BIMTOE', plugins: [globals] }));
const wif = await esbuild.build(Object.assign({}, common, {
  stdin: { contents: "export * from 'web-ifc';\n", resolveDir: here, loader: 'js' }, globalName: 'BIMWEBIFC',
  // web-ifc reaches for Node's modules only when it runs in Node; in a browser that branch never runs
  external: ['fs', 'path', 'url', 'module', 'worker_threads', 'os', 'crypto', 'node:*'] }));

// the packages each bundle holds, from esbuild's metafile, so every one's licence is written beside it
function packagesOf(r) {
  const s = new Set();
  for (const f of Object.keys(r.metafile.inputs)) {
    const m = /node_modules\/((?:@[^/]+\/)?[^/]+)\//.exec(f);
    if (m) s.add(m[1]);
  }
  // the @thatopen dists carry their own dependencies inline (jszip, three-mesh-bvh, pako, flatbuffers...), which
  // esbuild never sees as packages: each declared dependency, and theirs, is added so its licence ships too
  const todo = [...s];
  while (todo.length) {
    const n = todo.pop(), d = pkg(n).dependencies || {};
    for (const k of Object.keys(d)) if (!s.has(k) && fs.existsSync(path.join(mod, k, 'package.json'))) { s.add(k); todo.push(k); }
  }
  return [...s].sort();
}
// the licences CLAUDE.md's library rule allows; pako's "MIT AND Zlib" is MIT plus the zlib licence (permissive, recorded
// for the owner: research-thatopen-gap.md part 11); jszip is dual and used under its MIT option
const allowed = /^(MIT|ISC|BSD-[23]-Clause|Apache-2\.0|MPL-2\.0|\(MIT OR GPL-3\.0-or-later\)|\(MIT AND Zlib\))$/;
const pkgsToe = packagesOf(toe), pkgsWif = packagesOf(wif);
const licences = [];
for (const n of [...new Set(pkgsToe.concat(pkgsWif))].sort()) {
  const p = pkg(n), lic = typeof p.license === 'string' ? p.license : (p.license && p.license.type) || '';
  if (!allowed.test(lic)) { console.error(n + ': licence "' + lic + '" is not one the rule allows'); process.exit(1); }
  // That Open's npm packages carry no licence file: theirs is kept in licences/, from the repositories (ThatOpen/
  // engine_components @ 6bedaa4 for components and components-front, ThatOpen/engine_fragment @ 643d24e for fragments)
  const f = ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'LICENSE.markdown', 'license', 'LICENCE', 'license.md'].map((x) => path.join(mod, n, x))
    .concat([path.join(here, 'licences', n.replace('@', '').replace('/', '-') + '.md')]).find((x) => fs.existsSync(x));
  // a package that declares its licence but ships no file: the declaration and its author are recorded instead
  const au = p.author ? (typeof p.author === 'string' ? p.author : [p.author.name, p.author.email].filter(Boolean).join(' ')) : '';
  const text = f ? read(f) : 'No licence file in the package. Its package.json declares "' + lic + '"' +
    (au ? ', author ' + au : '') + (p.repository ? ', source ' + (p.repository.url || p.repository) : '') + '.';
  if (!f) console.warn(n + ': no licence file, its declared licence ' + lic + ' recorded');
  licences.push({ n, v: p.version, lic, text });
}
const credits = 'Packages in bim-thatopen.min.js and bim-webifc.min.js, each unchanged, bundled by esbuild ' + ebver +
  ' (tools/thatopen/build_thatopen.mjs). web-ifc is MPL-2.0 and is its own file, bim-webifc.min.js; its source is\n' +
  'https://github.com/ThatOpen/engine_web-ifc. jszip is used under its MIT option.\n\n' +
  licences.map((l) => '==== ' + l.n + ' ' + l.v + ' (' + l.lic + ')\n\n' + l.text.trim() + '\n').join('\n');

const bannerToe = '/* __acad3dV206: That Open Engine, @thatopen/components ' + PINS['@thatopen/components'] +
  ', components-front ' + PINS['@thatopen/components-front'] + ', fragments ' + PINS['@thatopen/fragments'] +
  ' (github.com/ThatOpen, MIT), with their\n   dependencies, every file unchanged, bundled by esbuild ' + ebver +
  ' into one classic script (tools/thatopen/build_thatopen.mjs). Its only global is BIMTOE;\n' +
  '   it runs on the page\'s BIMTHREE (three ' + PINS.three + ') and BIMWEBIFC. Licences: LICENSES.txt beside this file. */\n';
const bannerWif = '/* __acad3dV206: web-ifc ' + PINS['web-ifc'] + ' (github.com/ThatOpen/engine_web-ifc, MPL-2.0), unchanged, as one classic\n' +
  '   script by esbuild ' + ebver + ' (tools/thatopen/build_thatopen.mjs). Its only global is BIMWEBIFC. Licence: LICENSES.txt. */\n';
const wasm = fs.readFileSync(path.join(mod, 'web-ifc', 'web-ifc.wasm'));
const files = {
  'bim-thatopen.min.js': bannerToe + toe.outputFiles[0].text,
  'bim-webifc.min.js': bannerWif + wif.outputFiles[0].text,
  'bim-webifc-wasm.js': '/* __acad3dV206: web-ifc ' + PINS['web-ifc'] + "'s web-ifc.wasm (MPL-2.0, unchanged), as base64, for file:// pages. */\n" +
    'var BIMWEBIFC_WASM="' + wasm.toString('base64') + '";\n',
  'LICENSES.txt': credits
};
const dir = path.join(root, 'runtime', 'thatopen', VER);
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');

if (process.argv.includes('--check')) {
  let bad = 0;
  for (const f of Object.keys(files)) {
    const p = path.join(dir, f), have = fs.existsSync(p) ? read(p) : '';
    if (have !== files[f]) { console.error('runtime/thatopen/' + VER + '/' + f + ' is not what this script builds'); bad++; }
  }
  if (bad) process.exit(1);
  console.log('runtime/thatopen/' + VER + '/ is what tools/thatopen builds');
  process.exit(0);
}

fs.mkdirSync(dir, { recursive: true });
for (const f of Object.keys(files)) fs.writeFileSync(path.join(dir, f), files[f]);

const manPath = path.join(root, 'runtime', 'MANIFEST.json');
const man = JSON.parse(read(manPath));
const lock = JSON.parse(read(path.join(here, 'package-lock.json')));
const tb = (n) => 'npm ' + n + '@' + pkg(n).version + ' (the tarball ' + ((lock.packages['node_modules/' + n] || {}).integrity || '') + ')';
const from = {
  'bim-thatopen.min.js': pkgsToe.filter((n) => /^@thatopen\//.test(n)).map(tb).join(', ') + ' and ' +
    pkgsToe.filter((n) => !/^@thatopen\//.test(n)).join(', ') + ', bundled unchanged by esbuild ' + ebver + ': tools/thatopen/build_thatopen.mjs',
  'bim-webifc.min.js': tb('web-ifc') + ', web-ifc-api.js, bundled unchanged by esbuild ' + ebver + ': tools/thatopen/build_thatopen.mjs',
  'bim-webifc-wasm.js': tb('web-ifc') + ', web-ifc.wasm as base64: tools/thatopen/build_thatopen.mjs',
  'LICENSES.txt': 'the licence file of every package bundled: tools/thatopen/build_thatopen.mjs'
};
const licOf = { 'bim-thatopen.min.js': 'MIT (That Open) and the licences in LICENSES.txt', 'bim-webifc.min.js': 'MPL-2.0 (web-ifc)',
  'bim-webifc-wasm.js': 'MPL-2.0 (web-ifc)', 'LICENSES.txt': 'as listed in it' };
const mine = Object.keys(files).map((f) => {
  const rel = 'thatopen/' + VER + '/' + f, b = fs.readFileSync(path.join(root, 'runtime', rel));
  return { path: rel, bytes: b.length, sha256: sha(b), from: from[f], licence: licOf[f] };
});
man.thatopen = VER;
man.files = man.files.filter((f) => !/^thatopen\//.test(f.path)).concat(mine);
fs.writeFileSync(manPath, JSON.stringify(man, null, 1) + '\n');
for (const f of Object.keys(files)) {
  const b = fs.readFileSync(path.join(dir, f));
  console.log('runtime/thatopen/' + VER + '/' + f + ': ' + b.length + ' bytes, sri sha256-' + crypto.createHash('sha256').update(b).digest('base64'));
}
console.log('packages: ' + licences.map((l) => l.n + ' ' + l.v + ' ' + l.lic).join('; '));
