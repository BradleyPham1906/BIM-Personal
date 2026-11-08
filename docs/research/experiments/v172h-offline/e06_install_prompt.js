// e06_install_prompt.js -- H49 (V172h, 2026-11-07): does Chromium fire beforeinstallprompt headless, and does it
// still need a service worker with a fetch handler? Four pages under /BIM-Personal/, each in a fresh context:
//   none:        no manifest, no worker;
//   manifest:    a manifest (name, short_name, start_url, scope, display standalone, 192 and 512 px PNG icons), no worker;
//   sw-nofetch:  the manifest and a worker with no fetch handler;
//   sw-fetch:    the manifest and a worker with a fetch handler.
// For each: whether beforeinstallprompt fired within 8 s (listener added in <head>, before anything else), and
// what CDP says: Page.getInstallabilityErrors and Page.getAppManifest. Run with the default launch and with
// --bypass-app-banner-engagement-checks (Chromium's switch to skip the engagement heuristic), and once with the
// full Chromium binary in its new headless mode (channel 'chromium'): in a fresh context (incognito there) and in a
// persistent profile. ONLY=<label part> runs one launch kind. RUNS runs each (default 3).
'use strict';
var C = require('./_common.js');
var pw = require('playwright');
var zlib = require('zlib');
var RUNS = +process.env.RUNS || 3;

function png(size) {   // a solid RGBA square, a valid PNG
  function crc(buf) { var c, t = [], n, k, x = 0xffffffff; for (n = 0; n < 256; n++) { c = n; for (k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
    for (n = 0; n < buf.length; n++) x = t[(x ^ buf[n]) & 255] ^ (x >>> 8); return (x ^ 0xffffffff) >>> 0; }
  function chunk(type, data) { var l = Buffer.alloc(4); l.writeUInt32BE(data.length); var td = Buffer.concat([Buffer.from(type), data]);
    var c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([l, td, c]); }
  var ih = Buffer.alloc(13); ih.writeUInt32BE(size, 0); ih.writeUInt32BE(size, 4); ih[8] = 8; ih[9] = 6; ih[10] = 0; ih[11] = 0; ih[12] = 0;
  var row = Buffer.alloc(1 + size * 4), raw = [], i;
  for (i = 0; i < size; i++) { row[1 + i * 4] = 30; row[2 + i * 4] = 120; row[3 + i * 4] = 140; row[4 + i * 4] = 255; }
  for (i = 0; i < size; i++) raw.push(row);
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ih), chunk('IDAT', zlib.deflateSync(Buffer.concat(raw))), chunk('IEND', Buffer.alloc(0))]);
}

var MANIFEST = JSON.stringify({ name: 'BIM-Personal experiment', short_name: 'BIM exp', start_url: './i/sw-fetch.html', scope: './',
  display: 'standalone', background_color: '#ffffff', theme_color: '#1e788c',
  icons: [{ src: 'icon-192.png', sizes: '192x192', type: 'image/png' }, { src: 'icon-512.png', sizes: '512x512', type: 'image/png' }] });

var HEAD = '<script>window.__bip=null;window.addEventListener("beforeinstallprompt",function(e){window.__bip={at:Math.round(performance.now()),platforms:e.platforms||null};});' +
  'window.addEventListener("appinstalled",function(){window.__installed=true;});</script>';

(async function () {
  var A = C.buildA();
  var S = await C.serve({ build: A });
  S.override('/BIM-Personal/icon-192.png', { body: png(192), type: 'image/png' });
  S.override('/BIM-Personal/icon-512.png', { body: png(512), type: 'image/png' });
  S.override('/BIM-Personal/manifest.webmanifest', { body: MANIFEST, type: 'application/manifest+json' });
  S.override('/BIM-Personal/sw-fetch.js', { body: C.probeSw('fetch', true) });
  S.override('/BIM-Personal/sw-nofetch.js', { body: C.probeSw('nofetch', false) });
  var ML = '<link rel="manifest" href="/BIM-Personal/manifest.webmanifest">';
  var variants = {
    none: { head: HEAD, sw: null }, manifest: { head: HEAD + ML, sw: null },
    'sw-nofetch': { head: HEAD + ML, sw: '/BIM-Personal/sw-nofetch.js' }, 'sw-fetch': { head: HEAD + ML, sw: '/BIM-Personal/sw-fetch.js' }
  };
  Object.keys(variants).forEach(function (k) {
    S.override('/BIM-Personal/i/' + k + '.html', { body: C.page(variants[k].sw ? 'navigator.serviceWorker.register(' + JSON.stringify(variants[k].sw) + ',{scope:"/BIM-Personal/"});' : '', variants[k].head) });
  });
  var launches = [
    { label: 'headless-shell', opts: {} },
    { label: 'headless-shell + bypass-engagement', opts: { args: ['--bypass-app-banner-engagement-checks'] } },
    { label: 'chromium new headless + bypass-engagement', opts: { channel: 'chromium', args: ['--bypass-app-banner-engagement-checks'] } },
    { label: 'chromium new headless, persistent profile + bypass-engagement', persistent: true,
      opts: { channel: 'chromium', args: ['--bypass-app-banner-engagement-checks'] } },
    { label: 'chromium new headless, persistent profile, no bypass', persistent: true, opts: { channel: 'chromium' } }
  ];
  if (process.env.ONLY) launches = launches.filter(function (l) { return l.label.indexOf(process.env.ONLY) >= 0; });
  var fs = require('fs'), path = require('path');
  var out = { runs: [] };
  for (var li = 0; li < launches.length; li++) {
    var L = launches[li], browser = null, ver = null;
    if (!L.persistent) { browser = await pw.chromium.launch(L.opts); ver = browser.version(); }
    for (var r = 0; r < RUNS; r++) {
      var row = { launch: launches[li].label, version: ver, run: r + 1, variants: {} };
      var keys = Object.keys(variants);
      for (var i = 0; i < keys.length; i++) {
        var dir = null, ctx;
        if (L.persistent) {   // a profile on disk: not incognito, which the full binary's contexts are
          fs.mkdirSync(path.join(C.SCRATCH, 'profiles'), { recursive: true });
          dir = fs.mkdtempSync(path.join(C.SCRATCH, 'profiles', 'e06-'));
          ctx = await pw.chromium.launchPersistentContext(dir, L.opts);
        } else ctx = await browser.newContext();
        var p = await ctx.newPage();
        await p.goto(S.origin + '/BIM-Personal/i/' + keys[i] + '.html');
        if (variants[keys[i]].sw) {
          await p.evaluate(function () { return navigator.serviceWorker.ready.then(function () { return 1; }); });
          await p.reload();   // so the page is controlled
        }
        await p.mouse.click(10, 10);   // one user gesture on the page
        await C.sleep(8000);
        var cdp = await ctx.newCDPSession(p);
        var ie = await cdp.send('Page.getInstallabilityErrors').catch(function (e) { return { error: e.message }; });
        var am = await cdp.send('Page.getAppManifest').catch(function (e) { return { error: e.message }; });
        row.variants[keys[i]] = {
          beforeinstallprompt: await p.evaluate(function () { return window.__bip; }),
          controlled: await p.evaluate(function () { return !!(navigator.serviceWorker && navigator.serviceWorker.controller); }),
          installabilityErrors: ie.installabilityErrors ? ie.installabilityErrors.map(function (x) { return x.errorId; }) : ie,
          manifestErrors: am.errors ? am.errors.map(function (x) { return x.message; }) : am,
          manifestUrl: am.url || null
        };
        await ctx.close();
        if (dir) fs.rmSync(dir, { recursive: true, force: true });
      }
      out.runs.push(row);
      console.log(JSON.stringify(row));
    }
    if (browser) await browser.close();
  }
  await S.stop();
  C.save('e06_install_prompt' + (process.env.ONLY ? '-' + process.env.ONLY.replace(/\W+/g, '_') : ''), out);
})().catch(function (e) { console.error(e); process.exit(1); });
