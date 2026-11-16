# Program to plan: from a brief to a schematic plan to BIM spaces

Research, 2026-11-15 and 2026-11-16. Levels as in `research-protocol.md`: P primary, S secondary, U a pointer
only. The researchers' notes, with their search logs and references, are in `research-program-to-plan/`; the
experiment is in `experiments/program-to-plan/`. Follows `research-algorithmic-design.md` (V228 to V232).

## 1. Abstract

The owner wrote six brief research pages in Notion (2026-11-15) proposing V233 to V238: the brief and program,
spatial relationships, diagrams, schematic space planning, program-to-BIM, and design evaluation. Claude found
the direction sound and three things unsettled: an overlap with queued phases, the plan generator left
unspecified, and one stale fact. This round answers them.

The answer:

- **One model.** The brief, the program and its relationships extend V179's records (V179 is queued and not yet
  built, so its spec can be amended before Cline starts).
- **The plan generator is the hard part, and it is a trade-off, not an algorithm to find.** Measured on 200
  random 12-space programmes, no simple method gets adjacency, a corridor to every room and sensible room
  shapes at once. The best without a corridor meets 71% of required adjacencies; with a corridor reaching
  every room, about 50%. The published methods that do better need a solver library or take minutes, and none
  is in daily use by architects (Lobos and Donath 2010). So V236 should produce studies with a full
  scorecard, never claim an answer.
- **IFC already has a place for programmed areas.** `Pset_SpaceCommon.NetPlannedArea` and `GrossPlannedArea`
  are defined "for programming" (P). The IFC export being built (V176, V177) can write spaces with everything
  needed; IDS checking would add three small wheels.
- **V238 is V231 plus records.** Evaluation needs criteria, hard gates and a decision record on top of V231's
  search; the UK Green Book advises against single weighted scores.

## 2. The question and the hypotheses

Written before any search: `research-program-to-plan/00-question.md`.

| | Hypothesis | Outcome | Evidence |
|---|---|---|---|
| H1 | V179's records can be extended to carry V233 and V234 without a second model | **Held** | V179's spec and code (P): `bim/interiors.js` has no functions yet; its item `{id, use, count, areaMin, areaMax, rationale}` and relation `{a, b, kind, rel, nearM}` need fields added, not replacing. Usages (V131) already hold grossing ratios (GBA to GFA to NSA), so the area model partly exists too |
| H2 | An adjacency-ordered treemap with swaps places 12 spaces with areas within 10% and 80% of required adjacencies, in under a second | **Partly failed** | e01: areas exact, 2 ms, but a median 71% of required adjacencies met [64, 79]. The layout researcher's clinic: 77% (P, measured) |
| H3 | The corridor is the hard part, and a corridor-first method does better | **First half held, second failed** | e01: a corridor reaching every room cuts adjacency to about 50% and, at the building's depth, makes small rooms slots (worst aspect 8); at room depth with a minimum width, small rooms grow (worst +89%) and gross over net rises to 1.30. Corridor-first wins on reach, not adjacency |
| H4 | Deterministic methods beyond treemaps exist, and their papers state their limits | **Held, one correction** | Slicing (Wong and Liu 1989), rectangular duals (Kozminski and Kinnen; GPLAN), MIQP (Wu 2018), constraint programming (Medjdoub and Yannou 2000), all with stated limits (P, S). Correction: the graph family can now insert corridors (Shekhawat et al. 2025, P), at the cost of shrinking rooms |
| H5 | IfcOpenShell can write IfcSpace with all it needs, and its IDS checker is pure Python | **Held, two corrections** | The vendored 0.8.5 wheel has every call (P); ifctester 0.9.0 is pure Python, LGPL, and runs on Pyodide in IfcOpenShell's own web app (P). Corrections: IDS cannot check computed values such as area totals or adjacency (its own counter-example is an office-area total), so those checks stay the app's code; and ifctester's declared dependencies include flask and a GPL package that its core check does not import (P, PyPI metadata, re-read 2026-11-16) |
| H6 | V238 is data (criteria, gates, a record) over V231, not a new search engine | **Supported** | RIBA's Stage Report, GSA's concept reviews and the Green Book (2026) ask for records and comparison, not a search method (P) |
| H7 | An approved program revision can be a named history commit | **Held, a small addition** | A commit holds id, message, date, author and the tree, and `A3D.site` is one of its parts (`history/element-history.js:9-12, 155-166`, P). Nothing marks a commit as approved: one field to add |

## 3. Method

- Two researchers in parallel: layout methods (`research-program-to-plan/layout-methods.md`), and practice,
  IFC spaces and IDS (`research-program-to-plan/practice-ifc-ids.md`). A first attempt on 2026-11-15 was stopped
  by the usage limit before saving anything; both were rerun on 2026-11-16.
- The owner's seven practice sources (WBDG, RIBA, GSA P100, RAIC, AIA, IfcSpace, IDS) were each read in the
  original: all confirmed, two with corrections (part 4.1).
- One experiment, e01, five layout methods on a hand-written clinic and 200 random programmes (part 6).
- The app's code read by Claude: V179's spec, `bim/interiors.js`, `bim/usages-live-areas.js`,
  `history/element-history.js`, `history/branches-merge.js`, `core/state.js`.
- **No independent second reader.** Claude re-read two facts the code would use at their source: the two
  planned-area properties of `Pset_SpaceCommon` (buildingSMART's `reference_schemas/psd/Pset_SpaceCommon.xml`,
  confirmed) and ifctester's dependency list (PyPI, confirmed). The rest of the numbers here inform decisions;
  before any work order uses one, it is re-read.
- Nothing was installed or run except the experiment.

## 4. Findings

### 4.1 The owner's pages, checked

All seven sources confirmed in the original (P). Corrections:

- RIBA 2020 calls Stage 1 "Preparation and Briefing"; options are appraised at Stage 2, not before.
- GSA P100 2024, section 1.8.2: area "must be confirmed at each phase of design", with an 80% usable-to-gross
  target; three or more distinct concept schemes.
- RAIC 6.2's comparison criteria also include wall-to-floor ratio and cost.
- IfcSpace: a space joins its storey by aggregation; the predefined types are not room functions (and
  INTERNAL/EXTERNAL are deprecated). The pages missed that the common property set already carries planned
  net and gross areas for programming.
- IDS has six facets; `partOf` can say "on a storey" but not which one; it excludes geometry and computed values.
- V237's page said the platform does not yet write IFC: out of date (V176 and V177).

### 4.2 Layout methods (layout-methods.md, e01)

| Family | Areas | Adjacency | Corridor | Size and time reported | Needs | Few hundred lines of ES5 |
|---|---|---|---|---|---|---|
| Treemap / slicing, ordered, with swaps | Exact | Not guaranteed (71% median here) | No | 12 spaces, 2 ms (e01) | Nothing | Yes |
| Spine with two room bands | Close; small rooms grow | Not guaranteed (about 50%) | Yes, reaches every room | 12 spaces, 2 ms (e01) | Nothing | Yes |
| Rectangular dual (GPLAN) | Not an input; plot size is an output | Every requested, plus unrequested ones | Added in 2025 by shrinking rooms | Seconds | Planar triangulated graph; code licence unknown | Hard |
| Slicing with annealing (Wong and Liu) | Exact | Pulls together, not guaranteed | No | 15 to 40 modules, 1 to 13 CPU minutes | Nothing | Yes, but slow |
| MIQP (Wu 2018) | Within bounds | As constraints | Yes | 9 to 13 s a house; 75 s for 125 rooms | A solver library | No |
| Constraint programming (Medjdoub and Yannou) | Within bounds | As constraints | Some | Enumerates all for 10 rooms | A CP package | No |

Practice figures (P): school circulation at least 20 to 25% of net area, corridors 1.8 m (BB103); offices 28 to
38% of usable area (GSA 2012); health factors 1.20 to 1.60 (DoD 2018). The one product documented in detail,
Anthropocity, routes corridors along walls from ordered user paths on a bay grid, reports area deviation,
corridor share and unreached rooms, and calls itself a planning aid (S, its own documents).

### 4.3 Areas, IFC spaces and IDS (practice-ifc-ids.md)

- Area standards split area the same way at heart but place circulation differently; a ratio means nothing
  without its standard named. IPMS 2023 and FICM 2006 are free; DIN 277:2021 and BOMA 2017 are sold; ISO
  9836:2017 is withdrawn (P and S).
- The vendored IfcOpenShell 0.8.5 has every call to write a space on its storey, with names, property and
  quantity sets, a zone, and a kept GlobalId; V177 already keeps GlobalIds (P).
- IDS in the worker: ifctester 0.9.0, xmlschema and elementpath, about 0.8 MB with the two dependencies (MIT
  for those two; ifctester LGPL). Its other declared dependencies (flask, a GPL package) are not imported by the
  core check; shipping would vendor only what the check imports (P).

### 4.4 Practice: records, relations, decisions

- Programming tools keep requirements and model rooms as separate records joined by a readable programme
  number, and keep history as a change log (S, vendors' documents).
- There is no standard adjacency scale (Muther's A to X letters, the VA's 1 to 3, graded wording); the kinds of
  relation recur (proximity, direct access, visual, acoustic separation, security, sequence), each rating with
  a reason (P and S).
- Options appraisal asks for a record: alternatives, criteria, what was decided and why. The Green Book (2026)
  advises against simple weighting and scoring (P).

## 5. The alternatives compared

**The data model**

| Option | Duplicates V179 | Work | Risk |
|---|---|---|---|
| A. Extend V179's records before Cline builds them (recommended) | No | Rewrite V179's spec and tests now | Delays V179 by a session |
| B. Separate V233/V234 models, migrate V179 later | Yes | Two models, then a migration | Two sources of truth for a while |
| C. Build V179 as is, extend after | Briefly | V179's functions changed after shipping | Cline's work partly redone |

**The plan generator**

| Option | Adjacency | Corridor | Shapes | Verdict |
|---|---|---|---|---|
| Treemap ordered by adjacency, with swaps | Best of the simple ones | None | Good | As the "no corridor" typology (open plans, clusters) |
| Spine with two bands, the user choosing the typology | About 50% | Every room | Good with a minimum width; small rooms grow | Recommended first, with small rooms sharing a bay (to measure) |
| Graph duals, MIQP, CP | Better | Some | Varies | Not now: solver, licence unknown, or slow |

## 6. The experiment

e01 (`experiments/program-to-plan/e01-layout.js`, `e01-results.txt`; Node 22.23.4). A rectangular plan 18 m
deep, gross over net 1.15, corridor 1.8 m; adjacency means a shared wall of at least 1.0 m. 200 random 12-space
programmes (6 to 60 m2, 14 required pairs, 3 forbidden); median [quartiles]:

| Method | Required met | Forbidden broken | Worst aspect | Worst area deviation | Rooms on the corridor |
|---|---|---|---|---|---|
| A. Treemap, programme order | 36% [29, 43] | 1 [0, 1] | 3.1 | 0% | none |
| B. Treemap, adjacency order and swaps | 71% [64, 79] | 0 | 2.7 | 0% | none |
| C. Corridor first, sides fill the depth | 50% [43, 57] | 0 | 8.1 | 8% | 92% |
| D. Corridor first, a 5 m side | 43% [43, 50] | 0 | 7.1 | 5% | 100% |
| E. Double-loaded at 5.5 m, length free, 2.4 m minimum width | 50% [50, 57] | 0 | 2.3 | 89% | 100% |

E's gross over net is 1.30 [1.26, 1.35]. All five run in 2.2 ms per programme together. One threat: the random
programmes have random adjacencies; a real programme's adjacencies cluster (as the clinic: B 83%, C and E 67%).

## 7. Edges

- A small room at room depth becomes a slot; at a minimum width it grows past its area. Practice groups small
  rooms (toilets, stores) into a block; whether "small rooms share a bay" fixes this is unmeasured.
- A waiting room or lobby open to the corridor counts as circulation: the layout researcher's clinic went from
  38% to 69% adjacency when it did.
- An adjacency graph that is not planar and triangulated cannot be drawn as touching rectangles at all (GPLAN's
  condition): some programmes are impossible as stated, and the report must say so.
- A forbidden pair can always be kept apart by these methods; a required pair cannot always be met.

## 8. What the app already has

- V179 (queued, not built): programme items, relations with three kinds and three rels, matching against drawn
  rooms, a bubble diagram (`docs/work-orders/v179/SPEC.md`; `bim/interiors.js` header only).
- V181 (queued): routes on walkable geometry, which V235's flow paths would reuse.
- Usages (V131, `bim/usages-live-areas.js:11-32`): grossing ratios GBA to GFA to NSA per use.
- History: commits by element, `A3D.site` versioned (`history/element-history.js:9-12, 155-166`).
- IFC export with kept GlobalIds (V177); IfcOpenShell 0.8.5 in the worker (V176).
- V228's keys and overrides, V231's sampling and Pareto filter (queued).

## 9. Risks

- e01 is a rectangle, one level, 12 spaces, random adjacencies. Irregular boundaries and several levels are
  much harder (every source agrees).
- About 50% adjacency with a corridor will disappoint if the tool is presented as a planner. It must be
  presented as studies with a scorecard.
- Vendor claims (Anthropocity, the programming tools) are S.
- No independent second reader this round.

## 10. Still open (U)

- GPLAN's and the corridor paper's code and licences; the main Wu 2018 paper; Liggett 2000; Hypar's and
  Autodesk Forma's current documents.
- DIN 277 and BOMA 2017 texts (sold); UK Health Building Notes, FGI Guidelines; Muther's full reason codes.
- Whether small rooms sharing a bay fixes the slot problem (an experiment).
- Running the space-writing chain and ifctester in the worker (needs the owner's approval).

## 11. The owner's decisions

Asked together, 2026-11-16. Each has the recommendation.

1. **One model.** Extend V179's programme and relation records now (rewrite its spec and tests before Cline
   builds it), so V233 and V234 are V179's records grown, not new ones. Recommended: yes.
2. **What a programme item and a relation carry.** Item: the brief fields (department, level preference,
   criteria, source, status: unknown, assumed or confirmed). Relation: kinds of proximity, direct access,
   visual, acoustic separation, security, sequence; hard or soft; a reason; status suggested, approved,
   rejected. Recommended: yes, with no fixed numeric scale.
3. **Areas.** The project names its measurement standard (IPMS 2023 as the free default) and its grossing
   factor is project data, linked to the usages' ratios; never a universal default. Recommended: yes.
4. **The plan generator (V236).** Studies, not answers: the user picks the typology (spine with two bands, or no
   corridor), the layout is deterministic with swaps, and every study carries its scorecard (adjacency met,
   area deviation, corridor share, unreached rooms, forbidden pairs). One level, a rectangle or simple polygon,
   first. Solver-based methods not now. Recommended: yes.
5. **The identity chain.** Programme item id, then the schematic space's V228 key, then the room element with
   its readable programme number, then the IFC GlobalId from the element id. Recommended: yes.
6. **IDS.** Add ifctester, xmlschema and elementpath to the worker (about 0.8 MB, LGPL and MIT), for per-space
   information checks only; totals and adjacency stay the app's code. This is a new library under the rule, so
   it needs your approval of the library itself. Recommended: yes, when V237 is built.
7. **V238.** Fold it into V231 as criteria, hard gates and a decision record; no single weighted score.
   Recommended: yes.
8. **Approvals.** An approved programme or study is a history commit with an approval field (by, date, note).
   Recommended: yes.
9. **"AI suggested".** Means a rule set or relations pasted in as text (decision 13 of the algorithmic design
   research), marked suggested until approved. Recommended: yes.
10. **Numbers and order.** V179 amended now (it carries V233 and V234); V235 diagrams after V179 and V181; V236
    after V228; V237 after V177; V238 merged into V231. Recommended: yes.

## 12. References

The researchers' notes carry the full lists. The sources the recommendation rests on (read 2026-11-15 or 16):

- WBDG, Architectural Programming. https://legacy.wbdg.org/design-disciplines/architectural-programming (P)
- RIBA Plan of Work 2020 overview. https://www.riba.org/media/syneeeto/2020ribaplanofworkoverviewpdf.pdf (P)
- GSA P100 2024, section 1.8.2 and the concept appendix. https://www.gsa.gov/system/files/P100+2024+Final+(1).pdf (P)
- RAIC Canadian Handbook of Practice 6.2. https://chop.raic.ca/chapter-6.2 (P)
- buildingSMART, Pset_SpaceCommon.
  https://raw.githubusercontent.com/buildingSMART/IFC4.3.x-development/master/reference_schemas/psd/Pset_SpaceCommon.xml (P)
- buildingSMART IDS 1.0, specifications and limitations. https://github.com/buildingSMART/IDS (P)
- ifctester on PyPI. https://pypi.org/pypi/ifctester/json (P)
- Wong and Liu 1989, slicing floorplans; Shekhawat et al. 2025, corridors in rectangular floorplans (AI EDAM);
  Lobos and Donath 2010; Wu et al. 2018 (supplement); Medjdoub and Yannou 2000: see `layout-methods.md` (P, S)
- HM Treasury, The Green Book (2026), options appraisal: see `practice-ifc-ids.md` (P)
- Anthropocity documentation. https://anthropocity.com/docs/ (S)
- The owner's pages in Notion: V233 to V238 research, 2026-11-15 (the starting point; U until read here)
