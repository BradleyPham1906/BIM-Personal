# Algorithms behind the programme engine (bubble diagram, matrix, Graph Lab, layout)

Researched 2026-11-16 by Claude (a research agent) for the features listed in `anthropocity-features.md`.
Anthropocity's code is not available and nothing of theirs is taken: this note names the published,
citable method for each feature, so the app can implement it itself in ES5. Evidence levels: P (the source
itself read), S (a dependable secondary source), U (a search summary only; never reaches the code).
Status: IN PROGRESS (skeleton; topics are filled in order).

## 1. Summary

(to be written)

## 2. The topics

### 2.1 Force-directed bubble diagram (features 10, 11, 12, 13, 41)

**Sources read.** Fruchterman and Reingold 1991, "Graph drawing by force-directed placement", *Software:
Practice and Experience* 21(11) 1129-1164, the authors' copy at reingold.co (P, read: the history of Eades and
Kamada-Kawai, figure 1, "Modelling the forces", "The frame", the grid variant, cooling and time complexity).
d3-force 3.0.1 (ISC licence, read 2026-11-16 from raw.githubusercontent.com/d3/d3-force/main: `simulation.js`,
`link.js`, `manyBody.js`, `collide.js`, `x.js`, `radial.js`, `lcg.js`, `jiggle.js`, `LICENSE`, `package.json`;
P). Eades 1984 and Kamada and Kawai 1989 were not read in the original; what is said of them comes from
Fruchterman and Reingold's own account of them (S).

**What the published methods do.**

- *Eades 1984* (S, via FR): rings and springs; neighbours attract by a logarithmic spring, every pair repels;
  Eades asserted that almost all graphs settle after 100 runs of the step. FR quote this and note that Eades did
  not use Hooke's law. (The formula itself is an image in the PDF and did not extract; the commonly cited form
  is attraction c1 log(d/c2) and repulsion c3/d^2 with c1 = 2, c2 = 1, c3 = 1 and a step factor c4 = 0.1: S,
  not re-read here.)
- *Kamada and Kawai 1989* (S, via FR): every pair of vertices has an ideal distance proportional to the length
  of the shortest path between them; the energy is the sum over pairs of k_ij (|p_i - p_j| - l_ij)^2 / 2;
  one vertex is moved at a time (the one with the largest gradient, by Newton-Raphson) until the energy falls
  below a threshold. Cost: all-pairs shortest paths once (O(n^3) by Floyd-Warshall, or n BFS), then O(n) per
  vertex move. Suits small connected graphs; needs special handling for a disconnected graph (no finite
  distance).
- *Fruchterman and Reingold 1991* (P): only neighbours attract, all pairs repel; the ideal distance
  k = C sqrt(area / n), C found experimentally; attraction fa(d) = d^2/k, repulsion fr(d) = -k^2/d, which cancel
  at d = k. Each iteration sums the repulsive then the attractive displacements, then moves each vertex along its
  displacement by at most the temperature t, and clamps it inside the frame. The frame is modelled as four walls
  that push back with exactly the force pushing a vertex through them, i.e. a clamp. Coincident vertices are
  treated as a small distance apart in a random direction. Temperature: for example a tenth of the frame width,
  decaying to 0; they found "quenching then simmering" (fast cooling, then a constant low temperature) better and
  quicker than a steady decrease. Cost O(V^2 + E) per iteration, O(V + E) with the grid variant (repulsion only
  from vertices within 2k). Termination is "guesswork" (their word): a fixed number of iterations. Their stated
  open problem is a frame made of arbitrary line segments (a concave region), which they had not implemented.
- *d3-force 3.0.1* (P, ISC): a velocity Verlet-like integrator with an "alpha" that cools. Defaults read in the
  source: alpha 1, alphaMin 0.001, alphaDecay 1 - 0.001^(1/300) (about 0.0228, so about 300 ticks to settle),
  alphaTarget 0, velocity kept per tick 0.6 (the API's velocityDecay 0.4). Each tick: alpha moves toward
  alphaTarget by alphaDecay; every force adds to each node's velocity (scaled by alpha); then each node moves by
  its velocity times 0.6, unless it has a fixed position fx/fy, in which case it is put there with zero velocity.
  That fx/fy is the "pinned node" mechanism. Initial placement when a node has no position: a phyllotaxis
  spiral, radius 10 sqrt(0.5 + i), angle i times pi(3 - sqrt 5): deterministic. Its random source is a linear
  congruential generator (a = 1664525, c = 1013904223, m = 2^32, seed 1), used only to break exact ties ("jiggle",
  plus or minus 5e-7).
  - forceLink: per link, strength default 1 / min(degree of source, degree of target), distance default 30;
    the correction (l - distance)/l * alpha * strength is split between the two ends by a bias = each end's
    degree share, so a hub moves less. One iteration per tick by default.
  - forceManyBody: strength default -30 (repulsion), distanceMin 1, distanceMax infinite, Barnes-Hut theta 0.9
    (stored squared, 0.81): a quadtree cell of width w at squared distance l is treated as one body when
    w^2 / theta^2 < l. Force on a node: its offset times the summed strength times alpha divided by the squared
    distance (an inverse-distance law).
  - forceCollide: radius per node (default 1), strength 1, iterations 1; looks one tick ahead (x + vx) and
    pushes overlapping pairs apart by the overlap, shared in proportion to the other's squared radius (the small
    one moves more).
  - forceX / forceY / forceRadial: pull toward a coordinate (or a circle) with strength 0.1 per tick.

**What this app needs, and the recommended method (inference, confidence high).** Use the d3-force model,
written as the app's own small ES5 file, not the library (its parts used here total under 300 lines and the
app needs non-d3 additions: containment, determinism, a settled flag). The steps for a work order:

1. *Nodes*: one per room (and per building, for the "planning" mode). Radius r = sqrt(area / pi) times a drawing
   scale, so the bubble's area is the room's area (feature 19's scaled circles use the same formula).
2. *Initial placement, deterministic*: rooms with a saved position keep it; the rest are placed on the
   phyllotaxis spiral around their building's centre, in a stable order (sorted by programme id), scaled by the
   mean radius. No random numbers; ties broken by a seeded generator (the app already has mulberry32 in
   `simulation/traffic-sim.js`, `bimTrRng`) seeded from the project, so the same input gives the same diagram.
3. *Forces per tick*: link (strength from the adjacency strength: primary 1, secondary 0.5, tertiary 0.25,
   times d3's degree normalisation; rest length r_a + r_b + a gap, so linked bubbles touch rather than sit at an
   arbitrary 30); many-body repulsion (exact O(n^2) up to about 150 nodes, Barnes-Hut above; at 500 nodes the
   exact sum is 125 000 pair terms a tick, about 1 ms in a browser, so a quadtree is optional, not required);
   collision by radius (O(n^2) pair test is enough below about 200 nodes); a gentle pull (0.05 to 0.1) toward
   the room's building centre.
4. *Containment in a parent shape*: after the velocity step, any room whose centre lies outside its building's
   circle or polygon (shrunk inward by the room's radius) is moved to the nearest point of the shrunk shape
   and the outward part of its velocity removed. This is FR's "wall that pushes back exactly" generalised to a
   polygon by nearest-point projection (point-in-polygon by ray crossing; nearest point by segment
   projection). For a concave outline the projection is still well defined; edges between nodes may cross the
   outline (FR's own warning), which a bubble diagram tolerates.
5. *Pinned nodes*: a dragged node gets fx/fy; double-click clears them (feature 12). "Freeze all" pins every node
   at its current position; "unfreeze" clears every pin set by freeze, not those set by hand.
6. *Settled state*: alpha cools as in d3 (decay 0.0228 a tick, stop below 0.001, about 300 ticks). The solver
   status shown to the user is running / settled. On an edit, reheat to a small alpha (0.3) rather than 1, so the
   diagram adjusts without reshuffling (feature 41). For reproducible output (tests, export), run a fixed number
   of ticks (300) synchronously instead of on animation frames, so the result does not depend on frame timing.
7. *Determinism checks*: same input, same output to the last digit, given: a fixed node order, no Math.random,
   a fixed tick count, and no dependence on frame rate. Floating-point sums in a fixed order are reproducible in
   one engine; across browsers results may differ in the last bits (+, -, *, / are exactly rounded by IEEE 754;
   ECMAScript leaves Math.cos, Math.sin and possibly Math.sqrt "implementation-approximated", inference from
   memory of the spec, not re-read: U). So round the initial spiral to 1e-6 m and compare test outputs with a
   tolerance, not bit for bit.

**Cost.** Per tick O(n^2) exact: 10 nodes trivial; 500 nodes about 250 000 pair evaluations for repulsion plus
collision, a few ms; 300 ticks under a second. Kamada-Kawai at 500 nodes needs a 250 000-entry distance matrix
and many Newton steps; not needed.

**Failure modes.** Local minima (a node trapped behind another: FR note their quadratic forces help it shoot
past); oscillation if velocity is kept too high; disconnected components drift apart under repulsion (the pull
toward the building centre fixes it); a room larger than its building outline cannot be contained (report it);
pinned nodes that contradict links leave the links stretched (expected, show the strain). Termination is a
fixed schedule, not a proof of a minimum (FR, P).

Level: P for FR and d3-force, S for Eades and Kamada-Kawai. Confidence: high.

### 2.2 Links from weighted parameters
### 2.3 Community detection with a resolution
### 2.4 Bridges, articulation points, hubs, depth, aspect
### 2.5 Corridors routed from user paths
### 2.6 Stair placement
### 2.7 Bay grid and small-room clustering
### 2.8 Import of a programme sheet
### 2.9 Export
### 2.10 Offline stand-ins for the online AI features

## 3. Feature table

## 4. Counter-evidence and failure modes

## 5. Still open

## 6. Search log

## 7. References
