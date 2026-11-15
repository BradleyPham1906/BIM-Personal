// e05 runner: opens e05-page.html from file:// and from a plain http server with no special headers
// (as GitHub Pages serves), and from one sending COOP/COEP. Chromium only; Firefox and Safari not available here.
// Run: node docs/research/experiments/algorithmic-design/e05-browser.cjs
const { chromium } = require('playwright'); const http = require('http'); const fs = require('fs'); const path = require('path');
const dir = __dirname;
function serve(headers){ return new Promise(r => { const s = http.createServer((q, a) => {
  const f = path.join(dir, path.basename(q.url.split('?')[0]));
  if(!fs.existsSync(f)){ a.writeHead(404); return a.end(); }
  a.writeHead(200, Object.assign({'Content-Type': f.endsWith('.js') ? 'text/javascript' : 'text/html'}, headers)); a.end(fs.readFileSync(f)); });
  s.listen(0, '127.0.0.1', () => r(s)); }); }
(async () => {
  const b = await chromium.launch(); const res = {chromium: b.version()};
  const plain = await serve({}), iso = await serve({'Cross-Origin-Opener-Policy':'same-origin','Cross-Origin-Embedder-Policy':'require-corp'});
  const urls = {'file://': 'file://' + path.join(dir, 'e05-page.html'),
    'http, no headers': 'http://127.0.0.1:' + plain.address().port + '/e05-page.html',
    'http, COOP+COEP': 'http://127.0.0.1:' + iso.address().port + '/e05-page.html'};
  for(const k of Object.keys(urls)){ const p = await b.newPage(); await p.goto(urls[k]); res[k] = await p.evaluate(() => window.e05()); await p.close(); }
  await b.close(); plain.close(); iso.close();
  console.log(JSON.stringify(res, null, 1));
})();
