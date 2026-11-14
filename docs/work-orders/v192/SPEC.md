# V192 spec: LOD-E, facade images rectified onto walls

Notion: V190 LOD-E: facade images. Research: `docs/research/research-notion-v190-facades.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- The first source is the owner's own photo with four or more control points clicked on the photo and on the wall; Panoramax (CC BY-SA, no key) after a pose test on real panoramas.
- An uncalibrated stretch is allowed only as a labelled visual texture, never measured from.
- At least one independent check point gives the reported error; above 5 cm RMS the facade is marked not for measuring.
- Photos stay in the project file, never sent anywhere.

## 2. What it does for the user

On an LOD2 wall, open a photo and click four or more matching points: the photo is warped straight onto the wall in metres, with its check-point error shown.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/map/facade-rectify.js` | new, after `js/engine/map/roofs-lidar.js` in `src/index.html` (header done) | 6 pure functions (part 5) | Cline, WO-01 to WO-06 |
| `docs/work-orders/v192/v192.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-07, WO-08 |

## 5. Functions, `src/js/engine/map/facade-rectify.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimFacSolve(A, b)`**: x with A x = b by Gaussian elimination with partial pivoting on a copy; null when a pivot is under 1e-14.
- **WO-02 `bimFacNorm(pts)`**: Hartley's normalising matrix [[s, 0, -s cx], [0, s, -s cy], [0, 0, 1]]: c the centroid, s = sqrt(2) / the mean distance from it (1 when that is under 1e-15).
- **WO-03 `bimFacMul(A, B)`**: the 3x3 product.
- **WO-04 `bimFacApply(H, p)`**: [(h00 x + h01 y + h02)/w, (h10 x + h11 y + h12)/w], w = h20 x + h21 y + h22.
- **WO-05 `bimFacHomography(src, dst)`**: null unless 4 or more pairs of equal count. Normalise both sets (WO-02), build the two rows per pair of the DLT with h22 = 1 ([x, y, 1, 0, 0, 0, -x u, -y u | u] and [0, 0, 0, x, y, 1, -x v, -y v | v]), solve the normal equations (A^T A) h = A^T b (WO-01), then H = Td^-1 Hn Ts and divide by H[2][2]. null when the solve fails.
- **WO-06 `bimFacError(H, src, dst)`**: {rms, max} of the distances between H(src[i]) and dst[i]; {rms: 0, max: 0} for none.

## 6. Order of the work

WO-01 to WO-06 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-07** the rectify tool on walls; **WO-08** the records.

## 7. Not in this phase

Automatic matching; lens distortion beyond a declared camera model; panorama pose.
