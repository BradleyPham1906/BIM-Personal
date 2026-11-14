# V185 spec: Freeform F3, sweeps, pipes and caps

Notion: V183-V189 Freeform (F1-F7). Research: `docs/research/research-freeform-f1-f7.md`, `docs/research/research-rhino-guide-gap.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- A sweep carries its profile along a rail by rotation-minimising frames (Wang, Juttler, Zheng and Liu, double reflection, 2008), so a planar rail never twists the profile.
- Pipe is a circular profile swept along a rail; Cap closes an open ring with a centre fan.
- Results are meshes, previews of the exact surfaces until the kernel decision.

## 2. What it does for the user

Sweep a profile curve along a rail curve; Pipe a curve to a given radius; Cap the open ends.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/drawing/sweeps.js` | new, after `js/engine/drawing/surfaces.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v185/v185.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 4. Data

A frame {p, t, n, b}: the rail point, the unit tangent, normal and binormal (b = t x n). A profile point [x, y] goes to p + x n + y b.

## 5. Functions, `src/js/engine/drawing/sweeps.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimSwpPerp(t)`**: with the helpers bimSwpNorm(a) (unit vector, [0,0,0] for length under 1e-15) and bimSwpCross(a, b) written just above it: the unit perpendicular normalise(t x e), e the world axis whose |component| of t is smallest (x before y before z on a tie).
- **WO-02 `bimSwpFrames(rail)`**: one frame per rail point: t the normalised difference of the neighbours (one-sided at the ends); the first n bimSwpPerp(t); each next n by the double reflection: v1 = p_i - p_(i-1), reflect the previous n and t in v1 (r - 2(v1.r)/(v1.v1) v1), v2 = t_i - reflected t, reflect the reflected n in v2 (no reflection when v2.v2 < 1e-30; keep the previous n when v1.v1 < 1e-30), normalised; b = t x n. [] for fewer than 2 points.
- **WO-03 `bimSwpSweep(profile, rail, closed)`**: vertices frame by frame, each profile point [x, y] at p + x n + y b; faces [a, b, b + m, a + m] with a = i m + j, b = i m + (j + 1) % m, for j < m (closed) or m - 1. null for fewer than 2 frames or profile points.
- **WO-04 `bimSwpCircle(r, n)`**: n (16 when under 3; floored) points [r cos, r sin] at angles 2 pi i / n.
- **WO-05 `bimSwpCap(mesh, start, count, flip)`**: a new mesh: the vertices plus their centroid over the ring start .. start + count - 1, the faces plus a fan [centre, start + i, start + (i+1) % count], or [centre, start + (i+1) % count, start + i] when flip; the input unchanged.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** sweep, pipe and cap commands; **WO-07** the records.

## 7. Not in this phase

Two-rail sweeps; variable-radius pipes; self-intersection repair.
