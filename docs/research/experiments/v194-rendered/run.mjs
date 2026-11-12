/* run.mjs -- V194 experiment e01: harness.html driven in Edge (or any Chromium) through the DevTools protocol with
   Node's own WebSocket, no dependencies (as tests/e2e/bim_phase174_boards_edge_check.mjs does).

     python -m http.server 8766 --bind 127.0.0.1                         (from the repository's root)
     msedge --headless=new --remote-debugging-port=9334 --user-data-dir=<a NEW empty folder> about:blank
     node docs/research/experiments/v194-rendered/run.mjs <a folder for the pictures>

   Each case is the harness with other settings; for each it prints what the harness measured and saves the picture.
   The pictures are not committed: results.txt records the numbers and what the pictures showed. */
import fs from 'node:fs';
const PORT = +(process.env.CDP_PORT || 9334), BASE = process.env.APP_BASE || 'http://127.0.0.1:8766', OUT = process.argv[2] || '.';
const PAGE = BASE + '/docs/research/experiments/v194-rendered/harness.html';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function target() {
  for (let i = 0; i < 40; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' }); return await r.json(); } catch (e) { await sleep(250); }
  }
  throw new Error('no browser on port ' + PORT);
}
async function connect(t) {
  const ws = new WebSocket(t.webSocketDebuggerUrl); let id = 0; const wait = {}, ev = [];
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && wait[d.id]) { wait[d.id](d); delete wait[d.id]; } else ev.push(d); };
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; wait[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
  return { send, ev, ws };
}
const C = await connect(await target());
await C.send('Runtime.enable'); await C.send('Log.enable'); await C.send('Page.enable');
await C.send('Emulation.setDeviceMetricsOverride', { width: 1500, height: 900, deviceScaleFactor: 1, mobile: false });
async function val(expr) {
  const r = await C.send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
  return r.result && r.result.result ? r.result.result.value : undefined;
}
const CASES = [
  ['clear', ''], ['first-pass', '?first=1'], ['overcast', '?sky=overcast'], ['low-sun', '?alt=5&az=250'], ['night', '?alt=-10'],
  ['white-edges', '?sky=white&edges=1'], ['plan', '?flat=1'], ['no-ground', '?ground=0'], ['best-256', '?n=256']
];
const only = process.argv[3];
for (const [name, qs] of CASES) {
  if (only && only !== name) continue;
  C.ev.length = 0;
  await C.send('Page.navigate', { url: PAGE + qs });
  let done = false;
  for (let i = 0; i < 240 && !done; i++) { await sleep(250); done = await val('window.__done===true'); }
  const res = await val('JSON.stringify(window.__result||null)');
  const logs = C.ev.filter((e) => e.method === 'Runtime.exceptionThrown' || (e.method === 'Log.entryAdded' && e.params.entry.level === 'error') ||
    (e.method === 'Runtime.consoleAPICalled' && (e.params.type === 'error' || e.params.type === 'warning')))
    .map((e) => e.method === 'Log.entryAdded' ? e.params.entry.text : (e.params.exceptionDetails ? e.params.exceptionDetails.text : (e.params.args || []).map((a) => a.value || a.description || '').join(' ')));
  const shot = await C.send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`${OUT}/${name}.png`, Buffer.from(shot.result.data, 'base64'));
  console.log(name + ' ' + (done ? res : 'DID NOT FINISH') + (logs.length ? ' CONSOLE ' + JSON.stringify(logs.slice(0, 6)) : ''));
}
C.ws.close();
