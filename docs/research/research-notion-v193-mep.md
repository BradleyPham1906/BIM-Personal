## Abstract

The question is how World BIM can author connected ducts and pipes and compute useful, inspectable pressure-loss estimates without mistaking a picture of a run for a validated hydraulic system. Recommend a staged, **proposed** implementation: keep MEP as the owner-selected discipline; derive an explicit, inspectable topology from compatible snapped centerlines for a small single-source tree; calculate flow and **straight-run friction only** with explicit assumptions; refuse ambiguous connections, unsupported loops and transitional cases rather than inventing results. A later choice can add persisted explicit connectors, actual fitting objects and coefficient-based local losses. The existing V138 note contains a consequential oversimplification: applying Colebrook to every Reynolds number above 2,300 jumps across a region where the conventional fully developed circular-pipe result is uncertain; it also does not establish that 64/Re is valid for every rectangular section. A published circular-pipe worked example and a separate Moody-chart point agree approximately with the numerical check performed here. No actual application behavior, full current codebase, browser performance, professional design approval or independent second-reader review is claimed. **This research is not yet protocol-complete or an approved work order.**

## 1. Questions and hypotheses

**Primary questions.** What should a run and its connections mean? How should branch flow and critical-path friction be calculated, checked and presented? What evidence is sufficient for a specification, and where must the program refuse? What from the existing research and app is reliable enough to reuse?

| Claim that could be falsified | Outcome from this work | Evidence and confidence |
| --- | --- | --- |
| A graphic polyline alone is a valid system and tells us what it connects to. | Rejected as a general claim: compatible port/system semantics and explicit connection relationships convey information that visual intersection alone does not. | P: IFC ports and system documentation; high for the semantic distinction, not an implementation decision. |
| Every Re ≥ 2,300 is safely evaluated as a fully turbulent circular-pipe Colebrook result. | Rejected as a general engineering guarantee; Purdue describes approximately 2,300–4,000 as laminar-to-turbulent transition and its stated Colebrook formula for Re > 4,000. | P: Purdue pipe-flow reading; high for that source's domain. An application threshold is still a proposed conservative policy. |
| Laminar 64/Re with hydraulic diameter is automatically valid for rectangular ducts. | Not established; the Purdue derivation is explicitly circular. ASHRAE discusses hydraulic-diameter correlation for typical **turbulent** duct data, not a universal extension of the circular laminar result. | P: sources read; medium-high for rejecting unsupported generalization, not a rectangular laminar design formula. |
| Straight friction is the whole system pressure loss. | Rejected; fitting, terminal, device and elevation effects can matter. | P: ASHRAE duct design and TU Delft; high. |
| Equal hydraulic diameter and equal-friction equivalent diameter are the same concept. | Rejected: ASHRAE treats hydraulic diameter and equivalent round diameter for equal flow/resistance separately. | P: ASHRAE §§3.1, noncircular ducts; high. |
| A separate topology can use the existing BIM dependency graph unchanged. | Not established. The inspected dependency graph expresses change propagation, not MEP fluid connections; loops have different meanings. | P: app code as read on main; high for this file's stated function, low for all other code. |
| A scripted circular-pipe result agrees approximately with external worked data. | Held for the specific published TU Delft example and Purdue Moody chart comparison below. | P: own script plus educational sources; medium: no second independent reader and no app execution. |

## 2. Method and reproducibility

**Date and source scope:** 2026-11-13. Read the original [V138 research note](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-mep-runs.md), [project research protocol](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-protocol.md), [work-order workflow](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/work-orders/README.md), relevant [project instructions](https://github.com/BradleyPham1906/BIM-Personal/blob/main/CLAUDE.md), the MEP task and the [pipeline](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/dev/PIPELINE.md). Read practitioner and educational fluid sources plus IFC source definitions below. Read one app file and directory listings, not the entire app. Research experiments are data-only Python 3.13.15 and are supplied as `checks.py` and `results.json` with this record; no application build or app tests were run.

**Search log.** Search: “buildingSMART IFC distribution systems ports connectivity” and “MEP BIM duct pipe fittings IFC systems”; kept buildingSMART system and port-relationship definitions as semantic primary sources. Search: “ASHRAE duct design fittings loss methods”; kept ASHRAE Fundamentals chapter 21, directly read sections 3.1–3.3 and supporting tables. Search: “NIST pipe flow friction factor Colebrook equation Reynolds” and “engineering pipe laminar turbulent Colebrook equation Moody hydraulic diameter”; directly read Purdue pipe-flow notes and TU Delft friction chapter, not the search snippets. Looked specifically for limits opposing the original simple Reynolds split and rectangular-diameter assumption: Purdue gives a transitional range, and ASHRAE distinguishes turbulent hydraulic-diameter correlation from its rectangular equal-friction equivalent. Search results not read in full are not evidence here.

**Independent check:** None by a separate researcher. The script compares our calculation with published examples and contains internal consistency assertions, but it is not an independent engineering review and does not meet the protocol's required separate reader or broad parallel research. Source versions on `main` are unpinned web reads, and current repository state or unpublished branches may differ.

**Numbering warning:** This task is labeled V193 in Notion; the current pipeline shows “MEP runs” at ordered position 201 and states table numbers are order, not phase numbers. Do not silently rename the task or assume the earlier number is an assigned future version. Confirm version at phase start.

## 3. Findings: practice and semantics

### 3.1 A system is not a set of intersecting lines

The original V138 note proposes ducts and pipes under one MEP discipline, with HVAC and plumbing groups, runs storing centerlines, sizes and system classifications, and a flow display. It proposes deriving connections, a single source and terminal-demand aggregation; it explicitly leaves fitting pressure losses, risers, sizing, drainage, equipment families and IFC semantic export for later. This is **a prior design proposal**, not proof of implemented behavior. The user's one-discipline choice is recorded there. P for what the note says, U for current runtime behavior.

The IFC 4.3.2 development documentation's [IfcDistributionSystem](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDistributionSystem.htm) describes a distribution network and grouping of distribution elements. [IfcRelConnectsPorts](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRelConnectsPorts.htm) is an explicit relationship between two ports; ports are nested within distribution elements. These are schema semantics, not proof that implementing the following model constitutes a conformant IFC export. Record exact schema/version and model-view requirements and test a target reader before claiming IFC support. The particular online documentation identifies itself as a development build, so pin an approved target version before an interoperability specification.

A connector must eventually distinguish at least owner element, domain (e.g., air/water), system classification, location, direction if defined, profile/size, and its connection state. A crossing in plan is not a connection without compatible elevation and a permitted node. Geometric proximity can supply candidates; it does not establish intent. A visible diagnostic should identify incompatible or ambiguous candidates. A saved physical relationship can preserve intentional connection across edits but adds migration/repair costs. Do not use geographic intersection alone as a substitute for a fitting, a hydraulic design or a valid manifold.

### 3.2 Change propagation versus fluid topology

The inspected [`dependency-graph.js`](https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/bim/dependency-graph.js) states that its edges express “depended-on → depends-on-it,” are rebuilt from the live model rather than stored as a parallel copy, and use a topological traversal with cycle reporting for change propagation. Its `bimGraphBuild`, `bimGraphDownstream` and `bimGraphTopoOrder` are useful precedents for visibility, stable identifiers and cycle handling. They are **not** automatically the correct MEP graph: a physical loop can be a valid hydraulic network, while a dependency cycle has a different purpose and failure mode. Reuse or integrate its propagation pattern only after examining the whole flow and undo architecture. P for the inspected file; U for any uninspected connector implementation.

The [bim directory listing](https://github.com/BradleyPham1906/BIM-Personal/tree/main/src/js/engine/bim) and [unit-test listing](https://github.com/BradleyPham1906/BIM-Personal/tree/main/tests/unit) show no obviously named MEP file, but a directory-name observation cannot prove that the app has no MEP code elsewhere. The [README](https://github.com/BradleyPham1906/BIM-Personal) says source is under `src/`, the generated HTML is built from it, and tests run under Node. It is not a substitute for a complete current-code audit.

## 4. Engineering basis and boundaries

### 4.1 Straight, circular pressure pipe

For steady, fully developed, single-phase, incompressible Newtonian flow under the chosen assumptions, use SI internally and label Darcy's friction factor:

- `A = π D²/4`, `V = Q/A`, `Re = ρ |V| D/μ`.
- `Δp_f = f_D (L/D) ρV²/2`; `h_f = Δp_f/(ρg)` when pressure/head conversion is required.
- Laminar, fully developed **circular** flow: `f_D = 64/Re`, consistent with `Δp = 32 μ V L/D²` ([Purdue §§11.2–11.4](https://engineering.purdue.edu/~wassgren/teaching/ME30800/NotesAndReading/PipeFlows_Losses_Reading.pdf)).
- Turbulent circular flow: solve `1/sqrt(f_D) = −2 log10(ε/(3.7D) + 2.51/(Re sqrt(f_D)))`. Purdue states this relation for Re > 4,000; ASHRAE and TU Delft use the same Darcy/Colebrook basis for their respective domains. Explicitly report convergence and relative residual. Different sources can use different rounding constants and chart-reading approximations.

Inputs are **inside** diameter, length, flow, density, viscosity and effective roughness in declared units. A nominal pipe size is not necessarily its inside diameter. Roughness varies with material, lining, age and condition. Fluid property defaults are assumptions, not manufacturer data; record temperature, source and whether the user changed them. The units `μ` (Pa·s) and `ν` (m²/s) are not interchangeable; `ν = μ/ρ`. Distinguish Darcy and Fanning factors (`f_D = 4 f_F` under these definitions). A silent factor-of-four mixup produces a serious error. Reject nonpositive diameter, density or viscosity, negative physical length or roughness, nonfinite inputs, invalid solver convergence, and physically incompatible assumptions. At zero flow, return a zero-friction result with undefined/omitted friction factor and Reynolds number rather than dividing by zero. Reverse flow requires a consistent signed direction convention; loss magnitude is not a negative friction loss.

For approximately Re 2,300–4,000, the conservative **proposed** first implementation should display an indeterminate regime rather than selecting laminar at 2,299 and Colebrook at 2,300 with no qualification. This is a product safety decision, not a universal standard. Confirm thresholds, fluid types, uncertainty language and any later transition model with a qualified engineer.

### 4.2 Ducts and rectangular sections

ASHRAE Fundamentals 2025, chapter 21 §3, distinguishes friction in straight sections from local dynamic losses. Its hydraulic diameter `D_h = 4A/P` for a rectangular section equals `2ab/(a+b)`; its discussion describes turbulent rectangular-duct correlation using hydraulic diameter subject to empirical uncertainty. An equivalent round diameter defined for **equal flow, resistance and length** is a different quantity; using it with actual area/velocity in the wrong formula mixes two conventions. Geometry, units and cross-section must be explicit. Do not automatically assert `64/Re` for laminar rectangular flow; obtain a shape-dependent method or flag unsupported. High-confidence source interpretation, but no rectangular worked example was independently executed here.

ASHRAE's fitting coefficients relate a particular fitting's loss to the velocity pressure at a **specified reference section**. A tee has separate branch and main characteristics, and geometry and flow ratios matter. Do not combine a coefficient with an arbitrary velocity, or invent fitting values merely because a bend is shown. A coefficient database may be proprietary; review license, edition, access and redistribution before incorporating or publishing any table. A visual elbow is not evidence of a manufactured fitting with known loss.

### 4.3 What is not calculated

Friction-only values exclude bend, tee, entrance/exit, transitions, filters, valves, coils, diffusers, equipment losses, static elevation where relevant and other system effects. Results can therefore be materially incomplete and must not be described as a complete system pressure, pump/fan duty, pipe sizing, code compliance or approval. Sum along a specific path, not across mutually exclusive branches. Static pressure, total pressure, head and energy grade are related but not interchangeable labels. Refrigerant, compressible/transient flow, water hammer, multiphase flow, gravity sanitary drainage and thermal effects need other models. Do not treat gravity drains as pressure-pipe Darcy calculations.

Hazen–Williams is an empirical water-pipe relation with its own assumptions, units and C coefficient. TU Delft presents it for preliminary estimates and cautions that viscosity/temperature effects are not captured in the same manner. It is not an independent gold standard for every fluid or proof that either model is correct. If later shown, label it as an additional method with input provenance, not as verification of an arbitrary fluid. No automatic C value or normative adoption is approved here.

## 5. Alternatives against criteria

Criteria: preserves intent, handles editing and ambiguity, avoids a second source of truth, gives debuggable results, stays bounded for the browser CAD architecture, and leaves a path to interchange. Scores are qualitative; no runtime or cost measurement has been made.

| Option | Benefits | Risks / change required | Assessment |
| --- | --- | --- | --- |
| Derive all connectivity from geometry | Fits existing derived-graph precedent, fewer persisted records | Ambiguous overlaps, near misses, tolerance drift, intentional nonconnections and edits can silently change topology | Suitable only with deterministic candidates, explicit warnings and a bounded tree; verify with fixtures |
| Persist explicit connectors and relationships | Preserves intentional connections and supports equipment/IFC mapping | Stable IDs, file migration, edit repair, delete/undo and interchange policy required | Best long-term expressiveness; not yet proven within current model |
| Hybrid: derive candidates, persist user-confirmed relationships | Explains and preserves intent, can check drift after edits | Adds state/migration plus UI; needs robust stale-connection policy | Recommended **candidate** when actual code/storage contract is understood |
| Visual-only polylines | Smallest initial drawing change | Provides no defensible system/flow model | Acceptable drafting-only slice if no analysis claim is made |
| General nonlinear looped hydraulic solver | Broader network class | Requires boundary conditions, convergence, equipment curves and independent engineering validation | Exclude from first slice; not a simple extension of a tree sum |

Recommendation changes if the current app already has a stable explicit connector store, if intentional nonconnections are core, or if equipment families are included at launch. Do not put a guessed file or function in a work order: [work-order README](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/work-orders/README.md) requires specific scoped files and tests, and the code audit is not complete.

## 6. Proposed algorithm and data contracts

**Run input, proposed not code:** stable object ID; discipline/domain; system ID/classification; ordered 3D centerline in project units; profile (round or rectangular), **internal** dimensions and units; fluid and roughness provenance; declared terminal flow where applicable; active level/layer. Do not force a default elevation to be correct for all projects. A run can be present without being analyzable. A candidate connector carries owner, endpoint or attachment parameter, 3D location, compatible domain/system and diagnostic status. Keep generation settings and tolerance in the result, not hidden globals.

**Build candidate graph:** normalize units; validate segments and reject repeated/zero-length segments. Split every run at accepted endpoints/tees and bends so each analytical edge has known physical length, profile and flow. Spatially index candidates rather than naïvely comparing all pairs on large models; actual complexity and performance are unmeasured. Check 3D distance and compatibility separately. A line crossing in XY with distinct Z is not a joint. Record candidate ambiguity rather than choosing whichever object happened to be iterated first; require an explicit rule for connection tolerance, snapping and manual disconnection. Ensure deterministic output for shuffled input order.

**Validate before solving:** identify connected components and their sources and terminals; distinguish unconnected end from defined terminal demand. For the proposed first solver require one explicitly identified source, an acyclic tree and a known nonnegative terminal demand. A run's drawn direction is not automatically proof of the real flow direction. Reject or mark not analyzed for multiple sources, cycles, missing demand, incompatible systems, ambiguous joints, unsupported dimensions or zero-area sections. A component can be viewable without a valid calculation.

**Aggregate:** traverse from leaves toward source; for constant-density, conserved flow with no storage/leakage, `Q_parent = sum(Q_children)` for a branch point. This is a supplied-demand model; it does not solve distribution based on pressure or satisfy terminal balance automatically. Derive each section's area, velocity, Reynolds number, regime, Darcy factor and friction loss. For each source-to-terminal path sum its own segment friction exactly once; identify the maximum **friction-only path**, not the full design index circuit. Return path IDs and section-by-section quantities, input provenance, methods, exclusions, warnings and error statuses. Round only for display; preserve precision for calculation. Report a result stale when connected geometry, fluid, size, terminal flows or topology changes.

**Edit lifecycle:** preview connection changes; persist an intentional relationship only if that design is approved; update/invalidate affected calculations on geometry, system, size or unit edits; handle delete, copy, undo/redo, save/reload and old-file migration atomically. Display every unresolved connection and calculation refusal rather than silently dropping a node. Current persistence, history, rendering and object contracts must be audited before concrete files or function names can be committed.

## 7. Experiments and raw numbers

Single deterministic run, Python 3.13.15, standard library only, no application code or browser. Script and exact JSON are attached; these are research fixtures, not a software test suite.

**Check A — published Moody chart.** Purdue's chart exercise gives approximately `f_D ≈ 0.0225` at `Re = 100,000`, `ε/D = 0.001`. Bisection on the implicit Colebrook equation produced **0.0221745359**, 1.45% below the chart value; equation residual rounded to zero at Python floating-point precision. This is consistent with a rounded visual chart but does not prove every case or distinguish implementation bugs shared by similar equations.

**Check B — TU Delft worked example 1.** Published input: `Q=0.3 m³/s`, `D=0.593 m`, `L=400 m`, `ε=0.0001 m`, kinematic viscosities `1.52×10⁻⁶` and `0.9×10⁻⁶ m²/s`. The cited example uses an explicit approximate factor and reports **0.62 m** and **0.60 m** head loss. Our direct Colebrook bisection produces **0.624412 m** at 5°C and **0.595222 m** at 25°C. Differences are about 0.0044 m and −0.0048 m; do not present them as exact verification because the source rounds and uses an approximation. No fitting losses are included.

**Check C — laminar closed-form identity.** At Re = 1,000 for a 0.1 m circular pipe and the script's fluid inputs, `64/Re` in Darcy–Weisbach and the Poiseuille expression both give **0.321860629 Pa** over 10 m. These are algebraically related, not independent experimental corroboration. It does not validate rectangular laminar flow.

**Check D — hypothetical branch paths.** For 0.1 m inside diameter, trunk 10 m with `Q=0.010 m³/s`, branch A 5 m with `Q=0.004`, branch B 8 m with `Q=0.006`, water assumptions `ρ=998.2 kg/m³`, `μ=0.001002 Pa·s`, `ε=0.0000015 m`, computed straight losses are trunk **1393.399 Pa**, A **135.142 Pa**, B **445.722 Pa**. Summed paths: **1528.541 Pa** to A and **1839.121 Pa** to B. These are assumed terminal flows and pipe properties, not a balanced network solution, actual layout or app result. Branch B has the larger friction-only path under these assumptions; fitting/equipment losses could change the real design index.

## 8. Edge cases and proposed acceptance tests

The following are **not executed app tests**. Tests should state input, expected status/result and reproducibility, and be placed in approved files only after the app contract is audited.

1. Pure graph fixtures: single run, equal/unequal tee, two independent trees, terminal without demand, multiple sources and a loop. Confirm aggregation and the specific refusal reasons, not just a boolean success.
2. Three-dimensional topology: same-XY different-Z crossings; end-to-end, endpoint-to-middle tee, overlapping collinear segments, reversed points, duplicate points, zero-length segments, and candidate ties. Vary and record tolerance; shuffle input order and expect identical canonical graph and diagnostics.
3. Fitting geometry: mismatched duct/profile, pipe nominal versus internal size, incompatible domain, nearby but intentionally disconnected ends, a tee too close to a bend, a missing or changed referenced connector. No implicit fabricated fitting or zero-loss claim.
4. Calculation: A–D above; additional independent published rectangular duct case; Reynolds values on both sides of approved laminar/transition/turbulent boundaries; zero flow, negative flow direction, zero diameter, nonfinite input, roughness and viscosity extremes, and failure to converge. Compare SI and imperial conversions using full-precision internal units.
5. Path behavior: a shared trunk is counted once per path, unequal branches are not summed into one serial path, equal path losses have deterministic tie handling, and a change in a terminal flow invalidates all dependent upstream results. No full-system pressure label when loss contributors are missing.
6. Persistence and undo: create, connect, disconnect, move, resize, change classification, clone, delete, save/reopen and undo/redo. Check stable identities, stale results, topology, migration and diagnostic preservation, with no accidental edits to unrelated objects or layers.
7. Browser interaction: independently inspect table columns, units, source assumptions, warning prominence, zero/unsupported statuses, mobile layout, keyboard access and screen-reader labels when the feature exists. For new interfaces follow the repository's current stated browser-check rule; do not infer permission to run a full regression.
8. Scale: record network size, device/browser/build, load and recompute time, memory, invalidation scope and p95 interaction latency. Set acceptable budgets before testing. No numeric performance claim is made here.

## 9. Risks, threats to validity and unresolved work

- **Engineering misuse:** friction-only or synthetic results can appear authoritative. Mitigate through a persistent incomplete-analysis label and an explicit qualified-review gate; product copy needs owner and engineering approval.
- **No full code audit:** one dependency-graph file and three listings do not establish the current run, units, rendering, persistence, IFC or test implementations. Inspect them before naming SPEC functions/files.
- **Unpinned sources:** `main` and IFC development documentation may change; pin a commit and approved standard edition, and distinguish publication date from retrieval date.
- **No independent reader:** external examples are comparisons, not a second researcher checking every claim. The protocol remains unmet.
- **No real application tests:** all numerical work is isolated; no test establishes app accuracy, operation speed, browser support, or UI behavior.
- **No place-specific design code review:** IFC is an interchange schema, not a mechanical code. Determine jurisdiction, adopted edition, local amendments and professional responsibility when product scope is defined. Do not assume ASHRAE is adopted law.
- **No exhaustive source and license assessment:** ASHRAE tables, IFC specifications, any library and any vendor component have distinct terms; the free availability of a web page does not grant unrestricted redistribution.
- **Scope and number:** MEP phase/version and whether it overlaps prior V138 proposal need confirmation at execution. Rough 32-hour task effort is a backlog placeholder, not an estimate grounded in this analysis.

## 10. Decisions needed before specification (not answered here)

1. Initial deliverable: drawing-only, user-checked tree analysis, or full network analysis? Which air and water systems and profiles are in scope?
2. Connection contract: entirely derived, explicit persisted, or hybrid? What tolerance, snapping, ambiguity and intentional-disconnect rules apply?
3. Are physical fittings generated, modeled as visual placeholders, or excluded? If modeled, where do approved coefficient data and rights come from?
4. Which fluid properties, temperature/roughness sources and input units are supported? What is the transition-regime policy and what calculation confidence language is required?
5. Should risers and elevation effects, rectangular ducts, equipment and IFC semantics be included now or explicitly deferred? Which jurisdiction and professional reviewer apply?
6. What error, data completeness, latency and accessibility criteria are acceptable, and who approves the outcome?

These are framed for eventual owner decisions, not assumed approvals. The user's request to proceed without questions authorizes research, not inventing answers or changing engineering safety criteria.

## 11. References and evidence levels

- P — Original repository [V138 research](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-mep-runs.md), full note as read, for prior proposal and owner discipline choice; retrieved 2026-11-13.
- P — Repository [research protocol](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-protocol.md), full note, and [work-order workflow](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/work-orders/README.md); read 2026-11-13.
- P — Repository [pipeline](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/dev/PIPELINE.md), excerpts on ordered MEP item and phase numbering; retrieved 2026-11-13.
- P — Repository [dependency graph code](https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/bim/dependency-graph.js), `bimGraphBuild`, `bimGraphDownstream`, `bimGraphTopoOrder`, read as text, unpinned `main`; 2026-11-13.
- P — ASHRAE, [2025 Fundamentals Chapter 21, Duct Design](https://handbook.ashrae.org/Handbooks/F25/SI/F25_Ch21/F25_Ch21_si.aspx), §§3.1–3.3, hydraulic diameter and local-loss context; retrieved 2026-11-13.
- P — Purdue, [Pipe Flows](https://engineering.purdue.edu/~wassgren/teaching/ME30800/NotesAndReading/PipeFlows_Losses_Reading.pdf), §§11.2–11.4 and Moody exercise `pipe_49`, circular laminar and turbulent limits; retrieved 2026-11-13.
- P — TU Delft OpenCourseWare, [Friction Losses in Pipelines](https://ocw.tudelft.nl/wp-content/uploads/Friction_losses_in_pipelines.pdf), §§10.1–10.3, 10.6 example 1; retrieved 2026-11-13. OCR extraction of some equations was imperfect, so numerical input and example text were cross-checked against the clearly extracted values; this report does not use corrupted OCR symbols as a normative transcription.
- P — buildingSMART [IfcDistributionSystem](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDistributionSystem.htm) and [IfcRelConnectsPorts](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRelConnectsPorts.htm), IFC 4.3.2 development documentation; retrieved 2026-11-13.
- U until independently reviewed — research scripts and resulting calculations attached to this record; input assumptions and numerical derivations are inspectable, but the protocol requires a separate reader and relevant app tests.


---
Research evidence files: [`experiments/notion-v193/`](experiments/notion-v193/). Original scripts and results reflect only the experiments described above.
