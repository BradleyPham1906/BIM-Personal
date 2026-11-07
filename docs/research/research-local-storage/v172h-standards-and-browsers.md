# V172h: specifications and browsers for an installable, offline Pages app (research, 2026-11-07)

One of the four sides of part 14 of `docs/research/research-local-storage.md` (the plan in its 14.2). It answers,
from the specifications, the browsers' own data and code, and GitHub's documents, what a web app manifest and an ES5
service worker at `/BIM-Personal/sw.js` can rely on. It cites, and does not redo, what part 4.7 and
`files-and-install.md` (c) already hold as P (Chrome's install criteria page, Safari 17 and 26, Firefox 143, the
spec's path restriction measured in e12). Evidence levels are the protocol's: **P** read in the primary source or
measured here, **S** a dependable secondary with the gap said, **U** a search summary or our own inference, planning
only. Everything was read as text, from files kept in the session scratch directory
(`v172h-standards/`), never run. Status: done for this side on 2026-11-07; the independent check of part 14 is still to come.

## 1. The question

What do the standards and the shipping engines guarantee, and where do they differ, for: the worker's scope under a
Pages subpath; how and when a new worker is fetched, installed and activated (one tab, two tabs, reload); whether
the Ladybug runtime's Web Worker is controlled; how the Cache API keys the `?v=` file names; how caches share the
origin's quota and eviction with IndexedDB; the manifest members the app will write (`id`, `scope`, `start_url`,
`display`, `display_override`, `icons` and `purpose`, colours, `shortcuts`); Chrome's install prompt and the fetch
handler; iOS icons and standalone; Firefox; Pages' headers and MIME types; and whether third-party tiles and data
may be cached offline. Hypotheses H29 to H41 are those of part 14.1; this note says which held, failed or stay open
on this side's evidence. A good answer gives the code a P fact, or a stated gap, for every one of them.

## 2. Search log

| # | Where | Query or address | What came back | Kept, set aside, why |
|---|---|---|---|---|
| 1 | GitHub (git ls-remote) | HEAD of w3c/ServiceWorker, whatwg/storage, w3c/manifest, WICG/manifest-incubations, mdn/browser-compat-data, github/docs, web-platform-tests/wpt | Commits 57dfd24, 115691c, 7eaf743, a03b7d1, 82daeeb, 8cd1075, fea36e4 | Kept: every file below is read at these commits |
| 2 | raw.githubusercontent.com | `w3c/ServiceWorker@57dfd24/index.bs` (297,373 bytes; "Service Workers Nightly", Status ED) | The Bikeshed source | Kept: identical byte for byte to the copy the interrupted session fetched from main |
| 3 | raw.githubusercontent.com | `whatwg/storage@115691c/storage.bs` (LATESTRD 2026-02) | The Bikeshed source | Kept |
| 4 | raw.githubusercontent.com | `w3c/manifest@7eaf743/index.html` (ReSpec, specStatus ED) | The editor's draft source, converted to text with a 20-line HTML-to-text script (python3 -I) | Kept |
| 5 | raw.githubusercontent.com | `WICG/manifest-incubations@a03b7d1/index.bs` | 404 | Set aside: the source is `index.html` (ReSpec, CG-DRAFT), fetched instead |
| 6 | raw.githubusercontent.com | BCD at 82daeeb: 13 `manifests/webapp/*.json`, `api/ServiceWorkerRegistration`, `NavigationPreloadManager`, `Cache`, `CacheStorage`, `BeforeInstallPromptEvent`, `ServiceWorkerGlobalScope`, `Clients`, `StorageManager`, `css/at-rules/media` | JSON | Kept; `manifests/webapp/screenshots.json` is 404 (not a BCD file), set aside |
| 7 | wpt.fyi API | `/api/runs?label=master&label=stable` | Runs of 2026-11-07 at WPT 8c04fb8: Chrome 157.0.8103.38, Edge 157.0.4341.42, Firefox 159.0.1, Safari 27.2 | Kept: current engines' measured behaviour, desktop only |
| 8 | wpt.fyi `/api/search` and storage.googleapis.com per-test JSON | `local-url-inherit-controller`, `worker-interception.https` | Subtest results per engine | Kept for H36 |
| 9 | raw.githubusercontent.com | `web-platform-tests/wpt@fea36e4/service-workers/service-worker/{local-url-inherit-controller,worker-interception}.https.html` | Test sources | Kept: what the subtests assert |
| 10 | Live Pages (curl -I) | `/BIM-Personal/`, `app/engine.js`, `sw.js`, `runtime/MANIFEST.json`, `x.webmanifest`; `mdn.github.io/pwa-examples/js13kpwa/*.webmanifest` and `sw.js` | Headers (section 3.7) | Kept: measured |
| 11 | github/docs (sparse clone at 8cd1075, `content/pages/`) | grep header, MIME, cache, service worker | One MIME section; no page on response headers | Kept for H30 |

| 12 | chromium/chromium mirror (raw) at dd4d83c | `components/webapps/browser/installable/*`, banner managers | Source files | Kept for H38; `installable_status_code.h` path 404, set aside |
| 13 | webkit.org | Blog posts 12445, 13878, 17333 | HTML, converted to text | Kept for H39 |
| 14 | mozilla-firefox/firefox (raw) at ac7b5e4 | `browser/components/taskbartabs/` | Source files | Kept; support.mozilla.org refused (Client Challenge) |
| 15 | grep of `src/js/engine/` | `https://` hosts | Esri, AWS terrain, Overpass, Nominatim, Open-Meteo, Census, FEMA, USGS; no `tile.openstreetmap.org` | Kept for H41 |
| 16 | operations.osmfoundation.org, arcgis.com sharing REST, server.arcgisonline.com, open-meteo.com, awslabs/open-data-registry, tilezen/joerd, dev.overpass-api.de | Tile, Nominatim, Esri, Open-Meteo, terrain terms | Policy pages and service metadata | Kept for H41; goto.arcgisonline.com redirects to a JavaScript page, the item JSON read instead |
| 17 | bugs.webkit.org REST | quicksearch "service worker blob worker", "service worker home screen" | 15 and 20 bugs | Kept 4 as counter-evidence, the rest unrelated |
| 18 | whatwg/fetch (raw) at 59afe34 | `Accept-Encoding` | HTTP-network-or-cache fetch and the layering note | Kept for H31 |

## 3. Findings by topic

### 3.1 Scope and the path restriction (H29, H30 in part)

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| With no `Service-Worker-Allowed` header, the maximum scope is the script URL's folder: Update parses `./` against the script URL and the registration's scope path must start with that string, else `SecurityError`. A script at `/BIM-Personal/sw.js` may take the scope `/BIM-Personal/` and nothing above it | SW spec, Update algorithm, the `maxScopeString` steps; e12 measured the same rule in Chromium 153 (part 4.7) | P | High |
| A registration is per storage key (origin) and scope URL, and matching is by scope-URL prefix. `bradleypham1906.github.io` is one origin for all the account's Pages projects, so another project could register its own worker for its own path; a worker scoped `/BIM-Personal/` matches only URLs whose string starts with it. A worker of another project can never be scoped above its own folder (the rule above), so none can claim `/BIM-Personal/` unless it is served from under it | SW spec, Set Registration, Match Service Worker Registration; part 4.9 (the shared `github.io` origin) | P | High |
| The manifest's "within scope" is the same string-prefix test, "intentional for consistency with Service Workers"; the spec advises a scope ending in `/`. `/BIM-Personal` (no slash) is out of scope of `/BIM-Personal/`; Pages answers it with a 301 to `/BIM-Personal/` (measured), so an installed app never stays on it | Manifest ED, "within scope"; curl -I | P | High |
| The user guide under `/BIM-Personal/docs/` is within both scopes: the worker will see its requests, and the installed window keeps it in app chrome. The fetch handler must deliberately pass those through (or cache them) | Same prefix rule; repository layout | P (rule) | High |
| The script fetch is made with redirect mode "error": `sw.js` must be answered directly with a 200, never through a redirect | SW spec, Update, perform the fetch hook | P | High |
| Update rejects with `SecurityError` unless the script's MIME type is a JavaScript MIME type | SW spec, Update | P | High |

**H29 held** (spec; the measured subpath rule of e12): a worker at `/BIM-Personal/sw.js` can control `/BIM-Personal/`
and everything under it, and no other Pages project of the account.

### 3.2 Updates: when the browser checks `sw.js`, and the HTTP cache (H35)

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Every navigation request handled by an active registration (and every non-subresource request, which includes a worker's main script) runs Soft Update in parallel; a subresource request or a functional event runs it only when the registration is "stale" | SW spec, Handle Fetch (`shouldSoftUpdate`), Fire Functional Event | P | High |
| "Stale" means the last update check was more than 86,400 seconds ago | SW spec, service worker registration concepts | P | High |
| The script request uses cache mode `no-cache` unless `updateViaCache` is `all`, or the update is forced, or the registration is stale. The default `updateViaCache` is `imports`, so `sw.js` is always revalidated with the server whatever Pages' `max-age=600` says. `no-cache` is a conditional request, so an unchanged `sw.js` can come back as a 304 against the ETag Pages sends | SW spec, RegistrationOptions default `"imports"`, Update | P | High |
| Imported scripts (`importScripts`) are checked only when the main script did not change, and are revalidated only under `updateViaCache: none`, a forced update or a stale registration; with the default they may come from the HTTP cache for up to Pages' 600 s. An ES5 worker with no `importScripts` avoids this question entirely | SW spec, Update, the imported-scripts loop | P | High |
| The new worker is "updated" only if its body is not byte-for-byte identical. The build must therefore write something into `sw.js` that changes with every build (the four `?v=` hashes or a build id), or a new build never reaches an installed user | SW spec, Update, `hasUpdatedResources` | P | High |
| Calling `register()` again with the same script URL, type and `updateViaCache` resolves with the existing registration without fetching; a page that wants an explicit check calls `registration.update()` | SW spec, Register, the "same script URL" early exit | P | High |
| A shift+reload (force refresh) bypasses the worker: Handle Fetch returns null and `navigator.serviceWorker.controller` is null for that page | SW spec, Handle Fetch; note under `controller` | P | High |
| `updateViaCache`: Chrome 68, Edge 18, Firefox 57, Safari and iOS 11.1. `update()`: Chrome 45, Firefox 44, Safari 11.1 | BCD `api/ServiceWorkerRegistration` | P | High |

**H35 held, restated:** the check runs on every navigation into the scope (not "at most every 24 hours"); the 24 hours
is when a check also runs from subresource fetches and events. With the default `updateViaCache` the check revalidates
`sw.js` against Pages, ignoring `max-age=600`.

### 3.3 Activation: waiting, reload, two tabs, skipWaiting and claim (H33, H34)

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| After install, Try Activate activates the waiting worker only if no service worker client is using the registration, or the waiting worker's skip-waiting flag is set (and the active worker has no pending events). If not, activation is tried again when the last client using the registration unloads, when `skipWaiting()` is called, or when the active worker's pending events settle | SW spec, Install (final step and note), Try Activate, Handle Service Worker Client Unload | P | High |
| A reload of the only tab does not activate the waiting worker: the new navigation's reserved client starts using the registration in Handle Fetch, before the old document's unload runs Handle Service Worker Client Unload, which then finds "another client using" it and stops. This is a reading of the order in the algorithms, not a sentence of the spec | SW spec, Handle Fetch ("From this point, the service worker client starts to use ..."), Client Unload step 4 | P (text) / U (the ordering in engines, to be measured by the experiments side) | Medium-high |
| With two tabs open, reloading one leaves the worker waiting; closing (or navigating out of scope) every tab of the app activates it | Same steps | P | High |
| `skipWaiting()` sets the flag and runs Try Activate; it "allows this service worker to progress ... even while service worker clients are using the registration". Pages already open then get the new worker as controller (Activate sets every using client's active worker and fires `controllerchange`) while their code is the old build's | SW spec, `skipWaiting()`, Activate step "For each service worker client who is using registration" | P | High |
| A page can therefore hold the update back simply by not calling for it, and let it in later by posting a message to the waiting worker that calls `skipWaiting()` (the worker's `message` handler); the page learns of a waiting worker from `registration.waiting` and the `updatefound`/`statechange` events. Every other tab of the app is switched at the same moment, so the message must be sent only when no tab has unsaved work (V172f's tab locks are the place that knows) | SW spec as above; `ServiceWorker.postMessage` | P (mechanism) / U (the multi-tab policy is ours) | High for the mechanism |
| `clients.claim()` makes an active worker the controller of in-scope clients that have none (first visit); it does not replace one active worker by another | SW spec, `claim()` | P | High |
| Activation is not undone by a crash once started, and the `activate` handler "may not all run to completion": deleting old caches there must be safe to repeat on the next start | SW spec, Activate, the two notes | P | High |
| `skipWaiting`: Chrome 41, Firefox 44, Safari 11.1; `clients.claim`: Chrome 42, Firefox 44, Safari 11.1 | BCD | P | High |

**H33 held on the spec text** (one reload does not activate while another tab is open, and not even with one tab; the
engines' order is for the experiments side). **H34 held as a mechanism** (P): message the waiting worker, which calls
`skipWaiting()`; whether it loops depends on the page reloading once on `controllerchange` and never calling it again,
which is the design's, not the spec's.

### 3.4 The Ladybug runtime's Web Worker (H36)

The app makes the worker from a Blob URL (`src/js/engine/ladybug/runtime.js:156`, `new Worker(URL.createObjectURL(new
Blob([txt])))`), which then calls `importScripts(B+'pyodide.js')` and Pyodide fetches the `.wasm`, the standard library
and the wheels from `B`, the page's own `runtime/` folder on Pages (`runtime.js:29-35`).

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| A dedicated worker is a service worker client. One made from a Blob URL whose origin is its owner's inherits the owner document's active service worker; a data: URL worker gets none | SW spec, "The worker client case" and the note after it | P | High |
| Its requests are subresource requests of a controlled client, so Handle Fetch sends them to that worker (fetch, XHR and `importScripts` alike) | SW spec, Handle Fetch, the subresource branch | P | High |
| Measured in current engines (WPT run of 2026-11-07): "Same-origin blob URL worker should intercept fetch()" passes in Chrome 157, Edge 157, Firefox 159 and Safari 27.2. Chrome and Edge fail the companion "should inherit controller" subtest, which reads `navigator.serviceWorker` inside the worker; the fetch is intercepted all the same | wpt.fyi results JSON for `local-url-inherit-controller.https.html`; the test source at fea36e4 | P (measured by WPT) | High for desktop engines |
| For a dedicated worker made from a URL, "Requests on a dedicated worker controlled by a service worker" (xhr, fetch, importScripts) passes in all four; nested dedicated workers fail in Safari, and nested-in-shared fail in Chrome and Safari. Pyodide's worker nests none | wpt.fyi, `worker-interception.https.html` | P | High |

**H36 held** (spec and WPT, desktop): the runtime's fetches reach the page's service worker, so they can be served
from a cache offline. Not covered: `importScripts` from a Blob worker specifically (WPT tests fetch there), and iOS
(WPT runs Safari on macOS; same WebKit). The experiments side should measure an `importScripts` and a `.wasm` fetch
from the app's own worker.

### 3.5 The Cache API and the `?v=` names (H31)

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| A cached request matches only when the URLs are equal with the fragment excluded; the query takes part unless `ignoreSearch` is true (default false). So `app/engine.js?v=aaaa` and `app/engine.js?v=bbbb` are two entries, and an old build's entries can be listed with `cache.keys()` and deleted by exact URL | SW spec, Request Matches Cached Item; CacheQueryOptions defaults | P | High |
| Only GET matches unless `ignoreMethod` | Same | P | High |
| When the stored response has a `Vary` header, each named request header must have the same combined value in the stored and the queried request; `Vary: *` never matches. Pages sends `Vary: Accept-Encoding` on every file (measured). Neither the page's request nor the worker's `addAll` request carries `Accept-Encoding` in its own header list (Fetch adds it to the network copy), so the match holds; an explicit `ignoreVary: true` removes the question | SW spec, Request Matches Cached Item; curl -I; Fetch Standard (whatwg/fetch@59afe34): HTTP-network-or-cache fetch works on `httpRequest`, a clone, and appends `Accept-Encoding` there "per HTTP"; the layering note says it is "set in the network & cache layer", below the service worker layer | P | Medium-high (the experiments side should still measure a match) |
| `addAll` rejects the whole batch if any response is not ok (200-299) or is a 206, and writes nothing (Batch Cache Operations is atomic): a precache is all or nothing | SW spec, `addAll`, Batch Cache Operations | P | High |
| Cache: Chrome 40/43, Firefox 41, Safari and iOS 11.1; `addAll` Chrome 46 (HTTPS); CacheStorage needs a secure context (Chrome 65, Firefox 44, Safari 11.1) | BCD `api/Cache`, `api/CacheStorage` | P | High |

**H31 held** (P).

### 3.6 One bucket: caches, IndexedDB and the worker's registration (H37)

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| The registered storage endpoints are `caches`, `indexedDB`, `localStorage`, `serviceWorkerRegistrations` and `sessionStorage`; the local ones each get a bottle in the same local storage bucket. Only `localStorage` and `sessionStorage` have their own 5 MiB quota; caches and IndexedDB have none of their own and are bound by the shelf's storage quota | Storage Standard, registered storage endpoints table; storage bottles ("still bound by the storage quota of its ... shelf") | P | High |
| "Whenever a storage bucket is cleared by the user agent, it must be cleared in its entirety": caches, IndexedDB and the worker's registration go together | Storage Standard, "Storage buckets" clearing rule | P | High |
| A local bucket becomes "persistent" only with the `persistent-storage` permission; "The user agent cannot clear storage marked as persistent without involvement from the origin or user", which the standard calls "particularly useful for resources the user needs to have available while offline". A grant covers the caches with the projects | Storage Standard, "Storage buckets", mode and its note | P | High |
| Safari's 7-day rule names "Service Worker registrations and cache" with IndexedDB; home-screen apps have their own day counter | WebKit 10218, already P in `storage-standards-and-browsers.md` | P | High |

**H37 held** (P): the worker adds no eviction case of its own. Its corollary for the design: the caches take quota
the projects could use (the 16 MB runtime most of all), and an eviction that loses the app's cache has already lost
the projects.

### 3.7 GitHub Pages: headers and MIME types (H30)

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Pages takes MIME types from the mime-db project ("more than 750 MIME types"); "you can't specify custom MIME types on a per-file or per-repository basis" | GitHub Docs source, `content/pages/getting-started-with-github-pages/creating-a-github-pages-site.md`, "MIME types on GitHub Pages" (github/docs@8cd1075) | P | High |
| No GitHub Pages document offers a way to set a response header; the Pages content has no page on headers at all | Grep of `content/pages/` at 8cd1075 for "header", "cache", "service worker" | P (absence in the docs) | Medium-high (absence, not a statement) |
| Measured: `.js` is `application/javascript; charset=utf-8` (a JavaScript MIME type); `.webmanifest` is `application/manifest+json; charset=utf-8` (on `mdn.github.io`, same Pages servers); every file has `cache-control: max-age=600`, `vary: Accept-Encoding`, `access-control-allow-origin: *`, an ETag; no `Service-Worker-Allowed`; `/BIM-Personal/sw.js` is 404 `text/html` today; `/BIM-Personal` is a 301 to `/BIM-Personal/` | curl -I, 2026-11-07 | P (measured) | High |

**H30 held**: no custom header can be sent (docs offer none; measured none), and `sw.js` will be served with a
JavaScript MIME type. A manifest named `manifest.webmanifest` gets the registered `application/manifest+json`.

### 3.8 The manifest members the app will write

The Web Application Manifest is an editor's draft (ReSpec `specStatus: "ED"` at w3c/manifest@7eaf743; the TR is a
Working Draft of 26 October 2026, part 4.7) and "not stable"; `display_override` and the other extensions are in
Manifest Incubations, a WICG Community Group draft (`specStatus: "CG-DRAFT"`, WICG/manifest-incubations@a03b7d1),
not on the standards track. Browser rows are BCD at 82daeeb.

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| `start_url` is parsed against the manifest's URL and ignored unless same-origin with the document; when absent it is the document URL. It is "purely advisory" | Manifest ED, process the `start_url` member | P | High |
| `scope` is parsed against the manifest URL; query and fragment dropped; ignored unless `start_url` is within it; default is `start_url` with its file name removed. The spec says "always declare a scope" | Manifest ED, process the `scope` member; "Understanding scope" | P | High |
| `id` is parsed against `start_url`'s **origin**, not the manifest URL: "../foo", "foo", "/foo" and "./foo" all give `https://example.com/foo`; best practice is a leading "/". So the app must write `"id": "/BIM-Personal/"`; a relative `"./"` would give the origin root `/`, an identity shared in effect with any other project of the account that did the same. When absent, `id` is `start_url` | Manifest ED, `id` member, its example table and note | P | High |
| A manifest whose `id` differs from an installed app's is "a distinct application"; one whose `id` equals it is "a replacement". The `id` must therefore be fixed before the first release and never changed | Manifest ED, `id` member | P | High |
| `display`: one of fullscreen, standalone, minimal-ui, browser; anything else gives "browser". Standalone excludes the URL bar but "can include other system UI elements such as a status bar and/or system back button" | Manifest ED, `display` member, display modes | P | High |
| `display_override` is a fallback list tried before `display`; Chromium evaluates its first supported entry for installability | Manifest Incubations; Chromium `installable_evaluator.cc` `GetDisplayError` | P | High |
| Icons' `purpose`: `monochrome`, `maskable`, `any` (default when absent). An icon with no recognised purpose is ignored; the user agent "SHOULD NOT use an icon other than for its stated icon purpose" | Manifest ED, `purpose` member | P | High |
| Maskable safe zone: a centred circle of radius 2/5 of the smaller side; the user agent "MUST NOT make any pixel within the safe zone transparent" and may pad | Manifest ED, "Icon masks and safe zone" | P | High |
| `theme_color` applies to the app's windows; a `<meta name="theme-color">` in an in-scope document may override it. `background_color` is for the moment before the stylesheet loads and "MUST NOT" be used after; both may be overridden for `prefers-color-scheme` | Manifest ED, `theme_color`, `background_color` | P | High |
| `shortcuts`: each item's URL must be within scope (process a shortcut is given the scope); how many are shown is the platform's choice | Manifest ED, `shortcuts` | P | High |
| The manifest is fetched and processed on every page load; changed icons and names are "security-sensitive" and may be applied only with the user's knowledge | Manifest ED, "Updating the manifest" | P | High |
| Manifest image fetches carry the document as client "which ensures that ... service worker fetch interception remain in effect": icons can be served from the worker's cache | Manifest ED, fetching an image resource | P | High |
| Support (BCD): `name`, `short_name`, `start_url`, `display` (standalone), `icons`: Chrome 39, Firefox Android 47-79, Safari 17 (macOS), iOS 11.3 (icons 15.4); `scope` Chrome 53, Safari 17, iOS 11.3; `id` Chrome 96, Safari 17, iOS 16.4; `theme_color` Chrome 46, Safari 17, iOS 15; `background_color` Chrome 46, Safari `false`, iOS mirror; `display_override` Chrome 89 only (experimental); `shortcuts` Chrome 96 desktop (85-96 Windows only), Chrome Android 84, Safari 17.4 macOS, iOS `false`. Desktop Firefox is `false` for every member | BCD `manifests/webapp/*` | P | High |
| `display-mode` media feature: Chrome 42, Firefox 47, Safari 13, iOS 12.2 (sub-values browser, fullscreen, minimal-ui, standalone, picture-in-picture, window-controls-overlay). The manifest ED now also asks for an `application` value that BCD does not list yet | BCD `css/at-rules/media`; Manifest ED, display modes | P | High |

### 3.9 Chrome's install prompt and the fetch handler (H38)

Chromium read at `chromium/chromium@dd4d83c` (the GitHub mirror's HEAD on 2026-11-07), `components/webapps/browser/`.

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| `InstallableParams` has no service-worker or fetch-handler check at all: its checks are eligibility (HTTPS, not incognito), a valid primary icon, metadata, favicon, screenshots and the installable criteria | `installable/installable_params.h` | P | High |
| The desktop banner manager (the one that fires `beforeinstallprompt`) asks for `valid_primary_icon` and `kValidManifestWithIcons`; Android asks for `kImplicitManifestFieldsHTML` with `prefer_maskable_icon`, screenshots and favicon | `chrome/browser/banners/app_banner_manager_desktop.cc` `ParamsToPerformInstallableWebAppCheck`; `components/webapps/browser/android/app_banner_manager_android.cc` | P | High |
| The criteria: a manifest (or, for the implicit criteria, page metadata), a valid `start_url`, a name or short name, a display mode in {standalone, fullscreen, minimal-ui, window-controls-overlay, unframed, tabbed} (the first `display_override` entry wins), and a square PNG, SVG or WebP icon of purpose `any` of at least 144 px with `sizes` set | `installable_evaluator.cc` (`kMinimumPrimaryIconSizeInPx = 144`, `DoesManifestContainRequiredIcon`, `IsInstallableDisplayMode`, `GetDisplayError`); `installable_logging.cc` messages | P | High |
| The list of installability error messages has no service-worker or offline entry | `installable_logging.cc` | P | High |
| No site-engagement or 30-second rule appears in the files read; web.dev's 2024 criteria page states one. Where it now lives was not traced | Grep of the banner managers | P (absence in these files) | Low (not traced further) |

**H38 failed**: current Chromium does not need a fetch handler, or any service worker, for the install prompt or the
menu install. The worker is for offline use only. (This closes the row of part 10 left open.) The Chrome blog post of
2023-12-05 is superseded by the code.

### 3.10 Safari and WebKit: icons, standalone, workers (H39)

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Safari 15.4: "Safari and iOS use manifest-declared icons when there is no apple-touch-icon defined in the HTML head, and when the manifest ... either omits the "purpose" key or includes "purpose": "any". Defining icons by using apple-touch-icon takes precedence" | WebKit, "New WebKit Features in Safari 15.4" (blog 12445) | P | High |
| iOS 16.4: "If you do both, apple-touch-icon will take precedence over the Manifest-declared icons"; iOS uses the manifest `id` to sync Focus settings; "iOS has supported multiple installs of the same web app" | WebKit, "Web Push for Web Apps on iOS and iPadOS" (blog 13878) | P | High |
| BCD agrees: `icons` Safari 17 and iOS 15.4, "Only used when no `apple-touch-icon` is present and either purpose any or not specified" | BCD `manifests/webapp/icons.json` | P | High |
| Safari 26: SVG icons and data: URL icons are supported "everyplace there are icons", the Home Screen and the Dock included; every site added to the Home Screen opens as a web app by default; "If you define your icons in the manifest, they're used" | WebKit, "WebKit Features in Safari 26.0" (blog 17333) | P | High |
| Home Screen web apps "never required Service Workers ... yet including Service Workers in your code can greatly enhance the user experience"; Safari 15.4 added Navigation Preload | Blog 17333; blog 12445 | P | High |
| `display` fullscreen and minimal-ui: Safari macOS `false` (only standalone and browser); iOS mirrors Chrome's row | BCD `manifests/webapp/display.json` | P | Medium (the iOS "mirror" is BCD's inference from Chrome, not a WebKit statement) |

**H39 held**: on iOS, iPadOS and macOS Safari an `apple-touch-icon` wins over the manifest, and manifest icons are used
only with purpose `any` or none, so a `maskable`-only icon is never used there. The app should ship one
`apple-touch-icon` (180 px is Apple's usual size, not re-read here: U) and an `any` icon in the manifest besides the
`maskable` one.

### 3.11 Firefox

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Firefox's Taskbar Tabs read the page's manifest (`ManifestObtainer.browserObtainManifest`) and take `name`, `start_url`, `scope` and the best manifest icon from it; without a manifest the start URL is the page's `prePath`, the origin root (`https://bradleypham1906.github.io/`), which for this app is the wrong page | `mozilla-firefox/firefox@ac7b5e4`, `browser/components/taskbartabs/TaskbarTabs.sys.mjs` (`#findOrCreateTaskbarTab`, `fetchIconForTaskbarTab`), `TaskbarTabsRegistry.sys.mjs` (`findOrCreateTaskbarTab`) | P | High |
| A Taskbar Tab is created in the tab's container (`userContextId`) of the current profile, so it uses that profile's storage: the projects saved in a Firefox tab are the same ones (an inference from the code; not stated) | Same files; `TaskbarTabsUtils.createTaskbarTabTitle` names container and profile | P (code) / U (storage consequence) | Medium |
| Navigation is kept in the Taskbar Tab when the target has the same registrable domain as the scope's host (`Services.eTLD.getBaseDomain`); `github.io` is a public suffix, so other `*.github.io` sites leave it | `TaskbarTabsRegistry.isScopeNavigable` | P | Medium-high (the PSL listing of github.io is known, not re-read) |
| The source at HEAD has pinning code for Windows, MSIX and Linux (`TaskbarTabsPinWin`, `TaskbarTabsPinMsix`, `TaskbarTabsPinLinux`); release 143 notes (part 4.7) name Windows only and exclude Microsoft Store builds. Which release ships Linux is not known here | `browser/components/taskbartabs/moz.build` | P (code) | Medium |
| Service workers and the Cache API: Firefox 44 / 41 desktop and Android; `updateViaCache` 57; navigation preload 99 | BCD | P | High |
| Mozilla's help page refused the script (a "Client Challenge" page), as on 2026-10-31 | support.mozilla.org | — | — |

### 3.12 Standalone and the shell (H40, this side only)

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| The applied display mode is reflected in the `display-mode` media feature, from CSS or `matchMedia`; it is the only standard way for a page to know it runs standalone | Manifest ED, display modes | P | High |
| Standalone removes the URL bar and with it the browser's back, reload and address UI; the system may keep a back button (Android) or none (iOS). Anything the app needs from them (reload after an update, leaving the guide) must be in the app | Manifest ED, `standalone` | P | High |
| Navigation out of scope in an installed window should show "a prominent UI element indicating the URL" (how each engine draws it was not read: U); links to third-party sites are better opened with `target="_blank"` (the app already does for its credits, as seen in `map/surroundings-3d.js:386`) | Manifest ED, navigation scope | P | Medium-high |

**H40 open on this side**: the spec says nothing that forces a shell change; whether V149's safe areas and V147's
panels look right standalone is for the app-code and experiment sides, and a device.

### 3.13 Third-party terms for offline caching (H41)

The app fetches no tiles from `tile.openstreetmap.org` (grep of `src/js/engine/`): its raster basemaps are Esri's
World Imagery and World Street Map (`server.arcgisonline.com`), its terrain AWS Terrain Tiles (Terrarium,
`s3.amazonaws.com/elevation-tiles-prod`), and its data hosts include Overpass, Nominatim, Open-Meteo, the Census, FEMA
and USGS.

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| OSM tile policy: offline use "is not permitted on tile.openstreetmap.org"; bulk download is "any pre-emptive fetching of tiles other than those a user is actively viewing". The same policy requires caching what was viewed: honour the headers or keep each tile at least 7 days | OSMF Tile Usage Policy, sections 3.2 and 4 (operations.osmfoundation.org/policies/tiles/, read 2026-11-07) | P | High |
| Esri World Imagery: "This layer is not intended to be used to export tiles for offline", with a separate "(for Export)" layer for ArcGIS apps; licensed under the Esri Master License Agreement. Both services report `exportTilesAllowed: false` | ArcGIS item 10df2279f9684e4a9f6a7f08febac2a9 `licenseInfo` (sharing REST, modified 2026-10); `MapServer?f=json` of both services | P | High |
| Nominatim: "Results must be cached on your side"; periodic requests count as bulk geocoding | OSMF Nominatim Usage Policy | P | High |
| Open-Meteo: data under CC BY 4.0; free API for non-commercial use under 10,000 calls a day. Storing a fetched answer is allowed by the licence with attribution | open-meteo.com/en/terms | P | High |
| AWS Terrain Tiles: attribution required per source (USGS 3DEP, SRTM, EU-DEM and others); no offline prohibition stated; "you are responsible for researching each project" | awslabs/open-data-registry@ab85870 `datasets/terrain-tiles.yaml`; tilezen/joerd@0b86765 `docs/attribution.md` | P | Medium (the per-source licences were not each read) |

**H41 held for tiles, failed for data**: prefetching or keeping Esri or OSM tiles for offline use is not allowed, and
the worker should leave cross-origin tile requests to the network (and the browser's HTTP cache, which the OSM policy
asks for). Openly licensed data (Open-Meteo, Overpass/OSM under ODbL, US federal data) may be stored with its credit,
and Nominatim requires it; whether the app keeps such answers is a design choice, not a legal bar.

### 3.14 Navigation preload and the network-first page

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| With navigation preload enabled, a GET navigation is fetched in parallel with the worker's start-up, with the header `Service-Worker-Navigation-Preload: true`, and offered as `event.preloadResponse`; it applies only if the worker has a non-empty `fetch` listener. Enabling needs an active worker | SW spec, Handle Fetch, NavigationPreloadManager `enable()` | P | High |
| A network-first `fetch(event.request)` for `index.html` goes through the HTTP cache with the request's cache mode, so Pages' `max-age=600` can still return a page up to ten minutes old, as without a worker; `cache: 'no-cache'` would revalidate | Fetch Standard (cache modes); Pages header measured | P | Medium-high |
| Navigation preload: Chrome 59, Edge 18, Firefox 99, Safari and iOS 15.4 | BCD `api/NavigationPreloadManager` | P | High |

## 4. Counter-evidence and engine differences found

| What | Evidence | Level | What it changes |
|---|---|---|---|
| Chrome and Edge 157 fail "blob URL worker should inherit service worker controller" in WPT while passing the fetch-interception subtest; the failure is `navigator.serviceWorker` being absent in a dedicated worker, not a missing controller | wpt.fyi result JSON, messages "Cannot read properties of undefined" | P | Nothing for the app (it never reads the controller in the worker); the experiments side should still see a runtime fetch arrive in the worker's `fetch` handler |
| Safari 27.2 fails "Requests on a dedicated worker nested in a dedicated worker"; Chrome and Safari fail nested-in-shared | wpt.fyi `worker-interception.https.html` | P | Nothing now: Pyodide's worker nests no worker. A future nested worker would not be intercepted in Safari |
| Firefox 159 fails both blob URL **shared** worker subtests | wpt.fyi | P | Nothing: the app uses no shared worker |
| WebKit bug 227113 "PWA mistakingly thinking to be offline" (NEW, last changed 2022-01-19) and 213726 "fetch fails only when site/pwa is added to homescreen" (NEW, 2020-07-05) | bugs.webkit.org REST search | P (the reports exist; not confirmed by WebKit) | `navigator.onLine` should not be trusted in a Home Screen app; the app should decide offline by a failed fetch |
| WebKit bug 209732 "7-Day Cap on All Script-Writeable Storage shouldn't apply to Service Worker registrations" (NEW since 2020-03-30) and 237350 "Web App Added to Home Screen Cookies Deleted After 7 Days" (NEW, 2022-03-09) | bugs.webkit.org | P (reports) | In Safari (not installed) the worker and its caches go with the projects after seven days without a visit, as part 4.2 already says; the Home Screen exemption has at least one contrary report |
| The Chrome blog (2023-12-05) said the install prompt "still requires" a fetch handler | Part 4.7 | P (then) | Superseded by the Chromium code read here (H38) |
| Desktop Firefox is `false` for every manifest member in BCD, yet Firefox's Taskbar Tabs read the manifest | BCD; Firefox source | P | BCD lags; the app's manifest matters for Firefox on Windows too |
| WebKit's statement that `apple-touch-icon` wins dates from 15.4 and 16.4; Safari 26 says manifest icons "are used" without repeating the precedence | Blogs 12445, 13878, 17333 | P | Keep both, as BCD's current note still describes the precedence |

## 5. The hypotheses on this side

| # | Outcome here | Deciding source |
|---|---|---|
| H29 | Held | SW spec, Update (`maxScopeString`), and e12's measurement |
| H30 | Held | GitHub Docs (MIME from mime-db, none custom; no header setting documented) and headers measured on Pages |
| H31 | Held | SW spec, Request Matches Cached Item (`ignoreSearch` false by default); Vary handled per the Fetch Standard |
| H32 | Not this side's | The experiments side |
| H33 | Held on the spec text; engines to be measured | SW spec, Try Activate, Handle Fetch, Client Unload |
| H34 | Held as a mechanism | SW spec, `skipWaiting()` and Activate |
| H35 | Held, restated: a check on every in-scope navigation, plus subresource/event checks after 24 h; `sw.js` revalidated whatever `max-age` says | SW spec, Handle Fetch, stale (86,400 s), Update cache mode, `updateViaCache` default `imports` |
| H36 | Held for desktop engines | SW spec, worker client case; WPT 2026-11-07 (Chrome 157, Edge 157, Firefox 159, Safari 27.2) |
| H37 | Held | Storage Standard, registered storage endpoints and bucket clearing |
| H38 | Failed (no fetch handler or service worker needed) | Chromium `installable_params.h`, `installable_evaluator.cc`, `app_banner_manager_desktop.cc` at dd4d83c |
| H39 | Held | WebKit blogs 12445 and 13878; BCD `icons` note |
| H40 | Open | Spec gives only `display-mode`; needs the app's code and a device |
| H41 | Held for tiles (Esri, OSM); failed for openly licensed data (Open-Meteo, OSM data, federal data), which may be stored, and Nominatim, which must be cached | OSMF tile and Nominatim policies; Esri item `licenseInfo` and `exportTilesAllowed: false`; Open-Meteo terms |

## 6. What remains open, and why

| Open | Why | How to close |
|---|---|---|
| Whether the engines activate a waiting worker on a reload of the only tab (the spec's order says no) | A reading of algorithm order, not a sentence | The experiments side (Chromium here); Safari and Firefox on the owner's machines |
| `importScripts` and a `.wasm` fetch from the app's own Blob worker going through the worker | WPT tests `fetch()` from a Blob worker, `importScripts` only from a URL worker | Experiment in Chromium; WebKit and Gecko on the owner's machines |
| iOS and iPadOS behaviour of the above | WPT runs Safari on macOS only | A device |
| Where Chromium's engagement rule for the prompt lives now | Not in the files read | Read `chrome/browser/banners/` and site engagement code, or a current Chrome document |
| Apple's recommended `apple-touch-icon` size | Not read in an Apple document this session | Apple's Safari Web Content Guide or HIG |
| Esri's Master License Agreement text on caching; each Terrain Tiles source licence | Only the item's summary and the attribution page were read | Esri's terms page (JavaScript-rendered here) and each source's licence |
| Firefox Taskbar Tabs on Linux and their storage | Code at HEAD only; support.mozilla.org refused the script | Mozilla's release notes for the release that ships it |
| Whether a granted `persist()` or the Home Screen exemption keeps the worker's caches in Safari | WebKit bugs 209732 and 237350 are open reports | A device test over more than seven days |

## 7. References

All read 2026-11-07, as text; files in the session scratch directory `v172h-standards/` (`pinned/`, `bcd/`,
`chromium/`, `firefox/`, `webkit/`, `wpt/`, `terms/`, `ghdocs/`, `bugs/`).

| Source | Version or date | What was read | Level |
|---|---|---|---|
| W3C Service Workers, Bikeshed source, https://raw.githubusercontent.com/w3c/ServiceWorker/57dfd24943fee6ba795cea49d277dfb0754e4517/index.bs | "Service Workers Nightly", Status ED, commit 57dfd24 | Registration concepts (stale, navigation preload), service worker client and control (window and worker client cases), RegistrationOptions, `skipWaiting()`, `claim()`, NavigationPreloadManager, CacheQueryOptions, `addAll`, Register, Update, Install, Activate, Try Activate, Handle Fetch, Fire Functional Event, Handle Service Worker Client Unload, Request Matches Cached Item, Batch Cache Operations, `Service-Worker-Allowed` | P |
| WHATWG Storage Standard, https://raw.githubusercontent.com/whatwg/storage/115691c5158395b89063dee09278703f10494171/storage.bs | Living Standard, LATESTRD 2026-02, commit 115691c | Storage endpoints table, buckets, bottles, persistence, clearing, storage pressure, usage and quota | P |
| WHATWG Fetch Standard, https://raw.githubusercontent.com/whatwg/fetch/59afe349913d56898c947576216f1c2579308be7/fetch.bs | commit 59afe34 | HTTP-network-or-cache fetch (`httpRequest` clone, headers "per HTTP"), the layering note on `Accept-Encoding` | P |
| W3C Web Application Manifest, editor's draft source, https://raw.githubusercontent.com/w3c/manifest/7eaf7435779d0e58a375c14c377aaa8fe853ced3/index.html | ED, commit 7eaf743 | Understanding scope, `scope`, `start_url`, `id` (and its table), `display`, display modes, `icons`, `purpose`, safe zone, `theme_color`, `background_color`, `shortcuts`, updating the manifest, fetching image resources, within scope, navigation scope | P |
| WICG Manifest Incubations, https://raw.githubusercontent.com/WICG/manifest-incubations/a03b7d19bd07fe17c3ef0a9a448a7f5a6ccd0cb2/index.html | CG-DRAFT, commit a03b7d1 | `display_override` | P |
| MDN browser-compat-data, https://raw.githubusercontent.com/mdn/browser-compat-data/82daeebf5a7073d55223a8cdb8aa54fb9416e27d/ | commit 82daeeb | `manifests/webapp/` id, scope, start_url, display, display_override, icons, theme_color, background_color, shortcuts, name, short_name, description; `api/` ServiceWorkerRegistration, NavigationPreloadManager, Cache, CacheStorage, BeforeInstallPromptEvent, ServiceWorkerGlobalScope, Clients; `css/at-rules/media` display-mode | P |
| web-platform-tests, https://raw.githubusercontent.com/web-platform-tests/wpt/fea36e49ddda8a206a5d3489ac377c8b9f406af9/service-workers/service-worker/ | commit fea36e4 | `local-url-inherit-controller.https.html`, `worker-interception.https.html` | P |
| wpt.fyi runs and results, https://wpt.fyi/api/runs, https://wpt.fyi/api/search, https://storage.googleapis.com/wptd/8c04fb8d43f3536d4a4c92027b990bb620db2915/ | Stable runs of 2026-11-07 at WPT 8c04fb8: Chrome 157.0.8103.38, Edge 157.0.4341.42, Firefox 159.0.1, Safari 27.2 | Subtest results of the two tests | P (measured by WPT) |
| Chromium, https://raw.githubusercontent.com/chromium/chromium/dd4d83c7ea68df0f1321e95dc282959739871a79/ | GitHub mirror HEAD, commit dd4d83c | `components/webapps/browser/installable/installable_params.h`, `installable_evaluator.cc`, `installable_evaluator.h`, `installable_logging.cc`, `installable_manager.cc`; `components/webapps/browser/banners/app_banner_manager.cc`; `chrome/browser/banners/app_banner_manager_desktop.cc`; `components/webapps/browser/android/app_banner_manager_android.cc` | P |
| Firefox, https://raw.githubusercontent.com/mozilla-firefox/firefox/ac7b5e4bc10b65142541a54b0ef23462647f7da1/browser/components/taskbartabs/ | commit ac7b5e4 | `TaskbarTabs.sys.mjs`, `TaskbarTabsRegistry.sys.mjs`, `TaskbarTabsUtils.sys.mjs`, `TaskbarTabsWindowManager.sys.mjs`, `moz.build` | P |
| WebKit, "New WebKit Features in Safari 15.4", https://webkit.org/blog/12445/ | 2022 | Manifest icons, navigation preload | P |
| WebKit, "Web Push for Web Apps on iOS and iPadOS", https://webkit.org/blog/13878/ | 2023 (iOS 16.4 beta 1) | Home Screen web apps, manifest `id`, icon precedence | P |
| WebKit, "WebKit Features in Safari 26.0", https://webkit.org/blog/17333/ | 2025 | Every site a web app; SVG and data: URL icons; service workers; Web Apps fixes | P |
| WebKit Bugzilla REST search, https://bugs.webkit.org/rest/bug?quicksearch=... | 2026-11-07 | Bugs 227113, 213726, 209732, 237350 (summaries and status only) | P (as reports) |
| GitHub Docs source, https://github.com/github/docs `content/pages/` | commit 8cd1075 | `creating-a-github-pages-site.md` "MIME types on GitHub Pages"; grep of the folder for headers and caching | P |
| GitHub Pages responses (curl -I) | 2026-11-07 | `bradleypham1906.github.io/BIM-Personal/` (page, `app/engine.js`, `sw.js`, `runtime/MANIFEST.json`, a `.webmanifest`, `/BIM-Personal`); `mdn.github.io/pwa-examples/js13kpwa/js13kpwa.webmanifest` and `sw.js` | P (measured) |
| OSMF Tile Usage Policy, https://operations.osmfoundation.org/policies/tiles/ | Read 2026-11-07 | Sections 3.2 (caching), 4 (bulk downloading and offline use), 5 (caching proxies) | P |
| OSMF Nominatim Usage Policy, https://operations.osmfoundation.org/policies/nominatim/ | Read 2026-11-07 | Requirements and bulk geocoding | P |
| Esri World Imagery item, https://www.arcgis.com/sharing/rest/content/items/10df2279f9684e4a9f6a7f08febac2a9?f=json; services https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer?f=json and World_Street_Map | Item modified 2026-10 | `licenseInfo`; `exportTilesAllowed`, `copyrightText`, `serviceDescription` | P |
| Open-Meteo terms, https://open-meteo.com/en/terms | Read 2026-11-07 | Non-commercial terms, CC BY 4.0 | P |
| AWS Open Data registry, https://raw.githubusercontent.com/awslabs/open-data-registry/ab858700d39d37ded3eb5f76fca34af8aa1d9a8f/datasets/terrain-tiles.yaml; tilezen/joerd `docs/attribution.md` at 0b86765 | commits as given | Licence pointer, required attribution | P |
| Overpass API commons page, https://dev.overpass-api.de/overpass-doc/en/preface/commons.html | Read 2026-11-07 | Fetched; nothing on caching found by grep | P (fetched) |
| support.mozilla.org, "use web apps in Firefox on Windows" | 2026-11-07 | Refused: "Client Challenge" page | none |
| Part 4.7, part 10 and `files-and-install.md` (c) of this research | 2026-10-31 | Cited, not redone: Chrome's install criteria page, Chrome blog 2023-12-05, Safari 17, Firefox 143, e12 | as recorded there |
