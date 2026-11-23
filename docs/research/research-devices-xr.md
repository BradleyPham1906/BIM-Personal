# Research: the app on a phone in a cardboard headset, with hands and physics

Started 2026-11-23 by Claude, at the owner's request ("i want to be able to hand track and interact with objects
in my world bim with physics like real world", on an iPhone 13 and a cardboard viewer; the owner has a MacBook Air).
Follows `docs/research/research-protocol.md`. The topic notes are in `docs/research/research-devices-xr/`.

Status: **research in progress.** Parts 1, 5 to 12 are filled in when the topic notes are back.

## 1. Abstract

(When the findings are in.)

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

## 4. Findings, by topic

(From the topic notes.)

## 5. The alternatives compared

(When the findings are in.)

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

## 10. What is still open (U)

## 11. The owner's decisions

Known before the research: the owner has an iPhone 13, a cardboard viewer and a MacBook Air (2026-11-23); no
paid Apple developer account; "i refuse that would be my own limitation".

## 12. References

(Collected from the topic notes.)
