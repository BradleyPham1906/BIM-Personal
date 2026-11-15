# V238 — Design evaluation and alternative comparison

## Decision and verdict

**Question:** How should the platform compare design alternatives without presenting an opaque AI score as a design decision?  
**Verdict:** Build a reproducible evidence and comparison layer. Preserve hard-constraint failures, normalize only compatible metrics, show Pareto trade-offs, record assumptions and uncertainty, and require a named human approval. AI may explain findings but cannot approve the design.

## Evidence

GSA's concept process requires the program, adjacency and functional requirements to be demonstrated and calls for at least three distinctly different preliminary schemes with massing, site context and enough narrative for comparison. Reviews consider siting, programming, engineering, performance, budget and schedule.[^https://www.gsa.gov/system/files/P100+2024+Final+(1).pdf]

RAIC recommends comparing schematic alternatives by program and budget completeness, adjacency, sustainability, net-to-gross efficiency and circulation-to-usable-area ratio.[^https://chop.raic.ca/chapter-6.2]

RIBA Stage 2 uses iterative design reviews; Stage 3 tests and validates the accepted concept through design studies and engineering analysis.[^https://www.riba.org/media/syneeeto/2020ribaplanofworkoverviewpdf.pdf]

Wortmann's seven-problem benchmark found that genetic algorithms performed poorly under a 500-evaluation budget and recommends testing multiple methods; deterministic direct search can be useful when stability matters and model-based search can perform well when simulations are expensive.[^https://academic.oup.com/jcde/article/6/3/414/5732355]

## Evaluation model

Separate results into:

- **Hard gates:** site/legal exclusions, mandatory spaces, mandatory separations, required access and approved information requirements.
- **Program:** area variance, capacity, missing spaces, departmental totals and grossing.
- **Relationships:** weighted adjacency satisfaction, required-edge failures and separation conflicts.
- **Flow:** path coverage, travel distance, crossing conflicts and unresolved vertical transitions.
- **Site:** suitability, access, orientation and opportunity/constraint response.
- **Planning:** compactness, net/gross, circulation ratio and floor-plate depth.
- **Information quality:** provenance, completeness, confidence and unresolved assumptions.

Do not roll hard-gate failures into an average score. Do not compare metrics with different units without documented normalization. Show absolute values beside normalized views.

## Alternative generation and comparison

- Start with seeded sampling across bounded variables.
- Filter infeasible candidates using hard constraints.
- Display non-dominated alternatives with a Pareto filter.
- Use pattern search for stepped local refinement.
- Add heavier algorithms only after benchmarking against the actual evaluation cost and variable structure.

Each run records input revision, seed, engine version, criteria, weights, normalization, elapsed time and result set. Re-running the same case must reproduce the same values.

## Human decision and transparency log

For each approved alternative, record:

- decision owner and reviewers;
- compared alternatives;
- decisive criteria and trade-offs;
- waived requirements and rationale;
- uncertainty and missing specialist input;
- chosen alternative and rejected alternatives;
- monitoring or downstream validation required.

## Acceptance criteria

- At least three alternatives can be compared against the same frozen criteria set.
- Every metric links to source inputs and calculation method.
- Independent recomputation of fixture cases matches displayed results.
- A sensitivity view shows how reasonable weight changes affect ranking.
- The system distinguishes measured, simulated, assumed and AI-inferred values.
- Pareto and metric views do not conceal infeasible candidates.
- An accountable human must approve, revise or reject the recommendation.
- Approval freezes a decision snapshot without preventing later controlled change.

## Risks

Metrics can create false precision and encode stakeholder bias. Normalization and weights can reverse rankings. Early energy, daylight or circulation estimates may be too coarse for consequential claims. Validation fixtures must include opposing trade-offs, missing data and deliberately invalid designs. The final product should state what evidence would change the recommendation.
