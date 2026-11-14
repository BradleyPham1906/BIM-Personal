# Streaming: OGC 3D Tiles (outline)

Notion: Later: Streaming. PIPELINE: later (after the LOD track). Research: `docs/research/research-notion-streaming-3d-tiles.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

After LOD-D. Spec sprint then; the renderer library (NASA's 3DTilesRendererJS, Apache-2.0) is a library-rule decision.

## 1. The owner's decisions, 2026-11-14, as recommended

- read-only reference tiles first (a tileset shown around the site), export later;
- one named public tileset with its licence as the first fixture;
- inside the rendered view (three.js, V194), not a separate viewer;
- offline: tiles already seen are cached by the browser only; nothing promised offline.

## 2. What it does for the user

Show a city's 3D Tiles around the site in the rendered view, loading what is in view.

## 3. The first slice (pure functions in `src/js/engine/map/tiles3d.js`, ES5, no other file's names)

- `bimTilesSse(geometricError, distance, height, fovY)`: the screen-space error in pixels.
- `bimTilesBoxDistance(box, eye)`: the distance from the eye to an oriented bounding box.
- `bimTilesSelect(tileset, eye, maxSse)`: the tiles to draw by refinement (REPLACE or ADD), as 3D Tiles 1.1 defines.

Tests: Hand-computed SSE and distances; a small tileset JSON with both refinements.

## 4. Not in this phase

Writing tiles; implicit tiling; metadata styling.
