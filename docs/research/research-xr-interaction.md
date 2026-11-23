# Research: one app on every headset, and hand gestures as commands

Started 2026-11-23 by Claude, at the owner's request: "my goal is to make this easily accessible on any devices. lets
say later i got some money to buy a meta quest then how does it plug to our current app? or if i got rich some how i
got a vision pro. the point is accessibility and multi devices. then the tony stark jarvis mode. interaction and
improving UI/UX. certain hand movement have certain interactions and functions. like exploding an object big and
small, in and out." Follows `docs/research/research-protocol.md`. Builds on `research-devices-xr.md` (the iPhone
cardboard path, V274). Topic notes in `docs/research/research-xr-interaction/`.

Status: **research done**; the four topic notes and the independent check are in `research-xr-interaction/`, and
the owner's decisions are asked in part 11.

## 1. Abstract

One web app can serve every device the owner may own. A Meta Quest opens it by its address in Quest Browser, with
full VR, passthrough, and real hand tracking (25 joints a hand; the browser turns a pinch into `select`). An Apple
Vision Pro opens it in Safari with VR by default and gaze-plus-pinch input (a transient pointer, no hover; hand joints
after a permission prompt; no passthrough AR for pages). Android XR headsets bring hands too; Android phones bring AR
without hands; computers bring mouse, touch and, with a camera, MediaPipe hands; the iPhone in cardboard is V274's path.
The app's three.js already carries WebXR sessions, controllers and hand joints; what the app must build is one input
layer (every device reduced to pointers: ray, grab, poke, with press, drag and release, plus a two-hand step), its own
simple hand drawing (the library's hand models load from a CDN, outside the library rule), and 3D menus, since HTML is
not drawn inside a headset session. The six leading frameworks agree on a small core of interactions (pinch to select,
grab and poke near, ray or gaze plus pinch far, pinch and drag, two hands to scale), and the evidence favours few
gestures and visible menus over many shapes: designed gesture sets are recalled at 55 to 89 % the next day, one camera
misreads motion in depth, and raised arms tire in 20 to 30 minutes. The owner's "explode" becomes a visible mode
(Explode view, not the CAD `EXPLODE`, which edits polylines) in which a two-hand spread or a slider sets how far the
storeys separate; the app already has the storey data and a display-only offset in its renderer. Professional BIM
headset apps use controllers, keep being withdrawn, and offer no computed exploded building, which favours owning
the viewer. **Recommendation:** the Explode view first (useful on every device, the desktop included), then the input
layer, the headset session with in-scene menus, and the BIM interactions, as V275 to V278 (part 5).

## 2. The question and the hypotheses

**The question.** How does one web app serve a phone in cardboard, a Meta Quest, an Apple Vision Pro, an Android
phone and a desktop, each with the input it has, without a separate app per device? And which hand gestures should
drive the BIM app's commands (grab, far select, scale, rotate, explode a model apart and back, menus on the hand),
following what the leading interaction frameworks and design guides have found works, and avoiding what tires or
confuses people?

**What a good answer looks like.** A device ladder (what each device gives the app, how it is reached, what it costs);
one input layer the app's code sees on every device; a gesture vocabulary mapped to the app's existing commands, each
with its evidence; the phases that follow V274, and the owner's decisions.

**Hypotheses:**

| Id | Hypothesis | What would refute it |
|---|---|---|
| H1 | Meta Quest's browser runs the same web app in an immersive WebXR session with hand tracking (the WebXR Hand Input module, 25 joints a hand) and passthrough, so a Quest needs no separate app. | Quest Browser documentation or tests showing hand input or immersive-ar missing. |
| H2 | Safari on Apple Vision Pro runs WebXR immersive VR with its own input (gaze and pinch as a transient pointer); full hand joints are not given to pages by default. | Apple's documentation showing full hand joints by default, or no WebXR at all. |
| H3 | three.js 0.186.1, already in the app, carries WebXR sessions and the hand joints, so the same rendered view serves Quest and Vision Pro with a small adapter. | three.js lacking hand input or failing on these browsers. |
| H4 | One input layer can express every device's input (WebXR hands, transient pointer, controllers, our MediaPipe hands, mouse and touch) as the same few events (point, pinch start, pinch move, pinch end, poke, two-hand), so the app's commands are written once. | A device whose input cannot be reduced to that set without losing what makes it useful. |
| H5 | The established frameworks (Meta Interaction SDK, Unity XR Interaction Toolkit, MRTK3, Apple's visionOS guidelines) converge on a small core: direct grab and poke near, ray or gaze plus pinch far, two-hand scale and rotate, hand-attached menus. | Frameworks disagreeing on the core, or evidence that a larger gesture set works better. |
| H6 | Free-form "magic" gestures (many shapes to learn) fail in practice from fatigue, false triggers and discoverability; a few gestures plus visible menus work better. | Studies showing large gesture sets learned and used reliably. |
| H7 | An exploded view of a building (by storey, by system, by assembly) driven by a two-hand spread is possible from the app's own model data, and BIM viewers already offer exploded views. | No hierarchy in the app's model to explode by, or no prior art. |
| H8 | BIM apps already in XR (for example on Quest) show which BIM tasks people do in a headset (review, measure, section, issues), which sets the priority of gestures. | No usable prior art. |

## 3. Method

Three researchers in parallel, each writing its note in `docs/research/research-xr-interaction/`:

- `devices.md`: the device ladder and the input layer (H1 to H4).
- `gestures.md`: the frameworks and design guides, ergonomics, the gesture vocabulary (H5, H6).
- `bim-xr.md`: BIM in XR prior art, exploded views, and the app's own commands and model the gestures would drive
  (H7, H8).

Then an independent second reader, and the owner's decisions together at the end.

## 2a. The outcome of each hypothesis

| Id | Outcome |
|---|---|
| H1 | **Held** (P, high): Quest Browser gives immersive-vr and immersive-ar, WebXR hands (25 joints, radii), `select` on pinch, planes, anchors (8 persistent a site), hit test, meshes, depth; 72 Hz default. |
| H2 | **Held, corrected** (P): Vision Pro Safari has immersive-vr on by default since visionOS 2; input is a transient pointer (gaze at the pinch, then the hand moves it; no hover); hand joints after a permission prompt, poses only; immersive-ar not supported (one developer's report on visionOS 1, S). |
| H3 | **Held in part** (P, high): the app's three.js bundle has `renderer.xr`, controllers, `getHand`, joint poses and pinch events (1.5 cm in, 2.5 cm out); the hand and controller models and the VR and AR buttons are not in it, and their models load from a CDN by default. |
| H4 | **Held, with limits** (medium-high): pointers (ray, grab, poke) with point, press, drag, release and cancel, plus a two-hand step, cover every device; nothing may need hover (Vision Pro), joint pinch is off while a gaze pointer is active (one pinch must not count twice), a single camera grabs by pinch only. |
| H5 | **Held for the core** (P): six frameworks agree; hand-attached menus are the exception (Meta and Microsoft build them; Apple reserves the space round the hand). |
| H6 | **Held** (P): people can learn 8 to 22 gestures, but designed sets are recalled at 55 to 89 % the next day (Nacenta et al. 2013, corrected by the check), one camera misreads motion in depth (GRLib), and raised arms tire in 20 to 30 minutes; every guide says few, gated custom poses. |
| H7 | **Held, qualified** (P): explode by level exists in two Autodesk developer samples and That Open's on/off Exploder, not as a standard viewer feature; Li et al. 2008 give the interactive method; the app has storeys and a display-only offset. |
| H8 | **Held** (medium-high): headset BIM apps agree on full-size walking plus a tabletop model, measure, comments and issues, layer visibility, element data, multi-user, saved scenes; they use controllers; several were withdrawn (SketchUp's Quest viewer 2025-09-16, Unity Reflect, The Wild and Prospect folded into Workshop XR). |

## 4. Findings, by topic

Each topic note holds its findings, sources, levels and confidence: `devices.md`, `gestures.md`, `bim-xr.md`; the
check's corrections are in `independent-check.md` and win where they differ. The findings the plan rests on:

**The device ladder** (devices.md part 7, corrected):

| Device | How the app reaches it | Tracking | Hands | Passthrough | What the app must add |
|---|---|---|---|---|---|
| iPhone in cardboard | Home Screen web app | 3DoF (motion sensors) | MediaPipe, 21 points, 35-39 fps (measured) | the camera behind (V274) | V274, XR-2 |
| Android phone | Chrome | 6DoF in AR (ARCore) | none from WebXR; MediaPipe | immersive-ar | the session and the input layer |
| Meta Quest 3 / 3S | Quest Browser, by address or Web Launch; optional store wrap (Bubblewrap) | 6DoF | WebXR, 25 joints; pinch is `select` | immersive-ar | the session, hand drawing, 3D menus |
| Apple Vision Pro | Safari | 6DoF | gaze plus pinch (transient pointer); joints after a prompt | none for pages | the same, with no hover |
| Android XR headset | Chrome | 6DoF | WebXR hands by default | yes | the same |
| Computer | the browser | none | mouse, touch; MediaPipe with a camera | none | the input layer |

**The gesture vocabulary** (gestures.md, the proposal; three hand shapes, pinch, poke and palm-up, plus two-hand pinch):

| # | Gesture | Function | Touch or mouse | iPhone camera hands |
|---|---|---|---|---|
| 1 | Point (ray or gaze) and pinch | Select far | click, tap | in the image plane |
| 2 | Poke | Press a 3D button | click | in the image plane |
| 3 | Pinch and drag | Move the selection | drag | in the image plane, no push toward the camera |
| 4 | Two hands, pinch and spread or turn | Move, turn about the vertical, scale the model (snaps at 1:1 and drawing scales) | two-finger pinch and turn | both hands in view only |
| 5 | Explode mode, then spread or a slider | How far the storeys separate; drag one storey along its direction | the slider | the slider |
| 6 | Point and pinch on the floor | Go there (no smooth flying) | double tap | yes |
| 7 | Pinch two points | Measure (`DIST`) | two clicks | yes |
| 8 | Grab the section handle | Move the section (`SECTIONTOOL`) | drag | yes |
| 9 | Palm up, flat hand, looked at | Hand menu (a floating toolbar on Vision Pro) | the toolbar | the toolbar |
| 10 | Menu button | Undo | Ctrl+Z | the toolbar |

Never acted on: a pinch with the palm toward the user (Quest and Android XR system menus; a Quest store
requirement), looking at the palm or flipping the hand on Vision Pro. Controllers are first-class on Quest (bim-xr.md:
the professional apps use them): the trigger is the pinch, the grip is grab.

**The Explode view** (bim-xr.md part 4, the check's corrections): by storey first (ranked by elevation, offset =
rank x gap x amount, upward), then by building, then by layer standing in for systems. Display only: an offset row in
the renderer's batches (`render/gpu-batches.js:144`, read by WebGL, WebGPU, the rendered view and GPU picking); never
`o.pos`, which 38 engine files read, save and export included; every drawing and picking path to be found by a full
audit, not four named sites. View state outside the undo stack, saved in saved views; an edit collapses it first.
Imported IFC elements carry `bim.storey` but no level, and a storey with no elevation gets no level, so matching needs
a rule. A continuous explode rebuilds the rendered view's chunks each frame (`rendered-scene.js:41-46` hashes the
offsets), a cost to measure. The name is not `EXPLODE` (`editing/drafting-modify.js:159-193`, AutoCAD's polyline
explode, which edits).

**Menus in a headset:** HTML is not drawn inside an immersive session, so the panels the app needs there are drawn in
3D by the app; targets at least 2 degrees near and 1 degree far, text about 0.65 to 0.8 degrees, the hand menu 13 cm
above the palm on the little-finger side with 3 buttons; hover, pressed and released states (no hover on Vision Pro),
a pinch-progress ring, sounds, the hand dimmed when tracking is unsure.

## 5. The alternatives compared

| | Explode view first | Input layer first | Headset session first |
|---|---|---|---|
| Who benefits at once | everyone, on any device, the desktop included | phone and computer hands | Quest and Vision Pro owners |
| Needs hardware the owner lacks | no | no | yes, to check (an emulator helps) |
| Risk | the renderer audit | design of the pointer model | 3D menus, the largest piece |
| Depends on | nothing new | V274 | the input layer |

**Recommendation:** in this order, each written as work orders after the owner's decisions:

1. **V275 Explode view:** storey explode as a display-only view state, a slider in the view and saved views; the
   renderer audit; the chunk cost measured. On every device from day one.
2. **V276 The input layer and the simulated hand:** pointers (ray, grab, poke) and the two-hand step, fed by mouse,
   touch and MediaPipe hands (in a worker, the One Euro filter, the calibration: research-devices-xr.md's XR-2); the
   25-joint skeleton with MediaPipe retargeted onto it, the skinned hand (E4) and a Jolt capsule on every bone; the
   vocabulary's functions written once against it.
3. **V277 The headset session:** three.js WebXR on Quest, Vision Pro and Android XR (`renderer.setAnimationLoop`),
   WebXR hands, controllers and the transient pointer into the input layer, simple hand drawing of our own, the 3D
   menus and the hand menu; checked with Meta's emulator in a browser test if approved, then on a Quest.
4. **V278 BIM in the headset:** the tabletop model and 1:1 with snaps, go-there, measure, the section handle, layers,
   element data; the physics hand and the link to a computer (research-devices-xr.md XR-3, XR-4) after.

## 6. The experiments

- **E5, where the generic hand's metacarpals sit** (`experiments/xr-interaction/hand_bind_pose.py`, 2026-11-23):
  `@webxr-input-profiles/assets` 1.0.20 (MIT) `generic-hand/{left,right}.glb` read as data; each metacarpal joint lies
  on the wrist-to-knuckle line within 6.7 mm, at 0.398 (left) and 0.341 (right) for the index, 0.320 middle, 0.328 ring,
  0.502 pinky; the thumb's metacarpal 49.5 mm from the wrist. V276 rebuilds MediaPipe's 21 points as 25 joints with
  0.37, 0.32, 0.33 and 0.5.

## 7. Edges

- Vision Pro has no hover: no feature may depend on it. Its pinch arrives as a transient pointer; reading the joints
  too would count one pinch twice.
- Quest's palm pinch is the system menu; the app never acts on palm-toward-user pinches.
- A single camera cannot push toward or away (depth misread): the phone's gestures work in the image plane only.
- Two-hand gestures need both hands in view: on the phone, the camera's 65 degrees.
- The Explode view and editing: an edit collapses it first; it is never saved into positions.

## 8. What the app already has

- The iPhone cardboard path: `research-devices-xr.md`, V274 (`src/js/engine/render/headset.js`, queued), the phone
  test (`experiments/devices-xr/phone-test.html`) and the link test (`link-test.html`).
- three.js 0.186.1 (`runtime/three/`), the rendered view (`src/js/engine/render/rendered-*.js`), Jolt (`runtime/jolt/`,
  walk mode), the command catalogue (`src/js/engine/commands/`).

## 9. Risks and threats to validity

- No headset was used: Quest and Vision Pro facts are from documentation, specifications and source; frame times on
  a Quest are to measure when the owner has one, or in Meta's emulator for behaviour only.
- Meta, Apple forum and several vendor pages were read only through a fetch summary (P digest or S); the check
  marked them.
- Gesture recall figures come from tabletop studies, not headsets; no headset study compares symbolic air gestures
  with menus for picking commands.
- The explode's per-frame chunk rebuild may be costly on large models.

## 10. What is still open (U)

- An install button for web apps in Quest Browser; Meta's own pages on meshes and depth; whether visionOS 26 and 27
  keep WebXR on; whether a Safari WebXR session may defer Vision Pro's palm Home indicator; Cardboard VR in Chrome on
  ordinary phones; the WebXR Layers text (its address answered 404); current prices.
- On the phone: the pinch false-activation rate, palm-up detection, two-hand visibility.
- The explode's range, dead zone and scale snaps: one browser check.

## 11. The owner's decisions

Asked 2026-11-23. **Answered the same day: E4 changed by the owner (below); the rest "as recommended".** V275, the
Explode view, is written (`docs/work-orders/v275/`).

| # | Decision | Recommended |
|---|---|---|
| E1 | The order | V275 Explode view, V276 input layer, V277 headset session, V278 BIM in the headset. |
| E2 | The Explode view | By storey first (then building, then layer), upward, one amount from 0 to 1 by slider or two-hand spread in its mode; display only, saved in saved views, collapsed before an edit; a new name (Explode view), not `EXPLODE`. |
| E3 | The gesture vocabulary | The ten in part 4, palm-toward-user pinches never acted on; few gestures, visible menus. |
| E4 | Hands drawn and simulated | **The owner, 2026-11-23: "i dont want the hand to be simple outline, i need the skeleton and actual hand simulated so it can accurately interact with models".** A full 25-joint skeleton (WebXR Hand Input) on every device: measured by Quest, Vision Pro (after its prompt) and Android XR; on the iPhone and webcams, MediaPipe's 21 points retargeted onto it (metacarpals placed between wrist and knuckles, bone rotations from the joints they join: a short research of its own, Kalidokit (MIT) as prior art). Drawn as a skinned hand: three.js's `XRHandMeshModel` added to the bundle `tools/three/build_three.mjs` makes, and the WebXR generic hand models (MIT, about 94 KB; licence confirmed by the check) vendored under `runtime/`, pinned, loaded locally, never from the CDN. Simulated: a capsule collider on every bone (about 24 a hand) in the app's Jolt, driven toward its joint so it stops at surfaces; fingertips press, pinch or a closed hand grabs. Precision follows the device: measured joints on headsets, a few centimetres in depth from one phone camera. |
| E5 | Quest controllers | First-class beside hands: trigger is pinch, grip is grab. |
| E6 | Menus in the headset | Our own 3D panels; the hand menu on Quest and Android XR, a floating toolbar on Vision Pro. |
| E7 | A headset emulator for tests | Meta's `iwer` (MIT) as a test-only package, pinned, never shipped in the app (a library decision under the rule). |
| E8 | Vision Pro | VR only (no AR for pages); no USDZ export for Apple's model viewer for now. |

Known: the owner has an iPhone 13, a cardboard viewer, an M4 MacBook Air and a Windows mini PC without a webcam; may
buy a Meta Quest later; accessibility on any device is the goal (2026-11-23). Prompted by screenshots of a Quest 3 hand
menu (Ben Claremont's video) and a mixed-reality "build table" app with an exploded model handled by two hands.

## 12. References

Every source, with its URL, what was read, the date (2026-11-23) and its level, is in the topic notes' reference
sections (`devices.md`, `gestures.md`, `bim-xr.md`) and the check's re-readings (`independent-check.md`).
