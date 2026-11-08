// V174 research (2026-11-08), experiment (e): which strings globalCompositeOperation accepts,
// what an unknown or wrongly cased one does, and what globalAlpha does out of range.
// Research data, not a suite. Run: node docs/research/experiments/v174-blend/exp-e-keywords.js
'use strict';
var chromium = require('playwright').chromium;

var CANDIDATES = ['normal', 'multiply', 'screen', 'overlay', 'darken', 'lighten', 'color-dodge', 'color-burn',
  'hard-light', 'soft-light', 'difference', 'exclusion', 'hue', 'saturation', 'color', 'luminosity',
  'clear', 'copy', 'source-over', 'destination-over', 'source-in', 'destination-in', 'source-out',
  'destination-out', 'source-atop', 'destination-atop', 'xor', 'lighter',
  // not in the two grammars:
  'plus-lighter', 'plus-darker', 'darker', 'linear-burn', 'linear-dodge', 'pass-through', 'Multiply', 'MULTIPLY',
  ' multiply', 'multiply ', 'colorDodge', 'ColorDodge', 'color_dodge', 'over', 'foo', '', 'destination'];

function pageRun(cands) {
  var c = document.createElement('canvas'); c.width = 4; c.height = 4;
  var g = c.getContext('2d'), out = [];
  cands.forEach(function (s) {
    g.globalCompositeOperation = 'multiply';           // a known prior value
    var threw = false;
    try { g.globalCompositeOperation = s; } catch (e) { threw = String(e); }
    out.push({ set: s, readBack: g.globalCompositeOperation, accepted: g.globalCompositeOperation === s && s !== 'multiply' || s === 'multiply', threw: threw });
  });
  // Drawing after an ignored value uses the previous operator.
  g.globalCompositeOperation = 'source-over'; g.fillStyle = 'rgb(200,100,50)'; g.fillRect(0, 0, 4, 4);
  g.globalCompositeOperation = 'difference'; g.globalCompositeOperation = 'linear-burn';
  g.fillStyle = 'rgb(255,255,255)'; g.fillRect(0, 0, 4, 4);
  var px = Array.prototype.slice.call(g.getImageData(0, 0, 1, 1).data);
  var alpha = [];
  [0.5, 1.5, -0.1, NaN, Infinity, '0.3', null].forEach(function (v) {
    g.globalAlpha = 0.25; var threw = false;
    try { g.globalAlpha = v; } catch (e) { threw = String(e); }
    alpha.push({ set: String(v), readBack: g.globalAlpha, threw: threw });
  });
  var saveRestore = (function () {
    g.globalCompositeOperation = 'hue'; g.globalAlpha = 0.4; g.save();
    g.globalCompositeOperation = 'xor'; g.globalAlpha = 0.9; g.restore();
    return [g.globalCompositeOperation, g.globalAlpha];
  })();
  var filter = (function () {
    g.filter = 'none'; g.filter = 'url(#missing)'; var a = g.filter;
    g.filter = 'blur(2px'; var b = g.filter;
    return { afterMissingUrl: a, afterBadSyntax: b };
  })();
  return { modes: out, pixelAfterIgnoredMode: px, alpha: alpha, saveRestore: saveRestore, filter: filter };
}

(async function () {
  var browser = await chromium.launch(), page = await browser.newPage();
  console.log('Chromium ' + browser.version());
  var r = await page.evaluate(pageRun, CANDIDATES);
  r.modes.forEach(function (m) {
    console.log('  ' + JSON.stringify(m.set) + ' -> ' + JSON.stringify(m.readBack) + (m.threw ? ' THREW ' + m.threw : '') +
      (m.readBack === m.set ? '  (accepted)' : '  (ignored, kept previous)'));
  });
  console.log('pixel after difference then an ignored "linear-burn", white over rgb(200,100,50): ' + r.pixelAfterIgnoredMode +
    ' (difference gives 55,155,205)');
  console.log('globalAlpha (previous 0.25): ' + JSON.stringify(r.alpha));
  console.log('save/restore keeps operator and alpha: ' + JSON.stringify(r.saveRestore));
  console.log('filter strings: ' + JSON.stringify(r.filter));
  await browser.close();
})();
