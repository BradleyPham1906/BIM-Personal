// V174 research (2026-11-08), experiment (f): does an SVG with mix-blend-mode, opacity, masks
// and isolation (the V176 export path) render the same pixels in Chromium as the canvas 2D
// board does? The SVG is drawn as an image into a canvas and read back. Research data.
// Run: node docs/research/experiments/v174-blend/exp-f-svg-parity.js
'use strict';
var chromium = require('playwright').chromium;
var W3C = require('./w3c-blend.js');
var G = 20;   // 20 x 20 colour pairs per mode

function rng(seed) { return function () { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }; }

async function pageRun(arg) {
  var G = arg.G, modes = arg.modes, cases = arg.cases, out = {};
  function load(svg) {
    return new Promise(function (res, rej) {
      var im = new Image(); im.onload = function () { res(im); }; im.onerror = rej;
      im.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    });
  }
  function rgb(c) { return 'rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')'; }
  for (var m = 0; m < modes.length; m++) {
    var mode = modes[m], parts = [], i;
    for (i = 0; i < cases.length; i++) {
      var x = i % G, y = Math.floor(i / G), c = cases[i];
      parts.push('<rect x="' + x + '" y="' + y + '" width="1" height="1" fill="' + rgb(c.b) + '" fill-opacity="' + c.ab + '"/>');
      parts.push('<rect x="' + x + '" y="' + y + '" width="1" height="1" fill="' + rgb(c.s) + '" fill-opacity="' + c.as + '" style="mix-blend-mode:' + mode + '"/>');
    }
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + G + '" height="' + G + '" shape-rendering="crispEdges">' + parts.join('') + '</svg>';
    var im = await load(svg), cv = document.createElement('canvas'); cv.width = G; cv.height = G;
    var g = cv.getContext('2d'); g.drawImage(im, 0, 0);
    var svgPx = Array.prototype.slice.call(g.getImageData(0, 0, G, G).data);
    // The same pairs on canvas 2D.
    var cv2 = document.createElement('canvas'); cv2.width = G; cv2.height = G; var g2 = cv2.getContext('2d');
    for (i = 0; i < cases.length; i++) {
      var xx = i % G, yy = Math.floor(i / G), cc = cases[i];
      g2.globalCompositeOperation = 'source-over'; g2.fillStyle = 'rgba(' + cc.b.join(',') + ',' + cc.ab + ')'; g2.fillRect(xx, yy, 1, 1);
      g2.globalCompositeOperation = mode === 'normal' ? 'source-over' : mode;
      g2.fillStyle = 'rgba(' + cc.s.join(',') + ',' + cc.as + ')'; g2.fillRect(xx, yy, 1, 1);
    }
    out[mode] = { svg: svgPx, canvas: Array.prototype.slice.call(g2.getImageData(0, 0, G, G).data) };
  }
  // Masks and isolation in SVG.
  var maskSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="10">' +
    '<mask id="mL"><rect width="40" height="10" fill="rgb(128,128,128)"/></mask>' +
    '<mask id="mA" style="mask-type:alpha"><rect width="40" height="10" fill="rgb(128,128,128)" fill-opacity="0.25"/></mask>' +
    '<mask id="mL2"><rect width="40" height="10" fill="rgb(255,0,0)"/></mask>' +
    '<rect x="0" width="10" height="10" fill="#000" mask="url(#mL)"/>' +
    '<rect x="10" width="10" height="10" fill="#000" mask="url(#mA)"/>' +
    '<rect x="20" width="10" height="10" fill="#000" mask="url(#mL2)"/>' +
    '</svg>';
  var mi = await load(maskSvg), mc = document.createElement('canvas'); mc.width = 40; mc.height = 10;
  var mg = mc.getContext('2d'); mg.drawImage(mi, 0, 0);
  out.masks = { luminanceDefault_grey128: mg.getImageData(5, 5, 1, 1).data[3], alphaType_quarter: mg.getImageData(15, 5, 1, 1).data[3],
    luminanceDefault_red: mg.getImageData(25, 5, 1, 1).data[3] };
  var isoSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10">' +
    '<rect width="20" height="10" fill="rgb(0,128,255)"/>' +
    '<g><rect x="0" width="10" height="10" fill="rgb(255,0,0)" style="mix-blend-mode:multiply"/></g>' +
    '<g style="isolation:isolate"><rect x="10" width="10" height="10" fill="rgb(255,0,0)" style="mix-blend-mode:multiply"/></g>' +
    '</svg>';
  var ii = await load(isoSvg), ic = document.createElement('canvas'); ic.width = 20; ic.height = 10;
  var icg = ic.getContext('2d'); icg.drawImage(ii, 0, 0);
  out.isolation = { plainGroup: Array.prototype.slice.call(icg.getImageData(5, 5, 1, 1).data),
    isolatedGroup: Array.prototype.slice.call(icg.getImageData(15, 5, 1, 1).data) };
  return out;
}

(async function () {
  var browser = await chromium.launch(), page = await browser.newPage();
  console.log('Chromium ' + browser.version() + '; ' + G * G + ' pairs per mode; half opaque, half alpha 0.5/0.75');
  var r = rng(4242), cases = [];
  for (var i = 0; i < G * G; i++) {
    var op = i < G * G / 2;
    cases.push({ b: [0, 0, 0].map(function () { return Math.floor(r() * 256); }), s: [0, 0, 0].map(function () { return Math.floor(r() * 256); }),
      ab: op ? 1 : 0.75, as: op ? 1 : 0.5 });
  }
  var res = await page.evaluate(pageRun, { G: G, modes: W3C.MODES, cases: cases });
  W3C.MODES.forEach(function (mode) {
    var a = res[mode].svg, b = res[mode].canvas, mxO = 0, mxT = 0, mxRefO = 0;
    for (var k = 0; k < cases.length; k++) {
      var d = 0;
      for (var j = 0; j < 4; j++) d = Math.max(d, Math.abs(a[k * 4 + j] - b[k * 4 + j]));
      if (k < cases.length / 2) {
        mxO = Math.max(mxO, d);
        var R = W3C.composite(mode, { c: cases[k].b.map(function (v) { return v / 255; }), a: 1 }, { c: cases[k].s.map(function (v) { return v / 255; }), a: 1 });
        for (j = 0; j < 3; j++) mxRefO = Math.max(mxRefO, Math.abs(a[k * 4 + j] - R.c[j] * 255));
      } else mxT = Math.max(mxT, d);
    }
    console.log('  ' + (mode + '            ').slice(0, 12) + ' SVG vs canvas max channel diff: opaque ' + mxO + ', translucent ' + mxT +
      ' | SVG vs W3C (opaque) ' + mxRefO.toFixed(2));
  });
  console.log('SVG masks (alpha of black rect): ' + JSON.stringify(res.masks) +
    '  [luminance of grey 128 = 128; alpha-type 0.25 = 64; red under luminance: 0.2126*255 = 54 (sRGB) or about 0.2126*255 in linear = 54 too; check]');
  console.log('SVG isolation over rgb(0,128,255), red multiply child: ' + JSON.stringify(res.isolation));
  await browser.close();
})();
