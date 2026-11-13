# Later: Costs and pro forma — development feasibility by usage

## 1. Abstract
How should a usage-based project feasibility model consume V160's yield without confusing geometry assumptions, construction cost, operating income and property value? Recommend a transparent, scenario-versioned, unlevered stabilized income and sales model first, with explicit basis and provenance for every rate, reconciled quantity rollups and no return where inputs are missing. This is a development feasibility study, not the separate element-linked 4D/5D construction planning phase, a valuation, an investment recommendation or an approved spec. A synthetic worked model was executed; the World BIM application, an independent financial model and the research-protocol second reader were not.

## 2. Research question and hypotheses
- H1: V131 already contains usage assumptions and a formula evaluator, so a feasibility feature should reuse rather than duplicate the measurement pipeline. Supported by pinned app code; implementation completeness needs execution tests. P/high.
- H2: GBA, zoning GFA and rentable/saleable area are interchangeable. Rejected: usage ratios are assumptions and local regulatory definitions differ. P/high for observed source definitions.
- H3: Rent, sale revenue, NOI, cost and capitalization are interchangeable metrics. Rejected: they have different time periods and bases. P/high within the illustrative practitioner model.
- H4: A positive unlevered yield on cost proves the project is financeable. Rejected: timing, financing, uncertainty, market and other costs are not represented in a stabilized yield.
- H5: A historical rent or cost in an outside study can be used as a current project default. Rejected; all monetary assumptions must be project/date/currency specific.

## 3. Methods and search log
2026-11-13 searched `real estate pro forma net operating income capitalization rate expenses`, `zoning envelope building massing floor area ratio setbacks`, `parking lot design angle dimensions ADA accessible spaces`. Read the 2018 Leland Consulting Group draft feasibility report pp. 4, 8, 14, 20; Palmdale measurement guide; V131 research, and `usages-live-areas.js` and V160 zoning source at commit `95b7aee4db8be1fc28c0fbe7befc7407fabd1dda`. Used a synthetic Python calculation and saved raw output in `experiments/notion-later-20261113/`. No actual app cost engine, realistic deal dataset, valuation or independent professional review was run. Search summaries were leads, not evidence. No second independent reader; protocol exit remains open.

## 4. Findings and proposed calculation contract
### Actual app basis
[P/high] `usages-live-areas.js` stores each usage with GBA→GFA and GFA→NSA assumptions, floor-to-floor height, parameters and user formulas. It measures rooms as NSA only, while floors and masses get area conversions. Aggregation iterates all eligible usage-tagged objects and sums per-object results; it does not infer that rooms are already inside counted masses. An overlapping room and mass may therefore represent different views of one physical area and must not both flow into the same financial basis without a selection/ownership policy. Formulas are evaluated object by object and summed; `sum(floor(NSA/unitSize))` can differ from `floor(sum(NSA)/unitSize)`. Do not silently substitute aggregate logic. [V131 code](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/bim/usages-live-areas.js); [V131 research](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/docs/research/research-usages.md).

[P/high] V160 produces an achievable numerical area limited by FAR and envelope; it is an estimate of capacity, not a proven designed building. Feasibility must identify source as `zoning potential`, `generated design` or `measured as-designed` and prohibit summing overlapping alternatives. [V160 code](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/site-analysis/zoning-envelope.js).

### Professional scope and units
[P/high] The State Street feasibility example models program, parking, timing, land, site preparation, hard/soft cost, revenue, vacancy, expenses and NOI. It distinguishes apartment monthly rent from commercial annual rent and full-service office from NNN retail; treat those as assumptions in that 2018 study, not universal lease rules or current rates. It compares NOI with total project cost as return on cost. [Study pp. 4, 8, 20](https://www.ccdcstatestreet.com/wp-content/uploads/2020/05/State-Street-Development-Feasibility-Analysis-06-2018-v03.pdf).

[P/high] Palmdale's local definition uses net lot area and specific floor-area inclusions/exclusions. A user-defined usage GFA ratio is not evidence that a code-defined GFA requirement is satisfied. [Guide](https://www.cityofpalmdaleca.gov/DocumentCenter/View/15699/Zoning-Measurements-How-to-Guide-PDF).

[U/proposal] Separate building program, assumptions and scenario snapshots. A rate must specify amount, currency, denominator (m² or ft² of exact area basis, unit, parking stall or lump sum), interval (month/year/once), effective date, source/author, jurisdiction and confidence, escalator and scenario revision. Convert area and time exactly once. Mark estimates, user edits and missing values; no stale hidden defaults. Define local regulatory GFA separately from measured gross and lettable/saleable. Specify the source of residential units and treatment of partial floors. Reject negative or nonsensical rates, nonfinite numbers, zero cap rate and mismatched currency rather than producing infinity or false zero.

### Baseline model
[U/proposal] For each rental use compute potential gross rent = leased area × annual rate OR unit count × monthly unit rent × 12, not both; add distinct parking/other income. Apply vacancy and collection loss once by income line; add explicitly documented recoveries/other income to obtain effective gross income. Annual operating expenses require line-item basis, exclusions and lease responsibility, and must not be subtracted twice under NNN. `NOI = effective gross income − operating expenses` under the selected accounting definition. Keep income taxes, debt service, depreciation, capital expenditure and reserves explicitly classified instead of silently including/excluding them. The budget is land + site + hard + soft + finance/carry + contingency + selling costs, with bases made explicit and no double counting. `Yield on cost = stabilized NOI / total development cost`, only if all material inputs and denominator are valid. `Indicative value = stabilized NOI / cap rate` is a simplified income capitalization scenario, not an appraisal; no app claim of valuation accuracy or marketability. Sales proceeds by use = approved sellable area × price per area or units × price per unit; less costs exactly once. Never add asset value and sale proceeds for the same property; model mixed rental and for-sale portions separately. NPV/IRR, construction cash flow, financing and taxation require an independently reviewed dated cash-flow model and are a later extension, not implied by this snapshot.

## 5. Alternatives compared
Criteria: traceability, transparency, timing fidelity, reuse and scope.
| Alternative | Benefit | Trade-off |
| --- | --- | --- |
| Per-object usage formulas alone | Already present and editable | Weak units, double-counting risk, no scenario lineage or cash-flow semantics |
| Typed stabilized feasibility snapshot | Explicit source, calculation and scenario comparison | Not a finance or timing model |
| Dated full cash-flow/financing model | Captures timing, debt and exit | Higher verification, accounting and professional-review burden |
| External spreadsheet import/export | Independent review possible | Version, mapping and formula reproducibility challenges |
Recommend typed stabilized snapshot plus auditable export and spreadsheet cross-check; defer full cash flow unless scope and validation justify it.

## 6. Worked synthetic example
Run `python3 experiment.py`: 100 apartments × $1,800/month × 12 = $2,160,000/year; retail 10,000 ft² × $30/ft²/year = $300,000; total potential gross $2,460,000. Apartment vacancy 5% and retail vacancy 10% give effective income $2,322,000; assumed annual operating expense $300,000 gives NOI $2,022,000. Land $6m + hard $14m + soft $3m + contingency $1m = $24m total; yield on cost 8.425%; simple NOI/6% cap = $33.7m. Synthetic input only, with no parking, tax, financing, escalations, construction interest, timing or exit costs; no independent spreadsheet or app execution. These assumptions do not establish economic feasibility.

## 7. Edge/acceptance matrix
- Annual vs monthly rates; ft² vs m²; gross vs net vs per-unit inputs. Test equivalent inputs, exact conversions and explicit displayed basis.
- Two 60 m² objects, unit size 100 m²: sum of object floor(60/100)=0, whereas floor(total/100)=1; select one policy, show it and test both. Never conflate.
- Measured rooms plus enclosing floor/mass: select one authoritative source per economic line; reject overlap or show explicit reconciliation.
- Null ≠ 0; missing rent, cap, costs, currency, dates or area: show unassessed and missing inputs, not a falsely complete return. Zero/negative denominator rejected.
- Multiple uses, vacant units and differing leases, NNN recoveries, sales-vs-rent exclusion, parking both line item and hard cost: reconcile every input and total, prevent duplicate income and expense.
- Fixed, percentage and per-unit cost basis; contingency base explicitly selected; calculate on unrounded intermediate values and round display consistently.
- Baseline/downside/upside scenarios, immutable inputs/source dates, compare revisions and stale geometry; no external market rates inferred.
- Reproduce the worked example and compare a second independently implemented spreadsheet; save/reopen, edit/undo, exports, large values and version migrations. Add real anonymized case and qualified professional review.

## 8. Work-order slices
A: audit V131 objects, V160 area outputs and existing persistence; document overlap and allocation rules. B: typed assumptions/lineage and unit conversion; reconcile mixed usage and project-vs-zoning source. C: implement one stabilized rental scenario with explicit missing-input handling, independent reference and export. D: add sales case separately without double counting, scenario comparison and sensitivity. E: only after evidence, propose dated cash flows and finance; construction 4D/5D remains its own work package. Historical 20 h was rough and is not a validated budget or promise.

## 9–11. Risks, open gates, decisions
No professional valuation review, market sources, current rates, real model, independent reader or app tests; sold standards and local measurement definitions were not surveyed comprehensively. Owner decisions: first jurisdiction/currency and target uses; preferred area standard and entity ownership; rent basis and lease assumptions; cost categories, source/version and escalation; whether sales, leverage or time phasing are required. Obtain independent finance/real-estate professional review before investment use. No owner approval is implied.

## 12. References
Accessed 2026-11-13: pinned [usage code](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/bim/usages-live-areas.js), [V131 research](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/docs/research/research-usages.md), [V160 code](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/site-analysis/zoning-envelope.js), [Palmdale guide](https://www.cityofpalmdaleca.gov/DocumentCenter/View/15699/Zoning-Measurements-How-to-Guide-PDF), [State Street draft development feasibility](https://www.ccdcstatestreet.com/wp-content/uploads/2020/05/State-Street-Development-Feasibility-Analysis-06-2018-v03.pdf). P for what these sources say; the baseline model and assumptions are U/proposals until independently verified.
