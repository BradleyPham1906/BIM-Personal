# Prior art: how browser design/CAD/drawing apps store users' projects locally

Research date: 2026-10-31. Scope: what comparable web apps actually do for local project storage, autosave,
recovery, file save/open and offline, read in their own code or vendor documents, plus the design (method only)
of the main IndexedDB wrapper libraries, for a zero-dependency ES5 app moving from localStorage to IndexedDB.

**Method.** Code was read as text, never run. Each repository was cloned blobless and shallow
(`git clone --depth 1 --filter=blob:none --no-checkout`) into the session scratchpad (outside the repository),
and files were read with `git show HEAD:<path>`. The pinned commit (HEAD on 2026-10-31, from `git ls-remote`) is
given for each. Line numbers refer to that commit. The GitHub REST API (`gh api`, `api.github.com/search`) was
refused by this session's proxy ("sessions are bound to their configured repositories"), so issue reports were
found by web search and then each one cited was opened with WebFetch.

**Evidence levels** (per `reference/research-protocol.md`): **P** = read in the primary source (the code, the
vendor's own page, the bug tracker thread); **S** = dependable secondary, gap stated; **U** = search summary only,
planning use only, "to confirm".

## Pinned sources

| Project | Repository | Commit (HEAD 2026-10-31) | Licence (read in repo) |
|---|---|---|---|
| idb-keyval 6.3.0 | github.com/jakearchibald/idb-keyval | 17a69a1165bef486d88950cb47d3913744f038ac | Apache-2.0 (package.json line 55; no LICENSE file at HEAD) |
| safari-14-idb-fix | github.com/jakearchibald/safari-14-idb-fix | 2a9084feb17a1226a5aed0fd3f3d3a49c5b3e9eb | not checked (method only) |
| idb | github.com/jakearchibald/idb | 654c746bef13f9fe7f5871e03ac58015cebace5a | ISC (LICENSE) |
| localForage | github.com/localForage/localForage | fb78c77ee583fb727a558c439b5174aca38c5924 | Apache-2.0 (LICENSE) |
| Dexie.js 4.4.7 | github.com/dexie/Dexie.js | 45aade72aa19a601e6a13aa877beb7389e15b5d2 | Apache-2.0 (LICENSE) |
| Excalidraw | github.com/excalidraw/excalidraw | a758e93d6a03e9f995973703cb886850a398a6d3 | MIT (LICENSE) |
| tldraw | github.com/tldraw/tldraw | 9e700c63f66c040f172dbd7fef936a888ac4b8cc | tldraw licence (LICENSE.md): source-available, **not** open source; production use needs a licence key. Method only, no code taken. |
| draw.io | github.com/jgraph/drawio | 3e707fd20b6930778d6f6bf6e4d0079b4bce366b | Apache-2.0 (LICENSE) |
| Graphite | github.com/GraphiteEditor/Graphite | b39ec01d7d0b34d76122aaec5a48f82fd701583e | Apache-2.0 / MIT (LICENSE-APACHE, LICENSE-MIT) |
| That Open engine_components 3.4.0 | github.com/ThatOpen/engine_components | ad540db9c60362865362cbcdea2a1dfc623bc299 | MIT (package.json line 23) |

## Search log

| # | Where | Query / action | What came back | Kept / set aside, why |
|---|---|---|---|---|
| 1 | GitHub API via `gh` | `repos/<r>` and `commits/HEAD` for 14 repos | 403 for every repo: session bound to its configured repositories | Set aside; used `git ls-remote` and blobless clones instead (worked) |
| 2 | git | `git ls-remote https://github.com/<r> HEAD` | 10 commit SHAs (table above) | Kept: the pins |
| 3 | git | blobless clones, `git ls-tree -r` grep for storage files | Paths of storage code in each repo | Kept: located the files read below |
| 4 | git | `git show HEAD:<path>` for ~35 files | Source text | Kept: all P facts below |
| 5 | api.github.com/search/issues | 4 issue searches (Excalidraw lost, tldraw indexeddb lost, drawio draft lost, Excalidraw safari) | Refused by proxy | Set aside; moved to web search |
| 6 | Web search | "excalidraw github issue lost drawing localStorage cleared" | Discussions #7013, unrelated results | Set aside; too indirect |
| 7 | Web search | "tldraw github issue indexeddb data lost safari" | No tldraw issue; WebKit bugs 266559, 200078, 235579, 292142; a gist | Kept WebKit 266559 (opened, below); others not opened (U); no tldraw-specific report found |
| 8 | Web search | "webkit storage policy 7-day cap script-writable storage..." | itnews, Didomi, engineered.at, WebKit bugs | Pointers only; went to WebKit's own blog posts |
| 9 | Web search | "That Open Company components IndexedDB cache fragments IfcStreamer useCache" | docs.thatopen.com IfcStreamer pages | U only; checked the repo instead (IfcStreamer absent at HEAD) |
| 10 | Web search | "Photopea local storage files offline save browser" | Reviews, directories, a forum post | U only: no Photopea primary document found; kept as a gap |
| 11 | WebFetch | webkit.org/blog/14403/updates-to-storage-policy/ | Safari 17 quotas, eviction, persist() | Kept (P) |
| 12 | WebFetch | bugs.webkit.org/show_bug.cgi?id=266559 | Safari wiping localStorage + IndexedDB, fixed Jan 2024 | Kept (P) |
| 13 | WebFetch | webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/ | 7-day cap text, home-screen apps | Kept (P) |
| 14 | Web search (extended) | "github.com/excalidraw/excalidraw/issues "lost" all my drawings browser storage" | Issues #7870, #8968, #9480, #9195, #8738, #12202, #10861; discussions #6463, #6487 | Opened #7870 (P); rest U (titles and summaries only) |
| 15 | Web search | "Figma help center offline editing unsynced changes browser storage" | help.figma.com/hc/en-us/articles/360040328553, forum | Opened the help article (P); forum set aside (anecdotal) |
| 16 | Web search | "draw.io browser storage option deprecated..." | drawio.com docs, forums | Opened drawio.com/docs/security/diagrams-offline (P); forums U |
| 17 | WebFetch | github.com/excalidraw/excalidraw/issues/7870 | Maintainer replies | Kept (P) |
| 18 | WebFetch | help.figma.com/hc/en-us/articles/360040328553 | IndexedDB, 30 days / 7 days Safari | Kept (P) |
| 19 | WebFetch | drawio.com/docs/security/diagrams-offline/ | Offline use; no storage-loss warning on that page | Kept (P), and the absence noted |

Not searched for lack of budget (gaps, below): Penpot, JSCAD, Onshape, SketchUp for Web, tldraw's issue tracker
directly, Excalidraw issues other than #7870 opened in full.

---

## 1. What the open-source apps actually do (storage split, file save/open, offline)

### Takeaway
The mature apps split storage the same way: the scene's structured data in one place written whole on a short
debounce, binary blobs (images, assets) as separate IndexedDB records keyed by id, small preferences and
cross-tab "version" flags in localStorage. Excalidraw still keeps the scene itself in localStorage (only images and
the library in IndexedDB); tldraw and draw.io keep the document in IndexedDB; Graphite has moved documents out of
IndexedDB into the Origin Private File System (OPFS). All of them treat a real file (download, or File System
Access API) as the user's backup, not browser storage.

### Cited Findings
- **Excalidraw, scene in localStorage (P, high).** `excalidraw-app/data/LocalData.ts` lines 73-109: the
  non-deleted elements are written with `localStorage.setItem("excalidraw", JSON.stringify(...))` and app state
  under `"excalidraw-state"`; key names in `excalidraw-app/app_constants.ts` lines 39-52 —
  [LocalData.ts](https://github.com/excalidraw/excalidraw/blob/a758e93d6a03e9f995973703cb886850a398a6d3/excalidraw-app/data/LocalData.ts),
  [app_constants.ts](https://github.com/excalidraw/excalidraw/blob/a758e93d6a03e9f995973703cb886850a398a6d3/excalidraw-app/app_constants.ts)
- **Excalidraw, binary files in IndexedDB, one record per file (P, high).** `LocalData.ts` line 49 creates an
  idb-keyval store `("files-db", "files-store")`; lines 211-233 save each added file with `set(id, fileData)`,
  collecting per-file errors in an `erroredFiles` map rather than failing the batch — same file.
- **Excalidraw, image garbage collection by last use (P, high).** `LocalData.ts` lines 53-71: a file not on the
  canvas and not retrieved for 24 hours is deleted; lines 178-209: every load rewrites `lastRetrieved: Date.now()`
  on the record so "last used", not "created", drives eviction — same file.
- **Excalidraw, library moved from localStorage to IndexedDB with a migration adapter (P, high).** `LocalData.ts`
  lines 236-284: `LibraryIndexedDBAdapter` (db `excalidraw-library-db`) and `LibraryLocalStorageMigrationAdapter`
  that reads the legacy localStorage key once and removes it — same file.
- **Excalidraw, file save/open through browser-fs-access (P, high).** `packages/excalidraw/data/filesystem.ts`
  lines 1-75 wrap `fileOpen`/`fileSave` from `browser-fs-access` (0.38.0, `packages/excalidraw/package.json`
  line 93), passing an existing `FileSystemFileHandle` so repeated saves overwrite the same file where the File
  System Access API exists — [filesystem.ts](https://github.com/excalidraw/excalidraw/blob/a758e93d6a03e9f995973703cb886850a398a6d3/packages/excalidraw/data/filesystem.ts)
- **tldraw, everything in IndexedDB, four stores (P, high).** `packages/editor/src/lib/utils/sync/LocalIndexedDb.ts`
  lines 8-56: database name `"TLDRAW_DOCUMENT_v2" + persistenceKey`, opened at version 4 via the `idb` library,
  with stores for records, schema, session state and assets (blobs, lines 305-325) —
  [LocalIndexedDb.ts](https://github.com/tldraw/tldraw/blob/9e700c63f66c040f172dbd7fef936a888ac4b8cc/packages/editor/src/lib/utils/sync/LocalIndexedDb.ts)
- **tldraw stores records one per key, writes diffs, not the whole document (P, high).** `LocalIndexedDb.ts`
  lines 205-240 (`storeChanges`: `put` each added/updated record, delete removed ones, then put schema and session
  state in the same transaction) versus lines 255-280 (`storeSnapshot`: `clear()` then put all) — same file.
- **draw.io, ES5 hand-written IndexedDB layer (P, high).** `src/main/webapp/js/diagramly/EditorUi.js` lines
  40061-40330: `openDatabase` opens `indexedDB.open('database', 2)`, with prefixed fallbacks
  (`mozIndexedDB`, `webkitIndexedDB`); stores `objects` (keyPath `key`), `files` and `filesInfo` (keyPath
  `title`); `setDatabaseItem` (lines 40334-40368) writes to several stores in one transaction and reports through
  `oncomplete`/`onerror` callbacks — [EditorUi.js](https://github.com/jgraph/drawio/blob/3e707fd20b6930778d6f6bf6e4d0079b4bce366b/src/main/webapp/js/diagramly/EditorUi.js)
- **draw.io keeps file content and file metadata in separate stores (P, high).** `files` holds `{title, data}`,
  `filesInfo` holds `{title, size, lastModified, type}` (EditorUi.js, the import in `openDatabase` around the
  `importOneFile` function), so a file list can be read without loading every diagram — same file.
- **draw.io migrated localStorage files into IndexedDB on the version-2 upgrade (P, high).** EditorUi.js sets
  `EditorUi.migrateStorageFiles` in `onupgradeneeded` when `oldVersion < 2`, then calls `StorageFile.migrate(db)`
  on success; `StorageFile.js` lines 520-600 enumerate localStorage entries and copy them —
  [StorageFile.js](https://github.com/jgraph/drawio/blob/3e707fd20b6930778d6f6bf6e4d0079b4bce366b/src/main/webapp/js/diagramly/StorageFile.js)
- **draw.io says browser storage is device-and-browser bound (P, medium).** Its offline page says that in the
  browser you can "save diagrams to your device, or keep them only in your browser"; the page carries no warning
  about loss — [draw.io, Diagrams offline](https://www.drawio.com/docs/security/diagrams-offline/). Forum
  quotations of draw.io guidance that browser files are lost when cookies are cleared were seen only in search
  summaries (U) — [allaboutcircuits forum](https://forum.allaboutcircuits.com/threads/saving-google-drawio-files.164422/)
- **Graphite moved documents from IndexedDB to OPFS (P, high).** `frontend/src/utility-functions/persistence.ts`
  lines 70-87: legacy documents read from the IndexedDB key `documents` are written as files under
  `navigator.storage.getDirectory()` / `documents/<16-hex id>/legacy.graphite`; lines 97-119: each migrated
  document is first copied into a `documents_migrated` backup key, then removed from `documents`, in one
  transaction; IndexedDB keeps only `state` and `preferences` (lines 39-63; db `graphite`, store `store`,
  lines 3-4, 220-262) — [persistence.ts](https://github.com/GraphiteEditor/Graphite/blob/b39ec01d7d0b34d76122aaec5a48f82fd701583e/frontend/src/utility-functions/persistence.ts)
- **Graphite serialises all persistence operations through one promise queue (P, high).**
  `frontend/src/managers/persistence.ts` lines 17-31: each write/read is chained on a `tail` promise so they run
  in request order and a failure does not break the chain —
  [managers/persistence.ts](https://github.com/GraphiteEditor/Graphite/blob/b39ec01d7d0b34d76122aaec5a48f82fd701583e/frontend/src/managers/persistence.ts)
- **Figma, offline edits in IndexedDB, as a safeguard not an offline mode (P, high).** Figma: changes "are saved
  locally to your browser's IndexedDB, and can't be accessed from another computer or device"; kept "up to 30
  days in most browsers, and 7 days in Safari"; not saved in private mode, when the quota is full, or when an
  extension blocks storage — [Figma Learn, What can I do offline in Figma?](https://help.figma.com/hc/en-us/articles/360040328553)
- **That Open (IFC): no IndexedDB in engine_components 3.4.0 HEAD (P for absence, medium).** `git grep` for
  `indexedDB|Dexie|getDirectory` in the HEAD tree finds nothing in source, and no file name contains "streamer";
  the CHANGELOG records an earlier "add indexedDB cleaner, fix lost geometries in streamer" (line 333) and "make
  streamer file cacher public" (line 241) — [CHANGELOG.md](https://github.com/ThatOpen/engine_components/blob/ad540db9c60362865362cbcdea2a1dfc623bc299/CHANGELOG.md).
  The current docs describe an IfcStreamer `useCache`/`clearCache()` for downloaded fragment files, one search
  summary saying it uses the File System API (U) — [docs.thatopen.com IfcStreamer](https://docs.thatopen.com/api/@thatopen/components-front/classes/IfcStreamer)
- **Photopea (U only).** Reviews say it works offline after first load and keeps files local unless the user
  saves to its PeaDrive cloud; a forum post mentions an "Edit > Local Storage..." menu for fonts/brushes — no
  primary document found — [shotkit review](https://shotkit.com/photopea-review/), [gimpchat](https://gimpchat.com/viewtopic.php?p=284599)

### Inferences
- The common design for a CAD/BIM project: one small "project index" record (name, size, modified, schema
  version, thumbnail) separate from the heavy project body, and heavy binary (meshes, textures, imported models)
  as separate records keyed by content id. draw.io's `files`/`filesInfo` split and Excalidraw's one-record-per-file
  are the two closest ES5-compatible precedents.
- Chunking: none of the apps read chunks one large blob; they split by object (one record per element in tldraw,
  per image in Excalidraw, per asset in tldraw). For meshes this suggests one record per mesh/asset, not byte
  ranges of one buffer. (Inference; no app read chunked a single large binary.)
- OPFS (Graphite) is the newer option for whole-document files; it is a separate decision from IndexedDB and
  needs its own compatibility research (OPFS `createWritable` support in Safari is not checked here).

### Gaps
- Penpot, JSCAD, Onshape, SketchUp for Web: not read (budget). Penpot is server-based; whether it keeps any local
  project copy is unknown here.
- Photopea: no primary source; closed source.
- Where That Open's current fragment cache lives (likely the `@thatopen/fragments` repository) was not read.

## 2. Autosave intervals, flushing on exit, crash recovery

### Takeaway
Autosave is debounced at 300 ms to 1.5 s with a forced flush when the tab hides, blurs or unloads; draw.io adds a
30 s maximum delay and a separate crash-recovery draft record with an "alive check" that finds drafts left by
tabs that no longer exist. tldraw explicitly flushes on `pagehide` and on `visibilitychange` to hidden because
mobile browsers can discard a page without any unload event.

### Cited Findings
- **Excalidraw debounce 300 ms (P, high).** `SAVE_TO_LOCAL_STORAGE_TIMEOUT = 300` (`app_constants.ts` line 2),
  used by `LocalData._save = debounce(..., SAVE_TO_LOCAL_STORAGE_TIMEOUT)` (`LocalData.ts` lines 125-141) —
  [app_constants.ts](https://github.com/excalidraw/excalidraw/blob/a758e93d6a03e9f995973703cb886850a398a6d3/excalidraw-app/app_constants.ts)
- **Excalidraw does not save while the tab is hidden, and flushes on blur/hidden/unload (P, high).**
  `LocalData.isSavePaused` returns `document.hidden || locker.isLocked()` (`LocalData.ts` lines 170-172);
  `excalidraw-app/App.tsx` lines 656-679 call `LocalData.flushSave()` on `unload`, on `blur` and when
  `document.hidden`; lines 689-711 flush on `beforeunload` and call `preventUnload` while image files are still
  uploading — [App.tsx](https://github.com/excalidraw/excalidraw/blob/a758e93d6a03e9f995973703cb886850a398a6d3/excalidraw-app/App.tsx)
- **tldraw throttle 350 ms, retry 10 s after an error (P, high).** `PERSIST_THROTTLE_MS = 350`,
  `PERSIST_RETRY_THROTTLE_MS = 10_000` (`TLLocalSyncClient.ts` lines 16-19) —
  [TLLocalSyncClient.ts](https://github.com/tldraw/tldraw/blob/9e700c63f66c040f172dbd7fef936a888ac4b8cc/packages/editor/src/lib/utils/sync/TLLocalSyncClient.ts)
- **tldraw flushes on `pagehide` and on hidden, never before the first load (P, high).** Lines 148-170: the
  comment says "`pagehide` is the last reliable event before unload on desktop; on mobile the page can be
  discarded without it firing, so we also flush when the tab is hidden"; the flush is skipped until `didLoad`
  because "a full write would overwrite the saved document with an empty store" — same file.
- **tldraw waits for a closing client's flush before its own first write (P, high).** Lines 243-246: "our first
  write is a full snapshot, so it would erase whatever a client that just closed on this key is still flushing" —
  it awaits `pendingFlushes.get(persistenceKey)` — same file.
- **tldraw: on a failed write, the next write is a full snapshot (P, high).** Lines 440-491: the diff queue is
  swapped out before writing; on error `shouldDoFullDBWrite = true` so no change is lost by a transient failure,
  then the user is alerted and the page reloaded — same file.
- **tldraw keeps the transaction alive across close (P, high).** `LocalIndexedDb.ts` lines 150-172: it awaits
  `tx.done` in a `finally` "otherwise a persist racing an unmount is silently rolled back" —
  [LocalIndexedDb.ts](https://github.com/tldraw/tldraw/blob/9e700c63f66c040f172dbd7fef936a888ac4b8cc/packages/editor/src/lib/utils/sync/LocalIndexedDb.ts)
- **draw.io: 1.5 s autosave, 30 s forced, revisions every 5 min (P, high).** `DrawioFile.js` line 78
  `autosaveDelay = 1500`, line 161 `maxAutosaveDelay = 30000` ("maximum delay before an autosave is forced even if
  the graph is being changed"), lines 232-235 `maxAutosaveRevisionDelay = 300000` —
  [DrawioFile.js](https://github.com/jgraph/drawio/blob/3e707fd20b6930778d6f6bf6e4d0079b4bce366b/src/main/webapp/js/diagramly/DrawioFile.js)
- **draw.io crash-recovery drafts (P, high).** `DrawioFile.prototype.saveDraft` (around lines 3127-3170) writes
  `{type:'draft', created, modified, data, title, fileObject, aliveCheck}` under key `.draft_<guid>` in the
  `objects` store; empty diagrams remove the draft instead; any exception removes the draft — same file.
- **draw.io's alive check finds orphaned drafts (P, high).** `App.js` `checkDrafts` (around lines 5150-5180)
  writes a fresh guid to `localStorage['.draft-alive-check']`; every live tab, on that `storage` event
  (lines 4195-4215), re-saves its own draft stamped with the guid; after a timeout, drafts whose `aliveCheck` is
  not the guid belong to dead tabs and are offered for recovery (`filterDrafts`, lines 5085-5145): one draft is
  loaded directly, several open a picker (`DraftDialog`) —
  [App.js](https://github.com/jgraph/drawio/blob/3e707fd20b6930778d6f6bf6e4d0079b4bce366b/src/main/webapp/js/diagramly/App.js)

### Inferences
- A 300-1500 ms debounce plus a hard maximum (draw.io's 30 s) prevents a user who never pauses from never saving;
  the app should have both.
- Flush triggers to copy: `visibilitychange` to hidden and `pagehide` (tldraw's reasoning), plus `blur`
  (Excalidraw). `unload`/`beforeunload` alone are not enough on phones.
- An IndexedDB write started in `pagehide` may not finish; tldraw accepts this and relies on the earlier hidden
  flush. (Inference; no app documents a guarantee.)
- draw.io's alive-check is pure ES5 and localStorage `storage` events; it is the simplest proven crash-recovery
  design for multiple tabs.

### Gaps
- None of the apps document a measured worst-case data window on mobile discard; a test from here would be needed.

## 3. Schema versioning and migration

### Takeaway
Two layers are versioned separately: the IndexedDB database version (stores and indexes, upgraded in
`onupgradeneeded` with cumulative `if (oldVersion < n)` steps), and the document schema stored inside the data
(migrated in code on load). Every app read keeps a legacy-format reader and migrates once, keeping a backup copy
until the move is confirmed.

### Cited Findings
- **draw.io: cumulative `oldVersion` steps (P, high).** `onupgradeneeded` creates `objects` when
  `oldVersion < 1` and `files`/`filesInfo` when `oldVersion < 2` (EditorUi.js lines ~40072-40095) —
  [EditorUi.js](https://github.com/jgraph/drawio/blob/3e707fd20b6930778d6f6bf6e4d0079b4bce366b/src/main/webapp/js/diagramly/EditorUi.js)
- **tldraw: stores created if missing, document schema stored with data and migrated on load (P, high).**
  `LocalIndexedDb.ts` lines 31-45 create each store only if `!objectStoreNames.contains(...)`; the serialized
  schema is written with every change (lines 233, 271); `TLLocalSyncClient.ts` lines 263-275 call
  `schema.migrateStoreSnapshot` and fail the load with "Failed to migrate store" on error; a missing stored schema
  is treated as the earliest version (line 268) —
  [TLLocalSyncClient.ts](https://github.com/tldraw/tldraw/blob/9e700c63f66c040f172dbd7fef936a888ac4b8cc/packages/editor/src/lib/utils/sync/TLLocalSyncClient.ts)
- **tldraw migrates a legacy asset database into the new one (P, high).** `LocalIndexedDb.ts` lines 58-92:
  checks `indexedDB.databases()` (when available) for `TLDRAW_ASSET_STORE_v1...`, copies every asset into the new
  database's assets store, closes both — same repository.
- **Graphite: migration keeps a backup (P, high).** `persistence.ts` lines 97-119 copy each document into
  `documents_migrated` before deleting it from `documents`, in one transaction —
  [persistence.ts](https://github.com/GraphiteEditor/Graphite/blob/b39ec01d7d0b34d76122aaec5a48f82fd701583e/frontend/src/utility-functions/persistence.ts)
- **localForage: refuses impossible downgrades, aligns versions (P, high).** `src/drivers/indexeddb.js` lines
  224-262: if the requested version is lower than the stored one, it warns "can't be downgraded" and uses the
  stored version; a missing store bumps the version by one to trigger `upgradeneeded`; a `ConstraintError` from an
  already-existing store is caught and warned (lines 162-184) —
  [indexeddb.js](https://github.com/localForage/localForage/blob/fb78c77ee583fb727a558c439b5174aca38c5924/src/drivers/indexeddb.js)
- **Dexie: retries open on `VersionError` without a fixed version (P, high).** `src/classes/dexie/dexie-open.ts`
  lines 168-172: on `VersionError` with a native version set, it retries with `nativeVerToOpen = 0` —
  [dexie-open.ts](https://github.com/dexie/Dexie.js/blob/45aade72aa19a601e6a13aa877beb7389e15b5d2/src/classes/dexie/dexie-open.ts)

### Inferences
- An older copy of the app (a cached tab, or the offline `canvas_v10.html` file) opening a database a newer copy
  upgraded gets `VersionError`; the app must catch it and say "a newer version of the app has updated this
  project store; reload", not fail silently. (Inference from localForage/Dexie handling.)
- Copying, not moving, localStorage projects into IndexedDB and deleting the old key only after the IndexedDB
  transaction's `oncomplete` matches Graphite's backup pattern and Excalidraw's migration adapter.

### Gaps
- No app read stores a checksum of the document to detect corruption; whether any does was not found.

## 4. Multiple tabs: BroadcastChannel, storage events, onversionchange, blocked upgrades

### Takeaway
Tabs are coordinated with cheap signals: Excalidraw writes a timestamp to localStorage after each save and
reloads from storage when a tab regains focus and sees a newer timestamp; tldraw broadcasts diffs over
`BroadcastChannel` and refuses to run against a tab with a different schema; draw.io uses localStorage `storage`
events. Every wrapper and app read closes its connection in `onversionchange` so another tab's upgrade is not
blocked. None of the code read uses Web Locks.

### Cited Findings
- **Excalidraw: timestamp versions in localStorage (P, high).** `excalidraw-app/data/tabSync.ts` lines 1-39:
  each save writes `Date.now()` under `version-dataState` / `version-files`; `isBrowserStorageStateNewer` compares
  with the tab's in-memory copy; `App.tsx` lines 597-654 reload the scene from storage on `focus` /
  `visibilitychange` when storage is newer (debounced `SYNC_BROWSER_TABS_TIMEOUT = 50` ms) —
  [tabSync.ts](https://github.com/excalidraw/excalidraw/blob/a758e93d6a03e9f995973703cb886850a398a6d3/excalidraw-app/data/tabSync.ts)
- **Excalidraw: the file-version flag is set before the IndexedDB write (P, high).** `LocalData.ts` lines
  215-218: "let's update the flag optimistically. Hopefully nothing fails" — an admitted race —
  [LocalData.ts](https://github.com/excalidraw/excalidraw/blob/a758e93d6a03e9f995973703cb886850a398a6d3/excalidraw-app/data/LocalData.ts)
- **tldraw: BroadcastChannel with schema check (P, high).** `TLLocalSyncClient.ts` lines 52-65 fall back to a mock
  where `BroadcastChannel` is undefined; lines 120-140 post each diff with the serialized schema; lines 183-216:
  a tab with an older schema is told to refresh, and a tab that sees a newer schema reports "Schema mismatch,
  please close other tabs and reload the page"; lines 228-235 buffer messages that arrive before load —
  [TLLocalSyncClient.ts](https://github.com/tldraw/tldraw/blob/9e700c63f66c040f172dbd7fef936a888ac4b8cc/packages/editor/src/lib/utils/sync/TLLocalSyncClient.ts)
- **tldraw closes on `blocking` (P, high).** `LocalIndexedDb.ts` lines 46-54: "Another tab is deleting (hard
  reset) or upgrading this database. Its request waits until every open connection closes ... Closing here lets it
  proceed; this tab's next write then fails and goes through the write-failure alert-and-reload path" —
  [LocalIndexedDb.ts](https://github.com/tldraw/tldraw/blob/9e700c63f66c040f172dbd7fef936a888ac4b8cc/packages/editor/src/lib/utils/sync/LocalIndexedDb.ts)
- **draw.io closes on `onversionchange`, leaves `onblocked` empty (P, high).** EditorUi.js `openDatabase`:
  `db.onversionchange = function(){ db.close(); }` with a TODO to "Save open file and request a page reload before
  closing the DB"; `req.onblocked` is an empty function with a TODO —
  [EditorUi.js](https://github.com/jgraph/drawio/blob/3e707fd20b6930778d6f6bf6e4d0079b4bce366b/src/main/webapp/js/diagramly/EditorUi.js)
- **localForage closes on `onversionchange` (P, high).** `indexeddb.js` lines 202-210: "Closing the connection
  here prevents those operations from being blocked. If the database is accessed again later ... the connection
  will be reopened" — [indexeddb.js](https://github.com/localForage/localForage/blob/fb78c77ee583fb727a558c439b5174aca38c5924/src/drivers/indexeddb.js)
- **Dexie closes by default on `versionchange`, notes Safari/IE/Edge may not fire it (P, high).**
  `src/classes/dexie/dexie.ts` lines 219-245: default subscriber closes the connection and suggests reloading the
  page when `newVersion > 0`; lines 270-275 are a "Workaround (not fully*) for missing "versionchange" event in
  IE, Edge and Safari" that fires the event on other Dexie instances in the same page; `dexie-open.ts` line 142
  sets `vcFired` "to detect implementations that not support versionchange" —
  [dexie.ts](https://github.com/dexie/Dexie.js/blob/45aade72aa19a601e6a13aa877beb7389e15b5d2/src/classes/dexie/dexie.ts)
- **idb exposes `blocked`, `blocking`, `terminated` callbacks (P, high).** `src/entry.ts` lines 30-110:
  `blocked` (this open waits on another connection), `blocking` (this connection blocks a newer version),
  `terminated` (browser closed the connection abnormally, not called for `db.close()`) —
  [entry.ts](https://github.com/jakearchibald/idb/blob/654c746bef13f9fe7f5871e03ac58015cebace5a/src/entry.ts)

### Inferences
- For an ES5 app the minimum is: `onversionchange` → save what can be saved, `close()`, tell the user to reload;
  `onblocked` → tell the user to close other tabs of the app; a `storage`-event or `BroadcastChannel` signal after
  each committed save so other tabs know their copy is stale. draw.io's empty `onblocked` is the counter-example.
- Two tabs editing the same project is resolved in all apps read by "last write wins plus refresh"; none merges.
  Excalidraw only refreshes on focus, so a background tab's later save can overwrite. (Inference from the code.)

### Gaps
- Web Locks API: not used in any code read; no evidence for or against it from prior art.

## 5. Errors, QuotaExceededError, persist(), and telling the user

### Takeaway
Apps detect quota errors by several names and codes, show a persistent banner or alert, and (tldraw) reload.
No code read calls `navigator.storage.persist()`. Vendors (Figma, Excalidraw maintainers) tell users plainly that
browser storage is not a backup and recommend saving a file.

### Cited Findings
- **Excalidraw's quota detection covers old browser names and codes (P, high).** `LocalData.ts` lines 111-120:
  `QuotaExceededError`, `NS_ERROR_DOM_QUOTA_REACHED` (Firefox), `QUOTA_EXCEEDED_ERR`, `code === 22`,
  `code === 1014`; on failure an atom drives a banner (`App.tsx` lines 1078-1080) whose text is "Browser storage
  quota exceeded. Changes will not be saved." (`packages/excalidraw/locales/en.json` line 299); the banner clears
  on the next successful save (`LocalData.ts` lines 99-101) —
  [LocalData.ts](https://github.com/excalidraw/excalidraw/blob/a758e93d6a03e9f995973703cb886850a398a6d3/excalidraw-app/data/LocalData.ts)
- **Excalidraw wraps every localStorage access in try/catch (P, high).** `excalidraw-app/data/localStorage.ts`
  lines 11-100: each read/write catches "Unable to access window.localStorage"; corrupt JSON falls back to an empty
  scene — [localStorage.ts](https://github.com/excalidraw/excalidraw/blob/a758e93d6a03e9f995973703cb886850a398a6d3/excalidraw-app/data/localStorage.ts)
- **tldraw's user-facing messages (P, high).** `packages/editor/src/lib/utils/sync/alerts.ts` lines 1-22: write
  failure says it "could not save changes to your browser's storage" and will reload, naming private windows and a
  full disk; read failure says the app "won't work correctly without that" —
  [alerts.ts](https://github.com/tldraw/tldraw/blob/9e700c63f66c040f172dbd7fef936a888ac4b8cc/packages/editor/src/lib/utils/sync/alerts.ts)
- **draw.io: a failed draft write deletes the draft (P, high).** `saveDraft`'s catch calls `removeDraft()`
  (DrawioFile.js around line 3170) — [DrawioFile.js](https://github.com/jgraph/drawio/blob/3e707fd20b6930778d6f6bf6e4d0079b4bce366b/src/main/webapp/js/diagramly/DrawioFile.js)
- **`navigator.storage.persist()` not called (P for the files read, medium overall).** None of the files read in
  Excalidraw, tldraw, draw.io or Graphite call `persist()`; Graphite uses `navigator.storage.getDirectory()` only.
  A repository-wide search was not run for each repo, so "never" is not established.
- **Safari's persist() is heuristic (P, high).** WebKit: "WebKit currently grants a request based on heuristics"
  such as being opened as a Home Screen Web App; default mode is best-effort; eviction is per whole origin,
  least-recently-used; "The quota is an upper limit of how much can be stored," so handle `QuotaExceededError`;
  origin quota up to 60% of disk for browser apps, 15% for other apps (Safari 17, 2023-08-10) —
  [WebKit, Updates to Storage Policy](https://webkit.org/blog/14403/updates-to-storage-policy/)
- **Figma tells users what loses offline edits (P, high).** Clearing browsing data, private mode, a different
  browser, a full quota, a blocking extension; 7-day retention in Safari —
  [Figma Learn](https://help.figma.com/hc/en-us/articles/360040328553)

### Inferences
- The app should catch quota errors by name and legacy code like Excalidraw, keep a visible "not saved" state
  until a save succeeds, and never delete the last good copy on a failed write (draw.io's draft deletion is
  acceptable only because the draft is secondary).
- Calling `persist()` is cheap and harmless where denied; it is the only lever against best-effort eviction, but
  no peer relies on it, and on Safari it mostly helps home-screen installs.

### Gaps
- Chrome and Firefox persist() grant rules were not read in their primary documents here (another topic).

## 6. IndexedDB wrapper libraries: design and the edge cases a hand-written ES5 wrapper must handle

### Takeaway
The libraries handle the same short list: cache one connection and drop it on `close`/`versionchange`; resolve
writes on the transaction's `complete`, not the request's `success`; never await anything unrelated inside a
transaction; retry once on `InvalidStateError`/`NotFoundError` by reopening; work around Safari's hanging first
open (Safari 14.6) and missing `versionchange`; detect broken IndexedDB implementations; and (localForage) fall
back to another backend.

### Cited Findings
- **idb-keyval: one cached open promise, reset on close or failure (P, high).** `src/index.ts` lines 12-38:
  `createStore` caches the `indexedDB.open` promise; on success sets `db.onclose = () => (dbp = undefined)` with
  the comment "It seems like Safari sometimes likes to just close the connection"; on failure clears the cache so
  the next call reopens — [idb-keyval index.ts](https://github.com/jakearchibald/idb-keyval/blob/17a69a1165bef486d88950cb47d3913744f038ac/src/index.ts)
- **idb-keyval: writes resolve on transaction complete (P, high).** `promisifyRequest` maps `oncomplete`/`onsuccess`
  to resolve and `onabort`/`onerror` to reject (lines 1-10); `set` returns `promisifyRequest(store.transaction)`,
  so a write resolves only when the transaction commits (around lines 79-82) — same file.
- **idb-keyval: read-modify-write without promise chaining (P, high).** `update()` (around lines 124-140) uses
  raw `onsuccess` callbacks because "If I try to chain promises, the transaction closes in browsers" — same file.
- **idb-keyval 6.3.0 no longer depends on safari-14-idb-fix (P for HEAD, medium for history).** `package.json`
  at HEAD lists no runtime dependencies; whether earlier 6.x versions bundled the fix was seen only in memory (U)
  — [package.json](https://github.com/jakearchibald/idb-keyval/blob/17a69a1165bef486d88950cb47d3913744f038ac/package.json)
- **safari-14-idb-fix: the method (P, high).** `src/index.ts` lines 1-23: on Safari only (UA test, and only if
  `indexedDB.databases` exists), call `indexedDB.databases()` every 100 ms until one resolves, then open normally;
  README: "Safari on macOS Big Sur 11.4 and iOS 14.6 has a nasty bug where IndexedDB requests get lost and never
  resolve. The issue was fixed in Safari 14.7", WebKit bug 226547 —
  [safari-14-idb-fix](https://github.com/jakearchibald/safari-14-idb-fix/blob/2a9084feb17a1226a5aed0fd3f3d3a49c5b3e9eb/src/index.ts)
- **Dexie 4.4.7 still applies that fix (P, high).** `dexie-open.ts` lines 24, 178-188 import `safari-14-idb-fix`
  (dependency `^3.0.0`, package.json line 141) and run it before the first open when the global `indexedDB` is used
  — [dexie-open.ts](https://github.com/dexie/Dexie.js/blob/45aade72aa19a601e6a13aa877beb7389e15b5d2/src/classes/dexie/dexie-open.ts)
- **Dexie's other open workarounds (P, high).** Same file: line 72 `MissingAPI` when `indexedDB.open` returns
  nothing ("May happen in Safari private mode", Dexie issue #134); line 94 treats `oldVersion > 2^62` as 0
  ("Safari 8 fix"); lines 158-166 retry on `UnknownError` a bounded number of times ("Bug in Chrome after clearing
  site data", Dexie issue #543); lines 146-150 handle the `close` event as if `db.close()` was called; `quirks.ts`
  `safariMultiStoreFix` passes a single store name rather than a one-element array (Safari 8) — same repository.
- **idb: transaction lifetime rule (P, high).** README "Transaction lifetime": "Do not `await` other things
  between the start and end of your transaction, otherwise the transaction will close before you're done ... An
  IDB transaction auto-closes if it doesn't have anything left do once microtasks have been processed"; example of
  a `fetch` inside a transaction making the later `put` fail (README lines 171-198) —
  [idb README](https://github.com/jakearchibald/idb/blob/654c746bef13f9fe7f5871e03ac58015cebace5a/README.md)
- **localForage: driver order and validity test (P, high).** `src/localforage.js` lines 18-26: default order
  IndexedDB, WebSQL, localStorage, each driver's `_support` checked before use (lines 226-247);
  `src/utils/isIndexedDBValid.js`: rejects Safari before 10.1 (detected by the absence of native `fetch`,
  following PouchDB issue 5572) and implementations missing `IDBKeyRange` (old Samsung/HTC Android) —
  [isIndexedDBValid.js](https://github.com/localForage/localForage/blob/fb78c77ee583fb727a558c439b5174aca38c5924/src/utils/isIndexedDBValid.js)
- **localForage: Blob support probe and base64 fallback (P, high).** `indexeddb.js` lines 13-90: writes an empty
  Blob into a probe store once and caches the answer ("Blobs are not supported in all versions of IndexedDB,
  notably Chrome <37 and Android <5"); lines 269-295 store unsupported Blobs as
  `{__local_forage_encoded_blob: true, data: base64, type}` — same repository.
- **localForage: reconnect and retry once on a broken connection (P, high).** `indexeddb.js` lines 310-400:
  `createTransaction` retries (default 1) on `InvalidStateError` or `NotFoundError` by reopening (and upgrading
  if a store is missing); readiness is serialised with a deferred promise per database (lines 92-130) so
  operations queue during an upgrade — same repository.
- **localForage: callbacks not promises inside IDB on Firefox (P, medium).** Comment in `indexeddb.js`: "FF
  doesn't like Promises (micro-tasks) and IDDB store operations, so we have to do it with callbacks" — same file;
  the Firefox version affected is not stated.

### Inferences
- For a callback-style ES5 wrapper (no Promises needed; draw.io proves the shape), the checklist from these
  libraries: (1) one cached connection, cleared on `onclose`, `onversionchange` (after `close()`), and open
  failure; (2) resolve writes on `transaction.oncomplete`, reject on `onerror` and `onabort`, and read
  `transaction.error` for the reason (quota errors usually surface as an abort); (3) do every request of a
  read-modify-write inside the same synchronous callback chain; (4) on `InvalidStateError`/`NotFoundError` when
  creating a transaction, reopen and retry once; (5) on open: catch a synchronous throw and a null request
  (private modes), handle `onblocked`, `VersionError`, and a bounded retry of `UnknownError`; (6) treat a first
  open that never answers as possible (Safari 14.6) with a timeout that falls back to localStorage and tells the
  user; (7) cumulative `oldVersion` upgrade steps; (8) keep the localStorage path as the fallback backend, as
  localForage's driver order does.
- WebSQL fallback is obsolete and not needed; Blob-support probing matters only for very old Android/Chrome, below
  the app's likely support floor (to confirm against the app's browser matrix).

### Gaps
- Dexie and idb were read for open/upgrade/lifetime only; their bulk-write and cursor paging code was not read.
- The exact Safari versions without `versionchange` (Dexie comment) were not confirmed in a primary WebKit source.

## 7. Counter-evidence: user-reported data loss and what changed

### Takeaway
Data loss reports are common and are usually caused by the browser (clearing data, profile resets, Safari
eviction or bugs), not the app; maintainers answer that the data cannot be recovered and point users to file save
or a cloud product. Excalidraw has not changed its storage in response to #7870 (no linked change); the browser
side changed (WebKit fixed a wipe bug in Safari 17.4).

### Cited Findings
- **Excalidraw #7870 (P, high).** Opened 2024-04-08: a pinned tab's scene was blank after the Arc browser reset;
  maintainer: "unfortunately, we are unable to recover the scene if the browser suddenly wipes out the data";
  advised saving to a file or Excalidraw+; closed 2024-04-24 with no linked code change —
  [Excalidraw #7870](https://github.com/excalidraw/excalidraw/issues/7870)
- **More Excalidraw reports (U, titles and summaries only).** #8968 "Lost Diagrams" (closed not planned), #9480
  "Lost my file", #9195 "All the pictures on excalidraw disappeared", discussion #6463 "Frustrated about no
  auto-save and backup", #8738 asking for recent-drawings history, #12202 proposing Google Drive sync, #10861
  "Save to file silently drops images not yet fetched from server" —
  [#8968](https://github.com/excalidraw/excalidraw/issues/8968), [#9480](https://github.com/excalidraw/excalidraw/issues/9480),
  [#9195](https://github.com/excalidraw/excalidraw/issues/9195), [#6463](https://github.com/excalidraw/excalidraw/discussions/6463),
  [#8738](https://github.com/excalidraw/excalidraw/issues/8738), [#12202](https://github.com/excalidraw/excalidraw/issues/12202),
  [#10861](https://github.com/excalidraw/excalidraw/issues/10861)
- **Safari wiped localStorage and IndexedDB for all sites (P, high).** WebKit bug 266559 (2023-12-17, Critical,
  RESOLVED FIXED): opening Web Inspector made the network process "delete storage from several origins, which is
  clearly incorrect"; fix committed 2024-01-11 (272951@main); reporter saw no recurrence since Safari 17.4; another
  user reported it unresolved on Safari 17.5 (June 2024) —
  [WebKit 266559](https://bugs.webkit.org/show_bug.cgi?id=266559)
- **Safari's 7-day cap on script-writable storage (P, high).** WebKit (2020-03-24): ITP deletes "all of a
  website's script-writable storage after seven days of Safari use without user interaction on the site", covering
  IndexedDB, LocalStorage, SessionStorage, media keys and service-worker registrations and cache; home-screen web
  apps "have their own counter of days of use" — [WebKit, Full Third-Party Cookie Blocking and More](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/).
  Figma's 7-day Safari retention matches it — [Figma Learn](https://help.figma.com/hc/en-us/articles/360040328553)
- **Other WebKit storage reports (U, not opened).** Bug 200078 (2019, a whole IndexedDB dropped on some iPhones),
  bug 235579, bug 292142 — [200078](https://bugs.webkit.org/show_bug.cgi?id=200078),
  [235579](https://bugs.webkit.org/show_bug.cgi?id=235579), [292142](https://bugs.webkit.org/show_bug.cgi?id=292142)
- **What the projects changed in code (P, high, from the code itself).** tldraw added `pagehide`/hidden flushes,
  close-on-`blocking`, awaiting a closing client's flush, and full-write-after-error (all with comments explaining
  the loss each prevents, section 2/4); Graphite moved documents to OPFS with a backup; draw.io added empty-draft
  removal "so the post-restart prompt doesn't surface drafts that contain nothing to recover". The issues that
  prompted them were not traced (no API access).

### Inferences
- Moving to IndexedDB does not protect against browser-side loss; the 7-day Safari cap and origin-wide eviction
  hit localStorage and IndexedDB equally. The protection is a file the user holds: a prominent "Save to file",
  a reminder when a project has unsaved-to-file changes for some time, and plain wording that browser storage
  is not a backup (Figma and Excalidraw's maintainers both say so).
- Hypothesis "IndexedDB keeps the project safer than localStorage": fails for eviction and clearing (same
  policy); holds for size (quota is a share of disk, not ~5 MB) and for binary data (no base64 inflation).

### Gaps
- tldraw's own issue tracker was not searched directly; no tldraw-specific loss report was found by web search.
- Which Excalidraw or tldraw commits responded to which reports: not traced (GitHub API refused).
- No measurement from here of eviction or quota; that belongs to a separate experiment in `reference/experiments/`.

## Confidence summary

| Finding | Confidence | Reason |
|---|---|---|
| Storage split (scene / blobs / flags) across Excalidraw, tldraw, draw.io | High | Read in three codebases at pinned commits |
| Debounce values 300 / 350 / 1500 ms, 30 s max (draw.io) | High | Constants read in code |
| Flush on hidden + pagehide is needed on mobile | Medium-high | tldraw's comment states it; not measured here |
| draw.io alive-check crash recovery design | High | Read in App.js and DrawioFile.js |
| Close on versionchange is universal practice | High | Four independent codebases |
| Safari 14.6 hanging open, fixed 14.7 | Medium-high | Fix library README and Dexie still shipping it; WebKit bug 226547 itself not opened |
| No peer calls persist() | Medium | Only the storage files were read, not whole repositories |
| Safari 7-day cap and heuristic persist() | High | WebKit's own posts, Figma's doc agrees |
| Excalidraw users lose data to browser wipes, no fix possible app-side | High for #7870, low for the rest | One issue read, others summaries only |
| Photopea / That Open current cache | Low | No primary source read |
