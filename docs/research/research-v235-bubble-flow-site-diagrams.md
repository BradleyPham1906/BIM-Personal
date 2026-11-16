# V235 — Bubble, flow and site diagrams

## Decision and verdict

**Question:** What diagram system should connect program relationships with the existing site-analysis capability?  
**Verdict:** Add coordinated diagram views backed by V233/V234 records and the existing site findings. Do not build another site-analysis engine. V235 is the visual synthesis layer joining spatial intent, process flow and site evidence.

## Existing platform foundation

V158 already provides a seven-stage site-analysis workflow, ten analysis categories, sourced findings, confidence, severity, photographs and plan pins. Repeated model filling updates findings in place while preserving owner decisions.[^https://app.notion.com/p/4ee77a0a08f84d3bad5473621c62175b]

V172 already implements buffer, distance, slope, exclusions, suitability, locate, constraints/opportunities and buildable-area tools with result layers and run history.[^https://app.notion.com/p/394c97ed108346f489e565fcb4a47c20]

WBDG includes site analysis in programming and identifies legal limits, zoning, traffic, topography, views, vegetation, climate and built features as inputs to the design problem.[^https://legacy.wbdg.org/design-disciplines/architectural-programming]

RAIC recommends examining pedestrian and vehicular circulation alongside space relationships and site constraints, then using block models to evaluate form, massing, sun, shade, rain and wind.[^https://chop.raic.ca/chapter-6.2]

## Diagram families

- **Bubble:** relative size, grouping, adjacency and pinned/flexible positions.
- **Zoning:** public/private/service, department, security, environmental or operational zones.
- **Flow:** ordered paths for users, staff, goods, waste, vehicles and emergency access.
- **Stacking:** departments and major spaces by level, including vertical connections.
- **Site response:** program anchors over boundaries, constraints, suitability and access.
- **Form evolution:** saved transformations with the requirement, finding or decision that motivated each step.

All views read the same data but store their own presentation layout and annotations. A diagram is an explanation, not an independent model.

## Flow model

Represent a flow as a named ordered sequence with actor, frequency, priority and constraints. A step may target a specific room, a type of space or an access point. Analyze path coverage, crossings between incompatible flows, excessive travel and missing transitions. Anthropocity's user paths demonstrate how ordered routes can drive corridor concepts and expose uncovered rooms, while still allowing manual paths.[^https://anthropocity.com/docs/graph-lab-paths]

## Site synthesis

Translate site findings into explicit design influence:

- red flag or legal exclusion → hard constraint;
- slope, flood, wetland or setback → geometry mask or cost;
- access, view, daylight or public realm opportunity → weighted objective;
- uncertain source → visible confidence and review requirement.

Never convert a low-confidence site finding into a hard design constraint automatically.

## Acceptance criteria

- Diagram edits never overwrite the underlying program or source finding without confirmation.
- Pins and callouts link back to source, date and confidence.
- The same space maintains identity across matrix, bubble, flow, stacking and site views.
- Each diagram can be exported with legend, units, revision and provenance.
- Filters can isolate one department, actor, level or relationship type.
- The site-response view consumes V158/V172 outputs rather than duplicating their computations.
- Diagram snapshots can be compared across approved revisions.

## Risks and boundaries

Visual overlap or proximity can be mistaken for verified adjacency. Diagram layouts must carry a prominent conceptual status. Site tools provide evidence but do not replace surveys, code review or specialist judgment. V235 should stop before generating walls, corridors or BIM elements; that belongs to V236/V237.
