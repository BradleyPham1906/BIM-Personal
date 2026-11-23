# Research: OpenCASCADE in the browser, for FreeCAD's solid modelling (F-OCCT)

Asked by the owner, 2026-11-22: FreeCAD's gaps through OpenCASCADE (option 2), "if we can bring any code that already
done then why not copy and paste". The order: the CADCraft list first, then this.

## 1. The question

Which build of OpenCASCADE (OCCT, FreeCAD's own geometry kernel) can this app ship under its third-party rule
(CLAUDE.md, "Third-party libraries"), to give it what FreeCAD's Part and PartDesign have and it lacks: fillets and
chamfers on solid edges, shell, draft, revolve, loft and sweep as solids, booleans on true solids, and STEP and IGES?

Hypotheses: H1 a maintained OCCT WebAssembly build exists with those operations; H2 it is LGPL-2.1, so it can ship only
as its own unchanged, replaceable file; H3 it costs under 10 MB compressed, loaded only when a solid tool is used.

## 2. What was read (2026-11-22)

| # | Source | What | Level |
|---|---|---|---|
| 1 | npm registry, `npm view` | versions, licences, sizes, dates of opencascade.js, replicad, replicad-opencascadejs, occt-import-js, @bitbybit-dev/occt | P (registry metadata) |
| 2 | replicad-opencascadejs 1.2.1 tarball | its two WebAssembly builds measured (raw and gzip -9), its LICENSE | P (measured here) |
| 3 | occt-import-js 0.0.23 tarball | its WebAssembly measured, its LICENSE | P (measured here) |
| 4 | replicad 1.2.1 tarball | `dist/replicad.d.ts`: its operations read from the type definitions; its LICENSE | P (read as text) |

Nothing downloaded was run. The operations below are as replicad declares them; none was tried here.

## 3. Findings

| | replicad 1.2.1 + replicad-opencascadejs 1.2.1 | opencascade.js 1.1.1 | occt-import-js 0.0.23 | @bitbybit-dev/occt 1.7.0 | Manifold (already shipped) |
|---|---|---|---|---|---|
| Licence | MIT (replicad) + LGPL-2.1-only (the OCCT build) | LGPL-2.1-only | LGPL-2.1 | MIT and Apache-2.0 and LGPL-2.1 with the OCCT exception | Apache-2.0 |
| Last release | 2026-11-06 | 2023-03-23 (stale) | 2024-12-03 | 2026-11-17 | in use |
| WebAssembly | 22.9 MB, **7.2 MB gzip** (single-threaded) | about 66 MB unpacked | 7.6 MB, 3.1 MB gzip | 102 MB unpacked | about 0.6 MB |
| Wrapper | 0.7 MB (CommonJS) | none | small | large | small |
| Fillet, chamfer on edges | yes | via raw OCCT | no | yes | no |
| Shell, draft | yes | via raw OCCT | no | yes | no |
| Extrude, revolve, loft, sweep | yes | via raw OCCT | no | yes | extrude, revolve only |
| Booleans on solids | yes (fuse, cut, intersect) | via raw OCCT | no | yes | yes (on meshes) |
| STEP in / out | importSTEP / exportSTEP | via raw OCCT | in only (STEP, IGES, BREP) | yes | no |
| IGES in | no declared function | via raw OCCT | yes | yes | no |

- **H1 holds:** replicad declares fillet, chamfer, shell, draft, extrude, revolve, loft, sweep, fuse, cut, intersect,
  `importSTEP`, `exportSTEP` and STL export, over its own OCCT build released two weeks ago.
- **H2 holds:** every OCCT build is LGPL-2.1. Under the rule it ships as its own unchanged file under `runtime/`, with its
  licence and a written offer of the source, loaded by the app's code only through an adapter. replicad itself is MIT.
- **H3 holds** for replicad's build: 7.2 MB compressed, fetched only the first time a solid tool is used. That is about
  the size of the Pyodide runtime the analyses already load on demand.
- **IGES:** replicad declares no IGES reader; occt-import-js (3.1 MB compressed, LGPL) reads STEP, IGES and BREP.

## 4. Recommendation

**replicad 1.2.1 with replicad-opencascadejs 1.2.1**, vendored and pinned as cc-ifc and cc-dwg are:
`runtime/occt/1.2.1/` holds the unchanged `replicad_single.wasm` and its loader with the LGPL licence and a source
offer, and replicad's MIT code is bundled by a `tools/occt/` build script into one classic script. The app calls it only
through `src/js/engine/solids/occt-adapter.js`, in a worker so a slow fillet cannot freeze the page. Optionally
occt-import-js later, for IGES.

First three things to build, once approved:
1. A sketch's closed outline to an OCCT face, extruded (PAD), and the solid turned back into the app's mesh. This
   proves the round trip.
2. FILLET and CHAMFER on a picked edge of that solid, and SHELL.
3. REVOLVE, LOFT and SWEEP from sketches, then `importSTEP` and `exportSTEP`.

## 5. Risks and what is open

- **Size:** 7.2 MB on first use. The app stays usable without it.
- **The solids' identity:** an OCCT solid is kept as its BREP text with the object, so it can be edited again after a
  reload. How large these get is not measured.
- **Not tested here:** that replicad's build loads in this app's page and from `file://`, and how fast a fillet runs.
- **The owner's approval** of replicad and replicad-opencascadejs is needed before anything is vendored (the rule).
- **FreeCAD's own code:** FreeCAD's sources are LGPL C++ and Python built on OCCT. They are not copied into the app's
  files, which are Apache-2.0. The same capability comes from OCCT itself, as above.

## 6. Built (V264, 2026-11-22), the owner's approval: "Yes go ahead"

- `runtime/occt/1.2.1/`: `bim-replicad.min.js` (replicad with flatbush, flatqueue, opentype.js; MIT and ISC; 373 KB),
  `replicad_single.js` and `replicad_single.wasm` (LGPL-2.1, unchanged, 22.9 MB), `OCCT-LICENSE`, `OCCT-SOURCE.md` (the
  source offer), `REPLICAD-LICENSE`; pinned in `runtime/MANIFEST.json` by `tools/occt/build_occt.mjs` (`--check`).
- `src/js/engine/solids/occt-adapter.js` (loading, the plan's frame, outlines counter-clockwise, meshes, the B-rep kept
  with a mesh signature) and `occt-tools.js` (EXTRUDE, FILLETEDGE, CHAMFEREDGE, SHELL, REVOLVE, LOFT, SOLIDUNION,
  SOLIDSUBTRACT, SOLIDINTERSECT, EXPORTSTEP, STEP import). It runs in the page, not in a worker: a box's fillet takes
  about 50 ms here.
- Measured in Node with the pinned files: loading 0.18 s; the volumes of an arc-sided extrusion, a circle, a fillet, a
  chamfer, a shell, a revolve, a loft and a STEP round trip all equal their closed forms (`tests/unit/occt.test.mjs`).
  In the page: `tests/e2e/bim_phase264_occt_check.mjs`, 14 of 14.
- Found on the way: an outline that runs clockwise in OpenCASCADE's plane extrudes into a solid turned inside out,
  whose booleans come out wrong; outlines are now always walked counter-clockwise.
- Still open: picking one edge under the cursor (edges are chosen as all, vertical, top or bottom); IGES; a worker;
  sweeps along a path; the app's other tools editing an OpenCASCADE solid as a B-rep (they change its mesh, after which
  it is no longer edited as a B-rep).
