# Scale: scan an object, find what fits, stand in it at 1:1

The owner (2026-10-18), sharing github.com/ThomasZhang223/Scale: "this is my vision for interior
design. i want to scan objects or have AI do it for me." This note covers three things: what Scale
is, what was read and tested from here, and what the app can take under its own rules (one ES5
file, no dependencies, free and keyless data, credited). The owner's choices are asked at the end.

Scale was cloned read-only, outside this repository, at commit `d8b837a` (2026-10-14). It was read
as text and nothing in it was run. Its licence is MIT (Copyright 2026 Thomas Zhang). Its screenshots
and video are not copied here.

## Sources

| Source | What was read (2026-10-18) | Level |
|---|---|---|
| Scale's `README.md`, `BUILD_DOC.md`, `.claude/contracts.md` | The pipeline, the four schemas (RoomCapture v1, Object v1, Placement and Version v1, FitReport v1), the mesh normalisation contract, the conventions | P (for Scale) |
| Scale's `services/fit/app/fit.py` | The four fit checks, line by line | P |
| Scale's `services/gen/BINDING.md` | The scale binding, its validation and its distortion labels | P |
| Scale's `apps/mobile/modules/room-capture` and `object-measure` (README and Swift) | RoomPlan to RoomCapture v1, with true north; LiDAR raycast-and-grow measurement | P (for Scale's code) |
| Scale's `apps/xr/README.md`, `fixtures/` | The Quest page, the raw RoomPlan sample, the fixture shapes | P |
| Scale's `fixtures/library-models.ATTRIBUTION.md` | 100 library models, all from Poly Haven, CC0 | P |
| Apple, RoomPlan reference (developer.apple.com, its documentation JSON) | `CapturedRoom`, `Surface`, `Object`, `Section`, `Confidence`, `USDExportOptions`, `CapturedStructure` | P |
| Poly Haven: `polyhaven.com/license`, the API's `README.md` and `ToS.md` (GitHub), and the API itself | The licence, the API terms, `/assets`, `/info`, `/files`; CORS tested | P, and tested |
| Hugging Face: `spaces-zerogpu.md` (hub-docs on GitHub), the Spaces API | ZeroGPU's daily quotas; four image-to-3D Spaces, their state, Gradio versions and API names; CORS tested | P, and tested |
| Model licences: TRELLIS.2-4B's model card (MIT); Stable Fast 3D's `LICENSE.md` (GitHub); Hunyuan3D-2's `LICENSE` | The terms that matter for an app that may be sold | P |
| MDN's browser-compat-data (GitHub): `XRSystem`, `XRSession`, `XRHitTestSource`, `XRDepthInformation` | Which browsers run WebXR | P (for MDN's data) |
| The app's own code | Imports (DXF, IFC, OBJ, STL, SKP, JSON, GeoJSON, KML, CityJSON, LandXML); no glTF or GLB import; no WebXR; doors with no hinge or swing | P |

## What Scale is

Scale is a hackathon build (Hack the North 2026) of five services, an iPhone app and a Quest page:

```
room + object -> RoomPlan / LiDAR -> image or text query -> SigLIP2 retrieval + Shopify
-> verified dimensions -> deterministic fit check -> 2D->3D if no mesh exists
-> metric GLB binding -> 1:1 placement in Quest -> exact variant and checkout
```

Its ideas worth keeping:
- **The measurement gives size and the generator gives shape.** A generated mesh is scaled once,
  to the measured box. Nothing downstream rescales it.
- **A measured box comes first.** It shows with its real numbers in under a second, while the mesh
  is still being generated (`state: "measured"`).
- **Transport is JSON, never USDZ.** The room travels as wall transforms, opening rectangles and
  object boxes, and is rebuilt from those primitives.
- **Fit is a filter, never a similarity.** Style can be a vector search. Fit is a range test on
  width, depth and height, and a size without trustworthy provenance is marked unverified.
- **"The LLM never emits a coordinate."** A language model may turn a wish into an objective and
  constraints, and a solver places the furniture. An over-full room is reported as infeasible, with
  what to drop.

What it depends on, and the app cannot: Apple's native frameworks (RoomPlan, ARKit, Object
Capture), Cloudflare (Workers, D1, R2, Vectorize, Durable Objects), Baseten (paid GPU hosting),
Shopify's catalogue, Browserbase, ElevenLabs, OR-Tools, and SigLIP2 embeddings on a server.

## The pieces, against this app

### 1. A room from a scan

- **Apple's model.** RoomPlan's `CapturedRoom` is `Codable`, so it can be written as JSON:
  - `walls`, `doors`, `windows`, `openings` and `floors` are `Surface`s, each with a
    `dimensions` box, a `transform`, a `category`, a `confidence` (high, medium or low),
    `polygonCorners` (non-uniform wall heights and floor shapes), `completedEdges`, a `curve` and a
    `parentIdentifier`;
  - `objects` are `Object`s: `dimensions`, `transform`, `category`, `confidence`, `attributes` and
    `parentIdentifier`;
  - `sections` are labelled areas (dining room, kitchen, living room);
  - `story` is the level;
  - `CapturedStructure` merges several scans (`rooms`) into one result, a whole floor or house.
- **The object categories** (from Scale's exhaustive Swift switch over Apple's enum, S): bathtub,
  bed, chair, dishwasher, fireplace, oven, refrigerator, sink, sofa, stairs, storage, stove,
  table, television, toilet, washer-dryer.
- **How it encodes** (Scale's raw sample): a category is `{"wall": {}}`, and a transform is four
  columns of four. RoomPlan reports a wall's thickness as 0, so Scale assumes 0.1 m. A door's hinge
  side and swing are not detected: Scale writes `unknown` and 90 degrees, and says it is not a
  measurement.
- **True north** needs an ARKit session with `gravityAndHeading` set before RoomPlan starts (iOS
  17, Location Services). Without it, the room has no bearing, and a sun study on it is invented.
- **For the app:** an importer of RoomPlan JSON and of Scale's RoomCapture v1 would build:
  - walls with their heights;
  - doors, windows and openings on their walls (RoomPlan does not link them, so the nearest wall
    is taken, as Scale does);
  - the floor as a room or slab;
  - each object as a box of its category, on a layer, with its confidence;
  - several rooms from `CapturedStructure`.

  The importer would say what was assumed (wall thickness, the door's hinge and swing, the
  bearing).
- **What captures it** is native only. Safari on iPhone has no WebXR, and no browser reaches
  RoomPlan or LiDAR. The scan comes from an app: Scale's own iPhone app (MIT, built with Xcode on
  a Mac, LiDAR iPhone 12 Pro or later, iOS 17), or another app that writes RoomPlan's JSON.
  **Which free apps export it is not yet read (U).**

### 2. An object's size, measured

- Scale's raycast-and-grow, in its Swift code:
  - the object sits alone on a table that ARKit finds as a plane;
  - depth points between 1.5 cm and 1.2 m above that plane, within a radius of the tap, are the
    object;
  - the radius starts at 0.20 m and grows up to three times (the largest half-extent times 1.25,
    at most 1.5 times the last). It stops when the ring between the old and new radius holds under
    3% of the points already inside;
  - a minimum-area rectangle on the floor gives the width, depth and yaw, and the points' height
    range gives the height;
  - the result is a median over frames.
- **In a browser:** WebXR's depth sensing (`XRDepthInformation`) exists in Chrome, so on Android
  and on the Quest browser the same method could run in a page, behind an "experimental" flag in
  MDN's data. Not on an iPhone.
- **Without a sensor:** the size can be typed, read from a listing, or measured on the model.
  Each keeps its provenance (measured, declared, typed or catalogue), and an unverified size is
  said so.

### 3. A mesh bound to the size

Scale's binding (`BINDING.md`):
1. Apply an orientation the caller asserts. It is never guessed: no PCA.
2. Compute `scale = target / extent` per axis.
3. Put the origin at the bottom-centre, with +Y up, -Z the front, and metres.
4. Bake the transform into the vertices, fixing the normals and the winding.
5. Reload the result and check every dimension to 1 mm.

The distortion ratio `r = max(scale) / min(scale)` is labelled:
- up to 1.25: fit for a visual review;
- up to 1.5: needs review;
- over 1.5: a proxy box is recommended until the axes or dimensions are checked.

A non-unit placement scale downstream is a bug.

For the app this is a few dozen lines of ES5. It needs a mesh import first: **the app reads no
glTF or GLB today**. The pipeline lists glTF as a later "Model import" phase.

### 4. A mesh from a photo ("have AI do it for me")

Tested from here on 2026-10-18. Each Space was running, and each answered the app's origin with
`Access-Control-Allow-Origin`, both on its config and on a POST preflight to its upload:

| Space | Model licence | Gradio | Usable here |
|---|---|---|---|
| `microsoft/TRELLIS.2` | MIT (model card: "released under the MIT License") | 6.1.0, `image_to_3d` | **Yes:** the cleanest licence |
| `trellis-community/TRELLIS` | MIT (Space card) | 5.34.2 | Yes |
| `stabilityai/stable-fast-3d` | Stability AI Community License: free for research, and commercial use needs registration and under US$1M a year in revenue; outputs belong to the user | 4.41.0, `run_button` | Only within that licence |
| `tencent/Hunyuan3D-2` | Tencent's licence: "does not apply in the European Union, United Kingdom and South Korea"; the outputs may not be used outside its territory | 4.44.0 | **No:** an app used anywhere cannot meet it |

- **The free quota** (Hugging Face's ZeroGPU documentation): unauthenticated, 2 minutes of GPU a
  day at low queue priority; a free account, 5 minutes. So without a key, one person gets a few
  objects a day, and must sometimes wait.
- A Space can change its API or stop at any time. The app names the Space it uses and lets it be
  changed, and the binding (3) gives the mesh its size.
- Single-image generation is poor on transparent, reflective, thin and very dark objects (Scale's
  own finding). A matte solid object works best.

### 5. A library of real furniture

- **Poly Haven:**
  - **Licence:** every model is CC0, free for any purpose, commercial included, with no credit
    required.
  - **API terms** (ToS.md): free for anyone, commercial use included, no key ever. Calls must carry
    a unique Referer or user-agent naming the software. A visible credit ("Powered by Poly Haven",
    or a label naming it) is required when the live API surfaces the content.
- **Tested from here:** `api.polyhaven.com` and its file host `dl.polyhaven.org` both send
  `Access-Control-Allow-Origin`. A page can therefore list the models, read their dimensions and
  fetch their files directly.
- **What an asset gives:**
  - `/info` gives `dimensions` in millimetres, the third being the height (Green Chair 01:
    673 x 664 x 1059 mm), plus the categories, tags and polycount;
  - `/files` gives glTF at 1k, 2k and 4k: a `.gltf` file with its `.bin` and its textures.
- Scale's 100 library models are all Poly Haven's.
- **For the app:** the furniture library can grow from Poly Haven's models (glTF import first).
  It can be searched by name and filtered by size, the "find what fits" test without a server.
  The credit goes with the content.
- **Shopify's catalogue** (Scale's product search) is not taken. It needs a server for the crawl,
  the dimension extraction and the embeddings, and its storefront JSON's browser access is not
  tested (U).

### 6. The fit checks

Scale's `fit.py`, four checks over the room and the placed boxes:
- **Door swing:** the arc of a door's leaf (its width as the radius, from its hinge, the swing into
  the room) against each piece. The depth of the intrusion is reported, and the arc is drawn in
  red.
- **Clearance:** a corridor straight in through each door, at least 0.9 m wide and 0.9 m deep,
  must stay clear. The intrusion is measured along the wall.
- **Wall gap:** a piece 1.5 to 4 cm off a wall is "floating", a warning.
- **Window occlusion:** a piece taller than the sill within 0.6 m in front of a window, a
  warning.

Each is a few dozen lines, written ourselves for the app, with Scale credited (MIT). The values
are Scale's choices. Its "90 cm sits in the AODA and ADA neighbourhood" is not a citation (U).
They become V167 registry records, with their sources read (the ADA Standards' clear widths, Part
M), when the interiors' ergonomics phase (I2) does its research. **The app's doors carry no hinge
side or swing yet:** the door swing check needs them added (and a plan's door arc follows from
them).

### 7. Arranging the room

Scale discretises the floor and solves with OR-Tools CP-SAT (36 ms for five pieces). OR-Tools has no
browser build the app could inline. A small solver of the app's own would do: a grid, the fit
checks as constraints, and branch and bound over a handful of pieces. It would say "infeasible"
honestly, with the piece to drop. Without a free, keyless language model, the wish is a form (the
pieces, the walkway width, against a wall or not), not a sentence.

### 8. Standing in it at 1:1

- **MDN's data:** WebXR (`XRSystem`, `XRSession`) runs in Chrome from 79 and in Samsung Internet. It
  runs in the Meta Quest browser too, whose entry follows Chrome on Android. Hit testing works from
  Chrome 81, and depth sensing from Chrome 90 (experimental). Safari on Mac and iPhone has none.
- **For the app:**
  - an "Enter VR" session (`immersive-vr`) in the Quest browser, drawn by the app's own WebGL
    engine for both eyes, the model at true scale;
  - on an Android phone, `immersive-ar` with hit testing, to set a piece on the real floor.

  An iPhone would need a USDZ file for AR Quick Look instead, which is not in scope here.
- **WebXR needs a secure page (HTTPS).** The app's GitHub Pages site is one.

## What this suggests for the plan

The pipeline's interiors (I1 to I4, V176 to V179) cover programme, ergonomics, circulation and
light. Scale adds the way in: the room and its objects from a scan or a photo, real furniture, and
the headset. A possible order:

| Step | What | Builds on |
|---|---|---|
| A | glTF and GLB import (the pipeline's "Model import" row): models as Assets, in metres, origin bottom-centre, sizes kept | The Assets library (V124) |
| B | Poly Haven in the library: browse, search, filter by size, insert; the credit with the content | A |
| C | Scan import: RoomPlan JSON, `CapturedStructure` and RoomCapture v1, to walls, doors, windows, floors and object boxes, each assumption said | Walls, doors, rooms, levels |
| D | Measured box and binding: an object's size by scan, by hand or by listing, with its provenance; a mesh bound to it once, the distortion labelled | A |
| E | From a photo: TRELLIS.2's public Space (MIT, no key), the result bound to the measured size (D); the Space named and changeable | A, D |
| F | Fit checks (with I2): door swing (doors gain hinge and swing), the corridor through doors, wall gap, window light, clearances; values from the V167 registry with their sources | V167 |
| G | Arrange: the app's own small solver, honest when a room is too full | F |
| H | 1:1: WebXR on the Quest (immersive-vr) and Android (immersive-ar, hit test) | The WebGL engine |

## The owner's choices (asked together, 2026-10-18)

1. **When:** build this track now, before V167 and V168, or keep it with the interiors after the
   site analysis tools and their presentation.
2. **The iPhone scan:** build Scale's own iPhone app as a companion (it needs a Mac with Xcode),
   rely on other apps' exports, or both.
3. **A mesh from a photo:** use TRELLIS.2's public Space with no key (2 GPU minutes a day each).
4. **The headset:** whether a Meta Quest is to hand, which decides whether step H comes early.

## Still open

- Which free iPhone apps export RoomPlan's JSON, or GLB with true size (U).
- RoomPlan's own JSON from a real device: the encoding of `door(isOpen:)`, `polygonCorners` and
  `confidence` (Scale's sample is hand-made).
- The ADA Standards' and Part M's clear widths, read at the source (with I2 and V167).
- Shopify storefront JSON's browser access (CORS), if product links are ever wanted.
- A USDZ path for iPhone AR Quick Look.
