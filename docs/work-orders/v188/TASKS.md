# V188 work orders: Freeform F6, picture planes, text objects, flow along a surface

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/drawing/flow-picture.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v188/v188.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v188/v188.test.mjs
    node --check src/js/engine/drawing/flow-picture.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimPicPlane(wPx, hPx, widthM)`

- **It must:** SPEC 5 WO-01: null unless all three are positive; h = widthM hPx / wPx; {w, h, corners [[0,0],[w,0],[w,h],[0,h]], uv [[0,1],[1,1],[1,0],[0,0]]}.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/flow-picture.js`, `docs/work-orders/v188/v188.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v188/v188.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimTextBox(lines, h, ratio, gap)`

- **It must:** SPEC 5 WO-02: ratio 0.6 and gap 1.2 unless positive; {w: longest line's length * h * ratio, h: h + (lines - 1) h gap}; {w: 0, h: 0} for no lines or h not above 0.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/flow-picture.js`, `docs/work-orders/v188/v188.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v188/v188.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimFlowBox(pts)`

- **It must:** SPEC 5 WO-03: [minX, minY, maxX, maxY] of the points' first two coordinates; null for none.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/flow-picture.js`, `docs/work-orders/v188/v188.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v188/v188.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimFlowBilinear(q, u, v)`

- **It must:** SPEC 5 WO-04: (1-u)(1-v) q0 + u(1-v) q1 + u v q2 + (1-u) v q3, per coordinate.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/flow-picture.js`, `docs/work-orders/v188/v188.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v188/v188.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimFlowMap(pts, box, q)`

- **It must:** SPEC 5 WO-05: each point [x, y, z]: u, v its place in the box; the patch point plus the unit normal (dP/du cross dP/dv, the bilinear partials: du = (1-v)(q1-q0) + v(q2-q3), dv = (1-u)(q3-q0) + u(q2-q1)) times z. null when the box has no width or height.
- **May use:** bimFlowBilinear (WO-04).
- **Files:** `src/js/engine/drawing/flow-picture.js`, `docs/work-orders/v188/v188.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v188/v188.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-06 [Claude] Picture, Text and Flow commands

Claude's: the commands, the image kept with the project, flow onto F2's surfaces by their nearest patch; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 188, Notion.
