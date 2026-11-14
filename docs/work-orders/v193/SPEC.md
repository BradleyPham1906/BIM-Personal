# LOD-F: LOD3 openings on rectified facades (outline)

Notion: V191 LOD-F: LOD3 openings. PIPELINE: 193. Research: `docs/research/research-notion-v191-openings.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

After V192. Its first slice can be ordered in the same sprint as V192's.

## 1. The owner's decisions, 2026-11-14, as recommended

- openings drawn by hand first, rectangular only; rows and columns regularised on request, never silently;
- machine proposals (Segment Anything in the browser, Apache-2.0) only later, on request, each one confirmed by the owner, after its own research under the library rule;
- an approved opening is cut into the wall with the app's existing opening code and keeps its source image, its transform and its error.

## 2. What it does for the user

On a rectified facade, draw windows and doors; Regularise lines up their sills, heads and centres; Apply cuts them into the wall as real openings.

## 3. The first slice (pure functions in `src/js/engine/bim/facade-openings.js`, ES5, no other file's names)

- `bimOpnCluster(values, tol)`: one-dimensional clusters of sills, heads or centres within tol, each with its mean.
- `bimOpnRegularise(rects, tol)`: each rectangle moved to its clusters' means, with how far each moved.
- `bimOpnOverlap(rects)`: pairs of openings that overlap, to refuse them.
- `bimOpnToWall(rect, frame)`: a rectangle in facade metres as the app's opening (centre along the wall, sill, width, height).

Tests: Rectangles placed in known rows and columns with jitter: regularised back within tol; overlaps found.

## 4. Not in this phase

Non-rectangular openings; automatic detection; depth and reveals.
