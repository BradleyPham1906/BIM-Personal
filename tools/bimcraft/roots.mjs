// tools/bimcraft/roots.mjs -- the BimCraft revision the app takes and the modules it starts from (copy_upstream.mjs
// copies them and everything they import; build_bimcraft.mjs bundles them, one namespace each).
export const REV = '79b603f6';
// what the app takes: walls and their joins and assemblies, openings and their families, slabs, roofs, curtain walls,
// levels, rooms, plan views and their graphics, sections of walls, families, phases, schedules, stairs; the writer; and
// the IFC model and editor they are tested on (ifc-model.js, ifc-edit.js) with cc-ifc at the same revision (ifc/api.js:
// BimCraft's tests drive ModelWriter with it, tests/tools/bimcraft-test/office-bim-test.mjs 10-17)
export const ROOTS = [
  'ifc/api.js', 'ifc-model.js', 'ifc-edit.js', 'model-write.js', 'model-walls.js', 'wall-joins.js', 'wall-assemblies.js', 'model-openings.js',
  'opening-types.js', 'model-slabs.js', 'model-roof.js', 'model-curtain.js', 'model-levels.js', 'model-rooms.js',
  'model-plan.js', 'model-planview.js', 'plan-symbols.js', 'wall-plan-graphics.js', 'wall-section-graphics.js',
  'family-model.js', 'family-symbol.js', 'phases.js', 'model-schedule.js', 'stair-family.js',
  // the operations a person uses (new building, walls, openings, floors, ceilings, roofs, rooms: new-model.js,
  // model-ops.js), grids, and the drawing set: views projected from the model (res-views.js), their notes
  // (comforts-views.js), sheets with title blocks, at scale, to PDF (res-sheets.js), text sized by the office standard
  // (anno-standard.js, anno-scale-bim.js), rooms' geometry (spaces-geom.js): what tests/tools/bimcraft-test/house-test.mjs
  // and make-small-house.mjs drive
  'new-model.js', 'model-ops.js', 'model-grids.js', 'res-views.js', 'res-sheets.js', 'comforts-views.js',
  'anno-standard.js', 'anno-scale-bim.js', 'spaces-geom.js'];
