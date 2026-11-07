// e01_scope.js -- H29 (V172h, 2026-11-07): a worker at /BIM-Personal/sw.js controls /BIM-Personal/ and every path
// under it (docs/, v/x/), not /Other/ (another Pages project of the same origin) nor /BIM-Personalx/.
// Also: register with scope '/' (refused without Service-Worker-Allowed: H30's consequence), and the
// default scope of a worker registered from a page in docs/. Runs: RUNS fresh contexts (default 3).
'use strict';
var C = require('./_common.js');
var pw = require('playwright');
var RUNS = +process.env.RUNS || 3;

(async function () {
  var A = C.buildA();
  var fs = require('fs'), path = require('path');
  var other = path.join(C.SCRATCH, 'other');
  fs.mkdirSync(other, { recursive: true });
  fs.writeFileSync(path.join(other, 'index.html'), C.page(''));
  var S = await C.serve({ build: A, other: other });
  S.override('/BIM-Personal/sw.js', { body: C.probeSw('A') });
  S.override('/BIM-Personal/reg.html', { body: C.page('') });
  S.override('/BIM-Personal/v/x/', { body: C.page(''), type: 'text/html; charset=utf-8' });
  S.override('/BIM-Personalx/', { body: C.page(''), type: 'text/html; charset=utf-8' });
  S.override('/BIM-Personal/docs/reg2.html', { body: C.page(''), type: 'text/html; charset=utf-8' });
  S.override('/BIM-Personal/docs/sw2.js', { body: C.probeSw('docs') });
  var browser = await pw.chromium.launch();
  var out = { chromium: browser.version(), runs: [] };
  for (var r = 0; r < RUNS; r++) {
    var ctx = await browser.newContext();
    var p = await ctx.newPage();
    var run = {};
    await p.goto(S.origin + '/BIM-Personal/reg.html');
    run.register = await p.evaluate(function () { return window.__register('/BIM-Personal/sw.js'); });
    run.registerRoot = await p.evaluate(function () { return window.__register('/BIM-Personal/sw.js', { scope: '/' }); });
    await p.evaluate(function () { return navigator.serviceWorker.ready.then(function () { return 1; }); });
    var urls = ['/BIM-Personal/', '/BIM-Personal/reg.html', '/BIM-Personal/docs/', '/BIM-Personal/docs/bim.html',
      '/BIM-Personal/v/x/', '/BIM-Personal', '/Other/', '/BIM-Personalx/'];
    run.pages = {};
    for (var i = 0; i < urls.length; i++) {
      await p.goto(S.origin + urls[i], { waitUntil: 'load' });
      run.pages[urls[i]] = await p.evaluate(function () {
        var c = navigator.serviceWorker ? navigator.serviceWorker.controller : null;
        return fetch('/BIM-Personal/__probe?from=page').then(function (r) { return r.text(); }).then(function (t) {
          return { finalPath: location.pathname, controlled: !!c, probeViaSW: t.indexOf('viaSW') >= 0 };
        });
      });
    }
    // a worker registered from docs/ with no scope gets docs/ as its scope
    await p.goto(S.origin + '/BIM-Personal/docs/reg2.html');
    run.docsDefaultScope = await p.evaluate(function () { return window.__register('/BIM-Personal/docs/sw2.js'); });
    run.registrations = await p.evaluate(function () {
      return navigator.serviceWorker.getRegistrations().then(function (a) { return a.map(function (x) { return x.scope; }); });
    });
    out.runs.push(run);
    await ctx.close();
  }
  await browser.close();
  await S.stop();
  C.save('e01_scope', out);
  console.log(JSON.stringify(out.runs[0], null, 1));
})().catch(function (e) { console.error(e); process.exit(1); });
