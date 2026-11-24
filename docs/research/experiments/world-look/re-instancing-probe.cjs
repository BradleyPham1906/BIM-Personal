// Research experiment runner, not a suite: the second pass on re-instancing.html (2026-11-24).
// Adds the main thread's share of each frame (submitMedianMs), the merged buffer drawn through the instanced
// call with one instance (merged1), and a heavier tree (detail=8: 138 triangles) so per-instance work grows.
//   node docs/research/experiments/world-look/re-instancing-probe.cjs [runs]
// SwiftShader (software) renders here: the numbers rank the methods on this machine, they do not predict a phone.
const path = require('path'), fs = require('fs');
let pw; try { pw = require('playwright'); } catch (e) { pw = require('/opt/node-tools/node_modules/playwright'); }
const page = 'file://' + path.join(__dirname, 're-instancing.html');
const RUNS = parseInt(process.argv[2] || '2', 10);
const CASES = [];
for (const n of [1000, 10000, 100000]) for (const mode of ['single', 'merged', 'merged1', 'instanced']) CASES.push({ n, mode, detail: 1 });
for (const n of [1000, 10000]) for (const mode of ['single', 'merged', 'instanced']) CASES.push({ n, mode, detail: 8 });
(async () => {
  const browser = await pw.chromium.launch();
  const out = { date: new Date().toISOString(), browser: browser.version(), runs: RUNS, results: [] };
  for (let run = 0; run < RUNS; run++) for (const c of CASES) {
    const p = await browser.newPage({ viewport: { width: 1280, height: 720 } });
    await p.goto(page + '?mode=' + c.mode + '&n=' + c.n + '&detail=' + c.detail + '&anim=0&secs=3');
    let r;
    try { await p.waitForFunction(() => window.__result, null, { timeout: 300000, polling: 500 }); r = await p.evaluate(() => window.__result); }
    catch (e) { r = Object.assign({ error: String(e).slice(0, 200) }, c); }
    r.run = run; out.results.push(r);
    console.log(JSON.stringify({ run, n: c.n, mode: c.mode, detail: c.detail, tris: r.trisTotal, syncMedianMs: r.syncMedianMs && +r.syncMedianMs.toFixed(1),
      submitMedianMs: r.submitMedianMs && +r.submitMedianMs.toFixed(3), rafFps: r.rafFps && +r.rafFps.toFixed(1), err: r.error }));
    await p.close();
  }
  out.renderer = (out.results.find((r) => r.renderer) || {}).renderer;
  fs.writeFileSync(path.join(__dirname, 're-instancing-probe-results.json'), JSON.stringify(out, null, 1));
  await browser.close();
})();
