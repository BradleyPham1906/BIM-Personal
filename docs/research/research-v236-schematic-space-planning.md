# V236 — Schematic space planning

## Decision and verdict

**Question:** How should approved program diagrams become scaled schematic plans without pretending to automate architectural authorship?  
**Verdict:** Use a staged, inspectable planning pipeline: allocate zones, place scaled blocks, establish levels and cores, route conceptual circulation, then derive floor-plate and massing studies. Preserve fixed designer decisions and report unsatisfied constraints. Do not promise a construction-ready floor plan.

## Evidence

RIBA Stage 2 develops an Architectural Concept aligned with site information, the brief, spatial requirements and adjacency requirements. Stage 3 then tests and spatially coordinates that concept; it is not intended to reinvent it.[^https://www.riba.org/media/syneeeto/2020ribaplanofworkoverviewpdf.pdf]

RAIC describes schematic design as testing the program through space, circulation and massing studies. Alternatives should remain quick diagrammatic studies and be compared on program, adjacency, sustainability and net/gross efficiency.[^https://chop.raic.ca/chapter-6.2]

The AIA schematic-design checklist expects major plan elements, cores, preliminary structure and MEP spaces, circulation, site access and representative dimensions to be developed and checked against program requirements.[^https://www.aia.org/sites/default/files/2024-12/BestPractices_12.03.01_SchematicDesign_checklist.pdf]

Anthropocity's layout view shows a useful bounded precedent: scaled rooms, corridors, stairs, entrances and doors update from the graph, but the product explicitly calls the result a planning aid rather than a construction drawing.[^https://anthropocity.com/docs/layout-view]

## Proposed planning pipeline

1. **Feasibility envelope:** site/buildable area, floor count assumptions and gross target.
2. **Zone allocation:** departments and security/service zones by building and level.
3. **Scaled block placement:** target-area rectangles or simple polygons with tolerances.
4. **Core reservation:** stairs, lifts, toilets, shafts and major service rooms.
5. **Concept circulation:** main routes, loops, access spurs and vertical transitions.
6. **Floor-plate study:** outline, depth, grid compatibility and net/gross calculation.
7. **Massing study:** stack levels and site placement; no façade detail.
8. **Constraint report:** satisfied, violated, waived and unresolved requirements.

## Solver strategy

Avoid one opaque optimizer. Use deterministic heuristics where possible, seeded sampling for alternatives and pattern search for refinement. A treemap can create area-fit rectangles but cannot guarantee adjacency or circulation, so it may be an initial allocation only.[^https://app.notion.com/p/419cbfcc3a388166aaf4f10da9849507]

Every generated object should use V228 stable keys. Users may mark zones, spaces, cores or outlines as fixed, adaptive or manually overridden. Regeneration updates in place and parks invalid overrides for review.

## Acceptance criteria

- A 10–20-space single-level reference program can generate multiple reproducible studies.
- Target area, actual area and variance are shown for every space and total.
- Hard constraints are either satisfied or explicitly reported—not hidden in a score.
- Main circulation reaches every required space or lists failures.
- Fixed elements remain fixed across regeneration.
- Identical seed, inputs and version reproduce the same result.
- The user can move, resize or reassign a space and rerun only affected stages.
- Output remains conceptual and is labeled with scope and unresolved assumptions.

## Boundaries and uncertainty

Code compliance, egress, accessibility, structure and MEP coordination require separate validated analyses. Early circulation distance is a proxy, not an egress determination. Irregular rooms and multi-level circulation substantially increase difficulty; the first implementation should be a single building, simple outlines and one level before expanding.
