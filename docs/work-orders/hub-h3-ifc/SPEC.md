# Hub H3: full IFC (outline)

Notion: Later: Hub H3: full IFC. PIPELINE: later. Research: `docs/research/research-notion-hub-h3-ifc.md`, `docs/research/research-ifc-engine.md`, `docs/research/research-thatopen.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Folded into V177 (Save as IFC) and the That Open phase (IFC import and Review). What is left is H3's identity rule, written into those specs; no separate Cline work.

## 1. The owner's decisions, 2026-11-14, as recommended

- reference-only first (imported IFC elements read-only with their GlobalId), semantic editing after That Open (V177's D3);
- the source IFC kept beside the project up to 50 MB, its GUIDs on every element so H1's diffs are IFC diffs;
- IFC4 Reference View as the first model view; IFC2x3 and 4.3 read, IFC4 written.

## 2. What it does for the user

Every IFC element keeps its GlobalId from import to export, so the history and the hub compare IFC elements by identity.

## 3. The first slice (pure functions in `src/js/engine/io/ifc-guid.js`, ES5, no other file's names)

- `bimIfcGuidValid(s)`: a 22-character IFC GUID in IFC's base-64 alphabet.
- `bimIfcGuidNew()`: a new GUID: 128 random bits in IFC's encoding.
- `bimIfcGuidMap(objs)`: duplicate and missing GUIDs across the model.

Tests: IFC's own GUID examples; collisions found.

## 4. Not in this phase

A second ifc engine; validation against buildingsmart's service (an upload).
