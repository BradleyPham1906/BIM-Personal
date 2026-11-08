# Independent check, V172h (installable and offline)

Date: 2026-11-08

Method: every source was read as text from a scratch folder outside the repository; nothing downloaded was run.
The specifications were fetched again at the pinned commits from raw.githubusercontent.com and compared byte for
byte with the copies an earlier, interrupted reader had saved (identical: Service Workers @57dfd24, Storage @115691c,
Manifest @7eaf743). Line numbers below are of those files. Short names: SW = w3c/ServiceWorker@57dfd24 `index.bs`;
ST = whatwg/storage@115691c `storage.bs`; MF = w3c/manifest@7eaf743 `index.html` (reduced to text).

## Facts

| # | Fact | Source re-read | Result | Note |
|---|---|---|---|---|
| F1 | Without `Service-Worker-Allowed` the maximum scope is the script's folder; a scope outside it rejects with SecurityError | SW 2835-2851 (Update: `maxScopeString` from `./` against the script URL; "does not start with" rejects SecurityError) | Confirmed | Also e01's raw results: `scope:'/'` refused with SecurityError, 3 of 3; `/BIM-Personalx/` and `/Other/` uncontrolled. |
| F2 | `sw.js` must be a JavaScript MIME type and is fetched with redirect mode "error" | SW 2823, 2825 | Confirmed | |
| F3 | Cache matching keeps the query unless `ignoreSearch` (default false); fragment excluded; GET only; `Vary` compared unless `ignoreVary` | SW 2021 (default false), 4093-4104 (Request Matches Cached Item) | Confirmed | |
| F4 | `sw.js` revalidated (`no-cache`) unless `updateViaCache` is "all"; default "imports"; "stale" is 86,400 s | SW 747 (default "imports"), 2814-2819, 281 | Confirmed | Note at 2819: without `no-cache` the network layer still obeys max-age. |
| F5 | Every non-subresource request (navigation) runs Soft Update; subresources only when stale | SW 3274-3276, 3283-3286 | Confirmed | |
| F6 | A new worker counts as updated only if not byte-for-byte identical | SW 2855-2858, 2892 | Confirmed | So the build id in `sw.js` is required. |
| F7 | A waiting worker activates only when no client uses the registration, or its skip-waiting flag is set; retried on last client unload or `skipWaiting()` | SW 3073 (Try Activate), 3013 (note), 1139-1140 (`skipWaiting()` sets the flag, Try Activate) | Confirmed | |
| F8 | On activate every client using the registration gets the new active worker (`skipWaiting()` affects every tab) | SW 3042-3044 (Activate: "For each service worker client who is using registration", Notify Controller Change); 1134 note ("even while service worker clients are using") | Confirmed | Matches e04's raw result: the dirty tab 2 got `controllerchange` and B answered its fetches, 5 of 5. |
| F9 | A same-origin `blob:` dedicated worker inherits its owner's active service worker; a data: worker gets none | SW 357-368 (the worker client case and its note) | Confirmed | |
| F10 | The Storage Standard's endpoints `caches`, `indexedDB`, `serviceWorkerRegistrations` are local with no quota of their own; a bucket is cleared in its entirety | ST 175-199 (table), 411 (bound by the shelf's quota), 561-562 | Confirmed | |
| F11 | The manifest `id` is parsed against `start_url`'s origin; "../foo", "foo", "/foo", "./foo" give the same id; best practice a leading "/"; a different id is a distinct application | MF text 800-812 (process the id member: base origin), 1018-1025 (note), 760-776 (identity) | Confirmed | So `"id": "/BIM-Personal/"`; `"./"` would resolve to the origin root. |
| F12 | Icon `purpose` defaults to "any"; the user agent "SHOULD NOT use an icon other than for its stated icon purpose" | MF text 2007, 2073 | Confirmed | |
| F13 | Chromium needs no service worker or fetch handler to be installable | chromium@dd4d83c (fetched again, identical to the saved copies): `installable_params.h` (fields: check_eligibility, valid_primary_icon, fetch_metadata, prefer_maskable_icon, fetch_favicon, fetch_screenshots, is_debug_mode, criteria; none for a worker); `app_banner_manager_desktop.cc` 114-119 (`valid_primary_icon`, `kValidManifestWithIcons`); `installable_evaluator.cc` 35 (144 px); `installable_logging.cc` (no worker or offline message) | Confirmed | e06's method (four pages, four launch kinds, CDP's installability errors as a control) supports it; the event fired only in the full binary with a profile on disk, as the note says. Whether the address-bar install UI appears without a worker is not observable headless (the note says so). |
| F14 | `apple-touch-icon` takes precedence over manifest icons on Safari and iOS; manifest icons used only with purpose "any" or none | WebKit blog 12445 (Safari 15.4: "Defining icons by using apple-touch-icon takes precedence over manifest-declared icons"); blog 13878 ("If you do both, apple-touch-icon will take precedence"); BCD@82daeeb `manifests/webapp/icons.json` (fetched again, identical): Safari 17 and iOS 15.4, "Only used when no apple-touch-icon is present and either purpose any or not specified" | Confirmed | 180 px as Apple's size stays U, as the standards note already says. |
| F15 | GitHub Pages: no custom MIME types or headers; `.js` served as JavaScript, `.webmanifest` as `application/manifest+json`; no `Service-Worker-Allowed`; `/BIM-Personal` is a 301 | github/docs `creating-a-github-pages-site.md` lines 73-77 ("you can't specify custom MIME types on a per-file or per-repository basis"); saved headers (`hdr_mf.txt` from mdn.github.io, `hdr_noslash.txt`, `hdr_root.txt`, `hdr_sw.txt`); `curl -I` again on 2026-11-08: `app/engine.js` `application/javascript; charset=utf-8`, `max-age=600`, no Service-Worker-Allowed; `sw.js` 404 | Confirmed, partly for headers | "No way to set a header" rests on the docs' silence, not a statement (the standards note says so, Medium-high). The manifest MIME type was measured on mdn.github.io, not this project. |
| F16 | WPT 2026-11-07: a same-origin `blob:` dedicated worker's fetch is intercepted in Chrome 157, Edge 157, Firefox 159, Safari 27.2 | wpt.fyi per-test JSON at 8c04fb8 for `local-url-inherit-controller.https.html`, all four engines | Confirmed | "should intercept fetch()" PASS in all four; Chrome and Edge FAIL "should inherit service worker controller" (reads `navigator.serviceWorker` in the worker), as the note says. e05 measured `importScripts` and `fetch` from a `blob:` worker in Chromium, which WPT does not test; it supports H47 for Chromium. |
| F17 | OSM tile policy forbids offline use and pre-emptive fetching, and asks for viewed tiles to be cached (headers or at least 7 days) | operations.osmfoundation.org/policies/tiles/ (saved text): section 4 "Prohibited: bulk downloading ... and offline use"; "Offline use is not permitted on tile.openstreetmap.org"; "cache each tile for at least 7 days" | Confirmed | The app fetches no OSM tiles today (standards note 3.13); the rule binds if it ever does. |
| F18 | Esri World Imagery is not for offline tile export; both services report `exportTilesAllowed: false` | ArcGIS item 10df2279... `licenseInfo` (saved; modified 2026-10-29): "This layer is not intended to be used to export tiles for offline"; `MapServer?f=json` of World_Imagery and World_Street_Map fetched again 2026-11-08: `"exportTilesAllowed":false` both | Confirmed | |
| F19 | Open-Meteo's data is CC BY 4.0 (free API: non-commercial, under 10,000 calls a day) | open-meteo.com/en/terms (saved text): "You accept to the CC-BY 4.0 licence"; "Less than 10'000 API calls per day, 5'000 per hour and 600 per minute" | Confirmed, with a scope note | The terms do not speak of storing answers; "may be stored" is the CC BY licence's general permission, an inference, sound but not a sentence of the terms. |
| F20 | Nominatim: "Results must be cached on your side" | operations.osmfoundation.org/policies/nominatim/ (saved text) | Confirmed | |
| F21 | Workbox: a string or unrevisioned entry is its own cache key, query and all; only a `revision` adds `__WB_REVISION__` | workbox@4ea3138 (fetched again; identical) `packages/workbox-precaching/src/utils/createCacheKey.ts` 19-68 | Confirmed | |
| F22 | Workbox: activate deletes every key not in the new manifest; `cleanupOutdatedCaches` deletes other caches whose name has `-precache-` and the scope | `PrecacheController.ts` 247-269; `utils/deleteOutdatedCaches.ts` (substring `-precache-`, `includes(self.registration.scope)`) | Confirmed | |
| F23 | Squoosh and Workbox's recipe wait and offer a reload: no `skipWaiting()` until the page asks, then reload on `controllerchange` | squoosh@e8d35e0 (identical) `src/sw/index.ts` 36 (`clients.claim()`), 54-55 (other origins ignored), 88-89 (`skipWaiting` on the `'skip-waiting'` message only); `sw-bridge/index.ts` 11, 68-76 ("Ready to work offline", `location.reload()`), 90-96 ("Update available", reload / dismiss); Workbox's "Handling service worker updates" page (saved text): `messageSkipWaiting()` then `self.skipWaiting()`, "you may want to auto-save or persist transient state before triggering the reload" | Confirmed | |
| F24 | draw.io: an ES5 worker that reproduces Workbox's precache without its runtime; `skipWaiting()` at once; `index.html` precached and answered cache-first | drawio@c72c9a9 (identical) `service-worker.js` 6-8 ("without the Workbox runtime"), 32 (`self.skipWaiting();` at top level), 44 (`index.html` in the manifest), 1019-1028 and 1199-1210 (precached keys answered from the cache first) | Confirmed | |
| F25 | draw.io: failing installs kept clients on an old release for months | `service-worker.js` 360-377 ("kept it on an old release for months (30.0.3, May 2026)") | Confirmed | A recorded fault, in the worker's own comment. |
| F26 | draw.io: an HTML error page cached as a script, a fault on record | `service-worker.js` 857-866 | **Partly** | The code is a guard: "An HTML body for a non-document entry is an error page with a 200 status: caching it would poison the shell until the next release, so fail the (atomic) install instead". "Would" states a hazard guarded against; the source does not say it happened. Part 15.3 ("Faults on record: ... an HTML error page cached as a script") and 15.4 ("draw.io's fault") overstate it; the design rule it supports (refuse HTML for `.js`/`.css`) is unchanged. |
| F27 | draw.io: `clear.html` and `?offline=0&enableSW=1` remove the worker | github.com/jgraph/drawio wiki FAQ, read through raw.githubusercontent.com/wiki/jgraph/drawio/FAQ.md line 105 | Confirmed | `clear.html` at c72c9a9 exists (3,667 bytes; its script was not traced). |
| F28 | vite-plugin-pwa's `autoUpdate` sets `skipWaiting` and `clientsClaim` and reloads every tab; Excalidraw uses it with no options | vite-plugin-pwa@355cf3d (identical) `src/options.ts` 50 (default `registerType = 'prompt'`), 136-139; `src/client/build/register.ts` 59-74 (`activated` with `isUpdate`/`isExternal` reloads unless `onNeedReload`); excalidraw@701b901 `vite.config.mts` 302, `excalidraw-app/index.tsx` 3, 15 | Confirmed | |
| F29 | vite-plugin-pwa warns that its automatic reload can lose form data | vite-pwa-org.netlify.app/guide/auto-update.html (saved text; fetched again 2026-11-08, 200): "the user can lose data in any browser windows/tabs in which the application is open and is filling in a form", recommending `prompt` | Confirmed | |
| F30 | Excalidraw and tldraw keep a self-destroying `sw.js` | excalidraw@701b901 `public/service-worker.js` 1-20 (install `skipWaiting()`, activate `unregister()` then `client.navigate(client.url)`; the comment on CRA users needing a hard refresh); tldraw@9cc8223 `apps/dotcom/client/public/sw.js` 1-19 (same pattern, credited to benjaminrancourt.ca and NekR/self-destroying-sw) | Confirmed | |
| F31 | Create React App made its worker opt-in after issue #2398 ("super sticky") | github.com/facebook/create-react-app/issues/2398 | **Not re-read** | github.com answered 403 to this session (the earlier reader's saved copy is the same refusal). Context only in 15.3; no code depends on it. Stays at the level of the prior-art note's reading, unconfirmed by this check. |
| F32 | The three apps with a worker answer `index.html` from the cache first | squoosh `src/sw/index.ts` 51-80 (same-origin GET not dynamic goes to `cacheOrNetwork`); vite-plugin-pwa `src/options.ts` 85-95 (`navigateFallback: 'index.html'` by default, which Excalidraw does not override: no `navigateFallback` in its `vite.config.mts`); draw.io F24 | Confirmed | |

## The measured facts: method and raw results

The scripts in `docs/research/experiments/v172h-offline/` were read, and the raw JSON the 2026-11-07 runs wrote
(`<scratch>/v172h-exp/results/`) was compared with the experiments note. No script was rerun: nothing below needed it.

| # | Claim | What was read | Result | Note |
|---|---|---|---|---|
| E1 | H40: scope, 3 of 3 (e01) | `e01_scope.js`, `_server.js` (the `/Other/` project, the 301), the note's table | Supported | The 301 is the stand-in's; Pages' own 301 is in the saved header `hdr_noslash.txt`. |
| E2 | H42: exact `?v=` URLs hit, without the query or with another hash miss; the old build's cache deleted (e02) | `e02_precache.js`, `sw-app.template.js` | Supported | Agrees with F3. |
| E3 | H43: offline after one visit, 5 of 5, 0 errors; the control fails once the HTTP cache is cleared (e03) | `e03_offline_app.js`; the note | Supported, with a scope note | The experiment worker answers navigations **network first** (the note says so, H43 inferences), not cache first as option C does. The offline result holds for C a fortiori; the timings of e03 and e07 are those of a network-first page. |
| E4 | H44: no reload activates the waiting worker, even in one tab; it activates when the last tab leaves or closes (e04) | `e04_update.js`; `results/e04_update.json` `oneTab`, `twoTabs` | Supported | Raw steps identical in 5 of 5 runs; `updatefoundMs` 1544-1557. |
| E5 | H45: hold while dirty, one reload, no loop; `skipWaiting()` also switches the other, dirty tab, whose fetch B answers (e04) | `exp.js` 3-19 (reload once on `controllerchange` unless `__dirty`), 64-67 (`SKIP_WAITING` unless dirty); `e04_update.json` `message`: `whileDirty` "held: unsaved work", `reloads` 1 then 1 after 3 s, `dirtyTab` controller B, `dirtyTabProbe.version` "B" | Supported | This is the finding part 15 turns on; it agrees with F8. |
| E6 | H46: 25 of 25 navigations revalidate `sw.js` (`max-age=0`, `If-None-Match`), 0 of 25 with `updateViaCache:'all'` (e04) | `e04_update.json` `hits` | Supported | Agrees with F4 and F5. The request left about 1.92-2.01 s after the navigation (driver clock) while `updatefound` came at about 1.55 s (page clock) in the other scenario; both are Chromium on loopback. |
| E7 | H47: `importScripts` and `fetch` from a script-URL and a `blob:` worker answered by the service worker; the runtime started offline in about 2.5 s (e05) | `e05_worker_fetch.js`, `sw-probe.template.js`; the note | Supported | The uncontrolled control (both reach the server) makes the method sound. |
| E8 | H48: one usage figure, 32 KB, 8.8 MB, 25 MB (e02) | the note's table | Supported for counting | Eviction together rests on F10 (text), not a measurement. The experiments note calls that S, the standards note P; the text is P, the engines' behaviour is not measured. |
| E9 | H49: `beforeinstallprompt` with a manifest and no worker (e06) | `e06_install_prompt.js`; the note's launch table | Supported | Only in the full binary with a profile on disk; the headless shell never fires it. |
| E10 | Cost: precache about 330 ms and 3.97 MB a second time; repeat 63 ms against 31 inside 600 s; 50 ms and 442 bytes against 111 ms and 3.97 MB after (e07) | `e07_load_cost.js`; `results/e07_load_cost.json` | Supported | The second 3.97 MB is caused by the experiment worker's `cache: 'reload'` (the note says so); Workbox fetches unrevisioned (hash-named) entries with `cache: 'default'` (prior-art note, `PrecacheController.ts` 145-146). |

## Discrepancies in part 15

1. **15.1, "What the app has now": the runtime's address.** It says the runtime "is fetched from the absolute
   address `https://bradleypham1906.github.io/BIM-Personal/runtime/` (`ladybug/runtime.js:15`)". Line 15 declares
   that constant, but `bimLbBase()` (`runtime.js` 29-35) uses it only from `file://` or a page under `v/`; over
   http(s) the base is the page's own folder plus `runtime/`. Part 15.7 and the experiments note (H47) say this
   correctly. Correction: "fetched from the page's own folder plus `runtime/` (same origin on Pages), and from the
   absolute Pages address only from `file://` or a `v/` build (`runtime.js:15, 29-35`)".
2. **15.3 and 15.4: draw.io's HTML error page.** 15.3 lists "an HTML error page cached as a script" among "faults on
   record", and 15.4 calls the guard "draw.io's fault". The source is a guard against a hazard ("would poison the
   shell"), not a record that it happened (F26). Correction: "draw.io's guard against an HTML error page with status
   200 being cached as a script". The months-long stale release is a recorded fault (F25) and stands.
3. **15.3, prior art: what "every app" does.** Two items are not common to all: icons (Squoosh ships 1024 px `any`
   and `maskable` only; Excalidraw 192, 180, 32 and 16 px with no 512 and no maskable; only draw.io and tldraw have
   192 and 512 with maskable), and cross-origin requests (Excalidraw caches a CDN's fonts on purpose, prior-art PA5
   "held with an exception"). Correction: name the apps for each, as the prior-art note's comparison table does.
4. **15.3 and 15.8: the precache's second download.** "The precache ... fetched the app a second time (3.97 MB)" and
   "The precache doubles the first visit's download" are stated as costs of a worker; they are the experiment
   worker's `cache: 'reload'` (E10). Since the names carry the content hash, a precache that allows the HTTP cache
   would avoid most of it; that was not measured. Correction: say so in both places, and make the fetch mode a
   design choice of C.
5. **15.4, option C: "found within about 1.5 s of any navigation".** A Chromium-on-loopback number (E4, E6: 1.55 s to
   `updatefound` in one scenario, about 2 s to the request in another). Correction: "about 1.5 to 2 s after a
   navigation in Chromium here; the specification says only 'in parallel'".
6. **15.4, option C: "navigations in scope answer `index.html` from the cache".** `docs/` and `v/` are in scope (F1,
   E1) and the same paragraph leaves them to the network; the experiments note (H43 threats) warns that a blanket
   fallback would show the app for a guide address offline. Correction: "navigations to the app's own address
   (`/BIM-Personal/` and `index.html`)".
7. **15.9: "the specification's algorithm, which Chromium followed exactly".** The experiments tested some steps
   (activation, update checks), not the whole algorithm. Correction: "which Chromium followed in every step
   measured".
8. **15.1, "twelve engine files fetch third-party hosts".** No note gives this count or its method. A plain grep of
   `src/js/engine/` for files with an `'https://` literal finds 14, some of them only credit links. Minor:
   either give the method or drop the number.
9. **15.1, H48's level.** P in 15.1 and the standards note, S in the experiments note for "evicted together". The
   text is P (F10); engines' eviction is untested. Minor: say "P for the text; not measured".

Nothing in the recommendation (option C) changes: every fact it depends on was confirmed, and corrections 1 to 9
are wording, scope or a number.

## What goes back to U

- **F31** (Create React App's opt-in decision, issue #2398): not re-read, github.com refused; it carries no weight in
  the design. U until re-read.
- **F26's "fault on record" reading**: the guard is P; the claim that the fault happened is U.
- Already U in the notes and still U: H51 (standalone shell on devices), H47 on iOS, Apple's 180 px size, engines'
  eviction together, Firefox and Safari update timing, the cause of Chromium's ~2 s update-check delay.

## Tally

32 source facts: 30 confirmed (F15 and F19 with a scope note), 1 partly (F26), 1 not re-read
(F31), 0 refuted. 10 measured claims: all supported by their method and raw results (E3 and E10 with a scope note).
9 discrepancies in part 15, none changing the recommendation.
