// tools/bimcraft/build_bimcraft.mjs -- BimCraft's BIM-authoring core as one classic script (the owner, 2026-11-28: "copy
// their code"). vendor/bimcraft/app (copied unchanged by copy_upstream.mjs) is bundled, unchanged, by esbuild into
// runtime/bimcraft/<rev>/bim-craft.min.js, whose only global is BIMCRAFT: one namespace per root module (BIMCRAFT.modelWalls,
// BIMCRAFT.familyModel, BIMCRAFT.ifc for their cc-ifc, ...). Its licence and notice are written beside it, and
// runtime/MANIFEST.json pins it (tools/check_runtime.py).
// Left out, each a module that throws if reached: manifold-3d (the engine is handed the Manifold the app already ships,
// runtime/cc-ifc, the same 3.5.4: api.Init({manifold})), and tin.js with its delaunator and robust-predicates (terrain
// under a house, loaded only on demand by res-terrain.js; robust-predicates' Unlicense is not in the library rule's list).
// Workers: the bundle has no import.meta, so their cc-ifc reads and meshes on the page (open-async.js 49 and
// mesh-stream.js 24 fall back), as BimCraft's own Node tests run it.
//   cd tools/bimcraft && npm ci --ignore-scripts && node build_bimcraft.mjs [--check]
import * as esbuild from 'esbuild';
import fs from 'node:fs'; import path from 'node:path'; import crypto from 'node:crypto'; import { fileURLToPath } from 'node:url';
import { REV, ROOTS } from './roots.mjs';
const here = path.dirname(fileURLToPath(import.meta.url)), root = path.resolve(here, '..', '..');
const vend = path.join(root, 'vendor', 'bimcraft'), app = path.join(vend, 'app'), mod = path.join(here, 'node_modules');
if (!fs.existsSync(path.join(mod, 'esbuild'))) { console.error('Run npm ci --ignore-scripts in tools/bimcraft first'); process.exit(2); }
const ebver = JSON.parse(fs.readFileSync(path.join(mod, 'esbuild', 'package.json'), 'utf8')).version;
const nameOf = (f) => f.replace(/\.js$/, '').replace(/^ifc\/api$/, 'ifc').replace(/[\/-]([a-z])/g, (m, c) => c.toUpperCase());
// the English catalog for i18n.js, cut to the key families the copied code names (a key is often built at run time,
// 'model.ot.' + a type's key, so whole families are kept: every key whose first part is quoted in the code as 'part.)
const codeText = fs.readdirSync(app, { recursive: true }).filter((f) => /\.js$/.test(f)).map((f) => fs.readFileSync(path.join(app, f), 'utf8')).join('\n');
const families = new Set([...codeText.matchAll(/['"`]([a-z0-9]+)\./g)].map((m) => m[1]));
const en = JSON.parse(fs.readFileSync(path.join(app, 'lang', 'en.json'), 'utf8')), strings = {};
for (const k of Object.keys(en)) if (k.charAt(0) !== '@' && families.has(k.split('.')[0])) strings[k] = en[k];
const entry = "import { init as __bimI18n } from './i18n.js';\n__bimI18n({ locale: 'en', strings: " + JSON.stringify(strings) + " });\n" +
  ROOTS.map((f) => "export * as " + nameOf(f) + " from './" + f + "';").join('\n') + '\n';
const leftOut = { name: 'left-out', setup(b) {
  b.onResolve({ filter: /^(manifold-3d|delaunator|robust-predicates)$/ }, (a) => ({ path: a.path, namespace: 'out' }));
  b.onResolve({ filter: /(^|\/)tin\.js$/ }, (a) => ({ path: 'tin.js', namespace: 'out' }));
  b.onLoad({ filter: /.*/, namespace: 'out' }, (a) => ({ contents: "throw new Error('" + a.path + " is left out of the app\\'s BimCraft build')", loader: 'js' }));
} };
const r = await esbuild.build({ stdin: { contents: entry, resolveDir: app, loader: 'js' }, bundle: true, format: 'iife',
  globalName: 'BIMCRAFT', target: 'es2020', platform: 'browser', minify: true, legalComments: 'none', charset: 'ascii',
  write: false, logLevel: 'error', plugins: [leftOut], define: { 'import.meta.url': '"https://bim-craft.invalid/app/index.js"' } });
const files = JSON.parse(JSON.stringify(ROOTS));
const banner = '/* __acad3dV308: BimCraft\'s BIM-authoring core (github.com/getcadcraft/bimcraft @ ' + REV + ', Apache-2.0, Copyright 2026\n' +
  '   The Data Design Group, Inc.; see NOTICE), every file unchanged (vendor/bimcraft), bundled into one classic script by\n' +
  '   esbuild ' + ebver + ' (tools/bimcraft/build_bimcraft.mjs). Its only global is BIMCRAFT. Its names are their trademarks and\n' +
  '   are not used for this app (TRADEMARKS.md). */\n';
const text = banner + r.outputFiles[0].text;
const dir = path.join(root, 'runtime', 'bimcraft', REV), out = path.join(dir, 'bim-craft.min.js');
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
if (process.argv.includes('--check')) {
  if (!fs.existsSync(out) || fs.readFileSync(out, 'utf8') !== text) { console.error('runtime/bimcraft/' + REV + '/bim-craft.min.js is not what this script builds'); process.exit(1); }
  console.log('runtime/bimcraft/' + REV + '/bim-craft.min.js is what tools/bimcraft builds'); process.exit(0);
}
fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(out, text);
for (const f of ['LICENSE', 'NOTICE']) fs.copyFileSync(path.join(vend, f), path.join(dir, f));
const manPath = path.join(root, 'runtime', 'MANIFEST.json'), man = JSON.parse(fs.readFileSync(manPath, 'utf8'));
const up = 'getcadcraft/bimcraft@' + REV, entryOf = (rel, from) => { const b = fs.readFileSync(path.join(root, 'runtime', rel)); return { path: rel, bytes: b.length, sha256: sha(b), from, licence: 'Apache-2.0 (BimCraft)' }; };
const base = 'bimcraft/' + REV + '/';
man.bimcraft = REV;
man.files = man.files.filter((f) => !/^bimcraft\//.test(f.path)).concat([
  entryOf(base + 'LICENSE', up + ', LICENSE'), entryOf(base + 'NOTICE', up + ', NOTICE'),
  entryOf(base + 'bim-craft.min.js', up + ' app/ (vendor/bimcraft, ' + files.length + ' roots and what they import), bundled unchanged by esbuild ' + ebver + ': tools/bimcraft/build_bimcraft.mjs')]);
fs.writeFileSync(manPath, JSON.stringify(man, null, 1) + '\n');
const b = fs.readFileSync(out);
console.log('runtime/bimcraft/' + REV + '/bim-craft.min.js: ' + b.length + ' bytes, sri sha256-' + crypto.createHash('sha256').update(b).digest('base64'));
console.log('namespaces: ' + ROOTS.map(nameOf).join(' '));
console.log('English strings: ' + Object.keys(strings).length + ' of ' + Object.keys(en).filter((k) => k.charAt(0) !== '@').length + ' (families: ' + [...families].filter((f) => Object.keys(strings).some((k) => k.startsWith(f + '.'))).length + ')');
