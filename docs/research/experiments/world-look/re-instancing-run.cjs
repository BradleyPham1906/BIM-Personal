// Research experiment runner (docs/research/research-world-look/rendering-efficiency.md), not a suite.
// Loads re-instancing.html in headless Chromium for each mode, N and animation, and writes the results.
//   node docs/research/experiments/world-look/re-instancing-run.cjs [runs]
// Headless Chromium here renders WebGL with SwiftShader (software): the numbers rank the methods, they do not
// predict a phone or a desktop GPU.
const path = require('path');
const fs = require('fs');
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('/opt/node-tools/node_modules/playwright'); }
const page = 'file://' + path.join(__dirname, 're-instancing.html');
const RUNS = parseInt(process.argv[2] || '1', 10);
(async () => {
  const browser = await pw.chromium.launch();
  const out = { date: new Date().toISOString(), browser: browser.version(), runs: RUNS, results: [] };
  // what the browser offers: WebGPU's adapter, if any
  {
    const p = await browser.newPage();
    await p.goto(page + '?mode=instanced&n=1&secs=0.2');
    await p.waitForFunction(() => window.__result, null, { timeout: 60000 });
    out.webgpu = await p.evaluate(async () => {
      if (!navigator.gpu) return 'navigator.gpu absent';
      try { const a = await navigator.gpu.requestAdapter(); if (!a) return 'no adapter';
        const i = a.info || {}; return 'adapter: ' + [i.vendor, i.architecture, i.description].join(' / '); } catch (e) { return 'error ' + e.message; }
    });
    await p.close();
  }
  for (let run = 0; run < RUNS; run++) {
    for (const anim of ['0', '1']) {
      for (const n of [1000, 10000, 100000]) {
        for (const mode of ['single', 'merged', 'instanced']) {
          const p = await browser.newPage({ viewport: { width: 1280, height: 720 } });
          const errs = [];
          p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
          p.on('pageerror', (e) => errs.push(String(e)));
          await p.goto(page + '?mode=' + mode + '&n=' + n + '&anim=' + anim + '&secs=3');
          let r;
          try {
            await p.waitForFunction(() => window.__result, null, { timeout: 300000, polling: 500 });
            r = await p.evaluate(() => window.__result);
          } catch (e) { r = { mode, n, anim: anim === '1', error: String(e).slice(0, 200) }; }
          if (errs.length) r.errors = errs.slice(0, 3);
          r.run = run;
          out.results.push(r);
          console.log(JSON.stringify({ run, mode, n, anim, syncMedianMs: r.syncMedianMs && +r.syncMedianMs.toFixed(2),
            rafFps: r.rafFps && +r.rafFps.toFixed(1), setupMs: r.setupMs && +r.setupMs.toFixed(1), bytes: r.bytesUploaded,
            err: r.error || (r.errors && r.errors[0]) }));
          await p.close();
        }
      }
    }
  }
  out.renderer = (out.results.find((r) => r.renderer) || {}).renderer;
  out.vendor = (out.results.find((r) => r.vendor) || {}).vendor;
  fs.writeFileSync(path.join(__dirname, 're-instancing-results.json'), JSON.stringify(out, null, 1));
  await browser.close();
})();
