# V277a research: tensors and rotations, the first layer of the math core

Phase V277a of the World Engine (`plan-world-physics.md`, `plan-world-physics-math.md` part 9). Research
2026-11-24, under `research-protocol.md`. Side files: `research-tensors-rotations/search-log.md`,
`research-tensors-rotations/independent-check.md`. Experiments: `experiments/v277a-tensors/` (ref.mjs and
e01 to e08, each with its results file).

## 1. Abstract

**Question.** How should the app's math core represent vectors, rotations and the symmetric tensors of mechanics
(stress, strain, inertia, conductivity, elasticity), so that every later physics phase can rely on them, the
libraries we already ship (three.js, Jolt) and the formats we exchange (glTF, IFC) need no guesswork at their
boundaries, and the results are exact to rounding?

**Answer.** Store orientation as a unit quaternion in `[x, y, z, w]` order with Hamilton's algebra: glTF, three.js
and Jolt all use exactly that, so their adapters copy four numbers. Convert matrices to quaternions with Shepperd's
pivot (the trace-only formula fails near half a turn: e02). Integrate orientation with the exponential map (a
first-order update blows up in an hour at 60 Hz: e01b). Keep Euler angles for what people type only (they lose the
matrix by the distance to gimbal lock: e04). Hold symmetric rank-2 tensors in Mandel's six components, where
rotation is an orthogonal 6x6 matrix and a rank-4 stiffness rotates as Q C Q^T (Voigt's is not orthogonal: e06).
Find principal values with cyclic Jacobi (the closed form's eigenvectors fail on equal eigenvalues, which every
symmetric body has: e05). Give orthotropic timber its nine constants from the USDA Wood Handbook, deriving the
minor Poisson's ratios from reciprocity (the tabulated ones break it by up to 53 %, and 16 of 19 softwoods have none:
e07). Write it as plain ES5 arrays returned by small functions (10 ns a cross product, near the 7.5 ns floor; a
Float64Array per result costs 38 ns: e08).

**Recommendation.** Build `core/math` as described in part 5, with the eleven decisions of part 11.

## 2. The question and the hypotheses

The question: which representations and algorithms, measured here and checked against their primary sources, give
the core exact, convention-safe rotations and tensors at a cost the real-time world (plan Stage C) can carry?

| # | Hypothesis (falsifiable) | Outcome | Evidence |
|---|---|---|---|
| H1 | glTF, three.js and Jolt store a quaternion as [x, y, z, w] with Hamilton's algebra, so no conversion but a copy is needed | **Held** | glTF 2.0 section 3.4 and node TRS; three.js Quaternion; Jolt Quat.h; Eigen stores the same but its constructor takes w first (an edge, part 7) |
| H2 | Composing a million rotations drifts the quaternion norm past 1e-12 unless it is renormalised | **Failed** (drift only 1.2e-13) | e01; the real drift is in integration, H2b |
| H2b | A first-order orientation update at 60 Hz drifts measurably within an hour; the exponential map does not | **Held**, far beyond the claim | e01b: norm 3.8e6 unnormalised, 0.21 orientation error renormalised, 3e-11 with the exp map |
| H3 | The trace-only matrix-to-quaternion formula fails near a half turn; Shepperd's pivot stays at rounding | **Held** | e02: 4.2e-3 at 1e-6 rad from pi, NaN at pi; Shepperd 6.7e-16 everywhere |
| H4 | Euler ZYX round trips to 1e-12 except within about 1e-6 rad of gimbal lock | **Held** | e04: 4.1e-13 at 1e-5 rad, 2e-7 matrix error at 1e-7 rad |
| H5 | Cyclic Jacobi gives symmetric 3x3 eigenpairs to rounding in every case; the closed form loses accuracy on near-equal and wide-ranging eigenvalues | **Held**, and stronger: the closed form's eigenvectors fail outright on exactly equal eigenvalues | e05; Kopp 2008; Habera and Zilian 2021 |
| H6 | In Mandel form the rotation of a symmetric rank-2 tensor is an orthogonal 6x6 map; in Voigt form it is not, and Voigt's inner product needs the factor 2 on shear strains | **Held** | e06: Q^T Q = I to 3.1e-15 (Mandel); T^T T differs from I by 0.9997 (Voigt) |
| H7 | The Wood Handbook's orthotropic constants satisfy reciprocity within rounding and give a positive-definite compliance | **Half failed**: positive definite for all ten complete species; reciprocity broken by 3 % to 53 % | e07; the Handbook's own text (Eq. 5-1, "not always closely met") |
| H8 | Plain arrays are within 2x of the fastest vec3 form in V8; typed arrays allocated per result are slower | **Held** | e08: 10.2 ns array, 8.5 ns caller's output, 37.6 ns Float64Array per result, 7.5 ns floor |
| H9 | No element stores an orientation today; every rotation is baked into its geometry | **Held, with an exception**: a column stores a plan angle (`o.bim.rotation`) and a text its `o.rot` | Part 8 |

## 3. Method

- **Sources by kind** (part 12): the specification or standard (glTF 2.0, IFC 4.3's schema text, the SI Brochure),
  the government handbook (USDA Wood Handbook, 2021), papers (Shoemake 1985, Kopp 2008, Sola 2017, Habera and
  Zilian 2021), a practitioner's technical document (Eberly 2014/2021), four open implementations read as text
  (three.js, gl-matrix, Eigen, Jolt), a library's documentation (mechkit), and the app's own code.
- **Search log**: `research-tensors-rotations/search-log.md` (17 retrievals, 4 counter-evidence searches, 2 hosts
  refused or missing).
- **Experiments**: eight scripts in `experiments/v277a-tensors/`, deterministic (seeded generator), run in Node
  22.23.5, V8 12.4. Their results files hold the raw numbers. The reference functions in `ref.mjs` are the
  uncommitted-engine "reference version" the work orders' tests will be run against.
- **Independent check**: a separate research agent re-read the source of every fact the code uses (F1 to F15);
  results in `research-tensors-rotations/independent-check.md` and summarised in part 3.1.

### 3.1 The independent check

A separate research agent re-read every source (most fetched again independently; Wood Handbook Eq. 5-1 and Table
5-1 checked against a rendered image of the page) for F1 to F15, with F15 split into seven: 21 items, 18 confirmed,
3 not confirmed as worded, none unreadable (`research-tensors-rotations/independent-check.md`). The three were
corrected in this note: (F13) the SI Brochure gives the radian as 1 and calls m/m misleading (part 4.9); (F15a) UTM
files reach the model through `bimUtmInv` and `bimGeoToModel`, not the line first cited, with the same axes (part 7);
(F15c) `bimSunXyz` feeds two displayed readings, not one (part 8). Notes kept: gl-matrix's EPSILON is 1e-6; three.js,
gl-matrix and Jolt are MIT; columns' angle is also set in `ui/build-ui.js` line 665.

## 4. Findings, by topic

### 4.1 Quaternion conventions (H1)

Twelve quaternion conventions exist, from four binary choices (Sola 2017, section 3, Table 2): component order,
the algebra (ij = k, Hamilton; ij = -k, JPL), the function (passive or active), and the direction. **glTF 2.0**:
"rotation is a quaternion value stored in XYZW order where W is the scalar", and it "MUST be unit within the
margin of floating point precision"; the asset is right-handed, +Y up, front +Z, metres, radians (section 3.4,
node TRS). **three.js** `Quaternion(x = 0, y = 0, z = 0, w = 1)`. **Jolt** `Quat.h`: "we store the quaternion in a
Vec4 as [x, y, z, w]". **Eigen** stores [x, y, z, w] but its constructor takes (w, x, y, z) and warns about it. All
four use Hamilton's product. Level P, confidence high.

**Kinematics.** With the angular velocity in the world (global) frame, q' = 1/2 w_G (x) q; in the body frame,
q' = 1/2 q (x) w_L (Sola eqs. 201 and 99). The exponential map Exp(phi) = [u sin(theta/2), cos(theta/2)],
theta = |phi|, with a Taylor series near zero (eqs. 101 and the small-angle form). Level P, high.

### 4.2 Matrix to quaternion (H3)

The trace-only formula divides by 4w and w goes to zero at a half turn. Shepperd's method (1978) takes the largest
of w^2, x^2, y^2, z^2 as the pivot; three.js and gl-matrix (citing Shoemake's 1987 course notes) take the trace
branch only when it is positive, which keeps |w| > 1/2 there, and otherwise the largest diagonal: equivalent in
accuracy. e02 measured 2,000 random axes at each of nine angles: Shepperd's worst error 6.7e-16 at every angle; the
trace-only formula 2.3e-13 at 3 rad, 4.7e-11 at pi - 1e-2, 5.2e-7 at pi - 1e-4, 4.2e-3 at pi - 1e-6, and NaN at pi.
A half turn is common in a model (a door handed the other way, a mirrored bay): this matters. Level P (the open
code) and measured, high.

### 4.3 Interpolation (slerp)

Slerp(q1, q2; u) = sin((1 - u) theta)/sin(theta) q1 + sin(u theta)/sin(theta) q2 (Shoemake 1985); q and -q are the
same rotation, so the shorter arc takes -q2 when q1 . q2 < 0. Near-equal quaternions need a linear fallback. three.js
falls back below a dot of 0.9995 and renormalises; gl-matrix falls back at 1 - 1e-6 and does not. e03: at 1e-3 rad
apart, gl-matrix's result has a norm error of 3.1e-8 (three.js 2.2e-16); angle errors were at the measurement floor
(5e-8, set by acos near 1) for both. A counter-evidence search found a forum report of large errors from un-normalised
slerp in another engine (S1, level U, not used for numbers). Choice: three.js's form. Level P and measured, high.

### 4.4 Integrating orientation (H2, H2b)

Composing exact rotations hardly drifts: a million compositions leave the norm 1.2e-13 from one (e01), and a
hundred thousand matrix products stay orthogonal to 3.8e-14. Integrating does drift: spinning at a constant
w = (0.3, 1.2, -0.7) rad/s for an hour at 60 Hz (216,000 steps), the first-order update q += dt/2 (w (x) q) grows the
norm to 3.8 million; renormalised every step it stays unit but ends 0.21 off in orientation; the exponential-map
step Exp(w dt) (x) q ends 3e-11 from the closed form (e01b). Jolt integrates its own bodies; this governs our own
integrators (V277d) and any orientation we step ourselves. Level P (Sola) and measured, high.

### 4.5 Euler angles (H4)

R = Rz(psi) Ry(theta) Rx(phi) round trips to 4.4e-16 at ordinary pitch, 7.8e-15 at 1e-3 rad from 90 degrees and
4.1e-13 at 1e-5 rad; at 1e-7 rad the angles are no longer unique and the rebuilt matrix is 2e-7 off (e04). three.js's
default order is 'XYZ', applied in the object's local axes (Euler.js). Euler angles are therefore an input and display
form only, never stored. Level P and measured, high.

### 4.6 Symmetric tensors in six numbers (H6)

A symmetric rank-2 tensor has six independent components. **Voigt** writes stress as [s11, s22, s33, s23, s13, s12]
and strain with engineering shears [e11, e22, e33, 2e23, 2e13, 2e12]; the 6x6 matrices then depend on what they relate
(stress to strain or strain to strain). **Mandel** writes both as [a11, a22, a33, sqrt2 a23, sqrt2 a13, sqrt2 a12], an
orthonormal basis, so the 6-vector inner product equals the tensor double contraction and stress, strain, stiffness
and compliance convert alike (mechkit's documentation; S3). e06, 20,000 random rotations: the Mandel rotation matrix
satisfies Q^T Q = I to 3.1e-15 and reproduces R s R^T to 3.3e-16; the same construction in Voigt form differs from
orthogonal by 0.9997; both give the energy s:e to 4.4e-16 when Voigt's factor 2 is applied. Consequence: in Mandel
form a stiffness rotates as C' = Q C Q^T and inverts as an ordinary matrix. Level P (mechkit) and measured; the
paywalled originals (Mandel; Bond 1943; Helnwein 2001) at S. High.

### 4.7 Principal values and axes (H5)

Kopp (2008) compared Jacobi, QL, Cuppen and the analytical (Cardano) method: "Jacobi is the most accurate, but also
the slowest", the analytical method is over twice as fast "but becomes inaccurate or may even fail completely if the
matrix entries differ greatly in magnitude". Habera and Zilian (2021) show the closed form's invariants lose accuracy
near repeated eigenvalues. e05, 5,000 matrices per case, residual |A v - l v| / |A|:

| Case | Jacobi residual | Closed-form residual | Jacobi value error | Closed-form value error |
|---|---|---|---|---|
| Random | 5.5e-16 | 3.3e-13 | 1.3e-14 | 5.2e-13 |
| Two eigenvalues 1e-10 apart | 3.6e-16 | 8.2e-7 | 1.4e-15 | 2.0e-8 |
| Range 1e-8 (a thin rod's inertia) | 5.0e-16 | 0.52 | 2.3e-8 (absolute 2e-16) | 3.8e-8 |
| Range 1e-12 | 3.6e-16 | 0.34 | 2.0e-4 (absolute 2e-16) | 3.1e-4 |
| Two equal eigenvalues (a cylinder) | 3.7e-16 | 0.34 | 1.4e-15 | 1.4e-8 |

The relative error of a tiny eigenvalue is limited for both methods by the rounding in building the test matrix
(its absolute error is at rounding); the residuals are the decisive column. Cost: Jacobi 916 ns a call, the closed
form 257 ns (e05, 10^6 calls). Every cube, cylinder, square column and isotropic stress state has equal eigenvalues;
the closed form's eigenvectors fail on them. Eberly's noniterative robust solver (2014, revised 2021, CC BY 4.0) is
the fast alternative if profiling ever demands it. Level P and measured, high.

### 4.8 Orthotropic elasticity and timber (H7)

Wood is orthotropic: "Twelve constants (nine are independent)": three moduli E, three shear moduli G and six
Poisson's ratios, related by mu_ij/E_i = mu_ji/E_j (Eq. 5-1), with the first subscript the direction of applied
stress and the second that of lateral deformation; Table 5-1 gives E_T, E_R, G_LR, G_LT, G_RT as ratios to E_L,
Table 5-2 the six ratios, at about 12 % moisture content. The Handbook warns that Eq. 5-1 is "not always closely
met" and that mu_RL and mu_TL "are very small and are less precisely determined" (Wood Handbook, FPL-GTR-282, 2021,
chapter 5, pp. 5-1 to 5-3). e07 built the compliance of the ten species with every constant tabulated:

- every compliance is positive definite (the smallest eigenvalue of the normal block 0.88 to 0.99 of 1/E_L);
- the tabulated values break reciprocity by 3 % (African mahogany) to 53 % (Engelmann spruce), worst in S_12 (L-R);
- deriving the minor ratios from reciprocity (mu_RL = mu_LR E_R/E_L, mu_TL = mu_LT E_T/E_L) keeps every compliance
  positive definite (0.88 to 0.99 again) and makes it symmetric by construction;
- 16 of the 19 softwoods in Table 5-2 have no mu_RL or mu_TL at all, so derivation is required for them anyway.

A counter-evidence search (S4) found measured reciprocity failures reported for hardwoods (a Michigan State thesis,
level S) and minor ratios derived from reciprocity as practice (a Korean pine study, level S). Level P (the
Handbook) and measured, high for the method; the species values are averages of small samples, as the Handbook
says (part 9).

### 4.9 Units (SI)

The SI has seven base units (Table 2) and 22 coherent derived units with special names, among them the radian,
newton, pascal and joule (Table 4) (SI Brochure, 9th edition; the copy read is version V4.01 of June 2026). The
radian is expressed as 1, the angle subtended by an arc equal to the radius; the Brochure warns that writing it as
m/m "is not intrinsic and may be misleading", so the core treats angles as dimensionless radians, not as m/m. The core computes in coherent SI. The app's
structural model already works in kN, m and kPa (`structure/analytical-model.js` line 12), which is itself coherent
when mass is in tonnes (1 kN = 1 t m/s^2); it stays as it is, and its adapter scales at the boundary. Level P, high.

### 4.10 Placements in exchange formats

IfcAxis2Placement3D: Axis is the local Z, RefDirection approximates the local X and "if necessary an adjustment is
made to maintain orthogonality", Y is derived, both or neither are given, and they may not be parallel
(IFC4.3.x-development, the entity's schema text; buildingSMART's site refused us, as before). So reading IFC needs a
Gram-Schmidt step and Z-up to Y-up (the app's `io/import-ifc.js` already composes such frames). glTF needs none: its
axes are the app's (H1). Level P, high.

## 5. The alternatives compared

Criteria, stated before the comparison: exact to rounding over the app's full range (including half turns and
symmetric bodies); no conversion ambiguity at the three.js, Jolt, glTF and IFC boundaries; cost per call in V8;
simplicity for the gate's reviewers and Cline.

| Topic | Option | Exact over the range | Boundaries | Cost | Verdict |
|---|---|---|---|---|---|
| Stored orientation | 3x3 matrix | Yes, but drifts from orthogonal under integration | Converts to every format | 9 numbers | For applying, not storing |
| | Euler angles | No: gimbal lock (e04) | Order differs per tool | 3 numbers | Input and display only |
| | **Unit quaternion [x, y, z, w]** | Yes (e01, e01b with exp map) | Copy to glTF, three.js, Jolt (H1) | 4 numbers | **Store this** |
| | Rotation vector | Yes, but not unique past pi | None native | 3 numbers | Increments and solver unknowns |
| Matrix to quaternion | Trace only | No near pi (e02) | | Fastest | Never |
| | **Shepperd pivot** | Yes (e02) | | One branch | **Use** |
| Symmetric rank 2 | Full 3x3 | Yes | Clear | 9 numbers, rotations 2 products | Display, debugging |
| | Voigt | Yes, with factor-2 care | What tables and codes print | 6, rotation not orthogonal (e06) | At the boundary only |
| | **Mandel** | Yes, orthogonal rotation (e06) | Converts to Voigt in one step | 6 | **Store and compute** |
| Principal values | Closed form (Smith/Cardano) | No: vectors fail on equal values (e05) | | 257 ns | Never for vectors |
| | Kopp's hybrid | Mostly; falls back to QL | | Between | Not needed |
| | Eberly noniterative | Yes (his proof; not measured here) | | Fast | Later, if profiling asks |
| | **Cyclic Jacobi** | Yes (e05) | | 916 ns | **Use** |
| vec3 storage | Float64Array per result | Same | three.js accepts arrays | 37.6 ns (e08) | No |
| | Object {x, y, z} | Same | Unlike glTF and Jolt's JS arrays | Not measured | No |
| | **Plain array, new per result** | Same | Matches glTF JSON and the app's code | 10.2 ns | **Use**; caller's-output variants (8.5 ns) only where profiled hot |

What would change the recommendation: a profile showing principal values on the hot path of the live world (switch to
Eberly's noniterative solver behind the same function); a library adopted later whose quaternion order differs (its
adapter converts, the core does not change).

## 6. The experiments

All in `docs/research/experiments/v277a-tensors/`, Node 22.23.5 (V8 12.4.254), Linux, one run each after a fixed
seed; e08 the best of five runs of 2e7 calls. Raw numbers in each `eNN-*-results.json`.

| # | Measures | Result |
|---|---|---|
| e01 | Norm drift of 10^6 composed quaternions; orthogonality of 10^5 matrix products | 1.2e-13 unnormalised, 2.2e-16 normalised; 3.8e-14 |
| e01b | An hour of spin at 60 Hz: first-order, renormalised first-order, exp map | norm 3.8e6; 0.21 orientation error; 3e-11 |
| e02 | Matrix to quaternion at nine angles up to pi, 2,000 axes each | Shepperd 6.7e-16 throughout; trace-only up to 4.2e-3 and NaN |
| e03 | Slerp's linear fallback, two thresholds | gl-matrix norm error 3.1e-8 at 1e-3 rad; three.js 2.2e-16 |
| e04 | Euler ZYX round trip by distance to gimbal lock | 4.1e-13 at 1e-5 rad; 2e-7 at 1e-7 rad |
| e05 | Jacobi against the closed form, five cases, 5,000 each; cost | Table in 4.7; 916 ns against 257 ns |
| e06 | Mandel and Voigt rotations, 20,000 rotations | Q^T Q = I to 3.1e-15 (Mandel), 0.9997 off (Voigt) |
| e07 | Reciprocity and definiteness of ten species' compliances | 3 % to 53 % asymmetry; all positive definite either way |
| e08 | vec3 cross product, four forms and the floor | 10.2, 37.6, 8.5, 11.3 ns; floor 7.5 ns |

Not measured here: Safari's JavaScriptCore and Firefox's SpiderMonkey (only V8 runs in this environment); phones.
The timings are for V8 and are relative, not promises for every device.

## 7. Edges

| Edge | What happens | What the core does |
|---|---|---|
| A half turn (angle pi) | w = 0; trace formula divides by zero | Shepperd's pivot |
| q and -q | Same rotation, opposite sign | Comparisons use abs(dot); slerp flips to the shorter arc; storage keeps w >= 0 |
| Slerp of near-equal quaternions | sin(theta) near zero | Below a dot of 0.9995, lerp and renormalise |
| Zero rotation vector | u = phi/|phi| undefined | Taylor series below 1e-8 rad |
| Pitch within 1e-6 rad of 90 degrees | Euler angles not unique | Set roll to 0, keep the matrix; never store Euler |
| Equal eigenvalues | Eigenvectors not unique | Jacobi returns an orthonormal set; callers must not assume uniqueness |
| Mirroring (det R = -1) | Not a rotation; no quaternion represents it | Mirror stays baked into geometry, as `bimMirrorObject` (`editing/precision-editing.js` line 176) does now; the placement keeps det +1 |
| Non-uniform scale | Not a rotation | Kept separate from the quaternion (scale vector), as glTF does |
| IFC RefDirection not orthogonal to Axis | Allowed by the schema | Gram-Schmidt on import |
| Eigen's (w, x, y, z) constructor | Order differs from storage | Only matters if Eigen is ever used (it is not); recorded for adapters |
| The app's frame | x east, y up, z south when true north is 0 (map/cityjson.js: UTM files through `bimUtmInv` and `bimGeoToModel`, other files line 264; site/shadows.js line 27): right-handed | The core is frame-free; user-facing angles convert to the displayed Z-up frame (X east, Y north, Z up) in one function |
| kN, m, kPa in the structure model | A coherent system with tonnes | Scaled at the structure adapter; the core is base SI |
| Missing Poisson's ratios (dashes in Table 5-2) | 16 of 19 softwoods lack mu_RL, mu_TL | Derived from reciprocity (D7) |
| A compliance that is not positive definite | Unphysical energy | Refused on load with the failing check named |

## 8. What the app already has

- **No shared vector library.** An inline cross product appears in 10 engine files and a Euclidean norm in 9
  (counts by pattern, 2026-11-24); named helpers are duplicated: `cross` in `bim/stairs.js`,
  `bim/interiors-route-app.js`, `vcross`/`vdot`/`vnorm`/`vsub` in `core/mesh-primitives.js`, `ifcVCross`/`ifcVNorm`
  in `io/import-ifc.js` (lines 74 to 75).
- **Rotation.** `editing/precision-editing.js` line 35 `bimRotatePoint` is a plan (2D) rotation and
  `bimRotateObjectInPlace` (line 228) rewrites each kind's geometry. **Correction to the 2026-11-23 evaluation:** the
  transform gizmo already rotates solids in 3D. `gizmo/gizmo-handles.js` line 1195 `bimGizRotMat` is Rodrigues'
  formula and `bimGizmoXformObj` rewrites a solid's mesh vertices about a world point. So 3D tilting exists for
  generic solids, baked into their vertices; what does not exist is a stored orientation.
- **Stored orientation.** A column stores a plan angle (`o.bim.rotation`, read in `gizmo/transform-gizmo.js`
  `bimGizmoLocalDir` and set in `ui/build-ui.js` line 665), a text its `o.rot`; a wall's direction is implied by its first segment. Everything else has
  none (H9).
- **Frames.** IFC import composes placements as origin plus three axes (`io/import-ifc.js` lines 73 to 84);
  `io/gltf.js` line 27 notes glTF's axes equal the engine's; `solids/occt-adapter.js` line 14 and `io/iges-io.js`
  line 15 convert Z-up formats; `assets/scale-assets.js` line 593 turns Z-up models a quarter turn about X.
- **A displayed reading that disagrees with the model's axes.** `site-analysis/sun-path.js` line 128 `bimSunXyz`
  gives +Z to the north for two displayed readings (the Sun panel, `site-analysis/sun-panel.js` line 44, and the
  "On the dome" row of `bimSunNowRows`, `sun-path.js` line 133), while the model's north is -z
  (`site/shadows.js` line 27). It is display only; part 11, D10.
- **Units.** `properties/palette.js` lines 57 to 77 format lengths only; `structure/analytical-model.js` line 12:
  kN, m, kPa.
- **Eigenvalues.** `structure/modal.js` (V242) is queued to hold a Jacobi for K and M; `map/roofs-lidar.js` fits
  planes. V277a's Jacobi is for 3x3 symmetric tensors; V277c's for larger systems.

## 9. Risks and threats to validity

- Only V8 was measured; JavaScriptCore (Safari, every iPhone) may rank array and typed-array forms differently.
  Mitigation: the API hides the storage, so it can change without callers changing.
- The Wood Handbook's ratios are averages of a few samples per species, at 12 % moisture; real timber varies by
  species, grade, moisture and density, as the Handbook says. The registry records them as such, with the edition.
- Shoemake 1985 was read from a scanned course copy with OCR noise; the formula was checked on the scan's equations,
  and against three.js and gl-matrix.
- Shepperd 1978, Bond 1943, Helnwein 2001 and Mandel's own papers were not read (paywalled); their results are
  reproduced by measurement (e02, e06) and stated in open sources (level S).
- The e03 angle errors sit at the acos measurement floor; the norm errors carry the finding.
- e05's case "range 1e-12" builds its matrix with rounding of order 1e-16, which limits the tiny eigenvalue's
  relative accuracy for any method; residuals are the fair comparison.

## 10. What is still open (U), and why

Nothing the code will use is U. Open, not needed by V277a: the CLT products' published orthotropic values (the
manufacturers' European Technical Assessments; to research in V281 with the material cards), and whether Safari
changes e08's ranking (needs a device).

## 11. The owner's decisions

**Answered 2026-11-24** (the owner: "V277a decisions just do as recommended"): D1 to D11 as recommended. One
change in carrying them out: the core lives in `src/js/engine/math/math.js`, not `core/`, because `tools/gate.py`
keeps `core/` for Claude and these are Cline's work orders.

Asked together, each with its recommendation. They refine decision 3 of `plan-world-physics.md` (free tilt).

1. **D1 Quaternion convention.** Store `[x, y, z, w]`, Hamilton, unit, w >= 0. Recommended: yes (H1).
2. **D2 Where orientation lives.** (a) Keep baking every rotation into geometry, as now; (b) give every element a
   placement (position, quaternion, scale) over local geometry, as IFC and glTF do; (c) a placement for solids,
   imported models, assets and dynamic bodies, while parametric BIM elements (walls, floors, roofs) keep rebuilding
   from their parameters, with columns and openings gaining a full quaternion in place of their plan angle.
   Recommended: (c), built in V282; (b) would migrate every kind at once, (a) cannot give Jolt a body's orientation.
3. **D3 Six-number tensors.** Mandel inside the core; Voigt only where a table or a code prints it. Recommended: yes.
4. **D4 Principal values.** Cyclic Jacobi; Eberly's noniterative solver held in reserve. Recommended: yes.
5. **D5 Integrating orientation.** The exponential map, renormalised each step. Recommended: yes.
6. **D6 Angles people type.** Yaw, pitch and roll about the displayed axes (X east, Y north, Z up, as the gizmo's
   Revit order), converted to the stored quaternion; never stored. Recommended: yes.
7. **D7 Timber constants.** The registry keeps the Handbook's E ratios, shear ratios and major Poisson's ratios
   (mu_LR, mu_LT, mu_RT) with the edition, and derives the minor ones from reciprocity; the tabulated minor values
   are recorded but not used. Recommended: yes.
8. **D8 Units.** Base SI in the core; the structure model's kN, m, kPa stays coherent behind its adapter; units are
   documented on each function and checked by tests, not carried at run time. Recommended: yes.
9. **D9 API style.** Plain arrays returned by small pure functions; caller's-output variants only where a profile
   shows the need. Recommended: yes.
10. **D10 The Sun panel's reading.** Show the dome point in the displayed axes (Y north, Z up), not the current
    +Z north, so it agrees with the gizmo and the model. Recommended: yes, as a small separate fix.
11. **D11 Replacing the duplicates.** V277a's last task replaces the duplicated helpers and inline formulas of part 8
    (an inline cross product in 10 files, a norm in 9, the named copies) with the core's functions, file by file,
    each behind the existing tests. Recommended: yes.

## 12. References

| Source | URL | Read | Date | Level |
|---|---|---|---|---|
| Sola, J. (2017). Quaternion kinematics for the error-state Kalman filter. arXiv 1711.02508 | https://arxiv.org/abs/1711.02508 | Section 1.1, 3 (Table 2), 4 (eqs. 97 to 105, 99, 200, 201) | 2026-11-24 | P |
| Kopp, J. (2008). Efficient numerical diagonalization of hermitian 3x3 matrices. Int. J. Mod. Phys. C 19, 523. arXiv physics/0610206 v3 | https://arxiv.org/abs/physics/0610206 | Abstract, sections 2 to 4 | 2026-11-24 | P |
| Shoemake, K. (1985). Animating rotation with quaternion curves. SIGGRAPH '85, 245-254 | https://www.cs.cmu.edu/~kiranb/animation/p245-shoemake.pdf | Slerp definition, double cover | 2026-11-24 | P (scan) |
| Khronos Group. glTF 2.0 Specification | https://raw.githubusercontent.com/KhronosGroup/glTF/main/specification/2.0/Specification.adoc | 3.4 coordinate system and units; node TRS | 2026-11-24 | P |
| buildingSMART. IFC 4.3, IfcAxis2Placement3D (schema source) | https://raw.githubusercontent.com/buildingSMART/IFC4.3.x-development/master/docs/schemas/resource/IfcGeometryResource/Entities/IfcAxis2Placement3D.md | Whole entity | 2026-11-24 | P |
| BIPM. The International System of Units (SI Brochure), 9th edition (2019), the copy read V4.01 (June 2026) | https://www.bipm.org/en/publications/si-brochure | Tables 2 and 4, the radian's note | 2026-11-24 | P |
| USDA Forest Service, Forest Products Laboratory. Wood Handbook, FPL-GTR-282 (2021), chapter 5, Senalik and Farber | https://research.fs.usda.gov/download/treesearch/62244.pdf | Elastic properties, Eq. 5-1, Tables 5-1 and 5-2 | 2026-11-24 | P |
| Eberly, D. A Robust Eigensolver for 3x3 Symmetric Matrices (2014, modified 2021), CC BY 4.0 | https://www.geometrictools.com/Documentation/RobustEigenSymmetric3x3.pdf | Contents, sections 2, 5 | 2026-11-24 | P |
| Habera, M., Zilian, A. (2021). Symbolic spectral decomposition of 3x3 matrices. arXiv 2111.02117 | https://arxiv.org/abs/2111.02117 | Abstract | 2026-11-24 | P (abstract) |
| three.js, src/math/Quaternion.js, Euler.js, Matrix4.js (dev), MIT | https://github.com/mrdoob/three.js | setFromRotationMatrix, slerp, constructor; Euler order | 2026-11-24 | P |
| gl-matrix, src/quat.js, MIT | https://github.com/toji/gl-matrix | fromMat3, slerp | 2026-11-24 | P |
| Eigen, Eigen/src/Geometry/Quaternion.h, MPL-2.0 | https://gitlab.com/libeigen/eigen | Constructor and storage | 2026-11-24 | P |
| Jolt Physics, Jolt/Math/Quat.h, MIT | https://github.com/jrouwe/JoltPhysics | Storage and convention comment | 2026-11-24 | P |
| mechkit documentation, notation | https://mechkit.readthedocs.io/en/latest/source/notation.html | Mandel basis, conversions | 2026-11-24 | P (docs) |
| Shepperd, S. W. (1978). Quaternion from rotation matrix. J. Guidance and Control 1(3) | (paywalled) | Through three.js, gl-matrix and e02 | 2026-11-24 | S |
| Bond, W. L. (1943); Helnwein, P. (2001); Mandel, J. (1965) on 6x6 notations | (paywalled) | Through mechkit and e06 | 2026-11-24 | S |
| Michigan State University thesis on hardwood compliances; Korean pine elastic constants study (search S4) | https://d.lib.msu.edu/etd/24711 ; https://jwoodscience.springeropen.com/articles/10.1007/s10086-017-1671-y | Search summaries only | 2026-11-24 | S (support, not used for values) |
| The app's code, src/js/engine (files and lines in part 8) | this repository | As cited | 2026-11-24 | P |
