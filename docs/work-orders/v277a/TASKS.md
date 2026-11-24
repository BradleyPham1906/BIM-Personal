# V277a work orders: The math core, layer 1: vectors, rotations and tensors

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add its function or functions to `src/js/engine/math/math.js`, below the file's header comment
and below the earlier tasks' functions, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.
The reference functions in `docs/research/experiments/v277a-tensors/ref.mjs` show the methods (read, do not import).

The tests are in `docs/work-orders/v277a/v277a.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v277a/v277a.test.mjs
    node --check src/js/engine/math/math.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] vec3: `bimV3Add`, `bimV3Sub`, `bimV3Scale`, `bimV3Dot`, `bimV3Cross`, `bimV3Len`, `bimV3Norm`

- **It must:** SPEC 5 WO-01: vec3: `bimV3Add(a, b)`, `bimV3Sub(a, b)` (a - b), `bimV3Scale(a, s)`, `bimV3Dot(a, b)`, `bimV3Cross(a, b)` (right-handed: x cross y = z), `bimV3Len(a)`, `bimV3Norm(a)` (the unit vector; [0, 0, 0] for a zero vector, never NaN). Each returns a new array or a number.
- **May use:** nothing.
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+0+0 = 0.

---

## [ ] WO-02 [Cline] mat3, row-major: `bimM3Ident`, `bimM3Mul`, `bimM3T`, `bimM3MulV`, `bimM3Det`

- **It must:** SPEC 5 WO-02: mat3, row-major: `bimM3Ident()`, `bimM3Mul(a, b)` (a times b), `bimM3T(a)`, `bimM3MulV(m, v)`, `bimM3Det(m)`.
- **May use:** nothing.
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] quaternion basics: `bimQMul`, `bimQConj`, `bimQNormalize`, `bimQCanon`

- **It must:** SPEC 5 WO-03: quaternion basics: `bimQMul(a, b)` the Hamilton product a b: [aw bx + ax bw + ay bz - az by, aw by - ax bz + ay bw + az bx, aw bz + ax by - ay bx + az bw, aw bw - ax bx - ay by - az bz]; `bimQConj(q)` [-x, -y, -z, w]; `bimQNormalize(q)` (q / |q|; [0, 0, 0, 1] when |q| is 0); `bimQCanon(q)` (-q when w < 0, else a copy of q).
- **May use:** nothing.
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimQRotate`, `bimQFromAxisAngle`

- **It must:** SPEC 5 WO-04: `bimQRotate(q, v)`: q v q* for a unit q, as v + w t + u x t with u = (x, y, z) and t = 2 u x v. `bimQFromAxisAngle(axis, angle)`: [axis/|axis| sin(angle/2), cos(angle/2)]; [0, 0, 0, 1] when |axis| is 0.
- **May use:** nothing.
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Cline] `bimQToM3`, `bimM3ToQ`

- **It must:** SPEC 5 WO-05: `bimQToM3(q)`: the row-major rotation matrix of a unit q (research `ref.mjs` `qToMat`). `bimM3ToQ(m)`: Shepperd's pivot: the largest of trace, m00, m11, m22 chooses the branch (as `matToQShepperd` in `docs/research/experiments/v277a-tensors/ref.mjs`); the result normalised and canonical (w >= 0).
- **May use:** bimQNormalize, bimQCanon (WO-03).
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-06 [Cline] `bimQExp`, `bimQLog`

- **It must:** SPEC 5 WO-06: `bimQExp(phi)`: the exponential map of a rotation vector phi (rad): theta = |phi|; [phi sin(theta/2)/theta, cos(theta/2)], and below theta = 1e-8 the series [phi (1/2 - theta^2/48), 1 - theta^2/8]. `bimQLog(q)`: its inverse on the canonical normalised q: with n = |(x, y, z)|, theta = 2 atan2(n, w), the vector (x, y, z) theta / n; below n = 1e-12 return 2 (x, y, z).
- **May use:** bimQNormalize, bimQCanon (WO-03).
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-07 [Cline] `bimQSlerp`

- **It must:** SPEC 5 WO-07: `bimQSlerp(a, b, t)`: Shoemake's slerp on the shorter arc (negate b when a . b < 0); when the dot is 0.9995 or more, the linear blend renormalised with `bimQNormalize`.
- **May use:** bimQNormalize (WO-03).
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 18
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-08 [Cline] `bimQIntegrate`

- **It must:** SPEC 5 WO-08: `bimQIntegrate(q, w, dt)`: one step of orientation with the world-frame angular velocity w (rad/s): `bimQNormalize(bimQMul(bimQExp(w dt), q))`.
- **May use:** bimQMul, bimQNormalize (WO-03), bimQExp (WO-06).
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 5
- **Test:** the cases named `WO-08 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-09 [Cline] `bimEulerToQ`, `bimQToEuler`

- **It must:** SPEC 5 WO-09: `bimEulerToQ(yaw, pitch, roll)`: about the displayed axes, R = Rz(yaw) Ry(pitch) Rx(roll) in the displayed frame; in the app's frame q = qa(+y, yaw) qa(-z, pitch) qa(+x, roll), qa = `bimQFromAxisAngle`. Positive yaw turns east toward north (counterclockwise from above; not a compass bearing). `bimQToEuler(q)`: {yaw, pitch, roll} from D = C^T R C with R = `bimQToM3(q)`, C = [1, 0, 0, 0, 0, 1, 0, -1, 0]: pitch = asin(clamp(-D[6])); when |D[6]| > 1 - 1e-12 (gimbal lock) roll = 0 and yaw = atan2(-D[1], D[4]); else yaw = atan2(D[3], D[0]), roll = atan2(D[7], D[8]).
- **May use:** bimQMul (WO-03), bimQFromAxisAngle (WO-04), bimQToM3 (WO-05), bimM3Mul, bimM3T (WO-02).
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-09 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+1+0+2+0 = 3.

---

## [ ] WO-10 [Cline] `bimTrsToM4`, `bimM4MulPoint`

- **It must:** SPEC 5 WO-10: `bimTrsToM4(t, q, s)`: the column-major 4x4 of translation t, unit rotation q and scale s (glTF's TRS: scale, then rotate, then translate): column j is the rotation's column j times s[j], the fourth column [t, 1]. `bimM4MulPoint(M, p)`: M [p, 1]; divided by w when w is neither 0 nor 1.
- **May use:** bimQToM3 (WO-05).
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-10 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-11 [Cline] Mandel and Voigt: `bimSymToMandel`, `bimMandelToSym`, `bimMandelToVoigt`, `bimMandelFromVoigt`

- **It must:** SPEC 5 WO-11: Mandel and Voigt: `bimSymToMandel(m)` from a row-major symmetric 3x3: [m00, m11, m22, sqrt2 m12, sqrt2 m02, sqrt2 m01]; `bimMandelToSym(v)` back; `bimMandelToVoigt(v, kind)`: the shears divided by sqrt2 for kind 'stress', multiplied by sqrt2 for 'strain' (engineering shears, twice the tensor's); `bimMandelFromVoigt(v, kind)` the inverse.
- **May use:** nothing.
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-11 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-12 [Cline] `bimSymRotate`, `bimMandelRotM`

- **It must:** SPEC 5 WO-12: `bimSymRotate(R, m)`: R m R^T (row-major 3x3). `bimMandelRotM(R)`: the 6x6 Q (rows) with Q[i][k] the i-th Mandel component of `bimSymRotate(R, bimMandelToSym(e_k))`, e_k the k-th unit 6-vector; Q is orthogonal.
- **May use:** bimM3Mul, bimM3T (WO-02), bimSymToMandel, bimMandelToSym (WO-11).
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-12 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-13 [Cline] `bimMandelRotate4`

- **It must:** SPEC 5 WO-13: `bimMandelRotate4(Q, C)`: Q C Q^T for 6x6 arrays of rows (a stiffness or compliance turned to new axes).
- **May use:** nothing.
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-13 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-14 [Cline] `bimSymInvariants`

- **It must:** SPEC 5 WO-14: `bimSymInvariants(m)`: {I1: trace, I2: (I1^2 - tr(m m))/2, I3: det, J2: s:s/2 with s = m - I1/3 I, vonMises: sqrt(3 J2)}.
- **May use:** bimM3Det (WO-02).
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-14 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-15 [Cline] `bimSymEig3`

- **It must:** SPEC 5 WO-15: `bimSymEig3(m)`: the eigenvalues and unit eigenvectors of a symmetric 3x3 (row-major) by cyclic Jacobi rotations: {error: 'not a 3x3 matrix'} unless nine finite numbers; {error: 'not symmetric'} when |m_pq - m_qp| exceeds 1e-9 (|m_pq| + |m_qp|) for a pair; on a copy, sweep the pairs (0,1), (1,2), (0,2) until the sum of squares above the diagonal is 0 or at most 1e-30 times that of the diagonal (at most 50 sweeps), the rotation as `eigJacobi` in `ref.mjs`. Returns {values: ascending, vectors: vectors[r] the unit eigenvector of values[r]}. (V242's `bimEigJacobi` is the general n x n solver for K and M; this one is the fixed 3x3 for tensors.)
- **May use:** nothing.
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 45
- **Test:** the cases named `WO-15 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+1+0+0+2+0 = 3.

---

## [ ] WO-16 [Cline] `bimIsoStiffness`

- **It must:** SPEC 5 WO-16: `bimIsoStiffness(E, nu)`: the isotropic 6x6 Mandel stiffness: {error: 'E must be positive and nu between -1 and 0.5'} unless E > 0 and -1 < nu < 0.5; lambda = E nu / ((1 + nu)(1 - 2 nu)), mu = E / (2 (1 + nu)); C[i][j] = lambda + (i = j ? 2 mu : 0) for i, j < 3; C[i][i] = 2 mu for i >= 3 (Mandel: 2 mu, where Voigt has mu); zeros elsewhere.
- **May use:** nothing.
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-16 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-17 [Cline] `bimOrthoCompliance`

- **It must:** SPEC 5 WO-17: `bimOrthoCompliance(c)`: the orthotropic 6x6 Mandel compliance from c = {E1, E2, E3, G23, G13, G12, nu12, nu13, nu23} (nu_ij: strain in j over strain in i under stress in i): {error: '<name> must be positive'} for the first of E1, E2, E3, G23, G13, G12 that is not > 0; the normal block [[1/E1, -nu12/E1, -nu13/E1], [-nu12/E1, 1/E2, -nu23/E2], [-nu13/E1, -nu23/E2, 1/E3]] (the minor ratios by reciprocity, so it is symmetric); S33 = 1/(2 G23), S44 = 1/(2 G13), S55 = 1/(2 G12) at indices [3][3], [4][4], [5][5]; zeros elsewhere; {error: 'not positive definite'} when the normal block's smallest eigenvalue (`bimSymEig3`) is not > 0.
- **May use:** bimSymEig3 (WO-15).
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-17 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-18 [Cline] `bimWoodOrtho`

- **It must:** SPEC 5 WO-18: `bimWoodOrtho(EL, r)`: timber from the Wood Handbook (FPL-GTR-282, 2021, Tables 5-1 and 5-2), axes 1 L, 2 R, 3 T: {error: 'EL must be positive'}; {error: 'no ratios'}; {error: 'missing G_RT'} when r.GRT_EL is not > 0 (a dash in Table 5-1); else `bimOrthoCompliance({E1: EL, E2: EL r.ER_EL, E3: EL r.ET_EL, G23: EL r.GRT_EL, G13: EL r.GLT_EL, G12: EL r.GLR_EL, nu12: r.muLR, nu13: r.muLT, nu23: r.muRT})`.
- **May use:** bimOrthoCompliance (WO-17).
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-18 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+0+0 = 0.

---

## [ ] WO-19 [Cline] `bimInv6`

- **It must:** SPEC 5 WO-19: `bimInv6(A)`: the inverse of a 6x6 (array of rows) by Gauss-Jordan with partial pivoting: {error: 'not 6x6'}; {error: 'singular'} when a pivot's magnitude is not above 1e-300.
- **May use:** nothing.
- **Files:** `src/js/engine/math/math.js`, `docs/work-orders/v277a/v277a.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-19 ...` in `docs/work-orders/v277a/v277a.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] C-20 [Claude] The Wood Handbook record in the registry

- SPEC 6: `wood.fpl2021` in `src/js/engine/standards/registry.js`: FPL-GTR-282 (2021) chapter 5, Tables 5-1 and 5-2,
  every species row with all constants tabulated (the minor ratios kept, marked unused, D7), the source and pages.

---

## [ ] C-21 [Claude] Replace the duplicated helpers

- SPEC 6: the engine's copies of vector helpers (research part 8) call `math/math.js` instead, file by file, each
  behind the existing tests; `npm run modules`, the build, `npm test`.

---

## [ ] C-22 [Claude] The Sun panel's dome point in the displayed axes

- SPEC 6 and D10: `bimSunXyz` in `src/js/engine/site-analysis/sun-path.js` reports X east, Y north, Z up, as the gizmo does.

---

## [ ] C-23 [Claude] The tests and the records

- Move `v277a.test.mjs`'s cases to `tests/unit/core-math.test.mjs`; `npm run modules`; the build; PIPELINE, the
  engineering log and Notion (`docs/research/notion-sync.md`).
