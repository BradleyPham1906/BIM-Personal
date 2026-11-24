# The world's look: live weather and sky, a living world drawn efficiently, and its assets and sound

Research 2026-11-24, under `research-protocol.md`, for the World Engine (`plan-world-physics.md`). The owner asked
(2026-11-24): "what about the weather, if we could feed real live data ... the sky image changed according to the
weather just like in real life, but in an efficient mode ... do we actually need Unreal Engine ... and what about the
assets like people, tree, plants: should it be objs or generative algo". A broad question with independent sides, so
three research agents worked in parallel (the protocol, step 10), each writing a side note with its own hypotheses,
search log, experiments, alternatives, edges, risks and references; this note is written from them and checked like
any other source.

| Side note | Topic | Experiments |
|---|---|---|
| `research-world-look/weather-sky.md` | Live weather data; how games blend weather; sky, clouds, rain, snow, fog, wet surfaces, wind | `experiments/world-look/ws-*` |
| `research-world-look/rendering-efficiency.md` | Instancing, levels of detail, impostors, culling, texture compression, crowds | `experiments/world-look/re-*` |
| `research-world-look/assets-audio.md` | Trees and plants, people and animation, vehicles, formats, sound | `experiments/world-look/as-*` |
| `research-world-look/independent-check.md` | The second reader's re-check of every fact the code or the decisions rely on | (re-runs) |

## 1. Abstract

**Question.** How can the World BIM show the real weather at the site, live and cheaply; draw a neighbourhood that is
alive (forests, crowds, traffic) at 60 fps on a desktop and 30 on a phone; and fill it with trees, people, vehicles and
sound that may lawfully ship in a public repository, all inside the app's contract (a browser, offline, ES5, pinned
libraries behind adapters)?

**Answer.** None of it needs Unreal Engine: its web export is gone, and the sky technique it uses (Hillaire 2020) is a
published method that runs on an iPhone 6s. What the app lacks is a handful of systems, not an engine:

- **Weather:** one keyless request per site per hour (Open-Meteo, CORS open; MET Norway as the fallback), kept with the
  project for offline use, turned into a small *WeatherState* (cloud layers, fog from visibility by the WMO's
  definition, precipitation kind and intensity, wind, wetness) and blended toward it frame-rate independently, as games
  blend their weather types. Weather models update every 1 to 6 hours, so polling more often gains nothing.
- **Sky:** three.js r186's own `Sky.js` (MIT; the release the app vendors, but not in its bundle) with its built-in
  cloud layer first; Hillaire's lookup-table atmosphere as the quality step; volumetric clouds on desktops only.
  Moving weather (rain, snow, lightning, drifting cloud) is drawn as an overlay, because the rendered view averages
  passes and restarts on any change.
- **Efficiency:** GPU instancing first (measured: 100,000 trees in 1.6 MB instead of 218 MB; issuing 100,000 separate
  draws costs 23 to 28 ms of main-thread time a frame, one instanced draw under 0.1 ms), in the app's own renderer
  through the WebGL 1 extension it can already use, so picking and selection keep working; then levels of detail and
  impostors; crowds as instances animated from a texture; compressed textures when textured assets arrive.
- **Assets:** trees generated in the app (our own ES5 code from Weber and Penn's published method, fed by the Urban
  Tree Database the app already holds; a near tree is about 14,000 triangles, so levels of detail are required); people
  authored, not generated (one CC0 rigged glTF family driven by three.js's AnimationMixer from the existing walkers);
  vehicles and street furniture from CC0 glTF kits; glTF as the one format, never OBJ.
- **Sound:** the Web Audio API through three.js's PositionalAudio, started by the user, with rain and wind synthesised
  from noise and footsteps, engines and birds from CC0 recordings.

**Recommendation.** Twelve phases, V301 to V312 (part 5), inserted in the plan's Stages C, E and F; and the owner's
sixteen decisions in part 11.

## 2. The question and the hypotheses

Each side note states its own hypotheses and their outcomes (weather-sky H1 to H9, rendering-efficiency H1 to H9,
assets-audio H1 to H12). The ones that decide the plan:

| # | Hypothesis | Outcome | Where |
|---|---|---|---|
| W-H1 | A keyless live source always answers a browser | **Partly failed**: Open-Meteo's CORS is open, but its free API is non-commercial and limited to 10,000 calls a day per IP; this machine's shared IP was refused (429) | weather-sky 4.1 |
| W-H2 | At least two other keyless, CORS-open sources exist | **Held**: MET Norway (global), the US National Weather Service, Bright Sky (Germany); aviationweather.gov sends no CORS header and is named, not proxied | weather-sky 4.1 |
| W-H3 | Polling more often than hourly gains nothing | **Held**: ten models update every 1 to 6 hours | weather-sky 4.6 |
| W-H5 | A lookup-table sky costs about as little as today's gradient dome | **Held** (software rendering; Hillaire's own figure about 1 ms on an iPhone 6s) | weather-sky 4.4 |
| W-H6 | Volumetric clouds run at 60 fps on a phone | **Failed**: 36 to 53 fps on an iPhone 13 at the lowest quality (takram) | weather-sky 4.5 |
| W-H9 | Weather fits the rendered view unchanged | **Failed**: it accumulates passes and restarts on change; moving weather must be an overlay | weather-sky 8 |
| R-H1 | Instanced submission costs about the same at any count | **Held** | rendering 6 |
| R-H2 | Instanced draws are as fast as merged geometry on the GPU | **Failed here** (SwiftShader, software); real GPUs differ by report; to settle on a phone | rendering 6 |
| R-H9 | Instancing needs WebGL 2 | **Failed**: the app's WebGL 1 context has `ANGLE_instanced_arrays` | rendering 4.1 |
| A-H2 | A near tree fits in 20,000 triangles | **Held** for 14 of 16 EZ-Tree presets (mean 13,960); 1,000 of them would be 14 million, so levels of detail are required | assets 6.1 |
| A-H3 | EZ-Tree can be vendored unchanged | **Failed**: its code is MIT but its build inlines 20 textures of unstated origin | assets 4.1 |
| A-H5 | Shippable rigged humans exist | **Held** for CC0 families; **failed** for Mixamo (raw files may not be redistributed) and Ready Player Me (shut down) | assets 4.4 |

## 3. Method

Three research agents, one per side, each following the protocol: primary sources read and licences read at the
source, a search log, at least three independent sources per topic, a deliberate search for counter-evidence, and
experiments run here (Node; headless Chromium 158 with SwiftShader, so GPU timings rank methods but do not predict a
phone). Their side notes carry the full search logs (weather-sky 3, rendering 3, assets 3). Hosts that refused:
developer.arm.com (403; Arm's PDFs read instead), shaderbits.com (404), Qualcomm's Adreno guide (needs script);
aviationweather.gov refuses a browser (no CORS header). Open-Meteo refused this machine with 429 (a shared cloud IP),
after one 200 in Chromium.

### 3.1 The independent check

A separate agent re-read the source of every fact the code or the decisions rely on, across the three side notes, and
re-ran one decisive experiment from each: `research-world-look/independent-check.md`. Its outcome is recorded here
once it is complete.

## 4. Findings, by topic (summaries; evidence and levels in the side notes)

### 4.1 How games do it, and whether we need their engine

Games keep code generic and content as data: GTA V's weather "look" lives in per-weather timecycle files that modders
edit and blend (level S, modding documentation), the same idea as the app's standards registry. The techniques the
owner saw (a sky that matches the weather, blended transitions, rain near the camera, wet streets, swaying trees,
crowds and traffic) are published and portable to WebGL and WebGPU. Unreal Engine no longer exports to the web
(HTML5 left the engine around 4.24; level U, from memory, not needed by any decision), and streaming it would need a
GPU server per user, against the app's offline, one-file and phone contract.

### 4.2 Live weather (weather-sky 4.1 to 4.3, 4.6)

Open-Meteo: keyless, `access-control-allow-origin: *`, CC BY 4.0 with a credit link, free for non-commercial use only,
10,000 calls a day, 5,000 an hour, 600 a minute per IP. MET Norway Locationforecast: global, CC BY 4.0 and NLOD, a
shared limit of 20 requests a second for all users. NWS: the US only. Models update every 1 to 6 hours and publish
1.5 to 7.5 hours after each run, so one request per site per hour, at a random minute, only while the rendered view is
open and visible, is enough; `timeformat=unixtime` avoids daylight-saving and fractional time-zone traps; the answer is
kept with the project. The mapping to a WeatherState uses the WMO's definition of visibility (fog extinction
ln(20)/visibility) and the WMO 4677 weather codes; model visibility is itself weak data (an open Open-Meteo issue). A
visibility of 0 is dense fog, not missing data (an edge the experiment caught). Blending by an exponential rule gave
the same 0.950213 at 30, 60 and 120 fps.

### 4.3 Sky and weather rendering (weather-sky 4.4, 4.5)

`Sky.js` (three.js r186, MIT): an analytic Preetham-form sky with a 2D cloud layer whose coverage and density are
uniforms; about four to five times the gradient dome's cost per pixel in software rendering. Hillaire 2020: a few small
lookup tables, the atmosphere changeable for weather without heavy updates, about 1 ms on an iPhone 6s by its author's
figures; used by Unreal. Volumetric clouds: desktop only. Fog: today every model material in the rendered view sets
`fog: false`; turning fog on in weather mode is a material change. Wet surfaces: darker and smoother by Lagarde's
rule, by surface kind. Rain and snow: GPU particles near the camera in an overlay, capped per device class.

### 4.4 Drawing a living world efficiently (rendering 4.1 to 4.5, 6)

The app's renderer merges every object into 64 m chunks; there is no instancing, no render level of detail and no
impostor anywhere in the engine. Measured (software rendering, two runs each, a 26-triangle tree):

| Copies | One draw each | Merged | Instanced |
|---|---|---|---|
| 1,000 | 22 to 31 ms a frame | 8 to 14 ms | 23 to 26 ms |
| 100,000 | 1.6 to 2.0 s | 0.44 to 0.61 s | 1.5 to 2.0 s |

On the main thread, 100,000 separate draws take 23.4 to 27.6 ms a frame, more than a whole 16.7 ms frame; one instanced
or merged draw stays below 0.1 ms. Memory at 100,000: 1.6 MB instanced, 218 MB merged; moving every copy each frame
re-sends 1.6 MB against 93.6 MB; setting up takes 1.1 to 1.5 ms against 328 to 394 ms. So instancing wins on the main
thread, in memory and for anything that moves; merged geometry is faster in software rendering, which a phone must
settle. The vendored three.js already has `InstancedMesh`, `BatchedMesh`, `LOD`, `SkinnedMesh` and the meshopt
decoder; not a KTX2 loader or a simplifier. Arm's guidance for OpenGL ES: fewer than 500 draw calls a frame. Occlusion
query answers arrive two frames later, so occlusion culling comes last.

### 4.5 Assets (assets 4.1 to 4.6, 6)

Trees: generated, from the Weber and Penn method (EZ-Tree and three.js's TreeGenerator implement its family; three's
generators need its WebGPU and node-material build, which the app's bundle does not have), written as our own ES5 code,
sized from the Urban Tree Database's fields; growth over years needs the database's age equations (archive found, not
yet read). About 27 tree shapes (9 kinds by 3 seeds), each at three levels (about 14,000 and 3,500 triangles, then an
impostor), drawn as instances; leaf-on and leaf-off from the app's existing growing season; wind in the vertex shader
(GPU Gems 3, chapter 6). Grass as instanced crossed cards. People: authored; CC0 rigged glTF characters (Quaternius's
Universal Base Characters with the Universal Animation Library, or Kenney's), driven by AnimationMixer from the walkers'
position, heading and speed (`W.x`, `W.z`, `W.px`, `W.pz`, `W.v`), the clip rate matched to speed so feet do not slide;
only the nearest few dozen animated, the rest instanced poses (walker pools reach 3,000). `SkeletonUtils` (to clone a
skinned character) is not in the bundle. Format: glTF 2.0 (skins, animation, PBR materials, hierarchy, compression);
OBJ has none of these.

### 4.6 Sound (assets 4.7, 6.5)

The Web Audio API through three.js's `PositionalAudio` (in the bundle); 32 HRTF-panned sources rendered at about 3.6
times real time on this machine; the inverse distance model measured at -6.02 dB per doubling; an AudioContext may
start suspended until a user gesture (the specification and Chrome's policy; headless Chromium here starts it running,
so not testable here). Rain and wind synthesised from filtered noise; footsteps, engines and birds from CC0 recordings.

## 5. The alternatives compared, and the phases they lead to

The side notes compare the alternatives against criteria stated first (weather-sky 5, rendering 5, assets 5). Their
recommendations become these phases, each needing its own work orders (and, where marked, a short library research
first):

| Phase | What | Stage in the plan | Depends on |
|---|---|---|---|
| V301 | Instance batches in the app's renderer (`render/gpu-instances.js`; WebGL 1 extension and WebGPU instance step), picking and selection through the slot table, culling by cell | C, first | V277a |
| V302 | Levels of detail by projected size with hysteresis; impostors (billboards for people, octahedral for trees) | C | V301 |
| V303 | Walkers and cars as instances animated from a texture (from `traffic-draw.js`'s canvas fills) | C / F | V301, V309 |
| V304 | Live weather: the fetch, cache and fallback chain, the WeatherState and its blending (pure, unit-tested) | E | none |
| V305 | The sky: `Sky.js` in the bundle driven by the WeatherState; fog on materials in weather mode; wet surfaces | E | V304 |
| V306 | Moving weather as an overlay: rain, snow, lightning; wind sway | E | V305, V308 |
| V307 | Hillaire's lookup-table atmosphere (the quality step) | E | V305 |
| V308 | Generated trees: our own ES5 Weber and Penn generator from the Urban Tree Database, three levels, leaf-on and off, growth by age | F | V301, V302 |
| V309 | People: one CC0 rigged glTF family under `runtime/`, AnimationMixer from the walkers, `SkeletonUtils` in the bundle | F | V301 |
| V310 | Vehicles and street furniture: CC0 glTF kits; cars driven by V208's Jolt vehicle | F | V301, V208 |
| V311 | Sound: Web Audio, synthesised rain and wind, CC0 recordings, a Sound control | F | V304, V309 |
| V312 | Compressed textures (KTX2 and Basis Universal), after its library research | C | textured assets |

## 6. The experiments

`experiments/world-look/`: weather (`ws-*`: the endpoints with CORS and preflight, Open-Meteo's full answer, the
WeatherState mapping and blending, a sky shader timing), rendering (`re-*`: the instancing page and its runners, the
capability probe), assets (`as-*`: tree triangle counts from EZ-Tree's and three's generators, rigged glTF statistics
and root motion, Web Audio). Raw results beside each script; numbers summarised in part 4.

## 7. Edges

From the side notes: a visibility of 0 is dense fog; daylight saving and fractional time zones (use Unix time); a 429
with `Retry-After`; a site outside every regional model; instanced picking past 65,535 slots; an impostor seen from
straight above; a tree's 16-bit indices; a walker standing still (no foot sliding at speed 0); an AudioContext started
before a gesture; a saved picture taken while it rains (the overlay is not in it unless asked).

## 8. What the app already has

Open-Meteo calls for the climate archive and air quality (`site-analysis/climate-data.js` lines 21 to 22); four sky
presets and a night sky as colour rows (`render/rendered-core.js` lines 23 to 30); the exact sun (`site/sun-position.js`);
trees as a six-sided trunk and a 20-face crown sized from the Urban Tree Database (`assets/scale-assets.js` line 126);
leaves by date for shadows (`site/shadows.js`); walkers and traffic drawn in canvas 2D (`simulation/traffic-draw.js`);
glTF import (`assets/gltf-assets.js`, `io/gltf.js`); Draco in the vendored three.js; no instancing, render LOD,
impostors, skeletal animation (but the XR hand) or audio anywhere in the engine (survey, 2026-11-24).

## 9. Risks and threats to validity

Every GPU number is software rendering; a phone may reverse the merged-against-instanced ranking (R-H2) and decides
the animated-crowd budget (R-H8). Open-Meteo's non-commercial terms may not fit a future paid app. Model visibility is
weak data, so fog from it will sometimes be wrong. Licences of asset packs change (Ready Player Me closed in 2026);
each asset is pinned with its licence file and hash.

## 10. What is still open (U), and why

A phone's numbers (no phone here); the Urban Tree Database's growth equations (archive found, not read); the CLT and
species texture sources; whether the owner's deployment is non-commercial (a decision, W1).

## 11. The owner's decisions

Asked together, each with its recommendation.

**Weather and sky**
1. **W1 Commercial status.** Open-Meteo's free API is for non-commercial use. Treat the app as non-commercial while it
   has no subscriptions or advertising, and revisit (a paid plan, a self-hosted Open-Meteo, or MET Norway alone) if
   that changes. Recommended: yes.
2. **W2 Consent.** Ask once per project before sending the site's coordinates to a weather service. Recommended: yes.
3. **W3 Which weather.** Live weather when the view's time is now; the forecast for the coming days; the archive
   (already used) for a past date; the chosen preset otherwise. Recommended: yes.
4. **W4 The sky.** Add `Sky.js` to the vendored three.js bundle now; research Hillaire's atmosphere as the quality step.
   Recommended: yes.
5. **W5 Moving weather.** Rain, snow and lightning as an overlay, left out of saved pictures unless asked.
   Recommended: yes.
6. **W6 Fallback order.** Open-Meteo, then MET Norway, then the cached answer, then climate normals, then the preset.
   Recommended: yes.
7. **W7 Credits.** "Weather data by Open-Meteo.com" and "Data from MET Norway", with links, whenever live weather is on.
   Recommended: yes.

**Rendering**
8. **R1 Where first.** The living world is drawn first in the app's own renderer (picking and layers keep working),
   then in the rendered view. Recommended: yes.
9. **R2 Selection.** Every placed tree and person keeps its own table row (selectable one by one, 32 bytes each);
   generated forests and crowds are one element each. Recommended: yes.
10. **R3 Libraries to research later.** meshoptimizer's simplifier (MIT) for levels of detail; the Basis transcoder
    (Apache-2.0) with `ktx-parse` and `zstddec` (MIT) for compressed textures; each researched and approved before use.
    Recommended: yes, research only.
11. **R4 A phone check.** Run the standalone page `experiments/world-look/re-instancing.html` once on your phone, to
    settle how a real GPU ranks instanced against merged drawing. Recommended: yes, when convenient.

**Assets and sound**
12. **A1 Trees.** Our own ES5 generator from the published method, fed by the Urban Tree Database. Recommended: yes.
13. **A2 People.** One CC0 rigged character family and its clips pinned under `runtime/` (Quaternius's Universal set
    first, Kenney's as the alternative). Recommended: yes.
14. **A3 Licences of assets.** CC0 by default; CC BY 4.0 allowed with its credit shipped, where no CC0 equal exists
    (the owner's standing rule: free and credited). Recommended: yes.
15. **A4 Sound.** Off until the user turns it on with a Sound control (browsers require a gesture; no surprise noise).
    Recommended: yes.
16. **A5 `SkeletonUtils`.** Add it to the vendored three.js bundle (one export line) for cloning characters.
    Recommended: yes.

## 12. References

Each side note's part 12 or 13 lists its sources with URLs, what was read, the date and the level (weather-sky 13,
rendering 13, assets 12). The principal ones: Open-Meteo's documentation and terms; MET Norway's API terms; the
National Weather Service API documentation; WMO-No. 8 (visibility); WMO code table 4677; Hillaire, *A Scalable and
Production Ready Sky and Atmosphere Rendering Technique* (Computer Graphics Forum 39(4), 2020); Preetham, Shirley and
Smits (1999); three.js r186 source (MIT); the WebGL and WebGPU specifications and MDN's compatibility data; Arm's Mali
best-practice guide; Weber and Penn, *Creation and Rendering of Realistic Trees* (SIGGRAPH 1995); Runions et al. (2007);
GPU Gems 3, chapters 2 and 6; EZ-Tree (MIT); Quaternius and Kenney (CC0); Mixamo's and Ready Player Me's terms; the glTF
2.0 specification; the Web Audio API (W3C Recommendation) and Chrome's autoplay policy.
