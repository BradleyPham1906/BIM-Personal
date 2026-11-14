# Water and presentation rendering (outline)

Notion: Later: Water and presentation rendering. PIPELINE: later. Research: `docs/research/research-notion-later-water-presentation.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Spec sprint after the rendered view's materials (V194 T-07) are wired.

## 1. The owner's decisions, 2026-11-14, as recommended

- ponds only first, as a visual layer; flooding only as a display of results validated elsewhere, with a visible disclaimer;
- a still image first; animation is an option;
- falls back to flat water where the GPU cannot;
- caustics and refraction as separate, optional milestones; Evan Wallace's techniques (MIT) written ourselves.

## 2. What it does for the user

Ponds in the rendered view with a moving surface, reflections and soft shadows.

## 3. The first slice (pure functions in `src/js/engine/render/water-sim.js`, ES5, no other file's names)

- `bimWaterStep(h, v, n, damping)`: one step of the heightfield wave equation on an n by n grid.
- `bimWaterDrop(h, n, x, y, r, s)`: a drop added to the heightfield.
- `bimWaterNormals(h, n, cell)`: the surface normals.

Tests: Energy and symmetry checks on a small grid; the research's CPU fixture's numbers.

## 4. Not in this phase

Hydraulic flood modelling; exports of animations.
