# Parametric Design: feature history and reference resilience — research draft

2026-11-13. Parent: F1–F7 Freeform, with Parametric Design inside that workstream, not a new phase [1]. Repository baseline: 95b7aee4db8be1fc28c0fbe7befc7407fabd1dda. This is an architecture investigation, not approval to implement, a claim that the current app supports this workflow, or a complete Freeform research report. It complements the pinned SolidCraft source map in this PR; no upstream build, execution or integration was performed here. No independent review.

## Questions and findings

- Can a regenerated display mesh substitute for editable parametric geometry? Not reliably: geometry, topology and tessellated render output represent different things [2]. A feature history requires inputs and dependencies, not just an image or commit history. This does not settle which kernel to select.
- Can a face's array index be treated as a stable semantic ID? Not safely in general. FreeCAD documents that modeling operations can change a shape's internal name, causing dependent features to break or compute incorrectly [3]. A review catalogs naming ambiguity under insertion, deletion and parameter changes [4]. Neither source proves a particular defect in this app; it motivates explicit tests.
- Does assigning a stable feature ID solve face naming? No: a stable feature can still generate, split, merge or remove multiple faces. A mapping must describe provenance and ambiguity; when identity is uncertain, do not silently attach a pocket to another face.
- Is a dependency DAG sufficient? It can order acyclic rebuilds, but by itself does not solve nonlinear sketch constraint convergence, numerical geometry validity, subshape identity, old-file migration, undo or failure handling. Expressions need explicit units and a restricted grammar, not arbitrary code execution.

## Proposed narrow vertical slice, after owner approval

Use a constrained closed sketch → pad → pocket while preserving existing project model, selection, layers, commands, history and offline/build contract. Before choosing architecture, audit existing code paths and tests for actual sketch constraints, pad/pocket, persistence, undo/redo, render ownership, BIM objects and dependency handling; a partial upstream map is not a completed app audit. Do not add libraries or change build without approval [5].

Feature records would carry stable ID and schema version, kind, explicit inputs, units, parameters or safe expressions, references, dependency edges, creation order and precise status. Output contains native geometry/topology when available, with a disposable versioned display tessellation cache. Persist last valid result as explicitly stale only if users can distinguish it from current geometry, and only with an approved storage policy. An alternative is hiding failed downstream output; user decision required. No invalid or ambiguous recomputation may silently appear current.

References should prefer robust design datums (feature-origin planes/axes, construction geometry, user-selected semantic anchors) over transient face order when possible. For topology-derived references, record originating feature and role, geometric constraints and lineage where the chosen kernel exposes it. Resolve uniquely only within explicit tolerance and deterministic rules; on multiple candidates or missing lineage produce ambiguous/missing status and ask for reattachment. Geometry signatures alone can collide, especially symmetric faces; no universal naming solution is assumed. Topology change may legitimately break a reference.

Recompute in topological order; detect cycles before commit; restrict invalidation to affected descendants while avoiding stale siblings. Stage results and make undo/redo transactional: failed edit must not leave mixed old/new geometry represented as valid. Sketch constraints need under-constrained/over-constrained/inconsistent states and explicit solver error reporting; no claim that graph ordering replaces a sketch solver. Bound expression length, depth and dependency count and reject unknown units, nonfinite values and cyclic expressions. Document tolerance and conversion rules; never round storage to display precision.

## Hand-checkable acceptance examples

For rectangle width 4 m, length 3 m and pad depth 0.3 m, analytic volume is 3.6 m³; increasing width to 5 m gives 4.5 m³ before a pocket. For a non-through rectangular pocket 1 m × 0.5 m × 0.1 m fully contained in the pad, expected removal is 0.05 m³ and result after the width change is 4.45 m³. The pocket's placement/attachment and whether it is fixed to an edge or datum must be specified before judging rebuild behavior. An out-of-bounds or excessively deep pocket is not covered by this arithmetic: expected behavior is a named failure or an explicitly defined valid operation, not an invented result. These are analytic examples, not executed geometry tests.

## Alternatives and evidence gates

| Route | Benefit | Unresolved risk |
| --- | --- | --- |
| Extend proven current JS code | Minimum integration disruption | Actual solver/geometry capability, exactness, naming and test coverage not established |
| Adapt unchanged SolidCraft components | Reuse upstream design where suitable | Browser/WASM, compiler/runtime contract, data serialization, licensing and isolated execution require investigation and owner approval |
| Native BRep kernel behind narrow adapter | Mature geometric operations may be available | Kernel-specific history/naming, WASM bundle/build, tolerance, kernel and dependency licensing, offline portability |

The prior SMLib trial is documented in the parent task [1]; it was a limited build experiment, not proof of the complete modeling workflow or a final kernel adoption. Evaluate SMLib, OCCT and other candidate routes on an identical independently defined corpus; verify the exact revisions and licenses. The owner decides when a solid kernel is required and whether build constraints may change.

Test matrix before release: closed/open or self-intersecting sketches; under/over constraints; dimensional edits and multiple branches; insert/delete/reorder/cycle; ambiguous, split and removed face references; mirrored/symmetric solids; unchanged unrelated nodes; failure and repair; repeated undo/redo; save/reopen and old files; layer/visibility/selection and BIM linkage; export/reimport to another tool; numerical tolerances, memory and responsiveness across supported devices; offline packaging. Compare independent geometric measures and topology, not screenshots only. Deliberately break rebuild/persistence tests to show the suite detects the failure, as the plan requires [5]. None was executed for this draft.

## Decision and remaining work

Owner approval is required for target workflow, dependency/build changes, last-valid behavior and internal sequence. Independently audit app source and upstream candidate revisions and licenses; establish representative benchmarks and execute approved isolated comparisons; review with CAD experts and meet repository research-exit rules. The parent's 112 hours is an unvalidated old estimate, not a delivery commitment. Broader curves, NURBS surfaces, loft, sweep, Make2D, analysis and rendering remain separate F1–F7 work; this slice does not complete them.

## Sources

[1] https://app.notion.com/p/3fecbfcc3a38811e8e25f016056867ea
[2] https://dev.opencascade.org/about/modeling_data
[3] https://wiki.freecad.org/Topological_naming_problem
[4] https://www.sciencedirect.com/science/article/pii/S1110016818300814
[5] https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/docs/research/plan-parametric-design.md
