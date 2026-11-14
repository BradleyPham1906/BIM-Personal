# Generators: massing, parking, subdivision (outline)

Notion: Later: Generators. PIPELINE: later. Research: `docs/research/research-later-generators.md`, `docs/research/research-giraffe.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Next spec sprint: the arithmetic is pure; massing in V160's envelope reuses its code.

## 1. The owner's decisions, 2026-11-14, as recommended

- massing fills V160's zoning envelope to the achievable area: storeys from its height and a floor-to-floor the owner sets (3.5 m by default), plates from its floors, tagged by usage so the yield and checks follow;
- parking by a ratio per usage the owner enters (none shipped as law), stalls 2.6 by 5.5 m and aisles 7.2 m by default, all editable;
- subdivision into lots by a target frontage and depth; never claimed as a legal subdivision.

## 2. What it does for the user

Generate a massing that fills the zoning envelope, a parking layout to a ratio, and lots along a street.

## 3. The first slice (pure functions in `src/js/engine/site-tools/generators.js`, ES5, no other file's names)

- `bimGenStoreys(envelopeHeight, ftf)`: how many storeys fit and the top height.
- `bimGenStalls(area, ratio, units)`: the stalls the ratio asks for.
- `bimGenParkingRows(width, depth, stall, aisle)`: rows of 90-degree stalls along double-loaded aisles that fit a rectangle.
- `bimGenLots(frontage, depth, target)`: lot widths along a frontage, the remainder spread evenly.

Tests: Hand-worked layouts.

## 4. Not in this phase

Optimisation; non-rectangular parking fields in the first slice.
