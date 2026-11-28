// e02 probe: one file's items by local id: getItemsData with and without relations, and getGuidsByLocalIds
//   node probe-ids.mjs <file.ifc> <id,id,...>
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--js-flags=--max-old-space-size=6144'] });
const page = await browser.newPage(); page.on('pageerror', (e) => console.log('pageerror', String(e)));
await page.goto('file://' + path.join(here, 'page.html'));
const ids = process.argv[3].split(',').map(Number);
const out = await page.evaluate(async ([b64, ids]) => {
  const bin = atob(b64), b = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) b[i] = bin.charCodeAt(i);
  const OBC = BIMTOE.OBC, FRAGS = BIMTOE.FRAGS, c = new OBC.Components(), fm = c.get(OBC.FragmentsManager);
  fm.init(await FRAGS.toClassicWorker(await FRAGS.FragmentsModels.getWorker()), { classicWorker: true });
  const ld = c.get(OBC.IfcLoader); await ld.setup({ autoSetWasm: false, wasm: { path: 'https://bim-webifc.invalid/', absolute: true } });
  const m = await ld.load(b, false, 'm');
  const safe = (o) => { const s = new WeakSet(); return JSON.stringify(o, (k, x) => { if (x && typeof x === 'object') { if (s.has(x)) return '[cycle]'; s.add(x); } return x; }); };
  const plain = await m.getItemsData(ids, { attributesDefault: true });
  const rel = await m.getItemsData(ids, { attributesDefault: true, relations: { IsDefinedBy: { attributes: true, relations: true } } }).catch((e) => 'error ' + e);
  const relOff = await m.getItemsData(ids, { attributesDefault: true, relations: { IsDefinedBy: { attributes: true, relations: true }, DefinesOccurrence: { attributes: false, relations: false } } }).catch((e) => 'error ' + e);
  return { guids: await m.getGuidsByLocalIds(ids), plain: safe(plain).slice(0, 400), rel: typeof rel === 'string' ? rel : rel.length + ' items: ' + safe(rel).slice(0, 300),
    relOff: typeof relOff === 'string' ? relOff : relOff.length + ' items: ' + safe(relOff).slice(0, 300) };
}, [fs.readFileSync(process.argv[2]).toString('base64'), ids]);
for (const [k, v] of Object.entries(out)) console.log(k + ': ' + (typeof v === 'string' ? v : JSON.stringify(v)));
await browser.close();
