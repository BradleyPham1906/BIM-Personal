// Follow-up probe (2026-11-13): units of Philadelphia's height fields against known buildings,
// Overpass retried, and the 3DEP EPT bucket listed in full for datasets near Philadelphia.
// Run: node docs/research/experiments/site-context-accuracy/probe2.mjs  (writes results2.json)
import { writeFileSync } from 'node:fs';
const out = {};
const S = 39.9505, W = -75.1665, N = 39.9545, E = -75.1610;

// 1. Known heights: City Hall 548 ft to the statue's hat; One Liberty Place 945 ft; Centre Square 490 ft / 417 ft
const base = 'https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/LI_BUILDING_FOOTPRINTS/FeatureServer/0/query';
for (const [label, where] of [['City Hall', "address LIKE '1400 JOHN F KENNEDY%' OR building_name LIKE '%CITY HALL%'"],
                              ['One Liberty Place', "address LIKE '1650 MARKET%'"],
                              ['Centre Square', "address LIKE '1500 MARKET%'"]]) {
  try {
    const r = await fetch(base + '?where=' + encodeURIComponent(where) + '&outFields=address,building_name,base_elevation,approx_hgt,max_hgt,square_ft&returnGeometry=false&f=json');
    out[label] = ((await r.json()).features || []).map(f => f.attributes);
  } catch (e) { out[label] = String(e); }
}

// 2. Overpass, plain request, with the status and the head of the body when it fails
for (const host of ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter']) {
  const q = `[out:json][timeout:60];(way[building](${S},${W},${N},${E});relation[building](${S},${W},${N},${E}););out tags;`;
  try {
    const r = await fetch(host + '?data=' + encodeURIComponent(q), { headers: { 'User-Agent': 'BIM-Personal research probe' } });
    const t = await r.text();
    if (!r.ok || t[0] !== '{') { out['overpass ' + host] = { status: r.status, head: t.slice(0, 200) }; continue; }
    const e = JSON.parse(t).elements; let h = 0, lv = 0;
    for (const x of e) { const g = x.tags || {}; if (g.height) h++; else if (g['building:levels']) lv++; }
    out['overpass ' + host] = { status: r.status, cors: r.headers.get('access-control-allow-origin'), buildings: e.length, withHeight: h, levelsOnly: lv, neither: e.length - h - lv };
    const qi = `[out:json][timeout:60];(way[bridge](${S},${W},${N},${E});way[man_made=bridge](${S},${W},${N},${E});way[tunnel](${S},${W},${N},${E}););out tags;`;
    const ri = await fetch(host + '?data=' + encodeURIComponent(qi)); const ei = (await ri.json()).elements; const c = {};
    for (const x of ei) { const g = x.tags || {}; const k = g.man_made === 'bridge' ? 'man_made=bridge' : g.bridge && g.bridge !== 'no' ? 'bridge=' + g.bridge : 'tunnel=' + g.tunnel;
      c[k] = c[k] || { n: 0, layer: 0, vertical: 0 }; c[k].n++; if (g.layer) c[k].layer++; if (g.ele || g.height || g.min_height || g.maxheight) c[k].vertical++; }
    out['overpass infra'] = c; break;
  } catch (e) { out['overpass ' + host] = String(e); }
}

// 3. 3DEP EPT: every dataset name, paged, filtered to PA/NJ/DE and anything naming Philadelphia
let token = '', names = [];
for (let i = 0; i < 20; i++) {
  const r = await fetch('https://s3-us-west-2.amazonaws.com/usgs-lidar-public/?list-type=2&delimiter=/' + (token ? '&continuation-token=' + encodeURIComponent(token) : ''));
  const t = await r.text(); names = names.concat([...t.matchAll(/<Prefix>([^<]+)<\/Prefix>/g)].map(m => m[1]));
  const m = /<NextContinuationToken>([^<]+)</.exec(t); if (!m) break; token = m[1];
}
out.eptTotal = names.length;
out.eptNear = names.filter(n => /^(PA|NJ|DE)_|Phila|Delaware|SE_?PA/i.test(n));
// which of them contain City Hall (projected bounds need the srs; use boundsConforming in EPSG:3857)
const x = -75.1637 * 20037508.34 / 180, y = Math.log(Math.tan((90 + 39.9525) * Math.PI / 360)) / (Math.PI / 180) * 20037508.34 / 180;
out.eptCovering = [];
for (const nm of out.eptNear) {
  try { const j = await (await fetch(`https://s3-us-west-2.amazonaws.com/usgs-lidar-public/${nm}ept.json`)).json(); const b = j.boundsConforming;
    if (b && x >= b[0] && x <= b[3] && y >= b[1] && y <= b[4]) out.eptCovering.push({ nm, points: j.points, srs: j.srs && j.srs.horizontal, dataType: j.dataType, span: j.span, dims: (j.schema || []).map(s => s.name) }); } catch (e) {}
}
writeFileSync(new URL('./results2.json', import.meta.url), JSON.stringify(out, null, 1));
console.log(JSON.stringify(out, null, 1));
