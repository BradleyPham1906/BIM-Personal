# V218 work orders: Streaming: OGC 3D Tiles

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/map/tiles3d.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v218/v218.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v218/v218.test.mjs
    node --check src/js/engine/map/tiles3d.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimTilesSse(ge, dist, h, fov)`

- **It must:** SPEC 5 WO-01: ge h / (2 dist tan(fov / 2)); Infinity when dist is not positive.
- **May use:** nothing.
- **Files:** `src/js/engine/map/tiles3d.js`, `docs/work-orders/v218/v218.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v218/v218.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimTilesDist(sphere, eye)`

- **It must:** SPEC 5 WO-02: the distance from the eye to the sphere [x, y, z, r]'s surface, 0 inside.
- **May use:** nothing.
- **Files:** `src/js/engine/map/tiles3d.js`, `docs/work-orders/v218/v218.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v218/v218.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimTilesSelect(tile, eye, h, fov, maxSse, parentRefine)`

- **It must:** SPEC 5 WO-03: a tile whose error is within maxSse, or with no children, gives its content uri (when it has one); else ADD tiles (refine inherited from the parent, REPLACE by default) give their own uri and then their children's, REPLACE tiles only their children's, depth first in order.
- **May use:** bimTilesSse (WO-01), bimTilesDist (WO-02).
- **Files:** `src/js/engine/map/tiles3d.js`, `docs/work-orders/v218/v218.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v218/v218.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-04 [Claude] Tiles in the rendered view

Claude's: fetching tileset.json and glTF content (V195's reader), the cache, the source's credit, box and region volumes. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-05 [Claude] The records

PIPELINE row 218, Notion.
