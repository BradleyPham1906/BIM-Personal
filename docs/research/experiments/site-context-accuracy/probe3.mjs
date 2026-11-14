// Follow-up probe 3 (2026-11-13): OSM height and bridge tag coverage through the app's Overpass
// mirrors, and CORS on the 3DEP EPT dataset that covers City Hall.
// Run: node docs/research/experiments/site-context-accuracy/probe3.mjs  (writes results3.json)
import { writeFileSync } from 'node:fs';
const S = 39.9505, W = -75.1665, N = 39.9545, E = -75.1610, O = { headers: { Origin: 'https://example.org', Accept: '*/*', 'User-Agent': 'Mozilla/5.0 (BIM-Personal site-context research probe)' } };
const out = {};
for (const host of ['https://overpass.private.coffee/api/interpreter', 'https://maps.mail.ru/osm/tools/overpass/api/interpreter', 'https://overpass-api.de/api/interpreter']) {
  try {
    const q = `[out:json][timeout:60];(way[building](${S},${W},${N},${E});relation[building](${S},${W},${N},${E}););out tags;`;
    const r = await fetch(host + '?data=' + encodeURIComponent(q), O); const t = await r.text();
    if (t[0] !== '{') { out[host] = { status: r.status, head: t.slice(0, 80) }; continue; }
    const e = JSON.parse(t).elements; let h = 0, lv = 0; const hs = [];
    for (const x of e) { const g = x.tags || {}; if (g.height) { h++; hs.push([g.name || '', g.height]); } else if (g['building:levels']) lv++; }
    out.osmBuildings = { host, status: r.status, cors: r.headers.get('access-control-allow-origin'), buildings: e.length, withHeight: h, levelsOnly: lv, neither: e.length - h - lv, heights: hs.slice(0, 20) };
    const p = 0.005, qi = `[out:json][timeout:60];(way[bridge](${S - p},${W - p},${N + p},${E + p});way[man_made=bridge](${S - p},${W - p},${N + p},${E + p});way[tunnel](${S},${W},${N},${E}););out tags;`;
    const ei = (await (await fetch(host + '?data=' + encodeURIComponent(qi), O)).json()).elements; const c = {};
    for (const x of ei) { const g = x.tags || {}; const k = g.man_made === 'bridge' ? 'man_made=bridge' : g.bridge && g.bridge !== 'no' ? 'bridge' : 'tunnel';
      c[k] = c[k] || { n: 0, layer: 0, vertical: 0 }; c[k].n++; if (g.layer) c[k].layer++; if (g.ele || g.height || g.min_height || g.maxheight) c[k].vertical++; }
    out.osmInfra = c; break;
  } catch (e) { out[host] = String(e); }
}
const ds = 'https://s3-us-west-2.amazonaws.com/usgs-lidar-public/USGS_LPC_DE_DelawareValley_HD_2015_LAS_2017/';
const r1 = await fetch(ds + 'ept.json', O), r2 = await fetch(ds + 'ept-hierarchy/0-0-0-0.json', O);
out.ept = { eptJson: [r1.status, r1.headers.get('access-control-allow-origin')], hierarchy: [r2.status, r2.headers.get('access-control-allow-origin'), (await r2.text()).length + ' bytes'] };
writeFileSync(new URL('./results3.json', import.meta.url), JSON.stringify(out, null, 1));
console.log(JSON.stringify(out, null, 1));
