# Local storage: IndexedDB, files and an installable app (research, 2026-10-31)

The first note written under the protocol of 2026-10-31 (`reference/research-protocol.md`, "Research as a scientist
does it"). Levels: **P** read in the primary source (the specification, the browser's own code, the vendor's own
document, the bug record, the app's code, or measured here), **S** a dependable secondary source with the gap said,
**U** a search summary or a single unchecked copy, a pointer only, labelled "to confirm" and kept out of the plan.

## 1. Abstract

The question: how should BIM-Personal, a zero-dependency ES5 app served from GitHub Pages and also opened as one
`canvas_v10.html` from `file://`, keep users' projects large, durable and safe? Today every project, template and
the family library live in one origin's localStorage, which Chromium caps at exactly 5,242,880 UTF-16 code units
for all keys together (P, source and measured); an imported model costs about 31 characters per triangle, so, by that measured rate,
a project of about 165,000 imported triangles, or one 4 MB image note, already cannot autosave, and a project over
half the cap can never be switched away from. The answer has three parts that solve different problems. IndexedDB
removes the size wall (quotas are 60% of disk in Chrome and Safari 17+, min(10% of disk, 10 GB) in Firefox; P) and
stores binary without base64, but it is evicted, cleared and capped by the same policies as localStorage: Safari
deletes all script-writable storage after seven days of Safari use without interaction, and no engine promises to
keep best-effort data (P). Only a file the user holds is safe; the app already writes `.acad3d.json` by download
and reads it back. An installed app on Pages adds offline use, Safari's own day counter for home-screen apps, and
the conditions under which browsers grant `persist()`. The recommendation is all three, in three phases: an
IndexedDB project store with a copy-not-move migration (A), real files with a visible "not saved to a file" state
and the File System Access pickers where Chromium has them (B), and a manifest plus a service worker at
`/BIM-Personal/sw.js` (C). The `file://` build keeps working, with browser storage as a cache and files as the save.
Ten decisions for the owner close the note (part 11).

## 2. The question and the hypotheses

**The question.** Where should the app keep a project so that (a) a project of tens to hundreds of megabytes can be
saved, (b) it is not lost to the browser, to a crash or to a second tab, (c) it can be saved to and opened from a
real file, and (d) the app can be installed and used offline, in Chrome/Edge, Firefox and Safari on macOS and iOS,
from Pages and from `file://`, in ES5 with no dependency? A good answer must decide the store, the file path per
browser, what the offline build does, and what the app tells the user.

| # | Hypothesis (falsifiable) | Outcome | Evidence | Level |
|---|---|---|---|---|
| H1 | localStorage holds about 5 MiB per origin in every browser | **Held**, with the unit corrected: Chromium 5,242,880 UTF-16 units (10 MiB at 2 bytes each), Firefox 5 MiB of UTF-16 units plus a 25 MiB per-site cap, WebKit 5 MB of bytes (1 per Latin-1 character, 2 otherwise) | Chromium, Gecko, WebKit source; e01 (exact, 3 of 3) | P |
| H2 | IndexedDB keeps a 50 MB project in every supported browser in normal mode | **Held** for quota in all three engines; 50 MB read back byte-identical in Chromium | Quota code of all three; e02 | P (Chromium measured only) |
| H3 | IndexedDB keeps a 200 MB project as one value | **Failed** in Chromium: one value may not exceed 133,169,152 bytes (127 MiB); **held** as a Blob or as four 50 MB records | e02, e02b | P (Chromium 153 only) |
| H4 | IndexedDB is usable from ES5 without a library | **Held**: the API is events and callbacks; only `navigator.storage.*` and the file pickers return promises, callable with `.then` | IDB 3.0; draw.io's ES5 layer; the app already uses `.then` in 15 files | P |
| H5 | IndexedDB keeps a project safer than localStorage | **Failed** for eviction and clearing (one policy for both, whole origin at once); **held** for size and binary data | WebKit 2020 and 2023 posts; Storage Standard; prior art | P |
| H6 | `persist()` protects data in every browser | **Partly held**: it exempts from pressure and LRU eviction where granted, but Firefox asks the user, Chrome decides silently from engagement, install or bookmarks, WebKit grants only to exempt domains (a home-screen app among them); headless Chromium answered `false` | Storage Standard; WebKit source; web.dev 2020 (S); e04 | P / S |
| H7 | Safari's 7-day rule deletes the IndexedDB of a site the user stops interacting with | **Held** for Safari the browser; home-screen web apps "have their own counter of days of use", which is not an exemption | WebKit 2020 post; independent check item 4 | P |
| H8 | localStorage and IndexedDB work from `file://` in all three engines | **Failed**: Chromium shares one `file://` origin among every local page (measured); Firefox gives each file its own origin; WebKit refuses both with SecurityError unless a quirk or universal access is on | e05; Bugzilla 1730419, 1500453; WebKit source | P (Safari.app's settings U) |
| H9 | Chrome's default IndexedDB durability is "relaxed" | **Held** since Chrome 121; "strict" about 2.3 times slower here; committed data survived SIGKILL under both | Chrome's post; e08 | P |
| H10 | A second tab blocks a schema upgrade unless it closes on `versionchange` | **Held**, 6 of 6 runs | IDB 3.0 § 5.1; e09 | P |
| H11 | Moving to IndexedDB removes the main-thread cost of a save | **Failed**: `put()` clones on the main thread (15 ms for a 4 MB string, 56 ms for 40 MB); it removes the cold synchronous read (41 ms for 4 MB) and the cap | e07 | P (Chromium) |
| H12 | The File System Access pickers exist only in Chromium, and Firefox and WebKit decline them | **Held**: Chrome/Edge 86, Chrome Android 132; Mozilla "negative", WebKit "oppose" | BCD; standards-positions data | P |
| H13 | The pickers are refused from `file://` | **Failed** in Chromium: reached the dialog from `file://` (headless aborted it), against the specification's opaque-origin rule | e12; WICG FSA § 3 | P (measured up to the dialog) |
| H14 | OPFS works in every engine and is safer than IndexedDB | **Partly**: in all three engines (Safari 15.2+), but not in Safari private windows, refused on `file://` in Chromium, same quota and same eviction; a 64 MiB whole write was no faster than IndexedDB | BCD; WebKit 2022; web.dev; e12 | P |
| H15 | Installing needs a service worker; a service worker cannot run from `file://` | **First failed** for Chrome's menu install (no fetch handler since 108 mobile / 112 desktop), **second held** (TypeError, measured) | Chrome's post; SW spec; e12 | P |
| H16 | gzip through `CompressionStream` is in all current engines and shrinks project JSON several-fold | **Held**: Chrome 80, Firefox 113, Safari 16.4; ratios 0.108, 0.226 and 0.344 on three synthetic models; it stalls the main thread 86 to 131 ms for 4 MB | BCD; e10; e12 | P (ratios synthetic) |

## 3. Method

**Five research notes and a check, written in parallel on 2026-10-31**, one agent for each side of the question, as
the protocol's step 10 asks. Each holds its own search log, its hypotheses and its gaps; this note is written from
them and cites them, and where they disagree it says so.

| Note | Side | Search log |
|---|---|---|
| [storage-standards-and-browsers.md](research-local-storage/storage-standards-and-browsers.md) | The standards and each engine's quota, eviction, persistence, durability, private mode, `file://`, known bugs | its "Search and fetch log", 31 entries |
| [files-and-install.md](research-local-storage/files-and-install.md) | File System Access, downloads, OPFS, manifest, service worker, file handling, compression | its "Method: search log", 13 entries |
| [prior-art.md](research-local-storage/prior-art.md) | Excalidraw, tldraw, draw.io, Graphite, That Open, Figma, and the IndexedDB libraries, read as text at pinned commits | its "Search log", 19 entries |
| [app-code-audit.md](research-local-storage/app-code-audit.md) | Every storage use in `src/` at commit 179cc2f, the save format, tabs, files, errors, tests | its "Search log", 13 entries |
| [experiments.md](research-local-storage/experiments.md) | Ten hypotheses measured in Chromium, and what the built app writes at boot | its scripts table |
| [independent-check.md](research-local-storage/independent-check.md) | Step 9: a second reader re-opened the source of every fact the plan uses | its summary table |

**Sources by kind** (part 12 lists each):

| Kind | Count | Examples |
|---|---|---|
| Specifications and standards | 7 | IndexedDB 3.0, WHATWG Storage, WHATWG File System, WICG File System Access, Web App Manifest, Service Workers, WICG manifest incubations |
| Browser source code, read as text | 24 | Chromium 10 files, Gecko 3, WebKit 11 |
| Vendors' own documents | 18 | WebKit blog 5, Chrome for Developers 6, web.dev 5, Firefox release notes 1, GitHub Docs 1 |
| Curated reference data | 21 | MDN content 4 pages, MDN browser-compat-data 15 files, Mozilla's and WebKit's standards-positions data 2 |
| Bug records | 17 | WebKit 10, Bugzilla 5, WICG issue 1 (S), Excalidraw issue 1 |
| Open implementations, at pinned commits | 10 | idb-keyval, idb, safari-14-idb-fix, localForage, Dexie, Excalidraw, tldraw, draw.io, Graphite, That Open |
| Product documents | 2 | Figma's offline help, draw.io's offline page |
| The app's own code | about 40 files | `src/js/engine/` at commit 179cc2f (part 8) |
| Search pointers kept as U | 12 | listed in part 12, group H |

**Experiments.** Thirteen scripts in [reference/experiments/local-storage/](experiments/local-storage/): `_lib.js`
(a localhost server and helpers), `e01` to `e11` with `e02b` (the storage hypotheses), and `e12` (the files and
install surface; the files note calls it e10, the number it had before it was renumbered to end a clash with
`e10_compression.js`). Environment: Chromium build chromium-1243 (`browser.version()` 153.0.8010.12), headless,
driven by Playwright 1.63.0 under Node 22.23.4, on a Linux virtual machine of 4 vCPU and 16 GB RAM. Three to five
runs each, every run in a fresh context or a fresh profile; raw JSON in the session's scratch directory, numbers
copied into the notes and into part 6. Firefox and WebKit are not installed here, and nothing was installed. The
app-code audit also took measurements of the built app with scratch scripts that were not kept (part 9).

**The independent check.** A second reader re-opened every source behind the 28 facts the plan uses, without
quoting the notes, and re-ran e01 and e05: **28 facts, 27 confirmed, 1 corrected, 0 not confirmed**. The
correction: WebKit bug 273827 was closed on 2024-07-25 as CONFIGURATION CHANGED, with Apple's comment that it is
fixed in iOS 17.6 (and iOS 18) by an operating-system change outside WebKit; one user reported it again on
2025-10-10, without a new bug. Two further cautions came from the check and are applied here: the home-screen web
app has its own day counter for the 7-day rule and is not called exempt; and Firefox's `file://` history is that
localStorage became per file in Firefox 92 (bug 1599979), while unique file origins in general came in Firefox 68
(bug 1500453, whose pref was `privacy.file_unique_origin`, now gone from the source); the live pref is
`security.fileuri.strict_origin_policy`.

**Refused hosts.** `github.com` web pages and the GitHub API (proxy 403, "sessions are bound to their configured
repositories"; raw.githubusercontent.com and blobless clones used instead, and the WICG issue read through the fetch
tool's digest, S); `support.mozilla.org` (a JavaScript challenge page); `firefox-source-docs.mozilla.org`'s quota
page (404, moved; the Gecko source read instead).

## 4. Findings by topic

Confidence is high, medium or low, with the reason in the row.

### 4.1 Browser quotas and limits

Quota is not the constraint for a CAD or BIM project in any current engine in a normal window; localStorage is.

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Chromium: pool 80% of total disk, per origin 0.8 x 0.75 = **60% of total disk**, best-effort and persistent alike | `quota_features.cc`, `quota_settings.cc`; MDN agrees | P | High (code, checked twice) |
| Chrome reports 60% of the disk in `estimate()`, not free space, to limit cross-origin size leaks | web.dev, 2024-09-23 | S | Medium |
| Firefox: temporary storage up to 50% of disk (an 8 TiB cap); a site group (eTLD+1) gets min(limit / 5, 10 GB) = **min(10% of disk, 10 GB)**; a persisted origin is bounded only by the 50% limit | Gecko `dom/quota/ActorsParent.cpp` | P | High |
| Safari 17+ and WebKit apps on iOS 17 and macOS Sonoma: origin **60%** of disk and overall 80% for a browser app, 15% / 20% for other apps; cross-origin frames 10% of the parent's quota; a standalone (Home Screen or Dock) app has the browser's quota; no "use more space?" prompt any more | WebKit post 14403 (2023-08-10); `WebsiteDataStoreCocoa.mm` | P | High |
| The often-quoted "Safari 1 GB then a prompt" and "Firefox 2 GB group" are from before these changes | web.dev's older text against the code | S | High that they are out of date |
| Exceeding quota fails a write with `QuotaExceededError`, now a DOMException-derived interface (IDB 3.0, issue #463); its `name` is unchanged | IDB 3.0 revision history; WebKit post | P | High |
| localStorage: Chromium rejects a set when (key + value) x 2 > 10 MiB, i.e. **5,242,880 units for all keys of the origin together**; measured exactly, the same for U+4E00 as for Latin-1; error `QuotaExceededError`, code 22 | `dom_storage_constants.h`, `cached_storage_area.cc`; e01 (3 of 3, re-run by the checker) | P | High |
| localStorage: Firefox 5 MiB of UTF-16 units per origin (`dom.storage.default_quota`), 25 MiB per site; WebKit 5 MB of bytes, where a string with any non-Latin-1 character counts 2 bytes per character (about half as many characters) | `StaticPrefList.yaml`; `LocalStorageManager.cpp`; WTF::String's byte count is S | P / S | High / medium |
| localStorage use does not appear in `estimate()` (4 MiB moved `usage` by 0 in 12 runs) | e03 | P (Chromium) | High |
| Private windows: Chrome incognito pool is 15 to 20% of RAM, one third per origin (about 200 to 270 MB per origin on a 4 GB device); Firefox has IndexedDB in private windows (pref on, meta bug 1639542 fixed 2024-03-04; first release 115 is U); Safari private IndexedDB quota not found | `quota_settings.cc`; Gecko prefs; Bugzilla | P / U | Medium |
| Another kind of size limit: one IndexedDB value may not exceed **133,169,152 bytes** in Chromium 153 (`UnknownError`, "The serialized keys and/or value are too large"); values above 65,536 bytes are stored outside the record ("wrapping") | e02, e02b; `indexeddb.mojom`, `idb_value_wrapping.cc` | P (measured; the reason for 127 MiB not read, U) | High for this build |

What the app's projects weigh (app-code audit, measured in the built app from `file://`): an empty project 28,280
characters; 40 walls 46,051; with `site_kit.skp` 53,423; with a 20,000-triangle OBJ 528,922; with a 125,000-triangle
OBJ 3,908,935, about 31 characters per imported triangle. By that rate (an inference, not measured), the SketchUp
importer's own ceiling of 250,000 triangles (`BIM_SKP.maxTris`) would make a record of about 7.75 M characters,
above localStorage's cap before anything else is stored.

### 4.2 Eviction, and Safari's 7-day rule

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| A bucket is "best-effort" until granted "persistent"; under pressure the browser clears best-effort buckets, whole; a persistent bucket is cleared only with the user's or the origin's involvement | Storage Standard § 4, 5, 7 | P | High |
| All engines evict per origin, least recently used, whole; persisted origins and origins with an open page are skipped | WebKit post 14403; Chromium quota README; MDN for Firefox (S, Gecko's eviction code not read) | P / S | High |
| Safari (with tracking prevention, since Safari 13.1 and iOS 13.4) deletes **all script-writable storage** of a site (IndexedDB, localStorage, sessionStorage, service-worker registrations and cache) after **seven days of Safari use** without user interaction on the site; days of use, not calendar days | WebKit post 10218 (2020-03-24); MDN | P | High |
| Home-screen web apps "are not part of Safari and thus have their own counter of days of use"; Apple does "not expect" their first-party data to be deleted and would call it "a serious bug". **This is its own counter, not an exemption**: an installed app left unused can still meet the rule | Same post; independent check item 4 | P | High |
| The home-screen behaviour needs a `standalone` or `fullscreen` display; Apple refused an exception for an app that opens in Safari (WebKit bug 232302, WONTFIX) | WebKit bug 232302 | P | High |
| WebKit's code turns time-based eviction off for apps that are not full browsers; a build flag can narrow it to service workers only; which flag Safari ships is not known | `WebsiteDataStore.cpp`, `WebsiteDataStoreConfiguration.cpp` | P (code) / U (shipping) | Medium |
| Chromium deletes a localStorage area after 400 days without use, and throws the whole localStorage database away after 8 consecutive commit errors | `dom_storage_constants.h` (constants; the code paths not read) | P | Medium-high |
| Browsers also lose data by their own faults: Safari deleted many sites' storage when Web Inspector opened (WebKit 266559, fixed 2024-01-11); Excalidraw's maintainers answer such reports that nothing can be recovered (issue #7870) | WebKit 266559; Excalidraw #7870 | P | High |
| Figma tells its users that offline edits in IndexedDB are kept up to 30 days in most browsers and 7 days in Safari | Figma Learn | P | High |

The conclusion the notes agree on: moving to IndexedDB changes how much can be kept, not how long. A user who saves
a project in Safari and does not interact with the site for seven days of Safari use can lose it from either store.

### 4.3 Persistence: `persist()`

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| `persist()`, `persisted()`: Chrome 55, Firefox 57, Safari 15.2; `estimate()`: Chrome 61, Firefox 57, Safari 17 | BCD, re-read by the checker | P | High |
| Firefox shows a prompt; Chrome and Safari decide without one | MDN; web.dev 2020 | S | Medium-high |
| Chrome's signals: site engagement, installed or bookmarked, notification permission; Chromium's "important sites" code still lists engagement, durable, bookmarks (at most 5 used), home screen, notifications | web.dev 2020 (S, old); `important_sites_util.cc` (the link from `persist()` to it not traced) | S | Medium |
| WebKit grants `persist()` only when the origin's registrable domain is in the exempt set (app-bound, managed, already persisted, or the standalone application's domain) and never in a cross-origin frame; "WebKit currently grants a request based on heuristics like whether the website is opened as a Home Screen Web App" | `NetworkStorageManager.cpp`, `ResourceLoadStatisticsStore.cpp`; WebKit post 14403 | P | High |
| Headless Chromium returned `false` with no grant and with every grant Playwright accepts; `true` only when the permission is set through the DevTools Protocol; `false` on `file://` as well | e04, e05 | P (headless only) | High for headless, nothing for headed |
| web.dev advises asking after a user gesture, not on load, because the browser may prompt | web.dev 2020 | S | Medium |
| None of the storage code read in Excalidraw, tldraw, draw.io or Graphite calls `persist()` | prior-art (storage files only, not whole repositories) | P | Medium |
| A granted `persist()` protects against pressure and LRU eviction; not against the user clearing site data, and, under continued pressure, the browser may ask the user to clear even persistent storage | Storage Standard § 7 | P | High |

`persist()` is cheap, harmless when refused, and the only lever against best-effort eviction; in a Safari tab it
will normally answer `false`, so `false` must be treated as normal, not as an error. Whether a granted `persist()`
also exempts a Safari tab from the 7-day rule is not established (U).

### 4.4 The `file://` mode

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| The specification gives an opaque origin no storage key, so no storage | Storage Standard § 3 | P | High |
| **Chromium**: every `file://` page has the origin `file://` and one shared store: a page in `a/` and another in `b/deeper/` read each other's localStorage and IndexedDB, 6 of 6 runs; `isSecureContext` true; `navigator.storage`, `crypto.subtle`, `CompressionStream` present; `persist()` false | e05 (re-run by the checker, identical); `url/origin.h` | P | High |
| **Firefox**: each file URL is its own origin; for localStorage since Firefox 92 (bug 1599979, 1730419 closed INVALID 2021-11-26), for other storage since Firefox 68 (bug 1500453, pref `privacy.file_unique_origin`, removed since); the live pref is `security.fileuri.strict_origin_policy`, "not really a supported configuration anymore"; Mozilla's advice is to serve from `http://localhost/`. Moving or renaming the file loses its data | Bugzilla 1730419, 1500453, 1599979; `StaticPrefList.yaml` | P | High |
| **WebKit**: IndexedDB, localStorage and StorageManager are refused for a local origin (`IDBFactory.open()` throws SecurityError "called in an invalid security context"; `window.localStorage` throws SecurityError) unless `needsStorageAccessFromFileURLsQuirk` or universal access is on; what Safari.app turns on by default is not known | `ScriptExecutionContext.cpp`, `IDBFactory.cpp`, `LocalDOMWindow.cpp` | P (code) / U (Safari.app) | High for the code |
| No service worker on `file://`: "The URL protocol of the current origin ('null') is not supported" | SW spec, register algorithm; e12 | P | High |
| No OPFS on `file://` in Chromium (`getDirectory()` rejects with SecurityError) | e12 | P | High (one engine) |
| In Chromium the save picker is reached from `file://` (`self.origin` "null", `isSecureContext` true, `showSaveFilePicker()` after a click ends in AbortError, as on localhost, because headless cannot show the dialog), against the specification's SecurityError for an opaque origin | e12; WICG FSA § 3.2 | P (to the dialog only) | Medium |
| A Blob download of 8 MiB was saved from `file://` | e12 | P | High (Chromium) |
| The app's own code already records that `file://` storage is shared by every local page | `src/js/engine/core/storage-theme.js:5-7` | P | High |

So the one-file build cannot rely on browser storage anywhere: in Chromium any downloaded HTML file can read or wipe
the projects, and two copies of the app in different folders share them; in Firefox the projects belong to that
exact path; Safari may refuse storage outright, so even reading `window.localStorage` must sit in a try/catch. For
the one-file build the file on disk is the save.

### 4.5 IndexedDB for ES5: the API, durability, tabs, the value ceiling

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| The current edition is Indexed Database API 3.0, W3C Working Draft of 30 October 2026 (2.0 is the last Recommendation); the data API is events and callbacks; values are copied by StructuredSerializeForStorage, so ArrayBuffer, typed arrays and Blob are stored as they are | IDB 3.0 (TR and editor's draft) | P | High |
| Support floors: IDBFactory Chrome 24, Firefox 16, Safari 8; `getAll` Chrome 48, Firefox 44, Safari 10.1; `commit()` Chrome 76, Firefox 74, Safari 15; `durability` Chrome 83, Firefox 126, Safari 15 | BCD | P (checker) | High |
| Durability hint: "strict" may report success only after the data is on a persistent medium, "relaxed" once handed to the operating system; Chrome's default became relaxed in Chrome 121, "to align with" Firefox and Safari; Chrome names data migration as the case for strict, and says strict too "does not ensure" an immediate disk write | IDB 3.0 § 2.7, 4.4; Chrome's post | P (Firefox's and Safari's defaults S: Chrome's claim, not read in their source) | High |
| Measured: `tx.durability` reports "default" with no option; an unknown value is a TypeError; 200 small transactions took 53 ms relaxed, 56 ms default, 123 ms strict; 50 of 50 committed records survived SIGKILL under both | e08 | P (Chromium) | High here; power loss untested |
| An upgrade waits until every other connection closes: each other tab gets `versionchange`, the opener gets `blocked`; closing inside the `versionchange` handler avoids `blocked` altogether (B upgraded 0.5 ms later); no `close` event fires on a `db.close()` | IDB 3.0 § 5.1; e09 (6 of 6) | P | High |
| Every library and app read closes the connection on `versionchange` (localForage, Dexie, tldraw on "blocking", draw.io, whose `onblocked` is an empty TODO) | prior-art § 4 | P | High |
| A connection can drop on its own: idb-keyval clears its cached connection on `onclose` ("Safari sometimes likes to just close the connection"); localForage reopens and retries once on `InvalidStateError` or `NotFoundError`; Dexie retries `UnknownError` a bounded number of times (a Chrome bug after clearing site data) | prior-art § 6, checked (14c) | P | High |
| WebKit bug 273827, "Connection to Indexed Database server lost" (iOS 17.4, networking process crash, "hundreds of users"): closed 2024-07-25 CONFIGURATION CHANGED, Apple saying it is fixed in iOS 17.6 and iOS 18 by an OS change; one user reported it again 2025-10-10. WebKit 292142 (iOS 18.4, reading Blobs from IndexedDB killed the networking process) fixed 2025-07-08 | WebKit bugs, read through REST; corrected by the checker | P | High |
| Safari 14.6 lost IndexedDB requests that never answered (fixed in 14.7); Dexie still ships the workaround (poll `indexedDB.databases()` before the first open) | safari-14-idb-fix README and code; Dexie | P (WebKit bug 226547 itself not opened) | Medium-high |
| A transaction closes once it has nothing left to do after the microtasks run: nothing unrelated may be awaited inside it; writes resolve on the transaction's `complete`, not the request's `success`, and quota errors usually arrive as an abort | idb README; idb-keyval | P | High |
| Main-thread cost (4,008,905-character model): `JSON.stringify` 25.7 ms, `localStorage.setItem` 16.9 ms, cold `getItem` after a restart 40.8 ms; IndexedDB `put()` of the same string blocks 15.2 ms for the clone, of a 40 MB ArrayBuffer 55.9 ms; `get()` blocks 1.3 ms or less | e07 (5 runs) | P (Chromium) | High here |
| Value ceiling: 50 MB ArrayBuffer and 50 MB string stored and read back byte-identical; 200 MB as one value refused; the largest ArrayBuffer accepted 133,168,640 bytes; a U+4E00 string costs 2 bytes per character (66 M characters accepted, 67 M refused); 200 MB as a Blob (put about 10 ms) or as four 50 MB records in one transaction (about 600 ms) accepted and byte-identical | e02, e02b | P (Chromium 153) | High here; other engines unknown |
| Data survives a browser restart on one profile, over http and `file://`, 3 of 3; a fresh context sees none of it; the port is part of the origin | e06 | P | High |

### 4.6 Files on disk

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| The File System Access API is a WICG Draft Community Group Report (10 October 2025), "not a W3C Standard nor ... on the W3C Standards Track"; its base interfaces moved to the WHATWG File System Living Standard | WICG FSA; WHATWG FS | P | High |
| `showOpenFilePicker` and `showSaveFilePicker`: Chrome 86, Edge, Chrome Android 132; Firefox and Safari none; Mozilla #154 "negative" (cross-site access to the user's files lacks meaningful consent), #738 subset "defer"; WebKit #28 "oppose" (security) | BCD; standards-positions data | P | High |
| Pickers need a secure context, the top-level origin and a user gesture; a cross-origin frame got SecurityError ("Cross origin sub frames aren't allowed to show a file picker") | WICG FSA § 3; e12 | P | High |
| A stored handle (handles are serialisable into IndexedDB) usually answers "prompt" on a later visit; Chrome 122 shows "Allow this time / Allow on every visit / Don't allow", and an **installed** app keeps the grant without the three-way prompt; VS Code for the web keeps handles in IndexedDB the same way | WICG FSA § 2.3; Chrome posts (2024-01-09, 2024-08-19) | P | High for the rules, medium for current detail |
| `createWritable` exists in Firefox 111 and Safari 26 too, but only for OPFS files there, since neither has a picker to hand over a user-visible handle | BCD; WebKit bug 231706's thread | P (the inference is the note's) | High |
| Download fallback: `<a download>` works for same-origin, `blob:` and `data:` URLs; a 64 MiB Blob download completed on localhost (67,108,864 bytes) and an 8 MiB one from `file://`; revoking the object URL a moment later is the safe pattern (WebKit 212279 fixed 2020) | MDN; e12; WebKit 212279 | P | High (Chromium measured) |
| iOS Safari opens TXT and XML downloads in a tab instead of saving them (WebKit 263608, NEW since 2023-10-24); one user's workaround is a Blob typed `application/octet-stream`; whether `application/json` is affected is not stated | WebKit 263608 | P (bug) / U (the workaround, JSON) | Medium |
| Chromium Blob limits: in memory 2 GB on 64-bit desktop, 1% of RAM on Android, larger Blobs paged to disk (disk limit 10% of disk desktop, 6% Android) | Chromium blob README | P | High |
| Prior art: every app read treats a file as the user's backup; Excalidraw saves through browser-fs-access, passing the existing handle so a later save overwrites the same file where the API exists, and downloading elsewhere | prior-art § 1; Excalidraw `filesystem.ts` | P | High |
| Opening by double-click (`file_handlers` plus `launchQueue`) is Chrome 102 desktop only, installed apps only, with a permission prompt; Mozilla "defer"; `window.launchQueue` exists even on an uninstalled page and on `file://`, so its presence proves nothing | BCD; Chrome docs; e12 | P | High |
| Test harness: reading a stored `FileSystemFileHandle` back from IndexedDB closed the whole browser in an off-the-record Playwright context, in both Chromium binaries; it works in a persistent profile | e12 probes | P (measured; a real Incognito window untested) | Medium |

### 4.7 Installing and offline

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| "Any website is an installable web application" (manifest editor's draft; TR a Working Draft of 26 October 2026) | W3C manifest | P | High |
| Chrome's install promotion needs HTTPS, a click and 30 seconds on the page, a manifest with `name` or `short_name`, 192 and 512 px icons, `start_url`, `display` standalone (or fullscreen, minimal-ui, window-controls-overlay); "users can install your web app even if it doesn't meet" them | web.dev install criteria (2024-09-19) | P | High |
| Chrome dropped the fetch-handler requirement for installing from the menu (108 mobile, 112 desktop) and shows a default offline page; the automatic prompt "still requires" a fetch handler as of 2023-12-05; whether that is still so is open | Chrome post | P | Medium |
| Safari 17 (macOS): any site can be added to the Dock, manifest or not; only cookies are copied into the web app, "no other kind of local storage" | WebKit post 14445 | P | High |
| Safari 26 (iOS and iPadOS): every site added to the Home Screen opens as a web app; "zero requirements for 'installability'"; home-screen apps "never required Service Workers" | WebKit post 17333 | P | High |
| Firefox 143 (2025-09-16) pins sites as web apps to the Windows taskbar (not Microsoft Store builds); BCD lists no desktop Firefox manifest support | Firefox release notes; BCD | P | High |
| A service worker controls only paths under its script's folder (measured: a worker at `/app/sw/sw.js` refused for `/app/`) unless the server sends `Service-Worker-Allowed`, which Pages cannot (U: no GitHub page says so) | SW spec § 6.5; e12 | P / U | High for the rule |
| Pages serves `github.io` sites over HTTPS automatically | GitHub Docs | P | High |
| A worker updates when its script is byte-different; Chrome 68+ ignores HTTP caching for that check; a new worker waits until no page uses the old, unless `skipWaiting()`, which leaves old pages under a new worker | web.dev lifecycle | P (Chrome's team) | High |
| Installing helps storage: Safari's home-screen and Dock apps keep their own day counter and are a `persist()` heuristic; Chrome lists "installed" among its `persist()` signals (2020 page, S) and keeps file permissions for installed apps (Chrome 122) | WebKit posts; web.dev; Chrome post | P / S | High (WebKit), low-medium (Chrome's `persist()`) |

### 4.8 Compression

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| `CompressionStream` and `DecompressionStream` with gzip and deflate: Chrome 80, Firefox 113, Safari 16.4; deflate-raw Chrome 103; brotli Firefox 147 and Safari 18.4, not Chrome (TypeError measured); Mozilla's position "positive" | BCD; e10 | P | High |
| Ratios on synthetic models: 0.108 on an 8,007,274-byte model of 60,000 elements (e12); 0.226 on a repetitive 4.1 MB model and 0.344 on a varied 4.0 MB model (e10); round trips exact (30 of 30) | e10, e12 | P (synthetic data) | Medium for real projects |
| Time for 4 MB: compress 110 to 151 ms, decompress 19 to 24 ms; **the compression stalled the main thread 86 to 131 ms** in this build | e10 | P | High here |
| Compressed bytes in localStorage need base64 (a third larger), so compression does not rescue localStorage | experiments.md H10 | Inference (arithmetic) | Medium |
| A loader can tell a gzip file by its first two bytes, 1F 8B | gzip's format (files note's inference; RFC 1952 not re-read) | S | High |

The two compression measurements disagree in ratio because their inputs differ (60,000 small elements against 4,600
elements with 96 pseudo-random coordinates each); neither is a real BIM-Personal project, of which the repository
holds none (part 10).

### 4.9 The shared `github.io` origin

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Quotas, localStorage, IndexedDB and OPFS belong to the whole origin `https://bradleypham1906.github.io`, "even if this origin is used to run several websites" such as `/site1/` and `/site2/` | MDN quotas | S (MDN, consistent with the Storage Standard's storage key) | High |
| Every Pages project of the account, and the old builds `tools/build_site.py` keeps under `/BIM-Personal/v/<version>/`, share that one store; an old build can read and overwrite the current build's projects, and an old build opening a database a newer build upgraded gets `VersionError` | files note; prior-art § 3 (localForage, Dexie) | P (build script) / inference | High |
| A service worker at `/BIM-Personal/sw.js` would cover `/BIM-Personal/v/` too | SW path rule | P | High |
| The Pages origin and a `file://` copy are separate origins, so their stores never meet | app-code audit § 9 | P | High |

## 5. The alternatives compared

**Criteria, set before the comparison.** What the app needs: (1) capacity for projects of 50 MB and more; (2)
survival against eviction and clearing, which is the user's real risk; (3) the same behaviour in Chrome/Edge, Firefox
and Safari on desktop, tablet and phone; (4) the one-file build from `file://` keeps working; (5) the build
contract: ES5, no dependency, one app served by Pages. What it costs: (6) the work and the code to maintain. What it
breaks: (7) the synchronous boot, the `pagehide` flush, the six suites that address `acad3dV1`.

| Option | 1 Capacity | 2 Survival | 3 All engines | 4 `file://` | 5 Contract | 6 Cost | 7 Breaks |
|---|---|---|---|---|---|---|---|
| A. Keep localStorage | **No**: 5,242,880 units per origin; projects over half of it cannot be switched | Same eviction as IndexedDB; Chromium also drops it after 8 commit errors | Yes; Safari counts bytes, about half for non-Latin-1 text | Shared in Chromium, per file in Firefox, refused in Safari | Yes | None | Nothing; the wall stays |
| B. IndexedDB only | Yes: 60% / 10% / 60% of disk; one value under 127 MiB in Chromium | **No better**: the 7-day rule and LRU eviction apply equally | Yes, from Safari 8; durability from Safari 15 / Firefox 126 | As A | Yes (callbacks) | Medium: a wrapper, migration, two-stage boot | Synchronous boot and `pagehide`; suites |
| C. IndexedDB plus files | As B | **Yes for what the user saved to a file**; browser copy remains a cache | Yes: pickers in Chromium, download and `<input type=file>` elsewhere (already in the app) | Yes: the file path works there; picker reached in Chromium | Yes | B plus a file state and pickers | As B |
| D. OPFS for projects | Yes, same quota | **No better**: same eviction; cleared with site data | Yes from Safari 15.2; **not in Safari private windows**; sync handle only in workers | **No** in Chromium (SecurityError) | Yes, but a worker for the fast path | High: a worker, a second store | As B, plus a worker in a one-closure engine |
| E. IndexedDB plus files plus an installable app (recommended) | As B | As C, plus Safari's own day counter for a home-screen app, `persist()` heuristics favouring installed apps, Chrome 122's kept file permissions | Install in Chrome/Edge, Safari 17 (Dock), Safari 26 (Home Screen), Firefox 143 (Windows); offline only with a worker | As C; the worker is a Pages feature only | Yes: a JSON manifest, icons, one ES5 worker file | C plus a manifest, icons and a worker with its update rules | As B; the Pages build gains two files |
| F. A desktop wrapper (Electron, Tauri and the like) | Real files, no browser quota | Real files | **No phone or tablet** through the web; separate builds per OS | Replaces it | **No**: adds a runtime and a separate delivery; `reuse-first-integration.md` forbids changing the delivery contract without the owner's approval | High | The delivery model |

Option F was not researched in the notes beyond this: no wrapper's documents or code were read, so its column is
judged only against the app's written contract and the owner's "everything on phone, tablet and desktop" (U for any
claim about a wrapper's behaviour).

**Recommendation: E, built in three phases** (A, B and C in part 11, decision 1). B alone moves the wall without
making anything safer; C is what makes a project safe; E adds offline use and the browsers' better treatment of
installed apps at small cost. OPFS (D) is kept for later as a cache for large derived binaries (meshes, terrain
tiles) that the project file can rebuild, not for the project itself.

**What would change it.** Firefox or Safari shipping save pickers (then "Save" overwrites in place everywhere);
evidence that headed Chrome grants `persist()` to an installed site, or never does (the weight of phase C); real
projects that routinely pass about 120 MB as JSON (then a chunked or Blob body is needed in phase A, and OPFS
becomes worth its worker); a measured IndexedDB failure in Firefox or Safari that the wrapper cannot recover from;
the owner choosing a native desktop app, which only F answers.

## 6. The experiments

All in Chromium 153.0.8010.12 (chromium-1243), headless, Playwright 1.63.0, on 2026-10-31; scripts in
[reference/experiments/local-storage/](experiments/local-storage/); full tables in
[experiments.md](research-local-storage/experiments.md) and [files-and-install.md](research-local-storage/files-and-install.md).

**e01, localStorage's limit** (3 runs, spread 0; re-run by the checker, identical)

| Case | Largest value accepted | Key + value |
|---|---|---|
| Latin-1, key of 1 character | 5,242,879 | 5,242,880 |
| U+4E00, key of 1 character | 5,242,879 | 5,242,880 |
| Key of 100 characters | 5,242,780 | 5,242,880 |
| Several keys (4 x 1 Mi, then a top-up) | 1,048,556 top-up | 5,242,880 in total |
| Error | `QuotaExceededError`, code 22, a DOMException | |

**e02 and e02b, large values in IndexedDB** (3 runs, plus 1 in the full binary)

| Value | Result | put to `complete` (ms) | get (ms) |
|---|---|---|---|
| ArrayBuffer 50 MB | Stored, SHA-256 identical | 195.3, 179.9, 187.6 (mean 187.6) | 105.6, 139.4, 110.5 (mean 118.5) |
| JSON string 50 MB | Stored, identical | 289.0, 562.0, 265.3 (mean 372.1) | 116.9, 470.9, 117.9 (mean 235.2) |
| ArrayBuffer or string 200 MB | Refused, `UnknownError`, "size=200000068 bytes, max=133169152 bytes" | | |
| Largest ArrayBuffer | 133,168,640 bytes accepted; 133,169,328 refused | | |
| U+4E00 string | 66,000,000 characters accepted, 67,000,000 refused (134,000,050 bytes) | | |
| Blob 200,000,000 bytes | Stored, identical, 4 of 4 | 11.9, 9.8, 10.0, 9.8 | 257.5, 229.9, 270.8, 244.9 (with `arrayBuffer()`) |
| 4 x 50 MB records, one transaction | Stored, reassembled identical, 4 of 4 | 590.1, 620.4, 604.9, 583.8 | 272.9, 274.2, 334.3, 273.8 |

**e03, `estimate()`** (3 runs per row)

| Context | Quota before (bytes) | Rise after a 100,000,000-byte put | Rise after 4 MiB of localStorage |
|---|---|---|---|
| Persistent profile (shell and full) | 10,737,418,240 (10 GiB) | 100,002,076 | 0 |
| Fresh context (shell) | 4,294,967,296; 3,221,225,472; 3,221,225,472 | 100,167,680 | 0 |
| Fresh context (full) | 3,221,225,472 x 3 | 100,167,680 | 0 |

Quota was reported as usage plus a fixed headroom (after the write, 10,837,420,316 = 10 GiB + 100,002,076), not as
60% of the 270.6 GB disk; the rule behind the headroom was not read (U).

**e04, `persist()`** (3 runs per cell, fresh context and profile, shell and full: 48 + 24 page loads, all alike)

| Grant | `persisted()` before | `persist()` | after |
|---|---|---|---|
| None | false | false | false |
| Playwright `notifications` or `storage-access` | false | false | false |
| Playwright `persistent-storage` | refused: "Unknown permission" | false | false |
| DevTools `Browser.setPermission` or `grantPermissions(['durableStorage'])` | true | true | true |

**e05, `file://`** (3 fresh + 3 profile runs; re-run by the checker): origin `"file://"` on both pages; pages in
different folders read each other's localStorage and IndexedDB, 6 of 6; `isSecureContext` true; quota 3,221,225,472
(fresh) and 10,737,418,240 (profile); `persist()` false 12 of 12.

**e06, restart** (3 runs each, http and `file://`): a 1 MiB localStorage value and a 10 MB IndexedDB buffer read
back identical after relaunching on the same profile; a fresh context saw none (localStorage length 0,
`upgradeneeded` fired).

**e07, main-thread cost** (4,008,905-character model, 5 runs, ms)

| Operation | Mean | Range |
|---|---|---|
| `JSON.stringify` | 25.7 | 20.7 to 40.5 |
| `JSON.parse` | 20.8 | 15.6 to 36.8 |
| `localStorage.setItem` | 16.9 | 14.9 to 20.4 |
| `localStorage.getItem`, first after a browser restart | 40.8 | 33.3 to 53.2 |
| IndexedDB `put(string)`, longest main-thread stall | 15.3 | 14.7 to 15.8 |
| IndexedDB `put(4 MB ArrayBuffer)`, stall | 6.5 | 5.7 to 7.6 |
| IndexedDB `put(40 MB ArrayBuffer)`, stall | 56.8 | 52.1 to 66.2 |
| IndexedDB `get(string)`, stall | 1.3 | 1.1 to 1.4 |
| IndexedDB `get(40 MB)`, stall | 1.2 | 1.1 to 1.2 |

**e08, durability** (200 sequential transactions of 1 KB, 3 runs, ms): relaxed 53.1 (51.1 to 55.6); strict 123.4
(113.4 to 137.0); default 55.9; no option 58.7. SIGKILL after 50 committed transactions: 50 of 50 survived under
relaxed and strict, 3 of 3 runs.

**e09, two tabs** (3 runs per variant, ms from A's first event)

| Variant | A `versionchange` | B `blocked` | A closes | B `upgradeneeded` | B `success` |
|---|---|---|---|---|---|
| A closes 500 ms later | 4.6 to 4.9 | 4.9 to 5.2 | 505.1 to 505.3 | 506.0 to 506.3 | 506.4 to 506.6 |
| A closes in its handler | 3.6 to 5.3 | none | 3.6 to 5.3 | 4.1 to 5.7 | 4.4 to 6.1 |

**e10, compression** (5 runs each)

| Input / format | Out bytes | Ratio | Compress mean (ms) | Longest stall (ms) | Decompress mean (ms) |
|---|---|---|---|---|---|
| Repetitive 4,124,639 B / gzip | 931,299 | 0.226 | 120.2 | 86.3 to 115.1 | 19.5 |
| Repetitive / deflate-raw | 931,281 | 0.226 | 109.8 | 84.5 to 93.4 | 21.2 |
| Varied 4,008,905 B / gzip | 1,379,445 | 0.344 | 137.5 | 107.9 to 130.8 | 23.5 |
| Varied / deflate-raw | 1,379,427 | 0.344 | 150.7 | 108.1 to 127.0 | 22.2 |

**e11, the built app at boot** (3 runs over http, 3 from `file://`): `acad3dDocsV1` (173 to 176 units) at the load
event; `acad3dV1` (28,260 to 28,261) within 5 seconds; no sessionStorage, no IndexedDB, `estimate().usage` 0; no page
errors.

**e12, files and install surface** (Chromium; timings 3 runs)

| Test | Result |
|---|---|
| Pickers on `file://` after a click | Present; `AbortError` (headless cannot show the dialog), as on localhost |
| Picker in a cross-origin frame | `SecurityError` |
| Service worker on `file://` | `TypeError`, protocol "null" not supported |
| Worker at `sw/sw.js` | Scope `/app/sw/` and below accepted; `/app/` refused |
| OPFS on `file://` | `SecurityError` |
| 64 MiB write: OPFS `createWritable` | 121.4 ms mean (111.6 to 127.5) |
| 64 MiB write: IndexedDB `put(Blob)` | 96.8 ms mean (88.7 to 101.2) |
| 64 MiB write: worker sync handle, 4 MiB chunks | 284, 146.3, 71.8 ms (with worker start-up) |
| gzip of an 8,007,274-byte model | 860,941 bytes (0.108); 99 to 117 ms; decompress 29 to 33 ms |
| Blob download | 67,108,864 bytes saved on localhost; 8 MiB from `file://` |
| Handle read back from IndexedDB, off-the-record context | Browser closed; in a persistent profile, `isSameEntry` true |

**The app audit's own measurements** (built app from `file://`, scratch scripts not kept): with a
3.9 M-character project open, New project failed with "There is not enough browser storage to switch projects"
because parking needs a second copy; the envelope's `JSON.stringify` 28 to 31 ms, `setItem` 11 ms; localStorage
filled after 19 chunks of 262,144 characters on top of 28,437, about 5.0 M characters.

What the experiments show, together: the localStorage wall is exact and close; IndexedDB in Chromium takes 50 MB
values easily and 200 MB only as a Blob or in parts; durability and multi-tab behaviour are as the specification
says; nothing measured here speaks for Firefox, Safari, phones, or a headed browser's `persist()`.

## 7. Edges

The cases where the answer changes, for the test data.

| Edge | Below | Above or otherwise |
|---|---|---|
| localStorage, all keys of the origin together (Chromium, Firefox) | 5,242,880 UTF-16 units saves | one more unit throws `QuotaExceededError` |
| localStorage in WebKit | 5 MB of bytes, one byte per Latin-1 character | about half as many characters once a value holds a non-Latin-1 character (a degree sign is Latin-1; "≥" or CJK text is not) |
| Switching projects under localStorage | a project under about half the cap can be parked | above it, "not enough browser storage to switch projects" |
| One image note | a 4 MB image is about 5.6 M characters of base64 | alone above localStorage's cap; the importer refuses images over 4 MB |
| SketchUp import ceiling | 250,000 triangles at about 31 characters each, about 7.75 M characters (inference) | above localStorage's cap; fine in IndexedDB |
| One IndexedDB value, Chromium 153 | 133,168,640 bytes stored | 133,169,328 refused with `UnknownError`; a non-Latin-1 string costs 2 bytes per character |
| Chromium's record wrapping | values up to 65,536 bytes inline | larger values in separate files (where "missing large-value file" errors arise) |
| Safari's 7-day rule | interaction within seven days of Safari use | all script-writable storage deleted; a home-screen app counts its own days |
| Home-screen display mode | `standalone` or `fullscreen` opens as a web app with its own counter | an app that opens in Safari has none (WebKit 232302) |
| Firefox group limit | best-effort: min(10% of disk, 10 GB) per site | persisted: up to 50% of disk |
| Frames | top-level page: full origin quota | cross-origin frame: 10% in Safari; no picker; no `persist()` in WebKit |
| Private windows | Chrome incognito: 15 to 20% of RAM, a third per origin | gone when the window closes, in every engine |
| `file://` | Chromium: one shared store | Firefox: per file (localStorage since 92, other storage since 68); Safari: refused |
| Service worker scope | under the script's folder | above it refused; Pages cannot send `Service-Worker-Allowed` (U) |
| Picker support | Chrome/Edge 86 desktop, Chrome Android 132 | Firefox, Safari, iOS: download and `<input type=file>` only |
| Compression | Safari 16.4, Firefox 113, Chrome 80 and later | older engines: save plain JSON |
| `persist()` support | Safari 15.2, Firefox 57, Chrome 55 and later | absent: treat as best-effort |
| Durability option | Safari 15, Firefox 126, Chrome 83 and later | older engines ignore the dictionary member; an unknown value is a TypeError |
| Database versions | the same or newer app opens the store | an older copy on the same origin (a cached tab, an old `v/` build) gets `VersionError`; the `file://` copy is another origin |
| Chrome's localStorage | used within 400 days, fewer than 8 consecutive commit errors | deleted after 400 idle days; the whole database thrown away after 8 errors |
| Test harness | a persistent profile keeps stored file handles | an off-the-record context closes the browser when a handle is read back |
| Seeding storage in tests from `file://` | seeding from a blank page of the same origin | an init script touching localStorage cut the page's storage off in about half of runs (`tests/bim_phase115...:74-79`) |

## 8. What the app already has

All from the app-code audit at commit 179cc2f, confirmed by the checker where marked (15a to 15h); paths under
`src/js/engine/`.

| What | Where |
|---|---|
| The project on screen, key `acad3dV1` (`LSK`) | `core/state.js:1` (15a) |
| Boot reads it synchronously inside the closure, applies it, takes `docId` as `A3D_BOOT_DOC`; a failure warns, no toast | `core/state.js:110-119` (15b) |
| The project list `acad3dDocsV1` and parked projects `acad3dDocV1:<id>`; `A3D_DOCS=bimDocsBoot()`; per-project undo and view in memory (`A3D_DOC_RT`) | `core/state.js:121-123` (15b); `ui/project-tabs.js:41-100` |
| "The one list of what a project is", `bimProjectRecord()`; `A3D_PROJECT_DEFAULTS` from it | `core/objects-save.js:39-44`; `core/state.js:44` |
| `save3d()` writes `acad3dV1` whole; on failure one `console.warn` and one toast ("browser storage is full. Use Save to keep a copy as a file"), reset on the next success | `core/objects-save.js:48-61` (15c) |
| `saveSoon()`, a 300 ms trailing debounce, called 246 times in 90 files | `bim/region-regenerate.js:74-86` |
| `pagehide` flushes a pending save synchronously (it fixed "a wall drawn just before a reload, gone 8 times in 8") | `ui/project-tabs.js:101-106` (15d) |
| Project switching: park, write the next into `acad3dV1`, remove its parked copy; rollback and "stored data is damaged" toast on failure | `ui/project-tabs.js:143-206` (15e) |
| Boot repairs crash leftovers in the list | `ui/project-tabs.js:58-84` |
| Templates as whole records `acad3dTemplateV1:<id>` | `assets/family-library.js:88`; `assets/templates.js:1-22` |
| Family library `acad3dFamilyLibrary`, rewritten whole on each change, **`console.warn` only on failure, no toast** | `assets/family-library.js:6, 44-46` (15f) |
| Small preferences: `acad3dTheme`, `acad3dUIPrefs`, `acad3dToolPal`, `acad3dLeftPanel`, `acad3dRightPanel`, `acad3dPropTab`, `acad3dGraphics`, `acad3dCmdUsage` | `core/storage-theme.js:30`; `ui/build-ui.js:10`; `ui/tool-palette.js:4,182`; `history/branches-merge.js:381`; `analysis/analyze-tab.js:8`; `render/webgpu.js:11`; `commands/command-catalogue.js:118` |
| Legacy keys removed at start; `file://` shared-origin comment | `core/storage-theme.js:5-25, 39-42` |
| The file envelope `{app:'acad3d-project', formatVersion:1, savedAt, data}`, without `cam`, `seq` or `docId`; a newer `formatVersion` only warns | `io/project-file.js:5-17` (15g) |
| Save to file: `<name>.acad3d.json` through `bimTriggerDownload` (Blob, `<a download>`, revoke after 1 s) | `io/project-file.js:21-31`; `annotation/annotation-pick.js:181-190` |
| Open: hidden `#a3d-projin accept=".json"`, FileReader, each file into a new tab; Import also routes `.json` | `ui/build-ui.js:52, 197-203`; `io/project-file.js:36-72`; `io/import-entry.js:28-31` |
| No drag-and-drop of files from the OS, no `showSaveFilePicker`, no IndexedDB, no service worker, no manifest, no `CompressionStream`, no worker | grep of `src/` (audit and files note) |
| Element history inside the record, its blobs as JSON strings escaped a second time | `history/element-history.js:1-6, 33-38, 48-59` |
| Imported meshes inline as `mesh:{v,f}`; SketchUp limits `BIM_SKP={maxTris:250000, blockTris:6000, blockChars:1500000}` | `io/import-obj-stl.js:82-95`; `io/sketchup-import.js:20` (15h; the "stays within browser storage" wording is in `canvas_v10_STATUS.md:14145-14146`) |
| Image notes as data URIs, 4 MB cap | `annotation/annotation-overlay.js:207-229` (15h) |
| Not saved, rebuilt: terrain TIN, map tiles, result-layer images | `terrain/terrain-tin.js:61-62`; `map/map-tiles.js:18-25`; `analysis/results-layers.js:7,175-178` |
| Promises already used with `.then(function(){...})` in 15 engine files; no `async`, no arrows | e.g. `site-analysis/climate-data.js:41-45` |
| Test hooks for files and projects: `__a3dExportProject`, `__a3dProjectEnvelope`, `__a3dImportProject`, `__a3dParseProjectEnvelope`, `__a3dDocs`, `__a3dTemplateSave/Use`, `__a3dFamilyAdd/Get/Remove` | `testing/hooks-drawing.js:277-300`; `testing/hooks-layers-sheets.js:165-180`; `testing/hooks-assets-structure.js:16-17` |
| The storage contract suite: V115 (48 checks), with V121b and V124; 23 of 157 test files mention localStorage; V115 replaces `Storage.prototype.setItem` to simulate a full store | `tests/bim_phase115_project_tabs_browser_tests.py:1-26, 358-375` |
| The build contract: one file, no dependency, "must run from `file://` with no server"; failures warned and toasted; "never a half-written localStorage record"; "existing localStorage keys (`acad3dV1` and relatives) must survive every change" | `CLAUDE_INSTRUCTIONS.md:49-56` |

What it means for the build: the boot must become two-stage (build with defaults or with a localStorage copy, then
apply the IndexedDB record), every reader of `A3D_BOOT_DOC`, `A3D_DOCS` and `A3D_FAMLIB` at start must tolerate it,
and an asynchronous write cannot be finished inside `pagehide`; the prior art answers that by also saving when the
page turns hidden (tldraw, Excalidraw). The file envelope is already the export, the backup and the way out of a
failed migration.

## 9. Risks and threats to validity

- **One engine measured.** Every number in part 6 is Chromium 153, headless, on one Linux virtual machine with a
  fast virtual disk. Firefox, Safari (macOS and iOS), Android and headed Chrome were not run; quota, `persist()`,
  timing and the value ceiling are the most likely to differ. Their behaviour rests on source code and vendors'
  documents.
- **Headless is not a user's browser.** `persist()` and quota in headless report fixed values (10 GiB and 3 GiB
  headroom), so they test the code paths, not what a user's Chrome will grant.
- **Vendors' documents age.** web.dev's persistent-storage page is from 2020; the Chrome install post from 2023
  says the prompt needs a fetch handler while the 2024 criteria page does not list one; MDN is secondary to each
  engine. The newest primary text was preferred wherever two disagreed.
- **Source read is not shipping configuration.** WebKit's trunk shows the `file://` refusal and the eviction flags;
  which settings Safari.app ships is not known.
- **Synthetic data.** No real BIM-Personal project file exists in the repository; compression ratios (0.108 to
  0.344) and timings use made-up models.
- **Small samples.** Three to five runs per measurement on a shared machine; outliers are kept in the raw numbers.
- **SIGKILL is not power loss.** The page cache survives a killed browser, so e08 cannot show what "relaxed" risks.
- **Scratch measurements not kept.** The app-code audit's sizes and the switch failure were measured with scripts
  in the session scratchpad, not in `reference/experiments/`; they can be repeated from the audit's description but
  not rerun as they stand.
- **A shared scratch folder.** The standards researcher found a helper script altered between two calls by another
  process; it rewrote it in a private folder and re-made every extract after that point, so no finding depends on
  the altered copy.
- **Search summaries.** Kept only as pointers (U, group H in part 12); none reaches the plan.
- **Prior art read in part.** Only the storage files of each project were read, so "no peer calls `persist()`" is
  medium confidence; Penpot, JSCAD, Onshape and SketchUp for Web were not read.
- **Risk to users in the build itself.** A migration that moves rather than copies, a second tab holding an old
  connection, or an old `v/` build opening an upgraded store could lose or block projects; parts 7 and 11 carry
  the guards (copy then delete, close on `versionchange`, `VersionError` handled).

## 10. What is still open (U), and why

To confirm before any of it reaches the code; none of it is used in the plan.

| Open | Why | How to close |
|---|---|---|
| Firefox's and Safari's IndexedDB behaviour from `file://` | Not installed here; only WebKit's code read | Run e05 in Firefox and Safari (the owner's machine) |
| What Safari.app enables (`needsStorageAccessFromFileURLsQuirk`, universal file access) | Not found in any document | A run in Safari |
| Firefox's and WebKit's single-value ceiling in IndexedDB | Not found in source | Run e02b in each engine |
| Firefox's and Safari's default durability | Only Chrome's statement ("all use relaxed") | Read Gecko and WebKit source |
| Whether headed Chrome grants `persist()` to an installed site today | web.dev page of 2020; the permission-context source moved | A headed run, installed and not |
| Whether Chrome's automatic install prompt still needs a fetch handler | Two Chrome pages disagree; the post is from 2023 | A current Chromium source or post |
| Whether a granted `persist()` exempts a Safari tab from the 7-day rule | The exempt-domain set suggests so; not stated | WebKit source tracing |
| iOS: whether Safari's storage is visible to the home-screen app | Documented for macOS only (cookies copied, nothing else) | A WebKit statement or a device test |
| iOS Safari and `.json` downloads (WebKit 263608 names TXT and XML), and the maximum Blob download | Bug records only | A device test |
| Firefox 115 as the first release with private-window IndexedDB; CVE-2024-4767 | Search summaries | Mozilla's release notes |
| The reason for Chromium's 127 MiB value ceiling and its "missing large-value file" `NotFoundError` | Search summary of a blink-dev PSA | Chromium source |
| Whether `Service-Worker-Allowed` can be sent from Pages | Inferred (Pages sets no custom headers); no GitHub page read | GitHub Docs |
| Firefox's taskbar web apps: their storage and the profile; macOS and Linux | support.mozilla.org refused | Mozilla's help page |
| Real project sizes, compression ratios and save times on phones | No real project file; no phone here | A sample project committed (no photos), runs on devices |
| A desktop wrapper's behaviour and cost (option F) | Not researched | Only if the owner asks for a native app |

## 11. The owner's decisions

Each with the evidence and a recommended answer. **Answers pending.**

**D1. Scope and phases.** The evidence separates three problems: the size wall (localStorage's 5,242,880 units,
already reached by a 125,000-triangle import), safety (eviction and the 7-day rule hit IndexedDB as much as
localStorage), and offline use (only a service worker on Pages gives it). *Recommended:* three phases, in this
order: **A, the IndexedDB project store** (projects, parked projects, templates and the family library move; the
small preferences stay in localStorage; copy, never move, the old keys, and delete them only after the IndexedDB
transaction completes; keep reading `acad3dV1` as a legacy source; a localStorage fallback where IndexedDB is
refused); **B, files** (D2, D4, the pickers in Chromium); **C, installable and offline** (D6). A goes first because
it is the wall users meet; B is the one that makes projects safe and can follow at once; C last because it depends
on Pages only. The build contract's "existing localStorage keys must survive every change" needs the owner's word
that they may be read once and retired after a confirmed copy.

**D2. Browser storage as a cache, the file as the real save.** No engine promises to keep best-effort data; Safari
deletes it after seven days of Safari use without interaction; Figma tells users 7 days in Safari; Excalidraw's
maintainers cannot recover wiped scenes. *Recommended:* yes, say so in the app's own words: the browser keeps a
working copy; "Save" writes the file. A project shows whether it has changes not yet saved to a file; a quiet
reminder appears after a set time of unsaved-to-file work (draw.io forces an autosave at 30 s; a file reminder
needs a longer interval, the owner's choice, for example 30 minutes or at closing a tab) and at the first save in
Safari or in a private window; the existing "storage is full" toast keeps pointing to Save.

**D3. Asking `persist()`, and when.** It is the only lever against best-effort eviction; Firefox shows a prompt,
Chrome and Safari answer silently, Safari grants it mainly to home-screen apps; web.dev advises asking after a
gesture; no peer app read calls it. *Recommended:* ask once, on the user's first explicit Save (a gesture), never on
load; treat `false` as normal; do not ask again unless the user asks from a storage panel that shows `estimate()`'s
usage and whether storage is persistent.

**D4. The file format.** The envelope `.acad3d.json` (`formatVersion:1`) already round-trips but leaves out `cam`,
`seq` and `docId`, and the autosave record has no version at all. gzip shrank synthetic models to 0.108 to 0.344 of
their size in all engines since Safari 16.4, but stalled the main thread 86 to 131 ms for 4 MB in this build.
*Recommended:* keep `.acad3d.json` as the plain default, readable everywhere; add `formatVersion` to the stored
record and a version 2 envelope carrying the view; add an optional compressed form, `.acad3d.json.gz`, which the
loader recognises by its first bytes 1F 8B (not by the name), offered for large projects; compress in a worker or
accept the stall, the owner's choice, and fall back to plain JSON where `CompressionStream` is missing.

**D5. The `file://` one-file build.** Chromium shares one store among every local page (measured), Firefox gives each
file its own (moving the file loses its projects), Safari refuses storage (from WebKit's code); no service worker
and no OPFS there; the save picker was reached from `file://` in Chromium. *Recommended:* keep the build and the
contract's "runs from `file://`"; there, treat browser storage as a cache only, use a database name that will not
collide with other local pages, wrap every storage call in try/catch, and when storage is refused (Safari) say once
that the project lives only in its file; "Save" writes the file (picker where it exists, download otherwise). Point
users who want projects kept in the browser to the Pages app.

**D6. A service worker for offline use on Pages.** Installing needs no worker in Chrome's menu, Safari or Firefox
143, but offline does; the worker must sit at `/BIM-Personal/sw.js` to cover the app (path rule, measured); its
scope also covers the old builds under `v/`. *Recommended:* yes, in phase C: a manifest (`scope` and `start_url`
`/BIM-Personal/`, `display: standalone`, 192 and 512 px icons), and an ES5 worker that serves the hashed `app/`
files cache-first, `index.html` network-first, leaves `v/` alone, and carries the build's hash so every build is
byte-different; no `skipWaiting()` while a page is open with unsaved work. `file_handlers` (Chrome desktop only)
waits.

**D7. Several tabs.** A tab that does not close on `versionchange` blocks another's upgrade (measured); every library
read closes; tldraw and Excalidraw resolve two tabs on one project by "last write wins, then refresh"; draw.io's
alive check finds drafts of tabs that died. *Recommended:* every connection closes on `versionchange` and tells the
user to reload; the upgrading tab says "close the other tabs of the app" on `blocked`; after each committed save a
small localStorage stamp (or `BroadcastChannel`) tells other tabs; a project open in one tab opens read-only in a
second, with a button to take it over (rather than silent last-write-wins). An old copy that meets `VersionError`
says a newer version has updated the store.

**D8. The family library's warn-without-toast fault.** `bimSaveFamilyLibrary` only warns to the console
(`assets/family-library.js:44-46`), against the build contract (`CLAUDE_INSTRUCTIONS.md:54`); a SketchUp import into a
full library loses its blocks on reload without a word. *Recommended:* fix it now, as a small separate patch with its
own falsified check (a toast like the template's), before phase A, since phase A moves the library anyway and the
fault is live today.

**D9. Saving when the page is closed.** `pagehide` cannot wait for an IndexedDB write; prior art also saves on
`visibilitychange` to hidden (tldraw) and on blur (Excalidraw), and draw.io forces a save after 30 s of continuous
change. *Recommended:* keep the 300 ms debounce, add a forced save after a maximum delay and on hidden, and keep a
small localStorage journal of the last unsaved change only if a suite shows edits lost on reload without it.

**D10. The shared `github.io` origin.** Every Pages project of the account and every old build under `v/` share one
store. *Recommended:* one database named for the app (for example `BIM-Personal`), a stored schema version checked on
open, and old builds under `v/` opened read-only for projects, or told to use their own file saves.

## 12. References

Every source cited across the five notes and the check, all read on 2026-10-31 unless a date says otherwise; the
date in "What" is the source's own. Where a source is P in one note and S in another, the stronger reading is given.

**A. Specifications**

| # | What | URL | What was read | Level |
|---|---|---|---|---|
| A1 | Indexed Database API 3.0, W3C Working Draft 30 Oct 2026, and editor's draft | https://www.w3.org/TR/IndexedDB-3/ ; https://w3c.github.io/IndexedDB/ | Status; revision history; § 2.7 transactions and durability; § 4.4; § 4.5 put/add; § 5.1 opening a connection | P |
| A2 | Storage Living Standard (WHATWG), updated 19 Oct 2026 | https://storage.spec.whatwg.org/ | § 3 storage keys, § 4-5 buckets and persistence, § 6 quota, § 7 pressure, § 8 API | P |
| A3 | File System Access, WICG Draft Community Group Report 10 Oct 2025 | https://wicg.github.io/file-system-access/ | Status; § 2.3 permissions; § 3.1-3.2 picker checks; § 5.2-5.3 privacy and frames | P |
| A4 | File System Living Standard (WHATWG), updated 19 Oct 2026 | https://fs.spec.whatwg.org/ | Header; § 2.3.3; § 3 quota; `createSyncAccessHandle` exposure | P |
| A5 | Web Application Manifest, W3C Working Draft 26 Oct 2026, and editor's draft | https://www.w3.org/TR/appmanifest/ ; https://w3c.github.io/manifest/ | Status; "Installable web applications" | P |
| A6 | Service Workers, Editor's Draft 29 Oct 2026 | https://w3c.github.io/ServiceWorker/ | Register algorithm; § 6.5 path restriction | P |
| A7 | Manifest incubations (WICG) | https://wicg.github.io/manifest-incubations/ | `file_handlers`, `launch_handler` | P |

**B. Browser source code, read as text (main branches)**

| # | What | URL | What was read | Level |
|---|---|---|---|---|
| B1 | Chromium quota README | https://chromium.googlesource.com/chromium/src/+/main/storage/browser/quota/README.md | QuotaDatabase, LRU eviction | P |
| B2 | Chromium `quota_settings.cc` | https://chromium.googlesource.com/chromium/src/+/main/storage/browser/quota/quota_settings.cc | Per-origin ratio, incognito pool | P |
| B3 | Chromium `quota_features.cc` | https://chromium.googlesource.com/chromium/src/+/main/storage/browser/quota/quota_features.cc | `kPoolSizeRatio` 0.8; remain-available ratios | P |
| B4 | Chromium `dom_storage_constants.h` | https://chromium.googlesource.com/chromium/src/+/main/components/services/storage/dom_storage/dom_storage_constants.h | 10 MiB per area; 400-day cutoff; 8 commit errors | P |
| B5 | Chromium `cached_storage_area.cc` | https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/renderer/modules/storage/cached_storage_area.cc | (key + value) x 2 check, lines 80-83 | P |
| B6 | Chromium `indexeddb.mojom` | https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/public/mojom/indexeddb/indexeddb.mojom | `kIDBWrapThreshold = 65536` | P |
| B7 | Chromium `idb_value_wrapping.cc` | https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/renderer/modules/indexeddb/idb_value_wrapping.cc | Wrapping and compression threshold | P |
| B8 | Chromium `url/origin.h` | https://chromium.googlesource.com/chromium/src/+/main/url/origin.h | File URLs parse as ("file", "", 0) | P |
| B9 | Chromium `important_sites_util.cc` | https://chromium.googlesource.com/chromium/src/+/main/chrome/browser/engagement/important_sites_util.cc | Reasons list | S for `persist()` (link not traced) |
| B10 | Chromium blob README | https://chromium.googlesource.com/chromium/src/+/main/storage/browser/blob/README.md | "Blob Storage Limits" | P |
| B11 | Gecko `StaticPrefList.yaml` | https://raw.githubusercontent.com/mozilla-firefox/firefox/main/modules/libpref/init/StaticPrefList.yaml | `dom.storage.default_quota`, `default_site_quota`, `dom.indexedDB.privateBrowsing.enabled`, `security.fileuri.strict_origin_policy` | P |
| B12 | Gecko `dom/quota/ActorsParent.cpp` | https://raw.githubusercontent.com/mozilla-firefox/firefox/main/dom/quota/ActorsParent.cpp | `GetTemporaryStorageLimit`, `GetGroupLimitForLimit`, persisted check | P |
| B13 | Gecko `dom/localstorage/ActorsParent.cpp` | https://raw.githubusercontent.com/mozilla-firefox/firefox/main/dom/localstorage/ActorsParent.cpp | Usage accounting in UTF-16 units | P |
| B14 | WebKit `WebsiteDataStoreCocoa.mm` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/UIProcess/WebsiteData/Cocoa/WebsiteDataStoreCocoa.mm | Quota ratios 0.8/0.6, 0.2/0.15 | P |
| B15 | WebKit `WebsiteDataStore.cpp` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/UIProcess/WebsiteData/WebsiteDataStore.cpp | `timeBasedEvictionMode()` | P |
| B16 | WebKit `WebsiteDataStoreConfiguration.cpp` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/UIProcess/WebsiteData/WebsiteDataStoreConfiguration.cpp | Eviction build flag | P |
| B17 | WebKit `NetworkStorageManager.cpp` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/NetworkProcess/storage/NetworkStorageManager.cpp | `persist` grant, lines 915-949 | P |
| B18 | WebKit `ResourceLoadStatisticsStore.cpp` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/NetworkProcess/Classifier/ResourceLoadStatisticsStore.cpp | Exempt-domain set, lines 812-821 | P |
| B19 | WebKit `LocalStorageManager.cpp` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/NetworkProcess/storage/LocalStorageManager.cpp | `localStorageQuotaInBytes = 5 * MB` | P |
| B20 | WebKit `SQLiteStorageArea.cpp` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/NetworkProcess/storage/SQLiteStorageArea.cpp | `sizeInBytes()` accounting | P |
| B21 | WebKit `ScriptExecutionContext.cpp` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/dom/ScriptExecutionContext.cpp | `canAccessResource`, lines 950-978 | P |
| B22 | WebKit `IDBFactory.cpp` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/Modules/indexeddb/IDBFactory.cpp | SecurityError, line 101 | P |
| B23 | WebKit `LocalDOMWindow.cpp` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/page/LocalDOMWindow.cpp | localStorage SecurityError | P |
| B24 | WebKit `Document.cpp` | https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/dom/Document.cpp | Storage access from file URLs | P |

**C. Vendors' own documents**

| # | What | URL | What was read | Level |
|---|---|---|---|---|
| C1 | WebKit, "Full Third-Party Cookie Blocking and More", 2020-03-24 | https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/ | The 7-day cap; home-screen apps | P |
| C2 | WebKit, "The File System API with Origin Private File System", 2022-02-14 | https://webkit.org/blog/12257/the-file-system-access-api-with-origin-private-file-system/ | OPFS support, private browsing, lifetime | P |
| C3 | WebKit, "Updates to Storage Policy", 2023-08-10 | https://webkit.org/blog/14403/updates-to-storage-policy/ | Quotas, eviction, `persist()` | P |
| C4 | WebKit, "WebKit Features in Safari 17.0", 2023-09-18 | https://webkit.org/blog/14445/webkit-features-in-safari-17-0/ | Web apps on Mac | P |
| C5 | WebKit, "WebKit Features in Safari 26.0" | https://webkit.org/blog/17333/webkit-features-in-safari-26-0/ | Home Screen web apps; WritableStream | P |
| C6 | Chrome for Developers, IndexedDB durability defaults to relaxed | https://developer.chrome.com/blog/indexeddb-durability-mode-now-defaults-to-relaxed | Whole post | P |
| C7 | Chrome for Developers, File System Access API, updated 2024-08-19 | https://developer.chrome.com/docs/capabilities/web-apis/file-system-access | Support; permission persistence | P |
| C8 | Chrome for Developers, Persistent permissions for the FSA API, 2024-01-09 | https://developer.chrome.com/blog/persistent-permissions-for-the-file-system-access-api | Three-way prompt; installed apps | P |
| C9 | Chrome for Developers, Update to install criteria, 2023-12-05 | https://developer.chrome.com/blog/update-install-criteria | Fetch-handler requirement | P |
| C10 | Chrome for Developers, File handling, 2020-10-22 | https://developer.chrome.com/docs/capabilities/web-apis/file-handling | `file_handlers`, `launchQueue`, prompt | P |
| C11 | Chrome for Developers, Launch Handler API, 2021-12-14 | https://developer.chrome.com/docs/web-platform/launch-handler | `client_mode` values | P |
| C12 | web.dev, Storage for the web, updated 2024-09-23 | https://web.dev/articles/storage-for-the-web | Quotas (parts out of date), localStorage advice | S |
| C13 | web.dev, Persistent storage, 2020-05-12 | https://web.dev/articles/persistent-storage | Chrome's heuristics; Firefox prompt | S (old) |
| C14 | web.dev, What does it take to be installable?, 2024-09-19 | https://web.dev/articles/install-criteria | Criteria list | P |
| C15 | web.dev, The origin private file system, 2023-06-08 | https://web.dev/articles/origin-private-file-system | Quota, clearing, sync access | P |
| C16 | web.dev, The service worker lifecycle | https://web.dev/articles/service-worker-lifecycle | Update rules | P |
| C17 | Firefox 143.0 release notes, 2025-09-16 | https://www.firefox.com/en-US/firefox/143.0/releasenotes/ | Taskbar web apps | P |
| C18 | GitHub Docs, Securing your GitHub Pages site with HTTPS | https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https | Automatic HTTPS | P |

**D. Curated reference data**

| # | What | URL | What was read | Level |
|---|---|---|---|---|
| D1 | MDN, Storage quotas and eviction criteria (last modified 2026-01-05) | https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria (source: raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/storage_api/storage_quotas_and_eviction_criteria/index.md) | Whole page | S |
| D2 | MDN, `<a>` download | https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a | `download` attribute | S |
| D3 | MDN, `URL.createObjectURL` | https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL_static | Availability, revoking | S |
| D4 | MDN, Origin private file system | https://developer.mozilla.org/en-US/docs/Web/API/File_System_API/Origin_private_file_system | Speed claims (no numbers) | S |
| D5 | MDN browser-compat-data, main branch: `api/` StorageManager, IDBTransaction, IDBFactory, IDBObjectStore, Window, FileSystemHandle, FileSystemFileHandle, FileSystemWritableFileStream, FileSystemSyncAccessHandle, CompressionStream, LaunchQueue; `manifests/webapp/` display, icons, file_handlers, launch_handler | https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/StorageManager.json (and the sibling files) | Version rows, re-read by the checker | P (curated data; the checker's level) |
| D6 | Mozilla standards-positions data | https://raw.githubusercontent.com/mozilla/standards-positions/gh-pages/merged-data.json | #154, #158, #207, #562, #738 | P |
| D7 | WebKit standards-positions data | https://raw.githubusercontent.com/WebKit/standards-positions/main/summary.json | #28, #49, #90, #238, #534 | P |

**E. Bug records**

| # | What | URL | What was read | Level |
|---|---|---|---|---|
| E1 | WebKit 273827, IndexedDB "Connection ... lost" (iOS 17.4); closed 2024-07-25 CONFIGURATION CHANGED, fixed in iOS 17.6 per Apple; reported again 2025-10-10 | https://bugs.webkit.org/show_bug.cgi?id=273827 | Status, 23 comments, history | P (corrected) |
| E2 | WebKit 277615, same error (Safari 18), DUPLICATE 2026-03-27 | https://bugs.webkit.org/show_bug.cgi?id=277615 | Status | P |
| E3 | WebKit 197050, internal IndexedDB server error, CONFIGURATION CHANGED 2025-03-04 | https://bugs.webkit.org/show_bug.cgi?id=197050 | Status | P |
| E4 | WebKit 292142, Blobs in IndexedDB kill the networking process (iOS 18.4), FIXED 2025-07-08 | https://bugs.webkit.org/show_bug.cgi?id=292142 | Status ("lost data" detail U) | P |
| E5 | WebKit 212279, revoking an object URL after navigation, FIXED 2020 | https://bugs.webkit.org/show_bug.cgi?id=212279 | Status, cause of 211234 | P |
| E6 | WebKit 263608, TXT and XML open in a tab on iOS, NEW | https://bugs.webkit.org/show_bug.cgi?id=263608 | Status, comments | P |
| E7 | WebKit 232302, home-screen app storage deleted after 7 days, WONTFIX | https://bugs.webkit.org/show_bug.cgi?id=232302 | Apple's answer | P |
| E8 | WebKit 181850, cross-origin storage in home-screen apps lost, NEW | https://bugs.webkit.org/show_bug.cgi?id=181850 | Status | P |
| E9 | WebKit 231706, Implement File System standard, REOPENED | https://bugs.webkit.org/show_bug.cgi?id=231706 | Last comments | P |
| E10 | WebKit 266559, Web Inspector wiped storage, FIXED 2024-01-11 | https://bugs.webkit.org/show_bug.cgi?id=266559 | Thread | P |
| E11 | Bugzilla 1730419, localStorage not shared between local files (Firefox 92), INVALID 2021-11-26 | https://bugzilla.mozilla.org/show_bug.cgi?id=1730419 | Comments | P |
| E12 | Bugzilla 1500453, file URIs as unique origins, fixed Firefox 68 | https://bugzilla.mozilla.org/show_bug.cgi?id=1500453 | Status, pref name | P |
| E13 | Bugzilla 1599979, [meta] Enable LSNG on Release, fixed Firefox 92 | https://bugzilla.mozilla.org/show_bug.cgi?id=1599979 | Status | P |
| E14 | Bugzilla 1639542, IndexedDB in private browsing, FIXED 2024-03-04 | https://bugzilla.mozilla.org/show_bug.cgi?id=1639542 | Status | P |
| E15 | Bugzilla 1558299 | https://bugzilla.mozilla.org/show_bug.cgi?id=1558299 | Read with 1730419 and 1639542; no finding rests on it | P |
| E16 | WICG file-system-access issue #289, re-prompting each session | https://github.com/WICG/file-system-access/issues/289 | Thread, through the fetch tool's digest | S |
| E17 | Excalidraw issue #7870, scene lost after a browser reset | https://github.com/excalidraw/excalidraw/issues/7870 | Maintainer's replies | P |

**F. Open implementations, read as text at pinned commits**

| # | What | URL | What was read | Level |
|---|---|---|---|---|
| F1 | idb-keyval 6.3.0 @17a69a1 (Apache-2.0) | https://github.com/jakearchibald/idb-keyval/blob/17a69a1165bef486d88950cb47d3913744f038ac/src/index.ts | Lines 1-140; `package.json` | P |
| F2 | idb @654c746 (ISC) | https://github.com/jakearchibald/idb/blob/654c746bef13f9fe7f5871e03ac58015cebace5a/src/entry.ts | `entry.ts` 30-110; README "Transaction lifetime" | P |
| F3 | safari-14-idb-fix @2a9084f | https://github.com/jakearchibald/safari-14-idb-fix/blob/2a9084feb17a1226a5aed0fd3f3d3a49c5b3e9eb/src/index.ts | Method and README (method only) | P |
| F4 | localForage @fb78c77 (Apache-2.0) | https://github.com/localForage/localForage/blob/fb78c77ee583fb727a558c439b5174aca38c5924/src/drivers/indexeddb.js | `indexeddb.js`, `localforage.js`, `isIndexedDBValid.js` | P |
| F5 | Dexie.js 4.4.7 @45aade7 (Apache-2.0) | https://github.com/dexie/Dexie.js/blob/45aade72aa19a601e6a13aa877beb7389e15b5d2/src/classes/dexie/dexie-open.ts | `dexie-open.ts`, `dexie.ts`, `quirks.ts` | P |
| F6 | Excalidraw @a758e93 (MIT) | https://github.com/excalidraw/excalidraw/blob/a758e93d6a03e9f995973703cb886850a398a6d3/excalidraw-app/data/LocalData.ts | `LocalData.ts`, `app_constants.ts`, `App.tsx`, `tabSync.ts`, `localStorage.ts`, `filesystem.ts`, `en.json` | P |
| F7 | tldraw @9e700c6 (tldraw licence, source-available; method only) | https://github.com/tldraw/tldraw/blob/9e700c63f66c040f172dbd7fef936a888ac4b8cc/packages/editor/src/lib/utils/sync/TLLocalSyncClient.ts | `TLLocalSyncClient.ts`, `LocalIndexedDb.ts`, `alerts.ts` | P |
| F8 | draw.io @3e707fd (Apache-2.0) | https://github.com/jgraph/drawio/blob/3e707fd20b6930778d6f6bf6e4d0079b4bce366b/src/main/webapp/js/diagramly/EditorUi.js | `EditorUi.js` 40061-40368, `StorageFile.js` 520-622, `DrawioFile.js`, `App.js` | P |
| F9 | Graphite @b39ec01 (Apache-2.0 / MIT) | https://github.com/GraphiteEditor/Graphite/blob/b39ec01d7d0b34d76122aaec5a48f82fd701583e/frontend/src/utility-functions/persistence.ts | Two `persistence.ts` files | P |
| F10 | That Open engine_components 3.4.0 @ad540db (MIT) | https://github.com/ThatOpen/engine_components/blob/ad540db9c60362865362cbcdea2a1dfc623bc299/CHANGELOG.md | Tree grep; CHANGELOG | P (absence) |

**G. Product documents**

| # | What | URL | What was read | Level |
|---|---|---|---|---|
| G1 | Figma Learn, What can I do offline in Figma? | https://help.figma.com/hc/en-us/articles/360040328553 | Whole article | P |
| G2 | draw.io, Diagrams offline | https://www.drawio.com/docs/security/diagrams-offline/ | Whole page | P |

**H. Search pointers, not sources (U, kept out of the plan)**

| # | What | URL |
|---|---|---|
| H1 | blink-dev PSA, missing large-value files now `NotFoundError` | https://groups.google.com/a/chromium.org/g/blink-dev/c/JmDqNNWGm20 |
| H2 | Mozilla intent to ship IndexedDB in private browsing (Firefox 115) | https://groups.google.com/a/mozilla.org/g/dev-platform/c/yy7uUP47KGQ |
| H3 | CVE-2024-4767 | https://cve.circl.lu/vuln/cve-2024-4767 |
| H4 | TYPO3 #81156, Safari private-mode localStorage | https://forge.typo3.org/issues/81156 |
| H5 | Bugzilla 1915736, Taskbar Tabs | https://bugzilla.mozilla.org/show_bug.cgi?id=1915736 |
| H6 | Excalidraw #8968, #9480, #9195, #8738, #12202, #10861, discussion #6463 | https://github.com/excalidraw/excalidraw/issues/8968 (and siblings) |
| H7 | WebKit bugs 200078, 235579 (not opened) | https://bugs.webkit.org/show_bug.cgi?id=200078 ; https://bugs.webkit.org/show_bug.cgi?id=235579 |
| H8 | That Open IfcStreamer documentation | https://docs.thatopen.com/api/@thatopen/components-front/classes/IfcStreamer |
| H9 | Photopea, a review and a forum post | https://shotkit.com/photopea-review/ ; https://gimpchat.com/viewtopic.php?p=284599 |
| H10 | draw.io guidance quoted on a forum | https://forum.allaboutcircuits.com/threads/saving-google-drawio-files.164422/ |
| H11 | A 2018 blog on Safari's local-file SecurityError and "Disable Local File Restrictions" | (named in the standards note, URL not recorded) |
| H12 | Stack Overflow thread on iOS home-screen storage separation | (search pointer, not opened) |

**I. The app and the experiments**

| # | What | Where | What was read | Level |
|---|---|---|---|---|
| I1 | BIM-Personal `src/` at commit 179cc2f; `canvas_v10.html`; `CLAUDE_INSTRUCTIONS.md`; `tests/`; `tools/build_site.py` | this repository | Part 8 | P |
| I2 | Experiment scripts e01 to e12 and `_lib.js` | [reference/experiments/local-storage/](experiments/local-storage/) | Run 2026-10-31, Chromium 153 | P (measured, one engine) |
