// e01_file_origin_wasm.js -- the B-rep kernel research (reference/research-usd-brep.md), 2026-10-31.
// Question: can the one-file build, opened from file://, carry a WebAssembly kernel the size of a
// C++ CAD kernel, run it in a Worker (SMLib's rule: one kernel per worker, restart on corruption),
// and what does it cost at load?
// Hypotheses tested:
//   H3a  fetch() of a sibling .wasm from a file:// page fails in Chromium.
//   H3b  a module embedded as base64 text in the page compiles from file://.
//   H3c  a Worker made from a Blob URL starts from a file:// page and can compile the module.
//   H3d  SharedArrayBuffer (so Emscripten pthreads) is NOT available on file:// (not crossOriginIsolated).
//   H3e  base64 decode + compile of a 5 MB module takes under 1 s on this machine.
// Note: Chromium compiles WebAssembly lazily (each function at its first call), so compile time
// here is mostly validation; the cost of real calls is not measured by a synthetic module.
// Method: the module is SYNTHETIC, written by this script (no upstream code): N functions of
// integer arithmetic, sized to 1, 5 and 10 MB of code. Real compiled C++ differs in its mix of
// instructions; the sizes, not the timings, carry over (a threat said in the note). 5 runs each,
// fresh browser each run. Playwright 1.63.0 drives chromium-1243 in /opt/pw-browsers.
// Run: node e01_file_origin_wasm.js   (writes results.json beside a scratch dir outside the repo)
'use strict';
var pw = require('playwright');
var fs = require('fs');
var path = require('path');
var os = require('os');

var SCRATCH = process.env.KW_EXP_SCRATCH || path.join(os.tmpdir(), 'kw-exp');
fs.mkdirSync(SCRATCH, { recursive: true });

function uleb(n) { var o = []; do { var b = n & 0x7f; n >>>= 7; if (n) b |= 0x80; o.push(b); } while (n); return o; }
function section(id, bytes) { return [id].concat(uleb(bytes.length), bytes); }

// A valid module: one type (i32)->i32, N functions, each body = local.get 0, then R times
// (i32.const k; i32.add; i32.const 3; i32.xor), end. Exports function 0 as "f".
function makeWasm(targetBytes) {
  var R = 200;
  var body = [0x00, 0x20, 0x00]; // 0 locals, local.get 0
  for (var r = 0; r < R; r++) body.push(0x41, (r % 63) + 1, 0x6a, 0x41, 0x03, 0x73);
  body.push(0x0b);
  var fbody = uleb(body.length).concat(body);
  var N = Math.max(1, Math.floor(targetBytes / fbody.length));
  var type = section(1, [0x01, 0x60, 0x01, 0x7f, 0x01, 0x7f]);
  var funcs = uleb(N); for (var i = 0; i < N; i++) funcs.push(0x00);
  var func = section(3, funcs);
  var exp = section(7, [0x01, 0x01, 0x66, 0x00, 0x00]);
  var codeHead = uleb(N);
  var codeLen = codeHead.length + fbody.length * N;
  var head = [0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00].concat(type, func, exp, [0x0a], uleb(codeLen), codeHead);
  var buf = Buffer.alloc(head.length + fbody.length * N);
  Buffer.from(head).copy(buf, 0);
  var fb = Buffer.from(fbody);
  for (var j = 0; j < N; j++) fb.copy(buf, head.length + j * fb.length);
  return { buf: buf, functions: N };
}

// The page: ES5, as the app is. Everything it measures goes into window.__r.
function pageHtml(b64) {
  return '<!doctype html><html><head><meta charset="utf-8"><title>kw</title></head><body>kw' +
    '<script id="wasm64" type="application/octet-stream">' + b64 + '</script>' +
    '<script>\n' +
    'var r = window.__r = { origin: location.protocol, crossOriginIsolated: !!window.crossOriginIsolated,\n' +
    '  sab: typeof SharedArrayBuffer, wasm: typeof WebAssembly };\n' +
    'function now(){ return performance.now(); }\n' +
    'function decode(s){ var bin = atob(s), n = bin.length, u = new Uint8Array(n); for (var i = 0; i < n; i++) u[i] = bin.charCodeAt(i); return u; }\n' +
    'r.fetchSibling = "pending";\n' +
    'try { fetch("sibling.wasm").then(function(x){ r.fetchSibling = "ok " + x.status; }, function(e){ r.fetchSibling = "failed: " + e.name + ": " + e.message; }); } catch (e) { r.fetchSibling = "threw: " + e.message; }\n' +
    'var t0 = now(); var bytes = decode(document.getElementById("wasm64").textContent); var t1 = now();\n' +
    'r.decodeMs = t1 - t0; r.bytes = bytes.length;\n' +
    'r.mainCompile = "pending";\n' +
    'WebAssembly.compile(bytes).then(function(m){ var t2 = now(); r.mainCompileMs = t2 - t1;\n' +
    '  return WebAssembly.instantiate(m, {}); }).then(function(inst){ r.mainCompile = "ok"; r.mainResult = inst.exports.f(1); }, function(e){ r.mainCompile = "failed: " + e.message; });\n' +
    'var wsrc = "onmessage=function(e){var t=performance.now();WebAssembly.compile(e.data).then(function(m){return WebAssembly.instantiate(m,{}).then(function(i){postMessage({ok:true,ms:performance.now()-t,res:i.exports.f(1),sab:typeof SharedArrayBuffer});});},function(er){postMessage({ok:false,err:String(er)});});};";\n' +
    'r.worker = "pending";\n' +
    'try { var url = URL.createObjectURL(new Blob([wsrc], {type: "text/javascript"})); var w = new Worker(url);\n' +
    '  w.onmessage = function(e){ r.worker = e.data.ok ? "ok" : ("failed: " + e.data.err); r.workerCompileMs = e.data.ms; r.workerResult = e.data.res; r.workerSab = e.data.sab; };\n' +
    '  w.onerror = function(e){ r.worker = "error: " + (e.message || "worker error"); };\n' +
    '  var copy = bytes.slice(0); w.postMessage(copy.buffer, [copy.buffer]);\n' +
    '} catch (e) { r.worker = "threw: " + e.name + ": " + e.message; }\n' +
    'try { var mem = new WebAssembly.Memory({ initial: 1, maximum: 65536 }); var grown = 0;\n' +
    '  [4096, 8192, 16384, 32767, 65535].forEach(function(p){ try { mem.grow(p - mem.buffer.byteLength / 65536); grown = p; } catch (e) {} });\n' +
    '  r.memoryMaxGrownKiB = grown * 64; } catch (e) { r.memoryMaxGrownKiB = "threw: " + e.message; }\n' +
    'r.exnref = (function(){ try { return typeof WebAssembly.Exception === "function" && typeof WebAssembly.Tag === "function"; } catch (e) { return false; } })();\n' +
    '</script></body></html>';
}

function stats(a) {
  var n = a.length, m = a.reduce(function (s, x) { return s + x; }, 0) / n;
  var sd = Math.sqrt(a.reduce(function (s, x) { return s + (x - m) * (x - m); }, 0) / Math.max(1, n - 1));
  return { n: n, mean: +m.toFixed(1), min: +Math.min.apply(null, a).toFixed(1), max: +Math.max.apply(null, a).toFixed(1), sd: +sd.toFixed(1) };
}

(async function () {
  var sizesMB = [1, 5, 10], RUNS = 5, out = { date: new Date().toISOString(), runs: RUNS, sizes: [] };
  for (var s = 0; s < sizesMB.length; s++) {
    var w = makeWasm(sizesMB[s] * 1024 * 1024);
    var dir = path.join(SCRATCH, 'size' + sizesMB[s]); fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'sibling.wasm'), w.buf);
    var b64 = w.buf.toString('base64');
    var file = path.join(dir, 'page.html'); fs.writeFileSync(file, pageHtml(b64));
    var row = { targetMB: sizesMB[s], wasmBytes: w.buf.length, functions: w.functions, base64Bytes: b64.length,
      gzipWasmBytes: require('zlib').gzipSync(w.buf).length, gzipBase64Bytes: require('zlib').gzipSync(Buffer.from(b64)).length, runs: [] };
    for (var k = 0; k < RUNS; k++) {
      var browser = await pw.chromium.launch();
      var page = await browser.newPage();
      var tl = Date.now();
      await page.goto('file://' + file);
      await page.waitForFunction(function () { var r = window.__r; return r && r.mainCompile !== 'pending' && r.worker !== 'pending' && r.fetchSibling !== 'pending'; }, null, { timeout: 120000 });
      var r = await page.evaluate(function () { return window.__r; });
      r.loadToReadyMs = Date.now() - tl;
      r.browserVersion = browser.version();
      row.runs.push(r);
      await browser.close();
    }
    row.decodeMs = stats(row.runs.map(function (x) { return x.decodeMs; }));
    row.mainCompileMs = stats(row.runs.map(function (x) { return x.mainCompileMs; }));
    row.workerCompileMs = stats(row.runs.map(function (x) { return x.workerCompileMs; }));
    row.loadToReadyMs = stats(row.runs.map(function (x) { return x.loadToReadyMs; }));
    out.sizes.push(row);
    console.log(JSON.stringify({ size: sizesMB[s], wasmBytes: row.wasmBytes, b64: row.base64Bytes, gzW: row.gzipWasmBytes, decode: row.decodeMs, compile: row.mainCompileMs, worker: row.workerCompileMs, ready: row.loadToReadyMs, first: row.runs[0] }));
  }
  fs.writeFileSync(path.join(__dirname, 'e01_results.json'), JSON.stringify(out, null, 1));
})().catch(function (e) { console.error(e); process.exit(1); });
