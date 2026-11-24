# V277a spec: The math core, layer 1: vectors, rotations and tensors

Research: `docs/research/research-tensors-rotations.md` (parts 4 and 5), its experiments in
`docs/research/experiments/v277a-tensors/`, and the independent check in
`docs/research/research-tensors-rotations/independent-check.md` (18 of 21 confirmed, 3 corrected). The plan:
`docs/research/plan-world-physics-math.md` part 9. The owner's decisions: D1 to D11, all as the research recommends,
answered 2026-11-24 ("V277a decisions just do as recommended"). Implementation target: local `main`. Written by Claude,
2026-11-24.

## 1. The decisions this spec follows

- **D1** A unit quaternion is `[x, y, z, w]` with Hamilton's algebra (i j = k), as glTF, three.js and Jolt store it;
  stored canonical (w >= 0). A rotation acts on a vector as q v q*.
- **D3** A symmetric rank-2 tensor is held in Mandel's six components `[a11, a22, a33, sqrt2 a23, sqrt2 a13, sqrt2 a12]`;
  Voigt only at the boundary (stress keeps its shears; strain doubles them).
- **D4** Principal values by cyclic Jacobi (exact on equal eigenvalues, which every symmetric body has).
- **D5** Orientation is integrated with the exponential map, the angular velocity in the world frame, renormalised.
- **D6** Angles people type are yaw, pitch and roll about the displayed axes (X east, Y north, Z up); never stored.
- **D7** Timber takes the Wood Handbook's E ratios, shear ratios and major Poisson's ratios; minor ratios by reciprocity.
- **D8** Base SI: m, kg, s, N, Pa, rad. Units are written on each function here and checked by the tests.
- **D9** Plain arrays returned by small pure functions.
- Matrices: a **3x3 is row-major** (9 numbers, `m[3*row + col]`), as the gizmo's `bimGizRotMat` already is; a **4x4 is
  column-major** (16 numbers), as the GPU code (`render/gpu-batches.js` `bimMat4Mul`), glTF and three.js are. A 6x6 is an
  array of six rows.
- The app's frame: x east, y up, z south (right-handed; north is -z when true north is 0). The displayed frame: X east,
  Y north, Z up. The two differ by a proper rotation: app (x, y, z) = (X, Z, -Y).

## 2. What it does for the user

Nothing visible yet. V277a gives every later phase (mass properties, dynamic bodies, finite elements, timber panels)
one exact, tested set of vectors, rotations and tensors, and its last task removes the copies spread across the
engine (D11). The Sun panel's displayed dome point is fixed to the displayed axes (D10).

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/math/math.js` | new, first after `js/engine/_begin.js` in `src/index.html` (header done); its own folder, `math/`, because `tools/gate.py` keeps `core/` for Claude | 41 pure functions in 19 work orders (part 5) | Cline, WO-01 to WO-19 |
| `docs/work-orders/v277a/v277a.test.mjs` | new | their tests (19 cases) | Claude (done) |
| `src/js/engine/standards/registry.js` | changed | the Wood Handbook's ratios as a record with its edition | Claude, C-20 |
| the engine's duplicated helpers (research part 8) | changed | calls to `math/math.js` in place of their copies | Claude, C-21 |
| `src/js/engine/site-analysis/sun-path.js` | changed | `bimSunXyz` in the displayed axes | Claude, C-22 |

## 4. Units

Lengths m, angles rad, time s, angular velocity rad/s, stress and moduli Pa (any one consistent unit works: the
functions are linear in it), Poisson's ratios dimensionless.

## 5. Functions, `src/js/engine/math/math.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function
may use an earlier one of this file, as its task says. Vectors are arrays of 3, quaternions of 4.

- **WO-01 vec3**: `bimV3Add(a, b)`, `bimV3Sub(a, b)` (a - b), `bimV3Scale(a, s)`, `bimV3Dot(a, b)`, `bimV3Cross(a, b)`
  (right-handed: x cross y = z), `bimV3Len(a)`, `bimV3Norm(a)` (the unit vector; [0, 0, 0] for a zero vector, never NaN).
  Each returns a new array or a number.
- **WO-02 mat3, row-major**: `bimM3Ident()`, `bimM3Mul(a, b)` (a times b), `bimM3T(a)`, `bimM3MulV(m, v)`, `bimM3Det(m)`.
- **WO-03 quaternion basics**: `bimQMul(a, b)` the Hamilton product a b: [aw bx + ax bw + ay bz - az by, aw by - ax bz +
  ay bw + az bx, aw bz + ax by - ay bx + az bw, aw bw - ax bx - ay by - az bz]; `bimQConj(q)` [-x, -y, -z, w];
  `bimQNormalize(q)` (q / |q|; [0, 0, 0, 1] when |q| is 0); `bimQCanon(q)` (-q when w < 0, else a copy of q).
- **WO-04** `bimQRotate(q, v)`: q v q* for a unit q, as v + w t + u x t with u = (x, y, z) and t = 2 u x v.
  `bimQFromAxisAngle(axis, angle)`: [axis/|axis| sin(angle/2), cos(angle/2)]; [0, 0, 0, 1] when |axis| is 0.
- **WO-05** `bimQToM3(q)`: the row-major rotation matrix of a unit q (research `ref.mjs` `qToMat`). `bimM3ToQ(m)`:
  Shepperd's pivot: the largest of trace, m00, m11, m22 chooses the branch (as `matToQShepperd` in
  `docs/research/experiments/v277a-tensors/ref.mjs`); the result normalised and canonical (w >= 0).
- **WO-06** `bimQExp(phi)`: the exponential map of a rotation vector phi (rad): theta = |phi|; [phi sin(theta/2)/theta,
  cos(theta/2)], and below theta = 1e-8 the series [phi (1/2 - theta^2/48), 1 - theta^2/8]. `bimQLog(q)`: its inverse on
  the canonical normalised q: with n = |(x, y, z)|, theta = 2 atan2(n, w), the vector (x, y, z) theta / n; below n = 1e-12
  return 2 (x, y, z).
- **WO-07** `bimQSlerp(a, b, t)`: Shoemake's slerp on the shorter arc (negate b when a . b < 0); when the dot is 0.9995
  or more, the linear blend renormalised with `bimQNormalize`.
- **WO-08** `bimQIntegrate(q, w, dt)`: one step of orientation with the world-frame angular velocity w (rad/s):
  `bimQNormalize(bimQMul(bimQExp(w dt), q))`.
- **WO-09** `bimEulerToQ(yaw, pitch, roll)`: about the displayed axes, R = Rz(yaw) Ry(pitch) Rx(roll) in the displayed
  frame; in the app's frame q = qa(+y, yaw) qa(-z, pitch) qa(+x, roll), qa = `bimQFromAxisAngle`. Positive yaw turns
  east toward north (counterclockwise from above; not a compass bearing). `bimQToEuler(q)`: {yaw, pitch, roll} from
  D = C^T R C with R = `bimQToM3(q)`, C = [1, 0, 0, 0, 0, 1, 0, -1, 0]: pitch = asin(clamp(-D[6])); when |D[6]| > 1 - 1e-12
  (gimbal lock) roll = 0 and yaw = atan2(-D[1], D[4]); else yaw = atan2(D[3], D[0]), roll = atan2(D[7], D[8]).
- **WO-10** `bimTrsToM4(t, q, s)`: the column-major 4x4 of translation t, unit rotation q and scale s (glTF's TRS: scale,
  then rotate, then translate): column j is the rotation's column j times s[j], the fourth column [t, 1].
  `bimM4MulPoint(M, p)`: M [p, 1]; divided by w when w is neither 0 nor 1.
- **WO-11 Mandel and Voigt**: `bimSymToMandel(m)` from a row-major symmetric 3x3: [m00, m11, m22, sqrt2 m12, sqrt2 m02,
  sqrt2 m01]; `bimMandelToSym(v)` back; `bimMandelToVoigt(v, kind)`: the shears divided by sqrt2 for kind 'stress',
  multiplied by sqrt2 for 'strain' (engineering shears, twice the tensor's); `bimMandelFromVoigt(v, kind)` the inverse.
- **WO-12** `bimSymRotate(R, m)`: R m R^T (row-major 3x3). `bimMandelRotM(R)`: the 6x6 Q (rows) with Q[i][k] the i-th
  Mandel component of `bimSymRotate(R, bimMandelToSym(e_k))`, e_k the k-th unit 6-vector; Q is orthogonal.
- **WO-13** `bimMandelRotate4(Q, C)`: Q C Q^T for 6x6 arrays of rows (a stiffness or compliance turned to new axes).
- **WO-14** `bimSymInvariants(m)`: {I1: trace, I2: (I1^2 - tr(m m))/2, I3: det, J2: s:s/2 with s = m - I1/3 I, vonMises:
  sqrt(3 J2)}.
- **WO-15** `bimSymEig3(m)`: the eigenvalues and unit eigenvectors of a symmetric 3x3 (row-major) by cyclic Jacobi
  rotations: {error: 'not a 3x3 matrix'} unless nine finite numbers; {error: 'not symmetric'} when |m_pq - m_qp| exceeds
  1e-9 (|m_pq| + |m_qp|) for a pair; on a copy, sweep the pairs (0,1), (1,2), (0,2) until the sum of squares above the
  diagonal is 0 or at most 1e-30 times that of the diagonal (at most 50 sweeps), the rotation as `eigJacobi` in
  `ref.mjs`. Returns {values: ascending, vectors: vectors[r] the unit eigenvector of values[r]}. (V242's `bimEigJacobi`
  is the general n x n solver for K and M; this one is the fixed 3x3 for tensors.)
- **WO-16** `bimIsoStiffness(E, nu)`: the isotropic 6x6 Mandel stiffness: {error: 'E must be positive and nu between -1
  and 0.5'} unless E > 0 and -1 < nu < 0.5; lambda = E nu / ((1 + nu)(1 - 2 nu)), mu = E / (2 (1 + nu)); C[i][j] = lambda
  + (i = j ? 2 mu : 0) for i, j < 3; C[i][i] = 2 mu for i >= 3 (Mandel: 2 mu, where Voigt has mu); zeros elsewhere.
- **WO-17** `bimOrthoCompliance(c)`: the orthotropic 6x6 Mandel compliance from c = {E1, E2, E3, G23, G13, G12, nu12,
  nu13, nu23} (nu_ij: strain in j over strain in i under stress in i): {error: '<name> must be positive'} for the first
  of E1, E2, E3, G23, G13, G12 that is not > 0; the normal block [[1/E1, -nu12/E1, -nu13/E1], [-nu12/E1, 1/E2, -nu23/E2],
  [-nu13/E1, -nu23/E2, 1/E3]] (the minor ratios by reciprocity, so it is symmetric); S33 = 1/(2 G23), S44 = 1/(2 G13),
  S55 = 1/(2 G12) at indices [3][3], [4][4], [5][5]; zeros elsewhere; {error: 'not positive definite'} when the normal
  block's smallest eigenvalue (`bimSymEig3`) is not > 0.
- **WO-18** `bimWoodOrtho(EL, r)`: timber from the Wood Handbook (FPL-GTR-282, 2021, Tables 5-1 and 5-2), axes 1 L,
  2 R, 3 T: {error: 'EL must be positive'}; {error: 'no ratios'}; {error: 'missing G_RT'} when r.GRT_EL is not > 0 (a dash
  in Table 5-1); else `bimOrthoCompliance({E1: EL, E2: EL r.ER_EL, E3: EL r.ET_EL, G23: EL r.GRT_EL, G13: EL r.GLT_EL,
  G12: EL r.GLR_EL, nu12: r.muLR, nu13: r.muLT, nu23: r.muRT})`.
- **WO-19** `bimInv6(A)`: the inverse of a 6x6 (array of rows) by Gauss-Jordan with partial pivoting: {error: 'not 6x6'};
  {error: 'singular'} when a pivot's magnitude is not above 1e-300.

## 6. Order of the work

WO-01 to WO-19 in order. Then Claude: **C-20** the Wood Handbook record in the registry (`wood.fpl2021`: the 2021
edition's Tables 5-1 and 5-2 rows with every constant tabulated, the minor ratios kept but marked unused, the source
and pages); **C-21** replace the duplicated helpers with the core's functions, file by file, each behind the existing
tests (research part 8: an inline cross product in 10 files, a norm in 9, the named copies in `bim/stairs.js`,
`bim/interiors-route-app.js`, `core/mesh-primitives.js`, `io/import-ifc.js`); the gizmo's Rodrigues kept until V282
moves orientation onto placements; **C-22** `bimSunXyz` in the displayed axes (D10); then the tests to `tests/unit/`,
`npm run modules`, the build, the records (PIPELINE, the log, Notion).

## 7. Not in this phase

Placements stored on elements (V282); mass properties (V277b); sparse and large solvers (V277c); time integrators
other than orientation's (V277d); a run-time unit system (D8: documented and tested instead); Eberly's noniterative
eigensolver (held in reserve, D4).
