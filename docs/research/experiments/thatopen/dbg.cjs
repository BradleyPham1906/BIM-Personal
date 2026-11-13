const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  p.on('console', m => console.log('console:', m.text().slice(0,200)));
  p.on('pageerror', e => console.log('pageerror:', String(e.message).slice(0,200)));
  await p.goto(process.argv[2]);
  const r = await Promise.race([p.evaluate(m => RUN(m), process.argv[3]), new Promise(r => setTimeout(() => r('TIMEOUT 60s'), 60000))]);
  console.log(JSON.stringify(r)); await b.close();
})();
