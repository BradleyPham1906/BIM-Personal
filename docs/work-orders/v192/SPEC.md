# LOD-E: facade images rectified onto walls (outline)

Notion: V190 LOD-E: facade images. PIPELINE: 192. Research: `docs/research/research-notion-v190-facades.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Next spec sprint: the first slice is pure geometry.

## 1. The owner's decisions, 2026-11-14, as recommended

- the first source is the owner's own photo with four or more control points the owner clicks on the photo and on the wall; Panoramax (CC BY-SA, no key) only after a pose test on real panoramas;
- an uncalibrated stretch is allowed only as a labelled visual texture, never measured from;
- independent check points (at least one) give the reported error; above 5 cm RMS the facade is marked not for measuring;
- photos stay in the project file (the owner's), never sent anywhere; Panoramax images are referenced and credited, not copied.

## 2. What it does for the user

On an LOD2 wall, open a photo, click four or more matching points: the photo is warped straight onto the wall in metres, with its error shown.

## 3. The first slice (pure functions in `src/js/engine/map/facade-rectify.js`, ES5, no other file's names)

- `bimFacHomography(src, dst)`: the 3x3 homography from four or more point pairs by the normalised DLT (Hartley's normalisation, least squares by normal equations).
- `bimFacApply(H, p)`: a point through the homography, with the division by w.
- `bimFacError(H, src, dst)`: the RMS and the largest distance of the mapped check points from their targets.
- `bimFacWallFrame(wall)`: a wall face's local frame: origin at its lower left, u along it, v up, in metres.
- `bimFacRectifyGrid(H, w, h, step)`: the source pixel for each cell of the rectified image.

Tests: A known homography applied to synthetic points: recovered within 1e-9; noise of known size gives the expected RMS.

## 4. Not in this phase

Automatic matching; lens distortion beyond a declared camera model; panorama pose estimation in the first slice.
