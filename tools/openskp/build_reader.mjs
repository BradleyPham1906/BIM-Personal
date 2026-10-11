// tools/openskp/build_reader.mjs -- V163: the SketchUp reader the app inlines.
//
// openskp's TypeScript reader (MIT), at a pinned commit, bundled with its two runtime dependencies
// (fflate, MIT; earcut, ISC) by esbuild, then compiled to ES5 syntax by TypeScript, wrapped in a
// function of its own so its helpers are not globals of the page, and written ASCII-only to
// vendor/openskp/openskp_reader.es5.js. Phase/patch_phase163a.py inlines that file, by its hash.
//
//   git clone https://github.com/iamahsanmehmood/openskp /path/to/openskp
//   git -C /path/to/openskp checkout 359d1836c9665484c193635796a54aef004babac
//   cd tools/openskp && npm ci   (or npm install, with the versions pinned in package.json)
//   OPENSKP=/path/to/openskp node build_reader.mjs
//
// Only what reads a file is taken: parseSkp, buildScene, buildInstancedScene and SkpParseError.
// Writers, exporters and the Fragments code are left out by the bundler; their Node-only file
// helpers (fs, path) are marked external and are not reached by the reader.
import * as esbuild from 'esbuild';
import ts from 'typescript';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync } from 'child_process';

const COMMIT = '359d1836c9665484c193635796a54aef004babac';
const SRC = process.env.OPENSKP;
if (!SRC) { console.error('Set OPENSKP to a checkout of github.com/iamahsanmehmood/openskp'); process.exit(2); }
const head = execSync('git -C "' + SRC + '" rev-parse HEAD').toString().trim();
if (head !== COMMIT) { console.error('openskp is at ' + head + ', expected ' + COMMIT); process.exit(2); }

const here = path.dirname(new URL(import.meta.url).pathname);
const out = path.resolve(here, '../../vendor/openskp/openskp_reader.es5.js');
const tsrc = path.join(SRC, 'packages/typescript/src');
const entry = path.join(here, '.entry.ts');
fs.writeFileSync(entry,
  "export { parseSkp, buildScene, buildInstancedScene } from '" + path.join(tsrc, 'index') + "';\n" +
  "export { SkpParseError } from '" + path.join(tsrc, 'errors') + "';\n");

const r = await esbuild.build({
  entryPoints: [entry], bundle: true, format: 'iife', globalName: 'OpenSkp', target: 'es2017',
  platform: 'browser', external: ['fs', 'path'], minifyWhitespace: true, minifySyntax: true,
  treeShaking: true, write: false, legalComments: 'none', charset: 'ascii',
  nodePaths: [path.join(here, 'node_modules')], absWorkingDir: here, logLevel: 'warning'
});
fs.unlinkSync(entry);
const es2017 = r.outputFiles[0].text;
const es5 = ts.transpileModule(es2017, { compilerOptions: {
  target: ts.ScriptTarget.ES5, downlevelIteration: true, allowJs: true, removeComments: true,
  module: ts.ModuleKind.None, isolatedModules: false } }).outputText;

const pkg = (n) => JSON.parse(fs.readFileSync(path.join(here, 'node_modules', n, 'package.json'), 'utf8')).version;
// each copyright line as its own licence file states it
const owner = (file) => {
  const m = /^Copyright .*$/m.exec(fs.readFileSync(file, 'utf8'));
  if (!m) { console.error('no copyright line in ' + file); process.exit(1); }
  return m[0].trim();
};
const banner =
  '/* __acad3dV163: the SketchUp reader. openskp ' + COMMIT.slice(0, 7) + ' (github.com/iamahsanmehmood/openskp, MIT,\n' +
  '   ' + owner(path.join(SRC, 'LICENSE')) + '), its TypeScript reader only, with fflate ' + pkg('fflate') + ' (MIT,\n' +
  '   ' + owner(path.join(here, 'node_modules/fflate/LICENSE')) + ') and earcut ' + pkg('earcut') + ' (ISC, ' +
  owner(path.join(here, 'node_modules/earcut/LICENSE')) + '). Bundled by esbuild\n' +
  '   and compiled to ES5 syntax by TypeScript (tools/openskp/build_reader.mjs); it uses ES2015 built-ins\n' +
  '   (Map, Set, typed arrays, TextDecoder). The licences, which go with every copy of this page:\n' +
  [['openskp', path.join(SRC, 'LICENSE')], ['fflate', path.join(here, 'node_modules/fflate/LICENSE')],
   ['earcut', path.join(here, 'node_modules/earcut/LICENSE')]].map(([n, f]) =>
    '\n   ' + n + '\n' + fs.readFileSync(f, 'utf8').replace(/\*\//g, '* /').trim().split(/\r?\n/)
      .map((l) => (l.trim() ? '   ' + l : '')).join('\n') + '\n').join('') + '*/\n';
let body = banner + 'var OpenSkp=(function(){\n' + es5 + '\nreturn OpenSkp;\n})();\n';
// every character ASCII, and nothing that would end the script element it is inlined in
body = body.replace(/[^\x00-\x7e]/g, (c) => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0'));
if (/<\/script/i.test(body)) { console.error('the reader holds </script'); process.exit(1); }
fs.writeFileSync(out, body);
const sha = crypto.createHash('sha256').update(body).digest('hex');
console.log('wrote ' + path.relative(process.cwd(), out) + ' (' + body.length + ' bytes, sha256 ' + sha + ')');
