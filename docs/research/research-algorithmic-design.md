# Algorithmic design: how the app should generate and rebuild buildings from rules

Research, 2026-11-14 and 2026-11-15. Levels as in `research-protocol.md`: P primary, S secondary, U a pointer
only. The researchers' notes, with their search logs and full references, are in
`research-algorithmic-design/`; the experiments are in `experiments/algorithmic-design/`. The owner's decisions are in part 11 (answered 2026-11-15).

## 1. Abstract

The owner asked how the app can accommodate algorithmic design (form, layout and elements produced and rebuilt
from rules and parameters) and pasted a search engine's overview of the field. The question is what to build,
with which algorithms, inside the app's contract (an ES5 engine, one file that runs offline from `file://`,
vetted libraries loaded on demand, phone to desktop), on top of what is already queued (V204 feature records,
V213 generators, V215 flows).

The answer: the hard part is not the graph and not the geometry kernel. It is **identity**: today every
element a generator makes gets a new id on each run, so anything attached by hand is lost. Every professional
tool read solves this the same way: an element is keyed by how it was made, updated in place on a re-run, and
hand edits are stored beside the generator and re-attached, with the ones that no longer fit shown to the
user. Once that exists, a split grammar for facades is small (50 lines of core here, 1,632 parts in half a
millisecond), whole-graph re-evaluation is fast enough at any realistic size, and searching a design space
with a few hundred runs is better served by sampling and pattern search than by a genetic algorithm. The
pasted stack advice (SharedArrayBuffer, OPFS, service worker, React, Tauri, CRDTs) does not fit the one-file
build; a Blob-made worker with transferable buffers does, as the Ladybug runtime already shows.

**Recommendation:** five phases after V204, V213 and V215, in this order: (1) generated elements with a
stable key, in-place re-run and stored overrides; (2) a split grammar for facades, its rules kept as data;
(3) a model-wide graph that joins parameters, generators and analyses; (4) design-space exploration by
sampling, a Pareto filter and pattern search; (5) the node editor, written in ES5. Manifold (mesh booleans)
is the one library worth an approved embedding experiment, and it is not needed for phases 1 and 2.

## 2. The question and the hypotheses

Written before any search, kept unchanged in `research-algorithmic-design/00-question.md`. Outcomes:

| | Hypothesis | Outcome | On what evidence |
|---|---|---|---|
| H1 | Re-evaluating 1,000 arithmetic nodes takes under a frame; geometry is the cost, and caching by input is what matters | **Held**, amended | e01: 1,000 nodes 0.03 ms, 100,000 nodes 31 ms (P, measured). None of the tools read uses fine-grained incremental evaluation as its base (P). Amendment: cache by an input version stamp, not by comparing values. Open: the cost of the app's opening cutter in the browser |
| H2 | A CGA-style split grammar fits in under 400 lines of ES5 with no kernel and derives a 10-storey, 8-bay facade in under 50 ms | **Held**, restated | e02: core 50 lines; 1,632 leaves in 0.46 ms; 48,240 in 36 ms (P, measured). Restated: only while a shape is its box scope, rules are data, and plane cuts, occlusion, snapping and roofs are left out (the open implementations spend most of their code there, P) |
| H3 | A generated element can carry a deterministic identity that survives a change which keeps the counts; when counts change that must be reported | **Held**, amended | e03 (P, measured); Lipp, Wonka, Wimmer 2008 (P); Dynamo's element binding (P); Lipp et al. 2019 (P). Amendment: an index path keeps every id when 8 bays become 10, but 220 of 320 ids then name a window over half a bay away. Keys must be semantic (storey 3, bay 2), which still fail some changes (Lipp 2019: 0 to 100% of edits kept), and an override that no longer has a place is parked and listed, never moved by position |
| H4 | The app's CSG is enough for the first slices; Manifold only for booleans between arbitrary solids; OpenCascade only for fillets, lofts, NURBS solids | **Supported**, not measured | Libraries' documents, licences and package contents read as text (P). No upstream code was run. The app's CSG is the same BSP method as csg.js and JSCAD, fragile on its own output (P, the code) |
| H5 | Studies find node graphs easier to start with and text better for large models | **Partly held**, weak evidence | Leitao, Santos, Lopes 2012 has six subjects and is by the text tool's authors; Celani and Vaz 2012 is a course report (P for what they say, low confidence in the claim). No controlled study found, and none finding the opposite |
| H6 | With a few hundred runs, benchmarks do not favour genetic algorithms | **Supported**, qualified | Wortmann 2019: at 500 evaluations on 7 problems both genetic algorithms were worst (P). e04 agrees on a problem of this app's kind (P, measured). Qualified: Waibel et al. 2019 find no solver dominates (abstract only, S); and the premise depends on the cost of one run: yield arithmetic allows thousands |
| H7 | SharedArrayBuffer, OPFS and a service worker do not work from `file://`; a Blob worker with transferables does | **Held** in Chromium | e05 (P, measured in Chromium 153); MDN agrees (P). Firefox and Safari not available here (U) |
| H8 | If generators create ordinary elements, IFC needs nothing beyond V177 | **Supported in principle**, four conditions | Typed elements export as typed entities; the IFC GlobalId must derive from the stable element id (which is H3 again); repeated elements should share type objects; IFC carries no rules, so the generator stays in the app's file (P for IFC and Hypar; V177's code was not read against this) |

## 3. Method

- **Five parallel researchers,** one for each side (protocol, step 10): execution models and identity; rule
  systems and plan layout; kernels, libraries and the browser; optimisation, algorithmic BIM and versioning;
  the app's own code. Each kept a search log and a reference list in its note.
- **Sources read:** about 75 distinct documents: papers (Mueller et al. 2006, Wonka et al. 2003, Lipp et al.
  2008 and 2019, Wortmann 2017 and 2019, Deb et al. 2002, Bruls et al. 2000, Mokhov et al., Weber et al. 2022,
  Leitao et al.), the tools' own documentation (Esri's CGA reference, Grasshopper's API, Dynamo's primer,
  Rhino.Inside.Revit, Autodesk Generative Design, Speckle, MDN), code read as text (Khepri, DynamoRevit,
  shapeml, cgajs, Hypar Elements, Jane Street Incremental, Salsa, the manifold-3d package) and the app's code.
- **Experiments:** six scripts, e01 to e06, in `experiments/algorithmic-design/` with their raw results (part 6).
- **Not run:** no upstream library was built, installed or executed (reuse-first policy: that needs the owner's
  approval). The npm tarballs were listed and read only.
- **Interruptions:** the researchers were stopped three times by the account's usage limit and resumed from
  their saved state. The app-code researcher could not write files; its note is its condensed hand-back.
- **The independent check:** see part 3a.

### 3a. The independent check

A separate agent re-read the source behind each of 14 facts the code or the recommendation uses
(`research-algorithmic-design/independent-check.md`, 2026-11-15). Result: 8 confirmed as stated, 5 confirmed
with a correction, 1 could not be read. This note carries the corrections:

| Fact | Verdict |
|---|---|
| Mueller 2006: the relative-size formula and `ceil` for a repeat | **Could not be read** (the PDF is refused to scripts and too large for the fetch tool; four other copies refused). Back to U. Nothing in the recommendation depends on it: the repeat's rounding is our own choice (decision 4) |
| Esri's CGA split reference | Confirmed, including that no rounding rule is printed |
| Lipp, Wonka, Wimmer 2008: locators, edits stored outside, invalid ones not applied | Confirmed |
| Lipp et al. 2019: the measured numbers | Confirmed with a correction: the paper was read in full (P). Over five transfers, exact locators kept 0, 0, 0, 100, 100% of edits; the 2008 semantic locators 0, 100, 28.6, 100, 75%; the 2019 paper's own meta-locators 100, 100, 100, 100, 93.8%. An earlier draft credited the last range to plain semantic keys |
| Manifold: licence, version, size, no threads, wasm as bytes, module glue | Confirmed. Caution: the bytes option works through the loader but is not in the package's type file |
| Clipper2 is BSL-1.0; `straight-skeleton` wraps CGAL's GPL package | Confirmed |
| Build Systems a la Carte | Confirmed with a correction: dirty bits alone give minimal rebuilding, not early cutoff; the cutoff comes from verifying traces (stamps) |
| Wortmann 2019 | Confirmed |
| Autodesk Generative Design | Confirmed with a correction: Autodesk's page names the four methods and no algorithm; NSGA-II is named by the Generative Design Primer, whose publisher is not stated (S) |
| Dynamo's element binding | Confirmed |
| McKinnon 1998 | Confirmed (abstract and introduction) |
| Squarified treemaps | Confirmed with a correction: "deterministic" is our reading of pseudocode with no random step; the paper says input order matters and optimality is not guaranteed |
| The app's code (seven facts) | Confirmed, with two corrections: the undo snapshot is a fixed list of twenty fields, not the whole state, so a new top-level field must be added to both the snapshot and the restore; and provenance fields do exist outside `bim/` and `core/` (`dg` on analysis drawings, `linkSourceId`, `bim.sourceId`, `bim.hostId`, `bim.hostWallId`). A visitor that throws during propagation is skipped and the result is still `ok:true` |
| MDN: SharedArrayBuffer needs cross-origin isolation; a service worker needs http or https | Confirmed; MDN does not name `file://`, it says any other scheme is refused |

## 4. Findings, by topic

### 4.1 How the tools evaluate (execution-and-identity.md)

- Grasshopper expires an object and everything downstream of it, then solves that part again (its API page, P).
  Khepri, Rosetta and Luna Moth delete everything and run the program again (Khepri's code and the group's
  papers, P). Confidence high.
- The simplest correct algorithm for a fixed graph: mark everything downstream of the change dirty; recompute
  the dirty nodes once each in the stored topological order; skip a node whose inputs' version stamps did not
  change (Build Systems a la Carte; Jane Street Incremental; Salsa; the TC39 signals proposal; all P). The
  skip is the stamps' doing: dirty marks alone give minimal recomputation but no early cutoff. The
  order cures the diamond glitch; a cycle is refused when the edge is made; dependencies that change during a
  run are left out at first. A signals library is not needed. Confidence high.
- e01 shows this bookkeeping is not what decides responsiveness below about 10,000 nodes (P, measured).

### 4.2 Identity of generated elements (execution-and-identity.md, grammars-and-layout.md)

- Dynamo keys an element by the node call that made it and stores the host ids in the `.dyn` file; on a re-run
  the node changes the bound element, or deletes and remakes it (DynamoRevit's code, P). Rhino.Inside.Revit
  lets each component output choose Update or Replace (its guide, P). Confidence high.
- Lipp, Wonka, Wimmer 2008: an exact locator (the path of shapes and child indexes through the derivation) and
  a semantic locator (floor 2, column 3); edits are stored outside the derivation and re-applied each time; a
  stored key is valid, structurally invalid (its index is beyond the new count: kept, dormant) or semantically
  invalid (listed for the user) (P). Confidence high.
- Lipp et al. 2019 measured it (Table 2, five transfers of 7 to 48 edits): exact locators kept 0, 0, 0, 100,
  100% of the edits; the 2008 semantic locators 0, 100, 28.6, 100, 75%; the paper's own meta-locators 100, 100,
  100, 100, 93.8% (P). So a semantic key is much better than an index path and still not safe: the parked
  list is not optional. Meta-locators are more machinery than a first phase needs. Confidence high.
- FreeCAD 1.0 names sub-shapes by their history and its own documents call the matching heuristic (P): there
  is no general solution, only a scheme with stated failure cases.
- The app has the pattern once already: `bimDgPlace` (`site-analysis/model-layers.js:59-104`) keeps a stable
  key and edited, orphan and gone states for generated drawing objects (P, the code).

### 4.3 Split grammars (grammars-and-layout.md)

- A split grammar is a deliberately restricted grammar: whole labelled boxes are replaced by name, with no
  search for sub-shapes and no emergence (Wonka 2003; Mueller 2006; P). Every practical building generator read
  gives up general shape grammars on purpose. Confidence high for the split grammars; the early shape-grammar
  papers (Stiny and others) could not be reached and are S or U here.
- A shape is a symbol, a scope (origin, three axes, three sizes) and attributes; the derivation tree is kept.
- The 2006 arithmetic as the researcher recorded it: a relative size r becomes
  `r * (scope - sum of absolutes) / sum of r`; a repeat makes `ceil(scope / size)` pieces resized to fill. The
  second reader could not reach the paper, so this is U and the code does not use it.
- Esri's current CGA: no prefix is absolute, `'` is a fraction of the scope, `~` floats (the 2006 "relative"),
  `*` repeats; each child knows `split.index` and `split.total`. Esri does not print its rounding rule for the
  repeat; three sources use three rules (ceil; nearest, at least one; fill then shrink). It is a design choice
  (P). Esri's page has eight worked examples usable as test vectors.
- Limits said by the sources themselves: splits suit facades more than massing (Mueller 2006); no coordination
  across branches, no booleans, little context (Schwarz and Mueller 2015) (P).
- Licences: shapeml is GPL-3.0 (ideas only); cgajs is Apache-2.0.

### 4.4 Plan layout (grammars-and-layout.md)

- Weber, Mueller, Reinhart 2022 review 49 methods in three families (P).
- The squarified treemap (Bruls et al. 2000) has no random step, is about 30 lines, needs no solver, but its
  result depends on the input order, and it makes
  rectangles only and guarantees neither adjacency nor circulation (P; Marson and Musse 2010 is S).
- Merrell et al. 2010 takes seconds to minutes and fails in a share of runs; graph methods guarantee adjacency
  only for some graphs; learned methods need a trained network (P for Merrell; others S). Confidence medium.
- A treemap is an area-fit sketch inside the envelope, not a plan generator. That is this note's inference.

### 4.5 Geometry and libraries (kernels-libraries-browser.md)

- **Manifold:** Apache-2.0; `manifold-3d` 3.5.5; wasm 542,744 bytes (about 205 KB gzipped) and 82 KB of glue;
  single-threaded, no SharedArrayBuffer; its loader accepts the wasm as bytes. Two catches: the glue is an ES
  module, not a classic script; and its guarantee is topological, for input that is already manifold (P).
- **OpenCascade:** the replicad build is 22.9 MB, LGPL-2.1; opencascade.js itself has had no release for years
  (P). The repository's earlier ranking (SMLib ahead of OCCT, `research-usd-brep.md`) stands.
- **Pure JavaScript:** csg.js and JSCAD use the BSP method the app already has; three-bvh-csg says its results
  can be non-manifold (P).
- **2D:** Clipper2 is under the Boost Software License 1.0: permissive, but not on the app's list. The npm
  package `straight-skeleton` says MIT but carries CGAL's GPL code: not usable. No permissive, robust
  straight-skeleton library was found (P).
- **Node editors:** none is both free of a framework and good on touch. litegraph.js (MIT, 176 KB, its own
  engine) has touch marked to do and its last release is from early 2024; Drawflow (46 KB) has touch and pinch
  but no engine; Rete, Baklava, xyflow and Flume need a framework (P; issue pages read as digests).

### 4.6 The browser (kernels-libraries-browser.md, e05)

From `file://` in Chromium 153: `SharedArrayBuffer` is undefined, the origin private file system and the
service worker are refused, a worker from a file beside the page is refused; a worker made from a Blob,
transferable buffers, WebAssembly from bytes and IndexedDB work. Over http without headers (as Pages serves)
SharedArrayBuffer is still undefined (P, measured). `file://` is a secure context; the refusals come from the
missing cross-origin isolation and the opaque origin.

### 4.7 Optimisation and exploration (optimisation-abim-versioning.md)

- Wortmann 2019: 500 evaluations, 7 problems of 4 to 40 variables; both genetic algorithms worst; RBFOpt most
  robust; DIRECT best early and for few variables. Wortmann 2017: metaheuristics only where thousands of runs
  are possible; a Pareto front needs well over a thousand runs to settle (P). The papers are by the lead
  developer of the winning tool, which they disclose.
- Against it: Waibel et al. 2019 (no solver dominates; tuned GA and PSO competitive; S, abstract only); Rutten
  (a GA is slow but forgiving and can be harvested mid-run; P for his essay).
- Practice: Autodesk's Generative Design has four methods (Optimize, Randomize, Space evenly, Like this),
  three of them sampling (P). That Optimize is NSGA-II comes from the Generative Design Primer (S).
- Nelder-Mead can converge to a point that is not a minimum (McKinnon 1998, S here); storeys and bay counts
  are ordinal, so they are stepped axes, which a pattern search handles naturally.
- NSGA-II's parts are recorded from Deb et al. 2002, but its numeric settings were lost in text extraction and
  are S: re-read before any coding.

### 4.8 Algorithmic BIM, IFC, versioning (optimisation-abim-versioning.md)

- In A-BIM the program calls element operations (slab, wall, door with its host wall), not geometry (Feist et
  al., CAADRIA 2016; Khepri's code; P and S). This is what the app's own makers already are.
- IFC carries types, instances and property sets but no generating rules (P).
- No AEC tool read merges graphs automatically; they show differences. A merge needs a permanent id per node,
  ports addressed by node id and port name, and the layout stored apart from the logic (P). The app's history
  already merges three-way per element and per field (`history/branches-merge.js:75-107`).
- The pasted claim that 70% of tools stop at early massing was not found in any source: it stays U and is used
  nowhere.

## 5. The alternatives compared

Criteria, set before comparing: fits the contract (ES5, one file, `file://`); builds on V204, V213 and V215;
keeps hand work across re-runs; works on a phone; cost to build; what it risks.

**Where the rules live**

| Option | Fits the contract | Builds on the queue | Keeps hand work | Phone | Cost | Risk |
|---|---|---|---|---|---|---|
| A. Generators as records with typed parameters and rules as data; a model graph joins them later | Yes | V204 expressions, V213 generators, V215 ordering | Yes, by key and stored overrides | A form: yes | Low to medium | Less expressive than a program |
| B. A full node graph first (Grasshopper-like), every operation a node | Yes, with our own editor | V215 only | Only if every node keys its output | Poor: no touch-ready library | High | The editor consumes the phases before anything is generated |
| C. A text language (as Khepri, Luna Moth) | Needs an interpreter: no `eval` in the engine | Little | Whole model re-made each run in the tools read | Poor | High | A language to design, document and keep safe |

**Recommendation: A, with the graph (phase 3) and the editor (phase 5) after the generators work.** It would
change if the owner wants free-form visual programming before any generator: then B, starting with the editor.

**Geometry**

| Option | Licence | Size | Adds | From `file://` | Verdict |
|---|---|---|---|---|---|
| The app's own meshes and BSP CSG | ours | 0 | boxes, prisms, walls, openings | Yes | Enough for phases 1 and 2 |
| Manifold | Apache-2.0 | about 0.6 MB | robust booleans, 2D offsets | Likely, by embedding the wasm; the module glue needs an experiment | Approve an experiment when booleans between generated solids are needed |
| OpenCascade (replicad build) | LGPL-2.1 | 22.9 MB | fillets, lofts, STEP | Not tested | Not for this work |

**Search**

| Method | Code | At 200 runs (e04) | Published evidence | Verdict |
|---|---|---|---|---|
| Sampling, Pareto filter, parallel coordinates | Small | 23 to 32% of best as a search, but shows the whole space | What practice uses most (Autodesk) | First |
| Pattern search on stepped variables | Small | 72% | Direct search does well at small budgets (Wortmann) | Second |
| Genetic algorithm / NSGA-II | Medium | 37 to 51% | Worst at 500 runs; fair with thousands | Later, only for cheap evaluations and several objectives |
| Model-based (RBFOpt) | Large, a library | not tested | Most robust | Not now |

## 6. The experiments

All in `docs/research/experiments/algorithmic-design/`; Node 22.23.4 (V8, the engine Chromium uses) on Linux
x64, except e05 in Chromium 153.0.8010.12.

- **e01, graph evaluation** (`e01-graph-eval.js`, `e01-results.txt`; medians of 200 runs). Ordering plus whole
  re-evaluation: 100 nodes 0.008 ms; 1,000 nodes 0.034 ms; 10,000 nodes 1.28 ms; 100,000 nodes 31 ms.
  Recomputing only what one changed source reaches: 0.01 to 0.1 ms at every size (about 30 nodes recomputed).
- **e02, split grammar** (`e02-split-grammar.js`, `e02-results.txt`). Core of 50 lines. Four facades of a
  9.6 m box, a ground floor and 10 storeys of 8 bays: 1,632 leaves, 2,325 steps, 0.46 ms. A 96 by 48 m,
  40-storey box: 48,240 leaves, 36 ms.
- **e03, identity** (same script). 320 windows, ids as index paths. Window width or sill changed: all 320 ids
  kept, none displaced. Bay 1.2 to 1.0 m (8 bays become 10): 320 kept, 80 new, and 220 of the kept ids now
  name a window more than 0.6 m from where it was. One storey more: 320 kept in place, 32 new. Also: `ceil`
  against nearest for the repeat: a 35.1 m height gives 11 storeys of 3.19 m under `ceil`, 10 of 3.51 m under
  nearest.
- **e04, search methods** (`e04-optimise.js`, `e04-results.txt`; 51 seeds). A block on an L-shaped lot under a
  floor-area cap and a height plane. Median share of the best floor area at 50, 100, 200, 500, 2,000 runs:
  pattern search 31, 52, 72, 93, 100; Nelder-Mead 26, 48, 51, 93, 100; genetic (population 20) 14, 30, 51, 89,
  100; random 6, 17, 23, 39, 50. One toy problem: it agrees with the benchmarks, it does not replace them.
- **e05, the browser** (`e05-browser.cjs`, `e05-page.html`, `e05-results.json`). Part 4.6.
- **e07, a second window** (`e07-windows.cjs`, `e07-page.html`, `e07-results.json`). Part 10a.
- **e06, the app's wall geometry** (`e06-app-elements.mjs`, `e06-results.txt`). `bimBuildWallGeometry` costs
  a few thousandths of a millisecond per straight wall (1,000 walls in 3.4 ms). The interactive makers and the
  opening cutter could not be measured outside a browser: they exhaust memory in the unit-test stand-in, and
  `bimBuildWallOpening` is private to its file.

## 7. Edges

- A repeat whose size is larger than the scope: one piece, stretched (at least one).
- A split whose absolute parts exceed the scope: the last part is cut, later parts dropped (Esri's examples).
- A count change: overrides beyond the new count are parked, not deleted, and return when the count returns.
- A rule renamed or removed: its overrides become semantically invalid and are listed.
- A generated element edited by hand in a way no override can express (its mesh pushed and pulled): it must be
  detached from its generator, said plainly, or the edit refused.
- A cycle in the graph: refused when the edge is made. Today `bimGraphPropagate` warns and carries on.
- Non-rectangular faces, L-shaped footprints, setbacks larger than the face: outside a box-scope grammar.
- An unknown value into a node gives unknown, never 0 (V215's rule, kept).

## 8. What the app already has

From `research-algorithmic-design/app-code-audit.md` (P, the code; paths under `src/js/engine/`).

- A dependency graph derived on each call, ordered by Kahn's algorithm, which does not refuse cycles
  (`bim/dependency-graph.js:85-210`); propagation entry `bimPropagateFrom` (`bim/region-dependents.js:334-377`).
- Element makers that are already A-BIM operations: `buildWallSolid` (`bim/import-compliance.js:179`),
  `buildFloorSolid` (`bim/ceiling-floor-profile.js:79`), `buildColumnSolid` and the opening makers
  (`bim/columns-openings.js:130`, `406-437`), `buildRoofSolid` (`bim/roofs.js:473`). Each takes its own undo
  snapshot, repaints and saves.
- Ids from the clock and a counter: stable across save and reopen, new on every generator run. No "generated
  by" field on BIM elements, though provenance fields exist elsewhere (`dg`, `linkSourceId`, `bim.sourceId`,
  `bim.hostId`). The one precedent for keyed regeneration is `bimDgPlace` (`site-analysis/model-layers.js:59-104`).
- Undo is a JSON snapshot of a fixed list of twenty fields, 50 deep (`drawing/plan-mode-sketch.js:291-351`);
  a new top-level field must be added to both the snapshot and the restore.
- A stored project's unknown top-level keys are dropped on load (`core/state.js:64-131`); `A3D.site.*` already
  carries zoning, tools and Ladybug data and avoids that.
- Three-way merge per element and field (`history/branches-merge.js:75-107`).
- Blob-made workers with transferables: Ladybug (`ladybug/runtime.js:154-201`) and gzip (`io/file-save.js:139-178`).
- No instancing; a mesh change is seen when `o.mesh` is replaced by a new object (`render/gpu-batches.js:109-160`).
- Typed-parameter tools with a run history (`site-tools/tools.js:196`): the precedent for a rules panel.
- Objectives ready to call: `bimZnCalc` (synchronous), `bimFrameSolve`, `bimUsageSummary`; Ladybug runs are
  asynchronous, one at a time, seconds each.
- Still header-only: `bim/parametric.js` (V204), `commands/flows.js` (V215), `site-tools/generators.js` (V213).

**Gaps the first phase must close:** a batch way to add elements (one undo step, one repaint, one save); a
key and a generated-by field on elements; reconciliation by key on a re-run; cycles refused.

## 9. Risks and threats to validity

- The timings are from Node on a server, not a phone. The ratios should hold; the absolute numbers will not.
- e06 could not measure the opening cutter or the interactive makers. If cutting a window costs milliseconds,
  a 1,000-window facade needs a worker or a faster path; that is the first thing the phase's browser check
  must measure.
- Undo snapshots hold every mesh: a large generated facade makes each undo step large. Generated meshes may
  have to be left out of the snapshot and re-derived.
- H5 rests on two small studies by interested authors.
- Wortmann's benchmarks are by the developer of the winning tool; Waibel's counter-evidence was read as an
  abstract only.
- Several pages were read through a fetch tool's extraction, not raw; any number the code uses from them is
  re-read first.
- Firefox and Safari were not tested for workers from `file://`.
- The app audit is a condensed hand-back; its line numbers were checked only for the facts in part 3a.

## 10. What is still open (U), and why

- The early shape-grammar papers (Stiny and Gips 1972 and others): hosts refused. Nothing in the code depends
  on them.
- Mueller et al. 2006's split arithmetic: the second reader could not reach the paper (part 3a).
- Kripac 1997; Marcheix and Pierra 2002; Grasshopper's data trees; Houdini; Blender's evaluator: not reached.
- Manifold's speed in wasm and on phones; whether its module glue can be embedded in the one file: needs an
  approved experiment.
- NSGA-II's numeric settings; primary sources for Hooke and Jeeves and Latin hypercube sampling.
- The "70% early massing" claim: not found anywhere.
- The cost of the app's opening cutter and interactive makers in the browser.

## 10a. Round two, 2026-11-15: the Grasshopper question and the languages

The owner, after reading the first round: "This needs more research. Because i want to know how we can do
this. Should we have a grasshopper engine popup on a tab in web that link to the model? Like how grasshopper
run in rhino? What are the model generation languages outhere?" Two more researchers
(`research-algorithmic-design/hosts-and-interfaces.md`, `generation-languages.md`) and one experiment (e07).
Both researchers were stopped by the usage limit near the end; their summaries and the languages table were
written by the coordinator from their findings, and that is said in each note. No independent second reading
was made of this round.

### How Grasshopper is attached to Rhino, and what the BIM hosts changed

- Grasshopper is a plug-in with its own canvas window. Its link to the model is three separate things: a
  parameter that holds a Rhino object's id and reloads it (in); a preview drawn in the viewport that is not
  in the document, so it cannot be selected, saved or put on a layer (out, temporary); and a bake that copies
  the result into the document and keeps no link, so baking twice makes two sets (out, permanent). P, the
  Grasshopper API. Confidence high.
- Every vendor who took a graph to a BIM host dropped preview-then-bake for tracked elements, real from the
  start and updated in place: Rhino.Inside.Revit (per component: Update, Replace or Disabled, with a
  duplicate warning on Disabled and on Release), the Grasshopper-Archicad connection (what the graph controls
  is overwritten on each run; what it does not control keeps the hand-set value), Rhino 8's Content Cache,
  Dynamo's binding. P. Confidence high. This is round one's identity finding again, from the vendors' side.
- Tracking still fails at the key: orphans when a count shrinks, bindings lost between files, and
  Rhino.Inside.Revit's tracking is reported to be by output index (U), the weakest key Lipp 2019 measured.

### The four ways a rule engine meets its model

| Pattern | Who | What goes wrong | One-file offline app | Phone |
|---|---|---|---|---|
| (a) A canvas in its own window or tab, model-wide | Grasshopper, Dynamo | Preview and real objects confused; duplicates on re-bake; graphs unreadable at size (1,982 shared scripts: 97.5% without modules, S) | Possible with our own editor; only the tracked form is worth building | Poor: no vendor ships one |
| (b) The rule owned by an object, inputs in the properties panel | Blender Geometry Nodes, Marionette objects, Archicad Param-O, Houdini assets, SketchUp Live Components | Scope is one object; a shared definition changes every instance; detaching ends the link | Good: it is what V204 and V213 already are | Good |
| (c) A form that hides the graph (a player) | Dynamo Player, Grasshopper Player, ShapeDiver, Hypar | Limited input types; users cannot go past the form; the web ones compute on servers | Good, as the face of (a) or (b) | Good: the only form vendors ship on tablets |
| (d) Code and model as one | Zoo's KCL, CascadeStudio, OpenSCAD | Needs a language and interpreter; text is poor on touch | Poor now | Poor |

- Nothing found is a client-side, permissively licensed graph engine that makes BIM elements and could be
  vendored: the BIM-aware ones are services or desktop plug-ins (Hypar, Speckle Automate, Rhino.Inside), the
  client-side ones make geometry only (Nodi, Bitbybit's packages, CascadeStudio), Chili3D is AGPL, and That
  Open Engine has no generative part (P, their READMEs and licences). The engine is ours to write.
- e07 (measured, Chromium 153): a second window linked to the model works from `file://`. An empty window
  the model page writes into shares its script, so the editor can live there with no messaging; a second copy
  of the app in another tab can talk by `postMessage` or `BroadcastChannel` but cannot be reached into
  directly from `file://`. A real phone was not tested (desktop Chromium emulating one opens windows).

**Answer to the owner's first question.** Yes to a graph editor that opens beside the model and stays
linked to it, and it can be a docked tab or a popped-out window. No to the Rhino relationship itself
(preview, then bake): the BIM hosts all abandoned it. The order that follows from the evidence: the rule
lives on a generator object in the model (b), its inputs are a form in Properties, which is also the player
(c) and works on a phone; the canvas (a) comes after, as the author's view of the same records, on desktop
and tablet. The engine does not wait for the canvas.

### The model generation languages

Five families (`generation-languages.md`, part 2, each entry with what was read):

| Family | Examples | Makes | Use to this app |
|---|---|---|---|
| CSG scripts | OpenSCAD (GPL), JSCAD (MIT), libfive, Curv | Solids, no building elements | The idea of a readable tree; OpenSCAD's licence rules it out, JSCAD is code to run |
| Code on a B-rep kernel | CadQuery, build123d, Replicad, KCL, FeatureScript | Exact solids | Needs OpenCascade (22.9 MB) or a vendor's server |
| Grammars and constraint generators | CGA, L-systems, Wave Function Collapse | Named shapes | Split grammars: round one, 50 lines of core |
| Dataflow graphs | Grasshopper `.ghx`, Dynamo `.dyn` and DesignScript, Geometry Nodes, Houdini, Marionette | Whatever the host's nodes make | The files can be read; the node libraries are the hosts'. DesignScript's ideas are worth taking |
| BIM-oriented | Archicad GDL, Revit families, Hypar Elements, IfcOpenShell's Python API, Topologic | Building elements | None adoptable as is: proprietary, or services, or Python. IfcOpenShell's API is already in the app's Python worker |

- There is no open, implemented standard for a parametric or procedural model; IFC records the result (P).
- Text-to-model systems moved from token sequences to readable code or structured text in two years. The
  building ones give the model a small vocabulary of element calls (Text2BIM: 26 functions), not geometry and
  not raw IFC. General models compile CadQuery 85 to 96% of the time without training, but compiling is not
  being right: 48% of errors were structural, and Text2BIM's own authors report illogical door and window
  placement and a clear gap from real designs (P, the papers). Confidence medium: a young field.
- A new format has no training data and must be taught in the prompt each time; JSON itself is well known to
  models and a schema can force validity (the first P, the second inference).

**Answer to the owner's second question.** No existing language can be adopted. The app should speak its
own small format: rules and element-level calls as schema-checked text (JSON), shown as a form, later as a
graph, and always readable and pasteable as text. It borrows the scope, split and repeat from CGA; one
definition yielding plan, solid, schedule values and form from GDL; one assignment per name and replication
from DesignScript; a small element vocabulary from Text2BIM; permanent node ids with the layout stored apart
from Dynamo's file. Python through the existing worker (IfcOpenShell's API) is a later escape hatch.

## 11. The owner's decisions

Asked together, 2026-11-15, 1 to 10 after round one and 11 to 13 after round two. Each has the
recommendation and what it rests on.

**Answered 2026-11-15: all thirteen as recommended** (the owner: "Just do whats recommended"). The phases are
V228 to V232 in `docs/dev/PIPELINE.md`; V228 and V229 have their work orders (`docs/work-orders/v228/`,
`v229/`); V230 to V232 get theirs after the first two are wired.

1. **The approach.** Generators as records with typed parameters and rules as data first; the model graph and
   the node editor after (option A, part 5). Or the node editor first (B)? Recommended: A.
2. **The first slice.** Generated elements with a key, in-place re-run and stored overrides, then the facade
   split grammar. Recommended: yes, as the next two phases after V204, V213 and V215.
3. **When a count changes** (8 bays become 10). An override stays with its storey and bay number; one whose
   place is gone is parked and listed, and returns if the place returns. Or follow the nearest position?
   Recommended: by number, parked and listed (Lipp 2008 and 2019; e03).
4. **The repeat's rounding.** Nearest count, at least one (least stretching), or `ceil` as the 2006 paper?
   Recommended: nearest (e03's table: `ceil` turns 35.1 m into 11 storeys of 3.19 m).
5. **Manifold.** Approve an isolated experiment that downloads `manifold-3d` and tries to embed it in the
   one-file build from `file://`? Recommended: yes, but only when a phase needs booleans; not for phases 1, 2.
6. **Clipper2** (Boost Software License 1.0, for polygon offsets and setbacks). Add BSL-1.0 to the allowed
   licences? Recommended: decide when a phase needs offsets; the licence itself is permissive.
7. **Search.** Sampling with a Pareto filter and a parallel-coordinates view, then pattern search; no genetic
   algorithm at first. Recommended: yes (Wortmann 2019; Autodesk's practice; e04).
8. **The node editor.** Our own in ES5 with pointer events, since no library is both framework-free and good
   on touch; or adopt litegraph.js and fix its touch handling? Recommended: our own, as phase 5.
9. **A text language.** Not now. Recommended: agreed, revisited after the graph exists.
10. **Phase numbers.** V228 to V232 for the five phases, after the queue's V227; V204, V213 and V215 stay where
    they are and ship first. Or move them earlier in the queue?

Added by round two (part 10a). Decision 11 sharpens 1 and 8; decision 13 amends 9.

11. **The Grasshopper question.** The rule lives on a generator object in the model, with its inputs as a
    form in Properties (works on a phone); the graph canvas comes after, as the author's view of the same
    records, dockable as a tab or popped out as a window (e07), on desktop and tablet. Generated elements are
    real and tracked from the start: no preview-then-bake. Or build the canvas first, as Grasshopper has it?
    Recommended: the object and form first, the canvas after.
12. **The language.** The app's own format: rules and element-level calls as schema-checked JSON. Or JavaScript
    programs in a worker (as JSCAD), or Python in the existing worker (IfcOpenShell's API)? Recommended: our
    own format; Python as a later escape hatch; no JavaScript programs.
13. **A text view from the start.** Show a generator's rules as text beside its form from the first phase,
    with paste, export and validation, so a rule set written outside the app (by hand or by a language model)
    can be brought in and checked before it runs. This is a view of the data, not a programming language
    (decision 9 stands). Recommended: yes.

## 12. References

The full lists, with what was read in each and its level, are part 8 or 9 of each researcher's note. The
sources the recommendation rests on (all read 2026-11-14 or 2026-11-15):

- Mueller, Wonka, Haegler, Ulmer, Van Gool, "Procedural Modeling of Buildings", 2006.
  https://peterwonka.net/Publications/pdfs/2006.SG.Mueller.ProceduralModelingOfBuildings.final.pdf (section 2; U after the check)
- Wonka, Wimmer, Sillion, Ribarsky, "Instant Architecture", 2003.
  https://www.cg.tuwien.ac.at/research/publications/2003/Wonka-2003-Ins/Wonka-2003-Ins-Paper.pdf (P)
- Lipp, Wonka, Wimmer, "Interactive Visual Editing of Grammars for Procedural Architecture", 2008.
  https://www.cg.tuwien.ac.at/research/publications/2008/LIPP-2008-IEV/LIPP-2008-IEV-paper.pdf (P)
- Lipp, Specht, Lau, Wonka, Mueller, "Local Editing of Procedural Models", 2019.
  https://peterwonka.net/Publications/pdfs/2019.EG.Lipp.LocalEditingProceduralModels.pdf (Table 2, P)
- Esri, CityEngine CGA reference. https://doc.arcgis.com/en/cityengine/latest/cga/ (the split operation, P)
- cgajs (Apache-2.0) https://github.com/gromgull/cgajs ; shapeml (GPL-3.0) https://github.com/stefalie/shapeml (code as text, P)
- Bruls, Huizing, van Wijk, "Squarified Treemaps", 2000. https://www.win.tue.nl/~vanwijk/stm.pdf (P)
- Mokhov, Mitchell, Peyton Jones, "Build Systems a la Carte" (P); Jane Street Incremental
  https://raw.githubusercontent.com/janestreet/incremental/master/src/incremental_intf.ml (P); Salsa
  https://raw.githubusercontent.com/salsa-rs/salsa/master/book/src/reference/algorithm.md (P); TC39 signals
  https://raw.githubusercontent.com/tc39/proposal-signals/main/README.md (P)
- Grasshopper API, ExpireSolution.
  https://developer.rhino3d.com/api/grasshopper/html/M_Grasshopper_Kernel_GH_ActiveObject_ExpireSolution.htm (P)
- Khepri https://github.com/aptmcl/Khepri.jl and https://github.com/aptmcl/KhepriBase.jl (code as text, P)
- DynamoRevit https://github.com/DynamoDS/DynamoRevit (element binding, code as text, P); the Dynamo primer
  https://primer2.dynamobim.org/1_developer_primer_intro/3_developing_for_dynamo/13-dynamo-integration (digest)
- Rhino.Inside.Revit guide.
  https://raw.githubusercontent.com/mcneel/rhino.inside-revit/1.x/docs/pages/_en/1.0/guides/rir-grasshopper.md (P)
- FreeCAD, the topological naming problem.
  https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Topological_naming_problem.md (P)
- Manifold https://github.com/elalish/manifold ; its wiki
  https://raw.githubusercontent.com/wiki/elalish/manifold/Manifold-Library.md ; npm `manifold-3d` 3.5.5 (P)
- Clipper2's licence. https://raw.githubusercontent.com/AngusJohnson/Clipper2/main/LICENSE (P)
- litegraph.js https://github.com/jagenjo/litegraph.js ; Drawflow https://github.com/jerosoler/Drawflow (P)
- Wortmann, "Genetic evolution vs. function approximation", 2019.
  https://academic.oup.com/jcde/article/6/3/414/5732355 (P)
- Deb, Pratap, Agarwal, Meyarivan, "A fast and elitist multiobjective genetic algorithm: NSGA-II", 2002.
  https://sci2s.ugr.es/sites/default/files/files/Teaching/OtherPostGraduateCourses/Metaheuristicas/Deb_NSGAII.pdf (P; settings S)
- Autodesk, Generative Design in Revit.
  https://help.autodesk.com/cloudhelp/2024/ENU/Revit-GDiR/files/GUID-887BCC49-06E9-4C52-AECD-BE92646DF2F5.htm (P)
- Hypar Elements. https://raw.githubusercontent.com/hypar-io/Elements/master/README.md (P)
- Speckle, versions and comparing them. https://docs.speckle.systems/workspaces/versions.md (P)
- The app's own code and earlier notes: `research-parametric-history.md`, `research-parametric-app-audit.md`,
  `research-usd-brep.md`, `research-later-generators.md`, `research-notion-flows-sdk.md`, `research-giraffe.md`.
