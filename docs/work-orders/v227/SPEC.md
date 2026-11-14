# V227 spec: Track D, the drone bridge project: flight planning

Notion: Parked: Tracks C and D. Research: `docs/research/research-bridge-splatting.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Photogrammetry stays outside the app (Pix4D, iTwin Capture, WebODM or OpenSplat); the app plans before and places after: ground sample distance, the height for a target GSD, footprints, spacing for overlap, flight lines.
- Camera numbers are the owner's drone's (for example a 13.2 by 8.8 mm sensor, 8.8 mm lens, 5472 px wide); 80% forward and 70% side overlap by default.
- Results come back as splats (V205) or meshes placed on the site.

## 2. What it does for the user

Plan a bridge capture: pick the drone's camera, a target GSD and the overlap; the app gives the height, the photo spacing and the flight lines over the bridge's footprint.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/site/drone-plan.js` | new, after `js/engine/site/field-guide.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v227/v227.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 5. Functions, `src/js/engine/site/drone-plan.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimDpGsd(sw, f, iw, h)`**: sensor width mm, focal length mm, image width px, height m: sw h 100 / (f iw) cm per pixel; null unless all positive.
- **WO-02 `bimDpHeight(gsd, sw, f, iw)`**: the inverse: gsd f iw / (sw 100) m; null unless gsd, sw and iw are positive.
- **WO-03 `bimDpFootprint(sw, sh, f, h)`**: {w: sw h / f, h: sh h / f} in metres; null unless f is positive.
- **WO-04 `bimDpSpacing(len, overlap)`**: len (1 - overlap) for 0 <= overlap < 1, else null.
- **WO-05 `bimDpLines(width, spacing)`**: ceil(width / spacing - 1e-9) + 1; null unless spacing is positive.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** the capture planner; **WO-07** the records.

## 7. Not in this phase

Photogrammetry in the app; flying the drone; nstm inspection judgments.
