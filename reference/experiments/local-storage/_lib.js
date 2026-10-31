// _lib.js -- shared helpers for the local-storage experiments (2026-10-31).
// Not an experiment itself. Gives each script: a tiny localhost http server, a scratch
// directory outside the repository (env LS_EXP_SCRATCH, default os.tmpdir()/ls-exp), a
// result writer, and summary statistics (mean, min, max, spread = max - min, sample sd).
// Run every script with plain Node: `node e01_localstorage_quota.js`. Playwright 1.63.0
// drives the Chromium build chromium-1243 in /opt/pw-browsers; nothing is installed.
'use strict';
var http = require('http');
var fs = require('fs');
var path = require('path');
var os = require('os');

var SCRATCH = process.env.LS_EXP_SCRATCH || path.join(os.tmpdir(), 'ls-exp');
fs.mkdirSync(SCRATCH, { recursive: true });

var BLANK = '<!doctype html><html><head><meta charset="utf-8"><title>exp</title></head><body>exp</body></html>';

// routes: { '/path': {type, body} or {file: absPath} }; anything else answers BLANK.
function startServer(port, routes) {
  routes = routes || {};
  return new Promise(function (resolve) {
    var srv = http.createServer(function (req, res) {
      var u = req.url.split('?')[0];
      var r = routes[u];
      if (r && r.file) {
        res.writeHead(200, { 'content-type': r.type || 'text/html; charset=utf-8' });
        fs.createReadStream(r.file).pipe(res);
        return;
      }
      if (r) { res.writeHead(200, { 'content-type': r.type || 'text/html; charset=utf-8' }); res.end(r.body); return; }
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(BLANK);
    });
    srv.listen(port || 0, '127.0.0.1', function () {
      resolve({ server: srv, port: srv.address().port, origin: 'http://localhost:' + srv.address().port });
    });
  });
}

function stats(arr) {
  var a = arr.filter(function (x) { return typeof x === 'number' && isFinite(x); });
  if (!a.length) return { n: 0 };
  var sum = a.reduce(function (s, x) { return s + x; }, 0);
  var mean = sum / a.length;
  var min = Math.min.apply(null, a), max = Math.max.apply(null, a);
  var sd = a.length > 1 ? Math.sqrt(a.reduce(function (s, x) { return s + (x - mean) * (x - mean); }, 0) / (a.length - 1)) : 0;
  function r(x) { return Math.round(x * 1000) / 1000; }
  return { n: a.length, raw: a.map(r), mean: r(mean), min: r(min), max: r(max), spread: r(max - min), sd: r(sd) };
}

function save(name, obj) {
  var p = path.join(SCRATCH, name + '.json');
  fs.writeFileSync(p, JSON.stringify(obj, null, 2));
  console.log('[saved] ' + p);
}

function tmpDir(prefix) { return fs.mkdtempSync(path.join(SCRATCH, prefix)); }
function rm(p) { try { fs.rmSync(p, { recursive: true, force: true }); } catch (e) {} }

module.exports = { startServer: startServer, stats: stats, save: save, tmpDir: tmpDir, rm: rm, SCRATCH: SCRATCH };
