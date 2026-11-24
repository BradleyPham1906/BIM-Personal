# Assets for a living world: vegetation, people, animation and audio

One of three parallel research notes for the World Engine's look (`docs/research/plan-world-physics.md`); the others
cover weather and sky, and rendering efficiency. Researched 2026-11-24 under `docs/research/research-protocol.md`.
Every downloaded file sat in the session's scratch folder (`.../scratchpad/as-src/`), was read as text or parsed as
data, and was never run. No third-party model, texture, sound or screenshot is in the repository.

## 1. Abstract

The question was what form the World Engine's trees, ground cover, people, vehicles, street furniture and sounds
should take, and from where they may lawfully come, given a public Apache-2.0 repository, ES5 engine code, and
three.js 0.186.1 already vendored. The answer: trees should be generated in the app from the Urban Tree Database
fields it already holds, by a recursive branching generator of the Weber and Penn family (the method of EZ-Tree,
MIT, and of three.js 0.186.1's own TreeGenerator, MIT), written as our own ES5 code from the method, with CC0 bark and
leaf textures, wind sway in the vertex shader in the GPU Gems 3 manner, and leaf-on and leaf-off from the app's
existing growing season. People should be authored, not generated: one CC0 rigged glTF character family
(Quaternius's Universal Base Characters and Universal Animation Library, or Kenney's animated characters, both CC0)
driven by three.js's AnimationMixer from the walkers the traffic simulation already moves, with the clip rate
matched to each walker's speed. Vehicles and street furniture come from CC0 glTF kits (Kenney, Quaternius, Poly
Haven). glTF 2.0 is the one format. Sound uses the Web Audio API through three.js's PositionalAudio, started only
from a user gesture, with rain and wind synthesised from filtered noise and footsteps, traffic and birds from CC0
recordings. Mixamo, Ready Player Me, Quaternius's QAL-licensed packs and the Khronos sample models (mostly CC BY 4.0)
should not ship in the repository without the owner's decision.

## 2. The question and the hypotheses

**Question.** For each kind of living-world asset: generate or author; from which source under which licence; in
what file form; how it animates; what it costs on a phone; and how it plugs into the app's existing trees, glTF
import and walkers.

| # | Hypothesis (falsifiable) | Outcome | Evidence |
|---|---|---|---|
| H1 | A procedural generator can make a tree of the right kind and size from the fields the app already has (leaf type, leaf cycle, size class, height, crown) | **Held in part.** Height, crown and broad form map directly; growth over years needs the Urban Tree Database's age to dbh to height and crown equations, which the archive has but the registry does not yet hold; species look needs a texture per kind | 4.1, 4.2 |
| H2 | A near-field procedural tree fits in 20,000 triangles | **Held** for 14 of EZ-Tree's 16 presets (all 16 run 3,616 to 22,566, mean 13,960; ash large and oak large exceed it) and for three.js's TreeGenerator (6,252, branches only). **But** a block of 1,000 such trees is about 14 million triangles, so one mesh cannot serve every distance | 6.1, 6.2 |
| H3 | EZ-Tree can be vendored unchanged under the third-party rules | **Failed as packaged.** The code is MIT, but its 4.0 MB build inlines 20 bark and leaf images whose source and licence the package does not state; it uses 16-bit indices; it is an ES module with a three peer dependency | 4.1, 6.1 |
| H4 | three.js 0.186.1's TreeGenerator and city generators can be used directly in the app's rendered view | **Failed.** Every generator imports `three/webgpu` and TSL node materials; the app's bundle exports `three` only and its rendered view uses WebGLRenderer. Their geometry code is plain three core and its method is reusable | 4.1 |
| H5 | Rigged human characters with walk, run and idle exist under a licence that lets a public repository carry the files | **Held** for CC0 sources (Quaternius CC0 packs, Kenney, MakeHuman's exports, RobotExpressive in three.js's own repository). **Failed** for Mixamo (no free distribution of raw files), Ready Player Me (services ended 31 January 2026) and Quaternius's QAL packs (no redistribution as standalone assets) | 4.4 |
| H6 | The vendored three.js bundle already has what skeletal animation and positional sound need | **Held** for AnimationMixer, AnimationAction, SkinnedMesh, AudioListener and PositionalAudio (exported names found in `runtime/three/0.186.1/bim-three.min.js`). **Not** SkeletonUtils, whose `clone()` is needed to copy a skinned character: an addon, absent from the bundle | 4.5 |
| H7 | The app's walkers carry what an animated figure needs (position, heading, speed) each step | **Held**: `W.x`, `W.z`, the previous `W.px`, `W.pz`, and `W.v` | 8 |
| H8 | Common walk and run clips are "in place" (the hips do not travel forward) | **Held** for the three files measured (RobotExpressive, Soldier, Xbot): the hips move a few centimetres, not a stride | 6.4 |
| H9 | glTF 2.0 is the right single format for skinned, animated, PBR, compressed assets | **Held** against OBJ (no skins, no animation) and FBX (no open specification; three.js's loader reads 7.0 and later only) | 4.6 |
| H10 | The Web Audio API renders 32 positioned sources with HRTF in real time | **Held** here (about 3.6 times real time on a 4-core Xeon); a phone not tested | 6.5 |
| H11 | An AudioContext made before a user gesture starts suspended | **Not testable here**: headless Chromium 158 started it running even with `--autoplay-policy=user-gesture-required`. Chrome's policy page, the Web Audio specification and MDN all say a browser may hold it suspended until a gesture, so the design must assume it | 4.7, 6.5 |
| H12 | Web Audio's inverse distance model with rolloff 1 gives the free field's 6 dB loss per doubling of distance | **Held**: measured -6.02 dB at 2 m, -24.08 dB at 16 m (reference 1 m) | 6.5 |

## 3. Method

Read first: the research protocol, `reuse-first-integration.md`, CLAUDE.md's third-party rules and standing choices,
the plan's people, sound and wind rows, and the app files named in section 8 (grep first). Then each topic's sources
at their primary location, licences at their source, and five experiments (section 6), scripts and raw output in
`docs/research/experiments/world-look/as-*`. Independent second reading: not yet done (the protocol's step 9 is for
the orchestrating session to assign).

### Search log

| Where | Query or address | What came back | Kept or set aside, and why |
|---|---|---|---|
| npm registry | `@dgreenheck/ez-tree` metadata | 1.1.0 (15 January 2026), MIT, peer `three >=0.167`, no dependencies, 93 files, 23.9 MB unpacked | Kept: primary |
| npm registry | ez-tree-1.1.0.tgz | 19.5 MB tarball, SHA-256 4147b49d...; LICENSE, src/lib, build | Kept, read as text |
| npm registry | three-0.186.1.tgz | `examples/jsm/generators/` holds TreeGenerator, ForestGenerator, TerrainGenerator, CityGenerator and city/ (PersonGenerator, StreetTreeGenerator, CarGenerator, bench, hydrant, streetlight...) | Kept: a finding not expected (H4) |
| app repository | `tools/three/build_three.mjs`, the bundle | the bundle exports `three` plus GLTFLoader, GLTFExporter, DRACOLoader, meshopt | Kept |
| algorithmicbotany.org | ABOP PDF; Runions et al. 2007 PDF | both answered (16.8 MB, 1.8 MB) | Kept: primary (method only; ABOP is "all rights reserved", so no text copied) |
| Web search | Weber Penn 1995 PDF | a Duke course copy of the SIGGRAPH paper | Kept as S (a course copy, not ACM's) |
| developer.nvidia.com | GPU Gems 3 ch. 6; GPU Gems 1 ch. 7 | both answered | Kept: primary |
| fs.usda.gov | RDS-2016-0005 catalogue page | the allometric equations described | Kept |
| quaternius.com | home, FAQ, licence, 16 pack pages | per-pack licence; the QAL v1.0 text (updated 28 August 2026) | Kept: primary |
| kenney.nl | /support, 4 asset pages | CC0 on each page | Kept |
| raw.githubusercontent.com | MakeHuman LICENSE.md | assets and exports CC0, code AGPL | Kept |
| helpx.adobe.com | Mixamo FAQ (several regional copies) | 403 to scripts and to the fetch tool | Recorded as refused |
| community.adobe.com | the Mixamo licensing FAQ thread | an Adobe-posted FAQ (2022) on raw file distribution | Kept as S (Adobe's community copy, older) |
| readyplayer.me, docs.readyplayer.me | home and terms | no answer (connection failed) | Refused; TechCrunch (19 December 2025) read instead through the fetch tool, S |
| polyhaven.com | /license | CC0 for HDRIs, textures, models | Kept |
| KhronosGroup on GitHub | glTF-Sample-Assets README, three model READMEs; glTF specification source (AsciiDoc); EXT_mesh_gpu_instancing | per-model licences, mostly CC BY 4.0; the spec's skins and morph targets | Kept (registry.khronos.org answered 403, so the spec's own source on GitHub was read) |
| mrdoob/three.js at r186 | RobotExpressive README and four example .glb files | CC0 for RobotExpressive; no licence file for the Mixamo-derived ones | Kept as measurement data only |
| paulbourke.net | OBJ specification | answered | Kept |
| docs.blender.org | FBX importer page | describes FBX's use; no specification | Kept as S |
| freesound.org | /help/faq | licence explanation | Kept |
| creativecommons.org | CC0 1.0 legal code | read | Kept |
| developer.chrome.com, MDN | autoplay policy; autoplay guide | read | Kept |
| webaudio.github.io | Web Audio API 1.1 editor's draft (17 November 2026) | distance models, HRTF, "allowed to start" | Kept: primary (w3.org was refused in earlier sessions; the draft lists the 2021 Recommendation as a previous version) |
| GitHub API | ez-tree repository tree | refused: the session's GitHub access is bound to its repositories | Recorded; the npm package was read instead |

## 4. Findings, by topic

### 4.1 Vegetation: generated or authored

**Generation is the right default for trees; authored models for close-up hero specimens only.** The app's trees are
data-driven (type, height, crown from the Urban Tree Database, season from ETCCDI's growing season), and a generator
turns those numbers into geometry with no download per species; an authored model library would need one licensed
file per species and size and could not grow. (Confidence: medium; a judgement from the evidence below.)

**EZ-Tree 1.1.0** (MIT, Daniel Greenheck; P, read as text). A breadth-first queue of branches, each a tube of
`sections` rings of `segments` sides, without caps; children placed along the parent between `start` and the tip,
tilted by `angle` and spread evenly round the parent; each ring's orientation jittered by `gnarliness` (stronger on
thin branches) and pulled towards a growth `force` direction; deciduous branches continue from their tip; leaves are
one or two crossed alpha-tested quads. Parameters per level: levels (0 to 3), angle, children, gnarliness, length,
radius, sections, segments, start, taper, twist; leaves: type, billboard, angle, count, start, size, size variance,
tint, alpha test. Sixteen presets (ash, aspen, oak, pine in three sizes, three bushes, a trellis). Wind: a vertex
shader added through `onBeforeCompile`, leaves only, three sine terms phased by 3D simplex noise and weighted by the
leaf's `uv.y`, so branches do not sway. Defects read: indices are `Uint16Array`, so a tree past 65,535 vertices
would wrap (no preset does; the "high" setting tested reached 41,440 leaf vertices); one comparison tests
`type === 'Deciduous'` against the enum's `'deciduous'`, so that branch of the code never runs. Its build is 4.0 MB
because 16 JPEG and 4 PNG textures are inlined; neither the README nor the package states where the textures came
from, and their files carry no metadata (checked). **Licence of the textures: U.** Level P for the code; confidence
high.

**three.js 0.186.1 TreeGenerator** (MIT; P). Recursive tapered tubes with a parallel-transport frame, children on the
upper part of each parent rolled by the golden angle, child radius by the pipe model (child = parent x (1/n)^(1/2.3)),
an upward pull, gravity droop and a root flare; branches only, "add foliage as a separate layer"; switches to 32-bit
indices above 65,535 vertices. ForestGenerator scatters icosphere crowns in one InstancedMesh with a distance cull;
PersonGenerator makes a low-poly crowd in two baked poses (walk, stand), instanced; StreetTreeGenerator a young tree
with a pit grate. **All import `three/webgpu` and `three/tsl`** (MeshStandardNodeMaterial); the app's bundle does not
export them and its rendered view is WebGLRenderer (`render/rendered-view.js` lines 83 and 92). Confidence high.

**Weber and Penn 1995** (SIGGRAPH '95, pp. 119-128; S, a course copy of the paper). The parametric model both
generators descend from: per-level stems with curvature (`nCurve`, `nCurveBack`, `nCurveRes`), splits, `nBranches`,
a crown **Shape** chosen from a table (conical, spherical, hemispherical, cylindrical, tapered cylindrical, flame,
inverse conical, tend flame, and a pruning envelope), lobes, leaves. It already treats wind as time-varying
curvature of each stem (sway angles from wind speed and gust, a sum of sines) and argues that discrete levels of
detail make visible "resolution waves", proposing a continuous degradation at range; it puts its trees at 5,000 to
100,000 facets. Blender's Sapling add-on implements it under the GPL, so only the paper's method may be used. Level
S; confidence high on the method.

**L-systems** (Prusinkiewicz and Lindenmayer, *The Algorithmic Beauty of Plants*, electronic edition 2004, "all rights
reserved"; P). String rewriting with a turtle interpretation; very expressive for botanical structure but the
grammar per species must be authored, and the parameters do not map onto the Urban Tree Database's fields without a
fitting step. Method only. Confidence high.

**Space colonisation** (Runions, Lane and Prusinkiewicz, Eurographics Workshop on Natural Phenomena 2007; P). A crown
envelope is filled with attraction points; nodes grow towards points within a radius of influence; points are
removed within a kill distance; limb thickness by the pipe model. Its parameters map unusually well onto the app's
data: **the envelope is the crown** (height and crown diameter from the database), and the number of attraction
points sets density. Cost is an iterative nearest-node search (heavier than recursive branching; fine once per
archetype, not per frame). Confidence high on the method; cost U until measured.

**Mapping the app's fields to a generator** (our proposal, U until built and checked against photographs of the
database's species). Leaf type B or C selects deciduous-style recursive branching with a terminal leader or a
conifer whorl with a cone (Weber and Penn's Shape 0 for conifers); size S, M or L and the record's height and crown
set trunk length and the crown envelope; the crown ratio `r` picks the Shape (above about 0.95 spreading or
hemispherical, about 0.75 to 0.95 spherical, below about 0.75 tapered or flame); leaf cycle E or D decides whether
leaves are dropped outside the growing season. **Growth over years:** the Urban Tree Database (RDS-2016-0005) holds
365 sets of eight equations, for about 20 species in each of 16 climate regions: age predicts dbh, and dbh predicts
height, crown diameter, crown height and leaf area (P, the archive's catalogue page). Age therefore drives the size,
and leaf area drives the leaf count, with the registry's edition rules; the equations themselves are not yet read
(U). **Seasons:** the app already decides leaf-on and leaf-off by date from ETCCDI's growing season
(`bimEntBare`, `bimEntInLeaf`), and its tree meshes already keep the trunk faces first (`cf`) so a bare tree is the
first `cf` faces. A generated tree should keep the same split: a branch mesh and a separate leaf mesh, so leaf-off
draws only the first. Autumn colour and leaf fall can be a tint and a leaf-count ramp over the season's last weeks
(U, no source read).

**Wind sway** (GPU Gems 3, chapter 6, Renaldas Zioma; P). A tree as a shallow hierarchy of rigid segments (two to
three levels suffice), each rotating about its joint with its parent; motion synthesised from noise and periodic
functions in the vertex shader, which instances well. EZ-Tree's leaf shader is a simpler case of the same idea;
Weber and Penn's sway formula a third source. For the World Engine: bake per vertex the branch level, a phase and a
stiffness weight (the distance from the trunk's base along the branch), and let a uniform carry the wind speed and
direction from the weather system (V294 later). Confidence high.

**Ground cover and grass** (GPU Gems 1, chapter 7, Kurt Pelzer; P). Many blades stand in for few polygons: grass
"objects" of textured quads, instanced over the ground, animated by moving only the upper vertices (told apart by
their texture coordinate) in the vertex shader. ForestGenerator's stochastic distance cull is the modern three.js
form. For the app: grass as instanced crossed cards in a ring around the camera, density by distance, a CC0 grass
texture (Poly Haven); never as model geometry. Confidence medium (one primary source plus three.js's code).

### 4.2 What form trees must take for instancing and level of detail

For the rendering agent's instancing and LOD work, each tree is an **archetype** (kind x size class x seed; for
example the database's 9 kinds x 3 seeds = 27), generated once and drawn many times with a per-instance transform
(position, a yaw, a scale fitted to the record's height and crown) and a per-instance leaf-on flag. Each archetype is
two geometries: branches, and leaf cards (so leaf-off and wind act on each). Each vertex carries the wind data above.
Three levels: near (about 10,000 to 20,000 triangles), mid (about 3,500, measured in 6.1 by halving rings and
quartering leaves), far (a crossed-card or impostor billboard). The same applies to glTF street furniture
(`EXT_mesh_gpu_instancing` is a ratified Khronos extension that stores instance transforms in the file). Indices
32-bit where an archetype passes 65,535 vertices.

### 4.3 Vehicles and street furniture

CC0 glTF kits answered with their licence on each page (P): Kenney's Car Kit (45 files), City Kit (Commercial),
Nature Kit (330 files); Quaternius's Cars, Public Transport, Modular Streets, Downtown City MegaKit (315 pieces, glTF)
and Stylized Nature MegaKit (glTF). Poly Haven: all models, textures and HDRIs CC0, redistribution allowed (P).
Khronos sample models carry per-model licences, mostly CC BY 4.0 (CesiumMan, RiggedFigure: Cesium; Fox: tomkranis,
converted by AsoboStudio and scurest) (P): shippable only with credit, and CC BY is not in CLAUDE.md's list, so it is
the owner's decision. V207's glTF import already reads glTF and GLB with Draco and meshopt; it does not read KTX2
textures yet (`io/gltf.js` line 39, `BIM_GLTF.KTX`). For the simulation, a vehicle's wheels should be separate nodes
so they can turn; the app's design vehicles (`bimEntVeh`) keep their AASHTO sizes, and a model is scaled to them.

### 4.4 People: why generated humans are hard, and where rigged ones may come from

A moving human needs a mesh, a skeleton bound to it with per-vertex weights (glTF's linear blend skinning: `JOINTS_0`
and `WEIGHTS_0`, four influences a vertex, eight with `JOINTS_1`; P, the specification's Skins section), and
animation clips authored or captured for that skeleton. Generating the mesh is the easy part (three.js's
PersonGenerator does it, but poses it statically); generating plausible weights and motion is not, which is why
practice uses authored rigs and motion libraries and retargets between them (three.js ships
`SkeletonUtils.retargetClip`). Confidence high.

| Source | Licence read at the source | May the public repository carry the files? | Level |
|---|---|---|---|
| Quaternius CC0 packs (only a portion of each kit is free; the rest goes to supporters: independent check): Universal Base Characters (26 models, glTF), Universal Animation Library (120+ clips, GLB) and Library 2 (130+, January 2026), Ultimate Animated Character Pack, Animated Men and Women | CC0 on each pack's page; the FAQ: no attribution, modification allowed | Yes | P |
| Quaternius QAL packs | QAL v1.0: use in products allowed, but no redistribution "as a standalone asset" even when modified | **No** without a ruling: a public repository's files are extractable as such | P |
| Kenney Animated Characters (and the rest of Kenney) | CC0 (support page and each asset page) | Yes | P |
| MakeHuman | code AGPL; bundled assets CC0; the project claims nothing over exports (FBX, OBJ, DAE, MHX2) | Yes for exports from bundled assets only; third-party community assets each have their own licence | P |
| RobotExpressive in three.js's repository | CC0 1.0, by Tomás Laulhé (Quaternius), modified by Don McCurdy | Yes | P |
| Mixamo (Adobe) | official FAQ refused (403); Adobe's community FAQ (2022): royalty free in projects, but no free distribution of raw character or animation files, not to non-team members, no machine-learning training | **No** | S |
| Ready Player Me | site and docs did not answer; TechCrunch: Netflix acquired it on 19 December 2025, and it wound its services down on 31 January 2026 | **No**: the service is gone, and its terms cannot be read | S |
| Khronos samples (Fox, CesiumMan, RiggedFigure) | CC BY 4.0 | Only with credit and the owner's approval | P |

### 4.5 Skeletal animation in three.js and the app's walkers

The pinned bundle exports AnimationMixer, AnimationAction, AnimationClip, SkinnedMesh and Skeleton (P, grep of the
bundle). AnimationAction offers `setEffectiveWeight`, `setEffectiveTimeScale`, `crossFadeTo`, `syncWith` and `warp`
(P, `src/animation/AnimationAction.js`). Blending by speed: keep idle, walk and run playing, synchronised, and set
their weights from the walker's speed (idle below about 0.2 m/s, walk to about 2 m/s, run above; our proposal, U);
set each clip's time scale to the walker's speed divided by the clip's own speed (stride per cycle over cycle time),
which is what stops the feet sliding. The clips measured are in place (6.4), so the app moves the figure and the
clip only animates the limbs; the stride per cycle of each clip must be measured once from its foot bones (not done
here: it needs the skeleton's forward kinematics). The app's walkers already step at a fixed rate with
`W.x, W.z, W.px, W.pz, W.v` (section 8): heading is the step's direction, speed is `W.v` (mean desired 1.34 m/s,
spread 0.26, registry `hm.walk`). Cloning a skinned character needs `SkeletonUtils.clone`, which is not in the bundle:
`tools/three/build_three.mjs` would add one export line. Cost: every SkinnedMesh is its own skeleton update and draw;
the simulation's pools reach 3,000 walkers at Detailed (`BIM_TR_Q`), so only the nearest few dozen can be skinned;
the rest must be instanced static poses (as PersonGenerator does) or vertex-animation textures (the rendering note).
Confidence medium (API P; thresholds U).

### 4.6 Format: glTF 2.0 against OBJ and FBX

| Need | glTF 2.0 | OBJ | FBX |
|---|---|---|---|
| Hierarchy | nodes with transforms (P) | groups only, no transforms (P) | yes |
| Skins | linear blend skinning, 4 or 8 weights (P) | none (the specification has no skin or bone statement; its "animation" mentions are an old viewer's level of detail) | yes |
| Animation | keyframed translation, rotation, scale, morph weights (P) | none | yes |
| Materials | metallic-roughness PBR in the core (P) | MTL, not PBR | vendor-specific |
| Compression | Draco, meshopt, quantisation, KTX2 extensions (P) | none | binary only |
| Instancing | `EXT_mesh_gpu_instancing`, ratified (P) | none | none standard |
| Open | Khronos specification, royalty free | published text | **no open specification**; three.js's FBXLoader reads 7.0 and later ASCII or 6400 and later binary only (P, its header) |
| In the app | read and written since V195 | not for skinned assets | not bundled |

glTF is the one format (high confidence). Quaternius and Kenney ship glTF or GLB for the packs above; where a pack is
FBX only, conversion happens outside the repository and the converted file's provenance is recorded.

### 4.7 Audio

**The API** (Web Audio API; the W3C Recommendation of 17 June 2021, and the 1.1 editor's draft of 17 November 2026,
P). PannerNode positions a source against the AudioListener; `panningModel` is `equalpower` or `HRTF` (convolution
with measured human impulse responses); `distanceModel` is `linear`, `inverse` or `exponential`, the inverse model
being ref / (ref + rolloff x (max(d, ref) - ref)). An AudioContext is "allowed to start" only if the user agent lets it
move from suspended to running, which it may permit only after the page has sticky activation (a user gesture).
three.js wraps this: one global context (`AudioContext.getContext()`), `AudioListener` on the camera, and
`PositionalAudio`, whose panner defaults to HRTF (P, three's source).

**Autoplay** (Chrome's policy page and MDN, P). Since Chrome 71 the Web Audio API is under the autoplay policy: a
context made before a gesture is suspended and must be `resume()`d after one, or made in the gesture's handler. The
app should make its context in the handler of a "Sound on" control and never before. MDN also documents
`navigator.getAutoplayPolicy('audiocontext')`; Chromium 158 does not have it (measured, 6.5).

**What a living world needs, and how to make it.** Rain and wind are broadband noise shaped by filters and gain
envelopes, which Web Audio synthesises from a looping noise buffer and a biquad filter at almost no download cost
(measured cheap, 6.5), driven by the weather system's rain rate and wind speed. Footsteps, engines, tyres, birds,
voices and crowd murmur are hard to synthesise convincingly and are better as short CC0 recordings, varied by pitch,
gain and choice among several takes (practice; Andy Farnell's *Designing Sound* argues the procedural side at length,
**U**, not read). Traffic noise should be one source per nearby vehicle up to a cap, and a filtered bed for the rest.
Reverberation can use ConvolverNode with an impulse response (the plan's V293 computes reverberation times).

**Sources.** Freesound offers CC0, CC BY and CC BY-NC per sound (P, its FAQ), and still carries older Sampling+
sounds (independent check); only CC0 should ship, filtered on the
site, and the sound's page recorded. CC0 1.0 waives copyright and falls back to an unconditional licence, but keeps
trademark and patent rights and gives no warranty (P, the legal code). Poly Haven has no sounds. EZ-Tree's package
carries a 1.0 MB `ambience.mp3` of unstated origin: not usable.

**Memory.** Decoded audio is 32-bit float: 10 s of stereo at 48 kHz is 3.84 MB in memory whatever the file's size
(arithmetic), so long beds should loop short buffers or stream through a media element.

## 5. The alternatives compared

Criteria, stated before the comparison: (a) licence lets the public repository carry it; (b) download and memory
size; (c) realism at street distance; (d) fits the build contract (ES5 adapter, pinned, on demand, behind an
adapter); (e) works offline; (f) phone cost.

### 5.1 Trees

| Option | (a) Licence | (b) Size | (c) Realism | (d) Contract | (e) Offline | (f) Phone |
|---|---|---|---|---|---|---|
| Keep today's six-sided trunk and twenty-face crown | ours | 0 | low | yes | yes | trivial |
| **Our own ES5 generator from the Weber and Penn method (as EZ-Tree and TreeGenerator do it), CC0 textures** | ours, method credited | code only, plus about 0.5 to 1 MB of CC0 textures | medium to high | yes | yes | fine with archetypes, instancing and LOD |
| EZ-Tree vendored | code MIT; textures U | 4.0 MB build | high | an ES module, needs a three peer, 16-bit indices | yes | the same as above |
| three.js TreeGenerator and Forest | MIT | in the three package | medium (branches only) | needs `three/webgpu` and TSL in the bundle | yes | WebGPU path only |
| Space colonisation, our own | ours | code only | high, crown-true | yes | yes | generation heavier, once per archetype |
| Authored CC0 tree models (Quaternius, Kenney, Poly Haven) | CC0 | 0.1 to several MB each | stylised (Quaternius, Kenney) to photoreal (Poly Haven) | glTF import exists | yes once pinned | high-poly Poly Haven trees too heavy en masse |

**Recommendation:** our own generator (the second row), with space colonisation as its crown-filling mode once the
recursive one works, and Poly Haven CC0 models only as optional near-field hero trees. It would change if the owner
accepts EZ-Tree's code and its textures' origin is found to be CC0 (then vendor the code, swap nothing), or if the
app moves its rendered view to WebGPURenderer (then three's own generators become usable).

### 5.2 People

| Option | (a) | (b) | (c) | (d) | (e) | (f) |
|---|---|---|---|---|---|---|
| Today's column with a head | ours | 0 | low | yes | yes | trivial |
| **CC0 rigged glTF (Quaternius Universal Base Characters with the Universal Animation Library; or Kenney) with AnimationMixer** | CC0 | about 0.5 to 3 MB a character with clips (6.3) | medium to high | yes, glTF and three core | yes | skinned only near; instanced poses far |
| three.js PersonGenerator (posed, instanced) | MIT | code | low to medium, no limb motion | needs WebGPU/TSL | yes | cheapest crowd |
| MakeHuman exports | CC0 (bundled assets) | per export | high | yes | yes | heavy unless decimated |
| Mixamo | raw files may not be distributed | | high | | | |
| Ready Player Me | service ended | | | | | |

**Recommendation:** the CC0 rigged glTF row, skinned for the nearest figures and instanced static or baked poses
beyond, from one character family so one skeleton serves all clips.

### 5.3 Sound

| Option | (a) | (b) | (c) | (d) | (e) | (f) |
|---|---|---|---|---|---|---|
| **Web Audio through three's PositionalAudio; rain and wind synthesised; CC0 samples for the rest** | CC0 or ours | a few MB of samples | good | browser API, no library | yes | cap the voices (6.5) |
| All synthesised | ours | 0 | rain, wind good; footsteps, engines poor | yes | yes | cheap |
| All recorded | CC0 only | tens of MB | best | yes | yes | memory-heavy when decoded |

## 6. The experiments

Environment: Node 22 and Playwright's Chromium 158.0.8127.36, headless, on a 4-core Intel Xeon at 2.30 GHz. No phone.

### 6.1 EZ-Tree's triangles, worked out from its code (as-tree-triangles.js)

A counter written here from the reading of `tree.js` (EZ-Tree's code was not run), applied to its 16 preset files as
data. Raw output: `as-tree-triangles.out.txt`. Selected: aspen small 3,616 triangles; oak small 6,806; oak medium
13,806 (3,166 branch, 10,640 leaf); pine medium 19,872; oak large 22,566 (the most); all within 16-bit indices. Three
detail settings of oak medium: low (half the rings, the minimum sides, a quarter of the leaves, single quads) 3,434;
as shipped 13,806; high (double rings, 1.5 times sides, double leaves) 31,044, with 41,440 leaf vertices. Pine
medium: 3,820; 19,872; 49,776. Limit: the counts are from a re-implementation of the topology, not from running the
library; the random parts change positions only, not counts.

### 6.2 three.js TreeGenerator's triangles (as-treegen-triangles.js)

From `growBranch` and `createGeometry` read as text; with its defaults the count does not depend on the seed. Levels 3:
40 tubes, 1,068 triangles; levels 4 (defaults): 328 tubes, 6,252; levels 5: 1,480 tubes, 26,988; a 20 m trunk at
defaults: 9,120. Branches only.

For comparison the app's tree today is 12 trunk triangles and 20 crown faces (`bimEntTreeMesh`).

### 6.3 Rigged glTF characters, parsed as data (as-glb-stats.js)

SHA-256 of the files in `as-glb-stats.sha256.txt`; output in `as-glb-stats.out.txt`.

| File (three.js r186 examples) | Licence | Bytes | Triangles | Joints | Clips |
|---|---|---|---|---|---|
| RobotExpressive.glb | CC0 | 463,988 | 3,237 | 43 (two skins), 3 morph targets | 14 (Idle, Walking, Running, ...), 94 KB of keys |
| Soldier.glb | Mixamo-derived, no licence file | 2,160,468 | 11,376 | 49 | Idle, Walk, Run, TPose; 242 KB of keys, 663 KB of textures |
| Xbot.glb | Mixamo-derived | 2,930,032 | 49,112 | 67 | 7, 714 KB of keys |
| Michelle.glb | Mixamo-derived | 3,276,888 | 28,106 | 65 | 2, 1.43 MB of keys |

All use four weights a vertex. A low-poly CC0 character with a dozen clips is under 0.5 MB; full-body Mixamo-style
rigs with 65 joints are 2 to 3 MB and keyframes can outweigh the mesh. Quaternius's own files were not downloaded
(its downloads are behind itch.io and Google Drive pages), so their sizes are U.

### 6.4 Root motion (as-glb-rootmotion.js)

The largest translation range of any animated node in each walk, run and idle clip: RobotExpressive's Walking moves
a foot 0.019 in z over 0.958 s; Soldier's Walk moves the hips 8.5 units in z and Xbot's walk 0 in z (Mixamo rigs in
centimetres under a 0.01 scale: a bob and sway of a few centimetres, not a 1.3 m stride). All in place (H8 held).

### 6.5 Web Audio in Chromium (as-webaudio.js, three runs)

Rendering 10 s of a soundscape offline, N sources each a looping noise buffer through a band-pass filter and a moving
PannerNode, real-time factor (higher is better), runs 1, 2, 3: equal-power 1: 117, 110, 55; 8: 14.9, 16.0, 14.8; 32:
3.9, 3.9, 3.7; 64: 2.0, 1.8, 1.9. HRTF 1: 29.7, 28.4, 27.9; 8: 15.8, 15.3, 15.1; 32: 3.7, 3.5, 3.6; 64: 1.8, 1.6, 1.7.
The cost grows about linearly with sources; HRTF costs more only at one source. On this machine 64 sources leave
under half the audio thread free; a phone, several times slower, should cap at about 16 voices (U until measured).
Inverse model gains at 1, 2, 4, 8, 16 m: 1, 0.5, 0.25, 0.125, 0.0625 (0 to -24.08 dB). The autoplay check could not
be made: the context was running before any gesture, with or without `--autoplay-policy=user-gesture-required`, and
`navigator.getAutoplayPolicy` was absent.

## 7. Edges

- A tree past 65,535 vertices in one mesh breaks EZ-Tree's 16-bit indices (the high settings approach it).
- Leaf-off must hide the leaf mesh, not shrink it; evergreen conifers keep leaves all year (`cyc==='E'`).
- A site with no fetched climate has no growing season: the app keeps leaves all year and says so (`bimEntSeasonText`).
- Walkers below about 0.2 m/s (waiting at a crossing, `W.wait`) must idle, not walk on the spot.
- A walker turning sharply between two steps would pivot on the spot; heading should be smoothed over a few steps.
- CC0 waives copyright, not trademarks: a CC0 vehicle model with a real maker's badge still must not be shipped.
- A CC BY asset needs its credit on every page and export that shows it.
- Audio before a gesture: the context may be suspended; any sound code must cope with `state === 'suspended'`.
- `file://`: decoding an audio file fetched from `file://` may be refused by some browsers; inline or user-chosen
  files are safer (U, not tested).

## 8. What the app already has

| What | Where |
|---|---|
| Tree type from the Urban Tree Database (leaf, cycle, size) and its height, crown, ratio | `src/js/engine/assets/scale-assets.js` lines 116-124 (`bimEntTreeType`, `bimEntTreeSize`); registry `utd.trees`, `src/js/engine/standards/registry.js` line 323 |
| The tree mesh: six-sided trunk, icosahedron or eight-sided cone crown, trunk faces first (`cf`) | `scale-assets.js` lines 127-148 |
| Leaf-off by date from ETCCDI's growing season | `scale-assets.js` line 249 (`bimEntBare`); registry `etccdi.gsl` line 328; shadows `src/js/engine/site/shadows.js` line 34 |
| Mapped trees from OpenStreetMap's leaf tags | `scale-assets.js` lines 150-156; `src/js/engine/map/surroundings-3d.js` line 321 |
| Design vehicles at AASHTO's sizes | `scale-assets.js` `bimEntVeh`, `bimEntVehMesh` |
| glTF in and out, Draco and meshopt, KTX2 not read | `src/js/engine/io/gltf.js` lines 22-39; `src/js/engine/assets/gltf-assets.js` (V207's pure part) |
| three.js 0.186.1 with AnimationMixer, SkinnedMesh, PositionalAudio, AudioListener; no SkeletonUtils | `runtime/three/0.186.1/bim-three.min.js`; `tools/three/build_three.mjs` lines 30-34 |
| Walker pools, speed, position, previous position | `src/js/engine/simulation/traffic-sim.js` lines 19 (`BIM_TR_Q`: 300, 1,000, 3,000 walkers), 191-214, 465-512 |
| Walkers drawn as a column with a head | `src/js/engine/simulation/traffic-draw.js` lines 14-20 |
| No skeletal animation and no audio in the engine | grep for `AudioContext`, `SkinnedMesh`, `AnimationMixer` in `src/`: none |

## 9. Risks and threats to validity

- Triangle counts come from re-implemented counters, not from running the libraries (by rule).
- Mixamo's terms read only in Adobe's 2022 community copy; Ready Player Me's only in the press; both S.
- Quaternius's per-pack licences can change for new releases (QAL clause 7 says changes are not retroactive); the
  licence of a pinned file must be recorded with its download date and page.
- The QAL reading (no standalone redistribution) is ours, not legal advice.
- One browser, one desktop CPU; no phone, no Safari or Firefox for audio.
- Weber and Penn read from a course copy, not ACM's.

## 10. What is still open (U)

- EZ-Tree's texture origin and licence; its ambience recording's origin.
- The Urban Tree Database's growth equations themselves (the files, the regions, which species).
- The stride per cycle of each chosen walk and run clip; the speed thresholds for idle, walk and run.
- Sizes and joint counts of Quaternius's Universal Base Characters and Universal Animation Library files.
- Phone cost of skinned characters and of HRTF voices.
- Autoplay behaviour in a headed Chrome, Safari and Firefox.
- *Designing Sound* (Farnell) and any acoustic source for the loudness of rain, wind and traffic.
- The independent second reading (protocol step 9).

## 11. The owner's decisions

1. Trees: our own ES5 generator from the published method (recommended), or vendor EZ-Tree's MIT code once its
   textures' licence is known?
2. People: may the repository carry one CC0 character family and its clips under `runtime/` (pinned like three.js),
   and which (Quaternius's Universal set, or Kenney's)?
3. May CC BY 4.0 assets (Khronos samples, some Freesound sounds) ship with credit, or CC0 only?
4. Sound on by default after the first click anywhere, or only through an explicit "Sound on" control?
5. Add `SkeletonUtils` to the three.js bundle (one export line in `tools/three/build_three.mjs`)?

## 12. References

All read 2026-11-24.

| Source | URL | What was read | Level | Licence |
|---|---|---|---|---|
| EZ-Tree 1.1.0, npm package | https://registry.npmjs.org/@dgreenheck/ez-tree/-/ez-tree-1.1.0.tgz | LICENSE, package.json, README, src/lib (tree.js, options.js, enums.js, textures.js, presets) | P | MIT (code); textures unstated |
| three.js 0.186.1, npm package | https://registry.npmjs.org/three/-/three-0.186.1.tgz | generators/ (Tree, Forest, city/Person, StreetTree), AnimationAction.js, SkeletonUtils.js, audio/, FBXLoader.js header | P | MIT |
| The app's three.js bundle and build | runtime/three/0.186.1, tools/three/build_three.mjs | exported names | P | MIT |
| Weber and Penn, Creation and Rendering of Realistic Trees, SIGGRAPH '95, 119-128 | https://courses.cs.duke.edu/fall02/cps124/resources/p119-weber.pdf | Shape table, wind sway, degradation at range | S (course copy) | ACM copyright; method only |
| Prusinkiewicz and Lindenmayer, The Algorithmic Beauty of Plants (electronic edition 2004) | http://algorithmicbotany.org/papers/abop/abop.pdf | front matter, method | P | all rights reserved; method only |
| Runions, Lane and Prusinkiewicz, Modeling Trees with a Space Colonization Algorithm (2007) | http://algorithmicbotany.org/papers/colonization.egwnp2007.pdf | sections 1-3 | P | method only |
| Zioma, GPU-Generated Procedural Wind Animations for Trees, GPU Gems 3 ch. 6 | https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-6-gpu-generated-procedural-wind-animations-trees | 6.1-6.3 | P | method only |
| Pelzer, Rendering Countless Blades of Waving Grass, GPU Gems ch. 7 | https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-7-rendering-countless-blades-waving-grass | 7.1-7.4 | P | method only |
| McPherson, van Doorn and Peper, Urban Tree Database, RDS-2016-0005 | https://www.fs.usda.gov/rds/archive/catalog/RDS-2016-0005 | the abstract on equations | P | public domain |
| Quaternius FAQ, QAL v1.0, pack pages | https://quaternius.com/faq.html, /license.html, /packs/*.html | licences per pack | P | CC0 or QAL |
| Kenney support and asset pages | https://kenney.nl/support, /assets/car-kit, /assets/city-kit-commercial, /assets/nature-kit, /assets/animated-characters-1 | licence statements | P | CC0 |
| MakeHuman LICENSE.md | https://raw.githubusercontent.com/makehumancommunity/makehuman/master/LICENSE.md | all | P | AGPL code, CC0 assets |
| Mixamo licensing FAQ (Adobe community copy) | https://community.adobe.com/questions-696/mixamo-faq-licensing-royalties-ownership-eula-and-tos-589400 | the distribution table | S | Adobe terms |
| Mixamo FAQ (official) | https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html | refused (403) | not read | |
| TechCrunch, Netflix acquires Ready Player Me (19 December 2025) | https://techcrunch.com/2025/12/19/netflix-acquires-gaming-avatar-maker-ready-player-me/ | the wind-down date, through the fetch tool | S | |
| Poly Haven licence | https://polyhaven.com/license | all | P | CC0 |
| glTF-Sample-Assets README and model READMEs | https://github.com/KhronosGroup/glTF-Sample-Assets | licence lines for Fox, CesiumMan, RiggedFigure | P | per model, mostly CC BY 4.0 |
| three.js RobotExpressive README and example .glb files (r186) | https://github.com/mrdoob/three.js/tree/r186/examples/models/gltf | parsed as data | P | RobotExpressive CC0; others unstated |
| glTF 2.0 specification source | https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc | Skins, morph targets, materials, vertex attributes | P | Khronos |
| EXT_mesh_gpu_instancing | https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Vendor/EXT_mesh_gpu_instancing | overview | P | Khronos |
| Wavefront OBJ (Paul Bourke's copy) | http://paulbourke.net/dataformats/obj/ | statements | S | |
| Blender manual, FBX | https://docs.blender.org/manual/en/4.2/addons/import_export/scene_fbx.html | usage | S | |
| Web Audio API 1.1, editor's draft (17 November 2026); W3C Recommendation 17 June 2021 | https://webaudio.github.io/web-audio-api/ | PannerNode, DistanceModelType, AudioContext "allowed to start" | P | W3C |
| Chrome autoplay policy | https://developer.chrome.com/blog/autoplay | Web Audio section | P | |
| MDN, Autoplay guide for media and Web Audio APIs | https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay | Web Audio, getAutoplayPolicy | P | CC BY-SA (text) |
| Freesound FAQ | https://freesound.org/help/faq/ | licences | P | |
| CC0 1.0 legal code | https://creativecommons.org/publicdomain/zero/1.0/legalcode.en | sections 2-4 | P | |
| Farnell, Designing Sound (MIT Press, 2010) | | not read | U | |
