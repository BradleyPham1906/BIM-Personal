# Research: building reconstruction from LOD1 to LOD2 to LOD3

The owner: "a progression from LOD1 to LOD2, and then ultimately LOD3. And this progression requires a
lot of imagery reconstruction based on the facade ... make sure you do it carefully." They had
discussed LiDAR and Gaussian splatting with ChatGPT; that conversation could not be opened from here
(chatgpt.com is blocked by this environment's proxy), so this note is built from the published
research below.

Researched 2026-10-03. Several primary sources (arXiv, TU Delft, ISPRS, 3DBAG docs) are blocked
from the build environment; where so, the facts below come from the search engines' summaries of
those pages and from the projects' GitHub pages, and are marked to re-check when the owner can
open them.

---

## 1. What LOD1, LOD2 and LOD3 mean

**CityGML (OGC).** LOD is the geometric detail of a building's exterior:
- **LOD1:** the footprint extruded to one height. A block with a flat top.
- **LOD2:** adds the roof's real shape, its planes, and can carry roof parts and installations such
  as dormers. The surfaces are typed as roof, wall and ground.
- **LOD3:** adds the facade.
  - Openings: windows and doors, as real holes and objects in the walls.
  - Roof overhangs, balconies and chimneys.
  - A full architectural exterior.
- **CityGML 3.0 drops LOD4** (interiors). LOD3 is the highest building LOD, and interiors are
  modelled at any LOD instead.

**The refined LODs** (Biljecki, Ledoux and Stoter 2016, *An improved LOD specification for 3D
building models*) split each level into four, to make "LOD2" mean one thing. They are used by
the Dutch national model (3DBAG). The ones that matter here:

| LOD | Meaning |
|---|---|
| **1.2** | a fine footprint (small parts and extensions kept), extruded to **one** height |
| **1.3** | the footprint split where the roof height jumps (3DBAG keeps jumps over 3 m), each part extruded to its own height |
| **2.2** | roof planes; dormers and other roof superstructures over about 2 m modelled; walls straight up from the footprint |
| **3.x** | openings and facade detail; 3.0 to 3.3 refine how much |

**Where this app stands:** V133's context buildings are **LOD1.2**. Each OSM footprint is extruded
to its `height`, or its `building:levels` times 3 m, or an assumed 6 m.

## 2. LOD1 to LOD2

There are three routes, from the cheapest up.

### a. From OpenStreetMap's roof tags (no LiDAR)
- OSM's *Simple 3D Buildings* tags describe roofs:
  - `roof:shape`: flat, gabled, hipped, pyramidal, skillion, half-hipped, gambrel, mansard, dome,
    onion, round, saltbox;
  - `roof:height`;
  - `roof:direction` and `roof:orientation`.
- `building:part` splits a building into parts of their own heights, which gives LOD1.3.
- Procedural roof generators (OSM2World, OSM Buildings, the polyhedral method in *Sensors* 2024)
  build each shape from the footprint and these tags.
- **The limit:** most OSM buildings have no `roof:shape`. Where they do, the roof is a typical
  shape, not a measured one. Useful as a first LOD2, and as the fallback.

### b. From airborne LiDAR (the measured LOD2)
- **The state of the art in practice** is TU Delft's 3DBAG pipeline (*Automated 3D reconstruction
  of LoD2 and LoD1 models for all 10 million buildings of the Netherlands*, Peters et al. 2022).
  It is now the **roofer** tool, from 3DGI.
  - **Inputs:** the building's footprint and its LiDAR points.
  - **Planes:** roof planes are found by **region growing** on the points.
  - **Partition:** lines where planes meet, plus the footprint's edges, split the footprint into
    an initial partition. A **graph-cut optimisation** gives each face a roof plane and merges
    neighbours with the same plane.
  - **Extrusion:** each face is extruded up to its plane.
  - **The same partition gives LOD1.3** (height jumps over 3 m) and LOD1.2.
  - **Accuracy reported:** RMSE to the points under 9 cm for 75% of buildings and under 31 cm for
    95%.
- **City3D** (TU Delft, Huang et al. 2022) works from a footprint and points by
  hypothesis-and-selection, as PolyFit does.
- **Both are GPL-3, in C++** with CGAL, Qt and solvers. They cannot be pasted into this single ES5
  file. GPL code would also make the app GPL. Their methods are published, and V140 onward
  implements the method, not their code.

### c. From imagery alone
- Methods exist for LOD2 from satellite or aerial stereo (SAT2LoD2, PLANES4LOD2). They need
  photogrammetric surface models, which are not free or keyless for most sites.

### The free LiDAR available

| Where | Source |
|---|---|
| **US** | **USGS 3DEP**: over 350 TB, mostly QL2 (2 or more points per m²). On AWS as Entwine Point Tiles (`s3://usgs-lidar-public`, public) and as COPC on Microsoft Planetary Computer. Built to be streamed to a browser (Potree and Plasio read it). |
| **Philadelphia** | PASDA: city LiDAR from **2015** (QL2, about 2 points per m², 0.7 m spacing) and **2018**, classified LAS. |
| **Pennsylvania** | QL2 statewide coverage, 2014 to 2020, under 3DEP. |

**Point classes (ASPRS LAS 1.4):**
- 2: ground;
- 3, 4, 5: low, medium and high vegetation;
- 6: building.

**Reading LiDAR in a browser:**
- **laz-perf** decompresses LAZ. It is **Apache-2.0** (relicensed from LGPL at 3.1.0), so it can be
  used with its notice, as a WebAssembly module.
- **copc.js** reads COPC.
- Uncompressed LAS needs neither.

## 3. LOD2 to LOD3: the facade from imagery

LOD3 is where the research is still moving, and where care is needed most.

- **The main recipe** (Texture2LoD3, Tang, Biljecki et al., CVPR Workshops 2025):
  - **Inputs:** an LOD2 model and street-level panoramas.
  - **Rectifying:** each LOD2 wall is a plane, so a panorama, placed by its GPS and heading, is
    **ortho-rectified onto the wall's plane**. That turns a skewed photo into a straight-on facade
    image, in the wall's own metres.
  - **Segmenting:** the rectified facade is segmented into wall, window and door. Because it is
    straight-on, an opening's outline is directly its size and position on the wall.
  - **Result:** rectification improved facade segmentation by **11%** over unrectified images, on
    par with manual texturing.
  - **Benchmark:** ReLoD3 (Google Street View panoramas with LOD3 models).
- **Other lines of work:**
  - Multi-view detection with Faster R-CNN and Segment Anything (SAM), with the openings'
    positions projected into 3D (Salehitangrizi et al. 2024).
  - *Automatic upgrade of 3D building models to LoD3* (ISPRS Archives 2024).
  - CM2LoD3: semantic conflict maps between a LOD2 model and mobile laser scans, for glass and
    occlusions (ISPRS Annals 2025).
  - SVI2LoD3: an LLM agent with a vision model segments openings from volunteered street imagery
    (2026).
  - GT-LOD3: a benchmark (ISPRS Annals 2026).
- **Regularising:** windows sit in rows and columns.
  - Facade parsing aligns detections into a grid and makes each row's windows share a size.
  - It fills gaps where a window was missed (shape grammars, alignment regularisers).
  - This is the single most useful step for turning noisy detections into a clean LOD3 facade.
- **Segmenting in the browser:**
  - SAM and its small versions (SlimSAM at 5.5 M parameters, MobileSAM; SAM2 with WebGPU) run
    client-side through ONNX Runtime Web or Transformers.js. SAM is Apache-2.0.
  - The weights are megabytes to hundreds of megabytes, downloaded on first use. That cuts
    against working offline, so it is optional, asked for, and cached.
- **Gaussian splatting** (the owner's "Goshen plating"):
  - A splat is a photoreal capture of a scene from photos. It is not surfaces, so it is not
    LOD3 by itself.
  - Recent work uses the two together:
    - GS4Buildings: LOD2 models as priors for splatting;
    - GS4City: LOD3 models give the splats their semantic masks;
    - *Generative Gaussian splatting for 3D city models*.
  - The useful part here is a **site-aligned splat as a backdrop**, to trace LOD3 detail
    against, and as the photoreal view.
  - **antimatter15/splat** is a small **MIT** WebGL viewer of the `.splat` format, which can be
    carried over with its notice as GeoLibre's catalogue was in V135.
- **Free street-level imagery:**
  - **Panoramax** is open: CC BY-SA 4.0, a STAC API, no key.
  - Mapillary needs an access token.
  - Google Street View's terms do not allow this use.
  - **The owner's own photos** of the facade need no licence and are the most reliable source.

## 4. Verifying each level (the owner's "verified every time")

Each level gets checks of the same kind as V138's survey check, run on seed datasets in
`tests/data/` and on the owner's own.

- **Valid solids,** as val3dity (TU Delft, GPLv3; its rules are ISO 19107) checks them: closed,
  outward faces, planar faces, no self-intersection. The rules are written down; the code is not
  copied.
- **LOD2 against its points:** RMSE and the 95th percentile from each building's LiDAR points to
  its roof, as 3DBAG reports. Every building gets its number and a pass or warn.
- **LOD1.3 and LOD2 against survey:** the V138 check shots, such as roof ridge or eave heights
  taken with a total station, measured against the model.
- **LOD3 against measurements:** a few measured openings (width, height, sill) checked against the
  reconstructed ones. The window grid's regularity (rows level, columns plumb) is reported.
- **Every source credited,** as V133 to V135 do: OSM, USGS 3DEP, Panoramax, and the owner's
  photos.

## 5. The plan, in phases

Each phase is usable alone, and each is checked before the next. Automatic where the research is
solid (LOD1, LOD2 from LiDAR); guided by the owner where it is not yet (LOD3 openings), with
automation offered on top.

| Phase | Builds | Verified by |
|---|---|---|
| **LOD-A: LOD1.3, labelled LODs, CityJSON** (done, V139) | `building:part` heights (LOD1.3); every building says its LOD and how it was made; CityJSON export and import (CityGML's JSON form) | valid solids; round trip through CityJSON; cjval on the export |
| **LOD-B: LOD2 from OSM roofs** (done, V140) | procedural roofs from `roof:shape`, `roof:height`, `roof:direction` (gabled, hipped, pyramidal, skillion, half-hipped, gambrel, mansard); roof and wall surfaces typed | valid solids; roof heights match the tags |
| **LOD-C: point clouds** | read LAS, LAZ (laz-perf, Apache-2.0) and PLY; fetch USGS 3DEP around the site (EPT or COPC); show by class or height; ground points to a V108 surface through V138's check | the survey check; LiDAR against survey check shots |
| **LOD-D: LOD2.2 from LiDAR** | each building's points: region-growing roof planes, roof partition from plane intersections and the footprint, optimised; extruded; LOD1.3 from the same partition (3DBAG's method, written here) | RMSE and 95th percentile to the points, per building; valid solids; seed buildings of known roofs |
| **LOD-E: facade images** | the owner's photos or Panoramax panoramas placed on an LOD2 wall: the four corners picked (a homography), or the camera's position and heading; the wall shown straight-on, in metres | known rectangles come out square and to size |
| **LOD-F: LOD3 openings** | windows and doors drawn on the rectified facade, then regularised into rows and columns; optional automatic detection (SAM in the browser, downloaded on request); cut into the wall as the app's own openings | measured openings; grid regularity; valid solids |
| **LOD-G: splats** | a `.splat` capture placed on the site as a photoreal backdrop to trace against (MIT viewer) | its placement against surveyed points |

## Sources

- CityGML LODs and CityGML 3.0's: TU Delft GeoBIM benchmark, https://3d.bk.tudelft.nl/projects/geobim-benchmark/citygml.html
- Biljecki, Ledoux, Stoter (2016), An improved LOD specification for 3D building models: https://research.tudelft.nl/en/publications/an-improved-lod-specification-for-3d-building-models/ (and https://3d.bk.tudelft.nl/lod/)
- Peters et al. (2022), Automated 3D reconstruction of LoD2 and LoD1 models for all 10 million buildings of the Netherlands: https://arxiv.org/pdf/2201.01191 ; roofer: https://github.com/3DBAG/roofer
- City3D: https://github.com/tudelft3d/City3D
- OSM Simple 3D Buildings: https://wiki.openstreetmap.org/wiki/Simple_3D_Buildings ; Key:roof:shape: https://wiki.openstreetmap.org/wiki/Key:roof:shape
- USGS 3DEP on AWS: https://github.com/awslabs/open-data-registry/blob/main/datasets/usgs-lidar.yaml ; https://www.usgs.gov/news/usgs-3dep-lidar-point-cloud-now-available-amazon-public-dataset
- Philadelphia LiDAR (PASDA): https://www.pasda.psu.edu/uci/DataSummary.aspx?dataset=1048 (2015), https://www.pasda.psu.edu/uci/DataSummary.aspx?dataset=2021 (2018)
- LAS 1.4 classes: https://paulbourke.net/dataformats/laz/LAS_1_4_r15.pdf ; laz-perf: https://github.com/hobuinc/laz-perf
- Texture2LoD3 (Tang, Biljecki et al. 2025): https://wenzhaotang.github.io/Texture2LoD3/ , https://github.com/WenzhaoTang/Texture2LoD3
- Automatic upgrade of 3D building models to LoD3 (ISPRS Archives 2024): https://isprs-archives.copernicus.org/articles/XLVIII-2-W8-2024/471/2024/
- CM2LoD3 (ISPRS Annals 2025): https://isprs-annals.copernicus.org/articles/X-4-W6-2025/81/2025/ ; GT-LOD3: https://isprs-annals.copernicus.org/articles/XI-2-2026/293/2026/
- SVI2LoD3: https://arxiv.org/html/2608.29992 ; GS4Buildings: https://arxiv.org/pdf/2508.07355 ; GS4City: https://arxiv.org/html/2604.11401v1
- Facade parsing and regularisation: DeepFacade (IJCAI 2017) https://www.ijcai.org/proceedings/2017/0320.pdf ; Mask R-CNN window detection https://arxiv.org/pdf/2107.10006
- SAM in the browser: https://github.com/lucasgelfond/webgpu-sam2 ; Transformers.js SAM: https://huggingface.co/posts/Xenova/240458016943176
- Gaussian splat viewer (MIT): https://github.com/antimatter15/splat
- Panoramax: https://github.com/osmberlin/street-level-imagery-provider-overview
- val3dity: https://val3dity.readthedocs.io/2.5.0/
- LoD2 accuracy metrics: https://www.researchgate.net/publication/359006698 (3DBAG RMSE figures)

## 6. What V139 (LOD-A) settled

- **Parts and outlines.** OSM's Simple 3D Buildings: when a building outline has parts, renderers
  draw the parts, not the outline. The app does the same, and pairs each part with the smallest
  outline that holds a point well inside it. Where parts leave part of an outline uncovered, that
  part of the outline is not drawn (as in the renderers); the tagging, not the app, is then wrong.
- **The solid check** follows val3dity's published rules and error codes (101, 105, 203, 301, 302,
  303, 305, 307, 405), with its 1 cm planarity tolerance and 1 mm vertex snapping. Self-intersection
  (306) and nested shells are not checked yet; val3dity itself (C++, CGAL, GPL-3) is not used.
- **CityJSON 2.0** files are written in the site's UTM zone, checked by cjval (cityjson.org's Rust
  validator, MIT) in the suite, and read back to the millimetre. UTM is Krueger's series to the
  third order, within 0.05 mm of PROJ (pyproj) across a zone.
- **Files in other grids** (the Dutch RD/NAP of 3DBAG, a US state plane) are placed by their
  centre and named; converting them needs the grid's own projection, which a later phase can add
  for the grids the owner uses.

## 7. What V140 (LOD-B) settled

- **No smoothing, anywhere.** A roof is a set of planes. Hipped roofs come from the straight
  skeleton (every face planar by construction, since height is distance to the face's own eave
  times the slope). The other ridged shapes are the lower envelope of planes over a convex
  footprint: each plane keeps the convex region where it is lowest, so every ridge, hip and knee is
  an exact plane-plane line. Each face is checked flat to val3dity's 1 cm.
- **The same principle scales up:** LOD-D's LiDAR roofs are also planes (region growing, then a
  partition chosen by optimisation, 3DBAG's method), not a mesh fitted to the points. Splats and
  photogrammetry meshes stay backdrops to trace against.
- **Heights** follow Simple 3D Buildings: height includes the roof; levels count the walls.
