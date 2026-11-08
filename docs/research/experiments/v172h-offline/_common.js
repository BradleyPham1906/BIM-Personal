// _common.js -- helpers shared by the V172h experiment drivers (2026-11-07). Not an experiment itself.
//   SCRATCH: where builds and raw JSON go (outside the repository); override with V172H_SCRATCH.
//   buildA(): build what Pages serves into SCRATCH/siteA (once; reused when present, V172H_REBUILD=1 forces it).
//   buildB(): copy siteA to siteB and make it a different build: one comment appended to app/engine.js, its
//             ?v= hash in index.html recomputed the way tools/build_app.py names it (first 12 hex of SHA-256).
//   serve(opts): the _server.js stand-in for Pages, started, with the experiment helpers at /BIM-Personal/__exp/.
//   page(body): a minimal HTML page that loads exp.js and then runs `body`.
//   appSw(build, opts): the experiment worker for a build (sw-app.template.js), served at /BIM-Personal/sw.js.
//   save(name, obj): write raw results to SCRATCH/results/<name>.json and print a one-line summary.
'use strict';
var fs = require('fs');
var path = require('path');
var crypto = require('crypto');
var cp = require('child_process');
var srv = require('./_server.js');

var REPO = path.resolve(__dirname, '../../../..');
var SCRATCH = process.env.V172H_SCRATCH ||
  '/tmp/claude-0/-home-user-BIM-Personal/7ef9ec21-7e6e-54c5-bca1-4bc8d65ed6b9/scratchpad/v172h-exp';

function buildA() {
  var d = path.join(SCRATCH, 'siteA');
  if (process.env.V172H_REBUILD || !fs.existsSync(path.join(d, 'index.html'))) {
    cp.execFileSync('python3', ['tools/build_site.py', d], { cwd: REPO, stdio: 'inherit' });
  }
  return d;
}

function buildB() {
  var a = buildA(), b = path.join(SCRATCH, 'siteB');
  if (!fs.existsSync(path.join(b, 'index.html'))) {
    cp.execFileSync('cp', ['-a', a, b]);
    var eng = path.join(b, 'app', 'engine.js');
    fs.appendFileSync(eng, '\n/* V172h experiment: build B */\n');
    var h = crypto.createHash('sha256').update(fs.readFileSync(eng)).digest('hex').slice(0, 12);
    var ix = path.join(b, 'index.html');
    fs.writeFileSync(ix, fs.readFileSync(ix, 'utf8').replace(/app\/engine\.js\?v=[0-9a-f]{12}/g, 'app/engine.js?v=' + h));
  }
  return b;
}

function buildId(dir) {
  return crypto.createHash('sha256').update(srv.appUrls(dir).join('|')).digest('hex').slice(0, 8);
}

function serve(opts) {
  var S = srv.create(opts || {});
  S.override('/BIM-Personal/__exp/exp.js', { body: fs.readFileSync(path.join(__dirname, 'exp.js')) });
  return S.start();
}

function page(body, head) {
  return '<!doctype html><html><head><meta charset="utf-8">' + (head || '') +
    '<script src="/BIM-Personal/__exp/exp.js"></script></head><body><p>experiment page</p><script>' + (body || '') +
    '</script></body></html>';
}

function appSw(dir, opts) {
  opts = opts || {};
  return srv.fromTemplate('sw-app.template.js', {
    BUILD: opts.build || buildId(dir), PRECACHE: ['./'].concat(srv.appUrls(dir)), SKIP: !!opts.skip, CLAIM: !!opts.claim
  });
}

function probeSw(version, fetchHandler) {
  return srv.fromTemplate('sw-probe.template.js', { VERSION: version, FETCH: fetchHandler !== false });
}

function save(name, obj) {
  var d = path.join(SCRATCH, 'results');
  fs.mkdirSync(d, { recursive: true });
  var f = path.join(d, name + '.json');
  fs.writeFileSync(f, JSON.stringify(obj, null, 1));
  console.log('saved ' + f);
}

function stats(a) {
  var s = a.slice().sort(function (x, y) { return x - y; }), n = s.length, m = 0;
  s.forEach(function (x) { m += x; });
  return { n: n, min: s[0], median: n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2, mean: Math.round(m / n * 10) / 10, max: s[n - 1], raw: a };
}

function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

// Waits until the real app's store has opened (V172d/f's hook), as the e2e suites do.
async function appReady(p, ms) {
  var t0 = Date.now();
  while (Date.now() - t0 < (ms || 20000)) {
    var st = await p.evaluate(function () { return window.__a3dStore ? window.__a3dStore().mode : null; }).catch(function () { return null; });
    if (st === 'idb' || st === 'legacy' || st === 'refused') return { mode: st, ms: Date.now() - t0 };
    await sleep(50);
  }
  return { mode: null, ms: Date.now() - t0 };
}

module.exports = { REPO: REPO, SCRATCH: SCRATCH, buildA: buildA, buildB: buildB, buildId: buildId, serve: serve, page: page,
  appSw: appSw, probeSw: probeSw, save: save, stats: stats, sleep: sleep, appReady: appReady, srv: srv };
