# V207 work orders: glTF models in Assets, and valdrada's credited models

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/assets/gltf-assets.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v207/v207.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v207/v207.test.mjs
    node --check src/js/engine/assets/gltf-assets.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimAstGltfStats(g)`

- **It must:** SPEC 5 WO-01: null unless an object; {meshes, primitives, triangles, materials, textures, extensions (extensionsUsed sorted)}: triangles summed over primitives of mode 4 or no mode, floor(count / 3) of the indices accessor, else of the POSITION accessor.
- **May use:** nothing.
- **Files:** `src/js/engine/assets/gltf-assets.js`, `docs/work-orders/v207/v207.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v207/v207.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimAstFitBox(min, max, size)`

- **It must:** SPEC 5 WO-02: s = size / the largest extent when both are positive, else 1; {scale: s, move: [-(minX + maxX)/2 s, -minY s, -(minZ + maxZ)/2 s] (written so 0 stays 0, never -0), size: the extents times s}.
- **May use:** nothing.
- **Files:** `src/js/engine/assets/gltf-assets.js`, `docs/work-orders/v207/v207.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v207/v207.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimAstCheck(stats, bytes, limits)`

- **It must:** SPEC 5 WO-03: messages: no stats ['not a glTF file']; triangles over limits.triangles (200000 by default): 'N triangles, over T'; bytes over limits.bytes (20 MB, 20971520): 'X MB, over Y MB', MB to one decimal.
- **May use:** nothing.
- **Files:** `src/js/engine/assets/gltf-assets.js`, `docs/work-orders/v207/v207.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v207/v207.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimAstCredit(e)`

- **It must:** SPEC 5 WO-04: '"title" by author, license (source)', each part only when present; 'Untitled' without a title.
- **May use:** nothing.
- **Files:** `src/js/engine/assets/gltf-assets.js`, `docs/work-orders/v207/v207.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v207/v207.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] glTF models in Assets

Claude's: drop or import into Assets through V195's reader, the card with counts and credit, placement; valdrada's vehicles converted and credited; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 207, Notion.
