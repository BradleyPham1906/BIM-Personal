# V175c work orders: One paper space, steps 2 and 3: one editor, one print

Spec: `SPEC-step2.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/sheets/layout-merge.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v175c/v175c-step2.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v175c/v175c-step2.test.mjs
    node --check src/js/engine/sheets/layout-merge.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-11 [Cline] `bimLmVpToFrame(vp)`

- **It must:** SPEC 5 WO-11: a sheet viewport {id, kind, refId, label, x, y, w, h, scaleMode, scaleDenom} as the map frame {t: 'map', id, x, y, w, h, src: kind + ':' + refId, den: scaleDenom (null when scaleMode is 'fit'), fit: scaleMode === 'fit', px: 0, py: 0, label (or '')}.
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/layout-merge.js`, `docs/work-orders/v175c/v175c-step2.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-11 ...` in `docs/work-orders/v175c/v175c-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-12 [Cline] `bimLmFrameToVp(fr)`

- **It must:** SPEC 5 WO-12: the inverse: kind before the first ':' of src, refId after it ('' when none); scaleMode 'fit' when fr.fit or den is not positive, else 'fixed'; scaleDenom den when positive, else 100; the keys in the order id, kind, refId, label, x, y, w, h, scaleMode, scaleDenom.
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/layout-merge.js`, `docs/work-orders/v175c/v175c-step2.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-12 ...` in `docs/work-orders/v175c/v175c-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-13 [Cline] `bimLmSheetToLayout(sh)`

- **It must:** SPEC 5 WO-13: {id, num: number or '', name or '', w, h, drawing: true, objs: [{t: 'tblock', id: 'tb-' + id, x: 0, y: 0, w, h}, then a frame (WO-11) per viewport]}.
- **May use:** bimLmVpToFrame (WO-11).
- **Files:** `src/js/engine/sheets/layout-merge.js`, `docs/work-orders/v175c/v175c-step2.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-13 ...` in `docs/work-orders/v175c/v175c-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-14 [Cline] `bimLmDrawMenu(items, drawing)`

- **It must:** SPEC 5 WO-14: the items, leaving out those of kind 'live', 'figure' or 'chart' when drawing is true (the owner's D4).
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/layout-merge.js`, `docs/work-orders/v175c/v175c-step2.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-14 ...` in `docs/work-orders/v175c/v175c-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-15 [Cline] `bimLmN(v)`

- **It must:** SPEC 5 WO-15: v rounded to 3 decimals as a string, '0' for any rounded zero.
- **May use:** nothing.
- **Files:** `src/js/engine/sheets/layout-merge.js`, `docs/work-orders/v175c/v175c-step2.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-15 ...` in `docs/work-orders/v175c/v175c-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-16 [Cline] `bimLmSvgOpen(w, h)`

- **It must:** SPEC 5 WO-16: '<svg xmlns="http://www.w3.org/2000/svg" width="Wmm" height="Hmm" viewBox="0 0 W H">' with W, H by WO-15.
- **May use:** bimLmN (WO-15).
- **Files:** `src/js/engine/sheets/layout-merge.js`, `docs/work-orders/v175c/v175c-step2.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-16 ...` in `docs/work-orders/v175c/v175c-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-17 [Cline] `bimLmSvgRect(o, stroke, width)`

- **It must:** SPEC 5 WO-17: '<rect x=".." y=".." width=".." height=".." fill="none" stroke="S" stroke-width="W"/>', numbers by WO-15, stroke '#000000' and width 0.25 by default.
- **May use:** bimLmN (WO-15).
- **Files:** `src/js/engine/sheets/layout-merge.js`, `docs/work-orders/v175c/v175c-step2.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-17 ...` in `docs/work-orders/v175c/v175c-step2.test.mjs`. **Score:** 0.

---

## [ ] WO-18 [Claude] One editor and one print in the app

Claude's: sheets opened as layouts in the board editor (frames as viewports with Work in viewport), the sheet bar's actions on the board bar, the SVG print with each frame's drawing clipped inside it; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-19 [Claude] The records

PIPELINE row 175c, Notion.
