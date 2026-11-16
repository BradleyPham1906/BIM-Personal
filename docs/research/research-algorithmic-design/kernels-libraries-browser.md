# Algorithmic design: geometry kernels, node-editor libraries and browser limits

Side note for `docs/research/research-algorithmic-design.md`. Question and hypotheses: `00-question.md` (H4, H7 and
the library side of the node editor). Researched 2026-11-14 and 2026-11-15. Upstream code was read as text only:
npm tarballs were downloaded with curl, listed, unpacked and read; nothing was installed, built or run.

Levels: P = read at the source; P-wf = the source page read through the fetch tool, which returns a digest (GitHub's
HTML refuses scripts here); S = dependable secondary; U = not verified. Confidence high / medium / low.

## 1. Summary of findings

| # | Finding | Level | Confidence |
|---|---|---|---|
| 1 | **Manifold** (`manifold-3d` 3.5.5, 2026-11-13, Apache-2.0): `manifold.wasm` 542,744 bytes (204,769 gzip -9) plus `manifold.js` 82,371 (19,098). It fits the app's library rule. It is single-threaded in the npm build (no pthread or SharedArrayBuffer in the glue) and takes its binary from memory (`Module.wasmBinary`), so it can be embedded as the repo's e01 did | P | High |
| 2 | Manifold's glue is an ES module (`export default Module`, `import.meta.url`), not a classic script. The adapter must start it in a module context (a Blob-URL module worker or `import()` of a Blob URL) or re-wrap it at vendoring time. Not tested here | P (the code), U (which route works from `file://` in each engine) | High / low |
| 3 | Manifold's guarantee is topological: manifold output from manifold input, by construction. It is not a guarantee of geometric validity: that is a goal, "cannot be mathematically proven", and degenerate triangles may remain. Input must already be manifold, which the app's meshes are not known to be | P (its wiki) | High |
| 4 | **OCCT** in the browser stays 22 to 50 MB (replicad-opencascadejs 1.2.1: 22,942,327 bytes), LGPL-2.1, about 42 times Manifold. `opencascade.js` itself is dormant (latest tag 2020; beta untouched since 2023-03). replicad (MIT wrapper) is alive (1.2.1, 2026-11-06) | P | High |
| 5 | **Clipper2** is BSL-1.0, a permissive licence that needs its notice kept in source copies and nothing for object code; it is not in the app rule's list (MIT, BSD, ISC, Apache-2.0, MPL-2.0) by name, so the owner would have to add it. `clipper2-ts` 2.0.1-19 is a pure-TypeScript port with no dependencies (min build 123,355 bytes, 33,396 gzip), covering booleans, offsets and triangulation | P | High (licence text and package); the compatibility reading is ours |
| 6 | The npm package `straight-skeleton` 3.0.0 says MIT but is a 1.03 MB wasm wrapper of **CGAL's** straight skeleton, and CGAL lists that package as GPL. It could ship only as a separate program in a worker. Its v1 branch is pure TypeScript, "less robust" by its own README | P (README, bundle), P-wf (CGAL's package list) | High |
| 7 | Pure-JS mesh CSG adds little over the app's own: csg.js and @jscad/modeling are BSP booleans with the same `1e-5` plane epsilon as `csg-booleans.js`; three-bvh-csg warns its results "may not be" two-manifold and points to Manifold | P | High |
| 8 | **Node editors.** Only three candidates need no framework and ship a classic script: litegraph.js 0.7.18 (MIT, 176 KB min, canvas, own engine, last release 2024-01), Drawflow 0.0.60 (MIT, 46 KB, DOM, no engine, last release 2024-09) and Rete's core (needs a render plugin tied to React, Vue, Angular, Svelte or Lit). None is ES5 throughout, none is a clear fit for touch: litegraph's touch issue (#18) has been open since 2018 and its code still says "touch events -- TODO IMPLEMENT" | P (code), P-wf (issues) | High for the code; medium for the issue states |
| 9 | The ComfyUI fork of litegraph was archived and merged into ComfyUI's front end (2025-08-05); it is TypeScript, "largely incompatible with the original", and no longer a separate library | P-wf, P (registry: last version 2025-08-06) | High |
| 10 | **Browser platform.** Of the pasted advice, SharedArrayBuffer, OPFS and a service worker all fail from `file://`; a Blob-URL worker, transferable buffers, WebAssembly from bytes and IndexedDB work (Chromium measured by the coordinator, e05; MDN and Bugzilla for the rules) | P | High for Chromium; medium for Firefox; low for Safari (not measured) |
| 11 | On GitHub Pages the page is a secure context, so OPFS and a service worker work, but there are no COOP/COEP headers, so no SharedArrayBuffer unless a service worker adds the headers and reloads the page (the coi-serviceworker technique) | P (MDN, e05 "http, no headers"), S (coi-serviceworker's README for Pages) | High |

## 2. Findings by topic

### 2.1 Package facts read from the npm registry and the tarballs (P, 2026-11-14)

All tarballs fetched from `registry.npmjs.org` with curl; sha1 equals the registry's `dist.shasum` in each case.
gzip is `gzip -9`, measured here.

| Package, version, date | Licence (package.json) | Tarball bytes | Tarball sha256 (first 16) | Files that matter, bytes |
|---|---|---|---|---|
| manifold-3d 3.5.5, 2026-11-13 | Apache-2.0 (LICENSE read) | 722,143 | 79854f081b95a552 | `manifold.wasm` 542,744 (gzip 204,769; sha256 b172438703ef72de...); `manifold.js` 82,371 (gzip 19,098); `manifold.d.ts` 61,470; `dist/worker.bundled.js` 1,734,944 (manifoldCAD's worker, optional) |
| replicad-opencascadejs 1.2.1, 2026-11-06 | LGPL-2.1-only | 15,093,004 | 07b6fb17a26a0be2 | `replicad_single.wasm` 22,942,327; `replicad_single.js` 60,483; `replicad_multi.wasm` 22,475,349 |
| replicad 1.2.1, 2026-11-06 | MIT | 1,374,735 | 8c4ce4dc6d7e4575 | `replicad.js` 708,324; depends on flatbush, opentype.js |
| opencascade.js 1.1.1, 2020-09-27 (latest); beta 2.0.0-beta.b5ff984 | LGPL-2.1-only | not downloaded | | `research-usd-brep.md` 4.8: the beta's wasm is 50,305,130 bytes |
| @jscad/modeling 2.13.0, 2026-02-22 | MIT | 340,124 | cc86485bb3e48dba | `dist/jscad-modeling.min.js` 250,793 (gzip 58,962); no dependencies; not ES5 (classes, arrow functions) |
| three-bvh-csg 0.0.18, 2026-02-17 | MIT | 221,467 | 9cfc598742c8a072 | `build/index.umd.cjs` 169,425 (gzip 33,893); peers: three, three-mesh-bvh |
| three-mesh-bvh 0.9.18, 2026-11-03 | MIT | 434,105 | b041bf9ab59b90ca | peer: three |
| clipper2-ts 2.0.1-19, 2026-11-07 | BSL-1.0 | 378,007 | e437fd35f7ac6533 | `dist/clipper2.min.mjs` 123,355 (gzip 33,396), ES module only; no dependencies |
| clipper2-wasm 0.4.0, 2026-05-18 | BSL-1.0 | 429,138 | 22b3afe094024bd1 | `dist/umd/clipper2z.wasm` 213,643; `clipper2z.js` 54,145; no SharedArrayBuffer |
| clipper-lib 6.4.2, 2019-11-08 (Clipper 1) | BSL | 49,682 | 634d7d7627939bbe | `clipper.js` 203,786 (gzip 44,489), one classic script, no classes |
| polygon-clipping 0.15.7, 2023-12-18 | MIT | 91,226 | 23bdea671a650111 | `dist/polygon-clipping.umd.min.js` 29,106; booleans only, no offset |
| straight-skeleton 3.0.0, 2026-03-24 | MIT in package.json; wraps CGAL (GPL) | 681,235 | 66ab400f389445f9 | `dist/index.js` 1,034,461 with the wasm embedded |
| earcut 3.2.4, 2026-09-28 | ISC | 34,818 | 2f63624cc056e4f2 | `dist/earcut.min.js` 9,749; no classes or arrow functions |
| verb-nurbs 3.0.3, 2025-04-23 | MIT | not re-downloaded | | `research-usd-brep.md` 4.8: `build/js/verbHaxe.js` 278,479 bytes, ES5; no release since |
| litegraph.js 0.7.18, 2024-01-08 | MIT | 660,475 | a951ff79919b4e5f | `build/litegraph.core.min.js` 176,325 (gzip 47,885); `litegraph.min.js` 491,365 (with node packs); `css/litegraph.css` 12,820 |
| @comfyorg/litegraph 0.17.2, 2025-08-06 | MIT | 869,481 | 21c459056519b033 | `dist/litegraph.umd.js` 402,538 (gzip 97,617) |
| rete 2.0.6, 2025-06-30 | MIT | 47,958 | 3fb8b51360eae433 | `rete.min.js` 18,496 (core data model only); rete-area-plugin 2.3.2 (2026-07-08) and rete-engine 2.1.1 (2024-12-27) are separate, MIT |
| drawflow 0.0.60, 2024-09-03 | MIT | 15,497 | e587758f8c4e8e02 | `dist/drawflow.min.js` 46,190 (gzip 8,653); `drawflow.min.css` 1,910 |
| baklavajs 2.8.1, 2025-11-02 | MIT | 294,216 | 88d7ef9e156fdc42 | `dist/bundle.js` 175,784; renderer is Vue (`@baklavajs/renderer-vue`) |
| @xyflow/react 12.12.1, 2026-11-02 | MIT | 251,321 | ffd8b20eff216ceb | `dist/umd/index.js` 188,872; requires react, react-dom |
| flume 1.2.0, 2025-11-05 | MIT | 367,654 | 1c5565a79d99551b | `dist/index.js` 299,779; peers react, react-dom |

### 2.2 What the repo already established (cited, not repeated)

- `docs/research/research-usd-brep.md` (2026-10-31 to 11-01): OCCT builds 23 to 50 MB; Manifold 541 KB, mesh only;
  SMLib (Apache-2.0) built here at 5.76 MB and run from `file://` in a Blob-URL worker (e02); verb-nurbs' ES5
  build; the app's BSP CSG at `src/js/engine/bim/csg-booleans.js` with `CSG_EPS = 1e-5`; replicad's open leak and
  fillet bugs; WebKit's roughly 300 MB wasm ceiling on iOS.
- `docs/research/experiments/kernel-wasm/` e01: a sibling `.wasm` cannot be fetched from `file://`; a base64
  binary of 1, 5 and 10 MB decodes and compiles in the page and in a Blob-URL worker; no SharedArrayBuffer.
- `docs/research/solidcraft-integration-map.md` (2026-11-13): SolidCraft's Rust port of SMLib; discovery
  incomplete, nothing built.
- `docs/research/research-local-storage.md` 4.4, 4.7 and 15: storage on `file://` per engine, no service worker
  and no OPFS there in Chromium, the install rules, the Pages service-worker scope.
- `docs/research/experiments/algorithmic-design/e05-results.json` (the coordinator, Chromium 153.0.8010.12): from
  `file://`, `isSecureContext` true, `crossOriginIsolated` false, SharedArrayBuffer undefined, a worker from a
  file URL refused (SecurityError, origin 'null'), service-worker registration refused, OPFS refused, and a Blob
  worker, a transferred buffer (detached on send), wasm from bytes and IndexedDB all working; over http without
  headers the same except that OPFS and a file worker work and SharedArrayBuffer is still undefined.

### 2.3 Manifold

- **Licence (P, high).** `LICENSE` in the tarball is the Apache License 2.0; package.json says Apache-2.0.
- **What it guarantees (P, high).** Its wiki ("Manifold Library", which the author calls "as close to a paper as
  you'll get") says the method comes from Julian Smith's dissertation (`docs/RobustBoolean.pdf` in the repo, not
  opened here): accept floating-point error and build a result that is manifold by construction, with symbolic
  perturbation for coincident geometry. Topology is treated as exact and geometry as inexact. The boolean
  "guarantees manifold output, only requiring that all input is also manifold". Geometric validity
  (epsilon-valid output from epsilon-valid input) is a goal that "cannot be mathematically proven"; a counter
  example is treated as a bug. Not every degenerate triangle can be removed.
- **So the phrase in the pasted advice, "guaranteed-watertight mesh booleans", holds for topology only, and only
  for manifold input.** A mesh from the app that has a gap, a T-junction or a duplicated face has to be repaired
  or rejected first (`Manifold.ofMesh` plus `status()`; `Mesh.merge` exists for meshes that only look open
  because vertices were duplicated).
- **API (P, high; `manifold.d.ts`).** 3D: `union`, `difference`, `intersection` (pairs and lists), `add`,
  `subtract`, `intersect`, `split`, `splitByPlane`, `trimByPlane`, `hull`, `minkowskiSum`, `slice`, `project`,
  `warp`, `refine`, `smooth`, `levelSet`, `simplify`, `decompose`, `compose`, `volume`, `status`, `ofMesh`,
  `extrude` and `revolve` from a cross-section. 2D (`CrossSection`): `union`, `difference`, `intersection`,
  `offset`, `hull`, `simplify`, `extrude`, `revolve`, `decompose`. No fillet, no loft, no NURBS, no STEP. Each
  triangle of a result keeps the `originalID` and `faceID` of the input face it came from, which is a ready
  answer to "which generated face is this" after a boolean (bears on H3).
- **Loading (P, high for the code).** The Emscripten glue reads `Module["wasmBinary"]` when given and only
  otherwise locates `manifold.wasm` (`Module.locateFile`, else `new URL("manifold.wasm", import.meta.url)`) and
  tries `instantiateStreaming`. So a binary held in the page as base64 or an ArrayBuffer is supported by the
  loader. The file ends `export default Module` and uses `import.meta.url` three times: it parses only as a
  module.
- **Threads (P, high).** No `SharedArrayBuffer` or `pthread` string in `manifold.js`; the README says it
  pipelines "when only a single thread is available". The npm build needs no cross-origin isolation.
- **Memory (P-wf, medium).** Objects are C++ objects behind embind and are freed with `delete()` (the package
  ships `lib/garbage-collector.js`); issue #1855 (heap growth in the wasm bindings on extrude, revolve,
  toPolygons) was closed 2026-09-29. A long-lived adapter should keep one module per worker and delete what it
  makes.
- **Known issues (P-wf, medium; the list was read as a digest on 2026-11-15, 185 results for the query).** #1857
  boolean slowdown on coincident surfaces with different triangulations (closed 2026-10-16); #1706 sliver
  triangles on near-coincident inputs (closed 2026-10-15); #1873 wrong topology from `minkowskiDifference`
  (closed 2026-10-06); #1683 CrossSection loses double precision (closed 2026-08-11); #1849 the bindings fail
  under a Content-Security-Policy without `unsafe-eval` (closed 2026-09-25; the one-file build has no CSP);
  #1902 a request for a core-only npm package without manifoldCAD's dependencies (open). No issue comparing wasm
  to native speed was found in that page.
- **Maintenance (P, high).** 29 versions since 2022-10; 3.5.4 was current on 2026-11-01 and 3.5.5 on 2026-11-13.
  Named users per its README in the repo's earlier note: OpenSCAD, Blender, Babylon.js and others.

### 2.4 OpenCascade in the browser

- **Licence (P, high).** opencascade.js's `LICENSE` is LGPL-2.1 (26,526 bytes, the same file ships in
  replicad-opencascadejs). OCCT's own exception was read by the repo's earlier note. Under the app's rule LGPL is
  allowed "as its own replaceable file": a separate `.wasm` under `runtime/` satisfies that on Pages; embedding
  it as base64 inside `canvas_v10.html` is the unclear reading already recorded as U in `research-usd-brep.md`.
- **Sizes (P, high).** replicad-opencascadejs 1.2.1: 22.9 MB single-threaded, 22.5 MB the "multi" build. The
  earlier note has 42.8 MB (libcascade) and 50.3 MB (opencascade.js beta). ocjs.org's claim of a 7.1 MB custom
  build is still unverified here (U, carried over).
- **Maintenance (P, high).** opencascade.js: `latest` 1.1.1 (2020-09-27), the registry entry last modified
  2023-03-23; its README pins OCCT 7.6.2. replicad and its OCCT build released 1.2.1 on 2026-11-06.
- **What OCCT gives that mesh booleans do not (S, carried from `research-usd-brep.md` 4.8, and general
  knowledge of the kernel):** exact fillets and chamfers, lofts and sweeps as surfaces, NURBS solids, shells and
  offsets of solids, STEP and IGES. replicad (MIT) adds a readable drawing, sketching and finder API over it.
- **Topological naming (U here).** OCCT has no persistent face names across a rebuild without its OCAF naming
  layer; replicad works around it with "finders" that select faces by geometry. This was not read at the source
  in this pass; the identity side belongs to H3's researcher.
- **Against it:** size (a phone's first use downloads or parses 23 MB or more), the iOS memory ceiling and
  replicad's open leak (#282), all in the earlier note.

### 2.5 Pure-JavaScript alternatives

- **csg.js** (Evan Wallace, MIT in the file header, 18,659 bytes, not on npm). BSP-tree booleans; plane
  tolerance `CSG.Plane.EPSILON = 1e-5` (line 405). The app's `csg-booleans.js` uses the same method and the same
  epsilon, so csg.js adds nothing. Its README claims coplanar cases are handled; BSP splitting still leaves
  T-junctions and slivers, which is why three-bvh-csg and Manifold exist (S for the limit; P for the method).
- **@jscad/modeling** 2.13.0 (MIT, 251 KB min, 59 KB gzip, no dependencies, active: 2026-02). Booleans are the
  same BSP family (its README: "based on Constructive Solid Geometry"); what it adds over the app is breadth:
  `expansions` (2D and 3D offsets), `extrusions`, `hulls`, `measurements`. Not ES5; it would sit behind an
  adapter as a vendored classic script.
- **three-bvh-csg** 0.0.18 (MIT, 169 KB UMD, needs three.js and three-mesh-bvh). Its README warns that all
  brushes must be two-manifold and that "due to numerical precision and corner cases" results "may not be"
  two-manifold, and sends CAD users to Manifold. Version 0.0.x. It would also tie the kernel to three.js, which
  the app loads only for the rendered view.
- **Clipper2 for 2D.** `LICENSE` in AngusJohnson/Clipper2 is the Boost Software License 1.0: free use,
  modification and redistribution; the copyright notice and the licence text must stay in source copies, and are
  not required for "machine-executable object code". It is OSI-approved and permissive, with no copyleft, so it
  can be redistributed in an Apache-2.0 repository with its notice kept in `THIRD_PARTY_NOTICES.md` (our
  reading, not a lawyer's; a minified JS file is arguably still source, so keep the notice). **It is not named
  in the app's rule**, so it needs the owner's word. Ports: `clipper2-ts` (pure TypeScript, active 2026-11-07,
  booleans, `inflatePaths` offsets, constrained Delaunay triangulation, Z callbacks; ES module only);
  `clipper2-wasm` (214 KB wasm, UMD glue, takes `wasmBinary`); `clipper-lib` 6.4.2 (the older Clipper 1 in one
  ES5-style classic script, 204 KB, last release 2019). The older `clipper2-js` needs Angular peers: set aside.
  Manifold's `CrossSection` already includes 2D booleans and offsets, so Clipper2 matters only if 2D offsets are
  wanted without Manifold.
- **Straight skeletons (roofs, setbacks).** `straight-skeleton` 3.0.0 embeds CGAL's Straight_skeleton_2 as wasm
  (README; `WebAssembly.instantiate` in the bundle); CGAL's package list gives that package's licence as GPL. Its
  package.json says MIT, which can only cover the wrapper. Under the app's rule it is a separate program in a
  worker at best. Its v1 branch is pure TypeScript and "less robust" (README). The app already has roofs in
  `src/js/engine/map/` (LOD solids and roofs); whether that includes a skeleton is the code researcher's
  question. No permissive, robust, maintained JS straight-skeleton library was found in this pass (U: the search
  was npm metadata only).
- **verb-nurbs** (MIT): unchanged since 3.0.3 (2025-04-23); see the earlier note. Quiet, usable.
- **earcut** 3.2.4 (ISC, 9.7 KB min, active 2026-09): triangulation of polygons with holes. Now `type: module`
  in package.json, but `dist/earcut.min.js` has no classes or arrow functions.

### 2.6 Comparison of the geometry options

"Fits" = the app's library rule (licence list, vendored, on demand, behind an adapter).

| Option | Licence | Fits the rule | Size on disk / gzip | Adds over the app's CSG | Loads from `file://` | Threads needed | Maintenance |
|---|---|---|---|---|---|---|---|
| The app's own CSG (`csg-booleans.js`) | ours | yes | 0 | baseline: BSP booleans, eps 1e-5 | yes | no | ours |
| Manifold (`manifold-3d` 3.5.5) | Apache-2.0 | yes | 625 KB / 224 KB (wasm + glue) | manifold-by-construction booleans, hull, offset and 2D booleans, slice, split, minkowski, face provenance | yes if embedded and started as a module (loader takes `wasmBinary`); route untested | no | very active |
| OCCT (replicad-opencascadejs 1.2.1) | LGPL-2.1 | only as a separate replaceable file | 22.9 MB / about 7.2 MB (1.1.0 measured earlier) | exact B-rep: fillets, lofts, NURBS solids, shells, STEP | embedding 30 MB of base64 is impractical and legally unclear; as a sibling file it cannot be fetched from `file://` | no (single build) | replicad active; opencascade.js dormant |
| SMLib / USD BRep (own build, e02) | Apache-2.0 | yes | 5.76 MB / 1.82 MB | as OCCT less STEP | yes, measured (e02) | no | active, closed to contributions, young |
| @jscad/modeling 2.13.0 | MIT | yes | 251 KB / 59 KB | offsets, hulls, extrusions; booleans no more robust | yes (plain script) | no | active |
| three-bvh-csg 0.0.18 | MIT | yes, but needs three.js loaded | 169 KB / 34 KB + three-mesh-bvh | faster booleans; not robust by its own README | yes | no | active, 0.0.x |
| csg.js | MIT | yes | 19 KB | nothing | yes | no | unmaintained |
| clipper2-ts 2.0.1-19 (2D) | BSL-1.0 | not in the list; permissive; owner's call | 123 KB / 33 KB | robust 2D booleans, offsets, CDT | yes after re-wrapping the ES module | no | active |
| straight-skeleton 3.0.0 (2D) | wrapper MIT, CGAL GPL | only as a separate worker program | 1.03 MB | straight skeleton | embedded wasm; untested | no | active |
| verb-nurbs 3.0.3 | MIT | yes | 278 KB / 56 KB | NURBS curves and surfaces, no solids | yes (ES5) | no | quiet |
| earcut 3.2.4 | ISC | yes | 9.7 KB | triangulation with holes | yes | no | active |

### 2.7 Node-editor libraries

Read from the bundles (counts of event names, syntax), the READMEs and the issue lists.

| Library | Licence | Size (min / gzip) | Framework needed | Classic-script build | Touch | Own evaluation engine | Maintenance |
|---|---|---|---|---|---|---|---|
| litegraph.js 0.7.18 (jagenjo) | MIT | 176 KB / 48 KB core; CSS 13 KB | none; draws on Canvas2D | yes (`build/litegraph.core.min.js`, global `LiteGraph`; no classes, one arrow function) | weak: `pointerevents_method` defaults to "mouse", can be set to "pointer"; the code says "touch events -- TODO IMPLEMENT"; no pinch handling in the bundle; issues #18 "Touch Compatibility" (2018), #58, #236, #518 listed as open | yes (`LGraph.runStep`, execution order, `onExecute` per node) | slow: last npm release 2024-01-08; 132 open issues, 18 open pull requests; not archived |
| @comfyorg/litegraph 0.17.2 | MIT | 403 KB / 98 KB | none | UMD, but ES2015+ (59 classes) | pointer events; no pinch code found | yes | archived; merged into ComfyUI's front end 2025-08-05; "largely incompatible with the original" |
| Rete.js 2.0.6 | MIT | core 18 KB; area plugin and a render plugin on top | a render plugin: React, Vue, Angular, Svelte or Lit (its docs name no framework-free renderer) | core yes (`rete.min.js`); the usable editor no | in the area plugin, not read here (U) | yes, separate (`rete-engine`: dataflow and control flow) | active (area plugin 2026-07) |
| Drawflow 0.0.60 | MIT | 46 KB / 8.7 KB; CSS 1.9 KB | none ("Vanilla javascript"); DOM nodes with your own HTML | yes (`dist/drawflow.min.js`; one class, 27 arrow functions, so not ES5) | README: "Mobile support", long press for the menu, pinch to zoom; touchstart and pointerdown handlers present | no: draws and stores the graph only | slow: last release 2024-09-03; 247 open issues |
| Baklava.js 2.8.1 | MIT | 176 KB bundle | Vue 3 | no | pointer events; not read further | yes (`@baklavajs/engine`) | active (2025-11) |
| React Flow / xyflow 12.12.1 | MIT | 189 KB + React | React (Svelte version exists) | UMD that requires React | best documented: tap two handles to connect (`connectOnClick`), larger handles advised; pinch handling in the bundle | no | very active |
| Flume 1.2.0 | MIT | 300 KB + React | React | no | touchstart handlers present; not read further | yes (`RootEngine`) | active (2025-11) |
| Our own, in ES5 | ours | what we write | none | yes | ours to design | ours (H1's evaluator) | ours |

- **No library is both framework-free and good on a phone.** The two framework-free ones are also the two with
  the slowest upstreams. litegraph gives an engine and a canvas editor but its touch support is unfinished;
  Drawflow gives touch but no engine and DOM nodes that the app would have to style and fill.
- **How others did it.** ComfyUI kept litegraph and ended up owning it (the fork, then the merge into its own
  front end): evidence that a node editor at the centre of an app tends to become the app's own code (P-wf).
  React Flow's touch guidance is tap-to-connect instead of drag-to-connect, with enlarged handles (P-wf): the
  one published touch convention found. Nodi (nodi3d.com) describes itself as "a node-based geometry design
  tool" with a web version; its page states no licence, technology or touch support (P-wf; nothing usable).
  Hypar, Pollination's recipe interface and Blender's conventions were not reached in this pass (section 6).

### 2.8 Browser platform facts

Chromium is measured (e05, e01, e12); the rest is from MDN's sources and Bugzilla.

| | `file://` | https with no special headers (GitHub Pages) | https with COOP and COEP | Evidence, level |
|---|---|---|---|---|
| (a) SharedArrayBuffer, wasm threads | no | no; possible only if a service worker adds the headers and reloads (coi-serviceworker's README: for "situations in which you can't control the headers (e.g. GH pages)"; needs https or localhost) | yes | MDN SharedArrayBuffer: the document "must be in a secure context and cross-origin isolated" (P); e05 both rows (P); coi-serviceworker (S, not tried) |
| (b) Worker from a file URL | Chromium: refused (SecurityError, origin 'null'). Firefox: each file is its own origin since 68; a developer's comment on bug 1500453 says a file page can only load itself as a worker, any other file URL being cross-origin (P-wf; whether that exact rule shipped is not confirmed). Safari: not verified (U) | yes | yes | e05 (P); Bugzilla 1500453 (P-wf) |
| (b) Worker from a Blob URL | Chromium: yes (e05, e01, e02, and the Ladybug runtime). MDN: a `blob:` URL "inherits the origin of the document that created it" and is the advised route; a `data:` URL has an opaque origin. Firefox and Safari from `file://`: not measured (U) | yes | yes | e05 (P); MDN Worker() (P) |
| (c) Secure context and OPFS | `file://` is a secure context (MDN's table lists `file:///path` as secure; Chromium reports `isSecureContext` true) yet OPFS is refused in Chromium (SecurityError). The cause is the origin, not the secure context: the Storage Standard gives an opaque origin no storage (`research-local-storage.md` 4.4). Firefox, Safari: not measured; WebKit refuses storage for local origins in code read earlier | yes | yes | MDN Secure contexts, MDN OPFS (P); e05, e12 (P) |
| (d) Service worker | no ("The URL protocol of the current origin ('null') is not supported") | yes, within the script's folder scope | yes | e05, e12 (P); MDN Service Worker API: secure contexts, https or localhost (P) |
| (e) Transferable ArrayBuffer in `postMessage` | yes: the sender's buffer is detached (e05 `transferDetaches` true) | yes | yes | MDN Transferable objects: ArrayBuffer is first in the supported list, zero-copy (P); e05 (P). Universal in current engines (S: MDN's compatibility data, not opened) |
| (f) WebAssembly | from bytes: yes (`WebAssembly.instantiate(buffer)`; e05, e01). `instantiateStreaming` needs a `Response` with MIME `application/wasm`, else TypeError, and a sibling fetch from `file://` fails anyway (e01) | both work if the server sends the MIME type; Pages does for `.wasm` (U, not checked here; Pyodide already loads there) | both | MDN instantiateStreaming (P); e01, e05 (P) |
| (g) IndexedDB | Chromium yes (one store shared by all local files); Firefox per file path; WebKit may refuse | yes | yes | `research-local-storage.md` 4.4 (P); e05 (P) |

- **(h) Tauri and installation (a note only).** Tauri is a Rust toolchain plus the operating system's webview,
  built and signed per platform (its prerequisites page lists Rust, webkit2gtk on Linux, Xcode on macOS, and
  more for mobile; P). It would be a second delivery form with its own build and release, not a wrapper that
  costs nothing; it changes the delivery contract and is the owner's decision. Installing as a web app from
  Pages was researched and built already (V172h, `research-local-storage.md` 15): it gives offline use and
  OPFS without any of this.

### 2.9 Instancing

three.js r186 `src/objects/InstancedMesh.js` (P): `new InstancedMesh(geometry, material, count)` holds one
geometry and a `Float32Array(count * 16)` of matrices (`instanceMatrix`), set with `setMatrixAt`, with optional
per-instance colour; bounds must be recomputed after moving instances. It is the right tool **inside the
rendered view only**. The app's working view is its own WebGL/WebGPU renderer with its own GPU batches
(`src/js/engine/render/`), so the design point that carries over is the data shape, not the class: a generator
that repeats a part should emit one mesh and a list of transforms, and each renderer decides how to draw that.
Whether the app's batches can draw instances is the code researcher's question.

## 3. The pasted advice, line by line

| Advice | From `file://` (the one-file build) | On GitHub Pages | Verdict |
|---|---|---|---|
| "run the solver in a Web Worker" | holds, with a Blob-URL worker; a worker from a file URL fails | holds | **Holds**, by the Blob route |
| "with SharedArrayBuffer" | fails | fails without COOP/COEP; a header-adding service worker is a workaround with a forced reload | **Holds only over https with headers.** Not needed: transferable buffers work everywhere, and Manifold's npm build is single-threaded |
| "opencascade.js for exact B-rep" | impractical (23 MB or more, cannot be fetched as a sibling) | possible as a separate file, on demand | **Partly.** True that OCCT is the exact kernel; opencascade.js itself is dormant, replicad's build is the live one, LGPL; the repo's earlier research prefers SMLib |
| "or Manifold (wasm) for guaranteed-watertight mesh booleans" | holds if embedded and started as a module | holds | **Holds with a caveat:** guaranteed manifold topology for manifold input, not guaranteed geometric validity |
| "render with three.js InstancedMesh" | holds in the rendered view | same | **Holds for the three.js view only**; the app's main renderer is its own |
| "store caches in OPFS" | fails (Chromium measured) | holds | **Holds only when served** |
| "and metadata in IndexedDB" | Chromium yes; Firefox per path; Safari may refuse | holds | **Holds when served; unreliable from `file://`** (already the app's rule: the file is the save) |
| "precache with a Service Worker (Workbox)" | fails | holds; the app already has its own worker since V172h, and Workbox is a build-time dependency it does not need | **Holds only when served; Workbox unnecessary** |
| "wrap with Tauri" | not applicable | not applicable | **A different delivery contract**; owner's decision, not a technical need |
| "use Yjs/Automerge CRDTs" | not examined | not examined | **Outside this side** (collaboration); not checked |

## 4. What bears on H4 and H7

**H4 (the kernel): supported, with two refinements.**
- Nothing found requires a kernel for the first slices. Box and prism massing, facades and plates need extrusion,
  transforms and at most planar cuts, which the app has.
- Manifold is the right second step and is cheap: 625 KB on disk, Apache-2.0, single-threaded, binary loadable
  from memory. Two conditions the hypothesis did not state: its input must already be manifold, so generators
  must emit closed meshes (or the adapter must check `status()` and fall back to the app's CSG); and its glue is
  an ES module, so the vendoring step or the worker has to cope with that. A short experiment (Manifold embedded
  in a Blob-URL module worker from `file://`, in the manner of e01) would settle the second; it needs the
  owner's approval to run upstream code.
- Manifold also covers 2D booleans and offsets (`CrossSection`), which removes most of the case for Clipper2 once
  Manifold is in.
- Exact B-rep stays a later, separate decision, and the repo's own earlier research already ranks SMLib ahead of
  OCCT for it. Nothing here changes that.
- A gap H4 does not mention: straight skeletons for roofs and setbacks. The robust library is GPL through CGAL.

**H7 (the worker): supported.**
- SharedArrayBuffer, OPFS and service workers fail from `file://`; a Blob-made classic worker, transferable
  buffers, wasm from bytes and (in Chromium) IndexedDB work. Measured in Chromium (e05), consistent with MDN.
- Refinement: the reason differs per feature. `file://` is a secure context; SharedArrayBuffer fails for lack of
  cross-origin isolation, OPFS and service workers for lack of a usable origin. On Pages the last two work and
  only SharedArrayBuffer does not.
- Not established: a Blob worker from `file://` in Firefox and Safari. The design should keep a main-thread
  fallback (run the same evaluator in slices) so a refused worker degrades instead of failing.

**The node editor.** No library fits the contract without cost. The choice is between adopting litegraph.js as
vendored code that the app then maintains (it brings an engine and a canvas editor, but touch is unfinished and
upstream is slow), and writing the editor in ES5 on the app's own canvas and pointer handling. ComfyUI's history
with litegraph suggests the first becomes the second over time.

## 5. Counter-evidence found

- Against "Manifold is guaranteed": its own wiki limits the proof to topology; recent issues show sliver
  triangles (#1706), a slowdown on coincident faces (#1857) and a wrong-topology bug in a Minkowski operation
  (#1873), all closed within weeks.
- Against "Manifold drops into the build": ES-module glue; a wasm heap leak fixed only in 2026-09 (#1855); the
  npm package pulls manifoldCAD's dependencies unless only three files are vendored (#1902, open).
- Against "MIT on npm means MIT": `straight-skeleton` carries CGAL's GPL code.
- Against "a library saves writing the node editor": litegraph's touch issue open since 2018; Drawflow has 247
  open issues and no engine; the maintained libraries all need a framework.
- Against "`file://` is not a secure context" (a common belief, and a possible reading of H7): MDN and Chromium
  both say it is. The failures have other causes.
- Against "IndexedDB works from `file://`": true in Chromium only (`research-local-storage.md` 4.4).
- Nothing was found against the main claim that SharedArrayBuffer is unavailable without cross-origin
  isolation.

## 6. Still open (U), and why

- A Blob-URL worker, and a module worker or `import()` of a Blob URL, from `file://` in Firefox and Safari: no
  primary statement found, no device or browser here to measure.
- Manifold's speed in wasm against native, and on a phone: no figure found in the sources read; needs a run.
- Manifold started from the one-file build: needs the experiment in section 4 and the owner's approval.
- Julian Smith's dissertation (`RobustBoolean.pdf`) was not opened; the guarantee is reported from the wiki's
  account of it.
- GitHub issue pages were read as digests (P-wf); exact open or closed states of litegraph's touch issues and
  the latest commit dates were not all shown.
- OCCT's topological naming and replicad's finders: not read at the source in this pass.
- Rete's area plugin on touch; Baklava and Flume on touch: bundles only skimmed.
- Hypar, Pollination's recipe interface, Blender's node conventions, and any published study of node editors on
  touch devices: not reached (time). React Flow's touch page is the only published convention recorded.
- A permissive, robust straight-skeleton library in JavaScript: none found, search limited to npm metadata.
- Whether BSL-1.0 is acceptable under the app's rule: the owner's decision.
- Yjs and Automerge: outside this side.

## 7. Search log

| When | Where | Query or address | What came back | Kept or set aside |
|---|---|---|---|---|
| 11-14 | the repository | `research-usd-brep.md`, `solidcraft-integration-map.md`, `research-local-storage.md` 4.4-4.7, `experiments/kernel-wasm/` | Prior kernel and `file://` findings | Kept, cited |
| 11-14 | registry.npmjs.org | Metadata for 27 package names | 26 answered; `csg.js` 404 | Kept; csg.js read on GitHub instead |
| 11-14 | registry.npmjs.org | 19 tarballs by curl | All fetched; sha1 equal to the registry's | Kept; `clipper2-js` set aside (Angular peers), `js-angusj-clipper` and `polyclip-ts` set aside (older or narrower) |
| 11-15 | the tarballs | grep for `wasmBinary`, `instantiateStreaming`, `import.meta`, `SharedArrayBuffer`, `pthread` in `manifold.js`; method names in `manifold.d.ts` | Loader and API facts | Kept |
| 11-15 | the tarballs | grep for `touchstart`, `pointerdown`, pinch, `class`, `=>`, `require(` in each bundle | Touch handling, syntax level, framework needs | Kept as indicators, not as proof of behaviour |
| 11-15 | raw.githubusercontent.com | Manifold wiki, Clipper2 LICENSE, csg.js, opencascade.js README and LICENSE, coi-serviceworker README, three.js r186 `InstancedMesh.js`, Tauri prerequisites, nine MDN pages | All 200 except MDN's old secure-contexts path and three.js's old docs path (404) | Kept |
| 11-15 | doc.cgal.org | package list, Straight_skeleton_2 | GPL | Kept |
| 11-15 | github.com (fetch tool) | Manifold issues: wasm, coplanar, precision, slow | 185 results, first 25 read | Kept as P-wf |
| 11-15 | github.com (fetch tool) | litegraph.js issues: touch, mobile, pinch; repo page; Comfy-Org fork; Drawflow repo | 13 issues; counts; the archive banner | Kept as P-wf |
| 11-15 | reactflow.dev | `learn/advanced-use/touch-device` | 404 | Replaced by `examples/interaction/touch-device` (read) |
| 11-15 | retejs.org/docs | renderers, engines | Framework list, engines; nothing on touch | Kept |
| 11-15 | bugzilla.mozilla.org | bug 1500453 | file URLs as unique origins, fixed in Firefox 68; a comment on workers | Kept as P-wf, medium |
| 11-15 | nodi3d.com | home page | A description only | Set aside: nothing usable |
| 11-15 | v2.tauri.app | architecture page | OS webview, Rust binary | Kept, a note |

## 8. References

All read 2026-11-14 or 2026-11-15, as marked.

| Source | Address | What was read | Date | Level |
|---|---|---|---|---|
| npm registry metadata | `https://registry.npmjs.org/<name>` for the packages in 2.1, plus rete-area-plugin and rete-engine | `dist-tags`, the latest version's `license`, `dist`, dependencies, `time` | 11-14, 11-15 | P |
| npm tarballs | `https://registry.npmjs.org/<name>/-/<file>.tgz` | Listings, sizes, gzip sizes, sha256; files named below | 11-14, 11-15 | P |
| manifold-3d 3.5.5 | tarball | `LICENSE`, `package.json`, `README.md` (first 60 lines), `manifold.js` (loader strings), `manifold.d.ts` (method list) | 11-14, 11-15 | P |
| Manifold wiki, "Manifold Library" | `https://raw.githubusercontent.com/wiki/elalish/manifold/Manifold-Library.md` | Lines 1-11 (road map), 47-49, 61-67 (Smith's method), 83-95 (the guarantee, epsilon-validity), 121-125 (degenerates), 143-147 (IDs) | 11-15 | P |
| Manifold issues | `https://github.com/elalish/manifold/issues?q=...` | First page of 185 results: numbers, titles, states | 11-15 | P-wf |
| opencascade.js | `https://raw.githubusercontent.com/donalffons/opencascade.js/master/README.md`, `/LICENSE` | Whole README (OCCT 7.6.2, users); the licence's heading | 11-15 | P |
| replicad-opencascadejs 1.2.1, replicad 1.2.1 | tarballs | Listings and sizes | 11-14 | P |
| Clipper2 | `https://raw.githubusercontent.com/AngusJohnson/Clipper2/main/LICENSE` | The whole licence (BSL-1.0) | 11-15 | P |
| clipper2-ts 2.0.1-19 | tarball | `README.md` (features, lines 6-113), `dist/` listing | 11-15 | P |
| csg.js | `https://raw.githubusercontent.com/evanw/csg.js/master/csg.js`, `/README.md` | Header (licence, line 44), `EPSILON` (405), `splitPolygon` (427-447); README | 11-15 | P |
| @jscad/modeling 2.13.0 | tarball | `README.md` (22, 53, 94), `CHANGELOG.md` (top entry), bundle syntax | 11-15 | P |
| three-bvh-csg 0.0.18 | tarball | `README.md` lines 14-19, 78-79, 353-356 | 11-15 | P |
| straight-skeleton 3.0.0 | tarball | `README.md` lines 1-30; `dist/index.js` (wasm instantiation) | 11-15 | P |
| CGAL package overview | `https://doc.cgal.org/latest/Manual/packages.html` | The licence line of "2D Straight Skeleton and Polygon Offsetting" | 11-15 | P-wf |
| litegraph.js 0.7.18 | tarball; `https://github.com/jagenjo/litegraph.js` and its issues | `build/litegraph.core.js` lines 113-144, 5121-5196, 5699-5724, 890-1050; README; repo counts; 13 issues matching touch, mobile, pinch | 11-15 | P, P-wf |
| Comfy-Org/litegraph.js | `https://github.com/Comfy-Org/litegraph.js` | Archive banner and README | 11-15 | P-wf |
| Drawflow 0.0.60 | tarball; `https://github.com/jerosoler/Drawflow` | `README.md` lines 54, 144, 146; bundle; repo counts | 11-15 | P, P-wf |
| Rete.js | `https://retejs.org/docs/`; rete 2.0.6 tarball | Introduction (renderers, engines, licence); listing | 11-15 | P-wf, P |
| Baklava, xyflow, Flume | tarballs | Listings, `require` calls, event-name counts | 11-15 | P |
| React Flow, touch example | `https://reactflow.dev/examples/interaction/touch-device` | The page's text | 11-15 | P-wf |
| MDN, SharedArrayBuffer | `raw.githubusercontent.com/mdn/content/main/files/en-us/web/javascript/reference/global_objects/sharedarraybuffer/index.md` | Lines 33-50, 153-156 | 11-15 | P |
| MDN, Secure contexts | `.../web/security/defenses/secure_contexts/index.md` | Lines 32-45 (the table with `file:///`), 74-89 | 11-15 | P |
| MDN, Origin private file system | `.../web/api/file_system_api/origin_private_file_system/index.md` | Lines 8-31, 120-122 | 11-15 | P |
| MDN, Worker() constructor | `.../web/api/worker/worker/index.md` | Lines 32, 57-77, 118-127 | 11-15 | P |
| MDN, Transferable objects | `.../web/api/web_workers_api/transferable_objects/index.md` | Lines 13-27, 75-81 | 11-15 | P |
| MDN, WebAssembly.instantiateStreaming | `.../webassembly/reference/javascript_interface/instantiatestreaming_static/index.md` | Lines 28, 59, 91 | 11-15 | P |
| MDN, Service Worker API | `.../web/api/service_worker_api/index.md` | Line 23 | 11-15 | P |
| Mozilla bug 1500453 | `https://bugzilla.mozilla.org/show_bug.cgi?id=1500453` | Status, comments 7-11 and 18 | 11-15 | P-wf |
| coi-serviceworker | `https://raw.githubusercontent.com/gzuidhof/coi-serviceworker/master/README.md` | Lines 4, 16, 21 | 11-15 | S (for Pages' lack of headers) |
| three.js r186 | `https://raw.githubusercontent.com/mrdoob/three.js/r186/src/objects/InstancedMesh.js` | Constructor and bounds methods, lines 35-154 | 11-15 | P |
| Tauri | `raw.githubusercontent.com/tauri-apps/tauri-docs/v2/src/content/docs/start/prerequisites.mdx`; `https://v2.tauri.app/concept/architecture/` | Prerequisites headings; architecture overview | 11-15 | P, P-wf |
| Nodi | `https://nodi3d.com/` | Home page | 11-15 | P-wf |
| This repository | `docs/research/research-usd-brep.md`, `research-local-storage.md` 4.4-4.7, `solidcraft-integration-map.md`, `experiments/kernel-wasm/`, `experiments/algorithmic-design/e05-results.json` | As cited in 2.2 | 11-14, 11-15 | P |

Downloads are kept outside the repository, in the session's scratch folder, each tarball in its own directory.
