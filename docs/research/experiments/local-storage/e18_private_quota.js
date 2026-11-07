// e18_private_quota.js -- V172g, hypothesis H37 (2026-11-07).
// D2 asks for a reminder "at the first save in a private window". Can a page tell an off-the-record
// (incognito) context from a normal profile in Chromium? Measured: navigator.storage.estimate()
// quota and usage, navigator.storage.persisted(), and whether IndexedDB opens, in
// (1) a Playwright browser context (off the record, as Chrome's incognito profile is) and
// (2) a persistent profile (launchPersistentContext), over http and from file://.
// Also the host's memory and disk, since Chromium's quotas follow them (the threshold a page
// would compare against is that number, not a constant).
// 3 runs each. Run: node e18_private_quota.js
'use strict';
var pw = require('playwright');
var os = require('os');
var fs = require('fs');
var path = require('path');
var cp = require('child_process');
var L = require('./_lib');

function probe() {
  var out = {};
  return navigator.storage.estimate().then(function (e) { out.quota = e.quota; out.usage = e.usage; })
    .then(function () { return navigator.storage.persisted(); }).then(function (p) { out.persisted = p; })
    .then(function () {
      return new Promise(function (res) {
        try { var r = indexedDB.open('e18'); r.onsuccess = function () { r.result.close(); out.idb = 'opened'; res(); }; r.onerror = function () { out.idb = 'error ' + (r.error && r.error.name); res(); }; }
        catch (x) { out.idb = 'threw ' + x.name; res(); }
      });
    }).then(function () { return out; }, function (e) { out.error = e.name + ': ' + e.message; return out; });
}

(async function () {
  var srv = await L.startServer(0);
  var dir = L.tmpDir('e18-');
  var blank = path.join(dir, 'p.html');
  fs.writeFileSync(blank, '<!doctype html><title>e18</title>');
  var targets = { http: srv.origin + '/', file: 'file://' + blank };
  var df = cp.execSync('df -B1 --output=size,avail ' + L.SCRATCH).toString().trim().split('\n')[1].trim().split(/\s+/).map(Number);
  var out = { host: { totalmem: os.totalmem(), diskSize: df[0], diskAvail: df[1] }, offTheRecord: {}, persistent: {} };
  var browser = await pw.chromium.launch();
  out.version = browser.version();
  for (var k in targets) {
    out.offTheRecord[k] = []; out.persistent[k] = [];
    for (var run = 0; run < 3; run++) {
      var ctx = await browser.newContext(); var page = await ctx.newPage();
      await page.goto(targets[k]); out.offTheRecord[k].push(await page.evaluate(probe)); await ctx.close();
      var prof = L.tmpDir('e18-prof-');
      var pc = await pw.chromium.launchPersistentContext(prof);
      var pp = pc.pages()[0] || await pc.newPage();
      await pp.goto(targets[k]); out.persistent[k].push(await pp.evaluate(probe)); await pc.close(); L.rm(prof);
    }
  }
  await browser.close();
  function gib(x) { return Math.round(x / 1073741824 * 1000) / 1000; }
  console.log('host: RAM', gib(out.host.totalmem), 'GiB; disk', gib(out.host.diskSize), 'GiB, free', gib(out.host.diskAvail), 'GiB; Chromium', out.version);
  ['offTheRecord', 'persistent'].forEach(function (m) {
    for (var k in targets) {
      console.log(m, k, out[m][k].map(function (r) { return 'quota ' + gib(r.quota) + ' GiB (' + r.quota + '), persisted ' + r.persisted + ', idb ' + r.idb + (r.error ? ' ' + r.error : ''); }).join(' | '));
    }
  });
  out.ratios = {};
  for (var k2 in targets) {
    out.ratios[k2] = { quotaOverRam_offTheRecord: out.offTheRecord[k2][0].quota / out.host.totalmem, quotaOverDisk_persistent: out.persistent[k2][0].quota / out.host.diskSize };
  }
  console.log('ratios', JSON.stringify(out.ratios));
  L.save('e18', out);
  srv.server.close(); L.rm(dir);
})().catch(function (e) { console.error(e); process.exit(1); });
