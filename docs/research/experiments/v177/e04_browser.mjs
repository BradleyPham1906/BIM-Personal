// V177 e04: the import's time in a real browser's worker. Serves the app's runtime/, V176's pinned wheels and the
// page, starts the browser headless, prints what the page measured.
//   node docs/research/experiments/v177/e04_browser.mjs "<path to msedge.exe or chrome.exe>" [profile dir]
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..', '..', '..');
const CACHE = process.env.IFCOS_CACHE || path.join(ROOT, '.cache', 'ifcos');
const TYPES = { '.js': 'text/javascript', '.html': 'text/html', '.wasm': 'application/wasm', '.json': 'application/json' };
let child = null;
const srv = http.createServer((q, s) => {
  if (q.method === 'POST') { let b = ''; q.on('data', (d) => b += d); q.on('end', () => { s.end('ok'); console.log(JSON.stringify(JSON.parse(b), null, 1)); child.kill(); srv.close(); process.exit(0); }); return; }
  const u = decodeURIComponent(q.url.split('?')[0]);
  const f = u.startsWith('/runtime/') ? path.join(ROOT, u) : u.startsWith('/wheels/') ? path.join(CACHE, path.basename(u)) : path.join(HERE, path.basename(u));
  fs.readFile(f, (e, b) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); s.end(b); });
});
srv.listen(8791, () => {
  const prof = process.argv[3] || fs.mkdtempSync(path.join(os.tmpdir(), 'e04-'));
  child = spawn(process.argv[2], ['--headless=new', '--disable-gpu', '--user-data-dir=' + prof, 'http://localhost:8791/e04_page.html'], { stdio: 'ignore' });
});
setTimeout(() => { console.log('no answer in 5 minutes'); if (child) child.kill(); process.exit(1); }, 300000);
