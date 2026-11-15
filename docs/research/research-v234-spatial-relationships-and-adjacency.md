# V234 — Spatial relationships and adjacency matrix

## Decision and verdict

**Question:** How should adjacency matrices, bubble diagrams and spatial requirements share one source of truth?  
**Verdict:** Create a typed spatial-relationship graph. The matrix and bubble diagram are synchronized editors/views of that graph, not separate datasets. Reuse V230 for dependency evaluation; V234 adds architectural relationship semantics.

## Evidence

WBDG identifies relationship or bubble diagrams as programmatic strategies for showing which functions should be near one another, circulation connections, security, privacy and flow. It treats these as strategies derived from goals and evidence rather than arbitrary graphics.[^https://legacy.wbdg.org/design-disciplines/architectural-programming]

RIBA says Concept Design proposals must demonstrate that spatial and adjacency requirements are being achieved; unresolved room adjacencies should not be carried into Spatial Coordination.[^https://www.riba.org/media/syneeeto/2020ribaplanofworkoverviewpdf.pdf]

RAIC identifies functional requirements, adjacencies, flexibility, site constraints and budget as pre-design information. It recommends comparative space plans for size, relationships, circulation and optimal adjacency before form is fixed.[^https://chop.raic.ca/chapter-6.2]

Anthropocity demonstrates a practical interaction: parameters can generate links, an adjacency matrix edits relationship strength, and changes update the graph immediately.[^https://anthropocity.com/docs/getting-started]

## Relationship model

Each edge needs:

- stable ID;
- source and target space or group;
- type: must-adjoin, direct-access, near, visual-connection, acoustic-separation, secure-separation, avoid, sequence-before, served-by or shared-support;
- strength/priority;
- hard or soft constraint;
- directed or undirected behavior;
- minimum/maximum distance when meaningful;
- applicable user/process flow;
- source, rationale, confidence and approval status.

A single 0–3 matrix value is insufficient for final storage because proximity, access, separation and process sequence mean different things. The matrix may present a selected relationship family as compact symbols or scores.

## Core behaviors

- Edit an edge in the matrix and see it update in the bubble view.
- Dragging a bubble changes presentation coordinates, not the underlying requirement.
- Pinning a bubble records a designer constraint separately from relationship data.
- Group spaces by department, security zone, floor preference or functional cluster.
- Detect contradictions, such as must-adjoin and must-separate on the same pair.
- Show why an AI-suggested edge exists and require approval before it becomes a requirement.
- Preserve manual relationships when regeneration or import is repeated.

## Analysis outputs

- degree and weighted degree;
- required-edge coverage;
- unconnected spaces;
- relationship conflicts;
- clusters and hubs;
- shortest process path;
- adjacency satisfaction once geometry exists;
- matrix completeness without encouraging meaningless all-to-all ratings.

## Acceptance criteria

- One graph record produces consistent matrix, bubble and list views.
- Relationship types are schema-validated and extensible.
- Hard constraints cannot be silently downgraded by a layout solver.
- Suggested, approved, rejected and superseded edges remain distinguishable.
- Matrix edits are undoable and auditable.
- Graphs remain usable with hundreds of spaces through filtering, grouping and level-of-detail controls.
- V234 works without a generated floor plan.

## Alternatives and limitations

A force-directed bubble layout is suitable for communication but does not prove plan feasibility. Graph distance is not physical distance. An attractive bubble diagram must never be reported as satisfying area, circulation, code or constructability. Relationship weights are project decisions and may be biased by whoever authored the program; reports should identify unreviewed groups and missing stakeholder input.
