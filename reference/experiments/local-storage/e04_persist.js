// e04_persist.js -- Hypothesis 4 (2026-10-31).
// Tests: what navigator.storage.persist() returns in headless Chromium for a localhost page,
// with and without permissions granted through context.grantPermissions (tried: none,
// ['notifications'], ['persistent-storage'], ['storage-access'] -- a name Playwright refuses
// is recorded as refused), and navigator.storage.persisted() before and after. Also
// navigator.permissions.query({name:'persistent-storage'}) before and after. In an
// incognito-like context and in a persistent profile (launchPersistentContext), in the
// default headless shell and in the full Chromium binary (channel 'chromium'). 3 runs each.
// Extra cases (after the first pass showed Playwright refuses 'persistent-storage' and that a
// grant of any other permission turns 'persistent-storage' to 'denied', CDP's grantPermissions
// rejecting every permission it is not given): the permission set through the Chrome DevTools
// Protocol directly, Browser.setPermission {name:'persistent-storage'} -> 'granted', and
// Browser.grantPermissions ['durableStorage'], both for the localhost origin.
'use strict';
var pw = require('playwright');
var L = require('./_lib');

function pageTest() {
  var out = {};
  function q() {
    return navigator.permissions.query({ name: 'persistent-storage' }).then(function (s) { return s.state; }, function (e) { return 'query threw ' + e.name; });
  }
  return navigator.storage.persisted().then(function (p) { out.persistedBefore = p; return q(); })
    .then(function (s) { out.permBefore = s; return navigator.storage.persist(); })
    .then(function (r) { out.persistReturned = r; return navigator.storage.persisted(); })
    .then(function (p) { out.persistedAfter = p; return q(); })
    .then(function (s) { out.permAfter = s; return out; })
    .catch(function (e) { out.error = e.name + ': ' + e.message; return out; });
}

// sends a Browser.* permission command to every browser context (CDP needs the context id for
// a non-default context; ids come from Target.getBrowserContexts)
async function sendAllContexts(cdp, method, params) {
  var ids = (await cdp.send('Target.getBrowserContexts')).browserContextIds || [];
  var res = [];
  res.push(await cdp.send(method, params).then(function () { return 'default:ok'; }, function (e) { return 'default:' + e.message.split('\n')[0]; }));
  for (var i = 0; i < ids.length; i++) {
    var p = Object.assign({ browserContextId: ids[i] }, params);
    res.push(await cdp.send(method, p).then(function () { return 'ctx:ok'; }, function (e) { return 'ctx:' + e.message.split('\n')[0]; }));
  }
  return res;
}

(async function () {
  var srv = await L.startServer(0);
  var out = { origin: srv.origin, runs: [] };
  var grants = [null, ['notifications'], ['persistent-storage'], ['storage-access'], 'cdp:setPermission', 'cdp:grantDurable'];
  var channels = [undefined, 'chromium'];
  for (var c = 0; c < channels.length; c++) {
    var opt = channels[c] ? { channel: channels[c] } : {};
    for (var run = 0; run < 3; run++) {
      for (var g = 0; g < grants.length; g++) {
        for (var kind = 0; kind < 2; kind++) {
          var r = { channel: channels[c] || 'default', run: run, grant: grants[g], kind: kind ? 'persistent' : 'newContext' };
          var browser = null, ctx, dir = null;
          if (kind) { dir = L.tmpDir('e04-'); ctx = await pw.chromium.launchPersistentContext(dir, opt); }
          else { browser = await pw.chromium.launch(opt); ctx = await browser.newContext(); }
          r.version = (browser || ctx.browser()) ? (browser || ctx.browser()).version() : null;
          if (typeof grants[g] === 'string') {
            try {
              var cdp = await (browser || ctx.browser()).newBrowserCDPSession();
              if (grants[g] === 'cdp:setPermission') {
                var prm = { permission: { name: 'persistent-storage' }, setting: 'granted', origin: srv.origin };
                r.cdpResult = await sendAllContexts(cdp, 'Browser.setPermission', prm);
              } else {
                r.cdpResult = await sendAllContexts(cdp, 'Browser.grantPermissions', { permissions: ['durableStorage'], origin: srv.origin });
              }
              r.grantOk = true;
            } catch (e) { r.grantOk = false; r.grantError = String(e.message).split('\n')[0]; }
          } else if (grants[g]) {
            try { await ctx.grantPermissions(grants[g], { origin: srv.origin }); r.grantOk = true; }
            catch (e) { r.grantOk = false; r.grantError = String(e.message).split('\n')[0]; }
          }
          var page = await ctx.newPage();
          await page.goto(srv.origin + '/');
          Object.assign(r, await page.evaluate(pageTest));
          out.runs.push(r); console.log(JSON.stringify(r));
          await ctx.close(); if (browser) await browser.close(); if (dir) L.rm(dir);
        }
      }
    }
  }
  L.save('e04', out);
  srv.server.close();
})().catch(function (e) { console.error(e); process.exit(1); });
