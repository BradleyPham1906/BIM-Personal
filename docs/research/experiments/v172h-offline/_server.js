// _server.js -- the V172h experiments' local stand-in for GitHub Pages (2026-11-07). Not an experiment itself.
// Serves a site built by `python3 tools/build_site.py <dir>` under the subpath /BIM-Personal/ on
// http://localhost:<port> (localhost is a secure context, so service workers run), the way Pages does:
//   - `cache-control: max-age=600` and a strong ETag (SHA-1 of the bytes) on every file, 304 on If-None-Match;
//   - a directory without its slash is redirected (301) to the slash; a directory answers its index.html;
//   - JavaScript as `application/javascript; charset=utf-8` (Pages' type), wasm as `application/wasm`;
//   - anything outside /BIM-Personal/ and /Other/ is 404.
// What it adds for the experiments:
//   - setBuild(dir): swap the served build (an update test deploys build B over build A);
//   - override(path, {body, type, headers}): serve generated content at a path (sw.js, test pages, manifest);
//   - /Other/<file>: a second "Pages project" of the same account (same origin), from the `other` folder;
//   - hits: every request counted by its path with query, with the request headers of sw.js requests kept;
//   - stop() / restart(): close the listener and destroy open sockets (the server is gone: connection
//     refused), then listen again on the same port, so the origin and its storage stay the same.
// ES5 style like the page code; Node only.
'use strict';
var http = require('http');
var fs = require('fs');
var path = require('path');
var crypto = require('crypto');

var TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'application/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.webmanifest': 'application/manifest+json', '.wasm': 'application/wasm',
  '.whl': 'application/octet-stream', '.zip': 'application/zip', '.png': 'image/png', '.txt': 'text/plain; charset=utf-8'
};
function typeOf(p) { var t = TYPES[path.extname(p).toLowerCase()]; return t || 'application/octet-stream'; }

var etagMemo = {};
function etagOf(file, st) {
  var k = file + '|' + st.size + '|' + st.mtimeMs;
  if (!etagMemo[k]) etagMemo[k] = '"' + crypto.createHash('sha1').update(fs.readFileSync(file)).digest('hex') + '"';
  return etagMemo[k];
}

function create(opts) {
  opts = opts || {};
  var S = {
    build: opts.build, other: opts.other || null, port: opts.port || 0, overrides: {}, hits: {}, swHeaders: [],
    log: [], server: null, sockets: [], origin: null, bytesOut: 0
  };
  S.setBuild = function (dir) { S.build = dir; };
  S.override = function (p, o) { if (o === null) delete S.overrides[p]; else S.overrides[p] = o; };
  S.resetHits = function () { S.hits = {}; S.swHeaders = []; S.log = []; S.bytesOut = 0; };
  S.count = function (re) { var n = 0, k; for (k in S.hits) if (re.test(k)) n += S.hits[k]; return n; };

  function send(req, res, status, headers, body) {
    S.bytesOut += body ? body.length : 0;
    res.writeHead(status, headers);
    res.end(req.method === 'HEAD' ? undefined : body);
  }
  function handler(req, res) {
    var url = req.url, p = url.split('?')[0];
    S.hits[url] = (S.hits[url] || 0) + 1;
    S.log.push({ t: Date.now(), url: url, sw: req.headers['service-worker'] || null });
    if (/\/sw[^\/]*\.js$/.test(p)) S.swHeaders.push({ url: url, t: Date.now(), headers: req.headers });
    var o = S.overrides[p];
    if (o) {
      var b = Buffer.isBuffer(o.body) ? o.body : Buffer.from(String(o.body));
      var et = '"' + crypto.createHash('sha1').update(b).digest('hex') + '"';
      var h = { 'content-type': o.type || typeOf(p), 'cache-control': o.cacheControl || 'max-age=600', etag: et };
      var k; for (k in (o.headers || {})) h[k] = o.headers[k];
      if (req.headers['if-none-match'] === et) return send(req, res, 304, h, null);
      return send(req, res, 200, h, b);
    }
    var root = null, rel = null;
    if (p.indexOf('/BIM-Personal/') === 0) { root = S.build; rel = p.slice('/BIM-Personal/'.length); }
    else if (p === '/BIM-Personal' || p === '/Other') { return send(req, res, 301, { location: p + '/' }, Buffer.from('')); }
    else if (p.indexOf('/Other/') === 0 && S.other) { root = S.other; rel = p.slice('/Other/'.length); }
    if (!root) return send(req, res, 404, { 'content-type': 'text/html; charset=utf-8' }, Buffer.from('<!doctype html><title>404</title>404'));
    var file = path.join(root, decodeURIComponent(rel));
    if (file.indexOf(path.resolve(root)) !== 0) return send(req, res, 404, {}, Buffer.from('404'));
    var st = null;
    try { st = fs.statSync(file); } catch (e) {}
    if (st && st.isDirectory()) {
      if (!/\/$/.test(p)) return send(req, res, 301, { location: p + '/' }, Buffer.from(''));
      file = path.join(file, 'index.html');
      try { st = fs.statSync(file); } catch (e) { st = null; }
    }
    if (!st) return send(req, res, 404, { 'content-type': 'text/html; charset=utf-8' }, Buffer.from('<!doctype html><title>404</title>404'));
    var etag = etagOf(file, st);
    var hd = { 'content-type': typeOf(file), 'cache-control': 'max-age=600', etag: etag, 'last-modified': new Date(st.mtimeMs).toUTCString() };
    if (req.headers['if-none-match'] === etag) return send(req, res, 304, hd, null);
    var body = fs.readFileSync(file);
    hd['content-length'] = body.length;
    send(req, res, 200, hd, body);
  }
  S.start = function () {
    return new Promise(function (resolve, reject) {
      S.server = http.createServer(handler);
      S.server.on('connection', function (s) { S.sockets.push(s); s.on('close', function () { S.sockets.splice(S.sockets.indexOf(s), 1); }); });
      S.server.on('error', reject);
      S.server.listen(S.port, '127.0.0.1', function () {
        S.port = S.server.address().port;
        S.origin = 'http://localhost:' + S.port;
        resolve(S);
      });
    });
  };
  S.stop = function () {
    return new Promise(function (resolve) {
      if (!S.server) return resolve();
      S.sockets.slice().forEach(function (s) { s.destroy(); });
      S.server.close(function () { S.server = null; resolve(); });
    });
  };
  S.restart = function () { return S.stop().then(S.start); };
  return S;
}

// The build's four `app/<name>?v=<hash>` addresses, as its index.html names them.
function appUrls(buildDir) {
  var html = fs.readFileSync(path.join(buildDir, 'index.html'), 'utf8');
  return html.match(/app\/[a-z0-9_-]+\.(?:js|css)\?v=[0-9a-f]{12}/g) || [];
}

// An experiment service worker made from a template in this folder: each /*@NAME*/null is replaced by JSON.
function fromTemplate(file, values) {
  var t = fs.readFileSync(path.join(__dirname, file), 'utf8');
  Object.keys(values).forEach(function (k) { t = t.split('/*@' + k + '*/null').join(JSON.stringify(values[k])); });
  return t;
}

module.exports = { create: create, appUrls: appUrls, fromTemplate: fromTemplate };

if (require.main === module) {
  // node _server.js <buildDir> [port]: serve a build by hand.
  create({ build: process.argv[2], port: +process.argv[3] || 8172 }).start().then(function (S) { console.log(S.origin + '/BIM-Personal/'); });
}
