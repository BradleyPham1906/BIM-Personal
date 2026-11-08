// V174 research (2026-11-08), experiment (b): group opacity and isolation on canvas 2D.
// Naive per-child globalAlpha against an isolated offscreen group; pass-through against
// isolated groups for children with a blend mode. Research data, not a suite.
// Run: node docs/research/experiments/v174-blend/exp-b-groups.js
'use strict';
var chromium = require('playwright').chromium;
var W3C = require('./w3c-blend.js');

function pageRun() {
  var W = 120, H = 60;
  function mk(w, h) { var c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
  function px(g, x, y) { return Array.prototype.slice.call(g.getImageData(x, y, 1, 1).data); }
  function backdrop(g) {
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, W, H);
    g.fillStyle = 'rgb(0,128,255)'; g.fillRect(0, 30, W, 30);  // lower half blue
  }
  // children: red 10..70, green 50..110, full height
  function children(g, mode, alpha) {
    g.globalAlpha = alpha; g.globalCompositeOperation = mode;
    g.fillStyle = 'rgb(255,0,0)'; g.fillRect(10, 0, 60, H);
    g.fillStyle = 'rgb(0,200,0)'; g.fillRect(50, 0, 60, H);
    g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
  }
  function sample(g) {
    return { redOnly: px(g, 30, 10), overlap: px(g, 60, 10), greenOnly: px(g, 90, 10),
      redOnlyBlue: px(g, 30, 45), overlapBlue: px(g, 60, 45), greenOnlyBlue: px(g, 90, 45) };
  }
  function diffCount(a, b) {
    var da = a.getContext('2d').getImageData(0, 0, W, H).data, db = b.getContext('2d').getImageData(0, 0, W, H).data, n = 0, mx = 0;
    for (var i = 0; i < da.length; i += 4) {
      var d = Math.max(Math.abs(da[i] - db[i]), Math.abs(da[i + 1] - db[i + 1]), Math.abs(da[i + 2] - db[i + 2]));
      if (d > 0) n++; if (d > mx) mx = d;
    }
    return { pixelsDiffering: n, of: W * H, maxChannelDiff: mx };
  }
  var out = {};

  // 1. Group opacity 0.5, children normal.
  var naive = mk(W, H), ng = naive.getContext('2d'); backdrop(ng); children(ng, 'source-over', 0.5);
  var iso = mk(W, H), ig = iso.getContext('2d'); backdrop(ig);
  var off = mk(W, H), og = off.getContext('2d'); children(og, 'source-over', 1);
  ig.globalAlpha = 0.5; ig.drawImage(off, 0, 0); ig.globalAlpha = 1;
  out.opacity = { naive: sample(ng), isolated: sample(ig), diff: diffCount(naive, iso) };

  // 2. Children multiply: pass-through (drawn on the board) vs isolated (offscreen, then normal).
  var pass = mk(W, H), pg = pass.getContext('2d'); backdrop(pg); children(pg, 'multiply', 1);
  var iso2 = mk(W, H), i2 = iso2.getContext('2d'); backdrop(i2);
  var off2 = mk(W, H), o2 = off2.getContext('2d'); children(o2, 'multiply', 1); i2.drawImage(off2, 0, 0);
  out.multiply = { passThrough: sample(pg), isolated: sample(i2), diff: diffCount(pass, iso2) };

  // 3. Isolated group with its own blend mode (the group multiplies as one) and opacity 0.5.
  var gm = mk(W, H), gg = gm.getContext('2d'); backdrop(gg);
  gg.globalAlpha = 0.5; gg.globalCompositeOperation = 'multiply'; gg.drawImage(off, 0, 0);
  out.groupMode = sample(gg);

  // 4. Group invariance: a default group (normal, opacity 1) drawn via offscreen equals direct.
  var d1 = mk(W, H), dg = d1.getContext('2d'); backdrop(dg); children(dg, 'source-over', 1);
  var d2 = mk(W, H), dg2 = d2.getContext('2d'); backdrop(dg2); dg2.drawImage(off, 0, 0);
  out.invariance = diffCount(d1, d2);

  // 5. Offscreen at a non-integer device position: drawImage at (0.5, 0) resamples (blur).
  var d3 = mk(W, H), dg3 = d3.getContext('2d'); backdrop(dg3); dg3.drawImage(off, 0.5, 0);
  out.subpixelOffset = { edgePixel10: px(dg3, 10, 10), diff: diffCount(d1, d3) };
  return out;
}

(async function () {
  var browser = await chromium.launch(), page = await browser.newPage();
  console.log('Chromium ' + browser.version());
  var r = await page.evaluate(pageRun);
  var white = { c: [1, 1, 1], a: 1 }, blue = { c: [0, 128 / 255, 1], a: 1 };
  var red = { c: [1, 0, 0], a: 0.5 }, green = { c: [0, 200 / 255, 0], a: 0.5 };
  function to8(o) { return o.c.map(function (v) { return Math.round(v * 255); }); }
  // Reference for case 1.
  var naiveRef = W3C.composite('normal', W3C.composite('normal', white, red), green);
  var isoRef = W3C.composite('normal', white, { c: [0, 200 / 255, 0], a: 0.5 });
  console.log('\n1. Group opacity 0.5 over white (children opaque red, green):');
  console.log('   naive per-child globalAlpha overlap: ' + r.opacity.naive.overlap + '  (W3C chain ' + to8(naiveRef) + ')');
  console.log('   isolated offscreen overlap:          ' + r.opacity.isolated.overlap + '  (W3C group ' + to8(isoRef) + ')');
  console.log('   red only: naive ' + r.opacity.naive.redOnly + ' isolated ' + r.opacity.isolated.redOnly);
  console.log('   over blue, overlap: naive ' + r.opacity.naive.overlapBlue + ' isolated ' + r.opacity.isolated.overlapBlue);
  console.log('   pixels differing: ' + JSON.stringify(r.opacity.diff));
  console.log('\n2. Children multiply, group normal at opacity 1:');
  console.log('   pass-through: red only ' + r.multiply.passThrough.redOnly + ' overlap ' + r.multiply.passThrough.overlap +
    ' | over blue: red only ' + r.multiply.passThrough.redOnlyBlue + ' overlap ' + r.multiply.passThrough.overlapBlue);
  console.log('   isolated:     red only ' + r.multiply.isolated.redOnly + ' overlap ' + r.multiply.isolated.overlap +
    ' | over blue: red only ' + r.multiply.isolated.redOnlyBlue + ' overlap ' + r.multiply.isolated.overlapBlue);
  console.log('   W3C over blue, pass-through red: ' + to8(W3C.composite('multiply', blue, { c: [1, 0, 0], a: 1 })) +
    '; isolated red: 255,0,0 (red multiplied with a transparent initial backdrop is red)');
  console.log('   pixels differing: ' + JSON.stringify(r.multiply.diff));
  console.log('\n3. Isolated group drawn with multiply at opacity 0.5: ' + JSON.stringify(r.groupMode));
  var gmRef = W3C.composite('multiply', blue, { c: [0, 200 / 255, 0], a: 0.5 });
  console.log('   W3C over blue, green part: ' + to8(gmRef));
  console.log('\n4. Group invariance (offscreen at opacity 1, normal, vs direct): ' + JSON.stringify(r.invariance));
  console.log('5. Offscreen drawn at x+0.5: ' + JSON.stringify(r.subpixelOffset));
  await browser.close();
})();
