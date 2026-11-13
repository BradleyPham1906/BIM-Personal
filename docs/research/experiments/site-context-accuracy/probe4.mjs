// Follow-up probe 4 (2026-11-13): can the USGS 3DEP 1 m DEM give a dense terrain grid in one request?
// exportImage as an uncompressed float32 TIFF over the site box, decoded here; compared with getSamples.
// Run: node docs/research/experiments/site-context-accuracy/probe4.mjs  (writes results4.json)
import { writeFileSync } from 'node:fs';
const S = 39.9505, W = -75.1665, N = 39.9545, E = -75.1610, O = { headers: { Origin: 'https://example.org' } };
const base = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer';
const out = {};

function readTiff(buf) {   // little- or big-endian baseline TIFF, one float32 band, strips or tiles, no compression
  const le = buf.toString('ascii', 0, 2) === 'II', u16 = o => le ? buf.readUInt16LE(o) : buf.readUInt16BE(o), u32 = o => le ? buf.readUInt32LE(o) : buf.readUInt32BE(o);
  const ifd = u32(4), n = u16(ifd), tag = {};
  for (let i = 0; i < n; i++) { const e = ifd + 2 + i * 12, t = u16(e + 0), ty = u16(e + 2), c = u32(e + 4), sz = ty === 3 ? 2 : 4;
    const at = c * sz > 4 ? u32(e + 8) : e + 8, v = []; for (let k = 0; k < c; k++) v.push(ty === 3 ? u16(at + k * 2) : u32(at + k * 4)); tag[t] = v; }
  const w = tag[256][0], h = tag[257][0], comp = (tag[259] || [1])[0], f = new Float32Array(w * h);
  if (comp !== 1) throw new Error('compressed TIFF ' + comp);
  const rf = o => le ? buf.readFloatLE(o) : buf.readFloatBE(o);
  if (tag[324]) { const tw = tag[322][0], th = tag[323][0], across = Math.ceil(w / tw);
    tag[324].forEach((off, k) => { const tx = (k % across) * tw, ty = Math.floor(k / across) * th;
      for (let y = 0; y < th; y++) for (let x = 0; x < tw; x++) if (tx + x < w && ty + y < h) f[(ty + y) * w + tx + x] = rf(off + (y * tw + x) * 4); }); }
  else { let p = 0; for (const off of tag[273]) { const cnt = Math.min(w * h - p, (tag[279][tag[273].indexOf(off)]) / 4); for (let k = 0; k < cnt; k++) f[p++] = rf(off + k * 4); } }
  return { w, h, f };
}

// the box in Web Mercator, at 1 m per pixel along the ground (Mercator metres are 1/cos(lat) larger)
const mx = l => l * 20037508.34 / 180, my = l => Math.log(Math.tan((90 + l) * Math.PI / 360)) * 20037508.34 / Math.PI;
const k = 1 / Math.cos(39.9525 * Math.PI / 180), wpx = Math.round((mx(E) - mx(W)) / k), hpx = Math.round((my(N) - my(S)) / k);
for (const [label, size] of [['1 m', [wpx, hpx]], ['5 m', [Math.round(wpx / 5), Math.round(hpx / 5)]]]) {
  const t0 = Date.now();
  const url = `${base}/exportImage?bbox=${mx(W)},${my(S)},${mx(E)},${my(N)}&bboxSR=3857&imageSR=3857&size=${size[0]},${size[1]}&format=tiff&pixelType=F32&compression=None&interpolation=RSP_BilinearInterpolation&f=image`;
  try {
    const r = await fetch(url, O); const buf = Buffer.from(await r.arrayBuffer());
    const res = { status: r.status, cors: r.headers.get('access-control-allow-origin'), type: r.headers.get('content-type'), bytes: buf.length, ms: Date.now() - t0 };
    if (buf.toString('ascii', 0, 2) === 'II' || buf.toString('ascii', 0, 2) === 'MM') { const T = readTiff(buf); let mn = 1e9, mxv = -1e9; for (const v of T.f) { if (v > -1000) { mn = Math.min(mn, v); mxv = Math.max(mxv, v); } }
      Object.assign(res, { w: T.w, h: T.h, min: +mn.toFixed(2), max: +mxv.toFixed(2), centre: +T.f[(T.h >> 1) * T.w + (T.w >> 1)].toFixed(2) }); }
    else res.head = buf.toString('utf8', 0, 200);
    out['exportImage ' + label] = res;
  } catch (e) { out['exportImage ' + label] = String(e); }
}
writeFileSync(new URL('./results4.json', import.meta.url), JSON.stringify(out, null, 1));
console.log(JSON.stringify(out, null, 1));
