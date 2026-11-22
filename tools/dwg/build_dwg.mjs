// tools/dwg/build_dwg.mjs -- V252: BimCraft's DWG library (cc-dwg) as one classic script, for DWG open and save.
//
// cc-dwg (vendor/cc-dwg/dwg, Apache-2.0, docs/research/research-dwg-library.md) is ES modules. The engine is ES5 in
// one closure and must also run from file://, where a browser refuses a module, so the library is bundled, unchanged,
// by esbuild into one classic script whose only global is BIMDWG, and written with its licence to
// runtime/cc-dwg/<rev>/. runtime/MANIFEST.json pins every file by size and SHA-256 (tools/check_runtime.py); this
// script writes their entries, so the manifest cannot fall behind the files.
//
// It uses the esbuild that tools/ifc pins (one build tool, one version):
//   cd tools/ifc && npm ci --ignore-scripts
//   node tools/dwg/build_dwg.mjs            writes the bundle, the licence and the manifest's entries
//   node tools/dwg/build_dwg.mjs --check    builds in memory and fails when the committed bundle differs
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const REV = 'e36a94d';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const mod = path.join(root, 'tools', 'ifc', 'node_modules');
if (!fs.existsSync(path.join(mod, 'esbuild'))) { console.error('Run npm ci --ignore-scripts in tools/ifc first'); process.exit(2); }
const esbuild = createRequire(path.join(mod, 'x.js'))('esbuild');
const read = (p) => fs.readFileSync(p, 'utf8');
const ebver = JSON.parse(read(path.join(mod, 'esbuild', 'package.json'))).version;
const vend = path.join(root, 'vendor', 'cc-dwg');

const r = await esbuild.build({
  // index.js is readDwg, writeDwg and VERSIONS; read-async.js (its own worker) is left out: the app reads in its page
  stdin: { contents: "export * from './dwg/index.js';\n", resolveDir: vend, loader: 'js' },
  bundle: true, format: 'iife', globalName: 'BIMDWG', target: 'es2020', platform: 'browser',
  minify: true, legalComments: 'none', charset: 'ascii', write: false, logLevel: 'warning'
});
const banner =
  '/* __acad3dV252: cc-dwg, the DWG library of BimCraft (github.com/getcadcraft/bimcraft @ ' + REV + ', tests/lib/dwg,\n' +
  '   Apache-2.0, Copyright 2026 The Data Design Group, Inc.; see NOTICE), every file unchanged, bundled into one classic\n' +
  '   script by esbuild ' + ebver + ' (tools/dwg/build_dwg.mjs). Its only global is BIMDWG. The licence is beside this file. */\n';
const text = banner + r.outputFiles[0].text;
const dir = path.join(root, 'runtime', 'cc-dwg', REV);
const out = path.join(dir, 'bim-dwg.min.js');
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');

if (process.argv.includes('--check')) {
  const have = fs.existsSync(out) ? read(out) : '';
  if (have !== text) { console.error('runtime/cc-dwg/' + REV + '/bim-dwg.min.js is not what this script builds'); process.exit(1); }
  console.log('runtime/cc-dwg/' + REV + '/bim-dwg.min.js is what tools/dwg builds: ' + Buffer.byteLength(text) + ' bytes');
  process.exit(0);
}

fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(out, text);
fs.copyFileSync(path.join(vend, 'LICENSE'), path.join(dir, 'LICENSE'));
fs.copyFileSync(path.join(vend, 'NOTICE'), path.join(dir, 'NOTICE'));

const manPath = path.join(root, 'runtime', 'MANIFEST.json');
const man = JSON.parse(read(manPath));
const entry = (rel, from, licence) => {
  const b = fs.readFileSync(path.join(root, 'runtime', rel));
  return { path: rel, bytes: b.length, sha256: sha(b), from, licence };
};
const base = 'cc-dwg/' + REV + '/', up = 'getcadcraft/bimcraft@' + REV;
const mine = [
  entry(base + 'LICENSE', up + ', LICENSE', 'Apache-2.0 (cc-dwg)'),
  entry(base + 'NOTICE', up + ', NOTICE', 'Apache-2.0 (cc-dwg)'),
  entry(base + 'bim-dwg.min.js', up + ' tests/lib/dwg (vendor/cc-dwg), bundled unchanged by esbuild ' + ebver + ': tools/dwg/build_dwg.mjs',
    'Apache-2.0 (cc-dwg)')
];
man['cc-dwg'] = REV;
man.files = man.files.filter((f) => !/^cc-dwg\//.test(f.path)).concat(mine);
fs.writeFileSync(manPath, JSON.stringify(man, null, 1) + '\n');
const b = fs.readFileSync(out);
console.log('runtime/cc-dwg/' + REV + '/bim-dwg.min.js: ' + b.length + ' bytes');
console.log('sha256 ' + sha(b));
