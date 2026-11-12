# V196: full IFC import, and which engine reads it

Research, 2026-11-12. Levels as in `research-protocol.md`: P primary, S secondary, U a pointer only.

## 1. The question

The owner's second of five after V194 (2026-11-12): full IFC in. Today's `io/import-ifc.js` (269 lines) reads
storeys, and walls and slabs drawn as one vertical extrusion of a rectangle or polyline; everything else (doors,
windows, roofs, stairs, beams, columns, MEP, curved or sloped or B-rep geometry, openings, properties) is skipped.
The owner chose (2026-11-12) to decide the engine after research: web-ifc, or BimCraft's own reader.

## 2. Hypotheses

- H1: BimCraft's IFC engine (cc-ifc, `app/ifc/`) is its own code, not a wrapper of web-ifc. **Held** (P): its
  PROVENANCE.md says written from ISO 10303-21 and the buildingSMART schemas, with web-ifc used only as a test
  oracle; its 24 files import only each other (read here), with Manifold optional for openings.
- H2: cc-ifc reads real files as completely as web-ifc. **Held** on 13 files (e01, below): the same elements and the
  same model box on all 13; triangles within 2% on 12. Counter-evidence sought in the three differences; none was
  a fault (section 4).
- H3: web-ifc is much faster. **Mostly false** (e01): both open a 49 MB file in about a quarter of a second and
  mesh it in under half a second; the one exception is a file of curved B-reps, where cc-ifc samples 20 times finer
  than it needs to (6.5 s against 0.4 s).
- H4: either engine can serve one adapter. **Held** (P): cc-ifc copies web-ifc's `IfcAPI` calls and value shapes
  ("so switching an app is one import", `api.js` lines 4 to 6); e01 drives both through the same code.

## 3. Search log

- getcadcraft/bimcraft @ cfbd948: PROVENANCE.md, THIRD_PARTY.md, `app/ifc/` (file list and sizes by the GitHub API;
  `api.js`, `geo-bool.js`, `geo-curve.js`, `geo-nurbs.js` read), cloned sparse here.
- web-ifc 0.0.79 and manifold-3d 3.5.4 from npm (licence fields, package contents, sizes); run here.
- Test files: buildingSMART/Sample-Test-Files (8 small files, IFC2x3, IFC4, IFC4.3), KIT's FZK-Haus, and four large
  models from web-ifc's own test set. Not committed (their licences are not stated); URLs and SHA-256 in
  `experiments/v196-ifc/results.txt`.

## 4. Experiment e01 (`experiments/v196-ifc/`)

`run.mjs` opens each file with both engines through the same calls and streams every mesh: elements drawn,
triangles, the model's box in metres, time. `probe*.mjs` look into the differences.

| File | Size | Elements (web-ifc / cc-ifc) | Triangles | Open + mesh ms |
|---|---|---|---|---|
| 8 buildingSMART samples, 2x3 to 4.3 | 12 KB to 1.7 MB | equal on all 8 | within 0.4% | both under 50 |
| FZK-Haus | 2.6 MB | 83 / 83 | 21,650 / 21,684 | 95 / 85 |
| dental_clinic | 13 MB | 2,586 / 2,586 | 174,319 / 168,703 | 286 / 389 |
| FM_ARC_DigitalHub | 14 MB | 705 / 705 | 307,228 / 3,220,891 | 468 / 6,534 |
| advanced_model | 35 MB | 6,401 / 6,401 | 1,263,873 / 1,349,174 | 725 / 1,090 |
| schependomlaan | 49 MB | 3,569 / 3,504 | 261,321 / 261,457 | 557 / 616 |

The model box agrees to the millimetre on all 13 files. The three differences, looked into:

- **FM_ARC_DigitalHub, 10 times the triangles.** The densest elements are doors and proxies made of
  `IfcAdvancedBrep` (NURBS faces). Their surface areas agree (a door: 5.720 m2 by web-ifc, 5.715 by cc-ifc), so
  web-ifc lost no faces (its 51 "TriangulateBounds" errors, all on this file, were harmless) and cc-ifc only samples
  finer: `geo-nurbs.js` line 403 spaces points to turn the normal by 0.2 rad, down to a 96th of the face. One
  constant; an adapter or a one-line local change can coarsen it. The app's import cap (V195) is 300,000 triangles.
- **schependomlaan, 65 fewer elements.** All are walls and proxies named "kozijn" (window frame) that lie wholly
  inside their own openings; cc-ifc cuts them away and says so in its notes. web-ifc streams them with an area of
  0 m2, so neither draws them: the same picture.
- **Openings need Manifold.** cc-ifc without it: the wall with a window draws 24 triangles, not 44 (the hole is not
  cut). Manifold (Apache-2.0) is a 541 KB WebAssembly file.

## 5. The two engines compared

| | web-ifc 0.0.79 | cc-ifc (BimCraft cfbd948) + Manifold 3.5.4 |
|---|---|---|
| Licence | MPL-2.0 (shipping it unchanged is allowed, with notice and a link to its source; changes to its own files must be shared under MPL) | Apache-2.0, both (as three.js's credit) |
| What it is | C++ compiled to WebAssembly, by That Open Company | JavaScript, ES modules; Manifold is WebAssembly |
| Download | 6.1 MB script + 1.7 MB wasm; about 1.1 MB compressed | 617 KB script (bundled here) + 624 KB Manifold; about 0.39 MB compressed |
| Opened from a file (`file://`, the offline build) | Cannot load its wasm, so reads nothing (as V195's Draco) | Reads everything; openings are not cut unless Manifold's wasm loads |
| Completeness on e01 | reference | the same elements and box on 13 of 13 |
| Speed on e01 | faster on curved B-reps | the same order elsewhere; 14x slower on curved B-reps until coarsened |
| Schemas | IFC2x3, IFC4, IFC4.3 | IFC2x3, IFC4, IFC4.3 (its schema files) |
| Can we fix it | through its C++ build only | in JavaScript, as a pinned copy |
| Track record | widely used (That Open's viewers) | one project's engine, tested against web-ifc |

Either way it is another pinned runtime, loaded only when an IFC file is opened, as three.js was (V194): a change
to the "no dependencies" contract that the owner approves. Either way the adapter is the same, so the choice can be
changed later in one loader line. Today's `import-ifc.js` stays as the fallback when the runtime cannot load.

## 6. Recommendation, and the owner's decision

cc-ifc with Manifold: Apache-2.0, a third of the download, works offline except for cutting openings, and in
JavaScript we can fix and tune ourselves; e01 found it as complete as web-ifc on every file tried. Its one
measured weakness, curved B-reps sampled too finely, is one constant. web-ifc stays the test oracle, as BimCraft
uses it.

**The owner chose cc-ifc (2026-11-12).**

Tuning tried after the choice: the curved-door model with coarser sampling (`ext / 48`, 0.35 rad; `ext / 24`, 0.5 rad)
went from 6.5 s to 3.5 s and 2.8 s, while a proxy's area fell from 2.37 to 2.29 and 2.08 m2 (web-ifc 2.42). Not
worth the lost detail; cc-ifc is shipped unchanged.

## 7. As built (V196)

- `vendor/cc-ifc/` (upstream `app/ifc/` unchanged, with LICENSE, NOTICE, PROVENANCE.md); `tools/ifc/build_ifc.mjs`
  bundles it with Manifold's loader into `runtime/cc-ifc/cfbd948/bim-ifc.min.js` (662,318 bytes, global `BIMIFC`),
  `manifold.wasm` beside it; five entries in `runtime/MANIFEST.json`.
- `io/ifc-full.js`: the runtime is loaded on the first IFC (beside the page from a file://, then the site with SRI);
  each element is one welded mesh in metres, +Y up, in the colour covering most of its opaque pieces, its outline
  from V195's `mesh.fe`; a locked solid on a layer for its class (IfcWallStandardCase as IfcWall) under one named
  after the file, see-through elements on a sub-layer; storeys as levels; `o.bim` holds `ifcType`, `guid`,
  `storey`, `psets` (40 sets of 80 values at most); Properties shows them. Up to 1,500,000 triangles.
- The walls-and-slabs reader (`import-ifc.js`) is used when the runtime cannot be loaded. Its recovery of simple
  walls as editable walls is not done by the new reader: imported walls are locked solids.
- Node, the full read with property sets: FZK-Haus 0.2 s, dental_clinic 0.8 s, schependomlaan 1.5 s (every
  element on a storey), advanced_model 2.7 s (6,401 elements, 1.35 million triangles).

## 8. Open

Writing IFC (Hub H3) was not tried with either engine. A window's glass and frame are one object in one colour. Georeferencing (`IfcMapConversion`) read but not placed on
the map. Files over about 100 MB not tried. Threads (a worker) not tried; a 35 MB file takes about a second.

## 9. Sources

P: getcadcraft/bimcraft @ cfbd948 (PROVENANCE.md; THIRD_PARTY.md; `app/ifc/api.js` 1 to 120, `geo-bool.js` 1 to
40, `geo-curve.js` 20 to 25, `geo-nurbs.js` 380 to 425), read 2026-11-12. P: npm web-ifc 0.0.79 (MPL-2.0) and
manifold-3d 3.5.4 (Apache-2.0), run here. P: this repository's `io/import-ifc.js` at 961fc20. Experiment e01 (P),
2026-11-12. Second reading by an independent reviewer: not yet done.
