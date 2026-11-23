# V275 spec: the Explode view

Research: `docs/research/research-xr-interaction.md` (E1, E2) and `research-xr-interaction/bim-xr.md` part 4, with the
independent check's corrections. The owner's decisions, 2026-11-23: E1 to E8 as recommended, E4 changed by the owner
(a simulated hand, for V276). Implementation target: local `main`. Written by Claude, 2026-11-23.

## 1. What it does for the user

**EXPLODEVIEW** (a command, and a button with a slider in the view) pulls the storeys of each building apart upward,
like a stack of plates, so each floor can be seen. The slider sets how far, from 0 (together) to 1 (each storey one
storey-height above where it was, times its rank: the ground storey stays, the next rises one gap, the next two). It
works in every view and on phone, tablet and desktop; later the headset's two-hand spread sets the same amount. It is
display only: no element moves, nothing is saved into the model, nothing enters the undo list. Saved views remember it.
Starting an edit (a move, a draw, any command that changes the model) collapses it first, with a toast. The old
`EXPLODE` command (AutoCAD's polyline explode) is unchanged and unrelated.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/views/explode-view.js` | new, after `js/engine/views/saved-views.js` in `src/index.html` (header done) | 6 pure functions (part 4) | Cline, WO-01 to WO-06 |
| `docs/work-orders/v275/v275.test.mjs` | new | their tests | Claude (done) |
| the renderer, the view chrome, saved views, the command catalogue | changed | the offset drawn and picked, the button and slider, saving, collapsing | Claude, WO-07, WO-08 |

## 3. Data

- **A level** (`A3D.levels`, `core/state.js`): `{id, name, elev (m), height (m, may be missing), buildingId}`.
  IFC imports name theirs `<storey> (IFC)` (`io/ifc-full.js`) and leave a storey without elevation without a level.
- **An item** (built by WO-07 from each element): `{id, levelId, storey, minY}`: `levelId` is `o.bim.levelId` or
  `o.levelId` or null (`bimObjectLevelId`, `views/saved-views.js`); `storey` is `o.bim.storey` or ''; `minY` the lowest
  point of the element as drawn (`o.pos[1]` plus its mesh box's bottom), or undefined.
- **The state** `A3D.explode`: `{on: boolean, amount: 0 to 1}`; drawn amount = `on ? amount : 0`.
- **An offset**: `[0, dy, 0]` metres, added to the element where it is drawn and picked, never to `o.pos`.

## 4. Functions, `src/js/engine/views/explode-view.js`

ES5. Pure: none changes what it is given; none uses another file's names (WO-05 uses WO-01 to WO-04 of this file).

### WO-01 `bimXvRanks(levels)`
- **Returns:** `{levelId: rank}`: within each building (`buildingId`, missing is one group of its own), the levels sorted
  by `elev` ascending, equal elevations in their array order; rank 0 for the lowest. `{}` for null or none.
- **Example:** levels a2 (6 m), a0 (0), a1 (3) of building A give `{a0: 0, a1: 1, a2: 2}`.

### WO-02 `bimXvLevelOf(item, levels)`
- **Returns:** the level id for an item, by the first rule that answers:
  1. `item.levelId` when a level with that id exists;
  2. `item.storey` (non-empty) when a level is named `item.storey + ' (IFC)'`;
  3. `item.minY` (a finite number): the level with the highest `elev` that is at most `item.minY + 0.05` (a slab a few
     centimetres off still counts); if none is that low, the lowest level (the first of equal lowest);
  4. otherwise null. Null too when there are no levels.

### WO-03 `bimXvGap(levels)`
- **Returns:** the largest finite positive `height` among the levels; 3 when there is none.

### WO-04 `bimXvOffset(rank, amount, gap)`
- **Returns:** `[0, rank * gap * a, 0]`, with `a` the amount kept between 0 and 1; `[0, 0, 0]` when rank is null or undefined.

### WO-05 `bimXvOffsets(items, levels, amount)`
- **Returns:** `{id: offset}` for every item whose offset is not zero: its level by WO-02, its rank by WO-01, the gap by
  WO-03, the offset by WO-04. `{}` when the amount is 0 or nothing moves.
- **Example:** SPEC's test levels at amount 0.5, gap 4: a wall on a2 rises 4 m; a column on IFC storey "First" (b1)
  rises 2 m; an element on a0 is left out.

### WO-06 `bimXvNext(state, action)`
- **Takes:** the state (null is `{on: false, amount: 0}`) and an action: `{type: 'toggle'}`, `{type: 'set', amount}`,
  `{type: 'collapse'}`.
- **Returns:** a new state, never the same object: toggle turns off keeping the amount, or on with the last amount
  (0.5 when it was 0); set keeps the amount between 0 and 1 and is on when it is above 0; collapse is
  `{on: false, amount: 0}`; any other action returns a copy.

## 5. Order of the work

WO-01 to WO-06 in order. Then Claude:

- **WO-07 the offset drawn and picked.** `render/gpu-batches.js` adds the element's offset to its row (`v[0..2]`) and to
  its chunk's box; the rendered view (`render/rendered-scene.js`) and GPU picking (`render/gpu-pick.js`) read the row
  already. Every other drawing and picking path that reads `o.pos` (38 engine files read it; the check asked for a full
  audit) is listed and given the offset where it draws or picks, and nowhere else. The offsets are computed once when
  the amount or the model changes, not per frame. The cost of the rendered view rebuilding its chunks while the slider
  moves (`rendered-scene.js` hashes the rows) is measured and, if large, the drag updates at most every 100 ms.
- **WO-08 the interface.** `EXPLODEVIEW` in the command catalogue and map; a button and slider in the view chrome, on
  phone, tablet and desktop; `A3D.explode` saved in saved views and restored; any model-changing command collapses it
  first with the toast "Explode view closed for editing"; not saved in the project file.
- **WO-09** the tests to `tests/unit/explode-view.test.mjs`, `npm run modules`, the build, the one browser check of the
  new interface (CLAUDE.md Rule #1).
- **WO-10** the records: QUEUE, PIPELINE, Notion.

## 6. Not in this phase

Explode by building or by layer (next, the same functions with another rank); dragging one storey on its own; the
two-hand spread (V276, V277); explosions of assemblies or along other axes; editing while exploded.
