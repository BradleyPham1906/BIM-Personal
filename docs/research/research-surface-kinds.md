# V197: colours by surface kind, in both views

Research and build, 2026-11-12. Levels as in `research-protocol.md`: P primary, S secondary, U a pointer only.

## 1. The question

The owner's third of five after V194 (2026-11-12): roofs, walls, ground, water and trees each in their own colour,
in the shaded view and the rendered view (the look of the video the owner sent, V194's note section 4).

## 2. What the app already had (P, this repository at a183506)

- One colour an object: `bimSceneSync` (`render/gpu-batches.js`) writes each object's colour into the scene's table
  (8 floats a row: place, transparency, colour, selection); both engines and the rendered view read it.
- An object's kind is already recorded: Site Context's `o.context.kind` (buildings, roads, water, green, trees,
  rail, airports, power, landuse, terrain), `o.t==='terrain'`, a BIM element's `o.bim.type`, an IFC element's
  `o.bim.ifcType` (V196). glTF and SketchUp imports carry their own materials (`o.gltf`, `o.skp`).
- The colour lens (V136) and the Analyze workspace's quiet look (V171b) already override the colour, through
  `bimLensCol`; plot by layer turns the look off.

## 3. Hypotheses

- H1: roofs can be told from walls without new data. **Held** for map and city buildings: their faces looking up
  (normal's up part over 0.25, a slope under about 75 degrees) are the roof; tested on a box.
- H2: a roof colour can reach both views without changing either engine's shaders. **Held**: a building gets a
  second row in the table, its roof's; its upward triangles name that row. The rendered view reads triangles by row
  already, so it follows.
- Counter-case found: the rule must not apply to BIM or IFC elements (a wall's top looks up); they are coloured
  whole, by type.

## 4. The owner's decision (2026-11-12)

Both palettes, offered in View, Colours: Study model (light, calm) and Natural (realistic); own colours stay the
default. The setting is the project's (`A3D.site.colours`, saved with it), not the browser's.

| Key | Study model | Natural | Used for |
|---|---|---|---|
| walls | #f4f2ee | #e8e1d4 | map buildings, BIM and IFC walls |
| roofs | #b9bcc2 | #9c4f3c | building faces looking up, BIM roofs, IfcRoof |
| ground | #e7e1d3 | #c9b48a | terrain, IfcSite, IfcEarthworks |
| water | #9cc3e6 | #4f8fd6 | water |
| green | #b9d9a8 | #7cb36b | parks, grass |
| trees | #6fa86a | #3f7d3f | trees |
| roads | #d0cfcb | #8a8f98 | roads |
| glass | #bcd6e6 | #9fc4dc | BIM windows, IfcWindow, IfcCurtainWall, IfcPlate |

Derived here from those (not in the owner's preview): rail, airports, power, landuse (from roads and ground);
floor, door, structure (columns, beams, footings, members), stair (stairs, ramps, railings), ceiling (from walls and
ground). `render/surface-kinds.js` holds them.

## 5. As built

- `render/surface-kinds.js`: the palettes, an object's kind (`bimSkKey`), its colour (`bimSkCol`), the View row.
- `render/gpu-batches.js`: `B.roof`, a building's roof row, apart from `B.slots` (one row an object); each cached
  triangle notes whether it looks up; the roof row copies the object's row (place, transparency, selection) with the
  roof colour only when the palette chose the object's colour, so a lens or the Analyze look colours roofs too.
  Picking reads the roof rows; a removed building frees both.
- Order of colours everywhere: the lens (with the Analyze look), the palette, the object's own. Terrain in both
  views and the older drawing paths take the palette too.

## 6. Open

Roof faces of BIM roofs and IFC elements are whole-object colours. OSM's `roof:colour` and `building:colour` tags
are not read. Textures (brick, tiles) are not drawn. The app's own browser check has not been run.
