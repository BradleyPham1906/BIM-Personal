# V207 spec: glTF models in Assets, and valdrada's credited models

Notion: Later: Model import: glTF, and valdrada's credited models. Research: `docs/research/research-notion-gltf-assets.md`, `docs/research/research-gltf.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- glTF and GLB go into Assets as placeable models through V195's reader (three.js GLTFLoader), materials as colours with any loss listed, sizes kept, seated on the origin.
- A model over 200,000 triangles or 20 MB asks before it is added.
- valdrada's vehicles (CC BY 4.0) converted to V169's kinds with their dimensions, each credited on its card and in THIRD_PARTY_NOTICES.md; its generator code (MIT) is a reference for V171, not imported.

## 2. What it does for the user

Drag a .glb onto Assets: it becomes a model card with its counts and credit, placed by click like any asset; the credited vehicle set appears in Assets.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/assets/gltf-assets.js` | new, after `js/engine/assets/library-drag.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v207/v207.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/assets/gltf-assets.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimAstGltfStats(g)`**: null unless an object; {meshes, primitives, triangles, materials, textures, extensions (extensionsUsed sorted)}: triangles summed over primitives of mode 4 or no mode, floor(count / 3) of the indices accessor, else of the POSITION accessor.
- **WO-02 `bimAstFitBox(min, max, size)`**: s = size / the largest extent when both are positive, else 1; {scale: s, move: [-(minX + maxX)/2 s, -minY s, -(minZ + maxZ)/2 s] (written so 0 stays 0, never -0), size: the extents times s}.
- **WO-03 `bimAstCheck(stats, bytes, limits)`**: messages: no stats ['not a glTF file']; triangles over limits.triangles (200000 by default): 'N triangles, over T'; bytes over limits.bytes (20 MB, 20971520): 'X MB, over Y MB', MB to one decimal.
- **WO-04 `bimAstCredit(e)`**: '"title" by author, license (source)', each part only when present; 'Untitled' without a title.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** gltf models in assets; **WO-06** the records.

## 7. Not in this phase

Animations and skins; textures beyond the base colour; valdrada's generator code.
