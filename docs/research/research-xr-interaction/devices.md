# Topic note: the device ladder and one input layer (H1 to H4)

Corrections from the independent check (2026-11-23) are in `independent-check.md` and applied in the main note,
`../research-xr-interaction.md`; where they differ, those win.

Part of `docs/research/research-xr-interaction.md`, researched 2026-11-23 by one of three parallel researchers, under
`docs/research/research-protocol.md`. The iPhone cardboard path (`research-devices-xr.md`, V274) is not redone here;
its measured results are used as they stand. Levels: P primary (read in the source, the code read as text, the
specification's own text, the vendor's own document); S secondary (a dependable work citing it, a press report, a
vendor page that is out of date); U unverified (a search summary, a single unofficial copy, our own inference not
checked). Nothing was run on a headset here; no third-party code was run. Downloads were kept in the session's
scratchpad, read as text.

## 1. The questions

1. **Meta Quest (3 and 3S, Quest Browser).** Does the same web page get an immersive VR session and a passthrough
   (immersive-ar) session, hand joints (how many, named how), hit test, anchors, planes, meshes, depth, layers? At what
   frame rates? How does a person open a web app there (a URL, an installed web app, the store)? Does the Horizon
   Store take web apps? What does Meta say about performance?
2. **Apple Vision Pro (visionOS 2, 26, 27, Safari).** Is immersive-vr on by default or behind a flag? Immersive-ar?
   What is the input (gaze and pinch as a transient pointer)? Are hand joints given to the page, and how? What
   alternatives does Apple offer (the `<model>` element, USDZ Quick Look)?
3. **Android.** Chrome on a phone: immersive-ar (ARCore) and immersive-vr (Cardboard). Android XR headsets (Samsung
   Galaxy XR): Chrome's WebXR and its hand input.
4. **Desktop.** What a computer gives: mouse, touch, a webcam with MediaPipe hands, and a PC headset through Chrome.
5. **three.js 0.186.1, the app's pinned copy.** What of WebXR is in the core, what is in `examples/jsm` and so not in
   the app's bundle, and what the app must add.
6. **One input layer (H4).** A minimal event model every device maps onto, with prior art.
7. **A device ladder:** device, cost, how the app reaches it, tracking, hands, passthrough, what the app must add,
   effort.

## 2. Search log

| # | Where | Query or address | What came back | Kept / set aside |
|---|---|---|---|---|
| 1 | Web search | Meta Quest Browser WebXR hand tracking immersive-ar passthrough developer documentation | Meta pages webxr-hands, webxr-mixed-reality, webxr-overview; a Meta help page on permissions; Wikipedia | Meta pages kept and read (refs M1 to M3); summary not used |
| 2 | Web search | webkit.org visionOS Safari WebXR transient-pointer gaze pinch natural input | WebKit blog 15162; UploadVR, Road to VR, 9to5Mac | WebKit post read (A1); press set aside as secondary |
| 3 | Web search | Android XR Chrome WebXR hand tracking Galaxy XR | developer.android.com/develop/xr/web; Samsung support | Android page read (G1) |
| 4 | developers.meta.com | webxr-hands, webxr-mixed-reality, webxr-overview, webxr-perf, webxr-perf-bp, webxr-frames, pwa-overview, pwa-submit-app, release-notes/web, iwsdk-concept-xr-input-pointers, unity-isdk-interaction-sdk-overview, unity-isdk-architectural-overview, unity-isdk-interactor | each read through the fetch tool's reader | kept (M1 to M12) |
| 5 | Web search | Meta Horizon OS PWA store submit Bubblewrap | Meta pwa pages; a 2024 forum post saying submission was not possible | Meta's 2026 pages kept; the forum post recorded as superseded |
| 6 | Web search | visionOS 26 Safari WebXR enabled by default immersive-vr | Apple release-note links, WebKit Safari 26.0 post, MacStories | led to fetching WebKit's Safari 18.0 and 26.0 posts directly |
| 7 | curl, webkit.org | blog 15865 (Safari 18.0), blog 17333 (Safari 26.0) | full HTML, text extracted by our script | kept (A2, A3) |
| 8 | curl, raw.githubusercontent.com | mdn/browser-compat-data main: api/XRSystem, XRSession, XRFrame, XRHand, XRInputSource, XRJointPose, XRHitTestSource, XRAnchor, XRPlane, XRProjectionLayer, XRWebGLBinding, XRDepthInformation (XRMesh: 404) | JSON, summarised by our script | kept (B1); its Safari column disagrees with WebKit, see part 6 |
| 9 | curl, raw.githubusercontent.com | immersive-web/webxr index.bs, webxr-hand-input index.bs, webxr-ar-module index.bs (layers index.bs: 404 on main and master) | Bikeshed sources | kept (W1 to W3); Layers read only through BCD and three.js |
| 10 | npm | `npm pack three@0.186.1` (sha256 8cd06870...033fe7) | src/renderers/webxr/*, examples/jsm/webxr/* | kept (T1) |
| 11 | repository | runtime/three/0.186.1/bim-three.min.js; tools/three/build_three.mjs; src/js/engine/render/*.js | grep counts, the build's entry list | kept (R1 to R3) |
| 12 | curl, raw.githubusercontent.com | webxr-input-profiles LICENSE.md, registry generic-hand-select.json; pmndrs/xr LICENSE and pointer-events README; aframe LICENSE and hand-tracking-controls.js | text | kept (I1, X1, X3) |
| 13 | npm | `npm pack @pmndrs/pointer-events@6.6.32`, `@pmndrs/xr@6.6.32`, `@webxr-input-profiles/assets@1.0.20`, `iwer@2.8.0` | dist JS read as text | kept (X1, X2, I2, E1) |
| 14 | chromium.googlesource.com | device/vr/public/cpp/features.cc, device/vr/buildflags/buildflags.gni, chrome/browser/about_flags.cc (main, ?format=TEXT) | C++ and GN text | kept (C1) |
| 15 | Web search | Chrome Android WebXR Cardboard immersive-vr flag chromestatus | immersiveweb.dev support table, Chromium source links | led to reading Chromium's source (C1) |
| 16 | developers.google.com | MediaPipe hand landmarker guide (ai.google.dev redirects there) | landmark counts and coordinates | kept (P1) |
| 17 | Web search, developer.apple.com/forums | WebKit visionOS immersive-ar not supported; threads 743655 and 826845 | an Apple "Vision Pro Engineer" reply, June 2026 | kept (A4, A5) |
| 18 | learn.microsoft.com | MRTK3 interactor architecture (the input/interactors URL answered 404; the architecture page was read) | full page | kept (K1) |
| 19 | Web search, uploadvr.com | Quest Browser depth API hit testing | UploadVR, 10 October 2025, Browser 40.4 | kept as S (U1) |
| 20 | Web search | Quest 3S and Quest 3 prices; Galaxy XR price and WebXR | press and deal pages, no Meta store page | prices kept as S/U only |
| 21 | Web search | three.js transient-pointer visionOS controller index | WebKit's note, three.js forum, Babylon forum | counter-evidence for H3 (part 6) |
| 22 | developers.meta.com | blog: Web Launch for WebXR (2022); Building for MR on Quest 3 (2023) | dated posts | kept as S (M13, M14) |

Refused or missing: the Meta help page on immersive web permissions (meta.com/help/quest/1406582186767703) came back
as its title only; the Layers specification's source path answered 404; GitHub's REST API answered without data from
this container (rate limit or proxy), so repository licences were read from the files themselves.

## 3. Findings

### 3.1 Meta Quest (Quest Browser on Horizon OS)

**F1. Hand input: 25 joints a hand, by name, in WebXR.** Meta: "The API exposes the poses of the 25 skeleton joints"
of each hand, and points to the W3C module for names (M1, P). The module's `XRHandJoint` enum lists exactly 25:
`wrist`; `thumb-metacarpal`, `thumb-phalanx-proximal`, `thumb-phalanx-distal`, `thumb-tip`; and for each of index,
middle, ring and pinky: `-metacarpal`, `-phalanx-proximal`, `-phalanx-intermediate`, `-phalanx-distal`, `-tip` (W2,
P). Each joint has a radius in metres; tip joints should have a nonzero radius so fingertip collisions work (W2, P).
BCD records `XRHand`, `getJointPose`, `fillPoses` and `fillJointRadii` in Quest Browser ("oculus") from 15.1 (B1, P).
The session must request the `hand-tracking` feature; without it `inputSource.hand` is null (W2, P). Confidence
**high** (vendor, specification and compatibility data agree).

**F2. Pinch is a select; the palm pinch is the system's.** Physical hand sources must carry the input profile
`generic-hand-select` (W2, P), whose layout makes a single trigger the select component (I1, P). Meta: the regular
pinch "is implemented in the emulated Gamepad attribute for the hand as a button press", and the palm pinch on either
hand is reserved for the system (the left one is the menu button) (M1, P). So on a Quest the page receives
`selectstart`/`select`/`selectend` from a pinch without measuring fingers. Confidence **high**.

**F3. Passthrough: immersive-ar.** Meta's mixed-reality page: request `"immersive-ar"` and draw on a transparent
background or passthrough is hidden (M2, P). That page still names only Quest 2 (grey) and Quest Pro (colour); Quest 3's
full-colour passthrough is from Meta's 2023 blog (M14, S, the vendor's own post but not the WebXR page). Confidence
**high** that immersive-ar runs on Quest 3/3S, **medium** on the exact Quest 3 wording (the WebXR page is out of date).

**F4. Scene features.** Plane detection (`plane-detection`, planes as horizontal or vertical rectangles, wait 2 to 3 s
after the session starts), anchors including persistent anchors (at most 8 persistent per site, none in private mode),
and `initiateRoomCapture` to start space setup (M2, P). BCD lists in Quest Browser: hit test, anchors (persistent
from 31.2), `detectedPlanes` (31.2), `detectedMeshes` (31.2), depth information, `supportedFrameRates` and
`updateTargetFrameRate` (31.2), projection layers (16.1), and `trackedSources` (34.1) (B1, P). Since Browser 40.4 hit
testing uses Meta's Depth API, so no room scan is needed; depth reaches about 5 m on Quest 3/3S (U1, S, UploadVR,
October 2025; Meta's own WebXR page for this was not found). Confidence **high** for planes and anchors, **medium** for
meshes and depth (BCD only, plus a press report).

**F5. Frame rates and budget.** The WebXR session runs "by default at 90 frames per second on Meta Quest 2" and "72
frames per second on Meta Quest headsets"; the page reads `session.supportedFrameRates` and calls
`updateTargetFrameRate`; if frames take "longer than 11ms for a 90Hz framerate", lower the rate (M5, P). Meta's best
practices: one directional or point light, shadows are expensive, update animations at 30 a second while drawing at
90 (M6, P). No triangle or draw-call budget is published for the web (M4, M6, P: their absence). So the budget is
13.9 ms a frame at 72 Hz for both eyes. Confidence **high** for the numbers given; the BIM model's own cost on a Quest
is **unknown** until measured.

**F6. How a person opens the app.** (a) Type or follow the URL in Quest Browser (M3, P). (b) Web Launch: from a phone or
computer, "the current URL is sent to the headset and opened in the Meta Quest Browser" (M13, S: 2022 blog, current
availability not rechecked). (c) The store: a web app can be packaged with Meta's Bubblewrap fork
(`bubblewrap init --manifest=... --metaquest`) into an Android project that opens the site in a Trusted Web Activity,
in "2D" (windowed) or "immersive" mode; store distribution is "optional" and the site stays available without a
package (M7, P, updated 2026-07-22). The Feb 2025 packaging page said the store took immersive web apps only (S, via
search summary); the 2026 page offers both modes. Whether Quest Browser shows an install button for a plain PWA is
**not confirmed** (U: a forum report says no). Confidence **high** for (a) and (c), **medium** for (b).

**F7. Recent Browser releases.** 146.0 (21 Apr 2026): experimental WebGPU and WebXR depth projection, a bounded-floor fix;
154.0 (14 Oct 2026): experimental HTML-in-Canvas hit testing in WebXR; 156.0 (13 Nov 2026): WebGPU in WebXR (M8, P).
Meta now steers new work to its Immersive Web SDK (IWSDK, MIT) and says: feature-detect at run time, never by user
agent (M3, P). Confidence **high**.

### 3.2 Apple Vision Pro (Safari on visionOS)

**F8. immersive-vr is on by default since visionOS 2.** WebKit: "Safari 18.0 for visionOS 2 adds support for
immersive-vr sessions with WebXR", with transient-pointer and WebXR hand tracking, "permission to allow hand tracking
will be requested from users at the start of their WebXR session" (A2, P). Before that, visionOS 1.1 had it behind
the "WebXR Device API" feature flag, "for testing purposes only" (A1, P). Nothing read says visionOS 26 or 27 removed
it (A3 lists no WebXR change, P), so it is taken as still on; **medium** for 26 and 27 (no test, no explicit statement).

**F9. Input: gaze and pinch as a transient pointer.** The input array is empty until the user pinches; then an input
with `targetRayMode` `transient-pointer` is added (`inputsourceschange`, then `selectstart`); its `targetRaySpace`
starts between the eyes along the gaze and then moves with the hand; its `gripSpace` is the pinching fingers (A1, P).
The specification: a transient pointer comes from an operating-system intent "such as gaze", its target ray is "the
ray to the interaction target at the start of the interaction", static within the grip space (W1, P). The page never
gets continuous gaze, so there is no hover before the pinch (A1, P; Road to VR says the same, S). Confidence **high**.

**F10. Hand joints: yes, with a permission, for pose only.** With `hand-tracking` requested and granted, the first two
inputs are tracked-pointer hands with joints; "The hand inputs are supplied for pose information only and do not
trigger any events"; the transient pointers then sit at indices 2 and 3 (A1, P). So H2's "full hand joints are not
given by default" is right only in the sense that a permission prompt is needed; the joints are given. Confidence
**high** (Apple's own engineers' post, repeated for visionOS 2 in A2).

**F11. No immersive-ar.** An Apple "Vision Pro Engineer" (June 2026): "The WebXR immersive-ar mode isn't currently
supported in visionOS", pointing to immersive video, Quick Look models and immersive website environments (A5, P for
Apple's statement on its forum). Developers measured `isSessionSupported('immersive-ar')` false with the flag on (A4,
S). A user reports the AR flag removed in visionOS 27 (A5, U). Confidence **high**.

**F12. The alternative: `<model>`.** Safari on visionOS 26 supports `<model src="x.usdz">` with a fallback image,
environment maps, animation, a scriptable `entityTransform`, and the user can "drag the models off the page" to see
them at real size (A3, P). USDZ only; the app exports glTF, so this path needs a USDZ export (not in the app). It is a
viewer, not an editor. Confidence **high**.

### 3.3 Android

**F13. Phone: immersive-ar through ARCore; Cardboard compiled in.** Chromium builds both runtimes for Android by
default (`enable_cardboard` and `enable_arcore` = `_is_xr_supported_android`), and its flags page only offers to force
a runtime (ARCore, Cardboard, OpenXR, orientation sensors), not to enable Cardboard (C1, P). BCD gives Chrome
(Android mirrors desktop) WebXR from 79, hit test from 81, anchors 85, depth 90, light estimation 90 (B1, P). In a
handheld AR session, taps arrive as `select` from inputs with `targetRayMode` `screen` (W3, P). Hand tracking in
Chrome is tied to OpenXR (`IsHandTrackingEnabled()` returns `IsOpenXrEnabled()`), so a phone gets no WebXR hands (C1,
P). Whether `immersive-vr` on a phone actually shows the Cardboard viewer today was not tested (**medium**: source
read, no device).

**F14. Android XR headsets (Galaxy XR).** Chrome on Android XR supports the Device API, AR module, gamepads, hit test,
Hand Input, anchors, depth sensing and light estimation; "Hand input is the primary interaction mechanism in Android
XR. Chrome for Android XR supports the Hand Input API as the default input"; depth is stereo (two maps); every WebXR
API needs the "3d mapping and camera tracking" permission and hand data has its own (G1, P). The registry carries a
`samsung-galaxyxr` controller profile (I2, P). Galaxy XR's launch price was 1,799 US dollars, controllers 250 (S, press).
Confidence **high** for the feature list, **medium** for how its pinch maps to select (not read; the Hand Input
module requires `generic-hand-select`, so select on pinch is expected, W2).

### 3.4 Desktop

**F15. A computer gives mouse, touch (on touch screens) and, with a webcam, MediaPipe hands.** MediaPipe's hand
landmarker gives "21 3D keypoints per hand", image coordinates normalised 0 to 1, world landmarks "in real-world
meters, with the origin at the hand's geometric center", handedness "of the subject's hands, not the viewer", one hand
by default (P1, P). The owner's iPhone 13 ran it at 35 to 39 hand frames a second (E3, research-devices-xr.md). The
owner's MacBook Air has a camera; the Windows mini PC has none (research-xr-interaction.md part 11). **F16.** Chrome on
Windows enables OpenXR by default (`kOpenXR` FEATURE_ENABLED_BY_DEFAULT on Windows), so a PC headset (a Quest over Link)
reaches the same page with hands (C1, P); whether the owner's mini PC can drive Link was not checked (U).

### 3.5 three.js 0.186.1 and the app's bundle

**F17. The core has WebXR sessions, controllers, hands and pinch.** Read in `src/renderers/webxr/` of the npm tarball
(T1, P): `WebXRManager` has `getController`, `getControllerGrip`, `getHand`, `setSession`, `setReferenceSpaceType`,
`setFramebufferScaleFactor`, `setFoveation`, `getEnvironmentBlendMode`, depth sensing (`getDepthTexture`), and uses a
WebXR Layers projection layer when `XRWebGLBinding.prototype.createProjectionLayer` exists, else `XRWebGLLayer`.
`WebXRController.update` reads every joint with `frame.getJointPose` each frame (`joint.jointRadius` kept) and fires
its own `pinchstart`/`pinchend` from the thumb-tip to index-tip distance: enter at 0.015 m, leave at 0.025 m
(`distanceToPinch = 0.02`, `threshold = 0.005`). Session events `select`, `selectstart`, `selectend`, `squeeze*` are
forwarded to the controller holding that input source. The app's bundle contains these: `getHand` 10 times,
`pinchstart`, `thumb-tip`, `index-finger-tip`, `XRWebGLBinding`, `createProjectionLayer`, `inputsourceschange`,
`squeezestart`, `getJointPose`, `jointRadius`, `setFoveation` (R1, P, grep counts). Confidence **high**.

**F18. The hand and controller models are not in the bundle.** `XRHandModelFactory`, `OculusHandModel`,
`XRControllerModelFactory`, `VRButton`, `XRButton`, `ARButton`: zero matches in `bim-three.min.js` (R1, P); the build
bundles only `three`, GLTFLoader, GLTFExporter, DRACOLoader and the meshopt decoder (R2, P). Two of those helpers fetch
from a CDN by default: `XRHandMeshModel` loads `https://cdn.jsdelivr.net/npm/@webxr-input-profiles/assets@1.0/dist/profiles/generic-hand/`
and `XRControllerModelFactory` the profiles from the same CDN, through the bundled `motion-controllers` 1.0.0 (T1, P).
The library rule forbids run-time CDN fetches, so the app would either draw primitive hands (`XRHandPrimitiveModel`,
no fetch) or vendor the generic-hand `left.glb` and `right.glb` (94,572 and 94,004 bytes, MIT, Amazon 2019, in
`@webxr-input-profiles/assets` 1.0.20) under `runtime/` and set the path (I2, P). Confidence **high**.

**F19. Things the app's code does not do yet.** No file in `src/` uses `renderer.xr` or `navigator.xr` (R3, P, grep).
The rendered view creates `WebGLRenderer({antialias:false, alpha:false, preserveDrawingBuffer:true})`
(`src/js/engine/render/rendered-core.js:104`) and draws with its own `requestAnimationFrame` refine loop
(`rendered-view.js:187` to `206`) (R3, P); an XR session needs `renderer.xr.enabled = true` and
`renderer.setAnimationLoop`, which runs on the session's own frame callback. `WebGLRenderer`'s XR path does not use
`OVR_multiview2` (only the node-based renderers in `src/renderers/common/` do), so each eye is a separate pass (T1, P).
`src/js/engine/render/headset.js` holds only V274's header so far (R3, P).

### 3.6 Prior art for one input layer

**F20. MRTK3 (Microsoft, on Unity's XR Interaction Toolkit).** Input device, interactor and events are "architecturally
isolated"; interactors "generally don't have to map 1:1 with input devices"; every interactor moves an
`attachTransform` (the grab point, the ray's hit point, the mouse click point) and the object being moved reads only
that, "regardless of the input modality". Interfaces: poke (with a `PokeRadius`), grab (near), ray (far), gaze
(passive), gaze-pinch (gaze targets, the hand manipulates; several pinches offset from their median for two hands),
speech; select can be analog (`SelectProgress`). It warns against coding to a specific input type (K1, P, updated
2026-10-26). Confidence **high**.

**F21. Meta Interaction SDK.** Interactors ("initiate interactions") and interactables ("can be interacted with");
each interactor scores candidates of its own type (`ComputeCandidate`, `ProcessCandidate`) and `Drive()` advances
hover and select; groups arbitrate between a hand's interactors; types include grab, poke, ray and pose detection
(M9 to M11, P, but only card-level text was available). Confidence **medium** (summaries of the pages, not the code).

**F22. pmndrs/xr and pointer-events (MIT, 2023 Coconut Capital and 2024 Bela Bohlender), used by Meta's IWSDK.**
"Mouse, touch, XR controllers, hands, and custom inputs all become pointers that emit DOM-style pointer events
(`click`, `pointerover`, `pointerdown`, ...) on three.js objects, including pointer capture" (X1, P). Three pointer
kinds: ray, grab (a sphere of radius 0.07 m) and touch (pressed within 0.03 m) (X1 code, P). `@pmndrs/xr` classifies each
WebXR input by `hand`, then `targetRayMode` into gaze, screen, transient-pointer and controller, and drives a ray
pointer from the platform's `select` and a grab pointer from `squeeze` (X2, P). Meta's IWSDK: "a `MultiPointer` per
hand", `select` to the ray pointer, `squeeze` to the grab pointer, "powered by `@pmndrs/pointer-events`" (M12, P).
Confidence **high**. The packages are TypeScript-compiled ES2020 modules; the app would take the design, not the code
(the library rule allows a vendored library behind an adapter, but this one is small and our adapter would be most
of its value).

**F23. A-Frame 1.x hand-tracking-controls (MIT):** pinch enters below 0.015 m and ends above 0.02 m, and emits
`pinchstarted`, `pinchmoved`, `pinchended` with the midpoint of thumb and index tips and the wrist rotation (X3, P).
With three.js (0.015/0.025) and the MRTK, Ultraleap figures in `research-devices-xr/hands-and-physics.md` (0.02/0.05,
0.025/0.03), four implementations put the pinch's entry at 1.5 to 2.5 cm with a hysteresis gap of 0.5 to 3 cm.

**F24. The input profiles registry** (immersive-web/webxr-input-profiles) is under the W3C Software and Document
License (I1, P); its assets package is MIT (I2, P). It lists controller layouts per device, including
`meta-quest-touch-plus`, `samsung-galaxyxr`, `generic-hand` and `generic-hand-select`.

**F25. A headset emulator for tests.** Meta's Immersive Web Emulation Runtime, `iwer` 2.8.0 (MIT), is a JavaScript
WebXR runtime with device presets `metaQuest2`, `metaQuest3`, `metaQuestPro`, hands, controllers, planes, meshes,
anchors, hit test and depth (E1, P, its `lib/` folders read). It would let a Playwright suite open an XR session
without a headset; not a shipped library, but still a third-party package that needs the owner's approval.

## 4. The device ladder

Costs are US list prices at launch from press (S) unless said; they move, so confirm before buying.

| Device | Cost | How the app reaches it | Tracking | Hands (joints, source) | Passthrough | What our app must add | Effort |
|---|---|---|---|---|---|---|---|
| Desktop or laptop (owner's MacBook Air, Windows mini PC) | owned | URL, or the installed web app (V172h) | none (screen) | MediaPipe from a webcam, 21 points, one camera (Mac only; mini PC has no webcam) | n/a | the input layer's mouse/touch and MediaPipe adapters | small: mouse and touch exist (`ui/touch-input.js`), MediaPipe as XR-2 |
| iPhone 13 in cardboard (owned) | owned | URL in Safari, or the Home Screen app | 3DoF, motion sensors (no WebXR, P) | MediaPipe, 21 points, measured 35 to 39 a second | the camera drawn behind (app does it) | V274 XR-1 to XR-4 as planned | planned (research-devices-xr.md) |
| Android phone, Chrome | about 200 up (any ARCore phone) | URL | 6DoF in immersive-ar (ARCore); immersive-vr via Cardboard runtime (built in, untested) | none in WebXR (C1); MediaPipe possible as on the iPhone | camera AR (immersive-ar) | session start, `screen` taps, hit test to place the model on a table | small once the XR session code exists |
| Meta Quest 3S / Quest 3 | 299 (3S 128 GB) / 499 (3, 512 GB) at 2024 launch; reported since at 249 to 349 for 3S (S) | URL in Quest Browser; Web Launch from phone (S); optional store package by Bubblewrap, 2D or immersive (P) | 6DoF | WebXR, 25 joints a hand with radii, pinch as select (P) | yes, immersive-ar, colour on Quest 3/3S; planes, anchors, meshes, depth, hit test (P/S) | the XR session adapter, the WebXR input adapter, 3D menus (no HTML in an immersive session), a hand visual (primitive or vendored glb), frame-time care at 72 to 90 Hz | medium: the first headset; the session and in-world UI are new |
| Android XR (Samsung Galaxy XR) | 1,799, controllers 250 (S) | URL in Chrome | 6DoF | WebXR Hand Input, the default input, 25 joints (P) | yes, immersive-ar, stereo depth (P) | nothing beyond the Quest's work, plus a permission-denied path | small after the Quest |
| Apple Vision Pro | 3,499 at launch (U, not read here; to confirm) | URL in Safari | 6DoF | transient-pointer (gaze + pinch, no hover) for actions; 25 joints for pose only, after a permission (P) | no immersive-ar (P); `<model>` USDZ in a page instead | the transient-pointer adapter, handle inputs at any index, no hover-dependent UI, joint pinch suppressed while a transient pointer is active | small after the Quest; USDZ export would be extra |
| PC headset through Chrome on Windows (a Quest over Link) | the headset, plus a PC able to drive it (U for the mini PC) | URL in desktop Chrome | 6DoF | WebXR hands through OpenXR (C1) | depends on runtime | nothing beyond the Quest's work | none extra |

## 5. One input layer: the proposal (H4)

The design follows the three prior arts that agree (F20 to F22): sources are separated from what they do; every
source becomes one or more **pointers**; each pointer has a pose and a pressed state; manipulation code reads only
the pointer's pose, never the device. Everything below is ES5, in `src/js/engine/xr/` (new folder; names indicative).

**The pointer.** `{ id, source: 'mouse'|'touch'|'webxr-hand'|'webxr-controller'|'webxr-transient'|'webxr-screen'|'mediapipe'|'gaze',
kind: 'ray'|'grab'|'poke', hand: 'left'|'right'|'none', origin: [x,y,z], dir: [x,y,z] (ray) or point: [x,y,z] (grab,
poke), radius (grab 0.07 m, poke 0.01 m to the fingertip's joint radius), pressed: boolean, strength: 0..1 (optional,
analog select as MRTK3's SelectProgress), caps: { hover, depth, joints } }`. Poses are in the model's metres, the
same frame the rendered view uses.

**The events,** one stream for all devices: `point` (pose update, every frame the source has one), `press` (start of a
pinch, a click, a tap, a trigger, a poke crossing a surface), `drag` (pose update while pressed), `release`, `cancel`
(the source vanished while pressed: tracking lost, transient pointer removed, permission revoked). Then two
recognisers on top, not in the adapters: **grab** (a `grab` pointer pressed with a hit inside its radius) and
**two-hand** (two pointers pressed on the same target: translate by the midpoint, scale by the distance ratio,
rotate by the change of the line between them, MRTK3's median rule). Hover (`enter`/`leave`) is derived from `point`
only where `caps.hover` is true.

**How each device maps onto it.**

| Source | Pointers it makes | press / release from | Pose from | Hover | Notes |
|---|---|---|---|---|---|
| Mouse | 1 ray | `pointerdown`/`pointerup` (button 0) | camera through the cursor | yes | existing handlers stay; the layer only adds a ray |
| Touch | 1 ray per finger; two fingers feed two-hand | `pointerdown`/`pointerup` | camera through the touch point | no | today's pinch-zoom and orbit remain the default on a phone without a session |
| WebXR hand (Quest, Galaxy XR, PC) | 1 ray (target ray space), 1 grab (between thumb and index tips), 1 poke (index tip) | the session's `selectstart`/`selectend` for the ray (F2); for grab and poke, our own joint test (pinch enter 0.015 to 0.02 m, leave 0.025 m; poke by crossing a surface) | `targetRaySpace`, `getJointPose` | yes | near versus far picked by distance to the nearest target, MRTK3's near mode (F20) |
| WebXR controller | 1 ray, 1 grab | `select*` (trigger), `squeeze*` (grip) | `targetRaySpace`, `gripSpace` | yes | layout from the input profile; no model needed to work |
| WebXR transient pointer (Vision Pro) | 1 ray, created at `selectstart` | `selectstart`/`selectend` | `targetRaySpace` (gaze at start, then follows the hand); drag moves with `gripSpace` | **no** | the hand inputs fire nothing (F10); our own joint pinch is turned off for far use while a transient pointer exists, so one pinch is not two presses; inputs can be at any index (F10) |
| WebXR screen (Android phone AR) | 1 ray per tap | `selectstart`/`selectend` | `targetRaySpace` | no | handheld AR only |
| MediaPipe (phone, laptop webcam) | 1 ray (wrist to index base, or the camera ray through the pinch point), 1 grab, 1 poke | our pinch with hysteresis, tuned wider for one camera (research-devices-xr hands-and-physics: in 2 to 2.5 cm, out 3 to 5 cm) after the One Euro filter | 21 landmarks, depth from the one-time calibration | yes | depth weaker: poke only near the calibrated distance; grab on pinch, not on contact |
| Gaze only (cardboard without hands) | 1 ray from the head | a tap on the screen or the viewer's button | head pose | yes | the fallback for any 3DoF viewer |

**Why WebXR and our own pinch both.** On every headset read (Quest, Android XR, Vision Pro) the platform already
turns a pinch into `select`, tuned to its own tracking; the layer uses it for the ray. Joint distances are needed only
for grab and poke near the hand (which the platform does not report as such) and for MediaPipe. three.js's own
`pinchstart` (F17) is not used directly, because its thresholds are fixed and on Vision Pro it would double the
transient pointer's select.

**What three.js already gives and what we add.** three gives the session, the eyes, the joint poses and the select
events (F17); we add the adapters above, a small dispatcher, the two recognisers, a hand visual (F18), and in-world
menus, because no HTML is drawn inside an immersive session on a headset (the DOM overlay feature is for handheld AR;
Quest's HTML-in-canvas hit testing is experimental, F7). That last item, 3D menus for the app's commands, is the
largest piece of work on the whole ladder.

## 6. Counter-evidence and disagreements

- **MDN's compatibility data says Safari has no WebXR** (`version_added: false` on every interface, B1), while WebKit
  says visionOS 2 shipped immersive-vr, transient-pointer and hand tracking (A2). The data's Safari column follows
  macOS and iOS; it has no visionOS browser. The vendor's statement wins for visionOS; the data is right for iPhone
  (measured in E3: `navigator.xr` undefined).
- **Meta's mixed-reality page names only Quest 2 and Quest Pro** (M2); Quest 3 and 3S colour passthrough rests on the
  2023 blog (M14) and on BCD. Recorded as an out-of-date page, not a contradiction.
- **Quest PWA submission:** a 2024 forum reply said PWAs could not be submitted; Meta's 2026 pages describe the
  process (M7). The newer vendor page is taken.
- **Vision Pro hands:** H2 assumed no joints by default; Apple's own post shows joints after a permission (F10). The
  hypothesis is corrected, not refuted (actions still come only from the transient pointer).
- **three.js and Vision Pro:** WebKit warns that three.js examples act only on controllers 0 and 1, while the transient
  pointers land at 2 and 3 when hands are on (A1); forum threads confirm the symptom (search 21, S). three.js assigns
  input sources to controller slots in arrival order (`onInputSourcesChange`, T1, P), so the app must listen on every
  slot or on the session itself, and must not assume slot 0 is the left hand.
- **Hand tracking quality on Galaxy XR** is reported both "on par with Apple" and "a mixed bag" by reviewers (S); not
  relevant to the event model, relevant to thresholds.
- **Chrome Cardboard on phones:** compiled in by default (C1), but no current statement that `immersive-vr` is offered
  to every Android phone; untested here.
- Looked for and not found: a headset browser where hands exist but neither `select` nor joints reach the page (which
  would break H4); a Meta statement that three.js is unsupported (Meta recommends IWSDK, built on three.js).

## 7. Outcomes for H1 to H4

| Id | Outcome | Evidence | Confidence |
|---|---|---|---|
| H1 | **Held.** Quest Browser gives immersive-vr and immersive-ar with passthrough, WebXR hands with 25 named joints and radii, pinch as select, planes, anchors, hit test, meshes and depth. One web app serves it; a store package is optional. | F1 to F7; M1, M2, M7, B1, W2 | high (medium for meshes and depth details) |
| H2 | **Held, corrected.** Safari on visionOS runs immersive-vr by default since visionOS 2; actions come only from the transient pointer (gaze at the pinch, then the hand), with no hover; hand joints are given after a permission prompt, for pose only; no immersive-ar. | F8 to F12; A1, A2, A5, W1 | high (medium for visionOS 26/27 defaults) |
| H3 | **Held in part.** The bundle already has WebXR sessions, controllers, hand joints and pinch; it lacks the hand and controller models and the session buttons (examples/jsm), whose defaults fetch from a CDN; the app has no XR code, and its rendered view must move to `setAnimationLoop`. Not run on any headset. | F17 to F19; T1, R1 to R3 | high for what the code contains; untested on devices |
| H4 | **Held, with two limits.** Every device's input reduces to pointers (ray, grab, poke) with press, drag, release and cancel, plus a two-hand recogniser, as MRTK3, Meta's SDKs and pmndrs do. Limits: Vision Pro gives no hover, so no UI may depend on hover; one-camera MediaPipe has weak depth, so poke and grab by contact are unreliable there and grab is by pinch. | F9, F10, F15, F20 to F23; part 5 | medium-high (design, not built) |

## 8. What can be tested now, and later on a Quest

**On the owner's devices now:**
- iPhone 13 and MacBook Air: the MediaPipe adapter's pinch, drag and release with the mouse-like ray, using V274's phone
  test page as the base (already measured: E3).
- MacBook Air Safari: `navigator.xr` presence and `isSessionSupported` answers (expect no immersive session without a
  headset); a report, not a feature.
- Any desktop browser: the input layer's unit tests (pure functions: pinch hysteresis, two-hand transform from two
  pointer tracks, transient-pointer dedupe) in `tests/unit/`, under Rule #1's table.
- With the owner's approval of `iwer` (MIT) as a test-only package: a Playwright run that opens an emulated Quest 3
  session against the app, injects a hand pinch and checks one `press`/`release` pair reaches the layer.
- If an Android phone is at hand: `immersive-ar` placement and `screen` taps in Chrome.

**Later on a Quest 3 or 3S:**
- `isSessionSupported` for both modes; the granted features (`hand-tracking`, `local-floor`, `layers`,
  `plane-detection`, `hit-test`, `anchors`, `depth-sensing`); `supportedFrameRates`.
- Frame time of the app's model at 72 and 90 Hz with each eye a separate pass; `setFoveation` and framebuffer scale.
- Pinch: one `select` per pinch; the joint grab's thresholds against the platform's select; palm pinch reserved.
- Passthrough with a transparent clear; plane detection after 2 to 3 s; persistent anchors (8 per site).
- Opening paths: URL, Web Launch from the iPhone, an installed web app if Quest Browser offers it.
- Vision Pro, if ever: the same suite with transient pointers at indices 2 and 3 and no hover.

## 9. Still open (U)

- Quest Browser's install button for a plain PWA (no Meta statement found); Web Launch's current availability.
- Meta's own WebXR documentation for meshes and depth on Quest 3/3S (only BCD and a press report read).
- Whether visionOS 26 and 27 keep WebXR on by default (no statement either way; to test on a device).
- Whether Chrome on an ordinary Android phone offers `immersive-vr` (Cardboard) by default today.
- The Layers module's own text (its source path answered 404); only three.js and BCD read.
- Meta Interaction SDK's interactor states read as page summaries only.
- Whether the owner's Windows mini PC can drive a Quest over Link.
- Current device prices.

## 10. References (all read 2026-11-23)

| Id | Source | URL | What was read | Level |
|---|---|---|---|---|
| M1 | Meta, WebXR Hands | https://developers.meta.com/horizon/documentation/web/webxr-hands/ | 25 joints, palm pinch, pinch as gamepad button | P |
| M2 | Meta, WebXR Mixed Reality | https://developers.meta.com/horizon/documentation/web/webxr-mixed-reality/ | immersive-ar, planes, anchors, room capture | P (devices named out of date) |
| M3 | Meta, WebXR overview | https://developers.meta.com/horizon/documentation/web/webxr-overview/ | IWSDK, feature detection, subpages | P |
| M4 | Meta, WebXR performance | https://developers.meta.com/horizon/documentation/web/webxr-perf/ | the workflow; no numbers | P |
| M5 | Meta, WebXR frame rates | https://developers.meta.com/horizon/documentation/web/webxr-frames/ | 72/90 defaults, 11 ms at 90 Hz, updateTargetFrameRate | P |
| M6 | Meta, WebXR performance best practices | https://developers.meta.com/horizon/documentation/web/webxr-perf-bp/ | lights, shadows, animation rate | P |
| M7 | Meta, PWA overview (updated 2026-07-22) | https://developers.meta.com/horizon/documentation/web/pwa-overview/ | Bubblewrap --metaquest, TWA, 2D or immersive, optional store | P |
| M8 | Meta, Browser release notes | https://developers.meta.com/horizon/release-notes/web/ | entries 144.2 to 156.0 | P |
| M9 | Meta, Interaction SDK overview (2026-10-07) | https://developers.meta.com/horizon/documentation/unity/unity-isdk-interaction-sdk-overview/ | interactor and interactable | P (summary depth) |
| M10 | Meta, ISDK architectural overview (2025-08-07) | https://developers.meta.com/horizon/documentation/unity/unity-isdk-architectural-overview/ | groups, lifecycle cards | P (summary depth) |
| M11 | Meta, ISDK Interactor (2026-09-08) | https://developers.meta.com/horizon/documentation/unity/unity-isdk-interactor/ | ComputeCandidate, ProcessCandidate, Drive | P |
| M12 | Meta, IWSDK XR input pointers (2026-03-11) | https://developers.meta.com/horizon/documentation/web/iwsdk-concept-xr-input-pointers/ | RayPointer, GrabPointer, MultiPointer, select/squeeze | P |
| M13 | Meta blog, Web Launch for WebXR (2022-11-29) | https://developers.meta.com/horizon/blog/webxr-web-launch-mobile-matterport/ | sending a URL to the headset | S (old) |
| M14 | Meta blog, Building for MR on Quest 3 (2023-09-28) | https://developers.meta.com/horizon/blog/building-mixed-reality-MR-meta-quest-3-connect-developers-presence-platform/ | full-colour passthrough, Depth and Mesh APIs | S |
| U1 | UploadVR, Quest Browser 40.4 hit test on Depth API (2025-10-10) | https://www.uploadvr.com/quest-browser-depth-api-webxr-hit-testing-instant-placement/ | hit test without room scan, 5 m depth | S |
| A1 | WebKit, Introducing Natural Input for WebXR in Apple Vision Pro (2024-03-19, Cannon and Zachernuk) | https://webkit.org/blog/15162/introducing-natural-input-for-webxr-in-apple-vision-pro/ | transient-pointer, gripSpace, hands pose-only, indices 2 and 3 | P |
| A2 | WebKit, Features in Safari 18.0 | https://webkit.org/blog/15865/webkit-features-in-safari-18-0/ | "Spatial Web": immersive-vr, transient-pointer, hand tracking with permission | P |
| A3 | WebKit, Features in Safari 26.0 | https://webkit.org/blog/17333/webkit-features-in-safari-26-0/ | `<model>` on visionOS, immersive media; no WebXR change | P |
| A4 | Apple Developer Forums 743655 | https://developer.apple.com/forums/thread/743655 | immersive-ar false, immersive-vr true (developers) | S |
| A5 | Apple Developer Forums 826845 | https://developer.apple.com/forums/thread/826845 | Apple engineer, June 2026: immersive-ar not supported; user claim on visionOS 27 | P for Apple's reply, U for the claim |
| G1 | Android Developers, Develop for the web on Android XR | https://developer.android.com/develop/xr/web | feature list, hand input default, permissions, stereo depth | P |
| W1 | W3C WebXR Device API (CR), Bikeshed source | https://raw.githubusercontent.com/immersive-web/webxr/main/index.bs | XRTargetRayMode, transient input sources | P |
| W2 | W3C WebXR Hand Input Module Level 1 (ED) | https://raw.githubusercontent.com/immersive-web/webxr-hand-input/main/index.bs | XRHandJoint (25), radius, generic-hand-select, privacy, frequencyHint | P |
| W3 | W3C WebXR AR Module | https://raw.githubusercontent.com/immersive-web/webxr-ar-module/main/index.bs | interactionMode, screen inputs | P |
| B1 | MDN browser-compat-data, main branch | https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/ (XR*.json) | Chrome, Quest Browser, Safari columns | P (no visionOS column) |
| C1 | Chromium source, main | https://chromium.googlesource.com/chromium/src/+/main/device/vr/ (features.cc, buildflags.gni), chrome/browser/about_flags.cc | runtimes built on Android, OpenXR default on Windows, hand tracking tied to OpenXR | P |
| P1 | Google, MediaPipe Hand Landmarker guide | https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker | 21 keypoints, coordinates, handedness | P |
| T1 | three.js 0.186.1, npm tarball (sha256 8cd068708ea44f2c73c944b1cead2ba2f0d5c15c8fc194e5700f4e4f4a033fe7) | `npm pack three@0.186.1` | src/renderers/webxr/WebXRManager.js, WebXRController.js; examples/jsm/webxr/*.js | P |
| R1 | The app's bundle | runtime/three/0.186.1/bim-three.min.js | grep counts of WebXR names | P |
| R2 | The app's three build | tools/three/build_three.mjs | the entry list | P |
| R3 | The app's code | src/js/engine/render/rendered-core.js:104, rendered-view.js:83 to 206, headset.js; grep of src/ | renderer options, loop, no XR use | P |
| K1 | Microsoft, MRTK3 interactor architecture (updated 2026-10-26) | https://learn.microsoft.com/en-us/windows/mixed-reality/mrtk-unity/mrtk3-overview/architecture/interactors | attachTransform, interfaces, modality abstraction | P |
| X1 | pmndrs pointer-events 6.6.32 (MIT) | npm `@pmndrs/pointer-events`; https://github.com/pmndrs/xr | README, LICENSE, dist/pointer/grab.js, touch.js | P |
| X2 | pmndrs xr 6.6.32 (MIT) | npm `@pmndrs/xr` | dist/input.js, vanilla/default.js | P |
| X3 | A-Frame, hand-tracking-controls.js (MIT) | https://raw.githubusercontent.com/aframevr/aframe/master/src/components/hand-tracking-controls.js | pinch 0.015/0.02, events | P |
| I1 | WebXR input profiles registry (W3C Software and Document License) | https://raw.githubusercontent.com/immersive-web/webxr-input-profiles/main/ (LICENSE.md, generic-hand-select.json) | licence, hand-select layout | P |
| I2 | `@webxr-input-profiles/assets` 1.0.20 (MIT) | npm | profiles list, generic-hand glb sizes, LICENSE.md | P |
| E1 | Immersive Web Emulation Runtime `iwer` 2.8.0 (MIT) | npm `iwer`; github.com/meta-quest/immersive-web-emulation-runtime | lib/ folders, device presets | P |
| D1 | Prior note | docs/research/research-devices-xr.md and research-devices-xr/hands-and-physics.md | E3 measurements, pinch thresholds | P (our own measured record) |
| S1 | Press: Meta Quest 3S launch (about.fb.com, 2024-09), Galaxy XR (Android Central, Engadget, UploadVR, 2025-10) | via search results | prices | S/U |
