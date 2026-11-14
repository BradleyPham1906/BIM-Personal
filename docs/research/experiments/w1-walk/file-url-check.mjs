// W1 walkthrough research, experiment e02: can each engine load as one classic script from a file:// page, as
// three.js does (runtime/three, V194), and how long it takes to start there. Data, never a suite.
// Run from the folder of e01 (the packages installed, plus esbuild@0.25.10), with Playwright on the path:
//
//   node <repo>/docs/research/experiments/w1-walk/file-url-check.mjs
//
// Each engine is bundled unchanged by esbuild into an IIFE with one global (as tools/three does for three.js),
// written beside a blank page, and the page opened as file:// in Chromium. The page times the script's load and the
// engine's start (its WebAssembly compiled from the base64 the -compat builds carry), then reports both.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
const require = createRequire(path.join(process.cwd(), 'x.js'));   // the packages are where it is run, not here
const { chromium } = require('playwright'), esbuild = require('esbuild');
const out = path.join(process.cwd(), 'file-url-check');
fs.mkdirSync(out, { recursive: true });
const engines = [
  { name: 'rapier 0.21.0', file: 'rapier.js', global: 'BIMRAPIER', entry: "export * from '@dimforge/rapier3d-compat';",
    start: 'BIMRAPIER.init().then(function(){return typeof BIMRAPIER.World;})' },
  { name: 'jolt-physics 1.1.1', file: 'jolt.js', global: 'BIMJOLT', entry: "export { default } from 'jolt-physics/wasm-compat';",
    start: 'BIMJOLT.default().then(function(J){return typeof J.CharacterVirtual;})' },
];
const report = { chromium: null, engines: {} };
for (const e of engines) {
  const r = await esbuild.build({ stdin: { contents: e.entry, resolveDir: process.cwd(), loader: 'js' }, bundle: true, format: 'iife',
    globalName: e.global, target: 'es2020', platform: 'browser', minify: true, write: false, logLevel: 'error',
    external: ['node:*'] });   // Jolt's Emscripten output imports node:module on its Node path only; never reached in a page
  fs.writeFileSync(path.join(out, e.file), r.outputFiles[0].text);
  report.engines[e.name] = { bytes: r.outputFiles[0].contents.length };
}
fs.writeFileSync(path.join(out, 'index.html'), '<!doctype html><meta charset="utf-8"><title>e02</title><body>e02</body>');
const browser = await chromium.launch();
report.chromium = browser.version();
for (const e of engines) {
  const runs = [];
  for (let i = 0; i < 3; i++) {
    const page = await browser.newPage();
    const errs = []; page.on('pageerror', (x) => errs.push(String(x))); page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
    await page.goto(pathToFileURL(path.join(out, 'index.html')).href);
    const res = await page.evaluate(({ file, start }) => new Promise((ok) => {
      const t0 = performance.now(), s = document.createElement('script');
      s.src = file;
      s.onerror = () => ok({ loaded: false });
      s.onload = () => {
        const t1 = performance.now();
        Promise.resolve().then(() => eval(start)).then((what) => ok({ loaded: true, loadMs: t1 - t0, startMs: performance.now() - t1, what: String(what) }),
          (err) => ok({ loaded: true, loadMs: t1 - t0, startError: String(err) }));
      };
      document.head.appendChild(s);
    }), { file: e.file, start: e.start });
    res.errors = errs; runs.push(res); await page.close();
  }
  report.engines[e.name].runs = runs.map((r) => ({ ...r, loadMs: r.loadMs && +r.loadMs.toFixed(1), startMs: r.startMs && +r.startMs.toFixed(1) }));
}
await browser.close();
console.log(JSON.stringify(report, null, 1));
