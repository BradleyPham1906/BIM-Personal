# V242 spec: Modes and the response spectrum

Research: `docs/research/research-physical-world.md` (part 4.4) and `docs/research/research-physical-world/seismic-dynamics.md`; the independent check in `docs/research/research-physical-world/independent-check.md`. The owner's decisions: as the research recommends, answered 2026-11-22 (standard and scalable; 4, 9 and 11 amended) (part 11 of the note; the owner, 2026-11-21: "Do your research first, properly. And then develop the work orders"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-21.

## 1. The decisions this spec follows

- Lumped masses and three degrees of freedom per storey (two translations and a rotation, rigid floors), as ETABS does; e01: Jacobi is exact and fast to about 120 dof (decision 9).
- Our own cyclic Jacobi on M^-1/2 K M^-1/2, behind one interface (K and M in, modes out), so a subspace-iteration solver on the full frame can replace it beyond about 120 dof without changing callers; no library (decision 9, amended 2026-11-22).
- Enough modes for 90 % of the mass in each direction, listed with their participation; CQC at 5 % by default, SRSS beside it.
- The spectrum's base shear scaled up to 100 % of the ELF shear (7-22; 85 % was 7-10), never down.

## 2. What it does for the user

Analyze, Structure, Modes: the building's periods, mode shapes animated, the mass participation per mode and its sum; Response spectrum: storey forces, shears and drifts from the USGS spectrum, scaled to the ELF shear.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/structure/modal.js` | new, after `js/engine/structure/seismic-elf.js` in `src/index.html` (header done) | 7 pure functions (part 5) | Cline, WO-01 to WO-07 |
| `docs/work-orders/v242/v242.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, C-08, C-09 |

## 4. Units

stiffness kN/m, mass t (kN s2/m), w rad/s, T s.

## 5. Functions, `src/js/engine/structure/modal.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function may use an earlier one of this file, as its task says.

- **WO-01 `bimEigJacobi(A)`**: the eigenvalues and unit eigenvectors of a real symmetric matrix A (an array of rows) by cyclic Jacobi rotations: {error: 'not square'} unless every row has A.length entries; {error: 'not symmetric'} when some |A[i][j] - A[j][i]| exceeds 1e-9 (|A[i][j]| + |A[j][i]|). Work on a copy; sweep until the sum of squares above the diagonal is at most 1e-30 times that of the diagonal (at most 100 sweeps). Returns {values: ascending, vectors: vectors[r] the unit eigenvector of values[r]}. Example: [[2, 0], [0, 1]] gives values [1, 2].
- **WO-02 `bimModalLumped(K, m)`**: the modes of K phi = w2 M phi with M diagonal, m the masses: {error: 'bad input'} unless m is non-empty and K has m.length rows; {error: 'every mass must be positive'}. A[i][j] = K[i][j] / sqrt(m[i] m[j]); bimEigJacobi(A) (its error returned as it is); for each eigenpair in order {w2, w = sqrt(max(w2, 0)), T = 2 pi / w (Infinity when w is 0), phi[i] = v[i] / sqrt(m[i])} (so phi' M phi = 1). Example: K [[80000, -40000], [-40000, 40000]], m [100, 100] gives T 0.50832 and 0.19416 s.
- **WO-03 `bimModalPart(modes, m, iota)`**: for each mode {phi}: L = sum phi_i m_i iota_i, Mn = sum phi_i m_i phi_i; gamma = L / Mn, mEff = L^2 / Mn (both 0 when Mn is 0), ratio = mEff / (sum m_i iota_i^2) (0 when that is 0). Returns [{gamma, mEff, ratio}] in the modes' order. iota is the influence vector (1 for a dof in the direction, 0 else). Example: the two-storey modes give ratios 0.9472 and 0.0528.
- **WO-04 `bimCqcRho(wi, wj, z)`**: Der Kiureghian's CQC coefficient for equal damping z: NaN unless wi > 0, wj > 0 and z >= 0; r = wj / wi; 8 z^2 (1 + r) r^1.5 / ((1 - r^2)^2 + 4 z^2 r (1 + r)^2). Example: (10, 5, 0.05) gives 0.01849.
- **WO-05 `bimModalCombine(v, w, z, how)`**: combines modal peak values v (one per mode, w their circular frequencies): how 'srss': sqrt(sum v_i^2); otherwise CQC: sqrt(max(0, sum over i and j of bimCqcRho(w_i, w_j, z) v_i v_j)). Example: [3, 4] with 'srss' gives 5.
- **WO-06 `bimShearK(k)`**: the stiffness matrix of a shear building from its storey stiffnesses k (the ground storey first): K[i][i] = k[i] + k[i+1] (k[i] alone for the top), K[i][i+1] = K[i+1][i] = -k[i+1], zeros elsewhere; [] for an empty k. Example: [3, 2, 1] gives [[5, -2, 0], [-2, 3, -1], [0, -1, 1]].
- **WO-07 `bimRsaScale(Vt, V)`**: the factor applied to the spectrum's results: NaN unless Vt > 0 and V > 0; V / Vt when Vt < V, else 1. Example: (900, 1170.2) gives 1.3002.

## 6. Order of the work

WO-01 to WO-07 in order. Then Claude: **C-08** the storey model: lumped masses per level (self-weight and dead load), a condensed 3-dof-per-storey stiffness from the frame (unit storey displacements solved through the frame solve), the modes with `bimModalLumped`, the participation table, mode shapes animated in the viewport; the response spectrum from V241's multi-period answer, combined by CQC, scaled by `bimRsaScale`; the test to tests/unit/; npm run modules; **C-09** the records.

## 7. Not in this phase

Subspace iteration on the full 3D frame; Ritz vectors; the residual rigid mode; orthogonal combination (100 % + 30 %); P-delta.
