# W1 walkthrough: experiments

Data for `docs/research/research-walkthrough.md`, never a suite. Run 2026-11-14 in the cloud container: Node 22.23.4 and
Chromium 153.0.8010.12 (Playwright's chromium-1243), Linux. No phone or tablet, no Safari, no Firefox here.

| Experiment | Script | Results | What it measures |
|---|---|---|---|
| e01 | `physics-bench.mjs` | `e01-results.json` | Rapier 0.21.0, Jolt 1.1.1 and three.js 0.186.1's Octree on one course (a 0.18 m step, a 0.40 m curb, a 1:12 ramp, a 40 degree slope, a wall at 10 m/s), then a 5000-box town (60,002 triangles) walked for 600 frames, three runs |
| e02 | `file-url-check.mjs` | `e02-results.json` | Each engine bundled by esbuild into one classic script, loaded from a `file://` page in Chromium, three runs: does it load, how long to start |

How to run them: install the packages named at the top of each script in a scratch folder (never in the
repository), and run the script from there. e02 also needs esbuild 0.25.10 and Playwright.

## What the runs showed, in short

- All three walkers pass the step, the curb, the ramp and the wall. The Octree walker also walks up the 40 degree
  slope (it counts any upward push as floor), which the other two refuse.
- The town, per frame: Jolt 0.009 to 0.010 ms mean, Rapier 0.028 to 0.032 ms, the Octree 0.006 to 0.010 ms. All far under a
  frame's 16.7 ms. Building the collision: Rapier 39 to 54 ms, Jolt 237 to 263 ms, the Octree 5149 to 5645 ms.
- Rapier's walker stalled twice on flat ground in the town (about 30 frames each), ending 3.8 m from where Jolt's
  and the Octree's walkers ended (they agree within 3 cm). Turning off its snap to ground (`enableSnapToGround`) removed the
  stalls (run by hand on 2026-11-14 with the variants in the note; not in the JSON).
- A first run started the town walk inside a building's corner. Rapier then spent 3 ms a frame; that run is
  discarded, and the walk now starts in a street.
- e02: both load from `file://` with no error. Rapier's bundle 4,337,501 bytes (1,653,038 gzipped), started in 47 to 55 ms;
  Jolt's 4,010,952 bytes (950,921 gzipped), started in 128 to 152 ms. Jolt's file needs `node:*` marked external to bundle.
