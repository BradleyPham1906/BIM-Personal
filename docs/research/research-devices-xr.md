# Research: the app on a phone in a cardboard headset, with hands and physics

Started 2026-11-23 by Claude, at the owner's request ("i want to be able to hand track and interact with objects
in my world bim with physics like real world", on an iPhone 13 and a cardboard viewer; the owner has a MacBook Air).
Follows `docs/research/research-protocol.md`. The topic notes are in `docs/research/research-devices-xr/`.

Status: **research done except the phone measurements** (part 6, E3). The four topic notes and the independent check
are in `research-devices-xr/`; the owner's decisions are asked in part 11.

## 1. Abstract

Can an iPhone 13 in a cardboard viewer show the BIM model in stereo, see the owner's hands through its back camera, and
let them push and pick up model elements with real physics? In the browser, very probably yes, with one limit: Safari
on an iPhone has no WebXR (P, high), so the app draws both eyes itself, on the lenses of the owner's viewer, and the
head is tracked in rotation only (3DoF) from the motion sensors (P, high). Hands come from MediaPipe's hand landmarker
(Apache-2.0, no shared memory, iOS 16.4+, GPU in a worker from iOS 17; P, high), and the physics from the Jolt engine
the app already ships for walk mode (P, high): no new physics library. Whether all of it holds 30 frames a second on
an A15 is unknown; no one has published it, so the iPhone test page measures it (E3). If the browser falls short, the
owner's Mac opens the next step: the same web app inside a Capacitor shell with one small Swift plugin of ours for
ARKit's 6DoF tracking and native hand points, free to install on the owner's own phone for 7 days at a time. Godot
and Swift were weighed and set aside: both throw away the engine. The splat edits the videos showed fit a LOD-G2
phase on v205's own renderer, and the owner's devices can be linked by QR codes over WebRTC with no server of ours.
**Recommendation:** the web path, in four phases (part 5), started only after the phone's numbers are in.

## 2. The question and the hypotheses

**The question.** Can the owner's iPhone 13, in a cardboard viewer, show the BIM model in stereo, see the owner's
hands through its back camera, and let the hands grab and push model elements with rigid-body physics, at a frame
rate that is comfortable? And which way of building it serves that best: the web app as it is (Safari, the
installed web app), the web app in a native shell (Capacitor), or a separate native app (Godot or Swift), given
the owner's MacBook Air, no paid Apple developer account, and the reuse-first rule?

**What a good answer looks like.** A recommended path with its measured limits on an iPhone 13, the libraries it
needs (licence, size, pinned), the first phases with their tests, and the owner's decisions.

**Hypotheses** (each to be confirmed or refuted, with its evidence):

| Id | Hypothesis | What would refute it |
|---|---|---|
| H1 | Safari on iOS offers no immersive WebXR session on an iPhone, so cardboard stereo must be drawn by the app itself. | A WebKit release note or a test showing `navigator.xr.isSessionSupported('immersive-vr')` true on an iPhone. |
| H2 | Safari on iOS gives the page the phone's orientation (after a permission tap) and the back camera (`getUserMedia`), also in the installed web app. | WebKit bugs or tests showing either missing in standalone mode on iOS 16 or later. |
| H3 | An iPhone page cannot go truly full screen (the Fullscreen API on iPhone covers video only); the installed web app is the way to a full-screen view. | WebKit shipping element fullscreen on iPhone. |
| H4 | MediaPipe's hand landmarker (JavaScript, Apache-2.0) runs in Safari on an A15 at 20 frames a second or more. | Reports or a measurement below that, or a failure on iOS Safari. |
| H5 | A rigid-body engine for the browser (Rapier, cannon-es or Jolt) runs in iOS Safari without cross-origin isolation, under a permissive licence, at an acceptable download size. | Each candidate needing SharedArrayBuffer, or a licence outside the library rule. |
| H6 | The camera, hand tracking, physics and two eye views together hold 30 frames a second or more on an iPhone 13 for a modest model. | A measurement on the owner's phone below it, or sustained heat throttling. |
| H7 | A native build (Capacitor shell, Godot, or Swift) gives what the browser cannot: ARKit's six-degree tracking and Apple Vision's hand pose; with Xcode and a free Apple ID it installs on the owner's own phone for 7 days at a time. | Apple's documentation saying otherwise, or Vision hand pose unavailable on the A15. |
| H8 | Godot can only show the BIM model through an export (glTF or IFC); its iOS hand-tracking plugins are not maintained or not working on iOS. | A maintained Godot iOS plugin with hand pose, tested on iOS. |
| H9 | Region edits on a splat (select by a box or a pinch, hide, delete, move) are feasible in the browser for 1,000,000 splats on a phone. | Measurements or prior art showing it unworkable at that size. |
| H10 | Two of the owner's devices can be linked (the phone as the headset, the laptop as the editor) without a server of ours, by a QR code. | WebRTC needing a signalling server we would have to run, with no workable manual alternative. |

## 3. Method

Four researchers in parallel, one topic each, each writing its note in `docs/research/research-devices-xr/`:

- `web-on-iphone.md`: WebXR, orientation, camera, full screen, stereo drawing and lens correction in Safari on
  iOS; prior art (H1 to H3).
- `hands-and-physics.md`: hand tracking in the browser and on iOS, pinch detection, rigid-body engines, the
  physics hand (H4 to H6).
- `native-paths.md`: Capacitor, Godot and Swift on iOS; Apple's free provisioning; ARKit and Vision (H7, H8).
- `splats-and-link.md`: splat editing in the browser (LOD-G2) and the device link (H9, H10).

Then an iPhone test page in `docs/research/experiments/` for the owner to open on the phone (H4, H6), and an
independent second reader re-checking every fact the code would use.

## 2a. The outcome of each hypothesis

| Id | Outcome | Evidence |
|---|---|---|
| H1 | **Held** (P, high). WebXR is compiled only for visionOS and Macs; `navigator.xr` is absent on an iPhone. | web-on-iphone F1; confirmed by the check |
| H2 | **Held, with conditions** (P). Orientation after `requestPermission()` in a tap, HTTPS, up to 60 events a second, yaw from an arbitrary zero. The back camera works in the Home Screen app since iOS 13.4; a re-prompt at each launch is reported by users (S, medium). | web-on-iphone F2, F3; check |
| H3 | **Held** (P, high). No element fullscreen on iPhone; the Home Screen app is the full-screen way (by default for every site from iOS 26); Wake Lock there from iOS 18.4. | web-on-iphone F4; check |
| H4 | **Open, plausible.** No figure exists for MediaPipe 1.2.3 in Safari on an iPhone; the older library gave 5 to 8 fps on an iPhone 11 and 6 to 7 on a 13 Pro (2021-22); natively the model runs in 5.3 ms. | hands-and-physics 4.1; to measure (E3) |
| H5 | **Held** (P, high), and better than hoped: the app's own Jolt 1.1.1 (single-thread, no shared memory) serves. Rapier is the fallback; cannon-es lacks continuous collision; ammo.js is zlib, outside the rule. | hands-and-physics 4.4; check |
| H6 | **Open.** No combined measurement anywhere; an iPhone 13 keeps about 74 to 78 % of its GPU speed under sustained load (benchmark sites, S). | to measure (E3, 10 to 20 minutes) |
| H7 | **Mostly held** (P). ARKit gives 6DoF on the iPhone 13 without LiDAR; a free Apple ID installs for 7 days (3 apps, 3 devices). Two corrections: no plugin exists, we write one; Apple's Vision hand pose is 2D. | native-paths 3.1 to 3.3; check |
| H8 | **Held in part.** Godot gets the model only by GLB (which the app exports). Its plugins exist, MIT, updated in 2026, but none shows hand pose on an iPhone; its cardboard mode is 3DoF and unmaintained. | native-paths 3.4; check |
| H9 | **Held, with conditions** (medium). Box, sphere and colour selection on 1,000,000 splats in 7 to 11 ms on this machine's CPU, reproduced by the check; the "grow" worst case (2.2 s) was not reproducible from the committed script and is U. The phone is not measured. | splats-and-link A3, E2; check |
| H10 | **Held** (medium-high). Signalling is left to the application (RFC 9429, which replaced RFC 8829); an offer fits one QR code; on one Wi-Fi no STUN is needed. Not yet tried between the owner's iPhone and Mac. | splats-and-link B1, E1; check |

## 4. Findings, by topic

Each topic note holds its findings with their sources, levels and confidence; the independent check
(`research-devices-xr/independent-check.md`) re-read every fact the code or a decision relies on and its corrections
are applied here. The findings that decide the plan:

**The web on an iPhone** (`web-on-iphone.md`).
- No WebXR, so the app draws two eyes itself. A plain side-by-side split is wrong: on an iPhone 13 the lenses sit
  3 mm (Cardboard v2) to 5 mm (v1) inward of each half's centre, so each eye is placed on its lens from the viewer's
  profile (inter-lens and screen-to-lens distances, tray height, K1 and K2), which the viewer's QR code holds (P).
- The head: alpha, beta, gamma to a quaternion by the standard formula; never filter the three angles separately,
  as they can jump by 180 degrees while the rotation stays the same (P for the formula; the jump is inferred from
  WebKit's code, to observe).
- No reusable library: A-Frame 1.8 throws on an iPhone without WebXR; Google's cardboard polyfills stopped in 2022
  and never ask the motion permission. The Cardboard SDK's lens figures (Apache-2.0, not its `third_party/unity_plugin_api/`)
  are what we take.
- Copying each camera frame into WebGL cost 2.5 to 4.3 ms on an iPhone 12 Pro Max (WebKit bug 226830, iOS 15; S).

**Hands and physics** (`hands-and-physics.md`).
- MediaPipe Tasks Vision 1.2.3 and its float16 hand model (7.8 MB; SHA-256 `fbc2a300...07cde1`), Apache-2.0 for both
  (P, the model card read by the check). About 10 MB gzipped to download, 23 MB to commit under `runtime/`.
- Depth from one camera needs a one-time calibration: the browser does not give the focal length. With the user's
  measured hand, a 2023 study reports about 1.5 cm error at 75 cm (S: read through a summary; whether a median is not
  stated); with the model's default hand, errors near 28 cm at a larger distance (S).
- Jitter: our own One Euro filter (Casiez et al. 2012, P). Pinch with two thresholds, in about 2 to 2.5 cm, out about
  3 to 5 cm, from depth-sensing toolkits, to retune on the phone.
- The physics hand: hand bodies that collide, driven each step toward the tracked hand by velocity, with continuous
  collision, a speed cap, and a reset when they fall too far behind; pinch to grab. Hands that only follow the
  tracking pass through things and destabilise the engine. The check's correction: Ultraleap's soft-contact hand
  turns collisions off when far or grabbing, and its hard-contact hand teleports and ghosts; ours takes the reset
  from the second and keeps collisions on, so it is our own blend, and is named as such.

**Native paths** (`native-paths.md`).
- Free provisioning: 7-day installs, 3 apps per device, 3 devices, 10 App IDs, no TestFlight; no camera or ARKit
  entitlement is needed (P). Xcode 27 needs macOS Tahoe, so an M1 (2020) or later MacBook Air; the Intel 2020 Air stops
  at Xcode 26.3, still enough for Capacitor 8 (P).
- The Mac helps now: Safari's Web Inspector on the iPhone, with no developer account.
- ARKit hand tracking is visionOS only; on an iPhone, hand points come from Vision (2D) or MediaPipe's native
  landmarker (3D world landmarks).

**Splats and the link** (`splats-and-link.md`).
- Spark 2.4.0 (MIT, three.js) is the one maintained library that edits splats in our kind of view; SuperSplat
  (MIT) has the best tools but runs on WebGPU only. glTF `KHR_gaussian_splatting` is ratified; its SPZ compression
  extension is not on Khronos's main branch.
- For v205: WO-05's comparison sort is fine as a test reference, but the sort each frame (WO-06) must be a 16-bit
  counting sort in a worker (about 25 ms against 595 ms at 1,000,000 splats here). Recorded in v205's SPEC.
- With BIM: opaque elements first, then splats with depth test on and depth write off; section cuts as a per-splat
  discard in the shader.
- The link: draw the head pose on the phone from its own sensor (comfortable VR needs about 20 ms from movement to
  picture: Meta, S); the link carries only edits and a mirrored pose, which tolerate about 100 ms.

## 5. The alternatives compared

Criteria: what it gives the owner's goal (stereo, tracking, hands with depth, physics); cost in money and hardware;
how much of the existing engine it reuses (the reuse-first rule); licence fit; effort; how updates reach the phone.

| | Web app (Safari, Home Screen) | Capacitor shell + our Swift plugin | Godot 4 | Swift + RealityKit |
|---|---|---|---|---|
| Money | none | none (free Apple ID) | none | none |
| Mac | not needed (helps: Web Inspector) | Xcode 26+ | Xcode | Xcode |
| Head tracking | 3DoF, motion sensors | 6DoF, ARKit | 3DoF (unmaintained); 6DoF only through a plugin | 6DoF, ARKit |
| Hands | MediaPipe in the page, 3D | MediaPipe native (3D) or Vision (2D) | GDMP, untested on iOS | Vision or MediaPipe |
| Physics | Jolt, already in the app | the same Jolt | Godot's Jolt | RealityKit |
| Reuse of the engine | all | all; native only for pose and hands | none (model by GLB) | none (GLB to USD) |
| Effort | lowest | one small plugin, a rebuild each week | a second app | the largest |
| Updates | instant | reinstall from the Mac every 7 days | same | same |
| Who can use it | anyone with the link | the owner's 3 devices, until $99 a year | same | same |

**Recommendation: the web app first, then the Capacitor shell only if the phone's numbers fail.** In four phases,
each written as a work order after the owner's decisions and the phone's numbers:

1. **XR-1, the headset view:** a "Headset" mode of the rendered view: two eyes on the viewer's lenses (profile from
   its QR code or entered), the head from the motion sensors, the camera behind as an option, from the Home Screen
   app with the wake lock. Joins walk mode (v203, v208 to v211) for moving about.
2. **XR-2, hands:** MediaPipe vendored under `runtime/` (library rule), in a worker, our One Euro filter, a one-time
   calibration of focal length and hand span, pinch with hysteresis.
3. **XR-3, the physics hand:** Jolt's dynamic bodies beside `walk-physics.js`: hand bodies driven by velocity,
   elements the owner marks movable become dynamic bodies with mass from their material, pinch to grab, release
   with the hand's speed; the rest of the model stays one static body.
4. **XR-4, the link and LOD-G2:** phone and laptop by QR codes over WebRTC; splat edits (box and sphere hide and
   delete, then colour and grow, then move) on v205's renderer.

## 6. The experiments

- **E1, E2 (splats-and-link.md part 6):** an offer's SDP fits one QR code (572 base64 characters); 1,000,000 splats
  select by box, sphere or colour in 7 to 11 ms on this machine's CPU, and v205 WO-05's comparison sort takes about
  595 ms against 24.5 ms for a 16-bit counting sort. Scripts: `experiments/devices-xr/sdp.html`, `splat_cost.js`.
- **E3, the iPhone test page** (`experiments/devices-xr/phone-test.html`, published by `tools/build_site.py` at
  `/lab/phone-test.html` once on `main`): the device (M1, M3, M9), the motion sensors and their drift (M2), the back
  camera and its per-frame texture copy (M4, M5), the wake lock (M6), Jolt's step time with a 20,000 or 100,000
  triangle model (hands-and-physics.md 9.3), MediaPipe on GPU and CPU (9.1), the viewer's profile or QR address (M7),
  and the headset view: two eyes on the lenses with the barrel correction, the camera behind, a table of 20 blocks in
  Jolt pushed by six hand bodies and picked up by a pinch, the frame rate logged each minute (M8, H6). Results are
  copied as JSON for the note. three.js and Jolt come from the site's `runtime/`; MediaPipe 1.2.3 and its model are
  fetched from pinned addresses for this page only (the model's SHA-256 checked here, `fbc2a300...07cde1`), since
  they are not vendored before the owner's approval.
  Checked once in headless Chromium here (software drawing, so no speed figures): every step runs with no page
  error; at the iPhone 13's 3x scale both eyes fall on the lens centres and the blocks settle on the table.
  **Waiting on the owner's phone.**

## 7. Edges

- **iOS versions:** hand mode needs iOS 16.4 (SIMD) and, for the GPU in a worker, iOS 17; the check found MediaPipe's
  Safari-version test can pass wrongly on iOS 16.x Home Screen apps, so the app checks iOS 17 itself.
- **The viewer:** without its profile, the lenses land wrong by 3 to 5 mm per eye; a magnet button differs from a
  touch lever.
- **The screen:** the notch falls in one eye's outer edge in landscape; rotation cannot be locked by the page.
- **The cardboard covers the camera** unless it has a cut-out: hands and passthrough need one.
- **Movement:** 3DoF means leaning or stepping does not move the view; walk mode's joystick or a tap moves instead.
- **The link:** multicast DNS names work on one Wi-Fi; a guest or company network may block them (then STUN).
## 8. What the app already has

- `src/js/engine/render/`: the rendered view (three.js 0.186.1, V194, `runtime/`), and `splats.js` (v205's
  header).
- `src/js/engine/walk/`: walk mode, its controls (keys and a touch joystick), its own collision
  (`walk-physics.js`), and the queued drive, drone, swim and record modes (v208 to v211).
- `tools/build_pwa.py` and `src/js/engine/core/offline.js`: the installable, offline web app (V172h).
- Jolt Physics 1.1.1 (MIT, `runtime/jolt/`, V203) behind `walk/walk-physics.js`: the model as one static mesh body
  and a walker; no dynamic bodies yet (correction from hands-and-physics.md part 3: a rigid-body engine is there).
- `io/gltf.js` lines 267 to 276 export GLB (native-paths.md, for a Godot viewer if ever wanted).
- No camera input, no hand input, no stereo view yet.

## 9. Risks and threats to validity

- **The frame rate (H4, H6) is the decisive unknown,** and only the phone answers it. Below about 15 frames a second
  for the hands, the native path's hand points take over.
- **Heat:** sustained camera, tracking and drawing may throttle the A15 within minutes; the test logs each minute.
- **Comfort:** 3DoF with rotation-only tracking can cause discomfort when the user moves; sessions short at first.
- **Facts read through summaries:** the depth study and Meta's 20 ms are S; nothing in the code depends on them
  beyond starting values to tune.
- **Desktop-only checks:** the test page was run here in headless Chromium with software drawing; it shows the page
  runs, not how fast.
- **The repository grows** by about 23 MB if MediaPipe is vendored.

## 10. What is still open (U)

- The phone's numbers: hand tracking rate, Jolt in Safari, the combined rate over 10 to 20 minutes, camera re-prompt,
  wake lock, the viewer's profile (E3).
- Safari-to-Mac multicast DNS for the link; the splat "grow" worst case (its script to be committed); Spark's SPZ v4
  support and its compiled Rust code's licences; whether ARKit runs under a free Apple ID (first build).

## 11. The owner's decisions

Asked 2026-11-23, with the evidence above (answers recorded here when given):

| # | Decision | Recommended |
|---|---|---|
| D1 | The path | Web app first; the Capacitor shell only if the phone's numbers fail. Not Godot, not Swift. |
| D2 | Hand tracking library | MediaPipe Tasks Vision 1.2.3 and its hand model (Apache-2.0), vendored under `runtime/` (about 23 MB), after the phone test. |
| D3 | Physics | Reuse the app's Jolt for hands and movable elements; no new engine. |
| D4 | Minimum iOS for hand mode | iOS 17, with a message on older systems. |
| D5 | How hands act | Push with physics, pinch to grab, release with the hand's speed. |
| D6 | LOD-G2 | On v205's own renderer, no new library; Spark only if the phone shows ours too slow. |
| D7 | First splat edits | Hide and delete by box and sphere; then colour and grow; then move. |
| D8 | The link | QR codes on one Wi-Fi; Cloudflare's STUN as an option for other networks. |
| D9 | QR scanning on the iPhone | A small vetted QR library (its own short research), since Safari's built-in reader is behind a flag. |
| D10 | The test page | Keep MediaPipe from its pinned CDN address on the lab page only, until D2. **Approved by the owner, 2026-11-23** ("i approve"). |

Known before the research: the owner has an iPhone 13, a cardboard viewer and a MacBook Air (2026-11-23); no
paid Apple developer account; "i refuse that would be my own limitation". The Mac is an **M4** MacBook Air (the owner,
2026-11-23), so it runs Xcode 27 on macOS Tahoe. The owner, the same day: "i want this to be accessible for everyone",
which weighs for the web path: anyone with a phone and a link, no install, no Apple account; a native shell reaches
others only through the $99-a-year program (TestFlight or the App Store).

## 12. References

Every source, with its URL, what was read, the date (2026-11-23) and its level, is listed in the topic notes' own
reference sections: `web-on-iphone.md` part 9, `hands-and-physics.md` part 12, `native-paths.md` part 9,
`splats-and-link.md` part 12; the check's re-readings in `independent-check.md`. Prompted by two videos the owner
shared (an editable-splat engine shown at Adobe MAX; Arizona State University's Open4DGS, MIT and AGPL-3.0, not
read) and a screenshot of "PinchDrop" (not found online).
