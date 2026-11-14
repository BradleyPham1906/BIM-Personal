# V184 work orders: Freeform F2, surfaces from curves

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/drawing/surfaces.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v184/v184.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v184/v184.test.mjs
    node --check src/js/engine/drawing/surfaces.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimSrfGrid(rows, cols, closeU)`

- **It must:** SPEC 5 WO-01: quads [a, b, b + cols, a + cols] with a = j*cols + i and b = j*cols + (i+1) % cols, for j < rows - 1 and i < cols - 1 (i < cols when closeU).
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/surfaces.js`, `docs/work-orders/v184/v184.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v184/v184.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimSrfExtrude(pts, vec)`

- **It must:** SPEC 5 WO-02: {v: the points then the points moved by vec, f: bimSrfGrid(2, n, false)}; null for fewer than 2 points.
- **May use:** bimSrfGrid (WO-01).
- **Files:** `src/js/engine/drawing/surfaces.js`, `docs/work-orders/v184/v184.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v184/v184.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimSrfRotate(p, o, ax, a)`

- **It must:** SPEC 5 WO-03: p turned by a radians about the axis through o along ax (normalised), by Rodrigues' formula: x c + (k cross x) s + k (k dot x)(1 - c), x = p - o, plus o.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/surfaces.js`, `docs/work-orders/v184/v184.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v184/v184.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimSrfRevolve(pts, o, ax, angle, segs)`

- **It must:** SPEC 5 WO-04: segs (24 when under 1) steps; rings j = 0 .. segs (only 0 .. segs - 1 for a full turn, |angle| within 1e-9 of 2 pi) of the profile turned by angle j / segs; faces [a, a+1, b+1, b] with a = j n + i, b = ((j+1) % rings) n + i for j < segs, i < n - 1. null for fewer than 2 points.
- **May use:** bimSrfRotate (WO-03).
- **Files:** `src/js/engine/drawing/surfaces.js`, `docs/work-orders/v184/v184.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v184/v184.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-05 [Cline] `bimSrfLoft(a, b, rows)`

- **It must:** SPEC 5 WO-05: rows (1 when under 1) + 1 interpolated rings from a to b, faces by bimSrfGrid(rows + 1, n, false); null unless both have the same count, 2 or more.
- **May use:** bimSrfGrid (WO-01).
- **Files:** `src/js/engine/drawing/surfaces.js`, `docs/work-orders/v184/v184.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v184/v184.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Cline] `bimSrfCoons(c0, c1, d0, d1)`

- **It must:** SPEC 5 WO-06: the bilinear Coons patch: c0 (v = 0) and c1 (v = 1) with m points, d0 (u = 0) and d1 (u = 1) with k points, corners shared; vertex (j, i) with u = i/(m-1), w = j/(k-1): (1-w) c0[i] + w c1[i] + (1-u) d0[j] + u d1[j] minus the bilinear blend of the four corners; faces bimSrfGrid(k, m, false). null for mismatched counts or fewer than 2.
- **May use:** bimSrfGrid (WO-01).
- **Files:** `src/js/engine/drawing/surfaces.js`, `docs/work-orders/v184/v184.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v184/v184.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-07 [Claude] The surface commands

Claude's: Extrude, Revolve, Loft and Edge surface on curves, the surface object keeping its curves and rebuilding; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-08 [Claude] The records

PIPELINE row 184, Notion.
