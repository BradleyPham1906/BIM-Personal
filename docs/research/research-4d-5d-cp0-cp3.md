# 4D/5D construction planning: CP0–CP3 technical research

Status: draft, research in progress, not approved for implementation or use as an estimate. This supplements, rather than replaces, the [video review](https://app.notion.com/p/aa8e7dbfb2924f6a99ca5d5ae19da805) and [proposed plan](https://github.com/BradleyPham1906/BIM-Personal/blob/498b2b8fbf4f2583dae8aa68487bf21573bfd503/reference/plan-4d-5d-construction-planning.md). Task: [Later construction planning](https://app.notion.com/p/1941e266fa674656a3132727ca9df2b7). CP0–CP5 are internal unapproved planning labels, not V phases. This report focuses CP0–CP3; CP4 procurement and CP5 drawing intake still need their own detailed research. No app, real-model, browser, interoperability or independent practitioner tests were performed.

## Recommendation and decisions

Begin with native, supported slab/footing quantities and manual resource lines after Brad and qualified quantity/schedule reviewers approve the fixture, scope, policies and tolerances. Use explicit identity, quantity provenance and estimate links, then layer in a separate calendar/4D view and planned-cost buckets. Do not claim a complete estimate, IFC exchange, scheduling engine, actual spending or code compliance. The sample below validates arithmetic only. Costs are fictitious and not suitable for use.

**Do not build yet:** nominate reviewers; select jurisdiction and measurement edition, inclusion/exclusion and deductions, precise units and rounding, source revision/identity policy, cost currency/time basis, calendar/timezone and boundary conventions, representative model fixtures, and resource/performance budgets. Architecture and scope decisions are proposals, not approvals. Existing numbered phases, prototype scope, dates and allowances remain unchanged.

## Evidence ledger

| Source | Verified finding | Limits and consequence |
| --- | --- | --- |
| [Existing plan, pinned PR #56 commit](https://github.com/BradleyPham1906/BIM-Personal/blob/498b2b8fbf4f2583dae8aa68487bf21573bfd503/reference/plan-4d-5d-construction-planning.md) | Proposes separate element, measurement, resource, activity, allocation, scenario and package records; native-first/manual-first; CP0–CP5 gates | Pre-existing proposal based partly on visual demo; not independently checked or shipped. This report extends its CP0–CP3, not claims completion of all six. |
| [Current usage and schedule code](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/bim/usages-live-areas.js) | Floor usage calculates polygon profile area; room area and ratio-based GFA/NSA are separate; wall schedule computes centerline length × height; footing schedule calls a volume reader | No proof these quantities follow chosen contract-specific takeoff, opening, hole, joint or waste rules. Unsupported must remain unknown, not zero or a silently assumed bounding box. |
| [Current IFC importer](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/io/import-ifc.js) | Selected wall/slab extrusions and storeys imported; new internal IDs assigned; object construction shown does not carry IFC GlobalId | Do not remap changed IFC by name or array order. Full source-identity preservation and external schedule matching need a dedicated audited adapter. |
| [Current project record](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/core/objects-save.js), [project file](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/io/project-file.js) | Record enumerates project fields; format-v2 envelope takes `bimProjectRecord`; saves use browser storage/IndexedDB paths | A free-standing global alone is not persistence. Undo, history, new tabs, migration and read-only behavior need a complete source audit and browser tests. |
| [buildingSMART IFC4.3 IfcCostItem](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcCostItem.htm) | With CostQuantities the values indicate unit costs; without them, values indicate totals; quantities to sum must have the same physical type | Exchange is a mapping research input, not proof the app imports any costs. Preserve whether a cost is unit or total; do not sum mixed quantity kinds. |
| [buildingSMART scheduling example](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/annex_e/construction-scheduling/construction-scheduling-task.html), [IfcTask](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcTask.htm) | Example links products to tasks via IfcRelAssignsToProduct, sequences tasks, and applies a calendar; tasks can be non-product work and milestones have no duration | An example is not an exchange conformance test; IfcRelAssignsToProcess can express other operations, so relationship direction/meaning matters. Specify an exchange view and test the actual software before promising round-trip. |
| [RICS NRM overview](https://www.rics.org/profession-standards/rics-standards-and-guidance/sector-standards/construction-standards/nrm) | NRM 2 covers detailed measurement for building works; documents were reissued in 2022 without material content change | Relevant practitioner guidance, not automatically applicable to every jurisdiction or contract. Agree exact edition and item rules before coding; this report does not assert compliance. |
| [US VA estimating manual, 2022](https://www.cfm.va.gov/cost/CostEstimatingManual.pdf) | VA requires documented assumptions, comprehensive and credible estimates and says the estimator is responsible for BIM quantities rather than relying solely on the model | Agency-specific requirements are examples, not universal rules or an approved rate book. Independent estimate and scope cross-checks remain a human gate. |

## CP0 — identity, measurement and reproducibility contract

- Distinguish identity from revision. Native element ID is scoped to project; retain a revision or geometry fingerprint and the full measurement policy version. Copy creates a distinct element/link; delete leaves an explicit orphan requiring resolution. Reimport is not a proven identity match. Do not infer cross-document identity from a name, index, nearby geometry or STEP-local entity number. If later adding IFC, retain source document identity, IFC version, GlobalId and revision and detect missing, duplicate and changed IDs; mapping still requires explicit decisions.
- Build a coverage inventory listing every selected source object, supported/unsupported/deleted/ambiguous state and quantity kind; report excluded, missing, assumed and manually entered separately. A numeric zero is legitimate only when checked and supported. One original measure record may support multiple resource lines, but provenance and allocation rules must prevent counting the same cost line twice.
- CP0 fixture proposal: one 6 m × 4 m × 0.2 m rectangular slab with one 1 m × 1 m full-depth internal opening, plus a separately described non-model allowance. Reviewer independently measures source geometry, confirms topology, opening and method, then signs off policy and tolerances. Test no opening, multiple nonoverlapping holes, overlapping holes, boundary-crossing opening, nonmanifold/curved/imported/unsupported cases. Explicitly reject or label unvalidated shapes; do not extrapolate the sample to arbitrary geometry.
- Test translation and rotation invariance for supported rigid transforms, dimensional conversion (m, mm, m², m³), clone/edit/delete/undo/reload, schema migration and multi-tab persistence. Do not assume the existing revision counter alone is a persistent content hash. Confirm how save failures and browser read-only mode surface to users.

## CP1 — quantities and estimate contract

Measurement = kind + value + unit + gross/net rule + source ID/revision + method/version + exclusions + provenance + reviewer/state. A priced line references measurement or explicitly describes non-model scope, and includes quantity basis, resource kind, input unit, conversion/productivity, rate per compatible unit, currency/date/source, and adjustments with their own bases. Keep measured net work unchanged by purchasing waste. Crew-hours and person-hours must never be conflated; a productivity figure needs both numerator and denominator.

Calculations should use full precision internally with a single agreed display/line/total rounding policy and use decimal or integer minor-unit arithmetic for money. No silent cross-currency summation; tax, escalation, contingency, overhead, margin, material waste and scope exclusions each require declared bases and explicit treatment to avoid double counting. Rates without evidence or invalid units stay unpriced/blocked; completeness means coverage of the defined scope, not merely a numerical total. A provisional total must disclose unknowns and exclusions. Record review/sign-off separately from arithmetic.

## CP2 — programme and 4D contract

Define a small first scheduling model: explicit dates, work calendar and, if approved, finish-to-start zero-lag dependencies; reject unsupported dependency types or contradictory constraints rather than approximating. Define project timezone, work intervals, weekends/holidays, date inclusivity and milestone semantics. An illustrative convention is half-open intervals [start, finish); milestone at finish is an event, not a duration. The convention is proposed, not yet selected for the product.

Activity IDs, predecessor links and multiple element allocations must remain separate from design geometry; validate unknown links, cycles, dates and allocation scope before playback. Allow a task without geometry. For multiple tasks on one object, define installation/removal/temporary actions and priority explicitly rather than asserting one global element state from an arbitrary task. Playback must be reversible and view-only, and restore visibility/material state when stopped, changing project, loading or cancelling. Calendar dates are distinct from elapsed animation time and sun/site time.

A minimal independent schedule fixture should span a weekend, a holiday, one zero-duration milestone and a finish-to-start link; hand-check each boundary in the selected timezone, with DST and split calendars later. Test invalid cycle, missing task, contradictory dates, unsupported lag and deletion. This report does not run that scheduler or verify a critical path.

## CP3 — planned cost, allocations and baselines

Cost distribution belongs to an immutable approved estimate snapshot and scenario schedule, with a profile per line/allocated portion (e.g. linear over working days, specific delivery event, milestone or separately priced non-model item). Before aggregation, check allocation coverage: each included amount has fractions totalling exactly 1 under defined precision, and cannot be assigned twice across activities or packages. Time buckets, unallocated/incomplete amounts and total must reconcile. Rounding residuals need a deterministic policy, not silent loss. Timing-only changes preserve the total unless a separately recorded escalation/time-related rule changes it.

Expose base scenario, source revision and staleness; compare baseline to working scenario without mutating the baseline. A planned cost curve is neither incurred cost nor actual cashflow, paid invoices, earned value or a validated progress measurement; those require distinct approved evidence and policies. No construction schedule or estimate data in this research is a real baseline.

## Reproducible arithmetic fixture (synthetic, not app execution)

Script `experiments/cp0-cp3-fixture.py`; raw `experiments/cp0-cp3-fixture-results.json`. Executed with Python 3; inputs and rates are invented, generic currency. Full-depth isolated opening and 5% additive purchase waste are stipulated solely for illustration, not NRM or project requirements.

| Item | Arithmetic | Result |
| --- | --- | --- |
| Net volume | 6 × 4 × 0.2 − 1 × 1 × 0.2 | 4.6 m³ |
| Ordered material | 4.6 × 1.05 | 4.83 m³ |
| Material | 4.83 × 120 currency/m³ | 579.60 |
| Labour | 4.6 × 0.5 person-h/m³ × 50 currency/person-h | 115.00 |
| Non-model allowance | synthetic flat item | 100.00 |
| Total | 579.60 + 115.00 + 100.00 | 794.60 |
| Two working-day distribution | 50% material/labour each day; allowance day 1 | 447.30 + 347.30 = 794.60 |
| Bad split | 60% + 60% of one cost line | 120%; proposed validator rejects |

Only a Python assertion of the arithmetic and that the bad fractions exceed one ran. It does not call the application, implement a validator, use a model, schedule a calendar, or establish real-world quantity/cost accuracy. The hand calculation and the script share the same assumptions and were not independently reviewed.

## Verification and exit gates

1. **CP0:** human-reviewed source/identity audit, representative original fixture with independently measured quantities and explicit tolerances; signed policy, architecture and data retention decision.
2. **CP1:** unit and source cases, zero/unknown/exclusion, mixed units and currencies, negative/invalid inputs, net/gross, rounding and totals verified; real app save, reload, undo, copy/delete and tab tests; qualified estimate review.
3. **CP2:** independently calculated multi-calendar network fixture with boundary and cycle cases, plus actual browser playback and restore-state tests; planner review. No claim of CPM absent validated solver.
4. **CP3:** all included amounts uniquely allocated; bucket sum plus explicitly unallocated sum reconciles to estimate; allocation >100%, missing dates, changed rates and partial coverage visibly handled; baseline immutable after save/load; independent cost reviewer checks.
5. **Future CP4/CP5:** separate procurement lead-time/calendar, package and issue impact research; AI drawing extraction/ground truth, privacy/security and approval workflow research remain outstanding. IFC/XER exchange and any third-party runtime/library require their own version, license and actual interoperability test.

No independent expert or independent code review, production browser test, representative model/field pilot, paid service, customer data, runtime code change or formal standard compliance assessment was performed. Existing video review remains visual sampling, not an audio transcript or verified demo totals. Research is useful to refine the decision, not a substitute for professional construction or estimating judgment.
