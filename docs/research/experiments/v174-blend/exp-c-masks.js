// V174 research (2026-11-08), experiment (c): masks on a 2000 x 1400 board in canvas 2D.
// clip() (vector), destination-in with an alpha mask, luminance masks by pixel work and by an
// SVG feColorMatrix filter; the cost of each over N runs, and clip()'s edge anti-aliasing.
// Research data, not a suite. Run: node docs/research/experiments/v174-blend/exp-c-masks.js
'use strict';
var chromium = require('playwright').chromium;
var N = 30, WARM = 3;

var HTML = '<!doctype html><html><body>' +
  '<svg width="0" height="0" style="position:absolute"><filter id="l2a" color-interpolation-filters="sRGB">' +
  '<feColorMatrix type="luminanceToAlpha"/></filter></svg></body></html>';

function pageRun(arg) {
  var W = 2000, H = 1400, N = arg.N, WARM = arg.WARM, opts = arg.opts;
  function mk() { var c = document.createElement('canvas'); c.width = W; c.height = H; return c; }
  function seeded(s) { return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  var r = seeded(9);
  // The masked element: a busy picture (gradient and 400 shapes), pre-rendered.
  var content = mk(), cg = content.getContext('2d');
  var lg = cg.createLinearGradient(0, 0, W, H); lg.addColorStop(0, '#2a6'); lg.addColorStop(1, '#a26');
  cg.fillStyle = lg; cg.fillRect(0, 0, W, H);
  for (var i = 0; i < 400; i++) {
    cg.fillStyle = 'hsl(' + Math.floor(r() * 360) + ',70%,50%)';
    cg.beginPath(); cg.arc(r() * W, r() * H, 10 + r() * 80, 0, 6.2832); cg.fill();
  }
  // Alpha mask: radial gradient, opaque centre to transparent edge.
  var amask = mk(), ag = amask.getContext('2d');
  var rg = ag.createRadialGradient(W / 2, H / 2, 100, W / 2, H / 2, 700);
  rg.addColorStop(0, 'rgba(0,0,0,1)'); rg.addColorStop(1, 'rgba(0,0,0,0)');
  ag.fillStyle = rg; ag.fillRect(0, 0, W, H);
  // Luminance mask source: opaque, black to white horizontal ramp with a white disc.
  var lsrc = mk(), lg2 = lsrc.getContext('2d');
  var hg = lg2.createLinearGradient(0, 0, W, 0); hg.addColorStop(0, '#000'); hg.addColorStop(1, '#fff');
  lg2.fillStyle = hg; lg2.fillRect(0, 0, W, H);
  lg2.fillStyle = '#ff0000'; lg2.beginPath(); lg2.arc(500, 700, 200, 0, 6.2832); lg2.fill();

  var main = mk(), g = main.getContext('2d', opts);
  var tmp = mk(), tg = tmp.getContext('2d', opts);
  var lmask = mk(), lmg = lmask.getContext('2d', { willReadFrequently: true });
  var lmask2 = mk(), lm2 = lmask2.getContext('2d');
  var srcG = lsrc.getContext('2d', { willReadFrequently: true });

  function clipPath(c) {
    c.beginPath(); c.ellipse(W / 2, H / 2, 800, 500, 0.3, 0, 6.2832);
    c.moveTo(100, 100); c.lineTo(600, 150); c.lineTo(300, 600); c.closePath();
  }
  function lumByPixels() {
    var d = srcG.getImageData(0, 0, W, H), p = d.data;
    for (var k = 0; k < p.length; k += 4) {
      // Luminance-to-alpha (Filter Effects 1 coefficients) times alpha, as CSS Masking 7.10.1.
      var l = (0.2126 * p[k] + 0.7152 * p[k + 1] + 0.0722 * p[k + 2]) * p[k + 3] / 255;
      p[k] = 0; p[k + 1] = 0; p[k + 2] = 0; p[k + 3] = l;
    }
    lmg.putImageData(d, 0, 0);
    return lmask;
  }
  function lumByFilter() {
    lm2.clearRect(0, 0, W, H); lm2.filter = 'url(#l2a)'; lm2.drawImage(lsrc, 0, 0); lm2.filter = 'none';
    return lmask2;
  }
  function viaDestIn(maskCanvas) {
    tg.globalCompositeOperation = 'source-over'; tg.clearRect(0, 0, W, H); tg.drawImage(content, 0, 0);
    tg.globalCompositeOperation = 'destination-in'; tg.drawImage(maskCanvas, 0, 0);
    tg.globalCompositeOperation = 'source-over'; g.drawImage(tmp, 0, 0);
  }
  var cachedLum = null;
  var methods = {
    'none (drawImage only)': function () { g.drawImage(content, 0, 0); },
    'clip() vector path': function () { g.save(); clipPath(g); g.clip(); g.drawImage(content, 0, 0); g.restore(); },
    'alpha mask: destination-in, mask canvas': function () { viaDestIn(amask); },
    'alpha mask: destination-in, gradient fill': function () {
      tg.globalCompositeOperation = 'source-over'; tg.clearRect(0, 0, W, H); tg.drawImage(content, 0, 0);
      tg.globalCompositeOperation = 'destination-in'; tg.fillStyle = rg; tg.fillRect(0, 0, W, H);
      tg.globalCompositeOperation = 'source-over'; g.drawImage(tmp, 0, 0);
    },
    'luminance mask: pixels each frame': function () { viaDestIn(lumByPixels()); },
    'luminance mask: pixels once, cached': function () { if (!cachedLum) { lumByPixels(); cachedLum = true; } viaDestIn(lmask); },
    'luminance mask: SVG filter each frame': function () { viaDestIn(lumByFilter()); }
  };
  var res = {};
  Object.keys(methods).forEach(function (name) {
    var t = [];
    for (var n = 0; n < N + WARM; n++) {
      var t0 = performance.now();
      g.clearRect(0, 0, W, H); g.fillStyle = '#eee'; g.fillRect(0, 0, W, H);
      methods[name]();
      g.getImageData(0, 0, 1, 1);           // force the work to finish before the clock stops
      var dt = performance.now() - t0;
      if (n >= WARM) t.push(dt);
    }
    t.sort(function (a, b) { return a - b; });
    res[name] = { median: t[Math.floor(t.length / 2)], p90: t[Math.floor(t.length * 0.9)], min: t[0], max: t[t.length - 1] };
  });
  // Agreement of the two luminance masks (alpha of the mask canvas at sample points).
  lumByPixels(); lumByFilter();
  var pts = [[0, 50], [500, 50], [1000, 50], [1500, 50], [1999, 50], [500, 700]], agree = [];
  pts.forEach(function (q) {
    agree.push({ at: q, pixels: lmg.getImageData(q[0], q[1], 1, 1).data[3], filter: lm2.getImageData(q[0], q[1], 1, 1).data[3] });
  });
  var mx = 0, a1 = lmg.getImageData(0, 0, W, 4).data, a2 = lm2.getImageData(0, 0, W, 4).data;
  for (var k = 3; k < a1.length; k += 4) mx = Math.max(mx, Math.abs(a1[k] - a2[k]));
  return { times: res, lumAgreement: agree, lumMaxAlphaDiffRow: mx, filterSupported: typeof lm2.filter === 'string' };
}

function pageAA() {
  // clip() edge anti-aliasing vs a plain fill of the same circle, and the conflation seam.
  var c = document.createElement('canvas'); c.width = 200; c.height = 200;
  var g = c.getContext('2d');
  function partial(gg) {
    var d = gg.getImageData(0, 0, 200, 200).data, n = 0, full = 0;
    for (var i = 3; i < d.length; i += 4) { if (d[i] > 0 && d[i] < 255) n++; if (d[i] === 255) full++; }
    return { partialPixels: n, fullPixels: full };
  }
  g.fillStyle = '#f00'; g.beginPath(); g.arc(100, 100, 60.3, 0, 6.2832); g.fill();
  var fill = partial(g), fillData = g.getImageData(0, 0, 200, 200).data;
  g.clearRect(0, 0, 200, 200);
  g.save(); g.beginPath(); g.arc(100, 100, 60.3, 0, 6.2832); g.clip(); g.fillRect(0, 0, 200, 200); g.restore();
  var clip = partial(g), clipData = g.getImageData(0, 0, 200, 200).data, mx = 0;
  for (var i = 3; i < fillData.length; i += 4) mx = Math.max(mx, Math.abs(fillData[i] - clipData[i]));
  // Seam: two halves clipped at x = 100.5, both opaque red; the seam column should be opaque.
  g.clearRect(0, 0, 200, 200);
  g.save(); g.beginPath(); g.rect(0, 0, 100.5, 200); g.clip(); g.fillRect(0, 0, 200, 200); g.restore();
  g.save(); g.beginPath(); g.rect(100.5, 0, 99.5, 200); g.clip(); g.fillRect(0, 0, 200, 200); g.restore();
  var seamClip = Array.prototype.slice.call(g.getImageData(100, 50, 1, 1).data);
  g.clearRect(0, 0, 200, 200);
  g.fillRect(0, 0, 100.5, 200); g.fillRect(100.5, 0, 99.5, 200);
  var seamFill = Array.prototype.slice.call(g.getImageData(100, 50, 1, 1).data);
  // Unbounded operators: source-in with a clip, outside the shape but inside the clip.
  g.clearRect(0, 0, 200, 200); g.fillStyle = '#00f'; g.fillRect(0, 0, 200, 200);
  g.save(); g.beginPath(); g.rect(0, 0, 100, 200); g.clip();
  g.globalCompositeOperation = 'source-in'; g.fillStyle = '#f00'; g.fillRect(0, 0, 50, 50); g.restore();
  var srcIn = { insideShape: Array.prototype.slice.call(g.getImageData(10, 10, 1, 1).data),
    outsideShapeInsideClip: Array.prototype.slice.call(g.getImageData(80, 100, 1, 1).data),
    outsideClip: Array.prototype.slice.call(g.getImageData(150, 100, 1, 1).data) };
  return { fill: fill, clip: clip, maxAlphaDiffFillVsClip: mx, seamClip: seamClip, seamFill: seamFill, sourceInUnbounded: srcIn };
}

(async function () {
  var browser = await chromium.launch(), page = await browser.newPage();
  await page.setContent(HTML);
  console.log('Chromium ' + browser.version() + '; board 2000 x 1400; ' + N + ' timed runs after ' + WARM + ' warm-up; ms per frame incl. a 1-pixel read to flush');
  var variants = [['default context', {}], ['willReadFrequently context', { willReadFrequently: true }]];
  for (var v = 0; v < variants.length; v++) {
    var r = await page.evaluate(pageRun, { N: N, WARM: WARM, opts: variants[v][1] });
    console.log('\n' + variants[v][0] + ':');
    Object.keys(r.times).forEach(function (k) {
      var t = r.times[k];
      console.log('  ' + (k + '                                            ').slice(0, 42) + ' median ' + t.median.toFixed(1) +
        '  p90 ' + t.p90.toFixed(1) + '  min ' + t.min.toFixed(1) + '  max ' + t.max.toFixed(1));
    });
    if (v === 0) {
      console.log('  luminance mask, pixels vs SVG filter (mask alpha): ' + JSON.stringify(r.lumAgreement));
      console.log('  max alpha difference over the top 4 rows: ' + r.lumMaxAlphaDiffRow + '; ctx.filter present: ' + r.filterSupported);
    }
  }
  console.log('\nAnti-aliasing and unbounded operators: ' + JSON.stringify(await page.evaluate(pageAA), null, 1));
  await browser.close();
})();
