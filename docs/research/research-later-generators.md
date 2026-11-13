# Later: Generators — massing, parking and subdivision

## 1. Abstract
How can editable candidates be generated from V160's zoning envelope and yield while staying honest about feasibility? Recommend deterministic, preview-first massing constrained by each floor's actual envelope, then separately evaluated parking and lot subdivision candidates. Every output should carry a revisioned source, constraints, assumptions, diagnostic and explicit non-compliance/unknown states. Do not turn the current numeric `achievable` yield into a claim that a buildable configuration exists. The source audit and synthetic arithmetic below are real; a generator, geometry fixture, app integration and code-compliance review were not run.

## 2. Hypotheses
- H1: V160 already computes some quantitative capacity and FAR-limited yield. Supported: `bimZnCalc` computes plate capacity and takes the minimum with FAR. P/high, pinned code.
- H2: The achievable area itself proves there is a connected, buildable, accessible building and parking layout. Rejected: area is a bound, not a solved geometry or permit decision. P/high for code distinction, proposal for additional checks.
- H3: Floor plates from one plane automatically remain inside a sloping envelope for the whole floor. Rejected in general; stepped and tapering envelopes require 3D containment or conservative intersections at governing elevations.
- H4: Parking from area alone establishes compliant capacity. Rejected: accessible spaces, aisles and routes must be spatially evaluated; rules vary by occupancy and facility. P/high from Access Board guide.
- H5: Coverage or FAR terminology has a universal calculation. Rejected: exclusions and denominators depend on jurisdiction; Palmdale is an example, not a global rule.

## 3. Method
2026-11-13 queries: `zoning envelope building massing floor area ratio setbacks`, `parking lot design angle dimensions ADA accessible spaces`, `real estate pro forma net operating income capitalization rate expenses`. Read the pinned V160 research, `zoning-envelope.js`, and `usages-live-areas.js`; primary Palmdale and US Access Board guides; 2018 State Street feasibility study. Ran the synthetic arithmetic in `experiments/notion-later-20261113/experiment.py`; no actual generated geometry was run. No second independent researcher; no jurisdiction-specific approval, app execution, exhaustive tests or solver benchmark. Historical research discussing Giraffe acknowledges its page was unavailable and relies on search digests; treat those product claims as unverified here.

## 4. Findings
### Current app and interface
[P/high] `src/js/engine/site-analysis/zoning-envelope.js` exposes `bimZnCalc` and computes `farGFA=z.far*G.area`, `ach=Math.min(farGFA,cap)` where FAR exists, otherwise capacity. Storey plates are computed under envelope rules; later display allocates used area across successive plates. This scalar allocation does not by itself emit a constructible partial-plate polygon. At lines ~251–316 inspect actual returned structures against the pinned code before planning integration. [Code](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/site-analysis/zoning-envelope.js); [prior research](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/docs/research/research-zoning-envelope-yield.md).

[P/high] `usages-live-areas.js` includes usage IDs, GBA/GFA/NSA ratios, floor heights, formulas and mass/floor/room measurement. Masses are sliced at each band midpoint; rooms contribute measured NSA but no GBA or GFA; usage summary aggregates every eligible tagged object. Therefore the generator must avoid double counting a generated mass alongside its floors/rooms and must not equate zoning GFA with every usage's GFA without documented mapping. Code forces at least one mass level via `Math.max(1,...)`, including height below a floor-to-floor interval; validate that mismatch before using it for zoning. [Code](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/bim/usages-live-areas.js).

### Planning boundaries
[P/high] Palmdale's guide defines particular net-area exclusions, horizontal setback measurement and local gross-floor treatment; its FAR formula is GFA/net lot area. Those definitions cannot silently stand in for other jurisdictions or all building-area measurements. Store authority, adoption/date, edge role, exclusions, numerator/denominator and confidence with each rule. [Palmdale guide](https://www.cityofpalmdaleca.gov/DocumentCenter/View/15699/Zoning-Measurements-How-to-Guide-PDF).

[P/high] US Access Board requires accessible parking scoping separately per facility in covered contexts, plus location, access aisles, surface, signage and accessible routes. At least one of every six accessible spaces or fraction must be van-sized, subject to the specific scoping context. Residential, hospital and other special cases differ. Do not issue a universal 'ADA compliant' verdict from space counts. [Access Board parking guide](https://www.access-board.gov/ada/guides/chapter-5-parking).

[P/high] The State Street study separately accounts for parking type, land, hard/soft costs, rent and timing, and explains how parking constrains the form. Its assumptions are a 2018 example, not current market benchmarks. [Study pp. 4, 14–20](https://www.ccdcstatestreet.com/wp-content/uploads/2020/05/State-Street-Development-Feasibility-Analysis-06-2018-v03.pdf).

### Design proposal
[U] Snapshot envelope revision, project units, boundary, role and rule source, FAR denominator/area basis, per-floor elevations, target/usage mix, exclusions, deterministic algorithm version and random seed if used. Generate candidates as temporary previews, not authoritative BIM elements. At each storey intersect permissible envelope cross-sections at relevant top/bottom/step elevations; apply setbacks, coverage and FAR under an explicit policy; construct an actual trimmed plate for a partial floor rather than only changing the scalar. Validate containment, topology, minimum viability and area after geometry operations. Commit as one undoable transaction with stable IDs and parent/source references; rerun computes a diff and never silently overwrites manual edits.

For parking, calculate required spaces using usage-specific rates and local rounding; generate stall, drive aisle, accessible bay/aisle and route geometry; report provided/required, infeasibility and unknown requirements. Geometry depends on local dimensions, parking angle, one-way/two-way flow, fire access, slopes and obstructions; no generic default is proof. For subdivision, generate candidate parcels as polygons with legal frontage/access, area, boundaries and easements where provided; stop on invalid holes, self-intersection, sliver or disconnected access; professional subdivision approval remains external. Do not claim exact lot-line placement from an uncertain parcel.

## 5. Alternatives
Criteria: fidelity, explainability, runtime, edits and legal risk.
| Option | Strength | Cost / failure |
| --- | --- | --- |
| Scalar yield only | Existing, immediate upper bound | No physical layout or legal conclusion |
| Deterministic rule-based generator | Repeatable previews and debuggable provenance | May miss better solutions and needs robust polygons |
| Optimization over generated candidates | Explore competing capacity/cost/parking | Requires explicit objective, feasibility proof and compute budget |
| External generator import | Mature specialist workflow | Licensing, provenance, transform and editable-model mismatch |
Start deterministic and preview-first; retain an external candidate path; add optimization only when candidate validity and metrics have been independently checked.

## 6. Synthetic experiment
Run `python3 experiment.py`: 2,000 m² lot × 1.2 FAR = 2,400 m²; coverage 50% gives a 1,000 m² per-floor cap; four equal available levels total 4,000 m², so FAR governs and an illustrative allocation is 1,000 + 1,000 + 400 + 0 m². This is arithmetic only: no irregular polygon, cores, envelope change, parking, legal exclusions, construction or actual generated plate was evaluated. Allocation is not a geometry proof.

## 7. Acceptance and falsification matrix
- Rectangular constant envelope, known 4-floor capacity, exact FAR and coverage as above; verify polygon union area and per-level measured geometry against independently calculated values.
- FAR exact boundary and just above; floor height exactly at/just below threshold; tiered setbacks, slopes and setbacks with different edge roles, corner lot; no generated point outside allowable volume.
- Concave, holes, narrow necks, split insets, self intersections, tiny slivers and invalid parcels: retain all valid components or explicitly reject; never silently invent contiguous plate.
- Zero/null/invalid FAR and height; unknown is distinct from zero, finite checks and units required; source revisions make previews stale.
- Mixed-use allocation and unit rounding: sum allocated per-use equals generated areas; account for parking area and excluded floor area exactly once; compare V131 selection and schedule to independent calculation.
- Parking below/equal/above ratio rounding, blocked route, turning radii, accessible count per facility and special occupancy: show unassessed where authoritative rule or route input missing.
- Lot splits: no overlaps/gaps beyond declared tolerance, total conservation after exclusions, frontage and access rules tied to local source; flag unverified easements.
- Deterministic repeated runs, cancellation, large parcels, unit conversions, undo/redo, save/reopen, manual edits, regenerate conflict and downstream stale results. Define tolerances and target devices before testing.

## 8. Work-order decomposition
1. Inspect V160 exact data contracts and release tests; reconcile floor-ceiling vs usage midpoint and zoning vs usage area semantics. 2. Define candidate schema, lineage, stale detection and transactional preview/commit. 3. Implement/test one deterministic rectangular massing case and containment oracle; expand topology handling with regression corpus. 4. Specify separately parking and lot subdivision with local rule packs and manual overrides. 5. Profile realistic sites and independently compare results to surveyed/cadastral references and planning review. Do not treat three outputs as one inseparable work order; old 32 h is not a validated estimate.

## 9–11. Risks, open gates and owner choices
Unknowns include supported jurisdiction and exact area measure, allocation objective, minimum floor viability, parking dimensions/drive circulation, subdivision legal basis, topology algorithm, tolerance, and actual code/browser performance. Single-city and US-accessibility sources do not establish global applicability. No independent research review or actual solver exists. Owner must choose target jurisdiction/occupancies, preview versus automatic editing, area definitions, fixed vs opt-in assumptions, optimization objective, and professional review. This remains nonbinding research pending those gates.

## 12. References
Accessed 2026-11-13: pinned [zoning envelope](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/site-analysis/zoning-envelope.js), [usage code](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/bim/usages-live-areas.js), [V160 research](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/docs/research/research-zoning-envelope-yield.md), [Palmdale guide](https://www.cityofpalmdaleca.gov/DocumentCenter/View/15699/Zoning-Measurements-How-to-Guide-PDF), [US Access Board](https://www.access-board.gov/ada/guides/chapter-5-parking), [State Street study](https://www.ccdcstatestreet.com/wp-content/uploads/2020/05/State-Street-Development-Feasibility-Analysis-06-2018-v03.pdf); P for observed source statements, not jurisdiction-independent rules.
