# Rendering efficiency for a living world

Research note for the World Engine (`docs/research/plan-world-physics.md`, part 6 and Stage C), one of three
parallel notes on the world's look (the others: weather and sky; assets). Written 2026-11-24 by a research agent
under `docs/research/research-protocol.md`. Nothing here is built; no repository file other than this note and the
experiments under `docs/research/experiments/world-look/re-*` was changed.

## 1. Abstract

**Question.** How should the app draw a neighbourhood that is alive (forests of trees, crowds of people, traffic)
at 60 fps on a desktop and 30 fps on a phone, given that its own renderer (`render/webgl.js`, `gpu-batches.js`,
`webgpu.js`) merges every object's triangles into 64 m chunks, has no instancing, no render level of detail and no
impostors, and that the rendered view (three.js 0.186.1) builds one merged mesh per chunk and look?

**Answer.** Five techniques, in this order of payoff: (1) GPU instancing of repeated meshes, which removes the
per-copy cost on the main thread and divides the memory of a forest by the number of trees (measured here: 1.6 MB
against 218 MB for 100,000 trees; 23 to 28 ms of main-thread time a frame to issue 100,000 separate draws, below
the timer's 0.1 ms for one instanced draw); (2) discrete levels of detail chosen by projected size with hysteresis,
ending in an impostor (a billboard for people far away, an octahedral impostor for trees); (3) culling by the
ground cells the app already has, applied to instance batches, with occlusion queries left for later; (4) compressed
textures (KTX2 with Basis Universal) once textured assets arrive; (5) crowds as instanced meshes animated from a
texture (vertex animation or baked bone matrices), never one skinned mesh per person.

**Recommendation.** Add an instance batch to the app's own scene description (one prototype mesh, a buffer of
per-instance place, turn, scale and table slot), drawn with `ANGLE_instanced_arrays` in the existing WebGL 1 context
and with `stepMode: "instance"` in WebGPU, so picking, selection and colour keep working through the existing slot
table. In the rendered view use three.js's own `InstancedMesh` (already in the vendored bundle). Levels of detail and
impostors follow; KTX2 waits for the asset pipeline. No new library is needed for the first two phases; meshoptimizer's
simplifier (MIT) and the Basis transcoder (Apache-2.0) are candidates for later, each needing the owner's approval
under the third-party rule.

## 2. The question and the hypotheses

What a good answer must decide: which technique the app's own renderer adopts first, and where it lands; what the
rendered view uses; what breaks (picking, selection, per-instance colour, outlines, transparency); what assets must
look like to be drawn this way; and what budgets a phone imposes.

| # | Hypothesis (falsifiable) | Outcome | Evidence |
|---|---|---|---|
| H1 | Issuing N copies as one instanced draw costs the main thread a constant amount, against a cost growing with N for one draw per copy | **Held** | Measured: one draw a copy took 0.1 to 0.3 ms (1,000), 0.7 to 1.5 ms (10,000) and 23.4 to 27.6 ms (100,000) of main-thread time a frame; one instanced or merged draw stayed below the timer's resolution at every N (section 6) |
| H2 | On this machine's renderer an instanced draw costs the GPU no more than the same triangles merged | **Failed here** (SwiftShader) | Instanced was 2.7 to 3.6 times slower than merged at 26 triangles a tree and 1.2 to 1.4 times at 138; the merged buffer drawn through the instanced call with one instance (`merged1`) was as fast as merged, so the cost is per instance in SwiftShader, not in the instanced call. Real GPUs differ (section 4.1, counter-evidence); not a prediction for a phone |
| H3 | Instancing a forest uses over 100 times less memory than merging it | **Held** | 1,602,028 bytes against 218,400,000 for 100,000 trees of 26 triangles (136 times); setup 1.1 to 1.5 ms against 328 to 394 ms |
| H4 | When every copy moves each frame, instancing re-sends far less than merged geometry | **Held** | 1.6 MB a frame against 93.6 MB at 100,000; merged's frame rate fell from 2.0 to 2.3 fps to 1.2 when animated, instanced's did not change. The app's own scheme already avoids this (a move rewrites a 32-byte table row, `gpu-batches.js:144-147`), but only for translation, and only after every copy's triangles are stored |
| H5 | The vendored three.js bundle already has `InstancedMesh`, `BatchedMesh`, `LOD`, `SkinnedMesh` and the meshopt decoder, but no `KTX2Loader` and no simplifier | **Held** | `grep` of `runtime/three/0.186.1/bim-three.min.js` (section 8) |
| H6 | A WebGL 2 occlusion query's answer never arrives in the task that issued it | **Held** | The WebGL 2.0 specification's text; measured: not available after 1,000 polls in the same task, available after 2 animation frames (30.5 ms) |
| H7 | A phone's draw-call budget is hundreds, not thousands | **Held (S)** | Arm GPU Best Practices 3.4: "fewer than 500 draw calls per frame" on OpenGL ES, fewer than 1,000 on Vulkan |
| H8 | A phone draws 1,000 animated people at 30 fps with instancing and texture-driven animation | **Open (U)** | No phone here. Desktop evidence only (section 4.5) |
| H9 | Instancing in the app's renderer needs a WebGL 2 context | **Failed** | `ANGLE_instanced_arrays` is in WebGL 1 everywhere the app runs (MDN: Chrome 32, Firefox 47, Safari 8, Edge 12); measured present here. The app's context is WebGL 1 (`webgl.js:63`) |

## 3. Method

**Sources by kind.** Specifications (WebGL 2.0 and the `ANGLE_instanced_arrays` extension from the Khronos
repository; WebGPU from the gpuweb repository; OGC 3D Tiles; glTF's `EXT_mesh_gpu_instancing`,
`EXT_meshopt_compression`, `KHR_texture_basisu`); compatibility data (MDN's browser-compat-data JSON); open
implementations read as text (three.js r186's `InstancedMesh`, `BatchedMesh`, `LOD`, `WebGLRenderer`, `KTX2Loader`,
`SimplifyModifier`; CesiumJS's `Cesium3DTile.getScreenSpaceError`; meshoptimizer's JS documentation; Basis
Universal's README and licence); vendors' documents (Arm GPU Best Practices 3.4 and Arm's optimisation advice
guide, both PDFs; Apple's Metal and OpenGL ES guides); practitioners (GPU Gems 3 chapter 2; three.js forum threads
with measurements; the Godot octahedral impostor project and agargaro's three.js libraries); and the app's own code.
Downloads are in the session's scratchpad (`re-src/`), read as text, never run.

**Experiments.** Three scripts under `docs/research/experiments/world-look/`: `re-instancing.html` with its two
runners, and `re-caps.html` with its runner (section 6). Headless Chromium 158.0.8127.36 from Playwright 1.63.0.

**Independent check.** Not yet done: the protocol's second reader is for the lead to commission. The facts the code
would use are marked P below so that reader can go straight to them.

### Search log

| Where | Query or address | What came back | Kept or set aside, and why |
|---|---|---|---|
| GitHub raw, KhronosGroup/WebGL | `specs/latest/2.0/index.html` | The WebGL 2.0 specification | Kept (P): instanced draws, divisor, queries and the same-task rule |
| GitHub raw, KhronosGroup/WebGL | `extensions/ANGLE_instanced_arrays/extension.xml` | The WebGL 1 instancing extension | Kept (P) |
| GitHub raw, mdn/browser-compat-data | `WebGL2RenderingContext`, `ANGLE_instanced_arrays`, `GPU`, `WEBGL_multi_draw`, compressed-texture JSON | Version tables | Kept (P for MDN's data; its accuracy is MDN's) |
| GitHub raw, gpuweb/gpuweb | `spec/index.bs` | WebGPU source | Kept (P): `stepMode "instance"`, `draw(…, instanceCount, …, firstInstance)`, `drawIndirect`, `occlusionQuerySet`, `indirect-first-instance` |
| GitHub raw, mrdoob/three.js at tag r186 | `InstancedMesh.js`, `BatchedMesh.js`, `LOD.js`, `WebGLRenderer.js`, `KTX2Loader.js`, `SimplifyModifier.js`, `libs/basis/README.md`, examples | Source of the vendored version's release | Kept (P) |
| Local | `grep` of `runtime/three/0.186.1/bim-three.min.js` and `tools/three/build_three.mjs` | Which classes the bundle carries | Kept (P) |
| GitHub raw, CesiumGS | `3d-tiles/specification/README.adoc`, `cesium/.../Cesium3DTile.js` | Screen-space error and its formula | Kept (P) |
| GitHub raw, KhronosGroup/glTF | three extension READMEs | Instancing, meshopt and Basis extensions | Kept (P) |
| GitHub raw and npm, zeux/meshoptimizer | `LICENSE.md`, `js/README.md`, npm `meshoptimizer` latest; unpkg file sizes | MIT; simplifier API; 1.3.0; `meshopt_simplifier.js` 67,671 bytes | Kept (P) |
| GitHub raw, BinomialLLC/basis_universal | `LICENSE`, `README.md` | Apache-2.0; ETC1S about 0.3 to 3 bpp, UASTC LDR 8 bpp | Kept (P) |
| HTTP HEAD, three.js r186 `examples/jsm/libs` | basis transcoder, zstddec, ktx-parse, meshopt decoder | 527,333 + 57,529 + 39,754 + 19,932 bytes | Kept (P, sizes as served) |
| developer.arm.com | `documentation/101897/latest/` | 403 to a script | Refused; recorded |
| Web search | "Arm Mali GPU best practices guide draw calls batching instancing" | Pointers to documentation-service.arm.com PDFs, a 2013 blog's "under 50" figure | The two PDFs fetched and read (P); the 2013 figure set aside as dated and demo-specific |
| documentation-service.arm.com | two PDFs | Arm GPU Best Practices 3.4 issue 10 (2025); Optimization advice 1.0 issue 01 (2024) | Kept (P for Arm's advice) |
| developer.apple.com archive | Metal Best Practices; OpenGL ES guide (vertex data); Native Screen Scale | No draw-call number; advice to provide several levels of detail and to render at native scale | Kept (P, but dated archive documents) |
| docs.qualcomm.com | Adreno best practices page | A page that needs script to render; nothing readable | Set aside; recorded as unread |
| shaderbits.com | `blog/octahedral-impostors` | 404 ("Page Not Found"), with and without `www` | Refused; Brucks' write-up known only through citing projects (S) |
| Web search | "octahedral impostors Ryan Brucks shaderbits" | Godot, three.js forum, meep engine, Unity and Houdini pointers | Kept the Godot project (MIT) and the forum threads read in full as JSON |
| GitHub raw | `wojtekpil/Godot-Octahedral-Impostors`, `agargaro/octahedral-impostor`, `agargaro/instanced-mesh`, `agargaro/batched-mesh-extensions`, `Ctrlmonster/three-octahedral-impostor` | READMEs and licences: all MIT | Kept as prior art (code not read line by line) |
| discourse.threejs.org (`.json`) | Crowd in one draw call (2026); forest of octahedral impostors (2025); octahedral impostors (2025); skinned meshes CPU bottlenecks (2023); three counter-evidence threads | Practitioners' measurements | Kept (S, single-author measurements) |
| developer.nvidia.com | GPU Gems 3 chapter 2 | Instanced skinned crowd: almost 10,000 characters at 30 fps (GeForce 8800 GTX) | Kept (S, 2007 desktop) |
| blog.unity.com | Animation instancing for SkinnedMeshRenderer | 404 | Set aside |
| Web search (counter-evidence) | "instancing slower than merged geometry small meshes" | Forum reports where merged or naive equalled or beat instanced in Chrome | Kept, threads read in full (section 4.1) |
| Sibling agent's experiment | `as-tree-triangles.out.txt` (same folder) | Procedural trees of 3,616 to 22,566 triangles, low LOD about 3,400 | Used for budgets only (S: another agent's unreviewed output) |

## 4. Findings by topic

### 4.1 Instancing

**WebGL 2 (P, high).** The WebGL 2.0 specification adds `vertexAttribDivisor(index, divisor)` ("Set the rate at which
the vertex attribute identified by index advances when drawing"), `drawArraysInstanced` and `drawElementsInstanced`
("Vertex attributes which have a non-zero divisor advance once every divisor instances"), each referring to OpenGL ES
3.0.6 section 2.9. `gl_InstanceID` is available in GLSL ES 3.00. MDN's data: Chrome 56, Chrome Android 58, Firefox
51, Safari 15 (iOS mirrors Safari).

**WebGL 1 (P, high).** The same three calls exist in WebGL 1 as `ANGLE_instanced_arrays`
(`vertexAttribDivisorANGLE`, `drawElementsInstancedANGLE`), supported per MDN since Chrome 32, Chrome Android 30,
Firefox 47, Safari 8 and Edge 12, and present in this Chromium (measured). The app's renderer asks for `'webgl'`
(`webgl.js:63`), so instancing does not require moving it to WebGL 2. WebGL 2 would add `gl_InstanceID`, integer
attributes and uniform blocks; it is a separate, larger change.

**WebGPU (P, high).** A vertex buffer layout with `stepMode: "instance"` advances per instance;
`draw(vertexCount, instanceCount, firstVertex, firstInstance)` and `drawIndexed(...)` take an instance count and a
first instance; `drawIndirect`/`drawIndexedIndirect` read those from a buffer, which a compute pass can write (GPU-side
culling), with a non-zero `firstInstance` there needing the `indirect-first-instance` feature. MDN: Chrome 113 on
ChromeOS, macOS and Windows (144 adds Linux on some GPUs), Chrome Android 121, Safari 26, Firefox 141 partial
(Windows; Apple silicon later). The app's WebGPU path already reads its table from a storage buffer
(`webgpu.js:35`), which suits per-instance lookups.

**three.js r186 (P, high).** `InstancedMesh(geometry, material, count)` holds `instanceMatrix` (16 floats an
instance), an optional `instanceColor` (3 floats, made on the first `setColorAt`), an optional `morphTexture`
(per-instance morph weights, `setMorphAt`), and `raycast` over every instance. Its `computeBoundingSphere` spans all
instances, so culling is all or nothing for the mesh (no per-instance culling). `BatchedMesh(maxInstanceCount,
maxVertexCount, maxIndexCount, material)` holds several geometries (`addGeometry`) and instances of them
(`addInstance`, `setGeometryIdAt`, `setVisibleAt`), keeps matrices, colours and an indirection in float and integer
data textures, and by default culls and sorts per instance (`perObjectFrustumCulled`, `sortObjects`). The renderer
draws it with `WEBGL_multi_draw` when present; without it, a loop of one draw per instance with a `_gl_DrawID` uniform
(`WebGLRenderer.js:1315-1333`). MDN: `WEBGL_multi_draw` in Chrome 86 and Safari 15, **not in Firefox**, so a
`BatchedMesh` in Firefox costs one draw per instance. Both classes are in the vendored bundle (section 8).

**What breaks (P from the app's code, high).**
- *Picking* (`gpu-pick.js:12-79`): the pick shader writes `aObj+1` from a per-vertex attribute. With instancing,
  `aObj` becomes a per-instance attribute (divisor 1) and nothing else changes in the shader. The reverse lookup from
  slot to object loops over every slot (`gpu-pick.js:74-75`), O(N) a click; with 100,000 instances it wants an array
  from slot to owner.
- *Selection highlight and per-instance colour*: both come from the table row (`gpu-batches.js` vertex shader, `b.xyz`
  colour, `b.w` selection state). If each instance owns a slot, highlight and colour work unchanged; a forest of
  100,000 trees costs 100,000 rows, 3.2 MB of float texture at two texels a row (`BIM_GB_TEXW` 1024), within limits.
  The alternative (one slot per batch, colour per instance in the instance buffer) loses per-tree selection.
- *Place*: a row holds an offset only (`v[0..2]=o.pos`, `gpu-batches.js:144`). Trees and people need a turn about the
  vertical and a scale, so the instance buffer carries them (x, y, z, yaw, scale: 20 bytes, or 32 with the slot and
  padding); the full quaternion of V282 can come later.
- *Outlines*: edges are drawn only when the scene has at most `GL_EDGE_FACE_LIMIT` (20,000) faces
  (`gpu-batches.js:166`); a forest would switch outlines off for everything. Instanced vegetation must be left out
  of that count and of the outline pass.
- *Transparency*: the table's alpha splits opaque and blended passes per row (`gpu-batches.js` vertex shader), which
  still works per instance; leaves should be alpha-tested (discard), not blended, to stay out of the sorted pass.
- *Counting*: `A3D.glFaces` drives GPU picking's threshold (`gpu-pick.js:83`); it should count drawn instances at
  their level of detail.

**Counter-evidence (S, medium).** Merged geometry has often matched or beaten instancing in practice: Don McCurdy
(three.js maintainer, 2021) that a single-triangle `InstancedMesh` is "very unlikely to improve performance" and
that there is no vertex-count rule; a 2020 thread where Chrome on Intel HD 630 and an Adreno 506 phone gave the
same frame rate for naive, merged and instanced, while Firefox Android gave 39 fps instanced, 49 merged and 25 naive
at 1,000; a 2022 thread where Chrome on Windows gave 19 fps naive, 16 merged and 17 instanced at 10,000, while an
M1 gave 120 instanced and 40 naive. This note's own measurement (section 6) agrees that on SwiftShader merged beats
instanced for tiny meshes. What instancing always wins is memory (H3) and main-thread time (H1); its GPU time
depends on the driver and on how many vertices each instance has. For the world's real assets (trees of 3,400 to
22,000 triangles, people of a few hundred to a few thousand), the per-instance overhead is amortised over many
vertices, and merging is ruled out by memory alone (a 14,000-triangle tree merged 10,000 times at the app's 28 bytes
a vertex is about 12 GB).

### 4.2 Level of detail and impostors

**Discrete levels with hysteresis (P, high).** three.js's `LOD` holds levels `{object, distance, hysteresis}`; when a
level is visible its switching distance is reduced by `distance * hysteresis` (`LOD.js:188-210`, `250-271`), so a
tree on the boundary does not flicker. The fraction is the author's choice (default 0). Arm's guides (P) advise
"dynamic mesh level-of-detail to select simpler meshes as objects get further from the camera" and contiguous vertex
ranges per level; Apple's OpenGL ES guide (P, archive) advises "multiple versions of your model at different levels
of detail".

**Screen-space error (P, high).** OGC 3D Tiles selects detail by a maximum screen-space error in pixels from each
tile's geometric error; CesiumJS computes it as `error = geometricError * height / (distance * sseDenominator)`
(`Cesium3DTile.js:1012-1013`, where `sseDenominator` is `2 tan(fovy/2)` for a perspective frustum). For a single
model the same idea is a projected size: switch when the object's bounding radius covers fewer than k pixels. The app
already does this for traffic (a car under 3 pixels long is a dot, a walker under 6 pixels tall is a dot:
`simulation/traffic-draw.js:78`, `113`, `121`), and its projection gives pixels a metre directly
(`webgl.js:33-47`, `f=H*1.2`), in perspective and in plan alike.

**Cross-fading (S, medium).** A dithered or alpha cross-fade hides popping but draws two levels during the fade.
A practitioner who built an octahedral impostor system (three.js forum, 2025) argues that impostors switched when the
model covers no more pixels than the bake's resolution need no fade. Recommendation: no fade at first; add a dithered
fade (a screen-door discard on a per-instance fade value) only if popping is seen.

**Octahedral impostors (S, medium).** Brucks' write-up (Epic, 2018) could not be read (shaderbits.com answered 404).
From the projects citing it: a tree is rendered from many directions on a hemi-octahedron or octahedron into one
atlas (for example 16 by 16 views in 2,048 pixels), and at run time one quad samples and blends the three nearest
views, optionally with depth for parallax. Open implementations, all MIT: wojtekpil's Godot project (1,400 trees on
impostor planes in its README), Ctrlmonster's three.js prototype ("very hacky", by its author), and agargaro's
`octahedral-impostor` for three.js, whose demo draws 200,000 trees with `InstancedMesh2`, a BVH for culling, a
meshoptimizer level from 15 to 100 m and an impostor beyond 100 m. The overdraw of a transparent quad is the known
cost; that author's correspondent clipped about 30 percent of pixels with a five-vertex hull. For people, a plain
camera-facing billboard (a few views baked) is enough: they are seen from the side and small at distance.

**Simplification in the browser (P, high).** meshoptimizer (MIT, Arseny Kapoulkine; npm 1.3.0) ships
`meshopt_simplifier.js` (67,671 bytes, ES module with the WebAssembly embedded) with `simplify(indices, positions,
stride, targetIndexCount, targetError, flags)`, `simplifyWithAttributes`, `simplifySloppy` (merges disjoint parts, for
far levels of foliage) and `compactMesh`; it needs welded vertices. In r186, three.js's `SimplifyModifier` is itself
a wrapper over `MeshoptSimplifier` (it was an edge-collapse of Melax's method in older releases), so it brings nothing
the simplifier does not. The vendored bundle has neither. Simplification is best done once, when an asset is
prepared, not every session.

### 4.3 Culling and draw-call budgets

**What the app has (P).** Chunks are grouped by 64 m ground cells (`BIM_GB_CELL`, `gpu-batches.js:20`) and a chunk
wholly outside the view frustum is not drawn (`bimSceneCull`, `gpu-batches.js:170-184`), in both engines. That is the
right grain for instance batches too: one batch per prototype, level and cell.

**Per-instance culling (P, high).** WebGL has no base-instance draw in core WebGL 2, so a sub-range of an instance
buffer cannot be drawn without rebinding; the simplest correct scheme keeps one instance buffer per cell and prototype
(a cell out of view costs nothing), or compacts the visible instances into a stream buffer each frame (20 to 32
bytes each). WebGPU can draw from `firstInstance` directly and can cull in a compute pass that writes indirect draw
arguments. Arm (P): "Instancing allows the application to test and cull individual instances", and "Do not make
batches so large that frustum culling, and sorting for front-to-back rendering order, become inefficient."

**Occlusion queries (P, high).** WebGL 2 has `ANY_SAMPLES_PASSED` and `ANY_SAMPLES_PASSED_CONSERVATIVE` queries;
the specification forbids a result in the task that issued it ("must not be made available until control has returned
to the user agent's main loop"), and a single `requestAnimationFrame` is not guaranteed to be enough. Measured here:
2 frames (30.5 ms). Arm (P): prefer any-samples queries and read only when available. WebGPU has
`occlusionQuerySet` and `beginOcclusionQuery`. A query a frame late means a culled object pops in a frame late; for a
neighbourhood whose occluders are buildings, cells, distance and levels of detail come first, and occlusion queries
per cell are a later refinement.

**Budgets (P for Arm; S and U for the rest).** Arm GPU Best Practices 3.4 (2025): "For OpenGL ES, aim for fewer than
500 draw calls per frame. For Vulkan, aim for fewer than 1000", stated as approximate for current Arm hardware;
WebGL in Chrome on Android runs over OpenGL ES or Vulkan through ANGLE. Arm also expects about half of all triangles
to be back-face culled and warns that triangles hitting no sample point mean geometry too dense: a level-of-detail
problem. No vendor gives a triangle budget for a phone; the numbers commonly quoted (about one million triangles a
frame at 30 fps for mid-range phones) are U and must be measured on a phone. The main-thread budget in the plan
(desktop frame 16.7 ms with drawing the remainder after 8 ms of simulation) makes the measured 23 to 28 ms to issue
100,000 draws impossible on its own, on a desktop CPU.

### 4.4 Texture compression

**Formats (P, high).** Basis Universal (Apache-2.0) stores ETC1S (about 0.3 to 3 bits a pixel on disk, low to
medium quality) or UASTC LDR 4x4 (8 bits a pixel, high quality), transcoded in the browser to whatever the GPU takes:
ASTC, ETC2, BC7 or BC1/BC3, PVRTC. Uncompressed RGBA is 32 bits a pixel in GPU memory, so a compressed texture takes
4 times less (8 bpp formats) or 8 times less (4 bpp formats such as ETC1 or BC1) plus mipmaps either way. Arm (P)
advises offline compression, "ideally ASTC". glTF carries it as `KHR_texture_basisu` in a `.ktx2` container.

**In three.js (P, high).** `KTX2Loader` (r186) runs the Basis transcoder in a worker pool, picks the target from the
renderer's extensions (`detectSupport`), and imports `ktx-parse` (MIT) and `zstddec` (MIT). The files it needs from
three.js r186: `basis_transcoder.wasm` 527,333 bytes, `basis_transcoder.js` 57,529 bytes, plus the two modules
(39,754 and 19,932 bytes). The vendored bundle has none of them, though its `GLTFLoader` already names
`KHR_texture_basisu` and asks for `setKTX2Loader` when a file uses it. MDN: ASTC in Chrome 47, Firefox 53, Safari 12;
ETC in Chrome 63, Firefox 55, Safari 13.1; S3TC not on Android. Measured here: ASTC, ETC, ETC1, S3TC and BPTC
advertised by SwiftShader, PVRTC not.

**Geometry (P, high).** The bundle already has the meshopt decoder (MIT) and Draco (Apache-2.0, `runtime/three/
0.186.1/draco`), and `io/gltf.js:135-138` wires both. `EXT_meshopt_compression` decodes at 1 to 3 GB/s with SIMD
(meshoptimizer's documentation) and keeps vertex order friendly to the GPU; Draco compresses smaller but decodes
slower. For instanced assets meshopt is the better fit; neither changes what the GPU draws.

### 4.5 Animated crowds

**Approaches (S, medium).** GPU Gems 3 chapter 2 (NVIDIA, 2007): instanced skinning with every frame of every
animation encoded in a texture of bone matrices read in the vertex shader, per-instance data indexed by instance ID,
mesh variety by instanced sub-meshes, and a per-instance level of detail: "almost 10,000 characters ... at 30
frames/sec" on a GeForce 8800 GTX. A vertex animation texture (VAT) stores vertex positions per frame instead of
bones: no skinning cost, more memory, fine for a walk cycle. In three.js r186, `InstancedMesh.setMorphAt` gives each
instance its own morph weights through `morphTexture`, which can drive a small VAT-like cycle without a custom shader.

**Measurements by practitioners (S, low to medium).** One `SkinnedMesh` per person is the wrong path: a 2023 forum
case study found frame rates below 60 beyond about 200 skinned units with 25 bones on an i7-4720HQ, the cost being
the CPU's animation mixing and matrix updates, not the GPU. agargaro's `InstancedMesh2` (MIT) shows "Skinning 3k
instances". A 2026 three.js crowd ("Where's Walter?") draws all characters in one `InstancedMesh`, animates in the
shader, lowers detail by distance and facing, and updates far characters less often; its author reports 240 fps
"up to 100,000 people" on his desktop. None of these is a phone.

**For the app.** People (walkers in `simulation/traffic-walkers.js`, drawn today as canvas-2D columns and dots, one
`ctx.fill` each, `traffic-draw.js:86-119`) become instances of a few low-poly bodies with a walk cycle in a texture
indexed by a per-instance phase; beyond a few tens of pixels tall, a billboard; below 6 pixels, a dot as now. How
many a phone draws at 30 fps is H8, open.

## 5. The alternatives compared

Criteria, stated before the comparison: (a) main-thread cost a frame at 10,000 to 100,000 copies; (b) GPU memory;
(c) cost when copies move every frame; (d) picking, selection and colour through the existing slot table; (e) works in
both of the app's engines and the WebGL fallback; (f) a new library and the owner's approval; (g) effort and files
touched.

| Option | (a) | (b) | (c) | (d) | (e) | (f) | (g) |
|---|---|---|---|---|---|---|---|
| A. Keep merging (today) | Low per frame, but `bimSceneSync` walks every object every frame | Grows with copies: unworkable for real trees | Translation only, 32 bytes a row | Works | Yes | None | None |
| B. The app's own instance batches (WebGL 1 extension, WebGPU instance step) | Constant per batch and cell | One mesh per prototype + 20 to 32 bytes an instance | Instance buffer rewrite: small | Works if each instance owns a slot | Both engines | None | One new render file, edits to three files |
| C. three.js `InstancedMesh` in the rendered view | Constant | As B, plus 64 bytes a matrix | `instanceMatrix` rewrite | three.js raycast; the app's pick does not see it | Rendered view only | None (vendored) | Edits to rendered-scene/core |
| D. three.js `BatchedMesh` | Constant with `WEBGL_multi_draw`; one draw an instance in Firefox | Shared buffer of all geometries | Texture rewrite | As C | Rendered view only | None | As C |
| E. agargaro's `InstancedMesh2` (per-instance BVH culling, LOD, skinning) | Lowest with culling | As C | As C | As C | Rendered view only | New library (MIT), research and approval; TypeScript ES modules and a BVH dependency | Medium |
| F. Impostors and billboards (complement to B or C) | Constant | One atlas a prototype | Same as instances | As B | Both | None if written here; else as E | Medium, after B |

**Recommendation.** B first, because it is the only option that keeps picking, selection, layers and colour lenses
working through one description for both engines, needs no library, and fixes the memory wall; C alongside it for
the rendered view, since `InstancedMesh` is already vendored; F after B, with levels chosen by projected size. D is
held back by Firefox's missing `WEBGL_multi_draw`; E is the reference to read, not to ship, unless B's culling and
levels of detail prove too slow. What would change this: a phone test showing instanced draws slower than merged for
the real assets (then merge per cell the near levels and instance only the far ones), or the owner choosing to make
the rendered view the main play view (then C, E and three's WebGPU renderer weigh more).

## 6. The experiments

All in `docs/research/experiments/world-look/`. Environment: Linux container, headless Chromium 158.0.8127.36
(Playwright 1.63.0), renderer `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader
driver)` from `WEBGL_debug_renderer_info`. **SwiftShader is a software renderer on the CPU; these numbers rank
methods on this machine and do not predict a phone or a desktop GPU.** WebGPU: no adapter by default; with
`--enable-unsafe-webgpu`, a SwiftShader adapter (`texture-compression-bc`, `-etc2`, `-astc`, `timestamp-query`,
`indirect-first-instance`). Other agents' experiments ran on the same machine at the same time, so absolute times
vary between runs by up to 30 percent; the ranking did not change.

**re-instancing.html** draws N copies of a low-poly tree (a five-sided trunk and two eight-sided cones: 26
triangles, 78 vertices; `detail=8` gives 64-sided cones, 138 triangles) on a 6 m grid at 1280 by 720, viewed at 45
degrees, all in view, three ways: `single` (one `drawElements` a copy, its place a uniform), `merged` (every copy baked
into one buffer, one draw: today's chunks), `instanced` (one copy, a per-instance vec4 with divisor 1, one
`drawElementsInstanced`), and in the second pass `merged1` (the merged buffer through `drawElementsInstanced` with one
instance). Measured: `syncMedianMs`, the median of frames each followed by a one-pixel `readPixels` (so the
software GPU has finished), at least 5 frames or 3 s; `rafFps` over 3 s of `requestAnimationFrame`; in the second pass
`submitMedianMs`, the main thread's time to issue a frame without waiting. `anim=1` moves every copy every frame.
Runners: `re-instancing-run.cjs` (2 runs; results `re-instancing-results.json`) and `re-instancing-probe.cjs`
(2 runs; `re-instancing-probe-results.json`). The second pass used 32-bit indices for every mode (the first, 16-bit for
`single` and `instanced`).

First pass, static, median ms a frame (two runs) and fps:

| N | Triangles | single | merged | instanced | Bytes on the GPU: merged / instanced |
|---|---|---|---|---|---|
| 1,000 | 26,000 | 23.3, 22.3 (32 fps) | 9.6, 10.2 (56 to 58) | 24.0, 24.9 (31 to 34) | 2,184,000 / 18,028 |
| 10,000 | 260,000 | 217.9, 226.4 (4.5) | 55.4, 59.9 (13 to 16) | 223.1, 206.1 (4.7) | 21,840,000 / 162,028 |
| 100,000 | 2,600,000 | 1,761, 1,618 (0.6) | 459, 441 (2.0 to 2.3) | 1,563, 1,604 (0.6) | 218,400,000 / 1,602,028 |

First pass, every copy moving: merged at 100,000 rose to 748 and 696 ms (1.2 fps), re-sending 93,600,000 bytes a
frame; instanced stayed at 1,770 and 1,845 ms, re-sending 1,600,000; single unchanged. Setup at 100,000: merged
328 to 394 ms, instanced 1.1 to 1.5 ms.

Second pass, static, median ms a frame (two runs) and the main thread's share:

| N, tree | single | merged | merged1 | instanced | Main thread, single | Main thread, the others |
|---|---|---|---|---|---|---|
| 1,000, 26 tris | 30.8, 23.5 | 14.4, 8.2 | 13.8, 9.1 | 26.1, 23.3 | 0.3, 0.1 ms | below 0.1 ms |
| 10,000, 26 tris | 251, 211 | 80, 55 | 80, 55 | 265, 195 | 1.5, 0.7 ms | below 0.1 ms |
| 100,000, 26 tris | 2,015, 1,573 | 614, 459 | 719, 443 | 1,969, 1,474 | 23.4, 27.6 ms | below 0.1 ms |
| 1,000, 138 tris | 47.6, 41.7 | 32.6, 32.2 | | 42.8, 44.8 | 0.1, 0.1 ms | below 0.1 ms |
| 10,000, 138 tris | 340, 346 | 253, 250 | | 311, 347 | 0.7, 0.7 ms | below 0.1 ms |

What they show: (1) the main thread's cost of one draw a copy grows with N and alone exceeds a 16.7 ms frame at
100,000 (H1); (2) on SwiftShader each instance costs about as much as a separate draw (instanced tracks single, not
merged), while the instanced call itself does not (`merged1` equals `merged`), so the gap is SwiftShader's
per-instance work and shrinks as instances carry more vertices (2.7 to 3.6 times at 26 triangles, 1.2 to 1.4 at 138;
H2 failed here); (3) instancing's memory and setup are about 1/136 and 1/250 of merging's (H3); (4) animation makes
merging re-send its whole buffer (H4). The main thread's share is small even for `single` at 10,000 because Chromium
queues WebGL calls to its GPU process; the driver's own cost per draw, which is what Arm's budget is about, is not
visible to a page.

**re-caps.html** (runner `re-caps-run.cjs`, results `re-caps-results.json`) reports what this browser offers:
WebGL 1 with `ANGLE_instanced_arrays`, `OES_texture_float` and 32 vertex texture units; WebGL 2 with
`WEBGL_multi_draw`, ASTC, ETC, ETC1, S3TC and BPTC, no `EXT_disjoint_timer_query_webgl2`; and an occlusion query
around one triangle: not available within the issuing task after 1,000 polls, available after 2 animation frames
(30.5 ms), any samples passed = 1 (H6).

## 7. Edges

- **Tiny meshes.** Below a few dozen triangles an instance (a grass blade, a far person's quad) may cost more than
  merged triangles on some drivers (section 4.1); merge them per cell instead, or draw several per instance.
- **Index size.** WebGL 1 without `OES_element_index_uint` limits a mesh to 65,535 vertices with 16-bit indices; the
  sibling agent's trees all fit 16-bit (its `uint16 ok` column). A merged chunk already uses `drawArrays`, so it has no
  index limit; an instanced prototype should be indexed.
- **Plan view.** Orthographic projection has no distance; the projected size (pixels a metre, `k=H*1.2/camDist`,
  `webgl.js:36`) works in both, so levels are chosen by size, never by distance.
- **Walk mode.** The near plane is 5 cm while walking (`webgl.js:34`); a tree at arm's length is at its finest level,
  and its impostor must never be chosen there.
- **Outlines and the 20,000-face limit.** Instanced vegetation outside the face count and the edge pass (section 4.1).
- **Transparency.** Leaves alpha-tested; a row's opacity below 0.999 moves an instance to the blended pass, which is
  not sorted per instance.
- **Precision.** Positions are float32 in the table; far from the origin trees jitter. The app already keeps the model
  near its origin (`bimMapOrigin`, `map/map-tiles.js:47`), which instance positions must share.
- **Firefox.** No `WEBGL_multi_draw`, so `BatchedMesh` falls to one draw an instance there; WebGPU partial.
- **Selection of one tree among 100,000.** The reverse lookup from a picked slot must be an array, not a loop.
- **Context loss and WebGPU device loss.** Instance buffers must be rebuilt from the description, as chunks are
  (`webgpu.js:284-298`).

## 8. What the app already has

| What | Where |
|---|---|
| WebGL 1 context, one program, per-object offset as a uniform | `src/js/engine/render/webgl.js:58-99` (`getContext('webgl')` at 63) |
| The scene as merged chunks per 64 m cell, a table of rows (offset, alpha, colour, selection) as a float texture | `src/js/engine/render/gpu-batches.js:13-20`, `64-91` (build, mesh triangulated once per reference), `113-166` (sync), `197-233` (shader), `234-269` (upload) |
| Chunk frustum culling, both engines | `gpu-batches.js:170-184` |
| WebGPU: the same chunks, the table as a storage buffer, render bundles per chunk and pass | `src/js/engine/render/webgpu.js:22-49`, `231-282`, `309-390` |
| GPU picking by slot colour, one pixel read back | `src/js/engine/render/gpu-pick.js:12-79` |
| Scene-only objects (Walk's figure) drawn but never saved or picked | `gpu-batches.js:109-112`; used by `walk/walk-mode.js:253` |
| A stress model and frame benchmark hooks | `webgpu.js:419-491`; `testing/hooks-drawing.js:476-477` |
| Size-based "dot" level of detail for cars and walkers, drawn in canvas 2D | `src/js/engine/simulation/traffic-draw.js:70-125` |
| The rendered view: one `WebGLRenderer`, pixel ratio 1, shadow maps, accumulation passes (16 to 256) for a still picture | `src/js/engine/render/rendered-core.js:31-33`, `104-121` |
| three.js 0.186.1 bundle (MIT) with `GLTFLoader`, `GLTFExporter`, `DRACOLoader`, meshopt decoder; in it, counted by `grep`: `InstancedMesh` 22, `BatchedMesh` 24, `LOD` 7, `SkinnedMesh` 21, `setMorphAt` path, `EXT_mesh_gpu_instancing`, `KHR_texture_basisu` (named, needs a `KTX2Loader`), `KTX2Loader` only as `setKTX2Loader`, `SimplifyModifier` 0 | `runtime/three/0.186.1/bim-three.min.js`; `tools/three/build_three.mjs` (entry points) |
| Draco decoder (Apache-2.0), pinned | `runtime/three/0.186.1/draco/`; `runtime/MANIFEST.json:126-137` |
| glTF import with Draco and meshopt | `src/js/engine/io/gltf.js:135-138` |

## 9. Risks and threats to validity

- **One software renderer.** All timings are SwiftShader; the GPU-time ranking (H2) may invert on real GPUs, as the
  forum threads show it does on some. Only H1, H3 and H4 (main-thread time, bytes) carry over with confidence.
- **The phone is untested.** No phone budget in this note is measured; Arm's draw-call figure is a vendor's
  approximate guideline; triangle budgets are U.
- **A shared machine.** Other agents ran experiments at the same time; absolute times varied by up to 30 percent.
- **Practitioners' numbers** (crowds, forests) are single-author reports on unnamed or desktop hardware.
- **Brucks' original article** was not read (404); octahedral impostors rest on implementations that cite it.
- **The app's description** walks every object every frame in JavaScript (`bimSceneSync`); instances must live in
  typed arrays outside `A3D.objs`, or that walk becomes the bottleneck at 100,000.

## 10. What is still open (U)

- Frame time on a phone (Adreno, Mali, Apple) for merged against instanced with the real tree and person assets: needs
  a phone, or the owner running `re-instancing.html` on one (it is standalone; open it with `?mode=instanced&n=10000`).
- A triangle budget per frame for a mid-range phone at 30 fps: no vendor document found that states one.
- How many animated people a phone draws at 30 fps (H8).
- Qualcomm's Adreno guide: unreadable here (page needs script); Arm's HTML pages refused (PDFs read instead).
- The cost of an octahedral impostor's overdraw on a phone's fill rate.
- Whether three.js's WebGPU renderer (not in the vendored bundle) would serve the rendered view better: not researched.

## 11. The owner's decisions

1. **Where the living world is drawn first:** in the app's own renderer (recommended: picking and layers keep
   working), or in the rendered view (three.js)?
2. **Per-instance selection:** may every tree and person own a table row (selectable one by one, 32 bytes each), or
   are forests selected as one element?
3. **Libraries for later phases:** research and approval of meshoptimizer's simplifier (MIT, 68 KB) for levels of
   detail, and of the Basis transcoder (Apache-2.0, about 585 KB with its JavaScript) plus `ktx-parse` and `zstddec`
   (MIT) for compressed textures, each loaded only when used?
4. **A phone check:** may a phone run the standalone experiment page once, so H2 and H8 can be settled before Stage C?

## 12. Recommendations and the order of work

1. **Instance batches in the app's renderer.** A new file `src/js/engine/render/gpu-instances.js` (under 400 lines):
   a world layer of prototypes (one mesh each) and per-instance typed arrays (x, y, z, yaw, scale, slot), bucketed by
   the 64 m cells. Draw: in `gpu-batches.js`, an instanced variant of the face program whose `aObj`, offset, yaw and
   scale come from a divisor-1 buffer (`ANGLE_instanced_arrays` in the existing WebGL 1 context); in `webgpu.js`, a
   second vertex buffer with `stepMode: "instance"` in the face pipelines, recorded into the same render bundles.
   `gpu-pick.js`: the same instanced draw in the pick pass and an array from slot to owner. Culling per cell through
   `bimSceneCull`'s test. Excluded from the outline pass and the face limit. Assets: indexed meshes, 16-bit indices,
   one material, colours as vertex colours or a small atlas, Y up, metres, origin at the base.
2. **Crowds and traffic on the GPU.** Move walkers and cars from canvas-2D fills (`traffic-draw.js`) to instance
   batches of a few prototypes, the walk cycle a per-instance phase into a small animation texture (the `setMorphAt`
   idea, or baked bone matrices as GPU Gems 3); the dot below 6 pixels stays.
3. **Levels of detail.** Per prototype, levels chosen by projected radius in pixels with a hysteresis fraction of
   about 0.1 to 0.2 (three.js's `LOD` rule), each level its own instance batch per cell. Levels made once when an asset
   is prepared (meshoptimizer's simplifier, after approval; meanwhile hand-made or the asset generator's own low
   level, which the sibling agent measured at about 3,400 triangles for an oak).
4. **Impostors.** A billboard level for people and an octahedral impostor for trees, baked in the browser once per
   prototype into an atlas (a few hundred KB), drawn as instanced quads; in a new file
   `src/js/engine/render/impostors.js`. No cross-fade unless popping is seen.
5. **The rendered view.** In `rendered-scene.js` and `rendered-core.js`, the same world layer as `InstancedMesh`es
   (one per prototype and level), colours by `setColorAt`; while the world moves, one pass a frame instead of the
   accumulation of 16 to 256.
6. **Compressed textures** when textured assets arrive: `KTX2Loader` and the Basis transcoder added to
   `tools/three/build_three.mjs`'s entry and pinned in `runtime/MANIFEST.json`, after the library research and
   approval; ETC1S for vegetation and facades, UASTC for detail that must stay sharp.
7. **Occlusion culling last**, per cell with any-samples queries read a frame or more later, only if a measured scene
   needs it.

Budgets to hold each phase to, until a phone says otherwise: at most 300 draws a frame on a phone (under Arm's 500,
leaving room for the overlay, the map and the rendered view's passes); the main thread's share of drawing under 4 ms on
a desktop; triangles per frame measured on the owner's phone in the first phase and then fixed.

## 13. References

| Source | URL | What was read | Date | Level |
|---|---|---|---|---|
| Khronos, WebGL 2.0 Specification (latest) | https://github.com/KhronosGroup/WebGL/blob/main/specs/latest/2.0/index.html | IDL; `vertexAttribDivisor`, `drawArraysInstanced`, `drawElementsInstanced`; query objects and the rule on query results; range checking | 2026-11-24 | P |
| Khronos, `ANGLE_instanced_arrays` | https://github.com/KhronosGroup/WebGL/blob/main/extensions/ANGLE_instanced_arrays/extension.xml | The extension | 2026-11-24 | P |
| W3C gpuweb, WebGPU specification source | https://github.com/gpuweb/gpuweb/blob/main/spec/index.bs | `GPUVertexStepMode`, `draw`/`drawIndexed`/`drawIndirect`, `occlusionQuerySet`, `indirect-first-instance` | 2026-11-24 | P |
| MDN browser-compat-data | https://github.com/mdn/browser-compat-data (api/WebGL2RenderingContext, ANGLE_instanced_arrays, GPU, WEBGL_multi_draw, WEBGL_compressed_texture_astc, _etc, _s3tc) | Version tables | 2026-11-24 | P (MDN's data) |
| three.js r186 `InstancedMesh.js`, `BatchedMesh.js`, `LOD.js`, `WebGLRenderer.js` | https://github.com/mrdoob/three.js/tree/r186/src | Classes as listed in section 4; renderer lines 1315-1345 | 2026-11-24 | P |
| three.js r186 `KTX2Loader.js`, `SimplifyModifier.js`, `libs/basis/README.md` | https://github.com/mrdoob/three.js/tree/r186/examples/jsm | Imports, `detectSupport`, transcoder files; simplifier wrapper | 2026-11-24 | P |
| three.js r186 examples | https://github.com/mrdoob/three.js/tree/r186/examples (`webgl_instancing_performance`, `webgl_instancing_morph`, `webgl_batch_lod_bvh`) | Approach | 2026-11-24 | P |
| Vendored three.js bundle and its build | `runtime/three/0.186.1/bim-three.min.js`; `tools/three/build_three.mjs` | `grep` counts; entry points | 2026-11-24 | P |
| OGC/Cesium, 3D Tiles specification | https://github.com/CesiumGS/3d-tiles/blob/main/specification/README.adoc | Geometric error, screen-space error, refinement | 2026-11-24 | P |
| CesiumJS `Cesium3DTile.js` | https://github.com/CesiumGS/cesium/blob/main/packages/engine/Source/Scene/Cesium3DTile.js | `getScreenSpaceError`, lines 975-1020 | 2026-11-24 | P |
| Khronos glTF `EXT_mesh_gpu_instancing`, `EXT_meshopt_compression`, `KHR_texture_basisu` | https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0 | Extension READMEs | 2026-11-24 | P |
| meshoptimizer: licence, JS README, npm | https://github.com/zeux/meshoptimizer ; https://www.npmjs.com/package/meshoptimizer ; https://unpkg.com/meshoptimizer@1.3.0/ | MIT; simplifier and decoder APIs; version 1.3.0; file sizes | 2026-11-24 | P |
| Basis Universal: licence, README | https://github.com/BinomialLLC/basis_universal | Apache-2.0; ETC1S and UASTC bit rates; targets | 2026-11-24 | P |
| Arm, GPU Best Practices Developer Guide, revision 3.4, issue 10 (2025) | https://documentation-service.arm.com/static/67a62b17091bfc3e0a947695 | 3.2 draw call batching, 3.3 culling, 3.12 queries, 5.9 instanced vertex buffers, texture compression | 2026-11-24 | P |
| Arm, Optimization advice for graphics content on mobile devices 1.0 (2024) | https://documentation-service.arm.com/static/65952df1159ca73387227425 | Primitive culling, tiny triangles, high draw calls | 2026-11-24 | P |
| Arm developer documentation HTML | https://developer.arm.com/documentation/101897/latest/ | Refused (403) | 2026-11-24 | not read |
| Apple, Metal Best Practices Guide (archive) | https://developer.apple.com/library/archive/documentation/3DDrawing/Conceptual/MTLBestPracticesGuide/ | Contents; Native Screen Scale | 2026-11-24 | P (dated) |
| Apple, OpenGL ES Programming Guide, Techniques for Working with Vertex Data (archive) | https://developer.apple.com/library/archive/documentation/3DDrawing/Conceptual/OpenGLES_ProgrammingGuide/TechniquesforWorkingwithVertexData/TechniquesforWorkingwithVertexData.html | "Simplify Your Models": levels of detail | 2026-11-24 | P (dated) |
| Qualcomm, Adreno best practices | https://docs.qualcomm.com/bundle/publicresource/topics/80-78185-2/best_practices.html | Page did not render to a script | 2026-11-24 | not read |
| Dudash, "Animated Crowd Rendering", GPU Gems 3 ch. 2 (NVIDIA, 2007) | https://developer.nvidia.com/gpugems/GPUGems3/gpugems3_ch02.html | Technique; performance section | 2026-11-24 | S |
| Brucks, "Octahedral Impostors" (2018) | https://shaderbits.com/blog/octahedral-impostors | 404 | 2026-11-24 | not read |
| wojtekpil and Lee, Godot Octahedral Impostors (MIT) | https://github.com/wojtekpil/Godot-Octahedral-Impostors | README, licence | 2026-11-24 | S |
| agargaro, `octahedral-impostor`, `instanced-mesh`, `batched-mesh-extensions` (MIT) | https://github.com/agargaro | READMEs, licences | 2026-11-24 | S |
| Ctrlmonster, `three-octahedral-impostor` (MIT) | https://github.com/Ctrlmonster/three-octahedral-impostor | Licence | 2026-11-24 | S |
| three.js forum: "A forest of octahedral impostors" (2025) | https://discourse.threejs.org/t/a-forest-of-octahedral-impostors/85735 | Posts 1 to 6 | 2026-11-24 | S |
| three.js forum: "Octahedral Impostors for three.js" (2025) | https://discourse.threejs.org/t/octahedral-impostors-for-three-js/80318 | Posts 1 to 2 | 2026-11-24 | S |
| three.js forum: "One Draw Call, Massive Crowd" (2026) | https://discourse.threejs.org/t/one-draw-call-massive-crowd-performance-engineering-in-three-js/89928 | First post | 2026-11-24 | S |
| three.js forum: "Optimization of large amounts (100-1000) of Skinned Meshes" (2023) | https://discourse.threejs.org/t/optimization-of-large-amounts-100-1000-of-skinned-meshes-cpu-bottlenecks/58196 | Posts 1 to 8 | 2026-11-24 | S |
| three.js forum: "InstancedMesh for simple geometries?" (2021) | https://discourse.threejs.org/t/instancedmesh-for-simple-geometries/28658 | Posts 1 to 3 | 2026-11-24 | S |
| three.js forum: "Merge or Use instance and Native render make no difference with Chrome ..." (2020) | https://discourse.threejs.org/t/merge-or-use-instance-and-native-render-make-no-difference-with-chrome-plus-integrated-graphics-card/12257 | Posts 1 to 7 | 2026-11-24 | S |
| three.js forum: "Is it strange? ... webgl_instancing_performance" (2022) | https://discourse.threejs.org/t/is-it-strange-threejs-showcase-webgl-instancing-performance/40903 | Posts 1 to 7 | 2026-11-24 | S |
| Sibling research agent (assets), tree triangle counts | `docs/research/experiments/world-look/as-tree-triangles.out.txt` | Totals per preset and per level | 2026-11-24 | S (unreviewed) |
| This note's experiments | `docs/research/experiments/world-look/re-instancing.html`, `re-instancing-run.cjs`, `re-instancing-probe.cjs`, `re-caps.html`, `re-caps-run.cjs` and their `*-results.json` | Raw results | 2026-11-24 | P (measured here, SwiftShader) |
