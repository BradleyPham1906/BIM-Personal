// V196 experiment e01: two IFC engines on the same public files, through the same calls.
// web-ifc (MPL-2.0, WebAssembly) and BimCraft's cc-ifc (Apache-2.0, JavaScript, web-ifc's API) are each asked to
// open a file and stream every mesh; we count the elements drawn, their triangles, the box they fill in metres
// (Y up, after each mesh's flatTransformation), the time taken, and what each could not draw.
//
//   node run.mjs <cc-ifc dir (app/ifc of getcadcraft/bimcraft@cfbd948)> <dir of .ifc files> [--no-manifold]
//
// web-ifc and manifold-3d come from node_modules beside the working directory (npm i web-ifc@0.0.79 manifold-3d@3.5.4).
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const req = createRequire(path.join(process.cwd(), 'x.js'));
const [ccDir, fileDir] = process.argv.slice(2);
const useManifold = !process.argv.includes('--no-manifold');

function apply(m, x, y, z) {
  return [m[0] * x + m[4] * y + m[8] * z + m[12], m[1] * x + m[5] * y + m[9] * z + m[13], m[2] * x + m[6] * y + m[10] * z + m[14]];
}

async function run(name, api, bytes) {
  const t0 = performance.now();
  let mid;
  try { mid = api.OpenModel(bytes, { COORDINATE_TO_ORIGIN: false }); } catch (e) { return { name, error: String(e.message || e) }; }
  const t1 = performance.now();
  const ids = new Set();
  let tris = 0, verts = 0;
  const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  const types = {};
  try {
    api.StreamAllMeshes(mid, (mesh) => {
      ids.add(mesh.expressID);
      const t = api.GetLineType(mid, mesh.expressID);
      const tn = api.GetNameFromTypeCode ? api.GetNameFromTypeCode(t) : t;
      types[tn] = (types[tn] || 0) + 1;
      const g = mesh.geometries;
      for (let i = 0; i < g.size(); i++) {
        const pg = g.get(i);
        const geo = api.GetGeometry(mid, pg.geometryExpressID);
        const v = api.GetVertexArray(geo.GetVertexData(), geo.GetVertexDataSize());
        const ix = api.GetIndexArray(geo.GetIndexData(), geo.GetIndexDataSize());
        tris += ix.length / 3; verts += v.length / 6;
        const m = pg.flatTransformation;
        for (let k = 0; k < v.length; k += 6) {
          const p = apply(m, v[k], v[k + 1], v[k + 2]);
          for (let a = 0; a < 3; a++) { if (p[a] < lo[a]) lo[a] = p[a]; if (p[a] > hi[a]) hi[a] = p[a]; }
        }
        if (geo.delete) geo.delete();
      }
    });
  } catch (e) { return { name, error: 'stream: ' + String(e.message || e) }; }
  const t2 = performance.now();
  const notes = api.notes ? api.notes(mid) : null;
  api.CloseModel(mid);
  return {
    name, open: Math.round(t1 - t0), mesh: Math.round(t2 - t1), elements: ids.size, tris, verts,
    box: lo.map((l, i) => +(hi[i] - l).toFixed(3)), types,
    notes: notes ? Array.from(notes.values ? notes.values() : notes).slice(0, 6).map(String) : null,
    noteCount: notes ? (notes.size !== undefined ? notes.size : notes.length) : null
  };
}

const WebIFC = req('web-ifc');
const wi = new WebIFC.IfcAPI();
await wi.Init();
const CC = await import(pathToFileURL(path.join(ccDir, 'api.js')).href);
const cc = new CC.IfcAPI();
let manifold = null;
if (useManifold) { const Module = (await import('manifold-3d')).default; manifold = await Module(); manifold.setup(); }
await cc.Init(manifold ? { manifold } : {});

const out = [];
for (const f of fs.readdirSync(fileDir).filter((x) => x.endsWith('.ifc')).sort()) {
  const bytes = new Uint8Array(fs.readFileSync(path.join(fileDir, f)));
  const a = await run('web-ifc', wi, bytes), b = await run('cc-ifc', cc, bytes);
  out.push({ file: f, bytes: bytes.length, a, b });
  const line = (r) => r.error ? r.name + ' ERROR ' + r.error :
    `${r.name.padEnd(7)} open ${String(r.open).padStart(5)} ms  mesh ${String(r.mesh).padStart(5)} ms  elements ${String(r.elements).padStart(4)}  tris ${String(r.tris).padStart(7)}  box ${r.box.join(' x ')}` + (r.noteCount ? `  not drawn ${r.noteCount}` : '');
  console.log(`\n${f} (${bytes.length} bytes)\n  ${line(a)}\n  ${line(b)}`);
  if (b.notes && b.notes.length) console.log('  cc-ifc notes: ' + b.notes.join(' | ').slice(0, 300));
  const ta = a.types || {}, tb = b.types || {};
  const diff = Object.keys({ ...ta, ...tb }).filter((k) => ta[k] !== tb[k]).map((k) => `${k} ${ta[k] || 0}/${tb[k] || 0}`);
  if (diff.length) console.log('  types differing (web-ifc/cc-ifc): ' + diff.join(', '));
}
fs.writeFileSync('results.json', JSON.stringify(out, null, 1));
