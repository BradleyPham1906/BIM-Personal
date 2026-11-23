# BIM in XR: prior art, exploded views, and what the gestures would drive (H7, H8)

Corrections from the independent check (2026-11-23) are in `independent-check.md` and applied in the main note,
`../research-xr-interaction.md`; where they differ, those win.

One of three topic notes for `docs/research/research-xr-interaction.md`, written 2026-11-23 by a research agent,
following `docs/research/research-protocol.md`. Levels: P primary (read at the source, or the app's own code), S
secondary (a dependable work citing the source, or a vendor page read only through the fetch tool's digest), U
unverified (a search engine's summary only, or worked out here without a check). Confidence: high, medium, low, with
the reason. No third-party code was run; one MIT bundle and two papers were downloaded into the session's scratch
folder and read as text.

## 1. Questions

- Q1 (H8). Which BIM tasks do the apps already in headsets offer, on which devices, with which input (controllers or
  hands)? Which tasks do people actually do there, and which does research say benefit?
- Q2 (H7). How do CAD and BIM tools make exploded views; what algorithms exist; how is the amount controlled; is there
  building-specific prior art (by storey, by system, by assembly)?
- Q3 (H7). Does this app's model carry a hierarchy to explode by, and can an exploded view be drawn without changing
  the model?
- Q4. Which of the app's existing commands would the gestures drive, and what is missing?

Falsifiable forms: H7 fails if the app has no grouping to explode by, or if no BIM viewer offers an exploded view.
H8 fails if the vendors' documents give no usable task list, or if they disagree so much that no priority follows.

## 2. Search log

| # | Where | Query or address | Came back | Kept or set aside |
|---|---|---|---|---|
| 1 | Web search | Autodesk Workshop XR Meta Quest design review features | Autodesk product pages, press release | Product page refused (403); press release read |
| 2 | Fetch | adsknews.autodesk.com press release, 2023-11-13 | Feature text | Kept (P) |
| 3 | Fetch | workshopxr.autodesk.com/faq | Host not resolvable from here | Recorded as refused; its content known only from a search digest (U) |
| 4 | Web search | Revizto VR Quest issue tracking | Revizto blog, Resolve integration, help article | Revizto blog page held only titles; kept as S |
| 5 | Fetch | resolvebim.com | Feature headings | Kept (P, thin) |
| 6 | Web search | Resolve BIM VR dollhouse measure | Meta store, AEC Magazine, Road to VR | Digest only (U); used for planning |
| 7 | Fetch | arkio.is | Arkio is now a browser app, VR "coming soon" | Kept (P): counter-evidence |
| 8 | Fetch | thewild.com/help/tools-in-vr | The eleven VR tools | Kept (P) |
| 9 | Web search | IrisVR Prospect end of life | Autodesk FAQ digest, The Wild's acquisition post | Retirement in favour of Workshop XR: S (FAQ not reachable) |
| 10 | Fetch | help.sketchup.com Quest pages (tools; moving, rotating and scaling; viewer) | Full tool list, two-controller scale gesture, no hand tracking, end of download 2025-09-16 | Kept (P) |
| 11 | Web search, fetch | Unity Reflect end of life | docs.unity.com pages answer 404 now; search digest says deprecated December 2024 | S at best (U for the date) |
| 12 | Fetch | shapr3d.com blog (Vision Pro, 2024-03-27); support.shapr3d.com | Blog read; support refused (403) | Blog kept (P); gestures from search digest (U) |
| 13 | Fetch | jig.com/apple-vision-pro; App Store listing | "pull apart components" with the hands, SharePlay 4 users, visionOS 26 | Kept (P) |
| 14 | Web search | Enscape VR, Fologram, Bentley SYNCHRO XR, Dalux | Digests; Enscape docs moved to docs.chaos.com | U, planning only; Dalux nothing found |
| 15 | Web search, fetch | arXiv 2306.12274 (Yigitbas et al.) | Abstract | Kept (P) |
| 16 | Download, read as text | Horvat et al., ICED19 (Cambridge open PDF) | Full paper | Kept (P); its literature review gives counter-evidence (S for the works it cites) |
| 17 | Fetch | pure.psu.edu: Liu, Castronovo, Messner, Leicht 2020 | Abstract | Kept (P for the abstract) |
| 18 | Web search | Wolfartsberger 2019; Paes et al. 2017 | Abstracts via digests | S/U |
| 19 | Download, read as text | Li, Agrawala, Curless, Salesin 2008 (grail.cs.washington.edu) | Full paper | Kept (P) |
| 20 | Fetch | help.autodesk.com Revit "About Displacement Sets"; search on Displace Elements | Help page; tutorials | Kept (P for the page; view-only behaviour S) |
| 21 | Fetch | aps.autodesk.com blogs: explode along levels (2024), vertical explode (2018), ExplodeExtension reference | Code and API text | Kept (P) |
| 22 | Fetch | cad.onshape.com help, exploded views; Fusion help, auto explode one level; SolidWorks help search | Help text | Onshape and Fusion P; SolidWorks S (digest of its help pages) |
| 23 | unpkg.com, read as text | `@thatopen/components@2.4.11` `dist/index.mjs` (MIT, from its package.json; the repository's LICENSE.md also MIT) | The `Exploder` class, lines 25420-25503 | Kept (P) |
| 24 | docs.thatopen.com tutorial | 404 | Set aside; the code was read instead |
| 25 | The app | grep over `src/js/engine` and `src/js/shell/shell.js` | Section 5 | P |

Refused or unreachable on 2026-11-23: www.autodesk.com product pages (403), workshopxr.autodesk.com (does not resolve
here), help.thewild.com (proxy could not connect; thewild.com/help answered), docs.unity.com Reflect pages (404, the
docs are gone), support.shapr3d.com (403), docs.thatopen.com tutorial (404).

## 3. Findings

### 3.1 Prior art: BIM and design apps in headsets (H8)

F1. Autodesk Workshop XR (announced 2023-11-13) runs on Meta Quest 2, Pro and 3 standalone; teams "review their 3D
models together at a 1:1 scale" and "walk through models at a one-to-one scale", with "synced issue tracking" with
Autodesk Construction Cloud (press release, P). Measure, toggling categories such as walls and ceilings, Quest 3S, and a
browser version without a headset come only from search digests of the product pages (U). Autodesk's FAQ, by digest,
names it the successor to The Wild and Prospect by IrisVR (S: two digests and The Wild's own acquisition history agree).
Confidence high for the press-release facts, medium for the rest.

F2. The Wild (now being retired in favour of Workshop XR) documents eleven VR tools: Explore (teleport, rotate, pull
yourself), Grab, Group, Comment (speech to text), Measure (three modes), Mass (sketch massing, copy, arrays), Inspect
(an element's BIM data in a panel, "tool-hand trigger"), Paint, Sketch, Tour (a guide leads guests, who are teleported
and locked), Visibility (layers of SketchUp or Revit files) (thewild.com/help/tools-in-vr, P). No section tool is
listed. Input: the trigger wording implies controllers (P for the wording, the inference U). Confidence high.

F3. SketchUp Viewer for Meta Quest (Trimble) has two modes: Tabletop, "as if it were a physical scale model", and
Immersive, "inside your model at a 1:1 scale"; models open in Tabletop by default. Tools: Transform (rotate on the
table, table height), Tape Measure (points, edges, faces; not saved), Jump (eye height, Elevator between floors, jump
up to about 15 m), Scenes and a Presentation Mode, Tags and Outliner for visibility, Entity Info. Scaling is two
controllers: point both rays at the model, hold both grips, "Move your hands apart to zoom in, or close together to
zoom out"; a twisting motion rotates; one grip moves; touching the model with a grip held makes it follow the hand.
"Hand tracking is not supported." The viewer "will no longer be available to download" from 2025-09-16
(help.sketchup.com, three pages, P). No section planes. Confidence high.

F4. Resolve (Quest 2, 3, 3S; web and iPad viewers): "Review & Issue Tracking", "Collaboration", "Immersive model
reviews" (resolvebim.com, P). Its issues can be escalated to Revizto's issue manager (Revizto blog 2025-07-08, title and
digest, S). A "dollhouse" overview with detail loaded where one looks, speech-to-text issues, measuring, sketching and
BIM property inspection come from store and press digests (U). Revizto's own older headset path ran through a PC over
Oculus Link (help article, by digest, U).

F5. Arkio, once a VR-first sketching tool, now "Opens in your browser"; "VR version of Arkio 3.0 is coming soon"; Revit
or Navisworks context; "Live co-design and threaded comments" (arkio.is, P). Counter-evidence to a VR-first product:
the vendor moved its main product to the browser.

F6. Unity Reflect: deprecated, unavailable since December 2024 (search digest of Unity's docs, whose pages now answer
404 here; U, consistent with the 404s). SketchUp's Quest viewer withdrawn 2025-09-16 (F3), The Wild and Prospect
retired (F1). Three of the products a 2022 list would name are gone: the market churns, which argues for a web app
that owns its viewer rather than relying on any one vendor's headset app. Confidence medium (the Reflect date is U).

F7. Apple Vision Pro: Shapr3D runs natively, with "intuitive hand and eye motions" alongside a trackpad and keyboard,
"full capabilities to edit directly in Vision Pro" and real-time multi-user review (blog 2024-03-27, P). Its help
pages (refused here) say, by digest, that both-hand pinch zooms and one-hand pinch and circular motion rotates, and that
without a keyboard and mouse a person has "view access and limited real-time editing" (U). JigSpace on Vision Pro:
"Manipulate Jigs intuitively with your hands; pull apart components, annotate, and explore"; steps advanced by
finger-taps; SharePlay for "up to 4 users"; requires visionOS 26 (jig.com and the App Store listing, P). JigSpace is
the nearest prior art to the owner's "pull a model apart with two hands", but its explosions are authored on a
computer as steps, not computed (help-centre digest, U). Confidence medium.

F8. Mixed reality on site: Trimble Connect for HoloLens measures models "in the real world" (Trimble's lesson, by
digest, U); Bentley SYNCHRO XR for HoloLens 2 (2019) reviews 4D construction sequences with gestures (press, U);
Fologram streams Rhino and Grasshopper to HoloLens 2 (hand tracking), Quest (controllers) and phones, for fabrication
(digests, U). These are construction and fabrication tools, not design review; they confirm that on Quest the
professional tools chose controllers. Confidence low (digests only).

F9. Studies. A systematic review of AR/VR with BIM (32 of 447 papers, 2017-2022): "most approaches focus on the
construction phase and the use case of review and quality assurance"; "In the design phase, most approaches use VR"
(Yigitbas, Nowosad, Engels, INTERACT'23, arXiv 2306.12274, P). Liu, Castronovo, Messner, Leicht (2020, J. Comput.
Civ. Eng. 34(1)): "VR alone is not necessarily better than traditional media, such as drawings"; better discussion and
efficiency when VR is "orchestrated with" other media; decide by the reviewers' exposure, the review's scope and the
project's complexity (abstract, P). Horvat et al. (ICED19, read in full, P): in VR participants judged size and the fit
of human-scale elements better and estimated dimensions with lower relative error than at a desktop; the difference
grows with the model's complexity; and their review of earlier work records contradictory results, some studies
finding more issues in VR, others the same or fewer, and navigation and manipulation slower in VR (de Casenave and
Lugo 2017, cited there, S). Wolfartsberger (2019, Autom. Constr. 104): more faults seen in VR, faster entry, a
complement to screen review, not a replacement (abstract by digest, S). Paes, Arantes, Irizarry (2017, Autom. Constr.
84): better spatial perception of architectural models in an immersive system than at a workstation (digest, S).
Confidence medium: consistent on spatial understanding and scale, mixed on error finding and speed.

F10. The top tasks (H8), from F1 to F9, in order of how many of the documented apps offer them: (1) navigate at 1:1
(walk, teleport, jump between floors) and switch to a table-top scale model; (2) measure; (3) comments, issues or
markup, usually with speech to text; (4) visibility by layer, tag or category; (5) inspect an element's BIM data;
(6) multi-user sessions and guided tours; (7) saved scenes or views. Section planes are absent from every headset
app read at the source (The Wild, SketchUp Viewer); they appear in desktop and tablet viewers (Dalux, Catenda,
CMBuilder, by digest, U). Editing is rare in headsets except Shapr3D (with a keyboard) and The Wild's massing. What
research says benefits: judging size, fit and space at human scale, and involving people who do not read drawings;
not speed. Confidence medium-high for the ranking (seven products, most read at the source), the absence of sections
medium (two products read in full, others only by digest).

F11. Input on Quest is controller-first in every professional app read at the source (SketchUp: no hand tracking;
The Wild: trigger; Fologram on Quest: controllers, U). Vision Pro apps are hand-and-eye because the device has no
controllers. The two-handed "grip both, spread to scale, twist to rotate" of SketchUp is the documented gesture for
scaling a model; JigSpace's "pull apart" is the documented gesture for separating parts. (P, high.)

### 3.2 Exploded views (H7)

F12. The algorithm. Li, Agrawala, Curless, Salesin (SIGGRAPH 2008, ACM TOG 27(3):101; read in full, P): parts are
organised in an explosion graph that records, for each part, an explosion direction and its current offset; the graph
is built by repeatedly taking the unblocked part with the smallest escape distance; with a part hierarchy it becomes a
nested graph so sub-assemblies expand and collapse independently. The illustrators' conventions they adopt: explode in
unblocked directions; restrict directions to the model's canonical axes ("By default, our system allows parts to
explode only in directions parallel to the coordinate frame axes"); offsets chosen so the parts of interest are
visible; "Compactness. Exploded views often minimize the distance parts are moved". Interaction: expand or collapse
the whole view "with a single click", animated, larger sub-assemblies first; dragging a part slides it along its
direction and pushes or pulls the parts beyond it, so "the user can expand or collapse an entire collection of parts,
just by dragging a single part". Earlier systems offered "a single knob for expanding the entire exploded view"
(Agrawala et al. 2003, cited). Confidence high.

F13. Mechanical CAD. Onshape: an exploded view holds explode steps (translation or rotation, with distance and
direction), placed by dragging a manipulator, reviewed with a rollback bar that shows the explosion in stages
(help, P). Fusion: Auto Explode one level, with an Explosion Scale slider on the toolbar, in the Animation workspace on
a timeline (help, P). SolidWorks: explode steps, auto-space with a Spacing slider, animate explode and collapse (help
pages, by digest, S). Autodesk's web viewer: the Explode extension "Adds an explode button to the toolbar. When
pressed, a slider will be shown which allows changing the model's explosion value"; `viewer.explode(scale)` (APS
reference, P). The common pattern: one amount from 0 (assembled) to full, on a slider, animated. Confidence high.

F14. Buildings. Revit's Displace Elements: selected elements become a displacement set moved along X, Y and Z in one
view, with paths drawn back "to their original model location"; "2D elements such as tags, annotations, or dimensions
cannot be displaced" and "Dimension references are not available for displaced elements" (Autodesk help, P). That
the displacement changes positions only in that view is said by Autodesk's Revit LT help and the tutorials, by digest
(S); the AU 2013 class title, "Revit Now Has Explode... Well Not Quite", gives its date. Autodesk developer blogs:
"View each floor using vertical explode" (2018) buckets objects by Z into 10-unit bands and moves them only vertically,
`pt.z = cz * scale * 4`, driven by a slider with an ease-out animation; "Explode along levels" (2024) assigns each
fragment to the first level whose top lies above the fragment's mid-height, from the model's level data, and offsets
it by `key * scale` (the level's index times the amount), vertical only, reset at scale 0 (P, code read). That Open
Engine's `Exploder` (MIT, `@thatopen/components` 2.4.11, P): groups from the Classifier's `spatialStructures`
(storeys), `height` 10 by default, each group raised by its index times `height`, on or off (no amount between),
applied as a transform of the fragments' instances, not of the data. Confidence high.

F15. Building practice: the exploded axonometric (storeys or layers lifted apart) is a standard presentation drawing;
Revit's feature and its tutorials exist to make it (S, from the tutorials' framing; not searched as a topic of its
own).

### 3.3 The app's own model (H7, Q3)

F16. The hierarchy exists (P, high). `A3D` holds `levels` (`{id,name,elev,height,buildingId}`), `buildings`, `site`,
`layers` and `objs` (`src/js/engine/core/state.js:47-55`). Phase 46's site, building, level hierarchy keeps every level
in exactly one building (`src/js/engine/bim/building-site-hierarchy.js:10-29`). An object's level is
`o.bim.levelId` or `o.levelId` (`src/js/engine/views/saved-views.js:272-276`). Element types are `o.bim.type`: wall,
column, floor, roof, footing, door, ceiling, stair, window, beam, stripfooting, familyInstance (grep count, P). Layers
have parents (`src/js/engine/layers/layer-rules.js:49-56`), and an object's layer is `o.layer`
(`layer-rules.js:8-11`). A classification code per object, `o.classId` (`src/js/engine/bim/classification.js:11-25`).
There is no MEP "system" grouping; disciplines are only ribbon tabs (`src/js/engine/ui/discipline-tabs.js`).

F17. Imported IFC (P, high). The full reader reads `IfcBuildingStorey` elevations and the spatial containment
(`src/js/engine/io/ifc-full.js:121-140`), makes one app level per storey named "<storey> (IFC)" without a building id
(`ifc-full.js:205-208`), and gives each element `bim.storey` (the storey's name), its IFC class's layer under the file's
layer, `pos:[0,0,0]` and its mesh in world coordinates (`ifc-full.js:210-227`). So an imported element has no `levelId`:
grouping by storey must match `bim.storey` to the level named "<storey> (IFC)", or fall back to the element's
mid-height against the levels' `elev` and `height` (the APS 2024 rule, F14). Layers by IFC class are the nearest thing
to "systems" for imported models.

F18. Drawing without changing the model is already the renderer's design (P, high). The GPU scene keeps, per object, a
table row whose first three floats are the object's offset, `v[0]=o.pos[0]; v[1]=o.pos[1]; v[2]=o.pos[2]`, written
every frame by `bimSceneSync` and uploaded only when a row changes (`src/js/engine/render/gpu-batches.js:12-17, 56-61,
144-146`). WebGL and WebGPU draw from it; the rendered view (three.js) builds its triangles as `tri + d[o]` from the
same table (`src/js/engine/render/rendered-scene.js:50-64`); the GPU pick shader adds the same row's `a.xyz`
(`src/js/engine/render/gpu-pick.js:15-20`), so picking would follow an exploded part. A display offset added to that
row moves the part on every GPU path and in picking without a rebuild. The CPU paths add `o.pos` themselves: edges
`src/js/engine/map/terrain-3d.js:299`, the painter's polygons `terrain-3d.js:335` and `:429`, the CPU pick's outline
`src/js/engine/editing/selection-tools.js:49`. Precedent for a display-only substitute: the section view swaps an
object's mesh in `meshOf` (`src/js/engine/core/mesh-primitives.js:185-187`) without touching the object.

F19. `o.pos` is read in 29 engine files, including saving and export (`core/objects-save.js`, `io/ifc-save.js`),
snapping, dimensions and the editing tools (grep, P). An explode that wrote `o.pos` would corrupt saves and exports;
it must be a separate offset read only by the drawing and picking paths. Confidence high.

F20. Undo is a whole-state JSON snapshot (`objs, levels, layers, views, levelFilter, ...`; 50 deep) taken by `pushUndo`
(`src/js/engine/drawing/plan-mode-sketch.js:315-326`) and restored by `bimRestoreState` (`:327-365`). View state is
mixed: `levelFilter` and saved views are in the snapshot, the active section (`A3D.section`) is not. A saved view
records the camera, the level, the level filter and the section (`src/js/engine/views/saved-views.js:24-33`). A
continuous gesture must not push a snapshot per frame; one at the end at most. (P, high.)

F21. "Explode" already means something else here (P, high). `EXPLODE` (alias `X`, `src/js/shell/shell.js:115`) runs
`bimExplodeSelection` (`src/js/engine/commands/command-map.js:349`), AutoCAD's explode: it breaks selected polylines
into line segments, editing the model, with undo (`src/js/engine/editing/drafting-modify.js:159-193`). In
`src/js/engine/io/export-mappings.js:178` "exploded" describes hatching written as lines in DXF export. Neither is an
exploded view. A new command needs another name (for example `EXPLODEVIEW`, typed alias `XV`), and the guide and
command search must say the two apart.

## 4. The app's commands a headset would drive

Typed names from `src/js/shell/shell.js` (line), runners from `src/js/engine/commands/command-map.js` (line), the
function's own file:line where read.

| Headset task (F10) | Gesture family (from gestures.md, to be confirmed there) | Typed command | Runner | Function | Status |
|---|---|---|---|---|---|
| Select an element | point or poke, pinch | (click) | | `selection-tools.js:49` CPU pick; `gpu-pick.js` GPU pick | Exists; needs the XR ray in place of the mouse |
| Select all, clear | menu | `SELECTALL`, `CLEAR` (shell.js:138) | `selAll`, `selNone` (:359-360) | | Exists |
| Move | grab and drag | `MOVE`/`M` (shell.js:116) | `moveTool` (:286) | `startMoveTool`, `drafting-modify.js:42` | Exists, point-by-point; a grab needs a direct-manipulation entry |
| Rotate | two-hand twist | `ROTATE`/`RO` (:124) | `rotate` (:281) | `startRotateTool`, `precision-editing.js:243` | Exists |
| Scale an element | two-hand spread on a selection | `SCALE`/`SC` (:125) | `scale` (:224) | `startScaleTool`, `modify-toolbox.js:429` | Exists; must not be confused with scaling the view (below) |
| Transform handles | grab handles | `GIZMO`/`GZ` (:105) | `gizmo` (:225) | `bimGizmoCommand`, `gizmo-handles.js:1297` | Exists |
| Scale the model as a table-top (view, not edit) | two-hand spread on empty space | none | | | Missing: a view scale, as SketchUp's Tabletop (F3) |
| Walk, 1:1 | teleport, locomotion | `WALK` (:67) | `walk` (:177) | `bimWalkCommand`, `walk/walk-mode.js:172` | Exists (V203, Jolt) |
| Jump between storeys | menu, elevator | (Project Browser) | | `setActiveBuilding`, `building-site-hierarchy.js:31`; level filter `saved-views.js:277-287` | Partial: the active level and its filter exist, no camera jump |
| Measure | two pinches | `DIST`/`MEA` (:131), `AREA` (:131), `DIMLINEAR` (:133) | `inqdist`, `inqarea` (:340-341), `bimDims` (:149) | `startInquiryTool`, `annotation/inquiry.js:115`; `startDimTool`, `dimensions.js:217` | Exists |
| Inspect BIM data | pinch, panel | `LIST`/`LI` (:131) | `inqlist` (:342) | `bimListCommand`; Properties panel | Exists (panel needs a headset form) |
| Visibility by layer | hand menu | `LAYER` (:134), `LAYISO`, `LAYUNISO`, `LAYOFF`, `LAYON` (:134) | `layers` (:358), `layiso` (:329), `layuniso` (:330), `layoff` (:331), `layon` (:334) | `bimLayIso`, `layer-commands.js:81`; `bimLayUniso` `:94`; `bimLayCmdApply` `:65` | Exists, by layer only, with undo |
| Hide or isolate one element | pinch, menu | none | | | Missing (only layer-level isolate) |
| Section | grab a plane | `SECTION`/`SEC` (:104) | `sectionTool` (:208) | `startSectionTool`, `views/section-tool.js:149`; flip `:192`, exit `:199` | Exists as a two-click vertical cut drawn in plan; no movable plane or section box |
| Saved views | hand menu | `SAVEVIEW` (ribbon, command-catalogue.js:30) | | `bimSaveCurrentView`, `saved-views.js:34`; `bimApplyView` `:46` | Exists |
| Fit the model | menu | `ZOOM`/`FIT` (:136) | `zoomFit` (:357) | `fitScene`, `ui/tool-palette.js:456` | Exists |
| Undo, redo | hand menu or a fixed gesture | `UNDO`/`U`, `REDO` (:147-148) | `undo`, `redo` (:383-384) | `doUndo`, `plan-mode-sketch.js:366` | Exists |
| Delete | menu | `ERASE` (:127) | `del` (:356) | `delSelection`, `selection-tools.js:78` | Exists |
| Comments, issues, markup | speech, sketch | `REVCLOUD`/`RC` (shell.js:49) exists for 2D markup | | | Missing: no issue or BCF record (grep for BCF: none) |
| Rendered view | menu | `RENDER` (:69) | `render` (:176) | three.js view | Exists (V194); the XR session would start from it |
| Exploded view | two-hand pull apart | none (`EXPLODE` is the polyline command, F21) | | | Missing: section 6 |
| Multi-user | | none | | | Missing; out of scope |

Missing, in short: a view scale (table-top), a display-only exploded view, element hide and isolate, a movable
section plane or box, a jump-to-storey, issues or comments in the model. The headset view itself is only a header
today (`src/js/engine/render/headset.js`, 5 lines, V274 queued).

## 5. Counter-evidence and threats

- Studies disagree on whether VR finds more design issues, and some find navigation and manipulation slower in VR
  (Horvat et al. citing de Casenave and Lugo 2017; Liu et al. 2020). What holds across them is spatial and scale
  understanding. So the first headset tasks should be looking and judging (1:1, scale model, measure, explode,
  visibility), not editing.
- No vendor read at the source offers a computed exploded building view in a headset. Workshop XR, The Wild, SketchUp
  Viewer and Resolve do not list one; JigSpace's "pull apart" is authored steps. The exploded view in a headset is
  therefore our combination of two established things (BIM viewers' level explode on a slider, F13-F14; the
  two-handed spread of headset apps, F11), not a copied feature. H7's "BIM viewers already offer exploded views" holds
  on desktop and web, not yet shown in headsets.
- Hand tracking is not what the BIM vendors on Quest chose (F3, F11). A gesture-first design runs against their
  practice on Quest; it matches Vision Pro, which has no controllers. The input layer (devices.md) should keep
  controllers as first-class.
- That Open's exploder orders storeys by the classifier's iteration order, not by elevation, and has no amount between
  on and off (F14); copying it would inherit both. The APS 2024 code orders by the model's level list.
- Li et al.'s blocking graph is for interlocking mechanical parts; a building's storeys are stacked and unblocked
  upward, so the graph reduces to "rank times gap". The full algorithm would matter only for exploding an assembly
  (a stair, a family), later.
- Threats: several vendor facts are digests (U) because the hosts refused; vendor pages describe what is sold, not
  what is used; the study list is short and mostly abstracts.

## 6. Recommendation: the exploded view for this app (H7)

1. A view state, never an edit. A record such as `A3D_EXPLODE = {on, amount (0 to 1), by ('storey' | 'building' |
   'layer'), gap (metres), groups}` kept outside `A3D.objs`, like `A3D.section`. A function `bimExplodeOffset(o)` returns
   `[dx,dy,dz]`; `bimSceneSync` adds it to the row's three floats (`gpu-batches.js:144`), which carries it to WebGL,
   WebGPU, the rendered view and the GPU pick (F18); the four CPU sites (`terrain-3d.js:299, 335, 429`,
   `selection-tools.js:49`) add it too. `o.pos` is never written (F19). Saving, exports, schedules and areas see the
   model as it is.
2. By storey first. It is the hierarchy the app already has for its own elements (`levelId`) and, with a matching rule,
   for imported IFC (`bim.storey`, F17); it is what the APS samples and That Open do (F14), and the exploded
   axonometric is a standard drawing (F15). Rule: within a building, sort its levels by `elev`; an object's group is its
   level (by `levelId`, else by `bim.storey` matched to "<name> (IFC)", else the level whose band holds the mesh's
   mid-height, the APS 2024 rule); offset = rank x gap x amount, upward (the app's Y), so the ground stays put and the
   explosion is compact (Li's convention). Objects with no level (site, terrain, annotations) do not move; annotations
   follow their host's level or hide while exploded (Revit cannot displace annotations, F14).
3. By building second: buildings spread apart horizontally along the line between their centres, for a campus.
4. By layer third, as the proxy for "system" or discipline: imported IFC layers by class (walls, slabs, doors) and the
   app's own layers stacked by layer order. A real MEP or structural system grouping does not exist yet (F16); it
   should not be invented for this.
5. One amount, 0 to 1, with three controls on every device: a slider in the panel (desktop, phone), the typed command
   (`EXPLODEVIEW` 0.5, alias to be chosen; not `EXPLODE`, F21), and the two-hand pull in a headset: amount = clamp of
   the change in the distance between the hands divided by a reach constant, with snapping to 0 and 1 near the ends and
   an animated return on release when near 0. Gap defaults to the tallest storey's height, so amount 1 shows a full
   storey of air between floors; the owner may prefer otherwise.
6. Undo. The amount does not go on the undo stack while it moves (a 50-deep snapshot stack would fill in a second,
   F20). Either the explode stays outside undo, like the section, and is cleared by its own gesture or command (the
   recommendation), or one snapshot is pushed when the gesture ends; the owner decides. A saved view should capture
   `by` and `amount`, as it captures the section (`saved-views.js:24-33`).
7. Editing while exploded. Edits and snaps read `o.pos` (F19), so they would land in the wrong place. While the amount
   is above 0, editing tools either collapse the view first or are refused with a toast; selection, Properties, layer
   visibility and measuring between parts of one group stay on. Measuring across groups would measure exploded
   distances: refused or marked. Revit refuses dimension references to displaced elements (F14).
8. Later: an assembly explode for a selection (radial from its centre, on the model's axes, the Autodesk viewer and
   Li's conventions), and the drag-one-part-pushes-the-rest interaction of Li et al. for storeys (pull the top storey up
   and the ones below follow in proportion).

## 7. Which BIM tasks first in XR (H8)

In order, each mapped to section 4: (1) look at 1:1 and as a table-top model, with a view scale that is not an edit
(missing); walk (`WALK`) and jump between storeys (partial); (2) the exploded view by storey (missing, section 6);
(3) measure (`DIST`, `DIMLINEAR`); (4) visibility by layer (`LAYISO`, `LAYUNISO`, `LAYOFF`, `LAYON`) and, new, element
hide and isolate; (5) select and inspect (`LIST`, Properties); (6) saved views (`SAVEVIEW`) and undo, redo; (7) then
section, with a movable plane rather than today's two-click plan cut; (8) editing (`MOVE`, `ROTATE`, `GIZMO`) last,
since the studies and the vendors' choices both say headsets are for judging rather than drafting. Issues and
multi-user are the vendors' core but need a server or a shared file; they are left to the owner.

## 8. Outcomes

H7: holds, with one qualification. The app has a hierarchy to explode by (site, building, level, layer, element type),
for its own elements and for imported IFC by storey name (F16, F17); its renderer already carries a per-object offset
that a display-only explode can use on every GPU path and in picking (F18); BIM viewers on the web and desktop offer
exploded views by level on a slider (Autodesk's viewer, its developer samples, That Open, Revit's displacement sets,
F13, F14). Qualification: no headset BIM app read at the source offers a computed exploded building view (F10, section
5), so the headset gesture is our combination, not prior art. Confidence high for the app, high for desktop and web
prior art, medium for the headset absence.

H8: holds. The vendors' documents give a usable list, and it agrees across products: 1:1 navigation and a scale model,
measure, comments or issues, visibility, inspect, multi-user, saved scenes (F10); research supports spatial and scale
judgement more than speed or error counts (F9). Refinements: section planes are not a headset staple in the apps read;
on Quest the professional apps are controller-first (F11). Confidence medium-high.

## 9. Still open (U)

- Workshop XR's current tool list (measure, category visibility, hands or controllers): its product page and FAQ were
  refused here; read them when allowed, or the owner's copy.
- Resolve's tools (dollhouse, measure, section): digests only.
- Shapr3D's Vision Pro gestures and Unity Reflect's end date: digests only.
- Whether any headset BIM app offers a computed exploded view: none found; a search of Meta's store and visionOS apps
  was not done.
- Whether the rendered view's chunk cache (`rendered-scene.js:46`, its key) rebuilds when only offsets change: to read
  before building; the GPU paths upload changed rows (`gpu-batches.js:56-61`).
- The gesture's reach constant and snapping thresholds: to set from gestures.md's ergonomics, then measured on a device.
- Fuller study reading (Liu et al. 2020, Wolfartsberger 2019, Paes et al. 2017 in full).

## 10. The owner's decisions this topic asks

1. Explode by storey first, then building, then layer: agreed, or another order?
2. The explode outside undo (like the section), or one undo step when the gesture ends?
3. While exploded: collapse on any edit, or refuse edits with a message?
4. The command's name (`EXPLODEVIEW`, alias `XV`?), distinct from AutoCAD's `EXPLODE`.
5. Controllers as first-class beside hands on Quest (the vendors' choice), or hands only?

## 11. References

All read or attempted 2026-11-23.

| Source | URL | What was read | Level |
|---|---|---|---|
| Autodesk, Workshop XR press release, 2023-11-13 | https://adsknews.autodesk.com/en/pressrelease/autodesk-workshop-xr-immersive-design-reviews/ | Whole release | P |
| Autodesk, Workshop XR product page and FAQ | https://www.autodesk.com/products/workshop-xr/overview ; https://workshopxr.autodesk.com/faq | Refused (403; not resolvable); search digests only | U |
| The Wild, VR toolset | https://thewild.com/help/tools-in-vr | The eleven tools | P |
| The Wild, acquisition of Prospect | https://thewild.com/blog/the-wild-acquires-prospect-irisvr | Search digest | S |
| SketchUp Viewer for Meta Quest | https://help.sketchup.com/en/sketchup-viewer/meta-quest | Devices, hand tracking, end of download | P |
| SketchUp, Quest tools | https://help.sketchup.com/en/meta-quest/tools | Tool list (first 100,000 characters) | P |
| SketchUp, moving, rotating and scaling on Quest | https://help.sketchup.com/en/meta-quest/moving-rotating-and-scaling | Gestures, modes | P |
| Resolve | https://www.resolvebim.com/ | Feature headings | P |
| Revizto, Resolve integration, 2025-07-08 | https://revizto.com/en/resolve-and-revizto-launch-vr-integration | Page titles; digest | S |
| Resolve store and press | https://www.meta.com/experiences/resolve/7860400317363640/ ; https://aecmag.com/vr-mr/new-vr-tool-supports-huge-10gb-revit-models-on-oculus-quest/ | Search digests | U |
| Arkio | https://www.arkio.is/ | Home page | P |
| Unity Reflect docs | https://docs.unity.com/reflect/en/manual/Home | 404; search digest | U |
| Shapr3D, Introducing Shapr3D for Apple Vision Pro, 2024-03-27 | https://www.shapr3d.com/blog/introducing-shapr3d-for-apple-vision-pro | Whole post | P |
| Shapr3D, Immersive View help | https://support.shapr3d.com/hc/en-us/articles/16307199006620 | Refused (403); digest | U |
| JigSpace for Apple Vision Pro | https://www.jig.com/apple-vision-pro | Page | P |
| JigSpace, App Store listing | https://apps.apple.com/app/id6456791766 | Description, release notes | P |
| Enscape VR (now docs.chaos.com) | https://learn.enscape3d.com/?p=61437 | Redirect; digest | U |
| Fologram, Bentley SYNCHRO XR, Trimble Connect for HoloLens | search results listed in section 2 | Digests | U |
| Yigitbas, Nowosad, Engels, INTERACT'23 | https://arxiv.org/abs/2306.12274 | Abstract | P |
| Liu, Castronovo, Messner, Leicht 2020, J. Comput. Civ. Eng. 34(1) 04019045 | https://pure.psu.edu/en/publications/evaluating-the-impact-of-virtual-reality-on-design-review-meeting/ | Abstract | P |
| Horvat, Skec, Martinec, Lukacevic, Perisic, ICED19 | https://www.cambridge.org/core/services/aop-cambridge-core/content/view/F906024788EB60F52D2D92A35E761968/S2220434219001987a.pdf | Full paper, read as text | P (its citations S) |
| Wolfartsberger 2019, Autom. Constr. 104:27-37 | https://pure.fh-ooe.at/de/publications/analyzing-the-potential-of-virtual-reality-for-engineering-design/ | Abstract by digest | S |
| Paes, Arantes, Irizarry 2017, Autom. Constr. 84:292-303 | https://structurae.net/en/literature/journal-article/immersive-environment-for-improving-the-understanding-of-architectural-3d-models-comparing-user-spatial-perception-between-immersive-and-traditional-virtual-reality-systems | Digest | S |
| Li, Agrawala, Curless, Salesin 2008, ACM TOG 27(3):101 | https://grail.cs.washington.edu/projects/exview3D/exview3D-SIG08.pdf | Full paper, read as text | P |
| Autodesk, Revit, About Displacement Sets | https://help.autodesk.com/cloudhelp/2023/ENU/Revit-DocumentPresent/files/GUID-361CD6B7-38FA-47B3-86AA-ECF8BD0F8F40.htm | Page | P |
| Revit Displace Elements, other help and tutorials | https://help.autodesk.com/cloudhelp/2025/ENU/Revit-WhatsNew/files/GUID-1FDDA3F9-2171-4439-8C02-6997D59B0297.htm ; https://vdci.edu/learn/revit/creating-an-exploded-axonometric-view-with-displace-elements-in-revit | Digests | S |
| Autodesk APS, Explode along levels, 2024-06-17 | https://aps.autodesk.com/blog/explode-along-levels | Code and text | P |
| Autodesk APS, View each floor using vertical explode, 2018-12-12 | https://aps.autodesk.com/blog/view-each-floor-using-vertical-explode | Code and text | P |
| Autodesk APS, ExplodeExtension reference (v6) | https://aps.autodesk.com/en/docs/viewer/v6/reference/Extensions/ExplodeExtension | Page | P |
| Onshape, Exploded views | https://cad.onshape.com/help/Content/Assembly/exploded_views.htm | Page | P |
| Fusion, Auto Explode one level | https://help.autodesk.com/cloudhelp/ENU/Fusion-Animate/files/ANI-EXPLODE-ONE-LEVEL.htm | Page | P |
| SOLIDWORKS help, auto-space and explode steps | https://help.solidworks.com/2022/English/SolidWorks/sldworks/t_Auto-Spacing_Components.htm | Digests | S |
| That Open, `@thatopen/components` 2.4.11 (MIT) | https://unpkg.com/@thatopen/components@2.4.11/dist/index.mjs ; https://raw.githubusercontent.com/ThatOpen/engine_components/main/LICENSE.md | `Exploder` class, lines 25420-25503; package.json licence; LICENSE.md | P |
| This app | `src/js/engine/...`, `src/js/shell/shell.js` | Files and lines cited in sections 3.3 and 4 | P |
