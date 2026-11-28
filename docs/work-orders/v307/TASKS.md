# V307 work orders: OB3, types as IFC type objects

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom, after V305's WO-01 (bimIfcGuidNew). `[ ]` open, `[x]` done (its tests pass).

Every `[Cline]` task: add its function (and any table its task names, just above it) to
`src/js/engine/io/ifc-save-types.js`, below the file's header comment and the earlier tasks' functions, and change
nothing else: not another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`, `function`;
no `let`, `const`, arrow functions, classes or template strings. Use only the names listed. Implement the whole
function; never a placeholder.

The tests are in `docs/work-orders/v307/v307.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v307/v307.test.mjs
    node --check src/js/engine/io/ifc-save-types.js
    npm test

Nothing calls these functions until Claude's WO-06. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `BIM_IFC_TYPE_CLASS`, `bimIfcTypeClassOf(cat)`

- **It must:** SPEC 4 WO-01: the table of seven categories, each [type class, predefined type]; the function gives the type class, '' for anything else (hasOwnProperty, so 'hasOwnProperty' itself is '').
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-save-types.js`, `docs/work-orders/v307/v307.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v307/v307.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimIfcTypePredefinedDefault(cat)`

- **It must:** SPEC 4 WO-02: the table's predefined type, 'NOTDEFINED' for anything else.
- **May use:** `BIM_IFC_TYPE_CLASS` (WO-01).
- **Files:** `src/js/engine/io/ifc-save-types.js`, `docs/work-orders/v307/v307.test.mjs`
- **Budget:** 5
- **Test:** the cases named `WO-02 ...`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimIfcEnsureTypeIdentity(t, cat, rand)`

- **It must:** SPEC 4 WO-03: null for no t; the same t, its `ifc.guid` kept when valid else new, its `ifc.predefined` kept when a non-empty string else the category's default; other fields of `t.ifc` kept.
- **May use:** `bimTorGuidValid` (`src/js/engine/io/ifc-review.js`), `bimIfcGuidNew` (`src/js/engine/bim/ifc-identity.js`, V305 WO-01), `bimIfcTypePredefinedDefault` (WO-02).
- **Files:** `src/js/engine/io/ifc-save-types.js`, `docs/work-orders/v307/v307.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-03 ...`. **Score:** 0+0+0+0+1+0 = 1.
- **Distinguishing case:** replacing `t.ifc` with a new object loses "note: kept".

---

## [ ] WO-04 [Cline] `bimIfcPredefinedPair(typePre, instPre)`

- **It must:** SPEC 4 WO-04: empty or non-string values are none; no type predefined: {type: null, instance: instPre or 'NOTDEFINED'}; else {type: typePre, instance: instPre only when given and different, else null}.
- **May use:** nothing.
- **Files:** `src/js/engine/io/ifc-save-types.js`, `docs/work-orders/v307/v307.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-04 ...`. **Score:** 0.
- **Distinguishing case:** returning the instance's value when it equals the type's writes it twice; the test wants null.

---

## [ ] WO-05 [Cline] `bimIfcSaveTypes(types, used)`

- **It must:** SPEC 4 WO-05: the used types with a class and a valid GlobalId, in order, as {id, guid, cls, name (or the id), predefined (or the default)}.
- **May use:** `bimTorGuidValid` (`src/js/engine/io/ifc-review.js`), `bimIfcTypeClassOf` (WO-01), `bimIfcTypePredefinedDefault` (WO-02).
- **Files:** `src/js/engine/io/ifc-save-types.js`, `docs/work-orders/v307/v307.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-05 ...`. **Score:** 0.
- **Distinguishing case:** keeping a type without a GlobalId writes an IfcColumnType IfcOpenShell must invent an id for.

---

## [ ] WO-06 [Claude] Types stamped, saved and assigned

SPEC 5 WO-06: bim/type-instance-params.js, io/ifc-save.js, src/py/bim_ifcos.py; the tests to tests/unit/; the browser check; records.
