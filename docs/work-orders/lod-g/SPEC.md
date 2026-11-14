# LOD-G: Gaussian splats as a backdrop (outline)

Notion: V192 LOD-G: Gaussian splats. PIPELINE: 200 (its number is shared with V200, the 2D draw-order fix; renumber with WO-03). Research: `docs/research/research-notion-v192-splats.md`, `docs/research/research-bridge-splatting.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Spec sprint after the rendered view's materials (V194 T-07) are wired; the viewer is a library decision.

## 1. The owner's decisions, 2026-11-14, as recommended

- a visual-only, isolated layer: never converted to BIM geometry, never measured from, left out of exports unless the owner ticks it;
- the antimatter15 `.splat` format first (32 bytes a splat); its viewer ported or vendored only after its MIT licence and dependencies are read, under the library rule;
- placed by the owner (move, turn, scale with three point pairs), labelled with its placement error;
- a size limit measured on the owner's phone before it is set.

## 2. What it does for the user

Import a .splat capture; it shows as a photoreal backdrop in the rendered view, on its own layer, to trace against.

## 3. The first slice (pure functions in `src/js/engine/render/splats.js`, ES5, no other file's names)

- `bimSplatParse(bytes)`: the splats of a .splat file: position and scale (float32 x3 each), colour (uint8 x4), rotation (uint8 x4 as a quaternion); an error when the length is not a multiple of 32.
- `bimSplatBounds(splats)`: the bounding box and centre.
- `bimSplatFit3(src, dst)`: the similarity transform (scale, rotation, move) from three or more point pairs (Umeyama), with its RMS.
- `bimSplatOrder(splats, eye)`: indices sorted back to front from the eye.

Tests: A file of known splats written byte by byte; a known transform recovered.

## 4. Not in this phase

Training splats; editing splats; splats in sheets and prints.
