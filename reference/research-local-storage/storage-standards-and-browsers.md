# Browser storage, the standards and the browsers: IndexedDB and localStorage (research note, 2026-10-31)

Scope: the standards and each major browser's actual behaviour for IndexedDB and localStorage (limits,
quotas, eviction, persistence, durability, support, private mode, file:// pages, known bugs), for a
zero-dependency ES5 CAD/BIM app that today saves projects only in localStorage and also runs as one
HTML file opened from disk. Researcher: one research agent, 2026-10-31. Every source below was read on
2026-10-31 unless a date says otherwise.

Evidence levels (reference/research-protocol.md): **P** = read in the primary source itself (the
specification text, the browser's own source code read as text, the vendor's own post, the bug record
itself); **S** = dependable secondary, gap stated; **U** = search-engine summary only, never for code.
Confidence: high / medium / low, with the reason.

## Method: research question, hypotheses, search log

### Research question
What storage can the app rely on, in each browser it supports (Chrome/Edge, Firefox, Safari on macOS
and iOS), to keep a large CAD/BIM project safely: how much, for how long, under which conditions it is
deleted, how durable a write is, and what changes when the app runs from `file://` or in a private window?

### Hypotheses (each one falsifiable) and how they came out
| # | Hypothesis | Result |
|---|---|---|
| H1 | localStorage is limited to about 5 MiB per origin in every browser | **Held, with a correction**: Chrome counts 2 bytes per UTF-16 unit against 10 MiB (= 5,242,880 units); Firefox counts UTF-16 units against 5 MiB; WebKit counts bytes (1 per Latin-1 char, 2 per char of a 16-bit string) against 5 MiB. P. |
| H2 | IndexedDB holds a 50 MB+ project in every browser in normal mode | **Held** for quota (Chrome 60% of disk, Firefox min(10% disk, 10 GiB), Safari 17+ 60% of disk); **not guaranteed** by durability/eviction (see H4, H5) and by Safari bugs. P for quotas. |
| H3 | IndexedDB is usable from ES5 code (callbacks, no promises) | **Held**: the IDB API is event/callback based; only the Storage API (`navigator.storage.*`) is promise-only. P. |
| H4 | `navigator.storage.persist()` protects data from automatic eviction in every browser | **Held for pressure/LRU eviction** (spec + WebKit + MDN); grants differ: Firefox prompts, Chrome uses site heuristics, WebKit grants only to exempt domains (home-screen web app, app-bound, managed). P/S. |
| H5 | Safari's 7-day cap deletes IndexedDB of a first-party site the user stops visiting | **Held for Safari (browser)** when tracking prevention is on; **does not apply** to home-screen web apps (own day counter) or to non-browser WKWebView apps. P. |
| H6 | IndexedDB and localStorage work from a `file://` page in all three engines | **Failed**: WebKit trunk denies both for local (file) origins unless a quirk/universal-access setting is on; Firefox (since 92) gives each file URL its own origin; Chromium treats all `file://` URLs as one origin. P (code), S (behaviour reports). |
| H7 | Every browser now supports IndexedDB in private windows | **Held** for Firefox since 115 (pref default true, P), Chrome (incognito quota from RAM, P); Safari: localStorage works in private since Safari 11 (S); Safari private IDB quota not found (gap). |
| H8 | Chrome's IndexedDB durability default is "relaxed" | **Held**: since Chrome 121 (vendor post, P). |

### Search and fetch log
All fetches by `curl` through the session proxy into a scratch folder; no downloaded code was run. No
host was refused: w3.org, w3c.github.io, whatwg.org, webkit.org, web.dev, developer.chrome.com,
raw.githubusercontent.com, chromium.googlesource.com, bugzilla.mozilla.org (REST), bugs.webkit.org
(REST) all answered 200. `firefox-source-docs.mozilla.org/dom/quota/index.html` answered **404**
(page moved); replaced by the Gecko source on GitHub (`mozilla-firefox/firefox`). The GitHub code-search
API is refused in this session ("sessions are bound to their configured repositories"); replaced by
direct raw/googlesource paths. Two Chromium paths for the durable-storage permission context returned
404 (moved); the "important sites" code was read instead.

| # | Where | Query or URL | What came back | Kept / set aside, why |
|---|---|---|---|---|
| 1 | w3.org TR | https://www.w3.org/TR/IndexedDB-3/ | IDB 3.0 WD 30 Oct 2026 (1.47 MB) | Kept, P: status, durability, versionchange, changes list |
| 2 | w3c.github.io | https://w3c.github.io/IndexedDB/ | Editor's draft, same date | Kept as cross-check |
| 3 | GitHub raw | w3c/IndexedDB index.bs, whatwg/storage storage.bs | Spec sources | Downloaded; HTML used for reading |
| 4 | whatwg.org | https://storage.spec.whatwg.org/ | Living Standard, last updated 19 Oct 2026 | Kept, P: buckets, persist, estimate, pressure, opaque origins |
| 5 | GitHub raw (MDN content) | storage_quotas_and_eviction_criteria/index.md | Current MDN page | Kept, S (MDN summarises vendors; checked against code) |
| 6 | GitHub raw (MDN content) | web_storage_api/index.md, domexception/index.md | | Context only |
| 7 | webkit.org | /blog/14403/updates-to-storage-policy/ (Aug 10 2023, Sihui Liu) | Full post | Kept, P |
| 8 | webkit.org | /blog/10218/full-third-party-cookie-blocking-and-more/ (Mar 24 2020, John Wilander) | Full post | Kept, P: 7-day cap |
| 9 | web.dev | /articles/storage-for-the-web (last updated 2024-09-23) | | Kept as S; its Safari "1 GB + prompt" and Firefox "2 GB group" are **out of date** (contradicted by P below) |
| 10 | web.dev | /articles/persistent-storage (last updated 2020-05-12) | Chrome heuristics, Firefox prompt | Kept, S (old); Chrome heuristic re-checked in source |
| 11 | developer.chrome.com | /blog/indexeddb-durability-mode-now-defaults-to-relaxed | | Kept, P |
| 12 | chromium.googlesource.com | storage/browser/quota/README.md, quota_settings.cc, quota_features.cc | Quota constants | Kept, P |
| 13 | chromium.googlesource.com | components/services/storage/dom_storage/dom_storage_constants.h | localStorage quota, 400-day stale cutoff, commit-error wipe | Kept, P |
| 14 | chromium.googlesource.com | blink/.../storage/cached_storage_area.cc | `(key.length()+value.length())*2 > kPerStorageAreaQuota` | Kept, P |
| 15 | chromium.googlesource.com | blink/.../indexeddb/idb_value_wrapping.cc, indexeddb.mojom | `kIDBWrapThreshold = 65536` | Kept, P |
| 16 | chromium.googlesource.com | url/origin.h, blink security_origin.cc | file URLs parse as ("file","",0) | Kept, P (comment in code) |
| 17 | chromium.googlesource.com | chrome/browser/engagement/important_sites_util.cc | Reasons: engagement, persistent, bookmarks, home screen, notifications | Kept, S for persist() (link from persist() to this file not read) |
| 18 | GitHub raw (Gecko) | modules/libpref/init/StaticPrefList.yaml | `dom.storage.default_quota` 5*1024, `default_site_quota` 25*1024, `dom.indexedDB.privateBrowsing.enabled` true | Kept, P |
| 19 | GitHub raw (Gecko) | dom/quota/ActorsParent.cpp | 50% disk, 8 TiB cap, group = min(limit/5, 10 GB) | Kept, P |
| 20 | GitHub raw (Gecko) | dom/localstorage/ActorsParent.cpp | usage = utf16Length(key)+utf16Length(value) | Kept, P |
| 21 | GitHub raw (WebKit) | WebsiteDataStoreCocoa.mm, WebsiteDataStore.cpp, WebsiteDataStoreConfiguration.cpp | 0.6/0.8 browser, 0.15/0.2 app; time-based eviction disabled for non-browser apps | Kept, P |
| 22 | GitHub raw (WebKit) | NetworkStorageManager.cpp, ResourceLoadStatisticsStore.cpp, NetworkProcess.cpp | persist() grant rule | Kept, P |
| 23 | GitHub raw (WebKit) | LocalStorageManager.cpp, SQLiteStorageArea.cpp | `localStorageQuotaInBytes = 5 * MB`, `sizeInBytes()` accounting | Kept, P |
| 24 | GitHub raw (WebKit) | ScriptExecutionContext.cpp, IDBFactory.cpp, LocalDOMWindow.cpp, Document.cpp, SecurityOrigin.cpp | file-origin storage denial | Kept, P |
| 25 | GitHub raw (MDN BCD) | api/StorageManager.json, IDBTransaction.json, IDBFactory.json, IDBObjectStore.json, Window.json | First versions | Kept, S (BCD is curated data, not the browsers) |
| 26 | Web search | "localStorage file:// origin Firefox Chrome Safari shared all files" | Bugzilla 1730419, 507361, 643318; blog, kiwix copies of SO | Bugzilla 1730419 read in full via REST (P for Firefox's intent); SO copies set aside (U) |
| 27 | Web search | "Firefox 115 IndexedDB private browsing enabled" | Mozilla intent-to-ship, Bugzilla 1639542, CVE-2024-4767 | Bug 1639542 read via REST; pref read in source; CVE noted as U (summary only) |
| 28 | Web search | "Chrome IndexedDB maximum value size bug crbug large blob" | blink-dev PSA (NotFoundError), SO "max=133169152" | PSA and SO not opened: U; wrap threshold read in source instead |
| 29 | Web search | "bugs.webkit.org IndexedDB data lost iOS Safari ... connection lost" | WebKit bugs 273827, 277615, 197050, 292142 | All four read via REST (status, dates, comments of 273827): P |
| 30 | Web search | "Safari private browsing IndexedDB quota localStorage QuotaExceededError Safari 11 private mode fixed" | TYPO3, Drupal, cendio bug reports | Not opened: U, used only as a pointer; Safari private IDB quota left as a gap |
| 31 | Bugzilla REST | bugs 1730419 (comments), 1639542, 1558299 | | Kept, P |

A note on the scratch area: a helper script written to the shared scratch folder was found altered
between two calls (another process shares that folder). It was rewritten in a private sub-folder and
all extracts after that point were re-made from the downloaded files with it. No finding depends on the
altered copy.

## IndexedDB: the specification, ES5 use, values, durability, versions across tabs

### Takeaway
The current edition is Indexed Database API 3.0, a W3C Working Draft dated 30 October 2026 (2.0 remains
the last Recommendation). The whole data API is callback/event based and usable from ES5; ArrayBuffer,
typed arrays and Blob are stored by StructuredSerializeForStorage. The durability hint ("strict" /
"relaxed" / "default") exists since Chrome 83, Safari 15, Firefox 126, and Chrome's default became
relaxed in Chrome 121, so a `complete` event does not mean the data reached the disk unless `strict` is asked.

### Cited Findings
- IDB 3.0 status: "W3C Working Draft, 30 October 2026", this version `WD-IndexedDB-3-20261030`, previous `WD-IndexedDB-3-20250813` and `20261029`, editor Steve Becker (Microsoft). P, high (read in the TR header). — [Indexed Database API 3.0, TR](https://www.w3.org/TR/IndexedDB-3/)
- 3.0's changes since 2.0 (informative summary, read in full) include: `databases()`, `commit()`, the `durability` option and attribute (issue #50), `getAllRecords(options)` and a `direction` option for `getAll()`/`getAllKeys()`, and "Use of QuotaExceededError has been updated to reflect that it is now a DOMException-derived interface instead of an exception name" (issue #463). P, high. — [IDB 3.0 § Revision history](https://www.w3.org/TR/IndexedDB-3/)
- Durability hint, normative text: "strict": the UA "may consider that the transaction has successfully committed only after verifying that all outstanding changes have been successfully written to a persistent storage medium"; "relaxed": "as soon as all outstanding changes have been written to the operating system, without subsequent verification"; "default": "the user agent should use its default durability behavior for the storage bucket". IDL: `enum IDBTransactionDurability { "default", "strict", "relaxed" }; dictionary IDBTransactionOptions { IDBTransactionDurability durability = "default"; }`. The note says strict "typically" flushes OS buffers before `complete`, and apps are "encouraged to use relaxed for ephemeral data ... and strict in cases where reducing the risk of data loss outweighs the impact to performance and power". Note "may": even strict is a hint. P, high. — [IDB 3.0 § 2.7 Transactions, § 4.4](https://www.w3.org/TR/IndexedDB-3/)
- Chrome changed its default durability from strict to relaxed in Chrome 121, "to align with other major browsers like Firefox and Safari", which "all use relaxed"; relaxed fires `complete` "after changes make it to the OS buffer, which is typically flushed every couple seconds"; old behaviour back with `db.transaction(store, 'readwrite', { durability: 'strict' })`; the blog adds that "strict does not ensure that changes are actually written immediately to disk" and names data migration as the case that needs strict. P (vendor's own post), high. — [Chrome for Developers: A change to the default durability mode in IndexedDB](https://developer.chrome.com/blog/indexeddb-durability-mode-now-defaults-to-relaxed)
- Values: put/add serialize with `StructuredSerializeForStorage(value)` and a failure throws `DataCloneError`; values are copied, not referenced. ArrayBuffer, typed arrays and Blob/File are serializable types under HTML's structured clone (HTML not re-read here: S for the type list). P for the IDB side, high. — [IDB 3.0 § 4.5 put/add steps](https://www.w3.org/TR/IndexedDB-3/)
- Upgrade across tabs: when `open()` asks for a higher version, every other open connection without its close-pending flag gets a `versionchange` event; "If any of the connections in openConnections are still not closed, queue a database task to fire a version change event named blocked at request"; then "Wait until all connections in openConnections are closed" before the upgrade runs. So a second tab that does not call `db.close()` in `onversionchange` stalls the upgrade indefinitely (the request only gets `blocked`). P, high. — [IDB 3.0 § 5.1 Opening a database connection](https://www.w3.org/TR/IndexedDB-3/)
- First versions (MDN browser-compat-data, main branch, read 2026-10-31): IDBFactory Chrome 24, Edge 12, Firefox 16, Safari 8; `IDBObjectStore.getAll` Chrome 48, Firefox 44, Safari 10.1; `IDBTransaction.commit` Chrome 76, Firefox 74, Safari 15; `IDBTransaction.durability` Chrome 83, Firefox 126, Safari 15; `IDBFactory.databases` Chrome 72, Firefox 126, Safari 14; `getAllRecords` Chrome 141, Firefox 153, Safari "preview"; `getAll` options object Chrome 141 only. S (curated data), medium-high. — [mdn/browser-compat-data api/IDBTransaction.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/IDBTransaction.json), [IDBObjectStore.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/IDBObjectStore.json), [IDBFactory.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/IDBFactory.json)
- Chrome stores a serialized value above 65,536 bytes outside the inline record (`kIDBWrapThreshold = 65536`, "wrapping"; a compression threshold uses the same constant by default). P, high. — [Chromium indexeddb.mojom](https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/public/mojom/indexeddb/indexeddb.mojom), [idb_value_wrapping.cc](https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/renderer/modules/indexeddb/idb_value_wrapping.cc)
- Counter-evidence searched (large values): a search summary reports an older Chrome error "The serialized value is too large (size=140989466 bytes, max=133169152 bytes)" and a Chromium PSA that a missing large-value file now raises `NotFoundError`. U (pages not opened). — [blink-dev PSA (pointer)](https://groups.google.com/a/chromium.org/g/blink-dev/c/JmDqNNWGm20)

### Inferences
- ES5 is enough for all of IndexedDB: `indexedDB.open(name, version)` with `onupgradeneeded`/`onsuccess`/`onerror`/`onblocked`, transactions with `oncomplete`/`onerror`/`onabort`. Only `navigator.storage.estimate/persist/persisted` return promises, and ES5 code can still call `.then(fn)` on a native promise without a polyfill where they exist.
- For a "Save" of a project, request `{durability: 'strict'}` on the write transaction (feature-detected: older browsers ignore an unknown options argument per WebIDL dictionaries) and treat `oncomplete` as the save point; autosave can stay relaxed. That matches the spec's own advice and Chrome's migration example.
- The app must close its connection in `db.onversionchange` (and tell the user to reload), or a schema upgrade in a second tab will hang on `blocked`.
- Storing the geometry as ArrayBuffers/typed arrays rather than JSON strings avoids the JSON round trip; values above 64 KiB go to separate files in Chrome, which is where "missing large-value file" errors come from.

### Gaps
- Firefox and WebKit maximum single-value size: not found in source this session (Chrome's old 133,169,152-byte IPC cap is U and probably obsolete).
- What "default" durability maps to in Firefox and WebKit was taken from the Chrome post's claim ("all use relaxed"); not verified in Gecko/WebKit source.

## The WHATWG Storage Standard: buckets, best-effort vs persistent, estimate(), persist(), and how each browser grants it

### Takeaway
Storage is a Living Standard (last updated 19 October 2026): each origin has a local storage bucket
whose mode is "best-effort" or "persistent"; under pressure the UA clears best-effort buckets, and a
persistent bucket can only be cleared with the user's involvement. `persist()` exists since Chrome 55,
Firefox 57, Safari 15.2; `estimate()` since Chrome 61, Firefox 57, Safari 17. Firefox asks the user;
Chrome decides silently from site-importance signals; WebKit grants only to domains exempt from data
deletion (home-screen web app, app-bound or managed domains).

### Cited Findings
- "A local storage bucket has a mode, which is "best-effort" or "persistent". It is initially "best-effort"." It can only become persistent if permission for the "persistent-storage" powerful feature is granted; "The user agent cannot clear storage marked as persistent without involvement from the origin or user", useful "for resources the user creates locally". P, high. — [Storage Standard § 4, § 5](https://storage.spec.whatwg.org/)
- Storage pressure: the UA "should clear network state and local storage buckets whose mode is "best-effort""; if pressure continues it "should inform the user and offer a way to clear" the persistent ones. A bucket "must be cleared in its entirety". P, high. — [Storage Standard § 7, § 7.1](https://storage.spec.whatwg.org/)
- Quota: "an implementation-defined conservative estimate ... It must not be a function of the available storage space on the device"; UAs are "strongly encouraged to consider navigation frequency, recency of visits, bookmarking, and permission for "persistent-storage"". P, high. — [Storage Standard § 6](https://storage.spec.whatwg.org/)
- Obtaining a storage key fails ("return failure") if the origin is opaque or the user has disabled storage; `persist()`, `persisted()`, `estimate()` then reject with TypeError. P, high. — [Storage Standard § 3, § 8](https://storage.spec.whatwg.org/)
- Versions: StorageManager / persist / persisted Chrome 55, Firefox 57, Safari 15.2; estimate Chrome 61, Firefox 57, Safari 17; `usageDetails` Chrome 61 only. S (BCD), medium-high. — [mdn/browser-compat-data api/StorageManager.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/StorageManager.json)
- WebKit: "Starting in Safari 17.0 ... the Storage API is fully supported"; "WebKit currently grants a request based on heuristics like whether the website is opened as a Home Screen Web App". P (vendor post), high. — [WebKit: Updates to Storage Policy](https://webkit.org/blog/14403/updates-to-storage-policy/)
- WebKit source: `persist()` refuses when top origin and client origin differ (a frame), and otherwise grants only if the origin's registrable domain is in `domainsExemptFromWebsiteDataDeletion()` = app-bound domains ∪ managed domains ∪ persisted domains ∪ the standalone application domain; granting writes a `persisted` file in the origin's folder; persisted or active origins are skipped by eviction. P, high (trunk, 2026-10-31). — [NetworkStorageManager.cpp](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/NetworkProcess/storage/NetworkStorageManager.cpp), [ResourceLoadStatisticsStore.cpp](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/NetworkProcess/Classifier/ResourceLoadStatisticsStore.cpp)
- Firefox prompts: "In Firefox, when a site chooses to use persistent storage, the user is notified with a UI popup"; Safari and Chromium "automatically approve or deny ... and do not show any prompts". S (MDN), medium-high; matches web.dev 2020. — [MDN: Storage quotas and eviction criteria](https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/storage_api/storage_quotas_and_eviction_criteria/index.md), [web.dev: Persistent storage](https://web.dev/articles/persistent-storage)
- Chrome's heuristics (web.dev, 2020): site engagement, installed or bookmarked, notification permission. Chromium's "important sites" code still lists the reasons ENGAGEMENT (at least MEDIUM engagement), PERSISTENT, BOOKMARKS (at most 5 bookmarks used as signals), HOME_SCREEN, NOTIFICATIONS. S: the link from `persist()` to this file was not read (the permission-context file moved; two paths 404). — [web.dev: Persistent storage](https://web.dev/articles/persistent-storage), [important_sites_util.cc](https://chromium.googlesource.com/chromium/src/+/main/chrome/browser/engagement/important_sites_util.cc)
- web.dev advises calling `persist()` after a user gesture, not on load, because the browser "may prompt". S, medium. — [web.dev: Persistent storage](https://web.dev/articles/persistent-storage)

### Inferences
- In Safari (browser tab) `persist()` will normally resolve `false`; only the home-screen web app gets `true`. Code must treat `false` as normal, not as an error.
- Ask for persistence when the user first saves a project (a gesture), once; in Firefox it shows a prompt.

### Gaps
- Chrome's current exact grant algorithm (engagement threshold value, whether installed PWA alone suffices) was not read in the permission-context source (moved). Treat as S.
- What adds a domain to WebKit's `m_persistedDomains` was not traced.

## Quotas per browser, current numbers

### Takeaway
Chrome/Edge: pool 80% of total disk, per origin 60% (0.8 × 0.75), best-effort and persistent alike;
Firefox: temporary-storage limit 50% of disk (capped by an 8 TiB assumed capacity), group (eTLD+1)
limit min(20% of that, 10 GB), i.e. min(10% disk, 10 GB) best-effort, and persisted origins bounded by
the 50% limit only; Safari 17+/iOS 17+: per origin 60% of disk and 80% overall for browser apps, 15% / 20%
for other WebKit apps, the same as the browser for home-screen web apps, frames 10% of the parent, and no
more "use more space?" prompt. The often-quoted "Safari 1 GB + prompt" and "Firefox 2 GB group" are old.

### Cited Findings
- Chromium: `kPoolSizeRatio` 0.8 (80%), `kDefaultPerStorageKeyRatio = 0.75`, `per_storage_key_quota = pool_size * 0.75` → 60% of total disk; must-remain-available min(1 GB, 1%), should-remain-available min(2 GB, 10%); session-only (clear on exit) origins: min(300 MB randomized ±10%, 10% of pool). P, high. — [quota_settings.cc](https://chromium.googlesource.com/chromium/src/+/main/storage/browser/quota/quota_settings.cc), [quota_features.cc](https://chromium.googlesource.com/chromium/src/+/main/storage/browser/quota/quota_features.cc)
- Chrome "will always report 60% of the actual disk size" in `estimate()` (not free space), to limit cross-origin size leaks; other Chromium browsers "may factor in" free space. S (web.dev, 2024-09-23), medium; agrees with the code. — [web.dev: Storage for the web](https://web.dev/articles/storage-for-the-web)
- MDN: Chromium "an origin can store up to 60% of the total disk size in both persistent and best-effort modes"; browser uses at most 80%. S, high (matches P). — [MDN quotas](https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/storage_api/storage_quotas_and_eviction_criteria/index.md)
- Firefox: `GetTemporaryStorageLimit` "Allow temporary storage to consume up to 50% of disk capacity" with `maxAllowedCapacity = 8 TiB`; `GetGroupLimitForLimit`: `min(aLimit / 5, 10 GB)`, never below 10 MB nor above the limit; persisted origins are checked against the whole temporary limit instead of the group limit (`persisted ? mTemporaryStorageLimit : GetGroupLimit()`); a fingerprinting-resistance mode spoofs the limit. P, high. — [Gecko dom/quota/ActorsParent.cpp](https://raw.githubusercontent.com/mozilla-firefox/firefox/main/dom/quota/ActorsParent.cpp)
- MDN gives the same numbers: best-effort the smaller of 10% of disk or 10 GiB (group limit, per site); persistent up to 50% of disk capped at 8 TiB, not subject to the group limit; computed from total, not free, disk. S, high (matches P). Contradicted by web.dev's older "Firefox allows ... 50% of free disk space ... group ... up to 2GB" (S, outdated). — [MDN quotas](https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/storage_api/storage_quotas_and_eviction_criteria/index.md); [web.dev: Storage for the web](https://web.dev/articles/storage-for-the-web)
- WebKit: "Starting in Safari 17.0, and in WebKit apps for iOS 17, iPadOS 17 and macOS Sonoma: For a browser app, the origin quota is up to 60% of the total disk space. For other apps, ... up to 15%"; overall quota 80% / 20%; "Safari 17.0 no longer prompts users about a website wanting to use more space"; cross-origin frame quota "10% of the main frame's origin quota"; a standalone web app (Home Screen on iOS, Dock on macOS) "has the same origin quota and overall quota as when it is opened in a browser app"; quota "might change based on factors like existing usage and site visit frequency". P, high. — [WebKit: Updates to Storage Policy (2023-08-10)](https://webkit.org/blog/14403/updates-to-storage-policy/)
- WebKit source agrees: `defaultBrowserTotalQuotaRatio = 0.8`, `defaultBrowserOriginQuotaRatio = 0.6`, `defaultAppTotalQuotaRatio = 0.2`, `defaultAppOriginQuotaRatio = 0.15`, chosen by `isFullWebBrowserOrRunningTest()`. P, high. — [WebsiteDataStoreCocoa.mm](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/UIProcess/WebsiteData/Cocoa/WebsiteDataStoreCocoa.mm)
- Before Safari 17: "an origin is given an initial 1 GiB quota" then Safari asks the user (MDN); web.dev: about 1 GB, prompt in 200 MB steps, "I was unable to find any official documentation" (and installed PWA on iOS had its own container with no way to request more). S, medium (historic). — [MDN quotas](https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/storage_api/storage_quotas_and_eviction_criteria/index.md), [web.dev](https://web.dev/articles/storage-for-the-web)
- iOS/iPadOS: third-party browsers have used WebKit, so these quotas apply to them; in the EU (iOS 17.4+) other engines are allowed and bring their own policy. S (MDN), medium. — [MDN quotas](https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/storage_api/storage_quotas_and_eviction_criteria/index.md)
- Exceeding quota: IndexedDB/Cache/OPFS fail with `QuotaExceededError` (MDN, WebKit post); web.dev's IDB example checks `error.name == 'QuotaExceededError'` on the transaction's `onabort`. P (WebKit) / S, high. — [WebKit post](https://webkit.org/blog/14403/updates-to-storage-policy/), [web.dev](https://web.dev/articles/storage-for-the-web)

### Inferences
- Quota is not the constraint for a CAD/BIM project in any current browser in normal mode (even a 64 GB phone gives Safari about 38 GB per origin, Firefox about 6.4 GB best-effort); availability of free disk and eviction are.
- `estimate()` is a ceiling, not a promise (all three vendors say so); write errors must still be caught.

### Gaps
- Edge-specific changes to Chromium quota: not checked (Edge is Chromium; MDN treats it the same).
- Chrome on Android numbers: same code path assumed; not separately verified.

## Eviction: LRU under pressure, Safari's 7-day cap, what persist() protects

### Takeaway
All engines evict best-effort origins whole, least-recently-used first, under disk pressure or when
the overall pool is exceeded; persisted origins are skipped. Safari additionally deletes all
script-writable storage (IndexedDB, localStorage, sessionStorage, service-worker registrations and cache)
after seven days of Safari use without user interaction on the site, when tracking prevention is on;
home-screen web apps keep their own day counter and are not expected to lose first-party data, and the
time-based eviction is disabled for non-browser WebKit apps. Chrome adds a separate 400-day stale cutoff
for localStorage.

### Cited Findings
- WebKit: eviction "when exceeding the overall quota, when the system is under storage pressure, or when the site has not been interacted with by the user for some time"; by origin, LRU, where last use = last user interaction or last storage operation; excluded if it "has active page at the time of eviction, or its storage is in persistent mode". P, high. — [WebKit: Updates to Storage Policy](https://webkit.org/blog/14403/updates-to-storage-policy/)
- WebKit 7-day cap (March 2020; iOS/iPadOS 13.4, Safari 13.1): "deleting all of a website's script-writable storage after seven days of Safari use without user interaction on the site", for "Indexed DB, LocalStorage, Media keys, SessionStorage, Service Worker registrations and cache". Home-screen web apps "are not part of Safari and thus have their own counter of days of use ... We do not expect the first-party in such a web application to have its website data deleted"; Apple calls such deletion "a serious bug". P, high. — [WebKit: Full Third-Party Cookie Blocking and More (2020-03-24)](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/)
- WebKit source: `timeBasedEvictionMode()` returns Disabled when the app is not a full web browser; a build flag `TIME_BASED_EVICTION_SERVICE_WORKER_ONLY` narrows it to service-worker registrations only (default otherwise `AllTypes`); which flag Safari ships with was not determined. P, medium (code read; shipping config unknown). — [WebsiteDataStore.cpp](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/UIProcess/WebsiteData/WebsiteDataStore.cpp), [WebsiteDataStoreConfiguration.cpp](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/UIProcess/WebsiteData/WebsiteDataStoreConfiguration.cpp)
- Does the cap hit a site visited as first party? Yes: the 2020 post's rule is about the site's own storage after 7 days of Safari use without interaction; it is "gated on ... days of Safari use", not calendar days. P, high. MDN: "If an origin has no user interaction, such as click or tap, in the last seven days of browser use, its data created from script will be deleted." S. — [WebKit 2020](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/), [MDN quotas](https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/storage_api/storage_quotas_and_eviction_criteria/index.md)
- Chromium keeps per-origin last-access time in a SQLite QuotaDatabase "used to implement LRU eviction on storage pressure"; `QuotaTemporaryStorageEvictor` performs it. P, high. — [Chromium quota README](https://chromium.googlesource.com/chromium/src/+/main/storage/browser/quota/README.md)
- Chromium localStorage: "Storage keys become eligible for deletion after 400 days of inactivity" (`kLocalStorageStaleBucketCutoffInDays = 400`), and "After this many consecutive commit errors we'll throw away the entire database" (`kCommitErrorThreshold = 8`). P, high (constants; the deletion code path not read). — [dom_storage_constants.h](https://chromium.googlesource.com/chromium/src/+/main/components/services/storage/dom_storage/dom_storage_constants.h)
- MDN: eviction is LRU by origin, skips persisted origins, deletes all of an origin's data at once; Chrome research says data is "very rarely deleted". S, medium. — [MDN quotas](https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/storage_api/storage_quotas_and_eviction_criteria/index.md)
- Counter-evidence searched: none found contradicting the home-screen exemption; WebKit's own source puts the standalone application domain in the persist-exempt set (P), which supports it.

### Inferences
- In Safari (browser), a user who opens the app, saves a project, and does not interact with it for seven days of Safari use can lose the project; persist() is refused there, so the only defences are the home-screen install and a file export the user keeps.
- `persist()` protects against pressure/LRU and overall-quota eviction; it does not protect against the user clearing site data, nor (per the spec) against the UA asking the user under continued pressure.

### Gaps
- Whether a granted persist() exempts an origin from Safari's 7-day ITP deletion in a browser tab (the exempt-domain set suggests yes, but a browser tab rarely gets the grant).
- Firefox's eviction code (LRU over origins) not read; MDN relied on.

## localStorage: limits per browser, UTF-16 counting, synchronous cost, QuotaExceededError

### Takeaway
Effective limit is about 5 Mi characters per origin in Chrome and Firefox, and 5 MiB of bytes in
WebKit (where a string with any non-Latin-1 character counts 2 bytes per character, so JSON with such a
character in a value holds about 2.5 Mi characters). Firefox also has a 25 MiB per-site (eTLD+1) cap. It
is synchronous and blocks the main thread; failure is a `QuotaExceededError` DOMException.

### Cited Findings
- Chromium: `kPerStorageAreaQuota = 10 * 1024 * 1024` with a 100 KiB server-side over-quota allowance; Blink rejects a set when `(key.length() + value.length()) * 2 > kPerStorageAreaQuota`, i.e. counts 2 bytes per UTF-16 unit → 5,242,880 units for one item, and the whole area is bounded the same way. P, high. — [dom_storage_constants.h](https://chromium.googlesource.com/chromium/src/+/main/components/services/storage/dom_storage/dom_storage_constants.h), [cached_storage_area.cc](https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/renderer/modules/storage/cached_storage_area.cc)
- Firefox: `dom.storage.default_quota: 5 * 1024` (KiB) with the comment "Only allow relatively small amounts of data since performance of the synchronous IO is very bad. We are enforcing simple per-origin quota only"; `dom.storage.default_site_quota: 25 * 1024`; usage is `utf16Length(key) + utf16Length(value)`. P, high (prefs and accounting read; units per comparison inferred as UTF-16 units vs 5,242,880). — [StaticPrefList.yaml](https://raw.githubusercontent.com/mozilla-firefox/firefox/main/modules/libpref/init/StaticPrefList.yaml), [dom/localstorage/ActorsParent.cpp](https://raw.githubusercontent.com/mozilla-firefox/firefox/main/dom/localstorage/ActorsParent.cpp)
- WebKit: `constexpr unsigned localStorageQuotaInBytes = 5 * MB;` and the check sums `key.sizeInBytes() + value.sizeInBytes() <= quota()`. P for the code; that `sizeInBytes()` is 1 byte per character for 8-bit (Latin-1) strings and 2 for 16-bit strings is WTF::String's known behaviour, not re-read here: S. — [LocalStorageManager.cpp](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/NetworkProcess/storage/LocalStorageManager.cpp), [SQLiteStorageArea.cpp](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebKit/NetworkProcess/storage/SQLiteStorageArea.cpp)
- WebKit's 2023 policy applies to localStorage too (it is in scope with IndexedDB, Cache API etc.). P. — [WebKit post](https://webkit.org/blog/14403/updates-to-storage-policy/)
- MDN: Web Storage "limited to 10 MiB of data maximum on all browsers ... up to 5 MiB of local storage, and 5 MiB of session storage per origin", throws `QuotaExceededError`. S, medium (simplified; Chrome's "10 MiB" is per area in bytes). — [MDN quotas](https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/storage_api/storage_quotas_and_eviction_criteria/index.md)
- Synchronous cost: "LocalStorage should be avoided because it is synchronous and will block the main thread. It is limited to about 5MB and can contain only strings ... not accessible from web workers or service workers." S (web.dev), high. — [web.dev: Storage for the web](https://web.dev/articles/storage-for-the-web)
- Error naming: IDB 3.0 and WebIDL now define `QuotaExceededError` as a DOMException-derived interface instead of a name (2025 change); its `name` remains "QuotaExceededError". Legacy code 22 (and Firefox's old "NS_ERROR_DOM_QUOTA_REACHED", code 1014) is common folklore not re-read: U for the Firefox legacy name. P for the spec change. — [IDB 3.0 revision history](https://www.w3.org/TR/IndexedDB-3/)

### Inferences
- A JSON project of more than about 2.5 million characters can already fail in Safari if any value contains a non-Latin-1 character (a degree sign is Latin-1; CJK text, emoji-free Unicode names or a "≥" are not), and about 5.2 million characters in Chrome/Firefox.
- Detect quota errors by `e.name === 'QuotaExceededError' || e.code === 22 || e.code === 1014 || e.name === 'NS_ERROR_DOM_QUOTA_REACHED'` (the last two to confirm before use).

### Gaps
- Firefox legacy error name/code not verified in current source.
- Measured synchronous cost (ms per MB) not measured here: no browser experiment was run in this research; to be done in `reference/experiments/`.

## Private and incognito windows

### Takeaway
Chrome incognito gives IndexedDB a pool of 15-20% of physical RAM (randomized), one third of it per
origin; Firefox has supported IndexedDB in private windows since 115 (encrypted, pref on by default);
Safari's private localStorage works since Safari 11 (secondary reports). All private data is dropped
when the private session ends.

### Cited Findings
- Chromium incognito: "The incognito pool size is a fraction of the amount of system memory": ratio random between 0.15 and 0.2, `per_storage_key_quota = pool_size / 3`. P, high. Contradicts web.dev "approximately 5% of the total disk space" (S, outdated). — [quota_settings.cc](https://chromium.googlesource.com/chromium/src/+/main/storage/browser/quota/quota_settings.cc); [web.dev](https://web.dev/articles/storage-for-the-web)
- Firefox: pref `dom.indexedDB.privateBrowsing.enabled` default `true`, "Enable indexedDB in private browsing mode with encryption"; meta bug 1639542 "[meta] Support IndexedDB in Private Browsing Mode (with encrypted disk storage)" RESOLVED FIXED 2024-03-04. Firefox 115 as the first release is from Mozilla's intent-to-ship (search summary): U for the version. P for the pref and bug. — [StaticPrefList.yaml](https://raw.githubusercontent.com/mozilla-firefox/firefox/main/modules/libpref/init/StaticPrefList.yaml), [Bugzilla 1639542](https://bugzilla.mozilla.org/show_bug.cgi?id=1639542), [intent to ship (pointer)](https://groups.google.com/a/mozilla.org/g/dev-platform/c/yy7uUP47KGQ)
- Counter-evidence: CVE-2024-4767 (summary only): with `browser.privatebrowsing.autostart`, IDB files were not deleted on close, Firefox < 126. U. — [CVE-2024-4767 (pointer)](https://cve.circl.lu/vuln/cve-2024-4767)
- Safari: before Safari 11 private mode made `localStorage.setItem` throw; fixed in Safari 11 per TYPO3/Drupal reports. U (not opened). — [TYPO3 #81156 (pointer)](https://forge.typo3.org/issues/81156)
- MDN: private modes "may apply different quotas, and stored data is usually deleted when the private browsing mode ends". S. — [MDN quotas](https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/storage_api/storage_quotas_and_eviction_criteria/index.md)

### Inferences
- In private windows the app should warn that projects vanish at close and offer export; on a 4 GB-RAM device Chrome incognito allows roughly 200-270 MB per origin.

### Gaps
- Safari private-window IndexedDB quota and behaviour in Safari 17+: no reliable source found.
- Firefox private-window quota: not read.

## file:// pages: does storage work, and is the origin shared?

### Takeaway
No single answer. Chromium gives every `file://` URL the same origin ("file","",0) for storage, so all
local HTML files share one localStorage/IndexedDB. Firefox since 92 treats each file URL as its own origin
(storage is per file path; moving or renaming the file loses access to its data). WebKit trunk denies
IndexedDB and localStorage to local (file) origins with a SecurityError unless a quirk or universal-file-
access setting is on. The specification treats file origins as opaque/implementation-defined, and opaque
origins get no storage.

### Cited Findings
- Spec: a storage key is "failure" for an opaque origin. P. — [Storage Standard § 3](https://storage.spec.whatwg.org/)
- Chromium: "GURLs with a 'file' scheme are tricky. They are parsed as ('file', '', 0), but their behavior may differ from embedder to embedder. TODO(dcheng): This behavior is not consistent with Blink's notion of file URLs, which always creates an opaque origin"; and "'file' URLs all parse as ("file", "", 0)". P, medium-high (the storage key comes from this origin; the storage path not traced end to end). — [Chromium url/origin.h](https://chromium.googlesource.com/chromium/src/+/main/url/origin.h)
- Firefox: Bugzilla 1730419 (2021-09, Firefox 92: localStorage no longer shared between two local files in one folder), closed INVALID 2021-11-26. Mozilla: "Firefox by default treats each distinct file URL (distinct except for anchors or parameters) as a new origin, thus they cannot share local storage" (`security.fileuri.strict_origin_policy`, true since 3.6); "local storage was the last storage type that did interpret this at folder and not file level until we landed bug 1599979"; the pref is "not really a supported configuration anymore"; advice: serve from `http://localhost/`. A reporter states "Edge, Chrome, Opera behave as Firefox did before version 92"; a Mozilla engineer notes it "isn't supposed to work in Chromium either" (crbug 957695). P (bug record), high for Firefox. — [Bugzilla 1730419](https://bugzilla.mozilla.org/show_bug.cgi?id=1730419)
- WebKit trunk: `canAccessResource` returns No for IndexedDB, LocalStorage and StorageManager when `isOriginEquivalentToLocal(origin)` = `origin.isLocal() && !needsStorageAccessFromFileURLsQuirk() && !hasUniversalAccess()`; `IDBFactory.open()` then throws SecurityError "IDBFactory.open() called in an invalid security context" and `window.localStorage` throws SecurityError. Universal access is granted when web security is off or `allowUniversalAccessFromFileURLs`; the quirk when `settings().needsStorageAccessFromFileURLsQuirk()`. P, high for the code; which setting Safari.app enables is not known (S: a 2018 blog reports Safari's "SecurityError: The operation is insecure" for local pages and the Develop menu's "Disable Local File Restrictions"; U). — [ScriptExecutionContext.cpp](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/dom/ScriptExecutionContext.cpp), [IDBFactory.cpp](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/Modules/indexeddb/IDBFactory.cpp), [LocalDOMWindow.cpp](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/page/LocalDOMWindow.cpp), [Document.cpp](https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/dom/Document.cpp)

### Inferences
- The offline single-file build cannot rely on browser storage: Chrome shares it with every other local HTML file (any downloaded HTML can read or wipe the projects), Firefox ties it to the exact path, Safari may refuse it. The file:// mode needs an explicit "save project to file / open file" path (download + `<input type=file>`), with browser storage as a convenience cache only, and every storage call wrapped in try/catch.
- Feature-detect: in Safari, merely reading `window.localStorage` can throw; `indexedDB.open` can throw synchronously.

### Gaps
- Chrome/Firefox IndexedDB (as opposed to localStorage) behaviour on file:// not tested; a Playwright experiment with the installed Chromium could measure Chrome's (not Firefox's or Safari's) and should be kept in `reference/experiments/`.
- Safari.app's actual settings (`needsStorageAccessFromFileURLsQuirk`, `allowFileAccessFromFileURLs`) not found.

## Known bugs and counter-evidence

### Takeaway
IndexedDB is not trouble-free: on iOS, WebKit's networking process crashing drops IDB connections
("Connection to Indexed Database server lost"), a regression in iOS 17.4 still reported in 2025, and iOS
18.4 had a crash reading Blobs from IDB (fixed). Chrome wipes a localStorage database after 8 consecutive
commit errors. Robust code must reconnect, retry, and keep an exportable copy.

### Cited Findings
- WebKit 273827 "REGRESSION (iOS 17.4): IndexedDB failing with "UnknownError: Connection to Indexed Database server lost."", opened 2024-05-07, Safari 17; reporter: "hundreds of users (a high percentage of my iOS user base)", "causing data loss"; WebKit engineer: "This error happens when WebKit's Networking process crashes"; resolved CONFIGURATION CHANGED; last comment 2025-10-10: "Not resolved. Regression. Still occurring." P, high (bug record). — [WebKit bug 273827](https://bugs.webkit.org/show_bug.cgi?id=273827)
- WebKit 277615 (same error, Safari 18, opened 2024-08-04) resolved DUPLICATE 2026-03-27. P. — [WebKit bug 277615](https://bugs.webkit.org/show_bug.cgi?id=277615)
- WebKit 197050 "IndexedDB: An internal error was encountered in the Indexed Database server", opened 2019-04-18 (Safari 12), resolved CONFIGURATION CHANGED 2025-03-04. P. — [WebKit bug 197050](https://bugs.webkit.org/show_bug.cgi?id=197050)
- WebKit 292142 "REGRESSION (iOS 18.4.x): Accessing BLOBs stored in IndexedDB leads to Networking process getting terminated", opened 2025-04-28, RESOLVED FIXED 2025-07-08. P (status); the "lost data" detail is from a search summary, U. — [WebKit bug 292142](https://bugs.webkit.org/show_bug.cgi?id=292142)
- Chromium localStorage: whole database discarded after 8 consecutive commit errors; 400-day stale deletion. P. — [dom_storage_constants.h](https://chromium.googlesource.com/chromium/src/+/main/components/services/storage/dom_storage/dom_storage_constants.h)
- Chrome: missing large-value files now reported as `NotFoundError` (was "Failed to read large IndexedDB value"), tracking issue 362123231. U (summary only). — [blink-dev PSA (pointer)](https://groups.google.com/a/chromium.org/g/blink-dev/c/JmDqNNWGm20)

### Inferences
- Prefer ArrayBuffers over Blobs in IDB on iOS (the 18.4 crash was Blob-specific), and handle `UnknownError`/`InvalidStateError` by closing, reopening, and retrying once, then telling the user to export.
- The design should keep two independent copies of a saved project (for example last-good and current records in IDB, written in one transaction), plus the user-held file export, since no browser store is a guaranteed archive.

### Gaps
- No Chromium or Gecko IDB data-loss bug was opened in this pass (crbug search through the issue tracker's UI was not attempted; the tracker is script-rendered).
- Independent second-reader check (protocol step 9) not yet done for this note.
