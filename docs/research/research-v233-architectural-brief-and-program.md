# V233 — Architectural brief and program

## Decision and verdict

**Decision owner:** Brad Pham.  
**Question:** What minimum programming model should precede architectural design in World BIM Platform?  
**Verdict:** Build a versioned requirements-and-program subsystem before adjacency or layout generation. It should remain the source of truth for spaces, quantities, capacities, areas, goals, constraints, provenance, approvals and changes. Do not treat an imported spreadsheet as the durable model.

## Evidence

WBDG defines architectural programming as the research and decision-making process that identifies the scope to be designed. Its six steps are: research the project type, establish goals, gather information, identify strategies, determine quantitative requirements and summarize the program. It also calls for stakeholder participation, space criteria, typical spatial relationships, site requirements, net-to-gross calculations and client sign-off.[^https://legacy.wbdg.org/design-disciplines/architectural-programming]

RIBA Stage 1 requires a Project Brief containing outcomes, quality aspirations and detailed Spatial Requirements tested against budget and site information. RIBA distinguishes briefing from design: the brief must be sufficiently developed before Concept Design begins.[^https://www.riba.org/media/syneeeto/2020ribaplanofworkoverviewpdf.pdf]

GSA requires area to be checked at every design phase against the approved program and notes that plan configuration, circulation and floor-plate depth determine efficiency.[^https://www.gsa.gov/system/files/P100+2024+Final+(1).pdf]

## Recommended domain model

- **ProjectBrief:** purpose, outcomes, budget, schedule, site, applicable standards and approval state.
- **StakeholderNeed:** person/group, need, priority, source, date and decision owner.
- **Requirement:** stable ID, statement, type, mandatory/preferred, measurable criterion, source, confidence, status and supersedes link.
- **SpaceType:** functional category and reusable default criteria.
- **SpaceRequirement:** name/number, quantity, capacity, target/min/max net area, department, level preference, daylight/acoustic/security/accessibility criteria and equipment implications.
- **AreaModel:** net assignable area, departmental grossing, circulation/service allowance, gross target and chosen measurement standard.
- **ApprovalSnapshot:** approved revision, approver, date, exceptions and rationale.

Every imported row receives a stable key and provenance. Manual edits remain distinct from imported values so re-import can present differences rather than silently overwrite work.

## Workflow

1. Import or enter the brief and program.
2. Classify unresolved values as unknown, assumed or confirmed.
3. Validate duplicates, missing quantities, impossible ranges and unit mismatches.
4. Calculate net program, allowances and gross target without pretending one universal grossing factor applies to every building type.
5. Review goals, site constraints and space criteria with stakeholders.
6. Freeze an approved program revision while allowing a later controlled revision.

## Acceptance criteria

- Round-trip CSV/JSON import and export preserve stable IDs, units and provenance.
- Quantity × area totals reconcile with department and project totals.
- The user can compare current, imported and approved revisions.
- Every requirement identifies its source or is explicitly marked as an assumption.
- Unknown values remain visible; the engine never invents precision.
- The phase produces a machine-readable program and a human-readable brief summary.
- No adjacency or geometry is required for V233 to be complete.

## Alternatives considered

- **Spreadsheet only:** familiar but weak for identity, traceability and iterative regeneration; rejected as source of truth.
- **IFC spaces first:** premature because a program may exist before geometry or storey assignment; defer mapping to V237.
- **One generic Requirement object only:** flexible but hard to validate; use typed requirements plus extensible custom fields.

## Risks and open decisions

Area standards differ by jurisdiction and client. Grossing factors must be project data, not embedded universal defaults. Building-type templates should be references, never automatic regulatory claims. Brad must approve the initial relationship vocabulary, unit policy and approval workflow before implementation.
