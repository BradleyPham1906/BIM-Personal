# Physics in algorithmic design and on the site: form-finding and stormwater runoff

One of four parallel research notes on "the physical world" (2026-11-21). Method:
`docs/research/research-protocol.md`. Experiments: `docs/research/experiments/physical-world/formfinding.py`
and `runoff.py` (Python 3.13, numpy 2.5.3 for the comparison only; each run once, deterministic).
Downloads were kept in `/tmp/claude-0/dl-ff/`, read as text, never run.

## 1. Abstract

**Question.** What is the simplest correct way for an offline ES5 app to (A) find the shape of cable
nets, membranes and funicular shells under load and prestress, and hand the result to the frame
solver, and (B) route rain over the site's terrain and size the peak flow it makes?

**Answer.** (A) The force density method (Schek 1974) is one sparse, symmetric, positive definite
linear solve per axis when every force density is positive and every free node reaches a support;
it is exact, needs no parameters and makes deterministic test data. Dynamic relaxation (Day 1965;
Barnes) is the iterative alternative that also handles springs with rest lengths, elastic members
and live dragging; with zero rest lengths and stiffness equal to q it converges to the FDM answer
(measured: 8e-10 m on a 5 x 5 net). Kinetic damping with Barnes's peak correction took 81
iterations against 398 for compas's viscous scheme on that net. (B) Sample the TIN on a regular
grid, fill depressions with Priority-Flood+epsilon (Barnes et al. 2014), route with D8 (O'Callaghan
and Mark 1984), accumulate, and size peaks with the rational method Q = C i A / 360 (HEC-22 4th ed.,
2024), limited to drainage areas under 80 ha. A 200 x 200 grid took about 240 ms in CPython for all
three steps, so a browser is not the constraint. NOAA Atlas 14's CSV endpoint answers keyless but
sends no CORS header (and its preflight returns 500), so the app cannot fetch it: the intensity is
typed or pasted.

**Recommendation.** A: FDM first (one module, a test from the closed forms below), DR with kinetic
damping second, for rest-length goals and interactive dragging; thrust network analysis later.
B: grid D8 with Priority-Flood+epsilon, accumulation, the rational method with HEC-22 Table 4.1 as a
registry record; D-infinity later. Both are small ES5 code, no library.

## 2. The question and the hypotheses

What a good answer must decide: the algorithm and its parameters, the edge cases that make the test
data, the data sources and whether a browser can reach them, the licences of code that could be
read, and how the result joins the app (the model graph V230, the frame solver V125, the TIN V144).

| # | Hypothesis (falsifiable) | Outcome | Evidence |
|---|---|---|---|
| HA1 | With q > 0 on every edge and every free node joined to a support, FDM's matrix D = Ci^T Q Ci is positive definite and one solve per axis gives the unique equilibrium | **Held** | e01(b): eigenvalues of D 1.17 to 6.83; residual 1.8e-15; a free node with no path to a support makes D singular (detected) |
| HA2 | DR with zero-rest-length springs of stiffness k = q converges to FDM's coordinates | **Held** | e01(c): max difference 2e-10 to 8e-10 m for four damping settings |
| HA3 | Barnes's fictitious mass m_i = dt^2/2 * sum k is enough for stability, and much less diverges | **Held, refined** | lam = 0.45 gave NaN; the true limit on this net is lam = eig_max(D)/(2S) = 0.854 (0.86 bounded, 0.85 NaN undamped): the rule is a safe Gershgorin bound, not a sharp one |
| HA4 | Kinetic damping converges in fewer iterations than viscous damping on a small net | **Held here**, with counter-evidence | 81 (lam 1) and 62 (lam 1.5) against 398 and 389 (c = 0.1). A 2019 comparison for membranes is reported to favour viscous damping (search summary only, U) |
| HA5 | The kinetic damping correction (moving the nodes back to the energy peak) matters | **Held** | Without it, our restart rule fell into a four-step cycle and did not converge in 200 000 iterations |
| HB1 | Priority-Flood, D8 and accumulation on a 200 x 200 grid run in well under a second | **Held (proxy)** | CPython: fill 100 ms, D8 110 ms, accumulation 31 ms; JS in a browser not measured here |
| HB2 | NOAA's PFDS CSV endpoint is readable by a browser page (CORS) | **Failed** | 200 with the data, but no Access-Control-Allow-Origin header; OPTIONS preflight 500 |
| HB3 | HEC-22's 4th edition keeps the 80 ha (200 ac) limit and the ASCE 1960 C table, and state manuals agree with its values | **Limit held; values disagree** | HEC-22 p. 25-26; TxDOT Table 4-10 differs in 6 rows (section 4.B.2) |
| HB4 | A keyless non-US source of design rainfall intensity exists | **Partly** | Canada's ECCC IDF archive is keyless (zip, station files, no CORS header); Australia's BoM refused a script (403); the UK's FEH is sold. Others not searched (U) |
| HB5 | After a plain (epsilon = 0) fill, D8 leaves the filled cells without a direction | **Held** | e02(a): the filled pit is a flat ("."); epsilon = 0.001 drains it |

## 3. Method

### Search log

| # | Where | Query or request | What came back | Kept / set aside |
|---|---|---|---|---|
| 1 | GitHub (git clone, shallow) | `blockresearchgroup/compas_fd`, `compas-dev/compas` | compas_fd @7ee3c5a (2024-11-10), compas @a279a38 (2026-11-18); both MIT | Kept: `fd_numpy.py`, `fd_numerical_data.py`. compas 2.x has no DR |
| 2 | raw.githubusercontent.com | compas v1.17.10 `numerical/dr/dr.py`; `dr_numpy.py` | dr.py 200; dr_numpy 404 at that path | Kept dr.py (pure Python, RK4, viscous) |
| 3 | GitHub | `arpastrana/jax_fdm` | @7dc5122 (2026-11-11), MIT | Kept: `equilibrium/models.py` (stiffness and load matrices) |
| 4 | GitHub | `Dan-Piker/K2Goals` | @2ec9395 (2021-02-15), Apache-2.0; goals only, the Kangaroo2 solver is not in it | Kept: `Spring.cs`, `Unary.cs`, `ConstantTension.cs` |
| 5 | Web search | Barnes 1999 kinetic damping position correction | Pointers: Barnes 1999 IJSS 14(2) 89-104; Wikipedia; Oasys GSA theory; Rodriguez et al. 2011 | Kept pointers; the search summary itself not used |
| 6 | Web search | DR javascript kinetic damping GitHub | No JS kinetic-damping form-finder found; BRG DigitalFutures gitbook; Verlet tutorials | Gitbook is rendered by script: curl got an empty shell (refused in effect) |
| 7 | en.wikipedia.org (raw wikitext) | Dynamic_relaxation | 200: equations and iteration steps citing Lewis 2003 and Wakefield 1999 | Kept as S |
| 8 | docs.oasys-software.com | GSA 10.2 theory: dynamic relaxation | 200: practitioner's description of kinetic damping and fictitious masses | Kept (practice) |
| 9 | oss.jishulink.com | Rodriguez, Rio, Cadou, Troufflard (preprint 2011) | 200: PDF; Barnes's mass rule eq. 4-5 | Kept as S |
| 10 | arxiv.org | 1411.6823, 2206.10406 | 200; kinetic damping described, no correction formula | Kept 1411.6823 as S for "reset at the peak" |
| 11 | Web search; core.ac.uk; infoscience.epfl.ch; discovery.ucl.ac.uk | Senatore and Piker 2015 (CAD 61) | core.ac.uk 403; EPFL 429; UCL 403 | **Refused**; not read |
| 12 | sciencedirect.com | Schek 1974 CMAME 3 | 403 | **Refused**; FDM read through two implementations |
| 13 | Web search | FDM C_N^T Q C_N lecture notes | BRG gitbook (script-rendered), Bournemouth page (404) | Set aside |
| 14 | raw.githubusercontent.com | licences: pysheds, whitebox-tools, richdem, TauDEM, GRASS, compas_tna, Barnes2013-Depressions | read (section 4.B.1) | Kept |
| 15 | raw.githubusercontent.com | whitebox-tools `hydro_analysis/` d8_pointer, d8_flow_accum, fill_depressions, breach_depressions_least_cost, dinf_pointer | 200 | Kept, read as text |
| 16 | raw.githubusercontent.com | pysheds `sgrid.py`; landlab `flow_director_steepest.py`, LICENSE | 200 | Kept |
| 17 | arxiv.org | 1511.04463 (Priority-Flood) | 200; Algorithms 1 and 3 read | Kept, P |
| 18 | hydrology.usu.edu | Tarboton 1997 WRR 33(2) | 200, author's PDF | Kept, P |
| 19 | Web search; transportation.ky.gov; fhwa.dot.gov | HEC-22 4th ed. 2024 | Kentucky's copy 200 (12.9 MB, FHWA-HIF-24-006, Feb 2024); FHWA's own PDF answers 200 too | Kept, P: pp. 23-29, 9.2.2 |
| 20 | txdot.gov | Hydraulic Design Manual ch. 4 sections 11, 12, Table 4-10 | 200; Kirpich equation image read | Kept, P (a state's practice) |
| 21 | hdsc.nws.noaa.gov | `cgi-bin/hdsc/new/fe_text_mean.csv` (as briefed) | 301 to `cgi-bin/new/fe_text_mean.csv` | Kept the new path |
| 22 | hdsc.nws.noaa.gov | Philadelphia 39.9526, -75.1652: intensity metric/english, depth, PDS/AMS; London; OPTIONS | section 4.B.3 | Kept, P |
| 23 | weather.gov/disclaimer | NWS use of data | public domain unless noted | Kept, P |
| 24 | water.noaa.gov; weather.gov HDSC progress report (Jul-Sep 2025, published Dec 2025) | NOAA Atlas 15 status | Two dates that disagree (section 4.B.3) | Kept both |
| 25 | collaboration.cmc.ec.gc.ca; bom.gov.au | non-US IDF | ECCC 200, listing with `idf_v3-40_2025-12-5.zip`, no CORS header; BoM 403 | Recorded |

### Sources by kind

- Standards and agency manuals: HEC-22 4th ed. (FHWA 2024); TxDOT Hydraulic Design Manual; NWS disclaimer; NOAA Atlas 14 PFDS (a service, tested).
- Papers read in full or in the relevant part: Barnes et al. 2014 (Priority-Flood); Tarboton 1997 (D-infinity); Rodriguez et al. 2011 (DR masses); arXiv 1411.6823 (elastic sheets, DR section).
- Open implementations read as text: compas_fd, jax_fdm, compas 1.x dr.py, K2Goals, WhiteboxTools, pysheds, Landlab.
- Practitioners: Oasys GSA's theory manual; HEC-22's worked examples; TxDOT.
- Not reachable: Schek 1974, Barnes 1999, Day 1965, O'Callaghan and Mark 1984, Planchon and Darboux 2001, Senatore and Piker 2015, Block 2009.

### Independent check

Not yet done. The protocol's second reader should re-read: compas_fd and jax_fdm (the FDM system),
compas dr.py (masses, residual), HEC-22 pp. 23-29, TxDOT Table 4-10 and eq. 4-15, Barnes et al. 2014
Algorithm 1, Whitebox d8_pointer.rs lines 252-295, and the PFDS response.

## 4. Findings

### A. Form-finding

**A.1 The force density method.**

- The system, per axis: (Ci^T Q Ci) x_free = p_free - Ci^T Q Cf x_fixed, C the edge-node matrix
  (+1, -1 per edge), Q = diag(q), q = force / length. compas_fd builds `Ai = Ci.T Q Ci`,
  `Af = Ci.T Q Cf`, solves `Ai x = p[free] - Af x[fixed]` with scipy's spsolve, and reports forces
  q * length and residuals p - C^T Q C x (`fd_numpy.py`, `fd_numerical_data.py` lines 74-82).
  jax_fdm writes the same: stiffness `Cf.T @ diag(q) @ Cf` over the free nodes, right-hand side the
  free loads minus `Cf.T diag(q) Cb xyz_fixed` (`models.py` 801-856). **P (two independent
  implementations; the 1974 paper refused, so the paper's own notation is S). Confidence high**:
  e01 reproduces both with an assembly that never forms C (the form an ES5 port takes).
- The three axes decouple; the solve is linear, so the starting coordinates of free nodes do not
  matter (e01(a), checked with a start at (0.7, 1.6, 3.0)). **P (measured). High.**
- Uniqueness: with q > 0 D is a weighted graph Laplacian with the supports' rows removed, positive
  definite when every free node has a path to a support. **S (follows from the structure; measured on
  e01(b); Schek's own statement not read). Medium-high.**
- Edge cases (all measured in e01): a free node not connected to a support: singular; q = 0 on all
  edges at a node: singular; all q < 0 with downward load gives the mirror image, a vault in pure
  compression (centre z = +1.125 against -1.125); scaling all q by s scales the sag by 1/s; mixed
  signs can make D indefinite or singular (not measured; U). FDM controls force/length, not length
  or force: prescribed forces or lengths need an outer iteration (compas_fd's
  `fd_constrained_numpy`, not read in detail; U).

**A.2 Dynamic relaxation.**

- Updates (central differences, leapfrog): v(t + dt/2) = v(t - dt/2) + dt R(t) / M;
  x(t + dt) = x(t) + dt v(t + dt/2); residual R_i = p_i + sum_j (T_m / l_m)(x_j - x_i); constrained
  nodes' residuals zeroed. **S: Wikipedia's article citing Lewis 2003 and Wakefield 1999; the same
  residual in compas 1.x `dr.py` `update_R` (P for that code). High.**
- Fictitious masses: Barnes's lumped mass m_i = lam (dt^2 / 2) k_i, dt taken as 1, k_i the node's
  direct stiffness (the largest term for membranes, eq. 5). **S: Rodriguez et al. 2011 eq. 4-5
  citing Barnes 1988 and 1999.** compas 1.x uses M_i = sum over the node's edges of 0.5 dt^2 q
  (P). Oasys GSA builds them from nodal translational and rotational stiffness (P, practitioner,
  no formula). **High.** e01 shows lam = 1 is safe and the sharp limit on that net is 0.854.
- Kinetic damping: watch total kinetic energy; when it falls, the peak has passed: stop, move the
  nodes back to the estimated peak, zero every velocity, restart. Oasys estimates the peak by a
  parabola through the last energies (P, practitioner); a review summarised by the search cites
  Topping's assumption that the peak lies at the middle of the last step (U). **High for the
  principle.**
- The correction used in e01: x* = x(t+dt) - 1.5 dt v(t+dt/2) + (dt^2/2) R(t)/M. Algebra:
  x(t+dt) - dt v(t+dt/2) = x(t), and v(t+dt/2) - dt R(t)/M = v(t-dt/2), so x* = x(t) - (dt/2)
  v(t-dt/2), the position half a step before t: the midpoint assumption. Restart with
  v(dt/2) = (dt/2) R/M. **U for its attribution to Barnes 1999** (the paper was not reachable; the
  formula is from memory of the literature and derived here); **P for its effect** (e01: converges;
  omitted, it does not). Before code, read Barnes 1999 or Lewis 2003 to confirm.
- Viscous damping in compas 1.x: v_new = A v + B dt R/M with A = (1 - c/2)/(1 + c/2),
  B = (1 + A)/2, c = 0.1 by default, integrated with RK4; stop when the largest residual is under
  tol1 = 1e-3 or the largest step under tol2 = 1e-6 (P, `dr.py`). **High.**
- Convergence: the largest free-node residual under a tolerance (compas; Oasys; Wikipedia step 6).
  A displacement criterion alone can stop early during a slow drift (compas uses either). **P. High.**
- Equivalence with FDM: a spring with rest length 0 and stiffness k pulls with k (x_j - x_i), which
  is the FDM term with q = k; so DR's equilibrium is FDM's. With rest length L0 > 0 the force
  density is k (1 - L0/L), different per edge, and the shapes differ (e01: centre -1.772 against
  -1.125), but the DR net is an FDM equilibrium of those effective q (5.7e-10). **P (measured). High.**
- Kangaroo (Piker): closed-source solver, now shipped with Rhino; its goals are open (K2Goals,
  Apache-2.0). A goal returns, per particle, a target move and a weight: Spring moves both ends half
  the stretch with weight 2k; ConstantTension moves them together with weight strength/length;
  Unary is a constant force with weight 1 (P for the goals). How the solver combines them (a
  weighted average of moves, projection-style) is described in Senatore and Piker 2015, refused
  here: **U**.

**A.3 Thrust network analysis (later).** Block's TNA (Block and Ochsendorf 2007; Block's 2009 MIT
thesis) finds compression-only funicular shells for vertical loads: a form diagram in plan and its
reciprocal force diagram give the horizontal equilibrium; the heights follow from one linear solve
much like FDM's z-axis, with the force diagram's scale setting the rise. compas_tna (MIT, licence
read) implements it. It needs the reciprocal-diagram machinery and a horizontal-equilibrium
iteration, so it is a later phase; FDM with negative q already gives compression-only vaults for
studies. **S/U (the papers not read here). Medium.**

**A.4 From a form-found net to the frame solver (V125).**

- The app's analytical model takes only columns and beams (`bimIsFrameMember`,
  `analytical-model.js` 59-61); supports are `fixed`, `pinned` or `free` per node (line 14); the
  solver is linear, 6 degrees of freedom per node, with end releases condensed out
  (`frame-solve.js` 49-83, 107-188). **P (app code).**
- The hand-over: each edge a member (its section and material chosen by the user), each fixed node
  a support (pinned for a cable net, fixed for a gridshell's springing), free nodes as joints, the
  loads that shaped the net as nodal loads, and the FDM forces q L as the expected axial forces to
  compare with. **Recommendation, from the code.**
- What breaks: (1) a pin-ended net leaves every node's rotations unrestrained, so the linear solve
  is singular unless members keep some bending (a gridshell) or a truss element is added; (2) a
  cable's out-of-plane stiffness comes from its prestress (geometric stiffness), which a linear
  frame solve does not have, so a nearly flat net is near-singular across its surface; (3)
  tension-only (cables, membranes) and compression-only (masonry) members need an iteration that
  drops members whose force has the wrong sign and solves again. So "tension-only" in the app means:
  FDM with q > 0 guarantees all-tension at the form-found load; under any other load a cable can go
  slack, which only a nonlinear analysis shows. **P (code) for the facts; S for the mechanics
  (standard structural analysis, not read for this note). Medium.**

### B. Stormwater runoff

**B.1 Flow direction, depressions, accumulation.**

- D8: each cell drains to the one of its eight neighbours with the steepest drop per distance,
  diagonals at sqrt(dx^2 + dy^2). WhiteboxTools takes the first strictly steepest neighbour (ties to
  the first in its order) and marks a cell with no positive drop 0 (`d8_pointer.rs` 233-295). Its
  accumulation starts every cell at 1 and passes values downstream in topological order (cells with
  no inflow first) (`d8_flow_accum.rs` 474-560). **P (code; the 1984 paper not read). High.**
- D-infinity: eight triangular facets around the cell; on each, the downslope vector (s1, s2) from
  the centre and two neighbours; if its angle falls outside the facet, the steeper edge is used; the
  steepest facet gives one angle, and flow is split between the two neighbours bounding it in
  proportion to how close the angle is to each; ties go to the first facet; unresolved cells take a
  D8 direction after filling. **P (Tarboton 1997 pp. 310-313; the same in Whitebox
  `dinf_pointer.rs`). High.**
- On a TIN: the flow on a triangle follows the plane's steepest descent (minus the gradient); on
  the vertex graph, Landlab's FlowDirectorSteepest takes the steepest link to a neighbour on both
  rasters and Voronoi-Delaunay grids (P, code docstring). Following flow across triangles produces
  paths that cross edges and can loop on flat or concave edges (Jones, Wright and Maidment 1990: U,
  not read). **Medium.**
- Depressions: Planchon and Darboux's definition (as Barnes et al. quote it): the filled surface is
  at or above the original, every cell has a path to the edge descending by at least epsilon, and
  it is the lowest such surface. Priority-Flood seeds a priority queue with the edge cells, pops the
  lowest, raises each unvisited neighbour to at least the popped height, and pushes it; O(n log n)
  for floating point; it works on 4-, 8-connected grids and meshes; Algorithm 3 (+epsilon, with
  NextAfter) makes the filled areas drain. NoData is treated as lower than any cell, so a site's
  outline is an outlet. **P (arXiv 1511.04463, Algorithms 1, 3; pp. 2-5). High.**
- Whitebox advises breaching (least-cost cuts through dams such as a road embankment) over filling
  for most uses (P, `fill_depressions.rs` doc comment): counter-evidence that filling is always the
  right default. For a designed site (pads, kerbs, inlets), the designer's own grading is the truth,
  so a filled pit is better shown as a ponding area than silently raised. **Medium.**
- Licences (read at the source): WhiteboxTools MIT; Landlab MIT; compas_tna MIT; pysheds GPL-3.0;
  RichDEM GPL-3.0; TauDEM GPL-3.0 (`GPLv3license.txt`); GRASS GPL (COPYING). Only the MIT methods'
  code could be adapted; the GPL ones are read for method only, credited. **P. High.**

**B.2 Peak flow: the rational method.**

- HEC-22 4th edition (FHWA-HIF-24-006, February 2024) eq. 4.1: Q = C I A / Ku, Ku = 1.0 customary
  (ft3/s, in/h, ac), 360 SI (m3/s, mm/h, ha); weighted C = sum(Cx Ax)/A (eq. 4.2); its assumptions
  (whole catchment contributing, uniform intensity over tc, the peak's return period equal to the
  rainfall's, C fixed across storms); FHWA does not endorse the frequency correction factor; HDS-2
  limits the method to areas under 200 ac (80 ha). **P (pp. 23-26). High.**
- HEC-22 Table 4.1 (ASCE 1960), C ranges: roofs 0.75-0.95; asphalt streets 0.70-0.95; concrete
  0.80-0.95; drives and walks 0.75-0.85; lawns on heavy soil 0.13-0.17 (flat, 2%), 0.18-0.22
  (2-7%), 0.25-0.35 (steep, 7%); on sandy soil 0.05-0.10, 0.10-0.15, 0.15-0.20; parks 0.10-0.25;
  single-family 0.30-0.50; downtown 0.70-0.95. Higher values for steep areas and rarer storms.
  **P (p. 26). High.**
- TxDOT Table 4-10 (the same family of table) disagrees in six rows: neighbourhood business
  0.30-0.70 (HEC-22 0.50-0.70); suburban 0.35-0.40 (0.25-0.40); apartments 0.30-0.70 (0.50-0.70);
  light industrial 0.30-0.80 (0.50-0.80); asphalt 0.85-0.95 (0.70-0.95); concrete 0.90-0.95
  (0.80-0.95); drives and walks 0.75-0.95 (0.75-0.85). Roofs and lawns agree. **P (both). High**: C is
  a jurisdiction's record with its edition, as V167's registry keeps standards.
- The minimum duration differs: HEC-22 cites common practice of 5 minutes (p. 158, examples use
  "5 min minimum"); TxDOT requires 10 minutes. **P. High.** Another registry field.
- Time of concentration: HEC-22's velocity (segment) method: sheet flow by the kinematic-wave form
  tt = (Ku / P2^0.5) (n L / S^0.5)^0.8, minutes, Ku = 0.42 customary, 5.5 SI (eq. 4.3). The text
  extraction scrambled the layout; the grouping is read from the constant: 0.42 min = 0.007 h, the
  coefficient of NRCS TR-55's sheet-flow equation as commonly quoted, and (S^0.5)^0.8 = S^0.4 (S;
  confirm against the PDF page before code); shallow concentrated flow V = Ku k Sp^0.5 with Sp in percent (eq. 4.4, Table
  4.3: paved 0.619, unpaved 0.491, grassed waterway 0.457, short grass pasture 0.213); channels by
  Manning (eq. 4.5). **P (pp. 27-29). High except eq. 4.3's grouping.**
- Kirpich (TxDOT eq. 4-15): t_ch = K L^0.770 S^-0.385, minutes, K = 0.0078 (ft) or 0.0195 (m); TxDOT
  applies it to channel flow within Kerby-Kirpich, for watersheds 0.25 to 150 square miles, and
  adds 0.0005 to slopes under 0.002. Outside that range (a building site) it is an extrapolation.
  **P (equation image read). High.** The FAA formula and NRCS TR-55 were not read (U).
- HEC-22's own Example 4.3 prints "31.4 ft3/s (89 m3/s)": 31.4 ft3/s is 0.89 m3/s (e02). An erratum,
  recorded so no test copies it. **P.**

**B.3 Rainfall intensity data.**

- NOAA Atlas 14 PFDS: `https://hdsc.nws.noaa.gov/cgi-bin/new/fe_text_mean.csv?lat=&lon=&data=intensity|depth&units=metric|english&series=pds|ams`
  (the `cgi-bin/hdsc/new/` path now answers 301 to it). Keyless; 1.2 KB; about 1 s. The response is
  served as `text/html` with `Content-Disposition: attachment; filename="PF_Intensity_Metric_PDS.csv"`:
  a header (volume, version, project area, coordinates), then one row per duration (5-min to
  60-day) and one column per ARI (1 to 1000 years; AMS: AEP 1/2 to 1/1000). **P (tested).**
- Metric values come rounded to whole mm/h (Philadelphia 10-yr 10-min: 131), English to three
  figures (5.17 in/h = 131.3 mm/h); at long durations the metric table rounds to 0 or 1. Read the
  English table and convert. **P. High.** The confidence-bound columns of the web page are not in
  this CSV (U: `fe_text_upr`/`lwr` names not tested).
- Outside the project areas: London returned `Error 3.0: Selected location is not within a project
  area`. **P.**
- CORS: no `Access-Control-Allow-Origin` with an Origin header; OPTIONS returns 500. A browser page
  cannot fetch it. **P. High.** By the owner's rule, the server is named, not proxied: the user
  pastes the CSV or types the intensity.
- Terms: NWS web information is in the public domain unless noted, used freely if not claimed as
  one's own, not implying endorsement, and not modified and presented as official. **P
  (weather.gov/disclaimer).** Credit "NOAA Atlas 14, Volume N, Version N" as the CSV names it.
- NOAA Atlas 15: the Montana pilot was released 2024-09-26. The HDSC progress report (July-September
  2025, issued December 2025) still said final CONUS studies in 2026; the Atlas 15 information page
  (read 2026-11-21) says CONUS preliminary estimates no earlier than September 2026, published no
  earlier than September 2027, outside CONUS a year later each. Atlas 14 stays the standard until
  then. **P (both; the later page taken). High.** It will add non-stationary (future) estimates;
  the app should keep the atlas and its version on each result.
- Non-US: Canada's ECCC engineering climate IDF files (station-based, keyless zip, version 3.40 of
  2025-12-05 listed; no CORS header) (P for access; licence not read: U). Australia's BoM design
  rainfalls refused a script (403). Others not searched (U).

## 5. The alternatives compared

### A. Form-finding

Criteria, before the comparison: (1) exact equilibrium for test data; (2) handles rest lengths,
elastic members and goals beyond nets; (3) interactive, step by step; (4) parameters a user must
tune; (5) ES5 code size, no library; (6) hand-over to the frame solver.

| Method | (1) | (2) | (3) | (4) | (5) | (6) |
|---|---|---|---|---|---|---|
| FDM, one linear solve (Schek) | Yes, closed forms (e01) | No: q only; lengths and forces need an outer loop | One shot; re-solve on each q change (fast) | None but q | Small: sparse assembly and Cholesky or CG | Forces q L given directly |
| DR, kinetic damping (Barnes) | To a tolerance (8e-10) | Yes: any force law, rest lengths, elastic | Yes, natural animation | dt, lam (1 safe), tolerance | Small | Forces from the springs |
| DR, viscous (compas 1.x, RK4) | To a tolerance | Yes | Yes | c and lam; 5x the iterations here | Small, RK4 doubles the work | Same |
| Projection goals (Kangaroo2-style) | To a tolerance | Yes, the widest (planarity, collisions) | Yes | Goal weights | Medium; solver unpublished (U) | Geometry first, forces derived |
| Nonlinear FE (Newton, geometric stiffness) | Yes | Yes | No | Load steps | Large | Best (same model analyses) |
| Thrust network analysis | Yes, for vertical loads | Compression shells only | No | Force-diagram scale | Large | Compression forces |

**Recommendation:** FDM first, DR (kinetic) second, TNA later. What would change it: if the owner
wants live dragging of goals in the first phase, DR first (FDM becomes its warm start and its test).

### B. Runoff

Criteria: (1) correct drainage everywhere (no loops, every cell reaches an outlet); (2) realistic
spread on planes and ridges; (3) code size, ES5; (4) speed on 200 x 200; (5) works on the app's
TIN; (6) licence of the code read.

| Method | (1) | (2) | (3) | (4) | (5) | (6) |
|---|---|---|---|---|---|---|
| Grid D8 + Priority-Flood+epsilon | Yes (Barnes's guarantee) | Grid bias: 8 directions only | Smallest | ~240 ms CPython | Sample the TIN with `bimTinIndex().at` | Method from MIT/paper |
| Grid D-infinity + the same fill | Yes (D8 for flats) | Better on planes | Small-medium | Similar | Same | Paper P; Whitebox MIT |
| Multiple flow direction (Freeman/Quinn) | Yes | Over-dispersed on hillslopes (Tarboton) | Small | Similar | Same | Not read (U) |
| TIN triangle steepest descent | Needs care at edges and flats | Exact on the surface | Medium-large | Fast | Native | Not read (U) |
| TIN vertex graph, steepest link + Priority-Flood | Yes (Priority-Flood works on meshes) | Sparse where triangles are large | Small | Fast | Native, coarse | Landlab MIT |
| Breaching (least cost) instead of filling | Yes | Keeps valley lines through dams | Larger | Slower | Same | Whitebox MIT |

**Recommendation:** grid D8 with Priority-Flood+epsilon on a TIN sampled at a user cell size
(default so the site is about 200 cells across), accumulation in m2, then Q per cell by the
rational method; filled cells shown as ponding. D-infinity as a later option. What would change it:
a site where the TIN's triangles are much finer than the grid (kerbs, swales) would favour the TIN
vertex graph, or a finer grid.

Peak-flow alternatives: the rational method (here); NRCS TR-55 and curve numbers (volumes,
larger areas: not read, U); EPA SWMM (public domain, C; time series and pipes: not read, U). The
rational method fits a site under 80 ha and is what HEC-22 and state manuals use for inlets.

## 6. The experiments

### e01 `formfinding.py` (run 2026-11-21, CPython 3.13.18, numpy 2.5.3)

(a) One free node joined to (0,0,0), (2,0,0), (2,2,0), (0,2,0), q = 1, p = (0,0,-1): the node goes to
the corners' mean plus p / sum q: **(1, 1, -0.25)**; q = 2 gives -0.125; q = -1 gives +0.25. Each
edge 1.436141 m long with force 1.436141 kN; the vertical components sum to 1. Exact.

(b) 5 x 5 nodes at 1 m, the 16 boundary nodes fixed at z = 0, 9 free, q = 1 on all 40 edges, -1 kN at
each free node. Pure Python against numpy: 8.9e-16. Residual 1.8e-15; reactions sum to 9.000000. The
plan stays on the grid (x, y unchanged). Exact values by symmetry:

| Node (i, j) | x | y | z |
|---|---|---|---|
| (1, 1) corner of the free block | 1 | 1 | **-11/16 = -0.6875** |
| (2, 1) edge middle | 2 | 1 | **-7/8 = -0.875** |
| (2, 2) centre | 2 | 2 | **-9/8 = -1.125** |

q = 4: centre -0.28125 (1/4). q = -1: centre +1.125. Edge forces 1.000 to 1.329 kN, all tension.
A free node with no path to a support: singular, caught.

(c) DR on the same net from the flat start, zero rest lengths, k = 1, dt = 1, tolerance 1e-9 on
the largest residual:

| Damping | lam | Iterations | KE peaks | max abs(x_DR - x_FDM) |
|---|---|---|---|---|
| kinetic | 1.0 | 81 | 20 | 8.2e-10 |
| kinetic | 1.5 | 62 | 21 | 2.2e-10 |
| viscous c = 0.1 | 1.0 | 398 | - | 4.0e-10 |
| viscous c = 0.1 | 1.5 | 389 | - | 7.7e-10 |
| kinetic, no peak correction | 1.0 | 200 000 (not converged) | 50 000 | - |
| kinetic | 0.45 | NaN within 2000 | | |
| undamped | 0.86 / 0.85 | bounded / NaN | | |

Rest length 0.5: centre -1.771723 (FDM with q = 1: -1.125); FDM with the converged effective
q = k(1 - L0/L) reproduces the DR net to 5.7e-10.

### e02 `runoff.py` (same run)

(a) z = 10 - row - 0.5 col (row 0 north, 1 m cells), pit at (1,1) set to 6.0 (plane 8.5; lowest
neighbour 7.0).

    elevation           D8 before        accumulation before
    10.0 9.5 9.0 8.5    SE  S SW  S       1 1 1 1
     9.0 6.0 8.0 7.5     E  .  W  S       1 8 1 2
     8.0 7.5 7.0 6.5    NE  N SE  S       1 1 1 3
     7.0 6.5 6.0 5.5     E  E  E  .       1 2 3 8

Before filling, 8 cells end in the pit and only 8 reach the outlet (3,3). Priority-Flood with
epsilon = 0 raises the pit to 7.000 and leaves it a flat with no direction; with epsilon = 0.001 to
7.001, it drains SE:

    D8 after +epsilon    accumulation
    SE  S SW  S          1 1 1 1
     E SE SE  S          1 5 1 2
    SE SE SE  S          1 1 6 4
     E  E  E  .          1 3 5 16

All 16 cells reach (3,3). Edge cells drain only inward (the grid's edge is not an outlet unless
lowest); the site outline as an outlet is a choice to make (section 7).

Timing proxy, 200 x 200 random relief: fill 100 ms (11 637 cells raised), D8 110 ms, accumulation
31 ms, CPython. A browser was not measured.

(b) Composite C = (0.9 x 1 + 0.3 x 1)/2 = **0.600**; Q = 0.6 x 100 x 2 / 360 = **0.3333 m3/s
(333.3 L/s)**; with 0.00278: 0.3336 (+0.08%). In customary units with Ku = 1: 4.9421 ac, 3.9370 in/h,
11.674 ft3/s = 0.3306 m3/s, 0.83% lower, because 1 ac-in/h is 1.0083 ft3/s. With Philadelphia's
10-yr intensities from PFDS: 5-min 6.47 in/h (164.3 mm/h) gives 0.548 m3/s; 10-min 5.17 in/h
(131.3 mm/h) gives 0.438 m3/s. Kirpich, L = 200 m, S = 0.02: 5.20 min. HEC-22 eq. 4.4, paved,
2%: 0.875 m/s, 200 m in 3.81 min.

Note the brief's C = 0.9 for roofs is inside HEC-22's 0.75-0.95; C = 0.3 for lawn is above every
lawn range in Table 4.1 (0.05-0.35, 0.3 only for steep heavy soil): a worked number, not a
recommended value.

## 7. Edges

- FDM: a free node with no path to a support; zero or negative q; mixed signs; coincident nodes
  (zero length: force q L = 0, direction undefined); loads with q tiny (huge sag); q scaling.
- DR: lam below the stability limit diverges (0.85 on e01's net); the restart without the peak
  correction can cycle; zero-length springs at the start (direction undefined); tolerances in
  kN, so a net in N needs a scaled tolerance.
- Units: the app's analysis is kN, m, kPa (`analytical-model.js` line 12); q in kN/m.
- D8: ties (first in a fixed order); flats after a plain fill; edge cells; cells outside the TIN
  (`at()` returns null) as NoData, treated as lower than any cell, so the TIN's outline drains out.
- Rational: Ku = 360 against 0.00278 (0.08%); customary Ku = 1 (0.83%); the minimum tc (5 or 10
  min by jurisdiction); the area limit 80 ha; C by edition and jurisdiction; intensity must match
  tc's duration and the chosen return period; PFDS metric values rounded.
- PFDS: the 301 from the old path; locations outside project areas return an error text, not CSV;
  AMS columns are AEPs, PDS columns ARIs.

## 8. What the app already has

- `src/js/engine/terrain/terrain-tin.js` 68-76: `bimTerrainTin(o)` returns plan points `P` [x, z],
  heights `H`, triangles `tris`, cached by revision; 93-108: contours.
- `src/js/engine/terrain/grading.js` 29-61: `bimTinIndex(tin)` builds a uniform cell index and
  `at(x, z)`, the ground height by barycentric interpolation (null outside): the sampler a runoff
  grid needs. Lines 375-399: slope arrows, a display to reuse for flow arrows.
- `src/js/engine/structure/analytical-model.js` 12-61, 87-148 and `frame-solve.js` 107-288: the
  analytical model and linear frame solver (supports, releases, kN and m).
- The model graph (V230, `docs/research/research-algorithmic-design.md` part 4.1): FDM and runoff fit
  as nodes (inputs: a net or the terrain and parameters; outputs: geometry and fields).

## 9. Risks and threats to validity

- The primary papers for FDM (Schek), DR (Day, Barnes) and D8 (O'Callaghan and Mark) were not read;
  the equations rest on implementations and secondary sources that agree.
- The kinetic-damping correction's attribution is U; its effect is measured only on one net.
- The DR iteration counts are for one small, regular net; real membranes may favour viscous damping.
- The timing is CPython, not a browser.
- HEC-22's Table 4.1 is from ASCE 1960: old field data; Kentucky's copy of the manual was read
  (FHWA's own URL answered 200 but was not compared byte for byte).
- PFDS behaviour tested from one location and one day.

## 10. What is still open (U)

- Barnes 1999's own correction formula and restart rule (paper refused; read Lewis 2003 or the paper).
- Senatore and Piker 2015 (refused by core.ac.uk, EPFL, UCL): Kangaroo2's solver scheme.
- Schek 1974's own statement of uniqueness and his examples.
- HEC-22 eq. 4.3's grouping, inferred from its constant (S); confirm on the PDF page.
- NRCS TR-55, the FAA formula, SWMM; Jones et al. 1990 on TIN flow.
- ECCC IDF licence; any other keyless non-US IDF source.
- A 2019 comparison favouring viscous damping (SN Applied Sciences 1:1529), seen only as a summary.

## 11. The owner's decisions (to ask)

1. Form-finding order: FDM first, then DR (recommended), or DR first for live dragging?
2. Where form-found nets live: a model-graph node (V230) whose output becomes members, or a
   standalone tool?
3. Hand-over to the frame solver: add a truss (axial-only) element and tension-only iteration, or
   hand over only gridshells (members with bending) for now?
4. Rainfall: typed intensity plus a pasted PFDS CSV (no CORS, recommended), or nothing until a
   source with CORS exists?
5. Runoff coefficients: HEC-22 4th ed. Table 4.1 as the default registry record, with TxDOT and
   others as editions per place?
6. Minimum time of concentration: 5 min (HEC-22 practice) by default, 10 min where TxDOT applies?
7. Depressions: fill (and show ponding) by default, or breach?
8. Grid cell size for runoff: fixed (1 m) or sized to about 200 cells across the site?

## 12. References

All read 2026-11-21.

| Source | URL | What was read | Level |
|---|---|---|---|
| compas_fd (BRG, ETH Zurich), MIT, @7ee3c5a | https://github.com/blockresearchgroup/compas_fd | `solvers/fd_numpy.py`, `solvers/fd_numerical_data.py`, LICENSE | P |
| jax_fdm (R. Pastrana), MIT, @7dc5122 | https://github.com/arpastrana/jax_fdm | `equilibrium/models.py` 196-972, LICENSE | P |
| compas 1.17.10, MIT | https://raw.githubusercontent.com/compas-dev/compas/v1.17.10/src/compas/numerical/dr/dr.py | whole file | P |
| K2Goals (D. Piker), Apache-2.0, @2ec9395 | https://github.com/Dan-Piker/K2Goals | Spring.cs, Unary.cs, ConstantTension.cs, LICENSE | P |
| compas_tna licence | https://raw.githubusercontent.com/BlockResearchGroup/compas_tna/main/LICENSE | MIT | P |
| Wikipedia, Dynamic relaxation | https://en.wikipedia.org/w/index.php?title=Dynamic_relaxation&action=raw | equations, steps, damping | S |
| Oasys GSA 10.2 theory, Dynamic Relaxation Analysis | https://docs.oasys-software.com/structural/gsa/version/10.2.0/references-theory/dynamic-relaxation-analysis.html | damping, solution process, fictitious masses | P (practitioner) |
| Rodriguez, Rio, Cadou, Troufflard 2011, preprint (Thin-Walled Structures) | http://oss.jishulink.com/caenet/forums/upload/2015/10/25/113/13289042109463.pdf | section 2 (eq. 1-8) | S |
| Comparative analysis of elastic sheets (arXiv 1411.6823) | https://arxiv.org/pdf/1411.6823 | DR, kinetic damping paragraph | S |
| Barnes 1999, IJSS 14(2) 89-104 | https://journals.sagepub.com/doi/10.1260/0266351991494722 | not read (pointer) | U |
| Schek 1974, CMAME 3(1) 115-134 | https://www.sciencedirect.com/science/article/pii/0045782574900450 | refused (403) | U |
| Senatore and Piker 2015, CAD 61 | https://infoscience.epfl.ch/record/255716 | refused (429/403) | U |
| Barnes, Lehman, Mulla 2014, Priority-Flood (arXiv 1511.04463) | https://arxiv.org/pdf/1511.04463 | sections 1-2, Algorithms 1 and 3 | P |
| Tarboton 1997, WRR 33(2) 309-319 | https://hydrology.usu.edu/dtarb/96wr03137.pdf | abstract, method pp. 310-313 | P |
| WhiteboxTools, MIT | https://github.com/jblindsay/whitebox-tools (whitebox-tools-app/src/tools/hydro_analysis/) | d8_pointer.rs, d8_flow_accum.rs, fill_depressions.rs (doc), dinf_pointer.rs, LICENSE.txt | P |
| pysheds, GPL-3.0 | https://github.com/mdbartos/pysheds | LICENSE, sgrid.py (flowdir, fill_depressions) | P |
| RichDEM, GPL-3.0 | https://raw.githubusercontent.com/r-barnes/richdem/master/LICENSE.txt | licence | P |
| TauDEM, GPL-3.0 | https://github.com/dtarb/TauDEM | GPLv3license.txt | P |
| GRASS GIS, GPL | https://raw.githubusercontent.com/OSGeo/grass/main/COPYING | licence | P |
| Landlab, MIT | https://github.com/landlab/landlab | LICENSE.md, flow_director_steepest.py docstring | P |
| FHWA HEC-22 4th ed., FHWA-HIF-24-006 (Feb 2024), Kentucky's copy | https://transportation.ky.gov/Highway-Design/Drainage%20Manual/HEC-22(2024-02).pdf | 4.2.2 (pp. 23-29), Example 4.1, 4.3, Tables 4.1-4.3, 9.2.2 | P |
| TxDOT Hydraulic Design Manual, ch. 4 s. 11-12 | https://www.txdot.gov/manuals/des/hyd/chapter-4--hydrology/section-12--rational-method.html ; .../runoff-coefficients.html ; .../section-11--time-of-concentration.html | limits, Table 4-10, eq. 4-15 (image) | P |
| NOAA Atlas 14 PFDS | https://hdsc.nws.noaa.gov/cgi-bin/new/fe_text_mean.csv | responses for 39.9526, -75.1652 and 51.5, -0.12; headers; OPTIONS | P |
| NWS disclaimer | https://www.weather.gov/disclaimer | use of NOAA/NWS data | P |
| NOAA Atlas 15 information page | https://water.noaa.gov/about/atlas15 | timeline | P |
| HDSC progress report Jul-Sep 2025 | https://www.weather.gov/media/owp/oh/hdsc/docs/202512_HDSC_PR.pdf | section III | P |
| ECCC engineering climate IDF | https://collaboration.cmc.ec.gc.ca/cmc/climate/Engineer_Climate/IDF/ | directory listing, headers | P (access only) |
| BoM design rainfalls | http://www.bom.gov.au/water/designRainfalls/revised-ifd/ | refused (403) | U |
| Efficiency of DR methods for membranes, SN Appl. Sci. 2019 | https://link.springer.com/article/10.1007/s42452-019-1529-6 | script got a 3 KB stub; seen as a search summary | U |

## After the independent check (2026-11-21)

`independent-check.md` re-read F1 to F6. One addition:

- Oasys GSA states its fictitious-mass rule: twice the sum of the translational stiffness of the connected
  elements. It scales differently from Barnes's lam dt^2/2 sum k; both are recorded. The app's work order
  uses half the sum of k (Barnes with lam 1, dt 1), which the tests show converging in 81 iterations. The
  kinetic-damping position correction stays U for its attribution (derived and measured here).
