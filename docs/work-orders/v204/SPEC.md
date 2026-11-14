# V204 spec: The Parametric Design Foundation, sketch to Pad to Pocket

Notion: Parametric Design Foundation (SolidCraft-inspired modeling). Research: `docs/research/research-parametric-history.md`, `docs/research/research-parametric-app-audit.md`, `docs/research/solidcraft-integration-map.md`, `docs/research/plan-parametric-design.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- The first slice is a constrained closed rectangle sketch, Pad and Pocket, with feature records (id, kind, inputs as safe expressions, references, status) kept with the project; SolidCraft is a design reference, not copied code, until its integration map is verified.
- Rebuild in dependency order; a cycle is refused before anything is built; a failed feature says why and keeps its last valid result, never attaching silently to another face.
- Expressions allow numbers, parameter names, + - * / and brackets only (no code evaluated); units are metres.
- The app's own history (history/) carries undo; a failed edit never leaves mixed old and new geometry.

## 2. What it does for the user

Draw a rectangle sketch, Pad it, Pocket it; change the width parameter and the solid rebuilds; a pocket that no longer fits is marked failed with its reason and the last good solid stays.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/parametric.js` | new, after `js/engine/bim/mep-flow.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v204/v204.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 4. Data

A feature {id, kind: 'sketch'|'pad'|'pocket', refs: [ids it depends on], inputs: {name: expression string}}. A result {status: 'ok'|'failed', why, the values, kept (the last valid result)}.

## 5. Functions, `src/js/engine/bim/parametric.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimPfOrder(fs)`**: a depth-first post-order over the features in their given order, following refs (refs to absent ids are ignored): {order: [ids]}; a cycle met gives {error: 'cycle', ids: the path from the repeated id back to it, e.g. ['a', 'b', 'a']}.
- **WO-02 `bimPfDownstream(fs, id)`**: the ids that depend on id directly or through others, in bimPfOrder's order; the cycle error object when there is one.
- **WO-03 `bimPfExpr(s, params)`**: a recursive-descent reader over sum := prod (('+'|'-') prod)*, prod := atom (('*'|'/') atom)*, atom := number | name | '(' sum ')' | '-' atom, spaces skipped: {value} or {error} with the first of 'unknown name N', 'division by zero', 'expected )', 'unexpected C' (C the character, or 'end'). A name must be a number in params. No eval, no Function.
- **WO-04 `bimPfRebuild(fs, params, last)`**: the cycle error as {error: 'cycle', ids}; else in order: sketch {status 'ok', w, l, area} when both expressions are positive, else failed 'the sketch needs a positive width and length'; pad on its first ref: ok {depth, area, w, l, volume: area depth} when its sketch is ok and depth > 0, else failed 'its sketch or depth is not valid'; pocket on its pad: failed 'its pad is not valid', or failed 'the pocket does not fit in its pad' (any size not positive, w or l over the pad's, depth over its depth), else ok {volume: pad volume - w l depth}; any other kind failed 'unknown kind'. A failed feature whose entry in last was ok carries it as kept. {order, results}.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** sketch, pad and pocket in the app; **WO-06** the records.

## 7. Not in this phase

General sketch constraints (a solver); references to faces (topological naming) beyond the pad's own; fillets, chamfers, patterns.
