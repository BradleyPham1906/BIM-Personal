# V229 spec: A split grammar for facades

Notion: Algorithmic Design (research; proposed V228 to V232). Research: `docs/research/research-algorithmic-design.md` and the notes in `docs/research/research-algorithmic-design/`. The owner's decisions, 2026-11-15: all thirteen as the research recommends (the owner: "Just do whats recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-15.

## 1. The decisions this spec follows

- Rules are data, checked before anything runs; no code is evaluated (decisions 1 and 12).
- A split's sizes are absolute, relative to the scope, or floating, as Esri's CGA reference describes them (research 4.3; the reference was confirmed by the independent check).
- A repeat uses the nearest count, at least one (decision 4; e03: `ceil` turns 35.1 m into 11 storeys of 3.19 m).
- Every leaf carries its path of rule names and semantic indexes, which V228's key is built from (decision 3).
- A shape is its rectangle on the facade plane; plane cuts, occlusion, snapping and roofs are left out (H2 as restated).

## 2. What it does for the user

Describe a facade as rules (a ground floor and storeys; bays; in each bay a window between piers), set the storey height and bay width, and the facade is divided into named parts that follow when the wall is stretched or a parameter changes.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/split-grammar.js` | new, after `js/engine/bim/generated-elements.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v229/v229.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 4. Data

Rules {name: {op: 'split', axis, parts: [[size, ruleName]]} | {op: 'repeat', axis, size, rule} | {op: 'element', kind}}; a size is a number, a parameter's name, {rel} or {fl}. A leaf {rule, kind, path: [[ruleName, index]], x, y, w, h} in metres on the facade's plane, x along it and y up.

## 5. Functions, `src/js/engine/bim/split-grammar.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimSgSizes(len, sizes)`**: sizes: a number is absolute; {rel: r} is r times len; {fl: f} is floating. Negative numbers, rel and fl count as 0; anything else is 0. The floating parts share max(0, len - the absolute and relative sizes) in proportion to their f (0 each when the f sum to 0). The resolved sizes, in order; nothing is cut here.
- **WO-02 `bimSgSplit(len, sizes)`**: the sizes from bimSgSizes placed end to end from 0: [{i (the part's position in sizes), at, size}], each size cut to what is left of len; a part of 1e-9 or less (after cutting) is left out and does not advance; parts after the scope is full are therefore left out.
- **WO-03 `bimSgRepeat(len, size)`**: {n: 0, size: 0} unless len and size are both over 0; else n = max(1, floor(len / size + 0.5 + 1e-9)) (the nearest count, a half going up, at least one) and {n, size: len / n}.
- **WO-04 `bimSgValidate(rules, start)`**: rules {name: rule}; a rule is {op: 'split', axis: 'x'|'y', parts: [[size, ruleName], ...]}, {op: 'repeat', axis, size, rule: ruleName} or {op: 'element', kind}. In this order: start not an own key of rules {error: 'no start rule S'}; then for names in sorted order, the first of: op not one of the three 'unknown op in N'; a split or repeat whose axis is not 'x' or 'y' 'bad axis in N'; a split with no parts 'no parts in N'; an element whose kind is not a non-empty string 'no kind in N'; a split's part or a repeat's rule naming no rule 'missing rule R in N' (a split's parts in order); then a depth-first walk from each name in sorted order following a split's parts in order and a repeat's rule: a rule met again while still being walked gives {error: 'cycle at R'}, R that rule. Else {ok: true}.
- **WO-05 `bimSgDerive(rules, start, scope, params, limit)`**: bimSgValidate's error as it is. scope {x, y, w, h} (x and y 0 when absent); a shape is {rule, path, x, y, w, h}, the first {rule: start, path: [[start, 0]]} over the scope. Shapes are taken depth first, a shape's children in order; each shape taken counts one step, and more than limit (100000 unless limit is over 0) gives {error: 'more than L shapes'}. A size is a number, or a string naming a number in params, or {rel: ...} or {fl: ...} whose value is one of those. An element rule gives a leaf {rule, kind, path, x, y, w, h}. A split resolves its sizes (any size not a number of 0 or more: {error: 'bad size in N'}, N the shape's rule) and uses bimSgSplit along its axis (x: along w from x; y: along h from y); each cut gives a child of the part's rule whose path adds [ruleName, k], k the count of earlier parts of the same split with that rule name (so the second 'Pier' of a split is index 1 whether or not anything before it was cut). A repeat (size not over 0: 'bad size in N') uses bimSgRepeat and gives n children of its rule with path [ruleName, i]. {leaves (in the order met), steps}.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** a facade generator on V228's records: a wall face as the scope, leaves made into the app's walls and openings through V228's batch maker and keys, its parameters as a form in Properties and its rules as text beside it; **WO-07** the records.

## 7. Not in this phase

The four sides of a mass (a component split) and massing rules; roofs; plane cuts, occlusion and snapping; stochastic rules; any geometry kernel.
