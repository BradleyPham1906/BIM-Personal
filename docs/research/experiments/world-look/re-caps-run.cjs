// Research experiment runner, not a suite: loads re-caps.html in headless Chromium and writes what it reports.
//   node docs/research/experiments/world-look/re-caps-run.cjs
const path = require('path'), fs = require('fs');
let pw; try { pw = require('playwright'); } catch (e) { pw = require('/opt/node-tools/node_modules/playwright'); }
(async () => {
  const out = { date: new Date().toISOString() };
  for (const [name, opts] of [['default', {}], ['enable-unsafe-webgpu', { args: ['--enable-unsafe-webgpu'] }]]) {
    const b = await pw.chromium.launch(opts);
    const p = await b.newPage();
    await p.goto('file://' + path.join(__dirname, 're-caps.html'));
    await p.waitForFunction(() => window.__result, null, { timeout: 60000 });
    out[name] = await p.evaluate(() => window.__result);
    out[name].browser = b.version();
    await b.close();
  }
  fs.writeFileSync(path.join(__dirname, 're-caps-results.json'), JSON.stringify(out, null, 1));
  const d = out.default;
  console.log(JSON.stringify({ renderer: d.renderer, multiDraw: d.multiDraw, compressed: d.compressed, timer: d.timerQuery,
    sameTask: d.queryAvailableInSameTask, frames: d.queryFramesToResult, ms: d.queryMsToResult, webgpu: d.webgpu,
    webgpuFlag: out['enable-unsafe-webgpu'].webgpu, webgl1: [d.webgl1Instancing, d.webgl1FloatTex, d.webgl1VertexTexUnits] }));
})();
