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

### 2.2 Links from weighted parameters (features 20, 21, 22, 23)

**Sources read.** Gower 1971, "A general coefficient of similarity and some of its properties", *Biometrics*
27(4) 857-871 (a JSTOR copy hosted at mathematics.foi.hr; read: sections 1, 2, 4 and the statement of the
p.s.d. property; P). The R `gower` package vignette, van der Loo, 2024-12-16 (CRAN mirror; S, for how a
modern implementation treats missing values). Von Luxburg 2007, "A tutorial on spectral clustering",
arXiv 0711.0189, section 2.2 "Different similarity graphs" (P). Richard Muther and Associates, Planning
Guide RMA 1111 "Procedure for making relationship diagrams" (2002, richardmuther.com; P), for the practice
link between closeness ratings, line counts and a spring diagram.

**No published method found that derives architectural adjacency from room-parameter similarity** (two
searches, part 6). Anthropocity documents the feature but not the method (S). The nearest practice is
Muther's Systematic Layout Planning: each pair of activities gets a closeness rating A, E, I, O, U or X, each
with a coded *reason* (shared personnel, shared equipment, flow of material...); the relationship diagram then
draws A as four lines, E three, I two, O one, U none, and X as a zigzag that Muther himself likens to a
compressed spring pushing the pair apart, while the straight lines are elastic bands pulling them together
(P). That is the hand version of topic 1's force diagram with link strength = number of lines, and it
supports mapping strength 1/2/3 to a link force.

**The similarity, as published (Gower, P).** For rooms i and j and parameter k, a score s_ijk in [0, 1] and a
flag d_ijk that is 1 when the parameter can be compared (both values present) and 0 otherwise:
- quantitative (privacy 1 to 5, daylight lux): s_ijk = 1 - |x_ik - x_jk| / R_k, R_k the range of parameter k
  in the sample (or the population);
- qualitative (unordered categories): 1 if equal, 0 if not;
- dichotomous (present/absent): Gower's table, where absent-absent is not counted (d = 0).
Similarity S_ij = sum_k w_k d_ijk s_ijk / sum_k w_k d_ijk (Gower's equation 5, weights w_k >= 0). It is
undefined when no parameter can be compared. Without missing values and with non-negative weights the
similarity matrix is positive semi-definite, so 1 - S behaves as a squared Euclidean distance (Gower, P).
Modern packages simply skip missing values (vignette, S): the same as d = 0.

Why Gower and not the alternatives (inference, confidence high):
- Weighted Euclidean on range-normalised values gives the same ordering as Gower for all-numeric complete data
  but has no rule for blanks or categories.
- Cosine similarity ignores magnitude: a room scored 1 on every parameter and one scored 5 on every parameter
  have cosine 1 (identical), which is wrong for "level" parameters such as privacy. Not recommended.
- Gower handles mixed types, blanks ("blanks allowed", feature 20) and per-parameter weights (feature 20)
  exactly as the feature asks.

**From similarity to a few links (von Luxburg 2.2, P; the choices are ours).** Von Luxburg names three
constructions: the epsilon-neighbourhood graph (connect pairs closer than a threshold), the k-nearest-neighbour
graph (connect i and j if either is among the other's k nearest; the mutual version needs both), and the fully
connected graph. A bubble diagram needs few links, so:

1. Compute S for every pair of rooms in the same building (n(n-1)/2 pairs: 125 000 at 500 rooms, trivial).
   Parameters with weight 0 are ignored; a pair with no comparable parameter gets no link.
2. Candidates: for each room, its top k by S (k default 2; union kNN, so every room gets at least one link)
   and keep only pairs with S at or above a floor (default 0.7), except as in step 3.
3. Connectivity: add the edges of a maximum spanning tree of S (Kruskal: sort pairs by S descending, union-find)
   that are missing, so the diagram is one piece. Mark these as "connecting" in the report.
4. Strength: by S bands, S >= 0.9 strength 1 (primary), >= 0.8 strength 2, else 3 (thresholds are project
   settings, shown to the user). Or by rank: the top third of the kept links strength 1, etc.
5. Write the links as generated and "suggested" (decision 9 of program-to-plan), overwriting only earlier
   generated links (feature 22: "regenerating overwrites"); hand-made links are never touched.
6. Show the reason: the parameters that agreed most (Muther's reason codes in spirit), so the user can judge.

Parameters: weights per parameter (default 1), k (2), floor (0.7), band thresholds (0.9, 0.8), range R_k from
the sample. Cost: O(n^2 v) for v parameters; 500 rooms and 10 parameters is 1.25 million operations,
milliseconds; Kruskal O(n^2 log n) on the full pair list, under 50 ms at 500 rooms.

**Failure modes.** Similarity is not adjacency: rooms that must touch are often unlike (kitchen and dining
differ in privacy and noise; a waiting room and a consulting room) and like rooms need not touch (two
bedrooms at opposite ends). The method suggests clusters of like rooms, which is a zoning idea, not a
circulation idea; the user must review (inference, confidence high). With one parameter, many ties: sort ties
by programme id for determinism. With R_k = 0 (all rooms equal on k) the score is undefined: skip k.

Level: P (Gower, von Luxburg, Muther), the method assembled from them is inference. Confidence: high for the
similarity, medium for the link rules (no published architectural precedent).

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
