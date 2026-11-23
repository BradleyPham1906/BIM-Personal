# Independent check of the four device and XR topic notes (protocol step 9)

The second reading that `docs/research/research-protocol.md` step 9 asks for, of the four topic notes in this
folder (`web-on-iphone.md`, `hands-and-physics.md`, `native-paths.md`, `splats-and-link.md`), written for
`docs/research/research-devices-xr.md`. The reader is a separate research agent that wrote none of the notes. Every
source below was opened again on 2026-11-23 and read at the cited place. The notes' own paraphrases were not relied
on. Downloads went into the session scratchpad and were read as text. No third-party code was run. The only code
run was this repository's own `splat_cost.js`, under Node.

How sources were read. "curl" means the raw page or file was fetched and searched as text, which counts as P.
"digest" means the fetch tool's model summary quoted the page. The protocol treats that as S for wording unless the
quoted sentence is exact and short. Where a number matters, it was read from the raw text wherever that was possible.

Verdicts: **confirmed**, **corrected** (the correction follows), or **could not check**. A fact that fails goes back
to U, as step 9 requires.

## 1. web-on-iphone.md

**F1.1, WebXR is not compiled for iOS.** Read: `Source/WTF/wtf/PlatformEnableCocoa.h` on WebKit `main` (curl),
lines 1090 to 1100: `ENABLE_WEBXR 1` only if `PLATFORM(VISION) || (PLATFORM(MAC) && HAVE(COMPOSITOR_SERVICES))`;
`ENABLE_WEBXR_AR` on `PLATFORM(IOS)` is set equal to `ENABLE_WEBXR`; `ENABLE_WEBXR_HANDS` is visionOS or Mac with the
internal SDK. Also checked whether a build setting defines it elsewhere: `Configurations/FeatureDefines.xcconfig`
does not mention WebXR, and `Source/cmake/WebKitFeatures.cmake` defaults `ENABLE_WEBXR` to OFF. **Confirmed.**

**F1.2, MDN has no WebXR for Safari iOS.** Read: `api/XRSystem.json` on browser-compat-data `main` (curl): Safari
`version_added: false`, `safari_ios` "mirror". **Confirmed.**

**F1.3, Apple's notes add WebXR only for visionOS.** Read: Safari 18 release notes JSON (curl), "Added support for
immersive WebXR in visionOS. (125631316)"; Safari 27 release notes JSON: WebXR items are Layers and viewport fixes
only. **Confirmed.**

**F1.4, WebKit bug 208988.** Read: https://bugs.webkit.org/show_bug.cgi?id=208988 (curl). Comment 16 (2022-08-24):
flags on an iPhone 12 Pro, 15.6.1, no WebXR. Comment 18 (2023-05-27): all WebXR flags on iOS 16.4, samples failed to
detect WebXR. Comment 46 (Sergio Villar Senin, 2026-04-01): "Apple has already shipped WebXR support for VisionOS and
WPE and WebKit GTK ...". Status RESOLVED FIXED. The words "nothing related to iOS" come from another commenter quoting
an earlier remark about Linux work. They were not part of the closing comment. The comments run 0 to 46, so there
are 47, not 46. **Confirmed**, with that wording nuance.

**F2.1, permission API since iOS 13; MDN says 14.5.** Read: Safari 13 release notes JSON (curl), "Added a permission
API on iOS for DeviceMotionEvent and DeviceOrientationEvent". Also read MDN `api/DeviceOrientationEvent.json`,
`requestPermission_static`, `safari_ios` 14.5. **Confirmed**, both, and the disagreement is recorded correctly.

**F2.2, a user gesture is needed to prompt.** Read: `Source/WebCore/dom/DeviceOrientationAndMotionAccessController.cpp`
line 90 (curl), `bool mayPrompt = UserGestureIndicator::processingUserGesture(&document)`. Also read
`WebDeviceOrientationAndMotionAccessController.cpp` line 55, which returns the cached state when
`currentPermission != Prompt || !mayPrompt`. **Confirmed.** Bug 269706 was not re-read, so the worker round trip
rests on the note alone (S).

**F2.3, secure context only; the 26.4 fix.** Read: `DeviceOrientationEvent.idl` (curl), `SecureContext`. Safari 26.4
notes JSON: "Fixed DeviceMotionEvent and DeviceOrientationEvent interfaces so that they only show up in secure
contexts". **Confirmed.**

**F2.4, the decision is cached per top-level origin in memory.** Read: same controller, lines 53 to 100,
`m_deviceOrientationPermissionDecisions` keyed by the main frame's `documentSecurityOriginData`, set true or false.
**Confirmed.** The inference that a Home Screen app is asked again at each cold launch stays U, correctly marked.

**F2.5, relative angles, 1/60 s, compass heading.** Read: `WebCoreMotionManager.mm`, `kMotionUpdateInterval = 1.0f /
60.0f` (line 34), `startDeviceMotionUpdates` with no reference frame (line 174), an `NSTimer` at that interval
(line 182), `newHeading.magneticHeading` (line 318). The IDL gives `webkitCompassHeading` and `webkitCompassAccuracy`
only under `WTF_PLATFORM_IOS_FAMILY`, and `absolute` only in the non-iOS branch. **Confirmed.**

**F3.1, getUserMedia in Home Screen apps from 13.4.** Read: bug 185448 (curl), RESOLVED FIXED. Comment 84 (Luming
Yin, Apple, 2020-02-05): "With today's iOS and iPadOS 13.4 Beta, WebRTC (getUserMedia) should work as expected in
home screen web apps". **Confirmed.**

**F3.2, the camera permission is asked again on every launch.** Read: bug 215884 and bug 327237 (curl).
**Corrected**, in three points:

- 215884 is RESOLVED CONFIGURATION, not open. Comment 21 confirms the 14.5 improvement. Comment 29 (2025-06-25)
  reports the problem again on 18.5. In comment 31 (2026-02-03) a WebKit engineer, youenn fablet, says persistence
  across launches is a different request from the hash bug and asks for a new bug.
- 327237 is a single reporter's bug: NEW, one comment (the Radar importer), no WebKit engineer has confirmed it. Its
  only tested environment is "iPhone 14, iOS 26.6.2". The "iOS 26 or iOS 27" field is template text. Its "OTHER
  RESULTS" lines are unfilled placeholders such as "[result]".
- So the per-launch re-prompt is supported by several users' reports (215884 comments 28 and 29, and 327237) on
  iOS 18.5 and 26.6.2. It has not been confirmed by WebKit and has not been reported on iOS 27. Level S, medium
  confidence. The plan should still assume it, and measurement M4 decides.

**F3.4, texImage2D cost, bug 226830.** Read: bug 226830 (curl). **Corrected:**

- The iOS 15.0 figure is from an iPhone 12 Pro Max, not an iPhone 12 Pro.
- The bug contradicts itself on that figure: the prose says 2.503 ms, the table says 4.297 ms.
- The rest is as the note says: 6.904 ms on an iPhone 12 Pro with iOS 14.4.2; 4.454 and 2.963 ms with
  `UNPACK_PREMULTIPLY_ALPHA_WEBGL`; 0.407 ms on a Galaxy S10.
- Corrected wording: "about 2.5 to 7 ms per upload on iPhone 12 Pro and Pro Max, iOS 14 to 15".

**F4.1, no element fullscreen on iPhone.** Read: MDN `api/Element.json` `requestFullscreen` (curl), `safari_ios`
16.4 and prefixed 12, both noted "Only available on iPad, not on iPhone." Safari 16.4 notes: "Added support for the
unprefixed Fullscreen API on macOS and iPadOS." Bug 206854: NEW, 15 comments, the last on 2026-10-24. Bug 212934:
RESOLVED WONTFIX, comment 3 (Marcos Caceres, 2026-01-25) closes it in favour of 206854. Bug 310661: RESOLVED
DUPLICATE of 206854, reported 2026-03-24 on iOS 26. Safari 26 and 27 notes: fullscreen fixes only, none for
iPhone. **Confirmed.**

**F4.2, every site added to the Home Screen opens as a web app from iOS 26.** Read: WebKit's WWDC25 post (curl):
"By default, every website added to the Home Screen opens as a web app." Safari 26 release notes JSON, Web Apps:
"Added support for any website to become a web app on iOS or iPadOS. (113034903)". App code: `tools/build_pwa.py`
line 123 has `'display': 'standalone'`, and `src/index.html` line 5 has `viewport-fit=cover`. **Confirmed.**

**F4.3, Wake Lock in Home Screen apps from 18.4.** Read: Safari 18.4 notes JSON: "Fixed Wake Lock API for Home Screen
Web Apps. (108573133)". Bug 254545: RESOLVED FIXED; comment 10 has the ViewServices sentence; comment 65 (Jen
Simmons, 2025-03-31) says it shipped in 18.4. MDN `api/WakeLock.json`: `safari_ios` 18.4, and 16.4 to 18.4 partial
("Does not work in standalone Home Screen Web Apps"). Counter-evidence found and resolved: comment 69 (2025-12-04)
reported a regression on iOS 26.1, and comment 70 withdrew it ("the issue was with our browser detection library").
**Confirmed.**

**F5.1, StereoCamera in the app's three.js.** Read: `runtime/three/0.186.1/bim-three.min.js` contains
`StereoCamera` (2 matches) and no `StereoEffect`. **Confirmed.**

**F5.2, Cardboard SDK licence and its third_party exception.** Read: `LICENSE` of googlevr/cardboard on `master`
(curl). The first block puts "All files in the following folders: - third_party/unity_plugin_api/" under the Unity
Companion License. That licence allows use only with a Unity engine licence and forbids competing products. Then
"Except as indicated above in this LICENSE file files in this SDK are licensed as follows", followed by Apache-2.0.
Also read `proto/cardboard_device.proto`: fields 3, 4, 5 (packed), 6, 7 (packed), 11 (default BOTTOM), 12 (default
MAGNET). **Confirmed.**

**F5.3, the Cardboard v1 profile numbers.** The bytes in `sdk/qrcode/cardboard_v1/cardboard_v1.cc` (curl) were
decoded here with a decoder of our own, written apart from the note's. Result: vendor "Google, Inc.", model
"Cardboard v1", screen-to-lens 0.042, inter-lens 0.06, FOV [40, 40, 40, 40], tray-to-lens 0.035, K [0.441, 0.156],
vertical alignment 0 (BOTTOM), button 1 (MAGNET). Also read `cardboard-vr-display` 1.0.19 `src/device-info.js` (npm
tarball): CardboardV1 has the same values. CardboardV2 has fov 60, inter-lens 0.064, baseline 0.035, screen-to-lens
0.039, K [0.34, 0.55]. **Confirmed.**

**F5.5, the iPhone 13 screen and the lens offset.** Read: https://support.apple.com/en-us/111872 (curl):
"2532-by-1170-pixel resolution at 460 ppi"; a three-axis gyro, an accelerometer, a magnetometer and a digital
compass. Arithmetic redone:

- 2532 / 460 x 25.4 = 139.81 mm and 1170 / 460 x 25.4 = 64.60 mm, so each half is 69.90 mm wide.
- The half centre lies 34.95 mm from the middle. With lenses 60 mm apart (v1) the offset is 4.95 mm; with 64 mm
  (v2) it is 2.95 mm.
- 844 x 390 CSS px at device pixel ratio 3.

**Confirmed.** One caveat the note does not state: the 460 ppi width is the full panel, while the visible area has
rounded corners and the notch. The offset holds only if the phone is centred in the tray (the viewer's
`vertical_alignment` and the user's placement). Measurement M7 covers it.

**F6.1, A-Frame 1.8.0 throws without WebXR.** Read: npm tarball `aframe@1.8.0` (published 2026-06-23),
`src/core/scene/a-scene.js` line 346: `throw new Error('Failed to enter ' + mode + ' no WebXR')`. **Confirmed.**

**F6.2, the polyfills.** `cardboard-vr-display` 1.0.19 (2022-04-12), `webxr-polyfill` 2.0.3 (2022-05-24) and
`webvr-polyfill` 0.10.12 (2022-06-29), from npm metadata. `src/base.js` line 386 says "*sigh* Just fake it." No
`requestPermission` in `cardboard-vr-display/src`. **Confirmed.**

**F6, the iPhone 13 on iOS 27 (search log 17).** Apple's own page could not be found by search either. The press
(MacRumors 2026-06-08 and 2026-09-14, AppleInsider, TechRadar, EveryMac) agrees on "iPhone 11 and later".
**Could not check at Apple**; stays S, as the note says.

Not re-checked (low stakes, or not used by code): bugs 252465, 230617, 235845, 206636, 269706, 271891, 301294; the
W3C `index.bs` steps; Kuula.

## 2. hands-and-physics.md

**Tasks Vision 1.2.3: version, licence and files.** Read: the npm registry (dist-tags: `latest` 1.2.3,
`nightly` 1.3.0-rc.20261122; 1.2.3 published 2026-11-11T22:49Z) and the tarball:

- `package.json` licence Apache-2.0, and no LICENSE file in the package.
- `wasm/vision_wasm_internal.wasm` is 14,665,716 B, and 4,147,452 B under `gzip -9`.
- The loader `.js` is 336,624 B and `vision_bundle.mjs` is 155,990 B.
- The only other wasm is the `vision_wasm_module_internal` twin. No non-SIMD build ships.

**Confirmed.**

**The model, its size and licence.** Read: a HEAD request to the storage.googleapis.com `.task` URL:
content-length 7,819,105 B, last-modified 2023-04-26. Read the LiteRT community card's raw README: `license:
apache-2.0`; "Every model binary in this repository is byte-identical ... to the official artifact served by
Google"; Pixel 6 full bundle 17.12 ms CPU and 12.27 ms GPU. Then the card's bundled Google PDF, "Model Card Hand
Tracking (Lite_Full) with Fairness Oct 2021" (SHA-256 `43127ff8...ab76b`, matching the card), was downloaded and run
through pdftotext. It says "LICENSED UNDER ... Apache License, Version 2.0" and that the error "gets larger toward
the fingertip". **Confirmed, and raised from S to P.** The PDF is now read. It is Google's document, though served
from Hugging Face's copy.

**No SharedArrayBuffer or isolation needed.** Read: the wasm memory section, with our own header reader: flags 1,
not shared. There are no imports of shared memory. The strings `SharedArrayBuffer` and `crossOriginIsolated` occur 0
times in the bundle and 0 times in the loader. **Confirmed.**

**SIMD only, so iOS 16.4 or later.** Read: #6139 (digest). The maintainer wrote on 2026-11-17: "Note that 1.2.3 ships
only the SIMD WASM build, so it needs iOS 16.4 or later". The reporter's error is "invalid opcode 253". WebKit's
Safari 16.4 post (curl): "In WebAssembly, we've added support for 128-bit SIMD." **Confirmed** (issue wording S, the
WebKit post P).

**GPU in a worker needs Safari 17.** Read: `vision_bundle.mjs`, function `Oh`. It returns true when `OffscreenCanvas`
exists and the UA is either not Safari, or matches `Version/(\d+).*Safari` with a version of 17 or more. WebKit's
Safari 16.4 post: "Offscreen Canvas support for 2D operations. Support for 3D in Offscreen Canvas is in
development." WebKit's Safari 17.0 post: "adds support for WebGL in Offscreen Canvas" on iOS 17. MDN
`OffscreenCanvas.getContext` agrees: webgl and webgl2 from 17, webgpu from 26. **Confirmed.**

There is an edge the note misses (U, our reading of the code). A Home Screen web app's or a WKWebView's user agent
may lack the "Safari" token. The check then passes on `OffscreenCanvas` existing alone, which on iOS 16.4 to 16.x
means 2D-only OffscreenCanvas. It does not matter if the app requires iOS 17, as the note recommends.

**#6142, the maintainers' iOS retest.** Read: #6142 (digest): Image Segmenter (selfie multiclass), GPU delegate,
retested on an iPhone 12 with Safari 26.5; "the GPU mask matches the CPU mask on 99.4% of pixels"; closed as
completed on 2026-11-17. **Confirmed** (S).

**The cited old iPhone frame rates.** Read: TensorFlow blog, 2021-11, "3D Hand Pose" (curl), the browser table, two
hands. On the iPhone 11: MediaPipe WASM and GPU 8 fps (lite) and 5 fps (full); TF.js WebGL 15 and 12 fps.
**Confirmed.** Also read Zhang et al. 2020, Table 3 (ar5iv, curl): the full landmark model takes 5.3 ms on an iPhone
11 and 16.1 ms on a Pixel 3. That is the landmark model alone, without the palm detector. **Confirmed.** #3303
(6 to 7 fps on an iPhone 13 Pro) was not re-read and stays S.

**Jolt in runtime/jolt and its single-thread build.** Read: `runtime/MANIFEST.json`:

- `jolt/1.1.1/bim-jolt.min.js` is 4,011,306 B, SHA-256 `0a35863a...9a31fd` (recomputed here: it matches), "from npm
  jolt-physics@1.1.1 ... dist/jolt-physics.wasm-compat.js bundled unchanged by esbuild"; licence MIT; the version
  pin `"jolt": "1.1.1"`.
- `src/js/engine/walk/walk-physics.js` line 2 is the adapter to Jolt 1.1.1, and `walk-mode.js` line 34 loads
  `jolt/1.1.1/bim-jolt.min.js`.
- The vendored file contains `MoveKinematic` (8 matches), `EMotionQuality_LinearCast` (2), `SixDOFConstraintSettings`
  (64), `SpringSettings` (54) and `SharedArrayBuffer` (0). It is 951,174 B under `gzip -9`.
- In npm `jolt-physics@1.1.2`, `wasm-compat.js` is 3,235,858 B, 912,077 B gzipped, with no SharedArrayBuffer.
- Jolt's `MotionQuality.h`: "Body will tunnel through thin objects if its velocity is high enough", and `LinearCast`.

**Confirmed.** The note's correction of the parent note ("No rigid-body engine", `research-devices-xr.md` line 74) is
right.

**Rapier licence.** Read: npm `@dimforge/rapier3d-compat@0.21.0`, licence Apache-2.0; `@dimforge/rapier3d` modified
2026-09-25. **Confirmed.**

**ammo.js is zlib.** Read: `kripken/ammo.js` `LICENSE` on `main` and the npm 0.0.10 tarball `LICENSE`: "Copyright (c)
2011 ammo.js contributors. This software is provided 'as-is' ..." That is the zlib text. The npm metadata has no
licence field. **Confirmed.**

One interpretive point for the owner: the library rule lists "MIT, BSD, ISC, Apache-2.0, MPL-2.0, or LGPL". zlib is
a permissive licence compatible with an Apache-2.0 repository, so "outside the rule" is a literal reading of the
list. It is not an incompatibility. It does not change the recommendation, since Jolt is chosen.

**cannon-es has no CCD.** Read: npm `cannon-es@0.20.0` (MIT), `dist/cannon-es.js`: 0 matches for "ccd" or
"continuous". **Confirmed.**

**One Euro filter.** Read: https://gery.casiez.net/1euro/ (curl): "Casiez, G., Roussel, N. and Vogel, D. (2012) ...
CHI '12 ... pp. 2527-2530", and the tuning procedure. Read the reference `python/OneEuroFilter/OneEuroFilter.py` on
`main` (curl): it is "BSD License", and `python/LICENSE` says "Copyright 2023 Inria". The code computes
`dx = (x - prev_x) * freq` from the last filtered value, `alpha = 1/(1 + tau/te)` and `cutoff = mincutoff +
beta*|edx|`, with defaults mincutoff 1.0, beta 0.0 and dcutoff 1.0. `groundTruth.csv` is at the repository root,
not under `python/`. **Confirmed.** The page lists the JavaScript implementation as BSD. The page was read in full
as text, so the note's S for the page can be P.

**Pinch thresholds.**

- MRTK2 `ArticulatedHandDefinition.cs` (curl): enter 0.02 and exit 0.05, both settable between 0.015 and 0.1.
- MRTK2 `HandPoseUtils.cs`: `IndexThumbSqrMagnitudeThreshold = 0.0016f` and `Clamp(1 - d^2/0.0016)`.
- Ultraleap `PinchDetector.cs` (sparse clone): `activateDistance = 0.025f`, `deactivateDistance = 0.03f`, "Utilizes
  hysteresis".
- three.js r180 `OculusHandPointerModel.js`: `PINCH_THRESHOLD = 0.02`, `pinched = distance <= PINCH_THRESHOLD`.

**Confirmed**, with one small correction. In three.js the display scale `pinchScale` runs from `PINCH_MIN` 0.01 to
`PINCH_MAX` 0.05, while `focusScale` runs from 0.01 to 0.02. The note's "0.01 to 0.05" is right for the first and
leaves out the second. Nothing depends on it.

**The 1.5 cm at 75 cm study.** Read: Reimer, Podkosova, Scherzer and Kaufmann, Frontiers in VR 2023 (digest, two
reads). The abstract says "median errors below 1.75 cm at distances below 75 cm" and "a median error of 4.7 cm at
the distance of 2.75 m". Section 4.2.2 says "MediaPipeHand delivered a lower error of 1.53 cm than Oculus Quest with
a distance of 75 cm". It also gives "a maximum error of 4.47 cm at a distance of 250 cm". The "initial error of
28.48 cm" is MediaPipeInternal, the model's own hand size; its distance is not stated, and the context suggests
250 cm. The camera was a 1080p webcam with a 60 degree horizontal field of view. **Confirmed, with corrections:**

- The paper does not label 1.53 cm as a median. It is probably one, from the method, but that is an inference.
- The note's "28.48 cm at 2.5 m" is likely, not stated.
- The level should be S, not P. Both the note and this check read it through the fetch tool's digest. The
  supplementary tables were not read.

**Ultraleap Physical Hands licence and method.** Read: a sparse clone of `ultraleap/UnityPlugin` (`main`):

- `LICENSE.md` is Apache-2.0.
- `SoftContactBone.cs`: `DEAD_ZONE = 0.0005F` with "to avoid tiny vibrations", `targetVelocity = delta /
  Time.fixedDeltaTime`, and `softContactDislocationDistance = 0.03F` used with `IsGrabbing`.
- `SoftContactHand.cs`: `CollisionDetectionMode.Continuous` and `Physics.IgnoreCollision` between the hand's bones.
- `SoftContactParent.cs`: dynamic and static friction 1.
- `HardContactParent.cs`: `teleportDistance = 0.1f`, `boneMass = 0.1f`, `boneStiffness = 100f`,
  `grabbedBoneStiffness = 10f`, `boneDamping = 1f`, `handSolverIterations = 30` and
  `handSolverVelocityIterations = 20`.
- `HardContactHand.cs`: teleport beyond `teleportDistance`, then "Ghosted".

**Confirmed.** One precision: teleport-and-ghost belongs to the hard-contact hand. The soft-contact hand switches off
its collisions instead (above 0.03 m, or while grabbing). The note's recommended parameters mix the two, which is a
reasonable design choice, but it should say so.

**Thermal (UL stability 74 to 78 %).** Not re-read. It stays S, as marked.

## 3. native-paths.md

**F1, the free provisioning limits.** Read: https://developer.apple.com/support/compare-memberships/ (curl): "You
can register up to 10 App IDs, which expire after 7 days. You can register up to 3 devices, which expire after 7
days. You can install up to 3 apps per device. Provisioning profiles that enable apps to be installed on a device
will expire 7 days from issuance." **Confirmed.**

**F3, the capability list.** Read: https://developer.apple.com/help/account/reference/supported-capabilities-ios
(curl). The table was parsed here independently, with columns ADP, ADEP and Apple Developer. The free column has
exactly: App groups, Background modes, Data protection, HealthKit, HomeKit, Inter-App Audio, Keychain sharing, Maps
and Wireless Accessory Configuration. Paid only: Increased Debugging Memory Limit, Extended Virtual Addressing, the
three iCloud rows, Push notifications, Associated domains, Sign in with Apple and Game Center. There are no Camera or
ARKit rows. **Confirmed.**

One row the note does not mention: "Head Pose" is paid only. It is the headphone motion entitlement, not ARKit, so it
does not affect the inference. The inference that ARKit and the camera work under a Personal Team stays medium-high
until the first build, as the note says.

**F5, Xcode 27 needs macOS Tahoe, and its Mac models.** Read: https://developer.apple.com/support/xcode/ (curl, table
parsed):

| Xcode | macOS | Device support |
|---|---|---|
| 27, 27.1, 27.2, 27.3 beta 2 | Tahoe 26.6 or later | iOS 17 or later |
| 26.4.1 to 26.6 | Tahoe 26.2 to 26.x | iOS 15 or later |
| 26 to 26.3 | Sequoia 15.6 to Tahoe 26.x | iOS 15 or later |
| 16.4 | Sequoia 15.3 to Tahoe 26.1.x | iOS 15 or later |

The table's deployment targets are iOS 15 to 27.

Also read the Tahoe page (https://support.apple.com/en-us/122867, curl): every MacBook Air from M1 (2020) to M5, and
no Intel Air. The Sequoia page (https://support.apple.com/en-us/120282, curl) has the same list plus "MacBook Air
(Retina, 13-inch, 2020)".

**Confirmed.** The note's reading that "Device support" means "runs apps on" is right for running from Xcode. The
separate deployment target is iOS 15 or later.

**F15, Capacitor 8 needs Xcode 26.** Read: https://capacitorjs.com/docs/ios (curl): "iOS 15+ is supported. Xcode
26.0+ is required ... Capacitor uses WKWebView". npm `@capacitor/core` latest 8.6.2, MIT. **Confirmed.** The support
policy page served no readable table to curl (rendered by script), so the v7 and Xcode 16.0 row is **could not
check** here and rests on the note (S).

**F11, VNDetectHumanHandPoseRequest is 2D.** Read: Apple's documentation JSON:

- `vision/vndetecthumanhandposerequest`: iOS 14.0.
- `vision/vnrecognizedpoint`: "a normalized point in an image, along with an identifier label and a confidence
  value".
- `vision/vndetecthumanhandpose3drequest`: 404.
- `vision/vndetecthumanbodypose3drequest`: iOS 17.0, "points on human bodies in 3D space".

**Confirmed.**

**F13, ARKit hand tracking only on visionOS.** Read: `arkit/handtrackingprovider` JSON: platforms visionOS 1.0 only.
In GodotApplePlugins, `Sources/GodotARKit/ARHandTracking.swift` line 10 is `#if canImport(ARKit) && os(visionOS)`
(shallow clone). No Swift file imports Vision. **Confirmed.**

**F22, GDMP exists and is MIT.** Read: `git ls-remote`: HEAD 31a54ab, tags up to v0.6. `LICENSE`: "MIT License,
Copyright (c) 2021-present Jason Kuo & contributors". **Confirmed** for existence and licence. The iOS hand claim
(nothing shows it tested on iOS) was not re-tested. It is a negative finding and stays low confidence, as the note
says.

**F23, GodotApplePlugins.** Read: tags up to v1.11.0; last commit 2026-10-28 (clone); `LICENSE` "Copyright (c) 2025
Miguel de Icaza", MIT text. **Confirmed.**

**F21, Godot MobileVRInterface status.** Read: `godot-docs` `tutorials/xr/mobilevr_intro.rst` (curl): "a bare bones
implementation that outputs a side by side stereoscopic image. It supports basic 3DOF tracking"; "This
implementation is not actively maintained ... mostly used for diagnostic purposes." **Confirmed.**

**F6, iOS 27 on the iPhone 13.** As in section 1: **could not check at Apple**; S.

Not re-checked: Developer Mode, `NSCameraUsageDescription`, F8 to F10's ARKit pages other than
`ARWorldTrackingConfiguration` (iOS 11.0, confirmed), Capacitor's bridge code, Mozilla WebXR Viewer, RealityKit and
SceneKit pages, and GLTFKit2.

## 4. splats-and-link.md

**Spark 2.4.0: licence and editing features.** Read: npm metadata (licence MIT, peer `three >= 0.180.0`, modified
2026-10-20) and the tarball:

- `LICENSE`: "The MIT License, Copyright 2025 WORLD LABS TECHNOLOGIES, INC."
- `dist/types/SplatEdit.d.ts`: `SplatEditSdfType` is all, plane, sphere, box, ellipsoid, cylinder, capsule and
  infinite_cone.
- `SparkRenderer.d.ts` has `depthTest` and `depthWrite` options (lines 300 and 307).
- `spark.module.js`: 0 matches for `SharedArrayBuffer`.
- `spark.module.min.js` is 2,852,378 B, and 980,771 B under `gzip -9`. The note says 983 kB, which is within the
  difference between gzip settings.
- https://sparkjs.dev/docs/performance/ (curl): "iPhone: 1-3 million splats".

**Confirmed.**

**SuperSplat is WebGPU only.** Read: `playcanvas/supersplat` on `main` (curl):

- `src/main.ts` line 134: `deviceTypes: ['webgpu']`.
- `src/index.ts` lines 17 to 27: "SuperSplat requires WebGPU, which this browser does not support".
- `package.json`: version 3.9.2, MIT, playcanvas 2.24.1.

**Confirmed.**

**KHR_gaussian_splatting is ratified.** Read: `extensions/2.0/Khronos/KHR_gaussian_splatting/README.md` on `main`
(curl), "## Status: Complete, Ratified by the Khronos Group". `sortingMethod` defaults to `cameraDistance`: "sorts
the splats based on the length of the vector from the splat to the camera origin". It is listed in
`extensions/README.md`. **Confirmed.**

**The SPZ extension's status.** Read: `KHR_gaussian_splatting_compression_spz_2/README.md` answers 404. A tree
listing of `extensions/2.0/Khronos/` on `main` (blobless clone, head 2026-11-20) has only `KHR_gaussian_splatting`
matching "gauss" or "spz". No branch name on the remote matches "spz" or "gauss". **Confirmed** as absent from
`main`. Its "draft" status stays U, as the note says.

**ZSTD is not decodable by browsers.** Read: MDN `api/DecompressionStream.json`: `zstd` false in Safari and Chrome;
gzip, deflate and deflate-raw from Safari 16.4. **Confirmed.**

**RFC 8829 signalling.** Read: https://www.rfc-editor.org/rfc/rfc8829.txt, section 3.1: "JSEP does not specify a
particular signaling model or state machine". Line 195: "preferred signaling mechanism (e.g., ...". **Confirmed for
the text, corrected for the reference.** The RFC Editor's record (`rfc8829.json`) gives `obsoleted_by: RFC9429`.
RFC 9429 (Standards Track) "obsoletes RFC 8829" and keeps both sentences: section 3.1 at line 312, and line 197.
Cite RFC 9429 as the current JSEP. The finding is unchanged.

**mDNS candidates.** Read: `draft-ietf-mmusic-mdns-ice-candidates-03` (curl): "Expires: 8 June 2022", Apple and
Google authors. Also bug 189503 (curl), comment 4 (youenn fablet, 2019-01-14): "We recently enabled MDNS ICE
candidates by default in WebKit ToT. This should enable Safari <-> Safari connections in networks supporting MDNS."
The note leaves out one detail from comment 1 (2018-09-13): WebKit discloses host candidates to JavaScript only after
getUserMedia, or as mDNS names. So on the owner's phone the candidate will be an mDNS name unless the camera is
already open, which the hand-tracking mode does. **Confirmed.** The added detail goes on the phone test list (U until
seen).

**Cloudflare STUN terms.** Read: https://developers.cloudflare.com/realtime/turn/faq/index.md (curl), line 23:
"Cloudflare's STUN service at `stun.cloudflare.com` is free and unlimited." **Confirmed.** The TURN price was not
re-read.

**Web Bluetooth is not in Safari.** Read: MDN `api/Bluetooth.json`, Safari `version_added: false`, iOS "mirror".
WebKit `standards-positions` `summary.json`: Web Bluetooth "oppose" (issue 570). **Confirmed.**

**BarcodeDetector.** Read: MDN `api/BarcodeDetector.json`: Safari 17 behind the "Shape Detection API" preference,
iOS "mirror"; Chrome 88 partial, "Supported on ChromeOS and macOS only". **Confirmed.**

**Meta's 20 ms motion-to-photon figure.** Read: https://developers.meta.com/vr/resources/bp-rendering/ (digest): "We
believe the threshold for compelling VR to be at or below 20ms of latency"; "If latency is unavoidable, it will be
more uncomfortable the more variable it is." **Confirmed.** The page says "latency" in the context of motion to
photon. Since both the note's read and this one went through the fetch tool's digest, the level is S, not P.

### The two experiments, run again

**E2 (`docs/research/experiments/devices-xr/splat_cost.js`)**, run here under Node v22.23.5 on an Intel Xeon at
2.10 GHz (4 CPUs), one run of the script (each line is a median of 5):

| Operation | Note (median) | This check (median, min, max) |
|---|---|---|
| 16-bit counting sort | 24.5 ms | 18.3 ms (17.4, 30.7) |
| `Array.prototype.sort` | 595 ms | 589.4 ms (539.5, 626.5) |
| Box selection | 10.9 ms | 11.5 ms (10.7, 13.5) |
| Sphere selection | 6.9 ms | 7.2 ms (6.9, 8.9) |
| Colour match | 9.5 ms | 11.3 ms (9.3, 12.6) |
| Grid build (0.25 m) | 22.9 ms | 23.1 ms (22.8, 23.8) |
| Grow, worst case, all 1,000,000 reached, 0.5 m | 2,200 ms | **not reproducible**: the committed script grows with a 0.25 m radius on random colours, reaches 1 splat, and takes 0.0 ms |

The first six rows are **confirmed** within run-to-run noise. The comparison sort is about 32 times the counting sort
here, against the note's "about 25 times". Either way the conclusion holds: the per-frame sort must be a counting or
radix sort.

The grow row is **corrected to U**. The committed script cannot produce it: there is no 0.5 m radius, no forced
worst case, and no 3-run variant. Whatever produced 2.2 s is not in the repository. Either the script that made it is
committed, or the row is removed. The note's conclusion that growing must be bounded and run in a worker is still
sound as reasoning. Its number is unbacked.

The note's part 6 heading says the scripts were "kept in the session scratchpad, not committed". Both scripts are in
`docs/research/experiments/devices-xr/`, so the heading is out of date. The committed `splat_cost.js` also differs
from what the table describes, so it is probably the earlier or a different version.

**E1 (`sdp.html`)** was read, not run, as the brief allows. It makes an offer with one data channel
(`ordered:false, maxRetransmits:0`) and no ICE servers, waits for gathering (3 s cap), and compresses with
`CompressionStream('deflate-raw')`. It reports base64 length as `ceil(compressed / 3) * 4`. 428 B gives 572
characters, which matches the note's arithmetic. The page masks the last octet of IPv4 addresses, and it counts
candidates. Nothing in it contradicts the note's 587 and 586 B of SDP and 428 B compressed. The numbers themselves
were not re-measured: **could not check** (S, the author's run).

## 5. Contradictions between the four notes

1. **The Jolt download.** `hands-and-physics.md` says "0.95 MB gzipped" in section 3 and H5, but its engine table
   gives `wasm-compat` as "0.91 MB gz". Both are right for different files: the app's esbuild bundle of 1.1.1 is
   951,174 B, and npm 1.1.2's raw `wasm-compat.js` is 912,077 B. The note should name the file each time.
2. **MediaPipe's licence.** `native-paths.md` F14 and its table give MediaPipe's Apache-2.0 as S ("not re-read
   today"). `hands-and-physics.md` read it P, and this check read the model card PDF too. Raise native-paths to P by
   reference.
3. **The iPhone 13 on iOS 27.** `web-on-iphone.md` cites MacRumors, AppleInsider, 9to5Mac and EveryMac.
   `native-paths.md` cites MacRumors, TechRadar and EveryMac. Same finding, both S, consistent. Neither has
   Apple's page.
4. **WebGPU on iOS 26.** `splats-and-link.md` and `native-paths.md` F17 agree. MDN's `OffscreenCanvas` data, read
   here, also gives webgpu from Safari 26.
5. **The minimum iOS for hand mode.** `hands-and-physics.md` sets it at 17 (GPU in a worker), while `web-on-iphone.md`
   assumes 26 or 27. They do not conflict: 17 is the floor and 26 or 27 the expectation. The main note should state
   one floor.
6. **The physics hand's teleport and ghost.** `hands-and-physics.md` describes Ultraleap's soft-contact velocity drive
   and hard-contact teleport-and-ghost as one method in its recommendation. In the source they are two different
   hands (section 2 above). This is internal to one note, not across notes.
7. **The experiments' status.** `splats-and-link.md` says its scripts were not committed, but they are, and E2's
   table does not match the committed script (section 4).

No contradiction was found between the notes on WebXR, fullscreen, camera, orientation or the Cardboard numbers.

## 6. Level changes

Raised:

- **Hand landmarker model licence** (`hands-and-physics.md`): S to P (Google's PDF card read).
- **One Euro page** (`hands-and-physics.md`): S to P (read in full as text).
- **MediaPipe licence** (`native-paths.md` F14, table): S to P, by the reading in `hands-and-physics.md` and here.

Lowered:

- **Reimer et al. figures** (`hands-and-physics.md` 4.3): P to S. Read only through the fetch tool's digest. The
  1.53 cm is not labelled as a median, and the 28.48 cm distance is inferred.
- **Meta 20 ms** (`splats-and-link.md` B3): P to S, digest only. The fact is confirmed.
- **WebKit Safari 16.4 and 17.0 posts** (`hands-and-physics.md`): the note marked them "P (fetch digest)". They were
  read here as raw text, so P now holds. The note's own basis was S.
- **Bug 327237's per-launch re-prompt** (`web-on-iphone.md` F3.2): P (high) to S (medium). It is one unconfirmed
  user report on iOS 26.6.2 with placeholder results, plus user comments on 215884. It is not WebKit's statement,
  and not seen on iOS 27.
- **The grow-by-colour worst case, 2,200 ms** (`splats-and-link.md` E2): measured to U. Not reproducible from the
  committed script.
- **The Capacitor v7 and Xcode 16.0 row** (`native-paths.md` F15): P to S. The support policy page was unreadable to
  curl here.

Corrected without a level change:

- **The bug 226830 device** (`web-on-iphone.md` F3.4): the iOS 15.0 figure is from an iPhone 12 Pro Max, and the
  bug itself gives 2.503 ms in its prose and 4.297 ms in its table.
- **The JSEP reference** (`splats-and-link.md` B1): RFC 8829 is obsoleted by RFC 9429. The quoted text is
  unchanged. Cite RFC 9429.
- **Bug 215884's status** (`web-on-iphone.md` F3.2): RESOLVED CONFIGURATION, not open. A WebKit engineer moved the
  cross-launch request to a new bug.

Everything else checked above stays at the note's level.

## 7. Still open after this check

- Apple's own iOS 27 device list.
- Bug 269706 (the gesture lost through a worker) and the other permission edge-case bugs: not re-read.
- The TURN price; Capacitor's support-policy table; Godot export details; ARKit pages other than world tracking.
- E1's SDP sizes: not re-run here (the page was read only).
- E2's grow worst case: needs its script committed, or the row withdrawn.
