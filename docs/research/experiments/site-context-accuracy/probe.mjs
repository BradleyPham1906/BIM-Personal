// Site-context accuracy probe (2026-11-13).
// Question: for a real site, which free keyless sources give true building heights, ground
// elevations and bridges, and which of them a browser may call (CORS)?
// Site: Dilworth Park / Philadelphia City Hall (the owner's screenshot), a ~470 x 450 m box.
// Run: node docs/research/experiments/site-context-accuracy/probe.mjs  (Node 18+; writes results.json)
import { writeFileSync } from 'node:fs';
import { inflateSync } from 'node:zlib';

const S = 39.9505, W = -75.1665, N = 39.9545, E = -75.1610;
const ORIGIN = 'https://example.org';           // a foreign origin, as the app's page would be
const out = { date: new Date().toISOString(), bbox: [W, S, E, N], sources: {} };

async function get(url, opt) {
  const t0 = Date.now();
  const r = await fetch(url, Object.assign({ headers: { Origin: ORIGIN } }, opt || {}));
  const buf = Buffer.from(await r.arrayBuffer());
  return { status: r.status, cors: r.headers.get('access-control-allow-origin'), ms: Date.now() - t0, buf,
           json() { return JSON.parse(buf.toString('utf8')); }, headers: r.headers };
}
function rec(name, o) { out.sources[name] = o; console.log('\n== ' + name + '\n' + JSON.stringify(o, null, 1)); }
async function step(name, fn) { try { await fn(); } catch (e) { rec(name, { error: String(e && e.message || e) }); } }

// 1. OpenStreetMap through Overpass: how many buildings carry a height at all
await step('osm_buildings', async () => {
  const q = `[out:json][timeout:60];(way[building](${S},${W},${N},${E});relation[building](${S},${W},${N},${E}););out tags center;`;
  const r = await get('https://overpass-api.de/api/interpreter', { method: 'POST', headers: { Origin: ORIGIN, 'Content-Type': 'application/x-www-form-urlencoded' }, body: 'data=' + encodeURIComponent(q) });
  const e = r.json().elements; let h = 0, lv = 0;
  const named = [];
  for (const x of e) { const t = x.tags || {}; if (t.height) h++; else if (t['building:levels']) lv++;
    if (t.name && (t.height || t['building:levels'])) named.push([t.name, t.height || null, t['building:levels'] || null]); }
  rec('osm_buildings', { status: r.status, cors: r.cors, ms: r.ms, buildings: e.length, withHeight: h, levelsOnly: lv,
    neither_get6mDefault: e.length - h - lv, sampleNamed: named.slice(0, 12) });
});

// 2. OpenStreetMap: bridges, tunnels, rail, and what vertical information they carry
await step('osm_infra', async () => {
  const q = `[out:json][timeout:60];(way[bridge](${S},${W},${N},${E});way[man_made=bridge](${S},${W},${N},${E});way[tunnel](${S},${W},${N},${E});way[railway](${S},${W},${N},${E}););out tags;`;
  const r = await get('https://overpass-api.de/api/interpreter', { method: 'POST', headers: { Origin: ORIGIN, 'Content-Type': 'application/x-www-form-urlencoded' }, body: 'data=' + encodeURIComponent(q) });
  const c = {};
  for (const x of r.json().elements) { const t = x.tags || {};
    const k = t.bridge && t.bridge !== 'no' ? 'bridge' : t.man_made === 'bridge' ? 'man_made=bridge' : t.tunnel && t.tunnel !== 'no' ? 'tunnel' : 'railway(other)';
    c[k] = c[k] || { n: 0, layer: 0, verticalTag: 0 }; c[k].n++; if (t.layer) c[k].layer++;
    if (t.ele || t.height || t.min_height || t.maxheight || t['bridge:height']) c[k].verticalTag++; }
  rec('osm_infra', { status: r.status, cors: r.cors, counts: c });
});

// 3. City of Philadelphia building footprints (ArcGIS Online, OpenDataPhilly)
await step('phl_footprints', async () => {
  const base = 'https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/LI_BUILDING_FOOTPRINTS/FeatureServer/0';
  const meta = await get(base + '?f=json');
  const fields = (meta.json().fields || []).map(f => f.name);
  const q = `${base}/query?where=1%3D1&geometry=${W},${S},${E},${N}&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json`;
  const r = await get(q); const fs = (r.json().features || []).map(f => f.attributes);
  const hk = fields.filter(n => /HGT|HEIGHT|HT|STOR|ELEV/i.test(n));
  const filled = {}; for (const k of hk) filled[k] = fs.filter(a => a[k] != null && a[k] !== 0).length;
  const tall = fs.slice().sort((a, b) => (b[hk[0]] || 0) - (a[hk[0]] || 0)).slice(0, 8).map(a => { const o = {}; for (const k of hk) o[k] = a[k]; o.ADDRESS = a.ADDRESS; return o; });
  rec('phl_footprints', { status: r.status, cors: r.cors, metaCors: meta.cors, ms: r.ms, fields, heightFields: hk, features: fs.length, filled, tallest: tall });
});

// 4. National Bridge Inventory (FHWA, through BTS NTAD)
await step('nbi', async () => {
  const base = 'https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Bridge_Inventory/FeatureServer/0';
  const meta = await get(base + '?f=json'); const fields = (meta.json().fields || []).map(f => f.name);
  const pad = 0.01;
  const q = `${base}/query?where=1%3D1&geometry=${W - pad},${S - pad},${E + pad},${N + pad}&geometryType=esriGeometryEnvelope&inSR=4326&outFields=*&returnGeometry=true&outSR=4326&f=json`;
  const r = await get(q); const fs = r.json().features || [];
  const want = fields.filter(n => /FEATURES_DESC|FACILITY_CARRIED|STRUCTURE_LEN|DECK_WIDTH|ROADWAY_WIDTH|VERT_CLR|MAIN_UNIT_SPANS|MAX_SPAN|STRUCTURE_KIND|STRUCTURE_TYPE|YEAR_BUILT|STRUCTURE_NUMBER/i.test(n));
  rec('nbi', { status: r.status, cors: r.cors, features: fs.length, verticalAndSizeFields: want,
    sample: fs.slice(0, 6).map(f => { const o = {}; for (const k of want) o[k] = f.attributes[k]; o.xy = f.geometry && [f.geometry.x, f.geometry.y]; return o; }) });
});

// 5. USGS 3DEP bare-earth DEM (1 m where flown), sampled on a grid
const pts = []; for (let i = 0; i < 5; i++) for (let j = 0; j < 5; j++) pts.push([W + (E - W) * (i + 0.5) / 5, S + (N - S) * (j + 0.5) / 5]);
let dep = null;
await step('usgs_3dep_dem', async () => {
  const base = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer';
  const g = encodeURIComponent(JSON.stringify({ points: pts, spatialReference: { wkid: 4326 } }));
  const r = await get(`${base}/getSamples?geometry=${g}&geometryType=esriGeometryMultipoint&returnFirstValueOnly=true&interpolation=RSP_BilinearInterpolation&f=json`);
  const s = r.json().samples || []; dep = s.map(x => +x.value);
  const meta = await get(base + '?f=json'); const m = meta.json();
  rec('usgs_3dep_dem', { status: r.status, cors: r.cors, ms: r.ms, samples: s.length, cellSize_m: m.pixelSizeX, min: Math.min(...dep), max: Math.max(...dep) });
});

// 6. AWS Terrain Tiles (Terrarium), what the app uses today, at the same points (z15)
function decodePng(buf) {   // RGB(A) 8-bit, non-interlaced: enough for Terrarium tiles
  let p = 8, w, h, ct, idat = [];
  while (p < buf.length) { const len = buf.readUInt32BE(p), type = buf.toString('ascii', p + 4, p + 8), d = buf.subarray(p + 8, p + 8 + len);
    if (type === 'IHDR') { w = d.readUInt32BE(0); h = d.readUInt32BE(4); ct = d[9]; } else if (type === 'IDAT') idat.push(d); p += 12 + len; }
  const bpp = ct === 6 ? 4 : 3, raw = inflateSync(Buffer.concat(idat)), px = Buffer.alloc(w * h * bpp), st = w * bpp;
  for (let y = 0; y < h; y++) { const f = raw[y * (st + 1)], src = raw.subarray(y * (st + 1) + 1, (y + 1) * (st + 1));
    for (let x = 0; x < st; x++) { const a = x >= bpp ? px[y * st + x - bpp] : 0, b = y ? px[(y - 1) * st + x] : 0, c = x >= bpp && y ? px[(y - 1) * st + x - bpp] : 0; let v = src[x];
      if (f === 1) v += a; else if (f === 2) v += b; else if (f === 3) v += (a + b) >> 1; else if (f === 4) { const q = a + b - c, pa = Math.abs(q - a), pb = Math.abs(q - b), pc = Math.abs(q - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c; }
      px[y * st + x] = v & 255; } }
  return { w, h, bpp, px };
}
await step('terrarium_vs_3dep', async () => {
  const z = 15, n = 2 ** z, tiles = {}, vals = [];
  for (const [lon, lat] of pts) {
    const xf = (lon + 180) / 360 * n, yf = (1 - Math.asinh(Math.tan(lat * Math.PI / 180)) / Math.PI) / 2 * n, tx = Math.floor(xf), ty = Math.floor(yf), key = tx + '/' + ty;
    if (!tiles[key]) { const r = await get(`https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${z}/${tx}/${ty}.png`); tiles[key] = { img: decodePng(r.buf), cors: r.cors, src: r.headers.get('x-amz-meta-x-imagery-sources') }; }
    const T = tiles[key].img, px = Math.min(255, Math.floor((xf - tx) * 256)), py = Math.min(255, Math.floor((yf - ty) * 256)), o = (py * 256 + px) * T.bpp;
    vals.push(T.px[o] * 256 + T.px[o + 1] + T.px[o + 2] / 256 - 32768);
  }
  const d = dep ? vals.map((v, i) => v - dep[i]) : [];
  const rmse = d.length ? Math.sqrt(d.reduce((a, b) => a + b * b, 0) / d.length) : null;
  rec('terrarium_vs_3dep', { cors: Object.values(tiles)[0].cors, imagerySources: Object.values(tiles).map(t => t.src), terrarium: vals.map(v => +v.toFixed(2)),
    usgs3dep: dep && dep.map(v => +v.toFixed(2)), diffRMSE_m: rmse && +rmse.toFixed(2), diffMaxAbs_m: d.length ? +Math.max(...d.map(Math.abs)).toFixed(2) : null });
});

// 7. USGS 3DEP LiDAR point clouds, Entwine (EPT) on AWS: what covers Philadelphia, and is it browser-readable
await step('usgs_3dep_ept', async () => {
  const lst = await get('https://s3-us-west-2.amazonaws.com/usgs-lidar-public/?list-type=2&delimiter=/&prefix=PA_');
  const names = [...lst.buf.toString().matchAll(/<Prefix>([^<]+)<\/Prefix>/g)].map(m => m[1]).filter(p => p !== 'PA_');
  const res = { listStatus: lst.status, listCors: lst.cors, paDatasets: names };
  const pick = names.filter(n => /Philadelphia|SE_?PA|Southeast|PA_Statewide|PA_South/i.test(n));
  res.candidates = [];
  for (const nm of pick.slice(0, 6)) {
    const r = await get(`https://s3-us-west-2.amazonaws.com/usgs-lidar-public/${nm}ept.json`);
    if (r.status !== 200) { res.candidates.push({ nm, status: r.status }); continue; }
    const j = r.json(), b = j.boundsConforming || j.bounds;
    res.candidates.push({ nm, status: r.status, cors: r.cors, points: j.points, srs: j.srs && (j.srs.horizontal + '+' + (j.srs.vertical || '?')), dataType: j.dataType,
      dims: (j.schema || []).map(s => s.name).filter(n => /Classification|ReturnNumber|Red/.test(n)), boundsConforming: b });
  }
  rec('usgs_3dep_ept', res);
});

writeFileSync(new URL('./results.json', import.meta.url), JSON.stringify(out, null, 1));
console.log('\nwrote results.json');
