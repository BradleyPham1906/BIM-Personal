# V188 spec: Freeform F6, picture planes, text objects, flow along a surface

Notion: V183-V189 Freeform (F1-F7). Research: `docs/research/research-freeform-f1-f7.md`, `docs/research/research-rhino-guide-gap.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- A picture plane is a rectangle at the image's aspect, sized by the owner's width, its image kept in the project (the owner's file, never uploaded).
- Text objects are boxes of the app's own drafting font, sized by height and a 0.6 width ratio, lines at 1.2 by default; outlined 3D text waits for a font with an open licence, under the library rule.
- Flow along a surface maps objects from a base rectangle in plan onto a four-cornered patch (bilinear), their height along the patch normal; patches from F2's surfaces come with Claude's wiring.

## 2. What it does for the user

Place a photo or sketch as a picture plane to trace over; place text objects in the model; flow a pattern or text from a flat base onto a curved patch.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/drawing/flow-picture.js` | new, after `js/engine/drawing/nurbs-edit.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v188/v188.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 5. Functions, `src/js/engine/drawing/flow-picture.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimPicPlane(wPx, hPx, widthM)`**: null unless all three are positive; h = widthM hPx / wPx; {w, h, corners [[0,0],[w,0],[w,h],[0,h]], uv [[0,1],[1,1],[1,0],[0,0]]}.
- **WO-02 `bimTextBox(lines, h, ratio, gap)`**: ratio 0.6 and gap 1.2 unless positive; {w: longest line's length * h * ratio, h: h + (lines - 1) h gap}; {w: 0, h: 0} for no lines or h not above 0.
- **WO-03 `bimFlowBox(pts)`**: [minX, minY, maxX, maxY] of the points' first two coordinates; null for none.
- **WO-04 `bimFlowBilinear(q, u, v)`**: (1-u)(1-v) q0 + u(1-v) q1 + u v q2 + (1-u) v q3, per coordinate.
- **WO-05 `bimFlowMap(pts, box, q)`**: each point [x, y, z]: u, v its place in the box; the patch point plus the unit normal (dP/du cross dP/dv, the bilinear partials: du = (1-v)(q1-q0) + v(q2-q3), dv = (1-u)(q3-q0) + u(q2-q1)) times z. null when the box has no width or height.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** picture, text and flow commands; **WO-07** the records.

## 7. Not in this phase

3d outlined text; flow onto trimmed surfaces; image editing.
