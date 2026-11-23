# Topic note: the gesture vocabulary and its evidence (H5, H6)

Corrections from the independent check (2026-11-23) are in `independent-check.md` and applied in the main note,
`../research-xr-interaction.md`; where they differ, those win.

One of the three topic notes of `docs/research/research-xr-interaction.md`. Researched 2026-11-23 by a research agent,
following `docs/research/research-protocol.md`. Every fact carries its level: P (primary source read: the vendor's own
guide or SDK page, the paper's own text, the code read as text), S (dependable secondary, the gap said), U (search
summary, one unchecked copy, or our own reasoning not yet tested; never used by code). Where a primary page came back
through the fetch tool as a digest and not as the page's own text, it is marked "P, digest" and its confidence is one
step lower: the page is primary, but its wording passed through a summariser. Downloaded papers and code were kept in
the session scratchpad, read as text (`pdftotext`, `grep`), never run.

What is already settled in `../research-devices-xr/hands-and-physics.md` is not repeated: MediaPipe Hand Landmarker
(21 points, world landmarks in metres about the hand's centre, no reliable distance from the camera), the One Euro
filter, the pinch thresholds read in MRTK2, Ultraleap and three.js (enter about 2 to 2.5 cm, exit 3 to 5 cm, with
hysteresis), and the physics hand. This note decides what the hands should *do*.

## 1. The questions

1. Which core interactions do the leading frameworks and guides define, each from its own documentation (Meta
   Interaction SDK and Meta's hand design guides, Unity XR Interaction Toolkit 3.x and XR Hands, MRTK3 and Microsoft's
   mixed reality design pages, Apple's visionOS Human Interface Guidelines, Ultraleap's XR guidelines, Android XR's
   design guidance), and where do they agree (H5)?
2. Which gestures does each operating system reserve, so the app must not use them?
3. What does the evidence say about fatigue, false activation (the Midas touch), discoverability and memorability, the
   number of gestures, and recognition of static versus dynamic gestures from one RGB camera (H6)? Is there evidence
   that large gesture vocabularies work?
4. How do two hands scale, rotate and move an object, and how can a two-hand spread drive an exploded view without
   colliding with uniform scale?
5. How should hand-attached UI be placed and sized?
6. How is feedback given without haptics?
7. A proposed vocabulary of at most about ten interactions, each with its evidence, conflicts and fallbacks to touch,
   mouse and the phone's 21-point MediaPipe hands at about 35 fps.

**Falsifiable claims tested here (from the parent note):**

- H5: the frameworks converge on a small core: direct grab and poke near, ray or gaze plus pinch far, two-hand scale
  and rotate, hand-attached menus. Refuted by frameworks disagreeing on the core, or by evidence that a larger gesture
  set works better.
- H6: free-form "magic" gestures (many shapes to learn) fail in practice from fatigue, false triggers and
  discoverability; a few gestures plus visible menus work better. Refuted by studies showing large gesture sets
  learned and used reliably.

## 2. Search log

| # | Where | Query or request | What came back | Kept / set aside |
|---|---|---|---|---|
| 1 | web search | Meta Interaction SDK overview grab poke ray distance grab pose detection | Meta design and SDK pages | pointers; pages then read (5 to 13) |
| 2 | web search | Apple visionOS HIG gestures custom gestures ergonomics | HIG `.md` pages, support pages, third-party summaries | HIG pages read; a third-party summary (smithery.ai) set aside as U |
| 3 | web search | MRTK3 bounds control hand menu near far | learn.microsoft.com pages | read (16 to 20) |
| 4 | web search | XRI 3.0 near-far interactor poke gaze two-handed scale | Unity manual pages | read (21 to 24); two pages 404 at the guessed URL |
| 5 | developers.meta.com | `/design/hands-interaction-types/` | seven interaction types, 22 mm targets, 12 mm spacing, long-press timings | kept (P, digest) |
| 6 | developers.meta.com | `/design/hands/`, `/design/hands-gesture-design/`, `/design/hands-best-practices/`, `/design/hands-limitations-mitigations/`, `/design/hands-technology/` | principles, "small number of very simple poses", gating, 30 Hz / 60 Hz tracking | kept (P, digest) |
| 7 | developers.meta.com | `/design/grab_usage/`, `/design/interactions-input-mappings/` | pinch and palm grab, one- and two-point manipulation | kept (P, digest) |
| 8 | developers.meta.com | `/documentation/web/webxr-hands/` | palm pinch reserved on both hands in WebXR; pinch as emulated gamepad button | kept (P, digest) |
| 9 | developers.meta.com | `/resources/vrc-quest-input-8/` (store criteria) | "the system gesture is reserved" | kept (P, digest; one sentence) |
| 10 | meta.com/help | Quest hand tracking help article | page body not returned (truncated twice) | set aside; recorded as open |
| 11 | developers.meta.com | `/design/design-microgestures/` | thumb tap, double tap, swipes; do and do not | kept (P, digest) |
| 12 | developers.meta.com | `/documentation/unity/unity-isdk-hand-pose-detection/`, `/unity-isdk-two-handed-grab-interaction/`, `/unity-isdk-interaction-sdk-overview/` | six example poses, hysteresis, two-grab transformers | kept (P, digest); licence not stated on the page |
| 13 | web search | Meta microgestures documentation | pointers | used for 11 |
| 14 | developer.apple.com | HIG `gestures.md`, `designing-for-visionos.md`, `eyes.md`, `spatial-layout.md` (Markdown, verbatim) | standard and direct gestures, custom-gesture rules, system overlays, 60 pt / 16 pt spacing, 1 m reading distance | kept (P, verbatim) |
| 15 | learn.microsoft.com | MRTK3 hand menu, BoundsControl | gaze and flat-hand gating, ulnar side, world-lock on drop, uniform scale | kept (P, verbatim) |
| 16 | learn.microsoft.com | mixed reality design: hand menu, typography, interactable object | 3 buttons, 13 cm above palm, 10 degree attentional cone, text and target sizes in degrees | kept (P, verbatim) |
| 17 | raw.githubusercontent.com, git (anonymous read) | MRTK3 `LICENSE.md`; sparse clone of `MixedRealityToolkit/mixedrealitytoolkit-unity` at 83c8c1d, `org.mixedrealitytoolkit.spatialmanipulation` only | BSD-3-Clause; `ScaleLogic.cs`, `RotateLogic.cs`, `HandConstraintPalmUp.cs` | kept (P, code read as text) |
| 18 | docs.unity3d.com | XRI 3.0 `near-far-interactor.html`; API `XRGeneralGrabTransformer` (3.0) | near and far casters, attach modes; two-hand scale threshold and clamps | kept (P, digest) |
| 19 | docs.unity3d.com | XR Hands 1.4 `finger-shapes.html` | five finger shapes, tolerances, pinch as a system gesture | kept (P, digest) |
| 20 | docs.unity3d.com | guessed URLs for XRI general grab transformer manual and XR Hands 1.5 gestures overview | 404 | set aside; API page used instead |
| 21 | docs.ultraleap.com | XR guidelines: design principles, design considerations | "use poses sparingly", "as few and as simple as possible", tracking volume figures | kept (P, digest) |
| 22 | developer.android.com, support.google.com | Android XR design considerations (verbatim); Android XR navigation help; ARCore for Jetpack XR hands | system gestures on the palm-facing primary hand; one-handed priority; use the secondary hand for custom gestures | kept (P) |
| 23 | perso.lisn.upsaclay.fr (redirect from lri.fr) | Hincapie-Ramos et al., CHI 2014, PDF | full text via `pdftotext` | kept (P) |
| 24 | sutd-cgl.github.io | Song et al., CHI 2012, handle bar, PDF | full text via `pdftotext` | kept (P) |
| 25 | research-repository.st-andrews.ac.uk | Nacenta et al., CHI 2013, PDF | fetch tool 403; `curl` with a browser user agent 200; full text | kept (P) |
| 26 | marcjohnson.fr | Jacob, TOIS 1991, scanned PDF with a text layer | Midas touch passage | kept (P) |
| 27 | cs.princeton.edu | Zhai et al., MAGIC pointing slides | slide text only | set aside: a course copy, slides not the paper |
| 28 | arXiv (html) | 2311.15372, Kostic et al., mid-air gestures for visualisation | 8-gesture vocabulary, recall, expert ergonomics | kept (P, digest; first 100,000 characters) |
| 29 | inria.hal.science, ifip.hal.science, core.ac.uk | Piumsomboon et al., INTERACT 2013, full text | Anubis "not a bot" page, 403 | refused; abstract facts kept as U |
| 30 | api.openalex.org | the same DOI | metadata, no abstract | set aside |
| 31 | cs.cmu.edu | Stoakley et al., CHI 1995, WIM, HTML | full text | kept (P, digest) |
| 32 | grail.cs.washington.edu | Li et al., SIGGRAPH 2008, exploded views, PDF | full text via `pdftotext` | kept (P) |
| 33 | developers.google.com, huggingface.co | MediaPipe gesture recognizer guide; model card PDF (2022) | 7 static gestures, out of scope: motion and two-hand gestures, SS F1 93.9 to 95.5 % | kept (P; model card read in full) |
| 34 | ar5iv.labs.arxiv.org | 2006.10214, MediaPipe Hands | palm AP 95.7 %, landmark MSE, rule-based static gestures | kept (P, digest) |
| 35 | arXiv | 2310.14919, GRLib (Warchocki et al.) | MediaPipe depth makes forward/backward gestures falsely detected; dynamic precision about 60 % | kept (P, `pdftotext`) |
| 36 | vvise.iat.sfu.ca | Mutasim et al., ETRA 2021, pinch, click or dwell | full text | kept (P) |
| 37 | web search | static vs dynamic MediaPipe accuracy; command selection gestures vs menus | a Chalmers thesis (88.1 % dynamic, 93.1 % static, search digest only), HotGestures (snippet) | U; pointers only |
| 38 | web search | Guiard 1987 | Southampton archive copy | 403; principle kept as S via Hinckley et al. (search digest), so U for wording |
| 39 | the app's code | `grep` in `src/js/engine/commands/`, `src/js/engine/editing/drafting-modify.js` | UNDO, DIST, SECTIONTOOL, WALK, zoomFit exist; EXPLODE already means "break a polyline" | kept (P) |

## 3. Findings

### 3.1 The frameworks, each from its own documentation (H5)

**Meta (Interaction SDK and the Horizon design guides).** The interaction types page defines ray ("Use pinch gestures
for hands to perform selections"; do not rely on ray alone), distance grab (three methods: interactable to hand, anchor
at hand, hand to interactable; "Implement magnetism"), poke (index finger only; "Pinching is a different gesture and
should not be used for direct touch interactions"; minimum target 22 x 22 mm with 12 mm spacing), grab (pinch grab and
palm grab), pose and gesture detection ("Limit use to a small number of very simple poses and gestures"; add gating
such as proximity or hover), locomotion (gating against false positives) and long press (0.5 s delay, 0.25 s cooldown,
never the main method for critical actions). P, digest; high confidence (the same points recur on four Meta pages).
The input mappings page: selection by "Pinch (indirect), poke (direct), palm grab"; one-point manipulation by "Pinch and
drag, palm grab"; two-point manipulation by "Both hands pinch or palm grab", with "By moving the two grabbed points
closer together, the user can scale the object down." P, digest; high. The SDK's two-hand grab: position follows the
centroid of the grab points, rotation from relative hand movement, scale locked 1:1 by default and freed per axis with
min and max, and a `TwoGrabRotateTransformer` that constrains rotation to one axis. P, digest; high. Pose detection:
six example poses (rock, paper, scissors, thumbs up, thumbs down, stop), finger features with hysteresis (for curl,
open to neutral above 195, back below 185) and a minimum time in state (0.0222 s), and sequences for dynamic gestures.
P, digest; high. Tracking runs at 30 Hz by default, 60 Hz in Fast Motion Mode, which "can cause jitter". P, digest;
medium. Microgestures (thumb tap, double tap, swipes along the index finger) exist in the native SDK and OpenXR
extension; Meta says "Do NOT use Thumb-tap for selection" and not to treat a swipe as continuous scroll. P, digest;
high. Whether microgestures reach WebXR pages: not stated by Meta; WebXR's hand module gives joints only (U, see
`devices.md`).

**Unity XR Interaction Toolkit 3.x and XR Hands.** XRI 3.0's Near-Far Interactor "utilizes both near and far
interaction casters", replacing the separate direct and ray interactors; a far select can bring the object to the
hand (near attach) or hold it at the hit point (far attach). P, digest; high. The General Grab Transformer has
`allowTwoHandedScaling`, a `thresholdMoveRatioForScale` ("relative hand displacement required to trigger scale"),
`minimumScaleRatio`/`maximumScaleRatio` and `permittedDisplacementAxes`. P, digest; high. XRI also lists poke and gaze
interactors (the gaze interactor snaps rays to what the user looks at). S (search digest of the 3.0 table of contents
and the 3.5 page), medium. XR Hands describes static hand shapes from five finger shapes (full curl, base curl, tip
curl, pinch, spread) with tolerances, and warns that pinch "is a common system gesture" so custom high-pinch values
need care. P, digest; high.

**Microsoft MRTK3 and the mixed reality design pages.** MRTK3 builds on XRI (near and far inherited). BoundsControl
gives an auto-sized box with rotate and scale affordances, uniform or non-uniform scale; Microsoft "strongly recommend"
a `MinMaxScaleConstraint` "to prevent the user from scaling the object to an unusably small or large size", and pairing
it with ObjectManipulator for direct manipulation. P, verbatim; high. The hand menu: palm-up activation with optional
"Require Flat Hand" and "Use Gaze Activation" "to prevent false activation"; ulnar side; large menus world-lock on
hand drop. P, verbatim; high. Licence of MRTK3: BSD-3-Clause (P, `LICENSE.md` read). The code (P, read as text at
83c8c1d): two-hand scale is `startObjectScale * (currentHandDistance / startHandDistance)` (`ScaleLogic.cs`); two-hand
rotation is `FromToRotation(startHandlebar, currentHandlebar) * startRotation`, where the handlebar is the vector
between the two grab points (`RotateLogic.cs`). The palm-up menu defaults: palm within 80 degrees of facing the camera,
flat hand within 45 degrees, gaze proximity 0.1 m (eye) or 0.2 m (head), both thresholds stored as squared distances
0.01 and 0.04 (`HandConstraintPalmUp.cs`).

**Apple visionOS HIG.** Two categories: indirect (look to target, tap finger and thumb; "comfortable to perform at any
distance") and direct (touch; "Because people may find it tiring to keep their arms raised for extended periods,
direct gestures are best for infrequent use"). Direct gestures listed: touch, touch and hold, touch and drag, double
touch, swipe, "With two hands, pinch and drag together or apart: Zoom in or out", "With two hands, pinch and drag in a
circular motion: Rotate an object". Custom gestures: "Add custom gestures only when necessary"; they must be
discoverable, straightforward, distinct and "Not the only way to perform an important action"; avoid gestures needing
a specific hand; "Prioritize comfort"; complex two-hand gestures need a lower-movement alternative; "Avoid using a
familiar gesture like tap or swipe to perform an action that's unique to your app". Gaze is private: "visionOS doesn't
provide direct information about where people are looking before they tap." P, verbatim; high.

**Ultraleap XR guidelines.** "Make interactions physical", "Use poses sparingly", "Provide extra feedback", "Avoid users
needing to hold hand poses for extended periods of time", avoid total occlusion of one hand by the other; for one-time
experiences "hand interactions should be as few and as simple as possible", while "You can use more interactions but
may require help and onboarding content to introduce them gradually." P, digest; medium-high.

**Android XR.** "When interacting with 2D UI, use standard system gestures such as pinch. For 3D interactions like
picking up and throwing a ball, you should design with gestures that mimic the real-world interaction." Additional
gestures must be "easy to learn, remember, and execute"; "Prioritize one-handed interactions for essential actions. If
two-handed gestures are necessary, provide alternative one-handed methods"; usable with either hand; "Limit scenes
that move around the user such as flying"; teleportation causes the least motion sickness. P, verbatim; high. The
consumer help lists point, select (pinch), move/scroll/pan (pinch and drag) and "Zoom or adjust scale: Pinch with both
hands, then move your hands closer or further apart". P, digest; high.

**The comparison table (H5).** "Yes" means the framework's own document defines it; "discouraged" means its own
document advises against it.

| Interaction | Meta ISDK / guides | Unity XRI 3 / XR Hands | MRTK3 / MS design | Apple visionOS HIG | Ultraleap | Android XR |
|---|---|---|---|---|---|---|
| Near direct grab (pinch or palm) | yes | yes (near caster) | yes (ObjectManipulator) | yes (touch and drag) | yes (physical first) | yes (mimic real world) |
| Poke / direct touch of UI | yes (index only, 22 mm) | yes (poke interactor) | yes (1.6 cm at 45 cm) | yes (direct, for infrequent use) | yes (3D buttons) | yes (hand poke) |
| Far select: hand ray + pinch | yes | yes (far caster) | yes (hand ray) | no (gaze instead) | yes (learned) | yes (point + pinch) |
| Far select: gaze + pinch | not in hand guides | yes (gaze interactor, assist) | yes (eye or head gaze) | yes, the primary input | no | yes (gaze + pinch in AXRIF, S) |
| Pinch and drag (one-point move) | yes | yes | yes | yes (drag) | yes | yes (move, scroll, pan) |
| Distance grab (bring or hold far object) | yes, three methods | yes (near/far attach) | yes (far manipulation) | indirect drag | not stated | not stated |
| Two-hand scale | yes (two-point) | yes (opt-in flag) | yes (ratio, code) | yes (zoom) | not stated | yes (zoom or adjust scale) |
| Two-hand rotate | yes (relative hands; one-axis option) | yes | yes (handlebar, code) | yes (circular) | not stated | not stated |
| Hand-attached (palm) menu | yes (hand UI placements) | not a component | yes (palm-up, gated) | discouraged ("don't anchor content to hands") | not stated | not stated; system nav is on the palm |
| Static pose detection | yes, "small number", gated | yes (hand shapes) | not a component | custom only when necessary | "sparingly" | allowed, easy to learn |
| Dynamic / custom gestures | sequences; microgestures native | not in core | not a component | custom only when necessary | onboarding needed | avoid complex multi-step |
| Long press | yes, not for critical | n/a | n/a | yes (context menu) | n/a | yes (system) |

Where they agree (high confidence, six of six or five of six): pinch is the universal select; direct grab and poke
near; a far pointer (ray or gaze) confirmed by pinch; pinch and drag to move; two hands pinching and moving apart to
scale or zoom; few, simple, gated custom poses at most. Where they differ: Apple discourages hand-anchored content and
uses gaze, not a hand ray; MRTK and Meta build hand menus. So H5 holds for the core, with one exception (section 6).

### 3.2 What each operating system reserves

| System | Reserved gesture | What it does | Source, level |
|---|---|---|---|
| Meta Quest (WebXR too) | palm pinch, either hand: palm toward the face at eye level, thumb and index held until the icon fills | left hand: same as the controller's menu button (leaves the WebXR session); right: system menu | Meta WebXR hands page (P, digest); store criteria "the system gesture is reserved, and should not trigger any other actions within the app" (P, digest) |
| Apple Vision Pro (visionOS 2+) | looking at the palm, tap: Home; flipping the hand: Control Center; the rolling hand-wrist-forearm motion | system overlays drawn over app content; the app is not told | HIG gestures (P, verbatim): "Reserve the area around a person's hand for system overlays"; "Use caution when designing custom gestures that involve a rolling motion" |
| Android XR | palm facing the user, pinch and hold: Launcher; hold longer: Circle to Search; hold, move left: Back; move right: Recents; open palm up then pinch: Home | system navigation on the user's primary hand | Google help (P, digest); ARCore hands: "Use the secondary hand for your custom gestures" (P, verbatim) |
| The phone (our MediaPipe path) | none: the camera hands are ours | none | own reasoning (U) |

Consequence for the app: never bind anything to a pinch made with the palm facing the user, and never place hand UI
in the space just above the palm; the palm-up hand menu must open on palm-up plus gaze without a pinch, and its
buttons are poked by the other hand. A Meta feedback report says the palm-up pinch causes frequent accidental exits
(U, search digest), which is a reason to keep the menu hand's fingers open. On Vision Pro, Apple says not to anchor
content to the hands at all; Safari's WebXR may not expose hand joints by default (H2, `devices.md`), so the Vision
Pro build uses a floating, world-locked toolbar instead.

### 3.3 Ergonomics and errors (H6)

**Gorilla arm.** Hincapie-Ramos et al. (CHI 2014) define Consumed Endurance from Rohmert's endurance curve, which "is
asymptotic at 15% of the maximum force, meaning that forces exerted below that level could be sustained for long time
periods." In a 12-person target study, CE was lowest with the hand on the "center" plane (halfway between shoulder and
waist; 27.23 %) and with the arm bent (hand within 35 cm of the body; 23.44 %); Borg CR10 agreed. Of four selection
methods, the one that does not move the pointing hand (a click held in the other hand) was lowest (8.18 %); swipe was
worst and had the most errors from tracking. Their guidance: center plane, bent arm, a small (25 x 25 cm) interaction
area. P, high (a Kinect and wall screen; the shape of the result, not the numbers, carries to a headset). Song et al.
(CHI 2012): "Some users complained about arm fatigue after 20-30 minutes of continuous usage", "the issue of fast
fatigue onset is still a perennial problem when using mid-air interaction for precise control." P, high. Meta: "Avoid
requiring hands to be held above heart level or excessive reaching"; gestures not within 10 cm of the headset; arms at
rest. P, digest. Apple: indirect gestures so hands rest "in their lap or at their sides". P, verbatim.

**The Midas touch.** Jacob (TOIS 1991, on gaze): "Everywhere you look, another command is activated; you cannot look
anywhere without issuing a command ... the interface should act on the user's eye input when he wants it to and let
him just look around when that's what he wants, but the two cases are impossible to distinguish in general." P, high.
The same problem applies to hands that move to talk, to rest and to hold things; every guide answers it with gating:
Meta's "gating, such as proximity or hover state", MRTK's flat hand and gaze on the palm menu, Meta's microgestures
gated by hand posture and context. P. Mutasim et al. (ETRA 2021) measured gaze pointing confirmed by pinch, button or
dwell: pinch was slower and less accurate than a button but not significantly; dwell had the fewest errors but was
significantly slower. P, high for that setting (Leap Motion pinch).

**Number of gestures and memorability.** Meta: "a small number of very simple poses and gestures", "Too many gestures
... raise the chance of misrecognition" (P, digest); Ultraleap: "as few and as simple as possible" (P, digest); Apple:
custom "only when necessary" (P). Nacenta et al. (CHI 2013, 33 participants, sets of 22 free-form gestures per
condition): next-day recall 97 % for user-defined, 82 % pre-designed, 52 % random in experiment 1 (94 %, 89 %, 55 % in
experiment 3); errors were mostly association errors (which gesture means which command), not form errors. The
gestures were judged by an experimenter against video, not by a recogniser. P, high. Jansen (cited by Nacenta): 61 to
71 % recall of ten unfamiliar TV gestures (S). Kostic et al. (arXiv 2023): an 8-gesture mid-air vocabulary for
visualisation, 20 users, high recall except one gesture forgotten by 5 of 20 (75 %); gestures that resembled each other
caused lag (P, digest).

**Recognition from one RGB camera.** MediaPipe's gesture recognizer classifies seven static gestures plus none from
landmarks; its model card puts "Hand gestures involving motion (e.g. waving goodbye)" and "multiple hands" out of
scope, reports SS F1 93.9 to 95.5 % across perceived gender and skin tone groups, and says it "has not been tested in
'in-the-wild' smartphone camera conditions, including low-end devices, low light, motion blur". P, high. MediaPipe
Hands' paper recognises static gestures by rules on finger angles and only notes that landmark sequences "could" give
dynamic gestures (P, digest). GRLib (Warchocki et al., 2023): "the depth estimation of MediaPipe is problematic,
leading to the gestures 'forward' and 'backward' being frequently falsely detected", so they were dropped; on the rest,
dynamic detection precision was about 60 % overall (about 95 % ignoring repeated detections of the right gesture), and
complex trajectories (circle, infinity) had 0 % recall. P, high. A Chalmers thesis reports 93.1 % static against 88.1 %
dynamic on MediaPipe landmarks (U, search digest). So, from one RGB camera: static poses and pinch distance are the
reliable signals; motion along the camera axis is not; path-shaped gestures are worst.

**Direct manipulation against gesture commands.** The handle bar study found continuous bimanual manipulation "intuitive
to use, ease to remember" and multi-object operations "at least 2 to 3 times faster" than one at a time (P). Apple and
Android both prefer standard gestures and real-world mimicry over symbolic ones (P). No controlled study comparing
symbolic air gestures with menus for command selection in a headset was found (search 37); this is open.

### 3.4 Two hands: scale, rotate, move; and explode

**The established method.** Song et al.'s handle bar: both hands grab, the object follows the midpoint (translation),
the bar between the hands rotates it, and the distance between the hands scales it, all at once without mode switches;
it was designed for a sensor that "can only sense hand position but not hand orientation robustly" (Kinect), which is
the phone camera's situation too. P, high. Their scale was rate-based (`S = dL^2 / dt`, "A vigorous gesture gives a
larger scaling factor"); the shipping toolkits use the ratio of the current to the starting hand distance (MRTK3 code,
P; XRI's scale threshold and clamps, P, digest), which does not depend on speed or frame rate. Guiard's kinematic chain
(the non-dominant hand sets the frame, the dominant hand works in it) is the usual model for asymmetric two-hand tools
(S, via Hinckley et al.; Guiard's text refused, so its wording is U).

**Rotation for buildings.** MRTK3's `FromToRotation` of the handlebar leaves the roll about the bar undefined and lets a
model tip over; Meta's SDK offers a one-axis two-hand rotate transformer (P, digest). For a building on a table, rotate
about the vertical axis only (yaw) and keep it upright (U, our design; follows from the code read).

**Explode against scale.** Every framework maps "two hands pinch and move apart" to scale or zoom (table 3.1), and
Apple says not to give a familiar gesture an app-unique meaning (P). So a bare two-hand spread must stay scale. The
exploded view needs its own state. Prior art: Li et al. (SIGGRAPH 2008) explode a model along per-part explosion
directions with three controls: a one-click animated expand and collapse, direct manipulation ("As the user drags a
part p, the system slides p along its explosion direction", propagating to its ancestors so "the user [can] expand or
collapse an entire collection of parts, just by dragging a single part"), and riffling (parts move apart under the
pointer and return). P, high. Proposed mapping (U, design, to test in the browser check):

- Explode is a mode entered from the hand menu or an "explode" handle on the model, shown by a persistent badge and a
  different bounding-box colour. While it is on, two-hand scale is off.
- In the mode, the two-hand spread sets the explode factor: `e = clamp(e0 + (d - d0) / k, 0, 1)`, with `d` the hand
  distance, `d0` and `e0` at grab start, `k` about 0.4 m for the full range; a dead zone like XRI's
  `thresholdMoveRatioForScale` (about 2 cm) before anything moves, and a detent at `e = 0` (fully collapsed).
- One-hand pinch and drag on a storey or system slides it along its own explosion direction, as in Li et al.; release
  past half-way snaps to open or closed.
- Leaving the mode animates collapse. The app's own `EXPLODE` command already means "break a polyline into lines"
  (`src/js/engine/editing/drafting-modify.js:159`, P), so the view must be named differently (for example "Exploded
  view", command `EXPLODEVIEW`) and must never change the model.

**Scale: world in miniature against 1:1.** Stoakley et al. (CHI 1995): a hand-held miniature of the world beside the
1:1 view; users "adapted to the metaphor quickly", could manipulate through either view, and "if the WIM's scale is very
small, selection and manipulation become [too] difficult"; arm fatigue was minor because users raised the WIM to work
and lowered it to look. P, digest; high. MRTK: clamp scale with min and max (P). Proposed (U): two states, "table"
(the model fitted to about 0.5 m) and "1:1", with detents at 1:1 and at drawing scales (1:50, 1:100, 1:200, 1:500)
during two-hand scaling, and "go there" from the miniature to 1:1 (Pausch et al.'s flight into the miniature, S from
the SIGGRAPH history index only).

### 3.5 Hand-attached UI and readability

- Keep hand menus small: "the attentional cone of vision is roughly 10 degrees ... one column with three buttons works
  well"; use them for quick actions and world-lock large ones on hand drop or by grabbing them; billboard the menu
  toward the opposite shoulder; avoid buttons near the wrist's system button; place content on the ulnar side, "13 cm
  above the palm"; freeze the menu when the other hand comes near to stop jitter from overlapping hands. Microsoft
  design page, P verbatim; high.
- Prevent false activation with a flat palm and gaze at the hand (Microsoft, MRTK3 defaults in 3.1). P.
- Apple: reserve the area around the hand; "If possible, don't anchor content to a person's hands or wrists" (P).
- Target sizes: Microsoft, at least 2 degrees near (1.6 x 1.6 cm at 45 cm) and 1 degree far (3.5 x 3.5 cm at 2 m), P;
  Meta, 22 x 22 mm with 12 mm spacing for poke, P digest; Apple, centres 60 pt apart with 16 pt around (a visionOS
  point is an angle), P.
- Text: Microsoft's comfortable sizes are 0.65 to 0.8 degrees at 45 cm (5.1 to 6.3 mm) and 0.6 to 0.75 degrees at 2 m
  (20.9 to 26.2 mm); minimum legible 0.4 to 0.5 and 0.35 to 0.4 degrees. P, verbatim; high (HoloLens studies). Apple:
  reading content at least 1 m away. P.
- Follow and billboard: Apple warns against head-locked content ("can make them feel stuck"); MRTK's near menu follows
  within 30 to 60 cm (S, search digest of the MRTK page). Use a lazy follow with pin, not a head lock.

### 3.6 Feedback without haptics

- States: default, hover (targeted), pressed or grasped, released, each visually distinct; for direct touch also
  distance to the surface and contact; Microsoft's "ring" that shrinks to a dot as the fingertip nears; sounds on
  contact begin and end and on grab begin and end. P, verbatim (Microsoft); Meta says the same in brief ("Use visual
  and audio feedback to compensate for the lack of haptics"). High.
- Progress: Meta's palm pinch fills an icon before it fires (P, digest); long press needs visible progress (Meta, P).
  The app's pinch can show a ring that closes with the pinch strength (`1 - d^2 / 0.0016` in MRTK2, already in
  `hands-and-physics.md`).
- Hand rendering: keep hands visible when using UI, avoid flashing visuals (Meta, P digest); fade the hand as it nears
  the edge of the tracking volume to show tracking loss (Ultraleap blog, S search digest). Quest draws hand outlines
  in passthrough (the owner's screenshots; U for the rule).
- Confidence: MediaPipe gives handedness and presence scores (defaults 0.5) per frame (P). Proposed (U): draw the
  skeleton in a neutral colour above the presence threshold, dim it below, and refuse new pinches while dimmed.
- Unavailable actions must say so (Apple: "Indicate when a gesture isn't available", P) and, in this app, warn and toast
  (the build contract).

## 4. The proposed vocabulary

Three motor primitives (pinch, poke, palm-up) and two-hand pinch carry everything; the rest are tools chosen from the
menu and worked by direct manipulation. Ten interactions. "Phone" means the iPhone in cardboard with the rear camera
seeing the hands: 21 MediaPipe points, about 35 fps (the figure the parent study gives; to measure), no reliable
distance, a narrow camera field so two hands are often not both in view (U, to measure).

| # | Gesture | Function (app command) | Why (evidence) | Conflicts and guards | Touch / mouse | Phone (MediaPipe) |
|---|---|---|---|---|---|---|
| 1 | Point (hand ray on Quest; gaze on Vision Pro) then pinch | Select far element; hover shows its name | universal far select (3.1, six of six); Mutasim: pinch near a button in accuracy | not with palm facing user (Quest, Android); first-best hover and magnetism (Meta) | tap / click | cursor at the index tip's image position, pinch with hysteresis held 2 frames |
| 2 | Poke with the index finger | Press UI buttons and panels near the body | Meta, Apple, MS: poke for near UI; 22 mm / 2 degree targets | index only (Meta); pinch is not poke | tap / click | none (no depth); use 1 on panels |
| 3 | Pinch and drag, one hand | Move: on the model in review, orbit or slide the miniature; on a selected element with edit on, move it (MOVE) | pinch and drag is the standard one-point manipulation (3.1) | element edits only in edit mode, so a resting pinch cannot move walls | drag / one-finger drag | pinch-drag in the image plane only; no push-pull along the camera axis (GRLib) |
| 4 | Two hands pinch: move, turn, spread | Move, yaw-rotate and uniformly scale the model; detents at 1:1 and drawing scales | handle bar (Song et al.); ratio scale (MRTK3 code); every guide maps spread to scale | yaw only; min/max clamp (MS); 2 cm dead zone (XRI) | two-finger pinch and twist / wheel and drag | only when both hands are in view, else the menu's scale slider |
| 5 | Explode mode (from menu or handle), then two-hand spread or one-hand drag on a storey | Exploded view by storey or system, and back; never edits (EXPLODEVIEW, new) | Li et al.: one-click expand/collapse, drag along explosion direction; Apple: no new meaning for a standard gesture, so a mode | badge while on; scale off while on; detent at collapsed | slider and drag a storey / click to expand-collapse | one-hand drag on a storey, or the slider |
| 6 | Point at the floor or at a spot in the miniature, pinch, release | Go there: teleport at 1:1, or from the miniature to 1:1 at that spot (WALK) | teleport is the least sickening (Android); Stoakley's WIM; Android: limit flying | arc preview and a dimmed fade on the jump (Android) | double-click a spot / double-tap | gaze reticle plus pinch (no hand ray at depth) |
| 7 | Measure tool, then pinch at A, pinch at B | Distance with snaps to vertices and edges (DIST) | uses only primitive 1; Apple: standard gestures before custom | snapping magnetism; label in 0.65 degree text | click-click (DIST exists) | same, cursor at the index tip |
| 8 | Section tool, then grab the plane's handle and drag | Move the section plane; flip and exit from the menu (SECTIONTOOL, SECTIONFLIP, SECTIONEXIT) | handles with direct manipulation (MRTK BoundsControl) | handle visible only in the tool | drag the handle | pinch-drag the handle in the image plane |
| 9 | Non-dominant palm up, fingers open, look at it | Hand menu: up to 3 to 5 large buttons (tools, undo, explode, scale, exit); grab to world-lock | MS and MRTK3: palm-up gated by flat hand and gaze, ulnar side, 13 cm | never pinch with that palm (Quest, Android); on Vision Pro a floating toolbar instead (Apple) | the existing toolbar | palm-up flat hand detected from landmarks (static, reliable class), or a tap on the cardboard button |
| 10 | Undo button on the hand menu (poke) | Undo and redo (UNDO) | no reserved or familiar air gesture means undo; Apple: custom gestures not the only way; Android's Back belongs to the system | no swipe gesture (Meta: swipes are discrete and tiring; GRLib: dynamic gestures unreliable) | Ctrl+Z; three-finger swipe left on iOS (Apple's standard) | menu button |

Not proposed, with reasons: a flying gesture (Android advises against flying; continuous motion sickens); symbolic poses
for commands (Meta and Ultraleap "sparingly"; MediaPipe's own classifier has seven poses and none mean "section");
microgestures (native SDK only, not shown to reach WebXR, U); push and pull toward the camera on the phone (GRLib's
false detections); a two-hand spread that explodes without a mode (collides with scale in every framework).

## 5. Counter-evidence sought

- **For H5:** searched for a framework that makes a symbolic gesture set its core: none found. Apple's guide is the
  exception for hand menus and for the hand ray (it uses gaze); Ultraleap is a sensor maker whose guide covers fewer
  manipulation details. These narrow H5 but do not refute the core.
- **For H6, large vocabularies:** Nacenta et al. show 22 gestures recalled at 82 to 97 % the next day, and Kostic et
  al. 8 mid-air gestures recalled by most users; Ultraleap allows more interactions with onboarding. So "many
  gestures cannot be learned" is false. But those studies judged gestures by eye, not by a recogniser, ran for one or
  two days, and did not measure false activation in real use; the recognition evidence (GRLib, MediaPipe's model card)
  and the fatigue evidence (CE, handle bar) remain against large air-gesture sets.
- **Against the handle bar's comfort:** Song et al. themselves report fatigue at 20 to 30 minutes.
- **Against pinch as the select:** Mutasim et al. found pinch slower and less accurate than a button, not
  significantly; dwell was more accurate. So dwell is a reasonable accessibility option on the phone (U to test).
- **Against hand menus:** Apple reserves the hand area; Microsoft lists five placements that failed in its own research.
- **Against two-hand tools:** Android asks for one-handed alternatives; Apple says people may not have both hands
  free. Hence every two-hand interaction above has a one-hand or menu fallback.

## 6. Outcomes

- **H5: held for the core, with one exception.** Six frameworks define pinch select, near grab and poke, a far pointer
  confirmed by pinch, pinch and drag, and two-hand scale (five of six also two-hand rotate). Hand-attached menus are
  not common ground: Meta and Microsoft build them, Apple reserves the hand area for the system. High confidence (all
  from the vendors' own pages, four of them verbatim and MRTK3's code).
- **H6: held in its practical form, refuted in its strong form.** People can memorise 8 to 22 gestures (Nacenta,
  Kostic), so "magic gestures fail" is too strong. What fails is reliability and comfort: one-RGB-camera recognition of
  dynamic and depth-direction gestures is poor (GRLib), MediaPipe's classifier excludes motion and two-hand gestures,
  sustained raised arms tire within minutes (CE, handle bar), and every guide limits custom gestures and gates them.
  A few primitives plus visible menus and direct manipulation is what all six guides recommend. Medium-high
  confidence: no headset study directly compares a symbolic gesture set with menus for command selection.

## 7. Still open

- Meta's Quest help page on hand gestures (body not returned): the full list of Quest system gestures beyond palm pinch.
- Whether Quest Browser or Safari on Vision Pro deliver microgestures, system-gesture flags or hand joints to pages
  (`devices.md` owns this).
- Piumsomboon et al. (INTERACT 2013) full text: refused (Anubis page, 403); the agreement for scale gestures in AR is U.
- Guiard (1987) text: refused (403).
- The phone: pinch reliability, false activations per minute at rest and while talking, palm-up detection, two-hand
  visibility in the rear camera at arm's length, and real fps; all to measure in the phone experiment.
- The explode factor's range `k`, the dead zone and the scale detents: to tune in one browser check.
- Licences of Meta's Interaction SDK and Unity's XRI: not read (nothing is taken from their code; only methods).

## 8. References (all read 2026-11-23)

| Source | URL | What was read | Level |
|---|---|---|---|
| Meta, Hands interaction types | https://developers.meta.com/horizon/design/hands-interaction-types/ | whole page | P, digest |
| Meta, Hands design overview | https://developers.meta.com/horizon/design/hands/ | whole page and links | P, digest |
| Meta, Gesture design | https://developers.meta.com/horizon/design/hands-gesture-design/ | whole page | P, digest |
| Meta, Hands best practices | https://developers.meta.com/horizon/design/hands-best-practices/ | whole page | P, digest |
| Meta, Limitations and mitigations | https://developers.meta.com/horizon/design/hands-limitations-mitigations/ | whole page | P, digest |
| Meta, Hands technology | https://developers.meta.com/horizon/design/hands-technology/ | tracking rates | P, digest |
| Meta, Grab usage | https://developers.meta.com/horizon/design/grab_usage/ | whole page | P, digest |
| Meta, Input mappings | https://developers.meta.com/horizon/design/interactions-input-mappings/ | hand mappings | P, digest |
| Meta, Microgestures design | https://developers.meta.com/horizon/design/design-microgestures/ | whole page | P, digest |
| Meta, WebXR hands | https://developers.meta.com/horizon/documentation/web/webxr-hands/ | system gesture, pinch | P, digest |
| Meta, VRC Quest input 8 | https://developers.meta.com/horizon/resources/vrc-quest-input-8/ | criteria sentence | P, digest |
| Meta, ISDK hand pose detection | https://developers.meta.com/horizon/documentation/unity/unity-isdk-hand-pose-detection/ | poses, thresholds | P, digest |
| Meta, ISDK two-handed grab | https://developers.meta.com/horizon/documentation/unity/unity-isdk-two-handed-grab-interaction/ | transformers | P, digest |
| Meta, ISDK overview | https://developers.meta.com/horizon/documentation/unity/unity-isdk-interaction-sdk-overview/ | feature list | P, digest |
| Apple HIG, Gestures | https://developer.apple.com/design/human-interface-guidelines/gestures.md | whole page (change log to 2026-10-28) | P |
| Apple HIG, Designing for visionOS | https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos.md | whole page | P |
| Apple HIG, Eyes | https://developer.apple.com/design/human-interface-guidelines/eyes.md | whole page | P |
| Apple HIG, Spatial layout | https://developer.apple.com/design/human-interface-guidelines/spatial-layout.md | whole page | P |
| Microsoft, MRTK3 Hand menu | https://learn.microsoft.com/en-us/windows/mixed-reality/mrtk-unity/mrtk3-uxcomponents/packages/uxcomponents/hand-menu | whole page | P |
| Microsoft, MRTK3 BoundsControl | https://learn.microsoft.com/windows/mixed-reality/mrtk-unity/mrtk3-spatialmanipulation/packages/spatialmanipulation/bounds-control | whole page | P |
| Microsoft, Hand menu (design) | https://learn.microsoft.com/en-us/windows/mixed-reality/design/hand-menu | whole page | P |
| Microsoft, Typography | https://learn.microsoft.com/en-us/windows/mixed-reality/design/typography | size tables | P |
| Microsoft, Interactable object | https://learn.microsoft.com/en-us/windows/mixed-reality/design/interactable-object | states, sizes, audio | P |
| MRTK3 source, BSD-3-Clause | https://github.com/MixedRealityToolkit/MixedRealityToolkit-Unity (commit 83c8c1d) | `LICENSE.md`; `ObjectManipulator/MoveLogics/ScaleLogic.cs`, `RotateLogic.cs`; `Solvers/HandConstraintPalmUp.cs` | P, code |
| Unity XRI 3.0, Near-Far Interactor | https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@3.0/manual/near-far-interactor.html | whole page | P, digest |
| Unity XRI 3.0, XRGeneralGrabTransformer API | https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@3.0/api/UnityEngine.XR.Interaction.Toolkit.Transformers.XRGeneralGrabTransformer.html | scaling properties | P, digest |
| Unity XR Hands 1.4, Finger shapes | https://docs.unity3d.com/Packages/com.unity.xr.hands@1.4/manual/gestures/finger-shapes.html | whole page | P, digest |
| Ultraleap, Design principles | https://docs.ultraleap.com/xr-guidelines/Getting%20started/design-principles.html | whole page | P, digest |
| Ultraleap, Design considerations | https://docs.ultraleap.com/xr-guidelines/Getting%20started/DesignConsiderations.html | whole page | P, digest |
| Android XR, Considerations | https://developer.android.com/design/ui/xr/guides/considerations | whole page | P |
| Android XR, navigation help | https://support.google.com/android-xr/answer/16639048 | gesture list | P, digest |
| ARCore for Jetpack XR, Hands | https://developer.android.com/develop/xr/jetpack-xr-sdk/arcore/hands | whole page | P |
| Hincapie-Ramos, Guo, Moghadasian, Irani, Consumed Endurance, CHI 2014, doi 10.1145/2556288.2557130 | https://perso.lisn.upsaclay.fr/anab/teaching/evaluation/papers/consumed-endurance.pdf | full text | P |
| Song, Goh, Hutama, Fu, Liu, A handle bar metaphor, CHI 2012, doi 10.1145/2207676.2208585 | https://sutd-cgl.github.io/supp/Publication/papers/2012-CHI-HandleBar.pdf | full text | P |
| Nacenta, Kamber, Qiang, Kristensson, Memorability of pre-designed and user-defined gesture sets, CHI 2013 | https://research-repository.st-andrews.ac.uk/bitstream/10023/3486/5/NacentaKamberQiangKristensson_GestureMemorability.pdf | full text | P |
| Jacob, The use of eye movements in HCI techniques, ACM TOIS 9(3), 1991 | https://marcjohnson.fr/wp-content/uploads/2020/12/1991-Jacob-The-Use-of-Eye-Movements-in-human-computer-interaction-techniques.pdf | Midas touch section (text layer of a scan) | P |
| Mutasim, Batmaz, Stuerzlinger, Pinch, click, or dwell, ETRA 2021 | https://vvise.iat.sfu.ca/user/data/papers/pinchclickdwell.pdf | abstract and setup | P |
| Kostic, Dumas, Pratt, Beyer, Exploring mid-air hand interaction in data visualization, arXiv 2311.15372 | https://arxiv.org/html/2311.15372v1 | first 100,000 characters | P, digest |
| Stoakley, Conway, Pausch, Virtual reality on a WIM, CHI 1995 | https://www.cs.cmu.edu/~stage3/publications/95/conferences/chi/paper.html | full text | P, digest |
| Li, Agrawala, Curless, Salesin, Automated generation of interactive 3D exploded view diagrams, SIGGRAPH 2008 | https://grail.cs.washington.edu/projects/exview3D/exview3D-SIG08.pdf | abstract, section 5 | P |
| Google, MediaPipe gesture recognizer guide | https://developers.google.com/edge/mediapipe/solutions/vision/gesture_recognizer | gestures, defaults, latency | P, digest |
| Google, Hand gesture classification model card (2022) | https://huggingface.co/litert-community/MediaPipe-GestureRecognizer/resolve/main/model_card_hand_gesture_classification_with_faireness_2022.pdf | whole card | P |
| Zhang et al., MediaPipe Hands, arXiv 2006.10214 | https://ar5iv.labs.arxiv.org/html/2006.10214 | tables 1 to 3, gesture section | P, digest |
| Warchocki, Vlasenko, Eisma, GRLib, arXiv 2310.14919 | https://arxiv.org/pdf/2310.14919 | dynamic gesture results | P |
| Piumsomboon, Clark, Billinghurst, Cockburn, User-defined gestures for AR, INTERACT 2013 | https://inria.hal.science/hal-01501749v1/document | refused (Anubis page) | U |
| Guiard, Asymmetric division of labor, J. Motor Behavior 1987 | https://web-archive.southampton.ac.uk/cogprints.org/625/1/jmb_87.html | refused (403) | U (principle S via Hinckley et al. 1997, search digest) |
| The app's code | `src/js/engine/commands/command-catalogue.js`, `src/js/engine/editing/drafting-modify.js` | command names; EXPLODE | P |
