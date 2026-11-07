// e13b_commit_first_run.js -- V172f, H19 followed up (2026-11-02).
// e13 found an explicit commit() in the unload handler kept the write 9 times in 10, in every combination.
// Which run is lost? Hypothesis: the first run of a context, where the database was created moments before
// (its files new on disk). Method: e13's page and handlers (reused from e13 by reading its PAGE string); modes
// vcc and phc, action reload, 1 KB; 20 runs per context, three contexts; once with the database created by the
// first run's page (as in e13), once created and written beforehand by a setup page. Per-run outcomes kept.
'use strict';
var pw = require('playwright');
var fs = require('fs');
var L = require('./_lib');
var src = fs.readFileSync(__dirname + '/e13_unload_write.js', 'utf8');
var PAGE = eval(src.slice(src.indexOf('var PAGE = ') + 11, src.indexOf("var MODES")).trim().replace(/;$/, ''));

(async function () {
  var srv = await L.startServer(0, { '/app': { body: PAGE } });
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), date: new Date().toISOString(), sets: [] };
  var modes = ['vcc', 'phc'];
  for (var pre = 0; pre < 2; pre++) {
    for (var m = 0; m < modes.length; m++) {
      for (var c = 0; c < 3; c++) {
        var ctx = await browser.newContext();
        if (pre) {
          var sp = await ctx.newPage(); await sp.goto(srv.origin + '/app');
          await sp.evaluate(function () { return window.__ready.then(function () { return new Promise(function (res) {
            var t = window.__db.transaction('s', 'readwrite'); t.objectStore('s').put('x', 'warm'); t.oncomplete = function () { res(true); }; }); }); });
          await sp.close();
        }
        var lost = [];
        for (var run = 0; run < 20; run++) {
          var key = 'k' + modes[m] + 'p' + pre + 'c' + c + 'r' + run + 'x';
          var page = await ctx.newPage();
          await page.goto(srv.origin + '/app');
          await page.evaluate(function () { return window.__ready; });
          await page.evaluate(function (a) { return window.__arm(a.mode, a.key, 1024); }, { mode: modes[m], key: key });
          await page.reload();
          await page.evaluate(function () { return window.__ready; });
          var r = await page.evaluate(function (k) { return window.__check(k, 1024); }, key);
          if (!r.idb) lost.push(run);
          await page.close();
        }
        await ctx.close();
        var set = { mode: modes[m], dbBefore: !!pre, context: c, lostRuns: lost };
        out.sets.push(set);
        console.log(JSON.stringify(set));
      }
    }
  }
  await browser.close(); srv.server.close();
  L.save('e13b_commit_first_run', out);
})();
