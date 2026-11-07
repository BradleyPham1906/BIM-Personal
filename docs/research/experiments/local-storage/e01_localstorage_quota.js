// e01_localstorage_quota.js -- Hypothesis 1 (2026-10-31).
// Tests: localStorage's per-origin limit in this Chromium is about 5 MiB of UTF-16 characters.
// Method: on http://localhost, in a fresh browser context for each run, binary-search the
// largest N for which localStorage.setItem('k', X.repeat(N)) succeeds, for X = 'a' (Latin-1)
// and X = U+4E00 (outside Latin-1, so a 2-byte UTF-16 code unit in any encoding), and for a
// 100-character key (does the key count?). Then fill the origin with 8 keys to see whether the
// limit is per origin (sum) rather than per item. Records the thrown error's name, code,
// message and whether it is a DOMException. 3 runs.
'use strict';
var pw = require('playwright');
var L = require('./_lib');

function pageSearch(opts) {
  // runs in the page; ES5
  var ch = opts.ch, key = opts.key;
  localStorage.clear();
  var lo = 0, hi = 16 * 1024 * 1024, err = null; // hi: certainly fails
  while (lo < hi) {
    var mid = Math.floor((lo + hi + 1) / 2);
    try { localStorage.setItem(key, new Array(mid + 1).join(ch)); lo = mid; }
    catch (e) { hi = mid - 1; err = { name: e.name, code: e.code, message: e.message, isDOMException: e instanceof DOMException }; }
    localStorage.clear();
  }
  // confirm the edge
  var okAt = true, failAbove = false;
  try { localStorage.setItem(key, new Array(lo + 1).join(ch)); } catch (e) { okAt = false; }
  localStorage.clear();
  try { localStorage.setItem(key, new Array(lo + 2).join(ch)); } catch (e) { failAbove = true; }
  localStorage.clear();
  return { maxValueLen: lo, keyLen: key.length, totalChars: lo + key.length, okAtMax: okAt, failsAtMaxPlus1: failAbove, error: err };
}

function pageMultiKey() {
  localStorage.clear();
  var chunk = new Array(1024 * 1024 + 1).join('a'); // 1 Mi chars
  var stored = 0, i = 0, err = null;
  for (i = 0; i < 20; i++) {
    try { localStorage.setItem('key' + i, chunk); stored += chunk.length + ('key' + i).length; }
    catch (e) { err = { name: e.name, code: e.code }; break; }
  }
  // top up the last key with a binary search for the remainder
  var lo = 0, hi = chunk.length;
  while (lo < hi) {
    var mid = Math.floor((lo + hi + 1) / 2);
    try { localStorage.setItem('rest', new Array(mid + 1).join('a')); lo = mid; } catch (e) { hi = mid - 1; }
    localStorage.removeItem('rest');
  }
  var n = localStorage.length;
  localStorage.clear();
  return { fullKeys: i, charsInFullKeys: stored, remainderValueLen: lo, totalChars: stored + lo + 4, error: err, lengthBeforeClear: n };
}

(async function () {
  var srv = await L.startServer(0);
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), headless: true, origin: srv.origin, runs: [] };
  for (var run = 0; run < 3; run++) {
    var ctx = await browser.newContext();
    var page = await ctx.newPage();
    await page.goto(srv.origin + '/');
    var r = {};
    r.ascii = await page.evaluate(pageSearch, { ch: 'a', key: 'k' });
    r.cjk = await page.evaluate(pageSearch, { ch: '一', key: 'k' });
    r.longKey = await page.evaluate(pageSearch, { ch: 'a', key: new Array(101).join('x') });
    r.multi = await page.evaluate(pageMultiKey);
    out.runs.push(r);
    console.log('run ' + run, JSON.stringify(r));
    await ctx.close();
  }
  out.summary = {
    asciiMax: L.stats(out.runs.map(function (r) { return r.ascii.maxValueLen; })),
    cjkMax: L.stats(out.runs.map(function (r) { return r.cjk.maxValueLen; })),
    longKeyMax: L.stats(out.runs.map(function (r) { return r.longKey.maxValueLen; })),
    multiTotal: L.stats(out.runs.map(function (r) { return r.multi.totalChars; }))
  };
  console.log(JSON.stringify(out.summary, null, 1));
  L.save('e01', out);
  await browser.close(); srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
