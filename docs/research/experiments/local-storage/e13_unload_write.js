// e13_unload_write.js -- V172f, hypotheses H17 to H20 (2026-11-02).
// Question: once every save goes to IndexedDB, does a write started while the page goes away commit?
// The app today writes a waiting save to localStorage in `pagehide`, synchronously (V115: "a wall drawn just
// before a reload, gone 8 times in 8" without it). IndexedDB writes are asynchronous.
// Method: a localhost page opens database 'e13' (store 's') at load and keeps the connection open, as the app
// does. Before an unload it arms one handler that writes a value unique to the run:
//   vc   put in `visibilitychange` (to hidden), auto-commit
//   vcc  put in `visibilitychange`, then tx.commit()
//   ph   put in `pagehide`, auto-commit
//   phc  put in `pagehide`, then tx.commit()
//   ls   localStorage.setItem in `pagehide` (the control: the app's present way)
// Each handler first writes a marker to localStorage synchronously, so a run says whether its event fired.
// Then the page goes away in one of three ways: reload (page.reload), navigation to another page of the same
// origin (page.goto), or the tab closed (page.close). A page of the same origin then reads the key back.
// Two sizes: 1 KB and 4 MB (4,194,304 characters, a large project's record). Ten runs of each combination,
// each run with its own key, in one browser context per combination.
'use strict';
var pw = require('playwright');
var L = require('./_lib');

var PAGE = '<!doctype html><meta charset="utf-8"><title>e13</title><body>e13<script>' +
  'window.__ready=new Promise(function(res){var r=indexedDB.open("e13",1);' +
  'r.onupgradeneeded=function(){r.result.createObjectStore("s");};' +
  'r.onsuccess=function(){window.__db=r.result;res(true);};r.onerror=function(){res(false);};});' +
  'window.__arm=function(mode,key,size){' +
  '  var v=new Array(Math.floor(size/key.length)+2).join(key).slice(0,size);' +
  '  function mark(ev){try{localStorage.setItem("e13-fired-"+key,ev);}catch(e){}}' +
  '  function put(commit){var t=window.__db.transaction("s","readwrite");t.objectStore("s").put(v,key);if(commit&&t.commit)t.commit();}' +
  '  if(mode==="vc"||mode==="vcc")document.addEventListener("visibilitychange",function(){if(document.visibilityState!=="hidden")return;mark("vc");put(mode==="vcc");});' +
  '  if(mode==="ph"||mode==="phc")window.addEventListener("pagehide",function(){mark("ph");put(mode==="phc");});' +
  '  if(mode==="ls")window.addEventListener("pagehide",function(){mark("ph");try{localStorage.setItem("e13-ls-"+key,v);}catch(e){mark("ls-refused");}});' +
  '  return v.length;};' +
  'window.__check=function(key,size){return new Promise(function(res){' +
  '  var fired=localStorage.getItem("e13-fired-"+key),ls=localStorage.getItem("e13-ls-"+key);' +
  '  var r=indexedDB.open("e13",1);r.onupgradeneeded=function(){r.result.createObjectStore("s");};' +
  '  r.onsuccess=function(){var db=r.result,g=db.transaction("s","readonly").objectStore("s").get(key);' +
  '    g.onsuccess=function(){var x=g.result;db.close();' +
  '      res({fired:fired,idb:typeof x==="string"&&x.length===size&&x.slice(0,key.length)===key,ls:typeof ls==="string"&&ls.length===size});};' +
  '    g.onerror=function(){db.close();res({fired:fired,idb:false,err:"get"});};};' +
  '  r.onerror=function(){res({fired:fired,idb:false,err:"open"});};});};' +
  '</script></body>';

var MODES = ['vc', 'vcc', 'ph', 'phc', 'ls'];
var ACTIONS = ['reload', 'nav', 'close'];
var SIZES = [{ name: '1KB', n: 1024 }, { name: '4MB', n: 4194304 }];
var RUNS = 10;

(async function () {
  var srv = await L.startServer(0, { '/app': { body: PAGE }, '/other': { body: PAGE }, '/check': { body: PAGE } });
  var browser = await pw.chromium.launch();
  var out = { version: browser.version(), date: new Date().toISOString(), runs: RUNS, results: {} };
  for (var s = 0; s < SIZES.length; s++) {
    for (var a = 0; a < ACTIONS.length; a++) {
      for (var m = 0; m < MODES.length; m++) {
        var mode = MODES[m], action = ACTIONS[a], size = SIZES[s];
        if (mode === 'ls' && size.n > 1024 * 1024) { /* localStorage holds 5,242,880 units for the origin; 4 MB of ASCII fits once */ }
        var ctx = await browser.newContext();
        var res = { fired: 0, idb: 0, ls: 0, errors: [] };
        for (var run = 0; run < RUNS; run++) {
          var key = 'k' + mode + action + size.name + 'r' + run + 'x';
          var page = await ctx.newPage();
          try {
            await page.goto(srv.origin + '/app');
            await page.evaluate(function () { return window.__ready; });
            await page.evaluate(function (a) { return window.__arm(a.mode, a.key, a.size); }, { mode: mode, key: key, size: size.n });
            var checker = page;
            if (action === 'reload') { await page.reload(); }
            else if (action === 'nav') { await page.goto(srv.origin + '/other'); }
            else { await page.close(); checker = await ctx.newPage(); await checker.goto(srv.origin + '/check'); }
            await checker.evaluate(function () { return window.__ready; });
            var r = await checker.evaluate(function (a) { return window.__check(a.key, a.size); }, { key: key, size: size.n });
            if (r.fired) res.fired++;
            if (r.idb) res.idb++;
            if (r.ls) res.ls++;
            if (r.err) res.errors.push(r.err);
            /* the control's 4 MB value is removed so the next run's fits */
            await checker.evaluate(function (k) { localStorage.removeItem('e13-ls-' + k); }, key);
            await checker.close();
          } catch (e) {
            res.errors.push(String(e).slice(0, 160));
            try { await page.close(); } catch (e2) {}
          }
        }
        await ctx.close();
        var label = size.name + ' ' + action + ' ' + mode;
        out.results[label] = res;
        console.log(label + ': fired ' + res.fired + '/' + RUNS + ', idb ' + res.idb + '/' + RUNS + ', ls ' + res.ls + '/' + RUNS + (res.errors.length ? ' errors ' + res.errors.slice(0, 2).join(' | ') : ''));
      }
    }
  }
  await browser.close();
  srv.server.close();
  L.save('e13_unload_write', out);
})();
