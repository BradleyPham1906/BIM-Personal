# V172h experiments: installable and offline, measured in this container's Chromium (2026-11-07)

Measured evidence (level P, for this one Chromium build only) on the hypotheses of part 15 of
`research-local-storage.md` that can be tested from here: H40, H42 to H49, and the cost of a service
worker on the app's loads. Every number below was produced by a script in
`docs/research/experiments/v172h-offline/`, run on 2026-11-07 against the real built app
(`python3 tools/build_site.py` of commit `d546f1d`), served by a local stand-in for GitHub Pages. Raw JSON was
written to the session's scratch directory, not the repository; the numbers that matter are copied here.

The service workers used are **experiment workers**, not the app's: a minimal hand-written ES5 worker for the
built app (`sw-app.template.js`) and a probe worker (`sw-probe.template.js`). Nothing in `src/` was changed;
the experiments register the worker from the driver (`page.evaluate`), since the build has no registration
code yet.

## Method and environment

### Environment

| Item | Value |
|---|---|
| Browser | Chromium build `chromium-1243` in `/opt/pw-browsers`, `browser.version()` = **153.0.8010.12** |
| Mode | **Headless**, default `chromium.launch()` (the `chromium_headless_shell-1243` binary); for H49 also the full binary in its new headless mode (`channel: 'chromium'`). No headed run was possible (no display). |
| Driver | Node v22.23.4, `require('playwright')` 1.63.0; no `playwright install` was run |
| Machine | Linux 6.18.44, 4 vCPU, 15 GiB RAM |
| Server | `_server.js`: Node `http` on `127.0.0.1`, pages opened as `http://localhost:<port>` (a secure context, so service workers run). It serves the built site under `/BIM-Personal/` as Pages does: `cache-control: max-age=600`, a strong ETag (SHA-1 of the bytes) and 304 on `If-None-Match`, a 301 from a directory without its slash, `application/javascript; charset=utf-8` for `.js`. It counts every request, keeps the headers of `sw.js` requests, can swap in a second build (`setBuild`), serve generated files at a path (`override`), and be stopped and restarted on the same port (`stop()` destroys open sockets, so the origin's server is gone: connection refused). A second "Pages project" of the same origin is served at `/Other/`. |
| Builds | **A**: `build_site.py` output, 24 MB (app 3.97 MB in four files, runtime 16.05 MB in 13 files, the guide, `canvas_v10.html`). **B**: a copy of A with one comment appended to `app/engine.js` and its `?v=` recomputed as `build_app.py` names it (first 12 hex of SHA-256), so B differs from A in one of the four URLs and in the worker's bytes (its build id). |
| Not available | **Firefox and WebKit are not installed** and were not installed: nothing here covers Firefox, Safari (macOS, iOS, iPadOS), any phone, or headed desktop Chrome. Headless may differ where the browser uses engagement heuristics or shows UI (install prompts, update banners). |

### Procedure

- Each run uses a fresh browser context (`browser.newContext()`), or where storage on disk matters (H48) a
  fresh persistent profile in a temporary directory under the scratch directory, deleted after the run.
- Times are wall-clock in the Node driver (`Date.now()`) unless said to be in the page (`performance.now()`).
- Run counts are given per experiment: 3 where the outcome is a yes/no or a byte count, 5 to 10 where it is a
  time.

### Scripts (all in `docs/research/experiments/v172h-offline/`)

| Script | Tests |
|---|---|
| `_server.js` | the stand-in for Pages (above) |
| `_common.js` | builds A and B in the scratch directory, starts the server, makes experiment pages and workers, writes results |
| `exp.js` | helpers loaded by experiment pages: registration with its events logged, a `MessageChannel` ask, `applyUpdate` (skip waiting unless dirty), controllerchange reload-once |
| `sw-app.template.js` | the experiment worker for the built app: precache, delete old caches on activate, fetch strategies |
| `sw-probe.template.js` | a probe worker that answers `/__probe` itself and records every fetch it sees |
| `e01_scope.js` | H40 (and H41's consequence for scope) |
| `e02_precache.js` | H42, H48, the precache's cost |
| `e03_offline_app.js` | H43: the real app offline, two ways, with a no-worker control |
| `e04_update.js` | H44, H45, H46: a new worker reaching one tab, two tabs, closed tabs; holding it while there is unsaved work; `sw.js` refetches |
| `e05_worker_fetch.js` | H47: fetches from a dedicated worker (script URL and `blob:`), and the real Ladybug runtime started offline |
| `e06_install_prompt.js` | H49: `beforeinstallprompt` with no manifest, a manifest, a worker without and with a fetch handler; CDP's installability errors |
| `e07_load_cost.js` | the worker's cost on first, repeat and offline loads of the real app |

### Which hypotheses held

| # | Hypothesis | Outcome |
|---|---|---|
| H40 | `/BIM-Personal/sw.js` controls `/BIM-Personal/` and every path under it, no other project | **Held**, 3 of 3 runs |
| H42 | the `?v=` URLs are usable cache keys; an old build's entries can be deleted | **Held**, 3 of 3 runs |
| H43 | the app opens offline after one visit, reads its project, saves | **Held**, 5 of 5 runs, both ways of being offline; and a finding: without a worker it also opens offline while Pages' 600 s HTTP cache is fresh |
| H44 | a waiting worker is not activated by reloading one tab while another is open; activated when every tab has closed | **Held**, 5 of 5; and stronger: **reloading even a single tab does not activate it** |
| H45 | a page can hold the waiting worker while it has unsaved work and let it in after, one reload, no loop | **Partly held**, 5 of 5: held, one reload, no loop in the tab that asked; but `skipWaiting()` swaps the worker under **every** tab, including another tab with unsaved work |
| H46 | `sw.js` checked on every navigation past Pages' `max-age=600` (`updateViaCache` "imports") | **Held**, 25 of 25 navigations; with `updateViaCache: 'all'`, 0 of 25 |
| H47 | fetches by a dedicated worker the page created (Pyodide's, a `blob:` worker) go through the service worker | **Held**, 3 of 3, for a script-URL and a `blob:` worker; the real Ladybug runtime started offline from the worker's cache, 3 of 3 |
| H48 | caches and IndexedDB counted in one origin usage | **Held** for counting (3 of 3); eviction together not testable here |
| H49 | the automatic install prompt still needs a fetch handler | **Failed**: in the full Chromium binary (new headless, a profile on disk) `beforeinstallprompt` fired with a manifest and **no worker at all**, 3 of 3, with and without the engagement bypass; the headless shell never fires it |

---

## H40. The worker's scope

### Hypothesis
A worker at `/BIM-Personal/sw.js`, registered with no `scope` option, controls `/BIM-Personal/` and every path
under it (`docs/`, `v/x/`), and does not control another Pages project of the same account (same origin,
`/Other/`).

### Method
`e01_scope.js`. The probe worker is served at `/BIM-Personal/sw.js` and registered from `/BIM-Personal/reg.html`;
after `navigator.serviceWorker.ready`, the page is navigated to each address in turn and reports whether it is
controlled (`navigator.serviceWorker.controller`) and whether a `fetch('/BIM-Personal/__probe')` was answered by
the worker. The same page also tries `register('/BIM-Personal/sw.js', {scope: '/'})`, and a worker at
`/BIM-Personal/docs/sw2.js` is registered from a page in `docs/` with no scope. 3 runs, each a fresh context.

### Raw results (identical in runs 1, 2 and 3)

| Address navigated to | Final address | Controlled | `__probe` answered by the worker |
|---|---|---|---|
| `/BIM-Personal/` (the real app) | same | yes | yes |
| `/BIM-Personal/reg.html` | same | yes | yes |
| `/BIM-Personal/docs/` | same | yes | yes |
| `/BIM-Personal/docs/bim.html` | same | yes | yes |
| `/BIM-Personal/v/x/` | same | yes | yes |
| `/BIM-Personal` (no slash; the server answers 301) | `/BIM-Personal/` | yes | yes |
| `/Other/` | same | **no** | no (404 from the server) |
| `/BIM-Personalx/` | same | **no** | no |

- Registered scope with no option: `http://localhost:<port>/BIM-Personal/` (3 of 3).
- `scope: '/'` without a `Service-Worker-Allowed` header: refused, 3 of 3, `SecurityError`: "The path of the
  provided scope ('/') is not under the max scope allowed ('/BIM-Personal/'). Adjust the scope, move the Service
  Worker script, or use the Service-Worker-Allowed HTTP header to allow the scope."
- A worker at `docs/sw2.js` registered with no scope gets `/BIM-Personal/docs/` (3 of 3); both registrations then
  exist side by side.

### Outcome
**Held.** The default scope is the script's folder with its trailing slash; the match is a string prefix, so
`/BIM-Personalx/` is outside it and `/Other/` is untouched. The redirect from `/BIM-Personal` lands controlled.

### Threats to validity
- On Pages the redirect from `/BIM-Personal` to `/BIM-Personal/` is Pages' own; here it is the stand-in's 301, and
  Pages' answer was not measured from this container. The worker sees only the second navigation either way.
- A worker in `docs/` would be a second registration with its own caches; the app's design should keep exactly
  one worker, at the root of the project.

## H42. The `?v=` URLs as cache keys, and deleting an old build

### Hypothesis
The Cache API matches the full URL with its query by default, so the build's four files can be precached by the
exact URLs the page asks for (`app/<name>?v=<12 hex>`), and an old build's entries found and deleted.

### Method
`e02_precache.js`. The real app is opened at `/BIM-Personal/`, then the experiment worker for build A is
registered. Its install fetches `./` and the four `?v=` URLs that `index.html` names, with `cache: 'reload'`, into
the cache `bim-app-<build id>`. The page then lists the cache's entries and tries `cache.match` with the exact URL,
without its query, without its query but `{ignoreSearch: true}`, and with another hash. Then build B is deployed
(its worker, for this test, calls `skipWaiting()`), `registration.update()` is called and the driver waits until
A's cache is gone. 3 runs, each a fresh persistent profile.

### Raw results (identical in runs 1, 2 and 3)
- Cache entries after install: `/BIM-Personal/`, `/BIM-Personal/app/shell.js?v=7165cc6791ef`,
  `/BIM-Personal/app/app.css?v=2d05535e505b`, `/BIM-Personal/app/openskp.js?v=12816bb78193`,
  `/BIM-Personal/app/engine.js?v=482241c9cce3`: the page's own URLs, query kept.
- `cache.match(exact URL)`: hit. Without the query: **miss**. Without the query, `ignoreSearch: true`: hit. Same
  path with another hash: **miss**. `caches.match(exact URL)` across all caches: hit.
- After B activated: `caches.keys()` = `bim-exp-meta`, `bim-runtime-v1`, `bim-app-e8dd0181` (B). A's
  `bim-app-0a4f9f99` was deleted and the runtime cache kept, 3 of 3. From `update()` to A's cache gone:
  1344, 1364, 1351 ms (this includes B's own precache of its five files).

### Outcome
**Held.** The `?v=` names need no rewriting: the precache list is exactly what `index.html` names, a stale hash
never matches, and naming the cache after the build lets activate delete every other build's cache by name
while leaving the runtime's cache alone.

### Threats to validity
- B differed from A in one file; a real deploy differs in up to four, which changes only the bytes fetched.
- The worker matched by `Request` URL only; `Vary` headers were not involved (the server sends none, nor does
  Pages for these files, as far as part 15.7 read; not re-measured on Pages).

## H43. The real app offline after one online visit

### Hypothesis
After one online visit (the worker installed), the app opens with no network, its project saved before going
offline reads back from IndexedDB, and an edit saves, with no page error but third-party fetches' own.

### Method
`e03_offline_app.js`. Per run, a fresh context: open `/BIM-Personal/` online, wait for the store to open
(`__a3dStore().mode`), register the experiment worker and wait for `ready`, draw a wall (`__a3dWall`), wait 1.5 s
and check the wall is in the stored record (`__a3dStoredGet(<active project>)`). Then three offline visits in
turn, each a `page.goto('/BIM-Personal/')`:

1. **emulated, HTTP cache fresh**: `context.setOffline(true)` (Chromium's network emulation), straight after the
   online visit, so the browser's HTTP cache still holds the page and the four files under Pages' `max-age=600`;
2. **emulated, HTTP cache cleared**: the same after CDP `Network.clearBrowserCache` (it empties the HTTP cache and
   leaves Cache Storage alone): the state of a visit more than 600 s later;
3. **server stopped, HTTP cache cleared**: the browser online, the server's port closed (connection refused).

On each: is the page controlled, is the same project active, is the first wall on screen, then a second wall is
drawn and, 1.5 s later, is it in the stored record. Page errors, console errors and failed requests are logged.
The **control** repeats every step with no worker registered. 5 runs of each.

### Raw results

| Visit | With the worker: opened, project, wall read back, edit saved (runs 1-5) | Time from `goto` to the store open, ms (runs 1-5) | Without a worker (control) |
|---|---|---|---|
| 1. emulated, HTTP cache fresh | 5 of 5 yes, controlled | 80, 84, 80, 70, 70 | **5 of 5 opened too** (52, 69, 59, 56, 54 ms), read back and saved |
| 2. emulated, HTTP cache cleared | 5 of 5 yes, controlled | 76, 82, 73, 73, 65 | 5 of 5 failed: `net::ERR_INTERNET_DISCONNECTED` |
| 3. server stopped, HTTP cache cleared | 5 of 5 yes, controlled | 63, 66, 71, 71, 97 | 5 of 5 failed: `net::ERR_CONNECTION_REFUSED` |

- Page errors: **0**; console errors: **0**; failed requests with the worker: **0** in every visit of every run.
  The app's boot makes no third-party request at all (none was logged online either), so there were no
  third-party failures to list. After every edit `__a3dStore()` read `{mode: 'idb', v2: true, newer: false,
  dirty: false, inflight: false}`.
- In a first single trial (not counted above), visit 2 took 364 ms; in the 5 counted runs 65 to 82 ms.

### Outcome
**Held**, 5 of 5, both ways of being offline. Nothing in the app had to change: the app's own storage is
IndexedDB and works offline as it does online.

### Inferences
- **Without any worker the app already opens offline for 600 s after a visit**, from the HTTP cache (Pages'
  `max-age=600`). The worker matters for every later visit: after the HTTP cache has expired (simulated by
  clearing it), only the worker made the page open.
- The worker's navigation strategy here is network first: offline in Chromium's emulation and with a refused
  connection the network fails at once, so the fallback is fast. A network that hangs (captive portal, weak
  signal) would make a network-first navigation wait for its timeout; that case was not tested (see threats).

### Threats to validity
- Offline was emulated or the server was stopped; a real radio off, a captive portal and a slow network were not
  tested. Clearing the HTTP cache stands in for its expiry.
- Only the app's boot, one wall and its save were exercised; tools that fetch third-party data (the map, Overpass,
  Open-Meteo) were not opened offline. They are cross-origin and the worker leaves them to the network, so they
  fail as they do with no connection today.
- The guide pages (`docs/`) were not precached; the experiment worker's navigation fallback answers any
  navigation it cannot fetch with the app's page, which would show the app for a guide address offline. A real
  worker should fall back to the app's page only for the app's own address.

## H44. Does a waiting worker activate on reload, with one tab and with two?

### Hypothesis
A new worker left waiting (no `skipWaiting()`) is not activated by reloading one tab while another tab of the app
is open, and is activated when every tab has closed.

### Method
`e04_update.js`, the probe worker (no `skipWaiting()` of its own; build A's worker says `A`, B's `B`; the files
differ only in that string). Pages are `/BIM-Personal/t.html` with `exp.js`. In each scenario A is registered and
the tab reloaded so A controls it, then B is deployed (the server answers `sw.js` with B's bytes). State is read
from the page: the version the controller, the active and the waiting worker answer by `MessageChannel`.

- **One tab**: reload (the navigation's update check finds B); reload again; navigate the tab to `/Other/` (out of
  scope) and back; close the tab and open a new one.
- **Two tabs**: tab 1 reloads twice; tab 2 is closed; tab 1 reloads; tab 1 is closed and a new tab opened.

5 runs of each, each a fresh context.

### Raw results (controller / waiting, identical in runs 1 to 5)

| Step | One tab | Step | Two tabs |
|---|---|---|---|
| first reload after B deployed | A / B | tab 1, first reload | A / B |
| second reload | **A / B** | tab 1, second reload | A / B (tab 2: A / B) |
| tab navigated to `/Other/` and back | **B / none** | tab 2 closed, tab 1 reloaded | **A / B** |
| tab closed, a new tab opened | B / none | tab 1 closed, a new tab opened | **B / none** |

- Time from the navigation's start to `updatefound` in the page (`performance.now()`), one-tab scenario:
  **1557, 1549, 1550, 1544, 1546 ms**; B reached `installed` within 1 ms of `updatefound` (B is tiny).

### Outcome
**Held, and stronger than the hypothesis.** A reload never activated the waiting worker, not even in a lone tab:
during a reload the old page is still a client of A until the new one commits, so A is never without clients.
B was activated only when the last client of A went away: the tab navigated out of scope (`/Other/`), or every
tab closed. For the app this means a user who only ever reloads one tab would keep the old build indefinitely
unless the page asks the waiting worker to take over (H45).

### Threats to validity
- Headless, driven by Playwright; a real user closing a browser window, or a phone's browser discarding a
  backgrounded tab, was not tested. Whether Chromium counts a tab in the back-forward cache as a client was not
  tested.
- The ~1.55 s from navigation to `updatefound` is this machine on loopback; the check itself is made by the
  browser after the navigation, so its delay is the browser's (see H46 for when the request leaves).

## H45. Holding the waiting worker while there is unsaved work

### Hypothesis
A page can hold a waiting worker back while it has unsaved work and let it in after, by messaging it, without a
second reload or a reload loop.

### Method
`e04_update.js`, scenario "message". Two tabs controlled by A; tab 2 marks itself as having unsaved work
(`window.__dirty = true`). B is deployed and tab 1 reloads (B waits). Tab 1 marks itself dirty and calls
`__applyUpdate()` (in `exp.js`: if dirty, do nothing and say so; else post `{type: 'SKIP_WAITING'}` to
`registration.waiting`, which calls `self.skipWaiting()`). Then tab 1 becomes clean and calls it again. Each page
reloads itself on `controllerchange` once (a guard flag) unless it is dirty, and counts its reloads in
`sessionStorage`. 3 s after the reload the count is read again. 5 runs.

### Raw results (identical in runs 1 to 5 unless given)
- Tab 1 dirty: `__applyUpdate()` returned "held: unsaved work"; 0.8 s later still A / B (5 of 5).
- Tab 1 clean: "asked"; tab 1 reloaded once and came back controlled by B; time from the ask to the reload's
  `load`: **1021, 1023, 1024, 1023, 1024 ms**. Reload count 1, and still **1 after 3 s** (no loop), 5 of 5.
- **Tab 2 (dirty, not asked)**: got `controllerchange` (5 of 5), did not reload (its own guard), still had its
  unsaved work, and its controller was **B**: a fetch it made afterwards was answered by B (5 of 5).

### Outcome
**Partly held.** Within one tab the pattern works: hold while dirty, `skipWaiting()` by message, one reload on
`controllerchange`, no loop. But `skipWaiting()` acts on the registration, not the tab: every other open tab is
moved to the new worker at once, whatever its state. A tab with unsaved work keeps running build A's code under
build B's worker; it does not lose its work (nothing reloads it), but every later request it makes is answered by
B, and B's activate has already deleted A's cache.

### Inferences
- The "no unsaved work" check has to cover every tab of the app before any tab asks the worker to skip waiting
  (for example by asking the other tabs over a `BroadcastChannel` and waiting for their answers, or letting
  only an all-clean state proceed). V172f's tab locks know which tabs exist; this was not tested here.
- A tab left on old code under the new worker is safe for this app only while it never needs a file of its own
  build after boot: the build loads its four files at boot and fetches nothing else of its own except `runtime/`
  (in its own cache, not deleted by activate) and the guide pages. This is an inference from part 15.7, not tested.

### Threats to validity
- The dirty flag here is an experiment variable, not V172g's marker; the app's own signal was not used.
- The "reload once" guard is per page load; a page that reloads into a state where it is again told to apply an
  update could still loop if its code asked every time. Only this one design was measured.

## H46. `sw.js` refetched on navigation, past Pages' 600 s HTTP cache

### Hypothesis
The browser checks `sw.js` for an update on every navigation, ignoring Pages' `max-age=600`, because
`updateViaCache` is `"imports"` by default.

### Method
`e04_update.js`, scenario "hits". A controls one tab (registered with no options, then with
`{updateViaCache: 'all'}` in a second context); after 4 s the server's counters are reset and the tab navigates
to its own page 5 times, 4 s apart, all well inside the 600 s `max-age` of the `sw.js` it fetched. Every request
for `sw.js` is logged with its headers and put down to the last navigation started before it. 5 runs of each.

### Raw results
- Registered with no option: `registration.updateViaCache` = `"imports"`; **5 requests for 5 navigations**, in
  every run (25 of 25). Each request had `Cache-Control: max-age=0`, an `If-None-Match` (so the server answered
  304) and `Service-Worker: script`. Time from the navigation's start (driver clock) to the request:
  run 1: 1933, 2007, 2008, 2009, 2009 ms; run 2: 1921, 2008, 2012, 2012, 2011; run 3: 1921, 2007, 2010, 2009, 2012;
  run 4: 1928, 2010, 2011, 2010, 2007; run 5: 1931, 2012, 2011, 2007, 2009.
- Registered with `updateViaCache: 'all'`: `"all"`; **0 requests for 25 navigations** (the HTTP cache answered).

### Outcome
**Held.** With the default, every navigation to a controlled page revalidates `sw.js` with the server, about 2 s
after the navigation starts, whatever Pages' `max-age` says; the cost is one conditional request answered 304.
The 24-hour rule (an update forced when the last check is older) was not tested: it needs a clock 24 h ahead.

### Threats to validity
- 4 s between navigations; Chromium may coalesce checks closer together (not tested). The ~2 s delay after
  navigation is consistent across runs but its cause in Chromium was not read (U).
- Pages answers conditional requests too (part 15.7 recorded an ETag), so the 304 path applies there; not
  measured from here.

## H47. Fetches from a dedicated Web Worker the page created

### Hypothesis
Fetches made by a dedicated Web Worker that the page created (Pyodide's, made from a `blob:` URL) go through the
page's service worker, so the Ladybug runtime can be served from a cache offline.

### How the app makes its worker (read 2026-11-07)
`src/js/engine/ladybug/runtime.js` `bimLbStart()` (lines 147-175): `new Worker(URL.createObjectURL(new Blob([txt],
{type: 'text/javascript'})))`, where `txt` is the text of its own functions; the worker then `importScripts()`
`pyodide.js` and `fetch()`es the wheels from `bimLbBase()`. Over http(s) `bimLbBase()` (lines 30-35) is **the
page's own folder plus `runtime/`** (same origin on Pages: `/BIM-Personal/runtime/`); the absolute Pages address
`BIM_LB_PAGES` is used only from `file://` or a page under `v/`. So on Pages the runtime is same-origin and inside
the worker's scope.

### Method
`e05_worker_fetch.js`. Part 1, the probe worker: a page creates (a) a worker from a script URL
(`/BIM-Personal/wk.js`) and (b) a `blob:` worker made as `runtime.js` makes its own; each calls
`importScripts('/BIM-Personal/__probe?as=js')` and `fetch('/BIM-Personal/__probe')` (absolute URLs, since a `blob:`
worker's base is the `blob:` URL). The probe worker answers both itself, so an answer naming its version proves it
went through. The same is done from the page before it is controlled (control). Part 2, the real app: the
experiment worker (`runtime/` cache first) is registered, the page reloaded so it is controlled, and the runtime
started with `__a3dLbStart()` (Pyodide 0.29.5 and five wheels, in the app's `blob:` worker); then the HTTP cache is
cleared, the server stopped, the app reloaded offline and `__a3dLbStart()` called again. 3 runs of each part.

### Raw results
- Part 1, controlled page, 3 of 3 runs: for **both** workers, `importScripts` was answered by the worker
  (`destination: 'script'`, `mode: 'no-cors'`) and `fetch` too (`destination: ''`, `mode: 'cors'`). The worker
  also saw the script-URL worker's own script request (`/BIM-Personal/wk.js`, `destination: 'worker'`). A `blob:`
  worker's own script is not fetched, so there is nothing for the worker to see.
- Part 1, uncontrolled page (control), 3 of 3: both workers' `fetch` reached the server (its 404) and
  `importScripts` failed to load: nothing intercepted.
- Part 2: `__a3dLbBase()` = `http://localhost:8174/BIM-Personal/runtime/` (3 of 3). Online start: **ready** in
  2530, 2607, 2558 ms (driver) / 2519, 2596, 2545 ms (the app's own count), with **10** requests to `runtime/` at
  the server and 10 entries in the runtime cache: `pyodide.js`, `pyodide-lock.json`, `pyodide.asm.js`,
  `python_stdlib.zip`, `pyodide.asm.wasm` and the five wheels. Offline start (server stopped, HTTP cache cleared,
  page reloaded offline): **ready** in 2496, 2535, 2572 ms / 2482, 2521, 2561 ms, versions identical
  (ladybug-core 0.44.63, ladybug-comfort 0.19.13, ladybug-geometry 1.35.7, ladybug-radiance 0.2.12, Pyodide
  0.29.5). Page errors: 0.

### Outcome
**Held**, for a script-URL and a `blob:` worker (Chromium gives a `blob:` worker its creator's controller), and
end to end: the real runtime started offline from the worker's cache, 3 of 3, as fast as online over loopback.

### Inferences
- The runtime needs no change to work offline; the worker only has to keep `runtime/` (cache first fits: the
  files are pinned in `MANIFEST.json`, Pyodide's under a versioned folder `pyodide/0.29.5/`, and the app's worker
  checks each wheel's SHA-256 after fetching it, `runtime.js:51-54`; Pyodide's own files are not hash-checked by the app).
- Radiance's `gendaymtx.wasm` (115 KB) is fetched only on the first study (`runtime.js:23-24`), so it was not in
  the cache after a start alone: an offline study needs it fetched once online, or precached with the runtime.
  The `numpy` wheel (2.8 MB) was not fetched by a start either (`numpy: null` in the versions).
- From a `file://` copy the base is the absolute Pages address, which no service worker can serve to a
  `file://` page: the one-file build's runtime stays online-only.

### Threats to validity
- That a `blob:` worker inherits its creator's controller is the current spec's rule; older engines did not do
  this (part 15's standards note has the compat data). Safari and Firefox were not tested here.

## H48. Caches and IndexedDB in one origin quota

### Hypothesis
The worker's caches are counted in the same origin usage and quota as IndexedDB (one storage bucket), so caching
the app adds no eviction case of its own.

### Method
`e02_precache.js`, same runs as H42. `navigator.storage.estimate()` (with `usageDetails`) is read: after the app
has booted with no worker (0); after the precache (1); after the page, now controlled, fetched the 13 runtime
files through the worker, which caches them in `bim-runtime-v1` (2); after a 10 MiB ArrayBuffer was put into an
IndexedDB database of the same origin (3); after build B replaced A's cache (4).

### Raw results (identical in runs 1, 2 and 3; bytes)

| Point | usage | caches | indexedDB | serviceWorkerRegistrations |
|---|---|---|---|---|
| 0: app booted, no worker | 32,268 | (absent) | 32,268 | (absent) |
| 1: after the precache | 8,815,021 | 8,778,752 | 32,268 | 4,001 |
| 2: after the runtime through the worker | 24,996,549 | 24,846,080 | 146,468 | 4,001 |
| 3: after a 10 MiB IndexedDB value | 25,489,895 | 24,846,080 | 639,814 | 4,001 |
| 4: after build B replaced A | 25,490,406 | 24,846,592 | 639,814 | 4,000 |

- `quota`: 10,737,450,508 in every reading (the fixed headroom experiments.md H3 found for a persistent
  headless profile).
- `usage` is the sum of the three details in every reading: one figure for the origin.
- The precache fetched 3,970,631 bytes of bodies (the worker's own count; the server sent 3,974,632 bytes during
  install), but the cache grew by 8,778,752 bytes. The runtime's 16,050,897 bytes grew it by 16,067,328.

### Outcome
**Held for counting**: caches, IndexedDB and the registration are reported as one origin usage under one quota.
Whether they are **evicted together** cannot be tested here (it needs storage pressure on a real disk, and
`persist()` behaves differently headless, experiments.md H4); it rests on the Storage Standard's one bucket per
origin (part 15's standards note), level S for this claim.

### Inferences
- The app adds about 8.8 MB of cache per build installed, and 16 MB more if the runtime is cached; at any
  moment one build's cache is kept (activate deletes the others), so the steady cost is about 25 MB with the
  runtime.
- The precache's cache is about 2.2 times its bodies (8.78 MB for 3.97 MB), while the runtime's is about 1 times.
  The likely reason is V8's code cache, which Chromium stores beside scripts cached during a worker's install;
  that is an inference, not measured here (the runtime's scripts were cached outside install).
- The 10 MiB IndexedDB value added only 493,346 bytes: the value was mostly zeros and Chromium compresses large
  IndexedDB values; a project's real usage will be closer to its size.

### Threats to validity
- The quota is headless-specific (fixed headroom), so these numbers say nothing of real eviction thresholds.

## Cost of the precache on a first visit

From `e02_precache.js`, 3 runs (each a profile on disk): the install fetched five files, 3,970,631 bytes, in
**342, 357, 345 ms** inside the worker (from install start to the last `cache.put`); from `register()` to
`navigator.serviceWorker.ready` in the driver: **364, 376, 366 ms**. Fetching the 13 runtime files (16,050,897
bytes) through the worker into its cache: 246, 201, 233 ms. All over loopback; e07 below has the loads.

## H49. The install prompt, headless, with and without a fetch handler

### Hypothesis
Chrome's automatic install prompt (`beforeinstallprompt`) still needs a service worker with a fetch handler in
current Chromium (left open by part 10).

### Method
`e06_install_prompt.js`. Four pages under `/BIM-Personal/i/`, each in a fresh context or profile: **none** (no
manifest, no worker); **manifest** (`<link rel="manifest">` to a manifest with `name`, `short_name`, `start_url`,
`scope`, `display: standalone`, `background_color`, `theme_color`, and 192 and 512 px PNG icons generated by the
script); **sw-nofetch** (the manifest and a worker with no fetch handler, the page reloaded so it is controlled);
**sw-fetch** (the same with a fetch handler). A `beforeinstallprompt` listener is added first thing in `<head>`; one
click on the page; after 8 s the page reports whether the event fired, and CDP is asked
`Page.getInstallabilityErrors` and `Page.getAppManifest`. Four launch kinds, 3 runs of each:

1. the default headless shell, a fresh context;
2. the same with `--bypass-app-banner-engagement-checks`;
3. the full Chromium binary in its new headless mode (`channel: 'chromium'`), a fresh context, with the bypass;
4. the full binary with a persistent profile on disk (`launchPersistentContext`), with the bypass, and again
   without it.

### Raw results (identical in runs 1, 2 and 3 of each)

| Launch | none | manifest | sw-nofetch | sw-fetch |
|---|---|---|---|---|
| 1. headless shell | no event; errors `[]` | no event; `[]` | no event; `[]` | no event; `[]` |
| 2. headless shell, bypass | no event; `[]` | no event; `[]` | no event; `[]` | no event; `[]` |
| 3. full binary, fresh context, bypass | no event; `in-incognito`, `no-manifest` | no event; `in-incognito` | no event; `in-incognito` | no event; `in-incognito` |
| 4a. full binary, profile on disk, bypass | no event; `no-manifest` | **fired** at 48, 53, 54 ms | **fired** at 45, 29, 33 ms | **fired** at 37, 42, 50 ms |
| 4b. full binary, profile on disk, no bypass | no event; `no-manifest` | **fired** at 60, 74, 56 ms | **fired** at 33, 32, 34 ms | **fired** at 49, 36, 42 ms |

- Times are the page's `performance.now()` when the event fired (from the start of the navigation; for the worker
  pages, the reload). `e.platforms` was `["web"]` every time it fired. `Page.getAppManifest` reported no manifest
  errors in any run.
- The headless shell reports no installability errors and never fires the event: it has no install support to
  report on. The full binary's fresh contexts are incognito, where install is refused (`in-incognito`).

### Outcome
**Failed** (the hypothesis is false in this Chromium): with a valid manifest and its icons, `beforeinstallprompt`
fired with **no service worker at all**, and with a worker that has no fetch handler, in 3 of 3 runs each. A
fetch handler is not needed for the prompt in Chromium 153.

### Threats to validity
- Headless, under automation: Chromium's engagement heuristic did not hold the event back even without the bypass
  switch, which a real user's first visit may not see the same way. Whether the browser's own install UI (the
  address bar icon, the menu item) appears cannot be seen headless.
- The persistent-context runs do not report `browser.version()` (Playwright gives no browser object for them);
  the binary is the same `chromium-1243` build, whose version experiments.md recorded as 153.0.8010.12.
- Offline use still needs the worker (H43); this only says the prompt does not.

## Cost on the app's loads, with and without the worker

### Method
`e07_load_cost.js`, the real app, 7 runs, each a fresh context per arm. **No worker**: first load; repeat load (a
new `goto`, the HTTP cache fresh); repeat after clearing the HTTP cache (CDP). **With the worker**: first load, then
`register()` and wait for `ready` (the precache); repeat load (controlled); repeat after clearing the HTTP cache;
offline (server stopped, HTTP cache cleared). Per load: the navigation entry's `loadEventEnd` (ms from the
navigation's start), the driver's time from `goto` to the store open, bytes the server sent (bodies), and for the
four app files their `transferSize` and whether a worker handled them (`workerStart > 0`).

### Raw results (ms; runs 1-7, then the median)

| Load | `loadEventEnd` | median | `goto` to store open | median | server bytes |
|---|---|---|---|---|---|
| no worker, first | 114, 202, 99, 101, 92, 109, 101 | 101 | 177, 269, 161, 160, 150, 169, 168 | 168 | 3,970,631 |
| no worker, repeat (HTTP cache fresh) | 32, 42, 36, 31, 30, 30, 31 | 31 | 43, 48, 42, 43, 34, 35, 37 | 42 | 0 |
| no worker, repeat, HTTP cache cleared | 93, 77, 113, 197, 111, 89, 208 | 111 | 99, 152, 119, 210, 117, 93, 224 | 119 | 3,970,631 |
| worker, first (not yet controlled) | 118, 101, 104, 216, 101, 119, 209 | 118 | 181, 160, 164, 283, 163, 182, 273 | 181 | 3,970,631 |
| worker, precache after the first load | (`register` to `ready`) 353, 333, 317, 322, 327, 348, 329 | 329 | | | 3,974,632 |
| worker, repeat (controlled, HTTP cache fresh) | 68, 54, 62, 63, 72, 60, 63 | 63 | 72, 59, 68, 68, 79, 65, 70 | 68 | 0 |
| worker, repeat, HTTP cache cleared | 46, 50, 48, 49, 54, 53, 50 | 50 | 53, 55, 53, 53, 60, 58, 54 | 54 | 442 (the page only) |
| worker, offline (server stopped, HTTP cache cleared) | 57, 49, 59, 60, 55, 50, 51 | 55 | 63, 55, 67, 79, 73, 61, 55 | 63 | 0 |

- Controlled loads: all four app files had `workerStart > 0` and `transferSize` 0 (answered by the worker from its
  cache). The page itself came from the HTTP cache (fresh) or the server (442 bytes, the build's `index.html`).
- The precache fetched 3,974,632 bytes: the four files and the page again (3,970,631) plus `sw.js` (4,001).

### Outcome and inferences
- **First visit**: the same load time as today (the worker is registered after the load), plus a precache of
  about 330 ms on loopback that **downloads the app a second time** (3.97 MB), because the experiment worker
  fetches with `cache: 'reload'`. Fetching with the HTTP cache allowed (the files are named by their hash, so a
  cached copy is the right one) would avoid most of that second download; not measured here.
- **Repeat visit inside Pages' 600 s**: the worker made the load slower here, a median of 63 ms against 31 ms with
  no worker (the HTTP cache alone is faster than the worker answering four files from Cache Storage).
- **Repeat visit after the HTTP cache is gone**: 50 ms with the worker (442 bytes over the network) against 111
  ms and 3.97 MB without; on a real network the difference is the 3.97 MB download.
- **Offline**: 55 ms, no bytes.

### Threats to validity
- Loopback: network time is near zero, so these numbers show the browser's own costs, not a user's network.
  Clearing the HTTP cache overstates a no-worker repeat after 600 s: a real browser keeps the stale entries and
  sends conditional requests (304s, a few hundred bytes each) instead of refetching 3.97 MB; that case was not
  simulated.
- The worker was probably still running between loads seconds apart; a cold worker start (after the browser
  stops an idle worker) was not measured.
- One machine, 7 runs; spreads are given in the raw numbers.

## Not measured here, and why

- **H41** (Pages' headers and MIME type for `sw.js`): needs Pages itself; this container's network was not used
  for it. Measured here only its consequence: without `Service-Worker-Allowed` the scope cannot be widened (H40).
- **H48's eviction half**: whether caches and IndexedDB are evicted together needs real storage pressure.
- **H50** (iOS and iPadOS icons), **H51** (`display: standalone` on phones and tablets), **H52** (tile terms):
  no Safari, no phone, and H52 is a question of terms, not behaviour.
- **The 24-hour update rule** (H46's second half): needs the clock moved 24 h; not attempted.
- **Firefox and Safari**: not installed; every outcome here is for Chromium 153 only.
