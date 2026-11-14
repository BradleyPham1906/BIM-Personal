

  /* ================= __acad3dV177: Save as IFC, the pure part =================
     docs/research/research-ifcopenshell-app.md (the owner's D1 to D4, 2026-11-14) and docs/work-orders/v177/SPEC.md.
     The app's model as the plain model src/py/bim_ifcos.py's bim_ifcos_save_model writes as IFC4: levels, walls by
     straight segment, floors as slabs, rectangular columns, doors and windows on their walls, every other solid as a
     mesh. Plan points [x, z] become IFC [x, -z]; heights stay y. Each function is a work order in
     docs/work-orders/v177/TASKS.md, added below as it is built; none uses a name from another file. */
