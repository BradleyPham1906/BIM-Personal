# The work-order queue

Claude keeps this list full; Cline takes from the top. A phase is listed here only when its research
is done, the owner's decisions are made, and every `[Cline]` task has its test and names its file(s).

Cline: `/ship-task` with no arguments takes the first open `[Cline]` task below.

The owner's decisions (2026-11-14): for every phase below, all as its research recommends (each SPEC lists them;
overrule any there). V177's D1 to D4 and That Open's four were answered 2026-11-13. The phases are numbered in one
sequence, 175c to 248 (228 to 232 are algorithmic design, the owner's thirteen decisions, 2026-11-15; 233 to 238 program to plan, the owner's ten decisions, 2026-11-16; 239 to 247 the physical world, the owner's answer 2026-11-22: standard and scalable, `research-physical-world.md` part 11), in `docs/dev/PIPELINE.md`; there are no "later" rows.

## Ready for Cline, in order (310 tasks)

| Phase | What | Tasks | Where | Tests |
|---|---|---|---|---|
| v202 | Site context C3: measured heights, ground and bridges; part B, the Site and Map interface; part C, heights on one datum and the GEM-15 surface model (the owner, 2026-11-21: next) | WO-01 to WO-05, WO-12 to WO-14, WO-22 to WO-26 (13), any order | `v202/TASKS.md` | `v202/v202.test.mjs`, `v202/v202-ui.test.mjs`, `v202/v202-datum.test.mjs`, `v202/v202-surface.test.mjs` |
| v178 | Presentation P3, the report (Site Analysis and DA), styles, export | WO-01 to WO-12 (12) | `v178/TASKS.md` | `v178/v178.test.mjs` |
| v181 | Interiors I3, circulation and escape routes | WO-01 to WO-05 (5) | `v181/TASKS.md` | `v181/v181.test.mjs` |
| v182 | Interiors I4, sightlines and views | WO-01 to WO-05 (5) | `v182/TASKS.md` | `v182/v182.test.mjs` |
| v183 | Freeform F1, NURBS curves | WO-01 to WO-06 (6) | `v183/TASKS.md` | `v183/v183.test.mjs` |
| v184 | Freeform F2, surfaces from curves | WO-01 to WO-06 (6) | `v184/TASKS.md` | `v184/v184.test.mjs` |
| v185 | Freeform F3, sweeps, pipes and caps | WO-01 to WO-05 (5) | `v185/TASKS.md` | `v185/v185.test.mjs` |
| v186 | Freeform F4, surface analysis | WO-01 to WO-05 (5) | `v186/TASKS.md` | `v186/v186.test.mjs` |
| v187 | Freeform F5, point editing and blends | WO-01 to WO-05 (5) | `v187/TASKS.md` | `v187/v187.test.mjs` |
| v188 | Freeform F6, picture planes, text objects, flow along a surface | WO-01 to WO-05 (5) | `v188/TASKS.md` | `v188/v188.test.mjs` |
| v189 | Freeform F7, Make2D (hidden-line drawings) | WO-01 to WO-04 (4) | `v189/TASKS.md` | `v189/v189.test.mjs` |
| v190 | LOD-C point clouds, first slice (local LAS and PLY) | WO-01 to WO-11 (11) | `v190/TASKS.md` | `v190/v190.test.mjs` |
| v191 | LOD-D, LOD1.3 and LOD2.2 roofs from LiDAR | WO-01 to WO-05 (5) | `v191/TASKS.md` | `v191/v191.test.mjs` |
| v192 | LOD-E, facade images rectified onto walls | WO-01 to WO-06 (6) | `v192/TASKS.md` | `v192/v192.test.mjs` |
| v193 | LOD-F, LOD3 openings on rectified facades | WO-01 to WO-05 (5) | `v193/TASKS.md` | `v193/v193.test.mjs` |
| v201 | MEP runs, first slice (a checked tree, straight friction only) | WO-01 to WO-07 (7) | `v201/TASKS.md` | `v201/v201.test.mjs` |
| v204 | The Parametric Design Foundation, sketch to Pad to Pocket | WO-01 to WO-04 (4) | `v204/TASKS.md` | `v204/v204.test.mjs` |
| v205 | LOD-G, Gaussian splats as a backdrop | WO-01 to WO-05 (5) | `v205/TASKS.md` | `v205/v205.test.mjs` |
| v206 | That Open: the Review view and IFC import (with Hub H3's identity) | WO-01 to WO-07 (7) | `v206/TASKS.md` | `v206/v206.test.mjs` |
| v207 | glTF models in Assets, and valdrada's credited models | WO-01 to WO-04 (4) | `v207/TASKS.md` | `v207/v207.test.mjs` |
| v208 | Walkthrough W2, drive | WO-01 to WO-04 (4) | `v208/TASKS.md` | `v208/v208.test.mjs` |
| v209 | Walkthrough W3, fly and drone | WO-01 to WO-04 (4) | `v209/TASKS.md` | `v209/v209.test.mjs` |
| v210 | Walkthrough W4, swim | WO-01 to WO-04 (4) | `v210/TASKS.md` | `v210/v210.test.mjs` |
| v211 | Walkthrough W5, record and replay | WO-01 to WO-04 (4) | `v211/TASKS.md` | `v211/v211.test.mjs` |
| v212 | Survey control, traverses and closure | WO-01 to WO-05 (5) | `v212/TASKS.md` | `v212/v212.test.mjs` |
| v213 | Generators: massing, parking, lots | WO-01 to WO-05 (5) | `v213/TASKS.md` | `v213/v213.test.mjs` |
| v214 | Costs and pro forma | WO-01 to WO-04 (4) | `v214/TASKS.md` | `v214/v214.test.mjs` |
| v215 | Flows and an app SDK | WO-01 to WO-04 (4) | `v215/TASKS.md` | `v215/v215.test.mjs` |
| v216 | Hub H4, share and sync through GitHub | WO-01 to WO-05 (5) | `v216/TASKS.md` | `v216/v216.test.mjs` |
| v217 | Hub H5, the server's access rules | WO-01 to WO-04 (4) | `v217/TASKS.md` | `v217/v217.test.mjs` |
| v218 | Streaming: OGC 3D Tiles | WO-01 to WO-03 (3) | `v218/TASKS.md` | `v218/v218.test.mjs` |
| v219 | WebGPU compute: the CPU reference first | WO-01 to WO-04 (4) | `v219/TASKS.md` | `v219/v219.test.mjs` |
| v220 | Water and presentation rendering | WO-01 to WO-04 (4) | `v220/TASKS.md` | `v220/v220.test.mjs` |
| v221 | Wind around buildings: the lattice Boltzmann reference | WO-01 to WO-04 (4) | `v221/TASKS.md` | `v221/v221.test.mjs` |
| v222 | 4D/5D construction planning, CP0 to CP3: quantities, cost lines, allocation | WO-01 to WO-04 (4) | `v222/TASKS.md` | `v222/v222.test.mjs` |
| v223 | 4D/5D construction planning, CP4 and CP5: procurement and drawing intake | WO-01 to WO-03 (3) | `v223/TASKS.md` | `v223/v223.test.mjs` |
| v224 | Track E, field work: positions without GPS and step-by-step instructions | WO-01 to WO-04 (4) | `v224/TASKS.md` | `v224/v224.test.mjs` |
| v225 | The OpenBridge UI foundation | WO-01 to WO-04 (4) | `v225/TASKS.md` | `v225/v225.test.mjs` |
| v226 | Track C, the PennDOT LRFD input writer | WO-01 to WO-03 (3) | `v226/TASKS.md` | `v226/v226.test.mjs` |
| v227 | Track D, the drone bridge project: flight planning | WO-01 to WO-05 (5) | `v227/TASKS.md` | `v227/v227.test.mjs` |
| v228 | Generated elements: a stable key, re-run in place, hand overrides | WO-01 to WO-05 (5) | `v228/TASKS.md` | `v228/v228.test.mjs` |
| v229 | A split grammar for facades | WO-01 to WO-05 (5) | `v229/TASKS.md` | `v229/v229.test.mjs` |
| v234 | The programme graph engine: bubble diagram, matrix, links from parameters | WO-01 to WO-07 (7) | `v234/TASKS.md` | `v234/v234.test.mjs` |
| v235 | Graph analysis and user paths | WO-01 to WO-09 (9) | `v235/TASKS.md` | `v235/v235.test.mjs` |
| v236 | The layout view: bay grid, corridors from paths, scorecard | WO-01 to WO-08 (8) | `v236/TASKS.md` | `v236/v236.test.mjs` |
| v239 | Floor loads: live loads, reduction, roof | WO-01 to WO-03 (3) | `v239/TASKS.md` | `v239/v239.test.mjs` |
| v240 | Wind loads: Kz, q, Cp, storey forces, load cases | WO-01 to WO-06 (6) | `v240/TASKS.md` | `v240/v240.test.mjs` |
| v241 | Earthquake loads: spectra, ELF, the USGS service, drift | WO-01 to WO-09 (9) | `v241/TASKS.md` | `v241/v241.test.mjs` |
| v242 | Modes and the response spectrum | WO-01 to WO-07 (7) | `v242/TASKS.md` | `v242/v242.test.mjs` |
| v243 | Concrete members: cracking and strength | WO-01 to WO-06 (6) | `v243/TASKS.md` | `v243/v243.test.mjs` |
| v244 | Steel members: AISC 360-22 checks | WO-01 to WO-07 (7) | `v244/TASKS.md` | `v244/v244.test.mjs` |
| v245 | The building under a ground motion | WO-01 to WO-05 (5) | `v245/TASKS.md` | `v245/v245.test.mjs` |
| v246 | Form-finding: force density, dynamic relaxation | WO-01 to WO-03 (3) | `v246/TASKS.md` | `v246/v246.test.mjs` |
| v247 | Stormwater runoff on the site | WO-01 to WO-06 (6) | `v247/TASKS.md` | `v247/v247.test.mjs` |
| v248 | The shape of the ground: curvature, ruggedness, a viewshed | WO-01 to WO-03 (3) | `v248/TASKS.md` | `v248/v248.test.mjs` |
| v275 | The Explode view: storeys pulled apart upward by one amount, display only (the owner's decisions E1, E2, 2026-11-23, `research-xr-interaction.md`) | WO-01 to WO-06 (6) | `v275/TASKS.md` | `v275/v275.test.mjs` |
| v274 | XR-1, the headset view: a cardboard viewer's settings from its QR link, lenses, each eye's field, the head from the motion sensors (the owner's decisions 2026-11-23, `research-devices-xr.md`) | WO-01 to WO-09 (9) | `v274/TASKS.md` | `v274/v274.test.mjs` |

Every test was run against a reference version that was not committed (all passing) and against the empty files
(every case failing), so a task is done exactly when its own cases pass. Each phase's new file is already in the
build order with its header only; `npm test` and `npm run check` are green. After a phase's `[Cline]` tasks, its
TASKS file lists Claude's own: wiring the functions into the app, the one browser check of the new interface, the
records.

## Elsewhere

| Phase | Where |
|---|---|
| v203 Walkthrough W1 | Done 2026-11-21: WO-01 to WO-08 shipped by Cline; Claude's C-02 to C-08 (WALK, its controls, the rendered view's moving mode, the browser check 25 of 25) |
| v175c | Done 2026-11-21: WO-11 to WO-17 shipped; Claude's WO-18 (Open as layout, Work in viewport, the vector page; 13 of 13) and WO-19 |
| v177 | Done 2026-11-21: steps 1, 2a and 2b; the browser check on Cline's functions and Make editable, 26 of 26 |
| v194 | Done 2026-11-21: T-07's looks wired into the materials; T-06's browser check, 15 of 15 |
