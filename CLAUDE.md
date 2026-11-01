# BIM-Personal: start here

A zero-dependency browser CAD/BIM app, built phase by phase (V1 to V170 so far), each phase verified
by its own browser suite, deliberately broken builds its suite must catch, and the full regression.
Its source is `src/`, split by feature; `tools/build_app.py` joins it into `canvas_v10.html`, the
one-file build every suite tests, and Pages serves it as separate files (see "The source" below).

## In a new session

1. Read `PIPELINE.md` first, in full: the build's hash and size, the test counts, and the ordered
   path, with the phase marked **Start here**.
2. Then `CLAUDE_INSTRUCTIONS.md`: the build contract (ES5, no dependencies, phase markers,
   failures warned and toasted), the patch protocol (anchored Python scripts asserting exact counts
   and the base hash), the test protocol and the standing laws. Its paths under `claude/` and on a
   Mac are from an older setup: the files are at the repository's root, `Phase/`, `tests/` and
   `reference/`. Where it says the app is edited as one file, "The source" below replaces it.
3. The current work plan is `reference/plan-v167-v170.md`; each phase's research note is in
   `reference/`; the engineering log is `canvas_v10_STATUS.md` (search it, never read it whole).

## Rule #1: do not test unless the table says so (the owner, 2026-11-01)

This overrides every other testing rule in this repository: `CLAUDE_INSTRUCTIONS.md` section 4,
"Never idle on long checks" below, and any phase plan. The default after an edit: make the change,
say what changed, stop. No tests, browser, screenshots, falsification or regression unless the table
calls for it or the owner asks.

| Change | What to run |
|---|---|
| Text, style, markup, comments, or a few lines of JS | Nothing. |
| JS logic in one file | Syntax check of that file only. |
| Shared state, the order in `src/index.html`, or 3+ files | Syntax check of the changed files, then the build. Then ask the owner whether to run a browser check. |
| The owner says "full regression" | Full regression. This is the only trigger. |

If a bigger check seems needed, ask in one sentence; don't run it.

- **Syntax check** (cheap): `node --check src/js/<path>.js` (every file but `_begin.js`/`_end.js`,
  which only open and close the engine's closure).
- **Build** (cheap): `python3 tools/build_app.py`, which proves `src/` still joins into
  `canvas_v10.html`. A change under `src/` is not done until `canvas_v10.html` is rebuilt and committed:
  the Pages workflow runs `--check` and fails otherwise.
- **Browser check** (expensive, only when the owner approves): load the build, report console errors only.
- **Full regression / a phase's suite and falsification** (only when the owner asks): `tests/` and the
  test protocol in `CLAUDE_INSTRUCTIONS.md` section 4, which says how, not when.
- When a check fails, show only the failing lines. Stop after 2 failed fix attempts and say what is wrong.
- If a hook, script or instruction makes tests run automatically, tell the owner instead of following it.
  (2026-11-01: there is no `.claude/settings.json` and no git hook; CI runs only the build checks.)

## How to work in this repo (the owner, 2026-11-01)

- Read the module map below first. Open only the files the task touches; find code with
  `grep -rn 'name' src/`, then read that file or its range.
- Don't read the whole codebase to "understand the app". Ask before reading files outside the task.
- Edit with small targeted changes. Never rewrite a whole file for a small change.
- Keep files under about 400 lines. If one grows past that, suggest a split; don't do it unasked.
  (Already over, 2026-11-01: `vendor/openskp.js` 3239, third-party; `engine/gizmo/gizmo-handles.js` 1280;
  `engine/standards/registry.js` 1024; `engine/ui/build-ui.js` 993; `engine/site-analysis/zoning-envelope.js` 970.)

## Module map

<!-- Claude: keep this current. One line per folder: path, what it owns. Every file, in order, with
its first line: tools/app_layout.py. -->

    src/index.html                      the page; the order every css/js file is joined in
    src/css/shell/                      top bar, command palette, left shell, page base
    src/css/panels/                     layers, presentation, properties and Analyze panels
    src/css/workspace/                  components, engine chrome, responsive (phone/tablet)
    src/css/sheets/                     layouts, pages, present mode
    src/css/site-analysis/              Analyze workspace and its boards
    src/js/shell/shell.js               top bar, command palette, project tabs, boot
    src/js/vendor/openskp.js            SketchUp reader (third-party, never edited by hand)
    src/js/engine/_begin.js, _end.js    open and close the engine's one closure
    src/js/engine/core/                 state, IndexedDB store, storage/theme, mesh primitives, save
    src/js/engine/render/               WebGL/WebGPU, GPU batches and picking, view cube
    src/js/engine/drawing/              drawing tools: lines, arcs, curves, construction lines, endings
    src/js/engine/editing/              selection, push/pull, offset/align/trim, precision, modify toolbox
    src/js/engine/gizmo/                transform gizmo and its handles
    src/js/engine/bim/                  BIM elements: walls, columns, openings, slabs, footings, grids, CSG, site hierarchy
    src/js/engine/structure/            analytical model, frame solve, tributary loads, results display
    src/js/engine/annotation/           dimensions, annotation overlay, picking, grips
    src/js/engine/layers/               layer manager, rules, panel, plot-by-layer
    src/js/engine/properties/           properties palette, usages, site data and standards fields
    src/js/engine/views/                saved views, sections, schedules
    src/js/engine/sheets/               sheets, layouts, pages, presentation, editable boards
    src/js/engine/assets/               library, families, blocks, templates, drag-in
    src/js/engine/io/                   project file; import DXF/IFC/OBJ/STL/SketchUp; DXF export
    src/js/engine/map/                  map tiles, open-data layers, CityJSON, LOD solids and roofs
    src/js/engine/terrain/              terrain TIN, breaklines, grading
    src/js/engine/survey/               survey arithmetic and checks
    src/js/engine/site/                 property, alignment/profile, sun position, shadows
    src/js/engine/site-analysis/        Analyze workspace, site boards (climate, access, land use, zoning), sun path
    src/js/engine/site-tools/           V172 site tools: grid, capacity, suitability, panel
    src/js/engine/simulation/           traffic network, demand, signals, sim, walkers, UI
    src/js/engine/ladybug/              Pyodide runtime, weather sources, analyses, figures, panel, Python adapter
    src/js/engine/analysis/             Analyze tab, result layers, simulation glue
    src/js/engine/standards/registry.js industry standards as data, with editions (V167)
    src/js/engine/history/              element history, branches and merge
    src/js/engine/ui/                   UI build, chrome, tabs, docks/tooltips, project browser, guide
    src/js/engine/commands/             command catalogue and map
    src/js/engine/testing/              window.__a3d* hooks the suites drive
    src/py/bim_ladybug.py               Ladybug adapter (Python), embedded by tools/embed_py.py

## The source: src/, by feature (the owner, 2026-10-25)

"having a one html with all the code cost me so many token and i want the app structure to be like a
profesisonal app where there are multi folders and files." The app is edited in `src/`; never edit
`canvas_v10.html` by hand, and never read it whole: it is a build output, committed because every
suite, every falsification script, `Phase/`'s backups and the guide's tools read it.

    src/index.html            the page: its head and body, and for each block the files it is made of,
                              in order (<!-- @bundle -->, <!-- @include -->, <!-- @end -->)
    src/css/                  the stylesheet, 13 files: shell/, panels/, workspace/, sheets/, site-analysis/
    src/js/shell/shell.js     the top bar, the command palette, the project tabs, the boot
    src/js/vendor/openskp.js  the SketchUp reader (third-party, bundled; never edited by hand)
    src/js/engine/            the BIM engine, 196 files in 28 folders: core/ (state, storage, meshes,
                              save), drawing/, editing/, gizmo/, bim/, structure/, annotation/,
                              layers/, properties/, views/, sheets/ (with V172b's editable boards),
                              assets/, io/, render/, map/, terrain/, survey/, site/, site-analysis/
                              (with Analyze's workspace, V171b and V171c, and V171d's sun path and
                              its panel), simulation/ (V171's traffic and people), site-tools/
                              (V172's), ladybug/ (V172b's: the runtime, the weather, the analyses,
                              the figures, the panel), standards/, analysis/, history/, ui/,
                              commands/, testing/ (the window.__a3d* surface the suites drive);
                              _begin.js and _end.js open and close it
    src/py/bim_ladybug.py     the app's adapter to Ladybug's Python (ours): tools/embed_py.py writes it
                              into js/engine/ladybug/adapter-py.js, which a patch runs before the build
    runtime/                  Pyodide 0.29.5 and Ladybug's four wheels, committed and pinned by size and
                              SHA-256 in MANIFEST.json (tools/check_runtime.py): V172b's one written
                              exception to "no dependencies", loaded only when a Ladybug analysis runs

- **The engine is one closure.** `_begin.js` opens `(function(){ try{`, `_end.js` closes it, and every
  file between is a slice of that one function: they share its private variables and are joined into
  one script, in the order `src/index.html` lists them. A file is never loaded on its own, and a
  function a file uses may be defined in another. Each file is a whole list of statements: cut only
  between top-level statements (`new Function(text)` parses every file but `_begin.js`/`_end.js`).
- **Finding code:** `grep -rn 'name' src/` gives the file and line; read that file, or its range.
  `tools/app_layout.py` lists every file in order with the line it starts at.
- **Building:** `python3 tools/build_app.py` writes `canvas_v10.html` and prints its bytes and sha256;
  `--check` fails when `canvas_v10.html` is not what `src/` builds (the Pages workflow runs it);
  `--site DIR` writes the multi-file app. `tools/check_site.py` serves that app over http and proves
  it loads and runs exactly as the one file does (markers, globals, elements, pixels, desktop and phone).
- **Patching:** a phase's anchored scripts patch files under `src/`, then run `build_app.py`. The base
  hash they assert, and the hash `PIPELINE.md` records, is still `canvas_v10.html`'s, the built file's.
  Suites and falsification scripts read the built `canvas_v10.html`, as before; a pre-phase backup in
  `Phase/` is still that one file.
- **A new file:** create it in its folder, add its `<!-- @include -->` line to `src/index.html` where
  its code belongs in the order, and add its row (path, first line) to `tools/app_layout.py`.
- **A change made to `canvas_v10.html` itself** (a branch from before the split, merged): run
  `python3 tools/split_app.py`, which cuts it into `src/` by `app_layout.py` and refuses to finish
  unless `src/` joins back to it byte for byte. A row whose first line changed is fixed there first.
- **Playwright:** pin the Python package to the Chromium in `/opt/pw-browsers`, whatever
  `PIPELINE.md` last recorded: `ls /opt/pw-browsers`, then the release that drives that build
  (1.63.0 for chromium-1243, 2026-10-25; 1.56 for chromium-1194). A wrong pin fails at launch with
  "Executable doesn't exist" and names the build it wanted.
- **Pages:** `tools/build_site.py` serves `index.html` with `app/app.css`, `app/shell.js`,
  `app/openskp.js` and `app/engine.js` (each address carries its hash, so no browser runs an old
  copy), and `canvas_v10.html`, the same app as one file, for offline use from `file://`.

## Research depth (the owner, 2026-10-17)

"The more careful research the better for our plan when execute." Every phase's research follows
`reference/research-protocol.md`:
- every fact the code uses is read in its primary source (P), or in a dependable secondary one with
  the gap said (S); search-engine summaries are pointers, not sources (U), and U facts never reach
  the code;
- practice, the standard and its edition, where it applies, the free data tested from here, open
  implementations read as text, the edges of the rules, and the app's own code, for each topic;
- the owner's decisions asked together at the end of research;
- the note records each source, what was read, the date and its level, and what is still open;
- since 2026-10-31, as a scientist would ("use the research skills like a true researcher or
  scientist"): the question and falsifiable hypotheses first, a search log, three or more independent
  sources per topic, a deliberate search for counter-evidence, experiments run here wherever a claim
  can be measured (scripts in `reference/experiments/`), the alternatives compared in a table,
  prior art, a confidence for each finding, an independent second reader re-checking every fact the
  code uses, and parallel research agents for a broad question. The note's twelve parts are in the
  protocol.

## Notion (the owner, 2026-10-19)

The owner follows the project in Notion, on **World BIM Platform** (a Project in their G/P/R DB): every phase is
a task in the Internal Task DB, every research note and document a page in the Documentation DB, each pull
request a line on its phase's task. Keep it current as the work goes, through the Notion connector, at each step
of a phase (research started, the owner's decisions, PR opened, PR merged): `reference/notion-sync.md` has the
ids, the relations, the fields and the steps. The repository stays the source of truth; Notion mirrors it,
summarised and linked, never the full text of code or upstream documents. A research note's page carries the
research itself (the owner, 2026-10-31): its findings, evidence, comparisons, experiments, risks, decisions and
references, as `notion-sync.md` lists.

## Reuse first; keep source out of Notion (the owner, 2026-10-20)

Before integrating an open-source project, read `reference/reuse-first-integration.md`.
Prefer existing upstream modules plus narrow adapters over recreating working functionality.
A different language alone is not a reason to rewrite: evaluate the existing browser/WASM path.
Record concrete incompatibilities before proposing a port or replacement. Do not silently
change the app's delivery contract to achieve reuse; request approval with the evidence.

For SolidCraft, use `reference/plan-parametric-design.md` and issue #44. The first deliverable
is a verified `reference/solidcraft-integration-map.md`: pinned upstream revision, exact source
and documentation paths, reuse candidates, adapters, blockers and decisions. Create it from
actual inspection, not guessed module names. Keep a pinned local clone outside tracked project
files; inspect relevant source on demand, not the entire repository in model context. Upstream
build/execution remains gated by the research protocol and explicit owner approval.

GitHub/local files hold source, technical records and tests. Notion holds task scope, approvals,
progress summaries and links, not duplicate source trees or full upstream documentation. Do
not assume Claude Code can read Notion unless its connector is configured and works.

## Never idle on long checks (the owner, 2026-10-24)

(Since 2026-11-01 these checks run only when the owner asks; see Rule #1. When they do run, this applies.)

"i cant just wait till the falsification and full regression finish. we can build code ahead and plan while waiting."
Falsification and the full regression run against a frozen copy of the tested build: a git worktree at the tested
commit (`git worktree add <dir> <commit>`), started there, so nothing done meanwhile can change what they test. The
next phase is researched, designed and built in the main working copy at the same time, its patches based on the
tested build. Only the records' numbers wait for the checks; when a check finds a fault, the fix goes into both.

## Standing choices of the owner

- Free, keyless data only, credited; a server without CORS is named, not proxied.
- Industry standards kept as data with their editions, flexible when they change (V167's registry).
- Everything on phone, tablet and desktop. No emojis. No placeholders. Copyrighted text in our own
  words. Project photos and third-party screenshots never committed: the repository is public.
