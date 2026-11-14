# Walkthrough W1: walking through the model

Research note for phase **V202, Walkthrough W1: walk** (the owner, 2026-11-14: "a walk through feature. like i can
be in a car, walking, swimming and all that stuff"; on WebAssembly: "i saw people make web app game"; and "lets think
and document that on notion also, if this can be a new phase put it where appropriate"). Started 2026-11-14 by Claude.
Status: **research done; the owner's decisions made 2026-11-14** (part 11). Spec and work orders: `docs/work-orders/v202/`.

## 1. Abstract

**Question.** How should the app let a person walk through their own model, at their own eye height, stopped by walls,
up stairs and ramps, on desktop, tablet and phone, within the build contract (ES5, vetted libraries only, offline,
loaded on demand)? And which physics, if any, should do the walking, so that driving, flying and swimming (W2-W4)
can follow on the same base?

**Answer.** Walking is a character controller: a capsule moved by a kinematic query against the model's triangles,
not a falling rigid body. Two maintained WebAssembly engines have one ready: Jolt Physics (MIT, used in two
PlayStation games) and Rapier (Apache-2.0). three.js's own Octree also walks, with no engine. On a test course and a
60,000-triangle town measured here, all three cost far under a millisecond a frame; all three load offline. Jolt
passed every case with its documented settings, is half Rapier's download gzipped, and carries the car (its
wheeled vehicle) and water (its buoyancy) W2 and W4 need. Rapier stalled on flat ground with its snap to ground on,
as an open issue on its tracker reports. The Octree climbs slopes it should refuse and took over five seconds to build
the town's collision.

**Recommendation.** Jolt Physics 1.1.1's `wasm-compat` build, bundled unchanged by esbuild into one classic script
(as `tools/three` does three.js), pinned in `runtime/`, loaded only when Walk starts, behind an adapter in
`src/js/engine/walk/`. The walker is a V169 person: their eye height and walking speed from the standards registry,
and a wheelchair user who cannot climb a step. The rendered view needs a moving mode (one pass a frame) while walking.

## 2. The question and the hypotheses

| # | Hypothesis (falsifiable) | Outcome |
|---|---|---|
| H1 | A WebAssembly engine's character controller climbs a 0.18 m riser, stops at a 0.40 m curb, climbs a 1:12 ramp, refuses a 40 degree slope and does not pass through a wall at 10 m/s | **Held** for Jolt and Rapier (e01). The Octree fails the slope |
| H2 | One frame of walking costs under 1 ms on a 60,000-triangle model | **Held** for all three (e01: 0.006 to 0.032 ms mean, worst 4.4 ms once for Rapier) |
| H3 | The engine loads as one classic script from a `file://` page, as three.js does | **Held** for Jolt and Rapier in Chromium (e02). Not tested in Safari or Firefox |
| H4 | The engine adds under 1 MB gzipped | **Held** for Jolt (0.95 MB), **failed** for Rapier (1.65 MB) |
| H5 | No engine is needed: three.js's Octree walks as well | **Failed**: it climbs a 40 degree slope, and building its tree took 5.1 to 5.6 s for the town on one thread |
| H6 | The app's existing camera and rendered view can show a walk without change | **Failed**: the near plane is 0.5 m (a wall 0.3 m away vanishes), and the rendered view refines a still picture over many passes and starts again on every move (part 8) |
| H7 | Pointer lock (the mouse captured for looking) works on every device | **Failed**: not on iOS Safari at all (MDN's data); phones and tablets need on-screen controls |

## 3. Method

- **Sources by kind.** Specifications and data: MDN's browser-compat-data (`api/Element.json`); the 2010 ADA
  Standards and the IBC as the app's registry already cites them. Vendors' own documents: SketchUp's Help, Autodesk
  Navisworks's Help (2024, Freedom 2025), Epic's Unreal Collab Viewer docs. Open implementations read as text:
  three.js r180's `games_fps.html`, `Octree.js`, `PointerLockControls.js`; three-mesh-bvh's `characterMovement.js`;
  the READMEs of Jolt Physics, JoltPhysics.js and Rapier; both engines' TypeScript declarations as installed.
  Packages: npm's registry (versions, licences, dates). Counter-evidence: both engines' issue trackers.
- **Search log.** Part 12 lists each source. Searches: GitHub issue search `repo:dimforge/rapier is:issue character
  controller` (40 hits), `repo:dimforge/rapier.js is:issue character controller` (15), `repo:jrouwe/JoltPhysics.js
  is:issue memory` (12), `repo:jrouwe/JoltPhysics is:issue CharacterVirtual` (48); web searches for SketchUp's,
  Enscape's and Twinmotion's walk modes. Enscape and Twinmotion: no official page on walk physics found; set aside
  (forum posts only, part 10).
- **Experiments.** e01 and e02 in `docs/research/experiments/w1-walk/` (scripts, raw JSON, README).
- **Independent check.** A separate research agent re-read the sources behind every fact the code will use, on
  2026-11-14: 12 facts, 11 confirmed at their primary source, 1 (the IBC riser) confirmed only through the 2025 California
  Building Code (S). None failed. Part 12's last column has each verdict.

## 4. Findings

### 4.1 What walking is, and how professionals offer it (practice)

- SketchUp's Walk tool puts the eye at **5 ft 6 in (1.68 m)** above the point clicked, keeps that height up and down
  "inclines or stairs", has collision on by default, and **Alt walks through walls** (SketchUp Help). P, high.
- Navisworks: Collision, Gravity, Auto Crouch and Third Person, all **off by default**, set per user; the viewer is a
  collision volume of a set radius and height, with an eye offset below its top (Navisworks Help 2024, Freedom
  2025). P, high. No default values are published.
- Unreal's Collab Viewer (Epic's template for architecture): keys I, U, O switch Walk, Fly, Orbit; in Walk "you're
  held down to the ground by gravity" and collide with objects that have collision; Fly passes through everything
  (Epic's docs). P, high.
- Enscape and Twinmotion offer walk modes too; their physics is not documented in pages found (U, set aside).
- **What follows for us:** a Walk and a Fly, collision on with a key to pass through (SketchUp's Alt), gravity in
  Walk only, the eye height editable. Third person (Navisworks) is W2's car view, not W1's.

### 4.2 The walker: who, how tall, how fast (the standard, already in the registry)

The registry (V167) and V169's people already hold every number the walker needs, each with its source and edition:

- Eye height from height: NASA's Human Integration Design Handbook, `body.hidh` (`registry.js:260`); a V169 person's
  eye height is computed from it (`assets/scale-assets.js:49-58`). P (as V169 read it).
- A wheelchair user: eye height 1.152 m, the mean of all device users (`wheel.awmp`, `registry.js:267-271`, the
  Anthropometry of Wheeled Mobility report). P.
- Walking speed: 1.34 m/s mean, 0.26 m/s spread (`hm.walk`, Helbing and Molnar, `registry.js:370-373`, which the
  registry itself holds at S); 1.067 m/s, the MUTCD's clearance speed (`mutcd.walk`, `registry.js:276-279`). P.
- Ramps and slopes: 1:20 walking surface, **1:12 ramp** (ADA 403.3, 405.2, `registry.js:123`, `registry.js:453`). P.
- Stairs: the IBC's riser is 7 in (0.178 m) at most and 4 in at least (1011.5.2). Not yet in the registry; it sets
  the step-up height (part 7). S: read in the 2025 California Building Code, which adopts IBC 2024 with the same
  section; codes.iccsafe.org refused the request (403). To be read at the ICC with the build.

**A finding with design weight:** walking as the wheelchair user (step-up 0, the steepest climb 1:12) turns the walk
into an accessibility check: a level change with no ramp stops them. No source found offers this in a browser BIM
app; it is our idea, held as such.

### 4.3 The engines (open implementations, read and run)

| | Jolt Physics 1.1.1 (JoltPhysics.js) | Rapier 0.21.0 (rapier3d-compat) | three.js 0.186.1 Octree | cannon-es 0.20.0 |
|---|---|---|---|---|
| Licence | MIT | Apache-2.0 | MIT (already shipped) | MIT |
| Last release | 2026-10-23 | 2026-09-25 | three's own | 2022-08-12 |
| Character controller | `CharacterVirtual`, `ExtendedUpdate` (stairs, stick to floor) | `KinematicCharacterController` (autostep, snap to ground) | none: a capsule pushed out of triangles, as `games_fps.html` does | none |
| Car (W2) | `WheeledVehicleController` | `DynamicRayCastVehicleController` | none | `RaycastVehicle` |
| In production | Horizon Forbidden West, Death Stranding 2 (its README) | many web projects | three's examples | (unmaintained) |
| Memory | manual: every object made must be `destroy`ed | `free()` on the world | garbage collected | garbage collected |

Levels: licences and dates P (npm); controllers P (their declarations, run in e01); production use P as the vendor
states it. cannon-es is set aside: no character controller, no release in three years.

### 4.4 What was measured (e01, e02; part 6 has the numbers)

- Jolt and Rapier pass all five course cases; the Octree walks up the 40 degree slope (feet at 2.01 m). P, high
  (Node's V8; Chromium's engine is the same, phones not tested).
- Per frame in the town, all three are 0.006 to 0.032 ms mean: the physics is not the cost; drawing is.
- Building the collision for 60,002 triangles: Rapier about 40 ms, Jolt about 250 ms, the Octree over 5 s.
- Rapier's walker stalled on flat ground with snap to ground on, losing about 2.5 m twice in 10 s; with it off it
  walked the path. Its tracker has the same report open (dimforge/rapier#1019, 2026-09-25, "loses a step's horizontal
  motion on flat ground"). Its reporter traces it to the hit normal being a hair off vertical (1 - 2^-53 after GJK's
  normalisation), which sends Rapier's slope handling down a branch keeping 0 to 5% of the move; the proposed fix is not
  merged. High confidence it is Rapier's and not our settings: Jolt's walker, given the same input, walked the path,
  and the cause is in Rapier's own code.
- Both load as one classic script from `file://` in Chromium 153 and start in 47 to 152 ms there.

### 4.5 Controls on each device

- Desktop: pointer lock for looking, WASD and the arrows to move, Shift to run. Pointer lock is supported in
  Chrome, Firefox and desktop Safari (MDN). P.
- **iOS Safari has no pointer lock** (`safari_ios: false`); Chrome on Android from version 144 (MDN). P. So on phone
  and tablet: a joystick drawn on the left thumb's side to move and a drag anywhere else to look. nipplejs (MIT,
  1.0.4) does the joystick, but it is about 100 lines of our own ES5 with the app's existing touch handling
  (`ui/touch-input.js`), so no library is proposed.

## 5. The alternatives compared

Criteria, set before the comparison: (a) passes the course; (b) under 1 ms a frame on 60k triangles; (c) loads
offline as a classic script; (d) download; (e) collision built in under 1 s; (f) carries W2's car and W4's water;
(g) licence and maintenance.

| | (a) course | (b) frame | (c) offline | (d) gzip | (e) build | (f) W2/W4 | (g) |
|---|---|---|---|---|---|---|---|
| **Jolt 1.1.1** | 5 of 5 | 0.01 ms | yes | 0.95 MB | 0.25 s | car, buoyancy | MIT, active |
| Rapier 0.21.0 | 5 of 5, stalls on flat ground | 0.03 ms | yes | 1.65 MB | 0.04 s | car, no buoyancy | Apache-2.0, active |
| three Octree | 4 of 5 (climbs 40 deg) | 0.01 ms | already loaded | 0 | 5.1 s, blocks the page | none | MIT |
| Our own (ray casts) | to build | to build | yes | 0 | to build | none | ours |

**Recommendation: Jolt.** It is the only one meeting every criterion. What would change it: Jolt failing in Safari or
on a phone (part 10), or the owner preferring zero download for W1 alone, in which case the Octree with our own
slope rule, built in a Worker, would do for walking only, and W2 would bring an engine anyway.

## 6. The experiments

e01 (`physics-bench.mjs`, `e01-results.json`): Node 22.23.4, three runs each. Course end positions (x, feet height):

| Lane | Jolt | Rapier | Octree | Must |
|---|---|---|---|---|
| step 0.18 m | 6.99, 0.181 | 6.54, 0.20 | 6.76, 0.18 | on top |
| curb 0.40 m | 2.73, 0 | 2.73, 0.02 | 2.75, 0 | stopped before x = 3 |
| ramp 1:12 | 6.97, 0.332 | 6.85, 0.342 | 6.97, 0.332 | climbing |
| slope 40 deg | 2.90, 0 | 2.91, 0.027 | 5.31, 2.014 | stopped |
| wall at 10 m/s | 2.73, 0 | 2.73, 0.02 | 2.75, 0 | stopped before x = 3 |

Town, 5000 boxes, 60,002 triangles, 600 frames at 60 Hz, three runs (mean / p95 / worst frame, ms; build ms):

| | run 1 | run 2 | run 3 |
|---|---|---|---|
| Jolt | 0.0100 / 0.0203 / 0.34; 254 | 0.0089 / 0.0174 / 0.08; 263 | 0.0088 / 0.0164 / 0.13; 237 |
| Rapier | 0.0320 / 0.0494 / 0.27; 54 | 0.0283 / 0.0386 / 0.10; 40 | 0.0286 / 0.0398 / 0.20; 39 |
| Octree | 0.0059 / 0.0091 / 0.06; 5149 | 0.0097 / 0.0099 / 1.96; 5235 | 0.0062 / 0.0097 / 0.10; 5645 |

End of the town walk: Jolt (46.00, 33.72), Octree (46.00, 33.75), Rapier (49.79, 32.55). Rapier variants by hand: snap
to ground off ends at (46.22, 34.22), no stall; autostep off still stalls. Engine start in Node: Rapier 79 to 88 ms;
Jolt 97 to 992 ms across six runs (in Chromium 128 to 152 ms, e02), so Node's figure is not the browser's.

e02 (`file-url-check.mjs`, `e02-results.json`): Chromium 153.0.8010.12, `file://`, three runs: Rapier's bundle 4,337,501
bytes, loaded 31 to 40 ms, started 47 to 55 ms; Jolt's 4,010,952 bytes, loaded 52 to 62 ms, started 128 to 152 ms; no
console errors. three.js's own bundle, for scale: 859,434 bytes.

A first e01 run started the town walk inside a building's corner; Rapier then spent 3 ms a frame pushing out. It is
discarded, and recorded because a walker placed inside a wall (a saved position after an edit) is a real case.

## 7. Edges

- **The step-up height.** IBC risers are at most 0.178 m and curbs are usually 0.15 m; a walker that steps 0.25 m
  climbs both and is stopped by a 0.40 m curb or a seat wall. The wheelchair user steps 0 m.
- **The steepest climb.** 35 degrees stops a person on an embankment; the wheelchair user's is 1:12 (4.76 deg).
- **The near plane.** The app's projection keeps 0.5 m as its near plane below 1000 m (`webgl.js:33`); a walker with
  a 0.25 m radius stands 0.25 m from a wall and would see through it. Walking needs about 0.05 m.
- **The field of view** is fixed at about 45 degrees vertical (`webgl.js:41`, f = 1.2 H); games use wider. A setting.
- **Starting inside something.** A walker placed inside a wall (after an edit moved it there) costs time and may be
  pushed out the wrong side; the start should be found by a downward ray from the eye.
- **Big sites.** A V198 terrain plus a city's LOD blocks may pass 500,000 triangles; Jolt's 0.25 s for 60,000
  suggests about 2 s, so the collision is built per element (part 8) and only near the walker. U until measured.
- **Edits while walking.** An element changed in Properties must rebuild its collision only.
- **Glass, doors and open voids.** Glass is solid; a door is open or shut by its state; a void with no floor falls.

## 8. What the app already has

- **The rendered view** (V194) keeps every element as a record keyed by its signature and rebuilds only changed ones
  (`render/rendered-core.js:220-230`); the collision can follow the same keys, one Jolt body per element.
- **It refines a still picture**: each camera move restarts the accumulation (`rendered-view.js:159-188`), and the
  shadows are framed around the orbit's focus and reach (`rendered-core.js:239-258`). Walking moves every frame, so
  it shows the first pass only and the shadow frame follows the wrong point. W1 needs a moving mode: one pass a
  frame with filtered shadows framed around the walker, refining again when the walker stops.
- **The camera** is an orbit: a focus, yaw, pitch and distance (`core/state.js:42`), saved with views and tabs
  (`views/saved-views.js:129`). A walk sets the eye at the walker's eyes and the focus a metre ahead; no new camera.
- **Loading a runtime** from `runtime/` beside the page or Pages, with SRI (`rendered-view.js:69-96`); a physics
  script loads the same way.
- **People** with eye heights and speeds (V169, `assets/scale-assets.js`), and V171's **streets** for W2.

## 9. Risks and threats to validity

- One machine, one browser. Phones may be 5 to 10 times slower; the physics has that margin (0.03 ms of 16.7 ms),
  the drawing may not.
- The course is synthetic boxes; real models have thin walls, small gaps and bad normals. Jolt's mesh shape is
  two-sided by default; checked only on our boxes.
- Jolt's JavaScript needs every object destroyed by hand; a leak per walk would grow memory. The adapter owns them.
- Rapier's stall is reported upstream with its cause; a fixed Rapier would change criterion (a), not (d) or (f).
- The 4 MB script is parsed on Walk's first press: about 0.2 s on this machine, more on a phone.

## 10. What is still open (U)

- Safari and Firefox, and any phone or tablet: not available here. To test when the owner can, or by the browser
  check in the build on the devices the owner has.
- Enscape's and Twinmotion's walk physics: no official page found.
- The IBC riser read at the ICC itself (S here, through California's adoption).
- 500,000-triangle sites: not measured.

## 11. The owner's decisions

Asked 2026-11-14. Recommended answers first.

| # | Question | Recommended | Other choices |
|---|---|---|---|
| D1 | Which engine does the walking? | Jolt 1.1.1 (MIT, 0.95 MB gzipped, car and water later) | Rapier; three.js's Octree with our own slope rule (no download, walking only) |
| D2 | Who walks? | A V169 person: their eye height and speed; a wheelchair user walks too and is stopped by steps (an accessibility check) | A fixed 1.68 m eye height (SketchUp's) |
| D3 | How high a step does a walker climb? | 0.25 m (IBC risers and curbs pass, a 0.40 m curb stops) | 0.20 m; 0.30 m |
| D4 | Where can one walk? | Both views: the shaded view and the rendered view, which gets a moving mode while walking | The rendered view only |
| D5 | Phone and tablet controls | Our own joystick and drag to look, no library | nipplejs (MIT) |
| D6 | Passing through walls, and flying | Alt (or a button) passes through, as SketchUp; F switches Walk and Fly, as Unreal | Walk only in W1 |
| D7 | The rest of the series | W2 drive (V171's streets, Jolt's car), W3 fly and drone, W4 swim (water, buoyancy), W5 record a path; as "later" rows until W1 is built | Another order |

The owner's answers, 2026-11-14, in their words, and what follows from each:

- **D1 engine:** "jolt". Jolt Physics 1.1.1.
- **D2 who walks:** "for walk through it would be me the user of the app, there should be like a thrid person view or
  eye view walking like in video games where u can switch mode". The walker is the user, seen from their own eyes
  (first person) or from behind and above their figure (third person), switched by one key or button, as games do.
  Their figure is a V169 person (the registry's mean adult by default); the walk settings may change it, the
  wheelchair user included, so the accessibility check of 4.2 stays available but is not the default. (Our reading
  of the answer; said here so it can be corrected.)
  The owner also said: "currently in the simulation i dont see people just car". V171 draws walkers in 3D as a
  column with a head (`simulation/traffic-draw.js:18`); why none show is a separate question, not this phase's.
- **D3 step height:** "idk about this one. use what standard." No standard sets how high a walker steps; the codes
  set how high a stair's riser may be. The walker climbs every code-compliant stair: the steepest riser where the
  site is, plus the variation a flight may have. The IRC's riser is 7 3/4 in (196 mm) at most (R311.7.5.1) with 3/8 in
  (9.5 mm) between the greatest and smallest riser of a flight; the IBC's 7 in (1011.5.2). Some places amend the IRC
  upward: Philadelphia (the owner's city) and North Carolina to 8 1/4 in (210 mm). So the step-up is the registry's
  steepest riser for the site's place plus 3/8 in: 0.206 m under the model IRC, 0.219 m in Philadelphia. Levels: the IRC
  figure S (several jurisdictions' adoptions agree: South Carolina's regulation 8-1210, Boise's and Des Moines's
  handouts); Philadelphia's amendment U (seen only in a search's summary of its code library); both to read at the source before the
  registry record is written (a Claude task). The slope a walker climbs stays 35 degrees; a wheelchair user's step-up
  is 0 and their slope 1:12 (ADA 405.2).
- **D4 views:** "all view, the render or plain is just a view (wirefram, detail, rendered, ... just like revit).
  this moving simulation walkthrough can switch mode". Walking works in every visual style the app has, as Revit's
  navigation works in each of its visual styles; the rendered view gets its moving mode.
- **D5 phone and tablet:** "joystick". Our own on-screen joystick.
- **D6 walls and flying:** "idk do whats standard". From the prior art in 4.1 and the games' convention: W, A, S, D
  or the arrows to move, Shift to run, the mouse to look (pointer lock), Space to jump in Walk and to rise in Fly, C to
  sink in Fly; hold Alt to pass through walls (SketchUp's key, P); F switches Walk and Fly (Unreal's Collab Viewer has
  the two modes, P, on I and U; F is ours); V switches first and third person (a common games key, U: a convention,
  not a standard); Esc leaves the walk (browsers release pointer lock on Esc, P). Every action also has a button.
- **D7 the series:** "sure". W2 drive, W3 fly and drone, W4 swim, W5 record a path.

## 12. References

All read 2026-11-14. Level P unless said. Check: the independent reader's verdict (part 3).

| Source | What was read | URL | Level | Check |
|---|---|---|---|---|
| SketchUp Help, Walking through a model | Position Camera 5 ft 6 in, Walk, collision, Alt | https://help.sketchup.com/sketchup/walking-through-model | P |confirmed |
| Autodesk Navisworks 2024 Help, Collision dialog | collision, gravity, crouch, defaults off | https://help.autodesk.com/cloudhelp/2024/ENU/Navisworks/files/GUID-59545147-5F18-4078-B8EA-6A042DFCFE4B.htm | P |practice only, nothing the code uses |
| Autodesk Navisworks Freedom 2025, Default Collision | the same, per session | https://help.autodesk.com/cloudhelp/2025/ENU/Navisworks-Freedom/files/GUID-B9B5164F-C8E9-491E-BDAA-2EC24D858051.htm | P |practice only, nothing the code uses |
| Epic, Interacting with the Collab Viewer | Walk, Fly, Orbit keys, gravity | https://dev.epicgames.com/documentation/en-us/unreal-engine/interacting-with-the-collab-viewer-in-unreal-engine | P |practice only, nothing the code uses |
| Jolt Physics README | licence, production use, determinism | https://github.com/jrouwe/JoltPhysics | P |confirmed |
| JoltPhysics.js README and `types.d.ts` 1.1.1 | builds (`wasm-compat` embeds the WASM), CharacterVirtual | https://github.com/jrouwe/JoltPhysics.js | P |confirmed |
| Rapier README and rapier3d-compat 0.21.0 declarations | licence, KinematicCharacterController | https://github.com/dimforge/rapier, https://www.npmjs.com/package/@dimforge/rapier3d-compat | P |confirmed |
| dimforge/rapier#1019 | stall on flat ground, its cause and proposed fix (read by the check) | https://github.com/dimforge/rapier/issues/1019 | P |confirmed |
| three.js r180 `games_fps.html`, `Octree.js`, `PointerLockControls.js` | Capsule against Octree, 5 substeps, gravity 30 | https://github.com/mrdoob/three.js/tree/r180/examples | P |confirmed |
| three-mesh-bvh `characterMovement.js` (MIT) | a capsule against a BVH, the same method | https://github.com/gkjohnson/three-mesh-bvh | P |practice only, nothing the code uses |
| MDN browser-compat-data `api/Element.json` | `requestPointerLock` support | https://github.com/mdn/browser-compat-data | P |confirmed |
| npm registry | versions, licences, dates of the four engines, nipplejs | https://registry.npmjs.org | P |confirmed |
| The app's registry | `hm.walk`, `mutcd.walk`, `walk.speed`, `body.hidh`, the wheelchair record, ADA | `src/js/engine/standards/registry.js` | P |confirmed |
| 2010 ADA Standards 405.2 | ramps 1:12 | https://www.access-board.gov/ada/ | P |confirmed |
| IRC R311.7.5.1 risers, through South Carolina's regulation 8-1210 | 7 3/4 in at most, 3/8 in variation | https://www.law.cornell.edu/regulations/south-carolina/R-8-1210 | S | to read at the ICC |
| Philadelphia's amendment of the IRC risers | 8 1/4 in (210 mm) | https://codelibrary.amlegal.com/codes/philadelphia/latest/philadelphia_pa/0-0-0-272271 | U (a search summary only) | to read |
| IBC 1011.5.2, through the 2025 California Building Code | risers 7 in at most, 4 in at least | https://gocodebook.com/library/us/ca/ca-building-code/chapter-10-means-of-egress/section-1011-stairways | S |confirmed through CA's adoption |
