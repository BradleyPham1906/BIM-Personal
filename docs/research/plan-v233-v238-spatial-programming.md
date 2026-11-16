# V233–V238 Spatial Programming and Algorithmic Design Roadmap

Status: proposed implementation roadmap  
Project: World BIM Platform  
Decision owner: Brad Pham  
Research date: 2026-11-15

## Product decision

Build architectural programming as a staged, traceable subsystem rather than a single adjacency-matrix tool. The durable chain is:

**Brief → Program → Spatial relationship graph → Coordinated diagrams → Schematic planning → BIM spaces → Alternative evaluation**

The adjacency matrix is one editor for the relationship graph. Bubble, flow, stacking and site diagrams are coordinated views of the same program data. Geometry generation begins only after the program and relationships can be reviewed and approved.

## Phase sequence

| Phase | Capability | Primary output | Exit gate |
|---|---|---|---|
| V233 | Architectural brief and program | Versioned requirements, space program and area model | Approved program revision with sources, units and unresolved assumptions |
| V234 | Spatial relationships and adjacency | Typed relationship graph with matrix and bubble views | Reviewed hard/soft relationships without contradictions |
| V235 | Bubble, flow and site diagrams | Coordinated conceptual diagrams linked to site evidence | Exportable revisioned diagrams with provenance and conceptual status |
| V236 | Schematic space planning | Reproducible zoning, scaled blocks, circulation, floor plates and massing | Multiple studies with visible constraint failures and preserved overrides |
| V237 | Program-to-BIM generation | Requirement-to-space identity chain and IFC-compatible spaces | Deterministic export/re-import fixture preserving IDs and required information |
| V238 | Design evaluation and alternatives | Hard gates, comparable metrics, Pareto views and decision log | At least three alternatives compared against frozen criteria with human approval |

## Dependencies

- V233 is the source of truth for V234–V238.
- V234 relationships feed V235 visualization, V236 generation and V238 evaluation.
- V235 consumes existing site-analysis findings and geometry tools; it does not replace them.
- V236 reuses stable generated-element keys, fixed/adaptive/manual override behavior and reproducible seeded runs.
- V237 begins with spaces and boundaries before attempting construction-detail generation.
- V238 evaluates every earlier stage and must keep hard failures separate from weighted preferences.

## First implementation slice

Use one building, one level and a 10–20-space reference program. Support:

1. CSV/JSON program import with stable IDs and units.
2. Typed adjacency, access, separation and sequence relationships.
3. Synchronized matrix and bubble editing.
4. One named user-flow path and one site-response overlay.
5. Reproducible rectangular space-planning studies with fixed elements.
6. Space-first BIM output with deterministic identifiers.
7. Three-alternative comparison with hard gates, absolute metrics and a human decision record.

Multi-building campuses, irregular rooms, detailed code compliance, structure, MEP, façade and construction-ready documents remain later scope.

## Architectural rules

- Preserve program requirements, spatial concepts and BIM occurrences as related but distinct records.
- Never overwrite approved or manual decisions silently during import or regeneration.
- Treat unknown, assumed, measured, simulated and AI-inferred values distinctly.
- Store source, rationale, confidence, status and revision for consequential requirements.
- Label bubble and schematic outputs as conceptual; proximity in a diagram is not proof of geometric compliance.
- Do not combine hard-constraint failures into an average score.
- Require a named human to approve program revisions and selected alternatives.

## Research documents

- `research-v233-architectural-brief-and-program.md`
- `research-v234-spatial-relationships-and-adjacency.md`
- `research-v235-bubble-flow-site-diagrams.md`
- `research-v236-schematic-space-planning.md`
- `research-v237-program-to-bim-generation.md`
- `research-v238-design-evaluation.md`
