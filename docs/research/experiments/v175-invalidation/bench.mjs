// V175 research, invalidation: what each strategy costs, measured (data script, not a test).
// Node only: this machine has no Playwright browser (no /opt/pw-browsers, no Python playwright package).
// Uses the app's own functions through tests/unit/helpers/engine.mjs: bimBuildWallGeometry (walls),
// bimSnapshotState (the undo snapshot), bimDispLen / bimDispNum (the app's number format), bimBdsHtml (a
// board's markup). The model is built from bimBuildWallGeometry and the object literal buildWallSolid writes,
// without buildWallSolid itself (in the Node stand-in it runs out of memory through its UI calls).
//   node --max-old-space-size=2048 docs/research/experiments/v175-invalidation/bench.mjs > out.json
import os from 'node:os';
import { loadEngine } from '../../../../tests/unit/helpers/engine.mjs';

const E = loadEngine();
const RUNS = 41, WARM = 5;
function time(fn) {
  for (let i = 0; i < WARM; i++) fn();
  const t = [];
  for (let i = 0; i < RUNS; i++) { const a = process.hrtime.bigint(); fn(); t.push(Number(process.hrtime.bigint() - a) / 1e6); }
  t.sort((x, y) => x - y);
  return { median_ms: +t[Math.floor(RUNS / 2)].toFixed(4), p95_ms: +t[Math.floor(RUNS * 0.95)].toFixed(4), min_ms: +t[0].toFixed(4), runs: RUNS };
}
// FNV-1a, 32 bit, over UTF-16 code units (what an ES5 page would write)
function fnv1a(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h; }

// ---- the model: N walls, plus N/10 slab-like solids, on one level ----
function model(n) {
  const objs = [];
  for (let i = 0; i < n; i++) {
    const x = (i % 50) * 6, z = Math.floor(i / 50) * 6;
    const r = E.bimBuildWallGeometry([[x, z], [x + 5, z]], 0, 3, 0.3, 'center', false, null);
    const o = { id: 'a3d-bench-' + i, t: 'solid', name: 'Wall_' + (i + 1), col: '#c7bfae', pos: [0, 0, 0], mesh: r.mesh, bim: r.bim, layer: 'layer-0' };
    o.bim.levelId = 'lvl-0'; o.bim.typeId = 'wt-1'; o.bim.typeCat = 'wall';
    objs.push(o);
  }
  return objs;
}
const out = { env: { node: process.version, cpu: os.cpus()[0].model, cores: os.cpus().length, platform: os.platform() + ' ' + os.release(), date: new Date().toISOString() } };

// ---- 1. the revision compare vs a fingerprint of the inputs ----
const M = model(2000);
E.A3D.objs = M;
const json = JSON.stringify(M);
out.model = { objects: M.length, json_bytes: json.length };
let REV = 7; const cache = { rev: 7, v: 1 };
out.rev_compare_1e6 = time(() => { let hit = 0; for (let i = 0; i < 1e6; i++) if (cache.rev === REV) hit++; return hit; });
out.stringify_2000 = time(() => JSON.stringify(M));
out.fnv_over_json_2000 = time(() => fnv1a(json));
out.stringify_plus_fnv_2000 = time(() => fnv1a(JSON.stringify(M)));
// a narrower fingerprint: only the inputs a gross-area number uses (centerline, thickness, level), as a string
out.narrow_fingerprint_2000 = time(() => { let s = ''; for (const o of M) s += o.id + o.bim.centerline + o.bim.thickness + o.bim.levelId + ';'; return fnv1a(s); });
// ---- the value itself, recomputed: a quantity over the same walls (length x thickness), and the app's level areas ----
out.recompute_wall_area_sum_2000 = time(() => { let a = 0; for (const o of M) { const c = o.bim.centerline; for (let k = 1; k < c.length; k++) a += Math.hypot(c[k][0] - c[k - 1][0], c[k][1] - c[k - 1][1]) * o.bim.thickness; } return a; });
try { out.recompute_bimLevelAreas_2000 = time(() => E.bimLevelAreas('lvl-0')); out.bimLevelAreas_sample = E.bimLevelAreas('lvl-0'); }
catch (e) { out.recompute_bimLevelAreas_2000 = { error: String(e && e.message) }; }

// ---- 2. formatting N numbers and N text tokens ----
const vals = []; for (let i = 0; i < 200; i++) vals.push(1234.5678 * (i + 1) / 7);
const NF = (typeof Intl !== 'undefined' && Intl.NumberFormat) ? new Intl.NumberFormat('en-GB', { maximumFractionDigits: 2 }) : null;
const DICT = { project: 'Riverside Library', client: 'City of Example', date: '2026-11-08', sheet: '3 of 12', site: 'North parcel', level: 'Level 0' };
const KEYS = Object.keys(DICT);
const TPL = []; for (let i = 0; i < 200; i++) TPL.push('Project <' + KEYS[i % KEYS.length] + '>, issued <date>, ' + (i % 3 ? '<unknown>' : 'plain'));
function subst(s) { return s.replace(/<([a-z][a-z0-9_.]{0,40})>/gi, function (m, k) { return Object.prototype.hasOwnProperty.call(DICT, k) ? DICT[k] : m; }); }
for (const n of [50, 200]) {
  out['bimDispLen_' + n] = time(() => { let s = ''; for (let i = 0; i < n; i++) s += E.bimDispLen(vals[i]); return s; });
  out['bimDispNum_' + n] = time(() => { let s = ''; for (let i = 0; i < n; i++) s += E.bimDispNum(vals[i], 2); return s; });
  out['toFixed_' + n] = time(() => { let s = ''; for (let i = 0; i < n; i++) s += vals[i].toFixed(2); return s; });
  if (NF) {
    out['Intl_cached_' + n] = time(() => { let s = ''; for (let i = 0; i < n; i++) s += NF.format(vals[i]); return s; });
    out['Intl_new_each_' + n] = time(() => { let s = ''; for (let i = 0; i < n; i++) s += new Intl.NumberFormat('en-GB', { maximumFractionDigits: 2 }).format(vals[i]); return s; });
  }
  out['token_subst_' + n] = time(() => { let s = ''; for (let i = 0; i < n; i++) s += subst(TPL[i]); return s; });
}

// ---- 3. a board of 80 objects, 20 of them live text, its markup rebuilt ----
function board(live, withCache) {
  const objs = [];
  for (let i = 0; i < 80; i++) {
    const x = (i % 10) * 36, y = Math.floor(i / 10) * 30;
    const kind = i < 20 ? 'text' : ['rect', 'ellipse', 'line', 'poly', 'star', 'text'][i % 6];
    const n = { id: 'e' + (i + 1), t: kind, layer: 'layer-0', x, y, w: 30, h: kind === 'line' ? 0 : 20 };
    if (kind === 'rect' || kind === 'ellipse' || kind === 'poly' || kind === 'star') { n.fill = '#c3c2b7'; n.fop = 1; n.stroke = '#0b0b0b'; n.sw = 0.35; }
    if (kind === 'line') { n.stroke = '#0b0b0b'; n.sw = 0.5; }
    if (kind === 'rect') n.r = 0; if (kind === 'poly') n.n = 6; if (kind === 'star') { n.n = 5; n.ri = 0.38; }
    if (kind === 'text') { n.s = 'Text ' + i; n.fs = 14; n.fw = 400; n.al = 'left'; n.col = '#0b0b0b'; n.fit = 'auto-h'; }
    if (i < 20 && live) {
      n.bind = { k: 'num', src: 'gfa', lvl: 'lvl-0', fmt: { u: 'm2', dp: 1 } };
      if (withCache) n.cache = { v: 12345.6, s: '12,345.6 m²', rev: 991, at: '2026-11-08T21:00:00Z' };
    }
    objs.push(n);
  }
  return { id: 'b1', kind: 'custom', objs };
}
const B = board(true, false);
let liveVal = 0;
function resolveLive(B2) {   // the live part: recompute each bound object's text from the model
  const area = (function () { let a = 0; for (const o of M) { const c = o.bim.centerline; a += Math.hypot(c[1][0] - c[0][0], c[1][1] - c[0][1]) * o.bim.thickness; } return a; })();
  liveVal = area;
  for (const n of B2.objs) if (n.bind) n.s = E.bimDispNum(area, 1) + ' m²';
}
try {
  E.bimBdsHtml(B, [], { edit: false });
  out.board_html_80 = time(() => E.bimBdsHtml(B, [], { edit: false }));
  out.board_html_80_bytes = E.bimBdsHtml(B, [], { edit: false }).length;
  out.board_resolve_20_live_plus_html = time(() => { resolveLive(B); return E.bimBdsHtml(B, [], { edit: false }); });
  out.board_resolve_20_live_only = time(() => resolveLive(B));
} catch (e) { out.board_html_80 = { error: String(e && e.stack || e).slice(0, 400) }; }

// ---- 4. undo snapshot size: a board with 20 bound objects, with and without stored resolved values ----
function snapWith(Bx) { E.A3D.pres = { boards: [Bx] }; return E.bimSnapshotState().length; }
E.A3D.objs = [];
const sPlain = snapWith(board(false, false)), sBind = snapWith(board(true, false)), sCache = snapWith(board(true, true));
E.A3D.objs = M;
const mPlain = snapWith(board(false, false)), mBind = snapWith(board(true, false)), mCache = snapWith(board(true, true));
out.snapshot_bytes = {
  note: 'bimSnapshotState().length, A3D.pres set to one board (the record bimPresValid would keep may differ; this is the raw size)',
  empty_model: { board_plain: sPlain, board_20_bound: sBind, board_20_bound_with_cached_values: sCache, cache_delta: sCache - sBind, cache_delta_x50: (sCache - sBind) * 50, bind_delta: sBind - sPlain },
  model_2000: { board_plain: mPlain, board_20_bound: mBind, board_20_bound_with_cached_values: mCache, cache_delta_pct: +(100 * (mCache - mBind) / mBind).toFixed(3) },
  snapshot_x50_model_2000_MB: +(mBind * 50 / 1048576).toFixed(1)
};
out.snapshot_time_2000 = time(() => E.bimSnapshotState());
console.log(JSON.stringify(out, null, 1));
setTimeout(() => process.exit(0), 50);
