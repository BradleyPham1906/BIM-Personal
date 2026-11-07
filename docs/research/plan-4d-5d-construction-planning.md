# Proposed plan: element-linked 4D/5D construction planning

2026-10-30. **Later / Preparing / discovery-first.** CP0–CP5 below are internal workstream labels, not assigned V phases. No date, effort allowance or monetary budget is committed. Do not alter the current numbered order or the prototype scope to implement this plan.

[Evidence review and limitations](research-4d-5d-construction-planning.md) · [Notion work package](https://app.notion.com/p/1941e266fa674656a3132727ca9df2b7) · [Notion summary](https://app.notion.com/p/aa8e7dbfb2924f6a99ca5d5ae19da805).

## 1. Product outcome

Select a footing, slab or other supported element and see its reviewed measurements, resources, estimate lines, activities, packages and open questions. Select an activity and see the linked elements. Change a dimension or an approved planning assumption and see the affected quantities, cost and programme marked or recomputed under an explicit policy. Scrub a construction date to see future/in-progress/completed work and time-phased **planned** cost from the same scenario.

This is a construction planning model inside the existing design app, not a second app, not a development-finance replacement, and not an autonomous construction manager. Initial scope excludes full 2D drawing reconstruction, automatic clash resolution, resource leveling, live accounting, automatic purchasing and certified estimates or safe erection methods.

## 2. Interaction design proposal

Use the existing model viewport and selection. Proposed planning workspace or panel has Breakdown, Estimate, Programme, Procurement and Checks views of the same records; choose exact placement in CP0, consistent with current Analyze/Properties and command conventions. Avoid another disconnected dashboard or duplicate project state.

- **Breakdown:** group by element/type/level/zone and show quantity coverage, unknowns and exclusions. Selecting a row highlights its elements and vice versa.
- **Estimate:** resource lines with units, quantity basis, rate source/date/currency, adjustments and approval; filter by element, cost code, package or activity.
- **Programme:** activity list and accessible timeline; predecessor/calendar validation, linked-element selection, explicit scenario and construction-date control.
- **Procurement:** package totals derived from the same estimate lines, required-on-site and decision/order deadlines, supply lead-time assumptions.
- **Checks:** missing mappings, stale measurements/rates, unpriced scope, invalid dates/dependencies, duplicate allocations, unresolved drawing questions and reviewer decisions.
- **Mobile/tablet:** switch between model and details rather than squeeze multiple wide grids. Keyboard selection and text state labels must work without color or animation.

A new workspace name/layout is a proposal, not approval to undo One Analyze or alter existing navigation. V175 may eventually embed live planning summaries, but its present scope is not enlarged by this note.

## 3. Connected records (proposed schema, not existing API)

Keep the authoritative design geometry where it is. Refer to it by stable internal ID and revision; preserve external source identity separately when supported. Never join by a mutable display name or array position.

| Record | Minimum responsibilities |
|---|---|
| Element link | Internal object ID, source document/revision/entity ID where available, classification, level/zone, link status |
| Measurement | Quantity kind, value/unit, gross/net rule, deductions, method/version, source geometry revision, measured/manual/assumed status, evidence and reviewer |
| Resource definition | Material/labour/plant/subcontract, output unit, consumption/productivity basis, resource input unit, source |
| Estimate line | Unique line ID, model or non-model scope, measurement reference, resource input quantity, rate/source/date/currency, separate waste/risk/commercial adjustments, inclusion and approval |
| Activity | Persistent ID/WBS, calendar, duration or explicit dates, predecessor relationships, baseline/scenario dates, status and reviewer |
| Allocation | Many-to-many element/quantity/resource-line/activity links, allocation basis and coverage; explicit split without duplicate counting |
| Package | References to shared estimate lines/allocations, lead-time assumptions, need dates and decision status |
| Issue/check | Source drawing/page/revision and question, affected elements/lines/activities/packages, due date, response and approval history |
| Scenario/baseline | Versioned approved input snapshot and comparison; do not overwrite the baseline when the model or working scenario changes |

Non-model scope (preliminaries, supervision, temporary works, mobilization, excluded services, allowances) is first-class. Do not create dummy solids solely to make a budget line visible. Unknown differs from zero; excluded differs from omitted; an allowance differs from a measured quantity.

## 4. Deterministic core before AI

Proposed calculation flow:

1. Read supported geometry through existing authoritative readers; apply the selected measurement policy. Preserve net measurement and explicit deductions. Unsupported geometry reports a gap instead of using an unlabelled bounding box.
2. Convert measurement to resource inputs using unit-checked build-up rules. Keep gross purchase quantity/waste separate from net work quantity. Crew productivity and crew hours are not the same unit.
3. Price approved resource inputs against versioned rate records. Calculate line quantity × compatible unit rate, then explicit adjustments at their documented basis. Distinguish direct costs, preliminaries, contingency, overhead and margin; avoid charging them twice at line and project levels. Currency conversion, tax and escalation need an approved basis and are not silently assumed.
4. Validate activity graph and calendars before scheduling. Initial scheduling scope should be explicit-dates and a limited, documented finish-to-start dependency model; only expand dependency types after research. Detect cycles and missing predecessors. Do not claim critical-path dates from a colored Gantt alone, or derive elapsed construction duration directly from labour hours.
5. Map each construction date to activity state, then to linked elements/allocations. Define day boundaries, milestones, partial work and repeated work explicitly. Preview styling must not delete or permanently hide design geometry. Stop restores the prior design view; construction time never silently overwrites site/sun time.
6. Distribute each priced line once across dates under a declared profile (e.g. approved linear work distribution, delivery event or milestone). Time buckets reconcile with the estimate. **Planned cost-to-date is not actual cost, paid cash, earned value or physical percent complete.** Actuals require separate evidence; payment terms/retention require a separate cashflow policy.
7. Derive procurement totals from the same line allocations. Lead times work back through the appropriate calendar from need dates. An RFI exposes affected links and assumptions; it does not automatically approve a new rate, method or finish date.
8. On changes, recompute only reviewed deterministic derivatives, flag stale or invalid approvals and broken mappings, and show an impact preview before committing scenario/baseline changes. Preserve audit history.

UI painting can reuse the existing animation controller's accessibility and pause patterns, but `motion.js` is not already a construction scheduler. Calendar state, scenario persistence and playback's display overlay need their own tested contract.

## 5. Internal delivery stages and approval gates

### CP0 — source, identity and measurement audit

Deliver a verified integration map: existing quantity readers and their limits; all save/load, local storage, undo, history, tab switching and import identity paths; candidate reuse implementations and licenses; applicable measurement rules/editions and calendar/exchange semantics. Research follows `research-protocol.md`, including independent practitioner sources. Never interpret this plan's U-design choices as implementation evidence.

Select a small owner-approved, nonconfidential native slab/footing fixture, with independent hand/reference measurements and reviewer-agreed tolerances. Audit openings, holes, transformed objects, curved elements, imported locked solids, geometry edits and identity after copy/delete/reimport. Current wall schedule's length × height must not be relabelled net wall area. Existing IFC import does not retain source GlobalId; define native-first identity without falsely claiming interoperable mapping.

**Gate:** Brad approves bounded scope, UI location, architecture, data retention and tolerance/performance budgets. Dates/effort are estimated only after this audit. Nominate quantity/rate/schedule reviewers.

### CP1 — quantities, resources and estimate

Deliver the smallest vertical slice: supported native elements, traceable measurements, editable/reviewed resource build-ups and rates, non-model scope, bidirectional selection and exportable estimate/coverage report. Initial inputs can be manual; no AI or external service required. Reuse V131's parser and readers only where their dimensional and error contracts fit.

**Gate:** independent fixture quantities and line/project totals agree under stated rounding; unit mismatch/unknown rates remain visible; adjustments cannot mutate net quantities; edit-follow, undo and file round-trip pass. No market-rate defaults invented by the assistant.

### CP2 — construction programme and 4D

Deliver activity/calendar records, constrained dependency validation, explicit element/activity allocations, scenario dates, scrub/play/pause/stop and visible future/in-progress/complete states. Include non-geometric tasks (design approvals, fabrication, curing, access preparation); not every task creates an element. Keep design state and baseline untouched by preview.

**Gate:** independently checked tiny schedule fixture, cycles rejected, boundaries/milestones/non-working days covered, allocation completeness reported, manual dates/constraints not silently overwritten. Reuse of the shared playback controller must not regress sun, traffic, reduced motion or background pausing.

### CP3 — linked 5D planned cost and scenarios

Deliver declared cost-distribution profiles, period and cumulative planned-cost views synchronized with CP2, model/rate/schedule impact previews and baseline/scenario comparison. Derive values from shared estimate lines, not a manually copied summary.

**Gate:** every included line allocated once, bucket sum equals estimate total within agreed rounding policy; timing-only changes preserve total unless an explicit time-dependent rate changes it; excluded/non-model/time-related costs remain visible. Do not label planned curves as actual spending or earned value.

### CP4 — procurement, RFIs and quality links

Deliver package grouping, lead-time/deadline logic, issue-to-element/activity/cost links and quality-check records/evidence. A query can show affected scope, unresolved assumptions and critical procurement decisions. No automatic orders, vendor commitments, certified inspections or safety clearance.

**Gate:** package/estimate totals reconcile, split packages do not duplicate resource costs, late-decision alerts use reviewed calendars and assumptions, issue closure preserves evidence/approval. Dates remain advisory until planner/procurement review.

### CP5 — optional AI-assisted intake and planning

Only after the manual core is trustworthy: drawing text/vector/OCR extraction as a proposal; scale/grid/dimension calibration; candidate element classification; mapping suggestions; draft resource/activity assignments; missing-information questions. Preserve drawing/page/revision references, tool/model version, prompt/input/output and review decisions. Rendering generated meshes is not enough to establish measurable BIM semantics.

**Gate:** owner-approved representative drawing fixtures with independently labelled ground truth; agreed error tolerances; missing/ambiguous dimensions rejected or flagged; no silent hallucinated scope/rates; human-reviewed diff before model/estimate/programme edits. An AI service, backend, OCR/runtime library or other dependency must be justified and explicitly approved under the delivery contract. No inference that the video or imported Scenario skills grants service access or redistribution rights.

Full IFC, PDF/OCR, XER and other schedule-file exchange each require a separate format/version/license audit and actual import test. The video's XER button does not make that adapter available to us. Start with native elements and a narrow, versioned local JSON/CSV interchange proposal after defining schema; do not claim a generic file round-trip proves format correctness.

## 6. Release verification and failure cases

Each implementation stage needs a browser suite, deliberately broken variants caught for the correct reason, and the full current regression before release. Drive controls through the real model, not just DOM appearance. Protect existing save keys and source layout; do not hand-edit generated `canvas_v10.html`.

Required test families: geometry/deductions/unit conversions; unknown vs zero; copy/delete/remap IDs; source revision invalidation; split activity/package allocations; double counts; blank/mixed currency/rate bases; precision and rounding; calendar holidays and date boundaries; milestones/negative lag policy/cycles; no-geometry tasks; construction vs sun date isolation; before/after/partial activity states; undo/redo and project tabs; save/load/export with schema migration; baseline immutability; explicit errors/toasts; mobile keyboard/touch and reduced motion; imported mappings; malicious/untrusted file and AI text treated as data, never executable instructions.

No runtime tests were performed for this documentation-only proposal. Historical app test counts are not evidence that any of these new behaviors work.

## 7. Decisions needed before implementation

1. Approve or revise the native-model slab/footing pilot and initial measurement scope; nominate reviewers and tolerances.
2. Decide where planning lives in the existing UI and when this Later workstream is prioritized. Leave V numbers/dates unassigned until then.
3. Choose initial currency, region/rate basis, measurement policy and construction calendar from actual project needs; no universal defaults presumed.
4. Confirm manual inputs first, and which external model/schedule/estimate format needs an audited adapter first.
5. Decide whether optional AI intake is worth a separately evidenced architecture/service exception. No paid or confidential-data transfer authorized by this plan.

Documentation and preliminary planning were requested. Feature execution, programme/cost baseline approval, dependency exceptions, purchases and operational construction decisions remain pending human approval.
