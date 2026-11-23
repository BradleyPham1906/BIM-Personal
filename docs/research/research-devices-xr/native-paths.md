# Topic note: native paths on iOS (H7, H8)

Part of `docs/research/research-devices-xr.md`. Researched 2026-11-23 by one of four parallel research agents,
following `docs/research/research-protocol.md`. Nothing here has been run on a phone or a Mac: every finding is
from documents and source code read as text. Third-party code was cloned shallowly into the session's scratch
folder and read; none of it was built or run.

Levels: P primary (read at the source), S secondary (gap said), U unverified (planning only, never code).
Confidence: high, medium, low, with the reason.

## 1. The questions

1. Apple's free provisioning: can the owner install an app of his own on his own iPhone with Xcode and a free
   Apple Account; the expiry and the limits; which capabilities a free account cannot use (ARKit, camera?);
   which Xcode is current and whether it runs on a MacBook Air of unknown model; what the paid program adds.
2. ARKit on an iPhone 13 (A15, no LiDAR): six-degree world tracking, the camera frames; Apple Vision's hand
   pose (iOS version, joints, confidence, performance, can it read ARKit's frames); is there any ARKit hand
   tracking on iPhone.
3. Capacitor: wrapping the existing web app in a native iOS shell; WKWebView's limits (camera, WebGL/WebGPU,
   memory); plugins that give JavaScript ARKit's pose or Vision's hand pose; the cost of the bridge per frame.
4. Godot 4: iOS export requirements, MobileVRInterface on iOS, GDMP, xibbon/GodotApplePlugins, the web export
   on iOS Safari, how Godot would get the BIM model, physics (Jolt).
5. A Swift app with RealityKit or SceneKit: effort, how it gets the model.
6. One table comparing web, Capacitor, Godot and Swift.

Hypotheses under test (from the main note):

- **H7.** A native build gives what the browser cannot (ARKit's six-degree tracking, Vision's hand pose); with
  Xcode and a free Apple ID it installs on the owner's phone for 7 days at a time.
- **H8.** Godot can only show the BIM model through an export (glTF or IFC); its iOS hand-tracking plugins are
  not maintained or not working on iOS.

## 2. Search log

| # | Where | Query or address | What came back | Kept or set aside |
|---|---|---|---|---|
| 1 | GitHub API (gh) | repos j20001970/GDMP, xibbon/GodotApplePlugins, godotengine/godot, ionic-team/capacitor | 403: the session's GitHub access is bound to the owner's repositories | Set aside; used `git ls-remote` and shallow clones instead |
| 2 | git | `git ls-remote` GDMP, GodotApplePlugins | Both exist. GDMP tags v0.1 to v0.6; GodotApplePlugins tags to v1.11.0 plus build tags | Kept |
| 3 | git clone --depth 1 | GDMP (master 31a54ab, 2026-07-30), GodotApplePlugins (main 4089921, 2026-10-28) | Sources read as text: README, LICENSE, BUILD files, hand landmarker, ARKit sources | Kept |
| 4 | developer.apple.com documentation JSON (`/tutorials/data/documentation/...json`) | Vision: VNDetectHumanHandPoseRequest, DetectHumanHandPoseRequest, VNHumanHandPoseObservation and JointName, maximumHandCount, chirality, VNRecognizedPoint, VNImageRequestHandler, VNDetectHumanBodyPose3DRequest; a 3D hand request (404, does not exist) | Platforms, abstracts, discussions, topic lists | Kept |
| 5 | same | ARKit: ARWorldTrackingConfiguration, ARConfiguration.isSupported, ARFrame.capturedImage, estimatedDepthData, sceneDepth, personSegmentationWithDepth, supportsSceneReconstruction, ARBodyTrackingConfiguration, HandTrackingProvider | As above | Kept |
| 6 | same | RealityKit (Entity.load, PhysicsBodyComponent, ARView, RealityView), SceneKit (deprecation), WebKit (WKUIDelegate media capture, cameraCaptureState, isInspectable), Safari "Inspecting iOS", NSCameraUsageDescription, Developer Mode | As above | Kept |
| 7 | developer.apple.com/help/account/reference/supported-capabilities-ios (HTML, table parsed; two rows checked by hand against the raw HTML) | Capability by membership: ADP, ADEP, "Apple Developer" (free) | Kept |
| 8 | developer.apple.com/support/compare-memberships | Personal Team limits; $99 program | Kept |
| 9 | developer.apple.com/support/xcode | Xcode versions, macOS required, SDKs, device support | Kept |
| 10 | support.apple.com/en-us/122867 (Tahoe), /120282 (Sequoia, through the fetch tool after a 429) | Mac models | Kept |
| 11 | Web search | iOS 27 compatible iPhones | MacRumors, TechRadar, EveryMac agree iPhone 11 and later; Apple's own page not returned | Kept as S |
| 12 | Web search, then webkit.org/blog/11353 | getUserMedia in WKWebView, iOS 14.3 | WebKit's own post; WebKit bugs 220184, 221031 (secure-context and NotAllowedError reports) | Kept |
| 13 | Web search, then webkit.org/blog/17333 | WebGPU in Safari 26 | WebKit's Safari 26.0 post has a WebGPU section; WKWebView coverage not stated | Kept, WKWebView part U |
| 14 | capacitorjs.com/docs/ios, /docs/main/reference/support-policy, /docs/plugins/ios | Capacitor requirements | iOS 15+, Xcode 26.0+ for Capacitor 8 | Kept |
| 15 | git sparse clone ionic-team/capacitor (main e0f75b3, 2026-11-20), `ios/` only | How plugin results and events reach JavaScript | `CapacitorBridge.swift`, `CAPPlugin+Bridge.swift` read | Kept |
| 16 | registry.npmjs.org search | "capacitor arkit", "capacitor hand pose", "capacitor vision hand", "capacitor-plugin ar", "capacitor mediapipe", "capacitor hand tracking", "keywords:arkit", "arkit plugin ios", "arkit webview", "capacitor augmented reality", "capacitor webxr", "cordova arkit" | No Capacitor or Cordova plugin exposing ARKit pose or Vision hand pose. Found: @mediapipe/tasks-vision (web), expo-roomplan, model-viewer, AR.js | Recorded as a negative finding |
| 17 | git clone mozilla-mobile/webxr-ios (2020-06-23) | Prior art: ARKit in a WKWebView app | Read `WebController.swift`, `ARKController+ARSessionDelegate.swift` | Kept as prior art |
| 18 | git sparse clone godotengine/godot-docs (master 4b22866) | exporting_for_ios, exporting_for_web, mobilevr_intro, using_jolt_physics, runtime_file_loading_and_saving, class_cameraserver, class_mobilevrinterface | Kept |
| 19 | git sparse clone godotengine/godot (master 67421f3, 2026-11-20) and raw.githubusercontent | modules/mobile_vr, drivers/apple_embedded, modules/camera; config.py of jolt_physics, gltf, webxr; LICENSE | Kept |
| 20 | Web search | "MobileVRInterface iOS not working" | No iOS issue found; a forum thread on k1/k2 not applied in the Compatibility renderer (Android) | Kept as counter-evidence of maintenance |
| 21 | Web search | GDMP iOS hand landmarker issue | Discussion #33 (image size from camera_helper), no iOS report | Kept |
| 22 | developers.google.com MediaPipe hand landmarker iOS (fetch tool) | Install, outputs | Swift Package MediaPipeTasksVision; 21 landmarks; world landmarks in metres | Kept as S (digest) |
| 23 | developer.apple.com/videos/play/wwdc2020/10653 transcript | Vision hand pose limits | Edges, hands parallel to the camera, gloves, feet as hands, maximumHandCount and performance | Kept |
| 24 | Web search, then forums.unrealengine.com/t/.../137540 | Counter-evidence: "ARKit needs a paid account" | One unsourced "AFAIK" post (2020) | Recorded |
| 25 | Web search | "personal team" ARKit on device | No first-hand report either way | Recorded |
| 26 | git clone googlevr/cardboard (v1.36.0, 2026-10-07) | Native Cardboard SDK | Apache-2.0 (Unity plugin folder excepted), Metal distortion renderer on iOS | Kept |
| 27 | raw.githubusercontent warrenm/GLTFKit2 | glTF in a Swift app | MIT; loader and (WIP) exporter, SceneKit and Model I/O extensions | Kept |
| 28 | github.com release pages (HTML) | GDMP and GodotApplePlugins release dates | 403; tag dates read with `git fetch --depth 1 origin tag` instead | Recorded |
| 29 | The app's code | `grep -rn gltf src/js/engine` | `src/js/engine/io/gltf.js` has an import and a GLB export | Kept |

## 3. Findings

### 3.1 Free provisioning, Xcode and the Mac

**F1. A free Apple Account installs the owner's own app on his own phone, with limits.** Apple's membership page,
under "Enable a personal team in Xcode": "You can register up to 10 App IDs, which expire after 7 days. You can
register up to 3 devices, which expire after 7 days. You can install up to 3 apps per device. Provisioning
profiles that enable apps to be installed on a device will expire 7 days from issuance. You'll need to rebuild
and reinstall your app to your device after expiration." Level P. Confidence high. A second source (an Expo blog
post and Apple forum threads in the search results) repeats it; one forum anecdote reports a build stopping
after 12 to 24 hours, not in Apple's text (U).

**F2. The phone needs Developer Mode.** Apple: turn on Settings > Privacy & Security > Developer Mode, restart,
confirm; it appears only after the phone is paired with a Mac. P, high.

**F3. ARKit and the camera are not on the list of capabilities a free account lacks.** Apple's table of iOS
capabilities by membership (columns ADP, ADEP and "Apple Developer", the last defined as Apple Account holders
who accepted the free agreement and "can't distribute apps") has no row for the camera or ARKit at all. They are
not entitlements: the camera needs only the `NSCameraUsageDescription` key in Info.plist ("This key is required
if your app uses APIs that access the device's camera", P), and ARKit an optional `arkit` entry in
`UIRequiredDeviceCapabilities` (P, ARConfiguration.isSupported). Rows the free account does have: App groups,
Background modes, Data protection, HealthKit, HomeKit, Inter-App Audio, Keychain sharing, Maps, Wireless
Accessory Configuration. Rows it lacks that could matter here: **Increased Debugging Memory Limit**, **Extended
Virtual Addressing**, iCloud (all three), Push notifications, Associated domains, Sign in with Apple, Game
Center. The table P (parsed, two rows checked against the raw HTML); the inference "ARKit and camera work under
a Personal Team" medium-high, because no document says so in words and no first-hand report was found either
way (search 25). The owner's first build settles it.

**F4. The paid program is $99 a year** and adds TestFlight and App Store distribution (Apple's membership page,
P). Without it, there is no TestFlight and no way to give the app to anyone else's phone.

**F5. Current Xcode needs a recent Mac.** Apple's Xcode support table (P, read 2026-11-23):

| Xcode | macOS | iOS SDK | Runs apps on |
|---|---|---|---|
| 27 to 27.2 (current), 27.3 beta | Tahoe 26.6 or later | iOS 27.x | iOS 17 or later |
| 26.4.1 to 26.6 | Tahoe 26.2 to 26.x | iOS 26.4 to 26.5 | iOS 15 or later |
| 26 to 26.3 | Sequoia 15.6 to Tahoe 26.x | iOS 26 to 26.2 | iOS 15 or later |
| 16.3, 16.4 | Sequoia 15.2/15.3 and later | iOS 18.4/18.5 | iOS 15 or later |
| 16 to 16.2 | Sonoma 14.5 to Sequoia 15.x | iOS 18 to 18.2 | iOS 15 or later |

Which MacBook Air runs what (Apple's compatibility pages, P): **macOS Tahoe 26**: MacBook Air M1 (2020) and every
later Air; no Intel Air. **macOS Sequoia 15**: the same plus the Intel MacBook Air (Retina, 13-inch, 2020).
So:

- an Apple silicon Air (M1 or later) runs the current Xcode 27;
- the Intel Air of 2020 stops at Sequoia, so at Xcode 26.3 (iOS 26.2 SDK), which still meets Capacitor 8's
  Xcode 26.0 minimum;
- an older Intel Air (2018, 2019) stops at Sonoma, so at Xcode 16.2 (S: Sonoma as their last macOS is from
  Apple's earlier pages, not re-read today), below Capacitor 8's minimum; Capacitor 7 (Xcode 16.0) would be the
  ceiling.

Whether an older Xcode can install onto an iPhone running a newer iOS (iOS 27) is not stated in the table
("Device support: iOS 15 or later" for Xcode 26) and is U; the owner's model decides how much this matters.

**F6. The iPhone 13 runs iOS 27.** MacRumors (2026-09-14), TechRadar and EveryMac agree that iOS 27 supports the
iPhone 11 and later; Apple's own list was not returned by the search. S, high (three independent outlets
agreeing). Apple Intelligence is not available on it, which nothing here needs.

**F7. The Mac also opens Safari's Web Inspector on the iPhone.** Apple: web content on iOS, including Home
Screen web apps, is inspectable from a connected Mac once Settings > Apps > Safari > Advanced > Web Inspector is
on; a WKWebView is inspectable when the app sets `isInspectable` (iOS 16.4). P, high. This helps the web path
too, with no developer account at all.

### 3.2 ARKit and Vision on an iPhone 13

**F8. Six-degree world tracking works without LiDAR.** `ARWorldTrackingConfiguration` (iOS 11) "tracks the
device's movement with six degrees of freedom (6DOF): the three rotation axes ... and three translation axes";
"All ARKit configurations require an iOS device with an A9 or later processor." LiDAR is needed only for scene
reconstruction (`supportsSceneReconstruction`: "requires a device with a LiDAR Scanner") and `sceneDepth`. P,
high. The A15 is well past A9.

**F9. ARKit hands each frame's camera image to the app.** `ARFrame.capturedImage` (iOS 11) is a pixel buffer in
full-range planar YCbCr. P, high.

**F10. Vision's hand pose runs on any CVPixelBuffer, so on ARKit's frames.** `VNDetectHumanHandPoseRequest`:
iOS 14. `VNImageRequestHandler` has `init(cvPixelBuffer:orientation:options:)`. Joints: `wrist` plus four per
finger (thumb tip, IP, MP, CMC; index, middle, ring, little: tip, DIP, PIP, MCP): 21 points. Each is a
`VNRecognizedPoint`, "a normalized point in an image, along with an identifier label and a confidence value".
`maximumHandCount`: default 2, the largest hands first. `chirality` (left or right): iOS 15. The Swift-only
`DetectHumanHandPoseRequest` / `HumanHandPoseObservation`: iOS 18. All P, high. That an ARKit frame goes through
`VNImageRequestHandler` is from the types (both CVPixelBuffer), P, high; that it runs at camera rate alongside
ARKit on an A15 is not documented (U, measure).

**F11. Vision's hand pose is two-dimensional.** Its points are normalized image coordinates. No 3D hand request
exists (`vndetecthumanhandpose3drequest` answers 404; the 3D request that exists, iOS 17, is for the body). On a
phone without LiDAR, a hand's distance must come from elsewhere: an assumed hand size, ARKit's
`estimatedDepthData` with `personSegmentationWithDepth` (iOS 13, P; its device floor, A12, is S from Apple's
ARKit 3 announcement, and must be checked at run time with `supportsFrameSemantics`, P), or MediaPipe's world
landmarks (F14). P for the absence, high. This matters for grabbing: a grab needs depth.

**F12. Vision's documented limits** (WWDC20 session 10653, Apple's transcript, P): hands near the image edges
may fail; hands parallel to the camera's direction are hard; gloves; feet can be taken for hands; lowering
`maximumHandCount` helps performance. Apple publishes no frame rate or latency. High for the limits, none for
speed.

**F13. There is no ARKit hand tracking on iPhone.** `HandTrackingProvider` is visionOS 1.0 only (P). On iPhone,
ARKit's people features are body tracking (`ARBodyTrackingConfiguration`, iOS 13, a skeleton without fingers,
P) and person segmentation. GodotApplePlugins's own hand-tracking file is compiled only under
`#if canImport(ARKit) && os(visionOS)` (P, source). High.

**F14. MediaPipe's native iOS hand landmarker is the 3D alternative.** Google's guide: Swift Package
`MediaPipeTasksVision` from github.com/google-ai-edge/mediapipe; image, video and live-stream modes (live stream
drops frames while busy); 21 landmarks per hand; `worldLandmarks` in metres with the origin at the hand's
geometric centre; handedness. Published latency is for a Pixel 6 (17 ms CPU, 12 ms GPU), not an iPhone. S (read
through the fetch tool's digest), medium. Apache-2.0 is the licence of the MediaPipe repository (not re-read
today: S).

### 3.3 Capacitor

**F15. Capacitor 8 wraps the web app in a WKWebView, MIT.** Capacitor's iOS page: "iOS 15+ is supported. Xcode
26.0+ is required." "Capacitor uses WKWebView." Its support policy: v8 needs Xcode 26.0 and Node 22; v7 Xcode
16.0. `@capacitor/core` and `@capacitor/cli` 8.6.2 (2026-11-12) are MIT (npm metadata and the repository's
LICENSE, "Copyright (c) 2017-present Drifty Co."). P, high. The app's files are bundled into the iOS app, so it
opens offline; that fits the delivery contract.

**F16. JavaScript in the shell can use the camera, with caveats.** WebKit (blog 11353, iOS 14.3): "getUserMedia
can now be exposed to WKWebView applications ... automatically exposed if the embedding application is able to
natively capture either audio or video", gated by a user prompt. Since iOS 15 the app can decide the prompt
itself (`webView(_:requestMediaCapturePermissionFor:...)`, P) and read `cameraCaptureState` (P). WebKit bug
220184 reports getUserMedia only on secure origins in WKWebView, and 221031 a NotAllowedError on iOS 14.4
(S, bug reports, old). Capacitor serves from `capacitor://localhost`; whether that counts as secure for
getUserMedia today is U. Whether getUserMedia and an ARKit session can hold the back camera at the same time
is U, and unlikely (ARKit drives the camera itself): in the shell, hand pose would run natively on ARKit's frame
(F10, F14), not in JavaScript.

**F17. WebGL and WebGPU in the shell.** WebKit's Safari 26.0 post lists WebGPU as shipping (P for Safari).
WKWebView gets the same WebKit; whether WebGPU is on by default in a WKWebView is not stated (U; one Apple forum
thread from the iOS 18.2 era says Safari's feature flags do not reach WKWebView). WebGL 2 in WKWebView is long
standing (S). WKWebView's memory ceiling is not documented by Apple (U); the "Increased Debugging Memory Limit"
capability is not available to a free account (F3).

**F18. No maintained plugin gives JavaScript ARKit's pose or Vision's hand pose.** Twelve npm searches (log 16)
found none for Capacitor or Cordova. The owner would write one small plugin of his own (Swift, MIT or ours):
Capacitor's plugin guide shows the pattern (a `CAPPlugin` subclass, Swift Package and podspec). P for the
search result as of 2026-11-23, medium for "none exists" (npm search can miss unpublished GitHub code).

**F19. The bridge is JSON through `evaluateJavaScript` on the main thread.** In Capacitor's source (main
e0f75b3): `toJs` serializes the result to JSON and runs `window.Capacitor.fromNative({...})` with
`webView.evaluateJavaScript` inside `DispatchQueue.main.async`; `notifyListeners` delivers each event to every
listener the same way. P, high. Per-frame cost is not published (U, measure): ARKit's pose (16 floats) plus two
hands of 21 points (about 130 numbers) is under 2 KB of JSON a frame, small; images must never cross this way.
Prior art: Mozilla's WebXR Viewer (mozilla-mobile/webxr-ios, MPL-2.0, last commit 2020-06-23, no longer used)
did exactly this: `session(_:didUpdate frame:)` collected ARKit data and `callWebMethod` sent it as JSON through
`evaluateJavaScript` each frame; it also had an opt-in path sending camera frames ("computerVisionData") to
JavaScript. P (source read), high that it is feasible; the latency it achieved is not recorded (U).

### 3.4 Godot 4

**F20. iOS export needs a Mac with Xcode.** Godot docs: "You must export for iOS from a computer running macOS
with Xcode installed"; the export asks for an App Store Team ID (10 characters) and a bundle ID. P, high. A
Personal Team has a team ID (S: Godot's docs do not say whether a free team works; Xcode's Personal Team signs
like any other, F1).

**F21. MobileVRInterface works on iOS but only in three degrees, and is not maintained.** Godot docs: "a bare
bones implementation that outputs a side by side stereoscopic image. It supports basic 3DOF tracking"; warning:
"This implementation is not actively maintained ... mostly used for diagnostic purposes." It has k1, k2 lens
distortion and the phone and viewer dimensions. The module builds on every platform unless XR is disabled
(`modules/mobile_vr/config.py`), and on iOS Godot feeds the gyroscope from `CMMotionManager`
(`drivers/apple_embedded/godot_view_apple_embedded.mm`, lines 64, 153 to 156, 478 to 499). P, high. Counter-
evidence: a Godot forum thread reports k1 and k2 having no effect in the Compatibility renderer (Android, a
developer called it a likely bug) (S). No iOS-specific issue found (search 20).

**F22. GDMP exists, MIT, and has an iOS target, but nothing shows it tested on iOS for hands.**
github.com/j20001970/GDMP: "a Godot Engine plugin for utilizing MediaPipe framework and solutions", MIT
("Copyright (c) 2021-present Jason Kuo & contributors"). Latest tag v0.6 (2025-09-16); master 31a54ab
(2026-07-30, "mediapipe v1.0.0"). It wraps `MediaPipeHandLandmarker` (handedness, `hand_landmarks`,
`hand_world_landmarks`) and the other vision tasks. iOS: `docs/BUILDING.md` "Building for iOS: install Xcode
... run `build.py ios`" (Bazel; arm64 device), and its CI builds an iOS xcframework on macos-14. Its own camera
helper is deprecated ("Please consider CameraServer-based methods"), and on master `GDMP/io/BUILD` selects only
the stub for the default helper; frames come from Godot's `CameraServer`, which on iOS needs the export option
`modules/camera` (Godot class reference, P). Whether release archives ship an iOS build was not checkable
(GitHub's release pages refused, 403). P for what the source contains; low for "works on an iPhone 13".

**F23. xibbon/GodotApplePlugins exists, MIT, and is active, but gives no hand pose on iPhone.** By Miguel de
Icaza ("Copyright (c) 2025"), last commit 2026-10-28, tag v1.11.0 (2026-06-15). Bindings for GameCenter,
StoreKit, Sign in with Apple, file picker, iCloud key-value, ARKit, CoreMotion, AVFoundation; requires iOS 17,
macOS 14. Its iOS ARKit binding has `ARSession`, `ARWorldTrackingConfiguration` (6DoF), `ARFrame` with
`camera`, anchors, and the captured image as raw planes (`get_captured_image_plane_data` returns a
PackedByteArray). Hand tracking (`ARHandTracking.swift`) compiles only for visionOS (F13). No Vision framework
use in the sources. Built on SwiftGodot (pinned revision in Package.swift). P, high. So, in Godot on iPhone:
6DoF from this plugin plus hand pose from GDMP fed by ARKit's image bytes is possible on paper; nobody has been
found doing it (U).

**F24. Godot's web export on iOS Safari gives none of the native gains.** Godot 4's web export uses WebGL 2 (the
Compatibility renderer) and, since 4.3, a single-threaded build that "works very well on macOS and iOS"; the docs
also warn "Safari has several issues with WebGL 2.0" and that native exports "perform better by a significant
margin". P, high. It has no ARKit; its WebXR module needs a browser with WebXR, which iPhone Safari is not
(H1's topic).

**F25. Godot gets the model through glTF.** Godot docs: with `GLTFDocument` and `GLTFState`, "Godot can load
and save glTF files in exported projects" at run time. The app already exports GLB: `bimGltfExportBytes` and
`bimGltfExport` in `src/js/engine/io/gltf.js` lines 267 to 276, through three.js's `GLTFExporter`. Godot has no
IFC reader. P, high. IFC properties would travel only as glTF extras, if the exporter writes them (not checked).

**F26. Physics in Godot: Jolt is built in since 4.4, the default for new projects;** Jolt is MIT (Jorrit Rouwe);
the `jolt_physics` module builds unless 3D physics is disabled. Missing: some joint softness properties. P, high.

### 3.5 Swift with RealityKit or SceneKit

**F27. SceneKit is deprecated; RealityKit is Apple's path.** SceneKit's page: "SceneKit is deprecated, use
RealityKit instead" (WWDC25 session 288). RealityKit has physics built in (`PhysicsBodyComponent` with
`CollisionComponent`, iOS 13), `ARView` (iOS 13) and `RealityView` (iOS 18). RealityKit loads only USD and
.reality files ("RealityKit supports loading entities from USD ... and Reality files"). P, high. glTF needs a
converter or a library: GLTFKit2 (warrenm, MIT) loads glTF for SceneKit and Model I/O. P (README, LICENSE).

**F28. Cardboard stereo natively: Google's Cardboard SDK.** googlevr/cardboard, v1.36.0 (2026-10-07), Apache-2.0
except the Unity plugin folder (Unity Companion License). It provides head tracking, lens distortion
(polynomial radial, from the viewer's QR code) and a Metal distortion renderer for iOS. Its tracking is from
the phone's sensors (3DoF); combining it with ARKit's 6DoF would be our own work. P, high for what it is. Its
distortion method is also useful to the web path as a method, credited.

**F29. Effort.** A Swift app re-implements what the web engine already draws (model display, selection, layers)
and reaches the model only by export (GLB to USDZ, or GLTFKit2). Not measured; judged from the above. U.

## 4. The alternatives compared

Criteria, fixed before the table: what it unlocks for the owner's goal (6DoF, hand pose with depth, physics),
what it costs (money, a Mac), what it reuses of the existing engine (reuse-first), licence fit with the
library rule, effort, and how updates reach the phone.

| | Web (Safari, installed web app) | Capacitor shell + own plugin | Godot 4 native | Swift + RealityKit |
|---|---|---|---|---|
| Money | none | none (free Personal Team) | none | none |
| Mac needed | no (yes for Web Inspector, F7) | yes, Xcode 26+ (Capacitor 8) | yes, Xcode | yes, Xcode |
| Tracking | 3DoF from orientation (H2's topic) | 6DoF from ARKit (F8) | 3DoF MobileVR (F21); 6DoF only through GodotApplePlugins (F23) | 6DoF ARKit (F8) |
| Hand pose | MediaPipe JS in the page (H4's topic) | Vision 2D (F10, F11) or MediaPipe iOS with world landmarks (F14), natively on ARKit's frame | GDMP (F22), untested on iOS | Vision or MediaPipe, native |
| Physics | a JS/WASM engine (H5's topic) | the same JS engine | Jolt built in (F26) | RealityKit physics (F27) |
| Stereo, lens | our own drawing | our own drawing (same code) | MobileVR k1, k2 | Cardboard SDK (F28) |
| Reuse of the JS engine | all | all; native only for pose and hands | none (model by GLB, F25) | none (model by GLB/USDZ) |
| Licences | ours + chosen libraries | Capacitor MIT; Vision is the OS; MediaPipe Apache-2.0 (S) | Godot MIT, Jolt MIT, GDMP MIT, GodotApplePlugins MIT | OS frameworks; GLTFKit2 MIT; Cardboard Apache-2.0 |
| Effort (U) | lowest | small: one Swift plugin (ARKit session, Vision or MediaPipe, JSON events) and a build per week | large: a second app, a plugin chain nobody has shown working on iPhone | largest: a second app in Swift |
| Updates | instant (Pages, offline web app) | rebuild and reinstall from the Mac at least every 7 days (F1) | same as Capacitor | same as Capacitor |
| Who else can use it | anyone with a link | only the owner's 3 devices, until $99 (F4) | same | same |
| Fit with the delivery contract | full | keeps the engine as is; the native part is a separate, optional shell | a separate program | a separate program |

## 5. Counter-evidence sought

- **"Free provisioning blocks ARKit."** One forum post (Unreal Engine forums, 2020-02-04, "AFAIK, for ARKit
  stuff you are going to need a paid dev account"), unsourced. Apple's capability table lists no ARKit or
  camera entitlement (F3). Held: not blocked, medium-high, until the first build.
- **"Free provisioning blocks memory-hungry apps."** Found in Apple's table: Increased Debugging Memory Limit and
  Extended Virtual Addressing are paid only. A large BIM model in a native app runs under the default limit.
- **"Vision hand pose is not on iPhone or not on A15."** No such restriction found; iOS 14 and later (P).
  Found instead: 2D only (F11) and documented accuracy limits (F12).
- **"ARKit has hand tracking on iPhone."** Not found; visionOS only (F13).
- **"Godot MobileVR is maintained."** The docs say it is not (F21).
- **"GDMP and GodotApplePlugins are abandoned."** Not so: both had commits in 2026 (F22, F23). H8's "not
  maintained" fails; "not working on iOS for hands" stands for lack of evidence.
- **"A Capacitor plugin for ARKit exists."** Not on npm (F18).
- **"getUserMedia works in any WKWebView."** WebKit bugs report secure-origin and permission failures (F16).

## 6. Outcome for H7 and H8

**H7: holds, with three corrections.**

1. Confirmed: the free Personal Team installs on the owner's phone for 7 days at a time, up to 3 apps and 3
   devices (F1, P); ARKit and the camera need no paid capability (F3, medium-high); ARKit's 6DoF and Vision's
   hand pose run on an A15 (F8, F10, P).
2. Corrected: a Capacitor shell alone does not give them; it needs a small native plugin of our own, since none
   is published (F18). The bridge is JSON per event on the main thread (F19): fine for poses and points, wrong
   for images.
3. Corrected: Vision's hand pose is 2D; grabbing in depth needs MediaPipe's world landmarks or a depth estimate
   (F11, F14). The Mac must be an M1 or later Air for the current Xcode 27, or the Intel 2020 Air for Xcode 26.3,
   which is still enough for Capacitor 8 (F5).

**H8: holds in part.** Godot can show the model only by export: glTF at run time, from the app's existing GLB
export (F25, P); no IFC. The hand-tracking half is half right: GDMP and GodotApplePlugins are maintained (that
part fails), but neither offers working, tested hand pose on an iPhone: GodotApplePlugins' hands are visionOS
only, and GDMP's iOS build is from source on a Mac with no iOS hand report found (F22, F23).

## 7. Recommendation

1. **Build the web path first** (the other three notes): it reuses the whole engine, costs nothing, updates
   instantly, and anyone can open it. Use the Mac now for Safari's Web Inspector on the iPhone (F7) when the
   test page is measured.
2. **If the web path's measured limits fail the goal** (3DoF only, or MediaPipe in Safari under 20 frames a
   second, H4, H6), the native step is a **Capacitor shell with one small Swift plugin of our own**: an ARKit
   world-tracking session sending the camera pose each frame, and hand points (MediaPipe's native landmarker for
   3D world landmarks, or Vision for 2D with a depth estimate) as JSON events; the web engine, stereo drawing
   and physics stay in JavaScript, unchanged. This is the reuse-first choice: it adds a narrow native adapter and
   keeps the app's code ES5 behind the plugin's JavaScript interface. Capacitor would be a new library under
   the library rule (MIT, pinned, research and the owner's approval first), and only the shell uses it; the
   web app keeps working without it.
3. **Not Godot** for now: it throws away the engine, its MobileVR is 3DoF and unmaintained, and its iPhone hand
   path is a chain of two plugins nobody has shown working together.
4. **Not Swift** for now: the most effort, and the same loss of the engine. It becomes the choice only if both
   the browser and WKWebView prove too slow to draw the model in stereo.

What would change it: a measurement showing WebGL in WKWebView far slower than native for the owner's models;
ARKit refusing to run under a Personal Team on the first build; or Apple shipping WebXR immersive sessions in
iPhone Safari.

What the Mac makes possible, in short: Web Inspector on the phone (any Mac); Xcode builds signed by a free
Personal Team, installed on the owner's own iPhone for 7 days at a time (an M1 or later Air for Xcode 27; the
Intel 2020 Air for Xcode 26.3); with that, ARKit's 6DoF tracking and native hand pose. Without $99 a year, no
one else can install it.

## 8. Still open (U)

- The MacBook Air's model (decides Xcode 27, 26.3 or 16.2, and whether Capacitor 8 builds).
- A first ARKit build under a Personal Team on the owner's phone (F3's inference).
- Vision and MediaPipe hand pose frame rates on an A15 alongside an ARKit session (F10, F14).
- Whether getUserMedia works in a Capacitor WKWebView served from `capacitor://localhost`, and whether it can
  share the camera with ARKit (F16).
- WebGPU on by default in WKWebView on iOS 26/27 (F17); WKWebView's memory ceiling.
- The bridge's per-event latency at 60 events a second (F19).
- Whether an older Xcode installs onto an iPhone on iOS 27 (F5).
- Whether GDMP's releases include an iOS build, and whether it runs on an iPhone (F22).
- MediaPipe's licence and minimum iOS read at the source (F14 is S).
- iOS 27's device list on Apple's own page (F6 is S).

## 9. References (all read 2026-11-23)

| Source | URL | What was read | Level |
|---|---|---|---|
| Apple, Choosing a Membership | https://developer.apple.com/support/compare-memberships | Personal Team limits, $99 program, TestFlight | P |
| Apple, Supported capabilities (iOS) | https://developer.apple.com/help/account/reference/supported-capabilities-ios | The whole table, parsed; columns defined | P |
| Apple, Xcode support | https://developer.apple.com/support/xcode/ | Version table, macOS, SDKs, device support | P |
| Apple, macOS Tahoe compatible computers | https://support.apple.com/en-us/122867 | MacBook Air list | P |
| Apple, macOS Sequoia compatible computers | https://support.apple.com/en-us/120282 | MacBook Air list (through the fetch tool) | P |
| Apple, Enabling Developer Mode | https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device | Whole page | P |
| Apple, NSCameraUsageDescription | https://developer.apple.com/documentation/bundleresources/information-property-list/nscamerausagedescription | Abstract, discussion | P |
| Apple, ARWorldTrackingConfiguration | https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration | Overview | P |
| Apple, ARConfiguration.isSupported | https://developer.apple.com/documentation/arkit/arconfiguration/issupported | Discussion (A9) | P |
| Apple, ARFrame.capturedImage, estimatedDepthData, sceneDepth | https://developer.apple.com/documentation/arkit/arframe | Three property pages | P |
| Apple, personSegmentationWithDepth, supportsFrameSemantics, supportsSceneReconstruction | https://developer.apple.com/documentation/arkit/arconfiguration | Three pages | P |
| Apple, ARBodyTrackingConfiguration | https://developer.apple.com/documentation/arkit/arbodytrackingconfiguration | Overview | P |
| Apple, HandTrackingProvider | https://developer.apple.com/documentation/arkit/handtrackingprovider | Platforms (visionOS) | P |
| Apple, VNDetectHumanHandPoseRequest and maximumHandCount | https://developer.apple.com/documentation/vision/vndetecthumanhandposerequest | Platforms, topics, discussion | P |
| Apple, VNHumanHandPoseObservation, JointName, chirality, VNRecognizedPoint | https://developer.apple.com/documentation/vision/vnhumanhandposeobservation | Topics, joint list, platforms | P |
| Apple, DetectHumanHandPoseRequest, HumanHandPoseObservation | https://developer.apple.com/documentation/vision/detecthumanhandposerequest | Platforms | P |
| Apple, VNImageRequestHandler | https://developer.apple.com/documentation/vision/vnimagerequesthandler | Initializers | P |
| Apple, VNDetectHumanBodyPose3DRequest | https://developer.apple.com/documentation/vision/vndetecthumanbodypose3drequest | Overview | P |
| Apple, Detecting Hand Poses with Vision (sample) | https://developer.apple.com/documentation/vision/detecting-hand-poses-with-vision | Overview | P |
| Apple, WWDC20 10653 Detect Body and Hand Pose with Vision | https://developer.apple.com/videos/play/wwdc2020/10653/ | Transcript: limits, maximumHandCount | P |
| Apple, SceneKit | https://developer.apple.com/documentation/scenekit | Deprecation note | P |
| Apple, RealityKit Entity.load, PhysicsBodyComponent, ARView, RealityView | https://developer.apple.com/documentation/realitykit | Four pages | P |
| Apple, WKUIDelegate media capture; WKWebView cameraCaptureState, isInspectable | https://developer.apple.com/documentation/webkit/wkwebview | Three pages | P |
| Apple, Inspecting iOS and iPadOS | https://developer.apple.com/documentation/safari-developer-tools/inspecting-ios | Overview, steps | P |
| WebKit, MediaRecorder API (getUserMedia in WKWebView) | https://webkit.org/blog/11353/mediarecorder-api/ | The WKWebView section | P |
| WebKit, Features in Safari 26.0 | https://webkit.org/blog/17333/webkit-features-in-safari-26-0/ | WebGPU and WebKit API sections | P |
| WebKit bugs 220184, 221031 | https://bugs.webkit.org/show_bug.cgi?id=220184 | Search digest only | U |
| Apple forums thread 770862 (WebGPU in WKWebView) | https://developer.apple.com/forums/thread/770862 | Search digest only | U |
| Capacitor, iOS | https://capacitorjs.com/docs/ios | Requirements | P |
| Capacitor, support policy | https://capacitorjs.com/docs/main/reference/support-policy | Version table | P |
| Capacitor, iOS plugin guide | https://capacitorjs.com/docs/plugins/ios | Plugin basics, SPM and podspec | P |
| Capacitor source, main e0f75b3 | https://github.com/ionic-team/capacitor | `ios/Sources/Capacitor/CapacitorBridge.swift` 494 to 610, `CAPPlugin+Bridge.swift` 35 to 60, LICENSE | P |
| npm registry search | https://registry.npmjs.org/-/v1/search | Twelve queries (log 16) | P (for the result) |
| Mozilla WebXR Viewer v1, 24a4868 | https://github.com/mozilla-mobile/webxr-ios | README, LICENSE, `WebController.swift` 490 to 510, `ARKController+ARSessionDelegate.swift` | P |
| Godot docs, master 4b22866 | https://github.com/godotengine/godot-docs | exporting_for_ios, exporting_for_web, mobilevr_intro, using_jolt_physics, runtime_file_loading_and_saving, class_cameraserver, class_mobilevrinterface | P |
| Godot engine, master 67421f3 | https://github.com/godotengine/godot | modules/mobile_vr (config.py, mobile_vr_interface.cpp 123 to 222), drivers/apple_embedded/godot_view_apple_embedded.mm, modules/camera, config.py of jolt_physics, gltf, webxr, LICENSE.txt | P |
| Godot forum, MobileVRInterface distortion in Compatibility | https://forum.godotengine.org/t/mobilevrinterface-disortion-factors-in-compatibility-mode-dont-work/102057 | Search digest | S |
| GDMP, master 31a54ab, tag v0.6 | https://github.com/j20001970/GDMP | README, LICENSE, docs/BUILDING.md, GDMP/io/BUILD and camera_helper.cc, GDMP/tasks/vision/hand_landmarker.h, CI workflow | P |
| GDMP discussion #33 | https://github.com/j20001970/GDMP/discussions/33 | Search digest | U |
| GodotApplePlugins, main 4089921, tag v1.11.0 | https://github.com/xibbon/GodotApplePlugins | README, LICENSE, Sources/GodotARKit (ARKitGuide.md, ARHandTracking.swift, ARFrame.swift 30 to 130, ARSession and ARWorldTrackingConfiguration guards), Package.swift | P |
| MediaPipe hand landmarker for iOS | https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/ios | Install, outputs, latency (fetch tool digest) | S |
| Google Cardboard SDK, v1.36.0 | https://github.com/googlevr/cardboard | README, LICENSE, sdk/ layout, sdk/include/cardboard.h | P |
| GLTFKit2 | https://github.com/warrenm/GLTFKit2 | README, LICENSE | P |
| Jolt Physics | https://github.com/jrouwe/JoltPhysics | LICENSE | P |
| iOS 27 device list | https://www.macrumors.com/2026/09/14/ios-27-compatible-iphones/ and TechRadar, EveryMac (search digest) | Supported models | S |
| Unreal forums, FaceAR without a paid account | https://forums.unrealengine.com/t/facear-sample-ios-app-without-paid-developer/137540 | Both posts (fetch tool) | S (as counter-evidence) |
| Expo, Apple developer program free vs paid | https://expo.dev/blog/apple-developer-program-explained-free-vs-paid | Search digest | U |
| The app | `src/js/engine/io/gltf.js` | Function list; GLB export at lines 267 to 276 | P |
