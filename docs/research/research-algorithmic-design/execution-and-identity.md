# Algorithmic design: execution models and the identity of generated objects

One of five parallel research notes for `00-question.md`. Side: how algorithmic-design tools evaluate
(H1), how generated elements keep their identity across re-runs (H3), and text against node graphs (H5).
Started 2026-11-14, continued 2026-11-15. Levels: P = read in the source itself, S = dependable secondary,
U = unverified. Finished 2026-11-15; what was not reached is in part 6.

## 1. Summary of findings

| # | Finding | Level | Confidence |
|---|---|---|---|
| F1 | No professional algorithmic-design tool read here keeps a fine-grained incremental engine as its base model. Grasshopper expires an object and everything downstream of it and re-solves those; Khepri, Rosetta and Luna Moth delete everything and re-run the program; Dynamo re-runs changed nodes and their dependents. The saving in every case is "do not recompute what did not change", at node granularity. | P (Grasshopper API page, Khepri code, Dynamo primer), S for Dynamo's scheduler | High |
| F2 | The simplest correct incremental algorithm for a static graph is: mark the changed node and its downstream dirty (push), then recompute dirty nodes in topological (height) order, each at most once, with an equality cutoff. This is Make's scheduler plus Excel's dirty bit plus Shake's early cutoff in the vocabulary of Build Systems a la Carte, and what Jane Street Incremental does. | P (four sources) | High |
| F3 | The named failure modes are glitches at diamonds (cured by height order or by pulling), cycles (must be detected and reported), dynamic dependencies (break a precomputed order), and the cost or wrongness of equality on large values (use a version stamp). | P | High |
| F4 | Identity of generated elements is always a key made from how the element was made, never from its geometry: Dynamo keys by node call site (and position in the node's output list); Rhino.Inside.Revit by component output and item index; CGA by the path of sibling indices in the derivation tree; FreeCAD by modelling history. | P (code, guide, paper, wiki) | High; medium for Dynamo's list position |
| F5 | Every such key breaks when the count or order of siblings changes. Tools differ in what they do then: Dynamo and Rhino.Inside rebind by position (data can land on a different element, or elements are deleted and re-made); CGA meta-locators keep an unmatched edit parked and re-apply it when the place returns; FreeCAD 1.0 reports the broken reference. | P | High |
| F6 | A pure index path ("exact locator") transferred 0% of local edits in three of five model changes measured by Lipp et al. 2019; context-based keys (floor index, tile index, per attribute) transferred 100%, 100%, 100%, 100% and 93.8%. | P (their Table 2) | High for the numbers; medium for transfer to our case (CityEngine models only, authors are the vendor) |
| F7 | On text against nodes, the evidence is thin and mostly from one group. Leitao, Santos, Lopes 2012 is an experiment with six designers and no control of task order; it finds visual programs slow to build and poor at scale, and that people who know a text language write better visual programs. Celani and Vaz 2012 is a course report (classes of about thirty) and finds the visual tool the better start for novices, limited to parametric variation. No controlled study with a proper sample was found. | P (both papers) | Medium that "nodes to start, text to scale" is the consensus; low that it is established by measurement |
| F8 | The ADA group itself moved from "text is better" (2011, 2012) to a hybrid (Khepri components inside Grasshopper, 2020), recommending nodes for exploration and text-built components for the complex parts. | P (Visual Meets Textual, 2020) | High |

## 2. Findings by topic

### 2.1 How the tools evaluate

**Khepri (ADA group, Leitao). P, code read as text.** Repository `aptmcl/KhepriBase.jl`, commit
`a303d45c8b523e9cf452a70c81b4860a4e087d26` (2026-08-02), MIT. `aptmcl/Khepri.jl` (commit
`f76abd96c2eca6ff2f3a1d619203777ddc02575f`, 2026-08-01, MIT) is now a 4-line meta package re-exporting
`KhepriAutoCAD`; the engine is KhepriBase.

- A shape is a `Proxy` held in the program; each backend keeps a dictionary from proxy to the backend's
  native reference. `ref(b, s)` realizes the proxy in the backend the first time it is asked for and
  caches the reference (`src/Shapes.jl` lines 127 to 132). The same program is "portable" because the
  proxy is backend-neutral and each backend supplies `realize`.
- There is no incremental evaluation and no persistent identity of elements across runs. The re-run
  model is: `delete_all_shapes()` then run the whole program again. `b_delete_all_shapes` clears the
  trace table, deletes the backend's shapes and empties the proxy-to-reference dictionary
  (`src/Shapes.jl` lines 529 to 535). Every re-run makes new backend objects.
- "Traceability" is the link Khepri does keep: with `traceability(true)`, each created shape records
  the source locations (file, line) of the stack frames that created it, and a reverse table maps a
  source location to its shapes (`src/Shapes.jl` lines 378 to 472). It links program and model for
  understanding (select a shape, see the code; select a line, highlight the shapes). It is cleared on
  every `delete_all_shapes`, so it is not an identity that outlives a run.

Confidence: high for what the code does (read directly).

- **Search of the rest of KhepriBase** was not completed beyond `Shapes.jl`; the "no identity across
  runs" finding rests on `Shapes.jl` and on the group's own papers describing delete-and-regenerate.

**Rosetta (Lopes and Leitao 2011, "Portable Generative Design for CAD Applications"). P.** Front-end
languages compile to one intermediate language over an abstraction layer of modelling operations;
back-ends translate that layer to each CAD application. Portability is the abstraction layer, nothing
more: no dependency graph and no incremental evaluation.

**A-BIM ("Portable Generative Design for Building Information Modelling", 2016; the eCAADe 2016 A-BIM
paper itself is a scanned PDF with no text layer and was not read). P for the first.** The same
abstraction layer raised to BIM operations (slab, wall, beam with a family) so one program builds in
Revit and Archicad; where a back-end lacks a family the operation takes the back-end's own. The claimed
gain is that a change to the program propagates to all components without manual update. Nothing on
identity of elements between runs.

**Luna Moth (2017). P.** An HTML5/JavaScript environment in the browser with a text language, immediate
feedback (re-running the program on each edit) and traceability in both directions. The paper itself says
immediate feedback stops being possible when run time grows, and that it was slower than the desktop
tools. This is direct prior art for a browser app and for H1: whole re-run is fine until geometry
dominates.

**Grasshopper. P (Grasshopper API reference, `GH_ActiveObject.ExpireSolution`, build dated 2026-11-10).**
Expiring an object sets it blank and "is recursive, it will also expire any and all objects which depend
on this object"; with `recompute` true the document then solves the new state. So the model is dirty
marking pushed downstream, then one solve of the expired part; objects not downstream keep their data.
No early cutoff is described: a downstream object is re-solved even if its input came out the same.
Data trees were not read (the developer guide pages returned 404). U.

**Dynamo. P for binding (2.4); S for evaluation.** The integration page describes a DesignScript virtual
machine with call sites per node; it does not describe the scheduler. That only modified nodes and their
dependents re-execute is from memory of Dynamo's documents, not read today. U until read.

**Blender Geometry Nodes. P (developer documentation, "Fields" and "Analysis: Caching").** A field is an
immutable tree of functions evaluated later against a context (for example a mesh and its position
attribute): the node graph builds a function, it does not compute per-element values node by node. The
caching analysis lists "cache intermediate node evaluation results, for faster parameter tweaking" as a
use case and names the challenges: memory, and keeping inputs and results in sync. The lazy-function
evaluator itself was not read. U.

**Houdini, Hypar, Grasshopper-Archicad.** SideFX's cooking page returned 404 at two addresses; not read
(U). Hypar Elements' README (P) says only that an Element is "a uniquely identifiable piece of a building
system" produced by functions; how ids persist between function runs was not found (U). Graphisoft's
live connection was not reached (U).

### 2.2 Incremental computation as an algorithm (saved 2026-11-15)

- **Build Systems a la Carte (Mokhov, Mitchell, Peyton Jones; JFP 2020 version). P.** A build system is a
  scheduler (the order tasks run in) times a rebuilder (how it decides a task is out of date). Schedulers:
  topological (order computed in advance, needs static dependencies; Make), restarting (run in a remembered
  order, abort and retry a task whose input is not ready; Excel's calc chain, Bazel), suspending (compute
  an input on demand, then resume; Shake). Rebuilders: a dirty bit (Excel: one bit per cell, set on the
  changed cell and everything depending on it), verifying traces (remember the hashes of the inputs a
  result was built from; Shake), constructive traces (also keep the result, so it can be fetched; Bazel).
  "Minimal" means a task runs at most once per build and only if an input changed. "Early cutoff" means
  that when a task re-runs and gives the same result, its dependents are not re-run; Table 1 of the paper
  says Make and Excel have no early cutoff, Shake and Bazel do (section 2.3, 4.1 to 4.3, 5.1).
- **Jane Street Incremental, `incremental_intf.ml`. P.** `stabilize` visits changed nodes in non-decreasing
  height using a recompute heap (an array indexed by height); each node is computed at most once and
  after its children; a per-node "cutoff" (default: physical equality) stops propagation when the new
  value equals the old. Only "necessary" nodes (those an observer depends on) are computed. Height must
  stay small (default limit 128). Cycles are detected when heights are adjusted and raise an error.
- **Salsa "red-green" (book, reference/algorithm). P.** Pull-based: a global revision counter; each
  memoised result stores the revision it was verified at and the revision it last changed; on demand,
  inputs are checked first and the function re-runs only if one changed; "backdating" is early cutoff
  (same result, so the changed-at revision is left alone).
- **Signals: Reactively README, TC39 signals proposal README. P.** Push-pull: a write pushes a mark down
  the graph (direct dependents "dirty", further ones "check"/"checked"), nothing is computed; a read pulls,
  re-evaluating the deepest dirty sources first, and a "checked" node whose sources turn out unchanged
  becomes clean without running. The proposal defines "glitch" (a node seeing a mix of old and new values,
  or running twice for one change) and says the pull in topological order removes it; cycles are detected
  by a "computing" state and throw.

**Failure modes recorded in these sources.** Glitch and the diamond (A feeds B and C, both feed D: a naive
push runs D twice, once with a stale input): removed by ordering by height or by pulling. Cycles: must be
detected and reported; Incremental makes the system unusable after one. Dynamic dependencies (a node whose
inputs depend on a value): they break a precomputed order; this is why Excel restarts and Incremental
adjusts heights. Equality for cutoff: cheap for numbers, costly or wrong for meshes unless a version stamp
is compared instead. Confidence: high (four primary sources of different kinds agree).

### 2.3 Text against visual programming in architecture (saved 2026-11-15)

- **Leitao, Santos, Lopes 2012, IJAC 10(1) 139-162. P (author's copy; sections 3 to 5).** The experiment:
  six designers, group A three Grasshopper users with no text language, group B three with one. Phase 1
  (a tower in Grasshopper): group A 50/94/140 minutes (min/average/max), group B 25/37/50. Phase 2
  (modify it): A 20/37/60, B 20/23/25. The authors' text-language solution of the variation took under
  10 minutes by reuse. Their conclusion: Grasshopper "does not scale well with the complexity of the
  design task", for lack of abstraction and control structures (iteration, recursion) and the time spent
  on wires and boxes. Limits they state themselves: few subjects, times rounded to 5 minutes, group times
  only, "preliminary findings". Not stated but plain: the authors built the text tool being compared.
- **Celani and Vaz 2012 (IJAC 10(1); read in the Cadernos Proarq 18 English copy). P.** A course report,
  not an experiment: classes of about thirty; one exercise in VBA for AutoCAD, one in Grasshopper,
  opinions compared with earlier years that used text only. Fewer requests for help in the Grasshopper
  exercise; results "much above expectation". Conclusion: visual environments let students with no
  programming implement generative strategies "in a relatively simple way", but this does not remove the
  need for scripting later; only parametric variation was compared, not rule-based systems.
- **Castelo-Branco and Leitao 2020, "Visual Meets Textual". P.** Cites the older literature (Burnett;
  Green and Petre) for visual programs having low information density and scaling badly; then builds
  Khepri components for Grasshopper and concludes exploration is best done with nodes and the complex
  parts with text-built components. Lists what makes nodes pleasant and can be given to text too:
  traceability, immediate feedback, sliders.
- **Castelo-Branco, Caetano, Leitao 2022 (Frontiers of Architectural Research) and Janssen's visual
  dataflow papers.** Not read: the first was seen only as a search result; the cumincad addresses tried
  for Janssen returned other papers. U.

### 2.4 Identity of generated objects (saved 2026-11-15)

For the earlier instance and semantic locators (Lipp, Wonka, Wimmer 2008) see `grammars-and-layout.md`;
not repeated here.

- **Dynamo element binding (trace). P: Dynamo developer primer "Dynamo Integration", and DynamoRevit code
  read as text (`ElementBinder.cs`, `Wall.cs`, Apache-2.0, master as of 2026-11-15).** The key is the call
  site of a node in the graph (node GUID plus function-scope and instance markers), not anything about the
  element. The value is the host element's id (Revit UniqueId). It is saved in the `.dyn` file under
  "Bindings" (JSON, gzip, Base64). A create node asks trace for its previous element
  (`GetElementFromTrace`); if found and the host allows, it mutates it (the wall node resets the curve,
  level and type), else it makes a new one and `CleanupAndSetElementForTrace` deletes the old. So hand
  edits to properties the node does not set survive; properties it sets are overwritten. The primer does
  not say how list items are keyed; from the code a node storing many elements stores an ordered list of
  ids (`MultipleSerializableId`), so identity inside a list is by position.
- **Rhino.Inside.Revit element tracking. P (guide `rir-grasshopper.md`, branch 1.x).** Each Add
  component's output remembers the Revit elements it made, across saves. Modes: Disabled (duplicates),
  Replace (new element each run), Update (default: modify in place if the Revit API allows, else replace).
  S (McNeel forum, staff reply, via search only: U until read): matching is by the Grasshopper item index.
- **Khepri. P.** No identity across runs (2.1): delete all, regenerate.
- **CGA / CityEngine: Lipp, Specht, Lau, Wonka, Mueller 2019, "Local Editing of Procedural Models". P
  (author's copy, sections 3, 4, 5, 7).** Three schemes are compared. (a) The exact locator or "treekey":
  the list of sibling indices on the path from the root of the derivation tree to the node. It is unique
  but breaks whenever the tree changes. (b) Semantic locators (Lipp, Wonka, Wimmer 2008): tags written
  into the rules. (c) Their meta-locator: for each edited attribute, a list of (context function, index)
  pairs such as (floor index along y, 2), (tile index along x, 1), computed from the spatial order of
  siblings, with wildcards and ranges for multi-selection. Edits are stored as (meta-locator, attribute,
  value) with the initial shape and re-matched (exact, then unordered, then by global order) whenever the
  rule or the initial shape changes. Their Table 2 (five model changes, 7 to 48 edits each): exact
  locators transferred 0%, 0%, 0%, 100%, 100% of edits; semantic locators 0%, 100%, 28.6%, 100%, 75%;
  meta-locators 100%, 100%, 100%, 100%, 93.8%. Stated failures: an edit that addresses a place
  that no longer exists (floor 6 of a 4-floor building) is unmatched; it is kept and matches again when
  the floor returns; if a split collapses to one part the edits on it stop matching; recursion makes
  redundant locations.
- **FreeCAD topological naming. P (FreeCAD documentation, wiki page as Markdown; realthunder's
  "Topological Naming Algorithm" wiki page).** The problem: sub-shapes are named by index (`Face13`); a
  change upstream renumbers them and features attached by name break or attach to the wrong face. The fix
  shipped in FreeCAD 1.0 names each element from the modelling history: (1) copy the names of unchanged
  elements; (2) name generated and modified elements from the kernel's history map (source element plus
  operation); (3) name what is left by index under its named parent; (4) name what is still left by the
  set of its named children. The wiki calls it heuristics that "reduce the impact", not a full cure.
- **Kripac 1997; Marcheix and Pierra 2002.** Not read here (publishers refused; see part 6). U.

**What the schemes have in common.** Identity is never a property of the geometry; it is a key built from
how the thing was made: (generator, path of rule or operation, index within siblings). Every scheme breaks
at the same place: when the count or order of siblings changes, an index points at a different thing.
The better schemes (meta-locators, realthunder) add semantic context to the index and report or park what
no longer matches instead of silently re-attaching it. Confidence: high for the mechanisms (code and
paper read); medium for the list-position claim in Dynamo (read from code, not from a document).

## 3. H1, H3, H5

**H1 (evaluation cost): supported by the literature, undecided until measured here.** Nothing read
contradicts it and three things support it. Luna Moth (a browser tool) re-ran the whole program on every
edit and lost immediate feedback only when run time grew (geometry). Grasshopper's own model is coarse
(expire downstream, re-solve) with no early cutoff, and is the field's most used tool. Build Systems a la
Carte shows the dirty bit is the cheapest rebuilder and that what saves real work is not re-running
expensive tasks whose inputs did not change (traces, cutoff). The second half of H1 (cache a node's output
by its inputs) is exactly the "verifying trace"; it holds as the saving that matters. The 16 ms figure
itself is this app's to measure (another researcher's experiment); no source gives a number for ES5.
One correction to H1: caching by inputs needs a cheap equality. For meshes compare a version stamp or a
hash of the inputs, not the mesh.

**H3 (identity): held, with one amendment.** Held: every tool derives identity from the generating path
and an index; it survives a parameter change that keeps the counts (Dynamo mutates the bound wall; exact
locators survive when the tree is unchanged); all tools met the problem and document it. Amendment: "when
the counts change the identity changes" is true of a pure index path but is the weak form. Lipp et al.
2019 measured it: index paths lost all edits in three of five changes, while keys built from meaning
(storey number, bay number, side of the building, per attribute) kept them. So the identity should be the
rule path with semantic indices, not sibling positions, and an attachment whose key no longer exists
should be parked and reported, then re-applied if the place returns. "Reported, not hidden" is right and
is where Dynamo and Rhino.Inside are weakest (silent rebind by position or delete and re-make).

**H5 (text or nodes): partly held, on weak evidence.** The direction is what the hypothesis says: nodes
are the easier start (Celani and Vaz), text scales better (Leitao et al.), and the group that argued
hardest for text ended at a hybrid (2020). But no source is a controlled study: one is n = 6 by the
authors of the text tool, one is a course report. The design conclusion (a node graph with an expression
node first; a text language as a later, separate decision) is consistent with all three papers and with
practice (Grasshopper and Dynamo both carry script and expression nodes). What the papers add: the
specific things nodes cannot say well are iteration, recursion and abstraction (a reusable sub-graph), so
the node interface needs at least a repeat construct and grouping into a reusable node, or users will
hit the wall the 2012 paper describes.

## 4. Counter-evidence found

- Against "incremental bookkeeping is not worth it" (H1): Jane Street Incremental and Salsa exist
  because whole re-evaluation was too slow in their domains (large graphs, expensive nodes). The
  condition is the cost per node, which is H1's own claim. Blender's caching analysis names intermediate
  result caching as wanted for parameter tweaking. Nothing found says dirty flags help a graph of cheap
  arithmetic nodes.
- Against early cutoff being free: Build Systems a la Carte notes Excel and Make do without it; it needs
  an equality test per node, which on large values costs as much as it saves.
- Against stable identity by path (H3): Lipp et al. Table 2 (exact locators 0% in three of five);
  FreeCAD's wiki calls its own fix heuristics that reduce, not remove, the problem; Dynamo's known-issues
  page as returned by a search (not confirmed in the copy read here, U) describes leftover elements when a
  list shrinks between sessions; Rhino.Inside forum threads report duplicates and lost bindings (seen as
  search results only, U).
- Against meta-locators being a cure: their own limitations section (unmatched when the place is gone;
  a split collapsing to one part unbinds its edits; recursion multiplies locations), and 93.8% not 100%
  on the largest test.
- Against "text scales better" (H5): searched for a study finding visual better at scale or text no
  better; none found. Celani and Vaz is the nearest opposite finding and it concerns novices, not scale.
  The absence is of studies, not proof.

## 5. What a plain-ES5 app should take from this

1. **Evaluation: dirty bit, topological order, input-stamp cache.** Keep V215's Kahn order (a
   topological scheduler; correct because a flow's dependencies are static). On an edit, mark the node and
   its downstream dirty by one walk of the out-edges (Grasshopper's `ExpireSolution`; Excel's dirty bit).
   Recompute dirty nodes in the stored order, each once (Make's scheduler; Incremental's height order;
   this is what removes glitches at diamonds). Source: Build Systems a la Carte sections 4.1 and 5.1;
   `incremental_intf.ml`; Grasshopper API.
2. **Cutoff by version stamp, only on expensive nodes.** Each node output carries an integer version
   that increases only when the value actually changed. A node stores the versions of the inputs it last
   ran with and skips if they are equal (a verifying trace; Salsa's changed-at revision and backdating).
   Compare values for numbers and short strings; for geometry compare stamps, never meshes. Source: Build
   Systems a la Carte section 5.2 onward (traces); Salsa algorithm page.
3. **Cycles are an error at edit time.** Kahn's algorithm already detects them (nodes left over); refuse
   the wire and say why (TC39 proposal and Incremental both throw). Do not attempt fixed points.
4. **No dynamic dependencies in the first version.** They are what force restarting or suspending
   schedulers and height adjustment. An expression node's inputs are its declared wires.
5. **Do not import a signals library.** The push-pull three-state scheme (clean, check, dirty) exists to
   support dependencies discovered while running and unobserved lazy nodes. With a static graph of a few
   thousand nodes, items 1 and 2 are simpler and equivalent in work done.
6. **Identity: a key, stored on the element.** `generator id / rule path with named, semantic indices`
   (for example `flow12/facade:south/storey:3/bay:5/window`), not sibling position, wherever the rule
   knows the meaning (storey, bay, side). Fall back to an index only below a named level, as FreeCAD's
   step 3 does. Source: Lipp et al. 2019 sections 3 and 4; realthunder's algorithm steps 1 to 4.
7. **Re-run is update in place, by key.** After a run, match new outputs to existing elements by key:
   same key, mutate the element and keep its id, hand-attached data and anything the generator does not
   set (Dynamo's wall node; Rhino.Inside "Update"); new key, create; key gone, delete the element.
   Source: `ElementBinder.cs`, `Wall.cs`; Rhino.Inside guide.
8. **Overrides are stored beside the generator, not on the element.** A hand edit to a generated
   element is a tuple (key, property, value) kept with the generator and re-applied after each run (Lipp
   et al.: edits stored as locator, attribute, value with the initial shape). An override whose key did
   not match is kept, counted and shown ("3 edits have no element: storey 6"), and applies again if the
   key returns. Never rebind by position silently.
9. **Traceability both ways.** Selecting an element shows the node or rule that made it and the reverse
   (Khepri's two tables; Luna Moth). The key of item 6 gives this for free.
10. **Interface: nodes first, with the three things the 2012 study found missing.** An expression node,
    a repeat (map over a list or count), and grouping a sub-graph into a reusable node. A text language
    stays a later decision.

## 6. Still open (U) and why

- Kripac 1997 and Marcheix and Pierra 2002 (persistent naming): not fetched; publisher copies are
  behind paywalls and no author copy was sought for lack of time. Nothing in part 5 depends on them;
  FreeCAD's wiki and realthunder's page cover the same ground from an implementation.
- Dynamo: how trace keys items inside a replicated (list) call beyond position, and Dynamo's scheduler.
  The primer page read does not say. To confirm in `Dynamo/src/Engine/ProtoCore` (the path guessed for
  `TraceUtils.cs` returned 404).
- Dynamo known issues about leftover or lost elements: seen in a search summary of a fork's wiki; the
  DynamoDS wiki page fetched (14,981 bytes) had no line matching "bind" or "trace". U.
- Rhino.Inside matching by item index: a forum reply seen in a search summary only. U.
- Grasshopper data trees; Houdini cooking; Blender's lazy-function evaluator; Grasshopper-Archicad live
  connection; Hypar's element ids across runs; Adapton; Preact signals' code (downloaded, not read).
- Castelo-Branco, Caetano, Leitao 2022; Janssen's visual dataflow papers; Feist's A-BIM paper (scan
  without text) and thesis.
- CityEngine's own help on local edits: the "latest" help address returned 404; the paper by the same
  team was read instead. Whether the shipped product behaves as the paper says is S.
- The second half of F1 for Dynamo and all numbers in H1 remain to be measured here.

## 7. Search log

| When | Where | Query or address | What came back | Kept or set aside |
|---|---|---|---|---|
| 2026-11-14 | GitHub (git clone, shallow) | `aptmcl/Khepri.jl` | Meta package only, 4 lines of source | Kept as pointer to KhepriBase |
| 2026-11-14 | GitHub (git clone, shallow) | `aptmcl/KhepriBase.jl` | 27,398 lines of Julia, MIT | Kept; `src/Shapes.jl` read |
| 2026-11-14 | raw.githubusercontent.com | salsa book `reference/algorithm.md`, `durability.md`; `milomg/reactively` README and `core.ts`; `tc39/proposal-signals` README; `preactjs/signals` core; `janestreet/incremental` `incremental_intf.ml`; `hypar-io/Elements` README | All 200 | Kept, to be read |
| 2026-11-14 | raw.githubusercontent.com | `janestreet/incremental` README.md | 404 | Set aside; the interface file carries the documentation |

| 2026-11-15 | curl | wiki.freecad.org Topological_naming_problem (page and api.php) | Bot challenge page ("Making sure you're not a bot") | Host refused; used `FreeCAD/FreeCAD-documentation` Markdown copy instead |
| 2026-11-15 | raw.githubusercontent.com | realthunder/FreeCAD_assembly3 wiki, Topological-Naming-Algorithm.md | 200 | Kept; Overview and Algorithm read |
| 2026-11-15 | raw.githubusercontent.com | mcneel/rhino.inside-revit 1.x, guides/rir-grasshopper.md | 200 | Kept; "Element Tracking" read |
| 2026-11-15 | microsoft.com, ndmitchell.com | Build Systems a la Carte PDF | 403 and 404 | Set aside; JFP copy at cambridge.org returned 200 and was read |
| 2026-11-15 | raw.githubusercontent.com | guessed Dynamo paths for an element-binding document (4 guesses) and TraceUtils.cs | 404 | Set aside |
| 2026-11-15 | raw.githubusercontent.com | DynamoDS/DynamoRevit ElementBinder.cs, Wall.cs, LICENSE.txt | 200 | Kept; read |
| 2026-11-15 | Web search | Dynamo "element binding" trace Revit duplicates re-run | Blogs, AU class, McNeel forum threads, a fork's Known Issues | Pointers only; led to the primer page |
| 2026-11-15 | WebFetch | primer2.dynamobim.org developer primer, 13-dynamo-integration | Page returned, read through the fetch tool's extraction | Kept as P with the gap that the extraction, not the raw page, was read; agrees with the code |
| 2026-11-15 | Web search | Lipp Specht Lau Wonka Mueller "Local Editing of Procedural Models" pdf | diglib.eg.org (403 to script), academia.edu (403), KAUST | Found author's copy at peterwonka.net: 200, read |
| 2026-11-15 | curl | cg.tuwien.ac.at lipp2011a-draft.pdf | 200; it is "Interactive Modeling of City Layouts" (2011), not the paper sought | Set aside |
| 2026-11-15 | curl, WebFetch | doc.arcgis.com cityengine latest help-local-edits.htm | 404 | Set aside; search listed tutorial 20 and help-local-edits-overview pages, not read |
| 2026-11-15 | curl | papers.cumincad.org guessed ids for Feist 2016, Leitao 2012, Celani 2012, Janssen 2014 | 200 but other papers (wrong ids) | Set aside |
| 2026-11-15 | Web search | Leitao Santos Lopes "Programming Languages for Generative Design: A Comparative Study" | Author's page web.ist.utl.pt | Kept; PDF read; directory listing gave the group's other papers |
| 2026-11-15 | curl | web.ist.utl.pt ADA publications: 2011 Portable GD for CAD, 2016 A-BIM, 2016 Portable GD for BIM, 2017 Luna Moth, 2020 Visual Meets Textual | 200; A-BIM has no text layer | Four read in part; A-BIM set aside |
| 2026-11-15 | Web search | Castelo-Branco Caetano Leitao "Digital representation methods" | Journal record, open access | Not read; U |
| 2026-11-15 | Web search | Celani Vaz 2012; Janssen visual dataflow | Cadernos Proarq 18 copy of Celani and Vaz; nothing for Janssen | Celani read; an opus.lib.uts.edu.au address returned HTML, set aside |
| 2026-11-15 | curl | developer.rhino3d.com Grasshopper API, GH_ActiveObject.ExpireSolution | 200 | Kept; read |
| 2026-11-15 | curl | developer.blender.org docs/features/nodes/fields and proposals/caching | 200 | Kept; read |
| 2026-11-15 | curl, WebFetch | sidefx.com docs houdini network/cooking.html, nodes/cooking.html | 404 | Set aside |
| 2026-11-15 | Counter-evidence | searched the sources above for limits: Lipp 2019 "Limitations and Failure Cases"; FreeCAD wiki wording; Luna Moth evaluation; Leitao 2012 threats | Found, recorded in part 4 | Kept |

## 8. References

All read on 2026-11-15 unless a date is given.

1. KhepriBase.jl. https://github.com/aptmcl/KhepriBase.jl , commit a303d45c8b523e9cf452a70c81b4860a4e087d26,
   MIT. `src/Shapes.jl` lines 60-160, 370-475, 484-535. Read 2026-11-14. P.
2. Khepri.jl. https://github.com/aptmcl/Khepri.jl , commit f76abd96c2eca6ff2f3a1d619203777ddc02575f, MIT.
   `src/Khepri.jl`, `Project.toml`, `README.md`. Read 2026-11-14. P.
3. Mokhov, Mitchell, Peyton Jones, "Build Systems a la Carte: Theory and Practice", J. Functional
   Programming 30 (2020). cambridge.org open-access PDF (S0956796820000088). Sections 2.1-2.4, Table 1,
   4.1-4.3, 5.1 (by text search and reading the passages). P.
4. Jane Street Incremental, `src/incremental_intf.ml`.
   https://raw.githubusercontent.com/janestreet/incremental/master/src/incremental_intf.ml . The header
   documentation, lines 50-310 (stabilization, heights, cutoff, cycles). P.
5. Salsa book, "The red-green algorithm" and "Durability".
   https://raw.githubusercontent.com/salsa-rs/salsa/master/book/src/reference/algorithm.md . Whole. P.
6. Reactively README. https://raw.githubusercontent.com/milomg/reactively/main/README.md . "Execution
   model" section. P.
7. TC39 Signals proposal README. https://raw.githubusercontent.com/tc39/proposal-signals/main/README.md .
   Lines 156-177, 317, 488-560, 650-668, 748-770. P.
8. Grasshopper API, `GH_ActiveObject.ExpireSolution`.
   https://developer.rhino3d.com/api/grasshopper/html/M_Grasshopper_Kernel_GH_ActiveObject_ExpireSolution.htm
   . Whole page. P.
9. Rhino.Inside.Revit guide. https://raw.githubusercontent.com/mcneel/rhino.inside-revit/1.x/docs/pages/_en/1.0/guides/rir-grasshopper.md
   . "Element Tracking". P.
10. Dynamo developer primer, "Dynamo Integration", Element Binding and Trace.
    https://primer2.dynamobim.org/1_developer_primer_intro/3_developing_for_dynamo/13-dynamo-integration .
    Read through a fetch tool's extraction with quotes. P with that gap.
11. DynamoRevit, Apache-2.0, master. `src/Libraries/RevitServices/Persistence/ElementBinder.cs` lines
    17-130, 229-420; `src/Libraries/RevitNodes/Elements/Wall.cs` lines 41-108.
    https://github.com/DynamoDS/DynamoRevit . P.
12. Lipp, Specht, Lau, Wonka, Mueller, "Local Editing of Procedural Models", Computer Graphics Forum 38(2)
    2019, 13-25. Author's copy
    https://peterwonka.net/Publications/pdfs/2019.EG.Lipp.LocalEditingProceduralModels.pdf . Abstract,
    sections 3, 4.1-4.3, 5, Table 2, "Limitations and Failure Cases". P.
13. FreeCAD documentation, "Topological naming problem".
    https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Topological_naming_problem.md
    . Introduction and Example. P.
14. realthunder, "Topological Naming Algorithm".
    https://raw.githubusercontent.com/wiki/realthunder/FreeCAD_assembly3/Topological-Naming-Algorithm.md .
    Overview and Algorithm (first 60 lines). P.
15. Leitao, Santos, Lopes, "Programming Languages for Generative Design: A Comparative Study", IJAC 10(1)
    2012. https://web.ist.utl.pt/antonio.menezes.leitao/ADA/documents/publications_docs/2012_ProgrammingLanguagesForGenerativeDesign_AComparativeStudy.pdf
    . Sections 3 (experiment, Tables 1-3), 4, 5. P.
16. Celani and Vaz, "CAD scripting and visual parametric modeling environments" (Cadernos Proarq 18; the
    English version of the IJAC 2012 paper). https://cadernos.proarq.fau.ufrj.br/public/docs/Proarq18_CadScripting_CelaniVaz.pdf
    . The course description, results and conclusions. P (a copy in another journal: the gap).
17. Castelo-Branco and Leitao, "Visual Meets Textual", 2020. Same directory,
    `2020_VisualMeetsTextual.pdf`. Sections 4.1, 4.2, 5-7. P.
18. Lopes and Leitao, "Portable Generative Design for CAD Applications", ACADIA 2011. Same directory.
    Abstract and architecture section. P.
19. "Portable Generative Design for Building Information Modelling", 2016. Same directory. The passages
    on families and on A-BIM. P.
20. "Luna Moth: A Web-based Programming Environment for Generative Design", eCAADe 2017. Same directory.
    Introduction, features, evaluation passages. P.
21. Blender developer documentation, "Fields" and "Analysis: Caching".
    https://developer.blender.org/docs/features/nodes/fields/ and .../nodes/proposals/caching/ . Whole
    bodies. P.
22. Hypar Elements README. https://raw.githubusercontent.com/hypar-io/Elements/master/README.md . Read
    2026-11-14 in part. P for the one sentence used.
23. `grammars-and-layout.md` in this folder, for Lipp, Wonka, Wimmer 2008. Not re-read here.
