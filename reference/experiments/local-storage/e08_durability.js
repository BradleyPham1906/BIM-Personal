// e08_durability.js -- Hypothesis 8 (2026-10-31).
// Tests: IDBDatabase.transaction(store, 'readwrite', {durability: 'relaxed'|'strict'|'default'})
// is accepted; what tx.durability reports for each, and with no options (the default value);
// what an unknown value ('bogus') does. Then two measurements on a persistent profile:
// (a) the time for 200 sequential small readwrite transactions (one 1 KB record each) under
// each durability hint, on disk; (b) a crash check: write 50 records (one transaction each,
// under 'relaxed' and under 'strict' into two stores), wait for the last oncomplete, then
// SIGKILL every process of that browser at once (no clean shutdown), relaunch on the same
// profile and count the records that survived. A process kill leaves the OS page cache intact,
// so (b) cannot show the difference between fsync and no fsync (that needs power loss); it
// shows only whether committed data survives an abrupt browser death. 3 runs.
'use strict';
var pw = require('playwright');
var cp = require('child_process');
var L = require('./_lib');

// openDb is installed in every page with addInitScript (page functions cannot see Node's scope)
function openDb() {
  return new Promise(function (res, rej) {
    var rq = indexedDB.open('e08', 1);
    rq.onupgradeneeded = function () { var d = rq.result; d.createObjectStore('relaxed'); d.createObjectStore('strict'); d.createObjectStore('default'); };
    rq.onsuccess = function () { res(rq.result); }; rq.onerror = function () { rej(rq.error); };
  });
}

function probeOptions() {
  return openDb().then(function (db) {
    var out = {};
    var cases = { none: undefined, relaxed: { durability: 'relaxed' }, strict: { durability: 'strict' }, def: { durability: 'default' }, bogus: { durability: 'bogus' } };
    Object.keys(cases).forEach(function (k) {
      try {
        var tx = cases[k] === undefined ? db.transaction('relaxed', 'readwrite') : db.transaction('relaxed', 'readwrite', cases[k]);
        out[k] = { accepted: true, durability: tx.durability };
        tx.abort();
      } catch (e) { out[k] = { accepted: false, error: e.name + ': ' + e.message }; }
    });
    try { var ro = db.transaction('relaxed', 'readonly'); out.readonlyNone = { durability: ro.durability }; } catch (e) { out.readonlyNone = { error: e.name }; }
    out.hasDurabilityProp = 'durability' in IDBTransaction.prototype;
    db.close();
    return out;
  });
}

function timeSequential() {
  var rec = new Uint8Array(1000);
  return openDb().then(function (db) {
    function runMode(mode) {
      var t0 = performance.now(), i = 0;
      return new Promise(function (res) {
        function next() {
          if (i === 200) { res(performance.now() - t0); return; }
          var tx = mode === 'none' ? db.transaction('default', 'readwrite') : db.transaction(mode === 'default' ? 'default' : mode, 'readwrite', { durability: mode });
          tx.objectStore(mode === 'none' ? 'default' : (mode === 'default' ? 'default' : mode)).put(rec, 'k' + i);
          tx.oncomplete = function () { i++; next(); };
        }
        next();
      });
    }
    var out = {};
    return runMode('relaxed').then(function (t) { out.relaxedMs = t; return runMode('strict'); })
      .then(function (t) { out.strictMs = t; return runMode('default'); })
      .then(function (t) { out.defaultMs = t; return runMode('none'); })
      .then(function (t) { out.noOptionMs = t; db.close(); return out; });
  });
}

function writeForCrash() {
  return openDb().then(function (db) {
    var p = [];
    ['relaxed', 'strict'].forEach(function (mode) {
      var st = db.transaction(mode, 'readwrite'); st.objectStore(mode).clear();
      for (var i = 0; i < 50; i++) {
        p.push(new Promise(function (res) {
          var tx = db.transaction(mode, 'readwrite', { durability: mode });
          tx.objectStore(mode).put({ i: i, pad: new Array(2001).join('p') }, 'r' + i);
          tx.oncomplete = res;
        }));
      }
    });
    return Promise.all(p).then(function () { return 'all-complete'; });
  });
}

function countAfter() {
  return openDb().then(function (db) {
    function count(s) { return new Promise(function (res) { var rq = db.transaction(s).objectStore(s).count(); rq.onsuccess = function () { res(rq.result); }; }); }
    return Promise.all([count('relaxed'), count('strict')]).then(function (c) { db.close(); return { relaxed: c[0], strict: c[1] }; });
  });
}

(async function () {
  var srv = await L.startServer(47319);
  var out = { runs: [] };
  for (var run = 0; run < 3; run++) {
    var dir = L.tmpDir('e08-');
    var ctx = await pw.chromium.launchPersistentContext(dir);
    await ctx.addInitScript({ content: 'window.openDb = ' + openDb.toString() });
    var r = { run: run, version: ctx.browser().version() };
    var page = ctx.pages()[0] || await ctx.newPage();
    await page.goto(srv.origin + '/');
    r.options = await page.evaluate(probeOptions);
    r.timing200 = await page.evaluate(timeSequential);
    r.crashWrite = await page.evaluate(writeForCrash);
    // abrupt death: SIGKILL every process whose command line names this profile
    var pids = cp.execSync('pgrep -f -- ' + JSON.stringify(dir) + ' || true').toString().trim().split(/\s+/).filter(Boolean);
    r.killedPids = pids.length;
    pids.forEach(function (pid) { try { process.kill(Number(pid), 'SIGKILL'); } catch (e) {} });
    await ctx.close().catch(function () {});
    var ctx2 = await pw.chromium.launchPersistentContext(dir);
    await ctx2.addInitScript({ content: 'window.openDb = ' + openDb.toString() });
    var page2 = ctx2.pages()[0] || await ctx2.newPage();
    await page2.goto(srv.origin + '/');
    r.survivedOf50 = await page2.evaluate(countAfter);
    await ctx2.close(); L.rm(dir);
    out.runs.push(r); console.log(JSON.stringify(r));
  }
  out.summary = {};
  ['relaxedMs', 'strictMs', 'defaultMs', 'noOptionMs'].forEach(function (k) { out.summary[k] = L.stats(out.runs.map(function (r) { return r.timing200[k]; })); });
  console.log(JSON.stringify(out.summary));
  L.save('e08', out);
  srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
