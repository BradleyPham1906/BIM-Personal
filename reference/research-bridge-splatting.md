# Research: drone Gaussian splatting for bridges, CAD to BIM (PennDOT, NYSDOT)

The owner: a project with drones for PennDOT and the New York State DOT, using Gaussian splatting to
model bridges, "especially very high detail NSTM bridges". These bridges have CAD drawings, not BIM
models. Wanted: the most efficient way, and the most advanced companies, above all in Europe. The
owner had heard of Zurich and German groups doing this for buildings with Google Earth data.

Researched 2026-10-03. Several academic sites are blocked from the build environment; where so,
the facts come from search engines' summaries and the projects' pages. Company claims are the
companies' own unless said otherwise.

---

## 1. What NSTM inspection requires, and where drones fit

- **NSTM** (nonredundant steel tension member, formerly "fracture critical"): a steel member in
  tension whose fracture could collapse the bridge.
- **The rules.** The 2022 National Bridge Inspection Standards, 23 CFR 650.315(f)(2), and FHWA's
  NSTM memorandum require a **hands-on** inspection: within arm's length of the member, visual,
  supplemented by non-destructive evaluation. The aim is to find fatigue cracks early.
- **FHWA's position on drones (UAS):**
  - They may **supplement** an inspection where they meet a task's requirements.
  - They cut access-equipment time and work next to traffic.
  - They cannot do tactile work: sounding, hammering, feeling.
- **What follows:** for NSTMs, a drone capture and a Gaussian splat **document, prepare and
  target** the hands-on inspection, and track change between inspections. They do not replace it.
- **Two exceptions narrow the gap:**
  - **Contact drones.** Voliro, below, takes ultrasonic thickness and EMAT readings on steel.
  - **Close-range imagery.** Research measured the camera distance at which steel fatigue cracks
    can be seen: about **0.30 m in poor light and up to 1.10 m in good light**. NSTM details need
    close passes, not survey altitude.
- **DOT experience:**
  - PennDOT has run a UAS program since 2018: inspection, construction monitoring, and 3D models
    (for example the Kenmawr Bridge replacement).
  - The NY State Thruway Authority field-tested UAS inspection on a Buffalo bridge and Albany-area
    truss bridges in 2024. It projected annual costs falling from $12.07 M to $1.8 M on the
    Thruway, and from $66.4 M to $34.3 M statewide.

## 2. What Gaussian splatting is good for here, and what it is not

- **What it is:** a photoreal, real-time 3D capture from photos (or photos and LiDAR). It shows
  thin steel, bracing, cables and glass far better than a photogrammetric mesh. Pix4D and DJI
  both make this point for steel structures.
- **It is not survey-grade.** One independent comparison against LiDAR found a mean error of
  about **7.8 cm** (standard deviation 11.5 cm). Photogrammetry with ground control reaches 1 to
  3 cm; terrestrial LiDAR reaches millimetres.
  - **The practice in industry:** "LiDAR (or controlled photogrammetry) for the measurements,
    splats for the visuals".
  - XGRIDS, DJI Terra (with Zenmuse L3) and Leica do this, anchoring splats to LiDAR.
- **For geometry from splats:** 2D Gaussian splatting (2DGS) and TSDF fusion extract surfaces.
  Prior-guided splatting (GS4Buildings, TU Munich) starts from a known model to keep the surfaces
  true.
- **Open standard for delivery:** glTF `KHR_gaussian_splatting` and
  `KHR_gaussian_splatting_compression_spz`, in 3D Tiles with hierarchical level of detail.
  - Cesium, Bentley, Esri, Niantic, Khronos and OGC made it.
  - CesiumJS, Cesium for Unreal and Cesium ion stream it.
  - DOTs on Bentley (OpenBridge, iTwin) can take splats that way.

## 3. The most efficient way for these bridges

The bridges already have CAD drawings, and that is the shortcut. Rather than reconstructing a
bridge from points alone (slow, and still research), **build the BIM from the drawings, then fit
it to the capture**.

1. **Control first.** Survey ground control and check points on and around the bridge (bearings,
   deck joints, targets). Every later product is checked against them: this app's V138 survey
   check is exactly this step.
2. **Capture in three passes:**
   - **The exterior and deck:** an autonomous scan (Skydio X10 with 3D Scan, which navigates
     under bridges without GPS; or DJI M400 or M4E, with the Zenmuse L3 LiDAR for absolute
     accuracy).
   - **Between girders and inside box girders:** Flyability's Elios 3, collision-tolerant, with
     LiDAR. Flyability reports at least 25% less time inside box girders, and no scaffolding.
   - **Close range at every NSTM detail:** welds, cover-plate ends, pin-and-hanger, gussets.
     About 0.3 to 1 m away, for crack-level imagery.
3. **Process:**
   - **Photogrammetry** (Pix4D, RealityCapture, Metashape or DJI Terra), tied to the control,
     gives the **measured** point cloud and mesh.
   - **The same images give the Gaussian splat** for viewing. Pix4D and DJI Terra are
     georeferenced; Bentley iTwin Capture goes straight to 3D Tiles.
4. **The BIM from the CAD:**
   - **Model** each member parametrically from the drawings: girders, cross-frames, stiffeners,
     bearings, deck, as IFC 4.3 (IfcBridge).
   - **Register** that model to the measured point cloud.
   - **Check every member** against the cloud for deviation. Where the as-built differs from the
     drawing, the scan wins and the model is updated.
   - **Research:** BridgeTwin and TwinGen (point cloud to IFC bridge, semi-automated),
     IFC4x3-compliant generation from point clouds, and Scan-to-BrIM for steel.
5. **The inspection layer:**
   - **Crack detection runs on the original close-range photos,** not on splat renders, because
     splats blur fine detail. Deep-learning segmentation of fatigue cracks in steel-bridge images
     is an active area, and newer work reports probability of detection.
   - **Findings are tied to the IFC member** they are on.
   - **The NSTM hands-on inspection still happens,** targeted by this.
6. **Deliver:**
   - IFC 4.3 for the bridge model, with each element's ID;
   - the splat as 3D Tiles (`KHR_gaussian_splatting`), for the photoreal view;
   - a verification report: check-point RMSE, and member deviation from the drawings.

## 4. Companies, by what each does best

No source ranks these, so this is a shortlist by capability, not a ranking.

**Europe:**

| Company | Where | What is most advanced about it |
|---|---|---|
| **Voliro** | Zurich (ETH Zurich spin-off) | **Contact** inspection by drone: ultrasonic thickness (4 to 150 mm) and EMAT on steel, pressing with up to 30 N. The nearest a drone gets to NSTM's arm's-length rule. |
| **Flyability** | Lausanne, Switzerland | Elios 3: collision-tolerant drone with LiDAR for **inside box girders and between beams**. |
| **Pix4D** | Lausanne, Switzerland | **Georeferenced Gaussian splatting** for drone data in PIX4Dcloud (Intergeo 2025), and stable in PIX4Dmatic. |
| **Twinsity** | Germany | Bridge **digital twins with AI damage detection**. A Die Autobahn pilot (with DB mindbox) processed 5,400 drone images and 34 laser scans into a model in 48 hours, at 88.6% AI defect accuracy. An EIC Accelerator grant; a COWI partnership. |
| **STRUCINSPECT** | Austria (Palfinger, Vienna Consulting Engineers, Angst Group) | Multi-sensor drone and AI **structural inspection** with a 3D twin, and service-life prediction. |
| **Implenia, ZHAW, STRUCINSPECT, RPTU** | Switzerland and Germany | The HumanTech pilot on a bridge at Kleinandelfingen: drones, AI and 3D models as a best practice. |

**Research groups the owner may mean:**
- **TU Munich, Photogrammetry and Remote Sensing** (Olaf Wysocki, Boris Jutzi):
  - GS4Buildings (splats guided by LOD2 models);
  - GS4City (LOD3 models give splats their semantics);
  - CM2LoD3.
  - **Buildings, not bridges.**
- **ETH Zurich:** the Autonomous Systems Lab (Voliro came from it), and photogrammetry and remote
  sensing.
- **Splatting from Google Earth** comes in the sources found from the **University of Waterloo**
  (Canada), not Zurich or Germany:
  - *Gaussian Building Mesh* extracts a building's mesh from Google Earth Studio images;
  - *Enhanced 3D Urban Scene Reconstruction ... using Gaussian Splatting and Google Earth
    Imagery*, IEEE TGRS 2025.

**Outside Europe, but what the DOTs mostly use:**
- **Skydio** (US): autonomous 3D Scan under bridges; Texas DOT on the Pecos River High Bridge.
- **DJI** (Terra 5 with splats and L3 LiDAR fusion).
- **Bentley and Cesium:** iTwin Capture splats, 3D Tiles, and the open splat standard.

## 5. Google Earth data: not for this project

Google's terms forbid it.
- **Google Earth and Earth Studio:** their output may not be used to **reconstruct 3D models**.
  Research use of the imagery is allowed with attribution, but the reconstruction ban is not
  lifted for research, and there is no commercial use.
- **Map Tiles API (Photorealistic 3D Tiles):** no non-visualisation use. That rules out
  reconstruction, image analysis and object detection.
- **For a DOT deliverable:** the bridges must be built from the project's own drone (and LiDAR)
  capture. That is also far more detailed: Google Earth's meshes are metres coarse, useless at
  NSTM detail.

## 6. Where this app could help

This app is a browser BIM tool, not a photogrammetry engine. The heavy processing belongs in Pix4D,
DJI Terra, RealityCapture or iTwin Capture. What the app can do, in line with its LOD track:
- **Check:** control and check points against the capture (V138), and member deviation from the
  CAD.
- **Show:** a site-aligned splat (the LOD-G phase) beside the BIM.
- **Hold:** an IFC 4.3 bridge model, its members tied to inspection findings.

A bridge-specific track (IfcBridge members from drawings, member-deviation checks, splat and point
cloud side by side) would be its own set of phases, after the owner's priorities are set.

## 7. The owner's project: Skydio photos into the app

The owner's PennDOT/NYSDOT project flies **Skydio** (Blue UAS, cleared for DoD use). The aircraft
returns a set of overlapping photos. The owner runs photogrammetry on them to build the digital
model. Their CAD drawings are the only existing model of each bridge.

### What the Skydio photos carry

- **Skydio 3D Scan** flies the structure on its own and captures overlapping photos, with metadata.
  Onboard Modeling builds a quick 2D or 3D preview on site, so gaps are seen before leaving.
- **Exports:** every 3D Scan photo can be exported with its full metadata to any photogrammetry
  program. Skydio names Pix4D, Bentley iTwin Capture, DroneDeploy, Esri Site Scan, gNext and
  RealityCapture. A `Pix4D_geolocation.csv` comes with the photos.
- **Metadata:**
  - EXIF holds the GPS position, camera, time and focal length.
  - XMP holds the camera intrinsics and orientation.
  - X10 RTK/PPK photos record the gimbal as Omega, Phi and Kappa. Some firmware records yaw, pitch
    and roll instead.

  The exact tag names come from Skydio's support pages (support.skydio.com), which this research
  could not open. Read them off a real photo before writing the parser.
- **Is this a first?** Drone bridge inspection is not new in the US. Skydio says 43 of 50 state DOTs
  fly its drones, and AASHTO issued a UAS bridge inspection guide in early 2026. A splat and
  photogrammetry twin of an NSTM bridge, tied to a BIM model built from the CAD, does look new.
  No published DOT programme doing that turned up. Florida DOT research in 2026 used splats only
  to help a drone navigate under the deck, not as the deliverable.

### What runs where

Photogrammetry cannot run in the browser. A bridge scan is hundreds to thousands of
high-resolution photos, and structure from motion, dense matching and splat training take hours on
a GPU. That work stays in a desktop or cloud program:

- **Paid:** what the project already licenses, such as Pix4D, iTwin Capture or RealityCapture.
- **Free:**
  - **WebODM / OpenDroneMap** (AGPL-3), run as its own program. Its SfM gives the camera
    positions.
  - **OpenSplat** (AGPL-3) reads ODM's or COLMAP's camera positions and trains the splat.
  - **COLMAP** (BSD-3) and **gsplat** (Apache-2.0) are alternatives.

  These run as separate programs, so the AGPL does not reach this app.

Everything before and after that step fits the app. It all runs offline, on local files: the
photos are opened in the browser and never uploaded. That matters for DoD-cleared capture of
critical infrastructure.

### Possible phases (Track D), smallest and most useful first

| # | Phase | What it does |
|---|---|---|
| D1 | Flight read-in and coverage check | Open a folder of Skydio photos (or the geolocation CSV). An ES5 JPEG reader takes the EXIF GPS and the XMP orientation. Each photo appears as a camera on the map and in 3D. The app reports photo count, GSD (millimetres per pixel at the distance to the bridge, from the CAD or the terrain), overlap between neighbours, and parts of the bridge no photo sees well (under the deck, bearings, the backs of connections). Run it on site, before demobilising. |
| D2 | Hand-off to processing | Write the image list, ground control and check points (V138's control), and the coordinate system in the forms ODM/COLMAP and Pix4D read. Return the processed result to the same site position. |
| D3 | Bring the capture back | Point cloud (LAS, LAZ, PLY; shared with LOD-C), textured mesh (OBJ, glTF), splat (`.ply`, `.splat`; shared with LOD-G) and the solved camera positions (COLMAP `images.txt`, ODM `shots.geojson`). All placed in site coordinates. |
| D4 | Bridge model from the CAD | DXF plans and sections become IFC 4.3 `IfcBridge` members: girders, floor beams, stringers, cross frames, bearings, deck. Each member carries its NSTM flag and member ID. Builds on V125/V126 framing and profiles and V127 alignment. |
| D5 | Register and compare | Fit the capture to the model, first by control points, then by ICP. Show each member's deviation from the CAD as a V136 colour-by. Report check-point RMSE in V138's form. |
| D6 | Photo-linked findings | Click a point on a member to list every raw photo that saw it (from the solved camera positions). The full-resolution photo opens with the point marked. Record a finding (crack, section loss, corrosion, condition state) on that member, linked to those photos. Export an inspection-ready report. This is the most valuable step: the inspector judges from the original pixels, not the splat. |
| later | Defect detection | Suggest cracks on the raw photos with a model run on request. Always reviewed by the inspector. |

### Data handling

The repository and its GitHub Pages site are public. Project photos, models and drawings must
never be committed. Like V138's survey files, they stay on the owner's machine. Only synthetic
fixtures go in `tests/data/`.

## Sources

- FHWA NSTM memorandum: https://www.fhwa.dot.gov/bridge/pubs/memo_nstm_inspection.pdf
- 23 CFR 650 Subpart C (NBIS): https://www.ecfr.gov/current/title-23/chapter-I/subchapter-G/part-650/subpart-C ; Federal Register 2022: https://www.federalregister.gov/documents/2022/05/06/2022-09512/national-bridge-inspection-standards
- NBIS Q&A: https://www.fhwa.dot.gov/bridge/nbis2022/qanda/08.cfm
- PennDOT UAS: https://www.pa.gov/agencies/penndot/about-penndot/advisory-committees-boards-and-commissions/state-transportation-innovation-council/innovations/unmanned-aerial-systems ; https://thedronelifenj.com/penndot-drone-program/
- NYSTA UAS (ITS JPO): https://www.itskrs.its.dot.gov/2026-b02062 ; https://www.thruway.ny.gov/news/pressrel/2021/10/2021-10-04-drone-pilot-program.html
- Drone-based bridge inspections review: https://www.sciencedirect.com/science/article/pii/S0926580525001414
- Splat accuracy and practice: https://www.thefuture3d.com/blog/gaussian-splatting-accuracy-guide/ ; https://aecmag.com/technology/introducing-gaussian-splats-for-aec/ ; 2DGS: https://arxiv.org/pdf/2403.17888
- Cesium splats in 3D Tiles: https://cesium.com/blog/2026/04/27/3d-gaussian-splats-lod/ ; Bentley: https://www.bentley.com/en/blog/why-gaussian-splats-could-change-infrastructure/
- Pix4D georeferenced splats: https://www.pix4d.com/blog/pix4dcloud-georeferenced-gaussian-splatting-drones
- DJI Terra splats: https://terra.dji.com/user-manual/en/lidar/gaussian-splatting.html
- Skydio: https://www.skydio.com/solutions/bridge-inspection ; X10 https://www.skydio.com/x10 ; 3D Scan https://www.skydio.com/blog/introducing-skydio-3d-scan ; support (blocked here, from search summaries): https://support.skydio.com/hc/en-us/articles/20866347470491-Skydio-X10-camera-and-metadata-overview , https://support.skydio.com/hc/en-us/articles/32887502774171-Skydio-X10-RTK-PPK-metadata-overview , https://support.skydio.com/hc/en-us/articles/4402426074907-How-to-access-3D-Scan-data
- AASHTO UAS bridge inspection guide (2026): https://aashtojournal.transportation.org/bridge-inspection-guide-for-unmanned-aircraft-systems/
- FDOT splat navigation under decks (2026): https://www.researchgate.net/publication/408113408
- OpenSplat (AGPL-3): https://github.com/WebODM/OpenSplat ; gsplat (Apache-2.0): https://arxiv.org/pdf/2409.06765
- Flyability: https://www.flyability.com/casestudies/bridge-drone-inspection
- Voliro: https://voliro.com/industry/maintain-top-quality-infrastructure-using-voliro-t-for-aerial-ndt-inspections/
- Twinsity: https://twinsity.com/autobahn-bridge-inspection/ ; https://twinsity.com/cowi-partnership-digital-inspections/
- STRUCINSPECT: https://strucinspect.com/ ; https://www.traffictechnologytoday.com/news/infrastructure/palfinger-creates-joint-venture-to-revolutionize-bridge-inspection.html
- HumanTech, Kleinandelfingen: https://www.commercialuavnews.com/how-drones-are-making-transportation-infrastructure-across-europe-safer
- GS4Buildings (TUM): https://isprs-annals.copernicus.org/articles/X-4-W6-2025/249/2025/ ; https://github.com/zqlin0521/GS4Buildings
- Google Earth and splats (Waterloo): https://arxiv.org/pdf/2501.00625 ; https://arxiv.org/html/2405.11021v2
- Google terms: Map Tiles API policies https://developers.google.com/maps/documentation/tile/policies ; Google Maps Platform terms https://cloud.google.com/maps-platform/terms ; Google geo guidelines https://about.google/brand-resource-center/products-and-services/geo-guidelines/
- Bridge scan-to-BIM: https://www.frontiersin.org/journals/built-environment/articles/10.3389/fbuil.2024.1375873/full ; https://www.researchgate.net/publication/381695369 ; https://doi.org/10.3390/buildings16091838
- Steel-bridge crack detection: https://arxiv.org/abs/2403.17725 ; https://arxiv.org/pdf/2608.17726
