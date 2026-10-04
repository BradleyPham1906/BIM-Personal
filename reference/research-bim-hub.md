# The BIM Hub: "GitHub for the built world"

The owner's brief (2026-10-04), from their notes and a conversation with Gemini, in our words, and
what it means for this app. PIPELINE.md carries the phases: H1 and H2 after V145; H3 to H5 and the
rendering, streaming and simulation items under "later".

## 1. The brief

- **The vision.** A web-based, version-controlled hub for building data. Governments, firms and
  individuals keep one model of the built world and refine it together, instead of rebuilding
  separate models in separate programs.
- **The problem.** Vendor lock-in (Revit, Rhino, AutoCAD, SketchUp); the industry's IP and legal
  exposure.
- **Open standards.** IFC as the native format, read, edited and computed on in the browser.
- **Git per element.** History, branches, merges and pull requests at the level of building
  elements (by their IDs), not whole uploaded files.
- **IP controls.** Per-component privacy, paywalls and an audit trail that cannot be changed. Third
  parties can still run clash and compliance checks on hidden components.
- **Streaming.** A spatial index in the manner of 3D Tiles, so phones and desktops alike load what
  is in view.
- **Rendering.** Three.js on WebGL and WebGPU.
- **Simulation.** Structural FEA, thermal, CFD, on WebGPU compute and WebAssembly in the browser.

## 2. Sources the owner pointed to

- **Figma, "Figma rendering: powered by WebGPU"** (figma.com/blog). Figma moved its renderer to
  WebGPU behind one graphics layer that also runs on WebGL, falling back to WebGL where WebGPU is
  missing or fails. The lesson for us: one rendering interface with two back ends, not a fork. The
  page could not be fetched from this environment; this summary is from what we know of the post.
- **Evan Wallace, WebGL Water** (madebyevan.com) and his write-up on real-time caustics:
  - a heightfield water simulation;
  - raytraced reflections and refractions;
  - analytic ambient occlusion;
  - soft shadows;
  - caustics.

  These are techniques to reimplement ourselves, for V143's ponds, flooding and F7's rendering.
- **ACM, doi 10.1145/3507909.** Not reachable from this environment (dl.acm.org is blocked). To be
  read and summarised here when the owner pastes its title or abstract.

## 3. What fits this app, and what does not

| Pillar | Today | Path |
|---|---|---|
| Git per element | Every object has a stable ID; the project is JSON | H1 history and diff, H2 branches and merge, all in the app |
| Native IFC | IFC export and a partial reader | H3: web-ifc (WebAssembly, MPL-2.0); keep IFC GUIDs so diffs are IFC diffs |
| Sharing | Single file, offline, GitHub Pages | H4: push and pull history to a git repository, one file per element |
| Permissions, paywalls, audit | None; there is no server | H5: needs accounts and a backend |
| Streaming | CityJSON, LOD track | OGC 3D Tiles out and in, after the LOD track |
| WebGPU | Our own WebGL renderer, not Three.js | One rendering layer, WebGPU and WebGL back ends, when performance asks for it |
| Simulation | Solar, sun hours, rain (V143); a structural frame (V125) | A frame solver (stiffness method); wind by lattice Boltzmann on the GPU |

**A correction to the brief: checks on hidden geometry.** What runs in a viewer's browser can be
read there. That holds for WebGPU compute, WebAssembly, or anything else. So a clash or code check
on a hidden component cannot run on the viewer's machine. It runs on a server the owner of the
component trusts, and only the result goes back ("clash at grid C-4", "complies"). Zero-knowledge
proofs over geometry are research, not something to build on.

## 4. The order

1. **V146 H1 element history:**
   - commits with a message;
   - a change log;
   - a diff by element ID: added, removed, and changed property by property;
   - restore any version;
   - saved with the project.
2. **V147 H2 branches and merge:**
   - design options as branches, compared by their numbers;
   - a three-way merge per element, with conflicts shown side by side.

   Replaces the planned "design scenarios" phase.
3. **Later:** H3 full IFC, H4 share and sync, H5 the server, then streaming, WebGPU, water and
   presentation rendering, and structural and wind analysis.
