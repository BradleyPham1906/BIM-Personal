# Algorithmic design: execution models and the identity of generated objects

One of five parallel research notes for `00-question.md`. Side: how algorithmic-design tools evaluate
(H1), how generated elements keep their identity across re-runs (H3), and text against node graphs (H5).
Started 2026-11-14, continued 2026-11-15. Levels: P = read in the source itself, S = dependable secondary,
U = unverified. STATUS: in progress; parts are filled as each source is read.

## 1. Summary of findings

(In progress; see part 2. Filled at the end.)

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

Confidence: high for what the code does (read directly); the conclusion "no identity across runs" is
from the absence of any such mechanism in `Shapes.jl`, `Backend.jl` search to be completed.

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

### 2.4 Identity of generated objects (saved 2026-11-15)

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
  rule or the initial shape changes. Their Table 2: exact locators transferred 0% of edits in three of
  four model changes; meta-locators 100% in those four. Stated failures: an edit that addresses a place
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

(In progress.)

## 4. Counter-evidence found

(In progress.)

## 5. What a plain-ES5 app should take from this

(In progress.)

## 6. Still open (U)

(In progress.)

## 7. Search log

| When | Where | Query or address | What came back | Kept or set aside |
|---|---|---|---|---|
| 2026-11-14 | GitHub (git clone, shallow) | `aptmcl/Khepri.jl` | Meta package only, 4 lines of source | Kept as pointer to KhepriBase |
| 2026-11-14 | GitHub (git clone, shallow) | `aptmcl/KhepriBase.jl` | 27,398 lines of Julia, MIT | Kept; `src/Shapes.jl` read |
| 2026-11-14 | raw.githubusercontent.com | salsa book `reference/algorithm.md`, `durability.md`; `milomg/reactively` README and `core.ts`; `tc39/proposal-signals` README; `preactjs/signals` core; `janestreet/incremental` `incremental_intf.ml`; `hypar-io/Elements` README | All 200 | Kept, to be read |
| 2026-11-14 | raw.githubusercontent.com | `janestreet/incremental` README.md | 404 | Set aside; the interface file carries the documentation |

## 8. References

(In progress; each entry: what it is, URL, what was read, date, level.)

- KhepriBase.jl, the core of Khepri. https://github.com/aptmcl/KhepriBase.jl , commit a303d45c. Read
  `src/Shapes.jl` lines 60 to 160, 370 to 475, 484 to 535. 2026-11-14. P.
- Khepri.jl. https://github.com/aptmcl/Khepri.jl , commit f76abd96. Read `src/Khepri.jl`, `Project.toml`,
  `README.md`. 2026-11-14. P.
