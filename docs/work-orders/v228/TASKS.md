# V228 work orders: Generated elements: a stable key, re-run in place, hand overrides

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/generated-elements.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v228/v228.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v228/v228.test.mjs
    node --check src/js/engine/bim/generated-elements.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimGelKey(gen, path)`

- **It must:** SPEC 5 WO-01: gen a non-empty string without `|`, `/` or `:` (else {error: 'bad generator id'}); path a non-empty array (else {error: 'empty path'}) of [rule, index]: rule a non-empty string without those characters (else {error: 'bad rule name at I'}, I the position); index a whole number of 0 or more, or a non-empty string without those characters (else {error: 'bad index at I'}). {key: gen + '|' + the parts 'rule:index' joined by '/'}. The first fault met, in path order, is the one returned.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/generated-elements.js`, `docs/work-orders/v228/v228.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v228/v228.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimGelShape(key)`

- **It must:** SPEC 5 WO-02: the key as a string with every index made only of digits replaced by `*`: 'g1|Facade:front/Floor:3/Bay:2' gives 'g1|Facade:front/Floor:*/Bay:*'. A key without `|` is returned unchanged (as a string). A part without `:` is left as it is.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/generated-elements.js`, `docs/work-orders/v228/v228.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v228/v228.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimGelReconcile(existing, derived)`

- **It must:** SPEC 5 WO-03: existing [{id, key}] (the elements a generator made before), derived [{key, ...}] (this run's items). Two derived items with one key: {error: 'duplicate key K'}. Else {update: [{id, item}] in derived order for items whose key an existing element carries (the first existing element with that key), create: [the other derived items, in order], remove: [ids]}: first the later existing elements that repeat a key already seen, in existing order, then the existing elements whose key no derived item has, in existing order. Neither argument is changed.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/generated-elements.js`, `docs/work-orders/v228/v228.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v228/v228.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimGelOverrides(overrides, keys)`

- **It must:** SPEC 5 WO-04: overrides [{key, prop, value}], keys [the keys of this run]. Each override, in order, goes to one list: apply when its key is in keys; dormant when it is not but bimGelShape of its key equals bimGelShape of some key in keys (its place is gone for now, as when 10 bays become 8); listed otherwise (its rule is gone). {apply, dormant, listed}, holding the same override objects.
- **May use:** bimGelShape (WO-02).
- **Files:** `src/js/engine/bim/generated-elements.js`, `docs/work-orders/v228/v228.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v228/v228.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Cline] `bimGelApply(item, overrides)`

- **It must:** SPEC 5 WO-05: a copy of item (its own keys copied; props a new object with item.props's own keys, {} when it has none) with, for each override in order whose key is item.key, props[prop] = value; and ov, the names of the properties so set, each once, in the order first met.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/generated-elements.js`, `docs/work-orders/v228/v228.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v228/v228.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-06 [Claude] Wiring into the app

Claude's: the generator record in `A3D.site.generators`, `bim.gen` on elements, the batch maker (one undo step, one repaint, one save), re-run by reconciliation, the Properties form with its dormant and listed overrides and the rules as text; saving with the project and undo; the test to tests/unit/; npm run modules; the browser check, which also measures the opening cutter's cost on a facade.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 228, Notion.
