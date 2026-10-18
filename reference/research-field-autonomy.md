# Field work and autonomy: where a camera is, and 3D work steps on site

The owner (2026-10-18) shared four things "for the phase where field and autonomous work" happens,
to "document and research this for later stage ... understanding their system and integrate into
our app":

- a DeepScenario post: a vehicle localised in satellite imagery from one ordinary camera, with no
  GPS, over off-road farm tracks (the post's video frame is a third-party screenshot and is not
  committed);
- three companies the owner took to be simulation companies: bilt.ai, simlab-soft.com and
  synode.ai.

The first finding changes the framing. **BILT, SimLab and Synode do not simulate traffic, people or
physics on a site.** All three turn CAD into interactive 3D: step-by-step work instructions,
training, and VR or AR viewing. Only SimLab's Composer has a simulation in the physical sense, of
mechanisms. The traffic and pedestrian simulation the app plans (V170) is a different kind and gets
nothing from them. What they do offer is a model of **field work**: a crew on a phone or headset
following steps over the model. That fits the app well, and is set out below.

DeepScenario is the autonomy piece. Its product is closed, but its research behind the post is
published (OrthoLoC, NeurIPS 2025), and that was read in full.

## Sources

All read on 2026-10-18 from this environment. Downloaded files were kept outside the repository and
read as text; no code was run.

| Source | What was read | Level |
|---|---|---|
| DeepScenario's site: home, `/product`, `/defense`, `/automotive`, `/research`, `/about`, `/imprint`, the post "Turning dashcam footage into virtual 3D scenarios" (14.08.2026) | What the company sells, to whom, how the dashcam pipeline works, its research list, its seat | P (for the company's own statements) |
| OrthoLoC: project page (deepscenario.github.io/OrthoLoC), the paper (arXiv 2509.18350, NeurIPS 2025), the code (github.com/deepscenario/OrthoLoC at `6923e9f`, 2026-03-10): `LICENSE`, `README.md`, `ortholoc/utils/pose.py`, `ortholoc/scripts/run_localization.py`, `ortholoc/image_matching/*.yaml` | The method step by step, the dataset, the results, the limits, the licence | P |
| DSC3D: project page and paper (arXiv 2504.17371, IEEE IV 2025) | The dataset, its pipeline, accuracy, contents, where the licence is | P; the licence itself U (behind a login) |
| BILT: `bilt.ai` pages `/`, `/platform/`, `/ai-platform/`, `/frequently-asked-questions/`, its sitemap | What it is, how instructions are made, inputs, devices, pricing | S: bilt.ai refuses scripts (Cloudflare, 403); the pages were read through the fetch tool's digest. The sitemap answered directly |
| Siemens, "Digital Work Instructions (Training and Field enablement)" (siemens.com, BILT as seller, modified 2026-07-08) | How Siemens sells BILT with Teamcenter and NX data; who makes the content | P (for Siemens's statements) |
| SimLab Soft: home, Composer, VR Studio, CADVRter, VR Studio's supported formats | Products, formats in and out, simulation, training, LMS, viewer, pricing | P (for the company's own statements) |
| Synode: `/use-cases`, `/builder-app`, `/visualizer-app`, `/pricing`; the help centre as Markdown (`help.synode.ai`: file formats, system requirements, 3D optimisation, builder overview, user interface, step options, sharing, stages, FAQ) | Products, the step and stage model, formats, model limits, sharing, pricing | P |
| Matcher and localiser licences, read in each repository (`LICENSE`, `README.md`): XFeat, LightGlue, RoMa, LoFTR, DKM, GIM, SuperGlue, image-matching-webui, OrienterNet | What could ever ship in an app that may be sold | P |
| USGS: The National Map's `USGSNAIPImagery` ImageServer and `USGSImageryOnly` tile cache (service JSON, a tile, an `exportImage`, CORS with an `Origin` header); USGS's copyright policy page | Free orthophotos for the US: resolution, date, browser access, terms | P and tested; the policy page through the fetch tool's digest (S), as it refuses scripts (403) |
| ASAM: OpenDRIVE 1.9.0 and OpenSCENARIO XML 1.4.0 (publications.pages.asam.net, both 2026-05-08) | Current editions and their licence clause | P (asam.net itself answered 500) |
| Topografix: GPX 1.1 schema (`gpx.xsd`) | Track, segment and point, with elevation and time | P |
| Khronos: glTF 2.0 specification (`Specification.adoc`, GitHub) | Axes and units | P |
| MDN's browser-compat-data (GitHub): `api/SpeechSynthesis.json` | Spoken steps in the browser | P (for MDN's data) |
| The app's own code and guide | What exists to build on (below, in each section) | P |

## 1. DeepScenario, and finding a camera without GPS

### The company

- DeepScenario GmbH, Stuttgart, founded by Holger Banzhaf, Jacques Kaiser and Nijanthan
  Berinpanathan; its papers are written with TU Munich's computer vision group (Daniel Cremers) and
  MCML.
- It sells a closed "spatial AI" toolbox, as a cloud service, on premises or on the device:
  - the camera's pose from **map matching or visual-inertial odometry**;
  - 3D boxes and tracks of every object from one camera;
  - a mesh of the static scene, an occupancy grid, traffic-light states;
  - video anonymisation, scenario mining and a search of video by text.
- Two markets. **Defence:** autonomy in rough, GPS-denied ground with cameras only, because a
  LiDAR's emissions can be detected; surveillance cameras turned into 3D tracks; mapping from
  off-the-shelf drones. **Automotive:** dashcam footage turned into 3D scenarios, and traffic
  datasets.
- The dashcam pipeline (its post): the pose by visual-inertial odometry (tracked image features
  fused with the inertial sensor), then 3D detection and tracking; the scenarios **exported to
  OpenSCENARIO** for closed-loop testing.
- The post the owner shared names no method. The product page names map matching and
  visual-inertial odometry. The published work closest to it is OrthoLoC, for drones; the ground
  vehicle's method is unpublished (U).

### OrthoLoC: a drone photo placed on an orthophoto and a surface model

The question: given one drone photo and the free government geodata under it, an orthophoto (DOP)
and a digital surface model (DSM), where was the camera, and how was it pointed? The steps, read in
the paper and the code:

1. **Match** the photo against the orthophoto with a learned matcher. Matchers that are not
   rotation-invariant are run at four rotations and the best kept.
2. **Lift** each matched orthophoto pixel to a 3D point: its position from the raster's scale and
   offset, its height from the DSM at the same pixel.
3. **Filter:** drop matches below 0.5 confidence, points with no height, and points outside the
   view.
4. **Solve the camera** with EPnP inside RANSAC, 5-pixel inliers, when the lens is known. When it
   is not (calibration), a second stage refines the focal length with the pose by
   Levenberg-Marquardt.
5. **AdHoP**, their refinement: fit a homography to the first matches (normalised DLT with RANSAC),
   warp the orthophoto toward the photo's view by it, match again, map the new matches back by its
   inverse, and solve again. The result is kept only if its median reprojection error is lower.
   It works because much of what a drone sees is close to planar: roads, roofs, fields.

What they found:

- Best: GIM with DKM, plus AdHoP: **75.4% of photos within 1 m and 1 degree**; translation error
  from 0.40 m to 0.32 m with AdHoP. AdHoP helps every matcher (matching about 30% better, errors
  about 20% lower).
- **The lens is the hard part.** Focal length and distance trade against each other. The best
  calibration found the focal length within 1.6%, but for only 21.8% of photos.
- **Old or different geodata hurts most.** An orthophoto from another source or season tripled the
  translation error; a surface model too took it from 0.16 m to 1.12 m.
- **It needs overlap:** below about 20% of the photo's content in the geodata, accuracy falls away.
  It does not search a large map by itself: the right area must be found first.
- **Resolution matters.** Low-resolution reference imagery, such as satellite imagery, limits the
  accuracy (the conclusion). Section 5.4 gives the highest geodata resolution tested as "13 m/pixel",
  probably 13 cm (to confirm in the supplementary).
- The dataset: 16,425 photos (the README says 16,427), 47 locations in 19 regions of Germany and
  the US, 23 to 154 m up, tilted 0 to 86.8 degrees; its orthophotos and surface models at 5 cm from
  their own reconstructions, georeferenced by RTK or control points, plus the German states' open
  geodata (CC BY 4.0) to test the change of source.
- **Licence: code and dataset CC BY-NC-SA 4.0, non-commercial.** Neither can go into an app that may
  be sold (the owner ruled out Transitous for the same reason). The method can be followed and
  credited.

### DSC3D, their traffic dataset (for V170)

- 177,151 tracks of 14 kinds of road user, about 15 hours, five places: a car park (Sindelfingen),
  a crowded downtown (Munich), a T-junction without signals (Stuttgart), a steep junction without
  signals (San Francisco), and a federal road at 50 km/h (Berlin). Pedestrians are 140,227 of them.
- Filmed by DJI drones at 25 frames a second. The scene is reconstructed and georeferenced; each
  frame is placed on it by matching (LoFTR, LightGlue) and a camera solve. Median position error
  4.8 cm against hand-annotated boxes; road maps in OpenDRIVE. Each track gives position, speed,
  acceleration and heading, frame by frame.
- Free to research institutions; the licence is behind the web app's login (U). Unless DeepScenario
  allows commercial use, it can only be a reference the app's own figures are compared against.

### What can ship: matchers and maps

| Code | Licence (read in the repository) | For the app |
|---|---|---|
| OrthoLoC | CC BY-NC-SA 4.0 | Method only |
| OrienterNet (Meta; a ground photo placed on OpenStreetMap) | Code and weights CC BY-NC | Method only |
| SuperGlue (Magic Leap), and SuperPoint's weights | Academic, non-commercial | No |
| LightGlue | Code and weights Apache-2.0, DISK too; SuperPoint's weights and inference file under Magic Leap's restrictive licence; ALIKED BSD-3-Clause | Possible, without SuperPoint |
| XFeat | Apache-2.0; real time on a laptop CPU at VGA | The likeliest, if any |
| LoFTR | Apache-2.0 | Possible |
| RoMa | MIT | Possible, heavy |
| DKM | MIT for the MegaDepth-trained weights only; the synthetic-trained weights non-commercial | Only those weights |
| GIM | MIT; weights trained on YouTube walking videos | Provenance to weigh |
| image-matching-webui (OrthoLoC's matcher front end) | Apache-2.0; each model keeps its own licence | Reference |

Every learned matcher needs a neural runtime and weights of several megabytes, which the one-file,
no-dependency contract does not allow unless they are fetched on request like a data source. That
is the owner's call (question 3).

**Orthophotos, free and keyless, tested from here:**

- **USGS NAIP ImageServer** (`imagery.nationalmap.gov/.../USGSNAIPImagery/ImageServer`): browser
  access open (`Access-Control-Allow-Origin: *`), no key, any box by `exportImage` (a 512 px JPEG over
  central Philadelphia returned). Mostly 0.6 m, natural colour; "USGS, USDA, The National Map:
  Orthoimagery. January 09, 2025". USGS-made data is public domain by USGS's policy; NAIP is flown
  for the USDA, so its own public-domain statement is still to read (S).
- **USGS Imagery Only** tile cache: open too, but only to zoom 16 (about 1.8 m a pixel in
  Philadelphia): too coarse for this.
- **Esri World Imagery**, the app's satellite basemap: its terms favour non-commercial use
  (`research-open-data.md`), so not a base for a feature that is sold.
- NAIP's 0.6 m is about twelve times coarser than OrthoLoC's 5 cm, so an automatic match against it
  will be coarser than the paper's results; that is to be said on the result.

**Heights:** OrthoLoC lifts with a surface model (roofs and trees). The app fetches bare ground
(AWS Terrain Tiles, V165). The context buildings (V157, V139) can be added to it to approximate a
surface model, said as an approximation; a measured surface comes with LiDAR (LOD-C, V187).

### What this means for the app

- **Guided first, as the LOD track did.** "Place a photo": the person clicks matching points, on the
  photo and on the map or the model (six or more with the lens unknown; four with it known, or on
  flat ground; counts to confirm in the papers below). The app lifts the map points with the
  terrain or the model, solves the camera (a direct linear transform, then refined; with the lens
  from EXIF when the photo has it), lists each point's reprojection error, and shows the camera on
  the map and in 3D with the photo laid over the view. The geometry is classical (DLT, EPnP,
  RANSAC); their papers are to be read before code. It is the same solve as Track D's registration
  by control points (D5).
- **Under a bridge** the deck blocks the sky, and Skydio's 3D Scan flies there without GPS
  (`research-bridge-splatting.md`), so a photo's EXIF position there is not to be trusted (U: how
  far off, unmeasured). Track D's photogrammetry (D2, D3) already solves every photo's camera from
  the images themselves, which is visual localisation; the app reads those poses back. D1's coverage
  check should say which EXIF positions it doubts.
- **Automatic matches, later and optional:** an XFeat-class matcher proposes the points for "Place
  a photo" against NAIP, and the person confirms them.
- **A track and its video:** the post's view, a track on the map beside its video, is ordinary
  web work: a GPX 1.1 track (`trk`, `trkseg`, `trkpt` with `ele` and `time`) or a CSV, played on
  the map in step with a video file, with speed and heading. It serves a drone's flight (Track D) and
  a vehicle's real speeds as a check on V170.
- **Robots on site** (autonomous rovers, layout robots) need the map and the model the app already
  makes; driving them is outside the app.

## 2. BILT (bilt.ai, formerly biltapp.com)

- **What:** "Intelligent Instructions", interactive 3D step-by-step guides with voice, text and
  animation, for assembly, installation, maintenance, repair and training. The person goes at their
  own pace, turns and zooms the model, and sees parts named, called out or made see-through.
- **Who makes them:** BILT's own instruction and CAD designers, from the brand's CAD (Parasolid
  `.x_t` preferred, STEP accepted), a product sample and its manuals; a few days, or one to three
  weeks for complex sets. AI speeds up their authoring, and each step is still checked by a person.
  The brand approves and pays a set-up fee plus yearly hosting. It is a service, not a tool to buy.
- **Delivery:** the BILT app on iOS and Android, free to users, with no sign-in for public
  instructions; a QR code on the box; web embedding, an SDK and an API; AR and VR headsets. The FAQ
  says a touchscreen is needed and a Microsoft version is coming; the platform page lists Windows
  and Apple Vision Pro. The two pages disagree (U).
- **Analytics:** downloads, ratings and the average time on each step.
- **Siemens** sells it as digital work instructions for field users, made from Teamcenter or NX
  data. Its government users include the US Air Force and Navy.
- **For the app:** nothing to integrate; the format is closed and STEP or Parasolid export is out
  of the app's reach. The ideas to keep: short steps with the parts moving, voice, the person's own
  pace, and the time on each step as the measure of a hard step.

## 3. SimLab Soft

- **Composer** (Windows and macOS, desktop): imports over 30 formats, among them IFC, glTF and GLB,
  SketchUp, Rhino, DWG and DXF, STEP, and point clouds (LAS, LAZ, E57). It renders, animates by
  keyframes, and publishes 3D PDF, WebGL pages and VR packages. Everything runs locally and
  offline; nothing is uploaded. By the year: Free (watermarked), Pro $119 (rendering, export, 3D
  PDF, animation), Mechanical $599 (the physics-driven **mechanical simulation** of assemblies, and
  VR training with physics, quizzes and LMS links), Ultimate $1,199 (visual scripting, Python
  automation, the command line, multi-user rooms, CADVRter).
- **VR Studio:** code-free VR training. Its authoring model is **events and responses**, built
  visually, with quizzes. Results go to a learning management system by **xAPI and SCORM**. Rooms
  are multi-user. The free SimLab VR Viewer (built on Unreal Engine) runs on Quest, Pico, PC VR,
  desktop and phones. A free licence never expires and leaves a watermark.
- **For architecture:** a client walks the building at 1:1, with measurements and notes pinned to
  the geometry.
- **For the app:** SimLab already reads IFC and glTF, so a glTF export from the app (and later full
  IFC, Hub H3) is the whole integration. The ideas to keep: events and responses as the way to author
  steps without code, and xAPI for training records.

## 4. Synode

- **Visualizer:** a web viewer with hotspots, callouts and exploded views. Its unit is the
  **stage**: a saved camera and saved object positions, with hotspots leading from one stage to the
  next.
- **Builder:** a timeline of **steps**, each with keyframes, a saved camera, parts highlighted by
  colour or overlay, and text read aloud by text-to-speech. The product page promises automatic
  translation; the help centre says eight languages, each typed in by hand for now.
  Steps can list tools, parts, safety notes and prerequisites, ask questions, and take checkpoints.
  Analytics count completions and where people stop.
- **Sharing:** a link, a QR code or embed code; it runs in any browser, and the limit is the model's
  size, not the device. AR is an add-on.
- **Formats:** GLB (recommended) and FBX; JPEG, PNG and SVG images. Their guidance: under 2 million
  polygons, textures up to 1024 px, meshes named, pivots centred, transforms applied.
- **Pricing:** a free Starter plan (fair use to 10,000 views a month), Pro, and Enterprise on quote.
- **For the app:** a GLB export with meshes named by element and layer opens in Synode as it is.

## 5. What the three share, against the app

| | BILT | SimLab | Synode | The app today |
|---|---|---|---|---|
| Steps in order, each with a saved view | Yes | Sequences | Steps, stages | Named views (`SAVEVIEW`), Presentation's pages; no steps |
| Parts moving, exploded | Yes | Keyframes | Keyframes, exploded views | None: a move is an edit |
| Highlight, ghost, hide | Yes | Yes | Colour, overlay | Selection; layers' visibility and see-through |
| Text and voice on a step | Voice | Text | Text-to-speech | None. The browser's own speech (`SpeechSynthesis`) is in Chrome 33, Edge 14, Firefox 49, Safari 7 and their phone versions (MDN) |
| Checks, quizzes, records | Analytics | Quizzes, xAPI, SCORM | Questions, analytics | None |
| Phone, tablet, offline | App (offline not settled) | Viewer app | Browser | One file; runs offline once opened |
| VR or AR | Yes | Yes | Add-on | None (WebXR researched in `research-scale.md`, section 8) |
| Made from | CAD, by their team | 30+ formats | GLB, FBX | Its own elements, each with a stable ID (V146) |

The app's advantage is the last row. Their steps point at meshes, so a changed design means a new
export and the steps redone. The app's steps can point at **elements by ID**, so they follow the
model as it changes, as V174's live elements follow their source (the owner's rule that data stays
connected).

**The standards in this area:**

- **glTF 2.0** (Khronos) is the way into all three and into headsets: right-handed, +Y up, metres.
- **ASAM OpenDRIVE 1.9.0** (roads) and **OpenSCENARIO XML 1.4.0** (what moves on them), both
  2026-05-08, free to use under ASAM's clause. They are how DeepScenario hands its scenarios to
  simulators, and how V166's streets and a V170 run could reach CARLA and the like.
- **GPX 1.1** for tracks.
- **xAPI** for training records, only if the owner wants them.

## 6. What this suggests for the plan

A track of its own, **Track E, field work and autonomy**, parked beside Track D. These are the
candidates; their order is the owner's.

| Step | What | Builds on |
|---|---|---|
| E1 | **glTF and GLB export:** the model as meshes named by element ID and layer, in metres, +Y up, colours as materials; opens in Synode, SimLab, Blender and WebXR viewers | V152's chunks; the pipeline's glTF import row |
| E2 | **Steps:** a sequence over the model, each step a saved view, the elements shown, ghosted or highlighted, some moved or exploded with a short animation, a text read aloud by the browser, the tools, parts and safety lines, and a check; on phone, tablet and computer, offline; saved with the project, pointing at element IDs. Uses: a construction sequence, an installation or maintenance procedure, an inspection procedure (Track D) | `SAVEVIEW`, Presentation (V162, V173), History (V146) |
| E3 | **The field record:** each check done on site saved with its time, who and a photo; a report; xAPI later if wanted | E2 |
| E4 | **Place a photo:** the guided camera solve above, the camera on the map and in 3D, the photo over the view, each point's error | Terrain (V165), the basemap, Track D1 and D5 |
| E5 | **A track and its video:** GPX or CSV tracks, and Track D's flights, played on the map beside a video in step; speed and heading; a vehicle's real speeds as a check on V170 | The map; V170 |
| E6 | **Automatic matches (optional):** an XFeat-class matcher proposing E4's points against NAIP, confirmed by the person | E4; question 3 |
| E7 | **1:1 on site:** E2's steps in WebXR, Quest and Android (`research-scale.md`, step H) | E1, E2 |
| E8 | **Simulation out:** V166's streets as OpenDRIVE and a V170 run as OpenSCENARIO, so the site reaches CARLA and similar simulators | V166, V170 |

## 7. The owner's choices (asked together, 2026-10-18)

1. **When:** Track E parked after Track D, or E1 (glTF export, small) pulled forward now, since it
   opens the model in Synode, SimLab and headsets at once.
2. **The first use of steps (E2):** a construction sequence, an installation or maintenance
   procedure, or the bridge inspection procedure of Track D.
3. **Automatic matching (E6):** none, guided only; a matcher in the browser, its weights fetched on
   request (several megabytes, outside the one-file rule); or a free online service, which sends the
   photo out and so is not for project photos.
4. **Field records (E3):** kept in the project only, or also sent as xAPI to a learning system.
5. **DSC3D:** ask DeepScenario whether its licence allows commercial use for checking V170, or leave
   it.

## Still open

- DSC3D's licence (behind a login) (U).
- How DeepScenario localised the vehicle in the post (unpublished) (U).
- BILT's pages were read only through the fetch tool's digest (S); whether BILT works offline and on
  Windows, as its pages disagree (U).
- OrthoLoC's "13 m/pixel" in section 5.4, likely 13 cm: the supplementary material, to confirm.
- NAIP's own public-domain statement from the USDA (S through USGS's policy).
- Before E4: the DLT (Hartley and Zisserman), EPnP (Lepetit, Moreno-Noguer and Fua, 2009) and RANSAC
  (Fischler and Bolles, 1981), read at the source.
- Before E1: the rest of the glTF 2.0 specification (buffers, accessors, materials, node names).
- Before E8: OpenDRIVE's road geometry and georeferencing (section 8.5), and OpenSCENARIO's entities
  and trajectories.
- Before E3, if chosen: the xAPI specification (ADL, GitHub).
