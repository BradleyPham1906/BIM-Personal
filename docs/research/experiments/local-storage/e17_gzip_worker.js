// e17_gzip_worker.js -- V172g, hypotheses H33 to H36 (2026-11-07).
// The owner's open choice in D4: compress on the main thread and accept the stall, or in a worker.
// (a) The longest main-thread stall (a MessageChannel ticker, as e10) while gzip runs
//     1. on the main thread (TextEncoder + CompressionStream, as e10), and
//     2. in a Worker made from a Blob URL (the one-file build has no separate file to load):
//        the JSON string posted to it, the bytes posted back transferred;
//     and the total time to bytes in hand. Inputs: e10's 'varied' model (~4 MB) and the same
//     model four times over (~16 MB). Over http and from file://.
// (b) The first two bytes of every gzip output (1F 8B).
// (c) What DecompressionStream does with a truncated file (the last 10 bytes cut), one byte
//     changed in the middle, trailing bytes after the member, and two members back to back.
// 5 runs each, each in a fresh context. Run: node e17_gzip_worker.js
'use strict';
var pw = require('playwright');
var fs = require('fs');
var path = require('path');
var L = require('./_lib');

function measure(times) {
  function varied(n) {
    var els = [], types = ['wall', 'slab', 'column', 'beam', 'door', 'window', 'roof'], i, j, seed = 7;
    function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
    for (i = 0; i < 4600 * n; i++) {
      var v = []; for (j = 0; j < 96; j++) v.push(Math.round(rnd() * 100000) / 1000);
      els.push({ id: 'el-' + i, type: types[i % types.length], layer: 'L' + (i % 12), level: i % 5,
        props: { material: 'concrete-c30', fireRating: 'REI ' + (60 + i % 3 * 30), thickness: 0.2 + (i % 4) * 0.05, name: 'Element ' + i, tags: ['a', 'b'] },
        verts: v, faces: [0, 1, 2, 2, 3, 0, 4, 5, 6, 6, 7, 4] });
    }
    return { version: 170, units: 'm', site: { lat: 40.0, lon: -75.1 }, elements: els };
  }
  function ticker() {
    var ch = new MessageChannel(), last = performance.now(), maxGap = 0, on = true;
    ch.port1.onmessage = function () { var t = performance.now(); if (t - last > maxGap) maxGap = t - last; last = t; if (on) ch.port2.postMessage(0); };
    ch.port2.postMessage(0);
    return { stop: function () { on = false; return maxGap; } };
  }
  function gz(text) {
    return new Response(new Blob([new TextEncoder().encode(text)]).stream().pipeThrough(new CompressionStream('gzip')))
      .arrayBuffer().then(function (b) { return new Uint8Array(b); });
  }
  var WSRC = 'self.onmessage=function(e){var t0=performance.now();' +
    'new Response(new Blob([new TextEncoder().encode(e.data)]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer()' +
    '.then(function(b){self.postMessage({buf:b,ms:performance.now()-t0},[b]);},function(x){self.postMessage({error:String(x)});});};';
  var worker;
  try { worker = new Worker(URL.createObjectURL(new Blob([WSRC], { type: 'text/javascript' }))); } catch (e) { worker = null; }
  function inWorker(text) {
    return new Promise(function (res) {
      worker.onmessage = function (e) { res(e.data); };
      worker.onerror = function (e) { res({ error: 'worker error ' + (e.message || '') }); };
      var t0 = performance.now(); worker.postMessage(text); res.postMs = performance.now() - t0; inWorker.postMs = res.postMs;
    });
  }
  function unz(bytes) {
    return new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text()
      .then(function (t) { return { ok: true, len: t.length, text: t }; }, function (e) { return { ok: false, error: e.name + ': ' + e.message }; });
  }
  var out = { origin: location.protocol, workerMade: !!worker, sizes: {} };
  var chain = Promise.resolve();
  times.forEach(function (n) {
    var text = JSON.stringify(varied(n)), r = { chars: text.length };
    out.sizes[n] = r;
    chain = chain.then(function () {
      var tk = ticker(), t0 = performance.now();
      return gz(text).then(function (z) { r.mainMs = performance.now() - t0; r.mainGapMs = tk.stop(); r.bytes = z.length; r.magic = [z[0], z[1]]; r.ratio = z.length / text.length; });
    }).then(function () {
      if (!worker) return null;
      return new Promise(function (r2) { setTimeout(r2, 50); }).then(function () {
        var tk = ticker(), t0 = performance.now();
        return inWorker(text).then(function (d) {
          r.workerTotalMs = performance.now() - t0; r.workerGapMs = tk.stop(); r.workerPostMs = inWorker.postMs;
          if (d.error) { r.workerError = d.error; return; }
          r.workerInsideMs = d.ms; var z = new Uint8Array(d.buf); r.workerBytes = z.length; r.workerMagic = [z[0], z[1]];
          return unz(z).then(function (u) { r.workerRoundTrip = u.ok && u.text === text; });
        });
      });
    });
  });
  // (c) damaged files, on the small model
  chain = chain.then(function () {
    var text = JSON.stringify({ app: 'acad3d-project', formatVersion: 2, data: varied(0.05) });
    return gz(text).then(function (z) {
      var cut = z.slice(0, z.length - 10);
      var flip = z.slice(); flip[Math.floor(z.length / 2)] ^= 0xff;
      var trail = new Uint8Array(z.length + 4); trail.set(z); trail.set([1, 2, 3, 4], z.length);
      var two = new Uint8Array(z.length * 2); two.set(z); two.set(z, z.length);
      return Promise.all([unz(cut), unz(flip), unz(trail), unz(two)]).then(function (a) {
        function s(x) { return x.ok ? { ok: true, len: x.len, equalsOriginal: x.text === text, isDouble: x.text === text + text } : x; }
        out.damaged = { inputChars: text.length, truncated: s(a[0]), oneByteFlipped: s(a[1]), trailingBytes: s(a[2]), twoMembers: s(a[3]) };
      });
    });
  });
  return chain.then(function () { if (worker) worker.terminate(); return out; });
}

(async function () {
  var srv = await L.startServer(0);
  var dir = L.tmpDir('e17-');
  var blank = path.join(dir, 'p.html');
  fs.writeFileSync(blank, '<!doctype html><title>e17</title>');
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), runs: { http: [], file: [] } };
  var targets = { http: srv.origin + '/', file: 'file://' + blank };
  for (var k in targets) {
    for (var run = 0; run < 5; run++) {
      var ctx = await browser.newContext(); var page = await ctx.newPage();
      await page.goto(targets[k]);
      out.runs[k].push(await page.evaluate(measure, [1, 4]));
      await ctx.close();
    }
  }
  out.summary = {};
  ['http', 'file'].forEach(function (k) {
    [1, 4].forEach(function (n) {
      var rs = out.runs[k].map(function (r) { return r.sizes[n]; });
      var s = {
        chars: rs[0].chars, bytes: rs[0].bytes, ratio: Math.round(rs[0].ratio * 1000) / 1000, magic: rs[0].magic, workerMagic: rs[0].workerMagic,
        workerMade: out.runs[k].every(function (r) { return r.workerMade; }),
        roundTrips: rs.filter(function (r) { return r.workerRoundTrip; }).length,
        mainMs: L.stats(rs.map(function (r) { return r.mainMs; })), mainGapMs: L.stats(rs.map(function (r) { return r.mainGapMs; })),
        workerTotalMs: L.stats(rs.map(function (r) { return r.workerTotalMs; })), workerGapMs: L.stats(rs.map(function (r) { return r.workerGapMs; })),
        workerPostMs: L.stats(rs.map(function (r) { return r.workerPostMs; })), workerInsideMs: L.stats(rs.map(function (r) { return r.workerInsideMs; }))
      };
      out.summary[k + '/' + n] = s;
      console.log(k + '/x' + n, 'chars', s.chars, 'bytes', s.bytes, 'ratio', s.ratio, 'magic', s.magic, s.workerMagic, 'worker', s.workerMade, 'roundtrips', s.roundTrips + '/5',
        '\n  main ms', JSON.stringify(s.mainMs.raw), 'gap', JSON.stringify(s.mainGapMs.raw),
        '\n  worker total', JSON.stringify(s.workerTotalMs.raw), 'gap', JSON.stringify(s.workerGapMs.raw), 'post', JSON.stringify(s.workerPostMs.raw), 'inside', JSON.stringify(s.workerInsideMs.raw));
    });
  });
  console.log('damaged (http run 0):', JSON.stringify(out.runs.http[0].damaged));
  console.log('damaged identical in all runs:', ['http', 'file'].every(function (k) { return out.runs[k].every(function (r) { return JSON.stringify(r.damaged) === JSON.stringify(out.runs.http[0].damaged); }); }));
  L.save('e17', out);
  await browser.close(); srv.server.close(); L.rm(dir);
})().catch(function (e) { console.error(e); process.exit(1); });
