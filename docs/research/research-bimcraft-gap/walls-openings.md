# BimCraft gap: walls and what hangs on them

- Upstream: github.com/getcadcraft/bimcraft, pinned clone at commit `79b603f6683f2f000b9e8346c1fc92cf466ab01d`
  (2026-11-23 07:10 UTC), read as text only; no upstream code was run.
- Date of this note: 2026-11-28. Area: walls, joins, layered types, shaped walls, doors and windows, wall openings,
  curtain systems, sweeps, stacked walls.
- Levels: P = read in the primary source here (file:lines given), S = dependable secondary source with the gap
  said, U = unverified pointer (never used in a recommendation).
- Paths: BimCraft paths are relative to the clone's `app/` unless they start with `tests/`. Our paths are relative to
  `src/js/engine/` unless they start with `src/py/`.

## Licence and naming (P)

- Every BimCraft file read here starts with an `SPDX-License-Identifier: Apache-2.0` line (line 1 of each file listed
  below). The repository `LICENSE` is Apache-2.0, compatible with this Apache-2.0 repository.
- `NOTICE` lines 1-8: copyright The Data Design Group, Inc.; "CadCraft and the names of the apps in the CadCraft family
  are trademarks ... a fork must use another name". A port or vendored file keeps the NOTICE credit, and we must not
  reuse their names in our data: BimCraft writes property sets named `CadCraft_Wall`, `CadCraft_WallType`,
  `CadCraft_Opening`, `CadCraft_Door`, `CadCraft_CurtainSystem` and the join record name "CadCraft join"
  (`model-walls.js:54-55`, `:687`; `model-openings.js:47-49`; `model-curtain.js:42`). Our files would use our own
  names (for example `BIM_Personal_Wall`).

## Summary

BimCraft's wall work is far ahead of ours and, importantly, most of its geometry is already written as host-free
modules: `walls/joins.js`, `walls/joinstyle.js`, `walls/layerjoin.js`, `walls/shape.js`, `walls/cut.js`,
`walls/draw.js`, `walls/modify.js`, `walls/hold.js`, `walls/lod.js` and `walls/square.js` have no import line at all,
and `walls/reline.js` / `walls/typeswap.js` import only their siblings (P, the import listing of each file). Their
own headers say "Host-free: no DOM, no IFC, no app imports; plan millimetres" (for example `walls/joinstyle.js:3-5`,
`walls/layerjoin.js:3-6`). `curtain/layout.js` imports only five polygon helpers from `workplane/plane.js` (`:32`).
Everything that touches IFC (`model-walls.js`, `model-openings.js`, `wall-shape.js`, `model-curtain.js`,
`family-model.js`) is bound to BimCraft's IFC writer object `w` (`w.make`, `w.upsertPset`, `w.api.GetLine`) and to its
i18n module, so it cannot be reused; only its method can.

Our walls are JSON records on `A3D.objs` (`bim:{type:'wall', centerline, bulges, thickness, height, align, baseY,
closed, typeId, levelId}`, `bim/import-compliance.js:151-152`, `:184-187`), one polyline per object, mitred inside the
polyline by `bimOffsetRing` (`bim/section-profiles.js:217-235`) and meshed by `bimBuildWallRibbonMesh`
(`bim/wall-corners.js:5-28`). Between two separate walls there is no join: `bimJoinWalls`
(`editing/precision-editing.js:380-404`) only moves the two nearest ends to the centre lines' crossing, so the two
square-ended bodies overlap at the corner; there is no T, no X, no curved join (refused at `:383-384`). Types carry one
thickness and one material (`bim/type-instance-params.js:29-34`), no layers. Doors and windows are holes plus a marker
`{type, hostWallId, center, dir, width, height, sillHeight}` (`bim/columns-openings.js:406-433`): no panel, no frame,
no hand, no swing symbol in plan. Our IFC export writes each polyline segment as a separate box `IfcWall` with no type,
no material layer set and no connection record (`io/ifc-save.js:67-89`, `src/py/bim_ifcos.py:195-216`).

Recommendation in one line: port (P) the host-free geometry into small ES5 pure functions in a new
`src/js/engine/bim/wall-joins.js` family of files, in the order at the end of this note; vendor (V) nothing for core
walls, because wall bodies are built on every edit and must not wait on an on-demand module; consider V only for the
rarely used shaped-wall body (`walls/shape.js`) and the curtain layout if the owner prefers byte-identical upstream
code; leave families, stacked walls and sweeps (X from BimCraft: nothing there, or too IFC-bound).

## Data-model mismatch (P)

| Aspect | BimCraft | Ours | Consequence for a port |
|---|---|---|---|
| Source of truth | the IFC file: `IfcWall` placed at its start point with X along it, a `CadCraft_Wall` pset (TypeKey, Length, Thickness, Height, BaseOffset, TopLevel, TopOffset, ExteriorSide, Bulge, Justification, JoinOff), read back by `readWalls` (`model-walls.js:353-410`) | the JSON record on `A3D.objs`, written to IFC on save through IfcOpenShell (`io/ifc-save.js`, `src/py/bim_ifcos.py`) | the pure functions take plain rows; we build the rows from `o.bim` and never need BimCraft's reader |
| One wall | one straight or arc segment `{a, b, bulge}` | one polyline of any number of segments, optionally closed | the adapter explodes a polyline into segment rows `{key: id+'#'+i, a, b, t, bulge}`; the polyline's own vertices become L nodes that must keep today's mitre (the BimCraft rule gives the same mitre for two segments, `model-walls.js:228-239`) |
| Units and axes | millimetres, plan `[x, y]`, Z up | metres, plan `[x, z]`, Y up | the hard-coded tolerances are in mm (`JOIN_TOL = 1`, `walls/joins.js:21`; `MIN_H = 10`, `walls/shape.js:36`; `MIN_PART = 50`, `walls/cut.js:22`; `SHARP = 4` half-thicknesses, `walls/joinstyle.js:41`): a port takes the tolerance as a parameter in metres (0.001) instead |
| Join record | `IfcRelConnectsPathElements` named "CadCraft join L/T/X [style]" with ATSTART / ATEND / ATPATH (`model-walls.js:687-723`), derived from geometry by `deriveJoins` and reconciled (`walls/joins.js:37-80`) | none | store derived joins as `bim.joins` on each wall (or derive on each rebuild, which BimCraft also does when a file has none, `model-walls.js:392-393`); write them to IFC through IfcOpenShell later |
| Type | `IfcWallType` + `IfcMaterialLayerSet`; recipe `{key, name, exterior, layers:[{mat, t, function, core, priority, kind}]}` (`model-walls.js:58-93`, `wall-assemblies.js:24-54`) | `{id, name, params:{thickness, material}}` (`bim/type-instance-params.js:29-34`), instance keeps its own `bim.thickness` and a type edit propagates (`:19-28`) | add `params.layers` to our type; keep `thickness` as the sum so every existing reader still works |
| Openings | `IfcOpeningElement` voiding the wall, `IfcDoor`/`IfcWindow` filling it, placed relative to the wall; offset along the wall from its start, `hand` a/b, `face` left/right (`model-openings.js:17-33`) | marker object with a world `center` and `dir` (`bim/columns-openings.js:413`, `:430`) | the symbol and parts functions need `offset` along the host segment; the adapter computes it from `center` by projection, as `io/ifc-save.js:110-123` already does |

## Feature table

Gap: NONE = we match, PARTIAL, MISSING. Close by: V = vendor unchanged behind an adapter, P = port the method into
our ES5 engine, X = not worth it now. Effort: S (a day or less), M (a few days), L (a phase).

| # | Feature (Revit-level) | BimCraft (what, file:lines) | Ours (file) | Gap | Close by | Effort | Level |
|---|---|---|---|---|---|---|---|
| 1 | Layered (compound) wall types: layers with material, thickness, function, core flag | starter recipes with layers exterior to interior (`model-walls.js:58-72`); `wallType` marks the core and the layer functions, and makes a type at another thickness by growing the thickest layer (`:77-93`); project recipes validated, up to 32 layers, function in finish/substrate/structure/insulation/membrane, cavity kind, priority 0-999 (`wall-assemblies.js:22-54`) | one thickness and one material per type (`bim/type-instance-params.js:29-34`) | MISSING | P (data on our type record) | M | P |
| 2 | Location line: wall centre, core centre, finish face ext/int, core face ext/int | `JUSTIFICATIONS` and `locationOffset(just, t, extSide, assembly)` (`model-walls.js:330-342`), `locationLine(wall)` (`:344-349`); a type change keeps the location line by moving the centre line (`:535-563`) | `align` center/left/right (`bim/footings.js:219-225`) | PARTIAL (no core lines, no exterior side, line not kept on a thickness change) | P | S | P |
| 3 | Automatic wall cleanup at L, T and X between separate walls | `wallNodes(W, tol)`: ends within tol meet at a node, an end on another wall's side is a T (`model-walls.js:117-137`); `wallOutlines(walls, {tol, styles})`: rays sorted by angle, each neighbour pair meets where one's left face crosses the next one's right face, parallel faces end square, a mitre longer than four thicknesses is cut square, a self-crossing outline falls back to a rectangle (`:207-256`, helpers `clean`, `simpleCCW` `:295-322`) | inside one polyline only (`bim/section-profiles.js:217-235`); between walls `bimJoinWalls` moves the ends to the crossing, bodies overlap, no T, no X, on demand only (`editing/precision-editing.js:366-404`) | MISSING (between walls) | P | M | P |
| 4 | Join records (which walls are joined, where) | `deriveJoins(walls, {tol})`, `reconcile(derived, stored)`, `joinsIndex(records)`, `joinKey`, `kindOf` (`walls/joins.js:25-90`), no imports | none | MISSING | P (or V: 90 lines, no imports) | S | P |
| 5 | Join style per corner: mitre, butt, square off, which wall runs through; Disallow join per end | `cornerEnds(A, B, {style, through, tol})` (`walls/joinstyle.js:68-88`), `styleToken` / `parseStyleToken` / `nextStyle` (`:90-97`); used for a two-wall L only (`model-walls.js:188-206`); Disallow join per end as `JoinOff` 'a'/'b' (`:121-122`, `:634-638`) | none | MISSING | P (or V: 97 lines, no imports) | S | P |
| 6 | Layer cleanup at junctions by layer priority (cores join to cores) | `LAYER_PRIORITY` defaults, `layerPriority`, `layerBands(layers, extSide)` (`walls/layerjoin.js:49-80`); `cleanJunction({kind, walls, through})` gives pieces carried into the other wall, cuts and lines to draw (`:233-256`), display only; two walls per junction, straight walls only, refuses walls within 5 degrees of one line (`:44-45`); used by the fine plan (`wall-plan-graphics.js:10`, `:142`) | none (needs #1) | MISSING | P after #1 (V possible: 256 lines, no imports) | M | P |
| 7 | Top constraint to a level with offset, base offset, unconnected height, walls through several levels | `wallHeight(wall, levels, base)` (`model-walls.js:412-416`); `wallSpan`, `wallLevelsPassed`, `wallsThrough`, `topLevelChoices` (`:427-445`) | `baseY` and a fixed `height`; elements shift with a level's elevation (`bim/level-datum.js:13-30`) but the top does not follow a level above | PARTIAL | P | S | P |
| 8 | Attach top / base to a roof, floor or ceiling | `heightsFor` takes the lower of profile and attached underside per plan point, the higher for the base (`wall-shape.js:127-147`); `surfaceOf` reads the roof, floor or ceiling as `under(q)` / `over(q)` functions (`:61-93`), app-bound; `shapeBody(wall, outline, {topAt, baseAt, breaks, slant})` builds a closed faceted shell with volume, side area, foot area (`walls/shape.js:144-198`), `lineBreaks` (`:85`) | none | MISSING | P of `shapeBody` (or V of `walls/shape.js`, no imports, 342 lines); our adapter supplies `topAt` from `bim/roofs.js` | M | P |
| 9 | Edit profile (wall elevation outline) and slanted walls | profile lines `{top, bottom}` as `[[s, z]]`, `profileAt`, `checkProfile` (`walls/shape.js:57-75`); slant single or double, and the slanted wall's outline at the plan cut `cutOutline` (`:329-342`); curved walls too (`arcBody`, `:265`) | none | MISSING | same as #8 | M | P |
| 10 | Curved walls that join | curved faces as circles, `meetFaces` (`model-walls.js:258-272`), `arcOutline` keeps arc edges as bulges (`:278-292`); a curved wall keeps the mitre style (`:191`) | curved walls exist (bulges, `bim/import-compliance.js:51-64`) but Join and Merge refuse them (`editing/precision-editing.js:383-384`, `:426-427`) | PARTIAL | P, after #3 | M | P |
| 11 | Moving or resizing a wall keeps its joins (the joined walls follow and keep their angle) | `squareMove`, `moveJoined`, `setLength`, `setLengthGrow`, `setAngle`, `squareUp`, `roomSize` (`walls/square.js:120-458`); `relineJoined`, `endDrag` (`walls/reline.js:99-157`) | a grip drag rebuilds one wall only (`drawing/add-vertex.js:70-79`) | MISSING | P, after #4 | M | P |
| 12 | Constraints: align and lock, locked dimension, wall locked to a grid line | hold records `{kind:'line'|'end'|'dim'}`, `keep(walls, holds, plan, ctx)` refuses a change that breaks a hold (`walls/hold.js:2-30`, `:109-166`) | none for walls (`bim/grid-editing.js` edits grids only; not checked further) | MISSING | P, after #11 | M | P |
| 13 | Split, split with gap, delete a piece, rejoin; hosted doors and windows follow | `splitAt`, `deleteSegment`, `crossingAt`, `station`, `canRejoin`, `openingsAfter` (which part each opening goes to, refuses a cut through one) (`walls/cut.js:39-122`) | Break and Merge exist (`editing/modify-toolbox.js:271-301`, `editing/precision-editing.js:423-458`); Break moves no opening's `hostWallId` to the new piece (`:271-301` has no such line) | PARTIAL | P of `openingsAfter` and `canRejoin` | S | P |
| 14 | Door and window types with hand, face, sill; plan symbol with swing arc; 3D frame and leaves | starter kinds (single, double, sliding, pocket, garage, bifold, French, barn, sidelites; fixed, hung, casement, slider, awning, picture, egress, transom) with IFC operation / partitioning enums (`opening-types.js:14-37`); `handKind` (`:45-51`); `fitOffset(wall, width, offset, {gap})` (`model-openings.js:95-99`); `doorParts(type, op, t)` and `windowParts(type, op, t)` return boxes per part (`:321-381`); `openingSymbol(op, wall)` returns plan lines, arcs, thin and dashed lines and a pick polygon (`:492-575`); constants `FRAME`, `LEAF`, `WFRAME`, `WDEPTH`, `GLASS` (`:63`) | hole plus marker, width / height / sill only (`bim/columns-openings.js:191-216`, `:406-433`); IFC door and window bodies come from IfcOpenShell's own representation call (`src/py/bim_ifcos.py:274-279`) | PARTIAL (no hand, face, swing, parts) | P (pure apart from the i18n name and `wallGeom` for curved hosts) | M | P |
| 15 | Parametric door / window families (parameters, formulas, visibility, sizes as types) | `family-model.js` (1004 lines), recipe format and `evaluateFamily` (`:15-45`, `:429`), expression language in `expr.js` (313 lines); stored as `IfcGroup` + one type per size (`:7-13`) | type parameters (`bim/type-instance-params.js`), feature records with safe expressions (`bim/parametric.js:1-4`) | MISSING | X now; its own phase later (L), research separately | L | P |
| 16 | Curtain wall: grid lines by spacing or one by one, panels, mullions, border mullions | `layoutCurtain(sys)` gives panes (cell and glass), mullion pieces with their run-through rules, totals (`curtain/layout.js:2-31`, `:61-126`); grid edits `cleanLines`, `linesAtSpacing`, `addLine`, `moveLine`, `removeLine`, `setMullions`, `linesText`, `parseLines` (`:35-57`); needs `polyArea`, `isConvex`, `clipConvex`, `insetConvex`, `clipSegment` (`workplane/plane.js:92-194`); IFC as `IfcCurtainWall` aggregating `IfcPlate` and `IfcMember` (`model-curtain.js:11-21`); not embedded in a host wall, the host is only recorded (`:19`, `:73`) | none | MISSING | P (or V of the two files, 340 lines, one import edge) | M | P |
| 17 | Plain wall openings (a hole with no door or window) | `IfcOpeningElement` with Kind 'wallopening' (`wall-shape.js:15-16`, `addWallOpening` `:215`) | every opening is a door or window marker (`bim/columns-openings.js:413`, `:430`) | PARTIAL | P (a third marker type) | S | P |
| 18 | Wall quantities net of openings | `writeWallShape` writes length, width, height, gross and net side area, gross and net volume (`model-walls.js:846-856`) | schedule area is length x height, gross (`bim/usages-live-areas.js:306`) | PARTIAL | P | S | P |
| 19 | Mitres kept in the IFC file | the joined outline is the extruded profile (`model-walls.js:838-845`) | each polyline segment saved as a full-length box, so corners overlap in IFC (`io/ifc-save.js:71-84`, `src/py/bim_ifcos.py:205-208`) | MISSING | P (send the joined outline as the profile) | S | P |
| 20 | Wall type swap with a report of what moved | `planSwap`, `swapChoices`, `swapReport`, `reportLines` (`walls/typeswap.js:41-161`) | `bimSetWallTypeOf` (`bim/type-instance-params.js:868`) | PARTIAL | X now (nice to have) | S | P |
| 21 | Wall sweeps and reveals | nothing found (no match in `walls/`, `wall-*.js`, `model-walls.js` for sweep / reveal / skirting other than arc sweeps in `walls/draw.js:30-99`) | none (a general sweep mesh exists: `bimSweepMesh`, `bim/section-profiles.js:236-238`) | MISSING in both | X from BimCraft; our own research | M | P |
| 22 | Stacked walls | nothing found (the only "stacked" matches are UI panes, `panes.js:12-13`) | none | MISSING in both | X from BimCraft | M | P |
| 23 | Wall to floor join cleanup | none as geometry; floors are made from the wall loops (`wall-shape.js:34-36` reads `storeyLoops`) | rooms from walls (`bim/rooms.js:103`) | both lack it | X | - | P |

## Notes per gap

### 1. Layered types (P)

BimCraft keeps one type model for walls, floors, roofs and ceilings (`wall-assemblies.js:11-21`,
`element-types.js:7-11`). A layer is `{mat, t, function, core, kind ('material'|'cavity'), ventilation, priority}`;
a zero-thickness layer is allowed only as a membrane (`wall-assemblies.js:36-41`). The core is the first
studs/block/cmu/concrete/generic layer for starters (`model-walls.js:83-84`). For us: add `params.layers` to the type
records of `bim/type-instance-params.js`, keep `params.thickness` equal to the sum (the instance propagation at
`:19-28` and every reader of `bim.thickness` keep working), validate with a port of `validateAssembly`'s rules (not its
i18n). IFC: our adapter would send the layers to `src/py/bim_ifcos.py`; which IfcOpenShell API calls make an
`IfcMaterialLayerSet` and its usage is not read here (U) and must be read in the pinned wheel under `runtime/` before
that task is written.

### 2. Location line (P)

`locationOffset` (`model-walls.js:332-342`) answers the signed distance from centre line to location line to the
wall's left; the core variants need the layers (#1). Our `bimAlignOffsets(thickness, align)` already accepts an object
`{dLeft, dRight}` (`bim/footings.js:221`), so a port can return that object and nothing downstream changes. The
"keep the location line when the type changes" rule (`model-walls.js:535-563`) is a small extra: shift the centre line
by the difference of the two offsets.

### 3 and 10. Joins between walls (P)

The method to port is `wallNodes` + `wallOutlines` (`model-walls.js:117-256`) with `meet` (`:109-114`), `clean`,
`simpleCCW`, `segCross`, `rect` (`:293-322`). It needs `wallGeom(w)` from `model-arcs.js` (`:42`) for its `param`,
`at` and `tan` queries (`:132`, `:175-176`, `:216-219`); for straight segments those are a few lines, so a first port
handles straight walls and keeps our current refusal for curves, then #10 adds `meetFaces` / `arcOutline`. Our output
differs: BimCraft extrudes a closed plan outline per wall; we build a ribbon from two offset rings
(`bim/wall-corners.js:5-28`). The cleanest fit is to build a wall's body from the joined outline (an extruded polygon
mesh, which `padMesh` already makes for openings, `bim/columns-openings.js:275`) when it has joins, and keep the ribbon
for a lone polyline, so existing projects build byte-identically.

### 4 and 5. Join records and styles (P)

`walls/joins.js` (90 lines) and `walls/joinstyle.js` (97 lines) are pure and import nothing; they use ES2015+
(template strings, destructuring, default parameters), so a port is a mechanical ES5 rewrite. Our record: `bim.joins =
[{other, pos: 'start'|'end'|'mid', otherPos, kind, style, through}]`, derived on every wall rebuild with
`reconcile` keeping a stored style (`walls/joins.js:77-80`; BimCraft keeps style in the record and never rewrites a kept
record, `model-walls.js:725-729`). Per-end Disallow join: `bim.joinOff = {a, b}`.

### 6. Layer priority cleanup (P)

Display only by its own statement (`walls/layerjoin.js:4-6`): the wall body never changes. It is the piece that makes
plans look like Revit's at fine detail. Its inputs are the join (#3, #5 give `face`), the layers (#1) and the
wall's outline. It handles two walls per junction and straight walls only (`:44-45`). Our plan drawing would apply
`cuts` and `adds` as BimCraft's host does (`wall-plan-graphics.js:142-147`).

### 7. Level-bound tops (P)

Add `bim.topLevelId` and `bim.topOffset` (instance parameters, as Revit has them) and compute `height` from them on each
rebuild (`model-walls.js:412-416`); `bim/level-datum.js` then also rebuilds walls whose top level moved. `wallsThrough`
(`:436-441`) is what lets a plan show a two-storey wall on the upper level.

### 8 and 9. Shaped walls (P, V possible)

`walls/shape.js` is pure and self-contained (no imports; `fail`, `arcFrame`, `triangulate`, `clipS`, `planar`, `det3`
are its own, `:36-342`). The host supplies `topAt(p, s)` and `baseAt(p, s)` and the break stations. For us `topAt` would
come from our roof planes in `bim/roofs.js` (not read in this note; its plane query must be checked before the work
order). The body is a closed faceted shell, which our mesh format `{v, f}` takes directly. If the owner prefers
upstream code unchanged, this file is the best V candidate: it is only needed when a wall has a shape, so it can load
on demand like three.js (V194), and it is not held to ES5. Its outputs: `{verts, faces, volume, sideArea, footArea,
ring}` (`:198`).

### 11 and 12. Edits that keep joins, and holds (P)

`walls/square.js` (470 lines) and `walls/reline.js` (157 lines) work on rows `{guid, a, b, t, bulge, storey, joins}`
and answer `Map guid -> {a, b}` (`walls/square.js:4-8`); they throw `{key:'model.err.short'}` on a fold. ES5 has no
`Map`-free equivalent problem (Map is ES2015): a port returns a plain object keyed by id. Our grip drag
(`drawing/add-vertex.js:70-79`) and Move would call the port and rebuild every wall in the answer, inside one
`pushUndo`. `walls/hold.js` builds on these and is later work.

### 13. Split and openings (P)

`openingsAfter(openings, cut)` (`walls/cut.js:113-122`) sorts openings into stay / move (with their new offset) / cut
(the change is refused). Adding it to `bimApplyBreak` closes the hosted-opening hole in our Break.

### 14. Doors and windows (P)

`openingSymbol` (`model-openings.js:492-575`) is pure geometry over `op = {typeKey, kind, offset, width, hand, face}`
and `wall = {a, b, t, bulge}`; its only outside calls are `openingType` and `wallGeom` (curved host). `doorParts` /
`windowParts` (`:321-381`) answer boxes `{box:[x0,y0,z0,x1,y1,z1], style}` in the opening's axes, which our mesh
builder can turn into boxes and place with the marker's `center` and `dir`. Data to add to our marker: `typeKey`,
`hand`, `face`. The IFC operation enum per type (`opening-types.js:15-24`) can go to `src/py/bim_ifcos.py` as the
door's operation type; how IfcOpenShell's door representation call takes it was not read here (U).

### 15. Families (X now)

Large, IFC-centred (groups, type per size, representation maps, `family-model.js:7-13`) and tied to an expression
language. Our own parametric records (V204) are the base to grow from; a separate research note should compare
BimCraft's recipe format (`:15-41`) with ours before anything is ported.

### 16. Curtain walls (P, V possible)

`layoutCurtain` (`curtain/layout.js:61-126`) is a clean 2D layout in the system's own plane: panes are grid cells
clipped to the outline and inset by half a mullion (a whole one at the border); u-line mullions run through, v-line
mullions stop at u mullions and the border; border corners cut square (`:19-26`). Port it with the five helpers from
`workplane/plane.js` (`:92-194`), place the 2D results on a frame along a wall's centre line (BimCraft's
`wallCurtain`, `model-curtain.js:47`), and mesh panes as thin prisms and mullions as rectangular sweeps. Neither app
embeds a curtain wall in a basic wall (BimCraft records a host only, `model-curtain.js:19`); that and doors in curtain
panels stay open.

### 19. Mitres lost in our IFC (P)

`bimIfcSaveWalls` sends each segment as a box via `add_wall_representation` with a length and offset
(`io/ifc-save.js:71-84`, `src/py/bim_ifcos.py:205-208`), so every corner overlaps in the file. Once #3 gives a joined
outline per segment, send it as an arbitrary profile extrusion (`bim_ifcos.py` already extrudes polylines for slabs with
`add_slab_representation`, `:234-237`; whether the same call suits a wall body was not checked, S).

### 21 and 22. Sweeps and stacked walls (X from BimCraft)

Nothing to reuse. A wall sweep for us would be `bimSweepMesh` along a face offset of the joined outline; a stacked wall
is a type made of sub-types by height. Both need their own research note.

## Tests that cover the BimCraft code (P)

- `tests/lib/walls/test/test.mjs` (403 lines): known answers worked out by hand for draw, cut, modify, hold, joins,
  reline, join style (`:224`), layer priority at L, T and X (`:271`), moves of several walls (`:341`) and curved shaped
  walls (`:356-365`). The test files `tests/lib/walls/*.js` are byte-identical to `app/walls/*.js` (checked with cmp
  here, apart from `straight.js`, which exists only under `tests/lib/walls`).
- `tests/lib/walls/test/typeswap.test.mjs` (110 lines).
- `tests/tools/bimcraft-test/wall-joinstyle-test.mjs` (224), `wall-shape-test.mjs` (327), `wall-square-test.mjs`
  (152), `wall-tools-test.mjs` (272), `mlwall-test.mjs` (111), `model-test.mjs` (627; `openingSymbol` at `:274`,
  `:544`), `families-test.mjs` (starters equal `doorParts` / `windowParts`, `:67-73`), `tools-b-test.mjs` (338;
  curtain layout at `:19-56`, By Face at `:174`).
- These are not runnable here under our rules (never run upstream code) and are in their own runner; their known
  answers are what our ported unit tests should restate in metres. Ours today: no unit test covers wall joins or
  openings (`tests/unit/` has wall fixtures only in IFC, interiors and surface tests).

## Proposed build order (small pure functions, ES5, metres, plan [x, z])

Each is a separate `[Cline]` task with one unit test in `tests/unit/wall-joins.test.mjs` (or the named file),
restating BimCraft's hand-worked answers. Files are new under `src/js/engine/bim/`; each stays under 400 lines.

1. `bim/wall-joins.js`
   - `bimWjSegments(o)` -> `[{key, a, b, t, bulge, joinOff}]` from one wall record (explodes the polyline).
   - `bimWjDerive(rows, tol)` -> `[{key, a:{id, pos}, b:{id, pos}, kind}]` (port of `walls/joins.js:37-75`).
   - `bimWjReconcile(derived, stored)` -> `{add, remove}` (`:77-80`); `bimWjIndex(records)` (`:82-90`).
2. `bim/wall-joinstyle.js`
   - `bimWjCornerEnds(A, B, style, through, tol)` -> `{a:{left, right}, b:{left, right}, style}` (port of
     `walls/joinstyle.js:59-88`); `bimWjStyleNext(style)`.
3. `bim/wall-outline.js`
   - `bimWjNodes(rows, tol)` -> `[{p, ends, tees}]` (`model-walls.js:117-137`).
   - `bimWjOutlines(rows, tol, styles)` -> `{key: [[x, z]...]}` with each end's cut points (`:207-256`), straight walls
     first; `bimWjSimpleCCW(poly)`.
   - Then: build a joined wall's mesh from its outline; IFC save sends the outline (#19).
4. `bim/wall-layers.js`
   - `bimWlValidate(type)` -> `{ok, error}` (rules of `wall-assemblies.js:24-54`), `bimWlThickness(layers)`.
   - `bimWlLocationOffset(just, t, extSide, layers)` -> number (`model-walls.js:332-342`).
   - `bimWlBands(layers, extSide)`, `bimWlPriority(layer)` (`walls/layerjoin.js:63-80`).
5. `bim/wall-levels.js`
   - `bimWlHeight(wall, levels)` (`model-walls.js:412-416`), `bimWlSpan`, `bimWlThrough(walls, levels, levelId, cutY)`
     (`:427-445`).
6. `bim/opening-symbols.js`
   - `bimOpHandKind(type)` (`opening-types.js:45-51`), `bimOpFitOffset(segLen, width, offset, gap)`
     (`model-openings.js:95-99`).
   - `bimOpSymbol(op, seg)` -> `{lines, arcs, thin, dashed, poly}` (`:492-575`).
   - `bimOpDoorParts(type, op, t)`, `bimOpWindowParts(type, op, t)` -> boxes (`:321-381`).
7. `bim/wall-cut.js`
   - `bimWcOpeningsAfter(openings, cut)` (`walls/cut.js:113-122`), `bimWcCanRejoin(w1, w2, tol, maxGap)` (`:88-112`).
8. `bim/wall-move.js`
   - `bimWmSquareMove(rows, id, d)`, `bimWmSetLength(rows, id, len, from)` (`walls/square.js:120-153`, `:382-420`),
     `bimWmEndDrag(rows, id, end, to)` (`walls/reline.js:147-157`).
9. `bim/layer-cleanup.js`
   - `bimLcJunction(kind, walls, through)` -> `{adds, cuts, lines}` (`walls/layerjoin.js:146-256`), plus
     `bimLcSubtractConvex`, `bimLcSegmentOutside` (`:108-135`).
10. `bim/curtain-layout.js`
    - `bimCwLines(list, lo, hi, tol)`, `bimCwAtSpacing(lo, hi, spacing, m)` (`curtain/layout.js:35-49`).
    - `bimCwLayout(sys)` -> `{panels, mullions, totals}` (`:61-126`) with `bimCwClipConvex`, `bimCwInsetConvex`,
      `bimCwClipSegment`, `bimCwIsConvex` (`workplane/plane.js:93-194`).
11. `bim/wall-shape.js` (or V of `walls/shape.js` on demand)
    - `bimWsProfileAt(line, s)`, `bimWsCheckProfile(line, L)`, `bimWsBody(wall, outline, topAt, baseAt, breaks,
      slant)` (`walls/shape.js:57-198`).

Steps 1-3 together close the most visible Revit gap (walls that clean up at L, T and X); 4 and 6 are the next most
visible (layered types, doors with swings); 10 and 11 are new element kinds.

## Open questions and decisions for the owner

- D1: port (P, ES5, our names) or vendor (V, unchanged ES modules loaded on demand) for `walls/shape.js` and
  `curtain/layout.js`; everything on the edit path is recommended P.
- D2: store joins on the walls (`bim.joins`, like BimCraft's record) or derive them on every rebuild only.
- D3: whether IFC save writes `IfcRelConnectsPathElements` and material layer sets now, which needs the IfcOpenShell
  API calls read in the pinned wheel first (U today).
- Not read here: our `bim/roofs.js` plane query (needed by #8), `bim/grid-editing.js` beyond its name (#12).

## Search log

- `ls app | grep -iE 'wall|door|window|open|curtain|sweep|stack|join|layer|...'`, then the import lines and line counts
  of each match; read in full or by function: `model-walls.js` (860), `walls/joins.js`, `walls/joinstyle.js`,
  `walls/layerjoin.js`, headers and exports of every `walls/*.js`, `wall-shape.js:1-181`, `walls/shape.js:144-212`,
  `model-openings.js:1-103`, `:321-392`, `:492-576`, `opening-types.js`, `model-curtain.js:1-45`, `curtain/layout.js`,
  `wall-assemblies.js:1-40`, `element-types.js:1-25`, `family-model.js:1-45` and its exports, `NOTICE`.
- `grep -rlniE 'wall ?sweep|reveal|stacked wall|skirting'` over `app/` (no wall feature found), `grep -rniE stacked`.
- Ours: `grep -rn` for wall builders, `bimJoinWalls`, openings, `IfcOpeningElement`, `layers`, `attach`; read
  `bim/import-compliance.js`, `bim/wall-corners.js`, `bim/levels-walls-floors.js`, `bim/section-profiles.js:217-235`,
  `editing/precision-editing.js:360-470`, `bim/columns-openings.js:191-216`, `:406-436`, `bim/type-instance-params.js:1-80`,
  `io/ifc-save.js:1-130`, `src/py/bim_ifcos.py:195-300`, `editing/modify-toolbox.js:271-301`, `drawing/add-vertex.js:70-79`.
