// e02 runner: node run.mjs <dir of .ifc files> -- loads page.html over http and from file://, prints results
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url)), root = path.resolve(here, '../../../../..');
const dir = process.argv[2], files = fs.readdirSync(dir).filter((f) => f.endsWith('.ifc')).sort();
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': p.endsWith('.html') ? 'text/html' : 'text/javascript' }); fs.createReadStream(p).pipe(r); });
await new Promise((r) => srv.listen(0, '127.0.0.1', r));
const httpUrl = 'http://127.0.0.1:' + srv.address().port + '/docs/research/experiments/thatopen/e02/page.html';
const fileUrl = 'file://' + path.join(here, 'page.html');
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
console.log('Chromium ' + browser.version());
for (const [mode, url, classic] of [['http, module worker', httpUrl, false], ['file://, classic worker', fileUrl, true]]) {
  for (const f of files) {
    const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
    const errs = []; page.on('pageerror', (e) => errs.push(String(e))); page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text().slice(0, 200)); });
    await page.goto(url);
    const bytes = [...fs.readFileSync(path.join(dir, f))];
    let res;
    try { res = await Promise.race([page.evaluate(([b, c]) => window.e02(b, { classic: c }), [bytes, classic]), new Promise((_, j) => setTimeout(() => j(new Error('timeout 90 s')), 90000))]); }
    catch (e) { res = { error: String(e).slice(0, 300) }; }
    let ink = null;
    if (!res.error) { const png = await page.screenshot(); ink = png.length; }
    console.log(JSON.stringify({ mode, file: f, ...res, screenshotBytes: ink, errors: errs.slice(0, 3) }));
    if (f === files[0] && !res.error) await page.screenshot({ path: path.join(process.argv[3] || here, 'shot-' + (classic ? 'file' : 'http') + '.png') });
    await page.close();
  }
}
await browser.close(); srv.close();
