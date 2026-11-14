# V177 spec: IfcOpenShell II, step 2: the model as V177's data

Notion: V177 IfcOpenShell II (IFC save). Research: `docs/research/research-ifcopenshell-app.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- The owner's D1 to D4 (2026-11-13, in SPEC.md). Step 2's pure part turns the app's model into the data step 1's adapter takes (SPEC.md part 3): plan [x, z] to IFC [x, -z], heights kept, levels by index, walls by straight segment with their side as the offset, floors and rectangular columns as prisms, doors and windows on their segments, every other solid as a triangle mesh.
- Curved walls go as meshes; GUIDs already on elements (V196 imports) are kept.

## 2. What it does for the user

File, Export, IFC writes the model through step 1's adapter (Claude's WO-20 wires it).

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/io/ifc-save.js` | new, after `js/engine/io/gltf.js` in `src/index.html` (header done) | 9 pure functions (part 5) | Cline, WO-11 to WO-19 |
| `docs/work-orders/v177/v177-step2.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-20, WO-21 |

## 5. Functions, `src/js/engine/io/ifc-save.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-11 `bimIfsPlan(p)`**: [p[0], 0 - p[1]] (never -0).
- **WO-12 `bimIfsLevels(levels)`**: the levels with a finite elev, as {id: String(id), name (or 'Level ' + the count so far), elev}, sorted by elev.
- **WO-13 `bimIfsLevelIndex(lv, levelId, y)`**: the index of the level whose id is levelId; else of the last with elev <= y + 1e-6; else 0 (also for no levels).
- **WO-14 `bimIfsWalls(o, lv)`**: [] unless a wall with 2 or more centreline points and no bulges; one entry per segment (and last to first when closed with more than 2): {id (o.id, or o.id + '#' + i when several), host: o.id, name (o.name, or o.name + ' ' + (i+1)), level (WO-13 on levelId and baseY), x0, y0, x1, y1 (WO-11), base: baseY, height, thickness: dLeft + dRight, offset: 0 - dLeft, guid when bim.guid is set}; dLeft and dRight from align: 'left' {0, t}, 'right' {t, 0}, an object with finite dLeft and dRight as it is, else {t/2, t/2}.
- **WO-15 `bimIfsSlab(o, lv)`**: null unless a floor with 3 or more profile points; {id, name, level (on baseY - thickness), cls: 'IfcSlab', pts (WO-11), base: baseY - thickness, depth: thickness}.
- **WO-16 `bimIfsColumn(o, lv)`**: null unless a column with a center and no section; its four corners in the app's plan (local (-w/2,-d/2), (w/2,-d/2), (w/2,d/2), (-w/2,d/2) turned by rotation: x cos - z sin, x sin + z cos, plus the centre), each through WO-11, the list reversed (anticlockwise in IFC's plan); {id, name, level, cls: 'IfcColumn', pts, base: baseY, depth: height}.
- **WO-17 `bimIfsOpening(m, walls)`**: null unless a door or window with a center and walls given; among the walls whose host is bim.hostWallId (length 1e-9 or more), the projection t of the centre (WO-11) within -1e-6..L+1e-6, the one nearest its line: {id, name, cls: 'IfcDoor' or 'IfcWindow', host: that wall's id, x, y: the point t along its line, a: atan2(dy, dx) of the wall, base: the wall's base + (sillHeight or 0), width, height, depth: the wall's thickness + 0.1}; null when none.
- **WO-18 `bimIfsMesh(o, lv)`**: with BIM_IFS_CLASS (wall IfcWall, floor and slab IfcSlab, roof IfcRoof, stair IfcStair, beam IfcBeam, column IfcColumn, railing IfcRailing, ceiling IfcCovering, footing IfcFooting) just above it: null without mesh.v and mesh.f; verts [x + px, 0 - (z + pz), y + py]; each face of 3 or more fanned into triangles [f0, fj, fj+1]; null when none; level by the lowest y; cls bim.ifcType when it matches /^Ifc[A-Za-z]+$/, else the table's, else 'IfcBuildingElementProxy'.
- **WO-19 `bimIfsModel(objs, levels, name)`**: V177's data (its SPEC part 3): {name (or 'Project'), levels: [{name, elev}] (WO-12), walls, prisms, openings, meshes}; each solid into the first of walls (every segment), a slab or column prism, a mesh; openings (t 'opening') last against all walls.

## 6. Order of the work

WO-11 to WO-19 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-20** the wheels, the worker, file > export > ifc, make editable; **WO-21** the records.

## 7. Not in this phase

Editing imported elements beyond walls and slabs; ifc 4.3 output.
