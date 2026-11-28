# BimCraft's BIM-authoring core (V308)

`app/` is BimCraft (https://github.com/getcadcraft/bimcraft) at commit `79b603f6683f2f000b9e8346c1fc92cf466ab01d`
(2026-11-23), copied unchanged: the modules `tools/bimcraft/roots.mjs` names and every file they import (151 files),
with that repository's `LICENSE` (Apache License 2.0), `NOTICE`, `PROVENANCE.md`, `TRADEMARKS.md` and `THIRD_PARTY.md`.
Copyright 2026 The Data Design Group, Inc. `FILES.txt` lists each file with its SHA-256. Its names (CadCraft, BimCraft)
are their trademarks and are not used for this app (NOTICE; TRADEMARKS.md; Apache-2.0 section 6).

The owner, 2026-11-28: "copy their code ... reuse the codes, dont write new stuff". What it brings: parametric walls by
type with joins and assemblies, doors and windows by type with their plan symbols, floors, ceilings and roofs, rooms with
areas, curtain walls, levels, grids, families with parameters and formulas, phases, schedules, stairs, and the drawing
set: plans, elevations and sections projected from the model, sheets with title blocks at scale, PDF. It works on an IFC
model through BimCraft's own cc-ifc (`app/ifc/`, at the same revision as the rest, as BimCraft's tests run it).

- `tools/bimcraft/copy_upstream.mjs <clone>` copies it (`--check` proves this folder is the clone's files, unchanged).
- `tools/bimcraft/build_bimcraft.mjs` bundles it, unchanged, into `runtime/bimcraft/<rev>/bim-craft.min.js` (global
  `BIMCRAFT`), loaded only when the app needs it. Left out: manifold-3d (the app hands over the Manifold it already
  ships), and `tin.js` with delaunator and robust-predicates (terrain under a house, loaded only on demand upstream).
- Proof it runs in this app's runtime: `docs/research/experiments/bimcraft/e05/` builds BimCraft's own test house
  through the bundle and checks what their `house-test.mjs` checks, from numbers worked by hand.

Never edit these files by hand; to move to a newer revision, set `REV` in `tools/bimcraft/roots.mjs`, copy, rebuild, and
rerun e05.
