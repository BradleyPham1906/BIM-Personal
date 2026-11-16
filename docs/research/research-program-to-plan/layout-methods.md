# Layout methods for schematic space planning (H2, H3, H4)

Started 2026-11-16. Part of `research-program-to-plan`. Evidence levels: P (source read here), S (dependable
secondary or a vendor's own claim), U (search summary only). Already covered elsewhere and only cited here:
squarified treemaps (Bruls 2000), Marson and Musse 2010, Merrell 2010, Weber 2022 review, GPLAN's graph
conditions (`../research-algorithmic-design/grammars-and-layout.md`, F10 to F12).

## 1. Summary

| # | Finding | Level | Confidence |
|---|---|---|---|
| L1 | Slicing floorplans (Wong and Liu, VLSI) honour areas exactly with aspect-ratio bounds inside a rectangle; their objective is wire length between centres, so they never guarantee a shared wall; 15 to 40 modules took 1 to 13 CPU minutes by annealing in 1989. | P | high |
| L2 | Ordered (pivot) treemaps keep items consecutive in a given order near each other, only approximately. Ordering a programme by its adjacency graph before slicing is the cheapest adjacency-aware layout. | P (paper); inference (transfer) | high / medium |
| L3 | A rectangular dual exists only for a biconnected planar triangulated graph with at most four corner-implying paths and no separating triangle; GPLAN otherwise adds and merges rooms (non-rectangular rooms). Duals keep every requested adjacency but impose extra ones and say nothing about areas. | P via GPLAN; S for Kozminski-Kinnen and Bhasker-Sahni | high |
| L4 | Shekhawat's group dimensions duals by LP from minimum widths and aspect ranges (plot minimised, areas not targets) and, in 2025, inserts corridors deterministically from a circulation graph built from the entrance edge; corridors shrink rooms, and minimal circulation is an NP-hard set cover solved greedily. Code is said to be on GitHub; it could not be reached. | P | high (method) / low (code) |
| L5 | Practice budgets circulation at 20 to 25 % of net for schools (BB103), 28 to 38 % of usable for offices (GSA 2012), 1.20 to 1.60 department factors for health (DoD 2018); corridors 1.8 m main, 1.2 m short (BB103). | P | high |
| L6 | Of the products reached, only Anthropocity documents programme-to-plan with corridors: rooms on a bay grid, corridors routed along walls from ordered "user paths", a spine width where several paths share a wall, open rooms walkable, and per-layout reports of area deviation, corridor share and unreached rooms; it calls the result "a planning aid". Other vendors state no method and no satisfaction rate. | S (vendor docs) | medium |
| L7 | MIQP (Wu 2018): 9 to 13 s per house, 72 to 79 s for 125 to 138 rooms, all shown layouts meeting constraints; needs a solver. CP (Medjdoub and Yannou 2000): complete enumeration of topologies, 10 rooms, needs a CP package. EPSAP (Rodrigues 2013): penalty-weighted evolution, union-of-rectangles boundary. SQP (Michalek 2002): local optimum in seconds from the user's rough placement. | P (Wu from the supplement) | medium-high |
| L8 | Lobos and Donath (2010): no generator was in daily use by architects; a 1998 product made fast layouts that practice rejected for leftover space. | P | high (for 2010) |
| L9 | Our run (one 12-space programme): ordered slicing + deterministic swaps met 10/13 required adjacencies (77 %) with exact areas in 8 ms; a double-loaded spine met 5/13 by wall (9/13 with the waiting room open), spent 13 % of gross on the corridor, and reached every room. | P (measured here, one case) | low-medium |

Recommendation (inference): a deterministic spine-and-bands slicing layout, ordered by the adjacency graph,
improved by pair swaps, with open rooms counted as circulation and every score reported; leave out duals, solvers,
stochastic and learned methods for the first phase (section 5).

## 2. Findings by topic

### 2.1 Slicing and treemap layouts beyond squarified

**Slicing floorplans (VLSI).** Wong and Liu (Algorithmica 1989, the journal version of their DAC 1986 paper;
read: abstract, sections 1, 2.1-2.6, Table 1) define a slicing floorplan as one obtained by recursively cutting
a rectangle in two by a vertical or horizontal line, represented by a slicing tree; a skewed slicing tree is in
one-to-one correspondence with a normalized Polish expression of length 2n-1 (P). The search is simulated
annealing over three moves: M1 swap two adjacent operands, M2 complement a chain of operators, M3 swap an
adjacent operand and operator (accepted only if the result stays normalized) (P). The cost is A + lambda W
(bounding area plus weighted wire length between module centres): an adjacency-like term, but as a distance,
not as a shared wall (P). Modules are "flexible": each has an area and an allowed aspect-ratio range, so
areas are honoured exactly and shapes are bounded (P). Reported: 15 to 40 modules, 1 CPU minute (15) to 13 CPU
minutes (40) on a 1980s Pyramid machine in Pascal; final area within about 0.5 to 4 percent of the sum of
module areas (Table 1: e.g. P2, 20 modules, 198.88 total, 202.17 final) (P). Wong and Liu also note that an
annealing schedule (cooling ratio 0.85, about 7n moves per temperature) and a stop when fewer than 5 percent
of moves are accepted worked for them (P). Confidence high. Otten 1982 ("Automatic floorplan design", DAC 1982)
was not read; Wong and Liu cite it among the floorplanning works they build on (P for the citation, U for its content).

What slicing guarantees: every module is a rectangle; with flexible modules, areas are exact; the outline is a
rectangle; and evaluation of a given tree is linear in n (P for Wong and Liu's shape-curve evaluation;
"linear" is our reading of their incremental cost section). What it cannot: a shared wall between two given
modules (wire length only pulls centres together); any circulation; a non-rectangular outline (the paper's
L-shaped *modules* are allowed in its part 2, but the envelope stays a rectangle) (P). Every rectangular
layout that is sliceable is also "one-sided", and one-sided layouts are area-universal: any assignment of
areas can be realised with the same adjacencies (Eppstein, Mumford, Speckmann, Verbeek 2009, abstract, P; the
step "sliceable implies one-sided" is our inference from the definitions, confidence medium).

**Ordered treemaps.** Shneiderman and Wattenberg 2001 (read: whole, 6 pages) introduce ordered ("pivot")
treemaps: items near each other in a given order are placed near each other in the layout, with aspect ratios
far lower than slice-and-dice and somewhat worse than squarified (P). The pivot algorithm takes the largest
(pivot-by-size) or the middle (pivot-by-split-size) item as a pivot and splits the rest into three ordered
lists around it, recursively (P). The guarantee is approximate ("roughly preserve order"), not adjacency (P).
For space planning this is the useful variant: if the programme is first ordered so that related spaces are
consecutive (for example along a path through the adjacency graph), an ordered treemap keeps most consecutive
pairs touching. That is inference; it is what H2 proposes to measure. Confidence: high for the paper's
claims, low for the transfer.

**Applied to architecture.** Knecht and Koenig 2010 (GA2010, "Generating floor plan layouts with k-d trees
and evolutionary algorithms") subdivide a rectangle with a k-d tree (a slicing structure) and evolve it; the
proceedings PDF returned 404 here and the Weimar repository reset the connection, so only the title and
abstract-level description are known (U). Marson and Musse 2010 (treemap plus a corridor step) and Mirahmadi
and Shami 2012 are in grammars-and-layout.md (F11). Weber, Mueller, Reinhart 2022 count subdivision among 27
top-down methods (F10). The VLSI literature's slicing tree is the same object as an architectural "split" or
"subdivision" plan: our observation, confidence high.

### 2.2 Rectangular dualisation and graph methods

**The existence conditions.** A rectangular dual (every room a rectangle, the union a rectangle, two rooms share
a wall exactly when the graph has an edge) exists for a biconnected planar graph whose interior faces are
triangles (a PTPG) if and only if it has no more than four corner-implying paths; it does not exist when the
graph has a separating triangle or a triangular exterior face (GPLAN paper, Shekhawat et al., arXiv 2008.01803,
Theorem 1 and section 3.4, P; the theorem is Kozminski and Kinnen 1985 and Bhasker and Sahni 1987/1988 as
cited there, S, those papers were not read). Bhasker and Sahni give linear-time algorithms to test for and
construct a rectangular dual (title-level, through GPLAN's reference list, S). Kant and He's construction uses a
regular edge labelling after adding four poles N, E, S, W (P through GPLAN section 3.3). Confidence high.

**What happens when the graph is not a PTPG.** GPLAN adds extra vertices so that the modified graph has at most
four corner-implying paths and no separating triangle, builds a rectangular floorplan for that graph, and then
merges the extra rooms into neighbours, giving an orthogonal (L-, T-shaped rooms) floorplan, "OFP" (P, sec.
3.4). A planar graph that is not triangulated must first be triangulated: the user's adjacency list is
completed with extra adjacencies (P, GPLAN sec. 3; Shiksha et al. 2025 take a PTPG as input, P). Consequence
for a programme: required adjacencies are kept, but a rectangular dual also *imposes* adjacencies the brief did
not ask for, and a forbidden adjacency is honoured only if the triangulation step avoids that edge. That is
inference, confidence medium-high. A non-planar requirement graph (e.g. K5 among five spaces) has no solution at
all with shared walls; it must be weakened (standard graph theory; inference).

**Dimensions.** Upasani, Shekhawat, Sachdeva (arXiv 1910.00081, "Automated Generation of Dimensioned Rectangular
Floorplans"; read: abstract, sec. 1, 3.4, 4, 5) dimension a given dimensionless rectangular arrangement by
linear programming on two flow networks (one for widths, one for heights), with each room's *minimum width* and
*aspect-ratio range* as constraints; it minimises total width, then height, and repeats while an aspect ratio is
out of range (P). Target *areas* are not inputs: area follows from width and aspect ratio (P). The plot size is
an output (minimised), not a fixed boundary (P). Implementation: MATLAB R2018a with a simplex solver, "a few
seconds" (P). GPLAN (Python) claims "a feasible dimensioned layout for any given dimensions" and enumerates: 1300
topologically distinct floorplans over 154 boundaries in 282 s for its Figure 15 graph; 256 OFPs in 26.6 s for
another (P, sec. 3.5). Confidence high for what is reported; no failure rate is reported.

**Corridors.** Shiksha, Anand, Shekhawat, Agrawal 2025, "Automated generation of circulations within a
floorplan", AI EDAM 39 e9 (open access, CC BY 4.0; read: abstract, method sections, limitations, conclusion,
P). Input: a PTPG or an existing floorplan, one entrance assumed (P). Algorithm 1 builds a circulation graph by
subdividing edges of the PTPG with "corridor vertices", starting at an exterior edge that becomes the entrance;
Algorithm 2 inserts each corridor into the floorplan by *shifting walls* between the two rooms it joins, using
shift tables so no gaps open (P). The result, "spanning circulation", reaches every room but is redundant;
Algorithm 5 removes corridors as a minimum set-cover problem solved greedily (NP-hard, so the result may be
sub-optimal, as the authors show in their Figure 16) (P); Algorithm 6 keeps corridors only around rooms marked
private and lets public rooms serve as passage (P). Stated limits: no building codes or accessibility rules; 2D,
one storey; in "minimal circulation" rooms made public get several doors and lose privacy, needing manual fixes;
future work includes non-rectangular rooms and dimensional constraints together with circulation (P). The
corridor is cut out of the rooms by shifting walls, so room areas shrink by the corridor area; the paper treats
smaller rooms as the cost of corridors (P). Code: the paper links github.com/GPLAN-team/Circulation_Paper; from
here the repository could not be reached (GitHub refused unauthenticated access and the session could not
attach it), so its licence, language beyond "Python" (P from the paper) and size are unknown. GPLAN's own code
location and licence were not found (open). Confidence high for the method, low for code availability.

**Further from the same group (not read, U):** Bisht et al. 2022 (G2PLAN, dimensioned floorplans by graph
theory and optimisation, per Shiksha 2025's table); Lohani and Shekhawat 2026, "DPLAN: minimal connectivity to
floorplan generation" (arXiv 2606.21159; search summary says it supports rectangular plots only).

### 2.3 Corridor-first and typology-driven methods; products

**Organisations, as practice names them.** Ching, *Architecture: Form, Space and Order*, chapter 4
"Organization" (a course copy hosted by the University of Oregon; read: the chapter's opening and its list of
types, P): five spatial organisations: centralised (a dominant central space with secondary spaces grouped
round it), linear (a sequence of repeated spaces), radial (a central space from which linear organisations
extend), clustered (spaces grouped by proximity or a shared trait), grid (spaces within the field of a
structural or other grid). Ching notes that circulation in a centralised organisation may be radial, loop or
spiral (P). The words "double-loaded", "single-loaded", "spine" and "racetrack" are not Ching's categories;
they are corridor configurations inside a linear (spine, single/double loaded) or a centralised or grid
(racetrack: a loop corridor round a core) organisation. That mapping is our inference, confidence medium.

**Net-to-gross and corridor share, with sources.**

| Source | Building type | Figure | Level |
|---|---|---|---|
| UK DfE, Building Bulletin 103, Area guidelines for mainstream schools (2014), "Circulation, plant and internal walls" | primary school | circulation at least 22.5 % of total net area (20 % single-storey) | P |
| same | secondary school | circulation at least 25 % of net area; corridors serving more than one or two teaching rooms at least 1.8 m clear (2.55 m with lockers); short corridors to one or two small spaces at least 1.2 m; a 1.2 m strip is discounted where the route passes through a room | P |
| same | schools | internal walls 4 to 6 % of net area; plant 1.5 to 3.5 % | P |
| GSA-commissioned "Circulation: Defining and Planning" (11 May 2012, on WBDG) | federal offices | circulation multiplier on net area 1.4 to 1.6 (average 1.5); circulation factor (circulation / usable) 28 to 38 % (average 33 %); 1.4 for mostly enclosed offices, 1.6 for open plan or irregular floor plates; a multiplier of 1.35 gives a factor of only 25.9 % | P |
| US DoD Space Planning Criteria, Chapter 130 Net to Gross Conversion Factors (1 July 2018, on WBDG) | health facilities | department gross factors 1.20 (common areas) to 1.60 (surgery), e.g. 1.35 to 1.40 for clinics, 1.50 nursing units; building grossing factors on top, 1.35 (clinic) to 1.41 (medical centre) | P |

A worked geometry (inference, arithmetic only): a bar with rooms d deep and a corridor c wide spends c / (2d + c)
of its floor on the corridor if double-loaded and c / (d + c) if single-loaded; with d = 6 m and c = 1.8 m that is
13 % against 23 %. These shares sit inside the 20 to 38 % ranges above, which also include lobbies, stairs and
cross-corridors. So a generator for a school, clinic or office should expect roughly a fifth to a third of the net
area as circulation, and should report it.

**Generators built on them (vendor claims: level S at best).**

| Product | What it says it generates | From what | Corridors | What it says it does not do |
|---|---|---|---|---|
| Anthropocity (anthropocity.com/docs, 11 pages read 2026-11-16) | "Layout view" turns the bubble diagram into a schematic plan per level: scaled room shapes in each building, corridors, a stair, entrances, doors | buildings, rooms with sizes and copies, adjacencies (matrix, or derived from weighted room parameters), building outlines on a map; programme sheets PDF/CSV/Excel parsed; AI drafts optional (account) | not drawn by hand: routed from "user paths" (ordered room sequences per user type, hand-made or AI-suggested); corridors run along walls, form loops round blocks of rooms with short stubs to the facade; a wall walked by at least N paths ("spine threshold") gets the main corridor width; option "Spine + access" (spine plus shortest spur to every other room) or "All legs"; corridors do not cross rooms unless allowed; open rooms (lobby, waiting) can be walked through | "a planning aid ... not a construction drawing"; rooms are rectangles except at corridor elbows or the stair; rooms fit a bay grid (minimum bay width; small rooms cluster before competing for a bay); either rooms keep programmed area and spare floor is drawn outside the walls, or rooms grow proportionally to fill the level; reports per layout the share of floor filled by programme, the corridor share, the area deviation per room (e.g. "+20%"), and named failures ("No wall route", "No access" with a reason, stray corridor pieces) |
| Finch3D (finch3d.com, home page) | floor plans, area calculations, BIM geometry; residential, office test fits "from a brief", high-rise, master plan | the firm's standards and local codes | not stated | no limits stated |
| TestFit (testfit.io, home page) | site plans, parking, massing and yield for multifamily, hotel, industrial and other typologies | parcel, typology, zoning, unit mix, parking ratios | building corridors not claimed on the page | plan is a starting point to edit |
| Maket (maket.ai, home page) | residential floor plans, several options, in about 2 to 3 minutes | room list, target area, house shape, plain-language priorities | not stated | residential only; adjacencies and site boundary not mentioned as inputs; designs to be checked by a licensed professional |
| Architechtures (architechtures.com, home page) | residential developments: building geometry, unit programme, net and gross areas, parking, cost | min/max net areas per room and typology, minimum room dimensions, vertical circulation settings, user-drawn volumes | not stated on the page | "standardized initial BIM model" at LOD 200+; details added later |
| Hypar (HyparSpace repository README, P; docs pages returned 404) | open-source C# functions: "Space Planning" and "Circulation" produce space boundaries from building geometry; layout functions furnish them | building geometry | per search summary (U), corridors are drawn by the user and split the floor into spaces, which are then assigned programme | licence of the repository not found (LICENSE 404) |
| Autodesk Forma (Spacemaker) | product page refused the request (403); not reached | | | (U) |

Reading of the table (inference, confidence medium): only Anthropocity, among those reached, documents how it
goes from a programme with adjacencies to rooms with corridors, and it does it corridor-from-paths on a bay grid,
with honest per-layout reporting of area deviation and corridor share. The multifamily tools (TestFit,
Architechtures, Finch) work from a typology (unit bars on a corridor), not from an adjacency graph. None of the
vendors states a constraint-satisfaction rate.

### 2.4 Optimisation formulations

**Mixed-integer (MIQP).** Wu, Fan, Liu, Wonka 2018, "MIQP-based layout design for building interiors",
Computer Graphics Forum 37(2) (Eurographics). The main paper PDF (author's site) refused the request (406) and was
too large for the fetch tool; the diglib record refused (403). Read instead: the authors' supplementary material
(2 pages, P). What it shows: rooms are axis-aligned rectangles with position and size variables (x, y, w, d);
a hierarchical scheme splits a room into children with "refinement" constraints bounded by a range delta (P);
inputs per room are a size target, width and depth bounds, an aspect-ratio bound, and whether the room touches the
boundary; inside and non-overlap constraints are always on; the corridor is itself a room with width and depth
bounds (e.g. corridor depth 0.59 to 1.76 m in their Figure 1 example) (P). It returns several layouts meeting all
constraints for the same input, handles boundaries of different complexity (Figure 3, nine single-storey
houses), two-storey houses, and large plans: 125 to 138 rooms with 250 to 280 constraints in 72 to 79 s (supermarket,
office, mall) (P). Against Merrell 2010's stochastic method on the same houses: 9.3 to 12.8 s against 54 to 99.5 s,
with the stochastic results leaving uncovered (red) regions (P). The solver library is not named in what was read
(U: the paper is reported elsewhere to use Gurobi). A commercial or open MIQP solver is required; none fits an ES5
one-file build. Confidence: high for the supplement's numbers, medium for what the main paper adds.

**Constraint programming.** Medjdoub and Yannou 2000, "Separating topology and geometry in space planning",
Computer-Aided Design 32(1) (arXiv 1303.4017 author copy, 32 pages; read: abstract, sec. 1, 3.1.2, 4, 5, Table 2,
P). ARCHiPLAN first enumerates "topological solutions" (relative positions: adjacency and non-overlap variables,
orientation on the contour N/E/S/W) with arc-consistency and a most-constrained-space-first heuristic, then for
each one finds the optimal geometry by branch and bound on a weighted cost (P). It is built on "a constraint
programming package" (P; the package's name was not in the parts read). Sizes and times (Table 2, time unit not
restated in that table, presumably seconds): 4 to 10 rooms; the 10-space one-family dwelling (Maculet problem, a
fixed contour) has 345 potential and 72 consistent topological solutions, 3245 to enumerate all, 0.2 to find the
first or best geometry for one topology (P). The authors say the number of topological solutions stays at "ten to
one hundred" even for "practical size (20 rooms)" (P, their claim). Corridors: in an early version a corridor was
one rectangle; they added two-rectangle (L) corridors as two adjacent rectangles with a special constraint (P).
They also note that evolutionary approaches of the time handled "up to 20 spaces and several floors" with
sub-optimal results (P, their reading of Damski and Gero 1997 and others). Deterministic: yes (complete
enumeration). Needs: a CP solver. Confidence high.

**Evolutionary.** Rodrigues, Gaspar, Gomes 2013, "An evolutionary strategy enhanced with a local search technique
for the space allocation problem in architecture, Part 1: methodology", Computer-Aided Design 45(5) (University of
Coimbra repository preprint; read: abstract, sec. 1 to 3, evaluators, P). EPSAP couples an evolution strategy with
stochastic hill climbing; the cost is a weighted sum of penalties: connectivity/adjacency (distance until the
shared wall is long enough for a door), space overlap, openings overlap and orientation, floor dimensions (min
and max area and side), compactness (empty area inside the boundary, or inside the bounding rectangle when no
boundary is given) and overflow outside a polygonal boundary made of rectangles (P). A 9-space house with one
exterior door and one window per space has 56 variables (P). Rectangular rooms only; non-convex (L) spaces absent
(P, their own statement about the field, which applies to EPSAP too). Run times and success rates are in Part 2,
which was not read (open). Not deterministic. Confidence high for the formulation.

Guo and Li 2017, "Evolutionary approach for spatial architecture layout design enhanced by an agent-based topology
finding system", Frontiers of Architectural Research 6(1): a multi-agent step finds a topology first, which
narrows the evolutionary search (S, abstract through a search summary and the DOI record; the full text was
refused by the publisher's API with a rate limit). Sizes and times not reached (open).

**Physics / force-directed.** Arvin and House 1999/2002, "Modeling architectural design objectives in physically
based space planning" (ACADIA 1999 pp. 212-225; Automation in Construction 11(2) 2002): topological objectives
(adjacency, orientation) are forces on space locations; geometric objectives (area, proportion, alignment) are
forces on boundary edges; a dynamic simulation pushes rooms into place (P for the 1999 abstract; S for the
springs-and-dampers description through Michalek and Papalambros 2002). The dissertation PDF (Texas A&M) refused
the request (403); sizes and times not reached. Michalek and Papalambros 2002, "Interactive design optimization of
architectural layouts", Engineering Optimization 34(5) (read: whole, P): rooms, halls and "accessways" are
objects; the designer sketches and roughly places rooms, then a sequential quadratic programming solver (CFSQP, a C
library) compacts the geometry to a *local* optimum in "a few seconds" for a two-bedroom apartment; a whole
session takes about one to ten minutes; gradient methods need smooth functions (P). Lesson: force or gradient
methods give a good local fit from a good start, and they depend on that start; they do not by themselves decide
topology. That is the authors' framing (P) and our inference for force methods generally (medium).

**What the app already has** (repository read, P): V179's spec (docs/work-orders/v179/SPEC.md, part 1) queues a
bubble diagram that draws the programme as circles sized by area with lines by relation, coloured by status; it
does not say how the circles are placed. A force layout there would be the natural seed for any of the methods
above (inference).

### 2.5 Measures

| Measure | Definition, as the source gives it | Source | Level |
|---|---|---|---|
| Adjacency (door) satisfaction | a required connection counts as met only when the two rooms share a wall segment long enough for a door; cost Ca = number of missing connections + number of enclosed entrances, patios, garages | Merrell, Schkufza, Koltun 2010, sec. 5.2 | P |
| Adjacency as distance | penalty grows with the gap until the shared side reaches the minimal length for an interior door (connectivity) or contact (adjacency), per a matrix Mcon (1 = connectivity, 2 = adjacency) | Rodrigues, Gaspar, Gomes 2013, connectivity/adjacency evaluator | P |
| Adjacency as wire length | W = sum over pairs of c_ij * d_ij, d_ij the distance between module centres; cost A + lambda W | Wong and Liu 1989, sec. 1 | P |
| Area deviation | Merrell: minus the log-likelihood of each room's area and aspect ratio under learned distributions (Cd); EPSAP: penalty outside min/max area and sides; Anthropocity shows drawn area against programmed area as a signed percentage, e.g. "+20%" | Merrell 2010; Rodrigues 2013; Anthropocity docs | P, P, S |
| Aspect ratio | max(w/h, h/w), 1 for a square | Shneiderman and Wattenberg 2001; same in Bruls 2000 | P |
| Compactness | penalty for empty area inside the boundary (or inside the bounding rectangle when no boundary) | Rodrigues 2013 | P |
| Shape / convexity | penalty for deviation from convexity of each room | Merrell 2010 | P |
| Outline fit | area of the bounding rectangle against the sum of module areas | Wong and Liu 1989, Table 1 | P |
| Circulation multiplier and factor | CM = usable / net (1.##); CF = circulation / usable = (CM - 1) / CM, so 1.35 gives 25.9 % | GSA "Circulation: Defining and Planning" 2012 | P |
| Circulation share of net | circulation >= 22.5 % (primary), 20 % (single-storey primary), 25 % (secondary) of total net area | BB103 2014 | P |
| Circulation / usable ratio | named as a rational criterion "to keep most of the surface for use" | Lobos and Donath 2010, criterion (vi) | P |
| Corridor reach | every room on a circulation route (BB103: all rooms except stores off learning spaces); Anthropocity: coverage "12/14 rooms" on paths, and "No access" lists rooms no corridor reaches | BB103; Anthropocity | P; S |
| Plan fill | share of the floor the programme fills; corridor share of the floor | Anthropocity layout view | S |

A score the app could compute for any generated plan, assembled from the rows above (inference, not one
paper's formula): for n spaces with targets a_i and drawn areas A_i, area error max_i |A_i - a_i| / a_i;
required-adjacency satisfaction = met / required, "met" meaning a shared wall of at least a door width (Merrell's
rule) or a corridor-mediated connection, reported separately; forbidden adjacencies touched (a count, should be 0);
worst aspect ratio max_i max(w/h, h/w); circulation factor CF = corridor area / (net + corridor area); reach =
rooms with a door on a corridor or an open room / n; walking distance from the entrance to each room along the
corridor graph. Each is cheap to compute on rectangles.

### 2.6 Criticism and failure modes

- **Adoption.** Lobos and Donath 2010 (Arquiteturarevista 6(2), Redalyc copy; read: introduction, criteria,
  conclusions, commercial software review, P): despite decades of methods, architects "have nothing on our
  desks" that generates a useful floor plan; tools are not used "no matter how fast, optimal, automated, or
  parameterized"; only two research tools (Medjdoub and Yannou; Duarte) claim real use, "but no strong proof is
  shown"; half the approaches ignore the boundary; graphs are "seldom seen" (P, 2010 view). On products: Alberti
  (AcadGraph 1998) produced about a hundred solutions in seconds on real, also non-rectangular, boundaries but
  "never accepted in practice": non-artistic plans and many empty leftover spaces to fill the boundary;
  Vectorworks 10's Space Planning Tools (2004) only laid rooms out without overlap and the architect had to
  relocate them all by hand (P). Confidence high that this was the 2010 state; it predates the current products.
- **Rectangles.** Wong and Liu, Bruls, Merrell (rectilinear), Wu 2018 (rectangles), EPSAP (rectangles, "non-convex
  shapes absent"), GPLAN (rectangles unless orthogonal merges) all assume axis-aligned rectangles or unions of them
  (P each). A sloped or curved boundary is outside every method read.
- **The corridor costs area or adjacency.** Shiksha et al. 2025 cut the corridor out of the rooms by shifting walls
  (rooms shrink) and need a set-cover approximation to remove redundant corridors, which can stay sub-optimal (P);
  Mirahmadi and Shami 2012 say the treemap corridor step wastes space (already in F11, P). Anthropocity offers
  either area kept with spare floor outside the walls, or rooms grown to fill, i.e. area error (S).
- **Stochastic failure and time.** Merrell 2010 fails to satisfy accessibility in a share of runs (Figure 13 is
  "failure case: the accessibility term was not driven to zero", P; rates in F12). Wu 2018 shows Merrell's method
  leaving uncovered regions in 54 to 100 s against their 9 to 13 s (P, supplement).
- **Enumeration explodes.** GPLAN's enumeration gives 1300 layouts for one graph in 282 s, and its authors list
  "not feasible for the user/designer to go through each solution" as the first limitation (P). Medjdoub and
  Yannou needed 3245 (time units) to enumerate all topologies of a 10-space house (P).
- **Dimension methods ignore area targets.** Upasani et al. dimension from minimum widths and aspect ranges and
  minimise the plot; target areas are not inputs (P). For a fixed site boundary and fixed areas this is the wrong
  objective unless reformulated (inference).
- **Not reached:** Liggett 2000, "Automated facilities layout: past, present and future" (Automation in
  Construction 9(2) 197-215): no open copy found; only its bibliographic record (S). Its argument is not reported
  here.

## 3. Comparison table

| Family (source read) | Deterministic | Guarantees areas | Guarantees adjacencies | Makes a corridor | Non-rectangular boundary | Size and time reported | Needs a library | Fits a few hundred lines of ES5 |
|---|---|---|---|---|---|---|---|---|
| Squarified treemap (Bruls 2000; F11) | yes | yes, exact | no | no | no | trivial | no | yes (about 30 lines) |
| Ordered / pivot treemap (Shneiderman, Wattenberg 2001) | yes | yes, exact | no; order neighbours "near" | no | no | trivial | no | yes |
| Slicing tree + annealing (Wong, Liu 1986/1989) | no (annealing); a deterministic swap search is a variant (inference) | yes (flexible modules, aspect range) | no (wire length pulls centres) | no | no (rectangular envelope) | 15 to 40 modules, 1 to 13 CPU min (1980s) | no | yes (inference) |
| Ordered slicing + swap search (this note's experiment) | yes | yes, exact | no; 10/13 met on one 12-space case | no | no | 12 spaces, 8 ms in Node | no | yes (about 100 lines) |
| Rectangular dual (Kozminski-Kinnen, Bhasker-Sahni via GPLAN) | yes | no (topology only) | yes, every edge, if the graph is a PTPG; it also imposes extra adjacencies | no | rectangular outline; OFP rooms when merged | linear time to construct; GPLAN 256 to 1300 layouts in 27 to 282 s | no for the dual; LP for dimensions | dual: hard but possible (inference, several hundred lines with planarity and REL); not small |
| Dimensioning by LP (Upasani et al. 2020) | yes | no (min width and aspect range; plot minimised) | keeps the dual's | no | no | "a few seconds" (MATLAB) | LP solver | only with a hand-written simplex (inference) |
| Circulation insertion (Shiksha et al. 2025) | yes for spanning; greedy set cover for minimal | no (rooms shrink by the corridor) | keeps the dual's | yes: spanning, minimal, public/private | adaptable, shown on one non-rectangular example | complexity O(n^2) and similar; no timings read | no (Python, networkx-class graph code: inference) | possible after a dual exists (inference) |
| MIQP (Wu et al. 2018) | yes given the solver | within bounds | as constraints | corridor as a room with bounds | yes (polygonal domains from rectangles) | houses 9 to 13 s; 125 to 138 rooms 72 to 79 s | MIQP solver (U: Gurobi) | no |
| Constraint programming (Medjdoub, Yannou 2000) | yes (complete) | within bounds | yes, as constraints, with contour orientation | corridor as one or two rectangles | fixed contour (rectilinear) | 4 to 10 rooms; first geometry 0.1 to 0.2; all topologies of 10 rooms 3245 | CP solver | no (a small CP is possible but the enumeration grows fast; inference) |
| Evolutionary (Rodrigues 2013; Guo, Li 2017) | no | penalised | penalised | not in Part 1 | union of rectangles | Part 2 not read | no | yes in size, but not deterministic (seeded PRNG makes it repeatable; inference) |
| Bayesian + Metropolis (Merrell 2010; F12) | no | penalised | penalised; fails in a share of runs | no (halls as rooms) | rectilinear | seconds to 7 min | trained network | no |
| Physics / SQP (Arvin, House 1999/2002; Michalek, Papalambros 2002) | yes for a given start (local) | penalised | forces/penalties | halls as objects | not read | Michalek: a few seconds per apartment | SQP library (CFSQP, C) for Michalek; none for springs | springs: yes (inference) |
| Corridor-from-paths on a bay grid (Anthropocity docs) | not stated | optional: kept (spare floor outside) or grown to fill | not stated; reported | yes: routed along walls from user paths, loops, spine threshold | building outlines drawn on a map (shape support not stated) | not stated | not stated | unknown (closed product) |
| Spine, double-loaded (practice; this note's experiment) | yes | yes, exact | weak: 5/13 by wall, 9/13 if waiting is open | yes, by construction | no | 12 spaces, 2 ms | no | yes |

## 4. What bears on H2, H3, H4

**The experiment (E-layout, run here 2026-11-16, Node, the script in appendix A).** One programme of 12 spaces (a
small clinic, 194 m2 net: reception 30, waiting 40, four consult rooms 14, treatment 20, staff 18, office 12, two
WCs 5, store 8), 13 required adjacencies (6 of them to the waiting room), 2 forbidden. "Met" means a shared wall of
at least 1.0 m (Merrell's door rule). Deterministic: a greedy order from the entrance by links to placed spaces,
then best-improvement pair swaps until none improves (cost: -10 per met link, +30 per forbidden contact, +4 per unit
of aspect ratio above 3).

| Variant | Required met | Forbidden touched | Worst aspect | Max area error | Corridor share of gross | Time |
|---|---|---|---|---|---|---|
| H2: ordered slicing in a 15.9 x 12.2 m rectangle, no corridor | 6/13 at start, 10/13 (77 %) after 4 swap rounds | 0 | 3.24 | 0 % | 0 % | 8 ms |
| H3: double-loaded spine, 6 m strips, 1.8 m corridor, 16.2 m long | 4/13 at start, 5/13 (38 %) | 0 | 7.05 (a 5 m2 WC 0.8 m wide) | 0 % | 13.0 % | 2 ms |
| H3b: as H3, waiting counted as open circulation (links to it met through the corridor) | 9/13 (69 %) | 0 | 7.05 | 0 % | 13.0 % | |
| H3c: as H3, consecutive small rooms (< 10 m2) stacked in one bay | 6/13 (46 %) | 0 | 2.94 | 0 % | 13.0 % | |

Limits of the experiment: one programme, one boundary proportion, one adjacency graph with a strong hub; no
sweep; in H3c a stacked small room away from the corridor loses its corridor wall. Confidence in the direction:
medium; in the numbers: low (one case).

**H2, layout by slicing: partly supported, partly falsified (medium).** Areas exact, under a second, plain ES5:
supported by the method (exact by construction; P for Wong and Liu, Bruls) and by the run (8 ms). "At least 80 % of
required adjacencies": not met on the one case run (77 %), and no published slicing method guarantees adjacency
(Wong and Liu optimise wire length, Shneiderman and Wattenberg keep order only roughly, P). The swap search gained
4 links over the greedy order, so the local search matters. H2 as stated is too strong; a revised form that the
evidence supports: "areas exact, adjacency typically 70 to 80 % for a hub-and-spoke programme, reported, never
guaranteed".

**H3, the corridor is the hard part: supported (medium-high).** Every source that adds circulation pays for it:
Shiksha et al. shrink rooms and need an approximation for minimal corridors (P); Mirahmadi and Shami say the
treemap corridor step wastes space (P); Anthropocity makes the user choose between area error and spare floor (S);
practice budgets 20 to 38 % of net for circulation (BB103, GSA, P). In the run, a corridor-first spine reached
every room by construction but met far fewer wall adjacencies (38 % against 77 %) and spent 13 % of gross on the
corridor; with the waiting room open to the corridor it met 69 %. The second half of H3 ("a corridor-first method
does better for this size") is *not* supported for wall adjacency; it is supported for reach, which slicing alone
does not give at all. So the trade is reach for adjacency, and the open-room rule (a lobby or waiting room as part
of circulation, which Anthropocity and Shiksha et al. both use, S and P) recovers most of the loss.

**H4, published deterministic methods with stated limits: supported (high).** Rectangular dualisation (graph must be
a PTPG; extra rooms merged otherwise; GPLAN, P), LP dimensioning (min widths and aspect, not target areas;
Upasani, P), circulation insertion (rooms shrink; set cover approximated; Shiksha, P), MIQP (solver; Wu, P from the
supplement), CP (solver, enumeration growth; Medjdoub and Yannou, P). Each paper states rectangles-only or a solver
or no corridor, as H4 predicted. One correction: the circulation paper does make corridors deterministically from
a graph, so "no corridor" is not true of the whole graph family.

## 5. Recommendation (inference)

All of this section is inference from the findings above.

**First method: a deterministic two-level slicing layout with a spine, plus a swap search, plus honest scores.**

1. **Typology first, chosen by the user or suggested from the programme:** spine with double-loaded rooms
   (default), single-loaded (narrow site or one daylit side), or no corridor (open rooms reach each other, e.g. a
   small house or studio). The entrance fixes the end of the spine. This is what practice does (Ching's linear
   organisation; BB103 requires every room on a route) and what the commercial and research generators that make
   corridors converge on (Anthropocity's spine threshold; Shiksha's corridor graph from the entrance edge).
2. **Bands:** cut the boundary rectangle (or the largest rectangle in the zoning envelope) into strips: room
   band, corridor band, room band. Corridor width from a standard entry in the registry (BB103: 1.8 m main, 1.2 m
   short), not hard-coded.
3. **Order:** a greedy order from the entrance by links to already-placed spaces (as in the run), so related
   spaces are consecutive; split the order between the two bands by area.
4. **Slice each band** as an ordered slicing (exact areas); consecutive small rooms share a bay stacked in depth,
   with the deeper one flagged when it loses its corridor wall (H3c showed the aspect gain and that cost).
5. **Open rooms:** a space marked open (lobby, waiting, reception) may be entered through and counts as circulation
   for reach, as in Anthropocity and Shiksha et al.
6. **Swap search:** best-improvement pair swaps (deterministic, no random step), on the cost of section 2.5.
7. **Report, never hide:** required adjacencies met / required (by wall, and by corridor), forbidden contacts,
   worst aspect ratio, max area error (zero by construction unless the boundary is too small, then said), corridor
   share of gross against the standard's range, reach (rooms with a corridor wall or an open neighbour), and the
   walking distance from the entrance. The user then edits; the method suggests, it does not decide (Lobos and
   Donath's adoption criticism; Michalek and Papalambros's interactive argument).

Size: the run's core is about 100 lines; with bands, bays, open rooms and the report, an estimated 300 to 400 lines
of ES5 in one engine file under `src/js/engine/`, with unit tests. Time: milliseconds for 20 spaces (12 spaces took
8 ms with n^2 swaps per round; 20 spaces is about 3 times the swaps).

**Leave out, for now:**
- Rectangular dualisation and GPLAN-style enumeration: correct about adjacency but needs a triangulated planar
  graph the brief rarely gives, imposes adjacencies nobody asked for, ignores target areas, and enumerates more than
  a user can read (its authors' own first limitation). Revisit if users ask for "every arrangement".
- MIQP, CP, SQP: each needs a solver library; none is a small vetted MIT/BSD file today (a pure-JS LP exists in
  the wider ecosystem but was not researched here: open).
- Stochastic search (annealing, GA, Metropolis): not deterministic, fails in a share of runs (Merrell), and the
  deterministic swap search reached a local optimum in 4 rounds on the test case.
- Learned methods: trained networks (F10, F12).
- Non-rectangular boundaries: no method read handles a sloped or curved outline; for a rectilinear envelope, cut it
  into rectangles and plan each, or plan in the largest inscribed rectangle and report the remainder.
- Multi-storey and stairs: one level only, as the question asks.

## 6. Counter-evidence

- Against slicing: the run met 77 %, under H2's 80 %; slicing has no adjacency guarantee in any source; Bruls and
  ordered treemaps only keep order roughly. A strongly connected hub (6 links on one room) is the worst case for a
  slicing order, and the test programme was such a case, so a different programme could score better or worse.
- Against the spine: wall adjacency fell to 38 %; the thin strips gave a 7:1 WC; Ching lists five organisations and
  the spine is only the linear one; centralised, radial and clustered programmes (a library around a reading room)
  fit a spine badly.
- For the graph family, against this recommendation: rectangular duals do guarantee every requested adjacency, and
  Shiksha et al. add corridors deterministically. If the owner values guaranteed adjacency over exact areas, the
  dual is the stronger method; its cost is the PTPG requirement and size of code.
- For MIQP: Wu et al. reach 125 to 138 rooms in about 75 s with all constraints met in their shown cases; a solver
  approach is the published state of the art for quality. Its exclusion here rests on the build contract, not on
  the method.
- Against generation at all: Lobos and Donath (2010) found no generator in daily use; Alberti produced fast
  layouts that practice rejected for leftover space and "nonsensical" plans. The recommendation's answer is to
  report scores and leave edits to the user, which is untested here.
- Vendor claims (Finch, TestFit, Maket, Architechtures) imply generation works at scale; none states a
  satisfaction rate, so they neither support nor refute H2 or H3.

## 7. Still open

- GPLAN and Circulation_Paper code: location, licence and size not confirmed (the linked GitHub repository could
  not be reached from here).
- Wu et al. 2018 main paper: solver name, formulation details and failure discussion (main PDF refused, 406).
- Rodrigues et al. 2013 Part 2 (run times, success rates); Guo and Li 2017 full text (publisher API rate limit);
  Arvin and House 2002 full text and the 2004 dissertation (403).
- Liggett 2000: no open copy found.
- Otten 1982, Kozminski and Kinnen 1985, Bhasker and Sahni 1987/1988 not read directly (their results reached
  through GPLAN's paper, S).
- Knecht and Koenig 2010 (k-d tree plus evolution): proceedings PDF 404; Weimar repository reset the connection.
- Autodesk Forma (Spacemaker) and Hypar's current space planning docs: refused (403) or moved (404).
- Anthropocity: how its room shapes are cut (the algorithm), whether it is deterministic, and its failure rate are
  not documented in the pages read.
- The experiment needs a sweep: several programmes (house, school wing, clinic, office), boundary proportions 1:1
  to 3:1, 10 to 20 spaces, to give H2 and H3 numbers with a spread. The script is in appendix A for the main note
  to move into `docs/research/experiments/` if the owner wants it kept.
- Whether a small vetted pure-JS LP or CP library exists that meets the library rule (MIT/BSD, small, vendored):
  not researched.

## 8. Search log

| # | Date | Host / query | Target | Result | Kept |
|---|---|---|---|---|---|
| 1 | 11-16 | web search | Wong and Liu 1986 PDF | Algorithmica 1989 copy at limsk.ece.gatech.edu | P |
| 2 | 11-16 | limsk.ece.gatech.edu | Wong, Liu 1989 PDF | 200 | P |
| 3 | 11-16 | web search | ordered treemaps | cs.umd.edu PDF | P |
| 4 | 11-16 | cs.umd.edu | Shneiderman, Wattenberg 2001 | 200 | P |
| 5 | 11-16 | web search | Knecht, Koenig 2010 | generativeart.com PDF | - |
| 6 | 11-16 | generativeart.com | Knecht, Koenig PDF | 404 | U |
| 7 | 11-16 | e-pub.uni-weimar.de | Koenig, Knecht 2014 | connection reset | - |
| 8 | 11-16 | web search | Shekhawat corridor | AI EDAM 2025 open access | P |
| 9 | 11-16 | web search | GPLAN code | no repository found | - |
| 10 | 11-16 | arxiv.org | 1910.00081, 2008.01803 | 200 | P |
| 11 | 11-16 | cambridge.org | Shiksha et al. 2025 PDF | 200 | P |
| 12 | 11-16 | api.github.com, raw.githubusercontent.com, git clone, add_repo | GPLAN-team repos | refused / 404 / not found | open |
| 13 | 11-16 | arxiv.org | Eppstein et al. 0901.3924 abstract | 200 | P (abstract) |
| 14 | 11-16 | web search | net-to-gross WBDG | GSA circulation PDF, DoD ch. 130 | - |
| 15 | 11-16 | wbdg.org | GSA 2012; DoD 130 2018 | 200 | P |
| 16 | 11-16 | web search, assets.publishing.service.gov.uk | BB103 | 200 | P |
| 17 | 11-16 | web search, uoregon course copy | Ching ch. 4 | 200 | P |
| 18 | 11-16 | web search | double vs single loaded figures | no primary figure found | - |
| 19 | 11-16 | anthropocity.com/docs | 11 docs pages | 200 | S |
| 20 | 11-16 | finch3d.com, testfit.io, maket.ai, architechtures.com | home pages | 200 | S |
| 21 | 11-16 | hypar.io, docs.hypar.io; raw.githubusercontent.com HyparSpace | product, docs, README | title only / 404 / 200 | S / U |
| 22 | 11-16 | autodesk.com Forma | product page | 403 | U |
| 23 | 11-16 | web search | Wu et al. 2018 | author PDF + supplement | - |
| 24 | 11-16 | peterwonka.net | main PDF | 406 (curl), too large (fetch tool) | open |
| 25 | 11-16 | peterwonka.net | supplement | 200 | P |
| 26 | 11-16 | diglib.eg.org | record | 403 | - |
| 27 | 11-16 | arxiv.org 1303.4017 | Medjdoub, Yannou | 200 | P |
| 28 | 11-16 | oaktrust.library.tamu.edu | Arvin dissertation | 403 | open |
| 29 | 11-16 | pages.sandpoints.org (ACADIA archive) | Arvin, House 1999 abstract | 200 | P (abstract) |
| 30 | 11-16 | cmu.edu | Michalek, Papalambros 2002 | 200 | P |
| 31 | 11-16 | estudogeral.uc.pt | Rodrigues et al. 2013 Part 1 | redirect loop, then 200 with a cookie jar | P |
| 32 | 11-16 | journal.hep.com.cn, doaj.org, api.elsevier.com | Guo, Li 2017 | 404 / 403 / rate limit | S (search summary) |
| 33 | 11-16 | web search | Liggett 2000 | record only | open |
| 34 | 11-16 | redalyc.org | Lobos, Donath 2010 | curl 403; fetch tool 200 | P |
| 35 | 11-16 | paulmerrell.org | Merrell 2010 cost terms | 200 | P |
| 36 | 11-16 | repository | docs/work-orders/v179/SPEC.md | read | P |
| 37 | 11-16 | local Node | experiment E-layout | ran | P (one case) |

## 9. References

All read 2026-11-16 unless said otherwise.

1. Wong D F, Liu C L. Floorplan design of VLSI circuits. Algorithmica 4 (1989) 263-291 (journal version of "A new
   algorithm for floorplan design", DAC 1986). https://limsk.ece.gatech.edu/book/papers/polish.pdf Read: abstract,
   1, 2.1-2.6, Table 1. P.
2. Shneiderman B, Wattenberg M. Ordered treemap layouts. IEEE InfoVis 2001.
   https://www.cs.umd.edu/users/ben/papers/Shneiderman2001Ordered.pdf Read: whole. P.
3. Eppstein D, Mumford E, Speckmann B, Verbeek K. Area-universal rectangular layouts. arXiv 0901.3924 (2009).
   https://arxiv.org/abs/0901.3924 Read: abstract. P (abstract).
4. Shekhawat K et al. GPLAN: computer-generated dimensioned floorplans for given adjacencies. arXiv 2008.01803.
   https://arxiv.org/pdf/2008.01803 Read: 3.2-3.5, 6. P. (Also in grammars-and-layout.md.)
5. Upasani N, Shekhawat K, Sachdeva G. Automated generation of dimensioned rectangular floorplans. arXiv 1910.00081.
   https://arxiv.org/pdf/1910.00081 Read: abstract, 1, 3.4, 4, 5. P.
6. Shiksha, Anand S, Shekhawat K, Agrawal K. Automated generation of circulations within a floorplan. AI EDAM 39
   (2025) e9, CC BY 4.0. https://doi.org/10.1017/S0890060425000022 (PDF from cambridge.org) Read: abstract, method,
   limitations, conclusion. P.
7. Kozminski K, Kinnen E 1985; Bhasker J, Sahni S 1987/1988 (rectangular dual existence and linear algorithms):
   not read; through 4 and 6. S.
8. Ching F D K. Architecture: Form, Space, and Order, ch. 4 Organization (course copy, University of Oregon).
   https://bpb-us-e1.wpmucdn.com/blogs.uoregon.edu/dist/1/16101/files/2018/04/Ching_Ch-4-Organization_FormSpaceOrder-vikn3p.pdf
   Read: chapter opening, the five organisations. P.
9. UK Department for Education. Building Bulletin 103: Area guidelines for mainstream schools (2014).
   https://assets.publishing.service.gov.uk/media/5f23ec238fa8f57acac33720/BB103_Area_Guidelines_for_Mainstream_Schools.pdf
   Read: "Circulation, plant and internal walls". P.
10. GSA (commissioned). Circulation: Defining and Planning (11 May 2012), on WBDG.
    https://www.wbdg.org/FFC/DOD/UFC/600SERIES/RESOURCES/Circulation_-_Defining_and_Planning.pdf Read: pp. 1-7. P.
11. US DoD. Space Planning Criteria, Chapter 130: Net to Gross Conversion Factors (1 July 2018).
    https://www.wbdg.org/FFC/DOD/MHSSC/spaceplanning_healthfac_130_july_2018.pdf Read: sections 2, Tables 1-2. P.
12. Anthropocity documentation. https://anthropocity.com/docs (layout-view, graph-lab-paths, graph-lab-clusters,
    getting-started, ui-parameters-table, export-formats and five more pages). Read: whole pages. S (vendor).
13. Finch3D https://www.finch3d.com/ ; TestFit https://www.testfit.io/ ; Maket https://www.maket.ai/ ;
    Architechtures https://architechtures.com/en . Read: home pages through a fetch tool. S (vendor).
14. Hypar. HyparSpace README. https://raw.githubusercontent.com/hypar-io/HyparSpace/master/README.md Read: whole.
    P (README); docs pages 404; Autodesk Forma page 403.
15. Wu W, Fan L, Liu L, Wonka P. MIQP-based layout design for building interiors. Computer Graphics Forum 37(2)
    2018. Main: https://peterwonka.net/Publications/pdfs/2018.EG.Wenming.MIQPFloorplan.pdf (not reached).
    Supplement: https://peterwonka.net/Publications/pdfs/2018.EG.Wenming.MIQPFloorplan.Additional.pdf Read: whole.
    P (supplement).
16. Medjdoub B, Yannou B. Separating topology and geometry in space planning. Computer-Aided Design 32(1) 2000.
    https://arxiv.org/pdf/1303.4017 Read: abstract, 1, 3.1.2, 4, 5, Table 2. P.
17. Rodrigues E, Gaspar A R, Gomes A. An evolutionary strategy enhanced with a local search technique for the
    space allocation problem in architecture, Part 1. Computer-Aided Design 45(5) 2013.
    https://estudogeral.uc.pt/handle/10316/27167 Read: abstract, 1-3, evaluators. P. Part 2 not read.
18. Guo Z, Li B. Evolutionary approach for spatial architecture layout design enhanced by an agent-based topology
    finding system. Frontiers of Architectural Research 6(1) 2017. https://doi.org/10.1016/j.foar.2016.11.003
    Not reached. S (search summary of the abstract).
19. Arvin S A, House D H. Modeling architectural design objectives in physically based space planning. ACADIA 1999
    pp. 212-225; Automation in Construction 11(2) 2002. Abstract via the ACADIA archive (pages.sandpoints.org). P
    (abstract); body S through 20.
20. Michalek J J, Papalambros P Y. Interactive design optimization of architectural layouts. Engineering
    Optimization 34(5) 2002. https://www.cmu.edu/me/ddl/publications/2002-Michalek,Papalambros-EO-InteractiveLayout.pdf
    Read: whole. P.
21. Merrell P, Schkufza E, Koltun V. Computer-generated residential building layouts. ACM TOG 29(6) 2010.
    https://paulmerrell.org/wp-content/uploads/2021/06/floorplan-final.pdf Read: 5.2 cost terms, Figure 13. P.
22. Lobos D, Donath D. The problem of space layout in architecture: a survey and reflections. Arquiteturarevista
    6(2) 2010. https://www.redalyc.org/pdf/1936/193617358005.pdf Read: introduction, criteria, conclusions,
    commercial software. P.
23. Liggett R S. Automated facilities layout: past, present and future. Automation in Construction 9(2) 2000,
    197-215. Not reached (record only). S.
24. Already in grammars-and-layout.md, cited not re-read: Bruls, Huizing, van Wijk 2000; Marson, Musse 2010;
    Mirahmadi, Shami 2012; Weber, Mueller, Reinhart 2022.
25. This repository: docs/work-orders/v179/SPEC.md (part 1). P.

## Appendix A. The experiment script (E-layout)

Run with `node e_layout.js` (Node 18+; no dependencies). Kept here because the scratch copy is not durable.

```js
// H2/H3 experiment: ordered slicing + swap search vs. double-loaded spine. ES5 style, deterministic.
var P = [ // name, area m2
 ['Reception',30],['Waiting',40],['Consult1',14],['Consult2',14],['Consult3',14],['Consult4',14],
 ['Treatment',20],['Staff',18],['Office',12],['WC1',5],['WC2',5],['Store',8]];
var REQ = [[0,1],[1,2],[1,3],[1,4],[1,5],[1,9],[6,2],[7,8],[7,11],[6,11],[8,0],[7,10],[6,7]];
var FORB = [[11,1],[9,0]];
var DOOR = 1.0, CW = 1.8, n = P.length, i, j;
var NET = 0; for (i = 0; i < n; i++) NET += P[i][1];
function adj(a, b) { // shared wall length between rects
  var e = 1e-6, ov;
  if (Math.abs(a.x + a.w - b.x) < e || Math.abs(b.x + b.w - a.x) < e) { ov = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y); return ov > 0 ? ov : 0; }
  if (Math.abs(a.y + a.h - b.y) < e || Math.abs(b.y + b.h - a.y) < e) { ov = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x); return ov > 0 ? ov : 0; }
  return 0; }
function slice(order, x, y, w, h, out) { // ordered binary slicing, exact areas
  if (order.length === 1) { out[order[0]] = {x: x, y: y, w: w, h: h}; return; }
  var tot = 0, k, s = 0, best = 1, bd = 1e9;
  for (k = 0; k < order.length; k++) tot += P[order[k]][1];
  for (k = 0; k < order.length - 1; k++) { s += P[order[k]][1]; if (Math.abs(s - tot / 2) < bd) { bd = Math.abs(s - tot / 2); best = k + 1; } }
  var A = order.slice(0, best), B = order.slice(best), sa = 0;
  for (k = 0; k < A.length; k++) sa += P[A[k]][1];
  var f = sa / tot;
  if (w >= h) { slice(A, x, y, w * f, h, out); slice(B, x + w * f, y, w * (1 - f), h, out); }
  else { slice(A, x, y, w, h * f, out); slice(B, x, y + h * f, w, h * (1 - f), out); } }
function score(R, viaCorr) {
  var met = 0, forb = 0, k, worst = 1, r;
  for (k = 0; k < REQ.length; k++) if (adj(R[REQ[k][0]], R[REQ[k][1]]) >= DOOR) met++;
  for (k = 0; k < FORB.length; k++) if (adj(R[FORB[k][0]], R[FORB[k][1]]) > 0) forb++;
  for (k = 0; k < n; k++) { r = R[k]; worst = Math.max(worst, Math.max(r.w / r.h, r.h / r.w)); }
  return {met: met, forb: forb, worst: worst}; }
function cost(s) { return -s.met * 10 + s.forb * 30 + Math.max(0, s.worst - 3) * 4; }
function greedyOrder() { // start at entrance (0), add the space with most required links to placed ones
  var o = [0], used = {0: 1}, k, c, b, bs;
  while (o.length < n) { b = -1; bs = -1;
    for (c = 0; c < n; c++) if (!used[c]) { var sc = 0; for (k = 0; k < REQ.length; k++) { if ((REQ[k][0] === c && used[REQ[k][1]]) || (REQ[k][1] === c && used[REQ[k][0]])) sc++; } if (sc > bs) { bs = sc; b = c; } }
    o.push(b); used[b] = 1; }
  return o; }
function search(layoutFn) { // deterministic best-improvement over all pair swaps
  var o = greedyOrder(), R = layoutFn(o), s = score(R), c = cost(s), it = 0, improved = true;
  var s0 = s;
  while (improved && it < 500) { improved = false; it++;
    var bc = c, bi = -1, bj = -1;
    for (i = 0; i < n; i++) for (j = i + 1; j < n; j++) {
      var t = o[i]; o[i] = o[j]; o[j] = t; var cc = cost(score(layoutFn(o))); t = o[i]; o[i] = o[j]; o[j] = t;
      if (cc < bc - 1e-9) { bc = cc; bi = i; bj = j; } }
    if (bi >= 0) { var t2 = o[bi]; o[bi] = o[bj]; o[bj] = t2; c = bc; improved = true; } }
  R = layoutFn(o); return {first: s0, s: score(R), R: R, o: o, it: it}; }
// H2: whole boundary = net area, 1.3:1 rectangle
var W2 = Math.sqrt(NET * 1.3), H2 = NET / W2;
function lay2(o) { var out = []; slice(o, 0, 0, W2, H2, out); return out; }
// H3: double-loaded spine; boundary = net + corridor; two strips of depth D, split order in two by area
var D = 6.0, L = NET / (2 * D);
function lay3(o) { var out = [], tot = 0, s = 0, k, cut = 1, bd = 1e9;
  for (k = 0; k < n; k++) tot += P[o[k]][1];
  for (k = 0; k < n - 1; k++) { s += P[o[k]][1]; if (Math.abs(s - tot / 2) < bd) { bd = Math.abs(s - tot / 2); cut = k + 1; } }
  var A = o.slice(0, cut), B = o.slice(cut);
  function row(list, y) { var ar = 0, q, x = 0; for (q = 0; q < list.length; q++) ar += P[list[q]][1];
    for (q = 0; q < list.length; q++) { var w = L * P[list[q]][1] / ar; out[list[q]] = {x: x, y: y, w: w, h: D * ar / (L * D)}; x += w; } }
  row(A, 0); row(B, D + CW); return out; }
function report(name, r, corrArea) {
  var R = r.R, k, aerr = 0, gross = NET + corrArea;
  for (k = 0; k < n; k++) aerr = Math.max(aerr, Math.abs(R[k].w * R[k].h - P[k][1]) / P[k][1]);
  console.log(name + ': start met ' + r.first.met + '/' + REQ.length + ', after swaps met ' + r.s.met + '/' + REQ.length +
    ' (' + Math.round(100 * r.s.met / REQ.length) + '%), forbidden touched ' + r.s.forb + ', worst aspect ' + r.s.worst.toFixed(2) +
    ', max area error ' + (100 * aerr).toFixed(2) + '%, corridor share of gross ' + (100 * corrArea / gross).toFixed(1) + '%, iterations ' + r.it);
  console.log('  order: ' + r.o.map(function (q) { return P[q][0]; }).join(' > ')); }
var t0 = Date.now(); var r2 = search(lay2); var t1 = Date.now();
report('H2 ordered slicing, no corridor, ' + W2.toFixed(1) + ' x ' + H2.toFixed(1), r2, 0); console.log('  time ' + (t1 - t0) + ' ms');
t0 = Date.now(); var r3 = search(lay3); t1 = Date.now();
report('H3 double-loaded spine, strips ' + D + ' m, corridor ' + CW + ' m, length ' + L.toFixed(1), r3, CW * L); console.log('  time ' + (t1 - t0) + ' ms');
// facing across the corridor counts as near
var near = 0; for (i = 0; i < REQ.length; i++) { var a = r3.R[REQ[i][0]], b = r3.R[REQ[i][1]]; var ov = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
  if (adj(a, b) >= DOOR || (a.y !== b.y && ov >= DOOR)) near++; }
console.log('  H3 met by wall or facing across corridor: ' + near + '/' + REQ.length + '; every room has a corridor wall: yes by construction');
// H3b: Waiting treated as open circulation (practice: waiting as corridor widening); links to it count as met
var metB = 0; for (i = 0; i < REQ.length; i++) { var p = REQ[i]; if (p[0] === 1 || p[1] === 1 || adj(r3.R[p[0]], r3.R[p[1]]) >= DOOR) metB++; }
console.log('H3b spine with Waiting open to the corridor: met ' + metB + '/' + REQ.length);
// H3c: small rooms (< 10 m2) consecutive in a row share one bay, stacked in depth (bay clustering)
function lay3c(o) { var out = lay3(o), k, rows = {};
  for (k = 0; k < n; k++) { var y = out[k].y; (rows[y] = rows[y] || []).push(k); }
  for (var y in rows) { var list = rows[y].sort(function (a, b) { return out[a].x - out[b].x; }), q = 0;
    while (q < list.length) { var g = []; while (q < list.length && P[list[q]][1] < 10) { g.push(list[q]); q++; }
      if (g.length > 1) { var x0 = out[g[0]].x, wsum = 0, ar = 0, m; for (m = 0; m < g.length; m++) { wsum += out[g[m]].w; ar += P[g[m]][1]; }
        var yy = out[g[0]].y, hh = out[g[0]].h; for (m = 0; m < g.length; m++) { var hm = hh * P[g[m]][1] / ar; out[g[m]] = {x: x0, y: yy, w: wsum, h: hm}; yy += hm; } }
      if (!g.length) q++; } }
  return out; }
var r3c = search(lay3c); report('H3c spine with small-room bays', r3c, CW * L);
console.log('  note: in H3c a stacked small room away from the corridor loses its corridor wall');
```
