# V306 work orders: OB2, IFC class and predefined type

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add its function (and any table its task names, just above it) to `src/js/engine/bim/ifc-class.js`,
below the file's header comment and the earlier tasks' functions, and change nothing else: not another file, not the
`import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions,
classes or template strings. Use only the names listed. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v306/v306.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v306/v306.test.mjs
    node --check src/js/engine/bim/ifc-class.js
    npm test

Nothing calls these functions until Claude's WO-05. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimIfcRoofPredefined(style, pitch)`

- **It must:** SPEC 4 WO-01: 'FLAT_ROOF' when pitch is a finite number under half a degree either way; else by style: shed SHED_ROOF, gable GABLE_ROOF, hip HIP_ROOF, anything else NOTDEFINED.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/ifc-class.js`, `docs/work-orders/v306/v306.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v306/v306.test.mjs`. **Score:** 0.
- **Distinguishing case:** testing `pitch < 0.5` without the absolute value calls a pitch of -5 degrees flat; checking the style before the pitch calls a 0-degree gable GABLE_ROOF.

---

## [ ] WO-02 [Cline] `BIM_IFC_PREDEFINED`, `bimIfcPredefinedOptions(cls)`

- **It must:** SPEC 4 WO-02: the table holds the 12 lists of `docs/research/experiments/thatopen-gap/ifc4-predefined.json` ("enums"), exactly, in the same order; the function returns a copy of cls's list, [] for any other cls.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/ifc-class.js`, `docs/work-orders/v306/v306.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-02 ...`. **Score:** 0.
- **Distinguishing case:** returning the table's own array fails "a copy: changing it changes nothing".

---

## [ ] WO-03 [Cline] `bimIfcPredefinedValid(cls, value)`

- **It must:** SPEC 4 WO-03: true only for a non-empty string in cls's list (case as in the schema).
- **May use:** `bimIfcPredefinedOptions` (WO-02).
- **Files:** `src/js/engine/bim/ifc-class.js`, `docs/work-orders/v306/v306.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-03 ...`. **Score:** 0.

---

## [ ] WO-04 [Cline] `BIM_IFC_CLASS`, `bimIfcClassOf(rec)`

- **It must:** SPEC 4 WO-04, its five steps in order, the element's own valid predefined type replacing the default in steps 2 and 3.
- **May use:** `bimIfcRoofPredefined` (WO-01), `bimIfcPredefinedValid` (WO-03).
- **Files:** `src/js/engine/bim/ifc-class.js`, `docs/work-orders/v306/v306.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-04 ...`. **Score:** 0+0+0+0+1+0 = 1.
- **Distinguishing case:** taking own.predefined without checking it against the class gives an IfcWall FLOOR.

---

## [ ] WO-05 [Claude] The class and predefined type saved and chosen

SPEC 5 WO-05: io/ifc-save.js, src/py/bim_ifcos.py, properties/palette.js; the tests to tests/unit/; the browser check; records.
