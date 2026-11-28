// e02 probe: the shapes of That Open's data, for the import's reader (node probe.mjs <file.ifc>)
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage(); page.on('pageerror', (e) => console.log('pageerror', String(e)));
await page.goto('file://' + path.join(here, 'page.html'));
const bytes = [...fs.readFileSync(process.argv[2])];
const out = await page.evaluate(async (b) => {
  const T = window.BIMTHREE, OBC = BIMTOE.OBC, FRAGS = BIMTOE.FRAGS;
  const components = new OBC.Components(); const fm = components.get(OBC.FragmentsManager);
  fm.init(await FRAGS.toClassicWorker(await FRAGS.FragmentsModels.getWorker()), { classicWorker: true });
  const loader = components.get(OBC.IfcLoader);
  await loader.setup({ autoSetWasm: false, wasm: { path: 'https://bim-webifc.invalid/', absolute: true } });
  const model = await loader.load(new Uint8Array(b), false, 'm');
  const items = await model.getItemsWithGeometry(); const ids = [];
  for (const it of items) ids.push(await it.getLocalId());
  const geo = await model.getItemsGeometry(ids);
  const bb = new T.Box3(), v = new T.Vector3();
  geo.forEach((l) => l.forEach((m) => { if (!m.positions) return; for (let i = 0; i < m.positions.length; i += 3) bb.expandByPoint(v.set(m.positions[i], m.positions[i + 1], m.positions[i + 2]).applyMatrix4(m.transform)); }));
  const ob = new T.Box3().setFromObject(model.object);
  const sp = await model.getSpatialStructure();
  const storeyIds = []; (function w(n, cat) { if (cat === 'IFCBUILDINGSTOREY' && n.localId != null) storeyIds.push(n.localId); (n.children || []).forEach((k) => w(k, n.category || null)); })(sp, null);
  const sd = storeyIds.length ? await model.getItemsData(storeyIds.slice(0, 2), { attributesDefault: true }) : [];
  const d = await model.getItemsData([ids[0]], { attributesDefault: true, relations: { IsDefinedBy: { attributes: true, relations: true }, ContainedInStructure: { attributes: true, relations: false }, IsTypedBy: { attributes: true, relations: false } } });
  const mat = await model.getItemsMaterialDefinition(ids.slice(0, 2));
  const coord = await model.getCoordinates(); const meta = await model.getMetadata();
  const cats = await model.getItemsOfCategories([/.*/]);
  const safe = (o) => { const seen = new WeakSet(); return JSON.stringify(o, (k, x) => { if (x && typeof x === 'object') { if (seen.has(x)) return '[cycle]'; seen.add(x); } return x; }); };
  const W = window.BIMWEBIFC, api = new W.IfcAPI();
  await api.Init(function () { return 'https://bim-webifc.invalid/web-ifc.wasm'; }, true);
  const mid = api.OpenModel(new Uint8Array(b), { COORDINATE_TO_ORIGIN: true });
  const wb = new T.Box3();
  api.StreamAllMeshes(mid, (mesh) => { const g = mesh.geometries; for (let i = 0; i < g.size(); i++) { const pg = g.get(i), geo = api.GetGeometry(mid, pg.geometryExpressID);
    const vv = api.GetVertexArray(geo.GetVertexData(), geo.GetVertexDataSize()), m = new T.Matrix4().fromArray(pg.flatTransformation);
    for (let k = 0; k < vv.length; k += 6) wb.expandByPoint(v.set(vv[k], vv[k + 1], vv[k + 2]).applyMatrix4(m)); } });
  const cm = Array.from(api.GetCoordinationMatrix(mid)).map((x) => +x.toFixed(4));
  return { webifcBox: [wb.min.toArray(), wb.max.toArray()], webifcCoord: cm, geoBox: [bb.min.toArray(), bb.max.toArray()], objBox: [ob.min.toArray(), ob.max.toArray()], coord,
    spatialTop: JSON.stringify(sp).slice(0, 400), storeyData: JSON.stringify(sd).slice(0, 500),
    item: safe(d[0]).slice(0, 2500), mat: JSON.stringify(mat).slice(0, 600),
    meta: safe(meta).slice(0, 700), catsCount: Object.keys(cats).length, firstTransform: geo[0][0].transform.elements.map((x) => +x.toFixed(4)) };
}, bytes);
for (const [k, val] of Object.entries(out)) console.log(k + ': ' + (typeof val === 'string' ? val : JSON.stringify(val)));
await browser.close();
