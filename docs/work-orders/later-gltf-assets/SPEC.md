# Model import: glTF assets and valdrada's credited models (outline)

Notion: Later: Model import: glTF, and valdrada's credited models. PIPELINE: later. Research: `docs/research/research-notion-gltf-assets.md`, `docs/research/research-gltf.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Next spec sprint for the Assets part; V195 already imports and exports glTF.

## 1. The owner's decisions, 2026-11-14, as recommended

- glTF and GLB go into Assets as models (V195's reader), materials as colours with any loss listed, sizes kept;
- valdrada's vehicles (CC BY 4.0) converted to V169's kinds with their dimensions, credited in THIRD_PARTY_NOTICES.md; its generator code (pedestrians, trees, MIT) read for V171's walk cycle, not imported;
- a model over 200,000 triangles or 20 MB asks before it is added.

## 2. What it does for the user

Drag a .glb into Assets: it becomes a placeable model with its preview; the credited vehicle set appears in Assets.

## 3. The first slice (pure functions in `src/js/engine/assets/gltf-assets.js`, ES5, no other file's names)

- `bimAstGltfStats(gltf)`: triangles, meshes, materials, textures and the extensions used, from a parsed glTF's JSON.
- `bimAstFitBox(box, target)`: the uniform scale and move that seat a model's box on the origin, its size kept or set.
- `bimAstCredit(entry)`: the credit line from an asset's author, title, licence and source.

Tests: Parsed glTF JSON fixtures written in the test.

## 4. Not in this phase

Animations; skins; textures beyond the base colour.
