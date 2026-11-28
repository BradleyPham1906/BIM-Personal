// e05 runner: node run.mjs [http|file]
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url)), root = path.resolve(here, '../../../../..'), mode = process.argv[2] || 'http';
const types = { '.html': 'text/html', '.js': 'text/javascript', '.wasm': 'application/wasm' };
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); });
await new Promise((r) => srv.listen(0, '127.0.0.1', r));
const base = mode === 'file' ? 'file://' + root : 'http://127.0.0.1:' + srv.address().port;
const b = await chromium.launch(); const p = await b.newPage(); const errs = [];
p.on('pageerror', (e) => errs.push(String(e).slice(0, 300)));
await p.goto(base + '/docs/research/experiments/bimcraft/e05/page.html');
const res = await p.evaluate((m) => window.e05({ manifold: m }), base + '/runtime/cc-ifc/cfbd948/manifold.wasm').catch((e) => ({ error: String(e).slice(0, 500) }));
console.log('e05 ' + mode + ', Chromium ' + b.version());
if (res.error) console.log('ERROR ' + res.error); else {
  for (const c of res.checks) console.log((c.ok ? 'PASS ' : 'FAIL ') + c.m + (c.d ? ' (' + c.d + ')' : ''));
  console.log(JSON.stringify({ manifold: res.manifoldLoaded, manifoldError: res.manifold, ifcBytes: res.ifcBytes, sheets: res.sheets, pdfPages: res.pdfPages, ms: res.ms }));
}
console.log('page errors: ' + (errs.length ? errs.join(' | ') : 'none'));
await b.close(); srv.close();
