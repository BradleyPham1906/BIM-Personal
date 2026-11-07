// e02_browser.js -- the B-rep kernel research (reference/research-usd-brep.md), 2026-11-01.
// Runs NVIDIA's SMLib, built by e02_build.sh, the way the one-file app would have to carry it: the
// single-file build (wasm embedded as base64 in a classic script) placed inside a page opened from
// file://, started in a Worker made from a Blob URL (SMLib's rule: one kernel per worker, restarted
// after a crash). Measures, per run: the time to instantiate the module, the first call and a second
// call of each operation (Chromium compiles functions lazily, so the first call carries the compile),
// each result against its expected value, and the module's memory afterwards.
// Also runs the ES-module build once under Node, as a cross-check of the results.
// 5 runs, a fresh browser each. Playwright 1.63.0, chromium-1243 in /opt/pw-browsers.
// Usage: E02_OUT=<the build's output dir> node e02_browser.js   (writes e02_results.json beside it)
'use strict';
var pw = require('playwright');
var fs = require('fs');
var path = require('path');

var OUT = process.env.E02_OUT;
if (!OUT) { console.error('set E02_OUT'); process.exit(2); }
var PI = Math.PI;
var CASES = [
  ['box_minus_cylinder', 300 - 12 * PI],
  ['plate16', 12 * 12 * 1.5 - 16 * PI * 0.75 * 0.75 * 1.5],
  ['wall_join_union', 4.68],
  ['fillet_box_edge', 1000 - (1 - PI / 4) * 10],
  ['tessellate_plate', 1]
];

// The worker's own code, appended to the kernel's script. ES5.
var WORKER_TAIL = '\n;(function(){var t0=performance.now();SmlibModule().then(function(m){' +
  'var r={instantiateMs:performance.now()-t0,cases:{}};m._e02_init();' +
  'var names=' + JSON.stringify(CASES.map(function (c) { return c[0]; })) + ';' +
  'for(var i=0;i<names.length;i++){var f=m["_e02_"+names[i]];' +
  'var a=performance.now();var v1=f();var b=performance.now();var v2=f();var c=performance.now();' +
  'r.cases[names[i]]={first:v1,firstMs:b-a,second:v2,secondMs:c-b};}' +
  'r.heapBytes=m.HEAPU8.length;r.sab=typeof SharedArrayBuffer;postMessage(r);' +
  '},function(e){postMessage({error:String(e)});});})();\n';

function pageHtml(kernelJs) {
  var safe = kernelJs.split('</script').join('<\\/script');
  return '<!doctype html><html><head><meta charset="utf-8"><title>e02</title></head><body>e02' +
    '<script id="kernel" type="text/plain">' + safe + '</script>' +
    '<script>\n' +
    'window.__r = { origin: location.protocol };\n' +
    'var src = document.getElementById("kernel").textContent + ' + JSON.stringify(WORKER_TAIL) + ';\n' +
    'var t0 = performance.now();\n' +
    'var w = new Worker(URL.createObjectURL(new Blob([src], { type: "text/javascript" })));\n' +
    'w.onmessage = function (e) { var r = e.data; r.workerTotalMs = performance.now() - t0; r.origin = location.protocol; window.__r = r; window.__done = true; };\n' +
    'w.onerror = function (e) { window.__r = { error: "worker: " + (e.message || "error") }; window.__done = true; };\n' +
    '</script></body></html>';
}

function stats(a) {
  a = a.filter(function (x) { return typeof x === 'number'; });
  var n = a.length; if (!n) return null;
  var m = a.reduce(function (s, x) { return s + x; }, 0) / n;
  var sd = Math.sqrt(a.reduce(function (s, x) { return s + (x - m) * (x - m); }, 0) / Math.max(1, n - 1));
  return { n: n, mean: +m.toFixed(1), min: +Math.min.apply(null, a).toFixed(1), max: +Math.max.apply(null, a).toFixed(1), sd: +sd.toFixed(1) };
}

function check(v, expected) {
  if (typeof v !== 'number' || v < 0) return 'failed (' + v + ')';
  return Math.abs(v - expected) <= Math.abs(expected) * 1e-4 ? 'ok' : 'wrong value (' + v + ', expected ' + expected + ')';
}

(async function () {
  var out = { date: new Date().toISOString(), files: {}, node: null, runs: [] };
  ['smlib.wasm', 'smlib.mjs', 'smlib_single.js'].forEach(function (f) { out.files[f] = fs.statSync(path.join(OUT, f)).size; });

  // Node, the ES-module build: correctness only.
  var mod = await import(path.join(OUT, 'smlib.mjs'));
  var m = await mod.default();
  m._e02_init();
  out.node = {};
  CASES.forEach(function (c) { var v = m['_e02_' + c[0]](); out.node[c[0]] = { value: v, check: check(v, c[1]) }; });

  var kernelJs = fs.readFileSync(path.join(OUT, 'smlib_single.js'), 'utf8');
  var file = path.join(OUT, 'e02_page.html');
  fs.writeFileSync(file, pageHtml(kernelJs));
  out.files['e02_page.html'] = fs.statSync(file).size;

  for (var k = 0; k < 5; k++) {
    var browser = await pw.chromium.launch();
    var page = await browser.newPage();
    var tl = Date.now();
    await page.goto('file://' + file);
    await page.waitForFunction(function () { return window.__done === true; }, null, { timeout: 300000 });
    var r = await page.evaluate(function () { return window.__r; });
    r.loadToDoneMs = Date.now() - tl;
    r.browserVersion = browser.version();
    out.runs.push(r);
    await browser.close();
  }
  out.summary = {
    instantiateMs: stats(out.runs.map(function (r) { return r.instantiateMs; })),
    loadToDoneMs: stats(out.runs.map(function (r) { return r.loadToDoneMs; })),
    heapBytes: stats(out.runs.map(function (r) { return r.heapBytes; })),
    cases: {}
  };
  CASES.forEach(function (c) {
    out.summary.cases[c[0]] = {
      check: out.runs.map(function (r) { return r.cases ? check(r.cases[c[0]].first, c[1]) : r.error; }),
      firstMs: stats(out.runs.map(function (r) { return r.cases && r.cases[c[0]].firstMs; })),
      secondMs: stats(out.runs.map(function (r) { return r.cases && r.cases[c[0]].secondMs; }))
    };
  });
  fs.writeFileSync(path.join(__dirname, 'e02_results.json'), JSON.stringify(out, null, 1));
  console.log(JSON.stringify({ files: out.files, node: out.node, summary: out.summary }, null, 1));
})().catch(function (e) { console.error(e); process.exit(1); });
