# glTF/GLB and credited procedural assets — research

## 1. Abstract

How can World BIM safely import correctly scaled assets and export interoperable models, while honoring the in-house-first decision and each valdrada asset's actual rights? V195 already includes a glTF importer/exporter. Recommend an explicit **static color-and-geometry exchange profile** with measurable loss reports, hard failure for unsupported required features, accurate bounds/pivot/units, and independent validation. Adapt separately verified procedural assets only after file-level license and attribution review. A source-level concave-face counterexample exposes why fan triangulation needs a guard or robust triangulator. This is not evidence of an executed app round trip; tests, asset conversion and independent review remain open.

## 2. Question and hypotheses

- H1: A glTF import needs a new loader. **Rejected:** V195 code already uses pinned three.js GLTFLoader and GLTFExporter.
- H2: A successful import reproduces all source appearance and structure. **Rejected:** code groups by color/transparency into locked solids and says textures are not drawn; scene hierarchy and PBR cannot be assumed preserved.
- H3: glTF axes need a global metres-to-feet or Z-up conversion. **Rejected for conforming glTF + the inspected app assumptions:** standard and code use right-handed meters, +Y up. Individual authoring tools can still embed transforms, so measure at the asset boundary.
- H4: A triangle fan is valid for every polygon. **Rejected** by the attached U-shaped polygon experiment: absolute triangle area 11 against polygon area 7; signed area happens to remain 7. This tests the algorithm in isolation, not an actual imported or exported scene.
- H5: Every asset from valdrada has one permissive license. **Rejected:** upstream's own table distinguishes MIT code, CC BY assets, ODbL data, and pedestrian models with additional MetaHuman terms.
- H6: V195 is browser-proven end to end. **U:** its own research says browser check had not run; this session did not execute it.

## 3. Method and search log

2026-11-13: read the phase task, the glTF 2.0 standard, Khronos validator's description, V195 importer and research note, and valdrada's own licensing and acknowledgements. Searches: `buildingSMART IFC GlobalId object placement units`, `Khronos glTF validator required extensions materials`, `valdrada procedural pedestrians trees vehicles github license`, `site:github.com/BradleyPham1906/BIM-Personal "valdrada"`. Kept the primary specification, app code and upstream license table; search snippets were discovery only. No asset binaries were downloaded or converted. Ran one offline Node polygon experiment (script and raw result attached). No browser, validator or independent reviewer was run. P = source directly read; U = unknown/proposal. Research protocol independent-review and execution gates remain unmet.

## 4. Findings by topic

### Contract and presentation

[P/high] glTF 2.0 defines a right-handed coordinate system, +Y up, +Z forward and linear distances in meters. A node can transform its contents; identity at the root does not establish dimensions or floor pivot after authoring and conversion. Required extensions describe functionality needed to load properly. Texture color and numeric data use different transfer semantics: base-color textures are sRGB, metallic/roughness are linear, while the base-color factor is a linear multiplier. [Khronos specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html).

[P/high] The V195 import takes meshes with their world transforms, groups by color and approximate opacity, welds positions at 1e-5, removes faces with duplicate welded vertex indices, stores locked solids, and may place an import of up to 20,000 resulting triangles in the Assets library. Its maximum input processing is 300,000 triangles with warning above 100,000; the code can skip a whole group when that group would exceed the limit. Textures are not drawn, KTX2 is not read, and separate external resources are called unfinished by its own build note. The runtime configures Draco and meshopt decoders, but that is not proof every compressed file works in every deployment. [Code](https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/io/gltf.js), [V195 research](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-gltf.md).

[P/high] Export walks visible elements, exports per-element meshes under layer nodes with id/type/layer extras, applies positions via Float32Array, emits material color and transparency, computes vertex normals, and fans polygon faces. Texture/material fidelity, hidden layer handling, units and IDs must be declared as profile semantics and tested independently. For an IFC-like engineering exchange, glTF extras are application data, not a substitute for IFC semantics.

### Provenance is asset-specific

[P/high] Valdrada's table licenses source code MIT, OSM-derived compiled city ODbL, named original street-tree and vehicle models CC BY 4.0, CARLA vehicles/props CC BY 4.0, Rocketbox pedestrian set MIT, and the CARLA pedestrian bank CC BY 4.0 **plus** Epic MetaHuman terms. It identifies a separate built-in procedural pedestrian as MIT and using no third-party assets. Preserve the correct upstream notice, source, license, modifications and derivative chain for each selected item. No conclusion that all pedestrians are MIT is justified; do not mix photoreal bank into the procedural subset. [License table](https://github.com/mkturkcan/valdrada/blob/main/LICENSING.md), [acknowledgements](https://github.com/mkturkcan/valdrada/blob/main/ACKNOWLEDGEMENTS.md). Upstream reports further conditions for MetaHuman; verify applicable primary terms before use rather than relying on this summary as legal advice.

[P/medium] Khronos provides a validator for specification and extension problems. A clean validator report is necessary for the proposed profile but cannot establish correct appearance in the target app, provenance or a dimensionally correct round trip. [Validator](https://github.com/KhronosGroup/glTF-Validator).

## 5. Alternatives compared

Criteria: correctness under the current renderer, reuse, asset rights, size and operational scope.

| Approach | Benefit | Trade-off |
| --- | --- | --- |
| A. Color + static geometry, current V195 model | Reuses code; measurable and fast to scope | No texture/PBR/hierarchy fidelity; must expose losses |
| B. Full-fidelity scene referenced as an asset | Retains materials, hierarchy and animation in principle | New renderer, storage, editing and extension support burden |
| C. Pre-convert approved assets to V168 kinds | Consistent internal kinds and explicit credits | Conversion can lose dimensions, rights metadata and semantics; requires per-asset audit |
| D. Replace importer/exporter entirely | Could offer broader support | No evidence justifies replacement; regression risk |

Recommend A as the acceptance baseline and C as a later, separate curated workflow; adopt B only after the fidelity and performance needs are demonstrated. No implementation decision or timeline is implied.

## 6. Reproducible counterexample

Run `node experiment.js`. The polygon is `(0,0),(3,0),(3,3),(2,3),(2,1),(1,1),(1,3),(0,3)`. Shoelace polygon area = 7; six fan triangles around vertex 0 have absolute areas totaling 11, but signed areas total 7. A signed-area-only check hides overlap/outside fill. This demonstrates the index fan copied from the code is not valid for all concave faces. It does not prove that this particular polygon can be created in the app or that every exported concave face fails. Actual visual and geometry verification is required. The machine-readable inputs, triangle indices and results are attached.

## 7. Proposed acceptance and falsification matrix

| Case | Input / expected observation |
| --- | --- |
| Dimensions | Meter box with nested scale; compare 3 axes and bounding box before/after to a predeclared tolerance |
| Axis/pivot | +Y up, +Z front, floor origin; inspect orientation and insertion position in app and second viewer |
| Transform | Nested rotation, nonuniform and negative scale; check winding, normals, bounding box and mirroring |
| Hierarchy / repetition | Instanced nodes; verify whether grouping and node identities survive or disclose flattening |
| Appearance | Solid color, PBR, texture, alpha OPAQUE/MASK/BLEND, vertex colors and double-sided; record each loss rather than compare only color |
| Extensions | plain GLB, Draco, meshopt, KTX2 and unknown required extension; explicit supported/unsupported outcome and no silent false success |
| Files | embedded glTF/GLB, missing external .bin/image, corrupt buffer and invalid accessor; graceful error without partial mutation |
| Limits | 19,999 / 20,000 / 20,001 for Assets; 299,999 / 300,000 / 300,001 input; groups straddling cap and skipped counts |
| Weld | points straddling 1e-5 quantization cells, very small gaps, separate hard edges and degenerate triangles; no unreported geometric collapse |
| Export | convex and concave faces, including U shape, hidden layers, large coordinate offsets, non-ASCII names, id extras; validator and second viewer |
| Persistence | import, undo/redo, save/reopen, Assets replace and source names; compare IDs, geometry and disclosed losses |
| Procedural sources | manifest includes exact asset paths, source revision, license, attribution, measured dimensions, modifications and intended use; no MetaHuman mix-up |

All fixture checks are proposed, not results. Collect input hash, app commit, browser build, metrics, output and raw validator log. Use public/synthetic fixtures and a license-clean reference set.

## 8. Existing app and work-order decomposition

- `src/js/engine/io/gltf.js`: V195 reader, exporter, limits, materials, weld, Assets path, and fan index loop. The tool extraction did not preserve reliable file-line numbers; pin a commit and annotate line ranges in the work order.
- `docs/research/research-gltf.md`: notes Node reading tests and says browser check had not run; do not cite the latter as a test passed.
- First reconcile runtime version, deployment branches and existing tests; measure current behavior before changing importer. Second define fidelity profile and diagnostics. Third fix only verified failure modes (including concave faces when present), with regression fixtures and validator output. Fourth make a per-file provenance manifest, adapt approved procedural tree/vehicle/pedestrian assets to the existing V168 kinds and test actual dimensions and placement. Fifth run independent browser/viewer and save-reopen tests. Keep this phase's results separate from IFC H3 and 3D Tiles streaming.

## 9. Risks and threats to validity

No end-to-end app execution, browser tests or file conversion; source is moving main; experiment is geometry-only; no device performance or accessibility measurement; extensions depend on runtime packaging; legal terms can change and derivative assets may have mixed sources; no independent review; larger colors-only imports may grow project size. V195's limits are not an assurance of performance. The task's 16-hour estimate is historical, not a verified cost or commitment.

## 10. Open and completion gates

Pin repository revision; inventory current browser and exporter tests; define exact fixture corpus, profile and tolerance; execute across supported browsers and another viewer; investigate renderer/material and decoder limits; validate output; resolve current procedural-asset source paths and check licenses per file; test dimensions and conversion; independently reread the findings. Until then full research and readiness under the repository protocol are **not complete**. This report was initially drafted while GitHub was unavailable; the open validation gates remain unchanged.

## 11. Owner decisions, not yet made

Proposed choices: accepted material fidelity and loss warnings; supported compression/texture extensions and offline fallback; per-asset triangle/storage limits and measured device targets; whether to accept static procedural assets or richer scenes; attribution and asset distribution approach; geometric tolerances and behavior on over-limit partial imports. Existing in-house-first preference stands. None of these proposed choices is an owner approval.

## 12. References

Accessed 2026-11-13. [glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html), P, coordinate system, extensions and materials; [V195 code](https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/io/gltf.js), P; [V195 research](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-gltf.md), P for the authors' report; [Khronos validator](https://github.com/KhronosGroup/glTF-Validator), P; [Valdrada licensing](https://github.com/mkturkcan/valdrada/blob/main/LICENSING.md) and [attributions](https://github.com/mkturkcan/valdrada/blob/main/ACKNOWLEDGEMENTS.md), P for upstream statements; [research protocol](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-protocol.md), P.


---
Research evidence files: [`experiments/notion-gltf/`](experiments/notion-gltf/). Original scripts and results reflect only the experiments described above.
