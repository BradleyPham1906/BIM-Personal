
  /* ===== __acad3dV242: water on the ground (docs/work-orders/v242/SPEC.md) =====
     On the analyses' ground grid {nx, nz, cell, H, ok}: hollows filled by priority-flood (Barnes, Lehman and
     Mulla 2014), D8 flow directions (O'Callaghan and Mark 1984), flow accumulation, and a cell's catchment. */
  /* WO-01: the ground with its hollows filled to their spill heights, each filled cell at least eps above the
     one it drains to, as a Float64Array; NaN where there is no ground */
  function bimFill(G,eps){
    return null;
  }
  /* WO-02: each cell's steepest way down, 0 E, 1 SE, 2 S, 3 SW, 4 W, 5 NW, 6 N, 7 NE (rows run south), as an
     Int8Array; -1 at a pit, a flat or missing ground */
  function bimD8(G){
    return null;
  }
  /* WO-03: how many cells drain through each cell, itself included, as a Float64Array; NaN without ground */
  function bimFlowAcc(G,dir){
    return null;
  }
  /* WO-04: the cells whose water reaches cell k, k included, as a Uint8Array of 1s and 0s */
  function bimCatchment(G,dir,k){
    return null;
  }
export { bimCatchment, bimD8, bimFill, bimFlowAcc };
