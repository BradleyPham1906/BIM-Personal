/* V174 experiment e02: a nice-number scale-bar chooser (our own, ES5) compared with QGIS's
   "Fit segment width" method as read in QGIS master (qgslayoutitemscalebar.cpp refreshSegmentMillimeters,
   qgslayoututils.cpp calculatePrettySize / nextNiceNumber / prevNiceNumber, read as text 2026-11-08).
   The QGIS side below is our re-statement of the method from that reading, written here to compare
   numbers, not a copy of its source. Run: node scalebar.js */
'use strict';

var FT = 0.3048, MILE_FT = 5280;

/* ---- our chooser ----
   frameMm: the map frame's width on the page; denom: the scale's denominator (1:denom);
   opts: {unit:'m'|'ft', minMm, maxMm, segs, steps}. Ground per page mm = denom/1000 m.
   It picks the largest step from the 1-2-5 ladder (or opts.steps) whose whole bar fits
   between minMm and maxMm; when none fits it takes the one closest to the range.
   It switches the label to km above 1000 m per segment and to miles at a quarter mile and up. */
function niceLadder(lo, hi, steps) {
  var out = [], e, i;
  steps = steps || [1, 2, 5];
  for (e = Math.floor(Math.log(lo) / Math.LN10) - 1; e <= Math.ceil(Math.log(hi) / Math.LN10) + 1; e++) {
    for (i = 0; i < steps.length; i++) out.push(steps[i] * Math.pow(10, e));
  }
  return out;
}
function chooseBar(frameMm, denom, opts) {
  opts = opts || {};
  var unit = opts.unit || 'm', segs = opts.segs || 2;
  var minMm = opts.minMm || Math.max(20, frameMm * 0.15), maxMm = opts.maxMm || Math.max(minMm, frameMm * 0.4);
  var unitM = unit === 'ft' ? FT : 1;                 /* metres per label unit */
  var big = unit === 'ft' ? MILE_FT * FT : 1000;     /* metres per large unit */
  var mPerMm = denom / 1000;                           /* ground metres per page millimetre */
  function tryUnit(uM) {
    var lo = minMm * mPerMm / segs / uM, hi = maxMm * mPerMm / segs / uM, L = niceLadder(lo, hi, opts.steps), best = null, near = null, i, w, d;
    for (i = 0; i < L.length; i++) {
      w = L[i] * uM / mPerMm * segs;
      if (w >= minMm - 1e-9 && w <= maxMm + 1e-9) best = L[i];
      d = w < minMm ? minMm - w : (w > maxMm ? w - maxMm : 0);
      if (near === null || d < near.d) near = { v: L[i], d: d };
    }
    return best !== null ? { v: best, fit: true } : { v: near.v, fit: false };
  }
  var r = tryUnit(unitM), label = unit;
  if (r.v * unitM * segs >= (unit === 'ft' ? big / 4 : big)) {   /* a long bar: the large unit */
    var r2 = tryUnit(big);
    if (r2.fit || !r.fit) { r = r2; label = unit === 'ft' ? 'mi' : 'km'; }
  }
  var segM = r.v * (label === 'km' ? 1000 : label === 'mi' ? MILE_FT * FT : unitM);
  return { seg: r.v, label: label, segs: segs, barMm: segM / mPerMm * segs, fit: r.fit };
}

/* ---- QGIS's method, re-stated from the reading ---- */
function nextNice(a, d) { var s = Math.pow(10, Math.floor(Math.log(a) / Math.LN10)) / (d || 1); return Math.ceil(a / s) * s; }
function prevNice(a, d) { var s = Math.pow(10, Math.floor(Math.log(a) / Math.LN10)) / (d || 1); return Math.floor(a / s) * s; }
function prettySize(mn, mx) {
  if (mx < mn) return 0;
  var lo = nextNice(mn, 1), hi = prevNice(mx, 1), d = 1;
  while (lo > mx && hi < mn) { d *= 10; lo = nextNice(mn, d); hi = prevNice(mx, d); }
  return hi < mn ? lo : hi;
}
/* frameMm, denom, unit metres per scale-bar unit, min/max total bar mm (QGIS defaults 50/150), segments (default 2) */
function qgisFit(frameMm, denom, uM, minMm, maxMm, segs) {
  var mapWidthUnits = frameMm * denom / 1000 / uM;
  var minU = minMm * mapWidthUnits / (segs * frameMm), maxU = maxMm * mapWidthUnits / (segs * frameMm);
  var u = prettySize(minU, maxU);
  return { seg: u, barMm: frameMm / mapWidthUnits * u * segs };
}
/* QGIS's default when a scale bar is first added: a tenth of the map width per segment, then the
   leading power of ten times floor((width/(unit*10))/2.5)*2.5 */
function qgisDefault(frameMm, denom, uM) {
  var W = frameMm * denom / 1000 / uM, init = W / 10;
  var mag = Math.floor(Math.log(init) / Math.LN10), ups = Math.pow(10, mag);
  var mult = Math.floor((W / (ups * 10)) / 2.5) * 2.5;
  if (mult > 0) ups *= mult;
  return { seg: ups, barMm: ups * uM / (denom / 1000) * 2 };
}

function lead(v) { var m = v / Math.pow(10, Math.floor(Math.log(v) / Math.LN10 + 1e-9)); return Math.round(m * 1000) / 1000; }
function fmt(v) { return v >= 1 ? String(+v.toPrecision(6)) : String(+v.toPrecision(3)); }

var DENOMS = [1, 5, 20, 50, 100, 200, 250, 500, 1000, 1250, 2000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 1000000, 5000000];
var FRAMES = [60, 120, 180, 250, 400, 800];

function run() {
  var rows = 0, ourFit = 0, qInRange = 0, qNot125 = 0, agree = 0, leads = {}, dflt125 = 0, dfltOver = 0, d, f, u;
  var sample = [];
  for (u = 0; u < 2; u++) {
    for (d = 0; d < DENOMS.length; d++) {
      for (f = 0; f < FRAMES.length; f++) {
        var unit = u ? 'ft' : 'm', uM = u ? FT : 1, D = DENOMS[d], F = FRAMES[f];
        var ours = chooseBar(F, D, { unit: unit, minMm: 50, maxMm: 150, segs: 2 });
        var q = qgisFit(F, D, uM, 50, 150, 2), qd = qgisDefault(F, D, uM);
        rows++;
        if (ours.fit) ourFit++;
        if (q.barMm >= 50 - 1e-6 && q.barMm <= 150 + 1e-6) qInRange++;
        var L = lead(q.seg); leads[L] = (leads[L] || 0) + 1;
        if ([1, 2, 5].indexOf(L) < 0) qNot125++;
        var ourM = ours.seg * (ours.label === 'km' ? 1000 : ours.label === 'mi' ? MILE_FT * FT : uM);
        if (Math.abs(ourM - q.seg * uM) < 1e-6 * ourM) agree++;
        var Ld = lead(qd.seg); if ([1, 2, 5].indexOf(Ld) >= 0) dflt125++;
        if (qd.barMm > F) dfltOver++;
        if (F === 180 || (F === 60 && (D === 1 || D === 5000000))) sample.push([unit, '1:' + D, F, fmt(ours.seg) + ' ' + ours.label + ' x' + ours.segs + ' = ' + ours.barMm.toFixed(1) + ' mm' + (ours.fit ? '' : ' (no fit)'), fmt(q.seg) + ' ' + unit + ' = ' + q.barMm.toFixed(1) + ' mm', fmt(qd.seg) + ' ' + unit + ' = ' + qd.barMm.toFixed(1) + ' mm']);
      }
    }
  }
  console.log('Cases: ' + rows + ' (2 units x ' + DENOMS.length + ' scales x ' + FRAMES.length + ' frame widths), bar 50-150 mm, 2 segments');
  console.log('Ours: a 1-2-5 bar inside the range in ' + ourFit + ' of ' + rows);
  console.log('QGIS fit: bar inside the range in ' + qInRange + ' of ' + rows + '; segment not 1, 2 or 5 x 10^k in ' + qNot125 + ' of ' + rows);
  console.log('QGIS fit leading digits: ' + JSON.stringify(leads));
  console.log('Same segment length (in metres) as QGIS fit: ' + agree + ' of ' + rows);
  console.log('QGIS default on insert: leading digit 1, 2 or 5 in ' + dflt125 + ' of ' + rows + '; bar wider than the frame in ' + dfltOver);
  console.log('\nunit | scale | frame mm | ours | QGIS fit | QGIS default');
  sample.forEach(function (r) { console.log(r.join(' | ')); });
  /* edges */
  console.log('\nEdges:');
  console.log('  1:1, 60 mm frame (m): ' + JSON.stringify(chooseBar(60, 1, { unit: 'm' })));
  console.log('  1:50,000,000, 60 mm frame (m): ' + JSON.stringify(chooseBar(60, 5e7, { unit: 'm' })));
  console.log('  narrow frame 20 mm at 1:500 (m): ' + JSON.stringify(chooseBar(20, 500, { unit: 'm' })));
  console.log('  1:1200 (1 in = 100 ft), 180 mm, ft: ' + JSON.stringify(chooseBar(180, 1200, { unit: 'ft', minMm: 50, maxMm: 150 })));
  console.log('  1:63360 (1 in = 1 mi), 180 mm, ft: ' + JSON.stringify(chooseBar(180, 63360, { unit: 'ft', minMm: 50, maxMm: 150 })));
  console.log('  QGIS fit, min > max: ' + JSON.stringify(qgisFit(180, 1000, 1, 150, 50, 2)));
  /* the prettySize walk on the comment's own example */
  console.log('  nextNice(4573.23,d) for d=1,10,100,1000: ' + [1, 10, 100, 1000].map(function (d) { return nextNice(4573.23, d); }).join(', '));
  console.log('  prevNice(4573.23,d) for d=1,10,100,1000: ' + [1, 10, 100, 1000].map(function (d) { return prevNice(4573.23, d); }).join(', '));
}
run();
