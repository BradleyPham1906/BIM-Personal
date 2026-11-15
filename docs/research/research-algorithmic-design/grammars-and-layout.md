# Rule systems that generate buildings: shape grammars, split grammars, plan layout

One of five parallel notes for `docs/research/research-algorithmic-design.md`. Question and hypotheses:
`00-question.md` (this note bears on H2 and part of H3). Started 2026-11-14, continued 2026-11-15.

Evidence levels: P = the source itself was read (paper, the tool's own documentation, code as text);
S = a dependable secondary work citing it; U = seen only in a search summary or one unverified copy.

STATUS: work in progress. Sections marked (pending) are not yet read; nothing in them may reach code.

## 1. Summary of findings

(Filled in as sources are read; see section 2 for evidence.)

1. CGA shape's split arithmetic as published (Müller et al. 2006, section 2) is two formulas. A relative
   size r_i becomes `r_i * (Scope.sx - sum(abs_i)) / sum(r_i)`; a repeat of size s makes
   `ceil(Scope.sx / s)` pieces and resizes each to fill the scope. P, high confidence (read in the paper).
2. Esri's current CGA changed the vocabulary: no prefix = absolute, `'` = relative to the current scope
   size (not to the remainder), `~` = floating (shares what the absolutes leave, in proportion), `*` =
   repeat "as many times as possible", with the count and floating sizes adjusted for "least stretching".
   The 2006 paper's "relative r" corresponds to today's floating `~`, not to today's `'`. P, high.
3. Esri's reference does not state the repeat count's rounding rule. P for the absence; the rule itself is
   open until an implementation is read (pending).

## 2. Findings by topic

### 2.2 Split grammars and CGA shape

**Müller, Wonka, Haegler, Ulmer, Van Gool 2006, "Procedural Modeling of Buildings"** (P, read 2026-11-14,
sections 1.1, 2, 3 in part, 7, 8, 9).

- A shape = a symbol, geometry and numeric attributes. The geometric attributes that matter are a position
  P, three orthogonal axes X, Y, Z and a size vector S: an oriented box, the *scope*.
- Derivation: pick an active shape, choose a rule whose left side is its symbol, compute successors, mark
  the shape *inactive* (not deleted) and add the successors. Shapes are kept so the hierarchy can be queried.
  Rules carry a priority by level of detail, giving a modified breadth-first order (mass, then facade,
  then detail).
- Rule notation: `id: predecessor : cond ~> successor : prob` (a guard and a probability).
- Scope rules: `T(tx,ty,tz)` adds to P; `Rx/Ry/Rz(angle)` rotate the axes; `S(sx,sy,sz)` sets the size;
  `[` and `]` push and pop the scope; `I(objId)` instances a primitive (cube, quad, cylinder, any mesh).
- Basic split: `Subdiv("Y",3.5,0.3,3,3,3){ floor | ledge | floor | floor | floor }`. Sizes are absolute
  unless suffixed `r`. Relative sizes are replaced by `r_i * (Scope.sx - sum(abs_i)) / sum(r_i)`.
- Repeat: `Repeat("X",2){ B }` tiles B; `repetitions = ceil(Scope.sx / 2)`, and the element's actual size
  is adjusted to fit.
- Component split: `Comp("faces"){A}`, `Comp("edges"){B}`, `Comp("vertices"){C}`, `Comp("sidefaces")`,
  `Comp("edge",3)`. Lower-dimensional shapes are scopes with one or more zero sizes; `S` with a non-zero
  size brings a face back to a volume (extrusion along its normal).
- Splits along several axes ("XY", "XYZ") and nested splits exist.
- Occlusion query: `Shape.occ("all" | "noparent" | ...)` returns none / part / full, tested against other
  shapes, with the parents excluded because a parent always occludes its split children. The paper says the
  exact test is replaced by approximations (scope against scope, an octree).
- Snap lines: `Snap("XZ")` inserts a snap shape; a split on axis "XS" snaps. For a repeat, the snap lines
  cut the scope into parts and the repeat runs in each part separately (all sizes change); for a
  subdivision only the split line nearest the snap line moves.
- Stochastic rules: several successors each with a probability, and `rand(a,b)` in sizes.
- Stated limits (section 8): the strict hierarchy of a split grammar "can no longer be enforced" once
  volumes are combined; split rules suit facades but were found unsuitable "for many forms of mass
  modeling"; arbitrary GIS footprints sometimes give implausible configurations; application to
  architectural design "is not yet explored and might require significant changes"; no geometric booleans
  are used, on purpose, for robustness.
- Cost reported: a 50,000-polygon model derives in about one second (C++, 2006 hardware).

**Esri CityEngine CGA reference, `split` operation** (P, read 2026-11-14, whole page).

- Syntax: `split(axis) { size : operations | ... }` and the same followed by `*`; an optional
  `adjust` / `noAdjust` mode; a UV variant.
- Sizes: no prefix = absolute, "exactly the same size"; `'` = relative, `size * current scope size`;
  `~` = floating: the space left by absolute parts is shared, several floating parts in proportion.
- `*`: the block is repeated "as often as it fully fits"; "the number of repetitions and floating
  dimensions are adapted to the best solution (best number of repetitions and least stretching)".
- Worked examples on a scope of sx = 10 (useful as test vectors):
  - `{ '0.5 | '0.1 | '0.2 }` gives 5, 1, 2 and a gap of 2 at the end.
  - `{ ~0.5 | ~0.1 | ~0.2 }` fills the scope keeping the ratios (6.25, 1.25, 2.5).
  - `{ 3.3 | ~3 | 5 }` gives 3.3, 1.7, 5.
  - Oversized `{ '0.5 | '0.6 | 3 }`: first 5, second cut to 5, third never created.
  - `{ 2 | 1 }*` all absolute: the pair repeats 3 times and the last unit holds half an X, cut off.
  - `{ ~2 | ~1 }*`: no piece is cut; sizes are adjusted keeping the ratio.
  - `{ 1 : X | { ~1 : Y | 0.2 : Z | ~1 : Y }* | 1 : X }`: the Y pieces come out at 0.9
    (inner space 8; 4 repeats of 2.2 nominal; (8 - 4*0.2)/8 = 0.9).
  - Rhythm ABABA: `{ { 1 : X | ~3 : Y }* | 1 : X }`.
- Each child gets `split.index` (zero-based) and `split.total`; in a repeat they count across all
  repetitions (index 0..9, total 10 in the page's example).
- The geometry is cut by planes perpendicular to the axis and closed; `NIL` leaves a hole.

(pending: Wonka 2003; comp, setback, offset, extrude, roof pages; CGA++; Lipp 2019.)

### 2.1 Shape grammars (pending)
### 2.3 Open implementations (pending)
### 2.4 Floor-plan generation (pending)

## 3. What bears on H2 and H3 (pending)
## 4. Counter-evidence (pending)
## 5. What a plain-ES5 app should take (pending)
## 6. Edges (pending)
## 7. Still open (pending)

## 8. Search log

| # | Date | Where | Query or URL | Result | Kept / set aside |
|---|---|---|---|---|---|
| 1 | 2026-11-14 | peterwonka.net | Müller 2006 PDF, direct | 200, 10 pages | kept, P |
| 2 | 2026-11-14 | peterwonka.net | Wonka 2003 PDF, guessed file name | 404 | retry with another copy |
| 3 | 2026-11-14 | www.shapegrammar.org | Gips 1999, Stiny and Gips 1972 | host does not resolve from here | retry another copy |
| 4 | 2026-11-14 | win.tue.nl | Bruls 2000 PDF | 200 | kept |
| 5 | 2026-11-14 | graphics.stanford.edu | Merrell 2010 PDF | TLS certificate chain refused | retry another copy |
| 6 | 2026-11-14 | arxiv.org | 2008.01803, 2004.13204, 2003.06988 | 200 | kept |
| 7 | 2026-11-14 | doc.arcgis.com | CGA split, comp, setback, offset, extrude, roofGable, split attribute, splitArea, changelog, seedian | 200 | kept |

## 9. References

- Müller P., Wonka P., Haegler S., Ulmer A., Van Gool L. 2006. Procedural Modeling of Buildings. ACM TOG
  25(3). https://peterwonka.net/Publications/pdfs/2006.SG.Mueller.ProceduralModelingOfBuildings.final.pdf
  Read: sections 1.1, 2, 3 (occlusion, snapping), 5-6 rule listings, 7, 8, 9. 2026-11-14. P.
- Esri. CityEngine CGA reference, split operation.
  https://doc.arcgis.com/en/cityengine/latest/cga/cga-split.htm Read: whole page. 2026-11-14. P.
