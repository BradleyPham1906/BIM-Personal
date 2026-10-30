# 4D/5D construction planning: video review and capability gap

Review: 2026-10-30. Status: preliminary discovery, not implementation-ready research.
Decision owner: Brad, for product scope and architecture. Estimating, programming and construction-method acceptance require nominated competent reviewers; none is appointed by this note.

## Decision and boundary

Create a separate, unnumbered **Later: 4D/5D Construction Planning** workstream. Its distinctive capability is the persistent relationship between model elements, measured quantities, resource estimate lines and construction activities. It is not just image-to-mesh generation, an animation of objects appearing, or a usage-based development pro forma.

The current `main` inspected is `4ca15f952045cea42541f969b4d8b40f2b4e5972`. V172 remains Start here, followed by the existing path (including V172b/c and V173). This proposal assigns no V numbers, dates, effort or budget, changes no existing completion claim, and does not pull future work into the December prototype commitment. Publication on a branch is a proposal until merged; merging documents does not implement the feature.

- [Execution plan](plan-4d-5d-construction-planning.md)
- [Notion work package](https://app.notion.com/p/1941e266fa674656a3132727ca9df2b7)
- [Notion research summary](https://app.notion.com/p/aa8e7dbfb2924f6a99ca5d5ae19da805)

## What was actually reviewed

User-supplied `I Turned Construction Drawings into a 5D Plan with AI.mp4`, 640 by 360, duration 1102.855 seconds (about 18m23s). The supplied description identifies Tim / Contractor OS and [this YouTube reference](https://www.youtube.com/watch?v=ylHwByRVjzI). Attribution and publication date come from the supplied description, not an independently loaded web page.

Visual review sampled frames at approximately 30-second intervals across the clip and enlarged selected planning screens. This is not a continuous audiovisual viewing or a verified transcript: audio was not transcribed, and short interactions between samples may have been missed. No source drawings, original model, application code, rate database, XER file or AI prompt/output history was supplied. No demo figures were adopted as project data or independently recalculated. Screens are visual evidence of presentation, not validation of hidden calculations.

### Observation ledger

Times are approximate, relative to the attachment. P-video means primary evidence only for what the screen visibly presents, not for its technical correctness.

| Time | Visible observation | Useful design lesson | Evidence boundary |
|---|---|---|---|
| 00:15, 01:45, 02:45 | Blender/BIM-style warehouse model and element tree | Keep an elemental decomposition, not one decorative mesh | P-video; authoring process and model accuracy unverified |
| 03:15–05:45 | Element breakdown, estimate/budget table and selected element resource cards | Bidirectional model/table selection, shared resource records | P-video; rates and quantities not checked |
| 03:45, 04:45 | Diagram connects physical elements with estimate, programme, procurement and quality | One connected dataset feeds several views | P-video; underlying implementation not inspected |
| 06:15 | Dated programme screen, installed/in-activity/future states, scenario selector; a button labelled Refresh from Syncify XER | Link activities to elements; show date and scenario explicitly | P-video; button visibility does not prove working XER exchange |
| 07:15–11:15 | Slabs/footings selected from breakdown; resource quantities, rates, activities and packages | Quantity-to-resource-to-activity traceability | P-video; no demonstrated independent takeoff audit |
| 09:15, 16:15 | Construction-detail PDF pages | Preserve drawing/page/revision provenance | P-video; automatic interpretation accuracy unverified |
| 11:45 | Slide says Keep the net quantities as the source | Separate measured net quantities from waste and commercial adjustments | P-video; the proposed application's exact measurement rules still need research |
| 12:45–14:15 | Scope without a model element, site management/facilities, temporary works, exclusions, overheads/margin | Budget completeness must not depend on visible geometry | P-video; no adoption of displayed mark-ups |
| 14:45 | Elements → resources → tasks/programme and estimate/budget relationship | Separate physical objects, means of construction and sequence | P-video |
| 15:45–16:45 | Procurement packages and required dates linked to resource groups | Packages derive from shared lines, not a second estimate | P-video; procurement functionality not reproduced |
| 17:15 | Construction date, weekly/cumulative cost chart, programme and partially installed model | One date must drive visual state and planned cost distribution | P-video; cost-to-date is not proof of actual expenditure |
| 18:15 | RFI asks confirmation of wall construction; affected elements, activities, package and response date shown | Surface uncertainty and its downstream effects | P-video; displayed cost impact not recalculated |

The supplied description claims AI converts flat drawings into precise structured 3D environments. The sampled screens demonstrate a connected planning presentation, but do not establish reliable autonomous 2D-to-BIM, code compliance, validated methods, complete scope or production estimating accuracy. Do not repeat the precision/production-readiness claims as verified facts.

## Existing app: verified foundations and gaps

P-code / P-roadmap below are source inspection only. No browser test suite was run in this review.

| Source at inspected main | Read and finding | Consequence |
|---|---|---|
| [PIPELINE.md](https://github.com/BradleyPham1906/BIM-Personal/blob/4ca15f952045cea42541f969b4d8b40f2b4e5972/PIPELINE.md) | V131 usage areas/formulas; V160 yield; V170 analysis playback; Later Costs and pro forma; later full IFC and SDK | Existing overlap, but no dedicated element/activity/resource-linked construction planning row found |
| [usages-live-areas.js](https://github.com/BradleyPham1906/BIM-Personal/blob/4ca15f952045cea42541f969b4d8b40f2b4e5972/src/js/engine/bim/usages-live-areas.js) | `bimUsageMeasure`, summaries, formula parser and element schedule builders. Wall schedule area is length times height; footing schedule reads volume | Reuse measured readers where valid, not the assumption that current schedules are a complete/net bill of quantities. Mass-derived GFA/NSA ratios are not measured construction quantities |
| [source-contract.js](https://github.com/BradleyPham1906/BIM-Personal/blob/4ca15f952045cea42541f969b4d8b40f2b4e5972/src/js/engine/bim/source-contract.js) | One source-boundary reader and source ID, explicit errors | Follow the connected-source pattern; do not create detached cost geometry |
| [project-file.js](https://github.com/BradleyPham1906/BIM-Personal/blob/4ca15f952045cea42541f969b4d8b40f2b4e5972/src/js/engine/io/project-file.js) | Explicit field list in project envelope | New planning records will require audited persistence, undo/history and tab-switch integration; adding one global is insufficient |
| [motion.js](https://github.com/BradleyPham1906/BIM-Personal/blob/4ca15f952045cea42541f969b4d8b40f2b4e5972/src/js/engine/site-analysis/motion.js) | Elapsed seconds, transient analysis playback, pause/reduced motion/background handling; sun preview separate from saved project time | Reuse controller patterns, but construction calendar/scenario state is new. Do not conflate elapsed traffic time, sun-study date and construction date |
| [import-ifc.js](https://github.com/BradleyPham1906/BIM-Personal/blob/4ca15f952045cea42541f969b4d8b40f2b4e5972/src/js/engine/io/import-ifc.js) | Subset: storeys and vertically extruded wall/slab geometry; generated internal object IDs; source GlobalId not retained on constructed objects | Native model first. Audit stable identity and reimport matching before binding external schedules. Do not claim full IFC scheduling/cost interoperability |
| [CLAUDE.md](https://github.com/BradleyPham1906/BIM-Personal/blob/4ca15f952045cea42541f969b4d8b40f2b4e5972/CLAUDE.md), [CLAUDE_INSTRUCTIONS.md](https://github.com/BradleyPham1906/BIM-Personal/blob/4ca15f952045cea42541f969b4d8b40f2b4e5972/CLAUDE_INSTRUCTIONS.md), [research-protocol.md](https://github.com/BradleyPham1906/BIM-Personal/blob/4ca15f952045cea42541f969b4d8b40f2b4e5972/reference/research-protocol.md) | One connected model, derived data follows its source, offline ES5 delivery, public-repository restrictions, evidence levels and research gates | No automatic backend/dependency/paid-AI exception, source imagery publication or implementation approval |

## Phase mapping: what stays where

- **New Later work package:** construction-specific measurement policies, resource build-ups, construction programme, element/activity allocation, time-phased planned cost and procurement/issue links.
- **Later Costs and pro forma:** retain usage-based development feasibility, rent/yield/sale assumptions. Its existing 20-hour backlog allowance is not an estimate for the new workstream. Share a rate/currency convention later only if appropriate, not the same scope or totals.
- **V170/V171:** reusable playback infrastructure, not a construction scheduling solver or calibration certificate. Do not reopen completed work.
- **V175:** possible live presentation of later planning outputs. No expansion of its current committed scope.
- **Full IFC / Flows and SDK:** interoperability and automation integration candidates. Neither must block the initial native-model manual workflow; neither is claimed as shipped.
- **Freeform/parametric work:** geometry editing/history can later invalidate quantities. 4D/5D need not wait for all NURBS work; it must use accepted measurable native elements.
- **Scenario skills:** visual asset preparation may support site storytelling. Generated equipment, meshes or environments are not certified geometry, quantity sources, rate databases or construction planning algorithms.

## Alternatives and validation verdict

| Option | Fit to connected model | Accuracy/auditability | Delivery contract | Recommendation |
|---|---|---|---|---|
| Manual verified quantities + linked activities/resources in the app | Strong | Inspectable with independent fixtures | Can target existing offline contract; feasibility still to audit | Preferred first slice |
| External schedule/estimate exchanged through files | Useful | Depends on identity mapping, units and calendars | Adapter/reuse research first; no live integration claimed | Later, explicit formats |
| AI drawing-to-5D in one step | Unproven | Dimensions, hidden scope, rates and sequence can be invented | Usually needs additional models/services; unavailable here | Not the initial release |
| Unlinked visual animation and separate cost table | Weak | Easy to drift and imply false completeness | Simpler but violates the connected-data purpose | Reject as the final architecture |

**Verdict:** accept the demonstrated connected-data concept for preliminary product planning; restrict the claims of accuracy, AI automation and production readiness. The architecture and stages in the linked plan are proposals (U-design), not tested code. Do not use U items to implement until the research exit rule is met.

No estimates, forecasts or economic benefits were computed. No experiment installed dependencies, ran upstream code, connected a service, spent credits or changed approved model/cost/schedule data. Independent practitioner sources, applicable measurement rules/editions, schedule/calendar semantics, exchange specifications, licenses and reuse-source audits remain open. The video's attractive presentation is subject to demo selection bias and is not independent validation.

## Decision/transparency log

- Request: review the supplied video, assess fit to design/phases, and create a new phase document/plan if new.
- Inputs: supplied video/description, current main and selected source files, existing Notion tasks and documentation query. No original project files or audio transcript.
- Output: preliminary review, staged plan, unnumbered Preparing backlog work package, documentation-only PR.
- Brad's approval: pending for implementation, timing, funding, architecture exceptions and any AI service use. Professional quantity/rate/programme reviewers: to be nominated.
- Next decision: accept or revise the bounded native-model CP0/CP1 pilot and its acceptance criteria before any code work. Error tolerances and representative model/performance budget are to be agreed, not inferred from the video.
