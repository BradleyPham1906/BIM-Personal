# V194 work orders

Spec: `SPEC.md` in this folder. Branch: `render-r6`. `[x]` done (its required checks pass), `[ ]` open.

## [x] T-01 [Claude] three.js as a pinned runtime (`tools/three`, `runtime/three`, the manifest)
## [x] T-02 [Claude] The picture (`render/rendered-core.js`), tried in experiment e01
## [x] T-03 [Claude] The model as arrays, the camera, the sun (`render/rendered-scene.js`)
## [x] T-04 [Claude] Loading, the frame, settings, Properties, RENDER (`render/rendered-view.js`) and the hooks
## [x] T-05 [Claude] Unit tests (`tests/unit/rendered.test.mjs`), modules, the build, `npm run check`

## [ ] T-06 [Claude] The app's own browser check

- Needs the owner's word (Rule #1). Load the build over http, draw a few elements, `window.__a3dRendered(true)`,
  report the console and one picture; then Save image, a selection, a layer turned off, plan view, RENDER off.

## [ ] T-07 [Cline] Looks by element type in `src/js/engine/render/rendered-scene.js`

- **Add** `bimRvLook(o)`: returns `'glass'` for an object whose `bim.type` is `'window'`, `'metal'` when its
  material name matches `/steel|metal|alumin/i`, else `'matte'`.
- **Test:** a new case in `tests/unit/rendered.test.mjs` for each of the three results.
- **Do not** change `rendered-core.js`: Claude wires the look into the materials after review.
- **Score:** 0+0+1+0+0+0 = 1, tier B

## [x] T-08 [Claude] The basemap and the map draped on a terrain, in the rendered view
## [x] T-09 [Claude] glTF and GLB in and out (the next phase; research first)
