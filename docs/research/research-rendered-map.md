# V198: the map and the draped terrain in the rendered view

Research and build, 2026-11-12. Levels as in `research-protocol.md`: P primary, S secondary, U a pointer only.

## 1. The question

The owner's fourth of five after V194 (2026-11-12): the basemap the shaded view shows on the ground (V132) and draped
on a terrain (V137) should also be in the rendered view (V194). Until now the rendered view drew a plain ground disc
and terrain in a flat colour (V194's note, "not rendered yet").

## 2. What the app already had (P, this repository at 9fd633d)

- `map/map-tiles.js`: `bimMapPlan(V,W,H)` picks the view's tiles (zoom from metres per pixel, at most 80 a screen);
  `bimMapSource` gives a tile or, while it loads, the part of a parent; `A3D_MAP` is the tile store (CORS-requested
  images, a 400-tile least-recently-drawn cache). `bimMapTileCorners` puts a tile's corners on the model with the
  site's latitude, longitude and true north.
- `map/terrain-3d.js`: `bimTerrainMeshData` gives each terrain triangle corner its Web Mercator place at zoom 22;
  `bimDrapeTiles` picks the tiles over a terrain (at most 36); the shaded view draws each tile over the whole surface
  and discards outside it.
- `render/webgpu.js:393`: when the rendered view draws, `bimRender3D` returns before WebGL, so **none of the map's
  own frame runs**: no tile was asked for, the store's clock did not move, nothing was evicted, `A3D.lastMapDrawn`
  went stale. The rendered view has to do all four itself (found reading the code, confirmed by the advisor).
- `render/rendered-core.js`: three.js 0.186.1, `MeshStandardMaterial`, a shadowed sun and sky, a ground disc.

## 3. Hypotheses

- H1: the shaded view's tiles, store and credit can be reused unchanged, so the rendered view asks the tile server for
  nothing more. **Held**: the same plan; the browser check served 79 tiles for 5 cases in both views.
- H2: one canvas per surface (the tiles side by side, an atlas) is enough for both the ground and a terrain, with no
  shader of our own. **Held**: a terrain corner's u, v is its Mercator place over the atlas's tile rectangle; a tile's
  square on the ground maps to its cell.
- H3: tiles and parents placed this way land exactly where the shaded view puts them, the same way round, also when
  the site is turned by true north. **Held**: browser check, colour classes compared pixel by pixel: 100.0% agree in
  plan, in 3D, at 30 degrees true north and draped (about 38,000 samples each).
- Counter-case found in the browser: the map on the ground, tested against the ground disc 1e-4 of the reach below it,
  lost the depth test at low angles (white streaks, `3d-ground` case, first run). Fixed by drawing it after the sky and
  the disc and before the model, neither testing nor writing depth, as the shaded view does. Second finding: the
  ground's fog faded the map toward the horizon, which the shaded view does not; the map does not fog.

## 4. Sources (P unless said)

- three.js r186 `src/textures/Texture.js` (in `tools/three/node_modules`, the pinned build's source): the default
  colour space is `NoColorSpace` (a map must say `SRGBColorSpace`, or it is washed out against the hand-linearised
  vertex colours); `flipY` defaults to true (set false: the canvas's top row is v = 0, the north of the tiles).
- The app's own code as listed in part 2.
- Tile servers' terms and credit: unchanged from V132/V133 (the credit line in the footer is drawn whatever engine
  draws the picture: `bimMapFooterSync`, `terrain-3d.js:367`).

## 5. Alternatives

| | One texture per tile | One atlas per surface (chosen) | A custom shader with per-tile discard (as the shaded view) |
|---|---|---|---|
| Ground | 80 meshes, 80 textures | 1 mesh, 1 texture | 80 draws |
| Terrain | needs clipping per tile | per-vertex u, v from Mercator | the surface drawn once a tile |
| Store eviction | must free textures from under the picture | the canvas is a copy | as tiles |
| three.js lighting and shadows | yes | yes | must be rewritten |

## 6. Decisions (recorded, not asked)

The owner asked for this step plainly; the choices left are technical and are recorded here, as the owner's rule
"do what best means decide and record" says.

- The map is lit by the site's sun and sky and takes the model's shadows (a render, not the photo as it is).
- The same tiles and zoom as the shaded view: no extra requests to a free server.
- Opacity mixes toward the colour under the map (the ground disc's, or the terrain's own); in the Analyze workspace's
  look the ground map is grey and faded and the terrain plain, as in the shaded view. None under plot by layer.

## 7. As built

- `render/rendered-map.js` (no three.js; Node tests it): the frame's map (`bimRvMapFrame`: plan, sources, record as
  `'rendered'`, eviction), the atlas layout, the ground's squares and the drape's u, v, the canvas.
- `render/rendered-scene.js`: `bimRvPlan(edges, view)` adds the ground map item and a terrain's drape; the signature
  is the tile list with what stands for each, the opacity, the look, the ground's height and the site's place, so the
  picture is begun again as tiles arrive and not when the camera only orbits inside the same tiles.
- `render/rendered-core.js`: a map mesh (`CanvasTexture`, sRGB, not flipped, the device's anisotropy, at most 4096
  pixels, 2048 on a phone); its material and texture freed with it. Sky -3, ground disc -2, ground map -1.

## 8. Checks

`npm test` 229 of 229 (5 new: layout and parents, the frame and the store, the signature, the drape against the
Mercator formulas, the frame against the three.js stand-in). Browser: `tests/e2e/bim_phase198_rendered_map_check.mjs`,
Edge 157 headless, 12 of 12, no console errors.

## 9. Open

- While panning, each new set of tiles rebuilds the atlas (a few MB uploaded); a phone may stutter while it moves.
- A selected terrain under the map shows no selection colour (as in the shaded view).
- Sheets and Present still use the shaded view.

## 10. Confidence

High for placement (measured pixel by pixel against the shaded view). Medium for the look on real imagery: the
check used synthetic tiles; the owner's eye on a real satellite site is the remaining test.
