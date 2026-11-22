
  /* ===== __acad3dV248: the shape of the ground (docs/work-orders/v248/SPEC.md) =====
     On the analyses' ground grid {nx, nz, cell, H, ok}: plan and profile curvature (Zevenbergen and Thorne 1987),
     the terrain ruggedness index (Riley et al. 1999), and a viewshed by sight lines over the ground. */
  /* WO-01: plan and profile curvature (1/m) at every cell, as {plan, profile} Float64Arrays; 0 on a flat cell,
     NaN on the edge or beside missing ground */
  function bimCurvature(G){
    return null;
  }
  /* WO-02: the terrain ruggedness index at every cell, sqrt of the summed squared differences to its eight
     neighbours, as a Float64Array; NaN without all eight */
  function bimTri(G){
    return null;
  }
  /* WO-03: what can be seen from cell (oi, oj) with the eye eyeH above the ground, targets tgtH tall, within maxR
     metres, as a Uint8Array: 1 seen, 0 hidden, 255 out of reach or without ground */
  function bimViewshed(G,oi,oj,eyeH,tgtH,maxR){
    return null;
  }
export { bimCurvature, bimTri, bimViewshed };
