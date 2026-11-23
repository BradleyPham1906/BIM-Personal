# Topic note: hands from the phone camera, and physics hands (H4, H5, H6)

Corrections from the independent check (2026-11-23) are in `independent-check.md` and applied in the main note,
`../research-devices-xr.md`; where they differ, those win.

One of the four topic notes of `docs/research/research-devices-xr.md`. Researched 2026-11-23 by a research agent,
following `docs/research/research-protocol.md`. Every fact carries its level: P (primary source read, or measured
here), S (dependable secondary, the gap said), U (search summary, single unchecked copy, or our own reasoning not yet
tested; never used by code). Downloaded packages were kept in the session scratchpad, read as text, never run.

## 1. The questions

1. MediaPipe Tasks Vision's hand landmarker for the web (`@mediapipe/tasks-vision`): licence of the code and of the
   model, file sizes, the GPU and CPU delegates, whether it works in Safari on iOS, frame rates reported on iPhones,
   whether it runs in a Web Worker and whether it needs SharedArrayBuffer or cross-origin isolation, the 21 landmarks,
   their world coordinates, and handedness.
2. The alternatives (TensorFlow.js hand-pose-detection, ONNX Runtime Web with a hand model, others), compared.
3. Depth from one camera: how to place the hand in 3D from monocular landmarks, the accuracy to expect, jitter
   filtering (the One Euro filter), and pinch thresholds with hysteresis as practitioners set them.
4. Rigid-body engines for the browser (Rapier, cannon-es, Jolt, ammo.js, Oimo): licence, size, threads and isolation,
   iOS Safari, determinism, maintenance, latest version. Compared.
5. The physics hand: how VR hands collide instead of passing through; parameters and failure modes.
6. The combined budget on an A15 in Safari, thermal throttling, and what must be measured on the owner's phone.

Hypotheses under test (from the parent note):

| Id | Hypothesis |
|---|---|
| H4 | MediaPipe's hand landmarker (JavaScript, Apache-2.0) runs in Safari on an A15 at 20 frames a second or more. |
| H5 | A rigid-body engine for the browser (Rapier, cannon-es or Jolt) runs in iOS Safari without cross-origin isolation, under a permissive licence, at an acceptable download size. |
| H6 | The camera, hand tracking, physics and two eye views together hold 30 frames a second or more on an iPhone 13 for a modest model. |

## 2. Search log

| # | Where | Query or request | What came back | Kept / set aside |
|---|---|---|---|---|
| 1 | npm registry | `npm view <pkg> version license dist.unpackedSize dist.tarball time.modified` for 13 packages | versions, licences, sizes, dates | kept: table 7.2 and 7.4 |
| 2 | npm registry | `npm pack` of tasks-vision 1.2.3, rapier3d 0.21.0, rapier3d-compat 0.21.0, cannon-es 0.20.0, jolt-physics 1.1.2, ammo.js 0.0.10, oimophysics 1.2.2, hand-pose-detection 2.0.1, onnxruntime-web 1.31.1, tfjs-core/backend-webgl/converter 4.22.0 | tarballs, unpacked as data | kept: sizes measured raw and `gzip -9` |
| 3 | scratchpad script | a 40-line Python reader of WebAssembly section headers (memory section, memory import flags) run with `python3 -I` on each `.wasm` | shared or not, per build | kept: section 4.4 |
| 4 | the package text | `grep` in `vision_bundle.mjs`, `vision_wasm_internal.js`, `vision.d.ts` for SharedArrayBuffer, crossOriginIsolated, OffscreenCanvas, importScripts, delegate, Landmark | strings and the Safari version check | kept: 4.1 |
| 5 | storage.googleapis.com | GET `mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task` | 200, 7,819,105 bytes, last-modified 2023-04-26 | kept: size, SHA-256, zip members |
| 6 | huggingface.co | `litert-community/MediaPipe-HandLandmarker-Full` README (raw) | licence apache-2.0, SHA-256, tensor shapes, Pixel 6 latency | kept |
| 7 | developers.google.com | Hand Landmarker overview and web_js guide (fetch tool digest) | landmarks, world landmarks, options, defaults, Pixel 6 latency | kept as S where only the digest was read |
| 8 | GitHub issues, google-ai-edge/mediapipe | `is:issue safari hand` (25), `is:issue ios tasks-vision GPU` (47), `is:issue hand landmarker iphone` (7) | lists | read #3303, #3887, #4594, #4867, #2506, #6139, #6142 |
| 9 | GitHub, mediapipe-samples-web | shallow clone at 776b187 (2026-11-19) | official worker samples | kept: `src/workers/hand-landmarker.worker.ts`, `vite.config.ts` |
| 10 | arXiv (ar5iv) | 2006.10214, Zhang et al., MediaPipe Hands | architecture, latency on iPhone 11 | kept |
| 11 | blog.tensorflow.org | 2021-11 "3D Hand Pose with MediaPipe and TensorFlow.js" | browser fps table incl. iPhone 11 | kept as counter-evidence |
| 12 | Frontiers in VR | 10.3389/frvir.2023.1169313 (RGB vs HMD hand tracking) | depth from hand length, errors by distance | kept |
| 13 | arXiv | 2308.01088 (Amprimo et al.) | abstract only, no numbers | set aside: no figures in the abstract |
| 14 | gery.casiez.net/1euro, github.com/casiez/OneEuroFilter | page and reference code | algorithm, tuning, licences | kept |
| 15 | GitHub, microsoft/MixedRealityToolkit-Unity | sparse clone, `ArticulatedHandDefinition.cs`, `HandPoseUtils.cs` | pinch enter/exit distances | kept |
| 16 | GitHub, ultraleap/UnityPlugin | sparse clone (2026-07-07), `PinchDetector.cs`, Physical Hands hard and soft contact | pinch hysteresis, physics hand parameters | kept |
| 17 | raw.githubusercontent.com | three.js r180 `OculusHandPointerModel.js` | pinch threshold | kept |
| 18 | web search, then PDFs | Borst and Indugula 2005; Höll et al. 2018; Prachyabrued and Borst 2012 | the last two read in full text (pdftotext) | kept; Borst and Indugula 2005 only through citing papers (S) |
| 19 | GitHub issues | dimforge/rapier.js `safari OR ios`, dimforge/rapier `safari OR ios OR iphone`, jrouwe/JoltPhysics.js `safari OR ios OR iphone`, pmndrs/cannon-es `safari OR ios OR tunneling` | 2, 4, 0, 1 hits | read rapier.js #14, rapier #597 |
| 20 | git | `git clone --depth 1 --filter=blob:none --no-checkout` of each engine repository | date of last commit | kept: maintenance column |
| 21 | raw.githubusercontent.com | JoltPhysics `Body.h`, `MotionQuality.h` | MoveKinematic, LinearCast text | kept |
| 22 | webkit.org | Safari 16.4 and 17.0 feature posts | wasm SIMD 16.4; OffscreenCanvas 2D in 16.4, WebGL in 17.0 | kept |
| 23 | w3c.github.io | Media Capture and Streams, and its extensions | no focal length or intrinsics in the constrainable properties | kept |
| 24 | benchmarks.ul.com | iPhone 13 page; UL stress-test definition (search) | 3DMark stability 74 to 78 % | kept as S |
| 25 | web search | "mediapipe tasks-vision hand landmarker iPhone Safari fps", "...three.js fps measured" | no measured figure for tasks-vision on an iPhone in Safari | recorded as a gap |
| 26 | this repository | `src/js/engine/walk/walk-physics.js`, `runtime/jolt/1.1.1/`, `runtime/MANIFEST.json`, `docs/research/research-walkthrough.md` | the app already ships Jolt 1.1.1 | kept: section 8 |

GitHub's REST API refused this session for repositories not attached (403); issue pages were read through the fetch
tool (its digest, so S for wording) and repositories by `git clone` (P).

## 3. What the app already has (correction to the parent note)

The parent note (part 8) says "No rigid-body engine". That is out of date (P, read 2026-11-23):
`runtime/jolt/1.1.1/bim-jolt.min.js` (4,011,306 bytes, with its MIT `LICENSE`) is pinned in `runtime/MANIFEST.json`
and loaded by `src/js/engine/walk/walk-physics.js`, the adapter for walk mode (V203, the owner's decision D1 "jolt" in
`docs/research/research-walkthrough.md`: Jolt's `wasm-compat` build bundled by esbuild into one classic script,
0.95 MB gzipped). The vendored file contains `MoveKinematic`, `EMotionQuality_LinearCast`, `SixDOFConstraintSettings`
and `SpringSettings` (grep of the file, P), so the physics hand needs no new engine. The walkthrough research tested
Jolt in Chromium only; it is "Not tested in Safari or Firefox" (its H3). Reuse-first therefore points at Jolt, and
the open question moves from "which engine" to "does the vendored Jolt run in iOS Safari at the needed rate".

## 4. Findings

### 4.1 MediaPipe Tasks Vision, hand landmarker

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Latest `@mediapipe/tasks-vision` is 1.2.3 (2026-11-11); a nightly 1.3.0-rc.20261122 exists. The package moved from 0.10.x to 1.x in 2026. | npm `dist-tags`, `time` | P | high |
| Licence of the JavaScript and wasm: Apache-2.0 (`package.json`, the headers in `vision.d.ts`; the repository's `LICENSE` is Apache-2.0). The npm package carries no `LICENSE` file, so the vendored copy must add the repository's. | package read; raw LICENSE | P | high |
| Licence of the model `hand_landmarker.task`: Apache-2.0, stated by the model card (Google's 2021 PDF, as quoted in the LiteRT community card, which also states the bytes are identical to Google's). | HF README raw; SHA-256 match measured here | P for the card text, S for the PDF it cites (not opened) | high |
| Files (1.2.3): `vision_wasm_internal.wasm` 14,665,716 B (4,147,452 B gzipped), its loader `.js` 336,624 B (80,992 gz), `vision_bundle.mjs` 155,990 B (44,886 gz); a twin `vision_wasm_module_internal.*` for module workers. No non-SIMD wasm ships any more. | measured | P | high |
| Model: `hand_landmarker.task` 7,819,105 B (5,817,979 gz), SHA-256 `fbc2a300...07cde1`, a zip of `hand_detector.tflite` (2,339,878 B, input 192x192) and `hand_landmarks_detector.tflite` (5,478,949 B, input 224x224), float16. | measured; HF README tensors | P | high |
| Total download for hand tracking: about 23.0 MB raw, 10.2 MB gzipped (wasm, loader, bundle, model). | sum of the above | P | high |
| Delegates: `baseOptions.delegate` is `"CPU" or "GPU"`. The GPU path uses WebGL2 (strings in the wasm loader; a WebGPU path is also present in the loader). | `vision.d.ts` line 29; grep | P | high (that it exists); medium (which GPU API runs on iOS) |
| No SharedArrayBuffer and no cross-origin isolation needed: the wasm defines its own memory, not shared (flags 1, shared false); neither the bundle nor the loader mentions SharedArrayBuffer or crossOriginIsolated. | measured (wasm header reader) | P | high |
| Requires wasm SIMD, so iOS 16.4 or later: the maintainer on #6139 (2026-11-17) says 1.2.3 "ships only the SIMD WASM build" and advises iOS 16.4+; WebKit added 128-bit SIMD in Safari 16.4. The reporter's error was "invalid opcode 253" (the SIMD prefix 0xFD) on iOS 16. | #6139 (digest); WebKit 16.4 post | S (issue wording through the fetch tool), P (WebKit post) | high |
| Works in iOS Safari, recently tested by the maintainers: #6142 (closed 2026-11-17) retested 1.2.3 on an iPhone 12, Safari 26.5, GPU delegate, results matching the CPU on 99.4 % of pixels (Image Segmenter); #6139 Face Landmarker CPU and GPU on a current iOS device. No open issue found against the hand landmarker on iOS Safari. | issues | S | medium (no hand landmarker test on iOS published) |
| Runs in a Web Worker: the official samples (Apache-2.0) have `src/workers/hand-landmarker.worker.ts`, which takes an `ImageBitmap` per frame, calls `detectForVideo`, closes the bitmap and posts the result; #2506 was closed 2026-06-29 with "This is now supported". | sample code at 776b187; issue | P | high |
| GPU in a worker needs Safari 17 or later: the bundle creates `new OffscreenCanvas(1,1)` for its GL context only when `OffscreenCanvas` exists and, on Safari, the UA version is 17 or more; otherwise it needs a page canvas. WebKit added WebGL in OffscreenCanvas in Safari 17.0. #4594 traced earlier failures to Safari's 2D-only OffscreenCanvas. | bundle code (function testing `Version/(\d+).*Safari` >= 17); WebKit 17.0 post; #4594 | P | high |
| The samples' dev server sends COOP/COEP headers, but the vision wasm does not need them (previous row); they serve the other tasks (text, audio, LLM) in the same site. | `vite.config.ts`; wasm header | P for both facts; U for the reason | medium |
| Web running modes are `IMAGE` and `VIDEO`; "Web tasks run synchronously", so `detectForVideo` blocks the thread it runs on. Options and defaults: `numHands` 1, `minHandDetectionConfidence`, `minHandPresenceConfidence`, `minTrackingConfidence` 0.5 each. | web_js guide (digest); `vision.d.ts` | S for defaults, P for the API | high |
| Landmarks: 21 per hand, `x` and `y` normalised to [0,1] by image width and height, `z` relative depth with the wrist as origin and "roughly the same scale as x". | `vision.d.ts` NormalizedLandmark doc; guide; #4867 | P | high |
| World landmarks: 21 per hand "in meters"; the guide says "origin at the hand's geometric center"; TensorFlow's hand-pose-detection README says the origin is the average of the four finger MCP knuckles. Same model family, two wordings of the origin; both say metric. | `vision.d.ts` Landmark doc ("in meters"); guide (digest); TFJS README | P (units), S (origin) | high for units, medium for the exact origin |
| Depth (z) was learned from synthetic renders only; "Depth z cannot be derived mathematically from 2D annotations alone" (maintainer, #4867). | paper; #4867 | P (paper), S (issue) | high |
| Topology (index order): 0 wrist; thumb 1 to 4; index 5 to 8; middle 9 to 12; ring 13 to 16; little 17 to 20; tips are 4, 8, 12, 16, 20. | `HAND_CONNECTIONS` array in the bundle | P | high |
| Handedness: per hand, a category "Left" or "Right" with a score; it refers to the subject's hands, not the viewer's, and assumes a mirrored (selfie) image. With the back camera, unmirrored, the label is reversed. A 2022 issue (#3047) reports confusion near the image edge. | `vision.d.ts`; guide; #3047 title | P (doc), U (the back-camera reversal, reasoned) | medium |
| Speed, native: the paper gives 5.3 ms per frame for the full landmark model on an iPhone 11 (16.1 ms on a Pixel 3); the current card gives 17.12 ms CPU and 12.27 ms GPU on a Pixel 6 for the full bundle. | paper Table 3; HF card | P | high (for native) |
| Speed, web on iPhones: no published measurement of tasks-vision 1.x on an iPhone in Safari found. The older evidence is against: the 2021 TF blog measured MediaPipe's legacy web solution at 8 fps (lite) and 5 fps (full) on an iPhone 11 with two hands, and TF.js WebGL at 15 and 12 fps; #3303 (2022, iOS 15.4.1, legacy 0.8.9) reported 6 to 7 fps on an iPhone 13 Pro, improved by turning off CPU inference. | TF blog; #3303 | P (blog table), S (issue digest) | the gap: high; the old numbers' relevance to 1.2.3: low |

### 4.2 The alternatives

| | MediaPipe Tasks Vision 1.2.3 | TF.js hand-pose-detection 2.0.1 (tfjs runtime) | ONNX Runtime Web 1.31.1 plus a hand model | Apple Vision hand pose (native) |
|---|---|---|---|---|
| Licence | Apache-2.0; model Apache-2.0 | Apache-2.0; the models are MediaPipe's, converted | MIT runtime; the model's own licence (MediaPipe's if converted, Apache-2.0) | Apple SDK, native only |
| Download | wasm 4.15 MB gz + model 5.82 MB gz | tfjs core 76 KB + webgl 83 KB + converter 69 KB gz (minified, measured) + the model files from Kaggle/TF Hub (not measured, U) | wasm 14.8 MB raw, 3.8 MB gz (measured) + a model | none (in the OS) |
| Maintenance | releases daily (nightly), 1.2.3 on 2026-11-11 | last release 2023-10 (npm `time.modified`); tfjs 4.22.0 2025-01 | active, 2026-11-12 | active |
| iOS Safari | tested by maintainers in 2026 (4.1) | WebGL backend; 12 to 15 fps on iPhone 11 in 2021 | ships only `simd-threaded` builds whose memory is shared (measured); it falls back to one thread without isolation (code read), but whether a shared memory instantiates in a non-isolated iOS page is untested (U) | the native-paths note |
| Hand-specific | yes: detector, tracker, world landmarks, handedness | yes, same outputs (`keypoints3D` metric) | no: we would write the pre- and post-processing (anchors, crop, tracking) ourselves | yes, 21 joints, 2D only |
| Fit with the library rule | good: adapter-only use | possible, but unmaintained | poor: reinvention of MediaPipe's pipeline | out of the browser |

Set aside: handtrack.js (ISC, 0.1.5 of 2022, bounding boxes only, no landmarks; npm metadata P), `@mediapipe/hands`
(the legacy solution, superseded by the Tasks API, the maintainers "ending support" in #3887, P/S).

### 4.3 Depth, filtering and pinch

**Placing the hand in 3D from one camera.** World landmarks give the hand's shape in metres about its own centre but
not its distance. Two ways to get the distance, both from the pinhole model `u = fx * X / Z + cx`:

1. Similar triangles on a rigid length: `Z = fx * L_metric / L_pixels`, with `L` a span that does not bend (wrist to
   index MCP, index MCP to little MCP). Reimer et al. (Frontiers in VR, 2023) did this with the hand length (wrist to
   middle fingertip) and the intercept theorem: with the user's measured hand length the median error was 1.53 cm at
   75 cm and at most 4.47 cm at 2.5 m; with MediaPipe's own internal scale (no user measurement) errors reached
   28.48 cm at 2.5 m, because the model's metric scale did not match real hands. P (paper, fetch digest of the full
   text), high confidence for the method, medium for the numbers (a webcam, not a phone).
2. Fit the world landmarks to the image landmarks: find the translation `t` such that each world landmark plus `t`
   projects onto its image landmark; with known `fx, fy, cx, cy` this is a linear least-squares problem in `t` (two
   equations per landmark, 42 equations, 3 unknowns). Uses all 21 points, so it is less noisy than one span. U (our
   derivation; to be tested in the phone experiment), and it assumes the world landmarks' axes are the camera's
   (to confirm on the phone by comparing with method 1).

Both need the camera's focal length in pixels. Neither the Media Capture and Streams specification nor its
extensions expose focal length or intrinsics (P, both specifications read 2026-11-23; the constrainable properties are
width, height, aspect ratio, frame rate, facing mode, resize mode and audio ones). So the app must calibrate once per
phone and per capture size: hold an object of known width at a known distance (a tape measure is enough), and must
request a fixed resolution with `resizeMode: "none"` so the field of view does not change under it (U: whether iOS
crops for a given request is to be measured). Depth error is proportional to scale error: a hand 10 % larger than
assumed reads 10 % nearer (from the formula, P as arithmetic). A per-user hand-span calibration (the user enters or
measures one span) removes most of it, as Reimer et al. found.

Expect a working range of roughly 25 to 75 cm from the phone (arm's length in a cardboard viewer), where Reimer et al.
measured below 1.75 cm median error with a measured hand. Depth jitter is larger than lateral jitter, because the
span in pixels is small; the filter below must be stronger on Z (U, to measure).

**Jitter: the One Euro filter** (Casiez, Roussel and Vogel, CHI 2012, pp. 2527 to 2530). P, from the authors' own
reference code (BSD, Inria, `python/OneEuroFilter/OneEuroFilter.py`) and page. Per coordinate: estimate the speed
`dx = (x - x_prev_filtered) * freq`, low-pass it with cutoff `dcutoff` (default 1 Hz), set
`cutoff = mincutoff + beta * |dx_filtered|`, then low-pass `x` with `alpha = 1 / (1 + tau / Te)`,
`tau = 1 / (2 * pi * cutoff)`, `Te = 1 / freq` (freq from timestamps when given). Tuning (the authors): beta 0 first,
lower `mincutoff` (start near 1 Hz) until jitter at rest is gone, then raise `beta` by factors of 10 until fast moves
do not lag. The JavaScript and TypeScript reference implementations are BSD; it is twenty lines, so the app writes its
own ES5 version, credited, with a unit test against the authors' `groundTruth.csv` (in the same repository).
Filter positions in metres after depth is solved, not normalised image coordinates, so beta has one meaning across
distances (U, a design choice).

**Pinch thresholds used in practice** (all distances thumb tip to index tip, metres):

| Source (read as text) | Enter | Exit | Notes | Level |
|---|---|---|---|---|
| MRTK2, `ArticulatedHandDefinition.cs` (MIT) | < 0.02 | > 0.05 | both settable within 0.015 to 0.1 | P |
| MRTK2, `HandPoseUtils.CalculateIndexPinch` | strength = clamp(1 - d^2 / 0.0016) | | 0 at 4 cm, 1 at contact | P |
| Ultraleap `PinchDetector.cs` (Apache-2.0) | < 0.025 | > 0.03 | "Utilizes hysteresis to have different pinch and unpinch thresholds" | P |
| three.js r180 `OculusHandPointerModel.js` (MIT) | <= 0.02 | (none) | display scale from 0.01 to 0.05 | P |

These come from depth sensors and headset cameras with millimetre-level fingertips. From one phone camera the
fingertips are the least accurate points (model card: "fingertips show the largest error", S via digest) and depth
error is larger, so a fixed 2 cm threshold will chatter. Recommended start, to be tuned on the phone: compute the
thumb-to-index distance from the world landmarks (shape only, so unaffected by the distance error), divide it by a
palm span (wrist to index MCP) so it is scale-free, enter below the equivalent of 2.5 cm and exit above 4 cm (between
Ultraleap's and MRTK's), and require the state to hold for 2 frames before it changes (U: the ratio and frame count
are ours, to measure).

### 4.4 Rigid-body engines

| | Jolt (JoltPhysics.js) | Rapier (`@dimforge/rapier3d`) | cannon-es | ammo.js | OimoPhysics |
|---|---|---|---|---|---|
| Latest (npm) | 1.1.2, 2026-11-21; the app pins 1.1.1 | 0.21.0, 2026-09-25 | 0.20.0, 2022-08-12 | 0.0.10, 2016-04-17 (npm); GitHub repo active, 2026-09-22 | 1.2.2, 2024-03 |
| Licence | MIT (P) | Apache-2.0 (P) | MIT (P) | zlib (P, LICENSE read): not on the library rule's list | MIT (P) |
| Language | C++ to wasm (or asm.js) | Rust to wasm | JavaScript | C++ (Bullet) to asm.js/wasm | Haxe to JavaScript |
| Size, single-thread | `wasm-compat` 3.24 MB raw, 0.91 MB gz; `wasm` 0.97 MB js + 2.03 MB wasm (0.14 + 0.75 MB gz) | wasm 3.08 MB (1.17 MB gz) + js; `-compat` one file 4.34 MB (1.65 MB gz) | 0.35 MB (75 KB gz) | 1.56 MB (0.32 MB gz) | 1.58 MB (0.23 MB gz) |
| Shared memory / threads | single-thread builds: memory not shared (measured); `multithread` builds import a shared memory (measured), so they need cross-origin isolation | memory not shared (measured) | none (JS) | none in the npm build | none (JS) |
| SIMD | multithread builds have it on; others off; "Safari 16.4 was the last major browser to support this" (README) | separate `-simd` package needs simd128 | n/a | n/a | n/a |
| CCD | `EMotionQuality::LinearCast` (P, header) | `enableCcd`, soft CCD `setSoftCcdPrediction`, `maxCcdSubsteps` (P, d.ts) | none (0 matches for ccd or continuous, P) | Bullet's swept sphere | none listed in its d.ts |
| Kinematic and joints | `MoveKinematic(pos, rot, dt)` "Set velocity of body such that it will be positioned at [target] in [dt]"; Fixed, Point, Distance, SixDOF constraints with springs and motors | KinematicPositionBased and VelocityBased, `setNextKinematicTranslation`; Fixed, Spherical, Spring, Generic joints with `configureMotorPosition(target, stiffness, damping)` | kinematic body type; Lock, PointToPoint, Hinge, ConeTwist constraints | Bullet's | basic |
| Determinism | cross-platform only in a `CROSS_PLATFORM_DETERMINISTIC` build (README) | main build locally deterministic, not cross-platform; a `-deterministic` package for that (README) | not stated | not stated | not stated |
| iOS Safari | no iOS issues in the tracker (0 hits); not yet tested by the app in Safari | iOS 14 crashes (rapier.js #14, 2021, a WebKit segfault, then a minifier fault; rapier #597 closed 2026-08-08 as iOS 14 is end of life) | no iOS issues found | not searched further | not searched |
| Maintenance (last commit) | 2026-11-21 | 2026-10-10 (rapier.js merged into rapier and archived 2026-07-12) | 2024-01-06; 53 open issues | 2026-09-22 | 2025-05-18 |
| In the app | yes, V203 walk mode | no | no | no | no |

All P unless marked; sizes measured here with `stat` and `gzip -9 | wc -c`.

**Conclusion on engines.** Jolt's single-thread build meets the library rule and needs no isolation, and it is
already vendored, pinned and loaded on demand for walk mode. Rapier is the second choice (Apache-2.0, no isolation,
but 1.65 MB gzipped as the app would bundle it, and a second engine to carry). cannon-es is set aside (no CCD, which
fast-moving hands need, and no release since 2022); ammo.js is set aside (zlib licence is outside the rule's list,
and its npm build is from 2016); Oimo is set aside (no CCD, small community).

### 4.5 The physics hand

Three ways to couple a tracked hand to a physics world, from the sources:

1. **Kinematic hand.** The hand's colliders follow the tracking directly (Jolt `MoveKinematic`, Rapier
   KinematicPositionBased). One-way: "a kinematic body can push a dynamic body, but a kinematic body cannot be pushed by
   anything" (Rapier d.ts, P). Höll et al. (IEEE VR 2018, P): a hand "simply modeled as a 'kinematic object'... can
   penetrate the virtual objects, which can lead to very unstable results in physics engines". With infinite mass it
   crushes objects into walls and moves anything regardless of weight.
2. **Velocity-tracked dynamic hand (the soft spring).** Each hand body is dynamic and every physics step its velocity
   is set to reach the tracked pose in one step: `v = (target - current) / dt`, angular velocity from the rotation
   delta. Ultraleap's Physical Hands (Apache-2.0, read as text, P) do exactly this: soft contact bones set
   `linearVelocity = delta / fixedDeltaTime` with a dead zone of 0.5 mm "to avoid tiny vibrations", continuous
   collision detection on, bones of one hand ignoring each other, friction 1. Hard contact uses articulation bodies
   (bone mass 0.1 kg, stiffness 100, damping 1, solver iterations 30 and velocity iterations 20) and scales the
   driving velocity down as the bones are pushed away from the tracked hand. When the physics hand is more than
   0.1 m from the tracked hand ("teleportDistance") or bones are over-rotated, it is reset to the tracked pose and
   "ghosted" (no collisions) until it is clear of objects. Soft contact switches to non-colliding when the error
   exceeds 0.03 m or while grabbing.
3. **Spring-damper coupling (virtual coupling).** Borst and Indugula (IEEE VR 2005) tie a simulated hand to the
   tracked hand with linear and torsional spring-dampers (S: through Prachyabrued and Borst 2012 and Höll et al.,
   which describe it; the 2005 text not read). Höll et al. use a spring force `f = gamma (C - p)` with `gamma = 100`
   toward contact points, in Unity 5 with PhysX 3 (P). A PD drive in Jolt is a SixDOF constraint with spring and motor
   settings between a kinematic target body and the dynamic hand body; in Rapier, a joint motor with stiffness and
   damping.

**What users prefer** (Prachyabrued and Borst, 3DUI 2012, P, 20 subjects): preventing visual interpenetration (show the
physics hand, stopped at the surface) was preferred by most subjects (17, 19, 16 and 16 of 20 across the four object
conditions), although allowing it (show the tracked hand) gave 16 % smaller placement error. So: draw the physics
hand, and show the tracked hand as a faint ghost when they separate.

**Grabbing.** Physics-only grasping by friction (Höll et al.) needs accurate fingertips and contact forces that a
phone camera cannot give. The robust choice for this hardware: grab on pinch. When the pinch enters while the pinch
point is within a small radius of a body (or touching it), attach the body to the hand with a joint (Jolt
FixedConstraint, or a SixDOF with springs so heavy objects lag; Rapier fixed or spring joint); release on pinch exit,
handing the body the hand's filtered velocity so it can be thrown. Ultraleap's hard contact lowers finger stiffness
while grabbing (`grabbedBoneStiffness = 10` against 100), the same idea (P).

**Recommended parameters** (start values; U until measured on the phone): physics step 1/60 s, fixed, with the
hand target interpolated between the 20 to 30 Hz tracking samples; hand = one palm box plus five fingertip spheres
(about 1 cm radius) rather than 16 bones, to keep the solver cheap; hand bodies dynamic, velocity-tracked as in way 2,
mass about 0.1 kg per body (Ultraleap's bone mass), speed capped (for example 3 m/s) so a tracking glitch cannot fling
objects; Jolt `LinearCast` motion quality on hand bodies; teleport and ghost when the error exceeds 0.1 m (Ultraleap);
a dead zone of 0.5 mm; hand bodies do not collide with each other; while a body is grabbed, its collisions with the
holding hand are off.

**Failure modes, and the answer to each:**

| Failure | Cause | Answer | Source |
|---|---|---|---|
| Tunnelling | a hand moving 1 m/s covers 3 to 5 cm between 20 to 30 Hz samples, more than a thin panel | CCD (`LinearCast` / Rapier CCD) on hand bodies, physics substeps between samples, speed cap | Jolt `MotionQuality.h`: "Discrete ... will tunnel through thin objects if its velocity is high enough" (P) |
| Jitter of held or touched objects | landmark noise becomes velocity | One Euro filter before physics; the 0.5 mm dead zone | Casiez; Ultraleap (P) |
| Hand stuck inside an object, or explosions | large target jumps (tracking lost and re-found, depth jump) | teleport and ghost beyond 0.1 m; ghost while tracking confidence is low | Ultraleap (P) |
| Heavy objects moved as if weightless | kinematic hand, or uncapped velocity drive | dynamic hand with a force or speed cap; spring joint on grab so mass shows as lag | Ultraleap force limits (P); reasoning (U) |
| Objects squeezed between hand and wall | infinite-mass kinematic hand against a static body | dynamic hand; Jolt kinematic bodies do not collide with static ones, so a kinematic hand passes through walls | Rapier d.ts one-way note (P); Jolt kinematic-static rule (U, to confirm in Jolt docs) |
| Mirrored or swapped hands | handedness label assumes a selfie image | swap the label for the back camera, or ignore it and track by position | `vision.d.ts` (P), reasoning (U) |
| Lost tracking at the image edge, low light, blur | the model's stated limits | fade the hand out, freeze held objects or drop them on loss | model card (S) |

## 5. The combined budget on an A15 (H6)

- No published measurement of MediaPipe hand tracking together with WebGL rendering and a physics engine on an iPhone
  in Safari was found (search log 25). P for the absence in the searches run; it is not proof none exists.
- Native ceiling: 5.3 ms per frame for the full landmark model on an iPhone 11 (paper). The web adds the wasm and
  WebGL path; the 2021 and 2022 web figures (5 to 15 fps on iPhone 11 and 13 Pro) were from the legacy solution and are
  the only web numbers, so the margin is unknown.
- Physics: the walkthrough research measured Jolt at 0.006 to 0.032 ms a walking frame on a 60,000-triangle model in
  Node (P, `research-walkthrough.md`); a hand of six bodies against a static mesh and a handful of dynamic bodies
  should be of the same order, small next to tracking and drawing (U until measured in Safari on the phone).
- Thermal: UL's public results give the iPhone 13 a 3DMark "stability" of 74 to 78 % (Wild Life 78 %, Wild Life
  Unlimited 74 %, Wild Life Extreme 74 %, Solar Bay 76 %); UL defines stability for its stress tests as the worst
  loop's frame rate over the best loop's (S: definition read for the desktop tests through search results, the
  iPhone page does not define it). Read as: plan on about three quarters of the first minute's GPU performance after
  some minutes. An anecdote of a native iPhone 12 MediaPipe app dropping from 30 to 18 fps after 8 minutes was seen
  only in a search summary (U).
- Budget sketch at 30 fps (33 ms a frame; U, the measurement decides): tracking in a worker at 15 to 30 Hz, off the
  main thread; camera frame copied to an ImageBitmap each tracking tick; stereo drawing of a modest model, two views;
  physics at 60 Hz in small steps. The main thread then carries drawing, physics and filtering, and the tracker runs
  in parallel on another core and on the GPU, competing with the drawing for it.

## 6. Counter-evidence sought

- **Against H4 (iOS Safari works, 20 fps):** searched the MediaPipe tracker for Safari, iOS, iPhone and GPU issues
  (three searches, about 79 hits listed, seven read). Found: legacy-solution slowness on iPhones (#3303, 6 to 7 fps;
  TF blog, 5 to 8 fps); Safari OffscreenCanvas failures before Safari 17 (#4594); SIMD-only builds failing on iOS 16
  before 16.4 (#6139); wrong GPU results on iOS Safari in an older version (#6142, fixed in 1.2.3). None shows 1.2.3
  failing or slow on iOS 17 or later, but none measures the hand landmarker there either. H4 stays open.
- **Against H5:** looked for each engine needing SharedArrayBuffer (measured the wasm memory flags: only Jolt's and
  ONNX Runtime's threaded builds share memory), for licences outside the rule (ammo.js is zlib), and for iOS crash
  reports (Rapier's iOS 14 crashes, closed; none for Jolt; none for cannon-es). Also found that the parent note's "no
  rigid-body engine" is wrong (section 3).
- **Against the depth method:** Reimer et al. show MediaPipe's own metric scale alone gives large far-range error
  (28 cm at 2.5 m), so a calibration step is required, not optional.
- **Against fixed pinch thresholds:** all three practitioner thresholds come from depth-sensing trackers; the model
  card says fingertips are the least accurate points. So thresholds must be re-tuned for the phone.
- **Against kinematic hands:** Höll et al. and Rapier's own documentation of one-way kinematic interaction.

## 7. Outcomes

- **H4: open, leaning plausible.** Confirmed parts: Apache-2.0 for code and model (P); runs without SharedArrayBuffer
  or isolation (P, measured); runs in a worker (P); GPU in a worker from Safari 17 (P); works in current iOS Safari per
  the maintainers' 2026 retests of other vision tasks (S). Not confirmed: 20 fps on an A15 in Safari. The only web
  numbers on iPhones (legacy solution, 2021 to 2022) are below it; the native model takes 5.3 ms on an iPhone 11.
  Decided only by the phone experiment.
- **H5: held.** Jolt (MIT, single-thread `wasm-compat`, memory not shared, already vendored at 0.95 MB gzipped) and
  Rapier (Apache-2.0, memory not shared, 1.17 to 1.65 MB gzipped) both meet the rule without cross-origin isolation;
  cannon-es (MIT) too, but without CCD. Jolt's iOS Safari behaviour is untested by the app (and Rapier had iOS 14 bugs,
  now closed), so the phone experiment must include a Jolt step loop.
- **H6: untested; no published evidence either way.** Thermal data suggest about a quarter of the GPU performance is
  lost in sustained use. Decided only on the owner's phone over at least 10 minutes.

## 8. Recommended stack

1. **Hand tracking:** `@mediapipe/tasks-vision` 1.2.3 (Apache-2.0), `HandLandmarker` with the float16
   `hand_landmarker.task` (SHA-256 `fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1`), both vendored
   under `runtime/` with the repository's LICENSE and the model card, pinned in `MANIFEST.json`, loaded only when hand
   mode starts (about 10.2 MB gzipped). `runningMode: "VIDEO"`, `numHands` 2 (1 if the budget is short),
   `delegate: "GPU"` with a CPU fallback on error, run in a module Web Worker (the official sample's pattern:
   `createImageBitmap(video)` on the main thread, transfer, `detectForVideo`, close the bitmap, post landmarks back).
   Requires iOS 17 or later for GPU in the worker; the app checks and says so (toast) on older systems.
2. **Filtering and 3D:** our own ES5 One Euro filter (method credited to Casiez et al.; unit-tested against the
   authors' ground-truth data); depth by fitting world landmarks to image landmarks with a calibrated focal length,
   checked against the span method; a one-time calibration of focal length and of the user's hand span.
3. **Pinch:** world-landmark thumb-to-index distance normalised by palm span, with hysteresis (enter at about 2.5 cm
   equivalent, exit at about 4 cm) and a two-frame hold; values tuned on the phone.
4. **Physics:** Jolt, the app's existing `runtime/jolt/1.1.1` (or 1.1.2 if the phase updates it), single-thread
   `wasm-compat` build, behind a new narrow adapter beside `walk-physics.js`. Hand = palm box and five fingertip
   spheres, dynamic, velocity-tracked toward the filtered target (Ultraleap's soft-contact method), `LinearCast`,
   speed cap, teleport and ghost beyond 0.1 m; grab on pinch with a constraint, release with the hand's velocity.
   Model elements that can be moved become dynamic bodies with mass from their material and volume; the rest of the
   model is one static mesh body, as walk mode does.
5. **Not recommended:** TF.js hand-pose-detection (unmaintained since 2023), ONNX Runtime Web (no hand pipeline;
   threaded-only builds), cannon-es (no CCD), ammo.js (zlib, old npm build), Jolt's multithread builds (need
   isolation, which GitHub Pages cannot send as headers).

What would change it: a measurement below 15 fps for the tracker in Safari on the A15 (then the native path in
`native-paths.md`, Apple Vision, becomes the hand source); Jolt failing in iOS Safari (then Rapier's non-compat build).

## 9. What must be measured on the owner's iPhone 13

A test page in `docs/research/experiments/` (to be written; not part of this note), each run logged with iOS and
Safari versions, as a browser tab and as the installed web app:

1. Tracker rate and latency: `detectForVideo` time per frame, GPU and CPU delegates, main thread and worker, one and
   two hands, camera at 640x480 and 1280x720; frames per second delivered over 60 s.
2. The same with the stereo view drawing a modest model (three.js, the app's rendered view) at the same time.
3. Jolt in Safari: start time of the vendored script, ms per step for a static mesh of the size of a typical model
   plus 20 dynamic boxes plus six hand bodies.
4. Everything together for 10 minutes and 20 minutes: frame rate per minute (to see throttling), and whether iOS
   reports thermal state through any page-visible signal (U: none is known; time per frame is the proxy).
5. Depth accuracy: the hand at 30, 50 and 70 cm on a tape, both depth methods, with and without hand-span
   calibration; the focal length from the calibration; whether the field of view changes with the requested size.
6. Jitter at rest (standard deviation of the filtered palm position over 5 s) and lag on a fast move, for a few
   One Euro settings.
7. Pinch: false pinches and missed pinches over 50 trials at each distance, for two threshold pairs.
8. Memory: does the page survive the tracker plus the model plus the camera without the tab reloading (iOS kills tabs
   under memory pressure; U, to observe).

## 10. Still open

- The tracker's frame rate in iOS Safari on an A15 (H4) and the combined rate (H6): only the phone can answer.
- Whether the world landmarks' axes are aligned with the camera (needed by the fitting method): to test.
- The exact origin of the world landmarks (geometric centre in Google's guide, mean of the four MCPs in TensorFlow's
  README): matters little for the fit (a constant offset) but to settle by measurement.
- Whether Jolt kinematic bodies collide with static bodies (to read in Jolt's documentation; the recommendation does
  not depend on it, as the hand is dynamic).
- Whether ONNX Runtime Web's shared-memory build instantiates in a non-isolated iOS page (only matters if ONNX is
  reconsidered).
- The UL stability definition for the mobile Wild Life tests (read only for the desktop tests).
- Borst and Indugula 2005 in full text (read only as described by two citing papers).
- The size the app's repository grows by: about 23 MB of committed runtime for hand tracking (the owner's decision).

## 11. Decisions for the owner (proposed, to be asked with the parent note)

1. Hand tracking library: MediaPipe Tasks Vision 1.2.3 and its hand model (Apache-2.0, about 10 MB gzipped, 23 MB
   committed under `runtime/`), subject to the phone measurement.
2. Physics: reuse the vendored Jolt for hands and movable elements (no new engine).
3. iOS 17 as the minimum for hand mode (GPU in a worker), with a clear message on older systems.
4. Grab model: pinch-to-grab with physics pushing, not friction-only grasping.

## 12. References (all read 2026-11-23)

| Source | URL | What was read | Level |
|---|---|---|---|
| npm registry metadata and tarballs | https://registry.npmjs.org/ (packages in the search log) | versions, licences, dates; files unpacked and measured | P |
| @mediapipe/tasks-vision 1.2.3 | https://www.npmjs.com/package/@mediapipe/tasks-vision | `package.json`, `README.md`, `vision.d.ts` (Landmark, NormalizedLandmark, HandLandmarker options and result), `vision_bundle.mjs` (OffscreenCanvas and Safari check, HAND_CONNECTIONS), wasm headers | P |
| MediaPipe repository licence | https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/LICENSE | Apache-2.0 text | P |
| Hand landmarker model | https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task | downloaded, size, SHA-256, zip members | P |
| Model card (LiteRT community) | https://huggingface.co/litert-community/MediaPipe-HandLandmarker-Full | README raw: licence, files, tensors, latency | P (the Google PDF it cites: S) |
| Hand Landmarker guide | https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker | overview: model, landmarks, world landmarks, handedness, latency | S (fetch digest) |
| Hand Landmarker web guide | https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/web_js | options, defaults, running modes, result | S (fetch digest) |
| MediaPipe web samples | https://github.com/google-ai-edge/mediapipe-samples-web (776b187, 2026-11-19) | `src/workers/hand-landmarker.worker.ts`, `src/workers/base-worker.ts`, `vite.config.ts`, LICENSE | P |
| MediaPipe issue #3303 | https://github.com/google-ai-edge/mediapipe/issues/3303 | thread | S |
| MediaPipe issue #3887 | https://github.com/google-ai-edge/mediapipe/issues/3887 | thread | S |
| MediaPipe issue #4594 | https://github.com/google-ai-edge/mediapipe/issues/4594 | thread | S |
| MediaPipe issue #4867 | https://github.com/google-ai-edge/mediapipe/issues/4867 | thread | S |
| MediaPipe issue #2506 | https://github.com/google-ai-edge/mediapipe/issues/2506 | thread | S |
| MediaPipe issue #6139 | https://github.com/google-ai-edge/mediapipe/issues/6139 | thread | S |
| MediaPipe issue #6142 | https://github.com/google-ai-edge/mediapipe/issues/6142 | thread | S |
| MediaPipe issue searches | https://github.com/google-ai-edge/mediapipe/issues?q=is%3Aissue+safari+hand (and the two others in the log) | result lists | S |
| Zhang et al. 2020, MediaPipe Hands | https://ar5iv.labs.arxiv.org/html/2006.10214 | architecture, Tables 2 and 3 | P |
| TensorFlow blog, 3D Hand Pose, 2021-11 | https://blog.tensorflow.org/2021/11/3D-handpose.html | browser fps table, keypoints3D definition | P |
| TF.js hand-pose-detection 2.0.1 | https://www.npmjs.com/package/@tensorflow-models/hand-pose-detection | README (runtimes, keypoints3D), peer dependencies | P |
| ONNX Runtime Web 1.31.1 | https://www.npmjs.com/package/onnxruntime-web | dist file list, wasm header, thread fallback code | P |
| Reimer et al. 2023, Frontiers in VR | https://www.frontiersin.org/journals/virtual-reality/articles/10.3389/frvir.2023.1169313/full | method (hand length, intercept theorem), errors by distance, limits | P via fetch digest of the full text (first 100,000 characters) |
| Amprimo et al. 2023 | https://arxiv.org/abs/2308.01088 | abstract (no numbers) | P, not used |
| One Euro filter page | https://gery.casiez.net/1euro/ | citation, tuning, implementation licences | S (fetch digest) |
| One Euro reference code | https://github.com/casiez/OneEuroFilter | `python/OneEuroFilter/OneEuroFilter.py`, `python/LICENSE` (BSD, Inria), `javascript/` | P |
| MRTK2 | https://github.com/microsoft/MixedRealityToolkit-Unity | `Assets/MRTK/Core/Definitions/Devices/ArticulatedHandDefinition.cs`, `Assets/MRTK/Core/Providers/Hands/HandPoseUtils.cs`, LICENSE.md (MIT) | P |
| Ultraleap Unity Plugin | https://github.com/ultraleap/UnityPlugin (2026-07-07) | `PinchDetector.cs`; Physical Hands `HardContactParent.cs`, `HardContactBone.cs`, `HardContactHand.cs`, `SoftContactBone.cs`, `SoftContactHand.cs`; LICENSE.md (Apache-2.0) | P |
| three.js r180 | https://raw.githubusercontent.com/mrdoob/three.js/r180/examples/jsm/webxr/OculusHandPointerModel.js | pinch constants and test | P |
| Höll, Oberweger, Arth, Lepetit 2018 | https://www.tugraz.at/fileadmin/user_upload/Institute/ICG/Images/team_lepetit/publications/hoell_vr18.pdf | full text: kinematic-hand problem, spring force, gamma 100, Unity 5 and PhysX 3 | P |
| Prachyabrued and Borst 2012 | https://vrlab.cmix.louisiana.edu/wp-content/uploads/2025/04/Prachyabrued_Borst_3DUI2012_Interpenetration.pdf | full text: spring model, conditions, preferences, error | P |
| Borst and Indugula 2005, Realistic virtual grasping, IEEE VR, doi 10.1109/VR.2005.1492758 | https://dblp.org/rec/html/conf/vr/BorstI05 | described by the two papers above | S |
| Rapier 0.21.0 | https://github.com/dimforge/rapier | npm README (builds, determinism), d.ts (rigid_body, world, impulse_joint), LICENSE | P |
| rapier.js issue #14 | https://github.com/dimforge/rapier.js/issues/14 | thread | S |
| rapier issue #597 | https://github.com/dimforge/rapier/issues/597 | thread | S |
| JoltPhysics.js 1.1.2 | https://github.com/jrouwe/JoltPhysics.js | npm README (flavours, SIMD), LICENSE, `dist/types.d.ts`, wasm headers | P |
| Jolt Physics headers | https://raw.githubusercontent.com/jrouwe/JoltPhysics/master/Jolt/Physics/Body/Body.h, .../MotionQuality.h | MoveKinematic, EMotionQuality comments | P |
| cannon-es 0.20.0 | https://github.com/pmndrs/cannon-es | LICENSE, readme, dist (constraints, kinematic, no CCD); issue search | P |
| ammo.js 0.0.10 | https://github.com/kripken/ammo.js | LICENSE (zlib), npm dates, last commit | P |
| OimoPhysics 1.2.2 | https://github.com/saharan/OimoPhysics | package.json licence, d.ts, last commit | P |
| WebKit, Safari 16.4 | https://webkit.org/blog/13966/webkit-features-in-safari-16-4/ | wasm SIMD, OffscreenCanvas 2D | P (fetch digest quoting the text) |
| WebKit, Safari 17.0 | https://webkit.org/blog/14445/webkit-features-in-safari-17-0/ | WebGL in OffscreenCanvas, workers | P (fetch digest quoting the text) |
| Media Capture and Streams | https://w3c.github.io/mediacapture-main/ | constrainable properties (no intrinsics) | P |
| Media Capture extensions | https://w3c.github.io/mediacapture-extensions/ | no focal length or intrinsics | P |
| UL Benchmarks, iPhone 13 | https://benchmarks.ul.com/hardware/phone/Apple+iPhone+13+review | scores and stability | S (public median results; definition not on the page) |
| UL stress test result screen | https://support.benchmarks.ul.com/support/solutions/articles/44002134931-stress-test-result-screen | stability formula, via search summary | U |
| This repository | `runtime/jolt/1.1.1/`, `runtime/MANIFEST.json`, `src/js/engine/walk/walk-physics.js`, `docs/research/research-walkthrough.md` | the vendored engine and its decision | P |
