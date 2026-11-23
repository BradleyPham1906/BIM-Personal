# V275 work orders: the Explode view

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function to `src/js/engine/views/explode-view.js`, below the file's header comment, and
change nothing else: not another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed; never a name
from another file. Implement the whole function; never a placeholder. Never change the objects or arrays passed in.

The tests are in `docs/work-orders/v275/v275.test.mjs`, outside `npm test` while the orders are open, so main stays
green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v275/v275.test.mjs
    node --check src/js/engine/views/explode-view.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimXvRanks(levels)`

- **It must:** SPEC 4 WO-01: group the levels by `buildingId` (missing or empty is the group `''`); in each group sort
  copies `{id, e: elev, i: index}` by `e`, then by `i`; give rank 0, 1, 2 ... in that order; return `{id: rank}`;
  `{}` for null or an empty array.
- **Example:** `bimXvRanks([{id: 'x', elev: 3}, {id: 'y', elev: 3}, {id: 'z', elev: -3}])` returns `{z: 0, x: 1, y: 2}`.
- **User path:** internal only.
- **May use:** nothing.
- **Files:** `src/js/engine/views/explode-view.js`, `docs/work-orders/v275/v275.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v275/v275.test.mjs`.
- **Distinguishing case:** ranking all levels together, not per building, gives b1 the rank 3 and fails.
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimXvLevelOf(item, levels)`

- **It must:** SPEC 4 WO-02's four rules in order: an existing `item.levelId`; a level named `item.storey + ' (IFC)'`
  when `item.storey` is not empty; by `item.minY` when it is a finite number (the highest `elev` at most
  `item.minY + 0.05`, else the lowest level, the first of equal lowest); else null. Null when `levels` is empty.
- **Example:** `{minY: 2.96}` with levels at 0, 3 and 6 m returns the 3 m level.
- **User path:** internal only.
- **May use:** nothing.
- **Files:** `src/js/engine/views/explode-view.js`, `docs/work-orders/v275/v275.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-02 ...`.
- **Distinguishing case:** returning `item.levelId` without checking that the level exists fails the "gone" case; no
  5 cm allowance fails the 2.96 m case.
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimXvGap(levels)`

- **It must:** SPEC 4 WO-03: the largest `height` that is a finite number above 0; 3 when there is none or `levels` is null.
- **User path:** internal only.
- **May use:** nothing.
- **Files:** `src/js/engine/views/explode-view.js`, `docs/work-orders/v275/v275.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-03 ...`.
- **Distinguishing case:** `Math.max` over heights with a NaN gives NaN and fails.
- **Score:** 0.

---

## [ ] WO-04 [Cline] `bimXvOffset(rank, amount, gap)`

- **It must:** SPEC 4 WO-04: `[0, 0, 0]` when `rank` is null or undefined; else `[0, rank * gap * a, 0]` with
  `a = amount > 1 ? 1 : (amount > 0 ? amount : 0)`.
- **Example:** `bimXvOffset(2, 0.5, 4)` returns `[0, 4, 0]`.
- **User path:** internal only.
- **May use:** nothing.
- **Files:** `src/js/engine/views/explode-view.js`, `docs/work-orders/v275/v275.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-04 ...`.
- **Score:** 0.

---

## [ ] WO-05 [Cline] `bimXvOffsets(items, levels, amount)`

- **It must:** SPEC 4 WO-05: ranks once (`bimXvRanks`), the gap once (`bimXvGap`); for each item its level
  (`bimXvLevelOf`), its offset (`bimXvOffset` with the level's rank, or null when no level); keep only offsets whose
  second number is not 0, under the item's `id`. `{}` for none.
- **User path:** internal only (WO-07 calls it when the amount or the model changes).
- **May use:** `bimXvRanks`, `bimXvLevelOf`, `bimXvGap`, `bimXvOffset` (this file).
- **Files:** `src/js/engine/views/explode-view.js`, `docs/work-orders/v275/v275.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-05 ...`.
- **Distinguishing case:** keeping zero offsets returns `w0` and `loose` and fails.
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-06 [Cline] `bimXvNext(state, action)`

- **It must:** SPEC 4 WO-06: `s = state || {on: false, amount: 0}`; toggle: when `s.on`, `{on: false, amount: s.amount}`,
  else `{on: true, amount: s.amount > 0 ? s.amount : 0.5}`; set: `a` the amount kept between 0 and 1,
  `{on: a > 0, amount: a}`; collapse: `{on: false, amount: 0}`; anything else `{on: s.on, amount: s.amount}`. Always
  a new object.
- **User path:** the EXPLODEVIEW button and slider (WO-08).
- **May use:** nothing.
- **Files:** `src/js/engine/views/explode-view.js`, `docs/work-orders/v275/v275.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-06 ...`.
- **Distinguishing case:** changing `state` in place fails "the old state is not changed".
- **Score:** 0.

---

## [ ] WO-07 [Claude] The offset drawn and picked

SPEC 5 WO-07: the renderer's rows and chunk boxes, the full audit of drawing and picking paths that read `o.pos`, the
offsets computed on change, the rendered view's rebuild cost measured. Claude's: rendering and picking across files.
Score 2+1+2+1+2+1 = 9.

---

## [ ] WO-08 [Claude] The interface

SPEC 5 WO-08: EXPLODEVIEW, the button and slider on every screen size, saved views, collapse before an edit.

---

## [ ] WO-09 [Claude] Tests into tests/unit, modules, the browser check

---

## [ ] WO-10 [Claude] The records

QUEUE, PIPELINE, Notion.
