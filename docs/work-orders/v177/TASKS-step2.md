# V177 work orders: IfcOpenShell II, step 2: the model as V177's data

Spec: `SPEC-step2.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/io/ifc-save.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v177/v177-step2.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v177/v177-step2.test.mjs
    node --check src/js/engine/io/ifc-save.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-11 [Cline] `bimIfsPlan(p)`

- **It must:** SPEC 5 WO-11: [p[0], 0 - p[1]] (never -0).
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-save.js`, `docs/work-orders/v177/v177-step2.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-11 ...` in `docs/work-orders/v177/v177-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-12 [Cline] `bimIfsLevels(levels)`

- **It must:** SPEC 5 WO-12: the levels with a finite elev, as {id: String(id), name (or 'Level ' + the count so far), elev}, sorted by elev.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-save.js`, `docs/work-orders/v177/v177-step2.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-12 ...` in `docs/work-orders/v177/v177-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-13 [Cline] `bimIfsLevelIndex(lv, levelId, y)`

- **It must:** SPEC 5 WO-13: the index of the level whose id is levelId; else of the last with elev <= y + 1e-6; else 0 (also for no levels).
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-save.js`, `docs/work-orders/v177/v177-step2.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-13 ...` in `docs/work-orders/v177/v177-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-14 [Cline] `bimIfsWalls(o, lv)`

- **It must:** SPEC 5 WO-14: [] unless a wall with 2 or more centreline points and no bulges; one entry per segment (and last to first when closed with more than 2): {id (o.id, or o.id + '#' + i when several), host: o.id, name (o.name, or o.name + ' ' + (i+1)), level (WO-13 on levelId and baseY), x0, y0, x1, y1 (WO-11), base: baseY, height, thickness: dLeft + dRight, offset: 0 - dLeft, guid when bim.guid is set}; dLeft and dRight from align: 'left' {0, t}, 'right' {t, 0}, an object with finite dLeft and dRight as it is, else {t/2, t/2}.
- **May use:** bimIfsPlan, bimIfsLevelIndex (WO-11, WO-13).
- **Files:** `src/js/engine/io/ifc-save.js`, `docs/work-orders/v177/v177-step2.test.mjs`
- **Budget:** 70
- **Test:** the cases named `WO-14 ...` in `docs/work-orders/v177/v177-step2.test.mjs`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-15 [Cline] `bimIfsSlab(o, lv)`

- **It must:** SPEC 5 WO-15: null unless a floor with 3 or more profile points; {id, name, level (on baseY - thickness), cls: 'IfcSlab', pts (WO-11), base: baseY - thickness, depth: thickness}.
- **May use:** bimIfsPlan, bimIfsLevelIndex.
- **Files:** `src/js/engine/io/ifc-save.js`, `docs/work-orders/v177/v177-step2.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-15 ...` in `docs/work-orders/v177/v177-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-16 [Cline] `bimIfsColumn(o, lv)`

- **It must:** SPEC 5 WO-16: null unless a column with a center and no section; its four corners in the app's plan (local (-w/2,-d/2), (w/2,-d/2), (w/2,d/2), (-w/2,d/2) turned by rotation: x cos - z sin, x sin + z cos, plus the centre), each through WO-11, the list reversed (anticlockwise in IFC's plan); {id, name, level, cls: 'IfcColumn', pts, base: baseY, depth: height}.
- **May use:** bimIfsPlan, bimIfsLevelIndex.
- **Files:** `src/js/engine/io/ifc-save.js`, `docs/work-orders/v177/v177-step2.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-16 ...` in `docs/work-orders/v177/v177-step2.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-17 [Cline] `bimIfsOpening(m, walls)`

- **It must:** SPEC 5 WO-17: null unless a door or window with a center and walls given; among the walls whose host is bim.hostWallId (length 1e-9 or more), the projection t of the centre (WO-11) within -1e-6..L+1e-6, the one nearest its line: {id, name, cls: 'IfcDoor' or 'IfcWindow', host: that wall's id, x, y: the point t along its line, a: atan2(dy, dx) of the wall, base: the wall's base + (sillHeight or 0), width, height, depth: the wall's thickness + 0.1}; null when none.
- **May use:** bimIfsPlan.
- **Files:** `src/js/engine/io/ifc-save.js`, `docs/work-orders/v177/v177-step2.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-17 ...` in `docs/work-orders/v177/v177-step2.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-18 [Cline] `bimIfsMesh(o, lv)`

- **It must:** SPEC 5 WO-18: with BIM_IFS_CLASS (wall IfcWall, floor and slab IfcSlab, roof IfcRoof, stair IfcStair, beam IfcBeam, column IfcColumn, railing IfcRailing, ceiling IfcCovering, footing IfcFooting) just above it: null without mesh.v and mesh.f; verts [x + px, 0 - (z + pz), y + py]; each face of 3 or more fanned into triangles [f0, fj, fj+1]; null when none; level by the lowest y; cls bim.ifcType when it matches /^Ifc[A-Za-z]+$/, else the table's, else 'IfcBuildingElementProxy'.
- **May use:** bimIfsLevelIndex, BIM_IFS_CLASS (this task).
- **Files:** `src/js/engine/io/ifc-save.js`, `docs/work-orders/v177/v177-step2.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-18 ...` in `docs/work-orders/v177/v177-step2.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-19 [Cline] `bimIfsModel(objs, levels, name)`

- **It must:** SPEC 5 WO-19: V177's data (its SPEC part 3): {name (or 'Project'), levels: [{name, elev}] (WO-12), walls, prisms, openings, meshes}; each solid into the first of walls (every segment), a slab or column prism, a mesh; openings (t 'opening') last against all walls.
- **May use:** the functions of WO-11 to WO-18.
- **Files:** `src/js/engine/io/ifc-save.js`, `docs/work-orders/v177/v177-step2.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-19 ...` in `docs/work-orders/v177/v177-step2.test.mjs`. **Score:** 0+0+1+0+1+0 = 2.

---

## [ ] WO-20 [Claude] The wheels, the worker, File > Export > IFC, Make editable

Claude's: SPEC.md part 2 step 2 (the wheels in runtime/ with their licence texts, the worker, the command, Make editable); the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-21 [Claude] The records

PIPELINE row 177, Notion.
