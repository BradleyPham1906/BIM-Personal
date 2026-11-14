# V218 spec: Streaming: OGC 3D Tiles

Notion: Later: Streaming. Research: `docs/research/research-notion-streaming-3d-tiles.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Read-only reference tiles first, shown around the site in the rendered view (V194's three.js); export later.
- One named public tileset with its licence as the first fixture; NASA's 3DTilesRendererJS (Apache-2.0) only under the library rule, after this slice's own selection logic is proven.
- Bounding spheres first; boxes and regions with Claude's wiring. Refinement as 3D Tiles 1.1 defines it (REPLACE and ADD).
- Offline: tiles already seen are cached by the browser only; nothing promised offline.

## 2. What it does for the user

Add a 3D Tiles source: the city around the site streams into the rendered view, finer as the camera comes closer.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/map/tiles3d.js` | new, after `js/engine/map/facade-rectify.js` in `src/index.html` (header done) | 3 pure functions (part 5) | Cline, WO-01 to WO-03 |
| `docs/work-orders/v218/v218.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-04, WO-05 |

## 5. Functions, `src/js/engine/map/tiles3d.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimTilesSse(ge, dist, h, fov)`**: ge h / (2 dist tan(fov / 2)); Infinity when dist is not positive.
- **WO-02 `bimTilesDist(sphere, eye)`**: the distance from the eye to the sphere [x, y, z, r]'s surface, 0 inside.
- **WO-03 `bimTilesSelect(tile, eye, h, fov, maxSse, parentRefine)`**: a tile whose error is within maxSse, or with no children, gives its content uri (when it has one); else ADD tiles (refine inherited from the parent, REPLACE by default) give their own uri and then their children's, REPLACE tiles only their children's, depth first in order.

## 6. Order of the work

WO-01 to WO-03 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-04** tiles in the rendered view; **WO-05** the records.

## 7. Not in this phase

Writing tiles; implicit tiling; metadata styling.
