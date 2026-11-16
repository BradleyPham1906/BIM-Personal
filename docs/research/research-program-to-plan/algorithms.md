# Algorithms behind the programme engine (bubble diagram, matrix, Graph Lab, layout)

Researched 2026-11-16 by Claude (a research agent) for the features listed in `anthropocity-features.md`.
Anthropocity's code is not available and nothing of theirs is taken: this note names the published,
citable method for each feature, so the app can implement it itself in ES5. Evidence levels: P (the source
itself read), S (a dependable secondary source), U (a search summary only; never reaches the code).
Status: complete for the ten topics asked. No independent second reader yet: every number a work order uses is
re-read at its source first (as in program-to-plan part 3).

## 1. Summary

No library is needed for any of the ten topics; the optional ones are SheetJS (Apache-2.0) for .xls/.ods and
pdf.js (Apache-2.0) for PDF tables, both recommended *not now*. Everything below is about 1 500 to 2 000 lines of
the app's own ES5 across about eight engine files, each with unit tests.

| # | Topic | Recommended method, one line | Level | Confidence |
|---|---|---|---|---|
| 1 | Bubble diagram | d3-force's model (alpha cooling, link + many-body + collide + centre pull, fx/fy pins) as own ES5, plus projection into the parent circle/polygon, seeded spiral start and a fixed 300-tick run for reproducible output | P (FR 1991, d3-force 3.0.1 source) | high |
| 2 | Links from parameters | Gower's weighted similarity (ranges, blanks skipped), then union top-k neighbours above a floor, plus a maximum spanning tree for connectivity, strengths by bands; generated links marked suggested | P (Gower 1971, von Luxburg 2007, Muther RMA 1111) | high (similarity), medium (link rules) |
| 3 | Clusters | Louvain with Reichardt-Bornholdt resolution gamma, fixed node order, then split disconnected communities; Leiden later if needed | P (Blondel 2008, Traag 2019, R-B 2006) | high / medium for defaults |
| 4 | Bridges, hubs, depth, aspect | One iterative DFS with low-link (articulation points, bridges, subtree sizes for "separates N rooms"); weighted degree; centre by minimum eccentricity and BFS depth; PCA of area-weighted room positions with extents | P (NetworkX code), S (Tarjan) | high |
| 5 | Corridors from paths | Dijkstra per path leg on the wall graph, use counts per wall edge, spine at the threshold, Takahashi-Matsuyama nearest-first spurs, dead ends closed above a limit, corridors cut from rooms and reported | P (Mirahmadi-Shami 2012, NetworkX Steiner), S (KMB, T-M) | medium |
| 6 | Stair | Exhaustive weighted 1-median ("path priority") or 1-centre ("worst leg") over corridor corners that fit on all levels, with a move limit | P (Hakimi 1964 abstract) | high |
| 7 | Bay grid | Bands of depth d, rooms take whole bays of width b; b by exhaustive 1-D search for least area deviation; small rooms clustered with linked neighbours (max 3) then sliced inside their bays; order follows the bubble diagram | P (Muther, Concrete Centre), own method | medium |
| 8 | Import | CSV per RFC 4180 first; .xlsx second by own ZIP reader + DecompressionStream('deflate-raw') + DOMParser; PDF not now (paste text instead) | P | high / medium-high / medium |
| 9 | Export | SVG per view, PDF via print, DXF via the existing `bimBuildDXF` writer with a level elevation per polyline | P (app code), S (DXF code 38) | high |
| 10 | AI stand-ins | Templates and paste-in text; walk-through by a name list; entrance by name, else highest betweenness (Brandes); paths by BFS from the entrance per user group | P (NetworkX Brandes), inference | medium |

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

### 2.3 Community detection with a resolution (features 25, 26)

**Sources read.** Blondel, Guillaume, Lambiotte, Lefebvre 2008, "Fast unfolding of communities in large
networks", arXiv 0803.0476 (P: the two phases, equation 2, the note on node order). Traag, Waltman, van Eck
2019, "From Louvain to Leiden: guaranteeing well-connected communities", arXiv 1810.08473 (P: equations 1 and
2, section II on badly connected communities, the refinement phase, the fast local move, theta). Reichardt and
Bornholdt 2006, "Statistical mechanics of community detection", arXiv cond-mat/0603718 (P: the Hamiltonian
with the gamma-weighted null model, A_ij - gamma p_ij). NetworkX `louvain.py` (main branch, BSD-3-Clause; P:
defaults resolution 1, threshold 1e-7, seed None, nodes visited in a seeded random shuffle). Licences of the
reference Leiden code: `leidenalg` (Python) GPL-3.0 (P, LICENSE read); CWTS `networkanalysis` (Java) MIT (P).

**The quality function.** Modularity with resolution (Reichardt and Bornholdt's null model p_ij = k_i k_j / 2m,
in Traag's notation): H = (1/2m) sum over communities c of [ e_c - gamma K_c^2 / 2m ], with e_c the weight of
links inside c, K_c the sum of the weighted degrees in c, m the total link weight (P). gamma = 1 is ordinary
modularity; higher gamma gives more, smaller communities; lower gamma fewer, larger ones (P, Traag). The
alternative, the Constant Potts Model, H = sum_c [ e_c - gamma n_c(n_c - 1)/2 ], reads gamma as a density
threshold and avoids modularity's resolution limit (P, Traag); its gamma is not on the same scale.

**Louvain (P).** Start with each node alone. Phase 1: visit nodes in turn; for node i, compute the gain of
moving it into each neighbour's community (equation 2: needs only the community's inside weight, its total
degree, i's degree and i's weight into it), move it to the best positive gain (ties by a rule), repeat passes
until no move improves. Phase 2: collapse each community into one node (inner links become a self-loop),
then repeat phase 1 on the smaller graph; stop when nothing changes. The authors state that the result
depends on node order, that order seemed not to matter much for the quality reached, and that it affects time
(P). With resolution, the gain's second term is multiplied by gamma.

**Leiden (P).** Louvain can return arbitrarily badly connected communities, even internally disconnected
ones (in their tests up to 25 % badly connected and 16 % disconnected). Leiden adds a refinement phase:
within each community of the moved partition, start from singletons and merge nodes only with
sub-communities that are well connected to their community, choosing among improving merges at random
with a temperature theta (they used 0.01; 0.0005 to 0.1 work); aggregate on the refined partition. Its local
moving uses a queue: only nodes whose neighbourhood changed are revisited. Guarantees: every community is
connected (gamma-connected) after each iteration (P).

**Recommended for this app (inference, confidence medium-high).** Louvain with the resolution parameter and
a connectivity repair, written in ES5 (about 150 lines), deterministic:
1. Graph: rooms as nodes, adjacency links as weighted edges (strength 1 -> weight 3, 2 -> 2, 3 -> 1, so primary
   counts most), optionally without bridges (feature 26: "ignore bridges while clustering", from topic 4).
2. Node order: fixed (programme order, or sorted by id), not shuffled. Ties: lowest community index. This
   makes the run reproducible without a seed; NetworkX's equivalent is a fixed seed (P).
3. Phase 1 and phase 2 as Louvain, with gamma from the user's slider (0.2 to 3, default 1).
4. Repair: after the last level, split any community whose induced subgraph is disconnected into its
   connected components (a BFS per community). Traag et al. call this fix "unsatisfactory" for large networks
   because it only fixes the extreme case (P), but at 10 to 200 rooms with a final local-moving pass it is
   cheap and is what the user sees: no community drawn in two pieces.
5. Output: a community id per room, the modularity value, and per community its rooms, its total area and
   its strongest internal link (for naming).

Leiden itself, with theta = 0 (greedy refinement), is an option for later if users see poorly connected
clusters; with theta > 0 it needs a seeded generator. Writing Leiden from the paper is about 300 lines; its
reference code in Python is GPL-3.0 and cannot be copied; the Java one is MIT (read as text only if needed).

**Cost.** Louvain is near-linear in edges per pass; at 200 rooms and about 600 links, a few passes of a few
thousand operations each: under 1 ms. On small graphs the result is sensitive: a single link change can merge
or split clusters, and several partitions may have nearly equal quality (inference; the "degeneracy" of
modularity is a known issue, Good, de Montjoye, Clauset 2010, not read: U).

**Failure modes.** Resolution limit of modularity at gamma = 1 (small, clear groups merged in a large graph;
Fortunato and Barthelemy 2007, cited by Traag, not read: S); disconnected communities (Louvain, fixed by step
4); order dependence (fixed by step 2, but a different fixed order can give a different answer: say so);
isolated rooms form singleton communities.

Level: P. Confidence: high for the method, medium for the defaults chosen.

### 2.4 Bridges, articulation points, hubs, depth, aspect (features 26, 27)

**Sources read.** NetworkX (BSD-3-Clause), `algorithms/components/biconnected.py` `_biconnected_dfs` and
`algorithms/bridges.py`, main branch, read as text 2026-11-16 (P). They cite Hopcroft and Tarjan 1973,
"Efficient algorithms for graph manipulation", CACM 16:372-378 (S, not read). Tarjan 1972 "Depth-first search
and linear graph algorithms" (SIAM J. Computing 1(2)) and Tarjan 1974 "A note on finding the bridges of a
graph" (Information Processing Letters 2:160-161) were not reached (paywalled): S, through NetworkX's code and
the standard textbook statement. Hakimi 1964 for the centre: see topic 6.

**Articulation points and bridges (P through NetworkX's code; S for Tarjan).** One depth-first search,
recording for each vertex its discovery number disc(v) and low(v), the smallest discovery number reachable
from v's subtree by tree edges down and at most one back edge up. Then, for a tree edge parent u to child v:
- u is an articulation point if low(v) >= disc(u) and u is not the root; the root is one if it has two or more
  tree children (NetworkX's code, P);
- the edge (u, v) is a bridge if low(v) > disc(u) (strict).
NetworkX runs the search with an explicit stack (no recursion), which an ES5 version should copy in spirit to
avoid deep recursion; its bridges function instead uses chain decomposition (Schmidt 2013), an equivalent
linear method. Cost O(V + E): nothing at 500 rooms.

**"Separates at least N rooms" (inference, exact).** Record, in the same search, the size of each subtree,
sub(v). Removing bridge (u, v) leaves two pieces of sub(v) and n_c - sub(v) rooms (n_c the size of that
connected component); the bridge passes the filter when the smaller piece has at least N rooms (default N = 2,
so a link to a single leaf room is not reported as a bridge: a leaf hanging on one link is trivial). For an
articulation point u, the pieces are sub(c) for each child c with low(c) >= disc(u), plus the rest; report the
smallest piece. Weighted links do not change bridges (they are a property of the topology); an option "count
only links of strength 1 and 2" runs the same search on a filtered graph.

**Hub score.** Weighted degree: sum of the strengths of a room's links, with strength mapped so primary counts
most (1 -> 3, 2 -> 2, 3 -> 1; the same map as topic 3). Report the top hub, the maximum and the mean
(feature 27). This is "strength" in network science (Barrat et al. 2004, not read: U); the definition is
simple enough to need no source.

**Depth from the network's centre.** The centre is the set of vertices of minimum eccentricity, the
eccentricity of v being its largest shortest-path distance to any other vertex (Hakimi 1964's "absolute centre"
generalises it to points on edges: topic 6). Recommended: hop distance (BFS) for depth, because the user reads
"depth" as number of steps; centre = the room of minimum eccentricity, ties broken by highest hub score, then
by id. Then BFS from the centre gives each room's depth; report the mean and the maximum (feature 27). This is
also Hillier and Hanson's "depth" in space syntax (not read here: S from general knowledge), which supports
the reading. Cost: n BFS runs, O(n (n + m)), 500 rooms about 500 x 2 000 = a million steps: milliseconds.
Disconnected graph: compute per component and say so.

**Building aspect, major and minor axes (inference, exact arithmetic).** Principal axes of the rooms of a
building: take the area-weighted centroid of the room positions, the 2 x 2 covariance matrix
[[sxx, sxy], [sxy, syy]] (area-weighted, plus each disc's own second moment r^2/4 on both axes so one big
room is not a point), its eigenvalues in closed form, l1,2 = (sxx + syy)/2 +- sqrt(((sxx - syy)/2)^2 + sxy^2),
and the major axis angle 0.5 atan2(2 sxy, sxx - syy). Major and minor axis lengths: the extents of the room
discs projected on the two axes (max minus min of p.axis +- r), which a user can measure; aspect = major /
minor. (Using 4 sqrt(l) instead gives the equivalent ellipse; either is defensible, the extents are easier to
check.) For an editable building polygon, use the polygon's own second moments instead of the rooms.

Level: P (NetworkX code), S (Tarjan, Hakimi as cited), inference for the filter and aspect. Confidence: high.

### 2.5 Corridors routed from user paths (features 28, 29, 34, 36, 39)

**Sources read.** Kou, Markowsky and Berman 1981 (Acta Informatica 15:141-145) and Mehlhorn 1988, as
implemented and documented in NetworkX `algorithms/approximation/steinertree.py` (BSD-3-Clause; P for the code,
S for the papers: the papers themselves were not read). Takahashi and Matsuyama 1980 (Math. Japonica 24) not
reached: S from the standard account. Mirahmadi and Shami 2012, "A novel algorithm for real-time procedural
generation of building floor plans", arXiv 1211.5842, section III.C "Corridor placement" (P). Shiksha, Anand,
Shekhawat, Agrawal 2025 (AI EDAM 39 e9): as read and summarised in `layout-methods.md` section 2.3, cited not
re-read (P there). Marson and Musse 2010 (IJCGT, Hindawi): both hosts (downloads.hindawi.com, Wiley) returned a
script challenge page, not the PDF: not read; Mirahmadi and Shami describe it as placing a corridor when rooms to
be connected are not adjacent (S). Lopes, Tutenel, Smelik, de Kraker, Bidarra 2010, "A constrained growth method
for procedural floor plan generation" (GAME-ON 2010): graphics.tudelft.nl and publications.graphics.tudelft.nl
reset the connection twice; a search summary says it uses A* to find a shortest route joining the rooms that need
a corridor and then adjusts neighbouring rooms to make space (U only, not used for the method).

**What the published methods say.**
- *Corridors along walls (Mirahmadi and Shami, P).* Build a graph whose edges are the walls of the rooms that
  need a connection and of the hub room (the living room), leaving out the building's outer walls; prune edges
  to degree-one vertices; take the shortest path in that graph connecting all those rooms, a room counting as
  connected if it shares an edge or a vertex with the path; justify shortest by "corridor area is wasted area";
  among variants, reject those that leave rooms oddly shaped and keep the smallest corridor; cut the corridor
  polygon out of the overlapping rooms. This is the closest published match to "corridors routed along walls".
- *Steiner tree on a graph (KMB, P via NetworkX).* Given a weighted graph and terminals: compute shortest paths
  between all terminal pairs (the metric closure), take its minimum spanning tree, replace each tree edge by its
  shortest path, take the minimum spanning tree of that subgraph, and repeatedly delete non-terminal leaves.
  Result within 2 - 2/l of optimal (l the number of leaves of an optimal tree). Cost O(|S| |V|^2) as documented;
  Mehlhorn's variant O(|E| + |V| log |V|).
- *Takahashi and Matsuyama (S).* Start from one terminal; repeatedly add the terminal nearest to the current
  tree by its shortest path to the tree; same 2 - 2/l bound. Simpler than KMB and incremental, which is what
  "connect the remaining rooms with the shortest spur" means.
- *Shiksha et al. 2025 (P in layout-methods).* Corridors are inserted by shifting walls; rooms shrink by the
  corridor area; minimal circulation is a set cover solved greedily; public rooms may serve as passages.

**Recommended method (inference, confidence medium: the steps are assembled from the sources above; no paper
does exactly paths-with-frequencies to spine).**

1. *Wall graph.* From the rooms on the bay grid (topic 7), make vertices at every wall corner and T-junction,
   and an edge for every wall segment between them, weighted by its length. Exterior walls are kept but with a
   cost factor (default 3) so routes prefer interior walls and use the facade only for the short stubs that
   Anthropocity describes (Mirahmadi excludes them outright). Edges through a room's interior do not exist;
   "walk-through" rooms (feature 30: lobby, waiting) add edges across the room between its wall vertices.
2. *Legs.* For each user path (an ordered list of rooms with a frequency weight: primary 3, secondary 2,
   occasional 1), each consecutive pair of rooms is a leg. Route each leg with Dijkstra from all vertices on
   room A's walls (a multi-source start at cost 0) to any vertex on room B's walls (stop at the first reached).
   Ties: lowest vertex id, so the run is reproducible. A leg between levels is reported (feature 39), not routed,
   until the stair exists (topic 6).
3. *Use count.* For each wall edge, count the paths that use it (each path counted once even if several legs
   cross the edge) and the frequency-weighted sum.
4. *Spine.* Edges whose path count is at or above the spine threshold (a setting, default 2) get the main width
   (a registry value; BB103's 1.8 m for a corridor serving several rooms, see `layout-methods.md` 2.3, P there).
5. *Access spurs ("Spine + access").* Rooms not touching the network (sharing at least a door width of wall with
   it) are joined one at a time, nearest first, by the shortest path from the room's walls to any network vertex
   (Takahashi-Matsuyama's step, a multi-source Dijkstra from the network); spurs take the secondary width (1.2 m
   in BB103 for a corridor to one or two rooms). "All legs" instead keeps every leg edge at the secondary width.
6. *Entrance.* The entrance (topic 10, or the user's) is a terminal: the network must reach it; its stub to the
   facade is the shortest path from the network to the entrance point on the exterior wall.
7. *Loops versus dead ends.* The union of leg routes may already form loops (two paths using two sides of a block
   of rooms). Spurs make dead ends. Report each dead end's length; where a dead end is longer than a limit (a
   registry value: building codes cap dead-end corridors; the figures were not read here, U), close it by the
   shortest path from its end to another network vertex not on its own spur. Anthropocity's "loops round blocks
   with short stubs to the facade" is this union-of-routes behaviour (inference from their description, S).
8. *Geometry.* Each corridor edge becomes a band of its width centred on, or offset to one side of, the wall line,
   cut out of the rooms it overlaps (Mirahmadi; Shiksha). Rooms lose area; the scorecard reports each room's
   deviation and the corridor share (layout-methods recommendation; Anthropocity's report).
9. *Problems in plain words* (feature 39): a leg with no wall route (graph disconnected), corridor pieces not
   joined to the rest, rooms without access and why (no wall long enough for a door), spur count and length,
   corridor area and share.

**Cost.** A bay grid of 500 rooms has a few thousand wall vertices; one Dijkstra with a binary heap is about
E log V, about 10^4 x 12 operations; 100 paths of 10 legs is 1 000 runs, about 10^8 operations at worst: up to a
second in a browser. Early exit at the target and a multi-source start cut this by an order of magnitude. At 10
to 100 rooms it is instant. The heap is about 40 lines of ES5.

**Failure modes.** Routes hug the walls of the first-placed rooms and so depend on the room layout: a bad room
order makes long corridors (inference); a corridor carved from a small room can make it unusable (Mirahmadi
filters such variants, P); greedy spurs are not the minimum total (2 - 2/l bound, S); paths through the facade
when the interior is blocked (cost factor, report it); multi-level paths need the stair first.

Level: P (Mirahmadi, NetworkX), S (KMB, Takahashi-Matsuyama as stated), U (Lopes). Confidence: medium.

### 2.6 Stair placement (feature 35)

**Sources read.** Hakimi 1964, "Optimum locations of switching centers and the absolute centers and medians of
a graph", Operations Research 12(3) 450-459: the abstract only, on RePEc (P for the abstract; the body
paywalled, not read). Kariv and Hakimi 1979, "An algorithmic approach to network location problems. I: the
p-centers", SIAM J. Appl. Math. 37(3) 513-538: its stated running times through a search summary only (U).

**What the published results say.** Hakimi generalised the graph centre and median vertex to the *absolute*
centre and median of a graph with weights on vertices and edges; he showed the optimum "switching centre"
(minimise the weighted sum of distances: the 1-median) is always at a vertex, while the best "police station"
(minimise the largest distance: the 1-centre) is not necessarily at a vertex (P, abstract). So for the median,
checking every vertex is exact; for the centre, the exact optimum may lie part-way along an edge, and
Kariv and Hakimi give polynomial algorithms for that (U for their bounds).

**Recommended method (inference, confidence high: small graphs make exhaustive search exact and simple).**
1. *Candidates*: corner vertices of the corridor network (a vertex where the corridor turns or branches), on
   which a stair footprint of the programme's size fits beside the corridor without cutting a room it may not
   cut, on every level (the stair is in the same place on every level). Typically 10 to 200 candidates.
2. *Demand*: for each room, a weight = the frequency-weighted number of path legs that start or end in it and
   change level (those legs must pass the stair). If no leg changes level, every room on an upper level weighs 1.
3. *Distances*: one Dijkstra from each candidate over the corridor network (plus walk-through rooms) gives its
   distance to each room's door.
4. *"Path priority" = weighted 1-median*: choose the candidate minimising the sum over rooms of weight x
   distance, summed over the levels. Exact among the candidates (Hakimi's vertex result means nothing better
   lies between vertices for an unconstrained median; here the candidates are the corners anyway).
5. *"Balance the worst leg" = 1-centre*: choose the candidate minimising the largest weighted distance to any
   room with demand. Restricting to corners may miss the absolute centre on an edge (Hakimi, P); the loss is at
   most half an edge length, which on a bay grid is half a bay. Report the worst leg's length.
6. *Ties*: smaller second criterion (centre's max for the median, median's sum for the centre), then the
   lowest candidate id.
7. *"How far it may move"*: a setting; candidates farther than this from the previous stair position (or from
   the stair node in the bubble diagram) are dropped, so edits do not throw the stair across the plan (feature 41).
Cost: C candidates x one Dijkstra (E log V): 200 x 10^4 x 12, about 2 x 10^7 operations; a few tens of ms.

**Failure modes.** No candidate fits (report it and offer the best corner with the overlap); the median pulls
the stair toward one heavy room and leaves a far wing a long walk (show both scores so the user can pick);
egress rules (travel distance to a stair, two stairs) are code checks the method does not make (U: figures not
read; registry data later).

Level: P (Hakimi's abstract), U (Kariv-Hakimi bounds), inference for the procedure. Confidence: high.

### 2.7 Bay grid and small-room clustering (features 32, 33, 41)

**Sources read.** Muther, RMA 1111 (P; topic 2): its last step, the *space* relationship diagram, is drawn on
gridded paper at a scale where one square is a fixed area, each activity drawn as a block of squares, and the
relationship lines kept between the blocks: the hand form of "rooms take whole grid cells, placed as the
bubble diagram says". The Concrete Centre, "Commercial" sector page (read 2026-11-16, P): its independent office
cost study priced six short-span options on a 9.0 x 7.5 m grid and two long-span options on 15.0 x 9.0 m, and
it names post-tensioned band beams as the economic choice above 12 m spans. Hua 2016 ("Irregular architectural
layout synthesis with graphical inputs", Automation in Construction 72:388-396): from its abstract through a
search summary (U), it works on irregular regions by subgraph matching and simulated annealing and is *not* a
grid method. Lopes et al. 2010 grow rooms on a grid (U; host unreachable, topic 5). Wu et al. 2018 and the
other layout methods: see `layout-methods.md` 2.4 and 5 (cited, not re-read).

**Published methods.** No paper found that clusters small rooms before giving them bays (two searches). Grid
growth (Lopes, U) and Muther's gridded space diagram (P) are the nearest. The method below is ours, built on
layout-methods' recommendation (bands, ordered slicing, consecutive small rooms sharing a bay) (inference).

**Recommended deterministic method (inference, confidence medium).**
1. *Bands and depth*: from the typology (layout-methods 5, step 1-2): room bands of depth d either side of a
   spine. The bay is the module along the band: width b. A room takes k whole bays, k = max(1, round(A / (b d))).
2. *Bay width*: the user's minimum bay width b_min (default 3.0 m, a project setting), per building. "Fit":
   b = b_min. "Auto-optimise": try every b from b_min to b_max (default 9.0 m: the upper end of the short-span
   office grid the Concrete Centre priced, P) in steps of the planning module (default 0.3 m) and keep the b
   with the least total absolute area deviation sum |k_i b d - A_i| / A_i; ties to the smaller b. At most 21
   values x n rooms: trivial. The span is shown against the 7.5 to 9 m range so a user sees a structurally
   odd grid (S: the range from the cost study's grid, not a design rule).
3. *Small-room clustering*: a room is small if A < t b d (t, the small-room threshold, default 0.6 of a bay).
   Visit small rooms in programme order; each joins the cluster of its most strongly linked small neighbour if
   that cluster has fewer than the maximum per cluster (default 3) and their total area fits in whole bays
   with less deviation than apart; else it starts a cluster. A cluster takes k bays like one room and is
   sliced inside (in depth when two, in width and depth when three: the ordered slicing of layout-methods),
   the deeper room flagged if it loses the corridor wall.
4. *Order along the bands*: "follow the bubble diagram": project each room's bubble position onto the band's
   axis and sort by it, splitting between the two bands by which side of the spine the bubble lies; otherwise
   the greedy adjacency order with swaps of layout-methods 5 (steps 3 and 6).
5. *Spare floor*: either rooms keep their k b d area and the remainder of the outline is reported as exterior
   space, or every room's bays are scaled up in proportion to fill the level (feature 33's two options).
6. *Stability*: once laid out, a change to one room moves only the rooms after it in its band (the order is
   kept unless the user asks to re-order), so the layout "does not reshuffle" (feature 41).
Size: about 200 to 300 lines of ES5 beside layout-methods' 300 to 400.

**Failure modes.** Rounding to whole bays inflates small rooms by up to 50 % of a bay (hence clustering); a
large b makes small rooms worse, a small b makes the structure odd; rooms needing a particular depth (a hall)
do not fit a single-depth band; non-rectangular outlines need cutting into rectangles first (layout-methods 5).

Level: P (Muther, Concrete Centre), U (Hua, Lopes), inference for the procedure. Confidence: medium.

### 2.8 Import of a programme sheet (feature 3)

**Sources read.** RFC 4180, "Common format and MIME type for CSV files" (October 2005, section 2, P). PKWARE
APPNOTE.TXT 6.3.10 (2022-11-01, P: the local header 0x04034b50, central directory 0x02014b50, end of central
directory 0x06054b50, general-purpose bit 3 (sizes in a data descriptor), method 8 = deflate). MDN
browser-compat-data `api/DecompressionStream.json` (main branch, read 2026-11-16, P): DecompressionStream since
Chrome 80, Firefox 113, Safari 16.4; the `deflate-raw` format since Chrome 103, Firefox 113, Safari 16.4.
SheetJS: cdn.sheetjs.com index (P: "SheetJS Community Edition ... licensed under the Apache 2.0 License";
it recommends vendoring), `xlsx-latest/package/package.json` (P: version 0.20.3, licence Apache-2.0), sizes
measured by download (P): `xlsx.full.min.js` 951 904 bytes, `xlsx.mini.min.js` 279 523 bytes; the npm registry's
`xlsx` is still 0.18.5 (P), i.e. current releases are distributed from SheetJS's own CDN, not npm. The git host
git.sheetjs.com asked for a sign-in for the raw licence file (not read there). pdf.js: npm `pdfjs-dist` latest
6.5.438, licence Apache-2.0 (P, registry), sizes by download from jsDelivr (P): `build/pdf.min.mjs` 474 284 and
`build/pdf.worker.min.mjs` 1 271 915 bytes (legacy build 537 769 + 1 327 591). SpreadsheetML cell structure
(ECMA-376 Part 1): from general knowledge, not re-read (S).

**The app today (P, read).** No ZIP reader and no CSV parser in `src/js/engine` (a CSV *writer* exists,
`structure/analysis-properties.js` `bimScheduleToCSV`; survey points accept delimited text in
`site/alignment-profile.js`). `io/file-save.js` `bimGunzip` already uses the browser's DecompressionStream for
gzip, so the same API with `deflate-raw` inflates ZIP entries with no library.

**CSV (recommended first; confidence high).** A state machine over characters per RFC 4180: fields separated
by commas; a field may be quoted; inside quotes, a doubled quote is a quote and commas and line breaks are
data; records end at CRLF (accept LF and CR too, as most files in practice); the last record may lack a line
break; an optional header row. Additions the RFC does not cover but real sheets need (inference): a leading
UTF-8 BOM to strip; semicolon or tab as separator (detect from the header: the most frequent of , ; tab outside
quotes); decimal commas in European exports (only if the separator is not a comma). About 60 lines of ES5.
Then a column mapper: guess columns by header names (name/room/space, area/m2/sqm, count/qty/copies,
floor/level, building, group/department), show the guess, let the user correct it; rows with no area become
buildings or group headings when the user says so (feature 2's row type).

**Excel .xlsx (recommended second, own code; confidence medium-high).** An .xlsx is a ZIP of XML parts.
Steps: find the end-of-central-directory record by scanning back from the end for 0x06054b50; read the
central directory (names, methods, compressed sizes, local header offsets: reading sizes here avoids bit 3's
data descriptors); for each needed part, skip the local header (30 bytes plus name and extra lengths) and
inflate method 8 with `DecompressionStream('deflate-raw')` (method 0 is stored, copy as is); parse the XML
with the browser's DOMParser. Parts: `xl/workbook.xml` (sheet names and relationship ids),
`xl/_rels/workbook.xml.rels` (sheet file paths), `xl/sharedStrings.xml` (the string table),
`xl/worksheets/sheetN.xml` (rows of cells; a cell's reference like C12, its type: shared string index, inline
string, boolean, error, or a number by default). Dates and merged cells are not needed for a programme sheet;
formulas are read from their cached value. Then the CSV path's column mapper. About 150 lines of ES5. Limits:
ZIP64 and encrypted workbooks refused with a message; the old binary .xls not supported (say "save as .xlsx
or CSV"). SheetJS (Apache-2.0, permitted by the rule) is the fallback if users need .xls or .ods: the mini build
is 280 KB, the full 952 KB, loaded on demand, vendored from cdn.sheetjs.com (not npm, which is stale).

**PDF tables (recommended last, or not at all; confidence medium).** pdf.js (Apache-2.0) can extract each text
run with its position, but a PDF has no table structure: columns must be inferred by clustering x positions
and rows by y, which fails on wrapped cells, merged headings and scanned pages (no text at all). Cost: about
1.75 MB of library (main plus worker), the largest library the app would load for one feature. Recommendation:
not now; the paste-in-text route (topic 10) covers a PDF brief: the user copies the table text from their
viewer and pastes it, and the CSV parser with a whitespace-column fallback reads it. Revisit if users ask.

Level: P. Confidence: high (CSV), medium-high (xlsx by own code), medium (PDF advice).

### 2.9 Export (feature 42)

**The app today (P, quick read).** DXF: `io/export-mappings.js` `bimBuildDXF` writes an ASCII DXF with a HEADER
($INSUNITS 6, metres), a LAYER table and ENTITIES of LWPOLYLINE, LINE and TEXT, using `bimDxfPair` and
`bimDxfLayerName` from `io/dxf-export.js`; lines are written at z = 0 and polylines without an elevation group.
SVG: `sheets/viewports.js` `bimExportSheetSVG` writes vector plan viewports with `bimEscXml`. PDF: the app prints
through the browser (program-to-plan part 8).

**Recommended (inference, confidence high).**
- *SVG, direct*: each view (bubble diagram, matrix, programme map, radar, layout) builds its own SVG string:
  circles and lines for the diagram (stroke width by link strength), rects and text for the matrix, polygons for
  the layout; units in metres with a viewBox, so it is to scale; escape text with `bimEscXml`. About 40 to 80
  lines per view.
- *PDF, vector*: open the SVG in a print view at the chosen paper size and scale and call the browser's print
  (the existing route); a scaled programme map states its scale in the drawing. No PDF library needed.
- *DXF with levels stacked*: reuse `bimBuildDXF`'s pair writer and layer table; write each level's room outlines
  as LWPOLYLINE with the level's elevation (group code 38, the polyline's elevation: S, DXF reference from
  general knowledge, not re-read) and, for "one file", stacked by floor height; or one file per level at
  elevation 0 (feature 42). Layer per level and per kind (rooms, corridors, walls, text). The app's own DXF
  importer can round-trip-check it as the V24 comment describes.

Level: P for what exists; S for group code 38. Confidence: high.

### 2.10 Offline stand-ins for the online AI features (features 4, 5, 22, 30, 31)

**Sources read.** NetworkX `algorithms/centrality/betweenness.py` (BSD-3-Clause, P): Brandes's algorithm as
code, with its notes (weights must be positive; float weights can miscount equal paths, so scale to integers;
undirected pairs counted once). Brandes 2001, "A faster algorithm for betweenness centrality", J. Math. Sociol.
25(2):163-177: the author's copy at uni-konstanz.de returned an HTML page, not the PDF (S, via NetworkX).
Decision 9 of `research-program-to-plan.md` part 11 (P): "AI suggested" means a rule set or relations pasted in as
text, marked suggested until approved.

**Betweenness (P via code).** For each source s: a BFS (or Dijkstra for weighted links) records the order nodes
are finished, each node's predecessors on shortest paths, and sigma, the number of shortest paths from s; then,
in reverse finishing order, each node w passes to each predecessor v the share sigma(v)/sigma(w) x (1 +
delta(w)); a node's betweenness is the sum of its delta over all sources. Cost O(n m) unweighted,
O(n m + n^2 log n) weighted: 500 rooms and 1 500 links, under a million steps. About 50 lines of ES5.

**Recommended heuristics (inference, confidence medium: these are rules the user reviews, not methods with a
published success rate; every output is marked "suggested").**
1. *Draft a programme from a description (feature 4).* Two routes, no model: (a) the pattern library (feature 5):
   programme templates as data (rooms, areas, groups, links) for common types, chosen by the user, with counts
   scaled ("3 bedrooms" sets the bedroom count); a small parser picks numbers next to known room words in the
   description and fills the template's counts; (b) paste-in text: the user pastes a list from any source
   (including an online assistant they choose to use), one room per line, "name, area, count, group", read by
   the CSV parser of topic 8 with a whitespace fallback.
2. *Suggest adjacencies (feature 22's sibling).* Topic 2's parameter similarity, plus template links when the
   programme came from a template, plus pasted lines "A - B, strength".
3. *Walk-through rooms guessed from the name (feature 30).* A word list per language held as data (lobby, foyer,
   hall, reception, waiting, atrium, circulation, concourse...): a room whose name contains one is "open", others
   "closed" unless set. Word list is ours; mark guesses.
4. *Suggest an entrance (feature 31).* In order: a room named as an entrance space (entrance, lobby, foyer,
   reception, by the word list); else the room with the highest betweenness on the adjacency graph among rooms
   that can reach the exterior wall (the room most paths pass through; Brandes); ties by hub score, then id. The
   entrance point is on that room's exterior wall, at the point nearest the site's access (the road or path from
   the site data when present), else the middle of its longest exterior wall. Rationale: a lobby is the node most
   routes cross (inference; space syntax measures depth from the outside, Hillier and Hanson 1984, not read: S).
5. *Suggest user paths (feature 31).* One path per user group the programme has (visitors, staff, service; from
   room groups): start at the entrance, then visit the group's rooms in breadth-first order over the adjacency
   graph from the entrance (depth first, then stronger link, then programme order), ending at the deepest room;
   frequency primary for the group with most area, secondary for the next, occasional for the rest. Each path
   is a draft the user edits. Coverage (feature 29) then shows the rooms no path reaches.
6. *Paste-in for paths*: lines "path name: room, room, room; frequency" parsed the same way.

Level: P (NetworkX code, decision 9), S (Brandes paper, Hillier and Hanson), inference for the rules.
Confidence: medium.


## 3. Feature table

Feature numbers are those of `anthropocity-features.md`. Line counts are estimates of the app's own ES5,
without UI.

| Features | Method | Source | ES5 lines (approx.) | Library |
|---|---|---|---|---|
| 10, 11, 12, 13, 41 | Force layout with pins, containment, settled state | FR 1991; d3-force 3.0.1 (ISC, read) | 300 | no |
| 14, 19 | Scaled circles/squares, target vs current area | arithmetic | 60 | no |
| 20, 21, 22 | Gower similarity, kNN + max spanning tree, strength bands | Gower 1971; von Luxburg 2007 | 150 | no |
| 23, 8 | Matrix with strengths 1-3, merged copies | Muther (A/E/I lines) | UI only | no |
| 25, 26 | Louvain with resolution, connectivity split, ignore bridges | Blondel 2008; R-B 2006; Traag 2019 | 150 | no |
| 26, 27 | Bridges and articulation points with piece sizes; hub score; centre and depth; aspect | Hopcroft-Tarjan via NetworkX; Hakimi | 150 | no |
| 28, 29 | Paths, coverage | data plus set arithmetic | 60 | no |
| 30 | Walk-through by name list | own word list | 30 | no |
| 32, 33 | Bands, bay width search, small-room clusters, slicing | Muther; layout-methods 5 | 250 (plus layout-methods' 300 to 400) | no |
| 34, 36, 39 | Wall graph, Dijkstra legs, spine threshold, spurs, loops, report | Mirahmadi-Shami 2012; KMB; T-M | 350 | no |
| 35 | Stair by 1-median or 1-centre | Hakimi 1964 | 100 | no |
| 37, 38 | Doors on corridor walls; wall thicknesses | geometry on the layout | 100 | no |
| 40 | Scorecard | layout-methods 2.5 | 60 | no |
| 3 | CSV import | RFC 4180 | 60 + mapper 80 | no |
| 3 | .xlsx import | APPNOTE 6.3.10; DecompressionStream | 150 | no (SheetJS Apache-2.0 only for .xls/.ods) |
| 3 | PDF tables | pdf.js text positions | not now | pdf.js Apache-2.0, about 1.75 MB, if ever |
| 4, 5, 31 | Templates, paste-in, entrance by name or betweenness, BFS paths | Brandes via NetworkX | 200 | no |
| 42 | SVG, PDF by print, DXF stacked | app's `bimBuildDXF`, `bimExportSheetSVG` | 150 | no |

## 4. Counter-evidence and failure modes

- **Force layouts are not optimisers with a guarantee.** FR call their termination "guesswork" and
  Kamada-Kawai's energy can trap a node in a local minimum (P, FR). The diagram is a suggestion; pins let the
  user override it. Bit-identical results across browsers are not guaranteed (Math.cos/sin are
  implementation-approximated: U); compare with tolerances.
- **Similarity is not adjacency** (topic 2): no published architectural method derives adjacency from room
  parameter similarity; the nearest practice (Muther) rates each pair directly with a reason. Generated links
  are a zoning hint and must stay "suggested".
- **Community detection on small graphs is unstable**: modularity has a resolution limit and many near-equal
  optima (S, U as cited); Louvain can produce disconnected communities (Traag et al.: up to 16 % in their tests,
  P). Fixed order makes runs repeatable, not "right".
- **Corridors cut rooms**: every corridor method read either shrinks rooms (Shiksha 2025; Mirahmadi) or needs
  them planned around it; program-to-plan's experiment found a corridor reaching every room costs about 20
  points of adjacency (P there). The router depends on the room layout it is given.
- **Greedy Steiner spurs are approximate** (within 2 - 2/l, S); a few metres of extra corridor are possible.
- **The 1-centre restricted to corners** can miss the absolute centre on an edge by up to half an edge (Hakimi,
  P abstract).
- **Bay rounding** inflates small rooms; clustering reduces but does not remove it. The 7.5 to 9 m span range is
  from one cost study's grid, not a design rule (P, Concrete Centre).
- **Own .xlsx reader**: files written by unusual tools (ZIP64, strict OOXML namespaces, encrypted) will fail; it
  must refuse with a clear message rather than misread.
- **Entrance and path heuristics** have no published success rate; their value is a starting draft.

## 5. Still open

- Eades 1984 and Kamada-Kawai 1989 not read in the original (S via FR); Eades's constants are S.
- Tarjan 1972/1974, KMB 1981, Takahashi-Matsuyama 1980, Brandes 2001, Kariv-Hakimi 1979: not read in the
  original (paywalled or refused); their methods were read as code in NetworkX (BSD) or through the citing text.
- Marson and Musse 2010 (both hosts returned a script challenge) and Lopes et al. 2010 (TU Delft hosts reset the
  connection) not read: their corridor steps are S (Mirahmadi's account) and U.
- Dead-end corridor and travel-distance limits for egress: figures not read; they belong in the standards
  registry with an edition before V236 uses them.
- DXF group code 38 for LWPOLYLINE elevation: from general knowledge (S); re-read in Autodesk's DXF reference
  before the work order.
- SheetJS's licence file on git.sheetjs.com needs a sign-in; the CDN index and package.json say Apache-2.0 (P).
- Whether ECMAScript's Math.sqrt is required to be correctly rounded: not re-read (U); matters only for
  cross-browser bit-identity, not for the method.
- No independent second reader re-checked the facts here.

## 6. Search log

| # | Date | Where | Query or URL | Result | Level |
|---|---|---|---|---|---|
| 1 | 11-16 | raw.githubusercontent.com | d3/d3-force main: src/simulation, link, manyBody, collide, x, radial, center, lcg, jiggle, LICENSE, package.json | read, ISC, 3.0.1 | P |
| 2 | 11-16 | web search | Fruchterman Reingold 1991 pdf | author copy reingold.co | - |
| 3 | 11-16 | reingold.co | force-directed.pdf | read (text extracted) | P |
| 4 | 11-16 | web search | Gower 1971 general coefficient of similarity pdf | JSTOR copy on mathematics.foi.hr; CRAN vignette | - |
| 5 | 11-16 | mathematics.foi.hr; CRAN mirror | Gower 1971; gower vignette | read | P; S |
| 6 | 11-16 | web search | space planning adjacency from room attribute similarity | no published method found | U |
| 7 | 11-16 | web search | Muther SLP relationship chart | RMA 1111 on richardmuther.com | - |
| 8 | 11-16 | richardmuther.com | RMA 1111 Procedure for Making Relationship Diagrams | read | P |
| 9 | 11-16 | arxiv.org | 0711.0189 (von Luxburg) | section 2.2 read | P |
| 10 | 11-16 | arxiv.org | 0803.0476, 1810.08473, cond-mat/0603718 | read in parts | P |
| 11 | 11-16 | raw.githubusercontent.com | vtraag/leidenalg LICENSE; CWTSLeiden/networkanalysis LICENSE | GPL-3.0; MIT | P |
| 12 | 11-16 | raw.githubusercontent.com | networkx: community/louvain.py, bridges.py, components/biconnected.py, approximation/steinertree.py, centrality/betweenness.py, LICENSE.txt | read | P |
| 13 | 11-16 | web search | Marson Musse 2010 pdf | Hindawi; arXiv 1211.5842 (Mirahmadi) | - |
| 14 | 11-16 | downloads.hindawi.com; onlinelibrary.wiley.com | Marson Musse PDF | script challenge page, not read | - |
| 15 | 11-16 | arxiv.org | 1211.5842 | section III.C read | P |
| 16 | 11-16 | web search | Lopes 2010 constrained growth corridor | summary: A* corridor | U |
| 17 | 11-16 | graphics.tudelft.nl; publications.graphics.tudelft.nl | Lopes 2010 PDF | connection reset twice | - |
| 18 | 11-16 | web search; ideas.repec.org | Hakimi 1964 | abstract read | P (abstract) |
| 19 | 11-16 | web search | Hua 2016 irregular layout | abstract summary: not a grid method | U |
| 20 | 11-16 | web search; ribaj.com (403); infoacier.be (404); concretecentre.com | typical column grid spans | Concrete Centre page read | P |
| 21 | 11-16 | rfc-editor.org | RFC 4180 | section 2 read | P |
| 22 | 11-16 | pkware.cachefly.net | APPNOTE.TXT 6.3.10 | signatures, bit 3, method 8 | P |
| 23 | 11-16 | raw.githubusercontent.com | mdn/browser-compat-data api/DecompressionStream.json | versions read | P |
| 24 | 11-16 | cdn.sheetjs.com; git.sheetjs.com; registry.npmjs.org | SheetJS licence, version, sizes | Apache-2.0, 0.20.3, sizes; git host wants sign-in | P |
| 25 | 11-16 | registry.npmjs.org; cdn.jsdelivr.net | pdfjs-dist latest, sizes | 6.5.438, Apache-2.0, sizes | P |
| 26 | 11-16 | uni-konstanz.de | Brandes 2001 PDF | HTML page, not the PDF | - |
| 27 | 11-16 | this repository | `io/export-mappings.js`, `io/dxf-export.js`, `io/file-save.js`, `sheets/viewports.js`, `simulation/traffic-sim.js` (grep and short reads) | DXF writer, gunzip, SVG export, seeded PRNG | P |

## 7. References

| # | What it is | URL | What was read | Date | Level |
|---|---|---|---|---|---|
| 1 | Fruchterman, Reingold 1991, Graph drawing by force-directed placement, SPE 21(11) | https://www.reingold.co/force-directed.pdf | history, figure 1, forces, frame, grid variant, cooling, complexity | 2026-11-16 | P |
| 2 | d3-force 3.0.1 (ISC) | https://github.com/d3/d3-force (raw files) | simulation, link, manyBody, collide, x, radial, lcg, jiggle, LICENSE | 2026-11-16 | P |
| 3 | Eades 1984; Kamada, Kawai 1989 | via ref. 1 | FR's account | 2026-11-16 | S |
| 4 | Gower 1971, Biometrics 27(4) 857-871 | https://mathematics.foi.hr/Rprojekti/BDP%20concept/Gover_metric.pdf | sections 1, 2, 4 | 2026-11-16 | P |
| 5 | van der Loo, gower package vignette, 2024 | https://mirror.linux.duke.edu/cran/web/packages/gower/vignettes/intro.pdf | section 1 | 2026-11-16 | S |
| 6 | von Luxburg 2007, A tutorial on spectral clustering | https://arxiv.org/abs/0711.0189 | section 2.2 | 2026-11-16 | P |
| 7 | Richard Muther & Associates, RMA 1111, Procedure for making relationship diagrams (2002) | https://richardmuther.com/wp-content/uploads/2014/06/RMA%201111%20Procedure%20for%20Making%20Relationship%20Diagram.pdf | all 4 pages | 2026-11-16 | P |
| 8 | Blondel et al. 2008, Fast unfolding of communities | https://arxiv.org/abs/0803.0476 | method, equation 2 | 2026-11-16 | P |
| 9 | Traag, Waltman, van Eck 2019, From Louvain to Leiden | https://arxiv.org/abs/1810.08473 | introduction, section II, refinement, theta | 2026-11-16 | P |
| 10 | Reichardt, Bornholdt 2006, Statistical mechanics of community detection | https://arxiv.org/abs/cond-mat/0603718 | the gamma null model | 2026-11-16 | P |
| 11 | leidenalg (GPL-3.0); CWTS networkanalysis (MIT) | https://github.com/vtraag/leidenalg ; https://github.com/CWTSLeiden/networkanalysis | LICENSE files | 2026-11-16 | P |
| 12 | NetworkX (BSD-3-Clause): louvain.py, bridges.py, biconnected.py, steinertree.py, betweenness.py | https://github.com/networkx/networkx | functions named in the text | 2026-11-16 | P |
| 13 | Hopcroft, Tarjan 1973; Tarjan 1972, 1974 | via ref. 12 | cited | - | S |
| 14 | Kou, Markowsky, Berman 1981; Mehlhorn 1988; Takahashi, Matsuyama 1980 | via ref. 12 | cited | - | S |
| 15 | Mirahmadi, Shami 2012, A novel algorithm for real-time procedural generation of building floor plans | https://arxiv.org/abs/1211.5842 | section III.C | 2026-11-16 | P |
| 16 | Shiksha et al. 2025, Automated generation of circulations within a floorplan, AI EDAM 39 e9 | see `layout-methods.md` ref. 6 | cited | 2026-11-16 | P there |
| 17 | Marson, Musse 2010, IJCGT, doi 10.1155/2010/624817 | https://doi.org/10.1155/2010/624817 | not reached | - | S (via 15) |
| 18 | Lopes et al. 2010, A constrained growth method for procedural floor plan generation | https://graphics.tudelft.nl/~rafa/myPapers/bidarra.GAMEON10.pdf | not reached | - | U |
| 19 | Hakimi 1964, Operations Research 12(3) 450-459 | https://ideas.repec.org/a/inm/oropre/v12y1964i3p450-459.html | abstract | 2026-11-16 | P (abstract) |
| 20 | Kariv, Hakimi 1979, SIAM J. Appl. Math. 37(3) | search summary | running times | - | U |
| 21 | Hua 2016, Automation in Construction 72 | search summary | abstract | - | U |
| 22 | The Concrete Centre, Commercial sector page | https://www.concretecentre.com/Sectors/Building-Sectors/Commercial.aspx | cost study grids, band beams | 2026-11-16 | P |
| 23 | RFC 4180 | https://www.rfc-editor.org/rfc/rfc4180.txt | section 2 | 2026-11-16 | P |
| 24 | PKWARE APPNOTE.TXT 6.3.10 | https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT | headers, bit 3, method 8 | 2026-11-16 | P |
| 25 | MDN browser-compat-data, DecompressionStream | https://github.com/mdn/browser-compat-data/blob/main/api/DecompressionStream.json | versions | 2026-11-16 | P |
| 26 | SheetJS Community Edition 0.20.3 (Apache-2.0) | https://cdn.sheetjs.com/ | index, package.json, build sizes | 2026-11-16 | P |
| 27 | pdfjs-dist 6.5.438 (Apache-2.0) | https://www.npmjs.com/package/pdfjs-dist ; jsDelivr | registry entry, build sizes | 2026-11-16 | P |
| 28 | Brandes 2001, J. Math. Sociol. 25(2) | https://doi.org/10.1080/0022250X.2001.9990249 | not reached; code in ref. 12 | - | S |
| 29 | This app: `src/js/engine/io/export-mappings.js` (`bimBuildDXF`), `io/dxf-export.js`, `io/file-save.js` (`bimGunzip`), `sheets/viewports.js` (`bimExportSheetSVG`), `simulation/traffic-sim.js` (`bimTrRng`) | repository | short reads | 2026-11-16 | P |
| 30 | `layout-methods.md` and `research-program-to-plan.md` (this round) | repository | parts cited | 2026-11-16 | P |
