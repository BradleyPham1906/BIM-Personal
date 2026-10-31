# Independent check of the local-storage research (step 9)

Second reader, 2026-10-31. Every source below was opened again by the checker (curl through the
environment's proxy, or a file read in the repository); no quote was taken from the five notes. Text
pages were reduced to plain text by a script and searched; source files were read at the lines named.
Downloads were kept in the session's scratchpad, never run. Levels: P primary, S secondary, U unverified.

Result: **27 confirmed, 1 corrected, 0 not confirmed** (28 rows below; item 6a is confirmed with its history
corrected, item 4 with a wording caution; neither changes a value the plan uses).

## Summary

| # | Claim | Verdict | Level after check |
|---|---|---|---|
| 1 | Chrome per-origin quota 60% of disk (pool 80% x 0.75) | CONFIRMED | P |
| 2 | Firefox temporary storage 50% of disk (8 TiB cap); group min(limit/5, 10 GB) = min(10%, 10 GB); persisted origins bounded by the 50% limit | CONFIRMED | P |
| 3 | Safari 17: origin 60% / overall 80% (browser apps), 15% / 20% (other apps), frames 10%, home-screen apps same as browser, no prompt | CONFIRMED | P |
| 4 | Safari 7-day cap on script-writable storage incl. IndexedDB; home-screen apps have their own day counter | CONFIRMED | P |
| 5 | WebKit grants persist() only by heuristics (exempt-domain set incl. standalone app), never in a cross-origin frame | CONFIRMED | P |
| 6a | Firefox: each file:// URL its own origin for localStorage since Firefox 92 | CONFIRMED, with a correction of history and pref name | P |
| 6b | WebKit: IndexedDB / localStorage / StorageManager throw SecurityError on file:// unless quirk or universal access | CONFIRMED | P (code); which setting Safari.app uses stays U |
| 7 | Chromium localStorage 10 MiB per area, 2 bytes per UTF-16 unit (5,242,880 units) | CONFIRMED | P |
| 8 | Chrome default IndexedDB durability relaxed since Chrome 121 | CONFIRMED | P (vendor) |
| 9 | BCD versions: persist, estimate, durability, pickers, getDirectory, CompressionStream | CONFIRMED | P |
| 10 | Mozilla FSA negative; WebKit FSA oppose | CONFIRMED | P |
| 11 | Chrome: no fetch-handler needed for menu install since 108 mobile / 112 desktop; manifest fields required for promotion | CONFIRMED | P (vendor) |
| 12 | Firefox 143 taskbar web apps on Windows (not Microsoft Store builds) | CONFIRMED | P |
| 13 | WebKit bug 273827 (IDB connection lost, iOS 17.4) | CORRECTED (the note omits Apple's resolution comment) | P |
| 14a | draw.io ES5 IndexedDB layer and localStorage-to-IndexedDB migration | CONFIRMED | P |
| 14b | Excalidraw quota error names and codes | CONFIRMED | P |
| 14c | idb-keyval Safari connection-close note | CONFIRMED | P |
| 14d | Licences: draw.io Apache-2.0, Excalidraw MIT, tldraw source-available not open source, idb-keyval Apache-2.0 | CONFIRMED | P |
| 15a | core/state.js:1 `LSK='acad3dV1'` | CONFIRMED | P (app code) |
| 15b | core/state.js:110-119 boot read of `acad3dV1`; :121 docs key and prefix | CONFIRMED | P |
| 15c | core/objects-save.js:48-61 `save3d()` writes `acad3dV1`, toasts once on failure | CONFIRMED | P |
| 15d | ui/project-tabs.js:104-106 pagehide flush of a pending autosave | CONFIRMED | P |
| 15e | ui/project-tabs.js:143-206 project switch and its rollback | CONFIRMED | P |
| 15f | assets/family-library.js:44-46 library rewritten whole, `console.warn` only on failure | CONFIRMED | P |
| 15g | io/project-file.js:5-8 envelope `{app, formatVersion:1, savedAt, data}` without cam, seq, docId | CONFIRMED | P |
| 15h | io/sketchup-import.js:20 `BIM_SKP` limits; annotation/annotation-overlay.js:207-229 image notes as data URIs, 4 MB cap | CONFIRMED | P |
| 16a | e01: localStorage max 5,242,880 code units per origin (Latin-1 and CJK alike), QuotaExceededError code 22 | CONFIRMED (re-run, identical) | P (measured, Chromium 153) |
| 16b | e05: all file:// pages share origin `file://` and one store; persist() false; estimate quota 3,221,225,472 / 10,737,418,240 | CONFIRMED (re-run, identical) | P (measured, Chromium 153) |

## Details

### 1. Chrome quota
- Note: storage-standards-and-browsers.md, Chromium quota_settings.cc / quota_features.cc.
- Read: chromium.googlesource.com `storage/browser/quota/quota_features.cc` (`?format=TEXT`, main):
  `kPoolSizeRatio` default `0.8 /* 80% */`; `kMustRemainAvailableRatio` 0.01, `kShouldRemainAvailableRatio` 0.1.
  `quota_settings.cc`: `kDefaultPerStorageKeyRatio = 0.75`; `pool_size_by_ratio = total * kTemporaryPoolSizeRatio`;
  `settings.per_storage_key_quota = pool_size * kPerStorageKeyTemporaryRatio` -> 0.8 x 0.75 = 60% of total disk.
  Session-only origins: `kSessionOnlyStorageKeyQuotaRatio = 0.1`. Incognito (not in the note's main claim): pool is
  15-20% of physical memory, per origin pool/3.
- Verdict: CONFIRMED. Level P.

### 2. Firefox quota
- Note: Gecko `dom/quota/ActorsParent.cpp`.
- Read: raw.githubusercontent.com/mozilla-firefox/firefox/main/dom/quota/ActorsParent.cpp.
  `GetTemporaryStorageLimit`: "Allow temporary storage to consume up to 50% of disk capacity",
  `maxAllowedCapacity = 8LL * teraByte`; a fingerprinting-resistance spoof and a fixed-limit pref override it.
  `GetGroupLimitForLimit`: `min(aLimit / 5, 10 GB)`, then `min(aLimit, max(x, 10 MB))`.
  Line ~8552: `persisted ? mTemporaryStorageLimit : GetGroupLimit()`.
- Verdict: CONFIRMED. Level P.

### 3. Safari 17 quotas
- Note: webkit.org/blog/14403/updates-to-storage-policy/ (2023-08-10).
- Read: the post (HTTP 200). Text: "For a browser app, the origin quota is up to 60% of the total disk space. For
  other apps, ... up to 15%"; overall "up to 80%" / "up to 20%"; Safari 17.0 "no longer prompts users about a
  website wanting to use more space"; cross-origin frame quota "10% of the main frame's origin quota"; standalone
  (Home Screen / Dock) web app "has the same origin quota and overall quota as when it is opened in a browser app".
- Verdict: CONFIRMED. Level P.

### 4. Safari 7-day cap
- Note: webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/ (2020-03-24).
- Read: the post. "deleting all of a website's script-writable storage after seven days of Safari use without user
  interaction on the site"; list: Indexed DB, LocalStorage, Media keys, SessionStorage, Service Worker registrations
  and cache; "Web applications added to the home screen are not part of Safari and thus have their own counter of
  days of use"; deletion there would be "a serious bug".
- Verdict: CONFIRMED. Level P. (The post says "own counter", not "exempt": a home-screen app is safe only while it
  is used; the note's wording "does not apply" is slightly stronger than the source.)

### 5. WebKit persist()
- Note: NetworkStorageManager.cpp, ResourceLoadStatisticsStore.cpp; the 14403 post.
- Read: raw WebKit main `Source/WebKit/NetworkProcess/storage/NetworkStorageManager.cpp` lines 930-949:
  `if (origin.topOrigin != origin.clientOrigin) return completionHandler(false);` then `persistOrigin`, lines
  915-928, grants only when `m_domainsExemptFromEviction` contains the client's registrable domain (fetched by
  `registrableDomainsExemptFromWebsiteDataDeletion`), and writes an empty `persisted` file.
  `ResourceLoadStatisticsStore.cpp` lines 812-821: exempt set = app-bound ∪ managed ∪ persisted domains ∪ the
  standalone application domain. The 14403 post: "WebKit currently grants a request based on heuristics like
  whether the website is opened as a Home Screen Web App."
- Verdict: CONFIRMED. Level P (the IPC link between the two files is inferred from the function names, not traced).

### 6. file:// origins
- (a) Firefox. Note: Bugzilla 1730419; the task named the pref `privacy.file_unique_origin`.
  Read: bugzilla.mozilla.org REST, bugs 1730419, 1500453, 1599979, and current StaticPrefList.yaml.
  1730419 (Firefox 92, RESOLVED INVALID 2021-11-26): Mozilla "treats each distinct file URL ... as a new origin,
  thus they cannot share local storage", governed by `security.fileuri.strict_origin_policy` (true by default; still
  in StaticPrefList.yaml, comment "Whether strict file origin policy is in effect"); "local storage was the last
  storage type that did interpret this at folder and not file level until we landed bug 1599979".
  1599979 "[meta] Enable LSNG on Release": cf_status_firefox92 fixed.
  **Correction (history and name):** unique file origins in general came earlier, with bug 1500453 "Treating file:
  URIs as unique origins", fixed in Firefox 68 (cf_status_firefox68 fixed, resolved 2019-07-17); that is the
  change whose pref was `privacy.file_unique_origin` (named in its comments). That pref is no longer in
  `StaticPrefList.yaml` or `all.js` on main. "Since 92" holds for localStorage only; IndexedDB and other storage
  were per-file earlier. The relevant live pref is `security.fileuri.strict_origin_policy`, which the note names.
  Verdict: CONFIRMED (the note's claim), with the history corrected. Level P.
- (b) WebKit. Read: raw WebKit main `ScriptExecutionContext.cpp` lines 950-978: `isOriginEquivalentToLocal` =
  `origin.isLocal() && !origin.needsStorageAccessFromFileURLsQuirk() && !origin.hasUniversalAccess()`; for
  IndexedDB, LocalStorage, StorageManager (and WebSQL, Plugin) `canAccessResource` returns No; opaque origins return
  No for all. `IDBFactory.cpp` line 101: SecurityError "IDBFactory.open() called in an invalid security context".
  `LocalDOMWindow.cpp` localStorage: `canAccessResource(LocalStorage) == No` -> `Exception { SecurityError }`.
  Verdict: CONFIRMED. Level P for the code; what Safari.app sets by default stays U, as the note says.

### 7. Chromium localStorage limit
- Read: googlesource `components/services/storage/dom_storage/dom_storage_constants.h`:
  `kPerStorageAreaQuota = 10 * 1024 * 1024`, `kPerStorageAreaOverQuotaAllowance = 100 * 1024`.
  `third_party/blink/renderer/modules/storage/cached_storage_area.cc` lines 80-83:
  `if ((key.length() + value.length()) * 2 > mojom::blink::StorageArea::kPerStorageAreaQuota) return false;`
  -> 10,485,760 / 2 = 5,242,880 UTF-16 units. Experiment comparison: see item 16.
- Verdict: CONFIRMED. Level P.

### 8. Chrome durability default
- Read: developer.chrome.com/blog/indexeddb-durability-mode-now-defaults-to-relaxed (Thomas Steiner): "The default
  durability mode in IndexedDB is changing from strict to relaxed from Chrome 121"; "to align with other major
  browsers which all use relaxed"; "strict does not ensure that changes are actually written immediately to disk";
  "Data migration is an example where strict durability is required"; old behaviour with `{ durability: 'strict' }`.
- Verdict: CONFIRMED. Level P (vendor's own post). The "Firefox and Safari use relaxed" part is the vendor's claim
  about other engines, not checked in their source (the note already says so).

### 9. MDN browser-compat-data (raw.githubusercontent.com/mdn/browser-compat-data/main/api/*.json, 2026-10-31)

| Feature | Chrome | Chrome Android | Firefox | Safari | Note's value |
|---|---|---|---|---|---|
| StorageManager.persist / persisted | 55 | mirror | 57 | 15.2 | same |
| StorageManager.estimate | 61 | mirror | 57 | 17 | same (note gives Safari 17) |
| StorageManager.getDirectory (OPFS) | 86 | 109 | 111 | 15.2 | same |
| IDBTransaction.durability | 83 | mirror | 126 | 15 | same |
| Window.showSaveFilePicker / showOpenFilePicker | 86 | 132 | false | false | same; experimental |
| CompressionStream | 80 | mirror | 113 | 16.4 | same |

- Verdict: CONFIRMED. Level P. Note for the plan: BCD marks the pickers on Chrome Android 132, so "Chromium only"
  includes Android, which the files note already says.

### 10. Standards positions
- Read: raw mozilla/standards-positions gh-pages `merged-data.json`: #154 "File System Access API" position
  `negative`; #738 "Implement subset of File System Access API" `defer`; #207 "Compression Streams" `positive`.
  raw WebKit/standards-positions main `summary.json`: issue 28 "File System Access" `oppose`, concerns `["security"]`.
- Verdict: CONFIRMED. Level P. (github.com issue pages refused, 403, per the files note; the data files suffice.)

### 11. Chrome installability
- Read: developer.chrome.com/blog/update-install-criteria: "we have removed the requirement to have a service worker
  that implements the fetch() method for installation from the menu, since version 108 on mobile and 112 on Desktop";
  "For now the algorithm that displays the install prompt still requires the presence of a fetch() handler".
  web.dev/articles/install-criteria: manifest with `short_name` or `name`; `icons` with a 192px and a 512px icon;
  `start_url`; `display` one of fullscreen, standalone, minimal-ui, window-controls-overlay;
  `prefer_related_applications` absent or false; 30 seconds on the page; "Users can install your web app even if it
  doesn't meet the PWA installability criteria".
- Verdict: CONFIRMED. Level P (vendor). Whether the prompt still needs a fetch handler today is not dated beyond the
  2023 post (open, as the note says).

### 12. Firefox 143
- Read: www.firefox.com/en-US/firefox/143.0/releasenotes/ (September 16, 2025): "On Windows, Firefox now supports
  running websites as web apps pinned directly to the taskbar"; "This feature is not currently available for Firefox
  installs from the Microsoft Store."
- Verdict: CONFIRMED. Level P.

### 13. WebKit bug 273827
- Read: bugs.webkit.org REST `/rest/bug/273827`, its comments (23) and history.
  Summary "REGRESSION (iOS 17.4): IndexedDB failing with "UnknownError: Connection to Indexed Database server lost."",
  created 2024-05-07, version Safari 17; reporter: "hundreds of users (a high percentage of my iOS user base)",
  "It is causing DATA LOSS"; beidson 2024-05-10: "This error happens when WebKit's Networking process crashes".
  Last comment 2025-10-10: "Bump. Not resolved. Regression. Still occurring."
- **Correction:** the note leaves out why it was closed. History: status NEW -> RESOLVED, resolution CONFIGURATION
  CHANGED on 2024-07-25, with the comment "We believe that this is fixed in iOS 17.6 beta (and iOS 18 beta) with an
  OS change outside WebKit. Please file new bugs if you still see similar issues". So the right reading is: Apple
  considers it fixed in iOS 17.6 / 18 by an OS change; one user disputes that in 2025 without a new bug in this record.
  The plan's defence (reopen on connection loss, files as backup) does not change.
- Verdict: CORRECTED. Level P.

### 14. Prior art (all at the notes' pinned commits, via raw.githubusercontent.com)
- (a) draw.io `src/main/webapp/js/diagramly/EditorUi.js` @3e707fd (43,487 lines): line 40061 `openDatabase`;
  40065 `window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB`; 40071 `indexedDB.open('database', 2)`;
  40079/40082 `oldVersion < 1` -> `objects` keyPath `key`; 40085-40090 `oldVersion < 2` -> `files`, `filesInfo`
  keyPath `title`, `EditorUi.migrateStorageFiles = isLocalStorage`; 40109 migration on success; 40334
  `setDatabaseItem` with `db.transaction(storeName, 'readwrite')`, `trx.oncomplete = success`, `trx.onerror = error`.
  `StorageFile.js`: 520-530 enumerate localStorage; 557 `StorageFile.migrate = function(db)`; 568 reads each file;
  622 `localStorage.removeItem(title)` after copying. CONFIRMED, P.
- (b) Excalidraw `excalidraw-app/data/LocalData.ts` @a758e93 lines 111-120: `QuotaExceededError`,
  `NS_ERROR_DOM_QUOTA_REACHED`, `QUOTA_EXCEEDED_ERR`, `code === 22`, `code === 1014`; lines 99-101 clear the atom on
  success. CONFIRMED, P.
- (c) idb-keyval `src/index.ts` @17a69a1 lines 12-38: cached open promise; "It seems like Safari sometimes likes to
  just close the connection. It's supposed to fire this event when that happens. Let's hope it does!";
  `db.onclose = () => (dbp = undefined)`; failure clears the cache. CONFIRMED, P.
- (d) Licences: draw.io `LICENSE` Apache License 2.0; Excalidraw `LICENSE` MIT (Copyright 2020 Excalidraw);
  tldraw `LICENSE.md` "tldraw license", a proprietary licence with Production/Development environment terms
  (source-available, not an OSI licence); idb-keyval `package.json` line 55 `"license": "Apache-2.0"`. CONFIRMED, P.

### 15. App code (read in /home/user/BIM-Personal/src/js/engine/, 2026-10-31)
- 15a `core/state.js:1`: `var LSK='acad3dV1';`. CONFIRMED.
- 15b `core/state.js:110-119`: `try{ var raw=localStorage.getItem(LSK); ... JSON.parse(raw); bimApplyStoredState(st);
  ... A3D_BOOT_DOC=st.docId }catch(e0){console.warn(...)}`; line 121 `A3D_DOCS_KEY='acad3dDocsV1',
  A3D_DOC_PREFIX='acad3dDocV1:'`; 122 `A3D_DOCS=bimDocsBoot()`; 123 `A3D_DOC_RT={}`. CONFIRMED.
- 15c `core/objects-save.js:48-61`: line 48 `function save3d(){`, `rec=bimProjectRecord(); rec.docId=A3D_DOCS.active;
  localStorage.setItem(LSK,JSON.stringify(rec))`; on failure `console.warn` and one toast ("browser storage is full.
  Use Save to keep a copy as a file"), reset on the next success; line 61 closes it. Lines 39-44 are the comment and
  `bimProjectRecord()`, "the one list of what a project is". CONFIRMED.
- 15d `ui/project-tabs.js:104-106`: `window.addEventListener('pagehide',function(){ if(saveT){clearTimeout(saveT);
  saveT=null;save3d();} });`, comment above records 8 of 8 lost walls before it. CONFIRMED.
- 15e `ui/project-tabs.js:143-206`: `bimDocsSwap(toId,stB,fromKey)`: ends the command, closes dialogs, sheet and section;
  parks the current record under `acad3dDocV1:<id>`, writes the next into `acad3dV1`, removing the parked copy if that
  fails; loads it, and on a load error writes the old record back, restores the undo stacks and toasts "could not be
  opened: its stored data is damaged"; per-project undo/view stash in `A3D_DOC_RT`; `bimDocsSave()` at 205; `return true`
  at 206. CONFIRMED.
- 15f `assets/family-library.js`: the task named line 45; the audit cites 44-46 (`bimSaveFamilyLibrary`), and line 45 is
  its body: `try{localStorage.setItem(FAMILY_LIB_KEY,JSON.stringify(A3D_FAMLIB));}catch(eS){console.warn(...)}`, no toast;
  line 6 `FAMILY_LIB_KEY='acad3dFamilyLibrary'`. CONFIRMED.
- 15g `io/project-file.js:5-8`: `bimBuildProjectEnvelope()` returns `{app:'acad3d-project',formatVersion:1,savedAt:
  new Date().toISOString(), data:{objs, levels, grids, layers, counts, ..., pres}}`; a search of line 7 finds no `cam`,
  `seq` or `docId`. CONFIRMED.
- 15h `io/sketchup-import.js:20`: `var BIM_SKP={maxTris:250000,blockTris:6000,blockChars:1500000};`. The phrase "so the
  library stays within browser storage" is not in that file; it is in `canvas_v10_STATUS.md:14145-14146`, which the
  audit cites in the same sentence (attribution loose, value right). `annotation/annotation-overlay.js:207-229`:
  comment "Read as a data URI so the drawing stays self-contained" (207-208), `bimPlaceImageNote`, `f.size>4*1024*1024`
  refused with a toast, `readAsDataURL`, stored as `{src:String(rd.result)}`, read error warned and toasted. CONFIRMED.

### 16. Experiments re-run (2026-10-31)
Scripts read in full first (`_lib.js`, `e01_localstorage_quota.js`, `e05_file_origin.js`): a localhost Node http server,
headless Chromium through Playwright, files written only to the scratch directory (set with `LS_EXP_SCRATCH` to the
checker's session scratchpad), nothing fetched or installed. Environment: Node with Playwright 1.63.0 from
`/opt/node-tools/node_modules`, browser build chromium-1243 (`browser.version()` = 153.0.8010.12), headless.
- 16a e01, 3 runs: Latin-1 max value 5,242,879 with a 1-char key (5,242,879 / 5,242,879 / 5,242,879, spread 0);
  U+4E00 max 5,242,879 (all 3); 100-char key max value 5,242,780 (all 3); several keys total 5,242,880 (4 full keys of
  1 Mi chars + 1,048,556 top-up; all 3). Error: `QuotaExceededError`, code 22, a DOMException, message "Failed to execute
  'setItem' on 'Storage': Setting the value of 'k' exceeded the quota." Every number equals experiments.md lines 83-87,
  and 5,242,880 = 10 MiB / 2, the Chromium source in item 7. CONFIRMED.
- 16b e05, 3 runs fresh context + 3 persistent profile: `location.origin` "file://" on both pages; isSecureContext true;
  estimate, persist, persisted, crypto.subtle, CompressionStream present; page B (other folder) read A's localStorage
  value and IndexedDB record and A then read B's, 6 of 6; persist() false and persisted() false; page A quota
  3,221,225,472 (fresh) / 10,737,418,240 (profile), usage 0; page B 3,221,299,200 with usage 73,728 (fresh) and
  10,737,419,998 with usage 1,758 (profile). Matches experiments.md lines 209-218 and line 155. CONFIRMED.
  Caution for the plan (already in the note): headless Chromium's quota here is a fixed 3 GiB / 10 GiB, not 60% of a
  real disk, so these numbers do not test item 1.

## Facts the plan relies on that stay weak (found during the check)
- Firefox's and Safari's default IndexedDB durability ("relaxed") rests only on Chrome's post; not read in Gecko or
  WebKit source. Level S for those two engines. The plan's use of `{durability:'strict'}` on an explicit Save does not
  depend on it.
- Safari's behaviour on file:// (which of the quirk / universal-access settings Safari.app enables) remains U; only
  WebKit's code paths are P.
- Whether Chrome's install prompt still needs a fetch handler after 2023 remains open (vendor post dated 2023).
- Home-screen apps "have their own counter of days of use" (WebKit 2020): the source does not say they are exempt from
  the 7-day rule, only that the counter is theirs and data loss would be "a serious bug". A plan should not promise
  exemption; file saves remain the backup.
- WebKit bug 273827: Apple attributes the fix to iOS 17.6 / 18; one later comment disputes it. Keep the reopen-on-close
  handling (idb-keyval's pattern) regardless.

## Refused or unreached hosts
- None refused in this check: chromium.googlesource.com, raw.githubusercontent.com, bugzilla.mozilla.org (REST),
  bugs.webkit.org (REST), webkit.org, developer.chrome.com, web.dev, www.firefox.com all answered 200.
- github.com web pages were not tried (raw used instead, as instructed).
