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

## The source: src/, by feature (the owner, 2026-10-25)

"having a one html with all the code cost me so many token and i want the app structure to be like a
profesisonal app where there are multi folders and files." The app is edited in `src/`; never edit
`canvas_v10.html` by hand, and never read it whole: it is a build output, committed because every
suite, every falsification script, `Phase/`'s backups and the guide's tools read it.

    src/index.html            the page: its head and body, and for each block the files it is made of,
                              in order (<!-- @bundle -->, <!-- @include -->, <!-- @end -->)
    src/css/                  the stylesheet, 12 files: shell/, panels/, workspace/, sheets/, site-analysis/
    src/js/shell/shell.js     the top bar, the command palette, the project tabs, the boot
    src/js/vendor/openskp.js  the SketchUp reader (third-party, bundled; never edited by hand)
    src/js/engine/            the BIM engine, 174 files in 26 folders: core/ (state, storage, meshes,
                              save), drawing/, editing/, gizmo/, bim/, structure/, annotation/,
                              layers/, properties/, views/, sheets/, assets/, io/, render/, map/,
                              terrain/, survey/, site/, site-analysis/ (with V171b's analysis
                              workspace), simulation/ (V171's traffic and people), standards/,
                              analysis/, history/, ui/, commands/,
                              testing/ (the window.__a3d* surface the suites drive); _begin.js and
                              _end.js open and close it

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
- the note records each source, what was read, the date and its level, and what is still open.

## Notion (the owner, 2026-10-19)

The owner follows the project in Notion, on **World BIM Platform** (a Project in their G/P/R DB): every phase is
a task in the Internal Task DB, every research note and document a page in the Documentation DB, each pull
request a line on its phase's task. Keep it current as the work goes, through the Notion connector, at each step
of a phase (research started, the owner's decisions, PR opened, PR merged): `reference/notion-sync.md` has the
ids, the relations, the fields and the steps. The repository stays the source of truth; Notion mirrors it,
summarised and linked, never the full text.

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
