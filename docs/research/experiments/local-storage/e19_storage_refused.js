// e19_storage_refused.js -- V172g, hypothesis H38 (2026-11-07).
// D5: the one-file build opened from file:// in a browser that refuses storage there. WebKit's code
// (part 4.4) throws SecurityError from the window.localStorage getter and from indexedDB.open() for a
// local origin. Safari is not available here, so the refusal is imitated in Chromium by an init
// script that makes exactly those two calls throw SecurityError (navigator.storage left alone).
// Measured on the current build (canvas_v10.html from file://): page errors, console warnings, the
// toasts the app shows (the #a3d-toast text over time), whether a point added by the test hook is
// on screen, and what the app says when Save to file is used. Control: the same build with storage
// allowed. 3 runs each. Run: node e19_storage_refused.js [path to canvas_v10.html]
'use strict';
var pw = require('playwright');
var path = require('path');
var L = require('./_lib');

var BUILD = process.argv[2] || path.resolve(__dirname, '../../../../canvas_v10.html');

var REFUSE = function () {
  function refused() { var e = new DOMException('The operation is insecure.', 'SecurityError'); return e; }
  Object.defineProperty(window, 'localStorage', { configurable: true, get: function () { throw refused(); } });
  if (window.indexedDB) {
    var f = Object.getPrototypeOf(window.indexedDB);
    f.open = function () { throw refused(); };
  }
};

async function one(browser, refuse) {
  var ctx = await browser.newContext({ acceptDownloads: true, viewport: { width: 1500, height: 950 } });
  if (refuse) await ctx.addInitScript(REFUSE);
  var page = await ctx.newPage();
  var errors = [], warns = [], toasts = [];
  page.on('pageerror', function (e) { errors.push(String(e.message).slice(0, 200)); });
  page.on('console', function (m) { if (m.type() === 'warning' || m.type() === 'error') warns.push(m.text().slice(0, 200)); });
  await page.exposeFunction('__e19toast', function (t) { if (t && toasts.indexOf(t) < 0) toasts.push(t); });
  await page.addInitScript(function () {
    new MutationObserver(function () {
      var el = document.getElementById('a3d-toast');
      if (el && el.textContent) window.__e19toast(el.textContent.trim());
    }).observe(document, { subtree: true, childList: true, characterData: true, attributes: true });
  });
  await page.goto('file://' + BUILD);
  await page.waitForTimeout(2500);
  var drew = await page.evaluate(function () {
    try {
      // a point added through the test hook, then the page hidden, which flushes a pending save
      window.__a3dAddPoint(1, 0, 1);
      document.dispatchEvent(new Event('visibilitychange'));
      window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: false }));
      return 'objects ' + window.__a3dObjects().length;
    } catch (e) { return 'threw ' + e.name + ': ' + e.message; }
  });
  await page.waitForTimeout(800);
  var dl = null;
  try {
    var pr = page.waitForEvent('download', { timeout: 4000 });
    await page.evaluate(function () { window.__a3dExportProject(); });
    var d = await pr; dl = d.suggestedFilename();
  } catch (e) { dl = 'no download: ' + e.message.slice(0, 80); }
  await page.waitForTimeout(500);
  await ctx.close();
  return { errors: errors, warnings: warns, toasts: toasts, drew: drew, download: dl };
}

(async function () {
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), build: BUILD, refused: [], allowed: [] };
  for (var run = 0; run < 3; run++) {
    out.refused.push(await one(browser, true));
    out.allowed.push(await one(browser, false));
  }
  await browser.close();
  ['refused', 'allowed'].forEach(function (k) {
    console.log('== ' + k);
    out[k].forEach(function (r, i) {
      console.log('run ' + i + ': errors ' + r.errors.length + ', warnings ' + r.warnings.length + ', drew: ' + r.drew + ', download: ' + r.download);
      if (i === 0) { console.log('  errors:', JSON.stringify(r.errors)); console.log('  warnings:', JSON.stringify(r.warnings)); console.log('  toasts:', JSON.stringify(r.toasts)); }
    });
  });
  L.save('e19', out);
})().catch(function (e) { console.error(e); process.exit(1); });
