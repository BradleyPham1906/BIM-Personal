// V174 research (2026-11-08), experiment (a): the 16 blend modes of canvas 2D in Chromium
// against our own W3C formulas (w3c-blend.js). Research data, not a suite.
// Run: node docs/research/experiments/v174-blend/exp-a-modes.js
'use strict';
var chromium = require('playwright').chromium;
var W3C = require('./w3c-blend.js');

var SIZE = 160;              // cells per side: 25,600 colour pairs per mode
var ALPHAS = [255, 254, 192, 128, 64, 16];
var EDGE = [0, 1, 63, 64, 65, 127, 128, 129, 191, 254, 255];

function rng(seed) { return function () { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }; }

function makeCases(seed) {
  var r = rng(seed), cases = [], i;
  function ch() { return r() < 0.4 ? EDGE[Math.floor(r() * EDGE.length)] : Math.floor(r() * 256); }
  for (i = 0; i < SIZE * SIZE; i++) {
    var opaque = i < SIZE * SIZE / 2;   // first half: both opaque
    cases.push({
      b: [ch(), ch(), ch(), opaque ? 255 : ALPHAS[Math.floor(r() * ALPHAS.length)]],
      s: [ch(), ch(), ch(), opaque ? 255 : ALPHAS[Math.floor(r() * ALPHAS.length)]]
    });
  }
  // Fixed edge pairs at the start (opaque): the spec's special cases.
  var fixed = [
    { b: [0, 0, 0, 255], s: [255, 255, 255, 255] },       // dodge cb=0, cs=1 (W3C 0; PDF 2008 1)
    { b: [255, 255, 255, 255], s: [0, 0, 0, 255] },       // burn cb=1, cs=0 (W3C 1; PDF 2008 0)
    { b: [64, 64, 64, 255], s: [200, 200, 200, 255] },    // soft-light D() boundary near 0.25
    { b: [100, 150, 200, 255], s: [128, 128, 128, 255] }, // hard-light boundary 128/255 > 0.5
    { b: [128, 128, 128, 255], s: [255, 0, 0, 255] },     // hue/colour on grey backdrop
    { b: [255, 0, 0, 255], s: [0, 0, 255, 255] }
  ];
  for (i = 0; i < fixed.length; i++) cases[i] = fixed[i];
  return cases;
}

function pageDraw(arg) {
  var size = arg.size, cases = arg.cases, mode = arg.mode, out = {};
  function draw(withSource, opts) {
    var c = document.createElement('canvas'); c.width = size; c.height = size;
    var g = c.getContext('2d', opts);
    for (var i = 0; i < cases.length; i++) {
      var x = i % size, y = Math.floor(i / size), b = cases[i].b, s = cases[i].s;
      g.globalCompositeOperation = 'source-over';
      g.fillStyle = 'rgba(' + b[0] + ',' + b[1] + ',' + b[2] + ',' + (b[3] / 255) + ')';
      g.fillRect(x, y, 1, 1);
      if (withSource) {
        g.globalCompositeOperation = mode;
        g.fillStyle = 'rgba(' + s[0] + ',' + s[1] + ',' + s[2] + ',' + (s[3] / 255) + ')';
        g.fillRect(x, y, 1, 1);
      }
    }
    return Array.prototype.slice.call(g.getImageData(0, 0, size, size).data);
  }
  out.gpu = { back: draw(false, {}), res: draw(true, {}) };
  out.cpu = { back: draw(false, { willReadFrequently: true }), res: draw(true, { willReadFrequently: true }) };
  return out;
}

function analyse(cases, back, res, mode) {
  var st = { opq: { max: 0, sum: 0, n: 0, over2: 0 }, tr: { max: 0, sum: 0, n: 0, over2: 0, maxPm: 0, maxA: 0 }, worst: null };
  for (var i = 0; i < cases.length; i++) {
    var k = i * 4, s = cases[i].s;
    var B = { c: [back[k] / 255, back[k + 1] / 255, back[k + 2] / 255], a: back[k + 3] / 255 };
    var S = { c: [s[0] / 255, s[1] / 255, s[2] / 255], a: Math.round(s[3]) / 255 };
    var R = W3C.composite(mode, B, S);
    var g = R.a === 1 && B.a === 1 && S.a === 1 ? st.opq : st.tr, e = 0, epm = 0;
    for (var j = 0; j < 3; j++) {
      var d = Math.abs(res[k + j] - R.c[j] * 255);
      if (d > e) e = d;
      var dpm = Math.abs(res[k + j] * res[k + 3] / 255 - R.c[j] * R.a * 255);
      if (dpm > epm) epm = dpm;
    }
    var ea = Math.abs(res[k + 3] - R.a * 255);
    g.n++; g.sum += e; if (e > g.max) g.max = e; if (e > 2) g.over2++;
    if (g === st.tr) {
      if (epm > g.maxPm) {
        g.maxPm = epm;
        st.worstTr = { epm: +epm.toFixed(2), b: [back[k], back[k + 1], back[k + 2], back[k + 3]], s: s,
          got: [res[k], res[k + 1], res[k + 2], res[k + 3]],
          want: R.c.map(function (v) { return +(v * 255).toFixed(2); }).concat([+(R.a * 255).toFixed(2)]) };
      }
      if (ea > g.maxA) g.maxA = ea;
    }
    if (g === st.opq && (!st.worst || e > st.worst.e)) {
      st.worst = { e: +e.toFixed(2), b: [back[k], back[k + 1], back[k + 2], back[k + 3]], s: s,
        got: [res[k], res[k + 1], res[k + 2], res[k + 3]], want: R.c.map(function (v) { return +(v * 255).toFixed(2); }) };
    }
  }
  return st;
}

(async function () {
  var browser = await chromium.launch(), page = await browser.newPage();
  console.log('Chromium ' + browser.version() + ', ' + (await page.evaluate(function () { return navigator.userAgent; })));
  console.log('cells per mode: ' + SIZE * SIZE + ' (half opaque, half with alpha in ' + ALPHAS.join('/') + ')');
  console.log('error = |canvas - W3C reference| in 8-bit units, unpremultiplied colour; pm = premultiplied colour; a = alpha');
  var cases = makeCases(17401), edges = [];
  var only = process.env.MODES ? process.env.MODES.split(',') : null;
  for (var m = 0; m < W3C.MODES.length; m++) {
    var mode = W3C.MODES[m];
    if (only && only.indexOf(mode) < 0) continue;
    var r = await page.evaluate(pageDraw, { size: SIZE, cases: cases, mode: mode });
    ['gpu', 'cpu'].forEach(function (path) {
      var st = analyse(cases, r[path].back, r[path].res, mode);
      console.log([mode, path === 'gpu' ? 'default ctx' : 'willReadFrequently',
        'opaque max ' + st.opq.max.toFixed(2), 'mean ' + (st.opq.sum / st.opq.n).toFixed(3), '>2: ' + st.opq.over2,
        'translucent max ' + st.tr.max.toFixed(2), 'mean ' + (st.tr.sum / st.tr.n).toFixed(3), '>2: ' + st.tr.over2,
        'pm max ' + st.tr.maxPm.toFixed(2), 'a max ' + st.tr.maxA.toFixed(2)].join(' | '));
      if (path === 'gpu') console.log('   worst opaque: ' + JSON.stringify(st.worst));
      if (path === 'gpu') console.log('   worst translucent (premultiplied): ' + JSON.stringify(st.worstTr));
    });
    for (var e = 0; e < 6; e++) {
      edges.push(mode + ' edge' + e + ' b=' + cases[e].b.slice(0, 3) + ' s=' + cases[e].s.slice(0, 3) + ' -> ' +
        r.gpu.res.slice(e * 4, e * 4 + 4) + ' (cpu ' + r.cpu.res.slice(e * 4, e * 4 + 4) + ') W3C ' +
        W3C.composite(mode, { c: cases[e].b.slice(0, 3).map(function (v) { return v / 255; }), a: 1 },
          { c: cases[e].s.slice(0, 3).map(function (v) { return v / 255; }), a: 1 }).c.map(function (v) { return Math.round(v * 255); }));
    }
  }
  console.log('\nEdge pairs (opaque):');
  edges.forEach(function (l) { if (/color-dodge edge0|color-burn edge1|soft-light edge2|hard-light edge3|overlay edge3|hue edge4|color edge4|saturation edge4|luminosity edge5|hue edge5/.test(l)) console.log('  ' + l); });
  await browser.close();
})();
