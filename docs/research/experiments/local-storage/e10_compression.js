// e10_compression.js -- Hypothesis 10 (2026-10-31).
// Tests: CompressionStream exists with 'gzip' (and 'deflate', 'deflate-raw'); the ratio it
// reaches on a realistic CAD-like JSON of ~4 MB, and its time; DecompressionStream restores
// the exact text. Two inputs, so the result is not flattered by one kind of data:
//  'repetitive': 6,000 elements whose vertex arrays come from 40 shared shapes, offset to a grid
//      (many repeated numeric arrays, like copied walls, windows and columns);
//  'varied': the e07 model, 4,600 elements each with 96 pseudo-random coordinates (3 decimals),
//      the worst realistic case (little repetition in the numbers).
// Times: compress = TextEncoder + stream to a Uint8Array; decompress = stream + TextDecoder.
// Ratio = compressed bytes / UTF-8 bytes. Also maxGapMs: the longest stall seen by a
// MessageChannel ticker during compression (does the stream work block the main thread?).
// 5 runs, each in a fresh context.
'use strict';
var pw = require('playwright');
var L = require('./_lib');

function measure() {
  function repetitive() {
    var shapes = [], s, j, els = [], i, seed = 11;
    function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
    for (s = 0; s < 40; s++) { var v = []; for (j = 0; j < 72; j++) v.push(Math.round(rnd() * 5000) / 1000); shapes.push(v); }
    for (i = 0; i < 6000; i++) {
      var base = shapes[i % 40], ox = (i % 50) * 6, oy = Math.floor(i / 50) * 6, vv = [];
      for (j = 0; j < base.length; j += 3) vv.push(Math.round((base[j] + ox) * 1000) / 1000, Math.round((base[j + 1] + oy) * 1000) / 1000, base[j + 2]);
      els.push({ id: 'el-' + i, type: ['wall', 'window', 'column', 'slab'][i % 4], layer: 'L' + (i % 8), shape: i % 40,
        props: { material: 'concrete-c30', fireRating: 'REI 60', name: 'Element ' + i }, verts: vv, faces: [0, 1, 2, 2, 3, 0, 4, 5, 6, 6, 7, 4] });
    }
    return { version: 170, units: 'm', elements: els };
  }
  function varied() {
    var els = [], types = ['wall', 'slab', 'column', 'beam', 'door', 'window', 'roof'], i, j, seed = 7;
    function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
    for (i = 0; i < 4600; i++) {
      var v = []; for (j = 0; j < 96; j++) v.push(Math.round(rnd() * 100000) / 1000);
      els.push({ id: 'el-' + i, type: types[i % types.length], layer: 'L' + (i % 12), level: i % 5,
        props: { material: 'concrete-c30', fireRating: 'REI ' + (60 + i % 3 * 30), thickness: 0.2 + (i % 4) * 0.05, name: 'Element ' + i, tags: ['a', 'b'] },
        verts: v, faces: [0, 1, 2, 2, 3, 0, 4, 5, 6, 6, 7, 4] });
    }
    return { version: 170, units: 'm', site: { lat: 40.0, lon: -75.1 }, elements: els };
  }
  function streamAll(readable) {
    return new Response(readable).arrayBuffer().then(function (b) { return new Uint8Array(b); });
  }
  function ticker() {
    var ch = new MessageChannel(), last = performance.now(), maxGap = 0, on = true;
    ch.port1.onmessage = function () { var t = performance.now(); if (t - last > maxGap) maxGap = t - last; last = t; if (on) ch.port2.postMessage(0); };
    ch.port2.postMessage(0);
    return { stop: function () { on = false; return maxGap; } };
  }
  function one(text, fmt) {
    var tk = ticker();
    var t0 = performance.now(), bytes = new TextEncoder().encode(text);
    var cs = new Blob([bytes]).stream().pipeThrough(new CompressionStream(fmt));
    return streamAll(cs).then(function (z) {
      var tc = performance.now() - t0, gap = tk.stop(); t0 = performance.now();
      return streamAll(new Blob([z]).stream().pipeThrough(new DecompressionStream(fmt))).then(function (u) {
        var back = new TextDecoder().decode(u), td = performance.now() - t0;
        return { fmt: fmt, inBytes: bytes.length, outBytes: z.length, ratio: z.length / bytes.length, compressMs: tc, maxGapMs: gap, decompressMs: td, roundTripEqual: back === text };
      });
    });
  }
  var out = { has: { CompressionStream: typeof CompressionStream, DecompressionStream: typeof DecompressionStream } };
  var fmts = ['gzip', 'deflate', 'deflate-raw'];
  out.formatsAccepted = {};
  fmts.concat(['brotli', 'zstd']).forEach(function (f) { try { new CompressionStream(f); out.formatsAccepted[f] = true; } catch (e) { out.formatsAccepted[f] = e.name; } });
  var inputs = { repetitive: JSON.stringify(repetitive()), varied: JSON.stringify(varied()) };
  out.results = [];
  var chain = Promise.resolve();
  Object.keys(inputs).forEach(function (k) {
    fmts.forEach(function (f) {
      chain = chain.then(function () { return one(inputs[k], f); }).then(function (r) { r.input = k; out.results.push(r); });
    });
  });
  return chain.then(function () { return out; });
}

(async function () {
  var srv = await L.startServer(0);
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), runs: [] };
  for (var run = 0; run < 5; run++) {
    var ctx = await browser.newContext();
    var page = await ctx.newPage();
    await page.goto(srv.origin + '/');
    var r = await page.evaluate(measure); r.run = run;
    out.runs.push(r);
    if (run === 0) console.log(JSON.stringify({ has: r.has, formatsAccepted: r.formatsAccepted }));
    await ctx.close();
  }
  out.summary = {};
  out.runs[0].results.forEach(function (x, idx) {
    var key = x.input + '/' + x.fmt;
    out.summary[key] = {
      inBytes: x.inBytes, outBytes: L.stats(out.runs.map(function (r) { return r.results[idx].outBytes; })),
      ratio: L.stats(out.runs.map(function (r) { return r.results[idx].ratio; })),
      compressMs: L.stats(out.runs.map(function (r) { return r.results[idx].compressMs; })),
      decompressMs: L.stats(out.runs.map(function (r) { return r.results[idx].decompressMs; })),
      maxGapMs: L.stats(out.runs.map(function (r) { return r.results[idx].maxGapMs; })),
      allEqual: out.runs.every(function (r) { return r.results[idx].roundTripEqual; })
    };
    var s = out.summary[key];
    console.log(key, 'in', s.inBytes, 'out', JSON.stringify(s.outBytes.raw), 'ratio', s.ratio.mean, 'compressMs', JSON.stringify(s.compressMs.raw), 'mean', s.compressMs.mean, 'decompMs', JSON.stringify(s.decompressMs.raw), 'mean', s.decompressMs.mean, 'maxGapMs', JSON.stringify(s.maxGapMs.raw), 'equal', s.allEqual);
  });
  L.save('e10', out);
  await browser.close(); srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
