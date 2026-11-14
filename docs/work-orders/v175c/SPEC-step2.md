# V175c spec: One paper space, steps 2 and 3: one editor, one print

Notion: V175c One paper space. Research: `docs/research/research-one-paper-space.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- The owner's D1 to D8 (2026-11-12) as recommended, in SPEC.md. Step 2: the board's map frame becomes the one viewport object; a sheet opens as a layout of a title block and one frame per viewport, its number and tab kept; a layout marked drawing sheet keeps live values, figures and charts out of its Draw menu (D4).
- Step 3: a layout prints as one SVG of its objects and frames at its page size, in millimetres, replacing the sheet's canvas print and the board's HTML print.

## 2. What it does for the user

Every layout, sheet or board, is edited in one editor with the same viewports and prints as one vector page.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/sheets/layout-merge.js` | new, after `js/engine/sheets/layouts.js` in `src/index.html` (header done) | 7 pure functions (part 5) | Cline, WO-11 to WO-17 |
| `docs/work-orders/v175c/v175c-step2.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-18, WO-19 |

## 5. Functions, `src/js/engine/sheets/layout-merge.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-11 `bimLmVpToFrame(vp)`**: a sheet viewport {id, kind, refId, label, x, y, w, h, scaleMode, scaleDenom} as the map frame {t: 'map', id, x, y, w, h, src: kind + ':' + refId, den: scaleDenom (null when scaleMode is 'fit'), fit: scaleMode === 'fit', px: 0, py: 0, label (or '')}.
- **WO-12 `bimLmFrameToVp(fr)`**: the inverse: kind before the first ':' of src, refId after it ('' when none); scaleMode 'fit' when fr.fit or den is not positive, else 'fixed'; scaleDenom den when positive, else 100; the keys in the order id, kind, refId, label, x, y, w, h, scaleMode, scaleDenom.
- **WO-13 `bimLmSheetToLayout(sh)`**: {id, num: number or '', name or '', w, h, drawing: true, objs: [{t: 'tblock', id: 'tb-' + id, x: 0, y: 0, w, h}, then a frame (WO-11) per viewport]}.
- **WO-14 `bimLmDrawMenu(items, drawing)`**: the items, leaving out those of kind 'live', 'figure' or 'chart' when drawing is true (the owner's D4).
- **WO-15 `bimLmN(v)`**: v rounded to 3 decimals as a string, '0' for any rounded zero.
- **WO-16 `bimLmSvgOpen(w, h)`**: '<svg xmlns="http://www.w3.org/2000/svg" width="Wmm" height="Hmm" viewBox="0 0 W H">' with W, H by WO-15.
- **WO-17 `bimLmSvgRect(o, stroke, width)`**: '<rect x=".." y=".." width=".." height=".." fill="none" stroke="S" stroke-width="W"/>', numbers by WO-15, stroke '#000000' and width 0.25 by default.

## 6. Order of the work

WO-11 to WO-17 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-18** one editor and one print in the app; **WO-19** the records.

## 7. Not in this phase

A new title block designer; pdf without the browser's print.
