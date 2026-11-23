# Topic note: the web app on an iPhone 13 as a cardboard headset (H1, H2, H3)

Corrections from the independent check (2026-11-23) are in `independent-check.md` and applied in the main note,
`../research-devices-xr.md`; where they differ, those win.

Part of `docs/research/research-devices-xr.md`. Researched 2026-11-23 by one of four parallel research agents,
following `docs/research/research-protocol.md`. Nothing here was run on an iPhone; what must be measured on the
owner's phone is listed in section 7. No third-party code was run: library and browser sources were read as text.

## 1. The questions

1. WebXR in Safari on an iPhone (not Vision Pro): is an `immersive-vr` or `immersive-ar` session supported in
   iOS 17, 18, 26 or 27? Behind a feature flag?
2. `DeviceOrientationEvent` and `DeviceMotionEvent` on iOS: the `requestPermission()` flow, the HTTPS
   requirement, behaviour in a Home Screen web app (standalone), versions, known bugs.
3. `getUserMedia` with the back camera in Safari and in a Home Screen web app: since which version, known bugs,
   getting each frame into a WebGL texture, resolution and frame rate.
4. Full screen on an iPhone (element fullscreen or only video), Screen Wake Lock, orientation lock; how web
   cardboard apps get the whole screen.
5. Drawing stereo: three.js `StereoCamera`/`StereoEffect`; the Cardboard viewer profile and the barrel
   distortion of the Cardboard SDK and `cardboard-vr-display`; head orientation from `deviceorientation` to a
   quaternion and its gotchas.
6. Prior art: A-Frame on iOS, Google's WebXR polyfill on iOS, working web cardboard on iOS 17 or later.

Hypotheses under test (from the main note): **H1** Safari on iOS offers no immersive WebXR session on an iPhone,
so the app draws cardboard stereo itself. **H2** Safari on iOS gives the page orientation (after a permission tap)
and the back camera, also in the installed web app. **H3** an iPhone page cannot go truly full screen; the
installed web app is the way to a full-screen view.

## 2. Search log

| # | Where | Query or request | What came back | Kept or set aside |
|---|---|---|---|---|
| 1 | npm registry | `npm pack @mdn/browser-compat-data` (8.1.10, modified 2026-11-19) and a script reading `data.json` | Support records for `XRSystem`, `DeviceOrientationEvent`, `requestPermission`, `getUserMedia`, `requestFullscreen`, `WakeLock`, `ScreenOrientation.lock`, manifest `display`/`orientation`, `requestVideoFrameCallback`, `MediaStreamTrackProcessor`; a walk of every `safari_ios` note mentioning iPhone, standalone or Home Screen; the `safari_ios` release table (iOS 27.2 current, 27.3 beta) | Kept (P for what MDN records; MDN is itself a secondary compilation, so each key fact is also checked at WebKit or Apple) |
| 2 | Web search | WebKit WebXR iPhone Safari immersive-vr feature flag iOS 18 | Pointers to WebKit bug 208988, Apple forum threads on visionOS WebXR | Pointers only; bug read at the source |
| 3 | bugs.webkit.org (curl, text) | Bug 208988 (WebXR meta bug) | Read in full: no iPhone support at any time; flag reports from iOS 15.6.1 and 16.4 with sessions unsupported; closed 2026-04-01 with "Apple has already shipped WebXR support for VisionOS" | Kept, P |
| 4 | raw.githubusercontent.com, WebKit/WebKit main | `Source/WTF/wtf/PlatformEnableCocoa.h`, `Source/WTF/Scripts/Preferences/UnifiedWebPreferences.yaml` | `ENABLE_WEBXR` defined only for `PLATFORM(VISION)` or Mac with compositor services; `FullScreenEnabled` is an embedder preference (default false, Safari decides); `DeviceOrientationPermissionAPIEnabled` | Kept, P (the decisive H1 evidence) |
| 5 | developer.apple.com (JSON behind the Safari release notes) | Safari 13, 16.4, 17, 17.4, 18, 18.4, 26, 26.2, 26.4, 27 release notes | Safari 13 "Added a permission API on iOS for DeviceMotionEvent and DeviceOrientationEvent"; 16.4 Wake Lock, unprefixed Fullscreen "on macOS and iPadOS"; 18 "immersive WebXR in visionOS"; 18.4 "Fixed Wake Lock API for Home Screen Web Apps"; 26.2 WebGPU for WebXR under "Spatial Web"; 26.4 secure-context fix for the motion interfaces; 27 `<model>` on iOS, no iPhone fullscreen, no iPhone WebXR | Kept, P. Safari 13.4 and 14.5 notes answered 404 |
| 6 | bugs.webkit.org | 206854, 212934, 310661 (iPhone fullscreen) | 206854 "Add Fullscreen API to iOS" is NEW (last activity 2026-10-24); 212934 WONTFIX 2026-01-25 in favour of 206854; 310661 (iOS 26) duplicate of 206854; a commenter checked the Safari 27 beta notes on 2026-06-08 and found nothing | Kept, P |
| 7 | Web search | iPhone Safari element requestFullscreen iOS 26 | Pointers to the bugs above | Pointers only |
| 8 | bugs.webkit.org | 254545 (Wake Lock in Home Screen apps), 264218 (display-mode) | 254545: WebKit side done 2023, Safari side shipped later (Apple note 18.4); 264218 NEW: an installed app reports `display-mode: fullscreen` though the status bar shows | Kept, P |
| 9 | bugs.webkit.org | 185448, 215884, 252465, 327237 (getUserMedia in Home Screen apps) | 185448 fixed in iOS 13.4; 215884 hash change re-prompts (improved 14.5), still reports in 18.5; 252465 video fails to play stream in PWA, committed 265986@main 2023-07-12; 327237 (2026-10-12, NEW) camera permission asked again on every launch of a Home Screen app on iOS 26/27 | Kept, P |
| 10 | raw.githubusercontent.com, WebKit | `DeviceOrientationAndMotionAccessController.cpp`, `WebDeviceOrientationAndMotionAccessController.cpp`, `DeviceOrientationEvent.idl`, `WebPreferencesDefaultValues.cpp`, `WebCoreMotionManager.mm` | Permission needs a user gesture to prompt; decision cached per top-level origin in the website data store (memory); IDL `SecureContext`, iOS-only `webkitCompassHeading`; motion polled at 1/60 s; Euler extraction code | Kept, P |
| 11 | Web search, bugs.webkit.org | requestPermission home screen standalone; then bugs 269706, 271891, 221399, 213966, 283803, 301294 | 269706 (NEW): permission denied after a worker round trip in the tap; 301294: iOS 26 regression in iframes only; no bug found for top-level standalone pages | Kept, P; no counter-evidence for standalone top-level |
| 12 | raw.githubusercontent.com, w3c/deviceorientation | `index.bs` | Z-X'-Y'' intrinsic Tait-Bryan definition, axes, `requestPermission` steps (transient activation), relative vs absolute | Kept, P |
| 13 | npm registry (tarballs read as text) | three@0.186.1, cardboard-vr-display@1.0.19, webvr-polyfill@0.10.12, webxr-polyfill@2.0.3, aframe@1.8.0 | `StereoCamera` and `StereoEffect` source; distortion polynomial, viewer profiles, distortion mesh; iOS "just fake it" present path with NoSleep; A-Frame 1.8 throws without WebXR; A-Frame's vendored `DeviceOrientationControls` formula | Kept, P |
| 14 | raw.githubusercontent.com, googlevr/cardboard | `proto/cardboard_device.proto`, `LICENSE`, `sdk/qrcode/cardboard_v1/cardboard_v1.cc`, `sdk/qrcode/ios/device_params_helper.mm` | Viewer profile fields and distortion formula; licence is Apache-2.0 except `third_party/unity_plugin_api/` (Unity Companion License); Cardboard v1 bytes decoded here; QR URL handling | Kept, P |
| 15 | support.apple.com/en-us/111872 | iPhone 13 tech specs | 2532 x 1170 at 460 ppi, 6.1 inch; A15, 4-core GPU; three-axis gyro, accelerometer, magnetometer (digital compass) | Kept, P |
| 16 | Web search, then webkit.org | iOS 26 Open as Web App | WebKit's WWDC25 post: every site added to the Home Screen opens as a web app by default | Kept, P (post read) |
| 17 | Web search | iOS 27 compatible devices | Press coverage (MacRumors, AppleInsider, 9to5Mac, EveryMac) agrees: iPhone 11 and later, so the iPhone 13 runs iOS 27 | S (Apple's own list not read) |
| 18 | Web search, bugs.webkit.org | texImage2D video getUserMedia iOS slow or black | 226830 (NEW): 4.3 to 6.9 ms per `texImage2D` of a camera video on iPhone 12 Pro (iOS 14.4, 15.0); 230617 fixed; 235845 config changed; 206636 (NEW) stale frames | Kept, P (bug reports with measurements) |
| 19 | Web search, kuula.co/help/ios | web cardboard iPhone iOS 17/18 demo | Kuula (a 360 photo host) states it uses a software stereo fallback on iPhone, full window, not full screen, motion permission since iOS 13 | S (practitioner's own page, fetch-tool digest) |
| 20 | developer.apple.com/forums/thread/771270 | iOS 18 orientation permission | Unanswered question, no evidence either way | Set aside |
| 21 | App code (grep) | `tools/build_pwa.py`, `src/index.html`, `src/js/engine/sheets/present.js` | Manifest `display: standalone`; viewport has `viewport-fit=cover`; slideshow falls back when `requestFullscreen` is missing | Kept, P |

Downloads were kept in the scratchpad (`bcd/`, `web/`, `pkgs/` under the session's scratchpad directory), read as
text, never run.

## 3. Findings

### Q1. WebXR on an iPhone: none, in any version, and the code is not even compiled for iOS

- **F1.1 (P, high).** WebKit's build configuration defines `ENABLE_WEBXR 1` only when
  `PLATFORM(VISION) || (PLATFORM(MAC) && HAVE(COMPOSITOR_SERVICES))` (`PlatformEnableCocoa.h`, main branch,
  read 2026-11-23). `ENABLE_WEBXR_AR` on `PLATFORM(IOS)` is set equal to `ENABLE_WEBXR`, so it is off too. Safari
  on iOS is built from WebKit, so `navigator.xr` is not present on an iPhone. Reason for high: the build switch is
  unambiguous. Threat: Apple's internal SDK builds could differ; no evidence that they do.
- **F1.2 (P, high).** MDN's compatibility data (8.1.10) records `navigator.xr`, `XRSystem.isSessionSupported`
  and `requestSession` as `version_added: false` for Safari on iOS and for iOS WebViews.
- **F1.3 (P, high).** Apple's release notes add WebXR only for visionOS: Safari 18 "Added support for immersive
  WebXR in visionOS"; Safari 26.2 "Added WebGPU support for WebXR" and Safari 27's WebXR Layers fixes sit under
  "Spatial Web". Nothing in Safari 26, 26.2, 26.4 or 27 adds WebXR on iPhone.
- **F1.4 (P, high).** WebKit bug 208988 (the WebXR meta bug, 2020 to 2026): developers enabling the feature flags
  on an iPhone 12 Pro with iOS 15.6.1 (2022) and on iOS 16.4 (2023) found WebXR not detected or every session
  type unsupported; the bug was closed on 2026-04-01 with the note that Apple shipped WebXR for visionOS, and
  that recent work was "nothing related to iOS".
- **Counter-evidence sought:** searches for an iPhone `isSessionSupported('immersive-vr') === true`, for any
  iOS release note adding WebXR, and in WebKit source for an iOS enable. None found. An older Safari feature flag
  called "WebXR Device API" existed on iOS (2022 and 2023 reports), but by the bug reports it never produced a
  session; whether the toggle still appears in iOS 26 Settings is U and does not matter, since the code is not
  compiled.
- **Side finding (P).** Safari 27 adds the `<model>` element on iOS, iPadOS and macOS, and fixes `<a rel="ar">`
  wrapping `<model>` to enter AR Quick Look. This is a native USDZ viewer (and AR through Quick Look), not a
  stereo view or a WebXR session; it is a different path worth knowing for the main note.

### Q2. Orientation and motion: available after a tap, HTTPS only, gesture-bound, relative heading

- **F2.1 (P, high).** The permission API arrived in iOS 13: Apple's Safari 13 release notes, "Added a permission
  API on iOS for DeviceMotionEvent and DeviceOrientationEvent". Kuula's help page agrees ("Since iOS version
  13", S). **Disagreement:** MDN's data says `requestPermission` was added in Safari iOS 14.5. Apple's own note is
  the primary source; MDN's 14.5 is recorded and set aside. It does not matter for an iPhone 13, which runs iOS
  15 or later.
- **F2.2 (P, high).** The prompt appears only inside a user gesture. WebCore's access controller computes
  `mayPrompt = UserGestureIndicator::processingUserGesture(&document)`; the UI process returns the cached state
  without prompting when `!mayPrompt`. The W3C spec requires transient activation the same way. WebKit bug
  269706 (NEW, 2024) shows that a `postMessage` round trip to a worker inside the tap loses the gesture and the
  request is denied. So the call must be made synchronously in the tap handler, before any `await`.
- **F2.3 (P, high).** Secure context only: the IDL is `[SecureContext]`, and Safari 26.4 fixed the interfaces
  to be hidden outside secure contexts. GitHub Pages (HTTPS) qualifies; `http://` on the local network does not.
- **F2.4 (P, high).** The decision is cached per top-level origin in the website data store's memory
  (`m_deviceOrientationPermissionDecisions`), both granted and denied. Inference (U, to measure): a denial sticks
  until the app or Safari restarts, and a Home Screen app, which has its own data store, is asked again after
  each cold launch.
- **F2.5 (P, high).** On iOS the angles are relative: WebKit starts `CMMotionManager` device-motion updates
  without a reference frame argument (Core Motion's default is an arbitrary X with Z vertical, S from Apple's
  Core Motion docs as generally described; the WebKit call itself is P), converts the attitude matrix to
  Z-X'-Y'' angles, and dispatches from an `NSTimer` at `kMotionUpdateInterval = 1/60` s. `absolute` is not in the
  iOS IDL. A magnetic heading is offered separately as `webkitCompassHeading` (Core Location's
  `magneticHeading`, degrees from magnetic north) with `webkitCompassAccuracy`.
- **F2.6 (P, medium).** In a Home Screen web app: no WebKit bug was found reporting orientation events missing in a
  top-level standalone page on iOS 16 or later. The one iOS 26 regression found (bug 301294) is for iframes
  only. Medium, because absence of a bug is weaker than a test; it is item M2 in section 7.
- **F2.7 (P, high).** `deviceorientationabsolute` is not supported on iOS (MDN false); WebKit bug 271891 notes
  WebKit requires the "magnetometer" permissions-policy token for `deviceorientation` too (matters only in
  iframes).

### Q3. The back camera: works in Safari and in the Home Screen app since iOS 13.4, with known costs

- **F3.1 (P, high).** `getUserMedia` exists in Safari on iOS since 11 (MDN). In Home Screen apps it was missing
  until iOS 13.4: WebKit bug 185448, "With today's iOS and iPadOS 13.4 Beta, WebRTC (getUserMedia) should work as
  expected in home screen web apps", confirmed by the reporter on 13.4 beta 1.
- **F3.2 (P, high).** Permission in a Home Screen app does not persist: bug 215884 (hash-only navigation reset
  the permission; improved in 14.5; still reported on 18.5 in 2025) and bug 327237 (NEW, 2026-10-12, iOS 26 and
  27): the app asks again on every launch, and Safari's per-site "Allow" is not used by Home Screen apps. So the
  owner will tap Allow for the camera once per launch. Not a blocker, a nuisance. The app's router must not reset
  it by hash changes (to check: the app's own use of `location.hash`).
- **F3.3 (P, medium).** Bug 252465 (a PWA `<video>` sometimes never plays the camera stream) was fixed in WebKit
  on 2023-07-12 (265986@main); later comments report it gone on iOS 17 and 17.5. Medium: the fix's release
  version is not stated by Apple.
- **F3.4 (P, high for the facts, medium for today's numbers).** Getting frames into WebGL: the path is
  `<video playsinline muted>` with the stream as `srcObject`, then `texImage2D(video)` each frame (supported, MDN;
  Apple's Safari 17 notes also fixed the display going to sleep while the camera is on). Its cost on iOS is a
  known open problem: bug 226830 (NEW) measured 6.9 ms per upload on an iPhone 12 Pro with iOS 14.4 and 4.3 ms on
  iOS 15.0 ("WebGL via Metal"), against 0.4 ms on a Galaxy S10; `UNPACK_PREMULTIPLY_ALPHA_WEBGL` cut it to 4.5
  and 3.0 ms. Bug 206636 (NEW) reports stale frames under long frames. Uploads broke in betas twice (230617
  fixed; 235845). Medium, because the numbers are from iOS 14 and 15 and an iPhone 12 Pro: item M5.
- **F3.5 (P, high).** Newer frame APIs exist on iOS and may avoid the upload cost: `requestVideoFrameCallback`
  (15.4), `VideoFrame` (16.4), `MediaStreamTrackProcessor` (18). Whether WebGL accepts a `VideoFrame` as a
  texture source on iOS is not recorded by MDN (U).
- **F3.6 (U).** Resolution and frame rate of the back camera through `getUserMedia` on an iPhone 13 were not
  found in a primary source here (WebKit's capture source file could not be listed: the GitHub API for WebKit is
  not enabled in this session). `track.getCapabilities()` and `getSettings()` on the phone give the answer: M4.

### Q4. Full screen, wake lock, orientation

- **F4.1 (P, high). No element fullscreen on iPhone.** MDN: `Element.requestFullscreen` and its relatives on
  Safari iOS are "Only available on iPad, not on iPhone" (16.4 unprefixed, 12 prefixed). Apple's Safari 16.4
  note: "unprefixed Fullscreen API on macOS and iPadOS". WebKit bug 206854 "Add Fullscreen API to iOS" is NEW,
  with duplicates from iOS 26 (310661, March 2026) and as late as 2026-10-24; 212934 was closed WONTFIX on
  2026-01-25 in its favour. In WebKit, `FullScreenEnabled` is an embedder preference that Safari sets; it stays
  off on iPhone. Only `<video>` can go full screen on iPhone (`webkitEnterFullscreen`), which hides the page.
- **Counter-evidence sought:** Safari 26, 26.2, 26.4 and 27 notes searched for fullscreen: only fixes (26.4
  "`Element.requestFullscreen` on iOS ... hardware keyboard", which concerns iPad). None adds iPhone support.
- **F4.2 (P, high). The Home Screen web app is the way to a near-full-screen view.** Manifest `display:
  standalone` is supported since iOS 11.3; `display: fullscreen` is not (MDN false). Bug 264218 (NEW): an
  installed app reports `display-mode: fullscreen` even though the status bar is shown. Since iOS 26, every site
  added to the Home Screen opens as a web app by default (WebKit's WWDC25 post, P). The app already builds a
  manifest with `display: standalone` (`tools/build_pwa.py:123`) and a viewport with `viewport-fit=cover`
  (`src/index.html:5`). Whether the status bar shows in landscape in the installed app, and how much of the screen
  the safe area takes around the notch, is M3.
- **F4.3 (P, high). Screen Wake Lock.** Safari 16.4 added it; it did not work in Home Screen apps (bug 254545:
  "Home Screen Web Apps ... are not UIApplications but ViewServices") until Safari 18.4: "Fixed Wake Lock API for
  Home Screen Web Apps". MDN agrees (full support from 18.4). The cardboard libraries used a hidden looping video
  (NoSleep) instead; on iOS 18.4 or later that is unnecessary. A live camera also keeps the display awake (Safari
  17 note).
- **F4.4 (P, high). No orientation lock.** `screen.orientation.lock()` and the manifest `orientation` member are
  not supported on Safari iOS (MDN false; bug 208988 comments). `screen.orientation.type`, `.angle` and `change`
  exist since 16.4 (Apple note), `window.orientation` still exists (deprecated). Consequence: if the owner's
  rotation lock is on, the page stays portrait while the phone is in landscape in the viewer; the app must then
  draw the two eyes rotated 90 degrees in a portrait canvas, or ask the user to turn rotation lock off.

### Q5. Drawing stereo and reading the head

- **F5.1 (P, high).** three.js (MIT) `StereoCamera` (core, `src/cameras/StereoCamera.js`) makes two cameras from
  one: eye separation `eyeSep` 0.064 m, off-axis projection after Paul Bourke, shifting each eye by half the
  separation and skewing the frustum toward a `focus` distance. `StereoEffect` (examples, about 40 lines) renders
  each camera into one half of the canvas with scissor and viewport. Neither does lens distortion or uses a viewer
  profile. The app's pinned three.js build (`runtime/three/0.186.1/bim-three.min.js`) already contains
  `StereoCamera` (string found in the file); `StereoEffect` is not in it but is small enough to write in ES5.
  three.js no longer ships `DeviceOrientationControls` (not in 0.186.1).
- **F5.2 (P, high). The viewer profile.** Cardboard SDK (`googlevr/cardboard`, Apache-2.0 for everything except
  `third_party/unity_plugin_api/`, which is under the Unity Companion License and must not be used)
  `proto/cardboard_device.proto` `DeviceParams`: `screen_to_lens_distance`, `inter_lens_distance`,
  `left_eye_field_of_view_angles` (left, right, bottom, top, degrees), `vertical_alignment` (BOTTOM, CENTER, TOP),
  `tray_to_lens_distance`, `distortion_coefficients`, `primary_button`; lengths in metres. Distortion:
  `p' = p (1 + K1 r^2 + K2 r^4 + ...)` with r in tan-angle units. A viewer's QR code holds a URL whose `p` query
  parameter is the URL-safe base64 protobuf (`device_params_helper.mm`), or a short link that redirects to it.
- **F5.3 (P, high, measured here).** The Cardboard v1 profile bytes in `sdk/qrcode/cardboard_v1/cardboard_v1.cc`
  decode to: screen-to-lens 0.042, inter-lens 0.060, FOV 40/40/40/40, tray-to-lens 0.035, K = [0.441, 0.156],
  bottom alignment, magnet button. They match `cardboard-vr-display`'s `CardboardV1` exactly (independent copy).
  Its `CardboardV2` (2015, the default) is 0.039, 0.064, FOV 60, 0.035, K = [0.34, 0.55]. Script: a 20-line
  protobuf varint/fixed32 decoder in Python over the byte list, run 2026-11-23, one run (deterministic).
- **F5.4 (P, high). How the web polyfill did barrel distortion.** `cardboard-vr-display` 1.0.19 (Apache-2.0,
  last published 2022, used by `webvr-polyfill` 0.10.12 and `webxr-polyfill` 2.0.3, both Apache-2.0): render both
  eyes to an offscreen buffer, then draw a 20 x 20 vertex mesh per eye whose positions are pre-distorted on the
  CPU: for each grid point the lens-space radius is run through the inverse of the polynomial (secant method,
  `distortInverse`), so the texture is drawn barrel-shaped and the lens's pincushion cancels it. Each eye's
  frustum is asymmetric, from the profile and the screen size in metres (`getLeftEyeVisibleTanAngles`). The code
  carries a FIXME saying a factor of 2 was found by eye. The method (a distortion mesh) is what the Cardboard SDK
  does too; it costs one extra pass of a small mesh.
- **F5.5 (P, high, computed here).** iPhone 13 screen: 2532 x 1170 px at 460 ppi (Apple) = 139.8 x 64.6 mm,
  844 x 390 CSS px at device pixel ratio 3. Each eye's half is 69.9 mm wide, so the lens centres (60 or 64 mm
  apart) sit 5.0 mm (v1) or 3.0 mm (v2) inward of the half centres. With the v2 profile and a 4 mm bezel (the
  library's default, unknown for the iPhone 13), the visible field per eye is about 60 outer, 51 inner, 50 down,
  54 up degrees. So symmetric `StereoEffect` halves do not line up with the lenses; each eye needs the asymmetric
  frustum from the profile. The notch's region in landscape falls in one eye's outer edge.
- **F5.6 (P, high). Head orientation formula.** The W3C spec defines alpha, beta, gamma as intrinsic Tait-Bryan
  angles Z-X'-Y'' on the device frame (x right, y up the screen, z out of the screen, portrait natural
  orientation). The standard conversion (three.js's former `DeviceOrientationControls`, MIT, as vendored in
  A-Frame 1.8): `q = Euler(beta, alpha, -gamma, 'YXZ')`, then multiply by a -90 degree rotation about X (the
  camera looks out of the back of the phone), then by a rotation of minus the screen angle about Z
  (`screen.orientation.angle`, or `window.orientation`). Gotchas: (a) WebKit picks among four branches by the
  sign of R[8] (the screen normal's vertical component) when extracting angles, and the cardboard pose holds the
  screen vertical, R[8] near 0; the angles can jump by 180 degrees there while the rotation they describe stays
  the same, so build the quaternion from each consistent triple and never filter the three angles separately
  (inference from the code: to observe, M2); (b) alpha's zero is arbitrary at start and drifts slowly (no
  magnetometer correction in `deviceorientation` on iOS); `webkitCompassHeading` can re-anchor yaw if wanted,
  with magnetic interference near steel; (c) events come at most 60 per second from a timer, so a frame can show
  orientation up to about 17 ms old; `cardboard-vr-display` added a gyro-based predictor from `devicemotion`.
- **F5.7 (P, medium).** `cardboard-vr-display` adapts to iOS with an iOS-specific filter frame (a different
  rotation of the complementary filter) and a workaround for a `devicemotion` regression in Safari 13.4; it never
  calls `requestPermission`, so on iOS 13 or later the page must request permission itself first.

### Q6. Prior art

- **F6.1 (P, high).** A-Frame 1.8.0 (MIT, June 2026): `enterVR` on a mobile device without WebXR throws "Failed to
  enter VR mode no WebXR". So current A-Frame has no cardboard stereo on iPhone; it keeps a permission button
  (`device-orientation-permission-ui`) and a "magic window" (mono, orientation-driven) view.
- **F6.2 (P, high).** Google's `webxr-polyfill` 2.0.3 offers a `CardboardXRDevice` on mobile when
  `config.cardboard` is set, built on `cardboard-vr-display`, whose present path on iOS is "*sigh* Just fake it":
  no fullscreen, wake lock by NoSleep. All three packages were last published in 2022 and do not request the
  motion permission themselves.
- **F6.3 (S, medium).** Kuula states it renders stereo in software on iPhone for cardboard headsets, in full
  window because "web browsers on the iPhone do not support the Fullscreen API", after a motion permission
  "since iOS version 13". Read through the fetch tool's digest; no version tested is named.
- **F6.4 (U).** No current, verifiable iOS 17 or later web cardboard demo was found and tested. Forum reports
  (Babylon.js, PlayCanvas, Cesium) are mixed and old; they are pointers only.

## 4. Counter-evidence sought, summarised

- H1: an iOS release note, a WebKit enable, or a report of `isSessionSupported` true on iPhone. None; the build
  switch excludes iOS.
- H2: bugs on orientation or camera missing in standalone mode on iOS 16 or later. Found only nuisances (camera
  permission per launch; gesture loss through a worker; iframe-only regression on iOS 26; old PWA video bug fixed
  2023). No report of either missing at the top level.
- H3: any WebKit or Apple note shipping element fullscreen on iPhone up to Safari 27.2. None; the canonical bug is
  open as of 2026-10-24.

## 5. Outcome of the hypotheses

- **H1: holds (P, high).** No immersive WebXR on iPhone in iOS 17, 18, 26 or 27; WebKit does not compile WebXR
  for iOS. The app must draw cardboard stereo itself (two eye views, lens correction, head pose from
  `deviceorientation`).
- **H2: holds, with conditions (P, high for the APIs; medium for standalone orientation until M2).** Orientation:
  yes, after `DeviceOrientationEvent.requestPermission()` called synchronously in a tap, over HTTPS, relative yaw,
  60 per second. Camera: yes in Safari and in the Home Screen app (since 13.4), but the Home Screen app asks for
  camera permission again at each launch (bug 327237, open), and `texImage2D` from a camera video has cost about
  3 to 7 ms per frame on recent iPhones (bug 226830, open).
- **H3: holds (P, high).** No element fullscreen on iPhone through Safari 27. The Home Screen web app
  (`display: standalone`) removes Safari's interface; the status bar and safe areas remain to be measured. Wake
  Lock works in the Home Screen app from iOS 18.4. Orientation cannot be locked.

## 6. Surprises

1. WebXR is not merely disabled on iOS: `ENABLE_WEBXR` is compiled only for visionOS and Macs with compositor
   services. A feature flag cannot bring it back.
2. MDN dates the motion permission API to iOS 14.5; Apple's own Safari 13 notes date it to iOS 13.
3. Since iOS 26 any site added to the Home Screen opens as a web app; from 18.4 Wake Lock works there.
4. A-Frame, the usual answer for web cardboard, no longer does cardboard on iPhone (1.8 requires WebXR), and
   Google's polyfills are unmaintained since 2022.
5. Camera permission in a Home Screen app is asked on every launch (still open in October 2026).
6. The cardboard lenses are not centred on the halves of an iPhone 13 screen (3 to 5 mm off), so a plain
   side-by-side split is visibly wrong without asymmetric frusta.
7. Safari 27 brings `<model>` (USDZ, with AR Quick Look) to iPhone: a native AR viewer reachable from a page.

## 7. What must be measured on the owner's iPhone 13

- **M1.** iOS version (Settings, General, About). The findings assume iOS 26 or 27.
- **M2.** In Safari and in the Home Screen app, over HTTPS: `typeof DeviceOrientationEvent.requestPermission`,
  the prompt on a tap, the event rate (events per second), alpha/beta/gamma held upright in landscape (watch for
  the 180 degree jumps of F5.6), yaw drift over 5 minutes at rest, `webkitCompassHeading` values, and whether
  permission is asked again after closing the app from the App Switcher.
- **M3.** In the Home Screen app in landscape: `innerWidth`, `innerHeight`, `devicePixelRatio`,
  `env(safe-area-inset-*)`, whether the status bar shows, `matchMedia('(display-mode: standalone)')` and
  `fullscreen` (bug 264218), `screen.orientation.angle`; with rotation lock on and off.
- **M4.** `getUserMedia({video:{facingMode:{exact:'environment'}}})` in Safari and in the Home Screen app:
  success, `track.getCapabilities()` and `getSettings()` (width, height, frameRate), re-prompt at each launch.
- **M5.** Time per `texImage2D(video)` per frame (and with `UNPACK_PREMULTIPLY_ALPHA_WEBGL`), and whether
  `requestVideoFrameCallback` fires at the camera's rate; whether WebGL accepts a `VideoFrame` from
  `MediaStreamTrackProcessor` as a texture source.
- **M6.** `navigator.wakeLock.request('screen')` in the Home Screen app: granted, and whether the screen stays on
  for 10 minutes without touches.
- **M7.** The owner's viewer: its QR code (the URL, from which the profile can be decoded), or, failing that, its
  lens spacing, lens-to-screen distance and tray height measured with a ruler; whether the phone sits against a
  bottom tray; whether it has a button (magnet or touch lever).
- **M8.** Frame rate of a two-eye render of a modest model with the distortion pass, with and without the camera
  texture (feeds H6).
- **M9.** Whether `navigator.xr` is undefined (confirms F1.1 on the device).

These belong in the iPhone test page the main note plans in `docs/research/experiments/`.

## 8. Still open (U)

- The back camera's resolution and frame rate through `getUserMedia` on an iPhone 13 (M4).
- Whether orientation permission in a Home Screen app is asked at every launch (inferred from WebKit's in-memory
  cache, M2).
- The iPhone 13's bezel offset from the tray in a viewer (`bevelMeters`); the library's 4 mm default is a guess.
- Whether WebGL on iOS accepts `VideoFrame` as a texture source (M5).
- Whether the old "WebXR Device API" toggle still appears in iOS 26 Settings (irrelevant to the outcome).
- Apple's own iOS 27 device list was not read; the iPhone 13's support is S from four outlets agreeing.
- No independent second reader has re-checked these facts yet (protocol step 9): to do before code uses them.

## 9. References

All read 2026-11-23.

| Source | URL | What was read | Level |
|---|---|---|---|
| MDN browser-compat-data 8.1.10 (npm, 2026-11-19) | https://www.npmjs.com/package/@mdn/browser-compat-data | `data.json`: api.XRSystem.*, Navigator.xr, DeviceOrientationEvent (+requestPermission, absolute), DeviceMotionEvent.requestPermission, MediaDevices.getUserMedia, Element.requestFullscreen and the fullscreen family, WakeLock, ScreenOrientation (+lock), manifests.webapp.display (+fullscreen, standalone), manifests.webapp.orientation, HTMLVideoElement.requestVideoFrameCallback, VideoFrame, MediaStreamTrackProcessor, css display-mode notes; browsers.safari_ios releases | P (of MDN's records) |
| WebKit source, PlatformEnableCocoa.h | https://github.com/WebKit/WebKit/blob/main/Source/WTF/wtf/PlatformEnableCocoa.h | ENABLE_WEBXR, ENABLE_WEBXR_AR, ENABLE_FULLSCREEN_API, ENABLE_DEVICE_ORIENTATION | P |
| WebKit source, UnifiedWebPreferences.yaml | https://github.com/WebKit/WebKit/blob/main/Source/WTF/Scripts/Preferences/UnifiedWebPreferences.yaml | FullScreenEnabled, WebXREnabled, WebXRAugmentedRealityModuleEnabled, DeviceOrientation* | P |
| WebKit source, WebPreferencesDefaultValues.cpp | https://github.com/WebKit/WebKit/blob/main/Source/WebKit/Shared/WebPreferencesDefaultValues.cpp | defaultDeviceOrientationPermissionAPIEnabled, fullscreen defaults | P |
| WebKit source, WKPreferences.mm; Apple doc isElementFullscreenEnabled | https://github.com/WebKit/WebKit/blob/main/Source/WebKit/UIProcess/API/Cocoa/WKPreferences.mm ; https://developer.apple.com/documentation/webkit/wkpreferences/iselementfullscreenenabled | elementFullscreenEnabled maps to FullScreenEnabled; iOS 15.4+ (relevant to a native shell, not tested on iPhone) | P |
| WebKit source, DeviceOrientationAndMotionAccessController.cpp | https://github.com/WebKit/WebKit/blob/main/Source/WebCore/dom/DeviceOrientationAndMotionAccessController.cpp | user-gesture check, per-origin state | P |
| WebKit source, WebDeviceOrientationAndMotionAccessController.cpp | https://github.com/WebKit/WebKit/blob/main/Source/WebKit/UIProcess/WebsiteData/WebDeviceOrientationAndMotionAccessController.cpp | cached decisions per main-frame origin | P |
| WebKit source, DeviceOrientationEvent.idl | https://github.com/WebKit/WebKit/blob/main/Source/WebCore/dom/DeviceOrientationEvent.idl | SecureContext, requestPermission, webkitCompassHeading on iOS | P |
| WebKit source, WebCoreMotionManager.mm (+.h) | https://github.com/WebKit/WebKit/blob/main/Source/WebCore/platform/ios/WebCoreMotionManager.mm | 1/60 s interval, attitude to Euler, magneticHeading | P |
| Apple, Safari release notes 13, 16.4, 17, 17.4, 18, 18.4, 26, 26.2, 26.4, 27 | https://developer.apple.com/documentation/safari-release-notes | Full text searched for WebXR, fullscreen, wake lock, orientation, getUserMedia, camera, Home Screen, permission | P |
| WebKit blog, News from WWDC25 | https://webkit.org/blog/16993/news-from-wwdc25-web-technology-coming-this-fall-in-safari-26-beta/ | "Every site can be a web app on iOS and iPadOS" | P |
| WebKit bug 208988 | https://bugs.webkit.org/show_bug.cgi?id=208988 | All 46 comments | P |
| WebKit bugs 206854, 212934, 310661 | https://bugs.webkit.org/show_bug.cgi?id=206854 (and ids) | Status, comments 1 to 15 | P |
| WebKit bug 254545 | https://bugs.webkit.org/show_bug.cgi?id=254545 | Wake Lock in Home Screen apps, all comments | P |
| WebKit bug 264218 | https://bugs.webkit.org/show_bug.cgi?id=264218 | display-mode in installed apps | P |
| WebKit bugs 185448, 215884, 252465, 327237 | https://bugs.webkit.org/show_bug.cgi?id=185448 (and ids) | getUserMedia in Home Screen apps, all comments | P |
| WebKit bugs 226830, 230617, 235845, 206636 | https://bugs.webkit.org/show_bug.cgi?id=226830 (and ids) | camera video to WebGL texture, measurements and status | P |
| WebKit bugs 269706, 271891, 221399, 213966, 283803, 301294 | https://bugs.webkit.org/show_bug.cgi?id=269706 (and ids) | motion permission edge cases | P |
| W3C Device Orientation and Motion (editor's draft source) | https://github.com/w3c/deviceorientation/blob/main/index.bs | Device Orientation model, requestPermission steps, absolute vs relative, Appendix A | P |
| three.js 0.186.1 (MIT) | https://www.npmjs.com/package/three | src/cameras/StereoCamera.js, examples/jsm/effects/StereoEffect.js, LICENSE | P |
| App's three build | runtime/three/0.186.1/bim-three.min.js | contains StereoCamera | P |
| cardboard-vr-display 1.0.19 (Apache-2.0) | https://www.npmjs.com/package/cardboard-vr-display | src/distortion.js, device-info.js, cardboard-distorter.js, base.js, pose-sensor.js, sensor-fusion/*, util.js | P |
| webvr-polyfill 0.10.12, webxr-polyfill 2.0.3 (Apache-2.0) | https://www.npmjs.com/package/webxr-polyfill | src/devices.js (cardboard selection); licence; no requestPermission | P |
| A-Frame 1.8.0 (MIT) | https://www.npmjs.com/package/aframe | src/core/scene/a-scene.js (enterVR), src/components/look-controls.js, scene/device-orientation-permission-ui.js, vendor/DeviceOrientationControls.js, vendor/wakelock | P |
| Google Cardboard SDK (Apache-2.0 except third_party/unity_plugin_api) | https://github.com/googlevr/cardboard | LICENSE, proto/cardboard_device.proto, sdk/qrcode/cardboard_v1/cardboard_v1.cc, sdk/qrcode/ios/device_params_helper.mm | P |
| Apple, iPhone 13 Tech Specs | https://support.apple.com/en-us/111872 | display, chip, sensors | P |
| Kuula help, iOS | https://kuula.co/help/ios | VR on iPhone, fullscreen, motion permission (fetch-tool digest) | S |
| iOS 27 device support (MacRumors, AppleInsider, 9to5Mac, EveryMac) | https://www.macrumors.com/2026/09/14/ios-27-compatible-iphones/ ; https://appleinsider.com/articles/26/06/08/ios-27-keeps-iphone-11-and-newer-compatibility | search summaries agreeing; Apple's list not read | S/U |
| Apple Developer Forums 771270; Babylon.js, PlayCanvas, Cesium forum posts | https://developer.apple.com/forums/thread/771270 | pointers only | U |
| App code | tools/build_pwa.py:123, src/index.html:5, src/js/engine/sheets/present.js:98-101 | manifest display, viewport, fullscreen fallback | P |
