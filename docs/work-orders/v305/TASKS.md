# V305 work orders: OB1, IFC identity: GlobalIds that last

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function to `src/js/engine/bim/ifc-identity.js`, below the file's header comment and the
earlier tasks' functions, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes, template strings or
BigInt. Use only the names listed. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v305/v305.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v305/v305.test.mjs
    node --check src/js/engine/bim/ifc-identity.js
    npm test

Nothing calls these functions until Claude's WO-07. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimIfcGuidNew(rand)`

- **It must:** SPEC 4 WO-01: 16 bytes from rand (Math.random when rand is not a function), each Math.floor(v * 256) with v clamped (not a number at or above 0: 0; 1 or more: 0.999999); byte 6 = (b AND 0x0f) OR 0x40, byte 8 = (b AND 0x3f) OR 0x80; 32 lower-case hex digits through bimTorGuidFromHex.
- **Example:** rand giving 0, 1/256, 2/256 ... gives the GlobalId of hex `000102030405460788090a0b0c0d0e0f`.
- **User path:** internal only (Save as IFC, after WO-07).
- **May use:** `bimTorGuidFromHex` (`src/js/engine/io/ifc-review.js`).
- **Files:** `src/js/engine/bim/ifc-identity.js`, `docs/work-orders/v305/v305.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v305/v305.test.mjs`. **Score:** 0.
- **Distinguishing case:** leaving out the version bits passes the GlobalId's validity but fails the hex `...4607 88...`.

---

## [ ] WO-02 [Cline] `bimIfcEnsureIdentity(bim, rand)`

- **It must:** SPEC 4 WO-02: null for no bim; otherwise the same bim, with `bim.ifc.guid` set once: kept when valid, else `bim.guid` when that is valid, else a new one; the other fields of `bim.ifc` kept.
- **May use:** `bimTorGuidValid` (`src/js/engine/io/ifc-review.js`), `bimIfcGuidNew` (WO-01).
- **Files:** `src/js/engine/bim/ifc-identity.js`, `docs/work-orders/v305/v305.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-02 ...`. **Score:** 0.
- **Distinguishing case:** a version that always makes a new GlobalId fails "a valid GlobalId is never replaced".

---

## [ ] WO-03 [Cline] `bimIfcSegmentGuids(bim, n, rand)`

- **It must:** SPEC 4 WO-03: [] for no bim; ensures the identity; a list of n: entry 0 the element's GlobalId, entry i the old `segGuids[i]` when valid and not already in the list, else new; stored as `bim.ifc.segGuids`, a copy returned.
- **May use:** `bimTorGuidValid` (`src/js/engine/io/ifc-review.js`), `bimIfcGuidNew` (WO-01), `bimIfcEnsureIdentity` (WO-02).
- **Files:** `src/js/engine/bim/ifc-identity.js`, `docs/work-orders/v305/v305.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-03 ...`. **Score:** 0+0+0+0+1+0 = 1.
- **Distinguishing case:** keeping a repeated entry fails "a repeat is not kept".

---

## [ ] WO-04 [Cline] `bimIfcForgetIdentity(bim)`

- **It must:** SPEC 4 WO-04: null for no bim; deletes `bim.guid`, `bim.ifc.guid`, `bim.ifc.segGuids`, `bim.ifc.openingGuid`; `bim.ifc` deleted when empty; returns bim.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/ifc-identity.js`, `docs/work-orders/v305/v305.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-04 ...`. **Score:** 0.
- **Distinguishing case:** deleting all of `bim.ifc` loses the class and predefined type the test keeps.

---

## [ ] WO-05 [Cline] `bimIfcSpatialIds(prev, levelIds, buildingIds, rand)`

- **It must:** SPEC 4 WO-05: a new {project, site, buildings, levels}, prev unchanged; each prev value kept when valid, else new, made in the order project, site, buildings, levels; only the ids given.
- **May use:** `bimTorGuidValid` (`src/js/engine/io/ifc-review.js`), `bimIfcGuidNew` (WO-01).
- **Files:** `src/js/engine/bim/ifc-identity.js`, `docs/work-orders/v305/v305.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-05 ...`. **Score:** 0.
- **Distinguishing case:** changing prev in place fails "the previous record is not changed".

---

## [ ] WO-06 [Cline] `bimIfcDedupe(items, rand)`

- **It must:** SPEC 4 WO-06: {guids, made, repeated}: items without an id left out; a valid guid seen for the first time kept; else a new one (made again while already given); made counts new ones, repeated the valid ones seen before; items unchanged.
- **May use:** `bimTorGuidValid` (`src/js/engine/io/ifc-review.js`), `bimIfcGuidNew` (WO-01).
- **Files:** `src/js/engine/bim/ifc-identity.js`, `docs/work-orders/v305/v305.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-06 ...`. **Score:** 0+0+0+0+1+0 = 1.
- **Distinguishing case:** counting only missing ones as made gives 2, not 3.

---

## [ ] WO-07 [Claude] The wiring: identity on save and on copy

SPEC 5 WO-07: io/ifc-save.js, src/py/bim_ifcos.py (embedded: tools/embed_py.py), the copy paths, Properties; npm run modules; the tests to tests/unit/.

---

## [ ] WO-08 [Claude] Hidden layers exported

SPEC 5 WO-08: io/ifcos-worker.js, the header description.

---

## [ ] WO-09 [Claude] The faster import route, then cc-ifc retired

SPEC 5 WO-09: measured on V196's 13 files by e03 first.

---

## [ ] WO-10 [Claude] The browser check and the records

SPEC 5 WO-10; PIPELINE row 305, QUEUE, STATUS, Notion.
