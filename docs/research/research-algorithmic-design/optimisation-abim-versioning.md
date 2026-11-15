# Optimisation, algorithmic BIM and IFC, version control of parametric definitions

Research notes, one of five parallel sides of `research-algorithmic-design.md`. Started 2026-11-14, continued
2026-11-15. Status: IN PROGRESS; parts are filled as sources are read. Levels: P = the source itself was read,
S = a dependable secondary work, U = seen only in a search summary or not reached.

Reading method: pages were fetched through a fetch-and-extract tool that returns the page's text answered
against a question; where that was the route, the reference says so. Numbers quoted from it are the paper's,
but a second reader should re-check any number the code will use.

## 1. Summary of findings (so far)

| # | Finding | Level | Confidence |
|---|---|---|---|
| F1 | Wortmann 2019 benchmarks nine solvers on seven simulation-based architectural problems (4 to 40 variables, structure, energy, daylight) at 500 evaluations, 20 runs each. The two genetic algorithms (Galapagos GA, SGA) are the worst overall; the model-based RBFOpt is the most robust and the fastest to converge after about the first 40 evaluations; DIRECT is best in those first evaluations and is the stable choice for few variables. | P | High for what the paper says; medium for generality (seven problems; the author led the tool that won, which the paper discloses) |
| F2 | The paper treats 500 evaluations as a compromise budget for practice, the same number as Wetter and Wright 2004, and says thousands of simulations are often impractical. | P | High |

## 2. Findings by topic

### 2.1 Optimisation benchmarks

**Wortmann 2019, "Genetic evolution vs. function approximation" (JCDE 6(3), 414-428), P.**

- Solvers: direct search DIRECT and SBPLEX (NLopt, through Goat); model-based RBFOpt (through Opossum);
  metaheuristics Galapagos GA, SGA, simulated annealing (Galapagos), PSO (Silvereye), CRS2 (NLopt), CMA-ES.
- Budget: 500 function evaluations per run, 20 runs per problem (one for DIRECT, which is deterministic).
  Default parameters, except that the GA population was cut to 25; SGA used Wetter and Wright's settings.
- Problems and the time of one evaluation:

  | # | Kind | Variables | One evaluation |
  |---|---|---|---|
  | 1 | Structure | 8 discrete | about 25 ms |
  | 2 | Structure | 22 discrete | about 300 ms |
  | 3 | Energy | 4 continuous | about 4 s |
  | 4 | Energy | 13 continuous | about 8 s |
  | 5 | Energy | 13 discrete | about 8 s |
  | 6 | Daylight | 15 discrete | about 45 s |
  | 7 | Daylight and glare | 40 continuous | about 120 s |

- Results, section 4.8: apart from the first forty evaluations RBFOpt converges fastest, then CRS2, DIRECT,
  PSO, SA, CMA-ES; RBFOpt is the most robust, and SGA, CRS2, CMA-ES and GA the least. Per problem: RBFOpt best
  on 1, 2, 5, 7; DIRECT best on 3 and 6 and the stable choice on 4; DIRECT far too slow at 22 and 40 variables.
- Recommendations, section 6: DIRECT when stability matters and variables are few; RBFOpt as the all-round
  choice for small budgets; SA and PSO for larger budgets; CRS2, GA and SGA not recommended.
- Multi-objective: section 3.7 says designers should use Pareto-based optimisation "judiciously"; a
  multi-objective model-based tool is named as future work.
- Limits the paper states: seven problems only; performance is problem-dependent; default parameters assumed
  sensible; convergence counted in evaluations only, the solver's own overhead ignored.

(Other topics: to be filled.)

## 3. What bears on H6 and H8

To be filled.

## 4. Counter-evidence found

To be filled.

## 5. What a plain-ES5 app should take from this

To be filled.

## 6. Still open (U)

To be filled.

## 7. Search log

| Date | Where | Query or address | What came back | Kept or set aside |
|---|---|---|---|---|
| 2026-11-14 | curl | academic.oup.com, doi.org for 10.1016/j.jcde.2018.09.001 | 403 to scripts (OUP refuses curl) | Read through the fetch tool instead |
| 2026-11-14 | curl | sciencedirect.com article page | 403 | Set aside |
| 2026-11-14 | Unpaywall, Semantic Scholar APIs | DOI 10.1016/j.jcde.2018.09.001 | Gold open access, CC BY-NC-ND, publisher copy only | Kept as proof of open access |
| 2026-11-14 | fetch tool | academic.oup.com/jcde/article/6/3/414/5732355 | Full text, three passes (results; budget, limits, multi-objective; references) | Kept, P |

## 8. References

1. Wortmann, T. (2019). Genetic evolution vs. function approximation: Benchmarking algorithms for
   architectural design optimization. Journal of Computational Design and Engineering 6(3), 414-428.
   https://academic.oup.com/jcde/article/6/3/414/5732355 . Read: sections 2.1 to 2.3, 3.1 to 3.7, 4.1 to 4.8,
   5.1, 6, the footnotes and reference list, through the fetch tool. Read 2026-11-14. Level P.

## Interim findings log (2026-11-15; to be folded into the parts above)

- NSGA-II (Deb, Pratap, Agarwal, Meyarivan 2002), P, PDF read as text (sections III, IV intro, VI.A): fast
  non-dominated sort (domination count and dominated set per solution, fronts peeled off), crowding distance
  (per objective sort, boundary points infinite, interior points add the normalised gap between neighbours),
  crowded comparison (lower rank wins; same rank, larger distance wins), main loop (parents + offspring = 2N,
  sort, fill by fronts, cut the last front by crowding distance, then binary tournament + SBX + polynomial
  mutation). Constraint handling: feasible beats infeasible; two infeasible, the smaller violation wins; two
  feasible, ordinary domination. Their runs: population 100, 250 generations = 25,000 evaluations.
- Rutten, "Evolutionary Principles applied to Problem Solving" (his blog, 2011), P: evolutionary solvers are
  flexible, forgiving, give harvestable intermediate answers and allow a dialogue; but "slow. Dead slow": his
  example is 50 generations of 50 = 2,500 evaluations, two days at a minute each; no guaranteed solution.
- Feist, Barreto, Ferreira, Leitao 2016, "Portable generative design for BIM", P (full text). Correction to the
  brief: it is in CAADRIA 2016 (pp. 147-156), not eCAADe. RosettaBIM = an abstraction layer of parameterised
  operations that create BIM objects (slab, wall, door, stairs ...) + a plug-in per BIM tool (Revit, ArchiCAD).
  A window operation must receive its host wall. Defaults for family/properties keep programs portable. The
  BIM program is shorter than the CAD one because the operations carry the semantics. Booleans are restricted
  in BIM tools, so wall lengths were computed from the slab outline instead. IFC round trip between the two
  tools lost families (stairs, roofs became generic objects).
- Hypar Elements, P (README and Elements.Serialization.IFC/src read as text; commit e13edf59, 2026-11-12, MIT):
  typed elements map to typed IFC entities (Beam -> IfcBeam, Column -> IfcColumn, StandardWall ->
  IfcWallStandardCase, Wall -> IfcWall, Floor -> IfcSlab FLOOR, Space -> IfcSpace, Panel -> IfcPlate, Brace ->
  IfcMember, Opening -> IfcOpeningElement with IfcRelVoidsElement); any other GeometricElement and Mass fall
  back to IfcBuildingElementProxy. The IFC GlobalId is derived from the element's own Id (IfcGuid.ToIfcGuid).
  README: "An Element is a uniquely identifiable piece of a building system"; proxies make a model hard to
  reason about semantically.
- Ma, Wang, Wang, Xiang, Sun 2021, "Generative Design in BIM: Approaches and Requirements", Sensors 21(16) 5439,
  P (first 100,000 characters): 93 Scopus documents 2010-2020, 28 analysed. It is in Sensors, not Automation in
  Construction. It gives no "70% early massing" figure; the nearest number is 20 of 28 studies (71%) whose
  objective is "support design processes", which is not a design stage. The 70% claim stays U.
