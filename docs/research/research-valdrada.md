# Research: valdrada, a city simulator to build on (V170)

The owner, after V166: "this is a github repo that i want to clone into our and see how we can build
our simulation on top of it: https://github.com/mkturkcan/valdrada ... this only has apply to NYC
only but what if we can run simulation base on the site we chose". Read from a shallow clone of
its main branch (October 2026), as text; none of its code was run. Asked to choose, the owner chose
to bring its methods into the app (route 1 below).

## What it is

- A digital twin of New York City's five boroughs, by M. K. Turkcan, for synthetic data (camera
  frames with segmentation, instance boxes and depth), closed-loop driving scenarios and
  streetscape studies.
- A Node.js compiler reads the city's open records (the street centreline file with widths, lanes,
  direction and speed; building footprints joined to tax lots; the street-tree census; hydrants,
  shelters, kiosks and more) and writes binary tiles of 512 m. A three.js client streams the tiles
  around the camera, dresses the facades, simulates and renders. A server (Electron) speaks a TCP
  protocol to a Python client modelled on CARLA's. Takes export to OpenUSD for Blender and Unreal.
- The simulation (`client/src/sim/`):
  - cars on a lane graph built from the street centrelines, by IDM car following (a = 1.9 m/s2,
    b = 2.6 m/s2, T = 1.15 s, s0 = 2.2 m, delta 4), with turns planned at junctions, entry held
    when the junction is jammed, and lanes capped by what the roadway's width holds;
  - one fixed signal cycle everywhere: 40 s, each axis 15 s green, 3 s amber, 2 s all red;
  - pedestrians on offsets of the street graph, waiting at signalled corners and crossing on green
    only when they can finish;
  - both spawned around the camera, to fill what it sees.
  It is made to look and behave right on camera, not calibrated to counts or travel demand.

## Why it only covers New York

The simulation itself reads little, tile by tile: each street's centreline points, width, lanes,
one-way, speed, class and parking lanes, the junction ends, and which junctions are signalled. What
binds it to New York is the compiler, which reads New York's own datasets, and the many places
modelled by hand (125th Street, Central Park, the bridges, Times Square).

For any site, OpenStreetMap carries the same: V166 already keeps every street within 800 m of the
lot with its lanes, one-way, speed limit and parking by side, and the signals and stops at its
junctions. Only the width is missing, which `width` gives where mapped, else the lanes at 3.3 m (as
the site context already draws its roads).

## Licences

- Code: MIT. It may be adapted, in a product that is sold too, with its copyright and permission
  notice kept (THIRD_PARTY_NOTICES.md).
- The compiled city: ODbL 1.0, since it holds OpenStreetMap data; the app already credits
  OpenStreetMap wherever its data shows.
- Models: CARLA's vehicles CC BY 4.0; the author's own vehicles and trees CC BY 4.0 (CC0 textures);
  the procedural pedestrians MIT; the Rocketbox avatars MIT. The photoreal pedestrians also fall
  under Epic's MetaHuman terms, which forbid using them to build datasets or train or test models:
  not to be used.

## The routes, and the choice

1. **The methods inside the app (chosen).** Simulation S1 (V170): cars by IDM on V166's street graph,
   the mapped signals on an assumed cycle that is said, pedestrians on the sidewalks to and from the
   lot's doors, the stops and the car parks; live in plan and 3D; results as layers (the queue at
   the lot's entry, people at each door, delay at the crossings). Rewritten to the app's rules (ES5,
   one file, its own renderer), credited. It needs placeable people, bikes and cars first (V169).
2. A fork of valdrada with a compiler from OpenStreetMap: its renderer and sensors for any site, but
   as a separate program the design would be exported to.
3. Both: route 1, and later an export of a site and its design for photoreal footage.

## Light enough for a modest computer

The owner: "it use quite a lot of the memory usage on the web. how can we optimize it so even a
crappy computer can still run it". Valdrada's memory goes on the city and how it looks, not on the
simulation: a photoreal city of a million buildings streamed in tiles around the camera, textured
vehicle and pedestrian models (its photoreal walkers have 25 bodies over 249 material slots),
animated skeletons, sky images, and screen-space ambient occlusion and other post-processing,
each a full-screen buffer. The simulation's own state is a few numbers per car and per walker.
So V170 is light by design:

- **Only the site.** The streets V166 keeps (800 m, 6,000 nodes at most); nothing is streamed or
  fetched for the simulation, and the agents live within that window.
- **Agents as numbers, not objects.** Each kind in fixed pools of typed arrays (position along its
  street, lane, speed, length, route), allocated once: no garbage piling up while it runs, and a
  thousand cars and two thousand walkers in well under a megabyte.
- **Drawn the cheap way.** No textures, no skeletons, no post-processing. In plan, one batched draw
  of small rectangles and dots; in 3D, one instanced draw per kind of V168's low-detail models (tens
  of triangles each), on V152's GPU table, so thousands of agents are a handful of draw calls. Far
  away, an agent is a dot.
- **A fixed step.** The simulation ticks at its own rate (a fixed step of a few tenths of a second,
  which IDM tolerates), drawn interpolated between ticks; it pauses when the tab is hidden, and a
  slow machine ticks less often, not wrongly.
- **Results, not histories.** Queues, counts and delays are tallied into bins as it runs (every few
  seconds), so a long run does not grow.
- **Quality that fits the machine.** Light, Normal or Detailed: how many agents, figures or dots,
  how often it draws. The default is read from the device (its memory and cores, where the browser
  says) and lowered on its own when frames run long.
- **Measured.** The suite runs a long simulation and asks that the page's memory settles (no growth
  after the first minute) and stays within a stated budget, and BENCHMARK (V155) gains the
  simulation, so the owner's own devices give the figures.
