# The World Engine: a plan for simulating the real world in World BIM

Status: plan, for the owner's decisions (part 10). Written 2026-11-23 after the math evaluation of the same day.
Phase numbers below are proposals (V277 on, after the last number in use, V276); each phase still needs its own
research note under `docs/research/research-protocol.md` before work orders are written.

## 1. The vision

**World BIM is a model of a place that behaves like the place.** Every element the app holds, from a bolt to a
city block, is a physical object: it has a shape, a material, a mass, and it obeys the same laws as the real one.
Drop a beam and it falls. Load a floor and it deflects. Shake the ground and the building sways by the amount the
codes predict. Rain on the site and the water runs where the ground sends it. Walk, drive or fly through the
project and the world answers the way the real one would.

Open-world games such as the GTA series show how convincing a living world can be on ordinary hardware: cars with
suspension, people who walk around each other, water you can swim in, a city that streams around the player. They
get there by being *plausible*. World BIM has to go one step further and be *right*: a designer will build from
its answers. The plan rests on that difference.

### Two fidelities, one world

| | Play fidelity (what games do) | Engineering fidelity (what codes demand) |
|---|---|---|
| Question | Does it look and feel real? | Is the number right, to a stated tolerance? |
| Time | Real time, 60 frames a second, fixed steps | As long as it takes; results cached |
| Method | Rigid bodies, contacts, impulses (Jolt) | Stiffness, finite elements, validated integrators |
| Checked against | The eye, and experiments like W1's curb test | Closed-form solutions, published benchmarks, the codes |
| Example | A pallet of bricks tips off a slab edge | The slab edge's moment and deflection under the pallet |

Both read the same model and the same math core. A phase may build either fidelity, but never a second copy of
the math. The world test in part 1.2 needs both, side by side.

### 1.1 The end goal

A project in World BIM can be opened as a **live world**: the building, its site and its neighbourhood, at a date
and time, under a weather, with people and vehicles, all moving under one clock. In it, the user can:

1. pick up, drop, push and stack any element, and see it fall, slide, tip and rest with its true mass and friction;
2. walk, drive, fly and swim (V203 to V211), with vehicles that steer and brake on the real ground and slopes;
3. switch any part of what they see to its engineering answer: forces, stresses, deflections, flows, temperatures,
   light levels, noise, each with its method, standard and edition named;
4. run an event (an earthquake record, a storm, a flood, a rush hour, a fire evacuation) and watch it play out in
   the world, the engineering numbers running alongside;
5. save the world's state, replay it exactly, and share it.

### 1.2 The world test (how we know we are there)

The plan is done when one demonstration project passes all of these, on a desktop browser at 60 frames a second
and on a phone at 30, offline:

| # | Scenario | Pass when |
|---|---|---|
| T1 | A 1 m concrete cube dropped from 2 m | Lands at 0.64 s (sqrt(2h/g)), its mass is 2,400 kg, it rests without jitter |
| T2 | A tilted box on a 20 degree ramp, friction 0.3, then 0.5 | Slides at 0.3 (tan 20 = 0.36), holds at 0.5 |
| T3 | A five-storey steel frame under a recorded ground motion | Real-time sway matches V245's Newmark result to 5% at the roof |
| T4 | A car through the site at 30 km/h | Brakes to a stop in the distance its tyre friction predicts, climbs the ramp, not the kerb |
| T5 | 1,000 people evacuate a floor | Flow through each door within the published range for its width |
| T6 | A 10-year storm on the site | Ponding where V247's runoff puts it; the swimmer floats in it |
| T7 | Wind across the block | Velocity field matches V221's lattice Boltzmann reference on its benchmark |
| T8 | Noon on 21 June, then 21 December | Shadows and sun on the facade match the NOAA position (already true, V107) |
| T9 | Save, reload, replay | The same run, bit for bit, twice |

## 2. Where we are (from the evaluation of 2026-11-23)

Built: a 3D frame solve (banded Cholesky, RCM), a damped Gauss-Newton constraint solver, NURBS curves and surface
tools, polygon booleans and the OpenCASCADE kernel, Delaunay terrain with cut and fill, rays with a bounding volume
hierarchy, the sun's position, UTM, the Intelligent Driver Model for traffic, pipe friction, and Jolt Physics
moving one walker against a static model.

Researched and queued, files present but empty: V219 to V221 (GPU reference, water waves, wind), V239 to V248
(loads, modes, member checks, time history, form-finding, runoff, ground shape).

Missing, and no phase covers it:

1. a shared vector, matrix and quaternion module (each feature carries its own; `cross()` exists three times);
2. full 3D orientation of elements (rotation is about the vertical axis only, `editing/precision-editing.js:35`);
3. mass properties: volume, centre of mass and inertia tensor of a solid;
4. physical material data used by a simulation: density, friction, restitution, thermal and acoustic values;
5. dynamic bodies: Jolt holds the model as one static mesh;
6. a world clock: one fixed-step loop that every simulation runs under, with save and replay;
7. shared numerical tools: quadrature, ODE integrators, sparse solvers, field operators;
8. whole domains: heat, acoustics, smoke, soil, crowds by pressure, and any coupling between domains.

## 3. Principles

1. **One math core.** Every phase uses `core/math` (part 5, stage A). No feature writes its own `cross()` again.
2. **Pure functions first.** Each method is a pure function with its reference tests before it touches the page,
   as the work orders already require. That is what lets Cline build it and the gate check it.
3. **Verified, not plausible.** Every solver is checked against a closed-form answer or a published benchmark,
   named in its research note, before it is wired in (part 7).
4. **SI units inside, always.** Metres, kilograms, seconds, newtons, kelvin. Display units are a layer on top.
5. **Values are data.** Gravity, densities, friction, code coefficients live in the standards registry (V167)
   with their sources and editions, not in code.
6. **Libraries behind adapters.** Jolt for real-time contact (already vendored), OpenCASCADE for exact solids.
   New ones only under the third-party rule, researched and approved once.
7. **Scales by level of detail.** Like an open-world game, simulate fully only near the viewer or the question;
   further away, cheaper models or none (part 6).
8. **Deterministic.** Fixed time step, seeded randomness, ordered updates, so a run replays exactly (T9).
9. **Every device.** The phone gets the same world with fewer bodies and coarser grids, never a different one.

## 4. The mathematics, layer by layer

What the world needs, from the bottom up. Status: **Have**, **Part** (exists in one feature only, or a limited
form), **Queued** (a phase exists), **New** (in this plan).

### L0 Numbers

| Topic | Used for | Status |
|---|---|---|
| Floating point care: tolerances, robust predicates (orientation, in-circle) | Booleans, Delaunay, contact that never fails on a near-degenerate case | Part (terrain) |
| Units and dimensional checks | Every physical value | New |
| Seeded random numbers, distributions (normal, Poisson, Weibull) | Crowds, traffic arrivals, wind gusts, replay | Part (traffic) |
| Interval and error bounds | Saying how sure a result is | New |

### L1 Linear algebra and geometry

| Topic | Used for | Status |
|---|---|---|
| Vectors, 3x3 and 4x4 matrices, quaternions, slerp | Orientation of every element, cameras, joints | New (render and three.js only) |
| Rigid transforms, Euler angles both ways, axis-angle, R Rt = I and det R = 1 checks | 3D rotate and tilt; IFC and glTF placement | New |
| Dense solves: LU, Cholesky, QR | Small systems everywhere | Part (three separate copies) |
| Sparse matrices, sparse Cholesky, conjugate gradient with a preconditioner | Finite elements, heat, pressure, large frames | New |
| Eigenvalues: Jacobi, then subspace iteration and Lanczos | Modes (V242), principal axes of inertia, plane fits | Queued / Part |
| Least squares, SVD, PCA | Fitting surfaces to scans, registration of point clouds | Part (LiDAR roofs) |
| Polygon and mesh geometry: areas, Newell normals, half-edge meshes, booleans | Everything modelled | Have / Part |
| Curves and surfaces: NURBS, subdivision | Freeform | Have (curves) / Queued |
| Spatial indexes: BVH, uniform grid, octree | Ray casts, contact broadphase, neighbour search | Part (rays only) |
| Convex hulls, GJK and EPA, separating axes, convex decomposition | Contact between solids (inside Jolt), turning BIM solids into physics shapes | New |

### L2 Calculus and numerics

| Topic | Used for | Status |
|---|---|---|
| Quadrature: Gauss-Legendre, triangle and tetrahedron rules | Element stiffness, loads over areas, energies | New |
| Divergence theorem on a closed mesh (the third screenshot) | Exact volume, centre of mass and inertia from the triangles alone | New |
| Change of variables, Jacobians (the cylindrical r of the first screenshot) | Integrals over curved elements, finite element mapping | New |
| Gradient, divergence, curl, Laplacian on grids and meshes | Runoff, heat, pressure, wind, curvature of ground and surfaces | Part (V248 queued) |
| ODE integrators: semi-implicit Euler, Verlet, RK4, Newmark, generalized-alpha | Particles, cables, structures in time, vehicles | Part (Newmark queued) |
| Root finding and optimisation: Newton, Levenberg-Marquardt, line search | Constraints, form-finding, sizing | Have (sketch) |
| Constrained optimisation: projected Gauss-Seidel, linear complementarity | Contact and friction (inside Jolt), joints | New (via Jolt) |
| Interpolation and splines in time | Smooth playback, recorded paths, wind profiles | Part |
| Signal processing: FFT, filters, response spectra | Ground motions, vibration, acoustics | Part (V242, V245 queued) |
| Probability and statistics: Monte Carlo, extreme values, fitting | Wind and rain return periods, crowd variation, risk | New |
| Graphs: shortest paths, flows, connectivity | Escape routes, traffic, MEP networks, load paths | Have (several features) |

### L3 Physics domains

| Domain | Play fidelity | Engineering fidelity | Status |
|---|---|---|---|
| Rigid bodies | Jolt dynamic bodies: fall, stack, tip, joints | Statics of the resting state; impact loads | New |
| Structures | Real-time sway from modal superposition | Frame solve, modes, time history, member checks | Have / Queued |
| Continua | Visual deflection | Finite elements: shells for slabs and walls, solids for footings, nonlinear later | New |
| Cables and membranes | Verlet ropes and cloth (Jolt soft bodies) | Form-finding: force density, dynamic relaxation | Queued (V246) |
| Soil and ground | Terrain as collision, settling of loose fill | Bearing capacity, settlement, retaining walls, slope stability | New |
| Water | Heightfield waves, buoyancy | Runoff, ponding, pipe hydraulics | Queued / Part |
| Air | Gusts that sway trees and flags | Wind loads, lattice Boltzmann flow around buildings | Queued |
| Heat | Warm and cold surfaces in false colour | Conduction through assemblies, U-values, thermal mass over a day | New |
| Light | The rendered view, sun and sky | Daylight factor, illuminance (Ladybug, Radiance) | Have |
| Sound | Distance and occlusion in the walkthrough | Reverberation time (Sabine, Eyring), sound insulation between rooms | New |
| Smoke and fire | Visible smoke layer | Zone model of smoke filling, tenability timeline for evacuation | New |
| People | Walkers that steer and avoid | Social force crowd, door flow rates, evacuation times | Part (walkers, routes) |
| Vehicles | Jolt wheeled vehicle | Braking and turning paths, the IDM in traffic | Part (traffic, V208 queued) |
| Climate and sun | Sky, weather in the scene | Weather files, solar gains, comfort | Have |

### L4 The world runtime

| Part | What it does | Status |
|---|---|---|
| World clock | One fixed step (for example 1/60 s), interpolated rendering, pause, speed, rewind | New |
| Systems | Each domain registers its step; order fixed and documented | New |
| Coupling | A domain publishes fields (water depth, wind speed, ground acceleration) others read | New |
| Simulation level of detail | Full near the viewer or the question, simplified further out, asleep beyond | New |
| Streaming | Load and unload world tiles, as the map already does for tiles | Part (map, V218 queued) |
| State and replay | Snapshot and restore every system; record inputs, replay bit for bit | Part (V211 queued, for the walk) |
| Compute back ends | CPU reference first, then a Web Worker, then WebGPU compute | Queued (V219) |

## 5. The roadmap

Seven stages. The order is what the dependencies require. Stages A and B have to come first: every later stage
reads the math core and the physical object. Stages C to F can then run in parallel, and G puts them together.
Phase numbers are proposals; durations are not given, since Cline's pace sets them.

### Stage A: the math core (blocks everything else)

| Phase | What | Pass when |
|---|---|---|
| V277 | `core/math`: vec3, mat3, mat4, quat; transforms, Euler both ways, slerp; robust predicates; units | Identities hold over random cases: R Rt = I, det R = 1, q to R to q; old duplicates replaced |
| V278 | Numerics: dense LU, Cholesky, QR, Jacobi eigen, SVD; Gauss quadrature on lines, triangles, tetrahedra | Against closed forms and LAPACK-computed references stored as data |
| V279 | Sparse matrices, preconditioned conjugate gradient, sparse Cholesky; ODE integrators (semi-implicit Euler, Verlet, RK4, Newmark, generalized-alpha) | A 10,000-unknown Poisson problem solves; each integrator's order of accuracy measured |

### Stage B: the physical object

| Phase | What | Pass when |
|---|---|---|
| V280 | Mass properties from the divergence theorem: volume, centre of mass, inertia tensor, principal axes, for any closed mesh or OpenCASCADE solid | A cube, cylinder, sphere and an L-section to 1e-9 of their formulas; open meshes refused with a reason |
| V281 | Physical materials: density, friction, restitution, E, nu, conductivity, heat capacity, absorption, in the registry with sources | Every material card has them or says which is missing |
| V282 | Full 3D orientation for every element: the model stores a quaternion; the gizmo tilts; IFC and glTF placements kept | Rotate about any axis, save, reload, export: same placement |

### Stage C: the live world (play fidelity)

| Phase | What | Pass when |
|---|---|---|
| V283 | The world clock and systems loop; deterministic stepping; snapshot and restore | T9 for the walker and traffic |
| V284 | Dynamic bodies in Jolt: an element becomes a body with V280's mass and V281's friction; convex hulls or decomposition for its shape; sleeping | T1, T2 |
| V285 | Picking up, throwing and stacking in the walkthrough; joints (hinge, slider, fixed) from the V273 assembly joints | A door swings on its hinge; a stack of ten blocks stands |
| V286 | Simulation level of detail and streaming of physics with map tiles | 5,000 bodies on a desktop at 60 fps, 1,000 on a phone at 30 |

### Stage D: structures, all the way (engineering fidelity)

| Phase | What | Pass when |
|---|---|---|
| V239 to V245 | As queued: loads, modes, member checks, time history | Their own tests |
| V287 | Finite elements, first slice: plate and shell elements for slabs and walls, on Stage A's sparse solver | NAFEMS LE benchmarks for plates to their published tolerance |
| V288 | Solid elements for footings and transfer pieces; soil springs | Benchmarks; a footing on springs against a closed form |
| V289 | The live structure: real-time sway in the world from V242's modes (modal superposition), V245 as the reference | T3 |
| V290 | Geotechnics: bearing capacity, settlement, earth pressure on walls, slope stability (Bishop) | Worked examples from the referenced texts |

### Stage E: fluids, heat, light and sound

| Phase | What | Pass when |
|---|---|---|
| V219 to V221, V247 | As queued: GPU reference, water waves, wind, runoff | Their own tests |
| V291 | Shallow-water flow on the terrain (a finite-volume scheme), coupled to runoff and the swimmer's buoyancy | Dam break against its analytic solution; T6 |
| V292 | Heat: 1D conduction through assemblies, U-values, a day of thermal mass; surfaces in false colour | Against ISO 6946 and a steady-state closed form |
| V293 | Acoustics: room reverberation (Sabine, Eyring) from V281's absorption, sound insulation between rooms | Against worked examples in the standard |
| V294 | Wind in 3D: the D3Q19 lattice on the GPU (after V219), feeding wind loads and swaying trees | T7 |

### Stage F: people and vehicles

| Phase | What | Pass when |
|---|---|---|
| V208 to V211 | As queued: drive, fly, swim, record | Their own tests |
| V295 | A navigation mesh from the model's floors and stairs; path finding for agents | Every reachable room reached; none through a wall |
| V296 | Crowds: social force model, door flows, evacuation timelines | T5 against published flow rates |
| V297 | Vehicles in the traffic sim become Jolt vehicles near the viewer and stay IDM agents far away | T4; traffic counts unchanged by the switch |

### Stage G: coupled events (the world test)

| Phase | What | Pass when |
|---|---|---|
| V298 | Events: an earthquake, a storm, a flood, rush hour, an evacuation, each a script over the world clock | Each runs, saves and replays |
| V299 | Smoke: a two-zone smoke filling model feeding the evacuation's tenability | Against a published zone model example |
| V300 | The demonstration project and the world test T1 to T9 as a browser suite | All nine pass on desktop and phone |

## 6. What open-world games teach, and what we take

| Game technique | What it is | Our use |
|---|---|---|
| Fixed time step, interpolated frames | Physics at a steady 60 Hz whatever the frame rate | The world clock (V283) |
| Broadphase and narrowphase | Cheap boxes first, exact contact only for pairs that may touch | Inside Jolt; our BVH for ray queries |
| Islands and sleeping | Bodies at rest cost nothing until touched | Jolt does it; V286 sets the thresholds |
| Simulation level of detail | Full physics near the player, scripted further away, nothing off screen | V286, V297 |
| World streaming | Load tiles around the player, drop them behind | Map tiles and 3D Tiles (V218) |
| Raycast suspension for cars | Each wheel is a ray and a spring, not a rolling cylinder | Jolt's wheeled vehicle (V208) |
| Navigation meshes and steering | Walkable surfaces as polygons, agents steer and avoid | V295, V296 |
| Deterministic replay | Record inputs, not frames | V211, V283 |
| Convex decomposition | A complex shape as a few convex pieces for contact | V284 |

What we do not take: shortcuts that look right and are wrong. A game may make a car brake harder because it
feels better; ours brakes by its friction. Where play fidelity and engineering disagree, the world shows the
engineering answer and the difference.

## 7. How we get there

1. **The usual pipeline, per phase.** Research under the protocol (question, hypotheses, three sources, a search
   for counter-evidence, experiments in `docs/research/experiments/`), the owner's decisions, then Claude writes
   SPEC, TASKS and tests; Cline builds the pure functions through the gate; Claude wires them in, runs the one
   browser check and audits in batches.
2. **A verification ladder for every solver.** (a) identities and conservation (energy, momentum, mass);
   (b) closed-form cases; (c) published benchmarks (NAFEMS for finite elements, the dam break for shallow water,
   the cylinder's Strouhal number for wind, door flow rates for crowds); (d) a cross-check against an established
   program where its output can be read as data. Each research note names which rungs apply.
3. **Performance budgets.** A desktop frame is 16.7 ms: physics 4 ms, other simulation 4 ms, the rest for
   drawing. A phone frame at 30 fps: physics 6 ms. Each Stage C to F phase measures its cost against its budget.
4. **Background work.** Anything over a frame's budget runs in a Web Worker (as Ladybug does) or on WebGPU, its
   answer cached in the project so the app opens offline with the last result.
5. **The shared core is enforced.** `npm run check` gains a rule: no new vector or matrix helper outside
   `core/math`. Old duplicates are replaced in V277.

## 8. Risks

| Risk | Effect | Response |
|---|---|---|
| Phones cannot carry the full world | T1 to T9 fail at 30 fps | Level of detail from the start (V286); budgets per phase |
| Floating point differs between browsers | Replay drifts (T9) | Determinism promised per browser; Jolt's cross-platform determinism build checked in research |
| Finite elements are a large field | Stage D stalls | Narrow slices with benchmarks; an existing WebAssembly solver considered under the library rule |
| Coupling many domains is fragile | One change breaks another | Domains talk only through published fields on the world clock |
| Play and engineering answers disagree in view | Users trust the wrong one | The engineering answer is shown, with the difference and the method named |
| Scope | The plan outgrows the queue | Stages A and B first; every later stage is optional on its own |

## 9. What this plan is not

It is not a game, and it does not copy any game's content, look or code. It does not ship unverified physics as
engineering. It does not need a server: everything runs in the browser, offline, with pinned libraries.

## 10. The owner's decisions

Asked together, each with a recommendation.

1. **The vision.** Adopt part 1 (two fidelities, one world, the world test T1 to T9) as the goal for this track.
   Recommended: yes.
2. **Order.** Stages A and B start before the rest of the queued physical-world phases are wired in, so V239 to
   V248 are built on `core/math`. Recommended: yes, and V277 to V282 are inserted in the queue after V248.
3. **Orientation.** Elements store a quaternion and may tilt freely (V282), not just turn in plan. Recommended:
   yes, with walls and columns kept upright by default unless unlocked.
4. **Physics engine.** Jolt (already vendored) for all play-fidelity contact, vehicles, soft bodies and buoyancy;
   no second engine. Recommended: yes.
5. **Finite elements.** Write our own narrow slices (plates, then solids) on Stage A's sparse solver, and research
   a WebAssembly solver only if the slices fall short. Recommended: yes.
6. **Domains to drop or defer.** Heat (V292), acoustics (V293) and smoke (V299) are the least asked for so far.
   Recommended: keep them in the plan, after Stages A to D.
7. **Devices.** The world test must pass on a phone at 30 fps, not only on a desktop. Recommended: yes.
8. **First step.** Begin the research note for V277 (`core/math`) now. Recommended: yes.

## 11. References for the plan itself

Each phase's research note carries its own sources. This plan rests on the repository's records: the evaluation
of 2026-11-23, `docs/research/research-physical-world.md` (V239 to V248), `docs/research/research-walkthrough.md`
(Jolt, V203 to V211), `docs/research/research-wind-lbm.md` (V221), `docs/research/research-notion-later-webgpu-compute.md`
(V219), and `docs/work-orders/QUEUE.md`. The techniques in part 6 are standard in the game physics literature
(fixed steps, broadphase, sleeping islands); the research notes will cite the primary sources for those used.
