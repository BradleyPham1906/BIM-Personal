# Rule systems that generate buildings: shape grammars, split grammars, plan layout

One of five parallel notes for `docs/research/research-algorithmic-design.md`. Question and hypotheses:
`00-question.md` (this note bears on H2 and part of H3). Read 2026-11-14 and 2026-11-15.

Evidence levels: P = the source itself was read (paper, the tool's own documentation, code as text);
S = a dependable secondary work citing it; U = seen only in a search summary or one unverified copy.
Nothing was built or run; no measurement was made here (H2's timing and line count are still to be measured
by whoever writes the prototype). Section 7 lists every source asked for that could not be reached.

## 1. Summary of findings

| # | Finding | Level | Confidence |
|---|---|---|---|
| F1 | A split grammar is a restricted set grammar: shapes are whole labelled boxes replaced as units, matching is by symbol, and no subshape search is needed. That restriction is what makes automatic derivation possible (Wonka 2003 sec. 4; Müller 2006 sec. 1.1). | P | high: two primary papers say it in their own definitions |
| F2 | CGA shape (2006): a shape = symbol + scope (position P, axes X Y Z, size S) + attributes; the operations are T, R, S, push/pop, instance, Subdiv, Repeat, Comp, plus occlusion and snap queries; rules have a guard, a probability and a priority. | P | high |
| F3 | 2006 split arithmetic: relative size `r_i * (scope - sum(abs)) / sum(r)`; repeat count `ceil(scope / size)` with each piece resized to fill. | P | high |
| F4 | Esri's current CGA: no prefix = absolute, `'` = fraction of the scope, `~` = floating (shares the remainder in proportion), `*` = repeat. The 2006 "r" is today's `~`, not today's `'`. Splits may leave a gap or cut the last piece. | P | high |
| F5 | Esri's reference does not publish the repeat's rounding rule ("best number of repetitions and least stretching"). Open implementations differ from the 2006 paper: shapeml uses `max(round(total/size), 1)`, not `ceil`. | P | high for the facts; the Esri rule itself is unknown |
| F6 | The split arithmetic itself is tiny: cgajs does it in one 46-line function; shapeml's general pattern split (fixed and stretch parts, one repeated group) is about 140 lines of C++. Neither needs a geometry kernel for the arithmetic; both cut real meshes with a plane (their own mesh code). | P | high for the sizes; medium that this carries over to ES5 line counts |
| F7 | Identity: Lipp, Wonka, Wimmer 2008 define the "exact instance locator" (the path from the axiom: each shape, command and child edge number) and the "semantic instance locator" (tag = edge number, e.g. floor = 2, column = 3), store edits outside the tree, and re-attach them on every regeneration. They classify stored locators after a change as valid, structurally invalid (index beyond the new count) or semantically invalid, and show the list to the user. | P | high |
| F8 | CGA shape's stated limits (CGA++ 2015): no coordination across branches, no operation on several shapes (no booleans), almost no context, no trial derivations. Müller 2006 itself says splits suit facades but not much of mass modelling, and that architectural design use "might require significant changes". | P | high |
| F9 | A general shape grammar interpreter must find every transformed copy of a rule's left side inside the current drawing, including shapes that emerge from overlapping lines. The cost is at least quadratic to cubic in targets without parameters and can be non-polynomial with them (Wortmann and Stouffs 2018, abstract only). | S (abstract) | medium: abstract read, body paywalled; consistent with Müller 2006's and Wonka 2003's own remarks (P) |
| F10 | Floor-plan methods fall into bottom-up (aggregate rooms; often stochastic, may find no solution), top-down (subdivide a fixed boundary; small predefined design space) and referential (learned; trained on tens of thousands of plans) (Weber, Mueller, Reinhart 2022, 49 methods: 14 / 27 / 8). | P | high |
| F11 | The squarified treemap (Bruls 2000) is deterministic, about 30 lines, and fills a rectangle with given areas at low aspect ratios, but it guarantees neither optimality nor any adjacency, loses the order of siblings, and assumes a rectangle. Used for plans it needs a later corridor step that wastes area (Mirahmadi and Shami 2012 on Marson and Musse 2010). | P for Bruls and Mirahmadi; S for Marson and Musse | high |
| F12 | Merrell 2010 (Bayesian network + Metropolis optimisation) takes seconds to 7 minutes per house and fails in about 1 of 20 two-storey and 1 of 5 three-storey runs; it needs a trained network. | P | high |
| F13 | Graph-based plans (GPLAN) guarantee the adjacencies but only for a connected, planar, properly triangulated adjacency graph with no separating triangle and an outer face of four or more, and give a rectangular boundary; dimensions then need an optimisation step. | P | high for the conditions; medium on effort to port (Python, not read as code) |
| F14 | Learned methods (Graph2Plan, on RPLAN's 80K plans) need a trained network and so fall outside a one-file offline ES5 build. | P (abstract and figure 1 only) | high |

## 2. Findings by topic

### 2.1 Shape grammars as defined, and why building generators do not use them

- Wonka et al. 2003, section 4 (P). A grammar is defined over an algebra of objects with addition,
  subtraction, a set of transformations F and a match relation: a rule `a -> b` applies to `u` when some
  transformation f and parameter assignment g give `f(g(a)) <= u`, and produces `(u - f(g(a))) + f(g(b))`.
  A *set grammar* is the special case where objects are sets of whole elements, + and - are union and
  difference, and matching is the subset relation. A *split grammar* is a set grammar over basic shapes with
  two rule types only: a split (a basic shape decomposed into shapes that fill it) and a conversion (one
  shape replaced by another, which need not fill the same volume). The authors say the novelty is exactly
  these restrictions: strong enough for buildings, simple enough for "controlled and automatic derivation".
- Müller et al. 2006, section 1.1 (P). Stiny's original grammars work on arrangements of labelled lines and
  points; their derivation "is intrinsically complex and usually done manually, or by computer, with a human
  deciding on the rules to apply"; set grammars make them "more amenable to computer implementation". The
  paper cites the architectural grammars (Stiny and Mitchell 1978 Palladian; Koning and Eizenberg 1981
  Prairie; Duarte 2002 Malagueira; Downing and Flemming 1981; Flemming 1987) as analysis and design work,
  not as automatic generators.
- Wortmann and Stouffs 2018, "Algorithmic complexity of shape grammar implementation", abstract (S). The
  number of candidate matches is "quadratic or cubic" without parameters and "can be non-polynomial" with
  them; these are lower bounds whatever the data structure.
- Lipp et al. 2008, related work (P): earlier computer implementations of true shape grammars (Chase 1989;
  Piazzalunga and Fitzhorn 1998) produced ground plans, not detailed models.
- What an interpreter of Stiny's grammars needs, as far as the reachable sources say: a maximal-line
  representation so equal drawings compare equal, subshape detection under the allowed transformations
  (the match above), and with it emergence (matching shapes nobody put there as units). Parametric rules
  add the search over g. Graph-based interpreters (Grasl and Economou 2013) are one answer. (S/U: this
  paragraph rests on the abstracts and citing papers; Gips 1999, Stiny 1980, Krishnamurti and Grasl were
  not reachable, see section 7.)

Conclusion for the app: emergence is not needed to generate facades, massing or plans from rules; every
practical generator read here gives it up on purpose. Confidence high (P, two definitions and one statement
of motive).

### 2.2 Split grammars and CGA shape

**Müller, Wonka, Haegler, Ulmer, Van Gool 2006** (P; sections 1.1, 2, 3, rule listings of 5 and 6, 7, 8, 9).

- Shape = symbol, geometry, numeric attributes. Scope = position P, three orthogonal axes X, Y, Z, size S:
  an oriented box.
- Derivation: select an active shape, choose a rule with its symbol on the left, compute successors, mark
  the shape *inactive* (kept, not deleted, so the hierarchy can be queried), add the successors. Rules carry
  a priority by level of detail, giving a modified breadth-first order (mass, facade, detail).
- Notation: `id: predecessor : cond ~> successor : prob`.
- Scope rules: `T(tx,ty,tz)` adds to P; `Rx/Ry/Rz(angle)`; `S(sx,sy,sz)` sets the size; `[` `]` push and
  pop the scope; `I(objId)` instances a primitive or any mesh.
- Basic split: `Subdiv("Y",3.5,0.3,3,3,3){ floor | ledge | floor | floor | floor }`. Sizes are absolute by
  default; suffix `r` = relative, substituted as

      r_i * (Scope.sx - sum(abs_i)) / sum(r_i)

- Repeat: `Repeat("X",2){ B }`, with

      repetitions = ceil(Scope.sx / 2)      and the element's actual size adjusted to fit

- Component split: `Comp("faces"){A}`, `"edges"`, `"vertices"`, `"sidefaces"`, `Comp("edge",3)`. A face or
  edge is a scope with one or two zero sizes; `S` with a non-zero size turns a face back into a volume.
- Multi-axis splits ("XY", "XYZ") and nested splits.
- Occlusion: `Shape.occ("all" | "noparent" ...)` returns none / part / full; parents are excluded because a
  parent always occludes its split children; in practice approximated (scope against scope, an octree).
- Snap lines: `Snap("XZ")` inserts a snap shape; axis "XS" snaps. In a repeat, snap lines cut the scope into
  parts and the repeat runs in each part (every size changes); in a Subdiv only the nearest split line moves.
- Stochastic: alternative successors with probabilities, and `rand(a,b)` in sizes.
- Cost: a 50,000-polygon model in about one second (C++, 2006).

**Wonka, Wimmer, Sillion, Ribarsky 2003** (P; abstract, sections 1, 3, 4). Split grammar as in 2.1, plus an
attribute-matching system that picks among candidate rules by comparing attributes on the shape and on the
rules, and a separate *control grammar* that hands attributes out spatially (first floor differs, corners
differ). Attributes are copied from a shape to its children. No size arithmetic of the 2006 kind.

**Esri CityEngine CGA reference** (P; pages split, comp, setback, offset, extrude, split attribute, seedian).

- `split(axis) { size : ops | ... }`, optionally `*`; `adjust` (default; child scopes shrink to the cut
  geometry's bounding box) or `noAdjust` (children fill the parent scope with no gaps).
- Sizes: no prefix = absolute; `'` = `size * current scope size`; `~` = floating: "the remaining spaces
  between the split parts with absolute dimensions are automatically adapted", several floating parts
  "weighed proportionally". `*`: the block repeats "as often as it fully fits"; count and floating sizes go
  to "the best solution (best number of repetitions and least stretching)". No formula is given.
- Worked examples, scope sx = 10 (test vectors for a prototype):

  | Rule | Result |
  |---|---|
  | `{ '0.5 | '0.1 | '0.2 }` | 5, 1, 2, then a gap of 2 |
  | `{ ~0.5 | ~0.1 | ~0.2 }` | scope filled, ratios kept (6.25, 1.25, 2.5 by arithmetic) |
  | `{ 3.3 | ~3 | 5 }` | 3.3, 1.7, 5 |
  | `{ '0.5 | '0.6 | 3 }` | 5; second cut to 5; third never created |
  | `{ 2 | 1 }*` | the pair 3 times, then half an X cut off in the last unit |
  | `{ ~2 | ~1 }*` | nothing cut; sizes adjusted, ratio kept |
  | `{ 1 | { ~1 | 0.2 | ~1 }* | 1 }` | Y pieces come out 0.9 (4 repeats: (8 - 4*0.2)/8) |
  | `{ { 1 | ~3 }* | 1 }` | rhythm A B A B A |

- `split.index` (zero-based) and `split.total` are set on each child; in a repeat they count across all
  repetitions. A rule can test `split.index == 0` or `== split.total-1` (first and last floor).
- `NIL` leaves a hole; the cut closes hollow meshes.
- `comp(f|e|fe|v|fv|g|m|h) { selector operator ops }`: selectors front/back/left/right/top/bottom/side
  (by the face normal's quadrant in scope, object or world axes), vertical/horizontal/aslant/nutant (by
  angle bands: vertical within 11.25 degrees, horizontal beyond 78.75), border/inside, eave/hip/valley/
  ridge for roof edges, street.front etc., `all`, an index, a boolean expression, `isTagged(...)`.
  Operators: `:` one shape per component, `=` all in one shape, `=:` one per connected set.
- `setback(distance | distances[]) { selector : ops | remainder : ops }`: moves only the selected edges
  inward; `remainder` is the rest of the polygon; results carry tags `setback.front/back/side/remainder`.
- `offset(distance, all|inside|border)`: inner (negative) or outer (positive) offset polygon plus the
  border faces; for a positive offset the border faces overlap and are oriented negative.
- `extrude(distance)` / `extrude(world.up | world.up.flatTop | face.normal | vertex.normal, distance)`;
  the scope's y axis becomes the extrusion direction; result faces are tagged `extrude.bottom`,
  `extrude.side.outer`, `extrude.side.inner`, `extrude.top`; a negative distance gives a negative scope.sy.
- `seedian`: the random seed, readable and settable, so stochastic rules are repeatable.

**CGA++, Schwarz and Müller 2015** (P; abstract, section 1, headings of 3 and 4). Lists what CGA shape could
not do: L1 decisions cannot be coordinated across shapes once their lineages diverge; L2 no operation takes
several shapes (no boolean, no assembling); L3 context is not available apart from ad-hoc occlusion
queries; L4 no trial derivations or auxiliary constructions. CGA++ answers with shapes as first-class values
(operations take shapes as arguments) and *events* that pause several branches and let a handler decide for
all of them.

### 2.3 Open implementations (licence first; read as text, never built or run)

| Project | Licence | Commit read | Core size | Split sizes | Identity kept | Geometry needs |
|---|---|---|---|---|---|---|
| shapeml (S. Lienhard), C++ | GPL-3.0: ideas only, no code may be copied into an Apache-2.0 app | `5875a85` | `interpreter_shape_operations.cc` 3,125 lines; `shape.cc` 652; whole tree about 29,000 including viewer | see below | each Shape has `name_`, `parent_`, `children_`, `index_` (set to the child's position in a split or comp); no stored id | its own half-edge mesh with plane split (1,692 lines), straight skeleton for roofs (632), octree for occlusion; Eigen |
| cgajs (gromgull), JavaScript | Apache-2.0 (LICENSE.txt; package.json says "BSD": the two disagree) | `48cb20a` | `cgaprocessor.js` 872 lines; generated PEG parser 2,506; `polyutils.js` 267 | `_compute_splits`, 46 lines | not examined beyond the split | three.js geometry; `polyutils.split_geometry`; a `three-csg.js` (551 lines) is in `src/` (whether split uses it was not checked) |
| Building Tools (ranjian0), Blender Python | MIT | LICENSE only | not read | not read | not read | Blender's bmesh |
| pvallet/CGA_interpreter, C++ | not stated in README | README only | not read | | | flex, bison; Linux only |

shapeml's arithmetic (P, `src/shapeml/interpreter_shape_operations.cc` lines 2488-2552 and 2710-2846):

- Simple repeat: `num_reps = max(round(total / size), 1)`; `final = total / num_reps`. Never zero pieces;
  a piece may be up to 1.5 times or down to 0.67 times the nominal size.
- Pattern split with fixed and stretch parts, outer parts and one repeated inner group:

      outer = outer_fixed + outer_stretch;  inner = inner_fixed + inner_stretch
      ideal = round((total - outer) / inner)
      max   = floor((total - outer_fixed) / inner_fixed)      (when inner_fixed > 0)
      reps  = min(ideal, max)
      special case: ideal == 0, max > 0, no outer stretch, some inner stretch, and the inner fixed part
                    fits  ->  reps = 1
      scale = (total - outer_fixed - reps * inner_fixed) / (outer_stretch + reps * inner_stretch)
      every stretch size *= scale

  Then sizes are emitted in order; outer parts stop being added once the running sum would pass the total
  (so trailing fixed parts are dropped when there is no room), and a plane cut is skipped for the last
  piece. Empty meshes after a cut produce no child. Tolerance: one `EPSILON`.
- The child's `index` is its position in the final size list, so it counts across repetitions, as Esri's
  `split.index` does.

cgajs's arithmetic (P, `src/cgaprocessor.js` lines 226-271): walk the size list, wrapping round when
`repeat` is set, adding sizes until the next one would pass the scope; a floating size that overshoots is
still added and ends the repeat; then every floating size is shrunk by the same fraction so the total
equals the scope. So its repeat count is "as many whole items as fit, plus one more if it is floating",
closer to `ceil` for floating patterns and to `floor` for absolute ones.

Three sources, three repeat rules (`ceil`; `round` clamped to 1; fill-then-shrink). The choice is a design
decision, not a standard. P, high.

### 2.4 Identity of generated shapes (H3)

**Lipp, Wonka, Wimmer 2008, "Interactive visual editing of grammars for procedural architecture"**
(P; sections 1, 3, 3.1 and the locator-transformation part).

- The persistence problem in their words: after a direct edit to the generated hierarchy, a regeneration
  (for example a new building height) produces the unmodified version and the edit is lost.
- Exact instance locator: number every outgoing edge of each shape or command from left to right starting
  at 1; walk the path from the axiom to the shape and write down each shape, command and edge number.
  Example: `{a, 1, Sy, 2, b, 1, Sx, 3}`. Edge numbers alone would do; shapes are included "to be able to
  check whether the locator is valid after a hierarchy change".
- Semantic instance locator: tags (floor, column, facade) are attached to split or repeat commands; the
  locator keeps only `tag = edge number` along the path, e.g. `(F = 2, C = 3)`. Leaving a tag out selects a
  whole column or floor. Tags can be assigned automatically by thresholds (a Y split taller than several
  floors is "floor", and so on).
- Edits are stored outside the tree as (locator, variable assignment). On regeneration the tree is deleted
  and rebuilt from the axiom; each new shape's locator is computed and compared with the stored ones; on a
  match the stored assignment is attached. Later assignments override earlier ones.
- After a change, each stored locator is *valid* (a path exists), *structurally invalid* (a prefix matches
  but the next edge number is larger than the shape now has: the count shrank) or *semantically invalid*
  (does not fit at all). Structurally invalid ones are kept untouched because they "often become valid
  again" when the size comes back. Semantically invalid ones are listed for the user, colour coded, with a
  command to transform them by spatial ordering values; the authors note artists "prefer direct control
  over heuristics that run automatically".
- Semantic locators are "normally quite robust" to parameter and floor-plan changes; they break when the
  rules themselves are edited or a higher-level production choice changes.

Also bearing on identity: Esri's `split.index` / `split.total` (P) and the automatic component tags on
extrude and setback results (P) are the vendor's stable names for generated parts; shapeml keeps `index`
and the parent pointer (P). Lipp et al. 2019 "Local Editing of Procedural Models" continues this line
(bottom-up edit locations taken from model attributes, transferable between models): abstract only via a
search summary (U).

### 2.5 Floor-plan generation

**Survey: Weber, Mueller, Reinhart 2022** (P; eScholarship copy; sections 4.1-4.4, discussion).
49 methods with a geometric output: 14 bottom-up, 27 top-down, 8 referential.

- Bottom-up (aggregation, growth, agents, GA): large search spaces needing heuristics; "stochastic methods
  do not necessarily find a solution"; hard to embed hierarchy such as levels of circulation or structure.
- Top-down (subdivision, fitting, packing; MILP, squarified treemaps, geometric): "work best when used with
  fixed boundary constraints", which suits urban sites where codes fix the massing, and can test whether a
  massing holds a programme; but cover "a small, previously defined design space".
- Referential (learned): image-based ones are tied to a 256 x 256 raster, applied only to single-storey
  apartments, with fuzzy output needing heavy post-processing.
- The survey's own suggestion: hybrids, top-down for the envelope and bottom-up or referential to fill.

| Family | Source read | Deterministic | Size / needs | Guarantees | Limits |
|---|---|---|---|---|---|
| Squarified treemap | Bruls, Huizing, van Wijk 2000 (P, sec. 3) | yes | about 30 lines; nothing | exact areas, fills the rectangle | no adjacency control; not optimal ("counterexamples can be set up"); sibling order lost; rectangle only |
| Treemap plan + corridor | Marson and Musse 2010 (S, through Mirahmadi and Shami 2012 and Weber 2022); Mirahmadi and Shami 2012 (P, sec. I-III) | yes apart from random areas | small | areas; connectivity only after a corridor step | rectangular outline assumed; corridor step "wastes some space"; narrow rooms possible |
| Stochastic optimisation | Merrell, Schkufza, Koltun 2010 (P, sec. 5, 7, 8) | no (Metropolis) | Bayesian network trained on real programmes; cost function | none; rectilinear rooms | seconds to 7 minutes; fails 1 in 20 (two storeys), 1 in 5 (three); no non-rectilinear walls |
| Rectangular dual / graph | Shekhawat et al. GPLAN, arXiv 2008.01803 (P, abstract, sec. 1-3) | yes for the topology | graph algorithms (regular edge labelling) then optimisation for dimensions; Python | every requested adjacency | graph must be connected, planar, triangulated, no separating triangle, outer face >= 4; rectangular boundary for the graph input; errors otherwise |
| Evolutionary | Rodrigues, Gaspar, Gomes 2013 | no | not read | | (U) |
| MIQP | Wu et al. 2018 | yes given a solver | a mixed-integer QP solver | optimal for its model | not read (U); needs a solver library |
| Learned | Graph2Plan (P, abstract: trained on RPLAN, 80K plans); House-GAN (not read) | no | trained network, GPU-class | none | outside a one-file offline build |

Squarify, as published (Bruls 2000, section 3.2): areas sorted decreasing; lay rows along the shorter side
of the remaining rectangle; add the next area to the current row while that does not worsen the row's worst
aspect ratio, else fix the row and recurse on the rest. For a row R with sum s, shortest side w, largest
r+ and smallest r-:

    worst(R, w) = max( w^2 * r+ / s^2 ,  s^2 / (w^2 * r-) )

## 3. What bears on H2 and H3

**H2 (a CGA-style split grammar in under 400 lines of ES5, no kernel, 10 x 8 facade under 50 ms).**
Outcome from the literature: *supported in principle, not yet measured*.

- For: the arithmetic is two formulas (F3) or one 46-line function (cgajs); a scope is 15 numbers; Müller
  2006 says explicitly that no "complex and error-prone geometric computations" such as booleans are
  executed; a 10 x 8 facade is of the order of a few hundred shapes against 50,000 polygons per second in
  2006.
- Against, or bounding it: both implementations read cut *meshes* with a plane, which is the larger part
  of their code (shapeml's half-edge mesh is 1,692 lines). The 400 lines hold only if a shape's geometry
  is its scope (a box or a rectangle) and terminals are handed to the app's existing elements. A component
  split on a prism needs only the footprint polygon's edges; on an arbitrary mesh it needs face data. A
  text parser is extra (cgajs's generated parser is 2,506 lines): rules given as data (ES5 objects or
  arrays) avoid it.
- So H2 should be restated for the measurement: "split, repeat, component split of a box or prism, scope
  transforms, guards and seeded choice, rules as data" in under 400 lines; plane-cutting of arbitrary
  meshes, occlusion, snapping and roofs are outside it.

**H3 (deterministic identity from rule path and index; survives count-preserving changes; a count change is
reported).** Outcome: *supported by a primary source that solved the same problem*.

- Lipp 2008's exact locator is the hypothesis's "rule path and index"; its three-way classification is the
  "must be reported, not hidden" part, including the useful refinement that an index beyond the new count
  is kept dormant, not deleted.
- Added by the source, beyond H3: a second, semantic key (floor = 2, column = 3) is more robust than the
  raw path, because inserting an intermediate rule changes every path below it but not the tags.
- Not covered: the 2006 `ceil` repeat and snapping both renumber or resize every piece when a size crosses
  a threshold, so "keeps the counts" is a narrower condition than it sounds (section 6).

## 4. Counter-evidence found

- Against "split grammars are enough": Müller 2006 section 8 (splits unsuitable "for many forms of mass
  modeling"; arbitrary footprints give implausible results; architectural design use unexplored); CGA++
  2015 L1-L4. Coordinated decisions (exactly one door per building; align windows across masses) cannot be
  expressed by a pure top-down split.
- Against "the repeat rule is standard": three different rounding rules in three sources (2.3).
- Against treemap plans: Bruls's own limits; Mirahmadi and Shami's criticism of the corridor step; Weber's
  remark that top-down methods cover only a small predefined space.
- Against optimisation-based plans in a browser: Merrell's run times and failure rates.
- Against graph-based plans: GPLAN rejects any graph that is not planar and properly triangulated.
- Against automatic re-mapping of identity: Lipp 2008 reports that artists prefer to decide themselves.
- Not found: any report that split-grammar derivation is too slow for a single building; any published
  ES5-size measurement (the nearest is cgajs's line counts).

## 5. What a plain-ES5 app should take from this

**Operations of a first split grammar** (each with its source):

1. Scope: origin, three axes, three sizes; a face is a scope with one zero size (Müller 2006 sec. 2).
2. `split(axis, parts)` with three size kinds: absolute, relative to the scope (`'`), floating (`~`)
   (Esri split). Resolve as: fixed = absolutes + relatives * scope; floating share
   `(scope - fixed) * w_i / sum(w)` (Müller 2006's formula; Esri's examples agree: 3.3, 1.7, 5).
3. `repeat`: a group repeated inside a split, so a rhythm with end pieces works (Esri examples; shapeml's
   outer/inner model). Pick one rounding rule and document it; shapeml's `round` clamped to at least 1,
   with the cap `floor((scope - outerFixed)/innerFixed)`, is the most complete one read.
4. `comp`: faces of a box or prism by side (front, back, left, right, top, bottom, side), and edges
   (Müller 2006; Esri comp selectors and the three operators).
5. Scope transforms `t`, `r`, `s`, push and pop (Müller 2006).
6. `extrude(h)` face to volume and `setback(d, edges)` / `offset(d)` on a footprint, with named results
   (Esri: `extrude.top`, `setback.remainder`...). These reuse the app's polygon offset, not a kernel.
7. Guards and attributes on rules, `split.index` and `split.total` on children (Esri), a seed for any
   random choice (Esri `seedian`).
8. Terminals that create the app's ordinary elements (wall panel, opening, slab), not meshes.
9. Leave out of the first slice: plane cuts of arbitrary meshes, occlusion queries, snap lines, roofs,
   events. Each has a named source to return to (Müller 2006 sec. 3; CGA++ sec. 3-4).

**Data of a shape:** symbol; scope; attributes (inherited from the parent, as in Wonka 2003); parent;
children; index and total in the parent's operation; the operation and rule that made it; exact locator
(path of rule names and indices) and semantic locator (tag = index for tagged splits); active/inactive
flag, the tree kept after derivation (Müller 2006) so edits and queries can address it.

**Identity:** store hand edits outside the tree, keyed by locator; re-attach on every derivation; classify
each stored key as valid, dormant (index beyond the count) or orphaned, and show the orphans (Lipp 2008).

**Plan layout to start with:** top-down subdivision of a given rectangle: the squarified treemap with a
room hierarchy (zones, then rooms), because it is deterministic, tiny and needs no solver (Bruls 2000;
Weber 2022 on top-down fitting a fixed envelope, which matches the app's zoning envelope). Present it as an
area-fit test and a first sketch, not as a designed plan: it gives no adjacency or circulation guarantee.
A double-loaded corridor bar expressed as a split rule (corridor strip, then repeat units either side) is
the complement for apartment and office floors and needs nothing beyond the split grammar itself (this
last point is this note's inference, not a finding from a source). Graph-based rectangular dualisation is
the candidate second step when adjacency must be guaranteed.

## 6. Edges

Worked from the formulas above (arithmetic done by hand here, not run):

| Case | 2006 paper | shapeml | Esri reference |
|---|---|---|---|
| Repeat size 4 in scope 10 | ceil(2.5) = 3 pieces of 3.33 | round(2.5) = 3 pieces of 3.33 | not stated |
| Repeat size 4 in scope 9 | ceil(2.25) = 3 of 3.0 | round(2.25) = 2 of 4.5 | not stated |
| Repeat size 4 in scope 1 | 1 piece of 1 | round(0.25) = 0, clamped to 1 | not stated |
| Scope 0 (degenerate face) | ceil(0) = 0 pieces | clamped to 1 piece of size 0 | not stated |
| Absolutes exceed the scope | relative sizes go negative by the formula | later fixed parts dropped once the sum would pass the total | piece cut at the scope end, later ones never created |
| Relative `'` sizes sum under 1 | (no such prefix) | | a gap is left at the end |
| Floating only, no absolutes | fills | fills | fills, ratios kept |
| No floating part and absolutes under the scope | gap | gap (assert allows it) | gap, or last piece cut in a repeat |
| Size crossing a rounding threshold | every piece is resized and one index appears or disappears at the end | same | same; `split.total` changes |

- A piece count change renumbers nothing before the end but shifts "last" (`index == total-1`), so an edit
  attached to the top floor by index stays on the old floor number: store "last" as a semantic key when the
  user means it.
- Snap lines make a repeat run per segment, so one moved snap line changes all sizes on that facade
  (Müller 2006 figure 9).
- Non-rectangular faces: a split works on the scope (the bounding box); Esri then shrinks each child scope
  to its cut geometry (`adjust`), so on a gable or an L-shaped face children are not all the same size and
  some may be empty (shapeml drops empty children, which leaves holes in the index sequence only if the
  index is assigned before the test; in shapeml the index is the position in the size list, so gaps in the
  numbering are possible).
- L-shaped footprint: comp into side faces gives six facades with their own scopes; reflex corners are
  where the 2006 paper needed occlusion queries to stop windows meeting a neighbouring volume.
- Setback larger than the face: Esri's pages read here do not say what is returned (open, section 7).
- Treemap: areas must be positive and sum to the rectangle; a very small room next to large ones gets a
  sliver; a non-rectangular boundary is outside the algorithm.

## 7. Still open (U) and why

- Stiny and Gips 1972; Gips 1999: `www.shapegrammar.org` does not resolve from here; the Boston College
  copy fails TLS (certificate name mismatch); web.archive.org is not reachable from this environment.
- Stiny 1980; Stiny and Mitchell 1978; Koning and Eizenberg 1981; Duarte 2005; Krishnamurti's papers;
  Grasl and Economou 2013: publisher pages (SAGE) returned 403; no open copy found in the time given.
  What this note says about them is S (via Müller 2006, Wonka 2003, Weber 2022) or U.
- Wortmann and Stouffs 2018: abstract only (Cambridge paywall).
- Lipp, Specht, Lau, Wonka, Müller 2019: diglib.eg.org returned 403 / reset; abstract via search only (U).
- Marson and Musse 2010: hindawi.com and onlinelibrary.wiley.com returned 403; known through two works
  that describe it (S).
- Rodrigues, Gaspar, Gomes 2013; Wu et al. 2018 (MIQP); House-GAN body: not read.
- Esri's exact repeat-count rule; behaviour of setback beyond the face; the CGA changelog (downloaded, not
  read); roof operations (roofGable page downloaded, not read); splitArea (downloaded, not read).
- OSM2World, bcga/blosm: licence files not found at the guessed paths; not read. Building Tools: licence
  only. cgajs: shape identity and whether split uses CSG not examined.
- H2 itself: not measured here.

## 8. Search log

| # | Date | Where | Query or URL | Result | Kept / set aside |
|---|---|---|---|---|---|
| 1 | 11-14 | peterwonka.net | Müller 2006 PDF | 200 | kept, P |
| 2 | 11-14 | peterwonka.net | Wonka 2003 PDF, two guessed names | 404 | found at TU Wien, row 17 |
| 3 | 11-14 | www.shapegrammar.org | Gips 1999; Stiny and Gips 1972 | DNS failure | open |
| 4 | 11-14 | win.tue.nl | Bruls 2000 PDF | 200 | kept, P |
| 5 | 11-14 | graphics.stanford.edu | Merrell 2010 | TLS chain refused | got from paulmerrell.org, row 9 |
| 6 | 11-14 | arxiv.org | 2008.01803, 2004.13204, 2003.06988 | 200 | GPLAN and Graph2Plan read in part |
| 7 | 11-14 | doc.arcgis.com | CGA split, comp, setback, offset, extrude, split attribute, seedian, roofGable, splitArea, changelog | 200 | first seven read |
| 8 | 11-14 | doc.arcgis.com | guessed pages (setbackPerEdge, innerRectangle, stochastic rule...) and help-local-edits | 404 | wrong names; set aside |
| 9 | 11-15 | paulmerrell.org | Merrell 2010 PDF | 200 | kept, P |
| 10 | 11-15 | github.com | clone stefalie/shapeml | ok, GPL-3.0 | read as text |
| 11 | 11-15 | web search | Lipp "Local Editing of Procedural Models" pdf | publisher records only | U; led to Lipp 2008 at TU Wien |
| 12 | 11-15 | web search | Schwarz Müller CGA++ pdf | records; author page found through pvallet README | kept, row 19 |
| 13 | 11-15 | web search | Weber Mueller Reinhart review | eScholarship copy | kept, P |
| 14 | 11-15 | web search | Gips 1999 pdf | only the dead shapegrammar.org link; Wortmann and Stouffs abstract | S |
| 15 | 11-15 | web search | javascript CGA split grammar github | gromgull/cgajs, pvallet/CGA_interpreter, a student project | cgajs cloned; others set aside (not JS, or no licence) |
| 16 | 11-15 | hindawi.com, wiley.com, sagepub.com, diglib.eg.org, cs.bc.edu, web.archive.org | Marson 2010; Grasl 2013; Lipp 2019; Gips 1999 | 403, 403, 403, reset, TLS mismatch, unreachable | refusals recorded |
| 17 | 11-15 | cg.tuwien.ac.at | Wonka 2003 paper; Lipp 2008 paper | 200 | kept, P |
| 18 | 11-15 | arxiv.org | 1211.5842 Mirahmadi and Shami | 200 | kept, P (stands in for Marson and Musse) |
| 19 | 11-15 | research.michael-schwarz.com | CGA++ author's version | 200 | kept, P |
| 20 | 11-15 | raw.githubusercontent.com | LICENSE / README of bcga, building_tools, OSM2World, CGA_interpreter | 404, MIT, 404, README | noted |
| 21 | 11-15 | cambridge.org | Wortmann and Stouffs 2018 | abstract only | S |
| 22 | 11-15 | en.wikipedia.org | Shape grammar | pointer only | U, not used |

Two arXiv ids guessed for Lipp 2019 and Weber 2022 returned 404 (a wasted query, recorded for honesty).

## 9. References

Upstream clones are under the session scratchpad `upstream/` (outside the repository).

1. Müller, Wonka, Haegler, Ulmer, Van Gool 2006. Procedural Modeling of Buildings. ACM TOG 25(3).
   https://peterwonka.net/Publications/pdfs/2006.SG.Mueller.ProceduralModelingOfBuildings.final.pdf
   Read: 1.1, 2, 3 (occlusion, snapping), rule listings in 5-6, 7, 8, 9. 2026-11-14. P.
2. Wonka, Wimmer, Sillion, Ribarsky 2003. Instant Architecture. ACM TOG 22(3).
   https://www.cg.tuwien.ac.at/research/publications/2003/Wonka-2003-Ins/Wonka-2003-Ins-Paper.pdf
   Read: abstract, 1, 3, 4 (definitions 4.2-4.6). 2026-11-15. P.
3. Esri. CityEngine CGA reference. https://doc.arcgis.com/en/cityengine/latest/cga/ pages `cga-split.htm`
   (whole), `cga-comp.htm` (syntax, parameters), `cga-setback.htm` (syntax, parameters, description,
   tags), `cga-offset.htm` (whole), `cga-extrude.htm` (whole), `cga-split-attribute.htm` (whole),
   `cga-seedian-attribute.htm` (whole). 2026-11-14 and 15. P.
4. Schwarz, Müller 2015. Advanced Procedural Modeling of Architecture (CGA++). ACM TOG 34(4). Author's
   version: http://research.michael-schwarz.com/publ/files/cgapp-sig15.pdf Read: abstract, section 1
   (L1-L4), opening of 3 and 4. 2026-11-15. P.
5. Lipp, Wonka, Wimmer 2008. Interactive Visual Editing of Grammars for Procedural Architecture. ACM TOG
   27(3). https://www.cg.tuwien.ac.at/research/publications/2008/LIPP-2008-IEV/LIPP-2008-IEV-paper.pdf
   Read: 1, 3, 3.1 (locators, persistence, transformations between hierarchies), related work.
   2026-11-15. P.
6. Lipp, Specht, Lau, Wonka, Müller 2019. Local Editing of Procedural Models. CGF 38(2).
   doi:10.1111/cgf.13615. Abstract through a search summary only. 2026-11-15. U.
7. shapeml, S. Lienhard. https://github.com/stefalie/shapeml commit
   5875a85474c7d4a70f37ba328783ac74b76aa019, GPL-3.0. Read: `LICENSE` head;
   `src/shapeml/interpreter_shape_operations.cc` lines 2488-2552, 2710-2846; `src/shapeml/shape.h` lines
   41-46, 186-216; file sizes. 2026-11-15. P.
8. cgajs, G. A. Grimnes. https://github.com/gromgull/cgajs commit
   48cb20acae8c527120cc2aa2533f097625f055fd, Apache-2.0 (LICENSE.txt). Read: `src/cgaprocessor.js` lines
   220-272 and a grep of the file; file sizes. 2026-11-15. P.
9. Building Tools, I. Karanja. https://github.com/ranjian0/building_tools MIT. LICENSE only. 2026-11-15. P
   for the licence.
10. pvallet/CGA_interpreter. https://github.com/pvallet/CGA_interpreter README only. 2026-11-15. P for the
    README; no licence seen.
11. Wortmann, Stouffs 2018. Algorithmic complexity of shape grammar implementation. AI EDAM 32(2).
    https://www.cambridge.org/core/journals/ai-edam/article/algorithmic-complexity-of-shape-grammar-implementation/9A4042D3D4FE95F60866DB1B6004CC96
    Abstract only. 2026-11-15. S.
12. Weber, Mueller, Reinhart 2022. Automated floorplan generation in architectural design: a review of
    methods and applications. Automation in Construction 140, 104385.
    https://escholarship.org/content/qt42d0s4v3/qt42d0s4v3.pdf Read: abstract, 4.1-4.4 text around tables
    2-4, discussion. 2026-11-15. P.
13. Bruls, Huizing, van Wijk 2000. Squarified Treemaps. https://www.win.tue.nl/~vanwijk/stm.pdf Read: 3,
    3.1, 3.2, conclusion. 2026-11-15. P.
14. Mirahmadi, Shami 2012. A Novel Algorithm for Real-time Procedural Generation of Building Floor Plans.
    https://arxiv.org/pdf/1211.5842 Read: I-III. 2026-11-15. P (and S for Marson and Musse 2010).
15. Marson, Musse 2010. Automatic Real-Time Generation of Floor Plans Based on Squarified Treemaps
    Algorithm. IJCGT 2010, 624817. doi:10.1155/2010/624817. Not reachable (403). S through 12 and 14.
16. Merrell, Schkufza, Koltun 2010. Computer-Generated Residential Building Layouts. ACM TOG 29(6).
    https://paulmerrell.org/wp-content/uploads/2021/06/floorplan-final.pdf Read: abstract, 5 (opening), 7
    (results, failure case), 8. 2026-11-15. P.
17. Shekhawat, Upasani, Bisht, Jain 2020. GPLAN: Computer-Generated Dimensioned Floorplans for given
    Adjacencies. https://arxiv.org/pdf/2008.01803 Read: abstract, 1-3 (definitions, input conditions).
    2026-11-15. P.
18. Hu et al. 2020. Graph2Plan. https://arxiv.org/pdf/2004.13204 Read: abstract, figure 1. 2026-11-15. P
    for those parts only.
19. Not read, named in the task: Stiny and Gips 1972; Stiny 1980; Stiny and Mitchell 1978; Koning and
    Eizenberg 1981; Duarte 2005; Gips 1999; Krishnamurti; Grasl and Economou 2013; Rodrigues, Gaspar,
    Gomes 2013; Wu et al. 2018; House-GAN (arXiv 2003.06988, downloaded, not read). U here.
