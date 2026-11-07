# V172h experiments: installable and offline, measured in this container's Chromium (2026-11-07)

Measured evidence (level P, for this one Chromium build only) on the hypotheses of part 14 of
`research-local-storage.md` that can be tested from here: H29, H31 to H38, and the cost of a service
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
| Mode | **Headless**, default `chromium.launch()` (the `chromium_headless_shell-1243` binary). No headed run was possible (no display). |
| Driver | Node v22.23.4, `require('playwright')` 1.63.0; no `playwright install` was run |
| Machine | Linux 6.18.44, 4 vCPU, 15 GiB RAM |
| Server | `_server.js`: Node `http` on `127.0.0.1`, pages opened as `http://localhost:<port>` (a secure context, so service workers run). It serves the built site under `/BIM-Personal/` as Pages does: `cache-control: max-age=600`, a strong ETag (SHA-1 of the bytes) and 304 on `If-None-Match`, a 301 from a directory without its slash, `application/javascript; charset=utf-8` for `.js`. It counts every request, keeps the headers of `sw.js` requests, can swap in a second build (`setBuild`), serve generated files at a path (`override`), and be stopped and restarted on the same port (`stop()` destroys open sockets, so the origin's server is gone: connection refused). A second "Pages project" of the same origin is served at `/Other/`. |
| Builds | **A**: `build_site.py` output, 24 MB (app 3.97 MB in four files, runtime 16.05 MB in 13 files, the guide, `canvas_v10.html`). **B**: a copy of A with one comment appended to `app/engine.js` and its `?v=` recomputed as `build_app.py` names it (first 12 hex of SHA-256), so B differs from A in one of the four URLs and in the worker's bytes (its build id). |
| Not available | **Firefox and WebKit are not installed** and were not installed: nothing here covers Firefox, Safari (macOS, iOS, iPadOS), any phone, or headed desktop Chrome. Headless may differ where the browser uses engagement heuristics or shows UI (install prompts, update banners). |

### Procedure

- Each run uses a fresh browser context (`browser.newContext()`), or where storage on disk matters (H37) a
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
| `e01_scope.js` | H29 (and H30's consequence for scope) |
| `e02_precache.js` | H31, H37, the precache's cost |
| `e03_offline_app.js` | H32: the real app offline, two ways, with a no-worker control |

### Which hypotheses held

| # | Hypothesis | Outcome |
|---|---|---|
| H29 | `/BIM-Personal/sw.js` controls `/BIM-Personal/` and every path under it, no other project | **Held**, 3 of 3 runs |
| H31 | the `?v=` URLs are usable cache keys; an old build's entries can be deleted | **Held**, 3 of 3 runs |
| H32 | the app opens offline after one visit, reads its project, saves | **Held**, 5 of 5 runs, both ways of being offline; and a finding: without a worker it also opens offline while Pages' 600 s HTTP cache is fresh |
| H37 | caches and IndexedDB counted in one origin usage | **Held** for counting (3 of 3); eviction together not testable here |

---

## H29. The worker's scope

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

## H31. The `?v=` URLs as cache keys, and deleting an old build

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
  Pages for these files, as far as part 14.7 read; not re-measured on Pages).

## H32. The real app offline after one online visit

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

## H37. Caches and IndexedDB in one origin quota

### Hypothesis
The worker's caches are counted in the same origin usage and quota as IndexedDB (one storage bucket), so caching
the app adds no eviction case of its own.

### Method
`e02_precache.js`, same runs as H31. `navigator.storage.estimate()` (with `usageDetails`) is read: after the app
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
origin (part 14's standards note), level S for this claim.

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

From `e02_precache.js`, 3 runs: install with five files fetched, 3,970,631 bytes: **342, 357, 345 ms** inside the
worker (from install start to the last `cache.put`); from `register()` to `navigator.serviceWorker.ready`
in the driver: **364, 376, 366 ms**. Fetching the 13 runtime files (16,050,897 bytes) through the worker into its
cache: 246, 201, 233 ms. All over loopback: on a real network the time is set by the bandwidth (about 4 MB more
on the first visit, fetched once more because of `cache: 'reload'` even though the page has just loaded the same
files; see the load-cost section for the second fetch's effect).
