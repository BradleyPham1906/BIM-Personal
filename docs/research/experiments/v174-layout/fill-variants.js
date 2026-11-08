/* V174 research experiment: three ways to share a line's free space among Fill children, on the same cases.
   - spec: css-flexbox-1 section 9.7 (the freeze loop), as autolayout.js does it; Chromium agreed with it on
     every case in compare-chromium.txt;
   - yoga: our transcription of Yoga v3.2.2's two passes (yoga/algorithm/CalculateLayout.cpp,
     distributeFreeSpaceFirstPass and distributeFreeSpaceSecondPass, MIT), grow case, basis 0, grow 1;
   - penpot: our transcription of Penpot's distribute-space (common/src/app/common/geom/shapes/flex_layout/
     layout_data.cljc at 904cdd9, MPL-2.0): every Fill child starts at its min and takes equal shares of
     what is left, capped by its max, until nothing is left.
   Run: node fill-variants.js */
var lal = require('./autolayout.js');
function clamp(v, lo, hi) { if (typeof hi === 'number' && v > hi) v = hi; if (typeof lo === 'number' && v < lo) v = lo; return v; }
function spec(items, inner) {
  var L = items.map(function (it) { return { fill: true, basis: 0, min: it.min, max: it.max }; });
  lal.lalResolveFill(L, inner);
  return L.map(function (it) { return it.target; });
}
function yoga(items, inner) {
  var n = items.length, rem = inner, tg = n, delta = 0, i, base, bound;
  for (i = 0; i < n; i++) {
    base = 0 + rem / tg; bound = clamp(base, items[i].min, items[i].max);
    if (bound !== base) { delta += bound - 0; tg -= 1; }
  }
  rem -= delta;
  return items.map(function (it) { return Math.max(0, clamp(0 + rem / Math.max(tg, 1), it.min, it.max)); });   /* boundAxis floors at padding and border, 0 here */
}
function penpot(items, inner) {
  var v = items.map(function (it) { return typeof it.min === 'number' ? it.min : 0; });
  var mx = items.map(function (it) { return typeof it.max === 'number' ? it.max : Infinity; });
  var share = inner - v.reduce(function (a, b) { return a + b; }, 0), guard = 0;
  while (share > 1e-9 && guard++ < 100) {
    var open = [], i;
    for (i = 0; i < v.length; i++) if (Math.abs(v[i] - mx[i]) > 1e-9) open.push(i);
    if (!open.length) break;
    var per = share / open.length, rem = share;
    for (i = 0; i < v.length; i++) {
      if (Math.abs(v[i] - mx[i]) <= 1e-9) continue;
      var inc = v[i] + per > mx[i] ? mx[i] - v[i] : per;
      v[i] += inc; rem -= inc;
    }
    if (rem <= 0 || rem === share) break;
    share = rem;
  }
  return v;
}
var cases = [
  ['two fill, no limits', 300, [{}, {}]],
  ['min 100 on the first', 300, [{ min: 100 }, {}]],
  ['min 200 on the first', 300, [{ min: 200 }, {}]],
  ['max 50, max 110, free', 300, [{ max: 50 }, { max: 110 }, {}]],
  ['min 120 (x3) in 300', 300, [{ min: 120 }, { min: 120 }, { min: 120 }]],
  ['min 120 > max 80, free', 300, [{ min: 120, max: 80 }, {}]],
  ['min 60, min 60, max 40', 300, [{ min: 60 }, { min: 60 }, { max: 40 }]],
  ['free, max 110, max 50 (order reversed)', 300, [{}, { max: 110 }, { max: 50 }]],
  ['free, min 140, min 170 (min cascade)', 300, [{}, { min: 140 }, { min: 170 }]]
];
function f(a) { return '[' + a.map(function (x) { return Math.round(x * 1000) / 1000; }).join(', ') + ']'; }
cases.forEach(function (K) {
  var s = spec(K[2], K[1]), y = yoga(K[2], K[1]), p = penpot(K[2], K[1]);
  var sy = f(s) === f(y) ? 'same' : 'DIFF', sp = f(s) === f(p) ? 'same' : 'DIFF';
  console.log(K[0] + ' (inner ' + K[1] + '): spec ' + f(s) + ' | yoga ' + f(y) + ' ' + sy + ' | penpot ' + f(p) + ' ' + sp);
});
