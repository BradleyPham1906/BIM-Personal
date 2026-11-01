# App code audit: how BIM-Personal stores and saves data today (2026-10-31)

Groundwork for moving project saves from localStorage to IndexedDB. Read-only audit of `src/` at
commit 179cc2f, built file `canvas_v10.html` sha256 88f3938b... (matches PIPELINE.md). Every
citation is the app's own code (level P under `reference/research-protocol.md`); paths are relative
to the repository root. Measurements marked "measured" were taken here on 2026-10-31 by driving the
built `canvas_v10.html` from `file://` in headless Chromium 153 (chromium-1243, Playwright 1.63.0)
with scripts kept in the session scratchpad, not in the repository.

## 1. Every persistent-storage use in src/

### Takeaway
Only `localStorage` is used. There is no `sessionStorage`, `indexedDB`, Cache API (`caches.`),
`navigator.storage`, or File System Access API anywhere in `src/` (vendor excluded, and
`src/js/vendor/openskp.js` has none either). Twelve key names or prefixes exist: four carry
project data (`acad3dV1`, `acad3dDocV1:<id>`, `acad3dDocsV1`, `acad3dTemplateV1:<id>`), one carries
the cross-project asset library (`acad3dFamilyLibrary`), the rest are small preferences.

### Cited Findings
Key constants:
- `acad3dV1` (LSK), the project on screen — `src/js/engine/core/state.js:1`
- `acad3dDocsV1` (project list index) and prefix `acad3dDocV1:` (every other project, parked) — `src/js/engine/core/state.js:121`
- `acad3dTemplateV1:` prefix (a template's whole project record) — `src/js/engine/assets/family-library.js:88`
- `acad3dFamilyLibrary` (Assets library: models, blocks, template entries) — `src/js/engine/assets/family-library.js:6`
- `acad3dTheme` — `src/js/engine/core/storage-theme.js:30`
- `acad3dUIPrefs` — `src/js/engine/ui/build-ui.js:10`
- `acad3dToolPal` — `src/js/engine/ui/tool-palette.js:4`
- `acad3dLeftPanel` — `src/js/engine/ui/tool-palette.js:182`
- `acad3dRightPanel` — `src/js/engine/history/branches-merge.js:381`
- `acad3dPropTab` — `src/js/engine/analysis/analyze-tab.js:8`
- `acad3dGraphics` (WebGPU or WebGL preference) — `src/js/engine/render/webgpu.js:11`
- `acad3dCmdUsage` (command palette usage counts) — `src/js/engine/commands/command-catalogue.js:118`
- Legacy keys removed at every start, by exact name: `obsidian-canvas-enhanced-v6`, `-v5`, `acadDrawingsV1`, `acadLayoutsV1`, `acadBlocksV1`, `acadDockV1`, `canvas-grid` — `src/js/engine/core/storage-theme.js:8-25`; `canvas-theme` migrated once into `acad3dTheme` then removed — `src/js/engine/core/storage-theme.js:39-42`

Reads and writes, by key:
- `acad3dV1` read once at engine start, synchronously, inside the closure: `localStorage.getItem(LSK)`, `JSON.parse`, `bimApplyStoredState(st)`, and `st.docId` becomes `A3D_BOOT_DOC` — `src/js/engine/core/state.js:110-119`
- `acad3dV1` written by `save3d()` (`localStorage.setItem(LSK,JSON.stringify(rec))`) — `src/js/engine/core/objects-save.js:48-61`
- `save3d` is scheduled by `saveSoon()`, a 300 ms trailing debounce (`saveT=setTimeout(save3d,300)`) — `src/js/engine/bim/region-regenerate.js:74-86`; `saveSoon()` is called 246 times across 90 files (grep count), i.e. after every model edit
- `pagehide` flushes a pending debounce synchronously (`if(saveT){clearTimeout(saveT);saveT=null;save3d();}`) — `src/js/engine/ui/project-tabs.js:101-106`; the comment records the measured loss it fixes: "a wall drawn just before a reload, gone 8 times in 8" — `src/js/engine/ui/project-tabs.js:101-103`
- Closing the last tab saves directly — `src/js/engine/assets/templates.js:87-88`
- `acad3dDocsV1` read and rebuilt at start by `bimDocsBoot()` (called from `src/js/engine/core/state.js:122`), which also enumerates every `acad3dDocV1:` key with `localStorage.key(i)` — `src/js/engine/ui/project-tabs.js:41-100`; written by `bimDocsSave()` after every tab activate/add/close/remove — `src/js/engine/ui/project-tabs.js:107-114`
- `acad3dDocV1:<id>` written when a project is parked during a switch, removed when it is opened or deleted — `src/js/engine/ui/project-tabs.js:159,163,181,190,212`, `src/js/engine/assets/templates.js:101`
- `acad3dTemplateV1:<id>` written by Save as Template, read by Use Template, removed with its library entry — `src/js/engine/assets/templates.js:7,27`, `src/js/engine/assets/family-library.js:68`
- `acad3dFamilyLibrary` read once at start into `A3D_FAMLIB` (`src/js/engine/assets/family-library.js:8,37-43`), rewritten whole by `bimSaveFamilyLibrary()` on every add/remove (`src/js/engine/assets/family-library.js:44-46,58,74`), on template save (`src/js/engine/assets/templates.js:20`) and on SketchUp block import (`src/js/engine/io/sketchup-import.js:295`)
- `acad3dTheme` written when the Appearance menu changes, read at start — `src/js/engine/core/storage-theme.js:31-48`
- `acad3dUIPrefs` read/written — `src/js/engine/ui/build-ui.js:11-20`
- `acad3dToolPal`, `acad3dLeftPanel` read/written — `src/js/engine/ui/tool-palette.js:25-26,183-184`
- `acad3dRightPanel` — `src/js/engine/history/branches-merge.js:382-383`
- `acad3dPropTab` read at start, written on tab change — `src/js/engine/analysis/analyze-tab.js:10,32,45`
- `acad3dGraphics` — `src/js/engine/render/webgpu.js:205,472`
- `acad3dCmdUsage` read and rewritten on every command run (`bimCmdUsed`) — `src/js/engine/commands/command-catalogue.js:196-206`; cleared by a test hook — `src/js/engine/testing/hooks-commands-site.js:13`
- No storage use in `src/js/shell/` or `src/index.html` (grep returned nothing).

Measured key sizes (characters, key plus value): fresh project `acad3dV1` 28,280; `acad3dDocsV1` 261; a parked empty project 28,253; `acad3dFamilyLibrary` after importing `tests/skp/site_kit.skp` 14,378.

### Inferences
- An empty project is already about 28 K characters, so most of a small record is defaults (types, levels, layers, site), not geometry.
- The preference keys are tiny and read synchronously at start for layout; they are good candidates to stay in localStorage.

### Gaps
- Not measured: the size of the preference keys individually, or `acad3dCmdUsage` after long use.

## 2. The project save format

### Takeaway
There are three serialisations of nearly the same field list: the autosave record
(`bimProjectRecord`, no version field), the undo snapshot (`bimSnapshotState`), and the file
envelope (`bimBuildProjectEnvelope`, `formatVersion:1`). All are plain `JSON.stringify` of the live
`A3D` object graph. Geometry is inline JSON arrays of numbers; images are inline data URIs; map
tiles and derived meshes are not saved. There is no explicit migration code: old records are
upgraded by tolerant field-by-field validation on load.

### Cited Findings
- The autosave record: `{objs, cam, seq, counts, levels, grids, activeLevel, layers, activeLayer, types, activeWallType, views, activeViewId, levelFilter, sheets, titleBlock, buildings, activeBuilding, site, roomScheme, classifications, dataFeatures, history, resultLayers, pres}` — `src/js/engine/core/objects-save.js:42-44`; `save3d` adds `docId` — `src/js/engine/core/objects-save.js:50`
- The comment says this is "the one list of what a project is", used to park projects and to define a fresh project — `src/js/engine/core/objects-save.js:39-41`; `A3D_PROJECT_DEFAULTS=JSON.stringify(bimProjectRecord())` at start — `src/js/engine/core/state.js:44`
- File envelope: `{app:'acad3d-project', formatVersion:1, savedAt, data:{...}}`; its `data` omits `cam` and `seq` and has no `docId` — `src/js/engine/io/project-file.js:5-8`
- Envelope parse rejects non-JSON and foreign files; a `formatVersion>1` only adds a warning, no migration — `src/js/engine/io/project-file.js:9-17`
- Undo snapshot is a third list (no `cam`, `seq`, `dataFeatures`, `history`, `activeViewId`) — `src/js/engine/drawing/plan-mode-sketch.js:250-253`; up to `UNDO_MAX=50` full JSON strings held in memory, not persisted — `src/js/engine/drawing/plan-mode-sketch.js:250,257-260`
- Load path: `bimApplyStoredState` validates each field and falls back with `console.warn` on damage (levels, grids, layers, sheets, buildings, classifications), drops orphan data-layer features, validates history/result layers/presentation, then `bimAdoptLayers()` gives old layerless objects a layer — `src/js/engine/core/state.js:46-108`
- Opening a project resets every field to defaults first, then applies the record through the same validation — `src/js/engine/ui/project-tabs.js:125-142`
- Element history (V146) travels inside the record as `history:{v:1, head, commits:[{id,parent,msg,at,by,tree:[[key,hash]...],stats,branch}], blobs:{hash: canonicalJSONString}, branches, branch}` — `src/js/engine/history/element-history.js:1-6,48-59,150-161`; each blob is a JSON string stored as a string value, so it is escaped a second time inside the record — `src/js/engine/history/element-history.js:33-38`; commits are user-initiated (and merges), not automatic — `src/js/engine/history/element-history.js:150`, `src/js/engine/history/branches-merge.js:159,344`
- Imported meshes (OBJ, STL, SketchUp, IFC) are `mesh:{v:[[x,y,z],...], f:[[i,j,k],...]}` inline on the object; STL parsing builds exactly that shape — `src/js/engine/io/import-obj-stl.js:82-95`; SketchUp parts become `t:'solid'` objects with `mesh:q.mesh` — `src/js/engine/io/sketchup-import.js:260-263`
- SketchUp limits "so the library stays within browser storage": `BIM_SKP={maxTris:250000, blockTris:6000, blockChars:1500000}` — `src/js/engine/io/sketchup-import.js:20`; block character budget enforced — `src/js/engine/io/sketchup-import.js:286-288`; recorded in the log — `canvas_v10_STATUS.md:14145-14146`
- Terrain objects store their survey points (`survey:keep`, plus `source`), not their triangles — `src/js/engine/survey/survey-check.js:211-212`; the TIN is a derived cache, "The cache is not saved" — `src/js/engine/terrain/terrain-tin.js:61-62`
- OpenStreetMap surroundings are placed as ordinary objects in `A3D.objs` — `src/js/engine/map/surroundings-3d.js:241`; trees capped at `BIM_CTX_TREES_MAX=3000` — `src/js/engine/map/surroundings-3d.js:13`
- Map tiles live in an in-memory cache only (`A3D_MAP={cache:{},...}`, `BIM_MAP_CACHE=400`); only the map settings are saved under `A3D.site.map` — `src/js/engine/map/map-tiles.js:18-25`
- Data-layer features are saved as `dataFeatures[layerId]` — `src/js/engine/map/data-layers.js:104`, `src/js/engine/core/state.js:93-95`
- Image notes are read with `readAsDataURL` and stored as `{src:<data URI>}` inside the object, "so the drawing stays self-contained"; the file limit is 4 MB — `src/js/engine/annotation/annotation-overlay.js:207-229`
- Result-layer images are rebuilt into `A3D_RES_IMG`, an in-memory cache reset on load — `src/js/engine/analysis/results-layers.js:7,175-178`, `src/js/engine/core/state.js:100`
- Asset thumbnails are PNG data URIs from a canvas (`toDataURL`) stored on the library entry — `src/js/engine/assets/scale-assets.js:359-401`, `src/js/engine/assets/family-library.js:56`, `src/js/engine/io/sketchup-import.js:284`
- Measured sizes of `acad3dV1` (characters): empty project 28,280; with 40 walls 46,051; plus `site_kit.skp` (11 objects) 53,423; plus an OBJ of 20,000 triangles 528,922; plus an OBJ of 125,000 triangles 3,908,935 (about 31 characters per imported triangle).
- No recorded project sizes or quota incidents were found in `canvas_v10_STATUS.md` (grep for quota, QuotaExceeded, storage full, 5 MB, IndexedDB returned only the line about the five persistence points, `canvas_v10_STATUS.md:303`, and the SketchUp limits).

### Inferences
- A single 4 MB image note becomes about 5.6 M characters of base64, which on its own exceeds the measured localStorage quota (section 6); such a project cannot autosave today.
- A heavy imported model with history commits is stored twice (once in `objs`, once escaped in `history.blobs`), so committing roughly doubles the record.
- Because the envelope lacks `cam`/`seq` and the record lacks a version, a migration should add a version field to the stored record and keep reading unversioned ones.

### Gaps
- History-heavy and image-heavy projects were not measured.
- IFC import sizes were not measured (no IFC fixture was run).

## 3. Project tabs and multiple projects

### Takeaway
Many projects share one origin's localStorage: the one on screen in `acad3dV1`, every other parked
in `acad3dDocV1:<id>`, and an index in `acad3dDocsV1` that is a rebuildable cache. There is no
count limit in code; the limit is the storage quota.

### Cited Findings
- Design and crash-safety ordering: park current, write next into `acad3dV1`, only then remove the next one's own copy, so "each project is stored in at least one place"; boot re-derives the list from keys — `src/js/engine/ui/project-tabs.js:1-8`
- Index shape `{v:1, active, open:[ids], docs:[{id,name,objs,saved}]}` — `src/js/engine/ui/project-tabs.js:45,56,96`
- Boot repairs: stale parked copy of the active project removed; stored projects missing from the list re-listed; list entries with nothing stored dropped — `src/js/engine/ui/project-tabs.js:58-84`
- Switch sequence and its rollback on failure — `src/js/engine/ui/project-tabs.js:143-206`
- Undo stacks and view per project live only in memory (`A3D_DOC_RT`) — `src/js/engine/ui/project-tabs.js:169-174,195`, `src/js/engine/core/state.js:123`
- Ids: `'doc-'+Date.now().toString(36)+'-'+random` — `src/js/engine/ui/project-tabs.js:17-19`
- Delete refuses an open or active project — `src/js/engine/assets/templates.js:96-108`
- Templates are separate whole-project records under `acad3dTemplateV1:` plus an entry in the library — `src/js/engine/assets/templates.js:1-22`
- Measured: with a 3.9 M-character project on screen, New project failed with the toast "There is not enough browser storage to switch projects..." (from `src/js/engine/ui/project-tabs.js:158`) because parking needs a second copy while `acad3dV1` still holds the first.

### Inferences
- Under localStorage a project larger than about half the quota can never be switched away from; the switch protocol's "briefly in two places" is the binding constraint, and an IndexedDB store (one record per project, written in one transaction) removes it.

### Gaps
- None in code; behaviour across browsers was not tested.

## 4. File export and import already present

### Takeaway
Save writes `<project name>.acad3d.json` through a Blob and an `<a download>` link; Open reads
`.json` files through a hidden `<input type="file" accept=".json">` (no `multiple` attribute; the handler loops over whatever files arrive) and FileReader,
each into a new tab. There is no OS drag-and-drop and no File System Access API.

### Cited Findings
- Export: `bimExportProjectFile` builds the envelope and calls `bimTriggerDownload(json, stem+'.acad3d.json','application/json')`, toasting on success and failure — `src/js/engine/io/project-file.js:25-31`; the download helper uses `Blob`, `URL.createObjectURL`, a clicked `<a download>`, revoke after 1 s — `src/js/engine/annotation/annotation-pick.js:181-190`
- File name from the project name, unsafe characters replaced, 80 characters — `src/js/engine/io/project-file.js:21-24`
- Entry points for Save: dock menu `m:saveproj` — `src/js/engine/ui/dock-tooltips.js:213`; keyboard handler — `src/js/engine/ui/touch-input.js:217`; command `saveJson` — `src/js/engine/commands/command-map.js:168`
- Open: hidden input `#a3d-projin accept=".json"` — `src/js/engine/ui/build-ui.js:52`; its change handler opens each chosen file — `src/js/engine/ui/build-ui.js:197-203`; picker — `src/js/engine/io/project-file.js:63-72`; reader refuses non-.json, reads text with FileReader, toasts on error — `src/js/engine/io/project-file.js:48-62`; opens in a new tab named from the file when the title block is empty — `src/js/engine/io/project-file.js:36-47`, `src/js/engine/assets/templates.js:66-74`
- The Import path also routes `.json` (not `.city.json`) to the project reader — `src/js/engine/io/import-entry.js:28-31`
- The only `drop` listeners are internal reordering of data-layer rows and presentation pages — `src/js/engine/layers/analysis-data-rows.js:289-298`, `src/js/engine/sheets/presentation-panel.js:211-223`; no `dataTransfer.files` anywhere.
- No `showSaveFilePicker`/`showOpenFilePicker` in `src/` (grep).
- The autosave failure toast already points users to the file: "Use Save to keep a copy as a file." — `src/js/engine/core/objects-save.js:58`

### Inferences
- The file envelope is the natural export/backup and migration-escape format; it already round-trips through `bimDocsAdd`.

### Gaps
- None.

## 5. Error handling

### Takeaway
Project writes are wrapped and toasted (once per run of failures for autosave). Switching rolls
back on a full store. QuotaExceededError is not distinguished by name: any `setItem` exception is
treated as "storage is full". Library and preference writes fail silently or to the console only.

### Cited Findings
- Autosave: try/catch, one `console.warn` plus toast per failure run, and a "works again" toast on recovery, via `A3D_SAVE_FAILED` — `src/js/engine/core/objects-save.js:45-61`
- Switch: park failure aborts with toast; active-slot failure removes the parked copy and aborts; load failure restores `acad3dV1` and the previous project, toasts "stored data is damaged" — `src/js/engine/ui/project-tabs.js:158-188`
- Index save failure toasts "The list of projects could not be saved: browser storage is full" — `src/js/engine/ui/project-tabs.js:107-114`
- Template save failure toasts and adds no library entry ("a full store adds nothing") — `src/js/engine/assets/templates.js:1-12`
- Family library save failure: `console.warn` only, no toast — `src/js/engine/assets/family-library.js:44-46` (the build contract requires `console.warn` plus `a3dToast`, `CLAUDE_INSTRUCTIONS.md:54`)
- Preference writes swallow errors with empty catches — `src/js/engine/ui/build-ui.js:16,19`, `src/js/engine/ui/tool-palette.js:25-26,183-184`, `src/js/engine/history/branches-merge.js:382-383`, `src/js/engine/analysis/analyze-tab.js:32,45`, `src/js/engine/render/webgpu.js:205,472`; command usage warns only — `src/js/engine/commands/command-catalogue.js:204-205`; theme warns and toasts — `src/js/engine/core/storage-theme.js:31-34`
- Boot read failure of `acad3dV1` warns and starts from defaults, with no toast — `src/js/engine/core/state.js:117-119`
- No code references `QuotaExceededError` (grep); the suites simulate it by replacing `Storage.prototype.setItem` — `tests/bim_phase115_project_tabs_browser_tests.py:358-375`

### Inferences
- An SKP import that adds blocks to a full library loses them on reload without telling the user.

### Gaps
- None.

## 6. Main-thread work during save, size, compression

### Takeaway
Everything is synchronous on the main thread: `JSON.stringify` of the whole project, then
`localStorage.setItem` of the whole string, every 300 ms after an edit and at `pagehide`. No
compression, no workers, no incremental or per-object writes.

### Cited Findings
- `save3d` serialises the full record each time — `src/js/engine/core/objects-save.js:48-52`; `saveSoon` also runs sweeps and region regeneration synchronously before scheduling — `src/js/engine/bim/region-regenerate.js:74-86`
- No `Worker`, `CompressionStream`, pako or LZString in `src/` (grep).
- The family library is rewritten whole on every change — `src/js/engine/assets/family-library.js:44-46`
- Measured, 3.9 M-character project: envelope `JSON.stringify` 28-31 ms, `localStorage.setItem` of the same string 11 ms, `JSON.parse` 14.5 ms; 20,000-triangle project: stringify 4-5 ms.
- Measured localStorage quota on `file://` in this Chromium: 19 chunks of 262,144 characters on top of 28,437 used, then `QuotaExceededError`, i.e. about 5.0 M characters for keys and values together.
- Measured: a `file://` page in the same Chromium opened IndexedDB, wrote one 8 M-character string in a readwrite transaction, and `navigator.storage.estimate()` reported a quota of 3,221,225,472 bytes.
- A `file://` page shares its storage with every other page opened from disk — `src/js/engine/core/storage-theme.js:5-7`

### Inferences
- At the quota the save cost is about 40-50 ms of main-thread time per autosave, which is noticeable but not the binding problem; the quota is.
- IndexedDB's async write cannot complete inside a synchronous `pagehide` handler with certainty; the pagehide flush (`src/js/engine/ui/project-tabs.js:104-106`) needs a design (for example a localStorage journal of the last unsaved state, or writing on every debounce and on `visibilitychange`).

### Gaps
- IndexedDB on `file://` in Firefox and Safari was not tested here (only Chromium is installed).
- Whether IndexedDB structured clone of the live `A3D` graph (instead of a JSON string) is faster was not measured.

## 7. Tests covering save, load and storage

### Takeaway
23 of 157 files in `tests/` reference localStorage; V115's suite is the storage contract
(48 checks), with V121b and V124 also central. Suites run against the built `canvas_v10.html`
via `tests/run_all.py`, and each is falsified by `tests/falsify_all.py`.

### Cited Findings
- Files referencing localStorage (count of mentions): `bim_phase115_project_tabs` 15, `bim_phase121b_old_canvas_storage` 8, `bim_phase124_assets_library` 6, `bim_phase126_section_profiles` 4, `ui_responsive_audit` 3, `bim_phase117_wire_shell_retired` 3, `bim_phase114_stylesheet_start` 3, `bim_phase167_standards_registry` 2, `bim_phase166d_properties_width` 2, `bim_phase166b_panels` 2, and one each in `ui_overlap_probe`, `ui_interactive_test`, `bim_phase83`, `bim_phase55d`, `bim_phase55c`, `bim_phase46_48`, `bim_phase42`, `bim_phase163_sketchup_import`, `bim_phase153_webgpu_engine`, `bim_phase141`, `bim_phase135`, `bim_phase122`, `bim_phase116` (grep -c over `tests/`)
- V115 asserts: legacy single-record store boots into one tab; every project in exactly one place after each switch; full store during switch and failed autosave toast and leave the project whole; boot repairs crash leftovers — `tests/bim_phase115_project_tabs_browser_tests.py:1-26`; it reads and writes keys directly — `tests/bim_phase115_project_tabs_browser_tests.py:141-182,345-355,428-459`
- File:// storage harness hazard: an init script that touches localStorage cuts the page's storage off in about half of runs; suites seed storage from a blank page on the same origin instead — `tests/bim_phase115_project_tabs_browser_tests.py:74-79`, `canvas_v10_STATUS.md:9044-9052,9884`
- Suites using the envelope hooks: V51, V53, V73, V82, V115, V121, V148, V151, V162, V164 and `test_3d5.js` (grep for `__a3dProjectEnvelope|__a3dImportProject|__a3dExportProject`)
- Test hooks: `__a3dExportProject`, `__a3dProjectEnvelope`, `__a3dImportProject`, `__a3dParseProjectEnvelope` — `src/js/engine/testing/hooks-drawing.js:297-300`; `__a3dDocs` (list, open, active, activate, create, close, remove, undoDepth) — `src/js/engine/testing/hooks-layers-sheets.js:165-180`; `__a3dTemplateSave/Use` — `src/js/engine/testing/hooks-assets-structure.js:16-17`; `__a3dFamilyAdd/Get/Remove`, `__a3dLoadUIPanelPrefs` — `src/js/engine/testing/hooks-drawing.js:277-282`; `__a3dHistCommit` — `src/js/engine/testing/hooks-assets-structure.js:104`; `__a3dCommandUsageClear` — `src/js/engine/testing/hooks-commands-site.js:13`
- How they run: `tests/run_all.py [build] [filter] [-jN]`, default -j6, about 4 minutes; `tests/falsify_all.py <falsify_phaseNN.py> <suite.py>`; currently 133 suites, 6786 checks — `PIPELINE.md:19-38`; test protocol (falsify every suite, assert on the model) — `CLAUDE_INSTRUCTIONS.md:103-115`

### Inferences
- Six suites address `acad3dV1` by name and V115 manipulates `Storage.prototype.setItem`; a migration must either keep these keys meaningful (for example as a legacy source read once) or amend those suites, and falsify the amendments.
- Waits like `wait_for_timeout(600)` after an edit assume the 300 ms synchronous debounce; an async store will need a "saved" signal hook for suites.

### Gaps
- Each suite's exact storage assertions outside V115 were not read line by line.

## 8. Settings that could stay in localStorage

### Takeaway
Theme, panel layout, tool palette, property tab, graphics engine and command usage are small,
per-browser, read synchronously before first paint; they fit localStorage. The family library is
not a setting: it holds meshes and SketchUp blocks up to 1.5 M characters and belongs with the
project store.

### Cited Findings
- Theme restored at start and applied to `document.body` — `src/js/engine/core/storage-theme.js:35-48`
- Property tab read at variable initialisation — `src/js/engine/analysis/analyze-tab.js:10`
- Graphics preference read when choosing the renderer — `src/js/engine/render/webgpu.js:205`
- Family library holds model meshes (`mesh:bimNormalizeMeshForFamily(...)`) and block records with meshes — `src/js/engine/assets/family-library.js:47-60`, `src/js/engine/io/sketchup-import.js:275-283`

### Inferences
- Moving `acad3dFamilyLibrary` and `acad3dTemplateV1:*` with the projects avoids a second quota wall.

### Gaps
- None.

## 9. Constraints for a migration

### Takeaway
ES5 syntax, but Promises are already used (15 engine files, 45 mentions, all with
`.then(function(){...})`, no `async`/`await` or arrows), so a Promise-wrapped IndexedDB adapter
fits the house style. The hard constraints are the synchronous boot inside one closure and the
synchronous pagehide flush.

### Cited Findings
- Build contract: one file, zero dependencies, runs from `file://`; ES5 `var`/`function`; every new path `console.warn('[BIM] ...')` plus `a3dToast`; "Never a half-written localStorage record"; "Existing localStorage keys (`acad3dV1` and relatives) must survive every change"; every new block carries `__acad3dVNN` — `CLAUDE_INSTRUCTIONS.md:49-56`
- Promise use, e.g. `fetch(url).then(function(r){...})` and `Promise.all([...]).then(...)` — `src/js/engine/site-analysis/climate-data.js:41-45,244`, `src/js/engine/site-analysis/land-water.js:47-79`, `src/js/engine/site-analysis/analyze-site.js:54-143`
- The engine is one closure joined from `src/` in `src/index.html` order (`CLAUDE.md`, "The engine is one closure"); `state.js` is included at line 41 and `storage-theme.js` at 42, `objects-save.js` at 175, `project-tabs.js` at 176, `templates.js` at 177, `family-library.js` at 187 — `src/index.html:41-42,175-177,187`
- The stored project is applied synchronously while the closure is still executing (`src/js/engine/core/state.js:110-119`), before UI build; `A3D_DOCS=bimDocsBoot()` likewise — `src/js/engine/core/state.js:122`; `A3D_FAMLIB` is loaded at variable initialisation — `src/js/engine/assets/family-library.js:8`
- The pagehide flush is synchronous — `src/js/engine/ui/project-tabs.js:104-106`
- `file://` shares one storage origin across every local page — `src/js/engine/core/storage-theme.js:5-7`; the Pages build serves `index.html` plus split files and `canvas_v10.html` for offline `file://` use (`CLAUDE.md`, "Pages")

### Inferences
- Boot must become two-stage: build with defaults (or with a synchronous localStorage copy if present), then apply the IndexedDB record when it arrives, or delay UI build until the open resolves; every consumer of `A3D_BOOT_DOC`, `A3D_DOCS` and `A3D_FAMLIB` at initialisation must tolerate that.
- The Pages site (https origin) and the `file://` copy have different origins, so their stores are separate today and will stay so.

### Gaps
- IndexedDB availability in Firefox and Safari on `file://`, and in private windows, was not tested here; it needs primary browser documentation and a run in each browser.

## Search log

1. `grep -rn -E "localStorage|sessionStorage|indexedDB|IDBDatabase|caches\.|navigator\.storage|QuotaExceeded|showSaveFilePicker|showOpenFilePicker" src/` (vendor excluded)
2. `grep -rn -E "getItem\(|setItem\(|\.storage\b|Storage\b" src/` (non-localStorage callers: none)
3. `grep -rn -E "(LSK|A3D_DOC_PREFIX|...|BIM_[A-Z_]*KEY)\s*=" src/` for key constants
4. Read `core/state.js`, `core/storage-theme.js`, `core/objects-save.js`, `ui/project-tabs.js`, `assets/templates.js`, `io/project-file.js`, `assets/family-library.js` (1-90)
5. `grep saveSoon()` (246 calls, 90 files), `save3d()`, `bimSnapshotState`, `bimBuildProjectEnvelope`
6. Import paths: `io/import-entry.js`, `import-obj-stl.js`, `sketchup-import.js` (20, 255-300), `dataTransfer`, `drop`
7. Images and caches: `readAsDataURL|toDataURL`, `A3D_RES_IMG`, `map-tiles.js`, `terrain-tin.js`, `survey-check.js`, `surroundings-3d.js`
8. `grep Promise|\.then\(|async |await |=>`; `Worker|CompressionStream|pako|LZString`
9. History: `element-history.js` 1-60, 150-175
10. Tests: `grep -rl localStorage tests/`, per-file counts, V115 suite header and quota checks; envelope-hook users; testing hooks grep
11. `PIPELINE.md` head; `CLAUDE_INSTRUCTIONS.md` build contract and test protocol
12. `canvas_v10_STATUS.md` grep for quota, storage full, 5 MB, IndexedDB, init script
13. Measurements in headless Chromium from `file://` (sizes, timings, quota, IndexedDB probe); scripts in the session scratchpad only
