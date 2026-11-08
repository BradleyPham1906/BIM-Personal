/* V174 research experiment: an equal-gap ("smart spacing") snap search plus edge and centre snaps, timed
   for 50, 200 and 1000 boxes. Method after Excalidraw's packages/excalidraw/snapping.ts (MIT, master at
   701b901): the gaps between the other boxes are found once when a drag starts (pairs whose ranges
   overlap on the other axis and that do not overlap on this one); on each pointer move the moving box is
   tested against every gap for three snaps (equal gap after the gap's end box, before its start box, and
   centred in the gap when the gap is wider than the box), and against every edge and centre for a point
   snap. The nearest snap within the threshold wins. Our own ES5 code. Run: node spacing-snap.js */
'use strict';
function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
/* n boxes on a 1408 px board, in rows, jittered */
function scene(n, seed) {
  var r = rng(seed), L = [], cols = 6, i;
  for (i = 0; i < n; i++) {
    var c = i % cols, row = Math.floor(i / cols);
    L.push({ x: c * 236 + r() * 30, y: row * 180 + r() * 30, w: 120 + r() * 80, h: 90 + r() * 60 });
  }
  return L;
}
function overlap(a0, a1, b0, b1) { return a0 <= b1 && b0 <= a1; }
function buildGaps(R) {
  var H = [], V = [], i, j, a, b, S = R.slice().sort(function (p, q) { return p.x - q.x; });
  for (i = 0; i < S.length; i++) for (j = i + 1; j < S.length; j++) {
    a = S[i]; b = S[j];
    if (a.x + a.w < b.x && overlap(a.y, a.y + a.h, b.y, b.y + b.h)) H.push({ s: a, e: b, len: b.x - (a.x + a.w), o0: Math.max(a.y, b.y), o1: Math.min(a.y + a.h, b.y + b.h) });
  }
  S.sort(function (p, q) { return p.y - q.y; });
  for (i = 0; i < S.length; i++) for (j = i + 1; j < S.length; j++) {
    a = S[i]; b = S[j];
    if (a.y + a.h < b.y && overlap(a.x, a.x + a.w, b.x, b.x + b.w)) V.push({ s: a, e: b, len: b.y - (a.y + a.h), o0: Math.max(a.x, b.x), o1: Math.min(a.x + a.w, b.x + b.w) });
  }
  var xs = [], ys = [];
  R.forEach(function (o) { xs.push(o.x, o.x + o.w / 2, o.x + o.w); ys.push(o.y, o.y + o.h / 2, o.y + o.h); });
  return { H: H, V: V, xs: xs, ys: ys };
}
/* one axis: the best offset (or null) for a box at [p, p+s] whose cross range is [c0, c1] */
function axisSnap(p, s, c0, c1, gaps, pts, th, axis) {
  var best = null, bd = th + 1e-9, i, g, d, k, m;
  var mine = [p, p + s / 2, p + s];
  for (i = 0; i < pts.length; i++) for (k = 0; k < 3; k++) { d = pts[i] - mine[k]; if (Math.abs(d) < bd) { bd = Math.abs(d); best = { d: d, kind: 'point' }; } }
  for (i = 0; i < gaps.length; i++) {
    g = gaps[i];
    if (!overlap(c0, c1, g.o0, g.o1)) continue;
    var sP = axis === 'x' ? g.s.x : g.s.y, eP = axis === 'x' ? g.e.x : g.e.y, eS = axis === 'x' ? g.e.w : g.e.h;
    if (g.len > s) { m = sP + (axis === 'x' ? g.s.w : g.s.h) + g.len / 2; d = m - (p + s / 2); if (Math.abs(d) < bd) { bd = Math.abs(d); best = { d: d, kind: 'centre', g: g }; } }
    d = (eP + eS + g.len) - p; if (Math.abs(d) < bd) { bd = Math.abs(d); best = { d: d, kind: 'after', g: g }; }
    d = (sP - g.len) - (p + s); if (Math.abs(d) < bd) { bd = Math.abs(d); best = { d: d, kind: 'before', g: g }; }
  }
  return best;
}
function snapMove(B, G, th) {
  return { x: axisSnap(B.x, B.w, B.y, B.y + B.h, G.H, G.xs, th, 'x'), y: axisSnap(B.y, B.h, B.x, B.x + B.w, G.V, G.ys, th, 'y') };
}
function now() { var t = process.hrtime(); return t[0] * 1e3 + t[1] / 1e6; }
function pct(a, p) { var s = a.slice().sort(function (x, y) { return x - y; }); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; }
/* correctness: three boxes 100 apart; a fourth dragged near 100 after the third snaps 'after' */
(function () {
  var R = [{ x: 0, y: 0, w: 50, h: 50 }, { x: 150, y: 0, w: 50, h: 50 }, { x: 300, y: 0, w: 50, h: 50 }];
  var G = buildGaps(R), r = snapMove({ x: 455, y: 10, w: 50, h: 30 }, G, 12);
  console.log('check: gaps H ' + G.H.length + ' (expect 3: 100, 100, 250), snap x ' + JSON.stringify({ d: r.x.d, kind: r.x.kind, len: r.x.g && r.x.g.len }) + ' (expect -5, after, 100)');
  var r2 = snapMove({ x: 352, y: 10, w: 50, h: 30 }, G, 12);
  console.log('check: near an edge, snap x ' + JSON.stringify({ d: r2.x.d, kind: r2.x.kind }) + ' (expect -2, point: the right edge 350)');
})();
var MOVES = 500;
[50, 200, 1000].forEach(function (n) {
  var R = scene(n, n), mover = R.pop(), build = [], per = [], i, G, k, hits = 0;
  for (k = 0; k < 5; k++) { var t0 = now(); G = buildGaps(R); build.push(now() - t0); }
  var r = rng(7);
  for (i = 0; i < 50; i++) snapMove({ x: r() * 1400, y: r() * 1000, w: mover.w, h: mover.h }, G, 12);   /* warm up */
  var maxY = Math.ceil(n / 6) * 180;
  for (i = 0; i < MOVES; i++) {
    var B = { x: r() * 1400, y: r() * maxY, w: mover.w, h: mover.h }, t1 = now(), s = snapMove(B, G, 12);
    per.push(now() - t1);
    if (s.x || s.y) hits++;
  }
  console.log('n=' + n + ': gaps H ' + G.H.length + ' V ' + G.V.length + '; build (5 runs, ms) min ' + Math.min.apply(null, build).toFixed(3) + ' max ' + Math.max.apply(null, build).toFixed(3) +
    '; per move (' + MOVES + ' moves, ms) median ' + pct(per, 0.5).toFixed(4) + ' p95 ' + pct(per, 0.95).toFixed(4) + ' max ' + Math.max.apply(null, per).toFixed(4) + '; moves with a snap ' + hits);
});
