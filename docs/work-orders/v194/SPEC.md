# V194 spec: the rendered view

Research: `docs/research/research-rendered-view.md`. Branch: `render-r6`. Written by Claude, 2026-11-12.
Built by Claude at the owner's word ("write the code into the app"); rendering and `render/` are tier D in
`../ROUTING.md`. TASKS.md lists what is done and the follow-ups a first pass can take.

## 1. What it does for the user

`RENDER`, or Properties > View > Display > Rendered, shows the model in daylight: the sun and the sky, soft
shadows, see-through glass, a ground. The first picture is at once; it sharpens over a second while the view is
still. Drawing, selecting, dimensions and Save image work as before. `RENDER` again gives the shaded view.

## 2. The pieces

| File | New or changed | What it holds |
|---|---|---|
| `runtime/three/0.186.1/` | new | three.js as one classic script, its licence |
| `tools/three/` | new | the script that builds and pins it |
| `src/js/engine/render/rendered-core.js` | new | the picture: skies, sampling, `bimRvCore(T,canvas,opts)` |
| `src/js/engine/render/rendered-scene.js` | new | the model as arrays, the camera, the sun |
| `src/js/engine/render/rendered-view.js` | new | loading, the frame, settings, Properties rows, the command |
| `render/webgpu.js`, `map/terrain-3d.js`, `site/shadows.js`, `ui/zoom-window-save-image.js`, `drawing/sketch-constraints.js`, `commands/command-map.js`, `shell/shell.js`, `ui/build-ui.js`, `site-analysis/panel.js`, `testing/hooks-drawing.js`, `css/workspace/engine-chrome.css`, `src/index.html` | changed | one hook each |
| `tests/unit/rendered.test.mjs` | new | 20 tests |

## 3. Data

- Settings, this browser's, `localStorage['acad3dRenderedV1']`: `{sky:'clear'|'overcast'|'dusk'|'white',
  ground:true, edges:false, quality:'draft'|'good'|'best'}`. The view itself is never kept on.
- A part of the picture: `{key, sig}`; its arrays `{op:{pos,col,n}, tr:{pos,col(rgba),n}, ed:{pos,n}}`, world
  metres, linear colours.
- A picture: `{world, proj, focus, reach, sun|null, sky, ground, groundAt, edges}`.

## 4. Functions

Each is described where it is declared. The seam: `bimRvPlan(edges)` and `bimRvBuild(plan,item)` (scene),
`bimRvCore(T,canvas,opts)` -> `{size, scene, begin, pass, show, stats, dispose}` (core),
`bimRvRender(V,W,H)` -> true when the picture is what is seen (view).

## 5. Order of the work

Done in one piece. To try it: open a model in 3D, type RENDER.

## 6. Not in this phase

The basemap and draped terrain; sheets and Present; materials by element type; textures; lamps; glTF; IFC.
