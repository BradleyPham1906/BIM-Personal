# V172h prior art: how open web apps make themselves installable and offline, and how they update

Research date: 2026-11-07. Part of `docs/research/research-local-storage.md` part 14 (V172h, "Storage C:
installable and offline"), side 2 of its method. It extends `prior-art.md` (2026-10-31), which covered how the same
apps store projects; that note's storage findings are not repeated here. Scope: what comparable apps and the main
library actually do with a service worker and a manifest, read in their own code or their own documents, for a
zero-dependency ES5 app on GitHub Pages whose four bundles are named `app/<name>?v=<12 hex of sha256>`, whose page
is `index.html`, and whose 16 MB Ladybug runtime is loaded only when an analysis runs.

**Method.** Code was read as text, never run. Each repository was cloned shallow and blobless
(`git clone --depth 1 --filter=blob:none --no-checkout`) into the session scratchpad, outside the repository, and
read with `git show HEAD:<path>`. The commit is the clone's HEAD on 2026-11-07; line numbers refer to it. Vendor
pages were fetched as HTML and reduced to text in the scratchpad. Issue reports were found by web search (the
GitHub API is refused to this session, as in October) and each one cited was opened.

**Evidence levels** (per `docs/research/research-protocol.md`): **P** = read in the primary source (the code, the
vendor's own page, the issue thread); **S** = dependable secondary, gap stated; **U** = search summary only,
planning use only, "to confirm".

## The question

What do the apps and the library that do this well cache, when, with which strategy per kind of request, how do
they name and retire caches, how do they detect a new version and tell the user, do they call `skipWaiting()` and
`clients.claim()`, what do they do about unsaved work and several tabs, cross-origin requests and large optional
assets, and what do their manifests and icons hold? Where do they disagree, what faults have users filed against
the approach, and what does all of it suggest for a hand-written ES5 `sw.js` with app files cache-first,
`index.html` network-first and no `skipWaiting()` while a page has unsaved work?

Hypotheses this side can test (the H numbers are part 14.1's):

| # | Claim (falsifiable) | Tested here by |
|---|---|---|
| PA1 | Content-hashed (or query-versioned) URLs are used as cache keys as they are, with no extra revision, by the main library | Workbox `createCacheKey` |
| PA2 | No app read here calls `skipWaiting()` unconditionally on install when it edits user documents; they wait or ask | Squoosh, Excalidraw, draw.io, tldraw |
| PA3 | The common update UX is "a new version is ready, reload", sent from the page to a waiting worker by `postMessage` | Workbox docs and code, Squoosh, Excalidraw |
| PA4 | Large optional assets are not precached on install; they are cached when first used, or left to the network | Squoosh, draw.io, Excalidraw |
| PA5 | Cross-origin requests are left to the network by default (opaque responses are not cached unless asked) | Workbox, draw.io |
| PA6 | `index.html` network-first is a recognised pattern, and has a known fault (slow networks, "lie-fi") that a timeout fixes | Workbox `NetworkFirst`, offline cookbook |

(The outcome of each is in "Hypotheses: the outcome" near the end.)

## Pinned sources

| Project | Repository | Commit (HEAD, cloned 2026-11-07) | Date of commit | Licence (read in repo) |
|---|---|---|---|---|
| Workbox 7.4.1 | github.com/GoogleChrome/workbox | 4ea3138a120fd2c87389b54130e25f47e0fd7089 | 2026-09-02 | MIT (`LICENSE`, "Copyright 2018 Google LLC") |
| Squoosh | github.com/GoogleChromeLabs/squoosh | e8d35e0fb66eb16eff6fe8fc773eabcbb7128de3 | 2024-08-19 | Apache-2.0 (`LICENSE`) |
| Excalidraw | github.com/excalidraw/excalidraw | 701b901a0f1ba3d0b390d9cdf63d112e25abac4b | 2026-11-05 | MIT (`LICENSE`) |
| vite-plugin-pwa (Excalidraw's PWA tool) | github.com/vite-pwa/vite-plugin-pwa | 355cf3dd283ca50da3ac4759501e9c3312a3da91 | 2026-10-09 | MIT (`LICENSE`) |
| tldraw | github.com/tldraw/tldraw | 9cc8223e2a945ea4e22868536c70f19c8d40516d | 2026-11-07 | tldraw licence (`LICENSE.md`): source-available, not open source. Method only, no code taken |
| draw.io | github.com/jgraph/drawio | c72c9a98b7a6ce392556ed04c05e0ff19f43f5c3 | 2026-11-04 | Apache-2.0 (`LICENSE`) |

Vendor pages read (fetched 2026-11-07, text kept in the scratchpad):

| Page | URL | Page's own date |
|---|---|---|
| Handling service worker updates with immediacy (Workbox) | developer.chrome.com/docs/workbox/handling-service-worker-updates | 2021-12-07 |
| workbox-precaching | developer.chrome.com/docs/workbox/modules/workbox-precaching | 2017-11-27 (last updated as shown) |
| workbox-window | developer.chrome.com/docs/workbox/modules/workbox-window | 2019-02-24 |
| Navigation preload (Workbox) | developer.chrome.com/docs/workbox/navigation-preload | 2021-11-04 |
| The service worker lifecycle (Workbox) | developer.chrome.com/docs/workbox/service-worker-lifecycle | 2021-09-24 |
| The offline cookbook (Jake Archibald) | web.dev/articles/offline-cookbook | 2014-12-09, revised since |
| The service worker lifecycle (Jake Archibald) | web.dev/articles/service-worker-lifecycle | 2016-09-29 |

## Search log

| # | Where | Query / action | What came back | Kept / set aside, why |
|---|---|---|---|---|
| 1 | git | `git ls-remote <repo> HEAD`, then blobless shallow clones of the six repositories | Six HEADs (table above) | Kept: the pins |
| 2 | git | `git ls-tree -r --name-only HEAD` filtered for `sw`, `service-worker`, `manifest`, `pwa`, `workbox` | Paths of the worker, manifest and update code in each | Kept: the files read below |
| 3 | git | `git show HEAD:<path>` for the files named in each section | Source text | Kept: the P facts |
| 4 | developer.chrome.com, web.dev | The seven pages in the table above, fetched as HTML | Text | Kept (P for Workbox's and Chrome's own behaviour; the cookbook is a practitioner's document by a spec editor) |
| 5 | api.github.com | Issue search | Refused by the proxy, as on 2026-10-31 | Set aside; web search for pointers, then each issue opened |
| (more rows are added below as the work goes) | | | | |

---

## 1. Workbox (MIT): strategies, precaching, the window library, navigation preload

Workbox is Google's service-worker library; Excalidraw (through vite-plugin-pwa) and many other apps generate their
worker with it. Version 7.4.1 (`packages/workbox-core/src/_version.ts`). Paths below are under `packages/`.

### Strategies

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| `CacheFirst` looks in its cache and goes to the network only on a miss, putting the network answer in the cache (`fetchAndCachePut`) | `workbox-strategies/src/CacheFirst.ts:40-63` | P | High |
| `NetworkFirst` races the network against an optional timer (`networkTimeoutSeconds`); on a network error, or when the timer fires first, it answers from the cache; if both the timer fired and the cache missed it still waits for the network rather than failing | `workbox-strategies/src/NetworkFirst.ts:90-131` (race and the "rather wait" comment), `161-191` (timer answers `cacheMatch`), `200-245` (`_getNetworkPromise`: error or no response falls back to the cache) | P | High |
| `StaleWhileRevalidate` starts the network fetch and cache update at once, answers from the cache if it has one, else waits for the network | `workbox-strategies/src/StaleWhileRevalidate.ts:71-109` | P | High |
| `NetworkFirst` and `StaleWhileRevalidate` cache responses with status 200 **or 0 (opaque, cross-origin `no-cors`)** by default; `CacheFirst` and any strategy with no plugin cache only status 200 and warn that opaque responses are not cached | `workbox-strategies/src/plugins/cacheOkAndOpaquePlugin.ts` (`status === 200 \|\| status === 0`); `NetworkFirst.ts:66-67`, `StaleWhileRevalidate.ts:59-60` add it; `StrategyHandler.ts:610-625` (no plugin: only 200, warn on opaque) | P | High |
| A navigation request uses the navigation-preload response when one exists (`event.preloadResponse`) before fetching | `workbox-strategies/src/StrategyHandler.ts:148-168` | P | High |
| A response with a `Vary` header draws a warning to set `ignoreVary`; a `QuotaExceededError` on `cache.put` runs the app's registered quota callbacks | `StrategyHandler.ts:338-343`, `405-407` | P | High |
| Cache writes are deferred one task (`await timeout(0)`) to avoid blocking other cache reads, citing w3c/ServiceWorker#1397 | `StrategyHandler.ts:320-326` | P | Medium (a performance workaround; its need today not checked) |

### Precaching

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| A precache entry given as a string, or with `revision: null`, is taken to be a versioned URL and used **as the cache key as it is, query and all**; only an entry with a `revision` gets an extra `__WB_REVISION__=<rev>` search parameter in its key | `workbox-precaching/src/utils/createCacheKey.ts:19, 35-68` | P | High |
| The documents say the same: "URLs that already include versioning information (like a content hash) are used as cache keys without any further modification" | workbox-precaching page, "How workbox-precaching works" | P | High |
| Revisioned entries are fetched with `cache: 'reload'` (bypassing the HTTP cache), unrevisioned with `'default'`, all with `credentials: 'same-origin'` | `PrecacheController.ts:145-146, 212-216` | P | High |
| Install fetches only entries **not already in the cache under the same key**; a key already present is not downloaded again | `PrecacheStrategy.ts:93-104` (`cacheMatch` first; `_handleInstall` only on a miss during `install`) | P | High |
| Any precache response with status 400 or more, or one a plugin refuses, **fails the whole install** (the new worker is discarded, the old keeps running); redirected responses are copied so they can be served to navigations | `PrecacheStrategy.ts:39-53` (`status >= 400` refused, `copyResponse` on `redirected`), `207-228` (throws `bad-precaching-response`) | P | High |
| One precache cache per scope: its name is `workbox-precache-v2-<registration.scope>`; runtime caches are `workbox-runtime-<scope>` | `workbox-core/src/_private/cacheNames.ts:32-44` | P | High |
| New keys are added to the same cache during install while the old worker still serves from it; on **activate** every key not in the new manifest is deleted. Old and new builds thus coexist until the new worker takes over | `PrecacheController.ts:199-235` (install), `247-269` (activate deletes keys not expected) | P | High |
| `cleanupOutdatedCaches()` deletes, on activate, other caches whose name contains `-precache-` and the scope; it exists for format changes between Workbox majors (v3 to v4), not for each release | `utils/deleteOutdatedCaches.ts:14-53`; `cleanupOutdatedCaches.ts:20-39`; precaching page, "Clean up old precaches" | P | High |
| On lookup, a request URL is tried as it is, then with ignored parameters removed (default `/^utm_/` and `/^fbclid$/`, configurable by `ignoreURLParametersMatching`), then with `index.html` added to a directory URL, then with `.html` added | `utils/generateURLVariations.ts:23-59`; `utils/removeIgnoredSearchParams.ts:24-35`; `PrecacheRoute.ts:56-58` | P | High |
| A precached URL that is not found in the cache falls back to the network by default (`fallbackToNetwork = true`) | `PrecacheController.ts:71-82`; `PrecacheStrategy.ts:110-158` | P | High |
| The documents warn: "Never hardcode revision info into a 'hand written' manifest, as precached URLs will not be kept up to date unless the revision info reflects the URL's contents" | workbox-precaching page, after the tools list | P | High |

### The window library and the update recipe

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| `register()` waits for the page's `load` event unless told `immediate`, then records whether a worker already controlled the page (`isUpdate`) | `workbox-window/src/Workbox.ts:113-119` | P | High |
| If a worker with the same script URL is **already waiting** when the page registers (another tab is open, or the reload overlapped), it fires `waiting` with `wasWaitingBeforeRegister: true` | `Workbox.ts:143-170` | P | High |
| It fires `waiting` 200 ms after a worker reaches `installed` and is still waiting, to ignore workers that call `skipWaiting()` in install | `Workbox.ts:24, 478-507` | P | High |
| A worker installed by another tab's registration is reported as `isExternal` | `Workbox.ts:459-472` | P | High |
| `messageSkipWaiting()` posts `{type: 'SKIP_WAITING'}` to `registration.waiting`; `update()` calls `registration.update()` | `Workbox.ts:32, 319-328, 231-244` | P | High |
| The documented recipe: on `waiting`, ask the user; if they accept, listen for `controlling` and then `window.location.reload()`, and send `messageSkipWaiting()`; the worker answers the message with `self.skipWaiting()`. The sample notes "you may want to auto-save or persist transient state before triggering the reload" | Handling service worker updates page, page code and worker code | P | High |
| The same page says a prompt matters most when the HTML is precached, or when navigations are network-first while versioned assets are loaded lazily: "versioned assets may change, and a service worker hasn't precached them" | Same page, "Do you need to show a prompt?" | P | High |
| `generateSW`'s `skipWaiting` option is `false` by default; with it false the generated worker includes the `SKIP_WAITING` message listener | Same page, "The code to put in your service worker" | P | High |

### Navigation preload

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Enabling it is one call in `activate`: `registration.navigationPreload.enable()`, after a support check; the preload request carries `Service-Worker-Navigation-Preload: true` | `workbox-navigation-preload/src/enable.ts:26-49`; navigation preload page | P | High |
| It helps only navigations answered network-first or network-only; "sites that use a precached app shell don't need navigation preload ... the preloaded response will go to waste"; if no network-first route uses it, it is unused | Navigation preload page | P | High |
| Worker start-up can cost "up to a half a second when a CPU is slow" | Same page | P (vendor's statement, not measured here) | Medium |

### What Workbox's own guidance on the lifecycle adds

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| A new worker waits until the old controls no clients; a refresh is not enough because the old page stays until the new response arrives; `skipWaiting()` means "your new service worker is likely controlling pages that were loaded with an older version ... If this might break things, don't use skipWaiting()" | web.dev lifecycle, "Waiting", "Skip the waiting phase" | P | High |
| "If you expect the user to be using your site for a long time without reloading, you may want to call update() on an interval (such as hourly)" | web.dev lifecycle, "Manual updates" | P | High |
| A shift-reload bypasses the worker entirely (the page is uncontrolled) | web.dev lifecycle, "Shift-reload" | P | High |
| `clients.claim()` matters only on the first load; its author "rarely" uses it and warns it is troublesome when the worker serves pages differently than the network would | web.dev lifecycle, "clients.claim" | P | High |
| The offline cookbook: precache "on install, as a dependency" what the app cannot run without (one failure fails the install); cache "on install, not as a dependency" big optional assets (the install does not wait or fail for them, and they may not finish); delete old caches on activate, remembering "caches are shared across the whole origin" | web.dev offline cookbook, "On install, as a dependency", "not as a dependency", "On activate" | P | High |
| The cookbook calls network-falling-back-to-cache flawed: on "an intermittent or slow connection they'll have to wait for the network to fail before they get the perfectly acceptable content already on their device" | Offline cookbook, "Network falling back to cache" | P | High |
| Activation should be lean: "During activation, events such as fetch are put into a queue, thus a long activation could block page loads" | Offline cookbook, "On activate" | P | High |

---

## 2. Squoosh (Apache-2.0): a hand-written worker and a "reload" snackbar

Squoosh is Google Chrome Labs' image compressor, an offline-capable app written by the author of the offline
cookbook. Its worker is about 90 lines of TypeScript (`src/sw/index.ts`) with helpers (`src/sw/util.ts`,
`src/sw/to-cache.ts`); the page side is `src/client/lazy-app/sw-bridge/index.ts`. Last commit 2024-08-19: the
project is quiet, so this is a settled design, not a current one.

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Two caches: `'static-' + VERSION` for the build and `'dynamic'` for demo images; on activate every other cache name is deleted | `src/sw/index.ts:15-17, 35-49` | P | High |
| `VERSION` is a SHA-1 over every emitted asset's content, written into the worker with the list `ASSETS` at build time, so the worker's bytes change whenever any asset changes (which is what triggers the browser's update) | `lib/sw-plugin.js:55-63` | P | High |
| Install precaches the app shell (`initial`: `'/'` and the first JS) "as a dependency"; the codecs (`theRest`, chosen by feature detection: threads, SIMD, AVIF and WebP decode support) are added on install **only if the user has already used the app**, otherwise when the page later posts `'cache-all'` after the main app first loads | `src/sw/index.ts:19-33, 83-87`; `src/sw/to-cache.ts:83-152`; `sw-bridge/index.ts:103-111`; `lazy-app/Compress/index.tsx:336` | P | High |
| Precache requests use `cache: 'no-cache'` "as our hashing aren't updating properly right now", i.e. they revalidate against the HTTP cache rather than trust it | `src/sw/util.ts:87-90` | P | High |
| Fetch: other-origin requests are ignored (`if (url.origin !== location.origin) return`), non-GET ignored, demo images cache-then-network into `dynamic` (with old demos pruned on each such fetch), and **everything else, the HTML `/` included, is cache-first with `ignoreSearch: true`** | `src/sw/index.ts:51-80`; `src/sw/util.ts:6-15, 17-44, 64-85` | P | High |
| `activate` calls `self.clients.claim()` (so the first visit becomes controlled without a reload) | `src/sw/index.ts:35-36` | P | High |
| No `skipWaiting()` on install; the worker calls it only on the page's `'skip-waiting'` message | `src/sw/index.ts:83-91` | P | High |
| The page: on first install (no controller before) it shows "Ready to work offline" for 5 s when `controllerchange` fires; on later visits it waits for a worker to reach `installed`, then shows a snackbar "Update available" with "reload" and "dismiss"; "reload" posts `'skip-waiting'` to `reg.waiting`, and the `controllerchange` that follows calls `location.reload()` | `sw-bridge/index.ts:62-97`, helpers `8-42` | P | High |
| "dismiss" leaves the new worker waiting; it takes over when every Squoosh tab has closed (the default lifecycle) | `sw-bridge/index.ts:89-96` (no other path calls `skipWaiting`) | P | High |
| A leftover worker at an old URL (`src/copy/sw.js`) calls `skipWaiting()` only, with the comment "I accidentally shipped with the wrong service worker name. This picks up users that still might be using that version" | `src/copy/sw.js:1-4` | P | High |
| Manifest (`manifest.json`, built): `name`, `short_name`, `start_url: '/?utm_medium=PWA&utm_source=launcher'`, `display: 'standalone'`, `orientation`, `background_color`, `theme_color`, `description`, `lang`, `categories`, `screenshots` with `form_factor`, `share_target` (POST, multipart), and two icons, both **1024x1024**: one plain and one `purpose: 'maskable'` | `src/static-build/index.tsx:33-96`; icon sizes read from the PNG headers here | P | High |
| The page links `apple-touch-icon` (the 500x500 social image), `theme-color`, `mobile-web-app-capable`, `apple-mobile-web-app-capable`, and `rel="manifest"` | `src/static-build/pages/index/index.tsx:59-64, 45-46` | P | High |
| Hosting headers: `Cache-Control: no-cache` on everything, COOP and COEP for WebAssembly threads | `src/static-build/index.tsx:97-109` | P | High |

**What Squoosh does not have to solve.** It holds no user documents: an image is opened, compressed and saved, so
a reload loses at most the current image, and the snackbar is enough. Its `ignoreSearch: true` would be wrong for
us: our four bundles differ only by their `?v=` query, so ignoring the search would serve any cached build's file
for any other build's request.

---

## 3. Excalidraw (MIT): Workbox through vite-plugin-pwa, automatic update

Excalidraw generates its worker with Workbox's `generateSW` through vite-plugin-pwa (MIT, Anthony Fu). The
configuration is `excalidraw-app/vite.config.mts:301-486`; registration is `excalidraw-app/index.tsx:3, 15`.

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| `registerType: "autoUpdate"` | `excalidraw-app/vite.config.mts:302` | P | High |
| In vite-plugin-pwa, `autoUpdate` (with the default `injectRegister: 'auto'`) sets **`workbox.skipWaiting = true` and `workbox.clientsClaim = true`**; the default `registerType` is `'prompt'` | vite-plugin-pwa `src/options.ts:49-50, 136-139` | P | High |
| Its own description of `autoUpdate`: "when new content is available, the new service worker will update caches and reload all browser windows/tabs with the application open automatically" | vite-plugin-pwa `src/types.ts:305-313` | P | High |
| The page side of `autoUpdate`: on Workbox's `activated` event with `isUpdate` or `isExternal`, it calls `onNeedReload()` if the app gave one, else `window.location.reload()`; Excalidraw calls `registerSW()` with no options, so **every open tab reloads itself when a new build activates** | vite-plugin-pwa `src/client/build/register.ts:59-74`; `excalidraw-app/index.tsx:15` | P | High |
| The `prompt` mode (not Excalidraw's): on `waiting` it calls the app's `onNeedRefresh()`; the app calls `updateServiceWorker()`, which sends `SKIP_WAITING`, and on `controlling` the page reloads; an `installed` worker from another tab (`isExternal`) also raises the prompt | vite-plugin-pwa `src/client/build/register.ts:75-120, 32-37` | P | High |
| Precache: every built file by glob, **except** fonts' CSS, locales, `**/*.chunk-*.js`, the code editor, the Firebase SDK ("only needed for collab/sharing, which require network anyway") and the Mermaid chunks; no file over 2.3 MB is precached (`maximumFileSizeToCacheInBytes`) | `vite.config.mts:308-333, 394` | P | High |
| Runtime caching: `.woff2` fonts CacheFirst in `fonts`, 1000 entries, 90 days, **statuses `[0, 200]` "to cache opaque responses from cross-origin requests (i.e. CDN)"**; `fonts.css` StaleWhileRevalidate; locales CacheFirst 30 days; chunks and lazy `/assets/*.js` CacheFirst 90 days (50 and 200 entries) | `vite.config.mts:334-393` | P | High |
| Large optional code is cached on use, not on install: when the text-to-diagram dialog opens, the page waits 5 s and then fetches every Mermaid chunk at `priority: "low"` so the worker's runtime cache holds them for offline use; it only does so when a worker controls the page, and retries on a later open if offline | `excalidraw-app/data/cacheMermaidChunks.ts:7-42` | P | High |
| vite-plugin-pwa's defaults for `generateSW`: `cleanupOutdatedCaches: true`, `navigateFallback: 'index.html'` (navigations answered from the precached HTML, i.e. cache-first for the page) and `dontCacheBustURLsMatching` the hashed assets folder (no extra revision for hashed names) | vite-plugin-pwa `src/options.ts:85-95` | P | High |
| A **self-destroying worker** kept at the old address `public/service-worker.js`: on install `skipWaiting()`, on activate `registration.unregister()` then `client.navigate(client.url)` for every client, because users of the old (Create React App) worker "were not able to migrate to Vite or any new changes post Vite unless browser is hard refreshed" | `public/service-worker.js:1-20` | P | High |
| vite-plugin-pwa has a `selfDestroying` mode for the same purpose | vite-plugin-pwa `src/client/build/register.ts:5-13, 59` | P | High |
| Manifest: `short_name`, `name`, `description`, `id: "excalidraw"`, `start_url: "/"`, `display: "standalone"`, `theme_color`, `background_color`, `file_handlers` for `.excalidraw`, `share_target`, six `screenshots`; icons 192, 180 (the apple-touch file), 32 and 16 px | `vite.config.mts:396-485` | P | High |
| No 512 px icon and no maskable icon in the manifest, although `public/android-chrome-512x512.png`, `public/maskable_icon_x192.png` and `public/maskable_icon_x512.png` exist (no file references the maskable ones: `git grep maskable_icon` is empty) | `vite.config.mts:401-422`; `git ls-tree HEAD public/` | P | High |
| The page links `apple-touch-icon` 180x180 and `theme-color` | `excalidraw-app/index.html:12, 136` | P | High |

**Why automatic reload is tolerable there.** Excalidraw writes the scene to localStorage on a short debounce
(`prior-art.md` part 2), so a forced reload restores almost everything. It still reloads every tab at once, which is
the opposite of PA2; the counter-evidence section has what users filed about it.

---

## 4. draw.io (Apache-2.0): a hand-written ES5 worker that replaced the Workbox runtime

draw.io's worker, `src/main/webapp/service-worker.js` (1293 lines, 45.8 KB, of which about 300 are the generated
lists), says of itself that it is "Generated by GenerateServiceWorker.java from a workbox-config*.js file" and
"Reproduces the Workbox 7.2.0 generateSW precaching behaviour without the Workbox runtime" (lines 5-15). It is
written in ES5 style (`var`, `function`, promise chains, no `async`), with ES2015 `Map`, `Set` and `for...of`. It is
the closest prior art to what V172h plans: a dependency-free worker for a large editor that holds users' documents.
The page side is `src/main/webapp/js/diagramly/App.js`. Line numbers below are of the worker unless a file is named.

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| It keeps Workbox's cache name (`workbox-precache-v2-<scope>`) and its `__WB_REVISION__` cache keys "so an existing Workbox-populated cache is adopted in place and only changed files are re-fetched" | `:6-9, 344-345, 480-490` | P | High |
| Revisions are each file's MD5; `.html` entries add the release (`...-32.6.10`) "so documents are re-fetched once per release (a cached response pins the HTTP headers it was fetched with, e.g. the CSP, which a header-only change never invalidates)" | `:15-18`; manifest entries such as `index.html` revision `37d9...-32.6.10` | P | High |
| 52 precache entries (the app's minified JS, `index.html`, `open.html`, `images/manifest.json` and others), 60-odd language files in a separate `LAZY_MANIFEST` "cached on first use instead of at install time", and dev sources network-first only on development hosts | `:34-92, 93-156, 162+`; header `:11-15` | P | High |
| **`self.skipWaiting()` at the top of the script**, unconditionally; no `clients.claim()` | `:32` (and no `claim` anywhere in the file) | P | High |
| All query parameters are ignored on lookup (`ignoreURLParametersMatching: [/.*/]`), plus Workbox's `index.html` and `.html` variations | `:340-341, 545-600` | P | High |
| Fetch: non-GET ignored; a precached URL is answered **cache-first on the current revision**, then the network, then the newest previous revision; a lazy URL cache-first, then network (filling the cache), then a stale revision, then the English resources; **anything else, cross-origin included, is not handled** ("Not precached - fall back to the network (browser default handling)") | `:1001-1045` (`respondPrecache`), `1046-1081` (`respondLazy`), `1176-1199` (fetch handler) | P | High |
| `index.html` is precached and served cache-first, like the scripts | manifest entry for `index.html`; fetch handler `:1185-1190` | P | High |
| Install is all or nothing, but checks each entry: a status of 400 or more, or **an HTML body for a non-HTML entry ("an error page with a 200 status: caching it would poison the shell until the next release")**, fails it; redirected responses are copied; entries already cached under the same revision with intact bytes (SHA integrity) are not fetched again | `:782-880`, `1001-1010` (`isUsable`), `636-653`, `687-730` | P | High |
| A recorded fault and its fix: "Installs that keep failing on a client (a file its network blocks or rewrites, a full storage quota) kept it on an old release for months (30.0.3, May 2026): the old worker serves its old files until an install of a new one completes". Since then, after 7 days and 3 failed attempts an install keeps what it stored, activates, takes the rest from the network or the previous revision, and reports once to `/log` | `:360-377, 381-479, 870-880` | P | High |
| Activate deletes every key whose revision changed or that left the manifest, except the newest previous revision of an entry whose current revision is not yet stored (the offline fallback) | `:882-950` | P | High |
| Messages: `warmLazy` (cache one language file, answering on a `MessagePort`) and `warmDev`; only URLs in the worker's own lists are ever fetched | `:1200-1293` | P | High |
| The worker is enabled only on draw.io's own hosts or with `?offline=1` / `?enableSW=1`, and not with `?pwa=0` | `js/diagramly/Editor.js:210-214` | P | High |
| **It is not installed on a new user's first load**: registration is skipped unless a worker already exists, a release channel is pinned, settings are not new, or `enableSW=1` ("Skipping service worker (first load)") | `App.js:1116-1135` | P | High |
| On later loads the page calls `reg.update()` when a worker exists, and counts failures by day; after 14 days of failures on the "stable" channel it falls back to the default channel ("Frozen-but-working must not become permanent") | `App.js:1078-1113` | P | High |
| Normal releases **never force a reload**: with `skipWaiting()` the new worker takes over at once, but a page already running keeps its loaded code until the user next opens the app; "normal release updates set no flag and never force reloads" | `App.js:2776-2779`; worker `:32` | P | High |
| A reload is forced only when the release channel is switched, and then "only with no unsaved changes" (`getCurrentFile().isModified()`); otherwise "the next start uses the new channel" | `App.js:38-70, 2762-2800` | P | High |
| When a collaborator's file was written by a newer version, the user is told "This file was created or modified in a newer version of this app. You will be redirected now"; "Keep the document and modified flag intact. Cancel lets the user export a local copy before explicitly discarding and reloading" | `DrawioFile.js:1842, 3444-3446, 3451-3530`; `resources/dia.txt:884` | P | High |
| Before that forced reload it calls `App.updateServiceWorker`, which runs `reg.update()` and waits (up to 15 s) for the new worker to activate, because "a plain reload is served by the old worker and only triggers the update in the background"; "Deleting the cache would not help - the old worker refetches the revisions of its own manifest on a miss" | `App.js:599-660`; `DrawioFile.js:3514-3530` | P | High |
| Install promotion: on Android and iOS only, `beforeinstallprompt` is caught and an "Install App" banner shown | `App.js:2222-2232`; `resources/dia.txt:609` | P | High |
| Manifest (`images/manifest.json`): `name`, `short_name`, `description`, icons: `favicon.ico` (16 and 32), **192 and 512 px PNG, and 192 and 512 px `purpose: "maskable"` as separate entries**; `theme_color`, `background_color`, `display: "fullscreen"`, `start_url: "../index.html"`, `file_handlers` for `.drawio` with `launch_type: "multiple-clients"` | `images/manifest.json` (whole file) | P | High |
| The page links `theme-color`, `rel="manifest"` and `apple-touch-icon` | `index.html:17, 19, 22` | P | High |

**What draw.io teaches V172h.** Its worker's own comments record the two failures that matter most to a static
app: an install that cannot finish leaves users on an old release for months, and an error page with status 200
poisons the cache. It never reloads a page with unsaved changes, and it takes the new worker at once
(`skipWaiting`) only because every page it serves is self-contained once loaded and it ignores query strings; an
old page that later lazy-loads a file may get the new release's copy (the comment at `:360-375` accepts "a file of
the previous release next to the current ones" as a fallback). Its licence (Apache-2.0) allows taking code with the
notice kept; the method is what V172h needs, and its ES5 style makes the method easy to follow.

---

## 5. tldraw (source-available licence): installable, but its worker removed

tldraw's licence (`LICENSE.md`) is not an open-source licence: use in a "Production Environment" needs a licence
from tldraw, Inc. It was read as text for its method only; nothing is taken.

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| tldraw.com's `public/sw.js` is a **self-destroying worker** ("Taken from https://www.benjaminrancourt.ca/how-to-remove-a-service-worker/", "Inspired from https://github.com/NekR/self-destroying-sw"): `skipWaiting()` on install; on activate `unregister()`, then `client.navigate(client.url)` for each client | `apps/dotcom/client/public/sw.js:1-19` | P | High |
| No worker generator is configured: `apps/dotcom/client/vite.config.ts` has no PWA or Workbox plugin (searched for `pwa`, `workbox`, `sw`) | `apps/dotcom/client/vite.config.ts` | P | Medium (one file searched; a repository-wide `git grep` timed out on the blobless clone) |
| It stays installable through a manifest: `name`, `short_name`, `start_url: "/"`, `scope: "/"`, `display: "standalone"`, `background_color`, `theme_color`, `lang`, `orientation`, `description`; icons **512 and 192 px `purpose: "any"` and 512 and 192 px `purpose: "any maskable"`** | `apps/dotcom/client/public/manifest.webmanifest` | P | High |
| The page links the manifest, `theme-color`, and four `apple-touch-icon`s: a default PNG and 152, 167 and 180 px (as SVG) | `apps/dotcom/client/index.html:10, 56-62` | P | High |

**What it shows.** A whiteboard that keeps its documents in IndexedDB chose to give up its offline worker and keep
only installability. Its repository does not record why (shallow clone, no history read); that is open. Together
with Excalidraw's `public/service-worker.js`, it shows that the way back from a worker is a "self-destroying"
worker served at the same address, which every app that ships a worker should be ready to publish.
