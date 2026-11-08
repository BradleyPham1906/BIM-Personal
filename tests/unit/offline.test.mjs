// V172h, core/offline.js, src/sw/sw.js and tools/build_pwa.py: installable and offline
// (docs/research/research-local-storage.md, part 15; option C, the owner's Q1-Q7).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, mkdtempSync, readdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import { loadEngine } from './helpers/engine.mjs';

const E = loadEngine();
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

test('the page registers the worker only on the site, over https or this machine, never under v/', () => {
  const meta = {};
  const at = (protocol, hostname, pathname) => ({ protocol, hostname, pathname });
  assert.equal(E.bimSwWanted(at('https:', 'bradleypham1906.github.io', '/BIM-Personal/'), meta, true), true);
  assert.equal(E.bimSwWanted(at('http:', 'localhost', '/BIM-Personal/'), meta, true), true);
  assert.equal(E.bimSwWanted(at('http:', '127.0.0.1', '/'), meta, true), true);
  assert.equal(E.bimSwWanted(at('http:', 'example.com', '/'), meta, true), false, 'plain http elsewhere: no worker');
  assert.equal(E.bimSwWanted(at('file:', '', '/x/canvas_v10.html'), meta, true), false, 'file://: no worker (part 4.4)');
  assert.equal(E.bimSwWanted(at('https:', 'h', '/BIM-Personal/v/v171/index.html'), meta, true), false, 'a kept build');
  assert.equal(E.bimSwWanted(at('https:', 'h', '/BIM-Personal/'), null, true), false, 'no meta: the one-file build');
  assert.equal(E.bimSwWanted(at('https:', 'h', '/BIM-Personal/'), meta, false), false, 'no serviceWorker');
});

test('unsaved work is work not yet in the database (Q1), and any tab with it holds the update (Q4)', () => {
  assert.equal(E.bimSwUnsavedOf(null, { dirty: false }), false);
  assert.equal(E.bimSwUnsavedOf(123, { dirty: false }), true, 'a save waiting for its debounce');
  assert.equal(E.bimSwUnsavedOf(null, { dirty: true }), true);
  assert.equal(E.bimSwUnsavedOf(null, { inflight: {} }), true, 'a record being written');
  assert.equal(E.bimSwUnsavedOf(null, { next: {} }), true, 'a record waiting');
  assert.equal(E.bimSwUnsavedOf(null, { busy: true }), true);
  assert.equal(E.bimSwUnsavedOf(null, null), false);
  assert.equal(E.bimSwAnyUnsaved({}), false);
  assert.equal(E.bimSwAnyUnsaved({ a: false, b: false }), false);
  assert.equal(E.bimSwAnyUnsaved({ a: false, b: true }), true);
});

function workerRules() {
  const ctx = {};
  vm.runInNewContext(readFileSync(join(ROOT, 'src', 'sw', 'sw.js'), 'utf8'), ctx);
  return ctx;
}

test('the worker answers the page and the bundles from its cache, the runtime from its own, the rest from the network', () => {
  const W = workerRules();
  const s = 'https://bradleypham1906.github.io/BIM-Personal/';
  assert.equal(W.bimSwRoute(s, s, 'GET', 'navigate'), 'page');
  assert.equal(W.bimSwRoute(s + 'index.html', s, 'GET', 'navigate'), 'page');
  assert.equal(W.bimSwRoute(s + '?open=1', s, 'GET', 'navigate'), 'page');
  assert.equal(W.bimSwRoute(s + 'docs/index.html', s, 'GET', 'navigate'), null, 'the guide is in scope but not ours');
  assert.equal(W.bimSwRoute(s + 'v/v171/index.html', s, 'GET', 'navigate'), null);
  assert.equal(W.bimSwRoute(s + 'canvas_v10.html', s, 'GET', 'navigate'), null);
  assert.equal(W.bimSwRoute(s + 'app/engine.js?v=a3ad3b63adc9', s, 'GET', 'no-cors'), 'app');
  assert.equal(W.bimSwRoute(s + 'runtime/pyodide/pyodide.asm.wasm', s, 'GET', 'cors'), 'runtime');
  assert.equal(W.bimSwRoute(s + 'app/engine.js?v=1', s, 'POST', 'cors'), null);
  assert.equal(W.bimSwRoute('https://tile.openstreetmap.org/1/0/0.png', s, 'GET', 'no-cors'), null, 'tiles: never cached (H52)');
  assert.equal(W.bimSwRoute('https://bradleypham1906.github.io/Other/app/x.js', s, 'GET', 'cors'), null);
});

test('the worker keeps only whole answers, and never an HTML page for a script', () => {
  const W = workerRules();
  const res = (status, type, ok) => ({ status, ok: ok !== undefined ? ok : status >= 200 && status < 300, type: 'basic', headers: { get: () => type } });
  assert.equal(W.bimSwUsable(res(200, 'text/javascript'), 'app/engine.js?v=1'), true);
  assert.equal(W.bimSwUsable(res(200, 'text/html'), 'app/engine.js?v=1'), false, 'draw.io\'s guard');
  assert.equal(W.bimSwUsable(res(200, 'text/html; charset=utf-8'), 'app/app.css?v=1'), false);
  assert.equal(W.bimSwUsable(res(200, 'text/html'), 'index.html'), true);
  assert.equal(W.bimSwUsable(res(404, 'text/html'), 'index.html'), false);
  assert.equal(W.bimSwUsable(res(206, 'application/wasm', true), 'runtime/x.wasm'), false, 'a part is not the file');
  assert.equal(W.bimSwUsable({ ok: false, status: 0, type: 'opaque', headers: { get: () => '' } }, 'x'), false);
  assert.equal(W.bimSwUsable(null, 'x'), false);
  const shell = ['index.html', 'app/app.css?v=aa', 'app/engine.js?v=bb'];
  assert.equal(W.bimSwPageMatches('<link href="app/app.css?v=aa"><script src="app/engine.js?v=bb">', shell), true);
  assert.equal(W.bimSwPageMatches('<link href="app/app.css?v=aa"><script src="app/engine.js?v=cc">', shell), false,
    'a page of another build is not cached with these bundles');
});

function py(code) {
  return execFileSync('python3', ['-c', code], { cwd: ROOT, encoding: 'utf8' });
}

test('build_pwa: sw.js names this build\'s page and bundles, and changes with any bundle', () => {
  const out = JSON.parse(py(`
import json, sys; sys.path.insert(0, 'tools'); import build_pwa
a = '<head></head><link rel="stylesheet" href="app/app.css?v=111111111111" /><script src="app/engine.js?v=222222222222"></script>'
b = a.replace('222222222222', '333333333333')
sa, ba, sha = build_pwa.service_worker(a, 'rt1')
sb, bb, shb = build_pwa.service_worker(b, 'rt1')
print(json.dumps({'ba': ba, 'bb': bb, 'shell': sha, 'sa': sa}))`));
  assert.deepEqual(out.shell, ['index.html', 'app/app.css?v=111111111111', 'app/engine.js?v=222222222222']);
  assert.notEqual(out.ba, out.bb, 'a changed bundle is a new worker (H46: the browser compares bytes)');
  assert.match(out.sa, /var BIM_SW_BUILD = '[0-9a-f]{16}';/);
  assert.match(out.sa, /var BIM_SW_RUNTIME = 'rt1';/);
  const ctx = {};
  vm.runInNewContext(out.sa, ctx);
  assert.equal(ctx.BIM_SW_APP, 'BIM-Personal/app/' + out.ba, 'the cache is named with the app\'s path and the build');
});

test('build_pwa: the manifest, the icons and the page\'s tags', () => {
  const dir = mkdtempSync(join(tmpdir(), 'v172h-'));
  py(`
import sys, pathlib; sys.path.insert(0, 'tools'); import build_app, build_pwa
build_app.write_site(${JSON.stringify(dir)}); build_pwa.write(${JSON.stringify(dir)})`);
  const man = JSON.parse(readFileSync(join(dir, 'manifest.webmanifest'), 'utf8'));
  assert.equal(man.id, '/BIM-Personal/', 'the id resolves against the origin');
  assert.equal(man.display, 'standalone');
  assert.equal(man.scope, './');
  const sizes = man.icons.map((i) => i.sizes + ' ' + i.purpose).sort();
  assert.deepEqual(sizes, ['192x192 any', '512x512 any', '512x512 maskable']);
  for (const [name, size] of [['icon-192.png', 192], ['icon-512.png', 512], ['icon-maskable-512.png', 512], ['apple-touch-icon.png', 180]]) {
    const b = readFileSync(join(dir, 'icons', name));
    assert.equal(b.subarray(1, 4).toString('latin1'), 'PNG', name);
    assert.equal(b.readUInt32BE(16), size, name + ' width');
    assert.equal(b.readUInt32BE(20), size, name + ' height');
  }
  const page = readFileSync(join(dir, 'index.html'), 'utf8');
  for (const tag of ['rel="manifest"', 'name="theme-color"', 'rel="apple-touch-icon"', 'name="a3d-sw"']) {
    assert.equal(page.split(tag).length - 1, 1, tag + ' once');
  }
  assert.ok(readdirSync(dir).includes('sw.js'));
  assert.equal(readFileSync(join(ROOT, 'canvas_v10.html'), 'utf8').includes('<meta name="a3d-sw" content="sw.js" />'), false,
    'the one-file build never registers a worker');
});
