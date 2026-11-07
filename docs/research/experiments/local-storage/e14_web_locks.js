// e14_web_locks.js -- V172f, hypotheses H21 to H24 (2026-11-02).
// Question: can the Web Locks API tell a tab that a project is open in another tab, and does the lock go away
// when that tab reloads, navigates, closes, crashes or enters the back/forward cache? Does `steal` hand it over,
// and does the old holder learn of it? Do Web Locks and BroadcastChannel work for the one-file build from file://?
// Method: Chromium (Playwright's build), pages of one browser context. Page A asks for the lock 'p1' and holds it
// (its callback returns a promise that never settles). Page B then:
//   1. asks with {ifAvailable:true}: granted null while A holds it?
//   2. reads navigator.locks.query(): A's hold listed?
//   3. queues a plain request; A then reloads / navigates (same origin) / closes / crashes (CDP Page.crash):
//      is B granted, and how soon (ms)?
//   4. asks with {steal:true}: granted at once; A's request promise rejects with which error?
// The same on http://localhost and on file:// (two files in one folder). Then the back/forward cache: Chromium
// started without Playwright's --disable-back-forward-cache; A holds the lock and navigates away; is the lock
// still held, was A restored from the cache on Back (pageshow.persisted), and what does
// PerformanceNavigationTiming.notRestoredReasons say? Last, a BroadcastChannel message from A to B on both.
// Five runs of each release case.
'use strict';
var pw = require('playwright');
var fs = require('fs');
var path = require('path');
var L = require('./_lib');

var PAGE = '<!doctype html><meta charset="utf-8"><title>e14</title><body>e14<script>' +
  'window.__log=[];window.addEventListener("pageshow",function(e){window.__log.push("pageshow persisted="+e.persisted);});' +
  'window.__hold=function(name){if(!navigator.locks)return "no navigator.locks";' +
  '  navigator.locks.request(name,function(){window.__log.push("granted "+name);return new Promise(function(){});})' +
  '    .then(function(){window.__log.push("request settled");},function(e){window.__log.push("request rejected "+(e&&e.name));});' +
  '  return "asked";};' +
  'window.__probe=function(name){return new Promise(function(res){if(!navigator.locks){res({avail:"no navigator.locks"});return;}' +
  '  navigator.locks.request(name,{ifAvailable:true},function(l){res({avail:l?"granted":"null"});})' +
  '    ["catch"](function(e){res({avail:"error "+(e&&e.name)});});});};' +
  'window.__query=function(){if(!navigator.locks)return Promise.resolve(null);return navigator.locks.query().then(function(q){' +
  '  return {held:q.held.map(function(h){return h.name+"/"+h.mode;}),pending:q.pending.map(function(h){return h.name;})};},function(e){return {err:e&&e.name};});};' +
  'window.__queue=function(name){window.__granted=null;var t0=performance.now();' +
  '  navigator.locks.request(name,function(){window.__granted=performance.now()-t0;});return "queued";};' +
  'window.__steal=function(name){return new Promise(function(res){navigator.locks.request(name,{steal:true},function(l){res(l?"granted":"null");})' +
  '  ["catch"](function(e){res("error "+(e&&e.name));});});};' +
  'window.__env=function(){return {origin:String(self.origin),secure:window.isSecureContext,locks:!!navigator.locks,bc:typeof BroadcastChannel};};' +
  'window.__bcListen=function(){window.__bcGot=[];try{var c=new BroadcastChannel("e14");c.onmessage=function(e){window.__bcGot.push(e.data);};window.__bc=c;return "listening";}catch(e){return "error "+e.name;}};' +
  'window.__bcSend=function(x){try{var c=new BroadcastChannel("e14");c.postMessage(x);return "sent";}catch(e){return "error "+e.name;}};' +
  'window.__nrr=function(){var n=performance.getEntriesByType("navigation")[0];var r=n&&n.notRestoredReasons;' +
  '  if(!r)return null;function walk(x){return {reasons:(x.reasons||[]).map(function(y){return y.reason;}),children:(x.children||[]).map(walk)};}return walk(r);};' +
  '</script></body>';

function bounded(p, ms, what) {
  return Promise.race([p, new Promise(function (res, rej) { setTimeout(function () { rej(new Error('timeout: ' + what)); }, ms); })]);
}

async function releaseCase(ctx, urlA, urlB, how) {
  var a = await ctx.newPage(); await a.goto(urlA);
  var b = await ctx.newPage(); await b.goto(urlB);
  var r = { how: how };
  r.hold = await a.evaluate(function () { return window.__hold('p1'); });
  await a.waitForTimeout(50);
  r.probeWhileHeld = (await b.evaluate(function () { return window.__probe('p1'); })).avail;
  r.queryWhileHeld = await b.evaluate(function () { return window.__query(); });
  if (how === 'steal') {
    r.steal = await b.evaluate(function () { return window.__steal('p1'); });
    await a.waitForTimeout(100);
    r.aLog = await a.evaluate(function () { return window.__log; });
    r.queryAfter = await b.evaluate(function () { return window.__query(); });
  } else {
    await b.evaluate(function () { return window.__queue('p1'); });
    var t0 = Date.now();
    if (how === 'reload') await a.reload();
    else if (how === 'nav') await a.goto(urlB);
    else if (how === 'close') await a.close();
    else if (how === 'crash') {
      var cdp = await ctx.newCDPSession(a);
      /* Page.crash never answers: the page it would answer from is gone, so it is not awaited */
      cdp.send('Page.crash').catch(function (e) { r.crashSend = String(e).slice(0, 80); });
    }
    var granted = null;
    for (var i = 0; i < 60; i++) {
      granted = await b.evaluate(function () { return window.__granted; });
      if (granted !== null) break;
      await b.waitForTimeout(50);
    }
    r.grantedAfterMs = granted === null ? null : Date.now() - t0;
  }
  try { await bounded(a.close(), 5000, 'close A'); } catch (e) {}
  try { await bounded(b.close(), 5000, 'close B'); } catch (e) {}
  return r;
}

(async function () {
  var srv = await L.startServer(0, { '/a': { body: PAGE }, '/b': { body: PAGE } });
  var dir = L.tmpDir('e14-');
  fs.writeFileSync(path.join(dir, 'a.html'), PAGE);
  fs.writeFileSync(path.join(dir, 'b.html'), PAGE);
  var fa = 'file://' + path.join(dir, 'a.html'), fb = 'file://' + path.join(dir, 'b.html');
  var out = { date: new Date().toISOString(), env: {}, cases: {}, bfcache: {}, bc: {} };

  var browser = await pw.chromium.launch();
  out.version = browser.version();
  var ctx = await browser.newContext();
  var p = await ctx.newPage();
  await p.goto(srv.origin + '/a'); out.env.http = await p.evaluate(function () { return window.__env(); });
  await p.goto(fa); out.env.file = await p.evaluate(function () { return window.__env(); });
  await p.close();
  var hows = ['reload', 'nav', 'close', 'crash', 'steal'];
  var schemes = [{ name: 'http', a: srv.origin + '/a', b: srv.origin + '/b' }, { name: 'file', a: fa, b: fb }];
  for (var s = 0; s < schemes.length; s++) {
    for (var h = 0; h < hows.length; h++) {
      var label = schemes[s].name + ' ' + hows[h], runs = [];
      for (var run = 0; run < 5; run++) {
        var c = await browser.newContext();
        try { runs.push(await bounded(releaseCase(c, schemes[s].a, schemes[s].b, hows[h]), 20000, hows[h])); }
        catch (e) { runs.push({ error: String(e).slice(0, 160) }); }
        try { await bounded(c.close(), 10000, 'context close'); } catch (e) {}
      }
      out.cases[label] = runs;
      var r0 = runs[0] || {};
      console.log(label + ': probe while held ' + runs.map(function (r) { return r.probeWhileHeld; }).join(',') +
        (hows[h] === 'steal' ? '; steal ' + runs.map(function (r) { return r.steal; }).join(',') + '; A saw ' + JSON.stringify(r0.aLog)
          : '; B granted after ms ' + runs.map(function (r) { return r.grantedAfterMs; }).join(',')) +
        (r0.error ? ' ERROR ' + r0.error : ''));
    }
    // BroadcastChannel from A to B
    var c2 = await browser.newContext();
    var a2 = await c2.newPage(); await a2.goto(schemes[s].a);
    var b2 = await c2.newPage(); await b2.goto(schemes[s].b);
    var lis = await b2.evaluate(function () { return window.__bcListen(); });
    var sent = await a2.evaluate(function () { return window.__bcSend('hello'); });
    await b2.waitForTimeout(200);
    out.bc[schemes[s].name] = { listen: lis, sent: sent, got: await b2.evaluate(function () { return window.__bcGot; }) };
    console.log('BroadcastChannel ' + schemes[s].name + ': ' + JSON.stringify(out.bc[schemes[s].name]));
    await c2.close();
  }
  await browser.close();

  // the back/forward cache, enabled
  var b3 = await pw.chromium.launch({ ignoreDefaultArgs: ['--disable-back-forward-cache'] });
  for (var run2 = 0; run2 < 3; run2++) {
    var c3 = await b3.newContext();
    var A = await c3.newPage(); await A.goto(srv.origin + '/a');
    var B = await c3.newPage(); await B.goto(srv.origin + '/b');
    var rr = {};
    rr.withoutLock = {};
    // control: a page holding nothing goes into the cache and comes back from it
    await A.goto(srv.origin + '/b'); await A.goBack();
    rr.withoutLock.log = await A.evaluate(function () { return window.__log; });
    // A holds the lock, then navigates away and back
    await A.evaluate(function () { return window.__hold('p1'); });
    await A.waitForTimeout(50);
    await A.goto(srv.origin + '/b');
    await A.waitForTimeout(150);
    rr.queryWhileAway = await B.evaluate(function () { return window.__query(); });
    rr.probeWhileAway = (await B.evaluate(function () { return window.__probe('p1'); })).avail;
    await A.goBack();
    await A.waitForTimeout(100);
    rr.logAfterBack = await A.evaluate(function () { return window.__log; });
    rr.notRestoredReasons = await A.evaluate(function () { return window.__nrr(); });
    out.bfcache['run' + run2] = rr;
    rr.note = 'see notRestoredReasons';
    console.log('bfcache run ' + run2 + ': ' + JSON.stringify(rr));
    await c3.close();
  }
  await b3.close();
  srv.server.close();
  L.rm(dir);
  L.save('e14_web_locks', out);
})();
