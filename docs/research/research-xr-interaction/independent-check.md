# Independent check of the three topic notes (protocol step 9)

Second reader for `docs/research/research-xr-interaction.md`, 2026-11-23. I did not write `devices.md`, `gestures.md`
or `bim-xr.md`. Each fact below was re-read in its source on 2026-11-23, not in the notes' paraphrase. How each source
was read:

- **Text read directly** (curl or npm, then read as text in the session scratchpad, never run): the three.js 0.186.1
  tarball (sha256 `8cd06870...4a033fe7`, matches the note), `iwer` 2.8.0, `@pmndrs/pointer-events` and `@pmndrs/xr`
  6.6.32, `@webxr-input-profiles/assets` 1.0.20, `@thatopen/components` 2.4.11 `dist/index.mjs`, a sparse clone of
  MRTK3 at 83c8c1d, Chromium `features.cc` and `buildflags.gni` (main), MDN browser-compat-data (main), the WebXR Hand
  Input Bikeshed source, WebKit blog posts 15162, 15865 and 17333, Apple HIG `gestures.md`, `spatial-layout.md`,
  `designing-for-visionos.md` and `eyes.md`, Microsoft's hand menu, typography and interactable object pages,
  Android XR's considerations and ARCore hands pages, developer.android.com/develop/xr/web, and the PDFs of
  Hincapie-Ramos 2014, Song 2012, Nacenta 2013, the MediaPipe gesture model card, GRLib (arXiv 2310.14919) and Li
  et al. 2008 (`pdftotext`).
- **Read through the fetch tool's digest** (the host refused curl with 400 or a bot check; the page is primary but
  its wording passed through a summariser that quotes): every developers.meta.com page, the two Apple forum threads,
  help.sketchup.com, thewild.com, arkio.is, jig.com, the App Store listing, the Shapr3D blog, Autodesk's press release,
  the APS blogs and ExplodeExtension page, the Revit help page, docs.unity3d.com, Meta's Browser release notes, Google's
  Android XR help and MediaPipe hand landmarker guide. A fact checked this way is marked "confirmed (digest)".
- **Could not reach:** workshopxr.autodesk.com (not resolvable from this session), docs.unity.com Reflect pages.
- **The app's code:** every cited file:line opened in `src/` at the current working tree.

Verdicts: confirmed, corrected, or could not check. A fact that fails goes back to U (protocol step 9).

## 1. devices.md

| Claim | What I read | Verdict | Correction or note |
|---|---|---|---|
| F1: Meta exposes 25 joints a hand | Meta webxr-hands (digest): "The API exposes the poses of the 25 skeleton joints" | confirmed (digest) | |
| F1: the `XRHandJoint` enum has exactly 25 names; tips should have a nonzero radius | webxr-hand-input `index.bs`, enum counted by script: 25; line 214 "SHOULD have an appropriate nonzero radius" | confirmed | |
| F1: BCD gives `XRHand` in Quest Browser from 15.1 | BCD `api/XRHand.json`: oculus 15.1 (chrome 131, safari false) | confirmed | |
| F2: hand sources must carry `generic-hand-select` | `index.bs` line 188, MUST | confirmed | the same section lets a UA surface squeeze as a "grasp button" (`generic-hand-select-grasp`); the input layer should accept either |
| F2: pinch is the emulated Gamepad button; palm pinch reserved on both hands; left = menu button | Meta webxr-hands (digest): all three quoted | confirmed (digest) | |
| F3: immersive-ar, transparent background; page names only Quest 2 and Pro | Meta webxr-mixed-reality (digest): "use the new 'immersive-ar' mode", "You must draw your content on a transparent background", "on Meta Quest 2 and Meta Quest Pro headsets" | confirmed (digest) | |
| F4: plane detection "wait 2 to 3 s"; 8 persistent anchors a site; none in private mode; `initiateRoomCapture` | same page (digest) | confirmed (digest), wording corrected | the 2 to 3 s is how long to wait before deciding to call room setup because no planes came, not a general wait; `initiateRoomCapture` "can only be called once per session" (add it) |
| F4: BCD lists persistent anchors, planes, `supportedFrameRates`, `updateTargetFrameRate` from 31.2, `trackedSources` 34.1 | BCD XRAnchor, XRPlane, XRSession | confirmed | `detectedMeshes`, depth and layers not re-read |
| F4: hit test via Depth API since Browser 40.4 (UploadVR) | not re-read | could not check | stays S as the note says |
| F5: 90 fps default on Quest 2, 72 on other Quest headsets; 11 ms at 90 Hz; `supportedFrameRates`, `updateTargetFrameRate` | Meta webxr-frames (digest): "runs by default at 90 frames per second on Meta Quest 2 and 72 frames per second on Meta Quest headsets"; "longer than 11ms for a 90Hz framerate" | confirmed (digest) | |
| F6: Bubblewrap `--metaquest`, TWA, 2D or immersive, store optional, updated 2026-07-22 | Meta pwa-overview (digest), all quoted, date 2026-07-22 | confirmed (digest) | |
| F7: Browser 146.0 (21 Apr 2026), 154.0 (14 Oct 2026), 156.0 (13 Nov 2026) entries | Meta release notes (digest) | confirmed (digest) | 154.0 also adds a high-fidelity body tracking flag |
| F8: Safari 18.0 for visionOS 2 adds immersive-vr, transient-pointer, hand tracking with a permission at session start | WebKit blog 15865, text extracted: all three sentences present | confirmed | |
| F8: visionOS 1.1 had it behind a flag | WebKit 15162: "available behind a flag for Safari 17.4 in visionOS 1.1" | confirmed | |
| F8: Safari 26.0 post lists no WebXR change | WebKit 17333: the word "WebXR" occurs 0 times | confirmed | "on by default in 26 and 27" stays medium (absence of a statement) |
| F9: transient pointer: `inputsourceschange` then `selectstart`, `targetRaySpace` from between the eyes along the gaze, `gripSpace` | WebKit 15162 text | confirmed | |
| F10: hand inputs "for pose information only and do not trigger any events"; transient pointers at 2 and 3; three.js examples act on 0 and 1 | WebKit 15162, both sentences verbatim | confirmed | |
| F11: Apple engineer, June 2026: "The WebXR immersive-ar mode isn't currently supported in visionOS" | forum 826845 (digest): "Vision Pro Engineer", Jun '26, sentence verbatim; the visionOS 27 removal claim is from a user (5of12), Sep '26, unanswered | confirmed (digest) | |
| F11/A4: "Developers measured `isSessionSupported('immersive-ar')` false" | forum 743655 (digest): one developer (jol-jol, Dec 2023, flag on), immersive-ar false, immersive-vr true; no Apple reply | corrected | one developer, visionOS 1, not "developers"; S stays |
| F12: `<model>` on visionOS 26: fallback image, environment map, `entityTransform`, drag models off the page | WebKit 17333 text: all present | confirmed | |
| F13: Chromium builds Cardboard and ARCore on Android by default (`_is_xr_supported_android`) | `buildflags.gni` lines 14, 19, 21 | confirmed | |
| F13: `IsHandTrackingEnabled()` returns `IsOpenXrEnabled()` | `features.cc` lines 79-85 | confirmed | `IsOpenXrEnabled()` is also true on an Android XR device (`IsXrDevice()`, line 64-66), which is how Galaxy XR gets hands |
| F16: `kOpenXR` enabled by default on Windows | `features.cc` lines 51-53 | confirmed | |
| F14: Android XR: hand input is the primary mechanism and default; all WebXR APIs need the "3d mapping and camera tracking" permission; stereo depth | developer.android.com/develop/xr/web, text extracted, all verbatim | confirmed | |
| F15: MediaPipe 21 keypoints, normalised x/y, world landmarks in metres about the hand's centre, handedness of the subject, one hand by default | MediaPipe hand landmarker guide (digest); also thresholds 0.5 | confirmed (digest) | |
| F17: `WebXRManager` has `getHand`, `getControllerGrip`, `setFramebufferScaleFactor`, `setReferenceSpaceType`, `setFoveation`, `getEnvironmentBlendMode`, `getDepthTexture`; projection layer when `createProjectionLayer in XRWebGLBinding.prototype`, else `XRWebGLLayer` | tarball `src/renderers/webxr/WebXRManager.js` lines 153, 176, 289, 311, 439-451, 496, 523, 544, 561, 877 | confirmed | |
| F17: `WebXRController` reads joints with `getJointPose`, keeps `jointRadius`; `pinchstart` at distance <= 0.015, `pinchend` > 0.025 (`distanceToPinch = 0.02`, `threshold = 0.005`) | `WebXRController.js` lines 243, 253, 268-284 | confirmed | |
| F17: bundle counts (`getHand` 10, `pinchstart`, `thumb-tip`, `index-finger-tip`, `XRWebGLBinding`, `createProjectionLayer`, `inputsourceschange`, `squeezestart`, `getJointPose`, `jointRadius`, `setFoveation`) | grep of `runtime/three/0.186.1/bim-three.min.js`: 10, 1, 1, 1, 3, 2, 2, 2, 1, 1, 2 | confirmed | |
| F18: no hand or controller model factories or buttons in the bundle; build bundles three, GLTFLoader, GLTFExporter, DRACOLoader, meshopt | grep: 0 for each, 0 for `jsdelivr`; `tools/three/build_three.mjs` lines 31-35 | confirmed | |
| F18: `XRHandMeshModel` and `XRControllerModelFactory` default to jsDelivr | `examples/jsm/webxr/XRHandMeshModel.js:4,50`, `XRControllerModelFactory.js:16,284` | confirmed | |
| F18: generic-hand `left.glb` 94,572 and `right.glb` 94,004 bytes, MIT, Amazon 2019 | assets 1.0.20 tarball: sizes exact; LICENSE.md "MIT License, Copyright (c) 2019 Amazon" | confirmed | |
| F19: `WebGLRenderer` options at `rendered-core.js:104`; own rAF refine loop `rendered-view.js:187-206`; `headset.js` only a header | read: line 104 (also `powerPreference:'high-performance'`), `bimRvRefine` at 194-207 using `requestAnimationFrame`; `headset.js` 5 lines | confirmed | |
| F19: WebGLRenderer's XR path does not use `OVR_multiview2` | grep of tarball `src/`: matches only in `renderers/common/XRManager.js`, `webgl-fallback/` and `core/RenderTarget.js`; none in `renderers/webgl/` or `WebXRManager.js` | confirmed | |
| Part 6: three.js assigns input sources to slots in arrival order | `WebXRManager.js` `onInputSourcesChange` 567-607 (first null slot, else push) | confirmed | |
| F22: pointer-events grab sphere 0.07 m, touch pressed within 0.03 m | `dist/pointer/grab.js:5` (`radius ?? 0.07`), `touch.js:14` (`downRadius ?? 0.03`) | confirmed | |
| F22: licence "MIT, 2023 Coconut Capital and 2024 Bela Bohlender" | npm LICENSE files of both packages and `pmndrs/xr` main LICENSE: MIT text, "Copyright 2024 Bela Bohlender" only; package.json says "SEE LICENSE IN LICENSE" | corrected | MIT, Copyright 2024 Bela Bohlender; no Coconut Capital line in the files read |
| F22/M12: Meta IWSDK: a `MultiPointer` per hand, select to ray, squeeze to grab, powered by `@pmndrs/pointer-events` | Meta iwsdk-concept-xr-input-pointers (digest), updated 2026-03-11: all quoted | confirmed (digest) | |
| F25: `iwer` 2.8.0 MIT; presets `metaQuest2`, `metaQuest3`, `metaQuestPro` | tarball LICENSE "MIT License, Copyright (c) Meta Platforms, Inc. and affiliates"; package.json MIT; `lib/device/configs/headset` exports the three plus `oculusQuest1`, `metaVRGlasses`; `lib/` has anchors, depth, hittest, meshes, planes | confirmed | |
| F23: A-Frame pinch 0.015 / 0.02 | not re-read | could not check | low stakes (not used by code) |
| F20/F21: MRTK3 interactor architecture; Meta ISDK interactor pages | not re-read (design prior art only) | could not check | F21 is already medium |
| Device prices | not checked | could not check | stay S/U, as the note says |

## 2. gestures.md

| Claim | What I read | Verdict | Correction or note |
|---|---|---|---|
| Meta: poke target 22 x 22 mm, 12 mm spacing; "Pinching is a different gesture and should not be used for direct touch"; "Limit use to a small number of very simple poses and gestures"; long press 0.5 s, cooldown 0.25 s; gating | Meta hands-interaction-types (digest), all quoted | confirmed (digest) | the 0.5 s is given as an example delay |
| Meta ISDK pose detection: six poses; open to neutral above 195, back below 185; 0.0222 s | Meta unity-isdk-hand-pose-detection (digest), verbatim; also neutral to closed above 210, back below 200 | confirmed (digest) | |
| Meta tracking 30 Hz default, 60 Hz Fast Motion Mode "can create a jitter" | Meta hands-technology (digest) | confirmed (digest) | |
| Quest store rule: "the system gesture is reserved, and should not trigger any other actions within the app" | Meta vrc-quest-input-8 (digest): verbatim, marked Required for immersive and panel apps | confirmed (digest) | it is a Required VRC, not a recommendation; say so |
| Quest reserved gesture: left palm pinch "leaves the WebXR session" | Meta webxr-hands (digest) says only "equivalent to pressing the menu button on your left controllers" | corrected to U | that it ends or pauses the session is an inference; to test on a Quest |
| XRI 3 General Grab Transformer: `allowTwoHandedScaling`, `thresholdMoveRatioForScale`, min/max scale ratio, `permittedDisplacementAxes` | Unity API page (digest): all present | confirmed (digest), wording corrected | `thresholdMoveRatioForScale` is a ratio of relative hand displacement (0 to 1), not a distance; the "about 2 cm" dead zone in parts 3.4 and 4 is our own value (U), not XRI's |
| XR Hands: five finger shapes; pinch "often used as part of system gestures" | XR Hands 1.4 finger-shapes (digest) | confirmed (digest) | |
| MRTK3 licence BSD-3-Clause | `LICENSE.md` (main): "BSD 3-Clause License, Copyright (c) 2025, Mixed Reality Toolkit Contributors" | confirmed | |
| MRTK3 two-hand scale `startObjectScale * (current / start hand distance)` | `ScaleLogic.cs` lines 31-32, 57-58 at 83c8c1d (commit dated 2026-10-16) | confirmed | |
| MRTK3 rotation `FromToRotation(startHandlebar, current) * startRotation` | `RotateLogic.cs` line 57 | confirmed | |
| MRTK3 palm-up defaults: 80 degrees, flat hand 45 degrees, gaze proximity 0.01 and 0.04 squared | `HandConstraintPalmUp.cs` lines 25, 52, 105, 118, 304 (`sqrMagnitude`) | confirmed | also `followHandCameraFacingThresholdAngle` 60 degrees |
| Apple HIG: direct gestures "best for infrequent use"; two-hand pinch drag apart = zoom, circular = rotate; custom gestures only when necessary, not the only way; avoid a familiar gesture for an app-unique action | `gestures.md` lines 28, 36, 41, 92, 105-106 | confirmed | |
| Apple: "Reserve the area around a person's hand"; "If possible, don't anchor content to a person's hands or wrists"; rolling motion reserved | `gestures.md` lines 134, 164 | confirmed, with an omission | the same page says "Consider deferring the system overlay behavior when designing an immersive app or game" (Full Space apps can defer the Home indicator). Whether a WebXR session in Safari defers it is unknown (U). The note's "Apple discourages hand menus" is fair but softer than stated: "if possible" |
| Apple: indirect gestures with hands "in their lap or at their sides"; content at least 1 m away; no gaze before a tap | `designing-for-visionos.md:52`, `eyes.md:36`, `eyes.md:26` | confirmed | the 1 m is in `eyes.md`, not `spatial-layout.md` |
| Apple: centres 60 pt apart, 16 pt around | `spatial-layout.md:84` | confirmed | |
| Microsoft hand menu: attentional cone about 10 degrees, one column of three buttons, 13 cm above the palm, ulnar side | design/hand-menu, text extracted | confirmed | |
| Microsoft targets: 2 degrees, 1.6 x 1.6 cm at 45 cm (direct); 1 degree, 3.5 x 3.5 cm at 2 m (ray or gaze) | design/interactable-object | confirmed | |
| Microsoft text: 0.65-0.8 degrees (5.1-6.3 mm) at 45 cm, 0.6-0.75 (20.9-26.2 mm) at 2 m; minimum 0.4-0.5 at 45 cm | design/typography | confirmed | |
| Android XR: standard system gestures for 2D UI, mimic the real world for 3D; easy to learn, remember, execute; one-handed priority with alternatives; limit flying; teleport least sickening | design/ui/xr/guides/considerations, text extracted | confirmed | "is often the locomotion method that causes the least amount of motion sickness" |
| Android XR system gestures (palm facing you, pinch and hold: Launcher; hold: Circle to Search; move left: Back; right: Recents; palm up then pinch: Home); two-hand zoom | support.google.com/android-xr/answer/16639048 (digest), verbatim | confirmed (digest) | |
| ARCore hands: "Use the secondary hand for your custom gestures" | arcore/hands page, text extracted: system navigation on the primary hand; "Use the secondary hand for yo[ur]..." | confirmed | |
| Consumed Endurance: Rohmert curve asymptotic at 15 %; 12 participants; centre plane 27.23 %, bent arm 23.44 %; click with the other hand 8.18 %; 25 x 25 cm | Hincapie-Ramos et al. 2014 PDF lines 80, 241, 316-318, 332, 375 | confirmed | "bent" means the hand 35 cm or closer to the body plane; the click was a mouse held in the left hand; the lowest error rate was dwell (0.66), swipe differed from all |
| Song et al. 2012: Kinect senses position not orientation; rate-based scale ("A vigorous gesture gives a larger scaling factor"); "at least 2 to 3 times faster"; "ease to remember"; fatigue after 20-30 minutes; "perennial problem" | Song et al. PDF lines 17, 365-375, 508, 525, 541, 597 | confirmed | |
| Nacenta et al. 2013: "33 participants, sets of 22 free-form gestures per condition"; next-day recall 97/82/52 % (exp. 1) and 94/89/55 % (exp. 3) | Nacenta et al. PDF lines 50, 179, 243, 257, 322-324, 419-444, 463-548 | **corrected** | Experiment 1: 6 participants, 16 gestures per condition, 97/82/52 %. Experiment 2: 9 participants, 22 per condition, 94/89/55 %. Experiment 3: 18 participants, next-day 79/55/25 % (user-defined, pre-designed, random). 6+9+18 = 33. The gestures were free-form over a Microsoft Surface tabletop (on or above it), judged by an experimenter, no recogniser. So pre-designed sets were recalled at 55 to 89 % next day, not 82 to 97 %: the counter-evidence in gestures.md part 5 ("22 gestures recalled at 82 to 97 %") overstates it, and H6's "refuted in its strong form" rests on user-defined sets only. For a vocabulary the app designs (pre-designed), recall was 55 % in the largest experiment |
| Mutasim et al. 2021; Jacob 1991; Kostic et al. 2023; Stoakley et al. 1995 | not re-read | could not check | none is used by code; keep as the note marks them |
| MediaPipe gesture model card: out of scope motion and multiple hands; SS F1 93.9 to 95.5 %; not tested in the wild | model card PDF lines 80-91, 103, 150-166 | confirmed, wording sharpened | 95.5 % is the weighted average across skin-tone groups (range 94.3-97.8 %), 93.9 % across gender groups (range 93.1-94.4 %) |
| GRLib: forward and backward falsely detected (dropped); about 60 % precision overall, about 95 % ignoring repeats; circle and infinity 0 % recall | GRLib PDF lines 463-471 | confirmed | |
| Li et al. 2008 interactions (one click, drag slides along the direction, riffling) | Li et al. PDF lines 152-156, 251-259, 269-288, 318 | confirmed, with a nuance | the drag propagates to ancestors only once the part passes its fully exploded or collapsed position, and stops at a part with a different direction |
| Intro: thresholds "read in MRTK2, Ultraleap and three.js (enter about 2 to 2.5 cm, exit 3 to 5 cm)" | three.js tarball: enter 1.5 cm, exit 2.5 cm | corrected | three.js does not fit "enter 2 to 2.5, exit 3 to 5"; devices.md F23's range (entry 1.5 to 2.5 cm, gap 0.5 to 3 cm) is the right summary |
| EXPLODE already means "break a polyline" (`drafting-modify.js:159`) | see bim-xr F21 below | confirmed | |
| Licences of Meta ISDK and Unity XRI | not read by the note either | could not check | fine while only methods are taken |

## 3. bim-xr.md

### Prior art

| Claim | What I read | Verdict | Correction or note |
|---|---|---|---|
| F1: Workshop XR press release 2023-11-13, Quest 2, Pro, 3; "review their 3D models together at a 1:1 scale", "walk through models at a one-to-one scale", "synced issue tracking" with ACC | adsknews press release (digest): all quoted; no mention of The Wild or Prospect | confirmed (digest) | |
| F1/F6: The Wild and Prospect retired in favour of Workshop XR | workshopxr.autodesk.com/faq not resolvable here; a search summary says the FAQ names Workshop XR as the product their customers migrate to; thewild.com/help/tools-in-vr says nothing of retirement | could not check | stays S at best; "retired" is stronger than "customers are migrating": no dated shutdown found (U for any date) |
| F2: The Wild's eleven VR tools; no section; Inspect uses the "tool-hand trigger" | thewild.com/help/tools-in-vr (digest): the eleven tools listed, no section tool, trigger sentence verbatim | confirmed (digest) | |
| F3: SketchUp Viewer for Quest: "Hand tracking is not supported"; no longer available to download from 16 September 2025; Quest 2, Pro or 3 | help.sketchup.com/en/sketchup-viewer/meta-quest (digest), all verbatim | confirmed (digest) | |
| F3: two grips, apart to zoom in, twist to rotate; Tabletop default; Immersive 1:1 | help.sketchup.com moving-rotating-and-scaling (digest), verbatim | confirmed (digest) | the page calls the two-hand scale "Zoom" and the twist "Orbit" |
| F4: Resolve feature headings | not re-read | could not check | thin P as marked |
| F5: Arkio "Opens in your browser", "VR version of Arkio 3.0 is coming soon", Revit/Navisworks context, "Live co-design and threaded comments" | arkio.is (digest), all verbatim | confirmed (digest) | |
| F6: Unity Reflect unavailable since December 2024 | docs not reachable; a search found nothing | could not check | U, as the note says |
| F7: Shapr3D Vision Pro: "intuitive hand and eye motions", trackpad and keyboard, "full capabilities to edit directly in Vision Pro", real-time multi-user, 2024-03-27 | Shapr3D blog (digest) | confirmed (digest) | the post says "Multiple designers can view and edit in real-time together" |
| F7: JigSpace "Manipulate Jigs intuitively with your hands; pull apart components", SharePlay up to 4 users, requires visionOS 26 | App Store listing (digest): hands and pull apart quoted, "Requires visionOS 26.0 or later", no user count; jig.com (digest): "up to 4 users" in its FAQ; jig.com does not tie pull apart to hands in one sentence | confirmed (digest), sources split | the hands quote and visionOS 26 are from the App Store listing; the 4 users from jig.com |
| F12: Li et al. 2008 explosion graph, axes default ("parallel to the coordinate frame axes"), compactness, one-click expand, drag propagation, "single knob" (Agrawala 2003) | Li et al. PDF lines 108, 152-156, 251-259, 318 | confirmed | nuance on propagation as in part 2 |
| F13: Autodesk viewer Explode extension: toolbar button, slider, explosion value | APS v6 ExplodeExtension reference (digest), verbatim; it says nothing about levels | confirmed (digest), scope corrected | the Autodesk viewer's built-in explode is a radial explode by one amount. Explode by level is not a viewer feature: it exists only in the two APS developer-blog samples. H7's "BIM viewers already offer exploded views by level on a slider" should name these as samples, not product features |
| F14: APS 2018 vertical explode: `cz = Math.floor(z/10)*10`, `pt.z = cz * scale * 4`, ease-out | APS blog 2018-12-12 (digest), code verbatim | confirmed (digest) | the slider code is not in the post (linked to GitHub) |
| F14: APS 2024 explode along levels: first level whose top lies above the fragment's mid-height, `return key * scale`, Z only, reset at 0 | APS blog 2024-06-17 (digest): `if (fragMiddleZ < level.elevation + level.height - globalOffsetZ)`, `return key * scale`, `pt.z = ...` only | confirmed (digest), with a caveat | the post does not say what `key` is or guarantee the levels' order (a `for...in` loop); "the level's index" and "orders by the model's level list" (bim-xr part 5) are our reading (U) |
| F14: That Open `Exploder`, MIT, 2.4.11: group `spatialStructures`, `height` 10, raised by index times height, on or off, a transform of fragment instances | unpkg `dist/index.mjs` lines 25420-25500; package.json MIT | confirmed | `set(active)` applies a relative matrix (`elements[13] = i * factor * height`, factor -1 to undo) through `fragment.applyTransform`; group order is the object's key order (`for...in`), as the note says |
| F14: Revit Displace Elements: X, Y, Z; paths back to the original location; 2D elements cannot be displaced; no dimension references | Revit 2023 help (digest), all verbatim | confirmed (digest) | the page does not say displacement is per view; that remains S as the note marks it |
| F9: studies (Yigitbas, Liu, Horvat, Wolfartsberger, Paes) | not re-read | could not check | none is used by code |

### The app's code

| Claim | What I read | Verdict | Correction or note |
|---|---|---|---|
| F16: `A3D` holds `levels` `{id,name,elev,height,buildingId}`, `buildings`, `site`, `layers`, `objs` (`core/state.js:47-55`) | `state.js` 47-55 | confirmed | |
| F16: every level in exactly one building (`building-site-hierarchy.js:10-29`) | lines 10-29: `bimEnsureBuildings` backfills any level without a valid `buildingId` to the first building | confirmed | |
| F16: level of an object is `o.bim.levelId` or `o.levelId` (`saved-views.js:272-276`) | `bimObjectLevelId` at 272-276 | confirmed | |
| F16: layers have parents (`layer-rules.js:49-56`); `o.layer` (`:8-11`) | `bimLayerChain` 49-56; `bimLayerOf` 8-11 | confirmed | |
| F17: IFC storeys and containment at `ifc-full.js:121-140` | `bimIfcStoreys` 121-130, `bimIfcContainers` 131-140 | confirmed | |
| F17: one level per storey "<storey> (IFC)", no building id (`:205-208`) | lines 204-208 | corrected in detail | (a) a storey with no `Elevation` gets no level (`if(s.elev==null...)continue`) though its elements still get `bim.storey`, so the name match can fail and the mid-height fallback is needed; (b) the level has no `buildingId` when pushed, but `bimEnsureBuildings` gives it the first building after any restore, so "without a building id" is temporary; (c) a storey whose "(IFC)" name already exists is skipped, so a second import of the same file shares the first file's levels |
| F17: each element gets `bim.storey`, its class layer, `pos:[0,0,0]`, world mesh (`:210-227`) | lines 210-227 | confirmed | `bim.storey` comes from the containment map, whose holder can be an `IfcSpace` when no storey is above it; then `names[hold]` is empty and `storey` is '' |
| F18: GPU table row offset `v[0..2]=o.pos[...]` in `bimSceneSync` (`gpu-batches.js:144`), uploaded only when a row changes (`:56-61`) | line 144 verbatim; `bimGbPut` 56-61 marks dirty ranges only on change | confirmed | |
| F18: rendered view builds `tri + d[o]` (`rendered-scene.js:50-64`) | lines 49-64, `bimRvChunkArrays` | confirmed | |
| F18: GPU pick adds the row's `a.xyz` (`gpu-pick.js:15-20`) | lines 12-21: `gl_Position=uProj*uView*vec4(aPos+a.xyz,1.0)` | confirmed | |
| F18: CPU sites `terrain-3d.js:299, 335, 429`, `selection-tools.js:49` | 299 `uniform3f(offset, o2.pos...)` (an offset uniform, GL path in that file), 335 and 429 `m.v[j]+ob.pos`, selection-tools 49 `v+o.pos` | confirmed | 299 is a per-object uniform, not a CPU vertex add; it still must take the explode offset |
| F18: section swaps the mesh in `meshOf` (`mesh-primitives.js:185-187`) | line 185-187 | confirmed | |
| Part 9 open: does the rendered view's chunk cache rebuild when only offsets change? | `rendered-scene.js:41-46`, `bimRvChunkSig` hashes all 8 floats of each object's row | answered | yes: an offset change changes the chunk signature, so the chunk's arrays are rebuilt. Correct, but during a continuous two-hand explode every chunk with a moving object rebuilds each frame; a cost to measure |
| F19: `o.pos` read in 29 engine files | `grep -rlP '(?<![\w.$])o\.pos\b' src/js/engine`: **38** files (39 with a plain `o\.pos` grep); `objects-save.js` and `ifc-save.js` are among them | **corrected** | 38 files, not 29. The conclusion (never write `o.pos` for the explode) is unchanged and stronger. Other names also read positions (`ob.pos`, `o2.pos`: 56 files match `\.pos\b`), so the list of CPU paths that need the offset should come from a full audit, not from the four sites named |
| F20: undo is a whole-state JSON snapshot, 50 deep, without `A3D.section` (`plan-mode-sketch.js:315-365`) | line 315 `UNDO_MAX=50`, 316-317 `bimSnapshotState` (no `section`), 324 shift at max, 327 `bimRestoreState`, 366 `doUndo` | confirmed | |
| F20: saved view records camera, level, level filter, section (`saved-views.js:24-33`) | `bimCaptureView` 24-33 | confirmed | |
| F21: `EXPLODE`/`X` at `shell.js:115` runs `bimExplodeSelection` (`command-map.js:349`), breaking polylines with undo (`drafting-modify.js:159-193`) | shell.js 115; command-map.js 349 `explode:function(){bimExplodeSelection();}`; drafting-modify.js 159 header, `bimExplodePoly` 161-170, `bimExplodeSelection` 171-193 with `pushUndo()` | confirmed | |
| F21: `export-mappings.js:178` "exploded" hatching | line 178 "hatching as exploded lines" | confirmed | |
| `headset.js` 5 lines | `wc -l`: 5 | confirmed | |

The rest of bim-xr.md part 4 (command names and runner lines in `shell.js` and `command-map.js`) was not re-read
line by line beyond the EXPLODE row; it is a planning table, and each row should be re-read when a work order
names it.

## 4. Contradictions between the notes

1. **Vision Pro hand joints.** gestures.md 3.2 says "Safari's WebXR may not expose hand joints by default (H2,
   `devices.md`)". devices.md F10 found, and I confirmed in WebKit 15162 and 15865, that joints are given after a
   permission prompt, for pose only. gestures.md quotes the hypothesis, not the finding. The reason for a floating
   toolbar on Vision Pro is Apple's guidance (and that joints fire no events), not missing joints. Also, Apple lets
   Full Space apps defer the palm's Home indicator; whether WebXR does is untested.
2. **Pinch thresholds.** gestures.md's introduction says three.js's exit lies in 3 to 5 cm; three.js 0.186.1 exits at
   2.5 cm and enters at 1.5 cm (devices.md F17, confirmed). devices.md F23's range is the one to keep.
3. **Hands or controllers on Quest.** bim-xr.md F11 and decision 5 say the professional Quest apps are
   controller-first and controllers should be first-class; gestures.md's vocabulary (part 4) has a column for touch,
   mouse and the phone but none for Quest controllers. devices.md part 5 maps controllers into the input layer, so
   the gap is in the vocabulary table only: each row needs its controller mapping (trigger = select, grip = grab).
4. **Left palm pinch.** gestures.md 3.2 says it "leaves the WebXR session"; devices.md F2 and Meta's page say only
   that it equals the left menu button. Keep devices.md's wording.
5. **The explode's prior art.** gestures.md cites Li et al. for "one-hand drag on a storey slides it" and bim-xr.md for
   level explode "in BIM viewers". Per section 3 above, explode by level is in APS samples and That Open (on/off), and
   Revit's displacement is manual per set; the Autodesk viewer's product feature is a radial explode by amount. Both
   notes should say "samples and one open library", not "BIM viewers offer".
6. **Two-hand spread.** gestures.md uses `k` about 0.4 m for the full explode range; bim-xr.md uses "a reach constant"
   and a gap of the tallest storey. No contradiction, but the two must be one constant in the spec.

## 5. Level changes

- gestures.md, Nacenta et al. recall figures: the P level stands for the paper, but the figures as written were wrong
  (experiment numbering, set size, participants); the corrected figures above are P. The claim "people can memorise 8
  to 22 gestures at 82 to 97 %" goes back to U until rewritten.
- gestures.md, "left palm pinch leaves the WebXR session": P digest to **U**.
- gestures.md, "a dead zone like XRI's (about 2 cm)": the 2 cm is **U** (our value); XRI's parameter is a ratio.
- bim-xr.md, `o.pos` "in 29 files": the count fails the check; **corrected to 38** (P by grep, 2026-11-23).
- bim-xr.md, APS 2024 "offset = the level's index" and "orders by the model's level list": the code is P, its
  meaning (what `key` is, the order) is **U**.
- bim-xr.md, "The Wild and Prospect retired": S stays S for "Workshop XR is their successor"; any retirement date is U.
- devices.md, A4 "developers measured": one developer on visionOS 1; S stays, plural removed.
- devices.md, F22 licence holders: corrected (Bela Bohlender 2024 only).
- Every Meta page in devices.md is marked P; I could read them only through the fetch tool's digest, as gestures.md
  already marks its own Meta pages ("P, digest"). For consistency devices.md M1 to M12 should carry "P, digest";
  every Meta fact I checked matched the digest, so no fact changes.
- Claims I could not check stay at the level the notes gave them, none of which is used by code: UploadVR depth
  (S), Web Launch (S), A-Frame thresholds, MRTK3 interactor page, Meta ISDK interactor pages, Resolve, Unity Reflect
  (U), Workshop XR FAQ (U), the five BIM-in-VR studies, Mutasim, Jacob, Kostic, Stoakley, Jansen, prices.

## 6. Verdict on the facts code will use

Everything code would rely on from devices.md is confirmed: the WebXR session and input API surface in three.js
0.186.1 and in the app's bundle, the pinch thresholds, the CDN defaults to avoid, the generic-hand assets and their
licence, Quest's select-on-pinch and reserved palm pinch, Vision Pro's transient pointer at indices 2 and 3 with
pose-only hands, Android XR's hand input, Chromium's runtime flags. From gestures.md, the MRTK3 two-hand maths and
palm-up defaults, Microsoft's sizes and Apple's spacing are confirmed. From bim-xr.md, every renderer and model
claim is confirmed except the `o.pos` count (38 files), with the IFC level caveats in section 3. The corrections that
change a decision are the Nacenta figures (weaker support for learnable designed gesture sets, so H6 leans further
toward few gestures plus menus), the scope of "BIM viewers explode by level" (samples, not product features), and
the chunk rebuild per frame during a gesture (to measure).
