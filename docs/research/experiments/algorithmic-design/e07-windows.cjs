// e07 runner. Chromium only. Run: node docs/research/experiments/algorithmic-design/e07-windows.cjs
const { chromium } = require('playwright'); const http = require('http'); const fs = require('fs'); const path = require('path');
(async () => {
  const srv = http.createServer((q, a) => { a.writeHead(200, {'Content-Type': 'text/html'}); a.end(fs.readFileSync(path.join(__dirname, 'e07-page.html'))); });
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const b = await chromium.launch(); const res = {chromium: b.version()};
  const urls = {'file://': 'file://' + path.join(__dirname, 'e07-page.html'), 'http': 'http://127.0.0.1:' + srv.address().port + '/e07-page.html'};
  for(const k of Object.keys(urls)){ const ctx = await b.newContext(); const p = await ctx.newPage(); await p.goto(urls[k]);
    await p.click('#go'); await p.waitForFunction(() => window.e07result, null, {timeout: 15000}); res[k] = await p.evaluate(() => window.e07result); await ctx.close(); }
  // and for a phone: does a touch-emulating context open windows at all?
  const { devices } = require('playwright'); const ph = await b.newContext({...devices['Pixel 7']}); const pp = await ph.newPage(); await pp.goto(urls['http']);
  await pp.click('#go'); await pp.waitForFunction(() => window.e07result, null, {timeout: 15000}); res['http, Pixel 7 emulation'] = await pp.evaluate(() => window.e07result);
  await b.close(); srv.close(); console.log(JSON.stringify(res, null, 1));
})();
