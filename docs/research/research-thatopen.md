# That Open Engine: what it gives this app, and how it would fit

Research, 2026-11-13. Levels as in `research-protocol.md`: P primary, S secondary, U a pointer only.
Experiment e01: `experiments/thatopen/` (scripts and `results.txt`).

## 1. Abstract

The owner chose That Open Engine (2026-11-13) as the first library under the new "Third-party libraries" rule,
and asked that ifc-viewer-online (j03rul4nd) be read too, as an app with the same idea. The question is what
That Open adds that the app lacks, and whether it can meet the rule (pinned, loaded on demand, offline from
`file://`, behind an adapter). It can. e01 shows it reading IFC and loading the result offline from `file://`,
on the app's own three.js 0.186.1, with two workarounds the library allows. It costs about 1.0 MB compressed
plus web-ifc's 0.6 MB wasm. It is a viewer and coordination toolkit, not an authoring engine: it writes no IFC,
and its model format changed at each major version. **Recommendation:** use it as an on-demand **Review** view
for imported and federated IFC models (clipping, plans, measuring, IDS checks, BCF issues), beside the app's own
engine. Keep cc-ifc (V196) as the reader that brings IFC into the editable model, and IfcOpenShell (V176-V177)
for writing IFC. ifc-viewer-online is MIT and built on That Open, so it is prior art and a source of methods
(its 44 validation rules, its loading pipeline). Its React and TypeScript code is not taken as code.

## 2. The question and the hypotheses

What would That Open add to this app, at what cost, and can it meet the rule?

- H1: That Open is MIT and its dependencies are licences the rule allows. **Held** (P): components and fragments
  are MIT; web-ifc is MPL-2.0, shipped unchanged as its own file; three, camera-controls, jszip, three-mesh-bvh,
  fast-xml-parser, pako, earcut, flatbuffers and lru-cache are permissive (npm metadata).
- H2: It cannot run offline from `file://`. **False, with two workarounds** (e01, P): web-ifc cannot fetch its
  wasm from `file://`, but a fetch wrapper that hands it the wasm from a script works. The fragments worker hangs
  as a module worker from `file://`, but runs as a classic worker made by the library's own `toClassicWorker()`.
  V196 recorded "web-ifc cannot load its wasm from file://". That holds only without this wrapper.
- H3: It needs cross-origin isolation (SharedArrayBuffer), as ifc-viewer-online's notes say. **False** (P): e01
  ran with `crossOriginIsolated` false over http and from `file://`. The fragments source at bc3f688 does not
  use SharedArrayBuffer (grep). The viewer's note likely predates fragments 3.6.
- H4: It can share the app's three.js. **Held, for its WebGL paths** (e01): with "three" mapped to the app's
  `BIMTHREE`, and "three/webgpu" and "three/tsl" left out, the bundle drops to 987 KB compressed and still reads
  and loads all three files. Its WebGPU-only code paths are then unavailable.
- H5: It can replace the app's modelling engine (walls, joins, editing). **False** (P): it has no IFC writer
  and no parametric elements. Its fragments `Editor` edits fragments geometry and data, not BIM elements with
  rules.

## 3. Method

Search log:

| Where | What | Kept |
|---|---|---|
| npm registry | `npm view` for @thatopen/components, components-front, fragments, ui, web-ifc, three: versions, licences, dependencies, sizes, release dates | All (P) |
| GitHub, git clone | ThatOpen/engine_components @ 7dea8fe (2026-11-08); ThatOpen/engine_fragment @ bc3f688 (2026-11-08); j03rul4nd/ifc-viewer-online @ 89372f7 (2026-11-13) | Read as text, never run |
| engine_fragment | `FragmentsModels/index.ts` 38-110 (getWorker, inline worker), `bundled-worker-url.ts`, `multithreading-helper.ts`, `Utils/worker-utils.ts`, `Importers/IfcImporter` (SetWasmPath), `FragmentsModels/src/edit/editor.ts`; grep for SharedArrayBuffer, IFC writers | P |
| engine_components | `packages/core/src`, `packages/front/src` folder lists; `examples/`; CHANGELOG | P |
| ifc-viewer-online | LICENSE, readme (features, the 44 rules, paid plans), package.json, ARCHITECTURE.md (workers, loading), DECISIONS.md D-01, D-02, D-07, D-11 area | P (its own account) |
| buildingSMART/Sample-Test-Files | three files, sparse checkout, matching V196's hashes | Data |
| The app | `io/ifc-full.js`, `ladybug/runtime.js`, `tools/three/build_three.mjs`, `runtime/`, `research-ifc-engine.md` | P |

GitHub's REST API answered 403 for repositories outside this session's scope. Plain `git clone` of public
repositories worked. No web search was used, so no U facts.

Independent check: a second reader (separate agent) re-read the sources behind F1 to F14 and re-ran e01's
two key runs. All confirmed; its notes are in section 10.

## 4. Findings

| # | Finding | Level | Confidence |
|---|---|---|---|
| F1 | @thatopen/components 3.6.0, MIT; peers three >=0.182.0, web-ifc >=0.0.77, camera-controls >=3.1.2, @thatopen/fragments ~3.6.0; depends on jszip, three-mesh-bvh, fast-xml-parser | P | High |
| F2 | @thatopen/fragments 3.6.1, MIT. `FragmentsModels.getWorker()` fetches the worker from unpkg unless `@thatopen/fragments/inline` was imported, which carries it as base64 and makes a blob URL. The rule forbids the unpkg path, so the adapter must import `inline` | P | High |
| F3 | `toClassicWorker()` and the `classicWorker` option exist. A classic worker is the one that ran from `file://` | P, e01 | High |
| F4 | web-ifc 0.0.79, MPL-2.0; `web-ifc.wasm` (1,679,477 bytes) is a separate file; IfcImporter sets its place with `SetWasmPath`. Still 0.0.x: no stability promise | P | High |
| F5 | No writer from a model to IFC in components or fragments. Fragments' `IfcSplitter` writes IFC files holding a share of an input IFC's elements (found by the second reader) | P | High |
| F6 | Fragments has an `Editor` with `edit()` and `save()` for fragments models | P | High |
| F7 | Components: Clipper, Grids, Raycasters, Views, Viewpoints, FragmentsManager, IfcLoader, Classifier, Hider, ItemsFinder, BoundingBoxer, EdgeProjector, BCFTopics, IDSSpecifications, DxfManager, TechnicalDrawings. Front: Highlighter, Hoverer, Outliner, Mesher, Length/Area/Angle/Volume measurement, ClipStyler, PostproductionRenderer, Marker, Civil navigators, PointCloudLoader, SplatLoader, DrawingEditor | P (folders) | High that they exist; how complete each is was not tested |
| F8 | Components loads "three/webgpu" and "three/tsl" dynamically, for WebGPU-only code | P | High |
| F9 | ifc-viewer-online: MIT; React 18, TypeScript, Vite; on @thatopen 3.4.x, web-ifc 0.0.77, three 0.184; also Clerk (accounts) and PostHog (analytics); paid plans on closed code outside the repo | P | High |
| F10 | Its D-01 chose @thatopen v3 over raw web-ifc, web-ifc-three (discontinued) and xeokit, for batching, async picking, highlighting, camera controls and an internal worker. Its D-07 says fragments' worker needs SharedArrayBuffer; see H3 | P (their account) | High that they wrote it; the SharedArrayBuffer part is contradicted by e01 |
| F11 | Major versions: components 2.x 2024-05 to 2025-05, 3.x since 2025-07-10; fragments 3.x since 2025-04-10, with a new file format. Releases every few weeks | P (npm `time`) | High |
| F12 | e01: from `file://` without the wrapper, every file fails ("both async and sync fetching of the wasm failed"); with it and a classic worker, all three load | P (measured) | High for Chromium 1243; other browsers not tried |
| F13 | The app's three.js bundle publishes all of three on `BIMTHREE` (`tools/three/build_three.mjs`); That Open runs on it | P, e01 | High |
| F14 | Bundle on the app's three, without the WebGPU paths: 5,540,923 bytes, 987,269 compressed; plus web-ifc.wasm 605,575 compressed | P (measured) | High |

## 5. The alternatives compared

Criteria, set before the table: (a) what it adds that the app lacks; (b) works offline from `file://`;
(c) extra download, compressed; (d) fits the app's own engine and ES5 code; (e) writes IFC; (f) churn risk.

| | A. That Open as the app's 3D engine | B. That Open as an on-demand Review view | C. Only That Open's non-visual parts (IDS, BCF) | D. No That Open: cc-ifc + IfcOpenShell only |
|---|---|---|---|---|
| (a) | Fast large-model display, but the app's own drawing, picking, gizmos and editing would all be rebuilt on it | Fast display of large and federated IFC; clipping, plans, measuring, classify and hide; IDS; BCF | IDS checks and BCF issues | Nothing new beyond V176-V177 |
| (b) | Yes, with e01's two workarounds | Yes, with e01's two workarounds | Yes (IDS needs web-ifc's wasm: same wrapper) | Yes (V196) |
| (c) | ~1.6 MB | ~1.6 MB, only when Review is opened | Smaller, not measured | 0 more |
| (d) | Poor: rewrites most of 229 modules; moves the app off its WebGL/WebGPU engine | Good: its own canvas, as V194's rendered view; the adapter is the only meeting point | Good | Good |
| (e) | No | No (IfcOpenShell does) | No | Yes, V176-V177 |
| (f) | High: every major version touches the whole app | Medium: confined to the adapter; never store `.frag` files in projects, regenerate them from the IFC | Low to medium | Low |

**Recommendation: B.** It adds the most that the app lacks (a review and coordination view for big models)
at the lowest risk to what works. A loses the app's own engine for no authoring gain. C leaves out the reason to
take That Open (its fast viewing). D is the fallback if the download or the churn is judged too much. What would
change it: if That Open gains BIM authoring with an IFC writer, A becomes worth reconsidering; if the Review
view proves slow on phones, D.

## 6. The experiment (e01)

Bundling with esbuild 0.28.2 into one classic script (IIFE), then reading three buildingSMART sample files
(IFC2x3 and IFC4 architecture, IFC4 wall with opening) into fragments and loading them, in headless Chromium
1243, over http and from `file://`. Raw numbers in `experiments/thatopen/results.txt`. In short:

| Build | Raw | Compressed |
|---|---|---|
| With its own three | 7,030,304 | 1,390,396 |
| On the app's three (BIMTHREE) | 6,674,214 | 1,302,053 |
| On the app's three, WebGPU paths left out | 5,540,923 | 987,269 |
| web-ifc.wasm | 1,679,477 | 605,575 |
| (V196 cc-ifc + Manifold, for scale) | 1,158,658 | 368,257 |

From `file://`: the 2x3 architecture file converts in about 240 ms and loads in 140 ms (14 items with geometry);
the IFC4 one 120 ms and 75 ms (13); the wall 70 ms and under 10 ms (2). One run each, for order of magnitude.

## 7. Edges

- `file://`: works only with the wasm wrapper and the classic worker; either missing, it fails (F12).
- WebGPU: the lean build leaves out That Open's WebGPU-only paths. The Review view would draw with WebGL.
- Two copies of three: if "three/webgpu" is kept, a second copy of three's core is bundled beside the app's.
- Fragments files are tied to the library's major version (F11): cache them, never save them in a project.
- Large files: not tried here over 150 KB. ifc-viewer-online's notes say conversion is one synchronous wasm call
  per IFC class and the worker cannot be interrupted, only terminated.

## 8. What the app already has

- `src/js/engine/io/ifc-full.js` (V196): cc-ifc read into the editable model; `bimIfcSources` (line 31) picks
  `runtime/` beside the page from `file://`, the site with SRI otherwise. The Review view's loader would copy it.
- `src/js/engine/ladybug/runtime.js` 27-35: the same pattern for Pyodide.
- `tools/three/build_three.mjs`: three.js 0.186.1 as one classic script on `BIMTHREE`; That Open runs on it.
- `src/js/engine/render/rendered-view.js` and siblings (V194): a three.js canvas beside the app's own engine.
  The Review view would follow the same pattern.
- `runtime/MANIFEST.json` and `tools/check_runtime.py`: where the bundle and wasm would be pinned.

## 9. Risks and threats to validity

- One browser (Chromium 1243, headless, Linux); no Safari, Firefox or phone. Safari's `file://` rules differ.
- Three small files only. Speed and memory on 50 to 300 MB models are untested here.
- The two workarounds rely on undocumented behaviour (a fetch wrapper for Emscripten; stripping a worker's
  export). A That Open or web-ifc update could break them. Pin, and re-run e01 at each update.
- Fast churn (F11): roughly one major version a year so far.
- Download: about 1.6 MB compressed on first use of Review, on top of the app.
- Nothing was drawn to a canvas: the world, renderer, camera and clipping were not exercised in e01.

## 10. What is still open

- Drawing and interaction (a world, camera, clipping, plans, measuring) in the app: the next experiment, e02.
- IDSSpecifications' coverage of IDS 1.0's six facets, against buildingSMART's test cases (U until read).
- Safari, Firefox and a phone, from `file://` and over http.
- A large file (dental_clinic, 13 MB; schependomlaan, 49 MB) for speed and memory.
- Whether the WebGPU stub in the lean build is ever reached at run time (nothing was drawn).

**The independent check (2026-11-13), by a separate agent:** F1 to F14 all CONFIRMED against the sources; it
re-ran F12 (both modes) and F14, and loaded `bim-three.min.js` in Chromium for F13 (`BIMTHREE.Box3` a constructor,
448 names, `window.THREE` undefined). Its notes, now taken in: F5 holds as worded, but fragments 3.6.1 also exports
`IfcSplitter`, which writes IFC files holding a share of an input IFC's elements (IFC to IFC, not model to IFC).
F7's front list was read from the source at 7dea8fe, not an installed components-front. F10: in the fragments
3.6.1 dist, SharedArrayBuffer appears only in bundled three-mesh-bvh code behind `useSharedArrayBuffer`, false by
default. F13: the old mapping was not kept, so the cause of the first error is very likely, not proven.

## 11. The owner's decisions

To ask together:

1. Role: B (an on-demand Review view, recommended), A, C or D?
2. three.js: run That Open on the app's own three and leave out its WebGPU paths (987 KB compressed,
   recommended), or bundle its own three (1.39 MB)?
3. IFC reading: keep cc-ifc for bringing IFC into the editable model and use web-ifc only inside Review
   (recommended), or switch the import to That Open too?
4. Order and number: before, after or between V176-V177 (IfcOpenShell)?

**The owner's answers (2026-11-13):**

1. **B, a Review view**, loaded on demand, beside the app's engine.
2. **The app's own three.js**, with That Open's WebGPU paths left out (987 KB compressed).
3. **That Open for IFC import too**, against the recommendation. One IFC reader ships (web-ifc, through That
   Open), and cc-ifc (V196) is retired once the new import matches it. What this needs, for the spec:
   fragments' geometry turned into the app's meshes (per element, in metres, +Y up, with V196's layers, storeys
   and property sets), checked against V196's results on the same 13 files; the wasm wrapper and classic worker
   from e01; the walls-and-slabs reader (`import-ifc.js`) kept as the fallback. Cost: the first IFC import
   downloads about 1.6 MB compressed instead of cc-ifc's 0.37 MB.
4. **After V176-V177.** Meanwhile Claude runs e02 (drawing, clipping and measuring in a canvas; fragments into
   the app's meshes) and writes the spec. The phase number is set in `docs/dev/PIPELINE.md` with the spec.

## 12. References

- @thatopen/components 3.6.0, @thatopen/components-front 3.6.1, @thatopen/fragments 3.6.1, @thatopen/ui 3.4.28,
  web-ifc 0.0.79, three 0.186.1 / 0.187.0: npm registry metadata (`npm view`), and the installed packages'
  `dist/` and `.d.ts` files. Read 2026-11-13. P.
- ThatOpen/engine_components @ 7dea8fe, https://github.com/ThatOpen/engine_components: LICENSE.md,
  CHANGELOG.md, `packages/core/src`, `packages/front/src`, `examples/`. 2026-11-13. P.
- ThatOpen/engine_fragment @ bc3f688, https://github.com/ThatOpen/engine_fragment: the files listed in section 3.
  2026-11-13. P.
- j03rul4nd/ifc-viewer-online @ 89372f7, https://github.com/j03rul4nd/ifc-viewer-online: LICENSE, readme.md,
  package.json, ARCHITECTURE.md, DECISIONS.md (D-01, D-02, D-07, D-08, the chunking decision). 2026-11-13. P for
  what they wrote; their claims about That Open checked in e01.
- buildingSMART/Sample-Test-Files (main), https://github.com/buildingSMART/Sample-Test-Files: three files, hashes
  in `results.txt`. 2026-11-13. Data.
- This repository: `research-ifc-engine.md` (V196), `io/ifc-full.js`, `ladybug/runtime.js`,
  `tools/three/build_three.mjs`, `runtime/MANIFEST.json`. 2026-11-13. P.
