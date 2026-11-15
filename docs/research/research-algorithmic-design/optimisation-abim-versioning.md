# Optimisation, algorithmic BIM and IFC, version control of parametric definitions

Research notes, one of five parallel sides of `research-algorithmic-design.md`. Read 2026-11-14 and
2026-11-15. Levels: P = the source itself was read; S = a dependable secondary work, or a value recalled
from the source but not re-read in it; U = seen only in a search summary, or not reached.

How things were read: PDFs were downloaded and read as text (`pdftotext`); GitHub files were read raw; the
publisher pages that refuse scripts (Oxford Academic) were read through a fetch-and-extract tool that returns
the page's text answered against a question. Where that tool was the route the reference says so, and a
second reader should re-check any number the code will use. No upstream code was built or run. The app's own
code was not read for this note (the H8 check against V177 belongs to the main note).

## 1. Summary of findings

| # | Finding | Level | Confidence |
|---|---|---|---|
| F1 | At 500 evaluations on seven simulation-based architectural problems (4 to 40 variables), the two genetic algorithms tested were the worst solvers; the model-based RBFOpt was the most robust and the fastest after about the first 40 evaluations; DIRECT was best early and with few variables (Wortmann 2019). | P | High for what the paper says; medium for generality: seven problems, default parameters, and the author led the winning tool (disclosed) |
| F2 | The same author's 2017 paper used 200 evaluations and gives the rule: metaheuristics where thousands or tens of thousands of evaluations are possible, direct search for few variables, model-based methods for many variables and few evaluations. | P | High |
| F3 | Pareto search costs more than single-objective search: Wortmann 2017 cites 1,400 to 1,800 evaluations for a two-objective energy problem's front to settle, and found a single-objective RBFOpt run on a weighted sum gave better fronts than the Pareto GA HypE at 200 evaluations. | P | Medium: one problem, one author |
| F4 | A wider benchmark (Waibel et al. 2019, 15 energy problems) qualifies F1: no solver dominates; RBFOpt converges very fast but can be trapped locally; a simple GA and PSO are competitive when tuned to the problem's size; CMA-ES is consistently good with a very large budget; many "discrete" building variables are ordinal, so continuous operators work better than combinatorial ones. | P for the abstract only; the body was not reached | Medium |
| F5 | The tool builder himself calls evolutionary solvers "slow. Dead slow": Rutten's example is 50 generations of 50 = 2,500 runs. Their merits are flexibility, tolerance of badly posed problems, usable intermediate answers and a dialogue with the user. | P (his 2011 essay; the 2013 AD article was not reached) | High |
| F6 | NSGA-II is small enough to implement from the paper: fast non-dominated sort, crowding distance, crowded comparison, elitist (parents + offspring) selection, binary tournament, SBX and polynomial mutation, and a parameter-free constraint rule. Its own tests ran 25,000 evaluations (population 100, 250 generations). | P for the algorithm; S for the parameter values (lost in text extraction) | High / medium |
| F7 | Autodesk's Generative Design in Revit ships four methods: Randomize (default 40 outcomes), Space evenly (earlier "Cross Product"), Like this (plus or minus 20% around a chosen outcome) and Optimize (a customised NSGA-II, crossover 0.8, mutation 0.4, population at least three times the inputs, seedable, returns the Pareto set of the whole run). Three of the four are sampling, not optimisation. | P | High |
| F8 | Nelder-Mead can converge to a point that is not a minimum, even on smooth strictly convex functions of two variables (McKinnon 1998); pattern search methods have convergence proofs and Nelder-Mead does not belong to that class. | P (abstract, introduction) | High |
| F9 | A-BIM (Feist; Feist, Barreto, Ferreira, Leitao 2016) differs from generating geometry in that the program calls operations that create building components (slab, wall, door, stairs, roof, levels) with a family or properties defaulted, and that hosted elements take their host as a parameter (a door needs its wall). Booleans are restricted; the tool does the opening itself. | P | High |
| F10 | IFC has typed occurrences (IfcWall, IfcSlab ...), type objects that hold what occurrences share (IfcWallType, linked by IfcRelDefinesByType; an occurrence property overrides the type's), property sets, and IfcBuildingElementProxy for what has no semantic class. buildingSMART advises against the proxy for an arbitrary built element. | P | High |
| F11 | IFC carries no procedural definition of a building. What is parametric is local: profile parameters (IfcParameterizedProfileDef, 2D only) and recorded constraints (IfcConstraintResource: a named requirement with a grade and a benchmark value). A generator's rules cannot travel in IFC; only their result and, as properties, their parameters. | P for what the schema has; the absence is an inference from the parts read | Medium-high |
| F12 | Hypar Elements does exactly the H8 mapping: typed element to typed IFC entity, anything else to IfcBuildingElementProxy, and the IFC GlobalId derived from the element's own id. | P (code read as text) | High |
| F13 | The "70% of generative-design-for-BIM studies focus on early massing" claim was not found. The nearest real review (Ma et al. 2021, Sensors, not Automation in Construction) has no such figure; its closest number is 20 of 28 studies (71%) aimed at "supporting design processes", which is an objective, not a design stage. | U for the claim | High that this review does not contain it |
| F14 | Graph diff exists in practice; automatic graph merge does not. GHShot shows added, deleted and changed components and links but leaves merging to copy-and-paste; VVD applies a diff only if every change applies cleanly and lists three-way merge as future work; Speckle versions are immutable snapshots and its version-diff view is deprecated. | P | High |
| F15 | Model-differencing practice (EMF Compare) matches elements by identifier when they have one and by similarity only as a fallback; conflicts exist only in a three-way comparison; the conflict kinds are: change on one side and delete on the other, the same attribute changed to different values, a new reference to something the other side deleted. Equal changes on both sides are "pseudo" conflicts and need no action. Dynamo's file already gives every node, port and connector a GUID and keeps positions apart from the graph. | P | High |
| F16 | Text programs version well with ordinary tools: the A-BIM group used Git on the generating program, and notes that textual conflict detection suits textual languages. | P (passages on version control) | Medium |
| F17 | CityEngine explains a generated model through its shape tree: the Model Hierarchy window shows the derivation, clicking in the 3D view selects the node, and "Jump to rule" opens the rule that made it. | P | High |

## 2. Findings by topic

### 2.1 Optimisation benchmarks

**Wortmann 2019, "Genetic evolution vs. function approximation" (JCDE 6(3), 414-428), P.**

- Solvers: direct search DIRECT and SBPLEX (NLopt, through Goat); model-based RBFOpt (through Opossum);
  metaheuristics Galapagos GA, SGA, simulated annealing (Galapagos), PSO (Silvereye), CRS2 (NLopt), CMA-ES.
- Budget: 500 evaluations per run, 20 runs per problem (one for DIRECT, which is deterministic). Section 2.3.1
  calls 500 a compromise for practice, the number Wetter and Wright 2004 used; section 1 says thousands of
  simulations are often impractical. Default parameters; GA population cut to 25; SGA with Wetter and
  Wright's settings.
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
  on 1, 2, 5 and 7; DIRECT best on 3 and 6 and the stable choice on 4; DIRECT far too slow at 22 and 40
  variables. On problem 3 five solvers' medians lie within 0.05 kWh/m2a of each other: on easy problems the
  choice hardly matters.
- Recommendations, section 6: DIRECT when stability matters and variables are few; RBFOpt as the all-round
  choice for small budgets; SA and PSO for larger budgets; CRS2, GA and SGA not recommended.
- Limits the paper states: seven problems; performance is problem-dependent; defaults assumed sensible;
  convergence counted in evaluations only, the solver's own overhead ignored.

**Wortmann 2017, "Model-based optimization for architectural design" (TAD 1(2), 176-185), P.**

- 200 evaluations, ten runs per stochastic solver, two daylight problems; GA and HypE population halved.
- Problem 2 (40 variables): DIRECT worst; SA poor; the other metaheuristics including HypE improve the
  objective by about 40%, RBFOpt by 50%; RBFOpt the most stable.
- RBFOpt starts with a Latin hypercube sample whose size equals the number of variables, and gains from its
  surrogate after that (after 15 evaluations on problem 1).
- On Pareto search: useful only when objectives truly trade off; less efficient than single-objective search;
  a cited two-objective energy benchmark needed 1,400 to 1,800 evaluations for the fronts to settle. The
  author's conjecture: architects like Pareto search because it returns a set of alternatives, not because it
  represents the trade-off accurately.
- Conclusion: metaheuristics where thousands or tens of thousands of evaluations are possible; direct search
  for relatively few variables; model-based methods for more variables and limited evaluations. When one
  evaluation takes more than a few seconds the surrogate's own cost is negligible.
- It names Hooke-Jeeves and Nelder-Mead as the well-known local direct search methods and DIRECT as global.

**Waibel, Wortmann, Evins, Carmeliet 2019 (Energy and Buildings 187, 218-240), P for the abstract only.**
Single-objective black-box solvers on a set of building energy problems from the literature (15 according to
a search summary, U), with hyper-parameter studies. Findings as in F4. The body, its budgets and its ranking
tables were not reached (closed access; Academia.edu and Bohrium refuse scripts).

**The defence of genetic algorithms.**

- Rutten 2011 (the Galapagos author's essay, P): flexible; forgiving of under- or over-constrained problems;
  intermediate answers can be harvested at any time; the user can steer. Against: slow (2,500 runs in his
  example, two days at a minute each), and no guarantee of a solution.
- Wallacei (its About page, P): uses NSGA-II with K-means clustering, and its stated purpose is analysis and
  selection of solutions from the whole population, not the single best. The primer PDF (Google Drive) was
  not reached.
- Autodesk (help and primer, P): NSGA-II is the "Optimize" method; rule of thumb population at least three
  times the inputs; the example is 40 generations of 40 (1,600 runs).
- Waibel et al. (abstract, P): tuned simple GA and PSO are competitive.
- Octopus's own documentation was not reached (U).

**NSGA-II (Deb, Pratap, Agarwal, Meyarivan 2002, IEEE TEC 6(2) 182-197), P, enough to implement.**

1. Domination: a dominates b when a is no worse in every objective and better in at least one. With
   constraints (section VI.A): a feasible solution dominates an infeasible one; of two infeasible ones the
   smaller total violation dominates; two feasible ones use ordinary domination. No penalty weight is needed.
2. Fast non-dominated sort (III.A): for each solution p compute n_p (how many dominate it) and S_p (the set
   it dominates), by comparing all pairs. Those with n_p = 0 form front 1. For each p in the current front,
   for each q in S_p, decrement n_q; when n_q reaches 0, q joins the next front. Repeat until no front is
   left. Cost O(M N^2) for M objectives and N solutions.
3. Crowding distance (III.B), within one front: set every distance to 0; for each objective sort the front by
   that objective, give the two boundary solutions infinite distance, and add to each interior solution
   (f[i+1] - f[i-1]) / (f_max - f_min).
4. Crowded comparison: lower rank (front number) wins; equal rank, the larger crowding distance wins.
5. Main loop (III.C): start with a random population P of size N, sorted and ranked; make N offspring Q by
   binary tournament (crowded comparison), crossover and mutation. Each generation: R = P + Q (size 2N);
   sort R into fronts; fill the new P front by front; the first front that does not fit is sorted by
   crowding distance, largest first, and cut to fill exactly N; make the new Q from the new P. The sort may
   stop once N members are found.
6. Operators for real variables: simulated binary crossover (SBX) and polynomial mutation, from the paper's
   reference [6] (Deb and Agrawal 1995), which was not read. The values in the paper (crossover probability,
   mutation probability 1/n for n variables, the two distribution indexes) were printed as symbols that the
   text extraction lost; the commonly reproduced values are 0.9, 1/n, 20 and 20 (S, to be re-read in a
   copy with the mathematics intact before any code uses them). The SBX and polynomial-mutation formulas
   themselves are U here for the same reason: they must be taken from Deb and Agrawal 1995 or Deb's book.
7. Their experiments: population 100, 250 generations, 25,000 evaluations, on nine two-objective test problems.

**Small derivative-free methods.**

- Nelder-Mead: McKinnon 1998 (P) shows convergence to a non-stationary point by repeated inside contraction
  with the best vertex fixed, on strictly convex two-variable functions with up to three continuous
  derivatives. He notes direct search methods are "easy to program" and widely used, and that Torczon's
  convergence results cover pattern search but not Nelder-Mead.
- Hooke-Jeeves pattern search, coordinate search and Latin hypercube sampling: named in Wortmann 2017 (P) as
  the standard local direct search and as RBFOpt's start-up sample. Their primary sources (Hooke and Jeeves
  1961; Kolda, Lewis and Torczon 2003; McKay, Beckman and Conover 1979) were not read: the algorithms
  themselves are U in this note and need a primary reading before code.
- Mixed and discrete variables: Wortmann 2019 ran discrete problems (a section chosen from 30, 13 and 15
  discrete parameters) through the same solvers by treating the choices as ordered steps (P); Waibel et al.
  state that such variables are mostly ordinal and that continuous operators then beat combinatorial ones
  (P, abstract). So storeys and bay counts are integer steps on an ordered axis, rounded, not categories.

### 2.2 Design-space exploration without an optimiser

- Autodesk Generative Design in Revit (help 2024 and the Generative Design Primer, P): Randomize "for
  optioneering", when the user does not yet know what to optimise, default 40 outcomes; Space evenly / Cross
  Product combines each step of every parameter (the whole grid); Like this varies the selected variables
  within plus or minus 20% of a preferred outcome, inside each variable's limits, booleans taking either
  value; Optimize is NSGA-II. A seed makes any run repeatable.
- Design Explorer (Thornton Tomasetti CORE studio, README, P): a web application for exploring a
  multi-dimensional design space, built on a D3 parallel-coordinates component, a scatter matrix, a radar
  chart, range sliders, a star rating and a 3D viewer. Its input format and practice notes were not read.
- Mueller 2014 (MIT thesis, abstract, P): graphical views of the design space are "highly useful for
  designers"; it proposes clustered parallel coordinates for conceptual structural design. Brown and
  Mueller's papers were found (IJAC 17(1) 36-52) but not read: U.
- Wallacei (P, About page): the emphasis is on analysing and selecting from all the solutions of a run.
- Read together: the tools practitioners are given put sampling and a filterable multi-axis view first and
  treat the optimiser as one method among four. That practitioners prefer it is supported only indirectly
  (tool design, Wortmann's conjecture): medium-low confidence as a claim about practice.

### 2.3 Algorithmic BIM and IFC

- Feist, Barreto, Ferreira, Leitao 2016, "Portable generative design for building information modelling",
  P (full text). It is in CAADRIA 2016, pp. 147-156, not eCAADe as the brief had it. RosettaBIM is an
  abstraction layer of parameterised operations that create BIM objects, plus a plug-in per BIM tool (Revit,
  ArchiCAD). The operations take the same parameters for every back-end (a slab takes an absolute height;
  the plug-in converts). A window or door operation must receive its host wall. Family (Revit) or properties
  (ArchiCAD) are optional parameters with defaults so the generic call is portable. The BIM program came out
  shorter than the CAD one because the operations carry the semantics. BIM tools restrict booleans, so wall
  lengths were computed against the slab outline instead of by intersection. An IFC round trip between the
  two tools kept geometry but lost families (stairs, roofs became generic objects).
- Feist 2016, MSc thesis "A-BIM" (Tecnico Lisboa), P (section 6.1.1, the contents): the same points at more
  length. A slab and a wall are the same box in CAD and two different operations in BIM; a subtraction that
  makes no building sense is refused; a door "can only exist hosted in a wall", so creation order matters;
  library components replace modelling from scratch. Chapter 8 models levels, slabs, slab openings, walls,
  roof slab, stairs and doors three ways (algorithmic CAD, A-BIM, manual BIM).
- Khepri (README of Khepri.jl, P): the successor, in Julia; the README says only that the Julia package is
  currently restricted to the AutoCAD back-end. The Khepri papers on BIM back-ends were not read (U).
- Ma, Wang, Wang, Xiang, Sun 2021, "Generative Design in BIM: Approaches and Requirements", Sensors 21(16)
  5439, P (first 100,000 characters): 93 Scopus documents 2010-2020, 28 analysed in detail. Generative
  design "usually occurs at the conceptual design stage"; genetic algorithms are the usual optimiser and
  shape grammars the usual layout explorer; visual languages suit quick and simple work, textual ones complex
  and systematic work; current work is "too preliminary to solve complicated design issues". No 70% figure.
- IFC 4.3 (buildingSMART/IFC4.3.x-development, docs/schemas, P): see F10 and F11. Further: a proxy should
  carry a Name, and ObjectType when USERDEFINED; from IFC 4.3 the proxy should not stand for spatial
  placeholders (IfcVirtualElement does); IfcRoot.GlobalId is the identity "within the entire software world";
  IfcOwnerHistory keeps only the last modification, so IFC is not a history either.
- Hypar Elements (commit e13edf59, 2026-11-12, MIT; README and Elements.Serialization.IFC/src, P): Beam to
  IfcBeam, Column to IfcColumn, StandardWall to IfcWallStandardCase, Wall to IfcWall, Floor to IfcSlab
  (FLOOR), Space to IfcSpace, Panel to IfcPlate, Brace to IfcMember, Opening to IfcOpeningElement joined by
  IfcRelVoidsElement; any other GeometricElement, and Mass, to IfcBuildingElementProxy. GlobalId =
  IfcGuid.ToIfcGuid(element id); relationship ids are new on each export. One storey holds everything. The
  README: an element is "a uniquely identifiable piece of a building system"; an instance refers to a base
  definition plus a transform; a proxy makes a model hard "to reason about semantically".

### 2.4 Version control of parametric definitions

- Cristie and Joyce 2019, GHShot (eCAADe 37 / SIGraDi 23, vol. 3, p. 35 on), P: commit, diff, branch, merge
  as the four functions. Diff colours components and links deleted, added, or changed in their attributes.
  Branches stand for design alternatives. Merge is not automatic: Grasshopper files are XML text, but adding
  one file's components and links to another may leave a model that does not work, so the designer copies
  parts across. Five student designers found recording, overview and fallback useful. It cites Zaman et al.
  2017 (MACE) for highlighting node and edge differences between alternatives; that paper was not read (U).
- VVD (oderby/VVD README, P): diff, visualise and apply for Grasshopper and Dynamo graphs. Applying fails as
  a whole when the two authors changed the same region; three-way merge and a report of the problem areas
  are future work. It says binary formats and "messy XML" make ordinary version control of little use.
- Dynamo (Basics_Basic01.dyn in DynamoDS/Dynamo, P): JSON with top-level Nodes, Connectors, Inputs, Outputs
  and View. Each node has a GUID Id and a ConcreteType; each port its own GUID Id; a connector has an Id and
  names its Start and End port ids; node positions live apart, in View.NodeViews, keyed by node Id. How
  Dynamo itself behaves on a text merge was not found in a primary source (U).
- EMF Compare developer guide (source file in eclipse-emf-compare/emf-compare, P): phases match, diff,
  equivalence, requirements (one difference cannot be merged without another: adding a class needs its
  package added), conflict, merge. Matching: by identifier when there is one, by a distance measure
  otherwise. Difference kinds: add, delete, change, move. Conflicts only in three-way comparison, of the
  kinds in F15; pseudo conflicts need no action, real ones need resolution.
- Speckle (docs, Version Control and Compare versions pages, P): each publish makes a version, an immutable
  snapshot with author, time, source and message, linked to earlier versions. The viewer's version-diff view
  is deprecated in favour of an assistant's summary. No merge is described. How objects are identified
  across versions (content hash against application id) was not read (U).
- Feist, Ferreira, Leitao 2017, "Collaborative A-BIM" (CAADRIA 2017), P (version-control passages): Git on
  the generating program, with branches for alternative algorithms; compatible changes merge automatically,
  incompatible ones are reported; conflict detection is textual, which suits textual languages.

### 2.5 Explainability

- CityEngine (Model Hierarchy help page, P): F17. The rule file's structure and the shape tree match
  (Footprint to Solid to the facades and roof), and a node can be drawn with its scope.
- GHShot (P): colour for what changed between two versions.
- Hypar and IFC (P): the element's type and name are themselves the first explanation; a proxy explains
  nothing.
- Grasshopper's profiler and preview, and constraint reports, were not read (U).

## 3. What bears on H6 and H8

**H6 (for budgets of hundreds of runs, benchmarks do not favour genetic algorithms): supported, with three
qualifications.**

1. Supported directly for single-objective search at 200 and 500 evaluations (Wortmann 2017, 2019: GA and SGA
   worst; the paper's own advice is metaheuristics only where thousands of runs are possible).
2. Qualified by Waibel et al.: with tuning, a simple GA and PSO are competitive, and the model-based winner
   can be trapped locally. "Do as well or better" holds; "always better" does not.
3. The premise depends on the evaluator. Ladybug runs take seconds, so hundreds of runs is the real budget and
   H6 applies. The app's yield figures (floor area, FAR, height, coverage) are arithmetic; if one evaluation
   takes milliseconds, thousands of runs fit in seconds and the argument against a GA loses its force for
   those objectives. The cost of one evaluation, not the browser, sets the method. (The evaluation times are
   to be measured in the main note's experiment.)
4. The benchmarks' winner, RBFOpt, is not "simpler": it is a surrogate method with a mixed-integer
   sub-problem. H6's phrase "simpler direct search or model-based methods" joins two different things. What
   the sources support for little code is: direct search for few variables (about ten or fewer; DIRECT failed
   at 22 and 40), and a sample-first approach.

**H8 (generators that make ordinary elements need nothing new for IFC beyond V177): supported in principle,
with four conditions the sources add.**

1. Generated things must be the app's typed elements; anything a generator makes that has no element class
   becomes IfcBuildingElementProxy, with a Name and ObjectType, and that should be the exception (IFC 4.3
   note; Hypar's mapping and README).
2. The GlobalId must be derived from the element's stable identity, not made new on each export, or every
   regeneration looks like a new building to the receiver (Hypar's IfcGuid.ToIfcGuid(id); IfcRoot). This ties
   H8 to H3: a regenerated element that keeps its rule-path identity keeps its GlobalId.
3. Repeated generated elements should share a type object (IfcWallType and its kin) where V177 already
   writes types; a facade of 80 identical panels as 80 untyped occurrences is legal but poor.
4. IFC will not carry the rules. The generator and its parameters stay in the app's own file; at most the
   parameters and the rule path can go out as a property set. A round trip through IFC returns elements, not
   a generator (A-BIM's own finding: IFC "would not be the ideal solution for porting models generated by
   programs").

## 4. Counter-evidence found

- Against "GAs are a poor choice": Waibel et al. (tuned GA and PSO competitive; no dominator; RBFOpt's local
  traps); Rutten (robust to badly posed problems, harvestable intermediate results, user dialogue: qualities
  no benchmark of final objective value measures); Autodesk and Wallacei ship NSGA-II as the optimiser.
- Against trusting the benchmarks: the 2017 and 2019 papers are by the lead developer of the winning tool
  (disclosed); seven and two problems; defaults, where Waibel et al. show tuning matters.
- Against Pareto search: Wortmann 2017 (a weighted-sum single-objective run found better fronts at 200
  evaluations). Against that: one problem; and a weighted sum needs weights the designer may not have, which
  is why the tools offer a set of alternatives.
- Against Nelder-Mead as the "simple safe choice": McKinnon 1998.
- Against "IFC cannot carry anything parametric": it does carry profile parameters, type and occurrence
  sharing, and recorded constraints; the finding is narrower: no procedure and no regeneration.
- Against "graphs cannot be merged": model differencing with identifiers and three-way conflict detection is
  established (EMF Compare). The gap is in the AEC tools, not in the method. No source was found showing an
  AEC graph tool with a working three-way merge; the search for one (VVD, GHShot, Speckle) found none.
- Against "nodes are harder to version than text": true of the tools read, but Dynamo's JSON with GUIDs per
  node, port and connector is exactly the identity a merge needs; the missing piece is the merge tool.

## 5. What a plain-ES5 app should take from this

1. **First method: sample, then show; no optimiser in the first phase.** Three generators of design points,
   each a few dozen lines: random within ranges with a seed, an even grid ("space evenly"), and "like this"
   (plus or minus 20% around a chosen design, clamped to each variable's limits), with a default of about 40
   designs; then a Pareto filter (the domination test of NSGA-II, step 1 and 2 of section 2.1) and a
   parallel-coordinates or scatter view to pick from. Sources: Autodesk help and primer (the four methods,
   the default 40, the seed), Design Explorer (the view), Wortmann 2017 (a Latin hypercube start-up sample
   sized to the number of variables). Why: it works at any budget, needs no objective weights, is repeatable,
   and is what the tools put first. Latin hypercube sampling can replace plain random once its primary source
   is read.
2. **Second method, single objective, few variables: a pattern search (coordinate or Hooke-Jeeves) on integer
   and stepped variables, not Nelder-Mead.** Sources: Wortmann 2017 and 2019 (direct search for few variables,
   and its failure at 22 and 40), McKinnon 1998 (Nelder-Mead's failure; pattern search has the convergence
   results), Waibel et al. (treat storeys and bay counts as ordinal steps). The algorithm's exact steps need
   their primary source read first.
3. **Third, only for trade-offs and cheap evaluators: NSGA-II**, from section 2.1, with the constraint rule
   (a design that breaks the zoning envelope loses to one that does not, with no penalty weight), population
   at least three times the variables, a seed, and the returned set being the Pareto set of the whole run
   (Autodesk primer). Budget: expect on the order of 1,500 evaluations for two objectives (Wortmann 2017's
   cited figure; Autodesk's 40 by 40 example), so only where one evaluation is milliseconds, or in the
   worker with a progress display and a stop button (Rutten: intermediate answers must be harvestable).
4. **A surrogate method (RBFOpt's kind) is not a first-phase item**: best at small budgets in the benchmarks
   but not little code; revisit if Ladybug-driven optimisation becomes a real use.
5. **Element mapping for IFC**: a generator calls the same element constructors as the hand tools (wall,
   slab, opening hosted in its wall, column, roof, room, level), as A-BIM's operations do; each typed element
   exports as its typed IFC entity with a shared type object where one exists; only what has no class
   exports as IfcBuildingElementProxy with a Name and ObjectType; GlobalId is derived deterministically from
   the element's stable id (which for a generated element is its rule path and index, H3); the generator's
   parameters may go out as a property set, the rules stay in the app's file. Sources: Feist et al. 2016,
   IFC 4.3 documentation, Hypar Elements.
6. **Identity for diff and merge of a graph**: every node carries an id made once at creation and never
   reused or regenerated on copy-free edits; every port is addressed by node id plus a stable port name (or
   its own id, as Dynamo does); every connection is the pair (from port, to port), with or without its own
   id; layout (positions) is stored apart from the graph so that moving a node is not a change to the
   definition. Match by id only; never by position or order. Three-way merge against the common ancestor
   then reports, per node: added, deleted, parameter changed, connection added or removed. Conflicts to
   report and never resolve silently: both sides set one parameter of one node to different values; one side
   deletes a node the other edits or wires to; both sides wire different sources into one single-input port.
   Equal changes on both sides are not conflicts. A merged graph must be re-checked for cycles and dangling
   connections before it is accepted (GHShot's warning that a naive union may not work). Sources: EMF Compare
   developer guide, Dynamo's .dyn format, GHShot, VVD. The app's existing element history with branches and
   merge is the natural home; whether its merge is already three-way by id is a question for the main note.
7. **Explainability**: keep, on every generated element, the rule path that made it, and offer "jump to
   rule" from the element and "select what this rule made" from the rule, as CityEngine's Model Hierarchy
   does; in a comparison of two versions, colour added, deleted and changed (GHShot).

## 6. Still open (U) and why

- Waibel et al. 2019 body: budgets, ranking tables, the tuned settings. Closed access; Academia.edu 403,
  Bohrium serves a bot challenge. Only the abstract was read.
- Wortmann and Nannicini (2016, 2017) and Wortmann, Costa, Nannicini, Schroepfer 2015 on black-box and
  surrogate methods: seen only in the 2019 paper's reference list.
- Rutten 2013, Architectural Design 83(2): not reached (Wiley); his 2011 essay with the same argument was
  read instead.
- Opossum's page (food4rhino answered 200 but was not read), Octopus's documentation, Wallacei's primer PDF
  (Google Drive): not read.
- NSGA-II's numeric settings and the SBX and polynomial mutation formulas: symbols lost in extraction; need a
  copy with the mathematics, or Deb and Agrawal 1995.
- Hooke-Jeeves, coordinate search and Latin hypercube sampling: no primary source read.
- Brown and Mueller's papers; Zaman et al. 2017 (MACE); the Khepri papers; "Hops": not read.
- The "70% early massing" claim: not found in any source read; no Automation in Construction review of that
  description was found.
- Speckle's object identity across versions; Dynamo's behaviour under a text merge; Grasshopper's profiler.
- Whether practitioners in fact prefer exploration to optimisation: no survey was read.
- Hosts that refused scripts: academic.oup.com and doi.org to it (403 to curl; read through the fetch tool),
  sciencedirect.com (403), academia.edu (403), bohrium.com (bot challenge), standards.buildingsmart.org and
  ifc43-docs.standards.buildingsmart.org (403; the same text was read from buildingSMART's GitHub),
  github.com HTML pages and the GitHub API (not enabled; raw files and a shallow clone worked),
  papers.cumincad.org over https (failed; http worked).

## 7. Search log

| Date | Where | Query or address | What came back | Kept or set aside |
|---|---|---|---|---|
| 11-14 | curl | academic.oup.com, doi.org for 10.1016/j.jcde.2018.09.001; sciencedirect.com | 403 | Read OUP through the fetch tool |
| 11-14 | Unpaywall, Semantic Scholar | the same DOI | Gold open access, CC BY-NC-ND | Kept as proof of open access |
| 11-14 | fetch tool | academic.oup.com/jcde/article/6/3/414/5732355 | Full text, three passes | Kept, P |
| 11-15 | curl | sci2s.ugr.es copy of Deb et al. 2002 | PDF, 731 kB | Kept, P; mathematics lost in text |
| 11-15 | curl | raw README of tt-acm/DesignExplorer, hypar-io/Elements, aptmcl/Khepri.jl | Read | Kept, P |
| 11-15 | git | shallow clone hypar-io/Elements under the scratchpad `upstream/` | commit e13edf59, MIT | IFC serialisation read as text |
| 11-15 | curl | guessed fenix.tecnico.ulisboa.pt thesis address | An unrelated thesis | Discarded |
| 11-15 | curl | web.ist.utl.pt copy of Feist et al. 2016 | PDF; it is CAADRIA, not eCAADe | Kept, P |
| 11-15 | fetch tool | Rutten's blog, "Evolutionary Principles applied to Problem Solving" | Read | Kept, P |
| 11-15 | web search | Waibel Wortmann Evins Carmeliet benchmark pdf (twice) | Academia.edu, Bohrium, summaries | Full text not reached; abstract from Semantic Scholar kept |
| 11-15 | web search | "generative design" BIM systematic literature review, early design percentage | Ma et al. 2021 (Sensors); no percentage | Paper read; claim stays U |
| 11-15 | curl | buildingSMART/IFC4.3.x-development docs/schemas (six files) | Read | Kept, P |
| 11-15 | web search, curl | Generative Design in Revit methods; help.autodesk.com cloudhelp 2024 pages | Two pages read | Kept, P |
| 11-15 | curl | generativedesign.org llms.txt, Solvers, Genetic Algorithm Q&A | Read | Kept, P |
| 11-15 | web search, curl | McKinnon 1998 pdf | unicamp.br course copy | Abstract and introduction read, P |
| 11-15 | web search | Grasshopper definition version control diff merge three-way | GHShot, VVD, forum threads, GraphHop | GHShot and VVD read; forums and GraphHop set aside (not primary, or no detail) |
| 11-15 | curl | DynamoDS/Dynamo sample Basics_Basic01.dyn | Read | Kept, P |
| 11-15 | web search, curl | Feist A-BIM thesis | sofia-feist.github.io copy, 105 pages | Section 6.1.1 and contents read, P |
| 11-15 | web search, curl | Wortmann 2017 TAD pdf | Copy on the Ladybug forum | Read, P; an unofficial copy of the published article |
| 11-15 | curl | cumincad caadria2017_132.pdf (http) | Read in part | Kept, P |
| 11-15 | curl | docs.speckle.systems llms.txt, versions, compare-versions | Read | Kept, P |
| 11-15 | curl | wallacei.com/about; /learn | About read; Learn has only titles | About kept, P |
| 11-15 | fetch tool, curl | eclipse.dev EMF Compare overview; then the guide's source on GitHub | Overview empty of detail; source read | Source kept, P |
| 11-15 | fetch tool | dspace.mit.edu/handle/1721.1/90083 | Mueller 2014 abstract | Kept, P (abstract) |
| 11-15 | web search | Brown Mueller design space exploration | IJAC paper located, Scribd copy | Not read: Scribd is not a dependable copy |
| 11-15 | web search, curl | CityEngine Model Hierarchy | doc.arcgis.com latest page | Read, P |

## 8. References

All read on 2026-11-15 unless a date is given.

1. Wortmann, T. (2019). Genetic evolution vs. function approximation: Benchmarking algorithms for
   architectural design optimization. J. Computational Design and Engineering 6(3), 414-428.
   https://academic.oup.com/jcde/article/6/3/414/5732355 . Sections 2.1-2.3, 3.1-3.7, 4.1-4.8, 5.1, 6,
   footnotes, reference list, through the fetch tool. Read 2026-11-14. P.
2. Wortmann, T. (2017). Model-based optimization for architectural design: optimizing daylight and glare in
   Grasshopper. Technology|Architecture + Design 1(2), 176-185. DOI 10.1080/24751448.2017.1354615. Copy at
   https://discourse.ladybug.tools/uploads/default/original/2X/c/c328ae4ed5e801f88b6775a6b5344964f421859e.pdf .
   The method survey, benchmark set-up, results and conclusion, as text. P.
3. Waibel, C., Wortmann, T., Evins, R., Carmeliet, J. (2019). Building energy optimization: An extensive
   benchmark of global search algorithms. Energy and Buildings 187, 218-240. DOI 10.1016/j.enbuild.2019.01.048.
   Abstract only, from the Semantic Scholar API record. P for the abstract; the body U.
4. Deb, K., Pratap, A., Agarwal, S., Meyarivan, T. (2002). A fast and elitist multiobjective genetic
   algorithm: NSGA-II. IEEE Trans. Evolutionary Computation 6(2), 182-197. Copy at
   https://sci2s.ugr.es/sites/default/files/files/Teaching/OtherPostGraduateCourses/Metaheuristicas/Deb_NSGAII.pdf .
   Sections III, IV (set-up), VI.A, as text. P; numeric settings S.
5. Rutten, D. (2011). Evolutionary Principles applied to Problem Solving. Author's blog.
   http://ieatbugsforbreakfast.com/2011/03/04/epatps01/ . Whole essay, through the fetch tool. P.
6. McKinnon, K. I. M. (1998). Convergence of the Nelder-Mead simplex method to a nonstationary point. SIAM J.
   Optimization 9(1), 148-158. Copy at https://www.ime.unicamp.br/~sandra/MT853/handouts/Ref5(McKinnon1998).pdf .
   Abstract and introduction. P.
7. Autodesk. Generative Design in Revit help, 2024: "About Generation Methods"
   https://help.autodesk.com/cloudhelp/2024/ENU/Revit-GDiR/files/GUID-887BCC49-06E9-4C52-AECD-BE92646DF2F5.htm
   and "Generation Settings" .../GUID-710D71BE-3376-4647-822A-DA4D793DCBFA.htm . Whole pages. P.
8. Autodesk and matterlab. Generative Design Primer: "Solvers" and "Genetic Algorithm Q&A".
   https://www.generativedesign.org/02-deeper-dive/02-01_algorithms/02-01-04_solvers.md and
   .../02-deeper-dive/02-06_faq-under-the-hood.md . Whole pages (Q&A items 1 to 8). P.
9. Thornton Tomasetti CORE studio. Design Explorer, README.
   https://raw.githubusercontent.com/tt-acm/DesignExplorer/gh-pages/README.md . Whole file. P.
10. Wallacei. About page. https://www.wallacei.com/about . The platform description. P.
11. Mueller, C. T. (2014). High-dimensional design space visualization for conceptual structural design. S.M.
    thesis, MIT. https://dspace.mit.edu/handle/1721.1/90083 . Abstract, through the fetch tool. P (abstract).
12. Feist, S., Barreto, G., Ferreira, B., Leitao, A. (2016). Portable generative design for building
    information modelling. CAADRIA 2016, 147-156. Copy at
    https://web.ist.utl.pt/antonio.menezes.leitao/ADA/documents/publications_docs/2016_PortableGenerativeDesignForBuildingInformationModelling.pdf .
    Whole paper. P.
13. Feist, S. (2016). A-BIM: Algorithmic-based Building Information Modelling. MSc thesis, Instituto Superior
    Tecnico. https://sofia-feist.github.io/publications/Sofia_Feist_Thesis_ABIM.pdf . Contents and section
    6.1.1. P.
14. Feist, S., Ferreira, B., Leitao, A. (2017). Collaborative algorithmic-based building information
    modelling. CAADRIA 2017. http://papers.cumincad.org/data/works/att/caadria2017_132.pdf . Passages on
    version control (introduction, section on VC, scenarios). P.
15. Ma, W., Wang, X., Wang, J., Xiang, X., Sun, J. (2021). Generative Design in Building Information
    Modelling (BIM): Approaches and Requirements. Sensors 21(16), 5439.
    https://pmc.ncbi.nlm.nih.gov/articles/PMC8399883 . First 100,000 characters, through the fetch tool. P.
16. buildingSMART. IFC 4.3 documentation source, https://github.com/buildingSMART/IFC4.3.x-development ,
    branch master, files under docs/schemas: IfcBuildingElementProxy.md, IfcWallType.md, IfcTypeObject.md,
    IfcRoot.md, IfcParameterizedProfileDef.md, IfcConstraintResource/README.md. Read raw. P.
17. Hypar. Elements. https://github.com/hypar-io/Elements , commit
    e13edf5947b5bc5d58e3d9fa5d0afb423eadf63c (2026-11-12), MIT. README.md; Elements.Serialization.IFC/src/
    IFCElementExtensions.cs and IFCModelExtensions.cs (the type dispatch and the ToIfc functions). P.
18. Leitao, A. et al. Khepri.jl README. https://raw.githubusercontent.com/aptmcl/Khepri.jl/master/README.md .
    Whole file (four lines of substance). P.
19. Cristie, V., Joyce, S. C. (2019). GHShot: a collaborative and distributed visual version control for
    Grasshopper parametric programming. eCAADe 37 / SIGraDi 23, vol. 3.
    https://pdf.blucher.com.br/designproceedings/ecaadesigradi2019/ecaadesigradi2019_397.pdf . The sections
    on differentiating, branching and merging, and the user test summary. P.
20. Derby, O. et al. VVD, README. https://raw.githubusercontent.com/oderby/VVD/master/README.md . Whole file. P.
21. Dynamo. Sample graph doc/distrib/Samples/en-US/Basics/Basics_Basic01.dyn in
    https://github.com/DynamoDS/Dynamo (master). The file's keys, two nodes, connectors, one node view. P.
22. Eclipse EMF Compare. Developer guide, source file plugins/org.eclipse.emf.compare.doc/src/developer/
    developer-guide.mediawiki in https://github.com/eclipse-emf-compare/emf-compare (master). The comparison
    model, difference kinds, conflicts, and default matching. P.
23. Speckle. Documentation: https://docs.speckle.systems/workspaces/versions.md and
    https://docs.speckle.systems/3d-viewer/compare-versions.md . Whole pages. P.
24. Esri. ArcGIS CityEngine help, "Model Hierarchy".
    https://doc.arcgis.com/en/cityengine/latest/help/help-model-hierarchy.htm . Whole page. P.
