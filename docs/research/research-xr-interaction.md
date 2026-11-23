# Research: one app on every headset, and hand gestures as commands

Started 2026-11-23 by Claude, at the owner's request: "my goal is to make this easily accessible on any devices. lets
say later i got some money to buy a meta quest then how does it plug to our current app? or if i got rich some how i
got a vision pro. the point is accessibility and multi devices. then the tony stark jarvis mode. interaction and
improving UI/UX. certain hand movement have certain interactions and functions. like exploding an object big and
small, in and out." Follows `docs/research/research-protocol.md`. Builds on `research-devices-xr.md` (the iPhone
cardboard path, V274). Topic notes in `docs/research/research-xr-interaction/`.

Status: **research in progress.**

## 1. Abstract

(When the findings are in.)

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

## 4. Findings, by topic

## 5. The alternatives compared

## 6. The experiments

## 7. Edges

## 8. What the app already has

- The iPhone cardboard path: `research-devices-xr.md`, V274 (`src/js/engine/render/headset.js`, queued), the phone
  test (`experiments/devices-xr/phone-test.html`) and the link test (`link-test.html`).
- three.js 0.186.1 (`runtime/three/`), the rendered view (`src/js/engine/render/rendered-*.js`), Jolt (`runtime/jolt/`,
  walk mode), the command catalogue (`src/js/engine/commands/`).

## 9. Risks and threats to validity

## 10. What is still open (U)

## 11. The owner's decisions

Known: the owner has an iPhone 13, a cardboard viewer, an M4 MacBook Air and a Windows mini PC without a webcam; may
buy a Meta Quest later; accessibility on any device is the goal (2026-11-23). Prompted by screenshots of a Quest 3 hand
menu (Ben Claremont's video) and a mixed-reality "build table" app with an exploded model handled by two hands.

## 12. References
