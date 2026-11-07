# BIM-Personal

A browser CAD/BIM app with no dependencies: drawing, BIM elements, structure, sheets, site and
terrain, import and export. It runs from one HTML file, offline, on desktop, tablet and phone.

- The app: https://bradleypham1906.github.io/BIM-Personal/
- The user guide: `docs/` (published with the app)

## Layout

    src/             the source: css/, js/shell/, js/vendor/, js/engine/<feature>/ (ES modules), py/
    tests/unit/      unit tests (Node's built-in runner)
    tests/e2e/       browser suites (Python + Playwright)
    tests/fixtures/  what the suites serve and compare against
    tools/           build and check scripts
    docs/            the user guide; docs/dev/ for development records, docs/research/ for research notes
    runtime/         Pyodide and Ladybug's wheels, pinned, loaded only for Ladybug analyses
    vendor/          upstream sources of the vendored code
    canvas_v10.html  the build: the whole app in one file

## Working on it

Needs Python 3 and Node 22. Nothing to install for the app or the unit tests.

```bash
npm test
```

```bash
npm run build
```

```bash
npm run check
```

- `npm test` runs the unit tests (under a second). They load the engine in Node exactly as the
  build joins it, so each function can be tested on its own.
- `npm run build` joins `src/` into `canvas_v10.html`. Edit `src/`, never the build.
- `npm run modules` rewrites the engine files' import and export lines after you change what files
  share. `npm run check` (CI runs it) proves the build, the modules, the embedded Python and the
  guide are current; the module check needs TypeScript as a development tool (`npm install -g typescript`).
- `npm run test:e2e` runs the browser suites (slow; for changes to what the page shows).

How the engine is put together, and the project's working rules, are in `CLAUDE.md`.
