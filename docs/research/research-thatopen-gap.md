# That Open, all of it: what the app lacks, what V206 brought in, and the plan to close the rest

Research and integration, 2026-11-28. Levels as in `research-protocol.md`: P primary, S secondary, U a pointer only.
The owner (2026-11-24): "i need you to establish researches and plug their code to our. what are we missing and i want
to close that gap with openBIM their repos ... i want to actually catch up with that repo." This note is the synthesis;
the evidence is in four part notes, three experiments and an independent check:

| Part | What it covers | File |
|---|---|---|
| Core components | 25 components of `@thatopen/components` (BCF, IDS, Classifier, Hider, ItemsFinder, Clipper, Views, Viewpoints, EdgeProjector, DXF...) | `research-thatopen-gap/components-core.md` |
| Front and UI | 28 rows: Highlighter, Hoverer, Outliner, the four measurements, postproduction, ClipStyler, point clouds, splats, civil, `@thatopen/ui` panels | `research-thatopen-gap/components-front-ui.md` |
| Fragments and web-ifc | The data model, importer, editor, the geometry kernel's coverage, the writer, releases since 0.0.79, the import recipe | `research-thatopen-gap/fragments-webifc.md` |
| Authoring and openBIM | engine_clay, engine_templates, and the app's element model against IFC practice (identity, types, layers, Psets, spaces, joins, classification, georeferencing) | `research-thatopen-gap/authoring-openbim.md` |
| Independent check | Every fact the new code uses, re-read and re-run by a second reader | `research-thatopen-gap/second-reader.md` |
| Experiments | e02 (That Open drawn on the app's three, from file://), e03 (the import, That Open against cc-ifc on 13 files), the parts' own | `experiments/thatopen/e02/`, `e03/`, `experiments/thatopen-gap/` |

The first research, `research-thatopen.md` (2026-11-13), and the owner's four decisions of that day stand: That Open
as an on-demand Review view beside the app's own engine (B), on the app's own three.js without its WebGPU paths, and
That Open also for IFC import, cc-ifc retired once the new import matches it.

## 1. Abstract

That Open Engine is a viewer and coordination toolkit of high quality, not an authoring engine: none of its fifteen
public repositories writes a BIM model with rules (walls that join, hosted openings, types). The one modelling library,
engine_clay, stopped in October 2024 on versions the current libraries cannot load, and its IFC output has faults
(36-character GlobalIds, a member written as a plate, an area unit for volumes). So "catching up with That Open" has two
halves. **Its viewing, coordination and IFC reading** are taken as code: since V206 the app ships That Open 3.6
(components, components-front, fragments) and web-ifc 0.0.79 pinned in `runtime/thatopen/3.6.0/`, loaded only when
needed, working offline from `file://`; the Review view and the IFC import run on it, and match V196's reference on
all 13 test files. **Its standards discipline** (every element an IFC entity with a lasting GlobalId, types, Psets,
relations) has to be built into the app's own model, because no That Open code does that for an authoring app; the
plan is OB1 to OB8 (part 4). Between the two, 14 coordination features (BCF, IDS, per-element hide and isolate,
queries, classification groups, several section planes, viewpoints...) are missing or partial; each is placed in the
plan as reuse in Review, a port into the editable model, or both.

## 2. The question and the hypotheses

What does That Open have that the app lacks, which of it can be taken as code under the library rule, and what must be
built? Hypotheses, set before the work:

- H1: That Open can be shipped under the rule (pinned, on demand, offline, behind an adapter). **Held** (P, e02, e03):
  three files in `runtime/thatopen/3.6.0/`, 2.0 MB compressed, every package's licence allowed (31 packages, MIT, ISC,
  BSD, Apache-2.0, MPL-2.0 for web-ifc as its own file; `LICENSES.txt`).
- H2: That Open's IFC import can replace cc-ifc without losing anything V196 reads. **Held** (e03): 12 of 13 files
  agree element by element and class by class, with every GlobalId; the 13th is one where That Open reads more
  (cc-ifc stops at the triangle cap). **Counter-evidence found:** it is 2.5 to 5 times slower on large files.
- H3: Some That Open repository can serve as the app's authoring engine. **False** (P): Clay is stale and faulty
  (`authoring-openbim.md` part 4); components and fragments edit fragments, not elements with rules.
- H4: The app's own model is already IFC-ready apart from a few fields. **False** (P): authored elements get new
  GlobalIds at every save (`io/ifc-save.js:80`), types, Psets, Qtos, layer sets, spaces, joins and classification
  are not written (`authoring-openbim.md` part 6).

## 3. Method

Pinned clones of the six of ThatOpen's fifteen public repositories that hold the engine (engine_components @ 6bedaa4, engine_fragment @ 643d24e,
engine_web-ifc @ 9ab7d5c, engine_ui-components @ cd91b3f, engine_templates @ 1b30524, engine_clay @ 6f14cbe), read as
text, never run; the npm packages pinned in `tools/thatopen/package.json` and their `dist` and `.d.ts` read; four
research agents in parallel, one per part, each with the protocol's levels; the app's own code read by grep, file and
line. Experiments here: e02 (`experiments/thatopen/e02/`), e03 (`e03/`), and the parts' own
(`experiments/thatopen-gap/`). A separate agent re-read and re-ran every fact the new code uses (`second-reader.md`).
No web search: every fact is P from source, `.d.ts`, npm metadata or a run.

## 4. What V206 brought in (built, measured)

| Piece | Where | Evidence |
|---|---|---|
| That Open 3.6 and web-ifc 0.0.79 as three classic scripts on the app's three.js, licences beside them, pinned by size and SHA-256 | `tools/thatopen/build_thatopen.mjs`, `runtime/thatopen/3.6.0/`, `runtime/MANIFEST.json` | `tools/check_runtime.py`; unit test: the loader's SRI equals the manifest's |
| The loader: on demand, beside the page from a disk, then the site with SRI; the wasm through a fetch wrapper; the classic worker | `io/thatopen-runtime.js` (`bimToeLoad`) | e02: http and file:// alike, no errors |
| The IFC import through That Open: meshes per element in metres, +Y up, GlobalIds, storeys as levels, property and quantity sets, colours, the shift for Make editable; cc-ifc, then the walls-and-slabs reader, as fallbacks | `io/thatopen-runtime.js` (`bimToeRead`), `io/ifc-full.js` (`bimIfcReadAny`), pure helpers in `io/ifc-review.js` | e03: 12 of 13 agree, the 13th better; Make editable on a That Open import stands in place (browser check) |
| The Review view: several IFC files at once; select for IFC data; section planes; length and area (area cross-checked by `bimTorArea`, the section counted by `bimTorClip`); hide, isolate, show all; a storey and class tree with visibility; Import | `io/thatopen-review.js`, `css/workspace/review.css`, command REVIEW | `tests/e2e/bim_phase206_review_check.mjs`: 18 of 18, over http and from file://, desktop and phone |
| Audit of Cline's WO-01 to WO-07 | `io/ifc-review.js` | WO-03, WO-04 used BigInt (not ES5: the whole engine would fail to parse without it): rewritten; WO-01 swaps axes for Z-up input, but That Open's output is already +Y up, so the import does not use it (part 10) |

What the measurements say about cost: the bundle is 775 KB compressed, web-ifc 403 KB, its wasm 847 KB, all fetched
once, only on the first IFC import or REVIEW. The import is 0.2 to 0.9 s on small files, 4 to 13 s on 13 to 49 MB
files (cc-ifc 1.3 to 4 s), the time being That Open's conversion to fragments.

## 5. The whole gap, by area

Gap: NONE (the app has it at least as well), PARTIAL, MISSING. Close by: R (That Open's code in Review, now possible),
P (a port into the app's ES5 engine, for the editable model), R+P (both). Effort S, M, L. Rows with NONE are in the
part notes; the app already matches or beats That Open on grids, picking, snapping, shadows, boxes, technical
drawings and sheets, DXF, mesh export.

| Area | Feature | Gap | Close by | Effort | Part note |
|---|---|---|---|---|---|
| IFC reading | Read IFC2x3, IFC4, IFC4.3 into the editable model | NONE since V206 | done (R) | - | fragments-webifc 5 |
| IFC reading | Federated review of several large models, fast | NONE since V206 | done (R) | - | components-core |
| IFC reading | Type objects' property sets, materials, georeferencing (IfcMapConversion) on import | MISSING | R (fragments has them) | S | fragments-webifc 4 |
| Identity | GlobalIds that last across saves for authored elements, segments, openings, storeys | MISSING | P (OB1) | M | authoring-openbim 9 |
| Authoring | IFC class and predefined type at creation | PARTIAL | P (OB2) | S | authoring-openbim 9 |
| Authoring | Types written as IfcWallType and kin, shared by instances | MISSING | P (OB3) | M | authoring-openbim 9 |
| Authoring | Material layer sets | MISSING | P (OB4) | M | authoring-openbim 9 |
| Authoring | Standard Pset_*Common and Qto_* sets | MISSING | P (OB5), names from the pinned templates (e1) | M | authoring-openbim 8, 9 |
| Authoring | One IfcBuilding per building; rooms as IfcSpace | PARTIAL | P (OB6) | M | authoring-openbim 9 |
| Authoring | Wall joins and hosting as relations; openings that follow their wall (Clay's nester) | PARTIAL | P (OB7) | M | authoring-openbim 4.3, 9 |
| Authoring | Classification with system and edition; georeferencing written | PARTIAL | P (OB8) | M | authoring-openbim 9 |
| Coordination | BCF 2.1 and 3.0 topics, comments, viewpoints, .bcfzip | MISSING | R in Review now; P (`io/bcf.js`) for the model | L | components-core 3 |
| Coordination | IDS 1.0 checking | MISSING | P (`io/ids-check.js`): That Open's checker has faults (two facets do not test, applicability united, max overwrites min) | L | components-core 3 |
| Coordination | Queries over properties (ItemsFinder) | MISSING | P, with numeric bounds That Open lacks | M | components-core 3 |
| Coordination | Classification groups by class, storey, rule (Classifier) | PARTIAL | P (`bim/groupings.js`) | M | components-core 3 |
| Coordination | Hide, isolate, toggle single elements (Hider) | MISSING in the model (done in Review) | P | S | components-core 3 |
| Coordination | Viewpoints with selection, visibility exceptions, colours, snapshot | PARTIAL | P (saved views) | M | components-core 3 |
| Views | Several section planes, a plane on a picked face, a section box | PARTIAL (one capped plane) | P (done in Review: R) | M | components-core 3 |
| Views | View depth (far plane), orthographic 3D, plan views per storey | PARTIAL | P | S to M | components-core 3 |
| Views | Section styles per class (ClipStyler) | MISSING | P | M | components-front-ui 3 |
| Display | Hover pre-highlight, highlight styles with priority, outlines | MISSING / PARTIAL | P | S, M, M | components-front-ui 3 |
| Display | Pen and ambient-occlusion styles (postproduction) | MISSING | P | L | components-front-ui 3 |
| Measuring | 3D length, area, angle, volume on model surfaces in the editable model | PARTIAL (plan only) | P (done in Review for length and area: R) | M | components-front-ui 3 |
| Reality | Gaussian splats drawn (V205 left them undrawn), PLY and SOG | MISSING | R in Review (SplatLoader) or P | M | components-front-ui 3 |
| Reality | Streamed Potree point clouds, eye-dome lighting; E57 | MISSING | R (potree-core, MIT) / P (E57 reader) | M | components-front-ui 3, components-core 3 |
| Civil | IfcAlignment import, cross-section at a station | MISSING | R in Review (CivilNavigators) | M | components-front-ui 3 |
| Writing | web-ifc's writer for saving an imported IFC back with edited properties | MISSING | R, checked by IfcOpenShell's validator | M | fragments-webifc 6 |

## 6. Alternatives for the authoring half, compared

From `authoring-openbim.md` part 7, criteria set first (standard conformity, keeps what works, offline, effort):
A. adopt Clay as the model (stale, faulty, needs fragments 2.x: no); **B. the app's JSON model with an IFC identity and
relations kept as data, written by the IfcOpenShell already shipped (recommended)**; C. web-ifc's writer as the
model's store (writes no checks: e1 saved a wall without a GlobalId); D. IfcOpenShell as the live model in the worker
(every edit a message round trip; the app's tools all rewritten). B keeps every tool working and reaches Revit's
practice element by element.

## 7. Edges and risks

- Speed: That Open's import is 2.5 to 5 times slower than cc-ifc on large files (e03). The fragments note's route
  (IfcImporter then a single-threaded model, no worker round trips) may recover some; measure before deciding.
- `lastPick`: the Review view waits for That Open's measuring pick through a field its types mark protected; if it
  goes, the view waits 800 ms instead (no error). Re-run the browser check at each update.
- Churn: That Open releases every few weeks; the pins stay until a re-run of e02, e03 and the browser check passes.
- One browser (Chromium 158, SwiftShader); no Safari, Firefox or a real phone yet.
- The fetch wrapper for the wasm and the classic worker rely on behaviour the library allows but does not document.

## 8. What is still open

- Safari, Firefox and a real phone, from file:// and over http.
- Memory on files over 50 MB (the largest here, 49 MB, imported in 13 s).
- BCF 3.0 and IDS 1.0 schemas read in full (U in the core note).
- Whether ui-obc runs on three 0.186.1 (its peer is 0.185.0): needed only if its Lit panels are mounted in Review.

## 9. Prior art

ifc-viewer-online (MIT, on That Open; `research-thatopen.md`), That Open's own engine_templates (viewer starter: load,
highlight, clip, measure, viewpoints), BlenderBIM/Bonsai (IfcOpenShell as the authoring model: option D's shape).

## 10. Notes on the work orders

- SPEC 5 WO-01 `bimTorMesh` assumes Z-up input; fragments and web-ifc already give +Y up (P: web-ifc
  `geometry.h` 341-345; e02). It stays as written for Z-up sources and is not on the import's path.
- The class names, the space skip, the IFC4.3 facility parts and the id formatting were found by e03 and each has a
  unit test (`tests/unit/thatopen.test.mjs`).

## 11. The owner's decisions (to ask together)

1. cc-ifc: the condition of 2026-11-13 is met (12 of 13 agree, the 13th better). Retire it now (one IFC reader, 1.1 MB
   less in `runtime/`), or keep it as the fallback because it is 2.5 to 5 times faster on large files? Recommended:
   keep it one phase more while the single-threaded route is measured, then retire.
2. The plan's order (part 5): OB1 (lasting GlobalIds) first, then BCF and IDS in Review, then OB2 to OB8 and the ports.
   Recommended: OB1 to OB3 first (identity, class, types are what every openBIM exchange checks), BCF next.
3. Authoring approach B (part 6). Recommended: B.
4. Written schema: IFC4 only, or IFC4X3 as well. Recommended: IFC4 now, IFC4X3 with OB8.
5. Predefined types and standard properties edited on the type only, or per instance too. Recommended: both, the
   instance overriding (Revit's practice).
6. Wall layers: which functions first (finish, structure, insulation, membrane, air gap), layers in plan cuts later.
7. Classification systems first (Uniclass 2015, OmniClass), once their licences are read.
8. BCF and IDS: That Open's code in Review now and our own ES5 ports for the model later, or ports only.
   Recommended: Review now for BCF; our own IDS checker (That Open's has faults).
9. web-ifc 0.0.81 (geokernel booleans on by default, sections, polylines): move now or stay on 0.0.79 until e03 is
   re-run on it. Recommended: re-run, then move.
10. Unstyled elements: That Open's white or V196's grey. Recommended: grey (the import's look stays as it was).
11. Point clouds and splats through That Open in Review (potree-core, MIT, as an optional file), given V205's splats
    are not drawn (`components-front-ui.md`).
12. Footing-to-host relation written or not; elements on hidden layers exported or not (`authoring-openbim.md` 11).

## 12. References

- ThatOpen/engine_components @ 6bedaa4, engine_fragment @ 643d24e, engine_web-ifc @ 9ab7d5c, engine_ui-components @
  cd91b3f, engine_templates @ 1b30524, engine_clay @ 6f14cbe, https://github.com/ThatOpen. Read 2026-11-28. P.
- npm @thatopen/components 3.6.0, components-front 3.6.1, fragments 3.6.1, web-ifc 0.0.79 and 0.0.81, camera-controls
  3.1.2, potree-core 2.0.17 (`npm view`, installed `dist` and `.d.ts`). 2026-11-28. P.
- buildingSMART/Sample-Test-Files (main), KIT FZK-Haus, web-ifc's test files: the 13 of V196, hashes in
  `experiments/v196-ifc/results.txt`. Data.
- IfcOpenShell 0.8.5's wheel in `runtime/` (guid.py, the Pset templates), read as text. P.
- This repository: `research-thatopen.md`, `research-ifc-engine.md`, `research-ifcopenshell-app.md`, the files named
  in part 4. P.
