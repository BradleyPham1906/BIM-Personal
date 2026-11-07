# V172h experiments: installable and offline

Data scripts, not a suite: nothing here is run by `npm test`, CI or `tests/e2e/`. They measure, in this
container's Chromium, the hypotheses of part 14 of `docs/research/research-local-storage.md` that can be
measured from here. The results, with every raw number, are in
`docs/research/research-local-storage/v172h-experiments.md`.

The service workers here are **experiment workers**, not the app's, and are never deployed: the build has no
worker and no registration code; the drivers register these from the page with `page.evaluate`.

## Environment (2026-11-07)

- Chromium `chromium-1243` in `/opt/pw-browsers` (`browser.version()` 153.0.8010.12), headless; e06 also runs the
  full binary's new headless mode (`channel: 'chromium'`).
- Node v22.23.4 and `require('playwright')` 1.63.0, already installed. Never run `playwright install`.
- Linux, 4 vCPU, 15 GiB RAM. Firefox and WebKit are not installed.

## How to run

From this folder, one script at a time (they start their own server and browser):

    node e01_scope.js            # H29            ~20 s
    node e02_precache.js         # H31, H37, cost ~30 s
    node e03_offline_app.js      # H32            ~2 min (RUNS=5)
    node e04_update.js           # H33, H34, H35  ~6 min (RUNS=5)
    node e05_worker_fetch.js     # H36            ~2 min
    node e06_install_prompt.js   # H38            ~5 min
    node e07_load_cost.js        # load cost      ~2 min (RUNS=7)

- `RUNS=<n>` changes the number of runs.
- The first script builds the site with `python3 tools/build_site.py` into the scratch directory
  (`V172H_SCRATCH`, by default this session's scratchpad `.../scratchpad/v172h-exp/`): `siteA/` is the build,
  `siteB/` a copy with one comment appended to `app/engine.js` and its `?v=` recomputed (the "new deploy").
  `V172H_REBUILD=1` rebuilds A; delete `siteB/` to remake B. Nothing is written into the repository.
- Raw results: `<scratch>/results/<script>.json`. Temporary browser profiles: `<scratch>/profiles/`, deleted
  after each run.
- `node _server.js <siteDir> [port]` serves a build by hand at `http://localhost:<port>/BIM-Personal/`.

## Files

| File | What it is |
|---|---|
| `_server.js` | the local stand-in for GitHub Pages: subpath `/BIM-Personal/`, `max-age=600`, ETag and 304, JS MIME, a second build swapped in, generated files at a path, request counts, stop and restart on the same port |
| `_common.js` | builds A and B, starts the server, makes experiment pages and workers, writes results |
| `exp.js` | page helpers: registration with its events logged, ask a worker by `MessageChannel`, apply an update unless the page has unsaved work, reload once on `controllerchange` |
| `sw-app.template.js` | the experiment worker for the built app: precache by the build's exact `?v=` URLs, delete other builds' caches on activate, network-first navigations, cache-first `runtime/`, cross-origin untouched |
| `sw-probe.template.js` | a probe worker: answers `/__probe` itself and records every fetch it sees; with no fetch handler for e06 |
| `e01_scope.js` ... `e07_load_cost.js` | the experiments (each file's header says what it measures and how) |
