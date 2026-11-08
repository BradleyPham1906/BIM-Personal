// V174 research (2026-11-08), experiment (d): the frame cost of a 2000 x 1400 board with 200
// elements, normal against non-normal blend modes, and with isolated groups drawn through
// offscreen canvases. Research data, not a suite.
// Run: node docs/research/experiments/v174-blend/exp-d-cost.js
'use strict';
var chromium = require('playwright').chromium;
var N = 30, WARM = 3;

function pageRun(arg) {
  var W = 2000, H = 1400, N = arg.N, WARM = arg.WARM;
  var NON_NORMAL = ['multiply', 'screen', 'overlay', 'darken', 'lighten', 'color-dodge', 'color-burn',
    'hard-light', 'soft-light', 'difference', 'exclusion', 'hue', 'saturation', 'color', 'luminosity'];
  var NON_SEP = ['hue', 'saturation', 'color', 'luminosity'];
  function seeded(s) { return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  var r = seeded(5);
  function mk(w, h) { var c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
  var main = mk(W, H), g = main.getContext('2d', arg.opts);
  // A photo-like image element, pre-rendered, drawn by some elements.
  var img = mk(400, 300), ig = img.getContext('2d');
  var gr = ig.createLinearGradient(0, 0, 400, 300); gr.addColorStop(0, '#147'); gr.addColorStop(1, '#fc3');
  ig.fillStyle = gr; ig.fillRect(0, 0, 400, 300);
  // 200 elements in 20 groups of 10; each group's elements lie inside its own box.
  var groups = [], all = [];
  for (var gi = 0; gi < 20; gi++) {
    var gx = (gi % 5) * 400, gy = Math.floor(gi / 5) * 350, els = [];
    for (var k = 0; k < 10; k++) {
      var e = { kind: k % 3, x: gx + r() * 250, y: gy + r() * 200, w: 60 + r() * 140, h: 50 + r() * 140,
        color: 'hsl(' + Math.floor(r() * 360) + ',70%,' + Math.floor(30 + r() * 40) + '%)',
        mode: NON_NORMAL[Math.floor(r() * NON_NORMAL.length)], ns: NON_SEP[Math.floor(r() * 4)], alpha: 0.6 + r() * 0.4 };
      els.push(e); all.push(e);
    }
    groups.push({ x: gx, y: gy, w: 400, h: 350, els: els });
  }
  var pool = groups.map(function (gp) { return mk(gp.w, gp.h); });
  var full = groups.map(function () { return mk(W, H); });
  var single = mk(400, 400);
  function drawEl(c, e, mode, ox, oy) {
    c.globalCompositeOperation = mode; c.globalAlpha = e.alpha;
    var x = e.x - ox, y = e.y - oy;
    if (e.kind === 0) { c.fillStyle = e.color; c.fillRect(x, y, e.w, e.h); }
    else if (e.kind === 1) { c.fillStyle = e.color; c.beginPath(); c.ellipse(x + e.w / 2, y + e.h / 2, e.w / 2, e.h / 2, 0, 0, 6.2832); c.fill(); }
    else { c.drawImage(img, x, y, e.w, e.h); }
    c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
  }
  function background() { g.fillStyle = '#f4f1ea'; g.fillRect(0, 0, W, H); }
  function groupPass(childMode, groupMode, boards) {
    for (var i = 0; i < groups.length; i++) {
      var gp = groups[i], oc = boards[i], o = oc.getContext('2d'), ox = boards === full ? 0 : gp.x, oy = boards === full ? 0 : gp.y;
      o.clearRect(0, 0, oc.width, oc.height);
      for (var j = 0; j < gp.els.length; j++) drawEl(o, gp.els[j], childMode === 'random' ? gp.els[j].mode : childMode, ox, oy);
      g.globalAlpha = 0.7; g.globalCompositeOperation = groupMode;
      g.drawImage(oc, boards === full ? 0 : gp.x, boards === full ? 0 : gp.y);
      g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
    }
  }
  var variants = {
    '200 elements, normal': function () { all.forEach(function (e) { drawEl(g, e, 'source-over', 0, 0); }); },
    '200 elements, random non-normal modes': function () { all.forEach(function (e) { drawEl(g, e, e.mode, 0, 0); }); },
    '200 elements, non-separable modes only': function () { all.forEach(function (e) { drawEl(g, e, e.ns, 0, 0); }); },
    '20 isolated groups (box-sized), normal children': function () { groupPass('source-over', 'source-over', pool); },
    '20 isolated groups (box-sized), random children, group multiply': function () { groupPass('random', 'multiply', pool); },
    '20 isolated groups (board-sized offscreen)': function () { groupPass('source-over', 'source-over', full); },
    '200 elements each isolated (one offscreen each)': function () {
      var o = single.getContext('2d');
      all.forEach(function (e) {
        o.clearRect(0, 0, 400, 400); drawEl(o, { kind: e.kind, x: 0, y: 0, w: e.w, h: e.h, color: e.color, alpha: 1 }, 'source-over', 0, 0);
        g.globalAlpha = e.alpha; g.globalCompositeOperation = e.mode; g.drawImage(single, 0, 0, e.w, e.h, e.x, e.y, e.w, e.h);
        g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
      });
    }
  };
  var res = {};
  Object.keys(variants).forEach(function (name) {
    var t = [];
    for (var n = 0; n < N + WARM; n++) {
      var t0 = performance.now();
      background(); variants[name](); g.getImageData(0, 0, 1, 1);
      if (n >= WARM) t.push(performance.now() - t0);
    }
    t.sort(function (a, b) { return a - b; });
    res[name] = { median: t[Math.floor(t.length / 2)], p90: t[Math.floor(t.length * 0.9)], min: t[0], max: t[t.length - 1] };
  });
  return res;
}

(async function () {
  var browser = await chromium.launch(), page = await browser.newPage();
  console.log('Chromium ' + browser.version() + '; board 2000 x 1400; 200 elements (rect, ellipse, image); ' + N +
    ' frames after ' + WARM + ' warm-up; ms per frame incl. a 1-pixel read to flush');
  var variants = [['default context', {}], ['willReadFrequently context', { willReadFrequently: true }]];
  for (var v = 0; v < variants.length; v++) {
    var r = await page.evaluate(pageRun, { N: N, WARM: WARM, opts: variants[v][1] });
    console.log('\n' + variants[v][0] + ':');
    Object.keys(r).forEach(function (k) {
      var t = r[k];
      console.log('  ' + (k + '                                                                 ').slice(0, 66) + ' median ' + t.median.toFixed(1) +
        '  p90 ' + t.p90.toFixed(1) + '  min ' + t.min.toFixed(1) + '  max ' + t.max.toFixed(1));
    });
  }
  await browser.close();
})();
